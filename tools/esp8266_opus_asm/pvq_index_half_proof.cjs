// Specialize signed16 flash extraction for the two possible address phases.
// Parent is the immutable accepted index-word v2. New overlay restores the
// original load/store order without changing stack, SAR or the original a0.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,sourceHash}=require('./export.cjs'),base=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),word=require('./pvq_index_word_proof.cjs');
const frozen=require('./frozen_reloads.cjs'),{tables}=require('./pulse_lookup.cjs');
const {helper,helperBytes,site,late,continuation,indexBase,indexBytes,tableBase,tableBytes,helperInside,inside}=word;
const resume=site+3,liveBytes=25;
const parentFile=path.join(root,'firmware/development/esp8266-opus-pvq-index-word-candidate-v2/preflight.json');
const parentProof=()=>JSON.parse(fs.readFileSync(parentFile));
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=>`pvq_index_half = 0x${helper.toString(16)};\npvq_index_continue = 0x${resume.toString(16)};`;
function storageProof(fn){
 const p=parentProof();assert.deepEqual(fn,p.actual_functions.quant_partition);
 // This slot was already authenticated/proven encoder-only by the parent.
 // Do not pretend the parent's live helper is still dead original code.
 const origin=word.storageProof(p.functions.quant_partition);
 assert.deepEqual(word.helperSymbolic(fn),p.semantic.search.helper);
 return{origin,parent_sha256_lf:sourceHash(parentFile),replaces:'accepted signed-index helper at the only redirected decoder entry',live_bytes:liveBytes};
}
function storageBytesProof(elf){
 const p=parentProof(),patch=p.patches.find(x=>x.address===helper);
 assert.equal(patch.bytes,helperBytes);const off=frozen.offsetAt(elf,helper,helperBytes);
 assert.equal(elf.subarray(off,off+helperBytes).toString('hex'),patch.after_hex,'Parent helper storage changed');
 return{parent_sha256_lf:sourceHash(parentFile),address:helper,bytes:helperBytes,hex:patch.after_hex};
}
function findPatches(fn){
 storageProof(fn);assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);
 const rows=base.parsed(fn);assert.equal(rows.find(r=>r.address===site)?.text,'s32i a0, a1, 108');
 const jump=rows.find(r=>r.address===late);assert.equal(jump?.op,'j');assert.equal(prior.target(jump),helper);
 for(const r of rows)if(!helperInside(r.address)&&/^b|^j$|^call0$/.test(r.op)){
  const t=prior.target(r);if(helperInside(t)){assert.equal(r.address,late);assert.equal(t,helper);}
 }
 return[{address:helper,bytes:helperBytes},{address:site,bytes:3},{address:late,bytes:3}];
}
function helperSymbolic(fn){
 const rows=base.parsed(fn).filter(r=>helperInside(r.address));
 assert.equal(rows.length,9);assert.equal(rows[0].op,'bbci');assert.deepEqual(rows[0].operands,['a2','1',(helper+14).toString(16)]);
 assert.deepEqual(rows.slice(1,4).map(r=>r.text),['addi a2, a2, -2','l32i a2, a2, 0','srai a2, a2, 16']);
 assert.deepEqual(rows.slice(5,8).map(r=>r.text),['l32i a2, a2, 0','slli a2, a2, 16','srai a2, a2, 16']);
 for(const row of[rows[4],rows[8]]){assert.equal(row.op,'j');assert.equal(prior.target(row),resume);}
 assert.equal(rows[0].address,helper);assert.equal(rows[5].address,helper+14);
 assert.equal(rows[8].address+rows[8].bytes,helper+liveBytes);
 const records=[];
 for(const phase of[0,2]){
  const bits=Array.from({length:32},(_,i)=>'W'+i),initial=Array.from({length:16},(_,i)=>'R'+i),r=initial.slice();
  r[2]=indexBase+phase;let loads=0;
  const trace=phase?[rows[0],...rows.slice(1,5)]:[rows[0],...rows.slice(5)];
  for(const row of trace){const op=row.op,a=row.operands;if(op==='bbci'||op==='j')continue;
   const d=reg(a[0]),s=reg(a[1]);
   if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='l32i'){assert.equal(r[s]+Number(a[2]),indexBase);r[d]=bits;loads++;}
   else if(op==='slli'){const n=Number(a[2]);r[d]=Array(n).fill(0).concat(r[s].slice(0,32-n));}
   else if(op==='srai'){const n=Number(a[2]);r[d]=r[s].slice(n).concat(Array(n).fill(r[s][31]));}
   else assert.fail(op);
  }
  assert.deepEqual(r[2],bits.slice(phase*8,phase*8+16).concat(Array(16).fill(bits[phase*8+15])));
  for(let i=0;i<16;i++)if(i!==2)assert.equal(r[i],initial[i]);assert.equal(loads,1);
  records.push({phase,result:r[2],loads,executed:trace.length});
 }
 return{records,instructions:9,executed_per_phase:5,live_bytes:liveBytes,sar:'untouched',scope:'Every word bit and both aligned int16 phases; all GPRs except result a2 unchanged. No SAR instruction.'};
}
function execute(fn,initial,memory,index,sar){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r]));
 const r=initial.slice(),mem=new Map(memory),writes=[],visited=[];let pc=site,steps=0,words=0,shorts=0;
 const read=(addr,bytes)=>{if(addr>=indexBase&&addr+bytes<=indexBase+index.length){const off=addr-indexBase;if(bytes===4){assert.equal(addr%4,0);words++;return index.readUInt32LE(off);}shorts++;return index.readInt16LE(off)>>>0;}assert.ok(mem.has(addr),'Unknown RAM read '+addr.toString(16));const v=mem.get(addr);return bytes===2?((v<<16)>>16)>>>0:v;};
 while(pc!==continuation){assert.ok(++steps<24);const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));visited.push(pc);let next=pc+row.bytes;const op=row.op,a=row.operands;
  if(op==='j'){assert.ok(pc===site||helperInside(pc));next=prior.target(row);}
  else if(op==='bbci'){assert.equal(pc,helper);if(((r[reg(a[0])]>>>Number(a[1]))&1)===0)next=prior.target(row);}
  else{const d=reg(a[0]),s=reg(a[1]);
   if(op==='mov')r[d]=r[s];else if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='l16si'||op==='l32i')r[d]=read(r[s]+Number(a[2]),op==='l16si'?2:4);
   else if(op==='s32i'){assert.equal(s,1,'New non-stack write');const addr=r[s]+Number(a[2]);mem.set(addr,r[d]);writes.push(addr);}
   else assert.fail('Unknown prefix operation '+op);
  }pc=next;
 }return{registers:r,memory:mem,writes,visited,steps,words,shorts,sar,pc};
}
function numeric(oldFn,newFn){
 const original=parentProof().functions.quant_partition,a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r])),originalMap=new Map(base.parsed(original).map(r=>[r.address,r]));
 const result={signed_cases:0,table_cases:0,old_steps:0,new_steps:0,word_loads:0};const data=Buffer.alloc(212);
 const check=(off,sar,kind,seed)=>{
  const r=Array.from({length:16},(_,i)=>Math.imul(seed+i+1,0x45d9f3b)>>>0);r[1]=0x3fffef00;r[2]=indexBase+off;r[12]=0x3ffe1000;
  const mem=new Map([[r[1]+116,(seed^0x87654321)>>>0],[r[12]+28,(seed^0xf1234567)>>>0],[r[1]+108,0x12345678]]);
  const x=word.execute(a,r,mem,data,sar),y=execute(b,r,mem,data,sar),z=word.execute(originalMap,r,mem,data,sar);
  assert.deepEqual(y.registers,z.registers);assert.deepEqual(y.writes,z.writes);
  for(let i=1;i<16;i++)assert.equal(x.registers[i],y.registers[i],'Live a'+i);
  assert.equal(y.registers[0],r[0]);assert.deepEqual([...x.memory].sort(),[...y.memory].sort());assert.deepEqual(x.writes.sort(),y.writes.sort());
  assert.equal(y.memory.get(r[1]+108),r[0]);assert.equal(x.sar,y.sar);assert.equal(y.sar,sar);
  assert.equal(y.words,1);assert.equal(x.words,y.words);assert.equal(x.shorts,y.shorts);assert.equal(y.steps-x.steps,-5);
  result[kind+'_cases']++;result.old_steps+=x.steps;result.new_steps+=y.steps;result.word_loads++;
 };
 for(let value=0;value<65536;value++)for(const phase of[0,2]){data.writeUInt32LE(Math.imul(value+1,0x45d9f3b)>>>0,0);data.writeUInt16LE(value,phase);check(phase,value&63,'signed',value+phase);}
 const index=tables().index;assert.equal(index.length,105);index.forEach((n,i)=>data.writeInt16LE(n,i*2));
 for(let i=0;i<index.length;i++)for(let sar=0;sar<64;sar++)check(i*2,sar,'table',i*64+sar);
 assert.equal(base.parsed(original).find(r=>r.address===late)?.text,'s32i a0, a1, 108');
 return{...result,scope:'All65536 signed values/both phases and105 actual indices/all64 SAR values. Compare actual linked prefixes; original a0 preserved, all remaining GPRs and final stack identical.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)),'Outside index patches changed');
 const jump=b.find(r=>r.address===site);assert.equal(jump?.op,'j');assert.equal(jump.bytes,3);assert.equal(prior.target(jump),helper);
 assert.equal(b.find(r=>r.address===late)?.text,'s32i a0, a1, 108');
 assert.equal(b.find(r=>r.address===resume)?.text,'mov a15, a3');
 assert.equal(b.find(r=>r.address===0x4024e434)?.text,'l32i a0, a1, 108');
 return{storage:storageProof(oldFn),helper:helperSymbolic(newFn),numeric:numeric(oldFn,newFn),return_slot:108,patches,frame_bytes:112,static_ram_delta:0};
}
module.exports={helper,helperBytes,site,late,continuation,indexBase,indexBytes,tableBase,tableBytes,inside,helperInside,definitions,storageProof,storageBytesProof,findPatches,helperSymbolic,execute,numeric,prove};
