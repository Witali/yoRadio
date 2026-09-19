// Replay observed real PVQ searches through both linked instruction streams.
// Dynamic instructions and U loads are counts, NOT LX106 cycle estimates.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./pvq_n3_diff.cjs'),sem=require('./pvq_n3_diff_proof.cjs'),base=require('./frozen_reloads.cjs');
function analyze(){
 const p=f.read(path.join(f.art('candidate'),'preflight.json'));
 const before=sem.auditSite(p.functions.decode_pulses).filter(r=>r.address>=sem.site&&r.address<sem.done);
 const after=[...sem.auditSite(p.actual_functions.decode_pulses,true).filter(r=>r.address>=sem.site&&r.address<sem.done),...sem.checkHelper(p.helperDisassembly)];
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19'),census=f.read(path.join(dir,'summary.json'));
 const result={schema:1,recipe_sha256_lf:sourceHash(__filename),candidate_elf_sha256:p.candidate_elf_sha256,scope:'Dynamic instruction and U-row read counts on recorded real searches. No cycle/cache estimate. Index chosen at decoded interval lower boundary; every comparison has the same outcome throughout this interval.',cases:[]};
 for(const c of census.cases){
  const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl'));assert.equal(hash(bytes),c.trace_sha256);
  const rows=bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  let oldSteps=0,newSteps=0,oldReads=0,newReads=0,slower=0,faster=0,equal=0;
  for(const[n,k,t]of rows){
   const row=p.table.rows.find(r=>r.n===n);assert.ok(row);assert.ok(k>=n&&t>=n&&t<=k&&k+1-n<row.values.length);
   const mem=new Map(row.values.slice(0,k-n+1).map((v,i)=>[row.address+4*(n+i),v]));
   const r=Array(16).fill(0);r[2]=row.values[t-n];r[5]=k;r[6]=row.address;r[9]=(k<<16)>>>0;r[11]=row.values[0];r[12]=k;r[13]=n;r[15]=row.address+4*(k+1);
   const a=sem.emulate(before,r,mem),b=sem.emulate(after,r,mem);
   assert.equal(a.registers[12],t);assert.equal(b.registers[12],t);
   oldSteps+=a.steps;newSteps+=b.steps;oldReads+=a.reads.length;newReads+=b.reads.length;
   if(a.steps>b.steps)faster++;else if(a.steps<b.steps)slower++;else equal++;
  }
  assert.equal(rows.length,c.counts.rows);assert.equal(oldReads,c.counts.table_probes.linear);
  const model=f.read(path.join(root,'docs/benchmarks/esp8266-opus-pvq-n3-differences-2026-09-19/summary.json')).cases.find(v=>v.name===c.name).variants.find(v=>v.gate===3);
  assert.equal(newReads,model.proposed_reads);
  result.cases.push({name:c.name,searches:rows.length,old_instructions:oldSteps,new_instructions:newSteps,old_U_reads:oldReads,new_U_reads:newReads,
   fewer_instructions:faster,more_instructions:slower,equal_instructions:equal,
   instruction_change_percent:oldSteps?100*(newSteps/oldSteps-1):null,read_change_percent:oldReads?100*(newReads/oldReads-1):null});
 }
 const output=path.join(f.art('candidate'),'instruction-census.json');fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
 console.table(result.cases);return result;
}
module.exports={analyze};if(require.main===module)analyze();
