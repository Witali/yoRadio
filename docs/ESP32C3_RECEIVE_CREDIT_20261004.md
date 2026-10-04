# ESP32-C3 receive buffering and post-playback fragmentation

## Result and scope

Two 180-second-per-codec runs on the user's awake ESP32-C3 maintained playback
of MP3 320 kbit/s, Vorbis q10 and Opus 510 kbit/s at 48 kHz stereo. The six
playback windows contain 5,845 successful status responses with audio active.
They **do not pass the existing load acceptance gates**: free heap falls while
receive buffers fill, and one baseline Vorbis CPU log record is incomplete.

New TCP telemetry shows that the falling free heap coincides with increasing
receive credit consumption. This supports receive buffering as a substantial
cause of the initial decline. It does not assign every allocation to TCP or
exclude every leak. A separate, important failure remains: after Vorbis in the
second run, the largest idle free block falls from 114,688 to 59,392 bytes.

## Firmware and measurement

The baseline is the [PC19 network image](ESP32C3_AAC_PC19_NETWORK_20261004.md).
The receive-credit image changes only the optional network sampler in the
firmware; codec arithmetic, memory layouts, network limits and configuration
are unchanged. Application-only OTA passed during AAC-LC playback, with image
identity and unchanged settings, Wi-Fi configuration and playlist verified.

The new image is retained under
`firmware/development/esp32c3-aac-pc19-netrx/`. Its application SHA-256 is
`d77fa6d328ae8f73fa3df67cf53f61272cbb373504c36820e08bd144ea665e8d` and its ELF
SHA-256 is `6f99c0ec4c6201190e494735fe7bea64c23fcec919011229e7e231aef1f1705e`.
Executable sources match `ded89b55`; the embedded version retains
`e3b13fad-dirty` because compilation preceded the commit.

| Compiled item | Baseline | Receive-credit image | Change |
| --- | ---: | ---: | ---: |
| Static DRAM data | 12,620 B | 12,620 B | 0 |
| Static DRAM BSS | 31,480 B | 31,480 B | 0 |
| IRAM text | 43,354 B | 43,354 B | 0 |
| Snapshot symbol | 72 B | 80 B | +8 B, absorbed by section alignment |
| Flash text | 1,118,868 B | 1,119,036 B | +168 B |
| Application image | 1,567,760 B | 1,568,016 B | +256 B |

Both runs use identical deterministic 200-second files and the server's default
pacing of 1.02 times average encoded bitrate, with a 0.1-second delay between
WebUI status requests. The new load runner records explicit observation bounds
and checks idle heap before and after each case, including failed playback.
The [counter documentation](ESP32C3_NETWORK_RECEIVE_CREDIT.md) explains what is
and is not counted. Existing CPU/heap/latency thresholds were not weakened.

## Queue growth during the second run

Values are medians of samples in each interval. Receive credit is logical data
not yet credited by the consumer, **not allocated RAM**. Each value is derived
from matching TCP snapshots, adjusted for delayed logging.

| Codec | Free heap, 0–30 s | Free heap, 30–60 s | Free heap, 150–180 s | Uncredited data, 0–30 s | Uncredited data, 150–180 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| MP3 | 95,722 B | 81,604 B | 78,112 B | 0 B | 11,520 B |
| Vorbis | 82,388 B | 66,510 B | 67,358 B | 0 B | 10,496 B |
| Opus | 88,152 B | 79,328 B | 79,274 B | 2,560 B | 9,472 B |

The sampled out-of-order queue remains empty. That older `rx_bytes` counter
alone would miss the queued in-order data. MP3 also briefly retains up to
1,280 logical bytes in `refused_data`; these overlap receive credit and must
not be added to it. The stream task stops reading the socket when its encoded
audio ring is full, so TCP backpressure is expected here.

Diagnostic CPU results below exclude the first ten seconds. These are measured
values from failed load runs, not a replacement PASS decision or a controlled
CPU-overhead comparison between firmware images.

| Codec | Mean / peak CPU | Minimum free heap / largest block | Maximum status latency |
| --- | ---: | ---: | ---: |
| MP3 | 59.84 / 62.4% | 78,060 / 61,440 B | 125 ms |
| Vorbis | 72.13 / 75.8% | 64,732 / 53,248 B | 188 ms |
| Opus | 79.64 / 83.3% | 75,744 / 59,392 B | 532 ms |

## Recovery failure retained

The original run returns to exactly 146,124 B free heap, a 114,688 B largest
block and 17 tasks after each codec. In the receive-credit run, the Vorbis idle
check instead records 145,876–145,880 B free heap and a 59,392 B largest block.
The previous baseline was 145,964 / 114,688 B. The unchanged task count and
almost unchanged total free heap do not resolve the fragmentation concern.

The smaller block persists through the next idle baseline and after the
subsequent Opus run. Opus recovery passes relative to its already-fragmented
baseline; that does **not** erase the earlier Vorbis failure. The owner of the
small allocation(s) splitting the free region has not been identified.

One baseline Vorbis line ends with `heap=` and is joined to a later decoder
line. The CPU gate correctly rejects it. The pinned SDK's USB Serial/JTAG VFS
has a 50 ms transmit timeout and can drop output when the host does not drain
it; this is a possible cause, not proof of the cause of this particular record.
The corresponding second-run telemetry is complete. Preserve both runs.

## HE-AAC HTTPS from the fragmented state

Without a preliminary reboot, Groove Salad HE-AAC ran for 180 seconds at full
44.1 kHz stereo with certificate verification enabled. Startup was followed by
continuous playback; 933 of 947 status samples report audio active, with the
initial samples covering connection/startup. Mean CPU was 64.86%, peak 65.6%,
minimum free heap 18,056 B and minimum largest block 4,608 B. Maximum status
latency was 297 ms. No allocation/decoder failure or unexpected reset was
recorded during playback.

The load gate still reports **FAIL: progressive heap loss**. Receive credit
consumption rises from zero to as much as 11,520 bytes; this provides another
buffering observation, not permission to discard the failure. Idle free heap
returns from 145,892 to 145,860 B, while the largest block remains 59,392 B.
The restore step then deliberately reboots and verifies the original stopped
state, Wi-Fi configuration, playlist and settings.

This case shows that the observed fragmentation did not prevent this particular
AAC/TLS combination from running. The 4,608-byte contiguous margin remains
small, and broader stream/OTA concurrency is not qualified by this run.

## Evidence and next checks

### Ordinary HTTP download control

After the HTTPS runner's normal restore reboot, the same image and exact same
files were tested with `--unpaced-files --load-seconds 60 --load-idle-recovery`.
Only the producer pacing changes: the host sends as TCP permits, so receive
buffers fill near startup. All ten checks pass, including the three load cases,
their idle baselines/recoveries and final stopped-state restoration.

| Codec | Mean / peak CPU | Minimum free heap / largest block | Maximum status latency |
| --- | ---: | ---: | ---: |
| MP3 | 58.9 / 60.3% | 78,080 / 65,536 B | 672 ms |
| Vorbis | 71.5 / 72.3% | 66,592 / 53,248 B | 343 ms |
| Opus | 79.3 / 79.8% | 75,576 / 61,440 B | 218 ms |

All 958 status responses show playback active. The sampled TCP receive credit
consumption is already at least 7,424 B for MP3 and 9,472 B for Vorbis/Opus;
it reaches 11,520 B. Every post-stop largest block is 114,688 B, with 17 tasks.
The audio-time/wall-time ratios are 1.0016–1.0018.

These results strengthen the queue-filling explanation without weakening the
original gates. They do not replace the longer paced runs or reproduce the
fragmentation failure. Duration and boot state differ, and the new control must
be extended before drawing a long-term stability conclusion.

### Retained records

Saved records are under `tests/results/esp32c3-receive-credit-20261004/`, including
the original failed gates, configuration, byte hashes, exact runner snapshots,
build sizes and sanitizer results. `tests/test-esp32c3-receive-credit-evidence.py`
recomputes summaries and recovery decisions; it does not rerun the board.

Next, identify the retained allocation splitting the large free region, extend
the unpaced control and repeated HTTPS/OTA tests, and distinguish queue-filling
failures from ongoing heap growth in the acceptance method. Keep production
promotion open until the fragmentation concern and remaining codec/OTA gates
are resolved. Existing failed runs remain part of the evidence.
