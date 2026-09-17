// Diagnostic observations only: this does NOT qualify CPU or uninterrupted I2S.
// No OTA, UART, reset, Wi-Fi adapter or playlist operations.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const routes={memory:'/api/native/audio?memory=1',audio:'/api/native/audio',init:'/api/native/opus-stream'};
function request(base,route,body){
 return new Promise((resolve,reject)=>{
  const started=performance.now();
  const req=http.request(new URL(route,base),{method:body===undefined?'GET':'POST',agent:false,
   headers:{Connection:'close',...(body===undefined?{}:{'Content-Type':'text/plain','Content-Length':Buffer.byteLength(body)})}},res=>{
   let text='';res.setEncoding('utf8');res.on('data',s=>{text+=s;if(text.length>8192)req.destroy(Error('oversized response'));});
   res.on('error',reject);res.on('end',()=>{try{resolve({http:res.statusCode,ms:performance.now()-started,body:JSON.parse(text)});}catch(e){reject(e);}});
  });
  const timer=setTimeout(()=>req.destroy(Error('request timeout '+route)),3000);
  req.on('close',()=>clearTimeout(timer));req.on('error',reject);req.end(body);
 });
}
async function attempt(url,io,samples=8){
 const result={date:new Date().toISOString(),url,samples:[],scope:'Intrusive memory diagnosis; not a continuity or CPU measurement.'};
 try{result.start=await io.request(routes.init,url);}catch(e){result.start_error=e.message;}
 io.save(result);
 for(let i=0;i<samples;i++){
  const row={index:i,host_ms:io.now()};
  for(const[name,route]of Object.entries(routes)){
   try{row[name]=await io.request(route);}catch(e){row[name+'_error']=e.message;}
  }
  result.samples.push(row);io.save(result);
  if(i+1<samples)await io.wait(2000);
 }
 try{result.status=await io.request('/api/native/status');}catch(e){result.status_error=e.message;}
 result.observable=result.samples.some(s=>s.audio?.http===200&&Number.isInteger(s.audio.body?.uptime_ms));
 io.save(result);return result;
}
async function main(){
 const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
 const base=opt('--base','http://192.168.100.6'),url=opt('--url'),dir=opt('--directory'),count=Number(opt('--attempts','10'));
 if(!dir||!url||!/^http:\/\/[^\s]+$/.test(url)||!Number.isInteger(count)||count<10||count>100)throw Error('--directory, --url and --attempts>=10 required');
 fs.mkdirSync(dir,{recursive:true});
 if(fs.readdirSync(dir).some(n=>/^attempt-\d+\.json$|^summary\.json$/.test(n)))throw Error('Do not overwrite observations');
 const initial=await request(base,routes.memory);
 if(initial.http!==200||initial.body.heap_valid!==true)throw Error('Diagnostic memory API unavailable; no play command sent');
 const report={date:new Date().toISOString(),base,url,initial,requested:count,attempts:[]};
 for(let i=1;i<=count;i++){
  const file=path.join(dir,'attempt-'+i+'.json'),started=performance.now();
  console.log('MEMORY attempt '+i+'/'+count);
  const result=await attempt(url,{request:(route,body)=>request(base,route,body),now:()=>performance.now()-started,
   wait:ms=>new Promise(r=>setTimeout(r,ms)),save:r=>fs.writeFileSync(file,JSON.stringify(r,null,2)+'\n')});
  report.attempts.push({attempt:i,file:path.basename(file),observable:result.observable,status:result.status?.body,start_error:result.start_error});
  fs.writeFileSync(path.join(dir,'summary.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report.attempts.at(-1)));
  if(!result.observable)throw Error('No live observation; inspect board instead of another play POST');
 }
}
module.exports={request,attempt,routes};if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
