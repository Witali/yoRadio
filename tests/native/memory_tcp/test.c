#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdarg.h>
#include "memory_tcp_snapshot.h"

static unsigned critical_depth, callbacks, logs;
static uint32_t ticks;
static int queue_mode;
static void (*pending_fn)(void *);
static void *pending_arg;
static struct tcp_pcb *tcp_active_pcbs, *tcp_tw_pcbs;
#define portTICK_PERIOD_MS 1U
#define ERR_OK 0
#define taskENTER_CRITICAL() do { assert(critical_depth == 0); ++critical_depth; } while (0)
#define taskEXIT_CRITICAL() do { assert(critical_depth == 1); --critical_depth; } while (0)
static uint32_t xTaskGetTickCount(void) { return ticks; }
static void log_stub(const char *tag, const char *fmt, ...) {
    (void)tag; (void)fmt; assert(!critical_depth); ++logs;
}
#define ESP_LOGE(...) log_stub(__VA_ARGS__)
static int tcpip_try_callback(void (*fn)(void *), void *arg) {
    assert(!critical_depth); ++callbacks;
    if (queue_mode == 1) return -1;
    if (queue_mode == 2) fn(arg);
    else { assert(!pending_fn); pending_fn = fn; pending_arg = arg; }
    return ERR_OK;
}
static void run_pending(void) {
    assert(pending_fn); void (*fn)(void *) = pending_fn; void *arg = pending_arg;
    pending_fn = NULL; pending_arg = NULL; fn(arg);
}
typedef struct { unsigned total, free, low, largest, iram_free, blocks; bool valid; } heap_sample_t;
static heap_sample_t sample_heap(void) {
    assert(!critical_depth);
    return (heap_sample_t){.free=6000,.low=4000,.largest=3000,.blocks=7,.valid=true};
}
#include "functions.inc"

int main(void) {
    struct pbuf tail = {.tot_len=100,.len=100};
    struct pbuf head = {.next=&tail,.tot_len=300,.len=200};
    struct pbuf refused = {.tot_len=71,.len=71};
    struct tcp_seg ooseq2 = {.p=NULL,.len=40};
    struct tcp_seg ooseq = {.next=&ooseq2,.p=&head,.len=300};
    struct tcp_seg sent2 = {.len=17}, sent = {.next=&sent2,.len=31};
    struct tcp_seg unsent = {.len=99};
    struct tcp_pcb tw2 = {0}, tw = {.next=&tw2};
    struct tcp_pcb client = {.local_port=12345,.state=4,.rcv_wnd=2112,
        .ooseq=&ooseq,.refused_data=&refused,.unacked=&sent,.unsent=&unsent};
    struct tcp_pcb web = {.next=&client,.local_port=80,.state=5,.rcv_wnd=100};
    tcp_active_pcbs=&web; tcp_tw_pcbs=&tw;
    memory_tcp_snapshot_t snap;
    memory_tcp_capture(&snap,tcp_active_pcbs,tcp_tw_pcbs,99);
    assert(sizeof(snap) == 64 && snap.sampled_ms == 99 && snap.timewait == 2);
    assert(snap.web.pcbs == 1 && snap.web.states == 32 && snap.web.window == 100);
    assert(snap.client.pcbs == 1 && snap.client.states == 16 && snap.client.window == 2112);
    assert(snap.client.ooseq == (TCP_QUEUE_OOSEQ ? 300 : 0)); /* Not300+100. */
    assert(snap.client.refused == 71 && snap.client.unacked == 48 && snap.client.unsent == 99);
    assert(head.next == &tail && client.refused_data == &refused && client.unacked == &sent);
    client.state=32; memory_tcp_capture(&snap,&client,NULL,100); assert(snap.client.states==0);
    client.state=4;
    memory_tcp_capture(&snap,NULL,NULL,101);assert(snap.web.pcbs==0&&snap.client.pcbs==0&&snap.timewait==0);

    char json[1088];
    assert(memory_profile_json(NULL,sizeof(json))==-1 && callbacks==0);
    assert(memory_profile_json(json,0)==-1 && callbacks==0);
    ticks=10; assert(memory_profile_json(json,sizeof(json))>0);
    assert(callbacks==1 && strstr(json,"\"tcp_valid\":false") && strstr(json,"\"tcp_pending\":true"));
    assert(memory_profile_json(json,sizeof(json))>0 && callbacks==1); /* Coalesced. */
    ticks=20; run_pending(); assert(!s_tcp_pending && logs==0);
    ticks=30; queue_mode=1; assert(memory_profile_json(json,sizeof(json))>0);
    assert(callbacks==2 && strstr(json,"\"tcp_age_ms\":10") && strstr(json,"\"tcp_pending\":false"));
    assert(strstr(json,"\"tcp_queue_failures\":1") && strstr(json,"\"current_dram\":6000"));
    assert(strstr(json,"\"tcp_timewait\":2") && strstr(json,"\"largest_dram\":3000"));
    queue_mode=0; assert(memory_profile_json(json,sizeof(json))>0 && callbacks==3);
    ticks=UINT32_MAX-1; run_pending(); ticks=5;
    assert(memory_profile_json(json,sizeof(json))>0 && strstr(json,"\"tcp_age_ms\":7"));
    assert(memory_profile_json(json,8)==-1); /* No truncated successful JSON. */
    run_pending(); queue_mode=2; assert(memory_profile_json(json,sizeof(json))>0);
    assert(strstr(json,"\"tcp_pending\":false") && strstr(json,"\"tcp_age_ms\":0"));
    request_tcp_sample((void *)&s_tcp_log_request); assert(logs>0);
    assert(!critical_depth && !s_tcp_pending);
    puts("TCP payloads, empty/chained queues, coalescing, failure/retry, immediate callback and age wrap PASS");
    return 0;
}
