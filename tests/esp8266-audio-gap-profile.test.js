const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const root = path.resolve(__dirname, '../esp8266/rtos-sdk-native/main');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');

test('audio gap instrumentation is opt-in and its report window is configurable', () => {
  const cmake = read('CMakeLists.txt');
  assert.match(cmake, /option\(YORADIO_ESP8266_AUDIO_PROFILE[\s\S]*?OFF\)/);
  assert.match(cmake, /set\(YORADIO_ESP8266_AUDIO_PROFILE_WINDOW_MS "5000"/);
  assert.match(read('esp8266_nodac_i2s.h'), /#if YORADIO_ESP8266_AUDIO_PROFILE[\s\S]*esp8266_nodac_profile_t/);
});

test('DMA profiler distinguishes incomplete buffer starts from incomplete EOFs', () => {
  const source = read('esp8266_nodac_i2s.c');
  assert.match(source, /s_current_buffer == next->buf_ptr[\s\S]*?\+\+s_underruns/);
  assert.match(source, /#if YORADIO_ESP8266_AUDIO_PROFILE[\s\S]*?s_current_buffer == finished->buf_ptr[\s\S]*?\+\+s_profile.incomplete_eof/);
  assert.match(source, /s_profile.incomplete_words \+=[\s\S]*?NODAC_DMA_BUFFER_WORDS - s_current_position/);
});

test('profile snapshots DMA before UART logging and resets baseline afterwards', () => {
  const source = read('audio_profile_wrappers.cpp');
  const report = source.slice(source.indexOf('void maybe_report()'), source.indexOf('}  // namespace'));
  assert.ok(report.indexOf('esp8266_nodac_i2s_profile(&dma)') < report.indexOf('ESP_LOGI'));
  assert.ok(report.lastIndexOf('reset_profile(') > report.lastIndexOf('ESP_LOGI'));
  assert.match(source, /s_previous_pcm_end = 0/);
  assert.match(source, /started - s_previous_pcm_end/);
});
