# ESP32-C3 FLAC diagnostic follow-up

The TLS reserve with the startup input minimum still produces an intermittent
diagnostic dump during HTTPS FLAC playback. Three repeated HTTP/HTTPS series
reproduce the failure once. Improved CPU accounting and a task-watchdog event
counter are available for further diagnosis; the fault is not resolved.

## Physical results

Each series plays the same synthetic 48 kHz stereo FLAC level-8 file over
HTTP and HTTPS, with automatic and explicit FLAC selection. File delivery is
unpaced and uses TCP backpressure. Three series give 12 file cases per image.
Both images use pinned ESP-IDF revision `9a97f6c54ec6`, the same configuration,
full compact AAC and the 17,058-byte TLS reserve with the input queue minimum.

| Image | File cases passed | Captured allocation failures | Diagnostic dumps | Watchdog counter events |
| --- | ---: | ---: | ---: | --- |
| Existing startup-minimum reserve | 11/12 | 0 | 1 | Counter absent |
| Corrected profiler and watchdog counter | 12/12 | 0 | 0 | None observed |

RSSI ranges from -69 to -56 dBm in both suites. All cases reach the expected
PCM format and EOF; the failed case is rejected by the runtime-diagnostic
gate. CPU percentage is informational, with observed peaks of 100.0% and
99.9% respectively. These finite-file tests do not establish ten-minute
stability, physical PCM quality or absence of audible output gaps.

In the failed `https:flac-level8:auto` case, `MEPC=0x4203581c` and
`RA=0x42035402` resolve against the exact control ELF to
`restoreLinearPrediction(unsigned char, unsigned char)` at lines 813 and 765.
`MCAUSE=0xdeadc0de` is the SDK's synthetic cause used for a nonfatal register
dump. The previous failure pointed into `ip4_input`; neither sampled location
proves a defect in that function. The watchdog reason caption remains absent.
The timing and synthetic cause are consistent with watchdog starvation, but
the new counter did not observe the original fault in its repeat series.

## Diagnostic changes

- Recognize the SDK task name `tcpip` and FreeRTOS-truncated names such as
  `websocket_statu`. Previously these tasks were omitted from their CPU
  categories, although total busy time still included them. The corrected
  physical run records TCP/IP up to 12.7%; the old report's 0.0% was invalid.
- Retain watchdog task context, including RISC-V register captions, without
  storing arbitrary watchdog user names. Unknown names are redacted. Retained
  context fails runtime gates even if the initial timeout caption is missing.
- In profiling builds, count calls to the SDK's watchdog ISR hook and report
  changes from task context. The linked hook is 16 bytes in IRAM and accesses
  a four-byte DRAM counter using load, increment and store; it makes no calls.
  A link audit confirms the SDK ISR calls this hook. The timeout, watchdog
  behavior, task priorities and decoder arithmetic are unchanged.
- Both raw counter reports and filtered reports fail file/OTA runtime gates.
  Eleven host diagnostic tests, the existing CPU-profile configuration test,
  firmware build, AAC/HTTP link checks and the ISR placement/call audit pass.

The counter supports diagnosis when early ISR captions are missing from native
USB output. Its presence does not prove a watchdog fired. Further sustained
high-bitrate HTTPS FLAC testing must capture an actual event before choosing
a scheduling or decoder change. Do not mask the fault by extending the timeout.

## Artifacts and restoration

The [evidence archive](../tests/results/esp32c3-flac-watchdog-20261008/) retains
both successful and failed cases, exact source snapshots, source hashes,
build/link checks and address resolution. The diagnostic
[firmware manifest](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-profile/manifest.json)
identifies a laboratory image with an additional test CA; it is not qualified
for production. Private keys and captured broadcast audio are excluded.

Both controllers restore the ordinary awake firmware by app-only OTA, verify
its ELF identity and unchanged Wi-Fi, playlist and settings, and confirm saved
AAC playback in three observations over 15 seconds. The
[memory research plan](ESP32C3_MEMORY_STABILITY_TODO.md#further-memory-research-priorities)
and [TLS reserve qualification](ESP32C3_TLS_RESERVE_20261008.md) remain open.
