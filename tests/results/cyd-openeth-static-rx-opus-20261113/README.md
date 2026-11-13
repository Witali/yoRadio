# Static TLS RX and full Ogg Opus playback on CYD

The [original static RX run](../cyd-openeth-full-records-20261111/README.md)
reported a 560-byte heap minimum, 18,880 allocation failures, and nine
recovered OpenETH allocation waits. Espressif logged Opus error `-4` on a
1,275-byte packet. The application later reported `OGP_DECODER` with
`ESP_AUDIO_ERR_DATA_LACK` at the final 1,807-byte input chunk. That counter
describes the input to the application wrapper. The original run has no
packet digest or decoder-local allocation trace. The exact reason for the
first Opus rejection remains unconfirmed. [Opus error codes](https://opus-codec.org/docs/opus_api-1.5/group__opus__errorcodes.html).

The pinned Espressif Ogg parser can allocate when it assembles a packet across
pages. The fixture has 551 audio packets of 1,275 bytes, including packets
that span pages. FFmpeg independently decodes the full fixture in strict
mode. The [reference Opus parser](https://raw.githubusercontent.com/xiph/opus/v1.3.1/src/opus.c)
accepts the packet size used by this stream. A subsequent QEMU run with
the old PCM size and an 8,640-byte TCP window and eight-entry receive mailbox
completed on PDM with zero allocation failures. The run's HTTP body CRC
and all 12 sampled Opus packet CRCs match the fixture.

The [application fix](../../../idf/esp32-cyd2usb-native/main/ogg_playback.h)
starts mapping-family-0 Opus with a 3,840-byte PCM buffer when static TLS RX
is enabled. This releases 8,448 bytes of initial decoder workspace for
20-ms stereo streams. Longer packets keep the existing Espressif
`BUFF_NOT_ENOUGH` resize and retry path. An explicit decoder
`ESP_AUDIO_ERR_MEM_LACK` now reaches the application's allocation failure
status. The TLS RX reserve and its 16,384/4,096-byte record limits stay in
use for these tests. [Espressif public decoder API](https://github.com/espressif/esp-adf-libs/blob/master/esp_audio_codec/include/simple_dec/esp_audio_simple_dec.h).

| QEMU run | Result |
| --- | --- |
| PDM, TCP 8640/8, old PCM capacity | Full EOF and WebUI pass. 2,536-byte minimum heap. |
| PDM, TCP 11520/10, smaller PCM buffer | One run reached EOF with all 43 full TLS records and exactly 1,058,176 PDM driver bytes. Allocation, decoder, stream and output failure counts were zero. The post-EOF WebUI request timed out. Other attempts stopped at an HTTP timeout before Play or a PDM startup timeout. |
| PDM, TCP 8640/8, smaller PCM buffer | Both attempts stopped at the PDM startup timeout after the first Opus packet decoded. |
| Continuous DAC, TCP 8640/8, smaller PCM buffer | Full EOF and WebUI pass. 43 full TLS records and the tail. Zero allocation, decoder, stream or output failures, with 11,300 bytes of minimum free heap. |

The final continuous DAC run measured all 706,319 HTTP body bytes and all
551 Opus packets at the synthesis call. Both cumulative CRCs match the
fixture. The decoder returned 528,960 samples per channel before Ogg trim.
The output accepted exactly 528,000 PCM frames and served the exact
13,588-byte WebUI asset during playback and after EOF.

The [observations](observed.json) include the earlier nonpasses and hashes of
the original trace files and their LF-normalized copies. The
OpenETH build used ESP-IDF 6.0.2, the diagnostic RX backoff overlay, a local
disposable CA and the 30-second watchdog. To reproduce the final run, copy
the [CMake hook](attach.cmake.txt) and [trace](trace.c.txt) to
`.build/cyd-rx-trace-20261113-01/attach.cmake` and `trace.c`. Use the
[full application fixture](../../target/cyd_full_app_openeth_qemu/README.md)
with static RX enabled, dynamic Mbed TLS buffers disabled, continuous DAC,
TCP 8640/8, and both RX backoff and the PCM probe enabled. The trace hashes
only the local fixture and its packets.

The ASan/UBSan Ogg wrapper passed 144 cases with static RX enabled and
108 cases with the ordinary profile. The family-1 dispatch check passed
43 schedules and 12 controls. Physical Wi-Fi and DAC behavior remain open.
