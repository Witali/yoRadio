const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),main=path.join(root,'esp8266/rtos-sdk-native/main');
const wsl=process.platform==='win32',p=f=>wsl?'/mnt/'+f[0].toLowerCase()+f.slice(2).replace(/\\/g,'/'):f;
test('actual flash cache validates source and body, rebuilds stale data, reuses unchanged files',()=>{
  const dir=fs.mkdtempSync(path.join(root,'.build/playlist-web-cache-'));
  const csv=path.join(dir,'playlist.csv'),cache=csv+'.web.gz',output=path.join(dir,'served.gz'),bin=path.join(dir,'cache-test');
  fs.copyFileSync(path.join(main,'playlist_web_cache.c'),path.join(dir,'cache.c'));
  fs.writeFileSync(path.join(dir,'sdkconfig.h'),'#define CONFIG_YORADIO_PLAYLIST_WEB_GZIP 1\n');
  fs.writeFileSync(path.join(dir,'playlist_service.h'),`#include <stdbool.h>\n#define PLAYLIST_PATH ${JSON.stringify(p(csv))}\nbool playlist_service_entry_supported(char *line);\n`);
  fs.writeFileSync(path.join(dir,'esp_log.h'),'#include <stdio.h>\n#define ESP_LOGI(tag,...) do { (void)(tag); fprintf(stderr,__VA_ARGS__); fputc(10,stderr); } while(0)\n#define ESP_LOGW ESP_LOGI\n');
  const service=fs.readFileSync(path.join(main,'playlist_service.c'),'utf8');
  const filter=service.slice(service.indexOf('static bool has_unsupported_extension('),service.indexOf('static bool parse_line('));
  fs.writeFileSync(path.join(dir,'test.c'),`#include <stdio.h>\n#include <string.h>\n#include <stdbool.h>\n#include <stdlib.h>\n#include <assert.h>\n#include <unistd.h>\n#include "playlist_web_cache.h"\n${filter}\nint main(int argc,char **argv){
    assert(argc==2); playlist_web_cache_refresh(); size_t size; int fd=playlist_web_cache_open(&size);
    if(fd<0){return 2;} FILE *out=fopen(argv[1],"wb");assert(out); unsigned char buf[333];size_t total=0;ssize_t n;
    while((n=read(fd,buf,sizeof(buf)))>0){assert(fwrite(buf,1,n,out)==(size_t)n);total+=n;}
    assert(n==0&&total==size);fclose(out);close(fd);playlist_web_cache_invalidate();assert(playlist_web_cache_open(&size)<0);return 0;}
  `);
  const args=['-std=c11','-D_POSIX_C_SOURCE=200809L','-O2','-Wall','-Wextra','-Werror','-fsanitize=undefined',
    '-I'+p(dir),'-I'+p(main),p(path.join(dir,'test.c')),p(path.join(dir,'cache.c')),p(path.join(main,'small_gzip.c')),'-o',p(bin)];
  const opts={encoding:'utf8'};
  const build=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,opts);
  assert.equal(build.status,0,build.stdout+build.stderr);
  const run=()=>spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin),p(output)]:[p(output)],opts);
  const supported=Array.from({length:600},(_,i)=>`Радио ${i}\thttp://radio.example:8000/${i}.mp3\t0\r\n`).join('');
  fs.writeFileSync(csv,supported+'Skip\thttps://radio.example/a.mp3\t0\nSkip\thttp://host/a.ogg\t0\n');
  let r=run();assert.equal(r.status,0,r.stderr);assert.match(r.stderr,/Built gzip/);
  assert.deepEqual(zlib.gunzipSync(fs.readFileSync(output)),Buffer.from(supported));
  const first=fs.readFileSync(cache),time=fs.statSync(cache).mtimeMs;
  r=run();assert.equal(r.status,0,r.stderr);assert.match(r.stderr,/Validated gzip/);
  assert.equal(fs.statSync(cache).mtimeMs,time);assert.deepEqual(fs.readFileSync(cache),first);
  // Same-length content replacement cannot leave a stale cache.
  const next=fs.readFileSync(csv,'utf8').replace(/radio.example/g,'other.example');fs.writeFileSync(csv,next);
  r=run();assert.equal(r.status,0,r.stderr);assert.match(r.stderr,/Built gzip/);
  assert.deepEqual(zlib.gunzipSync(fs.readFileSync(output)),Buffer.from(supported.replace(/radio.example/g,'other.example')));
  // Truncated and silently corrupted cache bodies are rebuilt.
  fs.writeFileSync(cache,fs.readFileSync(cache).subarray(0,80));
  r=run();assert.equal(r.status,0,r.stderr);assert.match(r.stderr,/Built gzip/);
  const damaged=fs.readFileSync(cache);damaged[45]^=128;fs.writeFileSync(cache,damaged);
  r=run();assert.equal(r.status,0,r.stderr);assert.match(r.stderr,/Built gzip/);
  // Interrupted replacement recovers a valid previous copy without rewriting it.
  fs.renameSync(cache,cache+'.bak');r=run();assert.equal(r.status,0,r.stderr);assert.match(r.stderr,/Validated gzip/);
  // Small/incompressible lists and inability to create a temp file fall back,
  // without changing the canonical source or accepting an older gzip body.
  fs.writeFileSync(csv,'Radio\thttp://x\t0\n');const small=fs.readFileSync(csv);
  r=run();assert.equal(r.status,2,r.stderr);assert.deepEqual(fs.readFileSync(csv),small);
  fs.mkdirSync(cache+'.tmp');fs.writeFileSync(csv,supported);r=run();assert.equal(r.status,2,r.stderr);
  assert.deepEqual(fs.readFileSync(csv),Buffer.from(supported));
});
test('disabled cache needs no compressor or cache object code',()=>{
  const dir=fs.mkdtempSync(path.join(root,'.build/playlist-web-off-'));
  fs.writeFileSync(path.join(dir,'sdkconfig.h'),'/* option disabled */\n');
  fs.writeFileSync(path.join(dir,'test.c'),'#include "playlist_web_cache.h"\nint main(void){size_t n=0;playlist_web_cache_refresh();playlist_web_cache_invalidate();return playlist_web_cache_open(&n)==-1?0:1;}\n');
  const bin=path.join(dir,'test'),opts={encoding:'utf8'};
  const args=['-std=c11','-Wall','-Wextra','-Werror','-I'+p(dir),'-I'+p(main),p(path.join(dir,'test.c')),'-o',p(bin)];
  const build=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,opts);assert.equal(build.status,0,build.stderr);
  const run=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin)]:[],opts);assert.equal(run.status,0,run.stderr);
  const cmake=fs.readFileSync(path.join(main,'CMakeLists.txt'),'utf8');
  assert.match(cmake,/if\(CONFIG_YORADIO_PLAYLIST_WEB_GZIP\)\s*list\(APPEND YORADIO_SOURCES "playlist_web_cache.c" "small_gzip.c"\)\s*endif\(\)/);
});
test('playlist upload rebuilds cache under the same lock; requests never compress',()=>{
  const service=fs.readFileSync(path.join(main,'playlist_service.c'),'utf8');
  const install=service.slice(service.indexOf('esp_err_t playlist_service_install('),service.indexOf('static bool has_unsupported_extension('));
  assert.ok(install.indexOf('playlist_web_cache_invalidate()')<install.indexOf('rename(temporary, PLAYLIST_PATH)'));
  assert.match(install,/if \(result == ESP_OK\) playlist_web_cache_refresh\(\);\s*xSemaphoreGive\(s_lock\)/);
  const web=fs.readFileSync(path.join(main,'web_service.c'),'utf8');
  assert.ok(web.includes('playlist_web_cache_open(&left)'));assert.ok(!web.includes('small_gzip_feed'));
});
