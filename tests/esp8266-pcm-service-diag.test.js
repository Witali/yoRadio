const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
test('app-only service diagnostics keep a separate bounded HTTP response',()=>{
 const source=fs.readFileSync('esp8266/rtos-sdk-native/main/web_service.c','utf8');
 const block=source.slice(source.indexOf('static esp_err_t audio_health_handler'));
 assert.match(block,/#if YORADIO_ESP8266_OPUS_PCM_APP_TASK[\s\S]*?\?pcm=1[\s\S]*?#endif/);
 for(const name of ['service_calls','service_us','service_max_us','service_misses'])
  assert.ok(block.includes(name));
 const maximum=JSON.stringify({service_calls:0xffffffff,service_us:0xffffffff,
   service_max_us:0xffffffff,service_misses:0xffffffff});
 assert.ok(Buffer.byteLength(maximum)<160);
 assert.match(block,/size < 0 \|\| \(size_t\)size >= sizeof\(s_async_message\)/);
 const app=fs.readFileSync('esp8266/rtos-sdk-native/main/app_main.c','utf8');
 assert.ok(app.indexOf('audio_pcm_queue_record_service')<app.indexOf('notifications = ulTaskNotifyTake'));
});
