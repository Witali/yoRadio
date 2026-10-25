# CYD Vorbis/Ogg repair transfer

Stage CYD-C3-14 of the [transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md) remains
open. The [read-only Xtensa audit](../tests/results/cyd-vorbis-xtensa-audit-20261020/README.md)
examines the actual installed Espressif 2.6.2 ESP32 archives, rather than
assuming that the C3 binary layout carries over. It does not execute a decoder
or qualify a repair. A later isolated implementation checkpoint is described
below. The previously deferred AAC private-owner work is excluded.

## Isolated implementation checkpoint, 2026-10-20

Commit `cbb69fdad` adds the separate ESP32
[setup/open bridge](../idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c),
[Ogg adapter](../idf/esp32-cyd2usb-native/main/vorbis_repair/simple.c),
[output preflight](../idf/esp32-cyd2usb-native/main/vorbis_repair/output.c),
[typed ABI assertions](../idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h)
and [exact-archive build guard](../idf/esp32-cyd2usb-native/main/compat/vorbis_repair/enable.cmake).
These sources are used by the standalone target project; production radio
registration, Kconfig and the audio task do not enable them yet.

The [frozen qualification archive](../tests/results/cyd-vorbis-bridge-20261020/README.md)
records actual SDK6.0.2/Xtensa execution of all three canonical translation
units, with the coordinator on core0 and decoding on core1. For one fixture,
535 raw audio packets produce 2,112,000 bytes of per-packet exact PCM against
the original ESP32 ample-buffer decoder. The 1,602 undersized retries preserve
input consumption and the observed wrapper/DSP/history state. An independent
variant bypassing preflight fails the exact `rejected_dsp_unchanged` assertion.
Twenty-one real CMake configurations pass their expected outcomes: three
accepted and eighteen rejected. Final normalized-source runs are `raw-02`,
`raw-control-02` and `config-02`; earlier drafts and pre-normalization runs are
historical evidence only.

This partially exercises G1/G2/G3/G7. It does not close any whole gate: complete
callback binding, Ogg EOF/reset, allocation failures and reopen, concurrent
task-local scopes, broader codebook/format coverage, actual audio-task
integration, final static analysis/application exports and physical resource
measurements remain. The stripped vendor objects only partly corroborate
private layouts; compiler assertions and this fixture do not prove every field's
vendor semantics. The later raw8192 checkpoint resolves one inherited
rate/block-size restriction. No memory, speed or full conformance claim follows
from either checkpoint.

## Raw8192 format checkpoint, 2026-10-20

The default identification parser rejected 8192 long blocks below 64000 Hz.
[Vorbis I, section 4.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html) permits
those block sizes independently of the positive rate. The two-line fix removes
only that default branch; the optional `LIMIT_TO_64kHz` policy and the ordinary
rate, channel, block-order, block-bound and framing checks remain.

The [public raw target](../tests/target/cyd_vorbis_format_qemu/README.md) uses
opaque handles, complete packets and ample guarded output buffers. The
[frozen results](../tests/results/cyd-vorbis-format-20261020/README.md) record
SDK6.0.2/Xtensa execution: the original vendor first decodes all 68 packets at
8192 blocks, including 66 full 16384-byte outputs. Five original/checked pairs
then compare 340 packets and 4631808 PCM bytes exactly: four 8192-block rates
(192000, 64000, 63999 and 48000 Hz) and an ordinary 48000 Hz / 2048 control.
All four malformed identification headers still reject. A separate control
restores the original setup bytes and reaches exactly
`legal_candidate_open_required` after the full vendor/high/ordinary checks.

Ten host tests cover the runner's packet protocol, metadata, quoting and
generated compiler-input handling. Earlier metadata-lifetime and unsupported
response-file attempts remain NONPASS; the baseline's unchanged SDK build was
completed manually with a separate qualification record. Public metadata is
retained per opened handle and checked on every packet, including priming.
The generated cflags/specs remain byte-identical before and after probing.

This selected nonzero stereo floor1 fixture advances G6 and G7 only for this
restriction. Other formats, Ogg, callbacks, allocation/lifetime, SMP service,
radio integration and physical resources remain open. The CYD bridge is still
isolated.

### Independent C3 checkpoint

The [C3 raw-format results](../tests/results/c3-vorbis-format-20261020/README.md)
independently reproduce the inherited restriction on SDK6.1/RISC-V, then qualify
the same two-line removal in the C3 implementation. The original C3 vendor first
decodes all 68 high-rate8192 packets. Candidate acceptance covers 340 paired
packets and 4631808 exact PCM bytes at the same four rates and ordinary control;
four malformed headers reject. The separate old-guard control restores every
baseline setup byte and reaches the named failure after its full prerequisites.
Both coordinator and decoder run on core0, with actual RV32 flags, ELF machine243
and the C3 bootloader offset0 checked separately from CYD. Eight native protocol
host tests pass. The optional limit and all other setup checks remain unchanged.

The [reusable C3 target](../tests/target/c3_vorbis_format_qemu/README.md) preserves
the exercised caller and compile/link directives; its explicit setup-hash input
is a source-reviewed CMake adaptation, not an additional qualified SDK campaign.
This checkpoint does not run the production C3 application or qualify its Ogg,
EOF/reset, allocation failures, resource margins or physical playback. The
previously deferred application/AAC hooks are not invoked.

## Full block-pair raw checkpoint, 2026-10-20

The [reproducible fixture generators](../tests/vorbis_block_matrix/README.md)
retain all 36 ordered short/long block pairs from 64 through 8192. Three banks
cover the realistic encoder stream, explicit short/long transitions and a
constructed nonzero floor1/residue1 supplement. The original dual-reference
host campaign remains NONPASS: native FFmpeg 8.1.1 accepts 78 cases and rejects 30
because of an additional floor1 endpoint bound. The [primary floor1 algorithm](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
allows extending or truncating the curve to the transform length. A separate
Xiph completion accepts all 108 cases, retaining the 78 native cross-checks and
the 30 explicit native limitations. No cases are omitted. All 36 minimal 48000 Hz
fixtures also have independently accepted 192000 Hz rate-only counterparts.

The [frozen block-matrix evidence](../tests/results/cyd-vorbis-block-matrix-20261020/README.md)
records the actual SDK 6.0.2/Xtensa campaign: 108 cases, 5472 paired raw packets,
360 transition groups and 32543616 byte-exact PCM bytes. Each case opens fresh
opaque original/checked public handles; every packet checks complete consumption,
public metadata, guarded output and exact PCM, with nonzero output for every
present transition. The original decoder runs first. Both handles use 192000 Hz;
the separately qualified rate rebind is explicit. The coordinator runs on core 0
and decoding on core 1. The actual two setup/output translation units, SDK/archive
identities, ELF machine 94, unrestricted setup macro context, unchanged generated
compiler inputs and terminal emulator exit 0 are bound to the result. Eight
[protocol host tests](../tests/vorbis_block_matrix/PROTOCOL.md) pass separately.

This is a raw-format checkpoint, not radio integration or full G6. The fixture
Ogg carriers serve host references only. Target Ogg/EOF/reset/OOM, broader
codebooks/floors/residues/channels, full callback ABI, SMP service, actual audio
task integration and physical resource gates remain open. C3 matrix execution
is separate; the earlier C3 raw8192 result does not qualify this larger matrix.

## Unsigned rate checkpoint, 2026-10-20

Vorbis I section 4.2.2 defines the identification rate as unsigned32. The
fixed vendor ABI stores that bit pattern in signed32 `long`; the old `rate<1`
guard therefore rejected the upper half of the valid field range. The narrow
[setup change](../idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c) casts the
rate to `uint32_t` for validity and the optional `LIMIT_TO_64kHz` comparison.
The ABI field type/layout, signed bitrate hints, framing and other checks remain.

The [frozen SDK/Xtensa results](../tests/results/cyd-vorbis-uint32-rate-20261020/README.md)
retain five separate completed campaigns. The baseline reproduces rejection of
0x80000000 and UINT32_MAX after decoding the other 14 rates. Acceptance decodes
all 16 rates, including all nine advertised rates, with 1088 paired packets and
4362240 exact PCM bytes against fresh original vendor handles at 192000 Hz.
Public metadata, complete consumption, output guards and close results are
checked throughout; zero still rejects. The optional-cap campaign decodes
11 rates and rejects all five rates at or above 64000, including both high-bit
values. Restoring each signed guard independently reaches its exact named
failure. The coordinator remains on core0 and decoding on core1.

The [canonical protocol tests](../tests/vorbis_rate/README.md) pass all 19
methods separately. These results cover one stereo S256/L2048 raw fixture,
not every possible rate or format combination. They do not extend the radio
output hardware's supported rates. The same signed-rate finding has now been
independently reproduced and fixed on C3/RV32 as described below.

The [additional format generators](../tests/vorbis_format_corpus/README.md)
now reproduce all 100 nonmanifest files for 17 books/floor0/residue0 cases;
eight construction tests pass. Their original host campaign accepted all 17
with Xiph while FFmpeg native accepted seven and explicitly refused ten lookup2
cases. Target capture and independent numerical comparison for this corpus are
still pending. Neither checkpoint closes full G6 or enables radio integration.

### Independent C3 unsigned-rate checkpoint

The [C3 result archive](../tests/results/c3-vorbis-uint32-rate-20261020/README.md)
records five independently executed SDK6.1/RV32 campaigns using the C3 archives,
ELF machine243,160MHz/unicore configuration and bootloader offset0. Baseline
decodes14 rates and rejects the two high-bit values; the C3 source then receives
only the same two unsigned casts and explanatory comment, preserving its ABI.
Acceptance decodes all16 rates with1088 paired packets and4362240 exact PCM
bytes. The separately compiled cap accepts11 and rejects5; restoring each signed
guard independently reaches its named failure. Both coordinator and worker
remain on core0, including every packet witness. All five processes complete
with exit0 and all45 owned commands have terminal success without interruption.

Nineteen canonical C3 protocol methods pass; the source-preparation gate also
retains four Windows/RV32 compiler-context methods (23 total). The705-file archive
is verified offline from another working directory, including all five native
protocols, frozen source versions and compile/config/tool identities. This
standalone project does not configure the full C3 application or invoke the
previously deferred AAC hooks. Production images, actual radio/hardware and
other formats/lifetime/conformance gates remain separate.

## Entry points and confirmed problems

| Change | Donor implementation | CYD entry and required behavior |
| --- | --- | --- |
| Checked setup, DSP allocation and failed-open cleanup | [setup.c](../idf/esp32c3-oled-native/main/vorbis_repair/setup.c) | [decoder_registration.c](../idf/esp32-cyd2usb-native/main/decoder_registration.c) registers Vorbis. Its operation table must select the checked open function. The ESP32 failed-open path reads/frees an already freed wrapper; DSP and floor constructors also use unchecked allocations. Publish a handle only after complete initialization and release each partial child exactly once. |
| Checked Ogg open and allocation-error propagation | [simple.c](../idf/esp32c3-oled-native/main/vorbis_repair/simple.c) | [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c) opens `ESP_AUDIO_SIMPLE_DEC_TYPE_OGG` and closes on terminal errors. Ogg open must check the first allocation; header realloc/parser NO_MEM must reach the caller as MEM_LACK with no PCM. Other container types retain their existing path. |
| PCM capacity before synthesis | [output.c](../idf/esp32c3-oled-native/main/vorbis_repair/output.c) | The actual CYD decoder retries after `ESP_AUDIO_ERR_BUFF_NOT_ENOUGH`. The ESP32 library currently synthesizes before checking capacity. Repeated rejected retries must not consume input, advance overlap history or emit PCM. |
| Pending-packet retention and genuine-byte EOF | [simple.c](../idf/esp32c3-oled-native/main/vorbis_repair/simple.c) | Preserve the pending Ogg packet on every undersized retry, clear extensions on reset and retain a genuine final input byte when adapting a separate empty EOF. Keep CYD generation, lease and ordered-drain ownership. |

The audit records six concrete binary control-flow findings, with archive and
member hashes, section-relative offsets and disassembly excerpts. Selected
members contain no DWARF. Private structure offsets are only partially
corroborated by target consumers and cleanup routines; they still need actual
Xtensa compile/link and execution evidence. Donor RV32 assertions, instructions,
allocation counts and performance measurements are not CYD evidence.

## Implementation order

1. Add an independent Xtensa ABI/build guard for the exact ESP32 archives and
   all fields consumed by the bridge. Verify actual callback tables and every
   wrapped/real target once in the final ELF. Reject a wrong target, archive or
   missing wrapper. Do not invoke the donor verifier's unrelated deferred AAC
   work or reuse its RISC-V instruction matching.
2. Port checked setup/open and Ogg ownership with the retained license. Keep
   Huffman allocation based on used entries and check actual table capacities.
   Preserve original synthesis/MDCT/window/floor/residue/PCM arithmetic. Restore
   the previous task-local error scope after nested processing; never use one
   process-global failure flag across the two cores or replace the health hook.
3. Add output-capacity preflight and repeated pending retries against a frozen
   original ESP32 ample-buffer PCM oracle. Add EOF/reset behavior as its own
   regression. Do not change audio task cores, priorities, stacks or PCM leases.
4. Connect the repair to the actual decoder task only after standalone target
   qualification. Exercise generation changes, Stop/Play, output resize failure,
   maintenance, network EOF/error and stale input. Repeat full Clang after the
   source set is final and build all three output backends.

## Deferred Ogg target extension

The additional public Ogg EOF/reset/pending-ownership campaign is
[explicitly deferred](CYD_VORBIS_OGG_DEFERRED_20261020.md) after an automatic
content review stopped its agent. The already launched attempt completed SDK
compilation but failed its observer-selection check before QEMU. No new Ogg
runtime case or semantic control is qualified. The existing isolated raw-PCM
bridge qualification remains unchanged; the draft is not connected to radio.
The tooling restriction is not a confirmed firmware vulnerability and is not
bypassed by rephrasing or replacement execution.

## Required qualification

The format requirements use the primary
[Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html) and
[Ogg RFC 3533](https://www.rfc-editor.org/rfc/rfc3533), consulted 2026-10-20.
Embedded-profile omissions require an explicit allowance in the specification;
an inherited vendor or donor limit alone does not establish conformance.

- **G1 — ABI/link:** whole repair translation units on SDK 6.0.2/Xtensa, all
  asserted fields, machine94, both cores, correct operation tables and exact
  negative build guards.
- **G2 — PCM oracle:** original and repaired ESP32 raw-packet output compared
  byte-for-byte. Independent container/granule expectations use a pinned
  reference decoder with an explicit fixed-point comparison policy.
- **G3 — retry/EOF:** tiny, needed-size-minus-one, repeated tiny, exact and ample
  PCM capacities; priming, short/long transitions, window bits across byte two,
  multiple final-page packets, final-byte split, empty/repeated EOF and reset.
- **G4 — allocation/lifetime:** discover the actual target allocation sequence,
  fail each alloc/realloc and persistent failures, check guards/owner ledger and
  NULL handle publication, then prove a valid reopen/decode. Fault injection
  establishes error handling, not measured physical heap margins.
- **G5 — SMP/service:** two real task/core scopes, nesting, out-of-scope and
  non-Ogg passthrough, followed by the actual CYD audio-service scenarios.
  Concurrent close/reset on a handle still in process is not introduced.
- **G6 — format coverage:** sparse/ordered/unordered books, map types0/1/2,
  floor0/1, residue0/1/2, coupling/submaps, advertised channels/rates/block sizes,
  legal truncation and malformed setup. Check Ogg lacing/continuations, CRC,
  version, page sequence, serial/BOS/EOS/chaining and granule trim against the
  primary specifications. Record inherited rate/block-size limitations before
  deciding how to remove them; they are not a conformance pass.
- **G7 — exact controls:** undo each repair independently and require its named
  semantic failure. An unexpected panic or timeout is not a successful control.
- **G8 — integration/resources:** all three backend builds and saved firmware,
  actual task stack/CPU and heap/largest-block measurements, HTTP/HTTPS and
  prolonged radio playback on CYD.

The read-only audit did not run these gates; the later isolated checkpoint above
partially exercises four of them. Existing CYD registration
rollback, independent PCM ownership and terminal cleanup are reused, with new
regressions where coverage is missing. AAC compact-owner adaptation remains a
separate stage-14 work item; the deferred AAC item stays explicitly deferred.

## Floor1 X-position checkpoint, 2026-10-24

The [floor1 regression](../tests/results/vorbis-floor1-positions-20261024/README.md)
adds the missing normative maximum of 65 total X positions and uniqueness
checks in both CYD and C3 setup parsers. Existing sorting/cleanup and synthesis
are preserved. Eight construction tests pass. Independent SDK/QEMU runs on
both architectures accept 8 valid setups, reject 6 invalid setups and compare
112 packets/225280 PCM bytes exactly with their original vendor decoders.
Two ESP32 controls remove each guard independently and demonstrate actual
OK/non-null acceptance of its malformed case after the complete valid prefix.

Xiph independently confirms all 14 header decisions. Full target numerical
comparison remains NONPASS: three legal short-endpoint cases differ from Xiph
by up to 65535 S16 units on both platforms; the other five have maximum 1.
Every original signed16 sample is included with the unchanged project bound 2,
without alignment or signal modifications. Both targets produce identical PCM.
The internal vendor cause is not established. Native FFmpeg additionally
refuses one legal large endpoint and accepts both over-limit configurations;
its original NONPASS is retained, including the old classifier's limitations.

The setup validation regression advances finite G6/G7 coverage only. The new
short-endpoint numerical failure joins the outstanding wide/floor0/sequence1
failures. Full G6, callback ABI, Ogg/lifetime/SMP, radio integration, resources
and physical acceptance remain open; deferred work is not resumed.

## Floor1 curve application, 2026-10-24

The [renderer successor](../tests/results/vorbis-floor1-render-20261024/README.md)
resolves the three short-endpoint numerical failures in the checkpoint above.
Both architectures now wrap `floor1_inverse2` with the same portable
[curve renderer](../idf/esp32-cyd2usb-native/main/vorbis_repair/floor1_render.h).
Vorbis I section 7.2.4 and the pinned public Tremor `floor1.c`, `misc.h` and
`floor_lookup.c` supply the algorithm and full-precision inverse-dB table.
The final constant segment uses the same gain lookup and multiplication as
the preceding line segments; a segment extending beyond the spectral block
retains its original denominator. The wrapper consumes existing asserted ABI
fields and changes no allocation, ownership, task core, stack or priority.

Two independent SDK/QEMU banks cover eight position configurations and eight
nonflat curves on each architecture, including multipliers 1 through 4,
ascending/descending curves, active/inactive interior points and endpoints
1 through 32768. Each bank rejects six malformed setups and emits 112 raw
packets/225280 PCM bytes per architecture. All signed16 samples compare with
explicit Xiph libvorbis at maximum error 1 under the unchanged project bound
2, with no gain, alignment, resampling or trimming. This is a finite project
qualification, not a numerical tolerance specified by the Vorbis standard.

The five ordinary position cases remain byte-exact to the frozen old target
images. Restoring only the old tail computation in a separate ESP32 image
reproduces all eight frozen vectors, including the three errors up to 65535.
That is a functional control; the vendor's internal implementation is not
asserted from it. The old NONPASS reports and failed checker-classification
attempt are preserved. Eight classifier tests distinguish actual codec
refusals from crashes, timeouts and output failures.

ASan/UBSan tests independently check 1472 curves/1501440 bins, 2349 wide
products, 32 absent-floor cases, input preservation and output canaries.
The runner's bounded timeout/interruption controls also confirm termination
of its own child and grandchild process groups. The existing complete raw
capacity gate also passes with 535 packets/2112000 PCM bytes and 1602 rejected
undersized retries; its separate preflight-bypass control reaches the expected
`rejected_dsp_unchanged` failure. All 22 configure-only CMake cases pass,
including the missing-renderer-header guard and exact wrapper options.
Fresh same-loader raw/format
reports explicitly describe shared-renderer handle parity; they cannot prove
unchanged vendor PCM. The full G6 and other outstanding/deferred gates above
remain open. No production firmware or physical-board acceptance is claimed.

## Public raw registered dispatch, 2026-10-24

The [registered caller](../tests/target/vorbis_floor1_positions_qemu/main/registered.c)
exercises `esp_vorbis_dec_register` and generic `esp_audio_dec_open`,
`esp_audio_dec_process`, `esp_audio_dec_get_info` and void `esp_audio_dec_close`
on both architectures. Public `get_ops` checks select the checked open/decode
callbacks and vendor reset/close callbacks; reset behavior is not exercised.
The API contract comes from the pinned Espressif codec 2.6.2 public headers,
which are retained with the [execution evidence](../tests/results/vorbis-registered-raw-20261024/README.md).

Each target completes14 registration/unregistration cycles, accepts8 setups,
rejects6 with actual FAIL/null, and captures112 packets/225280 PCM bytes.
Before every nonempty packet, three one-byte output retries require
BUFF_NOT_ENOUGH, zero consumed/decoded bytes, exact needed capacity and
untouched guarded output:312 retries per target. Every nonempty accepted
packet requires stereo48kHz/S16 public metadata; the zero-output primer may
report NOT_FOUND. Independent whole-PCM comparison with retained Xiph output
has maximum error1 under the unchanged project bound2, without signal
adjustment. Five ordinary cases remain byte-exact to the frozen old images.

Two separately built ESP32 controls fail at case0 before open/decode:
omitting the registration wrap reaches `registry_open_binding`; selecting
the real decode callback reaches `registry_decode_binding`. Both retain the
exact ordered prefix, public registry cleanup and terminal controlled stop.
Panics, timeouts and unrelated failures cannot qualify these controls.

Twelve protocol host tests and eight real CMake script-mode tests pass. The
latter reproduce the misplaced binding guard in a frozen control and verify
early component discovery without option cache variables. Both first SDK
configuration failures are preserved; neither reached QEMU. This advances
the selected public callback path within G1. Full G1/G6, reset, Ogg,
allocation/lifetime/SMP service, radio integration and physical resource
acceptance remain open. Production source and task affinity are unchanged.

## Public raw reset checkpoint, 2026-10-24

The optional [reset caller](../tests/target/vorbis_floor1_positions_qemu/main/reset_cycles.h)
reuses one opaque generic handle per valid case on its single owner task.
The pinned Espressif codec 2.6.2 public `esp_audio_dec.h` describes resetting
processing state/cached buffers and reusing the handle without reopening;
it warns against reset during processing. Xiph's public
[`vorbis_synthesis_restart`](https://xiph.org/vorbis/doc/libvorbis/vorbis_synthesis_restart.html)
documents restoration of freshly initialized synthesis state. These public
contracts motivate the empty-primer and baseline-equivalence assertions;
the vendor's internal reset call path is not examined.

Each of eight valid cases requires an initial reset before its baseline,
a full replay after reset, replays after 7- and 5-packet prefixes, three tiny
retries before the latter reset, and a replay after three consecutive resets.
There are 9 calls per handle / 72 total. Invalid setups never reach reset.
The finite matrix counts 112 baseline + 448 replay + 96 prefix packets = 656,
312 baseline + 24 reset retries, and 225280 + 901120 + 212992 = 1339392 PCM
bytes. Every complete replay and prefix equals the corresponding captured
baseline bytes, including every final PCM16 sample. Metadata, consumption,
output guards and exact needed capacities are checked. Independent complete
baseline/Xiph comparison has maximum error 1 under the unchanged project
bound 2, without signal transforms. All 14 fresh reference commands terminate
normally: eight decode and six reject malformed setups. The replay/prefix
byte equality binds their complete vectors to that numerical comparison.

The separate ESP32 `reset-skip` image omits only the case-0 round-1 restart
after the complete baseline, round-0 replay and 7-packet prefix. It retains
2304 actual unexpected primer bytes, then the exact `reset_primer_empty`
failure, owned-handle close, public registry cleanup and controlled stop.
An empty primer, different failure, panic or timeout cannot qualify it.

Fourteen reset-protocol host methods, 22 CMake phase methods, the existing
12 registry-protocol methods and 8 reference-classifier methods pass. Initial
SDK attempts remain preserved NONPASS before compiler execution: sandbox
WinError 623 prevented tool startup. The installed GCC works outside the
sandbox; normal approved execution completes both targets and the control.
The [saved evidence](../tests/results/vorbis-raw-reset-20261024/README.md)
retains those attempts and explicit reuse of reviewed pure protocol parsers;
the offline signed16 metrics are independently recomputed. Production source,
task cores, stacks and priorities are unchanged. The fixture uses CYD
coordinator 0/worker 1, C3 core 0, priority 3 and stack 16384. This is
a finite public raw G1/G3 subset. Full G1/G3/G6, the explicitly deferred Ogg
work, allocation/lifetime/SMP integration, radio and physical resources remain
open.

## Checked raw-open allocation checkpoint, 2026-10-24

The pinned Espressif codec 2.6.2 public `esp_vorbis_dec.h` specifies
`ESP_AUDIO_ERR_MEM_LACK` for allocation failure and `ESP_AUDIO_ERR_FAIL` for
initialization failure. Actual unchanged-source ESP32 and C3 images expose a
classification defect: allocation 4 fails while parsing books, cleanup returns
all observed allocations, but open reports `FAIL`. The first three allocation
failures correctly report `MEM_LACK` and each allows a complete recovery decode.

Both [setup implementations](../idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c)
now record actual positive-size calloc failures in a task-local open scope.
Every post-validation exit restores the previous scope after cleanup, including
nested opens and successful publication. Zero-size requests and arithmetic
rejections do not become allocation failures. This changes error classification
without adding allocator calls, ABI fields, decoder arithmetic or task bindings.
TLS storage and physical memory/performance effects are not measured.

The optional [public raw caller](../tests/target/vorbis_floor1_positions_qemu/main/open_oom.h)
observes 32/36/32/36/36/36/36/36 positive allocation positions in eight valid
setups. Both targets complete single-failure and persistent-failure injection
at every observed position: 560 failed opens and 560 successful reopen/decode/
close recoveries per target. Every recovery checks 14 packets / 28160 bytes,
for 7840 recovery packets / 15769600 PCM bytes. Guarded external allocation
ledgers end empty, and all six uninjected malformed setups retain `FAIL`.
Four nested-open pairs and two ordered two-task scenarios check restoration
and error isolation across CYD cores 0/1 and C3 core 0. Independent handles
are never processed concurrently with their own close/reset.

Two separate ESP32 controls restore only the old header classification or
remove only the task-local scope pointer. They reach precisely
`oom_memory_error` at case 0 and `oom_task_error_isolation` at case 14. The
latter requires both an allocation-failing companion and an uninjected malformed
companion: two `MEM_LACK` outcomes alone could hide cross-task contamination.
All ordered prerequisites, cleanup and normal termination are required.

Independent full captured baseline PCM comparison with 14 fresh Xiph libvorbis
runs passes at maximum signed16 error 1 under the existing bound 2. Recovery
PCM equality is a target memcmp assertion against that baseline; recovery
vectors are not separately captured or independently numerically compared.
The 18 OOM-protocol, 37 real CMake-phase, 12 registry-protocol and 8 reference
outcome host methods pass.

The [saved evidence](../tests/results/vorbis-raw-open-oom-20261024/README.md)
retains initial baselines, both corrected targets, exact controls and an
offline verifier with explicit reviewed pure-parser reuse and independent PCM
metrics. This advances finite checked raw-open coverage within G4/G5. Full
G1/G4/G5/G6, general decode/reset/close allocation failures and lifetime/SMP
integration, deferred Ogg, radio integration and physical acceptance remain open.

## Current-source complete31 format checkpoint, 2026-10-24

The [refreshed capture](../tests/results/vorbis-current-format31-20261024/CHECKPOINT.md)
replays the complete earlier31 corpus with current canonical setup/output/ABI
and `floor1_render.h`. All 31 public raw open/decode/close cases finish on
SDK6.0.2/Xtensa: 434 packets, 738560 captured PCM bytes, 964 protocol records,
coordinator core0 and worker core1/priority3/stack16384. All ten owned commands
terminate successfully. The selected ELF's generated/queried link recipe has
all three wraps, including `floor1_inverse2`; its symbol and actual source pins
are also checked. A Ninja recipe query is not independent linker-execution
evidence. Production firmware and task bindings are unchanged.

Full numerical measurement completes with NONPASS at the existing bound2.
Fifteen cases have maximum signed16 error1. Four wide D16 cases still have
65535; all twelve original/equivalent floor0 cases retain their earlier errors.
Xiph satisfies all14 relations; target satisfies12 and still fails the two
wide sparse/dense equalities. Every one of the31 current PCM vectors is
byte-identical to its retained old target vector. Thus adding the current
floor1 renderer does not resolve these failures for this corpus. No opaque
backend cause is inferred and no new production parser correction is guessed.

The adapter revalidates retained qualified Xiph outputs in three original
scopes. It executes no new reference decoder and preserves their original
dual-reference NONPASS. Every original signed16 sample and packet is measured
without signal transforms. Eight real CMake phase tests, eight link-recipe
selection tests and nine changed-binding tests pass. A first attempt with an
incorrect SDK-Python argument stopped during environment activation and is
retained separately; the same frozen source succeeds with the installed SDK
virtualenv. No target ran in the first attempt.

[Remaining floor0 requirements](CYD_VORBIS_FLOOR0_REMAINING.md) distinguish the
public mathematical discrepancy from unverified backend behavior and explain
why an inverse2-only change cannot establish general precision/range support.
This checkpoint extends current-source regression evidence. Full G6, wide/
sequence1/floor0 correctness, callbacks/lifetime/SMP, deferred work, radio,
resources and physical acceptance remain open.

## Exact lookup1 value counts, 2026-10-25

The [lookup1 regression](../tests/results/vorbis-quantvals-20261025/CHECKPOINT.md)
fixes a separate shared setup arithmetic defect. The old Tremor-derived integer
root helper multiplies unchecked powers; entries2/dimension32 can overflow
ILP32 although its correct root is1. Both canonical setup files now use a
converging exact integer search with a pre-multiply division check. Positive
16/24-bit fields require no floating approximation or dimension clipping.
Allocations, ABI fields and production task bindings are unchanged.

ASan/UBSan checks35975 independent arbitrary-precision roots in each of the
native-long and explicitly modelled int32 profiles. The frozen old helper
reproduces signed overflow at entries2/dimension64 on the native64-bit host.
Both whole-source SDK/QEMU tests pass all2179 boundary cases: SDK6.0.2/Xtensa
machine94/core1 and pinnedSDK6.1/RV32 machine243/core0. Native ABI assertions,
actual compile/dependency/symbol/map evidence and9 normally completed commands
per target are retained; no codec archive is linked and compiler warnings are0.

This advances the lookup1 helper's correctness, not complete raw setup/PCM or
G6 qualification. Inherited parser limits remain. The retained full31 PCM
NONPASS predates this arithmetic edit and is not requalified by the helper
test. Wide/sequence1/floor0 correctness, deferred scopes, final Clang/exports,
radio integration, resources and physical acceptance remain open.
