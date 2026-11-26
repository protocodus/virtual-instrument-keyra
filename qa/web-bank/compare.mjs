import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
const modes = process.argv.slice(2);
for (const mode of modes) {
  const { KeyraDSP } = await import('../engines/' + mode + '/dsp/piano.mjs');
  for (const scenario of [
    { name: 'Concert chord', rate: 48000, notes:[36,48,52,55,59,64], preset:0 },
    { name: 'Hall damper', rate: 44100, notes:[21,42,45,66,70,79,100,108], preset:7 },
  ]) {
    const piano = new KeyraDSP(scenario.rate);
    piano.setPreset(scenario.preset);
    piano.controlChange(64,scenario.preset ? 100 : 0,1);
    scenario.notes.forEach((note,index) => piano.noteOn(note, 70+index*5, 1));
    const buffers=[new Float32Array(128),new Float32Array(128)], hash=createHash('sha256'), times=[];
    for (let repeat=0;repeat<5;repeat++) {
      if(repeat===4) {piano.pitchBend(.35,1); for(const note of scenario.notes) piano.noteOff(note,1)}
      const begin=performance.now();
      for(let j=0;j<188;j++){piano.render(...buffers);for(const b of buffers)hash.update(b)}
      times.push(Math.round(performance.now()-begin));
    }
    console.log('BANKCHECK', mode, scenario.name, hash.digest('hex'), times.join(','));
  }
}
