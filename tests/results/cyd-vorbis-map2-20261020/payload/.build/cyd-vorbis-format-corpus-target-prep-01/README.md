# Public raw format-corpus caller and protocol proposal

This preparation has no SDK/compiler/QEMU/codec/device/Git execution and changes
no canonical source or historical campaign. Its C caller is not compiled or
target-qualified. `data.h.template` deliberately fails with `#error`: root must
freeze actual raw arrays and their descriptor/contract relation separately.

Scope is the existing 17 named valid-data candidates: eight codebook cases,
nine floor0/residue0 cases, 14 complete packets each, 238 paired packets and
398080 expected PCM bytes. These are generic named cases, not the earlier
36-block-pair matrix. The full completed host report remains unchanged:
`.build/cyd-vorbis-format-corpus-host-01/report.json`, SHA256
`eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29`.
Its Xiph reference qualification is true; its dual-reference qualification is
false. Seven native references succeeded (measured PCM maximum difference 1),
and ten refused lookup2 with `Codebook lookup type not supported`. Those failures
remain failures. This caller adds neither numerical tolerance nor a new result.

`corpus_case.h` is the data ABI. Descriptors retain full identification 30 and
prefixed setup bytes, raw audio, offsets/modes, rate/channels/block lengths and
expected PCM total. `main.c` checks descriptor bounds, public identification
fields, packet modes/neighbors and overlap sizes. It removes seven bytes only
when constructing the public `esp_vorbis_dec_cfg_t`. No comment header is needed
by this public decoder. Two independent opaque handles are opened per case.
The original vendor function executes first on every packet, with separate
input copies; output goes into separate guarded 16384-byte buffers. One public
metadata object is retained per handle, including primer packet 0. The caller
requires complete consumption, exact overlap PCM lengths, vendor/checked PCM
equality, metadata, intact canaries, nonzero samples in each channel for every
output packet, and actual successful public close results.

Coordinator is core 0. Worker is pinned to core 1, priority 3, stack 16384, and
yields after each packet. Core and priority fields come from actual APIs;
`configured_stack` is explicitly a configuration value. Test-only static
capture adds a 32769-byte hex buffer; it does not enlarge the worker stack.
There is no resource-benefit claim. No private codec header/state, simple/Ogg,
EOF/reset/OOM, partial/buffer-shortage or unrelated codec operation is included.

The strict protocol has 530 ordered events: BEGIN, WORKER, then per case OPEN,
14 PAIR/PCM_HEX pairs, CLOSE and CASE, finally COMPLETE. `cases_mask=131071`
represents exactly 17 cases. Every PCM_HEX includes actual public checked output
after guards/equality checks, actual byte count/core and lowercase hex. Primer
hex is empty. A fixed static buffer is used, with no truncation or line folding.

Python API:

```python
contract = protocol.load_contract([
    {"path": books_matrix, "sha256": pinned_books_sha},
    {"path": floor_matrix, "sha256": pinned_floor_sha},
])
observations = protocol.validate_log(
    actual_stdout, contract,
    returncode=actual_returncode,
    timed_out=actual_timeout_boolean,
    interrupted=actual_interruption_boolean,
    manifest_hashes=actual_observed_matrix_hashes_in_source_order,
)
```

Process facts must come from the real controller/child result. Unknown facts,
nonzero status, timeout, interruption, source changes, duplicate/missing/foreign
events, panic, bad metadata/length/order, empty output transitions or malformed
hex are rejected. Sources are reread before and after parsing. The API returns
observations rather than `passed=true`. `case_pcm` contains dictionaries with
`case`, `id`, actual `pcm: bytes`, its SHA256 and 15 byte offsets (including both
zero primer offsets). The controller must save those bytes before JSON-encoding
its report, retaining their hashes/offsets. Recomputed channel nonzero counts
must match PAIR counters. Root independently compares captured PCM with saved
Xiph WAV output and records measured errors and its own acceptance policy.
`vendor_checked_pcm_equal` is only relative equality;
`independent_reference_compared` remains false in this API.

`contract.json` records both exact input matrix hashes, all 53 source identities,
ordered raw payload hashes and the independently checked frame/byte accounting.
Its `contract_sha256` hashes the stable model; use that value in data.h. The
logged identity alone does not prove compiled arrays: root's separate freeze,
source/build/ELF closure and actual SDK campaign remain required. Both strips
must be verified against the actual public headers/compiler later. No actual
ABI/header/build result is inferred from these source files.

`test_protocol.py` runs only synthetic logs and fresh local malformed raw copies.
It captures changed synthetic PCM faithfully instead of silently replacing it
with expected bytes, and makes no independent numerical claim. Example:

```powershell
& $python -B .build/cyd-vorbis-format-corpus-target-prep-01/test_protocol.py `
  --output .build/cyd-vorbis-format-corpus-target-prep-01/host-check01
```

Future target preparation should link only the reviewed public open/decode wraps
with the selected SDK/codec libraries. Root owns that build, generated data.h,
raw terminal stdout/stderr/status and independent PCM comparison. A completed
protocol would still be bounded valid-data evidence, not full Vorbis conformance.
