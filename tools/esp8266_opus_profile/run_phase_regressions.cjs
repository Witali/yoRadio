const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { buildHost, execute, hostPath, root } = require('./build_host.cjs');
const { prepareReference, defaultOutput } = require('./prepare_generic32_reference.cjs');
const { inspectPackets, sha256, fixtureDirectory } = require('./fixtures.cjs');
const { comparePcm, runRegressions } = require('./run_regressions.cjs');

async function phaseBuild(bounded) {
  const build = await buildHost({ bounded, fastInt64: 0, ...(bounded ? {} : { upstreamRoot: defaultOutput }) });
  const object = path.join(build.out, 'phase_probe.o'), binary = path.join(build.out, 'phase_probe');
  execute('gcc', [...build.flags, '-c', hostPath(path.join(__dirname, 'phase_probe.c')), '-o', hostPath(object)]);
  execute('gcc', [...build.objects.filter(file => !file.endsWith('probe.c.o')).map(hostPath), hostPath(object),
    ...(bounded ? ['-Wl,--wrap=quant_all_bands', '-Wl,--wrap=yoradio_opus_scratch_alloc'] : []),
    '-no-pie', '-Wl,--gc-sections', '-lm', '-o', hostPath(binary)]);
  return { ...build, binary };
}
async function runPhaseRegressions({ output = path.join(__dirname, 'pcm-scratch-results.json'), capacity = 6144 } = {}) {
  assert.ok(Number.isInteger(capacity) && capacity > 0 && capacity <= 7680 && capacity % 4 === 0);
  prepareReference();
  const standard = await runRegressions({ fastInt64: 0, upstreamRoot: defaultOutput });
  const pristine = await phaseBuild(false), bounded = await phaseBuild(true);
  const directory = path.join(fixtureDirectory, 'phase');
  const manifest = JSON.parse(fs.readFileSync(path.join(directory, 'manifest.json'), 'utf8'));
  const destination = path.join(root, '.build/esp8266-opus-phase-regression');
  fs.mkdirSync(destination, { recursive: true });
  const cases = manifest.fixtures.map(fixture => {
    const file = path.join(directory, fixture.name + '.opuspkt'), data = fs.readFileSync(file);
    assert.equal(sha256(data), fixture.opuspkt_sha256);
    for (const [key, value] of Object.entries(inspectPackets(data))) assert.deepEqual(value, fixture[key]);
    return { name: fixture.name, route: [file], plc: false, input_sha256: [sha256(data)] };
  });
  cases.push({ name: 'all-phase-mixed-plc', route: cases.map(test => test.route[0]), plc: true });
  cases.push({ name: 'standard-mixed-plc', route: standard.mixed_sequence.route.map(name =>
    path.join(name.startsWith('mixed-') ? '.build/esp8266-opus-regression-int64-0' : fixtureDirectory, name)), plc: true });
  cases.push({ ...cases.at(-1), name: 'standard-burst-plc', plcBurst: 6 });
  for (const fixture of standard.fixtures) cases.push({ name: 'standard-clean-' + fixture.name,
    route: [path.join(fixtureDirectory, fixture.name + '.opuspkt')], plc: false });
  for (const rate of [8000, 12000, 16000, 24000]) cases.push({ name: `downsample-${rate}-guard`,
    route: [path.join(directory, 'stereo-2_5ms.opuspkt')], rate, plc: false });
  const results = cases.map(test => {
    const probe = (build, name) => {
      const file = path.join(destination, test.name + '.' + name + '.pcm');
      const metadata = JSON.parse(execute('env', [`OPUS_PHASE_CAPACITY=${capacity}`, `OPUS_PHASE_RATE=${test.rate || 48000}`,
        `OPUS_PHASE_PLC_BURST=${test.plcBurst || 1}`, hostPath(build.binary), hostPath(file), ...(test.plc ? ['--plc'] : []),
        ...test.route.map(file => hostPath(path.resolve(file)))]));
      return { metadata, pcm: fs.readFileSync(file) };
    };
    const reference = probe(pristine, 'pristine'), actual = probe(bounded, 'bounded');
    const pcm = comparePcm(reference.pcm, actual.pcm);
    assert.equal(pcm.exact, true, test.name + ' PCM differs');
    assert.equal(actual.metadata.pcm_guards_ok, true);
    assert.equal(actual.metadata.reset_exact, true);
    assert.ok(actual.metadata.scratch_byte_peak_bytes <= capacity);
    if (test.rate) assert.deepEqual(actual.metadata.borrowed_by_lm, [0, 0, 0, 0], 'downsample guard borrowed PCM');
    process.stderr.write(`${test.name}: exact; DRAM ${actual.metadata.scratch_byte_peak_bytes}; transient ${actual.metadata.transient_borrowed}; dual ${actual.metadata.dual_stereo_borrowed}\n`);
    return { name: test.name, route: test.route.map(file => path.relative(root, path.resolve(file)).replace(/\\/g, '/')),
      plc_burst: test.plc ? test.plcBurst || 1 : 0,
      input_sha256: test.input_sha256 || test.route.map(file => sha256(fs.readFileSync(file))), pristine: reference.metadata, bounded: actual.metadata, pcm };
  });
  const coverage = results.reduce((sum, result) => {
    result.bounded.borrowed_by_lm.forEach((count, lm) => sum.borrowed_by_lm[lm] += count);
    for (const name of ['transient_borrowed', 'dual_stereo_borrowed', 'borrow_denied']) sum[name] += result.bounded[name];
    return sum;
  }, { borrowed_by_lm: [0, 0, 0, 0], transient_borrowed: 0, dual_stereo_borrowed: 0, borrow_denied: 0 });
  assert.ok(coverage.borrowed_by_lm.every(count => count > 0));
  assert.ok(coverage.transient_borrowed > 0 && coverage.dual_stereo_borrowed > 0 && coverage.borrow_denied > 0);
  const report = { schema_version: 1, passed: true, arithmetic: 'OPUS_FAST_INT64=0',
    scope: 'Host mono output, maximum 20-ms packets; 48 kHz except explicit downsample-denial guard cases. Independently prepared pristine generic32 comparison. No physical speed, stack or whole-device memory claim; corpus peak is not a universal upper bound.',
    pristine_provenance: standard.pristine_provenance,
    phase_source_sha256_lf: Object.fromEntries(['bands.c', 'bands.h', 'celt_decoder.c'].map(name => {
      const file = 'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/' + name;
      return [file, sha256(Buffer.from(fs.readFileSync(path.join(root, file), 'utf8').replace(/\r\n/g, '\n')))];
    })),
    standard_regression: { passed: standard.passed, fixtures: standard.fixtures.map(result => ({ name: result.name, pcm: result.pcm,
      bounded: result.bounded })), mixed: standard.mixed_sequence }, coverage, cases: results };
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  return report;
}
module.exports = { phaseBuild, runPhaseRegressions };
if (require.main === module) runPhaseRegressions().then(report => console.log(JSON.stringify({ passed: report.passed, coverage: report.coverage })))
  .catch(error => { console.error(error.stack); process.exitCode = 1; });
