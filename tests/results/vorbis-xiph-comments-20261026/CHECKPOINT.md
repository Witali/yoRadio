# Independent Xiph comment API qualification, 2026-10-26

**Metadata APIs qualify on host ASan/UBSan and ESP32 QEMU:399 scenarios each.**
This small project executes only comment utilities. Public synthesis/DSP/header
test symbols are absent from its ELF. It neither executes audio decoding nor
resumes the [deferred DSP scheduling gate](../../../docs/CYD_XIPH_DSP_TARGET_DEFERRED_20261026.md);
that gate and its watchdog NONPASS remain unchanged.

## API change

The [new exact info.c edit](../../../idf/components/native_vorbis_xiph_port/edits/info-comment-api.after.c)
removes temporary tag allocation from `vorbis_comment_query` and
`vorbis_comment_query_count`. ASCII-only case folding, duplicate order, literal
separator matching and returned borrowed value pointers are preserved. The
[official query contract](https://xiph.org/vorbis/doc/libvorbis/vorbis_comment_query.html)
keeps the underlying buffer owned by the comment object.

Append prepares a new pointer array, length array and final string before
publishing any change. Each of the three required refusals releases temporary
ownership and leaves the old structure, arrays, strings and vendor untouched.
Existing string addresses and explicit lengths remain stable on success,
including bytes after an embedded NUL in parsed metadata. The public input
strings are copied as the [add API](https://xiph.org/vorbis/doc/libvorbis/vorbis_comment_add.html)
requires; tag append writes its separator/value directly into the final string.
It does not allocate a fourth temporary joined string.

[Private checked variants](../../../idf/components/native_vorbis_xiph_port/include/native_vorbis_xiph_comment_error.h)
return0/OV_EFAULT/OV_EINVAL. The public void signatures remain unchanged and
preserve the existing state on refusal. Length/count/increment/allocation
products are checked before allocation. Failure atomicity does not provide
concurrent mutation synchronization for a shared comment object. Preparing
new arrays may consume more transient storage than an in-place realloc; no
universal heap saving is claimed. Query allocation removal is directly tested.

The materializer now applies24 exact edits across the same10 C units and copies
three owned private headers. All116 original baseline files remain unchanged;
the generated tree contains129 sources plus PORTING.json. The original22
library C units are compiled, with only reachable metadata sections linked.

Base manifest: `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
Port manifest: `decee153fa4d2a02802e13eaf5bb527afc6e2346e0a020265cad7531b97e2e6d`.
Generator: `4ea38a55c69bb4c8dec086972f87b62ef32ca24b9bcf9ef25709b5bdf2bb9928`.
Fixture: `fa56ed8ed50f58507babca311e81b49c57c8973ea4e995e7c2fe176d1dfe7d3f`.

## Tests and actual execution

The [C fixture](../../native/vorbis_xiph_comments.c) covers initialized-empty,
parsed-like empty/vendor and populated9-row objects; checked/public raw/tag
append; all three allocation refusals with successful retry; both zero-size
allocator policies; exact old-state/array/string/vendor and ledger identity;
caller-input guards/copy independence; aliases into existing values; and stable
borrowed query pointers after append. Lookup matrices cover duplicates, ASCII
case, prefix versus separator, empty/raw/no-separator cases, high bytes and
existing embedded-NUL storage. Thirty-two successive duplicate appends and
clear/reinitialize are included.

Armed-failure queries perform zero attempts; the immediately following checked
append still refuses ordinal1. NULL/negative/INT_MAX inputs reject without
allocation. Dummy-array INT_MAX-1 controls require product refusal with zero
attempts on ESP32/ILP32, versus the armed first-allocation refusal on LP64. No
large memory request reaches the system allocator, no fake array is copied,
and those deliberately invalid objects are not passed to clear.

The [host runner](../../test-vorbis-xiph-comments.py) compiles22 library plus3
fixture units with ASan/UBSan and active assertions. All29 owned Linux commands
terminate with reaped children and vanished owned groups; execution stderr is
empty. Initial host394 passes are also retained; five extra scenarios add
representability and armed-query checks without changing implementation.

The [independent native project](../../target/vorbis_xiph_comments_qemu/README.md)
uses SDK6.0.2, core1/priority3/stack16384 with coordinator core0. All9 owned
commands and25 actual compilation rows pass; all130 generated file identities, allocation
injection only into22 library units, symbols/dependencies and22 stack records
are bound. Watchdog and IDLE1 checking stay enabled. All four ordered metadata
events pass with zero live allocations/bytes. The observed minimum free heap
is253216 bytes and remaining worker stack13052 bytes, including fixture state;
these are not production margins or physical performance measurements.

Pure generation16 and metadata protocol6 tests pass. Clang-Tidy completes all25
actual units with311 warnings/zero parse errors. The metadata fixture has six
void-pointer conversion style warnings and four analyzer null reports. The
null traces assume positive comment counts with absent arrays, which its
constructor cannot produce: shape0 has count0/NULL arrays; shape1 has count0/
checked-owned arrays; shape2 has count9/checked-owned arrays and strings.
Snapshot helpers are called directly after construction, and later comparison
helpers require unchanged state or the successful-append array checks. Invalid
count controls never enter them. These controlled-context false positives and
the style findings remain recorded without suppression. The info.c unit has12
warnings; its six new multi-level pointer conversions are ordinary allocated
array/copy/free operations with verified element types. Five inherited GCC
diagnostics and their narrow existing build adapters remain visible.

## Preceding query behavior and archive

A standalone public-API witness reverses only the new metadata edit in info.c,
retaining all preceding header fixes. It adds a normal tag, arms failure1 and
calls query_count. The preceding source uses the refused temporary tag and
UBSan reports its null argument at info.c:119. Its three compile/link commands
exit0 and executable exits1 as expected. This witness calls no decoder or DSP;
its exact source/object/executable, query.c, trace and four owned receipts are
saved alongside the successful current metadata tests.

[captures.zip](captures.zip):1427 members /10412312 bytes.
SHA256: `762a1b1125684908c6ec46e74d377c1706d27bb2a5e4ac88cdc145d6c10da9f2`.
Manifest SHA256: `1178624e5a17dcfb972c6d0ddf678a273dd70a51058742415eb5aa5a615ad777`.
The [offline verifier](../../verify-vorbis-xiph-comments-checkpoint.py) passes
on the saved archive, replaying every member hash, exact source transformations,
host process receipts, preceding query failure, native symbols/config/protocol
and Clang streams. It launches no process, decoder or SDK and extracts no files.
It explicitly keeps decoder_executed=false and dsp_gate_qualified=false.
The raw QEMU images are metadata test fixtures, not production firmware; full
external SDK/tool binary dependency closure is not claimed.

Full current-source PCM/decoder qualification, the deferred DSP gate, packet
allocation handling, remaining format/range, radio integration and physical
acceptance remain open. Production decoder selection, display/audio backends
and task bindings are unchanged.
