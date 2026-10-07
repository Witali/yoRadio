// Decode pristine FAAD in float32 or fixed-point mode to signed 16-bit PCM.
// No history compression, resampling, gain matching or decoder modifications.
#include "common.h"
#include "structs.h"
#include "neaacdec.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#if !defined(SBR_DEC) || !defined(PS_DEC) || defined(SBR_LOW_POWER)
#error "Requires full complex SBR/PS"
#endif
#if defined(USE_DOUBLE_PRECISION) || defined(FAAD_PACKED_PS_HISTORY)
#error "Requires uncompressed float32 or fixed-point arithmetic"
#endif

int main(int argc, char **argv) {
    assert(argc == 4); // input.aac, output-prefix, continuous passes
    unsigned repeats = strtoul(argv[3], NULL, 10);
    assert(repeats == 1 || repeats == 2);
    assert(sizeof(real_t) == 4);
    FILE *input = fopen(argv[1], "rb"); assert(input);
    assert(!fseek(input, 0, SEEK_END));
    long length = ftell(input); rewind(input); assert(length > 0);
    unsigned char *bytes = calloc(1, length + 1024); assert(bytes);
    assert(fread(bytes, 1, length, input) == (size_t)length); fclose(input);
    char path[4096];
    assert(snprintf(path, sizeof(path), "%s.pcm", argv[2]) < sizeof(path));
    FILE *pcm_file = fopen(path, "wb"); assert(pcm_file);
    assert(snprintf(path, sizeof(path), "%s.frames", argv[2]) < sizeof(path));
    FILE *frames_file = fopen(path, "w"); assert(frames_file);
    assert(snprintf(path, sizeof(path), "%s.state", argv[2]) < sizeof(path));
    FILE *state_file = fopen(path, "w"); assert(state_file);
    unsigned endian = 1; assert(*(unsigned char *)&endian == 1);
    NeAACDecHandle decoder = NeAACDecOpen(); assert(decoder);
    NeAACDecConfigurationPtr cfg = NeAACDecGetCurrentConfiguration(decoder);
    // LC is the fallback object type; actual ADTS object type comes from input.
    cfg->defObjectType = LC; cfg->outputFormat = FAAD_FMT_16BIT;
    assert(NeAACDecSetConfiguration(decoder, cfg));
    unsigned long rate; unsigned char channels;
    long start = NeAACDecInit(decoder, bytes, length, &rate, &channels);
    assert(start >= 0 && start < length);
    uint64_t samples = 0;
    unsigned frames = 0, ps_frames = 0, sbr_frames = 0, upsampled_core_frames = 0;
    for (unsigned pass = 0; pass < repeats; ++pass) {
        long pos = start;
        while (pos + 7 <= length) {
            assert(bytes[pos] == 0xff && (bytes[pos + 1] & 0xf6) == 0xf0);
            unsigned size = ((bytes[pos + 3] & 3) << 11) |
                            (bytes[pos + 4] << 3) | (bytes[pos + 5] >> 5);
            assert(size >= 7 && pos + size <= length);
            NeAACDecFrameInfo info;
            int16_t *pcm = NeAACDecDecode(decoder, &info, bytes + pos, size);
            if (info.error) fprintf(stderr, "AAC error %u frame %u\n", info.error, frames);
            assert(pcm && !info.error && info.bytesconsumed == size);
            assert(info.channels == 1 || info.channels == 2);
            unsigned active_ps = ((NeAACDecStruct *)decoder)->ps_used_global != 0;
            // Passive diagnostics: public output rate alone cannot prove SBR
            // processing succeeded. These fixtures have at most one SBR element.
            NeAACDecStruct *state = decoder;
            for (unsigned e = 1; e < MAX_SYNTAX_ELEMENTS; ++e) assert(!state->sbr[e]);
            sbr_info *sbr = state->sbr[0];
            fprintf(state_file, "%d %d %d %d\n", sbr ? sbr->ret : -1,
                    sbr ? sbr->header_count : -1, sbr ? sbr->kx : -1, sbr ? sbr->M : -1);
            fprintf(frames_file, "%u %lu %lu %u %u %u\n", size, info.samples,
                    info.samplerate, info.channels, info.sbr, active_ps);
            assert(fwrite(pcm, sizeof(int16_t), info.samples, pcm_file) == info.samples);
            samples += info.samples; ++frames; ps_frames += active_ps;
            sbr_frames += info.sbr == SBR_UPSAMPLED || info.sbr == SBR_DOWNSAMPLED;
            upsampled_core_frames += info.sbr == NO_SBR_UPSAMPLED;
            pos += size;
        }
        assert(pos == length);
    }
    assert(!fclose(pcm_file)); assert(!fclose(frames_file));
    assert(!fclose(state_file));
    printf("{\"arithmetic\":\"%s\",\"real_bytes\":%zu,\"frames\":%u,\"samples\":%" PRIu64
           ",\"ps_frames\":%u,\"sbr_frames\":%u,\"upsampled_core_frames\":%u}\n",
#ifdef FIXED_POINT
           "fixed",
#else
           "float32",
#endif
           sizeof(real_t), frames, samples, ps_frames, sbr_frames, upsampled_core_frames);
    NeAACDecClose(decoder); free(bytes); return 0;
}
