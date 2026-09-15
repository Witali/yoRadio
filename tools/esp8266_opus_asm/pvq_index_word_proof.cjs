// Signed index word extraction and early-return-store scheduling proof.
// The target does not allocate, change frame size, or use a CALL return.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,sourceHash,hash}=require('./export.cjs'),base=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs');
const first=require('./pvq_byte_word_proof.cjs'),endpoint=require('./pvq_endpoint_word_proof.cjs');
const frozen=require('./frozen_reloads.cjs'),{tables}=require('./pulse_lookup.cjs');
const helper=0x4024dc95,helperBytes=29,site=0x4024db22,late=0x4024db36,continuation=0x4024db39;
const indexBase=0x402d5984,indexBytes=210,tableBase=first.tableBase,tableBytes=first.tableBytes;
const helperInside=a=>a>=helper&&a<helper+helperBytes;
const inside=a=>helperInside(a)||(a>=site&&a<site+3)||(a>=late&&a<late+3);
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=>`pvq_index_word = 0x${helper.toString(16)};\npvq_index_continue = 0x${continuation.toString(16)};`;
const originDir=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1');
function storageProof(fn){
 const file=path.join(originDir,'preflight.json'),origin=JSON.parse(fs.readFileSync(file)).functions.quant_partition;
 const p=prior.program(origin),analysis=analyze(p),dead=new Set(analysis.dead.map(d=>p.rows[d.index].address));
 const rows=base.parsed(origin),storage=rows.filter(r=>helperInside(r.address));
 assert.equal(storage[0].address,helper);assert.equal(storage.at(-1).address+storage.at(-1).bytes,helper+helperBytes);
 assert.ok(storage.every(r=>dead.has(r.address)));for(let i=1;i<storage.length;i++)assert.equal(storage[i-1].address+storage[i-1].bytes,storage[i].address);
 const previous=rows.filter(r=>r.address<helper).at(-1);assert.equal(previous.op,'j');assert.ok(!helperInside(prior.target(previous)));
 const incoming=rows.filter(r=>/^b|^j$|^call0$/.test(r.op)&&!helperInside(r.address)&&helperInside(prior.target(r)));
 assert.equal(incoming.length,1);assert.equal(incoming[0].address,0x4024e42d);assert.ok(incoming.every(r=>dead.has(r.address)));
 // The parent endpoint helper disconnected this old encoder island. Its bytes
 // remain in ELF and are authenticated independently by storageBytesProof.
 assert.equal(base.parsed(fn).filter(r=>helperInside(r.address)).length,0);
 return {origin_sha256_lf:sourceHash(file),helper,bytes:helperBytes,instructions:storage.length,incoming:incoming.map(r=>({address:r.address,target:prior.target(r),dead:true})),scope:'All original storage and incoming paths are encoder-only for immutable encode=0, including all data-dependent branches. No fallthrough.'};
}
function storageBytesProof(elf){
 const proof=JSON.parse(fs.readFileSync(path.join(originDir,'preflight.json'))),original=zlib.gunzipSync(fs.readFileSync(path.join(originDir,'parent.elf.gz')));
 assert.equal(hash(original),proof.parent_elf_sha256);
 const a=frozen.offsetAt(original,helper,helperBytes),b=frozen.offsetAt(elf,helper,helperBytes),bytes=original.subarray(a,a+helperBytes);
 assert.deepEqual(elf.subarray(b,b+helperBytes),bytes,'Old helper storage changed since authenticated original');
 return {parent_elf_sha256:hash(original),address:helper,bytes:helperBytes,hex:bytes.toString('hex')};
}
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);storageProof(fn);
 const rows=base.parsed(fn);for(const [pc,text]of[[site,'l16si a2, a2, 0'],[late,'s32i a0, a1, 108']]){const r=rows.find(r=>r.address===pc);assert.equal(r?.bytes,3);assert.equal(r.text,text);}
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)){const t=prior.target(r);assert.ok(!(t>site&&t<continuation),'Entry bypasses early saved return');}
 return [{address:helper,bytes:helperBytes},{address:site,bytes:3},{address:late,bytes:3}];
}
function helperSymbolic(fn){
 const rows=base.parsed(fn).filter(r=>helperInside(r.address));
 assert.deepEqual(rows.slice(0,9).map(r=>r.text.trim()),['rsr.sar a0','ssa8l a2','srli a2, a2, 2','slli a2, a2, 2','l32i a2, a2, 0','srl a2, a2','slli a2, a2, 16','srai a2, a2, 16','wsr.sar a0']);
 assert.equal(rows.length,10);assert.equal(rows[9].op,'j');assert.equal(prior.target(rows[9]),continuation);assert.equal(rows[9].address+rows[9].bytes,helper+29);
 const records=[];for(const phase of[0,2]){
  const word=Array.from({length:32},(_,i)=>'W'+i),saved=Array.from({length:6},(_,i)=>'S'+i);
  const r=Array.from({length:16},(_,i)=>'R'+i);r[2]=indexBase+phase;const initial=r.slice();let sar=saved,loads=0;
  for(const row of rows){const a=row.operands,op=row.op;if(op==='j')continue;const d=reg(a[0]);
   if(op==='rsr.sar')r[d]=sar;else if(op==='ssa8l')sar=(r[d]&3)*8;
   else if(op==='srli')r[d]=r[reg(a[1])]>>>Number(a[2]);
   else if(op==='slli'){const value=r[reg(a[1])],n=Number(a[2]);r[d]=Array.isArray(value)?Array(n).fill(0).concat(value.slice(0,32-n)):(value<<n)>>>0;}
   else if(op==='l32i'){assert.equal(r[reg(a[1])]+Number(a[2]),indexBase);r[d]=word;loads++;}
   else if(op==='srl')r[d]=r[reg(a[1])].slice(sar).concat(Array(sar).fill(0));
   else if(op==='srai'){const bits=r[reg(a[1])],n=Number(a[2]);r[d]=bits.slice(n).concat(Array(n).fill(bits[31]));}
   else if(op==='wsr.sar')sar=r[d];else assert.fail(op);
  }
  assert.deepEqual(r[2],word.slice(phase*8,phase*8+16).concat(Array(16).fill(word[phase*8+15])));assert.deepEqual(sar,saved);assert.equal(loads,1);
  for(let i=0;i<16;i++)if(i!==0&&i!==2)assert.equal(r[i],initial[i]);records.push({phase,result:r[2],sar,loads});
 }
 return {records,instructions:10,live_bytes:29,scope:'All32 word bits, both aligned int16 phases and arbitrary SAR; signed high word preserved, only a2 result/dead a0 change.'};
}
function execute(fn,initial,memory,index,sar){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r]));
 const r=initial.slice(),mem=new Map(memory),writes=[],visited=[];let pc=site,steps=0,words=0,shorts=0;
 const read=(addr,bytes,signed)=>{if(addr>=indexBase&&addr+bytes<=indexBase+index.length){const off=addr-indexBase;if(bytes===4){assert.equal(addr%4,0);words++;return index.readUInt32LE(off);}shorts++;return index.readInt16LE(off)>>>0;}assert.ok(mem.has(addr),'Unknown RAM read '+addr.toString(16));const v=mem.get(addr);return bytes===2?((v<<16)>>16)>>>0:v;};
 while(pc!==continuation){assert.ok(++steps<24);const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));visited.push(pc);let next=pc+row.bytes;const op=row.op,a=row.operands;
  if(op==='j'){assert.ok(pc===late||helperInside(pc));next=prior.target(row);}
  else {const d=reg(a[0]);
   if(op==='rsr.sar')r[d]=sar;else if(op==='wsr.sar')sar=r[d]&63;else if(op==='ssa8l')sar=(r[d]&3)*8;
   else {const s=reg(a[1]);
    if(op==='mov')r[d]=r[s];else if(op==='srli')r[d]=r[s]>>>Number(a[2]);else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;
    else if(op==='srl'){assert.ok(sar<32);r[d]=r[s]>>>sar;}else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
    else if(op==='l16si'||op==='l32i')r[d]=read(r[s]+Number(a[2]),op==='l16si'?2:4,true);
    else if(op==='s32i'){assert.equal(s,1,'New non-stack write');const addr=r[s]+Number(a[2]);mem.set(addr,r[d]);writes.push(addr);}
    else assert.fail('Unknown prefix operation '+op);
   }
  }pc=next;
 }return{registers:r,memory:mem,writes,visited,steps,words,shorts,sar,pc};
}
function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r]));
 const result={signed_cases:0,table_cases:0,old_steps:0,new_steps:0,word_loads:0};const data=Buffer.alloc(212);
 const check=(off,sar,kind,seed)=>{
  const r=Array.from({length:16},(_,i)=>Math.imul(seed+i+1,0x45d9f3b)>>>0);r[1]=0x3fffef00;r[2]=indexBase+off;r[12]=0x3ffe1000;
  const memory=new Map([[r[1]+116,(seed^0x87654321)>>>0],[r[12]+28,(seed^0xf1234567)>>>0],[r[1]+108,0x12345678]]);
  const x=execute(a,r,memory,data,sar),y=execute(b,r,memory,data,sar);
  for(let i=0;i<16;i++)if(i!==0)assert.equal(x.registers[i],y.registers[i],'Live a'+i);
  assert.deepEqual([...x.memory].sort(),[...y.memory].sort());assert.deepEqual(x.writes.sort(),y.writes.sort());
  assert.equal(y.memory.get(r[1]+108),r[0],'Lost original return');assert.equal(x.sar,y.sar);assert.equal(y.sar,sar);
  assert.equal(y.words-x.words,1);assert.equal(x.shorts-y.shorts,1);assert.equal(y.steps-x.steps,10);
  result[kind+'_cases']++;result.old_steps+=x.steps;result.new_steps+=y.steps;result.word_loads++;
 };
 for(let value=0;value<65536;value++)for(const phase of[0,2]){
  data.writeUInt32LE(Math.imul(value+1,0x45d9f3b)>>>0,0);data.writeUInt16LE(value,phase);check(phase,value&63,'signed',value+phase);
 }
 const index=tables().index;assert.equal(index.length,105);index.forEach((n,i)=>data.writeInt16LE(n,i*2));
 for(let i=0;i<index.length;i++)for(let sar=0;sar<64;sar++)check(i*2,sar,'table',i*64+sar);
 return {...result,scope:'All65536 signed values/two phases; all105 actual indices/all64 SAR values, including last word. Actual linked prefix, all live GPRs and final stack contents, no extra memory writes.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)),'Outside index patches changed');
 assert.equal(b.find(r=>r.address===site)?.text,'s32i a0, a1, 108');const jump=b.find(r=>r.address===late);assert.equal(jump?.op,'j');assert.equal(jump.bytes,3);assert.equal(prior.target(jump),helper);
 const middle=a.filter(r=>r.address>site&&r.address<late);
 assert.deepEqual(middle.map(r=>r.text),['mov a15, a3','s32i a7, a1, 24','mov a3, a4','l16si a7, a1, 116','l32i a4, a12, 28','s32i a13, a1, 100','s32i a14, a1, 96']);
 assert.ok(middle.every(r=>!r.operands.includes('a2')&&!r.operands.includes('a0')));
 assert.equal(a.find(r=>r.address===continuation)?.text,'add a2, a11, a2');assert.equal(a.find(r=>r.address===0x4024e434)?.text,'l32i a0, a1, 108');
 const dead=first.deadReg(oldFn,continuation,0);for(const e of dead.ends)assert.equal(e.kind,'call0-return-definition');
 return {storage:storageProof(oldFn),helper:helperSymbolic(newFn),scheduling:{intervening:middle,return_slot:108,old_store:late,new_store:site,a0_liveness:dead,rule:'Neither a2 nor a0 used in between; same RAM stores, static flash read has no alias to stack/ctx.'},numeric:numeric(oldFn,newFn),interrupt_context:endpoint.interruptContext(),patches,frame_bytes:112,static_ram_delta:0};
}
module.exports={helper,helperBytes,site,late,continuation,indexBase,indexBytes,tableBase,tableBytes,inside,helperInside,definitions,storageProof,storageBytesProof,findPatches,helperSymbolic,execute,numeric,prove};
