# Integrated fractional 48 kHz build and physical checks

See [the report](../../../docs/ESP32C3_FRACTIONAL_INTEGRATION_20261010.md).
Two current-branch images are built and audited. Only the diagnostic image
is installed. HE-AACv2 completes 600 seconds with zero observed DMA counter
increments, but fails post-Stop contiguous-memory recovery. FLAC's requested
600-second observation is interrupted after 77.34 seconds by a TCP connect
timeout. Original failures remain failures.

The quiet image is a build candidate, not hardware-qualified. The controller
restores the previous listened fractional image and the initial stopped
state, preserving Wi-Fi, playlist and settings. Those private values are
compared only in memory; no TLS private key is archived.

`review.py` and `events.py` replay frozen diagnostic, memory and transport
data. Wait statistics include scheduling and overlap across tasks. DMA
notification counts are not an analog gap measurement. The intermediate
`hev2-review.json` was captured before FLAC and restoration completed; the
final `review.json` is the complete campaign summary.

Offline verification:

```powershell
python tests/results/esp32c3-frac4-20261010/replay.py --output NEW_DIRECTORY
```

Local controller paths and public test certificates are retained for
provenance. Review them and use fresh output paths/certificates for another
physical run. Build logs, 154 source snapshots, 74 test helpers, image hashes
and linked-code checks are retained. The unrelated inactive CLZ change is
in the source snapshot but explicitly excluded from compilation.
