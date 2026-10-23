# Owned book publication unit: source-only standalone proposal

This unit calls the **actual production** `repair_vorbis_book_unpack` through an
include of its raw unchanged `setup.c`. It does not replace the parser with a
model. It tests the16 original vector books (book1 in books8 + new8), including
all59 active codewords and both consumed single-entry bit values:61 probes.
Scalar classification book0, full decoder opening, synthesis and PCM are outside
this unit's claim. The original25-case numeric NONPASS and bound2 are unchanged.

Nothing here has been compiled, linked, run on QEMU or executed as a unit/test.
`materialize.py` only copies bound source/header/fixture bytes and creates C
descriptors. AST and source-identity checks are source preparation, not evidence
of passing C code or numeric behavior. Root owns review and any later execution.
The current source-only receipt is `source-checks02.json`. The original AST
receipt/source in `history01` retains a Python non-raw regex literal warning;
that literal was corrected without changing the protocol's regex semantics.

## Concrete project

`project/` is an isolated SDK6.0.2 classic ESP32 project, `COMPONENTS main`,
ILP32,240MHz,dual-core configuration with the main task on core0. No production
sdkconfig or application is used or changed. `book_unit.c` includes:

- The raw production parser SHA256
  `6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c`
  and adjacent actual ABI header SHA256
  `e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60`.
- Four exact public codec header copies for declarations, with their licenses.
  There is no codec component dependency, imported archive or vendor decoder.
- Explicit single-owner bounded bit-reader and tracked zeroed allocator/free
  seams. They operate only on the original valid inputs. Allocation guards and
  zero live allocations after the actual clear check normal ownership; there
  is no injected failure/OOM/malformed/EOF experiment.

The reader begins at the original bitfield-recorded book1 sync and ends at its
original next time-field boundary. It returns32-bit patterns with the public
ILP32 signed reader type, does not read past its span and reports exact consumed
bits. The real parser's returned dim/entry/used/length/type/node/leaf/quantization
fields, allocation sizes and q_val bytes are checked. The wide table must be
exactly `80 01 81 02 82 83`, with the four original active rows in both sparse
and dense cases. All other returned table bytes are emitted and bounded; every
active path is traversed and its actual leaf value checked independently.

Expected vectors, original codeword IDs and bit spans come from the frozen
generator matrices/bitfields and raw setup files. `materialize.py` has normal
stdlib imports, never imports or monkeypatches a generator, and never calls the
parser to manufacture expected values. It derives expected packed leaves by
inverting the already recorded finite integer vectors. Copies and source
origins/hashes are listed in `source-pins.json`; `fixture-contract.json` pins
the complete16-case model and contains no ignored external runtime dependency.

## Independent consumer boundary

The documented public Tremor consumer seam reads our **returned** dec_table and
q_val. At explicit point0 it must produce the source-declared exact vectors for
each active word, both sequence modes and both single-entry wire bits. It is a
bounded adaptation of public Tremor semantics, not a byte-identical upstream
decoder and not a substitute production parser. See `PROVENANCE.md` for the
exact public revision, supported test representations and licensing boundary.

For sparsewide/dense pairs8↔9 and10↔11, actual copied rows, actual table bytes
and all four decoded vectors must match after independent expected-value checks.
The logical original entry counts remain6 versus4; no test silently requires
these distinct fields to become identical. No vendor handle, private offset,
binary, disassembly or opaque backend state is accessed.

These books have nonzero minimum−1 and delta1. The expected normalized fields are
q_min−2^30/point−30, q_delta2^28/point−28. Point0 uses finite shifts30/28 and
products that fit signed32; the seam checks those assumptions explicitly.
This is a decision for a focused public vector unit. It does not assert the
vendor uses point0, diagnose its wide arithmetic or address floor0's separate
zero-minimum/curve questions.

## Linking and terminal closure still require real execution

The exact whole setup TU also contains unrelated open/register wrappers.
`-ffunction-sections`, `-fdata-sections` and linker `--gc-sections` are explicit.
The design relies on unreachable wrappers/data being discarded. No fake vendor
open/decode/reset/close/register implementation is supplied to conceal unresolved
references. A real link failure is a failure to investigate, not grounds for
adding a vendor decoder or declaring this unit passed.

Before execution root must bind SDK6.0.2/target/generated config/compiler/source
dependencies, retain the actual compile/link commands and prove with ELF/map/nm
that the real setup and ABI copies were consumed while codec archives and all
vendor decoder/register/wrapper paths are absent from the linked image. CMake
source inspection does not prove that closure; no build occurred here.

The unit emits97 strict native protocol events: BEGIN,16 FIELDS,61 VECTOR,
16 CASE,2 PAIR and COMPLETE. All record actual core0. Failure emits FAILURE and
parks; it never resets, retries or emits COMPLETE. Successful `app_main` flushes
COMPLETE and returns into SDK idle. There is deliberately no reset or assumed
finite emulator exit. Root's future controller must record a reviewed owned QEMU
shutdown after COMPLETE, or add a separately reviewed finite-exit seam, and
preserve its actual terminal facts. A timeout, interruption, nonzero exit,
partial log or COMPLETE alone cannot qualify this unit.

The source-only Python interface is:

```python
contract = protocol.load_contract(path, expected_sha256=reviewed_raw_contract_sha256)
observed = protocol.validate_log(raw_stdout_and_stderr, contract,
    returncode=actual_returncode, timed_out=actual_timed_out,
    interrupted=actual_interrupted)
```

The parser requires all16 named cases/61 probes/97 events in exact order, exact
fields/leaf/vector/consumption values, complete wide equality and actual exit0
without timeout/interruption. It rejects target panic/reset/failure text. Even
a future passing report sets vendor_backend/PCM/fullG6/physical qualification
false. No synthetic protocol tests were run in this preparation.

Root should copy the frozen project into a new fresh campaign before build,
keeping this proposal and all original captures immutable. Actual unit results
would isolate our publication plus this public consumer, and would not close
the remaining wide PCM, floor0, fullG6 or production gates.
