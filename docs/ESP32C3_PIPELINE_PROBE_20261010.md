# DMA overrun diagnosis during HE-AAC TLS renegotiation

## Finding: the observed output task remains responsive while PCM runs out

The diagnostic firmware completes **17/18** checks on physical ESP32-C3.
Both 75-second cases play HE-AAC 44.1 kHz stereo and request a full TLS 1.2
renegotiation at 30 seconds. The 1 KiB case has no steady output events;
the 16 KiB case has 17 I2S completion-queue drops. All handshakes finish.

| TLS record size | Full renegotiation, ms | Steady queue drops / write errors | Min free / largest, B |
| --- | ---: | ---: | ---: |
| small | 522.1 | 0 / 0 | 31,776 / 24,576 |
| large | 413.5 | 17 / 0 | 32,192 / 24,576 |

The phase histogram captures all 17 events. At 15 of them, output is inside
PCM receive, the decoder is inside encoded-input receive, and the network
task is inside HTTP body read (phase 7). At the remaining two, output still
waits for PCM but the decoder/network have left those receive/read calls
(phase 1). Call phases alone do not establish scheduler state.

The last 16 events retain full timestamps; **one older event was overwritten**.
For those 16, output's latest queue checkpoint is only **0.058..4.735 ms** old.
It is being scheduled at the normal approximately 5 ms empty-queue polling
interval. Its latest accepted PCM packet is **53.166..213.172 ms** old.
During the retained phase-7 events, the latest encoded packet is
350.989..489.661 ms old and the latest successful HTTP read is
1,359.252..1,497.924 ms old. In the final two events, fresh input and a positive
HTTP read have returned 5..16 ms earlier, while output still awaits PCM.

For this captured stall, the evidence supports exhaustion of buffered audio
during the TLS read pause, followed by decoder refill. It does not support
raising output priority as the remedy: the output task already gets CPU time.
The counters are not an analog waveform capture or an exact audible-gap count.

## Qualification and next change

There are 159 health observations with one boot identity, zero
allocation failures, zero watchdog events and zero I2S write errors.
The SDK lifetime minimum free heap is 15,368 B.
The two runs do not make the firmware production-qualified, and do not erase
earlier quiet-image output failures or contiguous-memory headroom failures.

The baseline uses a 250..500 ms startup prefill. In
`prefill_encoded_input()`, a full input queue permits departure after only
250 ms; slower arrival can extend it to 500 ms. Large TLS records can fill
the queue in a burst. That code path is consistent with the large-record
failure despite its shorter handshake, but these probes do not directly
measure prefill duration or queued audio duration.

Next controlled experiment: require 1,000 ms minimum and maximum startup
prefill, retaining queue capacities, TLS support, decoder arithmetic and task
priorities. Measure actual startup latency and rerun both record sizes and
HE-AACv2. Do not adopt it by default solely because these cases improve:
higher bitrates, other codecs, memory headroom and recovery still need checks.
This is a buffering hypothesis to test, not a completed repair.

### Follow-up: one-second prefill

The subsequent [1000 ms campaign](ESP32C3_PREFILL1000_RENEGOTIATION_20261010.md)
passes 34/34 checks across HE-AAC and HE-AACv2 with both TLS record sizes.
All four measured playback windows have zero completion-queue drops and
write errors, with unchanged static RAM/IRAM and codec arithmetic. This is
a candidate mitigation for the measured pause; normal-trust multi-codec,
recovery and memory-headroom qualification remain open before changing defaults.

## Diagnostic implementation and audit

The optional probe uses 516 static bytes; alignment makes the linked DRAM
data-section increase 512 bytes. IRAM text grows by 132 bytes and stays within
the previous reserved aligned region. The full image is 1,457,952 bytes.
All 119 AAC/FLAC code/constant sections in 18 objects match the prior baseline.
Of 50 application objects, only audio_service, native_audio_output and
web_service change. TLS roots and the 17,058-byte RX reservation are unchanged.

With the option disabled, recompiled text/data sizes do not grow. Sections
match the quiet baseline except the verified source line and Windows path
spelling in the suspend error diagnostic. No playback code difference is
waived by that check. Host ASan/UBSan tests cover phase/history/counter wrap,
bounded JSON, and unchanged Stop/EOF ownership behavior.

An initial implementation used the CPU cycle counter. It was replaced before
the measured playback campaign because C3 stops that counter during WFI;
see [TRM mpcER/CYCLE](https://espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf#page=39).
The final implementation uses the hardware system timer through
[`esp_timer_get_time()`](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/system/esp_timer.html#obtaining-current-time).
Linked overrun, timer read, HAL counter read and conversion functions are all
in IRAM. The first controller invocation used an invalid `--name` argument,
exited before audio collection, and restored the board. Its failure and
restoration are preserved separately; they are not counted as playback tests.

The final controller restores the exact listened application ELF
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.
Wi-Fi, playlist and settings remain unchanged. Three final observations
confirm stopped playback. Diagnostic firmware is laboratory-only and contains
a test CA; it is not left on the board.

[Probe interpretation](ESP32C3_PIPELINE_DIAGNOSTICS.md).
[Frozen evidence and replay](../tests/results/esp32c3-pipeline-probe-20261010/README.md).
