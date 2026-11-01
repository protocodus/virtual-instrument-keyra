"""Independent numerical operator and coverage checks for quality_audit.py.

Uses synthetic stereo signals only. Compiles the observation-only C++ path;
no instrument is rendered and no source recording is read. Run directly with
python3 Tests/test_quality_audit.py (NumPy required).
"""
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('quality',ROOT/'Tools/quality_audit.py')
quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality)


class Operators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='keyra-quality-operator-')
        cls.path=Path(cls.temp.name);cls.probe=cls.path/'probe'
        subprocess.run([os.environ.get('CXX','c++'),'-std=c++17','-O2','-DNDEBUG','-DKEYRA_QUALITY_METRICS_ONLY',
            '-I',str(ROOT/'Source'),str(ROOT/'Tools/quality_probe.cpp'),'-o',str(cls.probe)],check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def observe(self,a,rate=48000,note=69):
        a=np.asarray(a,dtype='<f4');a.tofile(self.path/'signal.f32')
        subprocess.run([str(self.probe),'--analyze',str(self.path/'signal.f32'),
            str(self.path/'signal.csv'),str(rate),str(note),str(len(a)/rate)],check=True)
        with (self.path/'signal.csv').open() as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),1);self.assertNotIn(None,rows[0])
        return {k:float(v) for k,v in rows[0].items() if k!='case_id'}

    def test_spectrum_matches_independent_numpy_and_parseval(self):
        rng=np.random.default_rng(719)
        # Non-power-of-two lengths exercise real FFT recovery and zero padding;
        # independent L/R tones, correlated noise and DC expose stereo mistakes.
        for n,rate in ((2400,48000),(3307,44100),(1201,96000)):
            t=np.arange(n)/rate
            a=np.stack((.1*np.sin(2*np.pi*713*t)+.03+rng.normal(0,.01,n),
                        .07*np.cos(2*np.pi*1281*t)-.02+rng.normal(0,.02,n)),axis=1).astype(np.float32)
            d=self.observe(a,rate);w=np.hanning(n);nfft=1<<(n-1).bit_length()
            z=np.fft.rfft(a.astype(float)*w[:,None],n=nfft,axis=0)
            weights=np.ones(len(z));weights[1:-1]=2
            channel_power=np.abs(z)**2*weights[:,None]/(nfft*np.sum(w*w))
            cross=z[:,0]*z[:,1].conj()*weights/(nfft*np.sum(w*w))
            power=channel_power.mean(axis=1);hz=np.fft.rfftfreq(nfft,1/rate)
            self.assertAlmostEqual(d['w0_spectral_power'],np.sum(a.astype(float)**2*w[:,None]**2)/(2*np.sum(w*w)),places=13)
            self.assertAlmostEqual(d['w0_spectral_hz_power'],np.sum(power*hz),places=9)
            for name,mask in [('above4000',hz>=4000),('above8000',hz>=8000),
                              ('band50_150',(hz>=50)&(hz<150)),('band150_250',(hz>=150)&(hz<250)),
                              ('band500_1000',(hz>=500)&(hz<1000))]:
                self.assertAlmostEqual(d['w0_'+name],power[mask].sum(),places=13)
            mask=(hz>=500)&(hz<1000)
            self.assertAlmostEqual(d['w0_band500_1000_l'],channel_power[mask,0].sum(),places=13)
            self.assertAlmostEqual(d['w0_band500_1000_r'],channel_power[mask,1].sum(),places=13)
            self.assertAlmostEqual(d['w0_band500_1000_cross_re'],cross[mask].sum().real,places=13)
            self.assertAlmostEqual(d['w0_band500_1000_cross_im'],cross[mask].sum().imag,places=13)
            fractions=sum(d['w0_'+name] for name in ('f0_0_05','f0_05_2','f0_2_4','f0_4_8','f0_8_16','f0_16_up'))
            self.assertAlmostEqual(fractions,d['w0_spectral_power'],places=14)

    def test_channel_swap_and_antiphase_are_not_collapsed_to_mono(self):
        t=np.arange(2400)/48000;z=.1*np.sin(2*np.pi*700*t)
        d=self.observe(np.stack((z,-z),axis=1))
        self.assertLess(d['w0_lr'],0);self.assertGreater(d['w0_spectral_power'],.004)
        self.assertAlmostEqual(d['w0_band500_1000_cross_re'],-d['w0_band500_1000_l'],places=13)
        a=np.stack((z,.3*np.roll(z,7)),axis=1)
        x=self.observe(a);y=self.observe(a[:,::-1])
        self.assertAlmostEqual(x['w0_band500_1000_cross_im'],-y['w0_band500_1000_cross_im'],places=13)
        self.assertAlmostEqual(x['w0_spectral_power'],y['w0_spectral_power'],places=13)

    def test_silence_and_nonfinite_are_explicit_not_imputed(self):
        d=self.observe(np.zeros((2400,2)))
        self.assertEqual(d['whole_peak'],0);self.assertEqual(d['rise10_frame'],-1)
        self.assertEqual(d['w0_spectral_power'],0)
        _,columns=quality.load_csv(self.path/'signal.csv')
        self.assertTrue(np.isnan(quality.metrics(columns)['rise_ms'][0]))
        a=np.zeros((2400,2));a[11,0]=float('nan');a[17,1]=float('inf')
        d=self.observe(a);self.assertEqual(d['whole_bad'],2);self.assertEqual(d['w0_bad'],2)
        self.assertTrue(np.isnan(quality.divide(0.,0.)))
        self.assertIsNone(quality.clean(float('nan')))

    def test_time_power_cross_power_and_jump(self):
        rng=np.random.default_rng(5);a=rng.normal(0,.01,(1000,2)).astype(np.float32)
        d=self.observe(a);x=a.astype(float)
        self.assertAlmostEqual(d['w0_ll'],np.sum(x[:,0]**2),places=13)
        self.assertAlmostEqual(d['w0_rr'],np.sum(x[:,1]**2),places=13)
        self.assertAlmostEqual(d['w0_lr'],np.sum(x[:,0]*x[:,1]),places=13)
        delta=np.diff(x,axis=0,prepend=np.zeros((1,2)))
        self.assertAlmostEqual(d['w0_diff2'],np.sum(delta**2),places=13)
        self.assertAlmostEqual(d['w0_jump'],np.max(np.abs(delta)),places=13)


class Coverage(unittest.TestCase):
    def test_resume_does_not_accept_a_previously_failed_or_truncated_run(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);csv_path=p/'observed.csv';csv_path.write_text('header\nvalue\nvalue2\n')
            (p/'harness-freeze.json').write_text('{}\n');command=['probe','--grid','0',str(csv_path)]
            good=dict(command=command,freeze_sha256=quality.sha(p/'harness-freeze.json'),
                      csv=str(csv_path),csv_sha256=quality.sha(csv_path),returncode=0,cases=2,expected_cases=2)
            for patch in ({'returncode':3},{'cases':1},{'expected_cases':1}):
                (p/'test.receipt.json').write_text(json.dumps(dict(good,**patch)))
                with self.assertRaisesRegex(RuntimeError,'failed or is incomplete'):
                    quality.run_task(p,'test',command,2)
            (p/'test.receipt.json').write_text(json.dumps(good))
            self.assertEqual(quality.run_task(p,'test',command,2),good)

    def test_compare_refuses_changed_measurement_operator(self):
        with tempfile.TemporaryDirectory() as folder:
            args=SimpleNamespace(baseline=Path(folder)/'a',candidate=Path(folder)/'b')
            with mock.patch.object(quality,'verify',side_effect=[
                    {'pins':{'quality_probe.cpp':'old'}},{'pins':{'quality_probe.cpp':'changed'}}]):
                with self.assertRaisesRegex(RuntimeError,'observation operators differ'):
                    quality.compare(args)

    def test_plan_and_exact_event_coverage(self):
        p=quality.protocol();s=quality.scene_plan()
        self.assertEqual(p['grid']['cases'],67056)
        self.assertEqual(len({c['id'] for c in s}),len(s))
        self.assertEqual(sum(c['family']=='build_cartesian' for c in s),6**4)
        self.assertEqual(sum(c['family']=='long' for c in s),6*5*3*3)
        for model in range(6):
            modes={(c['rate'],c['quality'],c['note']) for c in s if c['model']==model and c['family']=='modes'}
            self.assertEqual(len(modes),3*3*3)
            channels={c['events'][0][-1] for c in s if c['model']==model and c['family']=='channels'}
            self.assertEqual(channels,set(range(1,17)))
        for c in s:
            self.assertTrue(all(0<=a<b<=c['duration'] for a,b in c['windows']))
            self.assertTrue(all(0<=e[0]<c['duration'] for e in c['events']))
            self.assertTrue(all(1<=e[-1]<=16 for e in c['events']))
            self.assertLessEqual(len(c['windows']),6)

    def test_rank_witnesses_use_only_same_key_adjacent_velocity(self):
        rows={k:np.array(v) for k,v in dict(model=[0,0,0,1],note=[60,60,61,60],velocity=[1,2,2,2]).items()}
        d=quality.rank_differences(np.array([0.,-2.,-5.,-50.]),rows,'velocity')
        self.assertEqual(d['available_pairs'],1);self.assertEqual(d['most_negative'][0],(-2.,(0,60,1),(0,60,2)))
        self.assertEqual(quality.rank_differences(np.array([0.,-2.,-5.,-50.]),rows,'note')['available_pairs'],1)


if __name__=='__main__':
    unittest.main()
