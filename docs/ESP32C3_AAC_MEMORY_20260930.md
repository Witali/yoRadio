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

This investigation is now followed by the implementation results below.
The buffer changes reduce RAM use; they do not yet fix full-radio HE-AAC.

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

## Implementation: PCM and ADTS buffers

`35162f8e` reduces the caller AAC PCM workspace from 12,288 to **8,192 bytes**.
It still holds a complete 2,048-sample/channel stereo SBR frame. Before AAC
opens it also shrinks a larger buffer retained from a different codec. Other
codecs retain their 12 KiB minimum and needed-size growth. Resize failure keeps
the old allocation valid and marks the generation failed, so EOF cannot replace
the allocation error with a success status.

`d77ea5b9` replaces the always-resident 8,191-byte ADTS array with a 7-byte inline
header and one growable frame buffer. It rounds capacity to 128 bytes, caps it
at the original **8,191-byte legal frame limit**, and retains capacity until
decoder close. CRC, resynchronization and arbitrary network chunk boundaries
still work. A pending frame survives a PCM retry; failed growth preserves both
the old storage and consumed-input accounting. It does not allocate per frame
once the high-water capacity is reached.

On the six retained fixtures, requested wrapper + caller PCM payload falls by
**11,504–12,016 bytes**. This is stream-dependent, not a universal fixed saving.
At maximum ADTS capacity the new wrapper itself is 15 bytes larger than the old
wrapper; the separate 4 KiB PCM saving remains. A moving `realloc` can briefly
hold old and new input buffers simultaneously. The SDK allocation tracer does
not include this transient or either caller-owned buffer.

### Lifetime boundaries

| Owner | Allocated / first needed | Last use / release | May share with |
| --- | --- | --- | --- |
| Codec registration | Application registration | Application lifetime | Never reset with a decoder arena |
| SDK AAC state before SBR, 51,200 requested bytes | SDK open | SDK close on format change, Stop or replacement | A later mutually exclusive codec only |
| SBR/PS, 55,128 + 1,180 bytes | First extended AAC frame | SDK close | Cannot overlap live AAC core or persistent histories |
| ADTS header/frame | Header arrival; grows for validated frame size | Pending PCM retry completes; capacity freed at close | No queue/DMA alias |
| Caller PCM, initially 8,192 bytes for AAC | Before decoder creation | Frame copied to the PCM queue; buffer retained between calls | Next decoded frame after copy |
| PCM queue and PDM DMA | Output pipeline creation | Output task/DMA completes consumption | Cannot overlay decoder scratch while consumers still own it |

The new host tests execute the production allocator/framing code with injected
create, grow, shrink and SDK-open failures, maximum/CRC frames, truncated input,
and 1-byte chunks. Real Espressif-decoder QEMU tests cover LC mono/stereo,
44.1/48 kHz HE, HEv2 stereo and configuration changes. **328,770 captured stereo
frames match the previous output byte-for-byte**, including resampling/output;
an output guard checks the 8 KiB boundary. This is equivalence for the retained
fixture sequence, not exhaustive AAC-profile or internal-state coverage.

Evidence: [PCM](../tests/results/esp32c3-aac-pcm-20260930/pcm-equivalence.json),
[ADTS capacities and provenance](../tests/results/esp32c3-aac-adts-20260930/provenance.json),
[physical buffer survey](../tests/results/esp32c3-aac-adts-20260930/radio/report.json).

### Physical comparison with identical diagnostics

All three images use DIO 80 MHz, no deep sleep, the same saved audio-buffer
setting, CPU profiling and bounded SDK tracing. Stacks, TLS buffers, PCM/DMA
queues and Wi-Fi buffer counts are unchanged.

| After first process | Original free / largest | New buffers free / largest | New buffers + heap in Flash free / largest |
| --- | ---: | ---: | ---: |
| LC 48 kHz stereo | 30,092 / 11,776 | 42,476 / 22,528 | 51,572 / 38,912 |
| HE 48 kHz, SBR failed | 33,564 / 11,776 | 45,964 / 22,528 | 55,112 / 38,912 |
| HEv2 44.1 kHz, SBR failed | 33,376 / 11,776 | 46,088 / 22,528 | 55,236 / 38,912 |

Heap deltas include allocator rounding and concurrent network activity. All HE
and v2 rows are **failed full-output tests**, not reduced-rate successes. The
new buffers alone recover roughly 12 KiB on the board. Mean total CPU over the
selected stable LC windows is 36.06% baseline, 35.95% with new buffers, 36.58%
with heap in Flash. These short sequential diagnostic observations are similar;
they do not qualify production CPU, IRQ latency, long soaks or full-SBR performance.
[CPU windows and scope](../tests/results/esp32c3-aac-heapflash-20260930/cpu-summary.json).

### Heap placement experiment — not a default

The separate `esp32c3-aac-heapflash-radio` image enables
`CONFIG_HEAP_PLACE_FUNCTION_INTO_FLASH` and disables the dependent SPI-master
IRAM option. Application-entry free heap increases by **9,072 bytes**.
The pinned ESP-IDF 6.0.2 `docs/en/api-guides/performance/ram-usage.rst` and
`components/heap/Kconfig` require avoiding heap calls in cache-disabled ISRs.
The board uses I2C OLED and I2S PDM, with their IRAM-safe ISR modes disabled;
there is no application SPI-master client. Encoder handlers only sample GPIO
and post preallocated queue items and are registered with flags 0. Project heap
calls and allocation-trace dumps occur in task context. This audit applies to
this board configuration, not arbitrary ESP32 firmware or other ISR callbacks.

WebSocket reconnect and LC playback passed, but the existing 40-second HTTP-load
oracle rejected its first/last heap-window comparison. Free heap oscillated
with requests; this result alone proves neither a leak nor a cause in Flash
placement. Keep the [failed load result](../tests/results/esp32c3-aac-heapflash-20260930/load/report.json).
The option remains experimental and is **not enabled in defaults**. Even its
diagnostic HE baseline lacks room for the complete 56,308-byte SBR/control pair
plus the required network headroom, and the largest block remains too small.

The [minimal-overhead repeat with the maximum 14-block audio buffer](../tests/results/esp32c3-aac-heapflash-20260930/minimal-max-usb/report.json)
disables runtime profiling and allocation tracing, retaining INFO logs over
USB. HE and v2 still fail full-rate output. After their first decoded core frame,
free/largest RAM is **59,184 / 38,912** and **59,316 / 38,912 bytes**. Adding the
56,308-byte SBR/control payload at the first checkpoint would leave only
**2,876 bytes**, before allocator overhead, below the existing 8,192-byte free
heap budget. The largest block also fails the 55,128-byte request. The earlier
no-console attempt retained no RAM evidence and is saved as a failed survey;
it is not used for this budget. Both attempts restored the original 10-block
setting and verified Wi-Fi, playlist and all exposed settings unchanged.

The arena and internal-SBR stages therefore remain open. No early 107+ KiB pool
has been enabled: reservation changes placement but cannot satisfy an inadequate
concurrent budget. The pinned public codec package provides this decoder as a
RISC-V archive, without compatible buildable SBR implementation sources. Internal
array splitting/overlays remain blocked on those sources or qualification of a
source-available replacement with full SBR **and PS**. The current Helix LC path
is not such a replacement. Existing 16 KiB decoder stack and full TLS buffers
were retained; any further stack/pool changes need their own worst-path tests.

## Regression checks for the buffer changes

The quiet `esp32c3-aac-buffers-quiet` application uses the normal memory-placement
settings, DIO 80 MHz and no deep sleep. Firmware sources match `fb64725c`;
its ELF identity is `fdcbb41da0bf8d41b67cb6d3795f9b921cfe8d6de06d7e2ffe150f4a67fd44ec`.

- The physical [HTTP/fault/WebSocket run](../tests/results/esp32c3-aac-buffers-qualification-20260930/http/report.json)
  passes all 16 MP3/FLAC/Vorbis/Opus/AAC-LC format cases (AUTO and explicit
  codec), all five network-fault cases, reconnect and saved-station restoration.
  All six HE/v2 full-format cases still fail, consistently with the SBR budget.
- The separate [HE/v2 EOF regression](../tests/results/esp32c3-aac-buffers-qualification-20260930/eof/report.json)
  passes all six AUTO/explicit cases and restoration. Correct terminal state
  does not count as successful SBR/PS output.
- Host C callbacks, actual Helix adapter, ADTS/PCM fault injection, codec trace,
  EOF ordering and OTA parser/service tests pass. Address/undefined-behavior
  sanitizers pass on the host C paths. The selected Node suites pass 66/66;
  acceptance-oracle tests pass 16/16 and cache/profile/Quad evidence tests 19/19.
- The [initial exact-image OTA run](../tests/results/esp32c3-aac-buffers-qualification-20260930/ota-initial.json)
  passes three rejection checks, then loses network access after rejecting the
  truncated image; subsequent requests/restoration fail. USB watchdog reset
  [restores HTTP and the same app/slot](../tests/results/esp32c3-aac-buffers-qualification-20260930/ota-recovery.json)
  without rewriting flash. The saved station plays again. The connection-loss
  cause is unproven; retain this failure even if a separate retry passes.
- The [complete independent OTA retry](../tests/results/esp32c3-aac-buffers-qualification-20260930/ota-retry.json)
  passes **15/15**: invalid requests, both app slots, update during playback,
  paced upload and final restoration. ELF identity and Wi-Fi/playlist/settings
  equality are checked. This pass does not explain or erase the initial outage.

The [final snapshot](../tests/results/esp32c3-aac-buffers-qualification-20260930/summary.json)
confirms the quiet buffer-optimized image, the restored 10-block setting and
active saved-station playback. Deep sleep, allocation tracing, CPU profiling
and experimental heap-in-Flash placement are disabled in this image.

Full-plan acceptance remains open: full-rate HE/v2, the unchanged-header LC→PS
transition, a compatible internal-SBR memory rewrite, trusted HTTPS fixture
matrix, one-hour full-format soaks, exhaustive AAC/state coverage, worst-case
controls/stack/IRQ paths, the intermittent OTA connection loss and physical
stereo/OLED inspection. These results do
not qualify a source-available replacement or the experimental heap placement.

## Original full-radio heap survey, before buffer changes

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

### Physical allocation-trace baseline

The diagnostic radio from `8740af78` was installed by WebUI OTA with unchanged
Wi-Fi, playlist and settings. Its [saved survey](../tests/results/esp32c3-aac-allocations-20260930/radio-baseline/report.json)
passes LC 48 kHz stereo and fails HE/v2 full-output validation. Both failures
coincide with a rejected 55,128-byte SDK request: 33,564/33,376 bytes free,
largest block 11,776 bytes. The tracer costs 2,576 bytes of static C3 RAM;
profiler/diagnostic costs from the earlier survey remain additional overhead.

The physical library registration set retains **108 bytes** after decoder
close (the isolated AAC QEMU build retains 72). Both traces return to their
own initial registration baseline with no lost events. This confirms why an
arena must distinguish registration lifetime from decoder lifetime. The
physical SDK peak is only 51,308 requested bytes because SBR allocation fails;
it must not be mistaken for the full-SBR requirement of 107,508 decoder bytes.

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

The later [decompilation audit](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md)
also confirms **reordered fields inside SBR_FRAME_DATA**, despite matching
aggregate sizes: the imaginary low-band QMF matrix is at `0x25b0` in Espressif
versus `0x2a34` in the reference. Use the recovered field map, not reference
offsets, for any binary-level investigation. The audit records new pointer-table,
smoothing-history and PS layout candidates and the one-LSB PCM accuracy limit.

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
   in this workload, before arena margin. The original fixed ADTS and 12 KiB
   caller PCM brought this near 127 KiB; the new caller buffers reduce that part
   by the stream-dependent amounts above. These are budget estimates, not a
   proven universal size.
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
candidate is enabled in board defaults. Heap placement was tested separately
as described above. Preserve the full TLS receive
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
