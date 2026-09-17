const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/ebands_final.cjs'),s=require('../tools/esp8266_opus_asm/ebands_final_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),{parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));

test('patch packaging cannot mutate the shared storage definitions',()=>{
 const p=read('preflight.json'),before=structuredClone(s.regions),patches=s.findPatches(p.functions);
 patches[3].after_hex='test';assert.deepEqual(s.regions,before);
 assert.ok(s.findPatches(p.functions).every(x=>!Object.hasOwn(x,'after_hex')));
});

test('three linked eBands pairs including split leaf preserve signed values and live registers without RAM/stack growth',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.numeric_cases,397248);assert.equal(p.semantic.frame_bytes,192);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.patches.length,7);assert.equal(p.patches.reduce((n,x)=>n+x.bytes,0),126);
 for(const c of p.semantic.cases){assert.deepEqual(c.symbolic.map(x=>x.loads),[1,2]);assert.ok(c.dead_return.visited.length>100);assert.ok(c.dead_return.stops.length);}
 assert.equal(p.semantic.storage.regions.reduce((n,r)=>n+r.bytes,0),108);assert.equal(p.table.bytes,44);
});

test('proof rejects sign errors, unexpected GPRs, broken split target, live a0 and occupied storage',()=>{
 const p=read('preflight.json');
 for(let i=0;i<s.specs.length;i++){
  const spec=s.specs[i],text=p.helperDisassembly[i],op='srai\ta'+spec.low+', a'+spec.low+', 16';assert.ok(text.includes(op));
  assert.throws(()=>s.symbolic(text.replace(op,op.replace(', 16',', 15')),spec));
  assert.throws(()=>s.symbolic(text.replace(op,'srai\ta9, a'+spec.low+', 16'),spec));
 }
 const split=p.helperDisassembly[2],broken=split.replace('4024dd14 <','4024dd15 <');assert.notEqual(split,broken);assert.throws(()=>s.symbolic(broken,s.specs[2]));
 const fn=p.functions.clt_compute_allocation,bad={...fn,disassembly:fn.disassembly.replace('sub\ta3, a3, a10','sub\ta3, a0, a10')};assert.notEqual(bad.disassembly,fn.disassembly);assert.throws(()=>s.deadReturn(bad,s.specs[0]),/Live a0/);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs').readAt(a,s.specs[0].helper,1)[0]^=1;assert.throws(()=>s.storageBytesProof(a),/Storage already changed/);
});

test('all three leaves reject invalid pointers and preserve extreme final signed pair with arbitrary SAR',()=>{
 const p=read('preflight.json'),data=Buffer.alloc(44),table=p.table.address;
 for(let i=0;i<s.specs.length;i++){
  const spec=s.specs[i],rows=[...parsed(p.actual_functions.clt_compute_allocation),...parsed({disassembly:p.helperDisassembly[i]})];
  for(const pointer of[table-2,table+42,table+1]){const r=Array(16).fill(0);r[spec.p]=pointer;assert.throws(()=>s.execute(rows,spec,r,data,0,0),/Invalid pair pointer/);}
  const r=Array(16).fill(0);r[spec.p]=table+40;data.writeInt16LE(-32768,40);data.writeInt16LE(32767,42);const out=s.execute(rows,spec,r,data,63,0xfedcba98);
  assert.equal(out.registers[spec.low],0xffff8000);assert.equal(out.registers[spec.high],32767);assert.equal(out.sar,63);assert.equal(out.words,1);assert.equal(out.stack,0);
 }
});

test('final eBands host mirror preserves24 PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'ebands-final');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ebands_final.cjs')));
});
