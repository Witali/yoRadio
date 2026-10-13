# Bounded format confirmation: core and queue integration

## Current state (2026-10-13)

`stream_confirm.h` implements and tests a bounded confirmation core over a
caller-owned byte window. `audio_service.c` now calls it through `stream_start.h`
when **`CONFIG_YORADIO_STREAM_CONFIRM=y`** and the frame router is enabled.
Both options remain experimental and off by default. Production therefore
still uses the original single-header initial probe. Startup confirmation does
not implement recovery after lost alignment during established playback.

The previous FFmpeg comparison identified false MP3 headers before AAC and false
AAC headers before MP3 as unresolved failures. The new core rejects those
candidates when their claimed next frame boundary is invalid, then searches for
a valid candidate within the supplied search budget. It accepts the first frame
when a second frame header is present at exactly its declared end.

### Rules implemented in the core

- Read through a callback; retain no caller pointers and allocate no memory.
  The callback can read across existing packet slots.
- Inspect only bounded headers (at most ten bytes per callback). Never require
  two complete frames in memory.
- After a false candidate, return a proven-junk prefix to discard and charge
  against the connection's remaining search allowance. The aligned frame walker
  remains separate and does not search ordinary compressed payloads.
- Allow VBR/padding, sample-rate/channel changes and a real MP3/AAC transition
  at a declared boundary. They are not grounds to reject synchronization.
- At EOF, accept exactly one complete elementary frame with an explicit
  `single_frame_eof` flag; its decoder must still validate its contents.
  Do not claim multi-header confidence for this short-file exception.
- Report free-format MP3 separately; no guessed length or false confidence.
- Native FLAC and Ogg retain the existing signature policy; their container
  parsers own further validation. This work does not add multi-frame container
  confirmation or container switching.
- Return an explicit metadata-removal request for a bounded ID3v2 envelope,
  or an ID3v1 tail after an MP3 candidate. The caller must skip the entire body,
  detect truncation, enforce metadata context/run limits, and preserve earlier
  candidate bytes. A header alone does not prove that the tag body arrived.
- Two syntactically valid headers are evidence of framing, not proof of valid
  AAC/MP3 payloads or CRC integrity. Decoder checks remain necessary.

## Measured evidence

`tests/run-stream-confirm.py --output NEW_DIRECTORY` compiles the actual header
under ASan/UBSan. The 26-file AAC/MP3 corpus uses ffprobe's first-frame lengths;
it includes AAC-LC, HE-AAC, HE-AACv2, all supported MPEG sample-rate groups,
CBR/VBR and mono/stereo. Five extra cases add both false-header directions,
single-frame AAC/MP3 EOF, and MP3 → HE-AAC. **31/31 cases pass** with input
limits of 1, 7 and 2048 bytes. Unit tests also cover tags, budget exhaustion,
maximum-length ADTS and 5,000 deterministic malformed windows.

| Input | Selected codec | Discarded bytes | Retained bytes at confirmation |
|---|---|---:|---:|
| False MP3 before HE-AAC | AAC | 32 | 386 |
| False AAC before MP3 | MP3 | 32 | 964 |
| Single HE-AAC frame at EOF | AAC, short-file exception | 0 | 341 |
| Single MP3 frame at EOF | MP3, short-file exception | 0 | 960 |
| One MP3 frame then HE-AAC | MP3 first | 0 | 967 |

An earlier false candidate can require a larger window than the ultimately
selected frame. Clean streams need the first frame plus the next header.

ESP32-C3 GCC 15.2, `-Os -march=rv32imc -mabi=ilp32`, compiles the standalone
wrapper to an object with **1,578 bytes text, 0 data, 0 BSS**. Static stack
reports show 144 bytes for the wrapper and 32-byte frames for the frame-header
and ID3-size helpers. This excludes the storage callback and caller and is not
a runtime stack high-water measurement or final linked firmware size.

[Frozen evidence](../tests/results/esp32c3-stream-probe-20261013/confirmation-core-01/)
contains the exact source, corpus report, logs and target compilation evidence.

## Memory design constraints for integration

ADTS can declare up to 8191 bytes. Four existing 2048-byte packet payloads
provide 8192 bytes; a separate ten-byte lookahead area handles the next header
or ID3 envelope. The current initial probe already owns a ten-byte header
array, which can be reused after copying the candidate header into held slots.
Do not allocate another full-frame buffer or import FFmpeg's growing buffers.

The existing adaptive queue permits multiple WRITING leases, protects them
from TLS reclamation, and can cancel them. A confidence adapter must explicitly
own these leases across network reads. The present ordinary frame adapter's
rule that no lease survives `send_stream_audio` must not be silently changed.

Holding all four slots while trying to enqueue an old-codec drain marker can
deadlock: the decoder cannot consume unpublished leases. A confirmed frame can
also end partway through a held packet, with bytes of another codec still in
its suffix. The integration uses a separate small control FIFO element for
both short replay fragments and drain markers. No unconfirmed bytes are
published to make room, and a whole held packet is never blindly labelled as
one codec.

## Ordered remaining work

### Queue storage implemented and tested (2026-10-13)

`stream_staging.h` now owns up to four unpublished leases from the actual
adaptive input queue plus ten lookahead bytes. It supports bounded append/read,
removal of proven junk or received metadata, cancellation, and ownership
transfer of an original packet pointer. It rejects a queue with fewer than
four guaranteed slots. Acquisition is nonblocking: a short append returns the
accepted byte count so the connection owner can retain the rest and enforce
its deadline. It never allocates a new frame buffer.

The state occupies **64 bytes on ESP32-C3**, including its ten-byte lookahead.
This standalone implementation does not yet replace the existing probe's
header storage. All six wrapper operations compile to a 930-byte text object,
zero data/BSS, using GCC 15.2 at `-Os`; reported static wrapper stack frames
range from 0 to 80 bytes, excluding queue/library callees. These are object
measurements, not a final firmware size or runtime high-water measurement.

Tests compile the actual adaptive queue and staging code with pthread RTOS and
heap doubles under ASan/UBSan. They cover 20,000 randomized append/erase/transfer/
cancel operations, overlapping reclamation attempts, reclamation of four spare
slots while four candidate leases stay protected, a maximum 8191-byte ADTS
frame plus its next header, full-queue backpressure, repeated cancellation,
exact payload preservation and original-pointer transfer. The simulated queue
allocator is forced to fail throughout the main storage exercise: no additional
allocation is required after queue creation. All allocations are released at
test teardown. The same 31 AAC/MP3 confirmation cases also pass through this
actual queue storage with 1/7/2048-byte delivery, matching the prior core results.

Reproduce:

```sh
python tests/run-stream-confirm.py --output .build/confirmation-fresh
python tests/run-stream-staging.py --output .build/staging-fresh --corpus .build/confirmation-fresh
```

[Frozen storage evidence](../tests/results/esp32c3-stream-probe-20261013/staging-01/)
includes sources, logs, corpus hashes and target compilation evidence.

The original packet-transfer test proves
storage ownership only: the caller still has to split at the selected codec's
frame boundary and replay lookahead through the frame walker. It must never
mark an entire retained packet as one codec when it contains a codec transition.
Those storage tests alone do not prove actual Stop/generation handling, EOF/tag
lifecycle, control-marker capacity, HTTP/HTTPS behavior or physical continuity.

### Startup adapter and control FIFO (2026-10-13)

The adaptive queue accepts one caller-owned control storage area, independent
of its data slots but ordered in the same FIFO. Normal acquire and TLS reclaim
never take it; it is excluded from resident/occupied audio-prefill statistics.
The queue does not free caller storage. The C3 queue descriptor adds a 20-byte
slot plus a four-byte capacity field, even when no control storage is attached.

`stream_start.h` retains candidates in the four existing data leases. If at
least one data slot is guaranteed to remain outside the held window, confirmed
bytes use ordinary packet coalescing. When all guaranteed data slots are held,
replay falls back to **128-byte control payloads**. This uses copies at startup;
it is not zero-copy playback. In the fallback, both replay data and codec-drain
markers use the independent slot, so four held candidates cannot prevent the
consumer from receiving them. No decoder pointer references a held candidate
lease, and TLS reclamation cannot lower the guaranteed data-slot floor.

The first implementation used the small control payload for every startup.
QEMU showed an extra **964 bytes** in MP3's first-frame decoder allocation
delta (41,912 instead of 40,948 bytes). Preferring ordinary coalescing restored
the **40,948-byte** decoder delta for that fixture. A pathological candidate
that occupies all slots still uses short fragments; its decoder-side memory
and latency need qualification under physical TLS pressure.

The adapter handles single-frame EOF, streams ID3 bodies without retaining
them, bounds consecutive metadata/search work, rejects duplicate ID3v1 tails
after the same candidate, and cancels held leases on failures and connection
reset. A generation check and a ten-second deadline bound startup storage
acquisition. HTTP EOF finalization and flash-fixture EOF both call the adapter
before the terminal marker; read failures retain their error reason.

Host evidence:

- The actual adaptive queue passes **60,000 concurrent packets** (30,000 normal
  and 30,000 mixed normal/control), with FIFO, invalid ownership, all 16 data
  indices, allocation failures, TLS reclamation and shrink/restore checks.
- The actual router replays MP3/AAC/MP3 with four data leases held, 128-byte
  control fragments, exact bytes and two ordered drain markers. Concurrent
  generation cancellation succeeds with input chunks of 1, 7 and 2048 bytes.
- The actual `send_stream_audio`/`finish_stream_audio` functions pass the 31-file
  corpus with exact encoded replay and clean EOF at all three chunk sizes.
  Unit checks cover single-frame EOF, a wrong MIME hint, large ID3 bodies,
  every truncated ID3v1 tail length, duplicate/oversized tags, maximum ADTS,
  empty input, FLAC/Ogg/free-format encoded pass-through, reset/generation
  cancellation, read failure and deadline expiry. ASan/UBSan report no errors.

These host tests use RTOS/heap doubles and a capturing consumer. They do not
exercise an HTTP socket, a hardware decoder task or physical audio output.

```sh
python tests/run-adaptive-input.py --output .build/control-fresh
python tests/run-stream-staging-router.py --output .build/router-fresh
python tests/run-stream-start.py --output .build/start-fresh --corpus .build/confirmation-fresh
```

### QEMU PCM and memory qualification

The final `idf61-confirm-start` C3 benchmark image passes **13/13 PCM captures**:
MP3, AAC-LC, HE-AAC, HE-AACv2, both false-prefix directions, ID3v1 tails and
the existing mixed-codec sequences with/without tags. The two false-prefix
captures equal their clean-stream references. All **11 overlapping cases**
also match the previous `idf61-id3v1-pcm` firmware byte for byte, including
sample count, channel layout and rate. No decoded-quality tolerance was needed.

| First decoded frame (QEMU) | Previous free heap | Final free heap | Difference | Final largest block |
|---|---:|---:|---:|---:|
| MP3 320 kbit/s | 228,556 | 228,300 | -256 | 114,688 |
| HE-AAC 48 kHz stereo | 174,008 | 173,752 | -256 | 114,688 |
| HE-AACv2 44.1 kHz stereo | 174,136 | 173,880 | -256 | 114,688 |

Decoder stack high-water values are unchanged in these fixtures. MP3's
first-frame decoder allocation delta returns to the previous 40,948 bytes;
the rejected all-small-fragment variant used 41,912 bytes. Both versions log
a 1000 ms input-prefill interval in QEMU; this is not a physical startup or CPU
timing result. The largest block at decoder **open** can differ despite an
equal first-frame largest block, so this table does not certify fragmentation
or TLS margins on hardware.

Linked named startup state is 96 bytes, control storage is 140 bytes, and its
attachment flag is one byte. Queue bookkeeping adds 24 bytes on C3. The measured
256-byte free-heap change includes linker layout/alignment effects; it is not
the arithmetic sum of the symbol sizes. The final QEMU-only app is 1,003,840
bytes, 5,808 bytes larger than the previous 998,032-byte benchmark image.

[Frozen integration evidence](../tests/results/esp32c3-stream-probe-20261013/startup-integration-01/)
contains host sources/logs, compressed QEMU traces with PCM, build identity and
the exact prior-firmware comparison. [Control-queue evidence](../tests/results/esp32c3-stream-probe-20261013/control-queue-01/)
records the separate 60,000-packet regression. Every archived file is covered
by a SHA-256 manifest; QEMU PCM bytes can be recovered from the compressed
capture logs with the existing parser. The physical board was not reflashed.

## Full-window replay and metadata ordering (2026-10-13)

The maximum-length false ADTS prefix now has real-decoder coverage. The QEMU
startup-only matrix passes 8/8 captures; replay after the false 8191-byte
candidate produces exactly the clean-stream PCM for HE-AAC (524,288 bytes)
and MP3 (294,912 bytes). The full-window MP3 path needs 964 additional bytes
for its decoder accumulator versus ordinary coalesced startup; HE-AAC has
the same first-frame heap as clean startup. These measurements use the
previous `idf61-confirm-start` benchmark, before the status-only fix below.

The host corpus has 33 cases. Both large-prefix fixtures exercise the
independent control node, with 64 control packets for each input chunk size
(1, 7 and 2048 bytes). The short HE-AAC host fixture must repeat complete
frames to exceed the candidate window: the first test-design attempt reached
EOF early and therefore did not exercise the required control fallback.

The first physical HTTP matrix passed 19/20 cases. In the failing large-prefix
HE-AAC case, the decoder reported 48 kHz stereo, but the stream task overwrote
its profile with generic `AAC` after replay. Replay can block while the decoder
already publishes metadata. The correction publishes the provisional family
before committing any encoded bytes, including the EOF-only single-frame path
and the legacy initial probe. Subsequent decoder metadata remains authoritative.

A deterministic consumer-first host schedule reproduces the overwrite on the
pre-fix code and passes on the corrected implementation under ASan/UBSan.
It checks one provisional publication per accepted stream and exact replay;
the pre-fix assertion failure is retained as a negative control.

Evidence is collected in
[startup-metadata-01](../tests/results/esp32c3-stream-probe-20261013/startup-metadata-01/),
including the failed hardware trial and its exact application image. Physical
requalification of the corrected image is tracked separately from QEMU PCM.

The corrected physical HTTP matrix passes **20/20 cases**: MP3, FLAC,
Vorbis, Opus, AAC-LC, HE-AAC, HE-AACv2, ID3-prefixed streams, three malformed
inputs, four false prefixes, rate/profile changes and MP3/AAC family changes.
The offline audit independently rechecks expected statuses, complete response
bodies, stable metadata, unchanged boot identity, zero allocation/watchdog
errors and unchanged output counters in sampled active intervals. Original
firmware, private settings and stopped state were restored and verified.

| HTTP case | Lowest sampled active free heap | Lowest sampled largest block |
|---|---:|---:|
| MP3 320 kbit/s | 83,680 | 69,632 |
| FLAC level 8 | 64,248 | 49,152 |
| HE-AAC 48 kHz stereo | 38,040 | 28,672 |
| HE-AACv2 44.1 kHz stereo | 40,560 | 31,744 |
| Large false ADTS before HE-AAC | 29,964 | 20,480 |
| Large false ADTS before MP3 | 84,364 | 65,536 |

These are sampled system values, not codec allocation sizes or absolute heap
minima. They do not establish HTTPS headroom. Startup/idle/EOF completion
counter changes are kept in the audit; no lifetime-zero-drop claim is made.
The final legacy-path adjustment preserves the failed-send `first_chunk`
contract and passes the default-mode corpus (11 files, six variants each).
Rebuilding the confirmation-enabled hardware configuration after that adjustment
produces **the identical app.bin**, as recorded in `rebuild-comparison.json`.

The physical held-candidate control test also passes 3/3 cases with the station
watchdog disabled. At 8180 bytes the server begins two-second pauses between
successive bytes, keeping the declared 8191-byte candidate incomplete:

| Action | Observed time |
|---|---:|
| Unresolved-format deadline | 10.49 s from server delivery start |
| Stop | 0.146 s from control request |
| Replacement with HE-AAC | 2.33 s until three matching status samples |

Median settled heap is 139,760 bytes before and after, largest block 106,496
bytes, and task count 16. No allocation/watchdog error or unexpected restart
was recorded. The first controller attempt requested a single unsupported
20-second server pause; it failed before playback cases, restored the board,
and is retained separately. Schedules are now validated before installing an
image. As elsewhere, server byte counts are not direct lease instrumentation.

The matching partial-header controller passes another 3/3 cases: deadline
10.69 s, Stop 0.212 s and HE-AAC replacement 2.08 s. Settled median heap
(139,752 bytes), largest block (110,592 bytes) and task count (16) are identical
before and after. Both control runs restore the original app and private
settings and leave playback stopped. Together with the format matrix, this
qualifies 26 finite HTTP scenarios on the saved candidate, not HTTPS or
continuous playback.

## HTTPS qualification: unresolved transition failure (2026-10-13)

The laboratory `idf61-start-confirm-tls` image uses the same firmware sources
as the HTTP candidate. Its sdkconfig differs only by the added laboratory CA;
full public roots, server certificate verification and 16384-byte TLS receive
records remain enabled. The image is saved separately and is not a production
release. Public certificate identities and the configuration comparison are in
[startup-tls-01](../tests/results/esp32c3-stream-probe-20261013/startup-tls-01/).

The first HTTPS matrix passes **19/20** cases. MP3, FLAC, Vorbis, Opus,
AAC-LC, HE-AAC, HE-AACv2, false prefixes, metadata and rate/profile changes
pass, as does AAC-LC -> MP3 -> HE-AACv2. **MP3 -> HE-AAC -> MP3 fails**:
the second profile is never observed and the terminal status is `decode failed`.
The offline audit rejects this run. The original app/settings were restored.

The last 17 active health samples before the failed transition have zero
allocation/watchdog failures and unchanged output counters. This does not
exclude an allocation failure at the boundary: the original runner did not
capture health after its transition assertion failed. It now attempts a
post-failure health snapshot before Stop/restoration, without masking the
original error if that diagnostic request also fails. Quiet firmware does
not expose the decoder return code, so MP3 drain versus AAC initialization
has not yet been distinguished. Do not classify this as a harmless UI race.

The next case's baseline provides additional evidence on the same boot
(`33dd1269d6827b79`): at uptime 304172 ms, `allocation_failures` is **1**,
versus 0 at 302928 ms in the failed sequence's last active sample. Thus an
allocation failure occurred by the time the failed case had been stopped.
Its requested size/capabilities and exact phase are not recorded. The following
AAC-LC -> MP3 -> HE-AACv2 case passed its local checks with the already-increased
counter; that is not proof of zero allocation failures for the matrix.

A standalone fresh-boot repeat of MP3 -> HE-AAC -> MP3 passes, including the
strict offline audit with zero allocation failures and verified restoration.
It does not erase the earlier failure or qualify the full sequence of tests.
History-dependent fragmentation or allocation pressure is a hypothesis to
investigate, not an established root cause.

| Successful case | HTTP sampled free / largest | HTTPS sampled free / largest |
|---|---:|---:|
| MP3 320 kbit/s | 83,680 / 69,632 | 79,948 / 65,536 |
| FLAC level 8 | 64,248 / 49,152 | 59,824 / 45,056 |
| HE-AAC 48 kHz stereo | 38,040 / 28,672 | 35,248 / 21,504 |
| HE-AACv2 44.1 kHz stereo | 40,560 / 31,744 | 36,596 / 21,504 |
| Large false ADTS before HE-AAC | 29,964 / 20,480 | 29,856 / 17,408 |

All figures are bytes and sampled system heap, not allocator peak guarantees
or isolated TLS costs. Queue/network occupancy differs between runs.

The held-candidate HTTPS control test passes 3/3: deadline 10.59 s, Stop
0.140 s and replacement 2.78 s. It negotiates TLS 1.2 with
ECDHE-RSA-AES256-GCM-SHA384. Settled median heap changes from 139,752 to
139,756 bytes, largest block remains 110,592 bytes and task count remains 16.
Firmware and private settings restoration passes. This control result does
not resolve the failed in-connection codec transition.

The partial-header HTTPS controller also passes 3/3: deadline 10.64 s, Stop
0.135 s and replacement 2.74 s, using the same TLS version/cipher. Settled
median free heap changes from 139,760 to 139,748 bytes (12 bytes lower),
largest block stays 110,592 bytes and task count stays 16. This is within
the existing recovery bounds (2048 free bytes, 4096 largest-block bytes);
it is not an exact-byte heap-recovery claim. Both TLS control variants pass
firmware/private-settings restoration and leave playback stopped.

Next diagnosis: repeat the preceding workload, retain post-failure health,
record the failed allocation size/capabilities, and capture the decoder's
return code and whether it occurred on the MP3
drain marker or an AAC data packet. Reproduce the encoded fragmentation with
real-decoder PCM tests before changing error handling; never suppress a
decoder error merely to turn the status green.

## Qualification status and remaining work

1. HTTP format requalification of the metadata-order correction is complete;
   maximum-length startup replay also has host and real-decoder QEMU coverage.
2. Resolve the HTTPS MP3/HE-AAC transition failure and complete control regressions on C3, including Stop
   during candidate collection, stalls and incomplete tags, TLS pressure,
   repeat connections, actual queue target below four, and heap recovery.
3. HTTP FLAC/Vorbis/Opus playback passed. Add decoded free-format playback
   and PCM-quality checks; host byte-preservation checks alone do not prove them.
4. Implement confidence at codec changes and bounded recovery after lost
   alignment. Startup success does not establish those behaviors. Keep every
   existing codec/profile and avoid discarding real payload after false sync.
5. Qualify longer physical playback and startup latency before enabling defaults.

Do not enable the new path by default until these gates pass. A passing core
test does not prove queue lifetimes, physical memory pressure or sound continuity.

### Retained failure diagnostics (2026-10-13)

Quiet firmware now retains the latest failed allocation's requested bytes and
capability mask, plus the latest Espressif/native AAC decoder failure: codec,
stage (1=open, 2=process, 3=PCM allocation), signed SDK result, original completion
marker, unconsumed input bytes, and allocation-failure count at that instant.
`completion=7` identifies a codec drain; it is not terminal EOF. See the native
codec enum and `audio_completion.h` for the numeric definitions. A zero decoder
sequence means no recorded failure. Custom FLAC/Helix/minimp3 adapters do not yet
publish decoder failure details through this API; their heap failures still count.

Both snapshots are copied with interrupts masked on single-core C3. The allocation
callback never dereferences its function-name pointer, allocates or logs. Numeric
records survive Stop/cleanup; a subsequent allocation failure can replace the
last size/caps but cannot rewrite the decoder's captured allocation sequence.
This is a last-event snapshot, not a complete allocation history or proof of cause.
Additional retained storage is 36 bytes; health JSON workspace grows by 256 bytes
inside the existing HTTP task stack. No new task or heap buffer is created.

Validation: actual counter/handler C passes ASan/UBSan in four watchdog/probe
combinations, including maximum-width JSON, interrupt-mask restoration and an
allocation failure after decoder failure. Eight Python health tests and five
pipeline tests pass, including bounded numeric filtering and older schema-1
compatibility. ESP-IDF 6.1 candidate builds successfully. Physical follow-up is recorded below.

Physical follow-up: `startup-fault-01` passes all 20 HTTPS cases and the strict
offline audit, including MP3 -> HE-AAC -> MP3 after the complete preceding workload.
All observed allocation, decoder-failure and watchdog counters remain zero;
recorded lifetime minimum heap is 19,108 bytes. Active output-counter checks pass.
Original app and private settings are verified restored, playback stopped.
The earlier failure did not recur; this diagnostic-only change is not a proven
root-cause fix. The candidate remains laboratory-only and production-unqualified.
Further repetitions with connection/codec history are required.

The real generic decoder loop also passes 30 ASan/UBSan stub scenarios, checking
that fatal process/PCM errors are recorded before cleanup with the original
codec, return code and data/drain/EOF marker. C callbacks are verified in the ELF:
allocation handler and both interrupt-mask helpers are in IRAM, retained state
is in DRAM. Source snapshots, logs, image identity, physical results and SHA-256
manifest: [startup-fault-01](../tests/results/esp32c3-stream-probe-20261013/startup-fault-01/summary.json).
Test image: `firmware/development/esp32c3-idf-6.1-r9a97-startup-fault-tls-lab/app.bin`.

### Next memory-placement experiment after repeated HTTPS failure

The repeat controller now distinguishes per-case success from whole-run health
and verifies that all cases share one boot. The completed five-iteration run
has 17 local case passes and three failures: the second, third and fifth
MP3 -> HE-AAC -> MP3 cases reproduce the failure with:
`size=32744`, `caps=6144`, AAC codec 2, process stage 2, SDK result -2
(`ESP_AUDIO_ERR_MEM_LACK`), completion marker 0 (ordinary data), and 723 remaining
input bytes. The allocation and decoder failure sequences advance together.
DWARF from the exact candidate ELF confirms `sizeof(owner_t)=32744` in
`aac_compact_owner.c`; SDK caps are INTERNAL | DEFAULT. This locates the failed
compact SBR allocation; it does not yet distinguish fragmentation from total
free-memory exhaustion at that instant.

All 20 cases share one boot; final allocation and decoder failure counts are
both three, watchdog count is zero, and lifetime minimum heap is 18,732 bytes.
Each failed stream stops with `decode failed`; starting the next fixture succeeds.
This is recovery on a new Play request, not recovery within the failed stream.
The strict offline audit rejects the matrix. Original firmware and all private
settings are verified restored, with playback stopped. Source/controller
snapshots, full results and allocation-size inspection are in
[startup-repeat-01](../tests/results/esp32c3-stream-probe-20261013/startup-repeat-01/summary.json).
The candidate manifest now records this repeat failure as well as the earlier
single matrix pass; it remains unqualified.

Next steps, keeping every AAC profile and unchanged PCM arithmetic:

1. Capture available/largest matching-capability heap around this owner request
   in the decoder task, before outer decoder cleanup. Keep the general IRAM
   failed-allocation callback free of heap traversal and logging. Label whether
   values precede or follow the allocation attempt; do not interpret settled
   post-cleanup heap as the failed allocation's available memory.
2. Test reserving the current compact `sizeof(owner_t)` earlier, before the
   AAC PCM/core allocation sequence. The old EARLY_SBR_RESERVE feature targets
   the original 55128-byte owner and is explicitly incompatible with compact
   SBR; enabling that old flag would not be a valid comparison.
3. If adding a compact pending owner, audit create, successful claim, LC-only
   first output, implicit late SBR, profile reopen, failed open/process, Stop
   and destroy. Pending storage must be freed exactly once or transferred to
   the normal owner; preserve pointer-audit registration. Do not keep an
   unused SBR reservation indefinitely for AAC-LC or hide failed HE as LC.
4. Compare the same repeated HTTPS workload, the full format matrix and real
   decoder PCM against the control. Allocation ordering must preserve exact
   PCM; it does not justify relaxing the existing 3-LSB compact-history bound.
   Check LC peak/steady heap as well as HE, so fixing HE does not regress LC/TLS.

This is a pending placement experiment, not an implemented or qualified fix.

### Compact early-owner prototype

`CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER` is now an opt-in allocation-order
experiment, dependent on compact SBR and disabled by default. It reserves the
configured `sizeof(owner_t)` before the service allocates AAC PCM/core state,
then transfers that zeroed block through the existing SDK owner-allocation
wrapper. Normal owner initialization, pointer-audit registration and free
handling remain in the common path. One extra pointer belongs to each native
AAC adapter; no additional permanent/global arena is introduced.

An unclaimed reservation is discarded on decoder destruction and after a
successful PCM-producing LC frame. Profile reopen prepares a new reservation;
an SDK open failure can release it and retry inside the same compact context.
Late implicit SBR after LC still uses the normal allocation path. Preparation
failure is not permission to emit LC instead of HE: the existing actual SBR
allocation-failure handling continues to reject incomplete decoding.

The actual prepare/claim/free functions pass ASan/UBSan ownership tests with
injected failures, task-context isolation, zeroing, late retry and cleanup.
These tests mock the ABI sizes and DSP; real-decoder PCM, complete adapter
lifetime and physical repeated-HTTPS/LC-memory qualification remain required.
The prototype is not a production default or a qualified fix.
