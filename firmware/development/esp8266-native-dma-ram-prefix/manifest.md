# Rejected intermediate: RAM decode with prefix-only DMA

2026-09-05 development snapshot based on `7f10ef6`, leading to `aab3600` but
BEFORE short neutral retries. Not equivalent to the final prefix-ON build.
RAM benchmark/real output ON, prefix-only ON, Wi-Fi/profile/trace OFF.
CPU160/QIO40, mono Helix SSO/AAC, GPIO3 PDM32, 2 x 512 words; RAM-only test
volume128, normalization off. Persistent settings were not overwritten.

App: 282832 bytes. SHA-256:
`3BDCC7BB1967176FB2A7C93A7C3CDD1CBB7055493899651079EA29040D44A948`.

MP3: zero underruns, 4.800/4.786369 s audio/wall. AAC: 4.266666/6.381378 s,
200 long neutral retries. FIFO-empty=0. Rejected: prefix handoff alone did
not prevent a bad deadline phase. Not left installed.
[Results](../../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).
