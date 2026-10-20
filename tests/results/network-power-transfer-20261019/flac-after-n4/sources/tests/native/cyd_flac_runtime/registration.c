#include <assert.h>
#include <stdio.h>
typedef int esp_audio_err_t;
#define ESP_AUDIO_ERR_OK 0
static unsigned calls, failure, flac_calls, containers_freed, codecs_freed;
static int register_one(void) { return ++calls == failure ? -17 : 0; }
static int esp_mp3_dec_register(void) { return register_one(); }
static int esp_aac_dec_register(void) { return register_one(); }
static int esp_flac_dec_register(void) { ++flac_calls; return register_one(); }
static int esp_vorbis_dec_register(void) { return register_one(); }
static int esp_opus_dec_register(void) { return register_one(); }
static int esp_audio_simple_dec_register_default(void) { return register_one(); }
static void esp_audio_simple_dec_unregister_default(void) { ++containers_freed; }
static void esp_audio_dec_unregister_all(void) { ++codecs_freed; }
#include "registration.inc"
int main(void) {
    assert(decoder_register_codecs() == 0);
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
    assert(!flac_calls);
#else
    assert(flac_calls == 1);
#endif
    unsigned count = calls;
    for (unsigned step = 1; step <= count; ++step) {
        calls = containers_freed = codecs_freed = flac_calls = 0; failure = step;
        assert(decoder_register_codecs() == -17);
        assert(calls == step && containers_freed == 1 && codecs_freed == 1);
    }
    puts("PASS actual decoder registration, selected FLAC backend and every failure rollback");
}
