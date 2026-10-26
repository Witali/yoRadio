# Xiph header allocation failure and reopen, 2026-10-26

The focused source port passes **1598 header scenarios** under host ASan/UBSan
and ESP32 SDK/QEMU. All original **31 streams, 434 packets and 738560 PCM bytes**
remain bit-identical to the retained references: maximum error0, unchanged
bound2 and all14 original relations. Existing arena/book/bitreader/residue tests
also pass. The [previous residue checkpoint](../vorbis-xiph-residue-20261026/CHECKPOINT.md)
and [unchanged upstream baseline](../vorbis-xiph-20261025/CHECKPOINT.md) remain
separate historical evidence.

## Implementation and failure contract

Seven new [exact edits](../../../idf/components/native_vorbis_xiph_port/edits.json)
cover13 allocation sites in comment/book/floor/residue/mapping/mode parsing.
The existing info-initialization NULL check is also exercised. Required
allocation refusals return **OV_EFAULT**; malformed-header paths retain their
previous codes. [Official headerin documentation](https://xiph.org/vorbis/doc/libvorbis/vorbis_synthesis_headerin.html)
defines OV_EFAULT for internal errors. [info_init](https://xiph.org/vorbis/doc/libvorbis/vorbis_info_init.html)
returns void: on failed setup allocation, the public identification-header
call returns OV_EFAULT, and clear remains safe.

Five checked unpack variants carry a caller-owned `int *failure`. The original
pointer-returning functions remain thin wrappers with their original names,
linkage and registry signatures. Setup parsing uses local typed checked-dispatch
tables, with compile-time assertions matching the pinned floor2/residue3/map1
registries; existing bounds checks precede indexing. No global error flag,
TLS, errno inference, public codec.h ABI change or baseline-header overlay is
introduced. The [owned private interface](../../../idf/components/native_vorbis_xiph_port/include/native_vorbis_xiph_header_error.h)
declares only these checked entry points.

Comment cleanup handles refused vendor/array/individual-string allocations.
Setup cleanup frees partial books/backends/modes before returning the saved
local status. Comments are independently owned and must still be cleared by
the caller after setup failure. Recovery clears both objects and initializes
them again before replaying all three headers; resending setup into the failed
object is not the recovery contract. Legal zero-size NULL allocations remain
accepted where the original parser accepts zero-size books/quantizers.

The materializer now applies16 unique exact edits to9 C units and copies one
owned private header, preserving all116 original baseline files. The generated
tree contains126 source files plus PORTING.json; all22 library C units remain
selected. Public release sources/licenses stay byte-identical in the sibling.

Base manifest: `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
Port manifest: `a5e00f16d4584cd16d5da327e552163002dfbc494a4b47ca309738c9201ae894`.
Generator: `8a67802770fe4bc6cbe0f85514041ee811596466f28a65cd12e28f5cbc3c03d4`.

## Meaningful tests

The [new fixture](../../native/vorbis_xiph_headers.c) sweeps every observed direct
allocation ordinal in info initialization and the three headers for all31
original streams. Each refused required allocation must return OV_EFAULT at
that ordinal, stop further allocation, clear twice without retained owners,
then reopen from fresh objects and validate metadata and the complete setup
graph. The same sweep covers six synthetic setups, floor0/1 × residue0/1/2,
with mapping0 and three comments including an empty string. Thus string
allocation and each supported backend dispatch are exercised explicitly.

Before and after each original stream's entire sweep, full14-packet synthesis
compares two float-bit fingerprints and exact frame/sample counts. Those are
same-process recovery identities, not independent numerical oracles. A full
decode is not repeated after every individual ordinal; each such recovery
does replay and validate all three headers. The separate retained-reference
PCM gate below remains independent of these fingerprints.

Direct ordered/unordered lookup2 book controls exercise the checked and legacy
wrappers, all four syntactic allocation sites, and normal/forced-NULL zero-size
policies for entries2/dim1, entries2/dim0 and entries0/dim1. Original floor,
residue and mapping wrappers have success/first-allocation-failure controls.
Six selected header truncations per original/synthetic stream return BADHEADER
with no refusal; the ID cuts retain version0 to preserve upstream error
precedence. These are finite malformed controls, not all possible cut points.
Input/packet guards and metadata, double-clear zero state, complete ownership
release and both backend type masks are asserted.

Host compiles22 library plus7 fixture units with ASan/UBSan and active asserts.
All33 owned Linux commands terminate normally with reaped children and vanished
owned groups; execution stderr is empty. Existing11 arena scenarios,200864 book
checks,124754 bit probes and3997 residue scenarios pass unchanged.

ESP32 SDK6.0.2/Xtensa runs the same fixture on **core1, priority3, stack16384**,
coordinator core0. All9 native commands terminate normally. All29 selected
compilation rows,22 library stack records, generated-header dependency and42
resource records are bound. Every original stream closes with zero tracked
allocation count/bytes. No vendor audio archive or second decoder is linked.
Separate numerical replay accepts all369280 original native S16 samples and14
relations, with no trim/shift/gain fit or omitted packet/case.

Observed cumulative minimum free heap is106732 bytes; remaining worker stack is
at least14584 bytes. Residue0 retains its32-byte static own frame. These values
include static fixture data and allocator instrumentation, are not production
margins, and do not bound all decoder call trees or transitive libc allocations.
Generation16, protocol12 and PCM/binding12 pure tests pass. Clang-Tidy completes
all29 actual units with310 warnings/zero parse errors, unchanged from the prior
checkpoint; the new header fixture has zero warnings. Five inherited GCC
diagnostics and the narrow existing build adapters remain visible. No sanitizer,
warning or numerical threshold is suppressed for this result.

## Original failure, archive and remaining gates

Replacing only library slot10 with the original info.c, while retaining all
other actual host objects and the new fixture, reproduces UBSan's null-char
store at info.c:45 during comment parsing after an allocation refusal. Compile
and link exit0; the owned executable exits1 as expected before PCM publication.
The source, object, executable, complete trace and nonce-bound command receipts
are saved. The initial exact-marker attempt also remains reproducible: its two
before fragments had a final CRLF where the original source has LF. Rejected
bytes/manifest are retained; the corrected fragments match uniquely. No SDK or
decoder ran with those mismatching markers.

[captures.zip](captures.zip) contains1450 members /14969100 bytes.
SHA256: `036bcc2ca51542e9ba4a6c9c77dda09b05e5ffb7bca14779b1d9f304cb916716`.
Manifest SHA256: `a3ae0d1399184a4a758406b14b4ea7ead9e3c3db5bffde19d0b2f046b1a251b7`.
The [offline verifier](../../verify-vorbis-xiph-headers-checkpoint.py) passes on
this saved ZIP, replaying member hashes, exact edits/header bytes, original
failure, raw protocol/resources, both complete PCM captures and Clang streams.
It launches no decoder/compiler/SDK/process and extracts no files. Publication
receipts are beside this file. Full external SDK/tool/libc binary dependency
closure and independent compiler-execution attestation are not claimed.

Next are DSP/MDCT/look allocation failures and partial cleanup, packet-arena
ownership plus fatal floor/residue propagation, and allocating comment query/add
helpers. Other stack scratch, uint32 rates, floor0 amplitude/VQ ranges, public
runtime integration and production/physical transfer gates remain. This is a
header-parsing resource qualification, not general decoder OOM recovery or full
format conformance. The radio still uses its existing Espressif path, production
task affinities are unchanged, and no physical board was accessed. Saved raw
QEMU fixture images are not production firmware.
