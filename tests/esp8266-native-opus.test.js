const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {buildHost, hostPath, execute, root, component} =
  require('../tools/esp8266_opus_profile/build_host.cjs');

for (const pcmLeases of process.env.YORADIO_OPUS_PCM_LEASES === undefined ?
  [false,true] : [process.env.YORADIO_OPUS_PCM_LEASES === '1'])
test('native Opus streaming adapter validates headers, trimming, cancellation and bounded memory; leases='+pcmLeases,
  {timeout: 180000}, async t => {
    try { execute('gcc', ['--version']); }
    catch (error) {
      if (error.code === 'ENOENT' || /not found|not installed|no installed distributions/i.test(error.message))
        return t.skip('GCC (WSL on Windows) unavailable');
      throw error;
    }
    const fastInt64 = process.env.YORADIO_OPUS_FAST_INT64 === undefined ? undefined :
      Number(process.env.YORADIO_OPUS_FAST_INT64);
    const lowRam = process.env.YORADIO_OPUS_LOW_RAM === '1';
    const scratchBytes = Number(process.env.YORADIO_OPUS_TEST_SCRATCH_BYTES || (lowRam ? 4352 : 7680));
    assert.ok(Number.isInteger(scratchBytes) && scratchBytes >= 3072 && scratchBytes <= 7680 && scratchBytes % 4 === 0);
    const build = await buildHost({bounded: true, fastInt64, pcmLeases,
      silkScratch: lowRam || process.env.YORADIO_OPUS_SILK_SCRATCH === '1',
      autocorrCompact: lowRam, silkPlcIram: lowRam,
      noBuild: process.env.YORADIO_OPUS_NO_BUILD === '1'});
    const directory = fs.mkdtempSync(path.join(build.out, 'adapter-test-'));
    t.after(() => fs.rmSync(directory, {recursive: true, force: true}));
    const objects = build.objects.filter(file => !file.endsWith('probe.c.o'));
    for (const name of ['native_opus.c', 'ogg_opus_demux.c', 'test.c']) {
      const source = name === 'test.c' ? path.join(__dirname, 'native/esp8266_native_opus_test.c') : path.join(component, name);
      const object = path.join(directory, name + '.o');
      execute('gcc', [...build.flags, '-DNATIVE_OPUS_TEST_SCRATCH_BYTES=' + scratchBytes,
        '-Wall', '-Wextra', '-Werror', '-c', hostPath(source), '-o', hostPath(object)]);
      objects.push(object);
    }
    const binary = path.join(directory, 'test');
    execute('gcc', [...objects.map(hostPath), '-Wl,--gc-sections', '-Wl,--wrap=malloc',
      '-Wl,--wrap=calloc', '-Wl,--wrap=realloc', '-lm', '-o', hostPath(binary)]);
    const capture = process.env.YORADIO_OPUS_LIVE_CAPTURE;
    const golden = process.env.YORADIO_OPUS_LIVE_GOLDEN;
    assert.equal(Boolean(capture), Boolean(golden), 'live capture and raw golden PCM paths must be supplied together');
    const result = execute(hostPath(binary), capture ?
      [hostPath(path.resolve(capture)), hostPath(path.resolve(golden))] : []);
    assert.match(result, /Native Opus PASS/);
    assert.match(result, /no allocations/);
    if (pcmLeases) assert.match(result, /Native PCM leases: .*no stranded slots PASS/);
    assert.match(result, /Native live join: strict default, pre-skip, 64-bit granules and reset PASS/);
    t.diagnostic('scratch=' + scratchBytes + ', lowRam=' + lowRam + '\n' + result.trim());
  });
