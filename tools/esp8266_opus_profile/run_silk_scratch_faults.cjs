const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { buildHost, execute, hostPath, component } = require('./build_host.cjs');
const { fixtureDirectory, sha256 } = require('./fixtures.cjs');

async function run({ output, sanitize = true } = {}) {
  const build = await buildHost({ bounded: true, silkScratch: true, fastInt64: 0, sanitize });
  const source = path.join(__dirname, 'silk_scratch_probe.c');
  const object = path.join(build.out, 'silk_scratch_probe.o');
  const binary = path.join(build.out, 'silk_scratch_probe');
  execute('gcc', [...build.flags, '-Wall', '-Wextra', '-Werror', '-c', hostPath(source), '-o', hostPath(object)]);
  execute('gcc', [...build.linkFlags, ...build.objects.filter(f => !f.endsWith('probe.c.o')).map(hostPath), hostPath(object),
    '-Wl,--gc-sections', '-Wl,--wrap=yoradio_opus_scratch_alloc', '-lm', '-o', hostPath(binary)]);
  const names = ['mono-12', 'stereo-64', 'stereo-128', 'stereo-510', 'phase/stereo-2_5ms', 'phase/stereo-5ms', 'phase/stereo-10ms'];
  const inputs = names.map(name => path.join(fixtureDirectory, name + '.opuspkt'));
  const result = JSON.parse(execute(hostPath(binary), inputs.map(hostPath)));
  assert.equal(result.passed, true);
  assert.ok(result.injected_ooms > result.packets && result.loan_peak_bytes > 0);
  const report = { ...result, sanitizers: sanitize ? ['address', 'undefined'] : [],
    scope: 'Host generic32 mono48k. Fault after each allocation while SILK is lent; poisoned allocated memory, OPUS_ALLOC_FAIL, then reset without rebind and exact SILK PCM. No target speed/memory qualification.',
    compiler: build.compiler, flags: build.flags,
    inputs: Object.fromEntries(inputs.map((file, i) => [names[i], sha256(fs.readFileSync(file))])),
    source_sha256_lf: Object.fromEntries(['opus_memory.c', 'opus_memory.h', 'upstream/src/opus_decoder.c'].map(name =>
      [name, sha256(Buffer.from(fs.readFileSync(path.join(component, name), 'utf8').replace(/\r\n/g, '\n')))])) };
  if (output) fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  return report;
}
module.exports = { run };
if (require.main === module) {
  const index = process.argv.indexOf('--output');
  run({ output: index < 0 ? undefined : process.argv[index + 1], sanitize: !process.argv.includes('--no-sanitize') })
    .then(r => console.log(JSON.stringify(r, null, 2))).catch(e => { console.error(e.stack); process.exitCode = 1; });
}
