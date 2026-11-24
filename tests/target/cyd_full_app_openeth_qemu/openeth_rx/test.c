/* Execute the pinned SDK RX task/receive functions with owned DMA descriptors.
 * SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <inttypes.h>
#include <setjmp.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int esp_err_t;
typedef struct { int unused; } esp_eth_mac_t;
typedef struct esp_eth_mediator_s {
    esp_err_t (*stack_input)(struct esp_eth_mediator_s *, uint8_t *, uint32_t);
} esp_eth_mediator_t;
#include "descriptor.inc"
enum { ESP_OK, ESP_ERR_INVALID_STATE, ESP_ERR_INVALID_SIZE, ESP_ERR_NO_MEM };
enum { RX_BUF_COUNT = 4, DMA_BUF_SIZE = 1600, ETH_MAX_PACKET_SIZE = 1522 };
enum { MALLOC_CAP_8BIT = 4, MALLOC_CAP_DMA = 8, pdFALSE = 0, portMAX_DELAY = -1 };
#define __containerof(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))
#define ESP_GOTO_ON_FALSE(condition, result, label, ...) do { \
    if (!(condition)) { ret = (result); goto label; } \
} while (0)

typedef struct {
    esp_eth_mac_t parent;
    esp_eth_mediator_t *eth;
    int cur_rx_desc;
} emac_opencores_t;

static openeth_rx_desc_t descriptors[RX_BUF_COUNT];
static uint8_t dma[RX_BUF_COUNT][DMA_BUF_SIZE];
static emac_opencores_t mac;
static jmp_buf task_exit;
static unsigned notifications, calls, failures, frees, live, delivered, delays;
static unsigned warnings, recovered, drops, consumed;
static unsigned expected_slots[RX_BUF_COUNT], expected_count;
static size_t requests[16], available, grant_after_delay;
static bool change_owner_during_allocation, upper_reject;
static uint8_t *allocated;

static openeth_rx_desc_t *openeth_rx_desc(int index) {
    assert(index >= 0 && index < RX_BUF_COUNT);
    return &descriptors[index];
}

static unsigned ulTaskNotifyTake(int clear, int timeout) {
    assert(clear == pdFALSE && timeout == portMAX_DELAY);
    if (!notifications) longjmp(task_exit, 1);
    --notifications;
    return 1;
}

static void vTaskDelay(unsigned ticks) {
    assert(ticks == 1);
    ++delays;
    assert(mac.cur_rx_desc >= 0 && mac.cur_rx_desc < RX_BUF_COUNT);
    /* Failed allocation must retain the same software-owned DMA descriptor. */
    assert(descriptors[mac.cur_rx_desc].e == 0 && live == 0 && delivered == 0);
    if (grant_after_delay) available = grant_after_delay;
    if (delays == 2) longjmp(task_exit, 2);
}

static void vTaskDelete(void *task) { assert(task == NULL); abort(); }
static size_t heap_caps_get_free_size(unsigned caps) { (void)caps; return available; }
static size_t heap_caps_get_largest_free_block(unsigned caps) { (void)caps; return available; }

static void *rx_malloc(size_t bytes) {
    assert(calls < sizeof(requests) / sizeof(requests[0]) && live == 0);
    requests[calls++] = bytes;
    if (bytes > available) {
        ++failures;
        return NULL;
    }
    allocated = malloc(bytes);
    assert(allocated != NULL);
    ++live;
    if (change_owner_during_allocation) descriptors[mac.cur_rx_desc].e = 1;
    return allocated;
}

static void rx_free(void *buffer) {
    assert(buffer != NULL && buffer == allocated && live == 1);
    free(buffer);
    allocated = NULL;
    --live;
    ++frees;
}

static void log_warning(const char *format, ...) {
    if (strstr(format, "CYD_OPENETH_RX_WAIT")) ++warnings;
    if (strstr(format, "CYD_OPENETH_RX_DROP")) ++drops;
}
static void log_info(const char *format, ...) {
    if (strstr(format, "CYD_OPENETH_RX_RECOVERED")) ++recovered;
}
#define ESP_LOGV(...) ((void)0)
#define ESP_LOGW(tag, ...) log_warning(__VA_ARGS__)
#define ESP_LOGI(tag, ...) log_info(__VA_ARGS__)

static esp_err_t emac_opencores_receive(esp_eth_mac_t *, uint8_t *, uint32_t *);
#define malloc rx_malloc
#define free rx_free
#include "receive.inc"
#undef malloc
#undef free

static esp_err_t stack_input(esp_eth_mediator_t *eth, uint8_t *buffer, uint32_t length) {
    assert(eth == mac.eth && delivered < expected_count);
    unsigned slot = expected_slots[delivered++];
    assert(descriptors[slot].e == 1);
    assert(length == descriptors[slot].len);
    /* This also checks the model-supplied FCS/padding bytes remain untouched. */
    assert(memcmp(buffer, dma[slot], length) == 0);
    rx_free(buffer);
    return upper_reject ? ESP_ERR_NO_MEM : ESP_OK;
}

static void reset(void) {
    assert(live == 0);
    static esp_eth_mediator_t mediator = { .stack_input = stack_input };
    memset(&mac, 0, sizeof(mac));
    mac.eth = &mediator;
    memset(descriptors, 0, sizeof(descriptors));
    memset(requests, 0, sizeof(requests));
    for (unsigned i = 0; i < RX_BUF_COUNT; ++i) {
        descriptors[i].e = 1;
        descriptors[i].wr = (i == RX_BUF_COUNT - 1);
        descriptors[i].irq = 1;
        descriptors[i].rxpnt = dma[i];
        for (unsigned n = 0; n < DMA_BUF_SIZE; ++n) dma[i][n] = (uint8_t)(n * 37u + i * 11u);
    }
    notifications = 1;
    calls = failures = frees = delivered = delays = 0;
    warnings = recovered = drops = consumed = expected_count = 0;
    available = ETH_MAX_PACKET_SIZE;
    grant_after_delay = 0;
    change_owner_during_allocation = upper_reject = false;
}

static void frame(unsigned slot, uint16_t length, bool valid) {
    descriptors[slot].e = 0;
    descriptors[slot].len = length;
    ++consumed;
    if (valid) expected_slots[expected_count++] = slot;
}

static int run_task(void) {
    int reason = setjmp(task_exit);
    if (!reason) emac_opencores_rx_task(&mac);
    assert(live == 0);
    return reason;
}

static void check_retired(void) {
    for (unsigned i = 0; i < RX_BUF_COUNT; ++i) assert(descriptors[i].e == 1);
    assert(delivered == expected_count && frees == delivered && mac.cur_rx_desc == (int)(consumed % RX_BUF_COUNT));
}

static bool short_under_pressure(void) {
    reset();
    available = 256;
    frame(0, 64, true);
    int reason = run_task();
    if (reason != 1 || delivered != 1) return false;
    assert(calls == 1 && requests[0] == 64 && failures == 0 && delays == 0 && warnings == 0);
    check_retired();
    return true;
}

int main(void) {
#ifdef MAX_ALLOCATION_CONTROL
    assert(!short_under_pressure());
    assert(calls == 2 && requests[0] == ETH_MAX_PACKET_SIZE && requests[1] == ETH_MAX_PACKET_SIZE);
    assert(failures == 2 && warnings == 1 && delivered == 0 && descriptors[0].e == 0 && mac.cur_rx_desc == 0);
    puts("EXPECTED REJECTION: exact pre-fix MAX allocation cannot deliver a 64-byte frame with heap=256");
    return 17;
#else
    assert(short_under_pressure());

    reset();
    descriptors[0].len = UINT16_MAX;
    descriptors[0].rxpnt = NULL;
    assert(run_task() == 1 && calls == 0 && drops == 0 && mac.cur_rx_desc == 0);

    reset();
    frame(0, ETH_MAX_PACKET_SIZE, true);
    available = 128;
    grant_after_delay = ETH_MAX_PACKET_SIZE;
    assert(run_task() == 1 && calls == 2 && failures == 1 && delays == 1);
    assert(requests[0] == ETH_MAX_PACKET_SIZE && requests[1] == ETH_MAX_PACKET_SIZE);
    assert(warnings == 1 && recovered == 1);
    check_retired();

    const uint16_t lengths[] = {1, 63, 64, 1500, 1518, ETH_MAX_PACKET_SIZE};
    for (unsigned i = 0; i < sizeof(lengths) / sizeof(lengths[0]); ++i) {
        reset();
        frame(0, lengths[i], true);
        available = lengths[i];
        assert(run_task() == 1 && calls == 1 && requests[0] == lengths[i] && failures == 0);
        check_retired();
    }

    const uint16_t malformed[] = {0, ETH_MAX_PACKET_SIZE + 1, DMA_BUF_SIZE + 1, UINT16_MAX};
    for (unsigned i = 0; i < sizeof(malformed) / sizeof(malformed[0]); ++i) {
        reset();
        frame(0, malformed[i], false);
        descriptors[0].rxpnt = NULL; /* A dropped payload must never be read. */
        frame(1, 64, true);
        assert(run_task() == 1 && calls == 1 && requests[0] == 64 && drops == 1);
        check_retired();
    }

    reset();
    frame(0, 64, true);
    uint8_t small[32] = {0};
    uint32_t capacity = sizeof(small);
    assert(emac_opencores_receive(&mac.parent, small, &capacity) == ESP_ERR_INVALID_SIZE);
    assert(capacity == sizeof(small) && descriptors[0].e == 0 && mac.cur_rx_desc == 0);
    for (unsigned i = 0; i < sizeof(small); ++i) assert(small[i] == 0);
    descriptors[0].e = 1;
    assert(emac_opencores_receive(&mac.parent, small, &capacity) == ESP_ERR_INVALID_STATE);
    assert(mac.cur_rx_desc == 0);

    reset();
    frame(0, 64, false);
    change_owner_during_allocation = true;
    assert(run_task() == 1 && calls == 1 && frees == 1 && delivered == 0 && mac.cur_rx_desc == 0);

    reset();
    frame(0, 64, true);
    upper_reject = true;
    assert(run_task() == 1);
    check_retired();

    reset();
    mac.cur_rx_desc = 3;
    frame(3, 64, true);
    frame(0, 0, false);
    frame(1, ETH_MAX_PACKET_SIZE, true);
    assert(run_task() == 1 && calls == 2 && requests[0] == 64 && requests[1] == ETH_MAX_PACKET_SIZE);
    assert(delivered == 2 && frees == 2 && drops == 1 && mac.cur_rx_desc == 2);
    for (unsigned i = 0; i < RX_BUF_COUNT; ++i) assert(descriptors[i].e == 1);

    puts("PASS 18 OpenETH exact-length RX ownership, pressure, bounds, copy and cleanup cases");
    return 0;
#endif
}
