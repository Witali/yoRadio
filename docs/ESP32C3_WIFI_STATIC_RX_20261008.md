# ESP32-C3 static Wi-Fi receive buffer experiment

**Rejected as a production memory fix.** This optional experiment targets the
full-record TLS allocation failure on pinned ESP-IDF 6.1 revision `9a97f6c54ec6`.
The short run passes, but the longer repetition reproduces the allocation
failure. It is not enabled in board
defaults. The [SDK qualification](ESP32C3_IDF61_REVISION_20261008.md) records
the control: 16,749 B requested with 27,040 B free / 15,360 B largest block.

## Controlled configuration

[`sdkconfig.wifi-static-rx-four.defaults`](../idf/esp32c3-oled-native/sdkconfig.wifi-static-rx-four.defaults)
changes the static Wi-Fi RX buffer count and its receive block-ack window
from six to four. Dynamic RX/TX limits remain 16, the TCP window remains
8,640 bytes, and RX copying and dynamic TLS remain enabled. AAC storage,
precision, output rates, codec families and TLS record capacity are unchanged.

The pinned SDK's `components/esp_wifi/Kconfig` permits this range and
recommends static RX count at least as large as the block-ack window. Static
buffers are allocated by `esp_wifi_init` and retained until deinitialization;
its documented estimate is approximately 1.6 KB per buffer. Removing two
therefore suggests about 3.2 KB of runtime heap capacity, to be measured on
the board. It does not reduce linked BSS by that amount.

This tests the permanent receive pool, separately from the earlier reduction
of dynamic RX/TX to six, which limited high-bitrate FLAC. Fewer permanent
buffers and a smaller block-ack window can still reduce throughput or AP
compatibility. A passing AAC start alone is insufficient.

## Acceptance

1. Build and audit the full AAC and HTTP/TLS configuration. Confirm only the
   two intended settings and their SDK aliases differ from the control.
2. Repeat the failing alternating 1 KiB/16 KiB TLS record case and measure
   idle heap, allocation failures, full-rate HEv2, WebUI and recovery.
3. If the short reproduction succeeds, run ten minutes, then high-bitrate
   MP3/FLAC/Vorbis/Opus and AAC LC/HE/v2 over HTTP and HTTPS.
4. Recheck format changes, mixed-codec lifetime, natural EOF, OTA under
   playback and final settings recovery before considering defaults.

## Build and first physical result

The saved laboratory image is
[`esp32c3-idf-6.1-r9a97f6c54ec6-rx6-srx4`](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-srx4/manifest.json),
1,613,728 B, ELF
`2932159861897a1064bfe1f9bf9ff3900c611704dac551617a7d2efe7aeb31bf`.
Build, full AAC linkage and HTTP/TLS linkage pass. The exact config comparison
finds only the two intended settings and their two compatibility aliases.

The initial **75-second alternating-record case passes** unchanged playback,
runtime, CPU/heap, WebUI, idle-recovery and settings checks. It observes 18
small and 18 full-size encrypted records, with 379 full-format HEv2 observations
after warmup. Output remains 44.1 kHz stereo; first full PCM is at 0.922 s.

| Measurement | Result |
| --- | ---: |
| Idle free heap before run, median | 146,206 B |
| Corresponding failed control idle median | 142,872 B |
| Observed increase in idle free heap | 3,334 B |
| Playback minimum free heap / largest block | 21,960 / 14,848 B |
| Mean / peak active CPU | 62.8 / 67.6% |
| Decoded audio / wall time | 1.00213 |
| Idle recovery free heap / largest block | 146,216 / 114,688 B |

The idle difference includes small per-run allocation variation. A periodic
largest-block sample while a TLS buffer is already allocated is not the same
as the largest block available at the next allocation request. The relevant
positive evidence here is successful full-size records without allocation
errors, not a threshold inferred from that sampled minimum.

The ordinary firmware and initial playback state are restored after this
short run. The following result prevents production qualification.

## Longer repetition fails

The requested 600-second repetition reaches full 44.1 kHz stereo HEv2 at
0.828 s, but fails a 16,749-byte allocation at **30.515 s**. There are 27,248 B
free / 15,872 B largest at that instant. Status becomes `stream read failed`
at 31.484 s. The extra permanent-pool headroom does not guarantee a contiguous
TLS allocation after other network allocations have changed the heap layout.

Status observation then ends at 58.656 s after a TCP-connect timeout. The
instrumented client preserves the original timeout and performs no retries.
Idle-recovery and original restoration also time out; the outer recovery OTA
attempt fails with host `WinError 10048`. There is no recorded panic or reset.
Serial telemetry after the TLS failure shows free heap back at 146,256 B with
114,688 B largest and continued WebSocket-task activity, so those connection
failures alone do not establish a crashed board.

An independent process subsequently reaches the expected candidate and sees
`stream read failed`. A separate app-only OTA recovery passes and verifies the
ordinary image, Wi-Fi, playlist and settings across that recovery operation.
Three additional observations over 15 seconds confirm saved-station playback.
The original failed restoration remains FAIL: its initial in-memory settings
snapshot was lost when that process exited, so it is not retrospectively
claimed to pass.

No high-bitrate or broader format promotion follows this failed memory gate.
The next memory experiment must control large-block ownership and placement,
rather than rely only on a larger free-byte total. Preserve full TLS records,
AAC profiles, output rates and the existing PCM error allowance.

The [evidence archive](../tests/results/esp32c3-wifi-static-rx4-20261008/index.json)
contains 126 indexed files: both physical runs, original restoration failures,
the separate successful recovery, request-phase traces, exact configuration
differences, build/link reports and measured sources. No private TLS key is
included.
