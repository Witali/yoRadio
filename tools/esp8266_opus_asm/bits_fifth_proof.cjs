// Exact linked search execution and decoder-private control-flow audit.
// PCM equivalence is separate from a speed claim; no fixture bitrate cap.
const assert=require('node:assert/strict'),base=require('./frozen_reloads.cjs');
const prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs');
const {tables}=require('./pulse_lookup.cjs');
const start=0x4024e1a6,main=0x4024e209,common=0x4024e21d,slow=0x4024e27b,slowEnd=0x4024e297;
const stops=[0x4024e241,0x4024e2aa];
const spans=[{address:main,bytes:common-main},{address:slow,bytes:slowEnd-slow}];
const inside=a=>spans.some(p=>a>=p.address&&a<p.address+p.bytes);
const definitions=()=>`sixth_probe = 0x${slow.toString(16)};\nnearest_endpoint = 0x${common.toString(16)};`;
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
function parsed(fn){return base.rows(fn.disassembly).map(r=>({...r,op:r.op.replace(/\.n$/,''),operands:r.args.replace(/\s+<[^>]*>$/,'').split(/,\s*/)}));}
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);
 const p=prior.program(fn),a=analyze(p);assert.equal(a.branches.length,3);
 const dead=new Set(a.dead.map(d=>p.rows[d.index].address));
 for(const r of p.rows.filter(r=>r.address>=slow&&r.address<slowEnd))assert.ok(dead.has(r.address),'Not encoder-only storage');
 assert.equal(p.rows.find(r=>r.address===0x4024e278).text,'beqz a7, 4024e297 <quant_partition+1947>');
 assert.ok(a.branches.some(b=>p.rows[b.index].address===0x4024e278&&b.taken));
 for(const s of spans)for(const r of p.rows)if(/^b|^j$/.test(r.op)&&!inside(r.address)){
  const t=prior.target(r);assert.ok(t<=s.address||t>=s.address+s.bytes,'Interior external entry');
 }
 return spans.map(s=>({...s}));
}
// Prove each permitted scratch-register difference unobservable along ALL
// successors from the join, not just the fixture's actual continuation.
function deadUntilDefinition(fn,pc,rn){
 const rs=parsed(fn),map=new Map(rs.map(r=>[r.address,r])),seen=new Set(),queue=[pc],ends=[];
 const destOps=new Set('addi addmi add sub mull mul16s slli srai srli sll sra srl and or xor neg extui nsau l32r movi mov l32i l16si l16ui l8ui'.split(' '));
 while(queue.length){const at=queue.pop();if(seen.has(at))continue;seen.add(at);const r=map.get(at);assert.ok(r,'Unresolved liveness edge');
  const a=r.operands,name='a'+rn;
  if(/^call/.test(r.op)){assert.ok(rn>=8&&rn<=11);assert.ok(!a.includes(name),'Indirect call reads scratch');ends.push({pc:at,kind:'call-clobber'});continue;}
  if(r.op==='ret'){assert.ok(rn===10||rn===11);ends.push({pc:at,kind:'caller-saved-return'});continue;}
  let reads=a;
  if(destOps.has(r.op))reads=a.slice(1);
  else if(/^mov(?:ltz|gez|eqz|nez)$/.test(r.op))reads=a; // conditional destination can survive
  else assert.ok(/^b|^j$|^s(?:8|16|32)i$|^ssr$|^ssl$/.test(r.op),'Unknown liveness opcode '+r.op);
  assert.ok(!reads.includes(name),'Live '+name+' read at '+at.toString(16));
  if(destOps.has(r.op)&&a[0]===name){ends.push({pc:at,kind:'definition'});continue;}
  if(r.op==='j')queue.push(prior.target(r));else if(/^b/.test(r.op)){queue.push(prior.target(r),at+r.bytes);}else queue.push(at+r.bytes);
 }
 return {register:rn,start:pc,visited:[...seen].sort((a,b)=>a-b),ends};
}
function execute(rows,initial,cache,pointer){
 const map=rows instanceof Map?rows:new Map(rows.map(r=>[r.address,r]));
 const r=initial.slice(),reads=[],visited=[];let pc=start,steps=0;
 while(!stops.includes(pc)){
  const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<150);
  visited.push(pc);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='j')next=parseInt(a[0],16);
  else if(op==='movi')r[reg(a[0])]=Number(a[1])>>>0;
  else if(op==='beqz'){if(r[reg(a[0])]===0)next=parseInt(a[1],16);}
  else if(op==='blt'||op==='bge'){const lt=(r[reg(a[0])]|0)<(r[reg(a[1])]|0);if(op==='blt'?lt:!lt)next=parseInt(a[2],16);}
  else if(op==='bgei'){if((r[reg(a[0])]|0)>=Number(a[1]))next=parseInt(a[2],16);}
  else {
   const d=reg(a[0]),s=reg(a[1]);
   if(op==='mov')r[d]=r[s];
   else if(op==='add')r[d]=(r[s]+r[reg(a[2])])>>>0;
   else if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='sub')r[d]=(r[s]-r[reg(a[2])])>>>0;
   else if(op==='or')r[d]=(r[s]|r[reg(a[2])])>>>0;
   else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='movi')assert.fail('MOVI must be handled separately');
   else if(op==='l8ui'){const address=(r[s]+Number(a[2]))>>>0,index=(address-pointer)>>>0;assert.ok(index<cache.length,'Out-of-row read');reads.push(index);r[d]=cache[index];}
   else assert.fail('Unexpected search instruction '+op);
  }
  pc=next;
 }
 return {registers:r,pc,reads,visited,steps};
}
function numeric(oldFn,newFn){
 const a=new Map(parsed(oldFn).map(r=>[r.address,r])),b=new Map(parsed(newFn).map(r=>[r.address,r]));
 const t=tables(),stats={cases:0,shortcuts:0,slow:0,old_steps:0,new_steps:0,step_differences:{},stops:{}};
 const seen=new Set();
 // Byte costs partition all ordinary budgets at -1..257. Include larger
 // budgets/negative sentinels separately; no runtime limit is introduced.
 for(const off of t.offsets)for(let budget=-64;budget<=16383;budget++){
  const cache=t.bits.slice(off,off+t.bits[off]+1),pointer=0x402d57fc+off;
  const r=Array.from({length:16},(_,i)=>Math.imul(budget+i+1,0x45d9f3b)>>>0);
  r[2]=pointer;r[6]=cache[0];r[7]=0;r[14]=budget>>>0;
  const x=execute(a,r,cache,pointer),y=execute(b,r,cache,pointer);
  assert.equal(x.pc,y.pc,'Changed q=0 exit');
  for(let i=0;i<16;i++)if(i!==10&&i!==11)assert.equal(x.registers[i],y.registers[i],'Live register a'+i+' budget'+budget+' row'+off);
  assert.ok(y.reads.every(v=>x.reads.includes(v)),'New data access');
  const usedSlow=y.visited.includes(slow);assert.ok(usedSlow?x.reads.length===y.reads.length:x.reads.length>y.reads.length);
  y.visited.filter(inside).forEach(v=>seen.add(v));stats.cases++;stats[usedSlow?'slow':'shortcuts']++;
  stats.old_steps+=x.steps;stats.new_steps+=y.steps;const d=x.steps-y.steps;
  stats.step_differences[d]=(stats.step_differences[d]||0)+1;stats.stops[x.pc]=(stats.stops[x.pc]||0)+1;
 }
 const live=parsed(newFn).filter(r=>inside(r.address)).map(r=>r.address).sort((a,b)=>a-b);
 assert.deepEqual([...seen].sort((a,b)=>a-b),live,'Uncovered reachable patch instruction');
 return {...stats,scope:'Actual linked instruction execution on all standard tables/budgets -64..16383, including complete first-five prefix and unchanged nearest-endpoint tail. No target timing claim.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn);assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 const a=parsed(oldFn),b=parsed(newFn);assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)));
 const newInside=b.filter(r=>inside(r.address));assert.ok(newInside.every(r=>!/^s(?:8|16|32)i$|^ssr$|^ssl$|^call|^ret/.test(r.op)),'Side effect in replacement');
 assert.equal(newInside.find(r=>r.address===main).text,'sub a10, a6, a9');
 assert.equal(newInside.filter(r=>r.op==='bgei').length,1);
 const liveness=stops.flatMap(pc=>[10,11].map(r=>deadUntilDefinition(newFn,pc,r)));
 return {numeric:numeric(oldFn,newFn),liveness,frame_bytes:112,static_ram_delta:0,patches,
  rule:'For hi=lo result is identical. For hi=lo+1, sixth mid=hi. If cache[hi]>=value endpoints stay unchanged; otherwise both sixth probe and final distance rule select hi. Other gaps execute original sixth probe. lo=0 retains cost sentinel -1.',
  limitations:'Result rule applies to valid immutable Opus cache rows and decoder-private encode=0 contract. Liveness proves a10/a11 differences dead on all continuations; all other registers identical at join. No approximation, encoder API or bitrate cap.',sar:'Changed instructions do not write SAR'};
}
module.exports={start,main,common,slow,slowEnd,stops,spans,inside,definitions,parsed,findPatches,deadUntilDefinition,execute,numeric,prove};
