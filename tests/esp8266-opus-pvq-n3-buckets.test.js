const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/pvq_prefix_word.cjs'),m=require('../tools/esp8266_opus_asm/analyze_pvq_n3_buckets.cjs');
const {root}=require('../tools/esp8266_opus_asm/export.cjs');
test('N3 bucket model covers all intervals, domain edges and rejected corrupt formula',()=>{
 const p=f.read(path.join(f.art('candidate'),'preflight.json')),v=m.verify(p.table);assert.ok(v.cases>100000);
 const bad=structuredClone(p.table);bad.rows[0].values[4]++;assert.throws(()=>m.verify(bad));
 const row=p.table.rows[0],tab=m.bounds(row,6);
 assert.equal(m.search(row,100,16383,6,12,tab).metadata,2);
 assert.equal(m.search(row,100,16384,6,12,tab).metadata,0);
 assert.equal(m.search(row,100,row.values[100-3],6,12,tab).helper,false);
});
test('saved read-only counts reproduce all traces without promising MCU acceleration',()=>{
 const saved=f.read(path.join(root,'docs/benchmarks/esp8266-opus-pvq-n3-buckets-2026-09-19/summary.json'));
 assert.deepEqual(m.analyze(),saved);assert.match(saved.scope,/No instruction\/CPU/);
 const c=saved.cases.find(c=>c.name==='stereo-192');assert.equal(c.linear_reads,24259);
 assert.equal(c.byN.find(c=>c.n===3).linear_reads,7030);assert.equal(c.byN.find(c=>c.n===4).linear_reads,7003);
 assert.ok(c.variants.every(v=>v.flash_word_bytes===1024));
});
