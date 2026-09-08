#!/usr/bin/env node
// Read-only on-board proof of PCM/DMA progress; does not start, stop or reset.
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const delta = (a,b) => (a-b) >>> 0;
function analyze(samples, seconds=20) {
  const errors=[];
  const fields=['host_ms','uptime_ms','generation','rx_bytes','pcm_frames',
    'sample_rate','pcm_age_ms','underruns','free_heap'];
  if(seconds<20) errors.push('minimum window is 20 seconds');
  if(samples.length<2 || samples.some(s=>s.error)) return {pass:false,errors:[...errors,'missing health samples']};
  if(samples.some(s=>fields.some(k=>!Number.isFinite(s[k]) || s[k]<0)))
    return {pass:false,errors:[...errors,'invalid health counters']};
  const a=samples[0], b=samples.at(-1);
  const wallMs=b.host_ms-a.host_ms, boardMs=delta(b.uptime_ms,a.uptime_ms);
  const frames=delta(b.pcm_frames,a.pcm_frames);
  const underruns=delta(b.underruns,a.underruns);
  if(wallMs<seconds*1000 || boardMs<seconds*1000) errors.push('window too short');
  if(samples.some(s=>s.generation!==a.generation || s.sample_rate!==a.sample_rate))
    errors.push('station or format changed');
  if(!a.sample_rate || samples.some(s=>s.pcm_age_ms>500)) errors.push('PCM stopped progressing');
  if(underruns || samples.some((s,i)=>i && s.underruns!==samples[i-1].underruns))
    errors.push('DMA underrun or counter reset');
  const ratio=boardMs && a.sample_rate ? frames*1000/(a.sample_rate*boardMs) : 0;
  if(ratio<0.98 || ratio>1.03) errors.push('PCM duration does not match elapsed time');
  if(delta(b.rx_bytes,a.rx_bytes)===0) errors.push('no stream bytes received');
  return {pass:errors.length===0,errors,wallMs,boardMs,frames,
    audioMs:a.sample_rate?frames*1000/a.sample_rate:0,underruns,ratio,
    minHeap:Math.min(...samples.map(s=>s.free_heap))};
}
function readHealth(base) {
  return new Promise((resolve,reject)=>{
    const req=http.get(new URL('/api/native/audio',base),{agent:false},res=>{
      if(res.statusCode!==200) {res.resume();reject(new Error('HTTP '+res.statusCode));return;}
      let body='';
      res.setEncoding('utf8');res.on('data',c=>body+=c);
      res.on('end',()=>{try {resolve(JSON.parse(body));}catch(e){reject(e);}});
      res.on('error',reject);
    });
    // socket.setTimeout alone does not bound Windows TCP SYN retransmission.
    const timer=setTimeout(()=>req.destroy(new Error('health timeout')),4000);
    req.on('close',()=>clearTimeout(timer));
    req.on('error',reject);
  });
}
async function main() {
  const args=process.argv.slice(2), opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
  const seconds=Number(opt('--seconds','25'));
  if(!Number.isFinite(seconds)||seconds<20||seconds>600) throw new Error('--seconds must be 20..600');
  const base=opt('--base','http://192.168.100.6');
  const output=opt('--output','.build/esp8266-audio-continuity/results.json');
  const report={date:new Date().toISOString(),base,seconds,samples:[]};
  const begin=performance.now();
  do {
    const start=performance.now();
    try {
      const s=await readHealth(base);
      report.samples.push({...s,host_ms:performance.now()-begin,request_ms:performance.now()-start});
      console.log(JSON.stringify(report.samples.at(-1)));
    }catch(e){report.samples.push({host_ms:performance.now()-begin,error:e.message});console.log('FAIL',e.message);}
    const elapsed=performance.now()-begin;
    if(elapsed>=(seconds+2)*1000 && report.samples.length>=2) break;
    await new Promise(r=>setTimeout(r,1000));
  }while(true);
  report.result=analyze(report.samples,seconds);
  fs.mkdirSync(path.dirname(output),{recursive:true});
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report.result));
  process.exitCode=report.result.pass?0:1;
}
module.exports={analyze};
if(require.main===module) main().catch(e=>{console.error(e);process.exitCode=1;});
