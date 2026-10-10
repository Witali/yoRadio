# ESP32-C3: TLS RX reservation and extended control tests (8 October 2026)

## Status

The optional RX-only reservation builds and passes host ownership, SDK-source
and linked-code checks. **It has not been tested on the board and remains off
by default.** The longer physical tests below used the preceding generic
reserve image; they do not qualify the new RX-only policy.

Separately, the requested audio scheduling default is now output **8**,
decoder **7**, stream **5**, for both staged and direct-DMA output. Kconfig
resolution, the 46 native C3 checks and the new image's task-creation machine
code confirm this configuration. The physical control still used output 6.
An existing explicit disabled setting in `sdkconfig` must be changed manually.

## RX-only ownership

Enable `sdkconfig.tls-rx-reserve.defaults` after the dynamic-TLS and large-reserve
overlays. `YORADIO_TLS_RX_ONLY_RESERVE` reuses the existing **17,058-byte** static
slot for every audited RX allocation, including the **24-byte** cached state.
It adds no second large buffer. Handshake structures, TX buffers and unrelated
allocations cannot claim it. If another RX context owns the slot, or a request
exceeds its capacity, the normal allocator remains the fallback.

The build generates a local copy of the pinned SDK dynamic-buffer source. It
changes exactly four allocation calls and adds the hook declaration:

| SDK function | Allocation / lifetime |
| --- | --- |
| `esp_mbedtls_add_rx_buffer` | Incoming record; a cached buffer is freed before replacement |
| `esp_mbedtls_free_rx_buffer` | Save counters/IV state in a 24-byte allocation after consuming a record |
| `esp_mbedtls_reset_add_rx_buffer` | Full buffer for reset; currently unused and removed from the final ELF |
| `esp_mbedtls_dynamic_set_rx_buf_static` | Convert to a retained full RX buffer after releasing the preceding buffer |

All four compiled object sections call the RX hook. The three live functions
also call it in the final ELF. The source generator rejects any unaudited SDK
source; shared SDK files remain unchanged. The pinned SDK is
`9a97f6c54ec638111ce55cd36581b3c192f15207`.

The free-path audit follows `esp_mbedtls_free_buf`, which recovers the prefix
base with `__containerof`, through the hooked `mbedtls_free` function pointer.
The application recognizes only the exact reserved base, erases it before
releasing ownership and passes ordinary allocations to the SDK free routine.
Read errors, cached records, retained conversion and context destruction retain
the SDK's existing rules. Initial `ssl_setup` has no reserved RX allocation;
calling setup again on a live context is not a supported lifecycle. The tested
configuration disables `MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH`.

The slot belongs to one allocation at a time, not permanently to one TLS
connection. Concurrent contexts may exchange ownership when a buffer is freed.
The adaptive queue still releases only idle slots and stays at its startup
minimum to fund the permanent reservation. This is a placement change, not a
net RAM saving or a reservation of all Wi-Fi/crypto/WebUI memory.

Host tests execute the actual C allocators under ASan/UBSan: generic/RX-only
times pool-only/adaptive input, **8,000 concurrent allocations per variant**,
**32,000 total**. They also cover cached/small/full/maximum-sized transitions,
zeroing, overflow, exhaustion, non-RX exclusion, fallback and balanced frees.
Three SDK routing tests pass. Linked checks preserve full 16 KiB TLS content,
normal certificate roots, matching free hooks and static DRAM placement.
These checks do not exercise live TLS cryptography or establish playback quality.

## Physical control results

Image: `esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-profile`, ELF SHA-256
`3c69ee33f17f0b2841f6202cb06755a729bbbc4de8cec84b7ee30ba8057e86ac`.
Both runs use verified HTTPS and passive serial capture. CPU percentage is
informational; runtime faults and playback continuity still matter.

| Measurement | HE-AACv2, alternating 1/16 KiB records | FLAC, 48 kHz stereo, 16 bit |
| --- | ---: | ---: |
| Requested observation | 600 s | 600 s |
| Observed steady window, excluding first 10 s | 590.047 s | 421.406 s; interrupted |
| Mean / peak CPU | 70.24% / 71.7% | 99.98% / 100% |
| Decoded audio / elapsed time | 1.00159 | 0.90646 |
| Minimum free heap / largest block | 16,676 / 4,608 B | 55,852 / 34,816 B |
| First / last median free heap | 26,140 / 16,784 B | 57,704 / 57,876 B |
| Maximum observed status request | 157 ms | 187 ms |
| Captured allocation failures | 0 | 0 |
| Task-watchdog evidence | None captured | ISR counter reaches 83 |
| Original verdict | FAIL: progressive heap loss | FAIL: Windows socket error 10048; watchdogs also fail runtime replay |

The AAC heap recovers after Stop: settled free heap **133,028 → 133,080 B**,
largest block **98,304 B** at both endpoints. This does not turn the failed
in-playback trend check into a pass or establish acoustic continuity.

The FLAC run confirms that the synthetic `MCAUSE=0xdeadc0de` dumps can be task
watchdog reports: the ISR counter advances during this run. There are 82
captured counter reports, ending at 83; serial capture is not assumed complete.
The sampled code addresses vary, so they do not isolate a single guilty
decoder function. Runtime replay independently fails even though the transport
exception ended observation before the normal end-of-run runtime check.
The socket exception belongs to the host test; its cause still needs diagnosis.

At the end of the control run, the controller restored the quiet application by
native OTA, verified its ELF identity, unchanged Wi-Fi/playlist/settings and
three playing AAC status samples over 15 seconds.

## RX-only short physical qualification

The RX-only candidate below passed **44/44 HTTP/HTTPS format cases** on the
physical board: MP3, FLAC, Vorbis, Opus, AAC-LC, HE-AAC and HE-AACv2, using
automatic and explicit codec selection. The HTTPS format server recorded
TLS 1.2 with `ECDHE-RSA-AES256-GCM-SHA384`. These were short finite-file tests;
they do not resolve the earlier ten-minute FLAC failure.

Four HE-AACv2 record-size tests ran for **75 seconds each** with verified TLS
1.2 and `ECDHE-RSA-AES128-GCM-SHA256`. Record payload sizes were 1 and 16 KiB.

| Record mode | Mean / peak CPU | Minimum free heap / largest block | Decoded audio / elapsed time |
| --- | ---: | ---: | ---: |
| Small | 68.19% / 73.3% | 26,172 / 15,360 B | 1.00193 |
| Large | 70.45% / 71.8% | 26,148 / 12,288 B | 1.00202 |
| Small then large | 70.57% / 72.9% | 25,748 / 15,360 B | 1.00200 |
| Alternating | 70.38% / 72.0% | 25,772 / 15,360 B | 1.00204 |

All **eight framing/closure cases** also passed: fixed-length and chunked
responses with close-notify, raw closure and truncation, plus close-delimited
responses with close-notify or raw closure. The truncated responses retained
the expected read-error status instead of being accepted as normal EOF.

No allocation-failure, panic or task-watchdog evidence was captured in these
short runs. The record suite's idle-recovery and runtime gates passed. The
controller restored the quiet image and verified unchanged Wi-Fi, playlist and
settings plus three playing AAC samples over 15 seconds. Decoded audio duration
and status polling do not replace acoustic or DMA continuity measurements.

A matched generic-reserve control is saved as
[`esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-output8`](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-output8/).
Its ELF is `8f1a86ef61f8c5e56beeccf8a85f3dde7052ab480a02a227e0a80c02fb41ff1c`.
Both images use output priority 8, decoder priority 7 and stream priority 5;
their saved configurations differ only in `CONFIG_YORADIO_TLS_RX_ONLY_RESERVE`.
The control passes build and linked-code audits; its completed physical
comparison is recorded below. Both images remain laboratory-only and
**NOT_QUALIFIED** for production.

The [short-run evidence archive](../tests/results/esp32c3-rxonly-physical-20261008/)
contains raw reports, configuration and image identities, source snapshots,
build audits and restoration checks. It also saves the prepared long-run
controller, which was not executed as part of this archive. The host fixture
server's separate TLS 1.3 loopback check does not establish board TLS 1.3 support.

## Saved candidate and remaining work

### Completed ten-minute comparison and DMA follow-up

The matched output-priority-8 runs completed all 600 seconds per case. CPU
values use complete telemetry intervals after ten seconds of warmup. Audio/wall
is decoded audio duration divided by elapsed time, not an acoustic measurement.

| Image / HTTPS case | Mean CPU busy | Audio/wall | Minimum free / largest block | New watchdog events | Original result |
| --- | ---: | ---: | ---: | ---: | --- |
| Generic reserve, HE-AACv2 alternating TLS records | 71.03% | 1.00158 | 16,508 / 4,608 B | 0 | FAIL: progressive heap loss |
| RX-only reserve, HE-AACv2 alternating TLS records | 70.83% | 1.00159 | 16,700 / 4,608 B | 0 | FAIL: progressive heap loss |
| RX-only reserve, FLAC 48 kHz stereo over HTTPS | 99.63% | 0.97436 | 57,232 / 40,960 B | 114 | FAIL: runtime watchdog |

Both AAC runs retain their heap-trend failure even though playback continued
and memory recovered after Stop. Increasing outstanding TCP payload credit
correlates with the heap decrease; credit counts payload bytes, not allocated
owner memory, so it does not prove that all of the decrease is expected queue
storage. One RX-only AAC receive-snapshot sequence is incomplete; its network
coverage remains unavailable rather than being reported as a full pass.

The FLAC run lagged real time by about 2.56%. Mean task CPU was 34.79% stream,
19.84% decoder, 19.83% Wi-Fi, 14.77% TCP/IP and 5.92% output. No allocation
failure was captured. This run completed without the earlier host socket
failure; it does not establish that the host issue can never recur.

A separate instrumented staged-output run measured **154 DMA completion-queue
overruns over 45.109 observed seconds** of a 60-second FLAC test, versus **zero
over 75.110 seconds** of a 90-second HE-AACv2 test. The FLAC runtime gate failed;
the short AAC gates passed. A discarded completion notification indicates
delayed output service, not an exact count of lost audio samples. See the
[DMA notes](ESP32C3_OUTPUT_DMA_20261005.md).

Both controllers restored the quiet image, verified unchanged Wi-Fi, playlist
and settings, and observed the original playing state over 15 seconds. Raw
reports, original failures, image identities, controllers and hashes are in the
[long-run evidence archive](../tests/results/esp32c3-rxonly-long-20261008/).
These results do not qualify the reserve configuration for production.

The RX-only laboratory build is saved under
[`firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly/`](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly/).
Its ELF is `cc16813f6dc499951d1976a0e47dbe0f01c8b4f1d570258d5cb9ec686f5dc4e9`;
the application is **1,617,264 B**. It includes a laboratory CA and profiling.
It also incorporates the new output-priority default, so comparison with the
physical control would change two variables. Use matched-priority images to
attribute memory results specifically to the allocator.

Before promotion, extend the short record/framing coverage above, test certificate rejection,
concurrent contexts, Stop/EOF/reset/error cleanup, codec switching, late SBR/PS,
longer playback after resolving the retained failures, and OTA. Investigate FLAC idle-task starvation with bounded
cooperative work and measured output continuity; do not disable the watchdog
or extend its deadline merely to pass. Preserve host transport diagnostics in
future soaks. Retain the AAC heap-trend failure for comparison.

Exact configurations, source hashes, host/physical logs, failed attempts and
restoration checks are in the [evidence archive](../tests/results/esp32c3-tls-rx-reserve-20261008/).
Private keys and large generated audio files are excluded; the fixture manifest
and generator are retained.
