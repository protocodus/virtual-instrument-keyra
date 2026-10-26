#!/usr/bin/env python3
"""Record provenance and lightweight onset observations without changing audio."""
from pathlib import Path
import json,re,hashlib
import numpy as np
from scipy.io import wavfile
root=Path(__file__).resolve().parent
project=root.parent
items=json.loads((root/'downloaded.json').read_text())
notes=(root/'upstream/notes.txt').read_text()
ranges={int(m[0]):(int(m[1]),int(m[2]))for m in re.findall(r'vel_(\d+)\.txt" lovel=(\d+) hivel=(\d+)',notes)}
keys={'C':0,'F#':6}
for item in items:
    note=item['note'];octave=int(note[-1]);pitch=note[:-1];midi=12*(octave+1)+keys[pitch];region=(midi-21)//3+1
    fs,x=wavfile.read(project/item['wav_path']);audio=x.astype(np.float64)/(2**31)
    energy=np.mean(audio*audio,axis=1);block=max(1,fs//1000);frames=len(energy)//block
    env=np.sqrt(energy[:frames*block].reshape(frames,block).mean(axis=1))
    threshold=max(float(np.max(env[:fs//block]))*.01,1e-7)
    over=np.flatnonzero(env>threshold);onset=float(over[0]*block/fs) if len(over) else None
    offsets=(root/f'upstream/vel_{item["layer"]:02}.txt').read_text()
    offset=int(re.search(r'\$OFF%02d\s+(\d+)'%region,offsets).group(1))
    vrange=ranges[item['layer']]
    item.update(midi_note=midi,model_velocity=int(np.floor(np.mean(vrange)+.5)),
        sfz_velocity_range=list(vrange),sfz_default_start_offset_frames=0,
        sfz_optional_full_cc98_start_offset_frames=offset,
        observed_onset_seconds=onset,frames=len(x),sample_rate=fs,channels=x.shape[1],pcm_bits=24,
        duration_seconds=len(x)/fs,sample_peak_dbfs=float(20*np.log10(np.max(np.abs(audio)))),
        channel_power_rms_dbfs=float(10*np.log10(np.mean(energy))))
manifest={
 'dataset_title':'Salamander Grand Piano V3, selected original note recordings',
 'recording_author':'Alexander Holm',
 'distribution_maintainer':'kinwie / sfzinstruments',
 'instrument':'Yamaha C5 acoustic grand piano',
 'capture':{'sample_rate':48000,'bits':24,'channels':2,'microphones':'Two AKG C414 in AB configuration approximately 12 cm above the strings','velocity_layers':16,'sampled_keys':'Minor thirds beginning at A0','room':None,'acquisition_pedal_state':None,'physical_strike_velocity':None,'normalization_or_noise_reduction_history':None},
 'repository':'https://github.com/sfzinstruments/SalamanderGrandPiano',
 'commit':'3382bf9496bba2486f5ab0de55a264d1dfc38404',
 'original_distribution':'https://archive.org/details/SalamanderGrandPianoV3',
 'project_page':'https://sfzinstruments.github.io/pianos/salamander/',
 'license':'Creative Commons Attribution 3.0 Unported',
 'license_url':'https://creativecommons.org/licenses/by/3.0/',
 'license_copy':'reference/upstream/LICENSE-CC-BY-3.0.txt',
 'acquisition_date':'2026-10-25',
 'modifications':{'flac':'None; byte-identical files downloaded from pinned repository commit.','wav':'Lossless decode to signed PCM24 WAV using ffmpeg; original sample rate/channel count retained. No gain, trim, EQ, denoising, pitch correction or looping applied by this acquisition.'},
 'velocity_interpretation':'model_velocity is rounded midpoint of the upstream SFZ playback bin, not a measured recording MIDI value or calibrated physical hammer velocity.',
 'offset_interpretation':'Upstream offset control defaults to0; optional full-CC98 offsets are playback-response trims, not known hammer-contact times. observed_onset_seconds is an estimate from the first1ms stereo-power RMS block exceeding1% of peak RMS in the firstsecond, with floor1e-7; use consistent independent onset alignment in comparisons.',
 'benchmark_limitations':['These are real acoustic piano recordings prepared as a sample library; the recording/editing chain is not a calibrated instrument measurement.','Unmodified natural samples are used; the SFZ natural tuning offsets are allzero. Retuned SFZ pitch offsets are not applied.','Acquisition pedal state and exact key-release time are not documented in the fetched upstream metadata. These files cannot independently establish pedal realism or noteoff dynamics.','The selected main note regions contain no loop instructions. The separate hammer, string-resonance and pedal release layers are not mixed into these note files.','Training/holdout labels are suggested; establish final split before fitting and disclose it.'],
 'samples':items,
 'upstream_text_files':[{'path':str(p.relative_to(project)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted((root/'upstream').glob('*'))]
}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'samples':len(items),'duration_range_seconds':[min(i['duration_seconds']for i in items),max(i['duration_seconds']for i in items)],'onset_range_seconds':[min(i['observed_onset_seconds']for i in items),max(i['observed_onset_seconds']for i in items)],'velocities':sorted(set(i['model_velocity']for i in items))},indent=2))
