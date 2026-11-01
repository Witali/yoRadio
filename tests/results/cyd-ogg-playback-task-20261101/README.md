# Actual CYD logical Ogg playback: complete task checkpoint

The current production audio service passes **all ten actual-task cases** on
the pinned dual-core LX6 / ESP-IDF 6.0.2 / public Espressif decoder QEMU profile.
All original complete production TUs, SDK tasks, queues, allocator, state and
health remain active. HTTP transport and output/LED hardware are explicit seams.

For each complete 20 ms Opus, 120 ms Opus and Vorbis fixture, ordered EOF,
partial Stop/discard/reopen, and partial three-owner maintenance/token/stale
rejection/resume pass. Each full output is **2112000 PCM16 stereo bytes at
48 kHz**. Opus uses the independently positioned stock-vendor logical-window
hashes; Vorbis preserves its earlier full output. This is sample-position and
integration qualification, not universal numeric codec conformance.

| Fixture | Complete PCM SHA-256 | Largest original encoded page |
| --- | --- | ---: |
| Opus 20 ms | b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f | 54597 |
| Opus 120 ms | 4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0 | 61475 |
| Vorbis | e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910 | 58231 |

The final playback concatenates **Opus20 -> Vorbis -> Opus120** in one HTTP
session and actual generation. Two genuine HTTP read blocks cross link
boundaries. All three complete logical links are independently hashed; one
PCM EOF follows all **6336000 bytes**, SHA-256
`0d56ce88a31d08d58d5e40a531c69f34bb9cc66a52c76fdb583233a07611dd1b`.
The actual production helper drains/closes/reopens its public decoder between
links. The harness injects no task ACK, generation, terminal marker or readiness.

All **18 real decoders** and **16 SDK HTTP clients** close. There are 5032
actual public process calls, six observed resizes and six immediate real retries.
All five interrupted/complete 120 ms lifecycle handles grow from 12288 to 23040
bytes; the chain witnesses the sixth transition. The unchanged task profiles
and observed unused stack are:

| Owner | Core | Priority | Allocated stack | Observed unused stack |
| --- | ---: | ---: | ---: | ---: |
| Stream | 0 | 3 | 6144 | 3836 |
| Decode | 1 | 5 | 16384 | 3812 |
| Output | 1 | 6 | 4096 | 2540 |

Each complete playback returns to **235600 free heap bytes**; Stop/maintenance
HELD observe 235304. The final largest internal free block is 110580 bytes.
Minimum free heap reaches **52024 bytes during chaining**. These are real global
diagnostic observations with the stated seams; they do not qualify production
HTTP/TLS/TFT margins or justify enabling optional memory optimizations.

The first campaign passes with no reader/source correction or native rerun.
All native commands and the actual SDK driver terminate zero, and every bound
source/tool/image remains unchanged. Actual GCC/Ninja closure contains **11
selected translation units and 421 dependencies**, including the new playback,
page, timeline, trim and public AAC configuration headers. The unrelated private
AAC and custom decoder paths remain unselected. Assertions, heap poisoning,
stack canaries, heap integrity and both idle watchdogs remain enabled.

The initial data-only checkpoint reader used the compiler command's relative
object path without its build-directory prefix. Its original reader/failure
record and initial package remain preserved; the successor joins the actual
object correctly. No native source, report, command status or result changed,
and no native campaign was rerun for this reader correction.

Eighteen in-memory contradictions of the actual transcript are all rejected:
wrong logical length/hash, missing lifecycle/link/page observations, Stop/stale
token errors, intermediate/multiple HTTP EOF, chain generation/input changes,
bad initial/retry capacities or consumed-input handling, owner leaks, wrong task
stack and impossible heap observations. Original native reports/logs are untouched.

```text
python -B tests/results/cyd-ogg-playback-task-20261101/verify.py
```

The data-only verifier imports only the pinned reviewed canonical transcript
reader. It executes no archived code, compiler, decoder or emulator. The archive
stores exact original sources, selected compiler objects/stack records, config,
command logs, child statuses, dependency joins and runtime identities under
deduplicated hash names. Whole executable/image payloads and publication-sensitive
installed header bytes remain local with explicit exact size/hash/role bindings;
they are not copied or encoded. The verifier checks published bytes and omitted
identities without claiming to read those omitted originals. No semantic scanner
override is used.

Diagnostic images must not be flashed as production radio firmware. Other legal
Opus modes/mappings, nonzero output gain, resource failures/backpressure, real
network/TLS/TFT traffic, all physical outputs and long production playback remain
separate requirements. This checkpoint covers these complete three fixtures,
their actual lifecycle behavior and the stated sequential chain.
