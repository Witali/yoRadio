#include "c3_ws_status/platform.h"
#include "state-header.inc"
#include "production.inc"

enum {STATUS,CURRENT,PLAYLIST,DEADLINE,KINDS};
typedef struct {bool used;void(*callback)(void*);void *argument;unsigned kind;char frozen[1280];} work_t;
static work_t work_queue[16];
static unsigned attempts[KINDS],accepted[KINDS],completed[KINDS],frames,shutdowns;
static unsigned reject_mask;
static bool list_failure,send_failure,no_clients,session_replaced;
static void *session_context;
static char sent_text[64][1280];
static httpd_ws_type_t sent_types[64];
static native_state_t fixture_state;

static unsigned work_kind(void *p){if(!p)return DEADLINE;if(p==&s_status_work)return STATUS;if(p==&s_current_work)return CURRENT;assert(p==&s_playlist_work);return PLAYLIST;}
static esp_err_t httpd_queue_work(httpd_handle_t server,void(*callback)(void*),void *arg){assert(server==s_server&&!in_httpd);unsigned kind=work_kind(arg);attempts[kind]++;if(reject_mask&(1U<<kind))return ESP_FAIL;for(unsigned i=0;i<16;i++)if(!work_queue[i].used){work_queue[i]=(work_t){.used=true,.callback=callback,.argument=arg,.kind=kind};if(kind!=DEADLINE)strlcpy(work_queue[i].frozen,((ws_broadcast_work_t*)arg)->text,sizeof(work_queue[i].frozen));accepted[kind]++;return ESP_OK;}return ESP_FAIL;}
static esp_err_t httpd_get_client_list(httpd_handle_t server,size_t *count,int *sockets){assert(in_httpd&&server==s_server&&*count==CONFIG_LWIP_MAX_SOCKETS);if(list_failure)return ESP_FAIL;*count=no_clients?0:1;if(*count)sockets[0]=3;return ESP_OK;}
static int httpd_ws_get_fd_info(httpd_handle_t server,int socket){assert(in_httpd&&server==s_server&&socket==3);return HTTPD_WS_CLIENT_WEBSOCKET;}
static void *httpd_sess_get_ctx(httpd_handle_t server,int socket){assert(server==s_server&&socket==3);return session_replaced?NULL:session_context;}
static esp_err_t httpd_ws_send_frame_async(httpd_handle_t server,int socket,httpd_ws_frame_t *frame){assert(in_httpd&&server==s_server&&socket==3&&frame->final);assert(frame->len<sizeof(sent_text[0]));assert(s_clients[0].send_deadline_us==monotonic_us+WS_FRAME_BUDGET_US);assert(frames<64);sent_types[frames]=frame->type;memcpy(sent_text[frames],frame->payload,frame->len);sent_text[frames][frame->len]=0;if(frame->type==HTTPD_WS_TYPE_TEXT){assert(websocket_message_utf8_valid(frame->payload,frame->len));printf("JSON %s\n",sent_text[frames]);}frames++;return send_failure?ESP_FAIL:ESP_OK;}
static void native_web_transport_shutdown(httpd_handle_t server,int socket,bool graceful){assert(in_httpd&&server==s_server&&socket==3);(void)graceful;shutdowns++;}
void native_state_snapshot(native_state_t *state,native_state_t *snapshot){assert(state==s_state);*snapshot=fixture_state;}

static void drain(unsigned kind){for(unsigned i=0;i<16;i++){work_t *queued=&work_queue[i];if(!queued->used||queued->kind!=kind)continue;ws_broadcast_work_t *work=queued->argument;if(kind!=DEADLINE){assert(!strcmp(work->text,queued->frozen)&&"queued payload immutable until HTTPD dispatch");assert(atomic_load(work->pending)>0&&atomic_load(&work->busy));}else assert(atomic_load(&s_message_poll_pending));in_httpd=true;queued->callback(queued->argument);in_httpd=false;queued->used=false;completed[kind]++;if(kind!=DEADLINE)assert(!atomic_load(&work->busy));else assert(!atomic_load(&s_message_poll_pending));assert(s_clients[0].send_deadline_us==0);}}
static void drain_all(void){for(unsigned kind=0;kind<KINDS;kind++)drain(kind);}
static void run(unsigned cycles,void(*hook)(unsigned)){budget=cycles;before_cycle=hook;if(!setjmp(loop_exit))status_task(NULL);assert(reboot_polls==cycles&&probe_polls==cycles);}
static void station(unsigned item){fixture_item=(uint16_t)item;snprintf(fixture_name,sizeof(fixture_name),"station %u",item);}
static void previous(unsigned item){assert(s_previous_status_key.current_item==item&&"previous key advances only after both admissions");}
static void reset_client(void){s_clients[0].closing=false;session_replaced=false;}

static void idle_hook(unsigned step){if(step==2){previous(1);drain_all();}}
static void heartbeat_hook(unsigned step){if(step==2){drain_all();ticks=2099;}if(step==3){assert(accepted[STATUS]==1);ticks=2100;}if(step==4){assert(accepted[STATUS]==2);drain_all();ticks=4099;}}
static void tickwrap_hook(unsigned step){if(step==1)ticks=UINT32_MAX-999U;if(step==2){drain_all();ticks=999U;}if(step==3){assert(accepted[STATUS]==1);ticks=1000U;}}
static void change_hook(unsigned step){if(step==2){drain_all();station(2);}if(step==3){previous(2);drain_all();fixture_volume++;}if(step==4){previous(2);drain_all();}}
static void reject_hook(unsigned step){if(step==2){previous(0);drain_all();reject_mask=0;}if(step==3){previous(1);drain_all();}}
static void held_status_hook(unsigned step){if(step==2){drain(CURRENT);previous(1);station(2);strcpy(fixture_state.title,"changed while queued");}if(step==3){previous(1);drain(STATUS);assert(accepted[STATUS]==1&&accepted[CURRENT]==1);}if(step==4){previous(2);drain_all();}}
static void held_current_hook(unsigned step){if(step==2){drain(STATUS);previous(1);station(2);}if(step==3){assert(accepted[CURRENT]==1);previous(1);drain(STATUS);drain(CURRENT);}if(step==4){previous(2);drain_all();}}
static void playlist_hook(unsigned step){if(step==2){drain_all();websocket_service_notify_playlist_changed();reject_mask=1U<<PLAYLIST;}if(step==3){assert(atomic_load(&s_playlist_changed_pending));assert(!accepted[PLAYLIST]);reject_mask=0;}if(step==4){assert(!atomic_load(&s_playlist_changed_pending)&&accepted[PLAYLIST]==1);assert(atomic_load(&s_status_send_pending)==1);station(2);}if(step==5){previous(1);assert(accepted[STATUS]==1);websocket_service_notify_playlist_changed();drain(PLAYLIST);}if(step==6){assert(accepted[PLAYLIST]==2);drain(PLAYLIST);}if(step==7){previous(2);drain_all();}}
static void failed_dispatch_hook(unsigned step){if(step==2){list_failure=true;drain_all();list_failure=false;assert(!atomic_load(&s_status_send_pending)&&!atomic_load(&s_current_send_pending));station(2);}if(step==3){previous(2);drain_all();}}
static void send_failure_hook(unsigned step){if(step==2){send_failure=true;drain_all();assert(shutdowns==1&&s_clients[0].closing);send_failure=false;reset_client();station(2);}if(step==3){previous(2);drain_all();}}
static void replaced_hook(unsigned step){if(step==2){session_replaced=true;drain_all();assert(!frames);reset_client();station(2);}if(step==3){previous(2);drain_all();}}
static void heartbeat_fields_hook(unsigned step){if(step==2){drain_all();fixture_state.wifi_rssi=-75;fixture_fill=88;ticks=2099;}if(step==3){assert(accepted[STATUS]==1);ticks=2100;}if(step==4)drain_all();}
static void stopped_hook(unsigned step){if(step==2){drain_all();fixture_state.audio_running=false;fixture_fill=99;}if(step==3)drain_all();}
static void profile_hook(unsigned step){if(step>1)drain_all();monotonic_us=(int64_t)step*INT64_C(6000000);}
static void fragment(void){ws_client_t *client=&s_clients[0];assert(websocket_message_init(&client->message,client->command,sizeof(client->command),WS_MESSAGE_BUDGET_US));websocket_message_result_t result=websocket_message_feed(&client->message,1,false,(const uint8_t*)"pl",2,0);assert(result.event==WEBSOCKET_MESSAGE_NONE&&client->message.active);ws_update_active(client,false);assert(atomic_load(&s_fragmented_clients)==1);}
static void deadline_hook(unsigned step){if(step==2){assert(accepted[DEADLINE]==1);monotonic_us=4999999;drain(DEADLINE);assert(s_clients[0].message.active&&!shutdowns);}if(step==3){assert(accepted[DEADLINE]==2);monotonic_us=5000000;drain(DEADLINE);assert(shutdowns==1&&!s_clients[0].message.active&&!atomic_load(&s_fragmented_clients));}if(step==4){assert(accepted[DEADLINE]==2&&accepted[STATUS]==1&&accepted[CURRENT]==1);drain_all();}}
static void deadline_retry_hook(unsigned step){if(step==2){assert(attempts[DEADLINE]==1&&!atomic_load(&s_message_poll_pending));}if(step==3){assert(attempts[DEADLINE]==2&&!atomic_load(&s_message_poll_pending));reject_mask=0;}if(step==4){assert(accepted[DEADLINE]==1);monotonic_us=5000000;drain(DEADLINE);assert(shutdowns==1);drain_all();}}

int main(int argc,char **argv){assert(argc==2);const char *test=argv[1];s_server=(void*)(uintptr_t)1;s_state=&fixture_state;fixture_state.audio_running=true;fixture_state.wifi_rssi=-40;fixture_state.sample_rate_hz=48000;fixture_state.channels=2;fixture_state.bits_per_sample=16;fixture_state.bitrate_kbps=128;strcpy(fixture_state.title,"title one");strcpy(fixture_state.codec,"MP3");strcpy(fixture_state.stream_format,"MP3 48 kHz");s_clients[0]=(ws_client_t){.used=true,.socket=3};session_context=&s_clients[0];
 if(!strcmp(test,"initial")){run(1,NULL);previous(1);assert(accepted[STATUS]==1&&accepted[CURRENT]==1&&!frames);drain_all();assert(frames==2&&strstr(sent_text[0],"\"meta\",\"value\":\"title one\"")&&strstr(sent_text[0],"\"heap\",\"value\":37")&&!strcmp(sent_text[1],"{\"current\":1}"));}
 else if(!strcmp(test,"unchanged")){run(10,idle_hook);assert(accepted[STATUS]==1&&accepted[CURRENT]==1);}
 else if(!strcmp(test,"heartbeat")){run(4,heartbeat_hook);assert(accepted[STATUS]==2&&accepted[CURRENT]==1);}
 else if(!strcmp(test,"tick_wrap")){run(3,tickwrap_hook);assert(accepted[STATUS]==2&&accepted[CURRENT]==1);}
 else if(!strcmp(test,"changes")){run(4,change_hook);assert(accepted[STATUS]==3&&accepted[CURRENT]==2);assert(strstr(sent_text[2],"station 2")&&!strcmp(sent_text[3],"{\"current\":2}"));}
 else if(!strcmp(test,"reject_status")){reject_mask=1U<<STATUS;run(3,reject_hook);assert(accepted[STATUS]==1&&accepted[CURRENT]==2);}
 else if(!strcmp(test,"reject_current")){reject_mask=1U<<CURRENT;run(3,reject_hook);assert(accepted[STATUS]==2&&accepted[CURRENT]==1);}
 else if(!strcmp(test,"reject_both")){reject_mask=(1U<<STATUS)|(1U<<CURRENT);run(3,reject_hook);assert(accepted[STATUS]==1&&accepted[CURRENT]==1);}
 else if(!strcmp(test,"held_status")){run(4,held_status_hook);assert(accepted[STATUS]==2&&accepted[CURRENT]==2);assert(strstr(sent_text[1],"title one")&&strstr(sent_text[2],"changed while queued"));}
 else if(!strcmp(test,"held_current")){run(4,held_current_hook);assert(accepted[CURRENT]==2);assert(!strcmp(sent_text[2],"{\"current\":1}")&&!strcmp(sent_text[4],"{\"current\":2}"));}
 else if(!strcmp(test,"playlist")){run(7,playlist_hook);assert(attempts[PLAYLIST]==3&&accepted[PLAYLIST]==2&&completed[PLAYLIST]==2);assert(accepted[STATUS]==2&&accepted[CURRENT]==2);}
 else if(!strcmp(test,"list_failure")){run(3,failed_dispatch_hook);assert(frames==2&&accepted[STATUS]==2&&accepted[CURRENT]==2);}
 else if(!strcmp(test,"send_failure")){run(3,send_failure_hook);assert(shutdowns==1&&frames==3&&accepted[STATUS]==2&&accepted[CURRENT]==2);}
 else if(!strcmp(test,"replaced_session")){run(3,replaced_hook);assert(frames==2&&!shutdowns);}
 else if(!strcmp(test,"heartbeat_fields")){run(4,heartbeat_fields_hook);assert(accepted[STATUS]==2&&accepted[CURRENT]==1);assert(strstr(sent_text[2],"\"rssi\",\"value\":-75")&&strstr(sent_text[2],"\"heap\",\"value\":88"));}
 else if(!strcmp(test,"stopped_buffer")){run(3,stopped_hook);assert(strstr(sent_text[2],"\"heap\",\"value\":0")&&strstr(sent_text[2],"\"playerwrap\",\"value\":\"stopped\""));}
 else if(!strcmp(test,"profile")){run(4,profile_hook);assert(profile_logs==3);}
 else if(!strcmp(test,"json_escape")){strcpy(fixture_name,"station \"quoted\"");strcpy(fixture_state.title,"line\nback\\slash");run(1,NULL);drain_all();assert(strstr(sent_text[0],"station \\\"quoted\\\"")&&strstr(sent_text[0],"line\\u000aback\\\\slash"));}
 else if(!strcmp(test,"no_clients")){no_clients=true;run(10,idle_hook);assert(!frames&&atomic_load(&s_last_ws_clients)==0);}
 else if(!strcmp(test,"deadline_backpressure")){fragment();run(4,deadline_hook);assert(frames==1&&sent_types[0]==HTTPD_WS_TYPE_CLOSE&&(unsigned char)sent_text[0][0]==3&&(unsigned char)sent_text[0][1]==0xf0);}
 else if(!strcmp(test,"deadline_retry")){fragment();reject_mask=1U<<DEADLINE;run(4,deadline_retry_hook);assert(attempts[DEADLINE]==3&&frames==1);}
 else if(!strcmp(test,"metadata_bounds")){memset(fixture_name,'"',sizeof(fixture_name)-1);fixture_name[sizeof(fixture_name)-1]=0;memset(fixture_state.title,1,sizeof(fixture_state.title)-1);fixture_state.title[sizeof(fixture_state.title)-1]=0;memset(fixture_state.stream_format,'\\',sizeof(fixture_state.stream_format)-1);fixture_state.stream_format[sizeof(fixture_state.stream_format)-1]=0;run(1,NULL);drain_all();assert(frames==2&&strlen(sent_text[0])<sizeof(s_broadcast_status));}
 else assert(!"unknown case");
 drain_all();assert(!atomic_load(&s_status_send_pending)&&!atomic_load(&s_current_send_pending));assert(!atomic_load(&s_status_work.busy)&&!atomic_load(&s_current_work.busy)&&!atomic_load(&s_playlist_work.busy));printf("PASS %s\n",test);return 0;
}
