#!/usr/bin/env python3
"""Export only three frozen TRAIN comparisons; never render, fit or open eval audio."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / 'out/full-calibration/v4/evaluation/freeze.json'
FREEZE_SHA = '100cf59663e203c58acfaa88c220d6cc270ee777437b5a7f5c974c205c24c105'
IDS = ('A0v4', 'C4v12', 'C8v12')
RATE, SECONDS, GAP_SECONDS, FADE_SECONDS = 48000, 3.5, .25, .020


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def decode(path, format):
    return subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', format, '-'],
                          check=True, stdout=subprocess.PIPE).stdout


def main():
    inputs = {}

    def guard(path, expected):
        path = Path(path).resolve()
        if sha(path) != expected:
            raise ValueError(f'Frozen input changed: {path}')
        if path in inputs and inputs[path] != expected:
            raise ValueError(f'Conflicting input identity: {path}')
        inputs[path] = expected
        return path

    guard(FREEZE, FREEZE_SHA)
    freeze = read(FREEZE)
    frozen = {Path(i['path']).resolve(): i['sha256'] for i in freeze['inputs']}

    def frozen_input(path):
        path = Path(path).resolve()
        return guard(path, frozen[path])

    fitter_path = frozen_input(ROOT / 'tools/fit_full_calibration.py')
    spec = importlib.util.spec_from_file_location('keyra_frozen_listening_fit', fitter_path)
    fit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fit)
    rows, _ = fit.training_inputs(fit.DEFAULT_REFERENCE, fit.DEFAULT_SPLIT)
    rows = {r['id']: r for r in rows}
    # The strict TRAIN inventory is checked before resolving any actual audio.
    if not set(IDS) <= rows.keys():
        raise ValueError('Requested listening case is outside locked TRAIN')
    producers = {}
    scores = {}
    for label, score_name in (('control', 'control'), ('candidate', 'final')):
        producer = freeze['producers'][label]
        for key in ('source', 'binary', 'header'):
            frozen_input(producer[key])
        manifest_path = frozen_input(producer['training_manifest']['path'])
        manifest = read(manifest_path)
        if (manifest.get('complete') is not True or manifest.get('errors') or
                manifest['rate'] != RATE or set(manifest['ids']) != set(rows) or
                len(manifest['renders']) != len(rows)):
            raise ValueError('Training render manifest is incomplete or inconsistent')
        for key, source in (('source_sha256', 'source'), ('engine_sha256', 'binary'),
                            ('calibration_sha256', 'header')):
            if manifest[key] != sha(producer[source]):
                raise ValueError(f'Producer/manifest mismatch: {label}/{key}')
        score_path = frozen_input(ROOT / f'out/full-calibration/v4/{score_name}-score/score.json')
        score = read(score_path)
        if set(score['training_ids']) != set(rows):
            raise ValueError('Score has a different TRAIN inventory')
        for item in score['provenance']['inputs']:
            guard(item['path'], item['sha256'])
        scores[label] = {c['id']: c for c in score['comparison']}
        producers[label] = (producer, manifest_path, manifest, score)

    prepared = []
    frames = round(RATE * SECONDS)
    fade_frames = round(RATE * FADE_SECONDS)
    fade = .5 + .5 * np.cos(np.linspace(0., np.pi, fade_frames))
    for identity in IDS:
        row = rows[identity]
        reference_path = Path(fit.reference_audio(row, fit.DEFAULT_REFERENCE)).resolve()
        receipt = fit.reference_audio_identity(row, reference_path)
        guard(reference_path, receipt['actual_wave_sha256'])
        segments, tracks = [], []
        for label in ('real', 'control', 'candidate'):
            gain_db, synthesis = 0., None
            if label == 'real':
                path = reference_path
            else:
                producer, manifest_path, manifest, score = producers[label]
                entry = next(r for r in manifest['renders'] if r['id'] == identity)
                comparison = scores[label][identity]
                path = manifest_path.parent / (identity + '.wav')
                guard(path, entry['output_sha256'][path.name])
                if sha(path) != comparison['model_sha256'] or comparison['split'] != 'train':
                    raise ValueError('Scored audio differs from frozen render')
                recorded_identity = next(i for i in score['reference_audio_identities'] if i['id'] == identity)
                if recorded_identity != receipt or comparison['reference_sha256'] != row['sha256']:
                    raise ValueError('Scored reference identity differs from strict PCM resolver')
                for key in ('source_sha256', 'engine_sha256', 'calibration_sha256'):
                    if entry['inputs'][key] != manifest[key]:
                        raise ValueError('Per-case synthesis identity differs from manifest')
                command = entry['inputs']['command']
                event_path = Path(command[command.index('--events') + 1])
                guard(event_path, entry['inputs']['score_sha256'])
                gain_db = comparison['early_gain_db']
                synthesis = {'source_sha256': manifest['source_sha256'],
                             'header_sha256': manifest['calibration_sha256'],
                             'binary_sha256': manifest['engine_sha256'],
                             'render_manifest_sha256': sha(manifest_path),
                             'events': {'path': str(event_path.relative_to(ROOT)),
                                        'sha256': sha(event_path), 'text': event_path.read_text()},
                             'recorded_command': command, 'metrics': entry['metrics']}
            sr, x = fit.benchmark.load_audio(path)
            if sr != RATE or x.shape[1] != 2:
                raise ValueError('Expected unchanged 48 kHz stereo input')
            onset, onset_detail = fit.benchmark.onset_index(x, sr)
            if label == 'real' and onset != round(row['onset_seconds'] * sr):
                raise ValueError('Reference onset differs from frozen feature measurement')
            if len(x) - onset < frames:
                raise ValueError('Requested common support would require padding')
            section = x[onset:onset + frames].copy() * 10 ** (gain_db / 20)
            section[-fade_frames:] *= fade[:, None]
            segments.append(section)
            tracks.append({'role': label, 'input': str(Path(path).relative_to(ROOT)),
                           'input_sha256': sha(path), 'input_frames': len(x),
                           'source_onset_frame': onset, 'source_onset_seconds': onset / RATE,
                           'onset_measurement': onset_detail,
                           'available_frames_after_onset': len(x) - onset,
                           'early_gain_db_from_frozen_score': gain_db,
                           'early_gain_linear': 10 ** (gain_db / 20),
                           'synthesis': synthesis})
        prepared.append((identity, receipt, segments, tracks))

    # One gain across all nine sections, preserving relative levels between notes.
    peak = max(float(np.max(np.abs(x))) for _, _, sections, _ in prepared for x in sections)
    common_gain = .8 / peak
    output_folder = ROOT / 'Audio/full-calibration-v4'
    output_folder.mkdir(parents=True, exist_ok=True)
    work = ROOT / 'out/full-calibration/v4/listening'
    work.mkdir(parents=True, exist_ok=True)
    entries = []
    gap = np.zeros((round(RATE * GAP_SECONDS), 2))
    for identity, receipt, sections, tracks in prepared:
        audio = np.concatenate([sections[0], gap, sections[1], gap, sections[2]]) * common_gain
        if not np.isfinite(audio).all() or np.max(np.abs(audio)) > .800001:
            raise ValueError('Invalid processed comparison')
        prefix = identity + '-real-control-candidate'
        wave_path, output_path = work / (prefix + '.wav'), output_folder / (prefix + '.flac')
        wavfile.write(wave_path, RATE, audio.astype(np.float32))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wave_path), '-c:a', 'flac',
                        '-sample_fmt', 's32', '-bits_per_raw_sample', '24', str(output_path)], check=True)
        pcm24 = decode(wave_path, 's24le')
        if pcm24 != decode(output_path, 's24le'):
            raise ValueError('FLAC does not reproduce expected 24-bit PCM conversion')
        flac_float = np.frombuffer(decode(output_path, 'f32le'), dtype='<f4').reshape(-1, 2)
        if flac_float.shape != audio.shape:
            raise ValueError('Decoded FLAC dimensions changed')
        error = float(np.max(np.abs(flac_float - audio.astype(np.float32))))
        if error > 2 ** -23:
            raise ValueError('Unexpected quantization/level error')
        for index, track in enumerate(tracks):
            track['output_start_frame'] = index * (frames + len(gap))
            track['output_start_seconds'] = track['output_start_frame'] / RATE
            track['output_frames'] = frames
        entries.append({'id': identity, 'split': 'train', 'reference_identity': receipt,
                        'file': output_path.name, 'sha256': sha(output_path),
                        'processed_float_wave_sha256': sha(wave_path),
                        'decoded_pcm24_sha256': hashlib.sha256(pcm24).hexdigest(),
                        'source_float_to_pcm24_maximum_quantization_error': error,
                        'frames': len(audio), 'duration_seconds': len(audio) / RATE,
                        'tracks': tracks})
    for path, expected in inputs.items():
        if sha(path) != expected:
            raise ValueError(f'Input changed during export: {path}')
    manifest = {'schema_version': 1, 'training_only': True, 'candidate_promoted': False,
                'evaluation_audio_opened_by_exporter': False, 'no_synthesis_or_fitting_run': True,
                'export_tool_sha256': sha(Path(__file__)), 'format': '24-bit FLAC, 48 kHz stereo',
                'order': ['real', 'original full control (hot float, original calibration)',
                          'v4 full candidate (hot float, TRAIN calibration)'],
                'seconds_per_section': SECONDS, 'gap_seconds': GAP_SECONDS,
                'alignment': 'Each source starts at its frozen benchmark onset; no time stretch, pitch shift or phase alignment.',
                'fade': {'where': 'last 20 ms of every section', 'shape': 'half cosine from 1 to 0',
                         'frames': fade_frames, 'attack_fade': False},
                'levels': {'model_gain': 'Exactly early_gain_db from corresponding frozen TRAIN score; reference gain 0 dB before common gain.',
                           'one_peak_gain_for_all_nine_sections': common_gain,
                           'peak_before_common_gain': peak, 'target_sample_peak': .8,
                           'independent_peak_normalization': False},
                'attribution': {'recordings': 'Salamander Grand Piano V3 by Alexander Holm',
                                'source': 'https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404',
                                'original_distribution': 'https://archive.org/details/SalamanderGrandPianoV3',
                                'license': 'Creative Commons Attribution 3.0 Unported',
                                'license_url': 'https://creativecommons.org/licenses/by/3.0/',
                                'modifications': 'Selected training recordings onset-trimmed, cropped to 3.5 s, final 20 ms faded, scaled by one common gain, concatenated with model comparisons and 0.25 s silence, converted to PCM24 FLAC. No resampling, EQ, denoising or added room.'},
                'limits': ['Training cases; no generalization or perceptual-parity claim.',
                           'Candidate NOT promoted: historical A3 envelope regression and unresolved strong C8 component.',
                           'Acquisition room and recording-chain properties remain in the real recordings; no room added to any track.',
                           'Layer4/12 MIDI proxies 40/93 are SFZ bin midpoints, not measured recording hammer velocities.',
                           'These single-note full-model renders do not include the separate repeated-strike or key/pedal mechanism adapters.',
                           'No realtime or Reason host qualification implied.'],
                'inputs': [{'path': str(p.relative_to(ROOT)), 'sha256': h} for p, h in inputs.items()],
                'entries': entries}
    (output_folder / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n')
    print(output_folder)


if __name__ == '__main__':
    main()
