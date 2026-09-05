# Diagnostic: original full-buffer live-radio profile

2026-09-05, source `7f10ef6`, before DMA recovery changes. Not an ordinary
image: AUDIO_PROFILE ON, 5000-ms windows, saved radio station, trace OFF.
CPU160/QIO40, mono Helix MP3 SSO/AAC, GPIO3 PDM32, 2 x 512 words.

App: 692448 bytes. SHA-256:
`8FDF86C2E289F9B641177DCE140EC935051D4D185F19F35AC6DC9F3CBA47B944`.

Physical Retro FM window: 3.915/5.023 s audio/wall, 106 missing-buffer events,
zero FIFO-empty flags, intended 16-KiB IRAM arena. The original full-size
neutral retries amplified producer starvation. Superseded; not left installed.
[Results](../../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).
