const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { execute, hostPath, root } = require('../tools/esp8266_opus_profile/build_host.cjs');
test('diagnostic live Opus URL request validates and queues without changing playlist', () => {
  const source = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/web_service.c'), 'utf8');
  const start = source.indexOf('static esp_err_t opus_test_stream_handler(');
  const end = source.indexOf('static esp_err_t opus_benchmark_start_handler(', start);
  assert.ok(start > 0 && end > start);
  const handler = source.slice(start, end);
  assert.doesNotMatch(handler, /playlist_service|persistent_settings/);
  assert.match(source.slice(source.lastIndexOf('#if', start), start), /YORADIO_ESP8266_OPUS_BENCHMARK/);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opus-stream-request-'));
  try {
    fs.writeFileSync(path.join(dir, 'handler.inc'), handler);
    const binary = path.join(dir, 'test');
    execute('g++', ['-std=c++17', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
      '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-pie', '-no-pie',
      '-I' + hostPath(dir), hostPath(path.join(root, 'tests/native/opus_stream_request_test.cpp')),
      '-o', hostPath(binary)]);
    assert.match(execute(hostPath(binary), []), /Opus stream request PASS/);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});
