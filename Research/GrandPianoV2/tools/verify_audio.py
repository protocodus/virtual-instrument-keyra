#!/usr/bin/env python3
"""Verify delivered PCM masters and decoded MP3 previews, including hash links."""
import hashlib
import json
from pathlib import Path
import subprocess
import wave

import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    exports = json.loads((ROOT/'renders/metrics/export.json').read_text())
    listening = json.loads((ROOT/'listening/manifest.json').read_text())
    records = []
    groups = [(ROOT/'renders', exports['files']), (ROOT/'listening', listening['cases'])]
    for folder, entries in groups:
        for entry in entries:
            path = folder/entry.get('wav', entry.get('file'))
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
            with wave.open(str(path)) as w:
                assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (2, 3, 48000), path
            fs, pcm = wavfile.read(path)
            x = pcm.astype(np.float64)/2147483648
            assert np.isfinite(x).all() and 0 < np.max(np.abs(x)) < 1, path
            row = {'file': str(path.relative_to(ROOT)), 'sha256_matches': True,
                   'duration_seconds': len(x)/fs, 'peak_dbfs': float(20*np.log10(np.max(np.abs(x)))),
                   'format': '48 kHz stereo PCM24', 'finite': True}
            if entry.get('mp3'):
                mp3 = folder/entry['mp3']
                probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0',
                    '-show_entries','stream=sample_rate,channels','-of','json',str(mp3)]))['streams'][0]
                assert int(probe['sample_rate']) == 48000 and probe['channels'] == 2, mp3
                raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(mp3),'-f','f32le','-'])
                decoded = np.frombuffer(raw,dtype='<f4').reshape(-1,2)
                assert np.isfinite(decoded).all() and 0 < np.max(np.abs(decoded)) < 1, mp3
                assert abs(len(decoded)-len(x))/fs < .05, mp3
                row['mp3'] = {'file': mp3.name, 'sha256': hashlib.sha256(mp3.read_bytes()).hexdigest(),
                    'finite': True, 'decoded_sample_peak_dbfs': float(20*np.log10(np.max(np.abs(decoded)))),
                    'duration_difference_seconds': (len(decoded)-len(x))/fs}
            records.append(row)
    result = {'passed': True, 'wav_files': len(records),
              'mp3_files': sum('mp3' in r for r in records), 'files': records,
              'scope': 'Container, checksum, finite-value and sample-headroom checks; no perceptual evaluation.'}
    (ROOT/'validation/delivered-audio.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))


if __name__ == '__main__':
    main()
