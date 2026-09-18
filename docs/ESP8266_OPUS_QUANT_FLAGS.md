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

- [ ] Fresh10A/10B/10A2 via native OTA,15s benchmark polling; preserve all
  errors, outliers and maxima without replacing attempts.
- [ ] Validate raw packet/sample counts, PCM hashes and scratch/RAM behavior.
- [ ] Recompute both high-bitrate speed gates and the separate75% CPU target.
- [ ] Restore ordinary accepted ASM radio; check HTTP/WebSocket/playlist.

Run directories: `.build/opus-quant-flags-board-20260918/`.
Reporter: `tools/esp8266_opus_asm/report_quant_flags.cjs`.
These raw tests exclude network/audio-output CPU and do not establish the
required20s continuous I2S PDM plus WebUI. The overall goal remains open.
