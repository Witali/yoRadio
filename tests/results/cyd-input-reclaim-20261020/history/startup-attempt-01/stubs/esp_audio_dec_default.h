#include "esp_audio_dec.h"
esp_audio_err_t esp_mp3_dec_register(void);
esp_audio_err_t esp_aac_dec_register(void);
esp_audio_err_t esp_flac_dec_register(void);
esp_audio_err_t esp_vorbis_dec_register(void);
esp_audio_err_t esp_opus_dec_register(void);
void esp_audio_dec_unregister_all(void);
