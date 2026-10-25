const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const { spawnSync } = require('node:child_process');
const { root, hash } = require('../tools/esp8266_opus_asm/export.cjs');
const { parseOutput } = require('../tools/esp8266_opus_qemu/run.cjs');
const { summarize } = require('../tools/esp8266_opus_qemu/trace.cjs');

const evidence = path.join(root, 'docs/benchmarks/esp8266-main-integration-20261025');
const dir = path.join(evidence, 'qemu-verified');
const read = name => fs.readFileSync(path.join(dir, name));
const json = name => JSON.parse(read(name));
const summary = json('summary.json');

test('accepted main QEMU evidence preserves exact inventory and input hashes', () => {
  const inventory = json('inventory.json');
  assert.equal(new Set(inventory.map(item => item.name)).size, inventory.length);
  for (const item of inventory) {
    assert.equal(path.basename(item.name), item.name);
    const data = read(item.name);
    assert.equal(data.length, item.bytes, item.name);
    assert.equal(hash(data), item.sha256, item.name);
  }
  for (const fixture of summary.correctness.accepted.fixtures) {
    assert.equal(hash(zlib.gunzipSync(read(fixture.name + '.opuspkt.gz'))), fixture.packet_sha256);
  }
});

test('24 accepted LX106 PCM and OOM cases retain their source and independent anchors', () => {
  const report = json('accepted-extended.json');
  assert.deepEqual(report, summary.correctness.accepted);
  assert.equal(report.passed, true);
  assert.equal(report.cases.length, 24);
  assert.equal(report.oom_recovery_cases, 24);
  assert.equal(report.state_bytes, 6582);
  const proof = JSON.parse(fs.readFileSync(path.join(root,
    'firmware/development/esp8266-opus-ebands-final-candidate-v2/preflight.json')));
  assert.equal(report.elf_sha256, proof.candidate_elf_sha256);
  const provenance = JSON.parse(fs.readFileSync(path.join(evidence, 'provenance.json')));
  for (const [name, digest] of Object.entries(report.recipe_hashes)) {
    const original = spawnSync('git', ['show', provenance.source_commit + ':tools/esp8266_opus_qemu/' + name],
      { cwd: root, encoding: 'utf8' });
    assert.equal(original.status, 0, original.stderr);
    assert.equal(hash(original.stdout.replace(/\r\n/g, '\n')), digest, name);
  }
  const manifest = JSON.parse(fs.readFileSync(path.join(root,
    'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json')));
  for (const anchor of manifest.fixtures) {
    const actual = report.cases.find(item => item.name === anchor.name);
    assert.ok(actual, anchor.name);
    assert.equal(actual.pcm_sha256, anchor.pcm_sha256, anchor.name);
  }
  const selected = report.cases.map(item => ({ ...item, packet_count: item.packets, pcm_bytes: item.samples * 2 }));
  const parsed = parseOutput(zlib.gunzipSync(read('accepted-extended.stdout.log.gz')).toString(), selected);
  assert.equal(parsed.oom_recovery_cases, 24);
  assert.equal(parsed.stack_used_in_harness, report.stack_used_in_harness);
  assert.equal(Math.max(...parsed.cases.map(item => item.byte_peak)), 5968);
  assert.equal(Math.max(...parsed.cases.map(item => item.word_peak)), 15600);
});

test('seven saved PVQ traces reproduce counts including verified empty SILK', () => {
  assert.equal(Object.keys(summary.profiles).length, 7);
  for (const [fixture, profile] of Object.entries(summary.profiles)) {
    const prefix = 'accepted-' + fixture;
    const report = json(prefix + '.json');
    const trace = zlib.gunzipSync(read(prefix + '.trace.log.gz'));
    assert.equal(hash(trace), report.instruction_trace.sha256);
    const parsed = summarize(trace.toString(), { allowEmpty: report.instruction_trace.silk_only });
    assert.deepEqual(parsed, json(prefix + '.trace-summary.json'));
    assert.deepEqual(parsed.totals.pvq, profile.accepted);
  }
  assert.equal(json('accepted-mono-12.json').instruction_trace.silk_only, true);
  assert.equal(summary.profiles['mono-12'].accepted.instructions, 0);
});

test('actual negative canary fails and the accepted 192 kbit trace replays exactly', () => {
  assert.equal(summary.negative_guard, true);
  assert.equal(summary.deterministic_replay, true);
  assert.match(read('negative-canary.runner.log').toString(), /QEMU 20:/);
  const single = json('accepted-stereo-192.json').cases[0];
  const selected = [{ ...single, packet_count: single.packets, pcm_bytes: single.samples * 2 }];
  assert.throws(() => parseOutput(zlib.gunzipSync(read('negative-canary.stdout.log.gz')).toString(), selected));
  assert.deepEqual(json('accepted-replay-stereo-192.json').instruction_trace.totals.pvq,
    summary.profiles['stereo-192'].accepted);
});
