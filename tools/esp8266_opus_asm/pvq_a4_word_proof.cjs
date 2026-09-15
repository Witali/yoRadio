// Two more word probes over the accepted byte-word image. Actual linked proof.
// No target timing claim; no change to the prior immutable recipe.
const assert=require('node:assert/strict');
const first=require('./pvq_byte_word_proof.cjs'),base=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),{tables}=require('./pulse_lookup.cjs');
const helper=0x4024de08,helperBytes=25,sites=[0x4024db52,0x4024e1ad];
const tableBase=first.tableBase,tableBytes=first.tableBytes;
const helperInside=a=>a>=helper&&a<helper+helperBytes;
const inside=a=>helperInside(a)||sites.some(s=>a>=s&&a<s+3);
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=> 'pvq_read_a4 = 0x'+helper.toString(16)+';';
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);
 const rows=base.parsed(fn),h=first.helperSymbolic(fn);
 assert.equal(h.live_bytes,25);assert.equal(first.helper+28,helper);
 assert.ok(first.helper+h.live_bytes<helper && helper+helperBytes<=first.helper+first.helperBytes);
 // The original helper reaches RET before this zero padding. Its private
 // encode=0 storage and caller contract are independently revalidated by parent.
 const earlier=rows.filter(r=>r.address<helper).at(-1);
 assert.equal(earlier.op,'ret');assert.equal(earlier.address+earlier.bytes,first.helper+h.live_bytes);
 assert.ok(!rows.some(r=>helperInside(r.address)),'Existing instruction in padding');
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)){
  const t=prior.target(r);assert.ok(!helperInside(t),'External entry into new helper storage');
 }
 for(const pc of sites){const r=rows.find(r=>r.address===pc);assert.equal(r?.bytes,3);assert.equal(r.text,'l8ui a4, a4, 0');}
 return [{address:helper,bytes:helperBytes},...sites.map(address=>({address,bytes:3}))];
}
function helperSymbolic(oldFn,newFn){
 const old=first.helperSymbolic(oldFn),a=base.parsed(oldFn).filter(r=>first.helperInside(r.address)),b=base.parsed(newFn).filter(r=>helperInside(r.address));
 assert.equal(b.length,9);assert.equal(b[0].address,helper);assert.equal(b.at(-1).address+b.at(-1).bytes,helper+helperBytes);
 // Bijective a4<->a10 alpha-renaming of the already symbolic-proved leaf.
 // Original leaf does not mention a4; new leaf must not mention a10.
 assert.ok(a.every(r=>!r.operands.includes('a4')));assert.ok(b.every(r=>!r.operands.includes('a10')));
 assert.deepEqual(b.map(r=>r.text.replace(/\ba4\b/g,'a10')),a.map(r=>r.text));
 assert.deepEqual(b.map(r=>r.bytes),a.map(r=>r.bytes));
 return {instructions:9,live_bytes:25,renaming:{a10:'a4',a4:'a10'},reference:old,
  statement:'All32 word bits,4 byte phases, arbitrary SAR; exactly the proven leaf with a4/a10 swapped, only a4 and dead a11 change.'};
}
let cachedBits;
function execute(fn,initial,cache,pointer,initialSar,options={}){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r])),data=cachedBits??(cachedBits=tables().bits);
 const r=initial.slice(),reads=[],wordReads=[],visited=[];let pc=options.start??base.start,steps=0,sar=initialSar,returnPc=null;const stops=options.stops??base.stops;
 while(!stops.includes(pc)){
  const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<260);
  visited.push(pc);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){const added=sites.includes(pc),dst=added?helper:first.helper,rn=added?4:10;assert.ok(added||first.sites.includes(pc));assert.equal(prior.target(row),dst);assert.equal(returnPc,null);returnPc=next;
   const index=r[rn]-pointer;assert.ok(index>=0&&index<cache.length,'Caller byte outside row');reads.push(index);r[0]=next;next=dst;}
  else if(op==='ret'){assert.ok(first.helperInside(pc));assert.equal(r[0],returnPc);next=r[0];returnPc=null;}
  else if(op==='j')next=prior.target(row);
  else if(op==='movi')r[reg(a[0])]=Number(a[1])>>>0;
  else if(op==='beqz'){if(r[reg(a[0])]===0)next=prior.target(row);}
  else if(op==='blt'||op==='bge'){const lt=(r[reg(a[0])]|0)<(r[reg(a[1])]|0);if(op==='blt'?lt:!lt)next=prior.target(row);}
  else if(op==='bgei'){if((r[reg(a[0])]|0)>=Number(a[1]))next=prior.target(row);}
  else if(op==='rsr.sar')r[reg(a[0])]=sar;
  else if(op==='wsr.sar')sar=r[reg(a[0])]&63;
  else if(op==='ssa8l')sar=(r[reg(a[0])]&3)*8;
  else {
   const d=reg(a[0]),s=reg(a[1]);
   if(op==='mov')r[d]=r[s];
   else if(op==='add')r[d]=(r[s]+r[reg(a[2])])>>>0;
   else if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='sub')r[d]=(r[s]-r[reg(a[2])])>>>0;
   else if(op==='or')r[d]=(r[s]|r[reg(a[2])])>>>0;
   else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='srli')r[d]=r[s]>>>Number(a[2]);
   else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;
   else if(op==='srl'){assert.ok(sar<32);r[d]=r[s]>>>sar;}
   else if(op==='extui'){assert.equal(Number(a[3]),8);r[d]=(r[s]>>>Number(a[2]))&255;}
   else if(op==='l8ui'){const address=(r[s]+Number(a[2]))>>>0,index=address-pointer;assert.ok(index>=0&&index<cache.length,'Out-of-row read');reads.push(index);r[d]=cache[index];}
   else if(op==='l32i'){assert.ok(first.helperInside(pc));const address=r[s]+Number(a[2]),off=address-tableBase;
    assert.equal(address%4,0,'Unaligned word');assert.ok(off>=0&&off+4<=data.length,'Word outside complete table');
    wordReads.push(address);r[d]=(data[off]|data[off+1]<<8|data[off+2]<<16|data[off+3]<<24)>>>0;}
   else assert.fail('Unknown helper/search operation '+op);
  }pc=next;
 }assert.equal(returnPc,null);return {registers:r,pc,reads,wordReads,visited,steps,sar};
}

function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r])),t=tables();
 const result={search_cases:0,upper_cases:0,added_word_loads:0,old_steps:0,new_steps:0,upper_stops:{}};
 const check=(r,cache,pointer,sar,options,kind)=>{
  const x=execute(a,r,cache,pointer,sar,options),y=execute(b,r,cache,pointer,sar,options);
  assert.equal(x.pc,y.pc);assert.equal(y.sar,sar);assert.equal(x.sar,sar);assert.deepEqual(x.reads,y.reads);
  for(let i=0;i<16;i++)if(i!==0&&i!==11)assert.equal(x.registers[i],y.registers[i],'Live a'+i+' '+kind);
  assert.deepEqual(x.visited,y.visited.filter(pc=>!helperInside(pc)),'Changed caller/old helper flow');
  assert.equal(y.wordReads.length-x.wordReads.length,1);
  result[kind+'_cases']++;result.added_word_loads++;result.old_steps+=x.steps;result.new_steps+=y.steps;
  if(kind==='upper')result.upper_stops[x.pc]=(result.upper_stops[x.pc]||0)+1;
 };
 for(const off of t.offsets){
  const cache=t.bits.slice(off,off+t.bits[off]+1),pointer=tableBase+off;
  for(let budget=-64;budget<=16383;budget++){
   const r=Array.from({length:16},(_,i)=>Math.imul(budget+i+1,0x45d9f3b)>>>0);r[2]=pointer;r[6]=cache[0];r[7]=0;r[14]=budget>>>0;
   check(r,cache,pointer,(budget^0x35)&63,{},'search');
  }
  const budgets=[...Array.from({length:577},(_,i)=>i-64),-2147483648,2147483647];
  for(const budget of budgets)for(const n of[0,1,2,3,32,1024]){
   const r=Array.from({length:16},(_,i)=>Math.imul(budget+i+n+1,0x45d9f3b)>>>0);r[2]=pointer;r[6]=cache[0];r[3]=n;r[14]=budget>>>0;
   check(r,cache,pointer,(budget^n)&63,{start:0x4024db50,stops:[0x4024db63,base.start]},'upper');
  }
 }
 assert.equal(result.new_steps-result.old_steps,9*result.added_word_loads);
 assert.equal(Object.keys(result.upper_stops).length,2);
 return {...result,scope:'Actual linked calls/helpers: all standard rows/budgets -64..16383 search, plus all upper thresholds/N branches and signed extremes. Counts exclude old exceptions; not timing.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)),'Outside new helper/calls changed');
 for(const pc of sites){const r=b.find(r=>r.address===pc);assert.equal(r?.bytes,3);assert.equal(r.op,'call0');assert.equal(prior.target(r),helper);}
 const liveness=sites.flatMap(pc=>[0,11].map(r=>first.deadReg(oldFn,pc+3,r)));
 const prefix=a.filter(r=>r.address<0x4024db50);
 // Exact unchanged pointer path: mode cache.index at+88, bits at+92,
 // signed row offset and cache[0]; no source/branch/header change.
 for(const [pc,text]of[[0x4024db12,'l32i a11, a8, 88'],[0x4024db1f,'l32i a11, a8, 92'],[0x4024db22,'l16si a2, a2, 0'],[0x4024db39,'add a2, a11, a2'],[0x4024db47,'l8ui a6, a2, 0']])assert.equal(prefix.find(r=>r.address===pc)?.text,text);
 return {helper:helperSymbolic(oldFn,newFn),liveness,numeric:numeric(oldFn,newFn),patches,frame_bytes:112,static_ram_delta:0,
  pointer_prefix:prefix,rule:'Valid original static-table addresses, both split outcomes/recursion preserved; original helper/C fallback unchanged; parent verifies encode=0 and full table/index image.'};
}
module.exports={helper,helperBytes,sites,tableBase,tableBytes,helperInside,inside,definitions,findPatches,helperSymbolic,execute,numeric,prove};
