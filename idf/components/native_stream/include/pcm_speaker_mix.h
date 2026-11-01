#pragma once

#include <math.h>
#include <stdbool.h>
#include <stdint.h>

// RFC7845 section5.1.1.5, figures4-9, in family1/Vorbis speaker order.
// Entries are the nearest binary64 values of the exact formula coefficients,
// rather than the six-digit display values. Mono/stereo rows are identities.
// This is a wide linear operator: it never rounds, clips or changes input PCM.
typedef struct {
    uint8_t channels;
    double left[8], right[8];
} pcm_speaker_mix;

typedef struct {
    uint8_t channels;
    double weight[8];
} pcm_speaker_mono;

static inline bool psm_begin(pcm_speaker_mix *mix, uint8_t channels)
{
    if (!mix || !channels || channels > 8) return false;
    static const double left[8][8] = {
        {1},
        {1, 0},
        {0.58578643762690497, 0.41421356237309503, 0},
        {0.42264973081037421, 0, 0.36602540378443865, 0.21132486540518711},
        {0.65080181379145008, 0.46018637574043919, 0,
         0.56361090357238564, 0.32540090689572504},
        {0.52906708224134369, 0.37410692155543496, 0,
         0.4581855335271145, 0.26453354112067184, 0.37410692155543496},
        {0.4553100233624493, 0.32195280506179325, 0,
         0.39431004682956733, 0.22765501168122465,
         0.27881930800317217, 0.32195280506179325},
        {0.38863141421212127, 0.27480390837150898, 0,
         0.33656467741636975, 0.19431570710606064,
         0.33656467741636975, 0.19431570710606064, 0.27480390837150898},
    };
    static const uint8_t mirror[8][8] = {
        {0}, {1, 0}, {2, 1, 0}, {1, 0, 3, 2},
        {2, 1, 0, 4, 3}, {2, 1, 0, 4, 3, 5},
        {2, 1, 0, 4, 3, 5, 6}, {2, 1, 0, 4, 3, 6, 5, 7},
    };
    pcm_speaker_mix next = {.channels = channels};
    for (uint8_t i = 0; i < channels; ++i) {
        next.left[i] = left[channels - 1][i];
        next.right[i] = left[channels - 1][mirror[channels - 1][i]];
    }
    *mix = next;
    return true;
}

// left/right are linear header * player/balance factors, already combined by
// the output owner. Prepare once per PCM packet. Refusal preserves the old mix.
static inline bool psm_scale(const pcm_speaker_mix *mix, double left,
                             double right, pcm_speaker_mono *mono)
{
    if (!mix || !mono || !mix->channels || mix->channels > 8 ||
        !isfinite(left) || !isfinite(right) || left < 0 || right < 0)
        return false;
    pcm_speaker_mono next = {.channels = mix->channels};
    double sum = 0;
    for (uint8_t i = 0; i < mix->channels; ++i) {
        double l = mix->left[i], r = mix->right[i];
        if (!isfinite(l) || !isfinite(r) || l < 0 || r < 0) return false;
        next.weight[i] = (left * 0.5) * l + (right * 0.5) * r;
        sum += next.weight[i];
    }
    if (!isfinite(sum * 32768.0)) return false;
    *mono = next;
    return true;
}

// Both arguments must have been validated/prepared by the owner. Keeping the
// sum wide preserves cancellation and headroom until its final S16 projection.
static inline double psm_value(const pcm_speaker_mono *mono,
                                const int16_t *channels)
{
    double result = 0, correction = 0;
    for (uint8_t i = 0; i < mono->channels; ++i) {
        double value = (double)channels[i] * mono->weight[i];
        double next = result + value;
        // Preserve addition residuals at cancellation and final-round ties.
        // Coefficients/products remain binary64; this is not exact-real DSP.
        correction += fabs(result) >= fabs(value)
            ? (result - next) + value : (value - next) + result;
        result = next;
    }
    return result + correction;
}
