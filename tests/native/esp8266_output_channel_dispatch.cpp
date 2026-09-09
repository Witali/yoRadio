#include <algorithm>
#include <cstdint>
#include <climits>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>
#include "rc_pdm_feedback.h"
#include "rcpdm_feedback_reference.h"
#include "rcpdm_variants.h"
#include "rcpdm_simple.h"
#include "rcpdm_simple_reference.h"

#ifdef _MSC_VER
#define __attribute__(x)
#endif
#define YORADIO_ESP8266_SPI_PDM 0
#define YORADIO_ESP8266_I2S_PDM 1
#define CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32 1
#define YORADIO_ESP8266_OUTPUT_COMPARE 0
#define RCPDM_DISABLE_BATCH 0
#if RCPDM_TEST_SIMPLE
#define RCPDM_TEST_SAMPLE rcpdm_simple_sample
#endif
#define BOARD_I2S_PDM_SAMPLE_RATE 48000U
#define BOARD_I2S_PDM_OVERSAMPLE 32U
#define BOARD_I2S_PDM_REPEAT 1U
#define BOARD_I2S_PDM_BCK_DIV 8U
#define BOARD_I2S_PDM_CLKM_DIV 13U
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define pdMS_TO_TICKS(x) (x)
using TickType_t = uint32_t;
using esp_err_t = int;
enum {ESP_OK, ESP_ERR_TIMEOUT, ESP_ERR_INVALID_ARG, ESP_ERR_INVALID_STATE};
static void check(bool value, const char *message) {
    if (!value) throw std::runtime_error(message);
}
static TickType_t xTaskGetTickCount() { return 0; }
static uint32_t s_input_sample_rate, s_resample_phase;
static bool s_i2s_started;
static uint32_t s_i2s_pdm_partial_word;
static uint8_t s_i2s_pdm_partial_bits;
#if CONFIG_YORADIO_RCPDM_FEEDBACK
static rc_pdm_feedback_t s_rcpdm;
#elif CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
static rc_pdm_t s_rcpdm;
#else
static uint32_t s_pdm_integrator;
#endif
static uint32_t dma_words[512];
static size_t dma_capacity = 512;
static bool fail_reserve, fail_commit;
static std::vector<uint32_t> emitted;
static unsigned normalized_channels;
static esp_err_t esp8266_nodac_i2s_init(uint32_t, unsigned, unsigned) { return ESP_OK; }
static void esp8266_nodac_i2s_silence(uint32_t) {}
static esp_err_t esp8266_nodac_i2s_reserve(uint32_t **words, size_t *capacity, TickType_t) {
    if (fail_reserve) return ESP_ERR_TIMEOUT;
    *words = dma_words; *capacity = dma_capacity;
    return ESP_OK;
}
static esp_err_t esp8266_nodac_i2s_commit(size_t words) {
    check(words <= dma_capacity, "DMA write outside span");
    if (fail_commit && words) return ESP_ERR_TIMEOUT;
    emitted.insert(emitted.end(), dma_words, dma_words + words);
    return ESP_OK;
}
static void native_audio_normalizer_configure(bool, uint8_t, int8_t, uint16_t, uint32_t) {}
static void native_audio_normalizer_process(int16_t *, size_t, uint8_t channels) {
    normalized_channels = channels;
}
static void native_audio_output_reload_settings() {}

#if CONFIG_YORADIO_STATUS_LED
static volatile bool status_led_capture_requested = true;
static unsigned led_blocks, led_clears;
static uint16_t led_peak;
static void status_led_publish_peak(uint16_t peak) {
    led_peak = peak;
    ++led_blocks;
}
static void status_led_clear() { ++led_clears; }
#endif

#include "output_under_test.inc"

struct Reference {
    uint32_t rate = 0, phase = 0, integrator = 0;
    rc_pdm_feedback_t feedback;
    rc_pdm_t rc;
    Reference() { rc_pdm_feedback_init(&feedback, RC_FB_DEFAULT_SEED); rc_pdm_init(&rc); }
    uint32_t pack(int16_t sample) {
#if CONFIG_YORADIO_RCPDM_FEEDBACK
        return rc_feedback_reference_sample(&feedback, sample);
#elif CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
#if RCPDM_TEST_SIMPLE
        return rcpdm_simple_reference(&rc, sample);
#else
        return rc_candidate_original(&rc, sample);
#endif
#else
        uint32_t word = 0;
        for (unsigned bit = 0; bit < 32; ++bit) {
            integrator += uint32_t(int32_t(sample) + 32768);
            bool high = integrator >= 65536;
            if (high) integrator -= 65536;
            word = (word << 1) | high;
        }
        return word;
#endif
    }
    bool same() const {
#if CONFIG_YORADIO_RCPDM_FEEDBACK
        return !std::memcmp(&feedback, &s_rcpdm, sizeof(feedback));
#elif CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
        return rc.rc == s_rcpdm.rc;
#else
        return integrator == s_pdm_integrator;
#endif
    }
};
static int16_t reference_scale(int16_t pcm, unsigned gain) {
    int64_t product = int64_t(pcm) * gain;
    int64_t rounded = (std::abs(product) + 16384) / 32768;
    return int16_t(std::clamp<int64_t>(product < 0 ? -rounded : rounded, -32768, 32767));
}

int main() {
    try {
        check(native_audio_output_init() == ESP_OK, "init");
        Reference reference;
        uint32_t random = 8266;
        size_t blocks = 0, words = 0;
        for (unsigned capacity : {1U, 31U, 512U}) {
            dma_capacity = capacity;
            for (unsigned rate : {48000U, 44100U, 22050U, 96000U})
                for (int balance : {-16, 0, 16}) for (unsigned volume : {0U, 160U, 254U})
                    for (unsigned channels : {1U, 1U, 2U, 2U, 1U})
                        for (unsigned frames : {1U, 3U, 4U, 5U, 32U, 127U, 128U, 129U, 513U}) {
                            s_balance = int8_t(balance); s_volume = uint8_t(volume);
                            std::vector<int16_t> pcm(frames * channels), scaled;
                            for (auto &sample : pcm) {
                                random = random * 1664525U + 1013904223U;
                                sample = int16_t(random >> 16);
                            }
                            pcm[0] = INT16_MIN;
                            if (pcm.size() > 1) pcm[1] = INT16_MAX;
                            scaled = pcm;
                            if (reference.rate != rate) { reference.rate = rate; reference.phase = 0; }
                            std::vector<uint32_t> expected;
                            for (unsigned i = 0; i < frames; ++i) {
                                int32_t mono = 0;
                                for (unsigned ch = 0; ch < channels; ++ch) {
                                    int atten = channels == 1 ? 16 : ch == 0 ? 16 + std::min(balance, 0) : 16 - std::max(balance, 0);
                                    unsigned gain = (volume * unsigned(atten) * 32768U + 2032U) / 4064U;
                                    auto value = reference_scale(pcm[i * channels + ch], gain);
                                    scaled[i * channels + ch] = value;
                                    mono += value;
                                }
                                mono /= int(channels);
                                reference.phase += 48000;
                                while (reference.phase >= rate) {
                                    expected.push_back(reference.pack(int16_t(mono)));
                                    reference.phase -= rate;
                                }
                            }
                            emitted.clear();
#if CONFIG_YORADIO_STATUS_LED
                            status_led_capture_requested = (blocks % 2) == 0;
                            const unsigned previous_led_blocks = led_blocks;
#endif
                            check(native_audio_output_write(pcm.data(), pcm.size(), rate, uint8_t(channels)) == ESP_OK, "write");
                            check(pcm == scaled, "gain/mono balance changed");
#if CONFIG_YORADIO_STATUS_LED
                            unsigned expected_peak = 0;
                            for (unsigned frame = 0; frame < std::min(frames, 128U); frame += 4) {
                                int value = scaled[frame * channels];
                                if (channels == 2) value = (value + scaled[frame * channels + 1]) / 2;
                                expected_peak = std::max(expected_peak, unsigned(std::abs(value)));
                            }
                            if (status_led_capture_requested) {
                                check(led_peak == expected_peak, "LED must use every fourth post-gain mono frame");
                                check(led_blocks == previous_led_blocks + 1, "one peak publication per selected block");
                            } else check(led_blocks == previous_led_blocks, "inactive LED snapshot must do no publication");
#endif
                            check(emitted == expected, "PDM sequence or DMA boundary changed");
                            check(reference.same() && s_resample_phase == reference.phase, "state discontinuity");
                            check(normalized_channels == channels, "normalizer format");
                            check(s_i2s_pdm_channels == channels && s_i2s_pdm_write ==
                                (channels == 1 ? i2s_pdm_write_mono : i2s_pdm_write_stereo), "wrong cached writer");
                            words += emitted.size(); ++blocks;
                        }
        }
        int16_t input[] = {-32768, 32767};
        auto selected = s_i2s_pdm_write;
        for (unsigned channels : {0U, 3U})
            check(native_audio_output_write(input, 2, 48000, uint8_t(channels)) == ESP_ERR_INVALID_ARG, "invalid channels");
        check(native_audio_output_write(input, 1, 48000, 2) == ESP_ERR_INVALID_ARG, "odd stereo");
        check(native_audio_output_write(input, 0, 48000, 1) == ESP_ERR_INVALID_ARG, "empty input");
        check(native_audio_output_write(nullptr, 1, 48000, 1) == ESP_ERR_INVALID_ARG, "null input");
        check(native_audio_output_write(input, 1, 0, 1) == ESP_ERR_INVALID_ARG, "zero rate");
        s_i2s_started = false;
        check(native_audio_output_write(input, 2, 48000, 2) == ESP_ERR_INVALID_STATE, "not started");
        check(s_i2s_pdm_write == selected && reference.same(), "invalid call changes dispatch/state");
        s_i2s_started = true;
        native_audio_output_silence(); reference = Reference();
        check(reference.same() && s_resample_phase == 0 && s_input_sample_rate == 0, "silence reset");
        for (unsigned channels : {1U, 2U}) {
            native_audio_output_silence(); reference = Reference();
            s_volume = 254; s_balance = 0;
            input[0] = -32768; input[1] = 32767;
            fail_reserve = true;
            check(native_audio_output_write(input, channels, 48000, uint8_t(channels)) == ESP_ERR_TIMEOUT, "reserve error");
            reference.pack(channels == 1 ? int16_t(-32768) : int16_t(0));
            check(reference.same() && s_resample_phase == 48000, "reserve error state");
            fail_reserve = false;
            native_audio_output_silence(); reference = Reference();
            dma_capacity = 1; fail_commit = true;
            check(native_audio_output_write(input, channels, 48000, uint8_t(channels)) == ESP_ERR_TIMEOUT, "commit error");
            reference.pack(channels == 1 ? int16_t(-32768) : int16_t(0));
            check(reference.same() && s_resample_phase == 48000, "commit error state");
            fail_commit = false;
        }
#if CONFIG_YORADIO_STATUS_LED
        check(led_blocks >= blocks / 2 && led_clears > 0, "LED hooks not exercised");
#endif
        std::cout << "{\"pass\":true,\"blocks\":" << blocks << ",\"words\":" << words << "}\n";
    } catch (const std::exception &error) { std::cerr << error.what() << '\n'; return 1; }
}
