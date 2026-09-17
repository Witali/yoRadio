// Exact on the immutable standard eBands table, NOT a generic signed16 leaf.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,sourceHash}=require('./export.cjs'),{parsed}=require('./bits_fifth_proof.cjs');
const {target}=require('./partition_frozen_proof.cjs'),{readAt}=require('./pvq_exp2_table32_proof.cjs');
const old=require('./ebands_pair_proof.cjs');
const table=old.table,values=old.values;
const specs=[
 {site:0x402484ae,bytes:6,helper:0x4024dcc4,span:42,p:3,low:11,high:2},
 {site:0x40248418,bytes:6,helper:0x4024dd48,span:36,p:5,low:2,high:3},
 {site:0x40248585,bytes:9,helper:0x4024dd6c,span:36,p:5,low:2,high:7},
 {site:0x40248a05,bytes:6,helper:0x4024dcf0,span:36,p:4,low:10,high:3},
 {site:0x40248a21,bytes:6,helper:0x4024ddb4,span:36,p:12,low:4,high:2},
 {site:0x40248a6c,bytes:6,helper:0x4024dcb4,span:0x74,p:6,low:2,high:7}];
const regions=[{address:0x4024dcc4,bytes:42},{address:0x4024dd48,bytes:36},{address:0x4024dd6c,bytes:36},{address:0x4024dcf0,bytes:36},{address:0x4024ddb4,bytes:36},{address:0x4024dcb4,bytes:16},{address:0x4024dd14,bytes:20}];
const definitions=()=> 'ebands_u16_cross = 0x4024dd14;';
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
function originals(){
 const load=family=>{const file=path.join(root,'firmware/development/esp8266-opus-'+family+'/preflight.json');return{proof:JSON.parse(fs.readFileSync(file)),file,sha256_lf:sourceHash(file)};};
 const a=load('ebands-pair-candidate-v1'),b=load('ebands-more-candidate-v1'),c=load('ebands-final-candidate-v2');
 return {leaves:[a.proof.helperDisassembly,...b.proof.helperDisassembly,...c.proof.helperDisassembly],patches:[...a.proof.patches,...b.proof.patches,...c.proof.patches],sources:[a,b,c].map(x=>({file:path.relative(root,x.file).replaceAll('\\','/'),sha256_lf:x.sha256_lf}))};
}
function tableProof(elf){
 const p=old.tableProof(elf);assert.ok(p.values.every(v=>v>=0&&v<=100));
 return {...p,minimum:0,maximum:100,exactness_domain:'Immutable standard table only; all valid packets use unchanged entries. No new bitrate limit or custom mode removal.'};
}
function storageBytesProof(elf){
 const o=originals();
 return {sources:o.sources,regions:regions.map(({address,bytes})=>{const p=o.patches.find(p=>p.address===address&&p.bytes===bytes);assert.ok(p);assert.equal(readAt(elf,address,bytes).toString('hex'),p.after_hex,'Parent helper differs');return{address,bytes,hex:p.after_hex};})};
}
function findPatches(functions){
 const rows=parsed(functions.clt_compute_allocation),inside=a=>regions.some(r=>a>=r.address&&a<r.address+r.bytes);
 specs.forEach(s=>{const r=rows.find(r=>r.address===s.site);assert.equal(r.op,'call0');assert.equal(target(r),s.helper);});
 // Only inherited CALL0 entries may target this storage. No new placement:
 // decoder-dead origin and ABI are re-authenticated by the parent recipe.
 for(const fn of Object.values(functions))for(const r of parsed(fn)){
  assert.ok(!inside(r.address),'Unexpected instruction in helper storage');
  if(/^b|^j$|^call0$|^l32r$/.test(r.op)&&inside(target(r)))assert.ok(r.op==='call0'&&specs.some(s=>s.site===r.address&&s.helper===target(r)),'Unexpected interior entry');
 }
 return regions.map(r=>({...r}));
}
function execute(rows,s,initial,data,sar,stackValue){
 const map=rows instanceof Map?rows:new Map(rows.map(r=>[r.address,r])),r=initial.slice();let pc=s.site,steps=0,words=0,stack=0;
 assert.ok(r[s.p]>=table&&r[s.p]<=table+40&&r[s.p]%2===0,'Invalid pair pointer');
 for(const offset of[0,2])assert.ok(data.readUInt16LE(r[s.p]-table+offset)<32768,'Negative eBands value outside contract');
 while(pc!==s.site+s.bytes){assert.ok(++steps<20);const row=map.get(pc);assert.ok(row);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){assert.equal(pc,s.site);assert.equal(target(row),s.helper);r[0]=next;next=s.helper;}
  else if(op==='ret')next=r[0];else if(op==='nop'){}
  else if(op==='bbsi'){if(r[reg(a[0])]&(1<<Number(a[1])))next=target(row);}
  else{const d=reg(a[0]),src=reg(a[1]);
   if(op==='addi')r[d]=(r[src]+Number(a[2]))>>>0;
   else if(op==='slli')r[d]=(r[src]<<Number(a[2]))>>>0;else if(op==='srai')r[d]=(r[src]>>Number(a[2]))>>>0;
   else if(op==='extui'){assert.deepEqual(a.slice(2),['0','16']);r[d]=r[src]&65535;}
   else if(op==='l32i'&&src===1){assert.equal(d,14);assert.equal(Number(a[2]),68);r[d]=stackValue>>>0;stack++;}
   else if(op==='l32i'){const address=r[src]+Number(a[2]),off=address-table;assert.equal(address%4,0);assert.ok(off>=0&&off+4<=44);r[d]=data.readUInt32LE(off);words++;}
   else assert.fail('Unmodeled '+op);
  }pc=next;
 }return{registers:r,sar,pc,steps,words,stack};
}
function symbolic(disassembly,s){
 const rows=parsed({disassembly}),map=new Map(rows.map(r=>[r.address,r])),records=[];
 for(const phase of[0,2]){
  const r=Array.from({length:16},(_,i)=>'R'+i),initial=r.slice();r[s.p]=table+phase;
  const a=Array.from({length:32},(_,i)=>i===15||i===31?0:'A'+i),b=Array.from({length:32},(_,i)=>i===15||i===31?0:'B'+i);let pc=s.helper,steps=0,loads=0;
  while(true){assert.ok(++steps<15);const row=map.get(pc);assert.ok(row,'Missing symbolic successor');const op=row.op,x=row.operands;let next=pc+row.bytes;
   if(op==='ret')break;
   if(op==='bbsi'){assert.equal(reg(x[0]),s.p);assert.equal(x[1],'1');if(phase===2)next=target(row);}
   else{const d=reg(x[0]),src=reg(x[1]);
    if(op==='addi')r[d]=r[src]+Number(x[2]);
    else if(op==='l32i'){const off=r[src]+Number(x[2])-table;assert.ok(off===0||off===4);r[d]=off===0?a:b;loads++;}
    else if(op==='slli'){const n=Number(x[2]);r[d]=Array(n).fill(0).concat(r[src].slice(0,32-n));}
    else if(op==='srai'){const n=Number(x[2]);r[d]=r[src].slice(n).concat(Array(n).fill(r[src][31]));}
    else if(op==='extui'){assert.deepEqual(x.slice(2),['0','16']);r[d]=r[src].slice(0,16).concat(Array(16).fill(0));}
    else assert.fail(op);
   }pc=next;
  }
  const widen=x=>x.concat(Array(16).fill(0));assert.deepEqual(r[s.low],widen(phase?a.slice(16):a.slice(0,16)));assert.deepEqual(r[s.high],widen(phase?b.slice(0,16):a.slice(16)));
  for(let i=0;i<16;i++)if(![s.low,s.high,s.p].includes(i))assert.equal(r[i],initial[i]);assert.equal(r[s.p],table+phase);assert.equal(loads,phase?2:1);
  records.push({phase,low:r[s.low],high:r[s.high],loads,steps});
 }return records;
}
function prove(functions,actual,helperDisassembly){
 const patches=findPatches(functions),o=originals(),rows=parsed(functions.clt_compute_allocation);assert.deepEqual(actual,functions);
 const cases=[];for(let i=0;i<specs.length;i++){
  const s=specs[i],a=parsed({disassembly:o.leaves[i]}),b=parsed({disassembly:helperDisassembly[i]});
  assert.equal(a.reduce((n,r)=>n+r.bytes,0),36);assert.equal(b.reduce((n,r)=>n+r.bytes,0),30);
  const am=new Map([...rows,...a].map(r=>[r.address,r])),bm=new Map([...rows,...b].map(r=>[r.address,r])),data=Buffer.alloc(44);let numeric=0;
  const check=(j,sar,seed)=>{const regs=Array.from({length:16},(_,k)=>Math.imul(seed+k+1,0x45d9f3b)>>>0);regs[s.p]=table+2*j;const v=Math.imul(seed,0x9e3779b9),x=execute(am,s,regs,data,sar,v),y=execute(bm,s,regs,data,sar,v);assert.equal(y.steps,x.steps-1);assert.deepEqual({...y,steps:0},{...x,steps:0});numeric++;};
  for(let n=0;n<32768;n++)for(const j of[0,1]){data.writeUInt32LE((Math.imul(n+1,0x45d9f3b)&0x7fff7fff)>>>0,0);data.writeUInt32LE((Math.imul(n+2,0x45d9f3b)&0x7fff7fff)>>>0,4);data.writeUInt16LE(n,2*j);check(j,n&63,n);}
  values.forEach((v,j)=>data.writeInt16LE(v,2*j));for(let j=0;j<21;j++)for(let sar=0;sar<64;sar++)check(j,sar,j*64+sar);
  const before=symbolic(o.leaves[i],s),after=symbolic(helperDisassembly[i],s);for(let p=0;p<2;p++){assert.equal(after[p].steps,before[p].steps-1);assert.deepEqual({...after[p],steps:0},{...before[p],steps:0});}
  cases.push({site:s.site,numeric_cases:numeric,before,after});
 }
 return {patches,cases,numeric_cases:cases.reduce((n,c)=>n+c.numeric_cases,0),frame_bytes:192,static_ram_delta:0,stack_delta:0,live_bytes_before:216,live_bytes_after:180,scope:'One fewer executed instruction per helper call. All original CALL0/stack operations unchanged; exact positive15-bit domain includes entire immutable standard table. No cycle prediction.'};
}
module.exports={specs,regions,definitions,table,values,tableProof,originals,storageBytesProof,findPatches,execute,symbolic,prove};
