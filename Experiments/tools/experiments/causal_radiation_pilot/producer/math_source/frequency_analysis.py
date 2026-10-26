from pathlib import Path
import json,hashlib,datetime
import numpy as np
OUT=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();meta=json.loads((OUT/'static-metadata.json').read_text());board=np.fromfile(OUT/'board.f64le','<f8').reshape(-1,11);modes=np.fromfile(OUT/'modes.f64le','<f8').reshape(-1,23)
w,sigma,c,s,d=board[:,1:6].T;B=board[:,6:9];M=board[:,9:11];R=np.array(meta['R']);h=meta['dt'];G=B.T@B
D0=(1-c)*(1-c*d*d)+(s*d)**2;kx0=h*s*d/D0;kv0=h*(1-c)/D0;d0=w*kx0+2*sigma*kv0

def continuous(omega):
 inv=1/(w*w-omega*omega+2j*sigma*omega);Y=B.T@((1j*omega*inv)[:,None]*B);T=M.T@((-omega*omega*inv)[:,None]*B)
 return T@np.linalg.inv(np.eye(3)+R[:,None]*Y)
def discrete(omega):
 z=np.exp(1j*omega*h);a=1-c/z;den=a*(1-c*d*d/z)+(s*d/z)**2;kx=h*s*d/z/den;kv=h*a/den
 Y=B.T@((kv-h/2)[:,None]*B);load=np.linalg.inv(np.eye(3)+R[:,None]*Y)
 return {'endpoint':(M.T@((1-w*kx-2*sigma*kv)[:,None]*B))@load,'dc_corrected_endpoint':(M.T@((d0-w*kx-2*sigma*kv)[:,None]*B))@load,'mid_velocity_difference':(M.T@(((1-1/z)/h*(kv-h/2))[:,None]*B))@load}
def compare(a,b):
 na=np.linalg.norm(a);nb=np.linalg.norm(b);delta=np.linalg.norm(b-a);dot=np.vdot(a,b)
 return {'reference_stereo_l2':float(na),'candidate_stereo_l2':float(nb),'gain_db':float(20*np.log10(nb/na)) if na*nb else None,'relative_complex_error':float(delta/na) if na else None,'vector_phase_degrees':float(np.angle(dot,deg=True)) if abs(dot) else None,'channel_gain_db':[float(20*np.log10(abs(y/x))) if abs(x*y) else None for x,y in zip(a,b)],'channel_phase_degrees':[float(np.angle(y/x,deg=True)) if abs(x*y) else None for x,y in zip(a,b)]}
selected=modes[np.isin(modes[:,1],[48,60,84])];rows=[];representatives=[]
for row in selected:
 omega=row[6];g=int(row[3]);target=continuous(omega)[:,g];values=discrete(omega)
 # Existing model routine's sampled H in binary export independently binds Python.
 exported=np.array([complex(row[11],row[12]),complex(row[13],row[14])]);assert np.max(abs(target-exported))<=1e-10*max(1,np.max(abs(exported)))
 rows.append({'note':int(row[1]),'unison':int(row[2]),'group':g,'partial':int(row[4]),'pol':int(row[5]),'Hz':float(omega/(2*np.pi)),'ratio':float(row[9]),'drive_weight':float(row[10]),'original_complex_coefficient_l2':float(np.linalg.norm(row[15:19])),'comparisons':{k:compare(target,v[:,g]) for k,v in values.items()}})
for hz in [0.,10.,27.5,31.,65.4,130.8,261.6,750.,784.5,1500.,3000.,6000.,10000.,13000.,15000.,18000.,19000.]:
 omega=2*np.pi*hz;target=continuous(omega);values=discrete(omega)
 for g in range(3):representatives.append({'Hz':hz,'group':g,'comparisons':{k:compare(target[:,g],v[:,g]) for k,v in values.items()},'absolute_discrete_norms':{k:float(np.linalg.norm(v[:,g])) for k,v in values.items()}})
rounding={};old=modes[:,15:19];exact=modes[:,19:23];norm=np.linalg.norm(exact,axis=1);diff=np.linalg.norm(old-exact,axis=1);valid=norm>1e-20;rounding={'maximum_absolute_component_error':float(np.max(abs(old-exact))),'maximum_complex_relative_l2_error':float(np.max(diff[valid]/norm[valid])),'zero_reference_modes':int(np.sum(~valid)),'total_modes':len(modes)}
summary={}
for variant in ['endpoint','dc_corrected_endpoint','mid_velocity_difference']:
 summary[variant]={}
 for note in [48,60,84]:
  rr=[r for r in rows if r['note']==note];gain=np.array([r['comparisons'][variant]['gain_db'] for r in rr]);phase=np.array([r['comparisons'][variant]['vector_phase_degrees'] for r in rr]);weights=np.array([r['original_complex_coefficient_l2'] for r in rr]);err=np.array([r['comparisons'][variant]['relative_complex_error'] for r in rr])
  summary[variant][str(note)]={'modal_rows':len(rr),'gain_db_min':float(gain.min()),'gain_db_max':float(gain.max()),'maximum_absolute_vector_phase_degrees':float(abs(phase).max()),'coefficient_weighted_relative_complex_error':float(np.sqrt(np.sum(weights*weights*err*err)/np.sum(weights*weights))),'maximum_relative_complex_error':float(err.max())}
report={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Math-only3readoutcomparison; no candidateaudio or parameterfitting','sample_rate':meta['rate'],'R':R.tolist(),'Gram':G.tolist(),'DC_feedthrough_coefficient_range':[float(d0.min()),float(d0.max())],'continuous_model':'ExactHc=T*(I+R*Y)^-1 fromfrozenradiationTransfer; storedexportH checked','discrete_model':'F=D*rotation*D, force solve(I+.5hRG)f=U-R*vfree; Ymid=B^T(Kv-.5h)B; Tendpoint=mic^T(1-wKx-2sigmaKv)B','dc_corrected_readout':'d0_j=w*Kx(1)+2sigma*Kv(1), D0=(1-c)*(1-c*d^2)+(s*d)^2. Replaceforcefeedthrough1 byd0; preservesdynamics/poles/loadwork andzeroDC permode.','mid_velocity_difference_readout':'(1-z^-1)/h timesmidpointmodalvelocity; exactzeroDC withknownhalf-samplephase/HFresponse','raw_legacy_coefficient_rounding':rounding,'summary_by_note':summary,'representative_rows':representatives,'all_selected_actual_modal_rows':rows,'input_sha256':{str(p):sha(p) for p in [OUT/'static.json',OUT/'board.f64le',OUT/'modes.f64le',OUT/'frequency_analysis.py']},'limits':['DCcorrectedreadoutchoice notyetfrozen; root/mathreviewchoosebeforeanycandidateaudio.','Relativeerrorsnearzeros/channellocalcancellation canbelarge; fullvalues andabsolute norms retained.','Coefficientweight isapriori oldobservermappingnorm, notnoteenergy orrecordingfitweight.','Thesearecontinuous/discretefrequencyresponses, not audibility orpassivity ofnoncollocatedpressure.']}
(OUT/'frequency-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print('rounding',rounding)
for k,v in summary.items():print(k,v)
for hz in [0.,31.,784.5,10000.,19000.]:
 row=next(r for r in representatives if r['Hz']==hz and r['group']==1);print(hz,{k:{kk:vv for kk,vv in v.items() if kk in ['gain_db','channel_phase_degrees']} for k,v in row['comparisons'].items()},row['absolute_discrete_norms'])
