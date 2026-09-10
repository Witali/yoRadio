#!/usr/bin/env node
// Explicit diagnostic POST only. No UART, Wi-Fi management, automatic reset or OTA.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { performance } = require('node:perf_hooks');
const {analyzeOutput} = require('./output_benchmark_result.cjs');
const args = process.argv.slice(2);
const option = (name, fallback) => { const i=args.indexOf(name); return i<0?fallback:args[i+1]; };
const base = option('--base', 'http://192.168.100.6');
const output = path.resolve(option('--output', '.build/esp8266-opus-board-results.json'));
const interval = Number(option('--interval-ms','1500'));
if (!Number.isInteger(interval) || interval < 250 || interval > 60000) throw Error('--interval-ms must be 250..60000');
const names = ['mono12 SILK', 'mono24 hybrid', 'stereo64 CELT', 'stereo128 CELT', 'stereo510 CELT'];
const report = {date: new Date().toISOString(), base, mode: 'raw packets in RAM; no network audio or PCM output',
  timing: 'task_us excludes other tasks, includes charged ISR and instrumentation; wall_us includes preemption', snapshots: []};
function save() { fs.mkdirSync(path.dirname(output), {recursive:true}); fs.writeFileSync(output, JSON.stringify(report,null,2)+'\n'); }
function request(uri, method='GET') {
  return new Promise((resolve,reject) => {
    const started=performance.now();
    const req=http.request(new URL(uri,base),{method,agent:false,headers:{Connection:'close','Content-Length':0}},res=>{
      let body='';
      res.on('data',chunk=>{body+=chunk; if(body.length>16384)req.destroy(Error('response bound exceeded'));});
      res.on('error',reject);
      res.on('end',()=>{try {if(res.statusCode<200||res.statusCode>=300)throw Error(`HTTP ${res.statusCode}: ${body}`);
        resolve({ms:performance.now()-started,data:JSON.parse(body)});}catch(error){reject(error);}});
    });
    const timer = setTimeout(()=>req.destroy(Error('request timeout')),8000);
    req.on('close',()=>clearTimeout(timer)); req.on('error',reject); req.end();
  });
}
(async()=>{
  report.before=await request('/api/native/status');
  const previous=await request('/api/native/opus-benchmark');
  if (previous.data.physical_output) {
    report.mode = 'own raw Opus packets from flash to physical PDM/DMA, no audio network or Ogg demux';
    report.timing = 'decode/output wall stages; full-pipeline task CPU including charged ISR and instrumentation, not decoder-only CPU';
  }
  report.interval_ms = interval;
  if (!args.includes('--observe')) {
    if([1,2].includes(previous.data.state))throw Error('Benchmark already running; use --observe');
    report.start=await request('/api/native/opus-benchmark','POST');
  }
  const started=performance.now();let progress='';
  while(performance.now()-started<300000) {
    try {
      const snapshot=await request('/api/native/opus-benchmark');
      report.snapshots.push(snapshot); save();
      const s=snapshot.data,key=`${s.state}/${s.case}/${s.round}`;
      if(key!==progress) { console.log('PROGRESS',key,'error',s.error); progress=key; }
      if(s.state===3||s.state===4) {
        report.final=s;
        report.comparison=s.results.map((item,i)=>s.physical_output ?
          ({name:names[i],...item,continuity:analyzeOutput(item)}) : ({name:names[i],...item,
          audio_duration_us:item.samples*1000000/48000,
          task_budget_percent:item.samples?item.task_us*4.8/item.samples:null,
          wall_budget_percent:item.samples?item.wall_us*4.8/item.samples:null,
          task_budget_minus_empty_estimate_percent:item.samples?
            Math.max(0,item.task_us-s.empty_task_us*item.packets)*4.8/item.samples:null}));
        report.after=await request('/api/native/status'); save();
        console.log(JSON.stringify({final:report.final,comparison:report.comparison},null,2));
        if(s.state!==3)throw Error('Device benchmark error '+s.error);
        if (s.physical_output && report.comparison.some(item=>!item.continuity.pass))
          throw Error('Physical output continuity gate failed; results retained');
        return;
      }
    } catch(error) {
      if(report.final)throw error;
      report.snapshots.push({error:error.message}); save();
      console.log('OBSERVATION',error.message);
    }
    await new Promise(resolve=>setTimeout(resolve,interval));
  }
  throw Error('Observation timeout; do not reset/restart without inspecting board status');
})().catch(error=>{report.error=error.message;save();console.error(error.message);process.exitCode=1;});
