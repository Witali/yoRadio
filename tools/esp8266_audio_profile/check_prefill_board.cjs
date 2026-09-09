#!/usr/bin/env node
// Opt-in OTA and live RAM/continuity check. No UART, Wi-Fi or filesystem uploads.
const fs = require('node:fs'), path = require('node:path');
const http = require('node:http'), crypto = require('node:crypto');
const zlib = require('node:zlib');
const {analyze} = require('../test_esp8266_audio_continuity.cjs');
const args = process.argv.slice(2), mode = args[0];
const opt = (key, fallback) => args.includes(key) ? args[args.indexOf(key)+1] : fallback;
const base = opt('--base', 'http://192.168.100.6');
const file = opt('--output', '.build/esp8266-prefill-board/result.json');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const report = {date:new Date().toISOString(), mode, base};
const save = () => {
  fs.mkdirSync(path.dirname(file), {recursive:true});
  fs.writeFileSync(file, JSON.stringify(report,null,2)+'\n');
};
function request(uri, body, headers={}) {
  return new Promise((resolve,reject) => {
    const start = performance.now();
    const req = http.request(new URL(uri,base), {method:body?'POST':'GET',
      agent:false, headers:{Connection:'close',...headers}}, res => {
      const chunks=[];
      res.on('data',b=>chunks.push(b));
      res.on('error',reject);
      res.on('end',()=>{
        try {
          const wire=Buffer.concat(chunks);
          const decoded=res.headers['content-encoding']==='gzip'?zlib.gunzipSync(wire):wire;
          resolve({http:res.statusCode,ms:performance.now()-start,wire_bytes:wire.length,
            wire_sha256:crypto.createHash('sha256').update(wire).digest('hex'),
            body:decoded.toString('utf8')});
        } catch(error) {reject(error);}
      });
    });
    const timer=setTimeout(()=>req.destroy(Error('request timeout '+uri)),body?120000:5000);
    req.on('close',()=>clearTimeout(timer)); req.on('error',reject);
    req.end(body);
  });
}
async function json(uri) {
  const response=await request(uri);
  if(response.http!==200)throw Error('HTTP '+response.http+' '+uri);
  return {data:JSON.parse(response.body),ms:response.ms};
}
async function command(value) {
  return new Promise((resolve,reject) => {
    const ws=new WebSocket(new URL('/ws',base).href.replace(/^http:/,'ws:'));
    const messages=[], start=performance.now(); let finished=false, linger;
    const finish=error=>{
      if(finished)return; finished=true; clearTimeout(timeout);clearTimeout(linger);
      ws.onerror=null;if(ws.readyState===WebSocket.OPEN)ws.close();
      if(error)reject(error);else resolve({value,ms:performance.now()-start,messages});
    };
    const timeout=setTimeout(()=>finish(Error('WebSocket command timeout')),8000);
    ws.onopen=()=>{ws.send(value);linger=setTimeout(()=>finish(),1500)};
    ws.onmessage=event=>{try {messages.push(JSON.parse(event.data))}catch{}};
    ws.onerror=()=>finish(Error('WebSocket connection failed'));
  });
}
async function main() {
  if(mode==='snapshot') {
    report.status=(await json('/api/native/status')).data;
    report.audio=(await json('/api/native/audio')).data;
    report.index=await command('getindex=1');
    report.playlist=await request('/data/playlist.csv');
  } else if(mode==='command') {
    const value=opt('--command','getindex=1');
    if(!/^(getindex=1|stop=1|next=1|prev=1|play=\d+|volume=\d+)$/.test(value))
      throw Error('Unsupported test command');
    report.command=await command(value);
    report.status=(await json('/api/native/status')).data;
  } else if(mode==='ota') {
    const firmware=opt('--firmware','');
    if(!firmware)throw Error('--firmware is required; no implicit update');
    const app=fs.readFileSync(firmware);
    const manifest=JSON.parse(fs.readFileSync(path.join(path.dirname(firmware),'manifest.json')));
    report.sha256=crypto.createHash('sha256').update(app).digest('hex');
    if(report.sha256.toUpperCase()!==manifest.app_sha256.toUpperCase() ||
        app.length!==manifest.bytes || app.length>0xf0000 || app[0]!==0xe9)
      throw Error('Native app/manifest validation failed');
    report.before=(await json('/api/native/status')).data;
    const stable=(await json('/api/native/status')).data;
    if(stable.app_address!==report.before.app_address ||
       ![0x10000,0x110000].includes(stable.app_address) || stable.firmware!=='esp8266-native')
      throw Error('Unstable/unsupported application slot; no upload');
    report.target=stable.app_address===0x10000?0x110000:0x10000;
    report.source_revision=manifest.source_revision;
    const boundary='YoRadioPrefillAppOnly';
    const body=Buffer.concat([
      Buffer.from('--'+boundary+'\r\nContent-Disposition: form-data; name="updatetarget"\r\n\r\nfw\r\n--'+boundary+'\r\nContent-Disposition: form-data; name="update"; filename="app.bin"\r\nContent-Type: application/octet-stream\r\n\r\n'),
      app, Buffer.from('\r\n--'+boundary+'--\r\n')]);
    save(); console.log('OTA',report.before.app_address,'->',report.target,app.length,'bytes');
    try {report.upload=await request('/update',body,{
      'Content-Type':'multipart/form-data; boundary='+boundary,'Content-Length':body.length});
    } catch(error) {report.upload={error:error.message};}
    console.log('UPLOAD',JSON.stringify(report.upload)); save();
    report.polls=[];
    for(let n=0;n<30;n++) {
      await sleep(2000);
      try {
        const state=(await json('/api/native/status')).data;
        report.polls.push({attempt:n+1,...state});
        if(state.app_address===report.target) {report.after=state;break;}
      } catch(error) {report.polls.push({attempt:n+1,error:error.message});}
      if(n%3===0)console.log('Waiting for new OTA slot',n+1);
    }
    report.pass=!!report.after;
    if(!report.pass)throw Error('New slot not confirmed; do not retry OTA or use serial automatically');
  } else if(mode==='sample') {
    const seconds=Number(opt('--seconds','30'));
    if(!Number.isFinite(seconds)||seconds<20||seconds>600)throw Error('--seconds must be 20..600');
    report.label=opt('--label','audio'); report.samples=[];
    const start=performance.now();
    do {
      const row={};
      try {
        const health=await json('/api/native/audio');
        Object.assign(row,health.data,{host_ms:performance.now()-start,audio_request_ms:health.ms});
        const state=await json('/api/native/status');
        Object.assign(row,{status:state.data,status_request_ms:state.ms});
      } catch(error) {row.error=error.message;row.host_ms=performance.now()-start;}
      report.samples.push(row);save();
      console.log(JSON.stringify({label:report.label,ms:Math.round(row.host_ms),
        free:row.free_heap,low:row.status?.min_heap,web_stack:row.status?.web_stack_free,
        rssi:row.status?.rssi,pcm_age:row.pcm_age_ms,underruns:row.underruns,error:row.error}));
      if(performance.now()-start >= (seconds+2)*1000)break;
      await sleep(1000);
    } while(true);
    report.continuity=analyze(report.samples,seconds);
    const valid=report.samples.filter(s=>!s.error);
    report.memory={samples:valid.length,failed:report.samples.length-valid.length,
      free_min:valid.length?Math.min(...valid.flatMap(s=>[s.free_heap,s.status.free_heap])):null,
      free_max:valid.length?Math.max(...valid.flatMap(s=>[s.free_heap,s.status.free_heap])):null,
      allocator_low:valid.length?Math.min(...valid.map(s=>s.status.min_heap)):null,
      web_stack_min:valid.length?Math.min(...valid.map(s=>s.status.web_stack_free)):null};
    report.pass=report.continuity.pass&&report.samples.every(s=>s.status?.playing);
  } else throw Error('Mode: snapshot | command | ota | sample');
  save(); console.log('RESULT',JSON.stringify({pass:report.pass,memory:report.memory,
    continuity:report.continuity,status:report.status,output:file}));
  if(report.pass===false)process.exitCode=1;
}
if(require.main===module)main().catch(error=>{
  report.error=error.stack;save();console.error(error.message);process.exitCode=1;
});
