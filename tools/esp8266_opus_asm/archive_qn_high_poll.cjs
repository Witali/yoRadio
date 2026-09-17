// Preserve the accidental1.5s observation experiment without relabeling it as15s.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash}=require('./export.cjs'),f=require('./pvq_qn_table.cjs');
const {archive}=require('./report_bands.cjs'),{compare}=require('../esp8266_opus_profile/compare_raw.cjs');
function report(){
 const source=path.join(root,'.build/opus-qn-table-board-20260917'),dest=path.join(f.art('candidate'),'high-poll');fs.mkdirSync(dest,{recursive:true});
 const fixtures=f.read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json')),groups={},inputs={};
 for(const name of['before','candidate','after']){
  const ota=f.read(path.join(source,'ota-'+name+'.json')),variant=name==='candidate'?'candidate':'control';
  assert.equal(ota.pass,true);assert.equal(ota.sha256,hash(fs.readFileSync(path.join(f.art(variant),'app.bin'))));
  const rows=archive(path.join(source,name),path.join(dest,name));
  for(const {report:r}of rows){
   assert.equal(r.interval_ms,1500);assert.deepEqual(r.fixtures,fixtures);assert.equal(r.final.rounds,10);
   assert.equal(r.before.data.app_address,ota.after.app_address);assert.equal(r.after.data.app_address,ota.after.app_address);
   assert.equal(r.final.profile_stage??0,0);assert.ok(!r.final.functions);assert.ok(!r.final.division_microbenchmark);
   for(const [i,v]of r.final.results.entries()){const q=fixtures.fixtures[i];assert.equal(v.pcm_hash,q.expected_hash);assert.equal(v.samples,q.samples*10);assert.equal(v.packets,q.packet_count*10);}
  }
  groups[name]=rows.map(r=>r.report);inputs[name]=rows.map(({report,...r})=>r);
  fs.copyFileSync(path.join(source,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));
 }
 for(const n of['initial.json','restored.json','ota-restore.json'])fs.copyFileSync(path.join(source,n),path.join(dest,n));
 const result={scope:'Exploratory matched1.5-second HTTP polling. Not the established15-second CPU protocol; not eligible for the75% goal or baseline replacement.',interval_ms:1500,inputs,
  initial:compare(groups.before,groups.candidate),repeated:compare(groups.after,groups.candidate)};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={report};if(require.main===module){report();console.log('All30 high-poll attempts retained separately; no goal verdict.');}
