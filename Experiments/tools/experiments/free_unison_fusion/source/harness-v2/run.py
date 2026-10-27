#!/usr/bin/env python3
"""Current full API fusion: compile/freeze only until explicit root receipts."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,statistics,subprocess,time

ROOT=Path('/workspace/virtual-instrument-keyra');OUT=Path(__file__).resolve().parent
CANDIDATE=OUT.parent/'v2'
FLAGS=['-std=c++17','-O3','-DNDEBUG','-fno-exceptions','-fno-rtti','-fno-builtin','-ffp-contract=off','-DKEYRA_FULL_PRESSURE_SIMD=0','-DKEYRA_FULL_FAST_CONTACT=1','-DKEYRA_FULL_MECHANISM_CACHE=1','-DKEYRA_FULL_MODEL_PROFILE=0','-fopenmp-simd','-DKEYRA_FULL_FREE_UNISON_SIMD=1']
FILES=['src/full_instrument/FullInstrument.cpp','src/full_instrument/PreparedModel.h','src/full_instrument/PreparedCalibration.h','src/full_instrument/SelectedModel.h','src/full_instrument/MechanismBodyCache.h','include/keyra/FullInstrument.h','include/keyra/physics/ContactSolver.h','include/keyra/physics/MechanismExciter.h','include/keyra/physics/StrikeController.h']
SOURCE=['run.py','harness.cpp','ObserverCapture.h','state_snapshot.inc','inventory.inc']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text())
def write(p,v):
    p=Path(p)
    if p.exists():raise ValueError('Refuse overwrite '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def once(s,a,b):
    if s.count(a)!=1:raise ValueError('Nonunique instrumentation '+a)
    return s.replace(a,b,1)
def verify(p):
    for r in p:
        if sha(r['path'])!=r['sha256']:raise ValueError('Frozen identity changed '+r['path'])
def prepare():
    if (OUT/'protocol.json').exists():raise ValueError('Already frozen')
    if not (CANDIDATE/'protocol.json').exists():raise ValueError('Wait for candidate source-only protocol freeze')
    if sha(CANDIDATE/'protocol.json')!='7b6414d12195f9d6fe936deaaa93135463f0107ee4d1d2dbe268fd56c5850e37':raise ValueError('Expected explicit FINAL candidate freeze')
    candidate=read(CANDIDATE/'protocol.json');verify(candidate['sources'])
    version=subprocess.check_output(['g++','--version'],text=True).splitlines()[0]
    if '14.' not in version:raise ValueError('Expected GCC14 native compiler')
    current=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if current!='0227028b7e86fe3f09d1381fa9dcb860080f22da':raise ValueError('Unexpected current source commit')
    if sha(ROOT/'src/full_instrument/PreparedModel.h')!='edae57fb1bad84a9e632961726d3ab60b3c5c27474b0f1194bcc89462384ee36':raise ValueError('Current model identity')
    inputs=[rec(ROOT/x) for x in FILES]+[rec(CANDIDATE/'protocol.json'),rec(CANDIDATE/'source-manifest.json'),rec(ROOT/'tools/probe_full_backend_budget.py'),rec(ROOT/'tools/probe_full_radiation_simd.py')]+candidate['sources']
    for variant in ('baseline','candidate'):
        dest=OUT/'build'/variant;source=CANDIDATE/variant
        for name in FILES:
            p=source/name;target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
            if (variant=='baseline' or name!='src/full_instrument/PreparedModel.h') and p.read_bytes()!=(ROOT/name).read_bytes():raise ValueError('Unexpected baseline/shared source difference '+str(p))
            text=p.read_text()
            if name in ('include/keyra/FullInstrument.h','include/keyra/physics/MechanismExciter.h','include/keyra/physics/StrikeController.h'):
                text=once(text,'private:','public: // copied diagnostic access; layout unchanged')
            if name.endswith('FullInstrument.cpp'):
                text=once(text,'#include "SelectedModel.h"','#include "SelectedModel.h"\n#if KEYRA_FUSION_CORRECTNESS\n#include "ObserverCapture.h"\n#endif')
                text=once(text,'    auto x=impl_->step();','    auto x=impl_->step();\n#if KEYRA_FUSION_CORRECTNESS\n    keyra_fusion_capture::capture(x);\n#endif')
                text+='\n#include "inventory.inc"\n#if KEYRA_FUSION_CORRECTNESS\n#include "state_snapshot.inc"\n#endif\n'
            target.write_text(text)
        if variant=='candidate':shutil.copyfile(source/'src/full_instrument/FreeUnisonFusion.h',dest/'src/full_instrument/FreeUnisonFusion.h')
    frozen=[rec(OUT/x) for x in SOURCE]+inputs+[rec(p) for p in sorted((OUT/'build').rglob('*')) if p.is_file()]
    p={'schema_version':1,'frozen_at_utc':now(),'scope':'SOURCE ONLY current default fullAPI exact fusion validation and later bounded paired timing; no model construction/step/render/timing performed by prepare.','source_commit':current,'compiler':version,'flags':FLAGS,'bindings':frozen,'candidate_source_protocol':rec(CANDIDATE/'protocol.json'),
      'correctness':{'sample_rates':[44100,48000,88200,96000],'cases':['music','repeats-pedal','dense-88-tail','silent-reset'],'length_seconds':[.64,.64,.4,.4],'callbacks':'Nominal64-frame boundaries, split at exact authored interior-frame events and five state checkpoints; no shifted events.','controls':'Current FullInstrumentConfig defaults, seed0x4b657972, pressureSIMDOFF fastcontactON mechanismcacheON OriginalControl profile0.','exact_requirements':['pre-HP/gain/width actual f64 stereo pressure everyframe','actual f32 stereo output everyframe','five deterministic padding-free original-state/coefficient checkpoints percase including controller/RNG, full mechanism ledgers and output filters','same event diagnostics and zero faults/unsafe/nonfinite','candidate prepare inventory valid with all17778modes covered once and alloriginalunisonrows scheduled'],'reset':'silent-reset has physical reset at0.20s; raw capture has independent absolute cursor and never overwrites on reset.','allocation_guard':'No new global allocator interposition. This experiment checks exact source scheduling; current allocation-free API tests remain separate.'},
      'performance':{'requires_correctness_pass':True,'sample_rates':[48000,96000],'pairs':[['baseline','candidate'],['candidate','baseline'],['baseline','candidate']],'cases':['music','repeats-pedal','dense-88-tail'],'frame_counts':[30720,30720,15360],'schedules':'Existing actualAPI budget frame/event sequences unchanged at both rates; all events64aligned.','timing':'CLOCK_THREAD_CPUTIME_ID and steadywall around eventdispatch+process only. Excludesprepare, inventory, snapshot, pressurecapture, audio/reportwrites and vectorbookkeeping. Separatepreprocessedbinary has no observer/snapshot symbols.','all_trials_retained':True,'discard_warmup_trials':False,'summary_percentile':'Sort each callbacklist, elementceil(p*(n-1)), p=.5/.95; maxandwallmisses retained.','host_scope':'Shared Linux GCC14 native, serial oneinstance/thread. No realtime/Reason/SDK/Recon/price claim.'},
      'authorization':'Each execution requires root receipt binding thisprotocolhash and actions correctness/performance. Performance additionallybinds a passedcorrectnessresult. No missinganswer/timeelapsed authorization.','adopted':False,'runtime_or_public_source_changes':False}
    write(OUT/'protocol.json',p)
    builds=[]
    for mode in ('correctness','performance'):
        for variant in ('baseline','candidate'):
            dest=OUT/'build'/variant;binary=dest/(mode+'-probe')
            cmd=['g++',*FLAGS,'-DKEYRA_FUSION_CORRECTNESS='+str(int(mode=='correctness')),'-DKEYRA_FUSION_CANDIDATE='+str(int(variant=='candidate')),'-I'+str(dest/'include'),'-I'+str(dest/'src/full_instrument'),'-I'+str(OUT),str(dest/'src/full_instrument/FullInstrument.cpp'),str(OUT/'harness.cpp'),'-o',str(binary)]
            call=subprocess.run(cmd,text=True,capture_output=True);(dest/(mode+'-compile.stdout.txt')).write_text(call.stdout);(dest/(mode+'-compile.stderr.txt')).write_text(call.stderr)
            if call.returncode:raise ValueError('Compilefailed '+mode+'/'+variant+': '+call.stderr)
            linked=subprocess.check_output(['ldd',str(binary)],text=True)
            if 'libgomp' in linked or 'libomp' in linked:raise ValueError('Unexpected OpenMPruntime')
            symbols=subprocess.check_output(['nm','-C',str(binary)],text=True)
            if mode=='performance' and ('keyra_fusion_snapshot' in symbols or 'keyra_fusion_capture::' in symbols):raise ValueError('Diagnosticcode inperformancebinary')
            builds.append({'mode':mode,'variant':variant,'command':cmd,'binary':rec(binary),'dynamic_dependencies':linked,'no_model_execution':True})
    verify(frozen);write(OUT/'build-receipt.json',{'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'builds':builds,'models_constructed':0,'model_frames':0,'model_timings':0});print('SOURCE ONLY frozen+compiled',flush=True)
def authorized(action):
    p=read(OUT/'protocol.json');build=read(OUT/'build-receipt.json');verify(p['bindings']);verify([build['protocol']]+[x['binary'] for x in build['builds']])
    auth=read(OUT/(action+'-authorization.json'))
    if action not in auth['actions'] or auth['protocol']!=rec(OUT/'protocol.json'):raise ValueError('Missing exactrootauthorization')
    if action=='performance':
        if auth['correctness_result']!=rec(OUT/'correctness-result.json') or read(OUT/'correctness-result.json')['pass'] is not True:raise ValueError('Correctnessnotpassed')
    return p,build
def invoke(mode,variant,rate,path):
    path.mkdir(parents=True,exist_ok=False);cmd=[str(OUT/'build'/variant/(mode+'-probe')),str(rate),str(path)]
    call=subprocess.run(cmd,text=True,capture_output=True,timeout=120);(path/'stdout.json').write_text(call.stdout);(path/'stderr.txt').write_text(call.stderr)
    if call.returncode:raise ValueError('Runtimefailure '+str(cmd)+': '+str(call.returncode))
    return read(path/'stdout.json')
def correctness():
    p,_=authorized('correctness');write(OUT/'correctness-started.json',{'started_at_utc':now(),'protocol':rec(OUT/'protocol.json')});start=time.monotonic();comparisons=[]
    for rate in p['correctness']['sample_rates']:
        outputs={v:invoke('correctness',v,rate,OUT/'correctness'/str(rate)/v) for v in ('baseline','candidate')}
        for case in p['correctness']['cases']:
            dirs={v:OUT/'correctness'/str(rate)/v for v in outputs};a=next(x for x in outputs['baseline']['cases'] if x['name']==case);b=next(x for x in outputs['candidate']['cases'] if x['name']==case)
            da={k:v for k,v in a.items() if k!='prepare_wall_seconds_excluded'};db={k:v for k,v in b.items() if k!='prepare_wall_seconds_excluded'}
            if da!=db:raise ValueError('Diagnosticdifference '+str(rate)+case)
            files=[case+'.f64le-pressure',case+'.f32le-planar']+[case+'-'+str(f)+'.state' for f in a['physical_state_checkpoints']]
            for name in files:
                x=dirs['baseline']/name;y=dirs['candidate']/name
                if x.read_bytes()!=y.read_bytes():raise ValueError('Exactparityfailed '+str(rate)+name)
            prep=read(dirs['candidate']/(case+'.prepare.json'))
            if prep['valid'] is not True:raise ValueError('Candidateinventoryinvalid')
            comparisons.append({'sample_rate':rate,'case':case,'files':[{'baseline':rec(dirs['baseline']/f),'candidate':rec(dirs['candidate']/f),'byte_identical':True} for f in files],'prepare_inventory':prep})
    verify(p['bindings']);write(OUT/'correctness-result.json',{'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'pass':True,'comparisons':comparisons,'wall_seconds':time.monotonic()-start,'adopted':False});print('Correctness exactpass',flush=True)
def performance():
    p,_=authorized('performance');write(OUT/'performance-started.json',{'started_at_utc':now(),'protocol':rec(OUT/'protocol.json')});runs=[]
    for rate in p['performance']['sample_rates']:
        for pair,order in enumerate(p['performance']['pairs']):
            for variant in order:
                folder=OUT/'performance'/str(rate)/('pair'+str(pair))/variant
                data=invoke('performance',variant,rate,folder);runs.append({'sample_rate':rate,'pair':pair,'variant':variant,'trace':rec(folder/'stdout.json'),'cases':data['cases']})
    comparisons=[]
    for rate in p['performance']['sample_rates']:
        for case in p['performance']['cases']:
            values={v:[next(c for c in r['cases'] if c['name']==case)['cpu_seconds_per_audio_second'] for r in runs if r['sample_rate']==rate and r['variant']==v] for v in ('baseline','candidate')}
            comparisons.append({'sample_rate':rate,'case':case,**values,'paired_speedups':[a/b for a,b in zip(values['baseline'],values['candidate'])],'median_cpu_reduction_fraction':1-statistics.median(values['candidate'])/statistics.median(values['baseline'])})
    verify(p['bindings']);write(OUT/'performance-result.json',{'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'runs':runs,'comparisons':comparisons,'all_trials_retained':True,'adopted':False});print('Performance alltrials retained',flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare','correctness','performance']);args=parser.parse_args()
    {'prepare':prepare,'correctness':correctness,'performance':performance}[args.action]()
