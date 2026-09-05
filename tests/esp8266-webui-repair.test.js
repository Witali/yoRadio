const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const zlib = require('node:zlib');
const test = require('node:test');
const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const main = 'esp8266/rtos-sdk-native/main/';

test('native stream identity is invalidated when changing the station', () => {
  const source = read(main+'native_state.c');
  const change = source.slice(source.indexOf('void native_state_set_station(uint16_t'),
    source.indexOf('void native_state_set_volume'));
  for(const field of ['bitrate_kbps', 'sample_rate_hz', 'channels', 'buffer_percent'])
    assert.match(change, new RegExp('s_state\\.'+field+' = 0;'));
  assert.match(change, /s_state.codec = CODEC_NONE/);
  assert.match(change, /s_state.error\[0\] = '\\0'/);
});

test('native connecting telemetry locks and unlocks Play without affecting Arduino states', () => {
  const source = zlib.gunzipSync(fs.readFileSync(path.join(root, 'yoRadio/data/www/script.js.gz'))).toString();
  const setup = source.slice(source.indexOf('function setupElement'), source.indexOf('/***--- playlist'));
  const calls = [];
  const context = {setPlaybackPending: value => calls.push(value), getId: () => null};
  vm.runInNewContext(setup, context);
  context.setupElement('connecting', true);
  context.setupElement('connecting', false);
  context.setupElement('playerwrap', 'playing');
  assert.deepEqual(calls, [true, false, false]);
  const server = read(main+'web_service.c');
  assert.match(server, /current->connecting != previous->connecting/);
  assert.match(server, /text_hash\(state->error\)/);
});
