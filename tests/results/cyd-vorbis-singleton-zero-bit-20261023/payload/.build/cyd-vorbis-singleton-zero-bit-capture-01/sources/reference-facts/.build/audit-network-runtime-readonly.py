"""Read-only audit of current network functions; no proposed runtime is executed."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.build/network-runtime-readonly-audit-02'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
def host(p):
    p=Path(p).resolve().as_posix()
    return '/mnt/'+p[0].lower()+p[2:] if sys.platform=='win32' else p
OUT.mkdir(exist_ok=False)
paths=[ROOT/'idf/esp32-cyd2usb-native/main/network_service.c',ROOT/'idf/esp32c3-oled-native/main/network_service.c',ROOT/'tests/run-web-warning-regressions.py']
report={'scope':'Current unchanged function-body audit; startup-return condition, SDK/RTOS/state seams are modeled. No new runtime, SMP safety or RF qualification claim.','source_sha256':{},'targets':{}}
for p in paths:
    q=OUT/'sources'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());report['source_sha256'][p.relative_to(ROOT).as_posix()]=hashlib.sha256(q.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('network_audit_extract',OUT/'sources/tests/run-web-warning-regressions.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
header=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdatomic.h>
#include <setjmp.h>
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NOT_FOUND 0x105
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_RETURN_ON_FALSE(v,e,...) do {if(!(v))return(e);} while(0)
#define ESP_RETURN_ON_ERROR(v,...) do {int r_=(v);if(r_!=ESP_OK)return r_;} while(0)
#define pdMS_TO_TICKS(x) (x)
#define WIFI_CONNECTED_BIT 1U
#define WIFI_FAILED_BIT 2U
#define WIFI_MAX_RETRIES 8
#define WIFI_RETRIES_PER_CREDENTIAL 2
#define WIFI_RSSI_INTERVAL_MS 2000
#define WIFI_EVENT 1
#define IP_EVENT 2
#define WIFI_EVENT_STA_START 1
#define WIFI_EVENT_STA_DISCONNECTED 2
#define IP_EVENT_STA_GOT_IP 3
#define IP_EVENT_STA_LOST_IP 4
#define WIFI_MODE_NULL 0
#define WIFI_MODE_STA 1
#define WIFI_MODE_AP 2
#define WIFI_MODE_APSTA 3
#define WIFI_IF_STA 0
#define WIFI_PS_NONE 0
#define WIFI_PS_MIN_MODEM 1
#define NATIVE_NETWORK_STARTING 0
#define NATIVE_NETWORK_CLIENT 1
#define NATIVE_NETWORK_ACCESS_POINT 2
typedef int esp_err_t,esp_event_base_t,wifi_mode_t,wifi_ps_type_t;
typedef struct {struct {uint8_t ssid[32],password[64];}sta;} wifi_config_t;
typedef struct {int mode;uint32_t ip;int rssi;} native_state_t;
typedef struct {struct {struct {uint32_t addr;} ip;}ip_info;} ip_event_got_ip_t;
typedef struct {int8_t rssi;} wifi_ap_record_t;
static native_state_t state,*s_state=&state;
static unsigned event_bits,connects,ap_calls,delays;
static int s_wifi_events,s_retries,driver_mode,driver_ps,query_result,config_result;
static bool s_have_credentials;
static wifi_config_t s_station_config,s_credentials[5],driver_config;
static size_t s_credential_count,s_credential_index;
static atomic_bool s_stopping_for_sleep;
static jmp_buf poll_exit;
static void xEventGroupClearBits(int unused,unsigned bits) {(void)unused;event_bits&=~bits;}
static void xEventGroupSetBits(int unused,unsigned bits) {(void)unused;event_bits|=bits;}
static esp_err_t esp_wifi_connect(void) {++connects;return ESP_OK;}
static esp_err_t esp_wifi_get_mode(wifi_mode_t *mode) {*mode=driver_mode;return ESP_OK;}
static esp_err_t esp_wifi_set_mode(wifi_mode_t mode) {driver_mode=mode;return ESP_OK;}
static esp_err_t esp_wifi_set_config(int interface,wifi_config_t *config) {assert(interface==WIFI_IF_STA);if(!config_result)driver_config=*config;return config_result;}
static esp_err_t esp_wifi_set_ps(wifi_ps_type_t mode) {driver_ps=mode;return ESP_OK;}
static esp_err_t esp_wifi_sta_get_ap_info(wifi_ap_record_t *record) {if(!query_result)record->rssi=-55;return query_result;}
static const char *esp_err_to_name(int e) {(void)e;return "modeled";}
static void native_state_set_network(native_state_t *s,int mode,uint32_t ip) {s->mode=mode;s->ip=ip;}
static void native_state_set_wifi_rssi(native_state_t *s,int rssi) {s->rssi=rssi;}
static void time_service_notify_network(bool ready) {(void)ready;}
static void time_service_notify_network_ready(void) {}
static void vTaskDelay(unsigned delay) {assert(delay==2000);if(delays++)longjmp(poll_exit,1);}
static esp_err_t start_access_point(void) {++ap_calls;driver_mode=WIFI_MODE_APSTA;return ESP_OK;}
'''
tests=r'''
static void reset(void) {memset(&state,0,sizeof(state));memset(&s_station_config,0,sizeof(s_station_config));memset(s_credentials,0,sizeof(s_credentials));memset(&driver_config,0,sizeof(driver_config));s_have_credentials=true;s_retries=0;event_bits=connects=ap_calls=delays=0;driver_mode=WIFI_MODE_STA;config_result=query_result=0;s_credential_count=2;s_credential_index=0;strcpy((char *)s_credentials[0].sta.ssid,"first");strcpy((char *)s_credentials[1].sta.ssid,"second");s_station_config=driver_config=s_credentials[0];}
int main(void) {
  reset();event_handler(NULL,WIFI_EVENT,WIFI_EVENT_STA_START,NULL);ip_event_got_ip_t ip={.ip_info.ip.addr=0x01020304};event_handler(NULL,IP_EVENT,IP_EVENT_STA_GOT_IP,&ip);
  assert(state.mode==NATIVE_NETWORK_CLIENT&&state.ip);unsigned before=connects;
  for(unsigned n=0;n<
#ifdef TARGET_C3
      6
#else
      9
#endif
      ;++n)event_handler(NULL,WIFI_EVENT,WIFI_EVENT_STA_DISCONNECTED,NULL);
  assert(event_bits&WIFI_FAILED_BIT);assert(!ap_calls&&driver_mode==WIFI_MODE_STA);
  printf("CONFIRMED late exhaustion: %u retry connect calls after GOT_IP; FAILED bit, no AP transition after startup consumer is gone\n",connects-before);
#ifdef TARGET_C3
  assert(state.mode==NATIVE_NETWORK_CLIENT&&state.ip);puts("CONFIRMED disconnected C3 status retains old CLIENT/IP");
  reset();config_result=ESP_FAIL;assert(select_credential(1)==ESP_FAIL);assert(s_credential_index==1&&!strcmp((char *)s_station_config.sta.ssid,"second")&&!strcmp((char *)driver_config.sta.ssid,"first"));puts("CONFIRMED failed C3 set_config publishes new index/cache before driver acceptance");
  reset();state.rssi=-42;query_result=ESP_FAIL;if(!setjmp(poll_exit))rssi_task(NULL);assert(state.rssi==-42);puts("CONFIRMED failed C3 RSSI query preserves obsolete sample");
  reset();assert(network_service_set_streaming(true)==ESP_OK&&driver_ps==WIFI_PS_NONE);assert(network_service_set_streaming(false)==ESP_OK&&driver_ps==WIFI_PS_MIN_MODEM);puts("CONFIRMED bool power API accepts later false without generation ownership (audio interleaving itself is not executed)");
#endif
  reset();driver_mode=WIFI_MODE_APSTA;assert(network_service_retry_client()==ESP_OK);assert(driver_mode==WIFI_MODE_STA);puts("CONFIRMED manual retry tears down APSTA synchronously before returning to HTTP caller");
  return 0;
}
'''
for target,source,names in [('cyd',paths[0],['station_lost_ip','event_handler','network_service_retry_client']),('c3',paths[1],['rssi_task','select_credential','event_handler','network_service_set_streaming','network_service_retry_client'])]:
    d=OUT/target;d.mkdir();raw=(OUT/'sources'/source.relative_to(ROOT)).read_text();bodies=''.join(m.function(raw,name) for name in names)
    (d/'actual.inc').write_text(bodies);(d/'audit.c').write_text(('#define TARGET_C3 1\n' if target=='c3' else '')+header+'\n#include "actual.inc"\n'+tests)
    command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',host(d/'audit.c'),'-o',host(d/'audit')]
    for stage,command in [('build',command),('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(d/'audit')])]:
        result=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60);(d/(stage+'.log')).write_bytes(result.stdout);assert result.returncode==0,result.stdout.decode(errors='replace')
    report['targets'][target]={'passed':True,'output':result.stdout.decode(),'actual_functions':names};print(target+': '+result.stdout.decode())
report['passed']=True;(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
