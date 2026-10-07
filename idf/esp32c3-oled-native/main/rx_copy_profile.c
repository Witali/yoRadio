// RX handoff adapted from pinned ESP-IDF 6.0.2 wlanif.c.
// SPDX-FileCopyrightText: 2001-2004 Swedish Institute of Computer Science
// SPDX-FileContributor: 2015-2025 Espressif Systems (Shanghai) CO LTD
// SPDX-License-Identifier: BSD-3-Clause
#include "rx_copy_profile.h"
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_netif_net_stack.h"
#include "esp_rom_crc.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "lwip/mem.h"
#include "lwip/netif.h"
#include "lwip/pbuf.h"

#if !MEM_LIBC_MALLOC || (LWIP_STATS && MEM_STATS)
#error RX copy profiling requires an unshifted libc heap pointer
#endif
#ifndef CONFIG_LWIP_L2_TO_L3_COPY
#error RX copy profiling requires the native packet-copy configuration
#endif

enum {
    RX_COPY_TRACK_SLOTS = 64,
    RX_COPY_SIZE_CLASSES = 5,
    RX_COPY_SMALL_FRAME = 128,
    RX_COPY_MEDIUM_FRAME = 512,
    RX_COPY_STREAM_FRAME = 1152,
    RX_COPY_FULL_FRAME = 1600,
    RX_COPY_LOG_BYTES = 384,
};
#define RX_COPY_REPORT_US INT64_C(5000000)

typedef struct {
    void *allocation;
    uint32_t bytes;
    uint16_t frame_bytes;
    uint8_t size_class;
} rx_copy_owner_t;
typedef struct { uint32_t allocations, live, peak; } rx_copy_class_t;
typedef struct {
    uint32_t sequence, allocations, releases, live, peak, bytes, peak_bytes;
    uint32_t failed, lost, rejected, max_frame, pbuf_bytes, capacity;
    rx_copy_class_t classes[RX_COPY_SIZE_CLASSES];
} rx_copy_record_t;
_Static_assert(sizeof(rx_copy_record_t) == 28 * sizeof(uint32_t), "CRC wire layout");
_Static_assert(RX_COPY_LOG_BYTES >= 28 * 11 + 9, "Bounded uint32 CSV record");

static rx_copy_owner_t s_owners[RX_COPY_TRACK_SLOTS];
static rx_copy_record_t s_counts;
static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;

static unsigned size_class(size_t length) {
    if (length <= RX_COPY_SMALL_FRAME) return 0;
    if (length <= RX_COPY_MEDIUM_FRAME) return 1;
    if (length <= RX_COPY_STREAM_FRAME) return 2;
    if (length <= RX_COPY_FULL_FRAME) return 3;
    return 4; // Preserve oversized-frame evidence, do not silently clamp it.
}

static void track_allocation(struct pbuf *p, uint16_t length) {
    // Called before handing p to lwIP: no other task can free it yet. Heap
    // lookup stays outside our lock. mem_trim is a no-op in the pinned SDK.
    size_t allocated = heap_caps_get_allocated_size(p);
    unsigned kind = size_class(length);
    portENTER_CRITICAL(&s_lock);
    ++s_counts.allocations;
    ++s_counts.classes[kind].allocations;
    if (length > s_counts.max_frame) s_counts.max_frame = length;
    unsigned slot = RX_COPY_TRACK_SLOTS;
    bool duplicate = false;
    for (unsigned i = 0; i < RX_COPY_TRACK_SLOTS; ++i) {
        if (s_owners[i].allocation == p) duplicate = true;
        if (!s_owners[i].allocation && slot == RX_COPY_TRACK_SLOTS) slot = i;
    }
    if (duplicate || slot == RX_COPY_TRACK_SLOTS || allocated > UINT32_MAX) {
        ++s_counts.lost; // Forward normally, but reject this measurement.
    } else {
        s_owners[slot] = (rx_copy_owner_t){p, (uint32_t)allocated, length, kind};
        ++s_counts.live;
        if (s_counts.live > s_counts.peak) s_counts.peak = s_counts.live;
        s_counts.bytes += (uint32_t)allocated;
        if (s_counts.bytes > s_counts.peak_bytes) s_counts.peak_bytes = s_counts.bytes;
        rx_copy_class_t *bucket = &s_counts.classes[kind];
        if (++bucket->live > bucket->peak) bucket->peak = bucket->live;
    }
    portEXIT_CRITICAL(&s_lock);
}

void __real_mem_free(void *pointer);
void __wrap_mem_free(void *pointer) {
    portENTER_CRITICAL(&s_lock);
    for (unsigned i = 0; i < RX_COPY_TRACK_SLOTS; ++i) {
        rx_copy_owner_t *owner = &s_owners[i];
        if (owner->allocation && owner->allocation == pointer) {
            --s_counts.live;
            ++s_counts.releases;
            s_counts.bytes -= owner->bytes;
            --s_counts.classes[owner->size_class].live;
            *owner = (rx_copy_owner_t){0};
            break;
        }
    }
    portEXIT_CRITICAL(&s_lock);
    // The real final free, including non-RX allocations, runs exactly once.
    // pbuf_ref()/chained pbufs retain the SDK's original ownership semantics.
    __real_mem_free(pointer);
}

esp_err_t __wrap_wlanif_input(void *handle, void *buffer, size_t length, void *l2) {
    struct netif *netif = handle;
    esp_netif_t *esp_netif = netif->state;
    if (!buffer || !netif_is_up(netif) || length > UINT16_MAX) {
        if (l2) esp_netif_free_rx_buffer(esp_netif, l2);
        return ESP_FAIL;
    }
    struct pbuf *p = pbuf_alloc(PBUF_RAW, (u16_t)length, PBUF_RAM);
    if (!p) {
        portENTER_CRITICAL(&s_lock);
        ++s_counts.failed;
        portEXIT_CRITICAL(&s_lock);
        esp_netif_free_rx_buffer(esp_netif, l2);
        return ESP_ERR_NO_MEM;
    }
    track_allocation(p, (uint16_t)length);
    memcpy(p->payload, buffer, length);
    esp_netif_free_rx_buffer(esp_netif, l2);
    if (netif->input(p, netif) != ERR_OK) {
        portENTER_CRITICAL(&s_lock);
        ++s_counts.rejected;
        portEXIT_CRITICAL(&s_lock);
        pbuf_free(p);
        return ESP_FAIL;
    }
    return ESP_OK;
}

void rx_copy_profile_poll(void) {
    static int64_t previous;
    int64_t now = esp_timer_get_time();
    if (now - previous < RX_COPY_REPORT_US) return;
    previous = now;
    portENTER_CRITICAL(&s_lock);
    ++s_counts.sequence;
    rx_copy_record_t record = s_counts;
    portEXIT_CRITICAL(&s_lock);
    record.pbuf_bytes = sizeof(struct pbuf);
    record.capacity = RX_COPY_TRACK_SLOTS;
    uint32_t words[sizeof(record) / sizeof(uint32_t)];
    memcpy(words, &record, sizeof(record));
    char line[RX_COPY_LOG_BYTES];
    size_t used = 0;
    for (size_t i = 0; i < sizeof(words) / sizeof(words[0]); ++i) {
        int count = snprintf(line + used, sizeof(line) - used, "%" PRIu32 ",", words[i]);
        if (count < 0 || (size_t)count >= sizeof(line) - used) return;
        used += (size_t)count;
    }
    uint32_t crc = esp_rom_crc32_le(0, (const uint8_t *)words, sizeof(words));
    snprintf(line + used, sizeof(line) - used, "%08" PRIx32, crc);
    // One CRC-protected row per snapshot, no packet contents or addresses.
    ESP_LOGI("rx_copy", "PERF RX_COPY: %s", line);
}
