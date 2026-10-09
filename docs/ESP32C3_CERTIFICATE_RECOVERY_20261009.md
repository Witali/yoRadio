# ESP32-C3 certificate rejection and playback recovery — 2026-10-09

## Result

The unchanged `idf61-prefill-min250` candidate passes **16/16 original report
entries** when repeating the previous sequence: eight HTTP/TLS completion
scenarios, rejection of an untrusted certificate, recovery to HTTP AAC, then
full HE-AACv2 over trusted HTTPS with growing TLS records. Settings, Stop and
heap-recovery entries are included in the count.

This supplies the successful recovery observation missing from the
[earlier campaign](ESP32C3_MIN250_TLS_OTA_20261009.md). Its Windows 10048 and
subsequent timeouts remain recorded failures: this run neither reproduces nor
explains them. No network settings, connection timeouts, retry rules or
certificate-verification requirements were changed.

Application SHA-256:
`89d320f663bda6439456c95b6f47d09cd5cac2d434ff9fe85df568fa07fbae9c`.
ELF identity:
`5a17d251e0a7b308dd011e850b1b1016afba0b46bc7dee6263b82f8c624a4ff3`.
The image retains full compact AAC/SBR/PS, the 17,058-byte TLS RX reserve,
adaptive input, 250/500 ms prefill, QIO 80 MHz and experimental fractional
nominal 48 kHz. Firmware behavior and production defaults are unchanged.

## Certificate and HTTP recovery evidence

| Check | Result |
| --- | --- |
| Original HTTP/TLS completion phase | 9/9 entries PASS |
| Independent full-format and terminal-state replay | 8/8 scenarios PASS |
| Untrusted certificate and following HTTP recovery | PASS |
| Stop after rejection/recovery | PASS |
| HE-AACv2 TLS growth, heap recovery and settings | 5/5 entries PASS |
| Failed traced board HTTP requests | 0 |
| Additional host socket captures triggered by 10048 | 0 |

The self-signed test certificate was valid at the recorded test time and
matched the server IP address. Its trust was rejected, rather than relying
on an expired certificate or a hostname mismatch. All 24 observations during
the 12-second rejection window show no playback. Four server
`TLSV1_ALERT_ACCESS_DENIED` alerts coincide with four groups of certificate
bundle failure, handshake return `-12288` and the propagated ESP-TLS failure.
Those 12 intentional-negative log rows are retained and scoped to rejection.

The following seven-second HTTP observation contains 15 samples; ten after
warmup pass full AAC-LC 48 kHz stereo format checks. No TLS message appears
during recovery. Independent replay verifies rejection and recovery separately.
No decoder, allocation, panic, watchdog, capture or unexpected-reset fault is
recorded in the three phases.

The three framing TLS `-29312` rows belong to the deliberately incomplete
Content-Length, chunked and raw close-delimited fixtures. Each produces
`stream read failed`; the five complete fixtures produce `stream ended`.
All terminal observations have cleared PCM fields. No blanket TLS-error
exemption is applied.

## Full HE-AACv2 after the failed handshakes

The next 75-second run uses trusted TLS 1.2 and a full HE-AACv2 44.1 kHz stereo
fixture, paced at 1.0x. Application records grow from 1 KiB to 16 KiB after
full decoding has started. The server records 118 small and 11 large writes;
the corresponding encrypted payload lengths are 1,048 and 16,408 bytes.

CPU, heap and DMA results below use complete selected intervals after a
ten-second warmup. RSSI and WebUI latency use the whole playback observation.

| Measurement | Result |
| --- | ---: |
| Mean / peak sampled CPU busy | 58.697% / 60.1% |
| Minimum sampled free heap | 26,280 B |
| Minimum sampled largest block | 14,336 B |
| Selected / whole observed DMA queue events | 0 / 0 |
| Selected DMA write errors | 0 |
| Median / minimum RSSI | -63 / -68 dBm |
| Maximum observed WebUI response | 125 ms |
| Idle heap before playback, two observations | 133,132 / 133,132 B |
| Idle heap after Stop, three observations | 133,124 / 133,124 / 133,124 B |
| Idle largest block before / after | 102,400 / 102,400 B |
| Idle task count before / after | 17 / 17 |

The eight-byte before/after difference is preserved; recovery passes the
existing 2 KiB free-heap and 4 KiB largest-block limits. A single run is not
proof that no slow leak can ever occur. CPU, decoder, DMA and queue-flow
coverage checks pass. No input/PCM continuity claim extends beyond captured
counters, and no analog recording was made.

## Restoration and replay

The controller restores `idf61-qio80-8c1f2d2d`, verifies unchanged Wi-Fi,
playlist and settings, and records three active AAC 44.1 kHz stereo states.
Both the controller and its host-error monitor finish. Listening remains
deferred; fractional clocking is still disabled by default.

The [archive](../tests/results/esp32c3-certificate-recovery-20261009/) saves
41 indexed files (1,716,641 bytes): original reports, observations, request timing, filtered serial rows,
independent replay and public certificates. It pins the existing frozen
source/analysis archives by their index hashes instead of duplicating them.
All 73 test-source hashes match the pre-run snapshot. Private settings and
TLS keys are excluded.

```powershell
python tests/results/esp32c3-certificate-recovery-20261009/replay.py --output .build/replay-certificate-recovery
```

Use a fresh output directory in the repository. Replay verifies this archive
and both pinned dependency archives before reproducing the findings, without
network or board access. Passing replay is evidence integrity, not full
production qualification.

Next work is quiet-image/public-radio qualification and the intermittent
heavy-FLAC/input-service finding. One concrete avenue for the latter is the
current input policy in `tls_input_reserve_prepare_connection()`: with a TLS
reserve configured, it shrinks to the minimum and never regrows, including
for HTTP. Investigate a bounded codec-dependent increase using measured RAM
headroom; preserve queued packet ownership, the TLS reserve and AAC startup
memory before considering such a change for production.
