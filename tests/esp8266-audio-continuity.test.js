const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {analyze}=require('../tools/test_esp8266_audio_continuity.cjs');
function sample(t) { return {host_ms:t,uptime_ms:1000+t,generation:1,
  sample_rate:48000,pcm_frames:48000+t*48,underruns:3,
  rx_bytes:3000+t*6,pcm_age_ms:10,free_heap:12000}; }
test('requires at least 20 seconds of real PCM progress and no DMA gap',()=>{
  assert.equal(analyze([sample(0),sample(20000)]).pass,true);
  assert.equal(analyze([sample(0),sample(19000)]).pass,false);
  assert.equal(analyze([sample(0),{...sample(20000),underruns:4}]).pass,false);
  assert.equal(analyze([sample(0),{...sample(20000),pcm_frames:48000}]).pass,false);
  assert.equal(analyze([sample(0),{...sample(20000),pcm_age_ms:900}]).pass,false);
});
test('failed requests, counter resets, rate/station changes are not discarded',()=>{
  assert.equal(analyze([sample(0),{...sample(22000),underruns:undefined}]).pass,false);
  assert.equal(analyze([sample(0),{error:'timeout'},sample(22000)]).pass,false);
  for(const changes of [{generation:2},{sample_rate:22050},{underruns:0}])
    assert.equal(analyze([sample(0),{...sample(22000),...changes}]).pass,false);
  assert.equal(analyze([sample(0),sample(22000)],5).pass,false);
});
test('health uses tick time and records PCM only after successful output',()=>{
  const c=fs.readFileSync('esp8266/rtos-sdk-native/main/audio_service.c','utf8');
  const cb=c.slice(c.indexOf('static bool pcm_output('),c.indexOf('static bool stream_read_exact('));
  assert.ok(cb.indexOf('result != ESP_OK')<cb.indexOf('s_pcm_frames +='));
  assert.match(c,/rx_age_ms = \(now - s_rx_tick\) \* portTICK_PERIOD_MS/);
  const web=fs.readFileSync('esp8266/rtos-sdk-native/main/web_service.c','utf8');
  assert.match(web,/register_get\("\/api\/native\/audio", audio_health_handler\)/);
});
