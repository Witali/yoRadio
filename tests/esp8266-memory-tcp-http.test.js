const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),main=path.join(root,'esp8266/rtos-sdk-native/main');
const read=n=>fs.readFileSync(path.join(main,n),'utf8').replace(/\r\n/g,'\n');
const unix=p=>process.platform==='win32'?p.replaceAll('\\','/').replace(/^([A-Z]):/i,(_,d)=>'/mnt/'+d.toLowerCase()):p;
function run(cmd,args){
 const r=spawnSync(process.platform==='win32'?'wsl.exe':cmd,process.platform==='win32'?['--exec',cmd,...args]:args,{encoding:'utf8',timeout:60000});
 assert.equal(r.status,0,r.error?.message||r.stdout+'\n'+r.stderr);return r.stdout;
}
test('actual sampler and HTTP formatter handle queue lifetime without blocking or mutation',()=>{
 const dir=path.join(root,'.build/memory-tcp-http-test');fs.mkdirSync(dir,{recursive:true});
 const c=read('memory_profile.c'),start=c.indexOf('static volatile bool s_tcp_pending;'),end=c.indexOf('#ifdef CONFIG_HEAP_TRACING');
 const first=c.indexOf('int memory_profile_json('),last=c.indexOf('\n}\n',first)+3;
 assert.ok(start>=0&&end>start&&first>end&&last>first);
 fs.writeFileSync(path.join(dir,'functions.inc'),c.slice(start,end)+'\n'+c.slice(first,last));
 const fixture=path.join(root,'tests/native/memory_tcp');
 for(const ooseq of [0,1]){
  const out=path.join(dir,'test-'+ooseq);
  run('gcc',['-std=c11','-Wall','-Wextra','-Werror','-O1','-fsanitize=address,undefined','-fno-sanitize-recover=all',
   '-DTCP_QUEUE_OOSEQ='+ooseq,'-I'+unix(main),'-I'+unix(fixture),'-I'+unix(dir),unix(path.join(fixture,'test.c')),'-o',unix(out)]);
  assert.match(run(unix(out),[]),/coalescing, failure\/retry, immediate callback and age wrap PASS/);
 }
});
test('TCP owner snapshot is diagnostic-only and uses shared HTTP output storage',()=>{
 const c=read('memory_profile.c'),w=read('web_service.c'),cm=read('CMakeLists.txt');
 assert.match(cm,/if\(YORADIO_ESP8266_MEMORY_PROFILE AND NOT YORADIO_ESP8266_DIAGNOSTIC\)[\s\S]*?FATAL_ERROR/);
 assert.match(w,/#if YORADIO_ESP8266_MEMORY_PROFILE\s+if[^]*?\?memory=1[^]*?memory_profile_json\(s_async_message, sizeof\(s_async_message\)\)[^]*?#endif/);
 assert.match(c,/tcpip_try_callback\(tcp_memory_sample, context\)/);
 assert.match(c,/if \(!context\) return;/);
 assert.equal((c.match(/memory_tcp_capture\(/g)||[]).length,1);
 assert.doesNotMatch(c,/\b(?:malloc|calloc|realloc|free|xTaskCreate)\s*\(/);
 assert.doesNotMatch(w.slice(w.indexOf('static esp_err_t audio_health_handler'),w.indexOf('static esp_err_t serve_static_request')),/tcp_active_pcbs|tcp_tw_pcbs/);
});
