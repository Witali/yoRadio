const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

const root = path.resolve(__dirname, '..');
const audio = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/audio_service.c'), 'utf8').replace(/\r\n/g, '\n');
const task = audio.slice(audio.lastIndexOf('static void audio_task('));

function section(source, begin, end) {
  const first = source.indexOf(begin), last = source.indexOf(end, first);
  assert.ok(first >= 0 && last > first, 'Production source boundaries: ' + begin);
  return source.slice(first, last);
}

test('actual audio task keeps Opus on reconnect with bounded cold fallback and cancellation', t => {
  // Like the HTTP ownership harness, compile the production branches verbatim.
  // Only the network, scheduler and low-level codec interfaces are mocked;
  // retry limits, ownership decisions, Stop and generation checks are not.
  let code = fs.readFileSync(path.join(__dirname, 'native/esp8266_opus_reconnect_test.c'), 'utf8');
  const replacements = {
    DEFINES: ['HTTP_OPEN_ATTEMPTS', 'CODEC_HEAP_RESERVE_BYTES'].map(name => {
      const value = audio.match(new RegExp('^#define ' + name + ' .*$', 'm'));
      assert.ok(value); return value[0];
    }).join('\n'),
    RELEASE: section(audio, 'static void release_codec(', 'static bool generation_current('),
    REQUEUE: section(audio, 'static void requeue_if_current(', 'static uint32_t advance_generation('),
    STOP: section(task, '        if (!command.play) {', '        opus_benchmark_cancel_pending();'),
    OPEN: section(task, '        int opened = -1;', '        size_t detect_size = stream.body_size;'),
    SNIFF: section(task, '        bool decoder_ready = codec', '        log_audio_stack("decoder ready");'),
    RECONNECT: section(task, '        int stream_closed = close(stream.socket);', '\n    }\n}\n#endif'),
  };
  for (const [name, value] of Object.entries(replacements)) code = code.replace('/* ' + name + ' */', value);
  assert.doesNotMatch(code, /\/\* (?:DEFINES|RELEASE|REQUEUE|STOP|OPEN|SNIFF|RECONNECT) \*\//);
  const windows = process.platform === 'win32';
  const run = (program, args) => spawnSync(windows ? 'wsl.exe' : program,
    windows ? ['--exec', program, ...args] : args,
    {encoding: 'utf8', timeout: 60000});
  const cc = process.env.CC || 'cc';
  const probe = run(cc, ['--version']);
  if (probe.error?.code === 'ENOENT' || probe.status !== 0) return t.skip('Host C compiler (WSL on Windows) unavailable');
  const hostPath = value => {
    if (!windows) return value;
    const result = run('wslpath', ['-a', '-u', value]);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    return result.stdout.trim();
  };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-opus-reconnect-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const source = path.join(dir, 'test.c');
  fs.writeFileSync(source, code);
  for (const opus of [0, 1]) {
    const binary = hostPath(path.join(dir, 'test-' + opus));
    const built = run(cc, ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-pedantic',
      '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
      '-DCONFIG_YORADIO_OGG_OPUS=' + opus,
      '-I' + hostPath(path.join(root, 'esp8266/rtos-sdk-native/components/helix_codecs')),
      hostPath(source), '-o', binary]);
    assert.equal(built.status, 0, built.stdout + '\n' + built.stderr);
    const result = run('env', ['ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
      'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', binary]);
    assert.equal(result.status, 0, result.stdout + '\n' + result.stderr);
    assert.match(result.stdout, /actual reconnect control-flow PASS/);
    t.diagnostic(result.stdout.trim());
  }
});
