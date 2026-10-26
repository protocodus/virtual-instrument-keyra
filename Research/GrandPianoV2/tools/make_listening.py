#!/usr/bin/env python3
"""Export onset-aligned real / v1 / v2 listening triplets without room effects.

Exactly one early-RMS gain per model note; it remains fixed for the full decay.
These are listening aids, not additional measurements or a blind evaluation.
"""
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from render import file_hash, true_peak, write_pcm24, measure

ROOT = Path(__file__).resolve().parents[1]
FS = 48000
IDS = ['C2v8', 'C4v8', 'C6v8', 'F#3v8', 'C1v8', 'C7v8']


def read(path):
    rate, x = wavfile.read(path)
    if x.dtype.kind in 'iu':
        x = x.astype(np.float64) / 2 ** (x.dtype.itemsize * 8 - 1)
    else:
        x = x.astype(np.float64)
    if rate != FS:
        d = math.gcd(rate, FS)
        x = resample_poly(x, FS // d, rate // d, axis=0, window=('kaiser', 12.0))
    return x


def excerpt(x, onset):
    # Preserve 50 ms before measured onset, four seconds of attack and decay.
    start = round((onset - .05) * FS)
    out = np.zeros((round(4.05 * FS), 2))
    lo, hi = max(0, start), min(len(x), start + len(out))
    out[lo-start:hi-start] = x[lo:hi]
    fade = round(.015 * FS)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out


def main():
    features = {}
    for name, path in [('real', 'reference_features.json'),
                       ('v1', 'baseline_report_features.json'),
                       ('v2', 'candidate_report_features.json')]:
        features[name] = {r['id']: r for r in json.loads((ROOT/'benchmark'/path).read_text())['samples']}
    sources = {'real': ROOT/'reference/wav', 'v1': ROOT/'benchmark/baseline', 'v2': ROOT/'benchmark/candidate'}
    out = ROOT/'listening'
    out.mkdir(exist_ok=True)
    clips, manifest = {}, []
    for ident in IDS:
        reference = features['real'][ident]
        row = {'id': ident, 'split': reference['split'], 'segments': []}
        pieces = []
        offset = 0
        for label in ['real', 'v1', 'v2']:
            feat = features[label][ident]
            path = sources[label]/(ident+'.wav')
            gain = reference['early_rms']/feat['early_rms']
            clip = excerpt(read(path), feat['onset_seconds'])*gain
            row['segments'].append({'label': label, 'start_seconds': offset,
                'end_seconds': offset+len(clip)/FS, 'source': str(path.relative_to(ROOT)),
                'source_sha256': file_hash(path), 'gain_db': float(20*np.log10(gain))})
            pieces.extend([clip, np.zeros((round(.55*FS), 2))])
            offset += len(clip)/FS+.55
        clips[ident] = np.concatenate(pieces[:-1])
        manifest.append(row)
    # One common presentation gain across every triplet. No limiting/compression.
    master = 10**(-2/20)/max(true_peak(x) for x in clips.values())
    for i, row in enumerate(manifest):
        name = row['id'].replace('#', 'sharp')+'-real-v1-v2'
        path = out/(name+'.wav')
        x = clips[row['id']]*master
        write_pcm24(path, x, 8025+i)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(path),
                        '-codec:a','libmp3lame','-b:a','320k',str(path.with_suffix('.mp3'))],check=True)
        row.update(file=path.name, mp3=path.with_suffix('.mp3').name,
                   sha256=file_hash(path), **measure(x))
    report = {'order': ['real', 'v1', 'v2'], 'sample_rate': FS, 'pcm_bits': 24,
        'level_matching': 'One 0.05–0.75s post-onset RMS scalar per model note, fixed through decay; one common final presentation gain.',
        'presentation_gain_db': float(20*np.log10(master)),
        'room_added': False, 'limiter': False, 'compressor': False,
        'attribution': 'Real recordings: Salamander Grand Piano V3, Alexander Holm, CC BY 3.0. Excerpted, onset-aligned, end-faded and concatenated for comparison. See reference/ATTRIBUTION.md.',
        'cases': manifest}
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'triplets':len(manifest),'presentation_gain_db':report['presentation_gain_db']},indent=2))


if __name__ == '__main__':
    main()
