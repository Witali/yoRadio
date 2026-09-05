# Diagnostic A/B control: RAM decode and whole-buffer DMA

2026-09-05 development snapshot based on `7f10ef6`, with changes subsequently
committed in `aab3600`. RAM benchmark and real audio output ON, prefix OFF;
Wi-Fi/profile/trace OFF. CPU160/QIO40, mono Helix SSO/AAC, GPIO3 PDM32.
200 retained 320-kbit/s frames per codec, volume128/normalization off in RAM
only. The test-only 1536-byte fixture is static, not on the app stack.

App: 282784 bytes. SHA-256:
`A9BC13EF9DC8213DB0CB5021423C17F880E0875F792EB7C704D68263CB456E06`.

MP3: 4.800 s audio / 4.785245 s wall, zero underruns. AAC: 4.266666 / 4.371473 s,
11 long neutral retries. FIFO-empty=0, IRAM arena16384, stack headroom1496.
Lifecycle returned initial heap. Diagnostic only; ordinary firmware restored.
[Results](../../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).
