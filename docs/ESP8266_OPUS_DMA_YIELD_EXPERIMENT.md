# Opus: avoid duplicate task delay after DMA wait

2026-09-10. Diagnostic A/B, OFF by default. Continuous Opus radio remains an
open goal. This is not a change to decoding, PCM, PDM, buffers or ISR priority.

- [x] Confirm baseline: the stream loop delays one RTOS tick after each
  successful process-one call, even when its PCM callback already waited on DMA.
- [x] Track ticks spent inside a successful DMA notification wait, in the
  producer task only. A same-tick/stale notification or timeout earns no credit.
- [x] Compare the cumulative count immediately before/after process-one.
  Only Opus may omit the extra delay; MP3/AAC retain the old scheduling.
  Headers and packets without a measured DMA wait retain the delay as well.
- [x] Add host tests for the actual acquire function, no-wait/stale/timeout,
  tick and cumulative-counter wrap, and no reuse of an earlier frame's credit.
- [ ] Build and compare the ISR and IRAM layout against the existing image.
- [ ] OTA and measure at least two steady 25-second intervals with the same
  own SILK12 fixture and sparse health polling. Preserve timeout/reconnect runs.
- [ ] Check a second Opus mode, WebUI/Stop/Play, and unchanged PCM/PDM regressions.
- [ ] Keep only demonstrated improvements; do not make a production default
  from one uncontrolled network run or relabel a failed continuity test.

Build option: `build_i2s_pdm_production.ps1 -OpusDmaYield`, with `-EnableOpus
-Diagnostic`, normal I2S PDM output. `opus_dma_yield` is recorded in the manifest;
the builder explicitly sets ON/OFF to avoid a stale CMake cache.

The experiment adds 12 bytes of persistent counters, no task or audio buffer.
The read-only audio health endpoint includes `frame_yields` and
`frame_yield_skips`; counters are cumulative since boot. All fields disappear
when the flag is OFF. A tick elapsed during the wait is conservative evidence
of scheduler time, not a measurement of how much time specifically ran idle.
The SDK uses 1000-Hz ticks. No frame delay is skipped purely because decoding
was slow or because the input remained full.

Baseline: `firmware/development/esp8266-opus-batch-resume/`, ICDF OFF,
WordASM/PDM IRAM/PDM batch ON, 160 MHz/QIO40, DMA 2 x 512 words, 48-kHz PCM.
The two early retry runs in `.build/opus-dma-yield-before-*.json` include RX
timeouts and are not isolated timing comparisons. No serial operations.
