const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_binary.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_binary_proof.cjs');
const {sections}=require('../tools/esp8266_opus_asm/frozen_div.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const evidence=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
const original=()=>zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
function changed(fn,from,to){const b=structuredClone(fn);assert.ok(b.disassembly.includes(from));b.disassembly=b.disassembly.replace(from,to);return b;}
test('linked binary search matches every U-row interval without RAM or stack growth',()=>{
 const p=evidence();assert.deepEqual(sem.prove(p.functions.decode_pulses,p.actual_functions.decode_pulses,p.helperDisassembly,p.table),p.semantic);
 assert.ok(p.semantic.cases>100000);assert.equal(p.semantic.stores,0);assert.equal(p.semantic.sar_writes,0);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.semantic.stack_bytes,48);
 assert.equal(p.app_bytes,903216);
});
test('real flash table monotonicity, pointers and final diagonal are checked',()=>{
 const a=original(),p=evidence();assert.deepEqual(sem.table(a),p.table);
 assert.equal(p.table.rows.at(-1).n,14);assert.equal(p.table.rows.at(-1).values.length,1);
 const mutate=(at,value)=>{const b=Buffer.from(a),s=sections(b).find(s=>at>=s.address&&at+4<=s.address+s.bytes&&(s.flags&2));assert.ok(s);b.writeUInt32LE(value,s.offset+at-s.address);return b;};
 assert.throws(()=>sem.table(mutate(p.table.pointers,0)));
 assert.throws(()=>sem.table(mutate(p.table.rows[0].address+16,0)),/Nonmonotone/);
 const b=base.patchElf(a,p.patches);assert.deepEqual(sem.table(b),p.table);
});
test('branch, midpoint, load width and wrong cached value mutations are rejected',()=>{
 const p=evidence();sem.checkHelper(p.helperDisassembly);
 for(const[from,to]of[['bltu','bgeu'],['srli','slli'],['l32i.n','l16ui'],['a11, a8','a11, a9'],['ret.n','retw.n']]){
  assert.ok(p.helperDisassembly.includes(from));assert.throws(()=>sem.checkHelper(p.helperDisassembly.replace(from,to)));
 }
 for(const[from,to]of[['call0','callx0'],['a15, a15, -4','a15, a15, -8'],['a3, a4, a5','a0, a4, a5']])
  assert.throws(()=>sem.auditSite(changed(p.actual_functions.decode_pulses,from,to),true));
});
test('decoder-dead storage contract is revalidated; all other ELF bytes stay exact',()=>{
 const p=evidence(),a=original();assert.deepEqual(sem.storage({functions:p.functions},path.join(f.build('control'),'../',f.parent,'yoradio_esp8266_helix_native.elf'),a),p.storage);
 assert.equal(p.storage.contract.caller.argument,'a2=0');assert.equal(p.storage.storage.bytes,94);
 assert.equal(p.patches.length,2);assert.equal(p.patches[0].address,sem.site);assert.equal(p.patches[1].address,sem.helper);
 base.patchElf(a,p.patches);
});
test('host semantic mirror passes24 exact PCM/state/sanitizer cases without bitrate cap',()=>{
 const r=f.read(path.join(f.art('candidate'),'correctness.json'));assert.equal(r.passed,true);assert.equal(r.kind,'pvq-binary');
 assert.equal(r.recipe_sha256_lf,require('../tools/esp8266_opus_asm/export.cjs').sourceHash(require.resolve('../tools/esp8266_opus_asm/pvq_binary.cjs')));
 assert.equal(r.cases.length,24);assert.ok(r.cases.every(c=>c.pcm.exact));
 for(const n of['stereo-510','stereo-320-2.5ms','320-48frames','192-120ms','mixed'])assert.ok(r.cases.some(c=>c.name===n));
});
