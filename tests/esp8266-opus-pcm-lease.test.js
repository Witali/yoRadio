const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {sha256}=require('../tools/esp8266_opus_profile/fixtures.cjs');
const {run}=require('../tools/esp8266_opus_profile/run_block_regressions.cjs');
const profile=path.join(__dirname,'../tools/esp8266_opus_profile');
test('leased PCM keeps exact samples with delayed consumption, bounded memory and failure cleanup',()=>{
  const before=JSON.parse(fs.readFileSync(path.join(profile,'block-results.json')));
  const after=JSON.parse(fs.readFileSync(path.join(profile,'leased-results.json')));
  assert.equal(after.passed,true);assert.equal(after.leased,true);assert.ok(after.cases.length>=11);
  assert.equal(after.cases.length,before.cases.length);
  for(const [file,hash] of Object.entries(after.source_sha256_lf))
    assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n'))),hash,file);
  assert.equal(after.probe_sha256_lf,sha256(Buffer.from(fs.readFileSync(path.join(profile,'leased_probe.c'),'utf8').replace(/\r\n/g,'\n'))));
  for(const c of after.cases) {
    const b=before.cases.find(x=>x.name===c.name);assert.ok(b,c.name);
    assert.equal(c.input_sha256,b.input_sha256);
    assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);
    assert.equal(c.pcm.actual_pcm_sha256,b.pcm.actual_pcm_sha256);
    assert.equal(c.result.pcm_bytes,3840);assert.equal(c.result.allocations,0);
    for(const key of ['guards','sink_mutation','reentry_rejected','delayed_consumer','failure_cleanup'])
      assert.equal(c.result[key],true,key);
    assert.equal(c.result.scratch_bytes,b.result.scratch_bytes);
    assert.equal(c.result.scratch_words,b.result.scratch_words);
  }
  assert.ok(after.cases.some(c=>c.packet_durations_ms['120']>0));
});
test('leased PCM full corpus is reproducible',{
  skip:process.env.OPUS_LEASE_TEST!=='1'&&'Set OPUS_LEASE_TEST=1 for full decoder comparison',timeout:240000
},async()=>{ assert.equal((await run({leased:true,
  output:path.join(__dirname,'../.build/opus-block-regression/reproduced-leases.json')})).passed,true); });
