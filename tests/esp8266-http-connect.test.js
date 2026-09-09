const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

test('actual HTTP connect has a bounded nonblocking lifecycle and cancels obsolete commands', t => {
  const root = path.resolve(__dirname, '..');
  const audio = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/audio_service.c'), 'utf8');
  const first = audio.indexOf('static void set_socket_timeout(');
  const last = audio.indexOf('static bool socket_wait_writable(', first);
  assert.ok(first >= 0 && last > first, 'Compile production connect and wait helpers verbatim');
  const defines = ['SOCKET_CONNECT_TIMEOUT_MS', 'SOCKET_CONNECT_POLL_MS',
    'SOCKET_READ_TIMEOUT_MS', 'SOCKET_WRITE_TIMEOUT_MS'].map(name => {
    const value = audio.match(new RegExp('^#define ' + name + ' .*$', 'm'));
    assert.ok(value); return value[0];
  }).join('\n');
  const code = fs.readFileSync(path.join(__dirname, 'native/esp8266_http_connect_test.c'), 'utf8')
    .replace('/* DEFINES */', defines)
    .replace('/* CONNECT_IMPLEMENTATION */', audio.slice(first, last));
  const windows = process.platform === 'win32';
  const run = (program, args) => spawnSync(windows ? 'wsl.exe' : program,
    windows ? ['--exec', program, ...args] : args,
    {encoding: 'utf8', timeout: 60000});
  const cc = process.env.CC || 'cc';
  const probe = run(cc, ['--version']);
  if (probe.error?.code === 'ENOENT' || probe.status !== 0)
    return t.skip('Host C compiler (WSL on Windows) unavailable');
  const hostPath = value => {
    if (!windows) return value;
    const result = run('wslpath', ['-a', '-u', value]);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    return result.stdout.trim();
  };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-http-connect-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const source = path.join(dir, 'test.c'), binary = hostPath(path.join(dir, 'test'));
  fs.writeFileSync(source, code);
  const build = run(cc, ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-pedantic',
    '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
    hostPath(source), '-o', binary]);
  assert.equal(build.status, 0, build.stdout + '\n' + build.stderr);
  const result = run('env', ['ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
    'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', binary]);
  assert.equal(result.status, 0, result.stdout + '\n' + result.stderr);
  assert.match(result.stdout, /actual HTTP connect lifecycle PASS/);
  t.diagnostic(result.stdout.trim());
});
