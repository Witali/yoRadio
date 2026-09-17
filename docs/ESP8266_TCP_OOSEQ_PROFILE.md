# Diagnostic TCP out-of-order queue profile

`build_i2s_pdm_production.ps1 -Diagnostic -NoTcpOutOfOrder` disables
the SDK's `CONFIG_LWIP_TCP_QUEUE_OOSEQ`. It is opt-in, requires a fresh named
build directory, validates the effective sdkconfig before building, and
records `tcp_queue_ooseq` in the firmware manifest. Production/default
profiles retain the queue. No board is flashed by this build option.

The pinned Espressif RTOS SDK's `components/lwip/Kconfig` explicitly
documents the trade-off: disabling this queue saves memory during TCP
sessions but increases retransmissions when segments arrive out of order.
TCP still delivers ordered, reliable bytes; this is not permission to
discard bytes in the application or bypass Ogg CRC. The option affects
both the audio client and WebUI server, so both need live testing.

Motivation: previous Opus telemetry observed retained out-of-order payload
after closing a stream, and low heap/reserve failures on reconnect. That
does not establish the initial cause of receive stalls. The experiment
tests whether reducing that retention improves real radio playback without
adding buffers or changing the decoder. It must not be described as a
proven fix before uninterrupted PCM/DMA, RAM and WebUI are measured.

Do not substitute the similarly named L2/L3-copy option without tracing
the actual ESP8266 Wi-Fi input path: its Kconfig help includes ESP32-specific
buffer counts, whereas this project's pinned `wlanif.c` accepts custom
pbufs directly. The number25 in that help is not a measurement of this board.

Host regression:

```powershell
node --test tests/esp8266-tcp-queue-profile.test.js
```

The test runs the actual PowerShell transformation/cache guard without
building or flashing, verifies all four enabled/disabled combinations,
preserves unrelated settings and checks that the default profile is unchanged.
