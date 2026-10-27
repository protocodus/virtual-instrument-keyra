from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
ROOT=Path('/workspace/virtual-instrument-keyra')
BASE=ROOT/'out/full-transient-music/v1';OUT=BASE.parent/'v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':str(p),'sha256':sha(p)}
def once(s,a,b):
 if s.count(a)!=1:raise ValueError('anchor '+a[:60])
 return s.replace(a,b)
if OUT.exists():raise SystemExit('Preserve existing v2')
OUT.mkdir()
for name in ['PitchMemoryCompanion.h','ShadowMechanics.h','filter.cpp','music.cpp']:
 shutil.copyfile(BASE/name,OUT/name)
for name in ['sources','shadow']:shutil.copytree(BASE/name,OUT/name)
# Keep predecessor helpers intact and add an all-mode diagonal contraction.
p=OUT/'ShadowMechanics.h';s=p.read_text();idx=s.rfind('\n}')
s=s[:idx]+'''
// Diagonal paired q/p loss. The order matches scalePitch exactly when fields
// are uniform within each string/body; no modal rotation or input B changes.
template<class PianoLike>
double scaleField(PianoLike& p,const std::vector<std::vector<double>>& rhos,
                  const std::vector<double>& bodyRhos,Stats& stats) {
  const double before=energy(p);
  for(size_t i=0;i<p.strings.size();++i){auto& m=p.strings[i].m;
    for(size_t j=0;j<m.size();++j){const double rho=rhos[i][j];
      m.q[j]=double(m.q[j])*rho;m.p[j]=double(m.p[j])*rho;}}
  for(size_t i=0;i<p.board.size();++i){auto& z=p.board[i];
    const double rho=bodyRhos[i];z.q=double(z.q)*rho;z.p=double(z.p)*rho;}
  const double after=energy(p);stats.rhoLoss+=before-after;
  stats.maxPositiveScaleEnergy=std::max(stats.maxPositiveScaleEnergy,after-before);
  return before;
}
'''+s[idx:];p.write_text(s)
p=OUT/'PitchMemoryCompanion.h';s=p.read_text()
s=once(s,'struct FrameResult {','enum class MemoryLaw { PitchOnly, PitchAndModalFrequency };\nstruct FrameResult {')
s=once(s,'  std::vector<double> rhos_;','  std::vector<std::vector<double>> rhos_;\n  std::vector<double> bodyRhos_;\n  MemoryLaw law_=MemoryLaw::PitchOnly;\n  double maxGamma_=0;')
s=once(s,'template<class Primary> bool prepare(const Primary& source) {','template<class Primary> bool prepare(const Primary& source,MemoryLaw law) {\n    law_=law;')
a='''    rhos_.clear();rhos_.reserve(fast_->strings.size());
    for(const auto& st:fast_->strings){const double rho=std::exp(-gammas_[st.note-21]/48000);
      if(!std::isfinite(rho)||rho<=0||rho>bodyRho_)return false;rhos_.push_back(rho);}
'''
b='''    rhos_.clear();rhos_.reserve(fast_->strings.size());maxGamma_=100;
    for(const auto& st:fast_->strings){std::vector<double> field;field.reserve(st.m.size());
      for(size_t j=0;j<st.m.size();++j){const double hz=double(st.m.omega[j])/(2*pitch_shadow::pi);
        if(!std::isfinite(hz)||hz<=0)return false;
        const double gamma=law_==MemoryLaw::PitchAndModalFrequency?
          std::max(gammas_[st.note-21],100*hz/1000):gammas_[st.note-21];
        const double rho=std::exp(-gamma/48000);
        if(!std::isfinite(rho)||rho<=0||rho>bodyRho_)return false;
        maxGamma_=std::max(maxGamma_,gamma);field.push_back(rho);}
      rhos_.push_back(std::move(field));}
    bodyRhos_.clear();bodyRhos_.reserve(fast_->board.size());
    for(const auto& z:fast_->board){const double hz=z.w/(2*pitch_shadow::pi);
      if(!std::isfinite(hz)||hz<=0)return false;
      const double gamma=law_==MemoryLaw::PitchAndModalFrequency?100*std::max(1.,hz/1000):100.;
      const double rho=std::exp(-gamma/48000);
      if(!std::isfinite(rho)||rho<=0||rho>bodyRho_)return false;
      maxGamma_=std::max(maxGamma_,gamma);bodyRhos_.push_back(rho);}
'''
s=once(s,a,b)
s=once(s,'scalePitch(*fast_,rhos_,bodyRho_,stats)','scaleField(*fast_,rhos_,bodyRhos_,stats)')
s=s.replace('body_gamma\\\":100','body_gamma_min\\\":100')
s=once(s,'  std::string report() const {','''  // Exact native-f64 field layout: all string modes in original order, then
  // all board modes. Captured for independent comparison to the frozen pilot.
  std::vector<double> preparedRhos() const {
    std::vector<double> out;out.reserve(17778+475);
    for(const auto& field:rhos_)out.insert(out.end(),field.begin(),field.end());
    out.insert(out.end(),bodyRhos_.begin(),bodyRhos_.end());return out;
  }
  std::string report() const {''')
s=once(s,'s<<"],\\\"K_LR\\\":["<<KLR_[0]', 's<<"],\\\"memory_law\\\":\\\""<<(law_==MemoryLaw::PitchAndModalFrequency?"pitch-and-modal-frequency":"pitch-only")<<"\\\",\\\"max_gamma\\\":"<<maxGamma_<<",\\\"K_LR\\\":["<<KLR_[0]')
p.write_text(s)
p=OUT/'sources/src/full_instrument/FullInstrument.cpp';s=p.read_text()
s=once(s,'companion.prepare(*impl_->model)','companion.prepare(*impl_->model,pitch_music::MemoryLaw::PitchAndModalFrequency)')
s=once(s,'if(frame+1==causal_capture::count)causal_capture::companionReport=impl_->companion.report();','if(frame+1==causal_capture::count){causal_capture::companionReport=impl_->companion.report();causal_capture::preparedRhos=impl_->companion.preparedRhos();}')
p.write_text(s)
p=OUT/'sources/src/full_instrument/Capture.h';s=p.read_text()
s=once(s,'inline std::string companionReport;','inline std::string companionReport;\ninline std::vector<double> preparedRhos;')
s=once(s,'companionReport.clear();','companionReport.clear();preparedRhos.clear();')
s=once(s,'write(folder,"state-proof.u64le",stateProof)', 'write(folder,"prepared-rhos.f64le",preparedRhos)&&write(folder,"state-proof.u64le",stateProof)')
p.write_text(s)
checks=[]
flags=['g++','-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-I'+str(OUT/'sources/include'),'-I'+str(OUT/'sources/src/full_instrument'),'-I'+str(OUT)]
for p in [OUT/'sources/src/full_instrument/FullInstrument.cpp',OUT/'music.cpp',OUT/'filter.cpp']:
 command=flags+['-fsyntax-only',str(p)];r=subprocess.run(command,capture_output=True,text=True)
 checks.append({'source':rec(p),'command':command,'returncode':r.returncode,'stderr':r.stderr})
report={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'SOURCE ONLY, no model construction, coefficient export, model step, recording/pressure/audio access, or render authorization','predecessor_plan':rec(BASE/'plan.json'),'generator':rec(Path(__file__)),'changes':['paired q/p per-mode rho field, selected explicit PitchAndModalFrequency law','strings gamma=100*max(1,f0_key/f0_C3,f_mode/1000); board gamma=100*max(1,f_board/1000)','source damping/active branch ordering, original physics, HP200 bytes unchanged','prepared-rhos.f64le planned capture in original string modes then board modes order'],'operator_caveat':'Nonuniform contraction A*D_rho does not satisfy scalar rho^age impulse-ramp identity. Not a newly identified physical part, not realtime architecture.','new_model_steps':0,'new_coefficients_or_pressure_accessed':False,'syntax_only':checks,'passed':all(c['returncode']==0 for c in checks),'sources':[rec(p) for p in sorted(OUT.rglob('*')) if p.is_file()]}
(OUT/'source-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'path':str(OUT/'source-preparation.json'),'sha256':sha(OUT/'source-preparation.json')}))
