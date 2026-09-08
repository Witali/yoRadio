const test=require('node:test');
const assert=require('node:assert/strict');
const {analyzeTcp}=require('../tools/esp8266_audio_profile/summarize_tcp_source.cjs');
const sample=(ms,window,retrans=0,rto=0)=>({event:'tcp',id:1,ms,snd_wnd:window,
  rtt_us:1000,bytes_retrans:retrans,rto_episodes:rto,fast_retrans:0,dup_acks:0});
const log=rows=>rows.map(JSON.stringify).join('\n');
test('TCP summary joins case/variant, retaining loss and zero-window observations',()=>{
  const report=analyzeTcp(log([{event:'listen'},{event:'begin',id:1,case:4,variant:1,sample_ms:100},
    sample(0,2048,100),sample(100,0,200,1),sample(200,0,300,2),sample(600,0,300,2),
    sample(700,500,400,3),{event:'end',id:1,error:10054,accepted_body:100000}]),
    {samples:[{case:4,variant:1,completed:false,error:116,rx_kbps:40}]});
  const c=report.connections[0];assert.equal(report.valid,true);
  assert.equal(c.zero_window_samples,3);assert.equal(c.longest_zero_window_sample_span_ms,100);
  assert.equal(c.retransmitted_bytes_sample_delta,300);assert.equal(c.rto_episodes_sample_delta,3);
  assert.equal(c.board_match.completed,false);assert.equal(c.end_error,10054);
});
test('missing telemetry is not reported as a zero retransmit count',()=>{
  const c=analyzeTcp(log([{event:'listen'},{event:'begin',id:2,case:0,variant:0}])).connections[0];
  assert.equal(c.retransmitted_bytes_sample_delta,null);assert.equal(c.rto_episodes_sample_delta,null);
  assert.equal(c.closed,false);assert.equal(c.board_match,null);
});
test('multiple server starts and malformed lines invalidate a combined capture',()=>{
  assert.equal(analyzeTcp(log([{event:'listen'},{event:'listen'}])).valid,false);
  assert.equal(analyzeTcp(log([{event:'listen'}])+'\nnot-json').valid,false);
});
test('ambiguous or wrong-variant board matches are not silently joined',()=>{
  const source=log([{event:'listen'},{event:'begin',id:1,case:4,variant:1}]);
  assert.equal(analyzeTcp(source,{samples:[{case:4,variant:0}]}).connections[0].board_match,null);
  assert.equal(analyzeTcp(source,{samples:[{case:4,variant:1},{case:4,variant:1}]}).connections[0].board_match,null);
});
