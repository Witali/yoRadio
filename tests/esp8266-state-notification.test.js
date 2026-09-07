const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const test=require('node:test'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const read=name=>fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main',name),'utf8');
test('actual native state wakes its consumer after unlocking, not for every bitrate sample',()=>{
  const strip=s=>s.replace(/^#(?:include|pragma).*$/gm,'');
  const source=`#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
typedef int SemaphoreHandle_t;
typedef int TaskHandle_t;
static int held, notifications;
#define portMAX_DELAY 0
#define pdMS_TO_TICKS(x) (x)
static int xTaskGetTickCount(void) { return 0; }
static int xSemaphoreCreateMutex(void) { return 1; }
static int xTaskGetCurrentTaskHandle(void) { return 42; }
static void xSemaphoreTake(int s,int t) { (void)s;(void)t;assert(!held);held=1; }
static void xSemaphoreGive(int s) { (void)s;assert(held);held=0; }
static void xTaskNotifyGive(int task) { assert(task==42 && !held);++notifications; }
${strip(read('native_state.h'))}
${strip(read('native_state.c'))}
int main(void) {
  native_state_init();
  native_state_set_audio(false,false,NULL); assert(notifications==0);
  native_state_set_audio(false,true,NULL); assert(notifications==1);
  native_state_set_audio(false,true,NULL); assert(notifications==1);
  native_state_set_audio(true,false,NULL); assert(notifications==2);
  native_state_set_stream(CODEC_HELIX_AAC,64,48000,2); assert(notifications==3);
  for (unsigned n=0;n<1000;++n) {
    native_state_set_stream(CODEC_HELIX_AAC,n,48000,2);
    native_state_set_wifi_rssi(-60-(n%15));
  }
  assert(notifications==3);
  native_state_set_title("Song"); assert(notifications==4);
  native_state_set_title("Song"); assert(notifications==4);
  native_state_set_volume(20); assert(notifications==5);
  native_state_set_volume(20); assert(notifications==5);
  native_state_set_station(2,"Station"); assert(notifications==6);
  native_state_set_audio(false,false,NULL); assert(notifications==7);
  native_state_set_audio(false,false,"Error"); assert(notifications==8);
  native_state_t snapshot; native_state_snapshot(&snapshot);
  assert(snapshot.station_index==2 && !snapshot.playing && !snapshot.title[0]);
}
`;
  const dir=fs.mkdtempSync(path.join(root,'.build/state-notify-'));
  const file=path.join(dir,'test.c'),bin=path.join(dir,'test');fs.writeFileSync(file,source);
  const wsl=process.platform==='win32',p=f=>wsl?'/mnt/'+f[0].toLowerCase()+f.slice(2).replace(/\\/g,'/'):f;
  const opts={encoding:'utf8'},args=['-std=c11','-Wall','-Wextra','-Werror',p(file),'-o',p(bin)];
  let r=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,opts);
  assert.equal(r.status,0,r.stdout+r.stderr);
  r=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin)]:[],opts);
  assert.equal(r.status,0,r.stdout+r.stderr);
});
test('station status and index are sent in one HTTP poll without a second timer tick',()=>{
  const web=read('web_service.c');
  assert.doesNotMatch(web,/s_current_pending|s_pending_current/);
  const poll=web.slice(web.indexOf('static void poll_on_http_task('),web.indexOf('static void poll_work('));
  assert.ok(poll.indexOf('broadcast_message(s_async_message)')<poll.indexOf('broadcast_message(selection)'));
  assert.match(poll,/if \(station_changed\)[\s\S]*broadcast_message\(selection\)/);
});
