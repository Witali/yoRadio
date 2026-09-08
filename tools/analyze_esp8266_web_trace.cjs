// Keep every raw measurement. Filter only separately reported, explicitly
// instrumented socket-backpressure samples, never merely the slow tail.
const fs=require('node:fs');
function decodeTrace(value){
  const fields=['id','path','start_us','total_us','parse_us','read_us','recv_us','send_us','max_send_us','tx_wait_us','tx_sleep_budget_us','mem_wait_us','other_wait_us','mem_errors','retries','bytes','calls','result'];
  if(!Array.isArray(value))return value;
  if(value.length!==fields.length)throw new Error('Unknown WEBTRACE record format');
  return Object.fromEntries(fields.map((key,i)=>[key,value[i]]));
}
function stats(values){
  const a=values.filter(Number.isFinite).sort((x,y)=>x-y);
  return {count:a.length,min:a[0]??null,median:a.length?a[Math.floor(a.length/2)]:null,
    p95:a.length?a[Math.ceil(a.length*.95)-1]:null,max:a.at(-1)??null};
}
function analyze(report,serial){
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
    const exclude=!load.error && !(load.errors||[]).length && resources.every(r=>r.trace) &&
      resources.some(r=>r.classification==='confirmed-tx-backpressure') &&
      !resources.some(r=>r.classification!=='confirmed-tx-backpressure' &&
        (r.totalMs>500 || r.serverWallMs>500 || r.trace.result!==0 || r.trace.mem_errors>0));
    return {kind:load.kind,round:load.round,readyMs:load.readyMs,rawPass:load.pass,
      excludedFromProcessingSample:exclude,
      exclusionReason:exclude?'Successful response dominated by explicitly measured EAGAIN wait; not proof of RF cause':null,
      resources};
  });
  const admitted=samples.filter(s=>!s.excludedFromProcessingSample);
  return {traceRecords:[...records.values()].reduce((n,v)=>n+v.length,0),samples,
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
  const result=analyze(JSON.parse(fs.readFileSync(opt('--report'),'utf8').replace(/^\uFEFF/,'')),fs.readFileSync(opt('--serial'),'utf8'));
  fs.writeFileSync(opt('--output'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({raw:result.raw,processingSample:result.processingSample,excluded:result.excluded,rawFailures:result.rawFailures,processingFailures:result.processingFailures}));
}
