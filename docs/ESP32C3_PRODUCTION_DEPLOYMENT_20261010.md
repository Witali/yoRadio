# ESP32-C3 production deployment — 2026-10-10

Built from `codex/esp32c3-idf-upgrade` and installed at the user's request
through WebUI application-only OTA. Wi-Fi credentials, playlist and settings
were compared in memory before and after installation and remained unchanged.
No NVS, SPIFFS, partition table or bootloader was flashed. The new application
remains on the board; playback was returned to its initial stopped state.

## Installed artifact

- [Application and manifest](../firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000/).
- Version: `idf61-production-prefill1000`.
- ESP-IDF 6.1 revision: `9a97f6c54ec638111ce55cd36581b3c192f15207`.
- Source HEAD at build capture: `ee282641`; exact source hashes and snapshots
  are archived. The existing inactive CLZ CMake overlay was preserved but its
  hardware test flag was explicitly disabled.
- Application size: 1,455,936 bytes.
- Application SHA-256: `8f086f439e00d9e4baf4fe603b1b64935c7ddd188bd6f5ea380a7202075bd664`.
- ELF identity verified on board: `73da8e2146c5b3691bcfc7a8fb46b34109e74099eac221df2b66e05a62b95245`.

Configuration: QIO 80 MHz, fractional divider for nominal 48,000 Hz PCM
output, one-second initial input prefill, full AAC/SBR/PS with the existing
compact storage, normal certificate trust, 17,058-byte TLS RX reserve,
production health counters, no pipeline profiling, console logs or deep sleep.
The bootloader config enables QIO; its initial DIO image header is expected.
This OTA keeps the previously installed QIO bootloader.

## Verification

Build/link checks passed for full AAC, HTTP implementation, allocator routing
and normal trust. All 50 application object code/data sets and static RAM/IRAM
sizes match the prior normal-trust one-second-prefill candidate. Its
[42 local cases and 15 OTA cases](ESP32C3_PREFILL1000_QUIET_20261010.md) are
existing baseline evidence, not tests rerun on this deployment.

This deployment verifies the installed ELF identity and partition, settings
persistence, 60 seconds of paced local HE-AACv2 at native 44.1 kHz stereo,
format/output/memory checks, and three final stopped-state observations.
All passed: zero completion queue drops and write errors in the 44.577-second
steady output window, zero allocation failures or watchdog events. Minimum
sampled free heap was 36,192 bytes; largest free block was 24,576 bytes.
Exact measurements, build scripts, audits, comparison and installation
controller are in the [evidence archive](../tests/results/esp32c3-production-deployment-20261010/).

## Known limits

This is the requested production **configuration**, not a claim that all
qualification gates pass. [Public MP3 interruption tests](ESP32C3_MP3_TRANSPORT_CONTROLS_20261010.md)
still fail over HTTP and HTTPS, and earlier public HE-AAC HTTPS tests crossed
the selected contiguous-memory headroom floor. These remain unresolved.
The short smoke check measures software counters, not analog audio quality.
No project defaults or release directories were changed by this deployment.
