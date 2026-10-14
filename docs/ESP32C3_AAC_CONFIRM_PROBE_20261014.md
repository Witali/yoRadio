# Continuous-confirmation AAC HTTPS diagnostic

## Result

The diagnostic image passes **7/7 checks** during a requested 600-second
observation of the public Groove Salad 128-kbit AAC-LC HTTPS stream. No steady
DMA completion-queue drops or write errors occur. This does **not** explain or
resolve the earlier 27-drop failure on the quiet candidate, nor the separate
FLAC/WebUI TCP-connect timeout. There was no reproduced event to attribute.

## Exact image and instrumentation

- Source: `8984bd2a0d38446571cae541ea0479867fa6e216`.
- Version: `idf61-cprobe-20261014`.
- App SHA-256: `eb2b6de173a07767a27f86b73309cef32669eae97f7b8fb4c2303a0ad929daad`.
- ELF SHA-256: `8fb26843ec3f001e7d257dd1cdb0aced27574258637acbbf51dd73730132a1bf`.
- ESP-IDF 6.1 revision `9a97f6c54ec638111ce55cd36581b3c192f15207`,
  QIO 80 MHz, public CA bundle, nominal exact 48-kHz output, deep sleep off.

Normalized sdkconfig comparison against `idf61-confirm-20261014` finds exactly
one change: `CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC=y`. The existing bounded
recorder stores ISR call phases and checkpoint ages without console logging,
an additional task, or a DSP change. AAC library bytes remain unchanged.

The recorder occupies 540 static bytes; linked DRAM data grows by 544 bytes
including alignment. IRAM text grows by 132 bytes to 46,476; the reserved IRAM
region remains 46,592 bytes because padding shrinks. The callback and system
timer aliases are in IRAM. AAC layout, HTTP-buffer release and adaptive-input
allocator link audits pass. The recorder changes interrupt work and memory
layout, so this is **diagnostic evidence, not quiet production qualification**.

[Build recipes, symbol/config audits and source snapshots](../tests/results/esp32c3-confirm-probe-20261014/build/)
and [firmware artifacts](../firmware/development/esp32c3-idf61-confirm-probe/)
are retained with hashes.

## Physical observation

| Measurement | Result |
| --- | --- |
| Decoded format, independently checked with FFprobe/FAAD | AAC-LC, 44.1 kHz stereo |
| Last playback observation | 599.625 s |
| First matching decoded-format status | 3.239 s |
| Post-warmup output-counter window | 1,147 samples spanning 584.577 s |
| New completion-queue drops / write errors | 0 / 0 |
| All retained health samples | 1,199, one boot |
| Recorded allocation / decoder / watchdog faults | 0 / 0 / 0 |
| Minimum sampled free heap / largest free block | 57,860 / 32,768 B |
| Settled free-heap median before / after | 138,924 / 138,928 B |
| Settled largest block before / after | 110,592 / 110,592 B |
| Longest combined status/health observation | 275.320 ms |
| Failed traced requests | 0 |
| Playback RSSI range / median | -77 to -55 / -70.5 dBm |

No new phase events were recorded or overwritten in the steady window.
The recorder's empty event set therefore supplies no starvation or scheduling
attribution. Call-phase flags would not, by themselves, establish scheduler
state even if an event had occurred. Status and counter checks do not establish
sample accuracy or acoustic continuity.

The earlier quiet-candidate drop interval (40.7–41.8 s) reports RSSI -72 dBm,
within this passing observation's range. RSSI alone cannot explain the earlier
failure; it is not a measurement of delivery gaps or retransmissions.

The controller installed the diagnostic app through OTA, then restored
`idf61-prod-20261013` on app1 and verified its ELF identity. Playback is stopped;
Wi-Fi, playlist and settings compare unchanged. Private settings stayed in
controller memory; the archive retains only equality results.

[Raw report, independent replay, phase analysis and restoration evidence](../tests/results/esp32c3-confirm-probe-20261014/physical/)
preserve the actual observed interval and source hashes.

## Remaining work

1. Repeat sustained AAC-LC HTTPS on the unchanged quiet candidate, to separate
   diagnostic-image evidence from production timing evidence.
2. Use controlled TLS delivery and the bounded recorder to reproduce the
   intermittent output fault. Preserve input/PCM/output age evidence before
   deciding whether to change buffering or scheduling.
3. Investigate the independent TCP-connect timeout and finish exact-image
   sustained heavy-codec, recovery and OTA acceptance before enabling defaults.

The previous failed observations remain failures. This passing repeat changes
neither production defaults nor their qualification status.
