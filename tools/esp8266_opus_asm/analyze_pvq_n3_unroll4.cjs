// Next hypothesis only: delay K updates until a group of four, keep exact p.
// Instruction counts assume the written scalar Xtensa operations; unassembled.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./pvq_n3_diff.cjs');
const scalar=require('./analyze_pvq_n3_differences.cjs');
const output=path.join(root,'docs/benchmarks/esp8266-opus-pvq-n3-unroll4-2026-09-19/summary.json');
function search(row,k,index){
 assert.equal(row.n,3);assert.ok(k>=3&&k<row.values.length+3);
 assert.ok(index>=row.values[0]);let p=row.values[k-3];
 if(index>=p)return{k,p,instructions:0};
 let delta=4*(k-1),instructions=2;
 outer:while(true){
  for(let step=1;step<=4;step++){
   assert.ok(p>=delta);p=(p-delta)>>>0;instructions++; // SUB
   assert.equal(p,row.values[k-step-3]);
   if(step<4){
    instructions++; // BGEU exitN
    if(index>=p){k-=step;instructions+=2;break outer;} // ADDI K / J done
    delta-=4;instructions++; // ADDI delta
   }else{
    delta-=4;k-=4;instructions+=3; // ADDI delta / ADDI K / BLTU group
    if(index>=p)break outer;
   }
  }
 }
 return{k,p,instructions:instructions+2}; // shared ADDI N-1 / RET
}
function analyze(){
 const p=f.read(path.join(f.art('candidate'),'preflight.json')),row=p.table.rows.find(r=>r.n===3);
 let cases=0;
 for(let k=3;k<row.values.length+2;k++)for(let t=3;t<=k;t++)for(const i of[row.values[t-3],row.values[t-2]-1]){
  const a=scalar.search(row,k,i),b=search(row,k,i),d=k-t,q=Math.floor(d/4),r=d%4;
  assert.equal(b.k,a.k);assert.equal(b.p,a.p);
  assert.equal(b.instructions,d?4+13*q+(r?3*(r-1)+4:0):0);cases++;
 }
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19');
 const result={recipe_sha256_lf:sourceHash(__filename),table_sha256:p.table.sha256,unit_cases:cases,
  scope:'Host exact K/p model, unassembled instruction-count hypothesis. Same CALL/site overhead as N3 diff. No CPU/cache, stack or complete PCM proof. No new lookup table. All other N unchanged.',cases:[]};
 for(const c of f.read(path.join(dir,'summary.json')).cases){
  const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl'));assert.equal(hash(bytes),c.trace_sha256);
  let calls=0,steps=0,old=0,next=0;
  for(const[n,k,t]of bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse))if(n===3&&k>t){
   const lo=row.values[t-3],hi=row.values[t-2]-1,a=search(row,k,lo),b=search(row,k,hi);
   assert.deepEqual(a,b);calls++;steps+=k-t;old+=4+4*(k-t);next+=a.instructions;
  }
  result.cases.push({name:c.name,trace_sha256:c.trace_sha256,calls,steps,old_helper_instructions:old,new_helper_instructions:next,reduction:old-next});
 }
 return result;
}
module.exports={search,analyze,output};
if(require.main===module){const r=analyze();fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(r,null,2)+'\n');console.log(r.unit_cases);console.table(r.cases);}
