"""Boundary, identity and split invariants for the native PCM corpus importer."""
import hashlib
import importlib.util
import concurrent.futures
import errno
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import wave

SCRIPT = Path(__file__).resolve().parents[1] / 'Tools/decode_yamaha_c3.py'
SPEC = importlib.util.spec_from_file_location('decode_yamaha_c3', SCRIPT)
yamaha = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(yamaha)


class YamahaImportTests(unittest.TestCase):
    def test_concurrent_wav_and_metadata_publication(self):
        # Hold both publishers just before rename: both temporary files must
        # still exist independently after either one has been published.
        original_replace = Path.replace
        barrier = threading.Barrier(2)
        temporary_names = []
        def publish(source, target):
            # A Windows sharing retry belongs to the same publisher; only its
            # first attempt rendezvouses with the other complete temporary.
            if source.name not in temporary_names:
                temporary_names.append(source.name)
                barrier.wait(timeout=5)
            return original_replace(source, target)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pcm = bytes((0, 0, 128, 255, 255, 127)) * 1024
            params = wave._wave_params(2, 3, 48000, 1024, 'NONE', 'not compressed')
            output = root/'region.wav'
            with patch.object(Path, 'replace', publish), concurrent.futures.ThreadPoolExecutor(2) as workers:
                futures = [workers.submit(yamaha.write_or_verify_wav, output, pcm, params) for _ in range(2)]
                hashes = [future.result(timeout=10) for future in futures]
            self.assertEqual(hashes, [yamaha.wav_sha256(pcm, params)] * 2)
            self.assertEqual(len(set(temporary_names)), 2)
            self.assertEqual(list(root.glob('*.part.wav')), [])
            temporary_names.clear()
            metadata = root/'metadata.json'
            value = {'frames': 1024, 'pcm_sha256': hashlib.sha256(pcm).hexdigest()}
            with patch.object(Path, 'replace', publish), concurrent.futures.ThreadPoolExecutor(2) as workers:
                futures = [workers.submit(yamaha.write_json, metadata, value) for _ in range(2)]
                for future in futures:
                    future.result(timeout=10)
            self.assertEqual(json.loads(metadata.read_text()), value)
            self.assertEqual(len(set(temporary_names)), 2)
            self.assertEqual(list(root.glob('*.part.json')), [])

    def test_transient_windows_read_handle_contention_retries_atomic_publication(self):
        original_replace = Path.replace
        for winerror in (5, 32):
            for kind in ('wav', 'json'):
                with self.subTest(winerror=winerror, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    output = root/('region.'+kind)
                    attempts = []
                    def publish(source, target):
                        attempts.append(source)
                        if len(attempts) <= 2:
                            # Another publisher won the initial creation; a
                            # verifier holds that complete destination briefly.
                            if not target.exists():
                                target.write_bytes(source.read_bytes())
                            error = PermissionError(errno.EACCES, 'reader denies replacement')
                            error.winerror = winerror
                            raise error
                        return original_replace(source, target)
                    with patch.object(Path, 'replace', publish), patch.object(yamaha.time, 'sleep') as sleep:
                        if kind == 'wav':
                            pcm = bytes((0, 0, 128, 255, 255, 127))*4
                            params = wave._wave_params(2, 3, 48000, 4, 'NONE', 'not compressed')
                            self.assertEqual(yamaha.write_or_verify_wav(output, pcm, params),
                                             yamaha.wav_sha256(pcm, params))
                            with wave.open(str(output), 'rb') as reader:
                                self.assertEqual(reader.readframes(4), pcm)
                        else:
                            yamaha.write_json(output, {'complete': True})
                            self.assertEqual(json.loads(output.read_text()), {'complete': True})
                    self.assertEqual(len(attempts), 3)
                    self.assertEqual(len(set(attempts)), 1)
                    self.assertEqual(sleep.call_count, 2)
                    self.assertEqual(list(root.glob('*.part.*')), [])

    def test_publication_retry_is_bounded_and_does_not_hide_other_errors(self):
        for winerror, exists in [(5, True), (32, True), (None, True), (5, False)]:
            with self.subTest(winerror=winerror, exists=exists), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output = root/'metadata.json'
                if exists:
                    output.write_text('{"old": true}')
                error = PermissionError(errno.EACCES, 'denied')
                if winerror is not None:
                    error.winerror = winerror
                with patch.object(Path, 'replace', side_effect=error) as replace, \
                        patch.object(yamaha.time, 'sleep') as sleep, self.assertRaises(PermissionError):
                    yamaha.write_json(output, {'new': True})
                retries = len(yamaha._REPLACE_RETRY_DELAYS) if winerror in (5, 32) and exists else 0
                self.assertEqual(replace.call_count, retries+1)
                self.assertEqual(sleep.call_count, retries)
                self.assertLessEqual(sum(call.args[0] for call in sleep.call_args_list), 1.)
                self.assertEqual(list(root.glob('*.part.*')), [])
                if exists:
                    self.assertEqual(json.loads(output.read_text()), {'old': True})
                else:
                    self.assertFalse(output.exists())

    def test_inclusive_boundaries_preserve_stereo_pcm24(self):
        # Non-normalized bytes include both channel payloads and signed extremes.
        frames = [bytes((0, 0, 128, 255, 255, 127)), bytes((1, 2, 3, 4, 5, 6)),
                  bytes((255, 255, 255, 0, 0, 0)), bytes((9, 8, 7, 6, 5, 4))]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.wav'
            output = Path(directory) / 'region.wav'
            with wave.open(str(source), 'wb') as writer:
                writer.setparams((2, 3, 48000, 0, 'NONE', 'not compressed'))
                writer.writeframes(b''.join(frames))
            with wave.open(str(source), 'rb') as reader:
                pcm = yamaha.read_region(reader, 1, 3)
                self.assertEqual(pcm, b''.join(frames[1:]))
                digest = yamaha.write_or_verify_wav(output, pcm, reader.getparams())
                self.assertEqual(digest, yamaha.sha256(output))
                self.assertEqual(digest, yamaha.wav_sha256(pcm, reader.getparams()))
                self.assertEqual(yamaha.write_or_verify_wav(output, pcm, reader.getparams()), digest)
                self.assertEqual(yamaha.read_region(reader, 3, 3), frames[3])
                with self.assertRaises(ValueError):
                    yamaha.read_region(reader, 0, 4)
                with self.assertRaises(ValueError):
                    yamaha.write_or_verify_wav(output, bytes(len(pcm)), reader.getparams())
            with source.open('rb') as stream:
                hashed = yamaha.ForwardHashReader(stream)
                with wave.open(hashed, 'rb') as reader:
                    self.assertEqual(yamaha.read_region(reader, 1, 1), frames[1])
                    self.assertEqual(yamaha.read_region(reader, 3, 3), frames[3])
                self.assertEqual(hashed.finish(), yamaha.sha256(source))

    def test_repeated_mapping_is_one_region_with_all_aliases(self):
        sample = ('<sample path="samples/Monolith.wav" rootNote="60" loNote="59" hiNote="61" '
                  'loVel="110" hiVel="127" start="2" end="5" seqPosition="{}"/>')
        preset = ('<DecentSampler><groups><group name="MIC1 F notes_with_pedal" loCC64="64" '
                  'hiCC64="127">' + ''.join(sample.format(position) for position in (1, 2, 3))
                  + '</group></groups></DecentSampler>').encode()
        items = yamaha.inventory(preset)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['frames'], 4)
        self.assertEqual(items[0]['sequence_positions'], [1, 2, 3])
        self.assertEqual(len(items[0]['mappings']), 3)
        self.assertEqual(items[0]['cc64'], [64, 127])
        self.assertEqual(items[0]['velocity'], [110, 127])
        conflict = preset.replace(b'rootNote="60"', b'rootNote="61"', 1)
        with self.assertRaises(ValueError):
            yamaha.inventory(conflict)

    def test_all_conditions_share_pitch_role_and_duplicates_cannot_leak(self):
        items = [{'id': f'{pitch}-{condition}', 'midi': pitch,
                  'pcm_sha256': hashlib.sha256(f'{pitch}-{condition}'.encode()).hexdigest()}
                 for pitch in range(21, 109, 3) for condition in ('up', 'down', 'release', 'second')]
        roles = yamaha.pitch_roles(items)
        self.assertEqual([pitch for pitch, role in roles.items() if role == 'dev'],
                         [27, 42, 57, 72, 87, 102])
        self.assertEqual(roles, yamaha.pitch_roles(list(reversed(items))))
        split = yamaha.build_split(items, roles)
        self.assertEqual(set(split['cases'].values()), {'train', 'dev'})
        for item in items:
            self.assertEqual(split['cases'][item['id']], roles[item['midi']])
        # Same-role exact duplicates are allowed, but cannot cross the boundary.
        items[1]['pcm_sha256'] = items[0]['pcm_sha256']
        yamaha.assert_no_duplicate_leakage(items, roles)
        self.assertEqual(len(yamaha.build_split(items, roles)['duplicate_cases']), 1)
        next(item for item in items if item['midi'] == 27)['pcm_sha256'] = items[0]['pcm_sha256']
        with self.assertRaises(ValueError):
            yamaha.build_split(items, roles)


if __name__ == '__main__':
    unittest.main()
