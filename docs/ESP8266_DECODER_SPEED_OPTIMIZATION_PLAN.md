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
- [x] Unroll only the measured hottest fixed-trip loops. Benchmark unroll
  factors 2 and 4 for MP3 dequant/IMDCT/polyphase synthesis and AAC IMDCT/QMF;
  also compare manual unrolling with GCC `-funroll-loops`. Flash capacity is
  not the limiting resource, but record text growth and reject variants that
  lose speed through instruction-cache pressure or exceed the safe IRAM
  budget. The tested global, pragma-directed, and manual variants were all
  rejected; the production source keeps the original compact loop.
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
- [x] Add the ESP8266Audio `libmad-8266` core as an experimental MP3 backend,
  pinned to upstream commit `10d929ac01436dfe8856e0a06fd9ec35a848c6e2`.
  Keep Helix as the production default and retain the same native stream,
  PCM callback, normalizer, and output path so the A/B benchmark changes only
  the MP3 decoder. The physical RAM benchmark is complete; the integrated
  radio image is currently blocked by its Wi-Fi startup memory failure.

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

The refined MP3 stage profile splits synthesis into FDCT32 and polyphase
convolution. Synthesis consumes 93.8% of measured decode time: FDCT32 accounts
for 19.7% and polyphase convolution for 73.8%. This makes
`PolyphaseStereo()` the dominant kernel, but loop unrolling is counterproductive
on the LX106. GCC 8.4 disassembly of the original, manually unrolled x2, and
manually unrolled x4 functions gives the following results:

| variant | function bytes | instructions | stack frame | `l32i` | `s32i` | stack operands | MP3 us/frame |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original | 1,730 | 680 | 144 B | 154 | 99 | 240 | 14,284 |
| manual x2 | 2,763 | 1,049 | 288 B | 305 | 146 | 432 | 15,092 |
| manual x4 | 4,699 | 1,754 | 560 B | 567 | 257 | 793 | 15,669 |

The x2 and x4 versions are 5.7% and 9.7% slower on the physical board. The
large increase in loads, stores, and stack references shows register pressure
forcing GCC to spill intermediate accumulators to RAM. Global
`-funroll-loops` is also slower (14,759 us/frame, with binary growth from
273,664 to 285,472 bytes). Targeted `#pragma GCC unroll 2/4` produces
14,336/14,338 us per frame, also slightly slower than the 14,284-us baseline.
All variants preserve the golden PCM output, but none earns its code and stack
cost, so no unrolling switch or duplicated loop remains in production.

The reciprocal-division change was also measured as a clean compile-time A/B
test with all stage hooks disabled. With reciprocal division disabled, MP3
averages 14,653 us per frame (1.637x realtime); with it enabled, the same frame
averages 14,284 us (1.680x), a 2.52% decoder speedup. The benchmark binary grows
from 273,040 to 273,664 bytes (+624 bytes). Disassembly leaves only the rare,
one-time free-format bitrate division in MP3. MP3 and AAC golden PCM hashes are
unchanged. AAC-LC has no affected code path; its 15,872 versus 15,920 us A/B
shift is caused by flash layout after the MP3 text-size change and is not an
AAC algorithm change.

## Experimental libmad-8266 baseline

The imported fixed-point core decodes the checked-in 48-kHz stereo
320-kbit/s fixture to the same 18 frames and 82,944 PCM bytes as the current
yoRadio Helix decoder. The approximate `FPM_DEFAULT`/`OPT_SPEED` arithmetic is
not bit-identical: measured directly against the Helix PCM, SNR is 49.41 dB
and the maximum absolute difference is 99 signed 16-bit PCM levels. These
small low-bit differences are accepted for the speed experiment.

Both complete QIO80 radio images build with GCC 8.4 and `-O3`. Compared with
Helix, the libmad image grows from 670,848 to 721,232 bytes (+50,384 bytes).
Static DRAM falls from 16,752 to 15,984 bytes, while the decoder's reported
dynamic workspace rises from 28,984 to 33,336 bytes (+4,352 bytes).

### Physical Wemos D1 mini result — 2026-09-01

The A/B run used the same ESP8266EX at 160 MHz, QIO flash at 80 MHz, GCC 8.4
`-O3`, the same first frame copied to RAM, 8 warm-up frames and 200 measured
frames. Wi-Fi, normalization and SPI-PDM output were disabled. The PCM callback
only consumed two samples, so the result measures decoder throughput rather
than the complete radio pipeline.

| Fixture/backend | Average frame | Maximum frame | Audio/CPU speed | Free heap | Workspace | Arena |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MP3 320 kbit/s, Helix | 14,289 us | 14,313 us | 1.679x | 81,416 B | 28,984 B | 23,228 B |
| MP3 320 kbit/s, libmad | 12,904 us | 12,925 us | 1.859x | 67,888 B | 33,336 B | 27,656 B |
| AAC 320 kbit/s, Helix image | 15,890 us | 15,900 us | 1.342x | 86,324 B | 28,984 B | 20,600 B |
| AAC 320 kbit/s, libmad image | 16,082 us | 16,103 us | 1.326x | 63,656 B | 33,336 B | 20,600 B |

For MP3, libmad reduces average frame time by 9.69% and raises throughput by
10.72%. Its maximum frame remains below the 24 ms represented by one MPEG-1
Layer III frame at 48 kHz, so the isolated decoder has 46.2% timing headroom.
The AAC implementation is identical in both images; its 1.2% shift is a build
layout effect, not a libmad AAC result. Free-heap values are end-to-end values
of different firmware images and therefore include code/layout effects in
addition to the reported codec workspace.

The complete libmad radio image is not usable yet. It starts with 92,996 bytes
free, allocates the 33,336-byte codec workspace before Wi-Fi, mounts SPIFFS and
loads the 511-station index, then `network_service_start()` returns an error
after indexing the Wi-Fi credential. `ESP_ERROR_CHECK` aborts and the board
enters a repeatable reset loop. The matching Helix image starts normally,
obtains `192.168.100.6`, and has 7,436 bytes free after DHCP. This strongly
indicates that the extra pre-Wi-Fi decoder allocation/heap layout leaves no
safe memory margin for the Wi-Fi startup path. Helix therefore remains the
production default. Before another integrated libmad test, allocate the MP3
decoder lazily after Wi-Fi initialization or reduce its workspace, then repeat
the full live-stream, WebUI and codec-switch matrix.

## Expected outcome

AAC is the more realistic candidate for realtime operation through a
combination of Xtensa-specific fixed-point operations, selective IRAM/RAM
placement, and output-path optimization. MP3 320 kbit/s still needs a much
larger improvement. It may require a decoder better optimized for LX106, a
mono-only synthesis path, or explicit limits on channel count and sample rate.
