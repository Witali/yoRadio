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

The controller restored the quiet application by native OTA, verified its ELF
identity, unchanged Wi-Fi/playlist/settings and three playing AAC status samples
over 15 seconds. The board is running that restored image, not RX-only reserve.

## Saved candidate and remaining work

The RX-only laboratory build is saved under
[`firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly/`](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly/).
Its ELF is `cc16813f6dc499951d1976a0e47dbe0f01c8b4f1d570258d5cb9ec686f5dc4e9`;
the application is **1,617,264 B**. It includes a laboratory CA and profiling.
It also incorporates the new output-priority default, so comparison with the
physical control would change two variables. Use matched-priority images to
attribute memory results specifically to the allocator.

Before promotion, test all TLS record sizes/framing, certificate rejection,
concurrent contexts, Stop/EOF/reset/error cleanup, codec switching, late SBR/PS,
ten-minute playback and OTA. Investigate FLAC idle-task starvation with bounded
cooperative work and measured output continuity; do not disable the watchdog
or extend its deadline merely to pass. Resolve the host socket failure before
claiming a complete FLAC soak. Retain the AAC heap-trend failure for comparison.

Exact configurations, source hashes, host/physical logs, failed attempts and
restoration checks are in the [evidence archive](../tests/results/esp32c3-tls-rx-reserve-20261008/).
Private keys and large generated audio files are excluded; the fixture manifest
and generator are retained.
