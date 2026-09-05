# Rejected intermediate diagnostic: prefix-only LAN profile

2026-09-05 development snapshot based on `7f10ef6`, during work leading to
`aab3600`. It predates short neutral retries and is NOT the final source.
AUDIO_PROFILE ON (5000 ms), automatic profile URL
`http://192.168.100.253:8765/stream.bin`; no playlist/settings upload.
CPU160/QIO40, mono Helix SSO/AAC, GPIO3 PDM32, 2 x 512 words, compact ISR.

App: 692544 bytes. SHA-256:
`0D7605374F28DA32FCCA7F095BC5D45C1158CC0AD55D0AE6A02CB7242F5AE66E`.

Physical IRAM arena fits, but LAN receive gaps dominate this capture
(1–2 kbit/s in some windows); not a valid speed or listening acceptance.
Retained for evidence only; superseded and not left installed.
[Results](../../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).
