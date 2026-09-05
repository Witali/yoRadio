const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const source = path.join(root, 'esp8266/rtos-sdk-native/main');
const audio = path.join(root, 'yoRadio/src/audioI2S');
const read = name => fs.readFileSync(path.join(source, name), 'utf8').replace(/\r\n/g, '\n');

test('production direct DMA writer preserves PCM/PDM across chunk boundaries and EOF races', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-direct-pdm-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const driver = read('esp8266_nodac_i2s.c');
  const output = read('native_audio_output.c');
  fs.writeFileSync(path.join(dir, 'esp_err.h'), '#pragma once\ntypedef int esp_err_t;\n');
  fs.writeFileSync(path.join(dir, 'gain_config.inc'), ['VOLUME_DENOMINATOR', 'BALANCE_DENOMINATOR', 'GAIN_Q15_ONE']
    .map(name => output.match(new RegExp(`^#define ${name} .+$`, 'm'))[0]).join('\n'));
  fs.writeFileSync(path.join(dir, 'settings.inc'), output.slice(output.indexOf('void native_audio_output_reload_settings(void)')));
  const prefix = driver.slice(driver.indexOf('static inline __attribute__((always_inline)) bool publish_committed_prefix('),
    driver.indexOf('static void IRAM_ATTR submit_buffer('));
  assert.ok(prefix.includes('s_reserved_words'));
  fs.writeFileSync(path.join(dir, 'prefix.inc'), prefix);
  fs.writeFileSync(path.join(dir, 'descriptor.inc'), driver.slice(
    driver.indexOf('typedef struct nodac_dma_descriptor {'),
    driver.indexOf('static uint32_t s_buffers[')));
  // Compile the actual production producer and PDM routines. Only replace
  // Xtensa MEMW with a host fence; MMIO/RTOS events are simulated in the harness.
  const producer = driver.slice(driver.indexOf('static bool acquire_free_buffer('),
    driver.indexOf('void esp8266_nodac_i2s_reset_underruns('));
  assert.ok(producer.includes('esp8266_nodac_i2s_reserve('));
  assert.equal((producer.match(/__asm__ __volatile__\("memw" ::: "memory"\);/g) || []).length, 1);
  fs.writeFileSync(path.join(dir, 'producer.inc'), producer.replace(
    '__asm__ __volatile__("memw" ::: "memory");',
    'std::atomic_thread_fence(std::memory_order_seq_cst);'));
  const start = output.indexOf('#elif YORADIO_ESP8266_I2S_PDM\n\n#define I2S_PDM_WRITE_TIMEOUT_MS');
  assert.ok(start >= 0);
  const end = output.indexOf('\n#else\n\nesp_err_t native_audio_output_init(void)', start);
  assert.ok(end > start);
  const helpers = output.slice(output.indexOf('static uint32_t channel_gain_q15('),
    output.indexOf('\n#if YORADIO_ESP8266_SPI_PDM\n\n#define SPI_PDM_CHUNK_BITS'));
  fs.writeFileSync(path.join(dir, 'output.inc'), helpers + output.slice(
    output.indexOf('\n', start) + 1, end));
  for(const mode of ['PDM32', 'RCPDM', 'PDM128']) {
    const exe = path.join(dir, mode + (process.platform === 'win32' ? '.exe' : ''));
    const files = [path.join(__dirname, 'native/esp8266_direct_pdm_test.cpp'), path.join(audio, 'AudioNormalizer.cpp')];
    let build;
    if(process.platform === 'win32') {
      const base = 'C:\\Program Files\\Microsoft Visual Studio';
      let vcvars;
      if(fs.existsSync(base)) for(const version of fs.readdirSync(base))
        for(const edition of fs.readdirSync(path.join(base, version))) {
          const p = path.join(base, version, edition, 'VC/Auxiliary/Build/vcvars64.bat');
          if(fs.existsSync(p)) vcvars = p;
        }
      if(!vcvars) return t.skip('Visual C++ build tools are not installed');
      const batch = path.join(dir, 'build.cmd');
      fs.writeFileSync(batch, `@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c++20 /O2 /EHsc /W3 /DTEST_${mode}=1 /I"${source}" /I"${audio}" /I"${dir}" ${files.map(p => `"${p}"`).join(' ')} /Fe:"${exe}"\r\n`);
      build = spawnSync('cmd.exe', ['/d', '/c', batch], {cwd:dir, encoding:'utf8'});
    } else {
      build = spawnSync('c++', ['-std=c++20', '-O2', `-DTEST_${mode}=1`, `-I${source}`, `-I${audio}`, `-I${dir}`, ...files, '-o', exe], {cwd:dir, encoding:'utf8'});
      if(build.error?.code === 'ENOENT') return t.skip('Host C++ compiler not installed');
    }
    assert.equal(build.status, 0, build.stdout + build.stderr);
    const run = spawnSync(exe, [], {encoding:'utf8'});
    assert.equal(run.status, 0, run.stdout + run.stderr);
    t.diagnostic(`${mode}: ${run.stdout.trim()}`);
  }
});
