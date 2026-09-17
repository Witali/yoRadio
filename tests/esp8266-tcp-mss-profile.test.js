const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const source=fs.readFileSync(path.join(__dirname,'../tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
test('full MSS is diagnostic only with verified two-MSS send/receive windows',()=>{
 assert.match(source,/if \(\$TcpFullMss -and -not \$Diagnostic\)/);
 assert.match(source,/tcp_full_mss=\[bool\]\$TcpFullMss/);
 assert.ok(source.indexOf('Assert-TaskTcpFullMssConfig $taskConfig')<source.indexOf('Write-Output "Building'));
 const extract=n=>{const m=source.match(new RegExp('^function '+n+'\\([^]*?^}','m'));assert.ok(m);return m[0]};
 const code=extract('Set-TaskTcpFullMssDefaults')+'\n'+extract('Assert-TaskTcpFullMssConfig')+`
$ErrorActionPreference='Stop'
$text="CONFIG_LWIP_TCP_MSS=536\r\nCONFIG_LWIP_TCP_SND_BUF_DEFAULT=2440\r\nCONFIG_LWIP_TCP_WND_DEFAULT=2440\r\nCONFIG_LWIP_TCP_QUEUE_OOSEQ=y\r\n"
if ((Set-TaskTcpFullMssDefaults $text $false) -cne $text) {throw 'Default changed'}
$full=Set-TaskTcpFullMssDefaults $text $true
Assert-TaskTcpFullMssConfig $text $false
Assert-TaskTcpFullMssConfig $full $true
Assert-TaskTcpFullMssConfig (Set-TaskTcpFullMssDefaults $full $true) $true
if ($full -notmatch 'CONFIG_LWIP_TCP_QUEUE_OOSEQ=y') {throw 'Unrelated setting changed'}
foreach ($bad in @($text,($full.Replace('WND_DEFAULT=2920','WND_DEFAULT=2440')),($full+"CONFIG_LWIP_TCP_MSS=1460\n"))) {
 $rejected=$false;try {Assert-TaskTcpFullMssConfig $bad $true} catch {$rejected=$true}
 if(-not $rejected){throw 'Stale or duplicate setting accepted'}
}
Write-Output 'MSS profile PASS'
`;
 const r=spawnSync(process.platform==='win32'?'powershell.exe':'pwsh',['-NoProfile','-NonInteractive','-Command',code],{encoding:'utf8'});
 assert.equal(r.status,0,r.stdout+r.stderr);assert.match(r.stdout,/MSS profile PASS/);
});
