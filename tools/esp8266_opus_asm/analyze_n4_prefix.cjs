const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
const {n4Table}=require('./algorithm_candidates.cjs');
function lookup(index,table=n4Table().entries) {
 assert.ok(Number.isInteger(index)&&index>=64&&index<65536);
 const low=index<512,w=table[low?(index>>>6)-1:7+(index>>>8)-2];
 let k=w&63,p=(w>>>6)&65535;
 if((index&(low?63:255))>=w>>>22){p+=4*k*k+2;k++;}
 return {k,p};
}
function verify(row) {
 const {entries,u}=n4Table();assert.equal(row.n,4);
 row.values.forEach((v,i)=>assert.equal(v,u(i+4),'U4 polynomial'));
 let k=4,cases=0,pairs=0;
 for(let i=64;i<65536;i++) {
  while(row.values[k+1-4]<=i)k++;
  assert.deepEqual(lookup(i,entries),{k,p:row.values[k-4]});cases++;
  for(let initial=k+1;initial<row.n+row.values.length-1;initial++){assert.ok(row.values[initial-4]>i);pairs++;}
 }
 return {indices:cases,initial_K_pairs:pairs,entries:entries.length,flash_data_bytes:entries.length*4,domain:[64,65535]};
}
function analyze() {
 const pre=JSON.parse(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-pvq-prefix-word-candidate-v1/preflight.json'))),row=pre.table.rows.find(r=>r.n===4);
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19'),trace=JSON.parse(fs.readFileSync(path.join(dir,'summary.json')));
 const unit=verify(row),result={scope:'Host exact N4 rank/p proof, read-count bounds from old traces. Includes literal+word table loads; excludes instruction/cache cost. Not CPU timing or all-packet proof.',recipe_sha256:sourceHash(__filename),unit,cases:[]};
 for(const c of trace.cases) {
  const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl'));assert.equal(hash(bytes),c.trace_sha256);
  let reads=0,savedMin=0,savedMax=0,callsMin=0,callsMax=0;
  for(const [n,k,t]of bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse)) {
   reads+=k-t+1;if(n!==4||k===t)continue;
   const lo=row.values[t-4],hi=row.values[t+1-4]-1,can=lo<65536&&hi>=64,always=lo>=64&&hi<65536,delta=k-t-2;
   if(can)callsMax++;if(always)callsMin++;
   if(always){savedMin+=delta;savedMax+=delta;}else if(can){savedMin+=Math.min(0,delta);savedMax+=Math.max(0,delta);}
  }
  result.cases.push({name:c.name,trace_sha256:c.trace_sha256,baseline_reads:reads,candidate_reads_min:reads-savedMax,candidate_reads_max:reads-savedMin,calls_min:callsMin,calls_max:callsMax});
 }
 const out=path.join(root,'.build/opus-algorithm-candidates/n4-prefix/analysis.json');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));return result;
}
module.exports={lookup,verify,analyze};if(require.main===module)analyze();
