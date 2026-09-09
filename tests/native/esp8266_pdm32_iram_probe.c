#include <stdint.h>
#include <limits.h>
#if !defined(PDM32_TARGET_PROBE)
#include <assert.h>
#include <stdio.h>
#endif
/* The generated include is extracted verbatim from native_audio_output.c. */
#define IRAM_ATTR __attribute__((section(".iram1.pdm32")))
#define CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM 0
static uint32_t s_pdm_integrator;
#include "pdm32_under_test.inc"

#if defined(PDM32_TARGET_PROBE)
extern long long __moddi3(long long, long long);
volatile long long pdm32_probe_input;
volatile uint32_t pdm32_probe_output;
void call_start_cpu(void) {
    pdm32_probe_output = i2s_pdm_pack32((int16_t)pdm32_probe_input);
    pdm32_probe_output ^= (uint32_t)__moddi3(pdm32_probe_input, 1000000LL);
}
#else
static uint32_t reference(uint32_t *state, int16_t sample) {
    uint32_t word = 0, target = (uint32_t)((int32_t)sample - INT16_MIN);
    for (unsigned bit = 0; bit < 32; ++bit) {
        *state += target;
        unsigned high = *state >= 65536U;
        if (high) *state -= 65536U;
        word = (word << 1) | high;
    }
    return word;
}
static void compare(int16_t sample, uint32_t *expected) {
    assert(i2s_pdm_pack32(sample) == reference(expected, sample));
    assert(s_pdm_integrator == *expected);
}
int main(void) {
    const uint32_t seeds[] = {0, 1, 32767, 32768, 65534, 65535};
    unsigned cases = 0;
    for (unsigned i = 0; i < sizeof(seeds) / sizeof(seeds[0]); ++i)
        for (int32_t sample = INT16_MIN; sample <= INT16_MAX; ++sample) {
            uint32_t expected = s_pdm_integrator = seeds[i];
            compare((int16_t)sample, &expected); ++cases;
        }
    uint32_t expected = s_pdm_integrator = 0, random = 1;
    for (unsigned i = 0; i < 100000; ++i) {
        random = random * 1664525U + 1013904223U;
        compare((int16_t)(random >> 16), &expected); ++cases;
    }
    printf("{\"passed\":true,\"words\":%u,\"placement\":%u}\n", cases, YORADIO_ESP8266_PDM32_IRAM);
    return 0;
}
#endif
