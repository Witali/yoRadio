# Four-row smoothing: production-adapter integration

The optional `CONFIG_YORADIO_AAC_SMOOTHING_HISTORY` uses the already measured
[four-row implementation](ESP32C3_AAC_SMOOTHING_HISTORY_20261003.md) in the
real TLS-scoped AAC adapter. It depends on PC18 high-history storage and remains
disabled by default. Use `sdkconfig.aac-smoothing-history.defaults` to select it.

## QEMU results

[Retained results](../tests/results/esp32c3-aac-smoothing-adapter-20261003/adapter/result.json):

| Check | Result |
| --- | --- |
| Streaming format/restart cases | 10 passed, including LC, HE-AAC and HE-AACv2 |
| PCM versus previous PC18 adapter | All 657,540 signed-16 samples identical |
| PCM versus original decoder | Maximum 1 LSB; 10 differing samples |
| Two concurrent HE-AACv2 decoders | Identical full-output hashes |
| Live temporary rows in different tasks | Forced overlap, peak 2 |
| Remaining concurrent-task stack | At least 4,956 of 8,192 bytes |
| Allocation failures / reset | 2 failures and 2 resets handled; heap valid |
| SBR owner request | 45,932 bytes |
| SBR allocator block | 47,104 bytes; poisoned-heap API reports 47,092 usable |

This saves another 2,048 allocator bytes per active SBR owner relative to
PC18-only, or 8,192 relative to the original owner. The new row payload uses
1,024 bytes of the existing decoder stack. These results do not establish
physical CPU timing or whole-radio free memory.

The first integration run exposed an undersized 4 KiB QEMU task stack.
[A hardware watchpoint confirmed the first corrupting stack write](../tests/results/esp32c3-aac-smoothing-adapter-20261003/rejected-stack4096/README.md).
All AAC emulator tests now receive the production decoder's stack plus harness
space; the separate concurrency tasks still use 8 KiB and passed unchanged.

## Physical radio qualification

The awake test image is retained in
[`firmware/development/esp32c3-aac-smoothing-history`](../firmware/development/esp32c3-aac-smoothing-history/manifest.json).
It was installed on the same C3 through WebUI OTA while AAC-LC played. The
transition took **21.593 seconds**, verified the running image hash and preserved
Wi-Fi, playlist and settings. Deep sleep and Flash Auto Suspend remain off;
Flash is DIO/80 MHz. No production default was changed.

The installed candidate also passed three subsequent WebUI application updates:
two alternating-slot round trips and an update while playing. Their update/boot
times were 21.157, 21.469 and 20.953 seconds. All verified the image hash and
preserved Wi-Fi, playlist and settings; filtered serial health and playback
restoration passed. The final snapshot confirms the expected image in `app1`
with 44.1 kHz stereo AAC playing. These checks do not cover interrupted uploads
or power loss during an update.

[Physical evidence](../tests/results/esp32c3-aac-smoothing-adapter-20261003/physical/)
retains complete reports, technical status samples and filtered serial logs.
The local matrix passes **14/14** playback/EOF cases: MP3 320 kbit/s, FLAC level 8,
Vorbis q10, Opus 510 kbit/s, HE-AAC 44.1/48 kHz stereo and HE-AACv2 44.1 kHz stereo,
each with automatic and explicit codec selection. No allocation/decode/panic
diagnostics were captured during that matrix, and restoration passed. Minimum
sampled decoder-stack headroom across it was **4,908 of 16,384 bytes**. The shared
stack must still accommodate Opus; shrinking it to 8 KiB is not a valid RAM fix.

Public streams were probed live immediately before each 60-second test, with
status requests every 0.1 seconds. A transport failure can end an observation
early; the result remains failed. Passing CPU values below are the acceptance
runner's measured mean busy percentages, including the complete radio workload.

| Public stream | HTTP | HTTPS |
| --- | --- | --- |
| AAC-LC 128 kbit/s | PASS; CPU 49.88% | PASS; CPU 53.24% |
| HE-AAC 64 kbit/s | FAIL; WebUI transport error after about 10 seconds | FAIL; allocation/TLS errors |
| HE-AAC 32 kbit/s | FAIL; runtime allocation errors | FAIL; allocation/TLS errors |
| 16 kbit/s AAC, FFprobe reports HEv2 | FAIL; runtime allocation errors | FAIL; allocation/TLS errors |
| MP3 256 kbit/s | PASS; CPU 57.08% | PASS; CPU 66.77% |

The HE cases briefly produce full-rate PCM, but that does not qualify continuous
playback. Their failed windows include stalls and must not be used as passing
decode-speed benchmarks. The separate retained Groove Salad 16 recording is
[mono SBR without PS](ESP32C3_AAC_PS_COVERAGE_20261003.md); neither FFprobe's
label nor two duplicated output channels prove PS coverage for a live test.

HTTP captured **54 failed allocations**: 51 requests for 1,700 bytes and three
for 1,512 bytes. HTTPS captured **23**, including 17 requests for 1,700 bytes.
At failed requests the smallest observed free totals were 4,712 / 5,012 bytes
and largest blocks 1,344 / 1,408 bytes, respectively. The larger HTTPS failures
are retained as reported; the failure callback alone does not identify their
owner. There were no retained panic/capture errors. Both suites recovered their
settled idle heap and restored saved settings/playback after reboot.

The additional 2,048-byte owner saving is therefore **insufficient for public
HE-AAC with network/WebUI load**. It remains an experimental component of the
RAM-reduction work, not a production-qualified solution. Preserve full rates,
channels, TLS buffers and the other codecs while reducing persistent QMF/PS
storage further; do not accept core-only AAC as successful HE-AAC.

Host evidence checks: `python tests/test-aac-smoothing-adapter.py`.
`python tests/test-aac-smoothing-radio-evidence.py` verifies the retained physical
checks and ensures the public HE failures are not relabelled as passes.
The result JSON retains the QEMU command and source/fixture hashes.
