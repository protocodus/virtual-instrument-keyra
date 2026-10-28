#!/usr/bin/env python3
"""Score the undamped strings a note sets ringing, narrow-band, against the
recordings, for one or more `keyra_render` binaries.

The fit measures a string through a window as wide as the gap to its
neighbours, which also holds the board's noise; this measures it as a tone.
A train case is a recorded pitch that the fit's provenance lists strings for,
at layers 5, 9, 13 and 16; a dev case is any of the split's dev notes, never
fitted, with the strings the engine plays there: its recorded pitch's, or
both neighbouring pitches'. The recording and a render of the held note (50 ms
of silence, then the layer's velocity, sympathetic resonance off) are each
normalised to their peak and timed from the first sample within 20 dB of it.
At 1, 2 and 3 s from there, each string's level is the largest amplitude
within 2 Hz of its frequency through a 0.5 s Hann window. A render that
stands over the recording there sounds a tone the piano did not, so that is
counted at every string. One under it may only miss the noise around the
string, which the recording also holds, so the error is averaged only where
the recording shows the string ringing clear of that noise: 10 dB or more
over the median level from 4 to 20 Hz either side of it.

  python3 Tools/compare_ring_levels.py --renderer candidate=build-dsp/keyra_render \\
      --renderer shipping=out/shipping/keyra_render --out out/rings.json
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

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_recordings as bench  # noqa: E402

METADATA = bench.ROOT / 'Docs/research/realtime-modal-fit-2026-10-27.json'
TRAIN_LAYERS = (5, 9, 13, 16)
TIMES = (1.0, 2.0, 3.0)


def load(path):
    """Mono, normalised to its peak, its onset sample and its sample rate."""
    sr, x = wavfile.read(path)
    y = x.astype(float)
    y = y.mean(axis=1) if y.ndim == 2 else y
    y /= np.max(np.abs(y))
    return y, int(np.flatnonzero(np.abs(y) > .1)[0]), sr


def levels(y, onset, sr, freqs):
    """Per time, each string's level (dB re peak) and the noise around it."""
    n = int(.5 * sr)
    w = np.hanning(n)
    f = np.fft.rfftfreq(8 * n, 1 / sr)
    out = {}
    for t in TIMES:
        start = onset + int((t - .25) * sr)
        if start + n <= len(y):
            spectrum = np.abs(np.fft.rfft(y[start:start + n] * w, 8 * n)) * 2 / np.sum(w)
            db = lambda x: round(float(20 * np.log10(x + 1e-12)), 1)
            out[t] = [(db(np.max(spectrum[np.abs(f - hz) < 2])),
                       db(np.median(spectrum[(np.abs(f - hz) >= 4) & (np.abs(f - hz) <= 20)]))) for hz in freqs]
    return out


def strings_at(anchors, note):
    """The strings the engine plays for `note`: its recorded pitch's, or both
    neighbouring pitches'."""
    notes = [a['note'] for a in anchors]
    if note in notes:
        return anchors[notes.index(note)]['rings']
    lower = [a for a in anchors if a['note'] < note][-1:]
    upper = [a for a in anchors if a['note'] > note][:1]
    return sorted({ring for a in lower + upper for ring in a['rings']})


def score(job):
    case, note, layer, role, freqs, renderers = job
    recording = load(bench.CORPUS / f'{case}.wav')
    out = {'case': case, 'role': role, 'note': note, 'layer': layer, 'hz': freqs,
           'recording': levels(*recording, freqs)}
    with tempfile.TemporaryDirectory(prefix='keyra-rings-') as tmp:
        events = Path(tmp) / 'note.events'
        events.write_text(f'{bench.LEAD} on {note} {bench.LAYER_VELOCITY[layer - 1]}\n')
        for name, renderer in renderers.items():
            wav = Path(tmp) / f'{name}.wav'
            subprocess.run([renderer, '--events', str(events), '--output', str(wav), '--sample-rate',
                            str(recording[2]), '--duration', '3.6', '--resonance', '0'], check=True, capture_output=True)
            out[name] = levels(*load(wav), freqs)
    return out


def summary(cases, name):
    by_time = {}
    for t in TIMES:
        pairs = [(c[name][t][i][0] - c['recording'][t][i][0], c['recording'][t][i][0] - c['recording'][t][i][1])
                 for c in cases if t in c[name] and t in c['recording'] for i in range(len(c['hz']))]
        d = np.array([difference for difference, _ in pairs])
        clear = np.array([difference for difference, above in pairs if above >= 10])
        by_time[f'{t:g} s'] = {'strings': len(d), 'over_10_db': round(float(np.mean(d > 10)), 3),
                               'over_20_db': round(float(np.mean(d > 20)), 3), 'clear': len(clear),
                               'clear_median_db': round(float(np.median(clear)), 1),
                               'clear_mean_abs_db': round(float(np.mean(np.abs(clear))), 1),
                               'clear_under_10_db': round(float(np.mean(clear < -10)), 3)}
    return by_time


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--renderer', action='append', required=True, help='name=path to keyra_render')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=os.cpu_count())
    args = parser.parse_args()
    renderers = dict(spec.split('=', 1) for spec in args.renderer)
    metadata = json.loads(METADATA.read_text())
    strings, anchors = metadata['rings']['strings'], metadata['anchors']
    split = json.loads(bench.SPLIT.read_text())['cases']
    items = {i['id']: i for i in json.loads(bench.MANIFEST.read_text())['files']}
    jobs = []
    for case, role in split.items():
        item = items[case]
        if item['kind'] != 'note' or role not in ('train', 'dev'):
            continue
        if role == 'train' and (item['layer'] not in TRAIN_LAYERS or item['midi'] not in [a['note'] for a in anchors]):
            continue
        rings = strings_at(anchors, item['midi'])
        if rings:
            jobs.append((case, item['midi'], item['layer'], role, [strings[ring]['hz'] for ring in rings], renderers))
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        cases = sorted(pool.map(score, jobs), key=lambda c: (c['role'], c['note'], c['layer']))
    report = {'summary': {role: {name: summary([c for c in cases if c['role'] == role], name) for name in renderers}
                          for role in ('train', 'dev')}, 'cases': cases}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1) + '\n')
    for role, by_name in report['summary'].items():
        for name, by_time in by_name.items():
            for t, s in by_time.items():
                print(f'{role} {name} {t}: {s}')


if __name__ == '__main__':
    main()
