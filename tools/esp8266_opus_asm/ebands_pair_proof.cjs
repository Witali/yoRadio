// Linked-instruction proof; no cycle prediction. Preserve the full int16 domain.
const assert=require('node:assert/strict');
const {parsed}=require('./bits_fifth_proof.cjs'),{target}=require('./partition_frozen_proof.cjs');
const storage=require('./pvq_logn_word_proof.cjs'),{readAt}=require('./pvq_exp2_table32_proof.cjs');
const site=0x402484ae,end=site+6,helper=storage.helper,helperBytes=42,table=0x402d5c5c;
const values=[0,1,2,3,4,5,6,7,8,10,12,14,16,20,24,28,34,40,48,60,78,100];
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const definitions=()=>`ebands_pair = 0x${helper.toString(16)};`;
function tableProof(elf){
 assert.equal(table%4,0);assert.equal(readAt(elf,0x402d3968+24,4).readUInt32LE(),table);
 const raw=readAt(elf,table,44);assert.deepEqual(values.map((_,i)=>raw.readInt16LE(2*i)),values);
 return{address:table,bytes:44,values,mode_pointer:0x402d3968+24};
}
function findPatches(functions){
 storage.storageProof(functions.quant_partition);
 const fn=functions.clt_compute_allocation,rs=parsed(fn);assert.equal(fn.address,0x402482b0);assert.equal(fn.bytes,0xa04);
 assert.equal(rs.find(r=>r.address===site).text,'l16si a2, a3, 2');assert.equal(rs.find(r=>r.address===site+3).text,'l16si a11, a3, 0');
 for(const r of rs)if(/^b|^j$|^call0$/.test(r.op))assert.ok(!(target(r)>site&&target(r)<end),'Interior entry');
 return[{address:site,bytes:6},{address:helper,bytes:helperBytes}];
}
function deadReturn(fn){
 const rs=parsed(fn),map=new Map(rs.map(r=>[r.address,r])),pending=[end],seen=new Set(),stops=[];
 const defs=new Set('addi addmi add sub mull mul16s slli srai srli sll sra srl and or xor neg extui nsau l32r movi mov l32i l16si l16ui l8ui'.split(' '));
 while(pending.length){const pc=pending.pop();if(seen.has(pc))continue;seen.add(pc);const r=map.get(pc);assert.ok(r,'Missing a0 liveness successor');const a=r.operands;
  if(/^call/.test(r.op)){assert.ok(!a.includes('a0'),'Old return address used as indirect target');stops.push({pc,kind:'call0-replaces-a0'});continue;}
  const reads=defs.has(r.op)?a.slice(1):a;assert.ok(!reads.includes('a0')&&r.op!=='ret','Live return address at '+pc.toString(16));
  if(defs.has(r.op)&&a[0]==='a0'){stops.push({pc,kind:'definition'});continue;}
  assert.ok(defs.has(r.op)||/^b|^j$|^s(?:8|16|32)i$|^ssr$|^ssl$|^mov(?:ltz|gez|eqz|nez)$/.test(r.op),'Unknown liveness instruction '+r.op);
  if(r.op==='j')pending.push(target(r));else if(/^b/.test(r.op))pending.push(target(r),pc+r.bytes);else pending.push(pc+r.bytes);
 }return{start:end,register:'a0',visited:[...seen].sort((a,b)=>a-b),stops};
}
function execute(rows,initial,data,sar,candidate){
 const map=rows instanceof Map?rows:new Map(rows.map(r=>[r.address,r])),r=initial.slice();let pc=site,steps=0,words=0,shorts=0;
 assert.ok(r[3]>=table&&r[3]<=table+40&&r[3]%2===0,'Invalid pair pointer');
 while(pc!==end){assert.ok(++steps<20);const row=map.get(pc);assert.ok(row,'Missing instruction '+pc.toString(16));const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){assert.equal(pc,site);assert.equal(target(row),helper);r[0]=next;next=helper;}
  else if(op==='ret')next=r[0];else if(op==='nop'){}
  else if(op==='bbsi'){if(r[reg(a[0])]&(1<<Number(a[1])))next=target(row);}
  else{const d=reg(a[0]),s=reg(a[1]);
   if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
   else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
   else if(op==='l32i'||op==='l16si'){const bytes=op==='l32i'?4:2,address=r[s]+Number(a[2]),off=address-table;
    assert.equal(address%bytes,0);assert.ok(off>=0&&off+bytes<=44,'Outside eBands');
    r[d]=(bytes===4?data.readUInt32LE(off):data.readInt16LE(off))>>>0;if(bytes===4)words++;else shorts++;
   }else assert.fail('Unmodeled '+op);
  }pc=next;
 }return{registers:r,sar,pc,steps,words,shorts};
}
function symbolic(rows){
 const rs=parsed({disassembly:rows}),records=[];
 // Structural bit proof: two arbitrary independent32-bit words. Covers all
 // signed16 pairs, not just a sweep with correlated random neighbor values.
 for(const phase of[0,2]){
  const r=Array.from({length:16},(_,i)=>'R'+i),initial=r.slice(),word0=Array.from({length:32},(_,i)=>'A'+i),word1=Array.from({length:32},(_,i)=>'B'+i);r[3]=table+phase;
  let pc=helper,steps=0,loads=0;const map=new Map(rs.map(x=>[x.address,x]));
  while(true){assert.ok(++steps<15);const row=map.get(pc);assert.ok(row);const op=row.op,a=row.operands;let next=pc+row.bytes;
   if(op==='ret')break;if(op==='bbsi'){if(phase===2)next=target(row);}
   else{const d=reg(a[0]),s=reg(a[1]);
    if(op==='addi')r[d]=r[s]+Number(a[2]);
    else if(op==='l32i'){const off=r[s]+Number(a[2])-table;assert.ok(off===0||off===4);r[d]=off===0?word0:word1;loads++;}
    else if(op==='slli'){const n=Number(a[2]);r[d]=Array(n).fill(0).concat(r[s].slice(0,32-n));}
    else if(op==='srai'){const n=Number(a[2]);r[d]=r[s].slice(n).concat(Array(n).fill(r[s][31]));}
    else assert.fail(op);
   }pc=next;
  }
  const sign=x=>x.concat(Array(16).fill(x[15]));assert.deepEqual(r[11],sign(phase?word0.slice(16):word0.slice(0,16)));assert.deepEqual(r[2],sign(phase?word1.slice(0,16):word0.slice(16)));
  for(let i=0;i<16;i++)if(i!==2&&i!==11&&i!==3)assert.equal(r[i],initial[i]);assert.equal(r[3],table+phase);assert.equal(loads,phase?2:1);
  records.push({phase,first:r[11],second:r[2],loads});
 }return records;
}
function prove(functions,actual,helperDisassembly){
 const patches=findPatches(functions),a=parsed(functions.clt_compute_allocation),b=parsed(actual.clt_compute_allocation);
 for(const name of Object.keys(functions))if(name!=='clt_compute_allocation')assert.deepEqual(actual[name],functions[name]);
 assert.deepEqual(a.filter(r=>r.address<site||r.address>=end),b.filter(r=>r.address<site||r.address>=end));
 const call=b.find(r=>r.address===site),nop=b.find(r=>r.address===site+3);assert.equal(call.op,'call0');assert.equal(target(call),helper);assert.equal(nop.op,'nop');assert.equal(nop.bytes,3);
 const hs=parsed({disassembly:helperDisassembly});assert.equal(hs[0].address,helper);assert.equal(hs.at(-1).op,'ret');assert.ok(hs.at(-1).address+hs.at(-1).bytes<=helper+helperBytes);
 const combined=[...b,...hs],oldMap=new Map(a.map(r=>[r.address,r])),newMap=new Map(combined.map(r=>[r.address,r]));
 const data=Buffer.alloc(44);let cases=0;
 const check=(index,sar,seed)=>{const init=Array.from({length:16},(_,i)=>Math.imul(seed+i+1,0x45d9f3b)>>>0);init[3]=table+2*index;
  const x=execute(oldMap,init,data,sar,false),y=execute(newMap,init,data,sar,true);assert.equal(y.registers[0],site+3);y.registers[0]=x.registers[0];assert.deepEqual(y.registers,x.registers);assert.equal(y.sar,x.sar);assert.equal(y.pc,x.pc);assert.equal(y.shorts,0);assert.equal(x.shorts,2);assert.equal(y.words,index%2?2:1);cases++;};
 for(let n=0;n<65536;n++)for(const index of[0,1]){data.writeUInt32LE(Math.imul(n+1,0x45d9f3b)>>>0,0);data.writeUInt32LE(Math.imul(n+2,0x45d9f3b)>>>0,4);data.writeUInt16LE(n,2*index);check(index,n&63,n);}
 values.forEach((v,i)=>data.writeInt16LE(v,2*i));for(let i=0;i<21;i++)for(let sar=0;sar<64;sar++)check(i,sar,i*64+sar);
 return{patches,storage:storage.storageProof(functions.quant_partition),symbolic:symbolic(helperDisassembly),numeric_cases:cases,dead_return:deadReturn(functions.clt_compute_allocation),frame_bytes:192,static_ram_delta:0,stack_delta:0,contract:'a2/a11 exact signed pair; all other GPR/SAR exact except caller-dead a0. No stack in leaf. Full44-B array, all21 adjacent pairs, both word phases; no padding read.'};
}
module.exports={site,end,helper,helperBytes,table,values,definitions,tableProof,findPatches,deadReturn,execute,symbolic,prove};
