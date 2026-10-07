#include "network_heap_profile.h"

#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "lwip/priv/tcp_priv.h"
#include "lwip/tcpip.h"

typedef struct {
    int64_t sampled_us;
    uint32_t sequence, walk_us;
    uint32_t free_bytes, largest_bytes, used_bytes, used_blocks, free_blocks;
    uint32_t active, time_wait, bound, listening;
    uint32_t tx_segments, tx_bytes, rx_segments, rx_bytes;
} network_heap_snapshot_t;

static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
static network_heap_snapshot_t s_snapshot;
static struct tcpip_callback_msg *s_message;
static bool s_pending, s_ready;
static uint32_t s_missed;

static void count_segments(const struct tcp_seg *segment,
                           uint32_t *count, uint32_t *bytes) {
    for (; segment; segment = segment->next) {
        ++*count;
        *bytes += segment->len;
    }
}

static void collect(void *context) {
    (void)context;
    // All list traversal happens on the owning lwIP thread. No list/pbuf
    // pointer or packet content escapes this callback.
    LWIP_ASSERT_CORE_LOCKED();
    network_heap_snapshot_t next = {0};
    const int64_t started = esp_timer_get_time();
    for (const struct tcp_pcb *pcb = tcp_active_pcbs; pcb; pcb = pcb->next) {
        ++next.active;
        count_segments(pcb->unsent, &next.tx_segments, &next.tx_bytes);
        count_segments(pcb->unacked, &next.tx_segments, &next.tx_bytes);
#if TCP_QUEUE_OOSEQ
        count_segments(pcb->ooseq, &next.rx_segments, &next.rx_bytes);
#endif
    }
    for (const struct tcp_pcb *pcb = tcp_tw_pcbs; pcb; pcb = pcb->next) ++next.time_wait;
    for (const struct tcp_pcb *pcb = tcp_bound_pcbs; pcb; pcb = pcb->next) ++next.bound;
    for (const struct tcp_pcb_listen *pcb = tcp_listen_pcbs.listen_pcbs;
         pcb; pcb = pcb->next) ++next.listening;

    multi_heap_info_t heap;
    heap_caps_get_info(&heap, MALLOC_CAP_8BIT);
    next.free_bytes = heap.total_free_bytes;
    next.largest_bytes = heap.largest_free_block;
    next.used_bytes = heap.total_allocated_bytes;
    next.used_blocks = heap.allocated_blocks;
    next.free_blocks = heap.free_blocks;
    next.sampled_us = esp_timer_get_time();
    next.walk_us = (uint32_t)(next.sampled_us - started);
    // Heap regions are inspected sequentially, not atomically across tasks.
    // Segment lengths count queued TCP payload, not unique allocated RAM.
    portENTER_CRITICAL(&s_lock);
    next.sequence = s_snapshot.sequence + 1;
    s_snapshot = next;
    s_ready = true;
    s_pending = false;
    portEXIT_CRITICAL(&s_lock);
}

void network_heap_profile_poll(void) {
    // One persistent lwIP callback message; no per-sample message allocation.
    // Only this HTTP-thread function creates/posts it. It lives until reboot.
    if (!s_message) {
        s_message = tcpip_callbackmsg_new(collect, NULL);
        if (!s_message) {
            ++s_missed;
            ESP_LOGW("net_heap", "PERF NET_HEAP_WAIT: allocation=1 missed=%u", (unsigned)s_missed);
            return;
        }
    }
    network_heap_snapshot_t previous;
    portENTER_CRITICAL(&s_lock);
    const bool ready = s_ready;
    if (ready) previous = s_snapshot;
    s_ready = false;
    const bool pending = s_pending;
    if (!pending) s_pending = true;
    portEXIT_CRITICAL(&s_lock);

    if (ready) {
        const int64_t age_ms = (esp_timer_get_time() - previous.sampled_us) / 1000;
        ESP_LOGI("net_heap",
                 "PERF NET_HEAP: seq=%u age_ms=%" PRId64 " heap=%u largest=%u used=%u"
                 " blocks=%u free_blocks=%u active=%u tw=%u bound=%u listen=%u"
                 " tx_segments=%u tx_bytes=%u rx_segments=%u rx_bytes=%u missed=%u walk_us=%u",
                 (unsigned)previous.sequence, age_ms,
                 (unsigned)previous.free_bytes, (unsigned)previous.largest_bytes,
                 (unsigned)previous.used_bytes, (unsigned)previous.used_blocks,
                 (unsigned)previous.free_blocks, (unsigned)previous.active,
                 (unsigned)previous.time_wait, (unsigned)previous.bound,
                 (unsigned)previous.listening, (unsigned)previous.tx_segments,
                 (unsigned)previous.tx_bytes, (unsigned)previous.rx_segments,
                 (unsigned)previous.rx_bytes, (unsigned)s_missed, (unsigned)previous.walk_us);
    }
    if (pending || tcpip_callbackmsg_trycallback(s_message) != ERR_OK) {
        ++s_missed;
        if (!pending) {
            portENTER_CRITICAL(&s_lock);
            s_pending = false;
            portEXIT_CRITICAL(&s_lock);
        }
        ESP_LOGW("net_heap", "PERF NET_HEAP_WAIT: pending=%u missed=%u",
                 (unsigned)pending, (unsigned)s_missed);
    }
}
