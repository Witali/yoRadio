#!/usr/bin/env node
// Explicit opt-in live Opus control; no OTA, UART, adapter or playlist writes.
const fs=require('node:fs'), path=require('node:path'), http=require('node:http');
const {spawn}=require('node:child_process');
function request(base,route,body) {
  return new Promise((resolve,reject)=>{
    const req=http.request(new URL(route,base),{method:body?'POST':'GET',agent:false,
      headers:{Connection:'close',...(body?{'Content-Type':'text/plain','Content-Length':Buffer.byteLength(body)}:{})}},res=>{
      let text=''; res.setEncoding('utf8');
      res.on('data',s=>{text+=s;if(text.length>8192)req.destroy(Error('oversized response'));});
      res.on('error',reject);res.on('end',()=>{
        try{resolve({http:res.statusCode,body:JSON.parse(text)});}catch(e){reject(e);}
      });
    });
    const timer=setTimeout(()=>req.destroy(Error('request timeout '+route)),8000);
    req.on('close',()=>clearTimeout(timer));req.on('error',reject);req.end(body);
  });
}
async function attempt(url,io) {
  const result={date:new Date().toISOString(),url};
  try{result.start=await io.request('/api/native/opus-stream',url);}
  catch(e){result.start_error=e.message;}
  // Keep observations even after an uncertain POST; a missing response does
  // not prove the command was rejected, but cannot qualify this attempt.
  await io.wait(5000);
  try{result.status=await io.request('/api/native/status');}
  catch(e){result.status_error=e.message;}
  try{result.trace=await io.capture();}catch(e){result.capture_error=e.message;}
  result.pass=result.start?.http===202 && result.start.body?.queued===true &&
    result.status?.http===200 && result.status.body?.playing===true &&
    result.status.body?.codec==='OPUS' &&
    result.trace?.result?.continuity?.pass===true && !result.trace?.result?.profile_error;
  return result;
}
async function main() {
  const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
  const base=opt('--base','http://192.168.100.6'),url=opt('--url'),directory=opt('--directory');
  const attempts=Number(opt('--attempts','10'));
  if(!directory || !url || !/^http:\/\/[^\s]+$/.test(url) ||
     !Number.isInteger(attempts)||attempts<10||attempts>100)
    throw Error('--directory, plain HTTP --url, and --attempts >=10 required');
  const dir=path.resolve(directory);fs.mkdirSync(dir,{recursive:true});
  for(let i=1;i<=attempts;i++)for(const stem of ['live-run','live-trace'])
    if(fs.existsSync(path.join(dir,stem+i+'.json')))throw Error('Refusing to overwrite '+stem+i);
  const summary={date:new Date().toISOString(),base,url,attempts,qualified:0,results:[]};
  for(let i=1;i<=attempts;i++) {
    const trace=path.join(dir,'live-trace'+i+'.json');
    console.log('Starting attempt '+i+'/'+attempts);
    const result=await attempt(url,{
      request:(route,body)=>request(base,route,body),
      wait:ms=>new Promise(r=>setTimeout(r,ms)),
      capture:()=>new Promise((resolve,reject)=>{
        const child=spawn(process.execPath,[path.join(__dirname,'run_stage_wall.cjs'),
          '--base',base,'--seconds','25','--output',trace],{stdio:['ignore','pipe','pipe']});
        let log='';child.stdout.on('data',s=>{log+=s;});child.stderr.on('data',s=>{log+=s;});
        child.on('error',reject);child.on('close',code=>{
          fs.writeFileSync(path.join(dir,'live-run'+i+'.log'),log);
          try{const data=JSON.parse(fs.readFileSync(trace,'utf8'));data.runner_exit=code;resolve(data);}
          catch(e){reject(e);}
        });
      })
    });
    fs.writeFileSync(path.join(dir,'live-run'+i+'.json'),JSON.stringify(result,null,2)+'\n');
    summary.qualified+=Number(result.pass);
    summary.results.push({attempt:i,pass:result.pass,start_error:result.start_error,
      status:result.status?.body,continuity:result.trace?.result?.continuity,
      profile_error:result.trace?.result?.profile_error,capture_error:result.capture_error});
    fs.writeFileSync(path.join(dir,'live-series.json'),JSON.stringify(summary,null,2)+'\n');
    console.log(JSON.stringify(summary.results.at(-1)));
  }
  process.exitCode=summary.qualified===attempts?0:1;
}
module.exports={attempt};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
