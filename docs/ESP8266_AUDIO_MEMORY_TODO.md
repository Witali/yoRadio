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
  Physical testing established this as the largest reliable contiguous
  allocation. MP3 splits IMDCT output per channel and uses 11472 bytes DRAM
  plus the 16384-byte IRAM arena; larger/spill arenas were rejected by the
  SDK heap regions and are not part of the default profile.
- [x] Add an MP3-only build profile. When AAC is disabled, size PCM for one
  576-sample stereo granule (2304 bytes instead of 4096) and use a backend-
  appropriate IRAM arena. libmad now reserves 12 KiB: 4236 bytes for
  `mad_synth`, 4608 bytes for `xr_raw`, 2304 bytes for the reorder workspace,
  and 1136 bytes of alignment/version headroom.
- [x] Move only libmad's aligned 32-bit Layer III `xr_raw` and reorder
  workspaces to IRAM. The Xtensa DWARF layout confirms that `mad_frame` falls
  from 20784 to 13880 bytes, freeing 6904 bytes of byte-addressable DRAM while
  keeping `mad_stream`, the frame header, subband samples, and overlap in DRAM.
- [x] Keep the normal upstream array layout unless the ESP8266 component
  explicitly enables `YORADIO_LIBMAD_EXTERNAL_FRAME_WORKSPACE`. The external-
  workspace host fixture decodes all 18 retained 320-kbit/s MP3 frames to PCM
  byte-for-byte identical to the original libmad layout.
- [x] Do not reduce the 1536-byte compressed-input buffer until fixtures prove
  that the maximum supported MP3/AAC frame still fits.

## Acceptance

- [x] Build Helix and libmad full/QIO80/MP3-only profiles with GCC 8.4 `-O3`.
- [x] Rebuild both libmad MP3-only/QIO80 and full libmad+AAC/QIO80 after the
  IRAM frame split; both link successfully with GCC 8.4 `-O3`.
- [x] Pass native HTTP, WebUI, codec-switch, PCM golden/SNR and repository
  regression tests.
- [x] On the physical board, boot without a reset loop, obtain DHCP, return
  WebUI HTTP 200, and preserve BOOT-button control.
- [x] Play low- and high-bitrate MP3 and AAC streams, including a 320-kbit/s
  fixture/stream, without decoder starvation or heap-reserve violations.
  Verified live MP3 at 128 kbit/s, live AAC near 320 kbit/s and the deterministic
  MP3/AAC 320-kbit/s RAM fixtures. Before the IRAM frame split, the full
  libmad+AAC profile could not create libmad after reserving AAC's 16-KB
  arena. The reduced-DRAM full image now builds, but keep using the tested
  MP3-only libmad or normal Helix profile until it is rechecked on hardware.
- [ ] Repeat the physical MP3-only RAM benchmark after the IRAM frame split.
  Expected active workspace accounting is 20388 bytes DRAM and 12288 bytes
  reserved IRAM; confirm boot, WebUI, BOOT control, lifecycle delta zero, and
  continuous 320-kbit/s playback before replacing the archived image.
- [x] Archive a successful development firmware and update the firmware
  changelog only after the integrated test passes.
