# Small TV flash backup

Complete flash snapshot read from the connected device on 2026-10-10 at
16:42:40 UTC (18:42:40 Europe/Budapest).

## Identified hardware

- Controller: ESP32-C2 / ESP8684H, silicon revision v2.0.
- CPU: single-core RISC-V, maximum frequency 120 MHz.
- Flash: 4 MiB (4,194,304 bytes), embedded; manufacturer ID `0xc8`,
  device ID `0x4016`. esptool identifies the flash vendor as GD.
- Crystal: 26 MHz.
- MAC address: `58:2a:bd:28:7d:54`.
- USB adapter: CH340, VID `1a86`, PID `7523`; capture port: COM8.
- On-chip SRAM: 272 KiB, including 16 KiB used for cache, according to the
  [Espressif ESP8684 datasheet](https://documentation.espressif.com/esp8684_datasheet_en.html).
  Free runtime RAM was not measured.

## Files and verification

- `full-flash.bin`: all flash bytes from address `0x000000` through `0x3fffff`,
  including firmware, partition data and any saved device settings.
- `full-flash.bin.sha256`: SHA-256 checksum of the complete binary.
- `manifest.json`: capture details and verification result.

SHA-256:

```text
5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4
```

esptool 5.2.0 read the snapshot at 460800 baud. A subsequent `verify-flash`
operation against the connected device succeeded with a matching digest.
The archived copy was also checked against the original size and SHA-256.
No flash was written or erased. An application reset was issued after the
capture; application startup was not independently verified.

The binary is stored with Git LFS. Run `git lfs pull` after cloning to obtain
the complete backup file.
