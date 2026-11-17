# CYD TLS reconnect and OTA during playback in QEMU

The PDM profile uses ESP-IDF 6.0.2 on dual-core ESP32, diagnostic OpenETH,
static TLS RX reservation, the five-second task watchdog and the 300 ms
interrupt watchdog. The fixture runs the application at `fcb2e90c2` with
the RX and PCM probes. The controller confirms decoded PCM output in
each of four independent TLS 1.2 sessions.

| Operation | Observed result |
| --- | --- |
| Stop then Play | Stop returned the static RX buffer. Playback restarted in a new generation and borrowed the reserve again. |
| Truncated image during playback | The upload reached image verification, returned HTTP 400 and resumed playback in the same boot and partition. |
| Same-image OTA during playback | HTTP 200, software reset, running slot `app1` and the original application ELF hash. |
| Post-update playback | The exact SPIFFS WebUI asset and a new TLS Opus stream both worked. The final Stop returned the reserve. |

The probe recorded four alternating loans and returns. Each loan came
from application BSS, and each return marker followed the SDK cleanup
call. The guest reported no watchdog fault. The controller verified
that QEMU's backing flash file retained its original digest.
[Observations and digests](observed.json)

A separate control with the same image completed the full stereo Opus
fixture with 43 full TLS body records, the final partial record,
1,058,176 accepted PDM bytes and the exact WebUI asset after EOF.

The Windows run uses a separate loopback connection for each guest TCP
connection. This gives reconnect the new TLS session it needs. The
original QEMU character-device forwarding route kept one host connection
open and the second TLS handshake received an unexpected message.
The test writes to a disposable QEMU snapshot. The physical CYD OTA
and Wi-Fi checks remain open.
[Reproduction and QEMU patch](../../target/cyd_full_app_openeth_qemu/README.md#tls-reconnect-and-ota-during-playback)
