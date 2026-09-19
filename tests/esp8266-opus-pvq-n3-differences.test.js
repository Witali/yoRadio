const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const prefix = require('../tools/esp8266_opus_asm/pvq_prefix_word.cjs');
const m = require('../tools/esp8266_opus_asm/analyze_pvq_n3_differences.cjs');
const table = prefix.read(path.join(prefix.art('candidate'), 'preflight.json')).table;

test('finite-difference model proves every stored N3 interval and the full largest-K index domain', () => {
  const proof = m.verify(table);
  assert.equal(proof.interval_endpoint_cases, 120408);
  assert.equal(proof.dense_index_cases_at_max_k, 61588);
  assert.equal(proof.maximum_search_k, 175);
  assert.equal(proof.maximum_delta, 696);
  assert.equal(proof.maximum_initial_p, 60901);
  const corrupt = structuredClone(table);
  corrupt.rows.find(r => r.n === 3).values[8]++;
  assert.throws(() => m.verify(corrupt));
});

test('first probe, small-K gate and other dimensions retain their exact fallback semantics', () => {
  const row = table.rows.find(r => r.n === 3);
  assert.deepEqual(m.search(row, 12, row.values[9]), {
    k: 12, p: row.values[9], reads: 1, steps: 0, arithmetic: false
  });
  assert.equal(m.search(row, 11, row.values[0], 12).arithmetic, false);
  assert.equal(m.search(row, 12, row.values[0], 12).reads, 1);
  assert.throws(() => m.search(row, 12, row.values[0] - 1));
  const n4 = table.rows.find(r => r.n === 4);
  const result = m.search(n4, 20, n4.values[0]);
  assert.equal(result.arithmetic, false);
  assert.equal(result.reads, 17);
  assert.equal(result.p, n4.values[0]);
});

test('all ten traces reproduce the archived load counts; no CPU claim or bitrate cap', () => {
  const report = m.analyze();
  assert.deepEqual(report, JSON.parse(fs.readFileSync(m.output, 'utf8')));
  assert.equal(report.cases.length, 10);
  assert.ok(report.cases.some(c => /510/.test(c.name)));
  assert.match(report.scope, /physical CPU remain unmeasured/);
  assert.ok(report.cases.every(c => c.variants.every(v => v.new_lookup_table_bytes === 0)));
});
