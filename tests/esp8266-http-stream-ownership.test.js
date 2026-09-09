const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');

test('actual HTTP opener never publishes a closed socket after a chunk error', t => {
  const audio = fs.readFileSync(path.join(main, 'audio_service.c'), 'utf8');
  function section(start, end) {
    const first = audio.indexOf(start), last = audio.indexOf(end, first);
    assert.ok(first >= 0 && last > first, 'Source boundaries: ' + start);
    return audio.slice(first, last);
  }
  const streamType = audio.match(/typedef struct \{\s+int socket;[\s\S]*?\} http_stream_t;/);
  assert.ok(streamType);
  const cleanup = audio.match(/if \(opened != 0 \|\| !generation_current\(command\.generation\)\) \{\s*(?:audio_transport_phase\([^;]+;\s*)?(if \(stream.socket >= 0\) close\(stream.socket\);)/);
  assert.ok(cleanup, 'Use production caller cleanup, not a test substitute');
  const fixture = fs.readFileSync(path.join(__dirname, 'native/esp8266_http_stream_ownership_test.c'), 'utf8');
  const code = fixture.replace('/* STREAM_TYPE */', streamType[0])
    .replace('/* PARSER_IMPLEMENTATION */', '') // Pure incremental parser is linked below.
    .replace('/* OPEN_IMPLEMENTATION */', section('static int open_http_stream(', 'static void parse_icy_title('))
    .replace('/* CALLER_CLEANUP */', cleanup[1]);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-http-owner-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const source = path.join(dir, 'test.c');
  const exe = path.join(dir, process.platform === 'win32' ? 'test.exe' : 'test');
  fs.writeFileSync(source, code);
  let build;
  if (process.platform === 'win32') {
    const base = 'C:/Program Files/Microsoft Visual Studio'; let vcvars;
    if (fs.existsSync(base)) for (const v of fs.readdirSync(base)) {
      for (const e of fs.readdirSync(path.join(base, v))) {
        const candidate = path.join(base, v, e, 'VC/Auxiliary/Build/vcvars64.bat');
        if (fs.existsSync(candidate)) vcvars = candidate;
      }
    }
    if (!vcvars) return t.skip('Visual C++ build tools unavailable');
    const batch = path.join(dir, 'build.cmd');
    fs.writeFileSync(batch, `@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n` +
      `@cl /nologo /std:c11 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /I"${main}" "${source}" "${path.join(main, 'http_stream_protocol.c')}" /Fe:"${exe}"\r\n`);
    build = spawnSync('cmd.exe', ['/d', '/c', batch], {cwd:dir, encoding:'utf8', timeout:60000});
  } else {
    build = spawnSync('cc', ['-std=c11', '-Wall', '-Wextra', '-Werror', '-I'+main,
      source, path.join(main, 'http_stream_protocol.c'), '-o', exe],
    {cwd:dir, encoding:'utf8', timeout:60000});
    if (build.error?.code === 'ENOENT') return t.skip('Host C compiler unavailable');
  }
  assert.equal(build.status, 0, build.stdout+'\n'+build.stderr);
  const run = spawnSync(exe, [], {encoding:'utf8', timeout:10000});
  assert.equal(run.status, 0, run.stdout+'\n'+run.stderr);
  assert.match(run.stdout, /HTTP stream ownership tests passed/);
});
