const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {summarize}=require('../tools/esp8266_opus_asm/analyze_pvq_search.cjs');
const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19');
test('archived search census is reproducible from all ten unchanged pulse traces',()=>{
 const report=JSON.parse(fs.readFileSync(path.join(dir,'summary.json')));assert.equal(report.passed,true);assert.equal(report.cases.length,10);
 assert.equal(report.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/analyze_pvq_search.cjs')));
 assert.equal(report.observer_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/pvq_search_observer.c')));
 for(const c of report.cases){
  const bytes=fs.readFileSync(path.join(dir,c.name+'.jsonl')),text=bytes.toString().trim();
  assert.equal(hash(bytes),c.trace_sha256);assert.deepEqual(summarize(text?text.split(/\r?\n/).map(JSON.parse):[]),c.counts);
  assert.equal(c.pcm.exact,true);assert.equal(c.probe.arena_guards_ok,true);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes'])assert.equal(c.reference[k],c.probe[k]);
 }
 assert.equal(report.cases.find(c=>c.name==='stereo-192').counts.table_probes.binary,17587);
 assert.equal(report.cases.find(c=>c.name==='mono-24').counts.table_probes.binary,154);
});
