const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), 'utf8');

test('cache-off is Opus-only, opt-in and recorded from the effective configuration', () => {
  assert.match(source, /\[switch\]\$NoSpiffsCache/);
  assert.match(source, /if \(\$NoSpiffsCache -and -not \$EnableOpus\) \{ throw '-NoSpiffsCache requires -EnableOpus' \}/);
  assert.match(source, /\$taskDefaults = Set-TaskSpiffsCacheDefaults \$taskDefaults \(\[bool\]\$NoSpiffsCache\)/);
  assert.match(source, /\$taskSpiffsCache = Get-TaskSpiffsCacheProfile \$taskConfig \(\[bool\]\$NoSpiffsCache\)/);
  assert.ok(source.indexOf('$taskSpiffsCache = Get-TaskSpiffsCacheProfile') < source.indexOf('Write-Output "Building'));
  assert.match(source, /spiffs_cache=\[bool\]\$taskSpiffsCache.enabled/);
  assert.match(source, /spiffs_write_cache=\[bool\]\$taskSpiffsCache.write_enabled/);
  assert.doesNotMatch(source, /max_files\s*=/);
  const defaults = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/sdkconfig.defaults'), 'utf8');
  assert.doesNotMatch(defaults, /# CONFIG_SPIFFS_CACHE is not set|CONFIG_SPIFFS_CACHE=n/);
  assert.match(fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/storage_service.c'), 'utf8'), /\.max_files = 5/);
});

test('actual PowerShell cache helpers preserve defaults and reject stale configurations', t => {
  const command = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
  const available = spawnSync(command, ['-NoProfile', '-NonInteractive', '-Command', '$PSVersionTable.PSVersion.Major'], {encoding:'utf8'});
  if (available.error?.code === 'ENOENT') return t.skip('PowerShell unavailable');
  assert.equal(available.status, 0, available.stderr);
  const extract = name => {
    const match = source.match(new RegExp('^function ' + name + '\\([^]*?^}', 'm'));
    assert.ok(match, name);
    return match[0];
  };
  // Execute only these pure functions, never the builder, filesystem or SDK.
  const code = extract('Set-TaskSpiffsCacheDefaults') + '\n' + extract('Get-TaskSpiffsCacheProfile') + `
$ErrorActionPreference = 'Stop'
$inputText = "CONFIG_SPIFFS_PAGE_SIZE=256\r\nCONFIG_SPIFFS_CACHE=y\r\nCONFIG_SPIFFS_CACHE_WR=y\r\nCONFIG_OTHER=y\r\n"
if ((Set-TaskSpiffsCacheDefaults $inputText $false) -cne $inputText) { throw 'Default mutated' }
$off = Set-TaskSpiffsCacheDefaults $inputText $true
if ($off -match '(?m)^CONFIG_SPIFFS_CACHE(?:_WR)?=') { throw 'Enabled entry retained' }
if ($off -notmatch '(?m)^CONFIG_SPIFFS_PAGE_SIZE=256' -or $off -notmatch '(?m)^CONFIG_OTHER=y') { throw 'Unrelated config lost' }
$again = Set-TaskSpiffsCacheDefaults $off $true
if (($again | Select-String -Pattern '# CONFIG_SPIFFS_CACHE is not set' -AllMatches).Matches.Count -ne 1) { throw 'Duplicate cache option' }
$cases = 0
foreach ($read in @($false, $true)) { foreach ($write in @($false, $true)) { foreach ($disabled in @($false, $true)) {
  $config = ''
  if ($read) { $config += "CONFIG_SPIFFS_CACHE=y\r\n" }
  if ($write) { $config += "CONFIG_SPIFFS_CACHE_WR=y\r\n" }
  $accepted = $true
  try { $result = Get-TaskSpiffsCacheProfile $config $disabled } catch { $accepted = $false }
  $expected = ($read -ne $disabled) -and ($write -eq $read)
  if ($accepted -ne $expected) { throw "Wrong guard: $read/$write/$disabled" }
  if ($accepted -and (($result.enabled -ne $read) -or ($result.write_enabled -ne $write))) { throw 'Wrong manifest flags' }
  ++$cases
}}}
Write-Output "cache profile PASS: $cases combinations"
`;
  const run = spawnSync(command, ['-NoProfile', '-NonInteractive', '-Command', code], {encoding:'utf8'});
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(run.stdout, /cache profile PASS: 8 combinations/);
});
