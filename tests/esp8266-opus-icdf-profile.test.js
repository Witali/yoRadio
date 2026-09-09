const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const builder = fs.readFileSync(path.join(root, 'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), 'utf8');

test('ICDF builder switch requires Opus, defaults OFF, explicitly sets CMake and records a boolean manifest', t => {
  const shell = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
  const available = spawnSync(shell, ['-NoProfile', '-Command', '$PSVersionTable.PSVersion.Major'], { encoding: 'utf8' });
  if (available.error?.code === 'ENOENT') return t.skip('PowerShell unavailable');
  assert.equal(available.status, 0, available.stderr);
  const prelude = builder.slice(0, builder.indexOf('$taskRoot ='));
  const assignment = builder.match(/^\s*\$taskOpusIcdfFlashWord = if \(\$OpusIcdfFlashWord\) \{ 'ON' \} else \{ 'OFF' \}/m)?.[0];
  const argument = builder.match(/"-DYORADIO_OPUS_ICDF_FLASH_WORD=\$taskOpusIcdfFlashWord"/)?.[0];
  const manifest = builder.match(/^\s*opus_icdf_flash_word=\[bool\]\$OpusIcdfFlashWord/m)?.[0];
  assert.ok(assignment && argument && manifest);
  assert.equal((builder.match(/-DYORADIO_OPUS_ICDF_FLASH_WORD=/g) || []).length, 1);
  // Run the actual validation/assignment/argument/manifest expressions only.
  // SDK configuration, compilation, artifact writes and OTA are never invoked.
  const code = '$validate = {\n' + prelude + '\n' + assignment + '\n' +
    '$profile = [ordered]@{\n' + manifest + '\n}\n' +
    'return [pscustomobject]@{ argument = ' + argument + '; profile = ($profile | ConvertTo-Json | ConvertFrom-Json) }\n}\n' + [
    "$ErrorActionPreference = 'Stop'",
    '$default = & $validate',
    'if ($default.argument -ne "-DYORADIO_OPUS_ICDF_FLASH_WORD=OFF" -or $default.profile.opus_icdf_flash_word) { throw "Default is not OFF" }',
    '$cases = 0',
    'foreach ($opus in @($false, $true)) { foreach ($icdf in @($true, $false)) { foreach ($word in @($false, $true)) {',
    '  $ok = $true; $reason = ""',
    '  try { $value = & $validate -EnableOpus:$opus -OpusIcdfFlashWord:$icdf -OpusWordAsm:$word } catch { $ok = $false; $reason = $_.Exception.Message }',
    '  if ($ok -ne ($opus -or -not ($icdf -or $word))) { throw "Wrong acceptance: $opus/$icdf/$word" }',
    '  if (-not $ok -and -not $word -and $reason -ne "-OpusIcdfFlashWord requires -EnableOpus") { throw "Wrong validation: $reason" }',
    '  if ($ok) {',
    '    $expected = if ($icdf) { "ON" } else { "OFF" }',
    '    if ($value.argument -ne "-DYORADIO_OPUS_ICDF_FLASH_WORD=$expected") { throw "Missing explicit CMake selection" }',
    '    if ($value.profile.opus_icdf_flash_word -isnot [bool] -or $value.profile.opus_icdf_flash_word -ne $icdf) { throw "Wrong manifest" }',
    '  }',
    '  ++$cases',
    '}}}',
    'if ($cases -ne 8) { throw "Missing combinations" }',
    'Write-Output "ICDF profile PASS: default and 8 combinations, including ON then OFF"',
  ].join('\n');
  const result = spawnSync(shell, ['-NoProfile', '-NonInteractive', '-Command', code], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /ICDF profile PASS/);
});
