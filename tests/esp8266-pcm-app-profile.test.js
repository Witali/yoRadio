const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
test('app PCM requires diagnostic queue, has no extra stack and is explicitly off by default',()=>{
 const s=fs.readFileSync(path.join(__dirname,'../tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
 const prefix=s.slice(0,s.indexOf('$taskRoot ='));
 const code='$check={\n'+prefix+'\nreturn [bool]$OpusPcmAppTask\n}\n'+[
  '$ErrorActionPreference="Stop"',
  'if (& $check -EnableOpus:$false) { throw "Wrong default" }',
  'foreach ($queue in @($false,$true)) { foreach ($diag in @($false,$true)) { foreach ($opus in @($false,$true)) {',
  ' $ok=$true; try { $value=& $check -OpusPcmAppTask -OpusPcmQueue:$queue -Diagnostic:$diag -EnableOpus:$opus } catch { $ok=$false }',
  ' if ($ok -ne ($queue -and $diag -and $opus)) { throw "Unsafe combination" }',
  ' if ($ok -and -not $value) { throw "Lost flag" }',
  '}}}'
 ].join('\n');
 const r=spawnSync(process.platform==='win32'?'powershell.exe':'pwsh',['-NoProfile','-NonInteractive','-Command',code],{encoding:'utf8'});
 assert.equal(r.status,0,r.stdout+r.stderr);
 assert.match(s,/taskOpusPcmAppTask = if \(\$OpusPcmAppTask\) \{ 'ON' \} else \{ 'OFF' \}/);
 assert.match(s,/"-DYORADIO_ESP8266_OPUS_PCM_APP_TASK=\$taskOpusPcmAppTask"/);
 assert.match(s,/opus_pcm_stack_bytes=\$\(if \(\$OpusPcmQueue -and -not \$OpusPcmAppTask\)/);
});
