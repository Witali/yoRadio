const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
test('build timeout is explicit, bounded, repeatable and checked against cached sdkconfig',t=>{
  const source=fs.readFileSync(path.join(__dirname,'../tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
  assert.match(source,/\[int\]\$StreamIdleTimeoutMs = 1000/);
  assert.match(source,/Assert-TaskStreamIdleConfig \$taskConfig \$StreamIdleTimeoutMs/);
  assert.match(source,/stream_idle_timeout_ms=\$StreamIdleTimeoutMs/);
  const start=source.indexOf('function Set-TaskStreamIdleDefaults('),end=source.indexOf('Push-Location $taskRoot',start);
  assert.ok(start>=0&&end>start);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'yoradio-idle-profile-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const file=path.join(dir,'check.ps1');
  fs.writeFileSync(file,source.slice(start,end)+`
$ErrorActionPreference='Stop'
$text="CONFIG_OTHER=1\r\nCONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS=999\r\n"
foreach($ms in @(250,1000,3000,60000,1000)) {
  $text=Set-TaskStreamIdleDefaults $text $ms
  Assert-TaskStreamIdleConfig $text $ms
  if($text -notmatch 'CONFIG_OTHER=1'){throw 'Unrelated option lost'}
  $caught=$false
  try { Assert-TaskStreamIdleConfig $text ($ms+1) } catch { $caught=$true }
  if(-not $caught){throw 'Stale timeout accepted'}
}
foreach($ms in @(249,60001)) {
  $caught=$false
  try { Set-TaskStreamIdleDefaults $text $ms } catch { $caught=$true }
  if(-not $caught){throw 'Invalid timeout accepted'}
}
Write-Output 'timeout profile PASS'
`);
  const r=spawnSync(process.platform==='win32'?'powershell.exe':'pwsh',['-NoProfile','-ExecutionPolicy','Bypass','-File',file],{encoding:'utf8'});
  if(r.error?.code==='ENOENT')return t.skip('PowerShell not installed');
  assert.equal(r.status,0,r.stdout+r.stderr);assert.match(r.stdout,/timeout profile PASS/);
});
