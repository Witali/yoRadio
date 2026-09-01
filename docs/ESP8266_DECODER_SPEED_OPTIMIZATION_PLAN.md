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

- [x] Create a pure RAM microbenchmark. Load one or more complete encoded
  frames into RAM and decode them repeatedly without Wi-Fi, flash reads,
  normalization, PDM conversion, SPI, or physical audio output. Compare this
  result with the existing decode-only network profile; that profile still
  includes Wi-Fi interrupts.
- [x] Add stage-level Helix profiling for Huffman decoding, dequantization,
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
- [x] Audit integer division in the measured hot paths. Replace the ESP8266
  MP3 parser and IMDCT block-count divisions by 3, 5, 6, 18, and 36 with an
  exact Q32 reciprocal multiply-and-shift. Derive a remainder from the one
  quotient instead of invoking both divide and modulo helpers. The reciprocal
  estimate has a one-step correction, preserving C integer truncation for the
  complete unsigned 32-bit range. Verify the generated code and golden PCM.
- [ ] For a divisor reused across samples or bands, calculate its fixed-point
  reciprocal once and replace repeated variable division with
  multiply-and-shift. The MP3 and AAC-LC sample loops contain no such variable
  division. AAC has candidates in SBR setup and gain limiting; add an
  HE-AAC/SBR golden fixture before changing them because the existing AAC
  fixture exercises LC only.
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
4. Reciprocal multiply-and-shift for measured repeated variable divisors.
5. Measured loop unrolling in the hottest fixed-trip kernels.
6. One carefully selected IRAM function and small hot tables.
7. Mono decode/synthesis path, including the guarded MP3 M/S joint-stereo
   experiment, where the hardware output is mono.
8. Asynchronous SPI-PDM refinements and integration profiling.

## Current performance gap

With QIO at 80 MHz and normalization/PDM/SPI bypassed, the measured physical
board reaches 53.8% realtime for MP3 320 kbit/s and 80.8% for AAC 320 kbit/s.
Reaching exactly 100% therefore requires theoretical speedups of about 1.86x
for MP3 and 1.24x for AAC before restoring the output path. Safe production
operation needs additional margin above 100%.

The earlier QIO 40 MHz decode-only MP3 result was 38.4%, corresponding to the
previously quoted 2.6x gap. QIO 80 MHz reduced that gap but did not make MP3
realtime.

The isolated QIO 80 MHz RAM benchmark, with Wi-Fi and audio output never
started, repeats one complete 48-kHz/320-kbit/s encoded frame 200 times. MP3
averages 16,189 us per frame (148.2% realtime, 1.482x), while AAC-LC averages
15,950 us (133.7% realtime, 1.337x). The 28-us MP3 and 23-us AAC min-to-max
spreads show that network interrupts and stream pacing account for most of the
long-tail latency in the integrated profile; the remaining CPU margin is still
insufficient once Wi-Fi and SPI-PDM are restored.

The physical stage profile (same RAM fixture, 200 iterations) identifies the
actual hot kernels. MP3 synthesis/subband consumes 93.2% of decode time;
Huffman consumes 2.3%, IMDCT 1.5%, and dequantization 0.5%. AAC-LC IMDCT
consumes 52.9%, Huffman 34.5%, stereo/PNS/TNS processing 6.7%, and
dequantization 4.5%. These figures make MP3 synthesis and AAC IMDCT/Huffman
the first loop-unrolling candidates. The instrumentation changes flash layout
and adds timer calls, so its absolute frame time is not used as the
unprofiled performance baseline.

The reciprocal-division change was also measured as a clean compile-time A/B
test with all stage hooks disabled. With reciprocal division disabled, MP3
averages 14,653 us per frame (1.637x realtime); with it enabled, the same frame
averages 14,284 us (1.680x), a 2.52% decoder speedup. The benchmark binary grows
from 273,040 to 273,664 bytes (+624 bytes). Disassembly leaves only the rare,
one-time free-format bitrate division in MP3. MP3 and AAC golden PCM hashes are
unchanged. AAC-LC has no affected code path; its 15,872 versus 15,920 us A/B
shift is caused by flash layout after the MP3 text-size change and is not an
AAC algorithm change.

## Expected outcome

AAC is the more realistic candidate for realtime operation through a
combination of Xtensa-specific fixed-point operations, selective IRAM/RAM
placement, and output-path optimization. MP3 320 kbit/s still needs a much
larger improvement. It may require a decoder better optimized for LX106, a
mono-only synthesis path, or explicit limits on channel count and sample rate.
