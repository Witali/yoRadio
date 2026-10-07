# ESP32-C3 custom decoder release at EOF and error

Date: 2026-10-05. Branch `codex/aac-storage18`.

## Confirmed defect and fix

The C3 service's custom FLAC and Helix/minimp3 branches returned each encoded
packet before reaching the cleanup used by the native AAC/simple decoders.
Consequently, natural EOF changed the player status to `stream ended` but left
the custom decoder and its input/channel workspaces allocated until Stop or a
new station generation. A decode error had the same ownership gap.

On the physical C3, the old prefill image retained approximately **52 KiB after
FLAC EOF**. An explicit Stop recovered that memory. This is retained state at
natural termination, not a claim of cumulative leakage or reduced peak decoding
memory.

The service now destroys each custom decoder after its synchronous feed call
finishes draining EOF, or after a failure of the current generation. It clears
the handle to make subsequent cleanup safe. For Helix/minimp3, destroy first
releases the arena owner; then discard returns the reusable arena allocation to
the heap. A failed discard remains an explicit error and never forcibly frees
an arena still owned by a decoder.

`send_pcm` copies each callback's PCM into the output queue. Those independent
queue items, including the DMA leases, remain alive until output consumes them.
The terminal marker still follows all queued PCM and keeps its generation tag.
Stop/station cancellation during a callback continues to use the existing
generation-change cleanup. DSP arithmetic, format support, sample rate,
resampling, precision and DMA prefill are unchanged.

Audited owners and consumers:

| Storage | Producer / consumer | Release |
| --- | --- | --- |
| Custom FLAC input | `reserve_input`, header parser, `decode_available` | `custom_flac_decoder_destroy` frees input and object |
| FLAC segmented channel workspaces | `FLACDecoder_AllocateBuffers`, FLAC prediction/output | `FLACDecoder_FreeBuffers` frees each segment and clears its pointer |
| Helix/minimp3 state and adapter input/PCM | `custom_legacy_decoder_feed`, synchronous PCM callback | Destroy calls the selected backend's FreeBuffers/scratch release, frees input/object |
| Shared legacy arena | Backend allocator and active-owner accounting | `CodecArenaRelease` precedes `CodecArenaDiscard`; discard refuses an active owner |
| Queued PCM / DMA leases | `send_pcm`, output task | Output task owns the copied bytes; decoder teardown does not free them |

## Hardware evidence

The new `terminal_memory.py` test waits for natural EOF and samples idle heap
**without calling Stop**. It separately tests an explicit Stop afterwards.
The usual 2 KiB total-free and 4 KiB largest-block recovery tolerances remain
unchanged. The before/after files, including failed baseline gates, are retained.

| Firmware / fixture / hint | Free heap before / after natural EOF | Largest block before / after EOF | EOF recovery |
| --- | ---: | ---: | --- |
| Before / FLAC / auto | 147996 / 94532 B | 110592 / 59392 B | **FAIL: 53464 B retained** |
| Before / FLAC / explicit | 147892 / 94568 B | 110592 / 59392 B | **FAIL: 53324 B retained** |
| Fixed / FLAC / auto | 147828 / 147710 B | 114688 / 114688 B | PASS |
| Fixed / FLAC / explicit | 147716 / 147744 B | 114688 / 114688 B | PASS |
| Fixed / HE-AACv2 / auto | 147744 / 147748 B | 114688 / 114688 B | PASS |
| Fixed / HE-AACv2 / explicit | 147748 / 147748 B | 114688 / 114688 B | PASS |
| Fixed / Vorbis / auto | 147748 / 147748 B | 114688 / 114688 B | PASS |
| Fixed / Vorbis / explicit | 147748 / 147748 B | 114688 / 114688 B | PASS |

Values are medians of settled samples; each run is compared against its own
idle baseline. All six fixed cases play at their expected rate/layout before
EOF, keep the terminal status, recover memory both without and with Stop, and
return to 17 tasks. Including their checkpoints and restored settings, the
candidate report has **37/37 passing checks**. The baseline's two failures
remain saved. Short synthetic-file tests do not cover every stream variant.

The host runner compiles the actual two custom service branches with guarded
decoder/platform stubs. ASan/UBSan cover 17 ownership scenarios: ordinary data,
EOF with final PCM, transport termination, decode errors, generation cancellation,
repeated terminal cleanup and refused arena discard. Copied queue bytes survive
workspace destruction. These are lifetime tests, not a replacement for actual
DSP quality tests or a physical qualification of optional Helix/minimp3 builds.

The full C3 build retains PC19 full-rate AAC/SBR/PS and three-block PCM prefill.
BSS stays **29,464 B**, DRAM data **12,620 B** and IRAM text **43,354 B**: no
additional permanent RAM. The saved candidate is
`firmware/development/esp32c3-custom-terminal/app.bin`, ELF SHA-256 beginning
`6eea8a8f2f90`. RX ownership tracing and deep sleep are disabled. This remains an
experimental playback image while the wider format/soak/fragmentation gates
are incomplete.

## Opus latency recheck and remaining work

Before installing the fix, the non-RX-tracing prefill image repeated the same
160-second Opus stream. The settled 120-second window passes: CPU mean/peak
79.90/80.8%, audio/wall ratio 1.00174, maximum WebUI response 141 ms, minimum
free heap 77,416 B and largest block 63,488 B. Idle memory recovers. The initial
heap-growth gate still fails and remains saved. The prior diagnostic image's
3,078 ms WebUI response is not reproduced or erased; its cause is unproven.

The fixed image then ran MP3 -> Vorbis -> Opus at 48 kHz stereo, 180 seconds
per codec, with HTTP status polling and Stop/idle measurements between codecs.
There was no reboot between codecs. The original report has **7 PASS / 3 FAIL**;
all failures remain retained. A supplementary window after 40 seconds reports
the following measurements, without replacing the original ten-second-warmup
acceptance gate:

| Codec | CPU mean / peak | Decoded audio / elapsed time | Max HTTP response, full run | Minimum RSSI | Largest free block after Stop |
| --- | ---: | ---: | ---: | ---: | ---: |
| MP3 | 60.02 / 61.3% | 1.00169 | 547 ms | -75 dBm | 114688 B |
| Vorbis | 73.62 / 74.7% | 1.00152 | 891 ms | -73 dBm | 94208 B |
| Opus | 64.41 / 80.8% | **0.80433** | **2204 ms** | -79 dBm | 94208 B |

- MP3 fails the original progressive-heap-loss gate. Its later window passes
  and idle memory recovers to the first baseline; the initial FAIL is not waived.
- Vorbis passes playback/CPU/HTTP checks but reproduces persistent fragmentation:
  largest free block falls **114688 -> 94208 B (20 KiB)**. Total free heap remains
  within the existing 2 KiB tolerance, and the task count returns to 17.
- Opus fails the original 2-second HTTP limit and the supplementary real-time
  progress gate. Its lower average CPU accompanies incomplete audio progress;
  it is not evidence of improved decoding efficiency. This occurs without RX
  tracing, so tracing is not required for a slow HTTP response. Network delivery,
  task scheduling and the retained allocation still need separate diagnosis.
- Opus's local idle comparison passes because it starts with an already
  fragmented heap. Comparing every checkpoint against the **first** idle baseline
  correctly preserves the 20 KiB loss after both Vorbis and Opus. The new summary
  and its regression test explicitly enforce this distinction.

The capture has no recorded panic/heap-corruption/capture-error marker. Restore
reboots to the same fixed image and the saved AAC station plays again. This
single sequence is not a 100-switch or 30-minute soak qualification.

This terminal-retention fix does not identify the owner of the reproduced
post-Stop Vorbis fragmentation, complete the full Ogg/Vorbis boundary corpus or qualify
unsupported FLAC layouts. Continue those items in the
[Vorbis plan](ESP32C3_VORBIS_REPAIR_PLAN.md) and the broader playback tests.

## Reproduction

```powershell
python tests/run-custom-decoder-terminal.py
python tests/test-terminal-memory.py
python tests/test-codec-sequence-summary.py
python tests/test-custom-decoder-terminal-evidence.py
python tools/esp32c3_tests/diagnostic.py terminal_memory --board http://BOARD_IP --host HOST_IP --serial-port COM_PORT --case flac-level8 --case hev2-44100-stereo --case vorbis-q10 --output .build/terminal-memory-recheck
python tools/esp32c3_tests/summarize_terminal_memory.py .build/terminal-memory-recheck/report.json --output .build/terminal-memory-recheck/summary.json
python tools/esp32c3_tests/diagnostic.py run --board http://BOARD_IP --host HOST_IP --serial-port COM_PORT --suite load --fixture-manifest .build/codec-load-long/stress-fixtures/manifest.json --case stress-mp3-48000-2ch-16bit-200s --case stress-vorbis-48000-2ch-16bit-200s --case stress-opus-48000-2ch-16bit-200s --load-seconds 180 --load-idle-recovery --sdkconfig firmware/development/esp32c3-custom-terminal/sdkconfig --output .build/codec-sequence-recheck
python tools/esp32c3_tests/summarize_codec_sequence.py .build/codec-sequence-recheck --output .build/codec-sequence-recheck/summary.json
```

Use the matching profiling firmware and reachable host HTTP server. The test
changes playback temporarily and reboots to restore the saved station. It does
not change stored settings. The native host test requires WSL GCC/ASan/UBSan on
Windows. [Evidence manifest](../tests/results/esp32c3-custom-terminal-20261005/manifest.json)
covers byte-exact source snapshots, compressed raw telemetry, reports and the
compiled-image checks. HTTP/OTA comparisons retain only equality checks for
private settings, not their contents.
