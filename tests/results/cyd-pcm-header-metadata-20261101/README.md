# PCM metadata regression after ordered header gain

The existing CYD host suites pass against the gain-metadata integration. These
checks preserve the raw-vendor/legacy fallback and custom FLAC behavior; they
do not enable the new Ogg timeline or qualify physical output and target timing.
The complete gain path has a separate actual-task QEMU qualification.

`lifecycle-report.json` is the unchanged original report from
`.build/cyd-header-metadata-lifecycle-20261101-02`: all six vendor/Helix/minimp3
and adaptive-input profiles pass their existing assertions under ASan/UBSan.
The first attempt stopped during test compilation because the extracted PDM
cleanup needed the new gain-cache declaration. Both local attempts are retained.

`flac-report.json` is the unchanged original report from
`.build/cyd-header-metadata-flac-regression-20261101-05`: 520 exact complete-PCM
comparisons, 16 existing lifecycle cases, both registration selections and all
three existing semantic mutants pass their original expectations. The mutants
fail by the intended assertion, exit6, rather than timeout or sanitizer crash.
All 26 frozen source identities still match the working inputs at this record.
The original report is 478257 bytes, SHA256
`3df9f84d19c711e7dc5f5751f778164bf077ebabbd58117f72c7058dfc107e68`.

Attempts01–04 remain local and unchanged: missing output-metrics header,
missing platform error header, missing pending/EOF declarations, then an
outdated maintenance-mutant anchor. Attempt04 completed all 520 PCM comparisons
before the final anchor check stopped the runner. These attempts are not marked
passing. The final runner freezes the actual production PCM packet declaration
instead of maintaining a second copy; each ordinary FLAC PCM packet must carry
identity header gain. Existing assertions and golden PCM were not relaxed.

Only existing host regression and extraction/dependency maintenance ran here.
The explicitly deferred additional FLAC target error/backpressure scope remains
deferred. No board, flashing, reset, SDK decoder replacement or production FLAC
algorithm change is involved. Native binaries, generated fixtures and PCM stay
in the ignored local captures; these reports do not replay or publish them.

Run fresh existing regressions with unique output directories:

```powershell
python -B tests/run-cyd-lifecycle.py --output .build/<fresh-lifecycle>
python -B tests/run-cyd-flac-runtime.py --output .build/<fresh-flac>
```
