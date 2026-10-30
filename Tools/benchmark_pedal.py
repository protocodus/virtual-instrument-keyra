#!/usr/bin/env python3
"""Score a Keyra renderer's sustain pedal going down against the grand's
pedal-down takes (Salamander's pedalD1, train, and pedalD2, dev): the knock,
then the strings the dampers free ringing on.

The renderer plays the pedal down at 50 ms on the grand at its default
controls. In the render and in each take, from the onset (where the power
over 5 ms first comes within 30 dB of its peak), per third-octave band of
fit_realtime_modal.LIFT_BANDS (63 Hz to 5 kHz): the ring, the energy from 0.3
to 2.3 s, against the knock, the whole energy of the first 0.3 s, and the
fall from that ring to the energy from 2.3 to 4.3 s; both in dB, so neither
depends on the file's scale. The whole ring against the knock, and the
string peaks fit_realtime_modal.open_ring_peaks finds and their median decay,
are reported beside them. Per take, the mean |dB| difference over the bands
of each measure; lower is better.

  python3 Tools/benchmark_pedal.py --renderer build-dsp/keyra_render --out out/bench/pedal
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_realtime_modal as fit  # noqa: E402
import piano_analysis as pa  # noqa: E402

TAKES = {'pedalD1': 'train', 'pedalD2': 'dev'}


def measure(path):
    """The file's knock, ring and fall per band (dB), its whole ring against
    its knock, and its string peaks."""
    sr, x = pa.load(path)
    m = x.mean(axis=1)
    step = int(.005 * sr)
    power = np.array([np.mean(m[i:i + step] ** 2) for i in range(0, len(m) - step, step)])
    onset = int(np.flatnonzero(power >= power.max() * 1e-3)[0]) * step

    def bands(t0, t1):
        y = x[onset + int(t0 * sr):onset + int(t1 * sr)]
        spectrum = np.mean(np.abs(np.fft.rfft(y, axis=0)) ** 2, axis=1)
        hz = np.fft.rfftfreq(len(y), 1 / sr)
        return np.array([spectrum[(hz >= f * 2 ** (-1 / 6)) & (hz < f * 2 ** (1 / 6))].sum() for f in fit.LIFT_BANDS])
    knock, ring, late = bands(0, .3), bands(.3, 2.3), bands(2.3, 4.3)
    peaks = fit.open_ring_peaks(path)
    falling = [p['db_s'] for p in peaks if p['upper_db_s'] < 0]
    return {'ring_over_knock_db': [float(v) for v in 10 * np.log10(ring / knock.sum())],
            'fall_db': [float(v) for v in 10 * np.log10(late / ring)],
            'whole_ring_over_knock_db': float(10 * np.log10(ring.sum() / knock.sum())),
            'peaks': len(peaks), 'median_decay_db_s': float(np.median(falling)) if falling else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--renderer', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    model = fit.MODELS['grand']
    roles = json.loads(model['split'].read_text())['cases']
    if any(roles.get(take) != role for take, role in TAKES.items()):
        raise SystemExit('the pedal takes are not in the roles this benchmark scores')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        events, render = Path(tmp) / 'pedal.events', out / 'pedal-down.wav'
        events.write_text('0.05 pedal 1\n')
        subprocess.run([args.renderer, '--events', str(events), '--output', str(render), '--duration', '6.5',
                        '--model', 'grand'], check=True, stdout=subprocess.DEVNULL)
        rendered = measure(render)
    report = {'renderer': args.renderer, 'band_hz': [round(f, 1) for f in fit.LIFT_BANDS], 'render': rendered,
              'takes': {}}
    for take, role in TAKES.items():
        measured = measure(model['wav'] / f'{take}.wav')
        report['takes'][take] = {'role': role, **measured, **{
            f'{key}_error_db': float(np.mean(np.abs(np.array(rendered[key]) - np.array(measured[key]))))
            for key in ('ring_over_knock_db', 'fall_db')}}
    (out / 'report.json').write_text(json.dumps(report, indent=1) + '\n')
    decay = rendered['median_decay_db_s']
    print(f'render: whole ring over knock {rendered["whole_ring_over_knock_db"]:.1f} dB, {rendered["peaks"]} peaks, '
          f'median decay {"none" if decay is None else f"{decay:.2f}"} dB/s')
    for take, r in report['takes'].items():
        print(f'{take} ({r["role"]}): whole ring over knock {r["whole_ring_over_knock_db"]:.1f} dB, {r["peaks"]} peaks, '
              f'median decay {r["median_decay_db_s"]:.2f} dB/s; band errors: ring over knock '
              f'{r["ring_over_knock_db_error_db"]:.2f} dB, fall {r["fall_db_error_db"]:.2f} dB')


if __name__ == '__main__':
    main()
