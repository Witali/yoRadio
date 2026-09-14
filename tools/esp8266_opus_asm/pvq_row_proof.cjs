// Actual linked instruction validation plus affine induction and edge emulator.
// No fixture-derived K/N cap. C/GCC snapshot unchanged; all arithmetic mod2^32.
const assert=require('node:assert/strict'),base=require('./frozen_reloads.cjs');
const address=0x40253331,bytes=35,done=0x40253361;
const oldOps=['addi a3, a12, -1','slli a8, a3, 2','add a6, a6, a8','addi a6, a6, -4','l32i a8, a6, 4','mov a12, a3','bgeu a2, a8, 40253348','addi a3, a3, -1','j 40253338','slli a9, a3, 16','srai a11, a9, 16','addi a6, a13, -1','j 40253361'];
const newOps=['addi a6, a15, -4','l32i a8, a6, 0','addi a6, a6, -4','addi a12, a12, -1','bltu a2, a8, 40253334','mov a3, a12','slli a9, a3, 16','srai a11, a9, 16','addi a6, a13, -1','j 40253361'];
const clean=r=>r.text.replace(/\s+<[^>]*>$/,'');
const inside=fn=>base.rows(fn.disassembly).filter(r=>r.address>=address&&r.address<address+bytes);
const target=r=>parseInt(r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]*>$/)?.[1],16);
function audit(fn,ops){const rs=base.rows(fn.disassembly);assert.deepEqual(inside(fn).map(clean),ops);
 for(const r of rs){assert.ok(!/^jx|^callx/.test(r.op),'Indirect edge requires separate audit');if(/^b|^j$|^call/.test(r.op)&&!(r.address>=address&&r.address<address+bytes)){const t=target(r);assert.ok(Number.isFinite(t));assert.ok(t<=address||t>=address+bytes,'External interior entry');}}
 assert.equal(rs.find(r=>r.address===0x40253329)?.text,'addi a15, a15, -4');assert.equal(rs.find(r=>r.address===0x4025332c)?.text,'l32i a8, a15, 0');
 assert.equal(rs.find(r=>r.address===0x4025332e)?.op,'bgeu');assert.equal(target(rs.find(r=>r.address===0x4025332e)),0x4025335d);
 assert.equal(rs[0].text,'addi a1, a1, -48');return rs;
}
const constant=n=>({'#':n>>>0}),variable=n=>({[n]:1});
function affine(...terms){const out={};for(const[v,m]of terms)for(const[k,x]of Object.entries(v))out[k]=((out[k]||0)+Math.imul(x,m))>>>0;return Object.fromEntries(Object.entries(out).filter(([,v])=>v).sort(([a],[b])=>a.localeCompare(b)));}
const add=(v,n)=>affine([v,1],[constant(n),1]),scale=(v,n)=>affine([v,n]);
const render=v=>JSON.stringify(v);
function symbolic(ops,initial){const r=structuredClone(initial),reads=[];for(const op of ops){const [cmd,...args]=op.replaceAll(',','').split(' ');const d=+args[0]?.slice(1),s=+args[1]?.slice(1),n=+args[2];
  if(cmd==='addi')r[d]=add(r[s],n);else if(cmd==='slli')r[d]=scale(r[s],2**n);else if(cmd==='add')r[d]=affine([r[s],1],[r[+args[2].slice(1)],1]);else if(cmd==='mov')r[d]=r[s];
  else if(cmd==='l32i'){const p=add(r[s],n);reads.push(p);r[d]=variable('MEM'+render(p));}
  else if(cmd==='srai')r[d]=variable('SRA'+n+render(r[s]));else assert.fail(op);
 }return{r,reads};}
function induction(){const initial=Array.from({length:16},(_,i)=>variable('R'+i));initial[6]=variable('B');initial[12]=variable('K');initial[13]=variable('N');initial[15]=affine([initial[6],1],[initial[12],4]);
 const a=symbolic(oldOps.slice(0,3),initial),b=symbolic(newOps.slice(0,1),initial);assert.deepEqual(a.r[6],b.r[6]);assert.deepEqual(a.r[3],add(initial[12],-1));
 const k=affine([variable('K'),1],[variable('J'),-1]),ptr=affine([variable('B'),1],[k,4]);const ar=structuredClone(initial),br=structuredClone(initial);
 ar[3]=k;ar[6]=ptr;ar[12]=add(k,1);br[6]=ptr;br[12]=add(k,1);
 const x=symbolic(oldOps.slice(3,6),ar),y=symbolic(newOps.slice(1,4),br);assert.deepEqual(x.reads,y.reads);for(const i of[2,6,8,12])assert.deepEqual(x.r[i],y.r[i]);
 // Unsigned BGEU exit and BLTU continue are complements, including equality.
 const exitA=symbolic(oldOps.slice(9,12),x.r),exitB=symbolic(newOps.slice(5,9),y.r);assert.deepEqual(exitA.r,exitB.r);
 const next=symbolic(oldOps.slice(7,8),x.r);assert.deepEqual(next.r[3],add(k,-1));assert.deepEqual(next.r[6],affine([variable('B'),1],[add(k,-1),4]));assert.deepEqual(y.r[6],next.r[6]);assert.deepEqual(y.r[12],k);
 return{scope:'Affine induction over any terminating valid row search, arbitrary unchanged registers, uint32 table values/index. No N/K/bitrate fixture cap.',entry_pointer:render(a.r[6]),iteration_read:render(x.reads[0]),exit_registers:exitA.r,old_loop_instructions:6,new_loop_instructions:4,table_reads_unchanged:true};
}
function emulate(rs,initial,memory){const r=initial.slice(),reads=[],map=new Map(rs.map(r=>[r.address,r]));let pc=address,steps=0;while(pc!==done){const row=map.get(pc);assert.ok(row,'Bad PC '+pc.toString(16));assert.ok(++steps<2000000,'Nontermination');const [op,...a]=clean(row).replaceAll(',','').split(' ');const d=+a[0]?.slice(1),s=+a[1]?.slice(1),n=+a[2];let next=pc+row.bytes;
  if(op==='addi')r[d]=(r[s]+n)>>>0;else if(op==='slli')r[d]=(r[s]<<n)>>>0;else if(op==='srai')r[d]=(r[s]>>n)>>>0;else if(op==='add')r[d]=(r[s]+r[+a[2].slice(1)])>>>0;else if(op==='mov')r[d]=r[s];
  else if(op==='l32i'){const p=(r[s]+n)>>>0;assert.ok(memory.has(p),'Out-of-row read '+p.toString(16));r[d]=memory.get(p);reads.push(p);}
  else if(op==='bgeu'||op==='bltu'){if(op==='bgeu'?r[d]>=r[s]:r[d]<r[s])next=parseInt(a[2],16);}
  else if(op==='j')next=parseInt(a[0],16);else assert.fail(op);
  pc=next;
 }return{registers:r,reads,steps};}
function numeric(oldRows,newRows){let cases=0,probes=0;const B=0x40280000;
 for(const K of[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,31,32,63,64,127,255,256,511,1023,32767,32768,65535]){
  const quantum=Math.floor(0xffffffff/(K+1)),memory=new Map(Array.from({length:K+1},(_,i)=>[B+4*i,i*quantum]));const tails=K<=64?Array.from({length:K},(_,i)=>i):[0,1,K>>>1,K-2,K-1];
  for(const tail of tails)for(const index of[memory.get(B+4*tail),memory.get(B+4*(tail+1))-1])for(const seed of[0,7349,0xffffffff]){
   const initial=Array.from({length:16},(_,i)=>Math.imul(seed+i,0x45d9f3b)>>>0);initial[2]=index;initial[6]=B;initial[12]=K;initial[13]=seed&0xffff;initial[15]=B+4*K;
   const a=emulate(oldRows,initial,memory),b=emulate(newRows,initial,memory);assert.deepEqual(a.registers,b.registers);assert.deepEqual(a.reads,b.reads);assert.equal(b.registers[12],tail);assert.equal(b.registers[3],tail);assert.equal(b.reads.length,K-tail);assert.equal(a.steps-b.steps,2*(K-tail)-1);cases++;probes+=b.reads.length;
  }
 }return{cases,probes,scope:'Supplemental numeric unsigned-boundary/long-search cases; linked instructions interpreted, not a target speed estimate.'};}
function prove(oldFn,newFn){const a=audit(oldFn,oldOps),b=audit(newFn,newOps);const outside=rs=>rs.filter(r=>r.address<address||r.address>=address+bytes);assert.deepEqual(outside(a),outside(b));const proof=induction();return{induction:proof,numeric:numeric(inside(oldFn),inside(newFn)),reachable_old:inside(oldFn).length,reachable_new:inside(newFn).length};}
module.exports={address,bytes,done,oldOps,newOps,inside,target,audit,induction,emulate,numeric,prove};
