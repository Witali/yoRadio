const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {root, component, execute, hostPath} = require('../tools/esp8266_opus_profile/build_host.cjs');
const builder = fs.readFileSync(path.join(root, 'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), 'utf8');

test('actual low-RAM PowerShell gate rejects production and unqualified scratch sizes', t => {
  const shell = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
  if (spawnSync(shell, ['-NoProfile', '-Command', '$PSVersionTable.PSVersion.Major']).error?.code === 'ENOENT')
    return t.skip('PowerShell unavailable');
  const prelude = builder.slice(0, builder.indexOf('$taskRoot ='));
  const assignment = builder.match(/^\s*\$taskOpusLowRam =.*$/m)?.[0];
  const argument = builder.match(/"-DYORADIO_OPUS_LOW_RAM=\$taskOpusLowRam"/)?.[0];
  const manifest = builder.match(/^\s*opus_low_ram=\[bool\]\$OpusLowRam/m)?.[0];
  const scratchManifest = builder.match(/^\s*opus_scratch_bytes=.*$/m)?.[0];
  assert.ok(assignment && argument && manifest && scratchManifest);
  // Only parameter validation and serialization; never SDK/build/artifact/OTA actions.
  const code = '$validate = {\n' + prelude + '\n' + assignment + '\n' +
    '$taskOpusEnabled = [bool]$EnableOpus\n$profile = [ordered]@{\n' + manifest + '\n' + scratchManifest + '\n}\n' +
    'return [pscustomobject]@{ argument = ' + argument + '; profile = ($profile | ConvertTo-Json | ConvertFrom-Json) }\n}\n' + [
    "$ErrorActionPreference = 'Stop'",
    '$default = & $validate -EnableOpus',
    'if ($default.argument -ne "-DYORADIO_OPUS_LOW_RAM=OFF" -or $default.profile.opus_low_ram -or $default.profile.opus_scratch_bytes -ne 6144) { throw "Changed production default" }',
    '$cases = 0',
    'foreach ($diag in @($false,$true)) { foreach ($opus in @($false,$true)) {',
    'foreach ($low in @($true,$false)) { foreach ($size in @(4352,6144,4096)) {',
    ' $ok = $true',
    ' try { $value = & $validate -Diagnostic:$diag -EnableOpus:$opus -OpusLowRam:$low -OpusScratchBytes $size } catch { $ok = $false }',
    ' $expected = ($size -eq 4352 -or $size -eq 6144) -and ((-not $low) -or ($diag -and $opus)) -and ($size -eq 6144 -or $low)',
    ' if ($ok -ne $expected) { throw "Wrong acceptance: $diag/$opus/$low/$size" }',
    ' if ($ok) {',
    '  $mode = if ($low) { "ON" } else { "OFF" }',
    '  if ($value.argument -ne "-DYORADIO_OPUS_LOW_RAM=$mode" -or $value.profile.opus_low_ram -isnot [bool] -or $value.profile.opus_low_ram -ne $low) { throw "Wrong low-RAM serialization" }',
    '  $capacity = if ($opus) { $size } else { 0 }',
    '  if ($value.profile.opus_scratch_bytes -ne $capacity) { throw "Wrong scratch serialization" }',
    ' }',
    ' ++$cases',
    '}}}}',
    'if ($cases -ne 24) { throw "Missing combinations" }',
    'Write-Output "low-RAM profile PASS: 24 combinations"'
  ].join('\n');
  const run = spawnSync(shell, ['-NoProfile', '-NonInteractive', '-Command', code], {encoding:'utf8'});
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(run.stdout, /24 combinations/);
});

test('actual component makes low-RAM opt-in and shares the scratch-mark ABI', t => {
  const bundled = path.join(root, '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const cmake = process.platform === 'win32' && fs.existsSync(bundled) ? bundled : 'cmake';
  if (spawnSync(cmake, ['--version']).error?.code === 'ENOENT') return t.skip('CMake unavailable');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opus-lowram-cmake-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const script = path.join(dir, 'check.cmake');
  fs.writeFileSync(script, [
    'cmake_minimum_required(VERSION 3.13)',
    'function(idf_component_register)', 'set(COMPONENT_LIB fake PARENT_SCOPE)', 'endfunction()',
    'function(target_compile_options)', 'endfunction()',
    'function(target_compile_definitions)',
    'foreach(def IN LISTS ARGN)',
    ' if(def MATCHES "^YORADIO_OPUS_(CELT_SILK_SCRATCH|AUTOCORR_COMPACT|SILK_PLC_IRAM)=1$")',
    '  list(APPEND FOUND "${def}")',
    '  if(def STREQUAL "YORADIO_OPUS_CELT_SILK_SCRATCH=1" AND NOT ARGV1 STREQUAL "PUBLIC")',
    '   message(FATAL_ERROR "Scratch mark ABI must be PUBLIC")', '  endif()', ' endif()', 'endforeach()',
    'set(FOUND "${FOUND}" PARENT_SCOPE)', 'endfunction()',
    `include("${path.join(component, 'CMakeLists.txt').replace(/\\/g, '/')}")`,
    'list(LENGTH FOUND COUNT)',
    'if(CONFIG_YORADIO_OGG_OPUS AND YORADIO_OPUS_LOW_RAM)',
    ' if(NOT COUNT EQUAL 3)', '  message(FATAL_ERROR "Missing low-RAM definitions")', ' endif()',
    'elseif(NOT COUNT EQUAL 0)', ' message(FATAL_ERROR "Default contains low-RAM definitions")', 'endif()'
  ].join('\n'));
  for (const opus of [false,true]) for (const diag of [false,true]) for (const low of [false,true]) {
    const run = spawnSync(cmake, ['-DCONFIG_YORADIO_OGG_OPUS='+(opus?'ON':'OFF'),
      '-DYORADIO_ESP8266_DIAGNOSTIC='+(diag?'ON':'OFF'), '-DYORADIO_OPUS_LOW_RAM='+(low?'ON':'OFF'),
      '-P',script], {encoding:'utf8'});
    assert.equal(run.status === 0, !opus || !low || diag, run.stdout + run.stderr);
    if (run.status) assert.match(run.stderr, /Low-RAM Opus requires diagnostic/);
  }
});

test('PLC IRAM rejects byte aliases and unsupported optional SILK modes', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opus-plc-gates-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const source = fs.readFileSync(path.join(component,'upstream/silk/PLC.c'),'utf8').replace(/^\s*#include[^\r\n]*/gm,'');
  const file = path.join(dir,'plc.c'); fs.writeFileSync(file,source);
  for (const flags of [[],['-DYORADIO_OPUS_BOUNDED=1'],
    ...['SMALL_FOOTPRINT','ENABLE_DEEP_PLC','ENABLE_OSCE'].map(f=>['-DYORADIO_OPUS_BOUNDED=1','-D'+f+'=1'])]) {
    const run = () => execute('gcc',['-E','-P','-DYORADIO_OPUS_SILK_PLC_IRAM=1',...flags,hostPath(file)]);
    if (flags.length===1) assert.doesNotThrow(run);
    else assert.throws(run,/PLC IRAM requires bounded plain SILK/);
  }
});
