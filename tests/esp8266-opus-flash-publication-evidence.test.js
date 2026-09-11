const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {summarize} = require('../tools/esp8266_opus_profile/compare_output_series.cjs');
const directory = path.resolve(__dirname, '../firmware/development/esp8266-opus-flash-publish-off');
const read = name => JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8').replace(/^\uFEFF/, ''));

test('saved flash publication A/B reproduces all twenty attempts and keeps the candidate unqualified', () => {
  const candidate = path.resolve(directory, '../esp8266-opus-flash-publish-on');
  const combined = JSON.parse(fs.readFileSync(path.join(candidate, 'comparison.json'), 'utf8'));
  for (const [dir,key] of [[directory,'reference'],[candidate,'candidate']]) {
    const reports=Array.from({length:10},(_,i)=>JSON.parse(fs.readFileSync(path.join(dir,`attempt${i+1}.json`),'utf8')));
    const summary=JSON.parse(JSON.stringify(summarize(reports)));
    for(const [k,v] of Object.entries(summary)) assert.deepEqual(combined[key][k],v,k);
    for(const r of reports) assert.equal(r.fixtures.header_sha256,combined[key].manifest.opus_benchmark_header_sha256.toLowerCase());
  }
  assert.equal(combined.qualified_candidate,false);
  assert.deepEqual(combined.candidate.cases.map(c=>c.continuous),[10,0,0,0,0]);
  assert.deepEqual(combined.candidate.cases.map(c=>c.dma_misses.median),[0,35,53,231.5,829]);
  assert.deepEqual(combined.candidate.observation_errors.map(e=>e.attempt),[1,2,3,4,10]);
  assert.equal(combined.target.before.isr_section_sha256,combined.target.after.isr_section_sha256);
});

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
