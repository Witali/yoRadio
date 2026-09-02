# ESP8266Audio WebRadio development firmware

- Built: 2026-09-02
- Target: Wemos D1 mini / ESP8266EX
- Framework: ESP8266 Arduino core 3.1.2
- Audio library: ESP8266Audio 2.4.1
- CPU: 160 MHz
- Flash: 4 MiB, QIO at 40 MHz (`E9 02 00 40` image header)
- lwIP: v2 higher bandwidth, features enabled
- Audio input: HTTP/ICY, fixed 5 KiB compressed buffer
- Decoders: ESP8266Audio MP3 and AAC, shared 29,192-byte workspace
- Audio output: `AudioOutputI2SNoDAC`, mono delta-sigma/PDM on GPIO3
- Application binary: `app.bin`, 554,784 bytes
- SHA-256: `4DE5D8E0D1D29274F99BE821EA93601E5DC830AB6839AEAD4C49DD87EA64D9DE`

Arduino build report:

- static RAM: 35,060 / 80,192 bytes (43%)
- IRAM including 32 KiB cache reservation: 61,155 / 65,536 bytes (93%)
- IROM code: 518,020 / 1,048,576 bytes (49%)

The image passed compilation and host/static tests. It has not yet been
flashed or validated on the physical board; keep the verified native RTOS-SDK
image available for restoration after experiments.
