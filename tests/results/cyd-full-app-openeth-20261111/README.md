# CYD full application in QEMU over OpenETH

The current production CYD image still stops in `register_chipv7_phy` at
`0x60033c00`. The [OpenETH diagnostic](../../target/cyd_full_app_openeth_qemu/README.md)
ran the same radio, WebUI, TFT and audio code past the Wi-Fi startup boundary.
The new startup case changes the transport only. The resource profile also
enables telemetry, extends the task watchdog from 5 to 30 seconds and adds a
local CA for the TLS station.

| Run | Observed result |
| --- | --- |
| Five-second watchdog, regular SPIFFS | OpenETH obtained IPv4 and the audio tasks started. IDLE0 watchdog fired during `fopen()` in `load_playlist_index_locked`. |
| Five-second watchdog, initial staged SPIFFS | IDLE0 watchdog fired in `SPIFFS_mount`. |
| Thirty-second watchdog, initial TSV fixture | The fixture lacked the third playlist field. Startup rebuilt a zero-station index and the watchdog fired in `native_file_replace`. The original run is retained as NONPASS. |
| Thirty-second watchdog, corrected TSV, idle | PASS. The radio validated one station and HTTP returned the exact 13,588-byte gzip JavaScript asset from SPIFFS. |
| Same application and corrected SPIFFS, TLS load | NONPASS on both runs. The station was selected through HTTP, the certificate bundle validated the TLS peer and the production output configured PDM at 48 kHz. OpenETH reported failed receive-buffer allocations before the simultaneous WebUI/audio progress check could finish. |

After the WebUI read in the idle control, the guest reported 153,496 bytes
free, a 143,348-byte minimum and a largest internal/DMA block of 110,592 bytes.
The stack high-water marks were 4,596 bytes free for stream, 14,252 for decode,
3,460 for output and 1,916 for HTTP. These values describe the OpenETH profile
with ST7789 initialized. They do not measure physical Wi-Fi, RF or DAC timing.

In the second load run the local TLS server reported TLS 1.2 with
`ECDHE-RSA-AES256-GCM-SHA384` and 322,560 bytes written into its socket before
the test stopped. That counter belongs to the sender. The guest did not
complete playback or return a resource sample under load. In the pinned SDK,
the OpenETH RX task calls `malloc(ETH_MAX_PACKET_SIZE)` and immediately retries
when it returns null. The repeated UART errors match that branch. Production
Wi-Fi follows a different driver path, so the exact production memory limit
remains open.

[observed.json](observed.json) binds the idle and load flash components,
receipts and UART logs and preserves the fault backtraces as function names.
The raw flash images, test certificates and build intermediates stay local.

The [RX backoff follow-up](../cyd-openeth-rx-backoff-20261111/README.md) corrects
the playback status check to match the production `OGG` label and records a
health sample after the first PDM driver write.
