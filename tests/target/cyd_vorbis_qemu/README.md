# Isolated CYD Vorbis raw PCM and retry gate

`tests/run-cyd-vorbis-qemu.py` freezes the whole canonical bridge, harness,
fixture, packet-accounting helpers, public codec sources/headers and selected
SDK inputs. It checks the pinned clean SDK commit and both ESP32 archive hashes,
builds actual SDK6.0.2/Xtensa translation units, and runs QEMU with two cores.
No device, network or radio application service is used.

The existing `vorbis-q10.ogg` supplies 535 raw audio packets. On core 1 an
ample-buffer handle opened through the vendor public API and the checked bridge
process the same packets.
Every emitted PCM span, result, consumed count and format is compared directly.
Three undersized retries before each nonempty packet output must preserve the
entire typed wrapper/DSP and every work/MDCT array byte. These are test-only
state reads and snapshots; the fixture never changes private decoder state.
Core 0 starts the decoder task; this is not two concurrent decoder handles.

Both handles use the linked `floor1_inverse2` renderer wrapper. The existing
`original_exact=1` wire marker records handle parity under that shared renderer;
it does not establish unchanged vendor floor arithmetic. Fresh reports state
`pcm_comparison_scope`, `unchanged_vendor_pcm_oracle=false` and
`independent_reference_compared=false`, and require the renderer wrapper symbol.
Independent PCM comparisons or frozen old-image comparisons remain separate.

Run on Windows with the pinned SDK and native Xtensa QEMU installed:

```text
python -B tests/run-cyd-vorbis-qemu.py --output .build/cyd-vorbis-raw-01 --qemu <qemu-system-xtensa.exe> --powershell <pwsh.exe>
python -B tests/run-cyd-vorbis-qemu.py --output .build/cyd-vorbis-raw-control-01 --control skip-preflight --qemu <qemu-system-xtensa.exe> --powershell <pwsh.exe>
```

SDK/tools/codec locations can be supplied with `--idf`, `--idf-tools` and
`--codec`. Use `--rom` when the QEMU executable is a separate build outside its
installed directory layout. Output must be fresh, strictly inside repository `.build`, outside
existing campaigns and disjoint from installed runtimes. Compilation and
execution failures retain nonpassing reports/logs. The control changes only a
frozen copy, bypassing PCM preflight; only the named `rejected_dsp_unchanged`
failure followed by controlled restart counts as detection. A panic, timeout
or build error never counts.

This gate covers one raw fixture and a specific capacity defect. Ogg ownership,
EOF/reset, OOM/lifetime, other modes/codebooks/rates, parallel task-local scopes,
all linker callbacks, actual audio-service integration, physical resources and
standards conformance remain separate. Build-local fixture binaries remain
test artifacts; these are not production firmware hand-offs.
