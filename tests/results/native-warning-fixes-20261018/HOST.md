# Native warning review and host qualification

The review prioritizes reproducible failures, data loss, object lifetime and
undefined arithmetic. A smaller warning count does not prove absence of defects.
These are host results; no board was flashed or physically measured.

| Finding and scope | Change and evidence |
| --- | --- |
| C3 Vorbis truncated setup: reproduced division by zero and left shift of `-1` | Validate quantization and residue fields before arithmetic; reject packet spans above the signed 32-bit bitreader limit before allocation. [Current](vorbis/report.json), [first failure](vorbis-before-first/failure.log), [second failure](vorbis-before-second/failure.log). 3928 malformed/prefix cases and 187 allocation-failure/retry cases pass ASan/UBSan. |
| C3 Wi-Fi/upload replacement: deleting the live file before a failed rename loses saved data | Reuse the shared recoverable file transaction and serialize recovery/open/publication. [Storage regression matrix](web/report.json) reproduces old Wi-Fi and asset loss, then passes with injected write/close/rename/rollback failures. This does not make the CSV/index pair a single atomic transaction. |
| Oversized physical Wi-Fi rows: a suffix was accepted as another profile | Both targets use [one bounded reader](../../../idf/components/native_storage/include/credential_line.h). [CYD](cyd-wifi/report.json) and [C3](web/report.json) cover fragmented input, NUL/CR/extra tabs, boundaries, EOF and errors; the old CYD source accepts the phantom profile in a negative control. First-valid CYD selection and field whitespace are preserved. |
| C3 file names: unbounded constant copy overflows unusually small configured name capacity | Bound the copy and reject insufficient capacity. [Seven capacities](web/report.json), including 1 and 8, pass; the old capacity-8 code triggers host FORTIFY. |
| Static downloads: rereading after a short failed read and publishing success after failure | Both targets check EOF/error immediately, preserve failures and check close. [C3](web/report.json), [CYD](cyd-static/report.json). Existing [multipart/form/sink](multipart/results.json) tests also pass. |
| C3 asynchronous HTTP session lifetime: queued session close can run before request completion | Shut down the still-owned socket, then complete the asynchronous request. [Executable SDK callback-order model](static-session/report.json) fails on the old helper and passes with ASan/UBSan. Real network scheduling remains a physical acceptance item. |
| C3 PDM interpolation: mixed signed/unsigned rounding relied on implementation-defined conversion | Keep rounding signed in all three implementations. [Wide-reference test](interpolation/report.json): 3654289 exact cases each, all fractions and signed endpoints. [Staged/direct output integration](dma-output/report.json): identical 12331776-byte PCM in four variants; 648 normalizer cases, zero LSB error. |
| Portable FLAC signed fields and wasted-bit reconstruction | Use explicit signed reconstruction and validated reduced depth; preserve signed error codes. [Four field variants](flac-fields/report.json): 323584 signed-field, 3900 wasted-bit and 95 malformed/error cases each. [120 fixtures](flac-depths/report.json): 360 exact FFmpeg comparisons, 456 allocation failures and 456 recoveries. |

The FLAC warning was **not reproduced as a current-path undefined-behavior
failure**: the [original implementation](flac-reference/report.json) passes the
same semantic tests. Its change makes conversions and range guarantees explicit.
Earlier checkpoints also pass [bounds/LPC](flac-bounds/report.json),
[contiguous/bytewise bounds](flac-bounds-bytewise/report.json) and
[Rice](flac-rice/report.json) tests. Each report records its own exact source
hash; final field/depth reports include the subsequent bounded LPC argument cast.

The Vorbis harness executes the actual setup parser with a signed 32-bit
bitreader seam, using native host pointer/long widths. RV32 layout assertions
are removed only from generated host header copies. It does not execute vendor
DSP, validate target private ABI layouts or qualify physical PCM.

Full clang-tidy/Clang Static Analyzer runs complete with zero errors:
[C3: 50 units, 77 warnings](../native-lint-20261018/c3-warning-fixes-final/report.json)
and [CYD: 24 units, 8 warnings](../native-lint-20261018/cyd-warning-fixes/report.json).
Compared by file/check/message with the preceding full baselines, C3 removes
20 warning instances and adds none; CYD retains the same eight. The small
subsequent shared-reader extraction has a separate
[focused rerun of both network units](../native-lint-20261018/shared-credential-focused-final/report.json).
No analyzer or memory-safety check was disabled.

The remaining CYD findings concern enum sentinels/size, conditional duplicate
branches and bounded audio conversions/constant arithmetic. Review found no
reproduced failure in those paths. Remaining C3 findings include private codec
ABI/container views, conversions, comparisons, enum sentinels and diagnostic
dead stores; they are not all declared harmless. In particular, the AAC owner
view warning remains open: no escaping owner was reproduced, and a proposed
reset-view change did not complete qualification. An automatic content check
stopped that assistant task. Its [unverified patch](deferred/README.md) is saved
but is **not applied** to production sources. It needs 32-bit layout/reset
guards and vendor/QEMU PCM regression before reconsideration. No alternate
prompts were used to bypass the check.

Reports retain exact source snapshots and logs. Files under this campaign use
Git `-text` to preserve the raw bytes identified by their hashes. Host filesystem,
RTOS and socket seams do not establish flash power-loss durability, physical
SMP/DMA timing or free heap/stack headroom. SDK compilation and archived firmware
are recorded separately after the source checkpoint is committed.
