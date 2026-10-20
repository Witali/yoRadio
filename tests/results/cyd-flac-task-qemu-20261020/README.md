# CYD actual audio task QEMU checkpoint — 2026-10-20

Fresh promoted attempt 01 passed all **3 lifecycle cases** on the classic
ESP32 dual-core Xtensa model with installed ESP-IDF 6.0.2. The unchanged whole
`audio_service.c`, `native_state.c`, `native_health.c` and
`decoder_registration.c` translation units were compiled from fresh snapshots.
Real SDK tasks, queues, adaptive input leases, PCM ring, heap allocation and
custom FLAC codec ran in the emulator. Tests drove production public APIs;
they did not write private owner phases, generations or ACKs.

| Case | Public drive and checked result | PCM compared |
| --- | --- | ---: |
| T0 | Play 24-bit FLAC to ordered EOF; complete PCM precedes EOF, codec workspace released | 4096 bytes |
| T1 | Stop while a large FLAC frame and HTTP read are held; release old owners, reopen 16-bit FLAC | 4096 bytes |
| T2 | Begin maintenance with live decoder workspace, wait for all three owners to release, end with resume; reject stale token | 33316 bytes |

All 5 actual custom decoders were destroyed and all 5 real SDK HTTP clients
were cleaned up. The three original task profiles were checked at creation
and callbacks checked their running core and priority:

| Owner | Core | Priority | Stack bytes |
| --- | ---: | ---: | ---: |
| Stream | 0 | 3 | 6144 |
| Decoder | 1 | 5 | 16384 |
| Output | 1 | 6 | 4096 |

The HTTP `open`/headers/read transport and public output/LED backend are
explicit seams. HTTP client init/cleanup use the real SDK. Output compares
every PCM byte with independent FFmpeg oracles and accepts writes immediately.
`CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE` is explicitly disabled in this
test profile because synthetic transport does not enter the SDK's connected
header state; actual request-TX release has a separate HTTP component gate.

The fixture container retains all 130 independently FFmpeg-checked encoded
fixtures and PCM oracles. This task checkpoint executes the three cases
above using three selected fixtures; it does not repeat the separate 520-case
adapter gate. Heap integrity, assertions and stack canaries are enabled in
the test profile. Production memory margins, OOM injection, output
backpressure, physical audio/RF behavior and performance remain open.

## Evidence and byte preservation

- `raw/report.json` and `raw/execution-bundle.json` are the original exact bytes.
- `manifest.json` maps every original input/artifact path to a SHA256-addressed
  file under `objects/`; content duplicates share a stored object. Long SDK
  dependency paths are flattened. All original source paths and roles are
  retained in `source_mapping` and the raw source manifest.
- The bundle binds 740 frozen input paths, 18 artifact paths and 12 installed
  runtime hashes. Their union is 757 input/artifact paths. The source manifest
  binds 474 live originals and snapshots; actual compiler closure records
  14 translation units and 420 dependencies. Extra headers are metadata.
- Generated fixtures/oracles, SDK configuration/compile commands, ELF, test app,
  merged emulator flash and build tool response files are preserved through
  the input/artifact mapping. These are test images, not production firmware.
- `logs/` contains original runner, SDK build, compiler dependency, symbol and
  QEMU logs. `terminal-observation.json` records session 82639 terminal exit 0
  as observed by the running agent. It is separate from firmware output.
- `preflight/` preserves the earlier 15 CLI/path protection cases, including
  custom Python and PowerShell parents; preflight starts no build or emulator.
- `runtime-hashes.json` retains tool and ROM hashes. Installed executables and
  ROM files are not copied. All archive files use `.gitattributes` `-text`.

Git HEAD observed at source freeze was
`edccc3ac33391592a33c154cf0a594f393c4cf0f`. Source hashes bind the actual working
files, including integration bytes not yet represented by that HEAD.
Review status: awaiting parent review; no independent review record is attached.

Verify the archive offline with Python 3.12 or newer:

```powershell
python tests/results/cyd-flac-task-qemu-20261020/verify_archive.py
```

Reproduce a fresh installed-tool run using `tests/run-cyd-flac-task-qemu.py`
with a fresh `--output`, `--idf`, `--idf-tools`, `--idf-python`,
`--vendor-component`, `--qemu`, `--rom-directory`, `--ffmpeg` and
`--powershell` as needed. `--preflight-only` validates paths without creating
output. Physical devices are never used by this runner.
