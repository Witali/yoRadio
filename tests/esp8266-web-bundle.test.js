const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const test=require('node:test'),vm=require('node:vm'),zlib=require('node:zlib');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const script=zlib.gunzipSync(fs.readFileSync(path.join(root,'yoRadio/data/www/script.js.gz'))).toString();
test('shared fragment loader uses preloaded content only when explicitly supplied',async()=>{
  const code=script.slice(script.indexOf('function fetchUiResource('),script.indexOf('const yoTitle'));
  const calls=[];
  const context={window:{},Response,Promise,Object,uiResource:p=>p+'?ui=test',fetch:(...a)=>{calls.push(a);return Promise.resolve(new Response('network'));}};
  vm.runInNewContext(code,context);
  assert.equal(await (await context.fetchUiResource('player.html')).text(),'network');
  assert.equal(calls[0][0],'player.html?ui=test');assert.equal(calls[0][1].cache,'no-store');
  context.window.yoUiAssets={'player.html':'same player'};
  assert.equal(await (await context.fetchUiResource('player.html')).text(),'same player');
  assert.equal(calls.length,1);
  assert.equal(await (await context.fetchUiResource('options.html')).text(),'network');
  assert.equal(calls.length,2);
});
test('generated gzip contains the exact common fragments and parseable common scripts',()=>{
  const dir=fs.mkdtempSync(path.join(root,'.build/web-bundle-'));
  const python=process.platform==='win32'?path.join(root,'.build/esp8266-python/Scripts/python.exe'):'python3';
  const header=path.join(dir,'generated.h'),gzip=path.join(dir,'player.html.gz');
  const build=spawnSync(python,[path.join(root,'tools/build_esp8266_web_bundle.py'),'--output',header,'--html-gzip',gzip],{encoding:'utf8'});
  assert.equal(build.status,0,build.stdout+build.stderr);
  const html=zlib.gunzipSync(fs.readFileSync(gzip)).toString();
  const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  assert.equal(scripts.length,3);
  for(const code of scripts) new vm.Script(code);
  assert.equal(scripts[1],script);
  assert.equal(scripts[2],zlib.gunzipSync(fs.readFileSync(path.join(root,'yoRadio/data/www/dragpl.js.gz'))).toString());
  const context={window:{},history:{replaceState(){}},location:{pathname:'/'}};
  vm.runInNewContext(scripts[0],context);
  for(const name of ['player.html','logo.svg']) assert.equal(context.window.yoUiAssets[name],zlib.gunzipSync(fs.readFileSync(path.join(root,'yoRadio/data/www',name+'.gz'))).toString());
  assert.equal(context.playMode,'player'); assert.equal(context.equalizerEnabled,false);
  const fnv=b=>{let h=2166136261;for(const v of b)h=Math.imul(h^v,16777619)>>>0;return h;};
  const generated=fs.readFileSync(header,'utf8');
  for(const name of ['theme.css','style.css','script.js','dragpl.js','player.html','logo.svg','options.html']) {
    const hash=fnv(fs.readFileSync(path.join(root,'yoRadio/data/www',name+'.gz'))).toString(16).padStart(8,'0');
    assert.ok(generated.includes(`{"/spiffs/www/${name}.gz", 0x${hash}U}`));
  }
  assert.doesNotMatch(html, /src="(?:variables|script|dragpl)\.js/);
  assert.ok(html.includes('id="content"') && html.includes('id="progress"'));
});
test('HTTP encoding selection respects integer qvalues, exclusions and wildcard',()=>{
  const dir=fs.mkdtempSync(path.join(root,'.build/web-encoding-'));
  const file=path.join(dir,'test.c'),bin=path.join(dir,'test');
  const header=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_encoding.h'),'utf8').replace('#pragma once','');
  fs.writeFileSync(file,header+`\n#include <assert.h>
int main(void) {
  assert(web_encoding_quality(NULL,"gzip")==1000);
  assert(web_encoding_quality("","gzip")==0);
  assert(web_encoding_quality("","identity")==1000);
  assert(web_encoding_quality("gzip, deflate, br","gzip")==1000);
  assert(web_encoding_quality("gzip;q=0, *;q=1","gzip")==0);
  assert(web_encoding_quality("*;q=0, gzip; q=0.125","gzip")==125);
  assert(web_encoding_quality("*;q=0, gzip;q=1","identity")==0);
  assert(web_encoding_quality("gzip;q=1, identity;q=0.5","identity")==500);
  assert(web_encoding_quality("GZIP;Q=1.000","gzip")==1000);
  assert(web_encoding_quality("gzip;q=0.000","gzip")==0);
  assert(web_encoding_quality("gzip;q=1.1","gzip")==0);
  assert(web_encoding_quality("gzip;q=0.1234","gzip")==0);
  assert(web_encoding_quality("gzip;q","gzip")==0);
  assert(web_encoding_quality("gzip;q=","gzip")==0);
  assert(web_encoding_quality("notgzip","gzip")==0);
}
`);
  const wsl=process.platform==='win32',p=f=>wsl?'/mnt/'+f[0].toLowerCase()+f.slice(2).replace(/\\/g,'/'):f;
  const options={encoding:'utf8'};
  const args=['-std=c11','-Wall','-Wextra','-Werror',p(file),'-o',p(bin)];
  const build=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,options);
  assert.equal(build.status,0,build.stdout+build.stderr);
  const run=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin)]:[],options);
  assert.equal(run.status,0,run.stdout+run.stderr);
});
test('bundle is validated before serving and invalidated by uploads, never used in AP mode',()=>{
  const web=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.c'),'utf8');
  assert.match(web,/s_bundle_current = bundle_matches_spiffs\(\)/);
  assert.match(web,/if \(s_bundle_current && network_service_connected\(\)/);
  assert.match(web,/web_service_notify_assets_changed\(void\)[\s\S]*?s_bundle_current = false/);
  const upload=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_upload.c'),'utf8');
  assert.match(upload,/if \(!u->wifi && !u->playlist\) web_service_notify_assets_changed\(\)/);
});
