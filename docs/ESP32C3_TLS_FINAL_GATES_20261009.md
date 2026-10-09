# ESP32-C3 controlled TLS and OTA follow-up — 2026-10-09

## Scope and identity

This continues the [PCM-tail hardware qualification](ESP32C3_PCM_TAIL_BOARD_20261009.md)
with controlled TLS record sizes, HTTP/TLS closure, certificate rejection and
OTA during full HE-AACv2 HTTPS playback. The filename identifies a planned
qualification stage; it does not imply that all acceptance gates passed.

The unchanged saved candidate is `idf61-pcm-tail`, 1,620,496 bytes, SHA-256
`e7d19f98719bb2f8b244096dffe73f57a98794d53fcb63ad918ff3ffbf3c1853`.
Its configuration includes full compact AAC/SBR/PS, the 17,058-byte RX-only
TLS reserve, adaptive input queue, a maximum 500 ms input prefill, staged PDM,
fractional clocking and laboratory diagnostics. This is the same image as
the previous qualification, not a new production build. Startup registers
confirm nominal 48,000 Hz and QIO 80 MHz; four mapped application CRC checks
match the saved binary. Nominal clock readback is not an external frequency
or analog noise measurement.

Two focused test changes precede this run:

- `7aef9537`: make record-server pacing explicit. Historical runs retain their
  default 1.02x; every controlled record case here requests **1.0x**.
- `aa5b721b`: require three consecutive matching rate/channel/profile readings
  before OTA with a controlled fixture. The new case uses full HE-AACv2 at
  44.1 kHz stereo over HTTPS, including SBR/PS rather than only the AAC core.

Six record-server host tests, five OTA format-gate tests and three existing
OTA serial-health tests pass. The record tests check real encrypted TLS
record sizes, exact delivered payload and pacing at 0.5x, 1.0x and 2.0x.

## Controlled record results

The four 75-second record cases pass the original playback, runtime and
settled-memory gates. Separate DMA service counters expose a remaining
continuity concern; passing those original gates does not override it.

| Record mode | Mean CPU busy | Minimum CPU-log free heap | Minimum largest block | DMA queue events after 10 s warmup | Events in whole observed counter interval | Driver write errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 KiB | 61.775% | 26,104 B | 15,360 B | 0 | 0 | 0 |
| 16 KiB | 60.952% | 17,728 B | 5,120 B | 4 | 5 | 0 |
| 1 KiB, then 16 KiB | 61.293% | 26,164 B | 15,360 B | 0 | 0 | 0 |
| Alternating 1/16 KiB | 60.959% | 26,140 B | 15,360 B | 0 | 2 | 0 |

Whole observed counter intervals run between the first and last readable DMA
samples. They cannot count events before the first sample. CPU/heap figures
use the selected post-warmup interval; the archive also retains separately
paired network-memory samples. Counters arrive about every five seconds and
cannot determine individual audible gap duration.

The pinned I2S driver invokes `on_send_q_ovf` when its completed-buffer queue
is full and removes an old notification. This indicates missed servicing;
it does not by itself distinguish absent PCM/input from task scheduling or
prove an analog discontinuity. No CPU-percentage rejection threshold is used.

The requested ten-minute alternating-record observation **fails after
395.390 seconds** with Windows `OSError`/`winerror=10048`. The timed transport
places the failure in `connect` for request 2190, before an HTTP response.
Microsoft identifies 10048 as
[WSAEADDRINUSE](https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2).
The following cleanup connection succeeds. This is not a completed ten-minute
pass, and no retry masks the failure.

A later host snapshot shows 497 total TIME_WAIT sockets, 451 to the board,
and a dynamic TCP range of 16,384 ports. It is not simultaneous with the
failure and does not establish port exhaustion. The interrupted capture
retains four post-warmup DMA queue events and zero driver write errors;
strict overall telemetry acceptance is false because observation stopped
early. Settled free heap returns from 132,996 to 133,004 bytes, with a
106,496-byte largest block both times. No allocation/panic/watchdog fault is
reported by the applicable runtime gate.

Across the whole interrupted observation, the readable counters record seven
queue events, including three near startup. The actual status-observation
duration is 394.281 seconds; 395.390 seconds includes the surrounding case
work. Neither interval is treated as a ten-minute completion.

## HTTP/TLS completion and OTA

All eight HTTP/TLS completion scenarios and their settings-preservation check
pass. They cover Content-Length, chunked transfer, close-delimited bodies,
TLS close-notify, raw socket closure and truncated bodies. Truncated framed
bodies and a close-delimited body without TLS close-notify end in `stream
read failed`; complete framed bodies and an authenticated close-delimited
ending produce `stream ended`. The untrusted-certificate case and its HTTP
recovery pass; normal certificate verification remains enabled.

All **15 original OTA report entries** pass, plus the original serial-health
gate: ten negative/interrupted uploads, two slot changes, a successful upload
during full HE-AACv2 HTTPS playback, a slow upload and restoration of the saved
station settings. Before the while-playing upload, three consecutive readings
confirm 44.1 kHz, stereo, 16-bit HE-AACv2 with `channels_are_core=false`.

However, the extended offline review finds two TLS error rows that the old
serial-health gate does not reject: components `Dynamic Impl` and
`esp-tls-mbedtls`, both at monotonic time 232419.421. They precede a software
reset banner by 94 ms, near the runner's explicit final restoration reboot.
The retained filter omits their numeric error codes. The rows could describe
one propagated failure; they are not proof of two separate failures or of an
allocation failure. Their cause and relationship to intentional cancellation
remain **unclassified**. The original passing results stay unchanged, and
extended runtime acceptance is `REVIEW_REQUIRED`.

The 75-second growing-record test after OTA passes all five original report
entries. Its selected post-warmup interval has zero queue events/write errors,
mean CPU busy 61.248%, minimum free heap 26,172 B and minimum largest block
17,408 B. The whole observed counter interval still contains **one startup
queue event**, which remains in the archive.

Across all six phases, **43 of 44 original report entries pass**. That count
includes idle/recovery/settings entries and is not a count of independent
audio formats. The additional original OTA serial-health check passes, but
the two TLS rows and DMA service findings remain open.

## Restoration and reproducibility

App-only OTA restores `idf61-qio80-8c1f2d2d` in `app1`, ELF identity
`54ec71b493261f3c00f86a649625c83e8c772b00eb2af5a3aae594c25e937094`.
Wi-Fi, playlist and settings comparisons pass. Three observations five seconds
apart confirm active 44.1 kHz stereo AAC. The previous integer-clock firmware
is running again; no experimental default is promoted.

The [frozen archive](../tests/results/esp32c3-tls-final-gates-20261009/)
contains 130 indexed files (6,275,437 bytes): original reports, diagnostic
rows, timed HTTP phases, public certificates, source snapshots and image
metadata. Private TLS keys and private board settings are excluded. Replay
verifies byte hashes, re-derives metrics and preserves every original verdict:

```powershell
python tests/results/esp32c3-tls-final-gates-20261009/replay.py --output .build/tls-final-gates-replay
```

Use a new output directory and installed Python test dependencies. Replay
contacts neither the board nor the network. Its `PASS` means evidence
integrity and identical analysis, not successful firmware qualification.

## Next experiment

At 4,000.869 encoded bytes/s, one 16 KiB record covers about 4.095 seconds of
audio. Full records arrive in bursts. The current prefill setting is a
**maximum** wait: it exits as soon as the encoded queue is full. Observed
prefill was 9 ms for the large/alternating cases, versus 500/509 ms for
small/growing records. An early full-queue exit may provide too little
timing margin at later record boundaries; this is a hypothesis, not a
demonstrated cause.

1. Repeat the interrupted ten-minute case with the same image and original
   failure policy. Capture host socket state if connect fails again; do not
   change Windows network settings or silently retry.
2. Add bounded input-wait and PCM-wait measurements to the staged-output
   diagnostic path, without allocating another audio buffer. Correlate
   starvation and DMA service events before changing task priorities.
3. Compare an optional minimum startup prefill (for example 250 ms) against
   the existing early-full behavior, bounded by the same 500 ms maximum.
   Retain immediate cancellation, generation ownership and finite-file EOF
   tests. Repeat the large-record cases with unchanged record pacing.
4. Retain safe numeric TLS error codes and explicit OTA/reboot timestamps.
   Re-run OTA and distinguish intentional cancellation from an active-playback
   TLS failure; do not exempt every error near a reboot or call this capture
   a clean TLS runtime pass.
5. Re-run the codec matrix and OTA on any selected firmware change. Keep
   nominal fractional clocking experimental until analog quality can be
   checked; the user cannot listen during this run.

The original failed run and all service events remain evidence. This
laboratory memory configuration does not yet qualify the quiet production
image or all public radio stations.

## Subsequent numeric TLS capture

The [minimum-250 follow-up](ESP32C3_MIN250_TLS_OTA_20261009.md) reproduces
two TLS messages 94 ms before the explicit restoration reboot, now with
persisted action timestamps and return `-76` (`MBEDTLS_ERR_NET_RECV_FAILED`).
This is a socket-read error; its underlying errno remains unknown. It narrows
the investigation without retroactively proving the cause of this earlier
capture. All 15 original OTA entries pass again, while extended TLS review
remains open. Both campaigns and their original failures are retained.
