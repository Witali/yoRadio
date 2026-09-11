const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const windows = process.platform === 'win32';
const hostPath = file => windows ? '/mnt/' + file[0].toLowerCase() + file.slice(2).replace(/\\/g, '/') : file;
function execute(program, args, options = {}) {
  return spawnSync(windows ? 'wsl.exe' : program,
    windows ? ['--exec', program, ...args] : args,
    { encoding: 'utf8', timeout: 60000, ...options });
}

for (const [outputMode, profileStage, publish] of [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 8, 0]]) test(`real board benchmark output=${outputMode} stage=${profileStage} publish=${publish} cleans up OOM/cancel/error and supports repeated runs`, t => {
  const compiler = execute('g++', ['--version']);
  if (compiler.error?.code === 'ENOENT' || compiler.status !== 0)
    return t.skip('C++ compiler unavailable (g++ via WSL on Windows).');
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-opus-board-benchmark-'));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const stubs = path.join(__dirname, 'native/opus_board_benchmark');
  const main = path.join(root, 'esp8266/rtos-sdk-native/main');
  const executable = path.join(directory, 'test');
  const build = execute('g++', ['-std=c++17', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
    '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
    '-DYORADIO_ESP8266_OPUS_BENCHMARK=1', '-DCONFIG_YORADIO_OPUS_SCRATCH_BYTES=6144',
    '-DYORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT=' + outputMode,
    '-DYORADIO_ESP8266_OPUS_PCM_PUBLISH=' + publish,
    '-DYORADIO_OPUS_PROFILE_STAGE=' + profileStage,
    ...(profileStage ? ['-DYORADIO_OPUS_PROFILE_TEST_CLOCK=1', '-I' + hostPath(path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder')),
      hostPath(path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder/opus_stage_profile.c'))] : []),
    '-I' + hostPath(stubs), '-I' + hostPath(main), hostPath(path.join(main, 'opus_benchmark.cpp')),
    hostPath(path.join(stubs, 'test.cpp')), '-o', hostPath(executable)]);
  assert.equal(build.status, 0, build.stdout + '\n' + build.stderr);
  const run = execute(hostPath(executable), []);
  assert.equal(run.status, 0, run.stdout + '\n' + run.stderr);
  assert.match(run.stdout, /Opus board benchmark lifecycle PASS/);
  assert.match(run.stdout, /5 allocation-failure sites/);
  t.diagnostic(run.stdout.trim());
});
