#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
#include <algorithm>
#include "nodac_buffer_state.h"
#include "AudioNormalizer.h"
#include "rc_pdm.h"
#include "persistent_settings.h"
#if defined(_MSC_VER)
#define __attribute__(x)
#endif

using TickType_t = uint32_t;
using TaskHandle_t = void *;
using esp_err_t = int;
enum { ESP_OK = 0, ESP_ERR_INVALID_ARG = 1, ESP_ERR_INVALID_STATE = 2, ESP_ERR_TIMEOUT = 3 };
#define pdTRUE true
#define pdMS_TO_TICKS(ms) (ms)
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define NODAC_DMA_BUFFER_WORDS 512U
#define NODAC_DMA_BUFFER_BYTES (NODAC_DMA_BUFFER_WORDS * sizeof(uint32_t))
#define ESP8266_NODAC_DMA_BUFFER_WORDS 512U
#define ESP8266_NODAC_DMA_BUFFER_COUNT 2U
static uint32_t s_buffers[2][512];
#include "descriptor.inc"
static nodac_dma_descriptor_t s_descriptors[2];
static nodac_buffer_state_t s_state;
static uint32_t *s_current_buffer;
static size_t s_current_position, s_reserved_words;
static TaskHandle_t s_waiter;
static bool s_waiting;
static bool s_running;
static uint32_t s_silence_word = 0xaaaaaaaaU;
static unsigned critical, waits;
static TickType_t ticks;
static bool autoEof = true;
static std::vector<uint32_t> committed;
static std::vector<uint32_t> transmitted;
#include "prefix.inc"

static void eof() {
    assert(critical == 0);
    const unsigned old = s_state.active;
    if (!s_state.silent) transmitted.insert(transmitted.end(), s_buffers[old],
        s_buffers[old] + s_descriptors[old].datalen / sizeof(uint32_t));
    publish_committed_prefix();
    if(nodac_state_eof(&s_state))
        std::fill(s_buffers[old], s_buffers[old] + 512, s_silence_word);
    if(s_state.silent) s_descriptors[s_state.active].control = s_running ? 0xc0100100U : 0xc0800800U;
    assert(s_state.state[s_state.active] == NODAC_DMA);
}
#define taskENTER_CRITICAL() (++critical)
#define taskEXIT_CRITICAL() do { assert(critical == 1); --critical; } while(0)
static TickType_t xTaskGetTickCount() { return ticks; }
static TaskHandle_t xTaskGetCurrentTaskHandle() { return reinterpret_cast<void *>(1); }
static uint32_t ulTaskNotifyTake(bool, TickType_t delay) {
    assert(critical == 0);
    ++waits;
    if(autoEof) { ++ticks; eof(); return 1; }
    ticks += delay;
    return 0;
}

#define esp8266_nodac_i2s_commit driver_commit
#include "producer.inc"
#undef esp8266_nodac_i2s_commit
static esp_err_t esp8266_nodac_i2s_commit(size_t count) {
    uint32_t *begin = s_current_buffer ? s_current_buffer + s_current_position : nullptr;
    const int result = driver_commit(count);
    if(result == ESP_OK && count) committed.insert(committed.end(), begin, begin + count);
    return result;
}
static esp_err_t esp8266_nodac_i2s_init(uint32_t silence, uint8_t, uint8_t) {
    nodac_state_init(&s_state);
    s_current_buffer = nullptr;
    s_current_position = s_reserved_words = 0;
    s_waiting = false;
    s_running = false;
    ticks = waits = critical = 0;
    autoEof = true;
    s_silence_word = silence;
    std::fill(&s_buffers[0][0], &s_buffers[0][0] + 512, silence);
    std::fill(&s_buffers[1][0], &s_buffers[1][0] + 512, silence);
    committed.clear();
    transmitted.clear();
    s_descriptors[0].control = s_descriptors[1].control = 0xc0800800U;
    return ESP_OK;
}

#if TEST_RCPDM
#define CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM 1
#endif
#if !TEST_PDM128
#define CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32 1
#define BOARD_I2S_PDM_OVERSAMPLE 32U
#else
#define BOARD_I2S_PDM_OVERSAMPLE 128U
#endif
#define BOARD_I2S_PDM_REPEAT 1U
#define BOARD_I2S_PDM_SAMPLE_RATE 48000U
#define BOARD_I2S_PDM_BCK_DIV 8U
#define BOARD_I2S_PDM_CLKM_DIV 13U
#define BOARD_I2S_DATA_GPIO 3
#include "gain_config.inc"
static uint32_t s_input_sample_rate, s_resample_phase, s_pdm_integrator;
static rc_pdm_t s_rcpdm;
static uint32_t s_i2s_pdm_partial_word;
static uint8_t s_i2s_pdm_partial_bits;
static bool s_i2s_started;
static uint8_t s_volume = 193;
static int8_t s_balance = -3;
static bool s_normalization_enabled;
static uint8_t s_normalization_max_gain_db = 12;
static int8_t s_normalization_target_db = -3;
static uint16_t s_normalization_time_ms = 5000;
static AudioNormalizer normalizer;
static persistent_settings_t storedSettings;
void persistent_settings_get(persistent_settings_t *out) { *out = storedSettings; }
void native_audio_output_reload_settings(void);
static void native_audio_normalizer_configure(bool enable, uint8_t boost, int8_t target, uint16_t ms, uint32_t rate) {
    normalizer.configure(enable, boost, target, ms, rate);
}
static void native_audio_normalizer_process(int16_t *pcm, size_t frames, uint8_t channels) {
    normalizer.processBlock(pcm, frames, channels);
}
static void native_audio_normalizer_reset() { normalizer.reset(); }
#include "output.inc"
#include "settings.inc"

static void balance_regression() {
    for(int value = -128; value <= 127; ++value) {
        const int expected = std::max(-16, std::min(16, value));
        storedSettings.balance = static_cast<int8_t>(value);
        native_audio_output_reload_settings();
        assert(s_balance == expected);
        s_balance = 99;
        native_audio_output_set_balance_runtime(static_cast<int8_t>(value));
        assert(s_balance == expected);
    }
}

static void ownership() {
    esp8266_nodac_i2s_init(0xaaaaaaaaU, 8, 13);
    uint32_t *words;
    size_t capacity;
    assert(driver_commit(0) == ESP_ERR_INVALID_STATE);
    assert(esp8266_nodac_i2s_reserve(nullptr, &capacity, 0) == ESP_ERR_INVALID_ARG);
    assert(esp8266_nodac_i2s_reserve(&words, &capacity, 0) == ESP_OK && capacity == 512);
    uint32_t *second;
    size_t secondCapacity;
    assert(esp8266_nodac_i2s_reserve(&second, &secondCapacity, 0) == ESP_ERR_INVALID_STATE);
    assert(second == nullptr && secondCapacity == 0);
    assert(esp8266_nodac_i2s_write(words, 1, 0) == ESP_ERR_INVALID_STATE);
    assert(driver_commit(513) == ESP_ERR_INVALID_ARG);
    // Interrupt after EVERY word, even after the final store but before commit.
    for(unsigned i = 0; i < 512; ++i) {
        words[i] = i;
        eof();
        assert(s_state.active == 0 && s_state.state[1] == NODAC_FILLING);
        assert(words[i] == i);
    }
    assert(driver_commit(32) == ESP_OK);
    assert(esp8266_nodac_i2s_reserve(&words, &capacity, 0) == ESP_OK && capacity == 480);
    assert(driver_commit(0) == ESP_OK); // cancel, keep already committed prefix
    assert(esp8266_nodac_i2s_reserve(&words, &capacity, 0) == ESP_OK && capacity == 480);
    assert(driver_commit(480) == ESP_OK && s_state.state[1] == NODAC_READY);
    autoEof = false;
    assert(esp8266_nodac_i2s_reserve(&words, &capacity, 7) == ESP_ERR_TIMEOUT);
    assert(words == nullptr && capacity == 0 && !s_waiting && ticks == 7);
    autoEof = true;
    eof();
    assert(s_state.active == 1);
    for(unsigned i = 0; i < 512; ++i) assert(s_buffers[1][i] == i);
    assert(esp8266_nodac_i2s_reserve(&words, &capacity, 0) == ESP_OK);
    words[0] = 99;
    assert(driver_commit(1) == ESP_OK);
    esp8266_nodac_i2s_silence(0xaaaaaaaaU);
    assert(s_current_buffer == nullptr && s_reserved_words == 0);
    assert(s_buffers[1][0] == 0); // active DMA not overwritten by stop
    eof();
    for(uint32_t word : s_buffers[1]) assert(word == 0xaaaaaaaaU);
    // Legacy copying API shares the same ownership / partial-buffer rules.
    std::vector<uint32_t> input(1300);
    for(unsigned i = 0; i < input.size(); ++i) input[i] = 4000 + i;
    assert(esp8266_nodac_i2s_write(input.data(), input.size(), 100) == ESP_OK);
    assert(s_current_position == 276 && s_reserved_words == 0);
    for(unsigned i = 0; i < 276; ++i) assert(s_current_buffer[i] == 5024 + i);
    assert(critical == 0);
}

struct Render { std::vector<int16_t> pcm; std::vector<uint32_t> pdm; };
static void prefix_handoff() {
    esp8266_nodac_i2s_init(0xaaaaaaaaU, 8, 13);
    uint32_t *loan;
    size_t capacity;
    assert(esp8266_nodac_i2s_reserve(&loan, &capacity, 10) == ESP_OK);
    for(unsigned i = 0; i < 32; ++i) {
        loan[i] = 1000 + i;
        eof(); // A loan must NEVER be consumed while the CPU holds it.
        assert(s_state.active == 0 && s_current_buffer == loan);
    }
    assert(driver_commit(32) == ESP_OK);
    eof();
    assert(s_state.active == 1 && !s_state.silent && s_current_buffer == nullptr);
    assert(s_descriptors[1].datalen == 128);
    assert(esp8266_nodac_i2s_reserve(&loan, &capacity, 10) == ESP_OK);
    assert(capacity == 512 && loan == s_buffers[0]);
    for(unsigned i = 0; i < 512; ++i) loan[i] = 2000 + i;
    assert(driver_commit(512) == ESP_OK);
    eof();
    assert(transmitted.size() == 32 && s_state.active == 0);
    for(unsigned i = 0; i < 32; ++i) assert(transmitted[i] == 1000 + i);
    assert(s_descriptors[0].datalen == 2048);
    eof();
    assert(transmitted.size() == 544 && s_state.silent);
    for(unsigned i = 0; i < 512; ++i) assert(transmitted[32 + i] == 2000 + i);
    assert(s_descriptors[0].datalen == 256); // short neutral retry while playing
    esp8266_nodac_i2s_silence(0xaaaaaaaaU);
    eof();
    assert(s_descriptors[s_state.active].datalen == 2048); // idle cadence

    // Random EOFs before/inside/after loans: compare actual DMA sequence,
    // excluding deliberate neutral underrun intervals, with input words.
    esp8266_nodac_i2s_init(0xaaaaaaaaU, 8, 13);
    std::vector<uint32_t> expected;
    uint32_t random = 0x8266;
    for(unsigned block = 0; block < 1000; ++block) {
        assert(esp8266_nodac_i2s_reserve(&loan, &capacity, 100) == ESP_OK);
        random = random * 1664525U + 1013904223U;
        const size_t count = std::min(capacity, size_t(1 + random % 280));
        for(size_t i = 0; i < count; ++i) {
            const uint32_t word = uint32_t(expected.size() + 1);
            loan[i] = word;
            expected.push_back(word);
            if(i % 23 == 0) eof();
        }
        assert(driver_commit(count) == ESP_OK);
        if(block % 3) eof();
    }
    eof(); eof(); eof(); // drain final committed prefix and active payload
    assert(transmitted == expected);
}

static Render render(unsigned rate, uint8_t channels, bool normalize, unsigned chunk) {
    normalizer = AudioNormalizer();
    storedSettings.volume = 193;
    storedSettings.balance = -3;
    storedSettings.normalization_enabled = normalize;
    storedSettings.normalization_max_gain_db = 12;
    storedSettings.normalization_target_db = -3;
    storedSettings.normalization_time_ms = 5000;
    assert(native_audio_output_init() == ESP_OK);
    Render out;
    const unsigned frames = 4099; // non-divisible tail exercises partial blocks
    out.pcm.resize(frames * channels);
    uint32_t rng = 8266;
    for(auto &sample : out.pcm) { rng = rng * 1664525U + 1013904223U; sample = static_cast<int16_t>(rng >> 16); }
    for(unsigned start = 0; start < frames; start += chunk) {
        const unsigned count = std::min(chunk, frames - start);
        assert(native_audio_output_write(out.pcm.data() + start * channels,
            count * channels, rate, channels) == ESP_OK);
        assert(s_reserved_words == 0 && critical == 0);
        if(start % 3 == 0) eof(); // independent interrupt schedule
    }
    out.pdm = committed;
    assert(out.pdm.size() == static_cast<size_t>(frames) * 48000U / rate * (BOARD_I2S_PDM_OVERSAMPLE / 32U));
    native_audio_output_silence();
    assert(s_reserved_words == 0 && s_current_buffer == nullptr);
    return out;
}

int main() {
    balance_regression();
    prefix_handoff();
    std::vector<uint32_t> monoReference;
    for(int balance : {0, -16, 16}) {
        storedSettings = {};
        storedSettings.volume = 254;
        storedSettings.balance = static_cast<int8_t>(balance);
        normalizer = AudioNormalizer();
        assert(native_audio_output_init() == ESP_OK);
        assert(s_balance == balance);
        native_audio_output_set_balance_runtime(static_cast<int8_t>(balance));
        int16_t pcm[32];
        for(int i = 0; i < 32; ++i) pcm[i] = (i & 1) ? -1234 : 2345;
        assert(native_audio_output_write(pcm, 32, 48000, 1) == ESP_OK);
        assert(pcm[0] == 2345 && pcm[1] == -1234);
        if(balance == 0) monoReference = committed;
        else assert(committed == monoReference);
        assert(std::any_of(committed.begin(), committed.end(), [](uint32_t w){return w != 0xaaaaaaaaU;}));
    }
    ownership();
    for(unsigned rate : {8000U, 16000U, 22050U, 32000U, 44100U, 48000U})
        for(uint8_t channels : {1, 2}) for(bool normalize : {false, true}) {
            const Render baseline = render(rate, channels, normalize, 576);
            for(unsigned chunk : {1U, 32U, 64U, 128U}) {
                const Render actual = render(rate, channels, normalize, chunk);
                assert(actual.pcm == baseline.pcm);
                assert(actual.pdm == baseline.pdm);
            }
        }
    assert(native_audio_output_init() == ESP_OK);
    autoEof = false;
    std::vector<int16_t> tooMuch(1100);
    assert(native_audio_output_write(tooMuch.data(), tooMuch.size(), 48000, 1) == ESP_ERR_TIMEOUT);
    assert(s_reserved_words == 0 && critical == 0); // no leaked writable span
    puts("PCM/PDM bit-exact at 6 rates, mono/stereo, normalization on/off, 1/32/64/128/576 frames; ownership, EOF, timeout, cancel and stop passed");
}
