#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdio>
#include <cstring>
#include "esp_http_client.h"
#include "esp_heap_caps.h"
#include "esp_partition.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_task_wdt.h"
#include "psa/crypto.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "custom_flac_adapter.h"
#include "flac_decoder.h"
#if CONFIG_ESP_TASK_WDT_TIMEOUT_S!=5 || CONFIG_ESP_INT_WDT_TIMEOUT_MS!=300
#error Ordinary diagnostic must retain the reviewed production watchdog intervals
#endif
#if !CONFIG_ESP_TASK_WDT_EN || !CONFIG_ESP_TASK_WDT_INIT || !CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0 || !CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1 || !CONFIG_ESP_INT_WDT || !CONFIG_ESP_INT_WDT_CHECK_CPU1
#error Both production idle watchdog owners and interrupt watchdogs are required
#endif
#if CONFIG_ESP_TASK_WDT_PANIC || !CONFIG_HEAP_POISONING_DISABLED || CONFIG_YORADIO_NATIVE_DIAGNOSTICS
#error Ordinary diagnostic requires production no-panic and quiet-heap settings
#endif
#if !CONFIG_YORADIO_OGG_TIMELINE || !CONFIG_YORADIO_AAC_PLUS || !CONFIG_YORADIO_AAC_DECODER_ESPRESSIF || !CONFIG_YORADIO_FLAC_DECODER_CUSTOM
#error Current public production codec/metadata branches must compile
#endif
extern "C" {
#include "audio_service.h"
#include "native_audio_output.h"
#include "native_network_power.h"
}
struct Header{uint32_t magic,version,count,entry_size;};
struct Entry{uint32_t id,bits,channels,rate,encoded_offset,encoded_bytes,pcm_offset,pcm_bytes;char name[64];};
static_assert(sizeof(Header)==16&&sizeof(Entry)==96,"fixture ABI");
static const uint8_t *blob;
static const Entry *entries;
static unsigned entry_count;
static native_state_t state;
static EventGroupHandle_t events;
static SemaphoreHandle_t read_gate;
static constexpr unsigned HELD=1U,WORKSPACE=2U,ENDED=4U;
static std::atomic<const Entry*> selected;
static std::atomic<bool> hold_reads;
static std::atomic<unsigned> live_client,cleanup_count,created,destroyed,live_decoder,flushes,writes,profiles,pauses,discards;
static std::atomic<size_t> pcm_position;
static TaskHandle_t owner_handles[3];
static std::atomic<unsigned> metadata_order,layout_calls,gain_calls,feed_calls,decode_calls,max_decode_call_us;
static psa_hash_operation_t output_hash;
static bool hash_live;
static char completed_hash[65];
static int64_t positive_deadline;
static constexpr int64_t POSITIVE_MIN_US=15000000,POSITIVE_DEADLINE_US=90000000;
static constexpr unsigned OBSERVER_ITERATION_LIMIT=10000;
static esp_http_client_handle_t current_client;
static const Entry *client_entry;
static size_t client_position;
static unsigned client_schedule;
static void check(bool condition,const char *name){if(!condition){printf("CYD_FLAC_TASK_FAILURE %s\n",name);fflush(stdout);assert(condition);}}
static void owner(int core,unsigned priority){check(xPortGetCoreID()==core,"actual_core");check(uxTaskPriorityGet(nullptr)==priority,"actual_priority");}
static const Entry *find(const char *name){for(unsigned i=0;i<entry_count;++i)if(!strcmp(entries[i].name,name))return &entries[i];assert(false);return nullptr;}
template<class Predicate>static void wait_until(Predicate predicate,const char *name){int64_t end=esp_timer_get_time()+30000000;while(!predicate()){int64_t now=esp_timer_get_time();check(now<end&&(!positive_deadline||now<positive_deadline),name);vTaskDelay(1);}check(!positive_deadline||esp_timer_get_time()<positive_deadline,"positive_whole_phase_deadline");}
static void configure(const Entry *entry,bool hold){check(!live_client&& !live_decoder,"configure_quiet");check(metadata_order==0,"prior_metadata_consumed");if(hash_live)check(psa_hash_abort(&output_hash)==PSA_SUCCESS,"discard_partial_observer_hash");output_hash=psa_hash_operation_init();check(psa_hash_setup(&output_hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"actual_output_hash_setup");hash_live=true;completed_hash[0]=0;selected=entry;hold_reads=hold;pcm_position=0;xEventGroupClearBits(events,HELD|WORKSPACE|ENDED);}
extern "C" BaseType_t __real_xTaskCreatePinnedToCore(TaskFunction_t,const char*,uint32_t,void*,UBaseType_t,TaskHandle_t*,BaseType_t);
extern "C" BaseType_t __wrap_xTaskCreatePinnedToCore(TaskFunction_t fn,const char *name,uint32_t stack,void *arg,UBaseType_t priority,TaskHandle_t *task,BaseType_t core){
 if(!strcmp(name,"radio_stream")){check(stack==6144&&priority==3&&core==0,"stream_profile");++profiles;}
 else if(!strcmp(name,"audio_decode")){check(stack==16384&&priority==5&&core==1,"decode_profile");++profiles;}
 else if(!strcmp(name,"audio_output")){check(stack==4096&&priority==6&&core==1,"output_profile");++profiles;}
 BaseType_t result=__real_xTaskCreatePinnedToCore(fn,name,stack,arg,priority,task,core);
 if(result==pdPASS&&task){if(!strcmp(name,"radio_stream"))owner_handles[0]=*task;else if(!strcmp(name,"audio_decode"))owner_handles[1]=*task;else if(!strcmp(name,"audio_output"))owner_handles[2]=*task;}
 return result;
}
extern "C" esp_http_client_handle_t __real_esp_http_client_init(const esp_http_client_config_t*);
extern "C" esp_err_t __real_esp_http_client_cleanup(esp_http_client_handle_t);
extern "C" esp_http_client_handle_t __wrap_esp_http_client_init(const esp_http_client_config_t *config){
 owner(0,3);check(!live_client,"single_real_sdk_client");check(live_decoder==0&&FLACDecoder_GetAllocatedBytes()==0,"old_decoder_released_before_next_http_init");
 auto client=__real_esp_http_client_init(config);check(client,"real_http_init");current_client=client;client_entry=selected.load();client_position=0;client_schedule=127;++live_client;return client;
}
static void client_check(esp_http_client_handle_t c){owner(0,3);check(c==current_client&&live_client==1,"real_client_identity");}
extern "C" esp_err_t __wrap_esp_http_client_open(esp_http_client_handle_t c,int write_len){client_check(c);check(!write_len,"read_only_fixture");return ESP_OK;}
extern "C" int64_t __wrap_esp_http_client_fetch_headers(esp_http_client_handle_t c){client_check(c);return client_entry->encoded_bytes;}
extern "C" int __wrap_esp_http_client_get_status_code(esp_http_client_handle_t c){client_check(c);return 200;}
extern "C" int __wrap_esp_http_client_read(esp_http_client_handle_t c,char *buffer,int capacity){
 client_check(c);
 if(hold_reads&&client_position>=2048){xEventGroupSetBits(events,HELD);xSemaphoreTake(read_gate,pdMS_TO_TICKS(10));return -ESP_ERR_HTTP_EAGAIN;}
 size_t bytes=std::min<size_t>(capacity,std::min<size_t>(client_schedule,client_entry->encoded_bytes-client_position));
 if(bytes){memcpy(buffer,blob+client_entry->encoded_offset+client_position,bytes);}
 client_position+=bytes;return (int)bytes;
}
extern "C" esp_err_t __wrap_esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t c,int *error,int *flags){client_check(c);if(error)*error=0;if(flags)*flags=0;return ESP_OK;}
extern "C" bool __wrap_esp_http_client_is_complete_data_received(esp_http_client_handle_t c){client_check(c);return !hold_reads&&client_position==client_entry->encoded_bytes;}
extern "C" esp_err_t __wrap_esp_http_client_cleanup(esp_http_client_handle_t c){client_check(c);esp_err_t result=__real_esp_http_client_cleanup(c);check(result==ESP_OK,"real_http_cleanup");current_client=nullptr;--live_client;++cleanup_count;return result;}
extern "C" custom_flac_decoder_t *__real_custom_flac_decoder_create(void);
extern "C" int __real_custom_flac_decoder_feed(custom_flac_decoder_t*,const uint8_t*,size_t,bool,custom_flac_pcm_callback_t,void*,custom_flac_feed_stats_t*);
extern "C" void __real_custom_flac_decoder_destroy(custom_flac_decoder_t*);
extern "C" custom_flac_decoder_t *__wrap_custom_flac_decoder_create(void){owner(1,5);check(!live_decoder,"one_actual_custom_decoder");auto d=__real_custom_flac_decoder_create();check(d,"real_custom_create");++created;++live_decoder;return d;}
extern "C" int __wrap_custom_flac_decoder_feed(custom_flac_decoder_t *d,const uint8_t *data,size_t bytes,bool eos,custom_flac_pcm_callback_t callback,void *user,custom_flac_feed_stats_t *stats){owner(1,5);check(live_decoder==1,"live_custom_feed");int result=__real_custom_flac_decoder_feed(d,data,bytes,eos,callback,user,stats);++feed_calls;decode_calls+=stats->decode_calls;unsigned previous=max_decode_call_us.load();while(previous<stats->max_call_us&&!max_decode_call_us.compare_exchange_weak(previous,stats->max_call_us)){}if(FLACDecoder_GetAllocatedBytes())xEventGroupSetBits(events,WORKSPACE);return result;}
extern "C" void __wrap_custom_flac_decoder_destroy(custom_flac_decoder_t *d){owner(1,5);check(live_decoder==1,"exact_custom_destroy");__real_custom_flac_decoder_destroy(d);check(!FLACDecoder_GetAllocatedBytes(),"destroy_released_workspace");--live_decoder;++destroyed;}
// Explicit public output-backend seam. Real output_task/PCM ring remain intact.
extern "C" bool native_audio_output_supports_pcm(uint8_t bits_per_sample,uint8_t channels){return channels&&(bits_per_sample==8||bits_per_sample==16||bits_per_sample==24||bits_per_sample==32);}
extern "C" esp_err_t native_audio_output_init(void){return ESP_OK;}
extern "C" const char *native_audio_output_name(void){return "QEMU PCM oracle seam";}
extern "C" esp_err_t native_audio_output_configure(uint32_t rate){owner(1,6);check(rate==selected.load()->rate,"output_rate");check(metadata_order==0,"configure_before_packet_metadata");return ESP_OK;}
extern "C" esp_err_t native_audio_output_set_channel_layout(pcm_channel_layout layout,uint8_t channels){owner(1,6);check(layout==PCM_CHANNEL_LAYOUT_LEGACY&&channels==selected.load()->channels&&channels>=1&&channels<=2,"ordinary_legacy_layout");check(metadata_order==0,"layout_before_gain");metadata_order=1;++layout_calls;return ESP_OK;}
extern "C" esp_err_t native_audio_output_set_header_gain(int16_t gain_q8){owner(1,6);check(gain_q8==0&&metadata_order==1,"ordinary_zero_gain_after_layout");metadata_order=2;++gain_calls;return ESP_OK;}
extern "C" esp_err_t native_audio_output_write_pcm(const uint8_t *pcm,size_t size,uint8_t bits,uint8_t channels){
 owner(1,6);const Entry *entry=selected.load();size_t position=pcm_position.load();check(bits==16&&channels==entry->channels&&size%(channels*2)==0,"pcm16_geometry");
 check(position<=entry->pcm_bytes&&size<=entry->pcm_bytes-position,"pcm_bounds");check(!memcmp(pcm,blob+entry->pcm_offset+position,size),"exact_output_pcm");check(metadata_order==2,"gain_before_write");metadata_order=0;check(hash_live&&psa_hash_update(&output_hash,pcm,size)==PSA_SUCCESS,"actual_output_hash_update");
 native_state_t snapshot;native_state_snapshot(&state,&snapshot);check(snapshot.bits_per_sample==entry->bits&&snapshot.pcm_channels==channels&&snapshot.channels==channels&&!strcmp(snapshot.codec,"FLAC"),"source_and_pcm_metadata");
 pcm_position=position+size;++writes;return ESP_OK;
}
extern "C" esp_err_t native_audio_output_flush_pcm(void){owner(1,6);check(pcm_position==selected.load()->pcm_bytes,"ordered_complete_pcm_before_eof");check(!live_decoder&&!FLACDecoder_GetAllocatedBytes(),"release_before_pcm_eof");check(metadata_order==0,"no_partial_metadata_at_eof");uint8_t digest[32];size_t length=0;check(hash_live&&psa_hash_finish(&output_hash,digest,sizeof(digest),&length)==PSA_SUCCESS&&length==32&&psa_hash_abort(&output_hash)==PSA_SUCCESS,"actual_complete_output_hash");hash_live=false;for(unsigned i=0;i<32;++i)snprintf(completed_hash+2*i,3,"%02x",digest[i]);++flushes;xEventGroupSetBits(events,ENDED);return ESP_OK;}
extern "C" void native_audio_output_discard_pcm(void){owner(1,6);metadata_order=0;++discards;}
extern "C" esp_err_t native_audio_output_pause(void){owner(1,6);check(!live_decoder&&!live_client,"three_owners_release_before_output_pause");++pauses;return ESP_OK;}
extern "C" void native_audio_output_request_pause(bool requested){(void)requested;}
extern "C" void native_audio_output_request_normalizer_reset(void){}
extern "C" void native_audio_output_idle(void){}
extern "C" esp_err_t audio_level_led_init(void){return ESP_OK;}
extern "C" void audio_level_led_update_peak(uint16_t peak){(void)peak;}
extern "C" void audio_level_led_update_pcm(const uint8_t *p,size_t n,uint8_t b,uint8_t c){(void)p;(void)n;(void)b;(void)c;}
extern "C" void network_service_audio_accept(uint32_t generation,bool active){native_network_power_accept(generation,active);}
extern "C" void network_service_audio_receive(uint32_t generation){native_network_power_receive(generation);}
extern "C" void network_service_audio_finish(uint32_t generation){native_network_power_finish(generation);}
static void play(const char *url){check(audio_service_play(url,NATIVE_CODEC_FLAC)==ESP_OK,"actual_public_play");}
static void complete(){wait_until([]{return (xEventGroupGetBits(events)&ENDED)!=0;},"bounded_ordered_eof");wait_until([]{return live_client==0&&live_decoder==0;},"bounded_cleanup");wait_until([]{native_state_t s;native_state_snapshot(&state,&s);return !s.audio_running&&!s.audio_pending&&!strcmp(s.stream_format,"stream ended");},"public_final_eof_state");check(heap_caps_check_integrity_all(true),"quiescent_heap_integrity");}
static void held(){wait_until([]{return (xEventGroupGetBits(events)&(HELD|WORKSPACE))==(HELD|WORKSPACE);},"active_real_decoder_and_held_transport");check(pcm_position==0,"partial_fixture_has_no_complete_frame");}
static void resources(unsigned iteration,int64_t elapsed){
 int idle0=esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0)),idle1=esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1));
 check(idle0==ESP_OK&&idle1==ESP_OK,"both_real_idle_watchdog_subscriptions");
 auto faults=native_health_snapshot().faults;check(!faults.decoder_failures&&!faults.output_failures&&!faults.stream_failures&&!faults.allocation_failures,"ordinary_no_real_pipeline_faults");
 check(created==destroyed&&!live_decoder&&!live_client&&!FLACDecoder_GetAllocatedBytes()&&layout_calls==gain_calls&&gain_calls==writes,"positive_quiet_exact_owners_and_metadata");
 check(completed_hash[0]&&heap_caps_check_integrity_all(true),"positive_real_hash_and_heap_integrity");
 printf("CYD_FLAC_ORDINARY_ITERATION index=%u elapsed_us=%llu pcm_bytes=%u sha256=%s created=%u destroyed=%u http_cleanup=%u writes=%u layouts=%u gains=%u feed_calls=%u decode_calls=%u max_decode_call_us=%u heap_free=%u heap_min=%u heap_largest=%u internal_free=%u internal_largest=%u dma_free=%u dma_largest=%u stream_stack_free=%u decode_stack_free=%u output_stack_free=%u idle0_status=%d idle1_status=%d workspace=0 live_decoders=0 live_clients=0 allocation_failures=0 decoder_failures=0 stream_failures=0 output_failures=0\n",
 iteration,(unsigned long long)elapsed,(unsigned)selected.load()->pcm_bytes,completed_hash,created.load(),destroyed.load(),cleanup_count.load(),writes.load(),layout_calls.load(),gain_calls.load(),feed_calls.load(),decode_calls.load(),max_decode_call_us.load(),(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_DEFAULT),(unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),(unsigned)heap_caps_get_free_size(MALLOC_CAP_DMA),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_DMA),(unsigned)uxTaskGetStackHighWaterMark(owner_handles[0]),(unsigned)uxTaskGetStackHighWaterMark(owner_handles[1]),(unsigned)uxTaskGetStackHighWaterMark(owner_handles[2]),idle0,idle1);fflush(stdout);
}
extern "C" void app_main(void){
 check(xPortGetCoreID()==0,"coordinator_core0");printf("CYD_FLAC_TASK_BOOT actual_audio_service_tu=1 sdk=%s core0_stream=1 core1_decode_output=1 hardware=0\n",esp_get_idf_version());
 check(psa_crypto_init()==PSA_SUCCESS,"public_hash_init");
 printf("CYD_FLAC_ORDINARY_CONFIG twdt_seconds=5 twdt_panic=0 int_wdt_ms=300 idle0=1 idle1=1 quiet_heap=1 diagnostics=0 ogg_timeline=1 aac_plus=1 custom_flac=1 real_output_driver=0 hardware=0\n");
 events=xEventGroupCreate();read_gate=xSemaphoreCreateBinary();check(events&&read_gate,"real_test_sdk_sync");
 auto part=esp_partition_find_first(ESP_PARTITION_TYPE_DATA,(esp_partition_subtype_t)0x40,"fixtures");check(part&&part->address==0x200000&&part->size==0x200000,"test_partition_bounds");
 const void *mapped=nullptr;esp_partition_mmap_handle_t mapping;check(esp_partition_mmap(part,0,part->size,ESP_PARTITION_MMAP_DATA,&mapped,&mapping)==ESP_OK,"fixture_mapping");blob=(const uint8_t*)mapped;
 auto header=(const Header*)mapped;check(header->magic==0x514c4643&&header->count==130&&header->entry_size==sizeof(Entry),"fixture_manifest");entries=(const Entry*)(header+1);entry_count=header->count;
 for(unsigned i=0;i<entry_count;++i){auto&e=entries[i];check(e.encoded_offset<part->size&&e.encoded_bytes<=part->size-e.encoded_offset&&e.pcm_offset<part->size&&e.pcm_bytes<=part->size-e.pcm_offset,"fixture_entry_bounds");}
 native_state_init(&state);check(state.lock&&native_health_start(),"actual_state_and_health_init");check(audio_service_start(&state)==ESP_OK,"actual_whole_tu_start");check(profiles==3,"three_original_task_profiles");
 configure(find("flac-24bit-mid-verbatim"),false);play("http://fixture/T0");complete();printf("CYD_FLAC_TASK_CASE id=T0 ordered_eof=1 byte_compare=1 pcm_bytes=%u\n",(unsigned)selected.load()->pcm_bytes);
 configure(find("flac-24bit-mid-verbatim-block8192"),true);unsigned old_cleanup=cleanup_count.load();play("http://fixture/T1-old");held();audio_service_stop();wait_until([old_cleanup]{return cleanup_count>old_cleanup&&!live_client&&!live_decoder;},"stop_releases_actual_owners");
 configure(find("flac-16bit-stereo-verbatim"),false);play("http://fixture/T1-reopen");complete();printf("CYD_FLAC_TASK_CASE id=T1 stop_reopen=1 byte_compare=1 pcm_bytes=%u\n",(unsigned)selected.load()->pcm_bytes);
 configure(find("flac-24bit-mid-verbatim-block8192"),true);play("http://fixture/T2");held();unsigned previous_cleanup=cleanup_count.load(),previous_pause=pauses.load();audio_maintenance_token_t token={};
 check(audio_service_maintenance_begin(10000,&token)==ESP_OK&&token.epoch,"actual_three_owner_maintenance");check(cleanup_count>previous_cleanup&&!live_client&&!live_decoder&&pauses>previous_pause,"held_all_owner_cleanup");
 auto health=audio_service_input_health();check(health.available&&health.leased&&!health.ready&&!health.reading&&!health.writing,"actual_input_leases_quiet");check(heap_caps_check_integrity_all(true),"held_heap_integrity");
 hold_reads=false;xEventGroupClearBits(events,HELD|WORKSPACE|ENDED);pcm_position=0;auto stale=token;check(audio_service_maintenance_end(&token,true)==ESP_OK&&!token.epoch,"actual_resume_handoff");check(audio_service_maintenance_end(&stale,true)==ESP_ERR_INVALID_STATE,"stale_maintenance_rejected");complete();
 printf("CYD_FLAC_TASK_CASE id=T2 maintenance_resume=1 byte_compare=1 pcm_bytes=%u\n",(unsigned)selected.load()->pcm_bytes);
 // Complete original valid files only. The public wait loops above retain
 // their original one-tick waits; this phase adds no sleep/yield/idle feed.
 int64_t positive_started=esp_timer_get_time();positive_deadline=positive_started+POSITIVE_DEADLINE_US;unsigned iterations=0;
 printf("CYD_FLAC_ORDINARY_POSITIVE_BEGIN minimum_us=%llu deadline_us=%llu started_us=%llu\n",(unsigned long long)POSITIVE_MIN_US,(unsigned long long)POSITIVE_DEADLINE_US,(unsigned long long)positive_started);fflush(stdout);
 int64_t elapsed=0;
 do{check(iterations<OBSERVER_ITERATION_LIMIT,"bounded_observer_iteration_limit");configure(find("flac-24bit-mid-verbatim-block8192"),false);play("http://fixture/T3-complete");complete();elapsed=esp_timer_get_time()-positive_started;check(elapsed>=0&&elapsed<POSITIVE_DEADLINE_US,"positive_fixed_deadline");resources(iterations,elapsed);check(esp_timer_get_time()<positive_deadline,"positive_observation_within_deadline");++iterations;}while(elapsed<POSITIVE_MIN_US);
 int64_t finished_elapsed=esp_timer_get_time()-positive_started;check(finished_elapsed>=elapsed&&finished_elapsed<POSITIVE_DEADLINE_US,"positive_actual_termination_within_deadline");
 positive_deadline=0;
 printf("CYD_FLAC_ORDINARY_POSITIVE_END iterations=%u elapsed_us=%llu last_completion_us=%llu minimum_us=%llu deadline_us=%llu\n",iterations,(unsigned long long)finished_elapsed,(unsigned long long)elapsed,(unsigned long long)POSITIVE_MIN_US,(unsigned long long)POSITIVE_DEADLINE_US);
 audio_maintenance_token_t final={};check(audio_service_maintenance_begin(10000,&final)==ESP_OK,"final_actual_quiescence");auto faults=native_health_snapshot().faults;check(!faults.decoder_failures&&!faults.output_failures&&!faults.stream_failures,"no_pipeline_faults");check(created==destroyed&&!live_decoder&&!live_client&&heap_caps_check_integrity_all(true),"all_actual_instances_clean");
 printf("CYD_FLAC_ORDINARY_COMPLETE original_cases=3 positive_iterations=%u actual_audio_service_tu=1 created=%u destroyed=%u real_http_cleanup=%u writes=%u layouts=%u gains=%u core_bindings=1 hardware=0 real_output_driver=0 oom_injection=0 deliberate_backpressure=0 semantic_fault_controls=0\n",iterations,created.load(),destroyed.load(),cleanup_count.load(),writes.load(),layout_calls.load(),gain_calls.load());fflush(stdout);esp_restart();
}
