# Accepted ASM radio with SDK RX diagnostics — 2026-09-17

All18 accepted stages, ordinary radio, I2S PDM32 GPIO3, synchronous DMA512,
input1024B/scratch6144B/reserve4096B, CPU160/runtime QIO40. Existing SDK
diagnostic overlay adds32B counters; installed SDK is not modified.
App886256B, SHA256
`cc17d2ef2356f699c4f1051c840769ec77fb9ec60f4bb54312974095745ed003`.

Rebase v2 checks actual reachable literal readers instead of misdecoding
alignment padding. Every accepted hot graph and unmodified ELF byte remains
verified. Ten image/literal checks pass. OTA switched0x110000 to0x10000.
Live DLF24 steady interval:45.080s PCM in46.015s elapsed,853 DMA misses.
SDK RX/TX failure counters stayed zero, live custom pbuf3..4, peak7.
Not qualified for uninterrupted playback. No acoustic recording.
