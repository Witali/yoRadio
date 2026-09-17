const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
test('TCP out-of-order experiment is opt-in, diagnostic and cache-checked',()=>{
 assert.match(source,/\[switch\]\$NoTcpOutOfOrder/);
 assert.match(source,/if \(\$NoTcpOutOfOrder -and -not \$Diagnostic\)/);
 assert.match(source,/\$taskDefaults = Set-TaskTcpQueueDefaults \$taskDefaults \(\[bool\]\$NoTcpOutOfOrder\)/);
 assert.match(source,/tcp_queue_ooseq=\(-not \[bool\]\$NoTcpOutOfOrder\)/);
 assert.ok(source.indexOf('Assert-TaskTcpQueueConfig $taskConfig')<source.indexOf('Write-Output "Building'));
 assert.doesNotMatch(fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/sdkconfig.defaults'),'utf8'),/# CONFIG_LWIP_TCP_QUEUE_OOSEQ is not set/);
});
test('actual PowerShell helpers preserve unrelated settings and reject stale profiles',()=>{
 const extract=name=>{const m=source.match(new RegExp('^function '+name+'\\([^]*?^}','m'));assert.ok(m);return m[0]};
 const code=extract('Set-TaskTcpQueueDefaults')+'\n'+extract('Assert-TaskTcpQueueConfig')+`
$ErrorActionPreference='Stop'
$text="CONFIG_LWIP_TCP_QUEUE_OOSEQ=y\r\nCONFIG_YORADIO_OPUS_INPUT_BYTES=1024\r\nCONFIG_LWIP_TCP_MSS=536\r\n"
if ((Set-TaskTcpQueueDefaults $text $false) -cne $text) {throw 'Default changed'}
$off=Set-TaskTcpQueueDefaults $text $true
if ($off -match '(?m)^CONFIG_LWIP_TCP_QUEUE_OOSEQ=') {throw 'Still enabled'}
if ($off -notmatch 'CONFIG_YORADIO_OPUS_INPUT_BYTES=1024' -or $off -notmatch 'CONFIG_LWIP_TCP_MSS=536') {throw 'Unrelated options changed'}
$again=Set-TaskTcpQueueDefaults $off $true
if (([regex]::Matches($again,'# CONFIG_LWIP_TCP_QUEUE_OOSEQ is not set')).Count -ne 1) {throw 'Duplicate option'}
foreach ($enabled in @($false,$true)) {foreach ($disabled in @($false,$true)) {
 $config=if($enabled){$text}else{$off};$pass=$true
 try {Assert-TaskTcpQueueConfig $config $disabled} catch {$pass=$false}
 if ($pass -ne ($enabled -ne $disabled)) {throw 'Wrong cache guard'}
}}
Write-Output 'TCP profile PASS'
`;
 const run=spawnSync(process.platform==='win32'?'powershell.exe':'pwsh',['-NoProfile','-NonInteractive','-Command',code],{encoding:'utf8'});
 assert.equal(run.status,0,run.stdout+run.stderr);assert.match(run.stdout,/TCP profile PASS/);
});
