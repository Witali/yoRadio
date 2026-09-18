#!/usr/bin/env node
// Live playlist tests: ordinary Play/Stop only, no OTA, UART, reset or uploads.
// Endpoint samples bracket a request-free interval. They can perturb its edges;
// only Opus has an autonomous, request-free DMA window in this firmware.
const fs = require('node:fs'), path = require('node:path');
const {request} = require('../esp8266_opus_profile/run_memory_probe.cjs');
const {analyze} = require('../test_esp8266_audio_continuity.cjs');
const {analyze: analyzeQuiet} = require('../esp8266_opus_profile/run_quiet_window.cjs');
const delta = (a,b) => (a-b) >>> 0;
const sleep = ms => new Promise(r => setTimeout(r,ms));

function command(base,value) {
  return new Promise(resolve => {
    const ws = new WebSocket(new URL('/ws',base).href.replace(/^http:/,'ws:'));
    const result = {value,messages:[]}, start = performance.now();
    let finished=false, linger;
    function finish(error) {
      if(finished)return; finished=true; clearTimeout(timer); clearTimeout(linger);
      result.ms=performance.now()-start; if(error)result.error=error;
      if(ws.readyState===WebSocket.OPEN||ws.readyState===WebSocket.CONNECTING)ws.close();
      resolve(result);
    }
    const timer=setTimeout(()=>finish('WebSocket command timeout'),8000);
    ws.onopen=()=>{ws.send(value);result.sent=true;linger=setTimeout(()=>finish(),1500);};
    ws.onmessage=e=>{try{result.messages.push(JSON.parse(e.data));}catch{}};
    ws.onerror=()=>finish('WebSocket connection failed');
  });
}
async function read(base,route) {
  try{return await request(base,route);}catch(e){return {error:e.message};}
}
function sample(response,hostMs) {
  return response.http===200 ? {...response.body,host_ms:hostMs} :
    {host_ms:hostMs,error:response.error || 'HTTP '+response.http};
}
function evaluate(r) {
  const errors=[];
  const start=r.before?.audio, end=r.after?.audio;
  const before=r.before?.status?.body, after=r.after?.status?.body;
  const confirmed=r.command?.messages?.some(m=>m.current===r.station);
  if(!confirmed)errors.push('selected station not confirmed over WebSocket');
  if(r.command?.error)errors.push(r.command.error);
  if(!before?.playing||before?.connecting||before?.error||!after?.playing||after?.connecting||after?.error)
    errors.push('station not playing cleanly at both boundaries');
  if(!before||!after)errors.push('missing status sample');
  if((before&&before.station!==r.name)||(after&&after.station!==r.name))errors.push('station identity mismatch');
  if(before&&after&&before.app_address!==after.app_address)errors.push('application slot changed');
  const continuity=analyze([sample(start||{},0),sample(end||{},r.observed_ms||0)],60);
  if(!continuity.pass)errors.push(...continuity.errors);
  if(start?.http===200&&end?.http===200&&end.body.uptime_ms<start.body.uptime_ms)
    errors.push('board uptime reset');
  const opus=before?.codec==='OPUS' || after?.codec==='OPUS';
  let quiet;
  if(opus) {
    quiet=analyzeQuiet(r.quiet?.body);
    if(!quiet.pass)errors.push(...quiet.errors.map(x=>'quiet: '+x));
    const q=r.quiet?.body;
    if(q?.generation!==start?.body?.generation||q?.start_ms<start?.body?.uptime_ms||q?.end_ms>end?.body?.uptime_ms)
      errors.push('quiet window is outside this station observation');
  }
  const driverDelta=start?.http===200&&end?.http===200 ?
    delta(end.body.tx_driver_fail,start.body.tx_driver_fail):null;
  const activeFormat=before?.playing&&after?.playing&&before?.codec===after?.codec;
  return {pass:!errors.length,errors,continuity,quiet,tx_driver_fail_delta:driverDelta,
    format_confirmed_while_playing:!!activeFormat,
    codec:after?.codec,bitrate:after?.bitrate,rssi:[before?.rssi,after?.rssi],
    boundary_heap:[start?.body?.free_heap,end?.body?.free_heap],
    boot_min_heap:after?.min_heap,
    limitation:'No acoustic capture. Boundary requests may perturb output; boot minimum is not a per-station minimum.'};
}
async function main() {
  const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
  const base=opt('--base','http://192.168.100.6'),dir=opt('--directory');
  const ids=opt('--stations','500,498,502,37,507,512,513').split(',').map(Number);
  const initialPath=opt('--initial');
  if(!dir||!initialPath||!ids.length||ids.some(x=>!Number.isInteger(x)||x<1))throw Error('Need --directory, --initial and valid --stations');
  if(fs.existsSync(dir))throw Error('Use a new evidence directory');
  const initial=JSON.parse(fs.readFileSync(initialPath,'utf8'));
  const rows=initial.playlist.body.trim().split(/\r?\n/).map(s=>s.split('\t'));
  if(ids.some(id=>!rows[id-1]))throw Error('Station outside saved device playlist');
  fs.mkdirSync(dir,{recursive:true});
  const report={date:new Date().toISOString(),base,playlist_sha256:initial.playlist.wire_sha256,
    seconds_without_runner_requests:65,warmup_seconds:12,attempts:[]};
  const save=()=>fs.writeFileSync(path.join(dir,'summary.json'),JSON.stringify(report,null,2)+'\n');
  for(let n=0;n<ids.length;n++) {
    const id=ids[n],r={station:id,name:rows[id-1][0],url:rows[id-1][1],date:new Date().toISOString()};
    report.attempts.push(r);save();
    console.log('START '+(n+1)+'/'+ids.length+' '+id+' '+r.name);
    r.command=await command(base,'play='+id);save();
    await sleep(12000);
    r.before={status:await read(base,'/api/native/status'),memory:await read(base,'/api/native/opus-stream')};
    r.before.audio=await read(base,'/api/native/audio');
    const started=performance.now();save();
    console.log('QUIET 65s '+id+' '+JSON.stringify({status:r.before.status.body,audio:r.before.audio.body,error:r.before.audio.error}));
    for(const ms of [30000,30000,5000]) {await sleep(ms);console.log('WAIT '+id+' '+Math.round((performance.now()-started)/1000)+'s (no board requests)');}
    r.after={audio:await read(base,'/api/native/audio')};r.observed_ms=performance.now()-started;
    r.quiet=await read(base,'/api/native/audio?quiet=1');
    r.after.status=await read(base,'/api/native/status');
    r.after.memory=await read(base,'/api/native/opus-stream');
    r.result=evaluate(r);save();
    console.log('RESULT '+id+' '+JSON.stringify(r.result));
    if(r.before.audio.http!==200&&r.after.audio.http!==200&&r.after.status.http!==200) {
      report.aborted='No board observation; do not queue another Play or reset';save();break;
    }
  }
  report.stop=await command(base,'stop=1');
  await sleep(2000);report.final_status=await read(base,'/api/native/status');save();
  console.log('DONE '+JSON.stringify(report.attempts.map(r=>({station:r.station,...r.result}))));
}
module.exports={evaluate};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
