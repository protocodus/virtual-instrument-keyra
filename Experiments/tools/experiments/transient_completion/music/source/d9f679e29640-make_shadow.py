#!/usr/bin/env python3
"""Generate a namespace-only pure shadow model; never construct or run Piano.

Only C++ identifier tokens are renamed. Comments, literals and all other bytes
are retained. A syntax-only translation unit checks coexistence with the pure
original model. No object, executable, model state, audio or freeze is created.
"""
from pathlib import Path
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,re,subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'tools/experiments/causal_radiation_pilot/producer/original_core/src/full_instrument'
EXPECTED={
 'PreparedModel.h':'5c8c92f8a761b46a66f3823765f6348ab0c08b74457d7efc062f0941ab07faf8',
 'PreparedCalibration.h':'619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7',
}
RENAMES={b'grand':b'pitch_shadow',b'piano_calibration':b'pitch_shadow_calibration'}
# The pinned headers contain ordinary C++ strings/chars and comments, no raw
# strings. Keep those opaque and replace only complete identifier tokens.
TOKENS=re.compile(rb'//[^\n]*(?:\n|$)|/\*[\s\S]*?\*/|"(?:\\[\s\S]|[^"\\])*"|\'(?:\\[\s\S]|[^\'\\])*\'|[A-Za-z_][A-Za-z0-9_]*')
FORBIDDEN=(b'causal_trace',b'causal_capture',b'Capture.h',b'Trace.h',b'CausalRadiation.h')

def sha(data):return hashlib.sha256(data).hexdigest()
def rename(data,mapping):
 count=Counter()
 def change(match):
  token=match.group()
  if token in mapping:count[token.decode('ascii')]+=1
  return mapping.get(token,token)
 return TOKENS.sub(change,data),dict(count)

def inspect():
 rows=[]
 for name,expected in EXPECTED.items():
  source=SOURCE/name;old=source.read_bytes()
  if sha(old)!=expected:raise ValueError('Original pure source identity changed: '+name)
  if re.search(rb'\b(?:u8|u|U|L)?R"',old):raise ValueError('Unsupported raw literal in pinned input')
  if any(token in old for token in RENAMES.values()):raise ValueError('Destination identifier already appears in original input')
  new,counts=rename(old,RENAMES)
  inverse,inverse_counts=rename(new,{v:k for k,v in RENAMES.items()})
  if inverse!=old:raise ValueError('Inverse namespace normalization is not byte-exact: '+name)
  if any(hook in old or hook in new for hook in FORBIDDEN):raise ValueError('Instrumented source rejected: '+name)
  # A code token must be renamed even when the old spelling remains in an
  # unchanged closing comment. Re-applying the mapping must find no code token.
  again,remaining=rename(new,RENAMES)
  if again!=new or remaining:raise ValueError('Unrenamed original C++ identifier: '+name)
  rows.append({'filename':name,'source_path':str(source),'source_sha256':sha(old),
   'source_bytes':len(old),'shadow_path':str(OUT/'shadow'/name),
   'shadow_sha256':sha(new),'shadow_bytes':len(new),'inverse_normalized_sha256':sha(inverse),
   'inverse_normalized_bytes_exact':True,'identifier_replacements':counts,
   'inverse_identifier_replacements':inverse_counts,'instrumentation_hooks_absent':True,
   '_new':new})
 return rows

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--check',action='store_true',help='Validate existing generated headers and metadata without rewriting')
 args=parser.parse_args();rows=inspect();destination=OUT/'shadow';report_path=OUT/'namespace-equivalence.json'
 if args.check:
  report=json.loads(report_path.read_text())
  if report['generator_sha256']!=sha(Path(__file__).read_bytes()):raise ValueError('Generator no longer matches report')
  for row in rows:
   if Path(row['shadow_path']).read_bytes()!=row['_new']:raise ValueError('Generated shadow differs: '+row['filename'])
  print(json.dumps({'checked':True,'files':len(rows),'inverse_normalized_bytes_exact':True,'model_constructed':False,'model_steps':0}))
  return
 if report_path.exists() or destination.exists():raise ValueError('New shadow output paths required; use --check to inspect existing files')
 destination.mkdir(parents=True)
 for row in rows:Path(row['shadow_path']).write_bytes(row['_new'])
 unit='\n'.join([
  '#include <type_traits>',
  '#include '+json.dumps(str(SOURCE/'PreparedModel.h')),
  '#include '+json.dumps(str(destination/'PreparedModel.h')),
  'static_assert(!std::is_same<grand::Piano,pitch_shadow::Piano>::value,"separate model namespace");',
  'static_assert(!std::is_same<piano_calibration::Anchor,pitch_shadow_calibration::Anchor>::value,"separate calibration namespace");',
  'static_assert(sizeof(grand::Piano)==sizeof(pitch_shadow::Piano),"same model layout");',
  'static_assert(sizeof(grand::Options)==sizeof(pitch_shadow::Options),"same options layout");',
  'static_assert(piano_calibration::partials==pitch_shadow_calibration::partials,"same calibration topology");',
  'static_assert(piano_calibration::anchors.size()==pitch_shadow_calibration::anchors.size(),"same anchor count");',
  'static_assert(piano_calibration::anchors[0].f1==pitch_shadow_calibration::anchors[0].f1,"same constant data");',
 ])+'\n'
 command=['g++','-std=c++17','-O3','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-x','c++','-fsyntax-only','-']
 compiled=subprocess.run(command,input=unit,text=True,capture_output=True)
 compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0]
 report={'schema_version':1,'created_at_utc':datetime.now(timezone.utc).isoformat(),
  'scope':'Source-only namespace equivalence and coexistence. No Piano construction, physical step, rendering, coefficient export, audio access or freeze.',
  'generator_path':str(Path(__file__)),'generator_sha256':sha(Path(__file__).read_bytes()),
  'identifier_map':{k.decode():v.decode() for k,v in RENAMES.items()},
  'transformation':'C++ identifier tokens only; comments, quoted literals, include filenames and every other byte unchanged.',
  'files':[{k:v for k,v in row.items() if k!='_new'} for row in rows],
  'syntax_only':{'command':command,'translation_unit':unit,'compiler':compiler,
   'exit_code':compiled.returncode,'stdout':compiled.stdout,'stderr':compiled.stderr,
   'passed':compiled.returncode==0,'object_or_executable_created':False},
  'forbidden_instrumentation_markers':[x.decode() for x in FORBIDDEN],
  'all_inverse_normalizations_byte_exact':True,'model_constructed':False,'model_steps':0,
  'pressure_or_recording_data_accessed':False,'freeze_created':False,'canonical_source_changed':False}
 report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 if compiled.returncode:raise ValueError('Coexistence syntax check failed; generated sources and report retained')
 print(json.dumps({'passed':True,'files':len(rows),'report':str(report_path),'report_sha256':sha(report_path.read_bytes()),'model_constructed':False,'model_steps':0},indent=2))

if __name__=='__main__':main()
