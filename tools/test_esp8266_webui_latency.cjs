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
  const finished = async req => {
    const res = await req.response(), t = req.timing();
    sample.resources.push({path:new URL(req.url()).pathname, status:res.status(),
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
      player:document.querySelector('#playerwrap')?.className})));
    sample.pass = sample.readyMs <= 500;
  } catch(e) {sample.error=e.message; sample.pass=false;}
  page.off('requestfinished', finished); page.off('requestfailed', failed);
  report.loads.push(sample); save();
  console.log(JSON.stringify(sample));
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
(async()=>{
  browser=await chromium.launch({channel:option('--channel','msedge'),headless:true});
  for(let round=0;round<rounds;round++) {
    const context=await browser.newContext({viewport:{width:1200,height:850}});
    await context.addInitScript(()=>{
      // Measure from navigationStart until the complete player, populated
      // playlist, current selection, live socket and logo are all available.
      const check=()=>{
        const ready=document.querySelector('body > #progress')?.classList.contains('hidden') &&
          document.querySelector('#playlist li.active') && document.querySelector('#logo svg') &&
          typeof websocket!=='undefined' && websocket.readyState===WebSocket.OPEN &&
          typeof currentItem!=='undefined' && Number(currentItem)>0;
        if(ready) window.__readyMs=performance.now(); else requestAnimationFrame(check);
      }; requestAnimationFrame(check);
    });
    const page=await context.newPage();
    page.on('pageerror',e=>report.errors.push(e.message));
    const cold=await load(page,'cold',round);
    if(cold) {
      await page.screenshot({path:path.join(output,`cold-${round}.png`)});
      if(args.includes('--controls')) await buttons(page);
      if(args.includes('--playback')) await playbackButtons(page);
      await load(page,'warm',round);
    }
    await context.close();
  }
})().catch(e=>{report.errors.push(e.stack);process.exitCode=1;})
.finally(async()=>{await browser?.close();save();
  if(report.loads.some(x=>!x.pass)||report.controls.some(x=>!x.pass)||report.errors.length) process.exitCode=1;
});
