const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const page = fs.readFileSync(process.env.CYD_NATIVE_PAGE_SOURCE || path.join(__dirname, '../idf/esp32-cyd2usb-native/main/web_pages.cpp'), 'utf8');
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
    element('wifi-refresh'),element('time-submit'),element('network-settings-submit'),...['playlist','assets','wifi','firmware'].map(name=>element(name+'-submit'))];
  const timers = new Map(), intervals = [], sockets = [], requests = [], firmwareRequests = [];
  let nextTimer = 0, now = 1000, failSettings = false, failStatus = false, failUpload = '', holdUpload = false;
  const pendingUploads = [];
  const capabilities = {audio_output:'PDM',websocket:true,smartstart:true,wifi_reconnect:true,
    nativeWiFiApi:'/api/native/wifi',nativeWiFiMaxProfiles:5,nativeWiFiPrivateExport:false,
    ota:false,ota_max_bytes:1769472,ota_body_max_bytes:1773568,
    playlist_upload:true,asset_upload:true,wifi_upload:true,upload_max_bytes:98304,upload_max_files:16,
    upload_name_max_bytes:22,wifi_file_max_bytes:799,wifi_body_max_bytes:4096,
    wifi_ssid_max_bytes:31,wifi_password_max_bytes:63,...overrides};
  const settings = {volume:123,balance:-4,normalization:false,normgain:12,normtarget:-6,normtime:6000};
  const state = {station:'Радио', title:'Название', format:'MP3 44.1kHz',bitrate:128,audio:true};
  const radio = {current:7,count:15,smartstart:false};
  const wifi = {revision:'0123456789abcdef-0000000000000001',profiles:[
    {id:'r1',ssid:'first fixture',ssid_utf8:true},{id:'r2',ssid:'untouched network',ssid_utf8:true}]};
  const time = {available:true,network_ready:false,clock_valid:false,synchronized_this_boot:false,
    utc_offset_minutes:-30,sync_interval_minutes:60,server1:'pool.ntp.org',server2:'time.nist.gov',
    desired_revision:1,applied_revision:0,last_apply_error:0,utc_epoch:null,local_time:null};
  let failWifi = '', failTime = '', failTimeGet = '', unavailableWifi = false;
  const network = {online:false,ap_enabled:true,rssi_valid:false,rssi:-70,reconciling:false};
  let failNetwork=false,holdNetworkReads=false;const pendingNetworkReads=[];
  const wifiReply = {saved:true,rebooting:true};
  let holdTimeReads = false;
  const pendingTimeReads = [];
  const networkSettings = {hostname:'yoradio',ap_timeout_minutes:0,desired_revision:1,runtime_available:true,
    configured_hostname:'yoradio',hostname_pending:false,hostname_revision:1,last_hostname_error:0,
    ap_timeout_armed:false,ap_timeout_remaining_ms:0};
  const networkSettingsReply = {saved:true,application_pending:true,rebooting:false};
  let failNetworkSettings = '', failNetworkSettingsGet = '', holdNetworkSettingsReads = false, holdNetworkSettingsWrites = false;
  const pendingNetworkSettingsReads = [], pendingNetworkSettingsWrites = [];
  class Socket {
    static OPEN = 1;
    constructor(url) { this.url=url;this.readyState=0;sockets.push(this); }
    close() { this.readyState=3;this.onclose?.(); }
    open() { this.readyState=1;this.onopen?.(); }
    message(value) { this.onmessage?.({data:JSON.stringify(value)}); }
  }
  class FirmwareRequest {
    constructor() { this.upload={};this.headers={};firmwareRequests.push(this); }
    open(method,url,async) { Object.assign(this,{method,url,async}); }
    setRequestHeader(name,value) { this.headers[name]=value; }
    send(body) { this.body=body; }
    progress(loaded,total,lengthComputable=true) { this.upload.onprogress?.({loaded,total,lengthComputable}); }
    uploaded() { this.upload.onload?.(); }
    finish(status=200,responseText='OK') { Object.assign(this,{status,responseText});this.onload?.(); }
    fail(kind='error') { this['on'+kind]?.(); }
  }
  const context = vm.createContext({console,URL,URLSearchParams,FormData,Request,TextEncoder,WebSocket:Socket,XMLHttpRequest:FirmwareRequest,
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
      if (name === 'network-settings') {
        const post = options.method === 'POST';
        const error = post ? failNetworkSettings : failNetworkSettingsGet;
        if(post)failNetworkSettings='';else failNetworkSettingsGet='';
        if(post && !error && networkSettingsReply.saved === true)Object.assign(networkSettings,{
          hostname:uri.searchParams.get('hostname'),ap_timeout_minutes:Number(uri.searchParams.get('ap_timeout_minutes')),
          desired_revision:networkSettings.desired_revision+1,hostname_pending:true});
        const data = structuredClone(post ? networkSettingsReply : networkSettings);
        const reply = {ok:!error,text:async()=>error,json:async()=>data};
        if(post && holdNetworkSettingsWrites)return new Promise(resolve=>pendingNetworkSettingsWrites.push(()=>resolve(reply)));
        if(!post && holdNetworkSettingsReads)return new Promise(resolve=>pendingNetworkSettingsReads.push(()=>resolve(reply)));
        return reply;
      }
      if (name === 'network') {
        const snapshot=structuredClone(network);
        const reply={ok:!failNetwork,text:async()=>'Network unavailable',json:async()=>snapshot};
        if(holdNetworkReads)return new Promise(resolve=>pendingNetworkReads.push(()=>resolve(reply)));
        return reply;
      }
      if (name === 'wifi') {
        if (options.method==='POST') {
          const error=failWifi;failWifi='';
          const reply={ok:!error,text:async()=>error,json:async()=>structuredClone(wifiReply)};
          if(holdUpload)return new Promise(resolve=>pendingUploads.push(()=>resolve(reply)));
          return reply;
        }
        if(unavailableWifi)return {ok:false,text:async()=>'Wi-Fi metadata unavailable'};
        return {ok:true,json:async()=>structuredClone(wifi)};
      }
      if (name === 'time') {
        const error=options.method==='GET'&&failTimeGet?failTimeGet:failTime;
        if(options.method==='GET')failTimeGet='';failTime='';
        if(options.method==='POST'&&!error)Object.assign(time,{
          utc_offset_minutes:Number(uri.searchParams.get('utc_offset_minutes')),
          sync_interval_minutes:Number(uri.searchParams.get('sync_interval_minutes')),
          server1:uri.searchParams.get('server1'),server2:uri.searchParams.get('server2'),
          desired_revision:time.desired_revision+1});
        const data=options.method==='POST'?{saved:true,application_pending:true}:structuredClone(time);
        const reply={ok:!error,text:async()=>error,json:async()=>data};
        if(options.method==='GET'&&holdTimeReads)return new Promise(resolve=>pendingTimeReads.push(()=>resolve(reply)));
        return reply;
      }
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
  return {element,context,buttons,radioButtons,sockets,requests,firmwareRequests,timers,intervals,settings,radio,state,capabilities,wifi,time,wifiReply,network,pendingNetworkReads,
    networkSettings,networkSettingsReply,pendingNetworkSettingsReads,pendingNetworkSettingsWrites,
    holdNetworkSettingsReads() {holdNetworkSettingsReads=true;},holdNetworkSettingsWrites() {holdNetworkSettingsWrites=true;},
    releaseNetworkSettingsRead(index=0) {const release=pendingNetworkSettingsReads.splice(index,1)[0];assert(release);release();},
    releaseNetworkSettingsWrite() {const release=pendingNetworkSettingsWrites.shift();assert(release);release();},
    failNetworkSettings(text) {failNetworkSettings=text;},failNetworkSettingsGet(text) {failNetworkSettingsGet=text;},
    networkSettingsWrites:()=>requests.filter(r=>r.method==='POST'&&r.url.startsWith('/api/native/network-settings?')),
    failNetwork() {failNetwork=true;},holdNetworkReads() {holdNetworkReads=true;},
    releaseNetworkRead() {const release=pendingNetworkReads.shift();assert(release);release();},
    setNow(value) { now=value; },failSettings() { failSettings=true; },failStatus() { failStatus=true; },
    failUpload(text) { failUpload=text; },holdUploads() { holdUpload=true; },
    failWifi(text) { failWifi=text; },failTime(text) { failTime=text; },failTimeGet(text) { failTimeGet=text; },unavailableWifi() { unavailableWifi=true; },
    holdTimeReads() { holdTimeReads=true; },pendingTimeReads,
    releaseTimeRead(index=0) { const release=pendingTimeReads.splice(index,1)[0];assert(release);release(); },
    releaseUploads() { holdUpload=false;for(const resolve of pendingUploads.splice(0))resolve(); },
    uploads:()=>requests.filter(item=>item.request),wifiWrites:()=>requests.filter(item=>item.url==='/api/native/wifi'&&item.method==='POST'),pendingUploads};
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
    '/api/native/capabilities','/api/native/status','/api/native/radio','/api/native/settings','/api/native/wifi']);
  assert(h.buttons.filter(button=>!['firmware-submit','time-submit','network-settings-submit'].includes(button.id)).every(button=>!button.disabled));
  assert.equal(h.element('firmware-submit').disabled,true);
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
  assert.deepEqual(h.requests.slice(6).map(item=>item.url),['/api/native/radio','/api/native/status']);
  assert.equal(h.element('message').textContent,'Файлы сохранены');
});

test('upload failure shows response text and keeps the old count and selected file', async () => {
  const h=harness();await tick();const selected=file('stations.csv');h.element('playlist-file').files=[selected];
  h.radio.count=99;h.failUpload('Storage full <b>retry</b>');submit(h,'playlist');
  await waitFor(()=>h.element('message').textContent==='Storage full <b>retry</b>');
  assert.equal(h.element('message').innerHTML,undefined);assert.equal(h.element('station-count').textContent,'из 15');
  assert.equal(h.requests.length,6);assert.equal(h.element('playlist-file').files[0],selected);
  assert.equal(h.element('playlist-fields').disabled,false);
});

test('one local upload locks all forms and prevents a second POST until completion', async () => {
  const h=harness();await tick();h.holdUploads();h.element('asset-files').files=[file('theme.css.gz','compressed')];
  h.element('wifi-ssid').value='fixture';h.element('wifi-password').value='pass';submit(h,'assets');
  await waitFor(()=>h.uploads().length===1);submit(h,'wifi');await tick();
  assert.match(h.element('message').textContent,/Дождитесь/);assert.equal(h.uploads().length,1);
  assert(['playlist','assets','wifi'].every(name=>h.element(name+'-submit').disabled));
  h.releaseUploads();await waitFor(()=>!h.element('assets-fields').disabled);
  submit(h,'wifi');await waitFor(()=>h.wifiWrites().length===1&&/перезапускается/.test(h.element('message').textContent));
  assert.equal(h.uploads().length,1);assert.match(h.element('message').textContent,/перезапускается/);
});

test('Wi-Fi form sends typed metadata edit, preserves other rows and announces reserved restart', async () => {
  const h=harness();await tick();h.element('wifi-ssid').value=' сеть ';h.element('wifi-password').value=' pass ';
  submit(h,'wifi');await waitFor(()=>h.wifiWrites().length===1&&h.element('wifi-password').value==='');
  const sent=h.wifiWrites()[0];assert.equal(sent.url,'/api/native/wifi');assert.equal(sent.method,'POST');
  assert.equal(sent.headers['Content-Type'],'application/json');
  const data=JSON.parse(sent.body);assert.equal(data.revision,h.wifi.revision);
  assert.deepEqual(data.profiles,[{id:'r1',ssid:' сеть ',password_action:'set',password:' pass '},{id:'r2',password_action:'keep'}]);
  assert.match(h.element('message').textContent,/Wi-Fi сохранён.*перезапускается/);
  assert.equal(h.element('wifi-password').value,'');assert.equal(h.requests.length,6);
  assert.equal(h.element('station-count').textContent,'из 15');
});

test('Wi-Fi blank password keeps existing secret and persistence failure keeps the new input', async () => {
  const h=harness();await tick();h.element('wifi-ssid').value='renamed fixture';h.element('wifi-password').value='';
  h.failWifi('Wi-Fi save failed');submit(h,'wifi');
  await waitFor(()=>h.element('message').textContent==='Wi-Fi save failed');
  assert.deepEqual(JSON.parse(h.wifiWrites()[0].body).profiles[0],{id:'r1',ssid:'renamed fixture',password_action:'keep'});
  h.element('wifi-password').value='retained';h.failWifi('Wi-Fi save failed again');submit(h,'wifi');
  await waitFor(()=>h.element('message').textContent==='Wi-Fi save failed again');
  assert.equal(h.element('wifi-password').value,'retained');assert.equal(h.wifiWrites().length,2);
});

test('board upload sends multiple www files and optional playlist only', async () => {
  const h=harness();await tick();h.element('asset-files').files=[file('style.css.gz','one'),file('theme.js.gz','two')];
  h.element('asset-playlist').files=[file('custom-stations.csv')];
  submit(h,'assets');await waitFor(()=>h.uploads().length===1&&!h.element('assets-fields').disabled);
  const sent=h.uploads()[0];assert.equal(sent.url,'/webboard');
  const data=await sent.request.clone().formData();
  assert.deepEqual(data.getAll('www').map(item=>item.name),['style.css.gz','theme.js.gz']);
  assert.deepEqual(data.getAll('data').map(item=>item.name),['playlist.csv']);
  assert.equal([...data].length,3);assert.equal(h.element('message').textContent,'Файлы сохранены');
});

test('capabilities hide unsupported forms and reject synthetic unsupported submissions', async () => {
  const h=harness(false,{playlist_upload:false,asset_upload:false,wifi_upload:false,nativeWiFiApi:undefined});await tick();
  assert.equal(h.element('uploads').hidden,true);
  for(const name of ['playlist','assets','wifi']){
    assert.equal(h.element(name+'-form').hidden,true);assert.equal(h.element(name+'-fields').disabled,true);
    submit(h,name);
  }
  await tick();assert.equal(h.uploads().length,0);assert.match(h.element('message').textContent,/недоступна/);
  const partial=harness(false,{playlist_upload:false,wifi_upload:false,nativeWiFiApi:undefined});await tick();
  assert.equal(partial.element('assets-form').hidden,false);
  assert.equal(partial.element('asset-playlist').disabled,true);
  partial.element('asset-playlist').files=[file('playlist.csv')];submit(partial,'assets');
  await waitFor(()=>!partial.element('assets-fields').disabled);
  assert.equal(partial.uploads().length,0);assert.match(partial.element('message').textContent,/плейлиста недоступна/);
});

test('client checks actual encoded multipart size before sending and displays advertised limits', async () => {
  const h=harness(false,{upload_max_bytes:512,upload_max_files:2,upload_name_max_bytes:12,wifi_file_max_bytes:100});await tick();
  assert.match(h.element('upload-limits').textContent,/512 байт/);assert.match(h.element('upload-limits').textContent,/до 2 файлов/);
  assert.match(h.element('upload-limits').textContent,/до 12 байт/);
  h.element('playlist-file').files=[file('stations.csv',new Uint8Array(512))];submit(h,'playlist');
  await waitFor(()=>!h.element('playlist-fields').disabled);
  assert.equal(h.uploads().length,0);assert.match(h.element('message').textContent,/оформлением формы превышает 512/);
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

test('firmware capability gates the form and rejects unsupported or premature submission', async () => {
  const h=harness();await tick();
  assert.equal(h.element('firmware').hidden,true);assert.equal(h.element('firmware-fields').disabled,true);
  h.element('firmware-file').files=[file('app.bin','image')];submit(h,'firmware');await tick();
  assert.match(h.element('message').textContent,/недоступно/);assert.equal(h.firmwareRequests.length,0);
  const failed=harness(true,{ota:true});submit(failed,'firmware');await tick();
  assert.equal(failed.firmwareRequests.length,0);assert.equal(failed.element('firmware-submit').disabled,true);
});

test('firmware checks selected file and the advertised app limit before network or audio pause', async () => {
  const h=harness(false,{ota:true,ota_max_bytes:512});await tick();
  assert.equal(h.element('firmware').hidden,false);assert.equal(h.element('firmware-fields').disabled,false);
  assert.match(h.element('firmware-limits').textContent,/PDM.*512 байт/);
  for(const selected of [undefined,file('app.bin',''),file('app.bin',new Uint8Array(513)),file('flash.txt','x')]){
    h.element('firmware-file').files=selected?[selected]:[];submit(h,'firmware');await tick();
    assert.equal(h.firmwareRequests.length,0);assert.equal(h.sockets.length,1);
    assert.equal(h.element('firmware-fields').disabled,false);assert(h.element('message').textContent);
  }
});

test('firmware uses ordered canonical multipart fields, browser boundary and honest transfer progress', async () => {
  const h=harness(false,{ota:true,ota_max_bytes:512});await tick();h.sockets[0].open();
  const selected=file('my CYD build.BIN',new Uint8Array(512));h.element('firmware-file').files=[selected];
  submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===1);
  const request=h.firmwareRequests[0];
  assert.equal(request.method,'POST');assert.equal(request.url,'/update');assert.equal(request.async,true);
  assert.equal(request.timeout,190000);assert.deepEqual(request.headers,{});
  assert.deepEqual([...request.body.keys()],['updatetarget','update']);
  assert.equal(request.body.get('updatetarget'),'fw');
  assert.equal(request.body.get('update').name,'app.bin');assert.equal(request.body.get('update').size,512);
  const encoded=new Request('http://radio.local/update',{method:'POST',body:request.body});
  assert.match(encoded.headers.get('content-type'),/^multipart\/form-data; boundary=/);
  assert.equal((await encoded.formData()).get('update').size,512);
  assert(h.buttons.every(button=>button.disabled));assert.equal(h.element('smartstart').disabled,true);
  assert.equal(h.sockets[0].readyState,3);assert.equal(h.timers.size,0);
  request.progress(42,100);assert.equal(h.element('firmware-progress').value,42);
  assert.match(h.element('firmware-status').textContent,/Передача.*42%/);
  request.progress(1000,100,false);assert.equal(h.element('firmware-progress').value,42);
  request.uploaded();assert.match(h.element('firmware-status').textContent,/Файл передан.*Проверка/);
  request.finish();await tick();assert.match(h.element('firmware-status').textContent,/Образ проверен.*перезапускается/);
});

test('successful firmware upload waits for reboot without background requests or claiming verified boot', async () => {
  const h=harness(false,{ota:true});await tick();h.element('firmware-file').files=[file('app.bin','image')];
  submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===1);h.firmwareRequests[0].finish();await tick();
  assert(h.buttons.every(button=>button.disabled));assert.equal(h.element('firmware-refresh').hidden,false);
  assert.match(h.element('message').textContent,/Успешный запуск.*ещё нужно проверить/);
  const before=h.requests.length;h.intervals[0]();h.sockets[0].close();
  for(const timer of h.timers.values())timer.fn();
  h.radioButtons[0].listeners.click();submit(h,'firmware');submit(h,'playlist');await tick();
  assert.equal(h.requests.length,before);assert.equal(h.sockets.length,1);assert.equal(h.firmwareRequests.length,1);
});

test('server rejection keeps firmware selection and restores capability-specific controls', async () => {
  const h=harness(false,{ota:true,smartstart:false,wifi_reconnect:false});await tick();
  const selected=file('app.bin','image');h.element('firmware-file').files=[selected];
  submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===1);
  h.firmwareRequests[0].finish(503,'Audio busy <b>try again</b>');await tick();
  assert.equal(h.element('message').textContent,'Audio busy <b>try again</b>');
  assert.equal(h.element('message').innerHTML,undefined);assert.equal(h.element('firmware-file').files[0],selected);
  assert.equal(h.element('firmware-fields').disabled,false);assert.equal(h.element('playlist-fields').disabled,false);
  assert.equal(h.element('smartstart').disabled,true);assert.equal(h.element('reconnect').disabled,true);
  assert.equal(h.element('firmware-progress').hidden,true);assert.equal(h.firmwareRequests.length,1);
  assert.equal(h.sockets.length,2);
});

test('network, timeout and abort outcomes never automatically retry firmware', async () => {
  for(const kind of ['error','timeout','abort']){
    const h=harness(false,{ota:true});await tick();h.element('firmware-file').files=[file('app.bin','image')];
    submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===1);h.firmwareRequests[0].fail(kind);await tick();
    assert.match(h.element('message').textContent,/перед повторной попыткой/);
    assert.equal(h.element('firmware-refresh').hidden,false);assert.equal(h.firmwareRequests.length,1);
    assert.equal(h.element('firmware-fields').disabled,false);
    for(const timer of h.timers.values())timer.fn();await tick();assert.equal(h.firmwareRequests.length,1);
  }
});

test('firmware and file forms serialize uploads and block control actions during installation', async () => {
  const h=harness(false,{ota:true});await tick();h.holdUploads();
  h.element('playlist-file').files=[file('stations.csv')];submit(h,'playlist');await waitFor(()=>h.uploads().length===1);
  h.element('firmware-file').files=[file('app.bin','image')];submit(h,'firmware');await tick();
  assert.equal(h.firmwareRequests.length,0);assert.match(h.element('message').textContent,/Дождитесь/);
  h.releaseUploads();await waitFor(()=>!h.element('playlist-fields').disabled);
  submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===1);
  const before=h.requests.length;h.radioButtons[1].listeners.click();submit(h,'playlist');h.intervals[0]();await tick();
  assert.equal(h.requests.length,before);assert.equal(h.firmwareRequests.length,1);
  h.firmwareRequests[0].finish(400,'Choose CYD application');await tick();
  submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===2);
  h.firmwareRequests[1].finish();await tick();
});

test('Wi-Fi first-row editor preserves all five IDs and omits untouched SSIDs and passwords', async () => {
  const h=harness();
  h.wifi.profiles=Array.from({length:5},(_,i)=>({id:'r'+(i+1),ssid:'fixture '+i,ssid_utf8:true}));
  await tick();submit(h,'wifi');await waitFor(()=>h.wifiWrites().length===1);
  const body=JSON.parse(h.wifiWrites()[0].body);
  assert.deepEqual(body.profiles,Array.from({length:5},(_,i)=>({id:'r'+(i+1),password_action:'keep'})));
  assert.equal(body.revision,h.wifi.revision);assert.equal(h.uploads().length,0);
  assert(h.requests.every(r=>!r.url.includes('/data/')&&!r.url.includes('.csv')));
});

test('unchanged non-UTF8 legacy SSID presentation is omitted even when replacement text exceeds the byte cap', async () => {
  const h=harness();h.wifi.profiles[0]={id:'r1',ssid:'\ufffd'.repeat(31),ssid_utf8:false};
  await tick();assert.equal(h.element('wifi-ssid').value,h.wifi.profiles[0].ssid);
  h.element('wifi-password').value='new secret';submit(h,'wifi');await waitFor(()=>h.wifiWrites().length===1);
  assert.deepEqual(JSON.parse(h.wifiWrites()[0].body).profiles[0],{id:'r1',password_action:'set',password:'new secret'});
});

test('open network requires an explicit action and sends set with an empty password', async () => {
  const h=harness();h.wifi.profiles=[];await tick();h.element('wifi-ssid').value='open fixture';
  submit(h,'wifi');await tick();assert.equal(h.wifiWrites().length,0);
  assert.match(h.element('message').textContent,/пароль.*открытую/);
  h.element('wifi-password').value='discarded new input';h.element('wifi-open').checked=true;
  h.element('wifi-open').listeners.change();assert.equal(h.element('wifi-password').value,'');
  submit(h,'wifi');await waitFor(()=>h.wifiWrites().length===1);
  assert.deepEqual(JSON.parse(h.wifiWrites()[0].body).profiles,[{ssid:'open fixture',password_action:'set',password:''}]);
});

test('stale Wi-Fi error preserves edits without fallback; explicit refresh loads the new revision', async () => {
  const h=harness();await tick();h.element('wifi-ssid').value='edited network';h.element('wifi-password').value='new input';
  h.failWifi('{"error":"Wi-Fi settings changed; reload"}');submit(h,'wifi');
  await waitFor(()=>h.element('message').textContent.includes('settings changed'));
  assert.equal(h.element('wifi-ssid').value,'edited network');assert.equal(h.element('wifi-password').value,'new input');
  assert.equal(h.wifiWrites().length,1);assert.equal(h.uploads().length,0);
  h.wifi.revision='0123456789abcdef-0000000000000002';h.wifi.profiles[0].ssid='other tab';
  h.element('wifi-refresh').listeners.click();await tick();
  assert.equal(h.element('wifi-ssid').value,'other tab');assert.equal(h.element('wifi-password').value,'');
  submit(h,'wifi');await waitFor(()=>h.wifiWrites().length===2);
  assert.equal(JSON.parse(h.wifiWrites()[1].body).revision,h.wifi.revision);
});

test('Wi-Fi metadata failure and malformed metadata disable editing without disabling playback or using raw files', async () => {
  for(const broken of ['unavailable','duplicate','too many']){
    const h=harness();
    if(broken==='unavailable')h.unavailableWifi();
    else if(broken==='duplicate')h.wifi.profiles[1].id='r1';
    else h.wifi.profiles=Array.from({length:6},(_,i)=>({id:'r'+(i+1),ssid:'x',ssid_utf8:true}));
    await tick();assert.equal(h.element('wifi-fields').disabled,true);assert.equal(h.element('wifi-refresh').disabled,false);
    assert.equal(h.radioButtons[0].disabled,false);submit(h,'wifi');await tick();assert.equal(h.wifiWrites().length,0);
    assert(h.requests.every(r=>!r.url.includes('/data/')&&!r.url.includes('.csv')));
  }
});

test('legacy upload capability does not enable native Wi-Fi editing and unconfirmed success never claims restart', async () => {
  const unsupported=harness(false,{nativeWiFiApi:undefined,wifi_upload:true});await tick();
  assert.equal(unsupported.element('wifi-form').hidden,true);submit(unsupported,'wifi');await tick();
  assert.equal(unsupported.wifiWrites().length,0);assert.equal(unsupported.uploads().length,0);
  const h=harness();await tick();h.wifiReply.rebooting=false;h.element('wifi-password').value='retained';
  submit(h,'wifi');await waitFor(()=>h.element('message').textContent.includes('Проверьте результат'));
  assert.equal(h.element('wifi-password').value,'retained');assert.equal(h.element('wifi-fields').disabled,false);
});

test('native time boot shows invalid clock and separate desired, applied and synchronized state', async () => {
  const h=harness(false,{nativeTimeApi:'/api/native/time'});await tick();
  assert.deepEqual(h.requests.map(r=>r.url),['/api/native/capabilities','/api/native/status','/api/native/radio',
    '/api/native/settings','/api/native/wifi','/api/native/time']);
  assert.equal(h.element('time-offset').value,-30);assert.equal(h.element('time-interval').value,60);
  assert.equal(h.element('time-section').hidden,false);assert.equal(h.element('time-fields').disabled,false);
  assert.equal(h.element('time-clock').textContent,'Часы ещё не установлены');
  assert.match(h.element('time-status').textContent,/Нет соединения.*Применение.*ожидается.*ещё не подтверждена/);
});

test('time saves exact four query fields without a body and announces persistence without claiming synchronization', async () => {
  const h=harness(false,{nativeTimeApi:'/api/native/time'});await tick();
  h.element('time-offset').value='345';h.element('time-interval').value='15';
  h.element('time-server1').value='ntp.example';h.element('time-server2').value='';
  submit(h,'time');await waitFor(()=>h.requests.some(r=>r.method==='POST'&&r.url.startsWith('/api/native/time?'))&&!h.element('time-fields').disabled);
  const sent=h.requests.find(r=>r.method==='POST'&&r.url.startsWith('/api/native/time?'));
  const q=new URL(sent.url,'http://radio').searchParams;
  assert.deepEqual([...q],[['utc_offset_minutes','345'],['sync_interval_minutes','15'],['server1','ntp.example'],['server2','']]);
  assert.equal(sent.body,undefined);assert.match(h.element('message').textContent,/сохранены.*Применение и синхронизация.*отдельно/);
  assert.equal(h.element('time-offset').value,345);assert.equal(h.element('time-server2').value,'');
  assert.match(h.element('time-status').textContent,/ещё не подтверждена/);
});

test('time persistence error retains edits and successful save with failed refresh remains visibly saved', async () => {
  const h=harness(false,{nativeTimeApi:'/api/native/time'});await tick();h.element('time-offset').value='-45';
  h.element('time-form').listeners.input();h.failTime('NVS commit failed');submit(h,'time');
  await waitFor(()=>h.element('message').textContent==='NVS commit failed');
  assert.equal(h.element('time-offset').value,'-45');assert.equal(h.element('time-fields').disabled,false);
  h.failTimeGet('Snapshot busy');submit(h,'time');
  await waitFor(()=>h.element('time-status').textContent==='Настройки сохранены; состояние пока недоступно');
  assert.match(h.element('message').textContent,/Настройки времени сохранены/);
});

test('time polling preserves unsaved values while updating clock, errors and synchronization status', async () => {
  const h=harness(false,{nativeTimeApi:'/api/native/time'});await tick();
  h.element('time-offset').value='-45';h.element('time-form').listeners.input();
  Object.assign(h.time,{clock_valid:true,local_time:'2026-10-18T12:34:56',network_ready:true,
    desired_revision:2,applied_revision:1,last_apply_error:263,synchronized_this_boot:true});
  h.intervals[0]();await tick();assert.equal(h.element('time-offset').value,'-45');
  assert.equal(h.element('time-clock').textContent,'2026-10-18T12:34:56');
  assert.match(h.element('time-status').textContent,/ожидается.*синхронизировано.*Ошибка применения: 263/);
});

test('native time service failure does not disable audio; later polling recovers the form', async () => {
  const h=harness(false,{nativeTimeApi:'/api/native/time'});h.failTime('Time unavailable');await tick();
  assert.equal(h.radioButtons[0].disabled,false);assert.equal(h.element('time-fields').disabled,true);
  assert.match(h.element('time-status').textContent,/недоступен/);
  h.intervals[0]();await tick();assert.equal(h.element('time-fields').disabled,false);
  const hidden=harness(false,{nativeTimeApi:true});await tick();assert.equal(hidden.element('time-section').hidden,true);
  assert(!hidden.requests.some(r=>r.url==='/api/native/time'));
});

test('OTA blocks new Wi-Fi and time saves and polling until installation completes', async () => {
  const h=harness(false,{ota:true,nativeTimeApi:'/api/native/time'});await tick();
  h.element('firmware-file').files=[file('app.bin','image')];submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===1);
  const before=h.requests.length;submit(h,'time');submit(h,'wifi');h.intervals[0]();await tick();
  assert.equal(h.requests.length,before);assert.equal(h.wifiWrites().length,0);
  assert.equal(h.element('time-fields').disabled,true);assert.equal(h.element('wifi-fields').disabled,true);
  h.firmwareRequests[0].finish();await tick();h.intervals[0]();submit(h,'time');submit(h,'wifi');await tick();
  assert.equal(h.requests.length,before);
});

test('periodic polling is sequential and an old time GET cannot overwrite a completed edit', async () => {
  const h=harness(false,{nativeTimeApi:'/api/native/time'});await tick();h.sockets[0].open();h.holdTimeReads();
  h.intervals[0]();await waitFor(()=>h.pendingTimeReads.length===1);
  const before=h.requests.length;h.intervals[0]();h.intervals[0]();await tick();
  assert.equal(h.requests.length,before);
  h.element('time-offset').value='345';h.element('time-form').listeners.input();
  submit(h,'time');
  await waitFor(()=>h.pendingTimeReads.length===2);
  h.releaseTimeRead(1);await waitFor(()=>!h.element('time-fields').disabled);
  assert.equal(h.element('time-offset').value,345);
  h.releaseTimeRead(0);await tick();assert.equal(h.element('time-offset').value,345);
  assert.match(h.element('time-status').textContent,/ожидается/);
});


test('native network view shows AP independently and hides invalid RSSI', async () => {
  const h=harness(false,{nativeNetworkApi:'/api/native/network'});await tick();
  assert.match(h.element('network-state').textContent,/Wi-Fi не подключён/);
  assert.match(h.element('network-state').textContent,/Точка доступа включена/);
  assert.doesNotMatch(h.element('network-state').textContent,/дБм/);
  Object.assign(h.network,{online:true,rssi_valid:true,rssi:-53});
  await h.intervals[0]();
  assert.match(h.element('network-state').textContent,/-53 дБм/);
  h.network.rssi_valid=false;h.network.rssi=-90;await h.intervals[0]();
  assert.doesNotMatch(h.element('network-state').textContent,/дБм/);
  assert.equal(h.radioButtons[1].disabled,false);
});

test('native network API errors hide signal without disabling audio', async () => {
  const h=harness(false,{nativeNetworkApi:'/api/native/network'});await tick();
  h.failNetwork();await h.intervals[0]();
  assert.match(h.element('network-state').textContent,/недоступно/);
  assert.doesNotMatch(h.element('network-state').textContent,/дБм/);
  assert.equal(h.radioButtons[1].disabled,false);
});

test('a delayed network GET cannot overwrite a newer WebSocket link notice', async () => {
  const h=harness(false,{nativeNetworkApi:'/api/native/network'});await tick();
  Object.assign(h.network,{online:true,rssi_valid:true,rssi:-41});h.holdNetworkReads();
  const pending=h.intervals[0]();await waitFor(()=>h.pendingNetworkReads.length===1);
  h.sockets[0].open();h.sockets[0].message({status:{network_online:false,ap_enabled:true,rssi_valid:true,rssi:-20}});
  assert.match(h.element('network-state').textContent,/Wi-Fi не подключён/);
  h.releaseNetworkRead();await pending;
  assert.match(h.element('network-state').textContent,/Wi-Fi не подключён/);
  assert.doesNotMatch(h.element('network-state').textContent,/дБм/);
  h.sockets[0].message({status:{network_online:true,ap_enabled:false,rssi_valid:true,rssi:'-50'}});
  assert.doesNotMatch(h.element('network-state').textContent,/дБм/);
});

const networkSettingsCaps = {nativeNetworkSettingsApi:'/api/native/network-settings',
  network_hostname_max_bytes:23,network_ap_timeout_max_minutes:30};

test('network settings require the exact capability and default AP reboot remains disabled', async () => {
  for(const caps of [{}, {...networkSettingsCaps,nativeNetworkSettingsApi:true},
      {...networkSettingsCaps,network_hostname_max_bytes:24},{...networkSettingsCaps,network_ap_timeout_max_minutes:60}]) {
    const h=harness(false,caps);await tick();submit(h,'network-settings');await tick();
    assert.equal(h.element('network-settings-section').hidden,true);
    assert.equal(h.element('network-settings-fields').disabled,true);
    assert(!h.requests.some(r=>r.url.includes('/network-settings')));
  }
  const h=harness(false,networkSettingsCaps);await tick();
  assert.equal(h.element('network-settings-section').hidden,false);
  assert.equal(h.element('network-settings-fields').disabled,false);
  assert.equal(h.element('network-hostname').value,'yoradio');assert.equal(h.element('network-ap-timeout').value,0);
  assert.match(h.element('network-timeout-status').textContent,/перезапуск отключён/);
  assert.match(h.element('network-settings-status').textContent,/Имя настроено в сетевом интерфейсе/);
  assert(h.requests.at(-1).url==='/api/native/network-settings');assert.equal(h.intervals.length,1);
});

test('network settings save exactly two bodyless query fields without claiming application or restart', async () => {
  const h=harness(false,networkSettingsCaps);await tick();
  h.element('network-hostname').value='Radio-23';h.element('network-ap-timeout').value='30';
  h.element('network-settings-form').listeners.input();submit(h,'network-settings');
  await waitFor(()=>h.networkSettingsWrites().length===1&&!h.element('network-settings-fields').disabled);
  const sent=h.networkSettingsWrites()[0], query=new URL(sent.url,'http://radio').searchParams;
  assert.deepEqual([...query],[['hostname','Radio-23'],['ap_timeout_minutes','30']]);assert.equal(sent.body,undefined);
  assert.equal(h.element('network-hostname').value,'Radio-23');assert.equal(h.element('network-ap-timeout').value,30);
  assert.match(h.element('message').textContent,/сохранены.*Применение имени и таймер.*отдельно/);
  assert.match(h.element('network-settings-status').textContent,/Сохранено имя DHCP: Radio-23.*интерфейсе: yoradio.*ожидается/);
  assert.equal(h.element('firmware-refresh').hidden,true);assert.equal(h.radioButtons[0].disabled,false);
  h.radioButtons[1].listeners.click();await tick();assert(h.requests.some(r=>r.url.includes('action=toggle')));
});

test('network settings reject invalid ASCII hostname and noncanonical timeout before sending', async () => {
  const h=harness(false,networkSettingsCaps);await tick();
  for(const hostname of ['', '-abc','abc-','a.b','a_b','a b','радио','a'.repeat(24)]) {
    h.element('network-hostname').value=hostname;h.element('network-ap-timeout').value='0';submit(h,'network-settings');await tick();
    assert.equal(h.networkSettingsWrites().length,0);assert.match(h.element('message').textContent,/Проверьте имя DHCP/);
  }
  for(const timeout of ['', '-1','+1','01','1.0','1e1',' 1','31','256']) {
    h.element('network-hostname').value='a';h.element('network-ap-timeout').value=timeout;submit(h,'network-settings');await tick();
    assert.equal(h.networkSettingsWrites().length,0);
  }
  h.element('network-hostname').value='A'.repeat(23);h.element('network-ap-timeout').value='0';submit(h,'network-settings');
  await waitFor(()=>h.networkSettingsWrites().length===1&&!h.element('network-settings-fields').disabled);
  assert.equal(h.networkSettings.hostname.length,23);
});

test('network persistence errors preserve edits and success with failed refresh stays visibly saved', async () => {
  const h=harness(false,networkSettingsCaps);await tick();
  h.element('network-hostname').value='retained-name';h.element('network-ap-timeout').value='5';
  h.element('network-settings-form').listeners.input();h.failNetworkSettings('NVS commit failed');submit(h,'network-settings');
  await waitFor(()=>h.element('message').textContent==='NVS commit failed');
  assert.equal(h.element('network-hostname').value,'retained-name');assert.equal(h.element('network-ap-timeout').value,'5');
  assert.equal(h.element('network-settings-fields').disabled,false);assert.equal(h.networkSettings.hostname,'yoradio');
  h.failNetworkSettingsGet('Snapshot busy');submit(h,'network-settings');
  await waitFor(()=>h.element('network-settings-status').textContent==='Настройки сохранены; состояние пока недоступно');
  assert.match(h.element('message').textContent,/Настройки сети сохранены/);
  assert.equal(h.element('network-hostname').value,'retained-name');assert.equal(h.element('network-settings-fields').disabled,false);
  const unconfirmed=harness(false,networkSettingsCaps);await tick();unconfirmed.networkSettingsReply.saved=false;
  unconfirmed.element('network-hostname').value='unsaved';submit(unconfirmed,'network-settings');
  await waitFor(()=>unconfirmed.element('message').textContent.includes('не подтверждено'));
  assert.equal(unconfirmed.element('network-hostname').value,'unsaved');assert.equal(unconfirmed.networkSettings.hostname,'yoradio');
});

test('network polling preserves dirty fields and reports configured error and AP deadline separately', async () => {
  const h=harness(false,networkSettingsCaps);await tick();
  h.element('network-hostname').value='my-unsaved';h.element('network-ap-timeout').value='7';
  h.element('network-settings-form').listeners.input();
  Object.assign(h.networkSettings,{hostname:'other-tab',ap_timeout_minutes:30,desired_revision:2,
    configured_hostname:null,hostname_pending:true,last_hostname_error:257,ap_timeout_armed:true,ap_timeout_remaining_ms:12345});
  await h.intervals[0]();
  assert.equal(h.element('network-hostname').value,'my-unsaved');assert.equal(h.element('network-ap-timeout').value,'7');
  assert.match(h.element('network-settings-status').textContent,/Сохранено имя DHCP: other-tab.*неизвестно.*ожидается.*Ошибка применения имени: 257/);
  assert.match(h.element('network-timeout-status').textContent,/осталось около 13 с/);
  Object.assign(h.networkSettings,{runtime_available:false,configured_hostname:null,last_hostname_error:null,
    hostname_revision:null,ap_timeout_armed:null,ap_timeout_remaining_ms:null});await h.intervals[0]();
  assert.match(h.element('network-timeout-status').textContent,/пока недоступно/);
  assert.equal(h.element('network-settings-fields').disabled,false);
});

test('saved AP timeout with failed refresh never retains the previous disabled or armed label', async () => {
  for (const [before,after] of [[0,1],[30,0]]) {
    const h=harness(false,networkSettingsCaps);
    Object.assign(h.networkSettings,{ap_timeout_minutes:before,ap_timeout_armed:before!==0,ap_timeout_remaining_ms:12000});
    await tick();assert.match(h.element('network-timeout-status').textContent,before ? /осталось около 12 с/ : /перезапуск отключён/);
    h.element('network-ap-timeout').value=String(after);h.element('network-settings-form').listeners.input();
    h.failNetworkSettingsGet('Snapshot busy');submit(h,'network-settings');
    await waitFor(()=>h.element('network-settings-status').textContent==='Настройки сохранены; состояние пока недоступно');
    assert.equal(h.networkSettings.ap_timeout_minutes,after);
    assert.equal(h.element('network-timeout-status').textContent,'Состояние таймера пока недоступно');
    assert.match(h.element('message').textContent,/Настройки сети сохранены/);
    assert.equal(h.element('network-ap-timeout').value,String(after));
    assert.equal(h.element('network-settings-fields').disabled,false);
  }
});

test('network settings outage disables only its form and periodic polling recovers it', async () => {
  const h=harness(false,networkSettingsCaps);h.failNetworkSettingsGet('Unavailable');await tick();
  assert.equal(h.element('network-settings-fields').disabled,true);assert.equal(h.radioButtons[0].disabled,false);
  assert.match(h.element('network-settings-status').textContent,/недоступен/);
  submit(h,'network-settings');await tick();assert.equal(h.networkSettingsWrites().length,0);
  await h.intervals[0]();assert.equal(h.element('network-settings-fields').disabled,false);
  h.networkSettings.hostname='broken.name';await h.intervals[0]();assert.equal(h.element('network-settings-fields').disabled,true);
});

test('stale network settings GET cannot overwrite completed save or later dirty input', async () => {
  const h=harness(false,networkSettingsCaps);await tick();h.sockets[0].open();h.holdNetworkSettingsReads();
  const poll=h.intervals[0]();await waitFor(()=>h.pendingNetworkSettingsReads.length===1);
  h.element('network-hostname').value='new-saved';h.element('network-ap-timeout').value='10';
  h.element('network-settings-form').listeners.input();submit(h,'network-settings');
  await waitFor(()=>h.pendingNetworkSettingsReads.length===2);h.releaseNetworkSettingsRead(1);
  await waitFor(()=>!h.element('network-settings-fields').disabled);
  assert.equal(h.element('network-hostname').value,'new-saved');
  h.releaseNetworkSettingsRead(0);await poll;assert.equal(h.element('network-hostname').value,'new-saved');
  assert.match(h.element('network-settings-status').textContent,/Сохранено имя DHCP: new-saved/);
  const nextPoll=h.intervals[0]();await waitFor(()=>h.pendingNetworkSettingsReads.length===1);
  h.element('network-hostname').value='latest-unsaved';h.element('network-settings-form').listeners.input();
  h.releaseNetworkSettingsRead();await nextPoll;assert.equal(h.element('network-hostname').value,'latest-unsaved');
});

test('new network input during pending save and refresh is retained', async () => {
  const h=harness(false,networkSettingsCaps);await tick();h.holdNetworkSettingsWrites();
  h.element('network-hostname').value='submitted';h.element('network-settings-form').listeners.input();submit(h,'network-settings');
  await waitFor(()=>h.pendingNetworkSettingsWrites.length===1);
  h.element('network-hostname').value='new-edit';h.element('network-settings-form').listeners.input();
  h.releaseNetworkSettingsWrite();await waitFor(()=>!h.element('network-settings-fields').disabled);
  assert.equal(h.element('network-hostname').value,'new-edit');
  await h.intervals[0]();assert.equal(h.element('network-hostname').value,'new-edit');
});

test('network saves serialize time Wi-Fi and file forms and block OTA until persistence finishes', async () => {
  const h=harness(false,{...networkSettingsCaps,nativeTimeApi:'/api/native/time',ota:true});await tick();
  h.holdNetworkSettingsWrites();h.element('network-hostname').value='pending';submit(h,'network-settings');
  await waitFor(()=>h.pendingNetworkSettingsWrites.length===1);
  assert(['time','wifi','playlist','assets','firmware','network-settings'].every(name=>h.element(name+'-fields').disabled));
  h.element('firmware-file').files=[file('app.bin','image')];h.element('playlist-file').files=[file('stations.csv')];
  const before=h.requests.length;submit(h,'time');submit(h,'wifi');submit(h,'playlist');submit(h,'firmware');submit(h,'network-settings');
  await tick();assert.equal(h.requests.length,before);assert.equal(h.firmwareRequests.length,0);
  h.releaseNetworkSettingsWrite();await waitFor(()=>!h.element('network-settings-fields').disabled);
  submit(h,'firmware');await waitFor(()=>h.firmwareRequests.length===1);
  const during=h.requests.length;submit(h,'network-settings');h.intervals[0]();await tick();
  assert.equal(h.requests.length,during);assert.equal(h.element('network-settings-fields').disabled,true);
  h.firmwareRequests[0].finish();await tick();submit(h,'network-settings');h.intervals[0]();await tick();
  assert.equal(h.requests.length,during);
});

test('independent review: successful timer save cannot leave disabled status after refresh failure', async () => {
  const h=harness(false,networkSettingsCaps);await tick();
  assert.match(h.element('network-timeout-status').textContent,/перезапуск отключён/);
  h.element('network-hostname').value='yoradio';h.element('network-ap-timeout').value='1';
  h.element('network-settings-form').listeners.input();h.failNetworkSettingsGet('Snapshot busy');
  submit(h,'network-settings');
  await waitFor(()=>h.element('network-settings-status').textContent==='Настройки сохранены; состояние пока недоступно');
  assert.equal(h.networkSettings.ap_timeout_minutes,1);
  assert.doesNotMatch(h.element('network-timeout-status').textContent,/перезапуск отключён/);
});
