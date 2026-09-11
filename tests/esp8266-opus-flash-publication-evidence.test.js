const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {summarize} = require('../tools/esp8266_opus_profile/compare_output_series.cjs');
const directory = path.resolve(__dirname, '../firmware/development/esp8266-opus-flash-publish-off');
const read = name => JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8').replace(/^\uFEFF/, ''));

test('saved flash-output control retains all ten attempts, exact PCM and failed continuity/RAM gates', () => {
  const manifest = read('manifest.json');
  assert.equal(manifest.opus_pcm_publish, false);
  assert.equal(manifest.opus_benchmark_output, true);
  const reports = Array.from({length:10}, (_,i) => read(`attempt${i+1}.json`));
  for (const [i,r] of reports.entries()) {
    assert.equal(r.interval_ms, 30000);
    assert.equal(r.fixtures.header_sha256, manifest.opus_benchmark_header_sha256.toLowerCase());
    assert.deepEqual(r.fixtures.fixtures.map(f => f.expected_hash),
      [898651720, 3216561658, 2337883435, 1528306318, 1717014079]);
    assert.equal(r.final.rounds, 100);
    assert.ok(fs.statSync(path.join(directory, `attempt${i+1}.log`)).size > 0);
  }
  // summarize/classify independently recheck each measured hash/count/gate.
  const result = summarize(reports);
  assert.equal(result.completed, 10);
  assert.equal(result.all_observed_gates_pass, false);
  assert.deepEqual(result.cases.map(c => c.continuous), [9,0,0,0,0]);
  assert.deepEqual(result.cases.map(c => c.min_dram.min), [7152,3244,1732,364,500]);
  assert.deepEqual(result.cases.map(c => c.dma_misses.median), [0,40,49,168.5,1023.5]);
  assert.deepEqual(result.observation_errors.map(e => e.attempt), [1,8]);
  assert.equal(reports[0].before.data.min_heap, 23708);
  assert.equal(result.global_min_heap.min, 192);
  assert.ok(reports.every(r => r.after.data.min_heap === 192));
});
