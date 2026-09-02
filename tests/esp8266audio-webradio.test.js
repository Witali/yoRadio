const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const root = path.resolve(__dirname, '..');
const target = path.join(root, 'esp8266', 'arduino-esp8266audio-webradio');
const sketch = fs.readFileSync(path.join(target, 'ESP8266AudioWebRadio', 'ESP8266AudioWebRadio.ino'), 'utf8');
const setup = fs.readFileSync(path.join(target, 'setup.ps1'), 'utf8');
const build = fs.readFileSync(path.join(target, 'build.ps1'), 'utf8');

test('ESP8266Audio reference target pins its upstream dependencies', () => {
  assert.match(setup, /ESP8266Audio@2\.4\.1/);
  assert.match(setup, /esp8266:esp8266@3\.1\.2/);
  assert.match(setup, /FABE42E0EB04D00E776A66178299FF95A46C623DBC260F997E58FD514853DD40/);
});

test('ESP8266Audio reference target uses the official streaming pipeline', () => {
  for (const symbol of ['AudioFileSourceICYStream', 'AudioFileSourceBuffer', 'AudioGeneratorMP3', 'AudioGeneratorAAC', 'AudioOutputI2SNoDAC']) {
    assert.match(sketch, new RegExp(symbol));
  }
  assert.match(sketch, /constexpr size_t kStreamBufferBytes = 5 \* 1024/);
  assert.match(sketch, /constexpr size_t kCodecWorkspaceBytes = 29192/);
});

test('ESP8266Audio Web API exposes status and player controls', () => {
  for (const route of ['/api/status', '/api/play', '/api/stop', '/api/volume', '/api/wifi']) {
    assert.ok(sketch.includes(`server.on("${route}"`), `missing ${route}`);
  }
  assert.match(sketch, /decoder->stop\(\)[\s\S]*delete decoder[\s\S]*streamBuffer->close\(\)[\s\S]*source->close\(\)/);
});

test('ESP8266Audio build selects the Wemos clock and flash profile', () => {
  assert.match(build, /xtal=160/);
  assert.match(build, /build\.flash_mode=qio/);
  assert.match(build, /build\.flash_freq=40/);
  assert.match(build, /firmware\\development\\esp8266-esp8266audio-webradio/);
});
