# Public MP3 / HE-AAC: HTTP/TLS failure diagnostics

## Findings

| Case, 120 s | First stopped status, s | New fatal reads | TLS code | Lost notifications while playing after warmup | Host decoded 125 s | Min free / largest, B |
| --- | ---: | ---: | --- | ---: | --- | ---: |
| mp3-first | 23.21 | 1 | 0x7280 | 531 | True | 78,764 / 69,632 |
| he64 | none | 0 | no new error | 224 | True | 21,056 / 7,168 |
| mp3-repeat | 21.51 | 1 | 0x7280 | 317 | False | 79,140 / 65,536 |

The numeric failure snapshot identifies `0x7280` as the positive form of
`MBEDTLS_ERR_SSL_CONN_EOF` in this SDK. Our existing TLS adapter maps a nonempty
read returning zero to that error, preserving the distinction between transport
EOF and TLS `close_notify`. The observed system errno 128 is `ENOTCONN` in the
ESP toolchain; it is an accompanying snapshot, not proof of why the peer closed.
`esp_tls_error` 32797 is `ESP_ERR_MBEDTLS_SSL_READ_FAILED`.
The error is not an allocation-failure code. Authenticated partial HTTP bytes
returned before the failure are still passed to the decoder; the connection is
then closed and is never read again.

The host independently decodes the same public URLs with FFmpeg, TLS verification
enabled, to a null output. Host completion demonstrates that a separate client
could decode the source during the observation. It does not prove both clients
used identical connections, packets, DNS destinations, HTTP headers or PCM.
No radio audio or private device settings are saved.

In the repeated MP3 case the host also ends early: 25.887347 seconds of decoded
audio, TLS EOF and a premature-stream/demux I/O error. FFmpeg exits with code 0,
so checking exit status alone would falsely report success; the review additionally
requires at least 124 seconds of decoded audio and a completed progress record.
The first MP3 host control and HE-AAC host control each decode all 125 seconds
without logged errors. Thus an external source/path failure is independently
observed, but this does not prove that every board interruption has that cause.

Pipeline events mainly show phase 7: output is waiting for PCM, decoder for
encoded input, and the stream task is inside HTTP reading. These are call-phase
observations, not scheduler traces. The detailed event ages and overwritten-event
counts are retained in `review.json`; the 16-event ring cannot retain every event.
Output notification losses are not counted as missing audio samples or clicks.
The table excludes periods after the first stopped status. The original full
window, including intentional idle after a failure, remains in `physical/results.json`.

The campaign records 0 failed allocations and
0 watchdog events in 656 observations,
with one boot identity. Settled idle recovery: **PASS**.
Memory-floor failures remain recorded. Diagnostics change memory layout; these
numbers are not a direct replacement for normal-image qualification.

## Implementation and checks

`CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC` remains disabled by default.
It now preserves the last fatal HTTP/TLS read's result, ESP-TLS code, mbedTLS
code, errno, timestamp and sequence in 24 extra static bytes. The total probe
structure is 540 bytes. Capture occurs before close, under an interrupt mask
on the single-core C3, and health serializes a consistent copied snapshot.
Transient retries do not overwrite fatal-error evidence. The timestamp is a
wrapping 32-bit microsecond value; interpret it in bounded observations.

- Actual SDK HTTP reader/parser/TLS adapter harness: 85 cases with diagnostics
  off and 85 with diagnostics on, ASan/UBSan PASS. Fatal retry, partial bytes,
  temporary errors, EOF/framing and errno capture before later API calls are checked.
- Bounded native health JSON: four watchdog/diagnostic combinations, ASan/UBSan PASS.
- Numeric diagnostic validation: five Python tests PASS.
- Build audit: full AAC/FLAC codec arithmetic unchanged in 119 code/constant
  sections across 18 objects; normal public CA bundle preserved.

Compared with the normal one-second-prefill candidate, linked DRAM data grows
by 536 bytes, BSS is unchanged, and IRAM instructions grow by 132 bytes within
the same aligned IRAM allocation. These linked deltas include layout effects;
the new failure record itself is exactly 24 bytes.

## Next action

Compare HTTP and HTTPS at the same MP3 sample rate/bitrate and controlled delivery,
then isolate TCP/TLS delivery delays and per-connection closure. Include a
44.1 kHz MP3 control because the existing high-bitrate local MP3 fixture is 48 kHz.
Investigate contiguous-memory headroom separately without weakening TLS closure
validation or accepting failed reads as clean EOF. Retry/reconnect policy requires
generation/lifetime and unavailable-station-timeout tests before changing it.

This diagnosis narrows the cause; it does not fix playback or qualify production.
The exact listened firmware/settings were restored after the campaign.

App SHA-256: `174d78968f7e02b37fc05d0d9ae00ad9d342b4bb4b615ce831e771fa6b15947d`.
ELF SHA-256: `ef2b83a5762b28ac34476175bd01365624c86ff737a390e44935c779e591bb85`.

[Frozen evidence](../tests/results/esp32c3-public-read-diagnostic-20261010/README.md).
