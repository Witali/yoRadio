const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const zlib = require('node:zlib');
const test = require('node:test');
const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const main = 'esp8266/rtos-sdk-native/main/';

test('two bounded WebSocket subscribers share a single HTTP-owned status buffer', () => {
  const source = read(main+'web_service.c');
  assert.match(source, /#define WEB_WS_CLIENTS 2U/);
  assert.match(source, /s_ws_fds\[WEB_WS_CLIENTS\]/);
  const subscribe = source.slice(source.indexOf('static bool subscribe_socket'),
    source.indexOf('static void session_closed'));
  assert.doesNotMatch(subscribe, /trigger_close/);
  assert.match(subscribe, /if \(available < 0\) return false/);
  const poll = source.slice(source.indexOf('void web_service_poll(void)'));
  assert.doesNotMatch(poll, /format_status|native_state_snapshot|s_async_message/);
  assert.match(poll, /httpd_queue_work\(s_server, poll_work, NULL\)/);
  const sessions = read('esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_sess.c');
  assert.match(sessions, /!hd->hd_sd\[i\].ws_handshake_done/);
});

test('VBR waits for heartbeat but state, format and metadata remain immediate', () => {
  const source = read(main+'web_service.c');
  const body = source.slice(source.indexOf('static bool status_requires_immediate_send'),
    source.indexOf('static void format_stream'));
  const expression = body.match(/return ([\s\S]*?);/)[1].replace(/->/g, '.');
  const compare = new Function('current', 'previous', 'return '+expression);
  const baseline = {playing:true, connecting:false, station_index:2, volume:160,
    bitrate_kbps:320, sample_rate_hz:44100, channels:2, codec:1,
    station_hash:1, title_hash:2};
  assert.equal(compare({...baseline, bitrate_kbps:299}, baseline), false);
  for(const field of ['playing','connecting','station_index','volume',
    'sample_rate_hz','channels','codec','station_hash','title_hash']) {
    assert.equal(compare({...baseline, [field]:Number(baseline[field])+1}, baseline),
      true, field);
  }
});

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
