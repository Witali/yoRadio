const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {analyze}=require('../tools/esp8266_opus_profile/run_quiet_window.cjs');
test('quiet qualification never accepts stale, empty, gapped or stretched audio',()=>{
 const good={valid:true,generation:1,start_ms:1000,end_ms:26000,frames:1200000,underruns:0,age_ms:5000,sample_rate:48000};
 assert.equal(analyze(good).pass,true);
 for(const bad of [{valid:false},{age_ms:20001},{underruns:1},{frames:0},{frames:1000000},
   {end_ms:61000},{sample_rate:0},{generation:-1},{frames:NaN}])assert.equal(analyze({...good,...bad}).pass,false,JSON.stringify(bad));
 assert.equal(analyze({...good,start_ms:0xffffffff-999,end_ms:24000}).pass,true);
 const audio=fs.readFileSync('esp8266/rtos-sdk-native/main/audio_service.c','utf8');
 assert.match(audio,/sizeof\(s_quiet_window\) == 48/);
 assert.match(audio,/s_quiet_window.valid && r.generation == s_generation/);
 const max=JSON.stringify({...good,generation:0xffffffff,start_ms:0xffffffff,end_ms:0xffffffff,frames:0xffffffff,underruns:0xffffffff,age_ms:0xffffffff});
 assert.ok(Buffer.byteLength(max)<300);
});
