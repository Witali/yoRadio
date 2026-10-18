const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const page = fs.readFileSync(path.join(__dirname, '../idf/esp32-cyd2usb-native/main/web_pages.cpp'), 'utf8');
const script = page.split('// NATIVE_UI_BEGIN')[1].split('// NATIVE_UI_END')[0];
const tick = () => new Promise(resolve => setImmediate(resolve));

function harness(failBoot = false, overrides = {}) {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {id, value:'', checked:false, disabled:true, hidden:true, textContent:'', files:[],
      listeners:{}, addEventListener(event, fn) { this.listeners[event] = fn; }});
    return elements.get(id);
  };
  const radioButtons = ['previous','toggle','next','stop'].map(action => ({...element(action),dataset:{radio:action}}));
  const buttons = [...radioButtons,element('station-submit'),element('audio-submit'),element('reconnect'),
    ...['playlist','assets','wifi'].map(name=>element(name+'-submit'))];
  const timers = new Map(), intervals = [], sockets = [], requests = [];
  let nextTimer = 0, now = 1000, failSettings = false, failStatus = false, failUpload = '', holdUpload = false;
  const pendingUploads = [];
  const capabilities = {audio_output:'PDM',websocket:true,smartstart:true,wifi_reconnect:true,
    playlist_upload:true,asset_upload:true,wifi_upload:true,upload_max_bytes:98304,upload_max_files:16,
    upload_name_max_bytes:22,wifi_file_max_bytes:799,wifi_body_max_bytes:4096,
    wifi_ssid_max_bytes:31,wifi_password_max_bytes:63,...overrides};
  const settings = {volume:123,balance:-4,normalization:false,normgain:12,normtarget:-6,normtime:6000};
  const state = {station:'Радио', title:'Название', format:'MP3 44.1kHz',bitrate:128,audio:true};
  const radio = {current:7,count:15,smartstart:false};
  class Socket {
    static OPEN = 1;
    constructor(url) { this.url=url;this.readyState=0;sockets.push(this); }
    close() { this.readyState=3;this.onclose?.(); }
    open() { this.readyState=1;this.onopen?.(); }
    message(value) { this.onmessage?.({data:JSON.stringify(value)}); }
  }
  const context = vm.createContext({console,URL,URLSearchParams,FormData,Request,TextEncoder,WebSocket:Socket,
    location:{protocol:'http:',host:'radio.local',href:'http://radio.local/'},Date:{now:()=>now},
    document:{getElementById:element,activeElement:null,
      querySelectorAll: selector => selector === '[data-radio]' ? radioButtons : buttons},
    setTimeout(fn, ms) { timers.set(++nextTimer,{fn,ms});return nextTimer; },
    clearTimeout(id) { timers.delete(id); },setInterval(fn) { intervals.push(fn); },
    async fetch(url, options) {
      if (url instanceof Request) {
        requests.push({url:new URL(url.url).pathname,method:url.method,request:url.clone()});
        const error = failUpload;failUpload='';
        const response = {ok:!error,status:error?400:200,text:async()=>error||'<html>redirected native page</html>'};
        if (holdUpload) return new Promise(resolve=>pendingUploads.push(()=>resolve(response)));
        return response;
      }
      requests.push({url,...options});
      const uri = new URL(url,'http://radio.local');
      const name = uri.pathname.split('/').at(-1);
      if ((failBoot && name === 'capabilities') || (failSettings && name === 'settings' && options.method==='POST') ||
          (failStatus && name === 'status')) {
        failSettings=false;failStatus=false;
        return {ok:false,text:async()=>'Сохранение не удалось'};
      }
      const data = name === 'capabilities' ? capabilities :
        name === 'settings' ? settings : name === 'radio' ? radio : name === 'status' ? state : {reconnecting:true};
      return {ok:true,json:async()=>structuredClone(data)};
    }});
  vm.runInContext(script,context);
  return {element,context,buttons,radioButtons,sockets,requests,timers,intervals,settings,radio,state,capabilities,
    setNow(value) { now=value; },failSettings() { failSettings=true; },failStatus() { failStatus=true; },
    failUpload(text) { failUpload=text; },holdUploads() { holdUpload=true; },
    releaseUploads() { holdUpload=false;for(const resolve of pendingUploads.splice(0))resolve(); },
    uploads:()=>requests.filter(item=>item.request),pendingUploads};
}

async function waitFor(predicate) {
  for(let attempt=0;attempt<200;++attempt){if(predicate())return;await tick();}
  assert.fail('Native page did not finish the expected asynchronous upload step');
}
const file = (name,body='station\thttps://fixture.invalid/audio\n') => new File([body],name);
const submit = (h,name) => h.element(name+'-form').listeners.submit({preventDefault(){}});

test('native page boots sequentially and renders status as plain text', async () => {
  const h=harness();
  assert(h.buttons.every(button=>button.disabled));
  await tick();
  assert.deepEqual(h.requests.map(request=>request.url),[
    '/api/native/capabilities','/api/native/status','/api/native/radio','/api/native/settings']);
  assert(h.buttons.every(button=>!button.disabled));
  assert.equal(h.element('volume').value,123);
  assert.equal(h.element('station-number').value,7);
  assert.equal(h.element('station-number').max,'15');
  assert.equal(h.sockets[0].url,'ws://radio.local/ws');
  h.sockets[0].open();
  h.sockets[0].message({status:{station:'<img onerror=bad()>',title:'Трек " \\ 🌍',format:'AAC PCM',bitrate:64,connecting:true}});
  assert.equal(h.element('station').textContent,'<img onerror=bad()>');
  assert.equal(h.element('title').textContent,'Трек " \\ 🌍');
  assert.match(h.element('details').textContent,/64 кбит\/с/);
  assert.equal(h.element('station').innerHTML,undefined);
});

test('radio/audio controls send complete values and recover after persistence failure', async () => {
  const h=harness();await tick();
  h.radioButtons[2].listeners.click();await tick();
  assert(h.requests.some(request=>request.url==='/api/native/radio?action=next' && request.method==='POST'));
  h.element('station-number').value='12';
  h.element('station-form').listeners.submit({preventDefault(){}});await tick();
  assert(h.requests.some(request=>request.url==='/api/native/radio?action=play&station=12'));
  h.element('normalization').checked=true;h.element('normtarget').value='-9';
  h.failSettings();h.element('audio-form').listeners.submit({preventDefault(){}});await tick();
  const update=h.requests.find(request=>request.url.startsWith('/api/native/settings?'));
  const query=new URL(update.url,'http://radio').searchParams;
  assert.equal(query.get('normalization'),'1');assert.equal(query.get('normtarget'),'-9');
  assert.equal(query.get('volume'),'123');assert.equal(update.method,'POST');
  assert.equal(h.element('normalization').checked,false);
  assert.match(h.element('message').textContent,/Сохранение/);
});

test('disconnect uses one bounded retry, ignores old socket frames and polls while disconnected', async () => {
  const h=harness();await tick();const first=h.sockets[0];first.open();first.close();
  assert.equal(h.timers.size,1);assert.equal([...h.timers.values()][0].ms,1000);
  h.intervals[0]();await tick();assert.equal(h.requests.at(-1).url,'/api/native/radio');
  const retry=[...h.timers.values()][0];h.timers.clear();retry.fn();
  const second=h.sockets[1];second.open();
  first.message({status:{station:'stale'}});assert.notEqual(h.element('station').textContent,'stale');
  second.message({status:{station:'current'}});assert.equal(h.element('station').textContent,'current');
  h.setNow(8001);h.intervals[0]();await tick();
  assert.equal(second.readyState,3);assert.equal(h.timers.size,1);
});

test('failed initial service keeps controls disabled and shows failure', async () => {
  const h=harness(true);await tick();
  assert(h.buttons.every(button=>button.disabled));assert.equal(h.sockets.length,0);
  assert.match(h.element('connection').textContent,/недоступен/);
});

test('cross-tab updates refresh radio/settings while preserving unsaved form edits', async () => {
  const h=harness();await tick();const socket=h.sockets[0];socket.open();
  socket.message({status:{...h.settings,volume:50,normalization:true,current:9,count:20,smartstart:true}});
  assert.equal(h.element('volume').value,50);assert.equal(h.element('normalization').checked,true);
  assert.equal(h.element('smartstart').checked,true);assert.equal(h.element('station-number').value,9);
  h.element('volume').value='87';h.element('audio-form').listeners.input();
  socket.message({status:{...h.settings,volume:20,current:10,count:20,smartstart:false}});
  assert.equal(h.element('volume').value,'87');assert.equal(h.element('station-number').value,10);
});

test('playlist upload uses native multipart and refreshes count only after HTTP success', async () => {
  const h=harness();await tick();h.holdUploads();
  h.element('playlist-file').files=[file('my-stations.csv')];submit(h,'playlist');
  await waitFor(()=>h.uploads().length===1);
  const sent=h.uploads()[0];assert.equal(sent.url,'/upload');assert.equal(sent.method,'POST');
  assert.match(sent.request.headers.get('Content-Type'),/^multipart\/form-data; boundary=/);
  const data=await sent.request.clone().formData();
  assert.equal(data.get('plfile').name,'my-stations.csv');assert.equal([...data].length,1);
  assert(['playlist','assets','wifi'].every(name=>h.element(name+'-fields').disabled));
  h.radio.count=23;assert.equal(h.element('station-count').textContent,'из 15');
  const before=h.requests.length;h.intervals[0]();await tick();assert.equal(h.requests.length,before);
  h.releaseUploads();await waitFor(()=>!h.element('playlist-fields').disabled);
  assert.equal(h.element('station-count').textContent,'из 23');
  assert.deepEqual(h.requests.slice(5).map(item=>item.url),['/api/native/radio','/api/native/status']);
  assert.equal(h.element('message').textContent,'Файлы сохранены');
});

test('upload failure shows response text and keeps the old count and selected file', async () => {
  const h=harness();await tick();const selected=file('stations.csv');h.element('playlist-file').files=[selected];
  h.radio.count=99;h.failUpload('Storage full <b>retry</b>');submit(h,'playlist');
  await waitFor(()=>h.element('message').textContent==='Storage full <b>retry</b>');
  assert.equal(h.element('message').innerHTML,undefined);assert.equal(h.element('station-count').textContent,'из 15');
  assert.equal(h.requests.length,5);assert.equal(h.element('playlist-file').files[0],selected);
  assert.equal(h.element('playlist-fields').disabled,false);
});

test('one local upload locks all forms and prevents a second POST until completion', async () => {
  const h=harness();await tick();h.holdUploads();h.element('asset-files').files=[file('theme.css.gz','compressed')];
  h.element('wifi-ssid').value='fixture';h.element('wifi-password').value='pass';submit(h,'assets');
  await waitFor(()=>h.uploads().length===1);submit(h,'wifi');await tick();
  assert.match(h.element('message').textContent,/Дождитесь/);assert.equal(h.uploads().length,1);
  assert(['playlist','assets','wifi'].every(name=>h.element(name+'-submit').disabled));
  h.releaseUploads();await waitFor(()=>!h.element('assets-fields').disabled);
  submit(h,'wifi');await waitFor(()=>h.uploads().length===2&&!h.element('wifi-fields').disabled);
  assert.match(h.element('message').textContent,/перезапустится/);
});

test('Wi-Fi form preserves field whitespace and announces restart after redirected success', async () => {
  const h=harness();await tick();h.element('wifi-ssid').value=' сеть ';h.element('wifi-password').value=' pass ';
  submit(h,'wifi');await waitFor(()=>h.uploads().length===1&&!h.element('wifi-fields').disabled);
  const sent=h.uploads()[0];assert.equal(sent.url,'/');assert.equal(sent.method,'POST');
  const data=await sent.request.clone().formData();assert.equal(data.get('ssid'),' сеть ');assert.equal(data.get('pass'),' pass ');
  assert.match(h.element('message').textContent,/Wi-Fi сохранён.*перезапустится/);
  assert.equal(h.element('wifi-password').value,'');assert.equal(h.requests.length,5);
  assert.equal(h.element('station-count').textContent,'из 15');
});

test('Wi-Fi allows an empty password and keeps it after an HTTP persistence error', async () => {
  const h=harness();await tick();h.element('wifi-ssid').value='open fixture';h.element('wifi-password').value='';
  submit(h,'wifi');await waitFor(()=>h.uploads().length===1&&!h.element('wifi-fields').disabled);
  assert.equal((await h.uploads()[0].request.clone().formData()).get('pass'),'');
  h.element('wifi-password').value='retained';h.failUpload('Wi-Fi save failed');submit(h,'wifi');
  await waitFor(()=>h.element('message').textContent==='Wi-Fi save failed');
  assert.equal(h.element('wifi-password').value,'retained');assert.equal(h.requests.length,6);
});

test('board upload sends multiple www files and optional CSVs with exact server field names', async () => {
  const h=harness();await tick();h.element('asset-files').files=[file('style.css.gz','one'),file('theme.js.gz','two')];
  h.element('asset-playlist').files=[file('custom-stations.csv')];h.element('asset-wifi').files=[file('networks.csv','fixture\tpass\n')];
  submit(h,'assets');await waitFor(()=>h.uploads().length===1&&!h.element('assets-fields').disabled);
  const sent=h.uploads()[0];assert.equal(sent.url,'/webboard');
  const data=await sent.request.clone().formData();
  assert.deepEqual(data.getAll('www').map(item=>item.name),['style.css.gz','theme.js.gz']);
  assert.deepEqual(data.getAll('data').map(item=>item.name),['playlist.csv','wifi.csv']);
  assert.equal([...data].length,4);assert.match(h.element('message').textContent,/перезапустится/);
});

test('capabilities hide unsupported forms and reject synthetic unsupported submissions', async () => {
  const h=harness(false,{playlist_upload:false,asset_upload:false,wifi_upload:false});await tick();
  assert.equal(h.element('uploads').hidden,true);
  for(const name of ['playlist','assets','wifi']){
    assert.equal(h.element(name+'-form').hidden,true);assert.equal(h.element(name+'-fields').disabled,true);
    submit(h,name);
  }
  await tick();assert.equal(h.uploads().length,0);assert.match(h.element('message').textContent,/недоступна/);
  const partial=harness(false,{playlist_upload:false,wifi_upload:false});await tick();
  assert.equal(partial.element('assets-form').hidden,false);
  assert.equal(partial.element('asset-playlist').disabled,true);assert.equal(partial.element('asset-wifi').disabled,true);
  partial.element('asset-playlist').files=[file('playlist.csv')];submit(partial,'assets');
  await waitFor(()=>!partial.element('assets-fields').disabled);
  assert.equal(partial.uploads().length,0);assert.match(partial.element('message').textContent,/плейлиста недоступна/);
});

test('client checks actual encoded multipart size before sending and displays advertised limits', async () => {
  const h=harness(false,{upload_max_bytes:512,upload_max_files:2,upload_name_max_bytes:12,wifi_file_max_bytes:100});await tick();
  assert.match(h.element('upload-limits').textContent,/512 байт/);assert.match(h.element('upload-limits').textContent,/до 2 файлов/);
  assert.match(h.element('upload-limits').textContent,/до 12 байт/);assert.match(h.element('upload-limits').textContent,/до 100 байт/);
  h.element('playlist-file').files=[file('stations.csv',new Uint8Array(512))];submit(h,'playlist');
  await waitFor(()=>!h.element('playlist-fields').disabled);
  assert.equal(h.uploads().length,0);assert.match(h.element('message').textContent,/оформлением формы превышает 512/);
  h.element('asset-wifi').files=[file('wifi.csv',new Uint8Array(101))];submit(h,'assets');
  await waitFor(()=>!h.element('assets-fields').disabled);assert.equal(h.uploads().length,0);
  assert.match(h.element('message').textContent,/размер/);
});

test('client enforces file count, backup-safe gz names and UTF-8 Wi-Fi field limits', async () => {
  const h=harness();await tick();h.element('asset-files').files=Array.from({length:17},(_,i)=>file('f'+i+'.gz','x'));
  submit(h,'assets');await waitFor(()=>!h.element('assets-fields').disabled);
  assert.match(h.element('message').textContent,/слишком много/);assert.equal(h.uploads().length,0);
  for(const name of ['abcdefghijklmnopqrst.gz','theme.css','theme..css.gz','theme.gz.gz','theme.bak.gz','theme.tmp.gz']){
    h.element('asset-files').files=[file(name,'x')];submit(h,'assets');
    await waitFor(()=>!h.element('assets-fields').disabled);assert.match(h.element('message').textContent,/имя файла/);
  }
  h.element('asset-files').files=[file('same.gz','x'),file('same.gz','y')];submit(h,'assets');
  await waitFor(()=>!h.element('assets-fields').disabled);assert.match(h.element('message').textContent,/различаться/);
  h.element('asset-files').files=[file('empty.gz','')];submit(h,'assets');
  await waitFor(()=>!h.element('assets-fields').disabled);assert.match(h.element('message').textContent,/непустой файл/);
  for(const [ssid,password] of [['я'.repeat(16),'pass'],['ssid','p'.repeat(64)],['bad\tssid','pass']]){
    h.element('wifi-ssid').value=ssid;h.element('wifi-password').value=password;submit(h,'wifi');
    await waitFor(()=>!h.element('wifi-fields').disabled);assert.match(h.element('message').textContent,/Проверьте имя/);
  }
  assert.equal(h.uploads().length,0);
  h.element('asset-files').files=[file('abcdefghijklmnopqrs.gz','x')];submit(h,'assets');
  await waitFor(()=>h.uploads().length===1&&!h.element('assets-fields').disabled);
  assert.equal(h.element('message').textContent,'Файлы сохранены');
});

test('a saved playlist with failed status refresh reports saved data without retrying upload', async () => {
  const h=harness();await tick();h.element('playlist-file').files=[file('playlist.csv')];h.failStatus();submit(h,'playlist');
  await waitFor(()=>h.uploads().length===1&&!h.element('playlist-fields').disabled);
  assert.match(h.element('message').textContent,/Файлы сохранены.*Не удалось обновить состояние/);
  assert.equal(h.uploads().length,1);
});
