# ESP32-C3: PC19 and late SBR in the network firmware

## Change and acceptance scope

Commit `ee920c0b` makes the tested PC19 representation and late-SBR controller
available outside QEMU. `CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19` keeps signed
19-bit real/imaginary mantissas, a shared four-bit shift and the extra bits in
the decoder context. `CONFIG_YORADIO_AAC_LATE_SBR` preserves AAC transform
history when SBR starts later and retains established SBR/PS through frames
without extensions. The checked FIL readers and native profile observer are
included. No new DSP arithmetic or sample-rate limit is introduced.

The options remain off by default. `sdkconfig.aac-pc19.defaults` is a combined
qualification profile. The existing QEMU switches still select their historical
experiments; physical builds do not link their tests or allocation registry.

The candidate is awake, DIO 80 MHz, CPU 160 MHz, with Flash Auto Suspend off,
the existing 16 KiB decoder stack and the previous network/CPU diagnostics.
The saved application is under
[`firmware/development/esp32c3-aac-pc19-network/`](../firmware/development/esp32c3-aac-pc19-network/).
Its ELF SHA-256 is
`25abec031731594df46a178734ac39a723bf2ed30113167a43d87084318a9810`.
The image was built before the source commit, so its embedded version contains
`1d68e0b4-dirty`; the executable sources match `ee920c0b`.

## Compiled layout and code

`verify_aac_network_build.py` checks the actual ELF/DWARF types, configuration,
image hash, pinned archive/patch provenance and disassembled calls. The native
frame controller calls the retention bridge and checked FIL wrappers. The FIL
wrapper calls the late-SBR history-bank adjustment. No QEMU test hooks are linked.

| Item | Previous physical diagnostic image | Candidate | Difference |
| --- | ---: | ---: | ---: |
| Native AAC adapter, requested bytes | 52 | 204 | +152 |
| High-history runtime, included in adapter | 16 | 160 | +144 |
| SBR owner, requested bytes | 32,744 | 32,744 | 0 |
| Static DRAM data / BSS | 12,620 / 31,480 | 12,620 / 31,480 | 0 |
| IRAM text | 43,354 | 43,354 | 0 |
| Flash text | 1,117,510 | 1,118,868 | +1,358 |
| Flash read-only data | 389,136 | 389,576 | +440 |

The adapter increment includes 144 bytes of PC19 metadata and eight bytes of
late-controller state. Do not count the runtime context twice. The owner is
already compact in the previous physical image: this integration improves
precision and late activation, rather than claiming another owner RAM saving.
Allocator overhead and network heap are measured separately.

## Emulator and installation

The new feature configuration passes the complete existing QEMU FIL, metadata,
late-activation, absent/resumed-SBR, allocation-failure, reset, concurrent-decoder
and pointer checks. All 865,280 transition/gap PCM channel samples are identical
to the previous passing PC19 image. This ties the integration to the retained
[synthetic](ESP32C3_AAC_PC19_20261004.md) and
[real-recording](ESP32C3_AAC_PC19_RECORDINGS_20261004.md) precision evidence.
It is not a fresh physical PCM capture or an all-input precision proof.

OTA while AAC-LC 48 kHz stereo was playing passed in 20.907 seconds, from app0
to app1. The running ELF hash matched, and in-memory comparisons confirmed
unchanged Wi-Fi configuration, playlist and settings. Passive serial capture
contained no panic or capture error. Only the application image was written.

## Physical playback

The first 14 finite-file checks passed: AAC-LC 48 kHz, HE-AAC 48 kHz,
HE-AACv2 44.1 kHz, MP3 320 kbit/s, FLAC level 8, Vorbis q10 and Opus
510 kbit/s, each with automatic and explicit codec selection. The checks require
actual full-rate PCM and the correct profile, then observe EOF.

Both in-stream transition sequences passed, including the previously failing
AAC-LC to HE-AACv2 transition with an unchanged ADTS configuration. Stop/play
generation isolation also passed. This is physical evidence for the late-SBR
repair, not just an updated display label.

All 20 matrix checks passed, including 21 station changes in three cycles and
WebSocket format/reconnect checks. Settled free heap was 145,872 B after the
first cycle and 145,776–145,788 B after the third; the largest block stayed
114,688 B and the task count stayed 17. No allocation/decoder failure or panic
was captured. This demonstrates bounded recovery over those cycles, not an
indefinite leak-free guarantee.

## CPU under WebUI load: failures retained

The original 40-second load suite polls status with a 0.1-second delay between
requests. The non-AAC cases use new deterministic 60-second stress files. CPU
figures below are from successful acceptance windows after the 10-second warm-up;
failed cases do not borrow samples from the next codec.

| Input | Result | Mean / peak CPU | Minimum free heap / largest block |
| --- | --- | ---: | ---: |
| AAC-LC 48 kHz stereo | PASS | 47.317 / 48.7% | 76,072 / 65,536 B |
| HE-AAC 48 kHz stereo | FAIL: one status connection timed out | Not qualified | Not qualified |
| HE-AACv2 44.1 kHz stereo | PASS | 67.317 / 68.0% | 42,460 / 31,744 B |
| MP3 320 kbit/s | FAIL: progressive free-heap decline | Not qualified | Not qualified |
| FLAC level 8 | PASS | 68.333 / 69.2% | 68,244 / 53,248 B |
| Vorbis q10 | FAIL: progressive free-heap decline | Not qualified | Not qualified |
| Opus 510 kbit/s | FAIL: progressive free-heap decline | Not qualified | Not qualified |

The failed HE window had 11 successful responses and full 48 kHz stereo PCM
before the connection timeout. The next HEv2 case recovered without a reset.
No allocation/decoder error, panic or unexpected reboot was captured anywhere
in the load run. The non-AAC heap declines occur in roughly 1.7 KiB allocation
steps. Bounded receive buffering is a hypothesis to investigate, not an
established cause or grounds for changing FAIL to PASS.

An isolated repeat of the same HE-AAC 48 kHz load case subsequently passed
40 seconds: 228 responses, 125 ms maximum HTTP latency, 62.733% mean / 63.5%
peak CPU, 42,404 B minimum free heap and 24,576 B minimum largest block. Serial
capture again had no panic or error. This repeat did not reproduce the timeout;
the earlier failure and its unresolved cause remain in the evidence.

The minimum sampled stack margins were 2,664 B for the decoder, 2,888 B for
HTTP and 2,640 B for TCPIP. Static WebUI worker margins were only 588/448 B.
Keep the current stack sizes. Overall production acceptance remains open.

## Five-minute real HTTPS radio

Groove Salad 64 kbit/s HE-AAC passed 300 seconds at full 44.1 kHz stereo, with
certificate verification and the same 0.1-second status polling delay. All four
gates passed: idle baseline, playback/load, settled heap recovery and restoration
of the original stopped state/settings.

| Measurement | Result |
| --- | ---: |
| Total CPU, mean / peak | 64.781 / 65.6% |
| Minimum free heap / largest block | 16,232 / 4,608 B |
| Audio-time / wall-time ratio | 1.001612 |
| Status responses | 1,635 |
| HTTP median / p95 / maximum | 78 / 94 / 266 ms |
| RSSI minimum / median / maximum | −84 / −69 / −58 dBm |
| First PCM | 2.563 s |
| Idle heap before / after | 145,788 / 145,764 B |
| Idle largest block / tasks | 114,688 B / 17, unchanged |

No allocation/decoder/TLS error or unexpected reset was recorded during
playback. The restore step deliberately reboots, then verifies settings.
The 4,608-byte minimum largest block passes the existing 4,096-byte gate with
little margin. This run does not establish unlimited TLS/WebUI headroom or
the cause of the separate local-load failures. The previous diagnostic image's
similar HTTPS run measured 64.020% mean CPU; different radio/network conditions
prevent attributing that difference entirely to PC19.

## Remaining work

- Diagnose the single HE-AAC status timeout without discarding its failed run.
- Distinguish bounded receive buffering from ongoing allocation growth in MP3,
  Vorbis and Opus; observe longer steady-state windows and settled recovery.
- Repeat OTA negative/repeated-upload cases on this candidate. The installation
  transition passed, but it is not the complete OTA regression suite.
- Extend sustained HTTP/HTTPS and AAC rate/profile/framing coverage, malformed
  input and same-decoder recovery, and verify physical OLED/acoustic behavior.
- Keep defaults unchanged until the outstanding qualification gates are met.

The [saved evidence](../tests/results/esp32c3-aac-pc19-network-20261004/) includes
the exact image identity, configs, linked-layout checks, diagnostic logs, source
snapshots and unmodified PASS/FAIL results. Captured music PCM and credentials
are not included. `python tests/test-aac-network-evidence.py` replays the retained
evidence checks; it does not rerun the physical board.

## Reproduction

Use separate build directories, the exact saved SDK configurations and the
pinned ESP-IDF/toolchain/archive. The general commands are:

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory <build> -Sdkconfig <build>/sdkconfig build
python tools/codec_benchmark/verify_aac_network_build.py --build <build-path> --objdump <riscv32-esp-elf-objdump.exe> --output <build-report.json>
python tools/codec_benchmark/run_aac_fill.py --build <qemu-build> --dependency-root <dependencies> --qemu <qemu-system-riscv32> --bios <qemu-share> --wsl --output <qemu-results>
python tools/esp32c3_tests/diagnostic.py ota_transition --help
python tools/esp32c3_tests/diagnostic.py run --help
python tools/esp32c3_tests/public_streams.py --help
```

Substitute real paths for placeholders. The physical test runners require the
board's current address, the reachable test-server address and passive USB log
port. They verify the installed image before qualification and preserve the
previous saved settings. The emulator image must never be installed on hardware.
