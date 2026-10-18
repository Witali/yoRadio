This integration gate joins actual generated HTTPD code to actual C3/CYD
WebSocket service receive/control/session functions over localhost TCP.

`tests/run-websocket-integration.py --output <new-output>` freezes sources,
generates the pinned SDK overlay, extracts unchanged C function bodies, builds
with ASan/UBSan, and runs both SDK profiles. `--target c3` or `--target cyd`
selects one. The `.idf` installation is read-only. Output must be new so earlier
source snapshots and failures cannot be overwritten.

The test includes actual SDK HTTP parsing, pause/pending/unrecv, request
creation/deletion, URI matching/registration/pre/post callbacks, session context
APIs, framing and session deletion. The foreground adapter invokes actual
`httpd_sess_process()` on real TCP sockets. It checks request-lifetime cleanup
on success and failure, Close ownership, and reuse of a real descriptor.
The FreeRTOS HTTPD main loop is not linked.

The matrix checks handshake plus first frame in one send, short transport reads
and writes, fragmentation, interleaved binary Ping/unsolicited Pong, UTF-8 split
across fragments, malformed text, binary rejection, frame/message limits,
empty text/control frames, NUL command rejection, Close payload validation and
echo, frame header rejection, malformed offered handshake headers, omitted
upgrade headers and ordinary HTTP requests to `/ws`. Original pinned SDK
handshake functions provide historical negative controls for malformed
extensions, duplicate protocols and empty Content-Length.

`tests/run-websocket-tls-integration.py` takes `--integration-evidence`,
`--tls-cyd`, `--tls-c3`, `--crypto-cyd`, `--crypto-c3` and a new `--output`.
Its input TLS reports must already pass `tests/run-native-web-tls.py` for the
corresponding pinned SDK. It reuses their software crypto cache without
recompiling or installing dependencies. The C backend links actual native
transport/ESP-TLS to the actual SDK session APIs in the HTTPD translation unit;
HTTPD structures never cross into the backend's separate host type model.

The independent Python OpenSSL client verifies the test CA and `localhost`,
sends upgrade plus first frame in one TLS application write, and checks
fragments/control/UTF-8/Close and malformed handshakes. WS Accept uses actual
PSA SHA-1 and Base64, replacing the plaintext gate's documented SHA sample
seam. Test RSA keys, certificates and NTLS bundles exist only in Linux temporary
storage and are deleted after the run. Positive credentials use the qualified
PKCS1 PEM container; no credentials are archived in evidence output.

Explicit remaining seams are host HTTPD/ESP-TLS field models, FreeRTOS
scheduling, radio command dispatch/status, NVS, logging/error tracking and HTTP
error-response formatting. The command seam observes exact reassembled bytes;
radio settings and playback are covered by their own tests. Plain transport is
a POSIX adapter; the WSS gate links the actual native transport. Crypto uses
the pinned software configuration rather than ESP hardware acceleration or
dynamic buffers. These tests establish their documented integration matrix,
not target ABI, board RAM/stack/timing, TLS1.3 or full RFC6455 conformance.
