const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {summarizeSeries}=require('../tools/esp8266_opus_profile/compare_live_input.cjs');
const {readStartStatus,checkManifests}=require('../tools/esp8266_opus_profile/compare_publication.cjs');
const root=path.resolve(__dirname,'../firmware/development');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
test('saved publication A/B keeps all attempts, unconfirmed starts and failed real radio',()=>{
  const combined=read(path.join(root,'esp8266-opus-publish-on/comparison.json'));
  for(const [name,side] of [['off','reference'],['on','candidate']]) {
    const dir=path.join(root,'esp8266-opus-publish-'+name),saved=combined[side];
    const reports=Array.from({length:10},(_,i)=>read(path.join(dir,`run${i+1}.json`)));
    const summary=JSON.parse(JSON.stringify(summarizeSeries(reports)));
    for(const [key,value] of Object.entries(summary))assert.deepEqual(saved[key],value,key);
    const unconfirmed=[];
    for(let i=1;i<=10;i++) {
      const status=readStartStatus(dir,i);
      if(!status.start_confirmed)unconfirmed.push(i);
      for(const key of Object.keys(status))assert.deepEqual(saved.inputs[i-1][key],status[key]);
    }
    assert.deepEqual(saved.unconfirmed_starts,unconfirmed);
  }
  checkManifests(combined.reference.manifest,combined.candidate.manifest);
  assert.deepEqual([combined.reference.qualified,combined.candidate.qualified],[0,3]);
  assert.deepEqual(combined.reference.unconfirmed_starts,[4,8]);
  assert.equal(combined.candidate_all_windows_continuous,false);
  assert.equal(combined.all_starts_confirmed,false);
  assert.equal(read(path.join(root,'esp8266-opus-publish-on/live56.json')).result.continuity.pass,false);
  const allocation=read(path.join(root,'esp8266-opus-publish-on/live56-allocation.json'));
  assert.equal(allocation.stage,10);assert.equal(allocation.reserve_bytes,4096);
  assert.ok(allocation.free_dram<allocation.reserve_bytes);
});
