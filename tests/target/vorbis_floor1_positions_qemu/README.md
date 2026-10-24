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
