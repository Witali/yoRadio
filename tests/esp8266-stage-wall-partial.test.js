const test=require('node:test'),assert=require('node:assert/strict');
const {collectSample,summarize}=require('../tools/esp8266_opus_profile/run_stage_wall.cjs');
test('profile timeout preserves health and original observation time without qualifying',async()=>{
 let clock=1000;
 const health={generation:1,uptime_ms:1000,pcm_frames:48000,sample_rate:48000};
 const row=await collectSample(async route=>{
  if(route.endsWith('/audio')) {clock=1010;return health;}
  clock=6010;throw Error('request timeout /api/native/audio?stages=1');
 },1000,()=>clock);
 assert.equal(row.health,health);assert.equal(row.host_ms,10);
 assert.equal(row.request_ms,5010);assert.match(row.error,/stages=1/);
 assert.equal(summarize([row,row]).continuity.pass,false);
 assert.match(summarize([row,row]).profile_error,/missing/);
});
test('failed health remains an explicit failure without an invented snapshot',async()=>{
 const row=await collectSample(async()=>{throw Error('request timeout /api/native/audio')},0,()=>5);
 assert.equal(row.health,undefined);assert.match(row.error,/audio/);
 assert.equal(row.host_ms,5);
});
