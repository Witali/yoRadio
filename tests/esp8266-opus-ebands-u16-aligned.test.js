const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/ebands_u16_aligned.cjs'),s=require('../tools/esp8266_opus_asm/ebands_u16_aligned_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),{parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const {readAt}=require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs'),read=n=>f.read(path.join(f.art('candidate'),n));

test('six positive eBands helpers save one executed instruction with unchanged callers, RAM, stack and image size',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.numeric_cases,401280);assert.equal(p.semantic.cases.length,6);assert.equal(p.semantic.frame_bytes,192);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.deepEqual(p.actual_functions,p.functions);assert.equal(p.patches.length,7);assert.equal(p.patches.reduce((n,x)=>n+x.bytes,0),222);
 assert.equal(p.semantic.live_bytes_before,216);assert.equal(p.semantic.live_bytes_after,180);
 for(const c of p.semantic.cases)for(let i=0;i<2;i++){assert.equal(c.after[i].steps,c.before[i].steps-1);assert.deepEqual({...c.after[i],steps:0},{...c.before[i],steps:0});}
 assert.equal(p.table.minimum,0);assert.equal(p.table.maximum,100);assert.equal(p.table.bytes,44);
});

test('positive-table proof rejects altered constants, wrong extraction and changed parent helpers',()=>{
 const p=read('preflight.json'),a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
 for(const value of[101,-1]){const copy=Buffer.from(a);readAt(copy,s.table+40,2).writeInt16LE(value);assert.throws(()=>s.tableProof(copy));}
 readAt(a,s.specs[0].helper,1)[0]^=1;assert.throws(()=>s.storageBytesProof(a),/Parent helper differs/);
 for(let i=0;i<s.specs.length;i++){
  const spec=s.specs[i],text=p.helperDisassembly[i],op='extui\ta'+spec.low+', a'+spec.high+', 0, 16';assert.ok(text.includes(op));
  assert.throws(()=>s.symbolic(text.replace(op,op.replace(', 16',', 6')),spec));
  assert.throws(()=>s.symbolic(text.replace(op,'extui\ta9, a'+spec.high+', 0, 16'),spec));
 }
});

test('negative or misaligned eBands inputs are explicitly outside this optimization contract',()=>{
 const p=read('preflight.json'),data=Buffer.alloc(44);
 for(let i=0;i<s.specs.length;i++){
  const spec=s.specs[i],rows=[...parsed(p.actual_functions.clt_compute_allocation),...parsed({disassembly:p.helperDisassembly[i]})];
  for(const pointer of[s.table-2,s.table+42,s.table+1]){const r=Array(16).fill(0);r[spec.p]=pointer;assert.throws(()=>s.execute(rows,spec,r,data,0,0),/Invalid pair pointer/);}
  const r=Array(16).fill(0);r[spec.p]=s.table+40;data.writeInt16LE(-1,40);assert.throws(()=>s.execute(rows,spec,r,data,63,0),/Negative eBands/);
  data.writeInt16LE(78,40);data.writeInt16LE(100,42);const out=s.execute(rows,spec,r,data,63,0xfedcba98);assert.equal(out.registers[spec.low],78);assert.equal(out.registers[spec.high],100);assert.equal(out.sar,63);assert.equal(out.words,1);
 }
});

test('immutable patch definitions and24 exact PCM host scenarios through510kbps and120ms',()=>{
 const p=read('preflight.json'),before=structuredClone(s.regions),patches=s.findPatches(p.functions);patches[0].after_hex='test';assert.deepEqual(s.regions,before);
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'ebands-u16-aligned');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ebands_u16_aligned.cjs')));
});

test('all five contiguous cross entries keep parent addresses and reject the prior unaligned experiment',()=>{
 const p=read('preflight.json');const a=s.alignment(p.helperDisassembly);assert.equal(a.length,6);
 for(const r of a){assert.equal(r.after,r.before);assert.equal(r.after%4,0);}
 const prior=f.read(path.join(f.art('candidate'),'../esp8266-opus-ebands-u16-candidate-v1/preflight.json'));
 assert.throws(()=>s.alignment(prior.helperDisassembly),/cross entry/);
});
