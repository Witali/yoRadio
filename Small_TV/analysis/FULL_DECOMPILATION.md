# Complete factory-code export — 3 November 2026

The factory application and second-stage bootloader now have complete exports
of every function recognized in the analyzed executable regions. This replaces
the earlier selected-function view for further investigation; it does not
replace the reviewed 176-function port inventory or prove behavioral parity.

| Observation | Application | Bootloader |
|---|---:|---:|
| Functions exported and independently indexed | 5,201 | 106 |
| Functions producing C pseudocode | 5,201 | 106 |
| Functions with decompiler warnings | 872 | 51 |
| Instructions checked against original ELF bytes | 287,093 | 4,811 |
| Decoded executable bytes | 811,438 / 813,936 | 13,862 / 13,908 |
| Decoded byte coverage | 99.6931% | 99.6693% |
| Undecoded executable bytes | 2,498 | 46 |
| Decoded instruction bytes without a function | 8,562 | 0 |

The combined result is **5,307 functions and 291,904 verified instructions**.
The counters, output hashes, tool hashes and limitations are preserved in
[`full-decompilation-20261103.json`](full-decompilation-20261103.json).

## Local artifacts

In `.worktree/small-tv-parity-20261103`:

- Application: `.build/factory-full-20261103/expanded/`.
- Bootloader: `.build/factory-bootloader-20261103/export/`.
- Baseline application export: `.build/factory-full-20261103/export/`.
- SDK match and recovery reports: `.build/factory-full-20261103/`.
- Independent checks: `verification-complete.json` in each analysis directory.

Each export contains `all-functions.c`, `functions.jsonl`, `instructions.asm`,
`computed-flows.jsonl`, `code-gaps.jsonl` and `report.json`. The C file is Ghidra
pseudocode with address and status markers, not the manufacturer's source or
a compilable replacement firmware. Raw exports and logs stay local under
ignored `.build/`; they were not committed, pushed or uploaded.

## Analysis and recovery

Ghidra **12.0.4**, `RISCV:LE:32:default:gcc`, processed a private copy of the
existing `SmallTV` project. The original application ELF remains pinned to
`8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882`.
Reviewed names from `src/symbol-map.json` seed the application entry list.

The first pass exported 5,140 application functions. The next pass applied the
previously verified ten runtime boundaries, including `_panic_handler`,
nothrow allocation and C++ exception helpers. `match_wifi_gaps.py` considered
1,896 original Wi-Fi SDK function models and found 53 unique complete matches
in unowned/undecoded regions. All 53 were recovered without stealing another
function's body. Ambiguous matches remained unresolved. Their names retain a
`sdk_candidate_` prefix because not every global binding is independently
proved. All 32 hardware-vector jumps were decoded, and the shared hardware
interrupt entry was recovered. Both recovery reports confirm unchanged
initialized program bytes. Further direct-call discovery produced the final
5,201-function export.

`prepare_bootloader_analysis.py` separately validates the exact 4 MiB dump,
the bootloader image checksum and appended SHA-256, then extracts only its
three initialized segments before the partition table. The bootloader image
is 19,536 bytes, entry `0x403ac37a`; its analysis ELF hash is
`d4cbef2f8d812f9b2d7451e3f5979c31003d71c0064f5bf7c36384fbcc65b8d2`.
The synthetic BSS helps analysis and is not a measured RAM allocation.
NVS, private settings and media are not included in either code export.

`verify_full_export.py` independently checks each instruction's literal bytes
against the ELF, rejects overlaps, verifies executable gap accounting and
checks every pseudocode block against its index and digest. Four deliberately
invalid application exports were rejected: altered instruction, missing
function, changed pseudocode and missing gap inventory. These checks establish
artifact integrity, not correct recovered types or semantics.

## Reproduction

Use a fresh output directory and a copy of the existing analyzed project.
Keep original ELF, SDK libraries and Ghidra database unchanged. The local
Ghidra installation is `.build/ghidra/ghidra_12.0.4_PUBLIC` under the repository
root; Python/pyelftools are the existing `.idf` and oracle dependencies.

1. Copy `SmallTV.gpr` and `SmallTV.rep` from
   `.build/small-tv-reverse/ghidra-project` into the new task output.
2. Write an address/name TSV from `src/symbol-map.json`. Run headless
   `-process factory-analysis.elf -noanalysis -postScript ExportAllFunctions.java`
   with the fresh export directory and TSV as script arguments.
3. Run `match_wifi_gaps.py --elf <factory-analysis.elf> --sdk <original-sdk-dir>
   --gaps <first-export/code-gaps.jsonl> --output <new-match.json>`.
   The tool requires the pinned original `libnet80211.a` and `libpp.a` hashes.
4. Decompress the hash-checked runtime manifest referenced by
   `qemu/parity/runtime-metadata-validation-20261026.json`. Copy
   `RecoverFactoryRuntime.java`, `RecoverMatchedFunctions.java` and
   `ExportAllFunctions.java` into one private script directory. A single
   script path avoids Windows launcher's semicolon argument splitting.
5. In one headless `-readOnly -noanalysis` session, run those three post scripts
   in order: runtime manifest/new report; SDK match/new report; new full export
   directory/name TSV. Metadata changes are visible to the final exporter in
   that session and discarded when it closes.
6. Run `prepare_bootloader_analysis.py --dump <full-flash.bin> --output <new-dir>`.
   Import its analysis ELF into a new Ghidra project with the same processor
   and compiler profile. Run `ExportAllFunctions.java` after auto-analysis,
   passing export directory, generated TSV and the exact ELF SHA from
   `image-map.json` as the third script argument.
7. Run `verify_full_export.py --elf <analysis.elf> --export <export-dir>
   --output <new-verification.json>`. For the bootloader, also pass
   `--expected-elf-sha256 <image-map ELF hash>`.

The scripts refuse to overwrite existing reports. Exporting only initialized
code segments avoids materializing private settings; do not publish raw
decompiler output without inspecting it under the repository's data rules.

## Remaining work

Application gaps comprise 60 undecoded ranges and 95 unowned instruction
ranges. Executable sections can contain literal data, alignment and deliberate
trap instructions; an unrecognized byte is not automatically a missing
function. Some GNU/Ghidra bad-instruction warnings correspond to actual
`unimp` trap instructions and require preserving their nonreturning semantics.

Warnings include overlapping globals, indirect control flow and jump tables.
Computed-flow inventories also include ordinary returns, so their row count
must not be described as unresolved calls. Resolve remaining owners, callback
tables, types and global lifetimes against original bytes and SDK evidence.
Then expand the firmware correspondence and regression tests. Complete feature
parity, remaining bug fixes, long-run acceptance and physical-board checks
are still open; no device was flashed or reset during this work.
