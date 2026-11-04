// Forward actual public scheduler calls. Never add a delay or feed an idle task.
// Only the stream task writes this census; HTTP cleanup publishes it before
// making the completed client available to the diagnostic control task.
struct stream_delay_census_t {
    unsigned reads,max_read,one_started,one_returned,other_started,other_returned;
    unsigned first_delay_read,last_delay_read;
    size_t bytes;
    int64_t first_positive_us,last_positive_us,first_delay_us,last_delay_us;
};
static stream_delay_census_t stream_delay;
static bool stream_last_read_positive;

extern "C" void __real_vTaskDelay(TickType_t);
extern "C" void __wrap_vTaskDelay(TickType_t ticks) {
    const bool observe=xTaskGetCurrentTaskHandle()==stream_task_handle && live_clients==1 && stream_last_read_positive;
    if(observe) {
        owner(0,3);
        if(ticks==1) {
            if(!stream_delay.one_started) {
                stream_delay.first_delay_read=stream_delay.reads;
                stream_delay.first_delay_us=esp_timer_get_time();
            }
            ++stream_delay.one_started;
        } else ++stream_delay.other_started;
    }
    __real_vTaskDelay(ticks);
    if(observe) {
        if(ticks==1) {
            ++stream_delay.one_returned;
            stream_delay.last_delay_read=stream_delay.reads;
            stream_delay.last_delay_us=esp_timer_get_time();
        } else ++stream_delay.other_returned;
    }
}

static void record_stream_fairness(unsigned ordinal) {
    owner(0,3);
    printf("CYD_F1_STREAM_FAIRNESS fixture=%s ordinal=%u generation=%u schedule=%u page_style=%u encoded_bytes=%u position=%u partial_transport=%u complete_transport=%u positive_reads=%u positive_bytes=%u max_positive_read=%u one_tick_started=%u one_tick_returned=%u other_started=%u other_returned=%u first_delay_read=%u last_delay_read=%u first_positive_us=%llu last_positive_us=%llu first_delay_us=%llu last_delay_us=%llu cleanup_us=%llu cleanup_real_returned=1 diagnostic_delays=0 core=0 priority=3\n",
        active->name,ordinal,(unsigned)http_generation.load(),active->schedule,active->page_style,(unsigned)fixture_bytes(),
        (unsigned)client_position.load(),(unsigned)partial_transport,(unsigned)(!partial_transport && client_position==fixture_bytes()),
        stream_delay.reads,(unsigned)stream_delay.bytes,stream_delay.max_read,stream_delay.one_started,stream_delay.one_returned,
        stream_delay.other_started,stream_delay.other_returned,stream_delay.first_delay_read,stream_delay.last_delay_read,
        (unsigned long long)stream_delay.first_positive_us,(unsigned long long)stream_delay.last_positive_us,
        (unsigned long long)stream_delay.first_delay_us,(unsigned long long)stream_delay.last_delay_us,
        (unsigned long long)esp_timer_get_time());
}
