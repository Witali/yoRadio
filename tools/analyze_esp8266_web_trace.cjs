// Keep every raw measurement. Filter only separately reported, explicitly
// instrumented socket-backpressure samples, never merely the slow tail.
const fs=require('node:fs');
function decodeTrace(value){
  const fields=['id','path','start_us','total_us','parse_us','read_us','recv_us','send_us','max_send_us','tx_wait_us','tx_sleep_budget_us','mem_wait_us','other_wait_us','mem_errors','retries','bytes','calls','result'];
  if(!Array.isArray(value))return value;
  if([19,22,25].includes(value.length))fields.push('last_errno');
  if(value.length===22||value.length===25)fields.push('select_wait_us','dispatch_us','dispatch_flags');
  if(value.length===25)fields.push('tcp_rx_us','tcp_rx_len','tcp_seq_gap');
  if(value.length!==fields.length)throw new Error('Unknown WEBTRACE record format');
  return Object.fromEntries(fields.map((key,i)=>[key,value[i]]));
}
function stats(values){
  const a=values.filter(Number.isFinite).sort((x,y)=>x-y);
  return {count:a.length,min:a[0]??null,median:a.length?a[Math.floor(a.length/2)]:null,
    p95:a.length?a[Math.ceil(a.length*.95)-1]:null,max:a.at(-1)??null};
}
// Bound host/board clock offset using HTTP request-send and first-response
// timestamps. No clock synchronization, no assumed symmetric network delay.
function startupTiming(load, resources, records) {
  const origin=load.pageTrace?.timeOrigin, sent=load.pageTrace?.indexSentMs;
  if(!Number.isFinite(origin)||!Number.isFinite(sent))return null;
  const roots=resources.filter(r=>r.path==='/'&&r.trace);
  const playlists=resources.filter(r=>r.path==='/data/playlist.csv'&&r.trace);
  if(roots.length!==1||playlists.length!==1)return null;
  const root=roots[0], playlist=playlists[0], boot=root.trace.id.split('-')[0];
  if(playlist.trace.id.split('-')[0]!==boot)return null;
  const relative=t=>((t-root.trace.start_us)>>>0)/1000;
  const end=relative(playlist.trace.start_us);
  if(end>2147483)return null; // Ambiguous wrap or reversed request order.
  const candidates=[...records.values()].flat().filter(t=>t.path==='/ws:getindex'&&
    t.id.split('-')[0]===boot&&relative(t.start_us)<end);
  if(candidates.length!==1)return null; // Concurrent/retried clients are not guessed.
  let low=-Infinity,high=Infinity;
  for(const r of [root,playlist]) {
    if(![r.startTime,r.requestStart,r.ttfbMs,r.trace.start_us].every(Number.isFinite))return null;
    low=Math.max(low,r.startTime+r.requestStart-relative(r.trace.start_us));
    high=Math.min(high,r.startTime+r.ttfbMs-relative(r.trace.start_us));
  }
  if(low>high)return null;
  const t=candidates[0],at=relative(t.start_us),command=origin+sent;
  return {traceId:t.id,clockOffsetUncertaintyMs:high-low,
    commandToSessionStartMs:{min:at+low-command,max:at+high-command},
    // select wait can include idle before the command existed. Never exclude it.
    selectWaitMs:Number.isFinite(t.select_wait_us)?t.select_wait_us/1000:null,
    readyToSessionMs:Number.isFinite(t.dispatch_us)?t.dispatch_us/1000:null,
    dispatchFlags:t.dispatch_flags??null,
    tcpPayloadBytes:t.tcp_rx_len||null,tcpSequenceGap:t.tcp_rx_len?t.tcp_seq_gap:null,
    tcpInputToSessionMs:t.tcp_rx_len?((t.start_us-t.tcp_rx_us)|0)/1000:null,
    sessionToCommandParsedMs:t.parse_us/1000,receiveWallMs:t.recv_us/1000,
    sessionWallMs:t.total_us/1000,sendWallMs:t.send_us/1000,
    note:'Bounds, not a one-way network measurement. Dispatch includes earlier handlers and preemption; select may include normal idle.'};
}
function analyze(report,serial,ping=null){
  const records=new Map();
  for(const line of serial.split(/\r?\n/)) {
    const match=line.match(/WEBTRACE (\{.*\}|\[.*\])/);if(!match)continue;
    const r=decodeTrace(JSON.parse(match[1]));if(!records.has(r.id))records.set(r.id,[]);records.get(r.id).push(r);
  }
  const samples=(report.loads||[]).map(load=>{
    const resources=(load.resources||[]).map(resource=>{
      const matches=records.get(resource.traceId)||[];
      const trace=matches.length===1&&matches[0].path===resource.path?matches[0]:null;
      if(!trace)return {...resource,classification:'unmatched-no-exclusion'};
      // EAGAIN proves that a nonblocking socket could not enqueue data. It
      // does NOT establish RF loss rather than receiver/lwIP backpressure.
      const wait=trace.tx_wait_us/1000,total=trace.total_us/1000;
      const budget=trace.tx_sleep_budget_us/1000;
      const valid=trace.result===0&&trace.mem_errors===0&&trace.mem_wait_us===0&&trace.other_wait_us===0;
      const dominant=valid&&budget>=200&&budget>=total*.5;
      return {...resource,trace,serverWallMs:total,explicitTxWaitMs:wait,
        txSleepBudgetMs:budget,serverWallWithoutTxSleepBudgetMs:total-budget,
        // Not pure CPU: socket calls, file reads and other fields include preemption.
        classification:dominant?'confirmed-tx-backpressure':
          trace.mem_errors||trace.mem_wait_us?'memory-pressure':
          resource.totalMs-total>200?'outside-measured-handler-unresolved':'no-dominant-network-wait'};
    });
    const waitBudget=Math.max(0,...resources.filter(r=>r.classification==='confirmed-tx-backpressure').map(r=>r.txSleepBudgetMs));
    const exclude=!load.error && !(load.errors||[]).length && resources.every(r=>r.trace) &&
      resources.some(r=>r.classification==='confirmed-tx-backpressure') &&
      // A proven socket wait must not hide an additional long browser/dispatch
      // delay. Do not sum waits from possibly concurrent requests.
      load.readyMs-waitBudget<=500 &&
      !resources.some(r=>r.classification!=='confirmed-tx-backpressure' &&
        (r.totalMs>500 || r.serverWallMs>500 || r.trace.result!==0 || r.trace.mem_errors>0));
    const began=Math.min(...resources.map(r=>r.startTime).filter(Number.isFinite));
    const during=(ping?.samples||[]).filter(p=>p.startTime<=began+load.readyMs && p.startTime+p.elapsedMs>=began);
    return {kind:load.kind,round:load.round,readyMs:load.readyMs,rawPass:load.pass,
      pageTrace:load.pageTrace,sockets:load.sockets,
      startup:startupTiming(load,resources,records),
      // Supporting evidence only. ICMP delay alone does not prove the cause
      // of a TCP transfer delay and never triggers automatic exclusion.
      pingDuringLoad:during.length?{samples:during.length,failures:during.filter(p=>p.status!=='Success').length,rttMs:stats(during.map(p=>p.rttMs))}:null,
      excludedFromProcessingSample:exclude,
      exclusionReason:exclude?'Successful response dominated by explicitly measured EAGAIN wait; not proof of RF cause':null,
      resources};
  });
  const admitted=samples.filter(s=>!s.excludedFromProcessingSample);
  const requestTraces=[...records.values()].flat();
  return {traceRecords:requestTraces.length,requestTraces,samples,
    raw:stats(samples.map(s=>s.readyMs)),processingSample:stats(admitted.map(s=>s.readyMs)),
    excluded:samples.filter(s=>s.excludedFromProcessingSample).length,
    rawFailures:samples.filter(s=>s.rawPass===false).length,
    processingFailures:admitted.filter(s=>s.rawPass===false).length,
    note:'Filtered sample is not an end-to-end guarantee. Unknown causes and memory waits remain included. Subtracted handler wall time is not CPU time.'};
}
module.exports={analyze,decodeTrace};
if(require.main===module){
  const args=process.argv.slice(2),opt=k=>args[args.indexOf(k)+1];
  if(!['--report','--serial','--output'].every(k=>args.includes(k)))throw new Error('Use --report <browser.json> --serial <uart.log> --output <analysis.json>');
  const json=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
  const result=analyze(json(opt('--report')),fs.readFileSync(opt('--serial'),'utf8'),args.includes('--ping')?json(opt('--ping')):null);
  fs.writeFileSync(opt('--output'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({raw:result.raw,processingSample:result.processingSample,excluded:result.excluded,rawFailures:result.rawFailures,processingFailures:result.processingFailures}));
}
