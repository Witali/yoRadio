// Same-address L32I -> MOVI experiment in the accepted quant_all_bands.
// No encoder branch removal, relocation, new frame, scratch register or SAR use.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createRequire}=require('node:module');
const audit=require('./audit_quant_decode.cjs'),prior=require('./quant_decode_proof.cjs');
const {parsed}=require('./bits_fifth_proof.cjs');

function facts(fn,options={}){
 // Expose only the converged load facts of the existing pinned analyzer.
 // Do not modify its transfer functions, merge, successor rules or old file:
 // old experiment manifests authenticate that file. Check every original
 // output against its uninstrumented run below, and hash this adapter as well.
 const file=path.join(__dirname,'audit_quant_decode.cjs');
 const code=fs.readFileSync(file,'utf8').replace(/\r\n/g,'\n');
 const anchor='ctx_encode_at_store:states[by.get(encodeStore)].r[13]';
 assert.equal(code.split(anchor).length-1,1);
 const instrumented=code.replace(anchor,anchor+`,
  load_values:rows.flatMap((r,i)=>!states[i]||r.op!=='l32i'||r.operands[1]!=='a1'||![32,36].includes(Number(r.operands[2]))?[]:
   [{address:r.address,bytes:r.bytes,text:r.text,register:r.operands[0],slot:Number(r.operands[2]),value:states[i].mem.get(Number(r.operands[2]))??null}])`);
 const module={exports:{}};
 new Function('require','module','exports','__filename','__dirname',instrumented)(createRequire(file),module,module.exports,file,__dirname);
 const result=module.exports.analyze(fn,options),{load_values,...original}=result;
 assert.deepEqual(original,audit.analyze(fn,options),'Observation changed dataflow analysis');
 return{load_values,analysis:original};
}
function findPatches(fn,options={}){
 const observed=facts(fn,options);
 assert.equal(observed.load_values.length,18,'Unexpected reachable private flag reads');
 const patches=observed.load_values.map(r=>{
  const value=r.slot===32?0:1;
  assert.equal(r.value,value,'Flag not proven at load 0x'+r.address.toString(16));
  assert.ok([2,3].includes(r.bytes));
  return{address:r.address,bytes:r.bytes,before:r.text,register:r.register,slot:r.slot,value,
   instruction:(r.bytes===2?'movi.n':'movi')+' '+r.register+', '+value};
 });
 assert.equal(patches.reduce((n,p)=>n+p.bytes,0),37);
 return patches;
}
function sourceFor(patches){
 return '# Experimental quant_all_bands private flag loads, native decoder only.\n'+
  '# LX106 call0 ABI: original384-byte frame, every instruction address retained.\n'+
  '# ctx.encode=0 / ctx.resynth=1 proven at each reachable read after initialization.\n'+
  '# MOVI writes the same destination; no SAR, memory write, branch or call changes.\n'+
  '# Original GCC snapshot and C fallback are unchanged. No added RAM or scratch.\n'+
  patches.map((p,i)=>`\n# 0x${p.address.toString(16)}: ${p.before}; private SP+${p.slot}, immutable ${p.value}\n.section .text.patch${i},"ax",@progbits\n.begin no-transform\n${p.instruction}\n.end no-transform\n`).join('');
}
function prove(before,after,patches){
 assert.deepEqual(patches.map(({before_hex,after_hex,...p})=>p),findPatches(before));
 assert.equal(before.address,after.address);assert.equal(before.bytes,after.bytes);
 const a=parsed(before),b=parsed(after);assert.equal(a.length,b.length);
 assert.deepEqual(a.map(r=>[r.address,r.bytes]),b.map(r=>[r.address,r.bytes]));
 for(let i=0;i<a.length;i++){
  const p=patches.find(p=>p.address===a[i].address);
  if(!p){assert.deepEqual(b[i],a[i]);continue;}
  assert.equal(b[i].op,'movi');assert.deepEqual(b[i].operands,[p.register,String(p.value)]);
 }
 return{replaced_reads:patches.length,patched_bytes:37,instructions:a.length,frame_bytes:384,
  static_ram_delta:0,stack_delta:0,dynamic_instruction_count_delta:0,
  proof:'Pointwise induction: every reached load reads its converged immutable ctx flag value; same-width MOVI writes the identical destination. Every other instruction/address/width/operand, including calls and branches, is exact. No claim of a speedup before target A/B/A.'};
}
module.exports={facts,findPatches,sourceFor,prove,contract:prior.contract};
