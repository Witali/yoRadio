# WebRadio development firmware

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
- Application binary: `app.bin`, 554,672 bytes
- SHA-256: `A449EFBE63A1E11329C1045F47C1A173CC6C3B81EDA66D52FB13DE503B7BB7CC`

Arduino build report:

- static RAM: 35,044 / 80,192 bytes (43%)
- IRAM including 32 KiB cache reservation: 61,155 / 65,536 bytes (93%)
- IROM code: 517,940 / 1,048,576 bytes (49%)

The image passed compilation and host/static tests. On 2026-09-03 it was
flashed to the physical Wemos D1 mini on COM8; esptool verified the written
data hash and hard-reset the board. UART reported `WebRadio` and the setup AP
at `192.168.4.1`. A Realtek client measured -41 dBm, received `192.168.4.2`
by DHCP, and fetched the 738-byte Wi-Fi setup page with HTTP 200. The returned
page title and heading were both `WebRadio`.
