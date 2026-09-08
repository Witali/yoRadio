#!/usr/bin/env node
const fs=require('node:fs');
const {readLog}=require('./summarize_mp3_matrix.cjs');
const {summarize}=require('./summarize_network.cjs');
function stats(values) {
  const a=values.filter(Number.isFinite).sort((x,y)=>x-y);
  const q=p=>{const i=(a.length-1)*p,l=Math.floor(i);return a[l]+(a[Math.ceil(i)]-a[l])*(i-l)};
  return a.length ? {n:a.length,min:a[0],median:q(.5),p95:q(.95),max:a.at(-1)} : {n:0};
}
function analyze(log,minimum=10) {
  const raw=summarize(log), groups=new Map(),cpu=new Map(raw.cpu.map(c=>[c.case,c]));
  const samples=raw.cases.filter(c=>c.variant!==undefined).map(c=>{
    const run=cpu.get(c.case),reader=run?.tasks.find(t=>t.name==='audio');
    const validCpu=run?.valid===1 && Math.abs(run.accounted_percent-100)<.5;
    return {...c,finished:c.error!==undefined||c.open!==undefined||c.allocation_failed===true,
      audio_task_percent:validCpu?reader?.percent:null,
      reader_percent:validCpu&&!c.output?reader?.percent:null,
      reader_us_per_kib:validCpu&&!c.output&&reader&&c.bytes>0?reader.runtime_us*1024/c.bytes:null,
      useful_bytes_per_read:c.calls>c.empty?c.bytes/(c.calls-c.empty):null,
      pcm_wall_ratio:c.output&&c.wall_us>0?c.pcm_seconds*1000000/c.wall_us:null,
      non_idle_percent:validCpu?run.non_idle_percent:null,
      network_percent:validCpu?run.tasks.filter(t=>['tiT','ppT'].includes(t.name)).reduce((s,t)=>s+t.percent,0):null,
      rssi_samples:stats((c.rssi_seconds||[]).filter(v=>v>-127))};
  });
  for(const c of samples) {
    const key=c.fixture+':'+c.variant;
    if(!groups.has(key))groups.set(key,{fixture:c.fixture,variant:c.variant,path:c.path,
      output:Boolean(c.output),wait_ms:c.wait_ms,read_limit:c.read_limit,batch:c.batch,samples:[]});
    groups.get(key).samples.push(c);
  }
  const summaries=[...groups.values()].map(g=>{
    const done=g.samples.filter(c=>c.finished),ok=done.filter(c=>c.completed);
    const errors={};for(const c of done.filter(c=>!c.completed)) {
      const e=c.error===0?'incomplete_window':c.error??(c.allocation_failed?'allocation':'open:'+c.open);errors[e]=(errors[e]||0)+1;
    }
    const rows=ok.filter(c=>Number.isFinite(c.reader_percent));
    const audioRows=ok.filter(c=>Number.isFinite(c.audio_task_percent));
    const {samples:unused,...identity}=g;
    return {...identity,attempts:done.length,complete_windows:ok.length,
      kept_up_windows:ok.filter(c=>c.kept_up).length,failed:done.length-ok.length,
      errors,reader_percent_complete:stats(rows.map(c=>c.reader_percent)),
      reader_percent_all:stats(done.map(c=>c.reader_percent)),
      audio_task_percent_complete:stats(audioRows.map(c=>c.audio_task_percent)),
      network_percent_complete:stats(audioRows.map(c=>c.network_percent)),
      non_idle_percent_complete:stats(audioRows.map(c=>c.non_idle_percent)),
      pcm_wall_ratio_complete:stats(ok.map(c=>c.pcm_wall_ratio)),
      underruns_complete:stats(ok.filter(c=>c.output).map(c=>c.underrun)),
      reader_us_per_kib_complete:stats(rows.map(c=>c.reader_us_per_kib)),
      useful_bytes_per_read_complete:stats(ok.map(c=>c.useful_bytes_per_read)),
      audio_stack_min:stats(done.map(c=>c.stack)),
      rx_kbps_complete:stats(ok.map(c=>c.rx_kbps)),
      rx_kbps_all:stats(done.map(c=>c.rx_kbps)),
      sampled_heap_min:stats(done.map(c=>c.sampled_heap_min)),
      empty_calls_complete:stats(ok.map(c=>c.empty)),
      rssi_complete:stats(ok.flatMap(c=>(c.rssi_seconds||[]).filter(v=>v>-127)))};
  });
  const paired=[];
  for(const a of samples.filter(c=>c.variant===0&&c.completed&&Number.isFinite(c.audio_task_percent))) {
    for(const b of samples.filter(c=>c.fixture===a.fixture&&c.round===a.round&&c.recovery_epoch===a.recovery_epoch&&c.variant!==0&&c.completed&&Number.isFinite(c.audio_task_percent)))
      paired.push({fixture:a.fixture,round:a.round,variant:b.variant,
        audio_delta_pp:b.audio_task_percent-a.audio_task_percent,
        reader_delta_pp:Number.isFinite(a.reader_percent)&&Number.isFinite(b.reader_percent)?b.reader_percent-a.reader_percent:null,
        non_idle_delta_pp:b.non_idle_percent-a.non_idle_percent,
        rx_delta_kbps:b.rx_kbps-a.rx_kbps});
  }
  return {complete:raw.complete&&samples.length===raw.cases.length&&samples.every(c=>c.finished)&&summaries.every(g=>g.attempts>=minimum),
    declared_cases:raw.cases.length,finished:samples.filter(c=>c.finished).length,
    minimum_attempts:minimum,starts:raw.starts,groups:summaries,paired,samples,raw};
}
module.exports={analyze,stats};
if(require.main===module) {
  const [file,save]=process.argv.slice(2);if(!file)throw Error('Usage: summarize_network_sweep.cjs capture.log [report.json]');
  const log=readLog(file),report=analyze(log);
  if(save){fs.writeFileSync(save,JSON.stringify(report,null,2)+'\n');
    fs.writeFileSync(save.replace(/\.json$/,'')+'.log',log.split(/\r?\n/).filter(l=>l.includes('net_bench:')||l.includes('net_cpu:')).join('\n')+'\n');}
  console.log(`Finished ${report.finished}/${report.declared_cases}; complete=${report.complete}`);
  console.table(report.groups.map(g=>({fixture:g.fixture,variant:g.variant,wait:g.wait_ms,read:g.read_limit,batch:g.batch,
    attempts:g.attempts,ok:g.complete_windows,failed:g.failed,
    audioTask:g.audio_task_percent_complete.median?.toFixed(2),busy:g.non_idle_percent_complete.median?.toFixed(2),
    kbps:g.rx_kbps_complete.median?.toFixed(1),minHeap:g.sampled_heap_min.min})));
  if(!report.complete)process.exitCode=1;
}
