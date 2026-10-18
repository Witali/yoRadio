# CYD bounded first-input prefill

The CYD default remains zero (disabled). Configured waits are limited to
0–2,000 ms and end when storage is occupied, a logical deadline is reached,
or the generation is cancelled/failed. Scheduling latency is not qualified.

[The standalone test](prefill/report.json) compiles the actual private
production helper under ASan/UBSan with scripted queue/time/task seams. It
covers disabled/full/empty input, filling during a wait, timeout, cancellation,
output failure, a coarse 20 ms tick, 64-bit time past UINT32_MAX and occupied
WRITING/READING leases with no ready audio.

[Lifecycle integration](lifecycle/report.json) executes actual decoder/output
tasks and state functions in six ring/leased-queue and codec combinations.
The three leased-queue branches enable a 250 ms prefill in the host build.
Assertions check that Stop returns the held input without decoder allocation,
startup control replay bypasses the wait, and AAC-to-MP3 drain in one generation
does not wait a second time. Codec and queue APIs are scripted here; the actual
shared queue has independent [concurrent ownership coverage](../cyd-c3-frames-20261018/README.md).

The GCC/ESP-IDF 6.0.2 PDM build with prefill set to 250 ms passes for source
`112c871f`. Its 1,365,040-byte [application](../../../firmware/development/esp32-cyd2usb-native-prefill250-pdm/app.bin)
and [manifest/config](../../../firmware/development/esp32-cyd2usb-native-prefill250-pdm/manifest.json)
are saved as a separate experimental profile. The descriptor is clean and the
embedded ELF hash matches the build ELF. All pre-existing baseline SDK values
are preserved; the manifest records the added portable feature settings.

A separate Clang configuration enables the same 250 ms branch. Its
[complete full analysis](../native-lint-20261018/cyd-prefill250/report.json)
covers 14 project-owned units, with 11 warnings and zero parse/tool errors.
The private prefill helper introduces no diagnostics.

This is software/build coverage, not a measured CYD network-jitter or
audio-quality improvement. No image was installed on a board.
