# Bounded format confirmation: core and queue integration

## Current state (2026-10-13)

`stream_confirm.h` implements and tests a bounded confirmation core over a
caller-owned byte window. **It is not yet called by `audio_service.c`.** The
production initial probe still accepts one header, and the frame router remains
experimental. This document does not certify false-sync recovery in firmware.

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

**Deadlock risk:** holding all four slots while trying to enqueue an old-codec
drain marker waits forever: the decoder cannot consume unpublished leases.
Do not publish an unconfirmed candidate just to make room, and do not drain
the old decoder based only on one speculative header.

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

**Still not connected to `audio_service.c`.** The packet-transfer test proves
storage ownership only: the caller still has to split at the selected codec's
frame boundary and replay lookahead through the frame walker. It must never
mark an entire retained packet as one codec when it contains a codec transition.
The tests do not yet prove actual Stop/generation handling, EOF/tag lifecycle,
control-marker capacity, HTTP/HTTPS behavior or physical playback continuity.
The following integration steps remain required.

1. **Startup staging adapter.** Reserve/reuse existing packet leases, expose a
   bounded read callback, and publish the confirmed first frame exactly once.
   Replay retained lookahead without copying into a fifth full-sized slot.
   Verify the actual queue minimum/target instead of assuming four free slots.
2. **Lifetime and terminal handling.** Cancel every held lease on generation
   change, Stop, HTTP failure, probe timeout and rejected candidates. Preserve
   exact bytes on retry/rescan. Resolve single-frame EOF before enqueueing the
   terminal marker; distinguish incomplete tags/frames from clean EOF. Never
   block awaiting input while the required queue storage is unavailable.
3. **Metadata removal.** Stream-skip bodies without retaining them. Charge the
   total metadata budget, enforce the existing ID3v1 context/duplicate rules,
   and test truncated bodies, false signatures in tags and oversized lengths.
4. **Codec-change/recovery staging.** Reuse the same core at lost alignment and
   codec changes only after solving marker capacity. Evaluate a small reserved
   control-only queue entry versus another allocation-free ordering mechanism;
   prove that a full set of held data leases cannot block a required drain.
5. **Integration gates.** Actual adaptive-queue tests with concurrent decoder
   consumption, TLS reclamation, cancellation and allocation failures; QEMU
   PCM equality on existing and false-prefix fixtures; complete HTTP/HTTPS
   format/control regression and longer playback/heap recovery on C3.

Do not enable the new path by default until these gates pass. A passing core
test does not prove queue lifetimes, physical memory pressure or sound continuity.
