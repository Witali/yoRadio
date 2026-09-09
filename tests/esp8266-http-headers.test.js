const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const windows = process.platform === 'win32';
const hostPath = file => windows ? '/mnt/' + file[0].toLowerCase() + file.slice(2).replace(/\\/g, '/') : file;
function execute(program, args) {
  return spawnSync(windows ? 'wsl.exe' : program, windows ? ['--exec', program, ...args] : args,
    { encoding: 'utf8', timeout: 60000 });
}

test('incremental radio response headers reuse one 1-KiB buffer under ASan/UBSan', t => {
  const compiler = execute('gcc', ['--version']);
  if (compiler.error?.code === 'ENOENT' || compiler.status !== 0)
    return t.skip('GCC unavailable (WSL on Windows).');
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-http-headers-'));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const main = path.join(root, 'esp8266/rtos-sdk-native/main');
  const binary = path.join(directory, 'test');
  const build = execute('gcc', ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
    '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
    '-I' + hostPath(main), hostPath(path.join(main, 'http_stream_protocol.c')),
    hostPath(path.join(__dirname, 'native/esp8266_http_headers_test.c')), '-o', hostPath(binary)]);
  assert.equal(build.status, 0, build.stdout + '\n' + build.stderr);
  const capture = path.join(root, '.build/opus-intense-new.headers');
  const run = execute(hostPath(binary), fs.existsSync(capture) ? [hostPath(capture)] : []);
  assert.equal(run.status, 0, run.stdout + '\n' + run.stderr);
  assert.match(run.stdout, /Incremental HTTP header tests PASS/);
  t.diagnostic(run.stdout.trim());
});
