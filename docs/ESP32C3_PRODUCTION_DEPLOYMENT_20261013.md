# ESP32-C3 production build and deployment — 2026-10-13

## Build

- Source: merged `main` snapshot `7993c426` in an isolated worktree.
- Version: `idf61-prod-20261013`.
- ESP-IDF 6.1 revision: `9a97f6c54ec638111ce55cd36581b3c192f15207`.
- [Application and manifest](../firmware/development/esp32c3-idf61-production-20261013/).
- Application: **1,461,376 bytes**, within the 1,900,544-byte OTA slot.
- Application SHA-256: `f31ffba883053cf33d7f2e928bf529e5cbcac8f14a8aafd172e835a027684631`.
- ELF identity: `dc06c1a61da089e10f4d22855f05b7e0e4168e35b1810c40751472ccdad9cbe8`.

Built with `build-production.ps1 -TestedRadioProfile`, from a fresh SDK
configuration. The [build recipe and evidence](../tests/results/esp32c3-production-deployment-20261013/)
include the configuration/link audits, deployment controller and observations.

## Selected improvements

QIO at 80 MHz, fractional divider for nominal 48,000 Hz PCM, output task
priority above decoding, full-rate AAC/SBR/PS with compact storage, repaired
Vorbis, custom FLAC, the 17,058-byte TLS RX reserve, bounded adaptive input
storage, one-second input prefill and HTTP request-buffer release are enabled.
This build also incorporates the merged WebUI memory changes: bounded file
serving and a 2 KiB upload buffer allocated on demand.

Production logging and deep sleep are disabled. HTTPS uses the normal public
certificate bundle. Experimental frame routing/startup confirmation, early
compact SBR owner reservation, the shared decoder arena and direct DMA decode
remain disabled. Merging their implementation did not enable them in the
production profile.

## Installation and verification

Installed through WebUI application-only OTA. The application identity and
new OTA partition were verified after reboot. Wi-Fi credentials, playlist and
settings were compared in memory before and after installation and remained
unchanged; private settings were not saved in the evidence. The bootloader,
partition table, NVS and SPIFFS were not written. The existing QIO bootloader
remains installed; its initial DIO image header is expected.

Build/link audits checked full AAC support, HTTP client integration and TLS
allocator routing. A 60-second local, paced HE-AACv2 44.1 kHz stereo smoke
test checked format, decoded PCM rate/channels, decoder faults, memory
allocation failures, watchdog events and sustained output error counters.
The final state is stopped, matching the state before installation.

All deployment checks passed. The 44.709-second post-warmup output window
contained 81 paired observations: zero completion queue drops and write
errors. Across playback there were zero decoder failures, allocation failures
or watchdog events. Minimum sampled free heap was **39,308 bytes**, with a
minimum largest free block of **30,720 bytes**.

## Scope

This is a production **configuration** and a deployment smoke test. The full
codec, network-fault and OTA regression matrix was not rerun for this image;
`production_qualified` remains false. Prior test evidence on other images is
not a qualification result for this binary. Software output counters do not
measure analog sound quality. See the [remaining work](ESP32C3_MEMORY_STABILITY_TODO.md).
