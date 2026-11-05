#!/usr/bin/env python3
"""Fit the whole keyboard of Keyra's pianos with one neural network.

Today each recorded pitch is fitted on its own (fit_realtime_modal.py) and the
engine blends between them. Here one small network gives, for any piano, key,
velocity layer and partial, the figures the engine plays: the partial's tuning
and its four lanes' decay rates, frequency offsets and pickup from the key
alone (the strings), each lane's level and phase and the partial's rise from
the key and the layer (the strike). It learns what pianos share from every
library in Tools/keyboard_network.json and what makes each piano itself from a
short code per piano. It runs offline only and never plays a note; nothing is
stored per key. The plan and its judging steps are in
Docs/research/keyboard-network.md.

The loss compares what is heard: every partial's power in each channel,
frame by frame, through the window the fitter measures with
(keyboard_measurements.py keeps the frames and the fitter's weights, so no
audio is read here), in log against the measured. Each frame counts against
the envelope's largest value within 0.3 s of it, as the fitter weighs it,
and a beat's nulls count down to 20 dB under that. The fitter's own misfit
(piano_analysis.fit_partial_layers), which compares the complex envelopes,
is reported beside it but cannot be trained on, because it also compares
the lanes' frequencies to a few hundredths of a hertz over seconds. A
unison's beat rate changes at random from one key to the next, and no model
that follows the keyboard smoothly can match it there: lanes off by 0.05 Hz
take today's tables' misfit at their own pitches from 0.20 to 0.57 on the
grand (by 0.3 Hz, to 0.98, where silence scores 1), while the power loss
moves from 0.71 to 1.01. Trained on the misfit, the network made every
partial silent. Phases themselves are not compared: the soundboard, the room
and the microphones' places turn every partial by their own response at its
frequency, which no key tells of its neighbour's. The lanes' phases against
each other, which set the beating, are the network's; the table writer takes
each partial's phases from the nearest recorded pitch, as the engine takes
them from the nearer anchor today. Each partial's frequency, where the
power-weighted centre of its lanes sits, is fitted to the measured one
directly, in cents.

Two things are left to each recording: the level of each take where its
library normalised its takes, and each library's recording term, a level
and a tone curve over octaves per microphone, which the network's answer
passes through before it is compared.

One knob sets how sharply the answer may change from one key to the next: a
penalty on its second difference over the 88 keys, never across a piano's
bass break (its first plain-string key, "tenor" in the settings). Cross-
validation on the five pianos' train pitches (folds by pitch; their second
captures are held out with them) alone chooses the architecture, the knob and
each piano's fine-tuning depth, by the held-out envelope misfit: first every
architecture at the smallest knob, then every knob at the best architecture.
"Character" is the knob that predicts the held-out pitches best, "smooth" the
largest within one standard error of it.

The backtest is the pianos' dev takes, which nothing here trains on. A
network fitted at both settings is scored on them, and so is today's engine
as it ships: keyra_render plays each take's key at its velocity, and the
render is measured at the take's own partial frequencies and frames, through
its frame weights, so that it is scored exactly as the network is. The
engine plays its own voicing beside its tables (the velocity colour, the
per-key loudness trims, the strike's noise), which a network's closed form
does not hold, so the two meet only once a network's tables are rendered
too (Tools/write_network_tables.py). Until then each is compared with
itself, train takes against dev takes, and a network's train scores with
today's tables in closed form at their own pitches (`baseline`), where the
tables hold each key's own fit. The sealed takes are never measured here.

`correct` trains a smaller network of another kind: not the keyboard's
figures but a correction to the engine's blend between two recorded pitches,
learned by hiding the recorded pitches of the five pianos one to three in a
row and comparing the blend of those around them with the hidden pitches'
own fits. It moves each partial's decay rates and its power in each channel
and vanishes at the recorded pitches; its section below says why it is
learned against the fits, and from each channel's energy over three windows
rather than frame by frame. The table writer writes it for the engine to
apply to its blend (`--corrections`).

  python3 Tools/keyboard_network.py all --run alone --alone  # every step below, unattended
  python3 Tools/keyboard_network.py measure            # measure what is missing or stale
  python3 Tools/keyboard_network.py check              # the training model against keyra_render
  python3 Tools/keyboard_network.py baseline           # today's tables under the same loss
  python3 Tools/keyboard_network.py engine             # today's engine at the train and dev takes
  python3 Tools/keyboard_network.py cv --run alone --alone   # cross-validate the five alone
  python3 Tools/keyboard_network.py fit --run alone --alone --arch small   # final fits, dev backtest
  python3 Tools/keyboard_network.py report --run alone       # out/network/alone/report.md
  python3 Tools/keyboard_network.py correct --run correct --arch medium   # corrections to the blend, every knob

A run's results, logs, exported weights and report go to out/network/<run>/;
`cv`, `fit` and `all` resume from what a run already finished with the same
settings, and `--workers` trains that many entries at once, one thread each.
Tests/test_keyboard_network.py checks the training model's arithmetic; `all`
runs it first.
"""
from __future__ import annotations

import argparse
import cmath
import concurrent.futures
import copy
import hashlib
import itertools
import json
import math
import multiprocessing
import pickle
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import piano_analysis as pa  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'Tools/keyboard_network.json'
MEASURED = ROOT / 'out/keyboard'
DEV = ROOT / 'out/keyboard-dev'      # the Keyra pianos' dev takes: scored, never trained on
ENGINE = ROOT / 'out/keyboard-engine'   # today's engine scored at those takes, cached by renderer and takes
RUNS = ROOT / 'out/network'
SELFTEST = ROOT / 'Tests/test_keyboard_network.py'
KEYS = np.arange(21, 109)
ENGINE_PIANOS = ['grand', 'upright', 'kawai', 'hamburg', 'newyork']   # KeyraEngine.h Piano, in its order
TOP_HZ = 17000.0       # the engine plays no partial above this, nor above .43 of its rate
RIDGE = .03            # fit_partial_layers' default: each lane amplitude costs this share of its layer's peak
KNOTS = 2.0 ** np.arange(5, 15)   # Hz: the recording terms' tone curves, one point per octave, 32 Hz to 16 kHz
LOG_RATE = (math.log(pa.SLOWEST_RATE), math.log(500.0))   # fit_partial_layers' bounds
LOG_RISE = (math.log(2e-4), math.log(.5))
NULL = .01             # the floor under a frame's power, of its local level: a beat's nulls count to -20 dB
# How large a step from one key to the next counts as one unit of the knob's
# penalty, per figure: the second difference over three keys, in these units.
# The lanes' offsets count in cents of their partial: in hertz the upper
# partials' offsets, which span about 10 cents of a far higher frequency,
# would outweigh every other figure.
ROUGH = {'log_rate': 1.0, 'offset_cents': 1.0, 'theta': .2, 'lag': .5, 'cents': 1.0, 'level_db': 6.0,
         'phase': .5, 'log_rise': .5, 'f1_cents': 2.0, 'log_b': .2}

torch.set_default_dtype(torch.float64)


def load_config(path=CONFIG):
    return json.loads(Path(path).read_text())


def library_corpus(name):
    """A library's corpus manifest: a Keyra piano's own, else Tools/corpus/<name>.json."""
    import fit_realtime_modal as fit
    path = fit.MODELS[name]['corpus'] if name in fit.MODELS else ROOT / f'Tools/corpus/{name}.json'
    return json.loads(path.read_text())


# --- measurements -----------------------------------------------------------

def measure(config, jobs):
    """Measure every library of the settings whose audio this checkout holds;
    keyboard_measurements caches each pitch by its inputs (the takes' pins,
    the analysis options and the analysis code), so this redoes only what is
    missing or stale. A stale pitch whose audio is gone, as a base library's
    is once measured, is kept and reported: decode it again to renew it."""
    import fit_realtime_modal as fit
    import keyboard_measurements as km
    for name in config['libraries']:
        if name in fit.MODELS:
            jobs_of = list(km.piano_jobs(name))
            source = fit.MODELS[name]['wav']
        else:
            jobs_of = list(km.library_jobs(name))
            source = ROOT / f'out/base/{name}/wav'
        if name in fit.MODELS:
            jobs_of += list(dev_jobs(name))
        stale = []
        for target, _, note, _, cases, options in jobs_of:
            if target.exists():
                with target.open('rb') as f:
                    if pickle.load(f).get('cache_key') != km.cache_key(cases, options):
                        stale.append(note)
        measured = sum(1 for j in jobs_of if j[0].exists())
        present = [j for j in jobs_of if all(Path(p).exists() for p in j[1])]
        if not jobs_of:
            # A base library lists only the pitches whose audio is here.
            kept = len(list((km.OUT / name).glob('*.pkl')))
            print(f'{name}: no audio in {source}; its {kept} measured pitches are used as they are '
                  f'(decode it again to measure them anew)', flush=True)
            continue
        print(f'{name}: {len(jobs_of)} pitches{" (train and dev)" if name in fit.MODELS else ""}, '
              f'{measured} measured ({len(stale)} stale), audio for {len(present)} in {source}', flush=True)
        if present:
            km.run(present, jobs)
        gone = sorted(set(stale) - {j[2] for j in present})
        if gone:
            print(f'{name}: pitches {gone} were measured by other analysis code and have no audio here to measure '
                  f'again; training uses them as they are', flush=True)


def dev_jobs(name):
    """A Keyra piano's dev takes, measured as its train pitches are
    (keyboard_measurements.piano_jobs) into out/keyboard-dev: the backtest's.
    The split holds some pitches' layers back and others' every layer."""
    import fit_realtime_modal as fit
    model = fit.MODELS[name]
    options = fit.analysis_options(model)
    corpus = {f['id']: f for f in json.loads(model['corpus'].read_text())['files']}
    pitches = {}
    for case, role in json.loads(model['split'].read_text())['cases'].items():
        item = corpus[case]
        if role == 'dev' and item['kind'] == 'note':
            pitches.setdefault(item['midi'], []).append(
                (case, fit.layer_velocity(item), item.get('flac_sha256', item.get('wav_sha256'))))
    for note, layers in sorted(pitches.items()):
        layers.sort(key=lambda layer: layer[1])
        yield (DEV / name / f'{note}.pkl', [model['wav'] / f'{case}.wav' for case, _, _ in layers], note,
               [velocity for _, velocity, _ in layers], layers, options)


def layer_levels(groups, reference=None):
    """Each layer's level (dB) under its pitch's loudest, as fit_realtime_modal
    measures the layer levels (the 50-750 ms RMS), robust to pitches that lack
    a layer: a pitch's reference is its layers' median offset from the
    library's typical level at their velocities, which the `reference`
    groups give where they are not these (the train pitches, for dev takes)."""
    reference = reference or groups
    full = max(len(g['rms']) for g in reference)
    complete = [g for g in reference if len(g['rms']) == full]
    typical = {}
    for g in complete:
        for v, r in zip(g['velocities'], g['rms']):
            typical.setdefault(v, []).append(r - g['rms'][-1])
    typical = {v: float(np.median(r)) for v, r in typical.items()}
    vs = np.array(sorted(typical))
    for g in groups:
        expected = np.interp(g['velocities'], vs, [typical[v] for v in vs])
        ref = float(np.median(np.asarray(g['rms']) - expected))
        g['x'] = [float(r - ref) for r in g['rms']]


def window_tensors(f1, sr, length):
    """The envelope window as _WindowedExponentials holds it."""
    grid, profile = pa.window_profile(f1, sr, min(.002, length / sr / 24), length)
    h = float(grid[1] - grid[0])
    return {'grid': grid, 'w': profile / h, 'u': grid - grid[0], 'h': h, 'half': -grid[0] + h / 2}


def load_library(name, info, piano, library, folds, root=MEASURED, reference=None):
    """Every measured pitch of one library as the arrays training reads: per
    pitch its layers, and per layer (a unit) each partial's frames. `root`
    DEV loads a Keyra piano's dev takes, levelled against its train pitches
    (`reference`)."""
    corpus = library_corpus(name)
    normalised = bool(corpus.get('normalised'))
    groups = []
    for path in sorted((root / name).glob('*.pkl'), key=lambda p: int(p.stem)):
        with path.open('rb') as f:
            m = pickle.load(f)
        g = {'library': library, 'name': name, 'piano': piano, 'note': m['note'], 'f1': m['f1'],
             'sr': m['sr'], 'length': m['length'], 'cache_key': m.get('cache_key'),
             'window': window_tensors(m['f1'], m['sr'], m['length']),
             'velocities': [L['velocity'] for L in m['layers']], 'rms': [L['early_rms_db'] for L in m['layers']],
             'fold': folds.get(m['note']), 'units': []}
        for i, L in enumerate(m['layers']):
            rows = [(k, m['series'][k][i]) for k in range(len(m['orders'])) if m['series'][k][i] is not None]
            if not rows:
                continue
            z = np.concatenate([s['z'].T.astype(complex) for _, s in rows])
            w = np.concatenate([s['w'].astype(float) for _, s in rows])
            sid = np.concatenate([np.full(len(s['t']), j) for j, (_, s) in enumerate(rows)])
            zw = z * w[:, None]
            g['units'].append({'group': g, 'layer': i, 'velocity': L['velocity'], 'slot': -1,
                               'order': np.array([m['orders'][k] for k, _ in rows], float),
                               'fd': np.array([m['freqs'][k] for k, _ in rows], float),
                               'peak': np.array([s['peak'] for _, s in rows], float),
                               't': np.concatenate([s['t'].astype(float) for _, s in rows]), 'zw': zw, 'w': w,
                               'sid': sid, 'zz': np.bincount(sid, np.sum(np.abs(zw) ** 2, axis=1))})
        groups.append(g)
    if not groups:
        raise SystemExit(f'{name}: nothing measured in {root / name}: run `measure` first')
    layer_levels(groups, reference)
    for g in groups:
        for u in g['units']:
            u['x'] = g['x'][u['layer']]
            u['normalised'] = normalised
    return groups, normalised


def keyra_folds(config):
    """Each Keyra piano's train pitches dealt into folds by pitch, in turn up
    the keyboard, so every fold spans it; a second capture's pitches take
    their piano's folds."""
    folds = {}
    for name, info in config['libraries'].items():
        if info.get('keyra'):
            notes = sorted(int(p.stem) for p in (MEASURED / name).glob('*.pkl'))
            folds[info['piano']] = {n: k % config['folds'] for k, n in enumerate(notes)}
    return folds


def load_all(config, alone=False):
    """All libraries the run learns from, with their pianos and folds; each
    unit of a library that normalised its takes gets its layer level's slot."""
    folds = keyra_folds(config)
    names = [n for n, i in config['libraries'].items() if i.get('keyra') or not alone]
    pianos = sorted({config['libraries'][n]['piano'] for n in names},
                    key=lambda p: (not config['libraries'].get(p, {}).get('keyra'), p))
    data = {}
    for li, name in enumerate(names):
        info = config['libraries'][name]
        piano = pianos.index(info['piano'])
        groups, normalised = load_library(name, info, piano, li, folds.get(info['piano'], {}))
        data[name] = {'groups': groups, 'normalised': normalised, 'piano': info['piano'],
                      'keyra': bool(info.get('keyra')), 'index': li}
    for name in names:
        assign_slots(names, data, name, data[name]['groups'])
    return names, pianos, data


def level_slots(names, data):
    """The learned layer levels: one per velocity of each library that
    normalised its takes, whose measured levels say nothing."""
    return [(name, v) for name in names if data[name]['normalised']
            for v in sorted({int(v) for g in data[name]['groups'] for v in g['velocities']})]


def assign_slots(names, data, name, groups):
    slot = {s: k for k, s in enumerate(level_slots(names, data))}
    for g in groups:
        for u in g['units']:
            u['slot'] = slot.get((name, int(u['velocity'])), -1)


def keyra_pianos(names, data):
    return sorted({data[n]['piano'] for n in names if data[n]['keyra']})


def load_dev(config, names, data):
    """Each Keyra library's dev takes as units of the run's libraries,
    levelled against its train pitches."""
    dev = {}
    for name in names:
        d = data[name]
        if d['keyra'] and any((DEV / name).glob('*.pkl')):
            groups, _ = load_library(name, config['libraries'][name], d['groups'][0]['piano'], d['index'], {},
                                     root=DEV, reference=d['groups'])
            assign_slots(names, data, name, groups)
            dev[name] = [u for g in groups for u in g['units']]
    return dev


# --- the network ------------------------------------------------------------

def mlp(n_in, width, depth, n_out=None):
    layers, size = [], n_in
    for _ in range(depth):
        layers += [torch.nn.Linear(size, width), torch.nn.SiLU()]
        size = width
    if n_out:
        layers.append(torch.nn.Linear(size, n_out))
    return torch.nn.Sequential(*layers)


def unit_vectors(v):
    """Complex unit vectors from pairs of real outputs (..., 2k) -> (..., k)."""
    re, im = v[..., 0::2], v[..., 1::2]
    norm = torch.sqrt(re * re + im * im + 1e-12)
    return torch.complex(re / norm, im / norm)


class Net(torch.nn.Module):
    """The keyboard network: a key trunk (f1 and B), a string trunk (the partial's lanes, from key and partial) and a strike
    trunk (the lanes' levels and phases and the partial's rise, from the
    string trunk and the layer level), each piano's code, and each library's
    recording term."""

    def __init__(self, pianos, breaks, libraries, level_slots, arch):
        super().__init__()
        self.pianos, self.arch = list(pianos), dict(arch)
        self.register_buffer('breaks', torch.tensor(breaks, dtype=torch.float64).reshape(len(pianos), -1))
        n_key = 1 + 2 * arch['fourier'] + self.breaks.shape[1] + arch['code']
        # The same start whatever ran before in the process: a worker trains
        # several entries in turn, and each must start as it would alone.
        with torch.random.fork_rng():
            torch.manual_seed(0)
            self.codes = torch.nn.Parameter(.1 * torch.randn(len(pianos), arch['code']))
            self.key = mlp(n_key, arch['width'] // 2, 2, 2)
            self.string = mlp(n_key + 1, arch['width'], arch['depth'])
            self.string_out = torch.nn.Linear(arch['width'], 21)
            self.strike = mlp(arch['width'] + 1, arch['width'], 2)
            self.strike_out = torch.nn.Linear(arch['width'], 13)
        self.gain = torch.nn.Parameter(torch.zeros(len(libraries), 2))
        self.tone = torch.nn.Parameter(torch.zeros(len(libraries), 2, len(KNOTS)))
        # The layer levels of libraries whose takes were normalised, one per
        # velocity (level_slots), from a generic 40 dB over the velocity range.
        self.level_slots = [list(s) for s in level_slots]
        self.levels = torch.nn.Parameter(torch.tensor([40 * math.log10(max(v, 1) / 127) for _, v in level_slots]))
        with torch.no_grad():
            for head in (self.key[-1], self.string_out, self.strike_out):
                head.weight.mul_(.1)
                head.bias.zero_()
            # Lanes from 0.3/s, each a factor e faster than the next; equal
            # channels, no lag; -60 dB; a 2 ms rise; B 2e-4.
            self.string_out.bias[3] = math.log(.383 / .617)
            self.string_out.bias[:3] = math.log(math.e - 1)
            self.string_out.bias[12:20:2] = 1.0
            self.strike_out.bias[:4] = -3.0
            self.strike_out.bias[4:12:2] = 1.0
            self.strike_out.bias[12] = math.log(.294 / .706)

    def key_features(self, piano, note):
        u = (note - 64.5) / 43.5
        feats = [u[:, None]]
        for k in range(self.arch['fourier']):
            feats += [torch.sin(math.pi * 2 ** k * u)[:, None], torch.cos(math.pi * 2 ** k * u)[:, None]]
        feats.append((note[:, None] >= self.breaks[piano]).to(u.dtype))
        feats.append(self.codes[piano])
        return torch.cat(feats, 1)

    def forward(self, piano, note, order, level):
        """The table's figures for each (piano, key, partial, layer level), as
        tensors over the rows; lanes fastest first."""
        kf = self.key_features(piano, note)
        key = self.key(kf)
        hidden = self.string(torch.cat([kf, (torch.log2(order) / 7)[:, None]], 1))
        st = self.string_out(hidden)
        sk = self.strike_out(self.strike(torch.cat([hidden, (level / 30)[:, None]], 1)))
        lo, hi = LOG_RATE
        slow = lo + (hi - lo) * torch.sigmoid(st[:, 3])
        rates = [slow]
        for j in (2, 1, 0):
            rates.insert(0, rates[0] + torch.nn.functional.softplus(st[:, j]))
        log_rate = hi - torch.nn.functional.softplus(hi - torch.stack(rates, 1))
        et = 440 * 2 ** ((note - 69) / 12)
        span = torch.maximum(torch.clamp(.2 * order, min=2.5), pa.UNISON_REACH * order * et)
        # Every output moves about one unit of its own scale for a unit of
        # the network's, so that Adam's steps move each alike.
        return {'f1_cents': 10 * key[:, 0], 'log_b': math.log(2e-4) + 2 * key[:, 1],
                'log_rate': log_rate, 'offset': span[:, None] * torch.tanh(st[:, 4:8]),
                'theta': (math.pi / 2) * torch.sigmoid(st[:, 8:12]), 'lag': unit_vectors(st[:, 12:20]),
                'cents': 10 * st[:, 20], 'level_db': 20 * sk[:, :4], 'phase': unit_vectors(sk[:, 4:12]),
                'log_rise': LOG_RISE[0] + (LOG_RISE[1] - LOG_RISE[0]) * torch.sigmoid(sk[:, 12])}

    def recording(self, library, hz):
        """Each library's recording term at `hz`, per channel (rows x 2)."""
        octave = torch.clamp(torch.log2(hz) - 5, 0, len(KNOTS) - 1)
        i = torch.clamp(octave.floor().long(), max=len(KNOTS) - 2)
        f = (octave - i)[:, None]
        tone = self.tone[library]
        db = self.gain[library] + tone.gather(2, i[:, None, None].expand(-1, 2, 1))[..., 0] * (1 - f) \
            + tone.gather(2, (i + 1)[:, None, None].expand(-1, 2, 1))[..., 0] * f
        return 10 ** (db / 20)

    def frequency(self, out, note, order):
        """The partial's frequency (Hz): the stiff string through f1 and B, and its own cents."""
        f1 = 440 * 2 ** ((note - 69 + out['f1_cents'] / 100) / 12)
        b = torch.exp(out['log_b'])
        return order * f1 * torch.sqrt((1 + b * order ** 2) / (1 + b)) * 2 ** (out['cents'] / 1200)


# --- the misfit -------------------------------------------------------------

def batch_of(units):
    """Concatenate units into one batch of series and frames."""
    series, frames = [], []
    base = 0
    for j, u in enumerate(units):
        g = u['group']
        n = len(u['order'])
        series.append({'unit': np.full(n, j), 'order': u['order'], 'fd': u['fd'], 'peak': u['peak'], 'zz': u['zz'],
                       'note': np.full(n, float(g['note'])), 'piano': np.full(n, g['piano']),
                       'library': np.full(n, g['library']), 'x': np.full(n, u['x']),
                       'velocity': np.full(n, float(u['velocity'])), 'slot': np.full(n, u['slot']),
                       'normalised': np.full(n, u['normalised'])})
        frames.append({'t': u['t'], 'zw': u['zw'], 'w': u['w'], 'sid': u['sid'] + base})
        base += n
    b = {k: torch.from_numpy(np.concatenate([s[k] for s in series])) for k in series[0]}
    b.update({k: torch.from_numpy(np.concatenate([f[k] for f in frames])) for k in frames[0]})
    b['units'] = units
    b['count'] = torch.bincount(b['sid'], minlength=len(b['fd'])).to(torch.float64)
    # Each frame's measured power in each channel over its local level (w
    # holds 1/sqrt(count)).
    b['dd'] = (b['zw'].real ** 2 + b['zw'].imag ** 2) * b['count'][b['sid']][:, None]
    G = max(len(u['group']['window']['grid']) for u in units)
    win = {k: np.zeros((len(units), G)) for k in ('grid', 'w', 'u')}
    for j, u in enumerate(units):
        wt = u['group']['window']
        for k in win:
            win[k][j, :len(wt[k])] = wt[k]
    b.update({'window_' + k: torch.from_numpy(v) for k, v in win.items()})
    b['h'] = torch.tensor([u['group']['window']['h'] for u in units])
    b['half'] = torch.tensor([u['group']['window']['half'] for u in units])
    if 'blend_S' in units[0]:
        # The engine's blend at each series of a correction's examples, and
        # the two recorded pitches around it (correction_examples).
        b['blend_S'] = torch.from_numpy(np.concatenate([u['blend_S'] for u in units]))
        b['blend_C'] = torch.from_numpy(np.concatenate([u['blend_C'] for u in units]))
        for k in ('lower', 'upper', 'mix'):
            b[k] = torch.from_numpy(np.concatenate([np.full(len(u['order']), float(u[k])) for u in units]))
    return b


def windowed_response(b, S):
    """_WindowedExponentials for every frame of the batch: the window-measured
    response of e^(s t), t >= 0, for the series' complex rates S (series x m).

    Each window cell is integrated exactly from the onset on. With the cells
    from the first wholly after the onset summed from the end once per
    series, Q_j(s) = sum over g >= j of w_g e^(s (grid_g - grid_j)), which is
    w_j + e^(s h) Q_(j+1), a frame at t needs e^(s (t - h/2 + grid_j))
    (e^(s h) - 1) / s Q_j and the one cell the onset cuts, which is what
    _WindowedExponentials sums cell by cell. No exponent there is positive,
    so no rate overflows, however fast its rise."""
    unit = b['unit']
    w = b['window_w'][unit]
    G = w.shape[1]
    r = torch.exp(S * b['h'][unit][:, None])
    Q = [torch.zeros_like(S)]                                               # Q_G = 0
    for j in range(G - 1, -1, -1):
        Q.append(w[:, j, None] + r * Q[-1])
    Q = torch.stack(Q[::-1], 2)
    sid, t = b['sid'], b['t']
    fu = unit[sid]
    hf = b['h'][fu]
    grid0 = b['window_grid'][fu, 0]
    # The first cell wholly after the onset: grid_j >= h/2 - t.
    first = torch.clamp(torch.ceil((hf / 2 - t - grid0) / hf - 1e-9), 0, G).long()
    s = S[sid]
    cell = torch.expm1(s * hf[:, None]) / s
    # Past every cell (first = G), Q_G = 0 and the exponent is held at zero.
    lead = torch.clamp(t - hf / 2 + grid0 + first * hf, min=0)
    B = torch.exp(s * lead[:, None]) * cell * Q[sid, :, first]
    cut = first - 1
    length = t + grid0 + cut * hf + hf / 2
    part = (cut >= 0) & (length > 0)
    k = torch.nonzero(part)[:, 0]
    if len(k):
        wk = b['window_w'][fu[k], cut[k]]
        B = B.index_add(0, k, wk[:, None] * torch.expm1(s[k] * length[k][:, None]) / s[k])
    return B


def predicted_frames(b, S, C):
    """The prediction at every frame, per channel, through the frames'
    weights, for lanes with complex rates S (series x 4 and the same less the
    rise rate, x 8) and channel amplitudes C (series x 2 x 4)."""
    B = windowed_response(b, S)
    return torch.einsum('fl,fcl->fc', B[:, :4] - B[:, 4:], C[b['sid']]) * b['w'][:, None]


def correlations(b, S, C):
    """Per series, the inner product of the prediction with the measured
    envelope in each channel, the prediction's energy (both through the
    frames' weights) and the fitter's ridge on the amplitudes."""
    pw = predicted_frames(b, S, C)
    sid, n = b['sid'], len(b['fd'])
    c = torch.zeros((n, 2), dtype=pw.dtype).index_add(0, sid, torch.conj(pw) * b['zw'])
    pp = torch.zeros(n).index_add(0, sid, torch.sum(pw.real ** 2 + pw.imag ** 2, 1))
    rd = (RIDGE / b['peak']) ** 2 * torch.sum(C.real ** 2 + C.imag ** 2, (1, 2))
    return c, pp, rd


def log_power_ratio(b, S, C):
    return power_ratio(b, predicted_frames(b, S, C))


def power_ratio(b, pw):
    """Each frame's predicted power (pw, through the frames' weights, as
    predicted_frames gives it) over its measured in each channel, in natural
    log, each floored at NULL of the frame's local level, with a unit's mean
    taken out where its library normalised its takes."""
    frames = b['count'][b['sid']][:, None]
    r = torch.log((pw.real ** 2 + pw.imag ** 2) * frames + NULL) - torch.log(b['dd'] + NULL)
    unit = b['unit'][b['sid']]
    units = len(b['units'])
    mean = torch.zeros((units, 2)).index_add(0, unit, r) / torch.bincount(unit, minlength=units)[:, None]
    return torch.where(b['normalised'][b['sid']][:, None], r - mean[unit], r)


def envelope_misfit(b, S, C):
    """The training loss: each series' mean squared log power ratio over its
    frames and channels."""
    return series_misfit(b, log_power_ratio(b, S, C))


def series_misfit(b, r):
    return torch.zeros(len(b['fd'])).index_add(0, b['sid'], torch.mean(r ** 2, 1)) / b['count']


def misfit(b, S, C):
    """Each series' misfit as fit_partial_layers weighs it, with its phase
    in each channel free and, where its library normalised its takes, its
    unit's level free. Returns the misfit with the ridge and the relative
    error without it."""
    c, pp, rd = correlations(b, S, C)
    fit = torch.sum(torch.abs(c), 1)
    unit, n = b['unit'], len(b['fd'])
    units = len(b['units'])
    take = torch.zeros(units).index_add(0, unit, fit) / torch.clamp(torch.zeros(units).index_add(0, unit, pp + rd),
                                                                   min=1e-300)
    gain = torch.where(b['normalised'], take[unit], torch.ones(n))
    zz = b['zz']
    m = zz - 2 * gain * fit + gain ** 2 * (pp + rd)
    rel = (zz - 2 * gain * fit + gain ** 2 * pp) / zz
    return m, rel


def network_prediction(net, b):
    """The network's lanes for every series of the batch, where the engine
    would play them (the partial's frequency plus each lane's offset, against
    the measured frequency the envelopes are taken at): complex rates,
    channel amplitudes, and the tuning error (cents) of the lanes'
    power-weighted centre against the measured frequency."""
    if isinstance(net, Correction):
        return correction_prediction(net, b)
    level = b['x']
    if len(net.level_slots):
        level = torch.where(b['slot'] >= 0, net.levels[torch.clamp(b['slot'], min=0)], level)
    out = net(b['piano'], b['note'], b['order'], level)
    fd = b['fd']
    f = net.frequency(out, b['note'], b['order'])
    s = torch.complex(-torch.exp(out['log_rate']), 2 * math.pi * (out['offset'] + (f - fd)[:, None]))
    S = torch.cat([s, s - torch.exp(-out['log_rise'])[:, None]], 1)
    amp = 10 ** (out['level_db'] / 20) * out['phase']
    left = math.sqrt(2) * torch.cos(out['theta'])
    right = math.sqrt(2) * torch.sin(out['theta']) * out['lag']
    C = amp[:, None, :] * torch.stack([left.to(right.dtype), right], 1) * net.recording(b['library'], fd)[:, :, None]
    power = 10 ** (out['level_db'] / 10)
    centre = f + torch.sum(power * out['offset'], 1) / torch.sum(power, 1)
    return S, C, 1200 * torch.log2(centre / fd)


def channel_gain(frames, rounds=50):
    """Each channel's amplitude gain at which the median frame's log power
    ratio is zero, over (batch, predicted frames, frames kept) triples, with
    no take's level taken out: where the typical frame meets the measured
    one. The median only rises with the gain, so it is bisected in log gain
    within 100 dB either way. (Stepping by the median instead stalls where
    the floor under each ratio holds the median frame: 20 dB off, thirty
    steps left it 1.5 dB short.)"""
    raw = []
    for b, pw, keep in frames:
        power = (pw.real ** 2 + pw.imag ** 2) * b['count'][b['sid']][:, None]
        raw.append((power[keep], torch.log(b['dd'][keep] + NULL)))
    lo, hi = torch.full((2,), -11.5, dtype=torch.float64), torch.full((2,), 11.5, dtype=torch.float64)
    for _ in range(rounds):
        mid = (lo + hi) / 2
        r = torch.cat([torch.log(p * torch.exp(2 * mid) + NULL) - d for p, d in raw])
        up = torch.median(r, 0).values < 0
        lo, hi = torch.where(up, mid, lo), torch.where(up, hi, mid)
    return torch.exp((lo + hi) / 2)


@torch.no_grad()
def start_gains(net, units, sample=40):
    """Start each library's recording level where the untrained network's
    typical frame meets the measured one."""
    for us in units.values():
        b = batch_of(us[::max(1, len(us) // sample)])
        S, C, _ = network_prediction(net, b)
        gain = channel_gain([(b, predicted_frames(b, S, C), torch.ones(len(b['t']), dtype=torch.bool))])
        net.gain[int(b['library'][0])] += 20 * torch.log10(gain)


def roughness(net, gen, pianos, orders=4):
    """The knob's penalty: the mean squared second difference of the table's
    figures over the 88 keys (in ROUGH's units) at a few random partials and
    layer levels of each piano, never across its bass break nor above the
    engine's highest partial."""
    keys = torch.tensor(KEYS, dtype=torch.float64)
    rows = []
    for p in pianos:
        n = np.unique(np.round(np.exp(gen.uniform(0, math.log(48), orders))))
        for order in n:
            rows.append((p, float(order), float(gen.uniform(-30, 0))))
    piano = torch.tensor([r[0] for r in rows]).repeat_interleave(len(KEYS))
    order = torch.tensor([r[1] for r in rows]).repeat_interleave(len(KEYS))
    level = torch.tensor([r[2] for r in rows]).repeat_interleave(len(KEYS))
    note = keys.repeat(len(rows))
    if isinstance(net, Correction):
        # Along the keyboard at a gap and a place in it, both drawn per row.
        gap = torch.tensor(np.exp(gen.uniform(math.log(2), math.log(WIDEST), len(rows)))).repeat_interleave(len(KEYS))
        t = torch.tensor(gen.uniform(0, 1, len(rows))).repeat_interleave(len(KEYS))
        out = net(piano, note, order, level, gap, t)
        scales = CORRECTION_ROUGH
    else:
        out = net(piano, note, order, level)
        out['offset_cents'] = 1200 / math.log(2) * out['offset'] / net.frequency(out, note, order)[:, None]
        scales = ROUGH
    parts = []
    for k, scale in scales.items():
        v = out[k]
        if v.is_complex():
            v = torch.view_as_real(v).flatten(1)
        parts.append((v.reshape(len(note), -1)) / scale)
    q = torch.cat(parts, 1).reshape(len(rows), len(KEYS), -1)
    d2 = q[:, 2:] - 2 * q[:, 1:-1] + q[:, :-2]
    tenor = net.breaks[[r[0] for r in rows], 0][:, None]
    k0, k2 = keys[None, :-2], keys[None, 2:]
    across = (k0 < tenor) & (k2 >= tenor)
    high = (torch.tensor([r[1] for r in rows])[:, None] * 440 * 2 ** ((k2 - 69) / 12)) > TOP_HZ
    keep = (~across & ~high).to(q.dtype)[:, :, None]
    return torch.sum(d2 ** 2 * keep) / (torch.sum(keep) * q.shape[2])


# --- training ---------------------------------------------------------------

def make_net(config, pianos, names, data, arch):
    breaks = [[config['pianos'][p]['tenor']] for p in pianos]
    return Net(pianos, breaks, names, level_slots(names, data), config['architectures'][arch])


def units_of(data, names, held=None, fold_only=False):
    """Each library's units: with `held` (piano -> fold) the train units
    without that fold, or with `fold_only` that fold's units alone."""
    out = {}
    for name in names:
        d = data[name]
        fold = None if held is None else held.get(d['piano'])
        units = []
        for g in d['groups']:
            if (fold is not None and g['fold'] == fold) == fold_only:
                units.extend(g['units'])
        if units:
            out[name] = units
    return out


def loss_of(net, units, weights, tune_weight):
    """The training loss on a batch of units: each library's mean envelope
    misfit (a correction's power misfit) over its series, averaged with the
    libraries' weights, and the tuning term."""
    b = batch_of(units)
    S, C, cents = network_prediction(net, b)
    per = (power_misfit if isinstance(net, Correction) else envelope_misfit)(b, S, C)
    libs = b['library']
    total, weight = 0.0, 0.0
    for li in torch.unique(libs).tolist():
        rows = libs == li
        total = total + weights[li] * per[rows].mean()
        weight += weights[li]
    tune = torch.mean(torch.nn.functional.huber_loss(cents, torch.zeros_like(cents), delta=1.0, reduction='none'))
    return total / weight + tune_weight * tune, per, cents


def train(net, units, weights, settings, knob, seed, params=None, steps=None, lr=None, pianos=None, log=None):
    """Adam on the envelope misfit, the tuning term, the knob's penalty and a
    ridge on the recording terms' tone curves, with a cosine-decaying rate."""
    torch.manual_seed(seed)
    gen = np.random.default_rng(seed)
    steps = steps or settings['steps']
    lr = lr or settings['learning_rate']
    params = list(params if params is not None else net.parameters())
    opt = torch.optim.Adam(params, lr=lr)
    names = sorted(units)
    pianos = sorted({u['group']['piano'] for us in units.values() for u in us}) if pianos is None else pianos
    started = time.time()
    for step in range(steps):
        for group in opt.param_groups:
            group['lr'] = lr * .5 * (1 + math.cos(math.pi * step / steps))
        batch = []
        for name in names:
            pick = gen.choice(len(units[name]), size=min(settings['units_per_library'], len(units[name])),
                              replace=False)
            batch.extend(units[name][k] for k in pick)
        loss, per, cents = loss_of(net, batch, weights, settings['tune_weight'])
        rough = roughness(net, gen, pianos) if knob > 0 else torch.zeros(())
        objective = loss + knob * rough
        if isinstance(net, Net):
            objective = objective + settings['tone_ridge'] * torch.sum(net.tone ** 2)
        opt.zero_grad()
        objective.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        if log and (step % 100 == 0 or step == steps - 1):
            log(f'  step {step:5d}: loss {loss.item():.4f}, level error {decibels(per.mean().item()):.2f} dB rms, '
                f'median tuning error {torch.median(torch.abs(cents)).item():.2f} cents, '
                f'roughness {rough.item():.4f}, {time.time() - started:.0f} s')
    return net


def decibels(loss):
    """An envelope misfit (mean squared log power ratio) as an rms level error in dB."""
    return 10 / math.log(10) * math.sqrt(loss)


@torch.no_grad()
def score(net, units, chunk=40):
    """Each library's envelope misfit (the mean over its series, the
    training loss) and, for reference, the fitter's misfit pooled over the
    series' weighted energy and at its median series."""
    out = {}
    for name, us in units.items():
        out[name] = scores_of([network_prediction(net, b)[:2] + (b,) for b in batches(us, chunk)])
    return out


def batches(units, chunk):
    for k in range(0, len(units), chunk):
        yield batch_of(units[k:k + chunk])


def scores_of(predictions):
    """The scores of `score` from (S, C, batch) triples."""
    env, rel, m, zz = [], [], 0.0, 0.0
    for S, C, b in predictions:
        env.append(envelope_misfit(b, S, C))
        _, r = misfit(b, S, C)
        rel.append(r)
        m += float(torch.sum(r * b['zz']))
        zz += float(torch.sum(b['zz']))
    env, rel = torch.cat(env), torch.cat(rel)
    return {'envelope': float(env.mean()), 'level_db': decibels(float(env.mean())), 'pooled': m / zz,
            'median': float(torch.median(rel)), 'series': len(env)}


def fine_tune(net, data, names, piano, units, weights, settings, knob, seed, depth):
    """Fit one piano again on its own train pitches: its code (and its
    libraries' recording terms) alone, or with the trunks' last layers too.
    Returns a copy; the shared network is untouched."""
    tuned = copy.deepcopy(net)
    for p in tuned.parameters():
        p.requires_grad_(False)
    params = [tuned.codes, tuned.gain, tuned.tone, tuned.levels]
    if depth == 'last':
        params += [*tuned.key[-1].parameters(), *tuned.string_out.parameters(), *tuned.strike_out.parameters()]
    for p in params:
        p.requires_grad_(True)
    mine = {n: us for n, us in units.items() if data[n]['piano'] == piano}
    index = tuned.pianos.index(piano)
    train(tuned, mine, weights, settings, knob, seed, params=params, steps=settings['fine_tune_steps'],
          lr=settings['fine_tune_learning_rate'], pianos=[index])
    return tuned


def library_weights(names, data):
    """Each library counts once, whatever its size, so the largest base
    libraries do not outvote the five pianos."""
    return {data[n]['index']: 1.0 for n in names}


def settings_hash(config, extra):
    blob = json.dumps({'config': config, 'extra': extra}, sort_keys=True).encode()
    h = hashlib.sha256(blob)
    h.update(Path(__file__).read_bytes())
    for name in sorted(config['libraries']):
        for p in sorted((MEASURED / name).glob('*.pkl')):
            h.update(p.name.encode())
            h.update(str(p.stat().st_size).encode())
    return h.hexdigest()[:16]


# --- cross-validation and the final fits, in worker processes ---------------

_WORKER = {}


def _start_worker(config, alone, threads, gains=None):
    """A worker loads the run's measurements once and trains one entry at a
    time on its own threads; with the fits' channel gains (`gains`, a
    correction's run), the correction's examples too."""
    torch.set_num_threads(threads)
    names, pianos, data = load_all(config, alone)
    _WORKER.update(config=config, alone=alone, names=names, pianos=pianos, data=data)
    if gains is not None:
        _WORKER['examples'] = all_examples(config, names, data, gains)


def run_jobs(config, alone, workers, threads, function, jobs, done, gains=None):
    """Run function(*job) for every job in `workers` processes; done(job,
    result) is called in this process as each finishes. Spawned, not forked,
    so no worker inherits a parent's PyTorch threads."""
    if not jobs:
        return
    context = multiprocessing.get_context('spawn')
    with concurrent.futures.ProcessPoolExecutor(min(workers, len(jobs)), mp_context=context,
                                                initializer=_start_worker,
                                                initargs=(config, alone, threads, gains)) as pool:
        futures = {pool.submit(function, *job): job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            done(futures[future], future.result())


def run_folder(run, alone):
    """A run's folder, which keeps to the libraries it was started with."""
    folder = RUNS / run
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'run.json'
    if path.exists() and json.loads(path.read_text())['alone'] != alone:
        raise SystemExit(f'run {run} was started {"without" if alone else "with"} --alone: '
                         'give this one another name')
    path.write_text(json.dumps({'alone': alone}))
    return folder


def file_log(path):
    path.parent.mkdir(parents=True, exist_ok=True)

    def log(line):
        with path.open('a') as f:
            f.write(line + '\n')
    return log


def cv_entry(arch, knob, fold, log_path):
    """One cross-validation entry, in a worker: train without the fold of
    the Keyra pianos' train pitches and score it, as trained and fine-tuned
    to each piano's code alone and with the last layers."""
    config, names, pianos, data = (_WORKER[k] for k in ('config', 'names', 'pianos', 'data'))
    log = file_log(Path(log_path))
    keyra = keyra_pianos(names, data)
    held = {p: fold for p in keyra}
    train_units = units_of(data, names, held)
    test_units = {n: us for n, us in units_of(data, names, held, fold_only=True).items() if data[n]['keyra']}
    weights = library_weights(names, data)
    settings = config['training']
    started = time.time()
    net = make_net(config, pianos, names, data, arch)
    start_gains(net, train_units)
    train(net, train_units, weights, settings, knob, config['seed'], log=log)
    entry = {'pretrained': score(net, test_units), 'tuned': {}}
    for depth in ('code', 'last'):
        entry['tuned'][depth] = {}
        for p in keyra:
            tuned = fine_tune(net, data, names, p, train_units, weights, settings, knob, config['seed'], depth)
            entry['tuned'][depth].update(score(tuned, {n: us for n, us in test_units.items()
                                                       if data[n]['piano'] == p}))
    entry['seconds'] = round(time.time() - started)
    log(f'done in {entry["seconds"]} s')
    return entry


def cross_validate(config, run, alone, archs, knobs, folds_to_run=None, workers=1, threads=1, log=print):
    """Every architecture, knob and fold not yet finished with these
    settings, `workers` at a time. Results accumulate in
    out/network/<run>/cv.json, each entry's training log in logs/."""
    folder = run_folder(run, alone)
    path = folder / 'cv.json'
    results = json.loads(path.read_text()) if path.exists() else {}
    jobs, tags = [], {}
    for arch in archs:
        for knob in knobs:
            for fold in (folds_to_run if folds_to_run is not None else range(config['folds'])):
                key = f'{arch}:{knob}:{fold}'
                tags[key] = settings_hash(config, {'alone': alone, 'arch': arch, 'knob': knob, 'fold': fold})
                if results.get(key, {}).get('settings') != tags[key]:
                    jobs.append((arch, knob, fold, str(folder / f'logs/cv-{arch}-{knob}-{fold}.log')))
    log(f'{run}: {len(jobs)} cross-validation entries to train, {workers} at a time')

    def done(job, entry):
        arch, knob, fold, _ = job
        key = f'{arch}:{knob}:{fold}'
        entry['settings'] = tags[key]
        results[key] = entry
        path.write_text(json.dumps(results, indent=1, sort_keys=True))
        log(f'{run}: {key} held out, level error ' + ', '.join(
            f'{n} {e["level_db"]:.2f} dB' for n, e in entry['pretrained'].items()) + f' ({entry["seconds"]} s)')
    run_jobs(config, alone, workers, threads, cv_entry, jobs, done)
    return results


def summarise(config, results, archs, knobs):
    """Per architecture and knob, each piano's held-out envelope misfit over
    the folds at its best fine-tuning depth, and the knob settings: character
    (lowest mean over the five) and smooth (largest within one standard
    error)."""
    table = {}
    for arch in archs:
        for knob in knobs:
            per_piano = {}
            for fold in range(config['folds']):
                e = results.get(f'{arch}:{knob}:{fold}')
                if not e:
                    break
                for depth, scores in [('none', e['pretrained'])] + list(e['tuned'].items()):
                    for name, s in scores.items():
                        per_piano.setdefault(name, {}).setdefault(depth, []).append(s['envelope'])
            else:
                table[(arch, knob)] = per_piano
    report = {}
    for (arch, knob), per_piano in table.items():
        best = {n: min(d.items(), key=lambda kv: np.mean(kv[1])) for n, d in per_piano.items()}
        folds = np.mean([v for _, v in best.values()], axis=0)
        mean = float(np.mean(folds))
        report[f'{arch}:{knob}'] = {'mean': mean, 'se': float(np.std(folds, ddof=1) / math.sqrt(len(folds))),
                                    'level_db': decibels(mean), 'depth': {n: d for n, (d, _) in best.items()},
                                    'pianos': {n: decibels(float(np.mean(v))) for n, (_, v) in best.items()}}
    choice = {}
    for arch in archs:
        rows = [(knob, report[f'{arch}:{knob}']) for knob in knobs if f'{arch}:{knob}' in report]
        if not rows:
            continue
        character = min(rows, key=lambda r: r[1]['mean'])
        bound = character[1]['mean'] + character[1]['se']
        smooth = max((r for r in rows if r[1]['mean'] <= bound), key=lambda r: r[0])
        choice[arch] = {'character': character[0], 'smooth': smooth[0], 'mean': character[1]['mean'],
                        'level_db': character[1]['level_db']}
    return report, choice


def print_summary(report, choice):
    for key, r in report.items():
        print(f'{key}: held-out level error {r["level_db"]:.2f} dB (envelope misfit {r["mean"]:.3f} +- '
              f'{r["se"]:.3f}); ' + ', '.join(f'{n} {e:.2f} dB ({r["depth"][n]})' for n, e in r['pianos'].items()))
    for arch, c in choice.items():
        print(f'{arch}: character knob {c["character"]}, smooth knob {c["smooth"]}')


def export(net, path, extra):
    """The weights as NumPy arrays, for a table writer that needs no PyTorch."""
    arrays = {k: v.detach().numpy() for k, v in net.state_dict().items()}
    arrays['meta'] = np.array(json.dumps({'pianos': net.pianos, 'arch': net.arch,
                                          'level_slots': getattr(net, 'level_slots', []), **extra}))
    np.savez_compressed(path, **arrays)


def fit_setting(arch, setting, knob, depth, folder, log_path):
    """One final fit, in a worker: train on every train pitch at the knob,
    fine-tune each Keyra piano at its chosen depth, export the weights and
    score each piano at its train and dev takes."""
    config, names, pianos, data = (_WORKER[k] for k in ('config', 'names', 'pianos', 'data'))
    folder, log = Path(folder), file_log(Path(log_path))
    weights = library_weights(names, data)
    units = units_of(data, names)
    dev = load_dev(config, names, data)
    started = time.time()
    net = make_net(config, pianos, names, data, arch)
    start_gains(net, units)
    train(net, units, weights, config['training'], knob, config['seed'], log=log)
    fits = {'knob': knob, 'pretrained': score(net, units), 'pianos': {}}
    export(net, folder / f'{setting}-shared.npz', {'knob': knob, 'setting': setting})
    for p in keyra_pianos(names, data):
        lib = next(n for n in names if data[n]['keyra'] and data[n]['piano'] == p)
        d = depth.get(lib, 'none')
        tuned = net if d == 'none' else fine_tune(net, data, names, p, units, weights, config['training'],
                                                  knob, config['seed'], d)
        fits['pianos'][p] = {'depth': d, 'train': score(tuned, {lib: units[lib]})[lib],
                             'dev': score(tuned, {lib: dev[lib]})[lib] if lib in dev else None}
        export(tuned, folder / f'{setting}-{p}.npz', {'knob': knob, 'setting': setting, 'depth': d})
    fits['seconds'] = round(time.time() - started)
    log(f'done in {fits["seconds"]} s')
    return fits


def final_fit(config, run, alone, arch, workers=1, threads=1, log=print):
    """Fit on every train pitch at both knob settings cross-validation chose
    for the architecture, fine-tune each piano at its chosen depth, export
    the weights and backtest them on the dev takes (receipt.json)."""
    folder = run_folder(run, alone)
    results = json.loads((folder / 'cv.json').read_text())
    knobs = sorted({float(k.split(':')[1]) for k in results if k.startswith(arch + ':')})
    report, choice = summarise(config, results, [arch], knobs)
    if arch not in choice:
        raise SystemExit(f'{run}: no finished cross-validation for architecture {arch}')
    tag = settings_hash(config, {'alone': alone, 'arch': arch, 'report': report})
    path = folder / 'receipt.json'
    if path.exists() and json.loads(path.read_text()).get('settings') == tag:
        log(f'{run}: final fits of {arch} already done with these settings')
        return json.loads(path.read_text())
    receipt = {'run': run, 'alone': alone, 'arch': arch, 'choice': choice[arch], 'report': report,
               'config': config, 'settings': tag, 'fits': {}}
    settings = {'character': choice[arch]['character'], 'smooth': choice[arch]['smooth']}
    jobs = [(arch, s, k, report[f'{arch}:{k}']['depth'], str(folder), str(folder / f'logs/fit-{s}.log'))
            for s, k in settings.items()]
    log(f'{run}: final fits of {arch}: ' + ', '.join(f'{s} at knob {k}' for s, k in settings.items()))

    def done(job, fits):
        receipt['fits'][job[1]] = fits
        log(f'{run}: {job[1]} fitted; dev takes, level error ' + ', '.join(
            f'{p} {f["dev"]["level_db"]:.2f} dB' for p, f in fits['pianos'].items() if f['dev']))
    run_jobs(config, alone, workers, threads, fit_setting, jobs, done)
    path.write_text(json.dumps(receipt, indent=1, sort_keys=True))
    return receipt


# --- today's tables, and the engine ----------------------------------------

def header_of(name):
    import fit_realtime_modal as fit
    import import_modal_measurements as imm
    return imm.load(fit.MODELS[name]['header'])


def table_prediction(table, b):
    """Today's tables' lanes for every series of the batch, where the engine
    plays them at the anchor, under the same model (the rise unclamped, as
    the fitter fits it); a partial the table does not hold predicts
    nothing."""
    import fit_realtime_modal as fit
    grid = table['grid']
    n = len(b['fd'])
    S = torch.full((n, 8), -1.0 + 0j, dtype=torch.complex128)
    C = torch.zeros((n, 2, 4), dtype=torch.complex128)
    anchors = {a['note']: a for a in table['anchors']}
    for row in range(n):
        a = anchors.get(int(b['note'][row]))
        p = None if a is None else next((q for q in a['partials'] if q['order'] == int(b['order'][row])), None)
        if p is None:
            continue
        v = float(b['velocity'][row])
        rise = p['rise_seconds'] * math.exp(p['rise_slope'] * (v - 64) / 64)
        away = float(pa.stiff(a['f1'], a['B'], p['order'])) * 2 ** (p['cents'] / 1200) - float(b['fd'][row])
        s = np.array([-L['rate'] + 2j * math.pi * (L['offset_hz'] + away) for L in p['lanes']])
        S[row] = torch.from_numpy(np.r_[s, s - 1 / rise])
        for j, L in enumerate(p['lanes']):
            amp = 10 ** (fit.level_at(grid, L['level_db'], v) / 20) * np.exp(1j * fit.phase_at(grid, L['phase'], v))
            C[row, 0, j] = complex(amp * L['left'])
            C[row, 1, j] = complex(amp * L['right'])
    return S, C


@torch.no_grad()
def baseline(config, chunk=40):
    """Today's tables scored at their own train pitches under the same
    losses, the figures a network's train scores compare with. Each library's
    recording term is the network's business, so the tables are given each
    channel's best level first, as start_gains gives an untrained network."""
    out = {}
    for name, info in config['libraries'].items():
        if not info.get('keyra'):
            continue
        groups, _ = load_library(name, info, 0, 0, {})
        table = header_of(name)
        predictions = []
        for b in batches([u for g in groups for u in g['units']], chunk):
            S, C = table_prediction(table, b)
            predictions.append((S, C, b))
        held = [torch.abs(C).sum((1, 2)) > 0 for S, C, b in predictions]
        gain = channel_gain([(b, predicted_frames(b, S, C), h[b['sid']]) for (S, C, b), h in zip(predictions, held)])
        out[name] = scores_of([(S, C * gain[None, :, None], b) for S, C, b in predictions])
        out[name]['gain_db'] = [20 * math.log10(float(g)) for g in gain]
        out[name]['missing'] = int(sum(int((~h).sum()) for h in held))
        e = out[name]
        print(f'{name}: today\'s tables, level error {e["level_db"]:.2f} dB rms (envelope misfit {e["envelope"]:.3f}); '
              f'fitter\'s misfit pooled {e["pooled"]:.3f}, median series {e["median"]:.3f}; '
              f'{e["missing"]} of {e["series"]} partials not in the tables; '
              f'levels moved {e["gain_db"][0]:+.1f}, {e["gain_db"][1]:+.1f} dB', flush=True)
    return out


# --- a correction to the engine's blend -------------------------------------
#
# Between two recorded pitches the engine blends their fits (KeyraEngine.cpp
# blended() and blend()). A correction learns what that blend misses of the
# fits: every recorded pitch of the five pianos is hidden, with up to
# HIDDEN - 1 of its neighbours, and the blend of the recorded pitches around
# them is compared with the hidden pitch's own fit. The pianos recorded every
# 2 to 6 keys (the grand, the upright, the Kawai) so give gaps as wide as the
# Hamburg's 7 and 14 keys and New York's 5 and 10, at pitches whose fits say
# what lies between. For any piano, key, partial and layer level, and the
# gap the key lies in and its place there, it shifts the partial's decay
# rates (in log) and its power in each channel (dB), times 4t(1 - t) at the
# key's place t between the two recorded pitches (`departure`): so it
# vanishes at the recorded pitches, which play their fits as they are. Its
# lanes stay the fits', so no lane decays faster than the fits' do (the first
# run's tables, whose lanes were the network's, put bursts on the upper
# partials that had to be left out).
#
# The fits, not the recordings, are the target: the fits stand off their own
# recordings too, quieter at the upper partials (from the 40th, by a median
# 2.6 to 3.2 dB on the Kawai, the Hamburg and New York), and a correction
# that took the keys between to the recordings would play them brighter than
# the recorded pitches beside them. Against the fits, the blend plays the
# hidden pitches quieter, by a median 0.7 to 1.5 dB per partial over its
# frames on each piano and 0.9 to 4.1 dB from the 16th partial to the 39th,
# and the more the wider the gap: the upright's by 0.1 dB across 2 to 5 keys
# and 5.4 dB across 15 to 21. So the gap is an input, rather than the
# correction being a curve's departure along the keyboard from its chord,
# which grows with the square of the gap alone. The dev takes, which no fit
# holds, are scored against their recordings.
#
# The correction moves each channel's power and the pace of the decay, not
# where the lanes beat, and the blend's beats fall elsewhere than the hidden
# pitch's. Scored frame by frame (envelope_misfit), that pulls it quieter
# and faster: a prediction's nulls sit on the floor whatever its level, so
# lowering it only shrinks its excess at the target's nulls. On the
# Hamburg's partials from the 40th the frame loss falls from 11.66 to
# 10.03 dB with every decay rate 35% faster and 4 dB less power. Trained so,
# the correction played the keys between quieter than the blend alone over
# their first 0.75 s on every piano, by 0.25 to 1.8 dB summed over the
# partials (the Kawai's from 1.5 s by 4 dB more), where the recordings of
# those keys, levelled as the recorded pitches are, put four pianos' louder
# than the blend. So a correction learns each channel's energy over
# POWER_WINDOWS instead, which no beat moves (power_misfit).

HIDDEN = 3            # recorded pitches hidden in a row, at most, in one example
WIDEST = 21           # keys: no example spans more (the Hamburg's widest gap is 14)
HEARD = .4            # KeyraEngine.cpp heard: shareLanes weighs a lane's power by e^(-t/heard)
WINDOW = (.05, .75)   # KeyraEngine.cpp windowPower: the window the layers' levels are measured over
POWER_WINDOWS = (WINDOW, (.75, 1.5), (1.5, 3.5))   # s after contact: a correction's loss weighs each one's energy
POWER_FLOOR = 1e-4    # of a series' energy over the first window: a later one counts down to 40 dB under it
# The knob's units for a correction's figures, as ROUGH's for the network's.
CORRECTION_ROUGH = {'rate_shift': ROUGH['log_rate'], 'level_db': ROUGH['level_db']}


class Correction(torch.nn.Module):
    """What the engine's blend between two recorded pitches misses, for each
    (piano, key, partial, layer level) in a gap of `gap` keys at t of the way
    across it: a shift of the partial's decay rates in log, from the key, the
    partial and its place (the strings), and of its power in each channel in
    dB, from those and the layer level (the strike). The key features and
    each piano's code are the network's (Net)."""

    def __init__(self, pianos, breaks, arch):
        super().__init__()
        self.pianos, self.arch = list(pianos), dict(arch)
        self.register_buffer('breaks', torch.tensor(breaks, dtype=torch.float64).reshape(len(pianos), -1))
        n_key = 1 + 2 * arch['fourier'] + self.breaks.shape[1] + arch['code']
        with torch.random.fork_rng():
            torch.manual_seed(0)
            self.codes = torch.nn.Parameter(.1 * torch.randn(len(pianos), arch['code']))
            self.string = mlp(n_key + 3, arch['width'], arch['depth'])
            self.string_out = torch.nn.Linear(arch['width'], 1)
            self.strike = mlp(arch['width'] + 1, arch['width'], 2)
            self.strike_out = torch.nn.Linear(arch['width'], 2)
        with torch.no_grad():
            # From no correction: the blend as the engine plays it.
            for head in (self.string_out, self.strike_out):
                head.weight.mul_(.1)
                head.bias.zero_()

    key_features = Net.key_features

    def forward(self, piano, note, order, level, gap, t):
        kf = self.key_features(piano, note)
        place = [(torch.log2(order) / 7)[:, None], (torch.log2(gap) / 4)[:, None], (t - .5)[:, None]]
        hidden = self.string(torch.cat([kf, *place], 1))
        strike = self.strike_out(self.strike(torch.cat([hidden, (level / 30)[:, None]], 1)))
        # At most a factor e on the decay rates and 12 dB on a channel's power.
        return {'rate_shift': torch.tanh(self.string_out(hidden)[:, 0]), 'level_db': 12 * torch.tanh(strike)}


def departure(net, piano, note, order, level, lower, upper, t):
    """The correction at each row, between the recorded pitches `lower` and
    `upper`, `t` of the way, times 4t(1 - t): none at either pitch."""
    out = net(piano, note, order, level, upper - lower, t)
    bump = 4 * t * (1 - t)
    return {k: v * (bump[:, None] if v.dim() > 1 else bump) for k, v in out.items()}


def correction_prediction(net, b):
    """The engine's blend at every series of the batch (blend_S, blend_C)
    with the correction's departure applied: every lane's decay rate scaled
    by e^shift, the rise kept, and each channel's power moved."""
    d = departure(net, b['piano'], b['note'], b['order'], b['x'], b['lower'], b['upper'], b['mix'])
    S0 = b['blend_S']
    rise = S0[:, :4] - S0[:, 4:]
    s = torch.complex(S0[:, :4].real * torch.exp(d['rate_shift'])[:, None], S0[:, :4].imag)
    C = b['blend_C'] * (10 ** (d['level_db'] / 20))[:, :, None]
    return torch.cat([s, s - rise], 1), C, torch.zeros(len(b['fd']))


def frame_spans(b):
    """Each frame's share of its series' time: half the way to the frames
    either side of it."""
    t, sid = b['t'], b['sid']
    gap = torch.where(sid[1:] == sid[:-1], t[1:] - t[:-1], torch.zeros_like(t[1:]))
    zero = gap.new_zeros(1)
    return (torch.cat([zero, gap]) + torch.cat([gap, zero])) / 2


def window_energies(b, pw):
    """Each series' energy in each channel over each of POWER_WINDOWS (series
    x windows x 2) from frames pw through the frames' weights, as
    predicted_frames gives a prediction's and b['zw'] holds the measured,
    and how many frames each window holds (series x windows)."""
    t, sid, n = b['t'], b['sid'], len(b['fd'])
    raw = (pw.real ** 2 + pw.imag ** 2) / (b['w'] ** 2)[:, None]
    span = frame_spans(b)
    energy, held = [], []
    for lo, hi in POWER_WINDOWS:
        inside = ((t >= lo) & (t < hi)).to(raw.dtype)
        energy.append(torch.zeros((n, 2), dtype=raw.dtype).index_add(0, sid, raw * (span * inside)[:, None]))
        held.append(torch.zeros(n, dtype=raw.dtype).index_add(0, sid, inside))
    return torch.stack(energy, 1), torch.stack(held, 1)


def window_ratio(b, pw):
    """Each series' predicted (pw) over measured energy in each channel and
    window, in natural log, each floored at POWER_FLOOR of the measured over
    the first window, and which windows hold frames. No take's level is
    taken out: the Keyra pianos' libraries normalise none."""
    if bool(b['normalised'].any()):
        raise ValueError('window_ratio leaves every take its level, and these takes were normalised')
    P, held = window_energies(b, pw)
    M, _ = window_energies(b, b['zw'])
    floor = POWER_FLOOR * M[:, :1, :].mean(2, keepdim=True)
    # A series whose frames all end before the first window (a bass key's
    # highest partials, gone within 50 ms) holds none: a floor of 1 leaves
    # it ratios of 0 and no gradient.
    floor = torch.where(floor > 0, floor, torch.ones_like(floor))
    return torch.log(P + floor) - torch.log(M + floor), held > 0


def series_power_misfit(b, pw):
    r, held = window_ratio(b, pw)
    k = held.to(r.dtype)
    return torch.sum(r ** 2 * k[:, :, None], (1, 2)) / (2 * torch.clamp(k.sum(1), min=1))


def power_misfit(b, S, C):
    """A correction's training loss: each series' mean squared log energy
    ratio over its channels and the windows that hold frames."""
    return series_power_misfit(b, predicted_frames(b, S, C))


@torch.no_grad()
def power_scores(predictions):
    """From (S, C, batch) triples, the mean power_misfit of the series that
    hold a window as an rms error in dB, and each window's mean error (dB,
    signed) over the series' channels: below zero the prediction plays
    quieter than measured."""
    per, total, count = [], torch.zeros(len(POWER_WINDOWS)), torch.zeros(len(POWER_WINDOWS))
    for S, C, b in predictions:
        pw = predicted_frames(b, S, C)
        r, held = window_ratio(b, pw)
        per.append(series_power_misfit(b, pw)[held.any(1)])
        k = held.to(r.dtype)
        total += torch.sum(r * k[:, :, None], (0, 2))
        count += 2 * k.sum(0)
    return {'power_db': decibels(float(torch.cat(per).mean())),
            'window_bias_db': [10 / math.log(10) * float(x) for x in total / torch.clamp(count, min=1)]}


def engine_partial(p, grid, v):
    """single() at velocity v: a fitted partial's lanes as the blend takes
    them (log rate, offset, level, phase, the pickup and its ratio and angle,
    and whether the fit timed its decay) and its log rise. Between the layers
    it leaves out the velocity masks' interpolation (interpolateVelocity)."""
    import fit_realtime_modal as fit
    lanes = []
    for L in p['lanes']:
        right = complex(L['right'])
        lanes.append({'rate': math.log(L['rate']), 'offset': L['offset_hz'], 'level': fit.level_at(grid, L['level_db'], v),
                      'phase': cmath.exp(1j * fit.phase_at(grid, L['phase'], v)),
                      'ratio': math.log(max(1e-6, abs(right)) / max(1e-6, L['left'])),
                      'angle': math.atan2(right.imag, right.real), 'left': complex(L['left']), 'right': right,
                      'identified': L['rate'] > pa.SLOWEST_RATE})
    return {'order': p['order'], 'cents': p['cents'],
            'rise': math.log(p['rise_seconds']) + p['rise_slope'] * (v - 64) / 64, 'lanes': lanes}


def window_terms(d):
    """windowPower's and windowChannels' terms: every pair of d's lanes'
    amplitudes times the window's integral of their product, and the
    pickups."""
    rate = np.exp([L['rate'] for L in d['lanes']])
    offset = np.array([L['offset'] for L in d['lanes']])
    amp = np.array([10 ** (L['level'] / 20) * L['phase'] for L in d['lanes']])
    c = rate[:, None] + rate[None, :] + 2j * math.pi * (offset[None, :] - offset[:, None])
    span = (np.exp(-c * WINDOW[0]) - np.exp(-c * WINDOW[1])) / c
    return (amp[:, None] * np.conj(amp)[None, :] * span, np.array([L['left'] for L in d['lanes']]),
            np.array([L['right'] for L in d['lanes']]))


def window_power(d, left=1.0, right=1.0):
    """windowPower: the partial's power over the window, each channel weighed."""
    A, a, b = window_terms(d)
    return float(np.sum(A * (left * a[:, None] * np.conj(a)[None, :] + right * b[:, None] * np.conj(b)[None, :])).real)


def window_channels(d):
    """windowChannels: the left channel times the conjugate of the right over the window."""
    A, a, b = window_terms(d)
    return complex(np.sum(A * a[:, None] * np.conj(b)[None, :]))


def lane_pairing(a, b):
    """pairing(): which of fitted partial b's lanes each of a's meets, of the
    24 pairings the one whose pairs' log decay rates differ least, each pair
    weighed by the shares of the partial its two lanes carry (shareLanes)."""
    def shares(p):
        power = np.array([[10 ** (db / 10) / (2 * L['rate'] + 1 / HEARD) for db in L['level_db']] for L in p['lanes']])
        total = power.sum(0)
        return np.mean(np.divide(power, total, out=np.zeros_like(power), where=total > 0), 1)
    sa, sb = shares(a), shares(b)
    ra, rb = [math.log(L['rate']) for L in a['lanes']], [math.log(L['rate']) for L in b['lanes']]
    best, least = None, math.inf
    for order in itertools.permutations(range(4)):
        cost = sum((sa[j] + sb[order[j]]) * (ra[j] - rb[order[j]]) ** 2 for j in range(4))
        if cost < least:
            best, least = order, cost
    return best


def rescale(d, kl, kr):
    """Each of d's lanes' left channel scaled by kl in power and its right by
    kr, its level the mean of the two (blend()'s balance)."""
    for L in d['lanes']:
        g = math.exp(L['ratio'])
        L['level'] += 10 * math.log10((kl + kr * g * g) / (1 + g * g))
        L['ratio'] += .5 * math.log(kr / kl)
        h = math.exp(L['ratio'])
        pickup = math.sqrt(2 / (1 + h * h))
        L['left'], L['right'] = complex(pickup), pickup * h * cmath.exp(1j * L['angle'])


def engine_blend(a, b, t, pair):
    """blend(): partials a and b (engine_partial) of two recorded pitches at
    t between them, a's lanes meeting b's by `pair`."""
    def mix(x, y):
        return x + (y - x) * t
    lanes = []
    for j in range(4):
        x, y = a['lanes'][j], b['lanes'][pair[j]]
        ratio, angle = mix(x['ratio'], y['ratio']), x['angle'] if t < .5 else y['angle']
        g = math.exp(ratio)
        left = math.sqrt(2 / (1 + g * g))
        if 0 < t < 1:   # pitchRate: in 1/s, and towards the identified endpoint where one is not
            u = t + t * (1 - t) * (int(y['identified']) - int(x['identified']))
            rate = math.log(math.exp(x['rate']) + (math.exp(y['rate']) - math.exp(x['rate'])) * u)
        else:
            rate = mix(x['rate'], y['rate'])
        lanes.append({'rate': rate, 'offset': mix(x['offset'], y['offset']), 'level': mix(x['level'], y['level']),
                      'phase': x['phase'] if t < .5 else y['phase'], 'ratio': ratio, 'angle': angle,
                      'left': complex(left), 'right': left * g * cmath.exp(1j * angle)})
    lanes.sort(key=lambda L: -L['rate'])
    d = {'order': a['order'], 'cents': mix(a['cents'], b['cents']), 'rise': mix(a['rise'], b['rise']), 'lanes': lanes}
    if not 0 < t < 1:
        return d
    la, lb, ld = (window_power(p, 1, 0) for p in (a, b, d))
    ra, rb, rd = (window_power(p, 0, 1) for p in (a, b, d))
    if min(la, lb, ld, ra, rb, rd) > 0:
        total = (la + ra) ** (1 - t) * (lb + rb) ** t
        balance = mix(math.log(la / ra), math.log(lb / rb))
        low, high = max(min(la, lb), total - max(ra, rb)), min(max(la, lb), total - min(ra, rb))
        share = max(low, min(high, total / (1 + math.exp(-balance))))
        rescale(d, share / ld, (total - share) / rd)
    ca, cb, cd = (window_channels(p) for p in (a, b, d))
    if abs(ca) > 0 and abs(cb) > 0 and abs(cd) > 0:
        start, end = cmath.phase(ca), cmath.phase(cb)
        turn = cmath.phase(cd) - (start + t * math.remainder(end - start, 2 * math.pi))
        for L in lanes:
            L['right'] *= cmath.exp(1j * turn)
            L['angle'] += turn
    return d


def engine_blended(index, table, lower, upper, t, v, pairs):
    """blended(): the partials of the table's recorded pitches `lower` and
    `upper` (anchor indices) merged by order at t between them and velocity
    v: blended where both hold an order, alone at their pitch's share
    otherwise. Per order, (partial, amplitude weight). `index` is the
    piano's place in KeyraEngine.h's Piano; `pairs` caches lane_pairing."""
    a, b = table['anchors'][lower], table['anchors'][upper]
    held = [{p['order']: p for p in x['partials']} for x in (a, b)]
    top = index >= 2 and (len(a['partials']) == 1 or len(b['partials']) == 1) and a['note'] >= 96
    grid, out = table['grid'], {}
    for order in sorted(set(held[0]) | set(held[1])):
        x, y = held[0].get(order), held[1].get(order)
        if x and y:
            key = (lower, upper, order)
            if key not in pairs:
                pairs[key] = lane_pairing(x, y)
            out[order] = (engine_blend(engine_partial(x, grid, v), engine_partial(y, grid, v), t, pairs[key]), 1.0)
        elif x:
            out[order] = (engine_partial(x, grid, v), max(.55, 1 - .45 * t) if top else 1 - t)
        else:
            out[order] = (engine_partial(y, grid, v), max(.55, .55 + .45 * t) if top else t)
    return out


def closed_form(d, weight, gain):
    """A partial as the engine plays it (engine_blended) under the training
    model, at the measured frequency: its complex rates (its lanes, then less
    the rise) and channel amplitudes, in the measurements' units (`gain`, the
    fits' channel gains). The blend's tuning is not the correction's, so it
    is left out."""
    s = np.array([complex(-math.exp(L['rate']), 2 * math.pi * L['offset']) for L in d['lanes']])
    amp = np.array([10 ** (L['level'] / 20) * L['phase'] for L in d['lanes']]) * weight
    C = np.array([amp * np.array([L['left'] for L in d['lanes']]) * gain[0],
                  amp * np.array([L['right'] for L in d['lanes']]) * gain[1]])
    return np.r_[s, s - math.exp(-d['rise'])], C


def subset(u, keep):
    """Unit u with only its series `keep` and their frames."""
    if keep.all():
        return dict(u)
    idx = np.flatnonzero(keep)
    remap = np.full(len(keep), -1)
    remap[idx] = np.arange(len(idx))
    frames = keep[u['sid']]
    e = dict(u)
    for k in ('order', 'fd', 'peak', 'zz'):
        e[k] = u[k][idx]
    for k in ('t', 'zw', 'w'):
        e[k] = u[k][frames]
    e['sid'] = remap[u['sid'][frames]]
    return e


def fitted_unit(u, table, gain):
    """Unit u at a recorded pitch with its fit's frames in place of its
    recording's (the fit at the measured frequency, as closed_form gives the
    blend), and only the series the fit holds."""
    fits = {p['order']: p for p in next(a for a in table['anchors'] if a['note'] == u['group']['note'])['partials']}
    e = subset(u, np.array([int(o) in fits for o in u['order']]))
    if not len(e['order']):
        return None
    forms = [closed_form(engine_partial(fits[int(o)], table['grid'], float(u['velocity'])), 1.0, gain) for o in e['order']]
    b = batch_of([e])
    pw = predicted_frames(b, torch.from_numpy(np.array([f[0] for f in forms])), torch.from_numpy(np.array([f[1] for f in forms])))
    e['zw'] = pw.numpy()
    e['zz'] = np.bincount(e['sid'], np.sum(np.abs(e['zw']) ** 2, axis=1), minlength=len(e['order']))
    return e


def correction_examples(name, groups, gain, dev=False):
    """A Keyra piano's units as a correction trains or is scored on them: at
    a train pitch, its fit (fitted_unit), once for every way of hiding it with
    up to HIDDEN - 1 of its neighbours in a row across no more than WIDEST
    keys, with the blend of the recorded pitches around them; at a dev take
    strictly between two recorded pitches (`dev`), its recording, with their
    blend. A series the blend does not hold is left out."""
    table = header_of(name)
    notes = [a['note'] for a in table['anchors']]
    index, pairs, out = ENGINE_PIANOS.index(name), {}, []
    for g in groups:
        k = g['note']
        if dev:
            if k in notes or not notes[0] < k < notes[-1]:
                continue
            upper = next(i for i, n in enumerate(notes) if n > k)
            spans = [(upper - 1, upper)]
            units = g['units']
        elif k in notes:
            i = notes.index(k)
            spans = [(lo, hi) for lo in range(max(0, i - HIDDEN), i) for hi in range(i + 1, min(len(notes), i + HIDDEN + 1))
                     if hi - lo - 1 <= HIDDEN and notes[hi] - notes[lo] <= WIDEST]
            units = [f for f in (fitted_unit(u, table, gain) for u in g['units']) if f is not None]
        else:
            continue
        for lo, hi in spans:
            t = (k - notes[lo]) / (notes[hi] - notes[lo])
            for u in units:
                blends = engine_blended(index, table, lo, hi, t, float(u['velocity']), pairs)
                keep = np.array([int(o) in blends for o in u['order']])
                if not keep.any():
                    continue
                e = subset(u, keep)
                forms = [closed_form(*blends[int(o)], gain) for o in e['order']]
                e.update(blend_S=np.array([f[0] for f in forms]), blend_C=np.array([f[1] for f in forms]),
                         lower=notes[lo], upper=notes[hi], mix=t)
                out.append(e)
    return out


def all_examples(config, names, data, gains):
    """Every Keyra library's train and dev examples (correction_examples)."""
    out = {'train': {}, 'dev': {}}
    dev = load_dev(config, names, data)
    for name in names:
        if not data[name]['keyra']:
            continue
        gain = 10 ** (np.asarray(gains[name]) / 20)
        out['train'][name] = correction_examples(name, data[name]['groups'], gain)
        if name in dev:
            groups = list({id(u['group']): u['group'] for u in dev[name]}.values())
            out['dev'][name] = correction_examples(name, groups, gain, dev=True)
    return out


@torch.no_grad()
def blend_scores(examples, chunk=40):
    """The engine's blend alone at a library's examples, scored as
    correction_scores scores a correction."""
    predictions = [(b['blend_S'], b['blend_C'], b) for b in batches(examples, chunk)]
    return {**scores_of(predictions), **power_scores(predictions)}


@torch.no_grad()
def correction_scores(net, examples, chunk=40):
    """A correction at a library's examples: `score`'s scores and the power scores."""
    predictions = [network_prediction(net, b)[:2] + (b,) for b in batches(examples, chunk)]
    return {**scores_of(predictions), **power_scores(predictions)}


def correction_entry(arch, knob, folder, log_path):
    """One correction, in a worker: trained at `knob` on every Keyra piano's
    train examples, exported, and scored beside the blend alone at the train
    and dev examples."""
    config, pianos, data, examples = (_WORKER[k] for k in ('config', 'pianos', 'data', 'examples'))
    log = file_log(Path(log_path))
    names = sorted(examples['train'])
    weights = {data[n]['index']: 1.0 for n in names}
    started = time.time()
    net = Correction(pianos, [[config['pianos'][p]['tenor']] for p in pianos], config['architectures'][arch])
    train(net, examples['train'], weights, config['training'], knob, config['seed'], log=log)
    export(net, Path(folder) / f'correction-{arch}-{knob:g}.npz', {'knob': knob, 'correction': True})
    entry = {}
    for role, units in examples.items():
        entry[role] = {}
        for name, us in units.items():
            blend = blend_scores(us)
            entry[role][name] = {**correction_scores(net, us),
                                 **{'blend_' + k: blend[k] for k in ('level_db', 'power_db', 'window_bias_db')}}
    entry['seconds'] = round(time.time() - started)
    log(f'done in {entry["seconds"]} s')
    return entry


def corrections(config, run, archs, knobs, gains, workers=1, threads=1, log=print):
    """Every correction not yet trained with these settings, `workers` at a
    time; results in out/network/<run>/correction.json."""
    folder = run_folder(run, True)
    path = folder / 'correction.json'
    results = json.loads(path.read_text()) if path.exists() else {}
    jobs, tags = [], {}
    for arch in archs:
        for knob in knobs:
            key = f'{arch}:{knob:g}'
            tags[key] = settings_hash(config, {'correction': True, 'arch': arch, 'knob': knob, 'gains': gains,
                                               'hidden': HIDDEN, 'widest': WIDEST})
            if results.get(key, {}).get('settings') != tags[key]:
                jobs.append((arch, knob, str(folder), str(folder / f'logs/correction-{arch}-{knob:g}.log')))
    log(f'{run}: {len(jobs)} corrections to train, {workers} at a time')

    def done(job, entry):
        key = f'{job[0]}:{job[1]:g}'
        entry['settings'] = tags[key]
        results[key] = entry
        path.write_text(json.dumps(results, indent=1, sort_keys=True))
        log(f'{run}: {key} dev takes, power error ' + ', '.join(
            f'{n} {e["power_db"]:.2f} dB (blend {e["blend_power_db"]:.2f})' for n, e in entry['dev'].items())
            + f' ({entry["seconds"]} s)')
    run_jobs(config, True, workers, threads, correction_entry, jobs, done, gains)
    return results


# How today's engine plays a take for the backtest: keyra_render's arguments
# beside the events, the output and the duration. Resonance and mechanics are
# off, as for `check`: their sounds are not partials of the struck key.
ENGINE_ARGS = ['--gain', '.07', '--resonance', '0', '--mechanics', '0', '--quality', 'full']


def engine_unit(renderer, name, u):
    """Today's engine at one take: keyra_render plays the take's key at its
    velocity, and the render is measured at the take's own partial
    frequencies, window and frame times after contact, through the take's
    frame weights (frames x 2, as predicted_frames gives a network's)."""
    g = u['group']
    sr, length = g['sr'], g['length']
    times = np.unique(u['t'])
    with tempfile.TemporaryDirectory() as tmp:
        events, wav = Path(tmp) / 'take.events', Path(tmp) / 'take.wav'
        events.write_text(f'{LEAD} on {g["note"]} {u["velocity"]:g}\n')
        seconds = LEAD + times[-1] + length / sr + 1.0
        subprocess.run([str(renderer), '--events', str(events), '--output', str(wav), '--duration', f'{seconds:.3f}',
                        '--sample-rate', str(sr), '--model', name, *ENGINE_ARGS], check=True,
                       stdout=subprocess.DEVNULL)
        _, x = pa.load(wav)
    start = pa.onset(x, sr)
    # A take's first frames come before its contact, some before its onset:
    # frames are timed from the file's start, which LEAD keeps silent.
    contact = start / sr + pa.contact_delay(x, sr, start)
    t, z = pa.envelopes(x, sr, u['fd'], g['f1'], 0, None, times=times + contact, length=length)
    if len(t) != len(times):
        raise RuntimeError(f'{name} {g["note"]}: the render of velocity {u["velocity"]:g} ended early')
    return z[u['sid'], :, np.searchsorted(times, u['t'])] * u['w'][:, None]


def velocity_colour(table, v, order):
    """The tilt of the engine's additional velocity colour on each partial's
    amplitude at velocity v (KeyraEngine.cpp additionalVelocityColour: by the
    owner's choice the tone answers velocity more strongly than the
    recordings do), before colour_scale."""
    import fit_realtime_modal as fit
    grid = table['grid']
    db = COLOUR * (fit.level_at(grid, table['layer_level'], v) - fit.level_at(grid, table['layer_level'], 100))
    return 10 ** (db * np.minimum(4.0, np.log2(order)) / 20)


def colour_scale(table, anchor, v, sr):
    """The scale KeyraEngine.cpp puts on a whole strike of one recorded pitch
    after its colour's tilt (`plain` and `coloured`), so that the strike's
    energy to silence stays where the uncoloured lanes put it: the series and
    the components beside it, up to the engine's highest partial. Without it
    the tilt alone scores the upright's shipped engine 8.5 dB where the
    render scores 7.0; with it the closed form scores 7.1."""
    import fit_realtime_modal as fit
    grid, top = table['grid'], min(TOP_HZ, .43 * sr)
    plain = coloured = 0.0
    for p in anchor['partials'] + anchor['extras']:
        if float(pa.stiff(anchor['f1'], anchor['B'], p['order'])) * 2 ** (p['cents'] / 1200) > top:
            continue
        c2 = float(velocity_colour(table, v, p['order'])) ** 2
        for L in p['lanes']:
            e = 10 ** (fit.level_at(grid, L['level_db'], v) / 10) * (abs(L['left']) ** 2 + abs(L['right']) ** 2) \
                / -math.expm1(-2 * L['rate'] / sr)
            plain += e
            coloured += e * c2
    return math.sqrt(plain / coloured) if coloured > 0 else 1.0


def engine_frames(renderer, name, roles, workers, log):
    """Today's engine rendered and measured at every take of `roles`
    (engine_unit), cached in out/keyboard-engine/<library>.npz by the
    renderer's bytes, how a take is rendered and measured, and the takes'
    measurements, so that scoring can change without rendering again."""
    import inspect
    key = hashlib.sha256(json.dumps([
        hashlib.sha256(Path(renderer).read_bytes()).hexdigest(), inspect.getsource(engine_unit), ENGINE_ARGS, LEAD,
        hashlib.sha256(Path(pa.__file__).read_bytes()).hexdigest(),
        {role: [f'{u["group"]["cache_key"]}:{u["velocity"]:g}' for u in units] for role, units in roles.items()},
    ]).encode()).hexdigest()[:16]
    cache = ENGINE / f'{name}.npz'
    if cache.exists():
        with np.load(cache) as f:
            if str(f['key']) == key:
                return {role: [f[f'{role}_{i}'] for i in range(len(units))] for role, units in roles.items()}
    log(f'{name}: rendering today\'s engine at {len(roles["train"])} train and {len(roles["dev"])} dev takes')
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        frames = {role: list(pool.map(lambda u: engine_unit(renderer, name, u), units))
                  for role, units in roles.items()}
    ENGINE.mkdir(parents=True, exist_ok=True)
    part = ENGINE / f'{name}.part.npz'
    np.savez(part, key=np.array(key), **{f'{role}_{i}': x for role, xs in frames.items() for i, x in enumerate(xs)})
    part.replace(cache)
    return frames


@torch.no_grad()
def engine(config, renderer, workers=4, log=print):
    """Today's engine as it ships at each Keyra piano's train and dev takes,
    scored as the network is. Each channel's level is set where the train
    takes fit best and kept for the dev takes, as a network's recording term
    is. Beside its tables the engine plays its own voicing: the additional
    velocity colour, the per-key loudness trims and the strike's noise,
    knocks and undamped strings, none of which a network's closed form holds.
    Dividing the colour back out of a render divides it out of the noise
    too, which it never coloured: where the colour cuts deepest, the soft
    layers' upper partials, the noise then stands 20 to 35 dB over the take,
    and the New York grand scored worse without its colour than with it. So
    only the shipped engine is scored; today's tables alone are `baseline`'s."""
    out = {}
    for name, info in config['libraries'].items():
        if not info.get('keyra'):
            continue
        groups, _ = load_library(name, info, 0, 0, {})
        dev = load_library(name, info, 0, 0, {}, root=DEV, reference=groups)[0] if any((DEV / name).glob('*.pkl')) \
            else []
        roles = {'train': [u for g in groups for u in g['units']], 'dev': [u for g in dev for u in g['units']]}
        frames = engine_frames(renderer, name, roles, workers, log)
        b = batch_of(roles['train'])
        gain = channel_gain([(b, torch.from_numpy(np.concatenate(frames['train'])),
                              torch.ones(len(b['t']), dtype=torch.bool))])
        e = {'gain_db': [20 * math.log10(float(v)) for v in gain]}
        for role, units in roles.items():
            if units:
                b = batch_of(units)
                env = series_misfit(b, power_ratio(b, torch.from_numpy(np.concatenate(frames[role])) * gain))
                e[role] = {'envelope': float(env.mean()), 'level_db': decibels(float(env.mean())),
                           'series': len(env), 'takes': len(units)}
        out[name] = e
        log(f'{name}: today\'s engine, level error {e["train"]["level_db"]:.2f} dB at the train takes, '
            + (f'{e["dev"]["level_db"]:.2f} dB at the dev takes' if 'dev' in e else 'no dev takes measured'))
    return out


# The engine's Model::contactTime (KeyraEngine.cpp): no partial rises slower
# than it, scaled by 2^(-(note-60)/24); the grand measures none.
CONTACT = {'grand': 0.0, 'upright': .002, 'kawai': .002, 'hamburg': .002, 'newyork': .002}
COLOUR = .4            # KeyraEngine.cpp additionalVelocityColour
LEAD = .05             # s of silence before each checked strike
FLOOR_DB = -130.0      # dBFS: the floor added to renders, as a recording has one


def check_anchor(renderer, name, note, table):
    """One anchor of today's tables played by keyra_render at every layer,
    measured as a recording is (keyboard_measurements.measure_anchor), against
    the training model's closed form with the engine's own rise limits and
    velocity colour. Returns per layer the render's gain, the median relative
    error over the partials (all frames, and from 0.3 s, after the strike's
    noise) and how far the first eight partials' own gains stray from it, at
    the median and at the partial that strays furthest."""
    import keyboard_measurements as km
    from scipy.io import wavfile
    grid_v = table['grid']
    anchor = next(a for a in table['anchors'] if a['note'] == note)
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for i, v in enumerate(grid_v):
            events, wav = Path(tmp) / f'{i}.events', Path(tmp) / f'{i}.wav'
            events.write_text(f'{LEAD} on {note} {v}\n')
            subprocess.run([str(renderer), '--events', str(events), '--output', str(wav), '--duration', '8',
                            '--model', name, '--gain', '.07', '--resonance', '0', '--mechanics', '0',
                            '--quality', 'full'], check=True, stdout=subprocess.DEVNULL)
            # A render has no floor, and the engine drops a partial whose
            # energy falls under 1e-15, which a floorless measurement would
            # weigh without bound: add a fixed one, as a recording has.
            sr, x = pa.load(wav)
            x = x + 10 ** (FLOOR_DB / 20) * np.random.default_rng(i).standard_normal(x.shape)
            wavfile.write(wav, sr, x.astype(np.float32))
            paths.append(wav)
        m = km.measure_anchor(paths, note, list(grid_v))
    sr, length = m['sr'], m['length']
    grid, profile = pa.window_profile(m['f1'], sr, min(.002, length / sr / 24), length)
    partials = {p['order']: p for p in anchor['partials']}
    contact = CONTACT[name] * 2 ** (-(note - 60) / 24)
    top = min(TOP_HZ, .43 * sr)
    rows_out = []
    for i, v in enumerate(grid_v):
        L = m['layers'][i]
        onset = L['start'] / sr
        scale = colour_scale(table, anchor, v, sr)
        rows, orders = [], []
        for k, n in enumerate(m['orders']):
            s_, p = m['series'][k][i], partials.get(n)
            fn = float(pa.stiff(anchor['f1'], anchor['B'], n)) * 2 ** (p['cents'] / 1200) if p else 0.0
            if s_ is None or p is None or fn > top:
                continue
            fd = float(m['freqs'][k])
            rise = p['rise_seconds'] * math.exp(p['rise_slope'] * (v - 64) / 64)
            if contact > 0:
                rise = min(rise, contact)
            rise = max(rise, anchor['onset_rise'][i])
            colour = float(velocity_colour(table, v, n)) * scale
            tau = s_['t'].astype(float) + (onset + L['delay'] - LEAD)
            response = pa._WindowedExponentials(tau, grid, profile)
            s = np.array([-q['rate'] + 2j * math.pi * (fn + q['offset_hz'] - fd) for q in p['lanes']])
            B, _ = response(np.r_[s, s - 1 / rise])
            a = np.array([10 ** (q['level_db'][i] / 20) * colour * np.exp(1j * q['phase'][i])
                          * np.array([q['left'], q['right']]) for q in p['lanes']])
            pred = ((B[:, :4] - B[:, 4:]) @ a).T * np.exp(-2j * math.pi * fd * (LEAD - onset))
            rows.append((pred * s_['w'], s_['z'] * s_['w'], s_['t'] >= .3))
            orders.append(n)
        P = np.concatenate([r[0] for r in rows], axis=1)
        Z = np.concatenate([r[1] for r in rows], axis=1)
        gain = float(np.vdot(P, Z).real / np.vdot(P, P).real)
        rel = [np.sum(np.abs(zw - gain * pw) ** 2) / np.sum(np.abs(zw) ** 2) for pw, zw, _ in rows]
        late = [np.sum(np.abs(zw[:, k] - gain * pw[:, k]) ** 2) / np.sum(np.abs(zw[:, k]) ** 2)
                for pw, zw, k in rows if k.sum() >= 4]
        own = np.array([np.vdot(pw, zw) / np.vdot(pw, pw) / gain for pw, zw, _ in rows[:8]])
        stray = np.abs(20 * np.log10(np.abs(own)))
        worst = int(np.argmax(stray))
        rows_out.append({'layer': i + 1, 'velocity': v, 'gain_db': 20 * math.log10(abs(gain)),
                         'median': float(np.median(rel)), 'late': float(np.median(late)) if late else None,
                         'stray_db': float(np.median(stray)), 'worst_order': orders[worst],
                         'worst_db': float(stray[worst]), 'worst_deg': float(abs(np.degrees(np.angle(own[worst]))))})
    return rows_out


def check(config, renderer, notes=None):
    """The closed form the network is trained through against the engine, at
    each Keyra piano's lowest, middle and highest train anchors. It passes
    where, at an anchor's loudest layer, the median partial's relative error
    is under 0.05 and the first eight partials' gains stay, at the median,
    within 1 dB of the layer's: the lanes then play as the closed form says.
    Softer layers are reported, not judged: their strike noise, the bass's
    body modes and the undamped strings are not in the closed form.

    The first eight are judged at the median, not one by one, because the
    lowest keys' fundamental, 29 to 47 dB under their strongest partial,
    shares the analysis window's half-power band with one of the body's
    lowest modes, which every strike knocks: on the grand A0 has a mode 2.2 Hz
    from it and strays 1.5 dB, on the New York grand C1 has one 2.8 Hz from it
    and strays 4.2 dB and 107 degrees, while the Hamburg grand's C1, whose
    nearest mode is 8 Hz away, stays within 0.5 dB. A fault in how the engine
    plays its lanes moves most of the eight; the one straying furthest is
    printed."""
    failed = []
    for name, info in config['libraries'].items():
        if not info.get('keyra'):
            continue
        table = header_of(name)
        anchors = [a['note'] for a in table['anchors']]
        picks = notes.get(name) if notes else [anchors[0], anchors[len(anchors) // 2], anchors[-1]]
        for note in picks:
            rows = check_anchor(renderer, name, note, table)
            print(f'{name} {note}:')
            for r in rows:
                print(f'  layer {r["layer"]:2d} v{r["velocity"]:3g}: gain {r["gain_db"]:+6.2f} dB, median relative '
                      f'error {r["median"]:.1e} (from 0.3 s {r["late"] if r["late"] is None else round(r["late"], 4)}),'
                      f' first 8 partials within {r["stray_db"]:.2f} dB at the median, partial {r["worst_order"]}'
                      f' furthest at {r["worst_db"]:.2f} dB, {r["worst_deg"]:.1f} deg', flush=True)
            loud = rows[-1]
            if loud['median'] > .05 or loud['stray_db'] > 1.0:
                failed.append(f'{name} {note}')
    print('check: ' + ('passed' if not failed else 'FAILED at ' + ', '.join(failed)))
    return not failed


# --- the whole run, and its report ------------------------------------------

def best_arch(config, results, knob):
    """The architecture whose held-out envelope misfit is lowest at `knob`."""
    _, choice = summarise(config, results, list(config['architectures']), [knob])
    if not choice:
        raise SystemExit(f'no architecture has finished its cross-validation at knob {knob}')
    return min(choice, key=lambda a: choice[a]['mean'])


def run_all(config, run, alone, workers, threads, renderer, log=print):
    """Every step of a run, unattended, each resuming what is already done:
    the self-test, the measurements, the check of the closed form against
    the engine, today's tables and engine scored, cross-validation of every
    architecture at the smallest knob and of every knob at the best one, the
    final fits with their dev backtest, and the report."""
    folder = run_folder(run, alone)
    log(f'{run}: self-test')
    subprocess.run([sys.executable, '-B', str(SELFTEST)], check=True)
    measure(config, workers)
    if not check(config, renderer):
        raise SystemExit(f'{run}: the closed form no longer plays as the engine does (the check above)')
    (folder / 'baseline.json').write_text(json.dumps(baseline(config), indent=1))
    (folder / 'engine.json').write_text(json.dumps(engine(config, renderer, workers, log), indent=1))
    knobs = sorted(config['knobs'])
    results = cross_validate(config, run, alone, list(config['architectures']), knobs[:1], None, workers, threads,
                             log)
    arch = best_arch(config, results, knobs[0])
    log(f'{run}: architecture {arch} predicts the held-out pitches best; every knob next')
    cross_validate(config, run, alone, [arch], knobs, None, workers, threads, log)
    final_fit(config, run, alone, arch, workers, threads, log)
    log(f'{run}: report in {write_report(config, run)}')


def write_report(config, run):
    """out/network/<run>/report.md and report.json from what the run holds:
    today's tables and engine, the cross-validation and the dev backtest."""
    folder = RUNS / run

    def read(name):
        return json.loads((folder / name).read_text()) if (folder / name).exists() else None
    results, receipt, base, eng = read('cv.json') or {}, read('receipt.json'), read('baseline.json'), \
        read('engine.json')
    report, choice = summarise(config, results, list(config['architectures']), sorted(config['knobs']))
    pianos = [n for n, i in config['libraries'].items() if i.get('keyra')]

    def db(x):
        return '' if x is None else f'{x:.2f}'

    def get(d, *path):
        for k in path:
            d = d.get(k) if isinstance(d, dict) else None
        return d
    alone = (read('run.json') or {}).get('alone')
    lines = [f'# Keyboard network: run {run}', '',
             f'Learns from {"the five Keyra pianos alone" if alone else "every library in the settings"}. '
             'Every figure is the rms level error of every partial\'s frames against the recording, in dB '
             '(Tools/keyboard_network.py: lower is better).', '',
             '## Today', '',
             'Today\'s tables in closed form at their own train pitches, and today\'s engine as it ships, rendered '
             'at the train and dev takes with its own voicing (velocity colour, per-key trims, strike noise).', '',
             '| Piano | Tables, closed form, train | Engine, train | Engine, dev |', '| --- | --- | --- | --- |']
    for p in pianos:
        lines.append(f'| {p} | {db(get(base, p, "level_db"))} | {db(get(eng, p, "train", "level_db"))} | '
                     f'{db(get(eng, p, "dev", "level_db"))} |')
    lines += ['', '## Cross-validation', '',
              'Held-out train pitches, each piano at its best fine-tuning depth (none, its code, or its code '
              'and the last layers).', '',
              '| Architecture : knob | Level error | Envelope misfit | ' + ' | '.join(pianos) + ' |',
              '| --- | --- | --- | ' + ' | '.join('---' for _ in pianos) + ' |']
    for key, r in report.items():
        lines.append(f'| {key} | {r["level_db"]:.2f} | {r["mean"]:.3f} ± {r["se"]:.3f} | ' + ' | '.join(
            f'{db(r["pianos"].get(p))} ({r["depth"].get(p, "")})' for p in pianos) + ' |')
    for arch, c in choice.items():
        lines.append(f'\n{arch}: character knob {c["character"]}, smooth knob {c["smooth"]}.')
    if receipt:
        lines += ['', '## Backtest on the dev takes', '',
                  f'Architecture {receipt["arch"]}, fitted on every train pitch and fine-tuned to each piano at the '
                  'depth in brackets; the dev takes are never trained on. The network is scored in closed form and '
                  'today\'s engine as rendered with its own voicing, so each compares with itself from train to dev '
                  'takes until the table writer renders the network\'s tables too.', '',
                  '| Piano | Tables, closed form, train | Character, train | Character, dev | Smooth, train | '
                  'Smooth, dev | Engine, train | Engine, dev |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
        fits = receipt['fits']
        for p in pianos:
            lines.append(f'| {p} | {db(get(base, p, "level_db"))} | ' + ' | '.join(
                f'{db(get(fits, s, "pianos", p, "train", "level_db"))} ({get(fits, s, "pianos", p, "depth")}) | '
                f'{db(get(fits, s, "pianos", p, "dev", "level_db"))}' for s in ('character', 'smooth'))
                + f' | {db(get(eng, p, "train", "level_db"))} | {db(get(eng, p, "dev", "level_db"))} |')
    (folder / 'report.md').write_text('\n'.join(lines) + '\n')
    (folder / 'report.json').write_text(json.dumps({'baseline': base, 'engine': eng, 'cv': report, 'choice': choice,
                                                    'fits': receipt and receipt['fits']}, indent=1, sort_keys=True))
    return folder / 'report.md'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('stage', choices=['all', 'measure', 'check', 'baseline', 'engine', 'cv', 'fit', 'report',
                                          'correct'])
    parser.add_argument('--config', default=str(CONFIG))
    parser.add_argument('--run', help='the run folder under out/network')
    parser.add_argument('--alone', action='store_true', help='the five pianos alone, no base library')
    parser.add_argument('--arch', nargs='+', help='architectures (default: every one in the settings; for fit, '
                                                  'the one cross-validation found best)')
    parser.add_argument('--knob', nargs='+', type=float, help='knob values (default: the settings\')')
    parser.add_argument('--folds', nargs='+', type=int, help='folds to run (default: all)')
    parser.add_argument('--workers', type=int, default=4, help='processes measuring, rendering or training at once')
    parser.add_argument('--threads', type=int, default=1, help='PyTorch threads per training process')
    parser.add_argument('--renderer', default=str(ROOT / 'build-dsp/keyra_render'))
    parser.add_argument('--baseline', default=str(ROOT / 'Docs/research/keyboard-network-2026-11-04/baseline.json'),
                        help='for correct: the fits\' channel gains (`baseline`)')
    args = parser.parse_args()
    config = load_config(args.config)
    torch.set_num_threads(args.threads)
    archs = args.arch or list(config['architectures'])
    knobs = args.knob or config['knobs']
    renderer = Path(args.renderer)
    if args.stage == 'measure':
        measure(config, args.workers)
    elif args.stage == 'check':
        raise SystemExit(0 if check(config, renderer) else 1)
    elif args.stage == 'baseline':
        baseline(config)
    elif args.stage == 'engine':
        engine(config, renderer, args.workers)
    else:
        if not args.run:
            raise SystemExit(f'{args.stage} needs --run')
        if args.stage == 'all':
            run_all(config, args.run, args.alone, args.workers, args.threads, renderer)
        elif args.stage == 'cv':
            results = cross_validate(config, args.run, args.alone, archs, knobs, args.folds, args.workers,
                                     args.threads)
            print_summary(*summarise(config, results, archs, knobs))
        elif args.stage == 'fit':
            results = json.loads((RUNS / args.run / 'cv.json').read_text())
            for arch in args.arch or [best_arch(config, results, min(config['knobs']))]:
                final_fit(config, args.run, args.alone, arch, args.workers, args.threads)
        elif args.stage == 'report':
            results = json.loads((RUNS / args.run / 'cv.json').read_text())
            print_summary(*summarise(config, results, archs, sorted(knobs)))
            print(f'report in {write_report(config, args.run)}')
        elif args.stage == 'correct':
            gains = {n: e['gain_db'] for n, e in json.loads(Path(args.baseline).read_text()).items()}
            corrections(config, args.run, archs, knobs, gains, args.workers, args.threads)


if __name__ == '__main__':
    main()
