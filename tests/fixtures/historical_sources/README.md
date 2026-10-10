# Historical source bytes

These files preserve exact source bytes named by SHA-256 in older measurement
records. `index.json` records the Git revision (or pre-existing snapshot) and
line-ending representation from which each file was recovered. Every stored
file must match its name's SHA-256. No recorded measurement, expected PCM value,
or expected source hash was changed.

Some original measurement sources were not found in Git or the retained
snapshots. Those fingerprint checks intentionally still fail:

- `sdkconfig.defaults`: `f67ed3d9a12ab589bbfa3805f89ad7b0e910b2f8d3a79a80c90edf4a31004bea`
- `common.py`: `114bb5dfeaae880642d9c0f8ec61ea0aa02a4cbc3e4e281e16bca13e31d25caa`
- `run.py`: `166d82ccbebaeb26056ffec7559522817b4c7ec8a8a654a22fcf42740da0db0e`

They belong to the 1 October IRAM/Wi-Fi evidence, not a runtime regression
introduced by the ESP-IDF upgrade. A missing original must not be replaced
with a different source and a newly invented expected hash.
