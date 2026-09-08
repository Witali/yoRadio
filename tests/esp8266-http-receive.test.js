const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
test('actual HTTP receiver and upload loop preserve errno, partial reads and deadlines',t=>{
  const tx=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_txrx.c'),'utf8');
  const upload=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_upload.c'),'utf8');
  const fixture=fs.readFileSync(path.join(__dirname,'native/esp8266_http_receive_test.c'),'utf8');
  const code=fixture.replace('/* SOCKET_IMPLEMENTATION */',tx.slice(tx.indexOf('static int httpd_sock_err(')))
    .replace('/* BUFFER_IMPLEMENTATION */',tx.slice(tx.indexOf('int httpd_recv_with_opt('),tx.indexOf('static void httpd_async_wakeup(')))
    .replace('/* REQUEST_IMPLEMENTATION */',tx.slice(tx.indexOf('int httpd_req_recv('),tx.indexOf('int httpd_req_to_sockfd(')))
    .replace('/* FORM_IMPLEMENTATION */',upload.slice(upload.indexOf('static bool receive_form('),upload.indexOf('esp_err_t web_upload_handler(')));
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'yoradio-recv-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const source=path.join(dir,'test.c'),exe=path.join(dir,process.platform==='win32'?'test.exe':'test');
  fs.writeFileSync(source,code);
  let build;
  if(process.platform==='win32') {
    const base='C:/Program Files/Microsoft Visual Studio'; let vcvars;
    if(fs.existsSync(base))for(const v of fs.readdirSync(base))for(const e of fs.readdirSync(path.join(base,v))) {
      const p=path.join(base,v,e,'VC/Auxiliary/Build/vcvars64.bat'); if(fs.existsSync(p))vcvars=p;
    }
    if(!vcvars)return t.skip('Visual C++ build tools unavailable');
    const batch=path.join(dir,'build.cmd');
    fs.writeFileSync(batch,`@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c11 /W4 /WX "${source}" /Fe:"${exe}"\r\n`);
    build=spawnSync('cmd.exe',['/d','/c',batch],{cwd:dir,encoding:'utf8'});
  } else build=spawnSync('cc',['-std=c11','-Wall','-Wextra','-Werror',source,'-o',exe],{cwd:dir,encoding:'utf8'});
  assert.equal(build.status,0,build.stdout+'\n'+build.stderr);
  const run=spawnSync(exe,[],{encoding:'utf8'});
  assert.equal(run.status,0,run.stdout+'\n'+run.stderr);
  assert.match(run.stdout,/HTTP receive\/upload tests passed/);
  assert.doesNotMatch(tx.slice(tx.indexOf('static int httpd_sock_err(')),/getsockopt/);
});
