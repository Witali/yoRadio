const test=require('node:test'),assert=require('node:assert/strict');
const r=require('../tools/esp8266_opus_asm/pvq_addx.cjs');
test('twenty actual ASM replacements preserve all registers, including aliases and wrapping',()=>{
 const {rows}=r.replacements(r.baseline());let seed=0x12345678,checks=0;
 const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 const edges=[0,1,0x3fffffff,0x40000000,0x7fffffff,0x80000000,0xfffffffc,0xffffffff];
 for(const p of rows)for(let n=0;n<10000;n++){
  const before=Array.from({length:16},()=>rnd());const d=+p.dst.slice(1),i=+p.index.slice(1),b=+p.base.slice(1);
  if(n<64){before[i]=edges[n%8];before[b]=edges[n>>3];}
  const old=before.slice(),next=before.slice();
  old[d]=(old[i]<<2)>>>0;old[d]=(old[d]+old[b])>>>0;
  next[d]=Number((BigInt(next[i])*4n+BigInt(next[b]))&0xffffffffn);
  assert.deepEqual(next,old);checks++;
 }
 console.log({instruction_pairs:20,register_state_checks:checks,scope:'local instruction equivalence, not board cycles'});
});
test('only selected function changes; no labels between operations, ABI/stack/table data unchanged',()=>{
 const base=r.baseline(),candidate=r.transform(base);
 assert.equal(candidate.replace(r.body(candidate),r.body(base)),base);
 assert.equal((r.body(candidate).match(/^\s*addx4 /gm)||[]).length,20);
 assert.throws(()=>r.transform(candidate));
 for(const [a,b]of [['slli a3, a4, 2','add a5, a3, a6'],['slli a3, a4, 2','add a3, a3, a3']])assert.equal(r.pair(a,b),null);
 const g=['slli a3, a4, 2','add a3, a6, a3','bne a3, a4, instruction:0'];
 assert.deepEqual(r.fuseGraph(g),{count:1,graph:['addx4 a3, a4, a6','bne a3, a4, instruction:0']});
  assert.equal(r.fuseGraph([...g,'j instruction:1']).count,0);
 require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-pvq-addx-asm');
});
test('GAS long-branch normalization preserves both edges, rejects entry into jump',()=>{
 const g=['bltu a2, a4, instruction:2','j instruction:3','add a2, a3, a4','ret '];
 assert.deepEqual(r.normalizeBranches(g),{collapsed:1,graph:['bgeu a2, a4, instruction:2','add a2, a3, a4','ret ']});
 assert.equal(r.normalizeBranches([...g,'j instruction:1']).collapsed,0);
 assert.equal(r.normalizeBranches(['bltu a2, a4, instruction:3',...g.slice(1)]).collapsed,0);
 for(const a of [0,1,0x7fffffff,0x80000000,0xffffffff])for(const b of [0,1,0x7fffffff,0x80000000,0xffffffff])assert.equal(a<b?2:3,a>=b?3:2);
});
