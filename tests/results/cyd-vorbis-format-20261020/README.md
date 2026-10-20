# CYD public raw Vorbis 8192 format evidence

This bundle preserves the diagnostic history and completed public raw-format
acceptance/control evidence. Acceptance covers 340 packet pairs and 4631808
exact PCM bytes at four 8192-block rates plus an ordinary 2048 control. Ten
host tests pass. Read the original reports and separate manual
qualification as recorded; an earlier NONPASS is never rewritten into a pass.

- Baseline01 and diagnostic01 preserve the per-packet metadata-reset harness
  failures as NONPASS.
- Baseline02 preserves its original response-file rejection as NONPASS and its
  separate manual REGRESSION_REPRODUCED result from the same unchanged build.
- Acceptance and old-guard control require complete reports and the exact
  counted vendor/pair/metadata/canary protocol. The old guard must fail only at
  `legal_candidate_open_required` after the vendor/ordinary/high-rate checks.
- Frozen sources, variants, actual macro context/generated inputs, compile DB,
  SDK logs, host02 receipt/logs and independent host reference Ogg/PCM are retained.

`manifest.json` maps each original repository-relative input to stored bytes,
decoded size/SHA256 and stored size/SHA256. Gzip is lossless; Python and fixture
headers remain uncompressed. Generated target ELF/application/full-flash,
library, tool and ROM binaries are deliberately omitted with size/SHA256.
Other object/CMake intermediates are unselected. This is an evidence bundle,
not a flashable firmware release or complete SDK/build environment.

Run the read-only verifier with ordinary host Python; no SDK, compiler, emulator
or reference codec runs. It imports only the frozen acceptance runner/helper and
uses its protocol validator against archived logs and the fixture.

```text
python -B verify_archive.py .
```

Successful verification checks the exact stored set and every decoded hash,
source/report/log bindings, semantic results, reference PCM invariance and the
two-line setup change. Control setup must restore baseline bytes exactly.
Physical board, production radio, target Ogg/EOF/reset/OOM and other formats
remain outside this qualification. Public fixed-point target PCM is compared
with the vendor target synthesis; no byte-exact float-versus-fixed claim is made.
