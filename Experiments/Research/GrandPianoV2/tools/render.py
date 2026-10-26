#!/usr/bin/env python3
"""Build the physical model and render the five supplied performances.

Requirements: Python 3.10+, NumPy, SciPy, C++17 compiler; ffmpeg for MP3.
All synthesis is native C++; Python performs FIR decimation and presentation.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import wave

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, firwin, lfilter, resample_poly

ROOT = Path(__file__).resolve().parents[1]
FS = 48000
SOURCE_FIELDS = ('solver_source_sha256', 'calibration_sha256', 'model_source_sha256')


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def model_source_hash(source_sha, calibration_sha):
    """Stable digest of the named model inputs, independent of filesystem paths."""
    files = {'src/grand.cpp': source_sha, 'src/calibration.h': calibration_sha}
    return hashlib.sha256(json.dumps(files, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def source_provenance():
    source_sha = file_hash(ROOT / 'src/grand.cpp')
    calibration_sha = file_hash(ROOT / 'src/calibration.h')
    return {'solver_source_sha256': source_sha, 'calibration_sha256': calibration_sha,
            'model_source_sha256': model_source_hash(source_sha, calibration_sha)}


def score_path(item):
    return ROOT / 'scores' / item['events']


def raw_paths(item):
    base = ROOT / 'build/raw' / item['id']
    return base.with_suffix('.wav'), base.with_suffix('.provenance.json')


def raw_provenance(item, require_verified=False):
    """Verify cached bytes against a recorded synthesis or registered origin.

    Missing sidecars are allowed only for ordinary cached exports, and never
    imply that the current source or score generated the cached audio.
    """
    raw, sidecar = raw_paths(item)
    if not raw.is_file():
        raise ValueError(f'Missing cached raw audio for {item["id"]}; render without --post-only first')
    raw_sha = file_hash(raw)
    events_sha = file_hash(score_path(item))
    if not sidecar.is_file():
        if require_verified:
            raise ValueError(f'Custom --post-only requires matching synthesis provenance for {item["id"]}; render without --post-only first')
        return {'id': item['id'], 'status': 'unverified',
                'origin': 'cached raw audio without a synthesis provenance sidecar',
                **dict.fromkeys(SOURCE_FIELDS), 'events_sha256': None,
                'binary_sha256': None, 'raw_sha256': raw_sha,
                'current_events_sha256': events_sha}
    try:
        record = json.loads(sidecar.read_text())
    except (OSError, ValueError) as exc:
        raise ValueError(f'Cannot read cached synthesis provenance for {item["id"]}: {exc}') from exc
    fields = SOURCE_FIELDS + ('events_sha256', 'binary_sha256', 'raw_sha256')
    if (not isinstance(record, dict) or record.get('schema_version') != 2
            or not isinstance(record.get('origin'), str) or not record['origin']
            or any(not isinstance(record.get(key), str)
                   or not re.fullmatch(r'[0-9a-f]{64}', record[key]) for key in fields)
            or record.get('input_sample_rate') not in (48000, 96000, 192000, 384000)
            or not isinstance(record.get('tail_seconds'), (int, float))
            or not math.isfinite(record['tail_seconds']) or not 0 <= record['tail_seconds'] <= 60):
        raise ValueError(f'Invalid cached synthesis provenance for {item["id"]}; rerender the performance')
    if record['model_source_sha256'] != model_source_hash(record['solver_source_sha256'], record['calibration_sha256']):
        raise ValueError(f'Inconsistent model source hashes for {item["id"]}; rerender the performance')
    current_sources = source_provenance()
    if any(record[key] != current_sources[key] for key in SOURCE_FIELDS):
        raise ValueError(f'Cached model source or calibration hash mismatch for {item["id"]}; rerender without --post-only')
    if record['raw_sha256'] != raw_sha:
        raise ValueError(f'Cached raw audio hash mismatch for {item["id"]}; rerender the performance')
    if record['events_sha256'] != events_sha:
        raise ValueError(f'Cached score hash mismatch for {item["id"]}; the current performance was not synthesized; rerender without --post-only')
    rate, _ = wavfile.read(raw, mmap=True)
    if rate != record['input_sample_rate']:
        raise ValueError(f'Cached sample rate disagrees with synthesis provenance for {item["id"]}')
    return dict(record, id=item['id'], status='verified')


def compile_engine():
    (ROOT / 'build').mkdir(exist_ok=True)
    provenance = ROOT / 'build/grand.provenance.json'
    provenance.unlink(missing_ok=True)
    sources = source_provenance()
    compiler = os.environ.get('CXX', 'clang++')
    subprocess.run([compiler, '-std=c++17', '-O3', '-march=native',
                    '-Wall', '-Wextra', '-Wpedantic', 'src/grand.cpp',
                    '-o', 'build/grand'], cwd=ROOT, check=True)
    if source_provenance() != sources:
        raise ValueError('Model source or calibration changed during compilation; rerun the renderer')
    provenance.write_text(json.dumps({'schema_version': 2, **sources,
                                     'binary_sha256': file_hash(ROOT / 'build/grand')}, indent=2)+'\n')


def synthesize(item, rate, tail):
    name = item['id']
    raw, sidecar = raw_paths(item)
    events = score_path(item)
    snapshot = {'schema_version': 2, 'origin': 'captured-during-synthesis',
                **source_provenance(),
                'events_sha256': file_hash(events),
                'binary_sha256': file_hash(ROOT / 'build/grand'),
                'input_sample_rate': rate, 'tail_seconds': tail}
    try:
        compiled = json.loads((ROOT / 'build/grand.provenance.json').read_text())
    except (OSError, ValueError) as exc:
        raise ValueError('Missing engine build provenance; rebuild with the renderer before synthesis') from exc
    if (not isinstance(compiled, dict) or compiled.get('schema_version') != 2
            or any(compiled.get(key) != snapshot[key] for key in SOURCE_FIELDS + ('binary_sha256',))):
        raise ValueError('Engine source, calibration, or binary changed after compilation; rebuild with the renderer')
    # A failed or interrupted render must not leave old metadata attached to new
    # or partially written audio.
    sidecar.unlink(missing_ok=True)
    command = [str(ROOT / 'build/grand'), '--events',
               str(events), '--output', str(raw),
               '--sample-rate', str(rate), '--tail', str(tail),
               '--metrics', str(ROOT / 'renders/metrics' / (name + '-engine.json'))]
    if name == '01_nocturne': command += ['--dump-model', str(ROOT / 'model.json')]
    print('Synthesizing', name, flush=True)
    subprocess.run(command, check=True)
    for key, path in [('solver_source_sha256', ROOT / 'src/grand.cpp'),
                      ('calibration_sha256', ROOT / 'src/calibration.h'),
                      ('events_sha256', events), ('binary_sha256', ROOT / 'build/grand')]:
        if file_hash(path) != snapshot[key]:
            raise ValueError(f'Synthesis input changed during rendering of {name}; cached audio remains unverified; rerender')
    snapshot['raw_sha256'] = file_hash(raw)
    temporary = sidecar.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(snapshot, indent=2)+'\n')
    temporary.replace(sidecar)


def downsample(path):
    rate, x = wavfile.read(path)
    if x.dtype != np.float32 or x.ndim != 2 or x.shape[1] != 2:
        raise ValueError(f'Expected raw stereo float32: {path}')
    if not len(x) or not np.isfinite(x).all():
        raise ValueError(f'Empty or nonfinite cached raw audio: {path}')
    if rate % FS: raise ValueError('Solver rate must be a multiple of 48000')
    factor = rate // FS
    if factor == 1: return x.astype(np.float64)
    # Symmetric odd FIR, >100dB rejection; polyphase implementation compensates
    # filter delay and keeps the supplied event times aligned with the output.
    fir = firwin(256 * factor + 1, 22500, fs=rate, window=('kaiser', 12.0))
    return resample_poly(x.astype(np.float64), 1, factor, axis=0,
                         window=fir, padtype='constant')


def room_ir(seconds=1.8):
    """Procedural room: image-source early paths plus a damped diffuse tail.

    No acoustic recording or piano response is used. This is presentation,
    independently bypassable from the mechanical model.
    """
    size = int(seconds * FS)
    ir = np.zeros((size, 2), np.float64)
    dimensions = np.array([7.2, 5.6, 3.2])
    source = np.array([2.4, 2.7, 1.05])
    for ch, mic in enumerate([np.array([3.30, 1.8, 1.4]),
                              np.array([3.65, 1.8, 1.4])]):
        direct = np.linalg.norm(source - mic)
        for tiles in itertools.product(range(-2, 3), repeat=3):
            for signs in itertools.product((1, -1), repeat=3):
                order = sum(abs(2*m-(s == -1)) for m, s in zip(tiles, signs))
                if not 1 <= order <= 4: continue
                image = 2 * np.array(tiles) * dimensions + np.array(signs) * source
                distance = np.linalg.norm(image - mic)
                pos = ((distance - direct) / 343.0 + .006) * FS
                tap = int(pos)
                gain = .63 ** order * direct / distance
                if tap < 0 or tap + 64 >= size: continue
                # Air/wall absorption; fractional-sample arrival by linear split.
                pole = math.exp(-2*math.pi*(9500/(1+.35*order))/FS)
                kernel = (1-pole) * pole ** np.arange(64)
                frac = pos - tap
                ir[tap:tap+64, ch] += gain*(1-frac)*kernel
                ir[tap+1:tap+65, ch] += gain*frac*kernel
        rng = np.random.default_rng(4250 + ch)
        t = np.arange(size)/FS
        noise = rng.standard_normal(size)
        low = lfilter([.07], [1, -.93], noise)
        high = noise - low
        onset = np.clip((t-.034)/.024, 0, 1)
        diffuse = onset * (low*np.exp(-math.log(1000)*t/1.45)
                           + .12*high*np.exp(-math.log(1000)*t/.80))
        diffuse *= .28 / max(np.linalg.norm(diffuse), 1e-20)
        ir[:, ch] += diffuse
    ir *= 1.1 / math.sqrt(float(np.mean(np.sum(ir*ir, axis=0))))
    return ir


def presentation(x, impulse, wet):
    mid = x.mean(axis=1)
    reflections = np.stack([fftconvolve(mid, impulse[:, ch])[:len(x)]
                            for ch in range(2)], axis=1)
    return x + wet * reflections


def true_peak(x):
    # Four-times oversampling with a long reconstruction filter, evaluated in
    # pieces to keep memory bounded. These are numerical intersample estimates.
    peak = 0.0
    for start in range(0, len(x), FS*8):
        region = x[max(0, start-128):min(len(x), start+FS*8+128)]
        up = resample_poly(region, 4, 1, axis=0, window=('kaiser', 12.0))
        peak = max(peak, float(np.max(np.abs(up))))
    return peak


def write_pcm24(path, x, seed):
    if not np.isfinite(x).all() or np.max(np.abs(x)) >= 1:
        raise ValueError(f'Nonfinite or clipping audio: {path}')
    rng = np.random.default_rng(seed)
    scale = 8388608
    dither = rng.random(x.shape) - rng.random(x.shape)
    samples = np.rint(x*scale + dither).astype('<i4')
    if samples.min() < -8388608 or samples.max() > 8388607:
        raise ValueError('PCM24 overflow')
    data = samples.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(3); f.setframerate(FS)
        f.writeframes(data)


def measure(x):
    sample_peak = float(np.max(np.abs(x)))
    correlation = float(np.corrcoef(x.T)[0, 1]) if np.all(np.std(x, axis=0) > 0) else None
    return {'sample_peak_dbfs': 20*math.log10(max(sample_peak, 1e-30)),
            'estimated_true_peak_dbtp': 20*math.log10(max(true_peak(x), 1e-30)),
            'whole_file_rms_dbfs': 10*math.log10(max(float(np.mean(x*x)), 1e-30)),
            'duration_seconds': len(x)/FS,
            'stereo_correlation': correlation,
            'nonfinite_samples': int(np.count_nonzero(~np.isfinite(x)))}


def finish(items, wet, report_name='export.json', require_provenance=False):
    if not items:
        raise ValueError('No performances selected for export')
    provenance = [raw_provenance(item, require_provenance) for item in items]
    impulse = room_ir()
    prepared = []
    peak = 0.0
    for item in items:
        name = item['id']
        dry = downsample(ROOT / 'build/raw' / (name+'.wav'))
        room = presentation(dry, impulse, wet)
        if not np.isfinite(room).all():
            raise ValueError(f'Nonfinite room output for {name}')
        # Fade only the final 50ms of the requested tail (seven seconds by
        # default). Short custom tails deliberately truncate the natural decay.
        fade = min(len(dry), int(.05*FS))
        taper = np.linspace(1, 0, fade)**2
        dry[-fade:] *= taper[:, None]; room[-fade:] *= taper[:, None]
        for version, x in [('dry', dry), ('room', room)]:
            path = ROOT / 'build' / (name+'-'+version+'.npy')
            np.save(path, x.astype(np.float32))
            peak = max(peak, true_peak(x))
            prepared.append((item, version, path))
    # One album gain preserves absolute dynamics across all five performances.
    # No compressor, limiter, saturation, per-note leveling or per-song boost.
    if not math.isfinite(peak) or peak <= 0:
        raise ValueError('No audible piano notes in the selected performances; check MIDI channels, note range, and score events')
    gain = 10**(-1.5/20)/peak
    reports = []
    for item, version, intermediate in prepared:
        name = item['id']+'-'+version
        audio = np.load(intermediate).astype(np.float64)*gain
        output = ROOT / 'renders' / (name+'.wav')
        write_pcm24(output, audio, seed=1700+len(reports))
        stats = measure(audio)
        stats.update(id=item['id'], title=item['title'], version=version,
                     wav=output.name, gain_db=20*math.log10(gain),
                     room_send=wet if version == 'room' else 0,
                     sha256=hashlib.sha256(output.read_bytes()).hexdigest())
        if version == 'room' and shutil.which('ffmpeg'):
            mp3 = output.with_suffix('.mp3')
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                            '-i', str(output), '-codec:a', 'libmp3lame', '-b:a',
                            '320k', str(mp3)], check=True)
            stats['mp3'] = mp3.name
        print('Exported', output.name, f"{stats['estimated_true_peak_dbtp']:.2f} dBTP", flush=True)
        reports.append(stats)
    verified = all(item['status'] == 'verified' for item in provenance)
    sources = {}
    for key in SOURCE_FIELDS:
        hashes = {item[key] for item in provenance}
        sources[key] = next(iter(hashes)) if verified and len(hashes) == 1 else None
    current_sources = source_provenance()
    report = {**sources,
              'current_source_sha256': current_sources['solver_source_sha256'],
              'current_calibration_sha256': current_sources['calibration_sha256'],
              'current_model_source_sha256': current_sources['model_source_sha256'],
              'raw_provenance_status': 'verified-sidecar-hashes' if verified else 'includes-unverified-cached-audio',
              'raw_provenance': provenance,
              'output_rate': FS, 'pcm_bits': 24, 'dither': 'deterministic TPDF, one 24-bit LSB',
              'gain_db': 20*math.log10(gain), 'gain_policy': 'one gain for all excerpts and dry/room variants',
              'room': 'procedural image-source early paths + frequency-damped stochastic diffuse tail',
              'room_send': wet, 'compressor': False, 'limiter': False,
              'decimation': 'Kaiser beta=12 FIR; taps=256*(input_rate/48000)+1, cutoff 22.5kHz; polyphase downsampling (bypassed at 48k)',
              'files': reports}
    (ROOT/'renders/metrics'/report_name).write_text(json.dumps(report, indent=2)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--internal-rate', type=int, choices=[48000, 96000, 192000, 384000], default=192000)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--tail', type=float, default=7)
    parser.add_argument('--room-send', type=float, default=.16)
    parser.add_argument('--post-only', action='store_true', help='Use already rendered build/raw files')
    parser.add_argument('--ids', nargs='*', help='Optional score IDs to render/export')
    custom = parser.add_mutually_exclusive_group()
    custom.add_argument('--events', type=Path, help='Render another timed event score')
    custom.add_argument('--midi', type=Path, help='Import and render a standard MIDI file')
    parser.add_argument('--name', default='custom', help='Output ID for a custom performance')
    args = parser.parse_args()
    if args.jobs < 1 or not 0 <= args.room_send <= 1 or not 0 <= args.tail <= 60:
        parser.error('Invalid jobs, room send, or tail')
    for directory in ['build/raw', 'renders/metrics']:
        (ROOT/directory).mkdir(parents=True, exist_ok=True)
    items = json.loads((ROOT/'scores/manifest.json').read_text())
    if args.events or args.midi:
        if args.ids or not re.fullmatch(r'[A-Za-z0-9_-]+', args.name):
            parser.error('Custom performances need a plain output name and no --ids')
        events = args.events.resolve() if args.events else ROOT/'build'/(args.name+'.events')
        if args.midi:
            subprocess.run([sys.executable, str(ROOT/'tools/midi_to_events.py'),
                            str(args.midi.resolve()), str(events)], check=True)
        items = [{'id': args.name, 'title': (args.midi or args.events).stem,
                  'events': str(events)}]
    if args.ids:
        items = [item for item in items if item['id'] in args.ids]
        if len(args.ids) != len(set(args.ids)) or len(items) != len(args.ids): parser.error('Unknown or repeated score ID')
    if not args.post_only:
        compile_engine()
        subprocess.run([str(ROOT/'build/grand'), '--self-test'], check=True)
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            list(executor.map(lambda item: synthesize(item, args.internal_rate, args.tail), items))
    finish(items, args.room_send,
           'export-'+args.name+'.json' if args.events or args.midi else 'export.json',
           require_provenance=bool(args.post_only and (args.events or args.midi)))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f'Render failed: {exc}')
