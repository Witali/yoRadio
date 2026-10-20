# CYD custom FLAC: ESP32 SDK/QEMU adapter and core

The final standalone Windows harness passed **520 unique exact PCM16 cases**
and **48 guard/recovery checks** using pinned ESP-IDF 6.0.2 and the installed
Xtensa QEMU. A single actual SDK decoder owner runs on core 1; its coordinator
runs on core 0. Every callback compares all PCM bytes against a separately
FFmpeg-verified oracle and validates depth, channels, rate, alignment and bounds.

There are 120 small fixtures and 10 fixtures with an 8192-frame block plus short
tail. Tested source depths are 4, 8, 12, 16, 20 and 24 bits, with mono, independent
stereo and three side-channel assignments. Each fixture runs with whole-input,
1-byte, 127-byte and 2048-byte schedules. Encoded source depth and delivered
PCM16 depth are checked separately. QEMU must produce every unique case and
the complete marker and terminate with exit zero; timeout/panic/watchdog,
heap failure, missing/duplicate cases and mismatches fail the gate.

The additional guards are 42 truncated STREAMINFO prefixes (0–41 bytes),
invalid signature, 65537-byte metadata, 65537-byte frame window, callback abort,
separate zero-byte EOF and clean reopen: 48 checks. Destruction must leave zero
core workspace and valid SDK heap integrity. The explicit oversized-metadata
error in `qemu.log` is an expected negative-input guard.

## Evidence map

| Path | Meaning |
| --- | --- |
| `report.json` | Unmodified final runner report and all 520 parsed cases. |
| `execution-bundle.json` | Unmodified source/fixture/tool/ROM/config/ELF/image hash bundle written before QEMU. |
| `sources/harness/` | Frozen target project, SDK build helper and harness README. |
| `sources/runner/` | Frozen actual Python runner. |
| `sources/repository/` | Unchanged production adapter/core/compatibility and fixture generator bytes. |
| `fixtures/`, `fixture-manifest.json`, `fixtures.bin` | Actual encoded fixtures, independent PCM16 oracles and the exact data-partition blob. |
| `build/`, `sdkconfig`, `qemu-flash.bin` | Bound standalone test ELF/app, compiler database, partition/config metadata and disposable 4 MiB flash image. |
| `*.log` | Original build, merge, version, SDK-state and emulator stdout logs. |
| `qualification.json` | Archive map and before/after live/bound-input hash verification. |
| `history/` | Clearly historical tracked-01 report/bundle and portable-tool preflight-02. |
| `archival/archive.py` | Archive procedure; original evidence is copied byte-for-byte. |
| `manifest.json` | Size and SHA-256 of every archive file except this self-index. |

Runtime executable and ROM bytes are deliberately not copied: their exact hashes
and version logs are retained. Absolute paths in original evidence identify the
run environment; archived bundle-relative paths retain the same byte content.
The archive binds SDK commit `7101770dc6db2667b3c477cc31365dd1acd6db4e`, real
Xtensa ELF/image identity, nonoverlapping factory/data partitions, bootloader
offset `0x1000` and a checked 4 MiB merged flash. These are standalone test images,
not production firmware and not intended for automatic flashing.

## Scope and remaining gates

This executes the shared adapter/core with real SDK FreeRTOS/heap/timers in an
emulator. It does **not** run the actual CYD `decoder_task` or its maintenance/
queue lifecycle, inject OOM, execute deliberate semantic-mutant target controls,
or qualify physical vendor/custom A/B, RF, DMA/I2S, full-radio resource margins,
power or physical timing/stack behavior. Those gates remain open. The six tested
depths are not all 21 possible integer depths from 4 through 24. No full FLAC
CRC/MD5/malformed-stream standard conformance is claimed. Debug guards and
DIO/40 MHz flash settings belong only to this isolated test profile; emulator
heap/stack observations do not establish production budgets or performance.
