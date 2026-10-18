# CYD block-level PCM gain

The CYD output now computes volume/balance coefficients once per PCM packet,
following the C3 optimization while retaining CYD mono downmix. PDM, continuous
DAC and legacy DAC all use this calculation. Mono continues to ignore balance;
multichannel input continues to mix its first two channels. There are no new
allocations or changes to pins, clocks, resampling, DMA, or SDK configuration.

[Executable test](../../run-cyd-output-gain.py) extracts the actual fixed-point
helpers and each backend's production PCM writer. Each of the three variants
passes 5,801,300 arithmetic comparisons and 375 output cases under ASan/UBSan.
The independent wide-arithmetic reference covers every volume/balance setting,
signed PCM limits, a full int16 sweep for selected settings, unaligned input,
incomplete final frames, split packets and settings changes between packets.
The coefficient counter proves one evaluation per mono packet or two per
stereo/multichannel packet, independent of its frame count. Invalid input
returns before reading settings or evaluating coefficients.

The PDM resampler and hardware writes are capture seams. The actual legacy
fractional DAC conversion and packing also execute and match the reference
across split packets. These results prove PCM behavior and evaluation counts,
not a measured speedup or physical audio quality on CYD.

See [report and source hashes](report.json). The existing six queue/codec
[lifecycle variants](lifecycle/report.json) and all 13 settings/clock
[source checks](source-tests.log) also pass. Two stale source assertions were
updated to follow the common radio implementation and the mono balance guard;
the executable PCM comparisons above cover actual balance behavior.

All three GCC/IDF 6.0.2 production builds from clean source `e822d3c2` pass:

| Backend | Image bytes | Saved image and manifest |
| --- | ---: | --- |
| PDM | 1,378,208 | [firmware](../../../firmware/development/esp32-cyd2usb-native-pcm-gain-pdm/manifest.json) |
| Continuous DAC | 1,372,160 | [firmware](../../../firmware/development/esp32-cyd2usb-native-pcm-gain-dac/manifest.json) |
| Legacy DAC | 1,378,208 | [firmware](../../../firmware/development/esp32-cyd2usb-native-pcm-gain-legacy/manifest.json) |

[Build logs and hashes](builds/report.json) accompany the saved app images and
SDK configurations. Each manifest agrees with the embedded source version and
ELF digest; all images fit the unchanged OTA slot. The PDM profile retains every
existing baseline SDK value and default-off prefill/diagnostic settings.

The full CYD PDM [clang-tidy/Static Analyzer rerun](../native-lint-20261018/cyd-output-gain/report.json)
completes all 18 project-owned units with 11 warnings and zero errors. The
file/check/message findings are identical to the preceding complete run; no
checks were disabled. GCC compilation and executable writer tests cover the
other two backend branches. The boards have not been flashed for this change;
physical acceptance and the remaining normalizer work are still open.
