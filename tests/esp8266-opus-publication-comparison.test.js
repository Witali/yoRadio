const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {checkManifests,readStartStatus}=require('../tools/esp8266_opus_profile/compare_publication.cjs');
test('publication experiment requires matched code, input buffer and output settings',()=>{
  const a={opus_pcm_publish:false,diagnostic:true,opus_stream_test:true,
    opus_benchmark:false,opus_input_bytes:1024,source_revision:'same',dma_words_per_buffer:512};
  const b={...a,opus_pcm_publish:true,bytes:128};
  checkManifests(a,b);
  for(const [key,value] of [['source_revision','different'],['dma_words_per_buffer',480],['opus_input_bytes',2048]])
    assert.throws(()=>checkManifests(a,{...b,[key]:value}));
  assert.throws(()=>checkManifests(a,{...b,opus_pcm_publish:false}));
});

test('missing, empty and rejected start responses remain unconfirmed attempts',t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'opus-start-status-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  assert.deepEqual(readStartStatus(dir,1),{
    start_confirmed:false,start_missing:true,start_sha256_lf:null});
  for(const response of ['', 'timeout', '{"queued":false}', '{}']) {
    fs.writeFileSync(path.join(dir,'start2.log'),response);
    const result=readStartStatus(dir,2);
    assert.equal(result.start_confirmed,false);
    assert.equal(result.start_missing,false);
    assert.match(result.start_sha256_lf,/^[0-9a-f]{64}$/);
  }
  fs.writeFileSync(path.join(dir,'start3.log'),'\uFEFF{"queued":true}\r\n');
  const result=readStartStatus(dir,3);
  assert.equal(result.start_confirmed,true);
  assert.equal(result.start_missing,false);
  assert.match(result.start_sha256_lf,/^[0-9a-f]{64}$/);
});
