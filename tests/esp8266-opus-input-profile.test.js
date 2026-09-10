const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
test('Opus input A/B keeps production default, gates changes and rejects stale cached input size',()=>{
  const source=fs.readFileSync(path.resolve(__dirname,'../tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
  assert.match(source,/\[ValidateSet\(1024, 1536, 2048, 3072, 4096\)\]\s*\[int\]\$OpusInputBytes = 1024/);
  assert.match(source,/if \(\$OpusInputBytes -ne 1024 -and \(-not \$Diagnostic -or -not \$EnableOpus\)\)/);
  assert.match(source,/CONFIG_YORADIO_OPUS_INPUT_BYTES=\$OpusInputBytes/);
  assert.match(source,/\$taskConfig -notmatch [^\n]*CONFIG_YORADIO_OPUS_INPUT_BYTES=\$OpusInputBytes[^\n]*throw 'Wrong cached Opus input size/);
  assert.match(source,/opus_input_bytes=\$\(if \(\$taskOpusEnabled\) \{ \$OpusInputBytes \} else \{ 0 \}\)/);
});
