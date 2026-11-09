#!/usr/bin/env python3
"""Measure the room each piano was recorded in on the train takes of its
locked split (fit_realtime_modal.MODELS) and write Source/DSP/MeasuredRoom.h.

Between a strike's partials every recording holds a floor that, from 0.1 s
after the strike, decays at one rate per band whatever the note, and above
250 Hz its two microphones hear it uncorrelated: the room's reverberation
(Docs/research/room-2026-11-09.md). The fitted partials hold the room at
their own frequencies already, so the engine's room hears only what they
leave out, the strike's noise and the board's ring, and its level is set
against the engine's own render: the room is what that render lacks under
the recordings' floor.

Each take is measured from its onset (piano_analysis.onset) in 100 ms Hann
windows starting 0.10 to 0.60 s after it every 50 ms: per third-octave band
the floor between the partials, the median power over ln 2 of the bins
75 Hz clear of every partial piano_analysis.partials finds in the recording,
where a band keeps four bins and a quarter of its own. The take's own floor
(its microphones and preamps, the tape) is the same measure's least over
0.1 s steps across the last 1.5 s before the library's fade-out.

- The rate per band: a line through the frames 15 dB over the take's own
  floor (five at least), in the bands from 1.5 times the note's fundamental
  up, where only the floor sounds between the partials; the median over five
  takes at least, a band that falls slower than 10 dB/s being the
  recording's own noise. Between the measured bands a band takes its
  neighbours' rates. From 1 kHz up a band decays at least as fast as the one
  under it: a room loses more toward the top (the air's absorption and its
  surfaces'), and where a recording's own noise holds a top band up (the
  Hamamatsu's from 4 kHz) it reads slower.
- The shelf: the engine's network loses the rates through a first-order
  shelf in each line (KeyraEngine.cpp), whose rate is its low one at DC and
  its high one at Nyquist. Per crossover in CROSSOVERS, the two rates within
  the measured ones by least squares over the measured bands; the crossover
  with the least error.
- The gain: each take is rendered at its layer's velocity through the engine
  without its room (--room 0) and with the room alone at unit gain on that
  shelf (--room-shelf), the room being the two renders' difference, both
  scaled to the recording as benchmark_recordings scores them (its early
  RMS). In every frame starting 0.10 to 0.50 s whose recording floor stands
  10 dB over the take's own, the room's gain squared that brings the
  render's floor to the recording's; per band the median over its frames
  (twenty at least), and the gain the square root of the median over the
  bands whose rates were measured, where the floor decays as the room does.

  python3 Tools/fit_room.py --renderer build/keyra_render   # measure, write the header and the receipt
  python3 Tools/fit_room.py --check                         # the receipt is current and the header the one it gives
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
from scipy import signal
from scipy.optimize import lsq_linear

import benchmark_recordings as br
import fit_realtime_modal as fit
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredRoom.h'
RECEIPT = ROOT / 'Docs/research/room-2026-11-09.json'
ENGINE = ROOT / 'Source/DSP/KeyraEngine.cpp'
PIANOS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork')
BANDS = np.asarray(pa.THIRD_OCTAVE)
STARTS = np.round(np.arange(.10, .601, .05), 2)  # each window's start after the onset (s)
WINDOW, CLEAR = .1, 75.  # window length (s); how far a kept bin sits from every partial (Hz)
LEVEL_STARTS = STARTS[STARTS <= .5]
RATE_OVER_FLOOR, LEVEL_OVER_FLOOR = 15., 10.  # dB over the take's own floor
RATE_FRAMES, RATE_TAKES, LEVEL_FRAMES = 5, 5, 20
SLOWEST = 10.  # dB/s: a band falling slower is the recording's own noise
CROSSOVERS = (250, 400, 630, 1000, 1600, 2500, 4000, 6300)
RENDER_SECONDS = 1.6
# The engine's network (KeyraEngine.cpp, roomDelaySeconds): its lines'
# lengths, each the first prime at or above the length in samples.
DELAY_SECONDS = (.0113, .0137, .0161, .0187, .0214, .0244, .0276, .0310,
                 .0346, .0385, .0426, .0470, .0517, .0566, .0619, .0675)
FIT_RATE = 48000


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def line_lengths(sr):
    prime = lambda n: n > 1 and all(n % k for k in range(2, int(n ** .5) + 1))
    out = []
    for seconds in DELAY_SECONDS:
        n = int(math.floor(seconds * sr + .5))  # std::lround
        while not prime(n) or n in out:
            n += 1
        out.append(n)
    return out


def shelf_rate(f, low, high, crossover, sr=FIT_RATE):
    """The decay (dB/s) at f of a line of the network's median length whose
    loss is the engine's shelf for these rates (prepareRoom())."""
    d = float(np.median(line_lengths(sr)))
    g0, gp = 10 ** (-low * d / (20 * sr)), 10 ** (-high * d / (20 * sr))
    w = math.tan(math.pi * min(crossover, .45 * sr) / sr)
    a1 = (w - 1) / (w + 1)
    b0, b1 = .5 * (g0 * (1 + a1) + gp * (1 - a1)), .5 * (g0 * (1 + a1) - gp * (1 - a1))
    z = np.exp(-2j * math.pi * np.asarray(f) / sr)
    return -20 * np.log10(np.abs((b0 + b1 * z) / (1 + a1 * z))) * sr / d


def floors(x, sr, at, freqs, starts):
    """Per window and band, the floor between the partials (power), or NaN."""
    n = int(WINDOW * sr)
    w = signal.windows.hann(n, sym=False)
    nfft = 1 << int(math.ceil(math.log2(2 * n)))
    hz = np.fft.rfftfreq(nfft, 1 / sr)
    keep = np.ones(len(hz), bool)
    for f in freqs:
        keep &= np.abs(hz - f) > CLEAR
    norm = 2 / (nfft * np.sum(w * w))
    masks = []
    for f in BANDS:
        band = (hz >= f * 2 ** (-1 / 6)) & (hz < f * 2 ** (1 / 6))
        kept = band & keep
        masks.append(kept if band.sum() and kept.sum() >= max(4, .25 * band.sum()) else None)
    out = np.full((len(starts), len(BANDS)), np.nan)
    for i, t in enumerate(starts):
        a = at + int(round(t * sr))
        if a < 0 or a + n > len(x):
            continue
        p = np.mean(np.abs(np.fft.rfft(x[a:a + n] * w[:, None], nfft, axis=0)) ** 2, axis=1) * norm
        for j, k in enumerate(masks):
            if k is not None:
                out[i, j] = np.median(p[k]) / math.log(2)
    return out


def early_rms(x, sr, start):
    """The level benchmark_recordings.features matches a render to its recording by."""
    xh = signal.sosfiltfilt(signal.butter(2, 20, 'highpass', fs=sr, output='sos'), x, axis=0)
    early = xh[start + int(.05 * sr):start + int(.75 * sr)]
    return float(np.sqrt(np.mean(early * early)))


def render(renderer, model, note, velocity, extra, tmp):
    events = Path(tmp) / 'note.events'
    events.write_text(f'{br.LEAD} on {note} {velocity}\n')
    out = Path(tmp) / f'render{len(list(Path(tmp).glob("render*.wav")))}.wav'
    subprocess.run([renderer, '--events', str(events), '--output', str(out), '--duration', str(RENDER_SECONDS)]
                   + br.MEASURE + (['--model', model] if model != 'grand' else []) + extra,
                   check=True, stdout=subprocess.DEVNULL)
    return pa.load(out)


def measure_recording(job):
    """A take's floor frames, own floor and fundamental, from the recording alone."""
    model, case, note = job
    sr, x = pa.load(fit.MODELS[model]['wav'] / f'{case}.wav')
    start = pa.onset(x, sr)
    _, _, found = pa.partials(x, sr, note, start)
    freqs = [q['hz'] for q in found] or [pa.midi_hz(note)]
    duration = len(x) / sr
    end = duration - max(1.0, .25 * duration) if duration > 8 else duration - 1.0
    ts = np.arange(max(start / sr + .8, end - 1.5), end - .1, .1)
    # fmin.reduce leaves a band no frame reaches NaN, as nanmin does, without its warning.
    own = np.fmin.reduce(floors(x, sr, 0, freqs, ts), axis=0) if len(ts) else np.full(len(BANDS), np.nan)
    return dict(case=case, note=note, sr=sr, start=start, freqs=freqs, floor=floors(x, sr, start, freqs, STARTS), own=own,
                early=early_rms(x, sr, start))


def measure_render(job):
    """A take's render without the room and the room alone at unit gain, at the recording's level."""
    model, take, velocity, renderer, shelf = job
    with tempfile.TemporaryDirectory(prefix='fit-room-') as tmp:
        sr, dry = render(renderer, model, take['note'], velocity, ['--room', '0'], tmp)
        _, both = render(renderer, model, take['note'], velocity, ['--room-shelf', ','.join(f'{v:.9g}' for v in shelf + [1.])], tmp)
    start = pa.onset(dry, sr)
    g = (take['early'] / max(early_rms(dry, sr, start), 1e-20)) ** 2
    starts = LEVEL_STARTS
    return dict(dry=floors(dry, sr, start, take['freqs'], starts) * g, room=floors(both - dry, sr, start, take['freqs'], starts) * g)


def takes_of(model):
    m = fit.MODELS[model]
    split = json.loads(m['split'].read_text())['cases']
    items = {i['id']: i for i in json.loads(m['corpus'].read_text())['files']}
    return [(c, items[c]) for c, role in sorted(split.items()) if role == 'train' and items[c]['kind'] == 'note']


def rates_of(takes):
    """Per band the floor's decay rate (dB/s, NaN unmeasured) and the takes it rests on."""
    t = STARTS + WINDOW / 2
    rates, count = np.full(len(BANDS), np.nan), np.zeros(len(BANDS), int)
    for j, f in enumerate(BANDS):
        slopes = []
        for take in takes:
            if f <= 1.5 * pa.midi_hz(take['note']) or not np.isfinite(take['own'][j]):
                continue
            db = 10 * np.log10(np.maximum(take['floor'][:, j], 1e-30))
            ok = np.isfinite(take['floor'][:, j]) & (db > 10 * math.log10(max(take['own'][j], 1e-30)) + RATE_OVER_FLOOR)
            if ok.sum() >= RATE_FRAMES:
                slopes.append(np.polyfit(t[ok], db[ok], 1)[0])
        count[j] = len(slopes)
        if len(slopes) >= RATE_TAKES and np.median(slopes) < -SLOWEST:
            rates[j] = -float(np.median(slopes))
    return rates, count


def shelf_of(rates):
    """The shelf nearest the measured rates, made monotone from 1 kHz up."""
    measured = np.flatnonzero(np.isfinite(rates))
    lo, hi = measured.min(), measured.max()
    r = np.interp(np.arange(len(BANDS)), measured, rates[measured])
    top = np.flatnonzero(BANDS >= 1000)
    r[top] = np.maximum.accumulate(r[top])
    span = slice(lo, hi + 1)
    best = None
    for crossover in CROSSOVERS:
        X = np.c_[shelf_rate(BANDS[span], 1., 0., crossover), shelf_rate(BANDS[span], 0., 1., crossover)]
        low, high = lsq_linear(X, r[span], bounds=(r[span].min(), r[span].max())).x
        error = float(np.sqrt(np.mean((shelf_rate(BANDS[span], low, high, crossover) - r[span]) ** 2)))
        if best is None or error < best[0]:
            best = (error, float(low), float(high), crossover)
    error, low, high, crossover = best
    return dict(low_rate=low, high_rate=high, crossover=crossover, rate_rms_error=error, fitted_rates=r[span].tolist(),
                measured_bands=[float(BANDS[lo]), float(BANDS[hi])])


def gain_of(takes, renders, lo, hi):
    """Per band the gain squared the room needs (median over frames), and the gain."""
    need, count = np.full(len(BANDS), np.nan), np.zeros(len(BANDS), int)
    for j in range(len(BANDS)):
        values = []
        for take, r in zip(takes, renders):
            own = take['own'][j]
            if not np.isfinite(own):
                continue
            rec = take['floor'][:len(LEVEL_STARTS), j]
            ok = np.isfinite(rec) & np.isfinite(r['dry'][:, j]) & np.isfinite(r['room'][:, j]) & (r['room'][:, j] > 0)
            ok &= rec > own * 10 ** (LEVEL_OVER_FLOOR / 10)
            values += list((rec[ok] - r['dry'][ok, j]) / r['room'][ok, j])
        count[j] = len(values)
        if len(values) >= LEVEL_FRAMES:
            need[j] = float(np.median(values))
    span = np.isfinite(need) & (BANDS >= lo) & (BANDS <= hi)
    return need, count, math.sqrt(max(0., float(np.median(need[span])))), int(span.sum())


def measure_piano(model, renderer, pool):
    cases = takes_of(model)
    takes = list(pool.map(measure_recording, [(model, c, item['midi']) for c, item in cases], chunksize=4))
    rates, rate_takes = rates_of(takes)
    shelf = shelf_of(rates)
    jobs = [(model, take, fit.layer_velocity(item), renderer, [shelf['low_rate'], shelf['high_rate'], shelf['crossover']])
            for take, (_, item) in zip(takes, cases)]
    renders = list(pool.map(measure_render, jobs, chunksize=4))
    need, frames, gain, bands = gain_of(takes, renders, *shelf['measured_bands'])
    m = fit.MODELS[model]
    finite = lambda v: [None if not np.isfinite(x) else float(x) for x in v]
    print(f'{model}: {len(takes)} takes; rates measured {shelf["measured_bands"][0]:.0f} to {shelf["measured_bands"][1]:.0f} Hz, '
          f'shelf {shelf["low_rate"]:.1f} to {shelf["high_rate"]:.1f} dB/s at {shelf["crossover"]} Hz (rms {shelf["rate_rms_error"]:.1f} dB/s); '
          f'gain {20 * math.log10(max(gain, 1e-12)):+.1f} dB from {bands} bands', flush=True)
    return dict(header=rel(m['header']), header_sha256=fit.sha256(m['header']),
                split=rel(m['split']), split_sha256=fit.sha256(m['split']),
                corpus=rel(m['corpus']), corpus_sha256=fit.sha256(m['corpus']),
                takes=len(takes), rates=finite(rates), rate_takes=rate_takes.tolist(), **shelf,
                need=finite(need), need_frames=frames.tolist(), gain=gain, gain_bands=bands)


def header_text(receipt):
    lines = [
        '// Generated by Tools/fit_room.py from the train takes of each piano\'s',
        f'// split ({rel(RECEIPT)}); regenerate, never edit.',
        '// Fitted numbers only: no recorded waveform or impulse response.',
        '#pragma once',
        '',
        'namespace keyra { namespace measured {',
        '// The room a piano was recorded in, as the engine\'s delay network plays it',
        '// (KeyraEngine.cpp): its decay rate in dB/s at low frequencies and at the',
        '// top, a first-order shelf between them at the crossover (Hz), and the',
        '// gain the strike\'s noise and the board\'s ring enter it with.',
        'struct Room { float lowRate; float highRate; float crossover; float gain; };',
    ]
    for name in PIANOS:
        m = receipt['pianos'][name]
        lines.append(f'namespace {name} {{ constexpr Room room{{{fit.number(m["low_rate"])},{fit.number(m["high_rate"])},'
                     f'{fit.number(m["crossover"])},{fit.number(m["gain"])}}}; }}')
    lines += ['}}', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='check the receipt against the tool, its inputs and the header, and exit')
    parser.add_argument('--renderer', type=Path, help='the keyra_render the gains are measured through')
    parser.add_argument('--jobs', type=int, default=3, help='takes measured at once')
    args = parser.parse_args()
    if args.check:
        receipt = json.loads(RECEIPT.read_text())
        stale = {rel(Path(__file__))} if receipt['tool_sha256'] != fit.sha256(Path(__file__)) else set()
        for measured in receipt['pianos'].values():
            stale |= {measured[k] for k in ('header', 'split', 'corpus') if measured[f'{k}_sha256'] != fit.sha256(ROOT / measured[k])}
        if stale:
            raise SystemExit(f'{rel(RECEIPT)} predates the current {", ".join(sorted(stale))}: run Tools/fit_room.py')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from {rel(RECEIPT)}: run Tools/fit_room.py')
        print(f'{rel(HEADER)} matches {rel(RECEIPT)}')
        return
    if args.renderer is None:
        parser.error('--renderer is required to measure')
    renderer = str(args.renderer.resolve())
    with ProcessPoolExecutor(args.jobs) as pool:
        pianos = {name: measure_piano(name, renderer, pool) for name in PIANOS}
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   engine=rel(ENGINE), engine_sha256=fit.sha256(ENGINE),
                   protocol=dict(bands=BANDS.tolist(), starts=STARTS.tolist(), level_starts=LEVEL_STARTS.tolist(),
                                 window_seconds=WINDOW, clear_hz=CLEAR, rate_over_floor_db=RATE_OVER_FLOOR,
                                 level_over_floor_db=LEVEL_OVER_FLOOR, rate_frames=RATE_FRAMES, rate_takes=RATE_TAKES,
                                 level_frames=LEVEL_FRAMES, slowest_db_s=SLOWEST, crossovers=list(CROSSOVERS),
                                 delay_seconds=list(DELAY_SECONDS), render_seconds=RENDER_SECONDS, measure=br.MEASURE),
                   pianos=pianos)
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
