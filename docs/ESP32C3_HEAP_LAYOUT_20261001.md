# ESP32-C3 AAC heap fragmentation — 2026-10-01

## Finding

A **168-byte TCP control block** can split the large SRAM heap region and prevent
the native HE-AAC decoder from allocating its 55128-byte SBR owner. The total free
memory is sufficient; its layout is not. A TCP allocation/free trace identifies
the divider as a PCB released in **TIME_WAIT (state 10)**. Structure size alone
was not used to establish ownership.

This investigation follows the [conservative IRAM trial](ESP32C3_CONSERVATIVE_IRAM_20261001.md).
Both diagnostic builds reproduce its first-cycle HE/v2 failures. Neither build
changes the codec, allocation order, TCP timers or production defaults. Diagnostic
logging changes scheduling; these images are not performance benchmarks.

## Captured layout

The first diagnostic build records selected block metadata at AAC checkpoints.
For the initial failed HE start, in the heap starting at `0x3fcc0000`:

| Address | Contents | Raw bytes |
|---|---|---:|
| `0x3fcc036c` | Caller PCM buffer | 8192 |
| `0x3fcc2370` | Free | 21448 |
| `0x3fcc773c` | Allocated divider | 168 |
| `0x3fcc77e8` | Free | 85796 |

The core's 35460-byte request occupies a 36864-byte block in the upper free area.
The 12288-byte scratch allocation fits in the lower free area. After open, the
largest raw free block is 48928 bytes; TLSF reports a maximum allocation of 47104.
SBR's 55128-byte request fails even with more than 75 KiB free in total.

Later the divider disappears and the lower free region coalesces to 107420 bytes.
Core and scratch then leave a raw block of 58260 bytes (reported maximum 57344),
large enough for the unchanged SBR owner. Thus simply assuming that the scratch
buffer always takes the largest free region would misdiagnose this failure.

## Ownership confirmation

The second build also wraps the SDK's `memp_malloc` / `memp_free`, forwarding them
unchanged and recording only TCP PCB addresses and state at release. Its relevant
complete snapshot contains:

| Address | Contents | Raw bytes |
|---|---|---:|
| `0x3fcc036c` | Free | 27140 |
| `0x3fcc6d74` | Allocated divider | 168 |
| `0x3fcc6e20` | Free | 88300 |

The next recorded TCP event at the divider address is
`PERF TCP_FREE address=0x3fcc6d74 state=10`. No intervening TCP allocation at this
address appears in the trace. The matching ELF's DWARF reports `tcp_pcb` as 168
bytes. IDF 6.0.2's `lwip/tcpbase.h` defines `TIME_WAIT = 10`.

The retained analysis explicitly separates this lifetime evidence from size
equality. It does not claim that every small divider is a TCP PCB.

## Physical results and capture limits

Three cycles use MP3 → FLAC → Vorbis → Opus → AAC-LC 48 kHz stereo → HE-AAC
48 kHz stereo → HE-AAC v2 44.1 kHz stereo. Each build passes **19/21** switches;
cycle 0 HE and v2 fail the full-rate/channel check. Later success does not erase
those failures. Reboot and image-fingerprint checks pass for both; the heap-only
run also passes the WebSocket format/reconnect suite. The switching runner does
not compare a full settings snapshot; the install OTA reports retain that check.

| Build | Snapshot headers | Complete selections | Incomplete | TCP events |
|---|---:|---:|---:|---:|
| Heap metadata | 40 | 39 | 1 | 0 |
| Heap + TCP lifetime trace | 36 | 35 | 1 | 946 |

`dropped=0` is necessary but not sufficient: received row count must equal the
declared selection count. One snapshot per run lost serial rows (49/54 and 5/60).
The analyzer retains and flags them, excluding them from largest-block/divider
calculations. Raw logs remain authoritative. Snapshots cover selected neighbors,
not every small allocation; different heaps are walked sequentially.

Both images have the same static layout as the control: 43520 bytes reserved
IRAM, 12620 bytes DRAM data, 31368 bytes DRAM BSS. The bounded metadata table uses
the existing AAC task stack. Typical walks take about 0.3 ms; logging adds much
more time and can alter network timing. Do not infer a decoder speed result.

## Reproduction and artifacts

Add `sdkconfig.heap-layout.defaults` to the awake conservative Wi-Fi16 HTTP
profiler defaults. Add `sdkconfig.tcp-allocation.defaults` for the lifetime trace.
Saved applications, exact configs and source fingerprints:

- [Heap image](../firmware/development/esp32c3-heap-layout/manifest.json).
- [Heap + TCP image](../firmware/development/esp32c3-heap-tcp/manifest.json).
- [Raw evidence and analyzer](../tests/results/esp32c3-heap-layout-20261001/).

Older CMake/Kconfig bytes are preserved as source snapshots where later changes
modified those files. Reproduce the physical sequence with:

```powershell
python tools/esp32c3_tests/diagnostic.py run --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 --suite switch --suite websocket --cycles 3 `
  --case mp3-320 --case flac-level8 --case vorbis-q10 --case opus-510 `
  --case lc-48000-stereo --case he-48000-stereo --case hev2-44100-stereo `
  --sdkconfig firmware/development/esp32c3-heap-layout/sdkconfig --output OUTPUT
python tests/results/esp32c3-heap-layout-20261001/analyze.py `
  --input OUTPUT/performance.json --output OUTPUT/topology.json
python tests/test-esp32c3-heap-layout.py
```

The TCP run used `esp32c3-heap-tcp/sdkconfig` and omitted the WebSocket suite.
The optional RTC TCP PCB pool is a separate candidate addressing this layout
problem. Its physical playback, OTA and RTC-footprint qualification must be
assessed separately; the diagnostic evidence alone does not qualify a fix.
