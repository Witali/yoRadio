#!/usr/bin/env node
// Physical-board test. Read-only unless --controls; then toggle/restore audioinfo.
// Never log Wi-Fi credentials or SSIDs and never change network configuration.
const fs=require('node:fs'), path=require('node:path'), {chromium}=require('playwright');
const args=process.argv.slice(2), option=(key,value)=>args.includes(key)?args[args.indexOf(key)+1]:value;
const base=option('--base','http://192.168.100.6'), output=option('--output','.build/settings-latency');
const report={date:new Date().toISOString(),base,loads:[],controls:[],errors:[]};
fs.mkdirSync(output,{recursive:true});
const save=()=>fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
let browser;
(async()=>{
  browser=await chromium.launch({channel:'msedge',headless:true});
  for(let round=0;round<Number(option('--rounds','3'));round++){
    const context=await browser.newContext();
    await context.addInitScript(()=>{
      const fields={}, received={}; let wifiDone=false;
      const NativeSocket=window.WebSocket;
      window.WebSocket=class extends NativeSocket {
        constructor(...args){super(...args);this.addEventListener('message',event=>{
          const data=JSON.parse(event.data);
          // Retain only numeric fields needed for readback, never credentials.
          for(const key of ['normtime','aif','br','tzh','wint','vols']) if(key in data){fields[key]=data[key];received[key]=performance.now();}
          if(data.act) received.act=performance.now();
          if(data.hide) received.hide=performance.now();
        });}
      };
      const send=XMLHttpRequest.prototype.send;
      XMLHttpRequest.prototype.send=function(...args){
        this.addEventListener('loadend',()=>{
          if(new URL(this.responseURL||location.href).pathname==='/data/wifi.csv') wifiDone=this.status===200;
        });return send.apply(this,args);
      };
      const check=()=>{
        const formReady=['normtime','aif','br','tzh','wint','vols','act','hide'].every(key=>key in received) &&
          document.querySelector('#group_system:not(.hidden)') && document.querySelector('#logo svg') &&
          document.querySelector('body > #progress')?.classList.contains('hidden') && wifiDone &&
          typeof websocket!=='undefined' && websocket.readyState===WebSocket.OPEN;
        if(formReady){
          const matches=['normtime','br','tzh','wint','vols'].every(key=>Number(document.getElementById(key)?.value)===fields[key]) &&
            document.getElementById('aif').classList.contains('checked')===!!fields.aif;
          if(matches){window.__settingsReady={readyMs:performance.now(),received,wifiDone,matches};return;}
        }
        requestAnimationFrame(check);
      };requestAnimationFrame(check);
    });
    const page=await context.newPage();
    page.on('pageerror',error=>report.errors.push(error.message));
    page.on('console',message=>{if(/ws.onMessage error/.test(message.text()))report.errors.push('Caught WebUI message error');});
    for(const kind of ['cold','warm']){
      const sample={round,kind,resources:[]};
      const finished=async req=>{const t=req.timing();sample.resources.push({path:new URL(req.url()).pathname,status:(await req.response()).status(),totalMs:t.responseEnd});};
      page.on('requestfinished',finished);
      try{
        await page.goto(base+'/settings.html',{waitUntil:'domcontentloaded',timeout:30000});
        await page.waitForFunction(()=>window.__settingsReady,null,{timeout:30000});
        Object.assign(sample,await page.evaluate(()=>window.__settingsReady));
        sample.pass=sample.readyMs<=500;
      }catch(error){sample.error=error.message;sample.pass=false;}
      page.off('requestfinished',finished);report.loads.push(sample);save();console.log(JSON.stringify(sample));
      if(sample.error) break;
    }
    if(args.includes('--controls') && await page.evaluate(()=>!!window.__settingsReady)){
      const original=await page.locator('#aif').evaluate(el=>el.classList.contains('checked'));
      try{
        for(let i=0;i<6;i++){
          const result=await page.evaluate(()=>new Promise(resolve=>{
            const before=document.getElementById('aif').classList.contains('checked'), started=performance.now();
            let timer, ackMs;
            const done=result=>{clearTimeout(timer);websocket.removeEventListener('message',message);resolve(result);};
            const message=event=>{const data=JSON.parse(event.data);
              if(data.accepted && ackMs===undefined){ackMs=performance.now()-started;websocket.send('getsystem=1');}
              if('aif' in data && ackMs!==undefined) done({ackMs,readbackMs:performance.now()-started,
                matches:!!data.aif!==before && document.getElementById('aif').classList.contains('checked')===!!data.aif});
            };
            websocket.addEventListener('message',message);
            timer=setTimeout(()=>done({error:'No accepted + saved readback in 5 s'}),5000);
            document.getElementById('aif').click();
          }));
          result.pass=!result.error&&result.matches&&result.ackMs<=200&&result.readbackMs<=200;
          report.controls.push(result);save();console.log(JSON.stringify(result));
        }
      }finally{await page.evaluate(value=>websocket.send('audioinfo='+Number(value)),original);}
    }
    await context.close();
  }
})().catch(error=>{report.errors.push(error.stack);process.exitCode=1;})
.finally(async()=>{await browser?.close();save();if(report.errors.length||[...report.loads,...report.controls].some(x=>!x.pass))process.exitCode=1;});
