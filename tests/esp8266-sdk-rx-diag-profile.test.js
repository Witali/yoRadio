const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

test('SDK RX counters require diagnostics and are explicitly OFF for normal builds', () => {
  const builder = fs.readFileSync(path.join(__dirname, '../tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), 'utf8');
  const prelude = builder.slice(0, builder.indexOf('$taskRoot ='));
  const assignment = builder.match(/^\s*\$taskSdkRxDiag = if \(\$SdkRxDiag\) \{ 'ON' \} else \{ 'OFF' \}/m)?.[0];
  const argument = builder.match(/"-DYORADIO_ESP8266_SDK_RX_DIAG=\$taskSdkRxDiag"/)?.[0];
  const manifest = builder.match(/^\s*sdk_rx_diag=\[bool\]\$SdkRxDiag/m)?.[0];
  assert.ok(assignment && argument && manifest);
  assert.equal((builder.match(/-DYORADIO_ESP8266_SDK_RX_DIAG=/g) || []).length, 1);
  const code = '$validate = {\n' + prelude + '\n' + assignment + '\n' +
    '$profile = [ordered]@{\n' + manifest + '\n}\n' +
    'return [pscustomobject]@{ argument = ' + argument + '; profile = ($profile | ConvertTo-Json | ConvertFrom-Json) }\n}\n' + [
      "$ErrorActionPreference = 'Stop'",
      '$default = & $validate',
      'if ($default.argument -ne "-DYORADIO_ESP8266_SDK_RX_DIAG=OFF" -or $default.profile.sdk_rx_diag) { throw "Wrong default" }',
      'foreach ($diag in @($false, $true)) { foreach ($enabled in @($true, $false)) {',
      ' $ok = $true',
      ' try { $value = & $validate -Diagnostic:$diag -SdkRxDiag:$enabled } catch { $ok = $false; if ($_.Exception.Message -ne "-SdkRxDiag requires -Diagnostic") { throw } }',
      ' if ($ok -ne ($diag -or -not $enabled)) { throw "Wrong guard" }',
      ' if ($ok) {',
      '  $expected = if ($enabled) { "ON" } else { "OFF" }',
      '  if ($value.argument -ne "-DYORADIO_ESP8266_SDK_RX_DIAG=$expected") { throw "Wrong CMake argument" }',
      '  if ($value.profile.sdk_rx_diag -isnot [bool] -or $value.profile.sdk_rx_diag -ne $enabled) { throw "Wrong manifest" }',
      ' }',
      '}}',
      'Write-Output "SDK RX profile PASS"',
    ].join('\n');
  const result = spawnSync(process.platform === 'win32' ? 'powershell.exe' : 'pwsh',
    ['-NoProfile', '-NonInteractive', '-Command', code], {encoding: 'utf8'});
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /SDK RX profile PASS/);
});
