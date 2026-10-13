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

## Remaining qualification

1. Extend real-decoder QEMU fixtures to a false maximum-length ADTS candidate
   before MP3/HE-AAC, forcing all four staging slots and the small-fragment
   fallback. The current synthetic full-slot host test proves FIFO/lifetime,
   but does not measure the real decoder's memory in that worst case.
2. Run complete HTTP/HTTPS format/control regressions on C3, including Stop
   during candidate collection, stalls and incomplete tags, TLS pressure,
   repeat connections, actual queue target below four, and heap recovery.
3. Verify decoded FLAC/Ogg and free-format playback with this option enabled;
   host byte-preservation checks alone do not prove decoding or output quality.
4. Implement confidence at codec changes and bounded recovery after lost
   alignment. Startup success does not establish those behaviors. Keep every
   existing codec/profile and avoid discarding real payload after false sync.
5. Qualify longer physical playback and startup latency before enabling defaults.

Do not enable the new path by default until these gates pass. A passing core
test does not prove queue lifetimes, physical memory pressure or sound continuity.
