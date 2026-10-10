# Quiet output health: real C3 HTTPS playback

Physical result: **7/8 checks**, with the original **memory headroom FAIL**
retained. See `physical/files/report.json` and `review.json`.

- 600-second public HE-AAC 64 kbit/s observation; 44.1 kHz stereo checked with
  FFprobe and an independent unquantized FAAD reference capture.
- 584.019 seconds after the startup window: 507 paired observations,
  **zero completion-queue drops and zero I2S write errors**.
- 540 lifetime-health observations, one boot identity, zero allocation failures
  and task-watchdog events. Minimum sampled free heap 20,684 B.
- One sample at 76.475 s: largest block 7,424 B, below the unchanged 8,192 B
  budget; current free heap 24,668 B. This is not an observed OOM.
- Longest paired status/health response 200.19 ms. The historical seven-second
  response did not recur; its cause remains unresolved.
- Idle largest block returns to 114,688 B; task count remains 16.
- Exact listened image restored by OTA, settings verified, three stopped states.

## Image and host evidence

Candidate app SHA-256:
`ada20228227e7fc6af79de6ba01d26b4da2b98b140a1faca4ab9c398f53df99d`.
Saved firmware: `firmware/development/esp32c3-idf-6.1-r9a97-quiet-output-health/`.
Configuration and public trust bundle match the prior quiet candidate.
All 119 AAC/FLAC sections in 18 objects match; 48/50 application objects retain
identical code/constants. Only output and WebUI code change. The overflow ISR
is 18 bytes in IRAM, contains no function calls and fits previous padding.
Additional persistent RAM is 8 bytes.

Actual C host checks pass under ASan/UBSan. Four staged/direct/profile variants
each cover 432 PCM cases and produce identical 12,331,776-byte PCM hashes.
The normalizer adds 648 cases with zero PCM deviation. Raw generated PCM and
test executables are excluded; reports, logs, sources and hashes are retained.

## Offline review

From the worktree root:

```text
python -B tests/results/esp32c3-output-health-20261010/review.py
```

This replays recorded gates against raw samples using frozen test sources,
including the failed gate, and verifies restored image/settings. Its PASS
means the evidence agrees; it does **not** turn the physical 7/8 into 8/8.
`index.json` hashes all archived files except itself. Build sources and
configuration identify inactive local CLZ work, excluded by build flags.
Do not run `physical.py`, `prepare.py`, `build.ps1` or `freeze.py` as a replay:
these are retained orchestration sources, not read-only replay commands.

The candidate is not production-qualified. Follow-up should measure allocation
requirements and lifetimes under TLS frame growth before changing reserves or
the memory threshold. Output counters are service indicators, not an analog
recording or a universal no-gap guarantee. This run covers one live stream.
