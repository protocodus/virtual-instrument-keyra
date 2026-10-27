#!/usr/bin/env python3
"""Source-only exact free/damping/unison scheduling candidate; never execute Piano."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent
EXPECTED='edae57fb1bad84a9e632961726d3ab60b3c5c27474b0f1194bcc89462384ee36'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='0227028b7e86fe3f09d1381fa9dcb860080f22da'
assert sha(ROOT/'src/full_instrument/PreparedModel.h')==EXPECTED
for kind in ['baseline','candidate']:
 dest=OUT/kind
 if dest.exists():raise ValueError('Source snapshot already exists; preserve preparation')
 shutil.copytree(ROOT/'src/full_instrument',dest/'src/full_instrument',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 shutil.copytree(ROOT/'include',dest/'include')
 shutil.copyfile(ROOT/'CMakeLists.txt',dest/'CMakeLists.txt')
original=(OUT/'baseline/src/full_instrument/PreparedModel.h').read_text();s=original
s=s.replace('#include <cstdint>','#include <cstdint>\n#include <cstring>',1)
needle='class Piano {\n';assert s.count(needle)==1;s=s.replace(needle,'#include "FreeUnisonFusion.h"\n\n'+needle,1)
needle='  std::vector<UnisonGroup> unisonGroups;';assert s.count(needle)==1;s=s.replace(needle,needle+'\n  std::array<std::vector<FreeUnisonGroup>,88> freeUnisonGroups;\n  std::array<std::vector<FreeModeRun>,88> freeModeRuns;\n  FreeUnisonInventory freeUnisonInventory;')
needle='    buildUnisonGroups();\n';assert s.count(needle)==1;s=s.replace(needle,needle+'    buildFreeUnisonViews();\n')
needle='  void resetState() noexcept {';assert s.count(needle)==1;s=s.replace(needle,(OUT/'build_views.inc').read_text()+'\n'+needle)
start=original.index('  void oscillators(){');end=original.index('  // Implicit midpoint on the complete reciprocal',start)
osc=original[start:end];new=osc.replace('void oscillators(){','void oscillatorsAndUnison(){').replace('    for(auto &k:keys){','    for(size_t keyIndex=0;keyIndex<keys.size();++keyIndex){auto& k=keys[keyIndex];')
old='      if(!k.hammerActive){for(int i:k.strings)strings[i].m.freeDampedStep();continue;}'
replacement='''      // Branch is selected at entry, before contact can retire this hammer.
      if(!k.hammerActive){
        for(auto& run:freeModeRuns[keyIndex])run.step();
        for(auto& group:freeUnisonGroups[keyIndex]){
          if(group.count==1)group.fusedStep<1>();
          else if(group.count==2)group.fusedStep<2>();
          else group.fusedStep<3>();
        }
        continue;
      }'''
assert new.count(old)==1;new=new.replace(old,replacement)
old='      for(int i:k.strings)strings[i].m.finishDamping();\n';replacement=old+'''      for(auto& group:freeUnisonGroups[keyIndex]){
        if(group.count==1)group.scalarStep<1>();
        else if(group.count==2)group.scalarStep<2>();
        else group.scalarStep<3>();
      }
''';assert new.count(old)==1;new=new.replace(old,replacement)
s=s[:s.index('  // Implicit midpoint on the complete reciprocal')]+new+s[s.index('  // Implicit midpoint on the complete reciprocal'):]
old='    oscillators();groupedUnisonStep();bridgeStep(dt,cachedRadiation);';new='''    if(freeUnisonInventory.valid)oscillatorsAndUnison();
    else {oscillators();groupedUnisonStep();}
    bridgeStep(dt,cachedRadiation);''';assert s.count(old)==1;s=s.replace(old,new)
(OUT/'candidate/src/full_instrument/PreparedModel.h').write_text(s);shutil.copyfile(OUT/'FreeUnisonFusion.h',OUT/'candidate/src/full_instrument/FreeUnisonFusion.h')
diff=subprocess.run(['diff','-u',str(OUT/'baseline/src/full_instrument/PreparedModel.h'),str(OUT/'candidate/src/full_instrument/PreparedModel.h')],capture_output=True,text=True);assert diff.returncode==1;(OUT/'prepared-model.diff').write_text(diff.stdout)
files=[p for kind in ['baseline','candidate'] for p in sorted((OUT/kind).rglob('*')) if p.is_file()]
manifest={str(p.relative_to(OUT)):rec(p) for p in files};(OUT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'snapshot_files':len(files),'original_model':rec(OUT/'baseline/src/full_instrument/PreparedModel.h'),'candidate_model':rec(OUT/'candidate/src/full_instrument/PreparedModel.h'),'diff':rec(OUT/'prepared-model.diff'),'model_constructed':False},indent=2))
