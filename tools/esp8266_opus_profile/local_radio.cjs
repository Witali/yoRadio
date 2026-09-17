#!/usr/bin/env node
// LAN-only finite test station. Serves one explicit file, never a directory.
const fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const crypto=require('node:crypto');
function crc(bytes) {
 let value=0;
 for(let i=0;i<bytes.length;i++) {
  value^=(i>=22&&i<26?0:bytes[i])<<24;
  for(let b=0;b<8;b++)value=(value<<1)^((value>>>31)?0x04c11db7:0);
 }
 return value>>>0;
}
function pages(data) {
 const out=[];let offset=0,serial,sequence=0,granule=0n,skip=0;
 while(offset<data.length) {
  if(offset+27>data.length||data.toString('ascii',offset,offset+4)!=='OggS'||data[offset+4])throw Error('Invalid Ogg header');
  const n=data[offset+26];if(offset+27+n>data.length)throw Error('Truncated lacing');
  let size=27+n;for(let i=0;i<n;i++)size+=data[offset+27+i];
  if(offset+size>data.length)throw Error('Truncated page');
  const page=data.subarray(offset,offset+size),s=page.readUInt32LE(14);
  if(serial===undefined)serial=s;
  if(s!==serial||page.readUInt32LE(18)!==sequence++)throw Error('Chained or unordered Ogg');
  if(crc(page)!==page.readUInt32LE(22))throw Error('Ogg CRC mismatch');
  const gp=page.readBigUInt64LE(6);
  if(gp===0xffffffffffffffffn||gp<granule)throw Error('Unsupported granule');
  if(!out.length) {
   if(!(page[5]&2)||page.toString('ascii',27+n,35+n)!=='OpusHead')throw Error('Missing OpusHead');
   skip=page.readUInt16LE(27+n+10);
  }
  const dueMs=Math.max(0,(Number(granule)-skip)/48);
  out.push({bytes:page,dueMs,endMs:Math.max(0,(Number(gp)-skip)/48)});
  granule=gp;offset+=size;
 }
 if(!out.length||!(out.at(-1).bytes[5]&4))throw Error('Missing final EOS');
 return out;
}
function createStation(data,{leadMs=1000,log=()=>{}}={}) {
 const parsed=pages(data);let nextId=0;
 if(!Number.isInteger(leadMs)||leadMs<0||leadMs>5000)throw Error('Invalid lead');
 return http.createServer(async(req,res)=>{
  const mode=req.url==='/live.opus'?'paced':req.url==='/buffered.opus'?'buffered':null;
  if(!mode){res.writeHead(404,{'Content-Length':0,Connection:'close'});res.end();return;}
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{Allow:'GET, HEAD','Content-Length':0,Connection:'close'});res.end();return;}
  const id=++nextId,start=performance.now();let sent=0,count=0,maxLateMs=0,drainWaitMs=0;
  let closed=false,cancelWait;
  res.once('error',error=>log({event:'response_error',id,mode,error:error.message}));
  res.once('close',()=>{closed=true;cancelWait?.();log({event:'closed',id,mode,complete:res.writableFinished,
   bytes:sent,pages:count,elapsed_ms:performance.now()-start,max_late_ms:maxLateMs,drain_wait_ms:drainWaitMs});});
  log({event:'request',id,mode,remote:req.socket.remoteAddress,method:req.method});
  req.socket.setNoDelay(true);
  res.writeHead(200,{'Content-Type':'audio/ogg','Content-Length':data.length,Connection:'close','Cache-Control':'no-store'});
  res.flushHeaders();if(req.method==='HEAD'){res.end();return;}
  for(const page of parsed) {
   if(mode==='paced') {
    const due=Math.max(0,page.dueMs-leadMs),wait=due-(performance.now()-start);
    if(wait>0)await new Promise(resolve=>{
     const timer=setTimeout(done,wait);function done(){clearTimeout(timer);cancelWait=undefined;resolve();}cancelWait=done;
    });
    maxLateMs=Math.max(maxLateMs,performance.now()-start-due);
   }
   if(closed)break;
   const ready=res.write(page.bytes);sent+=page.bytes.length;++count;
   if(!ready) {
    const before=performance.now();await new Promise(resolve=>{
     const done=()=>{res.off('drain',done);res.off('close',done);resolve();};res.once('drain',done);res.once('close',done);
    });drainWaitMs+=performance.now()-before;
   }
  }
  if(!closed)res.end();
 });
}
module.exports={crc,pages,createStation};
if(require.main===module) {
 const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
 const file=opt('--file'),host=opt('--host','127.0.0.1'),port=Number(opt('--port','8765'));
 const output=opt('--output'),lifetime=Number(opt('--seconds','900'));
 if(!file||!output||fs.existsSync(output)||!Number.isInteger(port)||port<1024||port>65535||
  !Number.isInteger(lifetime)||lifetime<60||lifetime>3600||!(/^(127\.0\.0\.1|192\.168\.\d+\.\d+)$/.test(host)))throw Error('Explicit file, new output and bounded LAN listener required');
 const data=fs.readFileSync(file);fs.mkdirSync(path.dirname(output),{recursive:true});
 const log=x=>{const line=JSON.stringify({utc:new Date().toISOString(),...x});fs.appendFileSync(output,line+'\n');
  if(x.event!=='tcp')console.log(line);};
 const server=createStation(data,{log});
 let addon;
 if(args.includes('--tcp-info')) {
  addon=require(path.resolve(__dirname,'../../.build/node-tcp-info',process.version,'tcp_info.node'));
  require('../esp8266_audio_profile/network_node_tcp_source.cjs').attachTelemetry(server,addon,log,500);
  if(!addon.keepAwake(true))throw Error('Cannot prevent automatic sleep during test');
  process.once('exit',()=>addon.keepAwake(false));
 }
 const timer=setTimeout(()=>{server.closeAllConnections();server.close()},lifetime*1000);
 server.once('close',()=>{clearTimeout(timer);addon?.keepAwake(false);});
 server.on('error',e=>{console.error(e);clearTimeout(timer);addon?.keepAwake(false);process.exitCode=1;});
 server.listen(port,host,()=>log({event:'listen',host,port,file:path.basename(file),bytes:data.length,
  sha256:crypto.createHash('sha256').update(data).digest('hex'),duration_ms:pages(data).at(-1).endMs,lifetime_seconds:lifetime}));
}
