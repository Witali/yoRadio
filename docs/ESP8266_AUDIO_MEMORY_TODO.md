# ESP8266 audio-service memory TODO

This checklist follows the 2026-09-01 physical Wemos D1 mini comparison of
the Helix and experimental libmad MP3 backends. Keep Helix as the production
default until every integrated libmad criterion below passes.

## Compressed-stream buffering follow-up (2026-09-05)

The live starvation measurements and reader-task RAM budget are in
`ESP8266_AUDIO_GAPS_2026-09-05.md`. Do not lower production WebUI's 5120-byte
stack based on the older 4096-byte experiments recorded below.

- [x] Remove the KaRadio producer's redundant 1024-byte detection probe.
  Before the consumer's first read the published ring prefix starts at zero,
  is contiguous and cannot be overwritten by the producer. Inspect it directly
  outside the critical section, keeping the existing 1024-byte probe limit.
  The 4096-byte input ring and 2560-byte network stack remain unchanged.
  This saves exactly 1024 bytes of static DRAM when the producer is enabled;
  native's default single-task profile already excludes that probe entirely.
- [ ] Reduce/reuse the remaining extra URL/protocol workspace with explicit
  lifetime ownership and cancellation acknowledgement before enabling the
  producer in the memory-constrained full MP3/AAC native build.
- [ ] Make the compressed ring configurable and assign verified savings to
  larger prebuffering, keeping headroom for WebUI, the TCP stack and AAC.
- [ ] Measure production heap low-water, largest allocation and stack margins
  with MP3/AAC, station switches and multiple WebUI tabs before choosing the
  larger default. Do not subtract all reserved IRAM as freed DRAM.
  Measurement work is recorded in `ESP8266_MEMORY_HEADROOM_2026-09-05.md`;
  do not approve a larger buffer yet. The two-tab MP3 stress reached only
  1160 bytes free DRAM (lifetime minimum), with a sampled largest block of
  548 bytes and loss of WebUI control. Full acceptance remains open.
  - [x] Add allocation-free DRAM/largest-block and app/audio/WebUI stack
    instrumentation; save the physical workload and diagnostic image.
  - [x] Measure MP3 128 and decoded AAC about 320 kbit/s on the physical board,
    and exercise AAC -> MP3 -> AAC with Wi-Fi and ordinary I2S PDM enabled.
  - [x] Load two actual WebUI pages and capture the MP3 low-memory failure.
  - [x] Repeat after reset with AAC 320, page reload during playback and MP3:
    AAC reload reached 5136 bytes minimum, and MP3 again lost WebUI with
    1472 bytes minimum / 548-byte largest sampled block. Restore and verify
    the exact ordinary firmware and the original station/volume/stop state.
  - [ ] Resolve slow/disconnected WebSocket/TCP resource pressure, then repeat
    the full two-tab/reload stress before reserving more compressed data.
  - [ ] Repeat with a controlled MP3 320-kbit/s fixture; the nominal 256 preset
    tested here actually supplied MP3 128.
  - [ ] Investigate the separate low-bitrate AAC PCM-output timeout observed
    with about 10 KiB minimum free heap; it is not proven to be an OOM failure.
- [ ] Replace the producer's EAGAIN 1-ms polling with readiness waiting and
  keep immediate cancellation/BOOT control responsive.

## Correctness before reduction

### MP3 scratch reuse (2026-09-05)

- [x] Reuse the dead IMDCT output for the 792-byte short-block reorder
  scratch, retaining IMDCT as the sole allocation owner.
- [x] Prove separate/shared PCM is byte-identical for Mono/Stereo and both
  output APIs; test allocation failures, reset, canaries and MP3/AAC cycles.
- [x] Build the optimized native profile; keep an explicit A/B switch.
- [ ] Measure the additional device heap headroom and CPU behavior under
  real playback/WebUI load. Host results are not on-board speed measurements.

See [lifetime contract and results](ESP8266_MP3_REORDER_REUSE.md).

### PCM32 and direct DMA (2026-09-05)

- [x] Emit Helix MP3 in 32-frame blocks: 64-byte mono PCM, 1088 bytes saved.
- [x] Write PDM into a reserved producer-owned DMA span, without the 256-byte
  temporary array/copy; keep two 512-word buffers and all task stack sizes.
- [x] Test bit-exact PCM/PDM, normalization continuity, EOF interleavings,
  partial commits, cancellation, timeout and reset.
- [x] Fix unsigned balance clamping and ignore balance completely for mono.
- [x] On-board trace: physical MP3 workspace 8440 DRAM / 16384 IRAM, nonzero
  decoded/processed PCM and changing DMA-PDM. All 337 host tests pass.
- [ ] Measure matched CPU timing and long-run audio/WebUI stability before
  assigning these savings to a larger compressed input buffer.

See [implementation and physical evidence](ESP8266_PCM32_DIRECT_DMA.md).

### Existing lifecycle checks

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
  activity before reducing the HTTP stack below 4096 bytes. Direct bounded
  status formatting and a physical Web API test made 4096 bytes reliable, but
  a smaller stack still needs a lower-overhead high-water measurement.
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
