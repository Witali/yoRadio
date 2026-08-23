const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), 'utf8');

test('codec benchmark generates deterministic maximum-rate fixtures', () => {
  const generator = read('tools', 'codec_benchmark', 'generate.ps1');

  assert.match(generator, /seed=12345/);
  assert.match(generator, /seed=67890/);
  assert.match(generator, /"libmp3lame", "-b:a", "320k"/);
  assert.match(generator, /"aac", "-profile:a", "aac_low", "-b:a", "320k"/);
  assert.match(generator, /"flac", "-compression_level", "8"/);
  assert.match(generator, /"libvorbis", "-q:a", "10"/);
  assert.match(generator, /"libopus", "-b:a", "510k", "-vbr", "off"/);
});

test('codec benchmark flashes and runs the same checked fixture matrix', () => {
  const runner = read('tools', 'codec_benchmark', 'run.ps1');
  const document = read('docs', 'ESP32C3_CODEC_BENCHMARK.md');

  for (const fixture of [
    'mp3-320.mp3',
    'aac-lc-320.aac',
    'flac-level8.flac',
    'vorbis-q10.ogg',
    'opus-510.ogg',
  ]) {
    assert.match(runner, new RegExp(fixture.replace('.', '\\.')));
  }
  assert.match(runner, /0x190000/);
  assert.match(runner, /0x240000/);
  assert.match(runner, /0x59434658/);
  assert.match(runner, /IO\.BinaryWriter/);
  assert.match(runner, /System\.IO\.Ports\.SerialPort/);
  assert.match(document, /## MP3 320 kbit\/s/);
  assert.match(document, /## Ogg Opus 510 kbit\/s/);
});

test('codec benchmark firmware uses all non-SPIFFS flash without OTA', () => {
  const partitions = read('idf', 'esp32c3-oled-native',
                          'partitions-codec-benchmark.csv');
  const builder = read('tools', 'codec_benchmark', 'build.ps1');

  assert.match(partitions, /factory,\s+app,\s+factory,\s+0x10000,\s+0x180000/);
  assert.match(partitions, /codec_test,\s+data,\s+0x40,\s+0x190000,\s+0x240000/);
  assert.match(partitions, /spiffs,\s+data,\s+spiffs,\s+0x3D0000/);
  assert.doesNotMatch(partitions, /ota_[01]|otadata/);
  assert.match(builder, /YORADIO_CODEC_BENCHMARK=ON/);
  assert.match(builder, /sdkconfig\.codec-benchmark\.defaults/);
});
test('codec benchmark reports comparable decoder heap and payload memory', () => {
  const audio = read('idf', 'esp32c3-oled-native', 'main', 'audio_service.c');
  const adapter = read('idf', 'components', 'custom_legacy_codecs',
                       'custom_legacy_adapter.cpp');
  const header = read('idf', 'components', 'custom_legacy_codecs',
                      'custom_legacy_adapter.h');

  assert.match(audio, /MEM %s %s: heap_before/);
  assert.match(audio, /heap_caps_get_largest_free_block/);
  assert.match(audio, /heap_caps_get_minimum_free_size/);
  assert.match(audio, /"first-frame"/);
  assert.match(adapter, /CodecArenaUsed()/);
  assert.match(header, /custom_legacy_decoder_memory_used/);
});

test('MP3 backend benchmark selects all decoders and saves reproducible results', () => {
  const builder = read('tools', 'codec_benchmark', 'build.ps1');
  const runner = read('tools', 'codec_benchmark', 'run-mp3-backends.ps1');

  assert.match(builder, /ValidateSet\("espressif", "helix", "minimp3"\)/);
  assert.match(builder, /sdkconfig\.mp3-\$Mp3Decoder\.defaults/);
  for (const backend of ['espressif', 'helix', 'minimp3']) {
    assert.match(runner, new RegExp(`"${backend}"`));
    assert.match(runner, new RegExp(`\\$backend\\.log`));
  }
  assert.match(runner, /mp3-320\.mp3/);
  assert.match(runner, /0x190000/);
  assert.match(runner, /summary\.csv/);
  assert.match(runner, /finally/);
  assert.match(runner, /sdkconfig\.mp3-helix\.defaults/);
  assert.match(runner, /"0x10000", \$normalApp/);
  assert.match(runner, /"0x1f0000", \$normalApp/);
  assert.doesNotMatch(runner, /"0x3d0000"/);
  assert.match(runner, /SPIFFS and NVS were preserved/);
});
