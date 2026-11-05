#!/usr/bin/env python3
"""Score a Keyra renderer's action knocks above the body modes, the click,
against a piano's action takes: each take its release format names
(fit_realtime_modal.MODELS release: a key let go, the upright's hammer
takes) and, on the grand, the pedal going up (PEDAL_UP), of the roles asked.

Each release take's key is struck at DAMPER_VELOCITY, held DAMPER_HOLD s and
let go, and the pedal held PEDAL_HOLD s and let go, through a `keyra_render`
binary at the measurement gain (benchmark_recordings.MEASURE) twice: at the
Mechanics control's default and at 0. Their difference is the action alone:
the strings play alike in both. In it and in the take, from the knock's
onset over the take's span (fit_action_noise.span), the density per noise
band from BODY_TOP up as fit_action_noise.band_densities measures it (the
median of the band's bin powers, both channels' mean, so that the tones of
strings a take holds count for neither). The render is set to the take's
knock: the header's modes refitted on each (fit_action_noise.own_levels),
as the engine plays them, A-weighted (fit_action_noise.modal_energy), so
that a take's strings, which also sound from BODY_LOW to BODY_TOP, do not
set its level. The take's floor in each band (fit_action_noise.floor_of)
is added to the render; per band the |dB| difference where the take stands
FLOOR dB over its floor, and per take their mean. Lower is better. A take
with no band standing so is not scored.

  python3 Tools/benchmark_action.py --model grand --renderer build-dsp/keyra_render --out out/bench/action
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
from scipy.io import wavfile  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_recordings as bench  # noqa: E402
import fit_action_noise as fan  # noqa: E402
import fit_realtime_modal as fit  # noqa: E402
import import_modal_measurements as imm  # noqa: E402
import piano_analysis as pa  # noqa: E402

PEDAL_UP = {'grand': {'pedalU1': 'train', 'pedalU2': 'dev'}}
PEDAL_HOLD = 3.0          # s: the pedal-down knock has rung out by then
FLOOR = 6.0               # dB


def knock_energy(path, body, action, seconds):
    """The knock at `path` on the header's modes as the engine plays them."""
    levels = fan.own_levels(path, body, action['decay'], action['rise'])
    return fan.modal_energy(body, [{'level_db': v} for v in levels], action['decay'], action['rise'], seconds)


def render(renderer, model_name, events, seconds, mechanics):
    with tempfile.TemporaryDirectory(prefix='keyra-action-') as tmp:
        path, wav = Path(tmp) / 'action.events', Path(tmp) / 'render.wav'
        path.write_text(events)
        subprocess.run([renderer, '--events', str(path), '--output', str(wav), '--model', model_name,
                        '--duration', str(seconds), '--mechanics', str(mechanics)] + bench.MEASURE,
                       check=True, stdout=subprocess.DEVNULL)
        return pa.load(wav)


def run_case(args):
    model_name, take, note, renderer, mechanics = args
    model = fit.MODELS[model_name]
    table = imm.load(model['header'])
    centres = table['noise']['hz']
    path = model['wav'] / f'{take}.wav'
    sr, x = pa.load(path)
    start, stop = fan.span(x, sr)
    span = (stop - start) / sr
    _, densities = fan.band_densities(x, sr, start, stop, centres)
    if note is None:
        at, events = PEDAL_HOLD, f'0.05 pedal 1\n{PEDAL_HOLD} pedal 0\n'
    else:
        at, events = fit.DAMPER_HOLD, f'0 on {note} {fit.DAMPER_VELOCITY}\n{fit.DAMPER_HOLD} off {note} 0\n'
    seconds = at + span + 1.2
    rate, played = render(renderer, model_name, events, seconds, mechanics)
    _, silent = render(renderer, model_name, events, seconds, 0)
    y = (played - silent)[int(round(at * rate)):]
    r_start = fan.onset(y, rate)
    _, rendered = fan.band_densities(y, rate, r_start, r_start + int(round(span * rate)), centres)
    with tempfile.TemporaryDirectory(prefix='keyra-action-') as tmp:
        action_wav = Path(tmp) / 'action.wav'
        wavfile.write(str(action_wav), rate, y.astype(np.float32))
        level = (knock_energy(path, table['body'], table['action'], span)
                 / max(knock_energy(action_wav, table['body'], table['action'], span), 1e-30))
    bands = []
    for c, d, e in zip(centres, densities, rendered):
        floor = None if d is None else fan.floor_of(d)
        if floor is None or e is None:
            continue
        frames = min(len(d), len(e))
        take_energy = float(d[:frames].mean(axis=1).sum())
        floor_energy = float(floor.mean()) * frames
        if take_energy < 10 ** (FLOOR / 10) * floor_energy:
            continue
        played_energy = float(e[:frames].mean(axis=1).sum()) * level
        bands.append({'hz': round(c, 1), 'take_over_floor_db': float(10 * np.log10(take_energy / floor_energy)),
                      'error_db': float(abs(10 * np.log10(take_energy / (played_energy + floor_energy))))})
    return {'case': take, 'note': note, 'level_db': float(10 * np.log10(level)), 'bands': bands,
            'mean_db': float(np.mean([b['error_db'] for b in bands])) if bands else None}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--model', choices=list(fan.PIANOS), default='grand')
    p.add_argument('--renderer', required=True)
    p.add_argument('--mechanics', type=float, default=.175, help="the Mechanics control's default")
    p.add_argument('--roles', nargs='+', default=['train', 'dev'], choices=['train', 'dev'])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=os.cpu_count())
    a = p.parse_args()
    model = fit.MODELS[a.model]
    split = json.loads(model['split'].read_text())['cases']
    takes = [(a.model, i['id'], i['midi'], a.renderer, a.mechanics)
             for i in json.loads(model['corpus'].read_text())['files']
             if 'midi' in i and i['id'] == model['release'].format(key=i['midi'] - 20, note=i['midi'])
             and split.get(i['id']) in a.roles]
    for take, role in PEDAL_UP.get(a.model, {}).items():
        if split.get(take) != role:
            raise SystemExit(f'{take} is not in the role this benchmark scores it in')
        if role in a.roles:
            takes.append((a.model, take, None, a.renderer, a.mechanics))
    with concurrent.futures.ProcessPoolExecutor(a.jobs) as pool:
        rows = list(pool.map(run_case, takes))
    for r in rows:
        r['role'] = split[r['case']]
    rows.sort(key=lambda r: (r['note'] is None, r['note'] or 0))
    scored = [r for r in rows if r['mean_db'] is not None]
    summary = {role: {'takes': len(v), 'mean_db': float(np.mean([r['mean_db'] for r in v]))}
               for role in a.roles if (v := [r for r in scored if r['role'] == role])}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / 'report.json').write_text(json.dumps({'renderer': a.renderer, 'model': a.model, 'mechanics': a.mechanics,
                                                   'summary': summary, 'cases': rows}, indent=1) + '\n')
    lines = ['| take | role | bands | mean dB |', '|---|---|---|---|']
    lines += [f'| {r["case"]} | {r["role"]} | {len(r["bands"])} | '
              f'{"-" if r["mean_db"] is None else format(r["mean_db"], ".2f")} |' for r in rows]
    lines += [''] + [f'{role}: {s["takes"]} takes, mean {s["mean_db"]:.2f} dB' for role, s in summary.items()]
    (a.out / 'summary.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
