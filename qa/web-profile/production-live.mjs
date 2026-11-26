import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { setTimeout as sleep } from 'node:timers/promises';
import { chromium } from 'playwright';

const origin = 'https://protocodus.cz';
const tracked = execFileSync('git', ['ls-files', '-z', 'fun/keyra', 'fun/oregana', 'fun/shared/instrument-audio.js', 'fun/index.html'], {encoding:'utf8'}).split('\0').filter(Boolean);
const sha256 = body => createHash('sha256').update(body).digest('hex');
const entries = await Promise.all(tracked.map(async path => ({path, url: origin + '/' + path.replace(/index\.html$/, ''), hash: sha256(await readFile(path))})));
let pending = [...entries];
for (let attempt=1; attempt<=20 && pending.length; ++attempt) {
  const stale = [];
  for (let i=0; i<pending.length; i+=5) {
    await Promise.all(pending.slice(i,i+5).map(async entry => {
      try {
        const response = await fetch(entry.url, {signal: AbortSignal.timeout(15000)});
        const actual = sha256(Buffer.from(await response.arrayBuffer()));
        if (!response.ok || actual !== entry.hash) throw new Error('HTTP ' + response.status + ', SHA-256 ' + actual);
        console.log('RELEASE', entry.path, actual);
      } catch (e) {
        console.log('PENDING', entry.path, e.message);
        stale.push(entry);
      }
    }));
  }
  pending = stale;
  if (pending.length && attempt<20) { console.log('CDN retry', attempt, pending.length); await sleep(30000); }
}
console.log('VERIFIED ASSETS', entries.length - pending.length, '/', entries.length);
assert.deepEqual(pending.map(x=>x.path), [], 'Files still outside the published release');

function meter() {
  const qa = window.liveQA = {left:0,right:0,difference:0, events:[]};
  const Native = window.AudioWorkletNode;
  window.AudioWorkletNode = class extends Native {
    constructor(...args) {
      super(...args);
      const context = args[0];
      const splitter=context.createChannelSplitter(2);
      this.connect(splitter);
      const analysers=[0,1].map(ch => {
        const analyser=context.createAnalyser(); analyser.fftSize=2048;
        splitter.connect(analyser,ch);
        return analyser;
      });
      const data=analysers.map(a => new Float32Array(a.fftSize));
      setInterval(() => {
        if(context.state!=='running') return;
        analysers.forEach((a,ch)=>a.getFloatTimeDomainData(data[ch]));
        for(let i=0;i<data[0].length;++i) {
          qa.left=Math.max(qa.left, Math.abs(data[0][i]));
          qa.right=Math.max(qa.right, Math.abs(data[1][i]));
          qa.difference=Math.max(qa.difference, Math.abs(data[0][i]-data[1][i]));
        }
      }, 20);
      const post = this.port.postMessage.bind(this.port);
      this.port.postMessage=(m,...extra)=>{
        qa.events.push(m,...(m.events||[]),...(m.notes||[]));
        return post(m,...extra);
      };
    }
  };
}
const browser=await chromium.launch({args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
try {
  const fun=await browser.newPage();
  await fun.goto(origin+'/fun/',{waitUntil:'domcontentloaded'});
  const destinations=await fun.locator('a[href]').evaluateAll(as=>as.map(a=>new URL(a.href).pathname.replace(/\/$/,'')));
  for(const name of ['oregana','keyra']) assert(destinations.includes('/fun/'+name), 'Fun listing missing '+name);
  await fun.close();
  for(const name of ['keyra','oregana']) for(const input of ['pointer','keyboard']) {
    const page=await browser.newPage({viewport:{width:1440,height:900}});
    page.setDefaultTimeout(30000);
    const errors=[];
    page.on('pageerror', e=>errors.push(e.message));
    page.on('requestfailed', r=>console.log('REQUEST FAILURE',r.url(),r.failure()));
    await page.addInitScript(meter);
    const response=await page.goto(origin+'/fun/'+name+'/',{waitUntil:'domcontentloaded'});
    assert.equal(response.status(),200);
    const selector=name==='keyra'?'#keyboard [data-note="60"]':'#keyboard [data-division="0"] [data-note="60"]';
    const key=page.locator(selector);
    await key.waitFor();
    assert.notEqual(await page.locator('#audio-start').getAttribute('aria-pressed'),'true');
    if(input==='pointer') {
      await key.scrollIntoViewIfNeeded();
      const box=await key.boundingBox();
      await page.mouse.move(box.x+box.width*.5,box.y+box.height*.86);
      await page.mouse.down();
    } else {
      await page.keyboard.down('q');
    }
    const expected=name==='oregana' && input==='pointer'?'divisionNoteOn':'noteOn';
    try {
      await page.waitForFunction(expected=>window.liveQA.events.some(m=>m.type===expected && m.note===60) &&
        window.liveQA.left>.003 && window.liveQA.right>.003 && window.liveQA.difference>.0001 &&
        document.querySelector('#audio-status').dataset.renderer==='simd',expected);
    } catch(e) {
      console.error('AUDIO FAILURE',name,input,await page.evaluate(()=>({qa:window.liveQA, status:document.querySelector('#audio-status').textContent, renderer:document.querySelector('#audio-status').dataset.renderer})));
      throw e;
    }
    const measured=await page.evaluate(()=>({left:window.liveQA.left,right:window.liveQA.right,difference:window.liveQA.difference,renderer:document.querySelector('#audio-status').dataset.renderer}));
    if(input==='pointer') await page.mouse.up(); else await page.keyboard.up('q');
    await page.waitForFunction(expectedOff=>window.liveQA.events.some(m=>m.type===expectedOff && m.note===60), expected.replace('On','Off'));
    console.log('PRODUCTION STEREO', name, input, JSON.stringify(measured),page.url());
    assert.deepEqual(errors,[]);
    await page.close();
  }
} finally {
  await browser.close();
}
