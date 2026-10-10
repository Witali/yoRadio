# Quiet HE-AAC playback with measured TLS record sizes

## Scope and result

The physical ESP32-C3 campaign completes **58/58 checks**.
Failed checks: None.
It runs eight 75-second playback observations: HE-AAC and HE-AACv2, each with
constant 1 KiB records, constant 16 KiB records, growth from 1 to 16 KiB after
30 seconds, and alternating sizes. Delivery is paced at exactly 1.0 audio
seconds per wall second. Both profiles produce 44.1 kHz stereo PCM.

| Profile / TLS record mode | Min free / largest, B | Output drops / errors | Max status + health, ms | Gates |
| --- | ---: | ---: | ---: | ---: |
| he-44100-stereo:small | 30,296 / 21,504 | 0 / 0 | 185 | 7/7 |
| he-44100-stereo:large | 32,492 / 24,576 | 0 / 0 | 193 | 7/7 |
| he-44100-stereo:grow | 32,048 / 24,576 | 0 / 0 | 187 | 7/7 |
| he-44100-stereo:alternate | 25,648 / 13,824 | 0 / 0 | 199 | 7/7 |
| hev2-44100-stereo:small | 32,480 / 24,576 | 0 / 0 | 186 | 7/7 |
| hev2-44100-stereo:large | 32,612 / 24,576 | 0 / 0 | 197 | 7/7 |
| hev2-44100-stereo:grow | 31,752 / 22,528 | 0 / 0 | 195 | 7/7 |
| hev2-44100-stereo:alternate | 32,432 / 24,576 | 0 / 0 | 200 | 7/7 |

The output deltas cover each measured steady window after a 15-second
startup exclusion; the raw lifetime counters keep startup/idle/Stop events.
The table rounds response times up. Free/largest values are sampled minima,
not a guarantee about allocations between observations.

Across 621 health observations, the allocation-failure
and watchdog counters are 0 and
0; boot identity remains unchanged.
The SDK lifetime minimum free heap is 15,940 bytes,
including startup and transients outside the steady windows.
`review.json` records exact durations, record counts, first full-rate PCM,
RSSI ranges and memory recovery after each Stop.

## Image and protocol evidence

The reused laboratory application is `idf61-quiet-growth-tls`, app SHA-256
`7871681aef75c9bb89caffab97f073eabe62b272ff8dc20f710cb4473c56b6fd`. Its earlier build audit shows identical
application code/constants and static RAM to the quiet output-health image;
the test image only adds one local CA to all 145 public trust entries.
QIO/80 MHz, nominal fractional 48 kHz output, full compact AAC, 17,058-byte
TLS RX reserve and the four-slot input floor remain unchanged. There is no
UART capture or optional runtime CPU profiling in this campaign.

The server negotiates TLS 1.2 / `ECDHE-RSA-AES128-GCM-SHA256`. Its MemoryBIO
parser observes actual ciphertext records, and the verifier compares them
with completed socket writes. A 16 KiB plaintext record is the maximum allowed
by [RFC 5246 section 6.2.1](https://www.rfc-editor.org/rfc/rfc5246.html#section-6.2.1).
With this AES-GCM suite, recorded payload lengths are 1,048 and 16,408 bytes:
the plaintext plus an 8-byte explicit nonce and a 16-byte authentication tag;
the 5-byte outer record header is separate. See
[RFC 5288 section 3](https://www.rfc-editor.org/rfc/rfc5288.html#section-3).

For growth cases, the first 16 KiB record must occur after the board first
reports full-rate PCM. Gates reject retried/ended TLS connections, incorrect
fixture hashes, changed pacing, incomplete write evidence, missing samples,
late PCM startup, stopped/mismatched playback and output errors independently.
The server may record a socket error after intentional Stop; the immutable
pre-Stop snapshot is the acceptance evidence, and later events are also saved.

## Interpretation and remaining work

These observations test maximum-size application records and size changes
with a live HE-AAC decoder. They do not reduce the existing 8,192-byte
largest-block budget or overwrite the earlier 7,424-byte headroom failures
in [the AAC frame-growth campaign](ESP32C3_AAC_TLS_HEADROOM_20261010.md).
The AAC fixtures are repeated without changing their frame payloads or lengths;
this is TLS-record growth, a separate scenario from ADTS frame growth.

This is not a renegotiation test. The pinned ESP-IDF `set_client_config()`
explicitly enables TLS renegotiation when `CONFIG_MBEDTLS_SSL_RENEGOTIATION=y`,
which the saved image uses. Its dynamic adapter can allocate handshake,
session and transform state again. The RX reserve alone does not reserve
those allocations. Late handshake allocation requirements remain to be checked.
Likewise, a run without the earlier seven-second WebUI delay does not establish
that delay's cause or resolution. Output service counters do not measure the
analog waveform. Production qualification remains open.

The controller restores the exact listened `idf61-listen48-8c1f2d` application
and verifies Wi-Fi/playlist/settings persistence plus three stopped states.
No serial recovery or settings erase is used.

[Frozen measurements and offline replay](../tests/results/esp32c3-quiet-tls-records-20261010/README.md).
