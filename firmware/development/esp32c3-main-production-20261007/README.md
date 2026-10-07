# ESP32-C3 OLED production firmware — 7 October 2026

Built from clean main commit `a06181cf` using ESP-IDF 6.0.2.
Embedded version: `v0.9.693-1220-ga06181cf`.

- `app.bin`: native WebUI OTA application, 1,401,008 bytes.
- `sdkconfig`: exact generated build configuration.
- `manifest.json`: source identity, application/ELF/configuration hashes.
- `deployment.json`: OTA response, running image identity, configuration/file
  preservation checks, and short playback observations from the physical board.

Uses the normal production defaults: DIO 80 MHz, full AAC Plus, custom FLAC,
Vorbis repair, no deep sleep, no console or firmware logs. Compact AAC storage,
direct DMA PCM, output priority override and experimental RX modes are off.

The OTA update writes only the application. Wi-Fi credentials and the playlist
are not part of this image. Their preservation is checked in memory; neither
their contents nor credential hashes are saved in the deployment report.

This is a replaceable development artifact built with the production profile,
not a versioned release. The deployment smoke test verifies identity, settings
and status-based playback; it does not establish acoustic continuity or full
codec qualification. See the report's `result` for the measured outcome.
