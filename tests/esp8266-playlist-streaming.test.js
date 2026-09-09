const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const test = require('node:test');
const root = path.resolve(__dirname, '..');
for (const opus of [0, 1]) {
test('actual buffered playlist handler preserves filtered rows across buffer boundaries, Opus=' + opus, () => {
  const web = fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.c'),'utf8');
  const handler = web.slice(web.indexOf('static esp_err_t playlist_handler('),web.indexOf('static esp_err_t status_handler('));
  const playlist = fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/playlist_service.c'),'utf8');
  const filter = playlist.slice(playlist.indexOf('static bool has_unsupported_extension('),playlist.indexOf('static bool parse_line('));
  const fixture = fs.readFileSync(path.join(__dirname,'native/esp8266_playlist_streaming_test.c'),'utf8');
  const dir = fs.mkdtempSync(path.join(root,'.build/playlist-streaming-'));
  const source = path.join(dir,'test.c'), binary=path.join(dir,'test');
  const scratch=Number(web.match(/#define WEB_STATIC_SCRATCH_SIZE (\d+)U/)[1]);
  assert.ok(scratch<=1024,'Keep the output workspace bounded to 1 KiB');
  const encoding=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_encoding.h'),'utf8').replace('#pragma once','');
  const shared = web.slice(web.indexOf('static union {'), web.indexOf('static bool s_bundle_current;'));
  const header = fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.h'),'utf8');
  const uploadSize = Number(header.match(/#define WEB_UPLOAD_RECEIVE_BYTES (\d+)U/)[1]);
  const defines = `#define WEB_STATIC_SCRATCH_SIZE ${scratch}\n#define WEB_STATUS_CAPACITY 1088\n#define WEB_UPLOAD_RECEIVE_BYTES ${uploadSize}\n`;
  fs.writeFileSync(source,fixture.replace('/* SCRATCH_IMPLEMENTATION */',defines+shared).replace('/* IMPLEMENTATION */',encoding+'\n'+filter+'\n'+handler));
  const wsl=process.platform==='win32';
  const platformPath=p=>wsl?'/mnt/'+p[0].toLowerCase()+p.slice(2).replace(/\\/g,'/'):p;
  const options={encoding:'utf8'};
  const cc=['-std=c11','-D_POSIX_C_SOURCE=200809L','-DCONFIG_YORADIO_OGG_OPUS='+opus,'-Wall','-Wextra','-Werror','-fsanitize=address,undefined',platformPath(source),'-o',platformPath(binary)];
  const build=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...cc]:cc,options);
  assert.equal(build.status,0,build.stdout+build.stderr);
  const run=spawnSync(wsl?'wsl.exe':binary,wsl?['--exec',platformPath(binary),platformPath(path.join(dir,'playlist.csv'))]:[path.join(dir,'playlist.csv')],options);
  assert.equal(run.status,0,run.stdout+run.stderr);
  assert.match(run.stdout,/streaming playlist passed/);
});
}

test('Opus capability changes invalidate the persistent filtered index in both directions', () => {
  const source=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/playlist_service.c'),'utf8');
  assert.match(source, /#if CONFIG_YORADIO_OGG_OPUS\s+#define INDEX_VERSION 3U[^]*?#else\s+#define INDEX_VERSION 2U/);
  assert.match(source, /header.version == INDEX_VERSION/);
});
