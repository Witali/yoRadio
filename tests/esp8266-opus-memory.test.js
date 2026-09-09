const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { fixtureDirectory, sha256, inspectPackets } = require('../tools/esp8266_opus_profile/fixtures.cjs');
const { runRegressions } = require('../tools/esp8266_opus_profile/run_regressions.cjs');
const { checkPitchInterpolation, checkWordOnlyZeroFills, defaultObject, defaultObjdump } = require('../tools/esp8266_opus_profile/check_xtensa_iram.cjs');

test('Xtensa pitch interpolation keeps IRAM correlation loads at 32 bits', {
  skip: (!fs.existsSync(defaultObject) || !fs.existsSync(defaultObjdump)) && 'Build the ESP8266 Opus component to inspect target instructions.',
}, () => {
  assert.equal(checkPitchInterpolation().passed, true);
});

test('Xtensa CELT IRAM zero fills cannot become raw libc memset', {
  skip: (!fs.existsSync(defaultObject) || !fs.existsSync(defaultObjdump)) && 'Build the ESP8266 Opus component to inspect target instructions.',
}, () => {
  assert.equal(checkWordOnlyZeroFills().every(result => result.passed), true);
});

test('Opus corpus pins CBR 12..510 kbps packets and covers SILK, hybrid and CELT', () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(fixtureDirectory, 'manifest.json'), 'utf8'));
  const modes = new Set();
  assert.deepEqual(manifest.fixtures.map(fixture => fixture.bitrate_kbps), [12, 24, 64, 128, 510]);
  for (const fixture of manifest.fixtures) {
    const packets = fs.readFileSync(path.join(fixtureDirectory, fixture.name + '.opuspkt'));
    const observed = inspectPackets(packets);
    assert.equal(sha256(packets), fixture.opuspkt_sha256);
    assert.equal(sha256(fs.readFileSync(path.join(fixtureDirectory, fixture.name + '.opus'))), fixture.ogg_sha256);
    for (const key of Object.keys(observed)) assert.deepEqual(observed[key], fixture[key], `${fixture.name}: ${key}`);
    assert.deepEqual(observed.packet_durations_ms, { 20: 61 });
    for (const [mode, count] of Object.entries(observed.modes)) if (count) modes.add(mode);
  }
  assert.deepEqual([...modes].sort(), ['CELT', 'SILK', 'hybrid']);
});

test('saved Opus host evidence has exact pristine/baseline/bounded PCM and bounded arena usage', () => {
  const report = JSON.parse(fs.readFileSync(path.join(__dirname, '../tools/esp8266_opus_profile/results.json'), 'utf8'));
  const manifest = JSON.parse(fs.readFileSync(path.join(fixtureDirectory, 'manifest.json'), 'utf8'));
  assert.equal(report.passed, true);
  assert.equal(report.fixtures.length, manifest.fixtures.length);
  for (const fixture of manifest.fixtures) {
    const result = report.fixtures.find(item => item.name === fixture.name);
    assert.ok(result, fixture.name);
    assert.equal(result.opuspkt_sha256, fixture.opuspkt_sha256);
    assert.equal(result.pcm.exact, true);
    assert.equal(result.pcm.compared_samples, fixture.samples);
    assert.equal(result.pcm.snr_db, 'Infinity');
    assert.equal(result.pcm.mismatched_samples, 0);
    assert.equal(result.pcm.max_absolute_error, 0);
    assert.equal(result.pcm.reference_pcm_sha256, result.pcm.actual_pcm_sha256);
    assert.equal(result.pristine.pcm_vs_baseline.exact, true);
    assert.equal(result.pristine.pcm_vs_baseline.reference_pcm_sha256, result.pcm.actual_pcm_sha256);
    assert.equal(result.baseline.reset_exact, true);
    assert.equal(result.bounded.reset_exact, true);
    assert.equal(result.bounded.oom_reinitialized_exact, true);
    assert.equal(result.bounded.arena_guards_ok, true);
    assert.equal(result.bounded.scratch_byte_capacity_bytes, 7680);
    assert.equal(result.bounded.scratch_word_capacity_bytes, 16384);
    assert.ok(result.bounded.scratch_byte_peak_bytes <= 7680);
    assert.ok(result.bounded.scratch_word_peak_bytes <= 16384);
  }
  const mixed = report.mixed_sequence;
  assert.ok(mixed, 'mixed SILK mono/stereo + mode transition + PLC evidence is missing');
  assert.equal(mixed.bounded.sequence_packets, 286);
  assert.equal(mixed.bounded.plc_frames, 35);
  assert.equal(mixed.bounded.samples, 308160);
  assert.equal(mixed.bounded.reset_exact, true);
  assert.equal(mixed.baseline.reset_exact, true);
  assert.equal(mixed.bounded.persistent_bytes, 11232);
  assert.equal(mixed.bounded.scratch_byte_capacity_bytes, 7680);
  assert.ok(mixed.bounded.scratch_byte_peak_bytes <= 7680);
  assert.ok(mixed.bounded.scratch_word_peak_bytes <= 16384);
  assert.equal(mixed.pcm.exact, true);
  assert.equal(mixed.pcm.mismatched_samples, 0);
  assert.equal(mixed.pristine.pcm_vs_baseline.exact, true);
});

test('real host decoders reproduce all Opus fixtures, reset and OOM recovery', {
  skip: process.env.OPUS_HOST_TEST !== '1' && 'Set OPUS_HOST_TEST=1 to run GCC (WSL on Windows).',
  timeout: 300000,
}, async () => {
  const report = await runRegressions({ noBuild: process.env.OPUS_HOST_NO_BUILD === '1', upstreamRoot: process.env.OPUS_HOST_UPSTREAM });
  assert.equal(report.passed, true);
});
