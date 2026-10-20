# CYD Vorbis/Ogg repair transfer

Stage CYD-C3-14 of the [transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md) remains
open. The [read-only Xtensa audit](../tests/results/cyd-vorbis-xtensa-audit-20261020/README.md)
examines the actual installed Espressif 2.6.2 ESP32 archives, rather than
assuming that the C3 binary layout carries over. It does not execute a decoder
or qualify a repair. The previously deferred AAC private-owner work is excluded.

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

## Required qualification

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

All eight gates are unrun by the read-only audit. Existing CYD registration
rollback, independent PCM ownership and terminal cleanup are reused, with new
regressions where coverage is missing. AAC compact-owner adaptation remains a
separate stage-14 work item; the deferred AAC item stays explicitly deferred.
