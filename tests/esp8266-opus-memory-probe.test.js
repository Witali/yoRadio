const test=require('node:test'),assert=require('node:assert/strict');
const {attempt,routes}=require('../tools/esp8266_opus_profile/run_memory_probe.cjs');
test('uncertain play POST is never resent and all failed memory observations are retained',async()=>{
 const calls=[],saved=[],waits=[];
 const r=await attempt('http://fixture/test.opus',{
  request:async(route,body)=>{calls.push({route,body});if(body!==undefined)throw Error('ambiguous POST');
   if(route===routes.memory)throw Error('read timeout');
   return {http:200,body:route===routes.audio?{uptime_ms:123}:{stage:8}};},
  now:()=>123,wait:async ms=>waits.push(ms),save:v=>saved.push(structuredClone(v))},3);
 assert.equal(calls.filter(c=>c.body!==undefined).length,1);assert.equal(r.samples.length,3);
 assert.equal(r.start_error,'ambiguous POST');assert.ok(r.samples.every(s=>s.memory_error==='read timeout'));
 assert.deepEqual(waits,[2000,2000]);assert.equal(r.observable,true);assert.equal(saved.length,5);
 assert.ok(!Object.hasOwn(r,'pass')); // Never masquerade as continuity qualification.
});
test('unreachable board is marked unobservable rather than silently retried',async()=>{
 let posts=0;
 const r=await attempt('http://fixture/test.opus',{request:async(_r,b)=>{posts+=Number(b!==undefined);throw Error('offline');},
  now:()=>0,wait:async()=>{},save:()=>{}},2);
 assert.equal(posts,1);assert.equal(r.observable,false);assert.equal(r.samples.length,2);
 assert.ok(r.samples.every(s=>s.memory_error&&s.audio_error&&s.init_error));
});
