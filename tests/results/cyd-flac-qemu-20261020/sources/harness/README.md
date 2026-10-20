# CYD custom FLAC on Xtensa QEMU

This Windows harness executes the unchanged shared custom FLAC adapter/core
with ESP-IDF 6.0.2 on the emulated classic, dual-core ESP32. One decoder owner
runs on core 1; the coordinator runs on core 0. Real SDK FreeRTOS, heap poisoning,
stack canaries and timers are used. PCM is compared inside the decoder callback;
the test does not use an emulated DAC or a physical serial port.

The matrix has 120 small fixtures plus 10 fixtures with an 8192-frame block and
a short tail. The six tested source depths are 4, 8, 12, 16, 20 and 24 bits.
Fixtures cover mono, independent stereo, left/side, right/side and mid/side;
constant, verbatim, fixed-order-4 and LPC-order-32 subframes are included.
Each independently FFmpeg-verified signed PCM16 oracle is tested with whole-input,
1-byte, 127-byte and 2048-byte feed schedules: 520 unique cases. Every emitted
PCM byte and the final complete byte count must match. The callback separately
checks encoded source depth, PCM16 depth, channels, rate, alignment and bounds.

Run from the repository root with installed dependencies:

```powershell
python tests/run-cyd-flac-qemu.py --output .build/cyd-flac-qemu-check
```

Use `--idf`, `--idf-tools`, `--idf-python`, `--qemu`, `--rom-directory`,
`--ffmpeg` and `--powershell` to select existing installations. Defaults match
the current Windows workspace. SDK commit
`7101770dc6db2667b3c477cc31365dd1acd6db4e` is required, with no tracked SDK
changes. Dependencies are never installed or downloaded. Build and emulator
timeouts default to 600 and 480 seconds and are configurable.

The output must be fresh, below repository `.build/` or outside repository
sources. Resolved paths protect source, SDK, tool and ROM directories. All builds
use frozen production component and harness copies in the output, including
this README. The factory/data partitions and disposable flash image fit 4 MiB;
the classic ESP32 bootloader starts at `0x1000`. The data partition holds both
encoded fixtures and expected PCM. Output contains source/fixture snapshots,
compiler/tool/ROM hashes, exact commands and logs, configuration, ELF, image and
an execution bundle written before QEMU starts. Bound inputs are checked again
after all cases complete. Missing/duplicate cases, mismatch, timeout, panic,
watchdog, heap failure, incomplete output or nonzero emulator exit fail the run.

The same owner then executes 48 guard/recovery checks:

| Guard | Checks | Required behavior |
| --- | ---: | --- |
| Truncated STREAMINFO at EOF | 42 | Prefix lengths 0–41 reject without PCM; destruction frees workspace. |
| Invalid FLAC signature | 1 | Reject before emitting PCM. |
| Oversized metadata | 1 | Reject a 65537-byte declaration; its explicit error log is expected. |
| Oversized frame window | 1 | Reject a 65537-byte frame-window declaration. |
| Callback abort | 1 | One byte-verified callback returns false; feed returns `-8`; destruction cleans up. |
| Separate zero-byte EOF | 1 | 127-byte feeds followed by null/zero/EOS produce complete exact PCM. |
| Reopen after guards | 1 | A fresh ordinary decode produces complete PCM and clean destruction. |

Actual callback assertions detect source/PCM depth confusion, wrong metadata,
misalignment, output overflow and byte mismatch. Coordinator assertions reject
duplicate case IDs/schedules, incomplete PCM or a missing guard completion.
Heap integrity and zero core workspace are checked after each destruction.
These checks are not deliberate semantic-mutant target runs; that additional
detector qualification remains open.

This is an adapter/core gate. The actual CYD `decoder_task`, maintenance/queue
lifecycle, allocation failure injection and physical vendor/custom comparison
remain open. It does not establish RF, DMA/I2S, full-radio resource margins,
physical stack/timing/power, all 21 possible source depths, or complete FLAC
CRC/MD5/malformed-stream conformance. Heap and stack observations come from this
emulator test profile. The debug guards and DIO/40 MHz flash configuration do
not change production settings or justify a performance claim.
