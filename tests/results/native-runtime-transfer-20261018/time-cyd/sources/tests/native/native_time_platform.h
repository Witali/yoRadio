#pragma once
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <assert.h>
#include <errno.h>
#include <inttypes.h>
#include <pthread.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/time.h>
#include <time.h>

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_SIZE 0x104
#define ESP_ERR_NOT_FINISHED 0x105
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_NVS_NOT_FOUND 0x1102
#define ESP_ERR_NVS_INVALID_LENGTH 0x110c
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
#define ESP_GOTO_ON_FALSE(c,e,label,...) do {if(!(c)){ret=(e);goto label;}}while(0)
#define ESP_GOTO_ON_ERROR(c,label,...) do {esp_err_t error_=(c);if(error_){ret=error_;goto label;}}while(0)
#define ESP_RETURN_ON_FALSE(c,e,...) do {if(!(c))return (e);}while(0)
#define ESP_STATIC_ASSERT(c,m) _Static_assert(c,m)
#define ESP_EVENT_DECLARE_BASE(x) extern int x
#define ESP_EVENT_DEFINE_BASE(x) int x
typedef int ip_event_t;
typedef int esp_event_base_t;
#define IP_EVENT 1
#define IP_EVENT_STA_GOT_IP 2
typedef int BaseType_t;
typedef unsigned TickType_t;
#define pdTRUE 1
#define pdFALSE 0
#define pdPASS 1
#define pdMS_TO_TICKS(x) (x)
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
typedef struct host_sem {pthread_mutex_t mutex;} *SemaphoreHandle_t;
static unsigned allocations, fail_allocation, sem_count;
static SemaphoreHandle_t sems[32], forced_timeout;
static void *host_calloc(size_t n,size_t size) {if(++allocations==fail_allocation)return NULL;return calloc(n,size);}
static SemaphoreHandle_t xSemaphoreCreateMutex(void) {SemaphoreHandle_t s=host_calloc(1,sizeof(*s));if(s){assert(sem_count<32);sems[sem_count++]=s;assert(!pthread_mutex_init(&s->mutex,NULL));}return s;}
static SemaphoreHandle_t xSemaphoreCreateBinary(void) {return xSemaphoreCreateMutex();}
static int xSemaphoreTake(SemaphoreHandle_t s,unsigned ticks) {(void)ticks;if(s==forced_timeout)return pdFALSE;assert(!pthread_mutex_lock(&s->mutex));return pdTRUE;}
static int xQueueSemaphoreTake(SemaphoreHandle_t s,unsigned ticks) {return xSemaphoreTake(s,ticks);}
static int xSemaphoreGive(SemaphoreHandle_t s) {assert(!pthread_mutex_unlock(&s->mutex));return pdTRUE;}
static void vSemaphoreDelete(SemaphoreHandle_t s) {assert(!pthread_mutex_destroy(&s->mutex));for(unsigned i=0;i<sem_count;i++)if(sems[i]==s)sems[i]=NULL;free(s);}
static void cleanup_sems(void) {for(unsigned i=0;i<sem_count;i++)if(sems[i])vSemaphoreDelete(sems[i]);}

typedef uint8_t u8_t;
typedef uint16_t u16_t;
typedef uint32_t u32_t;
typedef int32_t s32_t;
typedef uint64_t u64_t;
typedef int64_t s64_t;
typedef int err_t;
typedef struct {uint32_t addr;} ip_addr_t;
static const ip_addr_t zero_ip={0};
#define IP_ADDR_ANY (&zero_ip)
#define IP_ANY_TYPE (&zero_ip)
#define IPADDR_TYPE_ANY 0
#define ip_addr_set_zero(p) ((p)->addr=0)
#define ip_addr_isany(p) (!(p)->addr)
#define ip_addr_isany_val(p) (!(p).addr)
#define ip_addr_copy(d,s) ((d)=(s))
#define ip_addr_eq(a,b) ((a)->addr==(b)->addr)
#define LWIP_UNUSED_ARG(x) ((void)(x))
#define LWIP_UDP 1
#define LWIP_DHCP 0
#define LWIP_IPV4 1
#define LWIP_IPV6 0
#define LWIP_IPV6_DHCP6 0
#define LWIP_DHCP_GET_NTP_SRV 0
#define LWIP_DHCP6_GET_NTP_SRV 0
#define LWIP_HAVE_INT64 1
#define LWIP_IANA_PORT_SNTP 123
#ifndef CONFIG_LWIP_SNTP_MAX_SERVERS
#define CONFIG_LWIP_SNTP_MAX_SERVERS 2
#endif
#define SNTP_MAX_SERVERS CONFIG_LWIP_SNTP_MAX_SERVERS
#define CONFIG_LWIP_SNTP_UPDATE_DELAY 3600000U
#define SNTP_SERVER_DNS 1
#define SNTP_STARTUP_DELAY 1
#define SNTP_STARTUP_DELAY_FUNC 1234U
#define SNTP_SUPPRESS_DELAY_CHECK
#define SNTP_UPDATE_DELAY (sntp_get_sync_interval())
#define SNTP_SET_SYSTEM_TIME_US(s,u) sntp_set_system_time((s),(u))
#define SNTP_GET_SYSTEM_TIME(s,u) sntp_get_system_time(&(s),&(u))
#define LWIP_DBG_OFF 0
#define LWIP_DBG_TRACE 0
#define LWIP_DBG_STATE 0
#define LWIP_DBG_LEVEL_WARNING 0
#define LWIP_DBG_LEVEL_SERIOUS 0
#define LWIP_DEBUGF(...) ((void)0)
#ifdef HOST_NO_LWIP_ASSERT
#define LWIP_ASSERT(message,c) ((void)0)
#else
#define LWIP_ASSERT(message,c) assert((c) && (message))
#endif
#define LWIP_ERROR(message,c,handler) do {if(!(c)){handler;}}while(0)
static _Thread_local bool in_tcpip;
#define LWIP_ASSERT_CORE_LOCKED() assert(in_tcpip)
#define PACK_STRUCT_BEGIN
#define PACK_STRUCT_END
#define PACK_STRUCT_STRUCT __attribute__((packed))
#define PACK_STRUCT_FIELD(x) x
#define PACK_STRUCT_FLD_8(x) x
#define lwip_ntohl ntohl
#define lwip_htonl htonl
#define MEMCPY memcpy
#define LWIP_MIN(a,b) ((a)<(b)?(a):(b))
#define U32_F PRIu32
#define U16_F PRIu16
#define SOF_BROADCAST 1
struct pbuf {void *payload;u16_t tot_len;};
struct udp_pcb;
typedef void (*udp_recv_fn)(void*,struct udp_pcb*,struct pbuf*,const ip_addr_t*,u16_t);
struct udp_pcb {udp_recv_fn receive;void *arg;unsigned id;};
#define PBUF_TRANSPORT 0
#define PBUF_RAM 0
static unsigned udp_created, udp_removed, sent, null_sends, fail_udp, fail_pbuf;
static ip_addr_t last_sent;
static struct udp_pcb *udp_new_ip_type(int type) {(void)type;assert(in_tcpip);if(fail_udp)return NULL;struct udp_pcb *p=calloc(1,sizeof(*p));assert(p);p->id=++udp_created;return p;}
static void udp_recv(struct udp_pcb *p,udp_recv_fn cb,void *arg){p->receive=cb;p->arg=arg;}
static void udp_remove(struct udp_pcb *p){assert(in_tcpip);assert(p);udp_removed++;free(p);}
static err_t udp_sendto(struct udp_pcb *p,struct pbuf *b,const ip_addr_t *ip,u16_t port){assert(in_tcpip);assert(b&&port==123);if(!p){null_sends++;return -2;}last_sent=*ip;sent++;return 0;}
static err_t udp_bind(struct udp_pcb *p,const ip_addr_t *ip,u16_t port){(void)p;(void)ip;(void)port;return 0;}
#define ip_set_option(p,o) ((void)(p),(void)(o))
static struct pbuf *pbuf_alloc(int layer,u16_t n,int type){(void)layer;(void)type;if(fail_pbuf)return NULL;struct pbuf *p=calloc(1,sizeof(*p));assert(p);p->payload=calloc(1,n);assert(p->payload);p->tot_len=n;return p;}
static u8_t pbuf_free(struct pbuf *p){free(p->payload);free(p);return 1;}
static u8_t pbuf_get_at(const struct pbuf *p,u16_t at){assert(at<p->tot_len);return ((u8_t*)p->payload)[at];}
static u16_t pbuf_copy_partial(const struct pbuf *p,void *to,u16_t n,u16_t at){assert(at+n<=p->tot_len);memcpy(to,(u8_t*)p->payload+at,n);return n;}
typedef void(*timeout_fn)(void*);
static struct {timeout_fn fn;void *arg;unsigned delay;} timers[32];
static void sys_timeout(u32_t delay,timeout_fn fn,void *arg){assert(in_tcpip);for(unsigned i=0;i<32;i++)if(!timers[i].fn){timers[i].fn=fn;timers[i].arg=arg;timers[i].delay=delay;return;}assert(!"timer capacity");}
static void sys_untimeout(timeout_fn fn,void *arg){assert(in_tcpip);for(unsigned i=0;i<32;i++)if(timers[i].fn==fn&&timers[i].arg==arg)timers[i].fn=NULL;}
static unsigned timer_count(void){unsigned n=0;for(unsigned i=0;i<32;i++)n+=timers[i].fn!=NULL;return n;}
static unsigned ipc_calls, fail_ipc_at;
static pthread_mutex_t tcpip_lock=PTHREAD_MUTEX_INITIALIZER;
static esp_err_t esp_netif_tcpip_exec(esp_err_t(*fn)(void*),void *ctx){ipc_calls++;if(ipc_calls==fail_ipc_at)return ESP_FAIL;assert(!in_tcpip);assert(!pthread_mutex_lock(&tcpip_lock));in_tcpip=true;esp_err_t e=fn(ctx);in_tcpip=false;assert(!pthread_mutex_unlock(&tcpip_lock));return e;}
static int tcpip_callback(void(*fn)(void*),void *ctx){(void)fn;(void)ctx;assert(!"asynchronous SNTP API used");return -1;}
static int esp_event_post(int base,int id,const void *p,size_t n,unsigned ticks){(void)base;(void)id;(void)p;(void)n;assert(!ticks);return ESP_OK;}
static int esp_event_handler_register(int base,int id,void(*fn)(void*,int,int32_t,void*),void *arg){(void)base;(void)id;(void)fn;(void)arg;return ESP_OK;}
static int esp_event_handler_unregister(int base,int id,void(*fn)(void*,int,int32_t,void*)){(void)base;(void)id;(void)fn;return ESP_OK;}

static time_t wall_epoch=1704067200;
static int host_settimeofday(const struct timeval *tv,const void *zone){(void)zone;wall_epoch=tv->tv_sec;return 0;}
static int host_gettimeofday(struct timeval *tv,void *zone){(void)zone;tv->tv_sec=wall_epoch;tv->tv_usec=0;return 0;}
static int host_adjtime(const struct timeval *delta,struct timeval *old){(void)delta;if(old)memset(old,0,sizeof(*old));return 0;}
#define ERR_OK 0
#define ERR_ARG (-2)
#define ERR_MEM (-3)
#define ERR_TIMEOUT (-4)
#define ERR_INPROGRESS (-5)
#define DNS_TABLE_SIZE 16
#define DNS_MAX_REQUESTS 16
#define DNS_MAX_HOST_IP 1
#define DNS_MAX_NAME_LENGTH 256
#define LWIP_DNS_SECURE_RAND_XID 1
#define LWIP_DNS_SECURE_NO_MULTIPLE_OUTSTANDING 2
#define LWIP_DNS_SECURE_RAND_SRC_PORT 4
#define LWIP_DNS_SECURE 7
#define DNS_MAX_SOURCE_PORTS 16
#define LWIP_DNS_ADDRTYPE_ARG(x)
#define LWIP_DNS_SET_ADDRTYPE(x,y)
#define LWIP_DNS_ISMDNS_ARG(x)
#define lwip_strnicmp strncasecmp
typedef void(*dns_found_callback)(const char*,const ip_addr_t*,void*);
static err_t dns_gethostbyname(const char*,ip_addr_t*,dns_found_callback,void*);
static unsigned dns_alloc_pcb(void){return 0;}
static void dns_check_entry(u8_t index);
