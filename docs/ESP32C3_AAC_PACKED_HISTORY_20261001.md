# ESP32-C3 AAC: packed complex history (14 + 14 + 4)

## Decision and current accuracy requirement

Implemented a **QEMU-only numerical qualification** of the proposed 32-bit
complex representation in the shipped Espressif decoder. It is **rejected for
production**: errors reach **3 signed-16 PCM LSB on real radio recordings** and
**7 LSB on the synthetic HE-AAC v2 fixture**. Midpoint reconstruction does not
remove these exceedances. No board was flashed and actual RAM saved is **0 bytes**.

On 2026-10-01 the user increased the allowed error to **±2 LSB for every decoded
sample in every channel**. This is a maximum absolute error, not an RMS or a
percentile limit. The user subsequently allowed **±5 LSB during development**;
the final requirement remains ±2. Both thresholds are checked independently,
alongside the historical >1 LSB counts. Real recordings pass the temporary gate,
but the synthetic seven-LSB case still fails it. Historical BFP16 evidence
keeps its original one-LSB gate; its observed three-LSB errors also exceed the
new limit. Full existing AAC format/rate/channel support and eventual recovery
of any decoding slowdown remain requirements.

The development profile enables `CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST=y`
and defaults `CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_ERROR_LIMIT=5`. This is a
numerical test option. The requested default-on **production storage** option
remains unimplemented: the current adapter does not release RAM, and the complete
corpus fails even the temporary accuracy gate. A switch must not silently claim
compact allocations while retaining the original 55,128-byte binary layout.

The proposal came from `esp32c3_he_aac_v2_memory_handoff_en.md`, SHA-256
`75b45a6d636196f9a48d339ea6d8f6ccd0cd375d33aac7c4969b6e10f1fe69a5`.
Its FAAD2 measurements and CPU estimates describe another implementation and
were not independently reproduced here. They do not qualify our fixed-point
Espressif backend.

The subsequent [pinned FAAD2 source and scaling comparison](FAAD2_HISTORY_SCALING_20261001.md)
implements a separate 60-case host comparison. It follows the supplied fixed/full
SBR/PS build recommendation, measures the factor-512 signal scale and preserves
overflow-invalid trials. It does not reproduce the original study's unavailable
integration code or replace the firmware backend.

### Why the supplied study reports smaller errors

An exact cause is not established without its original quantizer/integration
code, FAAD2 build settings and AAC input. Two quantitative differences are
visible from the supplied numbers, assuming conventional SNR and full-scale
normalization and that the table/counts describe the same signal:

1. `signal_RMS = 8.209e-8 * 10^(100.626/20) = 0.008822 FS`, about **−41.09 dBFS**.
   Our ABBA reference is **−14.19 / −13.60 dBFS** on L/R, roughly 22–24 times
   larger in amplitude. Floating-exponent storage can preserve similar relative
   precision while creating larger absolute PCM errors on louder material.
2. Its 234 differing int16 samples out of 274,432, all of magnitude 1, imply
   `sqrt(234/274432) = 0.02920 LSB` error RMS. At the inferred signal level this
   would be about **79.91 dB int16 SNR**, not 100.626 dB. The latter therefore
   appears to describe the output **before** final int16 rounding. Our saved
   per-channel SNR uses actual int16 differences (ABBA nearest/both: about
   83.69 / 84.21 dB). These SNR values must not be compared as the same metric.

The study's pre-int16 peak error, `1.393e-6 FS`, is about **0.04565 PCM LSB**;
even that can flip final rounding for samples close to a boundary. Different
decoder scaling, histories, signal content and test length can also affect the
maximum. Their contributions have not been isolated. The supplied maximum of
1 LSB can be valid for that recording without guaranteeing ±2 LSB on our corpus.
Neither scaling the compared output down after decoding nor matching only a
mean/SNR would satisfy the current per-sample requirement.

## Representation and integration

- Word layout: bits 31..28 exponent, 27..14 signed Im14, 13..0 signed Re14.
  `shift = exponent + 3`, from 3 to 18. One complex pair occupies 4 bytes instead
  of 8. Masks and shifts define the ABI; there are no C bitfields.
- **Nearest:** choose the smallest shift whose rounded mantissas fit
  `[-8192, 8191]`; ties round away from zero. At shift 18 a positive rounding
  carry saturates to 8191. Saturations are counted.
- **Midpoint:** packing uses mathematical floor, including negative inputs,
  then reconstruction is `mantissa * 2^shift + (mantissa != 0 ? 2^(shift-1) : 0)`.
  This is not truncation toward zero. Exact zero stays zero, but the quantizer
  is asymmetric near zero: at shift 3, +1 becomes 0 and -1 becomes -4.
- `packed_complex14.h` implements both modes without signed shifts, signed
  overflow, `abs(INT32_MIN)` or implementation-defined unsigned-to-signed casts.
  Arithmetic remains `int32_t`; quantization is applied only at frame boundaries.

`qemu_aac_packed_history.c` wraps `sbr_dec`, calls the real function first and
packs/restores its **retained** complex values. Newly computed current-frame
QMF rows, real-only LC-SBR state, synthesis state, energy envelopes, gains,
indices and pointers are not quantized. AAC-LC has no SBR hook work.

The wrapper is pinned to the C3 AAC archive SHA-256
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.
The host runner rejects a different archive. Its eight-argument ABI and offsets
come from the retained [disassembly](audits/esp32c3-aac-decompile-20260930/disassembly/sbr_dec.txt),
[SBR pseudocode](audits/esp32c3-aac-decompile-20260930/pseudocode/sbr_dec.c) and
[PS allocation pseudocode](audits/esp32c3-aac-decompile-20260930/pseudocode/ps_allocate_decoder.c),
cross-checked with the PacketVideo source used by the
[decompilation audit](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md).

### Typed history coverage and potential payload saving

Offsets below are relative to `SBR_FRAME_DATA`, unless labelled PS. They are
private to the pinned binary, not public SDK struct definitions.

| Retained data | Complex pairs | Original bytes | Packed bytes |
| --- | ---: | ---: | ---: |
| SBR low QMF: 8 × 32, Re `0x11b0`, Im `0x25b0` | 256 | 2,048 | 1,024 |
| SBR high QMF: 6 × 48, Re `0x3e38`, Im `0x39b4` | 288 | 2,304 | 1,152 |
| PS QMF delays: 20 × 2, 12 × 14, 29 × 1 | 237 | 1,896 | 948 |
| PS sub-QMF delays: 10 × 2 | 20 | 160 | 80 |
| PS serial all-pass QMF: (3 + 4 + 5) × 20 | 240 | 1,920 | 960 |
| PS serial all-pass sub-QMF: (3 + 4 + 5) × 10 | 120 | 960 | 480 |
| PS hybrid filter: 3 × 12 | 36 | 288 | 144 |
| **One complex SBR channel plus PS** | **1,197** | **9,576** | **4,788** |

PS tables are at offsets `0x1a0/0x1ac`, `0x1b8/0x1c4`, `0x1d0/0x1d4`,
`0x1d8/0x1dc` and hybrid handle `0x1fc`. They reference the second SBR channel's
shared window, owner offsets `[0x7678, 0x93b4)`. The wrapper checks the owner,
alignment, table/data bounds, hybrid dimensions, linked `{3,4,5}` delay constants
and non-overlap of all sample spans. It asserts exactly 544 SBR pairs and 653 PS
pairs per corresponding active frame. A separate lossless traversal checks the
same addressing with PCM unchanged.

The **4,788-byte saving is theoretical**, before workspace and allocator costs.
The binary still reserves its original arrays, so pack/restore does not release
heap. Implementing actual packed storage requires a compatible source/layout
change. A new four-slot scratch cache would use 2,048 bytes and reduce this
payload-only benefit to 2,740 bytes if no existing scratch could be reused.
No cache or smaller allocator request was added after the precision rejection.
This candidate alone would not resolve the recorded ~20 KiB SBR memory deficit.

## Measurements and coverage

The [retained results](../tests/results/esp32c3-aac-packed-history-20261001/)
contain raw logs and JSON, including input, ELF, SDK config, codec and log hashes.
There are **201 paired comparisons**: 81 synthetic and 120 from five previously
captured 30-second radio recordings, three runs per configuration. The same
source bytes are fed to separate baseline/candidate decoders. Raw PCM is compared
before normalizing, resampling or PDM, without alignment or gain correction.
Consumed bytes, output lengths, rate, channels, 16-bit format and output-buffer
canaries must match. Existing baseline in-stream format regressions run too.

Variants 1/2/3 use nearest on SBR/PS/both; 4/5/6 use midpoint on SBR/PS/both;
7 traverses both histories without quantizing and 0 bypasses the wrapper.
An inactive history path is reported as **not exercised**, not a successful
quantizer qualification. In particular, the real HE-AAC v1 files use the real-only
LC-SBR path. The Groove Salad 16 kbps recording is identified as HE-AAC v2 by
FFprobe, but this backend did not enter the wrapped PS path on that recording;
its PS-only results are controls. ABBA and the synthetic HE-AAC v2 fixture do
exercise PS, including delayed activation in ABBA.

Per-channel JSON includes exact error histograms through 4,095 LSB, larger
bounded bins, maximum/location, MAE, RMS, signed bias, signal/error ratio,
percentiles, clipping, identical-sample fraction and >1/>2 LSB counts.
Quantizer diagnostics include exponent and component-ratio histograms,
saturation, nonzero-to-zero, zero-to-nonzero, near-zero changes and Re/Im bias.
Both modes preserve exact zero, and no recorded input saturated the quantizer.

See [TABLES.md](../tests/results/esp32c3-aac-packed-history-20261001/TABLES.md)
for the measured error and instruction comparisons. The maximum is not inferred
from SNR; even a rare three-LSB error fails the two-LSB requirement.

### Timing interpretation and speed follow-up

QEMU counts guest instructions with `icount` and validates `1024 NOPs = 1025`
counter difference. Run 1 collects extra QMF diagnostics and performs quadratic
span-overlap checks; **only runs 2/3 contribute to timing summaries**. Those runs
still include packing, unpacking, pointer construction, bounds assertions and
basic coverage counters. Counts are neither pure quantizer cost nor hardware CPU
load. The old hardware calibration factor is not automatically applied to new
packing code, and no cache/write-back performance claim is made.

Before production: find a representation/scope satisfying ±2 LSB, then replace
the shift search with a checked leading-bit estimate, fuse packing with existing
history copies, reuse stage-local scratch and remove diagnostic-only counters
from performance builds. Repeat raw PCM checks, measured net/peak RAM and physical
C3 speed/latency/underrun tests. Retain full SBR/PS support and recover speed.
Increasing mantissa precision or using selective wider storage needs a new
accuracy experiment; this result does not establish a safe reduced width.

## Reproduce

The subsequent [16+16 exponent-range decision and block API](ESP32C3_AAC_PC16_SHIFTS_20261001.md)
selects shifts 1..16 and packs eight independent exponent nibbles per word. Its
arithmetic checks do not change the 14-bit measurements in this report or qualify
the new format's PCM accuracy.

From this worktree, with the already-installed ESP-IDF dependencies (PowerShell):

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& ./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-packed-history `
  -Sdkconfig build-qemu-aac-packed-history/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.qemu.defaults', 'sdkconfig.qemu-aac-packed-history.defaults')

& $python tools/codec_benchmark/run_aac_packed_history.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu .build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl `
  --output .build/aac-packed-history/synthetic
```

For a real ADTS recording add `--input path/to/recording.aac` and optionally
`--source-url URL` (provenance only; no network access). FFprobe must be on PATH.
The runner writes the recording only into its disposable QEMU flash image.
Exit 0 means this input met the numerical gate, 2 means measured precision
rejection, and other failures indicate an incomplete/broken harness. A passing
control with no active packed history cannot qualify the representation.

```powershell
& $python tests/test-aac-packed-history.py
& $python tests/test-aac-bfp16.py
& $python tests/test-aac-bfp16-real.py
```

The arithmetic tests execute the actual RV32 quantizer: all 16,384 mantissa codes
at every exponent in both modes, int32 extrema, rounding/exponent boundaries,
zero/near-zero pairs, a fixed word-layout vector and 16,384 random pairs against
an independent int64 division oracle. Host tests validate the retained results
and reject missing/duplicated cases, false precision labels, corrupted history
coverage and inconsistent histograms. The original BFP16 QEMU harness is rebuilt
and rerun; its PCM results remain unchanged after sharing the comparison runner.

Neither the emulator image nor these isolated decoder tests qualify full-radio
heap, OTA, networking, hardware timing or every legal AAC bitstream.
