const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');
const read = name => fs.readFileSync(path.join(main, name), 'utf8');
const led = read('status_led.c');

test('GPIO2 hardware level LED supports NoDAC and SPI, excludes external-DAC WS', () => {
  assert.match(read('board_config.h'), /BOARD_STATUS_LED_GPIO 2/);
  assert.match(read('board_config.h'), /BOARD_STATUS_LED_ACTIVE_LOW 1/);
  assert.match(read('Kconfig.projbuild'), /config YORADIO_STATUS_LED\s+bool[^]*?default y\s+depends on YORADIO_AUDIO_OUTPUT_SPI_PDM \|\| YORADIO_AUDIO_OUTPUT_I2S_PDM \|\| YORADIO_AUDIO_OUTPUT_I2S_RCPDM/);
  assert.match(read('Kconfig.projbuild'), /config YORADIO_STATUS_LED_UPDATE_HZ[^]*?range 10 20\s+default 20/);
  assert.match(read('app_main.c'), /native_audio_output_init\(\)[^]*?status_led_init\(\)[^]*?network_service_start\(\)/);
  assert.match(read('app_main.c'), /wait = status_led_wait_ticks\(wait\)/);
  assert.doesNotMatch(led, /\b(xTaskCreate|xTimerCreate|malloc|calloc|realloc|pwm_init|native_state_snapshot|vTaskDelay)\s*\(/);
  assert.match(led, /GPIO\.sigma_delta = SIGMA_DELTA_ENABLE/);
  const output = read('native_audio_output.c');
  assert.equal((output.match(/status_led_capture_pcm\(samples, frames \* channels, channels\)/g) || []).length, 2);
  assert.equal((output.match(/status_led_clear\(\)/g) || []).length, 2);
  assert.match(output, /#if CONFIG_YORADIO_STATUS_LED\s+if \(status_led_capture_requested\)\s+status_led_capture_pcm/);
  assert.match(led, /STATUS_LED_CAPTURE_FRAMES 64U/);
});

for (const hz of [10, 20]) for (const activeLow of [0, 1]) {
  test(`real LED C: ${hz} Hz, activeLow=${activeLow}, peaks/decay/GPIO/stop/tick wrap`, t => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-led-'));
    t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
    const fixture = fs.readFileSync(path.join(__dirname, 'native/esp8266_status_led_test.c'), 'utf8');
    const body = led.slice(led.indexOf('#define STATUS_LED_UPDATE_MS'), led.lastIndexOf('#endif'));
    const file = path.join(dir, 'test.c');
    const exe = path.join(dir, process.platform === 'win32' ? 'test.exe' : 'test');
    fs.writeFileSync(file, fixture.replace('/* LED_IMPLEMENTATION */', body));
    const flags = [`CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=${hz}`, `BOARD_STATUS_LED_ACTIVE_LOW=${activeLow}`];
    let build;
    if (process.platform === 'win32') {
      const base = 'C:/Program Files/Microsoft Visual Studio'; let vc;
      if (fs.existsSync(base)) for (const v of fs.readdirSync(base)) for (const e of fs.readdirSync(path.join(base, v))) {
        const p = path.join(base, v, e, 'VC/Auxiliary/Build/vcvars64.bat'); if (fs.existsSync(p)) vc = p;
      }
      assert.ok(vc, 'Visual C++ required for LED behavior test');
      const batch = path.join(dir, 'build.cmd');
      fs.writeFileSync(batch, `@call "${vc}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c11 /W4 /WX ${flags.map(f => '/D' + f).join(' ')} "${file}" /Fe:"${exe}"\r\n`);
      build = spawnSync('cmd.exe', ['/d', '/c', batch], {cwd: dir, encoding: 'utf8', timeout: 60000});
    } else {
      build = spawnSync('cc', ['-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined', ...flags.map(f => '-D' + f), file, '-o', exe], {cwd: dir, encoding: 'utf8', timeout: 60000});
    }
    assert.equal(build.status, 0, build.stdout + '\n' + build.stderr);
    const run = spawnSync(exe, [], {encoding: 'utf8', timeout: 10000});
    assert.equal(run.status, 0, run.stdout + '\n' + run.stderr);
    assert.match(run.stdout, /LED PASS/); t.diagnostic(run.stdout.trim());
  });
}
