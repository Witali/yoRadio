// Host-only search design. No entropy format change or MCU speed claim.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./pvq_binary.cjs');
function alphabetic(weights){
 const memo=new Map();
 function solve(lo,hi){
  if(lo===hi)return{cost:0,tree:lo};
  const key=lo+':'+hi;if(memo.has(key))return memo.get(key);
  const total=weights.slice(lo,hi+1).reduce((a,b)=>a+b,0);let best;
  for(let split=lo+1;split<=hi;split++){
   const left=solve(lo,split-1),right=solve(split,hi),cost=total+left.cost+right.cost;
   if(!best||cost<best.cost)best={cost,tree:[split,left.tree,right.tree]};
  }
  memo.set(key,best);return best;
 }
 return solve(0,weights.length-1);
}
const value=(row,k)=>{assert.ok(k>=row.n&&k<row.n+row.values.length);return row.values[k-row.n];};
function linear(row,k,index){let reads=0,p;do{p=value(row,k);reads++;if(p<=index)return{k,p,reads};k--;}while(true);}
function treeSearch(row,k,index,tree,limit){
 if(k-row.n<limit)return{...linear(row,k,index),fallback:true};
 let node=tree,reads=0,lower=row.n,p=value(row,row.n);
 while(Array.isArray(node)){
  const at=k-node[0]+1,q=value(row,at);reads++;
  if(index>=q){lower=at;p=q;node=node[1];}else node=node[2];
 }
 if(node===limit){const tail=linear(row,k-limit,index);return{...tail,reads:reads+tail.reads,fallback:false};}
 assert.equal(lower,k-node,'Leaf needs an extra unaccounted table load');
 return{k:lower,p,reads,fallback:false};
}
function prefixTable(row,bits){
 const bins=1<<bits,result=[];
 for(let e=0;e<32;e++)for(let m=0;m<bins;m++){
  const high=e<bits?0:(bins+m+1)*2**(e-bits)-1;
  let k=row.n;while(k+1<row.n+row.values.length&&value(row,k+1)<=high)k++;
  result.push(k);
 }
 return result;
}
function prefixSearch(row,k,index,bits,table,gate=0){
 if(k-row.n<gate)return{...linear(row,k,index),prefix_reads:0};
 assert.ok(index>=value(row,row.n)&&index<=0xffffffff);
 const e=Math.floor(Math.log2(index)),bins=1<<bits;assert.ok(e>=bits);
 const mantissa=Math.floor(index/2**(e-bits))-bins,key=e*bins+mantissa;
 assert.ok(key>=0&&key<table.length);
 return{...linear(row,Math.min(k,table[key]),index),prefix_reads:1};
}
function verify(tables,trees){
 let cases=0;
 for(const row of tables.rows.filter(r=>r.values.length>1)){
  const prefixes=[0,1,2,3].map(b=>prefixTable(row,b));
  for(let k=row.n;k<row.n+row.values.length-1;k++)for(let target=row.n;target<=k;target++)
   for(const index of new Set([value(row,target),value(row,target+1)-1])){
    const expected={k:target,p:value(row,target)};
    for(const[limit,tree]of trees){const r=treeSearch(row,k,index,tree,limit);assert.equal(r.k,expected.k);assert.equal(r.p,expected.p);}
    for(let bits=0;bits<4;bits++)for(const gate of[0,8,16]){const r=prefixSearch(row,k,index,bits,prefixes[bits],gate);assert.equal(r.k,expected.k);assert.equal(r.p,expected.p);}
    cases++;
   }
 }
 return{cases,scope:'Every interval endpoint of all stored U rows with K+1 available. Table lookup upper bounds are monotone within each answer interval. Exact rank-search results; not a new decoder/ASM/PCM timing test.'};
}
function analyze(){
 const tables=f.read(path.join(f.art('candidate'),'preflight.json')).table;
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19'),summary=f.read(path.join(dir,'summary.json'));
 const corpus=summary.cases.map(c=>{const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl'));assert.equal(hash(bytes),c.trace_sha256);return{name:c.name,sha256:c.trace_sha256,rows:bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse)};});
 const specs=[4,8,16].map(limit=>{
  const weights=Array(limit+1).fill(1);
  for(const c of corpus.filter(c=>['stereo-128','stereo-192'].includes(c.name)))
   c.rows.forEach(([n,k,t],i)=>{if(i%2===0&&k-n>=limit)weights[Math.min(k-t,limit)]++;});
  const {tree,cost}=alphabetic(weights);return{limit,weights,tree,training_cost:cost,internal_nodes:limit};
 });
 const result={schema:1,recipe_sha256_lf:sourceHash(__filename),table_sha256:tables.sha256,
  scope:'Host-only ordered decision trees and exponent/mantissa prefix bounds. No bitstream change, firmware mutation, RAM claim or CPU speed measurement. Prefix counts are rigorous min/max over unknown ranks within observed answer intervals, not actual rank trace timings.',
  training:'Even-numbered searches of128/192 traces, one pseudocount per leaf; odd searches held out but from the same recordings, not independent audio.',trees:specs,
  unit:verify(tables,specs.map(s=>[s.limit,s.tree])),cases:[],prefix_storage:[0,1,2,3].map(bits=>({bits,rows:11,entries:11*32*(1<<bits),packed_byte_flash_bytes:11*32*(1<<bits),direct_word_flash_bytes:4*11*32*(1<<bits)}))};
 for(const c of corpus){
  const sums={linear:0,binary:0,trees:Object.fromEntries(specs.map(s=>[s.limit,{U_reads:0,heldout_U_reads:0,heldout_linear:0,fallback_searches:0}])),prefix:Object.fromEntries([0,1,2,3].map(b=>[b,{U_reads_min:0,U_reads_max:0,prefix_reads:0}]))};
  sums.prefix_gated={};for(const gate of[8,16])for(const bits of[0,1,2,3])sums.prefix_gated[gate+':'+bits]={gate,bits,U_reads_min:0,U_reads_max:0,prefix_reads:0};
  const cached=new Map();
  c.rows.forEach(([n,k,t],i)=>{
   const row=tables.rows.find(r=>r.n===n),lo=value(row,t),hi=value(row,t+1)-1;assert.ok(row&&k-n<row.values.length-1);
   sums.linear+=k-t+1;sums.binary+=require('./analyze_pvq_search.cjs').search(n,k,t,'binary').loads;
   for(const s of specs){const a=treeSearch(row,k,lo,s.tree,s.limit),b=treeSearch(row,k,hi,s.tree,s.limit);assert.equal(a.k,t);assert.equal(a.reads,b.reads);
    const x=sums.trees[s.limit];x.U_reads+=a.reads;if(a.fallback)x.fallback_searches++;if(i%2===1){x.heldout_U_reads+=a.reads;x.heldout_linear+=k-t+1;}}
   for(let bits=0;bits<4;bits++){
    const key=n+':'+bits;if(!cached.has(key))cached.set(key,prefixTable(row,bits));
    const a=prefixSearch(row,k,lo,bits,cached.get(key)),b=prefixSearch(row,k,hi,bits,cached.get(key));assert.equal(a.k,t);assert.equal(b.k,t);assert.ok(a.reads<=b.reads);
    sums.prefix[bits].U_reads_min+=a.reads;sums.prefix[bits].U_reads_max+=b.reads;sums.prefix[bits].prefix_reads++;
    for(const gate of[8,16]){
     const ga=prefixSearch(row,k,lo,bits,cached.get(key),gate),gb=prefixSearch(row,k,hi,bits,cached.get(key),gate),g=sums.prefix_gated[gate+':'+bits];
     assert.equal(ga.k,t);assert.equal(gb.k,t);g.U_reads_min+=ga.reads;g.U_reads_max+=gb.reads;g.prefix_reads+=ga.prefix_reads;
    }
   }
  });
  result.cases.push({name:c.name,trace_sha256:c.sha256,searches:c.rows.length,...sums});
 }
 const out=path.join(root,'docs/benchmarks/esp8266-opus-pvq-prefix-2026-09-19/summary.json');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
 console.table(result.cases.map(c=>({name:c.name,linear:c.linear,binary:c.binary,tree4:c.trees[4].U_reads,tree8:c.trees[8].U_reads,tree16:c.trees[16].U_reads,prefix0min:c.prefix[0].U_reads_min+c.prefix[0].prefix_reads,prefix0max:c.prefix[0].U_reads_max+c.prefix[0].prefix_reads,prefix2min:c.prefix[2].U_reads_min+c.prefix[2].prefix_reads,prefix2max:c.prefix[2].U_reads_max+c.prefix[2].prefix_reads})));
 return result;
}
module.exports={alphabetic,linear,treeSearch,prefixTable,prefixSearch,verify,analyze};if(require.main===module)analyze();
