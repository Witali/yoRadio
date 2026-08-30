# ESP8266 native development artifact

- Source revision: `eed1ac0`
- Target: ESP8266EX, 4 MiB flash
- Framework: ESP8266 RTOS SDK v3.4
- Profile: development, diagnostic logging enabled, `-O3`
- Features: HTTP radio streams, Helix MP3/AAC, WebUI-only display profile
- Application flash offset: `0x10000`
- File: `app.bin`
- Size: 654624 bytes
- SHA-256: `564820FBEE7FD98199D41C805143D3DD7D2BC23D3082C0479AE52A5A0333CDD1`

## Changes

- Backported the standard ESP HTTP Server asynchronous request lifecycle to
  the ESP8266 server component.
- Moved SPIFFS WebUI pages, compressed assets and the playlist to a bounded
  worker queue so their socket sends cannot block WebSocket/status handling.
- Configured one 3072-byte static-content worker and a 20-second send timeout
  to preserve ESP8266 RAM.
- Protected worker-owned sockets from the HTTP server receive loop and LRU
  eviction until `httpd_req_async_handler_complete()` releases them.

## Validation

- Clean firmware build completed successfully.
- All 218 repository regression tests passed.
- Flashed the application to a physical ESP8266EX on COM10 without replacing
  NVS or SPIFFS.
- Loaded the page shell, six compressed WebUI assets and the 53,808-byte
  playlist concurrently; all returned HTTP 200.
- Received 46 WebSocket ping replies during the concurrent transfers.
- Startup log reported 47,632 bytes free after creating the static worker and
  36,032 bytes free after DHCP initialization, with no reset, stack fault or
  allocation error.