const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execute, hostPath, component, root } = require('../tools/esp8266_opus_profile/build_host.cjs');
const { sha256 } = require('../tools/esp8266_opus_profile/fixtures.cjs');
const { buildIcdfProbe, runIcdfRegressions } = require('../tools/esp8266_opus_profile/run_icdf_regressions.cjs');
const { checkIcdf } = require('../tools/esp8266_opus_profile/check_xtensa_icdf.cjs');
const { defaultCompiler } = require('../tools/esp8266_opus_profile/check_xtensa_word_access.cjs');

test('ICDF word A/B defaults off and rejects invalid macro values', () => {
  const flags = ['-E', '-dM', '-x', 'c', '-include', hostPath(path.join(component, 'opus_memory.h')), '/dev/null'];
  assert.match(execute('gcc', flags), /^#define YORADIO_OPUS_ICDF_FLASH_WORD 0$/m);
  assert.throws(() => execute('gcc', ['-DYORADIO_OPUS_ICDF_FLASH_WORD=2', ...flags]), /must be 0 or 1/);
});

test('actual word branch matches legacy entropy state and preserves two-byte DRAM tables under ASan/UBSan', { timeout: 180000 }, async () => {
  const build = await buildIcdfProbe({ unit: true, sanitize: true });
  const result = JSON.parse(execute('env', ['ASAN_OPTIONS=detect_leaks=0', hostPath(build.binary)]));
  assert.equal(result.passed, true);
  assert.equal(result.sequences, 269);
  assert.equal(result.symbols, 137728);
  assert.equal(result.icdf_dram_calls, 2048);
  assert.ok(result.icdf_word_loads > result.icdf_flash_calls && result.icdf_flash_calls > 0);
});

test('Xtensa ICDF range dispatch is outside both loops and only flash reads become word loads', {
  skip: !fs.existsSync(defaultCompiler) && 'Pinned Xtensa compiler unavailable.',
}, () => assert.equal(checkIcdf().passed, true));

test('saved ICDF word evidence exercised real flash reads and exactly matched pristine PCM', () => {
  const report = JSON.parse(fs.readFileSync(path.join(root, 'tools/esp8266_opus_profile/icdf-word-results.json'), 'utf8'));
  assert.equal(report.passed, true);
  assert.equal(report.legacy_phase_passed, true);
  assert.equal(report.arithmetic, 'OPUS_FAST_INT64=0');
  for (const [name, expected] of Object.entries(report.source_sha256_lf))
    assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component, name), 'utf8').replace(/\r\n/g, '\n'))), expected);
  assert.equal(report.cases.length, 22);
  assert.equal(report.unit.symbols, 137728);
  assert.deepEqual(report.unit, report.address_undefined_sanitizers);
  for (const result of report.cases) {
    assert.equal(result.pcm.exact, true, result.name);
    assert.equal(result.pcm.max_absolute_error, 0);
    assert.equal(result.pcm.mismatched_samples, 0);
    assert.equal(result.pcm.snr_db, 'Infinity');
    assert.ok(result.coverage.icdf_word_loads > 0);
    assert.equal(result.coverage.icdf_flash_calls, result.coverage.readonly_tables_transferred);
    assert.equal(result.bounded.pcm_guards_ok, true);
    assert.equal(result.bounded.reset_exact, true);
    assert.ok(result.bounded.scratch_byte_peak_bytes <= 6144);
    assert.ok(result.bounded.scratch_word_peak_bytes <= 16384);
  }
  assert.ok(report.cases.find(result => result.name === 'standard-clean-mono-12').coverage.icdf_dram_calls > 0);
  assert.ok(report.cases.find(result => result.name === 'standard-clean-mono-24').coverage.icdf_dram_calls > 0);
});

test('full real-word-branch Opus PCM corpus can be reproduced', {
  skip: process.env.OPUS_ICDF_TEST !== '1' && 'Set OPUS_ICDF_TEST=1 for all host PCM comparisons.', timeout: 300000,
}, async () => assert.equal((await runIcdfRegressions()).passed, true));
