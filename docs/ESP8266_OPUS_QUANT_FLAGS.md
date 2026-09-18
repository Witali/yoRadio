# Opus ASM: same-address private flag loads

Date: 2026-09-18. Experimental raw benchmark, CPU160/QIO40; no change to
production defaults, original C fallback, GCC snapshot or accepted baseline.

## Hypothesis and exact scope

The previous packed `quant_all_bands` experiment regressed to81.875% CPU192.
It is **not** the parent. This experiment starts from accepted eBands-final
and changes only18 reachable reads of private `band_ctx.encode` (zero) and
`band_ctx.resynth` (one) into same-width MOVI instructions. It retains every
internal instruction address, every branch, all arithmetic and all calls.
The hypothesis is avoiding nonvolatile DRAM reads/load dependencies, not
reducing the number of instructions. A speedup is not assumed.

- 17 two-byte L32I.N become MOVI.N; one three-byte L32I becomes MOVI.
- 37 patched bytes in the original9416-byte function,3370 decoded instructions.
- Original384-byte call0 frame, callee saves and SAR behavior unchanged.
- Application903216 bytes for both images; zero static-RAM/stack delta.
- Control SHA256: `4155b84f57c6a87280b0f6ee2f0218aabb3d942751eb13fc01425e0b46202b81`.
- Candidate SHA256: `bf7b2ecde6f46e39a1bd0e0a5b0fe5dfa65d421e337025d576a84a6157d35f04`.

Artifacts are under `firmware/development/esp8266-opus-quant-flags-{control,candidate}-v1/`.
Each patch has original-PC, field, value and ABI comments in `patches.s`.

## Correctness before physical timing

`quant_flags_proof.cjs` observes converged load values from the pinned
`audit_quant_decode.cjs` analyzer, without modifying that old file or any
transfer/merge/CFG rule. It compares every original analyzer output against
an uninstrumented run. All18 values must be proven at the actual read, not
merely assumed from a nominal initializer. Removing the entry-zero,
immutable-field or private-frame contracts prevents specialization.

The existing linked caller/reference audit and pinned source contract remain
mandatory: native encode=0, sole real direct caller, no address-taken entry,
no field mutation by helpers,11 classified ROM division calls. Linked proof
compares every untouched instruction/address/width/operand exactly; MOVI must
have the original width and destination and the proven immediate value.
Whole ELF/application comparison rejects changes outside the18 patch spans
and the required image checksum. No encoder code or valid decoder mode is
removed, and there is no bitrate cap.

Host semantic mirror asserts immutable flags when read, substitutes their
values, and retains the accepted model chain. All24 cases pass exact PCM,
decoder state, reset/OOM, guards, ASan and UBSan:12/24/64/128/192kb/s,
320kb/s at2.5/5/10/20ms,510kb/s, mixed modes, phase/VBR fixtures and compound
120ms/48-frame packets. This is not a claim of running target ASM on the PC.
Six focused negative/positive regressions and six previous quant regressions
also pass. No physical speed result was available at this checkpoint.

## Physical protocol and acceptance

- [x] Fresh10A/10B/10A2 via native OTA,15s benchmark polling; preserve all
  errors, outliers and maxima without replacing attempts.
- [x] Validate raw packet/sample counts, PCM hashes and scratch/RAM behavior.
- [x] Recompute both high-bitrate speed gates and the separate75% CPU target.
- [x] Restore ordinary accepted ASM radio; check HTTP/WebSocket/playlist.

Run directories: `.build/opus-quant-flags-board-20260918/`.
Reporter: `tools/esp8266_opus_asm/report_quant_flags.cjs`.
These raw tests exclude network/audio-output CPU and do not establish the
required20s continuous I2S PDM plus WebUI. The overall goal remains open.

## Physical result: do not adopt as the new baseline

All30 attempts completed with exact target PCM hashes and packet/sample
counts. No attempt was dropped or replaced. Both comparisons are fresh,
with the same RAM fixtures and15s observation interval.

| Input kb/s | A CPU % | B CPU % | A2 CPU % |
| --- | ---: | ---: | ---: |
| mono12 | 23.098333 | 23.086750 | 23.085812 |
| mono24 | 53.895375 | 53.888896 | 53.895458 |
| stereo64 | 61.197625 | 61.201375 | 61.201333 |
| stereo128 | 70.365792 | 70.364854 | 70.378833 |
| stereo192 | 77.869750 | 77.851083 | 77.856958 |

Relative192 decode-time gain is only0.023972% versus A and0.007546% versus A2.
The first speed gate **fails**: minimum high-bitrate gain0.001332% (128)
is below the0.006128% slowdown at64. The repeated gate passes, but both are
required. The candidate is not adopted; accepted eBands-final remains the
parent for independent experiments. Do not claim either a statistically
established gain or a meaningful regression from these tiny differences.
The saved experimental image can be used in an explicitly separate bundle
experiment, not silently treated as an accepted optimization.

- Max192 wall-call times A/B/A2:19927/19984/20322us.
- Minimum sampled DRAM:2440/1756/1724B; lifetime free stack1660B in each group.
  Identical static memory and scratch bounds do not make these varying
  network-affected heap minima a codec memory saving.
- No HTTP observation timeout in these30 attempts. Raw task time exceeded
  its differently delimited wall window for B/run9 mono12 by278us and A2/run2
  mono12 by911us. Both are retained unchanged, with no clamping/subtraction.
- Combined local ASM, memory-lifecycle, reconnect and diagnostic-HTTP suite:
  33 passed,0 failed,0 skipped. Raw-image reconstruction and inherited
  semantic proofs are verified separately by the reporter.

Ordinary heapreserve accepted ASM radio was restored by OTA HTTP200/OK,
slot0x110000 ->0x10000, app SHA256
`dfa1c0a298dde56f33d5bb88627b4c9aa643deca12d5329ce4a0398e6f60b273`.
Stopped, no error, original Nightwave selection, RSSI-58dBm, combined free
heap30328B. HTTP/WS/getindex/playlist checks passed. No acoustic or visual
browser qualification is claimed. The source-only detection-cancellation
fix0edf328d is not in this existing restored image.

Saved evidence beside the candidate: all30 JSON/log pairs, manifests,
annotated ASM, ELF patch, `comparison.json`, OTA/snapshot records and tests.
Three result regressions pass: all30 hashes/OTA slots/PCM, exact recomputation
of medians and both gates, and confirmed restoration plus HTTP/WS/playlist.
JSON is pinned to LF in Git so these byte hashes survive Windows checkout;
raw logs are preserved verbatim and the parent ELF snapshot uses Git LFS.
The75% raw CPU and20s full-radio I2S/WebUI goals remain unproven.

## Separate follow-up hypotheses (not part of these images)

A read-only census of the same converged private-frame analysis found41
reachable constant-valued stack loads in total: the18 changed here plus23
reads of local copies/initializers in SP+124/+132/+140/+192/+220/+240.
Examples:0x40250902 (SP220=1),0x40250a95 (SP192=0),0x40250fc5 (SP240=0),
0x402514c0 (SP140=0),0x40251db8 (SP124=0),0x402521c5 (SP132=0).
These slots are reused: SP132 reads as1 at0x40252a20 but as0 elsewhere.
Do not replace by slot number alone: prove the value at each read and keep
the full call/alias/partial-store invalidation rules. This is a candidate
for a separate same-address experiment, not a demonstrated improvement.

Another possibility is replacing a constant load plus its flag branch with
one direct jump, using only unreachable padding and keeping outside PCs.
Candidate load PCs:0x40250ef3,0x4025191e,0x4025289c,0x40252913,0x40252943.
It additionally needs destination-register liveness on **every** successor,
all possible interior entries and a checked callee argument contract: a call
may read a2 before clobbering it. These removals are not authorized by the
current MOVI proof. Never reuse the rejected packed quant-decode image.
