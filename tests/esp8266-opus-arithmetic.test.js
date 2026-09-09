const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { root, buildHost } = require('../tools/esp8266_opus_profile/build_host.cjs');
const { prepareReference, addOverrideGuard, selection, provenanceName } = require('../tools/esp8266_opus_profile/prepare_generic32_reference.cjs');
const { sha256 } = require('../tools/esp8266_opus_profile/fixtures.cjs');
const { runRegressions } = require('../tools/esp8266_opus_profile/run_regressions.cjs');

test('generic32 reference is only an opt-in architecture guard, with verified file provenance', t => {
  const buildRoot = path.join(root, '.build');
  fs.mkdirSync(buildRoot, { recursive: true });
  const temporary = fs.mkdtempSync(path.join(buildRoot, 'opus-arithmetic-test-'));
  t.after(() => {
    assert.equal(path.dirname(path.resolve(temporary)), path.resolve(buildRoot));
    assert.ok(path.basename(temporary).startsWith('opus-arithmetic-test-'));
    fs.rmSync(temporary, { recursive: true });
  });
  const source = path.join(temporary, 'source'), output = path.join(temporary, 'copy');
  fs.mkdirSync(path.join(source, 'celt'), { recursive: true });
  fs.mkdirSync(path.join(source, 'src'));
  const original = Buffer.from(('/* untouched prefix */\n' + selection + '\n/* untouched suffix */\n').replaceAll('\n', '\r\n'));
  fs.writeFileSync(path.join(source, 'celt/arch.h'), original);
  fs.writeFileSync(path.join(source, 'src/opus_decoder.c'), '/* unchanged decoder */\n');
  const result = prepareReference({ source, output });
  assert.deepEqual(result.changed_files, ['celt/arch.h']);
  assert.equal(result.file_count, 2);
  assert.equal(result.files[0].source_sha256, sha256(original));
  assert.equal(result.files[0].copy_sha256, sha256(addOverrideGuard(original)));
  assert.deepEqual(fs.readFileSync(path.join(source, 'celt/arch.h')), original);
  assert.deepEqual(fs.readFileSync(path.join(output, 'celt/arch.h')), addOverrideGuard(original));
  assert.deepEqual(prepareReference({ source, output }), result, 'Repeated preparation must be idempotent');
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(output, provenanceName), 'utf8')), result);
  assert.throws(() => prepareReference({ source, output: source }), /overlap/);
  assert.throws(() => addOverrideGuard(addOverrideGuard(original)), /already has/);
  fs.appendFileSync(path.join(output, 'src/opus_decoder.c'), 'tamper');
  assert.throws(() => prepareReference({ source, output }), /Existing diagnostic file changed/);
  assert.match(fs.readFileSync(path.join(output, 'src/opus_decoder.c'), 'utf8'), /tamper$/, 'Preparation must not overwrite changed files');
});

test('arithmetic selection rejects invalid and identical comparison branches before building', async () => {
  await assert.rejects(buildHost({ fastInt64: 2 }), /must be 0 or 1/);
  await assert.rejects(runRegressions({ compareFastInt64: 1 }), /explicit 0\/1/);
  await assert.rejects(runRegressions({ fastInt64: 0, compareFastInt64: 0 }), /other branch/);
});

test('saved generic32 evidence is bit-exact to its pristine reference and quantifies host64 rounding', () => {
  const report = JSON.parse(fs.readFileSync(path.join(root, 'tools/esp8266_opus_profile/generic32-results.json'), 'utf8'));
  assert.equal(report.passed, true);
  assert.equal(report.arithmetic.fast_int64, 0);
  assert.equal(report.arithmetic.comparison_fast_int64, 1);
  for (const key of ['baseline_flags', 'bounded_flags', 'pristine_flags'])
    assert.ok(report.arithmetic[key].includes('-DOPUS_FAST_INT64=0'));
  assert.ok(report.arithmetic.comparison_flags.includes('-DOPUS_FAST_INT64=1'));
  assert.deepEqual(report.pristine_provenance.changed_files, ['celt/arch.h']);
  assert.match(report.pristine_provenance.manifest_sha256, /^[a-f0-9]{64}$/);
  assert.deepEqual(report.fixtures.map(item => item.arithmetic_quality.first_12_packets.actual_fnv1a32),
    [0x35905648, 0xbfb8d5fa, 0x8b59452b, 0x5b181a8e, 0xe690bf22]);
  let samples = 0;
  for (const fixture of report.fixtures) {
    samples += fixture.pcm.compared_samples;
    assert.equal(fixture.pcm.exact, true);
    assert.equal(fixture.pristine.pcm_vs_baseline.exact, true);
    assert.equal(fixture.baseline.reset_exact, true);
    assert.equal(fixture.bounded.reset_exact, true);
    assert.equal(fixture.bounded.oom_reinitialized_exact, true);
    assert.equal(fixture.bounded.arena_guards_ok, true);
    const prefix = fixture.arithmetic_quality.first_12_packets.pcm;
    assert.equal(prefix.compared_samples, 11520);
    assert.ok(prefix.max_absolute_error <= 2);
    assert.ok(prefix.snr_db === 'Infinity' || prefix.snr_db > 79);
  }
  assert.equal(samples, 292800);
  const hybrid = report.fixtures.find(item => item.name === 'mono-24').arithmetic_quality.first_12_packets.pcm;
  assert.equal(hybrid.mismatched_samples, 1024);
  assert.equal(hybrid.max_absolute_error, 1);
  assert.equal(report.mixed_sequence.pcm.exact, true);
  assert.equal(report.mixed_sequence.pristine.pcm_vs_baseline.exact, true);
  assert.equal(report.mixed_sequence.bounded.reset_exact, true);
});
