# C3 public raw8192 format evidence

This archive retains the completed isolated RV32/ESP-IDF6.1 baseline,
candidate and restored-old-guard control, original raw logs, actual compiler
context, receipts, source pins, native C3 protocol validator and eight host
tests. It preserves original reports without converting historical failures
into acceptance results.

| Campaign | Native lines | Exact pair packets | Pair PCM bytes | Result |
|---|---:|---:|---:|---|
| Original guard baseline | 285 | 204 | 2452224 | Regression reproduced |
| Two-line removal | 421 | 340 | 4631808 | Format accepted |
| Restored guard control | 279 | 204 | 2452224 | Exact expected failure |

Run `python -B verify_archive.py <absolute-archive-path>` from outside this
directory. The verifier reads only archive files, checks all manifest hashes,
source relations, native core0 protocol/process facts, SDK/macro/recipe pins,
captured ELF243 metadata and promoted source/test receipts. It evaluates the
exact hash-pinned native protocol module; no SDK/compiler/QEMU/codec process
is launched. A terminal0 verifier result is required separately from collection.

Large text is gzip-compressed without altering decoded bytes. Python and fixture
remain raw. Binary images, ELF, libraries, tools and ROM are represented by
size/SHA256 only; the archive cannot replay those omitted binaries. Original
paths in receipts are provenance and are not accessed by the verifier.

The historical original setup bytes and accepted canonical checkout bytes are
distinct records. The published Git-index LF snapshot reversibly maps to the
executed CRLF candidate; the manifest does not equate their raw hashes.

Scope: isolated public raw format only. No production firmware/radio, adapted
canonical CMake build, full G6, Ogg/EOF/reset/OOM, resource/heap saving or physical
audio qualification is claimed. See `PREP.md` for collection and closure details.
