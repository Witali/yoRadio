# Opus investigation: stopped at user request

2026-09-09: stop work, save/commit/push, shut down. Do not resume tests or
flashing unless the user requests it. Continuous Opus playback is NOT fixed.

## Completed and saved

- Opus already uses fixed-point arithmetic, with no soft-float/libm imports
  in its target archive. See ESP8266_OPUS_FIXED_POINT.md.
- Decoder-only ICDF A/B passed exact PCM checks. ON mean CPU: SILK12 58.20%,
  Hybrid24 91.85%, CELT64 74.35%, CELT128 90.03%, CELT510 150.91%. Network
  and PDM output are excluded; this does not qualify whole-pipeline playback.
- Sparse local SILK12 tests still have short DMA underruns. Frequent HTTP
  observations reproduce RX timeout and reconnect. Failed samples retained.
- PDM batch passes bit-exact host tests, but its physical run was interrupted
  by network timeout: no physical speed improvement is established yet.
- SDK RX/TX diagnostic counters occupy 32 bytes, OFF by default. All five
  observed error counters stayed zero during a timeout, while the own PC
  server recorded TCP retransmissions/RTO. Closed-driver/RF loss is unobserved.
- A later uncommanded boot was observed (uptime/generation reset); RSSI then
  was -82 dBm. Cause unknown. The stopped-state sparse capture is invalid
  as a playback performance measurement.

## Physical board

Last OTA: firmware/development/esp8266-opus-sdk-rx-diag/app.bin, source
4fa9043, 882704 bytes, app1 at 0x110000. Standard I2S PDM32 on GPIO3,
2x512-word DMA, CPU160/QIO40. Word ASM/PDM IRAM ON; ICDF/PDM batch OFF.
SPIFFS logging/runtime statistics OFF. Last observed state: stopped.

Source 2f42838 adds diagnostic reset_reason but has NOT been built/flashed.
A later OTA cannot retroactively report an earlier reset reason. No USB
serial operations were performed and no production default was changed.

Firmware/results are in firmware/development/esp8266-opus-* with CHANGELOGs.
Compressed raw own-server TCP_INFO logs accompany the SDK diagnostic artifact;
these describe local synthetic-fixture traffic, not credentials/radio captures.
The local fixture server was stopped before shutdown.

## Pending candidates, not applied or qualified

1. Capture reset reason and correlate RSSI/transport state.
2. Repeat PDM batch A/B over a stable interval without EOF/reconnect.
3. Consider skipping per-packet task delay only if output already blocked on
   DMA; do not remove yielding unconditionally.
4. If needed, measure peak decode/refill wall time and DMA reservation misses.

Unrelated pre-existing Arduino WebRadio source, firmware and test moves remain
in the working tree; they are preserved and excluded from the Opus commits.
