# ESP8266 Opus assembly backends

`lx106/gcc/` is the complete GCC 8.4/O3/fixed-point upstream decoder snapshot,
not handwritten source. Do not edit the baseline: use the overlay recipe in
`tools/esp8266_opus_asm/`. `lx106/optimized/` contains only changed units.

Every function retains GCC verbose C/operand annotations, ABI notes and source
context. See `docs/ESP8266_OPUS_ASM_EXPERIMENT.md` at the repository root for
configuration, tests, exact coverage and remaining physical qualification.

The default backend is C. All ASM modes are diagnostic and pinned to the
manifest's source/header hashes and compile-time feature set. SDK adapters,
container demuxing and memory ownership remain the existing C implementation.

Upstream copyrights and redistribution terms are in `../upstream/COPYING`
and the original C source headers, retained with this source distribution.
