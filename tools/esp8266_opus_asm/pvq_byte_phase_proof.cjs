// Compositional proof of the actual linked leaf, all word bits and addresses.
// A helper replacement does not alter the already-proven parent PVQ search.
const assert=require('node:assert/strict');
const parser=require('./bits_fifth_proof.cjs'),prior=require('./partition_frozen_proof.cjs');
const old=require('./pvq_byte_word_proof.cjs'),storage=require('./pvq_logn_word_proof.cjs');
const helper=storage.helper,helperBytes=storage.helperBytes;
const sites=[...old.sites,0x4024e21f].sort((a,b)=>a-b);
const helperInside=a=>a>=helper&&a<helper+helperBytes;
// The original 57-byte storage now also contains the accepted a4 helper.
// Only the a10 leaf's 25 live bytes become unreachable; keep a4 untouched.
const oldLeafInside=a=>a>=old.helper&&a<old.helper+25;
const inside=a=>helperInside(a)||oldLeafInside(a)||sites.includes(a);
const definitions=()=>`pvq_byte_phase = 0x${helper.toString(16)};`;
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);storage.storageProof(fn);
 const rows=parser.parsed(fn);
 const calls=rows.filter(r=>r.op==='call0'&&prior.target(r)===old.helper);
 assert.deepEqual(calls.map(r=>r.address).sort((a,b)=>a-b),sites,'Exact old helper caller inventory');
 for(const r of calls)assert.equal(r.bytes,3);
 // No hidden jump to the old leaf or its interior may be ignored.
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)&&!oldLeafInside(r.address)&&oldLeafInside(prior.target(r)))
  assert.ok(sites.includes(r.address)&&r.op==='call0'&&prior.target(r)===old.helper,'Unexpected old helper entry');
 const oldLeaf={...fn,disassembly:fn.disassembly.split('\n').filter(line=>{
  const m=line.match(/^\s*([0-9a-f]+):/);return m&&oldLeafInside(parseInt(m[1],16));
 }).join('\n')};
 assert.equal(old.helperSymbolic(oldLeaf).live_bytes,25);
 return[{address:helper,bytes:helperBytes},...sites.map(address=>({address,bytes:3}))];
}
function symbolic(fn){
 const rows=parser.parsed(fn).filter(r=>helperInside(r.address)),map=new Map(rows.map(r=>[r.address,r]));
 assert.equal(rows.length,14);assert.equal(rows[0].address,helper);
 assert.equal(rows.at(-1).address+rows.at(-1).bytes-helper,37);
 const records=[],allVisited=new Set();
 // Enumerate every address in the complete parent pulse table. Each loaded
 // word is symbolic, so this includes every possible 32-bit table content.
 for(let offset=0;offset<old.tableBytes;offset++){
  const phase=offset&3,address=old.tableBase+offset,aligned=address-phase;
  const r=Array.from({length:16},(_,i)=>'R'+i),word=Array.from({length:32},(_,i)=>'W'+i);
  const initial=r.slice();r[10]=address;let pc=helper,steps=0,loads=0;
  while(true){
   const row=map.get(pc);assert.ok(row,'Invalid helper PC');assert.ok(++steps<=7);allVisited.add(pc);
   const a=row.operands,op=row.op;let next=pc+row.bytes;
   if(op==='ret'){assert.equal(r[0],initial[0]);break;}
   if(op==='bbci'){
    const value=r[reg(a[0])],bit=Number(a[1]);assert.equal(typeof value,'number');assert.ok(bit===0||bit===1);
    if(!(value&(1<<bit)))next=prior.target(row);
   }else{
    const d=reg(a[0]),s=reg(a[1]);assert.ok(d===10||d===11,'Unexpected live register write');
    if(op==='extui'){
     const shift=Number(a[2]),width=Number(a[3]);assert.ok(shift>=0&&shift+width<=32&&width>0);
     if(Array.isArray(r[s]))r[d]=r[s].slice(shift,shift+width).concat(Array(32-width).fill(0));
     else{assert.equal(shift,0);assert.equal(width,2);r[d]=r[s]&3;}
    }else if(op==='sub'){
     assert.equal(typeof r[s],'number');assert.equal(typeof r[reg(a[2])],'number');r[d]=(r[s]-r[reg(a[2])])>>>0;
    }else if(op==='l32i'){
     assert.equal(r[s]+Number(a[2]),aligned);assert.equal(aligned%4,0);
     assert.ok(aligned>=old.tableBase&&aligned+4<=old.tableBase+old.tableBytes);
     r[d]=word;loads++;
    }else assert.fail('Unsupported helper instruction '+op);
   }
   pc=next;
  }
  assert.equal(steps,7);assert.equal(loads,1);
  assert.deepEqual(r[10],word.slice(phase*8,phase*8+8).concat(Array(24).fill(0)));
  for(let i=0;i<16;i++)if(i!==10&&i!==11)assert.equal(r[i],initial[i]);
  if(offset<4)records.push({phase,steps,loads,result:r[10]});
 }
 assert.equal(allVisited.size,rows.length,'Untested helper instruction');
 return{records,addresses:old.tableBytes,live_bytes:37,executed_per_phase:7,old_executed:9,
  sar:'untouched: no SAR instruction allowed',scope:'All bits of every aligned table word; all392 valid byte addresses; same one word read; no store or other GPR change except dead a11.'};
}
function prove(before,after){
 const patches=findPatches(before),a=parser.parsed(before),b=parser.parsed(after);
 assert.equal(before.address,after.address);assert.equal(before.bytes,after.bytes);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)),'Outside helper/call sites changed');
 assert.equal(b.filter(r=>oldLeafInside(r.address)).length,0,'Old helper remains reachable');
 for(const pc of sites){const r=b.find(r=>r.address===pc);assert.equal(r?.op,'call0');assert.equal(r.bytes,3);assert.equal(prior.target(r),helper);}
 for(const r of b)if(/^b|^j$|^call0$/.test(r.op)&&!helperInside(r.address)&&helperInside(prior.target(r)))
  assert.ok(sites.includes(r.address)&&r.op==='call0'&&prior.target(r)===helper,'Unexpected phase helper entry');
 // CALL0 already exists at exactly the same caller address: old/new a0
 // return values are identical. Only a11 changes from saved SAR to phase.
 const liveness=sites.map(pc=>old.deadReg(before,pc+3,11));
 return{storage:storage.storageProof(before),helper:symbolic(after),liveness,patches,frame_bytes:112,static_ram_delta:0,
  rule:'Exact leaf substitution at every old a10 CALL0. Original old helper bytes are authenticated separately and not changed. Caller branches, addresses, tables and C fallback are unchanged.'};
}
module.exports={helper,helperBytes,sites,inside,helperInside,definitions,findPatches,symbolic,prove,storageBytesProof:storage.storageBytesProof};
