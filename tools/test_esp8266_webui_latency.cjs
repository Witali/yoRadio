#!/usr/bin/env node
// Opt-in physical-board benchmark. No Wi-Fi changes, uploads or resets.
// --controls temporarily changes volume via the actual page buttons, restores it.
// --playback exercises real Play/Stop/Next/Prev/row clicks, restores station/state.
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const args = process.argv.slice(2);
const option = (k, v) => args.includes(k) ? args[args.indexOf(k)+1] : v;
const base = option('--base', 'http://192.168.100.6');
const output = option('--output', '.build/webui-latency');
const rounds = Number(option('--rounds', '3'));
const report = {date:new Date().toISOString(), base, loads:[], controls:[], errors:[]};
fs.mkdirSync(output, {recursive:true});
const save = () => fs.writeFileSync(path.join(output,'results.json'), JSON.stringify(report,null,2)+'\n');
let browser;
async function load(page, kind, round) {
  const sample = {kind, round, resources:[], errors:[]};
  let cdp;
  if(args.includes('--trace')) {
    sample.network=[];
    cdp=await page.context().newCDPSession(page);await cdp.send('Network.enable');
    const pending=new Map();
    cdp.on('Network.requestWillBeSent',e=>{
      if(!/^https?:/.test(e.request.url))return;
      const item={requestId:e.requestId,path:new URL(e.request.url).pathname,
        wallTime:e.wallTime,started:e.timestamp,chunks:[]};
      pending.set(e.requestId,item);sample.network.push(item);
    });
    cdp.on('Network.responseReceived',e=>{
      const item=pending.get(e.requestId);if(!item)return;
      item.headersAt=e.timestamp;item.timing=e.response.timing;
      item.traceId=Object.entries(e.response.headers).find(([k])=>k.toLowerCase()==='x-yoradio-trace')?.[1] || null;
    });
    cdp.on('Network.dataReceived',e=>{const item=pending.get(e.requestId);if(item)item.chunks.push({at:e.timestamp,bytes:e.encodedDataLength,decodedBytes:e.dataLength});});
    cdp.on('Network.loadingFinished',e=>{const item=pending.get(e.requestId);if(item){item.finished=e.timestamp;item.encodedBytes=e.encodedDataLength;}});
    cdp.on('Network.loadingFailed',e=>{const item=pending.get(e.requestId);if(item)item.error=e.errorText;});
    sample.sockets=[];const sockets=new Map();
    cdp.on('Network.webSocketCreated',e=>{
      const item={requestId:e.requestId,path:new URL(e.url).pathname};
      sockets.set(e.requestId,item);sample.sockets.push(item);
    });
    cdp.on('Network.webSocketWillSendHandshakeRequest',e=>{const item=sockets.get(e.requestId);if(item){item.handshakeStart=e.timestamp;item.wallTime=e.wallTime;}});
    cdp.on('Network.webSocketHandshakeResponseReceived',e=>{const item=sockets.get(e.requestId);if(item){item.handshakeEnd=e.timestamp;item.status=e.response.status;}});
    cdp.on('Network.webSocketClosed',e=>{const item=sockets.get(e.requestId);if(item)item.closedAt=e.timestamp;});
    cdp.on('Network.webSocketFrameError',e=>{const item=sockets.get(e.requestId);if(item)item.error=e.errorMessage;});
  }
  const finished = async req => {
    const res = await req.response(), t = req.timing();
    sample.resources.push({path:new URL(req.url()).pathname, status:res.status(),
      traceId:res.headers()['x-yoradio-trace'] || null,
      startTime:t.startTime, dnsStart:t.domainLookupStart, dnsEnd:t.domainLookupEnd,
      connectStart:t.connectStart, connectEnd:t.connectEnd, requestStart:t.requestStart,
      ttfbMs:t.responseStart, totalMs:t.responseEnd});
  };
  const failed = req => sample.errors.push({url:req.url(), error:req.failure()?.errorText});
  page.on('requestfinished', finished); page.on('requestfailed', failed);
  console.log('RUN',kind,round);
  try {
    await page.goto(base+'/', {waitUntil:'domcontentloaded',timeout:30000});
    await page.waitForFunction(()=>window.__readyMs != null, null, {timeout:30000});
    Object.assign(sample, await page.evaluate(()=>({readyMs:window.__readyMs,
      rows:document.querySelectorAll('#playlist li[attr-id]').length,
      current:currentItem, rssi:document.querySelector('#rssi')?.textContent,
      player:document.querySelector('#playerwrap')?.className,
      pageTrace:window.__pageTrace})));
    sample.pass = sample.readyMs <= 500;
  } catch(e) {sample.error=e.message; sample.pass=false;}
  page.off('requestfinished', finished); page.off('requestfailed', failed);
  if(cdp)await cdp.detach();
  report.loads.push(sample); save();
  console.log(JSON.stringify({...sample,network:sample.network?.map(({chunks,...rest})=>({...rest,chunkCount:chunks.length}))}));
  return !sample.error;
}
async function buttons(page) {
  const original = await page.locator('#volume').inputValue();
  try {
    for(let i=0;i<10;i++) {
      const selector = i%2 ? '#volpbutton' : '#volmbutton';
      const result = await page.evaluate(({selector})=>new Promise(resolve=>{
        const before = Number(document.querySelector('#volume').value);
        const started = performance.now();
        let timer;
        const finish = data => {clearTimeout(timer); websocket.removeEventListener('message',message); resolve(data);};
        const message = event => {
          let data; try {data=JSON.parse(event.data);} catch{return;}
          const value=data.payload?.find(x=>x.id==='volume')?.value;
          if(value==null || Number(value)===before) return;
          // This listener runs after the real onMessage handler. Check readback,
          // not the optimistic slider update made when the user clicks.
          finish({selector, before, serverValue:Number(value),
            displayedValue:Number(document.querySelector('#volume').value),
            elapsedMs:performance.now()-started});
        };
        websocket.addEventListener('message',message);
        timer=setTimeout(()=>finish({selector,error:'No changed server volume in 5000 ms'}),5000);
        document.querySelector(selector).click();
      }),{selector});
      result.pass=!result.error && result.elapsedMs<=200 && result.serverValue===result.displayedValue;
      report.controls.push(result); save(); console.log(JSON.stringify(result));
      await page.waitForTimeout(200);
    }
  } finally {
    await page.evaluate(value=>websocket.send('volume='+value),original);
    await page.waitForFunction(value=>document.querySelector('#volume').value===value,original,{timeout:5000});
  }
}
async function playbackButtons(page) {
  const original = await page.evaluate(()=>({station:Number(currentItem),
    playing:document.querySelector('#playerwrap').classList.contains('playing')}));
  const waitPlaying = async () => {
    const start=Date.now();
    try {
      // A station-selection packet can briefly carry the previous playing
      // flag. set_station clears stream identity: require its new format too.
      await page.waitForFunction(()=>document.querySelector('#playerwrap').classList.contains('playing') &&
        /MP3|AAC/.test(document.querySelector('#fmt')?.textContent||'') &&
        !document.querySelector('#playbutton').classList.contains('connecting'),null,{timeout:20000});
      report.controls.push({kind:'decoded-audio-start',elapsedMs:Date.now()-start,pass:true});
    } catch {report.controls.push({kind:'decoded-audio-start',error:'No playing state within 20 s',pass:false});}
    save();
  };
  const action = async (selector,kind,target) => {
    const result=await page.evaluate(({selector,kind,target})=>new Promise(resolve=>{
      const started=performance.now(); let timer;
      const finish=data=>{clearTimeout(timer);websocket.removeEventListener('message',message);resolve(data);};
      const message=event=>{
        let data;try{data=JSON.parse(event.data);}catch{return;}
        const fields=Object.fromEntries((data.payload||[]).map(x=>[x.id,x.value]));
        const confirmed=kind==='station'?Number(data.current)===target:
          kind==='play'?(fields.connecting===true||fields.playerwrap==='playing'):
          fields.playerwrap==='stopped'&&fields.connecting===false;
        if(!confirmed)return;
        finish({kind,selector,target,elapsedMs:performance.now()-started,
          current:Number(currentItem),active:Number(document.querySelector('#playlist li.active')?.getAttribute('attr-id')),
          player:document.querySelector('#playerwrap').className,
          connecting:document.querySelector('#playbutton').classList.contains('connecting')});
      };
      websocket.addEventListener('message',message);
      timer=setTimeout(()=>finish({kind,selector,target,error:'No device confirmation in 5000 ms'}),5000);
      document.querySelector(selector).click();
    }),{selector,kind,target});
    result.pass=!result.error&&result.elapsedMs<=200&&
      (kind!=='station'||(result.current===target&&result.active===target));
    report.controls.push(result);save();console.log(JSON.stringify(result));
    return !result.error;
  };
  try {
    if(original.playing) await action('#playbutton','stop');
    await action('#playbutton','play');await waitPlaying();
    await action('#playbutton','stop');
    const next=await page.evaluate(()=>Number(currentItem)===document.querySelectorAll('#playlist li[attr-id]').length?1:Number(currentItem)+1);
    await action('#nextbutton','station',next);await waitPlaying();
    await action('#prevbutton','station',original.station);await waitPlaying();
    const row=original.station===3?4:3;
    await action(`#playlist li[attr-id="${row}"]`,'station',row);await waitPlaying();
    await action('#playbutton','stop');
  } finally {
    await page.evaluate(station=>websocket.send('play='+station),original.station);
    await page.waitForFunction(station=>Number(currentItem)===station,original.station,{timeout:10000});
    if(!original.playing) {
      await page.evaluate(()=>websocket.send('stop=1'));
      await page.waitForFunction(()=>document.querySelector('#playerwrap').classList.contains('stopped')&&
        !document.querySelector('#playbutton').classList.contains('connecting'),null,{timeout:10000});
    }
  }
}
async function stress(page, context, round) {
  const original=await page.evaluate(()=>({station:Number(currentItem),
    playing:document.querySelector('#playerwrap').classList.contains('playing')}));
  report.playingStates ||= [];
  try {
    // The board's supported playlist used by the full functional audit.
    for(const [station,codec] of [[2,'AAC'],[498,'MP3']]) {
      await page.evaluate(station=>websocket.send('play='+station),station);
      await page.waitForFunction(({station,codec})=>Number(currentItem)===station &&
        document.querySelector('#playerwrap').classList.contains('playing') &&
        document.querySelector('#fmt').textContent.includes(codec),{station,codec},{timeout:20000});
      await page.waitForTimeout(2000);
      const status=async phase=>{
        const state=await page.evaluate(async()=>await (await fetch('/api/native/status',{cache:'no-store'})).json());
        report.playingStates.push({phase,expectedCodec:codec,...state});save();
        if(!state.playing||state.codec!==codec) throw new Error('Audio stopped during '+phase);
      };
      await status('before-'+codec);
      await load(page,'playing-'+codec,round);
      await buttons(page);
      const second=await context.newPage();
      second.on('pageerror',e=>report.errors.push(e.message));
      try {
        // Keep issuing real volume clicks while the other tab loads its shell
        // and entire playlist. No artificial idle gap before each command.
        await Promise.all([load(second,'concurrent-'+codec,round),buttons(page)]);
        await status('two-tabs-'+codec);
      }finally{await second.close();}
    }
  } finally {
    await page.evaluate(station=>websocket.send('play='+station),original.station);
    await page.waitForFunction(station=>Number(currentItem)===station,original.station,{timeout:10000});
    if(!original.playing) {
      await page.evaluate(()=>websocket.send('stop=1'));
      await page.waitForFunction(()=>document.querySelector('#playerwrap').classList.contains('stopped') &&
        !document.querySelector('#playbutton').classList.contains('connecting'),null,{timeout:10000});
    }
  }
}
(async()=>{
  browser=await chromium.launch({channel:option('--channel','msedge'),headless:true,
    args:args.includes('--netlog')?['--log-net-log='+path.resolve(output,'netlog.json'),'--net-log-capture-mode=Default']:[]});
  for(let round=0;round<rounds;round++) {
    const context=await browser.newContext({viewport:{width:1200,height:850}});
    await context.addInitScript(({trace})=>{
      if(trace){
        const timeline=window.__pageTrace={timeOrigin:performance.timeOrigin,sockets:[],longTasks:[],visibility:document.visibilityState};
        addEventListener('DOMContentLoaded',()=>timeline.domContentLoaded=performance.now());
        addEventListener('load',()=>timeline.windowLoad=performance.now());
        const OriginalSocket=WebSocket;
        window.WebSocket=class extends OriginalSocket{
          constructor(...args){
            const item={createdMs:performance.now()};super(...args);timeline.sockets.push(item);
            this.addEventListener('open',()=>item.openedMs=performance.now());
            this.addEventListener('message',()=>{item.firstMessageMs??=performance.now();});
            this.addEventListener('error',()=>item.errorMs=performance.now());
            this.addEventListener('close',e=>{item.closedMs=performance.now();item.closeCode=e.code;});
          }
          send(data){
            if(data==='getindex=1')timeline.indexSentMs=performance.now();
            return super.send(data);
          }
        };
        new PerformanceObserver(list=>{for(const e of list.getEntries())timeline.longTasks.push({startMs:e.startTime,durationMs:e.duration});}).observe({type:'longtask',buffered:true});
      }
      // Measure from navigationStart until the complete player, populated
      // playlist, current selection, live socket and logo are all available.
      const check=()=>{
        const ready=document.querySelector('body > #progress')?.classList.contains('hidden') &&
          document.querySelector('#playlist li.active') && document.querySelector('#logo svg') &&
          typeof websocket!=='undefined' && websocket.readyState===WebSocket.OPEN &&
          typeof currentItem!=='undefined' && Number(currentItem)>0;
        if(ready) window.__readyMs=performance.now(); else requestAnimationFrame(check);
      }; requestAnimationFrame(check);
    },{trace:args.includes('--trace')});
    const page=await context.newPage();
    page.on('pageerror',e=>report.errors.push(e.message));
    const cold=await load(page,'cold',round);
    if(cold) {
      await page.screenshot({path:path.join(output,`cold-${round}.png`)});
      if(args.includes('--controls')) await buttons(page);
      if(args.includes('--playback')) await playbackButtons(page);
      if(args.includes('--stress')) await stress(page,context,round);
      await load(page,'warm',round);
    }
    await context.close();
  }
})().catch(e=>{report.errors.push(e.stack);process.exitCode=1;})
.finally(async()=>{await browser?.close();save();
  if(report.loads.some(x=>!x.pass)||report.controls.some(x=>!x.pass)||report.errors.length) process.exitCode=1;
});
