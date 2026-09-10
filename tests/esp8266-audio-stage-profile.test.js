const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
test('actual diagnostic stage accounting is exclusive, bounded and rollover safe', () => {
  const windows = process.platform === 'win32';
  const run = (cmd, args) => spawnSync(windows ? 'wsl.exe' : cmd,
    windows ? ['--exec', cmd, ...args] : args, {encoding:'utf8', timeout:60000});
  const host = p => {
    if (!windows) return p;
    const r = run('wslpath', ['-a', '-u', p]);
    assert.equal(r.status, 0, r.stderr); return r.stdout.trim();
  };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'audio-stage-'));
  try {
    const binary = host(path.join(dir, 'test'));
    const built = run('cc', ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
      '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
      '-I' + host(path.join(root, 'esp8266/rtos-sdk-native/main')),
      host(path.join(root, 'tests/native/esp8266_audio_stage_profile.c')), '-o', binary]);
    assert.equal(built.status, 0, built.stdout + built.stderr);
    const result = run(binary, []);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.stdout, /stage accounting PASS/);
  } finally { fs.rmSync(dir, {recursive:true, force:true}); }
});
test('instrumentation uses existing debug-only profile and leaves scheduling unchanged', () => {
  const read = p => fs.readFileSync(path.join(root, p), 'utf8');
  const inc = read('esp8266/rtos-sdk-native/main/audio_stage_profile.inc');
  assert.match(inc, /#if YORADIO_ESP8266_OPUS_STREAM_TEST/);
  assert.match(inc, /#else\s+#define AUDIO_STAGE_BEGIN\(name\) \(\(void\)0\)\s+#define AUDIO_STAGE_END\(stage, name\) \(\(void\)0\)/);
  assert.doesNotMatch(inc, /\b(?:malloc|calloc|vTaskDelay|ESP_LOGI)\s*\(/);
  const source = read('esp8266/rtos-sdk-native/main/audio_service.c');
  for (const stage of ['READ', 'DECODE', 'OUTPUT']) assert.match(source, new RegExp('AUDIO_STAGE_END\\(AUDIO_STAGE_' + stage));
  assert.match(source, /AUDIO_STAGE_END\(decoded == 0 \? AUDIO_STAGE_WAIT : AUDIO_STAGE_INPUT_WAIT,\s*wait_stage\)/);
  assert.match(source, /if \(decoded == 0\) \{[^]*?vTaskDelay\(pdMS_TO_TICKS\(1\)\);/);
});
