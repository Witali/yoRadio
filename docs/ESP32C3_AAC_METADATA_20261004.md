# Native AAC profile and channel metadata — 2026-10-04

The adapter now distinguishes HE-AAC mono from HE-AACv2 using the native
decoder's verified `sbr_present` and `ps_present` flags. Previously, mono ADTS
plus stereo PCM was taken as PS evidence. The SDK also duplicates ordinary
HE-AAC mono into two PCM channels, so that inference was wrong.

## Implementation

- The core ABI names `encoded_channels` at `0x8c`, `sbr_present` at `0xbc` and
  `ps_present` at `0xc0`. Assertions match the extended analysis view, and CMake
  rejects a different native AAC archive SHA-256 before using the private ABI.
- A successful native frame updates one byte of per-decoder metadata. The byte
  occupies existing padding. Existing reservation/compact modes reuse their
  scoped TLS state; ordinary builds use the same TLS slot for the metadata byte.
  No additional TLS slot, allocation or global decoder registry is introduced.
- Frame errors, close/reopen and explicit reset clear the observation. Partial
  network chunks preserve the last successful frame's metadata.
- OLED/WebUI receive source channels separately from PCM channels. For example,
  HE mono shows `HE-AAC 32 kHz mono` while PCM routing remains 32 kHz/two channels.
  SBR/PS retention follows actual native state, including absent/resumed SBR.
- Base/unknown AAC still uses the generic `AAC PCM` description. Absence of SBR
  alone does not identify the base AAC object type.

## Verification

The new metadata test runs the actual pinned RV32 codec in QEMU:

| Build | Metadata frames | Source cases | Reset | Adapter bytes |
| --- | ---: | --- | --- | ---: |
| Ordinary native | 93 | AAC-LC, HE stereo, HE mono, HEv2 | Reopen | 28 |
| Full-precision history reference | 104 | Same | Reopen and explicit reset | 44 → 44 |
| PC19 with context metadata | 104 | Same | Reopen and explicit reset | 204 → 204 |

The tests check every successful frame, split headers/payloads into network
chunks, keep a second PS decoder alive while another decoder changes formats,
and verify duplicated mono PCM pairs. Expanded SBR-gap and late-activation tests
also check labels/source channels throughout the transitions.

The complete Groove Salad 16 recording reports **HE-AAC mono, 32 kHz, two PCM
channels**, from frame zero through all 469 frames. Its earlier FFprobe HE-AACv2
classification is retained in historical provenance, but does not override the
verified native PS state.

### PCM regression against the same storage implementation before this fix

| Comparison | Signed-16 channel samples | Changed samples | Maximum error |
| --- | ---: | ---: | ---: |
| Full-precision reference, absent/resumed SBR | 675,840 | 0 | 0 LSB |
| Full-precision reference, late SBR | 189,440 | 0 | 0 LSB |
| PC19, absent/resumed SBR | 675,840 | 0 | 0 LSB |
| PC19, late SBR | 189,440 | 0 | 0 LSB |
| PC19, complete Groove Salad 16 | 1,921,024 | 0 | 0 LSB |
| **Total** | **3,651,584** | **0** | **0 LSB** |

No alignment, resampling, gain adjustment or startup trimming is applied.
This establishes that the metadata change preserves PCM; PC19's separate
compact-vs-original precision qualification remains in its existing reports.

PC19 gap decode work is 252,439,833 guest instructions versus 252,432,273 before
the change (about +0.003% in this instrumented run). This is not physical CPU
utilization. The 16 KiB decoder task retains a 2,844-byte minimum stack margin;
the run completes 1,600,361 pointer checks with 565 allocations and 565 frees.

Host tests under ASan/UBSan execute the production audio callback, WebUI status
formatter and OLED formatter. They verify source mono/PCM stereo separation and
the following transition to PS stereo, alongside existing framing, buffer/OOM,
reservation ownership and cleanup checks.

## Evidence and reproduction

[Saved evidence](../tests/results/esp32c3-aac-metadata-20261004/) includes configs,
diagnostic logs, exact source snapshots, pre/post comparisons and synthetic PCM.
Radio PCM/source audio remain local; their input/log/output hashes are retained.

```powershell
python tools/codec_benchmark/run_aac_metadata.py `
  --build idf/esp32c3-oled-native/build-qemu-aac-metadata-pc19 `
  --dependency-root C:/Work/yoRadio/.idf --output .build/aac-metadata-repeat `
  --qemu /path/to/qemu-system-riscv32 --bios /path/to/qemu/share --wsl
python tests/test-aac-metadata.py
# Linux/WSL:
# C3_MEMORY_SANITIZE=1 python3 tests/run-esp32c3-stream-format.py
```

Use the saved SDK configuration for the selected build and the repository's
existing `build.ps1` wrapper. Metadata-only success is explicitly distinguished
from PCM qualification by the runner. Reproduce the exact PCM comparison with
`save_aac_metadata_evidence.py --help` and the retained local recording/logs.

The physical board has not been reflashed for this check. OLED/browser behavior
on the board, real Wi-Fi/HTTPS/OTA load, malformed-input coverage and all-codec
acceptance remain open. PC19 and late-SBR production defaults are unchanged.
