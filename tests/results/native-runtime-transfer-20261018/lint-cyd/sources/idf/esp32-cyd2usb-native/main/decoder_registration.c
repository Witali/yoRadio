#include "decoder_registration.h"

#include "esp_audio_dec_default.h"
#include "esp_audio_simple_dec_default.h"
#include "sdkconfig.h"

void decoder_unregister_codecs(void) {
    // The pinned archive has no container unregister_all. Release the exact
    // enabled default container set before releasing frame-decoder entries.
    esp_audio_simple_dec_unregister_default();
    esp_audio_dec_unregister_all();
}

esp_audio_err_t decoder_register_codecs(void) {
    esp_audio_err_t result;
#define REGISTER_CODEC(function) do { \
    result = function(); \
    if (result != ESP_AUDIO_ERR_OK) goto failed; \
} while (0)
    // Helix/minimp3 implementations are linked directly, without registry use.
#ifdef CONFIG_YORADIO_MP3_DECODER_ESPRESSIF
    REGISTER_CODEC(esp_mp3_dec_register);
#endif
#ifdef CONFIG_YORADIO_AAC_DECODER_ESPRESSIF
    REGISTER_CODEC(esp_aac_dec_register);
#endif
    REGISTER_CODEC(esp_flac_dec_register);
    REGISTER_CODEC(esp_vorbis_dec_register);
    REGISTER_CODEC(esp_opus_dec_register);
    REGISTER_CODEC(esp_audio_simple_dec_register_default);
#undef REGISTER_CODEC
    return ESP_AUDIO_ERR_OK;
failed:
    decoder_unregister_codecs();
    return result;
}
