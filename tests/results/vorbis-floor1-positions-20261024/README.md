# Floor1 setup checks and preserved numerical NONPASS — 2026-10-24

Both CYD and C3 setup parsers now enforce the two requirements in
[Vorbis I §7.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html#x1-1170007.2.2):
at most 65 total X positions, including the two implicit endpoints, and no
duplicates. The count check precedes post/index/neighbor allocation; the
duplicate check uses the existing sorted index before neighbor construction.
Original position order, endpoints, ABI, arithmetic and task bindings remain.

The [generator](../../vorbis_format_corpus/generate_floor1_positions.py) creates
14 complete setups: 8 legal/6 invalid. Eight host construction tests pass.
Actual public raw-API SDK/QEMU runs qualify 8 legal opens, 6 FAIL/null rejections,
112 packets and 225280 byte-exact vendor/checked PCM bytes **per architecture**.
CYD uses SDK 6.0.2/Xtensa, 240 MHz, two CPUs, coordinator 0/worker 1; C3 independently
uses SDK 6.1/RV32, 160 MHz, unicore/core 0. No malformed setup reaches synthesis.

The two ESP32 controls independently remove one guard in a frozen copy.
After all 8 legal cases/112 packets, removing the count check accepts malformed
case 12; removing uniqueness accepts case 8. Both require observed OK/non-null
acceptance and the exact preceding transcript. All four SDK campaigns have
actual command exit 0 and controlled emulator termination; no panic/timeout
qualifies a control. These checks establish each guard's finite regression.

## Independent numerical results

The original 28-command host campaign is retained as NONPASS. Xiph/libvorbis
accepts all 8 legal cases and rejects all 6 invalid cases. Native FFmpeg accepts
only 7 legal cases, refuses the legal 32768 endpoint, and incorrectly accepts
the 66/250-position cases. Its first three PCM vectors also differ from Xiph.
The original classifier additionally mishandled Windows's unsigned
AVERROR_INVALIDDATA status and a secondary output error. The read-only replay
classifies the actual retained receipts/logs; it never overwrites or reruns them.

Full saved target PCM was compared to Xiph with the predeclared engineering
bound 2 S16 LSB, without trimming, shifting, gain, resampling or channel changes:

| Cases | CYD maximum error | C3 maximum error | Samples beyond 2, per case/platform |
| --- | ---: | ---: | --- |
| Endpoints1/2/8, cases0/1/2 | 65535 | 65535 | 13722 /10779 /7346 |
| Other 5 legal setups, cases3–7 | 1 | 1 | 0 |

CYD and C3 PCM are byte-identical across all 8 cases. All 8 Xiph PCM vectors are
also identical to one another. An independent signed16/packet-boundary readback
confirms the numerical failure; its report is `replay-sanity-review.json`.
The correlation with short endpoints does not establish the vendor's internal
cause. Both target numerical results, dual-reference acceptance and full G6
remain **NONPASS/open**. Older wide/floor0/sequence1 failures and all deferred
work remain unchanged; the CYD bridge is still isolated from the radio.

## Evidence and verification

`manifest.json` binds 1295 artifact aliases to 235 lossless gzip objects, retaining
one copy of each distinct body. Groups include corpus, actual SDK campaigns and
controls, original reference NONPASS, read-only replay, command receipts and
source audits. Executable/ELF/flash bodies are explicit hash/size omissions;
the archive does not claim complete dependency closure.

The original acceptance SDK child output is retained under each `build/log/`
alias; its outer PowerShell logs contain activation output only. Later controls
also use explicit async child-stream files. Their controller verifies complete
canonical corpus bytes and uses a smaller `COMPONENTS main` SDK build. Those
controller/build revisions are distinct from the frozen acceptance-01 runs.

Run from any working directory:

```text
python -B path/to/vorbis-floor1-positions-20261024/verify.py
```

The verifier checks archived bytes, actual transcripts/controls and complete
PCM metrics while preserving both numerical NONPASS results. It launches no
compiler, decoder, QEMU or device. `validation/` contains its actual command
receipt/logs, separate from the frozen manifest. No production image was built,
no board was used and no physical performance/memory benefit is claimed.
