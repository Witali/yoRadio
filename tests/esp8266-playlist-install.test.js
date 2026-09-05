const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const test = require('node:test');
const root = path.resolve(__dirname, '..');
test('actual playlist installer skips identical files and rolls back index failure', () => {
  const main = path.join(root,'esp8266/rtos-sdk-native/main');
  const src = fs.readFileSync(path.join(main,'playlist_service.c'),'utf8');
  const code = src.slice(src.indexOf('static esp_err_t rebuild_locked(void);'),
    src.indexOf('static bool has_unsupported_extension'));
  const helper = fs.readFileSync(path.join(main,'file_replace.h'),'utf8').replace('#pragma once','');
  const fixture = fs.readFileSync(path.join(__dirname,'native/esp8266_playlist_install_test.c'),'utf8');
  const directory = fs.mkdtempSync(path.join(root,'.build/playlist-install-test-'));
  const source=path.join(directory,'test.c'), binary=path.join(directory,'test');
  fs.writeFileSync(source, fixture.replace('/* FILE_HELPERS */',helper).replace('/* INSTALLER */',code));
  const windows=process.platform==='win32';
  const hostPath=p=>windows?'/mnt/'+p[0].toLowerCase()+p.slice(2).replace(/\\/g,'/'):p;
  const args=['-std=c11','-Wall','-Wextra','-Werror',hostPath(source),'-o',hostPath(binary)];
  const build=spawnSync(windows?'wsl.exe':'cc',windows?['--exec','gcc',...args]:args,{encoding:'utf8'});
  assert.equal(build.status,0,build.stdout+build.stderr);
  const run=spawnSync(windows?'wsl.exe':binary,windows?['--exec',hostPath(binary)]:[],{cwd:directory,encoding:'utf8'});
  assert.equal(run.status,0,run.stdout+run.stderr);
  assert.match(run.stdout,/Playlist install tests passed/);
});
