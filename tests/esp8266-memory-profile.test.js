const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../esp8266/rtos-sdk-native/main');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');

test('memory diagnostics are compiled out of the ordinary firmware', () => {
  assert.match(read('CMakeLists.txt'), /option\(YORADIO_ESP8266_MEMORY_PROFILE[\s\S]*?OFF\)/);
  assert.match(read('CMakeLists.txt'), /if\(YORADIO_ESP8266_MEMORY_PROFILE\)\s+list\(APPEND YORADIO_SOURCES "memory_profile.c"\)/);
  assert.match(read('memory_profile.h'), /#else[\s\S]*static inline void memory_profile_poll\(void\) \{\}/);
});

test('read-only heap walk uses the SDK lock, flags and allocation alignment', () => {
  const source = read('memory_profile.c');
  const walk = source.slice(source.indexOf('static heap_sample_t sample_heap'), source.indexOf('void memory_profile_register'));
  assert.match(walk, /_heap_caps_lock\(0\)[\s\S]*g_heap_region\[i\][\s\S]*_heap_caps_unlock\(0\)/);
  assert.match(walk, /mem_blk_next\(block\)/);
  assert.match(walk, /!mem_blk_is_used\(block\)/);
  assert.match(walk, /blk_link_size\(block\) & ~\(HEAP_ALIGN_SIZE - 1U\)/);
  assert.match(walk, /span - MEM_HEAD_SIZE/);
  assert.match(walk, /\(uintptr_t\)next <= address/);
  assert.doesNotMatch(walk, /\b(?:malloc|calloc|realloc|free|ESP_LOGI)\s*\(/);
  assert.doesNotMatch(source, /xTaskCreate\s*\(|uxTaskGetSystemState\s*\(/);
});

test('reports separate byte-addressable DRAM, IRAM and sampled minima', () => {
  const source = read('memory_profile.c');
  assert.match(source, /!\(region->caps & MALLOC_CAP_8BIT\)/);
  assert.match(source, /iram_free \+= region->free_bytes/);
  assert.match(source, /sample.low \+= region->min_free_bytes/);
  assert.match(source, /window_free=%u[\s\S]*window_largest=%u/);
  assert.match(source, /pdMS_TO_TICKS\(10000\)/);
  assert.match(read('app_main.c'), /web_service_poll\(\);\s+memory_profile_poll\(\);/);
  assert.equal((read('audio_service.c').match(/memory_profile_register\(MEMORY_AUDIO\)/g) || []).length, 2);
  assert.match(read('web_service.c'), /memory_profile_register\(MEMORY_WEB\)/);
});

test('physical workload disconnect errors settle once without recursive close', async () => {
  const runner = fs.readFileSync(path.join(root, '../../../tools/esp8266_memory_profile/run.cjs'), 'utf8');
  const functionBody = runner.slice(runner.indexOf('async function rawCommand'), runner.indexOf('async function command'));
  let socket;
  let closes = 0;
  class Socket {
    static OPEN = 1;
    constructor() { socket = this; this.readyState = Socket.OPEN; }
    close() { ++closes; if (this.onerror) this.onerror(); }
  }
  const context = vm.createContext({WebSocket: Socket, host: 'test.invalid', setTimeout, clearTimeout});
  vm.runInContext(functionBody, context);
  const pending = context.rawCommand('stop=1');
  socket.onerror();
  await assert.rejects(pending, /command connection/);
  assert.equal(closes, 1);
  assert.equal(socket.onerror, null);
  assert.match(runner, /finally[\s\S]*browser.close[\s\S]*rawCommand\(`play=\$\{original.station\}`\)[\s\S]*rawCommand\('stop=1'\)/);
});
