# FIR ON live diagnostic — 2026-09-10

Source3f72f25, app884848B, CPU160/QIO40; Opus fixed-point, WordASM,
ICDF-word and FIR-word enabled. I2S PDM32 GPIO3, two512-word DMA buffers.
No raw benchmark task/fixtures or FreeRTOS runtime stats. Diagnostic stream
and wall-stage endpoints available; default board profile unchanged.

Installed through OTA into app1/0x110000. SPIFFS/Wi-Fi/playlist preserved.
DLF Opus24 via HTTP redirects was rejected by the existing20ms packet bound.
The supported56kbps Opus stream produced PCM, but the second health snapshot
timed out: uninterrupted playback was **not** confirmed. Both reports retained.
Explicit stop succeeded; playing=false, free_heap27324B, RSSI−59dBm.
This image remains installed, stopped. Not a continuous-audio qualification.

See [complete results](../../../docs/ESP8266_OPUS_FIR_WORD_BENCHMARK.md).

After the two unsuccessful CELT pulse-cache experiments this same image
was restored by OTA into app0/0x10000 (pulse-restore-ota.json). First boot
observation timed out; the next confirmed Wi-Fi RSSI -58dBm, playing=false,
free_heap27612B, no application error. SPIFFS/playlist unchanged.
This replaces the earlier installed-slot description, not the binary.

Rejected pulse code/build flag and temporary test hooks were removed from
the working decoder, with source retained in Git9e40898/f20ed03 and reports
in pulse firmware directories. After removal, 22 phase/PLC cases and 22
real-ICDF-word PCM comparisons pass against pristine generic32, ASan/UBSan
entropy unit passes, and FIR five-fixture/mixed PCM remains exact (saved
as pulse-removal-pcm-results.json). Suite:21 tests pass,2 expensive wrappers
skip by default; both corresponding full runners were executed separately.
No new continuous-audio qualification is claimed.
