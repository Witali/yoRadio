// In-place propagation of23 local scalar copies, separate from ctx flag reads.
// A slot is NOT immutable: SP132 in particular carries both zero and one.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createRequire}=require('node:module');
const audit=require('./audit_quant_decode.cjs'),prior=require('./quant_decode_proof.cjs');
const {parsed}=require('./bits_fifth_proof.cjs');
const addresses=[0x40250902,0x402509d1,0x40250a95,0x40250a98,0x40250b70,0x40250d32,
 0x40250fc5,0x40251007,0x402511d6,0x402513d2,0x402514c0,0x40251518,0x40251681,
 0x40251781,0x402518d9,0x40251db8,0x40251e90,0x40251f27,0x402521c5,0x4025229c,
 0x40252334,0x402529f4,0x40252a20];
function facts(fn,options={}){
 // Expose facts only AFTER fixed-point convergence of the pinned analyzer.
 // Memory changes at stores; path merges/calls/aliases retain their original
 // invalidation rules. Its existing outputs must match exactly, unchanged.
 const file=path.join(__dirname,'audit_quant_decode.cjs'),code=fs.readFileSync(file,'utf8').replace(/\r\n/g,'\n');
 const anchor='ctx_encode_at_store:states[by.get(encodeStore)].r[13]';assert.equal(code.split(anchor).length-1,1);
 const instrumented=code.replace(anchor,anchor+`,
  load_values:rows.flatMap((r,i)=>!states[i]||r.op!=='l32i'||r.operands[1]!=='a1'||!states[i].mem.has(Number(r.operands[2]))?[]:
   [{address:r.address,bytes:r.bytes,text:r.text,register:r.operands[0],slot:Number(r.operands[2]),value:states[i].mem.get(Number(r.operands[2]))}])`);
 const module={exports:{}};
 new Function('require','module','exports','__filename','__dirname',instrumented)(createRequire(file),module,module.exports,file,__dirname);
 const {load_values,...analysis}=module.exports.analyze(fn,options);
 assert.deepEqual(analysis,audit.analyze(fn,options));return{load_values,analysis};
}
function findPatches(fn,options={}){
 const loads=facts(fn,options).load_values.filter(r=>r.slot!==32&&r.slot!==36);
 assert.deepEqual(loads.map(r=>r.address),addresses,'Local constants are not proven at all pinned PCs');
 return loads.map(r=>{
  assert.equal(r.bytes,3);assert.ok([124,132,140,192,220,240].includes(r.slot));assert.ok([0,1].includes(r.value));
  return{address:r.address,bytes:r.bytes,before:r.text,register:r.register,slot:r.slot,value:r.value,instruction:'movi '+r.register+', '+r.value};
 });
}
function sourceFor(patches){
 return '# Experimental quant_all_bands local scalar loads, native decoder only.\n'+
  '# LX106 call0 ABI; original384-byte frame and every instruction PC retained.\n'+
  '#23 local L32I -> MOVI, values proven at each use; slots may change elsewhere.\n'+
  '# No ctx SP32/36 load replacement from the unaccepted flags experiment.\n'+
  '# Same destination/width, no SAR, memory writes, branches, calls or RAM changes.\n'+
  '# Original GCC snapshot and C fallback unchanged. Proof: quant_locals_proof.cjs.\n'+
  patches.map((p,i)=>`\n# 0x${p.address.toString(16)}: ${p.before}; SP+${p.slot} is ${p.value} HERE\n.section .text.patch${i},"ax",@progbits\n.begin no-transform\n${p.instruction}\n.end no-transform\n`).join('');
}
function prove(before,after,patches){
 assert.deepEqual(patches.map(({before_hex,after_hex,...p})=>p),findPatches(before));
 assert.equal(before.address,after.address);assert.equal(before.bytes,after.bytes);
 const a=parsed(before),b=parsed(after);assert.equal(a.length,b.length);
 assert.deepEqual(a.map(r=>[r.address,r.bytes]),b.map(r=>[r.address,r.bytes]));
 for(let i=0;i<a.length;i++){
  const p=patches.find(p=>p.address===a[i].address);if(!p){assert.deepEqual(b[i],a[i]);continue;}
  assert.equal(b[i].op,'movi');assert.deepEqual(b[i].operands,[p.register,String(p.value)]);
 }
 return{replaced_reads:23,patched_bytes:69,instructions:a.length,frame_bytes:384,
  static_ram_delta:0,stack_delta:0,dynamic_instruction_count_delta:0,
  proof:'Pointwise induction at23 converged local scalar reads; same-width MOVI writes the proven value to the original destination. Every other opcode/operand/width/address is exact, including all ctx flag reads. Private slots are NOT treated as globally constant. No speed claim before target A/B/A.'};
}
module.exports={addresses,facts,findPatches,sourceFor,prove,contract:prior.contract};
