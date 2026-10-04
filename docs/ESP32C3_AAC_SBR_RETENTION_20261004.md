# ESP32-C3: preserve established SBR across missing extension frames

Status: **QEMU-only experiment**, not installed on the physical board.
This extends the [late-SBR investigation](ESP32C3_AAC_LATE_SBR_20261004.md).

## Reference behavior changes the test expectation

The first reverse-transition test assumed that a frame without an SBR payload
must immediately return to 22.05 kHz mono. The native candidate instead
reported 44.1 kHz mono, and that assertion failed. This record is retained,
but its expected format was an assumption, not an established requirement.

Pristine FAAD float and fixed builds both decoded the same 41-frame sequence
(13 LC frames, 15 HEv2 frames, 13 LC-payload frames) successfully. Once SBR/PS
was established, **all remaining frames stayed 44.1 kHz stereo**. Missing
extension data alone does not provide an unambiguous new-stream boundary.
FAAD's default also upsamples the initial low-rate LC phase; that initial
upsampling policy is separate from the retention finding.

The local FAAD source was verified byte-for-byte against all 129 files in the
pinned source archive, revision `e8e76f0a44db45aed773a3f62fe35a63c867a738`.
Its [extension parser](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/syntax.c)
establishes SBR/PS state, and its
[reconstruction code](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/specrec.c)
continues using that state. This is reference implementation evidence,
not a claim of complete MPEG conformance certification.

## Native controller change

The native `sbr_applied` routine already handles zero new SBR elements using
retained state. Its caller prematurely disables SBR/PS before reaching that
path. The experiment routes one verified native conditional branch through
a predicate which keeps the established configuration only when its owner
and initialized control exist. A disabled experiment uses the original branch.

- No fake SBR payload or element count is inserted.
- Existing IMDCT, QMF, SBR and PS processing/history continue unchanged.
- The C predicate uses named fields of the verified native structures.
- Native continuation addresses are derived from local symbols and the
  verified branch relocation. No absolute address is embedded in the bridge.
- The branch bridge preserves other caller-saved RV32 registers and maintains
  stack alignment with a temporary 64-byte stack frame.
- The patcher verifies the complete input-object hash against the pinned
  compact-layout audit, then verifies the branch, registers, fall-through
  instructions and relocation. Only four bytes of native code change;
  an additional bridge section provides the predicate call.

New station generations and changed ADTS configurations still use the
existing reopen behavior. A single absent extension does not force either
a decoder reset or a lower-rate fallback.

## Exact PCM comparison

Two images use the same controller change. The reference retains full-precision
32-bit sample histories while keeping existing lossless pointer-table/owner
compaction. The candidate uses the current high-history packing, four-row
smoothing, scoped low-QMF workspace and asymmetric owner. PS PC16 and other
quantization experiments are disabled in the reference.

Both images capture raw signed-16 PCM from the same 56-frame sequence. There
is no resampling, alignment adjustment, gain matching, skipped startup sample
or WAV conversion in this comparison.

| Phase | Channel samples | Different samples | Maximum error |
| --- | ---: | ---: | ---: |
| Initial LC | 13,312 | 0 | 0 LSB |
| Late HEv2 activation | 61,440 | 4 | 1 LSB |
| Frames without new SBR | 53,248 | 145 | 2 LSB |
| SBR packets resume | 61,440 | 0 | 0 LSB |
| **Total** | **189,440** | **149** | **2 LSB** |

RMS error is **0.0324922 LSB**. Absolute-error counts are 189,291 at zero,
132 at one and 17 at two LSB; none exceeds the production tolerance of three.
This qualifies storage precision for this synthetic transition corpus only.
It does not quantify differences between the native decoder and FAAD.

The six ordinary-stream controller comparisons still pass byte-for-byte over
887,808 channel samples. Both odd/even LC history-bank phases pass missing-SBR
and resumed-SBR playback at full 44.1 kHz stereo. Two identical candidate
decoders also produce identical complete PCM when their output buffers are
filled with different patterns before every call, with guards intact.

The candidate passes 611,506 pointer checks, 41,124 copy checks, 312 matched
allocations/frees, reset/failure injection and concurrent decoder tests.
Minimum measured margin is 2,844 bytes on the unchanged 16 KiB decoder stack.

| SBR storage measurement in QEMU | Full-precision history reference | Compact candidate | Difference |
| --- | ---: | ---: | ---: |
| Owner requested size | 49,708 B | 32,744 B | 16,964 B |
| Owner allocated block, light heap poisoning | 51,188 B | 32,756 B | 18,432 B |
| Test adapter context | 16 B | 32 B | +16 B |

The reference already has lossless compaction, so this table is **not** the
total saving relative to the original 55,128-byte owner. Stack workspace,
context, other decoder allocations and physical heap fragmentation remain
separate. The controller bridge itself creates no persistent allocation.
Capture output and instrumentation make these runs unsuitable for CPU timing.

## Reproduce and inspect

[Evidence](../tests/results/esp32c3-aac-sbr-retention-20261004/) contains both
configs, exact logs and PCM (gzip), ELF hashes, native objects before/after
patching, source snapshots, FAAD frame traces and the rejected first assertion.

Build two separate directories with the saved `candidate/sdkconfig` and
`reference/sdkconfig`, using the same `build.ps1` invocation documented in
the preceding investigation. Their build directory names are
`build-qemu-aac-late-capture` and `build-qemu-aac-late-reference`.
Both enable `YORADIO_QEMU_AAC_LATE_SBR_TEST` and
`YORADIO_QEMU_AAC_LATE_SBR_CAPTURE`; only the candidate enables compact
history and the pointer audit.

Run the following from the worktree root, adjusting installed SDK/QEMU paths:

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
$qemu = '/mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32'
$bios = '/mnt/c/Work/QEMU-ESP32/share/qemu'
& $python tools/codec_benchmark/run_aac_late_sbr_capture.py --build idf/esp32c3-oled-native/build-qemu-aac-late-reference --dependency-root C:/Work/yoRadio/.idf --output .build/retention-reference --qemu $qemu --bios $bios --wsl --full-precision
& $python tools/codec_benchmark/run_aac_late_sbr_capture.py --build idf/esp32c3-oled-native/build-qemu-aac-late-capture --dependency-root C:/Work/yoRadio/.idf --output .build/retention-candidate --qemu $qemu --bios $bios --wsl
& $python tools/codec_benchmark/compare_aac_late_sbr_pcm.py --reference-log .build/retention-reference/qemu.log --candidate-log .build/retention-candidate/qemu.log --output .build/retention-comparison
& $python tests/test-aac-sbr-retention.py --toolchain C:/Work/yoRadio/.idf/tools-v6.0.2/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin
```

The capture runner's ordinary-PCM pass is separate from the cross-image
comparison in the third command. Incomplete captures, duplicate/reordered
chunks, wrong shape, native patch drift and insufficient evidence fail closed.

## Still required before physical deployment

- Extend missing-extension tests to HE v1 stereo/mono and more sample rates,
  plus malformed/truncated extension data and long recordings.
- Exercise reset, cancellation and allocation failures during late activation
  and while retained SBR is active, not only the existing standalone cases.
- Verify bitrate/profile reporting against actual extension state.
- Measure physical CPU/heap, HTTP/HTTPS playback, repeated switching, other
  codecs and OTA. No production default or physical image changed in this step.
