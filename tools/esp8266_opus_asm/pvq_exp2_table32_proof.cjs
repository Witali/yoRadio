// Exact inline word-table access. Signed values, all GPRs and SAR preserved.
// Dead flash storage and sole literal-reader audit are separate prerequisites.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,sourceHash,hash}=require('./export.cjs'),base=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs'),frozen=require('./frozen_reloads.cjs');
const {sections}=require('./frozen_div.cjs');
const table=0x4024dd28,tableBytes=32,oldTable=0x402d74d8,pool=0x40211a9c;
const shift=0x4024dc6b,load=0x4024dc76,start=0x4024dc68,continuation=0x4024dc7b,literalSite=0x4024dc6e;
const values=[16384,17866,19483,21247,23170,25267,27554,30048];
const storageInside=a=>a>=table&&a<table+tableBytes;
const instructionInside=a=>a===shift||a===load;
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=>`pvq_exp2_table32 = 0x${table.toString(16)};`;
const originDir=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1');
function storageProof(fn){
 const file=path.join(originDir,'preflight.json'),origin=JSON.parse(fs.readFileSync(file)).functions.quant_partition;
 const p=prior.program(origin),dead=new Set(analyze(p).dead.map(d=>p.rows[d.index].address));
 const rows=base.parsed(origin),storage=rows.filter(r=>storageInside(r.address));
 assert.equal(storage[0].address,table);assert.equal(storage.at(-1).address+storage.at(-1).bytes,table+tableBytes);
 assert.ok(storage.every(r=>dead.has(r.address)));for(let i=1;i<storage.length;i++)assert.equal(storage[i-1].address+storage[i-1].bytes,storage[i].address);
 const predecessor=rows.filter(r=>r.address<table).at(-1);assert.equal(predecessor.address+predecessor.bytes,table);
 assert.equal(predecessor.text,'add a3, a8, a3');assert.ok(dead.has(predecessor.address),'Live fallthrough into table');
 const incoming=rows.filter(r=>/^b|^j$|^call0$/.test(r.op)&&!storageInside(r.address)&&storageInside(prior.target(r)));
 assert.ok(incoming.every(r=>dead.has(r.address)),'Live original branch into table');
 const current=base.parsed(fn);assert.equal(current.filter(r=>storageInside(r.address)).length,0);
 for(const r of current)if(/^b|^j$|^call0$/.test(r.op))assert.ok(!storageInside(prior.target(r)),'Occupied table entry');
 return{origin_sha256_lf:sourceHash(file),address:table,bytes:tableBytes,instructions:storage.length,predecessor:{address:predecessor.address,text:predecessor.text,dead:true},incoming:incoming.map(r=>({address:r.address,target:prior.target(r),dead:true})),scope:'Original table slot, preceding fallthrough and entries are decoder-inaccessible under immutable encode=0. Current parent has no entry; data is never executed.'};
}
function storageBytesProof(elf){
 const p=JSON.parse(fs.readFileSync(path.join(originDir,'preflight.json'))),original=zlib.gunzipSync(fs.readFileSync(path.join(originDir,'parent.elf.gz')));
 assert.equal(hash(original),p.parent_elf_sha256);const a=frozen.offsetAt(original,table,tableBytes),b=frozen.offsetAt(elf,table,tableBytes),bytes=original.subarray(a,a+tableBytes);
 assert.deepEqual(elf.subarray(b,b+tableBytes),bytes,'Original table storage changed');return{parent_elf_sha256:hash(original),address:table,bytes:tableBytes,hex:bytes.toString('hex')};
}
function readAt(elf,address,bytes){const ss=sections(elf).filter(s=>s.type===1&&(s.flags&2)&&address>=s.address&&address+bytes<=s.address+s.bytes);assert.equal(ss.length,1);return elf.subarray(ss[0].offset+address-ss[0].address,ss[0].offset+address-ss[0].address+bytes);}
// Scan every byte position, not linear objdump boundaries (which can miss a
// real instruction after unreachable padding). Fail closed on new matches.
function literalReadersProof(elf,timeFn){
 const readers=[],pointers=[];
 for(const s of sections(elf).filter(s=>s.type===1&&(s.flags&2))){const b=elf.subarray(s.offset,s.offset+s.bytes);
  for(let i=0;i+4<=b.length;i++)if(b.readUInt32LE(i)===pool)pointers.push({section:s.name,address:s.address+i});
  if(s.flags&4)for(let i=0;i+3<=b.length;i++)if((b[i]&15)===1){const pc=s.address+i,target=((pc+3)&~3)+b.readUInt16LE(i+1)*4-0x40000;
   if(target===pool)readers.push({section:s.name,address:pc,register:b[i]>>4,hex:b.subarray(i,i+3).toString('hex')});}
 }
 assert.deepEqual(pointers,[],'Address-taken literal');
 assert.deepEqual(readers,[{section:'.flash.text',address:0x4021d1d3,register:2,hex:'2132d2'},{section:'.flash.text',address:literalSite,register:3,hex:'318b0f'}],'Unexpected literal reader');
 const rows=base.parsed(timeFn),cover=rows.find(r=>r.address===0x4021d1d2);
 assert.equal(cover?.text,'l32i a12, a1, 200');assert.equal(cover.bytes,3);assert.equal(readAt(elf,cover.address,3).toString('hex'),'c22132');
 assert.ok(!rows.some(r=>r.address===0x4021d1d3));
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op))assert.notEqual(prior.target(r),0x4021d1d3);
 return{readers,address_taken:pointers,excluded_mid_instruction:0x4021d1d3,covering_instruction:cover,sole_reader:literalSite,scope:'All byte alignments of allocated executable ELF sections scanned. The sole extra opcode pattern is inside an unchanged reachable time_service_poll L32I, not an instruction boundary; no allocated pointer to the literal exists.'};
}
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);storageProof(fn);
 const rows=base.parsed(fn);assert.equal(rows.find(r=>r.address===shift)?.text,'slli a4, a3, 1');assert.equal(rows.find(r=>r.address===load)?.text,'l16si a3, a3, 0');
 for(const pc of[shift,load])assert.equal(rows.find(r=>r.address===pc).bytes,3);
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)){const t=prior.target(r);assert.ok(!(t>start&&t<continuation),'Interior external entry');}
 return[{address:shift,bytes:3},{address:load,bytes:3},{address:pool,bytes:4},{address:table,bytes:tableBytes}];
}
function symbolic(oldFn,newFn){
 const a=base.parsed(oldFn).filter(r=>r.address>=start&&r.address<continuation),b=base.parsed(newFn).filter(r=>r.address>=start&&r.address<continuation);
 assert.equal(a.length,7);assert.equal(b.length,7);const records=[];
 for(let index=0;index<8;index++){
  const initial=Array.from({length:16},(_,i)=>'R'+i);initial[2]=Array.from({length:32},(_,i)=>i<3?(index>>>i)&1:'Q'+i);
  const run=(rows,candidate)=>{const r=initial.slice(),bits=Array.from({length:16},(_,i)=>'T'+index+'_'+i);let reads=0;
   for(const row of rows){const op=row.op,x=row.operands,d=reg(x[0]);
    if(op==='extui'){assert.equal(Number(x[2]),0);assert.equal(Number(x[3]),3);r[d]=r[reg(x[1])].slice(0,3).reduce((n,v,i)=>n+v*2**i,0);}
    else if(op==='slli')r[d]=r[reg(x[1])]*2**Number(x[2]);
    else if(op==='l32r'){assert.equal(prior.target(row),pool);r[d]=candidate?table:oldTable;}
    else if(op==='srai'){const input=r[reg(x[1])],n=Number(x[2]);r[d]=input.slice(n).concat(Array(n).fill(input[31]));}
    else if(op==='add')r[d]=r[reg(x[1])]+r[reg(x[2])];
    else if(op==='l16si'||op==='l32i'){assert.equal(r[reg(x[1])]+Number(x[2]),(candidate?table:oldTable)+index*(candidate?4:2));r[d]=bits.concat(Array(16).fill(bits[15]));reads++;}
    else if(op==='movi')r[d]=Number(x[1]);else assert.fail(op);
   }assert.equal(reads,1);return r;};
  const x=run(a,false),y=run(b,true);assert.deepEqual(x,y);records.push({index,result_bits:y[3],remaining_qb_bits:y[2],a4:y[4]});
 }
 return{cases:8,records,scope:'All32 input qb bits and every signed16 table bit are symbolic. Enumerate only the eight possible low3-bit indices. Signed32 storage is independently authenticated; other GPRs are unchanged symbols. No SAR instruction.'};
}
function execute(fn,initial,halfwords,words,sar,candidate){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r])),r=initial.slice(),reads=[];
 let pc=start,steps=0;
 while(pc!==continuation){const row=map.get(pc);assert.ok(row,'Unknown PC');assert.ok(++steps<=8);const op=row.op,a=row.operands,d=reg(a[0]);
  if(op==='l32r'){assert.equal(prior.target(row),pool);r[d]=candidate?table:oldTable;}
  else if(op==='movi')r[d]=Number(a[1])>>>0;
  else{const s=reg(a[1]);
   if(op==='extui')r[d]=(r[s]>>>Number(a[2]))&((1<<Number(a[3]))-1);
   else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='add')r[d]=(r[s]+r[reg(a[2])])>>>0;
   else if(op==='l16si'||op==='l32i'){const address=r[s]+Number(a[2]),bytes=op==='l16si'?2:4,off=address-(bytes===2?oldTable:table),data=bytes===2?halfwords:words;
    assert.ok(off>=0&&off+bytes<=data.length,'Table bounds');assert.equal(address%bytes,0,'Table alignment');
    r[d]=(bytes===2?data.readInt16LE(off):data.readInt32LE(off))>>>0;reads.push({bytes,index:off/bytes});}
   else assert.fail('Unknown instruction '+op);
  }pc+=row.bytes;
 }return{registers:r,sar,pc,steps,reads};
}
function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r])),half=Buffer.alloc(16),word=Buffer.alloc(32);
 const result={signed_cases:0,table_cases:0,old_steps:0,new_steps:0};
 const check=(qb,sar,kind,seed)=>{const r=Array.from({length:16},(_,i)=>Math.imul(seed+i+1,0x45d9f3b)>>>0);r[1]=0x3fffef00;r[2]=qb>>>0;
  const x=execute(a,r,half,word,sar,false),y=execute(b,r,half,word,sar,true);assert.deepEqual(x.registers,y.registers);assert.equal(x.sar,y.sar);assert.equal(x.pc,y.pc);assert.equal(x.steps,y.steps);
  assert.deepEqual(x.reads,[{bytes:2,index:qb&7}]);assert.deepEqual(y.reads,[{bytes:4,index:qb&7}]);result[kind+'_cases']++;result.old_steps+=x.steps;result.new_steps+=y.steps;};
 for(let value=0;value<65536;value++)for(const i of[0,1]){const signed=value<32768?value:value-65536;half.writeInt16LE(signed,i*2);word.writeInt32LE(signed,i*4);check(8+i,value&63,'signed',value+i);}
 values.forEach((v,i)=>{half.writeInt16LE(v,i*2);word.writeInt32LE(v,i*4);});
 for(let qb=4;qb<=64;qb++)for(let sar=0;sar<64;sar++)check(qb,sar,'table',qb*64+sar);
 return{...result,scope:'All65536 signed values at both int16 phases; all61 clamped qb values/all64 SAR states. Equal visible instruction count, no cycle estimate.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 assert.deepEqual(a.filter(r=>!instructionInside(r.address)),b.filter(r=>!instructionInside(r.address)),'Outside instruction patches changed');
 assert.equal(b.find(r=>r.address===shift)?.text,'slli a4, a3, 2');assert.equal(b.find(r=>r.address===load)?.text,'l32i a3, a3, 0');
 for(const pc of[shift,load])assert.equal(b.find(r=>r.address===pc).bytes,3);
 const seq=b.filter(r=>r.address>=start&&r.address<continuation);assert.equal(seq.length,7);
 assert.equal(seq[0].text,'extui a3, a2, 0, 3');assert.equal(seq[2].op,'l32r');assert.equal(prior.target(seq[2]),pool);
 assert.equal(seq[3].text,'srai a2, a2, 3');assert.equal(seq[4].text,'add a3, a3, a4');assert.equal(seq[6].text,'movi a4, 14');
 for(let i=1;i<seq.length;i++)assert.equal(seq[i-1].address+seq[i-1].bytes,seq[i].address);
 assert.equal(seq.at(-1).address+seq.at(-1).bytes,continuation);
 return{storage:storageProof(oldFn),symbolic:symbolic(oldFn,newFn),numeric:numeric(oldFn,newFn),patches,frame_bytes:112,static_ram_delta:0,contract:'For every32-bit input a2, EXTUI selects index0..7. Only a4 differs temporarily (2*i vs4*i), and unchanged immediate MOVI kills it at the join. Every other GPR and SAR match; signed32 table entries are exact extensions of original int16 entries. No new call or output buffer.'};
}
module.exports={table,tableBytes,oldTable,pool,shift,load,start,continuation,literalSite,values,storageInside,instructionInside,definitions,storageProof,storageBytesProof,readAt,literalReadersProof,findPatches,symbolic,execute,numeric,prove};
