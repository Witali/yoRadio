#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sdk_rx_diag.h"

static pthread_mutex_t critical_mutex = PTHREAD_MUTEX_INITIALIZER;
static _Thread_local unsigned critical_depth;
void rx_test_enter_critical(void)
{
    assert(critical_depth == 0);
    assert(pthread_mutex_lock(&critical_mutex) == 0);
    ++critical_depth;
}
void rx_test_exit_critical(void)
{
    assert(critical_depth == 1);
    --critical_depth;
    assert(pthread_mutex_unlock(&critical_mutex) == 0);
}

static sdk_rx_diag_snapshot_t snapshot(void)
{
    sdk_rx_diag_snapshot_t value;
    sdk_rx_diag_snapshot(&value);
    assert(value.rx_custom_live <= value.rx_custom_peak);
    return value;
}

#if SDK_RX_DIAG_FUNCTIONS
typedef int err_t;
struct pbuf {void *payload; uint16_t len; unsigned flags, ref;};
struct pbuf_custom {struct pbuf pbuf; void (*custom_free_function)(struct pbuf *);};
struct netif {void *state; int up;};
typedef err_t (*netif_input_fn)(struct pbuf *, struct netif *);
struct tcpip_msg {
    int type;
    union {struct {struct pbuf *p; struct netif *netif; netif_input_fn input_fn;} inp;} msg;
};
typedef struct esp_aio {
    int fd; void *pbuf; uint16_t len; int (*cb)(struct esp_aio *); void *arg; int ret;
} esp_aio_t;
#define ERR_OK 0
#define ERR_MEM -1
#define ERR_ARG -2
#define ERR_RTE -3
#define PBUF_RAW 0
#define PBUF_REF 1
#define PBUF_RAM 2
#define PBUF_FLAG_IS_CUSTOM 1
#define MEMP_TCPIP_MSG_INPKT 0
#define TCPIP_MSG_INPKT 0
#define LWIP_DEBUGF(...) ((void)0)
#define LWIP_ASSERT(message, condition) assert(condition)
#define sys_mbox_valid_val(value) ((value) == 1)
#define IS_DRAM(payload) ((payload) != iram_payload)
#define IS_IRAM(payload) ((payload) == iram_payload)
static int tcpip_mbox = 1;
static int fail_malloc, fail_pbuf_setup, fail_msg, fail_post, fail_copy;
static int copy_iram, driver_result, immediate_free, driver_calls;
static unsigned malloc_live, driver_rx_freed, pbuf_freed, msg_freed;
static char iram_payload[32], copy_payload[32];
static struct pbuf tx_copy;
static struct tcpip_msg *posted_msg;
static struct pbuf *queued_pbuf;

static void *os_malloc(size_t bytes)
{
    assert(critical_depth == 0);
    if (fail_malloc) return NULL;
    void *result = calloc(1, bytes);
    assert(result);
    ++malloc_live;
    return result;
}
static void os_free(void *ptr)
{
    assert(critical_depth == 0 && ptr && malloc_live);
    --malloc_live;
    free(ptr);
}
static void esp_wifi_internal_free_rx_buffer(void *ptr)
{
    assert(ptr && critical_depth == 0);
    ++driver_rx_freed;
}
static struct pbuf *pbuf_alloced_custom(int layer, uint16_t len, int type,
                                      struct pbuf_custom *pc, void *buffer, uint16_t size)
{
    assert(critical_depth == 0 && layer == PBUF_RAW && type == PBUF_REF && len == size);
    if (fail_pbuf_setup) return NULL;
    pc->pbuf = (struct pbuf){buffer, len, PBUF_FLAG_IS_CUSTOM, 1};
    return &pc->pbuf;
}
static void pbuf_free(struct pbuf *p)
{
    assert(critical_depth == 0 && p->ref > 0);
    ++pbuf_freed;
    if (--p->ref == 0 && (p->flags & PBUF_FLAG_IS_CUSTOM))
        ((struct pbuf_custom *)p)->custom_free_function(p);
}
void ethernetif_input(struct netif *netif, struct pbuf *p)
{
    assert(critical_depth == 0 && netif && snapshot().rx_custom_live >= 1);
    if (immediate_free) pbuf_free(p);
    else queued_pbuf = p;
}
static void *memp_malloc(int type)
{
    assert(critical_depth == 0 && type == MEMP_TCPIP_MSG_INPKT);
    return fail_msg ? NULL : os_malloc(sizeof(struct tcpip_msg));
}
static void memp_free(int type, void *ptr)
{
    assert(type == MEMP_TCPIP_MSG_INPKT);
    ++msg_freed;
    os_free(ptr);
}
static err_t sys_mbox_trypost(int *mbox, void *msg)
{
    assert(critical_depth == 0 && mbox == &tcpip_mbox);
    if (fail_post) return ERR_MEM;
    posted_msg = msg;
    return ERR_OK;
}
static void pbuf_ref(struct pbuf *p) {assert(critical_depth == 0); ++p->ref;}
static struct pbuf *pbuf_alloc(int layer, uint16_t len, int type)
{
    assert(critical_depth == 0 && layer == PBUF_RAW && type == PBUF_RAM && len <= 32);
    if (fail_copy) return NULL;
    tx_copy = (struct pbuf){copy_iram ? iram_payload : copy_payload, len, 0, 1};
    return &tx_copy;
}
static int netif_is_up(struct netif *netif) {return netif->up;}
static int low_level_send_cb(esp_aio_t *aio) {pbuf_free(aio->arg); return 0;}
static int ieee80211_output_pbuf(esp_aio_t *aio)
{
    assert(critical_depth == 0 && aio->arg && aio->cb == low_level_send_cb);
    ++driver_calls;
    return driver_result;
}

/* Actual generated SDK functions, not reimplementations. */
#include "sdk_fragments.inc"

static void test_sdk_flow(void)
{
    struct netif netif = {(void *)(uintptr_t)1, 1};
    char bytes[16] = "packet";
    unsigned freed;
    sdk_rx_diag_snapshot_t before = snapshot();
    fail_malloc = 1;
    assert(tcpip_adapter_recv_cb(&netif, bytes, sizeof(bytes), bytes) == -ENOMEM);
    fail_malloc = 0;
    fail_pbuf_setup = 1;
    assert(tcpip_adapter_recv_cb(&netif, bytes, sizeof(bytes), bytes) == -ENOMEM);
    fail_pbuf_setup = 0;
    assert(malloc_live == 0 && driver_rx_freed == 0);
    assert(snapshot().rx_custom_fail == before.rx_custom_fail + 2);
    assert(snapshot().rx_custom_total == before.rx_custom_total);
    immediate_free = 1;
    assert(tcpip_adapter_recv_cb(&netif, bytes, sizeof(bytes), bytes) == 0);
    assert(malloc_live == 0 && driver_rx_freed == 1 && snapshot().rx_custom_live == 0);
    immediate_free = 0;
    assert(tcpip_adapter_recv_cb(&netif, bytes, sizeof(bytes), bytes) == 0);
    struct pbuf *first = queued_pbuf;
    void *owned_buffer = os_malloc(16);
    assert(tcpip_adapter_recv_cb(&netif, owned_buffer, 16, NULL) == 0);
    assert(snapshot().rx_custom_live == 2 && snapshot().rx_custom_peak == 2);
    pbuf_free(first);
    assert(snapshot().rx_custom_live == 1 && driver_rx_freed == 2);
    pbuf_free(queued_pbuf);
    assert(snapshot().rx_custom_live == 0 && malloc_live == 0);
    assert(snapshot().rx_custom_total == before.rx_custom_total + 3);

    struct pbuf packet = {bytes, sizeof(bytes), 0, 1};
    before = snapshot();
    freed = pbuf_freed;
    fail_msg = 1;
    assert(tcpip_inpkt(&packet, &netif, NULL) == ERR_MEM);
    fail_msg = 0;
    fail_post = 1;
    assert(tcpip_inpkt(&packet, &netif, NULL) == ERR_MEM);
    fail_post = 0;
    assert(msg_freed == 1 && malloc_live == 0 && pbuf_freed == freed);
    assert(snapshot().rx_enqueue_nomem == before.rx_enqueue_nomem + 1);
    assert(snapshot().rx_enqueue_full == before.rx_enqueue_full + 1);
    assert(tcpip_inpkt(&packet, &netif, NULL) == ERR_OK);
    assert(posted_msg->msg.inp.p == &packet && posted_msg->msg.inp.netif == &netif);
    memp_free(MEMP_TCPIP_MSG_INPKT, posted_msg);
    assert(malloc_live == 0 && pbuf_freed == freed);

    before = snapshot();
    assert(low_level_output(NULL, &packet) == ERR_ARG);
    netif.up = 0;
    assert(low_level_output(&netif, &packet) == ERR_RTE);
    netif.up = 1;
    /* Force the real transform copy path, including both of its failure cases. */
    packet.flags = PBUF_FLAG_IS_CUSTOM;
    fail_copy = 1;
    assert(low_level_output(&netif, &packet) == ERR_OK); /* SDK behavior unchanged! */
    fail_copy = 0;
    copy_iram = 1;
    assert(low_level_output(&netif, &packet) == ERR_OK);
    copy_iram = 0;
    assert(driver_calls == 0 && snapshot().tx_transform_fail == before.tx_transform_fail + 2);
    driver_result = ERR_MEM;
    assert(low_level_output(&netif, &packet) == ERR_MEM);
    assert(tx_copy.ref == 0 && snapshot().tx_driver_fail == before.tx_driver_fail + 1);
    driver_result = ERR_OK;
    assert(low_level_output(&netif, &packet) == ERR_OK);
    assert(tx_copy.ref == 1 && !memcmp(copy_payload, bytes, sizeof(bytes)));
    pbuf_free(&tx_copy); /* eventual asynchronous TX completion */
    packet.flags = 0;
    assert(low_level_output(&netif, &packet) == ERR_OK);
    assert(packet.ref == 2);
    pbuf_free(&packet);
    assert(packet.ref == 1 && malloc_live == 0);
    puts("SDK RX/TX injected control-flow tests passed");
}
#endif

static void *worker(void *unused)
{
    (void)unused;
    for (unsigned i = 0; i < 10000; ++i) {
        sdk_rx_diag_custom_acquire();
        sdk_rx_diag_count(SDK_RX_DIAG_ENQUEUE_NOMEM);
        sdk_rx_diag_snapshot_t value = snapshot();
        assert(value.rx_custom_live >= 1 && value.rx_custom_live <= 4);
        sdk_rx_diag_custom_release();
    }
    return NULL;
}

int main(void)
{
    assert(sizeof(sdk_rx_diag_snapshot_t) == 32);
    sdk_rx_diag_snapshot(NULL);
    sdk_rx_diag_snapshot_t before = snapshot();
    sdk_rx_diag_count((sdk_rx_diag_event_t)-1);
    sdk_rx_diag_count((sdk_rx_diag_event_t)100);
    sdk_rx_diag_snapshot_t after = snapshot();
    assert(!memcmp(&before, &after, sizeof(before)));
    for (int event = 0; event < 5; ++event) sdk_rx_diag_count((sdk_rx_diag_event_t)event);
    after = snapshot();
    assert(after.rx_custom_fail == 1 && after.rx_enqueue_nomem == 1 && after.rx_enqueue_full == 1);
    assert(after.tx_transform_fail == 1 && after.tx_driver_fail == 1);
#if SDK_RX_DIAG_FUNCTIONS
    test_sdk_flow();
#endif
    before = snapshot();
    pthread_t threads[4];
    for (unsigned i = 0; i < 4; ++i) assert(pthread_create(&threads[i], NULL, worker, NULL) == 0);
    for (unsigned i = 0; i < 4; ++i) assert(pthread_join(threads[i], NULL) == 0);
    after = snapshot();
    assert(after.rx_custom_total == before.rx_custom_total + 40000);
    assert(after.rx_enqueue_nomem == before.rx_enqueue_nomem + 40000);
    assert(after.rx_custom_live == 0 && after.rx_custom_peak >= 1 && after.rx_custom_peak <= 4);
    assert(critical_depth == 0);
    puts("SDK diagnostics: 32 bytes, balanced lifetime, concurrent snapshots passed");
    return 0;
}
