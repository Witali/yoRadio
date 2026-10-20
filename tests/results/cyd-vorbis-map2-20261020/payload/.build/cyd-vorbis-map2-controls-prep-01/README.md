# Versioned CYD map2 source controls

These three source-only controls start from the exact fixed CYD setup SHA256
`6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c`.
Each `controls/<name>/candidate` is a self-contained candidate-main directory
containing the same five controller inputs. Only setup.c differs from `fixed/`.
Each control has an exact `fixed-to-control.patch` and inverse
`control-to-fixed.patch`. No canonical files, old preps or campaigns were edited;
no SDK/compiler/QEMU/reference command or target test was run.

| Control | Reverted code only | Changed function | setup SHA256 |
| --- | --- | --- | --- |
| `packed-skip-v1` | General packed lookup2 unused-row discard; the entire new single-active branch stays intact | `_make_words` | `dd216d11f54d8cbe8419b04b74b1bcf8ae5be223834285624fa824a2defd5feb` |
| `wide-rows-v1` | Wide lookup2 active-row compaction/allocation block, restored byte-for-byte from the pinned old source | `repair_vorbis_book_unpack` | `5444e4f7c1dd6bfcf85e8ae53b8af4bb2e5b6a3fe165013a528db6b668fa2160` |
| `mapped-single-v1` | New single-active branch, restored to original n<2 flagged-zero branch | `_make_words` | `c81c799d00616a5aa5cc80b7d2f9854b42bd1fcb9b9902598fdf044eca2506cc` |

The wide control deliberately restores the original allocation expression as
part of that one old source block. This finite valid corpus has tiny bounded
dimensions/entry counts; this is not an allocation/overflow/failure test. The
other two controls retain the checked wide allocation. All controls retain the
fixed unsigned rate checks, raw-only ABI/output inputs and all unrelated code.

## Expected checkpoints, not observed outcomes

The approved expanded order is books8, supplement8, floor0-nine. Every case has14
packets. All25 cases/350 packets/623360 PCM bytes must remain in its contract and
materialized data; there is no case selection or reordered control corpus.

| Control | Earliest expected named case (zero-based) | Completed prerequisites | Source prediction |
| --- | --- | --- | --- |
| packed | 6 `sparse_explicit_d4_seq0` | cases0..5;84 packets;168960 PCM bytes | Checked open rejection from shifted packed lookup2 setup fields |
| wide | 8 `sparse_explicit_d16_seq0` | cases0..7;112 packets;225280 PCM bytes | Checked open rejection from unread original wide rows |
| single | 12 `single_explicit_d2_seq0` | cases0..11;168 packets;337920 PCM bytes | Checked open rejection from unread mapped singleton quants, or decoded-value failure if the shifted header happens to parse |

Case indices and prerequisite totals follow the pinned two construction matrices;
these are not runtime receipts. The parent separately reported that the unchanged
checked baseline rejected case6 at open after its first6 cases. That observation
does not execute or qualify any of these new controls.

For the predicted open failure, require the ordered successful prerequisite
protocol, the expected case/id's OPEN on actual core1 with
`checked_rc=-1 checked_handle=0`, then exactly
`FAILURE case=<expected> packet=0 reason=checked_public_open core=1`.
The current caller emits those public facts; allocation/other error values,
panic, timeout, interruption, missing preceding events and earlier failures do
not establish this expected control result. Keep the actual owned-process exit
facts; this deliberate FAILURE does not become an acceptance PASS.

The predictions must not force the result. A control can instead open and decode
incorrect PCM. Such an outcome needs a separately reviewed numerical witness on
the same named case: preserve actual public result/consumption/metadata/size/
canaries, actual captured PCM, the pinned matching Xiph/fixed comparison and the
first concrete difference. A full target protocol followed by that numerical
mismatch is a capture success and format/numerical NONPASS, not acceptance. A
target `checked_nonzero_each_channel_transition` failure also needs its exact
packet/PCM diagnostics and the independently established nonzero expectation;
do not relabel any generic failure as an effective control. If the actual first
case/phase/reason differs, preserve NONPASS and review it before defining a new
version of a control contract. Do not weaken the existing acceptance validator.

## Safe root-owned launch route

The reviewed checked controller's `--candidate` already accepts a frozen main
source directory under the repository and copies its five inputs into a fresh
campaign/variant before compiling. Supply exactly one of these directories as
that input, rather than swapping canonical setup.c or editing an existing
project/variant. Use a new campaign sibling, with the same reviewed SDK, tool,
archive/ROM, configuration, macro, ELF94, flash and process guards. Record this
control name/hash and verify that the actual consumed setup.c compile row and
variant hash match it. Also retain the fixed candidate comparison result and
unchanged contract/raw-data/reference identities.

For the full25 run this requires root's separately reviewed expanded25 controller
and contract/header. The existing pinned17 controller/data can exercise only the
packed case6 regression; it cannot reach the new wide or singleton cases and
must not be presented as their control. No25 controller is fabricated here.

The intended source argument, after that review, is:

```text
--candidate <repository>/.build/cyd-vorbis-map2-controls-prep-01/controls/<control-name>/candidate
--output <repository>/.build/<fresh-root-selected-control-campaign>
```

Keep the campaign separate from every candidate/prep/input tree and all previous
reports. No command is launched by this proposal. These are public raw valid
format controls; no Ogg/EOF/reset, fault/OOM injection, AAC, private state,
physical-device or full-production claims are introduced.
