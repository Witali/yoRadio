# Root revision02: checked-only link closure

Baseline01 completed SDK build and macro/symbol commands, then stopped before
QEMU because its inherited symbol check required original vendor open. The
checked-only caller never references that open function and linker garbage
collection correctly removes it. No runtime case was executed by baseline01.
The original NONPASS remains unchanged. This revision requires the two actual
checked wrappers and the actual original decode backend; it removes only the
unused original-open requirement. Production decoder source, caller, protocol,
all17 fixtures and every other SDK/runtime gate remain unchanged.

# Checked-only public raw corpus proposal

Separate source proposal derived from frozen `.build/cyd-vorbis-format-corpus-sdk-prep-01`. Root reported that the original capture panicked in original-vendor open at case6, `sparse_explicit_d4_seq0`, after cases0–5 completed. That campaign, its NONPASS, logs and parser are unchanged. This proposal supplies no replacement vendor oracle and relabels no earlier result.

The new caller uses only checked public `esp_vorbis_dec_open/decode/close` handles. There is no separate original-vendor handle, direct `__real_` call, vendor field or equality assertion in its target protocol. The unchanged production setup/output wrappers still use their normal pinned archive backend; this change removes the separate reference path in the test caller.

## Current exact corpus and future bounds

The current controller requires every original case in order:17 cases,14 packets/case,238 packets,398080 actual PCM bytes,530 protocol events and the full17-bit case mask. It pins exactly the same two source matrices,51 raw payload files and three completed host proof JSONs as the original proposal. There is no case-selection, skip, subset, reorder or fixture-substitution option.

The caller/parser derive case count, total packets, total PCM, completion mask and event count from the pinned header/model. They support a bounded1–31 cases with14 packets/case, stereo only. This does **not** loosen this controller's current qualification: its contract identity, materialized header hash, all17 case/order/reference bindings and exact17/238/398080/530 checks remain mandatory. A future corpus needs separately reviewed source/proof/header/controller pins.

Unchanged current identities:

- contract file SHA256 `6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391`
- contract/model identity `847022a7835de03c0f820b3f8e418e7e8b89b6125d2dba8bdf09712d33d3a65a`
- descriptor header SHA256 `91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3`
- actual root-materialized data.h SHA256 `b4db391fda10e7361f57fe4242574593902042f0e0ef9a48fe24aac144bb153d`
- books matrix SHA256 `38e38f1f5ada7cd84a6ea91c5b46e0680ee62a7f511c9a72bfa7b6d7eb64cd2e`
- floor0 matrix SHA256 `aa1231b8813ac193767c85a2ef339a2da36af52f2af157a16cda9f3d2d438f07`

The host qualification remains17 Xiph-qualified cases, seven native crosschecks and ten native lookup2 refusals; the original dual-reference terminal1 report remains NONPASS. Qualification SHA256 is `d269d71ab02568fcb549c5abf39e4daf8ffcd082b1ede3c259351615768e02b0`, original report `eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29`, terminal receipt `799bb892e5b12e0ccc13fc02607aefe49527f51568d0aecfe8a98ac88c492773`.

## Native checked protocol

Prefix is **`CYD_VORBIS_CHECKED_CORPUS_`**. `BEGIN` binds the contract/counts and actual coordinator0. `WORKER` requires actual core1/priority3/configured stack16384. Every case has checked-only `OPEN`,14 ordered `PACKET` + `PCM_HEX` pairs, checked-only `CLOSE` and `CASE`, followed by the complete corpus event. OPEN/CLOSE require public result0 and a nonnull owned handle where appropriate. PACKET requires actual checked result/consumption, exact overlap bytes, retained rate/channels2/bits16 including primer,16-byte canary success, actual core1 and nonzero output in each channel for every output packet/transition. Primer PCM must be empty.

The strict parser rejects original vendor-prefixed logs, foreign/malformed prefixes, PAIR events, vendor fields, fake equality fields, missing/duplicate/reordered cases or packets, metadata/canary/PCM/hex/count errors, panic, timeout, interruption and nonzero/unknown process results. It reconstructs actual public PCM bytes and returns case hashes/packet offsets. It performs no numerical reference comparison.

The controller pops raw PCM bytes before any JSON assignment, writes17 fresh `.s16le` files, verifies byte/hash/length/offset/file-set identity and records only metadata in JSON. Full original stdout/stderr is retained. Only an actual complete zero-exit target run plus intact persisted output can set `checked_decode_completed` and `target_capture_completed` true. Its result is `CHECKED_CORPUS_PCM_CAPTURED`.

`vendor_checked_pcm_equal=false`, `vendor_comparison_available=false`, `independent_reference_compared=false`, `numeric_reference_qualified=false`, `format_corpus_qualified=false`, general `passed=false`, fullG6 and production-radio flags remain false. Root must separately compare the saved actual PCM with the pinned Xiph WAVs and own the numerical policy/result. No same-vendor equality or numeric PASS is fabricated.

## Source and host evidence

SDK6.0.2/Xtensa, raw setup/output/ABI, audited raw helper, Windows six-line @cflags/specs validation, source/tool/archive/SDK checks, actual setup macros,240MHz/two-core config, ELF94/public symbols, DIO40m4MB offsets0x1000/0x8000/0x10000, QEMU snapshot/headless/no-network/none-audio and bounded owned-process/log handling are inherited unchanged. Source diffs isolate caller/protocol/controller/test and project-name changes. No canonical or existing campaign file was edited.

Gate02 passed eight synthetic host methods and94 named negative controls, with60 input identities unchanged. It includes1/31-case generic positives and0/32 bound rejections, explicit missing/duplicated/reordered case6, wrong case names, old-prefix/vendor-field rejection, primer/final metadata, PCM/hex retention and process facts. Exact command/hashes/logs/exit are in `host-tests-02.command.json`. Gate01 and its pre-generic source snapshot remain under `history/attempt01` and the original gate01 paths; their records were not rewritten. These are pure host tests, not target results.

The project still contains the intentional `#error` data placeholder. Actual materialization is supplied by CLI only into the fresh campaign; root's reviewed header/contract and every source fact are frozen and rechecked. Both supplied file SHAs must match the exact unchanged identities above.

## Root-owned launch

After reviewing the frozen source, root may use the same explicit SDK/tool options as the original controller and a fresh campaign:

```powershell
python -B .build/cyd-vorbis-format-corpus-checked-prep-01/run-cyd-vorbis-format-corpus-checked-qemu.py --output .build/cyd-vorbis-format-corpus-checked-baseline-01 --contract .build/cyd-vorbis-format-corpus-target-prep-01/contract.json --contract-sha256 6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391 --data-header .build/cyd-vorbis-format-corpus-materialize-prep-01/generated01/data.h --data-sha256 b4db391fda10e7361f57fe4242574593902042f0e0ef9a48fe24aac144bb153d
```

This command has not been executed here. `--candidate` selects a source directory under the repository, defaulting to canonical CYD main. Root owns actual checked baseline, any production repair and later target/reference qualification. Keep all inputs unchanged through each run. No SDK/compiler/codec/QEMU/Git/device process was invoked during this prep. Physical gates stay open. Scope excludes target Ogg/EOF/reset, OOM injection, private binary/state inspection, AAC, radio and full conformance.
