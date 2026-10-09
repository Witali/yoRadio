#include "web_tcp_probe.h"
#include "network_heap_profile.h"

#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "esp_attr.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "lwip/ip.h"
#include "lwip/ip4.h"
#include "lwip/priv/tcp_priv.h"

enum { WEB_TCP_EVENTS = 64, WEB_TCP_NO_PCB = UINT8_MAX,
       WEB_TCP_RX = 0, WEB_TCP_TX = 1, WEB_TCP_POLL_US = 1000000 };
typedef struct {
    uint32_t sequence, at_us;
    uint16_t remote_port;
    uint8_t direction, flags, before, after;
    int8_t result;
    uint8_t pending;
} web_tcp_event_t;
_Static_assert(sizeof(web_tcp_event_t) == 16, "Bounded TCP diagnostic storage");

static RTC_DATA_ATTR web_tcp_event_t s_events[WEB_TCP_EVENTS];
static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
static uint32_t s_read, s_write, s_sequence, s_dropped;

static void record(web_tcp_event_t event) {
    event.at_us = (uint32_t)esp_timer_get_time();
    portENTER_CRITICAL(&s_lock);
    event.sequence = ++s_sequence;
    if (s_write - s_read == WEB_TCP_EVENTS) {
        ++s_dropped;
    } else {
        s_events[s_write % WEB_TCP_EVENTS] = event;
        ++s_write;
    }
    portEXIT_CRITICAL(&s_lock);
}

static uint8_t state_for(uint16_t remote_port, const ip_addr_t *remote_ip) {
    LWIP_ASSERT_CORE_LOCKED();
    for (const struct tcp_pcb *pcb = tcp_active_pcbs; pcb; pcb = pcb->next)
        if (pcb->local_port == WEB_TCP_PROBE_PORT && pcb->remote_port == remote_port &&
            ip_addr_eq(&pcb->remote_ip, remote_ip)) return (uint8_t)pcb->state;
    return WEB_TCP_NO_PCB;
}

static uint8_t pending_accepts(void) {
    LWIP_ASSERT_CORE_LOCKED();
#if TCP_LISTEN_BACKLOG
    for (const struct tcp_pcb_listen *pcb = tcp_listen_pcbs.listen_pcbs; pcb; pcb = pcb->next)
        if (pcb->local_port == WEB_TCP_PROBE_PORT) return pcb->accepts_pending;
#endif
    return WEB_TCP_NO_PCB;
}

void __real_tcp_input(struct pbuf *packet, struct netif *interface);
void __wrap_tcp_input(struct pbuf *packet, struct netif *interface) {
    struct tcp_hdr header;
    bool watched = packet && packet->len >= TCP_HLEN;
    if (watched) {
        memcpy(&header, packet->payload, sizeof(header));
        watched = lwip_ntohs(header.dest) == WEB_TCP_PROBE_PORT;
    }
    web_tcp_event_t event = {0};
    ip_addr_t remote_ip;
    if (watched) {
        // Packet ownership stays entirely with lwIP. Copy metadata before the
        // real input path changes or frees its pbuf; never inspect it afterwards.
        ip_addr_copy(remote_ip, *ip_current_src_addr());
        event.remote_port = lwip_ntohs(header.src);
        event.flags = TCPH_FLAGS(&header);
        event.before = state_for(event.remote_port, &remote_ip);
        watched = (event.flags & TCP_SYN) || event.before == SYN_RCVD;
    }
    __real_tcp_input(packet, interface);
    if (watched) {
        event.after = state_for(event.remote_port, &remote_ip);
        event.pending = pending_accepts();
        event.direction = WEB_TCP_RX;
        record(event);
    }
}

err_t __real_ip4_output_if(struct pbuf *packet, const ip4_addr_t *source,
                          const ip4_addr_t *destination, u8_t ttl, u8_t tos,
                          u8_t protocol, struct netif *interface);
err_t __wrap_ip4_output_if(struct pbuf *packet, const ip4_addr_t *source,
                          const ip4_addr_t *destination, u8_t ttl, u8_t tos,
                          u8_t protocol, struct netif *interface) {
    struct tcp_hdr header;
    bool watched = protocol == IP_PROTO_TCP && destination != LWIP_IP_HDRINCL &&
                   packet && packet->len >= TCP_HLEN;
    if (watched) {
        memcpy(&header, packet->payload, sizeof(header));
        watched = lwip_ntohs(header.src) == WEB_TCP_PROBE_PORT &&
                  (TCPH_FLAGS(&header) & (TCP_SYN | TCP_RST));
    }
    web_tcp_event_t event = {0};
    if (watched) {
        event.remote_port = lwip_ntohs(header.dest);
        event.flags = TCPH_FLAGS(&header);
        event.direction = WEB_TCP_TX;
        event.before = event.after = WEB_TCP_NO_PCB;
        event.pending = pending_accepts();
    }
    err_t result = __real_ip4_output_if(packet, source, destination, ttl, tos, protocol, interface);
    if (watched) {
        event.result = (int8_t)result;
        record(event);
    }
    return result;
}

void web_tcp_probe_poll(void) {
    // Logging and heap sampling never run in TCP input/output or its core lock.
    for (unsigned n = 0; n < WEB_TCP_EVENTS; ++n) {
        web_tcp_event_t event;
        portENTER_CRITICAL(&s_lock);
        bool available = s_read != s_write;
        if (available) event = s_events[s_read++ % WEB_TCP_EVENTS];
        uint32_t dropped = s_dropped;
        portEXIT_CRITICAL(&s_lock);
        if (!available) break;
        ESP_LOGI("web_tcp", "PERF WEB_TCP: seq=%" PRIu32 " us=%" PRIu32
                 " dir=%u port=%u flags=%u before=%u after=%u result=%d pending=%u dropped=%" PRIu32,
                 event.sequence, event.at_us, (unsigned)event.direction, (unsigned)event.remote_port,
                 (unsigned)event.flags, (unsigned)event.before, (unsigned)event.after,
                 (int)event.result, (unsigned)event.pending, dropped);
    }
    static int64_t previous_us;
    int64_t now = esp_timer_get_time();
    if (now - previous_us >= WEB_TCP_POLL_US) {
        previous_us = now;
        network_heap_profile_poll();
    }
}
