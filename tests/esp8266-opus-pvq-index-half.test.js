const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_index_half.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_index_half_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),frozen=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
function at(fn,pc,from,to){const out={...fn,disassembly:fn.disassembly.split('\n').map(l=>l.trimStart().startsWith(pc.toString(16)+':')?l.replace(from,to):l).join('\n')};assert.notEqual(out.disassembly,fn.disassembly);return out;}
test('halfword phases preserve signed PCM index, original a0, SAR and stack with five fewer executed instructions',()=>{
 const p=f.verifyPair().proof,s=p.semantic.search;
 assert.equal(p.patches.length,3);assert.equal(p.patches[0].address,sem.helper);assert.equal(p.patches[0].bytes,29);
 assert.equal(s.helper.live_bytes,25);assert.equal(s.helper.instructions,9);assert.equal(s.helper.executed_per_phase,5);assert.equal(s.helper.records.length,2);
 assert.equal(s.numeric.signed_cases,131072);assert.equal(s.numeric.table_cases,6720);assert.equal(s.numeric.word_loads,137792);
 assert.equal(s.numeric.new_steps-s.numeric.old_steps,-5*137792);assert.equal(s.return_slot,108);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.table.index_bytes,210);assert.equal(p.table.index_word_bytes,212);assert.equal(p.table.index_padding_hex,'0000');
});
test('halfword proof rejects wrong phase, alignment, unsigned extraction and original return slot',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 for(const [pc,from,to]of[[sem.helper,/a2, 1,/,'a2, 0,'],[sem.helper+3,/a2, a2, -2/,'a2, a2, -1'],[sem.helper+8,/srai/,'srli'],[sem.helper+11,/4024db25/,'4024db39'],[sem.late,/a0, a1, 108/,'a0, a1, 104']])assert.throws(()=>sem.prove(old,at(now,pc,from,to)));
 assert.throws(()=>sem.prove(old,at(now,0x4024db39,/a2, a11, a2/,'a2, a10, a2')),/Outside/);
});
test('halfword table bounds, parent storage and unmodified C fallback are authenticated',()=>{
 const p=proof(),now=p.actual_functions.quant_partition,elf=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
 const storage=Buffer.from(elf);storage[frozen.offsetAt(storage,sem.helper,sem.helperBytes)]^=1;assert.throws(()=>sem.storageBytesProof(storage),/storage changed/);
 const padding=Buffer.from(elf),address=sem.indexBase+sem.indexBytes;
 const sections=require('../tools/esp8266_opus_asm/frozen_div.cjs').sections(padding),ss=sections.filter(s=>s.type===1&&(s.flags&2)&&address>=s.address&&address+2<=s.address+s.bytes);assert.equal(ss.length,1);
 padding[ss[0].offset+address-ss[0].address]=1;assert.throws(()=>f.tableProof(padding),/padding/);
 for(const off of[1,212]){const r=Array(16).fill(0);r[1]=0x3fffef00;r[12]=0x3ffe1000;r[2]=sem.indexBase+off;assert.throws(()=>sem.execute(now,r,new Map([[r[1]+116,0],[r[12]+28,0]]),Buffer.alloc(212),0));}
 assert.equal(p.semantic.search.helper.sar,'untouched');
});
test('halfword model preserves24 exact PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-index-half');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_index_half.cjs')));
});
