"""Synthetic exact lossless-AIFF/cropped-WAV contracts; no library recordings."""
from pathlib import Path
import argparse
import copy
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from scipy.io import wavfile

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE/'Tools'))
import update_modal_measurements as u
import measurement_source_provenance as s
p = argparse.ArgumentParser(add_help=False)
p.add_argument('--decoder-dir', type=Path, required=True)
C, rest = p.parse_known_args()
C.decoder_dir = C.decoder_dir.absolute()
sys.argv = [sys.argv[0]] + rest

class SourceContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ref = lambda path: {'path': str(path), 'sha256': u.digest(path)}

    def convert(self, source, dest, codec):
        subprocess.run([s.executable('ffmpeg'),'-v','error','-nostdin','-i',str(source),'-map_metadata','-1','-c:a',codec,str(dest)],check=True)

    def fixture(self, model='newyork', bits=16, mono=False, rate=None):
        sr = rate or (44100 if model=='newyork' else 48000)
        frames = 128
        x = np.column_stack([np.arange(frames)*137-9000, np.arange(frames)[::-1]*83-5000]).astype(np.int16)
        if mono: x = x[:,0]
        if model=='newyork':
            if bits==24: x=x.astype(np.int32)*65536
            initial=self.root/'input.wav'; original=self.root/'source.aif'; analysis=self.root/'n1.wav'
            wavfile.write(initial,sr,x);self.convert(initial,original,'pcm_s'+str(bits)+'be');self.convert(original,analysis,'pcm_s'+str(bits)+'le')
            field='aif_sha256';kind='newyork-aiff-lossless-v1';span=[0,frames];analysis_bits=bits
        else:
            x=x.astype(np.int32)*65536
            initial=self.root/'input.wav';original=self.root/'source.wav';analysis=self.root/'n1.wav'
            wavfile.write(initial,sr,x);self.convert(initial,original,'pcm_s24le')
            _,samples=wavfile.read(original);wavfile.write(analysis,sr,samples[10:])
            field='wav_sha256';kind='hamburg-preset-crop-v1';span=[10,frames];bits=24;analysis_bits=32
        item={'id':'n1','kind':'note','midi':60,'source':original.name,field:u.digest(original)}
        if model=='hamburg':item['start']=10+round(.02*48000)
        q={'id':'n1','velocity':64,'wav':self.ref(analysis),'provenance':{'kind':kind,
           'historical_cache_pin':item.get('wav_sha256'),'original':self.ref(original),
           'decoder':self.ref(C.decoder_dir/f'decode_{model}.py'),'sample_rate':44100 if model=='newyork' else 48000,
           'channels':2,'source_bits':bits,'analysis_bits':analysis_bits,'frame_span':span}}
        return model,item,q

    def prepare(self, fixture):
        model,item,q=fixture
        return s.prepare(item,q,model,self.root,{},u.pinned)

    def test_aiff16_lossless(self):
        r=s.verify(self.prepare(self.fixture()))
        self.assertTrue(r['exact_pcm_identity']);self.assertIsNone(r['historical_cache_pin'])

    def test_explicit_decoder_paths_work_without_path_discovery(self):
        tools = {name: s.executable(name) for name in ('ffmpeg', 'ffprobe')}
        environment = {'KEYRA_MODEL_' + name.upper(): path for name, path in tools.items()}
        environment['PATH'] = ''
        # Exercise fixture encoding, format probing, streaming PCM decoding
        # and runtime identity with the same exact overrides CMake supplies.
        with patch.dict(os.environ, environment):
            self.assertTrue(s.verify(self.prepare(self.fixture()))['exact_pcm_identity'])
            runtime = s.runtime()
        for name, path in tools.items():
            self.assertEqual(runtime[name]['path'], path)
            self.assertEqual(runtime[name]['sha256'], u.digest(path))
            self.assertTrue(runtime[name]['version'].startswith(name + ' version'))

    def test_aiff24_lossless(self):
        self.assertTrue(s.verify(self.prepare(self.fixture(bits=24)))['exact_pcm_identity'])

    def test_crop24_to32_lossless(self):
        r=s.verify(self.prepare(self.fixture('hamburg')))
        self.assertEqual(r['analysis_pcm']['frames'],118)

    def test_wrong_original_hash(self):
        f=self.fixture();f[2]['provenance']['original']['sha256']='0'*64
        with self.assertRaisesRegex(u.InvalidInput,'hash mismatch'):self.prepare(f)

    def test_wrong_authored_hash(self):
        f=self.fixture();f[2]['wav']['sha256']='0'*64
        with self.assertRaisesRegex(u.InvalidInput,'hash mismatch'):self.prepare(f)

    def test_original_must_match_authoritative_corpus(self):
        f=self.fixture();f[1]['aif_sha256']='0'*64
        with self.assertRaisesRegex(s.ProvenanceError,'original source differs'):self.prepare(f)

    def test_analysis_frame_count_exact(self):
        f=self.fixture();path=Path(f[2]['wav']['path']);sr,x=wavfile.read(path);wavfile.write(path,sr,x[:-1]);f[2]['wav']=self.ref(path)
        with self.assertRaisesRegex(s.ProvenanceError,'frame count differs'):s.verify(self.prepare(f))

    def test_wrong_sample_rate(self):
        r=self.prepare(self.fixture(rate=48000))
        with self.assertRaisesRegex(s.ProvenanceError,'sample rate mismatch'):s.verify(r)

    def test_wrong_channels(self):
        r=self.prepare(self.fixture(mono=True))
        with self.assertRaisesRegex(s.ProvenanceError,'channel mismatch'):s.verify(r)

    def test_wrong_crop_begin(self):
        f=self.fixture('hamburg');f[2]['provenance']['frame_span'][0]=11
        with self.assertRaisesRegex(s.ProvenanceError,'crop does not match'):self.prepare(f)

    def test_negative_frame_span(self):
        f=self.fixture();f[2]['provenance']['frame_span'][0]=-1
        with self.assertRaisesRegex(s.ProvenanceError,'invalid frame span'):self.prepare(f)

    def test_end_outside_original(self):
        f=self.fixture('hamburg');f[2]['provenance']['frame_span'][1]+=1
        with self.assertRaisesRegex(s.ProvenanceError,'original final frame'):s.verify(self.prepare(f))

    def test_truncated_declared_tail(self):
        f=self.fixture('hamburg');f[2]['provenance']['frame_span'][1]-=1
        with self.assertRaisesRegex(s.ProvenanceError,'original final frame'):s.verify(self.prepare(f))

    def test_same_format_wrong_pcm(self):
        f=self.fixture();path=Path(f[2]['wav']['path']);sr,x=wavfile.read(path);x[17,1]+=1;wavfile.write(path,sr,x)
        f[2]['wav']=self.ref(path)
        with self.assertRaisesRegex(s.ProvenanceError,'decoded PCM differs'):s.verify(self.prepare(f))

    def test_relabelled_historical_cache_pin(self):
        f=self.fixture();f[2]['provenance']['historical_cache_pin']=f[2]['wav']['sha256']
        with self.assertRaisesRegex(s.ProvenanceError,'historical cache pin differs'):self.prepare(f)

    def test_wrong_decoder_version(self):
        f=self.fixture();path=self.root/'decoder.py';path.write_text('# different recipe\n');f[2]['provenance']['decoder']=self.ref(path)
        with self.assertRaisesRegex(s.ProvenanceError,'implementation not supported'):self.prepare(f)

    def test_declared_gain_or_channel_map_rejected(self):
        f=self.fixture();f[2]['provenance']['gain']=1
        with self.assertRaisesRegex(s.ProvenanceError,'transform fields differ'):self.prepare(f)

if __name__=='__main__': unittest.main(verbosity=2)
