# Opus ASM: constant local scalar copies

Date: 2026-09-18. CPU160/runtime QIO40, raw Opus-only experiment.
Parent is accepted eBands-final, **not** the unaccepted quant-flags or packed
quant-decode images. Production defaults and original C fallback unchanged.

## Hypothesis

Replace23 L32I instructions reading proven local0/1 copies with three-byte
MOVI, without changing any instruction PC, width, register destination,
branch, arithmetic, call, frame or literal address. This removes23 static
DRAM read sites, not23 dynamically executed instructions. No speedup is
assumed: the previous18 ctx-only read experiment did not pass both gates.

The69 patched bytes are in the original9416-byte `quant_all_bands`, keeping
all3370 disassembled instructions and the384-byte call0 frame. No RAM,
scratch, callee-save or SAR change. Source comments identify each PC, local
slot and the value proven at that specific point. All18 ctx reads from the
previous experiment remain original L32I.

## Correctness contract

Slots SP124/132/140/192/220/240 are **not** globally immutable. For example,
SP132 contains0 at0x402521c5 and1 at0x40252a20. Other reads of SP192 remain
dynamic and are not replaced. The existing converged constant-propagation
analysis is observed without changing its CFG, transfer, call/alias/partial-
write invalidation or join rules; its original outputs must still match.
Only the23 pinned PCs with proven per-use values qualify.

The original native-caller/valid-object/private-frame contract is rechecked
against the accepted linked ELF and C sources, including indirect ROM calls
and address-taken checks. Linked proof requires every other instruction to
remain exact. ELF/app comparison allows only69 patch bytes and the required
application checksum. No bitrate or mode restriction is introduced.

The host model checks origins of the spilled flags and initial local values;
it is not a one-to-one execution of Xtensa stack accesses. Local lifetime and
per-PC substitutions are covered by the separate linked proof. All24 host
PCM/state/guard/reset/OOM/ASan/UBSan scenarios pass, including12..510kb/s,
short and120ms/48-frame packets, mixed modes and phase/VBR fixtures.

Tools: `quant_locals.cjs`, `quant_locals_proof.cjs`,
`check_bands.cjs quant-locals` and `report_quant_locals.cjs` under
`tools/esp8266_opus_asm/`. Negative regressions invalidate contracts, partial
local stores, initializer sources, instruction operands and destinations.

## Required physical gate

- [ ] Fresh10A/10B/10A2,15s observation, retain every attempt and maximum.
- [ ] Target PCM hashes/counts, scratch/RAM, both high-bitrate speed gates.
- [ ] Separate75% raw CPU target and later20s live I2S PDM/WebUI requirement.
- [ ] Restore ordinary accepted ASM radio via native OTA, check HTTP/WS/playlist.

Artifacts: `firmware/development/esp8266-opus-quant-locals-{control,candidate}-v1/`.
Runs: `.build/opus-quant-locals-board-20260918/`. Native OTA only; no UART,
GPIO3 reset, Wi-Fi adapter changes, partition or SPIFFS writes.

This preflight is not an accepted optimization or a live-playback result.
