# Native WebSocket TLS/WSS implementation and qualification

Status, 2026-10-18: the shared public ESP-TLS transport and both WebSocket
adapters are implemented. Deterministic fault/application tests and actual
pinned TLS interoperability pass, including a CA/SAN-validating independent
client. Integrated WSS passes on both pins. Complete SDK linking and physical
resource qualification have their own gates below. Framing tests alone do not
establish full RFC compliance.

[RFC 6455 section 10.6](https://www.rfc-editor.org/rfc/rfc6455.html#section-10.6)
requires TLS support. WSS remains part of the user's full-standard requirement.
Optional WebSocket extensions are a separate negotiation choice.

## Chosen transport and entry points

The shared [component](../idf/components/native_web_transport/),
[public contract](../idf/components/native_web_transport/include/native_web_transport.h),
and [implementation](../idf/components/native_web_transport/native_web_transport.c)
use one existing `httpd_start` instance. They do not use `esp_https_server`, copy
opaque layouts, capture private callbacks, or modify the SDK installation.

Startup calls `native_web_transport_prepare(&config)` before the listener.
Secure configuration supplies HTTPD's `open_fn` and `close_fn`, port 443, three
client slots, and at least 10240 stack bytes. Task priority/core affinity remain
unchanged. After checked HTTPD stop/join, or listener start failure,
`native_web_transport_release()` wipes configuration memory; it refuses while
sessions remain. C3 retains its existing policy of keeping an already running
server/workers on route registration failure. This is not complete C3 startup
rollback qualification.

| Function | Responsibility |
| --- | --- |
| `native_web_transport_prepare` | Validate one NVS blob; choose maintenance or secure mode; amend caller's HTTPD config |
| `httpd_open_tls` | Reserve up to three sessions; attach public context; make fd nonblocking; finish bounded TLS handshake; install public transport overrides |
| `native_web_transport_send/recv` | One nonblocking operation through owned ESP-TLS, or lwIP in maintenance mode; expose actual WANT direction |
| `httpd_send_tls/httpd_recv_tls` | Bound HTTPD retries; complete short writes under one overall call deadline |
| `httpd_pending_tls` | Report plaintext buffered by lookahead/TLS without a fresh TCP readiness event |
| `native_web_transport_shutdown` | Fatal shutdown or bounded TLS alert after clean WebSocket Close |
| `httpd_close_tls/tls_free` | HTTPD owns final fd close; context free owns exactly one server TLS deletion |
| `native_web_transport_provision` | Trusted local API to validate and replace one NVS blob for next startup |

Both SDK pins expose `esp_tls_init`, `esp_tls_server_session_init`,
`esp_tls_server_session_continue_async`, `esp_tls_set_conn_state`,
`esp_tls_conn_read/write`, `esp_tls_get_bytes_avail`,
`esp_tls_get_ssl_context`, and `esp_tls_server_session_delete`.
The server destructor frees TLS without closing HTTPD's socket; the client
destructor `esp_tls_conn_destroy` has different ownership and is not used.
`mbedtls_ssl_close_notify` receives the actual selected backend through the
public SSL-context getter, with a compile guard for the mbedTLS server backend.

Both [C3](../idf/esp32c3-oled-native/main/websocket_service.c) and
[CYD](../idf/esp32-cyd2usb-native/main/websocket_service.c) frame overrides call
the shared transport. Their pre-handshake hooks wrap HTTP101 too. No secure
application send/receive issues raw `lwip_send/lwip_recv`. The existing
one-second frame/handler deadline spans header/mask/payload and retries. A TLS
write can request readability; a read can request writability. Pending write
arguments remain unchanged across WANT retries. Failed/expired HTTPD I/O marks
the TLS session aborted so cleanup cannot resume a pending write after its
buffer is freed.

Handshake budget is three seconds including session initialization; HTTPD I/O
calls have one second; clean TLS alerts have 200 ms. Readiness uses `lwip_select`
and scheduler yields, including EINTR handling. Crypto calls are synchronous:
elapsed time is checked after them, but an individual CPU call cannot be
preempted by the deadline. Board CPU/watchdog behavior remains a physical gate.
`MSG_PEEK` retains at most 128 plaintext bytes; subsequent reads drain that
prefix. Fatal transport failure and normal Close have different cleanup paths.

## Why the HTTPS wrapper was not selected

The initial feasibility proposal used typed private-header callback capture.
Own public HTTPD open/transport callbacks remove that dependency. The inspected
wrapper differences below are reasons for this choice, not active requirements
to patch the SDK:

* Public HTTPD has no getters for installed send/recv/pending functions; HTTPS
  transport context is private.
* HTTPS send/recv ignore flags: passing `MSG_DONTWAIT` does not bound inner TLS
  operations. Their event posts can also add blocking time.
* Configured HTTPS application `open_fn` runs after TLS and ignores its return;
  plain HTTPD rejects and deletes failed `open_fn` sessions correctly.
* In 6.0.2, allocating HTTPS transport context after successful TLS can leak TLS
  on OOM. Pinned 6.1 fixes it. Our context is attached before later failures and
  covered by allocation-failure tests.
* Pinned 6.1 adds unified `server_key` and optional HTTPS events; the common
  PEM/public ESP-TLS implementation requires neither.

## Credentials and out-of-band provisioning

NVS namespace **`web_tls`**, key **`bundle`**, stores one versioned blob. Absent
namespace/key means documented unprovisioned **maintenance HTTP/WS**. Mode 0
explicitly selects maintenance. A malformed blob, invalid certificate, wrong
key, or requested TLS startup failure returns an error without plaintext
fallback.

NTLS v1 header is 16 bytes, little endian:

| Offset | Type | Value |
| --- | --- | --- |
| 0 | byte[4] | `NTLS` |
| 4 | uint16 | Version 1 |
| 6 | uint16 | Mode 0 maintenance or 1 TLS |
| 8 | uint32 | Chain length, maximum 8192 |
| 12 | uint32 | Key length, maximum 4096 |
| 16 | bytes | Exact PEM chain followed by PEM key, without NUL terminators |

Native validation checks exact size, embedded NULs, PSA initialization,
certificate parse, private-key parse, and public/private pairing. One owned
allocation receives separate terminators and is wiped on failure/stop.
Provisioning validates a private copy before `nvs_set_blob`/`nvs_commit`. A
single blob avoids reading a certificate and key from different successful
updates; interrupted writes/rotation still require power-loss qualification.

The [local packer](../idf/components/native_web_transport/tools/pack_tls_bundle.py)
accepts a PEM certificate chain and an **unencrypted RSA PKCS#1 PEM key**
(`BEGIN RSA PRIVATE KEY`), validates local SSL pairing, and creates NTLS or NVS
CSV. This is the qualified initial provisioning profile. Other key algorithms
and containers are not qualified. It refuses output anywhere inside this repository/worktree,
creates a new file exclusively, and uses 0600 on POSIX. The containing directory
must be private; Windows ACLs remain the user's policy. It does not generate an
identity, contact/flash a device, replace NVS, or install trust. Example inputs
and output below are outside the repository and contain secrets:

```powershell
python idf/components/native_web_transport/tools/pack_tls_bundle.py `
  --certificate "$env:USERPROFILE\YoRadioSecrets\server-chain.pem" `
  --key "$env:USERPROFILE\YoRadioSecrets\server-key.pem" `
  --format ntls --output "$env:USERPROFILE\YoRadioSecrets\web-tls.ntls"
```

For factory provisioning, `--format nvs-csv` produces `web_tls`/`bundle` using
`data,hex2bin`, supported by the installed Espressif NVS partition generator.
Use a reviewed factory image/process or call `native_web_transport_provision`
from a trusted local integration. No unauthenticated key-upload route exists.
Do not replace live NVS with a TLS-only image: it also stores device settings.
Flashing/replacing NVS is a separate explicit device operation that must retain
those settings.

RSA PKCS#8 (`BEGIN PRIVATE KEY`) is rejected by the packer, including a valid
matching key. Both pinned crypto trees parse that format but leave the private
context's public-key cache empty: `tf-psa-crypto/extras/pkparse.c:799` imports the
RSA key without deriving the public part; PKCS#1's path at line965 derives it.
`extras/pk.c:1417` then rejects the empty cache with
`PSA_ERROR_INVALID_ARGUMENT` (-135). These files are identical across the two
pins, and the RSA branch is enabled in both target configurations; this is not
merely an extracted host ABI behavior. Real pinned-library tests reproduced
PKCS#8 failure and successful matching PKCS#1 provisioning/TLS. The embedded
`mbedtls_pk_check_pair` remains strict and unchanged; no failed crypto check is
ignored. Native provisioning may accept other formats only if that same check
succeeds, but acceptance and interoperability outside the profile are not
claimed.

Convert an existing RSA key **offline**, keeping both files in a private
directory outside this repository:

```powershell
openssl pkey -in "$env:USERPROFILE\YoRadioSecrets\rsa-pkcs8.pem" -traditional `
  -out "$env:USERPROFILE\YoRadioSecrets\server-key.pem"
```

This changes its container, not its mathematical identity. Re-run the packer
with its matching chain. Encrypted PKCS#8 and other profiles are rejected too;
an unencrypted provisioning file requires protected local storage and handling.
Input-container qualification does not limit the required TLS wire protocol.

Keys, bundles, CSVs and NVS images stay outside source, firmware archives,
evidence, manifests and logs. Never put them in SPIFFS `/data` or `/www`; C3
serves `/data/*` publicly. Test identities belong in ephemeral host `/tmp` and
must be removed rather than archived or reused in production. Plain NVS is
**not** an at-rest encryption claim. Encrypted NVS/flash, key rotation and
physical protection are separate supported configurations.

Clients must trust the issuing CA and verify the actual SAN hostname/IP.
Disabled certificate checks are not acceptance evidence. Independent clients
validate time/name; parsing the server's own credentials does not depend on
bootstrap SNTP.

## Hardware and resource policy

| Existing pinned profile | CYD | ESP32-C3 OLED |
| --- | --- | --- |
| SDK under repository `.idf/` | `v6.0.2` | `v6.1-9a97f6c54ec6` |
| Maintenance HTTPD stack | 6144 bytes | 8192 bytes |
| Maintenance client limit | 5 | 7 |
| lwIP descriptor limit | 10 | 10 |
| TLS server support | Compiled | Compiled |
| Protocol | TLS 1.2; TLS 1.3 off | TLS 1.2; TLS 1.3 off |
| TLS RX/TX content limits | 16384/4096 | 16384/4096 |
| Dynamic TLS buffers | Off | On |
| Secure HTTPD stack/client limit | At least 10240 /3 | At least 10240 /3 |

One listener serves assets, REST, uploads/OTA and `/ws` on one origin; no second
HTTP redirect listener. Three HTTPD internal descriptors, three clients, one
radio stream and one network operation form a planning total of 8 of 10.
DNS/SNTP/transitions must confirm remaining margin. The client cap and checked
allocation are not measured heap admission protection; a production audio
headroom threshold remains unqualified.

Do not copy C3 dynamic-buffer settings to CYD. Retain RX 16384, TX 4096 and TLS 1.2.
CYD keeps stream/core0 priority3, decoder/core1 priority5, output/core1 priority6,
pins, clocks, and DAC/PDM backend. Added stack, credential allocation (maximum
12306 bytes), per-session lookahead/context, TLS objects, parsed key/chain,
handshake temporaries and certificate-chain cost need target measurements.

## Evidence and remaining gates

Current deterministic production-code evidence:

* `.build/native-web-transport-final/report.json`: 65 credential/ownership/I/O
  groups, ASan/UBSan; four semantic mutants caught (raw plaintext bypass, lost
  TLS destructor, unchecked key pair, renewed write deadline). SDK/NVS/crypto/
  socket/allocation calls are explicitly labeled seams in this suite.
* [C3 handlers](../tests/results/native-web-transfer-20261018/ws-c3-final/report.json): 5189 C3 handler cases,
  ASan/UBSan, four historical negatives, opposite WANT directions through a
  labeled native-transport seam, graceful Close delegation.
* [CYD handlers](../tests/results/native-web-transfer-20261018/ws-cyd-final/report.json): 57 CYD handler groups,
  ASan/UBSan, unchanged RFC behavior through a labeled transport seam.
* `.build/native-web-bundle-profile-freeze/report.json`: six structural/boundary/
  container-profile/private-output groups using ephemeral `/tmp`. These do not
  qualify real certificates; the actual TLS suite covers real fixtures.

Actual [6.0.2 TLS](../tests/results/native-web-transfer-20261018/tls-cyd/report.json)
and [pinned 6.1 TLS](../tests/results/native-web-transfer-20261018/tls-c3/report.json)
each pass eight cases with 117 real pinned vendor crypto C units under ASan/UBSan.
MbedTLS versions are 4.1.0/4.1.1. Python OpenSSL verifies the ephemeral CA and
`localhost`; wrong CA, wrong hostname and unsupported TLS 1.3 are rejected.
The matrix covers peek/pending, 128 KiB exact data with backpressure and positive
partial writes, opposite WANT directions, both clean alerts, abrupt EOF and a
silent handshake deadline. Matching PKCS#1 succeeds; independently valid
matching PKCS#8 and mismatched PKCS#1 leave NVS unchanged on rejection.
Public/server ESP-TLS functions are extracted verbatim; host type/NVS/logging
and client-only branches are explicit seams. Software crypto configuration
does not qualify target acceleration, dynamic buffers, ABI, RAM or timing.

The [combined WSS gate](../tests/results/native-web-transfer-20261018/wss-integrated/report.json)
passes 14 cases and 14 real HTTPD/TLS session deletions for each pin. It joins
that production native transport and actual pinned ESP-TLS/crypto to generated
HTTPD parsing/URI/session/framing and actual application receive/control hooks.
PSA SHA-1/Base64 calculate the real Accept; OpenSSL verifies CA and hostname.
Handshake plus first frame in one write, fragments, split UTF-8, Ping/Pong,
Close echo and five ordinary/invalid upgrade cases pass. Its documented HTTP
error formatting, NVS, scheduling and radio-command seams remain explicit.

Acceptance requires evidence for each distinct layer:

1. Actual pinned ESP-TLS/mbedTLS host interoperability through production
   transport and an independent validating client: correct CA/SAN, rejected
   wrong CA/name, malformed/mismatched credentials, short I/O, WANT directions,
   pending plaintext/peek, clean alerts, abrupt EOF, failed handshake, fd reuse,
   OOM and repeated cleanup. Record public protocol/cipher, hashes and outcomes;
   no secret fixtures. Explicitly label host SDK seams and missing hardware.
2. SDK links/maps for both targets and intended variants; successful hand-off
   images under `firmware/development/<variant>/app.bin`, preserving versioned
   releases. Verify WebUI scheme/host/port follow its page origin.
3. Frame/message/handshake conformance over WS and WSS on actual targets where
   feasible (Autobahn or comparable per-requirement suite). Report configured
   limits/extensions precisely. A TLS proxy does not prove firmware transport.
4. **Physical gate, pending:** C3 and intended CYD audio backends with HTTPS
   playback plus WSS status/control, two browsers, sequential assets,
   handshake/churn, slow/invalid peers, maintenance uploads/OTA and reconnects.
   Measure internal heap minimum/largest block, DMA reserve, HTTPD/audio stack
   high water, CPU, underruns and cleanup recovery. Qualify interrupted NVS
   updates/rotation. No RAM, watchdog, at-rest or audio-safe admission result is
   inferred from host tests or total SoC SRAM.

## Inspected pinned source fingerprints

Paths relative to each SDK's `components/`; no SDK files were changed.

| Source | 6.0.2 SHA256 | Pinned 6.1 SHA256 |
| --- | --- | --- |
| `esp-tls/esp_tls.c` | `1790a0c7de2b41f1f44caceae0fbc0a0fd366e3e6570750eeb4fa0a91fe2f93f` | `5b575c188acedd581d8438e2b4125f74170237dce6da876c7b3912d0291d59f2` |
| `esp-tls/esp_tls.h` | `ce5b788664885025e509cc17fed24844b9fc4ed3a8cec8da5c87c199fd8e168d` | `c000a387e2babf2138c06ae29733dfec51cab3316638fd1333e145f2aed34a50` |
| `esp-tls/esp_tls_mbedtls.c` | `72dd83355fa64fc66e3a8636776c4b3ebbc5ec219834559a3aba33d217f730c7` | `cacc35f509cfda8779d058ff7ed6e01ce2218967443079f90281dc8718510055` |
| `esp_http_server/src/httpd_sess.c` | `96fb619e14b097e2f485db8cf3372e8768117d68cfefc5f7ee036804caf2f904` | Same |
| `esp_https_server/src/https_server.c` (unused wrapper audit) | `39975d1e6ef42136e6f3cc97f48eb48d8d053676ed4a4167f852fe8b49233a9d` | `0ef294cf3b6d00d52873fadefa9b24f5279233cfe999afd9c8ed4e9212c9fa74` |
| `mbedtls/mbedtls/tf-psa-crypto/extras/pkparse.c` | `40db1c4498f0c40903c56a3c51cf3440a0ba9f518679a1dd45b0087d4c3646d5` | Same |
| `mbedtls/mbedtls/tf-psa-crypto/extras/pk.c` | `a90d90b0d5a815e833a8d04925d121628e5f3be6b4fdd5db6466068e459cbad0` | Same |
| `mbedtls/mbedtls/tf-psa-crypto/extras/pk_rsa.c` | `3ab4e6d4e415ffc3121567eeaaae820a12c0e24d16e9973bf17b86e01922113e` | Same |
