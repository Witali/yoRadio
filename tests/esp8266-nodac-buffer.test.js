const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

test('production NoDAC ownership state machine survives delayed producer/EOF interleavings', t => {
  const root = path.resolve(__dirname, '..');
  const sourceDir = path.join(root, 'esp8266/rtos-sdk-native/main');
  const harness = path.join(__dirname, 'native/esp8266_nodac_buffer_test.c');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-nodac-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const exe = path.join(dir, process.platform === 'win32' ? 'test.exe' : 'test');
  let build;
  if (process.platform === 'win32') {
    const base = 'C:\\Program Files\\Microsoft Visual Studio';
    let vcvars;
    if (fs.existsSync(base)) {
      for (const version of fs.readdirSync(base)) {
        for (const edition of fs.readdirSync(path.join(base, version))) {
          const candidate = path.join(base, version, edition, 'VC/Auxiliary/Build/vcvars64.bat');
          if (fs.existsSync(candidate)) vcvars = candidate;
        }
      }
    }
    if (!vcvars) return t.skip('Visual C++ build tools are not installed');
    const batch = path.join(dir, 'build.cmd');
    fs.writeFileSync(batch, `@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c11 /W4 /WX /I"${sourceDir}" "${harness}" /Fe:"${exe}"\r\n`);
    build = spawnSync('cmd.exe', ['/d', '/c', batch], {cwd: dir, encoding: 'utf8'});
  } else {
    build = spawnSync('cc', ['-std=c11', '-Wall', '-Wextra', '-Werror', `-I${sourceDir}`, harness, '-o', exe], {cwd: dir, encoding: 'utf8'});
    if (build.error?.code === 'ENOENT') return t.skip('A host C compiler is not installed');
  }
  assert.equal(build.status, 0, build.stdout + build.stderr);
  const run = spawnSync(exe, [], {encoding: 'utf8'});
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(run.stdout, /NoDAC ownership tests passed/);
});
