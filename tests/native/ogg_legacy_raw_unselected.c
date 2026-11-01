/* Legacy-only HOST models: raw synthesis must remain unselected. These exact
 * documented public signatures intentionally abort rather than fake a result.
 */
#include <stdlib.h>
#include "esp_opus_dec.h"
esp_audio_err_t esp_opus_dec_open(void *config,uint32_t bytes,void **handle) {
    (void)config;(void)bytes;(void)handle;abort();
}
esp_audio_err_t esp_opus_dec_decode(void *handle,esp_audio_dec_in_raw_t *raw,
    esp_audio_dec_out_frame_t *frame,esp_audio_dec_info_t *info) {
    (void)handle;(void)raw;(void)frame;(void)info;abort();
}
esp_audio_err_t esp_opus_dec_close(void *handle) {(void)handle;abort();}
