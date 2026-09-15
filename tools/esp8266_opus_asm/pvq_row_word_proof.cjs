// Exact row-length word access on the accepted a4-word linked image.
// Preserve a2 source, produce a6; no new stack/table/RAM or outside movement.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const first=require('./pvq_byte_word_proof.cjs'),middle=require('./pvq_a4_word_proof.cjs');
const base=require('./bits_fifth_proof.cjs'),prior=require('./partition_frozen_proof.cjs');
const {analyze}=require('./partition_decode.cjs'),{tables}=require('./pulse_lookup.cjs'),{root,sourceHash}=require('./export.cjs');
const helper=0x4024e3e8,helperBytes=27,sites=[0x4024db47];
const tableBase=first.tableBase,tableBytes=first.tableBytes;
const helperInside=a=>a>=helper&&a<helper+helperBytes;
const inside=a=>helperInside(a)||sites.some(s=>a>=s&&a<s+3);
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=> 'pvq_read_row = 0x'+helper.toString(16)+';';
function storageProof(fn){
 const file=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1/preflight.json');
 // Parent verifyPair recursively authenticates this original endpoint-cost
 // input and its immutable ctx.encode=0 call chain. It contains no new leaves.
 const origin=JSON.parse(fs.readFileSync(file)).functions.quant_partition;
 const p=prior.program(origin),analysis=analyze(p),dead=new Set(analysis.dead.map(d=>p.rows[d.index].address));
 const before=base.parsed(origin),rows=base.parsed(fn),storage=rows.filter(r=>helperInside(r.address));
 assert.equal(helper%4,0);assert.equal(storage[0]?.address,helper);
 assert.equal(storage.at(-1)?.address+storage.at(-1)?.bytes,helper+helperBytes);
 assert.deepEqual(storage,before.filter(r=>helperInside(r.address)),'Storage changed since original CFG proof');
 assert.ok(storage.every(r=>dead.has(r.address)),'Reachable encoder-only storage');
 for(let i=1;i<storage.length;i++)assert.equal(storage[i].address,storage[i-1].address+storage[i-1].bytes);
 const previous=rows.filter(r=>r.address<helper).at(-1);
 assert.equal(previous.address+previous.bytes,helper);assert.equal(previous.op,'j','Fallthrough into helper');
 assert.ok(!helperInside(prior.target(previous)));
 const incoming=[];
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)&&!helperInside(r.address)){
  const target=prior.target(r);if(!helperInside(target))continue;
  assert.equal(target,helper,'External entry into helper interior');
  assert.deepEqual(r,before.find(x=>x.address===r.address),'Changed incoming edge');
  assert.ok(dead.has(r.address),'Incoming edge is reachable in decoder');
  incoming.push({address:r.address,target,dead:true});
 }
 assert.equal(incoming.length,1);
 return {origin_sha256_lf:sourceHash(file),instructions:storage.length,incoming,helper,bytes:helperBytes,
  statement:'Unchanged original encoder-only region, dead for encode=0 with all audio-dependent branches retained; no fallthrough or interior entry.'};
}
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);storageProof(fn);
 const rows=base.parsed(fn);
 for(const pc of sites){const r=rows.find(r=>r.address===pc);assert.equal(r?.bytes,3);assert.equal(r.text,'l8ui a6, a2, 0');}
 return [{address:helper,bytes:helperBytes},...sites.map(address=>({address,bytes:3}))];
}
function helperSymbolic(fn){
 const rows=base.parsed(fn).filter(r=>helperInside(r.address)),expected=[
 'rsr.sar a11','ssa8l a2','srli a6, a2, 2','slli a6, a6, 2',
 'l32i a6, a6, 0','srl a6, a6','extui a6, a6, 0, 8','wsr.sar a11','ret.n'];
 assert.deepEqual(rows.map(r=>r.text.trim()),expected);
 assert.equal(rows[0].address,helper);assert.equal(rows.at(-1).address+rows.at(-1).bytes,helper+25);
 const records=[];
 for(let phase=0;phase<4;phase++){
  const r=Array.from({length:16},(_,i)=>'R'+i);r[2]=tableBase+phase;
  const initial=r.slice(),word=Array.from({length:32},(_,i)=>'W'+i),savedSar=Array.from({length:6},(_,i)=>'S'+i);
  let sar=savedSar,loads=0;
  for(const row of rows){const a=row.operands,d=reg(a[0]||'a0'),op=row.op;
   if(op==='rsr.sar')r[d]=sar;
   else if(op==='ssa8l'){assert.equal(typeof r[d],'number');sar=(r[d]&3)*8;}
   else if(op==='srli')r[d]=r[reg(a[1])]>>>Number(a[2]);
   else if(op==='slli')r[d]=(r[reg(a[1])]<<Number(a[2]))>>>0;
   else if(op==='l32i'){assert.equal(r[reg(a[1])]+Number(a[2]),tableBase);r[d]=word;loads++;}
   else if(op==='srl'){assert.ok(Array.isArray(r[reg(a[1])]));r[d]=r[reg(a[1])].slice(sar).concat(Array(sar).fill(0));}
   else if(op==='extui'){assert.ok(Array.isArray(r[reg(a[1])]));r[d]=r[reg(a[1])].slice(Number(a[2]),Number(a[2])+Number(a[3])).concat(Array(32-Number(a[3])).fill(0));}
   else if(op==='wsr.sar')sar=r[d];
   else if(op==='ret')assert.equal(r[0],initial[0]);
   else assert.fail(op);
  }
  assert.deepEqual(r[6],word.slice(phase*8,phase*8+8).concat(Array(24).fill(0)));assert.deepEqual(sar,savedSar);
  for(let i=0;i<16;i++)if(i!==6&&i!==11)assert.equal(r[i],initial[i]);assert.equal(loads,1);
  records.push({phase,output:r[6],source_preserved:r[2]===initial[2],sar,word_loads:loads});
 }
 return {records,instructions:rows.length,live_bytes:25,
  statement:'All32 word bits/four byte phases/arbitrary SAR; a2 source preserved, a6 unsigned result, only dead a11 otherwise changes.'};
}
let cachedBits;
function execute(fn,initial,cache,pointer,initialSar,options={}){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r])),data=cachedBits??(cachedBits=tables().bits);
 const r=initial.slice(),reads=[],wordReads=[],visited=[];let pc=options.start??sites[0],steps=0,sar=initialSar,returnPc=null;const stops=options.stops??base.stops;
 while(!stops.includes(pc)){
  const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<300);
  visited.push(pc);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){const added=sites.includes(pc),a4=middle.sites.includes(pc),dst=added?helper:a4?middle.helper:first.helper,rn=added?2:a4?4:10;assert.ok(added||a4||first.sites.includes(pc));assert.equal(prior.target(row),dst);assert.equal(returnPc,null);returnPc=next;
   const index=r[rn]-pointer;assert.ok(index>=0&&index<cache.length,'Caller byte outside row');reads.push(index);r[0]=next;next=dst;}
  else if(op==='ret'){assert.ok(first.helperInside(pc)||helperInside(pc));assert.equal(r[0],returnPc);next=r[0];returnPc=null;}
  else if(op==='j')next=prior.target(row);
  else if(op==='movi')r[reg(a[0])]=Number(a[1])>>>0;
  else if(op==='bnei'){if((r[reg(a[0])]|0)!==Number(a[1]))next=prior.target(row);}
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
   else if(op==='l32i'){assert.ok(first.helperInside(pc)||helperInside(pc));const address=r[s]+Number(a[2]),off=address-tableBase;
    assert.equal(address%4,0,'Unaligned word');assert.ok(off>=0&&off+4<=data.length,'Word outside complete table');
    wordReads.push(address);r[d]=(data[off]|data[off+1]<<8|data[off+2]<<16|data[off+3]<<24)>>>0;}
   else assert.fail('Unknown helper/search operation '+op);
  }pc=next;
 }assert.equal(returnPc,null);return {registers:r,pc,reads,wordReads,visited,steps,sar};
}

function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r])),t=tables();
 const result={byte_cases:0,prefix_cases:0,added_word_loads:0,old_steps:0,new_steps:0,prefix_stops:{}};
 const check=(r,cache,pointer,sar,options,kind)=>{
  const x=execute(a,r,cache,pointer,sar,options),y=execute(b,r,cache,pointer,sar,options);
  assert.equal(x.pc,y.pc);assert.equal(y.sar,sar);assert.equal(x.sar,sar);assert.deepEqual(x.reads,y.reads);
  for(let i=0;i<16;i++)if(i!==0&&i!==11)assert.equal(x.registers[i],y.registers[i],'Live a'+i+' '+kind);
  assert.deepEqual(x.visited,y.visited.filter(pc=>!helperInside(pc)),'Changed caller/old helper flow');
  assert.equal(y.wordReads.length-x.wordReads.length,1);
  result[kind+'_cases']++;result.added_word_loads++;result.old_steps+=x.steps;result.new_steps+=y.steps;
  if(kind==='prefix')result.prefix_stops[x.pc]=(result.prefix_stops[x.pc]||0)+1;
 };
 for(let off=0;off<t.bits.length;off++)for(let sar=0;sar<64;sar++){
  const r=Array.from({length:16},(_,i)=>Math.imul(off+sar+i+1,0x45d9f3b)>>>0);r[2]=tableBase+off;
  check(r,[t.bits[off]],r[2],sar,{stops:[sites[0]+3]},'byte');
 }
 const budgets=[...Array.from({length:577},(_,i)=>i-64),16383,-2147483648,2147483647];
 for(const off of t.offsets){
  const cache=t.bits.slice(off,off+t.bits[off]+1),pointer=tableBase+off;
  for(const budget of budgets)for(const lm of[-1,0,3])for(const n of[1,2,3,32]){
   const r=Array.from({length:16},(_,i)=>Math.imul(budget+i+n+lm+1,0x45d9f3b)>>>0);
   r[2]=pointer;r[3]=n;r[7]=0;r[9]=lm>>>0;r[14]=budget>>>0;
   check(r,cache,pointer,(budget^n^lm)&63,{stops:[0x4024db63,...base.stops]},'prefix');
  }
 }
 assert.equal(result.new_steps-result.old_steps,9*result.added_word_loads);
 assert.ok(result.prefix_stops[0x4024db63]>0);assert.ok(Object.keys(result.prefix_stops).length>=2);
 return {...result,scope:'Every392 table byte/all64 SAR values;23 standard rows,580 budgets including signed extremes,LM=-1/0/3,N=1/2/3/32,actual split/search branches. Parent additionally verifies exhaustive search; instruction counts exclude old exceptions, not timing.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)),'Outside new helper/call changed');
 for(const pc of sites){const r=b.find(r=>r.address===pc);assert.equal(r?.bytes,3);assert.equal(r.op,'call0');assert.equal(prior.target(r),helper);}
 const liveness=sites.flatMap(pc=>[0,11].map(r=>first.deadReg(oldFn,pc+3,r)));
 // Only a0/a11 may rely on call-clobber. Internal private leaves really
 // overwrite both, unlike a generic C call's larger scratch-register set.
 for(const proof of liveness)for(const end of proof.ends)if(end.kind==='abi-clobber'||end.kind==='call0-return-definition'){
  const call=a.find(r=>r.address===end.pc),target=prior.target(call);
  if(target>=oldFn.address&&target<oldFn.address+oldFn.bytes){
   assert.ok([first.helper,middle.helper].includes(target),'Unknown private leaf clobber');
   assert.equal(a.find(r=>r.address===target).text,'rsr.sar a11');
  }
 }
 const prefix=a.filter(r=>r.address<sites[0]);
 for(const [pc,text]of[[0x4024db12,'l32i a11, a8, 88'],[0x4024db1f,'l32i a11, a8, 92'],[0x4024db22,'l16si a2, a2, 0'],[0x4024db36,'s32i a0, a1, 108'],[0x4024db39,'add a2, a11, a2']])assert.equal(prefix.find(r=>r.address===pc)?.text,text);
 return {storage:storageProof(oldFn),helper:helperSymbolic(newFn),liveness,numeric:numeric(oldFn,newFn),patches,frame_bytes:112,static_ram_delta:0,pointer_prefix:prefix,
  rule:'Original static row/index and all decoder branch outcomes retained; preserved a2/return/SAR, no memory write or new allocation, authenticated parent proves private encode=0 for all valid packets.'};
}
module.exports={helper,helperBytes,sites,tableBase,tableBytes,helperInside,inside,definitions,storageProof,findPatches,helperSymbolic,execute,numeric,prove};
