# ESP32-C3 TLS errors at explicit reboot — 2026-10-09

## Finding

The paired hardware comparison localizes the observed TLS `-76` messages
to rebooting with an active connection. All three active-stream reboots
produce the same two messages. All three reboots after Stop and verified
heap recovery produce none. No TLS message occurs during the preceding
controlled playback, Stop/settling, or outside the trial windows.

This supports a shutdown-related socket-read failure, rather than a decoder
or memory-allocation failure in these trials. The exact socket errno is not
captured, so it does not prove every internal step that produces the error.
It does not excuse arbitrary TLS errors or establish long-duration playback
stability. The test keeps the active trials' extended TLS verdict as
`REVIEW_REQUIRED` alongside their successful operational reboot checks.

## Controlled comparison

The application is unchanged: `idf61-prefill-min250`, SHA-256
`89d320f663bda6439456c95b6f47d09cd5cac2d434ff9fe85df568fa07fbae9c`, ELF identity
`5a17d251e0a7b308dd011e850b1b1016afba0b46bc7dee6263b82f8c624a4ff3`.
It uses the additional laboratory CA with normal public roots, full compact
AAC/SBR/PS, the TLS reserve, 250/500 ms prefill, QIO 80 MHz and experimental
fractional nominal 48 kHz. No firmware code or default changed in this study.

Each trial starts with 12 seconds of stopped-state/heap observation, then
plays the same full HE-AACv2 44.1 kHz stereo, 16-bit fixture over TLS 1.2
for 12 seconds at 1.0x server pacing. The active condition reboots directly.
The stopped condition sends Stop and observes another 12 seconds, requiring
cleared PCM state and recovered free heap, largest block and task count.
The middle pair reverses condition order. Six trials take 277.969 seconds,
excluding application installation and restoration.

| Trial, in execution order | Operational reboot | TLS rows | Time before reset banner |
| --- | --- | ---: | ---: |
| 1: active | PASS | 2 | 94 ms |
| 1: stopped | PASS | 0 | — |
| 2: stopped | PASS | 0 | — |
| 2: active | PASS | 2 | 109 ms |
| 3: active | PASS | 2 | 78 ms |
| 3: stopped | PASS | 0 | — |

Each active trial records `Dynamic Impl / fetch_input` and
`esp-tls-mbedtls / read`, both returning `-76`
(`MBEDTLS_ERR_NET_RECV_FAILED`). These can be two layers reporting one
failure; six rows are not evidence of six independent failures. Times use
host-received serial data and the same monotonic clock as command boundaries.

All six trials have exactly one `RTC_SW_CPU_RST` inside their explicit reboot
interval and return with the expected image and partition. No allocation,
decoder, panic, watchdog, invalid-free or capture fault is recorded. Median
playback RSSI ranges from -67 to -62 dBm; the minimum is -69 dBm. Maximum
observed playback WebUI response is 125 ms. These short windows are not a
CPU-load or DMA-continuity benchmark.

| Stopped control | Settled free heap samples | Largest block | Tasks |
| --- | --- | ---: | ---: |
| 1 | 133,364 / 133,364 / 133,364 B | 102,400 B | 17 |
| 2 | 133,348 / 133,376 / 133,376 B | 106,496 B | 17 |
| 3 | 133,384 / 133,384 / 133,384 B | 114,688 B | 17 |

Each passes the existing recovery limits relative to its own pre-playback
baseline. Largest-block variation between boots is retained, not treated as
a decoder memory saving.

## Source explanation and limits

The inspected pinned ESP-IDF revision is
`9a97f6c54ec638111ce55cd36581b3c192f15207`:

- `components/esp_system/esp_system.c`: `esp_restart()` invokes shutdown
  handlers before suspending the scheduler and entering `esp_restart_noos()`.
- `components/esp_wifi/src/wifi_default.c`: the default Wi-Fi handlers register
  `esp_wifi_stop` as a shutdown handler.
- `components/mbedtls/mbedtls/library/net_sockets.c`: `mbedtls_net_recv()` maps
  a negative socket `read()` result to `MBEDTLS_ERR_NET_RECV_FAILED` after
  separately handling would-block, connection-reset/broken-pipe and EINTR.
- The application's WebSocket reboot task delays 300 ms and calls
  `esp_restart()` without first stopping audio. Ordinary Stop invalidates the
  stream generation; the stream task owns and closes its HTTP/TLS client.

Together, this source order and the paired controls support the explanation
that the active stream encounters network shutdown before CPU reset. They
do not identify the actual errno or justify closing a client from another
task: that would violate the current single-owner design.

The [earlier OTA follow-up](ESP32C3_MIN250_TLS_OTA_20261009.md) recorded the
same two codes 94 ms before its explicit final reboot, after successful
uploads. This comparison makes shutdown a concrete explanation to pursue,
without rewriting either earlier report's original verdict. A bounded,
owner-acknowledged audio shutdown before reboot could remove the race, but
has not been implemented or qualified. Do not add a blind delay or suppress
TLS errors globally merely to obtain a green log.

## Test, restoration and evidence

The reusable runner is `tools/esp32c3_tests/reboot_tls.py`; usage is in
[the testing guide](ESP32C3_TESTING.md#tls-errors-around-an-explicit-reboot).
Four unit tests reject missing/duplicate/early/watchdog resets, retain TLS
errors on both sides of Stop/reboot, reject faults inside reboot intervals,
and require three stopped observations with cleared PCM fields.

The outer controller restores `idf61-qio80-8c1f2d2d`, verifies unchanged Wi-Fi,
playlist and settings, and records three active AAC 44.1 kHz stereo states.
It exits successfully. No private settings or TLS keys are saved in evidence.
Listening remains deferred; fractional clocking remains experimental and
disabled by default.

The [frozen archive](../tests/results/esp32c3-reboot-tls-20261009/) contains
101 indexed files (989,147 bytes): the controller, original observations,
38 persisted action pairs, filtered serial
rows, 74 support-source snapshots, application/SDK source evidence, public
certificates and independent replay:

```powershell
python tests/results/esp32c3-reboot-tls-20261009/replay.py --output .build/replay-reboot-tls
```

Use a fresh output directory. Replay makes no board/network requests and
preserves the six TLS error rows. Remaining playback qualification includes
certificate-rejection recovery, intermittent FLAC/input service behavior and
the quiet image with public stations; these reboot controls do not close
those separate findings.
