# ESP32-C3 memory stability TODO

Goal: keep HTTPS radio playback reliable on the ESP32-C3 OLED board by
avoiding repeated allocation and release of large heap blocks.

## Remaining qualification work, 2026-10-09

On `codex/esp32c3-idf-upgrade`, full-rate compact AAC/SBR/PS is already
implemented; the retained PC19 PCM comparisons meet the 3-LSB allowance.
Historical unchecked items below are not all descriptions of today's code.
The remaining release work concerns the complete network/audio application:

Latest [integer-clock cross-codec qualification](ESP32C3_INTEGER_QUALIFICATION_20261009.md)
passes the HTTPS matrix and 33 codec switches. Ten-minute HE-AACv2 retains one
initial-idle TCP timeout and 11 late delayed-DMA notifications. Compare rate
compensation in the resampler against the nominal integer PDM clock before
claiming continuous AAC output. This diagnostic image does not qualify the
separately built quiet production candidate.

1. Resolve or bound heavy-FLAC input starvation and delayed DMA service.
   Compare buffering against reproducible delivery interruptions, not just
   mean CPU usage. The [integer-clock baseline](ESP32C3_FLAC_INTEGER_20261009.md)
   and [matched delivery pauses](ESP32C3_DELIVERY_PAUSES_20261009.md) retain
   nonzero DMA counters and distinguish them from acoustic measurements.
2. Choose the production TLS reserve, input-pool and prefill settings.
   Verify full 16 KiB TLS records, bounded in-playback memory use, codec
   transitions and settled Stop recovery. Recovery alone does not explain
   earlier in-playback heap-trend failures or prove allocation ownership.
3. Diagnose the intermittent WebUI TCP connection timeout. A later run
   without the timeout does not establish a repair. Keep complete traces
   and separate host transport failures from firmware faults.
4. Qualify one final quiet production configuration: all supported formats
   over HTTP/HTTPS, AAC profile/rate/channel transitions, EOF, reconnect,
   certificate failures, repeated OTA and bounded long-playback tests.
   Previous passing matrices on different experimental images do not replace
   this check. Preserve full AAC features and rates; CPU percentage alone
   remains informational.

The [exact nominal 48 kHz option](ESP32C3_PDM_CLOCK_20261009.md) separately
awaits listening or analog output-noise measurements. It remains default-off.
The AP display and WebUI Deep Sleep switch are separate feature items in the
[board TODO](ESP32C3_OLED_NATIVE_TODO.md).

The [Flash constant audit](ESP32C3_FLASH_CONSTANT_CANDIDATES_20260930.md) records
source and ELF candidates, including string copies and SDK placement limits.
Large application/codec constants are already in Flash; the listed candidates
are not implemented savings and do not yet resolve the SBR allocation deficit.

## Further memory research priorities

The [RX-only implementation and extended control tests](ESP32C3_TLS_RX_RESERVE_20261008.md)
record the optional implementation, host/link checks and remaining physical
gates. The preceding reserve image still fails the ten-minute AAC heap-trend
check; extended FLAC testing confirms task-watchdog events. Neither issue is
closed by the allocator implementation or the new audio-priority default.

The next experiments should control allocation ownership and lifetime while
preserving full AAC/SBR/PS, original sample rates, the 3-LSB PCM allowance and
all other supported codecs. These are research items, not production defaults.

1. **Reserve one large buffer specifically for TLS reception.** Reuse it for
   both small and full-sized records. The current 17,058-byte generic reserve
   can be claimed by a large handshake allocation and does not serve small RX
   allocations. Audit RX setup, cached state, retained-buffer conversion,
   errors, reset, destruction and simultaneous contexts before changing its
   owner. Derive capacity from SDK symbols and retain certificate validation
   and full 16 KiB incoming records. Measure allocation churn, CPU and peak RAM.
2. **Keep a bounded pool of compressed-audio packets.** Release only unused
   blocks above the configured minimum; preserve queued data, FIFO order and
   producer/decoder pointer leases. The optional adaptive queue is the starting
   implementation. Compare effective buffering for short packets, network
   jitter, output underruns and stop/reconnect behavior at each pool size.
3. **Reuse decoder memory between sessions where lifetimes permit it.** Audit
   every user of each region, including interior pointers, output callbacks,
   cancellation and late SBR/PS activation. Retain or reset storage only after
   the previous owner has released it; release incompatible retained storage
   before another codec or TLS handshake needs that RAM. Measure total peak
   use and fragmentation across mixed-codec switches, not just allocation count.
4. **Budget separate operating headroom for Wi-Fi, cryptography and WebUI.**
   Include allocations outside the mbedTLS hooks, DMA/alignment requirements,
   certificate verification, reconnect and OTA. Measure total free memory and
   the largest allocatable block for each required memory capability. Reserving
   TLS RAM must not cause smaller network or crypto allocations to fail.

### Allocation order experiment

Compare early placement of large, long-lived TLS/decoder buffers with the
current allocation order before short-lived network/WebUI allocations begin.
Correct allocations already occupy disjoint regions; this experiment targets
free holes between live objects. Use stack-style allocation only for scratch
whose releases are strictly last-in, first-out, or reset an entire session
arena after all its users have released their pointers. TLS, packet queues and
decoders have independent lifetimes and must not share an assumed global LIFO
order. Check peak simultaneous use, late SBR activation, mixed-codec switches,
reconnect and OTA; early reservation may reduce headroom for smaller requests.

The [startup-minimum reserve experiment](ESP32C3_TLS_RESERVE_20261008.md) uses
**17,058 bytes** for the TLS slot and releases **8,240 bytes** of input-packet
storage. Its 44-case HTTP/HTTPS file matrix records **zero allocation failures**
and **43/44 passes**. The remaining FLAC case contains an unresolved diagnostic
dump. This result supports further investigation; it does not establish full
stability or a net RAM saving. Keep the failed case and the separate WebUI
timeout in the qualification record.

For each experiment, retain an unchanged control image, exact configuration
and source hashes, peak RAM and largest-block measurements, CPU, playback
continuity and PCM quality results. Acceptance requires all-codec HTTP/HTTPS,
small/growing/full TLS records, ten-minute playback, mixed-codec transitions,
reconnect, EOF and OTA tests. CPU percentage alone is not a rejection gate;
runtime faults and output gaps remain failures.

### Next ownership measurement: copied RX packets (2026-10-08)

The [matched ten-minute runs](../tests/results/esp32c3-rxonly-long-20261008/long/summary.json)
still fail the original heap-trend gate: first/last steady-state median free
heap falls by 9,352 B with the generic reserve and 9,440 B with RX-only.
Stop restores the settled heap and largest block, but this does not identify
the allocations retained while playing. TCP uncredited payload grows to about
8 KiB; it is not allocated RAM and must not be subtracted from the heap loss.
The RX-only network snapshot series is incomplete and remains rejected.

The [copy-path audit](ESP32C3_RX_COPY_20261007.md) establishes why the existing
`esp_pbuf_allocate` tracer cannot answer this question: enabled L2-to-L3 copies
use `pbuf_alloc(PBUF_RAW, len, PBUF_RAM)` instead.

- [ ] Generate guarded, build-local copies of pinned `wlanif.c` and `pbuf.c`.
  Register successful copied-RX allocations before network handoff; remove an
  owner only in the reference-count-zero `STD_HEAP` branch immediately before
  `mem_free(p)`. A non-final `pbuf_free()` is not a release. Preserve SDK sources,
  allocation behavior, error cleanup and packet traffic.
- [ ] Verify the exact allocator mapping before querying block size. The
  current pinned configuration uses `MEM_LIBC_MALLOC=1` and no lwIP memory
  statistics prefix, so the PBUF_RAM pointer is the malloc base. Record
  `heap_caps_get_allocated_size(p)` separately from payload length and allocator
  header overhead. Reject incompatible allocator settings at build time.
- [ ] Use a fixed registry, initially 32 entries of pointer, allocated size,
  birth time and allocation ID (512 B on RV32), plus bounded counters. Record
  live/peak count and allocated bytes, oldest live age, maximum completed
  lifetime, alloc/free totals, sequence and CRC. Overflow, duplicate live
  registration and incomplete telemetry invalidate coverage. The global
  final-free hook also sees legitimate unregistered TX/control pbufs; ignore
  those rather than reporting false missing releases.
- [ ] Keep registry locking short. Query size/time before registration locking;
  copy counters under the lock and log afterward. Remove the owner before the
  actual free to prevent address reuse races. Never dereference freed pointers,
  allocate tracker entries on the heap, walk the heap under the lock or log
  packet contents. Account for tracker BSS and execution overhead separately.
- [ ] Repeat the same 600-second alternating-record HE-AACv2 test, original
  memory/runtime gates, and settled Stop recovery. Use a compact periodic
  snapshot plus post-Stop observation. Attribute measured live RX blocks and
  their lifetimes first; investigate remaining heap movement separately.

This is a diagnostic plan, not evidence that the heap decline is harmless or
that copied RX packets explain all of it. Codec precision, full TLS record
capacity and certificate verification remain unchanged.

### Clock and startup follow-up, 2026-10-09

The [initial-input-prefill experiment](ESP32C3_INPUT_PREFILL_20261009.md)
uses the same existing queue and a bounded startup wait. With fractional PDM
clocking it passes 44 HTTP/HTTPS file cases, ten-minute HE-AACv2 and three-minute
heavy FLAC load, transitions/faults and 12 mixed-codec changes. Both sustained
selected DMA windows have zero queue overruns and write errors; Stop restores
the idle heap. Defaults remain disabled. HE-AACv2 network heap/receive pairing
is incomplete and rejected, so these results do not identify RX allocation
ownership or erase the earlier failed memory experiments.

The [staged PCM tail audit](ESP32C3_PCM_TAIL_AUDIT_20261009.md) separately
reproduces retained EOF samples entering the next equal-rate stream. The source
repair passes host checks and its [hardware follow-up](ESP32C3_PCM_TAIL_BOARD_20261009.md)
passes 60 measured short-file cases, the 44-case HTTP/HTTPS matrix, sustained
HE-AACv2/FLAC, transitions and switching. Both selected sustained DMA windows
have zero overruns/write errors and settled idle memory recovers. The saved
production image is restored afterward. Fractional clock noise, analog EOF
output and the final production memory configuration still require qualification.

The [controlled-record/OTA follow-up](ESP32C3_TLS_FINAL_GATES_20261009.md)
uses this same image with explicit 1.0x record pacing. Short record/memory
gates pass, but the 16 KiB case has four post-warmup DMA queue events;
whole observed intervals also retain startup events. The ten-minute
alternating-record run is interrupted by host Windows connect error 10048
after 395.390 seconds and remains failed. Repeat it without hiding the
transport error, add staged-path starvation measurements, and compare a
bounded minimum prefill against the current early-full exit before
promoting this configuration. No listening or analog noise test is complete.
All 15 original OTA entries pass, including full HE-AACv2 over HTTPS, but
extended review retains two generic TLS errors immediately before the
explicit restoration reboot. Add safe numeric error codes and phase timing
before classifying them; the old serial-health pass is not proof of clean
TLS runtime. The previous production image and settings are restored.

## Current SDK-upgrade branch checkpoint, 2026-10-07

On `codex/esp32c3-idf-upgrade`, the ESP32-C3 defaults now select the compact
PC19 owner, smoothing history, stack-scoped low-QMF workspace, asymmetric
channel layout and late SBR activation. The linked SBR owner is **32,744 B**,
down from 55,128 B; the native adapter is 204 B, including its PC19 sidecar.
This supersedes the earlier PC18/default-selection checkpoints below on this
branch. It does not describe `main` or qualify every public radio stream.

The current production precision allowance is **3 output PCM LSB**. Retained
compact-corpus measurements reach 2 LSB; the historical 1/2/5-LSB decisions
below remain records of their original experiments. Full SBR/PS and original
output rates remain required. See the
[SDK qualification report](ESP32C3_IDF_UPGRADE_20261007.md) and
[ICY/RX memory follow-up](ESP32C3_ICY_RX_MEMORY_20261007.md).

The remaining network-memory gates are separate from compact PCM quality:

- [x] Reduce the ICY metadata parser's static RAM: 3,888 B measured in the
  linked quiet image, with fragmented-input and physical title/audio tests.
- [x] Compare RX copying under a ten-minute HEv2/WebUI load. Copying eliminates
  the observed allocation failures in that run, but the original heap-decline
  gate still fails; retain both findings.
- [ ] Qualify full-sized TLS records after the decoder and receive queues are
  active. The [controlled TLS record test](ESP32C3_TLS_RECORD_MEMORY_20261007.md)
  passes 1 KiB records with both allocators, but dynamic 16 KiB records fail a
  16,749-byte allocation and permanent buffers suffer 167 small-block allocation
  failures across the three large-record modes. Small-record success is insufficient.
  The [four-segment TCP window follow-up](ESP32C3_TCP_RX_WINDOW_20261007.md)
  removes allocation failures in the dynamic run, but alternating records still
  fail the original heap-trend gate; static TLS retains three allocation failures.
  Keep the overlay optional until phase-aware/ten-minute and throughput checks.
  The [600-second follow-up](ESP32C3_HTTP_TLS_PHYSICAL_20261007.md) now
  reproduces a real failure at 270.906 s: 16,749 B requested, 27,756 B free,
  15,360 B largest block. RX4 is therefore not a production memory fix.
  The optional RX6 window passes a public MP3-256 minute that failed on RX4,
  but still has failing heap-trend gates and needs long-load qualification.
  The [retained RX experiment](ESP32C3_RETAINED_TLS_RX_20261008.md) avoids
  per-record large allocation but fails small network allocations instead:
  181 failures across eight framing cases and 51 in the interrupted soak.
  Keep it disabled. The active qualification target is the pinned latest
  `release/v6.1` revision `9a97f6c54ec6`, rather than the original release tag.
  Its [physical follow-up](ESP32C3_IDF61_REVISION_20261008.md) passes all 44
  HTTP/HTTPS file cases and four public AAC minutes, but the alternating-record
  run again fails a 16,749-byte request: 27,040 B free / 15,360 B largest.
  RX6 is still not a complete memory fix. A separate MP3 WebUI timeout also
  requires diagnosis; no decoder/allocation fault was recorded in that window.
  The [static Wi-Fi RX4 experiment](ESP32C3_WIFI_STATIC_RX_20261008.md) frees
  about 3.3 KB and passes 75 seconds, but its longer repeat fails at 30.515 s:
  16,749 B requested / 27,248 B free / 15,872 B largest. Keep it optional.
- [ ] Test a dedicated, early-placed TLS RX allocation block on the pinned
  SDK, so unrelated allocations cannot split the next full-record buffer.
  First audit every dynamic RX allocation and free path, including setup,
  error cleanup, retained-RX conversion, context destruction and concurrent
  TLS contexts. Derive capacity from SDK symbols, retain a heap fallback for
  additional contexts, and do not change certificate validation, full record
  capacity or AAC features. This is a placement experiment, not a claimed
  RAM saving; repeat the failing record-growth case and all codec/OTA gates.
  The [static-slot implementation](ESP32C3_TLS_RESERVE_20261008.md) and host/link
  audits are complete behind an off-by-default option. Its late-reclamation
  image passes all four paced record modes for 75 seconds each, but fails all
  eight framing cases and 13/44 file cases through smaller allocation failures.
  The startup-minimum follow-up funds the reserve before input packets arrive;
  framing improves to 8/8 and files to 43/44, with zero captured allocation
  failures. The remaining FLAC case has an unresolved nonfatal diagnostic dump;
  a small-record WebUI timeout passes a timed repeat but remains unexplained.
  Retain the separate results and keep production qualification open.
- [ ] Qualify the optional [adaptive input queue](ESP32C3_ADAPTIVE_INPUT_TLS_20261008.md):
  reclaim only idle packet slots above a configured minimum when mbedTLS needs
  memory, preserving queued bytes and outstanding leases. It is implemented
  behind an off-by-default build option; host ownership/concurrency and linked
  allocator checks pass. Two physical full-record tests still fail at about
  five seconds. The repeat confirms four idle slots (8,240 B) are released,
  with 33,920 B free but only a 12,288-byte largest block for a 16,749-byte TLS
  request. Preserve the feature as an optional experiment; physical TLS,
  all-codec and continuity gates remain.
- [ ] Compare the RX-only reservation with an isolated allocator for all
  mbedTLS allocations. The pinned SDK exposes `MBEDTLS_CUSTOM_MEM_ALLOC` and
  `mbedtls_platform_set_calloc_free()`; install the allocator before the first
  crypto/TLS allocation and retain it for every matching free. Measure peak
  live bytes, largest requests, allocator overhead and retained crypto state
  during handshake, certificate verification, playback, reconnect and OTA
  before choosing a capacity. A measured sample peak is not a bound for every
  certificate chain or concurrent connection. Keep a separate full-record RX
  slot so small TLS allocations cannot fragment that required contiguous block.
  Check full record capacity and normal certificate validation in every test.
  This remains a proposal; no private allocator is enabled by this audit.
  - The hook does **not** cover all memory needed by HTTPS: pinned
    `esp_tls.c`/`esp_tls_mbedtls.c` also use libc allocations; the PSA AES/GCM
    driver uses `malloc`, and the SHA driver uses `heap_caps_malloc` with
    `MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL`. Audit the enabled driver paths and
    their frees/alignment separately, as well as socket/network buffers.
    Do not claim complete TLS reservation based only on mbedTLS hook counters.
  - Do not implement transparent relocation of existing library allocations.
    The SDK's `components/heap/tlsf/tlsf.c::tlsf_free` already merges adjacent
    free blocks using `block_merge_prev/next`; it cannot join holes separated
    by live allocations without moving them. Moving live C objects requires
    updating every alias/interior pointer and respecting hardware ownership.
    Handles or offsets could support compaction in a separately owned data
    structure, but are not a drop-in replacement for TLS, Wi-Fi or DMA buffers.
  - Reference: [mbedTLS allocator hooks and static-buffer allocation](https://mbed-tls.readthedocs.io/en/latest/kb/how-to/using-static-memory-instead-of-the-heap/).
    Reserving RAM changes ownership and placement, not total RAM capacity;
    also measure the remaining codec/network/WebUI headroom.
- [ ] Resolve contiguous allocation with full TLS buffers. The static-TLS
  follow-up has 35,640–40,020 B free at three failed 32,744-byte SBR requests,
  but only 25,600–29,696 B in the largest block. Audit allocation order before
  testing an early **compact-sized** reservation; the old early-reserve switch
  requests the original 55,128-byte structure and is incompatible with this
  compact configuration. Do not enable that old switch as a shortcut.
- [ ] Repeat all public LC/HE/mono-HE/MP3 cases, ten-minute load, mixed-codec
  switches, late SBR/PS, EOF and OTA during playback on the final memory fix.
- [x] Reproduce and contain fatal TLS read errors after a positive partial HTTP
  read. The alternating-record test logs a second 46,622-byte request after
  allocation failure; its exact error-state cause still needs targeted proof.
  The [RFC audit and reader guard](ESP32C3_HTTP_TLS_RFC_AUDIT_20261007.md)
  now reproduce/prevent the extra read in both SDKs (85 updated host cases each
  plus 37 retained stream-task cases). The physical TLS allocation failure
  terminates with read failure and does not repeat the older large request.
- [ ] Resolve the RFC audit's remaining HTTPS closure gaps: distinguish TLS
  `close_notify` from raw EOF below HTTP, verify outbound closure/alert behavior,
  and cover truncation and certificate identity with actual TLS fixtures.
  Incoming raw EOF/clean close and complete/incomplete HTTP framing now pass
  eight physical cases; outgoing alerts and identity-negative fixtures remain.

## Physical AAC findings, 2026-09-30

**2026-10-03 follow-up:** the [four-row smoothing adapter](ESP32C3_AAC_SMOOTHING_ADAPTER_20261003.md)
reduces the SBR allocator block to 47,104 bytes (8,192 below original), passes
14/14 local format cases and installs successfully by OTA. Public HE-AAC still
fails HTTP/HTTPS load tests with allocation errors. Keep this goal open and
continue the low-QMF/PS ownership work; short local success is not full-radio
qualification. The saved Groove Salad 16 capture has no active PS according to
both FAAD modes; use ABBA/synthetic HEv2 for PS execution coverage.

See the [hardware report](ESP32C3_CACHE_HARDWARE_20260930.md). Isolated full-rate
AAC passes on this board, but the full radio has a separate heap limitation:

- [x] Reproduce the initial AAC-LC failure: a 12,288-byte allocation fails with
  14,848 bytes free and only 7,680 bytes in the largest block.
- [x] Disable Wi-Fi IRAM/RX IRAM speed optimizations for this C3 profile,
  freeing about 19 KiB; verify real 48 kHz stereo LC streaming with Wi-Fi,
  OLED updates, PDM output and WebUI polling.
- [ ] Make room for the additional **55,128-byte contiguous SBR allocation**,
  while keeping enough heap for Wi-Fi, WebUI and TLS. With the RAM-saving
  build it still failed with 27–36 KiB free and 8–16 KiB largest blocks.
- [ ] Prevent silent full-AAC degradation or clearly report it: the library
  fell back to 24 kHz stereo for HE-AAC and 22.05 kHz mono for HE-AAC v2 despite
  `CONFIG_YORADIO_AAC_PLUS=y`. This is not a configured frequency cap.
- [ ] Repeat full-rate HE/v2 playback, in-stream format transitions and total
  CPU measurements after the memory fix. Isolated decoder results do not prove
  that the complete radio can allocate the same decoder state.
- [ ] Repair late implicit SBR/PS activation with identical ADTS headers. The
  [flag-only QEMU experiment](ESP32C3_AAC_CONTINUITY_REJECTION_20261001.md)
  crashes and is rejected. Audit late SBR initialization and output contracts;
  retain AAC transform history and compare actual PCM.

Do not reduce the shared 16 KiB decoder task stack blindly: the retained Opus
benchmark used about 12.2 KiB. A fix must preserve other codecs and user settings.

The [2026-10-01 conservative IRAM test](ESP32C3_CONSERVATIVE_IRAM_20261001.md)
recovers 3584 bytes with Auto Suspend disabled. Clean-start AAC and 15 OTA gates
pass, but HE/v2 fail in the first of three mixed-codec cycles: SBR requests 55128
bytes with 75632–79340 bytes free and a largest block of 47104. Later cycles pass;
settled idle heap recovers. The subsequent [heap/TCP trace](ESP32C3_HEAP_LAYOUT_20261001.md)
identifies a 168-byte TIME_WAIT PCB splitting the large region. The
[optional RTC PCB pool](ESP32C3_TCP_PCB_POOL_20261001.md) passes 21/21 switches
with full SBR/PS but is rejected after two ownership assertions during OTA.
HTTP success after an automatic reboot does not qualify OTA. Bounded pool history and a serial-health
gate are available. The static WebUI workers have only 448/564 bytes of observed
unused stack during OTA negative tests; keep their current stack sizes.

The [half-close correction](ESP32C3_LWIP_HALF_CLOSE_20261001.md) reproduces the
ownership error in real lwIP with both allocators and passes six fixed host
scenarios for each. The fixed physical image passes all 15 repeat OTA checks
with no serial panics or extra resets, and 21/21 mixed-codec switches with full
SBR/PS. HTTPS/load/soak, implicit AAC transitions and physical RTC sleep gates
remain open; the pool stays optional pending broader qualification.

The subsequent [public radio HTTP/HTTPS load test](ESP32C3_PUBLIC_HTTPS_20261001.md)
passes AAC-LC and MP3 but reproduces full HE/v2 failures on real streams. HTTPS
has only 39892–41888 bytes free when SBR requests 55128; HTTP has about 60 KiB
free but a largest block of 53248 bytes. Both continue with reduced core PCM.
Keep total RAM and fragmentation as separate open problems; the local 21/21
switch result does not qualify this workload. Settings and idle heap recover.
With one-second HTTP polling after a reboot, full HE 44.1 kHz starts, but later
1700-byte allocations fail and sampled free/largest RAM falls to 6232/1728 bytes.
The next fix must preserve operating headroom after SBR allocation as well as
make its initial allocation possible.

## Current compact-owner checkpoint, 2026-10-03

The [PC18 production-adapter test](ESP32C3_AAC_HIGH_ADAPTER_20261003.md) reduces
the owner request to 47,980 B and the measured unguarded block to 49,152 B
(6,144 B less than the original, including lossless table/PS changes). Per-decoder
high-history state adds 16 B. QEMU PCM, reset, concurrent tasks and fail-closed
SBR allocation tests pass; an awake app-only OTA also passes on the board.

Public HTTP/HTTPS HE-AAC still fails under network/WebUI load: requests as small
as 1,700 B cannot fit despite several KiB of aggregate free heap. HTTPS can also
fail the compact owner allocation. Preserve both the initial contiguous-owner
budget and sustained network/TLS headroom as open requirements. Do not enable
this experimental profile by default or treat reduced/stalled PCM as a pass.
Continue the audited smoothing/QMF storage checklist in
[memory experiments](ESP32C3_AAC_MEMORY_EXPERIMENTS_20261002.md), then repeat
physical mixed-codec, CPU, EOF, OTA and sustained-playback checks. The remaining
large-area estimates are not measured savings yet.

## AAC memory reuse during decoding — planned, 2026-09-30

The [AAC decompilation audit](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md)
recovers 176 linked functions and documents RAM candidates. Preserve the complete
existing format/tool support; as updated by the user on 2026-10-01, the limit is
**±2 output PCM LSB per sample/channel**, with **±5 LSB temporarily permitted
during development**. Historical one-LSB experiment reports
retain their original thresholds. Layout-only changes should remain byte-identical.
The final speed target is no decoding slowdown versus the unmodified decoder
within measurement variability. A temporary slowdown is allowed during RAM
optimization, with a measured regression and an explicit follow-up to recover
speed while preserving full format support and the two-LSB output limit.

- [ ] **Do not cap AAC output at 22/22.05 kHz.** Preserve the stream's full
  decoded sample rate, including SBR reconstruction to 44.1/48 kHz and all
  other supported rates, in both floating-point and fixed-point backends.
  Memory or CPU optimizations must not introduce downsampling or AAC-core
  fallback; verify the actual PCM rate as well as OLED/WebUI metadata.
- [x] Decompile the shipped decoder, verify critical allocations/offsets against
  disassembly and save reproducible evidence. Probe reference pointer-table
  compaction on RV32: 55,128 → 53,240 bytes; no decoder change executed.
- [x] Download pinned FAAD2 and compare fixed/full-complex SBR/PS scaling on
  matching inputs. The [60-case host study](FAAD2_HISTORY_SCALING_20261001.md)
  reaches 2 LSB real / 3 LSB synthetic for its fixed history scope, within the
  temporary ±5 limit. It does not establish C3 RAM/CPU viability or qualify the
  final ±2 limit. Global rescaling alone does not add mantissa precision.
- [ ] Add the requested compact-storage build option, enabled by default for
  development, once an actual memory-saving implementation passes the ±5 gate.
  The QEMU pack/restore switch currently saves no heap and is not that option.
- [x] Compare pristine FAAD float32 and fixed PCM on the same LC/HE/v2 corpus:
  [baseline arithmetic comparison](FAAD2_FLOAT_FIXED_COMPARISON_20261001.md),
  22 main decodes plus 22 repeatability controls. This is distinct from the
  additional error of history compression against the same arithmetic backend.
- [ ] Isolate the sustained synthetic SBR differences (up to 7678 PCM LSB) and
  PS-onset transient (10211 LSB) between pristine FAAD float and fixed paths;
  compare against an independent reference before accepting a backend change.
- [x] Select `shift=exponent+1` (1..16) for 16+16 mantissas with eight independent
  four-bit exponents per word. Add block pack/unpack and verify arithmetic,
  rounding, saturation, nibble isolation and tails under UBSan. See the
  [PC16 range decision](ESP32C3_AAC_PC16_SHIFTS_20261001.md).
- [x] Measure PC16 on retained SBR/PS histories: [201 QEMU comparisons](ESP32C3_AAC_PC16_QUALITY_20261001.md)
  pass temporary ±5 LSB but retain three-LSB errors, failing the final ±2 gate.
  Block and scalar statistics match; the synthetic maximum improves from 7 to 3.
- [ ] Qualify actual allocation reduction and physical C3 CPU cost before enabling
  PC16 storage, and remove the remaining final-precision exceedances.
- [ ] Verify actual PS activation when labelling streams: the Groove Salad
  16 kbps capture is mono without PS in FAAD2, while the current C3 backend
  duplicates it to stereo. FFprobe's HE-AAC v2 label alone does not prove PS.
- [ ] Obtain/build a compatible full-feature source backend; account for the
  confirmed Espressif/reference SBR field-order differences before layout edits.
- [x] Test the supplied FAAD2 14+14+4 PS-storage patch at its actual write points:
  [33 host decodes](FAAD2_PS_PATCH_QUALITY_20261001.md) reach 2 LSB on both active-PS
  inputs, keep the disabled build bit-identical and reduce the host PS structure
  by 9600 bytes. Xsbr is unchanged. This is not yet an ESP32-C3 backend port or
  full-format/peak-heap/speed qualification.
- [x] Port FAAD-style PS packing to the current Espressif decoder's actual delay
  writes: [81 paired QEMU comparisons](ESP32C3_AAC_PS_WRITE_PORT_20261001.md).
  Native-source controls are bit-identical; packing reaches 3 LSB and passes
  temporary ±5, but fails final ±2. The 617-pair payload shrinks by 2468 bytes;
  the 55,128-byte owner is unchanged, so heap saving remains zero.
- [ ] Qualify packed PS reset/reconfigure and repeated stereo/PS transitions,
  reclaim owner storage without breaking its right-SBR aliases, and remove the
  remaining three-LSB errors. Recover the measured +26.681% / +40.658% guest
  instruction regression on synthetic HEv2 / ABBA before physical acceptance.
- [ ] Compact smoothing pointer tables (1,888-byte candidate), then validate
  full-format output, reset paths and PS aliases.
- [ ] Separate stereo low-band QMF work from retained histories (6,144-byte
  conservative candidate), with a separately verified PS layout.
- [ ] Evaluate retaining four smoothing history rows plus existing current
  vectors (2,048-byte candidate), preserving all five filter taps.
- [ ] Allocate PS control on demand (up to 3,536 bytes while PS is absent),
  preserving PS appearing later in a stream and transitions in both directions.
- [ ] Replace the unused right SBR channel in PS mode with compact PS-specific
  state (16,004-byte upper bound before retained control/alignment, not a proven
  saving). Preserve both synthesis histories and every PS delay/filter state.
- [ ] Use genuine synthesis history rings and explicit scratch lifetimes;
  measure the saving. Do not simply shrink the existing 12 KiB scratch block.
- [ ] Narrow stored smoothing exponents to 16 bits only after proving their
  ranges (2,560-byte candidate for the original two-channel layout).
- [ ] Prototype **24-bit signed QMF mantissas with a shared block exponent**
  after the failed BFP16 gate: 15,440 versus 20,480 bytes, a 5,040-byte
  storage saving for one byte of exponent per 32-complex-sample row. Compare
  smaller blocks, include unpacking workspace and measure output error/CPU.
- [x] Evaluate 16-bit QMF mantissas with shared exponents at the real decoder's
  analysis boundary in QEMU. **Rejected by the one-LSB PCM gate:** 32/8/1-subband
  groups reach 5,689/342/3 LSB respectively across HE/v2 fixtures. Controls are
  byte-identical. The prototype saves no RAM; the 10,160-byte row-storage saving
  remains hypothetical. See the [experiment and retained tests](ESP32C3_AAC_BFP16_20260930.md).
  [Real-radio captures](ESP32C3_AAC_BFP16_REAL_20260930.md) confirm the failure:
  finest blocking still reaches 3 LSB, with 0.925–1.383% of HE/v2 samples above
  one LSB; per-channel error distributions and repeated-run statistics are saved.
- [x] Qualify **14+14+4 complex history** separately for SBR, PS and both, using
  nearest and floor/midpoint reconstruction. **Rejected even at ±2 LSB**: maxima
  are 3 LSB on real recordings and 7 LSB on synthetic HE-AAC v2. The saved
  [experiment](ESP32C3_AAC_PACKED_HISTORY_20261001.md) includes 201 paired tests,
  error/quantizer statistics, controls and instruction counts. Actual RAM saved
  is zero; 4,788 bytes is only the potential history payload saving before
  workspace/layout changes. Keep production disabled and investigate wider or
  selectively wider storage before implementing a stage-local cache.
- [ ] Recover speed for any precision-qualified compact representation: fuse
  scans with QMF production, unpack only active work, then repeat A/B and board
  tests. BFP16's diagnostic pack/unpack adds roughly 3.4–8.0% median QEMU guest
  instructions per tested HE/v2 case; this is not physical CPU timing.
- [ ] Compare densely packed custom float24 and fixed-point int24 storage
  (5,120-byte storage saving each). Specify sign/exponent/fraction allocation
  for float24; 24 storage bits do not imply 24 significant bits. Keep integer
  processing where possible and account for conversion/packing cost on C3.
- [ ] Investigate exact packing of bounded flags, counters and relative offsets;
  preserve their ranges and ownership. Quantify savings separately.
- [ ] Explore lossless delta/residual compression of inactive history blocks
  only with a bounded raw fallback and complete peak-memory accounting. Do not
  rely on average compression to fit every stream; plain mu-law/A-law does not
  establish the required two-LSB accuracy.
- [ ] Split large arrays into smaller allocations and evaluate a common codec
  arena as detailed below. These address fragmentation/ownership, not payload
  size by themselves; the optional Helix arena is not reclaimable resident RAM.
- [ ] Benchmark every RAM candidate against the original decoder on matching
  inputs and settings: time/cycles per audio second, tail/maximum decode-call
  latency, total CPU and underruns, including copy/packing costs. Record each
  temporary slowdown by profile and percentage; create and complete a targeted
  speed-optimization follow-up, then repeat A/B to confirm recovery. Keep QEMU
  estimates separate from physical C3 results; core-only fallback is not a
  valid speed baseline for full SBR/PS.

The estimates above are **unimplemented candidates**, not measured production
savings. They overlap and must not be summed: QMF representations are mutually
exclusive, workspace sharing changes the amount left to pack, and PS uses a
different layout. See the [representation comparison](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md#qmf-storage-representations-float24-and-shared-exponents)
for assumptions, rounding/phase risks and the required accuracy/speed checks.

### Execution plan and decision gates

Status: **partially implemented; full-rate HE/v2 still fails on the radio**.
Bounded SDK tracing, an 8 KiB AAC PCM workspace and adaptive full-size ADTS
storage are implemented and committed. Real-decoder QEMU output is byte-identical
to the previous capture; physical surveys recover roughly 12 KiB. An additional
heap-in-Flash experiment recovers 9,072 bytes but is not qualified or enabled by
default. See [implementation evidence and limitations](ESP32C3_AAC_MEMORY_20260930.md#implementation-pcm-and-adts-buffers).
The baseline is the fixed EOF application
from `69410cd5`, archived and tested in `1bfc8b64`: DIO 80 MHz, no deep sleep,
Espressif AAC Plus, no PSRAM. The [EOF correction](ESP32C3_EOF_STATUS.md) is
complete; it does not resolve SBR memory allocation. Keep its regressions passing.

**Objective:** full-rate AAC-LC, HE-AAC v1 and HE-AAC v2 in the complete C3 radio,
with both output channels and all existing supported rates/bitrates preserved.
Do not obtain a memory saving by imposing a 22/24 kHz ceiling, disabling SBR/PS,
forcing mono, or replacing production AAC with the current LC-only Helix path.

The [measured allocation map](ESP32C3_AAC_MEMORY_20260930.md) is the starting
point, not a universal capacity calculation:

| Item | Recorded size / estimate | Planning consequence |
| --- | ---: | --- |
| SBR object plus control object | 55,128 + 1,180 bytes | The shipped binary needs the first object contiguous |
| Free heap at the measured failure | 36,192 bytes; largest block 13,312 bytes | Recover at least the 20,116-byte arithmetic deficit **plus** operating headroom; also address fragmentation |
| SDK state with SBR | Roughly 107 KiB before margin | Budget estimate, not a proven arena size for every stream |
| SDK state, ADTS wrapper and caller PCM | Roughly 127 KiB before margin | These allocations coexist; moving them into one pool does not reduce their total |
| Existing C3 Helix arena capacity | 24 KiB | Not resident in the production Espressif build; cannot count it as reclaimable RAM |

Proceed in this order; keep each accepted change and its evidence in a focused
commit. Record rejected candidates as well as improvements.

1. **Establish the peak live allocation budget.**
   - [ ] Trace allocation size, owner, lifetime and peak overlap through decoder
     open, first LC/SBR/PS frame, format changes, EOF, Stop and close. Use bounded,
     preallocated trace storage; do not allocate from the hook being measured.
   - [ ] Distinguish persistent history, frame-local scratch, input framing,
     caller PCM and queued/DMA-owned output. Separate decoder-owned allocations
     from registration/global objects that survive decoder close.
   - [ ] Measure total free RAM, largest block, stack margins and transient TLS/
     WebUI/OTA demand on the physical board, including the largest selectable
     audio buffer. Record instrumentation overhead and remeasure the quiet build.
   - Gate: save a lifetime diagram and a worst-observed concurrent budget. Do
     not add all allocation sizes together or count already shared memory twice.

2. **Recover RAM outside SBR before reserving a large arena.**
   - [x] In `audio_service.c`, evaluate an AAC-specific initial caller PCM
     workspace of 8,192 bytes instead of the shared 12,288-byte default: a
     saving of 4,096 requested bytes. AAC also shrinks a retained larger
     workspace after the previous decoder closes. Host checks cover transitions,
     grow/shrink failure and preservation of the old buffer; other codecs retain
     their capacity and needed-size growth. The real decoder's LC/HE/v2 QEMU
     output (328,770 stereo frames) matches the previous capture byte-for-byte
     with 8 KiB PCM plus an overrun guard. [Evidence](../tests/results/esp32c3-aac-pcm-20260930/pcm-equivalence.json).
     This alone cannot close the measured deficit; physical qualification follows.
   - [ ] Check bounded-output support before attempting smaller PCM chunks.
     The current adapter requires a complete 8,192-byte SBR stereo frame. Preserve
     the ability to receive legal ADTS frames up to the existing 8,191-byte limit;
     reducing a constant or splitting a network read is not a framing solution.
     Implemented adaptive ADTS storage: a 7-byte inline header, checked growth
     rounded to 128 bytes and capped at the original 8,191-byte frame limit.
     Capacity is reused until close, including PCM retries; OOM preserves the
     buffered header and returns an error. Host tests cover maximum/CRC frames,
     1-byte chunks, failed create/grow/open and truncated-frame cleanup. The
     real LC/HE/v2 QEMU output remains byte-identical to the fixed-buffer baseline.
     [Per-fixture capacities and provenance](../tests/results/esp32c3-aac-adts-20260930/provenance.json).
   - [ ] Audit system RAM candidates separately: stack reductions only after
     worst-path measurements, heap-function placement in flash only after a
     cache-disabled/ISR call audit, and Wi-Fi pool changes only with throughput,
     reconnect and concurrent WebUI tests. Preserve the shared 16 KiB decoder
     stack, full TLS receive capability and the user's buffer setting.
   - Gate: quantify actual peak savings. The already disabled Wi-Fi IRAM options
     and existing scratch overlays are baseline savings, not new gains.

3. **Prototype a common codec arena with correct ownership.**
   - [ ] Reuse the Helix arena's single-owner concept for Espressif AAC; avoid
     reserving independent pools for mutually exclusive decoder owners. Pin and
     verify the media allocator ABI and route only the intended allocations.
   - [ ] Implement alignment, zeroing, overflow checks, individual frees and
     realloc semantics, including preservation of old data on realloc failure.
     The existing bump allocator with no-op free is insufficient for repeated
     AAC reopen/configuration changes within one session.
   - [ ] Keep long-lived registration objects outside resets. Transfer ownership
     only after decoder close and release of all consumers; test open failure,
     repeated LC/HE/PS changes, Stop, cancellation and switching to other codecs.
   - Gate: reserve a measured budget early enough to avoid fragmentation **only
     once it fits the concurrent system budget**. An early reservation prototype
     may measure placement; it must not starve networking or be called a RAM saving.

4. **Reduce decoder-internal storage where source access permits.**
   - [ ] Obtain buildable compatible source or evaluate an equally capable
     source-available decoder. Rebuild all users of changed structures, including
     optimized routines. Allocator interception cannot split the shipped
     `SBRDECODER_DATA` object, whose fields are accessed at fixed offsets.
   - [ ] Separate persistent low-band QMF history from frame-local work; evaluate
     one workspace for sequential stereo channels. The investigation estimates
     **6,144 bytes** of potential ordinary-stereo savings, not a measured result
     and not an automatic saving for HEv2/PS.
   - [ ] Map a separate PS-safe layout: the right SBR channel already holds live
     PS state for a mono AAC core. Preserve filter delays, smoothing history,
     overlap, decorrelation and both output channels across frames.
   - [ ] Evaluate splitting large embedded arrays into smaller blocks and sharing
     envelope/synthesis scratch after its last reader. Splitting alone saves no
     payload RAM; never overlay input or PCM still owned by a queue/DMA consumer.
   - Gate: prove lifetimes and equivalence before combining optimizations. Do not
     add the estimated PCM and QMF savings unless they coexist in the same build.
     If compatible source is unavailable, retain internal-layout changes as blocked
     work; do not patch binary offsets or substitute an LC-only decoder.

5. **Prove compatibility and failure handling.**
   - [ ] Compare optimized PCM and persistent state with the unchanged same
     decoder, bit-exactly where applicable. Use FFmpeg/FDK for independent profile,
     layout, duration and drain checks; different decoder PCM is not assumed exact.
   - [ ] Cover LC/HE/v2, distinct left/right audio, window sequences, supported
     rates/bitrates and actual input paths; add missing fixture coverage explicitly.
     Test truncated/malformed input, allocation failure at every stage, failed
     realloc, backpressure, cancellation, reset, EOF and repeated owner changes.
   - [ ] Require correct LC -> SBR/PS transitions, including unchanged ADTS core
     headers. The existing detection/reopen limitation is a separate acceptance
     item; lower RAM consumption does not automatically fix it.
   - Gate: full decoded rate/channels and truthful OLED/WebUI metadata. AAC-core
     fallback is a failure of HE/v2 acceptance, even if audio and EOF still work.

6. **Qualify the complete radio and retain the result.**
   - [ ] Run the [C3 acceptance suites](ESP32C3_TESTING.md): HTTP and trusted
     HTTPS matrices, format transitions, EOF, faults, switching/heap recovery,
     WebSocket, concurrent load, one-hour LC/HE/v2 soaks and exact-image OTA.
     Recheck MP3, FLAC, Vorbis and Opus and inspect physical stereo output/OLED.
   - [ ] Compare total and decoder CPU, peak call time, RAM/largest-block minima,
     task stacks and actual underruns against the baseline. Use the existing
     published budgets; predeclare any additional regression limit before A/B.
     QEMU helps isolate decoder behavior but does not qualify full-radio memory,
     Wi-Fi, TLS or real-time output.
   - [ ] Save source/library/configuration hashes, allocation maps, failed and
     passing results, and successful test images under `firmware/development/`.
     Update manifests/changelog and preserve Wi-Fi, playlist and user settings.
   - Completion gate: full-rate HE/v2 works with the normal radio services and
     sustained load, all supported formats remain available, and the tests pass.
     A larger arena, isolated decode or a few saved KiB alone is not completion.

### Existing findings and detailed checklist

The [RAM/SBR investigation](ESP32C3_AAC_MEMORY_20260930.md) now maps the 55,128-byte
object, verifies existing PS reuse against the binary, and measures the full
radio. The 24 KiB Helix arena is not allocated in the current Espressif build.

- [x] Measure startup/AAC heap phases and task stack margins on physical C3.
- [x] Identify SBR channel/PS storage and already shared scratch using pinned
  primary source, a 32-bit layout probe and actual binary offsets.
- [ ] Prototype an Espressif-AAC adapter for the common codec arena, with
  free/realloc and complete cleanup across AAC configuration changes. Budget
  roughly 107 KiB for observed SDK state before margin, not the existing 24 KiB.
  First recover the measured total-RAM shortfall; reservation alone is no fix.
- [ ] Evaluate source-level separation of SBR persistent history and shared
  QMF scratch, including a distinct PS-safe lifetime map. Splitting an embedded
  array requires rebuilding its users; an allocator override cannot do it.

- [ ] Reduce peak AAC memory by reusing buffers whose lifetimes do not overlap,
  using the ESP8266 implementation as a reference. **Preserve the full AAC
  feature set; do not trade supported formats for lower RAM use.**

Reference: [ESP8266 bounded PCM output](ESP8266_AAC_PCM_BLOCKS.md),
[`AACDecodeBlocks`](../yoRadio/src/audioI2S/aac_decoder/aac_decoder.cpp), and the
[native ESP8266 bridge](../esp8266/rtos-sdk-native/components/helix_codecs/codec_bridge.cpp).
That implementation emits reusable PCM blocks and updates each overlap word
only after its last use for the current output. The selected 512-frame mono
profile saves 3,072 bytes, with about 6.1% more decoder time in its measured
workload. Stereo needs more PCM space. Neither the saving nor the CPU cost is
an estimate for C3.

The existing block API is guarded by `YORADIO_ESP8266_NATIVE` and excludes
`AAC_ENABLE_SBR`. C3 production uses Espressif `esp_audio_codec` 2.6.2, whose
decoder internals are supplied as a precompiled RISC-V library. Switching to
the current Helix AAC-LC-only path would lose HE-AAC functionality and is not
an acceptable implementation of this optimization.

### Investigation

- [ ] Map the peak live allocations of ADTS input, PCM, spectral/IMDCT scratch,
  overlap history, SBR and parametric stereo (PS). Share only temporary storage
  with disjoint lifetimes; preserve both channels and persistent decoder state.
  Do not reuse memory while output/DMA still owns it.
- [ ] Evaluate smaller reusable PCM blocks through the Espressif API before
  considering decoder-internal changes. The current
  [C3 adapter](../idf/esp32c3-oled-native/main/native_aac_decoder.c) requires an
  8,192-byte output to keep one SBR stereo frame atomic and reserves 8,191 bytes
  for a complete ADTS frame. Check bounded output and input sizing without
  truncating legal frames, losing pending PCM, or corrupting retry/progress
  accounting and format changes.
- [ ] Check whether supported allocator/workspace APIs permit shared scratch.
  If internals must change, establish source/API access or evaluate an equally
  capable decoder; do not assume ESP8266 source changes apply to the binary SDK.
- [ ] Measure peak live RAM **and the largest contiguous block**. A reusable
  arena can reduce fragmentation but cannot by itself remove a simultaneously
  needed 55,128-byte SBR allocation. Quantify the remaining shortfall after each
  change; a few KiB saved in PCM is not evidence that HE/v2 now fits.

### Required compatibility and acceptance

- [ ] Preserve every supported AAC variant: AAC-LC, HE-AAC v1 (SBR), HE-AAC v2
  (SBR + PS), mono/stereo, supported rates and bitrates, and supported input
  framing/container paths. Inventory the actual firmware paths separately
  from the SDK's capabilities; record missing variants as gaps to address,
  rather than claiming that all AAC profiles or containers already work.
- [ ] Require full decoded sample rate and channels, including 44.1/48 kHz
  HE/v2 stereo. No forced 22/24 kHz limit, forced mono, disabled SBR/PS, or silent
  AAC-core fallback is acceptable as a RAM optimization. The current full-radio
  SBR allocation failure above remains an open defect until this passes.
- [ ] Compare PCM and persistent overlap/state against the original path where
  exact comparison applies; exercise all window sequences, distinct L/R audio,
  malformed/truncated input, output backpressure/cancellation, reset and OOM.
- [ ] Verify source and PCM metadata, including in-stream changes, on OLED and
  WebUI. A changed output buffer size must not leave stale format information.
  The [native profile fix](ESP32C3_AAC_METADATA_20261004.md) passes real-library
  QEMU and host OLED/WebUI callback tests, including HE mono duplicated to stereo.
  Physical display/browser verification is still required.
- [ ] Run A/B on physical C3 with Wi-Fi, HTTP/HTTPS, WebUI and PDM active. Record
  total CPU, decoder CPU, heap/stack margins and underruns. Recheck other codecs;
  an isolated decoder or QEMU pass alone is insufficient for acceptance.

## Implementation

- [ ] Keep the 16 KiB TLS receive buffer and 4 KiB transmit buffer allocated
  for the lifetime of one HTTPS connection instead of reallocating them for
  every TLS record.
- [ ] Allocate the ICY metadata workspace once and reuse it across stations.
- [x] Preserve the Espressif decoder PCM workspace for explicitly compatible
  station changes and only grow it as needed. The current audio service releases
  it for AUTO or custom-decoder targets; this existing reuse is separate from
  the planned within-frame scratch/PCM optimization above.
- [ ] Use 16 KiB (10 x 1600-byte blocks) as the compressed-audio default,
  while keeping the user-selectable 8-22.4 KiB range for jittery streams.
- [ ] Log free heap, largest free block, minimum free heap and task stack
  high-water marks after the TLS handshake and after the first decoded frame.

## Verification

2026-10-04 checkpoint: [late implicit SBR experiment](ESP32C3_AAC_LATE_SBR_20261004.md)
reproduces the physical same-header LC → HE failure and fixes both LC history
bank phases in QEMU. Ordinary six-fixture PCM is unchanged over 887,808 channel
samples; pointer/lifetime checks pass. Reverse transitions and transition PCM
remain unqualified, so the option is QEMU-only and production gates stay open.

Later checkpoint: [retained SBR/PS](ESP32C3_AAC_SBR_RETENTION_20261004.md)
now passes absent/resumed-extension cases in both bank phases, matching the
FAAD retention behavior. Raw compact-vs-full-precision PCM differs by at most
2 LSB over 189,440 samples. This supersedes the assumed immediate LC fallback;
expanded corpus, physical CPU/network/OTA and all-codec gates remain open.

Expanded checkpoint: [parser-derived SBR gaps](ESP32C3_AAC_SBR_GAPS_20261004.md)
pass format/memory/lifecycle checks on four HE/HEv2 cases, but **reject** the
current compact precision candidate: 41 of 675,840 samples exceed 3 LSB, with a
5-LSB maximum in HE stereo 44.1 kHz while SBR is absent. Keep deployment gated
until precision is repaired. Also fix the HE-mono-as-HEv2 label inference:
the SDK can duplicate mono into stereo without PS.

Precision follow-up: [19-bit high-QMF history](ESP32C3_AAC_PC19_20261004.md)
repairs that corpus to a 2-LSB maximum with no samples over 3 LSB. Keeping extra
bits in the context costs 144 allocated bytes instead of the 2,048-byte owner
allocation increase. Audited guest instructions increase 2.39%; production
defaults remain unchanged. Extend to real recordings, reduce/qualify overhead,
repair mono/PS metadata and complete malformed-input and physical gates.

Real-recording follow-up: [PC19 through the production adapter](ESP32C3_AAC_PC19_RECORDINGS_20261004.md)
passes all five retained radio captures (12,505,088 channel samples), with a
2-LSB maximum and no samples over 3 LSB. The two HE-AAC captures and AAC-LC
control are exact. This closes that retained-corpus check only; actual
mono/PS reporting, malformed inputs, physical playback/OTA and broader codec
coverage remain open.

Metadata follow-up: [native SBR/PS flags and source channels](ESP32C3_AAC_METADATA_20261004.md)
replace the mono-core/stereo-PCM inference. All three QEMU variants pass, and
3,651,584 compared PCM samples remain exact against their respective previous
builds. The profile byte fits existing padding. This closes the emulator/host
metadata defect; physical metadata, malformed-input and all-codec gates remain open.

Fault-test follow-up: [late OOM and malformed frames](ESP32C3_AAC_FAULTS_20261004.md)
passes four late SBR allocation failures and four malformed-input cases, with
120 subsequent HE-AACv2 recovery frames and balanced allocation/free counts.
Following transition/gap PCM remains exact over 865,280 samples. The SDK may
skip a malformed frame with OK/zero output; the tests now account for that.
This does not qualify every input read: bounded FIL parsing, broader truncation,
same-decoder recovery, physical and all-codec gates remain open.

FIL follow-up: [bounded fill-element parsing](ESP32C3_AAC_FILL_BOUNDS_20261004.md)
reproduces the native cursor overrun and replaces both FIL helpers with checked
byte reads. Plain/compact QEMU comparisons and 343,475 truncated host cases pass;
865,280 subsequent PCM samples remain exact. The physical integration image is
saved, with no new persistent RAM. Other input readers, broader malformed syntax,
same-decoder recovery and physical/all-codec qualification remain open.

Physical integration follow-up: [PC19 and late SBR in the network image](ESP32C3_AAC_PC19_NETWORK_20261004.md)
passes the prior QEMU suite with 865,280 identical transition/gap samples, OTA
during playback, 20 physical matrix gates including 21 mixed-codec switches,
and five minutes of full-rate HE-AAC HTTPS under WebUI load. The previously
failing same-header LC-to-HEv2 transition now passes on hardware. The CPU-load
matrix still retains a HE status timeout and free-heap decline failures for
MP3/Vorbis/Opus. Diagnose them and repeat longer/repeated OTA and codec tests;
do not infer production acceptance from the successful HTTPS run.

Receive-credit follow-up: [long playback and fragmentation](ESP32C3_RECEIVE_CREDIT_20261004.md)
correlates initial MP3/Vorbis/Opus heap decline with 9–11.5 KiB of queued TCP
receive credit. Three 60-second unpaced-file controls pass unchanged load and
idle-recovery gates. However, one 180-second Vorbis run leaves the idle largest
block at 59,392 B instead of 114,688 B, despite nearly unchanged total free heap.
HE-AAC HTTPS then plays at full 44.1 kHz stereo from that state, but its progressive
heap gate still fails. Identify the retained allocation, extend the controls,
and distinguish bounded queue filling from a leak without dropping the failures.

- [ ] Add regression tests for buffer lifetime, the 16 KiB default, and the
  configurable upper limit.
- [ ] Run the complete host test suite.
- [ ] Build the normal ESP-IDF firmware with `-O3`.
- [ ] Test repeated HTTPS AAC playback on the physical ESP32-C3 OLED board.
