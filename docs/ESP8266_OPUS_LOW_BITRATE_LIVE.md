# Low-bitrate Opus with the accepted ASM decoder

2026-09-17. Current task: obtain continuous real radio playback, starting
with a lower bitrate, using the accepted assembly optimizations in ordinary
firmware. This does not replace the separate raw CPU192 qualification.

## Baseline

`esp8266-opus-live-asm-ebands-final-20260917` includes all18 accepted
post-link stages. It has no raw benchmark, tone generator or function
profiler; I2S PDM32 output is GPIO3, CPU160/QIO40, two512-word DMA buffers.
Opus input1024B, scratch6144B, reserve4096B.

- Reinstalled by OTA (0x10000 -> 0x110000); 11 offline checks passed.
- R2Rock produced21.020s PCM in28.019s with5340 underrun events.
- Plaza started, but the later health sample showed a receive timeout116
  and a13.947s PCM stall. A missing HTTP response is not a decoder failure.
- The planned alternating ten-start series was deliberately stopped when
  the user requested focus on successful low-bitrate playback. Do not report
  that interrupted series as ten completed attempts.

## A real24kbps source

The root playlist's Deutschlandfunk low Opus endpoint also accepts HTTP:
`http://st01.sslstream.dlf.de/dlf/01/low/opus/stream.opus?aggregator=web`.
Its302 redirects to a HTTP200 `application/ogg` stream. Use this stable
entry URL, not a temporary redirect token. This observation does not enable
HTTPS on the ESP8266.

PC capture SHA256:
`cd78f5c533d30d45dcfe07c6b9afd700afdae688b9a33d79813bcd32b77471fa`.
99 complete pages/873 packets passed Ogg CRC inspection; all packets are
mono Hybrid, three20ms coded frames in a60ms packet, max180B. PCM output
is48kHz. FFmpeg decoded the capture successfully. The25s capture timeout
is intentional; absolute Ogg granules in a live stream must not be reported
as captured audio duration. Server `ice-audio-info` says128kbps/44.1k/stereo
and is inconsistent with the actual packets; do not use it as decoder truth.

The first measurement started during connection and is not a steady-state
qualification. Subsequent baseline windows:

| Window | PCM / board elapsed | Underrun events | Qualified |
|---|---:|---:|---|
| Sparse health30s |32.620 /33.085s|449|No|
| Health/stages25s |29.580 /30.249s|590|No|

The latter wall-time stages were decode56.70%, output38.69% (including
DMA waits), read1.52%, input wait2.02%, post-decode wait0.86%.
These are NOT raw CPU percentages. Input-wait accounted for440 recorded
misses; stage and health requests are not atomic. No acoustic recording.

## Experiment checklist

- [x] Preserve the complete accepted ASM chain; no decoder approximation.
- [x] Verify a real low-bitrate source and keep the unfiltered baseline.
- [x] Build input2048B, leaving scratch/reserve/PCM/DMA sizes unchanged.
- [x] Rebase all18 patches and verify CFGs, image bytes and unchanged RAM/
  stack against the corresponding unpatched image; two new tests PASS.
- [x] OTA and test the2KiB input variant:10 attempts, NOT qualified.
- [ ] If it is insufficient, identify the remaining deadline misses before
  changing another parameter. Do not promote a failed experiment.
- [ ] Confirm repeated starts and >=20s continuous PCM/DMA, with zero new
  underruns and audio duration matching elapsed time; retain all failures.

The input change costs1024B of dynamic DRAM while Opus is allocated,
even though static RAM and app size are unchanged. An increase in compressed
buffering does not fix insufficient average decode speed or missing PCM
output headroom. The reserve guard must not be reduced to obtain a pass.

Variant: `firmware/development/esp8266-opus-live-asm-input2k-20260917`.
App885792B, SHA256
`6bbeef7e6afd0bf8a7eace76ac6e713175912d942e5d4a445c7b9d29b0c40167`.
`live_variant.cjs <unpatched-variant> <new-variant>` performs a build-only
rebase, rejects changed evidence and unsafe names, and never flashes.
The dated original recipe/evidence are retained unmodified.

## Completed input/TCP trials

- Input2KiB with the default TCP OOSEQ queue:0/10 qualified. Multiple
  stage10 refusals show the unchanged4096B reserve was not available after
  init; six timing windows were incomplete. Minimum observed boot heap2908B.
  This is insufficient RAM, not evidence of an Opus arithmetic error.
- Input1KiB with TCP OOSEQ OFF:0/10 qualified. No init-failure stage latched;
  complete windows had450..3931 underrun events, three windows were incomplete.
  RAM retention improved but playback did not qualify. Retransmission stalls
  remain possible; disabling OOSEQ is not promoted to the board default.
- Input2KiB with TCP OOSEQ OFF and asynchronous PCM output are tested as
  separate variants. Their manifests identify the actual flags; do not mix
  their timing series or infer CPU utilization from output wall time.

Every completed attempt, including timeout/error responses, is saved under
the corresponding `firmware/development/esp8266-opus-live-asm-*/board/`.
Increased compressed input alone is not a demonstrated fix. No heap guard,
Ogg CRC, decoder correctness check or continuous-output criterion was relaxed.
