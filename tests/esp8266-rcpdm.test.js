const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const test = require('node:test');

const root = path.resolve(__dirname, '..');
const project = path.join(root, 'esp8266', 'rtos-sdk-native');
const main = path.join(project, 'main');
const read = name => fs.readFileSync(path.join(main, name), 'utf8');

test('I2S RCPDM is a separate opt-in profile, not a new board default', () => {
  const defaults = fs.readFileSync(path.join(project, 'sdkconfig.defaults'), 'utf8');
  const profile = fs.readFileSync(path.join(project, 'sdkconfig.i2s-rcpdm.defaults'), 'utf8');
  assert.match(defaults, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=n/);
  assert.match(defaults, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y/);
  assert.match(profile, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=y/);
  assert.match(profile, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=n/);
  assert.match(profile, /CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_128=n/);
  assert.match(profile, /CONFIG_YORADIO_HELIX_MP3_SSO=y/);
  assert.match(profile, /CONFIG_ESPTOOLPY_FLASHFREQ_40M=y/);
  assert.match(read('Kconfig.projbuild'), /config YORADIO_AUDIO_OUTPUT_I2S_RCPDM\s+bool "I2S RCPDM/);
  assert.match(read('app_main.c'), /I2S RCPDM DMA GPIO/);
});

test('RCPDM32 reuses the production carrier, sample pacing and DMA ring', () => {
  const config = read('spi_pdm_config.h');
  assert.match(config, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM[\s\S]*BOARD_I2S_PDM_OVERSAMPLE 32U/);
  assert.match(config, /BOARD_I2S_PDM_SAMPLE_RATE 48000U/);
  assert.match(config, /BOARD_I2S_PDM_BCK_DIV 8U/);
  assert.match(config, /BOARD_I2S_PDM_CLKM_DIV 13U/);
  assert.match(read('esp8266_nodac_i2s.h'), /DMA_BUFFER_COUNT 2U/);
  assert.match(read('esp8266_nodac_i2s.h'), /DMA_BUFFER_WORDS 512U/);
  const output = read('native_audio_output.c');
  assert.match(output, /return rc_pdm_sample\(&s_rcpdm, sample\)/);
  assert.match(output, /i2s_pdm_push_word\(writer, i2s_pdm_pack32\(sample\)\)/);
  assert.match(output, /s_resample_phase \+= BOARD_I2S_PDM_SAMPLE_RATE/);
  assert.equal((output.match(/rc_pdm_init\(&s_rcpdm\)/g) || []).length, 2);
  assert.doesNotMatch(read('rc_pdm.h'), /\b(float|double|uint64_t|int64_t|malloc|calloc)\b/);
});

function findVcVars() {
  const base = 'C:\\Program Files\\Microsoft Visual Studio';
  if (!fs.existsSync(base)) return null;
  for (const version of fs.readdirSync(base).sort().reverse()) {
    const directory = path.join(base, version);
    if (!fs.statSync(directory).isDirectory()) continue;
    for (const edition of fs.readdirSync(directory).sort().reverse()) {
      const candidate = path.join(directory, edition, 'VC', 'Auxiliary', 'Build', 'vcvars64.bat');
      if (fs.existsSync(candidate)) return candidate;
    }
  }
  return null;
}

test('RCPDM32 C implementation matches the independent full-range RC reference', t => {
  const output = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-rcpdm-'));
  t.after(() => fs.rmSync(output, {recursive:true, force:true}));
  const executable = path.join(output, process.platform === 'win32' ? 'rcpdm.exe' : 'rcpdm');
  const harness = path.join(__dirname, 'native', 'esp8266_rcpdm_test.c');
  let build;
  if (process.platform === 'win32') {
    const vcvars = findVcVars();
    if (!vcvars) return t.skip('Visual C++ build tools are not installed');
    const batch = path.join(output, 'build.cmd');
    fs.writeFileSync(batch, `@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c11 /O2 /W4 /WX /I"${main}" "${harness}" /Fe:"${executable}"\r\n`);
    build = spawnSync('cmd.exe', ['/d', '/c', batch], {cwd:output, encoding:'utf8'});
  } else {
    build = spawnSync('cc', ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', `-I${main}`, harness, '-o', executable], {cwd:output, encoding:'utf8'});
    if (build.error?.code === 'ENOENT') return t.skip('A host C compiler is not installed');
  }
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
  const run = spawnSync(executable, [], {encoding:'utf8'});
  assert.equal(run.status, 0, `${run.stdout}\n${run.stderr}`);
  assert.match(run.stdout, /RCPDM32 tests passed/);
});
