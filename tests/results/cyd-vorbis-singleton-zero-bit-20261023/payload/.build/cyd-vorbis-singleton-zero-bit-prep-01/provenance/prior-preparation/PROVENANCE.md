# Provenance and limits

The five source-pins.json original/snapshot pairs retain byte-identical canonical
generate_books.py, generate_map2_regression.py, generate_minimal.py, corpus README
and owned production setup.c. All original paths, sizes and SHA256 values are
recorded. No original is modified. The map2 generator is retained as construction
history only; its codewords(lengths == [1]) exception is intentionally not used
as a sparse singleton decoder. No existing helper function is rebound or replaced.

The new generator uses the canonical book/minimal helper modules by ordinary
explicit importlib loading with their existing pins. Its new eight-case config,
complete floor1/residue0 setup, singleton token writer, metadata and planned
relations are independent additive source. The setup suffix follows the existing
map2 generator's complete public shape, with residue type0. The raw helper source
snapshots retain their original notices and headers. No third-party codec code
or binary is copied into the new executable source.

The independent witness is new stdlib-only source and does not import any
construction helper. It owns its per-bit LSb reader, finite public setup walker,
exact Fraction lookup calculations, original-entry selection, residue0 interleave
and CRC/table/page reader. The control suite is new host-only test source; it may
import both sides for independent comparisons after root approves execution.

Source-only preparation consists of text assembly, Python AST parsing and raw
source hashes. No generator, witness, control, reference decoder, C unit, compiler,
SDK, QEMU, Git, device/COM operation or external mutation is performed. No vendor
library/handle/private field/disassembly is accessed. Source-check receipts and
readiness deliberately retain runtime_executed=false. Future root commands must
preserve actual terminal facts and qualify each subsequent gate separately.
