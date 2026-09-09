const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { buildHost, runProbe, root, execute, hostPath } = require('./build_host.cjs');
const { fixtureDirectory, sha256, inspectPackets } = require('./fixtures.cjs');

function comparePcm(reference, actual) {
  assert.equal(actual.length, reference.length, 'PCM sample counts differ');
  assert.equal(actual.length % 2, 0, 'PCM has a partial sample');
  let mismatches = 0, maxError = 0, signal = 0, error = 0;
  for (let offset = 0; offset < reference.length; offset += 2) {
    const expected = reference.readInt16LE(offset), got = actual.readInt16LE(offset), difference = expected - got;
    if (difference) mismatches++;
    maxError = Math.max(maxError, Math.abs(difference));
    signal += expected * expected;
    error += difference * difference;
  }
  return { exact: mismatches === 0, compared_samples: reference.length / 2, mismatched_samples: mismatches,
    max_absolute_error: maxError, snr_db: error === 0 ? 'Infinity' : signal ? 10 * Math.log10(signal / error) : '-Infinity',
    reference_pcm_sha256: sha256(reference), actual_pcm_sha256: sha256(actual) };
}

async function runRegressions({ noBuild = false, upstreamRoot, output } = {}) {
  const manifest = JSON.parse(fs.readFileSync(path.join(fixtureDirectory, 'manifest.json'), 'utf8'));
  const baselineBuild = await buildHost({ noBuild });
  const boundedBuild = await buildHost({ bounded: true, noBuild });
  const pristineBuild = upstreamRoot ? await buildHost({ upstreamRoot, noBuild }) : null;
  const resultDirectory = path.join(root, '.build/esp8266-opus-regression');
  fs.mkdirSync(resultDirectory, { recursive: true });
  const results = [];
  for (const fixture of manifest.fixtures) {
    const filename = path.join(fixtureDirectory, fixture.name + '.opuspkt');
    const data = fs.readFileSync(filename), observed = inspectPackets(data);
    assert.equal(sha256(data), fixture.opuspkt_sha256, fixture.name + ' packet hash changed');
    assert.equal(sha256(fs.readFileSync(path.join(fixtureDirectory, fixture.name + '.opus'))), fixture.ogg_sha256);
    for (const key of Object.keys(observed)) assert.deepEqual(observed[key], fixture[key], fixture.name + ' ' + key);
    const baselinePcm = path.join(resultDirectory, fixture.name + '.baseline.pcm');
    const boundedPcm = path.join(resultDirectory, fixture.name + '.bounded.pcm');
    const baseline = runProbe({ fixture: filename, output: baselinePcm });
    const bounded = runProbe({ bounded: true, fixture: filename, output: boundedPcm });
    const baselineData = fs.readFileSync(baselinePcm);
    const pcm = comparePcm(baselineData, fs.readFileSync(boundedPcm));
    assert.equal(baseline.samples, fixture.samples);
    assert.equal(bounded.samples, fixture.samples);
    assert.deepEqual(baseline.modes, fixture.modes);
    assert.deepEqual(bounded.modes, fixture.modes);
    assert.equal(baseline.reset_exact, true);
    assert.equal(bounded.reset_exact, true);
    assert.equal(bounded.oom_reinitialized_exact, true);
    assert.equal(bounded.arena_guards_ok, true);
    assert.ok(bounded.scratch_byte_peak_bytes <= bounded.scratch_byte_capacity_bytes);
    assert.ok(bounded.scratch_word_peak_bytes <= bounded.scratch_word_capacity_bytes);
    let pristine;
    if (upstreamRoot) {
      const pristinePcm = path.join(resultDirectory, fixture.name + '.pristine.pcm');
      const metadata = runProbe({ upstreamRoot, fixture: filename, output: pristinePcm });
      pristine = { decoder: metadata, pcm_vs_baseline: comparePcm(fs.readFileSync(pristinePcm), baselineData) };
    }
    results.push({ name: fixture.name, opuspkt_sha256: fixture.opuspkt_sha256, baseline, bounded, pcm, ...(pristine ? { pristine } : {}) });
    process.stderr.write(`${fixture.name}: ${pcm.exact ? 'exact' : 'DIFF'}, scratch ${bounded.scratch_byte_peak_bytes}B DRAM / ${bounded.scratch_word_peak_bytes}B word arena\n`);
  }
  // Own synthesized 997/1703 Hz stereo tones, FFmpeg 8.1.1 libopus voip CBR
  // 24 kbps, 8 kHz cutoff, 20 ms: first packet. This explicitly exercises
  // SILK stereo (the existing high-rate stereo corpus is CELT-only).
  const stereoPacket = Buffer.from('4f4102a495791f5554d103e5bebfef8942795b69800d4e248f4a1491cd9dfd42164b35392b308fb81d8c575d8c81236efa1df77424d3b628079b0000', 'hex');
  const stereoLength = Buffer.alloc(2);
  stereoLength.writeUInt16LE(stereoPacket.length);
  const stereoPackets = Buffer.concat(Array.from({ length: 21 }, () => Buffer.concat([stereoLength, stereoPacket])));
  assert.deepEqual(inspectPackets(stereoPackets).packet_channels, { 2: 21 });
  assert.deepEqual(inspectPackets(stereoPackets).modes, { SILK: 21, hybrid: 0, CELT: 0 });
  const stereoFile = path.join(resultDirectory, 'mixed-silk-stereo.opuspkt');
  fs.writeFileSync(stereoFile, stereoPackets);
  const route = [path.join(fixtureDirectory, 'mono-12.opuspkt'), stereoFile,
    path.join(fixtureDirectory, 'mono-12.opuspkt'), path.join(fixtureDirectory, 'mono-24.opuspkt'),
    path.join(fixtureDirectory, 'stereo-128.opuspkt'), stereoFile];
  const sequence = (build, name) => {
    const pcmFile = path.join(resultDirectory, `mixed-${name}.pcm`);
    const decoder = JSON.parse(execute(hostPath(build.binary), ['--sequence', hostPath(pcmFile), ...route.map(hostPath)]));
    assert.equal(decoder.reset_exact, true);
    assert.equal(decoder.sequence_packets, 286);
    assert.equal(decoder.plc_frames, 35);
    assert.equal(decoder.samples, 308160);
    return { decoder, data: fs.readFileSync(pcmFile) };
  };
  const mixedBaseline = sequence(baselineBuild, 'baseline');
  const mixedBounded = sequence(boundedBuild, 'bounded');
  const mixed = { route: route.map(file => path.basename(file)), plc_every_packets: 8,
    silk_stereo_packet_sha256: sha256(stereoPacket), baseline: mixedBaseline.decoder,
    bounded: mixedBounded.decoder, pcm: comparePcm(mixedBaseline.data, mixedBounded.data) };
  assert.equal(mixed.bounded.persistent_bytes, 11232);
  assert.ok(mixed.bounded.scratch_byte_peak_bytes <= mixed.bounded.scratch_byte_capacity_bytes);
  assert.ok(mixed.bounded.scratch_word_peak_bytes <= 16384);
  if (pristineBuild) {
    const pristine = sequence(pristineBuild, 'pristine');
    mixed.pristine = { decoder: pristine.decoder, pcm_vs_baseline: comparePcm(pristine.data, mixedBaseline.data) };
  }
  process.stderr.write(`mixed SILK mono/stereo + hybrid/CELT + PLC: ${mixed.pcm.exact ? 'exact' : 'DIFF'}, scratch ${mixed.bounded.scratch_byte_peak_bytes}B DRAM / ${mixed.bounded.scratch_word_peak_bytes}B word arena\n`);
  const passed = mixed.pcm.exact && (!mixed.pristine || mixed.pristine.pcm_vs_baseline.exact) &&
    results.every(result => result.pcm.exact && (!result.pristine || result.pristine.pcm_vs_baseline.exact));
  const report = { schema_version: 1, passed, compiler: baselineBuild.compiler,
    comparison: 'Vendored libopus with YORADIO_OPUS_BOUNDED undefined versus enabled; mono output at 48000 Hz.',
    memory_scope: 'Host decoder state sizes and arena high-water marks only. Word arena includes persistent CELT history and both SILK excitation buffers. Excludes PCM, packets, bridge state, stack and SDK/Wi-Fi memory. Host sizeof pointers differs from ESP8266.',
    timing_scope: 'No physical ESP8266 throughput, deadline or audio-output claim.',
    ...(upstreamRoot ? { pristine_source: path.relative(root, path.resolve(upstreamRoot)).replace(/\\/g, '/') } : {}),
    fixtures: results, mixed_sequence: mixed };
  fs.writeFileSync(output || path.join(resultDirectory, 'results.json'), JSON.stringify(report, null, 2) + '\n');
  assert.equal(passed, true, 'PCM changed; inspect results.json');
  return report;
}
module.exports = { runRegressions, comparePcm };
if (require.main === module) {
  const value = key => { const i = process.argv.indexOf(key); return i < 0 ? undefined : process.argv[i + 1]; };
  runRegressions({ noBuild: process.argv.includes('--no-build'), upstreamRoot: value('--upstream'), output: value('--output') })
    .then(report => console.log(`PASS: ${report.fixtures.length} fixtures; exact PCM, reset and OOM recovery.`))
    .catch(error => { console.error(error.stack); process.exitCode = 1; });
}
