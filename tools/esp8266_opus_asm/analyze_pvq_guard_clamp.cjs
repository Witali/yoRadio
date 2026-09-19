// Next hypothesis only. No firmware mutation or CPU claim.
// Reuse the exact long-guard fact to lower starting K by5 before prefix MIN.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./pvq_prefix_long.cjs');
const sem=require('./pvq_prefix_long_proof.cjs');
const {rows:linkedRows}=require('./frozen_reloads.cjs');
function estimate(n,k,t,index,row,prefix){
 const bound=row.values[k-4-n];assert.ok(k-n>=8&&index<bound&&t<=k-5);
 assert.ok(index>=row.values[t-n]&&index<row.values[t+1-n],'Incorrect true rank');
 const upper=prefix[(n-3)*32+Math.clz32(index)];
 const a=Math.min(k,upper),b=Math.min(k-5,upper);
 assert.ok(a>=b&&b>=t);assert.ok(row.values[b-n]<=0xffffffff);
 // Current linked leaf: initial L32I/BGEU, one ADDI before its4-insn loop.
 // MOV executes when upper<=K. Candidate would add one ADDI K,-5.
 const tail=d=>2+(d>0?1+4*d:0);
 return {saved_U_reads:a-b,saved_instructions:tail(a-t)-tail(b-t)+(upper<=k?1:0)-(upper<=k-5?1:0)-1};
}
function analyze(){
 const p=f.read(path.join(f.art('candidate'),'preflight.json')),prefix=sem.prefix(p.table);
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19'),census=f.read(path.join(dir,'summary.json'));
 const result={schema:1,recipe_sha256_lf:sourceHash(__filename),parent_elf_sha256:p.candidate_elf_sha256,
  scope:'Hypothetical one-instruction ADDI K,-5 after successful long guard; exact rank bounds and modeled instruction differences, not linked ASM or CPU. Prefix and guard otherwise unchanged. Residual indices absent in traces; retain conservative min/max.',cases:[]};
 result.linear_loop_layout=Object.fromEntries([
  ['original',p.functions.decode_pulses,0x40253334],['long_guard',p.actual_functions.decode_pulses,0x4025333a]
 ].map(([name,fn,start])=>{
  const rows=linkedRows(fn.disassembly).filter(r=>r.address>=start&&r.address<start+10);
  assert.equal(rows.length,4);assert.equal(rows.at(-1).address+rows.at(-1).bytes,start+10);
  return[name,{start,end_exclusive:start+10,start_mod4:start%4,instructions:rows.map(r=>({address:r.address,bytes:r.bytes,text:r.text})),
   scope:'Address observation only; does not establish a fetch/cache cycle penalty.'}];
 }));
 for(const c of census.cases){
  const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl'));assert.equal(hash(bytes),c.trace_sha256);
  const rows=bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  const sums={name:c.name,searches:rows.length,eligible:0,min_saved_U_reads:0,max_saved_U_reads:0,min_saved_instructions:0,max_saved_instructions:0};
  for(const[n,k,t]of rows){
   if(k-n<8||k-t<5)continue;
   const row=p.table.rows.find(r=>r.n===n),lo=row.values[t-n],hi=row.values[t+1-n]-1,points=new Set([lo,hi]);
   for(let e=0;e<=32;e++)for(const x of[2**e-1,2**e])if(x>=lo&&x<=hi)points.add(x);
   const samples=[...points].map(index=>estimate(n,k,t,index,row,prefix));sums.eligible++;
   for(const key of['saved_U_reads','saved_instructions']){
    sums['min_'+key]+=Math.min(...samples.map(s=>s[key]));sums['max_'+key]+=Math.max(...samples.map(s=>s[key]));
   }
  }
  result.cases.push(sums);
 }
 fs.writeFileSync(path.join(f.art('candidate'),'guard-clamp-hypothesis.json'),JSON.stringify(result,null,2)+'\n');
 console.table(result.cases);return result;
}
module.exports={estimate,analyze};if(require.main===module)analyze();
