# ESP32-C3 four-segment TCP receive-window experiment

Date: 2026-10-07. Branch: `codex/esp32c3-idf-upgrade`.

**Keep this optional.** Smaller receive bursts eliminated the observed dynamic
TLS allocation failures in this run, but both image suites still have an original
FAIL. Public/high-bitrate/long-RTT playback and a ten-minute soak remain open.

## Controlled change

`sdkconfig.tcp-rx-four-segments.defaults` changes the TCP receive window from
11,520 to 5,760 bytes and receive mailbox from 10 to 6 entries. Saved config
comparison finds exactly these two settings and their compatibility aliases.
All other settings match the corresponding
[previous TLS laboratory images](ESP32C3_TLS_RECORD_MEMORY_20261007.md).

TCP transports a byte stream, not complete TLS records; see
[RFC 9293 §2.2](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2).
The receiver can consume portions while assembling a TLS record across windows.
Both images retain `CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384`; the experiment
does not restrict the peer to small records. Normal public roots remain intact,
with the same one temporary test CA added only in labelled laboratory images.

Firmware binaries, configs and manifests:

- [`esp32c3-idf-6.1-memory-icy-tlslab-rx4-dynamic`](../firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx4-dynamic/manifest.json)
- [`esp32c3-idf-6.1-memory-icy-tlslab-rx4-static`](../firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx4-static/manifest.json)

Both were built from `919c7f34`, plus the receive-window overlay. They do **not**
include the later [HTTP fatal-read guard](ESP32C3_HTTP_TLS_RFC_AUDIT_20261007.md).
The linked compact SBR owner remains 32,744 bytes. Certificates, input capacity,
codec support and PCM precision settings are unchanged.

## Physical results

Same ESP32-C3, HE-AAC v2 fixture, full 44,100 Hz / 16-bit stereo, four 75-second
record modes, WebUI polling and passive serial diagnostics. TLS 1.2 negotiated
ECDHE-RSA-AES128-GCM-SHA256: plaintext 1,024/16,384 bytes correspond to encrypted
payloads 1,048/16,408 bytes. Frozen pre-Stop record evidence passes all eight modes.

| TLS storage | Record mode | Original gate | Allocation failures | Mean active CPU | Minimum free / largest block, bytes |
| --- | --- | --- | ---: | ---: | ---: |
| Dynamic | Small | PASS | 0 | 71.83% | 36,728 / 24,576 |
| Dynamic | Large | PASS | 0 | 70.58% | 19,308 / 7,936 |
| Dynamic | Grow after 30 s | PASS | 0 | 71.04% | 19,404 / 4,608 |
| Dynamic | Alternate | **FAIL: heap trend** | 0 | 70.68% | 18,948 / 7,936 |
| Static | Small | PASS | 0 | 75.92% | 14,728 / 6,144 |
| Static | Large | **FAIL: allocation** | 3 | 74.28% | 14,360 / 4,608 |
| Static | Grow after 30 s | PASS | 0 | 75.23% | 14,372 / 5,120 |
| Static | Alternate | PASS | 0 | 74.95% | 8,608 / 6,144 |

CPU and heap columns use windows after the first full PCM observation plus five
seconds, ending at the last full PCM observation. They exclude startup and idle;
the original gate reports retain their own wider window. Periodic heap samples
do not capture every allocation-time low. CPU is informational, with no 85% gate.

All eight modes retained full-format observations through playback. This is not
an acoustic or DMA-underrun proof. Maximum observed WebUI request duration was
392 ms (rounded up); RSSI ranged from -76 to -67 dBm across the samples.

The static large-record failures are three 1,700-byte requests. At those instants
the largest compatible block was only 1,664 bytes, with 5,212 or 8,312 bytes free.
The previous static experiment had 167 allocation failures over its large/grow/
alternate modes; improvement in this run is not a guarantee across runs.

### Preserve the dynamic alternate FAIL

The unchanged gate compares medians of the first and last three CPU heap samples:
36,752 versus 19,368 bytes. That exceeds its 2,048-byte allowance. The raw trace
repeatedly returns to 36,752 bytes and ends at 36,740 bytes, with the same
17,408-byte largest block at those high-free points. This is consistent with
temporary TLS/RX allocation, but does not prove its lifetime or rule out a slower
leak. Do not rewrite the result as PASS. Add phase-aware measurements and a
ten-minute run before changing the gate or promoting the setting.

Both idle-recovery and settings-persistence checks pass. The normal quiet image
is restored by OTA after the experiment, with an explicit Stop and independent
15-second confirmation recorded in `final-board.json`.

## Evidence and next gates

The archive is
[`tests/results/esp32c3-tcp-rx-window-20261007`](../tests/results/esp32c3-tcp-rx-window-20261007/).
It retains original reports, status/serial observations, exact hashes, frozen
record snapshots, build audits and reproduction scripts. It contains no private key.

- Repeat public LC/HE/mono-HE/MP3 and high-bitrate FLAC/WAV/other codecs. A smaller
  window reduces the bandwidth-delay budget; local low-bitrate AAC is insufficient.
- Run ten minutes with alternating records and phase-aware heap measurements.
- Recheck station switches, full-rate late SBR/PS, EOF and OTA under playback.
- Qualify the HTTP guard separately; the results above cannot be attributed to it.
- Keep full TLS record capacity and certificate validation during further RAM work.
