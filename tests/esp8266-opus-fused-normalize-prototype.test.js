const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {execute,hostPath}=require('../tools/esp8266_opus_profile/build_host.cjs');
test('host-only fusion preserves actual vq.c normalization, raw collapse mask and guards',()=>{
 const source=path.join(root,'tests/native/esp8266_opus_fused_normalize_test.c');
 const dir=path.join(root,'.build/opus-fused-normalize-prototype'),bin=path.join(dir,'probe');
 fs.mkdirSync(dir,{recursive:true});
 execute('gcc',['-O2','-std=c99','-fwrapv','-ffunction-sections','-fdata-sections',
  '-fsanitize=address,undefined','-fno-sanitize-recover=all',
  ...['upstream/celt','upstream/include','upstream/silk'].map(d=>'-I'+hostPath(path.join(component,d))),
  hostPath(source),hostPath(path.join(component,'upstream/celt/mathops.c')),
  '-Wl,--gc-sections','-lm','-o',hostPath(bin)]);
 const result=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(bin)]));
 assert.equal(result.passed,true);assert.ok(result.cases>5000);
 assert.ok(result.fallback_cases>0);assert.ok(result.zero_pcm_nonzero_mask>0);
 fs.writeFileSync(path.join(dir,'result.json'),JSON.stringify({...result,
  scope:'Local fixed-point arithmetic prototype; not an ASM backend or CPU benchmark',
  source_sha256_lf:sourceHash(source),
  vq_sha256_lf:sourceHash(path.join(component,'upstream/celt/vq.c')),
  mathops_sha256_lf:sourceHash(path.join(component,'upstream/celt/mathops.c'))},null,2)+'\n');
});
