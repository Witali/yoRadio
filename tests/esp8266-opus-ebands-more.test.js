const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/ebands_more.cjs'),s=require('../tools/esp8266_opus_asm/ebands_more_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),{parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
test('two additional linked eBands leaves preserve signed pairs and every live register with zero RAM/stack growth',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.numeric_cases,264832);assert.equal(p.semantic.frame_bytes,192);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.patches.length,4);assert.equal(p.patches.reduce((n,x)=>n+x.bytes,0),87);
 for(const c of p.semantic.cases){assert.deepEqual(c.symbolic.map(x=>x.loads),[1,2]);assert.ok(c.dead_return.visited.length);assert.ok(c.dead_return.stops.length);}
 assert.equal(p.semantic.storage.bytes,72);assert.equal(p.table.bytes,44);
});
test('proof rejects sign errors, unexpected registers, live a0 and occupied storage',()=>{
 const p=read('preflight.json');
 for(let i=0;i<s.specs.length;i++){
  const text=p.helperDisassembly[i];assert.throws(()=>s.symbolic(text.replace('srai\ta2, a2, 16','srai\ta2, a2, 15'),s.specs[i]));
  assert.throws(()=>s.symbolic(text.replace('srai\ta2, a2, 16','srai\ta9, a2, 16'),s.specs[i]));
 }
 const fn=p.functions.clt_compute_allocation,bad={...fn,disassembly:fn.disassembly.replace('sub\ta3, a3, a2','sub\ta3, a0, a2')};assert.notEqual(bad.disassembly,fn.disassembly);assert.throws(()=>s.deadReturn(bad,s.specs[0]),/Live a0/);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs').readAt(a,s.specs[0].helper,1)[0]^=1;assert.throws(()=>s.storageBytesProof(a),/Storage already changed/);
});
test('both helper pointer phases and final table pair are bounded; preserved stack read is independent',()=>{
 const p=read('preflight.json'),data=Buffer.alloc(44),table=p.table.address;
 for(let i=0;i<s.specs.length;i++){
  const rows=[...parsed(p.actual_functions.clt_compute_allocation),...parsed({disassembly:p.helperDisassembly[i]})];
  for(const pointer of[table-2,table+42,table+1]){const r=Array(16).fill(0);r[5]=pointer;assert.throws(()=>s.execute(rows,s.specs[i],r,data,0,0),/Invalid pair pointer/);}
  const r=Array(16).fill(0);r[5]=table+40;data.writeInt16LE(-32768,40);data.writeInt16LE(32767,42);const out=s.execute(rows,s.specs[i],r,data,63,0xfedcba98);
  assert.equal(out.registers[2],0xffff8000);assert.equal(out.registers[s.specs[i].high],32767);assert.equal(out.sar,63);assert.equal(out.words,1);assert.equal(out.stack,i);if(i)assert.equal(out.registers[14],0xfedcba98);
 }
});
test('host model retains24 exact PCM/state/PLC/reset/OOM scenarios through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'ebands-more');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ebands_more.cjs')));
});
