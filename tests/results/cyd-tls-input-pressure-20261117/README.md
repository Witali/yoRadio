# CYD input-slot reclaim with a live TLS stream

The ESP-IDF 6.0.2 PDM build uses the [combined TLS profile](../cyd-tls-combined-options-20261117/README.md).
Static RX, early MPI and input reclaim are enabled. The test uses the
production stream, decode and output tasks in dual-core QEMU OpenETH.
After PCM starts, the [diagnostic probe](../../target/cyd_full_app_openeth_qemu/input_pressure.c)
holds temporary internal RAM on the stream task between HTTP reads.
It calls Mbed TLS's actual allocator once while static RX is loaned
and the production input pool has an idle slot.

The 1,536-byte request fails on the first allocation attempt and
succeeds during the same call after reclaim frees one idle slot.
The resident count drops from eight to seven and stays above the
four-slot floor. The published health counter records exactly one
failed allocation, with the request size and internal 8-bit heap
capabilities. The probe frees its temporary allocations before
the stream task reads again.

Both final runs reached EOF with the full 706,319-byte TLS response,
43 full records and the exact 1,058,176 bytes accepted by PDM. All
528,000 decoded PCM frames matched the no-pressure control's MD5.
WebUI served the asset during playback after reclaim and again after
EOF. The static reserve returned when the TLS connection closed.
The controller rejected the image without the pressure probe despite
observing PCM output from that image.
[Measurements and digests](observed.json)

An initial output-task probe observed a run with every encoded slot
occupied. The allocation failed and reclaim released zero slots.
Running the final probe on the sole producer removes that race from
the recovery case. Both the early probe and a producer-probe run
recorded an IDLE1 watchdog event during Espressif CELT decoding after
recovery. The [CYD caller](../../../idf/esp32-cyd2usb-native/main/audio_service.c)
now checks the existing 20 ms scheduler budget after each public
simple Ogg decoder call. A two-tick delay gives idle an opportunity
even when a delay starts near a tick boundary. The watchdog remains
active at five seconds. The two final runs recorded zero watchdog events.

[The wrapper suite](../../run-ogg-playback-host.py) passed 116 cases under
ASan/UBSan, including checkpoints after each vendor call and cancellation
before the frame is published. The gain and Family 1 regressions also passed.

[Fixture and reproduction](../../target/cyd_full_app_openeth_qemu/README.md#input-reclaim-under-allocator-pressure)
