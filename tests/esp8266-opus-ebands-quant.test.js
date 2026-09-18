const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/ebands_quant.cjs'),s=require('../tools/esp8266_opus_asm/ebands_quant_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),{parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
test('quant_all_bands reuses exact signed leaf in15B with no RAM/stack/image growth',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.numeric_cases,132416);assert.equal(p.semantic.frame_bytes,384);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.patches.length,1);assert.equal(p.patches[0].bytes,15);
 assert.deepEqual(p.semantic.symbolic.map(x=>x.loads),[1,2]);assert.equal(p.semantic.dead_a5.overwrite,0x40250ace);
 assert.deepEqual(p.semantic.dead_a0.stops,[{pc:0x40250afa,kind:'call'}]);
});
test('all CFG paths initialize the eBands pointer and pass both loop increments',()=>{
 const fn=read('preflight.json').functions.quant_all_bands,rs=parsed(fn),map=new Map(rs.map(r=>[r.address,r]));
 const target=require('../tools/esp8266_opus_asm/partition_frozen_proof.cjs').target;
 const successors=r=>r.op==='ret'?[]:r.op==='j'?[target(r)]:/^b/.test(r.op)?[target(r),r.address+r.bytes]:[r.address+r.bytes];
 const reachable=(start,end,cut)=>{const pending=[start],seen=new Set();while(pending.length){const pc=pending.pop();if(pc===cut||seen.has(pc))continue;if(pc===end)return true;seen.add(pc);const r=map.get(pc);assert.ok(r,'CFG must be complete');pending.push(...successors(r));}return false;};
 const header=0x40250ab0,latch=0x4025283e;
 assert.deepEqual(rs.filter(r=>successors(r).includes(header)).map(r=>r.address),[0x40250aad,latch]);
 for(const pc of[0x402507e0,0x40250809,0x402508b9,0x402509fa,0x40250a86,0x40250aad])assert.equal(reachable(fn.address,header,pc),false,'Initialization bypass '+pc.toString(16));
 for(const pc of[0x402527f2,0x402527fd,0x40252804,0x40252815,0x40252823,0x40252828,0x4025282f,0x40252832,0x4025283b])assert.equal(reachable(header,latch,pc),false,'Loop increment bypass '+pc.toString(16));
 assert.equal(map.get(0x402527f2).text,'l32i a14, a1, 116');
});
test('proof rejects live temporary, changed stack load and modified shared leaf',()=>{
 const p=read('preflight.json'),fn=p.functions.quant_all_bands;
 const bad={...fn,disassembly:fn.disassembly.replace('sub\ta12, a10, a11','sub\ta12, a5, a11')};assert.notEqual(bad.disassembly,fn.disassembly);assert.throws(()=>s.deadA5(bad),/Live a5/);
 // The same stack load occurs earlier too: mutate every exact match so the
 // target instruction, not an unrelated predecessor, is definitely changed.
 const changed={...fn,disassembly:fn.disassembly.replaceAll('l32i\ta9, a1, 0x1ac','l32i\ta9, a1, 0x1a8')};assert.notEqual(changed.disassembly,fn.disassembly);
 assert.throws(()=>s.findPatches({...p.functions,quant_all_bands:changed}));
 const elf=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
 require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs').readAt(elf,s.helper,1)[0]^=1;assert.throws(()=>s.sharedLeaf(elf),/Accepted helper changed/);
});
test('last pair signed extremes and all independent stack loads survive; invalid pointers rejected',()=>{
 const p=read('preflight.json'),rows=[...parsed(p.actual_functions.quant_all_bands),...parsed({disassembly:p.helperDisassembly})],data=Buffer.alloc(44),table=p.table.address;
 const stack={116:0x12345678,428:0x87654321,200:0xfedcba98};
 for(const pointer of[table-2,table+42,table+1]){const r=Array(16).fill(0);r[8]=pointer;assert.throws(()=>s.execute(rows,r,data,0,stack),/Invalid pair pointer/);}
 const r=Array(16).fill(0);r[8]=table+40;data.writeInt16LE(-32768,40);data.writeInt16LE(32767,42);const o=s.execute(rows,r,data,63,stack);
 assert.equal(o.registers[2],0xffff8000);assert.equal(o.registers[3],32767);assert.equal(o.registers[8],r[8]);assert.equal(o.sar,63);assert.equal(o.words,1);
 assert.deepEqual(o.stack,[{offset:116,d:10,value:stack[116]},{offset:428,d:9,value:stack[428]},{offset:200,d:11,value:stack[200]}]);
});
test('quant pair host mirror passes24 PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'ebands-quant');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ebands_quant.cjs')));
});
