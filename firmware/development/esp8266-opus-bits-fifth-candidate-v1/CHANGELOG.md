# 2026-09-15 — exact last PVQ search-step shortcut

- Preserves the original six-step selection while skipping a redundant last
  probe when the remaining interval is at most one. Two fixed ASM ranges,
  unchanged surrounding addresses, tables, RAM, stack frame and image size.
- Correctness: actual linked-instruction proof, all23 standard tables and
  378304 budgets;24 host PCM/state cases including320/510kbps and compound
  packets. Original C fallback remains available.
- Thirty physical raw tests:10 control,10 candidate,10 repeated control.
  CPU192 medians87.33733 /86.77006 /87.31838%; both high-bitrate gates pass.
  Accepted only as experimental raw baseline; production default unchanged.
- All attempts, maximum calls, memory minima and timing-window excesses are
  retained in comparison.json, controls/ and runs/. Final regression log is
  final-tests.log:91 related tests PASS/0skip in67.45s. This is not a complete
  repository-wide test run.
- Ordinary radio restored through native application OTA; root HTTP200,
  WebSocket, stopped station167 and playlist hash verified. No UART commands,
  flash partition, bootloader, Wi-Fi credentials or SPIFFS replacement.
- Still not qualified:80% raw CPU target and continuous live I2S PDM/WebUI.
  Candidate maximum192kbps call21.746ms; raw tests have no audio output.

[Detailed method and results](../../../docs/ESP8266_OPUS_ASM_BITS_FIFTH.md).
