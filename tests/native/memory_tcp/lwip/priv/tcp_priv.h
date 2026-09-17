#pragma once
#include <stdint.h>
struct pbuf { struct pbuf *next; uint16_t tot_len, len; };
struct tcp_seg { struct tcp_seg *next; struct pbuf *p; uint16_t len; };
struct tcp_pcb {
    struct tcp_pcb *next;
    unsigned local_port, remote_port, state, rcv_wnd;
    struct tcp_seg *ooseq, *unsent, *unacked;
    struct pbuf *refused_data;
};
