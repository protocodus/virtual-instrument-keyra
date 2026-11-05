#!/usr/bin/env python3
"""Measure the beat in each piano's undamped strings on the train takes of
its locked split (fit_realtime_modal.MODELS) and write it into
Source/DSP/MeasuredHaloBeats.h.

The strings from F6 up have no dampers, so every strike sets them ringing
through the bridge (fit_realtime_modal.halo_data), and the engine plays each
as one tone at its pitch: a prompt part the bridge drains within a few tenths
of a second, then its aftersound. A struck unison's strings, mistuned and
coupled through the bridge, ring as components a few tenths of a hertz to a
few hertz apart, which beat (G. Weinreich, "Coupled piano strings", JASA 62,
1977), and so do the undamped strings the bridge sets ringing. Where the
takes decide a string's beat, its aftersound plays as two components.

Each train take of a pitch from HALO_LOWEST up, at every undamped string but
the struck key's own, where no partial of the struck key's series lies within
HALO_APART of it (the tone there is that partial's) and the string's tone at
1 s stands ENVELOPE_CLEAR over its surroundings (halo_tone, through the halo
fit's 0.5 s window), so that it still stands over the room's noise at 3 s:
- its envelope: the take demodulated at the string's pitch as the engine
  plays it (the header's anchors and halo cents), both channels, low-passed at
  LOWPASS (zero phase, which rejects the strings and partials HALO_APART away)
  and read RATE times a second from START, past the prompt part (the pianos'
  prompts fall 13 to 34 dB by then), to END;
- its two components by ESPRIT, the poles both channels share and each one's
  amplitude per channel by least squares: the second's offset from the first
  (the stronger at START), its level against the first at START and its
  phase against the first at contact, both channels, in the analytic signal's
  sense and turned to a second component above the first (which side it lies
  on is not heard: the envelope is the same).
A string's beat is the median offset and level over its envelopes and the
circular mean of their phases. The engine plays both components at the
string's one rate, so each envelope is scored as unexplained energy: one
component, its amplitude per channel, its rate and its offset fitted, against
the two at the beat with the same freedom.

The takes decide a string's beat where it carries over between the struck
pitches: each train pitch's envelopes are scored at the beat the string's
other train pitches give, and so many pitches score better with it (their
envelopes' mean log ratio under 0) that tossed coins would show as many in
SIGN_P of draws or fewer (the one-sided sign test). Elsewhere the string
keeps one component.

The halo fit reads a string as one tone through the HALO_TIMES windows: its
rate from the fall between the first window and the last, its level from the
windows brought back to contact at that rate. Read so, a beat changes the
fall: each train envelope's own two components read a decided string falling
faster by a median of a dB or two (fall_bias_db), so the rate the fit gives
the string holds the beat's share. The two components therefore fall at the
rate (the string's times rate_scale) at which, read the same way, they fall
as the fit fitted the string, and the first stands at the level (first_db) at
which they read the level it fitted.

The dev takes score each decided beat on their envelopes, measured the same
way: scored, never fitted.

  python3 Tools/fit_halo_beats.py           # measure every piano, write the header and the receipt
  python3 Tools/fit_halo_beats.py --check   # the receipt is current and the header is the one it gives
"""
from __future__ import annotations

import argparse
import json
import math
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
from scipy import optimize, signal

import fit_realtime_modal as fit
import import_modal_measurements as imm
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredHaloBeats.h'
RECEIPT = ROOT / 'Docs/research/halo-beats-2026-11-05.json'
PIANOS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork')
START, END = .3, 3.0     # s after contact: the envelope
RATE = 100               # Hz: its frames
LOWPASS = 4.0            # Hz
ENVELOPE_CLEAR = 20.0    # dB over the tone's surroundings at 1 s
SIGN_P = .05             # the sign test's level
SILENT = -200.0          # dB: no second component


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def halo_pitches(table):
    """Each undamped key's string pitch as the engine plays it: the anchors'
    pitches as the engine interpolates them, at the header's halo cents."""
    strings = fit.string_pitches({a['note']: a['f1'] for a in table['anchors']})
    return {key: strings[key] * 2 ** (cents / 1200) for key, cents in zip(table['halo']['keys'], table['halo']['cents'])}


def envelope(x, sr, contact, hz, end):
    """The take at hz, both channels: complex demodulation, a LOWPASS
    low-pass, read RATE times a second from START to END after contact."""
    a = max(int(contact + START * sr) - int(.5 * sr), 0)
    b = min(int(contact + END * sr) + int(.5 * sr), end)
    if b - a < int((END - START) * sr):
        return None, None
    t = np.arange(a, b) / sr
    y = x[a:b] * np.exp(-2j * np.pi * hz * t)[:, None]
    y = signal.sosfiltfilt(signal.butter(4, LOWPASS, 'lowpass', fs=sr, output='sos'), y, axis=0)
    step = sr // RATE
    times = (np.arange(a, b, step) - contact) / sr
    keep = (times >= START) & (times <= END)
    return times[keep], y[::step][keep]


def esprit(z, order):
    """The poles both channels' envelopes z (frames x 2) share, and each
    pole's amplitude per channel by least squares."""
    n = len(z)
    m = n // 2
    H = np.hstack([np.array([z[i:i + m, c] for i in range(n - m + 1)]).T for c in range(z.shape[1])])
    U = np.linalg.svd(H, full_matrices=False)[0][:, :order]
    poles = np.linalg.eigvals(np.linalg.pinv(U[:-1]) @ U[1:])
    amps = np.linalg.lstsq(np.vander(poles, n, increasing=True).T, z, rcond=None)[0]
    return poles, amps


def components(times, z):
    """The envelope's two components: the second's offset from the first
    (Hz), its level against the first at START (dB) and its amplitude
    against the first at contact per channel, turned to a second component
    above the first."""
    poles, amps = esprit(z, 2)
    power = np.sum(np.abs(amps) ** 2, axis=1)
    first, second = np.argsort(-power)
    hz = np.angle(poles) * RATE / (2 * np.pi)
    split = float(hz[second] - hz[first])
    ratio = amps[second] / amps[first] * np.exp(-2j * np.pi * split * times[0])
    if split < 0:
        split, ratio = -split, np.conj(ratio)
    return {'split': split, 'db': float(10 * np.log10(power[second] / power[first])),
            'ratio': [[float(r.real), float(r.imag)] for r in ratio]}


def beat_of(rows):
    """A string's beat over its envelopes: the median offset (Hz) and level
    (dB), and the circular mean of the phases at contact (rad)."""
    ratios = np.array([complex(*r) for row in rows for r in row['ratio']])
    mean = np.mean(np.exp(1j * np.angle(ratios)))
    return {'split_hz': float(np.median([row['split'] for row in rows])),
            'second_db': float(np.median([row['db'] for row in rows])),
            'phase': float(np.angle(mean)), 'phase_concentration': float(abs(mean))}


def unexplained(times, z, beat=None):
    """The energy (fraction) an envelope leaves unexplained by one component
    (each channel's amplitude, the rate and the offset fitted), or by two at
    `beat` decaying together with the same freedom."""
    t = times - times[0]
    shape = np.ones_like(t, complex)
    if beat is not None:
        rho = 10 ** (beat['second_db'] / 20) * np.exp(1j * (beat['phase'] + 2 * np.pi * beat['split_hz'] * times[0]))
        shape = 1 + rho * np.exp(2j * np.pi * beat['split_hz'] * t)

    def residual(p):
        b = np.exp((-p[0] + 2j * np.pi * p[1]) * t) * shape
        e = z - np.outer(b, (b.conj() @ z) / (b.conj() @ b))
        return np.concatenate([e.real.ravel(), e.imag.ravel()])

    best = min((optimize.least_squares(residual, [r, d], bounds=([-5, -2], [60, 2]))
                for r in (.5, 2., 6.) for d in (-.3, 0., .3)), key=lambda s: s.cost)
    return float(2 * best.cost / np.sum(np.abs(z) ** 2))


def take_rows(args):
    """One take's envelopes at the strings it sets ringing clear."""
    path, note, f1, B, pitches = args
    sr, x = pa.load(path)
    start = pa.onset(x, sr)
    delay = pa.contact_delay(x, sr, start)
    end = pa.recorded_end(x, sr, start)
    ((f, spectrum),) = fit.halo_spectra({'layers': [{'start': start, 'delay': delay}], 'cases': [path.stem]}, 0,
                                        [(1.0, .5)], path.parent)
    if spectrum is None:
        return []
    ladder = pa.stiff(f1, B, np.arange(1, 400))
    rows = []
    for key, hz in pitches.items():
        if key == note or np.min(np.abs(ladder - hz)) < fit.HALO_APART:
            continue
        if fit.halo_tone(f, spectrum, hz)[1] < ENVELOPE_CLEAR:
            continue
        times, z = envelope(x, sr, start + delay * sr, hz, end)
        if times is not None:
            rows.append({'key': key, 'note': note, 'case': path.stem, 'times': times, 'z': z} | components(times, z))
    return rows


def decide(args):
    """A string's beat, decided by leaving each train pitch out in turn."""
    key, rows = args
    notes = sorted({row['note'] for row in rows})
    held = {}
    for n in notes:
        rest = [row for row in rows if row['note'] != n]
        if not rest:
            continue
        beat = beat_of(rest)
        held[n] = float(np.mean([math.log(unexplained(r['times'], r['z'], beat) / unexplained(r['times'], r['z']))
                                 for r in rows if r['note'] == n]))
    better = sum(v < 0 for v in held.values())
    p = sum(math.comb(len(held), i) for i in range(better, len(held) + 1)) / 2 ** len(held) if held else 1.0
    return key, {'pitches': len(notes), 'envelopes': len(rows), 'beat': beat_of(rows),
                 'held_out_log_ratio': {str(n): v for n, v in held.items()}, 'pitches_better': better,
                 'sign_p': p, 'decided': bool(held) and p <= SIGN_P}


def reading(rate, split, ratios, sr=48000, hz=2000.0):
    """The tone (dB) through each HALO_TIMES window as the halo fit reads a
    string (Hann, 0.5 s, zero-padded 8 times; the largest within 1 Hz of the
    channels' mean power) of a first component from unit amplitude at
    contact and a second `split` Hz above it at `ratios` against it (per
    channel, analytic), both falling at `rate` (1/s). It depends on the
    offsets only, so the string sits at `hz`."""
    t = np.arange(int((fit.HALO_TIMES[-1] + .5) * sr)) / sr
    n = int(.5 * sr)
    w = np.hanning(n)
    near = np.abs(np.fft.rfftfreq(8 * n, 1 / sr) - hz) <= 1
    x = [np.exp(-rate * t) * np.real(np.exp(2j * np.pi * hz * t) * (1 + r * np.exp(2j * np.pi * split * t))) for r in ratios]
    tones = []
    for centre in fit.HALO_TIMES:
        s = int(round(centre * sr)) - n // 2
        power = np.mean([np.abs(np.fft.rfft(c[s:s + n] * w, 8 * n) * 2 / np.sum(w)) ** 2 for c in x], axis=0)
        tones.append(10 * np.log10(np.max(power[near])))
    return np.array(tones)


def fall(tones):
    return float(tones[0] - tones[-1])


def matched(beat, rate):
    """The rate scale and the first's level (dB) at which two components at
    `beat`, read as the halo fit reads a string, read the fall and the level
    one at `rate` (1/s) reads; and how much faster (dB) they read at `rate`."""
    one = reading(rate, 0., [0j])
    ratio = [10 ** (beat['second_db'] / 20) * np.exp(1j * beat['phase'])]
    faster = fall(reading(rate, beat['split_hz'], ratio)) - fall(one)
    shared = rate
    for _ in range(20):
        miss = fall(reading(shared, beat['split_hz'], ratio)) - fall(one)
        if abs(miss) < 1e-4:
            break
        shared -= miss * math.log(10) / 20 / (fit.HALO_TIMES[-1] - fit.HALO_TIMES[0])
    return shared / rate, float(np.mean(one) - np.mean(reading(shared, beat['split_hz'], ratio))), faster


def measure_piano(name, pool):
    model = fit.MODELS[name]
    inputs = dict(header=rel(model['header']), header_sha256=fit.sha256(model['header']),
                  split=rel(model['split']), split_sha256=fit.sha256(model['split']),
                  corpus=rel(model['corpus']), corpus_sha256=fit.sha256(model['corpus']))
    table = imm.load(model['header'])
    pitches = halo_pitches(table)
    rates = dict(zip(table['halo']['keys'], table['halo']['rates']))
    anchors = {a['note']: a for a in table['anchors']}
    roles = json.loads(model['split'].read_text())['cases']
    corpus = {f['id']: f for f in json.loads(model['corpus'].read_text())['files']}
    jobs = []
    for note, layers in fit.train_anchors(model).items():
        if note >= fit.HALO_LOWEST:
            jobs += [(model['wav'] / f'{case}.wav', note, anchors[note]['f1'], anchors[note]['B'], pitches)
                     for case, _, _ in layers]
    train = [row for rows in pool.map(take_rows, jobs) for row in rows]
    by = defaultdict(list)
    for row in train:
        by[row['key']].append(row)
    strings = dict(pool.map(decide, sorted(by.items())))
    # The dev takes, at pitches the fit may not hold: their series as the
    # engine interpolates its anchors' (cents and log B linear in the key).
    notes = sorted(anchors)

    def series(note):
        if note in anchors:
            return anchors[note]['f1'], anchors[note]['B']
        below, above = [n for n in notes if n < note], [n for n in notes if n > note]
        lo, hi = (below[-1], above[0]) if below and above else (notes[0], notes[1]) if above else (notes[-2], notes[-1])
        t = (note - lo) / (hi - lo)
        cents = [1200 * math.log2(anchors[n]['f1'] / pa.midi_hz(n)) for n in (lo, hi)]
        logs = [math.log(anchors[n]['B']) for n in (lo, hi)]
        return (pa.midi_hz(note) * 2 ** ((cents[0] + t * (cents[1] - cents[0])) / 1200),
                math.exp(logs[0] + t * (logs[1] - logs[0])))

    dev_jobs = [(model['wav'] / f'{case}.wav', corpus[case]['midi'], *series(corpus[case]['midi']), pitches)
                for case, role in sorted(roles.items())
                if role == 'dev' and corpus[case]['kind'] == 'note' and corpus[case]['midi'] >= fit.HALO_LOWEST]
    dev = [row for rows in pool.map(take_rows, dev_jobs) for row in rows]
    for key, s in strings.items():
        if s['decided']:
            s['rate_scale'], s['first_db'], s['fall_db'] = matched(s['beat'], rates[key])
            one = fall(reading(rates[key], 0., [0j]))
            faster = [fall(reading(rates[key], r['split'], [complex(*c) for c in r['ratio']])) - one for r in by[key]]
            s['fall_bias_db'] = [float(np.percentile(faster, q)) for q in (25, 50, 75)]
            scored = [math.log(unexplained(r['times'], r['z'], s['beat']) / unexplained(r['times'], r['z']))
                      for r in dev if r['key'] == key]
            s['dev'] = {'envelopes': len(scored), 'mean_log_ratio': float(np.mean(scored)) if scored else None,
                        'better': float(np.mean(np.array(scored) < 0)) if scored else None}
    decided = [k for k, s in strings.items() if s['decided']]
    print(f'{name}: {len(train)} train envelopes at {len(by)} strings, {len(dev)} dev; beats at {decided or "none"}',
          flush=True)
    for key, s in sorted(strings.items()):
        b = s['beat']
        line = (f'  {key}: {s["pitches"]} pitches, {s["envelopes"]} envelopes; {b["split_hz"]:.3f} Hz, '
                f'{b["second_db"]:+.1f} dB, phase {b["phase"]:+.2f} ({b["phase_concentration"]:.2f}); '
                f'{s["pitches_better"]} of {len(s["held_out_log_ratio"])} pitches better, p {s["sign_p"]:.3f}')
        if s['decided']:
            d = s['dev']
            q = s['fall_bias_db']
            line += (f'; the takes read it falling {q[1]:+.2f} dB faster ({q[0]:+.2f} to {q[2]:+.2f}), the beat '
                     f'{s["fall_db"]:+.2f}: rate x{s["rate_scale"]:.3f}, first {s["first_db"]:+.2f} dB; dev {d["envelopes"]} envelopes'
                     + (f', ratio {math.exp(d["mean_log_ratio"]):.2f}, {d["better"]:.0%} better' if d['envelopes'] else ''))
        print(line, flush=True)
    return inputs | dict(train_envelopes=len(train), dev_envelopes=len(dev),
                         strings={str(k): v for k, v in sorted(strings.items())})


def row(s):
    if not (s and s['decided']):
        return '{1.f,0.f,0.f,-200.f,0.f}'
    b = s['beat']
    return '{' + ','.join(fit.number(v) for v in (s['rate_scale'], s['first_db'], b['split_hz'], b['second_db'], b['phase'])) + '}'


def header_text(receipt):
    lines = [
        '// Generated by Tools/fit_halo_beats.py from the train takes of each piano\'s',
        f'// split ({rel(RECEIPT)}); regenerate, never edit.',
        '// Fitted numbers only: no recorded waveform.',
        '#pragma once',
        '',
        '#include <array>',
        '',
        'namespace keyra { namespace measured {',
        '// An undamped string\'s aftersound (HaloString) as two components a strike',
        '// sets ringing together, both falling at the string\'s rate times',
        '// rateScale: the first at the string\'s pitch, firstDb (dB) from the level',
        '// its fit gives one, the second splitHz above it, secondDb (dB) against',
        '// the first and phase (rad) against it at contact, in the analytic',
        '// signal\'s sense. Read as the halo fit reads a string, the two read the',
        '// fall and the level it fitted to one. secondDb is -200, and rateScale 1,',
        '// where the takes do not decide a beat. One per key from F6 up.',
        'struct HaloBeat { float rateScale, firstDb, splitHz, secondDb, phase; };',
    ]
    for name in PIANOS:
        strings = receipt['pianos'][name]['strings']
        lines.append(f'namespace {name} {{')
        lines.append(f'constexpr std::array<HaloBeat,{len(fit.UNDAMPED)}> haloBeats{{{{'
                     + ','.join(row(strings.get(str(key))) for key in fit.UNDAMPED) + '}};')
        lines.append('}')
    lines += ['}}', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='check the receipt against the tool, its inputs and the header, and exit')
    parser.add_argument('--jobs', type=int, default=2, help='takes measured at once')
    args = parser.parse_args()
    if args.check:
        receipt = json.loads(RECEIPT.read_text())
        stale = {rel(Path(__file__))} if receipt['tool_sha256'] != fit.sha256(Path(__file__)) else set()
        for measured in receipt['pianos'].values():
            stale |= {measured[k] for k in ('header', 'split', 'corpus') if measured[f'{k}_sha256'] != fit.sha256(ROOT / measured[k])}
        if stale:
            raise SystemExit(f'{rel(RECEIPT)} predates the current {", ".join(sorted(stale))}: run Tools/fit_halo_beats.py')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from {rel(RECEIPT)}: run Tools/fit_halo_beats.py')
        print(f'{rel(HEADER)} matches {rel(RECEIPT)}')
        return
    with ProcessPoolExecutor(args.jobs) as pool:
        pianos = {name: measure_piano(name, pool) for name in PIANOS}
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   protocol=dict(start_seconds=START, end_seconds=END, rate_hz=RATE, lowpass_hz=LOWPASS,
                                 envelope_clear_db=ENVELOPE_CLEAR, sign_p=SIGN_P, halo_lowest=fit.HALO_LOWEST,
                                 halo_apart_hz=fit.HALO_APART, halo_times=list(fit.HALO_TIMES)),
                   pianos=pianos)
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
