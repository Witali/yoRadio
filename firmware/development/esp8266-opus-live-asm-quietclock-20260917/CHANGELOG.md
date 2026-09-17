# Clock compensation plus rebuffering — 2026-09-17

All18 accepted ASM stages, CPU160/QIO40, I2S PDM32 GPIO3. App PCM2x960,
DMA2x128, input2048, scratch6144/reserve4096, LED OFF. Includes rebuffering,
48-byte autonomous diagnostic window and624-to625 clock interpolation.
Image890272 bytes, SHA256:
3b5e113cadecee605686a96fc48811e6647b1c86eb16e4400b9da9dfdee77cb7

ASM rebase/proofs PASS. OTA PASS to0x110000; no UART or SPIFFS changes.
Kultur24 autonomous window:25.040s PCM/25.001s board,22 underruns, FAIL.
No requests from the runner during its65s wait. Clock compensation has
not demonstrated a continuity improvement. No acoustic verification.
This image remains on the board at the user's shutdown request. Not default.
