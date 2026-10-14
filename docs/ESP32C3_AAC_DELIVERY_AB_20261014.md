# AAC-LC delivery-pause comparison, 2026-10-14

## Question and result

The continuous-confirmation candidate records 27 steady DMA completion-queue
drops during one public 128-kbit AAC-LC HTTPS observation. This experiment asks
whether identical local delivery pauses reproduce a difference between that
candidate and the installed production image.

**All three preplanned runs pass 10/10 checks:** production, candidate, then
production again. Each observes 80 seconds of the same synthetic AAC-LC file,
including all three delivery pauses. No new steady completion drops, write
errors, allocation failures, decoder failures or watchdog events are recorded.
This does not reproduce or explain the public HTTPS failure. It does not
establish equal maximum buffering capacity or exclude TLS-specific effects.

## Controls

- Production app: `f31ffba883053cf33d7f2e928bf529e5cbcac8f14a8aafd172e835a027684631`.
- Candidate app: `832ad10f31dbfa2aebe1b9b01012a4b2c4fab3a7bad75bfce45e3c7cc84375bb`.
- The candidate adds continuous framing and early compact AAC ownership; this
  compares those complete images, not an isolated single-flag trial.
- One generated 100.032-second, 44.1-kHz stereo AAC-LC file at nominal
  128 kbit/s, 1,657,641 encoded bytes. FFprobe validates LC/rate/channels;
  independent FFmpeg PCM length matches the parsed ADTS frame count.
- The synthetic file and generation command are retained. The archive contains
  no downloaded broadcast content or private settings.
- Plain HTTP, pacing ratio 1.0, actual host socket send buffer 4,096 bytes on
  every run. No TLS qualification is inferred from this comparison.
- Pause before encoded offsets 414,279 / 745,703 / 1,077,126 for
  100 / 250 / 500 ms, respectively (approximately source seconds 25/45/65).
  The server resumes the original timeline after each pause.
- Existing output acceptance excludes the first 15 seconds and retains
  nonzero counters as failures. No limits or priorities were relaxed.

## Measurements

| Run | Checks | New steady drops / write errors | Sampled minimum free / largest | Actual pauses, ms |
| --- | --- | --- | --- | --- |
| Production before | 10/10 | 0 / 0 | 63,352 / 45,056 B | 113.5 / 252.0 / 503.6 |
| Candidate | 10/10 | 0 / 0 | 63,364 / 32,768 B | 103.7 / 260.8 / 507.2 |
| Production after | 10/10 | 0 / 0 | 63,440 / 47,104 B | 108.3 / 260.4 / 512.0 |

The three steady windows contain 57 paired observations each and span
64.493 / 64.523 / 64.332 seconds. All 274 health samples have zero recorded
allocation, decoder and watchdog faults. Settled memory recovery passes in
every run. Each run retains its own boot; intervening app-only OTA changes
are explicit. Final production firmware and settings are verified restored,
with playback stopped.

All pauses complete within the predeclared -5/+50-ms host timing tolerance.
Host write timing is not device receive timing: TCP buffering can hide part
of a pause. No acoustic, PCM accuracy, CPU-utilization or maximum-jitter-margin
claim is made. The smaller active largest block on the candidate is diagnostic;
no allocation failure or persistent recovery failure occurs.

## Reproducibility and next step

[Raw observations, sources, fixture, controller and independent replay](../tests/results/esp32c3-aac-pause-ab-20261014/summary.json)
retain all three runs. The first controller attempt failed on a missing host
module import before playback; its record is retained separately. It did not
test the firmware. After correcting the import path, the full A/B/A plan ran
once without modifying its schedule or gates.

The reusable `local_sustained.py` runner accepts `--delivery-pause` and
`--send-buffer-bytes`, preserves measured output counters on failure, and
requires actual pause evidence. Three evidence-validator tests and six HTTP
server pause tests pass. The first sandboxed server-test attempt was denied
loopback socket access (WinError 10013); the permitted loopback run passed.

Next compare the public AAC-LC source on the original image, then use matched
TLS delivery and existing pipeline phase/age telemetry if needed. The prior
27-drop event and independent WebUI TCP timeout remain open. Do not enable
continuous confirmation by default on the strength of this passing HTTP test.
