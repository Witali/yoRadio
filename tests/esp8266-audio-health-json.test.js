const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execute, hostPath, root} = require('../tools/esp8266_opus_profile/build_host.cjs');

test('health JSON preserves counters and gates transport fields without a stack body buffer', t => {
  const source = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/web_service.c'), 'utf8');
  const start = source.indexOf('static esp_err_t audio_health_handler(');
  const end = source.indexOf('\n#if YORADIO_ESP8266_SPIFFS_LOG_HTTP', start);
  assert.ok(start > 0 && end > start);
  const handler = source.slice(start, end);
  assert.doesNotMatch(handler, /char body\[/);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opus-health-json-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  fs.writeFileSync(path.join(dir, 'health_under_test.inc'), handler);
  for (const stream of [0, 1]) for (const decodeOnly of [0, 1]) {
    const binary = path.join(dir, `probe-${stream}-${decodeOnly}`);
    execute('gcc', ['-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
      '-fno-sanitize-recover=all', '-fno-pie', '-no-pie',
      '-DYORADIO_ESP8266_OPUS_STREAM_TEST=' + stream,
      '-DYORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY=' + decodeOnly,
      '-I' + hostPath(dir), hostPath(path.join(root, 'tests/native/esp8266_audio_health_json_test.c')), '-o', hostPath(binary)]);
    const result = JSON.parse(execute(hostPath(binary), []));
    assert.equal(result.output_enabled, !decodeOnly);
    assert.equal(result.generation, 0xffffffff);
    assert.equal(result.free_iram, 0xffffffff);
    for (const field of ['transport_phase', 'transport_result', 'transport_errno', 'input_bytes'])
      assert.equal(field in result, !!stream);
    if (stream) {
      assert.equal(result.transport_result, -2147483648);
      assert.equal(result.transport_errno, 2147483647);
      assert.equal(result.input_bytes, 0xffffffff);
    }
  }
});
