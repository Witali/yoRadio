# ESP32-C3 PC19 network qualification image

Awake ESP32-C3 OLED application, DIO 80 MHz, CPU 160 MHz, Flash Auto Suspend
off, with full SBR/PS, compact QMF history, late-SBR retention, checked FIL
parsing, native profile reporting and CPU/network diagnostics.

Executable source commit: `ee920c0b`. The image was built immediately before
that commit, so its embedded version retains `1d68e0b4-dirty`. Use the exact
image/ELF/config hashes in `manifest.json`, not the version string alone.

Installed and tested through application-only WebUI OTA. The mixed-codec
matrix, 21 switches and five-minute HE-AAC HTTPS run passed. The initial load
run also contains a HE-AAC status timeout and MP3/Vorbis/Opus free-heap decline
failures. An isolated HE load repeat passed; the original failures are retained.

This is an unreleased test image, **not a qualified production default**.
See [the report](../../../docs/ESP32C3_AAC_PC19_NETWORK_20261004.md) for exact
coverage, limitations, CPU/heap measurements and reproduction commands.
