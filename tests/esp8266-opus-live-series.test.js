const test=require('node:test'),assert=require('node:assert/strict');
const {attempt}=require('../tools/esp8266_opus_profile/run_live_series.cjs');
test('live series retains start failures and requires real playing Opus plus continuity',async()=>{
  for(const start of ['ok','timeout','reject'])for(const codec of ['OPUS','MP3'])
  for(const gap of [false,true]) {
    let captured=0;
    const r=await attempt('http://example.test/test.opus',{
      request:async (route,body)=>{
        if(route.endsWith('opus-stream')&&!body) {
          assert.equal(captured,1,'heap snapshot only after capture');
          return {http:200,body:{stage:8,largest_dram:1234}};
        }
        if(route.endsWith('opus-stream')) {
          if(start==='timeout')throw Error('timeout');
          return {http:start==='ok'?202:503,body:{queued:start==='ok'}};
        }
        return {http:200,body:{playing:true,codec}};
      },wait:async()=>{},capture:async()=>{captured++;return {result:{continuity:{pass:!gap}}};}
    });
    assert.equal(captured,1);
    assert.equal(r.init_diagnostic.body.largest_dram,1234);
    assert.equal(r.pass,start==='ok'&&codec==='OPUS'&&!gap);
    if(start==='timeout')assert.equal(r.start_error,'timeout');
  }
});
test('missing heap diagnostic is retained without discarding continuity',async()=>{
  const r=await attempt('http://example.test/a.opus',{
    request:async (route,body)=>{
      if(body)return {http:202,body:{queued:true}};
      if(route.endsWith('status'))return {http:200,body:{playing:true,codec:'OPUS'}};
      throw Error('heap diagnostic timeout');
    },wait:async()=>{},capture:async()=>({result:{continuity:{pass:true}}})
  });
  assert.equal(r.pass,true);assert.equal(r.init_diagnostic_error,'heap diagnostic timeout');
});
