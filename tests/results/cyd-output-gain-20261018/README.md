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

See [report and source hashes](report.json). Production builds, static analysis
and physical acceptance are tracked separately in the transfer plan.
