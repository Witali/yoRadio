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

- [ ] Expose flush/discard operations for every output backend, including the
  QEMU sink. Keep direct-DMA lease ownership and release rules unchanged.
- [ ] At EOF, submit the staged remainder with zero padding; propagate write
  failure without replaying stale PCM. Define whether completion means data
  submitted or hardware playback drained, and test that contract explicitly.
- [ ] On Stop/new generation, discard staged software PCM and reset resampler
  history before accepting new-generation data, including equal-rate streams.
  Check generation changes while receiving or writing a packet.
- [ ] Flush valid old-rate data before an in-stream rate change. Keep ordinary
  same-stream chunk boundaries continuous and avoid extra per-packet padding.
- [ ] Add regression cases for 1, 127, 511, 512 and 513 frames; mono/stereo;
  source rates 8–48 kHz; repeated EOF; same-rate replacement; Stop; rate changes;
  failed/short DMA writes; and resampler-history isolation. Remove the host
  harness's manual staged-tail workaround in favor of the public API.
- [ ] Test the actual output-task integration, not just helper functions.
  Repeat physical EOF/transitions, Stop/Play races and continuous playback.

No repair is included in this audit. The concurrently running prefill firmware
is kept unchanged so its physical comparison remains attributable.

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
