const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/pvq_prefix_long.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_prefix_long_proof.cjs');
const model=require('../tools/esp8266_opus_asm/analyze_pvq_guard_clamp.cjs');
test('hypothetical clamp stays above true rank at every U/CLZ interval and rejects an unproved guard',()=>{
 const p=f.read(path.join(f.art('candidate'),'preflight.json')),prefix=sem.prefix(p.table);let cases=0;
 for(const row of p.table.rows){const n=row.n;
  for(let k=n+8;k<n+row.values.length-1;k++)for(let t=n;t<=k-5;t++){
   const lo=row.values[t-n],hi=row.values[t+1-n]-1,points=new Set([lo,hi]);
   for(let e=0;e<=32;e++)for(const x of[2**e-1,2**e])if(x>=lo&&x<=hi)points.add(x);
   for(const index of points){const r=model.estimate(n,k,t,index,row,prefix);assert.ok(r.saved_U_reads>=0&&r.saved_U_reads<=5);assert.ok(r.saved_instructions>=-1);cases++;}
  }
 }
 assert.ok(cases>50000);
 const row=p.table.rows[0],n=row.n,k=n+8;
 assert.throws(()=>model.estimate(n,k,k-4,row.values[k-4-n],row,prefix));
});
test('saved modeled bounds reproduce from all ten trace files without claiming measured speed',()=>{
 const file=path.join(f.art('candidate'),'guard-clamp-hypothesis.json'),saved=f.read(file);
 assert.deepEqual(model.analyze(),saved);
 const c=saved.cases.find(c=>c.name==='stereo-192');assert.equal(c.eligible,1306);
 assert.match(saved.scope,/not linked ASM or CPU/);assert.ok(c.min_saved_instructions>0);
 assert.equal(saved.linear_loop_layout.original.start_mod4,0);
 assert.equal(saved.linear_loop_layout.long_guard.start_mod4,2);
 assert.ok(Object.values(saved.linear_loop_layout).every(x=>x.instructions.length===4));
});
