# Delayed AAC frame growth on ESP32-C3, 2026-10-10

**15/15 physical checks pass** on the unchanged `idf61-quiet-mpi-health`
candidate. Three 35-second synthetic files are each tested in baseline and
growth form over local HTTP. Growth starts after 15 seconds. All files retain
their audio configuration and reach EOF; Stop recovery, settings persistence
and lifetime health pass. No firmware implementation or budget was changed.

## Reference construction

The fixture generator prefixes byte-aligned Data Stream Elements (DSE) to
existing raw AAC blocks. It changes ADTS length/fullness fields but preserves
the audio elements. Its bounds follow the base AAC channel bit budget in
[ISO/IEC 14496-3:2001](https://www.ossrs.net/lts/zh-cn/assets/files/ISO_IEC_14496-3-AAC-2001-7f4d0b3622b322cb72c78f85d91c449f.pdf),
tables 4.10/4.57 and section 4.5.3.1. This is a specific, independently decoded
test construction, not a comprehensive MPEG conformance suite. CRC protection,
PCE configurations and multiple raw blocks are deliberately outside this
generator's scope; firmware support is unchanged.

| Fixture | Original maximum ADTS frame | Late ADTS frame | Expected retained frame capacity | Source/PCM rate |
| --- | ---: | ---: | ---: | --- |
| AAC-LC stereo | 519 B | 1,543 B | 1,664 B | 48 kHz |
| HE-AAC stereo | 517 B | 1,543 B | 1,664 B | 44.1 kHz |
| HE-AACv2 stereo (mono core) | 243 B | 775 B | 896 B | 44.1 kHz |

The original fixtures are retained synthetic tones from FDK AAC. Fresh FFmpeg
decodes and pristine float32 FAAD decodes each produce **byte-identical S16
PCM within that decoder** for baseline versus growth. FAAD processes all
frames, preserves SBR/PS activity and emits identical per-frame shape/state.
FFmpeg and FAAD differ in priming behavior; no cross-decoder equality is claimed.
The comparison does not measure PCM emitted by the ESP32-C3.

FAAD revision `e8e76f0a44db45aed773a3f62fe35a63c867a738` is checked against its
pinned archive before building. All 129 source-file hashes, compiler argv,
probe source, executable hash, decoder versions, per-frame traces and output
hashes are saved. The initial sandboxed WSL launch failed with
`Wsl/E_ACCESSDENIED`; the authorized build outside that sandbox succeeded.
Both logs are retained. Generated AAC/PCM and the disposable host executable
remain in the ignored build directory rather than this archive.

## Physical observations

Both parts of the growth fixture are paced separately at 1.0x so the larger
late frames cannot accelerate the small-frame warmup. Status polling also
reads health. Each case uses the same app, input-buffer settings and output
clock; baseline precedes growth for each profile.

| Fixture | Baseline minimum free / largest, B | Growth minimum free / largest, B | Growth longest status + health, ms |
| --- | ---: | ---: | ---: |
| AAC-LC | 69,688 / 57,344 | 57,988 / 43,008 | 344 |
| HE-AAC | 35,772 / 24,576 | 24,808 / 11,264 | 295 |
| HE-AACv2 | 36,140 / 24,576 | 27,904 / 15,360 | 318 |

The acceptance limits remain 16/8 KiB free/largest and two seconds per paired
request. All **520 health samples** retain one boot ID, zero allocation
failures and zero task-watchdog events. Settled free heap is 140,132 B before
the run and 139,948..139,952 B after the three pairs. Largest capacity returns
to 114,688 B, with 16 tasks.

Total memory impact exceeds the frame-buffer increase. Median free heap in
the 8..13 versus 23..30 second windows falls by 10,012 B for LC, 9,050 B for
HE and 6,352 B for HEv2 in the growth legs. Baseline windows are unchanged.
These are whole-system measurements; they do not attribute the difference to
the decoder, TCP, Wi-Fi or another allocator. The added ancillary data also
increases network bitrate. Further attribution must not call this entire
difference the cost of `reserve_frame()`.

## Image and restoration

- Candidate app SHA-256: `5505393d2b7d4fcad1303b3b96d9c41709c86a84e687bcbeb059a4241d243da6`.
- Candidate ELF SHA-256: `6524f1457d6009ee1c229e86bc64a2ff3361fd7df3810b1d2b652b9f0c2ce751`.
- Restored `idf61-listen48-8c1f2d` in `app0`, ELF SHA-256
  `76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.
- Wi-Fi, playlist and settings comparisons pass. Three stopped observations
  confirm restoration. Controller exit status is zero; no serial reset/flash.

## What this closes and what remains

Late growth of these valid single-block AAC-LC/HE/HEv2 files works on the
physical quiet image over HTTP. The historical 8,191-byte number is the ADTS
parser ceiling; it is not established as the allocation required by an
ordinary mono/stereo single-block frame. This result does not remove that
parser capacity or relax any acceptance threshold.

TLS pressure is not exercised here. The prior 7,936-byte-largest HTTPS sample
and intermittent slow WebUI request remain recorded. Next, distinguish
network/storage contributions under higher bitrate and verify sustained
playback with audio-output service evidence. No CPU, DMA underrun, analog
continuity or full-radio completion claim follows from status/health alone.

## Offline replay

From the worktree root, using a fresh output path:

```powershell
python tests/results/esp32c3-aac-growth-20261010/review.py --output .build/aac-growth-replay/review.json
```

This checks all archive hashes, regenerates the six fixture hashes from the
retained original audio and frozen generator, rechecks recorded physical
format/duration/memory/recovery gates and verifies both app identities plus
restoration. It neither downloads files nor accesses the board. Host PCM
hashes/traces are checked as retained evidence; the replay does not rerun the
reference decoders. `prepare.py` and `physical.py` record the original local
commands/paths and require deliberate relocation for a new physical run.
