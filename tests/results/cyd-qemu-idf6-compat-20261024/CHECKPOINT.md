# CYD: classic ESP32 emulator compatibility checkpoint, 2026-10-24

The completed scope is a finite set of emulator regressions. Full production
startup remains **NONPASS at unsupported RF MMIO**, not a firmware acceptance.
No physical board, serial port, OTA, host NIC or real audio output was used.

The separate QEMU branch is `codex/cyd-idf6-compat` in
`C:/Work/QEMU-ESP32/.worktree/cyd-idf6-compat`, based on
`2a593f8d00c9be312ddc6e600dbb778f0e6459eb`. Five focused local commits preserve
the completed changes:

- `9eb4a13c27fe`: native Windows trace generation paths.
- `afbf1d6a574f`: normal DPORT Wi-Fi clock register storage and reset.
- `87f45870bbcd`: continuous GD/Winbond Status Register 2 replies.
- `d86ee340b60c`: selection of classic ESP32 peripheral regressions.
- `9e320d7ef058`: SPI read modes, dummy phases, clock storage, optional input
  compensation, regression runners and model documentation.

The QEMU checkout was clean after these commits. The final executable was built
from the recorded preceding HEAD plus the matching working source patch; its
executed source bodies and build identity are saved. The original installed
QEMU and original checkout were preserved. No QEMU branch push is claimed.

## Actual checks

| Check | Actual completed result |
| --- | --- |
| Final default SPI/DPORT matrix | 274/274 comparisons |
| Input path 0 ns | 391/391 comparisons |
| Input path 25 ns | 391/391 comparisons |
| SPI2/SPI3 and legacy CYD at 0 ns | Both existing groups pass |
| SPI2/SPI3 and legacy CYD at 25 ns | Both existing groups pass |

The tests read distinct backing bytes at three addresses with lengths 2, 3,
16 and 64; cover six flash read modes, QIO/DIO partial address packing, SR2
clear/restore, JEDEC, real clock register reset/write/read, prescaling, EQU
bypass, missing protocol dummy and full-duplex/DOUTDIN exclusions. The two
peripheral groups check LCD pixels, SD sector write/read, CS isolation and
incorrect GPIO routes. Their owned QEMU children exited 0 without fallback.

Negative controls were actually executed and retained: the original rebuilt
emulator failed 49/187; newly exposed SR2 continuity failed 7/200; subbyte
rounding failed 73/274; the property-only model without compensation failed
24/386 and again 24/391 after adding an explicit DOUTDIN check. Final controls
and tests use unchanged comparison expectations. Initial build failures and
their Windows path fixes are retained, including the incorrect first MSYS cwd.

The paused MMIO fixtures deliberately terminate their own QEMU child after all
commands. Their recorded QEMU exit=1 is expected owner teardown; actual stdout
EOF and reader join are required. It is not a natural guest boot exit=0. Their
60-second phase deadline and 32 MiB polled log limits are monitored bounds,
followed by bounded cleanup; they are not OS-enforced hard quotas.

## Unchanged production image and remaining limit

The final emulator SHA256 is
`4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d`.
The unchanged production inventory is
`f9cf237bbbefe7967abbb558b06beb1ed4617035769669bb770223ad01bf5b12`;
its PDM application SHA256 is
`66e99cfb4773bad31cd646ec22e0cdda5d1231bf9b3ea74a6940401aea98ecf3`.
This is the original source `3a563324abdca56144a40d5759def0ccfe708b3c`
SDK6.0.2 QIO80/CPU240/two-core image, used to isolate emulator changes.
It is not a new production build or qualification of every later firmware change.
Firmware, partitions, SPIFFS bytes, task priorities/stacks/core bindings and
hardware setup were not changed. No filesystem formatting or assertion removal
was used.

Observer06 explicitly selects
`-global driver=ssi.esp32.spi,property=input-delay-ns,value=25`.
Default input delay remains 0. The SDK's fixed 80 MHz flash source and nominal
25 ns matrix path yield 2/1/0 compensation clocks at SPI 80/40/20 MHz. This
functional model collapses an input delay and its compensating clocks; it does
not qualify fractional-bit waveforms, analog latency or dynamic APB clocks.
The global property applies to classic SPI devices; receive-only gating and
the peripheral tests protect MOSI/full-duplex behavior.

The final UART detects `gd`, enters `app_main`, restores audio settings, enters
the CYD ST7789 driver and initializes Wi-Fi. The earlier SPIFFS mount error and
PHY clock-mask assertion are absent. Passing the mount call is a source/control
flow inference from the absence of its unconditional error log before later
startup; complete filesystem integrity is not established.

Full RF calibration then faults with `LoadStorePIFAddrError`,
`EXCVADDR: 0x60033c00`. Pipeline, radio and Web readiness markers remain false.
No RF register success stub was introduced. Audio playback, networking, memory
benefit, soak tests, OTA and physical acceptance remain open. The conservative
frozen display-clear predicate remains false; it has not been rewritten using
later source inference.

Observer06 completed 8.25 host seconds of guest observation, with QEMU exit0,
exact guest-reset SHUTDOWN, actual QMP EOF and joined reader. All selected
inputs and the scratch snapshot medium were unchanged. Its 20,570,088-byte
trace remained below the accepted 32 MiB limit. Its report SHA256 is
`d1e3de5c399d1d2a762a43ec6b45598da2e7af766ff3aa44890f43c780fa46ca`.
Earlier observations retain their original failures; completion of a capture
does not turn its startup result into PASS.

## Evidence and use

`selected-qemu-source/` contains the executed model and test entry points.
`evidence/` retains source preparation, reviews, command receipts, control
failures, successful finite tests and boot observations. Original production
configuration and selected source evidence are included separately. Primary
SDK files for the timing calculation are preserved with hashes.

Run `python -B verify.py` here, or `python -B verify.py <archive-path>` from
another directory. This verifies exact archive membership/bytes and saved
report consistency. It does not re-execute the compiler, decoder or QEMU.
Tool executables, replaceable synthetic/snapshot media and large production
bodies are explicitly omitted with path, size and SHA256 in the manifest.
No complete build/runtime dependency closure is claimed. The source-only
preparation notes are historical; actual root execution is recorded separately.

Existing codec deferrals and earlier numerical NONPASS results remain open.
C3 display/GPIO/USB/reset behavior was not transferred. This checkpoint does
not replace the Vorbis reference comparisons or qualify the full port.
