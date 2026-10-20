#include "platform.h"
#include "runtime_settings.h"
static bool with_credentials;
static bool read_credentials(wifi_config_t *config);
esp_err_t network_service_storage_init(void){return ESP_OK;}
#include "production.inc"
// Active credential loader is the sole startup seam touching the legacy cache.
// Tests never write AP facts, owner policy, acknowledgments or deadlines.
static bool read_credentials(wifi_config_t *config){
 if(!with_credentials)return false;
 s_credential_count=1;memset(s_credentials,0,sizeof(s_credentials));
 memcpy(s_credentials[0].sta.ssid,"test",5);*config=s_credentials[0];return true;
}
static native_state_t state;
static void save(unsigned minutes){CHECK(runtime_settings_set_softap_delay_min((uint8_t)minutes)==ESP_OK,"accepted_real_nvs_settings_save");}
static void start(void){CHECK(network_service_start(&state)==ESP_OK,"actual_network_start");fixture_parked();fixture_step(0);}
static void online(void){fixture_observe(true,true,0x01020304);fixture_emit(IP_EVENT,IP_EVENT_STA_GOT_IP);}
static void *settings_writer(void *arg){uintptr_t offset=(uintptr_t)arg;for(unsigned i=0;i<200;++i)save((i+offset)%31);return NULL;}
int main(int argc,char **argv){
 CHECK(argc==2,"case_argument");const char *name=argv[1];fixture_init();
 if(!strcmp(name,"restore"))fixture_boot_delay(30);else if(!strcmp(name,"restore-invalid"))fixture_boot_delay(31);
 CHECK(runtime_settings_init()==ESP_OK,"actual_settings_init");
#ifdef HISTORICAL
 save(1);start();
 if(!strcmp(name,"ota"))fixture_lease(true);
 else if(!strcmp(name,"online"))online();
 else if(!strcmp(name,"disable"))save(0);
 else CHECK(false,"known_historical_case");
 fixture_fire_timer();bool safe=!fixture_stats().restarts;fixture_finish();
 if(!safe){printf("SAFETY_FAILURE:ap_timeout_respects_%s\n",name);return 42;}
 printf("SAFETY_OK:ap_timeout_respects_%s\n",name);return 0;
#else
 if(!strcmp(name,"restore")||!strcmp(name,"restore-invalid")){
  bool valid=!strcmp(name,"restore");runtime_softap_settings_t desired=runtime_settings_get_softap_snapshot();
  CHECK(desired.revision==1&&desired.delay_min==(valid?30:0)&&!fixture_stats().writes&&!fixture_stats().commits,"actual_nvs_restores_valid_delay_or_keeps_default_without_rewrite");
  start();fixture_step(1799999999);CHECK(!fixture_stats().restarts,"restored_delay_not_fired_early");fixture_step(1);
  CHECK(fixture_stats().restarts==(valid?1U:0U),"restored_policy_reaches_actual_owner");
 }else if(!strcmp(name,"revision-exhaustion")){
  runtime_softap_settings_t before=runtime_settings_get_softap_snapshot();CHECK(before.revision==(UINT32_MAX>>5)&&before.delay_min==1,"explicit_settings_initialization_boundary_seed");start();
  CHECK(runtime_settings_set_softap_delay_min(0)==ESP_ERR_INVALID_STATE&&runtime_settings_set_softap_delay_min(1)==ESP_ERR_INVALID_STATE,"exhausted_admission_rejects_before_nvs");
  runtime_softap_settings_t after=runtime_settings_get_softap_snapshot();CHECK(after.revision==before.revision&&after.delay_min==before.delay_min&&!fixture_stats().writes&&!fixture_stats().commits,"exhausted_revision_never_wraps_or_writes_nvs");
 }else if(!strcmp(name,"default")){start();fixture_step(1800000000LL);CHECK(!fixture_stats().reserves&&!fixture_stats().restarts,"default_zero_never_admits_restart");}
 else if(!strcmp(name,"deadline")||!strcmp(name,"thirty")){
  unsigned minutes=!strcmp(name,"thirty")?30:1;save(minutes);start();fixture_step((int64_t)minutes*60000000-1);
  CHECK(!fixture_stats().restarts,"no_restart_before_exact_deadline");fixture_step(1);
  CHECK(fixture_stats().restarts==1&&fixture_stats().immediates==1&&!fixture_stats().reserved&&!fixture_stats().pending,"exact_deadline_uses_immediate_owned_lease");
  fixture_step(0);CHECK(fixture_stats().restarts==1,"no_repeated_decision_on_returning_restart_double");
 }else if(!strcmp(name,"online")){save(1);start();online();fixture_step(0);fixture_step(60000000);CHECK(!fixture_stats().restarts,"online_cancels_old_deadline");}
 else if(!strcmp(name,"disable")){save(1);start();save(0);fixture_step(60000000);CHECK(!fixture_stats().reserves,"accepted_zero_cancels_armed_timeout");}
 else if(!strcmp(name,"roundtrip")||!strcmp(name,"same-value")||!strcmp(name,"edit")){
  save(1);start();fixture_step(30000000);runtime_softap_settings_t before=runtime_settings_get_softap_snapshot();
  if(!strcmp(name,"roundtrip")){save(0);save(1);}else save(!strcmp(name,"edit")?2:1);
  runtime_softap_settings_t after=runtime_settings_get_softap_snapshot();CHECK(after.revision>before.revision,"accepted_saves_publish_new_coherent_revision");fixture_step(0);fixture_step(30000000);
  CHECK(!fixture_stats().restarts,"new_revision_invalidates_old_deadline_even_same_final_value");
  fixture_step(!strcmp(name,"edit")?90000000:30000000);CHECK(fixture_stats().restarts==1,"changed_policy_rearms_full_interval");
 }else if(!strcmp(name,"concurrent-settings")){
  save(1);start();runtime_softap_settings_t before=runtime_settings_get_softap_snapshot();pthread_t writers[2];
  for(uintptr_t i=0;i<2;++i)CHECK(!pthread_create(&writers[i],NULL,settings_writer,(void*)i),"concurrent_settings_writer_create");
  uint32_t previous=before.revision;for(unsigned i=0;i<2000;++i){runtime_softap_settings_t current=runtime_settings_get_softap_snapshot();CHECK(current.delay_min<=30&&current.revision>=previous,"atomic_policy_snapshot_monotonic_and_bounded");previous=current.revision;}
  for(unsigned i=0;i<2;++i)CHECK(!pthread_join(writers[i],NULL),"concurrent_settings_writer_join");
  runtime_softap_settings_t after=runtime_settings_get_softap_snapshot();CHECK(after.revision==before.revision+400&&after.delay_min==fixture_stats().saved,"serialized_nvs_writers_publish_every_accepted_revision");
 }else if(!strcmp(name,"nvs-errors")||!strcmp(name,"writer-timeout")||!strcmp(name,"invalid-setting")){
  save(1);start();runtime_softap_settings_t before=runtime_settings_get_softap_snapshot();
  if(!strcmp(name,"nvs-errors")){for(unsigned stage=1;stage<=3;++stage){fixture_nvs_failure(stage);CHECK(runtime_settings_set_softap_delay_min(0)==ESP_FAIL,"actual_nvs_failure_returned");}fixture_nvs_failure(0);}
  else if(!strcmp(name,"writer-timeout")){fixture_lock_failure(true);CHECK(runtime_settings_set_softap_delay_min(0)==ESP_ERR_TIMEOUT,"precommit_writer_timeout");fixture_lock_failure(false);}
  else CHECK(runtime_settings_set_softap_delay_min(31)==ESP_ERR_INVALID_ARG,"invalid_delay_rejected");
  runtime_softap_settings_t after=runtime_settings_get_softap_snapshot();CHECK(after.revision==before.revision&&after.delay_min==1&&fixture_stats().saved==1,"failed_persistence_preserves_ram_revision_and_flash");
  fixture_step(60000000);CHECK(fixture_stats().restarts==1,"failed_save_does_not_cancel_valid_old_timer");
 }else if(!strcmp(name,"ota")||!strcmp(name,"lease-error")){
  save(1);start();bool held=!strcmp(name,"ota");if(held)fixture_lease(true);else fixture_failure(RESERVE,true);fixture_step(60000000);
  CHECK(!fixture_stats().restarts&&!fixture_stats().pending,"blocked_admission_never_queues_ap_restart");if(held)fixture_lease(false);else fixture_failure(RESERVE,false);
  fixture_step(59999999);CHECK(!fixture_stats().restarts,"cancelled_ota_does_not_release_stale_pending_ap_restart");fixture_step(1);CHECK(fixture_stats().restarts==1,"fresh_full_interval_after_lease_failure");
 }else if(!strcmp(name,"sleep")){save(1);start();CHECK(fixture_sleep_claim(),"sleep_owns_activity");fixture_step(60000000);CHECK(!fixture_stats().reserves,"sleep_owner_prevents_ap_admission");fixture_sleep_release();fixture_step(59999999);CHECK(!fixture_stats().restarts,"sleep_release_does_not_replay_old_expiry");}
 else if(!strcmp(name,"associated")||!strcmp(name,"netif-up")||!strcmp(name,"stale-ip")||!strcmp(name,"query-error")||!strcmp(name,"ip-error")||!strcmp(name,"mode-error")){
  save(1);start();if(!strcmp(name,"associated"))fixture_observe(true,false,0);
  else if(!strcmp(name,"netif-up"))fixture_observe(false,true,0);else if(!strcmp(name,"stale-ip"))fixture_observe(false,false,1);
  else fixture_failure(!strcmp(name,"query-error")?QUERY:!strcmp(name,"ip-error")?IP_QUERY:GET_MODE,true);
  fixture_step(60000000);CHECK(!fixture_stats().reserves&&!fixture_stats().restarts,"live_proof_failure_blocks_admission");
 }else if(!strcmp(name,"late-online")||!strcmp(name,"late-disable")||!strcmp(name,"late-roundtrip")||!strcmp(name,"late-association")||!strcmp(name,"late-manual")||!strcmp(name,"activity-race")){
  with_credentials=!strcmp(name,"late-manual");save(1);start();
  if(with_credentials){for(unsigned i=0;i<3;++i)fixture_emit(WIFI_EVENT,WIFI_EVENT_STA_DISCONNECTED);fixture_step(0);}
  fixture_block(RESERVE);fixture_release_step(60000000);fixture_wait_blocked();
  if(!strcmp(name,"late-online"))online();else if(!strcmp(name,"late-association"))fixture_observe(true,false,0);
  else if(!strcmp(name,"late-disable"))save(0);else if(!strcmp(name,"late-roundtrip")){save(0);save(1);}
  else if(!strcmp(name,"late-manual"))CHECK(network_service_retry_client()==ESP_OK,"actual_manual_retry_before_final_check");
  else CHECK(!fixture_sleep_claim(),"active_ap_decision_excludes_sleep_cas");
  fixture_release_blocked();fixture_parked();stats_t s=fixture_stats();
  if(!strcmp(name,"activity-race"))CHECK(s.restarts==1,"owned_activity_allows_valid_restart");
  else CHECK(!s.restarts&&s.cancels==1&&!s.reserved&&!s.pending,"final_change_cancels_only_own_ap_lease");
 }else if(!strcmp(name,"query-race")){
  save(1);start();fixture_block(QUERY);fixture_release_step(60000000);fixture_wait_blocked();save(0);fixture_release_blocked();fixture_parked();CHECK(!fixture_stats().reserves,"settings_change_during_sdk_query_blocks_lease");
 }else if(!strcmp(name,"slow-lease")){
  save(1);start();fixture_failure(RESERVE,true);fixture_block(RESERVE);fixture_release_step(60000000);fixture_wait_blocked();fixture_clock(esp_timer_get_time()+60000000);fixture_release_blocked();fixture_parked();fixture_failure(RESERVE,false);fixture_step(0);CHECK(!fixture_stats().restarts,"slow_failed_admission_rearms_from_return_time");
 }else if(!strcmp(name,"prepare-sleep")||!strcmp(name,"sleep-error")){
  save(1);start();bool failure=!strcmp(name,"sleep-error");fixture_failure(STOP,failure);
  CHECK(network_service_prepare_sleep()==(failure?ESP_FAIL:ESP_OK),"actual_prepare_sleep_result");fixture_step(60000000);
  CHECK(!fixture_stats().restarts,"sleep_transition_invalidates_old_deadline");
  if(failure){fixture_failure(STOP,false);fixture_step(60000000);CHECK(fixture_stats().restarts==1,"failed_sleep_rearms_after_guard_restored");}
 }else if(!strcmp(name,"failed-enable")){
  save(1);fixture_failure(AP_CONFIG,true);CHECK(network_service_start(&state)==ESP_FAIL,"ap_config_failure_returned");fixture_parked();fixture_step(60000000);CHECK(!fixture_stats().reserves,"failed_ap_enable_never_arms");
 }else if(!strcmp(name,"pending-cancel")||!strcmp(name,"pending-cancel-error")){
  with_credentials=true;save(1);start();bool failure=!strcmp(name,"pending-cancel-error");fixture_failure(DISCONNECT,failure);
  fixture_step(60000000);CHECK(fixture_stats().disconnects==1&&!fixture_stats().reserves&&!fixture_stats().restarts,"expired_connect_intent_cancelled_before_any_restart_admission");
  fixture_step(0);fixture_step(59999999);CHECK(!fixture_stats().restarts,"cancellation_always_requires_new_full_interval");fixture_step(1);
  if(failure)CHECK(fixture_stats().disconnects==2&&!fixture_stats().reserves,"failed_cancel_never_claims_pending_finished");
  else CHECK(fixture_stats().restarts==1&&fixture_stats().disconnects==1,"successful_cancel_plus_fresh_live_proof_can_restart_later");
 }else if(!strcmp(name,"pending-late-online")||!strcmp(name,"pending-late-association")||!strcmp(name,"pending-new-attempt")){
  with_credentials=true;save(1);start();fixture_block(DISCONNECT);fixture_release_step(60000000);fixture_wait_blocked();
  if(!strcmp(name,"pending-late-online"))online();else if(!strcmp(name,"pending-late-association"))fixture_observe(true,false,0);else fixture_emit(WIFI_EVENT,WIFI_EVENT_STA_DISCONNECTED);
  fixture_release_blocked();fixture_parked();CHECK(!fixture_stats().restarts&&!fixture_stats().reserves,"cancel_return_never_restarts_in_same_iteration");
  fixture_step(0);fixture_step(60000000);
  if(strcmp(name,"pending-new-attempt"))CHECK(!fixture_stats().restarts,"late_link_during_cancel_cancels_timeout");
  else CHECK(fixture_stats().disconnects==2&&!fixture_stats().reserves,"older_cancel_does_not_clear_newer_connect_intent");
 }else if(!strcmp(name,"clock-limit")){
  save(1);fixture_clock(INT64_MAX-30000000);start();fixture_step(30000000);CHECK(!fixture_stats().reserves,"unrepresentable_interval_never_restarts_early");
 }else if(!strcmp(name,"clock-negative")){
  save(1);start();fixture_clock(-1);fixture_step(0);CHECK(!fixture_stats().reserves,"negative_clock_never_admits_restart");fixture_clock(1000000);fixture_step(0);fixture_step(60000000);CHECK(fixture_stats().restarts==1,"restored_clock_rearms_full_interval");
 }else CHECK(false,"known_case");
 fixture_finish();CHECK(!fixture_stats().activities,"all_activity_released_when_restart_double_returns");printf("PASS:%s\n",name);return 0;
#endif
}
