# Multipart output contract: GCC follow-up

2026-10-18. Supplement to the frozen [host checkpoint](HOST.md).

The first full C3 GCC15 build of `742d081f` stopped on three
`-Werror=maybe-uninitialized` diagnostics in the shared multipart helper.
CYD PDM/continuous built successfully. The original helper assigned both range
outputs on every successful path; GCC did not correlate the separate `found`
flag with those assignments. Commit `ef084fed` initializes both outputs and
uses the range pointer itself as the found predicate. Diagnostics stay enabled.

The [before/after record](gcc-output-contract/report.json) preserves the failed
full-build log and a passing actual C3 GCC component build. The
[multipart suite](multipart-gcc-output/report.json) repeats 896 header/body
checks, five actual receiver cases, four historical negatives and the OTA core.
The [full upload suite](uploads-gcc-output/report.json) repeats CYD69/C368,
reboot10 and pair105 scenarios under ASan/UBSan.

Focused clang-tidy for [C3](multipart-lint-c3/report.json) and
[CYD](multipart-lint-cyd/report.json) has zero errors and zero new diagnostics;
the same 12 parser style warnings remain per upload translation unit. All
reports record the new shared-header SHA. Final four GCC images/maps and
physical qualification remain separate gates, recorded in `SDK.md` when ready.
