const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_exp2_table32.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),frozen=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
function at(fn,pc,from,to){const out={...fn,disassembly:fn.disassembly.split('\n').map(l=>l.trimStart().startsWith(pc.toString(16)+':')?l.replace(from,to):l).join('\n')};assert.notEqual(out.disassembly,fn.disassembly);return out;}
function images(){const p=proof(),a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));return{p,a,b:frozen.patchElf(a,p.patches)};}
test('exp2 direct table32 preserves exact signed arithmetic, all registers at join, memory and image size',()=>{
 const p=f.verifyPair().proof,s=p.semantic.search;assert.equal(p.patches.length,4);assert.equal(p.patches.reduce((n,x)=>n+x.bytes,0),42);
 assert.equal(s.storage.bytes,32);assert.equal(s.storage.instructions,11);assert.equal(s.storage.predecessor.dead,true);assert.equal(s.storage.predecessor.address,sem.table-2);
 assert.equal(s.symbolic.cases,8);assert.equal(s.numeric.signed_cases,131072);assert.equal(s.numeric.table_cases,3904);assert.equal(s.numeric.old_steps,944832);assert.equal(s.numeric.new_steps,s.numeric.old_steps);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);assert.equal(s.frame_bytes,112);
 assert.equal(p.table.exp2_original_bytes,16);assert.equal(p.table.exp2_word_bytes,32);assert.equal(p.literal_readers.sole_reader,sem.literalSite);
 for(const name of ['pvq_logn_word_proof','pvq_exp2_word_proof']){const x=require('../tools/esp8266_opus_asm/'+name+'.cjs');assert.ok(x.helper+x.helperBytes<=sem.table);}
});
test('table32 proof rejects changed scaling, load, immediate kill, outside bytes and interior entries',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 for(const [pc,from,to]of [[sem.shift,/a4, a3, 2/,'a4, a3, 1'],[sem.load,/l32i/,'l16si'],[sem.continuation-2,/a4, 14/,'a4, 13'],[sem.start,/a3, a2, 0, 3/,'a3, a2, 0, 4']])assert.throws(()=>sem.prove(old,at(now,pc,from,to)));
 assert.throws(()=>sem.findPatches(at(old,0x4024e1a3,/4024e434/,'4024dc6b')),/Interior/);
 assert.throws(()=>sem.findPatches(at(old,0x4024e1a3,/4024e434/,'4024dd28')),/Occupied/);
});
test('literal audit finds every byte-aligned reader and rejects aliases or new readers',()=>{
 const {p,a}=images(),time=p.functions.time_service_poll;
 assert.equal(sem.literalReadersProof(a,time).excluded_mid_instruction,0x4021d1d3);
 const extra=Buffer.from(a),pc=0x4024dd78,off=frozen.offsetAt(extra,pc,3),delta=sem.pool-((pc+3)&~3)+0x40000;assert.equal(delta%4,0);
 extra[off]=0x21;extra.writeUInt16LE(delta/4,off+1);assert.throws(()=>sem.literalReadersProof(extra,time),/Unexpected literal reader/);
 const pointer=Buffer.from(a);pointer.writeUInt32LE(sem.pool,frozen.offsetAt(pointer,sem.table,4));assert.throws(()=>sem.literalReadersProof(pointer,time),/Address-taken/);
 assert.throws(()=>sem.literalReadersProof(a,at(time,0x4021d1d2,/a12, a1, 200/,'a12, a1, 196')));
});
test('old constants, sign-extended copy, literal pointer and originally dead bytes are authenticated',()=>{
 const {a,b}=images();assert.deepEqual(f.tableProof(a),f.tableProof(b,true));
 const storage=Buffer.from(a);storage[frozen.offsetAt(storage,sem.table,32)]^=1;assert.throws(()=>sem.storageBytesProof(storage),/storage changed/);
 const copy=Buffer.from(b);copy[frozen.offsetAt(copy,sem.table,32)]^=1;assert.throws(()=>f.tableProof(copy,true),/Signed32 table copy/);
 const pointer=Buffer.from(b);pointer.writeUInt32LE(sem.oldTable,frozen.offsetAt(pointer,sem.pool,4));assert.throws(()=>f.tableProof(pointer,true),/literal pointer/);
 const old=Buffer.from(b),ss=require('../tools/esp8266_opus_asm/frozen_div.cjs').sections(old).find(s=>s.type===1&&(s.flags&2)&&sem.oldTable>=s.address&&sem.oldTable+16<=s.address+s.bytes);
 old[ss.offset+sem.oldTable-ss.address]^=1;assert.throws(()=>f.tableProof(old,true));
});
test('inline data path also agrees on unclamped bit patterns and preserves arbitrary SAR',()=>{
 const p=proof(),half=Buffer.alloc(16),word=Buffer.alloc(32);sem.values.forEach((v,i)=>{half.writeInt16LE(v,i*2);word.writeInt32LE(v,i*4);});
 for(const qb of[0,3,4,7,8,63,64,0x7fffffff,0x80000000,0xffffffff])for(const sar of[0,31,63]){
  const initial=Array.from({length:16},(_,i)=>0xdead0000+i);initial[2]=qb;
  const a=sem.execute(p.functions.quant_partition,initial,half,word,sar,false),b=sem.execute(p.actual_functions.quant_partition,initial,half,word,sar,true);
  assert.deepEqual(a.registers,b.registers);assert.equal(b.sar,sar);assert.equal(a.steps,7);assert.equal(b.steps,7);
 }
});
test('table32 host model preserves24 exact PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-exp2-table32');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_exp2_table32.cjs')));
});
