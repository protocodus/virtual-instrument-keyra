#!/usr/bin/env python3
"""Score the undamped strings a note sets ringing, as tones, against the
recordings, for one or more `keyra_render` binaries.

Every strike sets the undamped strings from F6 up ringing, its own key's
excepted, each at the one frequency the fit's provenance lists for it
(`halo`). A train case is a recorded pitch the fit calibrated, at layers 5,
9, 13 and 16; a dev case is any of the split's dev notes, never fitted. The
recording and a render of the held note (50 ms of silence, then the layer's
velocity, sympathetic resonance off) are each timed from their onset and
scaled as the benchmark scales a case, by their RMS from 50 to 750 ms after
it (high-passed at 20 Hz). Scaled to their peaks instead, the renders'
strings read about 2 dB higher on the very notes the fit measured them in, as
a render peaks a median 0.8 dB lower over that RMS than its recording. At 1,
2 and 3 s from there, each string is measured as the fit measures it
(fit_realtime_modal.halo_tone): through a 0.5 s Hann window, the largest of
both channels' mean power within 1 Hz of its frequency, against the median
from 4 to 20 Hz either side. Where a partial of the struck key's series, as
the recording shows it, lies within HALO_APART of a string, the tone there is
that partial's, and below HALO_LOWEST the series is dense at every string:
those are left out. A render that stands over the recording there sounds a
tone the piano did not, so that is counted at every string. One under it may
only miss the noise around the string, which the recording also holds, so the
error is averaged only where the recording shows the string ringing clear of
that noise: 10 dB or more over that median.

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
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_recordings as bench  # noqa: E402
import fit_realtime_modal as fit  # noqa: E402
import piano_analysis as pa  # noqa: E402

METADATA = bench.ROOT / 'Docs/research/realtime-modal-fit-2026-10-27.json'
TRAIN_LAYERS = (5, 9, 13, 16)
TIMES = (1.0, 2.0, 3.0)


def load(path):
    """Stereo, scaled by its RMS from 50 to 750 ms after its onset as the
    benchmark scales a case, its onset sample and its sample rate."""
    sr, x = pa.load(path)
    start = pa.onset(x, sr)
    xh = signal.sosfiltfilt(signal.butter(2, 20, 'highpass', fs=sr, output='sos'), x, axis=0)
    early = xh[start + int(.05 * sr):start + int(.75 * sr)]
    return x / np.sqrt(np.mean(early * early)), start, sr


def levels(x, onset, sr, freqs):
    """Per time, each string's tone (dB re the case's scale) and how far it
    stands over the noise around it (dB)."""
    n = int(.5 * sr)
    w = np.hanning(n)
    f = np.fft.rfftfreq(8 * n, 1 / sr)
    out = {}
    for t in TIMES:
        start = onset + int((t - .25) * sr)
        if start + n <= len(x):
            z = np.fft.rfft(x[start:start + n] * w[:, None], 8 * n, axis=0) * 2 / np.sum(w)
            out[t] = [tuple(round(float(v), 1) for v in fit.halo_tone(f, z, hz)[:2]) for hz in freqs]
    return out


def score(job):
    case, note, layer, role, strings, renderers = job
    recording = load(bench.CORPUS / f'{case}.wav')
    f1, B, _ = pa.partials(recording[0], recording[2], note, recording[1])
    ladder = pa.stiff(f1, B, np.arange(1, 400))
    freqs = [s['hz'] for s in strings if s['key'] != note and np.min(np.abs(ladder - s['hz'])) >= fit.HALO_APART]
    out = {'case': case, 'role': role, 'note': note, 'layer': layer, 'hz': freqs,
           'recording': levels(*recording, freqs)}
    with tempfile.TemporaryDirectory(prefix='keyra-rings-') as tmp:
        events = Path(tmp) / 'note.events'
        events.write_text(f'{bench.LEAD} on {note} {bench.LAYER_VELOCITY[layer - 1]}\n')
        for name, renderer in renderers.items():
            wav = Path(tmp) / f'{name}.wav'
            subprocess.run([renderer, '--events', str(events), '--output', str(wav), '--sample-rate',
                            str(recording[2]), '--duration', '3.6', '--resonance', '0'] + bench.MEASURE,
                           check=True, capture_output=True)
            out[name] = levels(*load(wav), freqs)
    return out


def summary(cases, name):
    by_time = {}
    for t in TIMES:
        pairs = [(c[name][t][i][0] - c['recording'][t][i][0], c['recording'][t][i][1])
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
    strings, anchors = metadata['halo']['strings'], [a['note'] for a in metadata['anchors']]
    split = json.loads(bench.SPLIT.read_text())['cases']
    items = {i['id']: i for i in json.loads(bench.MANIFEST.read_text())['files']}
    jobs = []
    for case, role in split.items():
        item = items[case]
        if item['kind'] != 'note' or role not in ('train', 'dev') or item['midi'] < fit.HALO_LOWEST:
            continue
        if role == 'train' and (item['layer'] not in TRAIN_LAYERS or item['midi'] not in anchors):
            continue
        jobs.append((case, item['midi'], item['layer'], role, strings, renderers))
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
