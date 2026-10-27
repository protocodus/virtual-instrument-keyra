#!/usr/bin/env python3
"""Authorized fixed-gain presentation only; never synthesize a piano or fit gains."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,math,os,subprocess
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import scipy
from scipy.io import wavfile
from run import OUT,ROOT,sha,read,write,record,verify,check_authorization,now

def pcm24(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','s24le','-acodec','pcm_s24le','-'])
def decode(data):
 b=np.frombuffer(data,np.uint8).reshape(-1,3).astype(np.int32);q=b[:,0]+(b[:,1]<<8)+(b[:,2]<<16);q=(q^0x800000)-0x800000
 return q.reshape(-1,2).astype(np.float64)/2**23

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--authorization',required=True);args=parser.parse_args()
 auth,protocol=check_authorization(args.authorization,'export')
 env=protocol['numerical_environment'];assert np.__version__==env['numpy'] and scipy.__version__==env['scipy']
 assert subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]==env['ffmpeg']
 verify(auth['render_receipt']);assert Path(auth['render_receipt']['path']).resolve()==(OUT/'render/receipt.json').resolve()
 receipt=read(auth['render_receipt']['path']);assert receipt['passed'] and receipt['protocol']['sha256']==sha(OUT/'protocol.json')
 for row in receipt['outputs']:verify(row)
 dest=OUT/'listening'
 if dest.exists():raise ValueError('Export attempt exists; preserve it, no silent rerun')
 dest.mkdir();write(dest/'opening-started.json',{'at_utc':now(),'authorization':record(args.authorization),'protocol':record(OUT/'protocol.json'),'render_receipt':auth['render_receipt']})
 old=np.fromfile(OUT/'render/baseline.f32le','<f4').reshape(-1,2);new=np.fromfile(OUT/'render/candidate.f32le','<f4').reshape(-1,2)
 assert old.shape==new.shape==(432000,2) and np.isfinite(old).all() and np.isfinite(new).all()
 spec=importlib.util.spec_from_file_location('immutable_keyra_presentation',protocol['presentation_source']['path']);presentation=importlib.util.module_from_spec(spec);spec.loader.exec_module(presentation)
 impulse=presentation.room_ir();assert impulse.shape==(86400,2) and hashlib.sha256(impulse.astype('<f8').tobytes()).hexdigest()==protocol['presentation']['IR_sha256']
 fade=np.linspace(1,0,7200)[:,None];target=10**(-2/20);entries=[]
 def stats(x):
  stereo=float(np.mean(x*x));mono=np.mean(x,axis=1);powers=np.mean(x*x,axis=0)
  return {'frames':len(x),'finite':bool(np.isfinite(x).all()),'sample_peak':float(np.max(np.abs(x))),'true_peak_4x':float(presentation.true_peak(x)),'stereo_rms':math.sqrt(stereo),'mono_rms':float(np.sqrt(np.mean(mono*mono))),'mono_energy_relative_average_channel_db':float(10*np.log10(np.mean(mono*mono)/stereo)),'left_right_balance_db':float(10*np.log10(powers[0]/powers[1])),'left_right_correlation':float(np.corrcoef(x.T)[0,1])}
 versions={}
 for kind in ['room','dry']:
  versions[kind]={}
  for name,source in [('old',old),('modal',new)]:
   value=presentation.presentation(source.astype(np.float64),impulse,.16) if kind=='room' else source.astype(np.float64)
   value*=protocol['presentation'][kind+'_gain'];value[-7200:]*=fade;value*=protocol['presentation']['original_common_gain'];value*=protocol['presentation']['fixed_shared_safety'];checks=stats(value)
   if not checks['finite'] or checks['true_peak_4x']>target+3e-7 or checks['sample_peak']>=1:
    write(dest/'unsafe.json',{'kind':kind,'name':name,'statistics':checks,'recipe_unchanged':True});raise ValueError('Fixed recipe unsafe; no gain changed')
   versions[kind][name]=value
 for kind in ['room','dry']:
  joined=np.concatenate([versions[kind]['old'],np.zeros((24000,2)),versions[kind]['modal']]);wav=dest/('old-then-modal-'+kind+'.wav');flac=wav.with_suffix('.flac');wavfile.write(wav,48000,joined.astype(np.float32))
  command=['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24',str(flac)];subprocess.run(command,check=True)
  decoded=pcm24(flac);assert decoded==pcm24(wav) and len(decoded)==888000*6 and decoded[432000*6:456000*6]==bytes(24000*6)
  if kind=='room':assert hashlib.sha256(decoded[:432000*6]).hexdigest()==protocol['presentation']['expected_old_room_PCM24_sha256']
  quantized=decode(decoded);checks={name:stats(value) for name,value in [('combined',quantized),('old',quantized[:432000]),('modal',quantized[456000:])]}
  assert all(v['finite'] and v['true_peak_4x']<=target+3e-7 and v['sample_peak']<1 for v in checks.values())
  stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=codec_name,sample_rate,channels,time_base,duration_ts,bits_per_raw_sample','-of','json',str(flac)],text=True))['streams'][0]
  assert stream=={'codec_name':'flac','sample_rate':'48000','channels':2,'time_base':'1/48000','duration_ts':888000,'bits_per_raw_sample':'24'}
  entries.append({'kind':kind,'flac':record(flac),'wav':record(wav),'pcm24_sha256':hashlib.sha256(decoded).hexdigest(),'old_PCM24_sha256':hashlib.sha256(decoded[:432000*6]).hexdigest(),'encoder_command':command,'lossless_pcm24_decode_exact':True,'gap_pcm24_zero':True,'statistics':checks,'stream':stream})
 for row in protocol['bindings']:verify(row)
 manifest={'at_utc':now(),'status':'PRIVATE diagnostic on observed score; no promotion or listener verdict','protocol':record(OUT/'protocol.json'),'render_receipt':auth['render_receipt'],'authorization':record(args.authorization),'order':['old OriginalControl','modal transient completion of same physical trajectory'],'segment_start_seconds':[0,9.5],'segment_duration_seconds':9,'entries':entries,'same_fixed_gains':True,'candidate_RMS_matching':False,'default_changed':False,'listener_verdict':None,'public_audio_written':False,'realtime_claim':False,'limitations':protocol['limitations']};write(dest/'manifest.json',manifest);print(json.dumps({'manifest':record(dest/'manifest.json'),'entries':entries},indent=2))
if __name__=='__main__':main()
