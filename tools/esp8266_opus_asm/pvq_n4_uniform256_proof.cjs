// Linked-ISA proof for uniform buckets; reuse the already tested ISA engine,
// not the previous candidate's algorithm. No CPU speed inference is made.
const assert=require('node:assert/strict'),base=require('./frozen_reloads.cjs');
const old=require('./pvq_n4_prefix_proof.cjs');
const {site,siteBytes,helper,helperBytes,done,dataAddress,tableAddress,auditSite,program,emulate}=old;
const dataBytes=1024;
function uniformTable(){
 const u=require('./algorithm_candidates.cjs').n4Table().u,entries=[];
 for(let lo=256;lo<65536;lo+=256){
  let k=4;while(u(k+1)<=lo)k++;let last=k;while(u(last+1)<=lo+255)last++;
  assert.ok(last-k<=1);const p=u(k),cut=Math.min(256,u(k+1)-lo);
  assert.ok(k<=37&&p<65536&&cut>0&&cut<=256);entries.push((k|(p<<6)|(cut<<22))>>>0);
 }
 assert.equal(entries.length,255);return {u,entries};
}
function mathematical(row){
 const {u,entries}=uniformTable();assert.equal(row.n,4);row.values.forEach((p,i)=>assert.equal(p,u(i+4)));
 let k=4,pairs=0,indices=0;
 for(let index=256;index<65536;index++){
  while(row.values[k+1-4]<=index)k++;
  const w=entries[(index>>>8)-1];let rank=w&63,p=(w>>>6)&65535;
  if((index&255)>=(w>>>22)){p+=4*rank*rank+2;rank++;}
  assert.equal(rank,k);assert.equal(p,row.values[k-4]);indices++;
  for(let initial=k+1;initial<row.n+row.values.length-1;initial++){assert.ok(row.values[initial-4]>index);pairs++;}
 }
 return {indices,initial_K_pairs:pairs,entries:entries.length,flash_data_bytes:1020,domain:[256,65535]};
}
function checkHelper(text){
 const rs=base.rows(text),labels=new Map(),spec=[];
 for(const line of `
extui a3, a2, 16, 16
bnez a3, @fallback
srli a3, a2, 8
beqz a3, @fallback
extui a11, a2, 0, 8
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
 const clean=r=>r.text.replace(/\s+<[^>]*>$/,'').replace(/\.n(?= |$)/,'');
 assert.deepEqual(rs.map(clean),spec.map(s=>s.replace(/@(\w+)/g,(_,name)=>rs[labels.get(name)].address.toString(16))));
 assert.ok(rs.at(-1).address+rs.at(-1).bytes<=helper+helperBytes);return rs;
}
function prove(before,after,helperText,t){
 const a=auditSite(before),b=auditSite(after,true),h=checkHelper(helperText);
 assert.deepEqual(a.filter(r=>r.address<site||r.address>=site+siteBytes),b.filter(r=>r.address<site||r.address>=site+siteBytes));
 const ar=program(a.filter(r=>r.address>=site&&r.address<done)),br=program([...b.filter(r=>r.address>=site&&r.address<done),...h]);
 const row4=t.rows.find(r=>r.n===4),math=mathematical(row4),entries=uniformTable().entries;
 const extra=new Map([[dataAddress,tableAddress-4],...entries.map((v,i)=>[tableAddress+i*4,v])]);
 const visited=new Set();let intervalCases=0,denseCases=0,fastCases=0,lookupCases=0,baselineReads=0,candidateReads=0;
 function init(n,K,B,index,seed){const r=Array.from({length:16},(_,i)=>Math.imul(seed+i,0x45d9f3b)>>>0);
  r[2]=index;r[6]=B;r[9]=(K<<16)>>>0;r[11]=t.rows.find(r=>r.n===n).values[0];r[12]=K;r[13]=n;r[15]=B+4*(K+1);r[5]=K;return r;}
 function check(r,memory,tail,p){
  const x=emulate(ar,r,memory),y=emulate(br,r,memory,visited);
  for(let i=1;i<16;i++)if(i!==3)assert.equal(y.registers[i],x.registers[i],'Register a'+i);
  assert.equal(y.registers[12],tail);assert.equal(y.registers[8],p);
  if(tail===r[12]){assert.equal(x.steps,y.steps);fastCases++;}
  if(r[13]===4&&tail<r[12]&&r[2]>=256&&r[2]<65536){
   assert.equal(y.reads.length,3);assert.equal(y.reads[1],dataAddress);
   assert.ok(y.reads[2]>=tableAddress&&y.reads[2]<tableAddress+1020);lookupCases++;
  }else assert.deepEqual(y.reads,x.reads);
  baselineReads+=x.reads.length;candidateReads+=y.reads.length;
 }
 for(const {n,address:B,values} of t.rows)for(let K=n;K<n+values.length-1;K++){
  const memory=new Map([...extra,...values.slice(0,K-n+1).map((v,i)=>[B+4*(n+i),v])]);
  for(let tail=n;tail<=K;tail++){
   const lo=values[tail-n],hi=values[tail-n+1]-1,points=new Set([lo,hi,lo+Math.floor((hi-lo)/2)]);
   if(n===4)for(const v of [63,64,255,256,511,512,65535,65536])if(v>=lo&&v<=hi)points.add(v);
   for(const index of points)for(const seed of [0,0xffffffff]){check(init(n,K,B,index,seed),memory,tail,lo);intervalCases++;}
  }
 }
 let tail=4;
 // Include every lower-domain fallback input too: no accidental table[0]
 // read may occur for the legal original index>=U(4,4)=63.
 for(let index=63;index<65536;index++){
  while(row4.values[tail+1-4]<=index)tail++;
  const K=tail+1,B=row4.address,memory=new Map([...extra,...row4.values.slice(0,K-4+1).map((v,i)=>[B+4*(4+i),v])]);
  check(init(4,K,B,index,index),memory,tail,row4.values[tail-4]);denseCases++;
 }
 for(const row of h)assert.ok(visited.has(row.address),'Uncovered helper '+row.address.toString(16));
 return {interval_cases:intervalCases,dense_indices_including_fallback:denseCases,mathematical:math,fast_cases:fastCases,lookup_cases:lookupCases,
  baseline_reads:baselineReads,candidate_reads:candidateReads,helper_instructions:h.length,helper_bytes:h.at(-1).address+h.at(-1).bytes-helper,
  table_bytes:1020,stack_bytes:48,stack_delta:0,static_ram_delta:0,stores:0,sar_writes:0,
  invariant:'Unchanged initial probe/all dimensions. N=4 and 256<=index<65536: one uniform bucket word; literal base=table-4 so index>>8 addresses bucket-1. Zero bucket rejected before load. Exact p/rank and all live registers; lower/higher indices keep original search, not a bitrate cap.',
  scope:'Linked instruction differential execution, not CPU cycles or exhaustive Opus packet validation.'};
}
module.exports={site,siteBytes,helper,helperBytes,done,dataAddress,tableAddress,dataBytes,auditSite,uniformTable,mathematical,checkHelper,prove};
