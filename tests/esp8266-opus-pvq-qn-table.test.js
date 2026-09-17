const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_qn_table.cjs'),s=require('../tools/esp8266_opus_asm/pvq_qn_table_proof.cjs');
const old=require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
function change(fn,pc,from,to){const result={...fn,disassembly:fn.disassembly.split('\n').map(l=>l.trimStart().startsWith(pc.toString(16)+':')?l.replace(from,to):l).join('\n')};assert.notEqual(result.disassembly,fn.disassembly);return result;}
test('linked qn table preserves all GPRs and SAR for the entire guarded domain with unchanged RAM',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.cases,61*64);assert.equal(p.semantic.old_steps,13);assert.equal(p.semantic.new_steps,11);
 assert.equal(p.table.bytes,260);assert.equal(p.app_bytes,903216);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.semantic.frame_bytes,112);
 assert.equal(p.semantic.domain.minimum,4);assert.equal(p.semantic.domain.maximum,64);
 assert.ok(old.table>=s.table&&old.table+32<=s.table+s.tableBytes);
 const parse=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs').parsed;
 for(const fn of[p.functions.quant_partition,p.actual_functions.quant_partition])
  for(const row of parse(fn).filter(r=>s.inside(r.address)))
   for(const operand of row.operands.filter(x=>/^a\d+$/.test(x)))assert.ok(['a2','a3','a4'].includes(operand));
 const expected=require('../tools/esp8266_opus_asm/profile_pvq_qn.cjs').qnTable();assert.deepEqual(s.values.slice(4).map(n=>n&~1),expected);
});
test('proof rejects changed rounding, SAR, upper/lower guards and extra entries',()=>{
 const p=proof(),a=p.functions.quant_partition,b=p.actual_functions.quant_partition;
 for(const [pc,from,to]of [[s.start,/a4, a2, 2/,'a4, a2, 1'],[s.start+11,/a4, 14/,'a4, 13'],[s.start+21,/a3, -2/,'a3, -1']])assert.throws(()=>s.prove(a,change(b,pc,from,to)));
 assert.throws(()=>s.findPatches(change(a,0x4024dbcd,/a2, 4/,'a2, 3')));
 assert.throws(()=>s.findPatches(change(a,0x4024dc61,/a3, 64/,'a3, 65')));
 assert.throws(()=>s.findPatches(change(a,0x4024e1a3,/4024e434/,'4024dcb0')));
});
test('all table words, original constants, literal and unexpected readers are authenticated',()=>{
 const p=proof(),a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz'))),b=base.patchElf(a,p.patches);
 assert.equal(s.literalProof(b,p.actual_functions.time_service_poll,true).sole_reader,s.start+3);
 for(const addr of[s.table+4*64,s.pool,old.oldTable]){const bad=Buffer.from(b);old.readAt(bad,addr,4)[0]^=1;assert.throws(()=>s.tableProof(bad,true));}
 const bad=Buffer.from(b),pc=s.table+8,off=base.offsetAt(bad,pc,3),delta=s.pool-((pc+3)&~3)+0x40000;
 bad[off]=0x21;bad.writeUInt16LE(delta/4,off+1);assert.throws(()=>s.literalProof(bad,p.actual_functions.time_service_poll,true),/Unexpected literal reader/);
 for(const qb of[-1,0,3,65,0x7fffffff])assert.throws(()=>s.execute(p.actual_functions.quant_partition,qb,0,true));
});
test('host model retains24 exact PCM/state/PLC/reset/OOM scenarios through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-qn-table');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_qn_table.cjs')));
});
