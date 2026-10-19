const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const zlib = require('node:zlib');

const root = path.resolve(__dirname, '..');
const script = zlib.gunzipSync(fs.readFileSync(path.join(root, 'yoRadio/data/www/script.js.gz'))).toString('utf8');
const begin = '/* BEGIN NATIVE WIFI EDITOR: tools/web/native_wifi_editor.js */';
const end = '/* END NATIVE WIFI EDITOR */';
const editor = script.slice(script.indexOf(begin), script.indexOf(end) + end.length);
const functionBlock = name => {
  const start = script.indexOf('function ' + name + '(');
  assert.ok(start >= 0, name);
  const next = script.indexOf('\nfunction ', start + 1);
  return script.slice(start, next < 0 ? undefined : next);
};
const metadata = () => ({revision: '0123456789abcdef-0000000000000001', profiles: [
  {id: 'r1', ssid: ' duplicate ', ssid_utf8: true},
  {id: 'r2', ssid: 'legacy\ufffd', ssid_utf8: false},
]});

function harness(options = {}) {
  const ids = new Map(), requests = [], xhr = [], alerts = [], confirmations = [], downloads = [], opened = [];
  class Element {
    constructor(tag) { this.tagName = tag; this.value = ''; this.children = []; this.attributes = {}; this.dataset = {}; this.style = {}; this.events = {}; this.textContent = ''; this.innerHTML = ''; this.classList = {add() {}}; }
    set id(value) { this._id = value; ids.set(value, this); }
    get id() { return this._id; }
    appendChild(child) { this.children.push(child); child.parentNode = this; return child; }
    replaceChildren(...children) { this.children = children; }
    setAttribute(name, value) { this.attributes[name] = String(value); if (name === 'data-pass') this.dataset.pass = value; }
    removeAttribute(name) { delete this.attributes[name]; if (name === 'data-pass') delete this.dataset.pass; }
    attr(name, value) { if (arguments.length === 1) return this.attributes[name]; this.setAttribute(name, value); }
    addEventListener(name, fn) { this.events[name] = fn; }
    click() { if (this.tagName === 'a') downloads.push({href: this.href, name: this.download}); }
    getElementsByTagName(tag) { return tag === 'input' ? this.inputs || [] : []; }
  }
  const element = id => { const value = new Element('div'); value.id = id; return value; };
  const rows = Array.from({length: 5}, (_, index) => {
    const row = new Element('div'); row.inputs = [new Element('input'), new Element('input')];
    row.inputs.forEach((input, field) => { input.id = (field ? 'pass' : 'ssid') + index; const wrapper = new Element('div'); wrapper.appendChild(input); });
    row.inputs[1].setAttribute('data-pass', '');
    return row;
  });
  ['group_wifi', 'settingscontent', 'settingsdone', 'navigation', 'file-upload'].forEach(element);
  const save = element('save'), exportButton = element('export');
  const document = {
    createElement: tag => new Element(tag),
    getElementsByClassName: name => name === 'credential' ? rows : [],
    querySelector: selector => selector.includes('wifiupload') ? save : selector.includes('wifiexport') ? exportButton : null,
  };
  const responses = [];
  const context = {
    document, getId: id => ids.get(id), TextEncoder, Set, Blob,
    URL: {createObjectURL(blob) { downloads.push({blob}); return 'blob:test'; }, revokeObjectURL() {}},
    setTimeout() {}, Date,
    uiResource: value => value,
    window: {alert(value) { alerts.push(value); }, confirm(value) { confirmations.push(value); return options.confirm !== false; }, open(value) { opened.push(value); }, location: {}},
    SSID_WARNING_TEXT: 'Significant SSID whitespace. Save exactly as entered?',
    XMLHttpRequest: class { constructor() { xhr.push(this); } open(method, url) { this.method = method; this.url = url; } send(data) { this.data = data; } },
    fetch(url, config = {}) {
      requests.push({url, ...config});
      const result = responses.length ? responses.shift() : {ok: true, json: metadata};
      if (result instanceof Error) return Promise.reject(result);
      return Promise.resolve(result);
    },
  };
  if (!options.legacy) context.nativeFirmwareOnly = true;
  if (options.esp8266) context.yoVersion = 'esp8266-native';
  if (!options.legacy && !options.unsupported && !options.esp8266) context.nativeWiFiApi = '/api/native/wifi';
  vm.createContext(context);
  let code = editor + '\n' + ['handleWiFiData', 'getWiFi', 'submitWiFi', 'rebootSystem'].map(functionBlock).join('\n');
  if (options.publicReadControl) code = code.replace('if (nativeWiFiMode()) return getNativeWiFi();', '/* mutant: legacy public read */');
  if (options.passwordDomControl) code = code.replace('if (nativeWiFiMode()) return;', '/* mutant: accept downloaded passwords */');
  vm.runInContext(code, context);
  return {context, rows, requests, xhr, alerts, confirmations, downloads, opened, ids, save, exportButton, responses,
    call: (name, ...args) => context[name](...args),
    load: () => context.getWiFi('http://radio/data/wifi.csv?cache=1'),
    success() { responses.push({ok: true, json: () => ({saved: true, rebooting: true})}); },
    action(index, value) { ids.get('native-wifi-action-' + index).value = value; },
    state() { return vm.runInContext('nativeWiFiState', context); },
  };
}

test('actual gzip embeds maintained editor and gates legacy entry points', () => {
  const source = fs.readFileSync(path.join(root, 'tools/web/native_wifi_editor.js'), 'utf8').replace(/\r\n/g, '\n').trim();
  assert.equal(editor, source);
  assert.match(functionBlock('getWiFi'), /if \(nativeWiFiMode\(\)\) return getNativeWiFi\(\)/);
  assert.match(script, /case "wifiexport": if \(nativeWiFiMode\(\)\) exportNativeWiFi\(\); else window\.open/);
});

test('native load downloads SSIDs only, clears legacy attributes and never XHRs raw CSV', async () => {
  const h = harness(); await h.load();
  assert.equal(h.requests.length, 1); assert.equal(h.requests[0].url, '/api/native/wifi'); assert.equal(h.xhr.length, 0);
  assert.equal(h.rows[0].inputs[0].value, ' duplicate '); assert.equal(h.rows[1].inputs[0].value, 'legacy\ufffd');
  assert.equal(h.rows[0].inputs[1].type, 'password'); assert.equal(h.rows[0].inputs[1].value, '');
  assert.equal(h.rows[0].inputs[1].dataset.pass, undefined); assert.equal(h.exportButton.textContent, 'Export SSIDs');
  h.call('handleWiFiData', 'attacker\tOLD_PRIVATE_CANARY\n');
  assert.equal(h.rows[0].inputs[0].value, ' duplicate '); assert.equal(h.rows[0].inputs[1].dataset.pass, undefined);
  assert.ok(!JSON.stringify(h.state()).includes('password'));
});

test('unchanged passwords and legacy SSIDs are omitted using row identity', async () => {
  const h = harness(); await h.load(); h.success(); await h.call('submitWiFi');
  const sent = h.requests.at(-1); assert.equal(sent.method, 'POST'); assert.equal(sent.url, '/api/native/wifi');
  assert.equal(sent.headers['Content-Type'], 'application/json');
  const edit = JSON.parse(sent.body);
  assert.deepEqual(edit.profiles, [{id: 'r1', password_action: 'keep'}, {id: 'r2', password_action: 'keep'}]);
  assert.equal(edit.revision, metadata().revision); assert.equal(h.xhr.length, 0); assert.equal(h.state(), null);
});

test('new password is write-only and explicit open is distinct from blank keep', async () => {
  const h = harness(); await h.load();
  h.rows[0].inputs[1].value = 'NEW_REQUEST_CANARY'; h.rows[0].inputs[1].events.input();
  h.action(1, 'open'); h.success(); await h.call('submitWiFi');
  const edit = JSON.parse(h.requests.at(-1).body);
  assert.deepEqual(edit.profiles, [{id: 'r1', password_action: 'set', password: 'NEW_REQUEST_CANARY'}, {id: 'r2', password_action: 'set', password: ''}]);
  assert.equal(h.rows[0].inputs[1].value, ''); assert.equal(h.rows[0].inputs[1].dataset.pass, undefined);
  const blank = harness(); await blank.load(); blank.rows[2].inputs[0].value = 'open-new';
  await blank.call('submitWiFi'); assert.equal(blank.requests.length, 1); assert.ok(blank.alerts.length);
  blank.action(2, 'open'); blank.success(); await blank.call('submitWiFi');
  assert.equal(JSON.parse(blank.requests.at(-1).body).profiles[2].password, '');
});

test('decoded UTF-8 byte limits and significant spaces are enforced before sending', async () => {
  const h = harness(); await h.load(); h.rows[0].inputs[0].value = '\u00e9'.repeat(16);
  await h.call('submitWiFi'); assert.equal(h.requests.length, 1);
  h.rows[0].inputs[0].value = '\u00e9'.repeat(15); h.rows[0].inputs[1].value = 'p'.repeat(64); h.action(0, 'set');
  await h.call('submitWiFi'); assert.equal(h.requests.length, 1);
  h.rows[0].inputs[1].value = 'p'.repeat(63); h.success(); await h.call('submitWiFi');
  assert.equal(JSON.parse(h.requests.at(-1).body).profiles[0].ssid, '\u00e9'.repeat(15));
  const warning = harness({confirm: false}); await warning.load(); await warning.call('submitWiFi');
  assert.equal(warning.requests.length, 1); assert.ok(warning.confirmations.length);
});

test('stale edits, unavailable metadata and unknown secret-bearing schema fail closed', async () => {
  for (const response of [{ok: false}, new Error('offline'), {ok: true, json: () => ({...metadata(), password: 'OLD_PRIVATE_CANARY'})}]) {
    const h = harness(); h.responses.push(response); await h.load(); await h.call('submitWiFi');
    assert.equal(h.state(), null); assert.equal(h.requests.length, 1); assert.equal(h.xhr.length, 0); assert.equal(h.save.attributes['aria-disabled'], 'true');
  }
  const h = harness(); await h.load(); h.responses.push({ok: false, status: 409});
  await h.call('submitWiFi'); await h.call('submitWiFi');
  assert.equal(h.requests.length, 2); assert.equal(h.state(), null); assert.equal(h.xhr.length, 0);
});

test('delete-all requires explicit confirmation and exports are clearly SSID-only', async () => {
  const h = harness(); await h.load(); h.call('exportNativeWiFi');
  const blob = h.downloads.find(item => item.blob).blob;
  const data = JSON.parse(await blob.text());
  assert.equal(data.format, 'yoradio-ssid-list-v1'); assert.equal(h.downloads.at(-1).name, 'wifi-network-names.json');
  assert.deepEqual(data.profiles.map(row => Object.keys(row).sort()), [['ssid', 'ssid_utf8'], ['ssid', 'ssid_utf8']]);
  assert.equal(h.opened.length, 0);
  h.rows.forEach(row => { row.inputs[0].value = ''; }); h.success(); await h.call('submitWiFi');
  assert.deepEqual(JSON.parse(h.requests.at(-1).body).profiles, []); assert.ok(h.confirmations.some(text => text.includes('Delete all')));
});

test('unsupported native firmware never falls back; legacy firmware stays explicit', async () => {
  const h = harness({unsupported: true}); await h.load(); await h.call('submitWiFi');
  assert.equal(h.requests.length, 0); assert.equal(h.xhr.length, 0); assert.equal(h.state(), null);
  const legacy = harness({legacy: true}); legacy.call('getWiFi', '/data/wifi.csv');
  assert.equal(legacy.requests.length, 0); assert.equal(legacy.xhr[0].url, '/data/wifi.csv');
  legacy.call('handleWiFiData', 'fixture\tLEGACY_SYNTHETIC_PASSWORD\r\n');
  assert.equal(legacy.rows[0].inputs[1].dataset.pass, 'LEGACY_SYNTHETIC_PASSWORD');
  const esp8266 = harness({esp8266: true}); esp8266.call('getWiFi', '/data/wifi.csv');
  assert.equal(esp8266.requests.length, 0); assert.equal(esp8266.xhr[0].url, '/data/wifi.csv');
});

test('semantic controls detect former native public download and password DOM protocol', async () => {
  const read = harness({publicReadControl: true}); await read.load();
  assert.throws(() => assert.equal(read.xhr.length, 0), {code: 'ERR_ASSERTION'});
  assert.equal(read.xhr[0].url, 'http://radio/data/wifi.csv?cache=1');
  const dom = harness({passwordDomControl: true}); await dom.load();
  dom.call('handleWiFiData', 'fixture\tOLD_PRIVATE_CANARY\n');
  assert.throws(() => assert.equal(dom.rows[0].inputs[1].dataset.pass, undefined), {code: 'ERR_ASSERTION'});
});
