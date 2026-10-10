# Integrated-clock heap/TCP attribution, 2026-10-10

This archive preserves a fresh-boot first-use HE-AACv2 TLS test (75 s) and
an attempted heavy-FLAC HTTPS test (600 s) on the existing `web-tcp-v2`
diagnostic image. Original verdicts, interrupted intervals, DMA counters,
allocation-owner snapshots and TCP integrity failures are retained unchanged.
A replay PASS validates the evidence; it does not accept the firmware.

The candidate is already saved under
`firmware/development/esp32c3-idf-6.1-r9a97-web-tcp-v2/`. Its original build
sources and audit remain in `tests/results/esp32c3-web-tcp-v2-20261009/`.
`config-diff.json` records the three diagnostic settings added relative to
the integrated `frac4` image. Instrumentation changes timing and heap layout;
this is not a matched performance comparison.

`physical.py` restores the user's listened fractional-clock image in its
`finally` block. Private Wi-Fi/settings/playlist contents stay in memory;
only equality checks are saved. TLS private keys are excluded. Test helper
sources are copied byte-for-byte. The pinned SDK source excerpts and ELF
inspection support an explicitly unproven lazy-MPI-lock hypothesis.

From the repository worktree, replay into a new directory:

```powershell
python tests/results/esp32c3-frac4-attribution-20261010/replay.py --output .build/frac4-attribution-replay
```

This command checks hashes, image/config/source identities, complete owner
snapshots, CRC/sequence/watermark TCP windows and restoration. It does not
contact the board or change a firmware verdict.
