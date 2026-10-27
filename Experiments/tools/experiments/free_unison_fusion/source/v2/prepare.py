#!/usr/bin/env python3
"""ONE source-only pragma delta to frozen exact v1; never construct a Piano."""
from pathlib import Path
import hashlib,json,shutil,datetime
OUT=Path(__file__).resolve().parent;V1=OUT.parent/'v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(V1/'protocol.json')=='0e7f323362d0357fa90fd12e6f41a02a63e22eafe41aaf23952521e2969587f2'
assert sha(V1/'FreeUnisonFusion.h')=='8913d4c737f259ee7fc7c72d465284ac25f97cca79481247ade92c5acd5c54b1'
for record in json.loads((V1/'protocol.json').read_text())['sources']:
 assert sha(Path(record['path']))==record['sha256']
for name in ['baseline','candidate']:
 if (OUT/name).exists():raise ValueError('Prepared snapshot exists; preserve it')
 shutil.copytree(V1/name,OUT/name)
shutil.copyfile(V1/'kernel-parity.cpp',OUT/'kernel-parity.cpp')
s=(V1/'FreeUnisonFusion.h').read_text();needle='    for(size_t i=0;i<rowCount;++i){';assert s.count(needle)==1
pragma='''#if defined(KEYRA_FULL_FREE_UNISON_SIMD) && KEYRA_FULL_FREE_UNISON_SIMD && (defined(__GNUC__) || defined(__clang__))
    #pragma omp simd
#endif
'''
s=s.replace(needle,pragma+needle)
(OUT/'FreeUnisonFusion.h').write_text(s);(OUT/'candidate/src/full_instrument/FreeUnisonFusion.h').write_text(s)
# Every existing snapshot byte except the added pragma header stays unchanged.
changed=[]
for name in ['baseline','candidate']:
 for path in sorted((V1/name).rglob('*')):
  if not path.is_file():continue
  relative=path.relative_to(V1);target=OUT/relative
  if path.read_bytes()!=target.read_bytes():changed.append(str(relative))
assert changed==['candidate/src/full_instrument/FreeUnisonFusion.h']
manifest={str(p.relative_to(OUT)):rec(p) for name in ['baseline','candidate'] for p in sorted((OUT/name).rglob('*')) if p.is_file()}
(OUT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(OUT/'preparation.json').write_text(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Source-only exactV1 plusONEguardedrow-SIMDpragma. No new modelconstruction/steps/timing/audio.','v1_protocol':rec(V1/'protocol.json'),'v1_header':rec(V1/'FreeUnisonFusion.h'),'changed_snapshot_files':changed,'pragma_only_header_delta':True,'FP_body_changed':False,'cache_layout_changed':False,'frozen_v1_archived_unchanged':True},indent=2)+'\n')
print(json.dumps({'changed':changed,'header':rec(OUT/'FreeUnisonFusion.h'),'Piano_constructed':False}))
