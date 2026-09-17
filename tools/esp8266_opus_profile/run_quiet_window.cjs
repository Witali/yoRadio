// Read a completed board-side window after >=65s with no requests from this runner.
// Existing sampled tests remain valid failures; this is a separate interference check.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
function analyze(q) {
 const errors=[];
 const keys=['generation','start_ms','end_ms','frames','underruns','age_ms','sample_rate'];
 if(!q||keys.some(k=>!Number.isInteger(q[k])||q[k]<0||q[k]>0xffffffff)||typeof q.valid!=='boolean')
   return {pass:false,errors:['malformed window']};
 const ms=(q.end_ms-q.start_ms)>>>0, audioMs=q.sample_rate?q.frames*1000/q.sample_rate:0;
 if(!q.valid)errors.push('no complete current-generation window');
 if(ms<25000||ms>27000)errors.push('window duration or stalled output');
 if(q.age_ms>20000)errors.push('stale window');
 if(!q.frames||q.sample_rate!==48000)errors.push('PCM not progressing');
 if(q.underruns)errors.push('DMA underruns');
 const ratio=ms?audioMs/ms:0;
 if(ratio<0.98||ratio>1.03)errors.push('PCM/wall duration mismatch');
 return {pass:!errors.length,errors,board_ms:ms,audio_ms:audioMs,ratio,underruns:q.underruns};
}
function request(base) { return new Promise((resolve,reject)=>{
 const req=http.get(new URL('/api/native/audio?quiet=1',base),{agent:false,headers:{Connection:'close'}},res=>{
   let body='';res.setEncoding('utf8');res.on('data',s=>{body+=s;if(body.length>1024)req.destroy(Error('oversized response'))});
   res.on('error',reject);res.on('end',()=>{try{if(res.statusCode!==200)throw Error('HTTP '+res.statusCode);resolve(JSON.parse(body))}catch(e){reject(e)}});
 });
 const timer=setTimeout(()=>req.destroy(Error('quiet response timeout')),15000);
 req.on('close',()=>clearTimeout(timer));req.on('error',reject);
}); }
async function main() {
 const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
 const output=opt('--output'),base=opt('--base','http://192.168.100.6');
 if(!output||fs.existsSync(output))throw Error('New --output path required');
 const report={date:new Date().toISOString(),base,no_runner_requests_ms:65000};
 console.log('Waiting65s without contacting the board; then reading the completed autonomous window.');
 await new Promise(r=>setTimeout(r,65000));
 try{report.window=await request(base);report.result=analyze(report.window)}
 catch(e){report.result={pass:false,errors:[e.message]}}
 fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));process.exitCode=report.result.pass?0:1;
}
module.exports={analyze};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1});
