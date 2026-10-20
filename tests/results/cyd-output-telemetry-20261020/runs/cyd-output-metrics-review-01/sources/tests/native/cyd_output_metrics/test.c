#include "platform.h"
#include "native_output_metrics.h"

_Thread_local unsigned critical_depth;
_Thread_local bool in_isr;
static atomic_int_fast64_t now;
static atomic_uint clock_calls, workers;

int64_t esp_timer_get_time(void) {
    CHECK(!critical_depth && !in_isr, "clock_outside_critical_and_isr");
    atomic_fetch_add(&clock_calls, 1); return atomic_load(&now);
}
static void record(size_t requested, size_t written, int result, int64_t begin, int64_t end) {
    atomic_store(&now, begin); int64_t start = native_output_metrics_begin_write();
    atomic_store(&now, end); native_output_metrics_end_write(requested, written, result, start);
}
static void drop(void) { in_isr = true; native_output_metrics_queue_drop(); in_isr = false; }
static void initial(void) {
    native_output_metrics_t view = native_output_metrics_snapshot();
    CHECK(!view.writes && !view.requested_bytes && !view.written_bytes && !view.errors,
          "initial_write_counters_zero");
    CHECK(!view.queue_drops_available && !view.completion_queue_drops,
          "queue_unavailable_before_observation");
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    CHECK(view.timing_enabled, "diagnostic_timing_enabled");
#else
    CHECK(!view.timing_enabled, "quiet_timing_disabled");
#endif
}
static void writes(void) {
    record(100,100,ESP_OK,10,25); record(100,40,ESP_OK,30,33);
    record(100,20,ESP_ERR_TIMEOUT,40,47); record(100,0,ESP_FAIL,50,50);
    record(10,12,ESP_OK,60,66); record(0,0,ESP_OK,70,70);
    native_output_metrics_t view = native_output_metrics_snapshot();
    CHECK(view.writes==6 && view.requested_bytes==410 && view.written_bytes==172,
          "all_driver_calls_and_reported_bytes");
    CHECK(view.errors==4 && view.timeouts==1 && view.short_writes==3,
          "error_and_incomplete_classification");
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    CHECK(view.timing_samples==6 && !view.invalid_time_samples && view.write_us==31 && view.max_write_us==15,
          "diagnostic_driver_wall_time");
    CHECK(atomic_load(&clock_calls)==12, "exact_two_clock_reads_per_diagnostic_write");
#else
    CHECK(!atomic_load(&clock_calls) && !view.timing_samples && !view.write_us && !view.max_write_us,
          "quiet_has_no_clock_reads");
#endif
}
static void clocks(void) {
    record(1,1,ESP_OK,-1,0); record(1,1,ESP_OK,10,9); record(1,1,ESP_OK,0,0);
    native_output_metrics_t view = native_output_metrics_snapshot();
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    CHECK(view.invalid_time_samples==2 && view.timing_samples==1 && !view.write_us,
          "invalid_time_is_not_unsigned_elapsed");
#else
    CHECK(!view.invalid_time_samples && !atomic_load(&clock_calls), "quiet_invalid_clock_ignored");
#endif
    CHECK(view.writes==3 && !view.errors, "clock_failure_keeps_write_observations");
}
static void queue(void) {
    native_output_metrics_observe_queue();
    CHECK(native_output_metrics_snapshot().queue_drops_available, "successful_registration_observable");
    for (unsigned i=0;i<4;++i) drop();
    native_output_metrics_t view = native_output_metrics_snapshot();
    CHECK(view.queue_drops_available && view.completion_queue_drops==4,
          "actual_isr_calls_increment_queue_drops");
    CHECK(!view.writes && !atomic_load(&clock_calls), "isr_no_write_clock_side_effects");
}
static void bytes_limit(void) {
    record(SIZE_MAX,SIZE_MAX,ESP_OK,0,0); record(1,1,ESP_OK,0,0);
    native_output_metrics_t view = native_output_metrics_snapshot();
    CHECK(sizeof(size_t)==8, "host_boundary_uses_64bit_size_t");
    CHECK(view.requested_bytes==UINT64_MAX && view.written_bytes==UINT64_MAX && view.saturated,
          "byte_totals_saturate");
}
static void time_limit(void) {
    for(unsigned i=0;i<3;++i) record(1,1,ESP_OK,0,INT64_MAX);
    native_output_metrics_t view = native_output_metrics_snapshot();
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    CHECK(view.write_us==UINT64_MAX && view.max_write_us==INT64_MAX && view.saturated,
          "elapsed_totals_saturate");
#else
    CHECK(!view.write_us && !view.saturated && !atomic_load(&clock_calls), "quiet_no_elapsed_aggregation");
#endif
}
static void count_limit(void) {
    record(2,1,ESP_ERR_TIMEOUT,10,20); drop();
    native_output_metrics_t view=native_output_metrics_snapshot();
    CHECK(view.writes==UINT32_MAX && view.errors==UINT32_MAX && view.timeouts==UINT32_MAX &&
          view.short_writes==UINT32_MAX && view.completion_queue_drops==UINT32_MAX && view.saturated,
          "event_counts_saturate");
}
static void *writer(void *unused) {
    (void)unused;
    for(unsigned i=0;i<5000;++i) {
        int64_t begin=native_output_metrics_begin_write();
        native_output_metrics_end_write(16,16,ESP_OK,begin);
    }
    atomic_fetch_sub(&workers,1); return NULL;
}
static void *isr_writer(void *unused) {
    (void)unused;for(unsigned i=0;i<10000;++i)drop();
    atomic_fetch_sub(&workers,1);return NULL;
}
static void *reader(void *unused) {
    (void)unused;unsigned reads=0;native_output_metrics_t previous={0};
    while(atomic_load(&workers) || reads<2000) {
        native_output_metrics_t view=native_output_metrics_snapshot();
        CHECK(view.writes>=previous.writes && view.completion_queue_drops>=previous.completion_queue_drops,
              "snapshot_counters_monotonic");
        CHECK(view.requested_bytes==(uint64_t)view.writes*16 && view.written_bytes==view.requested_bytes &&
              !view.errors && !view.saturated, "snapshot_write_group_coherent");
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
        CHECK(view.timing_samples==view.writes && !view.write_us, "snapshot_timing_group_coherent");
#endif
        previous=view;++reads;
    }
    return NULL;
}
static void concurrent(void) {
    pthread_t threads[4];atomic_store(&now,20);atomic_store(&workers,3);
    CHECK(!pthread_create(&threads[0],NULL,writer,NULL),"writer0_create");
    CHECK(!pthread_create(&threads[1],NULL,writer,NULL),"writer1_create");
    CHECK(!pthread_create(&threads[2],NULL,isr_writer,NULL),"isr_create");
    CHECK(!pthread_create(&threads[3],NULL,reader,NULL),"reader_create");
    for(unsigned i=0;i<4;++i)CHECK(!pthread_join(threads[i],NULL),"thread_join");
    native_output_metrics_t view=native_output_metrics_snapshot();
    CHECK(view.writes==10000 && view.completion_queue_drops==10000 && view.requested_bytes==160000,
          "concurrent_events_preserved");
}
int main(int argc,char **argv) {
    CHECK(argc==2,"case_argument");
    if(!strcmp(argv[1],"initial"))initial();
    else if(!strcmp(argv[1],"writes"))writes();
    else if(!strcmp(argv[1],"clocks"))clocks();
    else if(!strcmp(argv[1],"queue"))queue();
    else if(!strcmp(argv[1],"bytes-limit"))bytes_limit();
    else if(!strcmp(argv[1],"time-limit"))time_limit();
    else if(!strcmp(argv[1],"count-limit"))count_limit();
    else if(!strcmp(argv[1],"concurrent"))concurrent();
    else CHECK(false,"known_case");
    printf("PASS:%s\n",argv[1]);return 0;
}
