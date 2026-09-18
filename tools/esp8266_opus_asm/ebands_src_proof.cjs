// Authenticate the linked leaf and prove exact signed extraction plus dead SAR.
// No cycle claim: more instructions can still only be judged on the board.
const assert=require('node:assert/strict');
const {parsed}=require('./bits_fifth_proof.cjs'),{target}=require('./partition_frozen_proof.cjs');
const pair=require('./ebands_pair_proof.cjs'),more=require('./ebands_more_proof.cjs');
const quant=require('./ebands_quant_proof.cjs');
const helper=0x4024dd48,helperBytes=36,site=0x40248418;
const tableProof=pair.tableProof,definitions=()=>'';
function storageBytesProof(elf){return quant.sharedLeaf(elf);}
function deadSar(functions){
 const rows=parsed(functions.clt_compute_allocation),at=pc=>rows.find(r=>r.address===pc);
 assert.equal(at(site).op,'call0');assert.equal(target(at(site)),helper);
 const expected=['nop','sub a3, a3, a2','slli a2, a3, 1','add a2, a2, a3','ssl a4'];
 let pc=site+3;const visited=[];
 for(const text of expected){const r=at(pc);assert.ok(r);assert.equal(r.text,text);visited.push(pc);pc+=r.bytes;}
 // Existing accepted callers cannot acquire an unnoticed second entry.
 const incoming=[];
 for(const [name,fn]of Object.entries(functions))for(const r of parsed(fn))if(/^b|^j$|^call0$/.test(r.op)){
  const t=target(r);if(t>=helper&&t<helper+helperBytes){assert.equal(t,helper);incoming.push({name,pc:r.address});}
 }
 assert.deepEqual(incoming,[{name:'clt_compute_allocation',pc:site}]);
 return{incoming,visited,overwrite:visited.at(-1),rule:'Only existing accepted init caller; NOP/SUB/SLLI/ADD do not read SAR before SSL overwrites it. No new callers.'};
}
function findPatches(functions){deadSar(functions);return[{address:helper,bytes:helperBytes}];}
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
function shape(text){
 const rows=parsed({disassembly:text});
 assert.equal(rows[0].address,helper);
 assert.deepEqual(rows.map(r=>r.text.replace(/\.n(?=\s|$)/,'')),['ssa8l a5','movi a2, -4','addi a3, a5, 2','and a3, a3, a2','and a2, a5, a2','l32i a3, a3, 0','l32i a2, a2, 0','src a3, a3, a2','slli a2, a3, 16','srai a2, a2, 16','srai a3, a3, 16','ret']);
 assert.equal(rows.at(-1).address+rows.at(-1).bytes,helper+31);
 for(let i=1;i<rows.length;i++)assert.equal(rows[i].address,rows[i-1].address+rows[i-1].bytes);
 return rows;
}
function execute(rows,initial,data,sar){
 const r=initial.slice(),loads=[];
 assert.ok(r[5]>=pair.table&&r[5]<=pair.table+40&&r[5]%2===0,'Invalid pair pointer');
 for(const row of rows){const a=row.operands,op=row.op;
  if(op==='ret')return{registers:r,sar,loads,steps:rows.length};
  if(op==='ssa8l'){sar=(r[reg(a[0])]&3)*8;continue;}
  const d=reg(a[0]);
  if(op==='movi'){r[d]=Number(a[1])>>>0;continue;}
  const s=reg(a[1]);
  if(op==='addi')r[d]=(r[s]+Number(a[2]))>>>0;
  else if(op==='and')r[d]=(r[s]&r[reg(a[2])])>>>0;
  else if(op==='l32i'){const address=r[s]+Number(a[2]),off=address-pair.table;assert.equal(address%4,0);assert.ok(off>=0&&off+4<=44,'Outside eBands');loads.push(address);r[d]=data.readUInt32LE(off);}
  else if(op==='src'){assert.ok(sar===0||sar===16);const low=r[reg(a[2])];r[d]=sar===0?low:((low>>>sar)|(r[s]<<(32-sar)))>>>0;}
  else if(op==='slli')r[d]=(r[s]<<Number(a[2]))>>>0;
  else if(op==='srai')r[d]=(r[s]>>Number(a[2]))>>>0;
  else assert.fail('Unmodelled '+op);
 }
 assert.fail('No return');
}
function symbolic(text){
 shape(text);
 // After exact opcode validation, interpret every bit of SRC followed by
 // SLLI/SRAI. A/B are independent arbitrary words, not test-fixture values.
 const A=Array.from({length:32},(_,i)=>'A'+i),B=Array.from({length:32},(_,i)=>'B'+i),records=[];
 for(const phase of[0,2]){
  const shift=phase*8,high=phase?B:A,joined=A.concat(high).slice(shift,shift+32);
  const sign=x=>x.concat(Array(16).fill(x[15]));
  const low=sign(joined.slice(0,16)),hi=sign(joined.slice(16));
  assert.deepEqual(low,sign(phase?A.slice(16):A.slice(0,16)));
  assert.deepEqual(hi,sign(phase?B.slice(0,16):A.slice(16)));
  records.push({phase,sar:shift,first:low,second:hi,loads:2});
 }return records;
}
function prove(functions,actual,helperDisassembly){
 assert.deepEqual(actual,functions,'No caller/other reachable code is changed');
 const rows=shape(helperDisassembly),data=Buffer.alloc(44);let numeric=0;
 const check=(index,sar,seed)=>{
  const r=Array.from({length:16},(_,j)=>Math.imul(seed+j+1,0x45d9f3b)>>>0);r[5]=pair.table+2*index;
  const out=execute(rows,r,data,sar),expected=r.slice();expected[2]=data.readInt16LE(index*2)>>>0;expected[3]=data.readInt16LE(index*2+2)>>>0;
  assert.deepEqual(out.registers,expected);assert.equal(out.sar,(index&1)*16);assert.equal(out.loads.length,2);numeric++;
 };
 for(let n=0;n<65536;n++)for(const index of[0,1]){data.writeUInt32LE(Math.imul(n+1,0x45d9f3b)>>>0,0);data.writeUInt32LE(Math.imul(n+2,0x45d9f3b)>>>0,4);data.writeUInt16LE(n,index*2);check(index,n&63,n);}
 pair.values.forEach((v,i)=>data.writeInt16LE(v,2*i));for(let i=0;i<21;i++)for(let sar=0;sar<64;sar++)check(i,sar,i*64+sar);
 return{patches:findPatches(functions),symbolic:symbolic(helperDisassembly),numeric_cases:numeric,dead_sar:deadSar(functions),provenance:more.provenance(functions.clt_compute_allocation),live_bytes:31,padding_bytes:5,frame_bytes:192,static_ram_delta:0,stack_delta:0,operations:{candidate_instructions:[12,12],candidate_word_loads:[2,2],accepted_instructions:[6,9],accepted_word_loads:[1,2]},contract:'Full signed16 pair; two aligned loads within44B, all21 pairs/all64 initial SAR. All GPR exact, SAR overwritten before next use. ISA SRC=(high||low)>>SAR, SSA8L=8*(p&3). Timing requires physical A/B/A.'};
}
module.exports={helper,helperBytes,site,definitions,tableProof,storageBytesProof,deadSar,findPatches,shape,execute,symbolic,prove};
