# ESP8266 decoder speed optimization plan

This plan targets the native ESP8266 RTOS SDK firmware on the Xtensa LX106 at
160 MHz. The reproducible physical-board baseline and measurement method are
documented in `ESP8266_AUDIO_PROFILE.md`.

## Goal

Reach reliable realtime decoding with enough CPU margin for Wi-Fi, WebUI,
normalization, and asynchronous SPI-PDM output. Optimizations must be measured
on the same deterministic 45-second MP3 and AAC fixtures and must not reduce
decoder correctness.

## Work plan

- [ ] Create a pure RAM microbenchmark. Load one or more complete encoded
  frames into RAM and decode them repeatedly without Wi-Fi, flash reads,
  normalization, PDM conversion, SPI, or physical audio output. Compare this
  result with the existing decode-only network profile; that profile still
  includes Wi-Fi interrupts.
- [ ] Add stage-level Helix profiling for Huffman decoding, dequantization,
  IMDCT, synthesis/subband, and PCM assembly. Measure total time, call count,
  average time, and maximum time for every stage before selecting code to
  optimize.
- [ ] Unroll only the measured hottest fixed-trip loops. Benchmark unroll
  factors 2 and 4 for MP3 dequant/IMDCT/polyphase synthesis and AAC IMDCT/QMF;
  also compare manual unrolling with GCC `-funroll-loops`. Flash capacity is
  not the limiting resource, but record text growth and reject variants that
  lose speed through instruction-cache pressure or exceed the safe IRAM
  budget.
- [ ] Implement and benchmark Xtensa LX106 fixed-point primitives for
  32x32-to-high-32 multiplication, multiply-accumulate, count-leading-zeros,
  and saturation. Generic 64-bit operations are the main candidate for
  replacement. Keep a portable reference path for correctness comparison.
- [ ] Move only the hottest function to IRAM and measure the effect. Do not
  move all of Helix: after reserving the 16 KiB codec arena, only about 5 KiB
  of IRAM is considered safe for additional hot code.
- [ ] Identify small, frequently accessed lookup tables and selectively copy
  only those tables to RAM. Do not move all Huffman or IMDCT tables. Measure
  speed and heap/IRAM cost for every table moved.
- [ ] Add a one-channel decode or synthesis path when the physical output is
  mono. Avoid decoding stereo and then discarding or mixing one channel.
  Verify that mono streams and stereo-to-mono output remain correct.
- [ ] Investigate an MP3 mid/side joint-stereo fast path for mono output. For
  frames that use M/S stereo without intensity stereo, benchmark decoding and
  synthesizing only the mid (sum) channel instead of reconstructing left and
  right. Compare its PCM output against the rounded average of the reference
  stereo decoder and account for the Helix dequantizer's existing 1/sqrt(2)
  scaling.
- [ ] Keep a full-decoder fallback for MP3 intensity stereo and ordinary
  independent stereo; `joint stereo` does not always mean that the first
  coded channel is a directly usable sum channel. Test streams containing
  mode changes between consecutive frames so skipped side-channel IMDCT and
  synthesis history cannot corrupt later output.
- [ ] Continue optimizing asynchronous SPI-PDM output and avoid polling,
  unnecessary copies, and long critical sections. Treat this as a separate
  output-path optimization; it cannot by itself make MP3 320 kbit/s realtime.
- [ ] Re-run the complete bitrate matrix after every accepted optimization:
  MP3 32/128/320 kbit/s and AAC 48/128/320 kbit/s. Record realtime ratio,
  CPU busy/idle, decoder stage timings, worst decoder call, free heap, minimum
  free heap, and IRAM consumption.

## Priority

1. RAM-only microbenchmark, to separate decoder cost from Wi-Fi and flash.
2. Stage-level profiling, to identify the actual hot path.
3. Xtensa fixed-point primitives applied only to measured hotspots.
4. Measured loop unrolling in the hottest fixed-trip kernels.
5. One carefully selected IRAM function and small hot tables.
6. Mono decode/synthesis path, including the guarded MP3 M/S joint-stereo
   experiment, where the hardware output is mono.
7. Asynchronous SPI-PDM refinements and integration profiling.

## Current performance gap

With QIO at 80 MHz and normalization/PDM/SPI bypassed, the measured physical
board reaches 53.8% realtime for MP3 320 kbit/s and 80.8% for AAC 320 kbit/s.
Reaching exactly 100% therefore requires theoretical speedups of about 1.86x
for MP3 and 1.24x for AAC before restoring the output path. Safe production
operation needs additional margin above 100%.

The earlier QIO 40 MHz decode-only MP3 result was 38.4%, corresponding to the
previously quoted 2.6x gap. QIO 80 MHz reduced that gap but did not make MP3
realtime.

## Expected outcome

AAC is the more realistic candidate for realtime operation through a
combination of Xtensa-specific fixed-point operations, selective IRAM/RAM
placement, and output-path optimization. MP3 320 kbit/s still needs a much
larger improvement. It may require a decoder better optimized for LX106, a
mono-only synthesis path, or explicit limits on channel count and sample rate.
