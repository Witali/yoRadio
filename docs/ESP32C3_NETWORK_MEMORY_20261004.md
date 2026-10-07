# ESP32-C3: relocated Wi-Fi and network heap measurements

## Signal after moving the board

At 10:38:26–10:38:55 UTC, 30 read-only status requests all succeeded. RSSI was
−78 to −59 dBm, median −75 dBm. Response time was median 128.4 ms,
p95 185.3 ms and maximum 208.5 ms. Timing was measured **after** each response.
The radio was then stopped with `connection failed`, so these initial readings
established WebUI reachability, not successful audio playback.

The preceding 300-second HE-AAC 32 kbit/s HTTP baseline still has its original
FAIL for `Progressive heap loss during continuous playback`. Idle recovery
passed, but saved-station restoration failed. No allocation/decoder/panic
fault was captured during playback. That earlier result is retained separately;
later successful runs do not replace it or establish the cause of its failure.

## Diagnostic image and installation

### Later signal and playback recheck

At 11:10:33–11:11:02 UTC, another 30 read-only requests all succeeded: RSSI
−72 / −70 / −58 dBm (minimum / median / maximum), last reading −59 dBm.
HTTP latency was median 125 ms, p95 203 ms and maximum 407 ms. The saved
station was stopped with `stream read failed`; reachability alone did not
establish successful playback or the cause of that earlier failure.

A subsequent 60-second local HE-AACv2 stream passed at 44.1 kHz stereo:
54 status responses, maximum 296 ms, RSSI −73 / −71 / −58 dBm. Mean CPU
was 66.289%, peak 67.3%; minimum free heap was 43,164 B and the largest
block was 32,768 B. The original CPU, real-time progress and heap gates
passed. After the runner's restore reboot, the saved station was observed
playing AAC-LC at 44.1 kHz stereo, RSSI −59 dBm. No firmware was flashed.

This supports continuing tests in the current location, not a claim that all
station/network failures are fixed. The [recheck records](../tests/results/esp32c3-wifi-recheck-20261004/)
are separate from the earlier five-minute runs.

### Image details

The [network sampler](ESP32C3_NETWORK_MEMORY.md) was added to the existing
asymmetric-owner image. Its only configuration change is
`CONFIG_YORADIO_NETWORK_HEAP_PROFILE=y`; the AAC native patch/layout audit is
identical. It retains full-rate AAC, the 16 KiB decoder stack, awake operation,
DIO 80 MHz and disabled Flash Auto Suspend. The option remains off by default.

The image adds 96 B of static DRAM, 1,308 B of flash code and 352 B of flash
read-only data; IRAM is unchanged. The complete app grows by 1,664 B. In
addition, one lwIP callback message is allocated at runtime until reboot.
No new task/stack is allocated. This is diagnostic overhead, not RAM savings.

The saved [development image](../firmware/development/esp32c3-aac-network-memory/manifest.json)
has app SHA-256 `023940e8c653cdc79a24fe93421eb2d1dadb08591751af9ccbbb395314fd330d`
and ELF SHA-256 `7a704681d09c8c59d1cfb1bab70aee372c6a891e0e7af7fd834ab401dff3cd6a`.
OTA during controlled AAC-LC playback passed in 21.500 s, app1 → app0.
The running hash, settings, Wi-Fi configuration and playlist were verified.

The first build failed because the new header did not include `sdkconfig.h`.
That compile-only failure is retained; it was corrected before the successful
build and no failed image was installed. The actual C callback passed GCC
AddressSanitizer/UndefinedBehaviorSanitizer tests; the disabled header also
linked without lwIP/FreeRTOS. Parser and existing acceptance/window tests passed
(30 host tests total before the evidence-specific tests).

## Five-minute playback tests

Both runs use the same diagnostic image and the original thresholds. The
runner waits 0.1 s between status requests, verifies the stream with FFprobe,
and requires full 44.1 kHz stereo PCM rather than AAC-core fallback. CPU and
minimum-heap figures below come from the existing acceptance window after
15 seconds of warm-up, not from the delayed network snapshots.

| Stream | Playback result | Status responses | RSSI min / median / max | HTTP median / p95 / max | Mean / peak CPU | Minimum free heap / largest block |
| --- | --- | ---: | --- | --- | --- | --- |
| HE-AAC 32 kbit/s HTTP | PASS | 1,614 | −78 / −62 / −59 dBm | 78 / 109 / 328 ms | 59.386 / 60.5% | 23,740 / 9,216 B |
| HE-AAC 64 kbit/s HTTPS | PASS | 1,575 | −79 / −73 / −58 dBm | 79 / 125 / 391 ms | 64.020 / 65.1% | 16,828 / 4,864 B |

The HTTP run also passed baseline, idle recovery and saved-state restoration.
Idle free heap was 145,944 B before, and 145,980 / 145,968 B after; the largest
block remained 114,688 B and the task count remained 17.

HTTPS baseline, idle recovery and saved-station restoration also passed.
The settled baseline free heap was 146,080 / 146,048 / 146,048 B, and recovery
was 146,076 / 146,092 / 146,092 B, with the same 114,688 B largest block and
17 tasks. Neither playback window captured an allocation, decoder, TLS or
panic fault. There were no unexpected resets; restoration deliberately reboots.
Minimum sampled stack margins in both runs were 2,892 B for HTTP, 2,640 B for
TCPIP and 4,036 B for the audio decoder. These are high-water measurements,
not permission to reduce any of the existing stack sizes.
The small 4,864 B minimum largest block leaves limited contiguous-memory
headroom even though it exceeds the unchanged 4,096 B gate.

Together these runs provide 3,189 successful status responses and full-rate
playback in both transports. They support using the new board placement for
further qualification. At 10:54:09 UTC the saved station was playing again,
with RSSI −61 dBm and a 109.8 ms status response. The diagnostic image remains
installed in app0; settings and the playlist are unchanged.

## What the TCP snapshots show

The HTTP run contains 60 snapshots, with no missing sequence or callback
warning. Their age is 4,981–5,382 ms and is subtracted before assigning windows.
Startup samples include the period before decoder allocations; do not interpret
their high free-heap values as steady playback memory.

For HTTP samples at least 15 seconds after the recorded playback start:

- Active TCP control blocks: 2–3; TIME_WAIT: 0–6, falling to zero.
- Bound: zero; listening: one. The configured 16-PCB limit was not reached.
- Queued transmit payload: 0–467 B; sampled out-of-order receive payload: zero.
- Allocated heap blocks: 482–494; free blocks: 11–19.
- Free heap: 21,992–32,648 B, median 27,348 B; largest block: 9,216–22,528 B.
- Snapshot callback elapsed time: 121–179 µs, median 124 µs.

HTTPS contains 59 snapshots, also with complete sequence coverage and no
callback warnings. Ages are 4,999–5,347 ms. Its steady-window samples show:

- Active TCP control blocks: two; TIME_WAIT: 0–6; bound: zero; listening: one.
- Sampled queued transmit and out-of-order receive payload: zero.
- Allocated blocks: 488–503; free blocks: 15–22.
- Free heap: 16,828–29,240 B, median 22,200 B; largest block: 4,864–15,360 B.
- Callback elapsed time: 122–273 µs, median 128 µs.

These samples do not show growing TCP lists or out-of-order receive queues.
They do not measure Wi-Fi/TLS/application receive buffers, and five-second
sampling can miss short-lived allocations. Different heap minima in CPU and
network logs are expected because they are sampled at different times.

The next allocation-level investigation should focus on the remaining buffer
owners and their sizes/lifetimes. Do not attribute heap changes to RSSI or
relax the existing first/last median trend gates from these samples alone.
These bounded repeats do not establish unlimited-duration playback or qualify
the experimental AAC memory options as production defaults.

## Retained evidence

[Evidence](../tests/results/esp32c3-network-memory-20261004/) includes the failed
baseline, initial RSSI measurements, OTA, raw status/performance records,
age-corrected summaries, build overhead, patch audit, host logs, source snapshots
and checksums. Private settings are compared in memory and are not recorded.

```text
python tests/test-esp32c3-network-memory.py
python tests/test-network-heap-native.py
python tests/test-network-memory-evidence.py
```

Passing evidence tests means the records and calculations are consistent;
it never changes a recorded failed hardware test into a pass.

## Signal recheck after the user's placement change

At 11:46:41–11:47:26 UTC on 2026-10-04, a read-only status poll returned
45 of 45 responses without a transport error. RSSI ranged from **−72 to
−58 dBm**, with a **−71 dBm median** and final reading. HTTP response times
were 78 ms median, 94 ms p95 and 110 ms maximum. All 45 responses reported
active AAC PCM at 44.1 kHz stereo, 16-bit, without core-channel fallback.

This placement is sufficient to continue qualification based on the observed
connectivity and playback status. The 45-second poll does not establish
long-duration stability or measure audible dropouts. Firmware, playback and
settings were not changed for this check.

The sanitized samples and calculated summary are saved in
[signal-114641-utc.json](../tests/results/esp32c3-wifi-recheck-20261004/signal-114641-utc.json).

### Follow-up at 12:25 UTC

A new read-only poll at 12:25:06-12:26:06 UTC on 2026-10-04 returned **60/60
responses**, with no transport failures. RSSI ranged from **-69 to -58 dBm**,
with a **-63.5 dBm median** and a final reading of -69 dBm. The median was
7.5 dB stronger than the 11:46 UTC measurement. HTTP response times were
79 ms median, 110 ms p95 and 219 ms maximum. All 60 samples reported active
44.1 kHz stereo, 16-bit AAC PCM playback.

The measured connectivity is sufficient to continue board tests at this
placement. This one-minute status check does not measure audible dropouts
or prove sustained playback stability. No firmware, playback or settings
changes were made. Sanitized samples and the summary are in
[signal-122506-utc.json](../tests/results/esp32c3-wifi-recheck-20261004/signal-122506-utc.json).
