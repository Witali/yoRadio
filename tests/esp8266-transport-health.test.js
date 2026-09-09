const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

test('transport health latches terminal refill across reconnect and has no production RAM', t => {
  const main = path.resolve(__dirname, '../esp8266/rtos-sdk-native/main');
  const audio = fs.readFileSync(path.join(main, 'audio_service.c'), 'utf8');
  const refill = fs.readFileSync(path.join(main, 'stream_input_refill.inc'), 'utf8');
  function section(start, end) {
    const first = audio.indexOf(start), last = audio.indexOf(end, first);
    assert.ok(first >= 0 && last > first, start); return audio.slice(first, last);
  }
  const code = fs.readFileSync(path.join(__dirname, 'native/esp8266_transport_health_test.c'), 'utf8')
    .replace('/* HEALTH */', section('static volatile uint32_t s_generation;', '/* Reused for HTTP headers'))
    .replace('/* ADVANCE */', section('static uint32_t advance_generation(', '#include "audio_web_pause.inc"'))
    .replace('/* FILL_ENUM */', refill.match(/enum \{[\s\S]*?\};/)[0])
    .replace('/* TERMINAL_FILL */', section('            if (filled == STREAM_FILL_EOF || filled == STREAM_FILL_TIMEOUT ||', '            if (prefill) {'));
  // Call placement is actual source, not a second state machine in the test.
  assert.match(audio, /audio_transport_phase\(AUDIO_TRANSPORT_DNS\);\s+int dns_error = getaddrinfo/);
  assert.match(audio, /audio_transport_phase\(AUDIO_TRANSPORT_CLOSE\);\s+int stream_closed = close\(stream.socket\);\s+\(void\)stream_closed;\s+audio_transport_phase\(AUDIO_TRANSPORT_IDLE\)/);
  assert.match(audio, /audio_transport_phase\(AUDIO_TRANSPORT_DECODE\);\s+int decoded = helix_codec_process_one[\s\S]*?audio_transport_phase\(AUDIO_TRANSPORT_REFILL\)/);
  assert.match(audio, /release_codec\(&codec, &codec_kind, "decoder init error"\);\s+audio_transport_phase\(AUDIO_TRANSPORT_IDLE\)/);
  const windows = process.platform === 'win32';
  const run = (program, args) => spawnSync(windows ? 'wsl.exe' : program,
    windows ? ['--exec', program, ...args] : args, {encoding:'utf8', timeout:60000});
  const cc = process.env.CC || 'cc';
  if (run(cc, ['--version']).status !== 0) return t.skip('Host C compiler (WSL on Windows) unavailable');
  const hostPath = value => {
    if (!windows) return value;
    const result = run('wslpath', ['-a', '-u', value]);
    assert.equal(result.status, 0, result.stdout + result.stderr); return result.stdout.trim();
  };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-transport-health-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const source = path.join(dir, 'test.c');
  fs.writeFileSync(source, code); fs.writeFileSync(path.join(dir, 'esp_err.h'), 'typedef int esp_err_t;\n');
  for (const enabled of [0, 1]) {
    const binary = hostPath(path.join(dir, 'test-' + enabled));
    const build = run(cc, ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-pedantic',
      '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
      '-DYORADIO_ESP8266_OPUS_STREAM_TEST=' + enabled, '-I' + hostPath(main),
      '-I' + hostPath(dir), hostPath(source), '-o', binary]);
    assert.equal(build.status, 0, build.stdout + build.stderr);
    const result = run('env', ['ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1', binary]);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.stdout, /transport health PASS/);
    const symbols = run('nm', ['-a', '-S', binary]);
    assert.equal(symbols.status, 0, symbols.stdout + symbols.stderr);
    if (!enabled) assert.doesNotMatch(symbols.stdout, /s_transport_|audio_transport_/);
    t.diagnostic(result.stdout.trim());
  }
});
