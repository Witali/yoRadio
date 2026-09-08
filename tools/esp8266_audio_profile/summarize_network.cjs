#!/usr/bin/env node
const fs=require('node:fs');
const {readLog}=require('./summarize_mp3_matrix.cjs');
function summarize(log) {
  const count=Number(/net_bench: begin cases=(\d+)/.exec(log)?.[1]||7);
  const cases=Array.from({length:count},(_,id)=>({case:id,seconds:[]}));
  const cpu=new Map();
  for(const line of log.split(/\r?\n/)) {
    if(line.includes('net_cpu: case=')) {
      const fields=Object.fromEntries([...line.matchAll(/(\w+)=(-?\d+)/g)]
        .map(m=>[m[1],Number(m[2])]));
      const row=cpu.get(fields.case)||{case:fields.case,tasks:[]};
      const task=/task=(\S+)/.exec(line)?.[1];
      if(task)row.tasks.push({name:task,id:fields.id,runtime_us:fields.runtime_us,existed:fields.existed===1});
      else Object.assign(row,fields);
      cpu.set(fields.case,row);continue;
    }
    if(!line.includes('net_bench: case='))continue;
    const fields=Object.fromEntries([...line.matchAll(/(\w+)=(-?\d+)/g)]
      .map(m=>[m[1],Number(m[2])]));
    const row=cases[fields.case];
    if(!row)continue;
    if(line.includes(' begin ')) {
      row.path=/path=(\S+)/.exec(line)?.[1];row.rssi_before=fields.rssi;
      row.output=fields.output===1;
    } else if(fields.second!==undefined) {
      row.seconds[fields.second]=fields.bytes;
    } else Object.assign(row,fields);
  }
  for(const c of cases) {
    c.target_kbps=Number(/rate=(\d+)/.exec(c.path||'')?.[1]||0);
    c.completed=c.wall_us>=19900000 && c.error===0 && c.seconds.filter(Number.isFinite).length===20;
    c.rx_kbps=c.wall_us ? c.bytes*8000/c.wall_us : null;
    c.rate_ratio=c.target_kbps && c.rx_kbps!==null ? c.rx_kbps/c.target_kbps : null;
    c.pcm_seconds=c.rate ? c.pcm_frames/c.rate : 0;
    c.ready_probe_supported=(c.ready_probes||0)>0;
    if(!c.ready_probe_supported)c.ready_max=null;
    c.kept_up=c.completed && (!c.target_kbps || c.rate_ratio>=0.98);
  }
  for(const row of cpu.values()) {
    for(const task of row.tasks)task.percent=row.total_us ? task.runtime_us*100/row.total_us : null;
    row.accounted_percent=row.tasks.reduce((sum,t)=>sum+(t.percent||0),0);
    row.idle_percent=row.tasks.find(t=>t.name==='IDLE')?.percent ?? null;
    row.non_idle_percent=row.idle_percent===null ? null : 100-row.idle_percent;
  }
  return {complete:log.includes('net_bench: complete'),cases,cpu:[...cpu.values()]};
}
module.exports={summarize};
if(require.main===module) {
  const [file,save]=process.argv.slice(2);
  if(!file)throw Error('Usage: summarize_network.cjs capture.log [report.json]');
  const log=readLog(file), report=summarize(log),json=JSON.stringify(report,null,2)+'\n';
  if(save) {
    fs.writeFileSync(save,json);
    // Keep all benchmark records, without SSID/BSSID or unrelated startup messages.
    fs.writeFileSync(save.replace(/\.json$/,'')+'.log',
      log.split(/\r?\n/).filter(s=>s.includes('net_bench:')||s.includes('net_cpu:')).join('\n')+'\n');
  }
  console.log(json);
  if(!report.complete || report.cases.some(c=>!c.completed))process.exitCode=1;
}
