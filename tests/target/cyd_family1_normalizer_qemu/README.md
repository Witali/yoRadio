# Enabled family1 normalizer gate — native UNRELEASED

This new profile prepares two complete original F12 `active8_120` plays over
the unchanged family1 application/renderer/driver observation graph. The first
uses whole pages with existing one-byte HTTP reads and a predeclared transport
hold; the second uses existing continued pages and 257-byte reads. Both retain
all original coded packets, OpusHead gain +6 dB, CRC/lacing/granule provenance,
eight logical channels and 9600 frames. Public settings select normalization
enabled, boost 20 dB, target −20 dBFS, time 100 ms, rate 48 kHz, volume 127/balance 0.

The coordinator includes the frozen original target with a renamed unused
entrypoint. The new main-component CMake file includes its unchanged declaration
and adds passive forwarding observations of public normalizer C APIs. All six
production translation units, original task bindings and diagnostic watchdog
profile remain inherited: stream 0/3/6144, decode 1/5/16384, output 1/6/4096;
TWDT 20 s/panic, interrupt 1000 ms, light heap poisoning. This does not establish
production watchdog equivalence, full-radio resource margins or physical audio.

The HTTP read seam clamps every returned byte at the independently prepared
first-complete-audio-page boundary at byte 8413. A large encoded ring cannot prefetch bytes
beyond that boundary. After all 5448 first-packet logical frames have passed the
real renderer and its public write wrapper has returned, two public reset
requests are issued before transport release. Current PDM idle() does not read
normalizer settings or consume reset. No task is suspended and no private DSP
state or ACK is written. The next real C reset must occur on output core 1/
priority 6 at frame 5448, with cached configuration and geometry unchanged.
The reader separately requires the real EOF C reset at frame 9600 in FLUSH phase
before any next generation. The second complete play requests no extra reset.
Its clean PCM checks restart integration; generation changes also discard/reset
DSP, so its PCM alone cannot isolate a missing EOF reset. The mandatory observed
FLUSH reset supplies that independent EOF evidence.

The independent Python model owns integer peak/envelope/gain/limiter arithmetic;
it imports no production normalizer. Selected profile constants derive max Q12
gain 40960 and target 3277. The limiter's rational nodes and interpolation are
constructed independently. Existing separately qualified Decimal speaker/header/
player formulas project its output at 100 and 160 digits, requiring exact agreement.
Fixed disabled, first-two detector, first-two processing and header-before-detector
controls must each differ in the final complete mono stream before native launch.
Expected interior reset positions are [5448] for case 1 and none for case 2. Raw S16 reference,
normalized/golden PCM and all media remain in the caller's ignored output.

The preparer may authenticate only the complete F12 direct-public reference
subphase of an unchanged terminal NONPASS whole capture. It never relabels that
whole run as successful or executes captured code. Original UART hash, report,
execution bundle, actual reference compiler dependencies and source pins are
bound. The decoder reference remains same-vendor integration; creator numerical
conformance and native limiter-knee coverage are separate.

```text
python tests/test-cyd-family1-normalizer-model.py --output .build/normalizer-model-controls-NEW
python tests/prepare-cyd-family1-normalizer-gate.py --prepare-only --output .build/normalizer-gate-prepared-NEW
```

The preparation reuses current owned family1 capture/fixture utilities without
calling their process launcher. Prepared source aliases are explicitly hashed,
including original shared sources and generated asset views. It starts no Git,
compiler, SDK, decoder or QEMU process. Native launch is UNRELEASED, with no
execution option implemented. Root must review the new sources/oracle and own a
future fresh compiler/dependency/link/image qualification and strict actual
transcript/full PCM comparison. The two-play oracle does not extend AAC or Vorbis.
