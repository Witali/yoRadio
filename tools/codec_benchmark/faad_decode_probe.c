// Decode with a source-built FAAD configuration; retain PCM and per-frame shape.
#include "common.h"
#include "structs.h"
#include "neaacdec.h"
#include "packed_complex14.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#if !defined(FIXED_POINT) || !defined(SBR_DEC) || !defined(PS_DEC) || defined(SBR_LOW_POWER)
#error "Requires fixed-point full complex SBR/PS"
#endif

static void quantizer_check(void) {
#ifdef FAAD_PACKED_PS_HISTORY
    uint32_t rng = 0x14040301u;
    for (unsigned n = 0; n < 100000; ++n) {
        int32_t r, i, a, b, c, d;
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; memcpy(&r, &rng, 4);
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; memcpy(&i, &rng, 4);
        if (!n) { r = INT32_MIN; i = INT32_MAX; }
        uint32_t word = pcx_pack_complex(r, i);
        assert(word == pc14_pack(r, i, PC14_MIDPOINT, NULL));
        pcx_unpack_complex(word, &a, &b); pc14_unpack(word, PC14_MIDPOINT, &c, &d);
        assert(a == c && b == d);
    }
#endif
}

int main(int argc, char **argv) {
    assert(argc == 4); // input.aac, output-prefix, repeats
    unsigned repeats = strtoul(argv[3], NULL, 10); assert(repeats == 1 || repeats == 2);
    quantizer_check();
    FILE *input = fopen(argv[1], "rb"); assert(input);
    fseek(input, 0, SEEK_END); long length = ftell(input); rewind(input); assert(length > 0);
    unsigned char *bytes = calloc(1, length + 1024); assert(bytes);
    assert(fread(bytes, 1, length, input) == (size_t)length); fclose(input);
    char path[4096];
    assert(snprintf(path, sizeof(path), "%s.pcm", argv[2]) < sizeof(path));
    FILE *pcm_file = fopen(path, "wb"); assert(pcm_file);
    assert(snprintf(path, sizeof(path), "%s.frames", argv[2]) < sizeof(path));
    FILE *frames_file = fopen(path, "w"); assert(frames_file);
    // The runner requires little-endian signed 16-bit output on this host.
    unsigned endian = 1; assert(*(unsigned char *)&endian == 1);
    NeAACDecHandle decoder = NeAACDecOpen(); assert(decoder);
    NeAACDecConfigurationPtr cfg = NeAACDecGetCurrentConfiguration(decoder);
    cfg->defObjectType = LC; cfg->outputFormat = FAAD_FMT_16BIT;
    assert(NeAACDecSetConfiguration(decoder, cfg));
    unsigned long rate; unsigned char channels;
    long start = NeAACDecInit(decoder, bytes, length, &rate, &channels); assert(start >= 0);
    uint64_t samples = 0; unsigned frames = 0, ps_frames = 0, sbr_frames = 0, upsampled_core_frames = 0;
    for (unsigned pass = 0; pass < repeats; ++pass) for (long pos = start; pos + 7 <= length;) {
        assert(bytes[pos] == 0xff && (bytes[pos + 1] & 0xf6) == 0xf0);
        unsigned size = ((bytes[pos + 3] & 3) << 11) | (bytes[pos + 4] << 3) | (bytes[pos + 5] >> 5);
        assert(size >= 7 && pos + size <= length);
        NeAACDecFrameInfo info;
        int16_t *pcm = NeAACDecDecode(decoder, &info, bytes + pos, size);
        if (info.error) fprintf(stderr, "AAC error %u frame %u\n", info.error, frames);
        assert(pcm && !info.error && info.bytesconsumed == size);
        assert(info.channels == 1 || info.channels == 2);
        unsigned active_ps = ((NeAACDecStruct *)decoder)->ps_used_global != 0;
        fprintf(frames_file, "%u %lu %lu %u %u %u\n", size, info.samples,
                info.samplerate, info.channels, info.sbr, active_ps);
        assert(fwrite(pcm, sizeof(int16_t), info.samples, pcm_file) == info.samples);
        samples += info.samples; ++frames; ps_frames += active_ps;
        sbr_frames += info.sbr == SBR_UPSAMPLED || info.sbr == SBR_DOWNSAMPLED;
        upsampled_core_frames += info.sbr == NO_SBR_UPSAMPLED;
        pos += size;
    }
    fclose(pcm_file); fclose(frames_file);
    printf("{\"frames\":%u,\"samples\":%" PRIu64 ",\"ps_frames\":%u,\"sbr_frames\":%u,"
           "\"upsampled_core_frames\":%u,\"ps_info_bytes\":%zu,\"quantizer_equivalence_cases\":%u}\n",
           frames, samples, ps_frames, sbr_frames, upsampled_core_frames, sizeof(ps_info),
#ifdef FAAD_PACKED_PS_HISTORY
           100000u
#else
           0u
#endif
    );
    NeAACDecClose(decoder); free(bytes); return 0;
}
