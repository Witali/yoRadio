// Platform doubles around the unchanged firmware wrappers. No live network.
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#define CONFIG_YORADIO_WEB_TCP_PROBE 1
#define RTC_DATA_ATTR
#define IP_PROTO_TCP 6
#define LWIP_IP_HDRINCL NULL
#define TCP_HLEN 20
#define TCP_SYN 2
#define TCP_RST 4
#define TCP_ACK 16
#define SYN_RCVD 3
#define ESTABLISHED 4
#define lwip_ntohs ntohs
#define TCPH_FLAGS(h) ((h)->flags)
typedef uint8_t u8_t;
typedef int8_t err_t;
typedef struct { uint32_t addr; } ip_addr_t;
typedef ip_addr_t ip4_addr_t;
#define ip_addr_eq(a,b) ((a)->addr == (b)->addr)
#define ip_addr_copy(a,b) ((a) = (b))
static ip_addr_t current_source = {123};
#define ip_current_src_addr() (&current_source)
struct netif { int id; };
struct pbuf { void *payload; uint16_t len; };
struct tcp_hdr { uint16_t src, dest; uint8_t flags, rest[15]; };
_Static_assert(sizeof(struct tcp_hdr) == TCP_HLEN, "TCP header stub length");
struct tcp_pcb {
    struct tcp_pcb *next;
    uint16_t local_port, remote_port;
    ip_addr_t remote_ip;
    uint8_t state;
};
struct tcp_pcb_listen { struct tcp_pcb_listen *next; uint16_t local_port; uint8_t accepts_pending; };
static struct tcp_pcb *tcp_active_pcbs;
static struct { struct tcp_pcb_listen *listen_pcbs; } tcp_listen_pcbs;
static bool in_core;
#define LWIP_ASSERT_CORE_LOCKED() assert(in_core)
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(lock) do { assert(!*(lock)); ++*(lock); } while (0)
#define portEXIT_CRITICAL(lock) do { assert(*(lock) == 1); --*(lock); } while (0)
static int64_t now_us;
static int64_t esp_timer_get_time(void) { return ++now_us; }
static unsigned heap_polls, logs;
static char last_log[512];
static void network_heap_profile_poll(void) { assert(!in_core); ++heap_polls; }
static void log_line(const char *tag, const char *format, ...) {
    assert(!in_core); assert(!strcmp(tag, "web_tcp"));
    va_list args; va_start(args, format);
    vsnprintf(last_log, sizeof(last_log), format, args); va_end(args); ++logs;
}
#define ESP_LOGI log_line
/* PRODUCTION_HEADER */
/* PRODUCTION_SOURCE */

static struct netif interface = {42};
static struct pbuf *expected_packet;
static unsigned input_calls, output_calls;
static bool complete_handshake, emit_response;
static struct tcp_pcb active;
static err_t output_result;
static ip4_addr_t source = {456}, destination = {123};
static const ip4_addr_t *expected_destination;
static u8_t expected_protocol;

err_t __real_ip4_output_if(struct pbuf *packet, const ip4_addr_t *src,
                          const ip4_addr_t *dest, u8_t ttl, u8_t tos,
                          u8_t protocol, struct netif *netif) {
    assert(in_core && packet == expected_packet && netif == &interface);
    assert(src == &source && dest == expected_destination);
    assert(ttl == 64 && tos == 8 && protocol == expected_protocol);
    ++output_calls;
    // Real output may prepend/change headers. The recorded event must not.
    if (packet) { memset(packet->payload, 0xa5, packet->len); free(packet->payload); free(packet); }
    return output_result;
}

static struct pbuf *packet(uint16_t src, uint16_t dest, uint8_t flags, unsigned length) {
    struct pbuf *p = malloc(sizeof(*p)); assert(p);
    p->payload = calloc(length ? length : 1, 1); assert(p->payload); p->len = length;
    if (length >= TCP_HLEN) {
        struct tcp_hdr h = {.src=htons(src), .dest=htons(dest), .flags=flags};
        memcpy(p->payload, &h, sizeof(h));
    }
    return p;
}

static void send_output(uint16_t src, uint16_t dest, uint8_t flags, unsigned length,
                        const ip4_addr_t *dest_ip, u8_t protocol) {
    expected_packet = packet(src, dest, flags, length);
    expected_destination = dest_ip; expected_protocol = protocol;
    in_core = true;
    assert(__wrap_ip4_output_if(expected_packet, &source, dest_ip, 64, 8, protocol, &interface) == output_result);
    in_core = false;
}

void __real_tcp_input(struct pbuf *p, struct netif *netif) {
    assert(in_core && p == expected_packet && netif == &interface); ++input_calls;
    if (p) { memset(p->payload, 0xa5, p->len); free(p->payload); free(p); }
    if (emit_response) {
        // Nested transmit is logged before the outer RX completion event.
        send_output(80, 32000, TCP_SYN | TCP_ACK, TCP_HLEN, &destination, IP_PROTO_TCP);
        in_core = true;
    }
    if (complete_handshake) active.state = ESTABLISHED;
    else if (emit_response) tcp_active_pcbs = &active;
    current_source.addr = 999; // Prove the saved remote IP is used after input.
}

static void receive(uint16_t dest, uint8_t flags, unsigned length) {
    current_source.addr = 123;
    expected_packet = packet(32000, dest, flags, length);
    in_core = true; __wrap_tcp_input(expected_packet, &interface); in_core = false;
}

int main(void) {
    struct tcp_pcb_listen listener = {.local_port=80,.accepts_pending=2};
    tcp_listen_pcbs.listen_pcbs = &listener;
    active = (struct tcp_pcb){.local_port=80,.remote_port=32000,.remote_ip={123},.state=SYN_RCVD};
    emit_response = true;
    receive(80, TCP_SYN, TCP_HLEN);
    assert(input_calls == 1 && output_calls == 1 && s_write == 2);
    assert(s_events[0].direction == WEB_TCP_TX && s_events[0].flags == (TCP_SYN|TCP_ACK));
    assert(s_events[1].direction == WEB_TCP_RX && s_events[1].before == WEB_TCP_NO_PCB);
    assert(s_events[1].after == SYN_RCVD && s_events[1].remote_port == 32000);
    assert(s_events[1].pending == (TCP_LISTEN_BACKLOG ? 2 : WEB_TCP_NO_PCB));
    emit_response = false; complete_handshake = true;
    receive(80, TCP_ACK, TCP_HLEN);
    assert(s_events[2].before == SYN_RCVD && s_events[2].after == ESTABLISHED);
    complete_handshake = false;
    receive(80, TCP_ACK, TCP_HLEN); // Established data is not retained.
    receive(81, TCP_SYN, TCP_HLEN); receive(80, TCP_SYN, TCP_HLEN-1);
    assert(input_calls == 5 && s_write == 3);
    expected_packet = NULL; in_core = true; __wrap_tcp_input(NULL, &interface); in_core = false;
    assert(input_calls == 6 && s_write == 3);
    output_result = -7;
    send_output(80,32000,TCP_RST,TCP_HLEN,&destination,IP_PROTO_TCP);
    assert(s_events[3].result == -7 && s_events[3].flags == TCP_RST);
    send_output(80,32000,TCP_ACK,TCP_HLEN,&destination,IP_PROTO_TCP);
    send_output(81,32000,TCP_SYN,TCP_HLEN,&destination,IP_PROTO_TCP);
    send_output(80,32000,TCP_SYN,TCP_HLEN-1,&destination,IP_PROTO_TCP);
    send_output(80,32000,TCP_SYN,TCP_HLEN,LWIP_IP_HDRINCL,IP_PROTO_TCP);
    send_output(80,32000,TCP_SYN,TCP_HLEN,&destination,17);
    assert(output_calls == 7 && s_write == 4);
    now_us = WEB_TCP_POLL_US;
    web_tcp_probe_poll(); assert(logs == 4 && heap_polls == 1 && s_read == s_write);
    assert(strstr(last_log,"port=32000") && strstr(last_log,"result=-7"));
    web_tcp_probe_poll(); assert(logs == 4 && heap_polls == 1);
    // Exercise both unsigned queue-index wrap and saturation without overwrite.
    s_read = s_write = UINT32_MAX-31;
    for (unsigned n=0;n<WEB_TCP_EVENTS+5;++n) {
        in_core=true; record((web_tcp_event_t){.remote_port=(uint16_t)n}); in_core=false;
    }
    assert(s_dropped == 5 && s_write-s_read == WEB_TCP_EVENTS);
    assert(s_events[s_read % WEB_TCP_EVENTS].remote_port == 0);
    web_tcp_probe_poll(); assert(logs == 68 && s_read == s_write);
    assert(strstr(last_log,"port=63") && strstr(last_log,"dropped=5"));
    puts("PASS TCP probe: input ownership, exact forwarding, states, filters, bounded ring and wrap");
    return 0;
}
