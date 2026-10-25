# Owned Vorbis floor packets: 2026-10-25

Implementation commit `b652d5c047ed55ea189fac093b55091722d82ec6` adds
[five caller-owned APIs](../../../idf/components/native_vorbis_numeric/include/native_vorbis_floor_packet.h)
for floor0/floor1 packet decoding, floor1 reconstruction/table indices and a
floor0 gain handoff. [Design and primary references](../../../docs/VORBIS_FLOOR_PACKET_DESIGN.md)
describe EOP, empty books, order0, exact LSP carry and late clamping.

The final strict GCC host run passes ASan/UBSan with 7,345 rows and 46 API
controls. There are 292 original cases and 7,053 explicit payload bit cuts:
239 fatal prefix EOPs and 6,814 nominal floor EOPs. Independent equations compare
1,297 affine LSP values, 949 raw floor1 values and 83,962 curve indices exactly.
The raw helper tests full uint32 inputs separately from encodable packet values.
General floor0 gain is an internal consistency check; only ABSENT and order0
D=1 unity cases receive the additional exact identity checks.

Host02 and Host03 produce identical binary observations, SHA-256
`12a8a34288efa01181ed09b3d0ec08d37e8e5ed87059259a31eed80598586e4c`.
Host03 separates the EOP counters. Host01 stopped on a strict GCC warning in
the test adapter; its diagnostic and pre-fix source are retained. The initial
protocol test stopped on a test-generator keyword collision; the corrected
suite passes all 12 methods. All five previous protocol suites also pass.

Cross-target Clang-Tidy analyzes all five component C files for ESP32 and C3.
The new floor-packet/setup/codebook/quantization units have no warnings.
The existing floor0 bounded-int widening warning remains once per target:
its multiplication is bounded by the phase-array index before conversion.

Native SDK/QEMU captures pass 200 original cases, 46 controls and 2,388 events
per architecture, with nine normally completed commands and zero build warnings.
ESP32 SDK6.0.2 uses worker core1; C3 SDK6.1.0 uses core0. The coordinator stays
on core0, priority3/stack16384. Separate exact replay accepts all 400 native
cases: 2,244 affine values, 1,898 raw Y values and 167,924 curve indices.
The largest new floor API compiler frame is 1,184 bytes on each target;
these estimates exclude callees/libm and do not measure task high-water usage.

`captures.zip` and `manifest.json` retain original inputs, output values,
source snapshots, command receipts, diagnostics and isolated QEMU build files.
They do not contain complete SDK installations. Replay all saved values without
compiling or starting QEMU:

```powershell
python -B -X utf8 tests/results/vorbis-floor-packet-20261025/verify.py
```

The [test instructions](../../target/vorbis_floor_packet_qemu/README.md) describe
fresh host/native runs. These are isolated test images, not radio firmware.
Residue, inverse coupling, spectrum multiplication, IMDCT/overlap, production
registration, full31 PCM/G6/G8 and physical acceptance remain open. Production
task affinities, display/audio configuration and deferred scopes are unchanged.
