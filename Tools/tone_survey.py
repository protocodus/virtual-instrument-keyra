#!/usr/bin/env python3
"""Where a Keyra renderer's tone and stereo image stand over or under a
piano's recordings, signed, per third-octave band.

Every train and dev note case of the piano's split is rendered and measured
as Tools/benchmark_recordings.py renders and measures it (same renderer
options, features and gain: one gain from the 50 to 750 ms RMS). Per band:

- attack, early and sustain: render less recording level (dB) over 0 to
  0.1 s, 0.1 to 0.5 s and 0.5 to 3 s, where the recording stands within
  50 dB of its loudest band in the window and 10 dB over its floor;
- side_mid, ild and icc: render less recording side-over-mid (dB), right-
  over-left (dB) and interchannel coherence over 0.05 to 1.5 s, where the
  recording stands within 40 dB of its loudest band and 10 dB over its
  floor; side_mid_ref and icc_ref hold the recording's own;
- noise: render less recording residual between the partials (dB) over
  the benchmark's first 0.3 s.

The benchmark scores these unsigned and pooled; signed and per band, they
show which way a register's tone leans and where. --compare prints two
surveys' per-register medians side by side.

  python3 Tools/tone_survey.py --renderer build-dsp/keyra_render --out out/survey/grand [--model upright]
  python3 Tools/tone_survey.py --compare out/survey/before.json out/survey/after.json --measure early --role dev
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_recordings as bench  # noqa: E402
import fit_realtime_modal as fit  # noqa: E402
import piano_analysis as pa  # noqa: E402

WINDOWS = {'attack': (0, .1), 'early': (.1, .5), 'sustain': (.5, 3.0)}
HOP = .01                                   # benchmark_recordings.band_spectrogram's


def survey(ref, mod):
    """One case's signed differences per band; NaN where a band is not scored."""
    g = (ref['early_rms'] / max(mod['early_rms'], 1e-20)) ** 2
    out = {}
    for name, (lo, hi) in WINDOWS.items():
        a, b = int(lo / HOP), int(hi / HOP)
        r = 10 * np.log10(np.maximum(np.mean(10 ** (ref['bands'][a:b] / 10), axis=0), 1e-30))
        m = 10 * np.log10(np.maximum(np.mean(10 ** (mod['bands'][a:b] / 10), axis=0) * g, 1e-30))
        out[name] = np.where((r > r.max() - 50) & (r > ref['band_floor'] + 10), m - r, np.nan)
    a, b = int(.05 / HOP), int(1.5 / HOP)

    def stereo(f):
        left, right, cross = f['left'][a:b].sum(0), f['right'][a:b].sum(0), f['cross'][a:b].sum(0)
        mid, side = left + right + 2 * cross.real, left + right - 2 * cross.real
        return (10 * np.log10(np.maximum(side, 1e-30) / np.maximum(mid, 1e-30)),
                10 * np.log10(np.maximum(right, 1e-30) / np.maximum(left, 1e-30)),
                np.abs(cross) / np.sqrt(np.maximum(left * right, 1e-60)))
    (rs, ri, rc), (ms, mi, mc) = stereo(ref), stereo(mod)
    r = 10 * np.log10(np.maximum(np.mean(10 ** (ref['bands'][a:b] / 10), axis=0), 1e-30))
    keep = (r > r.max() - 40) & (r > ref['band_floor'] + 10)
    out.update({'side_mid': np.where(keep, ms - rs, np.nan), 'side_mid_ref': np.where(keep, rs, np.nan),
                'ild': np.where(keep, mi - ri, np.nan),
                'icc': np.where(keep, mc - rc, np.nan), 'icc_ref': np.where(keep, rc, np.nan)})
    rn, mn = np.asarray(ref['noise'], float), np.asarray(mod['noise'], float)
    if rn.ndim == 2:
        rn = 10 * np.log10(np.maximum(np.mean(10 ** (rn / 10), axis=0), 1e-30))
        mn = 10 * np.log10(np.maximum(np.mean(10 ** (mn / 10), axis=0), 1e-30))
    out['noise'] = np.where(rn > np.nanmax(rn) - 40, mn + 10 * math.log10(g) - rn, np.nan)
    return out


def run(job):
    case, note, layer, velocity, renderer, options, wav, cache = job
    ref = bench.cached_reference(case, note, cache, wav)
    with tempfile.TemporaryDirectory() as tmp:
        events, render = Path(tmp) / 'note.events', Path(tmp) / f'{case}.wav'
        events.write_text(f'{bench.LEAD} on {note} {velocity}\n')
        subprocess.run([renderer, '--events', str(events), '--output', str(render),
                        '--duration', str(bench.RENDER_SECONDS)] + bench.MEASURE + options,
                       check=True, stdout=subprocess.DEVNULL)
        mod = bench.features(render, note, ref)
    return {'case': case, 'note': note, 'layer': layer,
            **{k: [None if not np.isfinite(v) else float(v) for v in values]
               for k, values in survey(ref, mod).items()}}


def register(note):
    return 'bass' if note < 48 else 'middle' if note < 84 else 'treble'


def compare(paths, measure, role):
    """Per band, two surveys' median over a role's cases, all and by register."""
    before, after = (json.loads(Path(p).read_text()) for p in paths)
    registers = ['all', 'bass', 'middle', 'treble']

    def median(survey, where, i):
        values = [row[measure][i] for row in survey['rows'] if row['role'] == role
                  and where in ('all', register(row['note'])) and row[measure][i] is not None
                  and math.isfinite(row[measure][i])]
        return float(np.median(values)) if len(values) >= 5 else float('nan')
    print(f'{measure}, {role}: median per band, {paths[0]} -> {paths[1]}')
    print('   band Hz' + ''.join(f'{r:>16s}' for r in registers))
    for i, hz in enumerate(before['bands']):
        cells = [(median(before, r, i), median(after, r, i)) for r in registers]
        if any(np.isfinite(c).any() for c in cells):
            print(f'{hz:9.0f}' + ''.join(f'   {a:6.2f} {b:6.2f}' for a, b in cells))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--model', choices=fit.MODELS, default='grand')
    p.add_argument('--renderer')
    p.add_argument('--out', type=Path, help='the survey JSON')
    p.add_argument('--roles', nargs='+', default=['train', 'dev'])
    p.add_argument('--jobs', type=int, default=os.cpu_count())
    p.add_argument('--cache', type=Path, default=bench.ROOT / 'out/bench/reference-cache')
    p.add_argument('--compare', nargs=2, metavar='SURVEY')
    p.add_argument('--measure', default='early', choices=list(WINDOWS) + ['side_mid', 'ild', 'icc', 'noise'])
    p.add_argument('--role', default='train')
    args = p.parse_args()
    if args.compare:
        compare(args.compare, args.measure, args.role)
        return
    if not args.renderer or not args.out:
        p.error('--renderer and --out are required to survey')
    model = fit.MODELS[args.model]
    split = json.loads(model['split'].read_text())['cases']
    items = {i['id']: i for i in json.loads(model['corpus'].read_text())['files']}
    options = ['--model', args.model] if args.model != 'grand' else []
    jobs = [(case, items[case]['midi'], items[case]['layer'], fit.layer_velocity(items[case]), args.renderer,
             options, model['wav'], args.cache)
            for case, role in split.items() if role in args.roles and items[case]['kind'] == 'note']
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        rows = list(pool.map(run, jobs))
    for row in rows:
        row['role'] = split[row['case']]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({'model': args.model, 'renderer': args.renderer,
                                    'bands': pa.THIRD_OCTAVE.tolist(), 'rows': rows}))
    print(f'{len(rows)} cases surveyed into {args.out}')


if __name__ == '__main__':
    main()
