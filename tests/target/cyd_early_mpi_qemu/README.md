# CYD early-MPI SDK observation

`tests/run-cyd-early-mpi-qemu.py` compiles frozen canonical production module
bytes with the actual production Kconfig and the pinned clean SDK6.0.2. It runs
an isolated QEMU image with two cores and unchanged SDK startup. The fixture
performs no cryptographic calculation, network access or board operation.

The canonical case observes the SDK mutex through public lock APIs, checks
repeated use without replacement and mutual exclusion across both cores.
Two exact source-copy controls omit only the acquire or release statement;
only their named failures followed by controlled restart count as detections.
The separate void-API gate fills the real internal heap, delegates to the
unchanged queue allocator and requires a real NULL result on the actual SDK
MPI mutex. It accepts only the exact constructor abort site and full expected
decoded stack from that ELF, rather than treating an arbitrary panic as success.

```text
python -B tests/run-cyd-early-mpi-host.py --output .build/cyd-early-mpi-host-02
python -B tests/run-cyd-early-mpi-qemu.py --output .build/cyd-early-mpi-qemu-01 --qemu <qemu-system-xtensa.exe> --powershell <pwsh.exe>
```

The host gate uses SDK/service seams and complete canonical `app_main` and
module translation units, with the frozen actual board header. It proves
ordering and configuration behavior, rather than real target mutex semantics.
The SDK gate proves the isolated runtime properties. Its
`production_integration: false` report field distinguishes this fixture from
the complete radio app; module source still comes from the canonical production
path. The fixture's pre-application lock history, resource margins and observed
lazy state are not physical-radio measurements or default-activation evidence.
