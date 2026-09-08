#!/usr/bin/env node
// Opt-in browser smoke: two subscribers, ten volume actions, no uploads/reset.
// Restores the exact original volume; never selects or starts a station.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const args=process.argv.slice(2),opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
const base=opt('--base','http://192.168.100.6');
const output=opt('--output','.build/esp8266-network-cpu/production-web.json');
const report={started:new Date().toISOString(),base,loads:[],actions:[],errors:[],sockets:[],health:[]};
const pages=[],messages=[];let browser,originalVolume;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const value=(data,id)=>data.payload?.find(p=>p.id===id)?.value;
async function state(page) {
  return page.evaluate(()=>({current:currentItem,volume:Number(document.querySelector('#volume').value),
    player:document.querySelector('#playerwrap').className,rows:document.querySelectorAll('#playlist li[attr-id]').length,
    active:document.querySelector('#playlist li.active')?.getAttribute('attr-id'),
    socket:websocket.readyState,scroll:document.querySelector('#playlist').scrollTop}));
}
async function health(label) {
  const r=await pages[0].request.get(base+'/api/native/status',{timeout:10000});
  if(!r.ok())throw Error('status HTTP '+r.status());
  report.health.push({label,...await r.json()});
}
async function waitVolume(after,expected) {
  const end=Date.now()+12000;
  while(Date.now()<end) {
    const found=[0,1].map(tab=>messages.find(m=>m.tab===tab&&m.at>=after&&Number(value(m.data,'volume'))===expected));
    if(found.every(Boolean))return found.map(m=>m.at-after);
    await sleep(25);
  }
  throw Error('Both subscribers did not acknowledge volume '+expected);
}
async function main() {
  browser=await chromium.launch({channel:opt('--channel','msedge'),headless:true});
  for(let tab=0;tab<2;tab++) {
    const page=await browser.newPage({viewport:{width:tab?390:1200,height:800}});pages.push(page);
    page.on('pageerror',e=>report.errors.push({tab,error:e.message}));
    page.on('requestfailed',r=>report.errors.push({tab,path:new URL(r.url()).pathname,error:r.failure()?.errorText}));
    page.on('websocket',ws=>{
      const socket={tab,opened:Date.now(),frames:0};report.sockets.push(socket);
      ws.on('close',()=>socket.closed=Date.now());
      ws.on('framereceived',f=>{socket.frames++;try{messages.push({tab,at:Date.now(),data:JSON.parse(f.payload.toString())});}catch{report.errors.push({tab,error:'Invalid WS JSON'});}});
    });
    const start=Date.now();
    await page.goto(base+'/?ui=wifi-rx-smoke',{waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForFunction(()=>typeof websocket!=='undefined'&&websocket.readyState===1&&
      typeof currentItem!=='undefined'&&currentItem>0&&document.querySelectorAll('#playlist li[attr-id]').length>0,null,{timeout:45000});
    const readyMs=Date.now()-start;
    await page.waitForFunction(()=>{
      const ul=document.querySelector('#playlist'),active=ul?.querySelector('li.active');
      if(!active)return false;
      const a=active.getBoundingClientRect(),b=ul.getBoundingClientRect();
      return a.top>=b.top&&a.bottom<=b.bottom;
    },null,{timeout:3000});
    const current=await state(page);report.loads.push({tab,ms:readyMs,state:current});
    if(tab===0)originalVolume=current.volume;
    console.log('LOAD',JSON.stringify(report.loads.at(-1)));
  }
  await health('two-tabs-before');
  for(let trial=0;trial<10;trial++) {
    const tab=trial%2,current=await state(pages[tab]);
    const selector=current.volume>=254?'#volmbutton':current.volume<=0?'#volpbutton':trial%2?'#volpbutton':'#volmbutton';
    const start=Date.now();await pages[tab].locator(selector).click();
    const end=Date.now()+12000;let own;
    while(Date.now()<end&&!own) {
      own=messages.find(m=>m.tab===tab&&m.at>=start&&value(m.data,'volume')!==undefined&&Number(value(m.data,'volume'))!==current.volume);
      if(!own)await sleep(25);
    }
    if(!own)throw Error('Click did not change volume');
    const expected=Number(value(own.data,'volume'));
    const delays=await waitVolume(start,expected);
    report.actions.push({trial,tab,selector,expected,ack_ms:delays});
    console.log('ACTION',JSON.stringify(report.actions.at(-1)));
    await health('action-'+trial);await sleep(150);
  }
  await sleep(5000);
  report.beforeClose=await Promise.all(pages.map(state));
  fs.mkdirSync(path.dirname(output),{recursive:true});
  for(let tab=0;tab<pages.length;tab++)await pages[tab].screenshot({path:output.replace(/\.json$/,`-tab${tab}.png`),fullPage:true});
  report.pass=report.actions.length===10&&report.sockets.length===2&&report.sockets.every(s=>!s.closed&&s.frames>0)&&!report.errors.length;
}
main().catch(e=>{report.fatal=e.stack;report.pass=false;}).finally(async()=>{
  if(pages[0]&&Number.isFinite(originalVolume)) {
    try {
      const at=Date.now();await pages[0].evaluate(v=>websocket.send('volume='+v),originalVolume);
      await waitVolume(at,originalVolume);await sleep(1500);
      report.restored=await Promise.all(pages.map(state));
      if(report.restored.some(s=>s.volume!==originalVolume))throw Error('Volume restore mismatch');
    }catch(e){report.restoreError=e.message;report.pass=false;}
  }
  report.finished=new Date().toISOString();
  fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  await browser?.close();console.log('RESULT',JSON.stringify({pass:report.pass,fatal:report.fatal,restoreError:report.restoreError,output}));
  process.exitCode=report.pass?0:1;
});
