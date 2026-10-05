#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

// RV32 stack-size assertion is checked by the real firmware compiler. This
// host model has 64-bit pointers and tests range matching/ownership instead.
#define _Static_assert(condition, message)
typedef struct { int unused; } esp_netif_t;
struct pbuf { int unused; };
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
static bool locked, walking;
#define portENTER_CRITICAL(m) do { (void)(m); assert(!locked); locked=true; } while(0)
#define portEXIT_CRITICAL(m) do { (void)(m); assert(locked); locked=false; } while(0)
static int64_t now;
static int64_t esp_timer_get_time(void) { return now; }
#define MALLOC_CAP_8BIT 1
typedef struct { void *start; } walker_heap_into_t;
typedef struct { void *ptr; size_t size; bool used; } walker_block_info_t;
static walker_block_info_t blocks[70];
static size_t block_count;
static void heap_caps_walk(unsigned caps, bool (*visit)(walker_heap_into_t,walker_block_info_t,void *), void *data) {
    assert(caps==1 && locked && !walking); walking=true;
    for(size_t i=0;i<block_count;++i) assert(visit((walker_heap_into_t){0},blocks[i],data));
    walking=false;
}
static void test_log(const char *tag, const char *format, ...) {
    (void)tag; assert(!locked && !walking);
    va_list args; va_start(args,format); vprintf(format,args); va_end(args); putchar('\n');
}
#define ESP_LOGI test_log
static struct pbuf *next_pbuf;
static unsigned real_allocs, real_frees;
struct pbuf *__real_esp_pbuf_allocate(esp_netif_t *n,void *p,size_t s,void *h) {
    (void)n;(void)p;(void)s;(void)h; assert(!locked);++real_allocs;return next_pbuf;
}
void __real_esp_netif_free_rx_buffer(void *n,void *p) {
    (void)n;(void)p;assert(!locked);++real_frees;
}

// The runner inserts the production source here, removing platform includes.
/* PRODUCTION_SOURCE */

static uint8_t payloads[34][1800], metadata[34][64], handles[34];
static void add(unsigned index) {
    next_pbuf=(struct pbuf *)metadata[index];
    assert(__wrap_esp_pbuf_allocate(NULL,payloads[index]+44,1280,&handles[index])==next_pbuf);
}
int main(void) {
    now=5000000;rx_buffer_diagnostic_poll();assert(!live);
    add(0);add(1);add(2);
    for(unsigned i=0;i<3;++i) {
        blocks[block_count++]=(walker_block_info_t){payloads[i],1724,true};
        blocks[block_count++]=(walker_block_info_t){metadata[i],32,true};
    }
    now+=5000000;rx_buffer_diagnostic_poll();assert(live==3 && !lost);
    for(unsigned i=0;i<3;++i)__wrap_esp_netif_free_rx_buffer(NULL,&handles[i]);
    assert(!live && releases==3 && real_frees==3);
    next_pbuf=NULL;
    assert(!__wrap_esp_pbuf_allocate(NULL,payloads[0],1280,&handles[0]));
    assert(allocations==3);__wrap_esp_netif_free_rx_buffer(NULL,&handles[0]);
    assert(untracked_releases==1 && real_frees==4);
    for(unsigned i=0;i<33;++i)add(i);
    assert(live==32 && lost==1 && peak==32);
    for(unsigned i=0;i<33;++i)__wrap_esp_netif_free_rx_buffer(NULL,&handles[i]);
    assert(!live && releases==35 && real_frees==37);
    add(0);uint32_t identity=owners[0].id;
    add(0);assert(lost==2 && live==1); // Ambiguous repeated L2 handle is flagged.
    __wrap_esp_netif_free_rx_buffer(NULL,&handles[0]);
    add(0);assert(owners[0].id>identity);
    // A pointer is matched only to an allocated block, never to free storage.
    blocks[0].used=false;
    now+=5000000;rx_buffer_diagnostic_poll();
    __wrap_esp_netif_free_rx_buffer(NULL,&handles[0]);
    rx_snapshot_t shared={.count=2};
    shared.rows[0].payload_allocation=100;shared.rows[0].metadata_allocation=200;
    assert(already_counted(&shared,1,100) && already_counted(&shared,1,200));
    assert(!already_counted(&shared,1,300));
    assert(!live && !locked && !walking);
    puts("PASS range/ownership/free/failure/overflow/identity/log-lock checks");
}
