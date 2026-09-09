const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/app_main.c'), 'utf8');
const start = app.indexOf('    /* Background poll scheduling:');
const end = app.indexOf('    /* End background poll scheduling. */');
assert.ok(start >= 0 && end > start);
// Execute the real app loop with virtual ticks/notifications, not a copy of
// a rate-limit predicate. GPIO, services and RTOS waits are deterministic mocks.
for (const hz of [0, 10, 20]) test(`app loop: LED ${hz} Hz does not accelerate services or delay controls`, t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-app-poll-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const fixture = fs.readFileSync(path.join(__dirname, 'native/esp8266_app_poll_test.c'), 'utf8');
  const file = path.join(dir, 'test.c'), exe = path.join(dir, process.platform === 'win32' ? 'test.exe' : 'test');
  fs.writeFileSync(file, fixture.replace('/* APP_LOOP */', app.slice(start, end)));
  const flags = [`CONFIG_YORADIO_STATUS_LED=${hz ? 1 : 0}`, `LED_HZ=${hz || 20}`];
  let build;
  if (process.platform === 'win32') {
    let vc; const base = 'C:/Program Files/Microsoft Visual Studio';
    if (fs.existsSync(base)) for (const version of fs.readdirSync(base)) for (const edition of fs.readdirSync(path.join(base, version))) {
      const p = path.join(base, version, edition, 'VC/Auxiliary/Build/vcvars64.bat'); if (fs.existsSync(p)) vc = p;
    }
    assert.ok(vc, 'MSVC required');
    const batch = path.join(dir, 'build.cmd');
    fs.writeFileSync(batch, `@call "${vc}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c11 /W4 /WX ${flags.map(f => '/D' + f).join(' ')} "${file}" /Fe:"${exe}"\r\n`);
    build = spawnSync('cmd.exe', ['/d', '/c', batch], {cwd: dir, encoding: 'utf8', timeout: 60000});
  } else {
    build = spawnSync('cc', ['-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined', ...flags.map(f => '-D' + f), file, '-o', exe], {cwd: dir, encoding: 'utf8', timeout: 60000});
  }
  assert.equal(build.status, 0, build.stdout + '\n' + build.stderr);
  const run = spawnSync(exe, [], {encoding: 'utf8', timeout: 10000});
  assert.equal(run.status, 0, run.stdout + '\n' + run.stderr);
  assert.match(run.stdout, /app poll PASS/); t.diagnostic(run.stdout.trim());
});
