const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {sha256}=require('../tools/esp8266_opus_profile/fixtures.cjs');
const {compareArtifacts}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
test('decoder-only CELT is opt-in and guarded before any allocation',()=>{
  assert.match(fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8'),/option\(YORADIO_OPUS_CELT_DECODE_ONLY [^\n]+ OFF\)/);
  const code=fs.readFileSync(path.join(component,'upstream/celt/bands.c'),'utf8');
  assert.equal((code.match(/encode = band_encode\(ctx\);/g)||[]).length,5);
  const body=code.slice(code.indexOf('void quant_all_bands('));
  assert.ok(body.indexOf('ec->error = 1;')<body.indexOf('m->eBands'));
  assert.ok(body.indexOf('ec->error = 1;')<body.indexOf('SAVE_STACK'));
});
test('saved CELT regression binds current source and exact PCM, including transitions',()=>{
  const r=JSON.parse(fs.readFileSync(path.join(root,'tools/esp8266_opus_profile/celt-decode-results.json'),'utf8'));
  assert.equal(r.source_sha256_lf,sha256(Buffer.from(fs.readFileSync(path.join(component,'upstream/celt/bands.c'),'utf8').replace(/\r\n/g,'\n'))));
  assert.equal(r.passed,true);assert.equal(r.encoder_guard_asan_ubsan,true);
  assert.equal(r.sanitized_pcm.length,5);
  for(const c of r.sanitized_pcm)assert.equal(c.pcm.exact,true);
  assert.equal(r.phase.length,10);assert.equal(r.blocks.cases.length,11);
  for(const c of [...r.full.fixtures,r.full.mixed_sequence,...r.phase,...r.blocks.cases])assert.equal(c.pcm.exact,true);
});
test('CELT A/B rejects any unmatched build setting',()=>{
  const a={opus_celt_decode_only:false,opus_fir_flash_word:true,cpu:160};
  compareArtifacts(a,{...a,opus_celt_decode_only:true},'opus_celt_decode_only');
  assert.throws(()=>compareArtifacts(a,{...a,opus_celt_decode_only:true,cpu:80},'opus_celt_decode_only'),/cpu/);
});
