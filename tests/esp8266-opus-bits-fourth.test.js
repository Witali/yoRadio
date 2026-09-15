const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/bits_fourth.cjs'),sem=require('../tools/esp8266_opus_asm/bits_fourth_proof.cjs');
const prior=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
const proof=()=>read('preflight.json');
function mutate(fn,from,to){assert.ok(fn.disassembly.includes(from));return {...fn,disassembly:fn.disassembly.replace(from,to)};}
test('fourth-step linked shortcut preserves accepted parent, outside bytes, ABI, RAM and all standard budgets',()=>{
 const pair=f.verifyPair(),p=pair.proof,s=p.semantic.search;
 assert.equal(p.patches.length,1);assert.equal(p.patches[0].address,0x4024e1f5);assert.equal(p.patches[0].bytes,40);
 assert.equal(s.numeric.cases,378304);assert.equal(s.numeric.fourth_shortcuts,295452);assert.equal(s.numeric.retained_fifth,82852);
 assert.deepEqual(s.numeric.step_differences,{8:290499,10:4953,'-2':82852});
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(pair.manifests.control.post_link_bits_fifth_variant,'candidate');
});
test('fourth-step proof rejects external entry into replaced interior and live scratch-register use',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const bad=mutate(old,'4024e1ba <quant_partition+0x6be>','4024e1fb <quant_partition+0x6ff>');
 assert.throws(()=>sem.findPatches(bad),/Interior external entry/);
 const badLive={...now,disassembly:now.disassembly.replace(/(4024e241:[^\n]*?)l32i\.n\s+a6, a12, 32/,'$1mov.n a6, a10')};
 assert.notEqual(badLive.disassembly,now.disassembly);
 assert.throws(()=>prior.deadUntilDefinition(badLive,0x4024e241,10),/Live a10/);
});
test('fourth-step proof rejects changed predicate and interpreter detects reversed subtraction or out-of-row access',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const bad={...now,disassembly:now.disassembly.replace(/bgei\s+a10, -1,/,'bgei a10, 0,')};
 assert.notEqual(bad.disassembly,now.disassembly);assert.throws(()=>sem.prove(old,bad));
 const reversed={...now,disassembly:now.disassembly.replace(/sub\s+a10, a4, a6/,'sub a10, a6, a4')};
 assert.notEqual(reversed.disassembly,now.disassembly);assert.throws(()=>sem.numeric(old,reversed));
 const badRead={...now,disassembly:now.disassembly.replace(/(4024e1ad:[^\n]*?)l8ui\s+a4, a4, 0/,'$1l8ui a4, a4, 255')};
 assert.notEqual(badRead.disassembly,now.disassembly);assert.throws(()=>sem.numeric(old,badRead),/Out-of-row read/);
});
test('fourth-step host shortcut preserves24 PCM/state cases through510kbps and compound packets',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'bits-fourth');
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));
 assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,require('../tools/esp8266_opus_asm/export.cjs').sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/bits_fourth.cjs')));
});
