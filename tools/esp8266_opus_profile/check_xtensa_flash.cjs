const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const defaultObjects = path.join(root, '.build/esp8266-opus-board-bench/esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/upstream/celt');
const defaultObjdump = path.join(root, '.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin/xtensa-lx106-elf-objdump.exe');

function inspect(object, symbol, objdump) {
  const result = spawnSync(objdump, ['-dr', '-j', '.text.' + symbol, object],
    {encoding: 'utf8', maxBuffer: 2 * 1024 * 1024});
  if (result.error) throw result.error;
  assert.equal(result.status, 0, result.stderr);
  const loads = [...result.stdout.matchAll(/^\s*([0-9a-f]+):\s+[0-9a-f]+\s+(l32i(?:\.n)?|l16si|l16ui|l8ui)\s+(.+)$/gm)]
    .map(([, offset, opcode, operands]) => ({offset: '0x' + offset, opcode, operands: operands.trim()}));
  const narrow = loads.filter(load => !load.opcode.startsWith('l32i'));
  return {object: path.relative(root, object).replaceAll('\\', '/'), symbol,
    word_load_instructions: loads.length - narrow.length,
    narrow_load_instructions: narrow.length, narrow_loads: narrow};
}

function checkFlashTables({objects = defaultObjects, baseline, objdump = defaultObjdump} = {}) {
  return [['mdct', 'clt_mdct_backward_c'], ['kiss_fft', 'opus_fft_impl']].map(([file, symbol]) => {
    const object = path.join(objects, file + '.c.obj');
    const source = path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt', file + '.c');
    const header = path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder/opus_memory.h');
    assert.ok(fs.statSync(object).mtimeMs >= Math.max(fs.statSync(source).mtimeMs, fs.statSync(header).mtimeMs),
      `${file} target object is stale; rebuild it before checking flash loads`);
    const after = inspect(object, symbol, objdump);
    assert.ok(after.word_load_instructions > 0, 'Function disassembly is missing');
    assert.equal(after.narrow_load_instructions, 0,
      `${symbol} reintroduced narrow loads; distinguish flash from any new DRAM locals before changing this guard`);
    return {passed: true, ...(baseline ? {before: inspect(path.join(baseline, file + '.c.obj'), symbol, objdump)} : {}), after};
  });
}

module.exports = {checkFlashTables};
if (require.main === module) {
  const value = key => { const i = process.argv.indexOf(key); return i < 0 ? undefined : process.argv[i + 1]; };
  try {
    const result = {scope: 'Static instruction counts in decoder MDCT/FFT, not runtime load counts or CPU measurements.',
      functions: checkFlashTables({objects: value('--objects'), baseline: value('--baseline'), objdump: value('--objdump')})};
    const json = JSON.stringify(result, null, 2) + '\n';
    if (value('--output')) fs.writeFileSync(value('--output'), json);
    process.stdout.write(json);
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
