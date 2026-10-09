# ESP32-C3 PCM-tail hardware qualification — 2026-10-09

## Purpose and configuration

This experiment checks the [staged-output repair](ESP32C3_PCM_TAIL_AUDIT_20261009.md)
on the physical ESP32-C3 OLED board. It verifies that very short files submit
their last PCM samples and leave the playing state at EOF, then exercises
continuous playback, codec changes and transport faults.

The candidate uses the same active configuration as the preceding
[input-prefill experiment](ESP32C3_INPUT_PREFILL_20261009.md): pinned ESP-IDF
`9a97f6c54ec638111ce55cd36581b3c192f15207`, QIO 80 MHz, full compact AAC/SBR/PS,
staged PDM output, a bounded 500 ms input prefill, fractional PDM clocking,
the laboratory TLS reserve/queue configuration, and runtime diagnostics.
It includes the PCM-tail repair and two optional diagnostic markers;
`CONFIG_YORADIO_STAGED_DMA_PROFILE` enables them. Production builds with that
option off do not emit the markers.

The saved [candidate](../firmware/development/esp32c3-idf-6.1-r9a97-pcm-tail/)
has version `idf61-pcm-tail`, application size 1,620,496 bytes, and SHA-256
`e7d19f98719bb2f8b244096dffe73f57a98794d53fcb63ad918ff3ffbf3c1853`.
Its ELF identity is
`8a95b5a9a3c72f4d82c5a1c3d2b1acee34445e253802c9fa1a820443b7d76a46`.
The source baseline is `7b9c017c`; diagnostic/test changes are committed as
`66e0e4e0`. The manifest records the exact source overlay and configuration
hashes. An unrelated inactive CLZ CMake block is captured as build provenance;
no CLZ benchmark source is compiled.

Actual startup readback confirms QIO 80 MHz and four identical CRC checks of
the mapped application. The PDM divider is `625/312`, with a nominal
160 MHz source, producing nominal 48,000 Hz. This is register verification,
not an externally measured oscillator frequency.

## Short-file submission

The shared generator creates 30 deterministic FLAC files: source frame
counts 1, 127, 511, 512 and 513, mono/stereo, and 8/44.1/48 kHz. FFmpeg 8.1.1
decodes every generated file back to exactly the original signed-16 samples.
FLAC permits a final block shorter than 16 samples while STREAMINFO block
bounds remain at least 16; see [RFC 9639, section 4.1](https://www.rfc-editor.org/rfc/rfc9639.html#section-4.1).

All **60 measured physical cases pass**, 30 over HTTP and 30 over HTTPS.
Warmup and final Stop also pass (62 report entries). Every case checks:

- Exactly one fresh EOF generation and ordered flush/counter/end records.
- The expected remaining PCM frames and full padded driver-submission count.
- No driver write error and inactive playback status after submission.

The resampler produces `1 + floor((source_frames - 1) * 48000 / source_rate)`
output frames. The final 512-frame stereo block is zero-padded; normal packet
boundaries do not add padding. Across the 60 measured cases, 19,968 source
frames produce 53,732 output frames and 294,912 driver-submitted bytes including
end padding. Replay of the saved serial rows reproduces every reported value.

This proves driver acceptance of the expected length, not physical DMA drain
or analog sample identity. Idle queue-overrun events are not used to judge
continuity of these tiny files. Exact PCM content, stale-history isolation,
failed writes and output-task races are covered by the separate host tests.

## Build and digital PCM checks

The final firmware links successfully. Linked-code audits confirm that the
real output task calls flush/discard, flush reaches the PDM driver, full AAC
SBR/PS remains present, and the checked HTTP completion path remains linked.

The four staged/direct and diagnostic/non-diagnostic host variants each pass
432 cases and emit the same 12,331,776 PCM bytes under ASan/UBSan, SHA-256
`5c0536fec9f7e968a8de7e92f868f86032b11c4b4f4ba3304b82804b8f1f0f09`.
The 648-case normalizer comparison is exact. Ten parser tests reject missing
tails, invalid lengths, stale generations, write errors and damaged records.

IRAM text remains 47,690 bytes; DRAM data remains 12,856 bytes and BSS remains
45,664 bytes, matching the preceding prefill image. The repair and diagnostics
add no static RAM in this build.

## Physical regression

The ten-minute HE-AACv2 HTTPS/WebUI test passes its playback, runtime and
settled-heap gates. The measured 585.984-second DMA interval has zero queue
overruns and zero driver write errors. Average CPU busy time is 61.780%; no
CPU-budget threshold is applied. Idle free heap returns from 133,108 to
133,168 bytes, with the largest idle block unchanged at 106,496 bytes.

All 44 ordinary file cases pass: 11 retained fixtures over HTTP and HTTPS,
each with AUTO and explicit decoder selection. They cover AAC-LC, HE-AAC,
HE-AACv2, MP3, FLAC, Vorbis and Opus, including EOF and actual decoded format.
This is the retained matrix, not exhaustive coverage of every syntax in those
formats. Its 44 startup-prefill observations are retained separately.

The heavy FLAC HTTPS/WebUI test also passes playback and settled-heap gates.
Its source is a 610-second synthetic 48 kHz stereo 16-bit FLAC file, about
1.28 Mbit/s; observation lasts 180 seconds. AAC delivery is paced at 1.0x;
finite files and FLAC use unpaced writes with TCP backpressure.

| Metric | HE-AACv2 HTTPS, 600 s | Heavy FLAC HTTPS, 180 s |
| --- | ---: | ---: |
| CPU/decoder/heap/DMA telemetry | Complete | Complete |
| Selected DMA interval | 585.984 s | 165.109 s |
| DMA queue overruns / write errors | 0 / 0 | 0 / 0 |
| Average total CPU busy | 61.780% | 79.480% |
| Minimum heap in paired network snapshots | 24,992 B | 56,980 B |
| Minimum largest free block | 15,360 B | 34,816 B |
| CPU-log heap, first / last median | 26,120 / 26,148 B | 60,880 / 59,348 B |
| Idle heap before / after | 133,108 / 133,168 B | 133,168 / 133,144 B |
| Idle largest block before / after | 106,496 / 106,496 B | 106,496 / 106,496 B |
| Submitted audio / elapsed time | 1.000018203 | 1.000066623 |
| Decoded audio / elapsed time | 0.999977845 | 0.999825482 |
| Median RSSI | -63 dBm | -66 dBm |
| Maximum status-request duration | 156 ms | 125 ms |
| Initial prefill | 500 ms, deadline | 19 ms, queue full |

CPU-log samples and paired network snapshots are taken at different times;
their minima need not match. The network analysis accepts all 116 HE-AACv2
and 34 FLAC paired snapshots. Receive credit is not allocated RAM and does
not identify allocation ownership. Earlier incomplete/failed captures remain
unchanged. This run does not close the separate RX allocation attribution plan.

The preceding prefill image also had zero selected DMA overruns/errors.
Average CPU was 61.088% / 79.362% for the corresponding HE-AACv2 / FLAC runs.
These sequential runs have different RF conditions and binary layout; the
small CPU differences do not isolate repair overhead. Zero queue overruns
are useful service evidence, not a measurement of audible gaps.

All nine transition/fault/WebSocket cases pass: changing AAC format, implicit
SBR, Stop/Play generation changes, connection drop, stalled stream, HTTP error,
redirect, delivery jitter, and WebSocket format/reconnect. Three further
LC → HE → HEv2 → FLAC cycles (12 changes) pass the switching and settled-heap
checks. No allocation, decoder, panic or watchdog fault is recorded by the
applicable runtime gates.

There are **127 passing report entries** across six phases. This total includes
warmup, idle-baseline/recovery and cleanup entries; it is not 127 independent
format combinations. The original per-case verdicts are retained unchanged.

## Restoration

After the tests, app-only OTA restores `idf61-qio80-8c1f2d2d` in `app1`, ELF
identity `54ec71b493261f3c00f86a649625c83e8c772b00eb2af5a3aae594c25e937094`.
Wi-Fi, playlist and settings comparisons pass. Three observations five seconds
apart show active AAC 44.1 kHz stereo playback. This restores the previous
production application and clock configuration; the laboratory candidate is
saved for reproduction rather than left installed.

## Acceptance limits

The user cannot listen during this experiment. No analog output capture or
listening comparison is claimed. Fractional clocking and bounded input prefill
remain disabled by default; exact nominal 48 kHz is the preferred target after
sound quality is qualified. This laboratory TLS/memory configuration is not a
production qualification of the quiet image or every public station.

## Evidence and replay

The [archive](../tests/results/esp32c3-pcm-tail-board-20261009/) retains the
exact short FLAC fixtures, original reports and filtered diagnostic rows,
source snapshots, compiler/link checks, host PCM parity logs, configuration,
clock/flash readback and restoration evidence. TLS private keys and private
settings snapshots are excluded. Frozen analysis sources are used for replay.

With the Python test dependencies installed, run from the repository root:

```powershell
python tests/results/esp32c3-pcm-tail-board-20261009/replay.py --output .build/pcm-tail-replay
```

Use a new output directory. This verifies every indexed byte hash, replays
short-file submission and sustained metrics, and checks firmware identity,
flash CRCs, nominal divider and restoration. It contacts neither the board
nor the network, and it preserves the original results. A new hardware run
requires an awake board, current trusted TLS certificate, and fresh output
paths; use the [test instructions](ESP32C3_TESTING.md#pcm-tail-submission-and-eof).
