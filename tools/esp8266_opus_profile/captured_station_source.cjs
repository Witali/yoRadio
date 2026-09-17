#!/usr/bin/env node
// Serve exactly one explicitly named capture, never a directory or credentials.
// Unpaced TCP lets the board apply backpressure; no looping/trimming/re-encoding.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const {attachTelemetry}=require('../esp8266_audio_profile/network_node_tcp_source.cjs');
function createSource(file,log=()=>{}) {
 const bytes=fs.readFileSync(file);
 if(bytes.subarray(0,4).toString()!=='OggS')throw Error('Expected Ogg capture');
 return http.createServer(async(req,res)=>{
  const url=new URL(req.url,'http://capture');
  if(req.method!=='GET'||url.pathname!=='/capture.opus'){
   res.writeHead(404,{Connection:'close'});res.end();return;
  }
  let closed=false,sent=0;const start=performance.now();
  res.on('close',()=>{closed=true});res.socket.setNoDelay(true);
  res.writeHead(200,{'Content-Type':'audio/ogg','Content-Length':bytes.length,Connection:'close'});
  try{
   while(!closed&&sent<bytes.length){
    const count=Math.min(1024,bytes.length-sent);
    const ready=res.write(bytes.subarray(sent,sent+count));sent+=count;
    if(!ready)await new Promise(resolve=>{
     const done=()=>{res.off('drain',done);res.off('close',done);resolve()};
     res.once('drain',done);res.once('close',done);
    });
   }
  }finally{res.end();log({event:'body_queued',bytes:sent,elapsed_ms:performance.now()-start,closed});}
 });
}
module.exports={createSource};
if(require.main===module){
 const [file,address,portText='8765',secondsText='900']=process.argv.slice(2);
 const port=Number(portText),seconds=Number(secondsText);
 if(!file||!/^192\.168\.\d+\.\d+$/.test(address)||!Number.isInteger(port)||port<1024||port>65535||!Number.isInteger(seconds)||seconds<60||seconds>3600)
  throw Error('Usage: capture.opus LAN-IPv4 port lifetime-seconds');
 const addon=require(path.resolve(__dirname,'../../.build/node-tcp-info',process.version,'tcp_info.node'));
 const log=x=>console.log(JSON.stringify({utc:new Date().toISOString(),...x}));
 const server=createSource(file,log);attachTelemetry(server,addon,log);
 if(!addon.keepAwake(true))throw Error('Cannot inhibit automatic sleep');
 process.once('exit',()=>addon.keepAwake(false));
 const timer=setTimeout(()=>{server.closeAllConnections();server.close()},seconds*1000);
 server.once('close',()=>{clearTimeout(timer);addon.keepAwake(false)});
 server.listen(port,address,()=>log({event:'listen',address,port,file:path.basename(file),lifetime_seconds:seconds}));
}
