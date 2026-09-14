const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
const small=require('../tools/esp8266_opus_asm/small_div.cjs'),tail=require('../tools/esp8266_opus_asm/small_div_tail.cjs');
test('tail placement preserves every instruction and data word of small-div',()=>{
 const input=fs.readFileSync(path.join(component,'asm/lx106/gcc/upstream/celt/entdec.c.s'),'utf8');
 const output=tail.transform(input);assert.equal((output.match(/\.section \.irom1\.text/g)||[]).length,2);
 const restored=output.replace(
  '\t.section .irom1.text,"ax",@progbits\n\t.balign 4\n.Ly_small_table:\n\t.word yoradio_opus_small_div_table\n.Ly_small_fallback:\n\t.word __udivsi3\n',
  '\t.section .text.yoradio_opus_small_udiv,"ax",@progbits\n\t.literal_position\n\t.literal .Ly_small_table, yoradio_opus_small_div_table\n\t.literal .Ly_small_fallback, __udivsi3\n'
 ).replace('\t.section .irom1.text,"ax",@progbits','\t.section .rodata.yoradio_opus_small_div_table,"a",@progbits');
 assert.equal(restored,small.transform(input));
 assert.equal((output.match(/call0\s+yoradio_opus_small_udiv/g)||[]).length,3);
});
test('tail remains guarded and reproducible without changing C/GCC fallback',()=>{
 const verified=require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-small-div-tail-asm');
 assert.equal(verified.files.length,110);
 assert.ok(verified.files.some(f=>f.replaceAll('\\','/').endsWith('/bands-small-div-tail/upstream/celt/entdec.c.s')));
 assert.throws(()=>tail.transform('not the protected source'));
});

test('raw report rejects changed fixtures, PCM, incomplete runs and profilers',()=>{
 const {root}=require('../tools/esp8266_opus_asm/export.cjs');
 const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
 const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
 const fixtures=read('firmware/development/esp8266-opus-asm-library/fixtures/manifest.json');
 const original=read('firmware/development/esp8266-opus-bands-small-div-v1/runs/run1.json');
 const address=original.before.data.app_address;validateRun(original,fixtures,address);
 for(const change of [
  r=>{r.final.results[4].pcm_hash++;},r=>{r.final.results[4].samples--;},
  r=>{r.final.results[4].packets--;},r=>{r.final.rounds=9;},
  r=>{r.fixtures.fixtures[4].name='different fixture';},r=>{r.final.physical_output=true;},
  r=>{r.final.division_microbenchmark=true;},r=>{r.final.profile_stage=1;},
  r=>{r.final.functions=[];},r=>{r.final.state=2;},r=>{r.interval_ms=1500;},
  r=>{r.after.data.app_address=0;},r=>{r.error='observation incomplete';}
 ]){const r=structuredClone(original);change(r);assert.throws(()=>validateRun(r,fixtures,address));}
});
