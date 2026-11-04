// Non-mutating forwarding witnesses for documented public cancellation APIs.
// No private phase reads and no state/ACK/token fabrication.
static std::atomic<unsigned> acquire_sequence,active_acquire,last_held_acquire;
static std::atomic<unsigned> pause_sequence,last_true_pause_start,last_true_pause_return,true_pause_acquire;
static std::atomic<bool> true_pause_started;
static TaskHandle_t control_owner_handle;
static bool control_owners_recorded;

// Capture SDK main before this diagnostic owns any mutex or creates a task.
// Priority1 is source/startup provenance, not a query of a live base priority.
static void register_control_owner() {
    check(!control_owner_handle && xPortGetCoreID()==0 && uxTaskPriorityGet(nullptr)==1,"controller_original_startup_profile");
    control_owner_handle=xTaskGetCurrentTaskHandle();
    check(control_owner_handle,"controller_public_task_handle");
}
struct control_owner_t {TaskHandle_t handle;const char *role,*provenance;unsigned declared,core;};
static control_owner_t public_control_owner(TaskHandle_t handle) {
    check(handle && control_owner_handle && stream_task_handle && decode_task_handle && output_task_handle,"all_actual_control_owner_handles");
    if(handle==control_owner_handle)return {handle,"controller","sdk_main_startup",1,0};
    if(handle==stream_task_handle)return {handle,"stream","wrapped_task_creation",3,0};
    if(handle==decode_task_handle)return {handle,"decode","wrapped_task_creation",5,1};
    if(handle==output_task_handle)return {handle,"output","wrapped_task_creation",6,1};
    check(false,"pause_caller_is_an_actual_registered_owner");return {};
}
static void record_control_owners() {
    check(xTaskGetCurrentTaskHandle()==control_owner_handle,"controller_publishes_creation_provenance");
    if(control_owners_recorded)return;
    TaskHandle_t handles[]={control_owner_handle,stream_task_handle,decode_task_handle,output_task_handle};
    check(profiles==3,"all_original_pipeline_creation_profiles");
    for(unsigned i=0;i<4;++i) {
        for(unsigned j=0;j<i;++j)check(handles[i]!=handles[j],"unique_actual_public_task_handles");
        auto owner=public_control_owner(handles[i]);
        printf("CYD_F1_CONTROL_OWNER role=%s task_handle=%llu core=%u declared_priority=%u priority_provenance=%s effective_priority_limit=%u live_base_query=0 creation_profile_checked=1\n",
            owner.role,(unsigned long long)reinterpret_cast<uintptr_t>(owner.handle),owner.core,owner.declared,owner.provenance,(unsigned)configMAX_PRIORITIES);
    }
    control_owners_recorded=true;
}
static unsigned sampled_effective_priority(const control_owner_t &owner) {
    check(xTaskGetCurrentTaskHandle()==owner.handle && xPortGetCoreID()==(int)owner.core,"same_registered_caller_task_and_core");
    unsigned value=uxTaskPriorityGet(nullptr);
    check(value>=owner.declared && value<configMAX_PRIORITIES,"effective_priority_in_public_scheduler_range");return value;
}

extern "C" void __real_native_audio_output_request_pause(bool);
extern "C" void __wrap_native_audio_output_request_pause(bool requested) {
    unsigned id=++pause_sequence,active_id=active_acquire.load();
    unsigned lifecycle=active_id?active_id:last_held_acquire.load();
    auto caller=public_control_owner(xTaskGetCurrentTaskHandle());
    check(requested?caller.handle==control_owner_handle:
        (caller.handle!=control_owner_handle || active_id!=0),"source_allowed_public_pause_caller");
    if(requested){true_pause_acquire=lifecycle;last_true_pause_start=id;true_pause_started=true;}
    unsigned priority=sampled_effective_priority(caller);
    printf("CYD_F1_CONTROL_PAUSE_START fixture=%s pause=%u acquire=%u acquire_active=%u requested=%u time_us=%llu core=%u priority=%u task_handle=%llu owner_role=%s declared_priority=%u priority_provenance=%s\n",
        active?active->name:"INIT",id,lifecycle,(unsigned)(active_id!=0),(unsigned)requested,
        (unsigned long long)esp_timer_get_time(),caller.core,priority,(unsigned long long)reinterpret_cast<uintptr_t>(caller.handle),caller.role,caller.declared,caller.provenance);
    __real_native_audio_output_request_pause(requested);
    runtime_pause_forwarded(requested);
    if(requested)last_true_pause_return=id;else true_pause_started=false;
    priority=sampled_effective_priority(caller);
    printf("CYD_F1_CONTROL_PAUSE_RETURN fixture=%s pause=%u acquire=%u acquire_active=%u requested=%u time_us=%llu real_returned=1 core=%u priority=%u task_handle=%llu owner_role=%s declared_priority=%u priority_provenance=%s\n",
        active?active->name:"INIT",id,lifecycle,(unsigned)(active_id!=0),(unsigned)requested,
        (unsigned long long)esp_timer_get_time(),caller.core,priority,(unsigned long long)reinterpret_cast<uintptr_t>(caller.handle),caller.role,caller.declared,caller.provenance);
}

extern "C" esp_err_t __real_audio_service_maintenance_begin(uint32_t,audio_maintenance_token_t *);
extern "C" esp_err_t __wrap_audio_service_maintenance_begin(uint32_t timeout_ms,audio_maintenance_token_t *token) {
    record_control_owners();
    unsigned id=++acquire_sequence;check(!active_acquire,"one_real_public_acquire_interval");active_acquire=id;
    unsigned pauses_before=pauses.load();
    printf("CYD_F1_CONTROL_ACQUIRE_START fixture=%s acquire=%u time_us=%llu timeout_ms=%u source_generation=%u core=%u priority=%u\n",
        active->name,id,(unsigned long long)esp_timer_get_time(),(unsigned)timeout_ms,(unsigned)session_generation.load(),
        (unsigned)xPortGetCoreID(),(unsigned)uxTaskPriorityGet(nullptr));
    esp_err_t result=__real_audio_service_maintenance_begin(timeout_ms,token);
    printf("CYD_F1_CONTROL_ACQUIRE_RETURN fixture=%s acquire=%u time_us=%llu result=%d token_epoch=%llu source_generation=%u real_returned=1\n",
        active->name,id,(unsigned long long)esp_timer_get_time(),(int)result,(unsigned long long)(token?token->epoch:0),
        (unsigned)session_generation.load());
    if(result==ESP_OK && token && token->epoch) {
        auto h=audio_service_input_health();last_held_acquire=id;
        printf("CYD_F1_CONTROL_ACQUIRE_HELD fixture=%s acquire=%u time_us=%llu token_epoch=%llu live_clients=%u live_decoders=%u input_available=%u input_leased=%u input_ready=%u input_reading=%u input_writing=%u pauses_before=%u pauses_after=%u driver_live=%u\n",
            active->name,id,(unsigned long long)esp_timer_get_time(),(unsigned long long)token->epoch,live_clients.load(),live_decoders.load(),
            (unsigned)h.available,(unsigned)h.leased,(unsigned)h.ready,(unsigned)h.reading,(unsigned)h.writing,pauses_before,pauses.load(),(unsigned)driver.live);
    }
    active_acquire=0;return result;
}
