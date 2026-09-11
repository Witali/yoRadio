# ESP8266: PCM buffering before PDM

2026-09-11. Goal: continuous real Opus radio, not only fast raw decoding.
No production buffer/default change in this first step.
The new API is compiled only with `YORADIO_OPUS_PCM_LEASES=1`; the build helper
exposes `-OpusPcmLeases`, requiring diagnostic Opus. Default OFF removes the
new acquire branch and wrappers from production. It does not start a consumer.

At mono 48 kHz, PCM16 costs 96 kB/s; PDM32 costs 192 kB/s. Two768-word
DMA buffers cost6144B and hold at most32ms. The existing decoder's separate
960-sample PCM workspace costs another1920B:8064B in total, excluding decoder
history/input/scratch, task stacks and queue/driver control structures.

Candidate: replace the decoder workspace with TWO960-sample PCM frame slots
(3840B total, not an additional ring), plus two256-word DMA buffers (2048B).
Total5888B saves2176B before adding the consumer stack/TCB and synchronization.
PCM capacity40ms plus DMA10.67ms is only a maximum. A slot currently being
decoded is NOT ready audio; an active DMA buffer is already partly consumed.
This must be measured, not advertised as an assured50.67ms underrun margin.

The old synchronous callback cannot transfer a pointer to an asynchronous
consumer: the next coded frame overwrites the same PCM. Packed Opus packets
can contain multiple coded frames. Changing the adapter's config pointer
between callbacks does not change libopus's local output pointer.

## Implemented: explicit PCM ownership at each coded frame

- [x] Add a separate `yoradio_opus_decode_leased_bounded` API. It acquires a
  writable slot before each complete coded frame. Successful output transfers
  ownership; no later Opus access to that PCM, including diagnostic checks.
- [x] On decode error, output cancellation or scratch OOM, return the current
  uncommitted slot with `abort`. Already transferred slots remain caller-owned.
  The lease record lives outside the setjmp frame, including the OOM path.
- [x] Keep ordinary full-packet and synchronous block APIs compatible.
- [x] Host test holds the previous slot THROUGH the next frame decode, checks
  it has not changed, consumes/mutates it, then permits reuse. Test cancellation
  before acquire and after output, invalid alignment, OOM, re-entry and recovery.
- [x] Compare actual PCM against pristine generic32 libopus across SILK,
  hybrid, CELT, CBR/VBR, padding, 2.5..20ms frames and packets up to120ms.

Reproduce both modes (append the same `--capture FILE.opuspkt` to include a
locally retained radio capture):

```
node tools/esp8266_opus_profile/run_block_regressions.cjs
node tools/esp8266_opus_profile/run_block_regressions.cjs --leased
```

Reports: `tools/esp8266_opus_profile/{block,leased}-results.json` include exact
PCM hashes, source hashes and peak scratch. These are host correctness tests,
NOT evidence of hardware speed, scheduler latency or a working PCM consumer.

Saved result:12/12 cases exact for BOTH modes, including the retained private
DLF capture (576 hybrid packets /1728 coded frames, input SHA256
`8f550f4cda894c8c2303bcd37b293d708ece1c8bfe32c74ae7de6156a912c200`).
The capture itself remains local; only hashes/results are committed. The
consumer simulation needs3840B PCM versus1920B for the synchronous baseline;
peak codec scratch is unchanged (worst mixed-mode5968B DRAM /15600B IRAM).
No allocations occur during decoding. This does not yet include an RTOS task.

Target compile check, source136a6a1: saved `esp8266-opus-pcm-lease-off` and
`esp8266-opus-pcm-lease-api`, neither flashed. API ON costs208B flash, zero
additional STATIC RAM; the future3840B PCM pool and consumer stack are not
allocated yet. DMA ISR section identical (387B), and OFF retains the older
DMA512 section sizes. Hardware scheduling/codec-speed qualification remains
open; do not confuse this compile check with a running asynchronous queue.

## Remaining integration and qualification

- [ ] Opt-in diagnostic build with two256-word DMA buffers; keep512 default.
- [ ] Extend native adapter/bridge to use the two PCM slots, including pre-skip,
  EOS trimming and packets with no output; do not copy into another full ring.
- [ ] One consumer owns all gain/normalizer/PDM state. Stop/switch waits for
  acknowledgement before resetting output or freeing queued PCM. No conversion
  in ISR and no blocking wait with interrupts disabled.
- [ ] Budget its stack and TCB explicitly; retain4KiB decoder heap reserve and
  the documented audio-stack minimum. Existing app task runs potentially slow
  network/WebUI/storage maintenance and cannot just become this consumer.
- [ ] Measure stack watermark, min DRAM, ready PCM and DMA occupancy, task CPU,
  underruns and stop/switch latency. DMA256 needs service roughly every5.33ms.
- [ ] Exact PCM/PDM sequence and ownership tests with cancellation and faults.
- [ ] At least10 matched board attempts, at least20s uninterrupted Opus audio
  per qualifying interval, plus WebUI and codec-switch tests. Keep all failures.

Do not lower memory guards or accept lossy u-law/A-law to make a test pass.
Buffering cannot cure average CPU demand above100%, and it does not fix TCP
receive/reconnect failures. Those remain independent qualification blockers.
