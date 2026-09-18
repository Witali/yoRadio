# Firmware changelog

Every released build is recorded here. Existing release directories and
entries are retained; changes are published under a new firmware version.

## Development - 2026-09-18: branchless eBands-SRC (preflight only)

- `development/esp8266-opus-ebands-src-{control,candidate}-v2/app.bin`,
  903216B, CPU160/runtimeQIO40, raw decoder only. One existing36B leaf
  replaced, no RAM/stack/image growth;31B live code plus5B unreachable pad.
- 132416 numerical cases, symbolic signed16/SAR/bounds proof,24 exact host
  PCM/state/OOM/PLC scenarios and6 regressions passed. Never flashed;
  physical10A/10B/10A2 and speed acceptance remain pending.
- v2 corrects the host model's loop selection; candidate binary unchanged.
  [Preflight and limitations](../docs/ESP8266_OPUS_ASM_EBANDS_SRC.md).

## Development - 2026-09-18: quant_all_bands eBands leaf reuse (rejected)

- `development/esp8266-opus-ebands-quant-{control,candidate}-v1/app.bin`,
  903216B, CPU160/runtimeQIO40, raw decoder only. One15B replacement,
  existing signed-pair helper reused; no RAM/IRAM/frame or image growth.
- 132416 linked numeric cases, symbolic signed/ABI proof, CFG and negative
  tests;24 exact host PCM/state/PLC/OOM cases through510kbps/120ms.
- All30 physical A/B/A2 retained. CPU19277.863875/78.206833/77.887833%,
  CPU12870.377792/70.715292/70.396313%. Both speed gates FAIL. Rejected;
  accepted eBands-final and production defaults unchanged.75% not reached.
- Max192 wall call27.899/20.224/19.927ms; min DRAM1224/904/896B,
  stack-free1660B. The A/run4 90.066125% CPU outlier is included.
  No new continuous I2S or playback-time WebUI qualification.
  [Full experiment](../docs/ESP8266_OPUS_ASM_EBANDS_QUANT.md).

## Development - 2026-09-17: aligned positive eBands ASM (not accepted)

- `development/esp8266-opus-ebands-u16-aligned-{control,candidate}-v1/app.bin`,
  903216B, CPU160/runtimeQIO40. EXTUI saves one instruction per helper call;
  unreachable padding preserves five original cross-branch entry addresses.
- 401280 numeric cases, symbolic ABI/bit proof,24 exact PCM host scenarios,
  all30 physical A/B/A2 retained;20 local regressions PASS. No RAM/frame growth.
- CPU19277.875625/77.859187/77.879229%, CPU128
  70.385687/70.404708/70.372021%. Both high-bitrate gates FAIL; not accepted.
  Keep eBands-final baseline and C/default profile unchanged.75% not reached.
- DRAM minima2940/5184/7484B, stack free1660B; max192
  19.949/20.980/20.771ms. A2/run2 mono12 task>wall2615us preserved.
- Ordinary accepted ASM6914f484... restored OTA, station167/stopped,
  playlist/settings retained; HTTP200/169.5ms and WS observed while stopped.
  No UART/reset. No new continuous I2S qualification.
  [Method and full evidence](../docs/ESP8266_OPUS_ASM_EBANDS_U16_ALIGNED.md).

## Development - 2026-09-17: accepted Opus ASM in ordinary ESP8266 radio

- `development/esp8266-opus-live-asm-ebands-final-20260917/app.bin`,
  885792B, CPU160/runtimeQIO40, I2S PDM32 GPIO3,2x512DMA.
- Full accepted18-stage ASM chain relocated from raw eBands-final into
  ordinary radio. Benchmark/tone/runtime profiling OFF; diagnostic API ON.
  Graph/literal/image proofs exact; no static RAM, IRAM or stack growth.
  All24 host PCM scenarios exact;11 regressions PASS,0skip.
- OTA installed this image, slot0x10000. Ten real-station attempts saved:
  no qualified uninterrupted20s window, including HTTP/WS timeouts and
  incomplete observations. Final PCM age28.39s/input0/transport timeout;
  no latched decoder-init error in the final snapshot. Min heap1440B.
- New ASM remains installed, original selection167/stopped restored,
  playlist unchanged. Idle pages HTTP200 in121/99ms; this does not qualify
  WebUI responsiveness during playback. Default production profile is
  unchanged; do not label this build stable or claim a new raw CPU result.
  [Method, limitations and full results](../docs/ESP8266_OPUS_ACCEPTED_ASM_LIVE.md).

## Development - 2026-09-17: ESP8266 Opus byte-phase helper (not accepted)

- `development/esp8266-opus-pvq-byte-phase-{control,candidate}-v1/app.bin`,
  903216B, CPU160/runtimeQIO40, frozen accepted exp2-table32 parent.
- Six a10 calls use a seven-instruction phase leaf instead of nine SAR
  instructions; exact linked proof, no RAM/IRAM/frame growth, C unchanged.
- All30 physical A/B/A attempts retained with exact PCM: CPU192
  79.618646 /80.282333 /79.643604%, CPU12871.839771 /72.508813 /71.860083%.
  Both speed gates fail: candidate rejected; default and accepted baseline
  unchanged.78% is not reached and continuous I2S is not qualified.
- Free DRAM minima8168 /8032 /8352B, free stack1660B. No decoder/HTTP
  observation errors; candidate mono12 task>wall712us retained unchanged.
  Final14 regressions PASS/0skip. Prior diagnostic C-radio restored OTA;
  HTTP200107.34ms/WS/current167/stopped/settings/playlist verified.
  [Full result and evidence](../docs/ESP8266_OPUS_ASM_PVQ_BYTE_PHASE.md).

## Development - 2026-09-15: ESP8266 Opus cached PVQ endpoint costs

- development/esp8266-opus-endpoint-cost-{control,candidate}-v1/app.bin,
  903216 B, CPU160/QIO40 raw ASM benchmark over accepted bits-fourth.
- Eight same-width point replacements retain both already-read endpoint
  costs: exact branches/q/cost/ABI, no code relocation or RAM/frame growth.
  378304 linked cases,24 host PCM/state/PLC/reset/OOM cases through510kbps.
- All30 A/B/A retained: CPU19286.47023 /85.96527 /86.49377%;128
  76.07402 /75.71290 /76.11025%. Both high-bitrate acceptance gates PASS.
  New experimental raw baseline; default unchanged.80% target still unmet.
- Free DRAM minima8040 /6800 /8896 B, free stack1660 B. No observation
  errors; all maxima/window excess retained, candidate192 maximum26.714ms.
- Ordinary C radio restored OTA; HTTP200/WS/current167/stopped/playlist
  verified. This does not qualify continuous I2S PDM playback.
  [Details](../docs/ESP8266_OPUS_ASM_ENDPOINT_COST.md).

## Development - 2026-09-14: ESP8266 Opus FFT scheduled-load experiment (not accepted)

- `development/esp8266-opus-fft-schedule-{control,candidate}-v1/app.bin`,
  903216 B, CPU160/QIO40 raw diagnostic, accepted MDCT post-pair parent.
- One19-byte radix-5 fragment moves an independent pointer read before use;
  seven instructions instead of eight, no NOP or new RAM/frame/other ELF changes.
- Exact symbolic register/memory/alias proof,648 numeric overlap cases,
  39 final related regressions PASS/0skip,11 host semantic-parent cases exact.
- All30 A/B/A retained: CPU19287.48044 /87.53837 /87.47348%; both speed gates
  FAIL, candidate rejected. No static RAM/frame/scratch growth.
- Free DRAM minima3296 /7484 /8168 B, stack free1660 B. All maxima and
  accounting excesses retained. Ordinary restored OTA/HTTP200/WS/current167/
  stopped/playlist, no UART/reset. Default unchanged;70%/live I2S unmet.
  [Details](../docs/ESP8266_OPUS_ASM_FFT_SCHEDULE.md).

## Development - 2026-09-14: ESP8266 Opus FFT three-load experiment (not accepted)

- `development/esp8266-opus-fft-load3-{control,candidate}-v1/app.bin`,
  903216 B, CPU160/QIO40 raw diagnostic, accepted MDCT post-pair parent.
- One8-byte radix-5 group uses three L32I instead of four, no executed padding.
  Exact registers/data read order, all other ELF bytes/RAM/frame unchanged.
- All30 A/B/A exact PCM: CPU19287.47015 /87.47965 /87.47535%; both speed gates
  FAIL, no reproducible gain. Candidate rejected; default unchanged.
- 33 final related regressions PASS/0skip,11 host semantic-parent cases exact.
  Free DRAM minima8176 /8352 /8024 B, stack free1660 B, static RAM/frame same.
- Every attempt/maximum/accounting excess retained; ordinary restored OTA,
  HTTP200/WS/current167/stopped/playlist verified. Goal70%/live I2S unmet.
  [Details](../docs/ESP8266_OPUS_ASM_FFT_LOAD3.md).

## Development - 2026-09-14: ESP8266 Opus MDCT post-rotation pairs

- `development/esp8266-opus-mdct-post-pair-{control,candidate}-v1/app.bin`,
  903216 B, CPU160/QIO40 raw diagnostic, accepted three-table parent.
- One276-byte loop, four cached words, table loads8→4 per iteration pair.
  Exact modular32/in-place events, no new RAM/frame or other ELF-byte changes.
- 225 symbolic pairs/all standard transforms,16 numeric full transforms,
  28 final related regressions PASS/0skip,11 host semantic-parent cases exact.
- All30 A/B/A exact PCM: CPU19287.66144 /87.48144 /87.67425%; both high-bitrate
  selection gates PASS, accepted experimentally. No static RAM/frame growth.
- Minimum free DRAM1224 /8216 /8168 B, task stack free1660 B. All outliers
  retained: A/run6 timeout, A2/mono12 accounting excesses; all maxima archived.
- Ordinary restored OTA, HTTP200/WS/current167/stopped/playlist verified.
  Default unchanged; goal70%/continuous I2S unproven, max192 call21.829ms.
  [Details](../docs/ESP8266_OPUS_ASM_MDCT_POST_PAIR.md).

## Development - 2026-09-14: ESP8266 Opus MDCT MUL16S (not accepted)

- `development/esp8266-opus-mdct-mul16-{control,candidate}-v1/app.bin`,903216 B.
  CPU160/QIO40 raw-RAM diagnostic, parent accepted three-table MDCT pairs.
- 16 signed16 products use MUL16S instead of MULL; full CFG range proof,
  same widths/addresses/operands, no RAM/frame growth. Unsigned products unchanged.
- 589824 numeric edge pairs,28 final related regressions PASS/0skip.
- All30 A/B/A exact PCM: CPU19287.66965 /87.68683 /87.67142%, no gain;
  both selection gates FAIL. RAM/frame/scratch unchanged, candidate rejected.
- Control/run7 timeout/min DRAM1044 B retained, no excluded attempts;
  minima A/B/A2:1044/8032/8172 B, stack1660 B. All maxima archived.
- Ordinary C-backend radio restored OTA/HTTP/WS/current167/stopped/playlist;
  no production/default change. Goal70%/live I2S still unmet.
  [Details](../docs/ESP8266_OPUS_ASM_MDCT_MUL16.md).

## Development - 2026-09-14: ESP8266 Opus three-table MDCT pair experiment

- `development/esp8266-opus-mdct-three-pair-{control,candidate}-v1/app.bin`,
  903216 B, CPU160/QIO40 raw-RAM diagnostic; accepted MDCT-half parent.
- One193-byte pre-rotation range: cached t0/t1/bitrev pairs and shared parity,
  rescheduled exact modular32 arithmetic. No RAM/stack growth or other ELF changes.
- 450 symbolic pairs/all four transforms and16 numeric full transforms exact;
  23 final related regressions PASS/0skip, fresh11-case host semantic parent.
- All30 A/B/A retained, PCM exact. CPU192:88.05410 /87.68704 /88.06704%;
  both128/192 relative gains exceed minor mono12 loss: accepted experimentally.
  Free DRAM minima8176 /8168 /8384 B, stack1660 B, static RAM/codec scratch same.
- Candidate maximum192 call21.932ms;70%/continuous I2S still unproven.
  Ordinary C-backend radio restored OTA, HTTP200/WS/current167/stopped/playlist
  verified. No default/profile change or UART recovery.
  [Recipe and evidence](../docs/ESP8266_OPUS_ASM_MDCT_THREE_PAIR.md).

## Development - 2026-09-14: ESP8266 Opus paired bitrev reads (not accepted)

- `development/esp8266-opus-mdct-bitrev-pair-{control,candidate}-v1/app.bin`,
  903216 B. CPU160/QIO40 raw diagnostic; parent is accepted MDCT-half variant.
- One24-byte pre-rotation replacement caches two int16 entries in a0.
  Half as many bitrev loads, no new RAM/stack, all other ELF bytes unchanged.
  Pinned standard tables/ABI/liveness/signed bits checked; C/default unchanged.
- All30 A/B/A exact PCM,24 related tests PASS/0skip. CPU192:
  88.05546 /88.02013 /88.07158%; candidate NOT accepted: repeated128 gain
  0.01595% is below mono12 slowdown0.02031%. Max192 call22.621ms not improved.
- DRAM minima8004 /8172 /8168 B, stack1660 B. All attempts/maxima retained.
  Ordinary radio restored OTA, root HTTP200/WS/current167/stopped/playlist
  verified. Goal70% and continuous I2S qualification remain unmet.
  [Detailed results](../docs/ESP8266_OPUS_ASM_MDCT_BITREV_PAIR.md).

## Development - 2026-09-14: ESP8266 Opus MDCT halfword selection

- `development/esp8266-opus-mdct-half-{control,candidate}-v1/app.bin`,903216 B.
  Five17-byte ASM selector replacements, unchanged other ELF bytes/addresses,
  RAM/stack/aligned loads. CPU160/QIO40, tell-inline raw benchmark, default OFF.
- All30 A/B/A exact PCM, no decoder/observation errors.18 related tests PASS,
  0 skipped. Symbolic all-word/parity/ABI proof and fresh11-case host parent.
- CPU19288.11908 /88.06342 /88.10215%; tiny0.044–0.063% relative time gain.
  CPU128 also improves; both saved high-bitrate criteria pass. Experimental
  recipe retained, no production change. Max192 call23.009ms NOT improved.
- Free DRAM minima6116 /6836 /8032 B, stack1660 B. All attempts/maxima archived.
  Ordinary live512-idle3s restored OTA; HTTP200/WS/current167/stopped/playlist
  verified. Goal70% and continuous I2S qualification remain incomplete.
  [Details and evidence](../docs/ESP8266_OPUS_ASM_MDCT_HALF.md).

## Development - 2026-09-14: ESP8266 Opus frozen-layout reloads (rejected)

- `development/esp8266-opus-frozen-reloads-control-v1/app.bin` and
  `development/esp8266-opus-frozen-reloads-candidate-v1/app.bin`,903216 B each.
  CPU160/QIO40, raw-RAM tell-inline parent; no production/default change.
- Eight redundant private-stack L32I replaced by same-size MOV.N/OR.
  Every other ELF byte/address, instruction count, RAM and stack unchanged.
- Symbolic/linked proof, image XOR/SHA, parent host PCM through510 kbps/mixed
  and all30 physical PCM runs pass.19 final regression tests pass,0 skipped.
- CPU192 A/B/A2:88.17585 /88.13479 /88.13423%; no reproducible improvement.
  CPU128 also not better; candidate rejected, default unchanged.
- All outliers retained: A2/run2 HTTP observation timeout, DRAM minimum556 B
  (allocator lifetime520 B), no decoder error. Stack free1660 B in all groups.
- Ordinary live512-idle3s restored OTA; station167/playlist/stopped state,
  HTTP200/WS verified. Goal70% and live candidate qualification not achieved.
  [Recipe, scope and checks](../docs/ESP8266_OPUS_ASM_FROZEN_RELOADS.md).

## Development - 2026-09-14: ESP8266 Opus ASM partition decoder-only (rejected)

- `development/esp8266-opus-partition-decode-v1/app.bin`,902672 B; control
  `esp8266-opus-folding-control-v1`,903216 B. CPU160/QIO40/cache16 raw-RAM
  benchmark; optional `bands-partition-decode-asm`, default unchanged.
- Three proven encode=0 branches and179 unreachable instructions removed
  directly from GCC ASM; quant_partition2382→1870 B, original112-byte frame,
  calls/registers/rounding retained. No RAM growth, C fallback unchanged.
- Linked decoder CFG and caller checked;24 host PCM/guard scenarios exact,
  including510 kbps and120ms compound packets.
- All30 physical A/B/A retained: CPU192 88.1312 /98.3201 /88.1099%,
  about11.56–11.59% more time; CPU128 also slower. Rejected, default OFF.
  Minimum sampled DRAM8168 /8168 /8176 B, stack1660 B, no PCM errors.
- Ordinary live512-idle3s restored OTA; HTTP200/WS/playlist/current167 checked.
  No live qualification of the rejected candidate; goal70% remains unmet.
  [Proof and experiment](../docs/ESP8266_OPUS_ASM_PARTITION_DECODE.md).

## Development - 2026-09-14: ESP8266 Opus folding8 (rejected)

- `development/esp8266-opus-folding8-v1/app.bin`,903344 B; matched control
  `esp8266-opus-folding-control-v1`,903216 B. CPU160/QIO40/cache16 raw-RAM
  benchmark, opt-in `bands-folding8-asm`, not ordinary radio/default.
- One folding sqrt site uses a92 B flash table for N0 multiples of8 <=176;
  all other sizes keep the original sqrt. Original fixed-point coefficients,
  no RAM/stack growth, unchanged C backend and constant-N2 site.
- Host PCM through510/mixed/PLC/reset/OOM exact;108193 actual-instruction
  cases. All30 raw A/B/A attempts retained: CPU192 88.1440 /89.5171 /88.1026%,
  about1.56–1.61% more time; CPU128 also slower. Rejected, default OFF.
- Minimum sampled DRAM6796 /8852 /8392 B, stack1660 B, no PCM errors.
  Ordinary live512-idle3s restored OTA; HTTP200/WS/playlist/current167 checked.
  No live qualification of this rejected candidate. Goal70% remains unmet.
  [Implementation and checks](../docs/ESP8266_OPUS_ASM_FOLDING8.md).

## Development - 2026-09-14: ESP8266 Opus exact small-div inline (rejected)

- `development/esp8266-opus-small-div-inline-v1/app.bin`, 904080 B,
  compared with current-source `esp8266-opus-inline-control-v1`, 903216 B.
  Full hashes/build configuration are in their manifests. Opt-in
  `bands-small-div-inline-asm`, CPU160/QIO40/cache16; no board default change.
- Three exact reciprocal divisions expand inline, one516 B flash table,
  original ROM fallback and C backend retained. No RAM/stack growth.
- Linked-instruction model1,050,880 cases +20 fallback; exact semantic host
  PCM through510 kbps; 29 related regression tests pass, no skips.
- All30 A/B/A board attempts retained: CPU192 88.1175 /101.9579 /88.1273%,
  about15.7% more time; CPU128 also regresses. Rejected, not enabled by default.
  Minimum sampled DRAM8168 /8168 /8344 B, stack free1660 B, no PCM errors.
- Ordinary live512-idle3s app restored OTA, HTTP200/playlist/WebSocket/current167
  stopped state verified. No live qualification of the rejected decoder.
- These are raw-RAM benchmark builds, not normal radio. See
  [experiment](../docs/ESP8266_OPUS_ASM_SMALL_DIV_INLINE.md).

## Development - 2026-09-14: ESP8266 Opus ASM bit_logp shrink-wrap (rejected)

- `development/esp8266-opus-bands-logp-v1/app.bin`, 903232 B,
  SHA256 `4d702c39ecb911d6d941059cb66323f72058bee0d03823cfbf62c7a9940b2b5d`.
  Opt-in `bands-logp-asm` raw-RAM benchmark, not ordinary radio/default.
- Shared entropy leaf delays its 16-byte frame to normalization; fast path
  saves11 instructions, cold path count unchanged. No static RAM growth.
  100000 instruction cases,58 Node PASS, exact host PCM through510 kbit/s.
- All30 board A/B/A attempts retained: CPU192 88.100 /92.442 /88.121%,
  about4.93% more time, rejected. Includes run9 CPU192106.260%, minimum
  sampled DRAM1356 B; all PCM exact, no discarded attempts or decoder errors.
- Ordinary live512-idle3s firmware restored OTA, initially stopped state
  retained. HTTP/status/audio, WebSocket, playlist verified. Root137ms is
  a single HTTP response, not full-browser timing. Goal70% remains unmet.
  [Recipe and measurements](../docs/ESP8266_OPUS_ASM_LOGP.md).

## Development - 2026-09-14: ESP8266 Opus ASM inner-product unroll4 (rejected)

- `development/esp8266-opus-bands-inner4-v1/app.bin`, 903280 B,
  SHA256 `f5f698a8bbe33a7d3aba466f5764d2396e5c44b93b49a4a4802bef081b39d658`.
  Diagnostic raw-RAM benchmark, not an ordinary radio release. Opt-in
  `bands-inner4-asm`, implementation `b6217542`; default remains unchanged.
- Expands the renormalise_vector energy loop by four for N>=8, retains exact
  scalar tail and order. 6162 actual-instruction cases, 56 Node tests and
  exact ASan/UBSan host PCM through320/510 kbit/s, PLC/reset/OOM.
  No new RAM/stack, image +64 B versus tell-inline. Host-only length census
  records 31 calls per0.24 s at192 kbit/s, not a dominant decoding loop.
- All30 physical A/B/A retained: CPU192 88.103 / 94.984 / 88.120%,
  about7.81% more time. Rejected; no arithmetic/quality degradation.
  [Detailed report](../docs/ESP8266_OPUS_ASM_INNER4.md).
- Restored ordinary `esp8266-opus-live512-idle3s-20260913` via OTA, stopped
  as initially. HTTP/status/audio, WebSocket and playlist verified. Root HTML
  HTTP200 in130 ms is not a full-browser timing. No UART/SPIFFS changes.

## Development - 2026-09-14: ESP8266 Opus ASM PVQ cache reuse (rejected)

- `development/esp8266-opus-bands-cache-reuse-v1/app.bin`, 903232 B,
  SHA256 `a3110a46703df7a543616619d27c957c574de72e7baf1a854e98bc2194faf463`.
  Diagnostic raw-RAM benchmark only, not an ordinary radio release. Opt-in
  `bands-cache-reuse-asm`; source recipe committed as `e0157c50`.
- Reuses the loaded cache[lo] cost without new buffers. 376832 instruction
  cases, 53 Node tests, exact host PCM through320/510 kbit/s, PLC/reset/OOM.
  Static RAM and stack unchanged, image +16 B versus best tell-inline.
- All 30 physical A/B/A runs retained: median CPU192 88.135 / 92.242 / 88.165%.
  Candidate slower on every fixture; rejected, default unchanged. Exact PCM
  on board, no decoder errors. See [report](../docs/ESP8266_OPUS_ASM_CACHE_REUSE.md).
- Restored ordinary `esp8266-opus-live512-idle3s-20260913` via OTA; native
  status/audio, WebSocket, playlist and root HTTP200 verified. Initial stopped
  state retained; no UART/USB recovery or SPIFFS update.

## Development - 2026-09-09: optional ESP8266 Ogg Opus

- Source `6a9f8ea`. Experimental app 881536 B; Opus-disabled regression app 763936 B.
  Both saved under `development/esp8266-opus-{experimental,disabled-regression}`
  with manifests/checksums. No board deployment or physical speed claim.
- Vendored fixed-point decoder, bounded scratch/shared IRAM, incremental Ogg,
  mono output up to 20 ms packets, codec lifecycle and WebUI integration.
  Experimental only; normal default remains MP3/AAC without Opus.
- 334/334 host tests passed. Final IRAM width fix additionally passed 12 focused
  tests and exact PCM against pristine upstream on 292800 samples.
- Future deployment is OTA; USB/serial not used. Remaining target RAM/CPU/stack
  qualification and a further memory-reuse candidate are recorded in
  [ESP8266 Opus documentation](../docs/ESP8266_OPUS_NATIVE.md).

## Development - 2026-09-09: ESP8266 volume 0..100

- `development/esp8266-volume100-production/app.bin`, source `be0207e`,
  763952 B (+704 versus LED production), SHA-256
  `fdb5565b24e72a7badadca7bac90ebf7a0dc1f04d5ad8ae11374cafee4aa0214`.
- Slider, WebSocket volume command/status, +/- buttons and encoder use
  inclusive 0..100; legacy NVS/gain remain 0..254 to preserve saved loudness.
  No PCM-loop change, new task, heap buffer or static DRAM/IRAM increase.
- Matching `script.js.gz` is included. Deploy it to `/www/script.js.gz`
  before application OTA; then reload all tabs. Other chips retain 0..254
  unless their firmware advertises the new `volumeMax=100` capability.
- 324/324 ESP8266 + shared WebUI host tests passed; build emitted no compiler
  warnings. No physical deployment, listening or browser-on-board test in
  this change. The previously documented audio/WebUI performance issues
  are not claimed fixed by the volume-scale change.
- I2S PDM32/GPIO3, QIO40/160 MHz, input 4096 B, short HTTP-priority profile,
  LED 10 Hz/max 32 and diagnostic logging disabled remain unchanged.
- [Deployment/verification details](development/esp8266-volume100-production/verification.md),
  [remaining-target plan](../docs/VOLUME_0_100_SYNC_PLAN.md).

## Development - 2026-09-09: ESP8266 LED regression correction

- `development/esp8266-led-production/app.bin`, source `82edaf2`, 763248 B,
  SHA-256 `3a06bb31ac4f31f311ffb57e825fe36956f23549037eac383697f54d9daf8235`.
  Installed via OTA in app1. I2S PDM32 remains on GPIO3; radio left playing.
- GPIO2 LED: 10 Hz, peak from every fourth of a bounded group of frames
  inside the gain loop; no second PCM walk, extra task, ISR or heap buffer.
  Background services retain 250-ms cadence independently of the LED.
- Existing enable flag retained; tested brightness ceiling changed to 32.
  Full scale 255 reproduced long stream/audio stalls, while OFF/1/32 did not
  in these windows. The physical coupling mechanism remains unproven.
- `development/esp8266-led-diagnostic/app.bin`, 765840 B, SHA-256
  `e09ce877727f25e9dc389143a7725ba1bfe25fe42c4f14098daeac229a5c1b65`:
  separate explicitly diagnostic SPIFFS/HTTP logging. Production excludes
  both file logging and its routes (HTTP 404 checked on board).
- 263/263 host regressions passed. Final audio sample 22.465 s: 98.91%
  PCM/time, free RAM >=8432 B, no long PCM stall, **253 underrun events**.
  This is not a zero-underrun pass. Occasional slow HTTP transfers remain.
- A/B control builds (low-overhead, OFF, diagnostic, cap1, cap32) retained
  with exact configs/manifests. See
  [full results and remaining work](../docs/ESP8266_LED_REGRESSION_2026-09-09.md).

## Development - 2026-09-09: ESP8266 hardware audio-level LED

- `development/esp8266-audio-level-led/app.bin`: ordinary native radio, source
  `a98116e`, 764272 bytes; SHA-256
  `562e1986f72097f33210fa85ce1e4a7350ef056522d24b051a43694915001517`.
- GPIO2 module LED uses hardware sigma-delta at its minimum bit clock with
  20-Hz envelope updates (10 Hz selectable at build time). No software PWM
  ISR or new task. At most 64 post-gain mono frames are sampled per update;
  this cosmetic indicator can miss transients between snapshots.
- PDM32 audio remains on GPIO3, unchanged byte-for-byte in host reference
  tests with LED hooks on/off. SPI and NoDAC I2S support the LED; conventional
  external-DAC I2S disables it because GPIO2 is WS. Stereo profile synchronized.
- +16 bytes static DRAM, no extra IRAM, +944 bytes application image versus
  the previous SPIFFS-logging production image. Short WebUI audio pause and
  local SPIFFS error logging retained. Built, host-tested and OTA-installed;
  physical LED brightness and CPU time are not yet measured.
- Final ESP8266 host regression: 257/257 passed, no skips. Includes LED tests
  at 10/20 Hz and bit-exact PCM/PDM comparisons with LED hooks on/off.
- Installed by OTA on 2026-09-09: HTTP 200/OK, confirmed new slot `0x110000`,
  Wi-Fi and HTTP/WebSocket status available. Main HTML fetched in 163 ms
  (single request, not a render benchmark). ROCK FM was stopped before and
  after update; the sound/LED test is left to the user.

## Maintenance - 2026-09-09: remove obsolete test images

- Removed 54 test/experimental directories from `development/`: isolated
  MP3/AAC and DMA benchmarks, audio/memory/TCP profiles, network sweeps,
  libmad and network-reader experiments, RC-PDM comparison builds, temporary
  SPI debug/tone images and alternate WebUI-pause A/B builds.
- Moved all 195 files (31,322,401 bytes, 29.87 MiB) into the ignored local
  safety archive `.build/firmware-test-archive-2026-09-09/`, including eight
  untracked files. This cleans `firmware/`, not the total disk or Git/LFS
  history. Previously tracked artifacts remain recoverable at `904394b`.
- Verified SHA-256 for every archived file and all 117 retained firmware
  files. Releases `0.9.721` through `0.9.724`, current logging-enabled radio,
  logging-disabled radio, ordinary variants and the modified WebRadio binary
  were preserved byte-for-byte. No firmware was rebuilt or flashed.
- Source code, test scripts, benchmark reports and unrelated working-tree
  changes are unchanged. Earlier entries below remain historical records.

## Development - 2026-09-08: HTTP receive throughput and CPU accounting

- Added opt-in native network benchmarks with the same decoder allocations,
  HTTP client and DMA configuration. Deterministic local MP3/AAC sources
  support unlimited and paced 64/128/320-kbit/s delivery. No new stream
  buffer or production decoder/output algorithm change.
- Original 20-second unlimited runs: 460.5..569.9 kbit/s, plus an aborted
  attempt. A runtime-instrumented run reached 816.5 kbit/s; none of these
  results guarantees continuous playback. Receive-only 320 had a 947-ms gap.
- Reduced-probe runtime measurement: non-idle 22.27/25.39/42.55% at actual
  64.23/128.14/518.77 kbit/s, without decoding. Connected background 2.17%.
  The reading task uses about 16%; 1-ms empty socket polling is a candidate
  for future optimization. The 320-kbit/s CPU case ended on timeout.
- Four diagnostic images, configurations and raw measurement reports are
  retained in development/esp8266-network-{profile,bulk,cpu,cpu-lean}/ and
  docs/benchmarks/esp8266-network-2026-09-08/. Exact hashes and caveats:
  docs/ESP8266_NETWORK_BENCHMARK_2026-09-08.md.
- Ordinary I2S PDM production image: source 4cea0d9, 760032 bytes, SHA-256
  E79263CC1B8F0E245D3D0F52E7CF6941671FCB3CAB76BF01C10CEAA3E15957BC.
  CPU160/QIO40, GPIO3, two 512-word DMA buffers, ERROR logs; network and
  codec benchmarks/runtime tracing are OFF. SPIFFS/NVS are not reflashed.

## Development - 2026-09-08: AAC-LC flash-source benchmark

- Added isolated flash-output (288224 bytes) and flash-decode (278672 bytes)
  AAC-LC images, source 75b6104. Same tone/noise source as MP3, target
  48/64/96 kbit/s, 44.1 kHz stereo encoded / mono PCM, 1000 measured frames.
- Decoder-only uses 64.77/67.25/69.50% of PCM time budget. The complete
  PDM/DMA path fails continuity in all three cases, Wi-Fi OFF:
  2098/2841/2916 neutral underruns per 23.219954 s PCM.
- Production decoder/output code and defaults are unchanged.
  Restore the ordinary I2S PDM production image after benchmarking.
- Saved fixtures, logs, JSON reports, exact configurations and binary
  hashes: docs/ESP8266_AAC_FLASH_BENCHMARK_2026-09-08.md.

## Development - 2026-09-08: MP3 flash-source benchmark and recovery diagnostics

- Ordinary I2S PDM32 image: development/esp8266-i2s-pdm-production/app.bin,
  source d8d0219, 760032 bytes, SHA-256
  670D808E07B91BA0ABE575A00DF5FA71544F7C83C1D4B3AB49A75B88F0813AF7.
  CPU160/QIO40, Helix SSO mono, 2 x 512 DMA words, ERROR logs only.
  No benchmarks/test files included; native radio/WebUI remain enabled.
- Stream inactivity timeout is build-configurable, default 1000 ms.
  Reconnect retries cannot overwrite newer user commands. Audio health
  exposes physical DMA progress; NoDAC does not mux unused external clocks.
- Separate MP3 flash-output and flash-decode images retain deterministic
  tone/noise fixtures at 64/128/320 kbit/s without whole-file RAM copies.
  64/128 pass 26.12 seconds of digital continuity; 320 has 286 underruns.
  Old repeated-Info MP3 results are invalid as music-decoding measurements.
- Measurements, exact configurations, hashes and limitations:
  docs/ESP8266_MP3_FLASH_BENCHMARK_2026-09-08.md.
  Live radio/WebUI acceptance is still unresolved; no analog capture.

## Development — 2026-09-06: bounded AAC PCM output

- Ordinary image: `development/esp8266-native-aac-blocks/app.bin`, source
  `9f991d6`, 690032 bytes. CPU160/QIO40, mono Helix MP3 SSO/AAC-LC,
  GPIO3 I2S-PDM32, profiling/trace/benchmarks OFF.
- AAC defaults to 512-frame callbacks / 1024 bytes mono PCM rather than a
  complete 4096-byte stereo frame. Actual AAC DRAM falls 9876 -> 6804 bytes;
  16384-byte IRAM arena and 2 x 512-word DMA payloads are unchanged.
- 341 host tests passed. PCM and next-frame overlap match the previous
  implementation, including mono clipping/rounding and all window sequences.
- On the physical board, the selected 512-frame path produced 4.266666 s of
  320-kbit/s AAC audio in 4.254014 s wall time with zero measured underruns.
  Smaller sizes were tested and had more underruns. Decode-only cost rose
  about 6.1%; this is a RAM optimization, not a decoder speed improvement.
- The twelve isolated A/B images (`esp8266-native-aac-decode-*` and
  `esp8266-native-aac-output-*`) are diagnostic, Wi-Fi disabled, and must not
  be used as normal radio firmware. Each includes a manifest and hash.
- See `docs/ESP8266_AAC_PCM_BLOCKS.md` and its retained measurement logs.
- Ordinary app0 flash/hash/startup verified, 511-station index retained.
  Wi-Fi association was delayed and HTTP at the prior IP timed out; live
  streaming/WebUI are not certified by this AAC change.


## Development — 2026-09-05: ESP8266 DMA starvation recovery

- Ordinary image: `development/esp8266-native-dma-recovery/app.bin`, source
  `aab3600`, 687312 bytes. App0 flashed and hash verified; NVS, SPIFFS and OTA
  selection retained. The 16-KiB IRAM decoder arena still fits.
- Hand off committed prefixes only when no producer loan is outstanding;
  use 64-word neutral retries while playing and 512-word neutral blocks
  when stopped. Buffer capacity remains 2 x 512 words. Mono ignores balance.
- Added an opt-in RAM decoder-to-PDM/DMA benchmark and A/B build switch.
  In isolated physical tests MP3 had zero underruns; AAC produced 4.267 s
  in 4.259 s with four short neutral retries and zero FIFO-empty flags.
- 338 host tests pass. Preserve the rejected prefix-only experiment and
  whole-buffer baseline separately, explicitly labelled diagnostic.
- The prior image's sound was confirmed but distorted. The new ordinary
  image started Retro FM and publishes WebSocket playing/reconnecting state;
  live-stream reconnects and initial HTTP timeouts remain. Listening
  acceptance and long-run network stability are not claimed.
- See `docs/ESP8266_DMA_STARVATION_RECOVERY.md` for measurements and limits.

## Development — 2026-09-05: ESP8266 PCM32, direct DMA and mono mute fix

- Source `6bd547b`; ordinary image saved as
  `development/esp8266-native-pcm32/app.bin` (687232 bytes). Optional bounded
  diagnostic image is `development/esp8266-native-pcm32-trace/app.bin`
  (689792 bytes). Older artifacts are retained.
- Helix MP3 emits 32-frame blocks; mono PCM storage falls from 1152 to 64
  bytes. Actual MP3 DRAM workspace is 8440 bytes, with 16384 bytes in IRAM.
- PDM is generated directly in a reserved producer-owned DMA span. Two
  512-word buffers, neutral underrun output and task stack sizes are retained.
- Fixed unsigned balance clamping that turned neutral balance into -16 and
  muted mono. Balance is ignored for mono input, including all codecs in
  build-time Mono mode; volume and normalization still apply.
- 337 host tests pass; PCM/PDM equivalence, settings, ownership, EOF races,
  cancellation and timeout are covered. GCC output-write frame is 80 bytes
  versus 352 previously; no matched hardware CPU timing was performed.
- Physical trace confirms nonzero decoded/processed PCM and changing DMA
  words. Restored/flashed the ordinary image, preserving NVS/SPIFFS/OTA
  selection; MP3/WebSocket status and WebUI HTTP 200 verified. Stream
  reconnects remain; long-run continuity and listening are not yet confirmed.
- See `docs/ESP8266_PCM32_DIRECT_DMA.md` and per-image manifests.

## Development — 2026-09-05: ESP8266 shared MP3 reorder workspace

- Saved `development/esp8266-native-mono-reorder/app.bin`, source `f3138f2`,
  686848 bytes; previous firmware artifacts remain unchanged.
- Reuse idle IMDCT output for reorder, removing one 792-byte DRAM allocation.
- Separate/shared PCM matches byte-for-byte in Mono and Stereo. Allocation
  failures, reset and AAC/MP3 lifecycle tests pass; all 331 host tests pass.
- GCC O3 firmware builds; static DRAM/IRAM size unchanged, image 96 bytes smaller.
- Subsequently flashed app0 on the Wemos D1 mini with hash verification;
  NVS/SPIFFS/OTA selection preserved. Wi-Fi, HTTP and a short WebSocket MP3
  128-kbit/s play/stop test passed, with one stream-open retry. Physical MP3
  workspace is 9528 bytes DRAM / 16384 bytes IRAM. Long-run performance and
  listening remain untested; see the shared-reorder document for raw results.

## Development — 2026-09-05: ESP8266 mono MP3 M/S fast path

- Saved `development/esp8266-native-mono/app.bin` separately from the
  physically verified preceding build; source `236d4ad`, 686944 bytes.
- Added build-time Mono/Stereo; default Mono skips the difference channel
  for compatible M/S MP3 and retains safe fallback for other stereo modes.
- MP3 PCM storage is 1152 bytes smaller; unchanged two-buffer DMA output.
- Fixed pre-existing MPEG2.5 sync detection, now covered by own fixtures.
- 329 host tests pass; Mono firmware and Stereo/libmad decoder component
  builds pass. CPU timing and listening on the board remain untested.
- No flashing, settings changes or WebUI asset update performed.

## Development — 2026-09-05: ESP8266 memory-only diagnostic

- Saved `development/esp8266-native-memory-profile/app.bin` and its manifest.
- Added opt-in allocation-free DRAM fragmentation/low-water and task-stack
  measurements, with normal MP3/AAC, Wi-Fi, WebUI and I2S PDM configuration.
- Saved a repeatable physical workload including codec switches and two real
  browser pages. See `docs/ESP8266_MEMORY_HEADROOM_2026-09-05.md` for results
  and failures; this is not a claim that the two-tab acceptance test passed.
- The ordinary native profile and its buffer/stack defaults are unchanged.

## Development — 2026-09-02

### ESP8266 verified default memory and streaming profile

- Locked the default to QIO40/160 MHz, Helix MP3 SSO + AAC, and GPIO3
  I2S-PDM32 with the static 2 x 512-word DMA ring.
- Kept the physically reliable 16-KiB IRAM codec arena and split MP3 IMDCT
  output by channel; the measured active workspace is 11,472 bytes DRAM and
  16,384 bytes IRAM.
- Bounded WebSocket sends, kept radio HTTP connections alive, reconnected clean
  stream EOF, and reduced persistent WebUI buffers without changing pages.
- Flashed the Wemos D1 mini and verified MP3 128 kbit/s playback, 32 WebSocket
  status frames over 60 seconds, and subsequent HTTP 200 status recovery.
- All 290 repository tests pass; the replaceable development binary and
  manifest were updated.

### ESP8266 canonical audio profile and end-to-end trace

- Made the tracked `sdkconfig.defaults` authoritative and explicit: QIO 40 MHz,
  160 MHz CPU, Helix MP3 SSO, Helix AAC, GPIO3 I2S-PDM32 at 1.536 MHz and a
  static 2 x 512-word DMA ring; experimental alternatives are disabled.
- Added an opt-in bounded diagnostic mode that fingerprints raw decoder PCM,
  processed mono PCM and the actual PDM words copied into the SLC-DMA ring.
  It is compiled out of the production image.
- Physically verified HTTP/ICY -> MP3 detection -> Helix decode -> fixed-point
  normalization/volume -> stereo-to-mono -> PDM32 -> DMA, while WebUI remained
  connected and changed from stopped to playing.
- Rebuilt the ordinary no-trace image, passed all 284 tests and archived it in
  [`development/esp8266-native-qio40-sso-pdm1536/`](development/esp8266-native-qio40-sso-pdm1536/).
### ESP8266 GPIO2/I2S status LED constraint

- Verified against the ESP8266EX pin table that I2S output uses fixed GPIO3
  DATA, GPIO15 BCLK and GPIO2 WS signals.
- A physical experiment reclaimed GPIO2 after the first DMA completion: the
  onboard LED then followed the requested 500-ms playback blink, but PDM audio
  stopped. Keeping GPIO2/GPIO15 assigned restored the GPIO3 audio output.
- The production I2S-PDM profile now leaves both hardware clock pins active and
  disables software ownership of the onboard LED. Its apparently steady light
  is the visual average of the 48-kHz WS waveform, not the player status.
- GPIO2 Wi-Fi/playback indication remains available only with the legacy
  SPI-PDM backend, which outputs audio on GPIO13 and does not claim GPIO2.
- Rebuilt and flashed the QIO40/160-MHz image, connected to Wi-Fi, started Retro
  FM as MP3 128 kbit/s, and passed all 282 repository tests.
### ESP8266 WebUI physical reliability

- Changed the Wemos default from QIO 80 MHz to QIO 40 MHz after verified QIO80
  images intermittently stopped immediately after the ROM loader on the physical
  module. Named QIO80 profiles remain available for explicit experiments.
- Fixed truncated HTML and JavaScript by copying memory-mapped IROM data through
  a DRAM scratch buffer, pacing 512-byte chunk writes, retrying transient lwIP
  `ENOMEM`/`ENOBUFS`, and allowing up to 15 seconds for a congested send.
- Removed `TCP_NODELAY` and the eager server-side close that could split chunk
  framing into tiny packets or discard the final queued bytes on a weak link.
- Reused one static scratch buffer for static files, playlist lines, and initial
  WebSocket state, avoiding the HTTP-task stack-canary reset seen with nested
  local buffers while retaining the documented 5120-byte minimum stack.
- Added regression checks for DRAM-backed IROM sends, bounded retry behavior,
  stack usage, QIO40 defaults, and all saved build profiles. All 280 tests pass.
- Flashed the physical Wemos and verified HTTP 200 for every page asset, the
  complete 36,086-byte playlist, and status. The isolated WebSocket scenario
  covered settings, station selection, Play, Stop, Pause, Next, and Previous.
- Archived the validated image under
  [`development/esp8266-native-qio40-sso-pdm1536/`](development/esp8266-native-qio40-sso-pdm1536/).

### ESP8266 playback and WebUI hang fixes

- Rebuilt and flashed the QIO80/160-MHz Helix SSO production profile with
  1.536-MHz I2S/SLC DMA PDM output.
- Removed unbounded waits from the radio socket and I2S-PDM callback. The
  stream socket is nonblocking and each PCM callback now has one cumulative
  100-ms DMA deadline rather than a fresh one-second wait for every batch.
- Allocated the exact 2304-byte MP3 PCM buffer instead of the 4096-byte AAC
  maximum, leaving 1792 more heap bytes for lwIP while MP3 is active. Codec
  switches still release the old decoder before allocating an incompatible
  replacement.
- Fixed incomplete WebUI downloads on the ESP8266 SDK: short HTTP responses
  use standard `Connection: close`, `TCP_NODELAY`, and deferred session close
  so the terminating chunk is flushed and the scarce socket is released.
- Kept the HTTP/WebSocket task stack at 5120 bytes. A physical 4096-byte test
  reproduced a FreeRTOS stack-canary reset during `getindex`; the 5-KiB minimum
  is now documented in the target README.
- Added Web API regression coverage for Play, Stop, Toggle, Next, Previous,
  current-station publication, player state, bitrate, and RSSI. All 280
  repository tests pass.
- On the physical Wemos D1 mini, WebSocket initialization and all settings
  requests passed. MP3 playback reported 128 kbit/s, 44.1 kHz stereo and sent
  live player/RSSI updates for about 50 seconds despite -74 to -86 dBm RSSI.

## Development — 2026-09-01

### ESP8266 I2S-PDM 1.536-MHz carrier

- Set the default I2S/SLC PDM carrier to nominally 1.536 MHz. The ESP8266
  divider produces 1.538461 MHz (+0.16%) and production uses genuine PDM32 x1;
  genuine PDM128 at 6.144 MHz remains an experimental build option.
- Two static 512-word DMA buffers implement true ping-pong buffering. They
  occupy 4,096 bytes and each covers about 10.67 ms. A direct FreeRTOS task
  notification blocks once per returned buffer, replacing 2-ms polling
  without dynamic allocation.
- Added a 456-byte IRAM, branchless, fully unrolled PDM32 packer. On the
  physical Wemos D1 mini it generated 100.2% realtime PCM with zero ping-pong
  underruns and reduced producer non-wait time from 33.5% to 9.1% (3.66x).
  Genuine PDM128 at 6.144 MHz reached only 64.4% realtime and remains rejected.
- Isolated 320-kbit/s RAM fixtures measured Helix MP3 SSO at 28.12% CPU and
  Helix AAC-LC at 76.20% CPU. The production binary is archived under
  [`development/esp8266-native-qio80-sso-pdm1536/`](development/esp8266-native-qio80-sso-pdm1536/).

### ESP8266 MP3 SSO with 384-kHz SPI-PDM

- Added a separate MP3 SSO + SPI-PDM8 profile while retaining 16-bit,
  769.231-kHz SPI-PDM as the normal default.
- The new HSPI configuration outputs eight PDM bits per 48-kHz PCM sample at
  384.615 kHz. It halves conversion work and transfer interrupts, doubles the
  12-block queue coverage to about 16 ms, and trades this for higher one-bit
  quantization noise.
- Built the complete QIO80/160-MHz radio and WebUI image, verified the final
  SDK configuration, and passed all 267 repository tests. The build is
  archived for physical testing under
  [`development/esp8266-native-qio80-sso-pdm8/`](development/esp8266-native-qio80-sso-pdm8/).

### ESP8266 isolated audio-output profiles

- Added a deterministic generated-PCM benchmark that exercises the real audio
  driver without Wi-Fi, HTTP, flash reads, or a decoder.
- Removed the producer-side 64-byte SPI-PDM copy by filling a reserved static
  queue slot directly. On the physical Wemos D1 mini this reduced output
  compute by 6.07% and total CPU busy time by 1.2 percentage points with no
  heap cost.
- Saved one QIO80 configuration for both stream profiling and generated-PCM
  output testing. SPI-PDM remains the default; the same benchmark compiles
  with fixed I2S/SLC DMA for a future GPIO3/15/2 hardware comparison.
- Refreshed and flashed the ordinary QIO80 radio/WebUI image after testing;
  WebUI returned HTTP 200 at `192.168.100.6`.

### ESP8266 Helix 32-bit SSO MP3 synthesis

- Added an optional reduced-precision Helix polyphase path that maps the hot
  synthesis loop to native LX106 32-bit multiply/accumulate operations without
  adding decoder buffers. The exact 64-bit path remains available at build
  time.
- The retained 320-kbit/s stereo fixture kept all frames and samples, measured
  48.50 dB PCM SNR against exact Helix, and had a maximum error of 34 signed
  16-bit PCM levels.
- On the physical 160-MHz Wemos D1 mini, average MP3 frame time fell from
  13,705 to 6,414 us (53.20%); isolated throughput rose from 1.751x to 3.741x
  realtime with unchanged codec DRAM and free heap.
- Built and flashed the complete radio/WebUI QIO80 image. It connected at
  `192.168.100.6`, served WebUI/status/playlist over HTTP 200, and started an
  MP3 128-kbit/s stereo station through WebSocket control.
- Archived the development image and exact hashes under
  [`development/esp8266-native-qio80-sso/`](development/esp8266-native-qio80-sso/).

### ESP8266 experimental libmad IRAM frame workspace

- Moved the 4,608-byte Layer III spectral workspace and 2,304-byte reorder
  workspace from `mad_frame` DRAM into the shared aligned 32-bit IRAM arena.
  The byte-addressed stream reservoir, frame header, subband samples, and
  overlap state remain in DRAM.
- Reduced the Xtensa `mad_frame` layout from 20,784 to 13,880 bytes, freeing
  6,904 bytes of 8-bit DRAM. The MP3-only profile now reserves 12 KiB IRAM,
  of which the decoder uses 11,152 bytes.
- Verified byte-identical PCM between the original and external-workspace
  layouts, passed all 261 repository tests, and built both MP3-only and full
  libmad+AAC QIO80 images.
- On the physical 160-MHz Wemos D1 mini, the new libmad decoded the retained
  320-kbit/s RAM frame in 11,965 us average (2.005x realtime), versus Helix at
  13,786 us (1.740x). libmad is 13.21% faster by frame time, but uses 7,424
  bytes more DRAM and adds 50,384 bytes of flash. The ordinary validated Helix
  radio image was restored after the benchmark and obtained `192.168.100.6`.
- Archived the test image under
  [`development/esp8266-native-libmad-iram/`](development/esp8266-native-libmad-iram/)
  without replacing the previously hardware-validated libmad image.

### ESP8266 experimental libmad MP3 backend

- Follow-up: made libmad follow the common codec-arena lifetime. `mad_stream`,
  `mad_frame` and `mad_synth` now have symmetric allocation/free paths; input,
  PCM and decoder state are created only after stream detection and released
  on Stop/error.
- Added exact DRAM/IRAM accounting, post-allocation reserve checks and a
  50-create/50-switch physical stress test; heap returned from 96,868 to 96,868
  bytes with no leak.
- Added the tested MP3-only QIO80 profile. Its 5-KB IRAM arena covers the
  measured 4,236-byte `mad_synth`, and its 2,304-byte PCM buffer lets real
  128-kbit/s MP3, ICY metadata, WebUI HTTP 200 and Stop coexist on the Wemos.
- Replaced the previous reset-loop development `app.bin` with the working
  MP3-only image. The combined libmad+AAC profile remains build-only because
  AAC's 16-KB word arena leaves insufficient contiguous heap for libmad.

- Added a pinned ESP8266Audio `libmad-8266` backend selected by
  `CONFIG_YORADIO_MP3_DECODER_LIBMAD`; Helix remains the production default.
- The deterministic 320-kbit/s fixture produced the same frame/sample count
  as Helix, with 49.41 dB SNR and a maximum difference of 99 PCM levels.
- Built both Helix and libmad QIO80 radio profiles and passed all 256 repository
  tests. On the physical 160-MHz Wemos D1 mini, libmad decoded the 320-kbit/s
  MP3 RAM fixture at 1.859x realtime versus 1.679x for Helix: 10.72% higher
  throughput and 9.69% lower average frame time.
- The full libmad radio image is not usable yet: allocating its 33,336-byte
  workspace before Wi-Fi makes `network_service_start()` fail and causes a
  repeatable reset loop. Helix remains the production default; the working
  QIO80 Helix image was restored after the test.
- Archived the experimental application and recovery binaries under
  [`development/esp8266-native-libmad/`](development/esp8266-native-libmad/).

### ESP8266 native persistent WebUI server

- Changed static WebUI delivery to standard HTTP/1.1 persistence: every
  response is explicitly framed and the browser reuses one keep-alive
  connection instead of reopening TCP for each asset.
- Serialized the ESP8266-only asset loader while retaining the common YoRadio
  HTML, JavaScript and CSS sources used by the other firmware targets.
- Increased the bounded server capacity to four active Web sessions and a
  three-connection listen backlog, with short idle expiry and LRU recovery.
- Backported the standard WebSocket connection-state query and stopped stale,
  reused file descriptors from closing an unrelated HTTP request.
- Flashed the QIO 80 MHz image on the physical Wemos D1 mini. With WebSocket
  open, nine page resources reused one HTTP socket; live playlist-row Play,
  Stop, Toggle, Next and Previous scenarios passed, along with 42 focused
  regressions.
- Replaced the checked development application and recorded its exact hash in
  [`development/esp8266-native-qio80/`](development/esp8266-native-qio80/).

### ESP8266 native QIO 80 MHz experiment

- Added a separate `sdkconfig.qio80.defaults` profile while retaining QIO
  40 MHz as the normal default.
- Identified the physical 4 MiB flash by JEDEC ID `5E:4016` as a Zbit
  ZB25VQ32B, whose Quad I/O read specification covers 80 MHz at 3.3 V.
- Flashed a physical Wemos D1 mini without erasing NVS or SPIFFS and verified
  two starts, Wi-Fi, WebUI/API access and repeated playlist reads.
- Archived the checked binaries and hashes in
  [`development/esp8266-native-qio80/`](development/esp8266-native-qio80/).

## Development — 2026-08-31

### ESP8266 native WebUI station selection

- Fixed clicks on the full station row and verified that the emitted `play=N`
  command selects and starts the requested station on a physical Wemos D1 mini.
- Kept the repository playlist shared, but made the ESP8266 index and WebUI list
  contain only its supported plain-HTTP MP3/AAC streams: 511 entries, no HTTPS
  and no Ogg/Opus/FLAC/HLS/WAV entries.
- Embedded the current shared `script.js.gz` in application flash, so this WebUI
  fix is delivered without overwriting SPIFFS, `wifi.csv` or the stored playlist.
- Built and flashed source revision `3acd51d`; all 243 regression tests and the
  live Play/Stop/Next/Previous/playlist-click scenarios passed. The checked
  artifact and SHA-256 manifest are in
  [`development/esp8266-native/`](development/esp8266-native/).
### ESP8266 native HTTP stack stabilization

- Corrected HTTP authority, redirect and chunked-transfer parsing for the
  low-memory radio client and added native protocol tests.
- Made ESP HTTP Server writes bounded and nonblocking, explicitly closed short
  static/API sessions and capped TCP PCB allocation to prevent heap exhaustion.
- Fixed mobile WebUI startup by excluding cache-busting query parameters from
  static SPIFFS filenames; all versioned page resources now return HTTP 200.
- Flashed and tested the physical Wemos D1 mini: 12 concurrent requests, three
  53,808-byte playlist transfers, follow-up HTTP and ping all succeeded.
- Played a real HTTP AAC stream on a non-default port and verified WebSocket
  Play/Pause/Next/Previous/Stop synchronization.
- Built source revision `ceb6440`; all 240 regression tests passed. The checked
  artifact and SHA-256 manifest are in
  [`development/esp8266-native/`](development/esp8266-native/).

## Development — 2026-08-30

### ESP8266 native asynchronous WebUI image

- Backported the standard ESP HTTP Server asynchronous request API and moved
  SPIFFS/static WebUI responses to one low-memory worker.
- Kept the primary HTTP task available for WebSocket and status traffic while
  static files are being read and transmitted.
- Protected asynchronous sockets from receive polling and LRU eviction until
  their worker completes the request.
- Built source revision `eed1ac0` with `-O3` and archived the application at
  [`development/esp8266-native/`](development/esp8266-native/).
- Flashed a physical ESP8266EX and concurrently loaded the WebUI shell, six
  compressed assets and the 53,808-byte playlist. Every request returned 200,
  while the same WebSocket delivered 46 ping replies.
- Confirmed 36,032 bytes of free heap after DHCP with no reset, stack fault or
  allocation error; all 218 repository tests passed.
## Development — 2026-08-29

### Native ESP-IDF ESP32-C3 OLED production and development images

- Merged `codex/esp32c3-overclock-profile` through source revision `eef49d1`.
- Rebuilt and archived separate production and development artifact sets. Each
  set includes an OTA/WebUI `app.bin`, a 4 MiB recovery `full.bin`, bootloader,
  partition table, initial OTA selector and a SHA-256 manifest:
  - [`development/esp32c3-oled-native-production/`](development/esp32c3-oled-native-production/)
  - [`development/esp32c3-oled-native-development/`](development/esp32c3-oled-native-development/)
- The production application leaves 31% of the smallest app partition free;
  the development application with diagnostic logging leaves 24% free.
- Recovery images deliberately exclude user SPIFFS content. Flashing
  `full.bin` at `0x0` erases the complete flash; normal OTA updates use
  `app.bin` and preserve settings.
- Fixed SNTP server-name lifetime: lwIP now receives pointers backed by
  persistent storage rather than a deleted startup task stack.
- Moved reconnect-triggered SNTP control and synchronization reporting to a
  FreeRTOS task at priority 1. The lwIP callback only posts a constant-time
  task notification.
- Confirmed an SNTP response on a physical ESP32-C3 at 8.237 seconds while a
  320 kbit/s MP3 stream was already decoding, with no underrun, reconnect or
  audio interruption.
- Exercised MP3, AAC and Ogg streams near 320 kbit/s. Decoder load remained
  about 25–28% for MP3, 21% for AAC and 33–34% for Ogg, leaving at least a
  roughly 3x real-time decoding margin.
- Verified Wi-Fi client mode, HTTPS certificate validation, WebUI status,
  SSD1306 initialization, stereo PDM output, playlist restoration and 55 host
  regression tests.
- Recorded the exact build identity, flash offsets, sizes and SHA-256 values in
  the accompanying manifests for both profiles.

## 0.9.724 — 2026-08-16

### ESP32-C3 0.42-inch OLED target

- Added an opt-in profile for the 01Space-style ESP32-C3 board with the
  onboard 72x40 SSD1306 OLED.
- Added a native 72x40 display driver with the panel-specific initialization
  sequence and 28-column controller offset instead of treating it as a
  cropped 128x64 display.
- Added a compact player, playlist and access-point layout for the 72x40
  visible area.
- Configured the onboard OLED on GPIO5/GPIO6 and the BOOT button on GPIO9.
- Adapted all explicitly pinned work to the ESP32-C3's single core.
- Configured external I2S audio on GPIO1 (BCLK), GPIO3 (LRC/WS) and GPIO10
  (DIN); ESP32-C3 has no internal analogue DAC.
- Added a reproducible build script and regression tests for the board
  profile, task placement, audio wiring and OLED geometry.

## 0.9.723 — 2026-08-16

### DAC startup

- Deferred installation and routing of the internal DAC until Arduino `setup()`
  is running, avoiding peripheral writes from the global audio constructor.
- Started the zero-filled I2S DMA path at DAC code 0 and ramped the analogue
  bias to its code-128 midpoint over 100 ms before any media can play.
- Kept midpoint samples queued before and after the first decoded frame changes
  the I2S sample rate.
- Preserved midpoint silence while stopped, connecting, buffering or recovering
  from a decoder error; the existing 100 ms media fade-in/fade-out remains in
  place above this hardware-bias sequence.
- Added regression tests for initialization order, ramp endpoints, clock-change
  protection and unsigned DAC silence.

## 0.9.722 — 2026-08-16

### Runtime scheduling

- Moved stream decoding, normalization and PCM output into a dedicated
  `AudioTask` on core 1 at priority 2.
- Kept AsyncTCP/WebUI and display work on core 0, leaving the lower-priority
  Arduino loop on core 1 for controls, OTA and service work.
- Added periodic audio-task timing and stack high-water telemetry when Audio
  Info is enabled.
- Reserved the audio-task stack statically so task creation cannot fragment the
  runtime heap used by network and codec buffers.
- Reused the dedicated audio task for bounded host connections, eliminating the
  transient 6 KiB connection-task allocation and its low-memory failure mode.
- Sized the unified static audio/connection stack to 8 KiB, preserving TLS
  stack headroom while using less peak RAM than the previous two-task path.
- Routed cross-core audio diagnostics through a static non-blocking queue so
  only the service loop writes Telnet sockets, preventing TCP-state races and
  keeping network writes out of the audio hot path.
- Raised web-stream startup prebuffering from 80% to 95% after hardware tests
  detected a near-empty buffer during the first second of MP3 playback.

## 0.9.721 — 2026-08-16

Initial archived build for the ESP32-2432S028 CYD2USB board.

### Audio

- Added internal DAC and I2S PDM/sigma-delta output support.
- Added selectable Helix/minimp3 decoding and made minimp3 the default.
- Added a shared codec arena and decoder cleanup to reduce heap fragmentation.
- Added 100 ms fade-out/fade-in when changing sources.
- Kept the internal DAC at its zero midpoint during stream gaps.
- Added adaptive normalization with configurable maximum boost, target dBFS
  and time constant.
- Optimized normalization with Q12 and a 32-bit soft limiter.
- Added 80% startup prebuffering and a 14-block default input buffer.
- Added independent adaptive left/right VU meters.

### Network and memory

- Added saved Wi-Fi retry attempts before access-point fallback.
- Reduced TLS transmit memory while retaining a 16 KiB receive buffer.
- Fixed decoder and TLS cleanup when changing stations.

### Display and WebUI

- Added Cyrillic and common UTF-8 character normalization.
- Increased display SPI frequency to 80 MHz.
- Added normalization and MP3 decoder controls to WebUI.
- Added content-derived WebUI cache revisions.
- Added confirmations and tests for destructive SPIFFS/settings operations.

### Board integration

- Added touch-to-reconnect from access-point mode.
- Preserved NVS and SPIFFS during normal firmware flashing.
