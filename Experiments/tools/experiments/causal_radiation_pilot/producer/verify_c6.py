#!/usr/bin/env python3
"""Independently reread the archived posthoc C6 model-path diagnosis; no render."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from scipy import signal
PACKAGE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pilot-root',type=Path,required=True,help='Directory containing C6v4/ and C6v12/ raw producer outputs');args=parser.parse_args()
 report_path=PACKAGE/'evidence/C6-path-attribution.json';expected=json.loads(report_path.read_text());pole=np.exp(-2*np.pi*24/48000);checks=0;maximum=0
 for case in expected['cases']:
  folder=args.pilot_root/case['id']
  for old,digest in case['artifacts'].items():
   p=folder/Path(old).name
   if sha(p)!=digest:raise ValueError('Historical input mismatch: '+str(p))
  trace=np.fromfile(folder/'trace.f64le','<f8').reshape(-1,15);old=np.fromfile(folder/'baseline.f32le','<f4').reshape(-1,2).astype(float);new=np.fromfile(folder/'candidate.f32le','<f4').reshape(-1,2).astype(float)
  body=signal.lfilter([pole,-pole],[1,-pole],trace[:,2:4],axis=0);correction=signal.lfilter([pole,-pole],[1,-pole],trace[:,4:6],axis=0)
  arrays={'old':old,'new':new,'raw_B':body,'old_instant_C':old-body,'new_causal_C':correction}
  for row in case['windows']:
   lo,hi=row['window_seconds'];first=4800+round(lo*48000);last=4800+round(hi*48000);n=last-first;win=signal.windows.hann(n,sym=False);freq=np.fft.rfftfreq(n,1/48000);spectra={key:np.fft.rfft(value[first:last]*win[:,None],axis=0) for key,value in arrays.items()}
   for band,values in row['bands'].items():
    a,b=map(float,band[:-2].split('-'));mask=(freq>=a)&(freq<b);power={key:float(np.sum(abs(z[mask])**2)) for key,z in spectra.items()}
    for key in arrays:
     observed=10*np.log10(power[key]/power['old']);target=values[key]['power_db_relative_old'];error=abs(observed-target);maximum=max(maximum,float(error));checks+=1
     if error>1e-9:raise ValueError(f'C6 projection changed: {case["id"]} {band} {key}')
 print(json.dumps({'passed':True,'diagnostic_sha256':sha(report_path),'verified_power_comparisons':checks,'maximum_dB_difference':maximum,'read_only':True,'source_identity_limit':'Explains model paths; reference LF source remains unassigned.'},indent=2))
if __name__=='__main__':main()
