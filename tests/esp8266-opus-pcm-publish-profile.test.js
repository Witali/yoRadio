const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
test('Opus PCM publication is explicit, diagnostic-only and defaults off',()=>{
  const builder=read('tools/esp8266_audio_profile/build_i2s_pdm_production.ps1');
  const prelude=builder.slice(0,builder.indexOf('$taskRoot ='));
  const code='$check = {\n'+prelude+'\nreturn [bool]$OpusPcmPublish\n}\n'+[
    '$ErrorActionPreference = "Stop"',
    'if (& $check) { throw "Enabled by default" }',
    'foreach ($diag in @($false,$true)) { foreach ($opus in @($false,$true)) {',
    ' $ok=$true; try { $value=& $check -OpusPcmPublish -Diagnostic:$diag -EnableOpus:$opus } catch { $ok=$false }',
    ' if ($ok -ne ($diag -and $opus)) { throw "Wrong acceptance" }',
    ' if ($ok -and -not $value) { throw "Flag lost" }',
    '}}',
  ].join('\n');
  const r=spawnSync(process.platform==='win32'?'powershell.exe':'pwsh',['-NoProfile','-NonInteractive','-Command',code],{encoding:'utf8'});
  assert.equal(r.status,0,r.stdout+r.stderr);
  assert.match(builder,/\$taskOpusPcmPublish = if \(\$OpusPcmPublish\) \{ 'ON' \} else \{ 'OFF' \}/);
  assert.match(builder,/"-DYORADIO_ESP8266_OPUS_PCM_PUBLISH=\$taskOpusPcmPublish"/);
  assert.match(builder,/opus_pcm_publish=\[bool\]\$OpusPcmPublish/);
  const cmake=read('esp8266/rtos-sdk-native/main/CMakeLists.txt');
  assert.match(cmake,/option\(YORADIO_ESP8266_OPUS_PCM_PUBLISH[\s\S]*?OFF\)/);
  assert.match(cmake,/YORADIO_ESP8266_OPUS_PCM_PUBLISH=\$<BOOL:/);
  const audio=read('esp8266/rtos-sdk-native/main/audio_service.c');
  assert.match(audio,/#if YORADIO_ESP8266_OPUS_PCM_PUBLISH\s+if \(result == ESP_OK && context->codec_kind == HELIX_CODEC_OPUS\)\s+result = native_audio_output_publish_pending\(\);\s+#endif/);
});
