const test=require('node:test'),assert=require('node:assert/strict');
const http=require('node:http'),zlib=require('node:zlib');
const {once}=require('node:events');
const {form,getRaw,upload}=require('../tools/esp8266_audio_profile/verify_upload_recovery.cjs');
test('delayed upload client preserves identical gzip bytes and multipart framing',async()=>{
  const asset=zlib.gzipSync(Buffer.from('<svg>fixture</svg>'));
  const expected=form(asset);let received,first,last;
  const server=http.createServer((req,res)=>{
    if(req.method==='GET') {
      res.writeHead(200,{'Content-Encoding':'gzip','Content-Length':asset.length});res.end(asset);return;
    }
    assert.equal(req.url,'/webboard');assert.equal(Number(req.headers['content-length']),expected.body.length);
    const chunks=[];
    req.on('data',b=>{first??=performance.now();last=performance.now();chunks.push(b)});
    req.on('end',()=>{received=Buffer.concat(chunks);res.writeHead(303,{'Location':'/'});res.end()});
  });
  server.listen(0,'127.0.0.1');await once(server,'listening');
  try {
    const base='http://127.0.0.1:'+server.address().port;
    assert.deepEqual((await getRaw(base+'/logo.svg')).body,asset);
    const response=await upload(base,asset,100);
    assert.equal(response.status,303);assert.equal(response.sent_bytes,response.total_bytes);
    assert.deepEqual(received,expected.body);assert.ok(last-first>=50);
  } finally {server.closeAllConnections();await new Promise(r=>server.close(r));}
});
test('early rejection stops the delayed second half instead of reporting a full upload',async()=>{
  const server=http.createServer((req,res)=>{res.writeHead(400);res.end('rejected')});
  server.listen(0,'127.0.0.1');await once(server,'listening');
  try {
    const response=await upload('http://127.0.0.1:'+server.address().port,Buffer.alloc(128),300);
    assert.equal(response.status,400);assert.ok(response.sent_bytes<response.total_bytes);
  } finally {server.closeAllConnections();await new Promise(r=>server.close(r));}
});
