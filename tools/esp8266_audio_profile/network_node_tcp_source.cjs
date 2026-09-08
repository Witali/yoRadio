#!/usr/bin/env node
// Same existing Node fixture server, with read-only samples of its own sockets.
const path=require('node:path');
const {createServer}=require('./network_source.cjs');
function attachTelemetry(server,addon,log,sampleMs=100) {
  let next=0;const active=new Map();
  server.on('request',(request,response)=>{
    const socket=request.socket,id=++next,started=performance.now();
    const url=new URL(request.url,'http://fixture');
    const key=socket.remoteAddress+':'+socket.remotePort;
    const c={id,started,socket};active.set(key,c);
    log({event:'begin',id,path:url.pathname,case:Number(url.searchParams.get('case')??-1),
      variant:Number(url.searchParams.get('variant')??-1),rate_kbps:Number(url.searchParams.get('rate')),sample_ms:sampleMs});
    socket.once('close',hadError=>{
      log({event:'end',id,elapsed_ms:performance.now()-started,accepted_wire_bytes:socket.bytesWritten,error:hadError?1:0});
      if(active.get(key)===c)active.delete(key);
    });
  });
  const timer=setInterval(()=>{
    const address=server.address();if(!address)return;
    const started=performance.now();
    for(const snapshot of addon.sample(address.port)) {
      const c=active.get(snapshot.peer_address+':'+snapshot.peer_port);if(!c)continue;
      log({event:snapshot.error!==undefined?'tcp_info_error':'tcp',id:c.id,ms:performance.now()-c.started,
        accepted_wire_bytes:c.socket.bytesWritten,...snapshot,sample_call_ms:performance.now()-started});
    }
  },sampleMs);
  timer.unref();server.once('close',()=>clearInterval(timer));
}
module.exports={attachTelemetry};
if(require.main===module) {
  const addon=require(path.resolve(__dirname,'../../.build/node-tcp-info',process.version,'tcp_info.node'));
  const log=data=>console.log(JSON.stringify({utc:new Date().toISOString(),...data}));
  if(!addon.keepAwake(true))throw Error('Cannot inhibit automatic sleep for this benchmark');
  process.once('exit',()=>addon.keepAwake(false));
  const server=createServer();attachTelemetry(server,addon,log);
  server.once('close',()=>addon.keepAwake(false));
  server.listen(8765,'192.168.100.253',()=>log({event:'listen',address:'192.168.100.253',port:8765,host:'node'}));
}
