// Pointwise cached endpoint-cost proof, relative to accepted bits-fourth.
// Both outcomes and every instruction address remain identical; only one
// final duplicate read is removed when q!=0. This is not a timing proof.
const assert=require('node:assert/strict'),base=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),{tables}=require('./pulse_lookup.cjs');
const specs=[
 [0x4024e21f,3,'l8ui a9, a9, 0','l8ui a10, a9, 0'],
 [0x4024e222,3,'sub a9, a9, a8','sub a9, a10, a8'],
 [0x4024e228,2,'add a10, a2, a4','add a11, a2, a4'],
 [0x4024e22a,3,'l8ui a11, a10, 0','l8ui a11, a11, 0'],
 [0x4024e22d,2,'mov a10, a4','mov a10, a10'],
 [0x4024e238,2,'mov a10, a6','mov a11, a10'],
 [0x4024e23c,2,'add a10, a2, a10','mov a8, a11'],
 [0x4024e23e,3,'l8ui a8, a10, 0','or a10, a10, a10']
].map(([address,bytes,before,after])=>({address,bytes,before,after}));
const inside=a=>specs.some(p=>a>=p.address&&a<p.address+p.bytes);
const definitions=()=>'';
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);
 const rs=base.parsed(fn),map=new Map(rs.map(r=>[r.address,r]));
 for(const p of specs){const r=map.get(p.address);assert.ok(r);assert.equal(r.bytes,p.bytes);assert.equal(r.text,p.before);}
 for(const r of rs)if(/^b|^j$/.test(r.op)){
  const t=prior.target(r);for(const p of specs)assert.ok(t<=p.address||t>=p.address+p.bytes,'Instruction-interior entry');
  if((r.address<0x4024e21d||r.address>=0x4024e241)&&t>0x4024e21d&&t<0x4024e241)
   assert.ok(r.address===0x4024e3b6&&t===0x4024e235,'Bypassed endpoint values');
 }
 return specs.map(p=>({...p}));
}
function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r]));
 const t=tables(),stats={cases:0,zero:0,nonzero:0,removed_reads:0,old_steps:0,new_steps:0};
 const seen=new Set();
 for(const off of t.offsets)for(let budget=-64;budget<=16383;budget++){
  const cache=t.bits.slice(off,off+t.bits[off]+1),pointer=0x402d57fc+off;
  const r=Array.from({length:16},(_,i)=>Math.imul(budget+i+1,0x45d9f3b)>>>0);
  r[2]=pointer;r[6]=cache[0];r[7]=0;r[14]=budget>>>0;
  const x=base.execute(a,r,cache,pointer),y=base.execute(b,r,cache,pointer);
  assert.equal(x.pc,y.pc);assert.deepEqual(x.visited,y.visited,'Changed branch path or instruction address');
  for(let i=0;i<16;i++)if(i!==10&&i!==11)assert.equal(x.registers[i],y.registers[i],'Live register a'+i+' budget'+budget+' row'+off);
  const nonzero=x.pc===0x4024e241;assert.deepEqual(y.reads,nonzero?x.reads.slice(0,-1):x.reads,'Read order excluding final duplicate');
  if(nonzero){assert.equal(x.reads.at(-1),x.registers[4]);assert.ok(y.reads.includes(x.reads.at(-1)),'Not previously read');}
  y.visited.filter(inside).forEach(v=>seen.add(v));stats.cases++;stats[nonzero?'nonzero':'zero']++;
  stats.removed_reads+=x.reads.length-y.reads.length;stats.old_steps+=x.steps;stats.new_steps+=y.steps;
 }
 assert.deepEqual([...seen].sort((a,b)=>a-b),specs.map(p=>p.address));assert.equal(stats.old_steps,stats.new_steps);
 return {...stats,scope:'Full actual linked search/endpoint execution, all standard tables/budgets -64..16383; exact q/cost and input to unchanged budget loop, not CPU timing.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn);assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 const a=base.parsed(oldFn),b=base.parsed(newFn);assert.equal(a.length,b.length);
 for(let i=0;i<a.length;i++){
  assert.equal(a[i].address,b[i].address);assert.equal(a[i].bytes,b[i].bytes);
  const p=specs.find(p=>p.address===a[i].address);if(p)assert.equal(b[i].text,p.after);else assert.deepEqual(b[i],a[i]);
 }
 const liveness=base.stops.flatMap(pc=>[10,11].map(r=>base.deadUntilDefinition(newFn,pc,r)));
 return {numeric:numeric(oldFn,newFn),liveness,patches,frame_bytes:112,static_ram_delta:0,
  rule:'Upper and lower distances use the original immutable byte values. Same branches select same q; nonzero q publishes the already read selected cost. q=0 exits unchanged. a4/a8/context at the remaining_bits join are identical, and every instruction of its adjustment loop is untouched.',
  limitations:'No new bitrate cap, approximation or encoder support; inherited private decoder contract. All registers exact except independently proven-dead a10/a11. Register copies preserve instruction width, not a claimed instruction-count gain.',sar:'No changed instruction writes SAR or memory'};
}
module.exports={specs,inside,definitions,findPatches,numeric,prove};
