# Independent public-consumer zero-sentinel diagnosis

The retained public C consumer has a concrete zero-magnitude shift bug. The public unpack helper represents a zero packed-float mantissa as value0 with point−9999. Canonical setup retains that zero representation and applies delta scaling as usual: `q_del >>= q_bits; q_delp += q_bits`. The public consumer then uses `point-q_minp` and `point-q_delp` as signed32 shift counts even when the corresponding magnitude is zero. A zero left operand does not make a shift count greater than31 valid.

This diagnoses the retained public source and the owned host diagnostic. The effect on an opaque vendor implementation is unknown. No opaque-code attribution, ABI normalization or production repair is proposed.

Actual root baseline completed all365 calls /366 normal child commands, terminal exit1 /chunk708824. Report SHA256 is `8289faff1ab23e749035ba912feefc58263c39b06f26f87689dd04fcb528c999`; outer receipt is `79adf7db0e86d0c5ae78e084143ad37746b1277ea0aa3237f759b946e48be22f`. The GCC compile completed without diagnostics. All331 available sanitizer-clean vectors equal their complete independent Fraction expectations. The34 UBSan failures produced no available vectors, so the complete Fraction comparison remains false. Those failures remain NONPASS, never expected passes.

The independently read metadata and source give this exact path:

| Case | Recorded zero fields | Declared points | First offending count | Calls without vectors |
| --- | --- | --- | --- | --- |
| 32, existing floor0 zero-minimum book | q_min0, q_minp−9999; q_del33554432, q_delp−29, q_bits5 | −8, −24 | minimum9991 /9975 | 4 |
| 34, additive unit-only zero delta | q_min−1073741824, q_minp−30; q_del0, q_delp−9997, q_bits2 | 0, −8, −24 | delta9997 /9989 /9973 | 15 |
| 35, additive unit-only zero minimum and delta | q_min0, q_minp−9999; q_del0, q_delp−9997, q_bits2 | 0, −8, −24 | minimum9999 /9991 /9975 | 15 |

For case35 UBSan first stops at the minimum shift; the later delta shift would independently use a sentinel-derived count too. This is a source-path observation, not a claim that the baseline reached that second instruction. In the frozen public port, the minimum shift is line139 and delta right shift is line145. Original public `codebook.c` is retained at SHA256 `0cfcbdadd7a491bc6bb7c24a2e7d3ed6ce9fb9360122b93631d205fcdf5ac749`; port SHA256 is `2660e256f14857b0aaa0f7104071796bc8095fa01c8eb1f87da82bdd116b696f`. `source-analysis.json` pins the exact source/ABI, contract, baseline report and receipt.

`PROPOSAL.diff` is an unapplied plan only. It adds two magnitude guards:

- q_min0 sets add0 directly; otherwise the original minimum shift branches are unchanged.
- q_del0 sets each component to add directly; otherwise the original scaled multiplication and shift branches are unchanged.

The sequence accumulation remains after those branches and is unchanged. A zero delta therefore preserves a constant minimum vector before sequence accumulation; it does not indiscriminately set every output to zero. With both magnitudes nonzero, the new conditions are false and every original arithmetic expression and branch remains identical. Codeword lookup, q_bits2/9/16 storage, dec_type2/q_pack0, bit consumption, min/delta/point fields, q_seq and the owned arrays do not change. A zero q_pack entry shift remains valid and is unrelated to this sentinel bug.

The guards do not normalize q_minp/q_delp, change encoded books or ABI fields, clamp/mask shift counts, alter fixed-point positions or unscale q_del. All chosen inputs already satisfy the scaled signed32 product bounds. A broader claim about arbitrary nonzero extrema or all other public arithmetic is outside this finite proposal.

No guarded C source, successor runtime or production file was created. This folder contains only the proposed diff, source/metadata analysis and plan. The preparing agent ran only source/JSON/hash checks; no prepared imports, tests, compiler, consumer, decoder, SDK, QEMU, Git or PCM operation ran.

The next gates remain sequential:

1. Root first records the actual unchanged SDK baseline: all36 canonical publications,439 protocol records,365 vector calls, normal owned free and full QMP quit/SHUTDOWN/EOF/reader-join/actual exit. Capture the actual Fraction match or NONPASS; do not rewrite the host baseline or require an invented passing outcome.
2. Only afterward, prepare a separate reviewed port successor with these exact two guards. Retain both immutable source baselines and every actual baseline failure/report/receipt. Keep the same36 fixtures,123 codewords,365 calls, oracle, existing GCC SHA, ASan/UBSan flags including `-fno-pie -no-pie`, parser/ABI and exact-equality criterion.
3. Root reruns all365 host calls. Require all331 previously available nonzero-path vectors to remain byte-identical and exact. Require complete availability, sanitizer-clean execution and exact independent expectations for the34 zero-field calls as new acceptance goals; these are not observed results yet. Preserve every original34 failure as historical NONPASS.
4. Root separately reruns the unchanged SDK publication path with the proposed consumer port. Actual returned scalar/array publications must remain identical to baseline, including zero sentinels. Check every full Fraction vector, canary, bit count, free and owned lifecycle. Keep SDK publication, complete numerical comparison and host sanitizers as distinct results.

Existing native singleton refusals, historical full-target numeric NONPASS, nonpreferred singleton-one tolerance classification and deferred scopes remain unchanged. Passing these finite owned-public-source checks would not prove full Vorbis compliance, a vendor cause or production integration.
