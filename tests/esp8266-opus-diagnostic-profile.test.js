const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {execute, hostPath, root} = require('../tools/esp8266_opus_profile/build_host.cjs');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const builder = read('tools/esp8266_audio_profile/build_i2s_pdm_production.ps1');
const main = read('esp8266/rtos-sdk-native/main/CMakeLists.txt');
const helix = read('esp8266/rtos-sdk-native/components/helix_codecs/CMakeLists.txt');

test('actual PowerShell flags and cached runtime guards cover live/raw/production', t => {
  const command = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
  const available = spawnSync(command, ['-NoProfile', '-NonInteractive', '-Command', '$PSVersionTable.PSVersion.Major'], {encoding:'utf8'});
  if (available.error?.code === 'ENOENT') return t.skip('PowerShell unavailable');
  assert.equal(available.status, 0, available.stderr);
  const extract = name => {
    const match = builder.match(new RegExp('^function ' + name + '\\([^]*?^}', 'm'));
    assert.ok(match, name);
    return match[0];
  };
  // Execute the real parameter validation and pure helpers, never SDK/build code.
  const prelude = builder.slice(0, builder.indexOf('$taskRoot ='));
  const code = extract('Set-TaskOpusRuntimeDefaults') + '\n' + extract('Get-TaskOpusRuntimeProfile') + '\n' +
    '$validate = {\n' + prelude + '\nreturn $taskOpusStreamTestEnabled\n}\n' + [
    "$ErrorActionPreference = 'Stop'",
    '$cases = 0',
    'foreach ($diag in @($false, $true)) { foreach ($opus in @($false, $true)) {',
    'foreach ($stream in @($false, $true)) { foreach ($bench in @($false, $true)) {',
    '  $accepted = $true',
    '  try { $effective = & $validate -Diagnostic:$diag -EnableOpus:$opus -OpusStreamTest:$stream -OpusBenchmark:$bench } catch { $accepted = $false }',
    '  $expected = (-not ($stream -or $bench)) -or ($diag -and $opus)',
    '  if ($accepted -ne $expected) { throw "Wrong flags: $diag/$opus/$stream/$bench" }',
    "  if ($accepted -and $effective -ne ($stream -or $bench)) { throw 'Missing implied stream test' }",
    '  ++$cases',
    '}}}}',
    "if ($cases -ne 16) { throw 'Missing flag combinations' }",
    "$options = @('GENERATE_RUN_TIME_STATS', 'USE_TRACE_FACILITY', 'USE_STATS_FORMATTING_FUNCTIONS', 'RUN_TIME_STATS_USING_ESP_TIMER', 'RUN_TIME_STATS_USING_CPU_CLK')",
    'foreach ($bench in @($false, $true)) {',
    "  $defaults = @('CONFIG_KEEP=42', 'CONFIG_FREERTOS_USE_TRACE_FACILITY=y', '# CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS is not set', 'CONFIG_FREERTOS_RUN_TIME_STATS_USING_CPU_CLK=y') -join [Environment]::NewLine",
    '  $result = Set-TaskOpusRuntimeDefaults $defaults $bench',
    "  if ($result -notmatch '(?m)^CONFIG_KEEP=42\\r?$') { throw 'Unrelated defaults lost' }",
    '  foreach ($option in $options) {',
    '    $lines = @($result -split [char]10 | Where-Object { $_ -match "^(?:CONFIG_FREERTOS_$option=|# CONFIG_FREERTOS_$option is not set)" })',
    '    if ($lines.Count -ne 1) { throw "Duplicate or missing default: $option" }',
    '  }',
    '  $profile = Get-TaskOpusRuntimeProfile $result $bench',
    "  if ($profile.enabled -ne $bench) { throw 'Wrong runtime manifest value' }",
    '  for ($mask = 0; $mask -lt 32; ++$mask) {',
    "    $config = ''",
    '    for ($i = 0; $i -lt $options.Count; ++$i) {',
    '      if ($mask -band (1 -shl $i)) { $config += "CONFIG_FREERTOS_$($options[$i])=y" + [Environment]::NewLine }',
    '    }',
    '    $accepted = $true',
    '    try { Get-TaskOpusRuntimeProfile $config $bench | Out-Null } catch { $accepted = $false }',
    '    $expected = $mask -eq $(if ($bench) { 15 } else { 0 })',
    '    if ($accepted -ne $expected) { throw "Wrong cached runtime guard: $bench/$mask" }',
    '  }',
    '}',
    "Write-Output 'diagnostic profile PASS: 16 flags, 64 runtime cache combinations'",
  ].join('\n');
  const run = spawnSync(command, ['-NoProfile', '-NonInteractive', '-Command', code], {encoding:'utf8'});
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(run.stdout, /16 flags, 64 runtime cache combinations/);
  assert.match(builder, /-DYORADIO_ESP8266_OPUS_STREAM_TEST=\$taskOpusStreamTest/);
  assert.match(builder, /\$taskDefaults = Set-TaskOpusRuntimeDefaults \$taskDefaults \(\[bool\]\$OpusBenchmark\)/);
  assert.match(builder, /\$taskOpusRuntime = Get-TaskOpusRuntimeProfile \$taskConfig \(\[bool\]\$OpusBenchmark\)/);
  assert.ok(builder.indexOf('$taskOpusRuntime = Get-TaskOpusRuntimeProfile') < builder.indexOf('Write-Output "Building'));
  assert.match(builder, /opus_stream_test=\[bool\]\$taskOpusStreamTestEnabled/);
  assert.match(builder, /freertos_runtime_stats=\[bool\]\$taskOpusRuntime.enabled/);
});

test('actual CMake gates both components and needs fixtures only for raw benchmark', t => {
  const bundled = path.join(root, '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const command = process.platform === 'win32' && fs.existsSync(bundled) ? bundled : 'cmake';
  const available = spawnSync(command, ['--version'], {encoding:'utf8'});
  if (available.error?.code === 'ENOENT') return t.skip('CMake unavailable');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opus-profile-cmake-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  fs.writeFileSync(path.join(dir, 'opus_board_fixtures.h'), '/* isolated fixture sentinel */\n');
  const mainBlock = main.slice(main.indexOf('option(YORADIO_ESP8266_DIAGNOSTIC'), main.indexOf('option(YORADIO_ESP8266_SPIFFS_LOG_HTTP'));
  const helixBlock = helix.match(/if\(YORADIO_ESP8266_OPUS_STREAM_TEST OR YORADIO_ESP8266_OPUS_BENCHMARK\)[^]*?endif\(\)/)?.[0];
  assert.ok(helixBlock);
  const script = path.join(dir, 'profile.cmake');
  // Check Helix before main: component ordering must not matter.
  fs.writeFileSync(script, [
    'cmake_minimum_required(VERSION 3.13)',
    'set(COMPONENT_LIB fake)',
    'function(target_compile_definitions)',
    ' if(NOT ARGV2 STREQUAL "YORADIO_ESP8266_OPUS_STREAM_TEST=1")',
    '  message(FATAL_ERROR "Wrong Helix definition")',
    ' endif()',
    ' set(HELIX_STREAM ON PARENT_SCOPE)',
    'endfunction()', helixBlock, mainBlock,
    'if(YORADIO_ESP8266_OPUS_STREAM_TEST AND NOT HELIX_STREAM)',
    ' message(FATAL_ERROR "Missing Helix diagnostic definition")',
    'endif()',
    'if(NOT YORADIO_ESP8266_OPUS_STREAM_TEST AND HELIX_STREAM)',
    ' message(FATAL_ERROR "Production has diagnostic storage")',
    'endif()',
    'list(FIND YORADIO_SOURCES "opus_benchmark.cpp" RAW_SOURCE)',
    'if(YORADIO_ESP8266_OPUS_BENCHMARK AND RAW_SOURCE LESS 0)',
    ' message(FATAL_ERROR "Missing benchmark source")',
    'elseif(NOT YORADIO_ESP8266_OPUS_BENCHMARK AND NOT RAW_SOURCE LESS 0)',
    ' message(FATAL_ERROR "Stream-only has benchmark source")',
    'endif()',
    'get_property(CACHED_STREAM CACHE YORADIO_ESP8266_OPUS_STREAM_TEST PROPERTY VALUE)',
    'if(NOT CACHED_STREAM STREQUAL REQUESTED_STREAM)',
    ' message(FATAL_ERROR "Implied stream option changed cache persistently")',
    'endif()',
  ].join('\n'));
  for (const diag of [false,true]) for (const opus of [false,true])
    for (const stream of [false,true]) for (const bench of [false,true]) {
      const run = spawnSync(command, ['-DYORADIO_ESP8266_DIAGNOSTIC=' + (diag ? 'ON':'OFF'),
        '-DCONFIG_YORADIO_OGG_OPUS=' + (opus ? 'ON':'OFF'), '-DYORADIO_ESP8266_OPUS_STREAM_TEST=' + (stream ? 'ON':'OFF'),
        '-DREQUESTED_STREAM=' + (stream ? 'ON':'OFF'), '-DYORADIO_ESP8266_OPUS_BENCHMARK=' + (bench ? 'ON':'OFF'),
        '-DYORADIO_ESP8266_OPUS_BENCHMARK_FIXTURES=' + (bench ? dir.replace(/\\/g, '/') : '/missing-fixtures'),
        '-P', script], {encoding:'utf8'});
      const valid = !(stream || bench) || (diag && opus);
      assert.equal(run.status === 0, valid, [diag,opus,stream,bench].join('/') + ': ' + run.stdout + run.stderr);
      if (!valid) assert.match(run.stderr, /requires diagnostic Opus profile/);
    }
  assert.match(main, /YORADIO_ESP8266_OPUS_STREAM_TEST=\$<BOOL:\$\{YORADIO_ESP8266_OPUS_STREAM_TEST\}>/);
  assert.match(main, /if\(YORADIO_ESP8266_OPUS_BENCHMARK\)\s+target_include_directories\([^]*?OPUS_BENCHMARK_FIXTURES/);
});

test('preprocessed production/live/raw routes and init snapshot have no crossed guards', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opus-profile-preprocess-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  for (const name of ['web_service.c', 'codec_bridge.cpp', 'codec_bridge.h']) {
    const relative = name === 'web_service.c' ? 'main/' : 'components/helix_codecs/';
    // Preprocess real conditional sections independently of SDK headers/types.
    const source = read('esp8266/rtos-sdk-native/' + relative + name).replace(/^\s*#include[^\r\n]*/gm, '');
    const file = path.join(dir, name);
    fs.writeFileSync(file, source);
    for (const [stream, bench] of [[0,0], [1,0], [1,1]]) {
      const output = execute('gcc', ['-E', '-P', '-x', 'c', '-DCONFIG_YORADIO_OGG_OPUS=1', '-DCONFIG_LWIP_SO_LINGER=1',
        '-DYORADIO_ESP8266_OPUS_STREAM_TEST=' + stream, '-DYORADIO_ESP8266_OPUS_BENCHMARK=' + bench, hostPath(file)]);
      assert.equal(output.includes('helix_codec_opus_init_failure_snapshot'), Boolean(stream), name + '/' + stream + '/' + bench);
      if (name === 'web_service.c') {
        assert.equal(output.includes('"/api/native/opus-stream"'), Boolean(stream));
        assert.equal(output.includes('opus_test_stream_handler('), Boolean(stream));
        assert.equal(output.includes('"/api/native/opus-benchmark"'), Boolean(bench));
        assert.equal(output.includes('opus_benchmark_request('), Boolean(bench));
        const additions = [...output.matchAll(/config.max_uri_handlers \+= (\d+);/g)].reduce((sum,m) => sum + Number(m[1]), 0);
        assert.equal(additions, stream * 2 + bench * 2);
      } else if (name.endsWith('.cpp')) {
        assert.equal(output.includes('s_opus_init_failure'), Boolean(stream));
      }
    }
  }
});
