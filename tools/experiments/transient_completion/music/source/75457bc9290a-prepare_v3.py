from pathlib import Path
import shutil,json,hashlib,datetime,subprocess
BASE=Path(__file__).resolve().parent;SRC=BASE/'v2';OUT=BASE/'v3'
if OUT.exists():raise SystemExit('Preserve v3')
shutil.copytree(SRC,OUT)
def replace(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise ValueError(a[:100])
 p.write_text(s.replace(a,b))
replace(OUT/'sources/src/full_instrument/FullInstrument.cpp','  impl_->parameters(c.parameters);impl_->reset();return true;','  impl_->parameters(c.parameters);impl_->reset();causal_capture::preparedRhos=impl_->companion.preparedRhos();return true;')
p=OUT/'sources/src/full_instrument/FullInstrument.cpp'
p.write_text(p.read_text()+'''
extern "C" bool causal_capture_coefficients_match(const char* expected,const char* folder){
 const auto& field=causal_capture::preparedRhos;std::vector<double> values(field.size());
 FILE* f=std::fopen(expected,"rb");if(!f)return false;
 const bool full=std::fread(values.data(),sizeof(double),values.size(),f)==values.size();
 const bool ended=std::fgetc(f)==EOF;const bool closed=std::fclose(f)==0;
 const bool written=causal_capture::write(folder,"prepared-rhos.f64le",field);
 return written&&full&&ended&&closed&&values.size()==18253&&std::memcmp(field.data(),values.data(),values.size()*sizeof(double))==0;
}
''')
replace(OUT/'music.cpp','extern "C" uint64_t causal_capture_mismatches();','extern "C" bool causal_capture_coefficients_match(const char*,const char*);\nextern "C" uint64_t causal_capture_mismatches();')
replace(OUT/'music.cpp','if(argc!=3)return 2;','if(argc!=4)return 2;')
replace(OUT/'music.cpp','if(!piano.prepare(config))return 4;','if(!piano.prepare(config))return 4;if(!causal_capture_coefficients_match(argv[3],dir.c_str()))return 11;')
# The copied report describes v2 paths and stays untouched under a new name.
(OUT/'source-preparation.json').rename(OUT/'v2-source-preparation.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
flags=['g++','-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-I'+str(OUT/'sources/include'),'-I'+str(OUT/'sources/src/full_instrument'),'-I'+str(OUT)]
checks=[]
for p in [OUT/'sources/src/full_instrument/FullInstrument.cpp',OUT/'music.cpp',OUT/'filter.cpp']:
 cmd=flags+['-fsyntax-only',str(p)];r=subprocess.run(cmd,capture_output=True,text=True);checks.append({'command':cmd,'returncode':r.returncode,'stderr':r.stderr})
report={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'SOURCE ONLY, no model/coefficient execution, model step, recording/pressure/audio access or render authorization','predecessor':{'path':str(SRC/'source-preparation.json'),'sha256':sha(SRC/'source-preparation.json')},'generator':{'path':str(Path(__file__)),'sha256':sha(__file__)},'changes':['Same explicit per-mode modal law as v2','Expected18253double rho artifact must match exactly after preparation and before first musical frame; actual field written even on mismatch','Main requires expected field path argument; original score/events/process order unchanged'],'syntax_only':checks,'passed':all(x['returncode']==0 for x in checks),'files':[{'path':str(p),'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()]}
(OUT/'source-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'sha256':sha(OUT/'source-preparation.json'),'path':str(OUT/'source-preparation.json')}))
