const test=require('node:test'),assert=require('node:assert/strict');
const {checkManifests}=require('../tools/esp8266_opus_profile/compare_publication.cjs');
test('publication experiment requires matched code, input buffer and output settings',()=>{
  const a={opus_pcm_publish:false,diagnostic:true,opus_stream_test:true,
    opus_benchmark:false,opus_input_bytes:1024,source_revision:'same',dma_words_per_buffer:512};
  const b={...a,opus_pcm_publish:true,bytes:128};
  checkManifests(a,b);
  for(const [key,value] of [['source_revision','different'],['dma_words_per_buffer',480],['opus_input_bytes',2048]])
    assert.throws(()=>checkManifests(a,{...b,[key]:value}));
  assert.throws(()=>checkManifests(a,{...b,opus_pcm_publish:false}));
});
