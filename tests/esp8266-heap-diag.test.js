const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {execute,hostPath,root}=require('../tools/esp8266_opus_profile/build_host.cjs');
test('diagnostic largest DRAM block walk is bounded and allocation-free', {timeout:60000},t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'heap-diag-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const harness=path.join(__dirname,'native/heap_diag');
  const component=path.join(root,'esp8266/rtos-sdk-native/components/helix_codecs');
  const binary=hostPath(path.join(dir,'test'));
  execute('gcc',['-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
    '-I'+hostPath(harness),'-I'+hostPath(component),hostPath(path.join(harness,'test.c')),
    hostPath(path.join(component,'native_heap_diag.c')),'-o',binary]);
  const out=execute('env',['ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
    'UBSAN_OPTIONS=halt_on_error=1',binary]);
  assert.match(out,/Heap diagnostic PASS/); t.diagnostic(out.trim());
});
test('diagnostic init JSON fits at maximum counters',()=>{
  const max=0xffffffff;
  const payload={stage:max,free_dram:max,requested_bytes:max,reserve_bytes:max,
    detail:-2147483648,largest_dram:max,current_dram:max,current_largest:max};
  const web=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.c'),'utf8');
  const handler=web.split('static esp_err_t opus_test_stream_status_handler')[1].split('\n}')[0];
  const size=Number(handler.match(/char body\[(\d+)\]/)[1]);
  assert.ok(Buffer.byteLength(JSON.stringify(payload))<size);
  assert.match(handler,/\(size_t\)n >= sizeof\(body\)/);
});
