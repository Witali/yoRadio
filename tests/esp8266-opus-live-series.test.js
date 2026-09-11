const test=require('node:test'),assert=require('node:assert/strict');
const {attempt}=require('../tools/esp8266_opus_profile/run_live_series.cjs');
test('live series retains start failures and requires real playing Opus plus continuity',async()=>{
  for(const start of ['ok','timeout','reject'])for(const codec of ['OPUS','MP3'])
  for(const gap of [false,true]) {
    let captured=0;
    const r=await attempt('http://example.test/test.opus',{
      request:async route=>{
        if(route.endsWith('opus-stream')) {
          if(start==='timeout')throw Error('timeout');
          return {http:start==='ok'?202:503,body:{queued:start==='ok'}};
        }
        return {http:200,body:{playing:true,codec}};
      },wait:async()=>{},capture:async()=>{captured++;return {result:{continuity:{pass:!gap}}};}
    });
    assert.equal(captured,1);
    assert.equal(r.pass,start==='ok'&&codec==='OPUS'&&!gap);
    if(start==='timeout')assert.equal(r.start_error,'timeout');
  }
});
