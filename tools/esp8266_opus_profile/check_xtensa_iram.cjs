const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { root } = require('./build_host.cjs');

const defaultObject = path.resolve(root, process.env.OPUS_TARGET_BUILD || '.build/esp8266-opus-experimental',
  'esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/upstream/celt/pitch.c.obj');
const defaultObjdump = path.join(root, '.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin/xtensa-lx106-elf-objdump.exe');

function checkPitchInterpolation({ object = defaultObject, objdump = defaultObjdump } = {}) {
  const source = path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/pitch.c');
  const lines = fs.readFileSync(source, 'utf8').split(/\r?\n/);
  const firstLine = lines.findIndex(line => line.includes('/* Refine by pseudo-interpolation */')) + 1;
  const lastLine = lines.findIndex((line, i) => i >= firstLine && line.includes('*pitch =')) + 1;
  assert.ok(firstLine && lastLine > firstLine, 'Could not identify pitch interpolation source range');
  assert.ok(fs.statSync(object).mtimeMs >= fs.statSync(source).mtimeMs, 'Target pitch object is stale; rebuild the Opus component first');
  const result = spawnSync(objdump, ['-dlr', '-j', '.text.pitch_search', object], { encoding: 'utf8', maxBuffer: 2 * 1024 * 1024 });
  if (result.error) throw result.error;
  assert.equal(result.status, 0, result.stderr);
  let inInterpolation = false;
  const accesses = [];
  for (const line of result.stdout.split(/\r?\n/)) {
    const location = line.match(/[/\\]pitch\.c:(\d+)/);
    if (location) {
      const sourceLine = Number(location[1]);
      inInterpolation = sourceLine >= firstLine && sourceLine < lastLine;
    }
    const instruction = line.match(/^\s*([0-9a-f]+):\s+[0-9a-f]+\s+(l32i(?:\.n)?|l8ui|l16ui|l16si|s8i|s16i)\s+(.+)$/);
    if (inInterpolation && instruction) accesses.push({ offset: '0x' + instruction[1], instruction: instruction[2], operands: instruction[3] });
  }
  assert.ok(accesses.filter(access => /^l32i/.test(access.instruction)).length >= 3,
    'Missing debug mapping or the three correlation reads in target interpolation code');
  const narrow = accesses.filter(access => !/^l32i/.test(access.instruction));
  assert.deepEqual(narrow, [], 'Pitch interpolation must not use narrow accesses to its IRAM correlation array');
  return { passed: true, function: 'pitch_search', object: path.relative(root, object).replace(/\\/g, '/'),
    checked_source_lines: [firstLine, lastLine - 1], accesses };
}
function checkWordOnlyZeroFills({ objectDirectory = path.dirname(defaultObject), objdump = defaultObjdump } = {}) {
  return [['bands', 'denormalise_bands'], ['celt_decoder', 'celt_decode_with_ec_dred']].map(([file, functionName]) => {
    const object = path.join(objectDirectory, file + '.c.obj');
    const source = path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt', file + '.c');
    assert.ok(fs.statSync(object).mtimeMs >= fs.statSync(source).mtimeMs, `${file} object is stale; rebuild the Opus component first`);
    const result = spawnSync(objdump, ['-dr', '-j', '.text.' + functionName, object], { encoding: 'utf8', maxBuffer: 2 * 1024 * 1024 });
    if (result.error) throw result.error;
    assert.equal(result.status, 0, result.stderr);
    // In these two functions every zero-filled vector is celt_sig/IRAM.
    // Other CELT functions legitimately zero 16-bit DRAM buffers with libc.
    assert.match(result.stdout, /R_XTENSA_ASM_EXPAND\s+yoradio_opus_clear\b/, `${functionName} must call the word-safe clear helper`);
    assert.doesNotMatch(result.stdout, /R_XTENSA_(?:ASM_EXPAND|SLOT0_OP)\s+(?:memset|memcpy|memmove)\b/,
      `${functionName} must not dispatch its IRAM zero-fill to byte-oriented libc`);
    return { passed: true, function: functionName, object: path.relative(root, object).replace(/\\/g, '/'), raw_libc_calls: 0 };
  });
}
module.exports = { checkPitchInterpolation, checkWordOnlyZeroFills, defaultObject, defaultObjdump };
if (require.main === module) {
  const value = key => { const i = process.argv.indexOf(key); return i < 0 ? undefined : process.argv[i + 1]; };
  try {
    const object = value('--object'), objdump = value('--objdump');
    console.log(JSON.stringify({ pitch: checkPitchInterpolation({ object, objdump }),
      zero_fills: checkWordOnlyZeroFills({ objectDirectory: object ? path.dirname(object) : undefined, objdump }) }, null, 2));
  }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
