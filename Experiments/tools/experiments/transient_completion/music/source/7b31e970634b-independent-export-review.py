#!/usr/bin/env python3
"""Audit existing synthetic listening files; no model steps or new audio files."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,hashlib,subprocess,datetime,importlib.util,math
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve,resample_poly
ROOT=Path('/workspace/virtual-instrument-keyra');OUT=ROOT/'out/full-transient-music/v4';A=ROOT/'out/full-transient-music-audit/v4';L=OUT/'listening'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def verify(x):
 p=Path(x['path']);assert sha(p)==x['sha256']
 if 'bytes' in x:assert p.stat().st_size==x['bytes']
p=read(OUT/'protocol.json');m=read(L/'manifest.json')
for key in ['protocol','render_receipt','authorization']:verify(m[key])
assert not m['recording_global_acceptance'] and m['recording_cases_passed']==33 and m['recording_cases_total']==34 and m['failed_recording_cases']==['C8v12']
assert m['same_fixed_gains'] and not m['candidate_RMS_matching'] and not m['default_changed'] and m['listener_verdict'] is None and not m['realtime_claim']
assert m['segment_start_seconds']==[0,9.5] and m['segment_duration_seconds']==9
baseline=np.fromfile(OUT/'render/baseline.f32le','<f4').reshape(432000,2);candidate=np.fromfile(OUT/'render/candidate.f32le','<f4').reshape(432000,2)
verify(p['presentation_source']);spec=importlib.util.spec_from_file_location('frozen_presentation_audit',p['presentation_source']['path']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
# Invoke only frozen procedural room-IR builder; no piano rendering function.
ir=module.room_ir();assert ir.shape==(86400,2) and hashlib.sha256(ir.astype('<f8').tobytes()).hexdigest()==p['presentation']['IR_sha256']
fade=np.linspace(1,0,p['presentation']['fade_frames'])[:,None];entries=[]
def pcm24(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','s24le','-acodec','pcm_s24le','-'])
def decode(raw):
 a=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32);v=a[:,0]+(a[:,1]<<8)+(a[:,2]<<16);v=(v^0x800000)-0x800000
 return v.reshape(-1,2).astype(np.float64)/(2**23)
def truepeak(value):
 peak=0.
 for start in range(0,len(value),48000*8):
  region=value[max(0,start-128):min(len(value),start+48000*8+128)]
  peak=max(peak,float(np.max(np.abs(resample_poly(region,4,1,axis=0,window=('kaiser',12.0))))))
 return peak
for entry in m['entries']:
 verify(entry['wav']);verify(entry['flac']);kind=entry['kind'];expected=[]
 for source in [baseline,candidate]:
  x=source.astype(float)
  if kind=='room':
   mid=x.mean(axis=1);reflections=np.stack([fftconvolve(mid,ir[:,ch])[:len(x)] for ch in range(2)],axis=1);x=x+p['presentation']['room_wet']*reflections
  x*=p['presentation'][kind+'_gain'];x[-len(fade):]*=fade;x*=p['presentation']['original_common_gain'];x*=p['presentation']['fixed_shared_safety'];expected.append(x)
 joined=np.concatenate([expected[0],np.zeros((24000,2)),expected[1]]).astype('<f4');rate,wave=wavfile.read(entry['wav']['path']);assert rate==48000 and wave.dtype==np.float32 and wave.shape==(888000,2) and wave.tobytes()==joined.tobytes()
 raw=pcm24(entry['flac']['path']);other=pcm24(entry['wav']['path']);assert raw==other and len(raw)==888000*6 and raw[432000*6:456000*6]==bytes(24000*6)
 assert hashlib.sha256(raw).hexdigest()==entry['pcm24_sha256'] and hashlib.sha256(raw[:432000*6]).hexdigest()==entry['old_PCM24_sha256']
 if kind=='room':assert entry['old_PCM24_sha256']==p['presentation']['expected_old_room_PCM24_sha256']
 decoded=decode(raw);stats={}
 for name,x in [('combined',decoded),('old',decoded[:432000]),('modal',decoded[456000:])]:
  tp=truepeak(x);sp=float(np.max(abs(x)));rms=float(np.sqrt(np.mean(x*x)));assert np.isfinite(x).all() and sp<1 and tp<=10**(-2/20)+3e-7
  old_stats=entry['statistics'][name];assert tp==old_stats['true_peak_4x'] and sp==old_stats['sample_peak'] and rms==old_stats['stereo_rms']
  stats[name]={'true_peak_4x':tp,'true_peak_dbfs':20*math.log10(tp),'sample_peak':sp,'stereo_rms':rms}
 stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=codec_name,sample_rate,channels,time_base,duration_ts,bits_per_raw_sample','-of','json',entry['flac']['path']],text=True))['streams'][0];assert stream==entry['stream']
 entries.append({'kind':kind,'float32_WAV_reconstructed_from_native_outputs_and_frozen_shared_presentation_bytes_exact':True,'FLAC_and_WAV_PCM24_decode_exact':True,'PCM24_frames':888000,'gap_24000_stereo_frames_exact_zero':True,'old_PCM24_sha256':entry['old_PCM24_sha256'],'stream':stream,'recomputed_statistics':stats})
result={'passed':True,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only independent audit of existing synthetic export files. Rebuilt presentation only in memory; no model steps, files exported, new recordings, fitted gains or listening verdict.','listening_manifest':rec(L/'manifest.json'),'protocol':rec(OUT/'protocol.json'),'render_review':rec(A/'independent-render-review.json'),'IR_sha256':p['presentation']['IR_sha256'],'fixed_shared_gains':{x:p['presentation'][x] for x in ['room_gain','dry_gain','original_common_gain','fixed_shared_safety']},'candidate_RMS_matching':False,'same_left_right_filter_and_presentation':True,'entries':entries,'global_recording_acceptance':False,'recording_case_count':34,'recording_pass_count':33,'failed_recording_cases':['C8v12'],'default_changed':False,'listener_verdict':None,'realtime_claim':False}
path=A/'independent-export-review.json';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'review':rec(path),'passed':True,'entries':entries},indent=2))
