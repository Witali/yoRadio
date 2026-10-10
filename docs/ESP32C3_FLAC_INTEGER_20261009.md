# ESP32-C3 integer-clock FLAC input comparison

The input-retention fix preserves settled memory here, but **extra FLAC
slots still do not qualify for production**. Input waiting falls substantially;
a repeatable improvement in DMA continuity is not established. The second
ordinary-queue control has fewer DMA events than the expanded candidate.
No production default changes.

## Controls and build checks

Three fresh boots use input capacity 4 / 8 / 4, with the same heavy 48 kHz
stereo 16-bit FLAC file over trusted HTTPS for 180 seconds each. The expanded
run also plays full-rate HE-AACv2 44.1 kHz stereo for 180 seconds after FLAC
and a settled Stop. Status is polled every 100 ms plus request time. FLAC
delivery is unpaced; continuous ADTS pacing ratio is 1.0.

Both builds use source `679facfb`, including the queue-retention correction,
ESP-IDF 6.1 revision `9a97f6c54ec638111ce55cd36581b3c192f15207`, QIO 80 MHz,
full compact AAC/SBR/PS, the 17,058-byte TLS RX reserve, adaptive input and
250/500 ms minimum/maximum prefill. They use the ordinary integer PDM clock.
Heap-owner hooks and the TCP probe are disabled; CPU, pipeline, DMA and
network-memory profiling remain enabled. Exact configs differ only in
`CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=0` versus `4`.

Linked AAC, HTTP and TLS allocator audits pass. All **128 code/constant
sections in 18 AAC/FLAC objects** match the retained-queue baseline. No codec
arithmetic changes, reduced AAC features or inactive CLZ experiment are
included. These images contain profiling and temporary laboratory trust.
The changed layout means older fractional-clock trials are not matched
clock controls for this comparison.

| Build property | Extra slots 0 | Extra slots 4 |
| --- | ---: | ---: |
| Application bytes | 1,622,192 | 1,623,184 |
| IRAM text bytes | 47,690 | 47,690 |
| Initialized DRAM bytes | 12,856 | 12,856 |
| DRAM BSS bytes | 45,664 | 45,672 |
| Encoded payload capacity after growth | 8,192 | 16,384 |
| Packet storage, excluding allocator overhead | 8,240 | 16,480 |

Every experimental boot verifies QIO/80 MHz, four matching full-image CRC
reads and the output divider. The integer divider corresponds to nominal
**48,076.923 Hz**. Register readback does not measure crystal accuracy or
analog noise. Exact-clock analog qualification remains deferred.

## Physical results

CPU and queue waits use complete windows after ten seconds of warmup. Waits
include preemption and are not CPU utilization. DMA deltas span the first
through last selected samples, about 165 seconds per measured run.

| Measurement | FLAC control before | FLAC expanded | FLAC control after | HEv2 after expanded FLAC |
| --- | ---: | ---: | ---: | ---: |
| Mean CPU busy | 79.32% | 79.85% | 79.00% | 62.09% |
| Decoder input-wait wall time | 24.99% | 0.236% | 24.16% | 0.00% |
| Output empty-PCM wait wall time | 11.92% | 0.139% | 10.86% | 1.30% |
| Measured DMA queue events | 64 | 7 | 0 | 0 |
| Whole observed DMA queue events | 64 | 7 | 1 | Rejected timestamps; see below |
| Measured DMA write errors | 0 | 0 | 0 | 0 |
| Minimum free heap, CPU samples | 57,308 B | 48,556 B | 57,128 B | 25,560 B |
| Minimum largest block, CPU samples | 36,864 B | 34,816 B | 34,816 B | 15,360 B |
| Median RSSI | -65 dBm | -67 dBm | -63 dBm | -69 dBm |
| Settled Stop heap recovery | PASS | PASS | PASS | PASS |

All four measured CPU/decoder/DMA/flow intervals pass completeness checks.
CPU has no ceiling. **Original controller entries: 20/21 PASS** (6/6 before,
9/9 expanded including AAC, 5/6 after). The last control fails the progressive
free-heap gate: first/last medians are **60,816 / 57,340 B**. After Stop, heap
returns to 133,128–133,132 B versus 133,084–133,104 B initially; largest block
stays 102,400 B and task count stays 17. This is settled recovery, not a reason
to erase the in-playback failure or assert allocation ownership without a trace.

All settled largest blocks recover within their own boots: 106,496 B for
the first control and 102,400 B for both later boots. No decoder/allocation/
TLS fault, panic or unexpected reset is recorded in the complete filtered
captures. All **4,192 host-traced TCP connections succeed**; this does not
resolve the earlier intermittent WebUI timeout.

The candidate's seven DMA events occur only between **85.797 and 90.812 s**.
An overlapping decoder window records 310 ms of input waiting and six
timeouts; output records 229 ms of empty-PCM waiting. RSSI in the counter
interval ranges from -61 to -70 dBm. These coarse observations support
investigating a delivery interruption but do not identify its cause. Host
socket-write statistics are not acknowledgements or board-arrival times.
DMA counters are not an exact count of audible gaps.

### HE-AACv2 and timestamp limitation

The HEv2 measured interval covers **165.235 s**, 15,516 writes and 31,776,768
bytes, with zero DMA event/error increments. Full-rate stereo status,
runtime, settled memory and measured flow checks pass.

The separate whole-observation DMA replay **fails**: two early records share
host timestamp `254955.906`, despite device log timestamps 224,338 and
224,341 ms. This Python's `time.monotonic()` uses `GetTickCount64()` with
15.625 ms resolution. Both records are preserved; the strict parser is not
weakened and the full interval is not reported as accepted. The separate
post-warmup interval has distinct timestamps and passes. No analog recording
or listening comparison was performed.

## Frame-size observation and next experiment

FFprobe 8.1.1 finds 6,355 frames in the 610-second fixture. Median encoded
size is **15,390 bytes**, maximum 15,522; full frames represent 96 ms.
6,354 frames exceed the ordinary 8,192-byte payload queue; none exceeds
16,384 bytes. The decoder has its own frame window, so a complete frame
need not fit in this queue. These sizes suggest scheduling/burst sensitivity
to investigate, not proof of the failure mechanism.

The repeat control's zero measured events despite approximately 24% input
waiting again shows why reduced waiting alone cannot qualify continuity.
Keep extra slots at default **0**. Next, introduce bounded, reproducible
delivery pauses with catch-up so average delivery remains sufficient;
compare ordinary/expanded capacity with the same pause schedule. Then repeat
the selected settings against the full format/network/OTA matrix. Preserve
full AAC features and verify additional FLAC allocations retire before AAC.

The [matched delivery-pause follow-up](ESP32C3_DELIVERY_PAUSES_20261009.md)
reuses these images with identical host send-buffer settings and byte-position
pauses. It measures 25/16/23 DMA events in control/expanded/control order,
with settled recovery and successful measured HE-AACv2 afterward. The extra
capacity helps in this bounded comparison but does not eliminate the events;
the default remains unchanged.

## Artifacts, restoration and replay

- [Ordinary queue image](../firmware/development/esp32c3-idf-6.1-r9a97-flac-integer0/manifest.json):
  app SHA-256 `2545f83c2d6c9796448899b256049d2aacd98c842989db93418e272048ecf5ca`.
- [Expanded queue image](../firmware/development/esp32c3-idf-6.1-r9a97-flac-integer4/manifest.json):
  app SHA-256 `28d24c6f7e1dd59ff2908f9e53d658f30eaf012a8af94ee34e3174cb5d75bc00`.

App-only OTA restores `idf61-qio80-8c1f2d2d` in app1, verifies unchanged Wi-Fi,
playlist and settings, and records three subsequent AAC 44.1 kHz stereo
playing observations. The outer controller finishing successfully confirms
restoration; it does not turn the failed phase into a passing test.

[Frozen evidence and offline replay](../tests/results/esp32c3-flac-integer-20261009/README.md)
include passing and failed gates, exact sources, build audits, packet sizes,
raw filtered observations and restoration. Private keys and user settings
are excluded.
