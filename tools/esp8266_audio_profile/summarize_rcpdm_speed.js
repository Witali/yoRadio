const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const directories = process.argv.slice(2);
assert.ok(directories.length, 'Supply matrix/final-ab/specialized-ab log directories');
const runs = [];
for (const directory of directories) for (const file of fs.readdirSync(directory).sort()) {
  const name = file.match(/^round-(\d+)-(.+)-uart\.log$/);
  if (!name) continue;
  const text = fs.readFileSync(path.join(directory, file), 'utf8');
  assert.match(text, /RCPDM bit-exact PASS: 493216 words and states/, file);
  assert.match(text, /audio_output_bench: complete/, file);
  assert.doesNotMatch(text, /invalid=[1-9]|bit-exact FAIL|PCM write failed|stalled producer.*FAIL/, file);
  const fields = prefix => {
    const line = text.split(/\r?\n/).find(s => s.includes(`audio_output_bench: ${prefix}`));
    assert.ok(line, `${file}: missing ${prefix}`);
    return Object.fromEntries([...line.matchAll(/(\w+)=(\d+(?:\.\d+)?)/g)].map(m => [m[1], +m[2]]));
  };
  const pack = [...text.matchAll(/pack_only round=\d+ samples=48000 elapsed=(\d+) us checksum=([\da-f]+)/g)];
  assert.equal(pack.length, 3);
  pack.forEach(m => assert.equal(m[2], 'e3126451'));
  const result = fields('result '), wait = fields('spi_wait='), active = fields('producer_nonwait=');
  assert.equal(result.write - wait.spi_wait, active.producer_nonwait);
  runs.push({suite: path.basename(directory), file, variant: name[2], round: +name[1],
    pack_us: pack.map(m => +m[1]), scalar_bit_exact_words: 493216,
    batch_bit_exact_words: +(text.match(/RCPDM batch bit-exact PASS: (\d+)/)?.[1] || 0),
    nonwait_us_per_audio_second: active.producer_nonwait * 1e6 / result.audio,
    result, wait, dma: fields('dma '), underruns: fields('spi_gap ').empty, heap: fields('heap ')});
}
console.log(JSON.stringify({runs}, null, 2));
