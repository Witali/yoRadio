#include <assert.h>
#include <malloc.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lwip/pbuf.h"
#include "lwip/netif.h"
#include "lwip/memp.h"
#include "lwip/mem.h"
#include "esp_netif.h"

static _Thread_local int fail_malloc;
void *test_malloc(size_t size) {
    if (fail_malloc) { fail_malloc = 0; return NULL; }
    return malloc(size);
}
void *memp_malloc(memp_t type) { (void)type; assert(!"Unexpected non-RAM pbuf allocation"); return NULL; }
void memp_free(memp_t type, void *pointer) { (void)type; (void)pointer; assert(!"Unexpected memp free"); }
size_t heap_caps_get_allocated_size(void *pointer) { return malloc_usable_size(pointer); }
static int64_t now;
int64_t esp_timer_get_time(void) { return now; }
static atomic_uint driver_frees;
void esp_netif_free_rx_buffer(void *netif, void *l2) {
    (void)netif; assert(l2); atomic_fetch_add(&driver_frees, 1);
}
static uint32_t esp_rom_crc32_le(uint32_t crc, const uint8_t *bytes, uint32_t size) {
    crc = ~crc;
    while (size--) {
        crc ^= *bytes++;
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ ((crc & 1) ? UINT32_C(0xedb88320) : 0);
    }
    return ~crc;
}
static void test_log(const char *tag, const char *format, ...) {
    (void)tag;
    va_list args; va_start(args, format); vprintf(format,args); va_end(args); puts("");
}
#include "rx_copy_profile.c"

static struct pbuf *received;
static err_t retain(struct pbuf *p, struct netif *n) { (void)n; received=p; return ERR_OK; }
static err_t reject(struct pbuf *p, struct netif *n) { (void)p; (void)n; return ERR_MEM; }
static err_t release(struct pbuf *p, struct netif *n) { (void)n; assert(pbuf_free(p)==1); return ERR_OK; }
static uint8_t frame[65536], handle;
static struct netif iface = {.flags=NETIF_FLAG_UP, .input=retain};

static struct pbuf *feed(unsigned length) {
    unsigned before=atomic_load(&driver_frees);
    assert(__wrap_wlanif_input(&iface,frame,length,&handle)==ESP_OK);
    assert(atomic_load(&driver_frees)==before+1);
    assert(received->len==length && !memcmp(received->payload,frame,length));
    return received;
}
static void empty(void) {
    assert(!s_counts.live && !s_counts.bytes);
    for(unsigned i=0;i<RX_COPY_SIZE_CLASSES;++i) assert(!s_counts.classes[i].live);
}
static void *worker(void *context) {
    (void)context;
    struct netif n={.flags=NETIF_FLAG_UP,.input=release};
    uint8_t bytes[1500]={0}, tag;
    for(unsigned i=0;i<1000;++i)
        assert(__wrap_wlanif_input(&n,bytes,100+i%1400,&tag)==ESP_OK);
    return NULL;
}
int main(void) {
    for(unsigned i=0;i<sizeof(frame);++i) frame[i]=(uint8_t)(i^0x55);
    assert(esp_rom_crc32_le(0,(const uint8_t *)"123456789",9)==UINT32_C(0xcbf43926));
    const unsigned lengths[]={0,128,129,512,513,1152,1153,1600,1601};
    for(unsigned i=0;i<sizeof(lengths)/sizeof(lengths[0]);++i) {
        struct pbuf *p=feed(lengths[i]);
        assert(s_counts.live==1 && s_counts.bytes==malloc_usable_size(p));
        assert(s_counts.classes[size_class(lengths[i])].live==1);
        assert(pbuf_free(p)==1); empty();
    }
    // The actual SDK refcount and trim paths must keep the original owner.
    struct pbuf *p=feed(1024);
    uint32_t held=s_counts.bytes, freed=s_counts.releases;
    pbuf_ref(p); assert(pbuf_free(p)==0);
    assert(s_counts.live==1 && s_counts.releases==freed);
    pbuf_realloc(p,200); assert(s_counts.bytes==held && p->len==200);
    assert(pbuf_free(p)==1); empty();
    struct pbuf *a=feed(100), *b=feed(1200);
    pbuf_ref(b); pbuf_cat(a,b);
    assert(pbuf_free(a)==1 && s_counts.live==1);
    assert(pbuf_free(b)==1); empty();
    a=feed(128); b=feed(512); pbuf_cat(a,b);
    assert(pbuf_free(a)==2); empty();
    freed=s_counts.releases;
    p=pbuf_alloc(PBUF_RAW,16,PBUF_RAM); assert(pbuf_free(p)==1);
    assert(s_counts.releases==freed); // Unrelated lwIP heap allocation.
    now=5000000; rx_copy_profile_poll();
    pthread_t workers[4];
    for(unsigned i=0;i<4;++i) assert(!pthread_create(&workers[i],NULL,worker,NULL));
    for(unsigned i=0;i<4;++i) assert(!pthread_join(workers[i],NULL));
    empty(); assert(s_counts.allocations==s_counts.releases && !s_counts.lost);
    now+=5000000; rx_copy_profile_poll();
    // Failure paths never leak or deliver an invalid packet to input().
    unsigned driver_before=atomic_load(&driver_frees);
    fail_malloc=1;
    assert(__wrap_wlanif_input(&iface,frame,100,&handle)==ESP_ERR_NO_MEM);
    assert(s_counts.failed==1 && atomic_load(&driver_frees)==driver_before+1); empty();
    iface.input=reject;
    assert(__wrap_wlanif_input(&iface,frame,100,&handle)==ESP_FAIL);
    assert(s_counts.rejected==1); empty(); iface.input=retain;
    iface.flags=0; assert(__wrap_wlanif_input(&iface,frame,100,&handle)==ESP_FAIL);
    iface.flags=NETIF_FLAG_UP;
    assert(__wrap_wlanif_input(&iface,NULL,100,&handle)==ESP_FAIL);
    assert(__wrap_wlanif_input(&iface,frame,65536,&handle)==ESP_FAIL); empty();
    struct pbuf *all[RX_COPY_TRACK_SLOTS+1];
    for(unsigned i=0;i<RX_COPY_TRACK_SLOTS+1;++i) all[i]=feed(100);
    assert(s_counts.lost==1 && s_counts.live==RX_COPY_TRACK_SLOTS);
    for(unsigned i=0;i<RX_COPY_TRACK_SLOTS+1;++i) assert(pbuf_free(all[i])==1);
    empty();
    p=feed(100); track_allocation(p,100); assert(s_counts.lost==2 && s_counts.live==1);
    assert(pbuf_free(p)==1); empty();
    puts("PASS actual SDK pbuf copy/refcount/chains/trim/free/failure/overflow/concurrency");
}
