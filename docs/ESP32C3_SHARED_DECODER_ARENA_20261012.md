# ESP32-C3 shared decoder arena experiment

Follow-up: [FLAC DMA investigation, October 13](ESP32C3_ARENA_FLAC_DMA_20261013.md)
separates input starvation from allocator latency and repeats the missing
no-arena FLAC control. The original failures below remain unchanged.

## Scope

`CONFIG_YORADIO_SHARED_DECODER_ARENA=y` reserves one private heap in static
internal RAM. `CONFIG_YORADIO_SHARED_DECODER_ARENA_BYTES=98304` selects the
initial **96 KiB** experimental budget. Both options are separate from the
tested radio profile; the feature is **off by default**.

The decoder task reuses this storage for MP3, AAC/HE-AAC, custom FLAC, Vorbis
and Opus. It includes libc allocations made during decoding and the caller's
PCM workspace. This is not a sum of permanently allocated per-codec heaps.
The SDK's global codec registration runs outside the arena. Alternative
Helix/minimp3 backends obtain their existing 24 KiB backing block from this
same pool, retaining their original internal lifetime rules; they require
separate qualification and are not the selected production backends.

Wi-Fi, TLS, input packets and output DMA retain their allocation domains.
The existing **17,058-byte TLS RX reserve** is unchanged. This experiment
does not reserve all mbedTLS handshake memory.

## Allocation and ownership

- The ESP-IDF `multi_heap`/TLSF allocator splits and coalesces blocks inside
  static storage. The region is never registered with `heap_caps`.
- Linker wrappers route decoder-task `malloc/calloc/realloc` calls using a
  task-local selector. Interrupt allocations and other tasks bypass it.
- `free/realloc` dispatch by pointer ownership, including when called from
  another task. Existing system pointers retain their original domain.
- Per-allocation headers retain the base and requested size. Payloads meet
  `max_align_t` alignment. Moving realloc preserves the payload and failure
  leaves the old pointer valid. No codec arithmetic or precision changes.
- There is no arena reset at station changes or EOF. Every pointer must be
  released normally; Stop should restore zero live arena allocations.
- Exhaustion returns failure, without falling back to the system heap.
- `/api/native/health` exposes `decoder_arena`: capacity, requested live/peak
  bytes, live blocks, allocator free/largest block and failure count.
  Requested bytes exclude allocator/header overhead; free bytes include
  neither live allocations nor their metadata. Peak is lifetime cumulative.
  The requested-byte peak also excludes the allocator's temporary old/new
  block overlap inside a moving realloc. Sampled free bytes are not a bound
  on that transient peak; do not size the pool from requested bytes alone.

All private heap operations and statistics share the C3 critical-section
lock. Realloc may copy data under this lock, like the underlying SDK
allocator. Its worst-case interrupt latency is not yet qualified. The
experiment does not promise constant-time allocation or lower CPU usage.

## Host validation

Run with the pinned ESP-IDF checkout:

```powershell
python -B -X utf8 tests/test-decoder-arena.py `
  --sdk-root C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6 `
  --output .build/decoder-arena-host
```

The test compiles the actual allocator adapter and pinned SDK `multi_heap`
and TLSF sources. It covers alignment, zero/overflow, realloc growth/shrink,
failed realloc data preservation, no-fallback exhaustion, coalescing,
thread-local and interrupt selection, cross-scope free and concurrent reuse.
All allocations return to the initial free/largest-block values.

ASan and UBSan are enabled. SDK allocator objects alone omit UBSan alignment
checks because the ESP port uses four-byte metadata on the 64-bit x86 host;
the adapter and returned payload alignment remain checked. Host mutexes
stand in for C3 critical sections. This is not an interrupt-latency test.

`tests/check-decoder-arena-link.py` verifies target call edges for SDK media
allocation shims, C++ new/delete, decoder selection and separate TLS
allocation. It also checks wrapper placement and that the only changed
enabled SDK settings are the two arena options.

An object-level comparison with the quiet production build found identical
instruction/constant sections and relocation targets in 14 locally compiled
AAC adapter/helper, Vorbis repair and custom FLAC objects. The vendor codec
archive is unchanged. This supports the intended allocation-only scope;
it is not a sample-by-sample PCM quality measurement.

## Physical experiment

Use `tools/esp32c3_tests/decoder_arena_experiment.py --help` for the reusable
OTA comparison runner. It restores the supplied original application and
station in a `finally` block. Wi-Fi credentials and original station/settings
remain in memory; reports contain only technical telemetry and synthetic
fixture descriptions. Keep failed attempts alongside successful reruns.

The first 96 KiB OTA attempt returned OK but did not become reachable within
the boot-check deadline; restoration over HTTP also failed. A native USB
watchdog reset subsequently started the exact candidate successfully. This
does **not** establish that arena exhaustion caused the original boot issue.

### Results

**Keep the feature disabled in production.** A 96 KiB pool was insufficient
for one AAC format transition. A 100 KiB pool decoded all tested formats and
transitions, but reduced system-heap headroom and had a failed FLAC DMA
counter check. This experiment provides isolation and predictable ownership,
not RAM compression or an established improvement in playback stability.

| Scenario | No private arena: sampled system free / largest block | 96 KiB arena | 100 KiB arena |
| --- | ---: | ---: | ---: |
| MP3 HTTP | 83,724 / 65,536 B | 26,992 / 13,312 B | 22,992 / 10,240 B |
| HE-AAC 48 kHz HTTP | 38,036 / 28,672 B | 37,204 / 17,408 B | 30,956 / 10,240 B |
| AAC changing formats | 40,228 / 24,576 B | Decoder allocation failed | 22,952 / 7,424 B |
| HE-AAC HTTPS, 60 s | 25,036 / 10,240 B | Not run | 18,372 / 4,608 B |

These are observed minima in the evaluation windows, not paired samples or
guaranteed bounds. HTTP files use a three-second warm-up; HTTPS uses fifteen
seconds. During the whole 100 KiB campaign, including startup/connection,
the lowest sampled system free heap was **11,840 B**; the board's lifetime
low-water counter reached **5,592 B** (control: **16,860 B**).

Useful live bytes and sampled free space **inside the 100 KiB arena**:

| Fixture | Maximum sampled requested live bytes | Minimum sampled arena free bytes |
| --- | ---: | ---: |
| MP3 320 kbps | 41,340 | 58,148 |
| AAC-LC 320 kbps | 60,620 | 38,148 |
| HE-AAC 48 kHz stereo | 94,032 | 4,660 |
| HE-AACv2 44.1 kHz stereo | 93,776 | 4,916 |
| FLAC level 8 | 53,024 | 45,872 |
| Vorbis q10 | 54,409 | 42,828 |
| Opus 510 kbps | 44,204 | 56,308 |
| AAC changing formats | 94,160 | 4,532 |
| AAC implicit SBR sequence | 94,288 | 4,404 |
| HE-AAC HTTPS | 94,160 | 4,540 |

- **96 KiB:** seven isolated files passed format/EOF, memory, output and
  arena checks. `changing` failed its third format transition with one arena
  allocation failure and output counter increments. The subsequent implicit
  SBR sequence played successfully with no additional allocation failure.
- **100 KiB:** all nine HTTP cases passed format/EOF and arena ownership
  checks; HTTPS also passed format, transport and output checks. There were
  **zero arena allocation failures**, and every Stop returned to **zero live
  bytes and zero live blocks**.
- The 100 KiB FLAC evaluation window recorded **31 completion-queue drops**,
  with zero write errors. Its cause was not isolated; this is a failed test,
  not evidence of unchanged audio continuity.
- Both AAC transition cases and HTTPS failed system contiguous-memory
  headroom with 100 KiB. The absolute gates remain 16 KiB total free and
  8 KiB largest block. No system allocation failure or task-watchdog event
  was recorded in the completed runs.
- No HTTP transport errors occurred in the completed 100 KiB run. An earlier
  control run aborted on a WebUI timeout; its evidence is retained.
- App-only OTA restored the original production image and settings after
  the completed campaigns. The saved playlist station was explicitly resumed
  at the end, restoring the first campaign's original playing state.

### Evidence and interpretation

[Raw measurements, replay and hashes](../tests/results/esp32c3-shared-decoder-arena-20261012/)
retain successful runs and failures. `review.json` reports the comparison;
`final-state.json` verifies the final application and resumed playback.
The original 96 KiB runner conservatively rejected the implicit-SBR arena
gate because an earlier case had incremented the lifetime failure counter.
Replay records **zero new** failures for implicit SBR without hiding the
preceding failed transition.

The initial control runner also applied a constant-format heap-trend check
to a deliberate LC-to-HE-AAC transition. That rejects expected growth in live
codec storage. Its original rejection remains saved. The corrected transition
gate retains absolute headroom and fault checks; Stop checks ownership
reclamation. The control transition passes those corrected gates, while both
100 KiB transitions still fail the unchanged largest-block floor.

The first 96 KiB runner made three HTTP requests per observation. The later
control/100 KiB runner reads arena and system counters from the same health
response, making two requests. The comparison is short and sequential;
network/music content and observation load are not perfectly identical.

Passing format/EOF and output counters does not establish PCM bit equivalence
or analog continuity. Long playback, maximum ADTS frames, unusual files,
alternative decoder backends and worst-case interrupt timing remain untested
for this allocator. Before another sizing change, add the allocator's actual
minimum-free telemetry to capture internal realloc overlap and investigate
the FLAC completion drops. Merely enlarging a permanent arena further takes
more memory away from TLS/Wi-Fi/WebUI.

### Saved experimental applications

- [96 KiB image](../firmware/development/esp32c3-idf-6.1-r9a97-decoder-arena/app.bin),
  ELF SHA-256 `cc368361c1317af977a284ecf1bd968ddce391d0b023b1f1b60b3dcac9b5a299`.
- [100 KiB image](../firmware/development/esp32c3-idf-6.1-r9a97-decoder-arena100/app.bin),
  ELF SHA-256 `0e14ca6699a3a34834d49dd62bf3c0a171a7946ae5ea53529b401dea110b2ec6`.

Each directory contains its exact sdkconfig and image manifest. Both are
experimental and **not production-qualified**. All enabled SDK configuration
differences from the quiet production control are the arena switch and size;
QIO, clock, TLS reserve, codec precision and other radio settings are retained.
