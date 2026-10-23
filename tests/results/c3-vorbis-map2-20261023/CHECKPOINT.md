# C3 lookup2 and mapped singleton checkpoint — 2026-10-23

The C3 setup parser now reads every original lookup2 multiplicand row, retains
active wide rows in used-entry order, and publishes both bit branches of a
mapped singleton. Only `_make_words` and `repair_vorbis_book_unpack` changed.
Raw CRLF and all bytes outside those functions are preserved. The actual C3
source changes from `f3d8b3ff1cb8d2cef675eb742be35f3e6a4533b3e10fbd368aacd929a10fcac0`
to `ce2eed3cdb80ded721623a3e57675ffeac88882d99e7a41f2d5cf9c85d3e1d87`.

The baseline SDK/QEMU campaign really returned NONPASS: case6
`sparse_explicit_d4_seq0` returned open−1/null after six cases and84 packets,
without panic. All seven owned child commands, including QEMU, exited0.
After the change, all25 cases,350 packets,623360 PCM bytes and778 native events
completed. All nine owned commands and the direct tool invocation exited0.
The first188 native events, including168960 PCM bytes, are byte-equal before
and after the change. Original baseline NONPASS evidence is retained.

These are independent ESP32-C3 SDK6.1/RV32 results: SDK revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`, ELF machine243, ILP32,160MHz,
unicore and coordinator/worker core0. Actual compile/macro context, generated
RV32 cflags/specs, map, source snapshots, logs, process facts and terminal
receipts are retained. The full C3 application and its deferred AAC hooks were
never configured. Production task affinities, ABI, synthesis/MDCT and output
code are unchanged. CYD retains stream core0 and decoder/output core1.

The independent full25 numerical measurement completed and remains NONPASS.
The predeclared maximum2 S16 LSB is an engineering regression criterion, not
a normative Vorbis tolerance. Direct comparison uses every original zero-lag
L/R sample without gain, trimming, resampling or channel changes.

| Cases | Count | Maximum absolute PCM16 error versus Xiph |
| --- | ---: | --- |
| Original books | 8 | 1 |
| Wide D16 lookup2 | 4 | 65535 |
| Mapped singletons and dense twins | 4 | 1 |
| Floor1/residue0 controls | 3 | 1 |
| Floor0 even6, three block pairs | 3 | 40664 / 1649 / 40664 |
| Floor0 odd5, three block pairs | 3 | 65535 / 65535 / 65535 |

Both wide sparse/dense target PCM equality relations fail; the other six
declared target relations pass. All eight Xiph relations pass. Full25 and the
declared books16 subgroup both remain rejected. The numerical report hash is
`129a992939260ef59d07671c510cd911958f203f3754caf8fab57fea3585bfe7`.
The original17 and additional8 host dual-reference NONPASS results and native
lookup2 refusals remain unchanged, with their separately qualified Xiph data.

A separate direct comparison of saved C3/CYD PCM finds21 byte-equal cases.
Exactly the four wide D16 cases differ across architectures. This observation
does not identify a backend defect or qualify the format.

This archive requires the committed sibling
`../cyd-vorbis-map2-20261020/`, manifest
`c3e1fa16adb85d25f90339a9d4c74b6c0cbc9feac3d4097624bbe1d6553bd11c`.
Shared historical reference entries use explicit original-path manifest keys;
actual C3 snapshots remain local. Large retained data uses lossless gzip.
Target/tool binaries are hash-only omissions, with actual ELF header bytes.
These QEMU fixture apps are not production firmware.

`README.md` records source preparation and offline verification commands.
The verifier checks archived bytes, actual protocol/process evidence, full
PCM metrics and relations while preserving both NONPASS outcomes. Verification
of evidence is distinct from numerical acceptance. Full G6, floor0/wide PCM,
remaining singleton/quant-width coverage, radio integration and physical
acceptance remain open. No board, COM port, flash or network device was used.
