const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {plan,checkArtifacts}=require('../tools/esp8266_opus_asm/run_abba.cjs');
test('ABBA preserves ten trials per variant and alternates first-run bias',()=>{
 const p=plan();assert.equal(p.length,20);assert.equal(p.filter(v=>v==='A').length,10);
 for(let i=0;i<p.length;i+=4)assert.deepEqual(p.slice(i,i+4),['A','B','B','A']);
 assert.throws(()=>plan(4));assert.throws(()=>plan(5.5));
});
test('matching physical A/B artifacts and raw fixtures are verified before OTA',()=>{
 const p=path.resolve(__dirname,'../firmware/development');
 const a=path.join(p,'esp8266-opus-gcc-asm-v1'),b=path.join(p,'esp8266-opus-optimized-asm-v1'),f=path.join(p,'esp8266-opus-asm-library/fixtures');
 assert.equal(checkArtifacts(a,b,f).A.cpu_mhz,160);
 assert.throws(()=>checkArtifacts(b,a,f));assert.throws(()=>checkArtifacts(a,a,f));
});
