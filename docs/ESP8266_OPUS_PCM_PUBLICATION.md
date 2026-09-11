# Opus: publish completed PCM batches before the next decode

2026-09-11. Experimental, default OFF; no continuity improvement claimed yet.

## Evidence and hypothesis

On source5147be3, input1KiB, FIR/ICDF/word helpers, local own SILK12 HTTP:
a steady 26991ms interval delivered27060ms PCM (ratio1.00256), with no
input-wait calls, but26 DMA misses. Read had0 attributed misses, decode0,
output15; health and profile are separate requests, so this is not a
precise causal accounting. Output wall time includes DMA waits, not CPU.

The bridge delivers a960-sample frame as512+448. Commit previously kept a
partially filled buffer available for the next callback until an EOF took
its prefix. Whether the next callback appends therefore depends on timing;
shorter prefixes leave less queued audio while the next frame is decoded.
This is a hypothesis for some short misses, not an explanation of TCP stalls.

## Isolated candidate

`-OpusPcmPublish`, CMake `YORADIO_ESP8266_OPUS_PCM_PUBLISH`, requires diagnostic
Opus and standard I2S PDM32. At the end of each successful Opus PCM callback,
publish its exact committed tail. MP3/AAC, the PCM callback sizes, normalization,
gain, PDM bit algorithm, network waits and the ISR are unchanged.

The single producer changes FILLING to READY in a short critical section:
no writable loan may remain, the descriptor length was set by commit,
and no active DMA memory is touched. Empty/already published calls succeed.
No padding, replay, extra buffer, persistent counter, busy wait or malloc.
Both physical buffers remain512words. Coded durations/pre-skip/EOS may yield
other tail lengths and must remain valid; no assumption that every call is448.

## Acceptance

- [x] Actual producer host tests: exact lengths1/64/120/136/448/480/512,
  publication during live loan rejected, idempotence,100 frames of512+448,
  ordered payload with no inserted/dropped words, stop and IRQ interleavings.
- [x] Full PCM/PDM publication ON/OFF matrix and build-flag regression:
  PDM32/128, RCPDM, Simple and Feedback, six sample rates, mono/stereo,
  normalization on/off and six batch sizes; every resulting PCM/PDM value
  matches. Ten initial tests and seven expanded tests pass, no skips.
- [ ] Compile matching ON/OFF images; compare static RAM, IRAM and ISR.
- [ ] At least10 attempted physical windows per variant on the same fixture;
  retain start failures, transport errors, missing samples and DMA misses.
- [ ] Recheck real Opus radio >=20s and WebUI; faster raw decoder alone is not
  completion. Reject candidate if no repeatable benefit or if RAM regresses.

No production default has been changed. Raw Opus CPU figures remain in
[the invariant audit](ESP8266_OPUS_LOOP_INVARIANTS.md); they do not measure PDM.
