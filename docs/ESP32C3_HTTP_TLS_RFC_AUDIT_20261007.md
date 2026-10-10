# ESP32-C3 HTTP/TLS read audit, 2026-10-07

Scope: the radio stream reader on `codex/esp32c3-idf-upgrade`, ESP-IDF
6.0.3 and 6.1. This is a targeted audit, **not full HTTP or HTTPS conformance
certification**. It accompanies the [TLS memory experiments](ESP32C3_TLS_RECORD_MEMORY_20261007.md).

## Requirements and evidence

| Requirement | Implementation / verification | Result |
| --- | --- | --- |
| A length-delimited response needs all declared bytes; chunked needs its terminator. [RFC 9112 §§6.3, 8](https://www.rfc-editor.org/rfc/rfc9112.html#section-8) | Real SDK parser/read functions: exact and truncated bodies, missing terminal chunk, malformed size, chunk extensions/trailers, 1/2/4/8-byte fragmentation. | Host PASS |
| TLS closure alone does not establish HTTP completeness. Explicit framing can establish completeness despite an incomplete TLS close; an unframed HTTPS body needs `close_notify`. [RFC 9112 §9.8](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.8) | The new pre-adapter shim preserves raw transport EOF as an error. Complete framed bodies still finish without an extra read. | Host PASS on both SDKs; eight physical framing cases PASS on 6.1 |
| Fatal TLS alerts terminate the connection. [RFC 5246 §7.2.2](https://www.rfc-editor.org/rfc/rfc5246.html#section-7.2.2), [RFC 8446 §6.2](https://www.rfc-editor.org/rfc/rfc8446.html#section-6.2) | New per-connection reader closes immediately after a recorded fatal TLS read error, preserves valid preceding bytes, then returns failure without re-entering TLS. | Host PASS; physical allocation failure ends as read failure; outbound alert emission remains open |
| A client that does not reuse HTTP connections sends `Connection: close`. [RFC 9112 §9.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3) | Explicit header added. The existing TCP keepalive option controls probes, not HTTP reuse. | Stream-task host PASS |
| Temporary lack of data is distinct from connection termination. [RFC 9112 §9.5](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.5) | Preserve EAGAIN and partial-byte timeout retries. The application retains its configurable station-availability deadline. | Host PASS, including timeout inside a chunk |
| TLS 1.2 plaintext records can carry 16,384 bytes. [RFC 5246 §6.2.1](https://www.rfc-editor.org/rfc/rfc5246.html#section-6.2.1) | Both receive-window experiments retain the full input-record capacity and certificate bundle. | Build/config audit PASS; separate physical report |

HTTPS authenticates the origin in addition to transporting HTTP; see
[RFC 9110 §4.3.4](https://www.rfc-editor.org/rfc/rfc9110.html#section-4.3.4).
The production client continues to use `esp_crt_bundle_attach`, with no
skip-verification or skip-hostname option. Previous physical testing rejected
the lab certificate on an ordinary image. This audit does not add a physical
wrong-hostname or expired-certificate test.

## Confirmed partial-read bug

In both audited SDKs, `esp_http_client_read` returns the already copied byte
count when a later transport read fails. Its positive result hides that error
from a caller which only checks the return value. The unguarded negative
control reproduces an additional TLS read on the next call.

`stream_http_read` also reads the SDK's saved TLS error. ESP-TLS stores a
positive magnitude for the underlying negative TLS code. A timeout is also
recorded as `ESP_ERR_MBEDTLS_SSL_READ_FAILED`, so that outer error alone must
not trigger teardown. The guard excludes temporary TLS codes, closes a failed
connection before the caller can block on its audio queue, and latches failure.
The next call produces the existing `AUDIO_END_READ_FAILED` marker. A new
connection gets fresh state. No allocation or additional PCM buffer is added.

This demonstrates a possible retry after the earlier allocation failure; it
does **not** establish the exact cause of the historical 46,622-byte request.

## Tests and reproducibility

```powershell
python tests/test-stream-http-reader.py --idf C:/Work/yoRadio/.idf/v6.0.3 --output .build/http-rfc-603
python tests/test-stream-http-reader.py --idf C:/Work/yoRadio/.idf/v6.1 --output .build/http-rfc-61
python tests/run-stream-connection-retry.py --output .build/stream-task-http-guard
```

The first runner uses WSL GCC with AddressSanitizer and UndefinedBehaviorSanitizer.
It compiles the selected SDK's actual HTTP parser, extracted read/completion
functions, body callbacks and TLS 1.2 read adapter, plus the production guard.
Transport results, mbedTLS results and header bookkeeping are controlled seams;
this does not emulate cryptography or radio hardware. Error constants for the
allocation/MAC/closure probes come from that SDK's headers, including its PSA
allocation-error alias.

Initial results: **70 cases PASS on each SDK**, and **37 stream-task cases PASS**.
The latter compile the actual stream task/guard and ICY parser, covering
cancellation, retry deadlines, EOF versus failure, header selection and immediate
close on a partial fatal read. Reports and logs are saved under
[`tests/results/esp32c3-http-rfc-20261007`](../tests/results/esp32c3-http-rfc-20261007/).
The unchanged SDK function/parser hashes match across these two versions;
the complete SDK source-file hashes differ and are recorded individually.

The initial integrated ESP32-C3 build and linked AAC audit also pass. The saved
[`memory-icy-tlslab-rx4-http-guard` image](../firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx4-http-guard/manifest.json)
records hashes for the source changes over its base commit. It is a laboratory
image has since passed 44 local HTTP/HTTPS format cases. Its ten-minute record
soak still fails a contiguous TLS allocation; see the
[physical follow-up](ESP32C3_HTTP_TLS_PHYSICAL_20261007.md).

## Incoming TLS EOF correction

The updated host suite passes **85 cases on each SDK**, including raw EOF,
clean close alerts, complete explicit framing and zero-length reads. The
application function `yoradio_mbedtls_ssl_read` runs before ESP-TLS collapses
raw EOF and a peer close alert. It calls the ordinary mbedTLS symbol so the
SDK's dynamic-buffer wrapper remains in the call chain. Only a nonempty read
returning zero changes to `MBEDTLS_ERR_SSL_CONN_EOF`; no buffer is added.

The first attempted integration collided with the SDK's wrapper name. Host
tests passed, but the physical raw-EOF negative test failed. That rejected
revision and the original insufficient link audit remain in the evidence.
The corrected build uses a distinct entry point and a source-local compiler
alias in `esp_tls_mbedtls.c`. Its linked audit verifies both the application
entry point and the SDK's RX allocation/free calls. The revised audit also
rejects the earlier image, rather than mistaking the SDK wrapper for the fix.

With the corrected ESP-IDF 6.1 image, **all eight real TLS/HTTP framing cases
pass on the board**, plus settings preservation. Each first observes full
HEv2 PCM format, then checks the terminal status. Explicit-length/chunked
completion, truncated framing, clean unframed closure and raw unframed EOF
are distinct fixtures. See the physical report for image hashes and limitations.

## Remaining work before claiming HTTPS closure compliance

- Audit and implement graceful outbound TLS closure on the normal Stop/EOF
  path. The current ESP-TLS destroy path frees SSL and closes the socket without
  an explicit `mbedtls_ssl_close_notify` call. [RFC 9112 §9.8](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.8)
- Verify required fatal-alert emission on wire, including local allocation
  failure. The guard proves teardown/no further reads; it does not implement
  or certify the TLS library's alert-generation behavior.
- Audit the transport's WANT_WRITE path: ESP-TLS does not save WANT_READ/WRITE
  as errors, and `transport_ssl.c` only maps WANT_READ/TIMEOUT to a receive
  timeout. A synthetic saved WANT_WRITE test is not end-to-end coverage.
- Add wrong-hostname/expiry fixtures beyond the new real TLS truncation tests;
  malformed/incomplete headers, informational responses, transfer-coding
  combinations and redirect trust transitions need separate coverage.
- Repeat long-load qualification after the independent memory-allocation fix.
  Correct HTTP terminal status does not make interrupted playback acceptable.

Keep TLS 1.3 RFC requirements as a design reference. These tests exercise the
current TLS 1.2 build; they do not qualify a TLS 1.3 configuration.
