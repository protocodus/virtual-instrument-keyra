"""Byte-preserved functions from the frozen single400Hz operator. No fitting."""
import math
import numpy as np
RATE=48000;CUTOFF=400.

def coefficients():
 k=math.tan(math.pi*CUTOFF/RATE);return (1-k)/(1+k),k/(1+k)

def block(old,new,state):
 old=np.asarray(old,dtype=np.float64);new=np.asarray(new,dtype=np.float64)
 if old.shape!=new.shape or old.ndim!=2 or old.shape[1]!=2 or state.shape!=(2,):raise ValueError('Invalid stereo/state shape')
 if not np.isfinite(old).all() or not np.isfinite(new).all() or not np.isfinite(state).all():raise ValueError('Nonfinite input/state')
 a,b=coefficients();out=np.empty_like(new)
 for i in range(len(new)):
  for ch in range(2):
   delta=old[i,ch]-new[i,ch];bd=b*delta;correction=bd+state[ch];state[ch]=bd+a*correction
   # A zero correction preserves same-input sample bits, including signedzero.
   out[i,ch]=new[i,ch]+correction if correction!=0. else new[i,ch]
 if not np.isfinite(out).all() or not np.isfinite(state).all():raise ValueError('Nonfinite postprocessor output/state')
 return out

def process(old,new,partitions):
 if not partitions or any(n<1 for n in partitions):raise ValueError('Invalid partitions')
 state=np.zeros(2,dtype=np.float64);result=np.empty(np.asarray(new).shape,dtype=np.float64);frame=0;index=0
 while frame<len(new):
  end=min(len(new),frame+partitions[index%len(partitions)]);result[frame:end]=block(old[frame:end],new[frame:end],state);frame=end;index+=1
 return result,state

def selftests():
 a,b=coefficients();assert 0<a<1 and abs(2*b/(1-a)-1)<1e-14
 rng=np.random.default_rng(4002026);old=rng.normal(size=(4096,2));new=rng.normal(size=(4096,2))
 baseline,s1=process(old,new,[64]);partitioned,s2=process(old,new,[1,3,17,64,129,7]);assert baseline.tobytes()==partitioned.tobytes() and s1.tobytes()==s2.tobytes()
 identical=old.astype(np.float32);identical[0]=[-0.,0.];same,zero=process(identical,identical,[1,7,64]);assert same.astype('<f4').tobytes()==identical.astype('<f4').tobytes() and np.array_equal(zero,[0.,0.])
 dc,dcstate=process(np.ones((4096,2)),np.zeros((4096,2)),[64]);assert np.max(abs(dc[-1]-1))<1e-13
 # Independent analytic impulse kernel, not a second recurrence implementation.
 impulse=np.zeros((512,2));impulse[0]=1;observed,_=process(impulse,np.zeros_like(impulse),[3,7,1]);kernel=np.r_[b,b*(1+a)*a**np.arange(511)];err=float(np.max(abs(observed-kernel[:,None])));assert err<1e-14
 rejected=0
 for value in [np.nan,np.inf,-np.inf]:
  bad=np.zeros((3,2));bad[1,0]=value
  try:process(bad,np.zeros_like(bad),[1])
  except ValueError:rejected+=1
 assert rejected==3
 return {'passed':True,'pole':a,'b0_b1':b,'DC_gain':2*b/(1-a),'Nyquist_gain':0.,'zero_difference_bit_identity':True,'partition_byte_identity':True,
 'canonical_partition':[64],'alternate_partitions':[1,3,17,64,129,7],'analytic_impulse_max_absolute_error':err,'nonfinite_inputs_rejected':rejected,
 'scope':'Synthetic data only. One fixed coefficient set; no pilot PCM opened.'}
