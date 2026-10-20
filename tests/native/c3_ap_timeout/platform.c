#include "platform.h"
#include <errno.h>
const char wifi_base[]="wifi",ip_base[]="ip";
static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER,writer=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t changed=PTHREAD_COND_INITIALIZER;
static pthread_t thread;
static bool created,parked,quit;
static unsigned permits,lap,target;
static void(*task_entry)(void*);
static _Thread_local bool owner;
static atomic_int_fast64_t now;
static stats_t stats;
static wifi_mode_t mode;
static bool associated,up,failures[API_COUNT];
static uint32_t ip;
static event_handler_t wifi_handler,ip_handler;
static esp_netif_t station={1},ap={2};
static int blocked_api=-1;
static bool blocked,released;
static unsigned nvs_failure;
static bool writer_failure;
static uint8_t staged;
static bool boot_delay_present;
static uint64_t epoch;
static void(*timer_callback)(void*);
static struct timespec deadline(void){struct timespec t;clock_gettime(CLOCK_REALTIME,&t);t.tv_sec+=15;return t;}
static void wait_change(void){struct timespec end=deadline();CHECK(!pthread_cond_timedwait(&changed,&lock,&end),"barrier_progress");}
static esp_err_t api(enum api api){
 pthread_mutex_lock(&lock);bool failed=failures[api];
 if(blocked_api==(int)api){blocked_api=-1;blocked=true;pthread_cond_broadcast(&changed);while(!released)wait_change();}
 pthread_mutex_unlock(&lock);return failed?ESP_FAIL:ESP_OK;
}
stats_t fixture_stats(void){pthread_mutex_lock(&lock);stats_t copy=stats;pthread_mutex_unlock(&lock);return copy;}
void fixture_init(void){atomic_store(&now,1000000);mode=WIFI_MODE_STA;}
void fixture_boot_delay(unsigned minutes){CHECK(minutes<=255,"raw_nvs_u8_boundary");stats.saved=(uint8_t)minutes;boot_delay_present=true;}
void fixture_clock(int64_t t){atomic_store(&now,t);}
int64_t esp_timer_get_time(void){return atomic_load(&now);}
void fixture_observe(bool a,bool u,uint32_t p){pthread_mutex_lock(&lock);associated=a;up=u;ip=p;pthread_mutex_unlock(&lock);}
void fixture_failure(enum api a,bool failed){pthread_mutex_lock(&lock);failures[a]=failed;pthread_mutex_unlock(&lock);}
void fixture_nvs_failure(unsigned stage){pthread_mutex_lock(&lock);nvs_failure=stage;pthread_mutex_unlock(&lock);}
void fixture_lock_failure(bool fail){pthread_mutex_lock(&lock);writer_failure=fail;pthread_mutex_unlock(&lock);}
void fixture_block(enum api a){pthread_mutex_lock(&lock);blocked_api=(int)a;blocked=released=false;pthread_mutex_unlock(&lock);}
void fixture_wait_blocked(void){pthread_mutex_lock(&lock);while(!blocked)wait_change();pthread_mutex_unlock(&lock);}
void fixture_release_blocked(void){pthread_mutex_lock(&lock);released=true;pthread_cond_broadcast(&changed);pthread_mutex_unlock(&lock);}
static void *entry(void *arg){(void)arg;owner=true;task_entry(NULL);CHECK(false,"task_does_not_return");return NULL;}
int xTaskCreate(void(*fn)(void*),const char *name,unsigned stack,void *arg,unsigned priority,void *handle){
 CHECK(!strcmp(name,"wifi_rssi")&&stack==2048&&priority==2&&!arg&&!handle&&!created,"original_task_profile");
 task_entry=fn;created=true;target=1;CHECK(!pthread_create(&thread,NULL,entry,NULL),"owner_create");return pdPASS;
}
void vTaskDelay(unsigned ticks){
 CHECK(owner&&ticks==100,"owner_100ms_period");pthread_mutex_lock(&lock);parked=true;++lap;pthread_cond_broadcast(&changed);
 while(!permits&&!quit){wait_change();}
 if(quit){pthread_mutex_unlock(&lock);pthread_exit(NULL);}--permits;parked=false;pthread_mutex_unlock(&lock);
}
void fixture_parked(void){pthread_mutex_lock(&lock);while(!(parked&&lap>=target))wait_change();pthread_mutex_unlock(&lock);}
void fixture_release_step(int64_t delta){fixture_parked();pthread_mutex_lock(&lock);CHECK(!permits&&delta>=0,"parked_step");
 int64_t old=atomic_load(&now);atomic_store(&now,old>INT64_MAX-delta?INT64_MAX:old+delta);target=lap+1;++permits;pthread_cond_broadcast(&changed);pthread_mutex_unlock(&lock);}
void fixture_step(int64_t delta){fixture_release_step(delta);fixture_parked();}
void fixture_finish(void){fixture_parked();pthread_mutex_lock(&lock);quit=true;pthread_cond_broadcast(&changed);pthread_mutex_unlock(&lock);CHECK(!pthread_join(thread,NULL),"owner_join");}
SemaphoreHandle_t xSemaphoreCreateMutex(void){return &writer;}
int xSemaphoreTake(SemaphoreHandle_t sem,TickType_t ticks){(void)ticks;CHECK(sem==&writer,"existing_settings_mutex");pthread_mutex_lock(&lock);bool fail=writer_failure;pthread_mutex_unlock(&lock);if(fail)return pdFALSE;CHECK(!pthread_mutex_lock(sem),"writer_lock");return pdTRUE;}
void xSemaphoreGive(SemaphoreHandle_t sem){CHECK(!pthread_mutex_unlock(sem),"writer_unlock");}
int xEventGroupCreate(void){return 1;}
void xEventGroupSetBits(int h,unsigned bits){CHECK(h==1&&bits,"event_bits");}
void xEventGroupClearBits(int h,unsigned bits){CHECK(h==1&&bits,"clear_event_bits");}
unsigned xEventGroupWaitBits(int h,unsigned bits,int clear,int all,unsigned timeout){CHECK(h==1&&bits==3&&clear&&!all&&timeout==20000,"startup_budget");return 0;}
void fixture_emit(esp_event_base_t base,int id){ip_event_got_ip_t event={.ip_info.ip.addr=0x01020304};(base==WIFI_EVENT?wifi_handler:ip_handler)(NULL,base,id,&event);}
esp_err_t esp_event_handler_register(esp_event_base_t base,int id,event_handler_t handler,void *arg){CHECK(!arg&&(id==ESP_EVENT_ANY_ID||id==IP_EVENT_STA_GOT_IP),"actual_registered_callback");if(base==WIFI_EVENT)wifi_handler=handler;else ip_handler=handler;return ESP_OK;}
void native_state_set_network(native_state_t *s,native_network_mode_t m,uint32_t p){s->mode=m;s->ip=p;}
void native_state_set_wifi_rssi(native_state_t *s,int rssi){(void)s;(void)rssi;pthread_mutex_lock(&lock);++stats.rssi;pthread_mutex_unlock(&lock);}
void time_service_notify_network_ready(void){}
void native_network_power_poll(int64_t t,esp_err_t(*fn)(void*,bool),void *context){(void)t;CHECK(fn(context,false)==ESP_OK,"actual_owner_power_caller");}
void native_network_power_invalidate(void){}
esp_err_t esp_netif_init(void){return ESP_OK;}
esp_err_t esp_event_loop_create_default(void){return ESP_OK;}
esp_netif_t *esp_netif_create_default_wifi_sta(void){return &station;}
esp_netif_t *esp_netif_create_default_wifi_ap(void){return &ap;}
esp_err_t esp_netif_set_hostname(esp_netif_t *n,const char *name){CHECK(n==&station&&!strcmp(name,"yoradio"),"initial_hostname_unchanged");return ESP_OK;}
bool esp_netif_is_netif_up(esp_netif_t *n){CHECK(n==&station,"station_up_query");pthread_mutex_lock(&lock);bool value=up;pthread_mutex_unlock(&lock);return value;}
esp_err_t esp_netif_get_ip_info(esp_netif_t *n,esp_netif_ip_info_t *info){CHECK(n==&station,"station_ip_query");esp_err_t result=api(IP_QUERY);pthread_mutex_lock(&lock);if(!result)info->ip.addr=ip;pthread_mutex_unlock(&lock);return result;}
esp_err_t esp_wifi_init(const wifi_init_config_t *c){(void)c;return ESP_OK;}
esp_err_t esp_wifi_set_storage(int s){CHECK(s==WIFI_STORAGE_RAM,"ram_credentials");return ESP_OK;}
esp_err_t esp_wifi_set_mode(wifi_mode_t m){esp_err_t result=m==WIFI_MODE_APSTA?api(AP_MODE):ESP_OK;pthread_mutex_lock(&lock);if(!result)mode=m;pthread_mutex_unlock(&lock);return result;}
esp_err_t esp_wifi_get_mode(wifi_mode_t *m){esp_err_t result=api(GET_MODE);pthread_mutex_lock(&lock);*m=mode;pthread_mutex_unlock(&lock);return result;}
esp_err_t esp_wifi_set_config(int iface,wifi_config_t *c){(void)c;return iface==WIFI_IF_AP?api(AP_CONFIG):ESP_OK;}
esp_err_t esp_wifi_start(void){fixture_emit(WIFI_EVENT,WIFI_EVENT_STA_START);return ESP_OK;}
esp_err_t esp_wifi_stop(void){return api(STOP);}
esp_err_t esp_wifi_connect(void){esp_err_t result=api(CONNECT);pthread_mutex_lock(&lock);++stats.connects;pthread_mutex_unlock(&lock);return result;}
esp_err_t esp_wifi_disconnect(void){esp_err_t result=api(DISCONNECT);pthread_mutex_lock(&lock);++stats.disconnects;pthread_mutex_unlock(&lock);return result;}
esp_err_t esp_wifi_set_ps(wifi_ps_type_t m){CHECK(owner&&m==WIFI_PS_MIN_MODEM,"power_owner_and_mode");pthread_mutex_lock(&lock);++stats.power;pthread_mutex_unlock(&lock);return ESP_OK;}
esp_err_t esp_wifi_sta_get_ap_info(wifi_ap_record_t *a){esp_err_t result=api(QUERY);pthread_mutex_lock(&lock);if(!result&&!associated)result=ESP_ERR_WIFI_NOT_CONNECT;if(!result)a->rssi=-50;pthread_mutex_unlock(&lock);return result;}
esp_err_t esp_read_mac(uint8_t *m,int type){CHECK(type==ESP_MAC_WIFI_SOFTAP,"mac_type");memset(m,0,6);return ESP_OK;}
esp_err_t esp_timer_create(const esp_timer_create_args_t *a,esp_timer_handle_t *t){timer_callback=a->callback;*t=&timer_callback;return ESP_OK;}
esp_err_t esp_timer_start_once(esp_timer_handle_t t,uint64_t delay){CHECK(t&&delay==60000000,"old_exact_timer_armed");return ESP_OK;}
void fixture_fire_timer(void){CHECK(timer_callback,"actual_old_timer_callback_captured");timer_callback(NULL);}
void esp_restart(void){pthread_mutex_lock(&lock);++stats.restarts;pthread_mutex_unlock(&lock);}
bool deep_sleep_clock_begin_activity(void){pthread_mutex_lock(&lock);bool ok=!stats.sleep;if(ok)++stats.activities;pthread_mutex_unlock(&lock);return ok;}
void deep_sleep_clock_end_activity(void){pthread_mutex_lock(&lock);CHECK(stats.activities,"activity_owned");--stats.activities;pthread_mutex_unlock(&lock);}
bool fixture_sleep_claim(void){pthread_mutex_lock(&lock);bool ok=!stats.activities&&!stats.sleep;if(ok)stats.sleep=true;pthread_mutex_unlock(&lock);return ok;}
void fixture_sleep_release(void){pthread_mutex_lock(&lock);stats.sleep=false;pthread_mutex_unlock(&lock);}
void fixture_lease(bool held){pthread_mutex_lock(&lock);CHECK(!stats.pending,"no_ap_ordinary_pending");stats.reserved=held;pthread_mutex_unlock(&lock);}
esp_err_t websocket_service_reboot_reserve(websocket_reboot_lease_t *l){esp_err_t result=api(RESERVE);pthread_mutex_lock(&lock);++stats.reserves;if(!result&&(stats.reserved||stats.pending))result=ESP_ERR_INVALID_STATE;if(!result){stats.reserved=true;l->epoch=++epoch;}pthread_mutex_unlock(&lock);return result;}
esp_err_t websocket_service_reboot_cancel(websocket_reboot_lease_t *l){pthread_mutex_lock(&lock);CHECK(l->epoch==epoch&&stats.reserved,"exact_cancelled_lease");l->epoch=0;stats.reserved=false;++stats.cancels;pthread_mutex_unlock(&lock);return ESP_OK;}
esp_err_t websocket_service_reboot_restart_reserved_now(websocket_reboot_lease_t *l){pthread_mutex_lock(&lock);CHECK(l->epoch==epoch&&stats.reserved&&stats.activities&&!stats.sleep,"lease_and_activity_retained_at_restart");++stats.immediates;++stats.restarts;pthread_mutex_unlock(&lock);return ESP_OK;}
esp_err_t nvs_open(const char *name,int m,nvs_handle_t *h){CHECK(!strcmp(name,"runtime")&&m==NVS_READWRITE,"nvs_compatible_namespace");pthread_mutex_lock(&lock);bool fail=nvs_failure==1;pthread_mutex_unlock(&lock);*h=1;return fail?ESP_FAIL:ESP_OK;}
void nvs_close(nvs_handle_t h){CHECK(h==1,"nvs_close");}
esp_err_t nvs_set_u8(nvs_handle_t h,const char *key,uint8_t value){CHECK(h==1&&!strcmp(key,"softap"),"unchanged_softap_key");pthread_mutex_lock(&lock);++stats.writes;staged=value;bool fail=nvs_failure==2;pthread_mutex_unlock(&lock);return fail?ESP_FAIL:ESP_OK;}
esp_err_t nvs_commit(nvs_handle_t h){CHECK(h==1,"nvs_commit");pthread_mutex_lock(&lock);++stats.commits;bool fail=nvs_failure==3;if(!fail)stats.saved=staged;pthread_mutex_unlock(&lock);return fail?ESP_FAIL:ESP_OK;}
esp_err_t nvs_set_i8(nvs_handle_t h,const char *k,int8_t v){(void)h;(void)k;(void)v;CHECK(false,"unrelated_setting_write");return ESP_FAIL;}
esp_err_t nvs_set_u16(nvs_handle_t h,const char *k,uint16_t v){(void)h;(void)k;(void)v;CHECK(false,"unrelated_setting_write");return ESP_FAIL;}
esp_err_t nvs_set_str(nvs_handle_t h,const char *k,const char *v){(void)h;(void)k;(void)v;CHECK(false,"unrelated_setting_write");return ESP_FAIL;}
esp_err_t nvs_get_u8(nvs_handle_t h,const char *key,uint8_t *v){CHECK(h==1,"actual_nvs_restore_handle");if(boot_delay_present&&!strcmp(key,"softap")){*v=stats.saved;return ESP_OK;}return ESP_ERR_NVS_NOT_FOUND;}
esp_err_t nvs_get_i8(nvs_handle_t h,const char *key,int8_t *v){(void)h;(void)key;(void)v;return ESP_ERR_NVS_NOT_FOUND;}
esp_err_t nvs_get_u16(nvs_handle_t h,const char *key,uint16_t *v){(void)h;(void)key;(void)v;return ESP_ERR_NVS_NOT_FOUND;}
esp_err_t nvs_get_str(nvs_handle_t h,const char *key,char *v,size_t *n){(void)h;(void)key;(void)v;(void)n;return ESP_ERR_NVS_NOT_FOUND;}
size_t strlcpy(char *out,const char *in,size_t cap){size_t len=strlen(in);if(cap){size_t n=len<cap-1?len:cap-1;memcpy(out,in,n);out[n]=0;}return len;}
