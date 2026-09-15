const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_index_word.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_index_word_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),frozen=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
function at(fn,pc,from,to){const out={...fn,disassembly:fn.disassembly.split('\n').map(l=>l.trimStart().startsWith(pc.toString(16)+':')?l.replace(from,to):l).join('\n')};assert.notEqual(out.disassembly,fn.disassembly);return out;}
test('signed index word preserves actual prefix, all signed values, SAR, stack and return without RAM growth',()=>{
 const p=f.verifyPair().proof,s=p.semantic.search;
 assert.equal(p.patches.length,3);assert.equal(p.patches[0].address,sem.helper);assert.equal(p.patches[0].bytes,29);assert.equal(p.patches[0].after_hex.length,58);
 assert.equal(s.helper.live_bytes,29);assert.equal(s.helper.instructions,10);assert.equal(s.helper.records.length,2);assert.equal(s.storage.instructions,11);
 assert.equal(s.numeric.signed_cases,131072);assert.equal(s.numeric.table_cases,6720);assert.equal(s.numeric.word_loads,137792);assert.equal(s.numeric.new_steps-s.numeric.old_steps,10*137792);
 assert.equal(s.scheduling.return_slot,108);assert.equal(s.scheduling.intervening.length,7);assert.equal(s.scheduling.a0_liveness.ends.length,1);assert.equal(Object.keys(s.interrupt_context.sha256_lf).length,4);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);assert.equal(p.table.index_bytes,210);assert.equal(p.table.index_word_bytes,212);assert.equal(p.table.index_padding_hex,'0000');
});
test('index proof rejects changed return slot, intervening pointer use and bypassed early store',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 assert.throws(()=>sem.prove(old,at(now,sem.site,/a0, a1, 108/,'a0, a1, 104')));
 const live=at(old,0x4024db25,/a15, a3/,'a15, a2');assert.throws(()=>sem.prove(live,at(now,0x4024db25,/a15, a3/,'a15, a2')));
 const bypass={...old,disassembly:old.disassembly+'\n4024dc93: 000000 j 4024db25 <quant_partition+0x29>\n'};
 assert.throws(()=>sem.findPatches(bypass),/Entry bypasses/);
 const wrong=at(now,0x4024db39,/a2, a11, a2/,'a2, a10, a2');assert.throws(()=>sem.prove(old,wrong),/Outside/);
});
test('index proof rejects unsigned extraction, wrong SAR, return destination and unverified flash bytes',()=>{
 const p=proof(),now=p.actual_functions.quant_partition;
 const change=(from,to)=>{const out={...now,disassembly:now.disassembly.split('\n').map(l=>{const m=l.match(/^\s*([0-9a-f]+):/);return m&&sem.helperInside(parseInt(m[1],16))?l.replace(from,to):l;}).join('\n')};assert.notEqual(out.disassembly,now.disassembly);return out;};
 for(const[from,to]of[[/srai\s+a2, a2, 16/,'srli a2, a2, 16'],[/ssa8l\s+a2/,'ssa8l a3'],[/wsr\.sar\s+a0/,'wsr.sar a2'],[/4024db39 </,'4024db3b <']])assert.throws(()=>sem.helperSymbolic(change(from,to)));
 const elf=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz'))),padding=Buffer.from(elf),storage=Buffer.from(elf);
 const address=sem.indexBase+sem.indexBytes,sections=require('../tools/esp8266_opus_asm/frozen_div.cjs').sections(padding);
 const matches=sections.filter(s=>s.type===1&&(s.flags&2)&&address>=s.address&&address+2<=s.address+s.bytes);assert.equal(matches.length,1);
 padding[matches[0].offset+address-matches[0].address]=1;assert.throws(()=>f.tableProof(padding),/padding/);
 storage[frozen.offsetAt(storage,sem.helper,sem.helperBytes)]^=1;assert.throws(()=>sem.storageBytesProof(storage),/storage changed/);
 const r=Array(16).fill(0);r[1]=0x3fffef00;r[12]=0x3ffe1000;r[2]=sem.indexBase+212;
 assert.throws(()=>sem.execute(now,r,new Map([[r[1]+116,0],[r[12]+28,0]]),Buffer.alloc(212),0),/Unknown RAM read/);
});
test('index host model preserves24 exact PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-index-word');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_index_word.cjs')));
});
