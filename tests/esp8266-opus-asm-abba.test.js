const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {plan,checkArtifacts}=require('../tools/esp8266_opus_asm/run_abba.cjs');
const fs=require('node:fs'),os=require('node:os'),crypto=require('node:crypto');
test('ABBA preserves ten trials per variant and alternates first-run bias',()=>{
 const p=plan();assert.equal(p.length,20);assert.equal(p.filter(v=>v==='A').length,10);
 for(let i=0;i<p.length;i+=4)assert.deepEqual(p.slice(i,i+4),['A','B','B','A']);
 assert.throws(()=>plan(4));assert.throws(()=>plan(5.5));
});

test('IRAM experiment permits placement only and rejects mismatched RAM or corpus',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'opus-iram-abba-'));
 const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
 try {
  const fixtures=path.join(dir,'fixtures');fs.mkdirSync(fixtures);
  const corpus=Buffer.from('{}');fs.writeFileSync(path.join(fixtures,'manifest.json'),corpus);
  const a=path.join(dir,'A'),b=path.join(dir,'B');fs.mkdirSync(a);fs.mkdirSync(b);
  const app=Buffer.from([0xe9,1,2,3]);
  const ma={app_sha256:digest(app),bytes:app.length,opus_benchmark:true,opus_benchmark_output:false,
   opus_benchmark_manifest_sha256:digest(corpus),opus_backend:'gcc-asm',opus_asm_optimization_sha256:null,
   opus_pvq_iram:false,opus_pvq_iram_fragment_sha256:'a'.repeat(64),opus_scratch_bytes:6144,cpu_mhz:160};
  const mb={...ma,opus_pvq_iram:true};
  const write=m=>fs.writeFileSync(path.join(b,'manifest.json'),JSON.stringify(m));
  for(const p of [a,b])fs.writeFileSync(path.join(p,'app.bin'),app);
  fs.writeFileSync(path.join(a,'manifest.json'),JSON.stringify(ma));write(mb);
  assert.equal(checkArtifacts(a,b,fixtures,'pvq-iram').B.opus_pvq_iram,true);
  assert.throws(()=>checkArtifacts(a,b,fixtures,'backend'));
  assert.throws(()=>checkArtifacts(b,a,fixtures,'pvq-iram'));
  for(const patch of [{opus_scratch_bytes:4096},{cpu_mhz:240},{opus_pvq_iram:false},
   {opus_backend:'hoisted-asm'},{opus_benchmark_manifest_sha256:'b'.repeat(64)},
   {opus_pvq_iram_fragment_sha256:'c'.repeat(64)}]){
   write({...mb,...patch});assert.throws(()=>checkArtifacts(a,b,fixtures,'pvq-iram'));
  }
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('matching physical A/B artifacts and raw fixtures are verified before OTA',()=>{
 const p=path.resolve(__dirname,'../firmware/development');
 const a=path.join(p,'esp8266-opus-gcc-asm-v1'),b=path.join(p,'esp8266-opus-optimized-asm-v1'),f=path.join(p,'esp8266-opus-asm-library/fixtures');
 assert.equal(checkArtifacts(a,b,f).A.cpu_mhz,160);
 assert.throws(()=>checkArtifacts(b,a,f));assert.throws(()=>checkArtifacts(a,a,f));
});
