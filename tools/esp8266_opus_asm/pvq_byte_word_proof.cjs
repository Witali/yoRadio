// Actual linked flash-byte helper + call-site proof. No timing claims.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=require('./bits_fifth_proof.cjs'),prior=require('./partition_frozen_proof.cjs');
const {analyze}=require('./partition_decode.cjs'),{tables}=require('./pulse_lookup.cjs');
const {component,sourceHash}=require('./export.cjs');
const helper=0x4024ddec,helperBytes=57,tableBase=0x402d57fc,tableBytes=392;
const sites=[0x4024e1c3,0x4024e1d6,0x4024e1ea,0x4024e204,0x4024e284];
const helperInside=a=>a>=helper&&a<helper+helperBytes;
const inside=a=>helperInside(a)||sites.some(s=>a>=s&&a<s+3);
const definitions=()=> 'pvq_read_byte = 0x'+helper.toString(16)+';';
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);
 const program=prior.program(fn),analysis=analyze(program),dead=new Set(analysis.dead.map(d=>program.rows[d.index].address));
 const rows=base.parsed(fn),storage=rows.filter(r=>helperInside(r.address));
 assert.equal(helper%4,0);assert.equal(storage[0].address,helper);
 assert.equal(storage.at(-1).address+storage.at(-1).bytes,helper+helperBytes);
 assert.ok(storage.every(r=>dead.has(r.address)),'Helper storage is reachable in decoder');
 for(let i=1;i<storage.length;i++)assert.equal(storage[i].address,storage[i-1].address+storage[i-1].bytes);
 for(const r of rows)if(/^b|^j$/.test(r.op)&&!helperInside(r.address)){
  const t=prior.target(r);assert.ok(t<=helper||t>=helper+helperBytes,'External entry into helper interior');
 }
 for(const site of sites){const r=rows.find(r=>r.address===site);assert.equal(r?.bytes,3);assert.equal(r.text,'l8ui a10, a10, 0');}
 return [{address:helper,bytes:helperBytes},...sites.map(address=>({address,bytes:3}))];
}
// Caller a0 may be discarded only before a new CALL0 or explicit restore.
// CALLX0 through a0 reads it first and must fail. Unlike the inherited generic
// scratch check this distinguishes CALL0's implicit a0 write from ABI arguments.
function deadReg(fn,start,rn){
 const rows=base.parsed(fn),map=new Map(rows.map(r=>[r.address,r])),seen=new Set(),queue=[start],ends=[];
 const dest=new Set('addi addmi add sub mull mul16s slli srai srli sll sra srl and or xor neg extui nsau l32r movi mov l32i l16si l16ui l8ui'.split(' '));
 while(queue.length){const pc=queue.pop();if(seen.has(pc))continue;seen.add(pc);const r=map.get(pc);assert.ok(r,'Missing liveness PC');
  const a=r.operands,name='a'+rn;
  if(r.op==='call0'){assert.ok(rn===0||(rn>=8&&rn<=11));ends.push({pc,kind:rn===0?'call0-return-definition':'abi-clobber'});continue;}
  if(r.op==='callx0'){assert.ok(!a.includes(name),'Live indirect target '+name);assert.ok(rn===0||(rn>=8&&rn<=11));ends.push({pc,kind:'callx0-clobber'});continue;}
  if(r.op==='ret'){assert.ok(rn===10||rn===11,'Live return a0');ends.push({pc,kind:'unused-return'});continue;}
  let reads=a;if(dest.has(r.op))reads=a.slice(1);
  else assert.ok(/^b|^j$|^s(?:8|16|32)i$|^ssr$|^ssl$/.test(r.op),'Unmodelled liveness opcode '+r.op);
  assert.ok(!reads.includes(name),'Live '+name+' at '+pc.toString(16));
  if(dest.has(r.op)&&a[0]===name){ends.push({pc,kind:'definition'});continue;}
  if(r.op==='j')queue.push(prior.target(r));else if(/^b/.test(r.op))queue.push(prior.target(r),pc+r.bytes);else queue.push(pc+r.bytes);
 }return {register:rn,start,visited:[...seen].sort((a,b)=>a-b),ends};
}
function helperSymbolic(fn){
 const rows=base.parsed(fn).filter(r=>helperInside(r.address)),expected=[
 'rsr.sar a11','ssa8l a10','srli a10, a10, 2','slli a10, a10, 2',
 'l32i a10, a10, 0','srl a10, a10','extui a10, a10, 0, 8','wsr.sar a11','ret.n'];
 assert.deepEqual(rows.map(r=>r.text.trim()),expected);
 assert.equal(rows[0].address,helper);assert.ok(rows.at(-1).address+rows.at(-1).bytes<=helper+helperBytes);
 const records=[];
 for(let phase=0;phase<4;phase++){
  const r=Array.from({length:16},(_,i)=>'R'+i),initial=r.slice(),word=Array.from({length:32},(_,i)=>'W'+i),savedSar=Array.from({length:6},(_,i)=>'S'+i);
  r[10]=tableBase+phase;let sar=savedSar,loads=0;
  for(const row of rows){const a=row.operands,d=reg(a[0]||'a0'),op=row.op;
   if(op==='rsr.sar')r[d]=sar;
   else if(op==='ssa8l'){assert.equal(typeof r[d],'number');sar=(r[d]&3)*8;}
   else if(op==='srli')r[d]=r[reg(a[1])]>>>Number(a[2]);
   else if(op==='slli')r[d]=(r[reg(a[1])]<<Number(a[2]))>>>0;
   else if(op==='l32i'){assert.equal(r[reg(a[1])]+Number(a[2]),tableBase);r[d]=word;loads++;}
   else if(op==='srl'){assert.ok(Array.isArray(r[reg(a[1])]));r[d]=r[reg(a[1])].slice(sar).concat(Array(sar).fill(0));}
   else if(op==='extui'){assert.ok(Array.isArray(r[reg(a[1])]));r[d]=r[reg(a[1])].slice(Number(a[2]),Number(a[2])+Number(a[3])).concat(Array(32-Number(a[3])).fill(0));}
   else if(op==='wsr.sar')sar=r[d];
   else if(op==='ret')assert.equal(r[0],initial[0]);
   else assert.fail(op);
  }
  assert.deepEqual(r[10],word.slice(phase*8,phase*8+8).concat(Array(24).fill(0)));assert.deepEqual(sar,savedSar);
  for(let i=0;i<16;i++)if(i!==10&&i!==11)assert.equal(r[i],initial[i]);assert.equal(loads,1);
  records.push({phase,output:r[10],sar,word_loads:loads});
 }
 return {records,instructions:rows.length,live_bytes:rows.at(-1).address+rows.at(-1).bytes-helper,
  statement:'All32 input word bits, all four byte phases, arbitrary SAR; no other register/memory change except dead a11.'};
}
let cachedBits;
function execute(fn,initial,cache,pointer,initialSar){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r])),data=cachedBits??(cachedBits=tables().bits);
 const r=initial.slice(),reads=[],wordReads=[],visited=[];let pc=base.start,steps=0,sar=initialSar,returnPc=null;
 while(!base.stops.includes(pc)){
  const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<240);
  visited.push(pc);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){assert.ok(sites.includes(pc));assert.equal(prior.target(row),helper);assert.equal(returnPc,null);returnPc=next;
   const index=r[10]-pointer;assert.ok(index>=0&&index<cache.length,'Caller byte outside row');reads.push(index);r[0]=next;next=helper;}
  else if(op==='ret'){assert.ok(helperInside(pc));assert.equal(r[0],returnPc);next=r[0];returnPc=null;}
  else if(op==='j')next=prior.target(row);
  else if(op==='movi')r[reg(a[0])]=Number(a[1])>>>0;
  else if(op==='beqz'){if(r[reg(a[0])]===0)next=prior.target(row);}
  else if(op==='blt'||op==='bge'){const lt=(r[reg(a[0])]|0)<(r[reg(a[1])]|0);if(op==='blt'?lt:!lt)next=prior.target(row);}
  else if(op==='bgei'){if((r[reg(a[0])]|0)>=Number(a[1]))next=prior.target(row);}
  else if(op==='rsr.sar')r[reg(a[0])]=sar;
  else if(op==='wsr.sar')sar=r[reg(a[0])]&63;
  else if(op==='ssa8l')sar=(r[reg(a[0])]&3)*8;
  else {
   const d=reg(a[0]),s=reg(a[1]);
   if(op==='mov')r[d]=r[s];
   else if(op==='add')r[d]=(r[s]+r[reg(a[2])])>>>0;
   else if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='sub')r[d]=(r[s]-r[reg(a[2])])>>>0;
   else if(op==='or')r[d]=(r[s]|r[reg(a[2])])>>>0;
   else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='srli')r[d]=r[s]>>>Number(a[2]);
   else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;
   else if(op==='srl'){assert.ok(sar<32);r[d]=r[s]>>>sar;}
   else if(op==='extui'){assert.equal(Number(a[3]),8);r[d]=(r[s]>>>Number(a[2]))&255;}
   else if(op==='l8ui'){const address=(r[s]+Number(a[2]))>>>0,index=address-pointer;assert.ok(index>=0&&index<cache.length,'Out-of-row read');reads.push(index);r[d]=cache[index];}
   else if(op==='l32i'){assert.ok(helperInside(pc));const address=r[s]+Number(a[2]),off=address-tableBase;
    assert.equal(address%4,0,'Unaligned word');assert.ok(off>=0&&off+4<=data.length,'Word outside complete table');
    wordReads.push(address);r[d]=(data[off]|data[off+1]<<8|data[off+2]<<16|data[off+3]<<24)>>>0;}
   else assert.fail('Unknown helper/search operation '+op);
  }pc=next;
 }assert.equal(returnPc,null);return {registers:r,pc,reads,wordReads,visited,steps,sar};
}
function numeric(oldFn,newFn){
 const old=new Map(base.parsed(oldFn).map(r=>[r.address,r])),now=new Map(base.parsed(newFn).map(r=>[r.address,r])),t=tables();
 const result={cases:0,word_loads:0,old_steps:0,new_steps:0,call_sites:Object.fromEntries(sites.map(s=>[s.toString(16),0]))};
 for(const off of t.offsets)for(let budget=-64;budget<=16383;budget++){
  const cache=t.bits.slice(off,off+t.bits[off]+1),pointer=tableBase+off,r=Array.from({length:16},(_,i)=>Math.imul(budget+i+1,0x45d9f3b)>>>0);
  r[2]=pointer;r[6]=cache[0];r[7]=0;r[14]=budget>>>0;const sar=(budget^0x35)&63;
  const a=base.execute(old,r,cache,pointer),b=execute(now,r,cache,pointer,sar);
  assert.equal(a.pc,b.pc);assert.equal(b.sar,sar);assert.deepEqual(a.reads,b.reads);
  for(let i=0;i<16;i++)if(i!==0&&i!==11)assert.equal(a.registers[i],b.registers[i],'Live a'+i+' budget'+budget+' row'+off);
  assert.deepEqual(a.visited,b.visited.filter(pc=>!helperInside(pc)),'Caller branch/order changed');
  result.cases++;result.word_loads+=b.wordReads.length;result.old_steps+=a.steps;result.new_steps+=b.steps;
  for(const pc of sites)result.call_sites[pc.toString(16)]+=Number(b.visited.includes(pc));
 }
 assert.ok(Object.values(result.call_sites).every(n=>n>0));
 return {...result,scope:'Actual linked helper and complete PVQ search, every standard row/budget -64..16383; byte results/order and SAR exact. Instruction counts exclude old exception emulation and are NOT time.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 const rest=rows=>rows.filter(r=>!inside(r.address));assert.deepEqual(rest(a),rest(b),'Outside helper/calls changed');
 for(const pc of sites){const r=b.find(r=>r.address===pc);assert.equal(r?.bytes,3);assert.equal(r.op,'call0');assert.equal(prior.target(r),helper);}
 const liveness=sites.flatMap(pc=>[0,11].map(r=>deadReg(oldFn,pc+3,r)));
 const config=fs.readFileSync(path.join(component,'upstream/include/config.h'),'utf8');assert.doesNotMatch(config,/^\s*#\s*define\s+CUSTOM_MODES\b/m);
 return {helper:helperSymbolic(newFn),liveness,numeric:numeric(oldFn,newFn),patches,
  frame_bytes:112,static_ram_delta:0,sar:'Saved/restored for every byte; helper changes only a10 and dead a11; CALL0 changes dead a0.',
  config_sha256_lf:sourceHash(path.join(component,'upstream/include/config.h')),
  rule:'Only five homogeneous byte probes, no table copy or new RAM, original private decoder contract inherited; every non-helper instruction stays at its old address.'};
}
module.exports={helper,helperBytes,tableBase,tableBytes,sites,inside,helperInside,definitions,findPatches,helperSymbolic,deadReg,execute,numeric,prove};
