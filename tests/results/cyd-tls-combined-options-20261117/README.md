# CYD static RX, early MPI and idle reclaim on PDM

The full-application QEMU OpenETH profile used ESP-IDF 6.0.2, dual-core
ESP32, PDM, the ST7789 status display and the production five-second task
watchdog. The generated SDK configuration differed from the static-RX
control only in `CONFIG_YORADIO_TLS_EARLY_MPI_LOCK` and
`CONFIG_YORADIO_TLS_INPUT_RECLAIM`. The ELF contains the early MPI call
in `app_main`, the reclaim binding in `audio_service_start` and the
Mbed TLS allocator wrapper. Both runs completed without a binding
warning.

The Opus run received all 706,319 bytes over verified TLS 1.2, using 43
full 16,384-byte body records and a 1,807-byte tail. The PDM driver
accepted exactly 1,058,176 bytes. WebUI returned the same 13,588-byte
asset during playback and after EOF. The minimum free heap was 13,632
bytes. During the WebUI sample the largest free DMA block was 18,432
bytes. There were zero allocation failures, output faults or watchdog
events.

The OTA run separately passed Stop/Play, recovery from a truncated
image and the complete same-image update to `app1`. The controller
checked the software restart, then WebUI and a new TLS Opus session.
Four independent TLS connections borrowed and returned the static
buffer. Both runs verified the original backing flash digest.
[Observations and digests](observed.json)

Start with the [static-RX PDM profile and probes](../../target/cyd_full_app_openeth_qemu/README.md#tls-reconnect-and-ota-during-playback).
Enable the two additional Kconfig flags and run the OpenETH controller
once with `--through-eof --full-tls-records` and once with
`--radio-ota-lifecycle`. The [isolated SDK/QEMU pressure test](../cyd-tls-traffic-20261101/README.md)
covers allocator failure and recovery with two clients. The full
application runs above cover ordinary traffic and actual OTA over
OpenETH. Allocator pressure in the full application and physical Wi-Fi
remain open.
