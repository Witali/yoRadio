#pragma once
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int esp_err_t;
enum { ESP_OK, ESP_FAIL, ESP_ERR_INVALID_ARG, ESP_ERR_INVALID_STATE,
       ESP_ERR_TIMEOUT, ESP_ERR_NOT_SUPPORTED };
#define ESP_RETURN_ON_ERROR(expr, ...) do { int e=(expr); if(e) return e; } while(0)
#define ESP_ERROR_CHECK(expr) assert((expr)==ESP_OK)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define IRAM_ATTR
#define DRAM_ATTR
#define SOC_I2S_PDM_MAX_TX_LINES 2
#define GPIO_MODE_OUTPUT 1
#define BOARD_AUDIO_LEFT_DATA 10
#define BOARD_AUDIO_RIGHT_DATA 3
typedef int gpio_num_t;
static void gpio_reset_pin(int p) {(void)p;}
static void gpio_set_direction(int p,int d) {(void)p;(void)d;}
static void gpio_set_level(int p,int l) {(void)p;(void)l;}
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
typedef uint32_t TickType_t;
typedef int BaseType_t;
static void vTaskDelay(unsigned ticks) {(void)ticks;}
static int64_t test_now_us;
static int64_t esp_timer_get_time(void) {return test_now_us;}

enum { I2S_DIR_TX, I2S_DIR_RX, I2S_CHAN_STATE_READY, I2S_CHAN_STATE_RUNNING };
enum { I2S_NUM_0, I2S_ROLE_MASTER, I2S_GPIO_UNUSED=-1, I2S_DATA_BIT_WIDTH_16BIT=16,
       I2S_SLOT_MODE_STEREO=2 };
typedef struct { unsigned guard1; int16_t pcm[1024]; unsigned guard2; } test_dma_t;
typedef struct { uint8_t *buf; } lldesc_t;
typedef struct { bool held, fail; } test_lock_t;
typedef test_lock_t *SemaphoreHandle_t;
typedef struct { void *items[8]; unsigned used, next; bool running, fail; unsigned spaces; } test_queue_t;
typedef test_queue_t *QueueHandle_t;
enum { pdTRUE=1, pdFALSE=0 };
static int xSemaphoreTake(SemaphoreHandle_t s,unsigned timeout) {
    (void)timeout; if(s->fail) return pdFALSE; assert(!s->held); s->held=true;return pdTRUE;
}
static void xSemaphoreGive(SemaphoreHandle_t s) {assert(s->held);s->held=false;}
static void xQueueReset(QueueHandle_t q) {q->used=q->next=0;}
static int xQueueSend(QueueHandle_t q,const void *p,unsigned timeout) {
    (void)timeout;if(q->used==8)return pdFALSE; q->items[q->used++]=*(void *const *)p;return pdTRUE;
}
static int xQueueReceive(QueueHandle_t q,void *p,unsigned timeout) {
    (void)timeout;if(q->fail || !q->used)return pdFALSE;
    *(void **)p=q->items[q->next++];if(q->next==q->used) {
        if(q->running)q->next=0;else q->used=q->next=0;
    }return pdTRUE;
}
static unsigned uxQueueSpacesAvailable(QueueHandle_t q) {return q->spaces;}
typedef struct i2s_channel_obj_t {
    int dir,state;
    struct {unsigned desc_num,buf_size,rw_pos;void *curr_ptr;lldesc_t **desc;} dma;
    SemaphoreHandle_t mutex,binary;QueueHandle_t msg_queue;
} *i2s_chan_handle_t;
typedef struct { void *dma_buf; size_t size; } i2s_event_data_t;
typedef struct {
    bool (*on_send_q_ovf)(i2s_chan_handle_t, i2s_event_data_t *, void *);
} i2s_event_callbacks_t;
static i2s_event_callbacks_t test_callbacks;
static esp_err_t test_callback_registration_result;
static int i2s_channel_register_event_callback(i2s_chan_handle_t h,
    const i2s_event_callbacks_t *callbacks, void *user) {
    assert(h->state == I2S_CHAN_STATE_READY && !user);
    if (test_callback_registration_result) return test_callback_registration_result;
    test_callbacks = *callbacks;
    return ESP_OK;
}
typedef struct {unsigned dma_desc_num,dma_frame_num;bool auto_clear_after_cb,auto_clear_before_cb;} i2s_chan_config_t;
typedef struct {int clk_cfg,slot_cfg;struct {int clk,dout,dout2;struct {bool clk_inv;} invert_flags;} gpio_cfg;} i2s_pdm_tx_config_t;
typedef struct {uint32_t bclk_hz;} i2s_chan_info_t;
#define I2S_CHANNEL_DEFAULT_CONFIG(...) ((i2s_chan_config_t){0})
#define I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(...) 0
#define I2S_PDM_TX_SLOT_DAC_DEFAULT_CONFIG(...) 0
typedef void (*native_i2s_fill_t)(void *,int16_t *,size_t);
static test_dma_t blocks[4];
static lldesc_t descriptors[4],*desc_ptrs[4];
static test_lock_t mutex_lock,binary_lock;
static test_queue_t queue;
static struct i2s_channel_obj_t channel;
static unsigned volume=254;static int balance;static bool normalize;
static unsigned last_peak,normalizer_calls;
static FILE *capture;
static size_t captured;
static esp_err_t i2s_new_channel(const i2s_chan_config_t *cfg,i2s_chan_handle_t *out,void *rx) {
    (void)rx;assert(cfg->dma_desc_num==4 && cfg->dma_frame_num==512);
    memset(&channel,0,sizeof(channel));memset(&queue,0,sizeof(queue));
    mutex_lock=(test_lock_t){0};binary_lock=(test_lock_t){0};queue.spaces=4;
    for(unsigned i=0;i<4;++i){blocks[i].guard1=blocks[i].guard2=0x1234abcd;descriptors[i].buf=(uint8_t *)blocks[i].pcm;desc_ptrs[i]=&descriptors[i];}
    channel.dir=I2S_DIR_TX;channel.state=I2S_CHAN_STATE_READY;
    channel.dma.desc_num=4;channel.dma.buf_size=2048;channel.dma.desc=desc_ptrs;
    channel.mutex=&mutex_lock;channel.binary=&binary_lock;channel.msg_queue=&queue;
    *out=&channel;return ESP_OK;
}
static int i2s_channel_init_pdm_tx_mode(i2s_chan_handle_t h,const i2s_pdm_tx_config_t *c){(void)h;(void)c;return 0;}
static int i2s_del_channel(i2s_chan_handle_t h){(void)h;return 0;}
static int i2s_channel_enable(i2s_chan_handle_t h){
    h->state=I2S_CHAN_STATE_RUNNING;h->dma.curr_ptr=NULL;h->dma.rw_pos=0;
    queue.used=4;queue.next=0;queue.running=true;
    for(unsigned i=0;i<4;++i)queue.items[i]=blocks[i].pcm;
    return 0;
}
static int i2s_channel_disable(i2s_chan_handle_t h){h->state=I2S_CHAN_STATE_READY;return 0;}
static int i2s_channel_get_info(i2s_chan_handle_t h,i2s_chan_info_t *i){(void)h;i->bclk_hz=6144000;return 0;}
static void audio_level_led_update_peak(uint16_t p){last_peak=p;}
static bool native_audio_settings_get_normalization(void){return normalize;}
static unsigned native_audio_settings_get_normalization_gain_db(void){return 6;}
static int native_audio_settings_get_normalization_target_dbfs(void){return -3;}
static unsigned native_audio_settings_get_normalization_time_ms(void){return 500;}
static void native_audio_normalizer_configure(bool e,uint8_t g,int8_t t,uint16_t ms,uint32_t r){(void)e;(void)g;(void)t;(void)ms;(void)r;}
static void native_audio_normalizer_set_sample_rate(uint32_t r){(void)r;}
static void native_audio_normalizer_reset(void){}
static void native_audio_normalizer_process_block(int16_t *p,size_t n,uint8_t c){
    ++normalizer_calls;if(normalize)for(size_t i=0;i<n*c;++i)p[i]/=2;
}
static uint8_t native_audio_settings_get_volume(void){return volume;}
static int8_t native_audio_settings_get_balance(void){return balance;}
static int native_audio_settings_set_volume(uint8_t v){volume=v;return 0;}
static int native_audio_settings_set_balance(int8_t b){balance=b;return 0;}

esp_err_t tested_i2s_write_generated(i2s_chan_handle_t,size_t,native_i2s_fill_t,void *,bool,size_t *);
typedef struct {native_i2s_fill_t fill;void *context;} tap_t;
static void tap_fill(void *context,int16_t *dma,size_t frames){
    tap_t *tap=context;bool valid=false;
    for(unsigned i=0;i<4;++i) {
        uintptr_t p=(uintptr_t)dma,b=(uintptr_t)blocks[i].pcm;
        if(p>=b && p+frames*4<=b+sizeof(blocks[i].pcm))valid=true;
    }
    assert(valid && (mutex_lock.held || binary_lock.held));
    tap->fill(tap->context,dma,frames);
    for(unsigned i=0;i<4;++i)assert(blocks[i].guard1==0x1234abcd && blocks[i].guard2==0x1234abcd);
    if(capture){assert(fwrite(dma,4,frames,capture)==frames);captured+=frames*4;}
}
static esp_err_t native_i2s_write_generated(i2s_chan_handle_t h,size_t n,native_i2s_fill_t f,void *ctx,bool pre,size_t *written){
    tap_t tap={f,ctx};return tested_i2s_write_generated(h,n,tap_fill,&tap,pre,written);
}
esp_err_t tested_i2s_write_full_block(i2s_chan_handle_t,native_i2s_fill_t,void *);
static size_t full_blocks;
static bool expect_full;
static void tap_full(void *ctx, int16_t *dma, size_t frames) {
    assert(frames == 512 && channel.dma.rw_pos == 0);
    ++full_blocks;
    tap_fill(ctx,dma,frames);
}
static esp_err_t native_i2s_write_full_block(i2s_chan_handle_t h,native_i2s_fill_t f,void *ctx) {
    tap_t tap={f,ctx};return tested_i2s_write_full_block(h,tap_full,&tap);
}
typedef struct {const uint8_t *data;} copy_t;
static void fill_copy(void *ctx,int16_t *dma,size_t frames){copy_t *c=ctx;memcpy(dma,c->data,frames*4);c->data+=frames*4;}
static unsigned test_write_delay_us;
static size_t test_short_write_bytes;
static int i2s_channel_write(i2s_chan_handle_t h,const void *p,size_t n,size_t *written,unsigned timeout){
    test_now_us += test_write_delay_us;
    if (test_short_write_bytes) {assert(test_short_write_bytes<n); *written=test_short_write_bytes; return ESP_OK;}
    (void)timeout;copy_t c={p};size_t frames=0;int e=native_i2s_write_generated(h,n/4,fill_copy,&c,false,&frames);*written=frames*4;return e;
}
static int i2s_channel_preload_data(i2s_chan_handle_t h,const void *p,size_t n,size_t *written){
    copy_t c={p};size_t frames=0;int e=native_i2s_write_generated(h,n/4,fill_copy,&c,true,&frames);*written=frames*4;return e;
}
