#!/usr/bin/env python3
"""Sets the physical piano's single notes beside recorded ones.

For each recorded note it renders the same key and blow through
render_model and measures both by Tools/piano_analysis.py's one protocol:
pitch and inharmonicity, each third-octave band's share of the first 300 ms,
the level's fall after 1 and 3 s, and the first partials' own levels and
decays. Levels are compared in shape only: a library's gain is its own.

usage: compare_model_notes.py --render build/render_model [--body concert]
           [--set name=value ...] note:velocity:recording.wav ...
"""
import argparse, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import piano_analysis as pa

BANDS = 1000.0 * 2.0 ** np.arange(-5, 5)  # 31 Hz .. 16 kHz octaves


def measure(path, note):
    sr, x = pa.load(path)
    start = pa.onset(x, sr)
    f1, B, found = pa.partials(x, sr, note, start)
    mono_power = np.mean(x * x, axis=1)
    def level(a, b):
        seg = mono_power[start + int(a * sr):start + int(b * sr)]
        return 10 * np.log10(max(np.mean(seg), 1e-20)) if len(seg) else float('nan')
    seg = x[start:start + int(.3 * sr)].mean(axis=1)
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    hz = np.fft.rfftfreq(len(seg), 1 / sr)
    bands = np.array([spec[(hz >= c / 2 ** .5) & (hz < c * 2 ** .5)].sum() for c in BANDS])
    bands = 10 * np.log10(np.maximum(bands / max(spec.sum(), 1e-30), 1e-12))
    centroid = float((hz * spec).sum() / max(spec.sum(), 1e-30))
    orders = [q for q in found if q['n'] <= 8]
    seconds = min(6.0, (len(x) - start) / sr - .3)
    rows = {}
    if orders and seconds > 1:
        t, z = pa.envelopes(x, sr, [q['hz'] for q in orders], f1, start, seconds, hop=int(.02 * sr))
        amp = 10 * np.log10(np.maximum((np.abs(z) ** 2).mean(axis=1), 1e-30))
        for q, a in zip(orders, amp):
            def at(s):
                i = np.searchsorted(t, s)
                return a[min(i, len(a) - 1)]
            early = (at(1.1) - at(.1))
            late = (at(min(seconds - .1, 5.1)) - at(2.1)) / max(min(seconds - .1, 5.1) - 2.1, 1e-9) if seconds > 3 else float('nan')
            rows[q['n']] = (a[:int(.3 / .02)].max(), early, late)
    return dict(f1=f1, B=B, n=len(found), top=max(q['hz'] for q in found) if found else 0, centroid=centroid, bands=bands,
                fall1=level(1.0, 1.2) - level(.05, .25), fall3=level(3.0, 3.2) - level(.05, .25),
                attack=level(0, .03) - level(.05, .25), rows=rows, peak=level(0, .3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--render', required=True)
    ap.add_argument('--body', default='concert')
    ap.add_argument('--mics', default='1,0,0,0')
    ap.add_argument('--set', nargs='*', default=[])
    ap.add_argument('--keep')
    ap.add_argument('notes', nargs='+')
    a = ap.parse_args()
    extra = []
    for s in a.set:
        k, v = s.split('=')
        extra += ['--' + k, v]
    with tempfile.TemporaryDirectory() as tmp:
        for spec in a.notes:
            note, velocity, path = spec.split(':', 2)
            note, velocity = int(note), int(velocity)
            events = Path(tmp) / 'e.events'
            events.write_text(f'0.05 on {note} {velocity}\n12 off {note} 0\n')
            out = Path(a.keep or tmp) / f'model-{note}-{velocity}.wav'
            subprocess.run([a.render, '--events', str(events), '--output', str(out), '--duration', '8', '--body', a.body,
                            '--mics', a.mics] + extra, check=True, stderr=subprocess.DEVNULL)
            r, m = measure(path, note), measure(out, note)
            print(f'\n== note {note} velocity {velocity}   recording | model')
            print(f'  f1 {r["f1"]:8.2f} | {m["f1"]:8.2f} Hz    B {r["B"]:.2e} | {m["B"]:.2e}    partials {r["n"]} | {m["n"]}   top {r["top"]:.0f} | {m["top"]:.0f} Hz')
            print(f'  centroid {r["centroid"]:6.0f} | {m["centroid"]:6.0f} Hz   level {r["peak"]:.1f} | {m["peak"]:.1f} dB   attack {r["attack"]:+.1f} | {m["attack"]:+.1f}   fall 1 s {r["fall1"]:+.1f} | {m["fall1"]:+.1f}   3 s {r["fall3"]:+.1f} | {m["fall3"]:+.1f} dB')
            print('  octave  ' + ' '.join(f'{c:6.0f}' for c in BANDS))
            print('  rec dB  ' + ' '.join(f'{b:6.1f}' for b in r['bands']))
            print('  model   ' + ' '.join(f'{b:6.1f}' for b in m['bands']))
            print('  diff    ' + ' '.join(f'{b - c:+6.1f}' for b, c in zip(m['bands'], r['bands'])))
            ns = sorted(set(r['rows']) & set(m['rows']))
            if ns:
                ref = r['rows'][ns[0]][0], m['rows'][ns[0]][0]
                print('  partial  level re first (rec|model)   first-second fall   later dB/s')
                for n in ns:
                    p, q = r['rows'][n], m['rows'][n]
                    print(f'   {n:2d}      {p[0] - ref[0]:+6.1f} | {q[0] - ref[1]:+6.1f}        {p[1]:+6.1f} | {q[1]:+6.1f}     {p[2]:+6.1f} | {q[2]:+6.1f}')


if __name__ == '__main__':
    main()
