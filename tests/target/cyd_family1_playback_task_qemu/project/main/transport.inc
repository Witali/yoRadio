extern "C" BaseType_t __real_xTaskCreatePinnedToCore(TaskFunction_t, const char *, uint32_t,
    void *, UBaseType_t, TaskHandle_t *, BaseType_t);
extern "C" BaseType_t __wrap_xTaskCreatePinnedToCore(TaskFunction_t run, const char *name,
        uint32_t stack, void *arg, UBaseType_t priority, TaskHandle_t *task, BaseType_t core) {
    const char *role = nullptr;
    TaskHandle_t *observed = nullptr;
    if (!strcmp(name, "radio_stream")) {
        check(core == 0 && priority == 3 && stack == 6144, "stream_creation_profile");
        role = "stream"; observed = &stream_task_handle;
    } else if (!strcmp(name, "audio_decode")) {
        check(core == 1 && priority == 5 && stack == 16384, "decode_creation_profile");
        role = "decode"; observed = &decode_task_handle;
    } else if (!strcmp(name, "audio_output")) {
        check(core == 1 && priority == 6 && stack == 4096, "output_creation_profile");
        role = "output"; observed = &output_task_handle;
    }
    BaseType_t result = __real_xTaskCreatePinnedToCore(run, name, stack, arg, priority, task, core);
    if (role) {
        check(result == pdPASS && task && *task, "actual_pipeline_task_created");
        *observed = *task;
        ++profiles;
        printf("CYD_F1_TASK_PROFILE role=%s core=%d priority=%u stack=%u\n",
            role, (int)core, (unsigned)priority, (unsigned)stack);
    }
    return result;
}

extern "C" esp_http_client_handle_t __real_esp_http_client_init(const esp_http_client_config_t *);
extern "C" esp_err_t __real_esp_http_client_cleanup(esp_http_client_handle_t);
extern "C" esp_http_client_handle_t __wrap_esp_http_client_init(const esp_http_client_config_t *config) {
    owner(0, 3);
    check(!live_clients && !live_decoders, "old_public_owners_released_before_http_init");
    auto client = __real_esp_http_client_init(config);
    check(client, "real_sdk_http_init");
    current_client = client;
    http_generation = snapshot().audio_generation;
    client_position = 0;
    read_index = 0;
    stream_delay={};stream_last_read_positive=false;
    ++live_clients;
    printf("CYD_F1_CONTROL_HTTP_OPEN fixture=%s ordinal=%u generation=%u core=0 priority=3\n",active->name,++http_opens,(unsigned)http_generation.load());
    return client;
}
static void client_check(esp_http_client_handle_t client) {
    owner(0, 3);
    check(client == current_client && live_clients == 1, "real_http_identity");
}
extern "C" esp_err_t __wrap_esp_http_client_open(esp_http_client_handle_t client, int write_bytes) {
    client_check(client); check(!write_bytes, "read_only_transport"); return ESP_OK;
}
extern "C" int64_t __wrap_esp_http_client_fetch_headers(esp_http_client_handle_t client) {
    client_check(client); return fixture_bytes();
}
extern "C" int __wrap_esp_http_client_get_status_code(esp_http_client_handle_t client) {
    client_check(client); return 200;
}
extern "C" int __wrap_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int capacity) {
    client_check(client);
    stream_last_read_positive=false;
    const size_t position=client_position.load();
    const size_t boundary=active->links[0]->hold_offset;
    if (partial_transport && position>=boundary) {
        check(position==boundary,"independently_counted_first_complete_audio_page");
        if(!hold_announced) {
            hold_announced=true;
            printf("CYD_F1_CONTROL_TRANSPORT_HELD fixture=%s position=%u boundary=%u encoded=%u core=0 priority=3 genuine_read=1\n",
                   active->name,(unsigned)position,(unsigned)boundary,(unsigned)fixture_bytes());
        }
        xEventGroupSetBits(events,TRANSPORT_HELD);xSemaphoreTake(read_gate,pdMS_TO_TICKS(10));return -ESP_ERR_HTTP_EAGAIN;
    }
    static constexpr size_t sizes[]={1,257,17,1024,31,511};
    size_t requested=active->schedule==1?1:active->schedule==2?257:active->schedule==3?4096:sizes[read_index++%6];
    size_t count=std::min<size_t>(capacity,requested);count=std::min(count,fixture_bytes()-position);
    if(partial_transport)count=std::min(count,boundary-position);
    if(count && copy_encoded((uint8_t *)buffer,position,count)>1)++cross_link_reads;
    client_position = position + count;
    if(count) {
        const int64_t now=esp_timer_get_time();
        if(!stream_delay.reads)stream_delay.first_positive_us=now;
        ++stream_delay.reads;stream_delay.bytes+=count;stream_delay.max_read=std::max(stream_delay.max_read,(unsigned)count);
        stream_delay.last_positive_us=now;stream_last_read_positive=true;
    }
    return (int)count;
}
extern "C" esp_err_t __wrap_esp_http_client_get_and_clear_last_tls_error(
        esp_http_client_handle_t client, int *error, int *flags) {
    client_check(client); if (error) *error = 0; if (flags) *flags = 0; return ESP_OK;
}
extern "C" bool __wrap_esp_http_client_is_complete_data_received(esp_http_client_handle_t client) {
    client_check(client); return !partial_transport && client_position == (size_t)(fixture_bytes());
}
extern "C" esp_err_t __wrap_esp_http_client_cleanup(esp_http_client_handle_t client) {
    client_check(client);
    stream_last_read_positive=false;
    esp_err_t result = __real_esp_http_client_cleanup(client);
    check(result == ESP_OK, "real_sdk_http_cleanup");
    record_stream_fairness(http_cleanup.load()+1);
    current_client = nullptr;
    --live_clients;
    ++http_cleanup;
    printf("CYD_F1_CONTROL_HTTP_CLOSE fixture=%s ordinal=%u generation=%u result=%d\n",active->name,http_cleanup.load(),(unsigned)http_generation.load(),result);
    return result;
}

