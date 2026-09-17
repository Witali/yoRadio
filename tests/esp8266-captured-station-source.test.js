const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {createSource}=require('../tools/esp8266_opus_profile/captured_station_source.cjs');
test('capture source serves exact bytes with normal HTTP framing, not a loop',async()=>{
 const file=path.join(__dirname,'../tools/esp8266_opus_profile/live-fixtures/silk12.opus');
 const server=createSource(file);await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{
  const base='http://127.0.0.1:'+server.address().port;
  const response=await fetch(base+'/capture.opus');
  assert.equal(response.status,200);assert.equal(response.headers.get('connection'),'close');
  const actual=Buffer.from(await response.arrayBuffer()),expected=fs.readFileSync(file);
  assert.equal(Number(response.headers.get('content-length')),expected.length);
  assert.deepEqual(actual,expected);
  assert.equal((await fetch(base+'/secret.csv')).status,404);
  assert.equal((await fetch(base+'/capture.opus',{method:'POST'})).status,404);
 }finally{server.closeAllConnections();await new Promise(r=>server.close(r));}
});
