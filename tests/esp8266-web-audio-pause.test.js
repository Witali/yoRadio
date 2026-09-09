const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');
const read = name => fs.readFileSync(path.join(main, name), 'utf8');
const audio = read('audio_service.c');
const web = read('web_service.c');

for (const [mode, value] of [['off', 0], ['short', 1], ['long', 2]]) {
  test(`Web audio pause ${mode}: execute production helpers`, t => {
    const first = audio.indexOf('static void requeue_if_current(');
    const last = audio.indexOf('static uint32_t advance_generation(', first);
    assert.ok(first >= 0 && last > first);
    const fixture = fs.readFileSync(path.join(__dirname, 'native/esp8266_web_audio_pause_test.c'), 'utf8');
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-web-pause-'));
    t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
    const source = path.join(dir, 'test.c');
    const exe = path.join(dir, process.platform === 'win32' ? 'test.exe' : 'test');
    const webFirst = web.indexOf('static esp_err_t static_handler(');
    const webLast = web.indexOf('static esp_err_t register_get(', webFirst);
    assert.ok(webFirst >= 0 && webLast > webFirst);
    fs.writeFileSync(source, fixture.replace('/* REQUEUE_IMPLEMENTATION */', audio.slice(first, last))
      .replace('/* STATIC_HANDLER */', web.slice(webFirst, webLast)));
    let build;
    if (process.platform === 'win32') {
      const base = 'C:/Program Files/Microsoft Visual Studio'; let vcvars;
      if (fs.existsSync(base)) for (const v of fs.readdirSync(base)) {
        for (const e of fs.readdirSync(path.join(base, v))) {
          const candidate = path.join(base, v, e, 'VC/Auxiliary/Build/vcvars64.bat');
          if (fs.existsSync(candidate)) vcvars = candidate;
        }
      }
      assert.ok(vcvars, 'Visual C++ build tools required');
      const batch = path.join(dir, 'build.cmd');
      fs.writeFileSync(batch, `@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n` +
        `@cl /nologo /std:c11 /W4 /WX /wd4505 /DYORADIO_ESP8266_WEB_AUDIO_PAUSE=${value} /I"${main}" "${source}" /Fe:"${exe}"\r\n`);
      build = spawnSync('cmd.exe', ['/d', '/c', batch], {cwd: dir, encoding: 'utf8', timeout: 60000});
    } else {
      build = spawnSync('cc', ['-std=c11', '-Wall', '-Wextra', '-Werror',
        '-Wno-unused-function', '-Wno-unused-variable', `-DYORADIO_ESP8266_WEB_AUDIO_PAUSE=${value}`,
        '-I'+main, source, '-o', exe], {cwd: dir, encoding: 'utf8', timeout: 60000});
    }
    assert.equal(build.status, 0, build.stdout+'\n'+build.stderr);
    const run = spawnSync(exe, [], {encoding: 'utf8', timeout: 10000});
    assert.equal(run.status, 0, run.stdout+'\n'+run.stderr);
    assert.match(run.stdout, /Web audio pause tests passed/);
  });
}

test('pause checkpoints surround open/detect/decode and leave generation semantics intact', () => {
  const native = audio.slice(audio.lastIndexOf('static void audio_task('), audio.indexOf('esp_err_t audio_service_init('));
  assert.equal((native.match(/audio_web_pause_checkpoint/g) || []).length, 4);
  assert.match(native, /audio_web_pause_gate[\s\S]*?xQueueReceive\(s_commands, &command, AUDIO_WEB_QUEUE_WAIT\)/);
  assert.match(native, /audio_web_pause_checkpoint[^\n]+\n\s*close\(stream.socket\)/);
  const pause = read('audio_web_pause.inc');
  assert.doesNotMatch(pause, /vTaskSuspend|vTaskDelete|malloc\(|advance_generation\(/);
  assert.match(pause, /requeue_if_current\(command\)/);
  assert.match(pause, /release_codec[\s\S]*?s_web_pause_ack = wanted/);
});

test('only static GETs request long pause; errors always release it', () => {
  const first = web.indexOf('static esp_err_t static_handler(');
  const wrapper = web.slice(first, web.indexOf('static esp_err_t register_get(', first));
  assert.match(wrapper, /503 Service Unavailable/);
  assert.match(wrapper, /Retry-After/);
  assert.match(wrapper, /result = serve_static_request\(request\);\s*audio_service_web_pause_end\(\);[\s\S]*?return result;/);
  assert.equal((web.match(/audio_service_web_pause_begin\(/g) || []).length, 1);
  for (const [route, handler] of [['/api/native/status', 'status_handler'], ['/api/native/audio', 'audio_health_handler']]) {
    assert.ok(web.includes(`register_get("${route}", ${handler})`));
  }
  assert.match(web, /YORADIO_ESP8266_WEB_AUDIO_PAUSE != 0[\s\S]*?config.task_priority = tskIDLE_PRIORITY \+ 6;/);
});

test('build switch validates all values and rejects long pause for KaRadio', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-pause-cmake-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const script = path.join(dir, 'test.cmake');
  fs.writeFileSync(script, `include("${path.join(main, 'web_audio_pause.cmake').replaceAll('\\', '/')}" )\nmessage("MODE=\${WEB_AUDIO_PAUSE_MODE}")\n`);
  const bundled = path.join(root, '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const cmake = fs.existsSync(bundled) ? bundled : 'cmake';
  for (const [mode, expected, karadio] of [['off',0,false], ['short',1,false], ['long',2,false],
      ['typo',null,false], ['long',null,true]]) {
    const result = spawnSync(cmake, [`-DYORADIO_ESP8266_WEB_AUDIO_PAUSE=${mode}`,
      `-DYORADIO_ESP8266_KARADIO_PIPELINE=${karadio ? 'ON' : 'OFF'}`, '-P', script],
      {encoding: 'utf8', timeout: 10000});
    if (expected === null) assert.notEqual(result.status, 0);
    else {
      assert.equal(result.status, 0, result.stdout+result.stderr);
      assert.ok((result.stdout+result.stderr).includes(`MODE=${expected}`));
    }
  }
});
