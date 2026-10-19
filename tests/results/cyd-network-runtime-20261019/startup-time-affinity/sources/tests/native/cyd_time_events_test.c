#include <assert.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "board_config.h"
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_WIFI_NOT_STARTED 0x301
#define ESP_RETURN_ON_ERROR(expr, ...) do {int e_=(expr);if(e_)return e_;}while(0)
#define ESP_RETURN_ON_FALSE(expr,err,...) do {if(!(expr))return(err);}while(0)
#define ESP_ERROR_CHECK(expr) assert((expr)==ESP_OK)
static void log_message(const char *tag,const char *format,...) {(void)tag;(void)format;}
#define ESP_LOGI(...) log_message(__VA_ARGS__)
#define ESP_LOGW(...) log_message(__VA_ARGS__)
#define ESP_LOGE(...) log_message(__VA_ARGS__)
static const char *const TAG="fixture";
static const char *esp_err_to_name(int error){(void)error;return "fixture";}
#include "network_profiles.h"
#include "network_netif.h"
struct esp_netif {unsigned marker;};
static struct esp_netif station;
typedef enum {NATIVE_NETWORK_STARTING,NATIVE_NETWORK_CLIENT,NATIVE_NETWORK_ACCESS_POINT,NATIVE_NETWORK_ERROR} native_network_mode_t;
typedef struct {void *lock;native_network_mode_t mode;uint32_t ip;} native_state_t;
static native_state_t s_app_state;
static int s_display;
static void native_state_init(native_state_t *state){memset(state,0,sizeof(*state));state->lock=&s_display;}
static void native_state_set_network(native_state_t *state,native_network_mode_t mode,uint32_t ip){state->mode=mode;state->ip=ip;}
typedef struct {int unused;} wifi_init_config_t;
#define WIFI_INIT_CONFIG_DEFAULT() ((wifi_init_config_t){0})
#define WIFI_STORAGE_RAM 1
#define WIFI_MODE_STA 1
#define pdTRUE 1
#define pdFALSE 0
#define pdMS_TO_TICKS(ms) (ms)
static unsigned sdk_calls,fail_sdk_at,groups;
static unsigned stops,deinits,releases,loop_deletes,runtime_stops,runtime_starts,waits,profile_wipes;
static bool driver_ram,shared_loop,empty_profiles;
static int profile_result,wait_result,stop_result,runtime_stop_result,deinit_result,release_result;
static const network_profiles_t *borrowed_profiles;
static int sdk_result(void){return ++sdk_calls==fail_sdk_at?ESP_FAIL:ESP_OK;}
static int network_service_storage_init(void){return sdk_result();}
static int esp_netif_init(void){return sdk_result();}
static int esp_event_loop_create_default(void){int result=sdk_result();return result?result:shared_loop?ESP_ERR_INVALID_STATE:ESP_OK;}
static void esp_event_loop_delete_default(void){++loop_deletes;}
int network_netif_create(network_netif_t *out,bool ap){assert(!ap&&!out->handle);int result=sdk_result();if(!result)out->handle=&station;return result;}
int network_netif_release(network_netif_t *owner){++releases;if(!release_result)owner->handle=NULL;return release_result;}
static int esp_wifi_init(const wifi_init_config_t *init){assert(init);return sdk_result();}
static int esp_wifi_set_storage(int storage){assert(storage==WIFI_STORAGE_RAM);int result=sdk_result();driver_ram=!result;return result;}
static int esp_wifi_set_mode(int mode){assert(mode==WIFI_MODE_STA);return sdk_result();}
int network_profiles_load(network_profiles_t *out){memset(out,0,sizeof(*out));out->count=empty_profiles?0:2;strcpy(out->rows[0].ssid,"fixture-one");strcpy(out->rows[0].password,"fixture-private");return profile_result;}
static void native_wifi_erase(void *pointer,size_t size){memset(pointer,0,size);if(pointer==borrowed_profiles){const network_profiles_t zero={0};assert(size==sizeof(zero)&&!memcmp(pointer,&zero,size));++profile_wipes;}}
static int network_runtime_start(native_state_t *state,esp_netif_t *netif,const network_profiles_t *profiles){
    assert(state==&s_app_state&&state->lock&&netif==&station&&driver_ram);
    borrowed_profiles=profiles;++runtime_starts;
    if(profile_result!=ESP_OK){const network_profiles_t zero={0};assert(!memcmp(profiles,&zero,sizeof(zero)));}
    else {assert(profiles->count==(empty_profiles?0:2));if(!empty_profiles)assert(!strcmp(profiles->rows[0].ssid,"fixture-one"));}
    return sdk_result();
}
static int esp_wifi_start(void){assert(driver_ram&&profile_wipes);return sdk_result();}
static int esp_wifi_stop(void){++stops;return stop_result;}
static int esp_wifi_deinit(void){assert(runtime_stops);++deinits;return deinit_result;}
static int network_runtime_stop(uint32_t timeout){assert(timeout==2000);++runtime_stops;return runtime_stop_result;}
static int network_runtime_wait_initial(uint32_t timeout){assert(timeout==20000);++waits;return wait_result;}
#define s_state s_network_state
#include "network.inc"
#undef s_state

// The actual C3 handler is retained here only for its credential/sleep guarded
// STA_START. Current CYD GOT/loss/time notifications execute in the owner suite.
typedef const char *esp_event_base_t;
static const char wifi_base[]="wifi",ip_base[]="ip";
#define WIFI_EVENT wifi_base
#define IP_EVENT ip_base
#define WIFI_EVENT_STA_START 1
#define WIFI_EVENT_STA_DISCONNECTED 2
#define IP_EVENT_STA_GOT_IP 3
#define IP_EVENT_STA_LOST_IP 4
#define WIFI_RETRIES_PER_CREDENTIAL 2
#define WIFI_CONNECTED_BIT 1U
#define WIFI_FAILED_BIT 2U
#define IPSTR "%u"
#define IP2STR(ip) ((unsigned)(ip)->addr)
typedef struct {struct {struct {uint32_t addr;} ip;} ip_info;} ip_event_got_ip_t;
typedef struct {int rssi;} wifi_ap_record_t;
static bool s_have_credentials;
static atomic_bool s_stopping_for_sleep;
static size_t s_credential_index,s_credential_count;
static int s_retries;
static unsigned s_wifi_events,event_bits,connect_calls,time_notices;
static unsigned xEventGroupSetBits(unsigned handle,unsigned bits){assert(handle==1);event_bits|=bits;return event_bits;}
static int esp_wifi_connect(void){++connect_calls;return ESP_OK;}
static int select_credential(size_t index){(void)index;return ESP_OK;}
static int esp_wifi_sta_get_ap_info(wifi_ap_record_t *ap){(void)ap;return ESP_FAIL;}
static void native_state_set_wifi_rssi(native_state_t *state,int rssi){(void)state;(void)rssi;}
static void time_service_notify_network_ready(void){++time_notices;}
#define s_state s_network_state
#define event_handler c3_event_handler
#include "c3-events.inc"
#undef event_handler
#undef s_state
static unsigned startup_step, display_step, time_step, pinned_step[2], pinned_count;
static int time_start_error, nvs_error, spiffs_error;
static bool health_ok;
typedef struct {const char *base_path, *partition_label; int max_files; bool format_if_mount_failed;} esp_vfs_spiffs_conf_t;
static int esp_vfs_spiffs_register(const esp_vfs_spiffs_conf_t *config) {
    assert(!strcmp(config->base_path, "/spiffs") && !strcmp(config->partition_label, "spiffs"));
    assert(config->max_files == 8 && !config->format_if_mount_failed);
    return spiffs_error;
}
static int nvs_flash_init(void) {++startup_step; return nvs_error;}
static int native_audio_settings_init(void) {++startup_step; return ESP_OK;}
static bool native_health_start(void) {++startup_step; return health_ok;}
static int cyd_display_init(int *display) {assert(display == &s_display); display_step = ++startup_step; return ESP_OK;}
static int time_service_start(void) {time_step = ++startup_step; return time_start_error;}
static void display_task(void *context) {(void)context;}
static void network_task(void *context) {(void)context;}
static int xTaskCreatePinnedToCore(void (*task)(void *), const char *name,
                                  unsigned stack, void *context, unsigned priority, void *handle, int core) {
    assert(!context && !handle && pinned_count < 2U);
    pinned_step[pinned_count++] = ++startup_step;
    if (task == display_task) {
        assert(!strcmp(name, "display") && stack == BOARD_TASK_STACK_DISPLAY && priority == 1U && core == 0);
    } else {
        assert(task == network_task && !strcmp(name, "network") && stack == BOARD_TASK_STACK_NETWORK && priority == 3U && core == 0);
    }
    return pdTRUE;
}
#define s_state s_app_state
#include "startup.inc"
#undef s_state


static void reset(void){
    sdk_calls=fail_sdk_at=stops=deinits=releases=loop_deletes=runtime_stops=runtime_starts=waits=profile_wipes=0;
    driver_ram=shared_loop=empty_profiles=false;
    profile_result=wait_result=stop_result=runtime_stop_result=deinit_result=release_result=ESP_OK;
    borrowed_profiles=NULL;s_station_netif=(network_netif_t){0};s_network_state=NULL;
    atomic_store(&s_network_start,NETWORK_OFF);native_state_init(&s_app_state);
    s_wifi_events=1;event_bits=connect_calls=time_notices=0;s_have_credentials=false;
    atomic_store(&s_stopping_for_sleep,false);s_credential_count=s_credential_index=s_retries=0;
    startup_step=display_step=time_step=pinned_count=0;
    time_start_error=nvs_error=spiffs_error=0;health_ok=true;
}
int main(void){
    reset();assert(network_service_start(NULL)==ESP_ERR_INVALID_ARG&&!sdk_calls);
    s_app_state.lock=NULL;assert(network_service_start(&s_app_state)==ESP_ERR_INVALID_ARG&&!sdk_calls);++groups;
    reset();assert(network_service_start(&s_app_state)==ESP_OK&&driver_ram&&runtime_starts==1&&waits==1&&profile_wipes==1);
    unsigned before=sdk_calls;assert(network_service_start(&s_app_state)==ESP_OK&&sdk_calls==before);
    native_state_t other={.lock=&s_display};assert(network_service_start(&other)==ESP_ERR_INVALID_STATE&&sdk_calls==before);++groups;
    reset();empty_profiles=true;assert(network_service_start(&s_app_state)==ESP_OK&&runtime_starts==1);++groups;
    reset();profile_result=ESP_FAIL;assert(network_service_start(&s_app_state)==ESP_OK&&runtime_starts==1&&profile_wipes==1);++groups;
    reset();shared_loop=true;assert(network_service_start(&s_app_state)==ESP_OK&&!loop_deletes);++groups;
    reset();wait_result=ESP_ERR_TIMEOUT;assert(network_service_start(&s_app_state)==ESP_OK&&atomic_load(&s_network_start)==NETWORK_READY);++groups;
    reset();wait_result=ESP_FAIL;assert(network_service_start(&s_app_state)==ESP_FAIL&&atomic_load(&s_network_start)==NETWORK_READY&&!runtime_stops);++groups;
    for(unsigned failure=1;failure<=9;++failure){
        reset();fail_sdk_at=failure;
        assert(network_service_start(&s_app_state)==ESP_FAIL&&atomic_load(&s_network_start)==NETWORK_OFF);
        assert(runtime_stops==1&&releases==1&&!s_station_netif.handle);
        assert(loop_deletes==(failure>=4));assert(stops==(failure>=6)&&deinits==(failure>=6));
        assert(!waits);++groups;
    }
    reset();shared_loop=true;fail_sdk_at=9;assert(network_service_start(&s_app_state)==ESP_FAIL&&!loop_deletes);++groups;
    reset();fail_sdk_at=9;stop_result=ESP_ERR_WIFI_NOT_STARTED;assert(network_service_start(&s_app_state)==ESP_FAIL&&atomic_load(&s_network_start)==NETWORK_OFF&&runtime_stops==1);++groups;
    for(unsigned failure=0;failure<4;++failure){
        reset();fail_sdk_at=9;
        if(failure==0)stop_result=ESP_FAIL;
        if(failure==1)runtime_stop_result=ESP_FAIL;
        if(failure==2)deinit_result=ESP_FAIL;
        if(failure==3)release_result=ESP_FAIL;
        assert(network_service_start(&s_app_state)==ESP_FAIL&&atomic_load(&s_network_start)==NETWORK_RETAINED);
        assert(s_station_netif.handle&&!loop_deletes);
        if(failure==0)assert(!runtime_stops&&!deinits&&!releases);
        if(failure==1)assert(!deinits&&!releases);
        if(failure==2)assert(!releases);
        before=sdk_calls;assert(network_service_start(&s_app_state)==ESP_ERR_INVALID_STATE&&sdk_calls==before);++groups;
    }
    reset();c3_event_handler(NULL,WIFI_EVENT,WIFI_EVENT_STA_START,NULL);assert(connect_calls==0U);
    s_have_credentials=true;c3_event_handler(NULL,WIFI_EVENT,WIFI_EVENT_STA_START,NULL);assert(connect_calls==1U);
    atomic_store(&s_stopping_for_sleep,true);c3_event_handler(NULL,WIFI_EVENT,WIFI_EVENT_STA_START,NULL);assert(connect_calls==1U);++groups;
    for(unsigned failure=0;failure<5;++failure){
        reset();time_start_error=failure==1?ESP_ERR_NO_MEM:0;nvs_error=failure==2?ESP_FAIL:0;spiffs_error=failure==3?ESP_FAIL:0;health_ok=failure!=4;
        app_main();assert(pinned_count==2U&&time_step>display_step&&time_step<pinned_step[0]);
        assert(pinned_step[0]<pinned_step[1]&&!time_notices);++groups;
    }
    printf("PASS CYD startup facade: %u groups; actual app/time ordering, task affinity, SDK bootstrap failure rollback, retained resources, default-loop ownership, atomic active-profile handoff; C3 guarded STA_START; platform seams only\n",groups);
    return 0;
}
