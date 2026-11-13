/* Actual TLS1.2 traffic over synthetic OpenETH; public TLS/PSA APIs only. */
#include <inttypes.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "esp_event.h"
#include "esp_eth.h"
#include "esp_eth_mac_openeth.h"
#include "esp_heap_caps.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "esp_tls.h"
#include "nvs_flash.h"
#include "psa/crypto.h"
#include "mbedtls/platform.h"
#include "native_tls_rx_reserve.h"
#include "native_tls_early_mpi.h"
#include "native_input_reclaim.h"
#include "test_clock.h"

_Static_assert(CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN == 16384, "Full input records");
_Static_assert(CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN == 4096, "Original output profile");
_Static_assert(CONFIG_MBEDTLS_HARDWARE_MPI && CONFIG_MBEDTLS_HARDWARE_AES && CONFIG_MBEDTLS_HARDWARE_SHA, "Hardware crypto retained");
#if CONFIG_FREERTOS_UNICORE
#error "Classic dual-core ESP32 required"
#endif

static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
static EventGroupHandle_t s_network;
static unsigned s_attaches, s_attach_failures;
#if CONFIG_YORADIO_TLS_STATIC_RX_RESERVE
static unsigned s_rx_calls, s_rx_frees;
static void *s_last_rx[2];
#endif
static atomic_bool s_pressure;
static TaskHandle_t s_pressure_owner;
static unsigned s_real_nulls, s_real_recoveries;
static size_t s_failed_count, s_failed_size;
static void *s_blocks[512];
static uint8_t s_plaintext[2][16384];
static unsigned s_early_mpi_calls;

__attribute__((noreturn)) static void fail(const char *label) {
    printf("TLS_TRAFFIC_FAILURE %s\nTLS_TRAFFIC_CONTROLLED_STOP\n", label);
    fflush(stdout);esp_restart();for (;;) vTaskDelay(portMAX_DELAY);
}
static void check(bool value,const char *label) {if(!value)fail(label);}
static void integrity(void) {check(heap_caps_check_integrity_all(true),"heap_integrity");}
void __real_native_tls_early_mpi_prepare(void);
void __wrap_native_tls_early_mpi_prepare(void) {
    __real_native_tls_early_mpi_prepare();++s_early_mpi_calls;
    printf("TLS_EARLY_MPI calls=%u core=%d\n",s_early_mpi_calls,xPortGetCoreID());
}

#if CONFIG_YORADIO_TLS_STATIC_RX_RESERVE
void *__real_yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *,size_t,size_t);
void *__wrap_yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *cfg,size_t count,size_t size) {
    void *pointer=__real_yoradio_tls_static_rx_calloc(cfg,count,size);
    portENTER_CRITICAL(&s_lock);++s_rx_calls;s_last_rx[xPortGetCoreID()]=pointer;portEXIT_CRITICAL(&s_lock);
    printf("TLS_RX_ALLOC core=%d cfg=%p ptr=%p count=%zu bytes=%zu\n",xPortGetCoreID(),(const void *)cfg,pointer,count,size);
    return pointer;
}
void __real_yoradio_tls_static_rx_free(void *);
void __wrap_yoradio_tls_static_rx_free(void *pointer) {
    __real_yoradio_tls_static_rx_free(pointer);
    portENTER_CRITICAL(&s_lock);++s_rx_frees;portEXIT_CRITICAL(&s_lock);
    printf("TLS_RX_FREE ptr=%p kind=setup\n",pointer);
}
void __real_yoradio_tls_static_rx_zeroize_free(void *,size_t);
void __wrap_yoradio_tls_static_rx_zeroize_free(void *pointer,size_t size) {
    __real_yoradio_tls_static_rx_zeroize_free(pointer,size);
    portENTER_CRITICAL(&s_lock);++s_rx_frees;portEXIT_CRITICAL(&s_lock);
    printf("TLS_RX_FREE ptr=%p kind=normal bytes=%zu\n",pointer,size);
}
#define TLS_ATTACH_REAL __real_native_tls_rx_reserve_crt_bundle_attach
#define TLS_ATTACH_WRAP __wrap_native_tls_rx_reserve_crt_bundle_attach
#else
#define TLS_ATTACH_REAL __real_esp_crt_bundle_attach
#define TLS_ATTACH_WRAP __wrap_esp_crt_bundle_attach
#endif
esp_err_t TLS_ATTACH_REAL(void *);
esp_err_t TLS_ATTACH_WRAP(void *cfg) {
    esp_err_t result=TLS_ATTACH_REAL(cfg);
    portENTER_CRITICAL(&s_lock);++s_attaches;if(result!=ESP_OK)++s_attach_failures;portEXIT_CRITICAL(&s_lock);
    printf("TLS_ATTACH cfg=%p result=%d\n",cfg,(int)result);return result;
}

static void *current_owner(esp_tls_t *tls) {
#if CONFIG_YORADIO_TLS_STATIC_RX_RESERVE
    (void)tls;
    return s_last_rx[xPortGetCoreID()];
#else
    return tls;
#endif
}
void *__real_heap_caps_calloc(size_t,size_t,uint32_t);
void *__wrap_heap_caps_calloc(size_t count,size_t size,uint32_t caps) {
    void *pointer=__real_heap_caps_calloc(count,size,caps);
    if(s_pressure && xTaskGetCurrentTaskHandle()==s_pressure_owner) {
        if(!pointer) {++s_real_nulls;s_failed_count=count;s_failed_size=size;}
        else if(s_real_nulls && count==s_failed_count && size==s_failed_size)++s_real_recoveries;
    }
    return pointer;
}
static void got_ip(void *arg,esp_event_base_t base,int32_t event,void *data) {
    (void)arg;(void)base;(void)event;(void)data;xEventGroupSetBits(s_network,1);
}
static void network_start(void) {
    ESP_ERROR_CHECK(nvs_flash_init());ESP_ERROR_CHECK(esp_netif_init());ESP_ERROR_CHECK(esp_event_loop_create_default());
    s_network=xEventGroupCreate();check(s_network!=NULL,"network_event_group");
    esp_netif_config_t netcfg=ESP_NETIF_DEFAULT_ETH();esp_netif_t *netif=esp_netif_new(&netcfg);check(netif!=NULL,"eth_netif");
    eth_mac_config_t mac_cfg=ETH_MAC_DEFAULT_CONFIG();eth_phy_config_t phy_cfg=ETH_PHY_DEFAULT_CONFIG();
    phy_cfg.phy_addr=1;phy_cfg.reset_gpio_num=-1;
    esp_eth_mac_t *mac=esp_eth_mac_new_openeth(&mac_cfg);esp_eth_phy_t *phy=esp_eth_phy_new_generic(&phy_cfg);
    check(mac && phy,"openeth_mac_generic_phy");esp_eth_config_t config=ETH_DEFAULT_CONFIG(mac,phy);esp_eth_handle_t eth=NULL;
    ESP_ERROR_CHECK(esp_eth_driver_install(&config,&eth));
    ESP_ERROR_CHECK(esp_netif_attach(netif,esp_eth_new_netif_glue(eth)));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT,IP_EVENT_ETH_GOT_IP,got_ip,NULL));ESP_ERROR_CHECK(esp_eth_start(eth));
    check(xEventGroupWaitBits(s_network,1,pdFALSE,pdTRUE,pdMS_TO_TICKS(30000))&1,"openeth_ipv4");
    puts("TLS_NETWORK openeth=1 synthetic_host=10.0.2.2 tls_ports=18443,18444,18445");
}
static esp_tls_t *open_client(const char *label,int port,const char *name,bool expect) {
    check(port>=18443 && port<=18445,"explicit_loopback_endpoint");
    esp_tls_cfg_t cfg={.crt_bundle_attach=native_tls_rx_reserve_crt_bundle_attach,
        .common_name=name,.timeout_ms=15000,.addr_family=ESP_TLS_AF_INET,.tls_version=ESP_TLS_VER_TLS_1_2};
    esp_tls_t *tls=esp_tls_init();check(tls!=NULL,"public_tls_init");
    int status=esp_tls_conn_new_sync("10.0.2.2",8,port,&cfg,tls);
    printf("TLS_OPEN case=%s core=%d status=%d ptr=%p\n",label,xPortGetCoreID(),status,current_owner(tls));
    if(expect)check(status==1,"actual_verified_handshake");
    else {check(status!=1,"expected_handshake_refusal");esp_tls_conn_destroy(tls);tls=NULL;}
    return tls;
}
static void transfer(esp_tls_t *tls,const char *label,unsigned slot,bool expect) {
    char request[160],header[256];
    int length=snprintf(request,sizeof(request),"GET /case/%s HTTP/1.1\r\nHost: cyd-tls.invalid\r\nConnection: close\r\n\r\n",label);
    check(length>0 && (size_t)length<sizeof(request),"bounded_synthetic_request");
    size_t sent=0;while(sent<(size_t)length) {ssize_t n=esp_tls_conn_write(tls,request+sent,(size_t)length-sent);check(n>0,"actual_tls_request_write");sent+=(size_t)n;}
    size_t used=0;while(used<sizeof(header)-1) {
        ssize_t n=esp_tls_conn_read(tls,header+used,1);check(n==1,"complete_http_header");++used;header[used]=0;
        if(used>=4 && !memcmp(header+used-4,"\r\n\r\n",4))break;
    }
    check(strstr(header,"HTTP/1.1 200 OK\r\n") && strstr(header,"Content-Length: 65536\r\n"),"synthetic_http_response");
    psa_hash_operation_t hash=psa_hash_operation_init();check(psa_hash_setup(&hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"psa_sha_setup");
    size_t total=0;unsigned reads=0,full=0;ssize_t last=0;
    while(total<65536) {
        last=esp_tls_conn_read(tls,s_plaintext[slot],sizeof(s_plaintext[slot]));if(last<=0)break;
        check((size_t)last<=sizeof(s_plaintext[slot]) && total+(size_t)last<=65536,"bounded_actual_plaintext");
        for(size_t i=0;i<(size_t)last;++i) {size_t at=total+i;check(s_plaintext[slot][i]==(uint8_t)(at*73+(at>>8)*19+11),"full_exact_plaintext_pattern");}
        check(psa_hash_update(&hash,s_plaintext[slot],(size_t)last)==PSA_SUCCESS,"psa_sha_update");total+=(size_t)last;++reads;full+=(last==16384);vTaskDelay(1);
    }
    if(expect)check(total==65536 && full==4,"full16384_plaintext_records");else check(!total && last<=0,"actual_truncated_record_refusal");
    uint8_t digest[32];size_t bytes=0;check(psa_hash_finish(&hash,digest,sizeof(digest),&bytes)==PSA_SUCCESS && bytes==32,"psa_sha_finish");
    check(psa_hash_abort(&hash)==PSA_SUCCESS,"psa_sha_abort");
    static const char digits[]="0123456789abcdef";char hex[65];
    for(unsigned i=0;i<32;++i) {hex[2*i]=digits[digest[i]>>4];hex[2*i+1]=digits[digest[i]&15];}
    hex[64]=0;
    printf("TLS_DATA case=%s bytes=%zu reads=%u full=%u terminal=%d sha256=%s\n",label,total,reads,full,(int)last,hex);
}
static void roundtrip(const char *label) {esp_tls_t *tls=open_client(label,18443,"cyd-tls.invalid",true);transfer(tls,label,0,true);esp_tls_conn_destroy(tls);integrity();}
static SemaphoreHandle_t s_parallel_start,s_parallel_ready,s_parallel_done;
static void *s_parallel_owners[2];
static void parallel_client(void *arg) {
    unsigned slot=(unsigned)(uintptr_t)arg;const char *label=slot?"parallel_b":"parallel_a";
    esp_tls_t *tls=open_client(label,18443,"cyd-tls.invalid",true);s_parallel_owners[slot]=current_owner(tls);
    xSemaphoreGive(s_parallel_ready);check(xSemaphoreTake(s_parallel_start,pdMS_TO_TICKS(30000))==pdTRUE,"parallel_start");
    transfer(tls,label,slot,true);esp_tls_conn_destroy(tls);xSemaphoreGive(s_parallel_done);vTaskDelete(NULL);
}
static void parallel_roundtrip(void) {
    s_parallel_start=xSemaphoreCreateCounting(2,0);s_parallel_ready=xSemaphoreCreateCounting(2,0);s_parallel_done=xSemaphoreCreateCounting(2,0);
    check(s_parallel_start && s_parallel_ready && s_parallel_done,"parallel_semaphores");
    for(unsigned i=0;i<2;++i)check(xTaskCreatePinnedToCore(parallel_client,"tls-peer",12288,(void *)(uintptr_t)i,3,NULL,(BaseType_t)i)==pdPASS,"parallel_tasks");
    for(unsigned i=0;i<2;++i)check(xSemaphoreTake(s_parallel_ready,pdMS_TO_TICKS(30000))==pdTRUE,"parallel_handshakes_live");
    check(s_parallel_owners[0] && s_parallel_owners[1] && s_parallel_owners[0]!=s_parallel_owners[1],"distinct_two_live_owners");
    printf("TLS_PARALLEL ptr0=%p ptr1=%p live=2\n",s_parallel_owners[0],s_parallel_owners[1]);
    xSemaphoreGive(s_parallel_start);xSemaphoreGive(s_parallel_start);
    for(unsigned i=0;i<2;++i)check(xSemaphoreTake(s_parallel_done,pdMS_TO_TICKS(30000))==pdTRUE,"parallel_complete");
    vSemaphoreDelete(s_parallel_start);vSemaphoreDelete(s_parallel_ready);vSemaphoreDelete(s_parallel_done);integrity();
}
static void pressure_with_live_tls(void) {
    adaptive_input_t *input=adaptive_input_create(6*8192,2*8192,8192);check(input && native_input_reclaim_bind(input),"actual_input_owner_bind");
    void *reading=NULL,*ready=NULL,*writing=NULL;size_t size=0;
    check(adaptive_input_acquire(input,&reading,8192,0)==pdPASS,"reading_acquire");memset(reading,0x51,8192);check(adaptive_input_commit(input,reading)==pdPASS,"reading_commit");
    check(adaptive_input_receive(input,&size,0)==reading && size==8192,"reading_lease");
    check(adaptive_input_acquire(input,&ready,8192,0)==pdPASS,"ready_acquire");memset(ready,0x62,8192);check(adaptive_input_commit(input,ready)==pdPASS,"ready_commit");
    check(adaptive_input_acquire(input,&writing,8192,0)==pdPASS,"writing_acquire");memset(writing,0x73,8192);
    esp_tls_t *tls=open_client("pressure",18443,"cyd-tls.invalid",true);void *live_owner=current_owner(tls);
    adaptive_input_stats_t before=adaptive_input_stats(input);unsigned blocks=0;
    while(blocks<512 && (s_blocks[blocks]=heap_caps_malloc(1024,MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT)))++blocks;
    s_pressure_owner=xTaskGetCurrentTaskHandle();s_pressure=true;void *recovered=mbedtls_calloc(1,4096);s_pressure=false;
    adaptive_input_stats_t after=adaptive_input_stats(input);
    bool proof=blocks<512 && recovered && s_real_nulls>0 && s_real_recoveries>0 && after.released>before.released &&
        after.released-before.released<=before.target-before.minimum && after.resident>=after.minimum &&
        after.ready==before.ready && after.reading==before.reading && after.writing==before.writing && live_owner==current_owner(tls);
    for(unsigned i=0;i<8192;++i)proof=proof && ((uint8_t *)reading)[i]==0x51 && ((uint8_t *)ready)[i]==0x62 && ((uint8_t *)writing)[i]==0x73;
    /* Restore only diagnostic pressure storage after capturing all predicates. */
    for(unsigned i=0;i<blocks;++i) {heap_caps_free(s_blocks[i]);}
    mbedtls_free(recovered);
    check(proof,"real_null_bounded_reclaim_preserves_live_owners");
    printf("TLS_PRESSURE real_null=%u recoveries=%u blocks=%u released=%u budget=%u owner_preserved=1 rx=%p\n",s_real_nulls,s_real_recoveries,blocks,after.released-before.released,before.target-before.minimum,live_owner);
    transfer(tls,"pressure",0,true);esp_tls_conn_destroy(tls);
    check(adaptive_input_cancel(input,writing) && adaptive_input_return(input,reading),"leased_cleanup");
    check(adaptive_input_receive(input,&size,0)==ready && adaptive_input_return(input,ready),"ready_cleanup");
    check(native_input_reclaim_detach(input)==NATIVE_INPUT_RECLAIM_DETACHED,"actual_input_owner_detach");adaptive_input_destroy(input);integrity();
}
void app_main(void) {
    native_tls_early_mpi_prepare();struct timeval now={.tv_sec=TLS_TEST_EPOCH};check(settimeofday(&now,NULL)==0,"valid_guest_clock");
    network_start();roundtrip("first");roundtrip("reopen");
    open_client("wrong_name",18443,"wrong.invalid",false);open_client("handshake_close",18444,"cyd-tls.invalid",false);
    esp_tls_t *tls=open_client("truncated_record",18445,"cyd-tls.invalid",true);transfer(tls,"truncated_record",0,false);esp_tls_conn_destroy(tls);
    roundtrip("after_failures");parallel_roundtrip();pressure_with_live_tls();roundtrip("after_pressure");
    check(s_early_mpi_calls==1 && s_attaches==10 && !s_attach_failures,"full_bundle_attach_lifecycle");
#if CONFIG_YORADIO_TLS_STATIC_RX_RESERVE
    check(s_rx_calls==s_rx_frees && s_attaches==s_rx_calls,"full_actual_rx_lifecycle");
    printf("TLS_TRAFFIC_PASS allocations=%u frees=%u attaches=%u full_responses=7 parallel_live=2 pressure_recovered=1\n",s_rx_calls,s_rx_frees,s_attaches);
#else
    printf("TLS_TRAFFIC_PASS dynamic=1 attaches=%u full_responses=7 parallel_live=2 pressure_recovered=1\n",s_attaches);
#endif
    fflush(stdout);for(;;)vTaskDelay(pdMS_TO_TICKS(1000));
}
