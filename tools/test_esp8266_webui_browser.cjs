#!/usr/bin/env node
// Live, opt-in browser audit. Never uploads or formats storage. The optional
// --verify-persistence flag resets the MCU through esptool (no flash writes).
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const args = process.argv.slice(2);
const option = (name, fallback) => { const i = args.indexOf(name); return i < 0 ? fallback : args[i + 1]; };
const host = option('--host', '192.168.100.6');
const output = option('--output', '.build/esp8266-native-current/webui-audit');
const base = `http://${host}`;
const report = { date: new Date().toISOString(), host, checks: [], resources: [], errors: [], sockets: [] };
fs.mkdirSync(output, { recursive: true });
let browser, page;
let messages = [];
let socketCount = 0;
let baseline = {};
let original;
let originalSystem;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const stamp = () => Date.now();
function result(name, pass, detail) {
  report.checks.push({ name, pass, detail });
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name}: ${JSON.stringify(detail)}`);
}
function attach(p, label) {
  p.on('pageerror', e => report.errors.push({ page: label, error: e.message }));
  p.on('console', m => { if (/error|failed/i.test(m.text())) report.errors.push({ page: label, console: m.text().slice(0,500) }); });
  p.on('requestfailed', r => report.errors.push({ page: label, path: new URL(r.url()).pathname, error: r.failure()?.errorText }));
  p.on('requestfinished', async r => {
    try { const response = await r.response(), t = r.timing(); report.resources.push({ page: label, path: new URL(r.url()).pathname, method: r.method(), status: response.status(), durationMs: Math.round(t.responseEnd), ttfbMs: Math.round(t.responseStart) }); } catch {}
  });
  p.on('websocket', ws => {
    const entry = { page: label, openedAt: stamp(), received: 0, sent: 0 };
    report.sockets.push(entry); socketCount++;
    ws.on('framereceived', f => {
      entry.received++;
      try { const data = JSON.parse(f.payload.toString()); messages.push({ at: stamp(), page: label, data }); } catch { report.errors.push({ page:label, error:'Invalid WebSocket JSON' }); }
    });
    ws.on('framesent', () => entry.sent++);
    ws.on('close', () => entry.closedAt = stamp());
  });
  p.on('dialog', d => { report.errors.push({ page:label, dialog:d.message().slice(0,180) }); d.dismiss().catch(()=>{}); });
}
const val = (m,id) => m.data.payload?.find(x=>x.id===id)?.value;
async function waitMessage(after, predicate, timeout=12000, label='main') {
  const end = stamp()+timeout;
  while(stamp()<end) {
    const match = messages.find(m=>m.page===label && m.at>=after && predicate(m));
    if(match) return match;
    await sleep(40);
  }
  throw new Error('WebSocket response timeout');
}
async function query(command, key) {
  const t=stamp();
  await page.evaluate(c=>websocket.send(c),command);
  return (await waitMessage(t,m=>Object.hasOwn(m.data,key))).data;
}
async function snap() {
  return page.evaluate(()=>({
    current: typeof currentItem==='undefined'?null:currentItem,
    station: document.querySelector('#nameset')?.textContent,
    player:document.querySelector('#playerwrap')?.className,
    playPending:document.querySelector('#playbutton')?.getAttribute('aria-disabled'),
    volume:document.querySelector('#volume')?.value,
    format:document.querySelector('#fmt')?.textContent,
    bitrate:document.querySelector('#bitrate')?.textContent,
    rssi:document.querySelector('#rssi')?.textContent,
    scroll:document.querySelector('#playlist')?.scrollTop,
    rows:document.querySelectorAll('#playlist li[attr-id]').length,
    active:document.querySelector('#playlist li.active')?.getAttribute('attr-id'),
    socket:typeof websocket==='undefined'?null:websocket.readyState
  }));
}
async function action(name, selector, predicate, timeout=12000) {
  const t=stamp();
  try { await page.locator(selector).click(); const m=await waitMessage(t,predicate,timeout); result(name,true,{ms:m.at-t,state:await snap()}); }
  catch(e){ result(name,false,{error:e.message,state:await snap()}); }
}
async function statusTimings(label) {
  const samples=[];
  for(let i=0;i<4;i++) {
    const t=stamp();
    try { const s=await page.evaluate(async()=>{const r=await fetch('/api/native/status',{cache:'no-store',signal:AbortSignal.timeout(10000)});return {status:r.status,...await r.json()};}); samples.push({ms:stamp()-t,...s}); }
    catch(e){samples.push({ms:stamp()-t,error:e.message});}
    await sleep(150);
  }
  result(`status latency ${label}`,samples.every(x=>x.status===200),samples);
}
async function loadPlayer(label) {
  const t=stamp();
  console.log('RUN', label);
  await page.goto(`${base}/?ui=audit-20260905`,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>document.querySelectorAll('#playlist li[attr-id]').length>0 && typeof currentItem!=='undefined' && currentItem>0,{},{timeout:60000});
  result(label,true,{ms:stamp()-t,state:await snap()});
}
async function testSetting(id, command, queryCommand, key, newValue, checkbox=false) {
  const unsupported = ['scre','scrt','scrb','dspon','scrpe','scrpt','watchdog','enca'];
  if(unsupported.includes(id)) {
    result('unsupported control hidden: '+id, !(await page.locator('#'+id).isVisible()), {});
    return;
  }
  console.log('RUN setting', id);
  const initial=(await query(queryCommand,key))[key];
  baseline[command]=initial;
  const t=stamp();
  const el=page.locator('#'+id);
  if(!checkbox && String(newValue)===String(initial)) newValue=Number(initial)+1;
  if(checkbox) await el.click(); else if(await el.evaluate(e=>e.tagName==='SELECT')) await el.selectOption(String(newValue)); else await el.fill(String(newValue));
  await sleep(200);
  const changed=(await query(queryCommand,key))[key];
  const expected=checkbox?(initial?0:1):newValue;
  result(`setting ${id}`,String(changed)===String(expected),{initial,expected,actual:changed,ms:stamp()-t});
  await page.evaluate(({c,v})=>websocket.send(`${c}=${v}`),{c:command,v:initial});
  await sleep(150);
}
(async()=>{
  browser=await chromium.launch({channel:option('--channel','msedge'),headless:true});
  page=await browser.newPage({viewport:{width:1280,height:800}});
  page.setDefaultTimeout(12000); attach(page,'main');
  // Do not include OS SYN retransmission while the MCU is still acquiring
  // Wi-Fi/DHCP in the page-load measurement. No browser cache is warmed here.
  const readyUntil=stamp()+90000;
  let ready=false;
  while(stamp()<readyUntil && !ready) {
    try {
      const r=await page.request.get(base+'/api/native/status',{timeout:5000});
      ready=r.ok() && (await r.json()).network===1;
    } catch {}
    if(!ready) { console.log('WAIT board HTTP readiness'); await sleep(1000); }
  }
  if(!ready) throw new Error('Board HTTP did not become ready');
  await loadPlayer('cold player load');
  original=await snap(); report.original=original;
  // The playlist uses smooth scrolling. Presence of rows is not its completion.
  await page.waitForFunction(()=>{
    const ul=document.querySelector('#playlist'), active=ul?.querySelector('li.active');
    if(!active) return false;
    const a=active.getBoundingClientRect(), b=ul.getBoundingClientRect();
    return a.top>=b.top && a.bottom<=b.bottom;
  },{},{timeout:3000}).catch(()=>{});
  const selectedVisible=await page.locator('#playlist').evaluate(ul=>{
    const active=ul.querySelector('li.active');
    if(!active) return false;
    const a=active.getBoundingClientRect(), b=ul.getBoundingClientRect();
    return a.top>=b.top && a.bottom<=b.bottom;
  });
  result('current station visible on initial load',selectedVisible,{current:original.current,scroll:(await snap()).scroll});
  if(args.includes('--bootstrap-only')) {
    await statusTimings('bootstrap');
    await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
    return;
  }
  originalSystem=await query('getsystem=1','normtime');
  if(original.player.includes('playing')) {await action('initial pause','#playbutton',m=>val(m,'playerwrap')==='stopped');await sleep(800);}
  await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
  await statusTimings('stopped');
  const requests=()=>report.resources.filter(r=>r.path==='/data/playlist.csv').length;
  const beforeSearch=requests(); let t=stamp();
  await page.locator('#playlistfilter').fill('opera');
  const count=await page.locator('#playlist li:not(.filtered)').count();
  result('station search',count>0 && count<original.rows,{ms:stamp()-t,count,networkReloads:requests()-beforeSearch});
  await page.locator('#playlistfilter').fill('');
  result('clear search',(await page.locator('#playlist li:not(.filtered)').count())===original.rows,{rows:original.rows});
  const beforeRow=await snap(); const reloads=requests();
  await action('AAC station row click','#playlist li[attr-id="2"]',m=>val(m,'playerwrap')==='playing',20000);
  await sleep(1200);
  result('station row selected without playlist reload',Number((await snap()).active)===2 && requests()===reloads,{reloads:requests()-reloads,scrollBefore:beforeRow.scroll,scrollAfter:(await snap()).scroll});
  await statusTimings('AAC playback');
  let start=stamp(); const socketsBefore=socketCount; await sleep(6500);
  const beats=messages.filter(m=>m.at>=start && val(m,'rssi')!==undefined);
  result('live playback heartbeat',beats.length>=2 && socketCount===socketsBefore,{count:beats.length,gapsMs:beats.slice(1).map((m,i)=>m.at-beats[i].at),socketReconnects:socketCount-socketsBefore});
  await action('pause','#playbutton',m=>val(m,'playerwrap')==='stopped');
  await sleep(700); const stopScroll=(await snap()).scroll;
  await sleep(2200); result('stop preserves playlist scroll',(await snap()).scroll===stopScroll,{scroll:stopScroll});
  await action('resume','#playbutton',m=>val(m,'playerwrap')==='playing',20000);
  await action('next','#nextbutton',m=>m.data.current===3);
  await action('previous','#prevbutton',m=>m.data.current===2);
  await sleep(1500);
  const v=Number((await snap()).volume);
  await action('volume down','#volmbutton',m=>val(m,'volume')<v);
  await action('volume up','#volpbutton',m=>val(m,'volume')===v);
  await page.locator('#eqalbutton').click();
  const oldBalance=Number(await page.locator('#balance').inputValue());
  await page.locator('#balance').focus(); t=stamp();
  await page.keyboard.press(oldBalance<16?'ArrowRight':'ArrowLeft');
  // A status broadcast already in flight can satisfy a payload query with the
  // old value. Allow the input command to settle before asking for readback.
  await sleep(500);
  const balance=(await query('getindex=1','payload')).payload.find(x=>x.id==='balance')?.value;
  result('balance slider',balance===oldBalance+(oldBalance<16?1:-1),{initial:oldBalance,value:balance,ms:stamp()-t});
  await page.evaluate(v=>websocket.send(`balance=${v}`),oldBalance);
  baseline.balance=oldBalance;
  await page.locator('#equalizer [data-target="equalizerbg"]').click();
  for(const [index,label] of [[498,'MP3 ROCK FM'],[502,'MP3 Europa Plus']]) {
    await page.evaluate(()=>websocket.send('stop=1')); await sleep(1000);
    await page.locator('#playlistfilter').fill(index===500?'Говорит Москва':index===498?'ROCK FM':'Европа Плюс');
    const name=await page.locator(`#playlist li[attr-id="${index}"]`).getAttribute('data-name');
    await action(`station ${label}`,`#playlist li[attr-id="${index}"]`,m=>val(m,'playerwrap')==='playing' && val(m,'nameset')===name && /^MP3 /.test(val(m,'fmt')||''),18000);
    await sleep(2500); await statusTimings(label);
  }
  // Use the browser socket for teardown so a second client cannot evict it.
  await page.evaluate(()=>websocket.send('stop=1')); await sleep(1200);
  await page.locator('#playlistfilter').fill('');
  t=stamp(); await page.locator('#logow [data-command="settings"]').click();
  await page.waitForURL('**/settings.html*',{timeout:60000});
  await page.waitForSelector('#group_system:not(.hidden)',{timeout:60000});
  await sleep(1500);
  result('settings navigation',true,{ms:stamp()-t});
  report.settingsControls=await page.locator('input[id],select[id],.checkbox[id],.fb[data-command]').evaluateAll(es=>es.filter(e=>e.getClientRects().length).map(e=>({id:e.id,command:e.dataset.command,type:e.type||e.className,text:(e.innerText||'').slice(0,65),value: /ssid|pass|sntp/i.test(e.id)?undefined:e.value})));
  await page.screenshot({path:path.join(output,'settings.png'),fullPage:true});
  for(const args of [
    ['sst','smartstart','getsystem=1','sst',0,true],
    ['normalize','normalization','getsystem=1','normalize',0,true],
    ['normtime','normtime','getsystem=1','normtime',4000],
    ['normgain','normgain','getsystem=1','normgain',12],
    ['normtarget','normtarget','getsystem=1','normtarget',-6],
    ['aif','audioinfo','getsystem=1','aif',0,true],
    ['softr','softap','getsystem=1','softr',1],
    ['upst','stationuppercase','getscreen=1','upst',0,true],
    ['nump','numplaylist','getscreen=1','nump',0,true],
    ['scre','screensaverenabled','getscreen=1','scre',0,true],
    ['scrt','screensavertimeout','getscreen=1','scrt',25],
    ['scrb','screensaverblank','getscreen=1','scrb',1],
    ['dspon','screenon','getscreen=1','dspon',0,true],
    ['scrpe','screensaverplayingenabled','getscreen=1','scrpe',0,true],
    ['scrpt','screensaverplayingtimeout','getscreen=1','scrpt',6],
    ['watchdog','watchdog','getsystem=1','watchdog',0,true],
    ['timeint','timeint','gettimezone=1','timeint',61],
    ['vols','volsteps','getcontrols=1','vols',2],
    ['enca','encacc','getcontrols=1','enca',50]
  ]) { try { await testSetting(...args); } catch(e){result(`setting ${args[0]}`,false,{error:e.message});} }
  // Leave a reversible value different while reloading to check actual saved state.
  const system=await query('getsystem=1','normtime'); const oldTime=system.normtime;
  await page.locator('#normtime').fill(oldTime===4000?'5000':'4000');
  const target=oldTime===4000?5000:4000;
  await sleep(6000);
  result('settings field not overwritten by telemetry',Number(await page.locator('#normtime').inputValue())===target,{target,actual:await page.locator('#normtime').inputValue()});
  t=stamp(); await page.reload({waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForSelector('#group_system:not(.hidden)',{timeout:60000}); await sleep(800);
  result('settings survive page reload',Number(await page.locator('#normtime').inputValue())===target,{ms:stamp()-t,target,actual:await page.locator('#normtime').inputValue()});
  await page.locator('#normtime').fill(String(oldTime)); await sleep(1500);
  result('compile-time MP3 decoder selector hidden',await page.locator('#mp3decoder:visible').count()===0,{});
  if(args.includes('--verify-persistence')) {
    const python=option('--python',null), esptool=option('--esptool',null);
    if(!python || !esptool) throw new Error('--verify-persistence requires --python and --esptool; close serial monitors first');
    const savedTime=(await query('getsystem=1','normtime')).normtime;
    const trialTime=savedTime===6000?7000:6000;
    const trialVolume=Number(original.volume)>2?Number(original.volume)-2:4;
    await page.evaluate(({time,volume})=>{
      websocket.send(`normtime=${time}`); websocket.send(`volume=${volume}`);
      websocket.send('smartstart=0');
    },{time:trialTime,volume:trialVolume});
    await sleep(2500); // Deferred NVS commit is one second after the last change.
    // Stop the old page's reconnect loop before resetting the server.
    await page.goto('about:blank');
    const reset=require('node:child_process').spawnSync(python,[esptool,'--chip','esp8266','--port',option('--port','COM8'),'--before','default_reset','--after','hard_reset','flash_id'],{encoding:'utf8',timeout:30000,windowsHide:true});
    report.reset={status:reset.status,error:reset.error?.message};
    if(reset.status!==0) throw new Error(`MCU reset failed: ${reset.stderr || reset.error?.message}`);
    let ready=false;
    for(let attempt=0;attempt<8&&!ready;attempt++) {
      await sleep(1500);
      try {
        const response=await page.request.get(base+'/api/native/status',{timeout:8000});
        ready=response.ok() && (await response.json()).network===1;
      } catch {}
    }
    if(!ready) throw new Error('HTTP did not recover after MCU reset; restore settings after board recovery');
    await page.goto(base+'/settings.html?ui=audit-20260905',{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForSelector('#group_system:not(.hidden)',{timeout:60000});
    const stored=(await query('getsystem=1','normtime')).normtime;
    const storedVolume=(await query('getindex=1','payload')).payload.find(x=>x.id==='volume')?.value;
    result('normalization persists across MCU reset',stored===trialTime,{expected:trialTime,actual:stored});
    result('volume persists across MCU reset',storedVolume===trialVolume,{expected:trialVolume,actual:storedVolume});
    await page.evaluate(({time,volume})=>{
      websocket.send(`normtime=${time}`); websocket.send(`volume=${volume}`);
    },{time:savedTime,volume:Number(original.volume)});
    await sleep(1500);
  }
  // GET-only capability checks; deliberately no upload or reset commands.
  for(const route of ['/data/wifi.csv','/webboard','/update.html','/updform.html']) {
    t=stamp();
    try{ const r=await page.request.get(base+route,{timeout:15000});result(`route ${route}`,r.status()===200,{status:r.status(),ms:stamp()-t}); }catch(e){result(`route ${route}`,false,{error:e.message});}
  }
  await loadPlayer('warm player load');
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
  const widths=await page.evaluate(()=>({viewport:innerWidth,body:document.body.scrollWidth,document:document.documentElement.scrollWidth}));
  result('mobile width',widths.document<=widths.viewport,widths);
  const beforeTabs=socketCount; const second=await browser.newPage({viewport:{width:390,height:844}}); attach(second,'second');
  await second.goto(base+'/?ui=audit-second',{waitUntil:'domcontentloaded',timeout:60000});
  await second.waitForSelector('#playbutton',{timeout:60000});
  await sleep(10000);
  result('two concurrent tabs',report.sockets.filter(s=>s.closedAt && s.openedAt>report.sockets[beforeTabs-1]?.openedAt).length===0,{newSockets:socketCount-beforeTabs,sockets:report.sockets.slice(beforeTabs-1)});
  const tabVolume=Number((await snap()).volume);
  let changeAt=stamp();
  await page.locator('#volmbutton').click();
  await waitMessage(changeAt,m=>val(m,'volume')<tabVolume,12000,'main');
  await waitMessage(changeAt,m=>val(m,'volume')<tabVolume,12000,'second');
  result('main tab command updates both subscribers',true,{ms:stamp()-changeAt});
  changeAt=stamp();
  await second.evaluate(v=>websocket.send('volume='+v),tabVolume);
  await waitMessage(changeAt,m=>val(m,'volume')===tabVolume,12000,'main');
  await waitMessage(changeAt,m=>val(m,'volume')===tabVolume,12000,'second');
  result('second tab command updates both subscribers',true,{ms:stamp()-changeAt});
  await statusTimings('two tabs stopped');
  await second.close(); await sleep(2300);
})().catch(e=>{report.fatal=e.stack;console.error('FATAL',e.message);process.exitCode=1;}).finally(async()=>{
  if(page && original) {
    try {
      await page.waitForFunction(()=>typeof websocket!=='undefined' && websocket.readyState===1,{},{timeout:15000});
      for(const [command,value] of Object.entries(baseline)) {await page.evaluate(({command,value})=>websocket.send(`${command}=${value}`),{command,value});await sleep(80);}
      const station=Number(option('--restore-station',original.current));
      await page.evaluate(({v,i})=>{websocket.send(`volume=${v}`);websocket.send(`play=${i}`);},{v:original.volume,i:station});
      await sleep(1300);
      const state=await query('getindex=1','payload');
      if(args.includes('--leave-stopped') || !original.player.includes('playing')) {await page.evaluate(()=>websocket.send('stop=1'));await sleep(1300);}
      if(originalSystem) {await page.evaluate(v=>websocket.send(`smartstart=${v}`),originalSystem.sst);await sleep(1300);}
      report.restored={station,volume:state.payload.find(x=>x.id==='volume')?.value};
    } catch(e) { report.restoreError=e.message; process.exitCode=1; }
  }
  // Persist diagnostic output even if the board becomes unresponsive.
  if(page&&!page.isClosed()) report.final=await snap().catch(()=>null);
  report.finished=new Date().toISOString();
  fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(report,null,2));
  await browser?.close();
  if(report.checks.some(c=>!c.pass)) process.exitCode=1;
  console.log('REPORT',path.join(output,'results.json'));
});
