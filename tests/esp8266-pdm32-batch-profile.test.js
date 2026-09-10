const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const builder = fs.readFileSync(path.join(root, 'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), 'utf8');

test('short loan profile validates diagnostics and resets the production limit to 512', () => {
  const prelude = builder.slice(0, builder.indexOf('$taskRoot ='));
  const code = '$check = {\n' + prelude + '\nreturn $Pdm32LoanWords\n}\n' + [
    '$ErrorActionPreference = "Stop"',
    'if ((& $check) -ne 512) { throw "Wrong default" }',
    'foreach ($n in @(64,128,256,512)) {',
    ' if ((& $check -Diagnostic -Pdm32LoanWords $n) -ne $n) { throw "Wrong limit" }',
    ' $accepted = $true; try { $null = & $check -Pdm32LoanWords $n } catch { $accepted = $false }',
    ' if ($accepted -ne ($n -eq 512)) { throw "Wrong production acceptance" }',
    '}',
    '$accepted = $true; try { $null = & $check -Diagnostic -Pdm32LoanWords 0 } catch { $accepted = $false }',
    'if ($accepted) { throw "Accepted zero" }',
  ].join('\n');
  const result = spawnSync(process.platform === 'win32' ? 'powershell.exe' : 'pwsh',
    ['-NoProfile','-NonInteractive','-Command',code], {encoding:'utf8'});
  assert.equal(result.status,0,result.stdout + result.stderr);
  assert.match(builder,/"-DYORADIO_ESP8266_PDM32_LOAN_WORDS=\$Pdm32LoanWords"/);
  assert.match(builder,/pdm32_loan_words=\$Pdm32LoanWords/);
});

test('PDM32 batch builder switch is diagnostic-only, independent of IRAM, and explicitly resets CMake/manifest', t => {
  const shell = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
  const available = spawnSync(shell, ['-NoProfile', '-Command', '$PSVersionTable.PSVersion.Major'], { encoding: 'utf8' });
  if (available.error?.code === 'ENOENT') return t.skip('PowerShell unavailable');
  assert.equal(available.status, 0, available.stderr);
  const prelude = builder.slice(0, builder.indexOf('$taskRoot ='));
  const assignment = builder.match(/^\s*\$taskPdm32Batch = if \(\$Pdm32Batch\) \{ 'ON' \} else \{ 'OFF' \}/m)?.[0];
  const argument = builder.match(/"-DYORADIO_ESP8266_PDM32_BATCH=\$taskPdm32Batch"/)?.[0];
  const manifest = builder.match(/^\s*pdm32_batch=\[bool\]\$Pdm32Batch/m)?.[0];
  assert.ok(assignment && argument && manifest);
  assert.equal((builder.match(/-DYORADIO_ESP8266_PDM32_BATCH=/g) || []).length, 1);
  const code = '$validate = {\n' + prelude + '\n' + assignment + '\n' +
    '$profile = [ordered]@{\n' + manifest + '\n}\n' +
    'return [pscustomobject]@{ argument = ' + argument + '; profile = ($profile | ConvertTo-Json | ConvertFrom-Json) }\n}\n' + [
    "$ErrorActionPreference = 'Stop'",
    '$default = & $validate',
    'if ($default.argument -ne "-DYORADIO_ESP8266_PDM32_BATCH=OFF" -or $default.profile.pdm32_batch) { throw "Default is not OFF" }',
    '$cases = 0',
    'foreach ($diag in @($false, $true)) { foreach ($batch in @($true, $false)) { foreach ($iram in @($false, $true)) {',
    '  $ok = $true; $reason = ""',
    '  try { $value = & $validate -Diagnostic:$diag -Pdm32Batch:$batch -Pdm32Iram:$iram } catch { $ok = $false; $reason = $_.Exception.Message }',
    '  if ($ok -ne ($diag -or -not ($batch -or $iram))) { throw "Wrong acceptance: $diag/$batch/$iram" }',
    '  if (-not $ok -and -not $iram -and $reason -ne "-Pdm32Batch requires -Diagnostic until board qualification") { throw "Wrong validation: $reason" }',
    '  if ($ok) {',
    '    $expected = if ($batch) { "ON" } else { "OFF" }',
    '    if ($value.argument -ne "-DYORADIO_ESP8266_PDM32_BATCH=$expected") { throw "Missing explicit CMake selection" }',
    '    if ($value.profile.pdm32_batch -isnot [bool] -or $value.profile.pdm32_batch -ne $batch) { throw "Wrong manifest" }',
    '  }',
    '  ++$cases',
    '}}}',
    'if ($cases -ne 8) { throw "Missing combinations" }',
    'Write-Output "PDM32 batch profile PASS: default and 8 combinations, including ON then OFF"',
  ].join('\n');
  const result = spawnSync(shell, ['-NoProfile', '-NonInteractive', '-Command', code], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /PDM32 batch profile PASS/);
});
