const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/ebands_src.cjs'),s=require('../tools/esp8266_opus_asm/ebands_src_proof.cjs');
const {parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs'),{sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
test('SRC candidate replaces one36B leaf, keeps all callers/layout/RAM and exact signed pairs',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.numeric_cases,132416);assert.equal(p.semantic.live_bytes,31);assert.equal(p.semantic.padding_bytes,5);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.deepEqual(p.patches.map(({address,bytes})=>({address,bytes})),[{address:s.helper,bytes:36}]);
 assert.deepEqual(p.functions,p.actual_functions);assert.equal(p.semantic.dead_sar.overwrite,0x40248426);
 assert.deepEqual(p.semantic.operations.candidate_instructions,[12,12]);assert.deepEqual(p.semantic.operations.candidate_word_loads,[2,2]);
});
test('proof rejects live SAR, modified SRC operand order and changed accepted leaf',()=>{
 const p=read('preflight.json'),functions=structuredClone(p.functions);
 const fn=functions.clt_compute_allocation,old=fn.disassembly;
 fn.disassembly=old.replaceAll('slli\ta2, a3, 1','sll\ta2, a3');assert.notEqual(fn.disassembly,old);assert.throws(()=>s.deadSar(functions));
 const bad=p.helperDisassembly.replace('src\ta3, a3, a2','src\ta3, a2, a3');assert.notEqual(bad,p.helperDisassembly);assert.throws(()=>s.symbolic(bad));
 const elf=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
 require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs').readAt(elf,s.helper,1)[0]^=1;assert.throws(()=>s.storageBytesProof(elf),/Accepted helper changed/);
});
test('last signed pair never reads beyond44B; inputs and unrelated registers preserved',()=>{
 const p=read('preflight.json'),rows=s.shape(p.helperDisassembly),table=p.table.address,data=Buffer.alloc(44),r=Array.from({length:16},(_,i)=>0xabcd0000+i);
 r[5]=table+40;data.writeInt16LE(-32768,40);data.writeInt16LE(32767,42);
 const a=s.execute(rows,r,data,63),expected=r.slice();expected[2]=0xffff8000;expected[3]=32767;
 assert.deepEqual(a.registers,expected);assert.deepEqual(a.loads,[table+40,table+40]);assert.equal(a.sar,0);
 for(const pointer of[table-2,table+42,table+1]){const q=r.slice();q[5]=pointer;assert.throws(()=>s.execute(rows,q,data,0),/Invalid pair pointer/);}
 const bad=structuredClone(rows),load=bad.find(x=>x.op==='l32i'&&x.operands[0]==='a3');load.operands[2]='4';assert.throws(()=>s.execute(bad,r,data,0),/Outside eBands/);
});
test('symbolic proof covers independent words and both alignment phases, not positive-only values',()=>{
 const p=s.symbolic(read('preflight.json').helperDisassembly);
 assert.deepEqual(p.map(x=>x.sar),[0,16]);assert.equal(p[0].first[31],'A15');assert.equal(p[0].second[31],'A31');assert.equal(p[1].first[31],'A31');assert.equal(p[1].second[31],'B15');
});
test('C mirror applies SRC to the init loop only, not the allocation-vector search',()=>{
 const model=f.cModels().find(m=>m.source==='upstream/celt/rate.c'),text=fs.readFileSync(model.file,'utf8');
 const init=text.slice(text.indexOf('   for (j=start;j<end;j++)',text.indexOf('int clt_compute_allocation(')),text.indexOf('   lo = 1;',text.indexOf('int clt_compute_allocation(')));
 assert.equal((init.match(/y_ebands_src_width\(m,j\)/g)||[]).length,3);
 assert.match(text,/int N = y_ebands_width\(m,j\);/);assert.doesNotMatch(text,/int N = y_ebands_src_width/);
});
test('host mirror passes24 exact PCM/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'ebands-src');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ebands_src.cjs')));
});
