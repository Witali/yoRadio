# Opus Family 1 in the full CYD application

The test ran the CYD application on both ESP32 cores with its production
audio tasks, TFT, SPIFFS, WebUI, and 5-second task watchdog watching both
idle tasks. The QEMU profile uses OpenETH and the corrected I2S DMA model.
The HTTPS station negotiates TLS 1.2 with a 16,384-byte inbound record limit.
The TCP receive window and mailbox are 8640 bytes and eight entries.
The ESP32 profile has no PSRAM.

FFmpeg encoded 14 seconds of distinct per-channel tones with libopus at
48 kHz and 512 kbit/s CBR. The independent libopus decode produced exactly
672,000 frames per channel after trimming. The output-task probe counts
accepted PCM and checks each Vorbis-order channel against the reference
energy and zero crossings. It allows 5% and 2% relative error respectively.
This comparison covers channel identity and ordering in the generated
fixtures. [Ogg Opus channel ordering](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1.1.2).

| Output | TLS RX | Channels | Packet | Ogg page target | First playback failure |
| --- | --- | ---: | ---: | ---: | --- |
| PDM | Dynamic | 8 | 20 ms | 1,000 ms | Espressif decoder allocation, 26,504 B |
| PDM | Dynamic | 8 | 120 ms | 1,000 ms | Espressif decoder allocation, 26,504 B |
| Continuous DAC | Dynamic | 8 | 120 ms | 1,000 ms | Espressif decoder allocation, 26,504 B |
| PDM | Static reserve | 8 | 20 ms | 1,000 ms | Espressif decoder allocation, 17,784 B |
| PDM | Static reserve | 8 | 120 ms | 1,000 ms | Espressif decoder allocation, 17,784 B |
| PDM | Static reserve, heap probe | 8 | 120 ms | 1,000 ms | Espressif decoder allocation, 17,784 B |
| PDM | Dynamic | 6 | 20 ms | 1,000 ms | Ogg audio page allocation, 54,807 B |
| PDM | Dynamic | 6 | 20 ms | 200 ms | Ogg audio page allocation, 12,887 B |
| PDM | Dynamic | 4 | 20 ms | 200 ms | CPU 0 idle watchdog during WebUI sampling, after PCM started |

The eight-channel runs returned `OGP_MEMORY` with the vendor error
`ESP_AUDIO_ERR_MEM_LACK` during OpusTags. In the instrumented static-RX run,
the five public opens were stereo, mono, stereo, stereo and mono. The
first four succeeded. Before the final mono open, 15,248 bytes were free
with a largest matching block of 12,800 bytes. The decoder requested
17,784 bytes of internal default heap. This request exceeded both measures
before the first audio page or PCM workspace was allocated. Each successful
stereo open reduced free memory by approximately 26.6 KB.

The six-channel control opened all of its decoder handles. The guest reported
`OPI_NO_MEMORY` during its first audio page allocation. Remuxing the same
signal to smaller pages kept the reference PCM hash and changed the failed
allocation from 54,807 to 12,887 bytes. Both profiles accepted zero PCM.
An earlier six-channel attempt stopped at the QEMU loopback connection
before guest boot. The playback rows use the successful loopback setup.

The four-channel run reached 14,600 accepted frames in the last progress
sample. Its health endpoint reported zero allocation failures. The watchdog
identified `IDLE0`, with `web_static` running on CPU 0 and `audio_decode`
running on CPU 1 at the time of the event. The stack ended in a synchronous
SPIFFS name lookup. The rebuilt baseline matched the executable segments
of the image that triggered the watchdog.

## Four-channel replay after the WebUI fix

The [WebUI file lookup](../../../idf/esp32-cyd2usb-native/main/web_static.c)
now runs at idle priority and restores the worker's priority before
sending a response. The matched four-channel replay passed with the same
QEMU, configuration, TLS policy, fixture and 5-second watchdog.

- The station transmitted all 903,530 bytes in 55 full 16 KiB body
  records and a 2,410-byte tail.
- The output task accepted 672,000 frames at the ordered EOF flush.
  All four channel metrics passed against the libopus decode.
- Audio advanced from 128 to 33,800 frames across the WebUI read.
  The response before playback, during playback and after EOF contained
  the same exact 13,588-byte asset.
- PDM completed all 1,345,920 requested driver bytes. Minimum free heap
  was 14,288 bytes, with zero reported allocator or output faults and
  no watchdog event.

The existing WebUI host suite passed under ASan/UBSan, including the added
priority assertions, five negative controls and 48 page tests. The
six- and eight-channel resource limits remain open.

## Moving encoded audio pages out of byte-addressable memory

After verified OpusTags, CYD can hold Family 1 audio payloads of at least
4,096 bytes in memory with aligned 32-bit access. The page header and lacing
table stay byte-addressable. The reader delivers complete packets from the
verified page, copying only the requested packet or continuation into its
existing assembly buffer. Short pages keep the borrowed-packet path. If a
word-capable block cannot be reserved, the byte-page path can still accept it.
The word payload is reclaimed when the link closes or playback is reset.
[Ogg page structure and CRC](https://www.rfc-editor.org/rfc/rfc3533.html#section-6).
[ESP32 heap capabilities](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/system/mem_alloc.html).

The intermediate image with word pages passed the first six-channel audio
page for both muxing profiles. The next allocation that failed in each case
was the initial 11,520-byte PCM scratch buffer. The current scratch policy
uses the validated first packet duration and the largest active stream width.
For 20 ms stereo substreams, the first request is 3,840 bytes. The same public
resize protocol handles legal packets up to 120 ms. The PCM plane path can
use aligned word storage while the encoded page is held.

The host comparison against libogg passes 65 existing packet schedules and
10 new word-page schedules under ASan/UBSan. The new cases cover byte-wise
input, continued packets, a 61,440-byte packet, CRC error, reuse and growth,
EOS retirement, and fallback after word memory refusal. The unchanged
page/trim suite passes 276 page and 204 trim cases, including the maximum
65,307-byte Ogg page. Independently, the libopus decoder-owner test passes 13
positive cases and 22 controls with 2,679,360 exact PCM samples.

In the matched four-channel, 120 ms replays with dynamic TLS buffers and
200 ms Ogg pages, both firmware images produced exactly 672,000 frames
and served the exact WebUI asset after EOF. The minimum free byte heap
rose from 7,804 to 14,204 bytes. An intermediate attempt timed out during
the WebUI read before playback and is included separately.

The six-channel replay with regular Ogg pages and dynamic TLS reached
120,200 frames in the last progress sample. No decoder failure was reported.
The minimum free byte heap fell to 520 bytes. OpenETH reported six receive
allocation wait and recovery episodes and the WebUI connection closed
before EOF. With 200 ms Ogg pages, a request for 11,520 bytes still failed
before any PCM was accepted.

With static TLS RX, the six-channel stream with regular pages reached
105,800 frames. OpenETH reported 13 RX allocation waits and WebUI closed
before EOF. With 200 ms pages, the decoder advanced to output setup.
PDM configuration failed on a 1,024-byte DMA allocation. The native error
was `ESP_ERR_NO_MEM` and no PCM reached the output task. Both TLS policies
still have a six-channel full-application resource limit.

The [word-page observations](word-page-observed.json) bind these measurements
to the fixture, firmware, SDK configuration and host test reports.

The [observations](observed.json) record the image, runner and UART hashes,
the fixture bounds, and the numeric results. For the commands, see
[the OpenETH harness](../../target/cyd_full_app_openeth_qemu/README.md).
