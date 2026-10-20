# Public raw block protocol validation

Run the eight synthetic host methods from the repository root with a non-SDK
Python interpreter:

```text
python -B tests/vorbis_block_matrix/test_block_protocol.py
```

`host_model.json` supplies expected packet offsets and mode flags for manufactured
logs. It contains no encoded bank bytes, reference-decoder result or target proof.
The synthetic test helper's success facts apply only to those manufactured logs.
Actual captures require the actual frozen bank manifest and its separately bound
encoded arrays and host-reference evidence.

`block_protocol.validate_log` directly checks native CYD/core1 or C3/core0 lines;
it never translates captures or starts a process. Supply both stdout and stderr,
the actual bank list, profile `cyd` or `c3`, and every required keyword fact:

- `manifest_sha256`: the actual frozen encoded-bank manifest hash, bound to the
  target's bank header and matching its BEGIN line.
- `minimal_rate_rebind_qualified`: actual independently verified, hash-bound
  proof for all36 minimal48000-to192000 rate-only cases.
- `returncode`, `timed_out`, `interrupted`: actual owned-command terminal facts.
  Unknown, interrupted, timeout or nonzero results cannot pass.

The strict ordered corpus contains identity68, transitions70 and minimal14
packets over all36 legal block pairs:108 cases,5472 paired packets and360 present
transition groups. It checks full consumption, expected overlap PCM sizes,
per-packet public metadata, exact PCM/canary attestations, nonzero PCM for each
present transition, handle closure and complete native protocol. Missing,
duplicate, reordered or extra data and panic/failure markers are rejected.

A successful function call returns observations only. Synthetic test success
does not qualify fixtures, SDK/QEMU execution, either ABI, physical audio, radio,
Ogg/EOF/reset/ownership, OOM or private codecs. Source/tool/input/proof binding and
actual target qualification remain the campaign owner's responsibility.
