# Integer-rate compensation: host experiment, not production acceptance

See [the report](../../../docs/ESP32C3_INTEGER_RATE_COMPENSATION_20261009.md).
The compensated linear resampler passes 35 memory-safety/sample-count cases
but fails the high-frequency quality requirement. It is default-off and has
not been installed. PCM arithmetic error versus rational *linear* interpolation
is separate from interpolation loss versus the original continuous signal,
and from the AAC compact decoder's 3-LSB requirement.

The default implementation remains byte-identical across four staged/direct
and profiling host paths. Reports save raw PCM size/hash; these replaceable
12 MB-per-variant PCM captures are not included here. Logs and source snapshots
are included. Five driver-generator checks and 62 source-contract checks pass.
No firmware binary was built in this experiment; the board remains on the
restored production image.

`filter-study.json` is an analytical comparison, not measured FIR firmware.
The 32-tap/Q19/256-phase option has promising response but its CPU, lifecycle
and physical behavior are unqualified. History-byte counts exclude state.
The initial host-unit filename collision caused a compile failure before the
successful run; no compiler stderr was retained from that first attempt.

Offline verification and analytical replay:

```powershell
python tests/results/esp32c3-integer-rate-20261009/replay.py --output NEW_JSON
```

To rerun the actual C with WSL/GCC/ASan/UBSan, execute the frozen
`sources/tools/codec_benchmark/run_integer_rate_host.py` and
`sources/tools/codec_benchmark/run_output_dma_host.py --profile`, each with
`--output NEW_DIRECTORY`. Use new paths to preserve evidence.
