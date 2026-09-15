// Prove the actual linked fourth-step shortcut relative to accepted bits-fifth.
// Reuse its interpreter/liveness proof, not its source-level timing estimates.
const assert=require('node:assert/strict');
const base=require('./bits_fifth_proof.cjs'),prior=require('./partition_frozen_proof.cjs');
const {tables}=require('./pulse_lookup.cjs');
const main=0x4024e1f5,common=base.common,spans=[{address:main,bytes:common-main}];
const inside=a=>a>=main&&a<common;
const definitions=base.definitions;
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);
 const rs=base.parsed(fn);
 assert.equal(rs.find(r=>r.address===main).text,'add a9, a6, a4');
 assert.equal(rs.find(r=>r.address===base.main).text,'sub a10, a6, a9');
 for(const r of rs)if(/^b|^j$/.test(r.op)&&!inside(r.address)){
  const t=prior.target(r);assert.ok(t<=main||t>=common,'Interior external entry');
 }
 return spans.map(s=>({...s}));
}
function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r]));
 const t=tables(),stats={cases:0,fourth_shortcuts:0,retained_fifth:0,old_steps:0,new_steps:0,step_differences:{},stops:{}};
 const seen=new Set();
 for(const off of t.offsets)for(let budget=-64;budget<=16383;budget++){
  const cache=t.bits.slice(off,off+t.bits[off]+1),pointer=0x402d57fc+off;
  const r=Array.from({length:16},(_,i)=>Math.imul(budget+i+1,0x45d9f3b)>>>0);
  r[2]=pointer;r[6]=cache[0];r[7]=0;r[14]=budget>>>0;
  const x=base.execute(a,r,cache,pointer),y=base.execute(b,r,cache,pointer);
  assert.equal(x.pc,y.pc,'Changed q=0 exit');
  for(let i=0;i<16;i++)if(i!==10&&i!==11)assert.equal(x.registers[i],y.registers[i],'Live register a'+i+' budget'+budget+' row'+off);
  assert.ok(y.reads.every(v=>x.reads.includes(v)),'New table access');
  const early=!y.visited.includes(main+6);
  assert.ok(early?y.reads.length<x.reads.length:y.reads.length===x.reads.length,'Unexpected probe count');
  y.visited.filter(inside).forEach(v=>seen.add(v));stats.cases++;stats[early?'fourth_shortcuts':'retained_fifth']++;
  stats.old_steps+=x.steps;stats.new_steps+=y.steps;const d=x.steps-y.steps;
  stats.step_differences[d]=(stats.step_differences[d]||0)+1;stats.stops[x.pc]=(stats.stops[x.pc]||0)+1;
 }
 assert.deepEqual([...seen].sort((a,b)=>a-b),base.parsed(newFn).filter(r=>inside(r.address)).map(r=>r.address).sort((a,b)=>a-b),'Uncovered reachable instruction');
 return {...stats,scope:'Actual linked instructions, full search and nearest-endpoint joins; all standard tables/budgets -64..16383, not CPU timing.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn);assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 const a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)));
 const changed=b.filter(r=>inside(r.address));
 assert.ok(changed.every(r=>!/^s(?:8|16|32)i$|^ssr$|^ssl$|^call|^ret/.test(r.op)),'Side effect in replacement');
 assert.equal(changed[0].text,'sub a10, a4, a6');
 assert.equal(changed[1].op,'bgei');assert.equal(changed[1].operands[1],'-1');assert.equal(prior.target(changed[1]),common);
 assert.equal(changed.filter(r=>r.op==='bgei').length,2);
 const liveness=base.stops.flatMap(pc=>[10,11].map(r=>base.deadUntilDefinition(newFn,pc,r)));
 return {numeric:numeric(oldFn,newFn),liveness,frame_bytes:112,static_ram_delta:0,patches,
  rule:'For hi-lo<=1 any remaining bisection leaves the same nearest endpoint: either bounds stay or collapse to hi when cache[hi]<value. lo=0 retains sentinel -1. Otherwise execute accepted fifth/sixth logic. Bounded indices make signed lo-hi safe.',
  limitations:'Immutable valid Opus cache rows, inherited decoder-private encode=0 contract; all registers exact except proven-dead a10/a11. No new bitrate cap or approximation.',sar:'Changed instructions do not write SAR'};
}
module.exports={main,common,spans,inside,definitions,findPatches,numeric,prove};
