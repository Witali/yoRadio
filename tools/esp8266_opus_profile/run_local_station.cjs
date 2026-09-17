#!/usr/bin/env node
// Explicit playback control only: no OTA, playlist writes or adapter changes.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {spawn}=require('node:child_process');
const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
const url=opt('--url'),directory=opt('--directory'),base=opt('--base','http://192.168.100.6');
const windows=Number(opt('--windows','2'));
if(!url||!directory||fs.existsSync(directory)||!Number.isInteger(windows)||windows<1||windows>5||
 !/^http:\/\/192\.168\.\d+\.\d+:\d+\/(live|buffered)\.opus$/.test(url))throw Error('Explicit local station URL and new directory required');
fs.mkdirSync(directory,{recursive:true});
const report={date:new Date().toISOString(),url,base,windows:[]};
const save=()=>fs.writeFileSync(path.join(directory,'summary.json'),JSON.stringify(report,null,2)+'\n');
function request(route,body) {return new Promise(resolve=>{
 const started=performance.now();const req=http.request(new URL(route,base),{method:body?'POST':'GET',agent:false,
  headers:{Connection:'close',...(body?{'Content-Type':'text/plain','Content-Length':Buffer.byteLength(body)}:{})}},res=>{
  let text='';res.setEncoding('utf8');res.on('data',c=>{text+=c;if(text.length>8192)req.destroy(Error('oversized'))});
  res.on('error',e=>resolve({error:e.message}));res.on('end',()=>{try{resolve({http:res.statusCode,ms:performance.now()-started,data:JSON.parse(text)})}catch(e){resolve({error:e.message})}});
 });const timer=setTimeout(()=>req.destroy(Error('request timeout '+route)),15000);
 req.on('close',()=>clearTimeout(timer));req.on('error',e=>resolve({error:e.message,ms:performance.now()-started}));req.end(body);
});}
async function main() {
 report.before=await request('/api/native/status');report.start=await request('/api/native/opus-stream',url);save();console.log('START',JSON.stringify(report.start));
 if(report.start.http!==202)throw Error('Local stream start not acknowledged');
 for(let i=1;i<=windows;i++) {
  const file=path.join(directory,`window${i}.json`);
  const code=await new Promise((resolve,reject)=>{
   const child=spawn(process.execPath,[path.join(__dirname,'run_quiet_window.cjs'),'--base',base,'--output',file],{stdio:'inherit'});
   child.on('error',reject);child.on('close',resolve);
  });
  const row={exit_code:code};try{row.measurement=JSON.parse(fs.readFileSync(file,'utf8'))}catch(e){row.error=e.message}
  // All health/status HTTP requests occur after the closed autonomous window.
  row.health=await request('/api/native/audio');row.status=await request('/api/native/status');
  report.windows.push(row);save();console.log('WINDOW',i,JSON.stringify({result:row.measurement?.result,health:row.health,status:row.status}));
 }
 report.pass=report.windows.length===windows&&report.windows.every(w=>w.measurement?.result?.pass&&w.status.data?.playing);
 report.init=await request('/api/native/opus-stream');save();console.log('SUMMARY',JSON.stringify({pass:report.pass,directory}));
 process.exitCode=report.pass?0:1;
}
main().catch(e=>{report.error=e.message;save();console.error(e);process.exitCode=1});
