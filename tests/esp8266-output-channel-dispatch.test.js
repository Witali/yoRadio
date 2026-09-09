const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {execute} = require('../tools/esp8266_audio_profile/run_rcpdm_radio');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');

// Compile the actual production I2S section with a mock DMA sink, not a copy
// of its channel dispatcher. SDK/Wi-Fi/ISR operation is outside this host test.
function section(source, start, end) {
  const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Missing source boundaries: ${start}`);
  return source.slice(a, b);
}

for (const led of [0, 1]) for (const backend of ['pdm', 'rcpdm', 'feedback', 'simple']) {
  test(`I2S ${backend} LED=${led}: format dispatch preserves PCM, bits, state and DMA boundaries`, t => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-channel-dispatch-'));
    t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
    const source = fs.readFileSync(path.join(main, 'native_audio_output.c'), 'utf8').replace(/\r\n/g, '\n');
    const common = section(source, 'static uint8_t s_volume =', '#if YORADIO_ESP8266_SPI_PDM\n\n#define SPI_PDM_CHUNK_BITS');
    const i2s = section(source, '#define I2S_PDM_WRITE_TIMEOUT_MS', '\n#else\n\nesp_err_t native_audio_output_init(void) {');
    assert.match(i2s, /if \(channels != s_i2s_pdm_channels\)/);
    assert.match(i2s, /return s_i2s_pdm_write\(samples, sample_count, sample_rate\)/);
    fs.writeFileSync(path.join(dir, 'output_under_test.inc'), common + i2s);
    const flags = [
      `CONFIG_YORADIO_STATUS_LED=${led}`,
      `CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=${backend !== 'pdm' ? 1 : 0}`,
      `CONFIG_YORADIO_RCPDM_FEEDBACK=${backend === 'feedback' ? 1 : 0}`,
      `RCPDM_TEST_SIMPLE=${backend === 'simple' ? 1 : 0}`,
    ];
    const exe = path.join(dir, 'test' + (process.platform === 'win32' ? '.exe' : ''));
    const harness = path.join(root, 'tests/native/esp8266_output_channel_dispatch.cpp');
    const includes = [dir, main, path.join(root, 'tests/native')];
    if (process.platform === 'win32') {
      let vc;
      const base = 'C:/Program Files/Microsoft Visual Studio';
      for (const v of fs.readdirSync(base)) for (const e of fs.readdirSync(path.join(base, v))) {
        const candidate = path.join(base, v, e, 'VC/Auxiliary/Build/vcvars64.bat');
        if (fs.existsSync(candidate)) vc = candidate;
      }
      assert.ok(vc, 'MSVC required');
      const cmd = path.join(dir, 'build.cmd');
      fs.writeFileSync(cmd, `@call "${vc}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c++20 /O2 /EHsc /W4 ${flags.map(f => '/D' + f).join(' ')} ${includes.map(p => `/I"${p}"`).join(' ')} "${harness}" /Fe:"${exe}"\r\n`);
      execute('cmd.exe', ['/d', '/c', cmd], {cwd: dir});
    } else {
      execute('c++', ['-std=c++20', '-O2', '-fsanitize=undefined', ...flags.map(f => '-D' + f),
        ...includes.map(p => '-I' + p), harness, '-o', exe], {cwd: dir});
    }
    const result = JSON.parse(execute(exe, []).stdout);
    assert.equal(result.pass, true);
    assert.ok(result.blocks >= 1000);
    assert.ok(result.words > 100000);
    t.diagnostic(JSON.stringify(result));
  });
}
