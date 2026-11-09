#!/usr/bin/env python3
"""Measure how much of the benchmark's partial error comes from orders a
render lacks: the evidence for fillGap() and denseGap() in KeyraEngine.cpp
(Docs/research/series-orders-2026-11-09.md).

Each train and dev take of a piano's locked split (fit_realtime_modal.MODELS)
is rendered at its layer's velocity as benchmark_recordings renders it (LEAD,
MEASURE) and scored as its partial_db scores it: every order the recording
holds, in each of the measure's windows, where it stands 10 dB over its
floor and within 50 dB of the strongest partial, is a cell, its error the
render's level there less the recording's at the benchmark's gain, at most
30 dB. A cell whose order the render does not play scores 30 dB. Per piano
and role, the table gives the cells, their mean error, the share of cells
whose order the render lacks and the share of the error they carry, for each
renderer. Sealed takes are never read, and nothing is fitted.

  python3 -B Tools/measure_absent_orders.py --renderer 0.4.29=old/keyra_render \\
      --renderer 0.4.30=build/keyra_render [--model kawai] [--jobs 3] [--cache DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.path.insert(0, str(Path(__file__).resolve().parent))

import benchmark_recordings as br
import fit_realtime_modal as fit

NAMES = {'grand': 'Kakegawa grand', 'upright': 'upright', 'kawai': 'Hamamatsu grand',
         'hamburg': 'Hamburg grand', 'newyork': 'New York grand'}


def cells(ref: dict, mod: dict) -> list[tuple[float, bool]]:
    """(error in dB, whether the render lacks the order) for each scored cell."""
    gain = 10 ** (br.compare(ref, mod)['gain_db'] / 10)
    played = {n: i for i, n in enumerate(mod['n'])}
    windows = [(lo, hi) for lo, hi in br.WINDOWS
               if br.window_db(ref['env_t'], ref['env_power'][0], lo, hi) is not None]
    strongest = [max(br.window_db(ref['env_t'], p, lo, hi) for p in ref['env_power']) for lo, hi in windows]
    out = []
    for i, n in enumerate(ref['n']):
        j = played.get(n)
        for (lo, hi), top in zip(windows, strongest):
            level = br.window_db(ref['env_t'], ref['env_power'][i], lo, hi)
            if level is None or level < max(ref['floor'][i] + 10, top - 50):
                continue
            rendered = br.window_db(mod['env_t'], mod['env_power'][j] * gain, lo, hi) if j is not None else -300.
            out.append((min(abs(rendered - level), 30.), j is None))
    return out


def measure(job):
    case, note, velocity, renderers, extra, wav_dir, cache = job
    ref = br.cached_reference(case, note, Path(cache), Path(wav_dir))
    row = {'case': case}
    with tempfile.TemporaryDirectory(prefix='keyra-orders-') as tmp:
        events = Path(tmp) / 'note.events'
        events.write_text(f'{br.LEAD} on {note} {velocity}\n')
        for label, renderer in renderers:
            wav = Path(tmp) / 'render.wav'
            subprocess.run([renderer, '--events', str(events), '--output', str(wav),
                            '--duration', str(br.RENDER_SECONDS)] + br.MEASURE + extra,
                           check=True, stdout=subprocess.DEVNULL)
            row[label] = cells(ref, br.features(wav, note, ref))
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--renderer', action='append', required=True, metavar='LABEL=PATH')
    parser.add_argument('--model', action='append', choices=list(NAMES))
    parser.add_argument('--jobs', type=int, default=3)
    parser.add_argument('--cache', default=None, help='reference feature cache (default: a temporary one)')
    args = parser.parse_args()
    renderers = [tuple(r.split('=', 1)) for r in args.renderer]
    print('| piano | role | takes | renderer | cells | mean error dB | orders lacked | their share of the error |')
    print('|---|---|---|---|---|---|---|---|')
    with tempfile.TemporaryDirectory(prefix='keyra-orders-cache-') as scratch:
        cache = args.cache or scratch
        for model in args.model or list(NAMES):
            m = fit.MODELS[model]
            roles = json.loads(m['split'].read_text())['cases']
            items = {i['id']: i for i in json.loads(m['corpus'].read_text())['files']}
            extra = ['--model', model] if model != 'grand' else []
            for role in ('train', 'dev'):
                jobs = [(case, items[case]['midi'], fit.layer_velocity(items[case]), renderers, extra,
                         str(m['wav']), cache)
                        for case, r in roles.items()
                        if r == role and items[case].get('kind') == 'note' and items[case].get('midi')]
                with ProcessPoolExecutor(args.jobs) as pool:
                    rows = list(pool.map(measure, jobs, chunksize=2))
                for k, (label, _) in enumerate(renderers):
                    scored = [c for row in rows for c in row[label]]
                    total = sum(e for e, _ in scored)
                    lacked = [e for e, absent in scored if absent]
                    head = [NAMES[model], role, str(len(rows))] if k == 0 else ['', '', '']
                    print('| ' + ' | '.join(head + [label, str(len(scored)), f'{total / len(scored):.2f}',
                                                    f'{100 * len(lacked) / len(scored):.1f} %',
                                                    f'{100 * sum(lacked) / total:.0f} %']) + ' |', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
