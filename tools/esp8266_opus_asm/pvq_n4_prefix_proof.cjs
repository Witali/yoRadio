// Differential execution of the linked LX106 instructions, not timing.
const assert=require('node:assert/strict');
const base=require('./frozen_reloads.cjs'),old=require('./pvq_n3_diff_proof.cjs');
const {n4Table}=require('./algorithm_candidates.cjs');
const {site,siteBytes,helper,helperBytes,done}=old;
const dataAddress=0x40248cb4,tableAddress=dataAddress+4,dataBytes=1048;
const clean=r=>r.text.replace(/\s+<[^>]*>$/,'').replace(/\.n(?= |$)/,'');
function auditSite(fn,candidate=false){
 if(!candidate)return old.auditSite(fn);
 // Reuse the same audited site/ABI as N3; only its dimension guard differs.
 assert.equal(fn.disassembly.split('beqi\ta13, 4').length,2);
 const changed={...fn,disassembly:fn.disassembly.replace('beqi\ta13, 4','beqi\ta13, 3')};
 old.auditSite(changed,true);return base.rows(fn.disassembly);
}
function checkHelper(text){
 const rs=base.rows(text),labels=new Map(),spec=[];
 for(const line of `
extui a3, a2, 16, 16
bnez a3, @fallback
blti a2, 64, @fallback
srli a3, a2, 9
beqz a3, @small
srli a3, a2, 8
addi a3, a3, 5
extui a11, a2, 0, 8
j @load
small:
srli a3, a2, 6
addi a3, a3, -1
extui a11, a2, 0, 6
load:
l32r a6, 40248cb4
addx4 a3, a3, a6
l32i a8, a3, 0
extui a12, a8, 0, 6
extui a3, a8, 22, 10
extui a8, a8, 6, 16
bltu a11, a3, @done
mull a3, a12, a12
slli a3, a3, 2
addi a3, a3, 2
add a8, a8, a3
addi a12, a12, 1
done:
addi a6, a13, -1
ret
fallback:
addi a6, a15, -4
fallback_loop:
l32i a8, a6, 0
addi a6, a6, -4
addi a12, a12, -1
bltu a2, a8, @fallback_loop
j @done
`.trim().split('\n')){
  if(line.endsWith(':'))labels.set(line.slice(0,-1),spec.length);else spec.push(line);
 }
 assert.equal(rs.length,spec.length);assert.equal(rs[0].address,helper);
 for(let i=1;i<rs.length;i++)assert.equal(rs[i].address,rs[i-1].address+rs[i-1].bytes);
 assert.deepEqual(rs.map(clean),spec.map(s=>s.replace(/@(\w+)/g,(_,name)=>rs[labels.get(name)].address.toString(16))));
 assert.ok(rs.at(-1).address+rs.at(-1).bytes<=helper+helperBytes);return rs;
}
function program(rows){return new Map(rows.map(row=>{
 const [op,...a]=clean(row).replaceAll(',','').split(' ');
 return [row.address,{...row,op,a,d:+a[0]?.slice(1),s:+a[1]?.slice(1),num:Number(a[2])}];
}));}
function emulate(code,initial,memory,visited=new Set()){
 const r=initial.slice(),reads=[];let pc=site,steps=0;
 while(pc!==done){
  const row=code.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<10000);visited.add(pc);
  const {op,a,d,s,num}=row;let next=pc+row.bytes;
  if(op==='addi')r[d]=(r[s]+num)>>>0;
  else if(op==='mov')r[d]=r[s];
  else if(op==='add')r[d]=(r[s]+r[+a[2].slice(1)])>>>0;
  else if(op==='addx4')r[d]=(4*r[s]+r[+a[2].slice(1)])>>>0;
  else if(op==='mull')r[d]=Math.imul(r[s],r[+a[2].slice(1)])>>>0;
  else if(op==='slli')r[d]=(r[s]<<num)>>>0;
  else if(op==='srli')r[d]=r[s]>>>num;
  else if(op==='srai')r[d]=(r[s]>>num)>>>0;
  else if(op==='extui')r[d]=(r[s]>>>num)&(2**Number(a[3])-1);
  else if(op==='l32i'||op==='l32r'){
   const at=op==='l32r'?parseInt(a[1],16):(r[s]+num)>>>0;
   assert.equal(at%4,0);assert.ok(memory.has(at),'Invalid word read '+at.toString(16));r[d]=memory.get(at);reads.push(at);
  }else if(op==='beqz'||op==='bnez'){if(op==='beqz'?r[d]===0:r[d]!==0)next=parseInt(a[1],16);}
  else if(op==='bgeu'||op==='bltu'){if(op==='bgeu'?r[d]>=r[s]:r[d]<r[s])next=parseInt(a[2],16);}
  else if(op==='beqi'||op==='blti'){if(op==='beqi'?(r[d]|0)===Number(a[1]):(r[d]|0)<Number(a[1]))next=parseInt(a[2],16);}
  else if(op==='j')next=parseInt(a[0],16);
  else if(op==='call0'){r[0]=next;next=parseInt(a[0],16);}
  else if(op==='ret')next=r[0];
  else assert.fail('Unproved instruction '+op);
  pc=next;
 }
 return {registers:r,reads,steps};
}
function prove(before,after,helperText,t){
 const a=auditSite(before),b=auditSite(after,true),h=checkHelper(helperText);
 assert.deepEqual(a.filter(r=>r.address<site||r.address>=site+siteBytes),b.filter(r=>r.address<site||r.address>=site+siteBytes));
 const ar=program(a.filter(r=>r.address>=site&&r.address<done)),br=program([...b.filter(r=>r.address>=site&&r.address<done),...h]);
 const table=n4Table(),row4=t.rows.find(r=>r.n===4);
 const mathematical=require('./analyze_n4_prefix.cjs').verify(row4);
 const extra=new Map([[dataAddress,tableAddress],...table.entries.map((v,i)=>[tableAddress+4*i,v])]);
 const visited=new Set();let intervalCases=0,denseCases=0,fastCases=0,lookupCases=0,baselineReads=0,candidateReads=0;
 function init(n,K,B,index,seed){const r=Array.from({length:16},(_,i)=>Math.imul(seed+i,0x45d9f3b)>>>0);
  r[2]=index;r[6]=B;r[9]=(K<<16)>>>0;r[11]=t.rows.find(r=>r.n===n).values[0];r[12]=K;r[13]=n;r[15]=B+4*(K+1);r[5]=K;return r;}
 function check(r,memory,tail,p){
  const x=emulate(ar,r,memory),y=emulate(br,r,memory,visited);
  for(let i=1;i<16;i++)if(i!==3)assert.equal(y.registers[i],x.registers[i],'Register a'+i);
  assert.equal(y.registers[12],tail);assert.equal(y.registers[8],p);
  if(tail===r[12]){assert.equal(x.steps,y.steps);fastCases++;}
  if(r[13]===4&&tail<r[12]&&r[2]>=64&&r[2]<65536){assert.equal(y.reads.length,3);lookupCases++;}
  else assert.equal(y.reads.length,x.reads.length);
  baselineReads+=x.reads.length;candidateReads+=y.reads.length;
 }
 for(const {n,address:B,values} of t.rows)for(let K=n;K<n+values.length-1;K++){
  const memory=new Map([...extra,...values.slice(0,K-n+1).map((v,i)=>[B+4*(n+i),v])]);
  for(let tail=n;tail<=K;tail++){
   const lo=values[tail-n],hi=values[tail-n+1]-1,points=new Set([lo,hi,lo+Math.floor((hi-lo)/2)]);
   if(n===4)for(const v of [63,64,511,512,65535,65536])if(v>=lo&&v<=hi)points.add(v);
   for(const index of points)for(const seed of [0,0xffffffff]){check(init(n,K,B,index,seed),memory,tail,lo);intervalCases++;}
  }
 }
 // Every input inside the table domain, not merely bucket boundaries.
 // Initial K=answer+1 forces a failed first probe. The separate mathematical
 // proof covers every permissible larger K; the helper never reads initial K.
 let tail=4;
 for(let index=64;index<65536;index++){
  while(row4.values[tail+1-4]<=index)tail++;
  const K=tail+1,B=row4.address,memory=new Map([...extra,...row4.values.slice(0,K-4+1).map((v,i)=>[B+4*(4+i),v])]);
  check(init(4,K,B,index,index),memory,tail,row4.values[tail-4]);denseCases++;
 }
 for(const row of h)assert.ok(visited.has(row.address),'Uncovered helper '+row.address.toString(16));
 return {interval_cases:intervalCases,dense_indices:denseCases,mathematical,fast_cases:fastCases,lookup_cases:lookupCases,
  baseline_reads:baselineReads,candidate_reads:candidateReads,helper_instructions:h.length,
  helper_bytes:h.at(-1).address+h.at(-1).bytes-helper,table_bytes:1044,stack_bytes:48,stack_delta:0,static_ram_delta:0,stores:0,sar_writes:0,
  invariant:'Initial probe and all dimensions retained. Only N=4 with 64<=index<65536 uses one exact word lookup and optional U(k+1)-U(k)=4*k*k+2. Full stored U rows and all lookup indices checked; no bitrate limit. a0/a3 are dead; other registers match at shared continuation.',
  scope:'Linked instruction differential execution; not cycle timing or proof of all possible Opus packets.'};
}
module.exports={site,siteBytes,helper,helperBytes,done,dataAddress,tableAddress,dataBytes,auditSite,checkHelper,program,emulate,prove};
