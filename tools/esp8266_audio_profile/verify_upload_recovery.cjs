#!/usr/bin/env node
// Re-upload an identical, backed-up gzip asset with a deliberate body gap.
// Only run between measurements: uploads intentionally stop the player.
const http=require('node:http'),fs=require('node:fs'),crypto=require('node:crypto'),zlib=require('node:zlib');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function getRaw(url) {
  return new Promise((resolve,reject)=>{
    const r=http.get(url,{agent:false,headers:{'Connection':'close','Cache-Control':'no-cache','Accept-Encoding':'gzip'}},s=>{
      const parts=[];let size=0;
      s.on('data',b=>{size+=b.length;if(size>96*1024)r.destroy(Error('Asset exceeds test bound'));else parts.push(b)});
      s.on('end',()=>resolve({status:s.statusCode,headers:s.headers,body:Buffer.concat(parts)}));s.on('error',reject);
    });r.setTimeout(20000,()=>r.destroy(Error('GET timeout')));r.on('error',reject);
  });
}
function form(asset) {
  const boundary='yoradio-rx-recovery-test';
  const head=Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="www"; filename="logo.svg.gz"\r\nContent-Type: application/gzip\r\n\r\n`);
  const body=Buffer.concat([head,asset,Buffer.from(`\r\n--${boundary}--\r\n`)]);
  return {body,boundary,split:head.length+Math.floor(asset.length/2)};
}
function upload(origin,asset,pauseMs) {
  const {body,boundary,split}=form(asset),started=performance.now();
  return new Promise((resolve,reject)=>{
    let timer,sent=0,finished=false;
    const request=http.request(origin+'/webboard',{method:'POST',agent:false,headers:{
      'Connection':'close','Content-Type':'multipart/form-data; boundary='+boundary,'Content-Length':body.length}},response=>{
      clearTimeout(timer);const chunks=[];
      response.on('data',b=>chunks.push(b));
      response.on('end',()=>{finished=true;resolve({status:response.statusCode,
        elapsed_ms:performance.now()-started,sent_bytes:sent,total_bytes:body.length,
        body:Buffer.concat(chunks).toString('utf8')});request.destroy()});
      response.on('error',reject);
    });
    request.setNoDelay(true);
    request.setTimeout(20000,()=>request.destroy(Error('Upload timeout')));
    request.on('error',error=>{clearTimeout(timer);if(!finished)reject(error)});
    request.write(body.subarray(0,split));sent=split;
    timer=setTimeout(()=>{sent=body.length;request.end(body.subarray(split))},pauseMs);
  });
}
module.exports={getRaw,form,upload};
if(require.main===module)(async()=>{
  const [base,file,attempts='10',pause='3000']=process.argv.slice(2);
  if(!base||!file)throw Error('Usage: verify_upload_recovery.cjs http://board report.json [attempts=10] [pause_ms=3000]');
  const url=new URL(base);if(url.protocol!=='http:'||url.username||url.password)throw Error('Use the board HTTP origin');
  const count=Number(attempts),pauseMs=Number(pause);
  if(!Number.isInteger(count)||count<1||count>100||!Number.isFinite(pauseMs)||pauseMs<0||pauseMs>15000)throw Error('Invalid test limits');
  const before=await getRaw(url.origin+'/logo.svg');
  if(before.status!==200||before.headers['content-encoding']!=='gzip'||before.body[0]!==0x1f||before.body[1]!==0x8b)throw Error('Expected existing gzip logo; no upload attempted');
  zlib.gunzipSync(before.body);
  fs.writeFileSync(file+'.logo.svg.gz',before.body);
  const report={origin:url.origin,asset:'logo.svg.gz',sha256:sha(before.body),pause_ms:pauseMs,attempts:[],complete:false};
  const save=()=>fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n');save();
  for(let n=0;n<count;n++) {
    const row={attempt:n+1};
    try {
      Object.assign(row,await upload(url.origin,before.body,pauseMs));
      const after=await getRaw(url.origin+'/logo.svg');row.after_sha256=sha(after.body);
      row.ok=row.status===303&&row.sent_bytes===row.total_bytes&&after.status===200&&row.after_sha256===report.sha256;
      if(after.status===200&&row.after_sha256!==report.sha256) {
        row.restore=await upload(url.origin,before.body,0);
        row.restored_sha256=sha((await getRaw(url.origin+'/logo.svg')).body);
        report.attempts.push(row);save();throw Error('Unexpected asset change; recovery attempted, inspect report');
      }
    } catch(error) {row.error=error.message;row.ok=false;}
    if(!report.attempts.includes(row))report.attempts.push(row);
    console.log(JSON.stringify({attempt:row.attempt,status:row.status,ok:row.ok,elapsed_ms:row.elapsed_ms,error:row.error}));save();
    if(row.restore)break;
  }
  report.complete=report.attempts.length===count;report.passed=report.complete&&report.attempts.every(r=>r.ok);save();
  if(!report.passed)process.exitCode=1;
})().catch(error=>{console.error(error.message);process.exitCode=1});
