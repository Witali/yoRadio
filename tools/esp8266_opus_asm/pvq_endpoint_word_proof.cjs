// Actual linked endpoint word accesses. Reuse the existing a10 leaf for upper;
// a fixed-continuation lower fragment uses dead a0 for SAR, not a CALL return.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const first=require('./pvq_byte_word_proof.cjs'),middle=require('./pvq_a4_word_proof.cjs'),rowWord=require('./pvq_row_word_proof.cjs');
const base=require('./bits_fifth_proof.cjs'),prior=require('./partition_frozen_proof.cjs');
const {analyze}=require('./partition_decode.cjs'),{tables}=require('./pulse_lookup.cjs'),{root,sourceHash}=require('./export.cjs');
const helper=0x4024e403,helperBytes=48,upperPtr=0x4024e21d,upperSite=0x4024e21f,lowerSite=0x4024e22a,lowerContinue=0x4024e22d;
const sites=[upperSite,lowerSite],tableBase=first.tableBase,tableBytes=first.tableBytes;
const helperInside=a=>a>=helper&&a<helper+helperBytes;
const inside=a=>helperInside(a)||(a>=upperPtr&&a<upperSite+3)||(a>=lowerSite&&a<lowerSite+3);
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=> 'pvq_read_byte = 0x'+first.helper.toString(16)+';\npvq_lower_word = 0x'+helper.toString(16)+';\npvq_lower_continue = 0x'+lowerContinue.toString(16)+';';
function storageProof(fn){
 const file=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1/preflight.json');
 const origin=JSON.parse(fs.readFileSync(file)).functions.quant_partition;
 const p=prior.program(origin),analysis=analyze(p),dead=new Set(analysis.dead.map(d=>p.rows[d.index].address));
 const before=base.parsed(origin),rows=base.parsed(fn),storage=rows.filter(r=>helperInside(r.address));
 assert.equal(storage[0]?.address,helper);assert.equal(storage.at(-1)?.address+storage.at(-1)?.bytes,helper+helperBytes);
 assert.deepEqual(storage,before.filter(r=>helperInside(r.address)),'Storage changed since original CFG proof');
 assert.ok(storage.every(r=>dead.has(r.address)),'Reachable encoder-only storage');
 for(let i=1;i<storage.length;i++)assert.equal(storage[i].address,storage[i-1].address+storage[i-1].bytes);
 const previous=rows.filter(r=>r.address<helper).at(-1);
 assert.equal(previous.op,'ret');assert.equal(previous.address+previous.bytes,rowWord.helper+25);
 assert.equal(rowWord.helper+rowWord.helperBytes,helper);rowWord.helperSymbolic(fn);
 const incoming=[];
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)&&!helperInside(r.address)){
  const target=prior.target(r);if(!helperInside(target))continue;
  assert.equal(target,helper,'External entry into helper interior');
  assert.deepEqual(r,before.find(x=>x.address===r.address),'Changed incoming edge');
  assert.ok(dead.has(r.address),'Incoming edge is reachable in decoder');
  incoming.push({address:r.address,target,dead:true});
 }
 assert.equal(incoming.length,1);
 return {origin_sha256_lf:sourceHash(file),instructions:storage.length,incoming,helper,bytes:helperBytes,
  statement:'Entire original encoder-only tail is dead for encode=0 for all audio-dependent branches. Preceding row helper returns before its own padding; no fallthrough/interior entry.'};
}
function findPatches(fn){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);storageProof(fn);
 const rows=base.parsed(fn);
 for(const [pc,text,bytes]of[[upperPtr,'add a9, a2, a6',2],[upperSite,'l8ui a10, a9, 0',3],[lowerSite,'l8ui a11, a11, 0',3]]){
  const r=rows.find(r=>r.address===pc);assert.equal(r?.bytes,bytes);assert.equal(r.text,text);
 }
 for(const r of rows)if(/^b|^j$|^call0$/.test(r.op)){
  const t=prior.target(r);assert.ok(!(t>upperPtr&&t<upperSite+3),'Bypassed upper address setup');
 }
 return [{address:helper,bytes:helperBytes},{address:upperPtr,bytes:2},...sites.map(address=>({address,bytes:3}))];
}
function helperSymbolic(fn){
 const rows=base.parsed(fn).filter(r=>helperInside(r.address));
 const expected=['rsr.sar a0','ssa8l a11','srli a11, a11, 2','slli a11, a11, 2','l32i a11, a11, 0','srl a11, a11','extui a11, a11, 0, 8','wsr.sar a0'];
 assert.deepEqual(rows.slice(0,8).map(r=>r.text.trim()),expected);assert.equal(rows.length,9);
 assert.equal(rows[8].op,'j');assert.equal(prior.target(rows[8]),lowerContinue,'Wrong fixed continuation');
 assert.equal(rows[0].address,helper);assert.equal(rows.at(-1).address+rows.at(-1).bytes,helper+26);
 const records=[];
 for(let phase=0;phase<4;phase++){
  const r=Array.from({length:16},(_,i)=>'R'+i);r[11]=tableBase+phase;
  const initial=r.slice(),word=Array.from({length:32},(_,i)=>'W'+i),savedSar=Array.from({length:6},(_,i)=>'S'+i);
  let sar=savedSar,loads=0;
  for(const row of rows){const a=row.operands,op=row.op;if(op==='j'){assert.equal(prior.target(row),lowerContinue);continue;}const d=reg(a[0]);
   if(op==='rsr.sar')r[d]=sar;
   else if(op==='ssa8l'){assert.equal(typeof r[d],'number');sar=(r[d]&3)*8;}
   else if(op==='srli')r[d]=r[reg(a[1])]>>>Number(a[2]);
   else if(op==='slli')r[d]=(r[reg(a[1])]<<Number(a[2]))>>>0;
   else if(op==='l32i'){assert.equal(r[reg(a[1])]+Number(a[2]),tableBase);r[d]=word;loads++;}
   else if(op==='srl'){assert.ok(Array.isArray(r[reg(a[1])]));r[d]=r[reg(a[1])].slice(sar).concat(Array(sar).fill(0));}
   else if(op==='extui'){assert.ok(Array.isArray(r[reg(a[1])]));r[d]=r[reg(a[1])].slice(Number(a[2]),Number(a[2])+Number(a[3])).concat(Array(32-Number(a[3])).fill(0));}
   else if(op==='wsr.sar')sar=r[d];else assert.fail(op);
  }
  assert.deepEqual(r[11],word.slice(phase*8,phase*8+8).concat(Array(24).fill(0)));assert.deepEqual(sar,savedSar);
  for(let i=0;i<16;i++)if(i!==0&&i!==11)assert.equal(r[i],initial[i]);assert.equal(loads,1);
  records.push({phase,output:r[11],sar,word_loads:loads});
 }
 return {records,instructions:9,live_bytes:26,continuation:lowerContinue,
  statement:'All32 word bits/four phases/arbitrary SAR. Only a11 result and dead a0 change; fixed jump cannot consume the saved original return or add a frame.'};
}
let cachedBits;
function execute(fn,initial,cache,pointer,initialSar,options={}){
 const map=fn instanceof Map?fn:new Map(base.parsed(fn).map(r=>[r.address,r])),data=cachedBits??(cachedBits=tables().bits);
 const r=initial.slice(),reads=[],wordReads=[],visited=[];let pc=options.start??base.start,steps=0,sar=initialSar,returnPc=null,lowerActive=false;const stops=options.stops??base.stops;
 while(!stops.includes(pc)){
  const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<340);
  visited.push(pc);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){const upper=pc===upperSite,rowProbe=rowWord.sites.includes(pc),a4=middle.sites.includes(pc),dst=rowProbe?rowWord.helper:a4?middle.helper:first.helper,rn=rowProbe?2:a4?4:10;assert.ok(upper||rowProbe||a4||first.sites.includes(pc));assert.equal(prior.target(row),dst);assert.equal(returnPc,null);returnPc=next;
   const index=r[rn]-pointer;assert.ok(index>=0&&index<cache.length,'Caller byte outside row');reads.push(index);r[0]=next;next=dst;}
  else if(op==='ret'){assert.ok(first.helperInside(pc)||rowWord.helperInside(pc)||helperInside(pc));assert.equal(r[0],returnPc);next=r[0];returnPc=null;}
  else if(op==='j'){
   if(pc===lowerSite){assert.equal(prior.target(row),helper);assert.equal(lowerActive,false);lowerActive=true;
    const index=r[11]-pointer;assert.ok(index>=0&&index<cache.length,'Lower byte outside row');reads.push(index);}
   else if(helperInside(pc)){assert.equal(prior.target(row),lowerContinue);assert.equal(lowerActive,true);lowerActive=false;}
   next=prior.target(row);
  }
  else if(op==='movi')r[reg(a[0])]=Number(a[1])>>>0;
  else if(op==='bnei'){if((r[reg(a[0])]|0)!==Number(a[1]))next=prior.target(row);}
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
   else if(op==='l32i'){assert.ok(first.helperInside(pc)||rowWord.helperInside(pc)||helperInside(pc));const address=r[s]+Number(a[2]),off=address-tableBase;
    assert.equal(address%4,0,'Unaligned word');assert.ok(off>=0&&off+4<=data.length,'Word outside complete table');
    wordReads.push(address);r[d]=(data[off]|data[off+1]<<8|data[off+2]<<16|data[off+3]<<24)>>>0;}
   else assert.fail('Unknown helper/search operation '+op);
  }pc=next;
 }assert.equal(returnPc,null);assert.equal(lowerActive,false);return {registers:r,pc,reads,wordReads,visited,steps,sar};
}

function numeric(oldFn,newFn){
 const a=new Map(base.parsed(oldFn).map(r=>[r.address,r])),b=new Map(base.parsed(newFn).map(r=>[r.address,r])),t=tables();
 const result={byte_cases:0,search_cases:0,upper_reads:0,lower_reads:0,added_word_loads:0,old_steps:0,new_steps:0,stops:{}};
 const commonHelper=pc=>first.helperInside(pc)||rowWord.helperInside(pc);
 const check=(r,cache,pointer,sar,options,kind)=>{
  const x=execute(a,r,cache,pointer,sar,options),y=execute(b,r,cache,pointer,sar,options);
  assert.equal(x.pc,y.pc);assert.equal(y.sar,sar);assert.equal(x.sar,sar);assert.deepEqual(x.reads,y.reads);
  for(let i=0;i<16;i++)if(i!==0&&i!==11)assert.equal(x.registers[i],y.registers[i],'Live a'+i+' '+kind);
  assert.deepEqual(x.visited.filter(pc=>!commonHelper(pc)),y.visited.filter(pc=>!commonHelper(pc)&&!helperInside(pc)),'Changed caller flow');
  const upper=Number(x.visited.includes(upperSite)),lower=Number(x.visited.includes(lowerSite)),extra=upper+lower;
  assert.ok(extra>0);assert.equal(y.wordReads.length-x.wordReads.length,extra);
  if(lower)assert.equal(x.registers[11],y.registers[11],'Lower endpoint result');
  result[kind+'_cases']++;result.upper_reads+=upper;result.lower_reads+=lower;result.added_word_loads+=extra;
  result.old_steps+=x.steps;result.new_steps+=y.steps;
  if(kind==='search')result.stops[x.pc]=(result.stops[x.pc]||0)+1;
 };
 for(let off=0;off<t.bits.length;off++)for(let sar=0;sar<64;sar++)for(const upper of[false,true]){
  const r=Array.from({length:16},(_,i)=>Math.imul(off+sar+i+1,0x45d9f3b)>>>0),pointer=tableBase+off;r[2]=pointer;r[6]=0;r[11]=pointer;
  check(r,[t.bits[off]],pointer,sar,{start:upper?upperPtr:lowerSite,stops:[upper?upperSite+6:lowerContinue]},'byte');
 }
 for(const off of t.offsets)for(let budget=-64;budget<=16383;budget++){
  const cache=t.bits.slice(off,off+t.bits[off]+1),pointer=tableBase+off;
  const r=Array.from({length:16},(_,i)=>Math.imul(budget+i+1,0x45d9f3b)>>>0);
  r[2]=pointer;r[6]=cache[0];r[7]=0;r[14]=budget>>>0;
  check(r,cache,pointer,(budget^0x35)&63,{},'search');
 }
 assert.equal(result.new_steps-result.old_steps,9*result.added_word_loads);
 assert.equal(Object.keys(result.stops).length,2);
 return {...result,scope:'Each endpoint across all392 table bytes/64 SAR values; complete search for23 standard rows and every budget -64..16383. Exact q/cost at untouched remaining_bits loop. Instruction counts exclude old exceptions, not timing.'};
}
function upperHelperProof(fn){
 // The old57-byte storage also contains the newer a4 leaf. Validate the
 // unchanged first25 live bytes independently, not both helpers as one body.
 const disassembly=fn.disassembly.split('\n').filter(line=>{
  const m=line.match(/^\s*([0-9a-f]+):/i);if(!m)return false;
  const pc=parseInt(m[1],16);return pc>=first.helper&&pc<first.helper+25;
 }).join('\n');
 return first.helperSymbolic({...fn,disassembly});
}
function interruptContext(){
 const sdk='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/port/esp8266';
 const files=['xtensa_vectors.S','xtensa_context.S','os_cpu_a.S','include/freertos/xtensa_rtos.h'];
 const text=Object.fromEntries(files.map(n=>[n,fs.readFileSync(path.join(sdk,n),'utf8').replace(/\r\n/g,'\n')]));
 const v=text['xtensa_vectors.S'],entry=v.slice(v.indexOf('_xt_user_entry1:\n'),v.indexOf('.L_xt_user_int:\n'));
 assert.match(entry,/rsr\s+a0,\s+EXCSAVE_1/);assert.match(entry,/s32i\s+a0,\s+sp,\s+XT_STK_A0/);
 const exit=v.slice(v.indexOf('_xt_user_exit:\n'),v.indexOf('_xt_user_exit:\n')+1400);assert.match(exit,/l32i\s+a0,\s+sp,\s+XT_STK_A0/);
 const c=text['xtensa_context.S'];assert.match(c,/rsr\s+a3,\s+SAR/);assert.match(c,/s32i\s+a3,\s+sp,\s+XT_STK_SAR/);assert.match(c,/l32i\s+a3,\s+sp,\s+XT_STK_SAR/);assert.match(c,/wsr\s+a3,\s+SAR/);
 assert.match(text['os_cpu_a.S'],/call0\s+_xt_context_save/);assert.match(text['os_cpu_a.S'],/call0\s+_xt_context_restore/);
 assert.match(text['include/freertos/xtensa_rtos.h'],/#define\s+XT_RTOS_INT_ENTER\s+_xt_int_enter/);
 return {sha256_lf:Object.fromEntries(files.map(n=>[n,sourceHash(path.join(sdk,n))])),
  scope:'Actual unchanged SDK level1/task context saves a0 and SAR. New fragment does not mask interrupts or change stack/PC restoration. Source contract check, not an interrupt-latency measurement.'};
}
// Replacing the last encoder tail disconnects an additional old encoder island
// from the generic disassembler. Do not pretend its bytes were deleted or waive
// the whole-ELF equality check in the recipe. Only independently proven-dead,
// unchanged original instructions may be absent from the reachable view.
function outsideViewProof(oldFn,newFn){
 const a=base.parsed(oldFn).filter(r=>!inside(r.address)),b=base.parsed(newFn).filter(r=>!inside(r.address));
 const oldMap=new Map(a.map(r=>[r.address,r])),now=new Map(b.map(r=>[r.address,r]));
 const file=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1/preflight.json');
 const origin=JSON.parse(fs.readFileSync(file)).functions.quant_partition,p=prior.program(origin),analysis=analyze(p);
 const dead=new Set(analysis.dead.map(d=>p.rows[d.index].address)),original=new Map(base.parsed(origin).map(r=>[r.address,r])),omitted=[];
 for(const r of b)assert.deepEqual(r,oldMap.get(r.address),'Outside endpoint patches changed');
 for(const r of a)if(!now.has(r.address)){
  assert.ok(dead.has(r.address),'Outside live instruction omitted');
  assert.deepEqual(r,original.get(r.address),'Outside omitted instruction changed since original CFG proof');
  omitted.push({address:r.address,bytes:r.bytes});
 }
 return {visible_unchanged:b.length,omitted_proven_dead:omitted,origin_sha256_lf:sourceHash(file),
  scope:'Reachable disassembly view only; full ELF/app byte equality outside the declared patches is independently checked by recipe.'};
}
function prove(oldFn,newFn){
 const patches=findPatches(oldFn),a=base.parsed(oldFn),b=base.parsed(newFn);
 assert.equal(oldFn.address,newFn.address);assert.equal(oldFn.bytes,newFn.bytes);
 const outside_view=outsideViewProof(oldFn,newFn);
 assert.equal(b.find(r=>r.address===upperPtr)?.text,'add a10, a2, a6');
 const upper=b.find(r=>r.address===upperSite);assert.equal(upper?.bytes,3);assert.equal(upper.op,'call0');assert.equal(prior.target(upper),first.helper);
 const lower=b.find(r=>r.address===lowerSite);assert.equal(lower?.bytes,3);assert.equal(lower.op,'j');assert.equal(prior.target(lower),helper);
 const liveness=[[upperSite+3,0],[upperSite+3,11],[upperSite+3,9],[lowerContinue,0]].map(([pc,rn])=>first.deadReg(oldFn,pc,rn));
 for(const proof of liveness)for(const end of proof.ends)if(end.kind==='abi-clobber'||end.kind==='call0-return-definition'){
  const target=prior.target(a.find(r=>r.address===end.pc));
  if(target>=oldFn.address&&target<oldFn.address+oldFn.bytes){assert.equal(proof.register,0,'Only actual private a0 clobber may terminate this audit');}
 }
 assert.equal(a.find(r=>r.address===upperSite+3)?.text,'sub a9, a10, a8','Old a9 must be overwritten without being read');
 assert.equal(a.find(r=>r.address===0x4024db36)?.text,'s32i a0, a1, 108','Original return not saved');
 assert.equal(a.find(r=>r.address===0x4024e434)?.text,'l32i a0, a1, 108','Original return not restored');
 return {storage:storageProof(oldFn),helper:helperSymbolic(newFn),upper_helper:upperHelperProof(newFn),liveness,
  numeric:numeric(oldFn,newFn),interrupt_context:interruptContext(),outside_view,patches,frame_bytes:112,static_ram_delta:0,
  rule:'Parent proves immutable encode=0. Complete table/source values and all branch outcomes preserved. Fixed continuation is the same on every recursive invocation; original saved return/frame and adjustment loop are untouched.'};
}
module.exports={helper,helperBytes,upperPtr,upperSite,lowerSite,lowerContinue,sites,tableBase,tableBytes,helperInside,inside,definitions,storageProof,findPatches,helperSymbolic,upperHelperProof,execute,numeric,interruptContext,outsideViewProof,prove};
