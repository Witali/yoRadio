# ESP32-C3 HTTP/TLS physical qualification, 2026-10-07

Branch: `codex/esp32c3-idf-upgrade`, ESP-IDF 6.1, awake SuperMini OLED.
This follows the [RFC audit](ESP32C3_HTTP_TLS_RFC_AUDIT_20261007.md) and
[TCP receive-window experiment](ESP32C3_TCP_RX_WINDOW_20261007.md).
The results qualify only the recorded runs. CPU is informational; no 85% gate
is applied. Status/serial observations are not an acoustic or PCM identity test.

## HTTP guard with a four-segment receive window

Image `esp32c3-idf-6.1-memory-icy-tlslab-rx4-http-guard`, embedded ELF hash
`58e00dd8b8fb14988a8aeebf75b98209ae73eeec598a9779132be5b9520c6e0b`.
It uses dynamic TLS, copied RX buffers and a 5,760-byte TCP receive window.
It retains the full 16 KiB TLS input limit and normal certificate roots plus
the explicitly labelled temporary laboratory CA.

All **44 local file cases pass**: 11 fixtures through HTTP and HTTPS, each
with automatic detection and an explicit codec hint. These cover MP3 320,
FLAC level 8, Vorbis q10, Opus 510, AAC-LC 320, LC at 22.05/44.1/48 kHz,
HE at 44.1/48 kHz, and HEv2 at 44.1 kHz. Settings restoration is a separate
45th passing check. File playback/EOF observations do not replace long soaks.

The public sources were independently probed with FFprobe; AAC additionally
uses the unquantized FAAD reference. Audio/metadata are not retained.

| Public HTTPS stream | Original gate | Mean CPU busy | Minimum free / largest block, B |
| --- | --- | ---: | ---: |
| LC 128 kbit/s | FAIL: heap-trend gate | 54.78% | 63,288 / 49,152 |
| HE 64 kbit/s | PASS | 64.45% | 26,484 / 12,800 |
| HE 32 kbit/s | PASS | 60.62% | 27,832 / 13,824 |
| Mono HE 16 kbit/s | PASS | 44.35% | 26,384 / 8,704 |
| MP3 256 kbit/s | FAIL: playback stops | 52.93% | 84,680 / 73,728 |

CPU/heap values above use the saved first-PCM +5..35-second window, clipped
to that station's actual observation. They are not minima over a ten-minute
run. The MP3 stops at 37.797 s. Its decoded/input progress is below real time
despite ample free RAM. A separate host connection receives 2,159,616 bytes
for 60.015 s without early EOF. That supports investigating TCP throughput;
it does not alone establish the cause on the board.

### Ten-minute alternating-record test: rejected

The 600-second HEv2 test alternates 1 KiB/16 KiB TLS records with concurrent
WebUI polling. At **270.906 s**, a **16,749-byte** TLS allocation fails:
**27,756 B total free, 15,360 B largest block**. By 274.812 s the board reports
`stream read failed`. This is a real interruption, not merely the old
phase-sensitive heap-trend gate. The reader guard contains the fatal read;
the log has one allocation failure and no repeated 46,622-byte request.
This observation does not prove the exact cause of that older request.

Settled idle heap recovers to 143,672 B with a 110,592-byte largest block.
The original playback/runtime FAILs remain saved. The four-segment overlay
must not become the default on the strength of short successful HE tests.

## Six-segment window comparison

The optional overlay selects 8,640 B and eight receive-mailbox entries.
The first image is `esp32c3-idf-6.1-memory-icy-tlslab-rx6-eof`, ELF
`f57860fbe7747285241ea6a617acdef6d03a6b814d3ab0c12a40cddfd6d3f096`.
Its attempted TLS EOF shim was **not linked into the read path**; retain this
image as a rejected integration revision, not an EOF fix.

| Public HTTPS stream | Original gate | Mean CPU busy | Minimum free / largest block, B |
| --- | --- | ---: | ---: |
| LC 128 kbit/s | FAIL: largest-block trend | 53.60% | 60,048 / 43,008 |
| HE 64 kbit/s | PASS | 64.33% | 25,308 / 12,288 |
| HE 32 kbit/s | FAIL: heap trend | 61.43% | 25,244 / 11,776 |
| Mono HE 16 kbit/s | PASS | 44.93% | 23,200 / 9,728 |
| MP3 256 kbit/s | PASS | 67.37% | 84,776 / 69,632 |

MP3 now passes this 60-second run, including real-time progress checks.
Live source/Wi-Fi variation still applies. This is not a ten-minute
qualification or evidence that HE memory fragmentation is fixed. Preserve
the original trend FAILs; periodic dynamic TLS size changes can affect their
interpretation. Do not relabel them as PASS after the fact.

## TLS EOF integration negative control

On the RX4 guard image, a close-delimited HTTPS body with `close_notify`
finishes normally; an otherwise identical raw TCP close is incorrectly
reported as normal EOF. The first RX6 image repeats that failure (seven of
eight framing cases pass, `close-raw` fails).

ESP-IDF already supplies `__wrap_mbedtls_ssl_read` for dynamic buffers. The
first shim used the same symbol and its archive member was not selected.
The original symbol-only audit gave a false positive by inspecting the SDK
wrapper. Both that report and the stronger audit's rejection are retained.
The stronger check requires the distinct application function in the actual
ESP-TLS call path and separately checks SDK RX-buffer allocation/free calls.

The corrected integration redirects only `esp_tls_mbedtls.c` to
`yoradio_mbedtls_ssl_read`; this function calls the normal mbedTLS symbol,
which still traverses ESP-IDF's dynamic wrapper. It changes raw transport EOF
to a negative connection-EOF result while preserving clean closure, valid
bytes and retry codes. It adds no buffers or persistent state.

## Corrected integration: physical PASS

Image `esp32c3-idf-6.1-memory-icy-tlslab-rx6-eof-fixed`, ELF
`9fb68fbdfd509d58fde9b4b3948e4b3aba1dc59dd0c7625ed2503b9ee549884d`,
passes the stronger linked call audit and the linked AAC audit.

| HTTPS fixture | Expected final status | Physical result |
| --- | --- | --- |
| Complete Content-Length + close alert | `stream ended` | PASS |
| Complete Content-Length + raw close | `stream ended` | PASS |
| Content-Length short by one byte + close alert | `stream read failed` | PASS |
| Complete chunked + close alert | `stream ended` | PASS |
| Complete chunked + raw close | `stream ended` | PASS |
| Missing terminal chunk + close alert | `stream read failed` | PASS |
| Close-delimited + close alert | `stream ended` | PASS |
| Close-delimited + raw close | `stream read failed` | PASS |

Every case first observes full 44.1 kHz stereo HEv2 PCM. The fixtures send
all valid audio frames; truncation is deliberately in HTTP framing, so these
cases isolate message completeness from malformed AAC. Settings preservation
also passes. Host parser/adapter tests pass 85 cases on each of IDF 6.0.3 and
6.1 with ASan/UBSan. The separate real-TLS server test checks all eight wire
variants, and four record-server tests check normal close-alert behavior.

Two targeted public 60-second reruns also pass:

| Stream | Mean CPU busy | Minimum free / largest, B |
| --- | ---: | ---: |
| HE 64 kbit/s | 65.53% | 23,804 / 8,704 |
| MP3 256 kbit/s | 66.50% | 84,860 / 69,632 |

These CPU/heap values again use the clipped +5..35-second summary window.
They do not replace ten-minute HE/TLS memory qualification.

After both physical sessions, app-only OTA restores the ordinary
`esp32c3-idf-6.1-compact-icy-quiet` image, ELF
`da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0`.
An explicit Stop is followed by three stopped observations over 15 seconds.
Settings are unchanged. No lab trust root remains in the running image.

## Retained evidence and remaining work

The [evidence directory](../tests/results/esp32c3-http-tls-physical-20261007/)
contains original PASS/FAIL reports, filtered serial/status data, exact source
revisions by hash, public certificates, build/linked audits and image identities.
The source inventory can include modules not used by a particular runner;
that does not establish their execution. Private keys and received audio are
excluded. `index.json` hashes every archived file except itself.

The normal static-TLS build `esp32c3-idf-6.1-compact-icy-quiet-eof` also passes
compilation and linked HTTP/TLS/AAC audits. It retains normal public roots,
is saved under `firmware/development`, and was not installed or physically
qualified. This check is separate from the physical dynamic-buffer image.
Broader remaining gates include contiguous TLS/SBR allocation, long
public playback, outbound TLS closure/alerts and certificate-identity negative
fixtures. The incoming EOF fix alone cannot certify full HTTPS.
