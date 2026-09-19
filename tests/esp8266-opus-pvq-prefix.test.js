const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const a=require('../tools/esp8266_opus_asm/analyze_pvq_prefix.cjs'),root=path.resolve(__dirname,'..');
test('alphabetic tree preserves ordered leaves and favours frequent results',()=>{
 const r=a.alphabetic([50,30,10,5,5]);const leaves=t=>Array.isArray(t)?[...leaves(t[1]),...leaves(t[2])]:[t];
 assert.deepEqual(leaves(r.tree),[0,1,2,3,4]);
 // Lengths1,2,3,4,4 give50+60+30+20+20=180, not190.
 assert.deepEqual(r.tree,[1,0,[2,1,[3,2,[4,3,4]]]]);assert.equal(r.cost,180);
});
test('all real U intervals pass tree/prefix verification without limiting bitrate',()=>{
 const p=JSON.parse(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-pvq-binary-candidate-v1/preflight.json')));
 const r=JSON.parse(fs.readFileSync(path.join(root,'docs/benchmarks/esp8266-opus-pvq-prefix-2026-09-19/summary.json')));
 assert.deepEqual(a.verify(p.table,r.trees.map(s=>[s.limit,s.tree])),r.unit);assert.ok(r.unit.cases>100000);
 const broken=structuredClone(r.trees[1].tree);broken[0]=1;assert.throws(()=>a.verify(p.table,[[8,broken]]));
});
test('search census is reproducible and includes metadata reads and high bitrates',()=>{
 const file=path.join(root,'docs/benchmarks/esp8266-opus-pvq-prefix-2026-09-19/summary.json'),old=JSON.parse(fs.readFileSync(file));
 assert.deepEqual(a.analyze(),old);assert.ok(old.cases.some(c=>c.name==='stereo-510'));
 assert.equal(old.prefix_storage[0].packed_byte_flash_bytes,352);assert.equal(old.prefix_storage[0].direct_word_flash_bytes,1408);
 for(const c of old.cases)for(const p of Object.values(c.prefix)){assert.equal(p.prefix_reads,c.searches);assert.ok(p.U_reads_min<=p.U_reads_max);}
 for(const c of old.cases)for(const p of Object.values(c.prefix_gated)){assert.ok(p.prefix_reads<=c.searches);assert.ok(p.U_reads_min<=p.U_reads_max);}
});
