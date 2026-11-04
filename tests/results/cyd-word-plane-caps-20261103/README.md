# Isolated ESP32 word-plane allocation and access

The successful SDK6.0.2/QEMU capture uses public allocation, pointer and heap
APIs on the classic dual-core ESP32 model. It holds a separate 23040-byte
byte-capable DRAM control while allocating eight 11520-byte planes in each of
two separate cases: `INTERNAL | 32BIT` and `INTERNAL | 32BIT | EXEC`.

Both cases allocated **8/8 planes**. Each used **80640 requested bytes of pure
IRAM and 11520 requested bytes of shared D/IRAM**. The D/IRAM address aliases
represent the same physical memory and are counted once. The two cases run
sequentially with cleanup between them; their totals are not simultaneous
allocations. Overlapping capability free-space totals cannot be added as
independent RAM pools.

Every allocated plane was cleared, written and read through aligned volatile
integer word operations, including odd-half read-modify-write neighbor checks.
The actual probe-object disassembly is retained. Separate DRAM scratch remains
byte-capable; no allocated storage is executed as code and no alias is
dereferenced. All six public free/largest measurements returned to their
original values after each real cleanup, with heap integrity passing.

## Original NONPASS and corrected diagnostic

The 1 November capture remains **NONPASS**. Its EXEC32 slot7 allocation reached
an address outside `esp_ptr_executable()`'s public query window and the original
diagnostic asserted that this query must be true for every EXEC allocation.
The pinned SDK's query stops at `SOC_IRAM_HIGH` (`0x400aa000`), whereas the
allocator can return a shared D/IRAM instruction alias through `0x400c0000`.
This diagnostic was wrong; the successor retains the actual false
`executable`/`in_iram` query flags and checks them against the SDK definitions.
It still performs integer data access only. The original report, failure UART
and frozen inputs are preserved; no earlier outcome is relabeled PASS.

The reader receipt records **26 synthetic refusals**, including altered alias
identity, alignment, capabilities, query flags, cleanup, access widths and false
application/extra-RAM claims. Its honest NULL/refusal and high-D/IRAM positive
vectors are parser checks, not native allocation-failure or hardware evidence.

## Evidence and currentness

`manifest.json` records retained reports, UART, command logs, source snapshots,
compiler-dependency/configuration records and recorded SDK/runtime/image
identities. For whole omitted originals it preserves byte-count/hash/provenance
bindings; the public verifier does not read or independently recompute those
omitted bytes. `captures.zip` contains only inspected UTF-8 text/data.
Whole images, ROMs, relocatable objects, executables, tool payloads and any
privacy-flagged originals remain local with byte-count/hash/provenance
omissions. The merged diagnostic flash image is not a production handoff.

The verifier reads this data without importing captured scripts, invoking SDK
tools or executing objects/images. Its package-owned pure UART parser is
AST-compared with the frozen controller's `fields`/`parse` functions and
reconstructs the actual measurements from unchanged UART. The probe's initial
boot/map pure-IRAM extent is separate from the older full-task native06 extent;
neither is an allocation-time free/largest measurement.

```text
python tests/results/cyd-word-plane-caps-20261103/verify.py
python tests/results/cyd-word-plane-caps-20261103/verify.py --require-current
```

Default verification checks the retained execution data and the complete
recorded source/tool/artifact identity graph, including explicit whole-file
omission bindings. `--require-current` checks seven unchanged target/helper
inputs plus one documentation successor: this updated target README has a
separate blob, while its original frozen README remains unchanged in the
archive. These are eight optional currentness entries, not eight compiled
inputs. The full family1 controller was
frozen/imported only for process/hash utilities; both complete controller
snapshots remain exact historical provenance. They are explicitly excluded
from current-source claims, so later family1 source-release edits do not
silently change or require repeating this isolated native result.

This does **not** qualify full application fit, the family1 production decoder,
radio/TLS/TFT coexistence, RF, throughput, physical hardware, native OOM behavior
or execution of allocated code. In particular, the minimal probe's available
memory is not the full radio application's available memory.
