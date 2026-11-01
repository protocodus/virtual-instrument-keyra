"""Native endpoint/continuity/energy checks for the guarded velocity morph.

Run with python3 Tests/test_velocity_interpolation.py. Uses no recordings and
compiles only a temporary C++17 probe of the real engine implementation.
"""
import copy
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('velocity_guard', ROOT/'Tools/generate_velocity_interpolation.py')
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

PROBE = r'''
#include <memory>
#include <array>
#include <cstddef>
#include <cstdint>
#define private public
#include "KeyraEngine.h"
#undef private
#include "KeyraEngine.cpp"
#include <complex>
#include <iostream>
#include <stdexcept>
using Z=std::complex<double>;
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
Z coefficient(const keyra::LaneData& lane){return std::pow(10.,lane.level/20)*Z(lane.phase.re,lane.phase.im);}
int main(){try{
  keyra::Engine engine(48000);std::size_t enabled=0,endpoints=0;
  for(int piano=0;piano<keyra::pianoCount;++piano){const auto& m=keyra::models[piano];int modelIntervals=0;
    const int count=m.anchors[m.anchorCount-1].first+m.anchors[m.anchorCount-1].count;
    for(int p=0;p<count;++p){const auto& measured=m.partials[p];const auto& cache=engine.impl->partialLanes[m.partialFirst+p];
      const auto& rawCache=static_cast<const std::array<keyra::LaneCache,keyra::lanes>&>(cache);
      for(int layer=0;layer<m.layers;++layer){const double v=m.layerVelocity[layer];
        const auto raw=keyra::single(m,measured,rawCache,v),now=keyra::single(m,measured,cache,v);
        for(int j=0;j<keyra::lanes;++j){const auto& a=raw.lane[j];const auto& b=now.lane[j];
          require(a.level==b.level&&a.phase.re==b.phase.re&&a.phase.im==b.phase.im&&a.rate==b.rate&&a.offset==b.offset,"measured layer changed");}
        ++endpoints;
      }
      // Extrapolation and intervals that the guard rejects remain bit-identical.
      for(double v:{1.,127.}){const auto raw=keyra::single(m,measured,rawCache,v),now=keyra::single(m,measured,cache,v);
        for(int j=0;j<keyra::lanes;++j)require(raw.lane[j].level==now.lane[j].level&&raw.lane[j].phase.re==now.lane[j].phase.re&&raw.lane[j].phase.im==now.lane[j].phase.im,"extrapolation changed");}
      int index=0;
      for(int layer=0;layer<m.layers-1;++layer){const double lo=m.layerVelocity[layer],hi=m.layerVelocity[layer+1];
        if(!(cache.velocityMask&(1u<<layer))){
          const auto raw=keyra::single(m,measured,rawCache,(lo+hi)/2),now=keyra::single(m,measured,cache,(lo+hi)/2);
          for(int j=0;j<keyra::lanes;++j)require(raw.lane[j].level==now.lane[j].level&&raw.lane[j].phase.re==now.lane[j].phase.re&&raw.lane[j].phase.im==now.lane[j].phase.im,"rejected interval changed");
          continue;
        }
        ++enabled;++modelIntervals;const auto& c=cache.velocity[index++];
        require(c.overlap>=0&&c.overlap<=1,"invalid window overlap");
        const auto a=keyra::single(m,measured,rawCache,lo),b=keyra::single(m,measured,rawCache,hi);
        for(double t:{1e-8,.125,.5,.875,1-1e-8}){
          const auto played=keyra::single(m,measured,cache,lo+t*(hi-lo));
          const double expected=std::exp(keyra::mix(c.logPowerA,c.logPowerB,t));
          if(std::abs(keyra::windowPower(played)/expected-1)>=1e-9)
            std::cerr<<"piano="<<piano<<" partial="<<p<<" layer="<<layer<<" t="<<t<<" relative_power_error="<<keyra::windowPower(played)/expected-1<<'\n';
          require(std::abs(keyra::windowPower(played)/expected-1)<1e-9,"intermediate window power mismatch");
          const double norm2=(1-t)*(1-t)+t*t+2*t*(1-t)*c.overlap;
          require(norm2>=.5&&norm2<=1+1e-14,"unbounded cancellation correction");
          if(t<1e-7||t>1-1e-7){const auto& endpoint=t<.5?a:b;double error=0,scale=0;
            for(int j=0;j<keyra::lanes;++j){error+=std::norm(coefficient(played.lane[j])-coefficient(endpoint.lane[j]));scale+=std::norm(coefficient(endpoint.lane[j]));}
            require(std::sqrt(error/scale)<2e-6,"velocity endpoint discontinuity");}
        }
      }
    }
    require(modelIntervals>0,"a piano has no guarded repair");
  }
  require(enabled==keyra::measured::velocity::intervalCount,"cache/mask interval count mismatch");
  std::cout<<"measured_endpoints="<<endpoints<<" guarded_intervals="<<enabled
           <<" extra_cache_bytes="<<enabled*sizeof(keyra::VelocityInterpolation)+keyra::partialCaches*(sizeof(keyra::PartialCache)-sizeof(std::array<keyra::LaneCache,keyra::lanes>))<<'\n';
  return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''


class VelocityInterpolation(unittest.TestCase):
    def test_freshness_failure_reports_exact_metadata_path_and_header_hash(self):
        import json
        from unittest import mock
        stored = {'sources': {'Source/DSP/KeyraEngine.cpp': 'old'},
                  'intervals': [{'candidate_excursion_db': [0.]}]}
        generated = copy.deepcopy(stored)
        generated['sources']['Source/DSP/KeyraEngine.cpp'] = 'new'
        generated['intervals'][0]['candidate_excursion_db'][0] = 2*guard.ROUNDING_DB
        with tempfile.TemporaryDirectory(prefix='keyra-freshness-diagnostic-') as folder:
            header, metadata = Path(folder)/'data.h', Path(folder)/'data.json'
            # A newline-only change must not be hidden by text-mode reads.
            header.write_bytes(b'new header\r\n')
            metadata.write_text(json.dumps(stored))
            argv = ['generate_velocity_interpolation.py', '--check', '--header', str(header),
                    '--metadata', str(metadata)]
            with mock.patch.object(sys, 'argv', argv), mock.patch.object(guard, 'generate',
                    return_value=('new header\n', generated)), self.assertRaises(SystemExit) as error:
                guard.main()
        message = str(error.exception)
        self.assertIn('header bytes: stored sha256=', message)
        self.assertIn('/sources/Source~1DSP~1KeyraEngine.cpp: stored=', message)
        self.assertIn('/intervals/0/candidate_excursion_db/0: stored=0.0, generated=2e-08', message)

    def test_provenance_reporting_roundoff_keeps_decisions_and_hashes_exact(self):
        reference = {
            'sources': {'Source/DSP/KeyraEngine.cpp': 'source-hash'},
            'generated_header_sha256': 'header-hash', 'enabled_intervals': 1,
            'partial_count': 2, 'rounding_tolerance_db': guard.ROUNDING_DB,
            'intervals': [{'model': 'grand', 'note': 60, 'order': 1, 'partial': 0,
                           'layer': 2, 'enabled': True, 'baseline_excursion_db': .1,
                           'candidate_excursion_db': [0., 0., None, 0.]}]}
        match = lambda metadata, header='same': guard.artifacts_match('same', header, reference, metadata)
        self.assertTrue(match(reference))
        for key, index in [('baseline_excursion_db', None), ('candidate_excursion_db', 0)]:
            small = copy.deepcopy(reference)
            if index is None:
                small['intervals'][0][key] += guard.ROUNDING_DB/2
            else:
                small['intervals'][0][key][index] += guard.ROUNDING_DB/2
            self.assertTrue(match(small))
            large = copy.deepcopy(reference)
            if index is None:
                large['intervals'][0][key] += 2*guard.ROUNDING_DB
            else:
                large['intervals'][0][key][index] += 2*guard.ROUNDING_DB
            self.assertFalse(match(large))
        for key, value in [('model', 'upright'), ('note', 61), ('order', 2),
                           ('partial', 1), ('layer', 3), ('enabled', False), ('enabled', 1)]:
            changed = copy.deepcopy(reference); changed['intervals'][0][key] = value
            self.assertFalse(match(changed), key)
        for key, value in [('enabled_intervals', 2), ('partial_count', 3),
                           ('generated_header_sha256', 'other'),
                           ('rounding_tolerance_db', guard.ROUNDING_DB*2)]:
            changed = copy.deepcopy(reference); changed[key] = value
            self.assertFalse(match(changed), key)
        changed = copy.deepcopy(reference); changed['sources']['Source/DSP/KeyraEngine.cpp'] = 'other'
        self.assertFalse(match(changed))
        self.assertFalse(match(reference, 'changed header bytes'))
        changed = copy.deepcopy(reference); changed['intervals'].append(copy.deepcopy(changed['intervals'][0]))
        self.assertFalse(match(changed))
        for value in [0., float('nan'), float('inf')]:
            changed = copy.deepcopy(reference); changed['intervals'][0]['candidate_excursion_db'][2] = value
            self.assertFalse(match(changed))
        for value in [None, float('nan'), float('inf')]:
            changed = copy.deepcopy(reference); changed['intervals'][0]['candidate_excursion_db'][0] = value
            self.assertFalse(match(changed))

    def test_native_endpoints_continuity_power_and_cache(self):
        with tempfile.TemporaryDirectory(prefix='keyra-velocity-test-') as directory:
            source, binary = Path(directory)/'probe.cpp', Path(directory)/'probe'
            source.write_text(PROBE)
            subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2', '-ffp-contract=off', '-I', str(ROOT/'Source/DSP'),
                            str(source), '-o', str(binary)], check=True, capture_output=True, text=True)
            print(subprocess.check_output([str(binary)], text=True).strip())

    def test_quartic_extrema_bound_independent_dense_sweep(self):
        rng = np.random.default_rng(20261101)
        t = np.linspace(0, 1, 2001)
        for _ in range(300):
            pa, pb, x, y = np.exp(rng.uniform(-10, 5, 4))
            rho = rng.uniform(0, 1)
            c = rng.uniform(-.999, .999)*np.sqrt(x*y)
            q = np.array([x, 2*(c-x), x+y-2*c])
            bound, _ = guard.constant_window_extrema(pa, pb, rho, q)
            curve = pa*np.exp(np.log(pb/pa)*t)*np.polynomial.polynomial.polyval(t, q)/(1+2*(rho-1)*t+2*(1-rho)*t*t)
            ends = curve[[0, -1]]
            observed = max(0., 10*np.log10(ends.min()/curve.min()), 10*np.log10(curve.max()/ends.max()))
            self.assertGreaterEqual(bound+1e-8, observed)
            self.assertTrue(np.isfinite(bound))

    def test_invalid_numeric_guard_inputs_are_rejected(self):
        for bad in (0., -1., float('nan'), float('inf')):
            for pa, pb in ((bad, 1.), (1., bad)):
                self.assertEqual(guard.constant_window_extrema(pa, pb, .5, [1., 0., 0.])[0], float('inf'))
        for rho in (-.1, 1.1, float('nan'), float('inf')):
            self.assertEqual(guard.constant_window_extrema(1., 1., rho, [1., 0., 0.])[0], float('inf'))
        for q in ([float('nan'), 0., 0.], [1., float('inf'), 0.], [-1., 0., 0.]):
            self.assertEqual(guard.constant_window_extrema(1., 1., .5, q)[0], float('inf'))
        probe = r'''
#define main velocity_guard_generator_main
#include "VelocityInterpolationGuard.cpp"
#undef main
int main(){
  for(double bad:{0.,-1.,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})
    for(int field=0;field<3;++field){
      double power[3]={1,1,1};power[field]=bad;bool rejected=false;
      try{excursion(power[0],power[1],power[2]);}catch(const std::runtime_error&){rejected=true;}
      if(!rejected)return 1;
    }
  return excursion(1,1,1)==0?0:1;
}
'''
        with tempfile.TemporaryDirectory(prefix='keyra-invalid-velocity-') as directory:
            source, binary = Path(directory)/'probe.cpp', Path(directory)/'probe'
            source.write_text(probe)
            subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2', '-ffp-contract=off',
                            '-I', str(ROOT/'Tools'), '-I', str(ROOT/'Source'), str(source), '-o', str(binary)],
                           check=True, capture_output=True, text=True)
            subprocess.run([str(binary)], check=True)

    def test_generator_bootstraps_without_header_and_after_partial_count_change(self):
        def succeeds(command):
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+'\n'+result.stderr)

        def masks(text):
            body = text.split('masks{{', 1)[1].split('}};', 1)[0]
            return [int(value) for value in re.findall(r'\d+', body)]

        expected = (ROOT/'Source/DSP/MeasuredVelocityInterpolation.h').read_text()
        with tempfile.TemporaryDirectory(prefix='keyra-velocity-bootstrap-') as directory:
            isolated = Path(directory)
            dsp = isolated/'Source/DSP'
            shutil.copytree(ROOT/'Source/DSP', dsp, ignore=shutil.ignore_patterns('MeasuredVelocityInterpolation.h'))
            (isolated/'Tools').mkdir()
            for name in ('generate_velocity_interpolation.py', 'VelocityInterpolationGuard.cpp'):
                shutil.copy2(ROOT/'Tools'/name, isolated/'Tools'/name)
            header = dsp/'MeasuredVelocityInterpolation.h'
            command = [sys.executable, str(isolated/'Tools/generate_velocity_interpolation.py')]
            self.assertFalse(header.exists())
            succeeds(command)
            self.assertEqual(header.read_text(), expected)

            # A new unused grand slot shifts every later model's cache offsets.
            # This simulates a changed fitted partial count against an old mask
            # header without inventing or altering any measured partial values.
            grand = dsp/'MeasuredModalData.h'
            text = grand.read_text()
            old_count = int(re.search(r'std::array<Partial,(\d+)> partials', text).group(1))
            grand.write_text(text.replace(f'std::array<Partial,{old_count}> partials',
                                          f'std::array<Partial,{old_count+1}> partials', 1))
            compile_only = [os.environ.get('CXX', 'c++'), '-std=c++17', '-fsyntax-only', str(dsp/'KeyraEngine.cpp')]
            stale = subprocess.run(compile_only, capture_output=True, text=True)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn('velocity masks cover the measured partials', stale.stderr)
            succeeds(command)
            old_masks = masks(expected)
            self.assertEqual(masks(header.read_text()), old_masks[:old_count]+[0]+old_masks[old_count:])
            succeeds(compile_only)

            # A mismatched declared capacity must fail at compile time, before
            # constructor writes could ever overrun the interval cache.
            generated = header.read_text()
            count = int(re.search(r'intervalCount=(\d+)', generated).group(1))
            header.write_text(generated.replace(f'intervalCount={count}', f'intervalCount={count+1}'))
            wrong_capacity = subprocess.run(compile_only, capture_output=True, text=True)
            self.assertNotEqual(wrong_capacity.returncode, 0)
            self.assertIn('velocity cache capacity equals the mask population', wrong_capacity.stderr)


if __name__ == '__main__':
    unittest.main()
