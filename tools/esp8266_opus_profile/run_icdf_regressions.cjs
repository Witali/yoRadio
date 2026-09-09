const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { buildHost, execute, hostPath, root, component } = require('./build_host.cjs');
const { runPhaseRegressions } = require('./run_phase_regressions.cjs');
const { comparePcm } = require('./run_regressions.cjs');
const { sha256 } = require('./fixtures.cjs');
const directory = path.join(root, '.build/esp8266-opus-icdf-word');
const entropy = path.join(component, 'upstream/celt/entdec.c');
const probe = path.join(root, 'tests/native/esp8266_opus_icdf_flash_probe.c');
const ecFunctions = ['ec_dec_init', 'ec_decode', 'ec_decode_bin', 'ec_dec_update', 'ec_dec_bit_logp',
  'ec_dec_icdf', 'ec_dec_icdf16', 'ec_dec_uint', 'ec_dec_bits'];

function compile(flags, source, output) {
  execute('gcc', [...flags, '-c', hostPath(source), '-o', hostPath(output)]);
}
async function buildIcdfProbe({ sanitize = false, unit = false } = {}) {
  const build = await buildHost({ bounded: true, fastInt64: 0 });
  const out = path.join(directory, (unit ? 'unit' : 'pcm') + (sanitize ? '-asan' : ''));
  fs.mkdirSync(out, { recursive: true });
  const sanitizers = sanitize ? ['-O1', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] : [];
  const flags = [...build.flags, '-Wall', '-Wextra', '-Werror', ...sanitizers];
  const on = path.join(out, 'entdec-word.o'), main = path.join(out, 'icdf-probe.o');
  compile([...flags, '-DYORADIO_OPUS_ICDF_FLASH_WORD=1', '-DYORADIO_OPUS_ICDF_TEST_HOOKS=1'], entropy, on);
  compile([...flags, '-DYORADIO_OPUS_ICDF_FLASH_WORD=1', '-DYORADIO_OPUS_ICDF_TEST_HOOKS=1',
    ...(unit ? ['-DOPUS_ICDF_UNIT=1'] : [])], probe, main);
  const objects = build.objects.filter(file => !file.endsWith('probe.c.o') && !file.endsWith('entdec.c.o'));
  objects.push(on, main);
  if (unit) {
    const legacy = path.join(out, 'entdec-legacy.o');
    compile([...flags, '-DYORADIO_OPUS_ICDF_FLASH_WORD=0', ...ecFunctions.map(name => '-D' + name + '=legacy_' + name)], entropy, legacy);
    objects.push(legacy);
  } else {
    const phase = path.join(out, 'phase-probe.o');
    compile(flags, path.join(__dirname, 'phase_probe.c'), phase);
    objects.push(phase);
  }
  const binary = path.join(out, 'probe');
  execute('gcc', [...objects.map(hostPath), ...sanitizers, '-no-pie', '-Wl,--gc-sections',
    ...(!unit ? ['-Wl,--wrap=ec_dec_icdf', '-Wl,--wrap=quant_all_bands', '-Wl,--wrap=yoradio_opus_scratch_alloc'] : []),
    '-ldl', '-lm', '-o', hostPath(binary)]);
  return { binary, compiler: build.compiler };
}
async function runIcdfRegressions({ output = path.join(__dirname, 'icdf-word-results.json') } = {}) {
  const phase = await runPhaseRegressions();
  const unit = await buildIcdfProbe({ unit: true });
  const unitResult = JSON.parse(execute(hostPath(unit.binary), []));
  const sanitized = await buildIcdfProbe({ unit: true, sanitize: true });
  const sanitizerResult = JSON.parse(execute('env', ['ASAN_OPTIONS=detect_leaks=0', hostPath(sanitized.binary)]));
  assert.equal(unitResult.passed, true);
  assert.equal(sanitizerResult.passed, true);
  const build = await buildIcdfProbe();
  const cases = phase.cases.map(test => {
    const pcmFile = path.join(directory, test.name + '.word.pcm');
    const lines = execute('env', ['OPUS_PHASE_CAPACITY=6144', 'OPUS_PHASE_RATE=' + test.bounded.sample_rate,
      'OPUS_PHASE_PLC_BURST=' + (test.plc_burst || 1), hostPath(build.binary), hostPath(pcmFile),
      ...(test.plc_burst ? ['--plc'] : []), ...test.route.map(file => hostPath(path.resolve(root, file)))])
      .trim().split(/\r?\n/).map(line => JSON.parse(line));
    assert.equal(lines.length, 2, 'Missing real word-path coverage output');
    const [bounded, coverage] = lines;
    assert.ok(coverage.icdf_word_loads > 0 && coverage.icdf_flash_calls > 0, 'Word branch did not run: ' + test.name);
    assert.equal(coverage.icdf_flash_calls, coverage.readonly_tables_transferred);
    assert.equal(bounded.scratch_byte_peak_bytes, test.bounded.scratch_byte_peak_bytes);
    assert.equal(bounded.scratch_word_peak_bytes, test.bounded.scratch_word_peak_bytes);
    assert.equal(bounded.reset_exact, true);
    assert.equal(bounded.pcm_guards_ok, true);
    const pristine = fs.readFileSync(path.join(root, '.build/esp8266-opus-phase-regression', test.name + '.pristine.pcm'));
    const pcm = comparePcm(pristine, fs.readFileSync(pcmFile));
    assert.equal(pcm.exact, true, test.name + ' changed PCM');
    process.stderr.write(`${test.name}: exact; real flash CDF calls=${coverage.icdf_flash_calls}, DRAM CDF calls=${coverage.icdf_dram_calls}, word loads=${coverage.icdf_word_loads}\n`);
    return { name: test.name, input_sha256: test.input_sha256, bounded, coverage, pcm };
  });
  assert.ok(cases.some(test => test.coverage.icdf_dram_calls > 0));
  const sources = ['opus_memory.h', 'upstream/celt/entdec.c', 'CMakeLists.txt'];
  const report = { schema_version: 1, passed: true, compiler: build.compiler,
    scope: 'Actual flash-word branch on host, mapped 0x40200000..0x40300000 with guard pages. Only constant readonly CDFs copied there by a test-only linker wrapper; local CDF and packet reads remain unmodified. No target speed claim.',
    arithmetic: 'OPUS_FAST_INT64=0', pristine_provenance: phase.pristine_provenance,
    source_sha256_lf: Object.fromEntries(sources.map(name => [name,
      sha256(Buffer.from(fs.readFileSync(path.join(component, name), 'utf8').replace(/\r\n/g, '\n')))])),
    unit: unitResult, address_undefined_sanitizers: sanitizerResult, legacy_phase_passed: phase.passed, cases };
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  return report;
}
module.exports = { buildIcdfProbe, runIcdfRegressions, directory, entropy };
if (require.main === module) runIcdfRegressions().then(result => console.log(JSON.stringify({ passed: result.passed, cases: result.cases.length, unit: result.unit })))
  .catch(error => { console.error(error.stack); process.exitCode = 1; });
