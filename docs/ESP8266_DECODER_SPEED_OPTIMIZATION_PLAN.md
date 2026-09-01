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
- [x] Adapt libmad `OPT_SSO` scaling to the Helix polyphase synthesis. Split
  the fixed-point shift between Q23 `vbuf`, Q18 coefficients, and final PCM
  conversion so the LX106 uses native 32-bit multiply/accumulate operations.
  Keep the exact 64-bit path as the default and select SSO at build time.
  The implementation adds no buffer and passes host PCM/SNR plus physical
  QIO80 RAM benchmarks.
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
- [x] Optimize the default I2S-PDM output: use a 456-byte IRAM branchless,
  fully unrolled PDM32 packer and replace 2-ms DMA polling with one direct
  FreeRTOS task notification per 512-word buffer. On the physical board this
  reduced the generated-PCM producer non-wait bound from 33.5% to 9.1%, with
  100.2% realtime output and zero underruns.
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

### Physical result after the libmad IRAM frame split — 2026-09-01

The comparison was repeated on the same Wemos D1 mini after moving libmad's
4608-byte `xr_raw` and 2304-byte reorder workspace from DRAM into the existing
16-KiB word arena. Both images used 160 MHz CPU, QIO flash at 80 MHz, GCC 8.4
`-O3`, the same RAM-resident 320-kbit/s frame, 8 warm-up frames and 200 measured
frames. Wi-Fi and audio output remained disabled.

| Backend/fixture | Average frame | Maximum frame | Audio/CPU speed | Free heap | Codec DRAM | Reserved IRAM | App binary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Helix MP3 320 kbit/s | 13,786 us | 13,806 us | 1.740x | 81,272 B | 14,756 B | 16,384 B | 275,744 B |
| libmad MP3 320 kbit/s | 11,965 us | 11,969 us | 2.005x | 74,648 B | 22,180 B | 16,384 B | 326,128 B |
| Helix AAC control, Helix image | 16,127 us | 16,140 us | 1.322x | 86,180 B | 9,872 B | 16,384 B | 275,744 B |
| Helix AAC control, libmad image | 15,981 us | 15,990 us | 1.334x | 86,940 B | 9,880 B | 16,384 B | 326,128 B |

Against the current Helix build, libmad reduces average MP3 frame time by
13.21% and increases throughput by 15.23%. It uses 7424 bytes more dynamic
DRAM, leaves 6624 bytes less free heap, and adds 50384 bytes of application
flash. Both reserve the same 16-KiB IRAM arena in this fair MP3+AAC profile.

Against the previous libmad baseline, the IRAM split reduces average frame
time from 12904 to 11965 us (7.28%), raises throughput from 1.859x to 2.005x
(7.85%), and increases free heap from 67888 to 74648 bytes (+6760). The
unchanged Helix AAC control differs by less than 1%, which bounds build-layout
and measurement noise well below the MP3 result. Fifty create/destroy cycles
and fifty MP3/AAC switches returned heap from 96868 to 96868 bytes (delta 0).

The reset-loop paragraph above records the older eager-allocation image. The
current source allocates codec state lazily and the new full benchmark creates
libmad successfully, but the complete libmad+AAC radio/WebUI image still needs
an integrated physical run before replacing Helix as the production default.

## Experimental Helix 32-bit SSO synthesis — 2026-09-01

The libmad `OPT_SSO` idea was adapted to the existing Helix data layout rather
than copying libmad's larger decoder state. Helix stores synthesis history as
Q23 and its window table as Q18. The experimental path removes 12 bits from
the history value and 4 bits from the coefficient before multiplication, then
uses a Q25 signed 32-bit accumulator and a 10-bit rounded PCM conversion. It
reuses the existing `vbuf` and `polyCoef` table and is selected with
`CONFIG_YORADIO_HELIX_MP3_SSO` or the reproducible
`sdkconfig.helix-sso-qio80.defaults` profile.

The host golden test decoded all 18 retained 320-kbit/s stereo MP3 frames and
kept the same frame/sample count. Against exact Helix PCM, SSO measures 48.50
dB SNR with a maximum absolute error of 34 signed 16-bit PCM levels. The exact
non-SSO build remains byte-identical to the existing golden hash.

The physical A/B used the same Wemos D1 mini, 160 MHz CPU, QIO flash at 80
MHz, GCC 8.4 `-O3`, RAM-resident first MP3 frame, 8 warm-ups and 200 measured
frames. Wi-Fi, normalization, and SPI-PDM output were disabled.

| Helix MP3 320 kbit/s | Average frame | Maximum frame | Audio/CPU speed | Free heap | Codec DRAM | App binary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Exact 64-bit polyphase | 13,705 us | 13,722 us | 1.751x | 81,280 B | 14,756 B | 275,872 B |
| 32-bit SSO polyphase | 6,414 us | 6,432 us | 3.741x | 81,280 B | 14,756 B | 275,472 B |

SSO reduces frame time by 53.20% and raises isolated decode throughput by
113.69%. Dynamic DRAM, arena use, and free heap are unchanged; 50
create/destroy and MP3/AAC switches return heap from 96,108 to 96,108 bytes in
both builds. The generated `PolyphaseStereo()` stack frame falls from 144 to
128 bytes. The complete benchmark image is 400 bytes smaller, although the
stereo function itself grows because GCC keeps more 32-bit operations inline.
AAC is unchanged and measured 15,860 us in the SSO image versus 16,010 us in
the exact image, a 0.94% build-layout variation.

This result is substantially faster and smaller in RAM than the experimental
libmad backend. SSO remains opt-in until live radio, WebUI, normalization, and
SPI-PDM tests cover the full MP3 bitrate/channel/block-type matrix.

## Experimental Helix AAC 32-bit transform products — 2026-09-01

The same reduced-precision idea was tested independently in AAC-LC. The exact
LX106 `MULSHIFT32` helper forms the signed high half of a 32x32 product from
four partial products. `CONFIG_YORADIO_HELIX_AAC_SSO` omits only the low*low
term and retains high*high plus both signed cross terms. TNS `MADD64` remains
exact. The switch is disabled by default and the reproducible QIO80 profile is
`sdkconfig.aac-sso-qio80.defaults`.

The host regression decoded the same 19 retained 320-kbit/s stereo AAC-LC
frames (38,912 samples). Against exact Helix PCM, the optimized output measures
82.65 dB SNR with a maximum absolute error of one signed 16-bit PCM level. A
more aggressive two-product experiment reached a 311-level maximum error and
was rejected.

The physical A/B used the same Wemos D1 mini, 160 MHz CPU, QIO flash at 80 MHz,
GCC 8.4 `-O3`, a RAM-resident AAC frame, 8 warm-ups and 200 measured frames.
Wi-Fi, normalization and SPI-PDM output were disabled.

| Helix AAC-LC 320 kbit/s | Average frame | Maximum frame | Audio/CPU speed | Free heap | Codec DRAM | App binary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Exact high-half product | 16,010 us | 16,990 us | 1.332x | 86,188 B | 9,872 B | 275,872 B |
| Three-product SSO | 15,698 us | 16,660 us | 1.358x | 86,188 B | 9,872 B | 274,512 B |

The optimized path reduces the measured average frame time by 1.95%, increases
isolated throughput by 1.95%, and removes 1,360 bytes from the benchmark image.
Free heap, codec DRAM and the 16-KiB reserved IRAM arena are unchanged. The
generated hot transform functions become 65 to 224 bytes smaller each, but an
unchanged MP3 control moved by about 4.7% between the two image layouts. The
AAC timing gain is therefore too small to promote this approximation to the
production default. It remains an opt-in experiment; the exact implementation
is still selected unless `CONFIG_YORADIO_HELIX_AAC_SSO` is enabled.

## Expected outcome

AAC is the more realistic candidate for realtime operation through a
combination of Xtensa-specific fixed-point operations, selective IRAM/RAM
placement, and output-path optimization. MP3 320 kbit/s still needs a much
larger improvement. It may require a decoder better optimized for LX106, a
mono-only synthesis path, or explicit limits on channel count and sample rate.
