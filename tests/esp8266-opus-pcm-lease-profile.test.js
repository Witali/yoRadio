const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
test('PCM lease build switch defaults off and requires diagnostic Opus',()=>{
  const text=fs.readFileSync(path.join(root,'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
  const prelude=text.slice(0,text.indexOf('$taskRoot ='));
  const script='$check = {\n'+prelude+'\nreturn [bool]$OpusPcmLeases\n}\n'+[
    '$ErrorActionPreference = "Stop"','if (& $check) { throw "Enabled by default" }',
    'foreach ($diag in @($false,$true)) { foreach ($opus in @($false,$true)) {',
    ' $ok=$true; try { $v=& $check -OpusPcmLeases -Diagnostic:$diag -EnableOpus:$opus } catch { $ok=$false }',
    ' if ($ok -ne ($diag -and $opus)) { throw "Wrong acceptance" }',
    ' if ($ok -and -not $v) { throw "Flag lost" }','}}'
  ].join('\n');
  const r=spawnSync(process.platform==='win32'?'powershell.exe':'pwsh',
    ['-NoProfile','-NonInteractive','-Command',script],{encoding:'utf8'});
  assert.equal(r.status,0,r.stdout+r.stderr);
  assert.match(text,/"-DYORADIO_OPUS_PCM_LEASES=\$taskOpusPcmLeases"/);
  assert.match(text,/opus_pcm_leases=\[bool\]\$OpusPcmLeases/);
});
test('actual Opus component CMake enforces lease diagnostic gate and definition',t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'opus-leases-cmake-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const text=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/components/opus_decoder/CMakeLists.txt'),'utf8');
  const prefix=['cmake_minimum_required(VERSION 3.13)','set(COMPONENT_LIB fake)',
    'function(idf_component_register)','endfunction()',
    'function(target_compile_options)','endfunction()',
    'function(target_compile_definitions)',
    ' if(ARGV2 STREQUAL "YORADIO_OPUS_PCM_LEASES=1")','  set(LEASE_DEFINITION ON PARENT_SCOPE)',' endif()',
    'endfunction()'].join('\n');
  const script=path.join(dir,'test.cmake');
  fs.writeFileSync(script,prefix+'\n'+text+'\nif(CONFIG_YORADIO_OGG_OPUS AND YORADIO_OPUS_PCM_LEASES AND NOT LEASE_DEFINITION)\n message(FATAL_ERROR "Missing lease definition")\nendif()\n');
  const bundled=path.join(root,'.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const cmake=process.platform==='win32'?bundled:'cmake';
  for(const diag of [0,1])for(const leases of [0,1]) {
    const r=spawnSync(cmake,['-DCONFIG_YORADIO_OGG_OPUS=1','-DYORADIO_ESP8266_DIAGNOSTIC='+diag,
      '-DYORADIO_OPUS_PCM_LEASES='+leases,'-P',script],{encoding:'utf8'});
    assert.equal(r.status===0,!leases||!!diag,r.stdout+r.stderr);
  }
});
