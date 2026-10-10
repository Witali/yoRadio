# ESP32-C3 staged PCM tail audit

## Confirmed baseline behavior

The normal staged output retains a partial 512-frame stereo block at EOF.
It can then copy those old samples into the beginning of a new stream at the
same sample rate. This finding concerns output buffering, independently of
AAC precision, the PDM clock divider, and the initial-input-prefill experiment.

An isolated host test compiles the actual `native_audio_output.c` and DMA
writer with guarded platform stubs under AddressSanitizer and UBSan:

1. Configure 48 kHz and write 128 stereo frames, each sample equal to 1234.
2. Run 1,000 idle calls over five simulated seconds. The 128 frames remain
   buffered; no audio bytes are submitted to DMA.
3. Configure the same rate and write 384 frames, each sample equal to -2345.
4. The resulting DMA block contains the previous 128 frames followed by the
   new 384 frames. No sanitizer error occurs: this is a lifetime/stream-boundary
   error, not an out-of-bounds write.

Source inspection connects this reproduction to the application:

- The staged `output_task` EOF branch only publishes completion and returns
  its queue item. It calls `native_audio_output_flush_pcm()` only when the
  optional direct-DMA output is enabled.
- Generation changes call `native_audio_output_discard_pcm()` only in that
  direct-DMA configuration.
- Staged `native_audio_output_idle()` only decays the level indicator.
- Staged configure resets the buffer and resampler only when the rate changes.

The host probe calls real output functions, but represents the current EOF
branch by its absence of output work. It does not execute the whole task or
prove physical audibility. The observed retained tail is 2.667 ms at 48 kHz;
the partial block can hold up to 511 frames, or about 10.65 ms. Previously
queued hardware DMA audio is a separate drain/cancellation question.

The existing staged/direct parity harness manually pads and writes the staged
tail after each case and forcibly resets its input rate. Those checks prove
PCM arithmetic parity, but do not cover production EOF and same-rate switching.

## Repair and acceptance plan

- [x] Expose flush/discard operations for every output backend, including the
  QEMU sink. Keep direct-DMA lease ownership and release rules unchanged.
- [x] At EOF, submit the staged remainder with zero padding; propagate write
  failure without replaying stale PCM. Define whether completion means data
  submitted or hardware playback drained, and test that contract explicitly.
- [x] On Stop/new generation, discard staged software PCM and reset resampler
  history before accepting new-generation data, including equal-rate streams.
  Check generation changes while receiving or writing a packet.
- [x] Flush valid old-rate data before an in-stream rate change. Keep ordinary
  same-stream chunk boundaries continuous and avoid extra per-packet padding.
- [x] Add regression cases for 1, 127, 511, 512 and 513 frames; mono/stereo;
  source rates 8–48 kHz; repeated EOF; same-rate replacement; Stop; rate changes;
  failed/short DMA writes; and resampler-history isolation. Remove the host
  harness's manual staged-tail workaround in favor of the public API.
- [x] Test the actual output-task integration with deterministic queue/output
  stubs, including generation changes during receive, write and flush.
- [x] Complete final firmware linking and physical EOF/transitions, Stop/Play
  races and continuous playback qualification of the repaired image.
  [Hardware follow-up](ESP32C3_PCM_TAIL_BOARD_20261009.md): 60 measured short-file
  cases, 44 format/transport cases, sustained HE-AACv2/FLAC, transitions and
  switching pass. Analog output quality and final production configuration
  remain separate qualification work.

## Source repair and validation

The working source now implements the repair. EOF flush submits one padded
block and consumes the software tail once, including a failed or short write.
The output task logs flush failure and keeps its existing completion-status
contract. Completion means submission to the driver, not the end of hardware
playback. Stop/new generation clears software samples and interpolation
history; already queued hardware DMA frames finish naturally.

The rate-change path flushes valid old-rate samples before resetting the
resampler. Padding can add silence up to the rest of that final 512-frame
block, matching the existing direct-DMA boundary behavior. Normal chunk
boundaries remain continuous. The QEMU sink writes frames synchronously, so
its flush is empty and its discard resets interpolation history.

Validation of the exact changed sources:

- 95 staged and 94 direct-output boundary cases pass ASan/UBSan. The staged
  suite includes the stock driver's extra short-write case; both produce the
  same 456,704 PCM bytes.
- 10 real `output_task` cases pass for each output mode. A negative control
  rejects the original task because it publishes EOF without calling flush.
- The existing 432-case PCM matrix passes for staged/direct output and both
  diagnostic configurations: all four emit the same 12,331,776 bytes. The
  648-case normalizer comparison remains exact.
- Six isolated ESP32-C3 compiler checks pass: staged output/task, direct task,
  direct task with pipeline diagnostics, and QEMU output/task. These are
  object compilation checks, not a final linked firmware or physical test.

The [repair evidence](../tests/results/esp32c3-output-tail-fix-20261009/)
retains source hashes, generated host translation units, logs, the expected
negative-control failure and target compile commands. Initial test-build
failures from an embedded `#pragma once` and mixed copies of a header are
also retained; both test setup issues were corrected before the passing runs.

The completed prefill experiment used the unchanged baseline output. Its
physical passes cannot be reused as hardware qualification of this repair.
At that source-repair checkpoint, the connected board remained on the restored
production image. The subsequent [linked-image and hardware follow-up](ESP32C3_PCM_TAIL_BOARD_20261009.md)
qualifies this repair's recorded digital/runtime checks and restores production
again. It does not qualify analog noise or replace the original failure record.

Run the repair tests from the repository root (use new output directories):

```powershell
python tools/codec_benchmark/run_output_dma_host.py --profile --output .build/output-parity
python tools/codec_benchmark/run_output_boundary_host.py --output .build/output-boundaries
python tests/run-output-task-boundaries.py --output .build/output-task-boundaries
```

## Frozen evidence

The [archive](../tests/results/esp32c3-output-tail-audit-20261009/) contains the
original C sources, assembled translation unit, guarded stubs, test PCM, logs
and SHA-256 index. It reproduces the **baseline bug**, not a passing firmware
acceptance result. Replay without contacting the board:

```powershell
python tests/results/esp32c3-output-tail-audit-20261009/replay.py --output .build/output-tail-replay
```

On Windows the replay uses GCC in WSL; on Linux it uses native GCC. Output
must be a new directory outside the archive.
