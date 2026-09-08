#!/usr/bin/env node
// Explicitly opt-in: temporarily edit one station name, then restore the FULL
// original CSV supplied from a SPIFFS backup (not the filtered WebUI download).
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const zlib=require('node:zlib'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const args=process.argv.slice(2),opt=(k,v)=>args.includes(k)?args[args.indexOf(k)+1]:v;
if(!args.includes('--allow-upload')||!opt('--original'))throw new Error('Requires --allow-upload --original <full backed-up playlist.csv>');
const base=opt('--base','http://192.168.100.6'),out=opt('--output','.build/playlist-gzip-upload');
fs.mkdirSync(out,{recursive:true});
const original=fs.readFileSync(opt('--original')), report={date:new Date().toISOString(),base,checks:[],errors:[]};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
report.originalSha256=hash(original);report.originalBytes=original.length;
function request(route,headers={},body){return new Promise((resolve,reject)=>{
  const start=performance.now(),req=http.request(base+route,{method:body?'POST':'GET',headers:{Connection:'close',...headers}},res=>{
    const chunks=[];res.on('data',b=>chunks.push(b));res.on('error',reject);
    res.on('end',()=>resolve({status:res.statusCode,headers:res.headers,body:Buffer.concat(chunks),ms:performance.now()-start}));
  });req.on('error',reject);req.setTimeout(30000,()=>req.destroy(new Error('HTTP timeout')));req.end(body);
});}
async function upload(bytes){
  const boundary='yoradio-gzip-regression-boundary';
  const body=Buffer.concat([Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="data"; filename="playlist.csv"\r\nContent-Type: text/csv\r\n\r\n`),bytes,Buffer.from(`\r\n--${boundary}--\r\n`)]);
  const r=await request('/webboard',{'Content-Type':'multipart/form-data; boundary='+boundary,'Content-Length':body.length},body);
  assert.equal(r.status,303);assert.equal(r.headers.location,'/');
  assert.equal(r.body.toString(),'OK');return r.ms;
}
async function read(encoding){
  const r=await request('/data/playlist.csv',{'Accept-Encoding':encoding});assert.equal(r.status,200);
  assert.match(r.headers.vary||'',/Accept-Encoding/);return r;
}
let previousRaw,mutated=false;
(async()=>{
  const state=await request('/api/native/status');assert.equal(state.status,200);
  // Avoid silently stopping a user's current session; this runner is for
  // maintenance tests while already stopped. Playback runners are separate.
  assert.equal(JSON.parse(state.body).playing,false,'Stop radio before upload regression');
  previousRaw=(await read('identity')).body;
  const first=previousRaw.subarray(0,previousRaw.indexOf(10)+1),at=original.indexOf(first);
  assert.ok(at>=0,'Backed-up original must contain the currently served first row');
  let edit=0;while(edit<first.indexOf(9)&&!(first[edit]>=65&&first[edit]<=122))edit++;
  assert.ok(edit<first.indexOf(9));
  const changed=Buffer.from(original),expected=Buffer.from(previousRaw);
  changed[at+edit]=expected[edit]=first[edit]===65?66:65;
  const before=await read('gzip');assert.equal(before.headers['content-encoding'],'gzip');
  assert.deepEqual(zlib.gunzipSync(before.body),previousRaw);
  mutated=true;
  const uploadMs=await upload(changed);
  const after=await read('gzip'),identity=await read('identity');
  assert.equal(after.headers['content-encoding'],'gzip');assert.equal(identity.headers['content-encoding'],undefined);
  assert.deepEqual(zlib.gunzipSync(after.body),expected);assert.deepEqual(identity.body,expected);
  assert.notEqual(hash(after.body),hash(before.body));
  report.checks.push({name:'changed upload rebuilds gzip before response',pass:true,uploadMs,gzipBytes:after.body.length,identityBytes:identity.body.length,gzipMs:after.ms,identityMs:identity.ms});
  const sameMs=await upload(changed),same=await read('gzip');assert.deepEqual(same.body,after.body);
  report.checks.push({name:'identical upload preserves encoded representation',pass:true,uploadMs:sameMs});
})().catch(error=>{report.errors.push(error.stack);process.exitCode=1;})
.finally(async()=>{
  if(mutated)try{
    const uploadMs=await upload(original),restored=await read('gzip');
    assert.deepEqual(zlib.gunzipSync(restored.body),previousRaw);
    report.checks.push({name:'full original restored and gzip verified',pass:true,uploadMs});
  }catch(error){report.errors.push('RESTORE FAILED: '+error.stack);process.exitCode=1;}
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
});
