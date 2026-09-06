# ESP8266 AAC speed optimization — 2026-09-06

## Scope and acceptance criteria

Optimize the native Helix AAC-LC decoder on ESP8266/LX106, CPU 160 MHz,
QIO40, GCC 8.4 `-O3`. Preserve the 512-frame bounded PCM output, its 1024-byte
mono buffer, 6804-byte codec DRAM workspace and 16384-byte IRAM arena.
Do not change MP3, computer Wi-Fi, partitions, saved settings or playlists.

Keep a change only when physical A/B measurements show a repeatable speed
improvement without increased working memory or peak stack use. Report
average and maximum decode time; identical unchanged MP3 is a layout/control
measurement. New lookup tables must remain in flash, not RAM. ROM growth is
allowed, but instruction-cache effects must be measured.

Correctness gates: retained AAC fixtures (mono/stereo, sample rates and
transients), all four window sequences and both shapes, PCM and next overlap,
cancellation and truncated input. Compare PCM against the exact baseline:
report sample count, maximum absolute error and SNR; bit-identical output has
zero error and infinite SNR. Do not introduce lossy arithmetic implicitly.
Then test real I2S-PDM output for underruns and restore ordinary radio firmware.

## Checklist

- [x] Record fresh reference timing, memory and correctness results.
- [x] 1. Specialize window/overlap output into block loops: select window
  sequence outside the sample loop, walk pointers and remove per-sample calls.
  Preserve clipping/downmix order and update overlap only after consuming it.
- [ ] 2. Try a flash-only Huffman prefix lookup with the exact canonical
  decoder as fallback. Exhaustively compare symbols and consumed bit counts.
- [ ] 3. Try a fused bit-reader fast path to avoid repeated peek/refill work,
  retaining the existing state size and bounds behavior.
- [ ] Run the complete regression suite and physical output checks for the
  accepted combination; archive measurements and an ordinary firmware build.

For each experiment append the implementation, correctness/SNR, memory,
physical timing and keep/reject decision. Rejected experiments must not remain
enabled or leave unnecessary complexity in production code.

## Starting evidence

The preceding [bounded PCM experiment](ESP8266_AAC_PCM_BLOCKS.md) saved
3072 bytes DRAM but increased isolated AAC time from 17859 to 18945 us/frame
(48-kHz stereo AAC-LC at 320 kbit/s; 21333 us of audio/frame).
The current ELF has actual `call0` instructions for `aac_window_sample`,
called 2048 times per stereo frame. Historical profiles identify window/IMDCT
and Huffman as the dominant stages; their old percentages are not a new
measurement of this revision.

Existing exact LX106 high-half multiplication, mixed-radix FFT and
three-product complex butterflies are already optimized. AAC SSO remains OFF:
its earlier ~1.95% gain was not separated reliably from code-layout variation.
No blanket loop unrolling, added RAM tables or additional IRAM code is planned.

## Research references

- [FDK-AAC MDCT/window loops](https://github.com/mstorsjo/fdk-aac/blob/master/libFDK/src/mdct.cpp):
  specialize window regions and walk pointers; adapt algorithms, not differing
  Q-format/rounding assumptions.
- [FAAD2 Huffman](https://github.com/knik0/faad2/blob/master/libfaad/huffman.c):
  prefix/two-stage lookup. Generate our tables from existing Helix codebooks.
- [FAAD2 bit reader](https://github.com/knik0/faad2/blob/master/libfaad/bits.h):
  small fast paths; do not copy its larger reader state.
- [FFmpeg fixed DSP](https://www.ffmpeg.org/doxygen/trunk/libavutil_2fixed__dsp_8c_source.html):
  combined window/scale/PCM operations. Its generic 64-bit products are not
  an acceleration for LX106.

## Experiment log

### 1 — Window blocks: KEEP

Sequence-specialized channel loops replace per-sample calls. Mono writes the
clipped left channel then averages the separately clipped right channel into
the same buffer. This also supports distinct L/R window sequences.

200-frame physical RAM tests, repeated alternating original/candidate images:
AAC average **18945 -> 17951 us (-5.25%)**, maximum **18970 -> 17960 us**.
Unchanged MP3 moves **4632 -> 4754 us**, demonstrating code-layout sensitivity:
these are complete-image timings, not a claim that every improvement is due
only to instruction count. AAC DRAM/IRAM and free heap are unchanged; benchmark
task minimum free stack improves **1712 -> 1792 bytes**. Lifecycle heap delta=0.
Diagnostic image size increases 3904 bytes (277856 -> 281760).

Both exact and experimental SSO window tests pass 1280 state vectors each,
all block sizes, cancellation boundaries, coefficient immutability and canaries.
All retained mono/stereo AAC fixtures match the old full-frame window path:
maximum PCM error=0, SNR=Infinity dB. SSO is still disabled in firmware.

Reproduce alternating saved binaries with
`tools/esp8266_audio_profile/run_saved_images.ps1`; it writes only app0 and
uses RTS reset/TX capture without sending UART application bytes.
