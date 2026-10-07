# Lossless SBR owner reduction — 2026-10-01

## Result

The first allocation-reducing implementation moves PS control state into unused
right-channel storage while PS is active. All DSP and sample representations
remain native. **81 paired comparisons on eleven inputs are bit-exact (0 PCM
LSB error).** This is a QEMU-only prototype, not a production firmware change.

| Metric | Original | Relocated PS | Difference |
| --- | ---: | ---: | ---: |
| SBR requested payload | 55128 B | 51596 B | −3532 B |
| Total decoder requested payload | 107508 B | 103976 B | −3532 B |
| Measured SBR heap block, including identical guards | 55296 B | 53248 B | **−2048 B** |
| Test adapter static state | Shared harness | 144 B total | Must account separately |
| Maximum PCM error against original | — | 0 LSB | Bit-exact |

Total payload excludes callers, registration and allocator overhead. Block sizes
are measured with `heap_caps_get_allocated_size`; both legs have 32 guard bytes.
Allocator rounding consumes part of the requested saving. The test registry and
counters occupy 144 bytes in this RV32 executable. Subtracting that entire state
from the block saving gives 1904 bytes, but **neither number is a measured net
full-radio RAM gain**. Production heap/stack and peak playback RAM still need
measurement. Do not add the earlier packed-delay payload saving to these values.

## Layout and lifetime

The pinned SBR allocation contains two 25792-byte channels, stream metadata at
`0xc980`, a PS pointer at `0xc984`, and 3536 bytes of PS control at `0xc988`.
Retain four bytes at the old tail as an inactive PS flag. On the first PS read,
move control into `[0x93b4, 0xa184)`, after PS delay/hybrid storage and before
right synthesis V at `0xa780`. Right-channel SBR envelope/QMF workspace is unused
for the mono AAC core with PS. Full stereo SBR uses its native workspace and the
small inactive sentinel. No lossy packing is required for this saving.

The wrapper restores the PS pointer before each `sbr_applied` call because the
vendor frame controller refreshes it. Owner guards are checked before/after
processing and on free. The private ABI is pinned to archive SHA-256
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.
The global selector/active owner supports the sequential test harness only;
it must be replaced with production lifetime ownership before integration.

## Quality and work measurements

Each comparison runs three times. Instruction overhead is the median of runs
2/3, including wrappers and checks but excluding PCM comparison. These are guest
instructions, not physical CPU percentages or cache-corrected timing.

| Input | Max / RMS error, LSB | Extra instructions | SBR block saving |
| --- | ---: | ---: | ---: |
| LC 22.05 kHz mono | 0 / 0 | +0.007% control | 0 B |
| LC 44.1 kHz stereo | 0 / 0 | +0.000% control | 0 B |
| LC 48 kHz stereo | 0 / 0 | +0.000% control | 0 B |
| HE 44.1 kHz stereo | 0 / 0 | +0.010% | 2048 B |
| HE 48 kHz stereo | 0 / 0 | +0.010% | 2048 B |
| HEv2 44.1 kHz stereo | 0 / 0 | +0.012% | 2048 B |
| ABBA 64 kbps, active PS | 0 / 0 | +0.011% | 2048 B |
| Groove Salad 16 kbps | 0 / 0 | +0.017% | 2048 B |
| Groove Salad 32 kbps | 0 / 0 | +0.013% | 2048 B |
| Groove Salad 64 kbps | 0 / 0 | +0.013% | 2048 B |
| Groove Salad 128 kbps, LC | 0 / 0 | +0.004% | 0 B |

Zero RMS follows from every compared sample being equal; explicit per-channel
moments and histograms are also retained for recordings. Output shapes, rates,
channels and consumed bytes match. No 22 kHz cap or new AAC-core fallback is used.
The 16 kbps recording retains the baseline decoder's 32 kHz duplicated stereo;
its FFprobe HEv2 label does not prove active PS in this decoder.

## Lifecycle tests and remaining gates

- Three cycles of HEv2 → HE44 → LC48 → HE48 → LC22 → LC44 → HEv2, fed in
  193-byte chunks: 21 segments, 18 format changes and 1102848 scalar PCM samples
  match. The native adapter closes/reopens its codec when ADTS configuration changes.
- Injected failures of the 55128-byte SBR and 1180-byte control allocations:
  baseline and candidate behavior/PCM match, guards and owner cleanup pass.
  These paths exercise the library's existing 22050 Hz mono fallback; they do
  **not** qualify successful full-rate HE decoding under low memory.
- All paired instances close with zero remaining owners. Each input also checks
  native/native control and binary bypass. ABBA includes delayed PS activation.
- Direct vendor reset is **not qualified**. Full decompilation found a suspect
  write at `core + 0x153dc` in `PVMP4AudioDecoderResetBuffer`, beyond the current
  35460-byte core allocation. The radio adapter currently uses close/reopen.
  Reproduce this safely and repair/reset-test before production integration.
- Same-core implicit PS/stereo transitions, unusual PS tools, malformed streams,
  long runs, full-radio peak heap, physical CPU time, Wi-Fi playback and OTA
  remain acceptance gates. Corpus equality does not prove all legal streams.

## Reproduce

```powershell
& ./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-sbr-layout `
  -Sdkconfig build-qemu-aac-sbr-layout/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.qemu.defaults', 'sdkconfig.qemu-aac-packed-history.defaults', 'sdkconfig.qemu-aac-sbr-layout.defaults')

$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& $python tools/codec_benchmark/run_aac_sbr_layout.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu .build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl `
  --output .build/aac-sbr-layout/synthetic
& $python tests/test-aac-sbr-layout.py
```

Add `--input path/to/recording.aac` and use another output directory for recordings.
The runner never accesses a board. Raw logs, hashes, configuration, implementation
fingerprints and error statistics are saved under
[`tests/results/esp32c3-aac-sbr-layout-20261001`](../tests/results/esp32c3-aac-sbr-layout-20261001/).
The [full archive decompilation](audits/esp32c3-aac-full-20261001/README.md) covers
186 functions, including unreferenced and optimized filter-bank objects.
