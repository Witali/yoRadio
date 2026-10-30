# Actual CYD audio tasks with public Espressif Ogg/Opus

The complete production audio service, state, health and decoder registration
execute with ESP-IDF 6.0.2 on dual-core ESP32 QEMU. The real RTOS tasks,
adaptive input, PCM ring and allocators remain enabled. HTTP transport and
physical output/LED calls are explicit seams; SDK HTTP client initialization
and cleanup remain real. No board or external network is used.

The unchanged 706,319-byte `opus-510.ogg` fixture is embedded in the diagnostic.
The task reference is generated from the complete [direct public-vendor
checkpoint](DIRECT.md), rather than inferred from Vorbis or the Opus logical
playback length. All three complete task runs emit **2,115,840 PCM16 stereo
bytes at 48 kHz**, SHA-256
`a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b`.
This is a raw vendor integration reference, not an independent numeric oracle
or a claim of standard-complete playback.

## Passing actual-task run

Campaign 01, its SDK driver child and every native command terminate with exit
0. The original report remains `passed=true`, `completed=true` and
`all_bound_inputs_current=true`. Actual GCC/Ninja records bind 11 translation
units and 416 dependencies to the frozen sources. No source, tool or bound
image changes during the run.

| Case | Actual behavior and observations |
| --- | --- |
| T0 | AUTO detects Ogg; complete raw PCM and checked metadata precede EOF. One real client/container closes. |
| T1 | Stop interrupts 3,840 emitted PCM bytes. The output discard observes exact Stop generation 3. Reopen produces the complete reference; cumulative opens/closes/HTTP cleanup are 3/3/3. |
| T2 | Maintenance interrupts 3,840 PCM bytes and waits for all three owners. Play is rejected while held, resume consumes its token, a stale token is rejected, and automatic resume produces the complete reference. Final opens/closes/HTTP cleanup are 5/5/5. |

Each complete stream makes 1,102 output writes. There are 2,710 public process
calls, no buffer resize requests, no remaining client or decoder handles, and
no recorded pipeline allocation/stream/decode/output health faults. The test
asserts the original 12,288-byte PCM buffer on every public process call.

| Actual task | Core | Priority | Allocated stack | Observed unused stack |
| --- | ---: | ---: | ---: | ---: |
| Stream | 0 | 3 | 6,144 | 4,236 |
| Decode | 1 | 5 | 16,384 | 4,564 |
| Output | 1 | 6 | 4,096 | 2,892 |

Observed final free heap is 235,792 bytes and minimum free heap is 182,548
bytes. Heap integrity, light poisoning, stack canaries, assertions and both
idle watchdogs remain enabled. These numbers describe this diagnostic with
synthetic transport/output, not production radio/TLS/TFT margins or zero total
allocator retention. The separate direct checkpoint records a 100-byte
first-use retention; it does not claim zero total retention.

The reference consumer requires all eight original direct native commands,
eleven mandatory build artifacts, actual SDK child status, the exact dual-core
QEMU flash invocation, pinned vendor archives, and the direct harness/shared
source inputs. A saved host execution accepts the real complete reference and
rejects all 19 missing or changed witness controls. Its actual child status,
stdout, stderr and exact four canonical source snapshots are retained. This
reader check starts no compiler, decoder or emulator.

## Required Opus trimming correction remains open

The actual task preserves the vendor's raw output, including the prefix and
tail that normal playback must discard. The fixture has 528,960 raw frames,
pre-skip 312 and a final EOS granule of 528,312. Correct logical playback has
528,000 frames, or **2,112,000 PCM16 stereo bytes**, after dropping the
312-frame prefix and 648-frame tail. These are container timeline rules from
[RFC 7845 sections 4.2–4.5](https://www.rfc-editor.org/rfc/rfc7845.html#section-4.2).

The direct checkpoint independently verifies all page CRCs and packet/timeline
accounting and preserves a separate FFmpeg/libopus observation with that
logical byte count. Matching the raw vendor hash proves transport, decoder
ownership and task integration; it does not prove correct trimming, exact
alignment, or independent codec numerical conformance. The
[required trimming and alignment work](../../../docs/CYD_OGG_OPUS_EOF.md)
remains explicitly pending. This successful task checkpoint does not close it.

## Saved evidence and verification

`task-captures.zip` stores identical bytes once under `blobs/<sha256>`.
`task-manifest.json` maps every logical file to its exact bytes, size and hash.
The package retains frozen production/harness/public-vendor sources, actual
GCC dependency closures and selected objects, configurations, link maps,
command logs, original reports, SDK child status and the 19-control reader
witness. Unselected replaceable SDK scratch is inventoried by hash.

The separate direct manifest/archive is bound by its exact hash. External
direct-campaign source and artifact runtime entries resolve through that
checkpoint's published bytes or explicit omission provenance. The direct
archive is not duplicated inside the task archive. Original reports and logs
are unchanged; the campaign already uses a safe alias for the local installed
PowerShell runtime identifier, with its executable hash and pre/post checks.

All selected ELF/app/merged-flash/boot/partition image byte payloads remain
unchanged in the ignored local campaigns and are omitted from publication.
Their exact hashes, byte counts, roles and local-only provenance remain in
the manifest. Installed SDK/toolchain headers flagged for contact data are
also omitted entirely, retaining their exact dependency hashes and source
identities. Their original licenses are not rewritten. No semantic scanner
override or encoded copy is used to publish an excluded payload.

Run the standalone data-only verifier:

```text
python -B tests/verify-cyd-opus-task-checkpoint.py
```

It checks every published archive byte and source/artifact/dependency binding,
the original command/SDK child statuses, all three task transcripts and the
negative-control witness. It imports only the pinned reviewed canonical
transcript readers and starts no archived program, compiler, decoder or QEMU.
Omitted image/header provenance is checked by hash; omitted binary bytes are
not claimed to be verified.

The retained images are diagnostics and must not be flashed as production
firmware. Other Opus modes/durations, 120 ms packets and resizing, chaining,
corruption handling, deliberate backpressure, real HTTP/TLS/TFT traffic,
production resource margins, all physical audio backends and board acceptance
remain separate gates.
