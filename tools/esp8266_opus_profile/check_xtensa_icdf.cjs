const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { root, component } = require('./build_host.cjs');
const { defaultCompiler } = require('./check_xtensa_word_access.cjs');
const { defaultObjdump } = require('./check_xtensa_iram.cjs');
const entropy = path.join(component, 'upstream/celt/entdec.c');
function command(program, args) {
  const result = spawnSync(program, args, { encoding: 'utf8', maxBuffer: 4 * 1024 * 1024 });
  if (result.error) throw result.error;
  assert.equal(result.status, 0, result.stdout + result.stderr);
  return result.stdout;
}
function inspect(object, symbol, objdump) {
  const text = command(objdump, ['-dlr', '-j', '.text.' + symbol, object]);
  let file, line;
  const instructions = [];
  for (const textLine of text.split(/\r?\n/)) {
    const source = textLine.match(/[\\/]([^\\/:]+\.[ch]):(\d+)/);
    if (source) { file = source[1]; line = Number(source[2]); }
    const match = textLine.match(/^[ \t]*([0-9a-f]+):[ \t]+([0-9a-f]+)[ \t]+([a-z][a-z0-9.]*)[ \t]*(.*)$/);
    if (match) instructions.push({ offset: parseInt(match[1], 16), hex: match[2], op: match[3], operands: match[4].trim(), file, line });
  }
  assert.ok(instructions.length, 'Missing function ' + symbol);
  return instructions;
}
function checkIcdf({ compiler = defaultCompiler, objdump = defaultObjdump } = {}) {
  const out = path.join(root, '.build/esp8266-opus-icdf-word/xtensa');
  fs.mkdirSync(out, { recursive: true });
  const source = fs.readFileSync(entropy, 'utf8').split(/\r?\n/);
  const guardLine = source.findIndex(line => line.includes('if((uintptr_t)_icdf>=')) + 1;
  const variants = [[0, 0], [1, 0], [1, 1]].map(([enabled, wordAsm]) => {
    const object = path.join(out, `icdf-${enabled}-asm-${wordAsm}.o`);
    command(compiler, ['-O3', '-std=c99', '-fwrapv', '-fstack-usage', '-g', '-ffunction-sections', '-fdata-sections',
      '-DYORADIO_OPUS_BOUNDED=1', '-DYORADIO_OPUS_ICDF_FLASH_WORD=' + enabled, '-DYORADIO_OPUS_WORD_ASM=' + wordAsm,
      '-I' + component, '-I' + path.join(component, 'upstream/include'), '-I' + path.join(component, 'upstream/celt'),
      '-c', entropy, '-o', object]);
    const instructions = inspect(object, 'ec_dec_icdf', objdump);
    const wordPath = instructions.filter(i => i.file === 'opus_memory.h');
    if (enabled) {
      assert.equal(wordPath.filter(i => /^l32i/.test(i.op)).length, 1, 'Flash loop must load exactly the current aligned word');
      assert.deepEqual(wordPath.filter(i => /^(l8ui|l16ui|l16si|s8i|s16i)$/.test(i.op)), [], 'Flash byte extraction spilled/narrowed');
      assert.equal(wordPath.filter(i => i.op === 'memw').length, wordAsm ? 0 : 1);
      const guards = instructions.filter(i => i.file === 'entdec.c' && i.line === guardLine && /^b/.test(i.op));
      assert.equal(guards.length, 1, 'Expected one range dispatch branch before both loops');
      const branches = instructions.filter(i => /^(b|j)/.test(i.op)).flatMap(i => {
        const target = i.operands.match(/(?:^|,\s*)([0-9a-f]+)\s+</);
        return target && parseInt(target[1], 16) < i.offset ? [{ offset: i.offset, target: parseInt(target[1], 16) }] : [];
      });
      assert.ok(branches.length >= 2);
      assert.ok(branches.every(branch => branch.target > guards[0].offset), 'A decode loop repeats flash classification');
    } else assert.equal(wordPath.length, 0);
    // One original local-CDF byte load and one original packet-byte load.
    assert.equal(instructions.filter(i => i.op === 'l8ui').length, 2);
    const sections = command(objdump, ['-h', object]);
    const mutable = [...sections.matchAll(/^\s*\d+\s+\.(?:bss|data)(?:\.[^ ]+)?\s+([0-9a-f]+)/gm)]
      .reduce((sum, [, size]) => sum + parseInt(size, 16), 0);
    const common = command(objdump, ['-t', object]).match(/^.*\*COM\*.*$/gm) || [];
    assert.equal(mutable, 0); assert.deepEqual(common, []);
    const stackText = fs.readFileSync(object.replace(/\.o$/, '.su'), 'utf8');
    const stack = Number(stackText.match(/:ec_dec_icdf\t(\d+)/)[1]);
    const unchanged = Object.fromEntries(['ec_dec_init', 'ec_dec_icdf16', 'ec_dec_bits'].map(symbol =>
      [symbol, inspect(object, symbol, objdump).map(i => i.hex).join('')]));
    return { enabled, word_asm: wordAsm, icdf_stack_bytes: stack, persistent_bytes: mutable,
      narrow_byte_loads: 2, flash_instructions: wordPath, unchanged };
  });
  for (const variant of variants.slice(1)) assert.deepEqual(variant.unchanged, variants[0].unchanged, 'Unrelated entropy function changed');
  return { passed: true, compiler: command(compiler, ['--version']).split(/\r?\n/)[0],
    scope: 'Isolated entropy object only; no firmware build, physical execution or speed claim.', variants };
}
module.exports = { checkIcdf };
if (require.main === module) {
  try { console.log(JSON.stringify(checkIcdf(), null, 2)); }
  catch (error) { console.error(error.stack); process.exitCode = 1; }
}
