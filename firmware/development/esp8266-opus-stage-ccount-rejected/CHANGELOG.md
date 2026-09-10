# Rejected raw CCOUNT profile, 2026-09-10

Source075c9b3. JSON formatting is fixed, but stage times are INVALID:
the RTOS tick resets CCOUNT to0. Raw subtraction reports huge wrap values.
None of these stage percentages may be used to select an optimization.

All ten attempted runs are retained, including decoder allocation failures.
The first runs also show declining free RAM; that separate transient/system
memory issue needs investigation. It is not explained away as a clock error
or proof of a codec leak. Decoder-only task-time uses the existing SDK
runtime-statistics mechanism, not these invalid CCOUNT differences.

Replaced with coherent SDK microsecond snapshots and an enclosing-window
sanity check. This image is archival evidence, not recommended for flashing.
