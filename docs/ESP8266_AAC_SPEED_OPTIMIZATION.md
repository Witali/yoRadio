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

- [ ] Record fresh reference timing, memory and correctness results.
- [ ] 1. Specialize window/overlap output into block loops: select window
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

Pending. No acceleration is claimed before measurement.
