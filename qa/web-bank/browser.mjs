import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { chromium } from 'playwright';
const root=resolve(process.argv[2]);
const server=createServer(async (req,res)=>{
  const path=new URL(req.url, 'http://localhost').pathname;
  if(path==='/')return res.setHeader('Content-Type','text/html').end('<title>Keyra benchmark</title>');
  if(path.endsWith('/bench.js'))return res.setHeader('Content-Type','text/javascript').end(
    "import {KeyraDSP} from './dsp/piano.mjs'; class Test extends AudioWorkletProcessor {constructor(){super();this.p=new KeyraDSP(sampleRate);this.p.setPreset(0);for(const n of [36,48,52,55,59,64])this.p.noteOn(n,90,1)} process(i,o){this.p.render(o[0][0],o[0][1]); return true}} registerProcessor('bench',Test);"
  );
  const f=resolve(root,'.'+path);if(!f.startsWith(root+sep))return res.writeHead(404).end();
  try{res.setHeader('Content-Type','text/javascript').end(await readFile(f))}catch{res.writeHead(404).end()}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:'+server.address().port);
 let expected=null;
 for(const mode of process.argv.slice(3)){
  const result=await page.evaluate(async mode=>{
    const seconds=2,ctx=new OfflineAudioContext(2,seconds*48000,48000);
    await ctx.audioWorklet.addModule('/'+mode+'/bench.js');
    const node=new AudioWorkletNode(ctx,'bench',{numberOfInputs:0,numberOfOutputs:1,outputChannelCount:[2]});
    node.connect(ctx.destination);let last=performance.now(); const timing=[];
    function mark(){const now=performance.now();timing.push(Math.round(now-last));last=now}
    for(const t of [0.5,1,1.5])ctx.suspend(t).then(()=>{mark();ctx.resume()});
    const pcm=await ctx.startRendering();mark();
    const bytes=new Uint8Array(seconds*48000*8);
    bytes.set(new Uint8Array(pcm.getChannelData(0).buffer));
    bytes.set(new Uint8Array(pcm.getChannelData(1).buffer),bytes.byteLength/2);
    const sha=await crypto.subtle.digest('SHA-256',bytes);const hash=[...new Uint8Array(sha)].map(x=>x.toString(16).padStart(2,'0')).join('');
    return {timing,hash};
  },mode);
  console.log('BROWSERBANK',mode,result.hash,result.timing.join(','));
  if(expected===null)expected=result.hash;
  else if(result.hash!==expected)throw Error('Browser PCM mismatch in '+mode);
 }
}finally{await browser.close();server.close()}
