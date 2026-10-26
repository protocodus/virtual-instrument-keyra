#!/usr/bin/env python3
"""TRAIN26-only rejection study of independent complex fast/late radiation vectors.

This is an offline feasibility diagnostic. It never reads held-out recordings,
changes canonical calibration/source, or creates native audio. Raw fitted
coefficients remain under out/; the compact tracked report records failures.
"""
import argparse
import json, math, time, hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1]
CAL=json.loads((ROOT/'Validation/live-calibration.json').read_text())
ST=json.loads((ROOT/'Validation/stereo-observation-feasibility.json').read_text())
FT=json.loads((ROOT/'References/GrandExpanded/train_features.json').read_text())
EXPECTED_TRAINING_IDS={f'{pitch}v{layer}' for pitch in ('A1','C2','D#2','A2','C3','D#3','C4','D#4','A4','C5','D#5','A5','C6') for layer in (4,12)}
assert len(CAL['training_ids'])==26 and set(CAL['training_ids'])==set(ST['training_ids'])=={x['id'] for x in FT['samples']}
assert set(CAL['training_ids'])==EXPECTED_TRAINING_IDS
assert not ST['heldout_cases_used'] and all(x['split']=='train' for x in FT['samples'])
rows={x['id']:x for x in ST['measurements']};features={x['id']:x for x in FT['samples']}
notes=sorted({x['midi'] for x in FT['samples']})
ids={(x['midi'],x['layer']):x['id'] for x in FT['samples']}
WINDOWS=[(.05,.25),(.25,.75),(.75,1.5),(1.5,3.5)]
POINTS=128
TIMES=np.array([np.linspace(a,b,POINTS,endpoint=False)+(b-a)/(2*POINTS) for a,b in WINDOWS]);W=np.sin(np.pi*(np.arange(POINTS)+.5)/POINTS)**4;W/=W.sum()
TWOPI=2*np.pi

def metadata(note):
 ss=[features[ids[note,l]] for l in (4,12)]
 return float(np.exp(np.mean([np.log(s['f1_hz']) for s in ss]))),float(np.exp(np.mean([np.log(s['B']) for s in ss])))
def obs(note,layer,n,wi):
 s=rows[ids[note,layer]]['windows'][wi]
 if n>len(s):return None
 p=s[n-1];assert p['n']==n
 c=complex(p['cross_real'],p['cross_imag']);M=np.array([[p['pl'],c],[np.conj(c),p['pr']]],complex)
 return M,p['relative_total_power']
def envelope(note,layer,n):return np.array(CAL['fits'][ids[note,layer]]['modes'][n-1],float)
def coefficient(M):
 M=M/np.trace(M).real
 return np.array([np.sqrt(max(1e-12,M[0,0].real)*2),np.sqrt(max(1e-12,M[1,1].real)*2)*np.exp(-1j*np.angle(M[0,1]))])
def raw_cov(T,Q):return np.einsum('ac,ncd,bd->nab',T,Q,T.conj(),optimize=True)
def qs(m,hz,attack=None):
 F,L,sf,sl=m;expf=F*np.exp(-sf*TIMES);expl=L*np.exp(-sl*TIMES)
 # Current envelope fit starts with this carrier-averaged cross phase. To isolate
 # the projection, no additional arbitrary attack/room term is fitted here.
 A=np.sum(expf*expf*W,axis=1);B=np.sum(expl*expl*W,axis=1);D=np.sum(expf*expl*np.exp(-1j*TWOPI*hz*(2**(.23/1200)-1)*TIMES)*W,axis=1)
 Q=np.empty((4,2,2),complex);Q[:,0,0]=A/2;Q[:,1,1]=B/2;Q[:,0,1]=D/2;Q[:,1,0]=np.conj(D)/2
 return Q
def vectors(x):return np.array([[np.exp(x[0]),x[3]+1j*x[4]],[x[1]+1j*x[2],x[5]+1j*x[6]]],complex)
def params(T):return np.array([np.log(max(T[0,0].real,.001)),T[1,0].real,T[1,0].imag,T[0,1].real,T[0,1].imag,T[1,1].real,T[1,1].imag])
def flatten(M):return np.stack([M[...,0,0].real,M[...,1,1].real,np.sqrt(2)*M[...,0,1].real,np.sqrt(2)*M[...,0,1].imag],axis=-1)
def static(note,n):
 ss=[]
 for l in (4,12):
  for wi in (0,1):
   o=obs(note,l,n,wi)
   if o is not None and o[1]>=1e-5:ss.append(o[0]/np.trace(o[0]).real)
 if not ss:return None
 return coefficient(np.mean(ss,axis=0))
def model_derivatives(x,Q):
 T=vectors(x);dT=np.zeros((7,2,2),complex)
 dT[0,0,0]=T[0,0];dT[1,1,0]=1;dT[2,1,0]=1j
 dT[3,0,1]=1;dT[4,0,1]=1j;dT[5,1,1]=1;dT[6,1,1]=1j
 return (np.einsum('kac,ncd,bd->nkab',dT,Q,T.conj(),optimize=True)
         +np.einsum('ac,ncd,kbd->nkab',T,Q,dT.conj(),optimize=True))

def fit_node(note,n,lam):
 f0,B=metadata(note);hz=f0*n*np.sqrt((1+B*n*n)/(1+B))
 prior=static(note,n)
 if prior is None:return None
 Q=[];R=[];prom=[]
 for l in (4,12):
  q=qs(envelope(note,l,n),hz)
  for wi in range(4):
   o=obs(note,l,n,wi)
   if o is None or o[1]<1e-5:continue
   Q.append(q[wi]);R.append(o[0]);prom.append(o[1])
 if len(Q)<3:return None
 Q=np.array(Q);R=np.array(R);tr=R.trace(axis1=1,axis2=2).real
 scale=np.maximum(tr,np.max(tr)*1e-4)
 pT=np.column_stack([prior,prior]);pv=np.array([pT[0,0].real,pT[1,0].real,pT[1,0].imag,pT[0,1].real,pT[0,1].imag,pT[1,1].real,pT[1,1].imag])
 def coefficients(x):
  T=vectors(x);v=np.array([T[0,0].real,T[1,0].real,T[1,0].imag,T[0,1].real,T[0,1].imag,T[1,1].real,T[1,1].imag]);return T,v
 def residual(x):
  T,v=coefficients(x);M=raw_cov(T,Q)
  contrast=np.array([v[0]-v[3],-v[4],v[1]-v[5],v[2]-v[6]])
  return np.r_[(flatten(M-R)/scale[:,None]).reshape(-1),lam*.5*(v-pv),lam*contrast]
 def jac(x):
  T,v=coefficients(x);dM=model_derivatives(x,Q)
  J=np.stack([dM[...,0,0].real,dM[...,1,1].real,np.sqrt(2)*dM[...,0,1].real,np.sqrt(2)*dM[...,0,1].imag],axis=1)
  # J shape N,4,K.
  J=(J/scale[:,None,None]).reshape(-1,7)
  V=np.eye(7);V[0,0]=T[0,0].real
  contrast=np.array([V[0]-V[3],-V[4],V[1]-V[5],V[2]-V[6]])
  return np.vstack([J,lam*.5*V,lam*contrast])
 best=None
 for phase in (0.,.6,-.6):
  T=pT.copy();T[:,1]*=np.exp(1j*phase);T[1,1]*=np.exp(-.3j*phase)
  start=params(T);start=np.clip(start,np.array([-5,-4,-4,-4,-4,-4,-4])+1e-9,np.array([np.log(4),4,4,4,4,4,4])-1e-9)
  fit=least_squares(residual,start,jac=jac,bounds=([-5,-4,-4,-4,-4,-4,-4],[np.log(4),4,4,4,4,4,4]),max_nfev=100,ftol=1e-7,xtol=1e-7,gtol=1e-7)
  if best is None or np.sum(fit.fun**2)<np.sum(best.fun**2):best=fit
 T=vectors(best.x)
 singular=np.linalg.svd(jac(best.x)[:len(Q)*4],compute_uv=False)
 rank=int(np.sum(singular>max(singular[0]*1e-6,1e-12)))
 condition=float(singular[0]/singular[-1]) if singular[-1]>1e-14 else None
 return {'data_jacobian_singular_values':singular.tolist(),'data_jacobian_rank_1e_6':rank,'data_jacobian_condition_number':condition,'T':T,'cost':float(np.sum(best.fun**2)),'windows':len(Q),'prior':prior,'maximum_column_scale':float(np.max(np.linalg.norm(T,axis=0)/np.sqrt(2))),
         'nfev':best.nfev,'success':bool(best.success),'power_mae_db':float(np.mean(abs(10*np.log10(np.maximum(np.trace(raw_cov(T,Q),axis1=1,axis2=2).real,1e-30)/tr))))}

def interp_modes(note,layer,n,lo,hi):
 t=(note-lo)/(hi-lo);a=envelope(lo,layer,n);z=envelope(hi,layer,n)
 return np.r_[(1-t)*a[:2]+t*z[:2],np.exp((1-t)*np.log(a[2:])+t*np.log(z[2:]))]
def cv(nodes):
 records=[]
 for k,note in enumerate(notes[1:-1],1):
  lo,hi=notes[k-1],notes[k+1];t=(note-lo)/(hi-lo)
  flo,Blo=metadata(lo);fhi,Bhi=metadata(hi)
  ca=1200*np.log2(flo/(440*2**((lo-69)/12)));cz=1200*np.log2(fhi/(440*2**((hi-69)/12)))
  f0=440*2**((note-69+((1-t)*ca+t*cz)/100)/12)
  B=np.exp((1-t)*np.log(Blo)+t*np.log(Bhi))
  for l in (4,12):
   for n in range(1,49):
    if (lo,n) not in nodes or (hi,n) not in nodes:continue
    A,Z=nodes[lo,n]['T'],nodes[hi,n]['T']
    priorA,priorZ=nodes[lo,n]['prior'],nodes[hi,n]['prior']
    # Branch column norm is absorbed into source amplitude before interpolation.
    scaleA=np.linalg.norm(A,axis=0)/np.sqrt(2);scaleZ=np.linalg.norm(Z,axis=0)/np.sqrt(2)
    unitA=A/scaleA[None,:];unitZ=Z/scaleZ[None,:]
    unit=(1-t)*unitA+t*unitZ
    norms=np.linalg.norm(unit,axis=0)/np.sqrt(2);unit=unit/np.maximum(norms[None,:],1e-9)
    ma=envelope(lo,l,n).copy();mz=envelope(hi,l,n).copy();ma[:2]*=scaleA;mz[:2]*=scaleZ
    m=np.r_[(1-t)*ma[:2]+t*mz[:2],np.exp((1-t)*np.log(ma[2:])+t*np.log(mz[2:]))]
    hz=f0*n*np.sqrt((1+B*n*n)/(1+B));Q=qs(m,hz);pred=raw_cov(unit,Q)
    # Direct T interpolation is a second no-extra-fit candidate. Its envelope
    # basis is predicted only from the two endpoint training anchors as well.
    direct=raw_cov((1-t)*A+t*Z,qs(interp_modes(note,l,n,lo,hi),hz))
    st=(1-t)*priorA+t*priorZ;st*=np.sqrt(2)/max(np.linalg.norm(st),1e-12);sM=np.outer(st,st.conj())/2
    pos=np.clip((note-64.5)/52,-.85,.85);pan=np.array([1-.588*pos,1+.588*pos]);panM=np.outer(pan,pan)/np.dot(pan,pan)
    for wi in range(4):
     target=obs(note,l,n,wi)
     if target is None or target[1]<1e-4:continue
     R,w=target;trace=np.trace(R).real;R=R/trace
     predictions={'pan':panM,'static_complex':sM,'two_branch_normalized':pred[wi]/max(np.trace(pred[wi]).real,1e-30),'two_branch_direct':direct[wi]/max(np.trace(direct[wi]).real,1e-30)}
     records.append({'id':ids[note,l],'midi':note,'n':n,'window':wi,'weight':w,
      'cov_error':{method:float(np.linalg.norm(M-R)) for method,M in predictions.items()},
      'balance_error_db':{method:float(abs(10*np.log10(max(M[1,1].real,1e-30)/max(M[0,0].real,1e-30))-10*np.log10(max(R[1,1].real,1e-30)/max(R[0,0].real,1e-30)))) for method,M in predictions.items()},
      'candidate_raw_power_error_db':float(10*np.log10(max(np.trace(pred[wi]).real,1e-30)/trace))})
 return records

def summary(records):
 out={};weights=np.array([r['weight'] for r in records]);weights/=sum(weights)
 for method in records[0]['cov_error']:
  out[method]={'weighted_covariance_error':float(sum(w*r['cov_error'][method] for w,r in zip(weights,records))),
               'weighted_balance_error_db':float(sum(w*r['balance_error_db'][method] for w,r in zip(weights,records)))}
 out['evaluated_partial_windows']=len(records)
 out['weighted_absolute_raw_power_error_db']=float(sum(w*abs(r['candidate_raw_power_error_db']) for w,r in zip(weights,records)))
 return out


def feature(note,n,bwf,bwp):
 f,B=metadata(note);hz=f*n*np.sqrt((1+B*n*n)/(1+B));return [np.log2(hz)/bwf,0 if np.isinf(bwp) else (note-60)/bwp]
def encode(T,mode):
 if mode=='cartesian':return params(T)
 out=[np.log(max(abs(T[0,0]),1e-6))]
 for z in (T[1,0],T[0,1],T[1,1]):
  out.extend([np.log(max(abs(z),1e-6)),np.cos(np.angle(z)),np.sin(np.angle(z))])
 return np.array(out)
def decode(v,mode):
 if mode=='cartesian':return vectors(np.clip(v,[-5,-4,-4,-4,-4,-4,-4],[np.log(4),4,4,4,4,4,4]))
 values=[np.exp(np.clip(v[0],-5,np.log(4)))+0j]
 for k in (1,4,7):
  amp=np.exp(np.clip(v[k],-5,np.log(5.657)));phase=np.arctan2(v[k+2],v[k+1]);values.append(amp*np.exp(1j*phase))
 return np.array([[values[0],values[2]],[values[1],values[3]]])

def evaluate_field(nodes,bwf,bwp,mode):
 records=[]
 for k,note in enumerate(notes[1:-1],1):
  lo,hi=notes[k-1],notes[k+1];t=(note-lo)/(hi-lo)
  train=[key for key in nodes if key[0]!=note];X=np.array([feature(a,n,bwf,bwp) for a,n in train]);Y=np.array([encode(nodes[key]['T'],mode) for key in train])
  distance=((X[:,None,:]-X[None,:,:])**2).sum(axis=2);K=np.exp(-.5*distance)
  # Explicit modest ridge and mean-centered observations; no fold target enters.
  mean=Y.mean(axis=0);weights=np.linalg.solve(K+.1*np.eye(len(K)),Y-mean)
  flo,Blo=metadata(lo);fhi,Bhi=metadata(hi);ca=1200*np.log2(flo/(440*2**((lo-69)/12)));cz=1200*np.log2(fhi/(440*2**((hi-69)/12)))
  f0=440*2**((note-69+((1-t)*ca+t*cz)/100)/12);B=np.exp((1-t)*np.log(Blo)+t*np.log(Bhi))
  for layer in (4,12):
   for n in range(1,49):
    if (lo,n) not in nodes or (hi,n) not in nodes:continue
    hz=f0*n*np.sqrt((1+B*n*n)/(1+B));targetX=np.array([np.log2(hz)/bwf,0 if np.isinf(bwp) else (note-60)/bwp])
    prediction=mean+np.exp(-.5*((X-targetX)**2).sum(axis=1))@weights;T=decode(prediction,mode)
    source=interp_modes(note,layer,n,lo,hi);pred=raw_cov(T,qs(source,hz))
    pos=np.clip((note-64.5)/52,-.85,.85);pan=np.array([1-.588*pos,1+.588*pos]);panM=np.outer(pan,pan)/np.dot(pan,pan)
    for wi in range(4):
     target=obs(note,layer,n,wi)
     if target is None or target[1]<1e-4:continue
     R,w=target;trace=np.trace(R).real;R=R/trace;P=pred[wi]/max(np.trace(pred[wi]).real,1e-30)
     records.append({'id':ids[note,layer],'midi':note,'n':n,'window':wi,'weight':w,
      'cov_error':{'pan':float(np.linalg.norm(panM-R)),'field':float(np.linalg.norm(P-R))},
      'balance_error_db':{'pan':float(abs(10*np.log10(max(panM[1,1].real,1e-30)/max(panM[0,0].real,1e-30))-10*np.log10(max(R[1,1].real,1e-30)/max(R[0,0].real,1e-30)))),
                          'field':float(abs(10*np.log10(max(P[1,1].real,1e-30)/max(P[0,0].real,1e-30))-10*np.log10(max(R[1,1].real,1e-30)/max(R[0,0].real,1e-30))))},
      'candidate_raw_power_error_db':float(10*np.log10(max(np.trace(pred[wi]).real,1e-30)/trace))})
 return {'frequency_bandwidth_octaves':bwf,'pitch_bandwidth_semitones':None if np.isinf(bwp) else bwp,'parameterization':mode,'ridge':.1,
         'early_window_cv':summary([r for r in records if r['window']<2]),'full_window_cv':summary(records),'records':records}

def known_training_summary(nodes):
 errors={name:[] for name in ('pan','shared_static','two_branch')};weights=[]
 for (note,n),fit in nodes.items():
  T=fit['T'];p=fit['prior'];shared=np.column_stack([p,p]);frequency,dispersion=metadata(note)
  hz=frequency*n*np.sqrt((1+dispersion*n*n)/(1+dispersion))
  position=np.clip((note-64.5)/52,-.85,.85);pan=np.array([1-.588*position,1+.588*position]);panM=np.outer(pan,pan)/np.dot(pan,pan)
  for layer in (4,12):
   Q=qs(envelope(note,layer,n),hz);fitted=raw_cov(T,Q);static=raw_cov(shared,Q)
   for wi in (0,1):
    observation=obs(note,layer,n,wi)
    if observation is None or observation[1]<1e-4:continue
    reference,power=observation;reference=reference/np.trace(reference).real;weights.append(power)
    for name,M in [('pan',panM),('shared_static',static[wi]/np.trace(static[wi]).real),('two_branch',fitted[wi]/np.trace(fitted[wi]).real)]:
     errors[name].append(float(np.linalg.norm(M-reference)))
 return {name:float(np.dot(values,weights)/sum(weights)) for name,values in errors.items()}

def conditioning_summary(nodes):
 values=list(nodes.values())
 ratios=[v['data_jacobian_singular_values'][-1]/max(v['data_jacobian_singular_values'][0],1e-30) for v in values]
 return {'nodes':len(values),'optimizer_successful_nodes':sum(v['success'] for v in values),
         'full_data_jacobian_rank_nodes':sum(v['data_jacobian_rank_1e_6']==7 for v in values),
         'median_smallest_largest_jacobian_singular_ratio':float(np.median(ratios)),
         'p10_smallest_largest_jacobian_singular_ratio':float(np.quantile(ratios,.1)),
         'limits':'Local identifiability is conditional on the assumed source envelopes, frequencies and gauge; it does not identify physical strings or microphones.'}

def json_nodes(nodes):
 result={}
 for (note,n),fit in nodes.items():
  result[f'{note}:{n}']={}
  for key,value in fit.items():
   if key=='T':value=[[[float(z.real),float(z.imag)] for z in row] for row in value]
   elif key=='prior':value=[[float(z.real),float(z.imag)] for z in value]
   result[f'{note}:{n}'][key]=value
 return result

def save(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def self_check():
 rng=np.random.default_rng(12345);maximum_covariance=0.;minimum_eigenvalue=0.;maximum_jacobian=0.;maximum_normalization=0.
 for repeat in range(30):
  source=np.r_[rng.uniform(.01,.3,2),rng.uniform(1,8),rng.uniform(.04,.9)]
  hz=float(rng.uniform(65,1500));Q=qs(source,hz)
  x=np.r_[rng.uniform(-1,.5),rng.uniform(-1.2,1.2,6)];T=vectors(x)
  analytic=raw_cov(T,Q)
  for wi,times in enumerate(TIMES):
   fast=source[0]*np.exp(-source[2]*times)
   late=source[1]*np.exp(-source[3]*times)*np.exp(1j*TWOPI*hz*(2**(.23/1200)-1)*times)
   pressure=T@np.vstack([fast,late])
   actual=.5*np.einsum('at,bt,t->ab',pressure,pressure.conj(),W)
   maximum_covariance=max(maximum_covariance,float(np.max(abs(actual-analytic[wi]))))
   minimum_eigenvalue=min(minimum_eigenvalue,float(np.min(np.linalg.eigvalsh(analytic[wi]))))
  derivative=model_derivatives(x,Q)
  for index in range(7):
   step=1e-6;above=x.copy();below=x.copy();above[index]+=step;below[index]-=step
   numeric=(raw_cov(vectors(above),Q)-raw_cov(vectors(below),Q))/(2*step)
   maximum_jacobian=max(maximum_jacobian,float(np.max(abs(numeric-derivative[:,index]))))
  norms=np.linalg.norm(T,axis=0)/np.sqrt(2);unit=T/norms[None,:]
  rescaled=source.copy();rescaled[:2]*=norms
  maximum_normalization=max(maximum_normalization,float(np.max(abs(raw_cov(unit,qs(rescaled,hz))-analytic))))
 passed=maximum_covariance<1e-12 and minimum_eigenvalue> -1e-12 and maximum_jacobian<1e-8 and maximum_normalization<1e-12
 if not passed:raise AssertionError('Two-branch covariance formulation failed its known-signal/gradient checks')
 return {'passed':bool(passed),'random_positive_source_cases':30,'maximum_direct_analytic_signal_covariance_error':maximum_covariance,
         'minimum_predicted_covariance_eigenvalue':minimum_eigenvalue,'maximum_finite_difference_jacobian_error':maximum_jacobian,
         'maximum_column_normalization_and_amplitude_rescale_error':maximum_normalization,
         'limits':'Checks the analysis formulation against explicit complex time signals and finite differences. It is not a native audio or recording-realism test.'}

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,default=ROOT/'Validation/two-branch-stereo-feasibility.json')
 parser.add_argument('--scratch-dir',type=Path,default=ROOT/'out/stereo-candidate/rejected-two-branch')
 args=parser.parse_args();checks=self_check();started=time.time()
 args.scratch_dir.mkdir(parents=True,exist_ok=True)
 input_paths={'training_features':ROOT/'References/GrandExpanded/train_features.json',
              'training_covariances':ROOT/'Validation/stereo-observation-feasibility.json',
              'calibration':ROOT/'Validation/live-calibration.json',
              'split':ROOT/'References/GrandExpanded/split.json',
              'engine':ROOT/'src/Piano.cpp','analysis':Path(__file__)}
 input_hashes={name:digest(path) for name,path in input_paths.items()}
 snapshots={}
 for name,path in input_paths.items():
  destination=args.scratch_dir/'inputs'/(name+path.suffix);destination.parent.mkdir(parents=True,exist_ok=True)
  destination.write_bytes(path.read_bytes());snapshots[name]=str(destination.relative_to(ROOT)) if destination.is_relative_to(ROOT) else str(destination)
 local_results={};field_results=[];raw_artifacts={};field_nodes=None
 for lam in (.03,.1,.3):
  nodes={}
  for note in notes:
   for partial in range(1,49):
    fitted=fit_node(note,partial,lam)
    if fitted is not None:nodes[note,partial]=fitted
  records=cv(nodes)
  result={'regularization':lam,'node_count':len(nodes),'optimizer':'Bounded least-squares, seven-real-parameter gauge, analytic Jacobian, three relative-phase starts.',
          'training_partial_mean_power_error_db':float(np.mean([v['power_mae_db'] for v in nodes.values()])),
          'maximum_column_amplitude_scale':max(v['maximum_column_scale'] for v in nodes.values()),
          'known_training_pitch_early_covariance':known_training_summary(nodes),'conditioning':conditioning_summary(nodes),
          'all_windows_cv':summary(records),'early_windows_cv':summary([row for row in records if row['window']<2]),
          'pitchwise_cv':{str(note):summary([r for r in records if r['midi']==note and r['window']<2]) for note in notes[1:-1]}}
  raw=args.scratch_dir/f'local-{lam}.json';save(raw,{**result,'nodes':json_nodes(nodes),'cv_records':records})
  raw_artifacts[str(raw.relative_to(ROOT)) if raw.is_relative_to(ROOT) else str(raw)]=digest(raw)
  local_results[str(lam)]=result
  if lam==.1:field_nodes=nodes
  print('local',lam,json.dumps(result['early_windows_cv']),flush=True)
 for bandwidth_frequency,bandwidth_pitch in ((.5,12),(.25,12),(.75,np.inf)):
  for mode in ('cartesian','polar'):
   result=evaluate_field(field_nodes,bandwidth_frequency,bandwidth_pitch,mode)
   name=f'field-{bandwidth_frequency}-{bandwidth_pitch}-{mode}.json'
   raw=args.scratch_dir/name;save(raw,result)
   raw_artifacts[str(raw.relative_to(ROOT)) if raw.is_relative_to(ROOT) else str(raw)]=digest(raw)
   field_results.append({key:value for key,value in result.items() if key!='records'})
   print('field',bandwidth_frequency,bandwidth_pitch,mode,json.dumps(result['early_window_cv']),flush=True)
 report={'schema_version':1,'training_only':True,'training_ids':CAL['training_ids'],'heldout_or_reserved_cases_used':False,
         'decision':'Reject this bounded two-branch surrogate projection candidate; no native audio, default source, header or plugin change was made.',
         'input_sha256':input_hashes,'input_snapshots':snapshots,'raw_artifact_sha256':raw_artifacts,
         'known_signal_and_gradient_checks':checks,
         'model':'S=T Q T_dagger; Q is the positive two-source covariance from the existing fast/late envelopes with .23-cent detuning. T has independent complex L/R columns, gauge a_fast_left>0.',
         'power_consistency':'Distinct normalized columns change the mean-power interference term. Normalizing each column and absorbing its norm in its source amplitude preserves new predictions, not the previous coherent fit or live early-energy normalization. A native candidate would need observation-aware energy normalization and velocity/attack checks.',
         'fit_scope':'Two velocities share T at each note/partial; all four windows fit with reference-trace-scaled covariance residuals and bounded coefficients. Source frequencies/rates/envelopes remain fixed during local fitting.',
         'cv_scope':'Both velocities of each interior training pitch omitted together. Prediction uses retained endpoint source amplitudes/rates, tuning offsets and dispersion. Target measurements enter only masks, weights and errors. Rank-one baselines use the same evaluated windows. This is training cross-validation, not a fresh recording test.',
         'field_scope':'RBF ridge smoothing of local T parameters over log-frequency and pitch, refit on retained pitches within each fold. Six predefined Cartesian/polar fields; ridge0.1. This is a bounded exploratory regularization check, not exhaustive model selection.',
         'metrics':'Covariance error is Frobenius norm after trace normalization, weighted by reference partial power. Channel-balance error is absolute R/L dB error. Raw power error is also retained; covariance success alone cannot justify changing the amplitude fit.',
         'local_fits':local_results,'frequency_pitch_fields':field_results,
         'native_candidate_generated':False,'elapsed_seconds':time.time()-started,
         'limits':'No first20/50ms, cross-harmonic onset phase, native audio, perception, dynamics or runtime CPU claim. Per-partial covariance leaves common onset phase unidentified. Conditional Jacobian rank does not identify physical polarizations, unisons, bridge geometry or microphones. Failed interpolation does not rule out richer consistently identified physical source bases.'}
 save(args.output,report);print(args.output)
if __name__=='__main__':main()
