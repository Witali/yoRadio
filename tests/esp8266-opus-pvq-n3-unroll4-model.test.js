const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const m=require('../tools/esp8266_opus_asm/analyze_pvq_n3_unroll4.cjs'),f=require('../tools/esp8266_opus_asm/pvq_n3_diff.cjs');
test('unrolled K update exits at every phase without losing p or crossing U(3,3)',()=>{
 const row=f.read(path.join(f.art('candidate'),'preflight.json')).table.rows.find(r=>r.n===3);
 for(let d=0;d<=16;d++){
  const r=m.search(row,20,row.values[20-d-3]);assert.equal(r.k,20-d);assert.equal(r.p,row.values[20-d-3]);
 }
 assert.equal(m.search(row,4,13).k,3);
 assert.throws(()=>m.search(row,4,12));
});
test('saved unroll4 hypothesis reproduces every stored interval and all10 traces',()=>{
 const r=m.analyze();assert.deepEqual(r,JSON.parse(fs.readFileSync(m.output,'utf8')));
 assert.equal(r.unit_cases,30102);assert.equal(r.cases.length,10);
 assert.equal(r.cases.find(c=>c.name==='stereo-192').reduction,3993);
 assert.equal(r.cases.find(c=>c.name==='stereo-128').reduction,1184);
 assert.match(r.scope,/unassembled/);
});
