const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const { execute } = require('../tools/esp8266_audio_profile/run_rcpdm_radio');
const root = path.resolve(__dirname, '..');
const compiler = process.env.YORADIO_ESP8266_XTENSA_GCC || path.join(root,
  '.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin/xtensa-lx106-elf-gcc.exe');

test('LX106 Simple assembly builds with safe architecture gating and forced-C fallback', t => {
  if (!fs.existsSync(compiler)) return t.skip('ESP8266 Xtensa GCC not installed');
  const temporaryRoot = path.resolve(os.tmpdir());
  const directory = fs.mkdtempSync(path.join(temporaryRoot, 'rcpdm-asm-'));
  t.after(() => {
    assert.equal(path.dirname(path.resolve(directory)), temporaryRoot);
    fs.rmSync(directory, { recursive: true, force: true });
  });
  const modes = [
    ['native', 1, '-DYORADIO_ESP8266_NATIVE=1'],
    ['arduino', 1, '-DESP8266=1'],
    ['forced-c', 0, '-DYORADIO_ESP8266_NATIVE=1', '-DRCPDM_SIMPLE_FORCE_C=1'],
    ['other-xtensa', 0, '-DESP32=1'],
    ['disabled-native', 0, '-DYORADIO_ESP8266_NATIVE=0'],
  ];
  for (const [name, expected, ...defines] of modes) for (const optimization of ['-O0', '-Os', '-O3']) {
    const prefix = path.join(directory, name + optimization);
    const args = [optimization, '-std=gnu99', '-mlongcalls', '-Wall', '-Wextra', '-Werror',
      '-I' + path.join(root, 'tests/native'), '-I' + path.join(root, 'esp8266/rtos-sdk-native/main'),
      '-DEXPECT_ASM=' + expected, ...defines, path.join(root, 'tests/native/rcpdm_simple_codegen.c')];
    execute(compiler, [...args, '-S', '-o', prefix + '.s']);
    execute(compiler, [...args, '-c', '-o', prefix + '.o']);
    const assembly = fs.readFileSync(prefix + '.s', 'utf8');
    assert.equal(/#APP/.test(assembly), !!expected, `${name} ${optimization}`);
    assert.doesNotMatch(assembly, /\b(?:rsil|wsr|callx0)\b/,
      'No interrupt masking, special-register writes, or indirect calls');
  }
});
