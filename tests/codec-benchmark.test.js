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
  assert.match(runner, /api\/native\/benchmark\?codec=/);
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
