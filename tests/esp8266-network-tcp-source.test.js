const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),net=require('node:net'),http=require('node:http');
const {spawn}=require('node:child_process');
test('Windows TCP source preserves ten encoded prefixes and returns socket telemetry',{skip:process.platform!=='win32'},async t=>{
  const probe=net.createServer();await new Promise(r=>probe.listen(0,'127.0.0.1',r));
  const port=probe.address().port;await new Promise(r=>probe.close(r));
  const child=spawn('powershell.exe',['-NoProfile','-ExecutionPolicy','Bypass','-File',
    path.resolve(__dirname,'../tools/esp8266_audio_profile/network_tcp_source.ps1'),
    '-Address','127.0.0.1','-Port',String(port),'-SampleMs','100'],{windowsHide:true});
  let output='',errors='';child.stdout.on('data',b=>output+=b);child.stderr.on('data',b=>errors+=b);
  t.after(()=>child.kill());
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{clearInterval(check);reject(Error('Source startup: '+errors))},15000);
    const check=setInterval(()=>{if(output.includes('"event":"listen"')){clearTimeout(timer);clearInterval(check);resolve()}},50);
    child.once('error',reject);
  });
  const fixtures=[['/mp3-128','mp3_composite/mix-128.mp3',128],
    ['/mp3-320','mp3_composite/mix-320.mp3',320],['/aac-64','aac_composite/mix-064.aac',64]];
  for(let i=0;i<10;i++) {
    const [uri,file,rate]=fixtures[i%fixtures.length];
    const expected=fs.readFileSync(path.join(__dirname,'fixtures',file)).subarray(0,4096);
    const started=performance.now();
    await new Promise((resolve,reject)=>{
      const req=http.get(`http://127.0.0.1:${port}${uri}?rate=${rate}&case=${i}&variant=0`,res=>{
        try {assert.equal(res.statusCode,200);assert.equal(res.headers.connection,'close');
          assert.ok(Number(res.headers['content-length'])>4096);assert.equal(res.headers['transfer-encoding'],undefined);
        } catch(e){req.destroy();reject(e);return}
        const chunks=[];let size=0;
        res.on('data',b=>{chunks.push(b);size+=b.length;if(size>=4096){
          try {assert.deepEqual(Buffer.concat(chunks).subarray(0,4096),expected);
            assert.ok(performance.now()-started>=3072*8/rate-20);
            req.destroy();resolve();
          }catch(e){req.destroy();reject(e)}
        }});
        res.on('error',e=>{if(e.code!=='ECONNRESET')reject(e)});
      });req.setTimeout(5000,()=>req.destroy(Error('Loopback source timeout')));req.on('error',reject);
    });
  }
  await new Promise(r=>setTimeout(r,200));
  const records=output.split(/\r?\n/).filter(l=>l.startsWith('{')).map(l=>JSON.parse(l));
  assert.equal(records.filter(r=>r.event==='begin').length,10);
  assert.ok(records.filter(r=>r.event==='tcp').length>=10);
  assert.ok(records.filter(r=>r.event==='tcp').every(r=>r.mss>0&&r.snd_wnd>=0&&r.rtt_us>=0));
  assert.equal(records.filter(r=>r.event==='tcp_info_error'||r.event==='tcp_info_size').length,0);
  assert.equal(errors,'');
});
