// Usage: node tools/esp8266_audio_profile/summarize_output_compare.js <log-directory>
// Only accept complete, valid generated-PCM measurements. No CPU-idle inference.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const directory = process.argv[2];
assert.ok(directory, 'Supply a directory containing round-N-{pdm,rcpdm}-uart.log');
const median = values => {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
};
const rows = [];
for (const file of fs.readdirSync(directory).sort()) {
  const name = file.match(/^round-(\d+)-(pdm|rcpdm)-uart\.log$/);
  if (!name) continue;
  const text = fs.readFileSync(path.join(directory, file), 'utf8');
  assert.match(text, /audio_output_bench: complete/, file);
  assert.match(text, /stalled producer.*PASS/, file);
  assert.doesNotMatch(text, /invalid=[1-9]|PCM write failed|stalled producer.*FAIL/, file);
  const fields = prefix => {
    const line = text.split(/\r?\n/).find(line => line.includes(`audio_output_bench: ${prefix}`));
    assert.ok(line, `${file}: missing ${prefix}`);
    return Object.fromEntries([...line.matchAll(/(\w+)=(\d+(?:\.\d+)?)/g)].map(m => [m[1], Number(m[2])]));
  };
  const pack = [...text.matchAll(/pack_only round=(\d+) samples=(\d+) elapsed=(\d+) us checksum=([\da-f]+) DMA=off/g)];
  assert.equal(pack.length, 3, file);
  assert.equal(new Set(pack.map(m => m[4])).size, 1, `${file}: unstable checksum`);
  pack.forEach(m => assert.equal(Number(m[2]), 48000));
  const result = fields('result '), wait = fields('spi_wait='), active = fields('producer_nonwait='), dma = fields('dma ');
  assert.equal(result.write - wait.spi_wait, active.producer_nonwait, file);
  assert.ok(result.audio > 0 && result.wall > 0);
  rows.push({file, mode: name[2], round: Number(name[1]),
    pack_us: pack.map(m => Number(m[3])), checksum: pack[0][4], result, wait, dma,
    underruns: fields('spi_gap ').empty,
    nonwait_us_per_audio_second: active.producer_nonwait * 1e6 / result.audio,
    heap: fields('heap ')});
}
const summary = {};
for (const mode of ['pdm', 'rcpdm']) {
  const selected = rows.filter(row => row.mode === mode);
  assert.ok(selected.length >= 2, `Need at least two complete ${mode} runs`);
  const pack = selected.flatMap(row => row.pack_us);
  summary[mode] = {
    runs: selected.length, pack_48000_words_us_median: median(pack),
    pack_48000_words_us_range: [Math.min(...pack), Math.max(...pack)],
    pack_us_per_word: median(pack) / 48000,
    nonwait_us_per_audio_second_median: median(selected.map(row => row.nonwait_us_per_audio_second)),
    underruns: selected.reduce((sum, row) => sum + row.underruns, 0),
    fifo_empty: selected.reduce((sum, row) => sum + row.dma.fifo_empty, 0)
  };
}
summary.rcpdm_to_pdm_pack_time = summary.rcpdm.pack_48000_words_us_median / summary.pdm.pack_48000_words_us_median;
summary.rcpdm_to_pdm_nonwait_time = summary.rcpdm.nonwait_us_per_audio_second_median / summary.pdm.nonwait_us_per_audio_second_median;
console.log(JSON.stringify({summary, runs: rows}, null, 2));
