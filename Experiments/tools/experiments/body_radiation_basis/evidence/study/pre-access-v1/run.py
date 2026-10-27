from pathlib import Path
import datetime,hashlib,json,subprocess,time,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def inputs():
    notes=['A0','C1','A1','C2','D#2','A2','C3','D#3','C4','D#4','A4','C5','D#5','A5','C6','C7','C8']
    cases=[]
    for note in notes:
        for layer in [4,12]:
            ident=f'{note}v{layer}';old=ROOT/f'out/full-causal-radiation/v1/pilot/{ident}/trace.f64le'
            trace=old if old.exists() else ROOT/f'out/full-radiation-crossover/train34/producer/renders/{ident}/trace.f64le'
            cases.append({'id':ident,'trace':str(trace)})
    return cases
def freeze():
    assert not (OUT/'freeze.json').exists()
    sources=[OUT/'replay.cpp',OUT/'run.py'];co=ROOT/'out/full-performance-click/capture/board-coefficients.f64le'
    protocol={'schema_version':1,'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Private475mode board-only reconstruction and static6basis reachability infrastructure; no fit, physicalnetwork rerender, referencePCM access or candidate listening audio.',
      'pressure_or_trace_access_before_freeze':False,'basis':{'centers_hz':[55,140,350,900,2400,6500],'formula':'For adjacent log centers, hi=.5-.5*cos(pi*t), lo=1-hi; all others0. Constant unit first/last basis outside endpoint centers. C1 smooth nonnegative partition of unity. Frequency uses actual board w/(2pi).','channels':'Same6scalars for LR; preserve signed existing mic weights. Weight complete modalacceleration incl instantaneous force.','test_alpha':[.5,.75,1,1.25,1.5,2],'limits':['6basis span rawboardmic only. Recomputing nonlinear empirical target/abs(H) string corrections is NOT represented.','No new poles, decay, physicalparts, stereo phase, body energy or acoustic accuracy established.','Global positive alpha chosen only in later separately authorized/frozen fit; no alpha selection in this study.']},
      'rate':48000,'frames_per_case':182400,'modes':475,'trace_columns':{'rawBoard':[2,3],'totalSchurForce':[12,13,14]},'recurrence':'Oldfloatq/p stores and doublecoeff arithmetic; serial3force sum; serial475modalpressure sum, completeacc=-w*w*q-2*sigma*w*p+force. Zero state each independent case.',
      'output':{'dtype':'littleendianfloat64','columns':['directL','directR']+[f'b{b}{ch}' for b in range(6) for ch in ['L','R']],'total_bytes_34':34*182400*14*8,'raw_only':True,'hp24':'Streamingcheck only, pole=exp(-2pi24/48000), zero state, identical LR, no retained HP duplicate.'},
      'stages':{'witnesses':[f'{n}v{v}' for n in ['A0','C3','C6'] for v in [4,12]],'remaining':'Only after all6 witnesses pass, same frozen source/protocol processes remaining28. Stop on any failure; retain failures, no silent retry.','chunk_checks':'Each witness replayed canonical64 and alternate1/3/17/64/129/7; byteidentical rawoutputs and finalstates required. Alternate duplicates deleted only after hashes recorded.'},
      'gates':{'direct':'Require bitidentical captured rawBoard (all364800samples percase). Any mismatch stops study.','partition':'Perframe absolute bound (8gamma475+32eps)*sum_abs_modal_contribution; ratio<=1. gamma475=475eps/(1-475eps).','positive_recombination':'Fixed testalpha directweightedmic vs recombinedsixbasis; bound2*(8gamma475+32eps)*sum_abs_modal_contribution.','hp24':'Absolute bound32gamma475*max_abs_modal_sum +128eps*max_abs_HP; no relative-only cancellationtest.','finite':'Allrawoutputs finite; basis[0,1], sum exactly1 per475modes; everybasis has support.','gram':'Synthetic anti-phase/coherentand actualwitness6x6Gram with offdiagonal terms; alphaTGramalpha vs explicit recombined energy <=256eps*sumabsolute terms, eigenPSDwithin256eps*trace; no reference measurement.','budget':'Retained rawbinaryoutputs <=1GiB;34actualoutputs total694579200bytes.'},
      'compile':['g++','-std=c++17','-O3','-fno-builtin','-ffp-contract=off',str(OUT/'replay.cpp'),'-o',str(OUT/'replay')],'sources':{str(p):sha(p) for p in sources},'coefficients':{'path':str(co),'sha256':sha(co)},'cases':inputs()}
    dump(OUT/'protocol.json',protocol);dump(OUT/'freeze.json',{'at_utc':protocol['frozen_at_utc'],'protocol_sha256':sha(OUT/'protocol.json'),'sources':protocol['sources'],'coefficients':protocol['coefficients']})
def gramcheck(x):
    a=np.array([.5,.75,1,1.25,1.5,2]);g=x.T@x;energy=float(np.sum((x@a)**2));projected=float(a@g@a);scale=float(np.sum(abs(g)*abs(a[:,None]*a[None,:])));bound=256*np.finfo(float).eps*max(scale,1e-300)
    ev=np.linalg.eigvalsh(g);psdbound=256*np.finfo(float).eps*max(float(np.trace(g)),1e-300)
    return {'direct_energy':energy,'gram_energy':projected,'error':abs(energy-projected),'bound':bound,'min_eigenvalue':float(ev[0]),'psd_bound':psdbound,'pass':abs(energy-projected)<=bound and ev[0]>=-psdbound}
def run():
    freezeobj=json.loads((OUT/'freeze.json').read_text());p=json.loads((OUT/'protocol.json').read_text());assert sha(OUT/'protocol.json')==freezeobj['protocol_sha256']
    for f,h in p['sources'].items():assert sha(f)==h
    assert sha(p['coefficients']['path'])==p['coefficients']['sha256']
    assert not (OUT/'result.json').exists();assert not (OUT/'renders').exists();subprocess.run(p['compile'],check=True)
    synthetic=np.arange(1,513,dtype=float)/512;x=np.column_stack([synthetic,-synthetic,synthetic*.5,synthetic[::-1],np.sin(synthetic),np.zeros_like(synthetic)])
    synth=gramcheck(x);dump(OUT/'synthetic-gram.json',synth);assert synth['pass']
    ordered=sorted(p['cases'],key=lambda c:(c['id'] not in p['stages']['witnesses'],p['stages']['witnesses'].index(c['id']) if c['id'] in p['stages']['witnesses'] else p['cases'].index(c)))
    results=[];beg=time.monotonic();stage='witnesses';failed=None
    for c in ordered:
        if c['id'] not in p['stages']['witnesses']:stage='remaining'
        d=OUT/'renders'/c['id'];d.mkdir(parents=True);output=d/'basis.f64le';stats=d/'stats.json';tick=time.monotonic()
        subprocess.run([str(OUT/'replay'),p['coefficients']['path'],c['trace'],str(output),str(stats),'canonical'],check=True)
        s=json.loads(stats.read_text());record={'id':c['id'],'stage':stage,'trace_sha256':sha(c['trace']),'output_sha256':sha(output),'stats_sha256':sha(stats),'wall_seconds':time.monotonic()-tick,'bytes':output.stat().st_size}
        gates={'frames':s['frames']==p['frames_per_case'],'direct_bitexact':s['direct_max_error']==0 and s['direct_nonidentical_samples']==0,'partition':s['partition_error_over_bound']<=1,'weighted':s['positive_weight_error_over_bound']<=1,'hp':s['hp24_partition_max_error']<=s['hp24_partition_bound'],'basis':s['basis_min']>=0 and s['basis_max']<=1 and s['basis_partition_max_error']==0 and min(s['basis_support_modes'])>0,'finite':s['nonfinite']==0,'bytes':record['bytes']==p['frames_per_case']*14*8}
        if c['id'] in p['stages']['witnesses']:
            alt=d/'alternate.f64le';ast=d/'alternate-stats.json';subprocess.run([str(OUT/'replay'),p['coefficients']['path'],c['trace'],str(alt),str(ast),'alternate'],check=True)
            record['alternate_output_sha256']=sha(alt);record['alternate_stats_sha256']=sha(ast);gates['chunks']=record['output_sha256']==record['alternate_output_sha256'] and s==json.loads(ast.read_text());alt.unlink()
            raw=np.memmap(output,dtype='<f8',mode='r',shape=(p['frames_per_case'],14));gc=[gramcheck(np.asarray(raw[:,2+ch::2])) for ch in [0,1]];del raw;record['coherent_gram']=gc;gates['gram']=all(g['pass'] for g in gc)
        record['gates']=gates;record['pass']=all(gates.values());results.append(record);dump(d/'receipt.json',record);print(json.dumps({'id':c['id'],'pass':record['pass'],'wall_seconds':record['wall_seconds']}),flush=True)
        if not record['pass']:failed=c['id'];break
        if len(results)==6:dump(OUT/'witness-stage.json',{'pass':True,'cases':results,'no_reference_or_fit':True})
    totalbytes=sum(r['bytes'] for r in results);result={'frozen_protocol_sha256':sha(OUT/'protocol.json'),'producer_source_sha256':sha(OUT/'replay.cpp'),'producer_binary_sha256':sha(OUT/'replay'),'synthetic_gram_sha256':sha(OUT/'synthetic-gram.json'),'cases':results,'pass':failed is None and len(results)==34 and totalbytes<2**30,'failed_case':failed,'count':len(results),'total_output_bytes':totalbytes,'wall_seconds':time.monotonic()-beg,'limits':p['basis']['limits']};dump(OUT/'result.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)
    manifest={str(f.relative_to(OUT)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='manifest.json'};dump(OUT/'manifest.json',manifest)
if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ['freeze','run']:raise SystemExit('usage: run.py freeze|run')
    freeze() if sys.argv[1]=='freeze' else run()
