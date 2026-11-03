# Ordinary FLAC task checkpoint

The recorded SDK6.0.2/Xtensa/QEMU run uses source commit
`de94a304ab70e0babe7345ac249b43b8d79300ca`, the complete production
`audio_service.c`, state, health and registration translation units, real RTOS
tasks, input/PCM queues and custom FLAC. It preserves the original task profiles.

The actual UART contains three original lifecycle results: ordered EOF/exact
PCM; Stop with held large-block input, followed by a fresh stereo stream; and
three-owner maintenance with stale-token rejection and large-block resume.
The positive phase then completed **382 whole block8192 files** over
**15033371 microseconds of SDK time**. Every complete iteration reports the
expected PCM hash/length, actual owner cleanup, progress, idle subscriptions and
zero workspace/live-owner/failure counts. It stops after the first complete file
that reaches the fixed 15-second threshold, within the unchanged 90-second limit.

The fixture preparation produced **130 encoded/oracle pairs**. This native run
executed **three fixture types**, not all 130. Its expected S16LE byte identities
are recorded in the unchanged fixture manifest. The target performs byte
comparison against the embedded FFmpeg oracle; the data-only verifier checks
recorded comparison flags, lengths and iteration hashes. It does not decode or
recompare excluded PCM bytes itself.

The matched production policy is TWDT 5 seconds, panic disabled, both idle tasks
subscribed, interrupt watchdog 300 ms including CPU1, quiet heap and diagnostics
disabled. The strict UART reader still rejects watchdog warnings under the
no-panic policy. Current Ogg timeline/AAC-Plus selectors remain enabled.
HTTP request-TX release is disabled because synthetic transport never enters the
SDK's connected/header state; its real HTTP qualification is separate.

HTTP transport and immediate public configure/layout/gain/write/flush functions
are explicit seams. HTTP client init/cleanup remain real SDK calls. This is not
the physical output driver, DMA, full radio/TLS/TFT integration, RF, hardware,
native OOM/backpressure/semantic fault injection or a resource-margin benchmark.
Per-iteration heap/stack numbers are observations of this isolated program.

## HOST and provenance scope

The two unchanged HOST receipts remain separately identified: 520 exact PCM
comparisons (130 fixtures across four feeds), 16 HOST lifecycle groups and three
HOST controls; and six decoder/output lifecycle profiles. These counts do not
become additional native test cases or physical output evidence.

Whole binary/media/PCM files and privacy-flagged originals stay complete and
local. The original controller report SHA256 is
`79997c9a1abe9754fdbec423015a11dec9c7e2b474e163f286941c3e7ceeee7a`.
It and the execution bundle contain local runtime paths and are omitted whole.
The package's binding/status index is explicitly author-recorded metadata from
those originals, not a sanitized replacement or an independently authenticated
copy of omitted report bytes. It records tool/image identities, terminal statuses
and unchanged-input results for local review against the original hashes.

Clean original UART, observation/fixture manifests, compiler dependency records,
source/configuration provenance and selected text snapshots independently support
the finite lifecycle/PCM/watchdog observations. The verifier authenticates retained
text hashes and cross-checks the recorded index, but cannot independently reread
omitted tool/image/media payloads or the omitted full report/post-run table.
It does not import captured scripts or invoke tools, builds or tests.

The archive retains 714 whole originals as 709 deduplicated UTF-8 text members.
There are 318 whole omissions, including the full report and execution bundle,
47 SDK/toolchain headers flagged for contact details and the saved production
policy manifest flagged for a private path. The other omissions are binary,
media or PCM payloads. Twelve installed runtime/tool payloads are separately
indexed by opaque locator, basename, size and recorded content hash. No omitted
original is opened by the verifier. All originals and the initial flagged
package candidate remain complete under the local ignored capture/audit roots.

The source table binds 506 historical inputs; the actual compiler closure
identifies 14 translation units and 438 dependencies. Hashes, sizes, source
snapshot links and retained before/after Git/SDK receipts are checked directly.
Privacy-omitted headers and the saved policy manifest have identity metadata
only. Runtime/image identities, normalized command displays, terminal status
rows and the full unchanged-input census come from the authored index anchored
to the omitted report/bundle hashes. They cannot independently authenticate
those omitted payloads or the omitted status table. Recorded compiler entrypoint
dispatch programs are not a complete compiler process/library closure.

```text
python tests/results/cyd-flac-ordinary-task-20261103/verify.py
python tests/results/cyd-flac-ordinary-task-20261103/verify.py --require-current
```

`--require-current` checks only the repository inputs identified as actually
consumed by the compiler or the recorded build/generator/observer/controller
execution: 73 repository files. Generated capture configuration is checked from
retained bytes; it is not a live repository input. Broad metadata-only snapshots
are excluded from that live-source
claim. Frozen historical source/configuration and HOST receipts retain their
own exact identities; the saved production receipt establishes policy provenance,
not current application identity.

## Source commit graph

`source-commit-inventory.json` records exact current bytes for the ten core
diagnostic files: the ordinary controller, its observer and all eight files in
`tests/target/cyd_flac_ordinary_task_qemu/`. Three additional reviewable support
files are the syntax-preparation helper and the source-identity and observer
control tests. These three support files were inspected, not newly executed by
this publication task; their presence adds no test result.

The current target README was updated after capture to link these results and
clarify fresh-launch prerequisites. Only its authored inventory entry tracks
that documentation change. The original frozen README remains unchanged in the
archive, and the 73 actually consumed input pins retain their original bytes.

The ordinary controller does not import an untracked Ogg/full-family controller.
It uses the tracked FLAC fixture generator, tracked production components and
the installed SDK/vendor component. Its actual run consumed explicit ordinary
HOST and six-profile lifecycle receipts and the saved production policy receipt.
Their generators are already tracked (`run-cyd-flac-runtime.py`,
`run-cyd-lifecycle.py` and their native sources). The two extra control tests
import only this ordinary controller or its observer. The optional syntax helper
contains its own Windows argument parser and does not introduce another
untracked Python dependency. Running/building the diagnostic still requires
the documented SDK, QEMU/ROM, FFmpeg, PowerShell and caller-supplied receipts;
none are shipped as executable payloads here.
