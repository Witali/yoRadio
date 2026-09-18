// Conditional linked-ASM reachability census. Not a firmware patch or speed proof.
// Only the valid native decoder contract can justify the immutable ctx.encode.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash}=require('./export.cjs');
const {parsed}=require('./bits_fifth_proof.cjs'),{target}=require('./partition_frozen_proof.cjs');
const entry=0x402507d8,span=9416,encodeStore=0x402509e6;
const reg=s=>/^a(?:[0-9]|1[0-5])$/.test(s)?+s.slice(1):-1;
const same=(a,b)=>a===b;
function analyze(fn,{encodeZero=true,immutableContext=true,immutableResynth=true,privateFrame=true}={}){
 assert.equal(fn.address,entry);assert.equal(fn.bytes,span);
 const rows=parsed(fn),by=new Map(rows.map((r,i)=>[r.address,i]));
 assert.equal(rows[0].text,'movi a9, 384');assert.equal(rows[1].text,'sub a1, a1, a9');
 const stores=rows.filter(r=>/^s(?:8|16|32)i$/.test(r.op)&&r.operands[1]==='a1'&&Number(r.operands[2])<=32&&Number(r.operands[2])+Number(r.op.match(/\d+/)[0])/8>32);
 assert.deepEqual(stores.map(r=>r.address),[encodeStore]);
 assert.equal(stores[0].text,'s32i a13, a1, 32');
 const resynthStores=rows.filter(r=>/^s(?:8|16|32)i$/.test(r.op)&&r.operands[1]==='a1'&&Number(r.operands[2])<=36&&Number(r.operands[2])+Number(r.op.match(/\d+/)[0])/8>36);
 assert.deepEqual(resynthStores.map(r=>r.text),['s32i a8, a1, 36']);
 // The only escaping private-frame address is &ctx at SP+32. The pinned C
 // struct occupies 60 bytes. Callees may modify its other fields, never encode.
 // No automatic encoder arrays/context copies exist in this bounded build.
 const aliases=rows.filter(r=>r.operands.slice(1).includes('a1')&&!/^(?:l32i|l16si|l16ui|l8ui|s32i|s16i|s8i)$/.test(r.op));
 for(const r of aliases)assert.ok(['sub a1, a1, a9','add a1, a1, a9','or a1, a1, a1'].includes(r.text)||r.op==='addi'&&r.operands[1]==='a1'&&Number(r.operands[2])===32,'Unexpected private-frame alias '+r.text);
 for(const r of rows)if(/^s(?:8|16|32)i$/.test(r.op))assert.notEqual(r.operands[0],'a1','Stack pointer escapes via store');
 for(const r of rows)if(r.operands[0]==='a1'&&!/^b|^s(?:8|16|32)i$/.test(r.op))assert.ok(['sub a1, a1, a9','add a1, a1, a9','or a1, a1, a1'].includes(r.text),'Unexpected stack pointer write');
 const states=Array(rows.length),queue=[0],queued=new Set([0]),decisions=new Map();
 const initial={r:Array(16).fill(null),mem:new Map()};if(encodeZero)initial.r[2]=0;states[0]=initial;
 let iterations=0;
 const dropMemory=s=>{for(const [slot,v]of s.mem)if(!(immutableContext&&slot===32&&v===0)&&!(immutableResynth&&slot===36&&v===1)&&!(privateFrame&&slot>=92&&slot<364))s.mem.delete(slot);};
 while(queue.length){
  assert.ok(++iterations<rows.length*100,'Nonconverging analysis');
  const i=queue.shift();queued.delete(i);const row=rows[i],before=states[i],after={r:before.r.slice(),mem:new Map(before.mem)};
  const [d,a,b]=row.operands,di=reg(d),av=before.r[reg(a)],bv=before.r[reg(b)],dv=before.r[di],op=row.op;
  let take=null;
  if(['beqz','bnez','bltz','bgez'].includes(op)&&dv!==null)
   take=op==='beqz'?dv===0:op==='bnez'?dv!==0:op==='bltz'?(dv|0)<0:(dv|0)>=0;
  if(['beq','bne','blt','bge','bltu','bgeu','bnone','bany','ball','bnall'].includes(op)&&dv!==null&&av!==null){
   const choices={beq:dv===av,bne:dv!==av,blt:(dv|0)<(av|0),bge:(dv|0)>=(av|0),bltu:dv<av,bgeu:dv>=av,bnone:(dv&av)===0,bany:(dv&av)!==0,ball:((dv&av)>>>0)===av,bnall:((dv&av)>>>0)!==av};take=choices[op];
  }
  if(['beqi','bnei','blti','bgei','bltui','bgeui','bbci','bbsi'].includes(op)&&dv!==null){
   const n=Number(a),choices={beqi:(dv|0)===n,bnei:(dv|0)!==n,blti:(dv|0)<n,bgei:(dv|0)>=n,bltui:dv<(n>>>0),bgeui:dv>=(n>>>0),bbci:((dv>>>n)&1)===0,bbsi:((dv>>>n)&1)!==0};take=choices[op];
  }
  if(take!==null)decisions.set(i,{address:row.address,text:row.text,taken:take,target:target(row)});else decisions.delete(i);
  if(op==='movi')after.r[di]=Number(a)>>>0;
  else if(op==='mov')after.r[di]=av;
  else if(['add','sub','and','or','xor','mull','addx2','addx4','addx8','subx2','subx4','subx8'].includes(op)){
   if(av===null||bv===null)after.r[di]=null;
   else {
    const vals={add:av+bv,sub:av-bv,and:av&bv,or:av|bv,xor:av^bv,mull:Math.imul(av,bv),addx2:av*2+bv,addx4:av*4+bv,addx8:av*8+bv,subx2:av*2-bv,subx4:av*4-bv,subx8:av*8-bv};after.r[di]=vals[op]>>>0;
   }
  } else if(op==='addi'||op==='addmi')after.r[di]=av===null?null:(av+Number(b))>>>0;
  else if(['slli','srli','srai'].includes(op))after.r[di]=av===null?null:(op==='slli'?av<<Number(b):op==='srli'?av>>>Number(b):av>>Number(b))>>>0;
  else if(op==='extui')after.r[di]=av===null?null:((av>>>Number(b))&(2**Number(row.operands[3])-1))>>>0;
  else if(['moveqz','movnez','movltz','movgez'].includes(op)){
   if(bv===null)after.r[di]=same(dv,av)?dv:null;
   else if(op==='moveqz'?bv===0:op==='movnez'?bv!==0:op==='movltz'?(bv|0)<0:(bv|0)>=0)after.r[di]=av;
  } else if(op==='l32i')after.r[di]=a==='a1'?(before.mem.get(Number(b))??null):null;
  else if(/^s(?:8|16|32)i$/.test(op)){
   if(a==='a1'){
    const slot=Number(b),width=Number(op.match(/\d+/)[0])/8;
    for(const key of after.mem.keys())if(key<slot+width&&key+4>slot)after.mem.delete(key);
    if(op==='s32i'&&dv!==null)after.mem.set(slot,dv);
   }else dropMemory(after);
  } else if(/^call/.test(op)){for(let k=0;k<=11;k++)if(k!==1)after.r[k]=null;dropMemory(after);}
  else if(!/^b/.test(op)&&!['j','ret','nop','ssl','ssr','ssai','ssa8l','ssa8b'].includes(op)){
   assert.ok(di>=0,'Unknown instruction '+row.text);after.r[di]=null;
  }
  const branchIndex=()=>{const n=by.get(target(row));assert.ok(Number.isInteger(n),'External CFG edge');return n;};
  const successors=op==='ret'?[]:op==='j'?[branchIndex()]:/^b/.test(op)?take===true?[branchIndex()]:take===false?[i+1]:[i+1,branchIndex()]:[i+1];
  for(const n of successors){
   assert.ok(n<rows.length,'Fallthrough outside function');const old=states[n];
   const merged=old?{r:old.r.map((v,k)=>same(v,after.r[k])?v:null),mem:new Map([...old.mem].filter(([k,v])=>after.mem.has(k)&&same(v,after.mem.get(k))))}:after;
   if(!old||merged.r.some((v,k)=>v!==old.r[k])||merged.mem.size!==old.mem.size){states[n]=merged;if(!queued.has(n)){queue.push(n);queued.add(n);}}
  }
 }
 const dead=rows.filter((r,i)=>!states[i]),branches=[...decisions.values()].sort((a,b)=>a.address-b.address);
 return{assumptions:{entry_encode_zero:encodeZero,ctx_encode_immutable:immutableContext,ctx_resynth_immutable:immutableResynth,private_frame_unaliased:privateFrame},frame_bytes:384,iterations,branches,
  dead:dead.map(r=>({address:r.address,bytes:r.bytes,text:r.text})),removed_instructions:dead.length,removed_bytes:dead.reduce((n,r)=>n+r.bytes,0),
  calls_live:rows.filter((r,i)=>states[i]&&/^call/.test(r.op)).map(r=>({address:r.address,text:r.text})),
  ctx_encode_at_store:states[by.get(encodeStore)].r[13]};
}
function audit(){
 const parent=path.join(root,'firmware/development/esp8266-opus-ebands-final-candidate-v2/preflight.json'),p=JSON.parse(fs.readFileSync(parent));
 const fn=p.actual_functions.quant_all_bands,conditional=analyze(fn),unknown=analyze(fn,{encodeZero:false,immutableContext:false,immutableResynth:false});
 const bands=fs.readFileSync(path.join(component,'upstream/celt/bands.c'),'utf8');
 assert.deepEqual([...bands.matchAll(/ctx(?:\.|->)encode\s*=(?!=)[^;]*;/g)].map(m=>m[0]),['ctx.encode = encode;']);
 assert.deepEqual([...bands.matchAll(/ctx(?:\.|->)resynth\s*=(?!=)[^;]*;/g)].map(m=>m[0]),['ctx.resynth = resynth;']);
 const result={date:new Date().toISOString(),parent_sha256_lf:sourceHash(parent),checker_sha256_lf:sourceHash(__filename),
  conditional,unknown,ready_for_specialization:false,
  scope:'Conditional analysis only: entry encode=0, ctx.encode/resynth immutable, private SP+92..363 not aliased under valid native object contract. Outgoing/mutable ctx/incoming stack facts invalidated at calls/indirect stores. No firmware generated or timing claimed.'};
 const dest=path.join(root,'.build/opus-quant-decode-audit');fs.mkdirSync(dest,{recursive:true});
 fs.writeFileSync(path.join(dest,'audit.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({conditional:conditional.removed_instructions,bytes:conditional.removed_bytes,branches:conditional.branches,unknownDead:unknown.removed_instructions,unknownBranches:unknown.branches,remainingEncoderCalls:conditional.calls_live.filter(r=>/ec_enc|ec_encode|alg_quant|stereo_itheta/.test(r.text))},null,2));
 return result;
}
module.exports={entry,span,analyze,audit};if(require.main===module)audit();
