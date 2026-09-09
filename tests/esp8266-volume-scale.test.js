const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const zlib = require('node:zlib');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');
const read = name => fs.readFileSync(path.join(main, name), 'utf8');
const wsl = process.platform === 'win32';
const nativePath = f => wsl ? '/mnt/' + f[0].toLowerCase() + f.slice(2).replace(/\\/g, '/') : f;

test('real percent controls: all 101 levels, legacy saved values, boundaries, lock failures and no-op saves', () => {
  const source = read('radio_control.c');
  const controls = source.slice(source.indexOf('uint8_t radio_control_volume'),
                                source.indexOf('void radio_control_flush_pending'));
  const dir = fs.mkdtempSync(path.join(root, '.build/volume-percent-'));
  const fixture = fs.readFileSync(path.join(__dirname, 'native/esp8266_volume_scale_test.c'), 'utf8');
  fs.writeFileSync(path.join(dir, 'test.c'), fixture.replace('/* REAL_CONTROLS */', controls));
  const bin = path.join(dir, 'test');
  const args = ['-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined',
    '-I'+nativePath(main), nativePath(path.join(dir, 'test.c')), '-o', nativePath(bin)];
  let r = spawnSync(wsl ? 'wsl.exe' : 'cc', wsl ? ['--exec','gcc',...args] : args, {encoding:'utf8'});
  assert.equal(r.status, 0, r.stdout+r.stderr);
  r = spawnSync(wsl ? 'wsl.exe' : bin, wsl ? ['--exec',nativePath(bin)] : [], {encoding:'utf8'});
  assert.equal(r.status, 0, r.stdout+r.stderr);
});

test('shared real slider opts into percent only on capable firmware, before status replay', () => {
  const script = zlib.gunzipSync(fs.readFileSync(path.join(root,'yoRadio/data/www/script.js.gz'))).toString();
  const fn = script.slice(script.indexOf('function applyVolumeScale()'), script.indexOf('function applyPlayerCapabilities()'));
  for (const maximum of [undefined, 100, 254, 255, 0, NaN]) {
    const slider = {min:'0', max:'254', step:'any'};
    const context = {getId: id => id === 'volume' ? slider : null};
    if (maximum !== undefined) context.volumeMax = maximum;
    vm.runInNewContext(fn, context);
    context.applyVolumeScale();
    assert.equal(slider.max, maximum === 100 ? '100' : '254');
    assert.equal(slider.min, '0');
    assert.equal(slider.step, '1');
  }
  const absent = {getId: () => null};
  vm.runInNewContext(fn, absent);
  assert.doesNotThrow(() => absent.applyVolumeScale());
  assert.match(script, /function applyPlayerCapabilities\(\) \{\s*applyVolumeScale\(\)/);
  const install = script.slice(script.indexOf("fetchUiResource('player.html')"));
  assert.ok(install.indexOf('applyPlayerCapabilities();') < install.indexOf('initialPlayerStateReady();'));
  assert.match(read('web_service.c'), /var volumeMax=100/);
  assert.match(fs.readFileSync(path.join(root,'tools/build_esp8266_web_bundle.py'),'utf8'), /volumeMax=100/);
});

test('status and compact replies use percent; NVS and PCM retain the legacy gain scale', () => {
  const web = read('web_service.c');
  assert.match(web, /volume_to_percent\(status->volume\)/);
  assert.match(web, /\(unsigned\)radio_control_volume\(\)/);
  assert.doesNotMatch(web, /target - \(int\)native_audio_output_volume/);
  assert.match(read('persistent_settings.c'), /SETTINGS_VERSION 1U/);
  assert.match(read('persistent_settings.c'), /settings->volume = 160/);
  assert.match(read('native_audio_output.c'), /VOLUME_DENOMINATOR 254U/);
  assert.doesNotMatch(read('native_audio_output.c'), /volume_from_percent|volume_to_percent/);
  assert.match(read('input_service.c'), /radio_control_adjust_volume\(event.delta \* settings.volume_steps\)/);
});

test('actual WebSocket volume command clamps both ends and rejects malformed input without changing gain', () => {
  const web = read('web_service.c');
  const start = web.indexOf('        httpd_trace_volume_begin();', web.indexOf('strcmp(command, "volume")'));
  const branch = web.slice(start, web.indexOf('    } else if (strcmp(command, "volp")', start));
  const dir = fs.mkdtempSync(path.join(root,'.build/volume-command-'));
  fs.writeFileSync(path.join(dir,'test.c'), `#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "volume_scale.h"
#define ESP_OK 0
static int target_value, errors, replies, busy;
static void httpd_trace_volume_begin(void) {}
static int radio_control_set_volume(int v) { if(busy) return -1; target_value=v; return 0; }
static void ws_send(void *r,const char *s) { (void)r; assert(strstr(s,"commandError")); errors++; }
static void send_current_volume(void *r) { (void)r; replies++; }
static void command(char *value) { void *request=NULL; ${branch} }
int main(void) {
  char text[32];
  for(int i=0;i<=100;i++) { sprintf(text,"%d",i); command(text); assert(target_value==i); }
  command("-1"); assert(target_value==0);
  command("101"); assert(target_value==100);
  command("9999999999999999999999999"); assert(target_value==100);
  command("-9999999999999999999999999"); assert(target_value==0);
  assert(replies==105 && errors==0);
  command(""); command("abc"); command("50junk"); command("50.5");
  assert(target_value==0 && replies==105 && errors==4);
  busy=1; command("75"); assert(target_value==0 && replies==105 && errors==5);
}
`.replace('#include <stdlib.h>', '#include <stdlib.h>\n#include <stdio.h>'));
  const bin=path.join(dir,'test');
  const args=['-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-I'+nativePath(main),nativePath(path.join(dir,'test.c')),'-o',nativePath(bin)];
  let r=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,{encoding:'utf8'});
  assert.equal(r.status,0,r.stdout+r.stderr);
  r=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',nativePath(bin)]:[],{encoding:'utf8'});
  assert.equal(r.status,0,r.stdout+r.stderr);
});
