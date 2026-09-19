// Host-only next hypothesis. Counts reads, not CPU or linked instructions.
// N=3 permits a fixed shift/domain instead of the generic NSAU/N-stride.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./pvq_prefix_word.cjs');
function bounds(row,shift){
 assert.equal(row.n,3);assert.ok([6,8].includes(shift));
 return Array.from({length:256},(_,b)=>{
  const hi=(b+1)*2**shift-1;let k=3;
  while(k+1<3+row.values.length&&row.values[k+1-3]<=hi)k++;
  return k;
 });
}
function search(row,k,index,shift,gate,table=bounds(row,shift)){
 const value=j=>{assert.ok(j>=row.n&&j<row.n+row.values.length);return row.values[j-row.n];};
 let reads=1,helper=false,metadata=0;
 if(index>=value(k))return{k,reads,metadata,helper};
 const originalK=k;k--;
 if(row.n===3&&originalK>=gate){
  helper=true;
  if(index<256*2**shift){
   k=Math.min(k,table[index>>>shift]);metadata=2;reads+=metadata;
  }
 }
 while(true){reads++;if(value(k)<=index)return{k,reads,metadata,helper};k--;}
}
function verify(t){
 const row=t.rows.find(r=>r.n===3);let cases=0;
 for(let i=0;i<row.values.length;i++){const k=i+3;assert.equal(row.values[i],2*k*k-2*k+1);}
 const tables=Object.fromEntries([6,8].map(s=>[s,bounds(row,s)]));
 for(let k=3;k<3+row.values.length-1;k++)for(let target=3;target<=k;target++){
  const lo=row.values[target-3],hi=row.values[target+1-3]-1,points=new Set([lo,hi]);
  for(let v=Math.ceil(lo/64)*64;v<=hi;v+=64)for(const x of[v-1,v])if(x>=lo)points.add(x);
  for(const index of points)for(const shift of[6,8])for(const gate of[12,16]){
   const r=search(row,k,index,shift,gate,tables[shift]);assert.equal(r.k,target);cases++;
  }
 }
 return{cases,word_table_bytes:1024,formula:'U(3,k)=2*k*k-2*k+1',scope:'All N=3 stored answer intervals, both sides of every64-index boundary, including domain fallback. Exact rank model, not a firmware or full-decoder timing test.'};
}
function analyze(){
 const p=f.read(path.join(f.art('candidate'),'preflight.json')),row3=p.table.rows.find(r=>r.n===3);
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19'),census=f.read(path.join(dir,'summary.json'));
 const result={schema:1,recipe_sha256_lf:sourceHash(__filename),table_sha256:p.table.sha256,unit:verify(p.table),
 scope:'Next hypothesis only: keep initial U(K) fast return, specialize N=3; k-1 is a proved upper bound after failed initial probe. Fixed1024B word table, shift6/domain16384 or shift8/domain65536; no bitrate cap, ordinary search outside domain. Includes two metadata loads. No instruction/CPU/RAM-growth claim for an unbuilt ASM implementation.',cases:[]};
 for(const c of census.cases){
  const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl'));assert.equal(hash(bytes),c.trace_sha256);
  const rows=bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse),byN={};
  for(const[n,k,t]of rows){const r=byN[n]??={n,count:0,linear_reads:0};r.count++;r.linear_reads+=k-t+1;}
  const variants=[];
  for(const shift of[6,8])for(const gate of[12,16]){
   const table=bounds(row3,shift),r={shift,gate,flash_word_bytes:1024,min_reads:0,max_reads:0,helper_calls:0,min_metadata_reads:0,max_metadata_reads:0};
   for(const[n,k,t]of rows){
    if(n!==3){r.min_reads+=k-t+1;r.max_reads+=k-t+1;continue;}
    const lo=row3.values[t-3],hi=row3.values[t+1-3]-1,points=new Set([lo,hi]);
    for(let v=Math.ceil(lo/2**shift)*2**shift;v<=hi;v+=2**shift)for(const x of[v-1,v])if(x>=lo)points.add(x);
    const samples=[...points].map(i=>search(row3,k,i,shift,gate,table));assert.ok(samples.every(s=>s.k===t));
    r.min_reads+=Math.min(...samples.map(s=>s.reads));r.max_reads+=Math.max(...samples.map(s=>s.reads));
    r.min_metadata_reads+=Math.min(...samples.map(s=>s.metadata));r.max_metadata_reads+=Math.max(...samples.map(s=>s.metadata));
    assert.ok(samples.every(s=>s.helper===samples[0].helper));if(samples[0].helper)r.helper_calls++;
   }
   variants.push(r);
  }
  result.cases.push({name:c.name,trace_sha256:c.trace_sha256,linear_reads:c.counts.table_probes.linear,byN:Object.values(byN),variants});
 }
 const out=path.join(root,'docs/benchmarks/esp8266-opus-pvq-n3-buckets-2026-09-19/summary.json');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
 console.log('verified',result.unit.cases);console.table(result.cases.flatMap(c=>c.variants.map(v=>({name:c.name,old:c.linear_reads,...v}))));return result;
}
module.exports={bounds,search,verify,analyze};if(require.main===module)analyze();
