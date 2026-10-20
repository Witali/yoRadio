#define OUTPUT_PACKET_BYTES 3072
#define SAMPLE_GAIN_SCALE 32768U
#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define NORMALIZER_CHUNK_FRAMES 128U
#define LEGACY_OUTPUT_BYTES (OUTPUT_PACKET_BYTES * 2)
#define LEGACY_OVERSAMPLE_FACTOR 16U
#define LEGACY_DMA_DESCRIPTORS 8
#define LEGACY_DMA_FRAMES 512
#define LEGACY_MIN_INPUT_SAMPLE_RATE 8000U
#define LEGACY_MAX_INPUT_SAMPLE_RATE 48000U
static int16_t scale_sample_q15(int16_t sample, uint32_t gain_q15) {
    int32_t scaled = (int32_t)sample * (int32_t)gain_q15;
    if (scaled >= 0) {
        return (int16_t)((scaled + SAMPLE_GAIN_SCALE / 2U) /
                         SAMPLE_GAIN_SCALE);
    }
    return (int16_t)-(((-scaled) + SAMPLE_GAIN_SCALE / 2U) /
                      SAMPLE_GAIN_SCALE);
}

static uint32_t channel_gain_q15(uint8_t volume, uint8_t balance_gain) {
    const uint32_t denominator =
        VOLUME_DENOMINATOR * BALANCE_DENOMINATOR;
    uint32_t numerator = (uint32_t)volume * balance_gain;
    return (numerator * SAMPLE_GAIN_SCALE + denominator / 2U) / denominator;
}

typedef struct {
    uint32_t left;
    uint32_t right;
} pcm_gains_t;

static pcm_gains_t pcm_channel_gains(uint8_t channels, uint8_t volume,
                                    int8_t balance) {
    uint8_t left_balance =
        channels > 1 && balance < 0
            ? (uint8_t)((int)BALANCE_DENOMINATOR + balance)
            : BALANCE_DENOMINATOR;
    uint8_t right_balance =
        balance > 0 ? (uint8_t)(BALANCE_DENOMINATOR - balance)
                    : BALANCE_DENOMINATOR;
    return (pcm_gains_t){
        .left = channel_gain_q15(volume, left_balance),
        .right = channels > 1 ? channel_gain_q15(volume, right_balance) : 0,
    };
}

static int16_t pcm_mono_values(int16_t left, int16_t right, uint8_t channels,
                               const pcm_gains_t *gains) {
    if (channels < 2) {
        return scale_sample_q15(left, gains->left);
    }
    left = scale_sample_q15(left, gains->left);
    right = scale_sample_q15(right, gains->right);
    return (int16_t)(((int32_t)left + (int32_t)right) / 2);
}

static int16_t pcm_mono_sample(const uint8_t *frame, uint8_t channels,
                               const pcm_gains_t *gains) {
    int16_t left, right = 0;
    memcpy(&left, frame, sizeof(left));
    if (channels > 1) memcpy(&right, frame + sizeof(right), sizeof(right));
    return pcm_mono_values(left, right, channels, gains);
}

bool native_audio_output_supports_pcm(uint8_t bits_per_sample,
                                      uint8_t channels) {
    return channels && (bits_per_sample == 8 || bits_per_sample == 16 ||
                        bits_per_sample == 24 || bits_per_sample == 32);
}

static int16_t pcm_sample_to_s16(const uint8_t *sample, uint8_t sample_bytes) {
    if (sample_bytes == 1) {
        int32_t value = sample[0] < 128U ? sample[0] : (int32_t)sample[0] - 256;
        return (int16_t)(value * 256);
    }
    // Keep the signed high 16 bits, with no unaligned load or negative shift.
    // Discarding the low bytes gives the same floor conversion as signed PCM
    // arithmetic shifts, including the negative values nearest to zero.
    uint16_t high = (uint16_t)sample[sample_bytes - 2U] |
                    ((uint16_t)sample[sample_bytes - 1U] << 8);
    int32_t value = high <= INT16_MAX ? high : (int32_t)high - 65536;
    return (int16_t)value;
}

typedef struct {
    bool valid;
    bool enabled;
    uint8_t max_gain_db;
    int8_t target_dbfs;
    uint16_t time_ms;
    uint32_t sample_rate;
} normalizer_config_cache_t;

// Only the output owner touches the cache, DSP instance and scratch. Settings
// getters are atomic; the controller can only publish a pending reset request.
static normalizer_config_cache_t s_normalizer_config;
static atomic_bool s_normalizer_reset_pending;
static atomic_bool s_pause_requested;
static uint32_t s_pcm_sample_rate = 16000U;
static uint8_t s_pcm_channels;
static uint8_t s_pcm_bits;
static int16_t s_normalizer_scratch[NORMALIZER_CHUNK_FRAMES * 2U];

static void reset_pcm_normalizer(void) {
    native_audio_normalizer_reset();
    s_pcm_channels = 0;
    s_pcm_bits = 0;
}

static void pcm_normalizer_set_sample_rate(uint32_t sample_rate) {
    if (sample_rate != s_pcm_sample_rate) {
        s_pcm_sample_rate = sample_rate;
        reset_pcm_normalizer();
    }
}

static bool sync_normalizer_configuration(uint8_t channels, uint8_t bits) {
    normalizer_config_cache_t next = {
        .valid = true,
        .enabled = native_audio_settings_get_normalization(),
        .max_gain_db = native_audio_settings_get_normalization_gain_db(),
        .target_dbfs = native_audio_settings_get_normalization_target_dbfs(),
        .time_ms = native_audio_settings_get_normalization_time_ms(),
        .sample_rate = s_pcm_sample_rate,
    };
    if (!s_normalizer_config.valid ||
        next.enabled != s_normalizer_config.enabled ||
        next.max_gain_db != s_normalizer_config.max_gain_db ||
        next.target_dbfs != s_normalizer_config.target_dbfs ||
        next.time_ms != s_normalizer_config.time_ms ||
        next.sample_rate != s_normalizer_config.sample_rate) {
        native_audio_normalizer_configure(
            next.enabled, next.max_gain_db, next.target_dbfs, next.time_ms,
            next.sample_rate);
        s_normalizer_config = next;
    }
    bool requested = atomic_exchange(&s_normalizer_reset_pending, false);
    if (requested || s_pcm_channels != channels || s_pcm_bits != bits) {
        native_audio_normalizer_reset();
    }
    s_pcm_channels = channels;
    s_pcm_bits = bits;
    return next.enabled;
}

void native_audio_output_request_normalizer_reset(void) {
    atomic_store(&s_normalizer_reset_pending, true);
}

void native_audio_output_request_pause(bool requested) {
    atomic_store(&s_pause_requested, requested);
}

typedef struct {
    const uint8_t *data;
    size_t frame_bytes;
    size_t frames;
    size_t position;
    size_t buffered_frames;
    size_t buffered_index;
    pcm_gains_t gains;
    uint8_t channels;
    uint8_t sample_bytes;
    bool normalize;
} pcm_reader_t;

static pcm_reader_t pcm_reader_begin(const uint8_t *data, size_t frames,
                                      uint8_t bits, uint8_t channels) {
    return (pcm_reader_t){
        .data = data,
        .frame_bytes = (size_t)channels * (bits / 8U),
        .frames = frames,
        .gains = pcm_channel_gains(channels,
            native_audio_settings_get_volume(),
            native_audio_settings_get_balance()),
        .channels = channels,
        .sample_bytes = bits / 8U,
        .normalize = sync_normalizer_configuration(channels, bits),
    };
}

static int16_t pcm_reader_next(pcm_reader_t *reader) {
    if (!reader->normalize) {
        const uint8_t *frame =
            reader->data + reader->position++ * reader->frame_bytes;
        if (reader->sample_bytes == sizeof(int16_t)) {
            return pcm_mono_sample(frame, reader->channels, &reader->gains);
        }
        int16_t left = pcm_sample_to_s16(frame, reader->sample_bytes);
        int16_t right = reader->channels > 1
            ? pcm_sample_to_s16(frame + reader->sample_bytes, reader->sample_bytes)
            : 0;
        return pcm_mono_values(left, right, reader->channels, &reader->gains);
    }

    uint8_t normalized_channels = reader->channels > 1 ? 2 : 1;
    if (reader->buffered_index == reader->buffered_frames) {
        size_t chunk = reader->frames - reader->position;
        if (chunk > NORMALIZER_CHUNK_FRAMES) chunk = NORMALIZER_CHUNK_FRAMES;
        // Keep the decoder's PCM read-only and tolerate unaligned input.
        // CYD's mono mixer consumes the first two channels of wider layouts.
        for (size_t frame = 0; frame < chunk; ++frame) {
            const uint8_t *input = reader->data +
                (reader->position + frame) * reader->frame_bytes;
            if (reader->sample_bytes == sizeof(int16_t)) {
                memcpy(s_normalizer_scratch + frame * normalized_channels,
                       input, normalized_channels * sizeof(int16_t));
            } else {
                for (uint8_t channel = 0; channel < normalized_channels; ++channel)
                    s_normalizer_scratch[frame * normalized_channels + channel] =
                        pcm_sample_to_s16(input + channel * reader->sample_bytes,
                                          reader->sample_bytes);
            }
        }
        native_audio_normalizer_process_block(
            s_normalizer_scratch, chunk, normalized_channels);
        reader->buffered_frames = chunk;
        reader->buffered_index = 0;
    }
    const uint8_t *frame = (const uint8_t *)(s_normalizer_scratch +
        reader->buffered_index++ * normalized_channels);
    ++reader->position;
    return pcm_mono_sample(frame, normalized_channels, &reader->gains);
}

static uint32_t legacy_pack_dac_code(uint8_t code) {
    uint16_t slot = (uint16_t)code << 8;
    return ((uint32_t)slot << 16) | slot;
}

static uint8_t legacy_fractional_dac_step(int16_t pcm) {
    uint16_t value = (uint16_t)((int32_t)pcm + 32768);
    uint16_t base = value >> 8;
    if (base == UINT8_MAX) {
        // There is no code above 255. Avoid retaining an impossible positive
        // error while the signal is clipped at the upper DAC rail.
        s_legacy_fractional_error = 0;
        return UINT8_MAX;
    }

    s_legacy_fractional_error += value & UINT8_MAX;
    if (s_legacy_fractional_error >= 256U) {
        s_legacy_fractional_error -= 256U;
        ++base;
    }
    return (uint8_t)base;
}

static esp_err_t legacy_write_frames(size_t frames) {
    if (atomic_load(&s_pause_requested)) return ESP_ERR_INVALID_STATE;
    if (!frames) return ESP_OK;
    size_t written = 0;
    int64_t started = native_output_metrics_begin_write();
    esp_err_t result = idf6_dac_output_write(
        s_legacy_frames, frames * sizeof(uint32_t), &written,
        pdMS_TO_TICKS(1000));
    native_output_metrics_end_write(frames * sizeof(uint32_t), written, result, started);
    if (result != ESP_OK) return result;
    return written == frames * sizeof(uint32_t) ? ESP_OK : ESP_FAIL;
}

static esp_err_t legacy_write_silence(size_t frames) {
    size_t capacity = LEGACY_OUTPUT_BYTES / sizeof(uint32_t);
    for (size_t index = 0; index < capacity; ++index) {
        s_legacy_frames[index] = 0x80008000UL;
    }
    while (frames) {
        size_t chunk = frames > capacity ? capacity : frames;
        ESP_RETURN_ON_ERROR(legacy_write_frames(chunk), TAG,
                            "write legacy DAC silence");
        frames -= chunk;
    }
    return ESP_OK;
}
esp_err_t native_audio_output_configure(uint32_t input_sample_rate) {
    if (input_sample_rate < LEGACY_MIN_INPUT_SAMPLE_RATE ||
        input_sample_rate > LEGACY_MAX_INPUT_SAMPLE_RATE) {
        return ESP_ERR_INVALID_ARG;
    }
    uint32_t output_sample_rate =
        input_sample_rate * LEGACY_OVERSAMPLE_FACTOR;
    if (s_legacy_installed) {
        if (input_sample_rate == s_legacy_sample_rate) return ESP_OK;
        ESP_RETURN_ON_ERROR(idf6_dac_output_set_sample_rate(output_sample_rate),
                            TAG, "set legacy DAC clock");
        s_legacy_sample_rate = 0;
        s_legacy_output_sample_rate = output_sample_rate;
        s_legacy_fractional_error = 0;
        ESP_RETURN_ON_ERROR(
            legacy_write_silence(LEGACY_DMA_DESCRIPTORS * LEGACY_DMA_FRAMES),
            TAG, "prime resampled legacy DAC");
        s_legacy_sample_rate = input_sample_rate;
        ESP_LOGI(TAG, "Legacy DAC input %lu Hz, x%u output %lu Hz",
                 (unsigned long)input_sample_rate, LEGACY_OVERSAMPLE_FACTOR,
                 (unsigned long)output_sample_rate);
        pcm_normalizer_set_sample_rate(input_sample_rate);
        return ESP_OK;
    }

    i2s_config_t config = {
        .mode = I2S_MODE_MASTER | I2S_MODE_TX | I2S_MODE_DAC_BUILT_IN,
        .sample_rate = output_sample_rate,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_MSB,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = LEGACY_DMA_DESCRIPTORS,
        .dma_buf_len = LEGACY_DMA_FRAMES,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = I2S_PIN_NO_CHANGE,
    };
    ESP_RETURN_ON_ERROR(
        idf6_dac_output_configure(&config, I2S_DAC_CHANNEL_LEFT_EN), TAG,
        "configure legacy DAC adapter");
    ESP_RETURN_ON_ERROR(idf6_dac_output_begin(), TAG,
                        "start legacy DAC adapter");
    s_legacy_installed = true;
    s_legacy_sample_rate = 0;
    s_legacy_output_sample_rate = output_sample_rate;
    s_legacy_fractional_error = 0;
    ESP_RETURN_ON_ERROR(
        legacy_write_silence(LEGACY_DMA_DESCRIPTORS * LEGACY_DMA_FRAMES), TAG,
        "prime legacy DAC with midpoint");
    s_legacy_sample_rate = input_sample_rate;
    ESP_LOGI(TAG,
             "Legacy ESP-IDF 5.5 I2S/DAC: input %lu Hz, x%u output %lu Hz "
             "on GPIO26",
             (unsigned long)input_sample_rate, LEGACY_OVERSAMPLE_FACTOR,
             (unsigned long)output_sample_rate);
    pcm_normalizer_set_sample_rate(input_sample_rate);
    return ESP_OK;
}

esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels) {
    if (atomic_load(&s_pause_requested)) return ESP_ERR_INVALID_STATE;
    if (!data || !s_legacy_installed ||
        !native_audio_output_supports_pcm(bits_per_sample, channels)) {
        return ESP_ERR_NOT_SUPPORTED;
    }
    size_t frame_bytes = (size_t)channels * (bits_per_sample / 8U);
    size_t frames = size / frame_bytes;
    size_t capacity = LEGACY_OUTPUT_BYTES / sizeof(uint32_t);
    size_t buffered = 0;
    pcm_reader_t reader = pcm_reader_begin(data, frames, bits_per_sample, channels);
    for (size_t frame = 0; frame < frames; ++frame) {
        int16_t pcm = pcm_reader_next(&reader);
        for (uint32_t phase = 0; phase < LEGACY_OVERSAMPLE_FACTOR; ++phase) {
            uint8_t code = legacy_fractional_dac_step(pcm);
            s_legacy_frames[buffered++] = legacy_pack_dac_code(code);
            if (buffered == capacity) {
                ESP_RETURN_ON_ERROR(legacy_write_frames(buffered), TAG,
                                    "write oversampled legacy DAC");
                buffered = 0;
            }
        }
    }
    return legacy_write_frames(buffered);
}

void native_audio_output_discard_pcm(void) {
    s_legacy_fractional_error = 0;
    reset_pcm_normalizer();
}

esp_err_t native_audio_output_flush_pcm(void) {
    // Each legacy write submits its complete on-the-fly conversion.
    s_legacy_fractional_error = 0;
    reset_pcm_normalizer();
    return ESP_OK;
}
