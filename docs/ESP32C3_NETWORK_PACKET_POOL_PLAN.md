# ESP32-C3: reserving network packet memory at startup

## Decision

A bounded, reusable receive-packet pool is worth an experiment. Its expected
benefits are predictable allocation and less fragmentation of the heap shared
with AAC. Reserving memory alone does not reduce the live payload or create RAM.
The pool must replace identified allocations, rather than sit beside the existing
packet buffers. Keep it optional until memory, throughput and playback gates pass.

This is a design analysis, not an implemented or measured packet-pool saving.

The subsequent [physical sizing run](ESP32C3_RX_COPY_PROFILE_20261007.md) observed
16 simultaneous copied packets and 17,664 B peak allocation capacity, with all
23,941 allocations released after Stop. No ownership/allocation failures were
recorded. Receive queues still grew during playback and the original progressive
heap gate remains FAIL. A 16-slot pool would leave no headroom; production sizing
still needs HTTPS, reconnect, other codec and OTA workload coverage.

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

## Optional sizing profiler

`CONFIG_YORADIO_RX_COPY_PROFILE=y` requires native
`CONFIG_LWIP_L2_TO_L3_COPY=y` and is off by default. It leaves the actual
`PBUF_RAM` allocation and input path intact while tracking up to 64 copies until
the final `mem_free()`. Refcount decrements that retain the packet do not release
its tracking entry. Source hashes pin the audited IDF 6.0.2 ownership path.

Every five seconds, one CRC-protected `PERF RX_COPY:` row reports cumulative
allocations/releases, live and peak allocation bytes, failure/overflow counts,
and five size classes: 0–128, 129–512, 513–1152, 1153–1600 and 1601–65535 bytes
of received frame. No packet contents or addresses are logged. Bytes include
the pbuf and allocation alignment but exclude allocator block headers. Peaks
are since boot; class peaks need not occur at the same time. This accounts for
buffer ownership lifetimes, not a histogram of retention time in milliseconds.

The first target build adds 888 B of static RAM (768 B owner slots, 112 B counters,
8 B report timestamp). Its per-free table search and logging affect timing;
use it for sizing, not a production CPU benchmark. This is instrumentation,
not the proposed fixed packet pool.

Host tests compile the real SDK `pbuf.c` and `mem.c` with the unchanged profiler,
ASan/UBSan and platform stubs. They exercise frame/class boundaries, references,
chains, trim, input rejection, allocation failure, unrelated frees, concurrency,
duplicate tracking and overflow. The ELF verifier checks both STA/AP callback
tables and the final-free hook. The parser rejects damaged CRCs, lost owners,
counter inconsistencies and sequence gaps; packet allocation/input failures make
the result invalid for pool sizing. Window coverage is checked separately.

```text
python tools/codec_benchmark/run_rx_copy_profile_host.py --idf <IDF-6.0.2> --output <new-host-result>
python tests/test-rx-copy-profile.py
python tools/esp32c3_tests/rx_copy_profile.py <study>/performance.json --status <study>/status.json --output <new-summary.json>
```

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
