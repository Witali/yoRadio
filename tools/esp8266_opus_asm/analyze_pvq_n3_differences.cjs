// Host-only investigation. No firmware patch, timing claim or extra lookup table.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { root, hash, sourceHash } = require('./export.cjs');
const prefix = require('./pvq_prefix_word.cjs');
const gates = [3, 8, 12, 16];
const output = path.join(root, 'docs/benchmarks/esp8266-opus-pvq-n3-differences-2026-09-19/summary.json');

function search(row, k, index, gate = 3) {
  const value = j => {
    assert.ok(j >= row.n && j < row.n + row.values.length);
    return row.values[j - row.n];
  };
  assert.ok(Number.isInteger(k) && Number.isInteger(index));
  assert.ok(index >= row.values[0] && index <= 0xffffffff);
  let p = value(k), reads = 1, steps = 0;
  const arithmetic = row.n === 3 && k >= gate && index < p;
  if (arithmetic) {
    // U(3,k)-U(3,k-1)=4*(k-1). Maintain the difference, not the row pointer.
    let delta = 4 * (k - 1);
    do {
      assert.ok(k > 3 && p >= delta && delta >= 0);
      p = (p - delta) >>> 0;
      delta -= 4;
      k--;
      steps++;
      assert.equal(p, value(k)); // Proof oracle only; no proposed target load.
      assert.equal(delta, 4 * (k - 1));
    } while (index < p);
  } else {
    while (index < p) { k--; p = value(k); reads++; steps++; }
  }
  return { k, p, reads, steps, arithmetic };
}

function verify(table) {
  const row = table.rows.find(r => r.n === 3);
  assert.equal(row.values.length, 174);
  row.values.forEach((v, i) => {
    const k = i + 3;
    assert.equal(v, 2 * k * k - 2 * k + 1);
    if (i) assert.equal(v - row.values[i - 1], 4 * (k - 1));
  });
  let cases = 0;
  // K+1 must exist for the enclosing sign/codeword logic. Every answer
  // interval is tested at both extremes; no intermediate branch thresholds
  // exist in this monotone recurrence, unlike a bucket lookup.
  for (let k = 3; k < row.n + row.values.length - 1; k++) {
    for (let target = 3; target <= k; target++) {
      for (const index of [row.values[target - 3], row.values[target - 2] - 1]) {
        for (const gate of gates) {
          const r = search(row, k, index, gate);
          assert.equal(r.k, target);
          assert.equal(r.p, row.values[target - 3]);
          assert.equal(r.steps, k - target);
          assert.equal(r.reads, r.arithmetic ? 1 : k - target + 1);
          cases++;
        }
      }
    }
  }
  let denseCases = 0;
  const k = row.n + row.values.length - 2;
  let target = 3;
  for (let index = row.values[0]; index < row.values.at(-1); index++) {
    while (target < k && row.values[target - 2] <= index) target++;
    const r = search(row, k, index);
    assert.equal(r.k, target);
    assert.equal(r.p, row.values[target - 3]);
    denseCases++;
  }
  return {
    interval_endpoint_cases: cases,
    dense_index_cases_at_max_k: denseCases,
    maximum_search_k: k,
    maximum_initial_p: row.values.at(-2),
    maximum_delta: 4 * (k - 1),
    formula: 'U(3,k)=2*k*k-2*k+1; U(3,k)-U(3,k-1)=4*(k-1)',
    scope: 'Exact rank and p model for the stored N=3 row, not linked ASM or full-decoder PCM/CPU validation.'
  };
}

function analyze() {
  const proof = prefix.read(path.join(prefix.art('candidate'), 'preflight.json'));
  const dir = path.join(root, 'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19');
  const saved = prefix.read(path.join(dir, 'summary.json'));
  const result = {
    schema: 1, recipe_sha256_lf: sourceHash(__filename), table_sha256: proof.table.sha256,
    unit: verify(proof.table),
    scope: 'Host rank/read model only. Initial U(K) fast return retained. Only N=3 uses finite differences; other dimensions and guarded small K retain the old search. No bitrate cap, new flash table or per-decoder array. Linked register/stack cost and physical CPU remain unmeasured. Trace counts omit common U(N,N) and sign probes as before.',
    cases: []
  };
  for (const c of saved.cases) {
    const bytes = fs.readFileSync(path.join(dir, c.name + '.jsonl'));
    assert.equal(hash(bytes), c.trace_sha256);
    const rows = bytes.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
    const variants = gates.map(gate => {
      const v = { gate, linear_reads: 0, proposed_reads: 0, removed_loads: 0,
        arithmetic_searches: 0, arithmetic_steps: 0, failed_initial_probes: 0,
        initial_probe_fast_returns: 0, new_lookup_table_bytes: 0 };
      for (const [n, k, target] of rows) {
        const row = proof.table.rows.find(r => r.n === n);
        const lo = row.values[target - n], hi = row.values[target + 1 - n] - 1;
        const a = search(row, k, lo, gate), b = search(row, k, hi, gate);
        assert.deepEqual(a, b); // Exact residual index absent: counts are constant over this interval.
        assert.equal(a.k, target);
        assert.equal(a.p, lo);
        v.linear_reads += k - target + 1;
        v.proposed_reads += a.reads;
        if (k === target) v.initial_probe_fast_returns++;
        else v.failed_initial_probes++;
        if (a.arithmetic) { v.arithmetic_searches++; v.arithmetic_steps += a.steps; }
      }
      v.removed_loads = v.linear_reads - v.proposed_reads;
      assert.equal(v.removed_loads, v.arithmetic_steps);
      assert.equal(v.linear_reads, c.counts.table_probes.linear);
      return v;
    });
    result.cases.push({ name: c.name, trace_sha256: c.trace_sha256, variants });
  }
  return result;
}

module.exports = { search, verify, analyze, output };
if (require.main === module) {
  const result = analyze();
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result.unit));
  console.table(result.cases.flatMap(c => c.variants.map(v => ({ name: c.name, ...v }))));
}
