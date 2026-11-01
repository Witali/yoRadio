#include <assert.h>
#include <float.h>
#include <stdio.h>
#include <string.h>
#include "pcm_speaker_mix.h"

int main(void)
{
    unsigned impulses = 0, controls = 0;
    for (uint8_t count = 1; count <= 8; ++count) {
        pcm_speaker_mix mix;
        memset(&mix, 0xa5, sizeof(mix));
        assert(psm_begin(&mix, count) && mix.channels == count);
        pcm_speaker_mono mono;
        assert(psm_scale(&mix, 1, 1, &mono));
        double left_sum = 0, right_sum = 0;
        int16_t samples[8] = {0}, before[8];
        for (uint8_t channel = 0; channel < count; ++channel) {
            left_sum += mix.left[channel];
            right_sum += mix.right[channel];
            assert(mix.left[channel] >= 0 && mix.right[channel] >= 0 &&
                   mix.left[channel] + mix.right[channel] > 0);
            samples[channel] = 32767;
            memcpy(before, samples, sizeof(before));
            double value = psm_value(&mono, samples);
            assert(value > 0 && !memcmp(samples, before, sizeof(before)));
            printf("{\"channels\":%u,\"index\":%u,\"left\":\"%a\",\"right\":\"%a\",\"impulse\":\"%a\"}\n",
                   count, channel, mix.left[channel], mix.right[channel], value);
            samples[channel] = 0;
            ++impulses;
        }
        double expected_sum = count <= 4 ? 1 : 2;
        assert(fabs(left_sum - expected_sum) <= 4 * DBL_EPSILON &&
               fabs(right_sum - expected_sum) <= 4 * DBL_EPSILON);
        for (uint8_t channel = count; channel < 8; ++channel)
            assert(mix.left[channel] == 0 && mix.right[channel] == 0 && mono.weight[channel] == 0);
        assert(psm_scale(&mix, 0, 0, &mono));
        memset(samples, 0x7f, sizeof(samples));
        assert(psm_value(&mono, samples) == 0);
        assert(psm_scale(&mix, 0.5, 0.5, &mono));
        double half = psm_value(&mono, samples);
        assert(psm_scale(&mix, 1, 1, &mono));
        assert(psm_value(&mono, samples) == 2 * half);
        assert(psm_scale(&mix, 1, 0, &mono));
        for (uint8_t channel = 0; channel < count; ++channel)
            assert(mono.weight[channel] == 0.5 * mix.left[channel]);
        assert(psm_scale(&mix, 0, 1, &mono));
        for (uint8_t channel = 0; channel < count; ++channel)
            assert(mono.weight[channel] == 0.5 * mix.right[channel]);
        assert(psm_scale(&mix, 256, 256, &mono));
        double wide = psm_value(&mono, samples);
        assert(wide > 32767);
        printf("{\"channels\":%u,\"wide\":\"%a\",\"headroom_preserved\":true}\n", count, wide);
        ++controls;
        for (uint8_t channel = 0; channel < count; ++channel) samples[channel] = INT16_MIN;
        assert(psm_value(&mono, samples) < -32768);
        controls += 3;
        pcm_speaker_mono old;
        memcpy(&old, &mono, sizeof(old));
        assert(!psm_scale(&mix, NAN, 1, &mono) && !memcmp(&old, &mono, sizeof(old)));
        assert(!psm_scale(&mix, 1, INFINITY, &mono) && !memcmp(&old, &mono, sizeof(old)));
        assert(!psm_scale(&mix, -1, 1, &mono) && !memcmp(&old, &mono, sizeof(old)));
        assert(!psm_scale(&mix, DBL_MAX, DBL_MAX, &mono) && !memcmp(&old, &mono, sizeof(old)));
        pcm_speaker_mix bad = mix;
        bad.left[0] = NAN;
        assert(!psm_scale(&bad, 1, 1, &mono) && !memcmp(&old, &mono, sizeof(old)));
        controls += 5;
        pcm_speaker_mix old_mix;
        memcpy(&old_mix, &mix, sizeof(mix));
        assert(!psm_begin(&mix, 0) && !memcmp(&old_mix, &mix, sizeof(mix)));
        assert(!psm_begin(&mix, 9) && !memcmp(&old_mix, &mix, sizeof(mix)));
        assert(!psm_begin(&mix, 255) && !memcmp(&old_mix, &mix, sizeof(mix)));
        controls += 3;
        if (count > 1) {
            memset(samples, 0, sizeof(samples));
            samples[0] = 30000;
            samples[count == 2 || count == 4 ? 1 : 2] = -30000;
            assert(psm_scale(&mix, 1, 1, &mono) && psm_value(&mono, samples) == 0);
            ++controls;
        }
    }
    assert(!psm_begin(NULL, 1) && !psm_scale(NULL, 1, 1, NULL));
    printf("{\"passed\":true,\"impulses\":%u,\"controls\":%u,\"production_selected\":false}\n", impulses, controls + 1);
    return 0;
}
