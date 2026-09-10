const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {sha256}=require('../tools/esp8266_opus_profile/fixtures.cjs');
const {compareArtifacts}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
test('single reciprocal is opt-in and binds complete PCM/arena evidence',()=>{
  assert.match(fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8'),/option\(YORADIO_OPUS_DIV_ONCE [^\n]+ OFF\)/);
  const r=require('../tools/esp8266_opus_profile/div-once-results.json');assert.equal(r.passed,true);
  for(const [file,hash] of Object.entries(r.source_sha256_lf))assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n'))),hash,file);
  assert.equal(r.full.div_once,true);assert.equal(r.extra.length,11);assert.equal(r.blocks.cases.length,11);
  for(const c of [...r.full.fixtures,r.full.mixed_sequence,...r.extra,...r.blocks.cases,...r.sanitized])assert.equal(c.pcm.exact,true);
});
test('reciprocal board A/B forbids unrelated changes',()=>{
  const a={opus_div_once:false,opus_rotation_lx106:false,opus_celt_decode_only:false};
  compareArtifacts(a,{...a,opus_div_once:true},'opus_div_once');
  assert.throws(()=>compareArtifacts(a,{...a,opus_div_once:true,opus_rotation_lx106:true},'opus_div_once'),/rotation/);
});
test('target reciprocal path follows outlined GCC function and does not add static RAM',()=>{
  const r=require('../tools/esp8266_opus_profile/div-once-target-results.json');
  assert.equal(r.passed,true);assert.equal(r.off_instructions_exact,true);
  assert.equal(r.reciprocal_call_sites.off.alg_unquant,3);
  assert.equal(r.reciprocal_call_sites.on.alg_unquant,0);
  assert.equal(r.reciprocal_call_sites.outlined_rotation.celt_rcp,1);
  for(const k of ['.dram0.data','.dram0.bss','.iram0.bss','.iram0.text'])assert.equal(r.sections.delta[k],0);
});
