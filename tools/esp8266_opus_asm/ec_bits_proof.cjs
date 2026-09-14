// Interpret actual linked instructions. Bit-vector tail proof for arbitrary
// uint32 windows/state; separate numeric full-function refill/exhaustion checks.
const assert=require('node:assert/strict'),base=require('./frozen_reloads.cjs');
const address=0x40298575,bytes=35,entry=0x40298548;
const oldOps=['l32i a6, a2, 20','movi a5, -1','ssl a3','sll a9, a5','ssr a3','srl a8, a7','sub a4, a4, a3','xor a5, a5, a9','add a3, a6, a3','s32i a8, a2, 12','s32i a4, a2, 16','s32i a3, a2, 20','and a2, a5, a7','ret'];
const newOps=['l32i a6, a2, 20','ssr a3','srl a8, a7','ssl a3','sll a9, a8','ssr a3','sub a4, a4, a3','add a3, a6, a3','s32i a8, a2, 12','s32i a4, a2, 16','s32i a3, a2, 20','xor a2, a7, a9','ret'];
const clean=r=>r.text.replace(/\s+<[^>]*>$/,'').trim().replace(/^ret\.n$/,'ret');
const inside=fn=>base.rows(fn.disassembly).filter(r=>r.address>=address&&r.address<address+bytes);
function audit(fn,ops){assert.equal(fn.address,entry);assert.equal(fn.bytes,80);const rows=base.rows(fn.disassembly);assert.deepEqual(inside(fn).map(clean),ops);
 for(const r of rows){assert.doesNotMatch(r.op,/^(?:call|jx)/);if(/^b|^j$/.test(r.op)){const t=parseInt(r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]*>$/)?.[1],16);assert.ok(Number.isFinite(t));assert.ok(t<=address||t>=address+bytes,'Interior tail entry');}}
 assert.equal(rows.at(-1).op,'ret.n');return rows;}
const bits=n=>Array.from({length:32},(_,i)=>(n>>>i)&1),variable=n=>Array.from({length:32},(_,i)=>n+'['+i+']');
const key=w=>JSON.stringify(w),number=w=>{assert.ok(w.every(x=>x===0||x===1),'Nonconstant shift');return w.reduce((n,b,i)=>(n+(b?2**i:0))>>>0,0);};
function bitOp(op,a,b){return a.map((v,i)=>{const w=b[i];if(op==='xor'){if(v===w)return 0;if(v===0)return w;if(w===0)return v;if(typeof v==='number'&&typeof w==='number')return v^w;}
 else if(op==='and'){if(v===0||w===0)return 0;if(v===1)return w;if(w===1||v===w)return v;}
 return op+'('+[v,w].sort().join(',')+')';});}
const shift=(w,n,left)=>Array.from({length:32},(_,i)=>w[left?i-n:i+n]??0);
function symbolic(rs,n){const r=Array.from({length:16},(_,i)=>variable('R'+i)),events=[];r[3]=bits(n);let sar=7;
 for(const row of rs){const [op,...a]=clean(row).replaceAll(',','').split(' '),d=+a[0]?.slice(1),s=+a[1]?.slice(1),t=+a[2]?.slice(1);
  if(op==='ret')break;
  if(op==='l32i'){const p=key(r[s])+'+'+a[2];r[d]=variable('MEM('+p+')');events.push({kind:'read32',address:p,value:r[d]});}
  else if(op==='s32i')events.push({kind:'write32',address:key(r[s])+'+'+a[2],value:r[d]});
  else if(op==='movi')r[d]=bits(+a[1]);
  else if(op==='ssr')sar=number(r[d])&31;
  else if(op==='ssl')sar=32-(number(r[d])&31);
  else if(op==='srl')r[d]=shift(r[s],sar,false);
  else if(op==='sll')r[d]=shift(r[s],32-sar,true);
  else if(op==='and'||op==='xor')r[d]=bitOp(op,r[s],r[t]);
  else if(op==='add'||op==='sub')r[d]=variable(op+'('+key(r[s])+','+key(r[t])+')');
  else assert.fail('Unproved op '+op);
 }return{r,events,sar};}
function symbolicProof(a,b){for(let n=0;n<=31;n++){
  const x=symbolic(a,n),y=symbolic(b,n);assert.deepEqual(x.events,y.events,'Ordered entropy accesses');assert.equal(y.sar,x.sar);assert.equal(y.sar,n);
  for(let i=0;i<16;i++)if(i!==5&&i!==9)assert.deepEqual(y.r[i],x.r[i],'ABI/live a'+i);
  const expected=variable('R7').map((bit,i)=>i<n?bit:0);assert.deepEqual(y.r[2],expected,'All32 arbitrary input bits');
 }return{shift_counts:32,documented_api_bits:'0..25 inclusive',arbitrary_window32:true,arbitrary_state32:true,ordered_entropy_accesses_exact:true,callee_saved_exact:true,sar_exact:true,permitted_call0_scratch_differences:['a5','a9']};}
function emulate(rs,initial,memory){const r=initial.slice(),mem=new Map(memory),events=[],map=new Map(rs.map(x=>[x.address,x]));let pc=entry,steps=0,sar=7;
 while(true){assert.ok(++steps<200);const row=map.get(pc);assert.ok(row,'Invalid PC '+pc.toString(16));const [op,...a]=clean(row).replaceAll(',','').split(' '),d=+a[0]?.slice(1),s=+a[1]?.slice(1),t=+a[2]?.slice(1);pc+=row.bytes;
  if(op==='ret')break;
  if(op==='l32i'||op==='l8ui'){const p=(r[s]+(+a[2]))>>>0;assert.ok(mem.has(p),'Unexpected memory read '+p.toString(16));r[d]=mem.get(p);if(op==='l8ui')r[d]&=255;events.push({op,address:p,value:r[d]});}
  else if(op==='s32i'){const p=(r[s]+(+a[2]))>>>0;assert.equal(p%4,0);mem.set(p,r[d]);events.push({op,address:p,value:r[d]});}
  else if(op==='movi')r[d]=(+a[1])>>>0;
  else if(op==='add')r[d]=(r[s]+r[t])>>>0;
  else if(op==='sub')r[d]=(r[s]-r[t])>>>0;
  else if(op==='addi')r[d]=(r[s]+(+a[2]))>>>0;
  else if(op==='xor')r[d]=(r[s]^r[t])>>>0;
  else if(op==='and')r[d]=(r[s]&r[t])>>>0;
  else if(op==='or')r[d]=(r[s]|r[t])>>>0;
  else if(op==='ssr')sar=r[d]&31;
  else if(op==='ssl')sar=32-(r[d]&31);
  else if(op==='srl')r[d]=sar===32?0:r[s]>>>sar;
  else if(op==='sll')r[d]=sar===0?0:(r[s]<<(32-sar))>>>0;
  else if(op==='bgeu'||op==='bge'){if(op==='bgeu'?r[d]>=r[s]:(r[d]|0)>=(r[s]|0))pc=parseInt(a[2],16);}
  else assert.fail(op);
 }return{r,mem,events,sar};}
function numeric(a,b){let cases=0,refills=0,exhausted=0;const P=0x3ffe1000,B=0x3ffe2000,windows=[0,1,0x7fffffff,0x80000000,0xffffffff,0x55555555,0xaaaaaaaa,...Array.from({length:32},(_,i)=>(2**i)>>>0)];
 for(const n of[...Array(26).keys()])for(const available of[0,1,7,8,15,16,24,25,31,32])for(const storage of[0,1,2,4])for(const atEnd of[false,true])for(const window of windows){
  const r=Array.from({length:16},(_,i)=>Math.imul(i+7349,0x45d9f3b)>>>0);r[2]=P;r[3]=n;
  const mem=new Map([[P,B],[P+4,storage],[P+8,atEnd?storage:0],[P+12,window],[P+16,available],[P+20,0xfffffff0]]);for(let i=0;i<storage;i++)mem.set(B+i,(37+i*53)&255);
  const x=emulate(a,r,mem),y=emulate(b,r,mem);assert.deepEqual(y.events,x.events);assert.deepEqual(y.mem,x.mem);assert.equal(y.sar,x.sar);
  for(let i=0;i<16;i++)if(i!==5&&i!==9)assert.equal(y.r[i],x.r[i],'Full-function a'+i);
  cases++;if(available<n)refills++;if(available<n&&(atEnd||storage===0))exhausted++;
 }return{cases,refills,exhausted,scope:'Actual linked full function, including unchanged byte-refill/EOF and wrapping nbits_total; not a speed emulator.'};}
function prove(oldFn,newFn){const a=audit(oldFn,oldOps),b=audit(newFn,newOps);assert.deepEqual(a.filter(r=>r.address<address),b.filter(r=>r.address<address),'Refill prefix unchanged');return{symbolic:symbolicProof(inside(oldFn),inside(newFn)),numeric:numeric(a,b),reachable_tail_old:inside(oldFn).length,reachable_tail_new:inside(newFn).length,live_bytes:inside(newFn).reduce((n,r)=>n+r.bytes,0)};}
module.exports={address,bytes,entry,oldOps,newOps,inside,audit,symbolicProof,emulate,numeric,prove};
