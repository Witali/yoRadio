#!/usr/bin/env node
const fs=require('node:fs');
const {readLog}=require('./summarize_mp3_matrix.cjs');
const {stats}=require('./summarize_network_sweep.cjs');

function analyzeTcp(log,board=null) {
  const connections=new Map();let malformed=0,starts=0;
  for(const line of log.split(/\r?\n/)) {
    if(!line.trim())continue;
    let event;
    try {event=JSON.parse(line.replace(/^\uFEFF/,''));} catch {++malformed;continue;}
    if(event.event==='listen'){++starts;continue;}
    if(!Number.isInteger(event.id))continue;
    if(!connections.has(event.id))connections.set(event.id,{id:event.id,samples:[],errors:[]});
    const c=connections.get(event.id);
    if(event.event==='begin')c.begin=event;
    else if(event.event==='tcp')c.samples.push(event);
    else if(event.event==='end')c.end=event;
    else c.errors.push(event);
  }
  const cases=board?.samples||board?.cases||[];
  const rows=[...connections.values()].map(c=>{
    const samples=c.samples.sort((a,b)=>a.ms-b.ms);
    const first=samples[0],last=samples.at(-1);
    // Counter deltas cover the sampled interval only, excluding both tails.
    const delta=key=>first&&last&&last[key]>=first[key]?last[key]-first[key]:null;
    let zeroStart=null,previous=null,longest=0,zeroCount=0;
    for(const s of samples) {
      if(s.snd_wnd===0) {
        ++zeroCount;
        if(zeroStart===null||s.ms-previous>2*(c.begin?.sample_ms||100))zeroStart=s.ms;
        longest=Math.max(longest,s.ms-zeroStart);
      } else zeroStart=null;
      previous=s.ms;
    }
    const matches=cases.filter(row=>c.begin?.case>=0&&row.case===c.begin.case&&row.variant===c.begin.variant);
    const match=matches.length===1?matches[0]:null;
    return {id:c.id,case:c.begin?.case,variant:c.begin?.variant,path:c.begin?.path,
      rate_kbps:c.begin?.rate_kbps,closed:Boolean(c.end),sample_count:samples.length,
      first_sample_ms:first?.ms??null,last_sample_ms:last?.ms??null,
      zero_window_samples:samples.length?zeroCount:null,longest_zero_window_sample_span_ms:samples.length?longest:null,
      rtt_us:stats(samples.map(s=>s.rtt_us)),send_window:stats(samples.map(s=>s.snd_wnd)),
      retransmitted_bytes_sample_delta:delta('bytes_retrans'),
      rto_episodes_sample_delta:delta('rto_episodes'),
      fast_retrans_sample_delta:delta('fast_retrans'),dup_acks_sample_delta:delta('dup_acks'),
      accepted_body:c.end?.accepted_body??null,max_send_us:c.end?.max_send_us??null,
      accepted_wire_bytes:c.end?.accepted_wire_bytes??null,
      sample_call_ms:stats(samples.map(s=>s.sample_call_ms)),
      end_error:c.end?.error??null,telemetry_errors:c.errors,
      board_match:match?{completed:match.completed,kept_up:match.kept_up,error:match.error,
        rx_kbps:match.rx_kbps,output:match.output,underruns:match.underrun,
        rssi_before:match.rssi_before,rssi:match.rssi}:null};
  });
  return {valid:starts===1&&malformed===0,starts,malformed,connections:rows,
    note:'Socket samples are not packet capture. Send acceptance is not delivery; sampled counter deltas omit interval tails. RTO/retransmission does not identify the losing hop. Zero-window spans are sampled observations, not exact durations.'};
}
module.exports={analyzeTcp};
if(require.main===module) {
  const [file,save,boardFile]=process.argv.slice(2);
  if(!file)throw Error('Usage: summarize_tcp_source.cjs source.log [report.json] [board-sweep.json]');
  const report=analyzeTcp(readLog(file),boardFile?JSON.parse(fs.readFileSync(boardFile,'utf8')):null);
  if(save)fs.writeFileSync(save,JSON.stringify(report,null,2)+'\n');
  console.table(report.connections.map(c=>({case:c.case,variant:c.variant,samples:c.sample_count,
    zero:c.zero_window_samples,zeroSpan:c.longest_zero_window_sample_span_ms,
    retrans:c.retransmitted_bytes_sample_delta,rto:c.rto_episodes_sample_delta,
    rtt:c.rtt_us.median,boardOK:c.board_match?.completed})));
  if(!report.valid)process.exitCode=1;
}
