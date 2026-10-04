#include "network_heap_profile_stubs/network_heap_profile_stubs.h"
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

int test_lock, test_core;
struct tcp_pcb *tcp_active_pcbs, *tcp_tw_pcbs, *tcp_bound_pcbs;
union test_listen tcp_listen_pcbs;
static struct tcpip_callback_msg message;
static unsigned allocations, posts;
static int allocation_fails, posting_fails, queued;
static int64_t now_us;
static char last_log[768];

struct tcpip_callback_msg *tcpip_callbackmsg_new(void (*fn)(void *), void *context) {
    assert(!test_core && !test_lock);
    ++allocations;
    if (allocation_fails) return NULL;
    message.function = fn; message.context = context;
    return &message;
}
int tcpip_callbackmsg_trycallback(struct tcpip_callback_msg *msg) {
    assert(!test_lock && !test_core && msg == &message);
    ++posts;
    if (posting_fails) return ERR_MEM;
    assert(!queued); queued = 1; return ERR_OK;
}
void heap_caps_get_info(multi_heap_info_t *info, unsigned caps) {
    assert(test_core && !test_lock && caps == MALLOC_CAP_8BIT);
    *info = (multi_heap_info_t){10000, 4096, 5000, 40, 5};
}
int64_t esp_timer_get_time(void) { return now_us++; }
void test_log(const char *format, ...) {
    assert(!test_core && !test_lock);
    va_list args; va_start(args, format);
    vsnprintf(last_log, sizeof(last_log), format, args);
    va_end(args);
}
static void deliver(void) {
    assert(queued); queued = 0; test_core = 1;
    message.function(message.context); test_core = 0;
}

#include "../../idf/esp32c3-oled-native/main/network_heap_profile.c"

int main(void) {
    allocation_fails = 1;
    network_heap_profile_poll();
    assert(!queued && s_missed == 1 && strstr(last_log, "allocation=1"));
    allocation_fails = 0;
    network_heap_profile_poll();
    assert(allocations == 2 && posts == 1 && queued);
    network_heap_profile_poll();
    assert(posts == 1 && queued && s_missed == 2); // Never queue one message twice.

    struct tcp_seg a = {NULL, 100}, b = {&a, 200}, c = {NULL, 73}, d = {NULL, 22};
    struct tcp_pcb second = {NULL, NULL, &c, &d};
    struct tcp_pcb first = {&second, &b, NULL, NULL};
    struct tcp_pcb waiting = {NULL, NULL, NULL, NULL};
    struct tcp_pcb bound = {NULL, NULL, NULL, NULL};
    struct tcp_pcb_listen listener = {NULL};
    tcp_active_pcbs = &first; tcp_tw_pcbs = &waiting; tcp_bound_pcbs = &bound;
    tcp_listen_pcbs.listen_pcbs = &listener;
    deliver();
    assert(!s_pending && s_ready && s_snapshot.sequence == 1);
    assert(s_snapshot.active == 2 && s_snapshot.time_wait == 1 && s_snapshot.bound == 1 && s_snapshot.listening == 1);
    assert(s_snapshot.tx_segments == 3 && s_snapshot.tx_bytes == 373);
    assert(s_snapshot.rx_segments == 1 && s_snapshot.rx_bytes == 22);
    // Snapshot must retain values, not pointers to potentially freed PCB/segments.
    first.unsent = NULL; b.len = 999;
    tcp_active_pcbs = tcp_tw_pcbs = tcp_bound_pcbs = NULL;
    tcp_listen_pcbs.listen_pcbs = NULL;
    now_us += 5000000;
    posting_fails = 1;
    network_heap_profile_poll();
    assert(!s_pending && !queued && s_missed == 3 && allocations == 2);
    posting_fails = 0;
    network_heap_profile_poll();
    deliver();
    assert(s_snapshot.sequence == 2 && !s_snapshot.active && !s_snapshot.tx_bytes && !s_snapshot.rx_bytes);
    now_us += 5000000;
    network_heap_profile_poll();
    assert(strstr(last_log, "seq=2 age_ms=5000 heap=10000 largest=4096 used=5000 blocks=40 free_blocks=5"));
    assert(strstr(last_log, "active=0 tw=0 bound=0 listen=0"));
    assert(strstr(last_log, "missed=3"));
    deliver();
    assert(allocations == 2 && s_snapshot.sequence == 3 && !test_lock);
    puts("network heap callback lifecycle: PASS");
    return 0;
}
