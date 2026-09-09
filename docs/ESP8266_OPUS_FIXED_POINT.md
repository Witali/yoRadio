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
