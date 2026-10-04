# ESP32-C3 TCP receive credit diagnostics

`CONFIG_YORADIO_NETWORK_HEAP_PROFILE` can help distinguish queued network data
from decoder allocations. It remains optional and does not alter TCP flow
control, buffer sizes, playback or the acceptance thresholds.

The existing `PERF NET_HEAP` line counts TCP transmit lists and the **out-of-order**
receive list (`ooseq`). Its `rx_bytes` field does not include in-order payload
already delivered to a socket's receive queue. Zero `rx_bytes` therefore does
not establish that receive buffering is empty.

## Receive window snapshot

The additional `PERF NET_RX` line carries the same sequence number and age as
the associated heap snapshot. It sums these fields across active TCP PCBs:

| Field | Meaning |
| --- | --- |
| `window` | Current `rcv_wnd`, the receive credit still available |
| `maximum` | Sum of `TCP_WND_MAX(pcb)`, respecting each connection's window scaling |
| `refused` | `tot_len` of payload retained in `refused_data`, pending acceptance by the upper layer |

`maximum - window` is logical receive credit not yet returned. In the pinned
ESP-IDF 6.0.2 lwIP socket path, receiving in-order data consumes credit and
`netconn_tcp_recvd()` returns it as the socket consumer reads data. FIN also
temporarily consumes one sequence number. Refused data overlaps this credit;
the two byte counts must not be added. Neither count measures allocated RAM:
packet metadata, allocation rounding, Wi-Fi buffers, out-of-order packets and
TLS/application storage need separate accounting.

The callback reads fields on the owning TCPIP thread. It copies only scalar
counters, never exports packet pointers or contents, and does not inspect the
application mailbox or cast a callback argument to a socket structure. The HTTP
thread prints the completed snapshot later. `logged_at - age_ms / 1000` estimates
sample time; USB and host scheduling delay still affect that estimate.

Source references in the pinned SDK are `lwip/src/include/lwip/tcp.h`,
`lwip/src/core/tcp_in.c`, `lwip/src/core/tcp.c`, `lwip/src/api/api_msg.c` and
`lwip/src/api/sockets.c`. Host sanitizer tests exercise empty and active lists,
scaled windows, refused buffers, delayed logging, callback failures and unchanged
PCB contents. This diagnostic does not prove that every allocation has an owner.

## Longer load observations

The load runner accepts `--load-seconds 180 --load-idle-recovery`. It checks idle
heap before and after each case, including failed playback cases. Finite fixtures
must be long enough to cover the requested observation. The original CPU, heap,
latency and real-time playback gates remain unchanged.

`tools/esp32c3_tests/load_windows.py --input <result-directory> --output <summary.json>`
summarizes CPU, heap and optional receive credit in 30-second bins. It requires
explicit `started_at` and `ended_at` values in `status.json`, preserves each
recorded PASS/FAIL and reports malformed telemetry. It never borrows samples
from a subsequent codec to fill an interrupted observation. Older firmware's
missing `NET_RX` lines mean unavailable telemetry, not zero queued data.

Use this summary to investigate failures, not to relabel a failed acceptance
run. Preserve raw filtered logs, exact source/configuration hashes and the failed
result before repeating a test.
