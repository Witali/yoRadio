# Actual CYD tasks: 120 ms Opus packets and real output resizing

The complete unchanged production audio service, state, health and decoder
registration pass on ESP-IDF 6.0.2 / dual-core LX6 QEMU with the full legal
120 ms Opus fixture. Actual RTOS tasks, SDK queues, allocation and public vendor
decoding remain enabled. HTTP transport and output/LED hardware are explicit
test seams; real SDK client initialization and cleanup remain active.

Each complete playback produces **2,119,680 raw PCM16 stereo bytes at 48 kHz**,
SHA-256 `670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684`,
through 736 actual output writes. This matches the separately qualified
[fragmented-input public-vendor reference](STREAM_RESIZE.md). The controller
rechecks that campaign's actual native commands, logs, SDK child, source/image
hashes and complete PCM before generating the task's reference header.

| Case | Actual behavior |
| --- | --- |
| T0 | AUTO selects Ogg; all raw PCM precedes ordered EOF. One real decoder/client closes. |
| T1 | Stop interrupts 23,040 PCM bytes. The output owner observes the exact Stop/discard generation 3; reopen produces the complete reference. Cumulative decoder/client cleanup reaches 3/3. |
| T2 | Maintenance interrupts 23,040 PCM bytes and waits for all three owners. Play is blocked while held, resume consumes its token, a stale token is rejected, and automatic resume produces the complete reference. Final cleanup reaches 5/5. |

## Observed production buffer transitions

The public process observer reads actual arguments and results. It never
changes vendor arguments, decoder layouts or application control/ACK state.
Every handle starts with the original 12,288-byte production allocation.

| Handle | Purpose | Public calls | Resize call | Global resize call | Real resize/retry pairs |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | T0 complete | 698 | 11 | 11 | 1 |
| 2 | T1 interrupted | 19 | 10 | 708 | 1 |
| 3 | T1 reopen complete | 697 | 10 | 727 | 1 |
| 4 | T2 interrupted | 19 | 10 | 1424 | 1 |
| 5 | T2 resume complete | 697 | 10 | 1443 | 1 |

Each real `BUFFER_NOT_ENOUGH` result is `-8`, with input length 2047, EOS false,
capacity 12288, consumed zero, decoded size zero and needed size 23040. The
immediately following real call uses capacity 23040 and unchanged encoded input
arguments; it consumes 2047 bytes, emits 23040 PCM bytes and returns success.
All five handles subsequently close. These are observed events, not a resize
count supplied to the application or inferred only from a terminal summary.

The standalone verifier independently tokenizes and recounts all five initial,
error, retry and close records. It also checks ten contradictory in-memory
transcripts: missing resize/close, incorrect needed/initial/retry capacities,
nonzero error consumption/output, changed retry arguments/counter and incorrect
terminal resize count. All are rejected. Original saved logs remain unchanged.

## Scheduling, health and preserved evidence

| Actual owner | Core | Priority | Allocated stack | Observed unused stack |
| --- | ---: | ---: | ---: | ---: |
| Stream | 0 | 3 | 6144 | 4204 |
| Decoder | 1 | 5 | 16384 | 4500 |
| Output | 1 | 6 | 4096 | 2892 |

Final observed free heap is 235744 bytes; minimum observed free heap is 166932
bytes. There are 2130 actual public process calls, five observed resizes and
five immediate retries. All five real clients and decoders close; none remains
live, and no pipeline allocation/stream/decode/output health fault is recorded.
Assertions, stack canaries, light heap poisoning, heap integrity and both idle
watchdogs stay enabled. These figures describe this diagnostic with its stated
seams, not production HTTP/TLS/TFT memory or timing margins.

The original outer report is `passed=true`, `completed=true` and
`all_bound_inputs_current=true`. Actual SDK build, compiler-driver child, QEMU
and every other native command terminate with exit 0. The actual GCC/Ninja
closure contains all 11 selected translation units and 416 dependencies,
including full production TUs and shared input/queue/network helpers.

`long-task-captures.zip` stores identical bytes once under `blobs/<sha256>`.
`long-task-manifest.json` maps logical paths to exact size/hash/blob records.
Sources, generated reference, selected compiler objects/stack records,
configuration, link maps, original command logs, child statuses and compiler
dependency bindings are retained. The separate fragmented checkpoint is pinned
by manifest/archive hashes; its full archive is not duplicated.

All application, merged-flash, boot/partition and compiler-probe image bytes
remain local, including executable ELF payloads regardless of filename. The
public manifest retains exact original hashes, byte counts, roles and explicit
local-only provenance. Flagged installed SDK/toolchain header bytes are omitted
entirely while their unchanged original identities and dependency hashes remain.
No semantic scanner override or encoded image copy is used. The verifier checks
published bytes and omission hash bindings, without claiming to read omitted
binary bytes. Original images remain in the ignored local campaign and must
not be flashed as production radio firmware.

```text
python -B tests/verify-cyd-opus-long-task-checkpoint.py
```

This data-only verifier imports only pinned reviewed canonical readers. It
executes no archived program, compiler, decoder or emulator.

## Required remaining scope

The raw vendor identity remains distinct from standard playback. The fixture
contains 529920 raw stereo frames; pre-skip is 312 and end padding is 1608, so
logical playback requires 528000 frames / 2112000 PCM16 stereo bytes. Correct
pre-skip/end trimming and exact sample alignment remain required work in
[the Ogg/Opus plan](../../../docs/CYD_OGG_OPUS_EOF.md). Passing task resizing
does not close that gap or prove universal Opus conformance.

Nonzero consumption on a resize error and empty-input retry remain unexercised.
Output-allocation failure, deliberate backpressure, real network/TLS/TFT traffic,
production resource margins and physical audio remain separate qualifications.
