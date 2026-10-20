/* Production backend control flow; only platform/DSP/driver APIs are seams.
 * A successful fake disable is the DMA barrier. Writes merely load DMA. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int esp_err_t;
#include "cyd_output_metrics_noop.h"
enum { ESP_OK, ESP_FAIL, ESP_ERR_INVALID_ARG, ESP_ERR_INVALID_STATE,
       ESP_ERR_NOT_SUPPORTED, ESP_ERR_NO_MEM, ESP_ERR_TIMEOUT };
#define ESP_RETURN_ON_ERROR(expr, ...) do { int e=(expr); if(e) return e; } while(0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define BOARD_AUDIO_DATA 26
#define GPIO_MODE_OUTPUT 1
#define pdMS_TO_TICKS(x) (x)
#ifndef CYD_MAINTENANCE_HOST
static void vTaskDelay(unsigned t) {(void)t;}
#endif
#ifndef MAINTENANCE_DRIVER_HOOK
#define MAINTENANCE_DRIVER_HOOK(name) ((void)0)
#endif
static unsigned pins_low;
static void gpio_reset_pin(int p) {(void)p;}
static void gpio_set_direction(int p,int d) {(void)p;(void)d;}
static void gpio_set_level(int p,int l) {(void)p;assert(!l);++pins_low;}
static bool native_audio_settings_get_normalization(void) {return false;}
static uint8_t native_audio_settings_get_normalization_gain_db(void) {return 6;}
static int8_t native_audio_settings_get_normalization_target_dbfs(void) {return -3;}
static uint16_t native_audio_settings_get_normalization_time_ms(void) {return 500;}
static uint8_t native_audio_settings_get_volume(void) {return 254;}
static int8_t native_audio_settings_get_balance(void) {return 0;}
static int native_audio_settings_set_volume(uint8_t v) {(void)v;return ESP_OK;}
static int native_audio_settings_set_balance(int8_t v) {(void)v;return ESP_OK;}
static void native_audio_normalizer_configure(bool e,uint8_t g,int8_t t,uint16_t m,uint32_t r) {(void)e;(void)g;(void)t;(void)m;(void)r;}
static void native_audio_normalizer_reset(void) {}
static void native_audio_normalizer_process_block(int16_t *p,size_t n,uint8_t c) {(void)p;(void)n;(void)c;}

typedef struct { atomic_bool allocated,running; } driver_t;
static driver_t driver;
static atomic_uint allocations,disables,deletes,writes;
static atomic_bool fail_disable,fail_delete,fail_enable,fail_prime;
static int allocate(void **out) {assert(!driver.allocated);driver=(driver_t){true,false};*out=&driver;++allocations;return ESP_OK;}
static int enable(void *h) {assert(h==&driver && driver.allocated);if(fail_enable)return ESP_FAIL;driver.running=true;return ESP_OK;}
static int disable(void *h) {assert(h==&driver && driver.allocated && driver.running);MAINTENANCE_DRIVER_HOOK("disable");++disables;if(fail_disable)return ESP_FAIL;driver.running=false;return ESP_OK;}
static int release(void *h) {assert(h==&driver && driver.allocated && !driver.running);++deletes;if(fail_delete)return ESP_FAIL;driver.allocated=false;return ESP_OK;}
static int write_driver(void *h,const void *p,size_t n,size_t *done,unsigned timeout) {
    assert(h==&driver && driver.allocated && driver.running && p && timeout);
    MAINTENANCE_DRIVER_HOOK("write");
    ++writes;*done=fail_prime ? 0:n;return fail_prime ? ESP_FAIL:ESP_OK;
}
typedef void *i2s_chan_handle_t;
typedef struct { unsigned unused; } i2s_event_data_t;
typedef struct { bool (*on_send_q_ovf)(i2s_chan_handle_t, i2s_event_data_t *, void *); } i2s_event_callbacks_t;
static int i2s_channel_register_event_callback(void *h, const i2s_event_callbacks_t *c, void *context) {
    assert(h==&driver && c && c->on_send_q_ovf && !context); return ESP_OK;
}

typedef struct {unsigned dma_desc_num,dma_frame_num;bool auto_clear_after_cb,auto_clear_before_cb;} i2s_chan_config_t;
typedef struct {int clk_cfg,slot_cfg;struct {int clk,dout;struct {bool clk_inv;} invert_flags;} gpio_cfg;} i2s_pdm_tx_config_t;
typedef struct {unsigned bclk_hz;} i2s_chan_info_t;
enum {I2S_NUM_0,I2S_ROLE_MASTER,I2S_GPIO_UNUSED=-1,I2S_SLOT_MODE_MONO=1,I2S_DATA_BIT_WIDTH_16BIT=16};
#define I2S_CHANNEL_DEFAULT_CONFIG(...) ((i2s_chan_config_t){0})
#define I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(...) 0
#define I2S_PDM_TX_SLOT_DEFAULT_CONFIG(...) 0
static int i2s_new_channel(const i2s_chan_config_t *c,void **out,void *rx) {assert(c->dma_desc_num==8 && !rx);return allocate(out);}
static int i2s_channel_init_pdm_tx_mode(void *h,const void *c) {(void)h;(void)c;return ESP_OK;}
static int i2s_channel_preload_data(void *h,const void *p,size_t n,size_t *done) {assert(h==&driver && p);*done=n;return ESP_OK;}
static int i2s_channel_enable(void *h) {return enable(h);}
static int i2s_channel_disable(void *h) {return disable(h);}
static int i2s_del_channel(void *h) {return release(h);}
static int i2s_channel_get_info(void *h,i2s_chan_info_t *i) {assert(h==&driver);i->bclk_hz=6144000;return ESP_OK;}
static int i2s_channel_write(void *h,const void *p,size_t n,size_t *done,unsigned t) {return write_driver(h,p,n,done,t);}
typedef void *dac_continuous_handle_t;
typedef struct {unsigned chan_mask,desc_num,buf_size,freq_hz;int offset,clk_src,chan_mode;} dac_continuous_config_t;
enum {DAC_CHANNEL_MASK_CH1=1,DAC_DIGI_CLK_SRC_APLL,DAC_CHANNEL_MODE_SIMUL};
static int dac_continuous_new_channels(const dac_continuous_config_t *c,void **out) {assert(c->desc_num==6);return allocate(out);}
static int dac_continuous_enable(void *h) {return enable(h);}
static int dac_continuous_disable(void *h) {return disable(h);}
static int dac_continuous_del_channels(void *h) {return release(h);}
static int dac_continuous_write(void *h,const void *p,size_t n,size_t *done,unsigned t) {return write_driver(h,p,n,done,t);}
typedef struct {unsigned mode,sample_rate,bits_per_sample,channel_format,communication_format,intr_alloc_flags,dma_buf_count,dma_buf_len;bool use_apll,tx_desc_auto_clear;int fixed_mclk;} i2s_config_t;
enum {I2S_MODE_MASTER=1,I2S_MODE_TX=2,I2S_MODE_DAC_BUILT_IN=4,I2S_BITS_PER_SAMPLE_16BIT=16,I2S_CHANNEL_FMT_RIGHT_LEFT,I2S_COMM_FORMAT_STAND_MSB,ESP_INTR_FLAG_LEVEL1,I2S_PIN_NO_CHANGE,I2S_DAC_CHANNEL_LEFT_EN};
static int idf6_dac_output_configure(const i2s_config_t *c,int mode) {assert(c && mode==I2S_DAC_CHANNEL_LEFT_EN);return ESP_OK;}
static int idf6_dac_output_begin(void) {void *h;int e=allocate(&h);return e ? e:enable(h);}
static int idf6_dac_output_end(void) {if(fail_disable)return ESP_FAIL;int e=disable(&driver);return e ? e:release(&driver);}
static int idf6_dac_output_set_sample_rate(unsigned r) {assert(r);return ESP_OK;}
static int idf6_dac_output_write(const void *p,size_t n,size_t *done,unsigned t) {return write_driver(&driver,p,n,done,t);}
esp_err_t native_audio_output_pause(void);
#include "production.inc"

#ifndef CYD_MAINTENANCE_HOST
int main(void) {
    unsigned cases=0;
    assert(native_audio_output_init()==ESP_OK);
    assert(native_audio_output_pause()==ESP_OK);++cases;
    assert(native_audio_output_configure(16000)==ESP_OK);assert(driver.running);++cases;
    unsigned before_cancel=writes;
    native_audio_output_request_pause(true);
    const uint8_t cancelled[64]={0};
    assert(native_audio_output_write_pcm(cancelled,sizeof(cancelled),16,1)==ESP_ERR_INVALID_STATE);
    native_audio_output_idle();assert(writes==before_cancel);++cases;
    native_audio_output_request_pause(false);
    unsigned old_allocations=allocations,old_pins=pins_low;
    fail_disable=true;
    assert(native_audio_output_pause()!=ESP_OK);
    assert(driver.allocated && driver.running && allocations==old_allocations);
    assert(pins_low==old_pins);++cases;
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM
    assert(s_pdm==&driver && s_pdm_running);
#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC
    assert(s_dac==&driver && s_dac_enabled);
    assert(native_audio_output_configure(22050)!=ESP_OK);
    assert(driver.running && allocations==old_allocations);++cases;
#else
    assert(s_legacy_installed);
#endif
    fail_disable=false;
#if !CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC
    fail_delete=true;
    assert(native_audio_output_pause()!=ESP_OK);
    assert(driver.allocated && !driver.running);++cases;
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC
    assert(native_audio_output_configure(16000)!=ESP_OK);
    assert(driver.allocated && !driver.running && allocations==old_allocations);++cases;
#endif
    unsigned old_disables=disables;
    fail_delete=false;
    assert(native_audio_output_pause()==ESP_OK);
    assert(!driver.allocated && disables==old_disables);++cases;
#else
    assert(native_audio_output_pause()==ESP_OK);assert(!driver.allocated);++cases;
#endif
    unsigned old_writes=writes;
    native_audio_output_idle();assert(writes==old_writes);++cases;
    assert(native_audio_output_pause()==ESP_OK);++cases;
    assert(native_audio_output_configure(16000)==ESP_OK);
    assert(driver.running && allocations==old_allocations+1);++cases;
    const uint8_t data[64]={0};
    assert(native_audio_output_write_pcm(data,sizeof(data),16,1)==ESP_OK);++cases;
    assert(native_audio_output_pause()==ESP_OK);assert(!driver.allocated);++cases;
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC
    fail_enable=true;
    assert(native_audio_output_configure(16000)!=ESP_OK);
    assert(driver.allocated && !driver.running && !s_dac_enabled);++cases;
    fail_enable=false;
    assert(native_audio_output_pause()==ESP_OK);assert(!driver.allocated);++cases;
    fail_prime=true;
    assert(native_audio_output_configure(16000)!=ESP_OK);assert(driver.running && !s_dac_sample_rate);++cases;
    fail_prime=false;
    assert(native_audio_output_configure(16000)==ESP_OK);++cases;
    assert(native_audio_output_pause()==ESP_OK);free(s_dac_data);
#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC
    free(s_legacy_frames);
#endif
    printf("PASS %u cases; real production pause/ownership; driver DMA barrier seam\n",cases);
    return 0;
}
#endif
