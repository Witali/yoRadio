# ESP32-C3 receive credit diagnostic image

Awake PC19 and late-SBR firmware with optional TCP receive-window telemetry.
DIO 80 MHz, CPU 160 MHz, Flash Auto Suspend off.

This unreleased diagnostic image is not a qualified production default.
Use manifest.json for exact image, ELF and configuration identities.

Application-only OTA passed. Three 60-second ordinary HTTP file-download load
tests and all idle-recovery checks passed on MP3, Vorbis and Opus. Longer paced
tests retain heap-decline failures and a post-Vorbis fragmentation failure.
HE-AAC HTTPS played from the fragmented state, but its heap gate also failed.
See the [measured results](../../../docs/ESP32C3_RECEIVE_CREDIT_20261004.md).
