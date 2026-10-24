# Floor1 X-position setup regression

This isolated public raw-API fixture compiles the actual CYD or C3 `setup.c`
and `output.c`; it never configures either production application or calls the
Ogg adapter. Generate its 14 cases with:

```text
python -B tests/vorbis_format_corpus/generate_floor1_positions.py --output .build/vorbis-floor1-positions-corpus-01
python -B tests/test-vorbis-floor1-positions.py
```

`tests/run-vorbis-floor1-positions-qemu.py --help` lists the explicit SDK,
tools, codec, PowerShell, QEMU, ROM and corpus inputs. Output must be fresh
beneath this checkout's `.build`. ESP32 requires SDK 6.0.2, Xtensa/machine94,
240 MHz, two CPUs, coordinator core 0 and worker core 1. ESP32-C3 requires the
pinned SDK 6.1 revision, RV32/machine243,160 MHz, one CPU, both tasks on core 0.
The bootloader offsets differ: ESP32 `0x1000`, C3 `0`. Both raw fixtures use
DIO40/4MiB and disable the emulated NIC.

Eight legal setups include the maximum 65 total X positions, unsorted unique
positions, rangebits0 with no explicit positions, and a large legal endpoint.
Six invalid setups contain repeated positions or 66/250 total positions. Only
valid setups reach synthesis. With `--renderer off` (the setup-only default),
every complete packet compares guarded PCM and metadata with a fresh
ample-buffer original vendor handle. Each invalid open
must return FAIL and a null handle. Heap integrity is checked after each case.

`--control count` or `--control unique` removes just that guard from a frozen
copy. Each control requires all 8 positive cases/112 packets first, the exact
preceding rejection sequence, then actual OK/non-null acceptance of malformed
case 12 or8 respectively. An allocation error, panic, timeout or another failure
does not qualify a control. Production source bytes are never changed by it.

The controller records actual child exits and selected input/tool hashes. It
does not establish complete dependency closure or QMP EOF/reader-join evidence.
Successful fixture builds are test artifacts, not production firmware handoffs.

[Saved execution and numerical limits](../../results/vorbis-floor1-positions-20261024/README.md)
include both architectures, the two ESP32 controls, the original dual-reference
NONPASS and an independent Xiph PCM comparison. Full numerical correctness is
still NONPASS for three short-endpoint cases. No hardware or radio integration
claim follows from this setup-validation regression.

## Independent renderer qualification

`--renderer on` selects `render.c`, links the `floor1_inverse2` wrapper, and
captures one checked handle's guarded PCM. It reports `RENDER_CAPTURED` with
`passed=false` until an independent numerical check. It does not compare two
handles sharing the same renderer as an arithmetic oracle.

Use the positions corpus above with `--corpus-kind positions`. A second bank
has individual packets for nonflat curves, all four multipliers, active and
inactive interior points, unsorted coordinates and short/long endpoints:

```text
python -B tests/vorbis_format_corpus/generate_floor1_slopes.py --output .build/vorbis-floor1-slopes-corpus-01
python -B tests/test-vorbis-floor1-slopes.py
python -B tests/test-vorbis-floor1-render.py --output .build/vorbis-floor1-render-host-01
python -B tests/test-vorbis-floor1-reference-outcomes.py
```

Select that bank with `--renderer on --corpus-kind slopes --corpus <directory>`
and retain independent ESP32/C3 captures. `--control old-tail` changes only the
frozen renderer's final multiplication; it must reproduce the original
position-bank PCM and its specific numerical failures. The raw control capture
alone does not qualify that semantic check.

`tests/check-vorbis-floor1-render.py` compares complete signed PCM16 samples
with explicit Xiph libvorbis at the fixed project bound 2, with no gain,
alignment, resampling or trim. For slopes it requires `--ffmpeg` with the pinned
executable. Its positions/reference/baseline checks deliberately bind to the
retained original campaign; this is a finite qualification tool. The
[renderer checkpoint](../../results/vorbis-floor1-render-20261024/README.md)
includes a portable offline verifier for the published evidence. Both banks
now have maximum error 1 on both architectures, while the original setup-only
NONPASS remains historical evidence. Full G6, radio and physical acceptance
remain separate.

## Registered public raw dispatch

`--dispatch registered --renderer on` selects [registered.c](main/registered.c).
It uses one generic handle per valid case through public registration,
`open`, `process`, `get_info` and void `close`. Every case checks public
operation-table pointers and removes the registration afterward. Reset is
checked only as a callback pointer and is never called. This path has no
second vendor handle as a numerical oracle.

The14-case protocol requires8 valid decodes,6 actual FAIL/null opens,
112 complete packets/225280 PCM bytes and312 one-byte retries. Rejected
retries leave all4096 output bytes and canaries unchanged, consume no input
and publish the exact needed size. Metadata is checked after every accepted
packet; only the zero-output primer may return NOT_FOUND. A complete capture
reports `registered_callbacks_qualified=true`; `RENDER_CAPTURED` remains
separate from independent numerical acceptance.

`--control register-open` and `--control register-decode` are early binding
controls. They require `registry_open_binding` or `registry_decode_binding`
respectively at case0, no open/PCM events, verified registry cleanup and a
controlled stop. A panic, timeout or generic failure is not an effective
control. Both controls, both architectures' captures and the independent
Xiph comparison passed for this finite corpus; see the
[saved evidence](../../results/vorbis-registered-raw-20261024/README.md).

```text
python -B tests/test-vorbis-registered-protocol.py -v
python -B tests/test-vorbis-registered-cmake.py --output .build/vorbis-registered-cmake-host-02 -v
```

The12 protocol methods and8 real script-mode phase tests pass. The CMake
test requires a fresh output directory; supply `--cmake` when the pinned
default executable is unavailable. First SDK configure failures are retained;
their misplaced discovery guard was fixed before the successful captures.
Full G1/G6, reset/Ogg, production radio and physical acceptance remain open.

## Optional sequential public raw reset cycles

`--dispatch registered --renderer on --reset-cycles` includes
[reset_cycles.h](main/reset_cycles.h). The default registered mode still does
not invoke reset. One generic opaque handle per valid setup remains on its
owner task: initial reset before the baseline; reset/full replay; prepare
reset/prefix 7/restart/full replay; prepare reset/prefix 5/three one-byte
retries/restart/full replay; and three consecutive resets/full replay. This
is 9 public reset calls per valid case, 72 total. Invalid setups have no reset
events. No production source or task affinity is changed.

The strict interleaved registry/reset protocol requires 112 baseline + 448
replay + 96 prefix = 656 accepted packets and 312 + 24 rejected tiny retries.
The corresponding PCM totals are 225280 + 901120 + 212992 = 1339392 bytes.
Every replay/prefix byte must equal its baseline packet slice; public metadata,
full consumption, capacities and canaries remain checked. Reports retain
hashes/counts while the existing baseline PCM files support the independent
Xiph comparison at the fixed bound 2. Both architectures complete this
matrix; full signed16 comparison has maximum error 1. Eight fresh Xiph
references decode and six malformed setups receive normal codec refusals.

`--control reset-skip` additionally requires reset cycles and skips only the
case-0 round-1 restart. The full baseline, round-0 replay and 7-packet prefix
must precede the actual nonempty full-primer record and exact
`reset_primer_empty` failure, owned-handle close, registry cleanup and controlled
stop. No unrelated failure or timeout qualifies the control. The separate
ESP32 image demonstrates the required 2304-byte unexpected primer and cleanup.

```text
python -B tests/test-vorbis-reset-protocol.py -v
```

The 14 reset-protocol, 22 CMake phase, existing 12 registry-protocol and 8
reference-classifier host methods pass. Initial SDK NONPASS attempts stopped
before compiler execution on sandbox WinError 623 and remain preserved. Normal
approved execution outside the sandbox completes the same frozen sources. The
[reset evidence](../../results/vorbis-raw-reset-20261024/README.md) keeps their
history. Espressif codec 2.6.2 documents handle reuse after reset and disallows
reset during processing; all fixture calls are sequential. Xiph's
[restart contract](https://xiph.org/vorbis/doc/libvorbis/vorbis_synthesis_restart.html)
provides the freshly initialized-state expectation. This finite public raw
subset leaves full G1/G3/G6, deferred Ogg, production radio, integration and
physical resource acceptance open.

## Optional checked raw-open allocation failures

`--dispatch registered --renderer on --open-oom` includes
[open_oom.h](main/open_oom.h); it is off by default and excludes reset cycles
and registration controls. The test observes only `AUD_Codec` allocations on
the calling task during the direct checked raw-open callback. Public close
runs outside that interval. Guarded, aligned, zeroed payloads and an external
ledger check cleanup without reading decoder-private fields.

Both SDK/QEMU targets discover 32/36/32/36/36/36/36/36 allocation positions
across eight valid setups. Each position gets a single failure and a persistent
failure from that position onward: 560 failed opens and 560 successful recovery
opens per target. Every recovery decodes all 14 packets / 28160 PCM bytes and
compares them with its captured baseline. There are 7840 recovery packets /
15769600 PCM bytes; these are target memcmp assertions, not separately captured
recovery vectors. All owned allocations are released and guards remain intact.
Six uninjected malformed setups still report `FAIL`. Four nested-open pairs
and two ordered two-task scenarios check error-scope restoration and isolation;
CYD uses cores 0/1, while both C3 workers use core 0.

The original source on both targets fails exactly at allocation 4: header
unpacking loses the actual memory failure and reports `FAIL` instead of the
publicly specified `MEM_LACK`. The production fix tracks actual positive-size
allocation failures in a task-local nested open scope. It adds no allocator
calls or ABI fields. TLS storage cost and physical resource margins are not
measured. A separate `--control oom-legacy` restores only the old classification;
`--control oom-global` removes only task locality. Both must reach their exact
named failures with ordered prerequisites and clean termination. The latter
requires the uninjected malformed companion to expose cross-task contamination.

The 18 OOM-protocol, 37 real CMake-phase, 12 registry-protocol and 8 reference
outcome tests pass. Independent full captured baseline PCM comparison against
14 fresh Xiph reference runs has maximum error 1 under the fixed project bound
2. The evidence retains an extra argument-parsing failure that ran no tests.

See [saved raw-open evidence](../../results/vorbis-raw-open-oom-20261024/README.md).
This is finite checked raw-open coverage within G4/G5. Full allocation/lifetime,
callback, Ogg, radio integration and physical acceptance remain open.
