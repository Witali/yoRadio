# Low-QMF lifetime experiment before reducing allocation

## Result and limits

The current PC18 high-history + four-row smoothing adapter can discard the
previous contents of low-QMF rows **8..39** immediately before each `sbr_dec`
call on the tested corpus. The native analysis stage replaces those rows before
their consumers use them. This is a lossless lifetime experiment; no additional
sample quantization was introduced.

Six QEMU runs poisoned **9,922,560 int32 words across 4,845 SBR calls**. Each run
also retained the complete pointer audit, allocation-failure/reset checks and
two concurrent decoders. All 657,540 signed-16 control samples match the
unpoisoned adapter exactly. Five station captures retain their complete-output
FNV-1a hashes and sample counts, covering 12,505,088 additional channel samples.
For captures this is a hash comparison, not a retained sample-by-sample error
distribution. The control sequence is repeated in each run; the coverage totals
include those repetitions.

| Run | SBR calls poisoned | Real-only / complex / PS calls | Comparison |
| --- | ---: | ---: | --- |
| Synthetic LC/HE/HEv2 controls | 191 | 80 / 111 / 105 | Control PCM identical |
| ABBA 64 capture + controls | 837 | 80 / 757 / 740 | Capture hash/count and control PCM identical |
| Groove Salad 16 capture + controls | 660 | 80 / 580 / 105 | Capture hash/count and control PCM identical |
| Groove Salad 32 capture + controls | 1,483 | 1,372 / 111 / 105 | Capture hash/count and control PCM identical |
| Groove Salad 64 capture + controls | 1,483 | 1,372 / 111 / 105 | Capture hash/count and control PCM identical |
| Groove Salad 128 capture + controls | 191 | 80 / 111 / 105 | Capture hash/count and control PCM identical |

PS calls are a subset of complex calls. The Groove Salad 16 capture itself has
[no active PS](ESP32C3_AAC_PS_COVERAGE_20261003.md); its PS coverage comes from the
repeated controls. The 128 kbit/s capture itself is AAC-LC and does not use SBR.

**Actual RAM saving in this checkpoint: zero.** The owner request remains
45,932 bytes, with a 47,104-byte allocator block (47,092 usable bytes reported by
the poisoned heap). The experiment neither changes the production default nor
updates the board. Public HE-AAC network-load failures remain unresolved.

## Native readers, writers and aliases

The dimensions in `aac_high_history_abi.h` name the native 32 bands, eight
history rows and 32 new rows. Only dimensions have been renamed; the ABI layout
is unchanged. The probe overwrites both real and imaginary components only in
the active `sbr_dec` frame. It never walks both channel allocations blindly.

| Function / path | Use that must survive a new allocation layout |
| --- | --- |
| `sbr_open` | Clears each channel, writes default headers and initializes both frames. |
| `init_sbr_dec` | Sets 40 rows, 32 columns, write offset 8 and read offset 2; does not regenerate the retained low history. |
| `calc_sbr_anafilterbank` | Generates both components for each new row and clears bands above the requested low-band limit. |
| `calc_sbr_anafilterbank_LC` | Generates/clears the real row; leaves imaginary storage untouched. |
| `sbr_dec`: high-frequency generation | Reads the low matrix starting at `read_offset`, including history and newly written rows. |
| `sbr_dec`: synthesis and PS input | Reads low real/imaginary rows for synthesis or copies them to the core's PS QMF workspace. |
| `sbr_dec`: history copies | Copies eight rows starting at `columns` (row 32) back to rows 0..7; real-only mode does not copy imaginary rows. |
| `ps_allocate_decoder` | Reuses the inactive right-channel low-QMF region for energy vectors, hybrid history, delay lines, tables and relocated PS control. These remain live between frames. |
| Repaired `PVMP4AudioDecoderResetBuffer` | Clears eight real rows under the audited mode conditions. Preserve its imaginary-history behavior and PS-specific reset path. |
| Owner free / concurrent tasks | Each decoder owns its retained history; temporary rows must be scoped to the current call/task and must not escape. |

Sources: pinned [SBR decode pseudocode](audits/esp32c3-aac-symbolic-20261001/pseudocode/sbr_dec.c),
[PS allocator](audits/esp32c3-aac-symbolic-20261001/pseudocode/ps_allocate_decoder.c),
[analysis filter](audits/esp32c3-aac-symbolic-20261001/pseudocode/calc_sbr_anafilterbank.c),
and the [pointer ownership audit](ESP32C3_AAC_POINTER_AUDIT_20261003.md).
Pseudocode is reconstructed from the pinned binary, not original source.

## Negative control and test synchronization

The separate negative configuration also overwrites row 7, which belongs to
retained history. The completed run correctly fails exact PCM comparison:
**302,728 differing samples, maximum 32,809 LSB, RMS 1,933.177923 LSB**. This is
intentional destructive test input, never a permitted decoding error.

The first negative run exposed a timing dependency in the concurrency test:
sleeping for one tick did not always overlap two live smoothing calls. The test
now waits, with a timeout, for an observed second live call. Counter updates are
protected against task preemption. Both the high-history and smoothing scopes
use this rendezvous. The failed scheduling run is retained separately and is
not counted as a completed PCM test.

## Next implementation gate

Follow-up: steps 1–4 below are now implemented and qualified in QEMU in the
[scoped low-QMF workspace experiment](ESP32C3_AAC_LOW_QMF_WORKSPACE_20261003.md).
Its actual owner block saves 10,240 bytes. Physical qualification and speed
measurements in step 5 remain open. The lifetime-only results in this document
still describe the unchanged owner and must not be credited with that saving.

Retaining eight complex low rows needs 2,048 bytes per channel instead of
10,240. The raw-data difference is 8,192 bytes per channel, **not yet a net
owner saving**: the right-channel PS overlay still needs its own live storage.
A complete native complex work matrix needs 10,240 bytes temporarily. Its stack
placement must be measured with the other DSP frames and the temporary smoothing
row; do not reduce the shared production decoder stack needed by Opus.

Before shrinking the owner:

1. Replace every native low-matrix base with a compiler-derived binding to the
   temporary matrix; retain eight rows independently for each channel.
2. Preserve inactive imaginary history in real-only mode. Verify all reset,
   reopen and channel/profile-change paths.
3. Relocate or separately size the right-channel PS overlay, auditing every
   parser, initializer, reader and reset writer before reusing its prefix.
4. Re-run exact PCM, captured-output comparisons, pointer audits, concurrent
   decoders and stack high-water checks on the smaller actual allocation.
5. Measure net heap saving and decoding work, then repeat physical HTTP/HTTPS,
   all-codec and OTA acceptance. This experiment does not establish CPU speed.

## Reproduce

Use a fresh emulator build directory with these defaults in order:

```text
sdkconfig.defaults
sdkconfig.qemu.defaults
sdkconfig.qemu-aac-compact-adapter.defaults
sdkconfig.aac-smoothing-history.defaults
sdkconfig.qemu-aac-low-lifetime.defaults
```

Run `tools/codec_benchmark/run_aac_low_lifetime.py` with the build/dependency
paths, `--qemu`, `--bios`, `--wsl` as needed, the matching unpoisoned pointer-audit
`--baseline result.json` and `--previous-wav audio.wav`. Add `--input` and
`--ffprobe` for a retained station recording. For the deliberately failing
control only, enable `CONFIG_YORADIO_QEMU_AAC_LOW_POISON_HISTORY`; expected runner
exit code is 2. It must be off for the passing runs.

[Retained evidence](../tests/results/esp32c3-aac-low-lifetime-20261003/) includes
both configurations, logs, image hashes, exact source snapshots and the failed
scheduling control. Gzip-compressed WAV files retain the original synthetic
control output, the passing output and the intentionally corrupted output;
station audio is not included. Run `python tests/test-aac-low-lifetime.py` to
recompute control error statistics, check saved results and verify rejection of
incomplete reports.
