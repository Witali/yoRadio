# AAC/TLS contiguous-memory headroom investigation

## Problem to reproduce

The quiet production candidate completed ten minutes of public HE-AAC HTTPS
playback without recorded allocation/watchdog faults or sustained I2S service
events. One sampled largest free block was 7,424 B, below the existing 8,192 B
headroom gate, while total free heap was 24,668 B. This is a failed headroom
gate, not an observed out-of-memory event. See
[output-health qualification](ESP32C3_OUTPUT_HEALTH_20261010.md).

## Allocation lifetimes checked in source

| Memory | Ownership/lifetime | Consequence for steady playback |
| --- | --- | --- |
| TLS receive storage, 17,058 B | Static RX-only slot in `tls_large_reserve.c`; four audited dynamic-RX allocation sites claim it, zero it before returning it, and release ownership after erasing used bytes | One active RX allocation fitting the slot does not require a matching free heap block. Busy/oversize requests still fall back to the ordinary TLS allocator. |
| Input packet slots | Adaptive pool; current minimum is four 2,060-byte slots, including headers | Reclaiming preserves queued/leased data and the floor. With all four minimum slots resident, there is no extra slot available for reclamation. |
| ADTS frame | `native_aac_decoder.c:reserve_frame`, grows with `realloc` in 128-byte steps and retains capacity until close | A larger frame can still need a new contiguous block while the decoder and TLS are live. Failure preserves the old allocation and propagates a memory error. |
| Caller PCM | `decoder_pcm_prepare`, initially 8,192 B for AAC, allocated before decoding; the generic retry contract can request a larger buffer | Normal stereo SBR output fits the prepared workspace. Do not treat that normal case as a universal proof that no PCM resizing is possible. |
| AAC/SBR owner | Compact-owner allocation wrappers and frame/parser callbacks; state persists between frames | Codec changes, reopening, or first SBR activation remain separate allocation phases. A frame-growth test alone does not cover all format transitions. |
| PCM ring and I2S buffers | Allocated during audio-service/output initialization | Ordinary playback reuses this storage. Reinitialization must preserve the existing release/order rules. |
| TLS TX and handshake state | SDK dynamic allocator; configured output content limit 4,096 B | RX reservation does not reserve all TLS memory. TLS 1.2 renegotiation is enabled in this configuration, so a universal claim that handshake work occurs only at startup would be wrong. |
| Wi-Fi, TCP and WebUI | Concurrent tasks and SDK allocations | Total free heap and largest block are observations, not reservations. Another task can allocate after a snapshot. |

The 8,191-byte ADTS parser ceiling is not a demonstrated frame requirement for
ordinary single-block mono/stereo AAC. The existing standards-bounded DSE
fixtures grow to 1,543 B (stereo core) or 775 B (mono core), with retained
capacities of 1,664/896 B. Keep the parser's support unchanged; do not substitute
an invalid padded frame or lower the memory gate merely to obtain PASS.

## Controlled HTTPS growth experiment

Reuse the exact six independently checked baseline/growth fixtures from
[the HTTP campaign](../tests/results/esp32c3-aac-growth-20261010/README.md).
They cover AAC-LC, HE-AAC and HE-AACv2; frames grow after 15 seconds without
changing decoded PCM in either FFmpeg or unquantized FAAD.

The separate laboratory image adds exactly one local test CA to all 145 normal
public trust entries. The saved config retains certificate verification, full
16 KiB TLS input content capacity, quiet operation, compact full-rate AAC,
the same 17,058 B RX reserve and input-pool policy. All 50 application objects
retain identical code/constants; static RAM does not change. This avoids
adding a large heap tracing buffer to the measurement.

The runner `tools/esp32c3_tests/aac_growth.py` accepts `--ca`, `--cert`, `--key`
only as a complete set, validates the firmware's laboratory-CA identity, and
records negotiated TLS parameters and complete delivery for each fixture.
`--require-output-health` also checks sustained I2S completion/write counters.
Keys remain local; only public certificates and technical observations are
retained. It records memory evidence before enforcing the existing budget,
so a failed gate does not erase its measurements.

## Physical result

**15/16 checks pass.** Every file completes with the expected profile, PCM
format, duration and EOF. Each of the six separate connections negotiates
TLS 1.2 / `ECDHE-RSA-AES256-GCM-SHA384` and delivers the complete fixture.
There are no sustained completion-queue drops or I2S write errors in any case.
Across 522 health samples, boot identity remains unchanged and allocation-
failure/watchdog counters stay zero.

| Case | Minimum steady free heap | Minimum largest block | Maximum status + health | Verdict |
| --- | ---: | ---: | ---: | --- |
| AAC-LC baseline, 48 kHz stereo | 63,588 B | 55,296 B | 272 ms | PASS |
| AAC-LC growth to 1,543 B/frame | 54,520 B | 40,960 B | 273 ms | PASS |
| HE-AAC baseline, 44.1 kHz stereo | 31,768 B | 22,528 B | 354 ms | PASS |
| HE-AAC growth to 1,543 B/frame | 20,832 B | **7,424 B** | 390 ms | **FAIL: headroom budget only** |
| HE-AACv2 baseline, 44.1 kHz stereo | 32,180 B | 24,576 B | 301 ms | PASS |
| HE-AACv2 growth to 775 B/frame | 26,192 B | 14,336 B | 297 ms | PASS |

Times in the table round up. The HE-AAC growth case still completes all
35.016 seconds of reference audio (observed active interval 35.224 s). Its
failure remains the existing 8,192 B largest-block budget, not a failed frame
allocation. Median free heap decreases by 8,640 B / 9,796 B / 4,674 B after
growth for LC / HE / HEv2 respectively; unchanged-frame controls remain flat.
This whole-system difference is larger than the retained ADTS capacity change.

After each profile pair, settled median free heap is 139,696 B versus
140,112 B initially; largest block is 114,688 B and task count is 16 throughout
the idle checkpoints. Memory recovery passes. The controller restores the
exact listened image and verifies Wi-Fi, playlist, settings and stopped state.

The laboratory image is saved at
`firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls/app.bin`, SHA-256
`7871681aef75c9bb89caffab97f073eabe62b272ff8dc20f710cb4473c56b6fd`.
It is not a production release. A test CA is deliberately included only in
this separate image; it is removed from the board by restoration.

[Frozen measurements, build audit and offline replay](../tests/results/esp32c3-aac-growth-tls-20261010/README.md).

## Interpretation limits and next decisions

The tested ordinary single-block frame-growth scenario now succeeds with an
already-live TLS connection and decoder, including the below-budget HE-AAC
case. It therefore narrows the original concern about this particular late
allocation. It does not prove that any arbitrary AAC frame or late TLS
allocation fits, and does not retroactively change earlier failed budgets.

This isolates frame growth with an already-live TLS connection and decoder.
The server uses paced 1,024-byte application writes; it does not cover every
TLS record pattern, concurrent TLS contexts, renegotiation or every AAC
configuration transition. Higher encoded bitrate after growth also changes
network buffer occupancy; do not attribute the whole heap difference to the
ADTS allocation itself.

Keep the previous failed budgets and production qualification open until the
applicable allocation requirements are demonstrated. Any reserve/pool change
must preserve leased input, format support and PCM quality, and be checked for
new output service events. No firmware allocator change is made by this
experiment.

The follow-up [quiet TLS-record campaign](ESP32C3_QUIET_TLS_RECORDS_20261010.md)
separates TLS record-size changes from ADTS frame growth. It uses measured
1/16 KiB records with HE-AAC/HE-AACv2 and independent output/memory gates.
The preserved 7,424-byte results above remain unchanged; application-record
tests do not establish the memory required by a late TLS renegotiation.
