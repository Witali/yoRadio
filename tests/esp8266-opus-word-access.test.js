const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execute, hostPath, component, root } = require('../tools/esp8266_opus_profile/build_host.cjs');
const { checkWordAccess, defaultCompiler, snippet } = require('../tools/esp8266_opus_profile/check_xtensa_word_access.cjs');

test('Opus private word access switch defaults off and rejects invalid selections', () => {
  const flags = ['-E', '-dM', '-x', 'c', '-include', hostPath(path.join(component, 'opus_memory.h')), '/dev/null'];
  assert.match(execute('gcc', flags), /^#define YORADIO_OPUS_WORD_ASM 0$/m);
  assert.throws(() => execute('gcc', ['-DYORADIO_OPUS_WORD_ASM=2', ...flags]), /must be 0 or 1/);
});

test('Opus word-helper C fallbacks preserve overlap, signed halves and alias ordering in both A/B modes', () => {
  const directory = path.join(root, '.build/esp8266-opus-word-access-host');
  fs.mkdirSync(directory, { recursive: true });
  for (const enabled of [0, 1]) {
    const binary = path.join(directory, 'test-' + enabled);
    execute('gcc', ['-O3', '-std=c99', '-fwrapv', '-Wall', '-Wextra', '-Werror', '-ffunction-sections', '-fdata-sections',
      '-DYORADIO_OPUS_WORD_ASM=' + enabled, '-I' + hostPath(component), '-I' + hostPath(path.join(component, 'upstream/include')),
      hostPath(snippet), hostPath(path.join(component, 'opus_memory.c')), '-Wl,--gc-sections', '-o', hostPath(binary)]);
    assert.match(execute(hostPath(binary), []), new RegExp(`Opus private word helpers PASS: macro=${enabled}`));
  }
});

test('actual LX106 A/B snippets preserve word width and ordering without MEMW or additional static/stack RAM', {
  skip: !fs.existsSync(defaultCompiler) && 'Install the pinned Xtensa toolchain to cross-compile these two isolated objects.',
}, () => {
  assert.equal(checkWordAccess().passed, true);
});
