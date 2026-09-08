const test = require('node:test'), assert = require('node:assert/strict');
const {summarize} = require('../tools/esp8266_audio_profile/summarize_mp3_matrix.cjs');
function log(underrun = 0, nonzero = 1) {
  return [64, 128, 320].map(rate =>
    'MP3/mix/'+rate+' FLASH frame=8359 iterations=1000 callbacks=36000 decode=8000000 audio=26122448\n'+
    'MP3/mix/'+rate+' PCM nonzero='+nonzero+' rate=44100 channels=1\n'+
    'MP3/mix/'+rate+' physical wall=26045376 audio=26122448 eof=2449 underrun='+underrun+' fifo_empty=0'
  ).join('\n')+'\ncodec_ram: complete';
}
test('MP3 matrix requires every codec case and actual nonzero PCM', () => {
  assert.equal(summarize(log(), true).continuous, true);
  assert.equal(summarize(log(0, 0), true).valid, false);
  assert.throws(() => summarize(log().replaceAll('MP3/mix/320', 'other'), true), /Missing result/);
});
test('DMA starvation is not accepted even with advancing nonzero PCM', () => {
  const result = summarize(log(286), true);
  assert.equal(result.valid, true);
  assert.equal(result.continuous, false);
  assert.equal(summarize(log().replace('codec_ram: complete', ''), true).valid, false);
  assert.throws(() => summarize(log().replaceAll('physical wall=', 'missing='), true), /Missing physical/);
});
test('decode-only results never certify physical continuity', () => {
  assert.equal(summarize(log(), false).continuous, null);
  assert.equal(summarize(log()+'\nINVALID benchmark', false).valid, false);
});
