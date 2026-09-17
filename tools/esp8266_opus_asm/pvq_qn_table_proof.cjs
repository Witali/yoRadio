// Exact table of v+1, NOT just rounded qn: preserve a2 and SAR at the join.
// Decoder-private clone only. Values qb<4 retain the untouched original path.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,sourceHash}=require('./export.cjs'),parser=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs');
const old=require('./pvq_exp2_table32_proof.cjs');
const table=0x4024dcb0,tableBytes=260,pool=old.pool,start=0x4024dc68,end=0x4024dc8b;
const values=Array.from({length:65},(_,qb)=>qb<4?1:(old.values[qb&7]>>>(14-(qb>>>3)))+1);
const inside=a=>a>=start&&a<end,storage=a=>a>=table&&a<table+tableBytes;
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=>`qn_table = 0x${table.toString(16)};\nqn_pool = 0x${pool.toString(16)};\nqn_continue = 0x${end.toString(16)};`;
function storageProof(fn){
 const file=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1/preflight.json');
 const origin=JSON.parse(fs.readFileSync(file)).functions.quant_partition;
 const prog=prior.program(origin),dead=new Set(analyze(prog).dead.map(d=>prog.rows[d.index].address));
 const rows=parser.parsed(origin),cover=rows.filter(r=>r.address<table+tableBytes&&r.address+r.bytes>table);
 assert.ok(cover.length&&cover[0].address<=table&&cover.at(-1).address+cover.at(-1).bytes>=table+tableBytes);
 assert.ok(cover.every(r=>dead.has(r.address)),'Live original storage');
 for(let i=1;i<cover.length;i++)assert.equal(cover[i-1].address+cover[i-1].bytes,cover[i].address);
 const before=rows.filter(r=>r.address<cover[0].address).at(-1);assert.ok(dead.has(before.address),'Live original fallthrough');
 const incoming=rows.filter(r=>/^b|^j$|^call0$/.test(r.op)&&!storage(r.address)&&storage(prior.target(r)));
 assert.ok(incoming.every(r=>dead.has(r.address)),'Original live entry');
 const now=parser.parsed(fn);assert.ok(!now.some(r=>r.address<table+tableBytes&&r.address+r.bytes>table),'Current storage reachable');
 for(const r of now)if(/^b|^j$|^call0$/.test(r.op))assert.ok(!storage(prior.target(r)),'Table entry');
 return{address:table,bytes:tableBytes,original_instructions:cover.length,origin_sha256_lf:sourceHash(file),incoming:incoming.map(r=>r.address),
  rule:'All overlapping original instructions and predecessor dead under immutable decoder encode=0. Accepted exp2-table32 data inside this span are intentionally replaced; current CFG has no entry.'};
}
function domainProof(fn){
 const rows=parser.parsed(fn),at=pc=>rows.find(r=>r.address===pc);
 assert.equal(at(0x4024dbcd).text,'blti a2, 4, 4024dbd3 <quant_partition+215>');
 assert.equal(at(0x4024dbd0).text,'j 4024dc61 <quant_partition+357>');
 assert.equal(at(0x4024dc61).text,'movi a3, 64');
 assert.equal(at(0x4024dc63).text,'bge a3, a2, 4024dc68 <quant_partition+364>');
 assert.equal(at(0x4024dc66).text,'mov a2, a3');
 const incoming=rows.filter(r=>/^b|^j$|^call0$/.test(r.op)&&prior.target(r)>=0x4024dc61&&prior.target(r)<end);
 assert.deepEqual(incoming.map(r=>r.address),[0x4024dbd0,0x4024dc63]);
 // Neither preceding interval can fall through: both end in unconditional J.
 assert.equal(at(0x4024dc5c).op,'j');assert.equal(at(0x4024dbd0).op,'j');
 return{minimum:4,maximum:64,lower_guard:0x4024dbcd,upper_guard:0x4024dc63,incoming:incoming.map(r=>r.address)};
}
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);storageProof(fn);domainProof(fn);
 return[{address:start,bytes:end-start},{address:pool,bytes:4},{address:table,bytes:tableBytes}];
}
function tableProof(elf,candidate){
 const t=Buffer.alloc(tableBytes);values.forEach((v,i)=>t.writeInt32LE(v,i*4));
 assert.equal(old.readAt(elf,pool,4).readUInt32LE(),candidate?table:old.table);
 assert.deepEqual(old.values.map((_,i)=>old.readAt(elf,old.oldTable+i*2,2).readInt16LE()),old.values);
 if(candidate)assert.deepEqual(old.readAt(elf,table,tableBytes),t,'Exact v+1 table');
 else {const raw=old.readAt(elf,old.table,32);assert.deepEqual(old.values.map((_,i)=>raw.readInt32LE(i*4)),old.values);}
 return{address:table,bytes:tableBytes,values,old_constants:old.oldTable};
}
function literalProof(elf,timeFn,candidate){
 // The earlier exhaustive byte-aligned scanner also authenticates the only
 // incidental opcode pattern in time_service_poll. Canonicalize solely our
 // changed live sequence before invoking it, never candidate table bytes.
 const read=old.readAt,base=require('./frozen_reloads.cjs'),buf=Buffer.from(elf);
 if(candidate){
  const p=JSON.parse(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-pvq-exp2-table32-candidate-v1/preflight.json')));
  const bytes=parser.parsed(p.actual_functions.quant_partition).filter(r=>inside(r.address));
  // Authentic parent instruction bytes are recovered from its retained ELF.
  const zlib=require('node:zlib'),origin=base.patchElf(zlib.gunzipSync(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-pvq-exp2-table32-candidate-v1/parent.elf.gz'))),p.patches);
  assert.equal(bytes[0].address,start);read(origin,start,end-start).copy(buf,base.offsetAt(buf,start,end-start));
  const seq=read(elf,start,end-start);assert.equal((seq[3]&15),1,'Candidate literal opcode');
  const pc=start+3;assert.equal(((pc+3)&~3)+seq.readUInt16LE(4)*4-0x40000,pool);
 }
 const audit=old.literalReadersProof(buf,timeFn);
 return{...audit,sole_reader:candidate?start+3:old.literalSite,scope:'All executable byte alignments outside the authenticated replacement scanned, including new table data; replacement has exactly one authenticated L32R.'};
}
function execute(fn,qb,sar,candidate){
 assert.ok(Number.isInteger(qb)&&qb>=4&&qb<=64);
 const map=new Map(parser.parsed(fn).map(r=>[r.address,r])),r=Array.from({length:16},(_,i)=>(0xdead0000+i)>>>0);r[2]=qb;
 let pc=start,steps=0,loads=0;
 while(pc!==end){const row=map.get(pc);assert.ok(row);assert.ok(++steps<20);const a=row.operands,op=row.op;
  if(op==='j'){assert.equal(prior.target(row),end);pc=end;continue;}
  const d=reg(a[0]);
  if(op==='l32r'){assert.equal(prior.target(row),pool);r[d]=candidate?table:old.table;}
  else if(op==='movi')r[d]=Number(a[1])>>>0;
  else if(op==='ssr')sar=r[d]&63;
  else{const s=reg(a[1]);
   if(op==='extui')r[d]=(r[s]>>>Number(a[2]))&((1<<Number(a[3]))-1);
   else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;
   else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='add')r[d]=(r[s]+r[reg(a[2])])>>>0;
   else if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='sub')r[d]=(r[s]-r[reg(a[2])])>>>0;
   else if(op==='and')r[d]=(r[s]&r[reg(a[2])])>>>0;
   else if(op==='sra'){assert.ok(sar<32);r[d]=(r[s]>>sar)>>>0;}
   else if(op==='l32i'){const index=(r[s]+Number(a[2])-(candidate?table:old.table))/4;
    assert.ok(Number.isInteger(index)&&index>=(candidate?4:0)&&index<=(candidate?64:7));r[d]=candidate?values[index]:old.values[index];loads++;}
   else assert.fail('Unexpected '+op);
  }pc+=row.bytes;
 }return{registers:r,sar,pc,steps,loads};
}
function prove(before,after){
 const patches=findPatches(before),a=parser.parsed(before),b=parser.parsed(after);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)),'Outside instructions changed');
 const seq=b.filter(r=>inside(r.address));
 assert.deepEqual(seq.map(r=>r.op),['slli','l32r','add','srai','movi','sub','ssr','l32i','movi','and','j']);
 let cases=0;
 for(let qb=4;qb<=64;qb++)for(let sar=0;sar<64;sar++){
  const x=execute(before,qb,sar,false),y=execute(after,qb,sar,true);
  assert.deepEqual(x.registers,y.registers);assert.equal(x.sar,y.sar);assert.equal(x.pc,y.pc);
  assert.equal(x.loads,1);assert.equal(y.loads,1);assert.equal(x.steps,13);assert.equal(y.steps,11);cases++;
 }
 return{storage:storageProof(before),domain:domainProof(before),cases,old_steps:13,new_steps:11,
  frame_bytes:112,stack_delta:0,static_ram_delta:0,patches,
  contract:'Only a2/a3/a4 and SAR written: compare all61 legal qb and64 incoming SAR. No GPR output depends on any other incoming register, and all other registers remain untouched. Equal all registers and SAR at original store; untouched qb<4 branch. No timing claim.'};
}
module.exports={table,tableBytes,pool,start,end,values,inside,storage,definitions,storageProof,domainProof,findPatches,tableProof,literalProof,execute,prove};
