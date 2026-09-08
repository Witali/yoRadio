const test=require('node:test'), assert=require('node:assert/strict');
const http=require('node:http'),fs=require('node:fs'),{once}=require('node:events');
const {createServer}=require('../tools/esp8266_audio_profile/network_source.cjs');
test('LAN source preserves HTTP framing, exact encoded prefix, and pacing',async()=>{
  const server=createServer(); server.listen(0,'127.0.0.1'); await once(server,'listening');
  const port=server.address().port;
  try {
    const started=performance.now();
    await new Promise((resolve,reject)=>{
      const req=http.get('http://127.0.0.1:'+port+'/mp3-128?rate=128',res=>{
        assert.equal(res.statusCode,200);assert.equal(res.headers.connection,'close');
        assert.equal(res.headers['content-type'],'audio/mpeg');
        assert.ok(Number(res.headers['content-length'])>300000);
        assert.equal(res.headers['transfer-encoding'],undefined);
        const chunks=[];let size=0;
        res.on('data',b=>{
          chunks.push(b);size+=b.length;
          if(size>=4096) {
            assert.deepEqual(Buffer.concat(chunks).subarray(0,4096),
              fs.readFileSync('tests/fixtures/mp3_composite/mix-128.mp3').subarray(0,4096));
            assert.ok(performance.now()-started>=120);
            req.destroy();resolve();
          }
        });
        res.on('error',e=>{if(e.code!=='ECONNRESET')reject(e)});
      });req.on('error',reject);
    });
    await new Promise((resolve,reject)=>http.get('http://127.0.0.1:'+port+'/unknown',res=>{
      assert.equal(res.statusCode,404);res.resume();res.on('end',resolve);
    }).on('error',reject));
  } finally { server.closeAllConnections(); await new Promise(r=>server.close(r)); }
});
test('network diagnostic retains decoder memory and distinguishes app gaps from socket emptiness',()=>{
  const source=fs.readFileSync('esp8266/rtos-sdk-native/main/network_benchmark.inc','utf8');
  assert.match(source,/helix_codec_create\(cases\[n\]\.codec, CODEC_HEAP_RESERVE_BYTES\)/);
  assert.match(source,/open_http_stream\(url, &stream\)/);
  assert.match(source,/stream_receive\(&stream, destination, capacity\)/);
  assert.match(source,/max_app_gap/); assert.match(source,/max_empty_wait/);
  assert.match(source,/FIONREAD/); assert.match(source,/generation_current\(generation\)/);
  assert.match(source,/vTaskDelay\(pdMS_TO_TICKS\(1\)\)/);
  assert.doesNotMatch(source,/nvs_set|nvs_commit|nvs_flash_erase/);
  const build=fs.readFileSync('tools/esp8266_audio_profile/build_i2s_pdm_production.ps1','utf8');
  assert.match(build,/-DYORADIO_ESP8266_NETWORK_BENCHMARK=OFF/);
});
test('network report does not discard failed or partial measurements',()=>{
  const {summarize}=require('../tools/esp8266_audio_profile/summarize_network.cjs');
  let log='net_bench: case=0 path=/mp3-320?rate=0 output=0 begin rssi=-80\n'+
    'net_bench: case=0 output=0 wall_us=20000000 bytes=1000000 open_us=1000 error=0 rssi=-78\n';
  for(let i=0;i<20;i++)log+='net_bench: case=0 second='+i+' bytes=50000\n';
  const result=summarize(log);
  assert.equal(result.cases[0].rx_kbps,400);
  assert.equal(result.cases[0].completed,true);
  assert.equal(result.cases[1].completed,false);
  assert.equal(result.complete,false);
  assert.equal(summarize(log.replace('error=0','error=-116')).cases[0].completed,false);
});

test('runtime report separates task residency and baseline from receive elapsed time',()=>{
  const {summarize}=require('../tools/esp8266_audio_profile/summarize_network.cjs');
  const report=summarize('net_bench: begin cases=4\n'+
    'net_cpu: case=-1 valid=1 total_us=20000000 tasks_before=2 tasks_after=2\n'+
    'net_cpu: case=-1 task=IDLE id=1 runtime_us=19000000 existed=1\n'+
    'net_cpu: case=-1 task=tiT id=2 runtime_us=1000000 existed=1\n');
  assert.equal(report.cases.length,4);
  assert.equal(report.cpu[0].case,-1);
  assert.equal(report.cpu[0].idle_percent,95);
  assert.equal(report.cpu[0].non_idle_percent,5);
  assert.equal(report.cpu[0].accounted_percent,100);
  assert.equal(summarize('net_cpu: case=0 valid=0 total_us=0').cpu[0].idle_percent,null);
  const lean=summarize('net_bench: case=0 cpu_lean=1 gap_metrics_valid=0 heap_is_final=1\n'+
    'net_bench: case=0 heap_min=10000 rx_gap_us=0\n'+
    'net_cpu: case=0 valid=1 total_us=1000\n'+
    'net_cpu: case=0 task=Tmr Svc id=3 runtime_us=10 existed=1');
  assert.equal(lean.cpu[0].tasks[0].name,'Tmr Svc');
  assert.equal(lean.cases[0].heap_min,null);
  assert.equal(lean.cases[0].heap_final,10000);
  assert.equal(lean.cases[0].rx_gap_us,null);
  const source=fs.readFileSync('esp8266/rtos-sdk-native/main/network_benchmark.inc','utf8');
  assert.match(source,/uxTaskGetSystemState/);
  assert.match(source,/recv_total_us/);
  assert.match(source,/net_cpu_end\(-1\)/);
});
