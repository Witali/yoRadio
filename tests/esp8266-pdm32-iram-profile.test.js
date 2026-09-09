const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const builder = fs.readFileSync(path.join(root, 'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), 'utf8');

test('PDM32 IRAM builder switch is opt-in, diagnostic-only, and explicitly clears CMake cache', t => {
  const shell = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
  const available = spawnSync(shell, ['-NoProfile', '-Command', '$PSVersionTable.PSVersion.Major'], {encoding:'utf8'});
  if (available.error?.code === 'ENOENT') return t.skip('PowerShell unavailable');
  assert.equal(available.status, 0, available.stderr);
  const prelude = builder.slice(0, builder.indexOf('$taskRoot ='));
  const code = '$validate = {\n' + prelude + '\nreturn [bool]$Pdm32Iram\n}\n' + [
    "$ErrorActionPreference = 'Stop'",
    "if (& $validate) { throw 'Default must be OFF' }",
    'foreach ($diag in @($false, $true)) { foreach ($enabled in @($false, $true)) {',
    '  $ok = $true',
    '  try { $value = & $validate -Diagnostic:$diag -Pdm32Iram:$enabled } catch { $ok = $false }',
    '  if ($ok -ne (-not $enabled -or $diag)) { throw "Wrong acceptance $diag/$enabled" }',
    '  if ($ok -and $value -ne $enabled) { throw "Wrong value $diag/$enabled" }',
    '}}',
    "Write-Output 'PDM32 profile PASS'",
  ].join('\n');
  const result = spawnSync(shell, ['-NoProfile', '-NonInteractive', '-Command', code], {encoding:'utf8'});
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /PDM32 profile PASS/);
  assert.match(builder, /\$taskPdm32Iram = if \(\$Pdm32Iram\) \{ 'ON' \} else \{ 'OFF' \}/);
  assert.match(builder, /-DYORADIO_ESP8266_PDM32_IRAM=\$taskPdm32Iram/);
  assert.match(builder, /pdm32_iram=\[bool\]\$Pdm32Iram/);
});
