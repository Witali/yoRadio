# Opt-in standard PDM32 DMA-span fill

YORADIO_ESP8266_PDM32_BATCH is OFF by default. The production builder exposes
it as -Pdm32Batch with -Diagnostic; it is independent of -Pdm32Iram and the
Opus options. CMake rejects it unless standard I2S PDM with genuine 32-bit
oversampling is selected.

At 48 kHz and resampler phase zero, the audio task reserves the existing DMA
span and writes one i2s_pdm_pack32() word per mono PCM frame directly into it.
Stereo downmix retains signed division by two. This removes per-sample
push/phase-loop overhead, not the modulator or its integrator updates.

- PCM normalization, gain, balance and LED capture remain before conversion.
- No new static/heap allocation or stack buffer is added; the existing
  two 512-word DMA buffers and reservation lifetime are unchanged.
- Other sample rates and nonzero phase use the unchanged scalar path.
- RC-PDM and its existing batch path are unchanged.
- A failed reserve advances one packed sample and retains pending phase,
  matching scalar emit ordering. A failed full commit retains pending phase;
  a failed final partial commit does not. Flush cancels the failed DMA loan.

Run this host suite (one command line):

    node --test tests/esp8266-output-channel-dispatch.test.js tests/esp8266-pdm32-batch.test.js tests/esp8266-pdm32-batch-profile.test.js

The actual output source is compared with an independent scalar reference
for both batch settings and LED settings, including PCM, PDM words,
integrator/resampler state, commit lengths and DMA canaries. The failure
matrix covers mono/stereo, 8/12/16/22.05/24/32/44.1/48/96 kHz, five DMA
capacities, first/later reserve and commit failures, phase carry, and a
following call without reset. PDM variants run under ASan/UBSan.

Host bit-exactness does not establish a physical CPU improvement or qualify
continuous playback. Keep the option experimental until target A/B results
show a benefit.
