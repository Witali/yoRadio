// Included only by the isolated Vorbis test image. Version-2 commands retain
// complete PCM and exercise the same resize helper used by the radio service.
static bool reject_pcm_allocation;
static void *output_realloc(void *old, size_t bytes) {
    return reject_pcm_allocation ? NULL : realloc(old, bytes);
}
#define realloc output_realloc
#include "decoder_pcm.h"
#undef realloc

static void record_pcm(psa_hash_operation_t *hash, uint32_t *bytes,
                       const uint8_t *data, size_t count) {
    assert(psa_hash_update(hash, data, count) == PSA_SUCCESS);
    if (run_id == 1) {
        char hex[257];
        const char digits[] = "0123456789abcdef";
        for (size_t pos = 0; pos < count; pos += 128) {
            size_t n = count - pos;
            if (n > 128) n = 128;
            for (size_t i = 0; i < n; ++i) {
                hex[2*i] = digits[data[pos+i] >> 4];
                hex[2*i+1] = digits[data[pos+i] & 15];
            }
            hex[n*2] = 0;
            esp_rom_printf("VPCM run=%u offset=%u data=%s\n", run_id,
                           (unsigned)(*bytes + pos), hex);
        }
    }
    *bytes += count;
}

static int decode_output(psa_hash_operation_t *hash, uint32_t *pcm_bytes) {
    output_command_t options = output_command;
    if (run_id > 1) options = (output_command_t){PCM_BYTES, 0, 4, 0, 0, INPUT_BYTES};
    phase = PH_OPEN;
    esp_audio_simple_dec_handle_t decoder = NULL;
    esp_audio_simple_dec_cfg_t cfg = {.dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_OGG};
    uint8_t *workspace = NULL;
    size_t capacity = 0, offered = options.initial_bytes;
    reject_pcm_allocation = false;
    assert(decoder_pcm_resize(&workspace, &capacity, offered));
    int result = esp_audio_simple_dec_open(&cfg, &decoder);
    unsigned calls = 0, retries = 0, eos_index = 0, rejections = options.rejected_retries;
    unsigned allocation_failed = 0, synthesis_before = synthesis_calls;
    if (result) goto closed;
    for (size_t position = 0;;) {
        size_t size = command.ogg_bytes - position;
        if (size > options.input_bytes) size = options.input_bytes;
        memcpy(input, fixture + position, size);
        bool eos = !size;
        esp_audio_simple_dec_raw_t raw = {.buffer = input, .len = size, .eos = eos};
        do {
            phase = PH_DECODE;
            esp_audio_simple_dec_out_t out = {.buffer = workspace, .len = offered};
            raw.consumed = 0;
            result = esp_audio_simple_dec_process(decoder, &raw, &out);
            ++calls;
            assert(calls <= MAX_DECODE_CALLS && out.decoded_size <= offered && raw.consumed <= raw.len);
            if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                ++retries;
                esp_rom_printf("VOUTPUT_RETRY run=%u call=%u needed=%u offered=%u consumed=%u pcm=%u synthesis=%u\n",
                    run_id, calls, out.needed_size, (unsigned)offered, raw.consumed,
                    out.decoded_size, synthesis_calls - synthesis_before);
                // Log unsafe consumption without feeding bytes twice; the
                // simple-decoder API must retain its input until retry succeeds.
                if (raw.consumed || out.decoded_size) { result = -101; goto closed; }
                assert(out.needed_size > offered && out.needed_size <= PCM_BYTES);
                size_t required = rejections ? out.needed_size - 1 : out.needed_size;
                if (rejections) --rejections;
                reject_pcm_allocation = options.resize_oom;
                uint8_t *old = workspace;
                size_t old_capacity = capacity;
                if (!decoder_pcm_resize(&workspace, &capacity, required)) {
                    assert(workspace == old && capacity == old_capacity);
                    allocation_failed = 1;
                    reject_pcm_allocation = false;
                    result = ESP_AUDIO_ERR_MEM_LACK;
                    goto closed;
                }
                offered = required;
                continue;
            }
            if (result) goto closed;
            if (out.decoded_size) record_pcm(hash, pcm_bytes, workspace, out.decoded_size);
            if (eos) esp_rom_printf("VOUTPUT_EOS run=%u index=%u pcm=%u consumed=%u result=%d\n",
                                   run_id, eos_index, out.decoded_size, raw.consumed, result);
            if (!raw.consumed && !out.decoded_size && !eos) { result = -100; goto closed; }
            raw.buffer += raw.consumed;
            raw.len -= raw.consumed;
            if (options.each_packet) offered = options.initial_bytes;
            rejections = options.rejected_retries;
            if ((calls & 31U) == 0) vTaskDelay(1);
            if (eos ? !out.decoded_size : !raw.len) break;
        } while (true);
        if (eos && ++eos_index == options.eos_calls) break;
        position += size;
    }
closed:
    phase = PH_CLOSE;
    if (decoder) esp_audio_simple_dec_close(decoder);
    free(workspace);
    esp_rom_printf("VOUTPUT_RESULT run=%u result=%d calls=%u retries=%u eos=%u resize_oom=%u synthesis=%u\n",
                   run_id, result, calls, retries, eos_index, allocation_failed,
                   synthesis_calls - synthesis_before);
    return result;
}

// Independent packet feed bypasses the Ogg/simple parser. It uses the same
// original synthesis and PCM conversion, with an ample output buffer.
static int decode_output_raw(psa_hash_operation_t *hash, uint32_t *pcm_bytes) {
    esp_vorbis_dec_cfg_t cfg = {.info_header=(uint8_t *)info_header, .info_size=command.info_bytes,
                              .setup_header=(uint8_t *)setup_header, .setup_size=command.setup_bytes};
    void *decoder = NULL;
    phase = PH_OPEN;
    unsigned before = synthesis_calls, calls = 0;
    int result = esp_vorbis_dec_open(&cfg, sizeof(cfg), &decoder);
    for (size_t position = 0; !result && position < command.ogg_bytes;) {
        assert(command.ogg_bytes - position >= sizeof(uint32_t));
        uint32_t size;
        memcpy(&size, fixture+position, sizeof(size)); position += sizeof(size);
        assert(size && size <= command.ogg_bytes-position);
        esp_audio_dec_in_raw_t raw = {.buffer=(uint8_t *)(fixture+position), .len=size};
        esp_audio_dec_out_frame_t out = {.buffer=pcm, .len=sizeof(pcm)};
        esp_audio_dec_info_t info = {0};
        phase = PH_DECODE;
        result = esp_vorbis_dec_decode(decoder, &raw, &out, &info);
        ++calls;
        if (result) break;
        assert(raw.consumed==size && out.decoded_size<=sizeof(pcm));
        if (out.decoded_size) record_pcm(hash, pcm_bytes, pcm, out.decoded_size);
        position += size;
        if ((calls & 31U)==0) vTaskDelay(1);
    }
    phase = PH_CLOSE;
    esp_vorbis_dec_close(decoder);
    esp_rom_printf("VOUTPUT_RESULT run=%u result=%d calls=%u retries=0 eos=0 resize_oom=0 synthesis=%u\n",
                   run_id, result, calls, synthesis_calls-before);
    return result;
}
