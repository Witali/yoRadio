const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {buildHost, hostPath, execute, root, component} =
  require('../tools/esp8266_opus_profile/build_host.cjs');

test('native Opus streaming adapter validates headers, sample trimming, chains, cancellation and bounded memory',
  {timeout: 180000}, async t => {
    try { execute('gcc', ['--version']); }
    catch (error) {
      if (error.code === 'ENOENT' || /not found|not installed|no installed distributions/i.test(error.message))
        return t.skip('GCC (WSL on Windows) unavailable');
      throw error;
    }
    const build = await buildHost({bounded: true, noBuild: process.env.YORADIO_OPUS_NO_BUILD === '1'});
    const directory = fs.mkdtempSync(path.join(build.out, 'adapter-test-'));
    t.after(() => fs.rmSync(directory, {recursive: true, force: true}));
    const objects = build.objects.filter(file => !file.endsWith('probe.c.o'));
    for (const name of ['native_opus.c', 'ogg_opus_demux.c', 'test.c']) {
      const source = name === 'test.c' ? path.join(__dirname, 'native/esp8266_native_opus_test.c') : path.join(component, name);
      const object = path.join(directory, name + '.o');
      execute('gcc', [...build.flags, '-Wall', '-Wextra', '-Werror', '-c', hostPath(source), '-o', hostPath(object)]);
      objects.push(object);
    }
    const binary = path.join(directory, 'test');
    execute('gcc', [...objects.map(hostPath), '-Wl,--gc-sections', '-Wl,--wrap=malloc',
      '-Wl,--wrap=calloc', '-Wl,--wrap=realloc', '-lm', '-o', hostPath(binary)]);
    const result = execute(hostPath(binary), []);
    assert.match(result, /Native Opus PASS/);
    assert.match(result, /no allocations/);
    t.diagnostic(result.trim());
  });
