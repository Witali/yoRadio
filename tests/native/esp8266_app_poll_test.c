#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <setjmp.h>

typedef uint32_t TickType_t;
#define pdMS_TO_TICKS(ms) (ms)
#define pdTRUE 1
static jmp_buf finished;
static uint32_t elapsed_ms, origin, pending;
static unsigned input_polls, waits, led_updates, service_calls[6];
static uint32_t service_times[128];
static uint32_t led_tick;
static bool events, delayed_service, debounce_posted;
static unsigned event_index;
static const uint32_t event_times[] = {75, 243, 612};
static TickType_t xTaskGetTickCount(void) { return origin + elapsed_ms; }
static void input_service_poll(void) { ++input_polls; }
static void radio_control_flush_pending(void) { ++service_calls[0]; }
static void network_service_poll(void) { ++service_calls[1]; }
static void time_service_poll(void) { ++service_calls[2]; }
static void web_service_poll(void) {
    assert(service_calls[3] < 128);
    service_times[service_calls[3]++] = elapsed_ms;
}
static void memory_profile_poll(void) { ++service_calls[4]; }
static void spiffs_log_poll(void) {
    ++service_calls[5];
    if (delayed_service && service_calls[5] == 2) elapsed_ms += 310;
}
static TickType_t input_service_wait_ticks(TickType_t maximum) {
    /* A BOOT debounce timer may shorten the wait without a notification. */
    if (events && elapsed_ms < 115 && 115 - elapsed_ms < maximum)
        return 115 - elapsed_ms;
    return maximum;
}
#if CONFIG_YORADIO_STATUS_LED
static void status_led_poll(void) {
    if ((TickType_t)(xTaskGetTickCount() - led_tick) >= pdMS_TO_TICKS(1000U / LED_HZ)) {
        ++led_updates; led_tick = xTaskGetTickCount();
    }
}
static TickType_t status_led_wait_ticks(TickType_t maximum) {
    TickType_t elapsed = xTaskGetTickCount() - led_tick;
    TickType_t remaining = elapsed >= 1000U / LED_HZ ? 0 : 1000U / LED_HZ - elapsed;
    return remaining < maximum ? remaining : maximum;
}
#endif
static uint32_t ulTaskNotifyTake(int clear, TickType_t wait) {
    assert(clear == pdTRUE && ++waits < 250); // Reject a busy loop.
    if (events && elapsed_ms == 115 && !debounce_posted) {
        pending = 1; debounce_posted = true; // Debounce action posts state once.
    }
    if (pending) { uint32_t result = pending; pending = 0; return result; }
    uint32_t next = elapsed_ms + wait;
    if (events && event_index < 3 && event_times[event_index] <= next) {
        elapsed_ms = event_times[event_index++]; return 1;
    }
    if (next > 2000) longjmp(finished, 1);
    elapsed_ms = next;
    return 0;
}
static void run_actual_loop(void) {
    /* APP_LOOP */
}
static void run_case(bool with_events, bool slow_service, uint32_t first_tick) {
    elapsed_ms = pending = input_polls = waits = led_updates = event_index = 0;
    origin = led_tick = first_tick; events = with_events; delayed_service = slow_service;
    debounce_posted = false;
    memset(service_calls, 0, sizeof(service_calls)); memset(service_times, 0, sizeof(service_times));
    if (!setjmp(finished)) run_actual_loop();
    for (unsigned i = 0; i < 6; ++i) assert(service_calls[i] == service_calls[0]);
    if (!with_events && !slow_service) {
        assert(service_calls[3] == 9);
        for (unsigned i = 0; i < 9; ++i) assert(service_times[i] == i * 250U);
#if CONFIG_YORADIO_STATUS_LED
        assert(led_updates == 2 * LED_HZ);
#else
        assert(led_updates == 0);
#endif
    }
    if (with_events) {
        assert(event_index == 3);
        for (unsigned event = 0; event < 3; ++event) {
            bool found = false;
            for (unsigned i = 0; i < service_calls[3]; ++i) found |= service_times[i] == event_times[event];
            assert(found); // User/state events cannot wait for a 250-ms poll.
        }
        bool debounce_sent = false;
        for (unsigned i = 0; i < service_calls[3]; ++i) debounce_sent |= service_times[i] == 115;
        assert(debounce_sent);
        assert(service_calls[3] <= 13);
    }
    if (slow_service) {
        assert(service_times[1] == 250 && service_times[2] == 560);
        assert(service_times[3] == 810); // No replay of missed periodic ticks.
    }
}
int main(void) {
    run_case(false, false, 0);
    run_case(false, false, UINT32_MAX - 101);
    run_case(true, false, 0);
    run_case(true, false, UINT32_MAX - 101);
    run_case(false, true, 0);
    puts("app poll PASS: 4-Hz services, independent LED rate, immediate events, wrap and delayed service");
    return 0;
}
