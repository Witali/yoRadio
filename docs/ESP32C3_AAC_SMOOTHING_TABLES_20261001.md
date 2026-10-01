# Compact SBR smoothing tables: access audit and experiment

## Scope and mandatory rule

Before reducing any AAC allocation, identify its readers, writers, initializers,
reset paths, aliases, and lifetime across frames and format changes. Check native
instructions as well as decompiler output. A smaller `calloc` alone is unsafe.
This rule also applies to the pending QMF, hybrid, synthesis and IMDCT work.

This experiment targets only unused **pointer slots**. It keeps all four
`int32_t[5][64]` smoothing matrices, every frequency band, all five FIR terms,
and the original DSP instructions. It is QEMU-only and disabled by default.
It does not change the installed radio firmware.

## Standard check

[ISO/IEC 14496-3:2009, 4.6.18.7.6, printed pages 255–256](https://ossrs.io/lts/zh-cn/assets/files/ISO_IEC_14496-3-AAC-2009-90cda427e845cc176293bffee3f92f99.pdf#page=731)
defines a five-coefficient smoothing filter. Its summation includes indices
0 through `hSL=4`; `bs_smoothing_mode=1` disables smoothing (`hSL=0`). The same
filter applies to gain and noise. Four preceding time columns survive across
SBR frames; reset initializes them from the first new values.

Therefore five time rows suffice for this rolling-buffer implementation.
This is an implementation inference, not a standard-mandated C struct layout.
The frequency dimension remains 64. Removing pointer entries 5–63 does not
remove any required time history or subband values.

The [PacketVideo implementation](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/calc_sbr_envelope.cpp)
agrees: `maxSmoothLength=4`, first-use fill touches rows 0–3, current values use
row 4, and rotation accesses 0–4. Both enabled and disabled smoothing paths
retain this bound. Native `smoothLengths` is `{4,0}`. The header parser reads
the smoothing mode as one bit, with default 1. The reference's `[64]` function
parameter annotations decay to pointers in C/C++; they do not imply 64 time
entries are read. The struct's four allocated pointer arrays do waste space.

## Functions using the affected memory

Reviewed against the [complete pinned archive audit](audits/esp32c3-aac-full-20261001/README.md)
and its RV32 object disassembly. Archive SHA-256:
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.

| Function | Access or lifetime responsibility | Required action |
| --- | --- | --- |
| `init_sbr_dec` | Writes five entries in each of four pointer tables | Change inter-table stride 256 → 20 bytes |
| `sbr_dec` | Passes four table addresses to envelope calculation | Change table base offsets; retain all matrix storage |
| `calc_sbr_envelope` | On first use/reset fills four historical rows; supplies max history 4 | Preserve pointer-indirect accesses and all sample arithmetic |
| `envelope_application` | Reads five FIR rows, writes row 4, rotates pointers 0–4; includes both tone paths | Preserve implementation and five entries; never shorten to four |
| `sbr_open` | Clears both full channels and invokes their initializer | Change clear length, channel stride and loop endpoint |
| `sbr_read_data` | Parses SCE/CPE, copies right header, resets channels, passes PS pointer | Change right-channel and owner-tail offsets |
| `sbr_get_header_data` | Reads one-bit smoothing mode or default 1 | Prefix layout unchanged; valid mode domain remains 0/1 |
| `sbr_reset_dec` | Updates header/reset flag and frequency tables through frame prefix | Prefix unchanged; no use of discarded pointer entries |
| `sbr_get_sce`, `sbr_get_cpe`, envelope/noise parsers | Consume channel/frame prefixes supplied by caller | Prefix fields unchanged; right frame supplied at its new address |
| `sbr_applied` | Dispatches channels, stores high-QMF pointers, selects PS, assigns right synthesis V | Change every right-channel/tail address; leave DSP dimensions intact |
| `ps_allocate_decoder` | Overlays hybrid/delay storage on the right channel and assigns pointers | Move workspace addresses by new channel stride; preserve all overlay sizes |
| PS hybrid/decorrelation/mixing routines | Access overlaid storage through pointers initialized above | Arithmetic and pointed-to extents unchanged |
| `PVMP4AudioDecodeFrame` | Allocates owner and refreshes embedded PS pointer/flag | Redirect only candidate to patched offsets; intercept its allocation |
| `PVMP4AudioDecoderDeInit` | Frees owner through `core+0x8a58` | Core pointer offset unchanged; guarded allocation wrapper frees true base |
| `PVMP4AudioDecoderResetBuffer` | Has separate absolute right-channel/tail accesses and known invalid core write | **Not supported by this experiment; explicit wrapper rejects candidate calls** |
| `native_aac_decoder_process` / destroy / reopen | Handles ADTS configuration transitions by closing and reopening | Lifecycle A/B tests must cover transitions and allocation failure cleanup |

Pointer-indirect callees are safe only because their pointed-to arrays remain
the same size. This audit does not authorize shrinking their QMF, PS or transform
arrays. Those require separate access/lifetime maps before modification.

## Implemented experimental layout

Offsets below are relative to the channel's frame data, which begins at channel
offset 8. The first smoothing matrix still begins at `0x4cb8`.

| Object | Original | Candidate |
| --- | ---: | ---: |
| Four smoothing matrices per channel | 5120 B | 5120 B |
| Four pointer tables per channel | 1024 B | 80 B |
| Table bases | 0x60b8 / 0x61b8 / 0x62b8 / 0x63b8 | 0x60b8 / 0x60cc / 0x60e0 / 0x60f4 |
| Full channel stride | 25792 B / 0x64c0 | 24848 B / 0x6110 |
| SBR owner request | 55128 B | 53240 B |
| Requested saving, two channels | — | **1888 B** |

The exact allocator saving and full-radio peak saving must be measured separately.
PS control is still allocated at the tail; this experiment does not combine the
previous PS relocation or lossy packing changes.

## Results

**81 paired comparisons on eleven inputs pass with 0 LSB maximum and RMS error.**
These comprise 24 candidate comparisons and 57 control comparisons. The compact
leg produced 38,596,608 scalar PCM samples. Output rates, channel
counts, consumed input and frame counts match the original. No new rate limit or
core-only fallback is introduced. The existing implicit-SBR activation limitation
remains; a passing corpus does not qualify every possible AAC bitstream.

| Measurement | Original | Five-entry tables | Saving |
| --- | ---: | ---: | ---: |
| Requested SBR owner payload | 55128 B | 53240 B | 1888 B |
| Decoder requested payload, excluding caller/registration | 107508 B | 105620 B | 1888 B |
| Measured allocation without test guards | 55296 B | 53248 B | 2048 B |
| Measured allocation with 32-byte test guards | 55296 B | 55296 B | 0 B |
| Test registry and counters | Shared | 144 B | Test overhead |

The extra guard bytes push the compact request into the next allocator size bin.
The unguarded result is a separate allocator probe, **not a measured full-radio
peak RAM improvement**. Keep both measurements when comparing later layouts.

| Input | Max / RMS PCM error | Additional guest instructions |
| --- | ---: | ---: |
| Synthetic HE 44.1 kHz stereo | 0 / 0 LSB | +0.013% |
| Synthetic HE 48 kHz stereo | 0 / 0 LSB | +0.013% |
| Synthetic HEv2 44.1 kHz stereo | 0 / 0 LSB | +0.010% |
| ABBA 64 kbps, active PS | 0 / 0 LSB | +0.012% |
| Groove Salad 16 kbps | 0 / 0 LSB | +0.020% |
| Groove Salad 32 kbps | 0 / 0 LSB | +0.017% |
| Groove Salad 64 kbps | 0 / 0 LSB | +0.015% |
| Groove Salad 128 kbps, LC control | 0 / 0 LSB | +0.009% |

Work is the median of runs 2/3 and includes the candidate dispatch and checks;
it is not physical CPU time. Three synthetic LC inputs also pass unchanged.

Additional checks:

- Compare every retained 32-bit owner word after `sbr_open`, then after
  `ps_allocate_decoder`, translating pointer addresses between layouts. Both
  downsample flag settings pass. This caught a second initialization cursor at
  `ps_allocate_decoder+0x102`, separate from the stored delay-table pointer.
- Execute the actual vendor `envelope_application` with original 64-entry and
  guarded five-entry tables: 24 combinations of 1/32/48 bands, tone/no-tone and
  noise/no-noise paths, each across three 32-slot blocks with smoothing toggled
  on/off/on or off/on/off. QMF output, history, pointer rotation and guards match.
  This exercises enabled smoothing explicitly; the audio corpus uses mode 1.
- 21 lifecycle segments, 18 format changes and injected SBR/control allocation
  failures match, with complete owner cleanup and 1,102,848 scalar PCM samples.
  Failure injection compares the existing fallback; it does not qualify fallback
  as successful HE playback.
- Seven host regression tests validate saved evidence, hashes, expected memory
  accounting, missing/corrupted evidence rejection and fail-closed binary patches.

Raw logs, configuration, all 53 changed instruction immediates, source snapshots
and the rejected first PS-cursor trace are retained in
[`tests/results/esp32c3-aac-smoothing-20261001`](../tests/results/esp32c3-aac-smoothing-20261001/).

## Implementation and acceptance

`tools/codec_benchmark/compact_sbr_tables.py` makes build-local copies of seven
objects, changes only reviewed address/stride immediates and renames their
symbols. Archive hash, original instruction bytes, immediate bounds and absence
of overlapping relocations are checked before writing. Constants with global
symbols are also renamed to isolate the A/B legs. The SDK archive stays intact.

The [typed ABI follow-up](ESP32C3_AAC_ABI_20261001.md) replaces adapter field
offsets with named struct members. The patcher now obtains replacement offsets
from `offsetof`/`sizeof` in an RV32 compiler object. Its seven patched objects
remain byte-identical; the original evidence below retains its original source.

`qemu_aac_smoothing.c` selects the original/candidate frame controller, measures
actual guarded allocation blocks and checks both guards after decode and on free.
The patched allocator request remains intercepted at 55128 so the same failure
injection tests exercise both legs. A 53240-byte payload is actually allocated
for the candidate, plus the identical 32-byte test guards.

Required checks: exact PCM, full output format, input consumption, enabled and
disabled smoothing, active PS, lifecycle transitions, allocation-failure cleanup,
and instruction counts. Production integration additionally requires reset/API
coverage, malformed inputs, long runs, physical CPU/heap and radio/OTA tests.

## Reproduce

Run in PowerShell 7 from the repository worktree:

```powershell
& ./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-smoothing `
  -Sdkconfig build-qemu-aac-smoothing/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.qemu.defaults', 'sdkconfig.qemu-aac-packed-history.defaults', 'sdkconfig.qemu-aac-smoothing.defaults')

$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& $python tools/codec_benchmark/run_aac_smoothing.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu .build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl `
  --output .build/aac-smoothing/synthetic
& $python tests/test-aac-smoothing.py
```

Add `--input path/to/recording.aac` with a distinct output directory to compare a
continuous unmodified recording. QEMU binaries are test images, not board images.
