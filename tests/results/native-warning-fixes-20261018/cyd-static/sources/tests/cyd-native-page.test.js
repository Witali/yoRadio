const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const page = fs.readFileSync(path.join(__dirname, '../idf/esp32-cyd2usb-native/main/web_pages.cpp'), 'utf8');
const script = page.split('// NATIVE_UI_BEGIN')[1].split('// NATIVE_UI_END')[0];
const tick = () => new Promise(resolve => setImmediate(resolve));

function harness(failBoot = false) {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {id, value:'', checked:false, disabled:true, textContent:'',
      listeners:{}, addEventListener(event, fn) { this.listeners[event] = fn; }});
    return elements.get(id);
  };
  const radioButtons = ['previous','toggle','next','stop'].map(action => ({...element(action),dataset:{radio:action}}));
  const buttons = [...radioButtons,element('station-submit'),element('audio-submit'),element('reconnect')];
  const timers = new Map(), intervals = [], sockets = [], requests = [];
  let nextTimer = 0, now = 1000, failSettings = false;
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
  const context = vm.createContext({console,URLSearchParams,WebSocket:Socket,
    location:{protocol:'http:',host:'radio.local'},Date:{now:()=>now},
    document:{getElementById:element,activeElement:null,
      querySelectorAll: selector => selector === '[data-radio]' ? radioButtons : buttons},
    setTimeout(fn, ms) { timers.set(++nextTimer,{fn,ms});return nextTimer; },
    clearTimeout(id) { timers.delete(id); },setInterval(fn) { intervals.push(fn); },
    async fetch(url, options) {
      requests.push({url,...options});
      const uri = new URL(url,'http://radio.local');
      const name = uri.pathname.split('/').at(-1);
      if ((failBoot && name === 'capabilities') || (failSettings && name === 'settings' && options.method==='POST')) {
        failSettings=false;
        return {ok:false,text:async()=>'Сохранение не удалось'};
      }
      const data = name === 'capabilities' ? {audio_output:'PDM',websocket:true,smartstart:true,wifi_reconnect:true} :
        name === 'settings' ? settings : name === 'radio' ? radio : name === 'status' ? state : {reconnecting:true};
      return {ok:true,json:async()=>structuredClone(data)};
    }});
  vm.runInContext(script,context);
  return {element,context,buttons,radioButtons,sockets,requests,timers,intervals,settings,radio,
    setNow(value) { now=value; },failSettings() { failSettings=true; }};
}

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
