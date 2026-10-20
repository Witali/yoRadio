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
