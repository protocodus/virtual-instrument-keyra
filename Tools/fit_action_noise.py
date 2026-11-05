#!/usr/bin/env python3
"""Measure the click of each piano's action knocks above its body modes on
the train takes of its locked split (fit_realtime_modal.MODELS) and write it
into Source/DSP/MeasuredActionNoise.h.

The engine plays the action's knocks (fit_realtime_modal.action_data: each
anchor's key let go and the grand's pedal going down and up) on the body
modes, 25 Hz to 1 kHz. The takes also hold a click above them: the felt and
the wood meet their stops in a few milliseconds and set ringing the board's
dense upper modes, which no mode the engine fits resolves. It is played as
band noise in the engine's noise bands (MeasuredModalData.h noiseBands) from
the first whose lower edge lies at BODY_TOP or over it, 1.26 to 16 kHz; under
it the modes play the knock. The pedal going down has no click of its own to
measure: from 1.26 to 12.7 kHz the grand's pedalD1 climbs 20 to 30 dB over
its first 100 ms and then falls only 3 to 21 dB/s over the next 0.9 s, the
strings its dampers free ringing on, which the engine plays as its open
strings.

Each take, from the knock's onset (where its BODY_LOW to BODY_TOP power over
5 ms first comes within 30 dB of its peak, as action_signal finds it) to
ACTION_SECONDS after it or FADE before the take's end, whichever comes first
(the libraries fade their takes out):
- per band and channel, the density (1/Hz, one-sided) through WINDOW Hann
  frames every HOP, each wholly inside that span: the median of the band's
  bin powers over ln 2, as noise_bands measures the ring's noise, so that
  the tones of strings a take holds (the Kawai's keys are let go from a
  sounding note, the string still ringing under its damper) are not taken
  for the click;
- its floor, the frames' mean over the QUIET seconds where both channels'
  mean is lowest. A band sounds where that mean, smoothed over SMOOTH,
  stands CLEAR dB over its floor somewhere; elsewhere it is silent
  (fit_realtime_modal.NOISE_SILENT);
- what stands over the floor, the density less it, is played as the burst
  a (e^(-r t) - e^(-(r + 1/rise) t)) under the action's rise (actionRise,
  the modes' own: one stroke of the action drives both) at a decay r of
  its own, its square averaged over each frame's window as the frame
  measures it: r gives the burst the take's centroid in time over the span,
  both channels together, and a^2 each channel's energy over it. The table
  holds the density sqrt(aL^2 aR^2) and the balance 10 log10(aR^2 / aL^2),
  right over left, which the engine plays exactly.
The densities are in each take's own scale, as the knocks' levels are, so
the engine sets them against the notes with the knocks. Each take's modes
refitted on the header's (action_fit) must give the header's levels, which
checks that the click is measured from its knock's own onset on its own take.

The Kawai's release takes are let go from sounding notes (SOUNDING): over
their first 0.3 s the key's partials stand 32 to 62 dB over the median of
their 0.9 to 6 kHz spectrum (D#6's fundamental 62 dB, C4's 4th to 9th 38 to
47, C5's 2nd to 5th 32 to 55), and above the modes those partials' sidelobes
and their fall under the damper, not the action, fill the bands: measured
so, D#6's take, which the keys from F6 up share, would click 24 dB over its
knock, A-weighted, where the grand's release clicks stand 4 to 19 dB under
theirs. The engine plays that string through its dampers, so the Kawai
plays no click.

The receipt also gives each take's click against its knock as the engine
plays both, A-weighted (IEC 61672) over the span: the modes at the header's
levels under the action's rise and decay, each at half its level's power
per channel, the bands at their densities over their widths.

  python3 Tools/fit_action_noise.py           # measure every piano, write the header and the receipt
  python3 Tools/fit_action_noise.py --check   # the receipt is current and the header is the one it gives
"""
from __future__ import annotations

import argparse
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
from scipy import ndimage, signal

import fit_realtime_modal as fit
import import_modal_measurements as imm
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredActionNoise.h'
RECEIPT = ROOT / 'Docs/research/action-noise-2026-11-05.json'
PIANOS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork')
WINDOW, HOP = .02, .0025      # s: the frames, as the strike's knock is measured (KNOCK_WINDOW, KNOCK_HOP)
FADE = .03                    # s before a take's end that the span stops
QUIET = .1                    # s: the floor's frames
SMOOTH = .025                 # s: the frames a band must stand clear over
CLEAR = 10.0                  # dB over the floor
RATES = (.3, 3000.0)          # 1/s: the decays the burst may take
REFIT_CHECK = .05             # dB: the refit's largest departure from the header's knock
SOUNDING = ('kawai',)         # pianos whose release takes are let go from sounding notes


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def a_weight(hz):
    """IEC 61672 A-weighting (dB)."""
    f2 = np.asarray(hz, float) ** 2
    ra = 12194 ** 2 * f2 * f2 / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    return 20 * np.log10(ra) + 2.0


def onset(x, sr):
    """The knock's onset (samples): action_signal's."""
    sos = signal.butter(6, [fit.BODY_LOW, fit.BODY_TOP], 'bandpass', fs=sr, output='sos')
    y = signal.sosfiltfilt(sos, x, axis=0)
    p = ndimage.uniform_filter1d(np.mean(y * y, axis=1), int(.005 * sr))
    peak = int(np.argmax(p[:int(1.0 * sr)]))
    return int(np.flatnonzero(p >= p[peak] * 1e-3)[0])


def envelope(times, offsets, weights, rate, rise):
    """The burst's square, (e^(-r t) - e^(-(r + 1/rise) t))^2, averaged over
    each frame's window: three exponentials, each frame's average of one its
    value at the frame's centre times the window's mean of it over the
    offsets, as every frame lies wholly after the onset."""
    out = np.zeros(len(times))
    for gain, beta in ((1, 2 * rate), (-2, 2 * rate + 1 / rise), (1, 2 * rate + 2 / rise)):
        out += gain * float(weights @ np.exp(-beta * offsets)) * np.exp(-beta * times)
    return out


def burst(times, rest, offsets, weights, rise):
    """The decay (1/s) whose burst has the centroid in time of `rest`
    (frames x channels, the density over the floor) and each channel's a^2."""
    total = rest.sum(axis=1)
    centre = float(times @ total / total.sum())

    def centroid(rate):
        e = envelope(times, offsets, weights, rate, rise)
        return float(times @ e / e.sum())
    lo, hi = math.log(RATES[0]), math.log(RATES[1])
    if centroid(math.exp(lo)) <= centre:
        rate = math.exp(lo)
    elif centroid(math.exp(hi)) >= centre:
        rate = math.exp(hi)
    else:
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if centroid(math.exp(mid)) > centre else (lo, mid)
        rate = math.exp((lo + hi) / 2)
    e = envelope(times, offsets, weights, rate, rise)
    return rate, rest.sum(axis=0) / e.sum(), centre


def span(x, sr):
    """The knock's onset and where its span ends (samples)."""
    start = onset(x, sr)
    return start, min(len(x), start + int(fit.ACTION_SECONDS * sr)) - int(FADE * sr)


def band_densities(x, sr, start, stop, centres):
    """The frames' centres (s after `start`) and per band of `centres` from
    BODY_TOP up that the rate holds its density (frames x channels): WINDOW
    Hann frames every HOP wholly between start and stop, the median of the
    band's bin powers over ln 2; None for the other bands."""
    length = int(WINDOW * sr)
    nfft = 1 << int(math.ceil(math.log2(2 * length)))
    w = signal.windows.hann(length, sym=False)
    scale = 2 / (sr * np.sum(w * w))
    firsts = np.arange(start, stop - length + 1, int(round(HOP * sr)))
    times = (firsts + length // 2 - start) / sr
    spectra = np.abs(np.array([np.fft.rfft(x[a:a + length] * w[:, None], nfft, axis=0) for a in firsts])) ** 2 * scale
    hz = np.fft.rfftfreq(nfft, 1 / sr)
    densities = []
    for c in centres:
        lo, hi = c * 2 ** (-1 / 6), c * 2 ** (1 / 6)
        inside = (hz >= lo) & (hz < hi)
        densities.append(np.median(spectra[:, inside, :], axis=1) / math.log(2)
                         if lo >= fit.BODY_TOP and hi <= .45 * sr and len(times) else None)
    return times, densities


def floor_of(density):
    """Each channel's mean over the QUIET seconds of frames where both
    channels' mean is lowest; None where the span is shorter."""
    quiet = max(1, int(round(QUIET / HOP)))
    if len(density) < quiet:
        return None
    q = int(np.argmin(np.convolve(density.mean(axis=1), np.ones(quiet) / quiet, 'valid')))
    # A take's digital silence (a fade, a gate) is no floor to stand over.
    return np.maximum(density[q:q + quiet].mean(axis=0), 1e-30)


def measure_take(args):
    """One take's click per noise band: (density dB, rate 1/s, balance dB)
    and what the receipt keeps of it."""
    path, centres, rise = args
    sr, x = pa.load(path)
    start, stop = span(x, sr)
    times, densities = band_densities(x, sr, start, stop, centres)
    length = int(WINDOW * sr)
    w = signal.windows.hann(length, sym=False)
    weights = w * w / np.sum(w * w)
    offsets = (np.arange(length) - length // 2) / sr
    smooth = max(1, int(round(SMOOTH / HOP)))
    bands, kept = [], []
    for c, density in zip(centres, densities):
        floor = None if density is None else floor_of(density)
        if floor is None:
            bands.append((fit.NOISE_SILENT, 1.0, 0.0))
            kept.append(None)
            continue
        mean = density.mean(axis=1)
        clear = 10 * math.log10(np.convolve(mean, np.ones(smooth) / smooth, 'valid').max() / floor.mean())
        row = {'hz': c, 'floor_db': [float(10 * np.log10(v)) for v in floor], 'clear_db': float(clear)}
        if clear < CLEAR:
            bands.append((fit.NOISE_SILENT, 1.0, 0.0))
            kept.append(row)
            continue
        rest = density - floor
        if not rest.sum() > 0:
            bands.append((fit.NOISE_SILENT, 1.0, 0.0))
            kept.append(row | {'negative': True})
            continue
        rate, a2, centre = burst(times, rest, offsets, weights, rise)
        if not (a2 > 0).all():
            bands.append((fit.NOISE_SILENT, 1.0, 0.0))
            kept.append(row | {'negative': True})
            continue
        level = 5 * math.log10(a2[0] * a2[1])
        balance = 10 * math.log10(a2[1] / a2[0])
        bands.append((level, rate, balance))
        kept.append(row | {'density_db': level, 'rate': rate, 'balance_db': balance, 'centroid_s': centre})
    return {'onset_s': start / sr, 'span_s': (stop - start) / sr, 'bands': bands, 'kept': kept}


def modal_energy(body, levels, decay, rise, span):
    """The knock's modes as the engine plays them over the span, A-weighted:
    per channel half each level's power under the rise and the decay."""
    t = np.arange(0, span, 1 / 4000)
    total = 0.0
    for hz, rate, k in zip(body['hz'], body['rates'], levels):
        e = (1 - np.exp(-t / rise)) * np.exp(-decay * rate * t)
        total += 10 ** ((k['level_db'] + a_weight(hz)) / 10) / 2 * float(np.sum(e * e)) / 4000
    return total


def click_energy(centres, bands, rise, span):
    """The click as the engine plays it over the span, A-weighted: per
    channel each band's density over its width."""
    t = np.arange(0, span, 1 / 4000)
    total = 0.0
    for c, (level, rate, balance) in zip(centres, bands):
        if level <= fit.NOISE_SILENT:
            continue
        g = np.exp(-rate * t) * (1 - np.exp(-t / rise))
        mean = 10 ** (level / 10) * math.cosh(balance * math.log(10) / 20)
        total += mean * c * (2 ** (1 / 6) - 2 ** (-1 / 6)) * 10 ** (a_weight(c) / 10) * float(np.sum(g * g)) / 4000
    return total


def own_levels(path, body, decay, rise):
    """The take's modal knock refitted on the header's modes (action_fit)."""
    y = fit.action_signal(path)
    design = fit.action_design(fit.action_waves(len(y), body['hz']), decay * np.asarray(body['rates']), rise)
    shapes = [np.array(s) for s in body['shapes']]
    levels, _ = fit.action_fit(y, design, shapes)
    return 20 * np.log10(np.abs(levels) + 1e-12)


def measure_piano(name, pool):
    model = fit.MODELS[name]
    inputs = dict(header=rel(model['header']), header_sha256=fit.sha256(model['header']),
                  split=rel(model['split']), split_sha256=fit.sha256(model['split']),
                  corpus=rel(model['corpus']), corpus_sha256=fit.sha256(model['corpus']))
    if name in SOUNDING:
        print(f'{name}: its release takes are let go from sounding notes; no click', flush=True)
        return inputs | dict(sounding=True)
    table = imm.load(model['header'])
    centres = table['noise']['hz']
    action, body = table['action'], table['body']
    notes = [a['note'] for a in table['anchors']]
    roles = json.loads(model['split'].read_text())['cases']
    names = [model['release'].format(key=note - 20, note=note) for note in notes] + list(model['pedal'][1:])
    if any(roles.get(n) != 'train' for n in names):
        raise SystemExit('the action noise is fitted on train recordings only')
    knocks = action['releases'] + ([action['pedal_up']] if model['pedal'] else [])
    paths = [model['wav'] / f'{n}.wav' for n in names]
    measured = list(pool.map(measure_take, [(p, centres, action['rise']) for p in paths]))
    owns = list(pool.map(own_levels, paths, [body] * len(paths), [action['decay']] * len(paths),
                         [action['rise']] * len(paths)))
    takes = []
    worst = max(float(np.max(np.abs(np.array([k['level_db'] for k in levels]) - own)))
                for levels, own in zip(knocks, owns))
    if worst > REFIT_CHECK:
        raise SystemExit(f'{name}: its knocks refitted depart {worst:.3f} dB from {rel(model["header"])}')
    for i, (n, m, levels) in enumerate(zip(names, measured, knocks)):
        span = m['span_s']
        modal = modal_energy(body, levels, action['decay'], action['rise'], span)
        click = click_energy(centres, m['bands'], action['rise'], span)
        takes.append({'case': n, 'note': notes[i] if i < len(notes) else None, 'onset_s': m['onset_s'],
                      'span_s': span, 'bands': m['bands'], 'kept': m['kept'],
                      'click_over_knock_a_db': 10 * math.log10(click / modal) if click > 0 else None})
    heard = [t['click_over_knock_a_db'] for t in takes if t['click_over_knock_a_db'] is not None]
    spread = f'median {np.median(heard):+.1f} dB ({min(heard):+.1f} to {max(heard):+.1f})' if heard else 'none'
    print(f'{name}: {len(heard)} of {len(takes)} takes click; click over knock, A-weighted, {spread}; '
          f'the refit departs at most {worst:.4f} dB from the header', flush=True)
    for t in takes:
        sounding = [f'{c / 1000:.3g}k {b[0]:.0f} dB {b[1]:.0f}/s' for c, b in zip(centres, t['bands'])
                    if b[0] > fit.NOISE_SILENT]
        print(f'  {t["case"]}: {"; ".join(sounding) or "silent"}', flush=True)
    return inputs | dict(sounding=False, anchors=len(notes), pedal=bool(model['pedal']),
                         refit_departure_db=worst, takes=takes)


def row(band):
    level, rate, balance = band
    return f'{{{fit.number(level)},{fit.number(rate)},{fit.number(balance)}}}'


def header_text(receipt):
    lines = [
        '// Generated by Tools/fit_action_noise.py from the train takes of each piano\'s',
        f'// split ({rel(RECEIPT)}); regenerate, never edit.',
        '// Fitted numbers only: no recorded waveform.',
        '#pragma once',
        '',
        '#include <array>',
        '',
        'namespace keyra { namespace measured {',
        '// The click of a knock of the action above the body modes, per noise band',
        '// (noiseBands): the burst a (e^(-rate t) - e^(-(rate + 1/actionRise) t))',
        '// of density a^2 (dB re 1/Hz, in the knock\'s take\'s scale, as its',
        '// ActionKnock levels are) and its right-over-left balance (dB);',
        '// densityDb -200 where the band is silent. Release clicks are per',
        '// anchor, as releaseKnocks are; the pedal going down has none to measure.',
        'struct ActionNoise { float densityDb, rate, balanceDb; };',
    ]
    for name in PIANOS:
        m = receipt['pianos'][name]
        if m['sounding']:
            lines.append(f'// {name}: its release takes are let go from sounding notes; no click.')
            continue
        anchors = m['anchors']
        releases = [band for t in m['takes'][:anchors] for band in t['bands']]
        bands = len(m['takes'][0]['bands'])
        lines.append(f'namespace {name} {{')
        lines.append(f'constexpr std::array<ActionNoise,{anchors}*{bands}> releaseNoise{{{{'
                     + ','.join(row(b) for b in releases) + '}};')
        if m['pedal']:
            lines.append(f'constexpr std::array<ActionNoise,{bands}> pedalUpNoise{{{{'
                         + ','.join(row(b) for b in m['takes'][anchors]['bands']) + '}};')
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
            raise SystemExit(f'{rel(RECEIPT)} predates the current {", ".join(sorted(stale))}: run Tools/fit_action_noise.py')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from {rel(RECEIPT)}: run Tools/fit_action_noise.py')
        print(f'{rel(HEADER)} matches {rel(RECEIPT)}')
        return
    with ProcessPoolExecutor(args.jobs) as pool:
        pianos = {name: measure_piano(name, pool) for name in PIANOS}
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   protocol=dict(window_seconds=WINDOW, hop_seconds=HOP, fade_seconds=FADE, quiet_seconds=QUIET,
                                 smooth_seconds=SMOOTH, clear_db=CLEAR, rates=list(RATES), body_top_hz=fit.BODY_TOP,
                                 action_seconds=fit.ACTION_SECONDS, refit_check_db=REFIT_CHECK,
                                 sounding=list(SOUNDING)),
                   pianos=pianos)
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
