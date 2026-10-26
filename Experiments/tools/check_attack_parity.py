#!/usr/bin/env python3
"""Compare an attack optimization against a supplied pre-change source file.

Build both with identical scalar host approximations of Rack flags, compare a
fixed four-rate control/event stream byte for byte, then time simultaneous
attacks. This is output parity on this toolchain, not a Jukebox SDK measurement.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FLAGS=['-O3','-std=c++17','-fno-exceptions','-fno-rtti','-fno-builtin',
       '-fno-tree-vectorize','-ffp-contract=off']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-source',type=Path,required=True)
    parser.add_argument('--candidate-source',type=Path,default=ROOT/'src/Piano.cpp')
    parser.add_argument('--compiler',default='g++')
    parser.add_argument('--output',type=Path,default=ROOT/'Validation/attack-optimization.json')
    args=parser.parse_args()
    sources={'baseline':args.baseline_source.resolve(),'candidate':args.candidate_source.resolve()}
    result={'schema_version':1,'platform':platform.platform(),
            'compiler':subprocess.check_output([args.compiler,'--version'],text=True).splitlines()[0],
            'flags':FLAGS,'harness_sha256':sha(ROOT/'tests/attack_performance.cpp'),
            'calibration_sha256':{name:sha(ROOT/'src'/name) for name in ('LiveCalibration.h','UprightCalibration.h')},
            'limits':'Scalar host compiler approximation. Byte parity is verified for the stated event/control stream; timing is not Reason-host certification.',
            'stream':{'sample_rates':[44100,48000,88200,96000],
                      'events_per_rate':120,'frames_per_event':257,
                      'channels':2,'encoding':'native float32, left/right block planes'},
            'variants':{}}
    with tempfile.TemporaryDirectory(prefix='keyra-attack-parity-') as temporary:
        folder=Path(temporary)
        snapshots={label:folder/(label+'.cpp') for label in sources}
        for label,source in sources.items(): snapshots[label].write_bytes(source.read_bytes())
        result['source_diff']=''.join(difflib.unified_diff(snapshots['baseline'].read_text().splitlines(True),
                                                        snapshots['candidate'].read_text().splitlines(True),
                                                        fromfile='baseline/Piano.cpp',tofile='candidate/Piano.cpp'))
        for label,source in snapshots.items():
            executable=folder/label
            command=[args.compiler,*FLAGS,'-I'+str(ROOT/'include'),'-I'+str(ROOT/'src'),
                     str(source),str(ROOT/'tests/attack_performance.cpp'),'-o',str(executable)]
            subprocess.run(command,check=True)
            stream=folder/(label+'.f32')
            subprocess.run([str(executable),'--parity-stream',str(stream)],check=True)
            result['variants'][label]={'source_sha256':sha(source),'binary_sha256':sha(executable),
                                       'stream_sha256':sha(stream),'stream_bytes':stream.stat().st_size,
                                       'attack_diagnostic':json.loads(subprocess.check_output([str(executable)],text=True))}
        baseline,candidate=[result['variants'][label] for label in ('baseline','candidate')]
        result['byte_identical_output']=(baseline['stream_sha256']==candidate['stream_sha256']
                                         and baseline['stream_bytes']==candidate['stream_bytes'])
        result['timing_comparison']=[]
        for old,new in zip(baseline['attack_diagnostic']['cases'],candidate['attack_diagnostic']['cases']):
            result['timing_comparison'].append({'sample_rate':old['sample_rate'],'notes':old['notes'],
                                                'baseline_median_us':old['median_us'],'candidate_median_us':new['median_us'],
                                                'median_reduction_fraction':1-new['median_us']/old['median_us']})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'byte_identical_output':result['byte_identical_output'],
                      'timing_comparison':result['timing_comparison']},indent=2))
    if not result['byte_identical_output']: raise SystemExit(1)


if __name__=='__main__': main()
