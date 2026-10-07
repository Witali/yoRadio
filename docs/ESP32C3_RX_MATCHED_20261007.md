# ESP32-C3: matched ten-minute RX-copy comparison

## Outcome

Native packet copying increased the sampled minimum free heap by **8,496 B
(8.30 KiB)** and the minimum largest block by **7,680 B (7.50 KiB)** in a matched
HE-AACv2 experiment. Mean CPU changed by +0.16 percentage points. Neither run
recorded a decoder/allocation fault, watchdog or unexpected reset. Both recover
after Stop and pass the settings-preserving restoration checks.

The original progressive-heap-loss gate **fails for both images**, including
their later subwindows. Do not treat this experiment as a repaired memory gate,
proof of no packet loss, or sample-level audio continuity. The copy setting
remains experimental; it has not yet passed the full codec/HTTPS/OTA matrix.

## Controlled configuration

Both images contain the same recorded firmware sources and codec configuration,
including full-rate PC19 AAC/SBR/PS, direct DMA output, priorities 5/7/8 and the
new configurable station timeout. Deep sleep and extended RX-owner tracing are
disabled. The semantic sdkconfig difference is only
`CONFIG_LWIP_L2_TO_L3_COPY=y` and its generated deprecated alias
`CONFIG_L2_TO_L3_COPY=y`. TCP window and Wi-Fi/audio buffer counts are unchanged.

In the candidate's actual `wlanif_input` disassembly, `pbuf_alloc(PBUF_RAM)` and
`esp_netif_free_rx_buffer` replace `esp_pbuf_allocate`. The driver buffer is
released after the copy instead of remaining attached to the queued packet.
This still uses heap allocation and is **not a preallocated packet pool**.

The same HE-AACv2 44.1 kHz stereo fixture loops for 600 seconds, paced at 1.02
times its nominal rate, under WebUI status requests separated by 100 ms.
No host firmware build overlapped either playback window. Runs are sequential
on one board; RF conditions and host scheduling are not controlled. A single
pair cannot establish a precise CPU cost or a universal RAM saving.

## Measurements

CPU/decoder analysis excludes the first ten seconds. Playback heap endpoints
are medians of the first/last three valid CPU records. Minima are sampled,
not allocator low-water marks. Idle values are settled medians.

| Measurement | Ordinary RX references | Native RX copies |
| --- | ---: | ---: |
| Observed duration, s | 600.031 | 600.000 |
| Status samples | 3,190 | 3,205 |
| CPU records / decoder windows | 117 / 117 | 117 / 118 |
| Mean / peak CPU busy | 76.51% / 77.8% | 76.67% / 78.0% |
| Decode time / decoded audio time | 58.765% | 58.805% |
| Decoded audio / wall time | 1.001535 | 1.001598 |
| First / last free heap, B | 44,476 / 23,312 | 44,448 / 30,908 |
| Minimum free heap, B | 19,760 | 28,256 |
| First / last largest block, B | 32,768 / 12,800 | 24,576 / 22,528 |
| Minimum largest block, B | 5,120 | 12,800 |
| Maximum HTTP response, ms | 641 | 203 |
| Minimum RSSI, dBm | -71 | -76 |
| Idle heap before / after Stop, B | 147,748 / 147,748 | 147,720 / 147,456 |
| Idle largest block before / after, B | 114,688 / 114,688 | 114,688 / 114,688 |
| Idle task count before / after | 17 / 17 | 17 / 17 |
| Full-window memory gate | FAIL | FAIL |
| Stop recovery / runtime | PASS / PASS | PASS / PASS |

The candidate retains 264 B less idle free heap after Stop; the largest block
returns fully. This passes the existing recovery gate, but should not be described
as an exact byte-for-byte return of every allocation.

## TCP data and heap movement

NET_HEAP/NET_RX sampling passes its coverage checks in both full load windows.
Unlike RX-owner tracing, these records are available in both ordinary images.
The summary now has an explicit `--independent-network` mode to inspect them
even without the optional owner hooks. Historical archive replay is unchanged.

| Median in the indicated minute | Ordinary RX references | Native RX copies |
| --- | ---: | ---: |
| First-minute free heap, B | 44,476 | 44,448 |
| Last-minute free heap, B | 26,820 | 31,390 |
| First-minute uncredited TCP payload, B | 0 | 0 |
| Last-minute uncredited TCP payload, B | 9,473 | 10,192.5 |
| Maximum uncredited TCP payload, B | 11,520 | 11,520 |

The last-minute candidate retains more logical TCP payload while using less
heap in the sampled medians. That supports the expected storage-efficiency
benefit of copying shorter frames. Receive credit is aggregated across active
connections and is not the allocated byte count of each buffer. Snapshots are
asynchronous; do not subtract the two as an exact allocator accounting.

There is no complete per-packet ownership/size trace in either image. Next,
measure live and peak packet counts by size before choosing the reservation and
size classes in the [startup packet-pool plan](ESP32C3_NETWORK_PACKET_POOL_PLAN.md).
The pool must replace allocations and expose occupancy/exhaustion counters;
otherwise a flat heap can merely hide the same queue growth inside a reservation.
Continue full-rate AAC HTTPS and other-codec tests and obtain output-continuity
evidence before changing production defaults.

## Images, restoration and retained evidence

| Development artifact | ELF SHA-256 | App size |
| --- | --- | ---: |
| `esp32c3-station-timeout` | `0117c66082ecfba3cc6a17f2cfe93aa91ba09a3eabf43d929ccda3beaa67dc65` | 1,581,552 B |
| `esp32c3-station-timeout-rx-copy` | `6d31f9bbe4fea05fef594b2f3039fbca5ee58c587fb3c9a0a959fab036a5ed98` | 1,581,392 B |

Both have IRAM 43,354 B, DRAM data 12,620 B and BSS 29,464 B. The 160-byte
application reduction is Flash storage, not saved static RAM.

OTA installation and restoration while a controlled AAC stream plays both
pass. Independent serial-health replay finds no panic/capture failures. The
board is restored to the ordinary `esp32c3-station-timeout` image, playing its
saved AAC PCM 44.1 kHz stereo station, timeout 10 seconds, deep sleep disabled.
Wi-Fi, playlist and settings comparisons pass; their values stay in RAM only.

[Retained archive](../tests/results/esp32c3-rx-matched-20261007/manifest.json)
includes both failed load reports, raw filtered telemetry, configuration/source
hashes, SDK receive-path source, linked disassembly, OTA records and final board
state. Five tests validate the archive, reproduce summaries, reject mismatched
images/configuration/duration and check restoration. These are evidence tests,
not a replacement physical run.

```text
python tools/esp32c3_tests/stream_memory_study.py --board http://BOARD_IP --host PC_IP --serial-port COM_PORT --firmware firmware/development/VARIANT/app.bin --seconds 600 --output NEW_DIRECTORY
python tools/esp32c3_tests/summarize_stream_memory.py NEW_DIRECTORY --independent-network --output SUMMARY.json
python tests/test-rx-comparison-evidence.py
```
