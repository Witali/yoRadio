#!/usr/bin/env node
// Offline summary only; never contacts the board or changes pass thresholds.
const fs=require('node:fs'),path=require('node:path');
const directory=process.argv[2];if(!directory)throw Error('Evidence directory required');
const report={date:new Date().toISOString(),cases:[],servers:[],note:'TCP retransmissions can include congestion/window effects; not proof of RF loss. Autonomous windows are wall time, not CPU utilization.'};
for(const entry of fs.readdirSync(directory,{withFileTypes:true})) {
 const file=path.join(directory,entry.name);
 if(entry.isDirectory()&&fs.existsSync(path.join(file,'summary.json'))) {
  const s=JSON.parse(fs.readFileSync(path.join(file,'summary.json'),'utf8'));
  report.cases.push({name:entry.name,url:s.url,pass:s.pass??false,init:s.init?.data,
   windows:s.windows.map(w=>({result:w.measurement?.result,generation:w.measurement?.window?.generation,
    age_ms:w.measurement?.window?.age_ms,free_heap:w.health?.data?.free_heap,
    min_heap:w.status?.data?.min_heap,pcm_age_ms:w.health?.data?.pcm_age_ms,
    rssi:w.status?.data?.rssi,playing:w.status?.data?.playing,error:w.status?.data?.error,
    health_error:w.health?.error,status_error:w.status?.error}))});
 } else if(entry.name.match(/^server\d+\.jsonl$/)) {
  const rows=fs.readFileSync(file,'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
  report.servers.push({name:entry.name,source:rows.find(x=>x.event==='listen'),
   connections:rows.filter(x=>x.event==='request').map(begin=>{
    const a=rows.filter(x=>x.event==='tcp'&&x.id===begin.id),last=a.at(-1);
    return {request:begin,closed:rows.find(x=>x.event==='closed'&&x.id===begin.id),samples:a.length,
     min_window:a.length?Math.min(...a.map(x=>x.snd_wnd)):null,
     zero_window_samples:a.filter(x=>x.snd_wnd===0).length,last_tcp:last};
   })});
 }
}
fs.writeFileSync(path.join(directory,'comparison.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.cases,null,2));
