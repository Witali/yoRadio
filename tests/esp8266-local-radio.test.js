const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const crypto=require('node:crypto');
const {pages,createStation}=require('../tools/esp8266_opus_profile/local_radio.cjs');
const input=fs.readFileSync(path.join(__dirname,'fixtures/opus_native/mono-24.opus'));
test('local station validates Ogg framing, checksum, sequence and duration',()=>{
 const p=pages(input);assert.ok(p.length>2);assert.equal(p.at(-1).endMs,1200);
 assert.deepEqual(Buffer.concat(p.map(x=>x.bytes)),input);
 const bad=Buffer.from(input);bad[bad.length-1]^=1;assert.throws(()=>pages(bad),/CRC/);
 assert.throws(()=>pages(input.subarray(0,input.length-1)),/Truncated/);
});
test('long own-signal fixtures have verified checksums and five-minute granules',()=>{
 const dir=path.join(__dirname,'fixtures/opus_local_radio');
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));
 assert.equal(manifest.duration_seconds,300);
 for(const f of manifest.files) {
  const data=fs.readFileSync(path.join(dir,f.name)),p=pages(data);
  assert.equal(crypto.createHash('sha256').update(data).digest('hex'),f.sha256);
  assert.equal(data.length,f.bytes);assert.equal(p.at(-1).endMs,300000);
  assert.equal(p.length,f.pages);
 }
});
test('paced and buffered responses preserve every source byte and HTTP framing',async t=>{
 const server=createStation(input,{leadMs:0});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 t.after(()=>{server.closeAllConnections();server.close()});
 const get=(route,method='GET')=>new Promise((resolve,reject)=>{
  const start=performance.now(),req=http.request({host:'127.0.0.1',port:server.address().port,path:route,method,agent:false},res=>{
   const chunks=[];res.on('data',x=>chunks.push(x));res.on('end',()=>resolve({status:res.statusCode,headers:res.headers,data:Buffer.concat(chunks),ms:performance.now()-start}));res.on('error',reject);
  });req.on('error',reject);req.end();
 });
 for(const route of ['/buffered.opus','/live.opus']) {
  const r=await get(route);assert.equal(r.status,200);assert.equal(Number(r.headers['content-length']),input.length);
  assert.equal(r.headers.connection,'close');assert.equal(r.headers['transfer-encoding'],undefined);assert.deepEqual(r.data,input);
  if(route==='/live.opus')assert.ok(r.ms>=1000,'real-time pacing must not send all audio immediately');
 }
 assert.equal((await get('/buffered.opus','HEAD')).data.length,0);
 assert.equal((await get('/buffered.opus','POST')).status,405);
 assert.equal((await get('/../../wifi.csv')).status,404);
});
