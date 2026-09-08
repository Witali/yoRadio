#!/usr/bin/env node
const fs = require('node:fs');

function summarize(log, physical, codec = 'MP3') {
  if (!['MP3', 'AAC'].includes(codec)) throw new Error('Unknown codec');
  const cases = (codec === 'AAC' ? [48, 64, 96] : [64, 128, 320]).map(bitrate => {
    const prefix = codec + '/mix/' + bitrate;
    const line = log.split(/\r?\n/).find(s => s.includes(prefix + ' FLASH frame='));
    if (!line) throw new Error('Missing result: ' + prefix);
    const fields = s => Object.fromEntries(
      [...s.matchAll(/(\w+)=(\d+(?:\.\d+)?)/g)].map(m => [m[1], Number(m[2])]));
    const result = {bitrate_kbps: bitrate, ...fields(line)};
    const pcm = log.split(/\r?\n/).find(s => s.includes(prefix + ' PCM nonzero='));
    result.pcm = fields(pcm || '');
    result.valid = result.iterations >= 800 && result.callbacks >= result.iterations &&
      result.audio >= 20000000 && result.pcm.nonzero === 1 &&
      result.pcm.rate === 44100 && result.pcm.channels === 1;
    result.decode_elapsed_budget_percent = result.decode * 100 / result.audio;
    if (physical) {
      const dma = log.split(/\r?\n/).find(s => s.includes(prefix + ' physical wall='));
      if (!dma) throw new Error('Missing physical output: ' + prefix);
      result.physical = fields(dma);
      result.continuous = result.valid && result.physical.audio === result.audio &&
        result.physical.eof > 0 && result.physical.underrun === 0 &&
        result.physical.fifo_empty === 0 &&
        result.physical.audio / result.physical.wall > 0.98 &&
        result.physical.audio / result.physical.wall < 1.03;
    }
    return result;
  });
  const complete = /codec_ram: complete/.test(log);
  const errors = /INVALID benchmark|failed at|allocation failed|memory regression|Guru Meditation/.test(log);
  return {codec, mode: physical ? 'physical-output' : 'decode-only',
    valid: complete && !errors && cases.every(c => c.valid),
    continuous: physical ? complete && !errors && cases.every(c => c.continuous) : null,
    cases};
}
function readLog(file) {
  const bytes = fs.readFileSync(file);
  return bytes.toString(bytes[0] === 0xff && bytes[1] === 0xfe ? 'utf16le' : 'utf8');
}
if (require.main === module) {
  const [file, mode = 'physical', save] = process.argv.slice(2);
  if (!file || !['physical', 'decode'].includes(mode))
    throw new Error('Usage: node summarize_mp3_matrix.cjs capture.log [physical|decode] [report.json]');
  const log = readLog(file);
  const result = summarize(log, mode === 'physical', log.includes('AAC/mix/') ? 'AAC' : 'MP3');
  const json = JSON.stringify(result, null, 2) + '\n';
  if (save) {
    fs.writeFileSync(save, json);
    // Preserve application output, omitting only the different-baud ROM bytes.
    fs.writeFileSync(save.replace(/\.json$/, '') + '.log',
      log.slice(log.indexOf('I (')).replace(/\r\n/g, '\n'));
  }
  console.log(json);
  if (!result.valid || result.continuous === false) process.exitCode = 1;
}
module.exports = {summarize, readLog};
