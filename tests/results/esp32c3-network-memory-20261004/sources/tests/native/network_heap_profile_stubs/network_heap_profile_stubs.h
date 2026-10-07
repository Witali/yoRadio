#ifndef NETWORK_HEAP_PROFILE_STUBS_H
#define NETWORK_HEAP_PROFILE_STUBS_H
#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#define TCP_QUEUE_OOSEQ 1
#define ERR_OK 0
#define ERR_MEM -1
#define MALLOC_CAP_8BIT 1
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
extern int test_lock, test_core;
#define portENTER_CRITICAL(p) do { (void)(p); assert(!test_lock); ++test_lock; } while (0)
#define portEXIT_CRITICAL(p) do { (void)(p); assert(test_lock == 1); --test_lock; } while (0)
#define LWIP_ASSERT_CORE_LOCKED() assert(test_core && !test_lock)
typedef struct { size_t total_free_bytes, largest_free_block, total_allocated_bytes, allocated_blocks, free_blocks; } multi_heap_info_t;
struct tcp_seg { struct tcp_seg *next; uint16_t len; };
struct tcp_pcb { struct tcp_pcb *next; struct tcp_seg *unsent, *unacked, *ooseq; };
struct tcp_pcb_listen { struct tcp_pcb_listen *next; };
extern struct tcp_pcb *tcp_active_pcbs, *tcp_tw_pcbs, *tcp_bound_pcbs;
extern union test_listen { struct tcp_pcb_listen *listen_pcbs; } tcp_listen_pcbs;
struct tcpip_callback_msg { void (*function)(void *); void *context; };
struct tcpip_callback_msg *tcpip_callbackmsg_new(void (*function)(void *), void *context);
int tcpip_callbackmsg_trycallback(struct tcpip_callback_msg *message);
void heap_caps_get_info(multi_heap_info_t *info, unsigned caps);
int64_t esp_timer_get_time(void);
void test_log(const char *format, ...);
#define ESP_LOGI(tag, ...) do { (void)(tag); test_log(__VA_ARGS__); } while (0)
#define ESP_LOGW(tag, ...) ESP_LOGI(tag, __VA_ARGS__)
#endif
