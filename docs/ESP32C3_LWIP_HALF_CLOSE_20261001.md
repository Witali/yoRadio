# TCP half-close ownership fix — 2026-10-01

## Finding

The RTC TCP pool exposed a defect in the pinned esp-lwIP revision
`fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e` (ESP-IDF 6.0.2). It also exists with
the SDK's ordinary heap allocator. This is independent of Flash Auto Suspend:
the physical pool failures were captured with Auto Suspend disabled.

Rejected OTA uploads send an error response, call `shutdown(fd, SHUT_WR)`,
briefly drain incoming data, and let HTTPD close the socket. This preserves
the browser's response when an upload is rejected before its body is consumed.
The socket can still own a PCB after TCP enters TIME_WAIT or LAST_ACK.

Two missing ownership transitions matter:

1. `lwip_netconn_do_close_internal()` treats read shutdown after write shutdown
   as a full close for FIN_WAIT_1, FIN_WAIT_2 and CLOSING, but omits LAST_ACK and
   TIME_WAIT. Consuming EOF can set `TF_RXCLOSED` without detaching the netconn.
   LAST_ACK completion then frees the PCB without notifying the netconn because
   `TF_RXCLOSED` is set. A later socket close accesses freed memory. This matches
   the delayed-close/free followed by socket-close path observed on the board.
2. TIME_WAIT reclamation under PCB pressure, and normal 2*MSL expiry, free the
   PCB without notifying a half-close owner which has not consumed EOF yet.
   The old socket can later access the freed or reassigned memory.

The [original hardware evidence](ESP32C3_TCP_PCB_POOL_20261001.md) remains a
rejected image. Host tests establish a matching defect in real TCP code;
they do not retroactively prove every earlier crash had this one cause.

## Correction

`tools/patch_lwip_timewait.py` generates project-local copies of `tcp.c` and
`api_msg.c` during CMake configuration. SHA-256 checks reject unaudited SDK
sources. The shared SDK checkout is never edited; original license headers
remain in the generated sources. The C3 build replaces exactly those two source
entries in the existing lwIP component, retaining its flags and dependencies.

- Recognize LAST_ACK and TIME_WAIT when read shutdown completes a prior write
  shutdown. Use the existing full-close path to detach callbacks and netconn.
- On TIME_WAIT release, notify a remaining half-close owner with `ERR_CLSD`
  after freeing the detached PCB, as the existing delayed-close path does.
  Keep queued receive data and EOF available; do not report a reset.
- Restart the TIME_WAIT timer traversal after notification because callbacks
  may change the list. Fully closed PCBs receive no extra notification.

TCP timers, capacity, retransmissions, OTA body validation and the bounded drain
are unchanged. There is no added permanent buffer, codec change, rate cap or
PCM quantization. The optional RTC pool remains a separate configuration.

## Reproducible host checks

Run under Linux/WSL with `cc`, AddressSanitizer and UndefinedBehaviorSanitizer:

```sh
python3 tests/run-lwip-half-close.py --allocator pool --output /tmp/pool-fixed.json
python3 tests/run-lwip-half-close.py --allocator heap --output /tmp/heap-fixed.json
```

Use `--lwip /path/to/esp-lwip` if the pinned SDK is not in the repository's
`.idf/v6.0.2` directory. Add `--unpatched` to reproduce the defect. That run
intentionally returns nonzero and must not count as a passing fixed test.

The harness compiles real TCP, netconn, socket and IPv4 code, creates a TCP
loopback connection with a real handshake, and sends the response and FINs.
It uses upstream's deterministic unit-test OS shim, adapting its invalid-mailbox
initializer for non-zeroed heap storage. No TCP state machine is mocked.
For LAST_ACK only, a packet wrapper delays the real final ACK until after EOF
has been consumed. Timer tests advance TCP ticks and invoke the real slow timer.

| Scenario | Original RTC pool | Original heap | Fixed RTC pool | Fixed heap |
| --- | --- | --- | --- | --- |
| TIME_WAIT reclamation after EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| Reclamation before draining data/EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| TIME_WAIT expiry after EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| Expiry before draining data/EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| LAST_ACK: EOF before final ACK | FAIL | FAIL: use-after-free | PASS | PASS |
| Ordinary full close, control | PASS | PASS | PASS | PASS |

Pool failures are detected when the old socket corrupts the new socket's PCB
ownership. Fixed cases check exact response/data, EOF, ownership of all 16
replacement PCBs, complete TCP cleanup, and sanitizer success. Retained output
and source hashes are in
[`tests/results/esp32c3-lwip-half-close-20261001`](../tests/results/esp32c3-lwip-half-close-20261001).

These host checks do not simulate FreeRTOS scheduling, Wi-Fi or Flash writes.
Physical OTA and mixed-codec qualification of the fixed firmware are pending.

References: pinned [TCP implementation](https://github.com/espressif/esp-lwip/blob/fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e/src/core/tcp.c),
[netconn implementation](https://github.com/espressif/esp-lwip/blob/fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e/src/api/api_msg.c),
and [raw TCP ownership contract](https://www.nongnu.org/lwip/2_1_x/group__tcp__raw.html).
