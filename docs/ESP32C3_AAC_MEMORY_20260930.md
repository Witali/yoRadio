# ESP32-C3 AAC/SBR memory investigation — 2026-09-30

## Conclusions

The next implementation steps, dependencies and acceptance gates are saved in
the [AAC/SBR memory execution plan](ESP32C3_MEMORY_STABILITY_TODO.md#execution-plan-and-decision-gates).

1. **The Helix arena mechanism can be shared with Espressif AAC, but the current
   24 KiB arena cannot hold it.** Production Espressif AAC does not use this
   arena; it is not a spare resident 24 KiB block that can simply be reclaimed.
2. The failing 55,128-byte request is an entire `SBRDECODER_DATA` object. Its
   two channel objects and PS state use fixed offsets in the shipped binary.
   An allocator cannot replace this one pointer with scattered small blocks.
3. Splitting arrays and sharing additional scratch is feasible **with decoder
   source changes**, followed by full SBR/PS equivalence tests. Some substantial
   reuse already exists, including right-channel storage in parametric stereo.
4. Fragmentation is only half the problem: the physical radio also lacks about
   20 KiB of total heap for SBR plus its control object in the measured LAN case,
   before reserving operating headroom. A larger arena alone creates no RAM.

This is an investigation, not an HE-AAC fix. The board was restored to its
previous quiet production image without deep sleep; its saved station plays.

## Evidence and scope

ESP32-C3 SuperMini OLED, 160 MHz, no PSRAM, ESP-IDF 6.0.2, codec package 2.6.2
at `esp-adf-libs` revision `67b8d0e98f58c774b8652480893037273190e8dc`.
Both optional Wi-Fi IRAM settings are disabled. The compressed ring is 10 ×
1,600 bytes. Diagnostics add runtime accounting, a 4 KiB profiler task and logs.

[Saved evidence](../tests/results/esp32c3-aac-memory-20260930/provenance.json)
includes the exact ELF/image hashes, configuration, heap/stack log, playback
observations, linker sections, selected binary disassembly and reference types.
The measured application ELF identity is
`3c6eb7f97d80861ae209a0b87e242ed5befa0f627788334213811df2e4a9f184`.

### Full-radio heap, bytes

| Stage | Total free | Largest block |
| --- | ---: | ---: |
| Application entry | 278,944 | 139,264 |
| Before network initialization | 252,300 | 114,688 |
| After network initialization | 207,620 | 114,688 |
| After audio pipeline startup | 141,212 | 114,688 |
| After WebUI startup | 112,132 | 98,304 |
| HE test, before ADTS wrapper | 97,616 | 61,440 |
| After ADTS wrapper, before SDK open | 88,908 | 61,440 |
| After SDK open / failed SBR request | 36,192 | 13,312 |

Stages include concurrent tasks and temporary startup allocations; differences
are observed heap changes, not an allocation trace attributable to one function.
The SDK open accounts for about 52.7 kB in this run. The native ADTS wrapper is
8,204 bytes (`data[8191]` plus fields/alignment), and the separate caller PCM
workspace is 12,288 bytes. They are not part of the 55,128-byte SBR object.

The binary also requests an additional **1,180-byte `SBR_DEC`** control object
after the large SBR allocation succeeds. The simple deficit at this checkpoint
is therefore `55,128 + 1,180 - 36,192 = 20,116 bytes`, excluding allocator overhead
and network headroom. HTTPS additionally needs its TLS state and 16 KiB receive /
4 KiB transmit record buffers. Moving allocations earlier may improve largest
block size but does not remove this simultaneous-memory deficit.

The initial diagnostic map has 55,130 bytes of IRAM code (55,296 bytes including
alignment), 13,492 bytes of initialized DRAM and 31,352 bytes of BSS. The added
survey keeps the same RAM section sizes, recorded in `sections.json`. Do not add
`.dram0.dummy` again: it represents the DRAM alias occupied by IRAM code.
The codec's large constant tables are already in flash, not heap.

LC 48 kHz stereo passes the 35-second low-rate-polling survey. HE 48 kHz fails
full-format validation; both HE and v2 log the 55,128-byte allocation failure.
The v2 observation also encounters a request error, so it is not a completed
playback validation. Separate [acceptance runs](../tests/results/esp32c3-acceptance-20260930/README.md)
record the full-rate failures and HTTP-load problems. No acoustic result is
inferred from metadata alone.

## What occupies the SBR object

The primary reference is Android's PacketVideo implementation at
[`437ced8a…`, `s_sbr_channel.h`](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/s_sbr_channel.h).
Compiling its headers with the C3 compiler and `AAC_PLUS`, `HQ_SBR`,
`PARAMETRICSTEREO` produces:

`2 × 25,792 (SBR_CHANNEL) + 4 + 4 + 3,536 (PS state) = 55,128 bytes`.

This is more than a name match: our binary requests `calloc(1, 0xd758)`,
`sbr_open` clears/advances by `0x64c0` per channel, and `ps_allocate_decoder`
uses offsets `0xc984` (PS pointer) and `0x7678` (right-channel QMF storage).
These agree with the reference layout. The **entire decoder is not identical**:
Espressif's core requirement is 35,460 bytes and its initialization allocates
several extra objects separately; the upstream monolithic core is 108,344.
Do not substitute upstream core offsets into the Espressif binary.

| Storage inside both SBR channels | Bytes | Lifetime / reuse constraint |
| --- | ---: | --- |
| Low-band QMF real/imaginary matrices, `40 × 32` each | 20,480 | Current-frame work plus prior-frame rows; cannot discard all rows |
| High-band QMF histories, six slots | 4,608 | Persists between frames |
| Synthesis filter histories `V[1152]` | 4,608 | Persists between frames, separate left/right output |
| Four smoothing-history matrices per channel | 10,240 | Persists between frames when HQ SBR uses them |
| Envelopes, gains, bandwidth state, pointer tables and other fields | 11,648 | Mixed lifetimes; must separate field by field |
| PS structure and two top-level fields | 3,544 | PS parameters/state, with pointers into reused channel storage |
| **Total** | **55,128** | Excludes the additional 1,180-byte control object |

Sizes come from the saved 32-bit reference layout; matching binary offsets above
support the identification, but are not a proof of every internal field's use.

### Reuse already present

[`sbr_applied.cpp`](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/sbr_applied.cpp)
processes ordinary stereo channels sequentially, pointing both at the AAC
coefficient workspace. The reference also overlays FFT/filter scratch and
other temporary AAC buffers. Their sizes must not be counted as fresh savings.

[`ps_allocate_decoder.cpp`](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/ps_allocate_decoder.cpp)
places PS delay/filter state in unused right-channel SBR storage. The binary's
matching offsets confirm that this reuse is present in our library too.
[`sbr_dec.cpp`](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/sbr_dec.cpp)
also uses the unused right AAC channel and coefficient area for PS matrices.
Removing the right SBR channel just because HEv2 has a mono AAC core would
overwrite live PS state and break stereo reconstruction.

### Further candidates, requiring source changes

- Replace embedded matrices with pointers and allocate large arrays separately,
  typically in 1–5 KiB blocks. This reduces the largest-request requirement but
  initially saves no payload RAM and adds allocation/pointer overhead. Splitting
  only into two 25,792-byte channels is insufficient for a 13,312-byte largest
  block, and still does not solve the total deficit.
- Separate the persistent low-band history from current-frame QMF workspace,
  then share workspace between sequentially processed channels. A conservative
  stereo design with one 10,240-byte shared matrix pair and 4,096 bytes of
  per-channel history replaces 20,480 bytes: **6,144 bytes of potential saving**.
  This is a design estimate, not an implemented result. PS already overlays
  these regions and needs a separately validated layout; it is not automatically
  a 6 KiB saving for HEv2 or every SBR mode.
- Give frame-local envelope/synthesis scratch explicit lifetimes and reuse it
  only after its last reader. Preserve inter-frame filter delays, smoothing,
  noise/bandwidth history, PS decorrelation and both output channels. Do not
  reuse caller PCM while the output queue/DMA still owns it.
- Consider mode-specific allocation without disabling any mode. A transition
  into SBR/PS must allocate full state safely; lazy allocation cannot silently
  fall back to the lower-rate core. Releasing/reallocating on every frame would
  add fragmentation and timing variability without removing persistent state.

Changing these embedded array layouts requires rebuilding all code which uses
them, including optimized routines, or a source-available compatible decoder.
Overriding `calloc` in the current binary can change placement, not layout.

## Reusing the Helix arena

[`CodecMemoryArena.cpp`](../yoRadio/src/audioI2S/CodecMemoryArena.cpp) currently
reserves 24 KiB on C3, tracks one owner and resets a bump allocator between
decoder owners. Its individual `Free` is a no-op inside the arena, and it has
no `realloc` API. With Espressif MP3/AAC selected, these unused functions are
garbage-collected from the measured ELF; there is no extra allocated Helix pool.

The linked codec routes allocations through weak `media_lib_module_malloc`,
`media_lib_module_calloc`, `media_lib_module_realloc` and `media_lib_free`.
They currently forward to libc. Espressif's
[media abstraction layer](https://github.com/espressif/esp-adf-libs/blob/master/media_lib_sal/media_lib_os.c)
also exposes memory callbacks, but that layer is not linked in this build.
This gives an integration route; the AAC configuration itself has no workspace
pointer. Pin/check the ABI instead of globally wrapping all system allocation.

A safe shared-arena implementation needs:

1. An explicit Espressif-AAC owner and adapter that routes only that decoder's
   allocations. Registration/global objects must outlive arena resets.
2. Matching zeroing, alignment, overflow, free and realloc behavior, with
   pointer/size tracking and unchanged old data if realloc fails.
3. Release only after SDK close; reset on open failure, Stop, codec changes and
   AAC configuration reopen. Test repeated same-family changes too: ignoring
   individual frees forever would exhaust a bump allocator within one session.
4. A C3-specific budget and early reservation. About 52.7 kB at open plus
   56.3 kB for SBR/control suggests **at least roughly 107 KiB for SDK state**
   in this workload, before arena margin. Including ADTS and caller PCM brings
   this near 127 KiB. These are budget estimates, not a proven universal size.
5. Enough separate heap for networking, TLS, WebUI, PCM/encoded rings, tasks and
   other codecs. Using one pool avoids two simultaneous decoder reservations;
   it does not reclaim 24 KiB that production is already using elsewhere.

The largest block after WebUI startup is only 96 KiB; a larger arena would have
to be reserved earlier. Reordering alone still leaves the measured total-RAM
shortfall. First reduce peak live storage or free additional system RAM, then
use the arena to keep that budget contiguous across station changes.

## System RAM candidates and limits

The survey finds unused stack in WebSocket status, BOOT, audio output and other
tasks, but it does **not** exercise every stack's worst path. Static workers
were largely idle. TLS, OTA, controls and every codec must run before reductions.
Keep the shared 16 KiB decoder stack: Opus previously used about 12.2 KiB.

The heap component currently occupies roughly 8 KiB of internal RAM code/data;
`CONFIG_HEAP_PLACE_FUNCTION_INTO_FLASH` is a candidate, not an accepted change.
The SDK permits it only if heap functions are not called by cache-disabled IRAM
ISRs. Smaller Wi-Fi pools also need throughput/reconnect/load A/B tests. Neither
candidate has been enabled by this investigation. Preserve the full TLS receive
record, all AAC modes and the existing user buffer setting.

## Reproduce

### Allocation lifetime trace added during implementation

`CONFIG_YORADIO_CODEC_MEMORY_TRACE=y` enables diagnostic-only replacements for
the codec's weak `media_lib_module_malloc/calloc/realloc` and `media_lib_free`
shims. The ABI was checked against the linked 2.6.2 binary and Espressif's
[media allocator declarations](https://github.com/espressif/esp-adf-libs/blob/master/media_lib_sal/include/media_lib_os.h).
The ordinary build leaves the shims unchanged. The tracer uses 64 live slots
and 64 queued events, no allocations or logging inside its hooks, and reports
overflow rather than silently accepting an incomplete trace. Event/slot arrays
cost 2,560 bytes on C3, plus small counters and a lock. INFO logging is required.

The [retained QEMU trace](../tests/results/esp32c3-aac-allocations-20260930/provenance.json)
runs the actual RISC-V decoder with full-rate HE/v2, configuration changes,
close/reopen and the existing implicit-SBR limitation check:

| Requested payload through media shims | Bytes |
| --- | ---: |
| Registration objects retained after close | 72 |
| Open AAC Plus decoder, excluding registration | 51,200 |
| Decoder after successful SBR/PS setup, excluding registration | 107,508 |
| Peak including registration | 107,580 |

The 55,128-byte SBR object and 1,180-byte control allocation are simultaneous
with the open decoder's state. All tracked per-decoder objects are released on
close; registration objects survive. No trace events were lost. These are
requested payload sizes, not the full heap budget: allocator overhead, transient
realloc copies, the ADTS wrapper, caller PCM and radio services are excluded.
This isolated run does not establish that the complete radio has enough RAM.

```sh
python3 tests/run-esp32c3-memory-trace.py
python3 tools/esp32c3_tests/allocations.py path/to/trace.log --output .build/allocations.json
```

The host test executes the real tracer and rejects overflow/missing events in
the analyzer. The real Helix/stream-format/framing regressions also passed.
Do not use trace-enabled runs as CPU benchmarks; logging changes scheduling.

### Physical heap and stack survey

Build the diagnostic radio as in [testing](ESP32C3_TESTING.md), with the added
profiler snapshots. Install only the application through OTA, then run:

```powershell
python tools/esp32c3_tests/memory.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM_PORT --output .build/c3-memory
python tools/codec_benchmark/sbr_memory_layout.py --compiler PATH_TO/riscv32-esp-elf-g++.exe --output .build/sbr-layout
```

The layout tool downloads pinned reference headers, compiles for 32-bit RISC-V,
reads DWARF member sizes/offsets and saves source hashes. It does not execute or
install that reference decoder. The hardware runner records diagnostic RAM and
stack lines, rejects AAC-core fallback, then reboots to restore the saved station.
The diagnostic app is retained under
`firmware/development/esp32c3-oled-memory-survey/app.bin`.

Before accepting any allocator/layout change, run PCM/state equivalence against
the unmodified decoder, allocation-failure cleanup, changing AAC configurations,
HE/v2 stereo at full rate, other codecs, HTTP/HTTPS, OTA and heap/CPU soak tests.
The broader acceptance gaps remain in [the testing document](ESP32C3_TESTING.md).
