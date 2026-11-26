// Isolated benchmark diagnostic, deliberately starts the V8 sampler after warm-up.
import { Session } from 'node:inspector/promises';
import { writeFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';
import { KeyraDSP } from '../../fun/keyra/dsp/piano.mjs';

const rate = 48000, frames = 128;
const chords = [[48,55,60,64,71], [45,52,57,60,67], [41,53,57,60,67], [43,53,59,62,67]];
const piano = new KeyraDSP(rate);
const left = new Float32Array(frames), right = new Float32Array(frames);
function phrase(rounds) {
  for (let pass = 0; pass < rounds; ++pass) for (const chord of chords) for (let block = 0; block < 96; ++block) {
    if (block === 0) chord.forEach((note, i) => piano.noteOn(note, 71 + 6 * i));
    if (block === 12) piano.controlChange(64, 102);
    if (block === 57) for (const note of chord) piano.noteOff(note);
    if (block === 89) piano.controlChange(64, 0);
    piano.render(left, right);
  }
}
function summarize(profile, preset) {
  const nodes = new Map(profile.nodes.map(n => [n.id, n]));
  const byFunction = new Map();
  const parents = new Map();
  for (const n of profile.nodes) for (const id of n.children || []) parents.set(id, n.id);
  const key = n => n.callFrame.functionName + ' @ ' +
    (n.callFrame.url ? n.callFrame.url.split('/').at(-1) : 'V8') + ':' + (n.callFrame.lineNumber + 1);
  const touch = n => {
    const name = key(n);
    if (!byFunction.has(name)) byFunction.set(name, { name, self: 0, inclusive: 0, lines: new Map() });
    return byFunction.get(name);
  };
  for (const n of profile.nodes) for (const { line, ticks } of n.positionTicks || []) {
    const lines = touch(n).lines;
    lines.set(line, (lines.get(line) || 0) + ticks);
  }
  let total = 0;
  profile.samples.forEach((id, i) => {
    const us = profile.timeDeltas[i];
    total += us;
    touch(nodes.get(id)).self += us;
    const seen = new Set();
    while (id) {
      const entry = touch(nodes.get(id));
      if (!seen.has(entry)) { entry.inclusive += us; seen.add(entry); }
      id = parents.get(id);
    }
  });
  const sorted = [...byFunction.values()].sort((a, b) => b.self - a.self);
  console.log('PROFILE ' + preset + ' total=' + (total / 1e6).toFixed(3) + 's samples=' + profile.samples.length);
  for (const e of sorted.slice(0, 15)) {
    const lines = [...e.lines].sort((a,b) => b[1]-a[1]).slice(0,6);
    console.log('HOT ' + e.name + ' self=' + (100*e.self/total).toFixed(2) + '% inclusive=' +
      (100*e.inclusive/total).toFixed(2) + '% source-lines=' + JSON.stringify(lines));
  }
}
for (const [preset, label] of [[0, 'concert'], [7, 'hall']]) {
  piano.allSoundOff();
  piano.setPreset(preset);
  phrase(1);
  const sampler = new Session();
  sampler.connect();
  await sampler.post('Profiler.enable');
  await sampler.post('Profiler.setSamplingInterval', { interval: 1000 });
  await sampler.post('Profiler.start');
  const start = performance.now();
  phrase(2);
  const end = performance.now();
  const { profile } = await sampler.post('Profiler.stop');
  sampler.disconnect();
  writeFileSync(label + '.cpuprofile', JSON.stringify(profile));
  console.log(label + ' mean ' + ((end-start)/768).toFixed(3) + 'ms');
  summarize(profile, label);
}
