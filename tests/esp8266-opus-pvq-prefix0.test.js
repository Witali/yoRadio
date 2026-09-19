const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_prefix0.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_prefix0_proof.cjs');
const {sections}=require('../tools/esp8266_opus_asm/frozen_div.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const evidence=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
const original=()=>zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
function changed(fn,from,to){const b=structuredClone(fn);assert.ok(b.disassembly.includes(from));b.disassembly=b.disassembly.replace(from,to);return b;}
test('linked packed prefix search matches every U-row interval without RAM or stack growth',()=>{
 const p=evidence();assert.deepEqual(sem.prove(p.functions.decode_pulses,p.actual_functions.decode_pulses,p.helperDisassembly,p.table),p.semantic);
 assert.ok(p.semantic.cases>100000);assert.equal(p.semantic.helper_instructions_covered,26);assert.equal(p.semantic.stores,0);assert.equal(p.semantic.sar_preserved,true);
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
test('branch, extraction, word width and SAR restoration mutations are rejected',()=>{
 const p=evidence();sem.checkHelper(p.helperDisassembly);
 for(const[from,to]of[['bltu','bgeu'],['a3, a13, 5','a3, a13, 4'],['l32i.n','l16ui'],['a8, a8, 0, 8','a8, a8, 0, 7'],['wsr.sar','rsr.sar'],['ret.n','retw.n']]){
  assert.ok(p.helperDisassembly.includes(from));assert.throws(()=>sem.checkHelper(p.helperDisassembly.replace(from,to)));
 }
 for(const[from,to]of[['call0','callx0'],['bgei','blti'],['a15, a15, -4','a15, a15, -8'],['a3, a4, a5','a0, a4, a5']])
  assert.throws(()=>sem.prove(p.functions.decode_pulses,changed(p.actual_functions.decode_pulses,from,to),p.helperDisassembly,p.table));
});
test('decoder-dead storage contract is revalidated; all other ELF bytes stay exact',()=>{
 const p=evidence(),a=original();assert.deepEqual(sem.storage({functions:p.functions},path.join(f.build('control'),'../',f.parent,'yoradio_esp8266_helix_native.elf'),a),p.storage);
 assert.equal(p.storage.contract.caller.argument,'a2=0');assert.equal(p.storage.storage.bytes,94);
 assert.equal(p.patches.length,3);assert.equal(p.patches[0].address,sem.site);assert.equal(p.patches[1].address,sem.storageAddress);
 base.patchElf(a,p.patches);
});
test('host semantic mirror passes24 exact PCM/state/sanitizer cases without bitrate cap',()=>{
 const r=f.read(path.join(f.art('candidate'),'correctness.json'));assert.equal(r.passed,true);assert.equal(r.kind,'pvq-prefix0');
 assert.equal(r.recipe_sha256_lf,require('../tools/esp8266_opus_asm/export.cjs').sourceHash(require.resolve('../tools/esp8266_opus_asm/pvq_prefix0.cjs')));
 assert.equal(r.cases.length,24);assert.ok(r.cases.every(c=>c.pcm.exact));
 for(const n of['stereo-510','stereo-320-2.5ms','320-48frames','192-120ms','mixed'])assert.ok(r.cases.some(c=>c.name===n));
});
test('packed bounds are exact flash bytes; pointer and byte mutations fail closed',()=>{
 const p=evidence(),a=original(),b=base.patchElf(a,p.patches);
 assert.deepEqual(sem.prefixProof(b,p.table),p.prefix_table);assert.equal(p.prefix_table.bytes,352);
 assert.equal(p.semantic.extra_sar_cases,256);
 const modify=(at,value)=>{const copy=Buffer.from(b),off=base.offsetAt(copy,at,1);copy[off]=value;return copy;};
 assert.throws(()=>sem.prefixProof(modify(sem.prefixAddress,0),p.table));
 const bad=Buffer.from(b);bad.writeUInt32LE(sem.prefixAddress,base.offsetAt(bad,sem.dataAddress,4));
 assert.throws(()=>sem.prefixProof(bad,p.table));
});
test('full encoder storage is unreachable and has no address-taken references',()=>{
 const p=evidence(),x=p.storage.encoder_storage;
 assert.equal(x.address,sem.dataAddress);assert.equal(x.bytes,356);assert.equal(x.function_bytes,1788);
 assert.deepEqual(x.calls,[{from:0x402518fa,to:sem.dataAddress}]);
 assert.deepEqual(x.pointers,[]);assert.deepEqual(x.external_jumps,[]);
 assert.deepEqual(x.source_refs,['celt/bands.c','celt/vq.c']);
 const b=original();b.writeUInt32LE(sem.dataAddress,base.offsetAt(b,sem.dataAddress,4));
 assert.throws(()=>sem.storage({functions:p.functions},path.join(f.build('control'),'../',f.parent,'yoradio_esp8266_helix_native.elf'),b),/Address-taken/);
});
