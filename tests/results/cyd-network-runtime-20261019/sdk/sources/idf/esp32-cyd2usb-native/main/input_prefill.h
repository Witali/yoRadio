#pragma once

// Decoder-owned first-input wait. The caller holds a READING lease, so count
// every occupied slot, including producer WRITING leases, when detecting full.
// The independent startup control lease must bypass this wait: the producer
// may need it returned before it can publish another candidate.
static bool prefill_encoded_input(uint32_t generation, uint32_t maximum_ms) {
    if (!maximum_ms) return STREAM_INPUT_ACTIVE(generation);
    const int64_t started = esp_timer_get_time();
    const int64_t maximum_us = (int64_t)maximum_ms * 1000;
    TickType_t poll = pdMS_TO_TICKS(5);
    if (!poll) poll = 1;
    while (STREAM_INPUT_ACTIVE(generation)) {
        adaptive_input_stats_t stats = adaptive_input_stats(s_encoded);
        if (!stats.resident) return false;
        if (stats.occupied >= stats.resident ||
            esp_timer_get_time() - started >= maximum_us)
            return STREAM_INPUT_ACTIVE(generation);
        vTaskDelay(poll);
    }
    return false;
}
