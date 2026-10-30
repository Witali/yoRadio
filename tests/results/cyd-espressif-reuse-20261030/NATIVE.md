# Unchanged Espressif Vorbis: ESP32/C3 native checkpoint

The pinned Espressif 2.6.2 Xtensa and RV32 archives execute through public Ogg
interfaces on both SDK/QEMU targets. The diagnostic compiles the canonical CYD
registration and the shared pending-input owner. No private repair, custom
Vorbis decoder or custom arithmetic is selected. ELF architecture, linked
public symbols, configuration, source bytes and build outputs are checked.

Each target finishes four complete streams: warmup, then measured input
chunks of 4096, 257 and 1 byte. All eight streams produce 2,112,000 PCM bytes
with SHA-256 `e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910`.
The first 2,107,648 bytes also exactly match the retained historical original
C3 output, SHA-256
`eb2037928cd89a1922fd9ae9d055c03b587484b7378c55b0f319d79980976144`.

The complete length follows independently from the fixture's EOS granule:
528,000 stereo frames at PCM16. The old public test loop deliberately stopped
after one empty EOF call and omitted 1,088 stereo frames. Its frozen source
and report are retained. The new full digest is a vendor integration identity;
the tail has not been compared sample by sample to an independent decoder.

The one-byte schedule submits exactly 703,584 input fragments and makes
703,587 process calls. The decoder leaves one byte unconsumed once. Retaining
it and appending the next fragment preserves every input byte and yields the
same complete PCM as both larger schedules. The normal 4096/257-byte schedules
need no pending-input copy or allocation for this fixture.

| Measurement | ESP32 LX6 / SDK 6.0.2 | C3 RV32 / pinned SDK 6.1 |
| --- | ---: | ---: |
| Coordinator / worker core | 0 / 1 | 0 / 0 |
| Diagnostic worker priority / stack bytes | 3 / 16384 | 3 / 16384 |
| Free heap before/after each measured stream | 250160 / 250160 | 283080 / 283080 |
| Observed minimum free heap | 203140 | 236096 |
| Worker minimum unused stack bytes | 14196 | 14288 |
| Retained after first use and unregister | 100 | 452 |

Assertions, canaries, heap poisoning, heap integrity and idle watchdogs remain
enabled. Scheduling yields occur only after every 32 completed public process
calls. Persistent first-use retention is reported, not attributed to a codec
leak or logging without evidence. Repeat streams restore their exact heap
baselines; zero total retention is explicitly false.

## Attempts and reader correction

- Attempt 01 on each target cannot activate installed compilers inside the
  sandbox (`WinError 623`); no SDK compiler child or QEMU executes.
- Attempt 02 reaches the native decoder and shows complete EOF output, but
  the diagnostic incorrectly assumes zero first-use retention. Its assertion
  failures, images, sources and original reports remain nonpassing.
- Attempt 03 verifies the historical prefix and stable repeated heap for two
  schedules. One-byte input then reveals the real zero-consumption caller
  defect and motivates the shared pending-input fix. Those failures remain.
- Attempt 04 completes every actual SDK/QEMU child with exit 0 and all native
  assertions pass. Its outer Python reader still returns nonpass because it
  incorrectly requires a retained prefix longer than one byte. A one-byte
  retained prefix is sufficient and is exactly what the decoder reports.

The final reader changes only `pending_max > 1` to `pending_max > 0`.
Data-only replay proves this exact single-predicate difference from each
frozen controller, rechecks every frozen input, all other live input bytes,
all saved build-output hashes and every completed native record. It also
rejects altered zero-coalescing, empty-prefix, missing-feed and truncated
completion transcripts. No compiler or QEMU reruns are used for this reader
correction. The original attempt04 nonpassing reports remain unchanged;
the passing qualification is the separately saved replay verification.

## Retained evidence and limits

`native-captures.zip` and `native-manifest.json` retain all eight campaigns'
frozen sources/public headers/target archives, command logs, terminal statuses,
available images/ELFs/maps/configurations and the final replay/controller.
Identical bytes are stored once under `blobs/<sha256>`; each logical `files`
entry in the manifest gives its original path, byte count, hash and `blob`.
Every logical byte was checked after compaction. Compiler/SDK installations
are identified and pinned rather than republished in full.

Run the standalone data-only verifier from a checkout containing this reader:

```text
python -B tests/verify-espressif-vorbis-checkpoint.py
```

It checks all 799 logical files / 216 physical blobs, the exact reader delta,
original terminal statuses, frozen sources/build outputs and every native
transcript record. It imports the reviewed repository reader, executes no code
from the archive and starts no compiler or emulator.

The archive also retains the three successful current production CYD
`audio_service.c` Xtensa translation-unit compilations. Their host/compile
scope is described in [PENDING_HOST.md](PENDING_HOST.md).

These isolated images are diagnostics, not production firmware for flashing.
They do not execute the whole radio audio task, TLS, display, hardware output,
OTA or malformed/OOM decoder internals. Production task integration, resource
qualification, physical acceptance and broader Vorbis conformance remain
separate requirements. Production cores, priorities, stacks and backends are
unchanged by this diagnostic.
