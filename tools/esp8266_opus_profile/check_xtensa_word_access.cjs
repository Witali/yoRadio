const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { root, component } = require('./build_host.cjs');
const { defaultObjdump } = require('./check_xtensa_iram.cjs');
const defaultCompiler = defaultObjdump.replace('objdump.exe', 'gcc.exe');
const defaultDirectory = path.join(root, '.build/esp8266-opus-word-access-probe');
const snippet = path.join(root, 'tests/native/esp8266_opus_word_access_test.c');

function command(program, args) {
  const result = spawnSync(program, args, { encoding: 'utf8', maxBuffer: 4 * 1024 * 1024 });
  if (result.error) throw result.error;
  assert.equal(result.status, 0, result.stdout + result.stderr);
  return result.stdout;
}
function inspect(objdump, object, symbol) {
  const text = command(objdump, ['-dr', '-j', '.text.' + symbol, object]);
  const instructions = [...text.matchAll(/^[ \t]*[0-9a-f]+:[ \t]+[0-9a-f]+[ \t]+([a-z][a-z0-9.]*)[ \t]*(.*)$/gm)]
    .map(([, op, operands]) => ({ op, operands: operands.trim() }));
  assert.ok(instructions.length, 'Missing target function ' + symbol);
  return { symbol, memw: instructions.filter(i => i.op === 'memw').length,
    word_loads: instructions.filter(i => /^l32i/.test(i.op)).length,
    word_stores: instructions.filter(i => /^s32i/.test(i.op)).length,
    narrow: instructions.filter(i => /^(l8ui|l16ui|l16si|s8i|s16i)$/.test(i.op)), instructions };
}
function mutableBytes(objdump, object) {
  const text = command(objdump, ['-h', object]);
  const sections = [...text.matchAll(/^\s*\d+\s+(\.(?:bss|data)(?:\.[^ ]+)?)\s+([0-9a-f]+)/gm)]
    .reduce((sum, [, , size]) => sum + parseInt(size, 16), 0);
  // GCC 8 defaults to -fcommon; the first symbol-table column is allocation
  // size for *COM*, while its later size column records alignment.
  const symbols = command(objdump, ['-t', object]);
  const common = [...symbols.matchAll(/^([0-9a-f]+)[^\n]*\*COM\*/gm)]
    .reduce((sum, [, size]) => sum + parseInt(size, 16), 0);
  return sections + common;
}
function stackUsage(file) {
  return Object.fromEntries(fs.readFileSync(file, 'utf8').trim().split(/\r?\n/).map(line => {
    const [location, size] = line.split('\t');
    return [location.slice(location.lastIndexOf(':') + 1), Number(size)];
  }));
}
function checkWordAccess({ compiler = defaultCompiler, objdump = defaultObjdump, directory = defaultDirectory } = {}) {
  const variants = [0, 1].map(enabled => {
    const out = path.join(directory, 'asm-' + enabled);
    fs.mkdirSync(out, { recursive: true });
    const flags = ['-O3', '-std=c99', '-fwrapv', '-fstack-usage', '-ffunction-sections', '-fdata-sections',
      '-Wall', '-Wextra', '-Werror', '-DYORADIO_OPUS_BOUNDED=1', '-DYORADIO_OPUS_WORD_ASM=' + enabled,
      '-DOPUS_WORD_TARGET_SNIPPET=1', '-I' + component, '-I' + path.join(component, 'upstream/include')];
    const objects = {};
    for (const [name, source] of [['memory', path.join(component, 'opus_memory.c')], ['snippet', snippet]]) {
      const object = path.join(out, name + '.o');
      command(compiler, [...flags, '-c', source, '-o', object]);
      objects[name] = object;
    }
    const functions = ['opus_word_load_low', 'opus_word_load_high', 'opus_word_table_first', 'opus_word_table_second',
      'opus_word_write_read', 'opus_word_alias_order'].map(symbol => inspect(objdump, objects.snippet, symbol));
    functions.push(...['yoradio_opus_copy', 'yoradio_opus_clear'].map(symbol => inspect(objdump, objects.memory, symbol)));
    for (const fn of functions) {
      assert.deepEqual(fn.narrow, [], 'A word helper narrowed its access: ' + fn.symbol);
      assert.ok(enabled ? fn.memw === 0 : fn.memw > 0, `${fn.symbol}: wrong fence selection for macro=${enabled}`);
    }
    for (const fn of functions.slice(0, 6)) assert.ok(fn.word_loads > 0);
    const ordered = functions.find(fn => fn.symbol === 'opus_word_alias_order');
    assert.deepEqual(ordered.instructions.filter(i => /^(?:l|s)32i/.test(i.op)).map(i => i.op[0]), ['s', 'l', 's', 'l'],
      'Compiler memory clobbers lost ordinary-store / asm-load / asm-store / ordinary-load ordering');
    return { enabled, flags, functions, mutable_bytes: mutableBytes(objdump, objects.memory),
      stack: { ...stackUsage(path.join(out, 'memory.su')), ...stackUsage(path.join(out, 'snippet.su')) } };
  });
  assert.equal(variants[1].mutable_bytes, variants[0].mutable_bytes, 'A/B increased static RAM');
  for (const [symbol, size] of Object.entries(variants[1].stack))
    assert.ok(size <= variants[0].stack[symbol], symbol + ' A/B increased target stack frame');
  return { passed: true, compiler: command(compiler, ['--version']).split(/\r?\n/)[0],
    scope: 'Two isolated source objects, not a firmware build or target execution. Exact full-width instructions and compiler alias ordering; physical PCM/timing still requires board A/B.', variants };
}
module.exports = { checkWordAccess, defaultCompiler, defaultDirectory, snippet };
if (require.main === module) {
  try { console.log(JSON.stringify(checkWordAccess(), null, 2)); }
  catch (error) { console.error(error.stack); process.exitCode = 1; }
}
