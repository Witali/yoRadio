const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');

test('PDM32 batch CMake option is OFF by default and rejects non-standard backends', t => {
  const source = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/CMakeLists.txt'), 'utf8');
  const start = source.indexOf('option(YORADIO_ESP8266_PDM32_BATCH');
  const end = source.indexOf('set(YORADIO_AUDIO_LDFRAGMENTS', start);
  assert.ok(start >= 0 && end > start);
  const block = source.slice(start, end);
  assert.match(block, /option\(YORADIO_ESP8266_PDM32_BATCH\s+"[^"]+" OFF\)/);
  assert.match(source, /YORADIO_ESP8266_PDM32_BATCH=\$<BOOL:\$\{YORADIO_ESP8266_PDM32_BATCH\}>/);
  const bundled = path.join(root, '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const command = process.platform === 'win32' && fs.existsSync(bundled) ? bundled : 'cmake';
  const available = spawnSync(command, ['--version'], {encoding:'utf8'});
  if (available.error?.code === 'ENOENT') return t.skip('CMake unavailable');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pdm32-batch-cmake-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const script = path.join(dir, 'profile.cmake');
  fs.writeFileSync(script, 'cmake_minimum_required(VERSION 3.13)\n' + block);
  const run = options => spawnSync(command, [...options, '-P', script], {encoding:'utf8'});
  assert.equal(run([]).status, 0, 'default must allow ordinary non-PDM32 builds');
  for (const enabled of [false,true]) for (const pdm of [false,true]) for (const os32 of [false,true]) {
    const result = run(['-DYORADIO_ESP8266_PDM32_BATCH=' + (enabled ? 'ON':'OFF'),
      '-DCONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=' + (pdm ? 'ON':'OFF'),
      '-DCONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=' + (os32 ? 'ON':'OFF')]);
    assert.equal(result.status === 0, !enabled || (pdm && os32), result.stdout + result.stderr);
    if (result.status) assert.match(result.stderr, /requires standard I2S PDM32 output/);
  }
});
