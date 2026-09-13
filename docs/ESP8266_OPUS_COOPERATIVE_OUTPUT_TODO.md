# Opus: cooperative PCM draining without another task stack

Status: hypothesis, NOT implemented or qualified. 2026-09-13.

The synchronous radio path decodes a complete coded frame before supplying
PCM. Current DMA512 capacity is at most21.33ms; a partly consumed/filled
descriptor provides less. Raw CPU averages below100% do not establish that
each individual decode fits this deadline.

The existing asynchronous PCM experiment has two960-sample leases and
DMA256. It adds a separate consumer stack/TCB and has not passed live RAM
or continuity qualification. Repeating it with a larger queue is not the
next step unless the actual memory budget changes.

## Candidate to investigate after the ASM A/B and fresh live trace

Use the same audio task to drain the previous ready PCM lease at explicit
safe checkpoints during the next frame's decode. No RTOS task is added;
this is cooperative scheduling, not PCM production from an ISR. Keep two
960-sample PCM16 slots and two256-word DMA buffers, with explicit ownership.
Relative to synchronous DMA512, PCM grows1920B and DMA shrinks2048B: nominal
payload saving128B BEFORE control state and increased call-chain stack.
This calculation is not a measured net memory saving.

- [ ] Measure the longest CELT/SILK regions between potential checkpoints;
  choose a bounded service interval compatible with5.33ms DMA256 duration.
  Wi-Fi preemption still needs headroom; adding checkpoints cannot remove it.
- [ ] Design a nonblocking output pump: reserve only currently writable DMA,
  convert only accepted PCM, publish promptly, return when no span is free.
  A failed reserve must not consume PCM, advance the modulator, or reset the
  resampler. Do not reuse the blocking write API as a polling primitive.
- [ ] Prepare normalization/gain once per original callback boundary, not
  every checkpoint. Preserve PCM/PDM bits, volume semantics and source status.
- [ ] Call checkpoints outside allocator/RTOS critical sections and before
  retaining writable DMA loans. No decoder re-entry, nested lease acquisition,
  packet-buffer mutation, or new allocation in the hot path.
- [ ] Stop/cancel discards unpublished PCM and releases each lease exactly
  once. An OOM longjmp must not strand output state or loans.
- [ ] Target stack call-chain audit and watermark: nested decoder + output
  calls share a stack and may exceed the old maximum. Preserve the5KiB main
  stack minimum and4KiB decoder reserve; reject unsafe results.
- [ ] Compile-time experimental C path, default OFF. Existing pinned ASM
  snapshots must not silently inherit a changed ABI or callback contract.
- [ ] Host exact PCM/PDM, ownership and fault tests, then physical flash-only
  and real-radio tests, ten attempts,>=20s uninterrupted qualifying windows.
  Record CPU, longest calls, DMA underruns, heap/largest block and all errors.

If average CPU is already exhausted, this only redistributes latency and
cannot solve overload. Network starvation and reconnect allocation failures
remain separate cases and must not be excluded from real-radio qualification.

Evidence: [PCM queue](ESP8266_OPUS_PCM_QUEUE.md),
[DMA capacity](ESP8266_OPUS_DMA_CAPACITY.md),
[partial publication](ESP8266_OPUS_PCM_PUBLICATION.md).
