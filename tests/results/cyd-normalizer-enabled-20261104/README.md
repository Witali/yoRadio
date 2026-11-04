# CYD enabled multichannel normalizer: finite SDK/QEMU result

Native02 completed **PASS**: two complete creator F12 C8/48 kHz plays using the
real CYD stream/decode/output tasks and output DSP. Settings are enabled,
20 dB maximum boost, -20 dBFS target, 100 ms response, volume 127, balance 0.
The whole and fragmented transports each retain 9,600 logical frames:
153,600 B source PCM, 19,200 B exact mono and 19,456 B wire output including
256 verified zero-padding bytes. The two mono SHA256 values match the
preselected independent integer/100- and 160-digit Decimal model with zero tolerance.

The first play requests reset twice after 5,448 frames; one actual output-owner
reset follows before the next packet. Both plays separately record the EOF
reset at frame 9,600 in FLUSH phase. A second play alone cannot isolate EOF
reset because generation discard also resets DSP. All 152 real write returns
retain the borrowed source unchanged. All 10 public codec owners and two HTTP
owners close. Stream/decode/output bindings remain core 0/1/1, priorities 3/5/6,
stacks 6144/16384/4096 B.

The reference phase completes 13 direct-public cases before the application
tasks. Fresh F12 PCM is byte-equal to the complete 153,600 B preselected source;
both source and final mono use the same pinned Espressif decoder integration.
This is finite integration acceptance, with diagnostic TWDT 20 s/panic,
INT 1000 ms and light heap checks. Production-policy timing, full radio/TLS/TFT
resources, physical DMA/audio and independent codec conformance remain separate.
The larger 48-case descriptor is retained as an asset source; this gate executes
two enabled cases. Allocation/error qualification is separate; no terminal
word-allocation or health-fault census is asserted here.

SDK wrapper PID 35748 returned 0 in 186.031 s; its SDK child PID 27032 returned 0.
QEMU PID 6592 returned 0 in 46.796 s. There are 18 actual application TUs and 474
compiler dependencies; the diagnostic app is 3,192,160 B. Exact linker wrappers
are SDK 32 + inherited target 43 + normalizer 4 = 79. Original native01 remains
NONPASS from test CMake early-expansion handling; the subsequent change adds
only the outer post-include early return.

`observations.json` contains exact selected UART lines with original line indexes,
including every source-write return. `expected.json` is the original preselected
golden metadata. `provenance.json` records process/source/reference bindings;
whole process receipts, raw PCM, full UART, SDK, ELF and images remain local.
Published verification checks selected observations and current source hashes.
Replaying the numeric oracle requires the retained local PCM. It executes no
archived controller, SDK, decoder, native object or guest.

Run `python -B verify.py --require-current` from this directory or any cwd.

Entry points: [thin target](../../target/cyd_family1_normalizer_qemu/project/main/main.cpp),
[integer model](../../fixtures/family1_normalizer/model.py),
[strict record reader](../../fixtures/family1_normalizer/records.py),
[actual output DSP](../../../idf/esp32-cyd2usb-native/main/native_audio_output.c).
