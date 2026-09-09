const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
test('HTTP startup and URI allocation failures release every owned resource',t=>{
  const base=path.resolve(__dirname,'../esp8266/rtos-sdk-native/components/esp_http_server/src');
  function section(file,start,end) {
    const s=fs.readFileSync(path.join(base,file),'utf8');const a=s.indexOf(start),b=s.indexOf(end,a);
    assert.ok(a>=0&&b>a);return s.slice(a,b);
  }
  const uri=section('httpd_uri.c','static int httpd_find_uri_handler(', 'esp_err_t httpd_unregister_uri_handler(')+
    section('httpd_uri.c','void httpd_unregister_all_uri_handlers(', '/* Alternate implmentation');
  const start=section('httpd_main.c','esp_err_t httpd_start(', 'esp_err_t httpd_stop(');
  const code=fs.readFileSync(path.join(__dirname,'native/esp8266_http_allocation_test.c'),'utf8')
    .replace('/* URI_IMPLEMENTATION */',uri).replace('/* START_IMPLEMENTATION */',start);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'yoradio-http-allocation-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const source=path.join(dir,'test.c'),exe=path.join(dir,process.platform==='win32'?'test.exe':'test');
  fs.writeFileSync(source,code);let build;
  if(process.platform==='win32') {
    const base='C:/Program Files/Microsoft Visual Studio';let vc;
    if(fs.existsSync(base))for(const v of fs.readdirSync(base))for(const e of fs.readdirSync(path.join(base,v))) {
      const p=path.join(base,v,e,'VC/Auxiliary/Build/vcvars64.bat');if(fs.existsSync(p))vc=p;
    }
    if(!vc)return t.skip('Visual C++ unavailable');
    const batch=path.join(dir,'build.cmd');
    fs.writeFileSync(batch,`@call "${vc}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c11 /W4 /WX "${source}" /Fe:"${exe}"\r\n`);
    build=spawnSync('cmd.exe',['/d','/c',batch],{cwd:dir,encoding:'utf8',timeout:60000});
  }else{
    build=spawnSync('cc',['-std=c11','-Wall','-Wextra','-Werror',source,'-o',exe],{cwd:dir,encoding:'utf8',timeout:60000});
    if(build.error?.code==='ENOENT')return t.skip('C compiler unavailable');
  }
  assert.equal(build.status,0,build.stdout+'\n'+build.stderr);
  const run=spawnSync(exe,[],{encoding:'utf8',timeout:10000});
  assert.equal(run.status,0,run.stdout+'\n'+run.stderr);
  assert.match(run.stdout,/HTTP allocation cleanup tests passed/);
});
