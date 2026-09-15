// Exact signed exp2_table8 extraction, fixed continuation, no live-register clobber.
// Decoder-only storage proof includes the otherwise falling-through predecessor.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,sourceHash,hash}=require('./export.cjs'),base=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs'),frozen=require('./frozen_reloads.cjs');
const helper=0x4024dcf8,helperBytes=25,liveBytes=25,site=0x4024dc76,continuation=site+3;
const tableBase=0x402d74d8,tableBytes=16,tableValues=[16384,17866,19483,21247,23170,25267,27554,30048];
const helperInside=a=>a>=helper&&a<helper+helperBytes;
const inside=a=>helperInside(a)||(a>=site&&a<site+3);
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=>`pvq_exp2_word = 0x${helper.toString(16)};\npvq_exp2_continue = 0x${continuation.toString(16)};`;
const originDir=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1');
function storageProof(fn){
 const file=path.join(originDir,'preflight.json'),origin=JSON.parse(fs.readFileSync(file)).functions.quant_partition;
 const p=prior.program(origin),analysis=analyze(p),dead=new Set(analysis.dead.map(d=>p.rows[d.index].address));
 const rows=base.parsed(origin),storage=rows.filter(r=>helperInside(r.address));
 assert.equal(storage[0].address,helper);assert.equal(storage.at(-1).address+storage.at(-1).bytes,helper+helperBytes);
 assert.ok(storage.every(r=>dead.has(r.address)));for(let i=1;i<storage.length;i++)assert.equal(storage[i-1].address+storage[i-1].bytes,storage[i].address);
 const predecessor=rows.filter(r=>r.address<helper).at(-1);
 assert.equal(predecessor.address+predecessor.bytes,helper);assert.equal(predecessor.text,'add a2, a2, a8');assert.ok(dead.has(predecessor.address),'Live fallthrough into storage');
 const incoming=rows.filter(r=>/^b|^j$|^call0$/.test(r.op)&&!helperInside(r.address)&&helperInside(prior.target(r)));
 assert.ok(incoming.every(r=>dead.has(r.address)),'Live original branch into storage');
 const current=base.parsed(fn);assert.equal(current.filter(r=>helperInside(r.address)).length,0);
 for(const r of current)if(/^b|^j$|^call0$/.test(r.op))assert.ok(!helperInside(prior.target(r)),'Occupied helper entry');
 return{origin_sha256_lf:sourceHash(file),helper,bytes:helperBytes,instructions:storage.length,predecessor:{address:predecessor.address,text:predecessor.text,dead:true},incoming:incoming.map(r=>({address:r.address,target:prior.target(r),dead:true})),scope:'All original storage, preceding fallthrough and branch entries are decoder-inaccessible under immutable encode=0. Current parent has no entry. Parent proof chain preserves this contract.'};
}
function storageBytesProof(elf){
 const p=JSON.parse(fs.readFileSync(path.join(originDir,'preflight.json'))),original=zlib.gunzipSync(fs.readFileSync(path.join(originDir,'parent.elf.gz')));
 assert.equal(hash(original),p.parent_elf_sha256);
 const a=frozen.offsetAt(original,helper,helperBytes),b=frozen.offsetAt(elf,helper,helperBytes),bytes=original.subarray(a,a+helperBytes);
 assert.deepEqual(elf.subarray(b,b+helperBytes),bytes,'Original exp2_table8 helper storage changed');
 return{parent_elf_sha256:hash(original),address:helper,bytes:helperBytes,hex:bytes.toString('hex')};
}
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);storageProof(fn);
 const rows=base.parsed(fn),load=rows.find(r=>r.address===site);assert.equal(load?.bytes,3);assert.equal(load.text,'l16si a3, a3, 0');
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)){const t=prior.target(r);assert.ok(!(t>site&&t<continuation));}
 return[{address:helper,bytes:helperBytes},{address:site,bytes:3}];
}
function helperSymbolic(fn){
 const rows=base.parsed(fn).filter(r=>helperInside(r.address));assert.equal(rows.length,9);
 assert.equal(rows[0].op,'bbci');assert.deepEqual(rows[0].operands,['a3','1',(helper+14).toString(16)]);
 assert.deepEqual(rows.slice(1,4).map(r=>r.text),['addi a3, a3, -2','l32i a3, a3, 0','srai a3, a3, 16']);
 assert.deepEqual(rows.slice(5,8).map(r=>r.text),['l32i a3, a3, 0','slli a3, a3, 16','srai a3, a3, 16']);
 for(const row of[rows[4],rows[8]]){assert.equal(row.op,'j');assert.equal(prior.target(row),continuation);}
 assert.equal(rows[0].address,helper);assert.equal(rows[5].address,helper+14);assert.equal(rows[8].address+rows[8].bytes,helper+liveBytes);
 const records=[];
 for(const phase of[0,2]){
  const word=Array.from({length:32},(_,i)=>'W'+i),r=Array.from({length:16},(_,i)=>'R'+i);r[3]=tableBase+phase;const initial=r.slice();let loads=0;
  const trace=phase?[rows[0],...rows.slice(1,5)]:[rows[0],...rows.slice(5)];
  for(const row of trace){const op=row.op,a=row.operands;if(op==='bbci'||op==='j')continue;const d=reg(a[0]),s=reg(a[1]);
   if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='l32i'){assert.equal(r[s]+Number(a[2]),tableBase);r[d]=word;loads++;}
   else if(op==='slli'){const n=Number(a[2]);r[d]=Array(n).fill(0).concat(r[s].slice(0,32-n));}
   else if(op==='srai'){const n=Number(a[2]);r[d]=r[s].slice(n).concat(Array(n).fill(r[s][31]));}
   else assert.fail(op);
  }
  assert.deepEqual(r[3],word.slice(phase*8,phase*8+16).concat(Array(16).fill(word[phase*8+15])));
  for(let i=0;i<16;i++)if(i!==3)assert.equal(r[i],initial[i]);assert.equal(loads,1);
  records.push({phase,result:r[3],loads,executed:trace.length});
 }
 return{records,instructions:9,executed_per_phase:5,live_bytes:liveBytes,sar:'untouched',scope:'Every word bit, both int16 phases, all GPRs except signed result a3 unchanged, including a0/a10; no SAR or stack instruction.'};
}
function execute(fn,initial,data,sar){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r])),r=initial.slice(),visited=[];
 let pc=site,steps=0,words=0,shorts=0;assert.equal(r[3]%2,0,'Unaligned source');assert.ok(r[3]>=tableBase&&r[3]+2<=tableBase+tableBytes,'Source outside exp2_table8');
 while(pc!==continuation){assert.ok(++steps<10);const row=map.get(pc);assert.ok(row,'Unknown PC');visited.push(pc);let next=pc+row.bytes;const op=row.op,a=row.operands;
  if(op==='j'){assert.ok(pc===site||helperInside(pc));next=prior.target(row);}
  else if(op==='bbci'){assert.equal(pc,helper);if(((r[reg(a[0])]>>>Number(a[1]))&1)===0)next=prior.target(row);}
  else{const d=reg(a[0]),s=reg(a[1]);
   if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='l16si'||op==='l32i'){const address=r[s]+Number(a[2]),off=address-tableBase,bytes=op==='l16si'?2:4;assert.ok(off>=0&&off+bytes<=data.length,'Word outside storage');
    if(bytes===4){assert.equal(address%4,0,'Unaligned word');words++;r[d]=data.readUInt32LE(off);}else{shorts++;r[d]=data.readInt16LE(off)>>>0;}}
   else assert.fail('Unsupported exp2_table8 instruction '+op);
  }pc=next;
 }
 return{registers:r,visited,steps,words,shorts,sar,pc};
}
function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r])),data=Buffer.alloc(16);
 const result={signed_cases:0,table_cases:0,word_loads:0,old_steps:0,new_steps:0};
 const check=(off,sar,kind,seed)=>{
  const r=Array.from({length:16},(_,i)=>Math.imul(seed+i+1,0x45d9f3b)>>>0);r[1]=0x3fffef00;r[3]=tableBase+off;
  const x=execute(a,r,data,sar),y=execute(b,r,data,sar);assert.deepEqual(x.registers,y.registers);assert.equal(y.sar,sar);assert.equal(x.sar,y.sar);assert.equal(x.pc,y.pc);
  assert.equal(x.shorts,1);assert.equal(y.shorts,0);assert.equal(y.words,1);assert.equal(x.words,0);assert.equal(y.steps-x.steps,5);
  result[kind+'_cases']++;result.word_loads++;result.old_steps+=x.steps;result.new_steps+=y.steps;
 };
 for(let value=0;value<65536;value++)for(const phase of[0,2]){data.writeUInt32LE(Math.imul(value+1,0x45d9f3b)>>>0,0);data.writeUInt16LE(value,phase);check(phase,value&63,'signed',value+phase);}
 tableValues.forEach((v,i)=>data.writeInt16LE(v,i*2));
 for(let i=0;i<8;i++)for(let sar=0;sar<64;sar++)check(i*2,sar,'table',i*64+sar);
 return{...result,scope:'All65536 signed values/two phases,8 actual exp2_table8 values/all64 SAR states. Five extra visible instructions replace the emulated narrow read; no cycle estimate.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)),'Outside exp2_table8 patches changed');
 const jump=b.find(r=>r.address===site);assert.equal(jump?.op,'j');assert.equal(jump.bytes,3);assert.equal(prior.target(jump),helper);
 for(const r of b)if(/^b|^j$|^call0$/.test(r.op)&&!helperInside(r.address)&&helperInside(prior.target(r))){assert.equal(r.address,site);assert.equal(prior.target(r),helper);}
 assert.equal(b.find(r=>r.address===continuation)?.text,'movi a4, 14');assert.equal(b.find(r=>r.address===0x4024db36)?.text,'s32i a0, a1, 108');
 return{storage:storageProof(oldFn),helper:helperSymbolic(newFn),numeric:numeric(oldFn,newFn),patches,frame_bytes:112,static_ram_delta:0};
}
module.exports={helper,helperBytes,liveBytes,site,continuation,tableBase,tableBytes,tableValues,inside,helperInside,definitions,storageProof,storageBytesProof,findPatches,helperSymbolic,execute,numeric,prove};
