#pragma once
#include <stdint.h>

/* Optional lwIP hook: observe already demultiplexed TCP payloads on WebUI's
 * port only. Never retain packet contents, change a packet or reject it.
 * tcp_input has converted sequence fields to host order and removed headers.
 * LISTEN pcbs share only a prefix with full pcbs; do not read rcv_nxt there. */
void httpd_trace_tcp_packet(uint16_t port, uint16_t length,
                            uint32_t sequence, uint32_t expected);
#define LWIP_HOOK_TCP_INPACKET_PCB(pcb, hdr, optlen, opt1len, opt2, p) \
    (((pcb)->state != LISTEN && (pcb)->local_port == 80 && (p)->tot_len) ? \
     (httpd_trace_tcp_packet((pcb)->remote_port, (p)->tot_len, \
                             (hdr)->seqno, (pcb)->rcv_nxt), 0) : 0)
