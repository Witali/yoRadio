const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_exp2_word.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_exp2_word_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),frozen=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
function at(fn,pc,from,to){const out={...fn,disassembly:fn.disassembly.split('\n').map(l=>l.trimStart().startsWith(pc.toString(16)+':')?l.replace(from,to):l).join('\n')};assert.notEqual(out.disassembly,fn.disassembly);return out;}
test('exp2 word helper preserves signed result, every live register, SAR, stack and outside addresses',()=>{
 const p=f.verifyPair().proof,s=p.semantic.search;
 assert.equal(p.patches.length,2);assert.equal(p.patches[0].address,sem.helper);assert.equal(p.patches[0].bytes,25);
 assert.equal(p.patches.reduce((n,x)=>n+x.bytes,0),28);
 assert.equal(s.storage.instructions,9);assert.equal(s.storage.predecessor.dead,true);assert.equal(s.storage.predecessor.address,sem.helper-2);
 assert.equal(s.helper.live_bytes,25);assert.equal(s.helper.executed_per_phase,5);assert.equal(s.helper.records.length,2);
 assert.equal(s.numeric.signed_cases,131072);assert.equal(s.numeric.table_cases,512);assert.equal(s.numeric.word_loads,131584);
 assert.equal(s.numeric.new_steps-s.numeric.old_steps,5*131584);assert.equal(s.frame_bytes,112);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.table.exp2_bytes,16);assert.equal(p.table.exp2_word_bytes,16);
 const logn=require('../tools/esp8266_opus_asm/pvq_logn_word_proof.cjs');assert.ok(logn.helper+logn.helperBytes<=sem.helper);
});
test('exp2 proof rejects wrong phase, alignment, sign, source register and continuation',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 for(const [pc,from,to]of [[sem.helper,/a3, 1,/,'a3, 0,'],[sem.helper+3,/a3, a3, -2/,'a3, a3, -1'],[sem.helper+8,/srai/,'srli'],[sem.helper+14,/a3, a3, 0/,'a3, a4, 0'],[sem.helper+11,/4024dc79/,'4024dc7b']])assert.throws(()=>sem.prove(old,at(now,pc,from,to)));
 assert.throws(()=>sem.prove(old,at(now,sem.continuation,/a4, 14/,'a4, 13')),/Outside/);
 assert.throws(()=>sem.findPatches(at(old,0x4024e1a3,/4024e434/,'4024dcf8')),/Occupied/);
});
test('exp2 word bounds, values and originally dead storage are authenticated',()=>{
 const p=proof(),elf=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
 const storage=Buffer.from(elf);storage[frozen.offsetAt(storage,sem.helper,sem.helperBytes)]^=1;assert.throws(()=>sem.storageBytesProof(storage),/storage changed/);
 const changed=Buffer.from(elf),address=sem.tableBase;
 const ss=require('../tools/esp8266_opus_asm/frozen_div.cjs').sections(changed).filter(s=>s.type===1&&(s.flags&2)&&address>=s.address&&address+16<=s.address+s.bytes);assert.equal(ss.length,1);
 changed[ss[0].offset+address-ss[0].address]^=1;assert.throws(()=>f.tableProof(changed));
 for(const off of [1,16]){const r=Array(16).fill(0);r[3]=sem.tableBase+off;assert.throws(()=>sem.execute(p.actual_functions.quant_partition,r,Buffer.alloc(16),0));}
 assert.equal(p.semantic.search.helper.sar,'untouched');
});
test('exp2 host model preserves24 PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-exp2-word');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_exp2_word.cjs')));
});
