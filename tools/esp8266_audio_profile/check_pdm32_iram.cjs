const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { execute, hostPath, root } = require('../esp8266_opus_profile/build_host.cjs');
const { defaultCompiler: compiler } = require('../esp8266_opus_profile/check_xtensa_word_access.cjs');
const objdump = compiler.replace('gcc.exe', 'objdump.exe');
const nm = compiler.replace('gcc.exe', 'nm.exe');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');
const probe = path.join(root, 'tests/native/esp8266_pdm32_iram_probe.c');
const directory = path.join(root, '.build/esp8266-pdm32-iram-check');
const defaultBuild = path.join(root, '.build/esp8266-opus-live-join');
function command(program, args, env = process.env) {
  const result = spawnSync(program, args, { encoding: 'utf8', maxBuffer: 16 * 1024 * 1024, env });
  if (result.error) throw result.error;
  assert.equal(result.status, 0, result.stdout + result.stderr);
  return result.stdout;
}
function extractPacker() {
  const source = fs.readFileSync(path.join(main, 'native_audio_output.c'), 'utf8').replace(/\r\n/g, '\n');
  const begin = source.indexOf('#ifndef YORADIO_ESP8266_PDM32_IRAM');
  const end = source.indexOf('#if YORADIO_ESP8266_OUTPUT_COMPARE', begin);
  assert.ok(begin > 0 && end > begin);
  const text = source.slice(begin, end);
  assert.match(text, /i2s_pdm_pack32/); assert.match(text, /s_pdm_integrator = integrator/);
  fs.mkdirSync(directory, { recursive: true });
  fs.writeFileSync(path.join(directory, 'pdm32_under_test.inc'), text);
}
function checkBits() {
  extractPacker();
  assert.throws(() => execute('gcc', ['-std=c99', '-DYORADIO_ESP8266_PDM32_IRAM=2',
    '-I' + hostPath(directory), '-E', hostPath(probe), '-o', '/dev/null']), /must be 0 or 1/);
  return [0, 1].map(enabled => {
    const binary = path.join(directory, 'host-' + enabled);
    execute('gcc', ['-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined',
      '-DYORADIO_ESP8266_PDM32_IRAM=' + enabled, '-I' + hostPath(directory), hostPath(probe), '-o', hostPath(binary)]);
    const result = JSON.parse(execute(hostPath(binary), []));
    assert.equal(result.passed, true); assert.equal(result.words, 493216);
    return result;
  });
}
function symbols(elf) {
  return Object.fromEntries(command(nm, ['-S', '-n', elf]).trim().split(/\r?\n/).flatMap(line => {
    const m = line.match(/^([0-9a-f]+)(?:\s+[0-9a-f]+)?\s+[a-zA-Z]\s+(\S+)$/);
    return m ? [[m[2], parseInt(m[1], 16)]] : [];
  }));
}
function validateColdCallers(build, sdk) {
  const map = fs.readFileSync(path.join(build, 'yoradio_esp8266_helix_native.map'), 'utf8');
  const match = map.match(/^__moddi3[^\n]*\n((?:[ \t]{10,}[^\n]+\n)*)/m);
  assert.ok(match, 'Missing link cross-reference table for __moddi3');
  const callers = match[1].trim().split(/\r?\n/).map(line => line.trim().replace(/\\/g, '/')).sort();
  assert.equal(callers.length, 2, 'New signed-modulo caller needs a cache-off safety audit');
  assert.ok(callers.some(line => line.endsWith('liblwip.a(sntp.c.obj)')));
  assert.ok(callers.some(line => line.endsWith('libnewlib.a(time.c.obj)')));
  const functions = symbols(path.join(build, 'yoradio_esp8266_helix_native.elf'));
  for (const name of ['sntp_sync_time', 'adjtime'])
    assert.ok(functions[name] >= 0x40200000 && functions[name] < 0x40300000, name + ' must already execute from flash');
  for (const [object, expected, source] of [
    ['esp-idf/lwip/CMakeFiles/__idf_lwip.dir/apps/sntp/sntp.c.obj', 'sntp_sync_time', 'components/lwip/apps/sntp/sntp.c'],
    ['esp-idf/newlib/CMakeFiles/__idf_newlib.dir/src/time.c.obj', 'adjtime', 'components/newlib/src/time.c'],
  ]) {
    const assembly = command(objdump, ['-r', path.join(build, object)]);
    const references = assembly.split('RELOCATION RECORDS FOR ').filter(section => /R_XTENSA_32\s+__moddi3\b/.test(section));
    assert.equal(references.length, 1);
    assert.ok(references[0].startsWith('[.literal.' + expected + ']'));
    assert.doesNotMatch(fs.readFileSync(path.join(sdk, source), 'utf8'), /Cache_Read_Disable|spi_flash_disable|cache_disable/i);
  }
  return { callers, functions: { adjtime: functions.adjtime, sntp_sync_time: functions.sntp_sync_time } };
}
function checkPlacement({ build = defaultBuild } = {}) {
  extractPacker();
  const sdk = JSON.parse(fs.readFileSync(path.join(build, 'config.env'), 'utf8')).IDF_PATH;
  const safety = validateColdCallers(build, sdk);
  const ninja = fs.readFileSync(path.join(build, 'build.ninja'), 'utf8');
  const commandLine = ninja.split(/\r?\n/).find(line => line.includes('COMMAND =') && line.includes('/ldgen.py '));
  assert.ok(commandLine, 'Existing build must provide the authentic SDK ldgen command');
  const fragments = commandLine.match(/--fragments (.*?) --input/)[1].trim().split(/\s+/);
  assert.ok(fragments.every(file => fs.existsSync(file)), 'Whitespace in SDK fragment paths is unsupported');
  const python = process.env.YORADIO_ESP8266_PYTHON || path.join(root, '.build/esp8266-python/Scripts/python.exe');
  const gccLibrary = path.join(sdk, 'components/esp8266/lib/libgcc.a');
  const variants = [0, 1].map(enabled => {
    const out = path.join(directory, 'target-' + enabled); fs.mkdirSync(out, { recursive: true });
    const script = path.join(out, 'esp8266.project.ld');
    command(python, [path.join(sdk, 'tools/ldgen/ldgen.py'), '--config', path.join(build, 'sdkconfig'),
      '--fragments', ...fragments.filter(file => !file.endsWith('pdm32_iram.lf')),
      ...(enabled ? [path.join(main, 'pdm32_iram.lf')] : []),
      '--input', path.join(sdk, 'components/esp8266/ld/esp8266.project.ld.in'), '--output', script,
      '--kconfig', path.join(sdk, 'Kconfig'), '--env-file', path.join(build, 'config.env'),
      '--libraries-file', path.join(build, 'ldgen_libraries'), '--objdump', objdump], { ...process.env, IDF_PATH: sdk });
    const generated = fs.readFileSync(script, 'utf8');
    const rule = '*libgcc.a:_moddi3.*';
    if (enabled) {
      assert.ok(generated.includes(rule), 'ldgen did not emit the object-level mapping');
      const iram = generated.slice(generated.indexOf('.iram0.text :'), generated.indexOf('.iram0.bss :'));
      assert.match(iram, /EXCLUDE_FILE\([^)]*\*libgcc\.a:_moddi3\.\*/);
      assert.match(generated, /\*libgcc\.a:_moddi3\.\*\(\s*\.literal\s+\.literal\.\*\s+\.text\s+\.text\.\*\)/);
    } else assert.ok(!generated.includes(rule));
    const object = path.join(out, 'probe.o'), elf = path.join(out, 'probe.elf'), map = path.join(out, 'probe.map');
    command(compiler, ['-O3', '-std=c99', '-mlongcalls', '-ffunction-sections', '-fdata-sections', '-fstack-usage',
      '-DPDM32_TARGET_PROBE=1', '-DYORADIO_ESP8266_PDM32_IRAM=' + enabled, '-I' + directory,
      '-c', probe, '-o', object]);
    command(compiler, ['-nostdlib', '-Wl,--gc-sections', '-Wl,--cref', '-Wl,--Map=' + map,
      '-T', path.join(build, 'esp-idf/esp8266/esp8266_out.ld'), '-T', script,
      '-T', path.join(sdk, 'components/esp8266/ld/esp8266.rom.ld'), object, gccLibrary, '-o', elf]);
    const syms = symbols(elf);
    const inIram = address => address >= 0x40100000 && address < 0x4010c000;
    assert.equal(inIram(syms.i2s_pdm_pack32), !!enabled);
    assert.equal(inIram(syms.__moddi3), !enabled);
    const disassembly = command(objdump, ['-d', elf]);
    const packer = disassembly.match(/<i2s_pdm_pack32>:\r?\n([\s\S]*?)(?=\r?\n[0-9a-f]+ <|$)/);
    assert.ok(packer);
    const text = packer[1];
    assert.doesNotMatch(text, /\b(?:call0|callx0)\b/, 'Packer must remain self-contained in IRAM');
    const instructions = [...text.matchAll(/^[ \t]*[0-9a-f]+:[ \t]+[0-9a-f]+[ \t]+([a-z][a-z0-9.]*)[ \t]*([^\r\n]*)/gm)]
      .map(([, op, operands]) => op + ' ' + (op === 'l32r' ? operands.split(',')[0] + ',<relocated literal>' : operands.trim()));
    assert.equal(instructions.length, 164, 'Re-audit instruction shape when the packer changes');
    const stack = fs.readFileSync(object.replace(/\.o$/, '.su'), 'utf8').match(/:i2s_pdm_pack32\t(\d+)/)[1];
    return { enabled, packer_address: syms.i2s_pdm_pack32, modulo_address: syms.__moddi3,
      iram_bytes: syms._iram_end - syms._iram_start, dram_bytes: syms._bss_end - syms._data_start,
      stack_bytes: Number(stack), instructions, generated_script: path.relative(root, script), map: path.relative(root, map) };
  });
  assert.deepEqual(variants[0].instructions, variants[1].instructions, 'Placement changed packer instruction sequence');
  assert.equal(variants[0].dram_bytes, variants[1].dram_bytes);
  assert.equal(variants[0].stack_bytes, variants[1].stack_bytes);
  assert.ok(variants[0].iram_bytes - variants[1].iram_bytes >= 480);
  return { passed: true, scope: 'Isolated SDK-generated link of actual packer and unchanged libgcc helper; not a firmware build or physical speed result.',
    safety, variants, iram_saved_bytes: variants[0].iram_bytes - variants[1].iram_bytes };
}
module.exports = { checkBits, checkPlacement, defaultBuild, directory };
if (require.main === module) {
  try { console.log(JSON.stringify({ bits: checkBits(), target: checkPlacement({ build: process.argv[2] ? path.resolve(process.argv[2]) : defaultBuild }) }, null, 2)); }
  catch (error) { console.error(error.stack); process.exitCode = 1; }
}
