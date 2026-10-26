#!/usr/bin/env python3
"""Restore or verify the pinned, licensed reference recordings from manifest.json."""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,struct,subprocess
import numpy as np
from scipy.io import wavfile
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def decoded_pcm_identity(path):
    """Hash signed PCM24 little-endian samples in frame/channel order, without headers."""
    with path.open('rb') as f:
        header=f.read(12)
        if header[:4]!=b'RIFF' or header[8:]!=b'WAVE':
            raise RuntimeError(f'Expected RIFF/WAVE PCM24: {path}')
        while True:
            chunk=f.read(8)
            if len(chunk)!=8:raise RuntimeError(f'Missing WAV format: {path}')
            kind,size=struct.unpack('<4sI',chunk)
            if kind==b'fmt ':
                fmt=f.read(size)
                if len(fmt)<16:raise RuntimeError(f'Invalid WAV format: {path}')
                code,_,_,_,_,bits=struct.unpack_from('<HHIIHH',fmt)
                valid_bits=struct.unpack_from('<H',fmt,18)[0] if code==0xfffe and len(fmt)>=40 else bits
                if bits!=24 or valid_bits!=24:raise RuntimeError(f'Expected 24-bit PCM: {path}')
                break
            f.seek(size+(size&1),1)
    rate,samples=wavfile.read(path)
    if samples.dtype.kind!='i' or samples.dtype.itemsize!=4 or samples.ndim not in (1,2):
        raise RuntimeError(f'Expected decoded signed PCM24: {path}')
    if np.any(samples&255):raise RuntimeError(f'Invalid PCM24 precision: {path}')
    # SciPy left-justifies PCM24 in int32; discard its zero low byte and fix
    # byte order explicitly so the digest is platform/container independent.
    packed=np.ascontiguousarray(samples,dtype='<i4').reshape(-1).view(np.uint8).reshape(-1,4)[:,1:].tobytes()
    return {'sha256':hashlib.sha256(packed).hexdigest(),'encoding':'s24le-interleaved',
            'sample_rate':int(rate),'channels':1 if samples.ndim==1 else int(samples.shape[1]),
            'frames':int(len(samples)),'pcm_bits':24}

def verify_wav(item,path):
    identity=decoded_pcm_identity(path)
    if identity!=item.get('decoded_pcm'):
        raise RuntimeError(f'Decoded PCM or format mismatch: {item["id"]}')
    return {'id':item['id'],'container_matches':sha(path)==item['wav_sha256'],
            'decoded_pcm_matches':True,'sample_rate':identity['sample_rate'],
            'channels':identity['channels']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify-only',action='store_true')
    p.add_argument('--jobs',type=int,default=4)
    a=p.parse_args()
    if a.jobs<1:p.error('--jobs must be positive')
    manifest=json.loads((ROOT/'manifest.json').read_text())
    def get(item):
        flac=PROJECT/item['flac_path'];wav=PROJECT/item['wav_path']
        if not flac.exists():
            if a.verify_only:raise RuntimeError(f'Missing {flac}')
            flac.parent.mkdir(parents=True,exist_ok=True)
            tmp=flac.with_suffix('.download')
            subprocess.run(['curl','-fsSL','--retry','2','--max-time','120',item['source_url'],'-o',str(tmp)],check=True)
            if sha(tmp)!=item['flac_sha256']:
                tmp.unlink();raise RuntimeError(f'Download checksum mismatch: {item["id"]}')
            tmp.replace(flac)
        if sha(flac)!=item['flac_sha256']:raise RuntimeError(f'FLAC checksum mismatch: {item["id"]}')
        if not wav.exists():
            if a.verify_only:raise RuntimeError(f'Missing {wav}')
            wav.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(flac),'-c:a','pcm_s24le',str(wav)],check=True)
        # A different WAV header is acceptable only when every decoded sample
        # and its rate/channel/precision/frame metadata exactly match the pin.
        return verify_wav(item,wav)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs)as pool:done=list(pool.map(get,manifest['samples']))
    print(json.dumps({'verified':True,'samples':len(done),'source_commit':manifest['commit'],
                     'container_matches':all(r['container_matches'] for r in done),
                     'results':done},indent=2))
if __name__=='__main__':main()
