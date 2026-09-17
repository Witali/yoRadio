const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/allocation_byte.cjs'),s=require('../tools/esp8266_opus_asm/allocation_byte_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),{parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
test('linked allocation byte load has exact uint8 output, bounded flash and zero RAM/stack growth',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.numeric_cases,80320);assert.equal(p.semantic.frame_bytes,192);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.patches.length,2);assert.equal(p.patches.reduce((n,x)=>n+x.bytes,0),39);assert.deepEqual(p.semantic.symbolic.map(x=>x.loads),[1,1,1,1]);
 assert.deepEqual(p.semantic.sar_liveness.stops,[0x402484c0]);assert.equal(p.table.logical_bytes,231);assert.equal(p.table.backing_bytes,232);assert.equal(p.table.next_object,p.table.address+232);
});
test('byte proof rejects wrong shift, premature SAR use, altered table and occupied helper storage',()=>{
 const p=read('preflight.json');assert.throws(()=>s.symbolic(p.helperDisassembly[0].replace('extui\ta4, a4, 0, 8','extui\ta4, a4, 0, 7')));
 const leaf=s.sharedLeaf().helperDisassembly,badLeaf=leaf.replace('srai\ta2, a2, 16','sra\ta2, a2');assert.notEqual(leaf,badLeaf);assert.throws(()=>s.sarLiveness(p.functions.clt_compute_allocation,badLeaf),/Live SAR/);
 const fn=p.functions.clt_compute_allocation,bad={...fn,disassembly:fn.disassembly.replace('ssl\ta14','sll\ta14, a14')};assert.notEqual(bad.disassembly,fn.disassembly);assert.throws(()=>s.sarLiveness(bad),/Live SAR/);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz'))),readAt=require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs').readAt;
 readAt(a,s.helper,1)[0]^=1;assert.throws(()=>s.storageBytesProof(a),/Storage already changed/);readAt(a,s.helper,1)[0]^=1;
 readAt(a,s.table+230,1)[0]^=1;assert.throws(()=>s.tableProof(a));
});
test('last byte is independent of all256 possible padding values and invalid pointers are rejected',()=>{
 const p=read('preflight.json'),rows=[...parsed(p.actual_functions.clt_compute_allocation),...parsed({disassembly:p.helperDisassembly[0]})],data=Buffer.alloc(232);
 for(const pointer of[s.table-1,s.table+231,s.table+232]){const r=Array(16).fill(0);r[5]=pointer;assert.throws(()=>s.execute(rows,r,data,0),/Invalid allocation pointer/);}
 for(let padding=0;padding<256;padding++){const r=Array(16).fill(0);r[5]=s.table+230;data[230]=0xa5;data[231]=padding;const out=s.execute(rows,r,data,63);assert.equal(out.registers[4],0xa5);assert.equal(out.words,1);assert.equal(out.sar,16);assert.equal(out.steps,8);}
});
test('host byte model preserves24 PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'allocation-byte');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/allocation_byte.cjs')));
});
