#!/usr/bin/env python3
"""One private six-weight body-only TRAIN fit; no reference PCM is opened.

freeze reads metadata only. run is separately authorized after reconstruction
passes; it computes coherent Grams, fits once, emits/scores all34 once. No
canonical write, physical synthesis, restarts, gain change or automatic adoption.
"""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time
import traceback
import numpy as np
import scipy
from scipy import ndimage, optimize, signal
from scipy.io import wavfile

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASIS=ROOT/'out/full-body-basis/v1'
REFERENCE=ROOT/'out/full-radiation-crossover/train34/reference-control.json'
HISTORY=ROOT/'out/full-radiation-crossover/train34/result.json'
FIRST_SIX=ROOT/'out/full-causal-radiation/v1/producer-receipt.json'
HELPER=ROOT/'out/full-radiation-crossover/train34/measure_references.py'
METRIC=ROOT/'tools/probe_full_causal_radiation_metrics.py'
OPERATOR=ROOT/'out/full-radiation-crossover/v1/postprocess.py'
FEATURES=ROOT/'References/GrandFullRange/combined_train_features.json'
SPLIT=ROOT/'References/GrandFullRange/split.json'
RATE=48000
FRAMES=182400
POLE=math.exp(-2*math.pi*24/RATE)
EARLY=((0.,.005),(.005,.020),(.020,.050),(.050,.100))
BANDS=((31.25,250.),(250.,1000.),(1000.,4000.),(4000.,12000.),(12000.,19000.))
TEST_ALPHA=np.array([.5,.75,1.,1.25,1.5,2.])
BOUNDS=(20*math.log10(.025),20*math.log10(40.))
OPTIONS={'maxiter':500,'maxfun':10000,'ftol':1e-12,'gtol':1e-7,'maxls':30}
EPS=np.finfo(float).eps

def now(): return datetime.now(timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def read(path): return json.loads(Path(path).read_text())
def record(path): return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def write(path,value):
    path=Path(path).resolve()
    if OUT not in path.parents or path.exists(): raise ValueError('New private output required: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def verify(records):
    for item in records:
        if sha(item['path'])!=item['sha256']: raise ValueError('Changed input: '+item['path'])
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value
def tools():
    # Import functions only. Do not call historical locked()/dependencies():
    # those recursively hash/open reference PCM, which this experiment forbids.
    metric=module(METRIC,'body_fit_frozen_metric')
    helper=module(HELPER,'body_fit_frozen_helper')
    operator=module(OPERATOR,'body_fit_frozen_gate_source')
    gate,gate_sha=operator.gate_function(metric,METRIC.read_text())
    return metric,helper,gate,gate_sha

def hp_compile():
    destination=OUT/'highpass.so'
    if destination.exists(): raise ValueError('Refuse existing HP binary')
    command=['g++','-std=c++17','-O3','-fno-builtin','-ffp-contract=off',
             '-shared','-fPIC',str(OUT/'highpass.cpp'),'-o',str(destination)]
    subprocess.run(command,check=True)
    library=ctypes.CDLL(str(destination))
    function=library.keyra_hp24
    pointer=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
    function.argtypes=[pointer,pointer,ctypes.c_size_t,ctypes.c_uint,ctypes.c_double]
    function.restype=ctypes.c_int
    def hp(value):
        original=np.asarray(value).shape
        x=np.ascontiguousarray(value,dtype=np.float64).reshape((original[0],-1))
        y=np.empty_like(x)
        if function(x,y,len(x),x.shape[1],POLE): raise ValueError('HP nonfinite/error')
        return y.reshape(original)
    return hp,{'command':command,'source':record(OUT/'highpass.cpp'),'binary':record(destination)}

def fft_basis(x):
    n=len(x)
    window=signal.windows.hann(n,sym=False)
    nfft=1<<int(math.ceil(math.log2(n*2)))
    z=np.fft.rfft(x*window[:,None,None],n=nfft,axis=0)
    f=np.fft.rfftfreq(nfft,1/RATE)
    normalization=2/(nfft*float(np.sum(window*window)))
    return f,z,normalization

def band_gram(f,z,normalization,lo,hi):
    df=f[1]-f[0]
    weights=np.clip((np.minimum(f+df/2,hi)-np.maximum(f-df/2,lo))/df,0,1)
    weights[0]*=.5
    weights[-1]*=.5
    selected=weights>0
    # Sum complex cross products across bins and both channels. Divide by2
    # for the frozen stereo-mean convention. All signed cross terms remain.
    values=z[selected]*np.sqrt(weights[selected,None,None]*normalization/2)
    values=values.transpose(0,2,1).reshape((-1,6))
    gram=np.real(values.conj().T@values)
    return (gram+gram.T)*.5

def fullwindow_gram(x):
    window=signal.windows.hann(len(x),sym=False)
    values=(x*window[:,None,None]).transpose(0,2,1).reshape((-1,6))
    gram=(values.T@values)/(2*float(np.sum(window*window)))
    return (gram+gram.T)*.5

def temporal_grams(x,times):
    samples=np.asarray(times,dtype=float)*RATE
    low=np.floor(samples).astype(int)
    high=np.minimum(low+1,len(x)-1)
    fraction=samples-low
    before=np.empty((len(times),6,6)); after=np.empty_like(before)
    for j in range(6):
        for k in range(j,6):
            product=np.mean(x[:,j,:]*x[:,k,:],axis=1)
            smooth=ndimage.uniform_filter1d(product,240,mode='nearest')
            before[:,j,k]=before[:,k,j]=smooth[low]
            after[:,j,k]=after[:,k,j]=smooth[high]
    return before,after,fraction

def build_grams(hp_basis,old,row):
    onset=old['baseline']['fixed_onset_frame']; gain=old['baseline']['fixed_gain']
    x=hp_basis[onset:]*gain
    reference=old['reference']; sustain=reference['sustain_power']
    early=[]; early_target=[]; early_full=[]
    for index,(a,b) in enumerate(EARLY):
        chunk=x[round(a*RATE):round(b*RATE)]
        f,z,normalization=fft_basis(chunk); full=fullwindow_gram(chunk)
        for band,target in zip(BANDS,reference['early'][index]['band_power']):
            early.append(band_gram(f,z,normalization,*band)); early_target.append(target);early_full.append(full)
    harmonic=[]; harmonic_target=[]; harmonic_locations=[];harmonic_full=[]
    for wi,(a,b) in enumerate(old['support']['late_windows_seconds']):
        chunk=x[round(a*RATE):round(b*RATE)]
        f,z,normalization=fft_basis(chunk);full=fullwindow_gram(chunk)
        for pi,part in enumerate(reference['late_harmonics'][wi]['partials']):
            if not part['included']: continue
            center=part['frequency_hz']; width=min(.38*row['f1_hz'],max(3/(b-a),.004*center))
            harmonic.append(band_gram(f,z,normalization,center-width,center+width))
            harmonic_target.append(part['power']); harmonic_locations.append([wi,pi]);harmonic_full.append(full)
    envelope=reference['late_envelope']; mask=np.asarray(envelope['included'],dtype=bool)
    times=np.asarray(envelope['times_seconds'])[mask]
    before,after,fraction=temporal_grams(x,times)
    if not harmonic or not np.any(mask): raise ValueError('Missing frozen metric support')
    return {'early_Q':np.asarray(early),'early_target':np.asarray(early_target),'early_full_Q':np.asarray(early_full),
            'harmonic_Q':np.asarray(harmonic),'harmonic_target':np.asarray(harmonic_target),
            'harmonic_full_Q':np.asarray(harmonic_full),
            'harmonic_locations':np.asarray(harmonic_locations,dtype=np.int64),
            'envelope_low_Q':before,'envelope_high_Q':after,'envelope_fraction':fraction,
            'envelope_target':np.asarray(envelope['rms'])[mask],
            'envelope_times':times,'envelope_mask':mask,
            'fixed_gain':np.asarray(gain),
            'power_floor':np.asarray(sustain*1e-10),
            'amplitude_floor':np.asarray(math.sqrt(sustain)*1e-5)}

def power(Q,alpha): return np.einsum('j,njk,k->n',alpha,Q,alpha)
def envelope_values(gram,alpha):
    p0=np.maximum(power(gram['envelope_low_Q'],alpha),0)
    p1=np.maximum(power(gram['envelope_high_Q'],alpha),0)
    fraction=gram['envelope_fraction']
    return (1-fraction)*np.sqrt(p0)+fraction*np.sqrt(p1)
def relative_check(left,right,floor):
    left=np.asarray(left,dtype=float); right=np.asarray(right,dtype=float)
    bound=5e-10*np.maximum(np.maximum(abs(left),abs(right)),floor)
    ratio=float(np.max(abs(left-right)/np.maximum(bound,1e-300)))
    return {'maximum_error_over_bound':ratio,'pass':bool(ratio<=1)}

def feature_parity(gram,features,alpha=TEST_ALPHA):
    early=[p for w in features['early'] for p in w['band_power']]
    harmonic=[features['late_harmonics'][wi]['partials'][pi]['power']
              for wi,pi in gram['harmonic_locations']]
    envelope=np.asarray(features['late_envelope']['rms'])[gram['envelope_mask']]
    checks={'early':relative_check(power(gram['early_Q'],alpha),early,float(gram['power_floor'])),
            'harmonic':relative_check(power(gram['harmonic_Q'],alpha),harmonic,float(gram['power_floor'])),
            'envelope':relative_check(envelope_values(gram,alpha),envelope,float(gram['amplitude_floor']))}
    psd=[]
    for name in ['early_Q','harmonic_Q','envelope_low_Q','envelope_high_Q']:
        Q=gram[name]; eigen=np.linalg.eigvalsh(Q)
        bound=4096*EPS*np.maximum(np.trace(Q,axis1=1,axis2=2),1e-300)
        ratio=float(np.max(np.maximum(-eigen[:,0],0)/bound))
        psd.append({'name':name,'negative_eigenvalue_over_bound':ratio,'pass':bool(ratio<=1)})
    return {'test_alpha':np.asarray(alpha).tolist(),'coherent_feature_checks':checks,'psd':psd,
            'pass':bool(all(c['pass'] for c in checks.values()) and all(c['pass'] for c in psd))}

def float32_feature_parity(gram,features,alpha):
    # Componentwise round-to-nearest gives ||delta|| <= u||signal|| + eta/2.
    # A band projection is a contraction of full Hann-window energy, hence
    # |delta_Pband| <= 2*sqrt(Pband*Pdelta_full)+Pdelta_full. This remains
    # meaningful in deep band cancellation; relative-only tolerances do not.
    u=2.**-24;eta=float(np.nextafter(np.float32(0),np.float32(1)))*float(gram.get('fixed_gain',1.))
    checks={}
    for name,observed in [
        ('early',[p for w in features['early'] for p in w['band_power']]),
        ('harmonic',[features['late_harmonics'][wi]['partials'][pi]['power'] for wi,pi in gram['harmonic_locations']])]:
        prediction=np.maximum(power(gram[name+'_Q'],alpha),0)
        total=np.maximum(power(gram[name+'_full_Q'],alpha),0)
        delta=(u*np.sqrt(total)+eta/2)**2
        observed=np.asarray(observed)
        roundoff=2*np.sqrt(prediction*delta)+delta
        arithmetic=5e-10*np.maximum(np.maximum(abs(prediction),abs(observed)),float(gram['power_floor']))
        bound=roundoff+arithmetic
        ratio=float(np.max(abs(prediction-observed)/np.maximum(bound,1e-300)))
        checks[name]={'maximum_error_over_bound':ratio,'pass':bool(ratio<=1)}
    prediction=envelope_values(gram,alpha)
    observed=np.asarray(features['late_envelope']['rms'])[gram['envelope_mask']]
    bound=u*prediction+eta/2+5e-10*np.maximum(np.maximum(abs(prediction),abs(observed)),float(gram['amplitude_floor']))
    ratio=float(np.max(abs(prediction-observed)/np.maximum(bound,1e-300)))
    checks['envelope']={'maximum_error_over_bound':ratio,'pass':bool(ratio<=1)}
    return {'alpha':np.asarray(alpha).tolist(),'checks':checks,'pass':bool(all(c['pass'] for c in checks.values()))}

def huber(value):
    absolute=np.abs(value)
    return np.where(absolute<=6,value*value,12*absolute-36),np.where(absolute<=6,2*value,12*np.sign(value))

def power_residual(Q,target,floor,alpha):
    observed=power(Q,alpha)
    residual=10*np.log10(np.maximum(observed,floor)/np.maximum(target,floor))
    derivative=alpha[None,:]*np.einsum('njk,k->nj',Q,alpha)/np.maximum(observed,floor)[:,None]
    derivative[observed<=floor]=0
    return residual,derivative

def envelope_residual(gram,alpha):
    Q0=gram['envelope_low_Q']; Q1=gram['envelope_high_Q']; t=gram['envelope_fraction']
    p0=np.maximum(power(Q0,alpha),0); p1=np.maximum(power(Q1,alpha),0)
    r0=np.sqrt(p0); r1=np.sqrt(p1); value=(1-t)*r0+t*r1
    floor=float(gram['amplitude_floor'])
    residual=20*np.log10(np.maximum(value,floor)/np.maximum(gram['envelope_target'],floor))
    numerator0=alpha[None,:]*np.einsum('njk,k->nj',Q0,alpha)
    numerator1=alpha[None,:]*np.einsum('njk,k->nj',Q1,alpha)
    term0=np.divide(numerator0,r0[:,None],out=np.zeros_like(numerator0),where=r0[:,None]>0)
    term1=np.divide(numerator1,r1[:,None],out=np.zeros_like(numerator1),where=r1[:,None]>0)
    derivative=((1-t[:,None])*term0+t[:,None]*term1)/np.maximum(value,floor)[:,None]
    derivative[value<=floor]=0
    return residual,derivative

def objective(theta,grams,details=False):
    alpha=10**(np.asarray(theta,dtype=float)/20)
    gradient=np.zeros(6); families=np.zeros(3)
    for gram in grams:
        residuals=[power_residual(gram['early_Q'],gram['early_target'],float(gram['power_floor']),alpha),
                   power_residual(gram['harmonic_Q'],gram['harmonic_target'],float(gram['power_floor']),alpha),
                   envelope_residual(gram,alpha)]
        for index,(error,derivative) in enumerate(residuals):
            loss,slope=huber(error)
            families[index]+=float(np.mean(loss))/len(grams)
            gradient+=np.mean(slope[:,None]*derivative,axis=0)/(3*len(grams))
    prior=.01*float(np.mean(np.asarray(theta)**2))
    difference=np.diff(theta); smooth=.02*float(np.mean(difference*difference))
    gradient+=.02*np.asarray(theta)/6
    gradient[:-1]-=.04*difference/5; gradient[1:]+=.04*difference/5
    value=float(np.mean(families)+prior+smooth)
    if not math.isfinite(value) or not np.isfinite(gradient).all(): raise ValueError('Nonfinite objective')
    if details: return {'total':value,'family_losses':families.tolist(),'prior':prior,'smooth':smooth,'gradient':gradient.tolist()}
    return value,gradient

def metadata():
    if sha(REFERENCE)!='e3ad140a8052c2e81acdc0a281a4e658a2df7f796029572d562634c8adf375fe': raise ValueError('Reference identity')
    if sha(METRIC)!='14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd': raise ValueError('Metric identity')
    if sha(HELPER)!='45b38bc157afdff800c1c2f9c6090d4c51225acb058f5057f214808d0a74e3b6': raise ValueError('Helper identity')
    if sha(HISTORY)!='5895dc53be8bf77398327c4b1f0c3057abadbb5cfe5904f957a9bde97cab49fe': raise ValueError('History identity')
    if sha(FIRST_SIX)!='c18f0a3fbcec5fb85a21e1b33b95863aacb4a64b064bddd5e93056f8ae8d60ae': raise ValueError('Originalsix producer identity')
    if sha(OPERATOR)!='636dc354c5eb475757bbf8f0a1195d7b40782dd5a72969af0127beaccdb51a3e': raise ValueError('Gateextractor identity')
    old=read(REFERENCE); references={c['id']:c for c in old['cases']}
    rows={c['id']:c for c in read(FEATURES)['samples']}
    if set(references)!=set(rows) or len(rows)!=34: raise ValueError('TRAIN34 inventory')
    return old,references,rows

def proof_inventory():
    history={c['id']:c for c in read(HISTORY)['cases']}
    originals={c['id']:c for c in read(FIRST_SIX)['cases']}
    inventory={}
    for ident,previous in history.items():
        if ident in originals:
            source=originals[ident]
            proof={key:source[key] for key in ['mechanical_state_bit_parity','force_bit_parity','new_faults']}
            proof.update(parity_proof=source['parity_proof'],scope='Originalsix producer collection-time proof, not rerun by this fit.')
            baseline=source['baseline_float32_payload_identical_to_cached_control']
            lineage='original_six_producer_receipt'
        else:
            proof=previous['source_proof'];baseline=previous['gates']['baseline_payload_exact_to_cached_control'];lineage='full_train34_history'
        if proof['mechanical_state_bit_parity'] is not True or proof['force_bit_parity'] is not True or proof['new_faults']!=0 or baseline is not True:
            raise ValueError('Invalid historical proof: '+ident)
        inventory[ident]={'proof':proof,'baseline_exact':baseline,'lineage':lineage}
    if len(inventory)!=34:raise ValueError('Proof inventory must coverall34')
    return inventory

def freeze():
    if (OUT/'protocol.json').exists(): raise ValueError('Protocol already exists')
    _,references,rows=metadata()
    result=read(BASIS/'result.json')
    if result.get('pass') is not True or result.get('count')!=34: raise ValueError('Reconstruction must pass before fit freeze')
    _,_,_,gate_sha=tools()
    proofs=proof_inventory()
    dependencies=[REFERENCE,HISTORY,FIRST_SIX,HELPER,METRIC,OPERATOR,FEATURES,SPLIT,
                  ROOT/'tools/fit_full_calibration.py',ROOT/'Research/GrandPianoV2/tools/benchmark.py',
                  ROOT/'Research/GrandPianoV2/tools/radiation_fit.py',ROOT/'Research/GrandPianoV2/tools/fit_calibration.py',
                  BASIS/'result.json',BASIS/'protocol.json',BASIS/'freeze.json',BASIS/'manifest.json']
    cases=[]
    for item in result['cases']:
        ident=item['id']; old=references[ident]
        if item.get('pass') is not True: raise ValueError('Failed reconstruction case')
        cases.append({'id':ident,'basis':{'path':str(BASIS/'renders'/ident/'basis.f64le'),'sha256':item['output_sha256']},
                      'fixed_old_gain':old['baseline']['fixed_gain'],'fixed_old_onset_frame':old['baseline']['fixed_onset_frame'],
                      'support':old['support'],'fit':not ident.startswith('C8'),'historical_proof':proofs[ident]})
    if sum(c['fit'] for c in cases)!=32: raise ValueError('Expected32 nonC8 fit cases')
    value={'schema_version':1,'frozen_at_utc':now(),'scope':'One bounded6positiveweight bodyonly TRAIN fit;32nonC8 fit, all34 rendered/reported/gated, no referencePCM or physical synthesis.',
           'basis_PCM_opened_for_fit':False,'sources':[record(OUT/'fit.py'),record(OUT/'highpass.cpp')],
           'inputs':[record(p) for p in dependencies],'cases':cases,
           'operator':'Rawbody=sum alpha_b*basis_b; HP24 exact recurrence from zero state frame0; float32 final output. No empirical string correction. Gain/width/phase untouched.',
           'alpha':'alpha_b=10^(theta_dB_b/20); modegain=sum alpha_b*phi_b, not exponential interpolation',
           'fit_selection':'32alreadyobservedTRAIN cases. C8excludedonlyfromfit becauseunassignedLFdominatesnormalization. Samealpha all34; allC8metrics/gates mandatory.',
           'objective':'mean32cases((mean20early_huber6 + meanincludedlateharmonic_huber6 + meanincludedlateenvelope_huber6)/3) + .01mean(theta_dB²) + .02mean(diff(theta_dB)²)',
           'huber6':'e² ifabs(e)<=6dB else12abs(e)-36; dataerrors originalfixedfloorpowerdB/envelopeamplitudedB',
           'optimizer':{'method':'L-BFGS-B','start_theta_dB':[0.]*6,'bounds_alpha':[.025,40.],'bounds_theta_dB':list(BOUNDS),'options':OPTIONS,'jacobian':'analytic, syntheticfinite-differencecheck beforefit','restarts_or_sweeps':False},
           'gram':'Allcoherentcross terms includingLRphase, exactHann/spectrum/fractionalbins; 240sample envelope smoothing andRMSinterpolation. Actualfixedtestalpha directfeatureparity beforefit.',
           'numerical_gates':{'feature_error_bound':'5e-10*max(abs(prediction),abs(explicit),originalfixedfloor)','psd_bound':'negativeeigenvalue<=4096eps*trace','synthetic_gradient_relative_tolerance':1e-6,
                              'final_float32_spectral':'Pdelta=(2^-24*sqrt(Pfull_Hann)+smallest_float32_subnormal/2)^2; bound2sqrt(Pband*Pdelta)+Pdelta+doublefeaturebound',
                              'final_float32_envelope':'bound2^-24*predictedRMS+smallest_float32_subnormal/2+doublefeaturebound; originalgatesuseactualfloat32helperfeaturesonly'},
           'preservation':'Exact unchanged originalgate arithmetic appliedall34;C3click>=3dB reductions; others earlyMAE<=+1; lateharm/env<=+.75;RMS<=.5;LR<=.5;mono<=.75. No exception/retargeting.',
           'gate_arithmetic_sha256':gate_sha,'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},
           'limits':['No extra runtime states; sixstaticweights cannotaddpoles/decays/partialfrequency/stereopropagation.','Bodyalpha1 isuncalibratedrawbody, notoldfinalbaseline.','Localnonconvexsolve only; nofeasiblepointorconvergencedoesnotproveglobalinfeasibility.','All34 previouslyobservedTRAIN, noholdout/generalization/realtime/SDK proof.'],'adopted':False}
    write(OUT/'protocol.json',value)
    write(OUT/'freeze.json',{'frozen_at_utc':value['frozen_at_utc'],'protocol':record(OUT/'protocol.json'),'sources':value['sources']})

def synthetic_checks(hp,metric):
    rng=np.random.default_rng(6026)
    x=rng.normal(size=(4096,6,2)); x[:,1,:]=-x[:,0,:]
    x[:100]=0; alpha=TEST_ALPHA
    filtered=hp(x); direct=hp(np.einsum('nbc,b->nc',x,alpha))
    recombined=np.einsum('nbc,b->nc',filtered,alpha)
    hp_error=float(np.max(abs(direct-recombined)))
    f,z,norm=fft_basis(filtered)
    Q=band_gram(f,z,norm,250.,1000.)
    observed=metric.band_powers(direct,((250.,1000.),))[0]
    spectral=relative_check([alpha@Q@alpha],[observed],1e-20)
    times=np.array([.03,.0400123,.06])
    q0,q1,t=temporal_grams(filtered,times)
    gram={'early_Q':np.stack([Q,Q*.7]),'early_target':np.array([observed*.75,observed*1.5]),
          'harmonic_Q':np.stack([Q*.8,Q*.5]),'harmonic_target':np.array([observed,observed*.5]),
          'envelope_low_Q':q0,'envelope_high_Q':q1,'envelope_fraction':t,
          'envelope_target':np.array([1.,1.1,1.2]),'power_floor':np.array(1e-20),'amplitude_floor':np.array(1e-10)}
    env=np.sqrt(ndimage.uniform_filter1d(np.mean(direct*direct,axis=1),240,mode='nearest'))
    actual=np.interp(times*RATE,np.arange(len(env)),env)
    envelope=relative_check(envelope_values(gram,alpha),actual,1e-10)
    theta=np.array([1.,-2.,.5,2.,-1.,.25]); _,gradient=objective(theta,[gram])
    numerical=np.empty(6); step=1e-5
    for i in range(6):
        delta=np.zeros(6);delta[i]=step
        numerical[i]=(objective(theta+delta,[gram])[0]-objective(theta-delta,[gram])[0])/(2*step)
    gradient_error=float(np.max(abs(gradient-numerical)/np.maximum(1,abs(numerical))))
    return {'hp_maximum_recombination_error':hp_error,'spectral':spectral,'envelope':envelope,
            'analytic_gradient':gradient.tolist(),'numeric_gradient':numerical.tolist(),'gradient_relative_error':gradient_error,
            'pass':bool(hp_error<1e-11 and spectral['pass'] and envelope['pass'] and gradient_error<=1e-6)}

def execute():
    p=read(OUT/'protocol.json'); frozen=read(OUT/'freeze.json')
    verify([frozen['protocol'],*p['sources'],*p['inputs']])
    if (OUT/'opening-started.json').exists(): raise ValueError('Once-only fit already started')
    write(OUT/'opening-started.json',{'started_at_utc':now(),'protocol':record(OUT/'protocol.json'),'basis_PCM_opened_before_marker':False})
    start=time.monotonic(); metric,helper,gate,gate_sha=tools()
    if gate_sha!=p['gate_arithmetic_sha256']: raise ValueError('Gate arithmetic changed')
    _,references,rows=metadata(); hp,hp_identity=hp_compile()
    synthetic=synthetic_checks(hp,metric);write(OUT/'synthetic-checks.json',synthetic)
    if not synthetic['pass']: raise ValueError('Synthetic/gradientcheck failed beforefit')
    proofs=proof_inventory()
    grams=[]; parity=[]; input_records=[]
    for case in p['cases']:
        ident=case['id']; old=references[ident]; verify([case['basis']])
        raw=np.fromfile(case['basis']['path'],dtype='<f8').reshape((FRAMES,14))
        basis=np.ascontiguousarray(raw[:,2:].reshape((FRAMES,6,2)))
        if not np.isfinite(basis).all(): raise ValueError('Nonfinite basis: '+ident)
        filtered=hp(basis); gram=build_grams(filtered,old,rows[ident])
        direct=hp(np.einsum('nbc,b->nc',basis,TEST_ALPHA))
        features=helper.observation_features(metric,direct,case['fixed_old_onset_frame'],case['fixed_old_gain'],old['reference'],rows[ident],case['support'])
        check=feature_parity(gram,features); check['id']=ident; parity.append(check)
        write(OUT/'parity'/(ident+'.json'),check)
        if not check['pass']: raise ValueError('Actual coherent featureparity failed: '+ident)
        destination=OUT/'grams'/(ident+'.npz'); destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists(): raise ValueError('Existing Gram file')
        np.savez_compressed(destination,**gram)
        input_records.append(record(destination))
        if case['fit']: grams.append(gram)
        print(ident+' coherent Grams/direct parity PASS',flush=True)
    if len(grams)!=32: raise ValueError('Fit count changed')
    write(OUT/'gram-receipt.json',{'completed_at_utc':now(),'protocol':record(OUT/'protocol.json'),'files':input_records,'all34_direct_parity':parity,'hp':hp_identity,'reference_PCM_opened':False})
    trace=[]
    def evaluate(theta):
        value,gradient=objective(theta,grams)
        trace.append({'evaluation':len(trace),'theta_dB':np.asarray(theta).tolist(),'objective':value,'gradient':gradient.tolist()})
        return value,gradient
    initial=objective(np.zeros(6),grams,True)
    fitted=optimize.minimize(evaluate,np.zeros(6),method='L-BFGS-B',jac=True,bounds=[BOUNDS]*6,options=OPTIONS)
    theta=np.asarray(fitted.x,dtype=float); alpha=10**(theta/20)
    fit_result={'completed_at_utc':now(),'protocol':record(OUT/'protocol.json'),'method':'L-BFGS-B','success':bool(fitted.success),'status':int(fitted.status),'message':str(fitted.message),'iterations':int(fitted.nit),'evaluations':int(fitted.nfev),'theta_dB':theta.tolist(),'alpha':alpha.tolist(),'initial_uncalibrated_body_objective':initial,'final_objective':objective(theta,grams,True),'trace':trace,'initial_is_old_final_sound':False,'fit_count':32,'excluded_fit_cases':['C8v4','C8v12'],'same_alpha_all34':True,'adopted':False}
    write(OUT/'fit-result.json',fit_result)
    outcomes=[]
    for case in p['cases']:
        ident=case['id']; old=references[ident];verify([case['basis']])
        raw=np.fromfile(case['basis']['path'],dtype='<f8').reshape((FRAMES,14))
        basis=raw[:,2:].reshape((FRAMES,6,2))
        candidate=hp(np.einsum('nbc,b->nc',basis,alpha)).astype(np.float32)
        if not np.isfinite(candidate).all(): raise ValueError('Nonfinite finalcandidate')
        destination=OUT/'candidate'/(ident+'.wav');destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists(): raise ValueError('Existing final candidate')
        wavfile.write(destination,RATE,candidate)
        features=helper.observation_features(metric,candidate.astype(float),case['fixed_old_onset_frame'],case['fixed_old_gain'],old['reference'],rows[ident],case['support'])
        proof=proofs[ident]['proof'];baseline_exact=proofs[ident]['baseline_exact']
        if case['historical_proof']!=proofs[ident]:raise ValueError('Frozen historicalproof changed')
        with np.load(OUT/'grams'/(ident+'.npz'),allow_pickle=False) as archive:
            gram={key:archive[key] for key in archive.files}
        direct_double=hp(np.einsum('nbc,b->nc',basis,alpha))
        double_features=helper.observation_features(metric,direct_double,case['fixed_old_onset_frame'],case['fixed_old_gain'],old['reference'],rows[ident],case['support'])
        double_forecast=feature_parity(gram,double_features,alpha)
        float_forecast=float32_feature_parity(gram,features,alpha)
        scored=gate(old,features,ident,baseline_exact,{ident:proof})
        outcome={'id':ident,'used_in_fit':case['fit'],'candidate_audio':record(destination),'candidate':features,**scored,
                 'source_proof':proof,'baseline_payload_proof_reused_from_history':True,
                 'historical_proof_lineage':proofs[ident]['lineage'],'final_double_gram_forecast':double_forecast,
                 'final_float32_gram_forecast':float_forecast,
                 'scope':'No new physicaltrajectory. Bodyreconstructionmatches previouslycapturedrawbody and authenticatedforces; oldbaseline/state/forceproofs are collectiontime facts, not rerun.'}
        outcomes.append(outcome); write(OUT/'case-results'/(ident+'.json'),outcome)
        print(ident+' final '+('PASS' if scored['passes_all_case_gates'] else 'FAIL'),flush=True)
    verify([frozen['protocol'],*p['sources'],*p['inputs'],*input_records,*[c['basis'] for c in p['cases']]])
    failed=[c['id'] for c in outcomes if not c['passes_all_case_gates']]
    forecast=bool(all(c['final_double_gram_forecast']['pass'] and c['final_float32_gram_forecast']['pass'] for c in outcomes))
    result={'completed_at_utc':now(),'protocol':record(OUT/'protocol.json'),'fit_result':record(OUT/'fit-result.json'),'gram_receipt':record(OUT/'gram-receipt.json'),'case_count':34,'cases':outcomes,'failed_case_ids':failed,'passes_all_preservation_gates':bool(not failed),'final_forecast_checks_pass':forecast,'optimizer_converged':bool(fitted.success),'passed':bool(not failed and fitted.success and forecast),'wall_seconds':time.monotonic()-start,'reference_PCM_opened':False,'physical_synthesis_runs':0,'adopted':False,'limits':p['limits']}
    write(OUT/'result.json',result)
    manifest={str(f.relative_to(OUT)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='manifest.json'}
    write(OUT/'manifest.json',manifest)
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','limits']}),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','run'])
    args=parser.parse_args()
    if args.command=='freeze': freeze();return
    try: execute()
    except Exception as error:
        if not (OUT/'failure.json').exists():
            write(OUT/'failure.json',{'failed_at_utc':now(),'error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc(),'silently_retried':False})
        raise
if __name__=='__main__': main()
