# CYD FLAC over TLS with TFT, continuous DAC and WebUI

Both diagnostic images use ESP-IDF 6.0.2, continuous DAC with the DMA wait
fix, dynamic Mbed TLS buffers, TCP receive window and mailbox 8640/8, and a
30-second task watchdog. OpenETH replaces Wi-Fi on the emulator. The two
generated SDK configurations differ only in the FLAC decoder selection.

The tracked level-8 calibration stream contains 528,000 stereo PCM16 frames
at 48 kHz and uses 4,608-sample blocks. The official Xiph FLAC 1.5.0 decoder
and FFmpeg independently produced the STREAMINFO MD5
`7e7636f603770391913d2d7521b969ea`. The application probe checks the
interleaved PCM accepted by the output task against that value.
[Xiph reference decoder](https://github.com/xiph/flac/releases/tag/1.5.0).
[STREAMINFO and sample order](https://www.rfc-editor.org/rfc/rfc9639.html#section-8.2).

| Decoder | Result | Minimum free heap |
| --- | --- | ---: |
| Espressif | One failed 18,432-byte allocation. The vendor decoder reported frame error 8 and eventually returned `ESP_AUDIO_ERR_FAIL`. Zero PCM frames reached the output. | 7,324 B |
| Transferred custom FLAC | Exact 528,000-frame flush and matching PCM MD5. WebUI served the same complete 13,588-byte asset before playback, during playback and after EOF. | 47,276 B |

The custom run received the entire 1,771,852-byte stream as 108 full
16,384-byte TLS application records and the 2,380-byte tail. It reported no
allocation failures, output errors, short writes, watchdog events or OpenETH
allocation waits. The vendor heap minimum is from a failed run that never
activated DAC playback. These measurements describe the two observed
workloads. The [observations](observed.json) include config and image hashes,
output counters, PCM checks and stack watermarks.

Use the [matched FLAC profile](../../target/cyd_full_app_openeth_qemu/README.md)
with the [validated QEMU build profile](../cyd-pdm-static-rx-20261113/README.md).
The vendor decoder remains the default. Physical Wi-Fi, DAC timing and the
production watchdog under simultaneous network and display load remain open.
