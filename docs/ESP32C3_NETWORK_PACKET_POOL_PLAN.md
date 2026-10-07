# ESP32-C3: reserving network packet memory at startup

## Decision

A bounded, reusable receive-packet pool is worth an experiment. Its expected
benefits are predictable allocation and less fragmentation of the heap shared
with AAC. Reserving memory alone does not reduce the live payload or create RAM.
The pool must replace identified allocations, rather than sit beside the existing
packet buffers. Keep it optional until memory, throughput and playback gates pass.

This is a design analysis, not an implemented or measured packet-pool saving.

## Current implementation, 2026-10-07

The measured awake `esp32c3-station-timeout` configuration uses:

| Layer | Current storage |
| --- | --- |
| Hardware Wi-Fi RX | Six buffers, approximately 1,600 B each, allocated by `esp_wifi_init()` and held until deinit |
| Wi-Fi dynamic RX | Maximum 16 outstanding driver buffers; storage depends on frame size |
| Wi-Fi TX | Dynamic buffers, maximum 16 |
| TCP receive window | 11,520 logical payload bytes per connection; this is not a reserved memory block |
| TCP receive mailbox | Ten messages; this is not a hard byte limit for all network memory |
| TCP control blocks | Existing optional RTC pool enabled, 16 slots / 2,688 B; this stores connection state, not packet payload |
| Ordinary netif RX | `esp_pbuf_allocate()` allocates metadata and retains the Wi-Fi payload until the final `pbuf_free()` |
| Native copy experiment | `wlanif_input()` allocates `PBUF_RAM`, copies the frame, then immediately releases the driver buffer |

The pinned IDF 6.0.2 `lwipopts.h` sets both `MEM_LIBC_MALLOC=1` and
`MEMP_MEM_MALLOC=1`. `PBUF_RAM` calls `mem_malloc()`. Even changing the receive
path to `PBUF_POOL` would still use heap-backed `memp_malloc()` in this configuration;
its name alone does not establish a fixed pool.

The controlled 600-second HE-AACv2 baseline completed with no recorded runtime
faults. Sampled free heap reached 19,760 B and the largest block 5,120 B. After
Stop, idle heap returned to a median of 147,748 B and the largest block to
114,688 B, exactly matching the idle baseline. Receive credit consumption
reached 11,520 B. The original progressive-heap-loss gate remains FAIL.
This supports investigating retained packet queues; it does not assign every
heap byte to those queues or prove physical audio continuity. The completed
[matched comparison](ESP32C3_RX_MATCHED_20261007.md) raises minimum free heap to
28,256 B with native packet copies, at similar CPU load. Both original memory
gates still fail. Retained baseline: `tests/results/esp32c3-rx-matched-20261007/baseline/`.

## Recommended boundary

Prototype the pool at the receive netif copy boundary. Reuse the current
native-copy ownership sequence, but obtain the copy destination and its
`pbuf_custom` metadata from the reserved pool. Return a slot only from the
custom free callback after the last reference is released. Free the driver's
original buffer exactly once on success and all failure paths.

This isolates long-lived TCP packet storage from the main heap. It does not
remove the initial dynamic Wi-Fi allocation or reserve TLS records, HTTP
workspaces, TCP transmit data, sockets or all connection state. Patching a
global `malloc()` by allocation size would not establish correct ownership.

Use a static region or one startup allocation retained for the network lifetime.
Audit placement and the remaining largest block before AAC/SBR opens. A compact
set of fixed size classes can avoid giving a full-frame slot to every small
packet; choose counts from complete size/lifetime measurements. Validate alignment,
maximum accepted frame length, chains, reference counts and concurrent release.

For scale only, 16 slots of 1,600 payload bytes reserve **25,600 B (25 KiB)**
before metadata and alignment. This is not a proposed final size or a claimed
memory saving. The incremental cost is the reservation minus the dynamic
allocations it replaces, plus metadata and any simultaneous driver/copy storage.
Idle codec switching and TLS handshakes still need their own headroom.

## Exhaustion and acceptance

- Never wait for a slot while blocking Wi-Fi/lwIP processing. Define an explicit
  exhaustion result and count it. TCP retransmission may recover a dropped
  packet but can still cause an audio gap; exhaustion is not a passing result.
- Audio traffic must not consume all capacity needed by ACKs, ARP, DNS, WebUI
  and OTA. Audit per-connection admission/reserves before selecting a hard cap.
- An unlimited heap fallback defeats the hard bound. If a fallback is evaluated,
  bound and measure it separately and retain the failure/exhaustion counts.
- Track live/peak slots and bytes by size class, failures, allocation/free balance
  and maximum allocation latency. A flat general heap alone could merely hide
  the same queue growth inside the pool.
- Exercise refcount/chained-pbuf/error/Stop/reconnect paths with host sanitizers
  and the actual lwIP free path before flashing. Check pointers against slot
  ownership; do not reuse live buffers.
- Compare total reserved RAM, occupied pool capacity, ordinary free heap and
  largest contiguous block. Preserve full-rate AAC/SBR/PS and other codecs.
- Run ten-minute HTTP and certificate-verified HTTPS playback with WebUI load,
  codec changes and OTA. CPU remains informational; packet loss, allocation
  failures, resets and output gaps remain failures. Pool allocation speed and
  physical audio continuity need measurements, not assumptions.

## Sources

- Pinned local IDF: `components/esp_wifi/Kconfig`,
  `components/lwip/port/include/lwipopts.h`,
  `components/esp_netif/lwip/netif/wlanif.c`, `esp_pbuf_ref.c`,
  and lwIP `src/core/pbuf.c` / `memp.c`.
- [Espressif IDF 6.0.2 Wi-Fi memory and data path](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32c3/api-guides/wifi-driver/wifi-performance-and-power-save.html).
- [lwIP packet buffers and custom-buffer ownership](https://www.nongnu.org/lwip/2_1_x/group__pbuf.html).
- [Existing TCP control-block pool](ESP32C3_TCP_PCB_POOL_20261001.md).
- [Earlier native packet-copy measurements](ESP32C3_RX_COPY_20261007.md).
