# ESP8266 audio-service memory TODO

This checklist follows the 2026-09-01 physical Wemos D1 mini comparison of
the Helix and experimental libmad MP3 backends. Keep Helix as the production
default until every integrated libmad criterion below passes.

## Correctness before reduction

- [ ] Fix the libmad DRAM leak: `mad_stream` and `mad_frame` must be released
  with `CodecArenaFree()` before resetting their pointers/arena owner.
- [ ] Add a regression that repeatedly resets MP3 and switches MP3/AAC in
  both orders without monotonically losing heap.
- [ ] Separate DRAM and IRAM accounting. Do not treat the 16-KB IRAM capacity
  as if all of it replaced DRAM used by the current decoder.
- [ ] Enforce the configured post-allocation DRAM reserve using actual free
  heap after all decoder objects have been allocated.

## Lazy audio lifecycle

- [ ] Start Wi-Fi and WebUI without allocating input, PCM or decoder state.
- [ ] Allocate the codec only after an HTTP stream is open and its FOURCC/
  frame signature identifies MP3 or AAC.
- [ ] Reuse a decoder when a user immediately switches stations and the next
  stream uses the same backend.
- [ ] Release input, PCM and decoder state when playback is explicitly
  stopped or terminates with no replacement command pending.
- [ ] Exercise at least 50 play/stop cycles and 50 MP3/AAC switches; record
  initial, minimum and final free heap to detect leaks or fragmentation.

## Stack and profile-specific sizing

- [ ] Add audio-task stack high-water instrumentation to the diagnostic
  profile. Measure connection, MP3 320 kbit/s, AAC 320 kbit/s, switching,
  ICY metadata and WebUI activity before changing the 5120-byte stack.
- [ ] Keep the full MP3+AAC profile's 16-KB word arena: AAC can use the whole
  arena for its two 8-KB 32-bit workspaces.
- [ ] Add an MP3-only build profile. When AAC is disabled, size PCM for one
  576-sample stereo granule (2304 bytes instead of 4096) and use a backend-
  appropriate IRAM arena (about 9 KB for libmad; measured Helix requirement
  must remain covered).
- [ ] Do not reduce the 1536-byte compressed-input buffer until fixtures prove
  that the maximum supported MP3/AAC frame still fits.

## Acceptance

- [ ] Build Helix and libmad full/QIO80/MP3-only profiles with GCC 8.4 `-O3`.
- [ ] Pass native HTTP, WebUI, codec-switch, PCM golden/SNR and repository
  regression tests.
- [ ] On the physical board, boot without a reset loop, obtain DHCP, return
  WebUI HTTP 200, and preserve BOOT-button control.
- [ ] Play low- and high-bitrate MP3 and AAC streams, including a 320-kbit/s
  fixture/stream, without decoder starvation or heap-reserve violations.
- [ ] Archive a successful development firmware and update the firmware
  changelog only after the integrated test passes.

