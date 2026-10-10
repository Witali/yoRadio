# Early MPI-lock initialization experiment, 2026-10-10

`CONFIG_YORADIO_TLS_EARLY_MPI_LOCK` creates the SDK's existing MPI mutex
before normal application allocations. It stays disabled by default pending
quiet-production qualification. The frozen overlay changes only `app_main.c`
and `Kconfig.projbuild` for this experiment; unrelated inactive CLZ work was
already present and explicitly excluded from both builds.

Two saved diagnostic images are compared with the previous `web-tcp-v2` and
`frac4` controls. The active config delta is only the new flag. AAC/FLAC code
and constant sections, full public-plus-laboratory trust and allocation
routes are checked. Linked startup disassembly confirms acquire/release
before other services, with unchanged IRAM/DRAM/RTC sections.

`physical.py` attempts fresh-boot 75-second HE-AACv2 TLS record growth on each
image, then the 22-case HTTPS playback/EOF matrix, nine HTTPS station changes
and two AAC format transitions on the image without owner/TCP probes.
Original case failures and skipped later phases must remain visible. The
controller restores the user's listened fractional-clock image in `finally`;
private settings are compared only in memory. No TLS private key is included.

Replay recorded evidence from the repository worktree into a new directory:

```powershell
python tests/results/esp32c3-mpi-startup-20261010/replay.py --output .build/mpi-startup-replay
```

This checks frozen hashes, image/config/source identities, startup audit,
owner snapshots, original memory/playback verdicts and restoration without
contacting hardware. Replay PASS does not qualify the final production image.
`probe-comparison.json` references the preserved previous failed control.
The exporter used by the build is frozen as `export-used.py`.
