# Actual CYD task pipeline with Espressif Vorbis

The complete unchanged production audio service, state, health and decoder
registration execute with ESP-IDF 6.0.2 on dual-core ESP32 QEMU. The actual RTOS
tasks, adaptive input, PCM ring, allocation and public Espressif Ogg/Vorbis
decoder are enabled. HTTP transport and hardware output/LED are explicit test
seams; HTTP client initialization and cleanup remain real SDK calls.

The embedded encoded-only fixture is 703,584 bytes, SHA-256
`09d6cfa599f2c4a25f5745e5c8a605b5a1583a42d7990b9e5242b8990adff12f`.
Every full output contains 2,112,000 PCM16 stereo bytes at 48 kHz, SHA-256
`e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910`.
This is the [frozen direct-vendor integration reference](../cyd-espressif-reuse-20261030/NATIVE.md),
not an independent numeric or listening-quality oracle.

## Passing actual-task run

Attempt 02 completes all native commands and the SDK driver child with exit 0.
Its original report remains `passed=true`, `completed=true` and
`all_bound_inputs_current=true`. Every frozen input and selected build artifact
was checked again when saving this checkpoint. The earlier attempt remains
historical and nonpassing; its source snapshots are not replaced by the fix.

| Case | Actual behavior and observations |
| --- | --- |
| T0 | AUTO detects Ogg, exact complete PCM precedes EOF, metadata is checked; one container/client closes. |
| T1 | Stop interrupts 6,912 emitted PCM bytes; output discard observes the exact Stop generation 3. Reopen produces the complete reference; cumulative opens/closes/HTTP cleanup are 3/3/3. |
| T2 | Maintenance interrupts 3,840 PCM bytes and waits for all three owners. Play is blocked while held, resume consumes its token, a stale token is rejected, and automatic resume produces the complete reference. Final opens/closes/HTTP cleanup are 5/5/5. |

Each full stream makes 1,044 output writes. There are 2,682 public process
calls in total, no buffer resize requests, no remaining client or decoder
handles and no recorded pipeline allocation/stream/decode/output health faults.

The Stop scenario logs `PCM buffer stalled` when a blocked send observes the
new generation and returns cancellation. The generation barrier and zero health
fault checks distinguish this from a tested output-failure scenario. This is
not a deliberate backpressure or slow-consumer qualification.

| Actual task | Core | Priority | Allocated stack | Observed unused stack |
| --- | ---: | ---: | ---: | ---: |
| Stream | 0 | 3 | 6,144 | 4,204 |
| Decode | 1 | 5 | 16,384 | 14,580 |
| Output | 1 | 6 | 4,096 | 2,892 |

Final observed free heap is 235,792 bytes; minimum observed free heap is
169,476 bytes. Heap integrity, light poisoning, stack canaries, assertions and
both idle watchdogs stay enabled. These figures describe this diagnostic with
synthetic transport/output, not production radio/TLS/TFT margins. The original
core affinities, priorities and stacks are preserved.

## Preserved original failure and public-call diagnosis

Attempt 01 builds and its emulator exits 0, but the target assertion
`all_pcm_precedes_eof` fails. Its outer qualification is therefore nonpassing;
an emulator exit code alone does not establish success. The public output seam
observes only 2,110,464 PCM bytes, 1,536 short of the complete reference.

Read-only GDB probes use this exact original ELF/flash. They read application
test counters and public simple-decoder input/output fields after real calls,
using normal debugger breakpoints. They do not change arguments, assign codec
state, rebuild an image or inspect private vendor decoder layouts.

The final public trace covers native counters 1 through 538 without gaps.
Consumed encoded bytes sum to exactly 703,584, matching the synthetic transport
position. Decoded PCM sums to exactly 2,110,464, matching output. All results
are successful. The last data call has `len=862`, `eos=0`, consumes 862 bytes
and emits 512 PCM bytes. The sole EOF call has `len=0`, consumes zero and emits
zero. Thus this run loses no encoded input or queued PCM: the missing tail is
already absent at the public decoder output when EOF arrives separately.

The correction retains the genuine final Ogg byte until the following input
or terminal control arrives, supplies that byte with EOS, then drains empty
EOS until neither consumption nor PCM remains. Other codecs keep their prior
input path. This is caller integration with the existing vendor decoder; it
does not introduce another synthesis implementation.

Diagnostic attempts are kept separately from qualification:

- The first public-trace launcher has a GDB directory typo and starts no native
  child. Its source and original failure report remain saved.
- The second trace reaches the public EOF seam, but its aggregate reader fails
  because debugger line hits can repeat. Its original report stays nonpassing.
- The third trace records the native call counter. Of 540 debugger hits, only
  identical repeated records for counters 101 and 110 are collapsed. All 538
  unique records, the exact duplicate audit, logs and original reports remain
  saved. GDB exits 0 and each debugger-owned QEMU process has terminal status 1
  after observation/detach/cleanup; these runs are diagnostic, not passing
  emulator qualification runs.

## Saved evidence and replay

`native-captures.zip` stores identical bytes once under `blobs/<sha256>`.
`native-manifest.json` maps every logical path to its bytes, hash and blob.
Both task campaigns retain complete repository/harness/vendor source and public
headers/target archives, actual GCC/Ninja dependency closures and selected object files,
configuration, link maps, command logs and SDK child statuses. The GDB
probes, failed diagnostic attempts and their helpers are also retained.
Replaceable unselected SDK scratch is inventoried by hash instead of copied.
The ancestor direct-vendor archive is identified by its exact hash; its
manifest and selected reference records are saved without duplicating that
33 MB archive.

Two execution-bundle runtime identifier keys contained an installed PowerShell
path below the local user home. The published metadata replaces only those
keys with `runtime-path-redacted:pwsh.exe`; original and published hashes and
the exact transformation scope are recorded in `inventory/privacy-views.json`.
Original bundles remain locally unchanged. All native reports and published
source bytes remain exact. Forty-seven installed SDK/toolchain headers
(94 logical copies) contain author contact strings. Their bytes are excluded
from publication; their exact hashes, original installation/source identities
and actual dependency bindings remain in the manifests. This is not a claim
that those omitted installation files were completely byte-copied.

Automatic approval review declined publication of the flagged application
ELF/app/merged-flash payloads. The public archive therefore omits all six such
payloads, along with the parser-proof source/inventory and previous verifier.
Original compiled images remain unchanged in ignored local campaigns. The
published omission manifest retains each exact image hash, byte count, role
and local-only provenance; it does not contain those image bytes or an encoded
copy. The revised verifier is included as matching reviewed canonical source.
No semantic classification override is used to publish a flagged payload.

Run the standalone data-only verifier:

```text
python -B tests/verify-cyd-vorbis-task-checkpoint.py
```

It checks every published byte, source/artifact/dependency binding, original child
status and reference identity. It imports only the pinned reviewed canonical
controller to validate the passing transcript. It independently recounts the
public-call trace and its duplicates. It checks explicit omitted-image hash
provenance against the original source/build/debug records, without claiming
to validate the omitted binary bytes. No archived program is executed and no
compiler, decoder, debugger or emulator is started.

The retained images are diagnostics and must not be flashed as production
radio firmware. Physical audio, real HTTP/TLS, DMA/TFT, deliberate output
backpressure, decoder allocation-failure internals, production resource and
timing margins, OTA and universal Vorbis conformance remain separate gates.
