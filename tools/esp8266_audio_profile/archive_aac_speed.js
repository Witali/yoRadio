// Archive filtered, reproducible measurements; never includes Wi-Fi/NVS dumps.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const input = path.resolve(root, process.argv[2] || '.build/aac-speed');
const output = path.resolve(root, process.argv[3] || 'docs/benchmarks/esp8266-aac-speed-2026-09-06');
fs.mkdirSync(output, {recursive:true});
const cases = ['reference-1', 'reference-2', 'window-1', 'window-ab',
  'huffman-2', 'huffman-ab', 'reader-1', 'reader-cache-1',
  'accepted-output', 'output-ab', 'huffman6-output', 'huffman6-decode',
  'final-decode-ab', 'final-output-ab'];
const summary = {description:'CPU160 QIO40 GCC8.4 O3, AAC-LC stereo48k/320kbps RAM fixture; no Wi-Fi', runs:[], images:[]};
const ordinary = path.join(input, 'ordinary-uart.log');
if (fs.existsSync(ordinary)) {
  const lines = fs.readFileSync(ordinary, 'utf8').split(/\r?\n/).filter(x =>
    /(?:yoradio8266|codec_arena|audio_output|storage|playlist):|network: Client address:/.test(x));
  fs.writeFileSync(path.join(output, 'ordinary-boot.log'), lines.join('\n') + '\n');
}
for (const name of cases) {
  const dir = path.join(input, name);
  if (!fs.existsSync(dir)) continue;
  for (const file of fs.readdirSync(dir).filter(x => x.endsWith('-uart.log')).sort()) {
    const lines = fs.readFileSync(path.join(dir, file), 'utf8').split(/\r?\n/)
      .filter(x => /(?:codec_ram|codec_arena|audio_output|yoradio8266):/.test(x));
    const target = `${name}-${file.replace('-uart.log', '.log')}`;
    fs.writeFileSync(path.join(output, target), lines.join('\n') + '\n');
    const metrics = lines.filter(x => /RAM frame=|physical wall=|task stack free=|lifecycle /.test(x));
    summary.runs.push({file:target, complete:lines.some(x => /codec_ram: complete/.test(x)), metrics});
  }
}
for (const name of ['window-tests', 'huffman-tests', 'reader-tests', 'reader-cache-tests', 'huffman6-tests', 'final-tests']) {
  const source = path.join(input, `${name}.log`);
  if (fs.existsSync(source)) fs.copyFileSync(source, path.join(output, `${name}.log`));
}
const sizeTool = path.join(root, '.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin/xtensa-lx106-elf-size.exe');
for (const name of ['reference', 'window', 'huffman', 'reader-topup', 'reader-cache', 'huffman6', 'original-output', 'huffman-output', 'huffman6-output-image']) {
  const binary = path.join(input, name, 'app.bin');
  if (!fs.existsSync(binary)) continue;
  const bytes = fs.readFileSync(binary);
  const image = {name, bytes:bytes.length, sha256:crypto.createHash('sha256').update(bytes).digest('hex')};
  const elf = path.join(input, name, 'app.elf');
  if (fs.existsSync(elf) && fs.existsSync(sizeTool)) {
    const run = spawnSync(sizeTool, ['-A', elf], {encoding:'utf8'});
    if (run.status) throw Error(run.stderr);
    image.sections = run.stdout.split(/\r?\n/).filter(x => /^\.(dram0|iram0|flash)/.test(x));
  }
  summary.images.push(image);
}
fs.writeFileSync(path.join(output, 'measurements.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(`Archived ${summary.runs.length} captures and ${summary.images.length} image identities in ${output}`);
