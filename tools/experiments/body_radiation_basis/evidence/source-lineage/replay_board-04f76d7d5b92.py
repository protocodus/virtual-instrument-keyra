from pathlib import Path
import json,hashlib,datetime
import numpy as np
OUT=Path(__file__).resolve().parent;RATE=48000;DT=1/RATE;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
coef=np.fromfile(OUT/'board-coefficients.f64le',dtype='<f8').reshape(-1,11);assert coef.shape==(475,11)
trace=np.fromfile(OUT/'contact.f64le',dtype='<f8').reshape(-1,21);reference=np.fromfile(OUT/'board.f64le',dtype='<f8').reshape(-1,2)
w,sigma,c,s,damp=coef[:,1:6].T;port=coef[:,6:9];mic=coef[:,9:11];windows={'C3':round(1.147563*RATE),'F5':round(2.160396*RATE)}
q=np.zeros(475,dtype=np.float32);p=q.copy();frames=max(windows.values())+4800
contributions={n:np.zeros((4800,475,2),dtype=np.float32) for n in windows};replay=np.zeros((frames,2));force_obs=replay.copy();restoring_obs=replay.copy()
for frame in range(frames):
 oldq=q.astype(np.float64);v=p.astype(np.float64)*damp
 q=(c*oldq+s*v).astype(np.float32);p=((c*v-s*oldq)*damp).astype(np.float32)
 force=np.zeros(475)
 for g in range(3):force-=port[:,g]*trace[frame,4+g]
 p=(p.astype(np.float64)+DT*force/w).astype(np.float32)
 restoring=-w*w*q.astype(np.float64)-2*sigma*w*p.astype(np.float64)
 pressure=(restoring+force)[:,None]*mic;replay[frame]=np.sum(pressure,axis=0);force_obs[frame]=np.sum(force[:,None]*mic,axis=0);restoring_obs[frame]=np.sum(restoring[:,None]*mic,axis=0)
 for name,start in windows.items():
  if start<=frame<start+4800:contributions[name][frame-start]=pressure.astype(np.float32)
for name,arr in contributions.items():arr.tofile(OUT/(name+'-board-mode-pressure.f32le'))
replay.tofile(OUT/'board-replay.f64le');force_obs.tofile(OUT/'board-force-observer.f64le');restoring_obs.tofile(OUT/'board-restoring-observer.f64le')
delta=replay-reference[:frames];rms=lambda x:float(np.sqrt(np.mean(x*x)))
summary={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Offlineboard475mode replay, driven by exact frozen original-model Schurforces, no second full-network render','frames':frames,'coefficient_exporter':'StaticPiano constructor only, same immutable oldPreparedModel/calibration; no simulation or preset changes','source_sha256':{str(p):sha(p) for p in [OUT/'export_coefficients.cpp',OUT/'export_coefficients',OUT/'board-coefficients.f64le',OUT/'key-coefficients.f64le',OUT/'contact.f64le',OUT/'replay_board.py']},'maximum_replay_pressure_error':float(abs(delta).max()),'replay_rms_error':rms(delta),'replay_null_db_relative_rms':20*np.log10(rms(delta)/rms(reference[:frames])) if rms(delta) else None,'force_sign':'RecordedSchurtotal incontactcolumns4..6; actualboardmodalforce=-sum(port[g]*total[g])','mode_pressure_layout':'C3/F5 files:4800frames×475modes×2channels float32, firstframeonroundednote-event','windows':windows,'limits':['Boardreplay preserves original per-mode float q/p writes and doublecoefficient arithmetic; mode summation/reduction may differ in NumPy.','Per-mode audio is an observer decomposition under the intact recorded junction drive, not a disconnected-source physics ablation.','Canonical transientstem=board−baseStringSum; it does not equal rawboardpressure or an isolated soundboard source.']}
(OUT/'board-replay.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
