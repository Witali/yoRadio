# Combined AAC compression: precision and memory accounting

This experiment combines the previously separate compression probes and the
actual packed PS delay writes in one candidate decoder. Every comparison uses
an independent unmodified decoder with the same input. IMDCT compression stays
disabled because it failed the accuracy limit. Native DSP scales and output
formats remain unchanged.

Production tolerance is **+/-3 signed-16 PCM units per channel and sample**.
This is a maximum-error gate, not an RMS limit or permission to discard three
bits. See [precision policy](ESP32C3_AAC_PRECISION_POLICY.md).

The [persistent high-history follow-up](ESP32C3_AAC_HIGH_HISTORY_20261003.md)
implements one of these areas with a genuinely smaller owner and also tests
real-only SBR. It measures 6,144 B of owner-block saving including the earlier
lossless changes. That separate result does not turn the full combination's
21,096-byte estimate below into a measured saving.

## What is combined

- New low-QMF analysis rows and retained high-QMF history.
- PS decorrelation delays: actual packed writes and reads, with the original
  arithmetic and checked bounds/guards.
- Hybrid history, previous PS mix coefficients, left hybrid output and PS energy
  histories at the previously audited boundaries.
- Gain/noise smoothing mantissas at frame boundaries and checked int16 exponents.
- Independent memory accounting for the lossless five-pointer table layout and
  PS-control relocation; these do not alter numerical precision.

The final mixed candidate uses **16+16 with a shared exponent** for low/high QMF,
smoothing mantissas and PS delays, and **18+18 with a shared exponent** for the
smaller hybrid/mix/energy areas. Smoothing exponents are checked int16 values.
Aligned metadata words contain eight shared16 exponents or four shared18
metadata bytes. Numerical probes process eight pairs per block.

All-shared16 storage is retained as a rejected comparison: it reaches **10 LSB**
on synthetic HE-AACv2, although the five real captures reach no more than 3 LSB.
This demonstrates why radio captures alone are insufficient.

## Reading the results

The [summary JSON](../tests/results/esp32c3-aac-combined-storage-20261002/summary.json)
and [comparison table](../tests/results/esp32c3-aac-combined-storage-20261002/TABLES.md)
contain all variants, corpus maxima, RMS and QEMU instruction costs. Raw logs,
source snapshots, configuration, failed cases and recording hashes are retained.

There are 345 paired comparisons: six synthetic formats (including the AAC-LC
controls) and five real captures, with three repetitions. Bypass and exact
traversal must be bit-identical. Guards, saturation/range checks, area coverage,
output rates, channels, frame shape and histogram counts are validated. The
complete batch intentionally fails because its all-shared16 comparison fails;
passing candidates are selected by their own measured maxima.

## Memory model: account for the right-channel union

The original SBR owner is **55,128 bytes**. Lossless table compaction and
PS-control relocation reduce its requested size by **5,420 bytes**. Their
separate allocator measurement is 55,296 -> 51,200 bytes (**4,096 bytes saved**).

For the mixed candidate, the persistent-layout estimate is:

| Component | Bytes |
| --- | ---: |
| Left channel after compaction | 16,960 |
| Right channel with enough space for both SBR and PS | 17,060 |
| Owner tail | 12 |
| Estimated combined owner | **34,032** |
| Difference from original 55,128-byte owner | **21,096 (20.60 KiB, 38.27%)** |

PS overlays the right SBR channel. It is not another independent allocation.
The compressed PS region reaches byte 11,700 while the compressed stereo-SBR
synthesis would begin at byte 11,600. The model therefore reserves an extra
**100 bytes on the right**, preserving the two-channel support requirement.
Adding every per-array saving would incorrectly claim 23,700 bytes.

These are **persistent-layout estimates**, before extra unpack windows, caches,
alignment beyond the modeled word boundaries, or allocator rounding. The model
assumes all affected readers/writers can use the compact layout. That adapter is
not yet implemented for the QMF and other roundtrip arrays. Thus this combined
numerical binary saves **0 allocated heap bytes**; the separately measured
4,096-byte lossless saving must not be called a measured 21,096-byte saving.

The frame-boundary smoothing probe does not qualify every within-frame FIR
write. The full native representation is restored before its consumers in this
experiment. A real compact owner must recheck precision at its actual access
boundaries and establish the required scratch/cache memory.

## Speed and next integration gate

QEMU reports guest instruction counts including the source PS port, conversion,
guards and probe counters. They are not calibrated board CPU percentages.
The complete combinations incur a substantial instruction increase, so these
probes are not promoted to production defaults. The next implementation must
reduce conversion cost and measure physical CPU, heap, full-format transitions,
reset/EOF, malformed inputs, radio networking and OTA.

Build and reproduce with the existing QEMU setup:

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-combined-storage `
  -Sdkconfig build-qemu-aac-combined-storage/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.qemu.defaults',`
    'sdkconfig.qemu-aac-packed-history.defaults','sdkconfig.qemu-aac-combined-storage.defaults')
python tools/codec_benchmark/run_aac_combined_storage.py --help
python tools/codec_benchmark/summarize_aac_combined.py `
  --results tests/results/esp32c3-aac-combined-storage-20261002
python tests/test-aac-combined-storage.py
```

The runner uses the same `--build`, `--qemu`, `--bios`, `--wsl`, `--input` and
`--output` parameters as the previous separate-area test. Raw results retain
the exact executed QEMU commands. Real recordings themselves remain local.
