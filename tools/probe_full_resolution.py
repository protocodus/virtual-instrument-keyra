#!/usr/bin/env python3
"""Three bounded modal-resolution experiments on the full biased-float piano.

Only primary/secondary partial caps change. Preparation recomputes mechanical
ports and radiation; no static correction, held-out recording or parameter fit.
"""
from __future__ import annotations
import argparse,difflib,hashlib,json,math,platform,shutil,statistics,subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import probe_full_precision as precision
ROOT=Path(__file__).resolve().parents[1]
PINNED_FLOAT_SOURCE='7ecdb865518ad726e693e104e87a00f19d2dd05f062c702e0ade61a5f996e411'
PINNED_CALIBRATION='619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7'


def replace(source,old,new):
    if source.count(old)!=1:raise ValueError('Expected exactly one template match: '+old[:60])
    return source.replace(old,new,1)

TOPOLOGY=r'''
struct TopologyResult {
  bool passed=true,bothPolarizations=true,unisonMembership=true,groupCache=true,coefficientsFinite=true;
  size_t modes=0,expectedModes=0,primaryModes=0,secondaryModes=0,keys=0,strings=0,board=0;
  double maxStringComplianceError=0,maxContactComplianceError=0,maxRotationNormExcess=0;
};
TopologyResult topology(const Piano& piano) {
  using namespace grand;
  constexpr int caps[2]={@PRIMARY_CAP@,@SECONDARY_CAP@};
  TopologyResult result;
  result.keys=piano.keys.size();result.strings=piano.strings.size();result.board=piano.board.size();
  std::vector<std::vector<int>> membership;
  for(const auto& st:piano.strings)membership.emplace_back(st.m.size(),0);
  std::array<double,88> contactCompliance{};
  std::array<int,88> keyStrings{};
  for(size_t si=0;si<piano.strings.size();++si){
    const auto& st=piano.strings[si];const auto& m=st.m;const int n=st.note;
    if(n<21||n>108){result.passed=false;continue;}
    const auto& key=piano.keys[n-21];Cal cal(n);++keyStrings[n-21];
    const int stringCount=n<=31?1:n<=43?2:3;
    const double detunes[3]={-.60,.12,.73};
    double cents=stringCount==1?0:stringCount==2?(st.unison==0?-.38:.43):detunes[st.unison];
    cents*=.7+.45*(n-21)/87.0;
    if(piano.opt.calibrated)cents*=cal.scalar(&piano_calibration::Anchor::detuneScale);
    const double fundamental=key.f0*std::pow(2.0,cents/1200);
    size_t offset=0;int observed[2]={0,0};double compliance=0;
    for(int pol=0;pol<2;++pol){
      for(int j=1;j<=caps[pol];++j){
        double f=j*fundamental*std::sqrt((1+key.B*j*j)/(1+key.B));
        f*=pol==0?1.0:1.00023+.00002*std::sin(n*.7);
        if(f>(pol==0?19000.0:9000.0))break;
        ++result.expectedModes;
        if(offset>=m.size()){result.passed=false;continue;}
        result.passed=result.passed&&m.partial[offset]==j&&m.polarization[offset]==pol&&
          m.omega[offset]==static_cast<float>(2*pi*f);
        ++observed[pol];++offset;
      }
    }
    result.passed=result.passed&&offset==m.size()&&st.unison>=0&&st.unison<stringCount;
    result.bothPolarizations=result.bothPolarizations&&observed[0]>0&&observed[1]>0;
    result.primaryModes+=observed[0];result.secondaryModes+=observed[1];result.modes+=m.size();
    for(size_t j=0;j<m.size();++j){
      const double b=static_cast<double>(m.b[j]);compliance+=b*b;
      contactCompliance[n-21]+=static_cast<double>(m.hammer[j])*static_cast<double>(m.forceQ[j]);
      const double c=static_cast<double>(m.c[j]),s=static_cast<double>(m.s[j]);
      result.maxRotationNormExcess=std::max(result.maxRotationNormExcess,c*c+s*s-1);
      for(double value:{double(m.q[j]),double(m.p[j]),double(m.c[j]),double(m.s[j]),double(m.omega[j]),
          double(m.hammer[j]),double(m.b[j]),double(m.forceQ[j]),double(m.forceP[j]),double(m.loss[j]),
          double(m.damper[j]),double(m.damp[j]),double(m.radQL[j]),double(m.radPL[j]),double(m.radQR[j]),
          double(m.radPR[j]),double(m.radiationMagnitude[j]),double(m.baseQL[j]),double(m.basePL[j]),
          double(m.baseQR[j]),double(m.basePR[j]),double(m.portOmega[j]),double(m.portInverse[j])})
        result.coefficientsFinite=result.coefficientsFinite&&std::isfinite(value);
      result.passed=result.passed&&m.omega[j]>0&&m.loss[j]>=0&&m.damper[j]>=0&&m.damp[j]>=0&&m.damp[j]<=1;
    }
    result.maxStringComplianceError=std::max(result.maxStringComplianceError,
      std::abs(st.compliance-compliance)/std::max(1e-30,std::abs(compliance)));
  }
  for(size_t ki=0;ki<piano.keys.size();++ki){
    const auto& key=piano.keys[ki];const int n=static_cast<int>(ki)+21;
    const int count=n<=31?1:n<=43?2:3;
    result.passed=result.passed&&keyStrings[ki]==count&&key.strings.size()==static_cast<size_t>(count);
    const double expected=contactCompliance[ki]+piano.dt*piano.dt/(2*key.mass);
    result.maxContactComplianceError=std::max(result.maxContactComplianceError,
      std::abs(key.contactCompliance-expected)/std::max(1e-30,std::abs(expected)));
  }
  for(const auto& port:piano.unisonPorts){
    result.unisonMembership=result.unisonMembership&&port.count>=1&&port.count<=3&&
      port.modes.size()==static_cast<size_t>(port.count)&&std::isfinite(port.coefficient)&&
      port.coefficient>=0&&double(port.coefficient)*port.count<=1+1e-7;
    for(size_t lane=0;lane<port.modes.size();++lane){
      const auto [si,j]=port.modes[lane];
      if(si<0||si>=static_cast<int>(membership.size())||j<0||j>=static_cast<int>(membership[si].size())){
        result.unisonMembership=false;continue;
      }
      ++membership[si][j];const auto& m=piano.strings[si].m;
      result.unisonMembership=result.unisonMembership&&!m.polarization[j]&&
        port.velocityState[lane]==&m.p[j]&&port.omega[lane]==m.omega[j]&&
        port.inverseOmega[lane]==static_cast<float>(1.0/m.omega[j]);
    }
  }
  for(size_t si=0;si<membership.size();++si)for(size_t j=0;j<membership[si].size();++j)
    result.unisonMembership=result.unisonMembership&&membership[si][j]==(piano.strings[si].m.polarization[j]?0:1);
  size_t row=0;
  for(const auto& group:piano.unisonGroups)for(size_t i=0;i<group.coefficient.size();++i){
    if(row>=piano.unisonPorts.size()){result.groupCache=false;continue;}
    const auto& port=piano.unisonPorts[row++];
    result.groupCache=result.groupCache&&group.count==port.count&&group.coefficient[i]==port.coefficient;
    for(int lane=0;lane<port.count;++lane)
      result.groupCache=result.groupCache&&group.velocity[lane]+i==port.velocityState[lane]&&
        group.omega[lane][i]==port.omega[lane]&&group.inverse[lane][i]==port.inverseOmega[lane];
  }
  result.groupCache=result.groupCache&&row==piano.unisonPorts.size();
  result.passed=result.passed&&result.keys==88&&result.strings==230&&result.board==475&&
    result.modes==result.expectedModes&&result.bothPolarizations&&result.unisonMembership&&
    result.groupCache&&result.coefficientsFinite&&result.maxStringComplianceError<=1e-12&&
    result.maxContactComplianceError<=1e-12&&result.maxRotationNormExcess<=0;
  return result;
}
'''

def resolution_physics_template():
    source=precision.PHYSICS_TEMPLATE
    source=replace(source,'bool finiteStates(const Piano& piano) {',TOPOLOGY+'\nbool finiteStates(const Piano& piano) {')
    source=replace(source,'  double maxDrift=0,finalRatio=1,rotationNormMinusOne=0;',
                   '  double maxDrift=0,finalRatio=1,rotationNormMinusOne=0,minimumRatio=1,maximumRatio=1;')
    source=replace(source,'        result.finalRatio=current/initial;',
    '''        result.finalRatio=current/initial;
            result.minimumRatio=std::min(result.minimumRatio,result.finalRatio);
            result.maximumRatio=std::max(result.maximumRatio,result.finalRatio);''')
    start=source.index('    const bool topologyPassed=')
    end=source.index('    std::cout<<std::boolalpha',start)
    source=source[:start]+'''    const auto contactTopology=topology(contactPiano),bridgeTopology=topology(bridgePiano);
        const bool topologyPassed=contactTopology.passed&&bridgeTopology.passed;
        double maxFreeEnergyRatio=1,maxFreeEnergyLoss=0;
        for(const auto& result:freeResults){
          maxFreeEnergyRatio=std::max(maxFreeEnergyRatio,result.maximumRatio);
          maxFreeEnergyLoss=std::max(maxFreeEnergyLoss,1-result.minimumRatio);
        }
        const bool freeNoInjection=freeFinite&&maxFreeEnergyRatio<=1+5e-6;
        const bool freeBoundedLoss=freeFinite&&maxFreeEnergyLoss<=.05;
        const bool boundedFloatLossEligible=topologyPassed&&contactPassed&&bridgePassed&&freeNoInjection&&freeBoundedLoss;
        // Keep the strict conservation verdict intact; eligibility is a separate,
        // explicitly lossy engineering screen, never a conservation claim.
        const bool passed=topologyPassed&&contactPassed&&bridgePassed&&freePassed;
    '''+source[end:]
    source=replace(source,'    std::cout<<"{\\"passed\\":"<<passed<<",\\"topology\\":{\\"passed\\":"<<topologyPassed',
    '''    std::cout<<"{\\"passed\\":"<<passed<<",\\"bounded_float_loss_eligible\\":"<<boundedFloatLossEligible
          <<",\\"strict_free_conservation_passed\\":"<<freePassed<<",\\"topology\\":{\\"passed\\":"<<topologyPassed''')
    source=replace(source,'      <<",\\"unison_groups\\":"<<contactPiano.unisonGroups.size()<<"}"',
    '''      <<",\\"unison_groups\\":"<<contactPiano.unisonGroups.size()
          <<",\\"primary_cap\\":@PRIMARY_CAP@,\\"secondary_cap\\":@SECONDARY_CAP@"
          <<",\\"expected_modes\\":"<<contactTopology.expectedModes
          <<",\\"primary_modes\\":"<<contactTopology.primaryModes<<",\\"secondary_modes\\":"<<contactTopology.secondaryModes
          <<",\\"both_polarizations_every_string\\":"<<contactTopology.bothPolarizations
          <<",\\"unison_membership_valid\\":"<<contactTopology.unisonMembership
          <<",\\"group_cache_valid\\":"<<contactTopology.groupCache
          <<",\\"all_coefficients_finite\\":"<<contactTopology.coefficientsFinite
          <<",\\"max_string_compliance_relative_error\\":"<<contactTopology.maxStringComplianceError
          <<",\\"max_contact_compliance_relative_error\\":"<<contactTopology.maxContactComplianceError
          <<",\\"max_rotation_norm_excess\\":"<<contactTopology.maxRotationNormExcess<<"}"''')
    source=replace(source,'    std::cout<<",\\"energy_drift_tolerance\\":1e-3,\\"cases\\":[";',
    '''    std::cout<<",\\"energy_drift_tolerance\\":1e-3,\\"no_energy_injection_passed\\":"<<freeNoInjection
          <<",\\"bounded_numerical_loss_passed\\":"<<freeBoundedLoss
          <<",\\"maximum_energy_ratio_over_all_steps\\":"<<maxFreeEnergyRatio
          <<",\\"maximum_energy_loss_fraction\\":"<<maxFreeEnergyLoss
          <<",\\"energy_injection_tolerance\\":5e-6,\\"numerical_loss_fraction_tolerance\\":0.05,\\"cases\\":[";''')
    source=replace(source,'      std::cout<<",\\"final_energy_ratio\\":";printNumber(result.finalRatio);',
    '''      std::cout<<",\\"final_energy_ratio\\":";printNumber(result.finalRatio);
          std::cout<<",\\"minimum_energy_ratio\\":";printNumber(result.minimumRatio);
          std::cout<<",\\"maximum_energy_ratio\\":";printNumber(result.maximumRatio);''')
    return source


def timing(source):
    source=replace(source,'#include <chrono>','#include <chrono>\n#include <ctime>')
    source=replace(source,'auto start=std::chrono::steady_clock::now();size_t next=0;',
                   'auto cpuStart=std::clock();auto start=std::chrono::steady_clock::now();size_t next=0;')
    source=replace(source,'double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();',
                   'double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();double processCpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;')
    return replace(source,'<<p.energy()<<"}";',r'<<p.energy()<<",\"process_cpu_seconds\":"<<processCpu<<"}";')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(command,prefix,allow_failure=False):
    call=subprocess.run([str(x) for x in command],text=True,capture_output=True,timeout=180)
    Path(str(prefix)+'.stdout.txt').write_text(call.stdout)
    Path(str(prefix)+'.stderr.txt').write_text(call.stderr)
    if call.returncode and not allow_failure:raise RuntimeError(f'Command exited {call.returncode}: {command[0]}; see {prefix}')
    return call.stdout,call.returncode


def harmonic_difference(reference,candidate,rate,note,model):
    a,b=int(.16*rate),int(.56*rate)
    frequencies,pa=precision.spectrum(reference[a:b],rate)
    _,pb=precision.spectrum(candidate[a:b],rate)
    key=next(row for row in model['keys'] if row['midi']==note)
    rows=[]
    for partial in range(1,65):
        center=partial*key['fundamental_hz']*np.sqrt((1+key['B']*partial*partial)/(1+key['B']))
        if center>19000:break
        width=max(8.,.002*center)
        mask=(frequencies>=center-width)&(frequencies<=center+width)
        ea,eb=float(pa[mask].sum()),float(pb[mask].sum())
        rows.append({'partial':partial,'center_hz':float(center),'control_band_db_relative_total':precision.db_ratio(ea,pa.sum()),
                     'candidate_minus_control_db':precision.db_ratio(eb,ea)})
    audible=[row for row in rows if row['control_band_db_relative_total']>=-40]
    return {'window_seconds':[.16,.56],'band_half_width':'max(8Hz,.002*center); inharmonic centers from unchanged authored key parameters',
            'max_abs_change_db_control_bands_above_minus40db':max((abs(row['candidate_minus_control_db']) for row in audible),default=0.),'partials':rows}


def difference(reference,candidate,rate,note,model):
    result=precision.compare(reference,candidate,rate,note)
    if note is not None:
        result['harmonics']=harmonic_difference(reference,candidate,rate,note,model)
        times=np.array([.75,.85,.95,1.05]);slopes=[]
        for x in (reference,candidate):
            levels=[10*np.log10(max(np.mean(x[int((t-.04)*rate):int((t+.04)*rate)]**2),1e-30)) for t in times]
            slopes.append(float(np.polyfit(times,levels,1)[0]))
        result['release_decay_slope_db_per_second']={'control':slopes[0],'candidate':slopes[1],'change':slopes[1]-slopes[0],
            'limits':'Short whole-signal release-energy slope; not independently fitted modal decay.'}
    # Conservative engineering screens identify conspicuous losses; a pass is
    # never an inaudibility verdict. No gains, model parameters or EQ are fitted.
    reasons=[]
    if abs(result['rms_change_db'])>1:reasons.append('whole-file energy shift exceeds1dB')
    if note is not None:
        if result['harmonics']['max_abs_change_db_control_bands_above_minus40db']>3:reasons.append('resolved harmonic above-40dB changes more than3dB')
        if max(abs(row['energy_change_db']) for row in result['attack_windows'].values())>1:reasons.append('an attack window changes more than1dB')
        if abs(result['dominant_fundamental_peak']['difference_cents'])>2:reasons.append('dominant fundamental peak shifts more than2cents')
    if max(abs(row['balance_change_db']) for row in result['stereo_windows'].values())>.5:reasons.append('stereo balance shifts more than0.5dB')
    result['engineering_screen']={'rejected':bool(reasons),'reasons':reasons,
        'limits':'Conservative triage only. Nulls can reflect phase; screens cannot prove audibility or inaudibility.'}
    return result


def export_listening(folder,audio,labels):
    case_order=['C2soft','C4hard','C6hard','music_prefix'];gap=np.zeros((9600,2));rate=48000
    raw={label:np.concatenate([piece for case in case_order for piece in (audio[label,case],gap)]) for label in labels}
    gains={label:.08/max(np.sqrt(np.mean(x*x)),1e-30) for label,x in raw.items()}
    shared=(10**(-2/20))/max(np.max(np.abs(x*gains[label])) for label,x in raw.items())
    exports={};rendered={}
    for label,x in raw.items():
        samples=(x*gains[label]*shared).astype(np.float32);rendered[label]=samples
        path=folder/f'listening-{label}.wav';wavfile.write(path,rate,samples)
        exports[label]={'file':str(path),'sha256':sha(path),'whole_file_rms_gain':float(gains[label]),'shared_sample_peak_gain':float(shared),
                        'format':'float32 stereo WAV; lossless PCM','case_order':case_order,'segment_starts_seconds':[0,1.4,2.8,4.2],
                        'processing':'Whole-file RMS matching and shared sample-peak ceiling only. No EQ, room, per-note gain or time alignment.'}
    pairs={}
    for label in labels:
        if label=='full_f32':continue
        sequence=np.concatenate([rendered['full_f32'],np.zeros((24000,2),np.float32),rendered[label]])
        path=folder/f'full-then-{label}.wav';wavfile.write(path,rate,sequence)
        pairs[label]={'file':str(path),'sha256':sha(path),'order':['full_f32',label],'second_start_seconds':len(rendered['full_f32'])/rate+.5}
    return {'versions':exports,'pairs':pairs,'limits':'Labeled short dry matches; no blind listening or audibility conclusion. All source renders also retained without matching.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'out/full-precision-optimization/hot_f32_biased.cpp')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'out/full-resolution-optimization')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-resolution.json')
    parser.add_argument('--compiler',default='g++')
    parser.add_argument('--repeats',type=int,default=2)
    args=parser.parse_args()
    if not 1<=args.repeats<=3:parser.error('Use one to three bounded interleaved repeats')
    source=args.source.read_text()
    if sha(args.source)!=PINNED_FLOAT_SOURCE:parser.error('Float control source hash changed; freeze and review a new control first')
    folder=args.output_dir.resolve();folder.mkdir(parents=True,exist_ok=True)
    calibration=args.source.parent/'calibration.h'
    if sha(calibration)!=PINNED_CALIBRATION:parser.error('Frozen calibration hash changed')
    shutil.copyfile(calibration,folder/'calibration.h')
    template=resolution_physics_template();(folder/'physics-template.cpp.in').write_text(template)
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    caps={'full_f32':(320,48),'cap128_32':(128,32),'cap64_24':(64,24),'cap32_16':(32,16)}
    result={'schema_version':1,'control_source_sha256':sha(args.source),'calibration_sha256':sha(calibration),'tool_sha256':sha(Path(__file__)),
            'precision_analysis_helper_sha256':sha(ROOT/'tools/probe_full_precision.py'),'physics_template_sha256':hashlib.sha256(template.encode()).hexdigest(),
            'compiler':subprocess.check_output([args.compiler,'--version'],text=True).splitlines()[0],'platform':platform.platform(),'flags':flags,
            'repeats':args.repeats,'sample_rate':48000,'variants':{},'cases':{},
            'limits':'Resolution experiment on frozen same-f32 control; no recordings, held-out data, physical parameter fitting, static compensation or canonical edits. All strings, both polarizations, full board, nonlinear contact and reciprocal feedback remain. Smaller modal caps change the model and may be audible. Shared-host CPU timings are not Reason or realtime validation.'}
    for label,(primary,secondary) in caps.items():
        candidate=replace(source,'int cap=pol==0?320:48;',f'int cap=pol==0?{primary}:{secondary};') if label!='full_f32' else source
        path=folder/f'{label}.cpp';path.write_text(candidate)
        (folder/f'{label}.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),candidate.splitlines(True),fromfile='full-f32-control.cpp',tofile=label+'.cpp')))
        timed=folder/f'{label}.timed.cpp';timed.write_text(timing(candidate));binary=folder/label
        run([args.compiler,*flags,timed,'-o',binary],folder/f'{label}-compile')
        stdout,code=run([binary,'--self-test'],folder/f'{label}-strict-original-selftest',True)
        original_selftest=json.loads(stdout)
        probe=folder/f'{label}-physics.cpp';probe.write_text(template.replace('@SOURCE@',str(path)).replace('@PRIMARY_CAP@',str(primary)).replace('@SECONDARY_CAP@',str(secondary)))
        pbinary=folder/f'{label}-physics';run([args.compiler,*flags,probe,'-o',pbinary],folder/f'{label}-physics-compile')
        physical=json.loads(run([pbinary],folder/f'{label}-physics-run')[0])
        result['variants'][label]={'caps':[primary,secondary],'source_sha256':sha(path),'timed_source_sha256':sha(timed),'binary_sha256':sha(binary),
            'source_file':str(path),'original_strict_selftest':original_selftest,'original_strict_selftest_exit':code,
            'physics':physical,'bounded_float_physics_eligible':physical['bounded_float_loss_eligible'],'runs':[]}
        print('prepared',label,'modes',physical['topology']['string_modes'],'boundedphysics',physical['bounded_float_loss_eligible'],flush=True)
    control_free=result['variants']['full_f32']['physics']['free_oscillator']
    for label,row in result['variants'].items():
        row['free_numerical_loss_identical_to_full_control']=row['physics']['free_oscillator']==control_free
        if not row['free_numerical_loss_identical_to_full_control']:raise ValueError('Cap experiment changed standalone float rotation behavior')
    cases={}
    for label,note,velocity in [('C2soft',36,40),('C4hard',60,93),('C6hard',84,93)]:
        event=folder/f'{label}.events';event.write_text(f'.01 on {note} {velocity}\n.65 off {note} 0\n');cases[label]=(event,1.2,note)
    score=ROOT/'Research/GrandPianoV2/scores/01_nocturne.events'
    music=folder/'music-prefix.events';music.write_text(''.join(line+'\n' for line in score.read_text().splitlines() if line and not line.startswith('#') and float(line.split()[0])<1))
    cases['music_prefix']=(music,1.,None);result['authored_score_sha256']=sha(score)
    audio={};model=None
    # Reverse traversal on the second repeat; retain each CPU sample and spread.
    for case,(events,duration,note) in cases.items():
        case_row={'events_file':str(events),'events_sha256':sha(events),'duration_seconds':duration,'note':note,'variants':{}};result['cases'][case]=case_row
        for repeat in range(args.repeats):
            order=list(caps) if repeat%2==0 else list(reversed(caps))
            for label in order:
                output=folder/f'{label}-{case}-{repeat}.wav';command=[folder/label,'--events',events,'--output',output,'--sample-rate','48000','--duration',str(duration)]
                if model is None and label=='full_f32':command+=['--dump-model',folder/'full-model.json']
                metrics=json.loads(run(command,folder/f'{label}-{case}-{repeat}')[0])
                top=result['variants'][label]['physics']['topology']
                if (metrics['string_count'],metrics['string_modes'],metrics['board_modes'],metrics['nonfinite_samples'])!=(230,top['string_modes'],475,0):raise ValueError('Topology/nonfinite render failure')
                result['variants'][label]['runs'].append({'case':case,'repeat':repeat,**metrics})
                if repeat==0:
                    rate,x=precision.load(output);assert rate==48000;audio[label,case]=x
                    case_row['variants'][label]={'render_metrics':metrics,'audio_file':str(output),'audio_sha256':sha(output)}
                if model is None:model=json.loads((folder/'full-model.json').read_text())
                print('rendered',case,label,repeat,metrics['process_cpu_seconds'],flush=True)
        for label in caps:
            runs=[r['process_cpu_seconds'] for r in result['variants'][label]['runs'] if r['case']==case]
            case_row['variants'][label]['cpu_seconds']={'samples':runs,'median':statistics.median(runs),'min':min(runs),'max':max(runs)}
            case_row['variants'][label]['speedup_vs_same_full_f32']=case_row['variants']['full_f32']['cpu_seconds']['median']/statistics.median(runs)
            if label!='full_f32':case_row['variants'][label]['difference']=difference(audio['full_f32',case],audio[label,case],48000,note,model)
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    result['listening_exports']=export_listening(folder,audio,caps)
    for label,row in result['variants'].items():
        row['speedup_geomean_four_cases']=float(np.exp(np.mean(np.log([r['variants'][label]['speedup_vs_same_full_f32'] for r in result['cases'].values()]))))
        row['rejected_cases']=[name for name,case in result['cases'].items() if label!='full_f32' and case['variants'][label]['difference']['engineering_screen']['rejected']]
        row['decision']='control' if label=='full_f32' else 'reject_by_engineering_screen' if row['rejected_cases'] else 'requires_matched_listening; not_adopted'
    result['control_source_unchanged']=sha(args.source)==PINNED_FLOAT_SOURCE
    result['canonical_sources_edited']=False
    args.report.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'report':str(args.report),'variants':{k:{f:v[f] for f in ('speedup_geomean_four_cases','decision','rejected_cases')} for k,v in result['variants'].items()}},indent=2))


if __name__=='__main__':main()
