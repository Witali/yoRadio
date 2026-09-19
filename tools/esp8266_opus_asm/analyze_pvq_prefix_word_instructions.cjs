// Bounds for actual linked prefix-search instructions on recorded real U ranks.
// Traces omit the residual index. Enumerate every CLZ subinterval, not one fake timing.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./pvq_prefix_word.cjs'),sem=require('./pvq_prefix_word_proof.cjs');
function analyze(){
 const p=f.read(path.join(f.art('candidate'),'preflight.json'));
 const before=sem.auditSite(p.functions.decode_pulses).filter(r=>r.address>=sem.site&&r.address<sem.done);
 const after=[...sem.auditSite(p.actual_functions.decode_pulses,true).filter(r=>r.address>=sem.site&&r.address<sem.done),...sem.checkHelper(p.helperDisassembly)];
 const prefix=sem.prefix(p.table),extra=new Map([[sem.dataAddress,sem.prefixAddress-384]]);
 for(let off=0;off<prefix.length;off+=4)extra.set(sem.prefixAddress+off,prefix.readUInt32LE(off));
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19'),census=f.read(path.join(dir,'summary.json'));
 const result={schema:1,recipe_sha256_lf:sourceHash(__filename),candidate_elf_sha256:p.candidate_elf_sha256,
 scope:'Instruction and load min/max over all residual indices consistent with each recorded answer. Includes pointer-literal and direct-word-prefix loads separately. Not cycles/cache timing; actual residual indices are not in these traces.',cases:[]};
 for(const c of census.cases){
   const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl'));assert.equal(hash(bytes),c.trace_sha256);
   const rows=bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
   const sums={old_instructions:0,min_instructions:0,max_instructions:0,old_U_reads:0,min_U_reads:0,max_U_reads:0,literal_reads:0,prefix_word_reads:0,helper_calls:0,short_linear:0};
   const longGuard={hypothetical:true,condition:'K-N>=8 && index<U(N,K-4)',prefix_calls:0,extra_U_reads:0};
   for(const[n,k,t]of rows){
     const row=p.table.rows.find(r=>r.n===n),lo=row.values[t-n],hi=row.values[t+1-n]-1;
     const memory=new Map([...extra,...row.values.slice(0,k-n+1).map((v,i)=>[row.address+4*(n+i),v])]);
     const points=new Set([lo,hi]);
     for(let e=0;e<=32;e++)for(const x of[2**e-1,2**e])if(x>=lo&&x<=hi)points.add(x);
     const r=Array(16).fill(0);r[2]=lo;r[5]=k;r[6]=row.address;r[9]=(k<<16)>>>0;r[11]=row.values[0];r[12]=k;r[13]=n;r[15]=row.address+4*(k+1);
     const old=sem.emulate(before,r,memory);assert.equal(old.registers[12],t);
     sums.old_instructions+=old.steps;sums.old_U_reads+=old.reads.length;
     const observations=[];
     for(const index of points){
       r[2]=index;const out=sem.emulate(after,r,memory);assert.equal(out.registers[12],t);assert.equal(out.sar,0);
       const literal=out.reads.filter(a=>a===sem.dataAddress).length;
       const metadata=out.reads.filter(a=>a>=sem.prefixAddress&&a<sem.prefixAddress+sem.prefixBytes).length;
       assert.equal(literal,k-n>=8?1:0);assert.equal(metadata,literal);
       observations.push({steps:out.steps,U_reads:out.reads.length-literal-metadata});
     }
     sums.min_instructions+=Math.min(...observations.map(x=>x.steps));sums.max_instructions+=Math.max(...observations.map(x=>x.steps));
     sums.min_U_reads+=Math.min(...observations.map(x=>x.U_reads));sums.max_U_reads+=Math.max(...observations.map(x=>x.U_reads));
     if(k-n>=8){
       sums.literal_reads++;sums.prefix_word_reads++;sums.helper_calls++;
       const bound=row.values[k-4-n];assert.equal(lo<bound,k-t>=5);assert.equal(hi<bound,k-t>=5);
       longGuard.extra_U_reads++;if(k-t>=5)longGuard.prefix_calls++;
     }else sums.short_linear++;
   }
   assert.equal(rows.length,c.counts.rows);assert.equal(sums.old_U_reads,c.counts.table_probes.linear);
   result.cases.push({name:c.name,searches:rows.length,...sums,hypothetical_long_guard:longGuard,
     min_total_reads:sums.min_U_reads+sums.literal_reads+sums.prefix_word_reads,
     max_total_reads:sums.max_U_reads+sums.literal_reads+sums.prefix_word_reads});
 }
 fs.writeFileSync(path.join(f.art('candidate'),'instruction-census.json'),JSON.stringify(result,null,2)+'\n');console.table(result.cases);return result;
}
module.exports={analyze};if(require.main===module)analyze();
