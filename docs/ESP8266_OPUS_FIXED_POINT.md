# ESP8266 Opus arithmetic audit

Verified on 2026-09-09 against the native LX106 build
`firmware/development/esp8266-opus-http-ram` (source `9ebf42d`).

Opus already uses integer fixed-point arithmetic. No float-to-fixed
conversion is required:

- `upstream/include/config.h`: `FIXED_POINT=1`, `DISABLE_FLOAT_API=1`.
- The actual Xtensa GCC preprocessor selects `OPUS_FAST_INT64=0`.
- The active `celt/arch.h` types are signed 16-, 32- and 64-bit integers.
  Remaining integer 64-bit operations are not floating-point emulation.
- `FLOAT_APPROX=1` is an inherited configuration definition, but the
  corresponding floating-point arithmetic branch is inactive.
- `xtensa-lx106-elf-nm -u` on `libopus_decoder.a` finds no software
  float/double arithmetic/conversion helpers or libm arithmetic calls.
  This check applies to the Opus component, not every module in the firmware.

The preprocessor and archive results are saved in the firmware directory's
`fixed-point-results.json`. Raw physical CPU measurements are in
`../firmware/development/esp8266-opus-word-asm/comparison-results.json`:
CELT 64 kbit/s takes about 73.8% of the CPU budget, CELT 128 about 91.4%,
with the opt-in private-word ASM access experiment. These are decoder-only
measurements, excluding network, Ogg, normalizer and PDM output; ISR time
charged to the decoding task remains included. They do not prove continuous
whole-pipeline playback.

A captured 56-kbit/s CELT radio excerpt also matches the independently
prepared upstream generic32 reference exactly: 648000 PCM samples, zero
differences; scratch peak 5488/6144 bytes. See `real-capture-pcm-results.json`.
The capture itself is not redistributed. The board's separate Ogg live-join
failure at this revision is not a floating-point performance problem.

## Later physical ICDF comparison

The two-run comparison in
`../firmware/development/esp8266-opus-icdf-on-bench/comparison-results.json`
keeps the same fixed-point decoder and uses aligned32-bit loads for static
ICDF flash tables. Compared with its paired OFF build, decode time fell
1.09–4.54% depending on mode, with all PCM fingerprints unchanged. This is
a memory-access optimization, not replacement of floating-point arithmetic.
ON CPU budgets: SILK12 58.20%, Hybrid24 91.85%, CELT64 74.35%, CELT12890.03%,
CELT510150.91%, excluding network audio and output. The same revisions still
show real radio RX timeouts and DMA underruns; full playback is not qualified.
