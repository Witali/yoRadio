# Deferred custom Vorbis standard-support work

On 2026-10-28 the user explicitly deferred the custom Vorbis/full-range
arithmetic direction and requested that all work be saved and pushed before
continuing with reuse of the Espressif Vorbis decoder. Do not resume this
direction automatically from older plan entries or numerical TODO documents.

The saved branch is `codex/esp32-cyd-c3-review` in
`.worktree/esp32-cyd-c3-review`. The active CYD firmware already registers
Espressif Vorbis and its Ogg simple decoder; the next work is to inspect and
reuse that path and the relevant C3 improvements for the correct Xtensa ABI.
No task core, priority, stack or audio/display backend is changed by deferral.

## Previously completed work retained

- `92257e45b`: persistent custom raw decoder; the ordinary original31/434-packet
  corpus passed host and ESP32/C3 QEMU. It remains unselected in production.
- `113a6dafb`: independent MPFR host reference, with 8202 numerical requests
  and all 447 retained packet-frame identities.
- `3b59f6b4a`: checked basic arithmetic; 701 cases on both host limb models,
  allocation-failure recovery and both MCU source-only compiler profiles.
- The subsequently completed isolated arithmetic SDK/QEMU runs are saved in
  `tests/results/vorbis-bigfloat-native-20261028/`. They test the basic engine,
  not the newly drafted interval or log-gain implementations.

## Unqualified source snapshot

The following new work is preserved as WIP, with no compiler, sanitizer or
numerical qualification claimed:

- `idf/components/native_vorbis_interval/`: interval arithmetic, rational-series
  pi/ln2 and Taylor sine/cosine with remainder bounds and quadrant reduction.
- `idf/components/native_vorbis_certified_gain/`: exact affine input imports,
  stable half-angle denominator and one-index log-gain enclosure, persistent
  workspace/result ownership and arbitrary-integer floor pair exports.
- `tests/test-vorbis-certified-gain.py`: corpus/model preparation, exact
  primitive expectations and encoders. The launcher, MPFR integration, captures,
  comparisons, refinement and final reports remain unfinished. Direct execution
  refuses instead of falsely reporting a passing qualification.
- `tests/native/vorbis_certified_gain_host.c`: draft gain/ownership/OOM/export
  fixture and conditional MPFR probes. Primitive execution, lifecycle guards
  and complete protocol integration remain unfinished.

The mathematical formulas received read-only review. That does not establish
that the C implementation is correct, buildable, fast enough or usable on an
MCU. The `source-snapshot.json` in
`tests/results/vorbis-extended-deferred-20261028/` records the actual saved bytes
and this explicit qualification boundary. No custom-gain test process was
launched; no source result should be inferred from completed basic-engine tests.

## Remaining custom requirements, preserved for a future explicit resume

The [previous numerical requirements](CYD_VORBIS_CERTIFIED_GAIN_REMAINING.md)
remain historical requirements for this deferred implementation: qualify all
encoded inputs, certified Bark mapping, exp2 conversion, wide exponents through
IMDCT/window/history and final PCM, then transport/audio-task/resource integration.
The original PCM bound and reference corpus must not be weakened on resumption.
The incomplete candidate is not selected by either production project's CMake.
Previously deferred private/controller scopes remain deferred separately.

The current priority is reuse of Espressif through supported interfaces. Any
remaining limitations of that decoder must be documented and tested honestly;
reusing it does not imply completion of the deferred custom numerical work.
