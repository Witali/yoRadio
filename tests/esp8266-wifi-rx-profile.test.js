const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const source=fs.readFileSync(path.join(__dirname,'../tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
test('WiFi RX experiment validates both SDK settings without changing other defaults',()=>{
 assert.match(source,/\[int\]\$WifiRxBuffers = 14/);
 assert.match(source,/if \(\$WifiRxBuffers -ne 14 -and -not \$Diagnostic\)/);
 assert.ok(source.indexOf('Assert-TaskWifiRxConfig $taskConfig')<source.indexOf('Write-Output "Building'));
 const extract=n=>source.match(new RegExp('^function '+n+'\\([^]*?^}','m'))[0];
 const code=extract('Set-TaskWifiRxDefaults')+'\n'+extract('Assert-TaskWifiRxConfig')+`
$ErrorActionPreference='Stop'
$text="CONFIG_ESP8266_WIFI_RX_BUFFER_NUM=14\r\nCONFIG_ESP8266_WIFI_LEFT_CONTINUOUS_RX_BUFFER_NUM=14\r\nCONFIG_LWIP_TCP_MSS=536\r\n"
foreach($count in @(14,16)) {
 $candidate=Set-TaskWifiRxDefaults $text $count
 Assert-TaskWifiRxConfig $candidate $count
 Assert-TaskWifiRxConfig (Set-TaskWifiRxDefaults $candidate $count) $count
 if($candidate -notmatch 'CONFIG_LWIP_TCP_MSS=536'){throw 'Other setting changed'}
}
foreach($bad in @($text,($candidate+"CONFIG_ESP8266_WIFI_RX_BUFFER_NUM=16\n"))) {
 $rejected=$false;try {Assert-TaskWifiRxConfig $bad 16}catch{$rejected=$true}
 if(-not $rejected){throw 'Stale/duplicate cache accepted'}
}
$rejected=$false;try {Set-TaskWifiRxDefaults $text 12}catch{$rejected=$true}
if(-not $rejected){throw 'Invalid count accepted'}
Write-Output 'WiFi RX profile PASS'
`;
 const r=spawnSync(process.platform==='win32'?'powershell.exe':'pwsh',['-NoProfile','-NonInteractive','-Command',code],{encoding:'utf8'});
 assert.equal(r.status,0,r.stdout+r.stderr);assert.match(r.stdout,/WiFi RX profile PASS/);
});
