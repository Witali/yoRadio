# ESP32-C3 late implicit SBR: QEMU experiment

Status: **not enabled in physical firmware or production defaults**.
`CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST` requires the QEMU AAC suite, AAC Plus
and compact SBR storage. It changes the controller, not sample precision or
storage packing. The board still runs the network-memory diagnostic image.

## Reproduced failure and code finding

The physical board passed explicit ADTS configuration changes and the
stop/play generation test, but failed `transition:implicit-sbr` with
`Missing full-rate transition 2/3`. The sequence is LC 22.05 kHz mono →
HE-AACv2 44.1 kHz stereo → LC 48 kHz stereo. Its first two phases have the
same ADTS core configuration, so reopening on a changed ADTS header does
not detect the extension.

The pinned native controller stops parsing SBR after LC. Simply re-enabling
its two flags is insufficient: it also initializes SBR and refreshes some
output metadata only during its first two frames. An experiment restoring
the flags, initializing SBR late and updating metadata still crashed in
QEMU (`MTVAL=0x348`, native frame controller). That rejected attempt is
retained as `initialization-only`; emulator process exit zero did not mean
the test passed.

The named decompilation exposes a further history-bank mismatch:

- LC selects history bank 0 or 1,024 samples.
- SBR selects bank 0 or 1,312 samples (1,024 core samples plus 288 history).
- The SBR history copy subtracts 1,312 samples for its second bank. Entering
  with the LC bank at 1,024 makes that destination 288 samples before the
  channel history array.

The candidate wraps the native `get_sbr_bitstream` parser. Only after it
reports an actual SBR element does the wrapper change an incompatible
1,024-sample bank to zero, before the transform writes the frame. It keeps
IMDCT overlaps intact. The candidate also initializes previously unused SBR
control and refreshes the decoded rate/frame length. It does not reset the
frame counter or scan raw payload bytes itself.

Relevant pinned analysis:
[frame controller](audits/esp32c3-aac-core-symbolic-20261001/pseudocode/PVMP4AudioDecodeFrame.c),
[SBR processing](audits/esp32c3-aac-core-symbolic-20261001/pseudocode/sbr_dec.c),
[native extension parser](audits/esp32c3-aac-core-symbolic-20261001/pseudocode/get_sbr_bitstream.c).
This is a code-derived explanation supported by the two emulator outcomes;
the failing store has not yet been independently captured with a watchpoint.

## Measured regression results

Six ordinary fixtures were each repeated three times. Two separate native
decoders receive identical 193-byte input chunks: the control disables only
the late-SBR experiment, and the candidate enables it. Both use identical
compact storage. The test compares every emitted PCM byte, consumption,
output size and decoded rate/channels, checks both PCM buffer guards and
checks heap integrity after teardown. This comparison isolates controller
changes; it is not another comparison against an uncompressed decoder.

| Ordinary stream | Frames | Signed 16-bit channel samples | Maximum difference |
| --- | ---: | ---: | ---: |
| LC 44.1 kHz stereo | 72 | 147,456 | 0 LSB |
| LC 22.05 kHz mono | 39 | 39,936 | 0 LSB |
| LC 48 kHz stereo | 78 | 159,744 | 0 LSB |
| HE-AAC 44.1 kHz stereo | 42 | 172,032 | 0 LSB |
| HE-AAC 48 kHz stereo | 45 | 184,320 | 0 LSB |
| HE-AACv2 44.1 kHz stereo | 45 | 184,320 | 0 LSB |
| **Total** | **321** | **887,808** | **0 LSB** |

The same-header LC → HEv2 transition passed after both 13 and 26 LC frames:
15 HEv2 frames each, full 44.1 kHz stereo output, valid buffer guards/heap.
These cover both LC bank phases. They do **not** compare PCM at the transition
against an independent reference or establish inaudible switching.

The combined run also passed existing owner failure injection, two resets
and two concurrent decoder tasks. The final pointer report includes the new
paired/transition cases: 436,116 checks, 290 allocations and 290 frees,
27,492 copy checks; all pointer and buffer-boundary negative tests passed.
Minimum stack margin was 2,844 bytes on the unchanged 16,384-byte decoder
stack. Test context is 32 bytes versus 24 without this experiment; these
QEMU measurements are not physical CPU or production RAM qualification.

Host validation passed 24 tests: four new evidence/acceptance tests, eleven
existing pointer-audit tests and nine asymmetric-owner tests, including the
fresh RV32 compiler layout check. Corrupted/truncated logs, a missing bank
phase, changed PCM, leaked allocations and insufficient stack margin are
rejected by the new acceptance parser.

The final run uses ELF SHA-256
`6e13554c29062350e00b4df30ef5fc8e3f31ecc565ffee975ec62082d8647ec7`
and codec archive SHA-256
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.
[Evidence](../tests/results/esp32c3-aac-late-sbr-20261004/) retains the physical
baseline failure, rejected first attempt, initial bank-fix run, paired/audit
run, final runner output, source snapshots, configuration and checksums.

## Reproduce

From the repository/worktree root, with the existing local SDK and QEMU:

```powershell
$project = 'idf/esp32c3-oled-native'
$build = "$project/build-qemu-aac-late-sbr"
New-Item -ItemType Directory -Force $build | Out-Null
Copy-Item tests/results/esp32c3-aac-late-sbr-20261004/regression-final/sdkconfig "$build/sdkconfig"
& "$project/build.ps1" -BuildDirectory build-qemu-aac-late-sbr -Sdkconfig build-qemu-aac-late-sbr/sdkconfig -DependencyRoot C:/Work/yoRadio/.idf build
& C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe tools/codec_benchmark/run_aac_late_sbr.py --build $build --dependency-root C:/Work/yoRadio/.idf --output .build/aac-late-sbr-recheck --qemu /mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32 --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl --timeout 240
python tests/test-aac-late-sbr.py
```

Adjust SDK/QEMU paths for another machine. These commands only build and
run an emulator; they do not install an image on the board. The runner
checks the pinned codec and fixture hashes, rejects incomplete logs and
keeps transition/production qualification false even when ordinary PCM
comparison passes.

## Remaining gates

- Reproduce and fix reverse same-header HEv2 → LC transitions. Audit stale
  upsampling/requested-channel state and both history-bank phases first.
- Compare transition PCM with a suitable reference while preserving overlap,
  including streams with intermittently missing SBR data and malformed input.
- Validate bitrate/profile reporting separately; duplicated mono output is
  insufficient proof of active parametric stereo.
- Repeat reset/OOM/concurrency tests through transitions and longer recordings.
- Only then consider physical HTTP/HTTPS, CPU/heap, repeated switching and OTA
  qualification. Production tolerance remains ±3 signed 16-bit LSB.
