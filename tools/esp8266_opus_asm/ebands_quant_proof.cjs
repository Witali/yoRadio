// Authenticate and execute the actual linked replacement, including stack reads.
// Reuse an accepted leaf; never infer spare space from linear disassembly.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,sourceHash,hash}=require('./export.cjs');
const {parsed}=require('./bits_fifth_proof.cjs'),{target}=require('./partition_frozen_proof.cjs');
const old=require('./ebands_pair_proof.cjs'),more=require('./ebands_more_proof.cjs'),final=require('./ebands_final_proof.cjs');
const {readAt}=require('./pvq_exp2_table32_proof.cjs');
const site=0x40250ab3,bytes=15,end=site+bytes,helper=0x4024dd48,helperBytes=36;
const definitions=()=>`ebands_init = 0x${helper.toString(16)};`;
const tableProof=old.tableProof,reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
function sharedLeaf(elf){
 const file=path.join(root,'firmware/development/esp8266-opus-ebands-more-candidate-v1/preflight.json'),p=JSON.parse(fs.readFileSync(file));
 const slot=p.patches.find(x=>x.address===helper);assert.equal(slot.bytes,helperBytes);
 assert.equal(readAt(elf,helper,helperBytes).toString('hex'),slot.after_hex,'Accepted helper changed');
 return{origin_sha256_lf:sourceHash(file),sha256:hash(readAt(elf,helper,helperBytes)),disassembly:p.helperDisassembly[0]};
}
function findPatches(functions){
 const fn=functions.quant_all_bands,rs=parsed(fn);assert.equal(fn.address,0x402507d8);
 assert.deepEqual(rs.filter(r=>r.address>=site&&r.address<end).map(r=>r.text),[
  'l32i a10, a1, 116','l16si a2, a8, 0','l32i a9, a1, 428','l32i a11, a1, 200','l16si a3, a8, 2']);
 for(const r of rs)if(/^b|^j$|^call0$/.test(r.op))assert.ok(!(target(r)>site&&target(r)<end),'Interior entry');
 return[{address:site,bytes}];
}
function deadA5(fn){
 const rs=parsed(fn),map=new Map(rs.map(r=>[r.address,r])),seen=[];let pc=end;
 while(pc!==0x40250ace){const r=map.get(pc);assert.ok(r);assert.ok(!r.operands.includes('a5'),'Live a5');
  assert.ok(!/^b|^j|^call|^ret/.test(r.op),'Unreviewed branch before a5 overwrite');seen.push(pc);pc+=r.bytes;}
 assert.equal(map.get(pc).text,'movi a5, 1');return{visited:seen,overwrite:pc};
}
function provenance(fn){
 const rs=parsed(fn),at=pc=>rs.find(r=>r.address===pc)?.text;
 const checks={
  0x402507e0:'l32i a9, a3, 24',0x402507f1:'s32i a4, a1, 224',0x40250803:'s32i a5, a1, 244',0x40250809:'s32i a9, a1, 280',
  0x40250887:'l32i a10, a1, 224',0x4025088f:'l32i a8, a1, 280',0x40250892:'slli a10, a10, 1',0x4025089a:'add a8, a8, a10',0x402508b9:'s32i a8, a1, 288',
  0x402509e0:'l32i a10, a1, 224',0x402509e3:'l32i a11, a1, 244',0x402509fa:'blt a10, a11, 40250a00 <quant_all_bands+552>',0x402509fd:'j 40252844 <quant_all_bands+8300>',
  0x40250a21:'mov a15, a10',0x40250a6f:'l32i a8, a1, 288',0x40250a86:'s32i a8, a1, 144',0x40250aad:'s32i a15, a1, 116',0x40250ab0:'l32i a8, a1, 144',
  0x402527fd:'addi a14, a14, 1',0x40252804:'s32i a14, a1, 116',0x40252815:'l32i a11, a1, 144',0x40252823:'addi a11, a11, 2',0x40252828:'s32i a11, a1, 144',
  0x4025282f:'l32i a10, a1, 116',0x40252832:'l32i a11, a1, 244',0x4025283b:'beq a10, a11, 40252841 <quant_all_bands+8297>',0x4025283e:'j 40250ab0 <quant_all_bands+728>'};
 for(const [pc,text]of Object.entries(checks))assert.equal(at(+pc),text);
 const writes=rs.filter(r=>/^s(?:8|16|32)i$/.test(r.op)&&r.operands[1]==='a1'&&[116,144,224,244,280,288].some(x=>Number(r.operands[2])<x+4&&Number(r.operands[2])+Number(r.op.match(/\d+/)[0])/8>x));
 assert.deepEqual(writes.map(r=>r.address),[0x402507f1,0x40250803,0x40250809,0x402508b9,0x40250a86,0x40250aad,0x40252804,0x40252828]);
 // Only the60-byte band_ctx at frame32 escapes; slots116/144/224+ are not
 // part of that object. Assert every direct private-frame address creation.
 const aliases=rs.filter(r=>['add','addi','addmi','mov','or'].includes(r.op)&&r.operands.slice(1).includes('a1'));
 for(const r of aliases)assert.ok(r.text==='or a1, a1, a1'||r.text==='add a1, a1, a9'||(r.op==='addi'&&r.operands[1]==='a1'&&r.operands[2]==='32'),'Unexpected private frame alias');
 return{checks,slot_writes:writes.map(r=>r.address),frame_aliases:aliases.map(r=>({pc:r.address,text:r.text})),domain:'Unchanged standard-mode call contract:0<=start<=end<=21. Header checks start<end. Pointer starts eBands+2*start, increments2 with i until end; pairs i0..20 fit44B. Only band_ctx[32,92) escapes; valid caller arrays cannot alias private slots. No bitrate restriction.'};
}
function execute(rows,initial,data,sar,stackValues){
 const map=rows instanceof Map?rows:new Map(rows.map(r=>[r.address,r])),r=initial.slice();let pc=site,steps=0,words=0,shorts=0;const stack=[];
 assert.ok(r[8]>=old.table&&r[8]<=old.table+40&&r[8]%2===0,'Invalid pair pointer');
 while(pc!==end){assert.ok(++steps<24);const row=map.get(pc);assert.ok(row);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){assert.equal(pc,site+3);assert.equal(target(row),helper);r[0]=next;next=helper;}
  else if(op==='ret')next=r[0];
  else if(op==='bbsi'){if(r[reg(a[0])]&(1<<Number(a[1])))next=target(row);}
  else{const d=reg(a[0]),src=reg(a[1]);
   if(op==='or')r[d]=(r[src]|r[reg(a[2])])>>>0;
   else if(op==='addi')r[d]=(r[src]+Number(a[2]))>>>0;
   else if(op==='slli')r[d]=(r[src]<<Number(a[2]))>>>0;
   else if(op==='srai')r[d]=(r[src]>>Number(a[2]))>>>0;
   else if(op==='l32i'&&src===1){const offset=Number(a[2]);assert.ok(Object.hasOwn(stackValues,offset));r[d]=stackValues[offset]>>>0;stack.push({offset,d,value:r[d]});}
   else if(op==='l32i'||op==='l16si'){const n=op==='l32i'?4:2,address=r[src]+Number(a[2]),off=address-old.table;assert.equal(address%n,0);assert.ok(off>=0&&off+n<=44);r[d]=(n===4?data.readUInt32LE(off):data.readInt16LE(off))>>>0;if(n===4)words++;else shorts++;}
   else assert.fail('Unmodeled '+op);
  }pc=next;
 }return{registers:r,sar,pc,steps,words,shorts,stack};
}
function prove(functions,actual,helperDisassembly){
 const patches=findPatches(functions),fn=functions.quant_all_bands,a=parsed(fn),b=parsed(actual.quant_all_bands),hs=parsed({disassembly:helperDisassembly});
 for(const n of Object.keys(functions))if(n!=='quant_all_bands')assert.deepEqual(actual[n],functions[n]);
 const inside=pc=>pc>=site&&pc<end;assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)));
 assert.deepEqual(b.filter(r=>inside(r.address)).map(r=>r.text),['or a5, a8, a8','call0 4024dd48 <quant_partition+588>','l32i a10, a1, 116','l32i a9, a1, 428','l32i a11, a1, 200']);
 const symbolic=more.symbolic(helperDisassembly,{helper,high:3}),before=new Map(a.map(r=>[r.address,r])),after=new Map([...b,...hs].map(r=>[r.address,r]));
 const data=Buffer.alloc(44);let numeric=0;
 const check=(index,sar,seed)=>{const r=Array.from({length:16},(_,j)=>Math.imul(seed+j+1,0x45d9f3b)>>>0);r[8]=old.table+2*index;
  const stack={116:Math.imul(seed,0x9e3779b9),428:seed^0x2468ace0,200:~seed};
  const x=execute(before,r,data,sar,stack),y=execute(after,r,data,sar,stack);assert.equal(y.registers[0],site+6);assert.equal(y.registers[5],r[8]);y.registers[0]=x.registers[0];y.registers[5]=x.registers[5];
  assert.deepEqual(y.registers,x.registers);assert.deepEqual(y.stack,x.stack);assert.equal(y.sar,x.sar);assert.equal(y.pc,x.pc);assert.equal(x.shorts,2);assert.equal(y.shorts,0);assert.equal(y.words,index%2?2:1);numeric++;};
 for(let n=0;n<65536;n++)for(const index of[0,1]){data.writeUInt32LE(Math.imul(n+1,0x45d9f3b)>>>0,0);data.writeUInt32LE(Math.imul(n+2,0x45d9f3b)>>>0,4);data.writeUInt16LE(n,2*index);check(index,n&63,n);}
 old.values.forEach((v,j)=>data.writeInt16LE(v,2*j));for(let j=0;j<21;j++)for(let sar=0;sar<64;sar++)check(j,sar,j*64+sar);
 return{patches,symbolic,numeric_cases:numeric,dead_a0:final.deadReturn(fn,{site,bytes}),dead_a5:deadA5(fn),provenance:provenance(fn),frame_bytes:384,static_ram_delta:0,stack_delta:0};
}
module.exports={site,bytes,end,helper,helperBytes,definitions,sharedLeaf,tableProof,findPatches,deadA5,provenance,execute,prove};
