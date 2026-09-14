// Complete linked-path proof for the fifteen-way unrolled PVQ search.
// Symbolic uint32 arithmetic / arbitrary memory, followed by numeric edge paths.
const assert=require('node:assert/strict'),base=require('./frozen_reloads.cjs');
const {hash}=require('./export.cjs'),{target}=require('./pvq_row_proof.cjs');
const address=0x402533b9,done=0x402534d7,bytes=done-address;
const clean=r=>r.text.replace(/\s+<[^>]*>$/,'');
const inside=fn=>base.rows(fn.disassembly).filter(r=>r.address>=address&&r.address<done);
const oldHash='622ef239b3b702650b4bda95955fde637b4720f52e9f9e85a1ef077c67d8568f';
function audit(fn,original){
 const rs=base.rows(fn.disassembly),inner=inside(fn);
 if(original)assert.equal(hash(inner.map(clean).join('\n')),oldHash,'Original block changed');
 assert.equal(rs[0].text,'addi a1, a1, -48');
 assert.deepEqual(rs.filter(r=>/^call/.test(r.op)).map(r=>[r.address,r.text]),[[0x40253213,'call0 40246c20 <ec_dec_uint>']]);
 const outside=rs.filter(r=>r.address<address||r.address>=done);
 assert.deepEqual(outside.filter(r=>/\ba0\b/.test(r.args)).map(r=>[r.address,r.text]),
  [[0x402531cd,'s32i a0, a1, 44'],[0x40253584,'l32i a0, a1, 44']],'a0 is not dead until restore');
 assert.deepEqual(rs.filter(r=>/^ret/.test(r.op)).map(r=>r.address),[0x40253597]);
 assert.deepEqual(rs.filter(r=>/\ba1, 44$/.test(r.args)).map(r=>r.address),[0x402531cd,0x40253584]);
 assert.deepEqual(rs.filter(r=>/^addi/.test(r.op)&&r.args.startsWith('a1,')).map(r=>r.text),
  ['addi a1, a1, -48','addi a1, a1, 48']);
 for(const r of rs){
  assert.ok(!/^jx|^callx/.test(r.op),'Indirect transfer');
  if(/^b|^j$/.test(r.op)){
   const t=target(r);assert.ok(Number.isFinite(t));
   if(r.address<address||r.address>=done)assert.ok(t<=address||t>=done,'External interior entry');
   if(r.address>0x40253213)assert.ok(t>=0x40253216&&t<=0x40253597,'Return to pre-save/call code');
  }
 }
 return rs;
}
const variable=n=>({[n]:1}),constant=n=>({'#':n>>>0});
function affine(...terms){const out={};for(const[v,m]of terms)for(const[k,x]of Object.entries(v))out[k]=((out[k]||0)+Math.imul(x,m))>>>0;return Object.fromEntries(Object.entries(out).filter(([,v])=>v).sort(([a],[b])=>a.localeCompare(b)));}
const add=(a,b)=>affine([a,1],[b,1]),sub=(a,b)=>affine([a,1],[b,-1]),repr=x=>JSON.stringify(x);
const symbolicOps={
 num:constant,add,sub,neg:a=>affine([a,-1]),shl:(a,n)=>affine([a,2**n]),
 and:(a,b)=>variable('AND('+repr(a)+','+repr(b)+')'),
 load:p=>variable('MEM('+repr(p)+')')
};
function execute(rows,initial,ops,stop,memory){
 const r=structuredClone(initial),reads=[],branches=[],visited=new Set(),map=new Map(rows.map(r=>[r.address,r]));
 let pc=address,steps=0,count=0;
 while(pc!==done){
  const row=map.get(pc);assert.ok(row,'Bad instruction address '+pc.toString(16));assert.ok(++steps<300);
  visited.add(pc);const [op,...args]=clean(row).replaceAll(',','').split(' '),d=+args[0]?.slice(1),s=+args[1]?.slice(1);
  const reg=x=>{assert.match(x,/^a(?:[0-9]|1[0-5])$/);return +x.slice(1);};
  let next=pc+row.bytes;
  if(op==='addi')r[d]=ops.add(r[s],ops.num(Number(args[2])));
  else if(op==='slli')r[d]=ops.shl(r[s],Number(args[2]));
  else if(op==='add')r[d]=ops.add(r[s],r[reg(args[2])]);
  else if(op==='sub')r[d]=ops.sub(r[s],r[reg(args[2])]);
  else if(op==='neg')r[d]=ops.neg(r[s]);
  else if(op==='and')r[d]=ops.and(r[s],r[reg(args[2])]);
  else if(op==='mov')r[d]=r[s];
  else if(op==='l32i'){const p=ops.add(r[s],ops.num(Number(args[2])));reads.push(p);r[d]=ops.load(p,memory);}
  else if(op==='bltu'||op==='bgeu'){
   ++count;assert.ok(count<=14,'Unexpected additional condition');
   const less=stop===null?r[d]<r[s]:count<stop;
   branches.push({left:r[d],right:r[s],less});
   if(op==='bltu'?less:!less)next=parseInt(args[2],16);
  }else if(op==='j')next=parseInt(args[0],16);else assert.fail('Unproved instruction '+op);
  pc=next;
 }
 return{registers:r,reads,branches,visited:[...visited],steps};
}
function symbolic(before,after){
 const initial=Array.from({length:16},(_,i)=>variable('R'+i)),paths=[],seenA=new Set(),seenB=new Set();
 for(let stop=1;stop<=15;stop++){
  const a=execute(before,initial,symbolicOps,stop),b=execute(after,initial,symbolicOps,stop);
  assert.deepEqual(a.registers.slice(1),b.registers.slice(1),'Live register at exit'+stop);
  assert.deepEqual(a.reads,b.reads);assert.deepEqual(a.branches,b.branches);
  assert.equal(a.branches.length,Math.min(stop,14));assert.equal(a.reads.length,2*stop);
  assert.equal(a.steps-b.steps,stop-1-(stop===8?1:0),'Dynamic instruction count');
  a.visited.forEach(v=>seenA.add(v));b.visited.forEach(v=>seenB.add(v));
  paths.push({stop,reads:a.reads,branches:a.branches,exit_registers:b.registers.slice(1),old_steps:a.steps,new_steps:b.steps});
 }
 assert.deepEqual([...seenA].sort(),before.map(r=>r.address).sort());
 assert.deepEqual([...seenB].sort(),after.map(r=>r.address).sort(),'Unproved reachable code');
 return{paths,scope:'All15 original exits, arbitrary uint32 registers and row values, exact ordered reads and branch predicates; a0 dead until checked restore. No fixture-derived K/N/bitrate cap.'};
}
const numericOps={num:n=>n>>>0,add:(a,b)=>(a+b)>>>0,sub:(a,b)=>(a-b)>>>0,neg:a=>(-a)>>>0,shl:(a,n)=>(a<<n)>>>0,and:(a,b)=>(a&b)>>>0,load:(p,m)=>{assert.ok(m.has(p),'Extra/out-of-row read '+p.toString(16));return m.get(p);}};
function numeric(before,after){
 let cases=0;const exits=Array(15).fill(0);
 for(const K of[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,31,255,0x7fffffff,0xffffffff])
 for(let stop=1;stop<=Math.min(K,15);stop++)for(const offset of[12,20,64,512])
 for(const index of[0,1,0x7ffffffe,0xfffffffe])for(const sign of[0,1]){
  const r=Array.from({length:16},(_,i)=>Math.imul(K+i+index,0x45d9f3b)>>>0),memory=new Map();
  r[2]=(index+sign)>>>0;r[3]=offset;r[4]=1;r[6]=sign;r[12]=K;r[14]=0x40280000;
  // Only cells actually read on this path exist; prefetch/out-of-bounds fails.
  for(let j=1;j<=stop;j++){const entry=(r[14]+Math.imul((K-j)>>>0,4))>>>0,ptr=0x20000+j*1024;memory.set(entry,ptr);memory.set(ptr+offset,j===stop?index:(index+1)>>>0);}
  const a=execute(before,r,numericOps,null,memory),b=execute(after,r,numericOps,null,memory);
  assert.deepEqual(a.registers.slice(1),b.registers.slice(1));assert.deepEqual(a.reads,b.reads);assert.deepEqual(a.branches,b.branches);
  assert.equal(a.reads.length,stop*2);assert.equal(b.registers[12],(K-stop)>>>0);
  assert.equal(a.steps-b.steps,stop-1-(stop===8?1:0));exits[stop-1]++;cases++;
 }
 return{cases,exits,scope:'Supplemental linked instruction execution on numeric uint32/sign/boundary paths, not a target timing measurement.'};
}
function prove(oldFn,newFn){
 const a=audit(oldFn,true),b=audit(newFn,false),outside=rs=>rs.filter(r=>r.address<address||r.address>=done);
 assert.deepEqual(outside(a),outside(b));const ar=inside(oldFn),br=inside(newFn);
 return{symbolic:symbolic(ar,br),numeric:numeric(ar,br),old_instructions:ar.length,new_instructions:br.length,live_bytes:br.reduce((s,r)=>s+r.bytes,0),a0_restore:0x40253584,frame_bytes:48,sar:'No instruction in the changed block writes SAR'};
}
module.exports={address,done,bytes,clean,inside,audit,execute,symbolic,numeric,prove};
