const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{once}=require('node:events');
const {createServer}=require('../tools/esp8266_audio_profile/network_source.cjs');
const {attachTelemetry}=require('../tools/esp8266_audio_profile/network_node_tcp_source.cjs');
const {analyzeTcp}=require('../tools/esp8266_audio_profile/summarize_tcp_source.cjs');
test('native Node TCP_INFO samples ten real fixture connections without changing HTTP bytes',async t=>{
  const binary=path.resolve(__dirname,'../.build/node-tcp-info',process.version,'tcp_info.node');
  if(process.platform!=='win32'||!fs.existsSync(binary))return t.skip('Build optional Windows TCP_INFO addon first');
  const addon=require(binary);assert.throws(()=>addon.sample(0));
  const events=[],server=createServer();attachTelemetry(server,addon,event=>events.push(event),50);
  server.listen(0,'127.0.0.1');await once(server,'listening');
  events.push({event:'listen'});const port=server.address().port;
  try {
    for(let n=0;n<10;n++) {
      const aac=n%2,source=aac?'aac-64':'mp3-128',rate=aac?64:128;
      const original=fs.readFileSync(aac?'tests/fixtures/aac_composite/mix-064.aac':'tests/fixtures/mp3_composite/mix-128.mp3');
      await new Promise((resolve,reject)=>{
        const req=http.get(`http://127.0.0.1:${port}/${source}?rate=${rate}&case=${n}&variant=${n%2}`,res=>{
          assert.equal(res.statusCode,200);assert.equal(res.headers.connection,'close');
          const chunks=[];let received=0;
          res.on('data',b=>{
            chunks.push(b);received+=b.length;
            if(received>=4096) {
              assert.deepEqual(Buffer.concat(chunks).subarray(0,4096),original.subarray(0,4096));
              req.destroy();resolve();
            }
          });res.on('error',e=>{if(e.code!=='ECONNRESET')reject(e)});
        });req.on('error',reject);
      });
      await new Promise(r=>setTimeout(r,20));
    }
    const report=analyzeTcp(events.map(JSON.stringify).join('\n'));
    assert.equal(report.valid,true);assert.equal(report.connections.length,10);
    for(const c of report.connections) {
      assert.ok(c.sample_count>=2);assert.equal(c.telemetry_errors.length,0);
      assert.ok(c.send_window.min>0);assert.ok(c.rtt_us.min>=0);
      assert.equal(c.retransmitted_bytes_sample_delta,0);assert.equal(c.closed,true);
    }
  } finally {server.closeAllConnections();await new Promise(r=>server.close(r));}
  assert.deepEqual(addon.sample(port),[]);
});
