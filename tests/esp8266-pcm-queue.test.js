const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {execute,hostPath,root}=require('../tools/esp8266_opus_profile/build_host.cjs');
for (const stack of [1536,2048])
for (const appTask of [0,1])
test('actual PCM queue survives concurrent ownership, backpressure, stop and output failure, stack '+stack+' app '+appTask,{timeout:60000},t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'pcm-queue-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const binary=hostPath(path.join(dir,'test'));
  const main=path.join(root,'esp8266/rtos-sdk-native/main');
  const harness=path.join(__dirname,'native/pcm_queue');
  execute('gcc',['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pthread',
    '-DAUDIO_PCM_QUEUE_STACK_BYTES='+stack,
    '-DYORADIO_ESP8266_OPUS_PCM_APP_TASK='+appTask,
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
    '-I'+hostPath(harness),'-I'+hostPath(main),hostPath(path.join(harness,'test.c')),
    hostPath(path.join(main,'audio_pcm_queue.c')),'-o',binary]);
  const out=execute('env',['ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
    'UBSAN_OPTIONS=halt_on_error=1',binary]);
  assert.match(out,/PCM queue PASS/);t.diagnostic(out.trim());
});
