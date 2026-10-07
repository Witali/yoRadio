# ESP32-C3: FAAD-style packed PS history in the current decoder

**Current policy (2026-10-02): production permits +/-3 PCM LSB; development permits +/-5.**
The older acceptance statements below describe the limits at measurement time.
Measured errors and archived evidence are unchanged. See [current precision policy](ESP32C3_AAC_PRECISION_POLICY.md).

## Result

Ported the supplied FAAD patch's **14+14+4 midpoint storage strategy** to the
current Espressif AAC decoder's actual PS delay writes. This executable RV32/QEMU
experiment includes feedback writes inside each decorrelation call. Native DSP
arithmetic and other AAC/SBR processing retain their representation. It does not
switch the firmware to FAAD.

**81 paired comparisons pass the temporary ±5 PCM LSB limit. The maximum is
3 LSB, so the final ±2 requirement still fails.** The source replacement with
compression disabled is bit-identical to the binary on all eleven inputs.
Production firmware and the physical board were not changed.

## Implementation

`CONFIG_YORADIO_QEMU_AAC_PS_HISTORY_PORT_TEST` selects the experiment; it is
QEMU-only, default off and mutually exclusive with the PC16 experiment. Link
wrappers replace `ps_decorrelate` and initialize packed delays after
`ps_allocate_decoder`. A build-time archive hash pins the private ABI.

The four delay families store one 32-bit word per complex pair: signed real and
imaginary 14-bit cell indices plus a shared four-bit exponent. The shift is
`exponent + 3` (3..18); nonzero cells reconstruct at the midpoint. Zero remains
zero. This uses `PC14_MIDPOINT`, previously checked against the
[supplied FAAD patch](FAAD2_PS_PATCH_QUALITY_20261001.md), not the PC16 format.

All-pass feedback, QMF delays and sub-QMF delays pack on each write and unpack
on each read. Hybrid analysis histories, QMF work buffers, energy tracking,
mixing coefficients and full-rate SBR synthesis are unchanged. Original integer
multiply-high, shifts, wrapping additions and coefficient tables are preserved.
The native-source control verifies that arithmetic against the pinned binary.
The earlier [history experiment](ESP32C3_AAC_PACKED_HISTORY_20261001.md) quantized
at frame boundaries, without these within-frame writes and feedback loops.

## Measurements

Counts are scalar signed-16 PCM samples across channels, from one run. Three runs
reproduce the same errors. Synthetic files repeat twice; each unchanged radio
capture runs once. No normalization, resampling or alignment adjustment is applied.

| Input | Packed PS exercised | Max error, LSB | Samples beyond ±2 | Samples compared | RMS L / R, LSB | Extra guest instructions |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| Synthetic LC 22.05 kHz mono | No; native control | 0 | 0 | 26624 | Not collected | +0.007% |
| Synthetic LC 44.1 kHz stereo | No; native control | 0 | 0 | 98304 | Not collected | +0.000% |
| Synthetic LC 48 kHz stereo | No; native control | 0 | 0 | 106496 | Not collected | +0.000% |
| Synthetic HE 44.1 kHz stereo | No | 0 | 0 | 114688 | Not collected | +0.000% |
| Synthetic HE 48 kHz stereo | No | 0 | 0 | 122880 | Not collected | +0.001% |
| Synthetic HEv2 44.1 kHz stereo | Yes | 3 | 11 | 122880 | Not collected | +26.681% |
| ABBA 64 kbps | Yes | 3 | 2542 | 2646016 | 0.531375 / 0.526306 | +40.658% |
| Groove Salad 16 kbps | No | 0 | 0 | 1921024 | 0 / 0 | +0.000% |
| Groove Salad 32 kbps | No | 0 | 0 | 2646016 | 0 / 0 | +0.000% |
| Groove Salad 64 kbps | No | 0 | 0 | 2646016 | 0 / 0 | +0.000% |
| Groove Salad 128 kbps | No | 0 | 0 | 2646016 | 0 / 0 | +0.004% |

No sample exceeds ±5. Both channels reach 3 LSB on the active-PS inputs. FAAD's
corresponding experiment reached 2 LSB, but its arithmetic, scaling and delay
layout differ. Reusing its packing rule does not establish the same error bound
in the Espressif decoder.

Groove Salad 16 kbps has no active PS here despite the FFprobe HEv2 label. It
remains 32 kHz duplicated stereo in the current decoder. Other retained HE
recordings and fixtures keep full 44.1/48 kHz output. No 22 kHz ceiling or
AAC-core fallback is introduced.

## Storage accounting

| Espressif PS delay family | Complex pairs | Native bytes | Packed bytes |
| --- | ---: | ---: | ---: |
| Main QMF: 20×2 + 12×14 + 29×1 | 237 | 1896 | 948 |
| Sub-QMF: 10×2 | 20 | 160 | 80 |
| QMF all-pass: (3+4+5)×20 | 240 | 1920 | 960 |
| Sub-QMF all-pass: (3+4+5)×10 | 120 | 960 | 480 |
| **Total** | **617** | **4936** | **2468** |

Delay payload shrinks by **2468 bytes (50%)**, but **actual heap saving is zero**.
Packed pairs live in existing real-array words. Unused imaginary words hold
guards checked after each comparison. The enclosing **55,128-byte SBR allocation
remains unchanged**. This is not FAAD's 2400-pair layout; its 9600-byte structure
saving does not transfer to this decoder.

Espressif already overlays PS delays on right-channel SBR storage. Reclaiming
heap needs a complete layout/ownership change covering other users of those
offsets and stereo/PS transitions; reducing the allocation alone is unsafe.
The 36-pair hybrid analysis history included in earlier probes is excluded here,
matching the supplied patch's delay-only scope.

## Controls, timing and limits

- Variant 7: source replacement with native storage; every PCM sample matches
  the binary. Variant 0: binary bypass; also bit-identical.
- Variant 1: packed writes, per-call/store counters and 617 guarded pairs per
  initialized PS owner. Unused imaginary words retain their guards.
- The RV32 arithmetic check covers 100000 deterministic pairs. The paired
  harness checks consumed bytes, output size/rate/channels/bit depth and output
  guards. Recording logs retain per-channel error moments and histograms.
- The 36 synthetic and 45 recording comparisons use fresh decoder lifetimes.
  ABBA includes delayed PS activation. The test-only owner registry assumes the
  harness lifetime and global variant selection; it is not a concurrent adapter.
- Timing is median **QEMU guest instructions** from runs 2/3. PCM comparison and
  first-run quantizer diagnostics are excluded. Wrapper dispatch, assertions and
  counters remain included. Native-source PS adds 6.847% on synthetic HEv2 and
  7.132% on ABBA; packed storage adds 26.681% and 40.658% against the binary.
  These are neither physical CPU percentages nor cache-corrected times; no
  hardware calibration factor is applied.
- The baseline format-transition suite passes in the same executable but does
  **not** enable this packed variant. Packed PS→stereo→PS transitions,
  reset/seek/reconfigure on the same decoder, malformed/adversarial inputs,
  wider PS tools, long runs and physical Wi-Fi/OTA playback remain unqualified.
  This corpus pass does not prove a bound for every legal stream.

Before production: remove the ±2 exceedances, reclaim owner storage, qualify
lifetime/format paths and recover the speed regression by reducing dispatch and
scanning work and fusing packing with producing stages. Then measure full-radio
heap/stack, physical decode time and underruns.

## Provenance

Espressif `esp_audio_codec` 2.6.2 archive SHA-256:
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.
The [decompilation audit](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md) provides the
private layout. Public reference algorithms are PacketVideo's
[PS decorrelation](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/ps_decorrelate.cpp)
and [all-pass filters](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/ps_all_pass_fract_delay_filter.cpp)
at revision `437ced8a14944bf5450df50c5e7e7a6dfe20ea40`. Notices are retained in the
port. Espressif arithmetic and field-order differences are adapted explicitly;
reference source is not assumed ABI-compatible.

Logs, error statistics, input/ELF/config hashes, implementation fingerprints and
PacketVideo source hashes are retained in
[`tests/results/esp32c3-aac-ps-port-20261001`](../tests/results/esp32c3-aac-ps-port-20261001/).
Test ELF and disposable flash images remain in ignored build directories.

## Reproduce

With the installed IDF dependency root, pinned codec and Linux QEMU:

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& ./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-ps-port `
  -Sdkconfig build-qemu-aac-ps-port/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.qemu.defaults', 'sdkconfig.qemu-aac-packed-history.defaults', 'sdkconfig.qemu-aac-ps-port.defaults')

& $python tools/codec_benchmark/run_aac_ps_history_port.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu .build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl `
  --output .build/aac-ps-port/synthetic

& $python tests/test-aac-ps-history-port.py
```

For a recording add `--input path/to/recording.aac` and a separate output directory.
The runner never accesses a board. Exit 0 means the development gate passed;
exit 2 records a precision failure and exit 1 indicates a harness failure.
Inspect `production_precision_pass` for the final ±2 gate.
