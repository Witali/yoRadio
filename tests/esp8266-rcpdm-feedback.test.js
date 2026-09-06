const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {execute}=require('../tools/esp8266_audio_profile/run_rcpdm_radio');
const root=path.resolve(__dirname,'..');
test('RCPDM feedback preserves fractional PCM, state bounds and chunk continuity',t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rcpdm-feedback-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const exe=path.join(dir,'test'+(process.platform==='win32'?'.exe':''));
  const source=path.join(root,'tests/native/rcpdm_feedback_test.cpp');
  const includes=[path.join(root,'tests/native'),path.join(root,'esp8266/rtos-sdk-native/main')];
  if(process.platform==='win32'){
    let vc;const base='C:/Program Files/Microsoft Visual Studio';
    for(const v of fs.readdirSync(base))for(const e of fs.readdirSync(path.join(base,v))){
      const p=path.join(base,v,e,'VC/Auxiliary/Build/vcvars64.bat');if(fs.existsSync(p))vc=p;
    }
    assert.ok(vc,'MSVC required');
    const cmd=path.join(dir,'build.cmd');
    fs.writeFileSync(cmd,`@call "${vc}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c++17 /O2 /EHsc /W4 ${includes.map(p=>`/I"${p}"`).join(' ')} "${source}" /Fe:"${exe}"\r\n`);
    execute('cmd.exe',['/d','/c',cmd],{cwd:dir});
  }else execute('c++',['-std=c++17','-O2','-fsanitize=undefined',...includes.map(p=>`-I${p}`),source,'-o',exe],{cwd:dir});
  const result=JSON.parse(execute(exe,[]).stdout);
  assert.equal(result.pass,true);assert.equal(result.state_bytes,16);assert.equal(result.batch_cases,16);
  assert.ok(result.word_state_frames>300000);t.diagnostic(JSON.stringify(result));
});
