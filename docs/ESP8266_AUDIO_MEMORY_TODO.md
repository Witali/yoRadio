# ESP8266 audio-service memory TODO

This checklist follows the 2026-09-01 physical Wemos D1 mini comparison of
the Helix and experimental libmad MP3 backends. Keep Helix as the production
default until every integrated libmad criterion below passes.

## Correctness before reduction

- [x] Fix the libmad DRAM leak: `mad_stream` and `mad_frame` must be released
  with `CodecArenaFree()` before resetting their pointers/arena owner.
- [x] Add a regression that repeatedly resets MP3 and switches MP3/AAC in
  both orders without monotonically losing heap.
- [x] Separate DRAM and IRAM accounting. Do not treat the 16-KB IRAM capacity
  as if all of it replaced DRAM used by the current decoder.
- [x] Enforce the configured post-allocation DRAM reserve using actual free
  heap after all decoder objects have been allocated.

## Lazy audio lifecycle

- [x] Reserve the shared 32-bit arena before Wi-Fi claims IRAM, but start
  Wi-Fi and WebUI without allocating input, PCM or decoder state. If the arena
  ever falls back to DRAM, account its full capacity as DRAM rather than IRAM.
- [x] Allocate the codec only after an HTTP stream is open and its FOURCC/
  frame signature identifies MP3 or AAC.
- [x] Reuse a decoder when a user immediately switches stations and the next
  stream uses the same backend.
- [x] Release input, PCM and decoder state when playback is explicitly
  stopped or terminates with no replacement command pending.
- [x] Exercise at least 50 decoder create/destroy cycles and 50 MP3/AAC
  switches; record
  initial, minimum and final free heap to detect leaks or fragmentation.
  Physical result: 96,868 initial, 67,744 minimum and 96,868 final bytes;
  delta 0.

## Stack and profile-specific sizing

- [x] Add audio-task stack high-water instrumentation to the diagnostic
  profile.
- [ ] Measure connection, MP3 320 kbit/s, switching, ICY metadata and WebUI
  activity before changing the 5120-byte stack. The diagnostic wrappers
  currently fragment the last free block before libmad allocation; keep 5120
  bytes until a lower-overhead diagnostic build can finish the full scenario.
- [x] Keep the full MP3+AAC profile's 16-KB word arena: AAC can use the whole
  arena for its two 8-KB 32-bit workspaces.
- [x] Add an MP3-only build profile. When AAC is disabled, size PCM for one
  576-sample stereo granule (2304 bytes instead of 4096) and use a backend-
  appropriate IRAM arena (5 KB for libmad: 4236 bytes measured plus 884 bytes
  headroom; measured Helix requirement must remain covered).
- [x] Do not reduce the 1536-byte compressed-input buffer until fixtures prove
  that the maximum supported MP3/AAC frame still fits.

## Acceptance

- [x] Build Helix and libmad full/QIO80/MP3-only profiles with GCC 8.4 `-O3`.
- [x] Pass native HTTP, WebUI, codec-switch, PCM golden/SNR and repository
  regression tests.
- [x] On the physical board, boot without a reset loop, obtain DHCP, return
  WebUI HTTP 200, and preserve BOOT-button control.
- [x] Play low- and high-bitrate MP3 and AAC streams, including a 320-kbit/s
  fixture/stream, without decoder starvation or heap-reserve violations.
  Verified live MP3 at 128 kbit/s, live AAC near 320 kbit/s and the deterministic
  MP3/AAC 320-kbit/s RAM fixtures. The full libmad+AAC profile still cannot
  create libmad after reserving AAC's 16-KB arena; use the tested MP3-only
  libmad profile or the normal Helix profile.
- [x] Archive a successful development firmware and update the firmware
  changelog only after the integrated test passes.
