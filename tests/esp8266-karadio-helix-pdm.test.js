const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const target = path.join(root, 'esp8266', 'karadio-helix-pdm');
const audio = fs.readFileSync(path.join(
  root, 'esp8266', 'rtos-sdk-native', 'main', 'audio_service.c'), 'utf8');
const cmake = fs.readFileSync(path.join(target, 'main', 'CMakeLists.txt'), 'utf8');
const defaults = fs.readFileSync(path.join(target, 'sdkconfig.defaults'), 'utf8');
const readme = fs.readFileSync(path.join(target, 'README.md'), 'utf8');
const arena = fs.readFileSync(path.join(
  root, 'esp8266', 'rtos-sdk-native', 'components', 'helix_codecs',
  'CodecMemoryArena.cpp'), 'utf8');

test('KaRadio target uses Helix MP3 and DMA I2S PDM without VS1053', () => {
  assert.match(cmake, /YORADIO_ESP8266_KARADIO_PIPELINE=1/);
  assert.match(defaults, /CONFIG_YORADIO_MP3_DECODER_HELIX=y/);
  assert.match(defaults, /CONFIG_YORADIO_HELIX_MP3_SSO=y/);
  assert.match(defaults, /CONFIG_YORADIO_HELIX_AAC=n/);
  assert.match(defaults, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y/);
  assert.match(defaults, /CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y/);
  assert.doesNotMatch(cmake + defaults, /VS1053/i);
});

test('KaRadio pipeline separates network producer from audio consumer', () => {
  assert.match(audio, /KARADIO_NETWORK_PRIORITY 6U/);
  assert.match(audio, /KARADIO_AUDIO_PRIORITY 5U/);
  assert.match(audio, /xTaskCreate\(karadio_network_worker, "karadio-net"/);
  assert.match(audio, /xTaskCreate\(audio_task, "audio"/);
  assert.match(audio, /#define KARADIO_RING_BYTES 4096U/);
  assert.match(audio, /KARADIO_PREBUFFER_BYTES \(KARADIO_RING_BYTES \* 3U \/ 4U\)/);
  assert.match(audio, /ulTaskNotifyTake\(pdTRUE, pdMS_TO_TICKS\(10\)\)/);
});

test('network producer receives directly into the bounded ring', () => {
  assert.match(audio, /karadio_ring_write_window\(&destination\)/);
  assert.match(audio, /stream_receive\(&stream, destination, capacity\)/);
  assert.match(audio, /karadio_ring_commit\(\(size_t\)received\)/);
  assert.match(audio, /karadio_ring_read\(destination, capacity\)/);
  assert.doesNotMatch(audio, /malloc\([^\n]*KARADIO_RING_BYTES/);
});

test('MP3 word workspace uses the physically verified 16-KiB IRAM arena', () => {
  assert.match(arena, /kWordArenaBytes = 16U \* 1024U/);
  assert.doesNotMatch(audio, /s_karadio_prepared_codec/);
});

test('documentation states the physical output and compatibility limits', () => {
  assert.match(readme, /I2S PDM DATA on GPIO3/);
  assert.match(readme, /4096-byte static compressed ring/);
  assert.match(readme, /HTTPS is intentionally not linked/);
  assert.match(readme, /does \*\*not\*\* use a VS1053/);
});
