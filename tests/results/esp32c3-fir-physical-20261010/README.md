# FIR physical rejection, archived 2026-10-10

The original 2026-10-09 controller completed its restoration before the
computer was shut down. This archive retains all four phases, failures,
short-file successes and passive USB observations. It does not contain a
laboratory private key or saved board settings.

The heavy FLAC control and FIR runs requested 90 seconds each. The FIR AAC
run requested 600 seconds but its observation was interrupted after about
49 seconds; it is not a completed ten-minute result. FIR produced watchdog
events, substantially increased output-task work and failed physical
acceptance. CPU utilization alone is not the rejection criterion.

`review.py` uses frozen helpers and reproduces the original failed gates.
It adds explicit incomplete-observation flags. Driver DMA notifications are
not a measurement of audible gaps. Short EOF tests pass all 60 independent
sample-count checks, including both HTTP and HTTPS.

The restored image recorded here is the integer-clock production firmware
installed at that time. It is a historical record; the board subsequently
received the fractional-clock listening image on 2026-10-10.

See [the report](../../../docs/ESP32C3_FIR_PHYSICAL_20261010.md) and
[host/build evidence](../esp32c3-fir-build-20261009/README.md).

Replay without a board or network:

```powershell
python tests/results/esp32c3-fir-physical-20261010/replay.py --output NEW_DIRECTORY
```

The controller is retained for provenance, not immediate reuse. Its local
paths and historical restore image must be reviewed before another run.
