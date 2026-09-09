// Hardware regression: one persistent WS, mixed decoder starts and stops.
// No reset, UART traffic, Wi-Fi changes, playlist or settings writes.
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.RADIO_URL || 'http://192.168.100.6';
const file = process.argv[2];
const rounds = Number(process.argv[3] || 10);
if (!file || !Number.isInteger(rounds) || rounds < 1 || rounds > 100)
  throw Error('Usage: node check_codec_lifecycle.cjs report.json [rounds=10]');
const report = {date: new Date().toISOString(), base, rounds, rows: []};
fs.mkdirSync(path.dirname(file), {recursive:true});
const save = () => fs.writeFileSync(file, JSON.stringify(report, null, 2));
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function status() {
  const response = await fetch(base+'/api/native/status', {headers:{Connection:'close'}, signal:AbortSignal.timeout(5000)});
  if (!response.ok) throw Error('HTTP '+response.status);
  return response.json();
}
async function openSocket() {
  const ws = new WebSocket(base.replace(/^http/, 'ws')+'/ws');
  await new Promise((resolve,reject) => {
    const timer=setTimeout(()=>{ws.close();reject(Error('WS timeout'));},5000);
    ws.onopen=()=>{clearTimeout(timer);resolve();};
    ws.onerror=()=>{clearTimeout(timer);reject(Error('WS error'));};
  });
  ws.onmessage=()=>{};
  return ws;
}
async function main() {
  let ws=await openSocket();
  try {
    ws.send('stop=1'); await sleep(1500);
    report.before=await status(); save();
    for(let round=0;round<rounds;++round) {
      for (const [command,codec] of [['play=502','MP3'],['play=485','AAC'],['play=502','MP3'],['stop=1',null]]) {
        if(ws.readyState!==WebSocket.OPEN) {ws.close();ws=await openSocket();}
        ws.send(command);
        const start=performance.now();
        let state, error;
        const transportErrors=[];
        do {
          await sleep(1000);
          try { state=await status(); } catch(e) {error=e.message;transportErrors.push(error);continue;}
          if (codec ? state.playing && state.codec===codec : !state.playing && !state.connecting) break;
          if(ws.readyState!==WebSocket.OPEN) {error='WebSocket closed during command';break;}
          if(state.error && !state.connecting && performance.now()-start>3000) break;
        } while(performance.now()-start<25000);
        // Let TCP closures and delayed worker cleanup run before sampling.
        await sleep(codec ? 2000 : 1500);
        try {state=await status();error=undefined;} catch(e) {error=e.message;}
        const row={round:round+1,command,ms:performance.now()-start,state,error,transportErrors};
        row.pass=!error && !state.error && (codec ? state.playing && state.codec===codec : !state.playing && !state.connecting);
        report.rows.push(row); save();
        console.log(JSON.stringify(row));
      }
    }
    report.after=await status();
    report.stop_heaps=report.rows.filter(r=>r.command==='stop=1').map(r=>r.state?.free_heap);
    report.retained_bytes=report.before.free_heap-report.after.free_heap;
    // A noisy Wi-Fi/closing-TCP sample is not proof of a malloc/free leak.
    // Keep the numerical delta, but report it as a regression threshold only.
    report.pass=report.rows.every(r=>r.pass) && report.retained_bytes<=2048;
  } finally {
    if(ws.readyState===WebSocket.OPEN)ws.send('stop=1');
    ws.close();save();
  }
  console.log('RESULT',JSON.stringify({pass:report.pass,retained:report.retained_bytes,stop_heaps:report.stop_heaps}));
  if(!report.pass) process.exitCode=1;
}
main().catch(e=>{report.error=e.stack;save();console.error(e);process.exitCode=1;});
