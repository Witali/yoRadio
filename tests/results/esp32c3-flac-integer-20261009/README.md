# Integer-clock FLAC queue comparison

See [the report](../../../docs/ESP32C3_FLAC_INTEGER_20261009.md).
The same-source firmware pair includes the input-retention correction,
full compact AAC/SBR/PS, QIO 80 MHz and the normal integer PDM divider.
Only `CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS` differs between the two
configurations: `0` versus `4`. Heap-owner hooks and the TCP probe are off.
CPU, pipeline, staged-DMA and network-memory profiling remain on, together
with the temporary laboratory CA. These are testing images.

`physical.py` installs applications through native OTA, verifies identity,
settings persistence, flash readback and PDM registers, and restores the
prior quiet image in `finally`. `trial.py` captures continuously through
180-second heavy FLAC playback and settled Stop recovery. The expanded
variant also runs full-rate HE-AACv2 for 180 seconds after FLAC. The order
is control / expanded / control. Host polls use a 100 ms interval plus the
request duration. The server sends the finite FLAC file without pacing;
continuous ADTS uses pacing ratio 1.0.

`review.py` retains the original runner verdicts, rechecks runtime faults
after capture closes, and independently measures complete CPU/decoder/flow
windows and DMA deltas. Zero DMA events is a separate criterion. The
counters do not establish analog continuity, and incomplete telemetry must
not be promoted to success. CPU has no pass/fail ceiling.

Replay without a board or network:

```powershell
python tests/results/esp32c3-flac-integer-20261009/replay.py --output NEW_DIRECTORY
```

The replay verifies exact archive bytes, firmware/config/source identities,
restoration and reproduces the independent analysis, including failed gates.
Local build/controller recipes retain the exact laboratory paths for
provenance. For a new run prepare new output paths and valid trust; never
overwrite this evidence. Private TLS keys and user settings are excluded.
