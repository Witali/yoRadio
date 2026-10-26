# Xiph VQ range baseline and exact quantization comparison

2026-10-26. Parent implementation: `7380d038f4693b6aa297f6f65788b32252c304bc`.
**Measurement valid; current Xiph full VQ range remains NONPASS.** This is an
audit and reusable regression capture, not a firmware correction or a new native
decoder qualification. See the [integration design](../../../docs/CYD_XIPH_VQ_RANGE_DESIGN.md).

## Actual results

The host build used GCC13.3.0/x86_64-linux-gnu, assertions, ASan/UBSan,
`-fno-sanitize-recover=all`, `-fno-fast-math` and `-ffp-contract=off`. The
library table unit uses the existing allocation ledger; the test's own input
and guarded-output buffers use ordinary host allocations covered by ASan.
All eight final owned commands returned0, their child process groups were
reaped, and execution stderr was empty.

| Measurement | Result |
| --- | ---: |
| Packed scalar words | 14336 |
| Signed/exponent zero words | 2048 |
| Direct lookup1/lookup2 tables | 8225 |
| Exact affine component comparisons | 271626, all equal |
| Scalar differences from specified rational | 10764 |
| Scalar differences where the specified value fits binary32 exactly | 1682 |
| Actual table components unequal to specified rational | 137563 |
| Exact table values altered by field clamping | 8201 |
| Actual float components unequal to exact clamped-field recurrence | 132024 |

The last two counts overlap; they are not a partition. Sequence float rounding
contributes to the last count and is not by itself proof of nonconformance.
The1682 exactly representable scalar differences directly demonstrate an
avoidable range change. For example, packed`0x5a800001` specifies`2^-64` but
the actual helper returns`2^-63`. The inherited Xiph exponent clamp is measured
independently from ordinary rounding. The existing owned quantizer retains the
original fields and exact unsigned multipliers for every captured component.

Coverage includes all1024 exponents, both signs and seven selected mantissas;
both lookup types; sequence on/off; dimension65535; cancellation; full exponent
span; ordinary values; and lookup1's leftover entry16 for entries17/dimensions2.
This is not exhaustive over all32-bit words. Quantization width is16 and
`sparsemap=NULL`. Multi-entry direct descriptors use dummy all-one length
lists and are not complete valid Huffman trees. No actual header parser,
entropy packet, floor, DSP, transform, native target, PCM or radio task runs.

## Preserved attempts

- `host01/`: initial compilation **failed** with GCC`-Werror=type-limits` at
  the test's guarded-output allocation check. No test executable ran. The
  check was rewritten as a division before allocation; no sanitizer, warning
  flag or format bound was disabled. All diagnostics and partial objects remain.
- `host02/`: first successful sanitized capture using the corrected C fixture.
  Its frozen Python reader predates the separate clamp/rounding metrics and
  the self-test control-count label correction. It did not run that self-test.
- `host03/`: final successful sanitized capture and classified exact comparison,
  using the repository's final C fixture and runner. Its complete capture is
  byte-identical to host02. Its source/input hashes were checked before the
  runner reported completion.
- `validation/oracle.*`:14 explicit rational-rounding/root/cancellation controls
  pass, including half-subnormal, normal/subnormal boundary, maximum finite,
  overflow and ties to even.
- `lint/`: actual Xtensa Clang-Tidy analysis of frozen sharedbook, quantization
  and capture units:25 warnings/0 errors. No SDK application or target ran.
- `publication/verify.*`: repository offline verifier returns0; it checks the
  archive, component/source/input/receipt bindings and exact capture again.
  Six corrupted/partial capture controls are rejected. Nothing is extracted,
  compiled or executed from the archive.

Clang reports23 inherited warnings in sharedbook, zero in quant.c, and two
in the new host fixture. The fixture allocation diagnostic follows file-derived
counts; all nonzero/product/addressability checks execute before allocation,
and this test consumes its frozen finite input. The object-representation
diagnostic refers to comparing a descriptor with its own pre-call byte snapshot,
including preserved padding, not equality of independently initialized structs.
Both raw diagnostic traces remain; no suppression was introduced.

## Identities and retained evidence

- Unchanged baseline manifest:
  `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
- Unchanged resource-port manifest:
  `b9cc3c829a816ef8f1a283e23a5b9cc1a45214e9eee541e85560858ed70b0104`.
- Final runner:
  `bdf65c89293e159a5b96cc01880d1e7d3fd57c174ac3772973c105ff3043ae5c`.
- Final C fixture:
  `5bebe07378688c15e670890a0c8271b6a2f1159999167d4460dd011e16380d61`.
- Offline verifier:
  `35c7133f965242b2243baa2205b7fde123e63f8c8605c78a37521c455f3adf77`.
- Final capture:
  `403e529d8b167a39cd6bcb05c010a6877c71a07dcfa4fb0bba36f1ba029159f0`.
- Final classified measurement:
  `2f6c80dd43fa68f69586b70c579ebaee0f238092697d2969afecfca202be877e`.
- [captures.zip](captures.zip):7043418 bytes,1211 members, SHA256
  `29a4fec2ed51dc87c78db94868847cb6c3a262ffb38c6487710c74cbe29c590b`.
- [manifest.json](manifest.json): each member's hash and extent, SHA256
  `bf4a6f61b0daaf999ccce36d82198a48678e1387c5b4afb9bb1c5e301391dc2e`.

The archive includes all three attempt directories, complete frozen source
trees and generated port, actual inputs/captures, objects/binaries, raw compiler
and sanitizer streams, owned process requests/receipts, outer command records,
the Clang analysis, and the capture/collection helpers. These host executables
are test artifacts, not production firmware.

From the task worktree, verify the retained evidence with:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 tests/verify-vorbis-xiph-vq-range-checkpoint.py
```

A fresh host measurement uses the installed WSL/GCC runtime:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 tests/test-vorbis-xiph-vq-range.py --output .build/vorbis-xiph-vq-range-host-fresh --port-manifest-sha256 b9cc3c829a816ef8f1a283e23a5b9cc1a45214e9eee541e85560858ed70b0104
```

No decoder/component implementation or production selection changed. Previous
ordinary31 PCM results remain independent and were not repeated for this test
addition. All deferred scopes, the exact-to-transform integration, native
resource qualification and physical acceptance remain open. The working CYD
stream/decode/output affinity and all display/audio configurations are preserved.
