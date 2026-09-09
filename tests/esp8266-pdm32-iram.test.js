const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { checkBits, checkPlacement, defaultBuild } = require('../tools/esp8266_audio_profile/check_pdm32_iram.cjs');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');
test('PDM32 IRAM is default-off, standard-PDM-only and maps one cold object without shrinking the codec arena', () => {
  const cmake = fs.readFileSync(path.join(main, 'CMakeLists.txt'), 'utf8');
  assert.match(cmake, /option\(YORADIO_ESP8266_PDM32_IRAM\s+"[^"]+" OFF\)/);
  assert.match(cmake, /if\(YORADIO_ESP8266_PDM32_IRAM\)[\s\S]*CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM[\s\S]*CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32/);
  assert.match(cmake, /LDFRAGMENTS \$\{YORADIO_AUDIO_LDFRAGMENTS\}/);
  const fragment = fs.readFileSync(path.join(main, 'pdm32_iram.lf'), 'utf8').replace(/^#.*$/gm, '').trim();
  assert.equal(fragment.replace(/\s+/g, ' '), '[mapping:yoradio_pdm32_cold_modulo] archive: libgcc.a entries: _moddi3 (inflash_text)');
  const arena = fs.readFileSync(path.join(main, '../components/helix_codecs/CodecMemoryArena.cpp'), 'utf8');
  assert.match(arena, /kWordArenaBytes = 16U \* 1024U/);
});
test('Both placements execute actual packer body with identical words and state under UBSan', () => {
  const results = checkBits();
  assert.equal(results.length, 2);
  for (const result of results) assert.equal(result.words, 493216);
});
test('Actual CMake option block registers the fragment only for explicit standard PDM32', () => {
  const cmake = path.join(root, '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const source = fs.readFileSync(path.join(main, 'CMakeLists.txt'), 'utf8');
  const begin = source.indexOf('option(YORADIO_ESP8266_PDM32_IRAM');
  const end = source.indexOf('set(YORADIO_ESP8266_RCPDM_VARIANT', begin);
  assert.ok(begin > 0 && end > begin);
  const out = path.join(root, '.build/esp8266-pdm32-cmake-check');
  fs.mkdirSync(out, { recursive: true });
  for (const [name, enabled, pdm, pdm32, accepted] of [
    ['default', undefined, 1, 1, true], ['off', 'OFF', 0, 0, true],
    ['on', 'ON', 1, 1, true], ['other-output', 'ON', 0, 1, false], ['pdm64', 'ON', 1, 0, false],
  ]) {
    const script = path.join(out, name + '.cmake');
    fs.writeFileSync(script, (enabled === undefined ? '' : `set(YORADIO_ESP8266_PDM32_IRAM ${enabled} CACHE BOOL "")\n`) +
      `set(CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM ${pdm})\nset(CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32 ${pdm32})\n` +
      source.slice(begin, end) + `\nif(NOT YORADIO_AUDIO_LDFRAGMENTS STREQUAL "${enabled === 'ON' ? 'pdm32_iram.lf' : ''}")\nmessage(FATAL_ERROR "Wrong fragment selection")\nendif()\n`);
    const result = spawnSync(cmake, ['-P', script], { encoding: 'utf8' });
    if (result.error) throw result.error;
    assert.equal(result.status === 0, accepted, name + ': ' + result.stdout + result.stderr);
    if (!accepted) assert.match(result.stderr, /requires standard I2S PDM32/);
  }
});
test('SDK-generated linker and minimal target ELF prove targeted placement, cold callers and unchanged RAM/stack', {
  skip: !fs.existsSync(path.join(defaultBuild, 'build.ninja')) && 'Pinned SDK build is unavailable',
}, () => assert.equal(checkPlacement().passed, true));
