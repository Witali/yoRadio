#pragma once
#include <stdint.h>
#include "lwip/priv/tcp_priv.h"

/* Diagnostic only. Caller MUST own the TCP/IP thread. These are payload
 * counters, NOT allocated RAM or complete socket receive-queue occupancy.
 * netconn mailboxes, driver buffers and allocator headers are not counted. */
typedef struct {
    uint32_t pcbs, states, window, ooseq, refused, unsent, unacked;
} memory_tcp_group_t;
typedef struct {
    memory_tcp_group_t web, client;
    uint32_t timewait, sampled_ms;
} memory_tcp_snapshot_t;

static inline void memory_tcp_capture(memory_tcp_snapshot_t *out,
                                      const struct tcp_pcb *active,
                                      const struct tcp_pcb *timewait,
                                      uint32_t sampled_ms) {
    *out = (memory_tcp_snapshot_t){.sampled_ms = sampled_ms};
    for (const struct tcp_pcb *p = active; p; p = p->next) {
        memory_tcp_group_t *g = p->local_port == 80 ? &out->web : &out->client;
        ++g->pcbs;
        if ((unsigned)p->state < 32U) g->states |= 1U << (unsigned)p->state;
        g->window += p->rcv_wnd;
#if TCP_QUEUE_OOSEQ
        for (const struct tcp_seg *s = p->ooseq; s; s = s->next)
            if (s->p) g->ooseq += s->p->tot_len;
#endif
        if (p->refused_data) g->refused += p->refused_data->tot_len;
        for (const struct tcp_seg *s = p->unsent; s; s = s->next) g->unsent += s->len;
        for (const struct tcp_seg *s = p->unacked; s; s = s->next) g->unacked += s->len;
    }
    for (const struct tcp_pcb *p = timewait; p; p = p->next) ++out->timewait;
}
