#include "decoder_registration.h"
#include "esp_audio_dec_default.h"
#include "esp_audio_simple_dec_default.h"
#include "sdkconfig.h"

esp_audio_err_t decoder_register_codecs(void) {
    esp_audio_err_t result;
#define REGISTER_CODEC(function) do { \
    result = function(); \
    if (result != ESP_AUDIO_ERR_OK) goto failed; \
} while (0)
#ifndef CONFIG_YORADIO_QEMU_VORBIS_LIFECYCLE
#ifdef CONFIG_YORADIO_MP3_DECODER_ESPRESSIF
    REGISTER_CODEC(esp_mp3_dec_register);
#endif
#ifdef CONFIG_YORADIO_AAC_DECODER_ESPRESSIF
    REGISTER_CODEC(esp_aac_dec_register);
#endif
#ifdef CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF
    REGISTER_CODEC(esp_flac_dec_register);
#endif
#endif
    REGISTER_CODEC(esp_vorbis_dec_register);
#ifndef CONFIG_YORADIO_QEMU_VORBIS_LIFECYCLE
    REGISTER_CODEC(esp_opus_dec_register);
    REGISTER_CODEC(esp_audio_simple_dec_register_default);
#else
    REGISTER_CODEC(esp_ogg_dec_register);
#endif
#undef REGISTER_CODEC
    return ESP_AUDIO_ERR_OK;
failed:
    /* This task owns the registry. The pinned archive does not implement
     * unregister_all for containers; release exactly those we register. */
#ifndef CONFIG_YORADIO_QEMU_VORBIS_LIFECYCLE
    esp_audio_simple_dec_unregister_default();
#else
    esp_ogg_dec_unregister();
#endif
    esp_audio_dec_unregister_all();
    return result;
}
