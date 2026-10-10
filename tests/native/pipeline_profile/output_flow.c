// Included after the actual output-flow helpers extracted from audio_service.c.
int main(void) {
    output_flow_t flow = {0};
    test_now = 10;
    test_overruns = 2;
    output_flow_reset(&flow, true);
    assert(flow.start_us == 10 && flow.overruns == 2);
    flow.empty = (pipeline_wait_t){.us=100, .count=1, .max_us=100};
    flow.submit = (pipeline_wait_t){.us=4900000, .count=450, .max_us=20000};
    test_now += DECODE_STATS_INTERVAL_US - 1;
    output_flow_report(&flow, 7);
    assert(test_logs == 0);
    ++test_now;
    test_overruns = 5;
    test_dma = (pipeline_wait_t){.us=4800000, .count=448, .max_us=11000};
    output_flow_report(&flow, 7);
    assert(test_logs == 1);
    assert(strstr(test_log, "gen=7 window_us=5000000 "));
    assert(strstr(test_log, "empty_us=100 empty_n=1 empty_timeouts=0 empty_max=100 "));
    assert(strstr(test_log, "submit_us=4900000 submit_n=450 submit_max=20000 "));
    assert(strstr(test_log, "overruns=3"));
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
    assert(strstr(test_log, "PERF FLOW_OUT:"));
    assert(strstr(test_log, "dma_us=4800000 dma_n=448 dma_timeouts=0 dma_max=11000 "));
    assert(test_dma_reads == 2);
#else
    assert(strstr(test_log, "PERF FLOW_STAGED_OUT:"));
    assert(!strstr(test_log, "dma_us="));
    assert(test_dma_reads == 0);
#endif
    // The simulated ISR event during logging must survive the report reset.
    assert(test_overruns == 6 && flow.overruns == 5);
    test_now += DECODE_STATS_INTERVAL_US;
    output_flow_report(&flow, 7);
    assert(strstr(test_log, "overruns=1"));
    assert(strstr(test_log, "empty_us=0 empty_n=0 "));
    output_flow_reset(&flow, false);
    test_now += DECODE_STATS_INTERVAL_US;
    output_flow_report(&flow, 8);
    assert(test_logs == 2 && !flow.start_us);
    // Unsigned cumulative counters may wrap; the delta remains correct.
    test_overruns = UINT32_MAX - 1;
    output_flow_reset(&flow, true);
    test_overruns = 1;
    test_now += DECODE_STATS_INTERVAL_US;
    output_flow_report(&flow, 8);
    assert(strstr(test_log, "gen=8 ") && strstr(test_log, "overruns=3"));
    puts("PASS output-flow timing, reset, generation, ISR event and counter wrap");
}
