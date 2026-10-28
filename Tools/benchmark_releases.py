#!/usr/bin/env python3
"""Score a Keyra renderer's key releases against a piano's key-release
recordings: the upright's Helsinki 1967 release takes, each a key let go and
recorded from about the key-up.

Each take's key is struck at velocity 85, held 1.5 s and let go through a
`keyra_render` binary (the takes match such a note; see
fit_realtime_modal.DAMPER_HOLD). The take's partials are those of the key's
loudest note recording up to the tenth, 25 dB over the take's floor (its
last half second) in its first 60 ms. The render is cut where the take would
start, the key-up `shift` seconds into the take (searched every 10 ms from
-60 to 400 ms, the best kept), and both are measured with
piano_analysis.envelopes at those partials every 10 ms to 3 s, or half a
second before the take's end; the take's floor is added to the render in
power. Per partial one level offset is removed (soft L1, 2 dB), so only the
shape of each partial's release is scored: the mean |dB error| over the
frames where the take stands 6 dB over its floor, per take over all its
partials' frames. Lower is better. A take's partials can also hold an
undamped string's sympathy, which the halo plays, and a stray sound in a take
scores against every renderer alike.

  python3 Tools/benchmark_releases.py --renderer build-dsp/keyra_render --out out/bench/releases
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np  # noqa: E402
from scipy import optimize  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_recordings as bench  # noqa: E402
import fit_realtime_modal as fit  # noqa: E402
import piano_analysis as pa  # noqa: E402

VELOCITY, HOLD = fit.DAMPER_VELOCITY, fit.DAMPER_HOLD
SHIFTS = np.arange(-.06, .4001, .01)


def take_partials(model, take, note):
    """The take's frame times and, per partial it shows, (order, Hz, dB, floor dB)."""
    items = json.loads(model['corpus'].read_text())['files']
    loud = max((i for i in items if i['kind'] == 'note' and i['midi'] == note and i.get('round_robin', 1) == 1),
               key=lambda i: i['layer'])
    sr, x = pa.load(model['wav'] / f'{loud["id"]}.wav')
    f1, _, found = pa.partials(x, sr, note, pa.onset(x, sr))
    orders = [(q['n'], q['hz']) for q in found if q['n'] <= 10]
    sr, x = pa.load(model['wav'] / f'{take}.wav')
    end = len(x) / sr
    times = np.arange(0, min(fit.DAMPER_SECONDS, end - .55), .01)
    hz = [h for _, h in orders]
    _, z = pa.envelopes(x, sr, hz, f1, 0, None, times=times)
    db = 10 * np.log10(np.mean(np.abs(z) ** 2, axis=1) + 1e-30)
    _, z = pa.envelopes(x, sr, hz, f1, 0, None, times=np.arange(end - .5, end - .03, .01))
    floors = 10 * np.log10(np.mean(np.abs(z) ** 2, axis=(1, 2)) + 1e-30)
    return f1, times, [(n, h, p, float(e)) for (n, h), p, e in zip(orders, db, floors)
                       if p[times <= .06].max() >= e + 25]


def soft_l1(r):
    return float(np.sum(4 * (np.sqrt(1 + (r / 2) ** 2) - 1)))


def partial_error(take_db, render_db, floor):
    """The best level offset's (loss, |errors|) over the take's frames 6 dB over its floor."""
    use = take_db > floor + 6

    def errors(level):
        return (take_db - 10 * np.log10(10 ** ((render_db + level) / 10) + 10 ** (floor / 10)))[use]
    start = float(np.median((take_db - render_db)[use]))
    best = optimize.minimize_scalar(lambda level: soft_l1(errors(level)), bracket=(start - 5, start + 5))
    e = np.abs(errors(best.x))
    return soft_l1(e), e


def run_case(args):
    model_name, take, note, renderer = args
    model = fit.MODELS[model_name]
    f1, times, partials = take_partials(model, take, note)
    with tempfile.TemporaryDirectory(prefix='keyra-release-') as tmp:
        events, wav = Path(tmp) / 'release.events', Path(tmp) / 'render.wav'
        events.write_text(f'0 on {note} {VELOCITY}\n{HOLD} off {note} 0\n')
        subprocess.run([renderer, '--events', str(events), '--output', str(wav), '--model', model_name,
                        '--duration', str(HOLD + SHIFTS[-1] + times[-1] + .2)] + bench.MEASURE,
                       check=True, stdout=subprocess.DEVNULL)
        sr, x = pa.load(wav)
    best = None
    for shift in SHIFTS:
        _, z = pa.envelopes(x[int(round((HOLD - shift) * sr)):], sr, [h for _, h, _, _ in partials], f1, 0, None,
                            times=times)
        render = 10 * np.log10(np.mean(np.abs(z) ** 2, axis=1) + 1e-30)
        scored = [partial_error(p, r, floor) for (_, _, p, floor), r in zip(partials, render)]
        loss = sum(s for s, _ in scored)
        if best is None or loss < best[0]:
            best = (loss, shift, scored)
    _, shift, scored = best
    frames = np.concatenate([e for _, e in scored])
    return {'case': take, 'note': note, 'key_up_ms': round(1000 * float(shift)), 'mean_db': float(np.mean(frames)),
            'partials': [{'order': n, 'hz': round(h, 1), 'mean_db': round(float(np.mean(e)), 3), 'frames': len(e)}
                         for (n, h, _, _), (_, e) in zip(partials, scored)]}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--model', choices=[m for m, spec in fit.MODELS.items() if spec.get('damper')], default='upright')
    p.add_argument('--renderer', required=True)
    p.add_argument('--roles', nargs='+', default=['train', 'dev'], choices=['train', 'dev'])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=os.cpu_count())
    a = p.parse_args()
    model = fit.MODELS[a.model]
    split = json.loads(model['split'].read_text())['cases']
    takes = [(a.model, i['id'], i['midi'], a.renderer) for i in json.loads(model['corpus'].read_text())['files']
             if i['kind'] == 'key-release' and i['midi'] < fit.UNDAMPED.start and split.get(i['id']) in a.roles]
    with concurrent.futures.ProcessPoolExecutor(a.jobs) as pool:
        rows = sorted(pool.map(run_case, takes), key=lambda r: r['note'])
    for r in rows:
        r['role'] = split[r['case']]
    summary = {role: {'takes': len(v), 'mean_db': float(np.mean([r['mean_db'] for r in v]))}
               for role in a.roles if (v := [r for r in rows if r['role'] == role])}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / 'report.json').write_text(json.dumps({'renderer': a.renderer, 'model': a.model, 'summary': summary,
                                                   'cases': rows}, indent=1) + '\n')
    lines = ['| take | role | key-up ms | mean dB |', '|---|---|---|---|']
    lines += [f'| {r["case"]} | {r["role"]} | {r["key_up_ms"]} | {r["mean_db"]:.2f} |' for r in rows]
    lines += [''] + [f'{role}: {s["takes"]} takes, mean {s["mean_db"]:.2f} dB' for role, s in summary.items()]
    (a.out / 'summary.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
