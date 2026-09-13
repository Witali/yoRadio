# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/quant_bands.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"quant_bands.c"
# GNU C99 (crosstool-NG esp-2020r3-49-gd5524c1) version 8.4.0 (xtensa-lx106-elf)
#	compiled by GNU C version 6.3.0 20170516, GMP version 6.1.2, MPFR version 4.0.1, MPC version 1.1.0, isl version isl-0.19-GMP

# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed:
# -I C:/Work/yoRadio/.build/esp8266-opus-baseline6144-raw192/config
# -I @OPUS@/.
# -I @OPUS@/upstream/include
# -I @OPUS@/upstream/celt
# -I @OPUS@/upstream/silk
# -I @OPUS@/upstream/silk/fixed
# -I @OPUS@/upstream/src
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/newlib/platform_include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/include/freertos
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/include/freertos/private
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/port/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/port/esp8266/include/freertos
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/heap/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/heap/port/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/log/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/include/apps
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/include/apps/sntp
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/lwip/src/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/port/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/port/esp8266/include/arch
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp8266/include/driver
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp_common/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp_event/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/tcpip_adapter/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/vfs/include
# -iprefix c:\work\yoradio\.build\esp8266-tools\tools\xtensa-lx106-elf\esp-2020r3-49-gd5524c1-8.4.0\xtensa-lx106-elf\bin\../lib/gcc/xtensa-lx106-elf/8.4.0/
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\quant_bands.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\quant_bands.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\quant_bands.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\quant_bands.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\quant_bands.c.s.raw
# -g0 -Os -O3 -Wno-frame-address -Wall -Werror=all
# -Wno-error=unused-function -Wno-error=unused-but-set-variable
# -Wno-error=unused-variable -Wno-error=deprecated-declarations -Wextra
# -Wno-unused-parameter -Wno-sign-compare -Wno-old-style-declaration
# -std=gnu99 -ffunction-sections -fdata-sections
# -fstrict-volatile-bitfields -fwrapv -fverbose-asm
# options enabled:  -faggressive-loop-optimizations -falign-functions
# -falign-jumps -falign-labels -falign-loops -fauto-inc-dec
# -fbranch-count-reg -fcaller-saves -fchkp-check-incomplete-type
# -fchkp-check-read -fchkp-check-write -fchkp-instrument-calls
# -fchkp-narrow-bounds -fchkp-optimize -fchkp-store-bounds
# -fchkp-use-static-bounds -fchkp-use-static-const-bounds
# -fchkp-use-wrappers -fcode-hoisting -fcombine-stack-adjustments -fcommon
# -fcompare-elim -fcprop-registers -fcrossjumping -fcse-follow-jumps
# -fdata-sections -fdefer-pop -fdelete-null-pointer-checks -fdevirtualize
# -fdevirtualize-speculatively -fearly-inlining
# -feliminate-unused-debug-types -fexpensive-optimizations
# -fforward-propagate -ffp-int-builtin-inexact -ffunction-cse
# -ffunction-sections -fgcse -fgcse-after-reload -fgcse-lm -fgnu-runtime
# -fgnu-unique -fguess-branch-probability -fhoist-adjacent-loads -fident
# -fif-conversion -fif-conversion2 -findirect-inlining -finline
# -finline-atomics -finline-functions -finline-functions-called-once
# -finline-small-functions -fipa-bit-cp -fipa-cp -fipa-cp-clone -fipa-icf
# -fipa-icf-functions -fipa-icf-variables -fipa-profile -fipa-pure-const
# -fipa-ra -fipa-reference -fipa-sra -fipa-vrp -fira-hoist-pressure
# -fira-share-save-slots -fira-share-spill-slots
# -fisolate-erroneous-paths-dereference -fivopts -fkeep-static-consts
# -fleading-underscore -flifetime-dse -floop-interchange
# -floop-unroll-and-jam -flra-remat -flto-odr-type-merging -fmath-errno
# -fmerge-constants -fmerge-debug-strings -fmove-loop-invariants
# -fomit-frame-pointer -foptimize-sibling-calls -foptimize-strlen
# -fpartial-inlining -fpeel-loops -fpeephole -fpeephole2 -fplt
# -fpredictive-commoning -fprefetch-loop-arrays -freg-struct-return
# -freorder-functions -frerun-cse-after-loop
# -fsched-critical-path-heuristic -fsched-dep-count-heuristic
# -fsched-group-heuristic -fsched-interblock -fsched-last-insn-heuristic
# -fsched-rank-heuristic -fsched-spec -fsched-spec-insn-heuristic
# -fsched-stalled-insns-dep -fschedule-fusion -fschedule-insns
# -fschedule-insns2 -fsemantic-interposition -fshow-column -fshrink-wrap
# -fshrink-wrap-separate -fsigned-zeros -fsplit-ivs-in-unroller
# -fsplit-loops -fsplit-paths -fsplit-wide-types -fssa-backprop
# -fssa-phiopt -fstdarg-opt -fstore-merging -fstrict-aliasing
# -fstrict-volatile-bitfields -fsync-libcalls -fthread-jumps
# -ftoplevel-reorder -ftrapping-math -ftree-bit-ccp -ftree-builtin-call-dce
# -ftree-ccp -ftree-ch -ftree-coalesce-vars -ftree-copy-prop -ftree-cselim
# -ftree-dce -ftree-dominator-opts -ftree-dse -ftree-forwprop -ftree-fre
# -ftree-loop-distribute-patterns -ftree-loop-distribution
# -ftree-loop-if-convert -ftree-loop-im -ftree-loop-ivcanon
# -ftree-loop-optimize -ftree-loop-vectorize -ftree-parallelize-loops=
# -ftree-partial-pre -ftree-phiprop -ftree-pre -ftree-pta -ftree-reassoc
# -ftree-scev-cprop -ftree-sink -ftree-slp-vectorize -ftree-slsr -ftree-sra
# -ftree-switch-conversion -ftree-tail-merge -ftree-ter -ftree-vrp
# -funit-at-a-time -funswitch-loops -fverbose-asm -fwrapv
# -fzero-initialized-in-bss -mserialize-volatile

	.text
	.section	.text.quant_coarse_energy_impl,"ax",@progbits
	.literal_position
	.literal .LC0, 4915
	.literal .LC1, -28672
	.literal .LC2, -131072
	.literal .LC3, beta_coef
	.literal .LC4, pred_coef
	.literal .LC5, -9216
	.literal .LC6, 65536
	.literal .LC8, small_energy_icdf
	.literal .LC9, -3670016
	.align	4
	.type	quant_coarse_energy_impl, @function
# Function: quant_coarse_energy_impl
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return MIN32(200,SHR32(dist,2*DB_SHIFT-6));
# C context: }
# C context:
# C context: static int quant_coarse_energy_impl(const CELTMode *m, int start, int end,
# C context: const opus_val16 *eBands, opus_val16 *oldEBands,
# C context: opus_int32 budget, opus_int32 tell,
# C context: const unsigned char *prob_model, opus_val16 *error, ec_enc *enc,
# C context: int C, int LM, int intra, opus_val16 max_decay, int lfe)
quant_coarse_energy_impl:
	movi	a9, 0x90	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\celt\quant_bands.c:164:    opus_val32 prev[2] = {0,0};
	movi.n	a8, 0	# tmp201,
	s32i.n	a8, sp, 0	# prev, tmp201
	s32i.n	a8, sp, 4	# prev, tmp201
# @OPUS@\upstream\celt\quant_bands.c:161: {
	s32i.n	a6, sp, 24	# %sfp, oldEBands
# @OPUS@\upstream\celt\quant_bands.c:168:    if (tell+3 <= budget)
	l32i	a8, sp, 144	# tell, tell
# @OPUS@\upstream\celt\quant_bands.c:161: {
	l16si	a6, sp, 172	# max_decay,
	s32i	a12, sp, 136	#,
	s32i	a13, sp, 132	#,
	s32i	a0, sp, 140	#,
	s32i	a14, sp, 128	#,
	s32i	a15, sp, 124	#,
# @OPUS@\upstream\celt\quant_bands.c:168:    if (tell+3 <= budget)
	addi.n	a8, a8, 3	# tmp203, tell,
# @OPUS@\upstream\celt\quant_bands.c:161: {
	s32i.n	a2, sp, 56	# %sfp, m
	s32i	a3, sp, 68	# %sfp, start
	s32i	a4, sp, 72	# %sfp, end
	s32i.n	a5, sp, 36	# %sfp, eBands
	s32i.n	a6, sp, 40	# %sfp,
	l32i	a13, sp, 156	# enc, enc
	l32i	a12, sp, 168	# intra, intra
# @OPUS@\upstream\celt\quant_bands.c:168:    if (tell+3 <= budget)
	blt	a7, a8, .L2	# budget, tmp203,
# @OPUS@\upstream\celt\quant_bands.c:169:       ec_enc_bit_logp(enc, intra, 3);
	movi.n	a4, 3	#,
	mov.n	a3, a12	#, intra
	mov.n	a2, a13	#, enc
	s32i	a7, sp, 92	#,
	call0	ec_enc_bit_logp		#
	l32i	a7, sp, 92	#,
.L2:
# @OPUS@\upstream\celt\quant_bands.c:170:    if (intra)
	bnez.n	a12, .L30	# intra,
# @OPUS@\upstream\celt\quant_bands.c:175:       beta = beta_coef[LM];
	l32i	a2, sp, 164	# LM, LM
	l32r	a4, .LC3	#, tmp204
# @OPUS@\upstream\celt\quant_bands.c:176:       coef = pred_coef[LM];
	l32r	a3, .LC4	#, tmp209
# @OPUS@\upstream\celt\quant_bands.c:175:       beta = beta_coef[LM];
	slli	a2, a2, 1	# tmp205, LM,
	add.n	a4, a4, a2	# tmp206, tmp204, tmp205
# @OPUS@\upstream\celt\quant_bands.c:176:       coef = pred_coef[LM];
	add.n	a2, a3, a2	# tmp211, tmp209, tmp205
# @OPUS@\upstream\celt\quant_bands.c:175:       beta = beta_coef[LM];
	l16si	a4, a4, 0	# beta_coef,
# @OPUS@\upstream\celt\quant_bands.c:176:       coef = pred_coef[LM];
	l16si	a2, a2, 0	# pred_coef,
# @OPUS@\upstream\celt\quant_bands.c:175:       beta = beta_coef[LM];
	s32i.n	a4, sp, 48	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:176:       coef = pred_coef[LM];
	s32i.n	a2, sp, 44	# %sfp,
	j	.L3		#
.L30:
# @OPUS@\upstream\celt\quant_bands.c:173:       beta = beta_intra;
	l32r	a10, .LC0	#,
# @OPUS@\upstream\celt\quant_bands.c:172:       coef = 0;
	movi.n	a6, 0	#,
# @OPUS@\upstream\celt\quant_bands.c:173:       beta = beta_intra;
	s32i.n	a10, sp, 48	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:172:       coef = 0;
	s32i.n	a6, sp, 44	# %sfp,
.L3:
# @OPUS@\upstream\celt\quant_bands.c:180:    for (i=start;i<end;i++)
	l32i	a10, sp, 68	# %sfp,
	l32i	a2, sp, 72	# %sfp,
	bge	a10, a2, .L31	#,,
	l32i	a6, sp, 160	# C,
	mov.n	a14, a10	# i,
	slli	a2, a6, 1	# tmp219,,
	add.n	a2, a2, a6	#, tmp219,
	s32i	a2, sp, 76	# %sfp,
	l32i	a2, sp, 72	# %sfp,
	l32i	a6, sp, 176	# lfe,
	sub	a3, a10, a2	# tmp221,,
	movi.n	a10, 0	#,
	movi.n	a2, 1	# tmp216,
	moveqz	a2, a10, a6	# tmp215,,
	l32i	a6, sp, 76	# %sfp,
	l32i.n	a10, sp, 56	# %sfp,
	mull	a3, a3, a6	#, tmp221,
	addi	a7, a7, 32	#, budget,
	extui	a2, a2, 0, 8	#, tmp215
	movi.n	a15, 0	# prephitmp_551,
	l32i.n	a11, a10, 8	# m_133(D)->nbEBands, prephitmp_559
	s32i.n	a7, sp, 52	# %sfp,
	s32i.n	a3, sp, 20	# %sfp,
	s32i	a2, sp, 80	# %sfp,
	mov.n	a7, a14	# i, i
	s32i.n	a15, sp, 16	# %sfp, <retval>
	mov.n	a8, a13	# enc, enc
.L28:
# @OPUS@\upstream\celt\quant_bands.c:225:          if (lfe && i>=2)
	movi.n	a2, 1	# tmp222,
	bgei	a7, 2, .L5	# i,,
	movi.n	a2, 0	# tmp222,
.L5:
# @OPUS@\upstream\celt\quant_bands.c:225:          if (lfe && i>=2)
	l32i	a10, sp, 80	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:230:             pi = 2*IMIN(i,20);
	movi.n	a3, 0x14	# tmp230,
# @OPUS@\upstream\celt\quant_bands.c:225:          if (lfe && i>=2)
	and	a2, a10, a2	#,, tmp222
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:230:             pi = 2*IMIN(i,20);
	mov.n	a2, a7	# i, i
	bge	a3, a7, .L6	# tmp230, i,
	mov.n	a2, a3	# i, tmp230
.L6:
	l32i	a10, sp, 68	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:230:             pi = 2*IMIN(i,20);
	slli	a2, a2, 1	# pi$14_49, i,
	sub	a3, a10, a7	# tmp234,, i
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i	a10, sp, 148	# prob_model,
	movi.n	a5, 1	# tmp235,
	movi.n	a6, 0	#,
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	addi.n	a4, a2, 1	# tmp231, pi$14_49,
	movnez	a6, a5, a3	#, tmp235, tmp234
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	add.n	a2, a10, a2	#,, pi$14_49
	extui	a3, a6, 0, 8	#, tmp233
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:182:       c=0;
	movi.n	a6, 0	# c,
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	mov.n	a2, a15	# prephitmp_551, prephitmp_551
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	add.n	a4, a10, a4	#,, tmp231
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	mov.n	a15, a6	# c, c
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	s32i	a4, sp, 64	# %sfp,
	s32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	mov.n	a6, a2	# prephitmp_551, prephitmp_551
.L27:
# @OPUS@\upstream\celt\quant_bands.c:191:          x = eBands[i+c*m->nbEBands];
	mull	a2, a15, a11	# tmp237, c, prephitmp_559
# @OPUS@\upstream\celt\quant_bands.c:192:          oldE = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	l32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:191:          x = eBands[i+c*m->nbEBands];
	add.n	a2, a2, a7	# tmp238, tmp237, i
# @OPUS@\upstream\celt\quant_bands.c:191:          x = eBands[i+c*m->nbEBands];
	slli	a2, a2, 1	# _666, tmp238,
# @OPUS@\upstream\celt\quant_bands.c:192:          oldE = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	l32r	a4, .LC5	#, tmp245
# @OPUS@\upstream\celt\quant_bands.c:192:          oldE = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	add.n	a9, a10, a2	# _687,, _666
# @OPUS@\upstream\celt\quant_bands.c:191:          x = eBands[i+c*m->nbEBands];
	l32i.n	a10, sp, 36	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:192:          oldE = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	l16si	a3, a9, 0	# *_8, _9
# @OPUS@\upstream\celt\quant_bands.c:192:          oldE = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	slli	a4, a4, 16	# tmp249, tmp245,
# @OPUS@\upstream\celt\quant_bands.c:191:          x = eBands[i+c*m->nbEBands];
	add.n	a5, a10, a2	# tmp239,, _666
# @OPUS@\upstream\celt\quant_bands.c:192:          oldE = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	srai	a4, a4, 16	# tmp248, tmp249,
# @OPUS@\upstream\celt\quant_bands.c:191:          x = eBands[i+c*m->nbEBands];
	l16si	a5, a5, 0	# *_7, x
# @OPUS@\upstream\celt\quant_bands.c:192:          oldE = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	mov.n	a12, a3	# oldE, _9
	bge	a3, a4, .L7	# _9, tmp248,
	l32r	a12, .LC5	#, oldE
.L7:
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	l32i.n	a10, sp, 44	# %sfp,
	movi	a4, 0x80	#,
	mul16s	a12, a12, a10	# tmp250, oldE,
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	slli	a13, a5, 7	# tmp253, x,
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	add.n	a12, a12, a4	# tmp252, tmp250,
# @OPUS@\upstream\celt\quant_bands.c:196:          qi = (f+QCONST32(.5f,DB_SHIFT+7))>>(DB_SHIFT+7);
	l32r	a10, .LC6	#,
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	srai	a12, a12, 8	# _17, tmp252,
# @OPUS@\upstream\celt\quant_bands.c:194:          f = SHL32(EXTEND32(x),7) - PSHR32(MULT16_16(coef,oldE), 8) - prev[c];
	sub	a13, a13, a6	# tmp254, tmp253, prephitmp_551
	sub	a13, a13, a12	# f, tmp254, _17
# @OPUS@\upstream\celt\quant_bands.c:196:          qi = (f+QCONST32(.5f,DB_SHIFT+7))>>(DB_SHIFT+7);
	add.n	a14, a13, a10	# tmp255, f,
# @OPUS@\upstream\celt\quant_bands.c:197:          decay_bound = EXTRACT16(MAX32(-QCONST16(28.f,DB_SHIFT),
	l32i.n	a10, sp, 40	# %sfp,
	l32r	a4, .LC1	#, iftmp$7_108
	sub	a3, a3, a10	# tmp361, _9,
# @OPUS@\upstream\celt\quant_bands.c:196:          qi = (f+QCONST32(.5f,DB_SHIFT+7))>>(DB_SHIFT+7);
	srai	a14, a14, 17	# _21, tmp255,
# @OPUS@\upstream\celt\quant_bands.c:197:          decay_bound = EXTRACT16(MAX32(-QCONST16(28.f,DB_SHIFT),
	blt	a3, a4, .L8	# tmp361, tmp10,
# @OPUS@\upstream\celt\quant_bands.c:197:          decay_bound = EXTRACT16(MAX32(-QCONST16(28.f,DB_SHIFT),
	slli	a3, a3, 16	# tmp260, tmp361,
	srai	a4, a3, 16	# iftmp$7_108, tmp260,
.L8:
# @OPUS@\upstream\celt\quant_bands.c:207:          if (qi < 0 && x < decay_bound)
	bgez	a14, .L52	# _21,
# @OPUS@\upstream\celt\quant_bands.c:207:          if (qi < 0 && x < decay_bound)
	blt	a5, a4, .L9	# x, iftmp$7_108,
	j	.L52		#
.L9:
# @OPUS@\upstream\celt\quant_bands.c:209:             qi += (int)SHR16(SUB16(decay_bound,x), DB_SHIFT);
	sub	a4, a4, a5	# tmp268, iftmp$7_108, x
# @OPUS@\upstream\celt\quant_bands.c:209:             qi += (int)SHR16(SUB16(decay_bound,x), DB_SHIFT);
	srai	a4, a4, 10	# tmp269, tmp268,
# @OPUS@\upstream\celt\quant_bands.c:209:             qi += (int)SHR16(SUB16(decay_bound,x), DB_SHIFT);
	add.n	a14, a14, a4	# _21, _21, tmp269
# @OPUS@\upstream\celt\quant_bands.c:210:             if (qi > 0)
	bgei	a14, 1, .L13	# _21,,
.L52:
# @OPUS@\upstream\celt\quant_bands.c:209:             qi += (int)SHR16(SUB16(decay_bound,x), DB_SHIFT);
	s32i.n	a14, sp, 8	# qi, _21
	j	.L12		#
.L13:
# @OPUS@\upstream\celt\quant_bands.c:211:                qi = 0;
	movi.n	a3, 0	#,
	s32i.n	a3, sp, 8	# qi,
	mov.n	a14, a3	# _21,
.L12:
# @OPUS@\upstream\celt\quant_bands.c:217:          bits_left = budget-tell-3*C*(end-i);
	l32i.n	a10, sp, 52	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a8, 28	# MEM[(unsigned int *)enc_124(D) + 28B], MEM[(unsigned int *)enc_124(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:217:          bits_left = budget-tell-3*C*(end-i);
	l32i.n	a4, a8, 20	# MEM[(int *)enc_124(D) + 20B], MEM[(int *)enc_124(D) + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a3, a3	# _176, MEM[(unsigned int *)enc_124(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:217:          bits_left = budget-tell-3*C*(end-i);
	sub	a4, a10, a4	# tmp272,, MEM[(int *)enc_124(D) + 20B]
# @OPUS@\upstream\celt\quant_bands.c:217:          bits_left = budget-tell-3*C*(end-i);
	l32i.n	a10, sp, 20	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:217:          bits_left = budget-tell-3*C*(end-i);
	sub	a4, a4, a3	# _33, tmp272, _176
# @OPUS@\upstream\celt\quant_bands.c:217:          bits_left = budget-tell-3*C*(end-i);
	add.n	a5, a4, a10	# bits_left, _33,
# @OPUS@\upstream\celt\quant_bands.c:218:          if (i!=start && bits_left < 30)
	movi.n	a3, 0x1d	# tmp276,
	blt	a3, a5, .L33	# tmp276, bits_left,
# @OPUS@\upstream\celt\quant_bands.c:218:          if (i!=start && bits_left < 30)
	l32i.n	a10, sp, 32	# %sfp,
	beqz.n	a10, .L33	#,
# @OPUS@\upstream\celt\quant_bands.c:220:             if (bits_left < 24)
	movi.n	a10, 0x17	# tmp278,
	mov.n	a3, a14	# prephitmp_719, _21
	blt	a10, a5, .L16	# tmp278, bits_left,
# @OPUS@\upstream\celt\quant_bands.c:221:                qi = IMIN(1, qi);
	blti	a14, 1, .L17	# _21,,
	movi.n	a3, 1	# prephitmp_719,
.L17:
# @OPUS@\upstream\celt\quant_bands.c:221:                qi = IMIN(1, qi);
	s32i.n	a3, sp, 8	# qi, prephitmp_719
.L16:
# @OPUS@\upstream\celt\quant_bands.c:222:             if (bits_left < 16)
	movi.n	a10, 0xf	# tmp281,
	blt	a10, a5, .L14	# tmp281, bits_left,
# @OPUS@\upstream\celt\quant_bands.c:223:                qi = IMAX(-1, qi);
	movi.n	a5, -1	# tmp282,
	movltz	a3, a5, a3	# prephitmp_719, tmp282, prephitmp_719
# @OPUS@\upstream\celt\quant_bands.c:223:                qi = IMAX(-1, qi);
	s32i.n	a3, sp, 8	# qi, prephitmp_719
	j	.L14		#
.L33:
	mov.n	a3, a14	# prephitmp_719, _21
.L14:
# @OPUS@\upstream\celt\quant_bands.c:225:          if (lfe && i>=2)
	l32i.n	a10, sp, 28	# %sfp,
	beqz.n	a10, .L18	#,
# @OPUS@\upstream\celt\quant_bands.c:226:             qi = IMIN(qi, 0);
	blti	a3, 1, .L19	# prephitmp_719,,
	movi.n	a3, 0	# prephitmp_719,
.L19:
# @OPUS@\upstream\celt\quant_bands.c:226:             qi = IMIN(qi, 0);
	s32i.n	a3, sp, 8	# qi, prephitmp_719
.L18:
# @OPUS@\upstream\celt\quant_bands.c:227:          if (budget-tell >= 15)
	movi.n	a5, 0xe	# tmp285,
	bge	a5, a4, .L20	# tmp285, _33,
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:231:             ec_laplace_encode(enc, &qi,
	addi.n	a3, sp, 8	#,,
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a5, a10, 0	# *_56, *_56
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i.n	a10, sp, 60	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:231:             ec_laplace_encode(enc, &qi,
	slli	a5, a5, 6	#, *_56,
# @OPUS@\upstream\celt\quant_bands.c:232:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a4, a10, 0	# *_50, *_50
# @OPUS@\upstream\celt\quant_bands.c:231:             ec_laplace_encode(enc, &qi,
	mov.n	a2, a8	#, enc
	slli	a4, a4, 7	#, *_50,
	s32i	a6, sp, 84	#,
	s32i	a7, sp, 92	#,
	s32i	a8, sp, 88	#,
	call0	ec_laplace_encode		#
	j	.L53		#
.L20:
# @OPUS@\upstream\celt\quant_bands.c:234:          else if(budget-tell >= 2)
	blti	a4, 2, .L22	# _33,,
# @OPUS@\upstream\celt\quant_bands.c:236:             qi = IMAX(-1, IMIN(qi, 1));
	mov.n	a9, a3	# iftmp$16_171, prephitmp_719
	blti	a3, 1, .L23	# prephitmp_719,,
	movi.n	a9, 1	# iftmp$16_171,
.L23:
	movi.n	a2, -1	# tmp304,
	movltz	a9, a2, a9	# iftmp$16_171, tmp304, iftmp$16_171
# @OPUS@\upstream\celt\quant_bands.c:237:             ec_enc_icdf(enc, 2*qi^-(qi<0), small_energy_icdf, 2);
	slli	a2, a9, 1	# tmp308, iftmp$16_171,
# @OPUS@\upstream\celt\quant_bands.c:237:             ec_enc_icdf(enc, 2*qi^-(qi<0), small_energy_icdf, 2);
	srai	a3, a3, 31	# tmp307, prephitmp_719,
# @OPUS@\upstream\celt\quant_bands.c:237:             ec_enc_icdf(enc, 2*qi^-(qi<0), small_energy_icdf, 2);
	l32r	a4, .LC8	#,
	xor	a3, a3, a2	#, tmp307, tmp308
	movi.n	a5, 2	#,
	mov.n	a2, a8	#, enc
# @OPUS@\upstream\celt\quant_bands.c:236:             qi = IMAX(-1, IMIN(qi, 1));
	s32i.n	a9, sp, 8	# qi, iftmp$16_171
# @OPUS@\upstream\celt\quant_bands.c:237:             ec_enc_icdf(enc, 2*qi^-(qi<0), small_energy_icdf, 2);
	s32i	a6, sp, 84	#,
	s32i	a7, sp, 92	#,
	s32i	a8, sp, 88	#,
	call0	ec_enc_icdf		#
	j	.L53		#
.L22:
# @OPUS@\upstream\celt\quant_bands.c:239:          else if(budget-tell >= 1)
	bnei	a4, 1, .L35	# _33,,
# @OPUS@\upstream\celt\quant_bands.c:241:             qi = IMIN(0, qi);
	mov.n	a5, a3	# _67, prephitmp_719
	blti	a3, 1, .L24	# _67,,
	movi.n	a5, 0	# _67,
.L24:
# @OPUS@\upstream\celt\quant_bands.c:242:             ec_enc_bit_logp(enc, -qi, 1);
	movi.n	a4, 1	#,
	neg	a3, a5	#, _67
	mov.n	a2, a8	#, enc
# @OPUS@\upstream\celt\quant_bands.c:241:             qi = IMIN(0, qi);
	s32i.n	a5, sp, 8	# qi, _67
# @OPUS@\upstream\celt\quant_bands.c:242:             ec_enc_bit_logp(enc, -qi, 1);
	s32i	a6, sp, 84	#,
	s32i	a7, sp, 92	#,
	s32i	a8, sp, 88	#,
	call0	ec_enc_bit_logp		#
.L53:
	l32i.n	a10, sp, 56	# %sfp,
	l32i.n	a4, sp, 8	# qi, pretmp_635
	l32i.n	a11, a10, 8	# m_133(D)->nbEBands, prephitmp_559
	slli	a3, a4, 10	# tmp324, pretmp_635,
	mull	a2, a15, a11	# tmp328, c, prephitmp_559
	l32i	a7, sp, 92	#,
	slli	a10, a3, 16	# tmp327, tmp324,
	slli	a3, a3, 8	#, tmp324,
	s32i	a3, sp, 96	# %sfp,
	add.n	a2, a2, a7	# tmp329, tmp328, i
	l32i.n	a3, sp, 24	# %sfp,
	slli	a2, a2, 1	# _666, tmp329,
	add.n	a9, a3, a2	# _687,, _666
	l32i	a3, sp, 96	# %sfp,
	srai	a10, a10, 16	# _646, tmp327,
	srai	a3, a3, 16	#,,
	slli	a5, a4, 17	# _683, pretmp_635,
	s32i	a3, sp, 96	# %sfp,
	l32i	a6, sp, 84	#,
	l32i	a8, sp, 88	#,
	j	.L21		#
.L35:
	movi.n	a4, -4	#,
	l32r	a5, .LC2	#, _683
	s32i	a4, sp, 96	# %sfp,
	movi	a10, -0x400	# _646,
	movi.n	a4, -1	# pretmp_635,
.L21:
# @OPUS@\upstream\celt\quant_bands.c:246:          error[i+c*m->nbEBands] = PSHR32(f,7) - SHL16(qi,DB_SHIFT);
	addi	a13, a13, 64	# tmp336, f,
	srai	a13, a13, 7	# tmp337, tmp336,
# @OPUS@\upstream\celt\quant_bands.c:246:          error[i+c*m->nbEBands] = PSHR32(f,7) - SHL16(qi,DB_SHIFT);
	l32i	a3, sp, 152	# error,
# @OPUS@\upstream\celt\quant_bands.c:246:          error[i+c*m->nbEBands] = PSHR32(f,7) - SHL16(qi,DB_SHIFT);
	sub	a13, a13, a10	# tmp339, tmp337, _646
# @OPUS@\upstream\celt\quant_bands.c:247:          badness += abs(qi0-qi);
	sub	a14, a14, a4	# tmp340, _21, pretmp_635
# @OPUS@\upstream\celt\quant_bands.c:247:          badness += abs(qi0-qi);
	l32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:246:          error[i+c*m->nbEBands] = PSHR32(f,7) - SHL16(qi,DB_SHIFT);
	add.n	a2, a3, a2	# tmp335,, _666
# @OPUS@\upstream\celt\quant_bands.c:247:          badness += abs(qi0-qi);
	abs	a14, a14	# tmp341, tmp340
# @OPUS@\upstream\celt\quant_bands.c:250:          tmp = PSHR32(MULT16_16(coef,oldE),8) + prev[c] + SHL32(q,7);
	add.n	a12, a12, a6	# tmp342, _17, prephitmp_551
# @OPUS@\upstream\celt\quant_bands.c:246:          error[i+c*m->nbEBands] = PSHR32(f,7) - SHL16(qi,DB_SHIFT);
	s16i	a13, a2, 0	# *_80, tmp339
# @OPUS@\upstream\celt\quant_bands.c:247:          badness += abs(qi0-qi);
	add.n	a10, a10, a14	#,, tmp341
# @OPUS@\upstream\celt\quant_bands.c:252:          tmp = MAX32(-QCONST32(28.f, DB_SHIFT+7), tmp);
	l32r	a2, .LC9	#,
# @OPUS@\upstream\celt\quant_bands.c:250:          tmp = PSHR32(MULT16_16(coef,oldE),8) + prev[c] + SHL32(q,7);
	add.n	a12, a12, a5	# tmp, tmp342, _683
# @OPUS@\upstream\celt\quant_bands.c:247:          badness += abs(qi0-qi);
	s32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:252:          tmp = MAX32(-QCONST32(28.f, DB_SHIFT+7), tmp);
	bge	a12, a2, .L25	# tmp,,
	mov.n	a12, a2	# tmp,
.L25:
# @OPUS@\upstream\celt\quant_bands.c:255:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	l32i	a2, sp, 96	# %sfp,
	l32i.n	a10, sp, 48	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:255:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	add.n	a6, a6, a5	# tmp352, prephitmp_551, _683
# @OPUS@\upstream\celt\quant_bands.c:255:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	mull	a3, a10, a2	# tmp353,,
# @OPUS@\upstream\celt\quant_bands.c:254:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	addi	a12, a12, 64	# tmp349, tmp,
	slli	a2, a15, 2	# _715, c,
# @OPUS@\upstream\celt\quant_bands.c:255:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	sub	a3, a6, a3	# tmp354, tmp352, tmp353
# @OPUS@\upstream\celt\quant_bands.c:254:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	srai	a12, a12, 7	# tmp350, tmp349,
# @OPUS@\upstream\celt\quant_bands.c:255:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	add.n	a4, sp, a2	# tmp351,, _715
# @OPUS@\upstream\celt\quant_bands.c:256:       } while (++c < C);
	l32i	a6, sp, 160	# C,
# @OPUS@\upstream\celt\quant_bands.c:254:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	s16i	a12, a9, 0	# *prephitmp_689, tmp350
# @OPUS@\upstream\celt\quant_bands.c:255:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	s32i.n	a3, a4, 0	# MEM[base: _714, offset: 0B], tmp354
# @OPUS@\upstream\celt\quant_bands.c:256:       } while (++c < C);
	addi.n	a15, a15, 1	# c, c,
	bge	a15, a6, .L26	# c,,
	l32i.n	a6, a4, 4	# MEM[base: _711, offset: 0B], prephitmp_551
	j	.L27		#
.L26:
	l32i.n	a10, sp, 20	# %sfp,
	l32i	a6, sp, 76	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:180:    for (i=start;i<end;i++)
	addi.n	a7, a7, 1	# i, i,
	add.n	a10, a10, a6	#,,
	s32i.n	a10, sp, 20	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:180:    for (i=start;i<end;i++)
	l32i	a10, sp, 72	# %sfp,
	beq	a10, a7, .L51	#, i,
	l32i.n	a15, sp, 0	# prev, prephitmp_551
	j	.L28		#
.L31:
# @OPUS@\upstream\celt\quant_bands.c:163:    int badness = 0;
	movi.n	a9, 0	# <retval>,
	j	.L4		#
.L51:
	l32i.n	a9, sp, 16	# %sfp, <retval>
.L4:
# @OPUS@\upstream\celt\quant_bands.c:258:    return lfe ? 0 : badness;
	l32i	a6, sp, 176	# lfe,
	movi.n	a2, 0	# tmp406,
	movnez	a9, a2, a6	# <retval>, tmp406,
# @OPUS@\upstream\celt\quant_bands.c:259: }
	l32i	a0, sp, 140	#,
	mov.n	a2, a9	#, <retval>
	movi	a9, 0x90	#,
	l32i	a12, sp, 136	#,
	l32i	a13, sp, 132	#,
	l32i	a14, sp, 128	#,
	l32i	a15, sp, 124	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	quant_coarse_energy_impl, .-quant_coarse_energy_impl
	.global	__udivsi3
	.section	.text.quant_coarse_energy,"ax",@progbits
	.literal_position
	.literal .LC10, 16384
	.literal .LC11, 3072
	.literal .LC12, e_prob_model
	.literal .LC13, pred_coef
	.align	4
	.global	quant_coarse_energy
	.type	quant_coarse_energy, @function
# Function: quant_coarse_energy
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return lfe ? 0 : badness;
# C context: }
# C context:
# C context: void quant_coarse_energy(const CELTMode *m, int start, int end, int effEnd,
# C context: const opus_val16 *eBands, opus_val16 *oldEBands, opus_uint32 budget,
# C context: opus_val16 *error, ec_enc *enc, int C, int LM, int nbAvailableBytes,
# C context: int force_intra, opus_val32 *delayedIntra, int two_pass, int loss_rate, int lfe)
# C context: {
quant_coarse_energy:
	movi	a9, 0x110	#,
	sub	sp, sp, a9	#,,
	s32i	a12, sp, 264	#,
	s32i	a13, sp, 260	#,
	s32i	a14, sp, 256	#,
	s32i	a15, sp, 252	#,
	mov.n	a14, a3	# start, start
	s32i	a0, sp, 268	#,
# @OPUS@\upstream\celt\quant_bands.c:265: {
	s32i	a4, sp, 196	# %sfp, end
	s32i	a2, sp, 168	# %sfp, m
	mov.n	a15, a5	# effEnd, effEnd
	s32i	a6, sp, 200	# %sfp, eBands
	s32i	a7, sp, 176	# %sfp, oldEBands
	l32i	a12, sp, 280	# enc, enc
	l32i	a13, sp, 284	# C, C
# @OPUS@\upstream\celt\quant_bands.c:275:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i	a2, sp, 144	# _saved_stack,
	l32i	a2, sp, 196	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	l32i	a8, sp, 296	# force_intra,
	sub	a2, a2, a14	#,, start
# @OPUS@\upstream\celt\quant_bands.c:275:    SAVE_STACK;
	s32i	a3, sp, 148	# _saved_stack,
	s32i	a2, sp, 164	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	beqz.n	a8, .L56	#,
	l32i	a8, sp, 300	# delayedIntra,
	l32i.n	a8, a8, 0	# *delayedIntra_91(D),
	s32i	a8, sp, 208	# %sfp,
	movi.n	a8, 1	#,
	s32i	a8, sp, 296	# force_intra,
	j	.L57		#
.L56:
	l32i	a8, sp, 300	# delayedIntra,
	l32i.n	a8, a8, 0	# *delayedIntra_91(D),
	s32i	a8, sp, 208	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	l32i	a8, sp, 304	# two_pass,
	bnez.n	a8, .L57	#,
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	mull	a3, a13, a2	# _3, C,
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	l32i	a8, sp, 208	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	slli	a4, a3, 1	# tmp181, _3,
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	movi.n	a2, 1	# tmp182,
	blt	a4, a8, .L58	# tmp181,,
	l32i	a8, sp, 304	# two_pass,
	mov.n	a2, a8	# tmp182,
.L58:
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	l32i	a5, sp, 292	# nbAvailableBytes,
	movi.n	a4, 1	# tmp184,
	blt	a3, a5, .L59	# _3,,
	movi.n	a4, 0	# tmp184,
.L59:
	and	a2, a2, a4	# tmp186, tmp182, tmp184
# @OPUS@\upstream\celt\quant_bands.c:277:    intra = force_intra || (!two_pass && *delayedIntra>2*C*(end-start) && nbAvailableBytes > (end-start)*C);
	extui	a2, a2, 0, 8	#, tmp186
	s32i	a2, sp, 296	# force_intra,
.L57:
# @OPUS@\upstream\celt\quant_bands.c:279:    new_distortion = loss_distortion(eBands, oldEBands, start, effEnd, m->nbEBands, C);
	l32i	a8, sp, 168	# %sfp,
	l32i	a3, sp, 176	# %sfp,
	l32i.n	a8, a8, 8	# m_100(D)->nbEBands,
	l32i	a4, sp, 200	# %sfp,
	s32i	a8, sp, 160	# %sfp,
	l32i	a2, sp, 160	# %sfp,
	slli	a5, a14, 1	# tmp187, start,
	slli	a8, a15, 1	# tmp188, effEnd,
	sub	a11, a14, a15	# tmp192, start, effEnd
# @OPUS@\upstream\celt\quant_bands.c:145:    opus_val32 dist = 0;
	movi.n	a7, 0	# dist,
	slli	a10, a2, 1	# _258,,
	add.n	a5, a3, a5	# ivtmp$92,, tmp187
	add.n	a8, a4, a8	# ivtmp$93,, tmp188
	slli	a11, a11, 1	# _234, tmp192,
# @OPUS@\upstream\celt\quant_bands.c:146:    c=0; do {
	mov.n	a9, a7	# c, dist
.L62:
# @OPUS@\upstream\celt\quant_bands.c:147:       for (i=start;i<end;i++)
	bge	a14, a15, .L60	# start, effEnd,
	add.n	a3, a11, a8	# ivtmp$85, _234, ivtmp$93
	mov.n	a4, a5	# ivtmp$86, ivtmp$92
.L61:
# @OPUS@\upstream\celt\quant_bands.c:149:          opus_val16 d = SUB16(SHR16(eBands[i+c*len], 3), SHR16(oldEBands[i+c*len], 3));
	l16ui	a2, a3, 0	# MEM[base: _269, offset: 0B],
	l16ui	a6, a4, 0	# MEM[base: _268, offset: 0B],
	slli	a2, a2, 16	# tmp195, MEM[base: _269, offset: 0B],
	slli	a6, a6, 16	# tmp199, MEM[base: _268, offset: 0B],
	srai	a2, a2, 19	# tmp196, tmp195,
	srai	a6, a6, 19	# tmp200, tmp199,
# @OPUS@\upstream\celt\quant_bands.c:149:          opus_val16 d = SUB16(SHR16(eBands[i+c*len], 3), SHR16(oldEBands[i+c*len], 3));
	sub	a2, a2, a6	# d, tmp196, tmp200
# @OPUS@\upstream\celt\quant_bands.c:150:          dist = MAC16_16(dist, d,d);
	mull	a2, a2, a2	# tmp205, d, d
	addi.n	a3, a3, 2	# ivtmp$85, ivtmp$85,
# @OPUS@\upstream\celt\quant_bands.c:150:          dist = MAC16_16(dist, d,d);
	add.n	a7, a7, a2	# dist, dist, tmp205
	addi.n	a4, a4, 2	# ivtmp$86, ivtmp$86,
# @OPUS@\upstream\celt\quant_bands.c:147:       for (i=start;i<end;i++)
	bne	a8, a3, .L61	# ivtmp$93, ivtmp$85,
.L60:
# @OPUS@\upstream\celt\quant_bands.c:152:    } while (++c<C);
	addi.n	a9, a9, 1	# c, c,
	add.n	a5, a5, a10	# ivtmp$92, ivtmp$92, _258
	add.n	a8, a8, a10	# ivtmp$93, ivtmp$93, _258
	blt	a9, a13, .L62	# c, C,
# @OPUS@\upstream\celt\quant_bands.c:153:    return MIN32(200,SHR32(dist,2*DB_SHIFT-6));
	srai	a7, a7, 14	#, dist,
	s32i	a7, sp, 184	# %sfp,
	movi	a2, 0xc8	# tmp210,
	bge	a2, a7, .L63	# tmp210,,
	s32i	a2, sp, 184	# %sfp, tmp210
.L63:
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, a12, 28	# MEM[(unsigned int *)enc_105(D) + 28B], MEM[(unsigned int *)enc_105(D) + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a12, 20	# MEM[(int *)enc_105(D) + 20B], MEM[(int *)enc_105(D) + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a2, a2	# _123, MEM[(unsigned int *)enc_105(D) + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a3	# _106, _123, MEM[(int *)enc_105(D) + 20B]
# @OPUS@\upstream\celt\quant_bands.c:282:    if (tell+3 > budget)
	addi	a3, a2, -29	# tmp213, _106,
# @OPUS@\upstream\celt\quant_bands.c:282:    if (tell+3 > budget)
	l32i	a8, sp, 272	# budget,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a2, a2, -32	#, _106,
	s32i	a2, sp, 204	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:282:    if (tell+3 > budget)
	bltu	a8, a3, .L76	#, tmp213,
	l32i	a6, sp, 296	# force_intra,
	l32i	a8, sp, 304	# two_pass,
	or	a6, a6, a8	#,,
	s32i	a6, sp, 188	# %sfp,
	j	.L64		#
.L76:
	movi.n	a8, 0	#,
	s32i	a8, sp, 296	# force_intra,
# @OPUS@\upstream\celt\quant_bands.c:283:       two_pass = intra = 0;
	s32i	a8, sp, 188	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:283:       two_pass = intra = 0;
	s32i	a8, sp, 304	# two_pass,
.L64:
# @OPUS@\upstream\celt\quant_bands.c:286:    if (end-start>10)
	l32i	a3, sp, 164	# %sfp,
	movi.n	a2, 0xa	# tmp214,
# @OPUS@\upstream\celt\quant_bands.c:285:    max_decay = QCONST16(16.f,DB_SHIFT);
	l32r	a15, .LC10	#, max_decay
# @OPUS@\upstream\celt\quant_bands.c:286:    if (end-start>10)
	bge	a2, a3, .L65	# tmp214,,
# @OPUS@\upstream\celt\quant_bands.c:289:       max_decay = MIN32(max_decay, SHL32(EXTEND32(nbAvailableBytes),DB_SHIFT-3));
	l32i	a4, sp, 292	# nbAvailableBytes,
	slli	a2, a4, 7	# tmp215,,
	bge	a15, a2, .L66	# max_decay, tmp215,
	mov.n	a2, a15	# tmp215, max_decay
.L66:
# @OPUS@\upstream\celt\quant_bands.c:289:       max_decay = MIN32(max_decay, SHL32(EXTEND32(nbAvailableBytes),DB_SHIFT-3));
	slli	a2, a2, 16	# tmp221, tmp215,
	srai	a15, a2, 16	# max_decay, tmp221,
.L65:
# @OPUS@\upstream\celt\quant_bands.c:296:    enc_start_state = *enc;
	l32i.n	a5, a12, 4	# *enc_105(D), *enc_105(D)
	l32i.n	a8, a12, 24	# *enc_105(D),
# @OPUS@\upstream\celt\quant_bands.c:294:    if (lfe)
	l32r	a7, .LC11	#, tmp357
# @OPUS@\upstream\celt\quant_bands.c:296:    enc_start_state = *enc;
	s32i	a8, sp, 164	# %sfp,
	s32i	a5, sp, 100	# enc_start_state, *enc_105(D)
# @OPUS@\upstream\celt\quant_bands.c:294:    if (lfe)
	l32i	a8, sp, 312	# lfe,
# @OPUS@\upstream\celt\quant_bands.c:296:    enc_start_state = *enc;
	l32i.n	a5, a12, 20	# *enc_105(D),
	l32i.n	a6, a12, 0	# *enc_105(D), *enc_105(D)
# @OPUS@\upstream\celt\quant_bands.c:298:    ALLOC(oldEBands_intra, C*m->nbEBands, opus_val16);
	l32i	a3, sp, 160	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:294:    if (lfe)
	movnez	a15, a7, a8	# max_decay, tmp357,
# @OPUS@\upstream\celt\quant_bands.c:296:    enc_start_state = *enc;
	s32i	a5, sp, 116	# enc_start_state,
	l32i	a8, sp, 164	# %sfp,
	l32i.n	a5, a12, 28	# *enc_105(D),
	l32i.n	a9, a12, 8	# *enc_105(D), *enc_105(D)
	l32i.n	a10, a12, 12	# *enc_105(D), *enc_105(D)
	l32i.n	a11, a12, 16	# *enc_105(D), *enc_105(D)
	l32i.n	a7, a12, 36	# *enc_105(D),
# @OPUS@\upstream\celt\quant_bands.c:298:    ALLOC(oldEBands_intra, C*m->nbEBands, opus_val16);
	mull	a2, a3, a13	#,, C
# @OPUS@\upstream\celt\quant_bands.c:296:    enc_start_state = *enc;
	s32i	a6, sp, 96	# enc_start_state, *enc_105(D)
	s32i	a8, sp, 120	# enc_start_state,
	l32i.n	a6, a12, 32	# *enc_105(D),
	l32i.n	a8, a12, 40	# *enc_105(D),
	s32i	a5, sp, 124	# enc_start_state,
	l32i.n	a5, a12, 44	# *enc_105(D),
# @OPUS@\upstream\celt\quant_bands.c:298:    ALLOC(oldEBands_intra, C*m->nbEBands, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
# @OPUS@\upstream\celt\quant_bands.c:296:    enc_start_state = *enc;
	s32i	a9, sp, 104	# enc_start_state, *enc_105(D)
	s32i	a6, sp, 128	# enc_start_state,
	s32i	a10, sp, 108	# enc_start_state, *enc_105(D)
	s32i	a11, sp, 112	# enc_start_state, *enc_105(D)
	s32i	a7, sp, 132	# enc_start_state,
	s32i	a5, sp, 140	# enc_start_state,
	s32i	a8, sp, 136	# enc_start_state,
# @OPUS@\upstream\celt\quant_bands.c:298:    ALLOC(oldEBands_intra, C*m->nbEBands, opus_val16);
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\quant_bands.c:299:    ALLOC(error_intra, C*m->nbEBands, opus_val16);
	l32i	a8, sp, 168	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:298:    ALLOC(oldEBands_intra, C*m->nbEBands, opus_val16);
	s32i	a2, sp, 160	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:299:    ALLOC(error_intra, C*m->nbEBands, opus_val16);
	l32i.n	a2, a8, 8	# m_100(D)->nbEBands, m_100(D)->nbEBands
	movi.n	a4, 0	#,
	mull	a2, a13, a2	#, C, m_100(D)->nbEBands
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\quant_bands.c:300:    OPUS_COPY(oldEBands_intra, oldEBands, C*m->nbEBands);
	l32i	a8, sp, 168	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:299:    ALLOC(error_intra, C*m->nbEBands, opus_val16);
	s32i	a2, sp, 180	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:300:    OPUS_COPY(oldEBands_intra, oldEBands, C*m->nbEBands);
	l32i.n	a4, a8, 8	# m_100(D)->nbEBands, m_100(D)->nbEBands
	l32i	a8, sp, 288	# LM,
	l32i	a3, sp, 176	# %sfp,
	l32i	a2, sp, 160	# %sfp,
	mull	a4, a13, a4	#, C, m_100(D)->nbEBands
	slli	a8, a8, 1	#,,
	movi.n	a5, 2	#,
	s32i	a8, sp, 172	# %sfp,
	call0	yoradio_opus_copy		#
	l32i	a8, sp, 172	# %sfp,
	l32i	a3, sp, 288	# LM,
# @OPUS@\upstream\celt\quant_bands.c:302:    if (two_pass || intra)
	l32i	a6, sp, 188	# %sfp,
	add.n	a2, a8, a3	# tmp242,,
	slli	a9, a2, 3	# tmp243, tmp242,
	sub	a9, a9, a2	# tmp244, tmp243, tmp242
	slli	a9, a9, 2	# tmp245, tmp244,
	beqz.n	a6, .L68	#,
# @OPUS@\upstream\celt\quant_bands.c:304:       badness1 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands_intra, budget,
	l32i	a8, sp, 312	# lfe,
# @OPUS@\upstream\celt\quant_bands.c:305:             tell, e_prob_model[LM][1], error_intra, enc, C, LM, 1, max_decay, lfe);
	l32r	a7, .LC12	#,
# @OPUS@\upstream\celt\quant_bands.c:304:       badness1 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands_intra, budget,
	s32i.n	a8, sp, 32	#,
	l32i	a8, sp, 288	# LM,
# @OPUS@\upstream\celt\quant_bands.c:305:             tell, e_prob_model[LM][1], error_intra, enc, C, LM, 1, max_decay, lfe);
	addi	a2, a9, 42	# tmp247, tmp245,
# @OPUS@\upstream\celt\quant_bands.c:304:       badness1 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands_intra, budget,
	s32i.n	a8, sp, 20	#,
	l32i	a8, sp, 180	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:305:             tell, e_prob_model[LM][1], error_intra, enc, C, LM, 1, max_decay, lfe);
	add.n	a2, a2, a7	# tmp248, tmp247,
# @OPUS@\upstream\celt\quant_bands.c:304:       badness1 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands_intra, budget,
	s32i.n	a8, sp, 8	#,
	l32i	a8, sp, 204	# %sfp,
	movi.n	a3, 1	#,
	s32i.n	a2, sp, 4	#, tmp248
	l32i	a7, sp, 272	# budget,
	l32i	a6, sp, 160	# %sfp,
	l32i	a5, sp, 200	# %sfp,
	l32i	a4, sp, 196	# %sfp,
	l32i	a2, sp, 168	# %sfp,
	s32i.n	a3, sp, 24	#,
	s32i.n	a8, sp, 0	#,
	s32i.n	a15, sp, 28	#, max_decay
	s32i.n	a13, sp, 16	#, C
	s32i.n	a12, sp, 12	#, enc
	mov.n	a3, a14	#, start
	s32i	a9, sp, 224	#,
	call0	quant_coarse_energy_impl		#
# @OPUS@\upstream\celt\quant_bands.c:308:    if (!intra)
	l32i	a8, sp, 296	# force_intra,
# @OPUS@\upstream\celt\quant_bands.c:304:       badness1 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands_intra, budget,
	mov.n	a10, a2	# badness1,
# @OPUS@\upstream\celt\quant_bands.c:308:    if (!intra)
	bnez.n	a8, .L69	#,
# @OPUS@\upstream\celt\quant_bands.c:319:       tell_intra = ec_tell_frac(enc);
	mov.n	a2, a12	#, enc
	s32i	a10, sp, 216	#,
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\quant_bands.c:321:       enc_intra_state = *enc;
	l32i.n	a6, a12, 0	# *enc_105(D), *enc_105(D)
	l32i.n	a7, a12, 4	# *enc_105(D), *enc_105(D)
# @OPUS@\upstream\celt\quant_bands.c:325:       intra_buf = ec_get_buffer(&enc_intra_state) + nstart_bytes;
	l32i	a3, sp, 164	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:321:       enc_intra_state = *enc;
	s32i.n	a6, sp, 48	# enc_intra_state, *enc_105(D)
# @OPUS@\upstream\celt\quant_bands.c:325:       intra_buf = ec_get_buffer(&enc_intra_state) + nstart_bytes;
	add.n	a3, a6, a3	#, *enc_105(D),
# @OPUS@\upstream\celt\quant_bands.c:321:       enc_intra_state = *enc;
	s32i.n	a7, sp, 52	# enc_intra_state, *enc_105(D)
	l32i.n	a6, a12, 12	# *enc_105(D),
	l32i.n	a7, a12, 16	# *enc_105(D),
	l32i.n	a5, a12, 24	# *enc_105(D), *enc_105(D)
# @OPUS@\upstream\celt\quant_bands.c:319:       tell_intra = ec_tell_frac(enc);
	s32i	a2, sp, 212	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:321:       enc_intra_state = *enc;
	s32i.n	a6, sp, 60	# enc_intra_state,
# @OPUS@\upstream\celt\quant_bands.c:326:       save_bytes = nintra_bytes-nstart_bytes;
	l32i	a2, sp, 164	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:321:       enc_intra_state = *enc;
	l32i.n	a6, a12, 20	# *enc_105(D),
	s32i	a7, sp, 64	# enc_intra_state,
	l32i.n	a7, a12, 28	# *enc_105(D),
	l32i.n	a11, a12, 8	# *enc_105(D), *enc_105(D)
	l32i.n	a8, a12, 44	# *enc_105(D), *enc_105(D)
# @OPUS@\upstream\celt\quant_bands.c:326:       save_bytes = nintra_bytes-nstart_bytes;
	sub	a2, a5, a2	#, *enc_105(D),
# @OPUS@\upstream\celt\quant_bands.c:329:       ALLOC(intra_bits, save_bytes, unsigned char);
	l32i	a4, sp, 296	# force_intra,
# @OPUS@\upstream\celt\quant_bands.c:321:       enc_intra_state = *enc;
	s32i	a6, sp, 68	# enc_intra_state,
	s32i	a5, sp, 72	# enc_intra_state, *enc_105(D)
	l32i.n	a6, a12, 36	# *enc_105(D),
	l32i.n	a5, a12, 32	# *enc_105(D),
	s32i	a7, sp, 76	# enc_intra_state,
	l32i.n	a7, a12, 40	# *enc_105(D),
# @OPUS@\upstream\celt\quant_bands.c:325:       intra_buf = ec_get_buffer(&enc_intra_state) + nstart_bytes;
	s32i	a3, sp, 164	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:329:       ALLOC(intra_bits, save_bytes, unsigned char);
	movi.n	a3, 1	#,
# @OPUS@\upstream\celt\quant_bands.c:321:       enc_intra_state = *enc;
	s32i.n	a11, sp, 56	# enc_intra_state, *enc_105(D)
	s32i	a6, sp, 84	# enc_intra_state,
	s32i	a7, sp, 88	# enc_intra_state,
	s32i	a8, sp, 92	# enc_intra_state, *enc_105(D)
	s32i	a5, sp, 80	# enc_intra_state,
# @OPUS@\upstream\celt\quant_bands.c:326:       save_bytes = nintra_bytes-nstart_bytes;
	s32i	a2, sp, 188	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:329:       ALLOC(intra_bits, save_bytes, unsigned char);
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\quant_bands.c:331:       OPUS_COPY(intra_bits, intra_buf, nintra_bytes - nstart_bytes);
	l32i	a4, sp, 188	# %sfp,
	l32i	a3, sp, 164	# %sfp,
	movi.n	a5, 1	#,
# @OPUS@\upstream\celt\quant_bands.c:329:       ALLOC(intra_bits, save_bytes, unsigned char);
	s32i	a2, sp, 192	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:331:       OPUS_COPY(intra_bits, intra_buf, nintra_bytes - nstart_bytes);
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\quant_bands.c:333:       *enc = enc_start_state;
	l32i	a8, sp, 124	# enc_start_state,
# @OPUS@\upstream\celt\quant_bands.c:336:             tell, e_prob_model[LM][intra], error, enc, C, LM, 0, max_decay, lfe);
	l32i	a9, sp, 224	#,
# @OPUS@\upstream\celt\quant_bands.c:333:       *enc = enc_start_state;
	s32i.n	a8, a12, 28	# *enc_105(D),
	l32i	a8, sp, 128	# enc_start_state,
	l32i	a6, sp, 96	# enc_start_state, enc_start_state
	s32i.n	a8, a12, 32	# *enc_105(D),
	l32i	a8, sp, 132	# enc_start_state,
	l32i	a5, sp, 100	# enc_start_state, enc_start_state
	s32i.n	a8, a12, 36	# *enc_105(D),
	l32i	a8, sp, 136	# enc_start_state,
	l32i	a4, sp, 104	# enc_start_state, enc_start_state
	s32i.n	a8, a12, 40	# *enc_105(D),
	l32i	a8, sp, 140	# enc_start_state,
	l32i	a3, sp, 108	# enc_start_state, enc_start_state
	s32i.n	a8, a12, 44	# *enc_105(D),
# @OPUS@\upstream\celt\quant_bands.c:336:             tell, e_prob_model[LM][intra], error, enc, C, LM, 0, max_decay, lfe);
	l32r	a8, .LC12	#,
# @OPUS@\upstream\celt\quant_bands.c:333:       *enc = enc_start_state;
	l32i	a2, sp, 112	# enc_start_state, enc_start_state
	l32i	a7, sp, 116	# enc_start_state, enc_start_state
	l32i	a11, sp, 120	# enc_start_state, enc_start_state
# @OPUS@\upstream\celt\quant_bands.c:336:             tell, e_prob_model[LM][intra], error, enc, C, LM, 0, max_decay, lfe);
	add.n	a9, a9, a8	# tmp278, tmp245,
# @OPUS@\upstream\celt\quant_bands.c:335:       badness2 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands, budget,
	l32i	a8, sp, 312	# lfe,
# @OPUS@\upstream\celt\quant_bands.c:333:       *enc = enc_start_state;
	s32i.n	a6, a12, 0	# *enc_105(D), enc_start_state
	s32i.n	a5, a12, 4	# *enc_105(D), enc_start_state
	s32i.n	a4, a12, 8	# *enc_105(D), enc_start_state
	s32i.n	a3, a12, 12	# *enc_105(D), enc_start_state
	s32i.n	a2, a12, 16	# *enc_105(D), enc_start_state
	s32i.n	a7, a12, 20	# *enc_105(D), enc_start_state
	s32i.n	a11, a12, 24	# *enc_105(D), enc_start_state
# @OPUS@\upstream\celt\quant_bands.c:335:       badness2 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands, budget,
	s32i.n	a8, sp, 32	#,
	l32i	a8, sp, 296	# force_intra,
	s32i.n	a9, sp, 4	#, tmp278
	s32i.n	a15, sp, 28	#, max_decay
	s32i.n	a8, sp, 24	#,
	l32i	a8, sp, 288	# LM,
	l32i	a7, sp, 272	# budget,
	s32i.n	a8, sp, 20	#,
	l32i	a8, sp, 276	# error,
	l32i	a6, sp, 176	# %sfp,
	s32i.n	a8, sp, 8	#,
	l32i	a8, sp, 204	# %sfp,
	l32i	a5, sp, 200	# %sfp,
	l32i	a4, sp, 196	# %sfp,
	l32i	a2, sp, 168	# %sfp,
	s32i.n	a8, sp, 0	#,
	s32i.n	a13, sp, 16	#, C
	s32i.n	a12, sp, 12	#, enc
	mov.n	a3, a14	#, start
	call0	quant_coarse_energy_impl		#
# @OPUS@\upstream\celt\quant_bands.c:338:       if (two_pass && (badness1 < badness2 || (badness1 == badness2 && ((opus_int32)ec_tell_frac(enc))+intra_bias > tell_intra)))
	l32i	a8, sp, 304	# two_pass,
	l32i	a10, sp, 216	#,
	beqz.n	a8, .L75	#,
# @OPUS@\upstream\celt\quant_bands.c:338:       if (two_pass && (badness1 < badness2 || (badness1 == badness2 && ((opus_int32)ec_tell_frac(enc))+intra_bias > tell_intra)))
	bge	a10, a2, .L71	# badness1, badness2,
.L73:
# @OPUS@\upstream\celt\quant_bands.c:340:          *enc = enc_intra_state;
	l32i.n	a5, sp, 48	# enc_intra_state, enc_intra_state
# @OPUS@\upstream\celt\quant_bands.c:342:          OPUS_COPY(intra_buf, intra_bits, nintra_bytes - nstart_bytes);
	l32i	a4, sp, 188	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:340:          *enc = enc_intra_state;
	s32i.n	a5, a12, 0	# *enc_105(D), enc_intra_state
	l32i.n	a5, sp, 52	# enc_intra_state, enc_intra_state
# @OPUS@\upstream\celt\quant_bands.c:342:          OPUS_COPY(intra_buf, intra_bits, nintra_bytes - nstart_bytes);
	l32i	a3, sp, 192	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:340:          *enc = enc_intra_state;
	s32i.n	a5, a12, 4	# *enc_105(D), enc_intra_state
	l32i.n	a5, sp, 56	# enc_intra_state, enc_intra_state
# @OPUS@\upstream\celt\quant_bands.c:342:          OPUS_COPY(intra_buf, intra_bits, nintra_bytes - nstart_bytes);
	l32i	a2, sp, 164	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:340:          *enc = enc_intra_state;
	s32i.n	a5, a12, 8	# *enc_105(D), enc_intra_state
	l32i.n	a5, sp, 60	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 12	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 64	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 16	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 68	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 20	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 72	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 24	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 76	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 28	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 80	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 32	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 84	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 36	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 88	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 40	# *enc_105(D), enc_intra_state
	l32i	a5, sp, 92	# enc_intra_state, enc_intra_state
	s32i.n	a5, a12, 44	# *enc_105(D), enc_intra_state
# @OPUS@\upstream\celt\quant_bands.c:342:          OPUS_COPY(intra_buf, intra_bits, nintra_bytes - nstart_bytes);
	movi.n	a5, 1	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\quant_bands.c:343:          OPUS_COPY(oldEBands, oldEBands_intra, C*m->nbEBands);
	l32i	a8, sp, 168	# %sfp,
	l32i	a3, sp, 160	# %sfp,
	l32i.n	a4, a8, 8	# m_100(D)->nbEBands, m_100(D)->nbEBands
	l32i	a2, sp, 176	# %sfp,
	mull	a4, a13, a4	#, C, m_100(D)->nbEBands
	movi.n	a5, 2	#,
	j	.L86		#
.L71:
# @OPUS@\upstream\celt\quant_bands.c:338:       if (two_pass && (badness1 < badness2 || (badness1 == badness2 && ((opus_int32)ec_tell_frac(enc))+intra_bias > tell_intra)))
	bne	a10, a2, .L75	# badness1, badness2,
# @OPUS@\upstream\celt\quant_bands.c:338:       if (two_pass && (badness1 < badness2 || (badness1 == badness2 && ((opus_int32)ec_tell_frac(enc))+intra_bias > tell_intra)))
	mov.n	a2, a12	#, enc
	call0	ec_tell_frac		#
	mov.n	a14, a2	# _41,
# @OPUS@\upstream\celt\quant_bands.c:278:    intra_bias = (opus_int32)((budget**delayedIntra*loss_rate)/(C*512));
	l32i	a8, sp, 272	# budget,
	l32i	a2, sp, 308	# loss_rate, loss_rate
# @OPUS@\upstream\celt\quant_bands.c:278:    intra_bias = (opus_int32)((budget**delayedIntra*loss_rate)/(C*512));
	slli	a3, a13, 9	#, C,
# @OPUS@\upstream\celt\quant_bands.c:278:    intra_bias = (opus_int32)((budget**delayedIntra*loss_rate)/(C*512));
	mull	a2, a2, a8	# tmp296, loss_rate,
# @OPUS@\upstream\celt\quant_bands.c:278:    intra_bias = (opus_int32)((budget**delayedIntra*loss_rate)/(C*512));
	l32i	a8, sp, 208	# %sfp,
	mull	a2, a2, a8	#, tmp296,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\quant_bands.c:338:       if (two_pass && (badness1 < badness2 || (badness1 == badness2 && ((opus_int32)ec_tell_frac(enc))+intra_bias > tell_intra)))
	l32i	a8, sp, 212	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:338:       if (two_pass && (badness1 < badness2 || (badness1 == badness2 && ((opus_int32)ec_tell_frac(enc))+intra_bias > tell_intra)))
	add.n	a2, a2, a14	# tmp303,, _41
# @OPUS@\upstream\celt\quant_bands.c:338:       if (two_pass && (badness1 < badness2 || (badness1 == badness2 && ((opus_int32)ec_tell_frac(enc))+intra_bias > tell_intra)))
	blt	a8, a2, .L73	#, tmp303,
.L75:
# @OPUS@\upstream\celt\quant_bands.c:355:       *delayedIntra = ADD32(MULT16_32_Q15(MULT16_16_Q15(pred_coef[LM], pred_coef[LM]),*delayedIntra),
	l32i	a8, sp, 300	# delayedIntra,
	l32r	a2, .LC13	#, tmp304
	l32i.n	a3, a8, 0	# *delayedIntra_91(D), _62
	l32i	a8, sp, 172	# %sfp,
	srai	a7, a3, 16	# tmp312, _62,
	add.n	a2, a2, a8	# tmp306, tmp304,
	l16si	a2, a2, 0	# pred_coef, _56
	extui	a3, a3, 0, 16	# tmp315, _62,
	mull	a2, a2, a2	# tmp309, _56, _56
	l32i	a8, sp, 184	# %sfp,
	slli	a2, a2, 1	# tmp311, tmp309,
	srai	a2, a2, 16	# _61, tmp311,
	mull	a7, a7, a2	# tmp313, tmp312, _61
	mull	a2, a3, a2	# tmp316, tmp315, _61
	slli	a7, a7, 1	# tmp314, tmp313,
	srai	a2, a2, 15	# tmp317, tmp316,
	add.n	a7, a7, a2	# tmp318, tmp314, tmp317
	add.n	a7, a7, a8	# tmp319, tmp318,
# @OPUS@\upstream\celt\quant_bands.c:355:       *delayedIntra = ADD32(MULT16_32_Q15(MULT16_16_Q15(pred_coef[LM], pred_coef[LM]),*delayedIntra),
	l32i	a8, sp, 300	# delayedIntra,
	s32i.n	a7, a8, 0	# *delayedIntra_91(D), tmp319
	j	.L74		#
.L69:
# @OPUS@\upstream\celt\quant_bands.c:348:       OPUS_COPY(oldEBands, oldEBands_intra, C*m->nbEBands);
	l32i	a8, sp, 168	# %sfp,
	l32i	a3, sp, 160	# %sfp,
	l32i.n	a4, a8, 8	# m_100(D)->nbEBands, m_100(D)->nbEBands
	l32i	a2, sp, 176	# %sfp,
	mull	a4, a13, a4	#, C, m_100(D)->nbEBands
	movi.n	a5, 2	#,
.L86:
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\quant_bands.c:349:       OPUS_COPY(error, error_intra, C*m->nbEBands);
	l32i	a8, sp, 168	# %sfp,
	l32i	a2, sp, 276	# error,
	l32i.n	a4, a8, 8	# m_100(D)->nbEBands, m_100(D)->nbEBands
	l32i	a3, sp, 180	# %sfp,
	mull	a4, a13, a4	#, C, m_100(D)->nbEBands
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\quant_bands.c:353:       *delayedIntra = new_distortion;
	l32i	a2, sp, 184	# %sfp,
	l32i	a8, sp, 300	# delayedIntra,
	s32i.n	a2, a8, 0	# *delayedIntra_91(D),
.L74:
# @OPUS@\upstream\celt\quant_bands.c:358:    RESTORE_STACK;
	l32i	a2, sp, 144	# _saved_stack,
	l32i	a3, sp, 148	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\quant_bands.c:359: }
	l32i	a0, sp, 268	#,
	movi	a9, 0x110	#,
	l32i	a12, sp, 264	#,
	l32i	a13, sp, 260	#,
	l32i	a14, sp, 256	#,
	l32i	a15, sp, 252	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L68:
# @OPUS@\upstream\celt\quant_bands.c:319:       tell_intra = ec_tell_frac(enc);
	mov.n	a2, a12	#, enc
	s32i	a9, sp, 224	#,
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\quant_bands.c:326:       save_bytes = nintra_bytes-nstart_bytes;
	l32i.n	a2, a12, 24	# MEM[(struct ec_enc *)enc_105(D) + 24B], MEM[(struct ec_enc *)enc_105(D) + 24B]
	l32i	a8, sp, 164	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:325:       intra_buf = ec_get_buffer(&enc_intra_state) + nstart_bytes;
	l32i.n	a5, a12, 0	# MEM[(struct ec_enc *)enc_105(D)], MEM[(struct ec_enc *)enc_105(D)]
# @OPUS@\upstream\celt\quant_bands.c:326:       save_bytes = nintra_bytes-nstart_bytes;
	sub	a6, a2, a8	# save_bytes, MEM[(struct ec_enc *)enc_105(D) + 24B],
# @OPUS@\upstream\celt\quant_bands.c:329:       ALLOC(intra_bits, save_bytes, unsigned char);
	l32i	a4, sp, 188	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:325:       intra_buf = ec_get_buffer(&enc_intra_state) + nstart_bytes;
	add.n	a5, a5, a8	# intra_buf, MEM[(struct ec_enc *)enc_105(D)],
# @OPUS@\upstream\celt\quant_bands.c:329:       ALLOC(intra_bits, save_bytes, unsigned char);
	movi.n	a3, 1	#,
	mov.n	a2, a6	#, save_bytes
	s32i	a5, sp, 216	#,
	s32i	a6, sp, 220	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\quant_bands.c:331:       OPUS_COPY(intra_bits, intra_buf, nintra_bytes - nstart_bytes);
	l32i	a6, sp, 220	#,
	l32i	a5, sp, 216	#,
	mov.n	a4, a6	#, save_bytes
	mov.n	a3, a5	#, intra_buf
	movi.n	a5, 1	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\quant_bands.c:333:       *enc = enc_start_state;
	l32i	a2, sp, 128	# enc_start_state,
	l32i	a7, sp, 132	# enc_start_state,
	s32i.n	a2, a12, 32	# *enc_105(D),
	l32i	a2, sp, 136	# enc_start_state,
	l32i	a8, sp, 124	# enc_start_state, enc_start_state
	s32i.n	a7, a12, 36	# *enc_105(D),
	s32i.n	a2, a12, 40	# *enc_105(D),
	l32i	a6, sp, 100	# enc_start_state, enc_start_state
	l32i	a5, sp, 104	# enc_start_state, enc_start_state
	l32i	a4, sp, 108	# enc_start_state, enc_start_state
	l32i	a3, sp, 112	# enc_start_state, enc_start_state
	l32i	a2, sp, 140	# enc_start_state, enc_start_state
	l32i	a7, sp, 96	# enc_start_state, enc_start_state
	l32i	a10, sp, 116	# enc_start_state, enc_start_state
	l32i	a11, sp, 120	# enc_start_state, enc_start_state
	s32i.n	a8, a12, 28	# *enc_105(D), enc_start_state
# @OPUS@\upstream\celt\quant_bands.c:335:       badness2 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands, budget,
	l32i	a8, sp, 312	# lfe,
# @OPUS@\upstream\celt\quant_bands.c:333:       *enc = enc_start_state;
	s32i.n	a7, a12, 0	# *enc_105(D), enc_start_state
	s32i.n	a6, a12, 4	# *enc_105(D), enc_start_state
	s32i.n	a5, a12, 8	# *enc_105(D), enc_start_state
	s32i.n	a4, a12, 12	# *enc_105(D), enc_start_state
	s32i.n	a3, a12, 16	# *enc_105(D), enc_start_state
	s32i.n	a2, a12, 44	# *enc_105(D), enc_start_state
	s32i.n	a10, a12, 20	# *enc_105(D), enc_start_state
	s32i.n	a11, a12, 24	# *enc_105(D), enc_start_state
# @OPUS@\upstream\celt\quant_bands.c:335:       badness2 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands, budget,
	l32i	a6, sp, 188	# %sfp,
	s32i.n	a8, sp, 32	#,
	l32i	a8, sp, 288	# LM,
	s32i.n	a6, sp, 24	#,
	s32i.n	a8, sp, 20	#,
	s32i.n	a15, sp, 28	#, max_decay
	s32i.n	a13, sp, 16	#, C
	s32i.n	a12, sp, 12	#, enc
	l32i	a8, sp, 276	# error,
# @OPUS@\upstream\celt\quant_bands.c:336:             tell, e_prob_model[LM][intra], error, enc, C, LM, 0, max_decay, lfe);
	l32r	a2, .LC12	#, tmp341
	l32i	a9, sp, 224	#,
# @OPUS@\upstream\celt\quant_bands.c:335:       badness2 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands, budget,
	s32i.n	a8, sp, 8	#,
	l32i	a8, sp, 204	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:336:             tell, e_prob_model[LM][intra], error, enc, C, LM, 0, max_decay, lfe);
	add.n	a9, a9, a2	# tmp340, tmp245, tmp341
# @OPUS@\upstream\celt\quant_bands.c:335:       badness2 = quant_coarse_energy_impl(m, start, end, eBands, oldEBands, budget,
	l32i	a7, sp, 272	# budget,
	l32i	a6, sp, 176	# %sfp,
	l32i	a5, sp, 200	# %sfp,
	l32i	a4, sp, 196	# %sfp,
	l32i	a2, sp, 168	# %sfp,
	s32i.n	a9, sp, 4	#, tmp340
	s32i.n	a8, sp, 0	#,
	mov.n	a3, a14	#, start
	call0	quant_coarse_energy_impl		#
	j	.L75		#
	.size	quant_coarse_energy, .-quant_coarse_energy
	.section	.text.quant_fine_energy,"ax",@progbits
	.literal_position
	.align	4
	.global	quant_fine_energy
	.type	quant_fine_energy, @function
# Function: quant_fine_energy
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: RESTORE_STACK;
# C context: }
# C context:
# C context: void quant_fine_energy(const CELTMode *m, int start, int end, opus_val16 *oldEBands, opus_val16 *error, int *fine_quant, ec_enc *enc, int C)
# C context: {
# C context: int i, c;
# C context:
# C context: /* Encode finer resolution */
quant_fine_energy:
	addi	sp, sp, -64	#,,
	s32i.n	a13, sp, 52	#,
	slli	a13, a3, 2	# tmp92, start,
	add.n	a13, a7, a13	#, fine_quant, tmp92
	s32i.n	a0, sp, 60	#,
	s32i.n	a12, sp, 56	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\celt\quant_bands.c:362: {
	s32i.n	a4, sp, 16	# %sfp, end
	s32i.n	a2, sp, 8	# %sfp, m
	s32i.n	a5, sp, 12	# %sfp, oldEBands
	s32i.n	a13, sp, 0	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:366:    for (i=start;i<end;i++)
	bge	a3, a4, .L87	# start, end,
	mov.n	a14, a3	# start, start
	mov.n	a15, a6	# error, error
.L90:
# @OPUS@\upstream\celt\quant_bands.c:368:       opus_int16 frac = 1<<fine_quant[i];
	l32i.n	a5, sp, 0	# %sfp,
	l32i.n	a10, a5, 0	# MEM[base: _115, offset: 0B], _24
# @OPUS@\upstream\celt\quant_bands.c:369:       if (fine_quant[i] <= 0)
	bgei	a10, 1, .L89	# _24,,
.L94:
	l32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:366:    for (i=start;i<end;i++)
	l32i.n	a2, sp, 16	# %sfp,
	addi.n	a5, a5, 4	#,,
# @OPUS@\upstream\celt\quant_bands.c:366:    for (i=start;i<end;i++)
	addi.n	a14, a14, 1	# start, start,
	s32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:366:    for (i=start;i<end;i++)
	bne	a2, a14, .L90	#, start,
	j	.L87		#
.L89:
# @OPUS@\upstream\celt\quant_bands.c:368:       opus_int16 frac = 1<<fine_quant[i];
	movi.n	a3, 1	#,
	ssl	a10	# _24
	sll	a12, a3	# tmp94,
	slli	a12, a12, 16	# tmp96, tmp94,
	l32i.n	a5, sp, 8	# %sfp,
	srai	a12, a12, 16	# tmp95, tmp96,
	addi.n	a12, a12, -1	#, tmp95,
	l32i.n	a9, a5, 8	# m_50(D)->nbEBands, _27
# @OPUS@\upstream\celt\quant_bands.c:371:       c=0;
	movi.n	a13, 0	# c,
	s32i.n	a12, sp, 4	# %sfp,
.L93:
# @OPUS@\upstream\celt\quant_bands.c:377:          q2 = (error[i+c*m->nbEBands]+QCONST16(.5f,DB_SHIFT))>>(DB_SHIFT-fine_quant[i]);
	mull	a9, a13, a9	# tmp97, c, _27
# @OPUS@\upstream\celt\quant_bands.c:377:          q2 = (error[i+c*m->nbEBands]+QCONST16(.5f,DB_SHIFT))>>(DB_SHIFT-fine_quant[i]);
	movi.n	a3, 0xa	#,
# @OPUS@\upstream\celt\quant_bands.c:377:          q2 = (error[i+c*m->nbEBands]+QCONST16(.5f,DB_SHIFT))>>(DB_SHIFT-fine_quant[i]);
	add.n	a9, a9, a14	# tmp98, tmp97, start
	slli	a9, a9, 1	# tmp99, tmp98,
	add.n	a9, a15, a9	# tmp100, error, tmp99
# @OPUS@\upstream\celt\quant_bands.c:385:          ec_enc_bits(enc, q2, fine_quant[i]);
	mov.n	a4, a10	#, _24
# @OPUS@\upstream\celt\quant_bands.c:377:          q2 = (error[i+c*m->nbEBands]+QCONST16(.5f,DB_SHIFT))>>(DB_SHIFT-fine_quant[i]);
	sub	a10, a3, a10	# tmp106,, _24
# @OPUS@\upstream\celt\quant_bands.c:377:          q2 = (error[i+c*m->nbEBands]+QCONST16(.5f,DB_SHIFT))>>(DB_SHIFT-fine_quant[i]);
	l16si	a3, a9, 0	# *_11, tmp101
	l32i.n	a5, sp, 4	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:377:          q2 = (error[i+c*m->nbEBands]+QCONST16(.5f,DB_SHIFT))>>(DB_SHIFT-fine_quant[i]);
	addmi	a3, a3, 0x200	# tmp104, tmp101,
# @OPUS@\upstream\celt\quant_bands.c:377:          q2 = (error[i+c*m->nbEBands]+QCONST16(.5f,DB_SHIFT))>>(DB_SHIFT-fine_quant[i]);
	ssr	a10	# tmp106
	sra	a3, a3	# q2, tmp104
# @OPUS@\upstream\celt\quant_bands.c:385:          ec_enc_bits(enc, q2, fine_quant[i]);
	l32i	a2, sp, 64	# enc,
	bge	a5, a3, .L92	#, q2,
	mov.n	a3, a5	# q2,
.L92:
	movi.n	a12, 0	# q2$33_19,
	movgez	a12, a3, a3	# q2$33_19, q2, q2
	mov.n	a3, a12	#, q2$33_19
	call0	ec_enc_bits		#
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a2, sp, 8	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:387:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	l32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a9, a2, 8	# m_50(D)->nbEBands, _27
# @OPUS@\upstream\celt\quant_bands.c:387:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	l32i.n	a10, a5, 0	# MEM[base: _115, offset: 0B], _24
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	mull	a4, a9, a13	# tmp114, _27, c
# @OPUS@\upstream\celt\quant_bands.c:387:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	slli	a2, a12, 10	# tmp108, q2$33_19,
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a3, sp, 12	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:387:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	addmi	a2, a2, 0x200	# tmp109, tmp108,
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	add.n	a4, a4, a14	# tmp115, tmp114, start
	slli	a4, a4, 1	# _31, tmp115,
# @OPUS@\upstream\celt\quant_bands.c:387:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	ssr	a10	# _24
	sra	a2, a2	# tmp110, tmp109
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	add.n	a5, a3, a4	# _32,, _31
# @OPUS@\upstream\celt\quant_bands.c:387:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	addmi	a2, a2, -0x200	# tmp112, tmp110,
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	l16ui	a11, a5, 0	# *_32,
# @OPUS@\upstream\celt\quant_bands.c:387:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	slli	a2, a2, 16	# tmp113, tmp112,
	srai	a2, a2, 16	# offset, tmp113,
# @OPUS@\upstream\celt\quant_bands.c:391:          oldEBands[i+c*m->nbEBands] += offset;
	add.n	a11, a2, a11	# tmp117, offset, *_32
	s16i	a11, a5, 0	# *_32, tmp117
# @OPUS@\upstream\celt\quant_bands.c:392:          error[i+c*m->nbEBands] -= offset;
	add.n	a4, a15, a4	# _35, error, _31
	l16ui	a3, a4, 0	# *_35,
# @OPUS@\upstream\celt\quant_bands.c:394:       } while (++c < C);
	l32i	a5, sp, 68	# C,
# @OPUS@\upstream\celt\quant_bands.c:392:          error[i+c*m->nbEBands] -= offset;
	sub	a2, a3, a2	# tmp119, *_35, offset
# @OPUS@\upstream\celt\quant_bands.c:394:       } while (++c < C);
	addi.n	a13, a13, 1	# c, c,
# @OPUS@\upstream\celt\quant_bands.c:392:          error[i+c*m->nbEBands] -= offset;
	s16i	a2, a4, 0	# *_35, tmp119
# @OPUS@\upstream\celt\quant_bands.c:394:       } while (++c < C);
	blt	a13, a5, .L93	# c,,
	j	.L94		#
.L87:
# @OPUS@\upstream\celt\quant_bands.c:396: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	quant_fine_energy, .-quant_fine_energy
	.section	.text.quant_energy_finalise,"ax",@progbits
	.literal_position
	.align	4
	.global	quant_energy_finalise
	.type	quant_energy_finalise, @function
# Function: quant_energy_finalise
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void quant_energy_finalise(const CELTMode *m, int start, int end, opus_val16 *oldEBands, opus_val16 *error, int *fine_quant, int *fine_priority, int bits_left, ec_enc *enc, int C)
# C context: {
# C context: int i, prio, c;
# C context:
# C context: /* Use up the remaining bits */
quant_energy_finalise:
	addi	sp, sp, -80	#,,
	s32i.n	a3, sp, 20	# %sfp, start
	s32i.n	a2, sp, 0	# %sfp, m
	l32i.n	a2, sp, 20	# %sfp,
	s32i.n	a15, sp, 60	#,
	s32i	a0, sp, 76	#,
	s32i	a12, sp, 72	#,
	s32i	a13, sp, 68	#,
	s32i	a14, sp, 64	#,
# @OPUS@\upstream\celt\quant_bands.c:399: {
	s32i.n	a4, sp, 12	# %sfp, end
	s32i.n	a5, sp, 8	# %sfp, oldEBands
	mov.n	a15, a6	# error, error
	l32i	a10, sp, 84	# bits_left, bits_left
	movi.n	a3, 1	# tmp104,
	blt	a2, a4, .L99	#, end,
	movi.n	a3, 0	# tmp104,
.L99:
	l32i.n	a4, sp, 20	# %sfp,
	extui	a3, a3, 0, 8	#, tmp104
	slli	a2, a4, 2	# tmp106,,
	add.n	a2, a7, a2	#, fine_quant, tmp106
# @OPUS@\upstream\celt\quant_bands.c:403:    for (prio=0;prio<2;prio++)
	movi.n	a5, 0	#,
	s32i.n	a3, sp, 28	# %sfp,
	s32i.n	a2, sp, 24	# %sfp,
	s32i.n	a5, sp, 16	# %sfp,
	j	.L100		#
.L123:
	mov.n	a2, a15	# error, error
	mov.n	a15, a14	# i, i
	mov.n	a14, a12	# ivtmp$110, ivtmp$110
	mov.n	a12, a2	# error, error
.L103:
# @OPUS@\upstream\celt\quant_bands.c:407:          if (fine_quant[i] >= MAX_FINE_BITS || fine_priority[i]!=prio)
	l32i.n	a2, a14, 0	# MEM[base: _98, offset: 0B], MEM[base: _98, offset: 0B]
	bgei	a2, 8, .L101	# MEM[base: _98, offset: 0B],,
# @OPUS@\upstream\celt\quant_bands.c:407:          if (fine_quant[i] >= MAX_FINE_BITS || fine_priority[i]!=prio)
	l32i	a5, sp, 80	# fine_priority,
	slli	a2, a15, 2	# tmp108, i,
	add.n	a2, a5, a2	# tmp109,, tmp108
# @OPUS@\upstream\celt\quant_bands.c:407:          if (fine_quant[i] >= MAX_FINE_BITS || fine_priority[i]!=prio)
	l32i.n	a2, a2, 0	# MEM[base: _94, offset: 0B], MEM[base: _94, offset: 0B]
	l32i.n	a5, sp, 16	# %sfp,
	bne	a2, a5, .L101	# MEM[base: _94, offset: 0B],,
	l32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:409:          c=0;
	movi.n	a13, 0	# c,
	l32i.n	a2, a3, 8	# m_56(D)->nbEBands, _24
	addi.n	a10, a10, -1	#, bits_left,
	mov.n	a3, a12	# error, error
	s32i.n	a10, sp, 4	# %sfp,
	mov.n	a12, a13	# c, c
	mov.n	a13, a15	# i, i
	mov.n	a15, a3	# error, error
.L102:
# @OPUS@\upstream\celt\quant_bands.c:413:             q2 = error[i+c*m->nbEBands]<0 ? 0 : 1;
	mull	a2, a12, a2	# tmp111, c, _24
# @OPUS@\upstream\celt\quant_bands.c:414:             ec_enc_bits(enc, q2, 1);
	movi.n	a4, 1	#,
# @OPUS@\upstream\celt\quant_bands.c:413:             q2 = error[i+c*m->nbEBands]<0 ? 0 : 1;
	add.n	a2, a2, a13	# tmp112, tmp111, i
	ssl	a4	#
	sll	a2, a2	# tmp113, tmp112
	add.n	a2, a15, a2	# tmp114, error, tmp113
# @OPUS@\upstream\celt\quant_bands.c:413:             q2 = error[i+c*m->nbEBands]<0 ? 0 : 1;
	l16ui	a9, a2, 0	# *_13,
	movi.n	a5, -1	#,
	xor	a9, a5, a9	# tmp117,, *_13
	extui	a9, a9, 15, 1	# _15, tmp117,,
# @OPUS@\upstream\celt\quant_bands.c:414:             ec_enc_bits(enc, q2, 1);
	l32i	a2, sp, 88	# enc,
	mov.n	a3, a9	#, _15
	s32i.n	a9, sp, 32	#,
	call0	ec_enc_bits		#
# @OPUS@\upstream\celt\quant_bands.c:420:             oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:416:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	l32i.n	a9, sp, 32	#,
# @OPUS@\upstream\celt\quant_bands.c:420:             oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a2, a3, 8	# m_56(D)->nbEBands, _24
# @OPUS@\upstream\celt\quant_bands.c:420:             oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a5, sp, 8	# %sfp,
	mull	a3, a2, a12	# tmp128, _24, c
# @OPUS@\upstream\celt\quant_bands.c:416:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	l32i.n	a10, a14, 0	# MEM[base: _98, offset: 0B], MEM[base: _98, offset: 0B]
# @OPUS@\upstream\celt\quant_bands.c:420:             oldEBands[i+c*m->nbEBands] += offset;
	add.n	a3, a3, a13	# tmp129, tmp128, i
	slli	a3, a3, 1	# _28, tmp129,
	add.n	a11, a5, a3	# _29,, _28
# @OPUS@\upstream\celt\quant_bands.c:416:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	slli	a9, a9, 10	# tmp122, _15,
# @OPUS@\upstream\celt\quant_bands.c:420:             oldEBands[i+c*m->nbEBands] += offset;
	l16ui	a4, a11, 0	# *_29,
# @OPUS@\upstream\celt\quant_bands.c:416:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	addi.n	a10, a10, 1	# tmp124, MEM[base: _98, offset: 0B],
	addmi	a9, a9, -0x200	# tmp123, tmp122,
# @OPUS@\upstream\celt\quant_bands.c:416:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	ssr	a10	# tmp124
	sra	a9, a9	# offset, tmp123
# @OPUS@\upstream\celt\quant_bands.c:420:             oldEBands[i+c*m->nbEBands] += offset;
	add.n	a4, a9, a4	# tmp131, offset, *_29
	s16i	a4, a11, 0	# *_29, tmp131
# @OPUS@\upstream\celt\quant_bands.c:421:             error[i+c*m->nbEBands] -= offset;
	add.n	a3, a15, a3	# _32, error, _28
	l16ui	a4, a3, 0	# *_32,
	l32i.n	a5, sp, 4	# %sfp,
	sub	a9, a4, a9	# tmp133, *_32, offset
	sub	a10, a5, a12	# _107,, c
# @OPUS@\upstream\celt\quant_bands.c:423:          } while (++c < C);
	l32i	a5, sp, 92	# C,
# @OPUS@\upstream\celt\quant_bands.c:421:             error[i+c*m->nbEBands] -= offset;
	s16i	a9, a3, 0	# *_32, tmp133
# @OPUS@\upstream\celt\quant_bands.c:423:          } while (++c < C);
	addi.n	a12, a12, 1	# c, c,
	blt	a12, a5, .L102	# c,,
	mov.n	a12, a15	# error, error
	mov.n	a15, a13	# i, i
.L101:
# @OPUS@\upstream\celt\quant_bands.c:405:       for (i=start;i<end && bits_left>=C ;i++)
	l32i.n	a2, sp, 12	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:405:       for (i=start;i<end && bits_left>=C ;i++)
	addi.n	a15, a15, 1	# i, i,
	addi.n	a14, a14, 4	# ivtmp$110, ivtmp$110,
# @OPUS@\upstream\celt\quant_bands.c:405:       for (i=start;i<end && bits_left>=C ;i++)
	bge	a15, a2, .L122	# i,,
# @OPUS@\upstream\celt\quant_bands.c:405:       for (i=start;i<end && bits_left>=C ;i++)
	l32i	a5, sp, 92	# C,
	bge	a10, a5, .L103	# bits_left,,
.L122:
	mov.n	a15, a12	# error, error
.L110:
# @OPUS@\upstream\celt\quant_bands.c:403:    for (prio=0;prio<2;prio++)
	l32i.n	a5, sp, 16	# %sfp,
	beqi	a5, 1, .L98	#,,
	movi.n	a5, 1	#,
	s32i.n	a5, sp, 16	# %sfp,
.L100:
# @OPUS@\upstream\celt\quant_bands.c:405:       for (i=start;i<end && bits_left>=C ;i++)
	l32i	a5, sp, 92	# C,
	blt	a10, a5, .L110	# bits_left,,
# @OPUS@\upstream\celt\quant_bands.c:405:       for (i=start;i<end && bits_left>=C ;i++)
	l32i.n	a5, sp, 28	# %sfp,
	l32i.n	a12, sp, 24	# %sfp, ivtmp$110
	l32i.n	a14, sp, 20	# %sfp, i
	bnez.n	a5, .L123	#,
	j	.L110		#
.L98:
# @OPUS@\upstream\celt\quant_bands.c:426: }
	l32i	a0, sp, 76	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	quant_energy_finalise, .-quant_energy_finalise
	.section	.text.unquant_coarse_energy,"ax",@progbits
	.literal_position
	.literal .LC14, 4915
	.literal .LC15, -131072
	.literal .LC16, e_prob_model
	.literal .LC17, beta_coef
	.literal .LC18, pred_coef
	.literal .LC19, small_energy_icdf
	.literal .LC20, -9216
	.literal .LC21, -3670016
	.align	4
	.global	unquant_coarse_energy
	.type	unquant_coarse_energy, @function
# Function: unquant_coarse_energy
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void unquant_coarse_energy(const CELTMode *m, int start, int end, opus_val16 *oldEBands, int intra, ec_dec *dec, int C, int LM)
# C context: {
# C context: const unsigned char *prob_model = e_prob_model[LM][intra];
# C context: int i, c;
# C context: opus_val32 prev[2] = {0, 0};
unquant_coarse_energy:
	addi	sp, sp, -80	#,,
	l32i	a8, sp, 84	# LM, LM
	s32i	a13, sp, 68	#,
# @OPUS@\upstream\celt\quant_bands.c:430:    const unsigned char *prob_model = e_prob_model[LM][intra];
	slli	a10, a8, 1	# tmp214, LM,
	slli	a13, a6, 1	# tmp208, intra,
	add.n	a9, a10, a8	# tmp215, tmp214, LM
	add.n	a11, a13, a6	# tmp209, tmp208, intra
	slli	a8, a9, 3	# tmp216, tmp215,
	slli	a13, a11, 3	# tmp210, tmp209,
	sub	a8, a8, a9	# tmp217, tmp216, tmp215
	sub	a13, a13, a11	# tmp211, tmp210, tmp209
# @OPUS@\upstream\celt\quant_bands.c:432:    opus_val32 prev[2] = {0, 0};
	movi.n	a9, 0	# tmp221,
# @OPUS@\upstream\celt\quant_bands.c:430:    const unsigned char *prob_model = e_prob_model[LM][intra];
	slli	a13, a13, 1	# tmp212, tmp211,
	slli	a8, a8, 2	# tmp218, tmp217,
# @OPUS@\upstream\celt\quant_bands.c:429: {
	s32i.n	a2, sp, 44	# %sfp, m
# @OPUS@\upstream\celt\quant_bands.c:430:    const unsigned char *prob_model = e_prob_model[LM][intra];
	l32r	a2, .LC16	#, tmp220
# @OPUS@\upstream\celt\quant_bands.c:429: {
	s32i	a12, sp, 72	#,
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\celt\quant_bands.c:430:    const unsigned char *prob_model = e_prob_model[LM][intra];
	add.n	a13, a13, a8	# tmp219, tmp212, tmp218
# @OPUS@\upstream\celt\quant_bands.c:429: {
	s32i	a0, sp, 76	#,
	s32i	a14, sp, 64	#,
# @OPUS@\upstream\celt\quant_bands.c:432:    opus_val32 prev[2] = {0, 0};
	s32i.n	a9, sp, 0	# prev, tmp221
	s32i.n	a9, sp, 4	# prev, tmp221
# @OPUS@\upstream\celt\quant_bands.c:429: {
	s32i.n	a4, sp, 40	# %sfp, end
	s32i.n	a5, sp, 20	# %sfp, oldEBands
	mov.n	a12, a3	# start, start
	mov.n	a15, a7	# dec, dec
# @OPUS@\upstream\celt\quant_bands.c:430:    const unsigned char *prob_model = e_prob_model[LM][intra];
	add.n	a13, a13, a2	# prob_model, tmp219, tmp220
# @OPUS@\upstream\celt\quant_bands.c:438:    if (intra)
	bne	a6, a9, .L144	# intra,,
# @OPUS@\upstream\celt\quant_bands.c:443:       beta = beta_coef[LM];
	l32r	a3, .LC17	#, tmp223
# @OPUS@\upstream\celt\quant_bands.c:444:       coef = pred_coef[LM];
	l32r	a2, .LC18	#, tmp228
# @OPUS@\upstream\celt\quant_bands.c:443:       beta = beta_coef[LM];
	add.n	a3, a3, a10	# tmp225, tmp223, tmp214
# @OPUS@\upstream\celt\quant_bands.c:444:       coef = pred_coef[LM];
	add.n	a10, a2, a10	# tmp230, tmp228, tmp214
# @OPUS@\upstream\celt\quant_bands.c:443:       beta = beta_coef[LM];
	l16si	a3, a3, 0	# beta_coef,
# @OPUS@\upstream\celt\quant_bands.c:444:       coef = pred_coef[LM];
	l16si	a10, a10, 0	# pred_coef,
# @OPUS@\upstream\celt\quant_bands.c:443:       beta = beta_coef[LM];
	s32i.n	a3, sp, 28	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:444:       coef = pred_coef[LM];
	s32i.n	a10, sp, 24	# %sfp,
	j	.L125		#
.L144:
# @OPUS@\upstream\celt\quant_bands.c:441:       beta = beta_intra;
	l32r	a5, .LC14	#,
# @OPUS@\upstream\celt\quant_bands.c:440:       coef = 0;
	s32i.n	a9, sp, 24	# %sfp, tmp221
# @OPUS@\upstream\celt\quant_bands.c:441:       beta = beta_intra;
	s32i.n	a5, sp, 28	# %sfp,
.L125:
# @OPUS@\upstream\celt\quant_bands.c:447:    budget = dec->storage*8;
	l32i.n	a2, a15, 4	# dec_66(D)->storage, dec_66(D)->storage
	l32r	a14, .LC21	#, tmp354
	slli	a2, a2, 3	#, dec_66(D)->storage,
	s32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:450:    for (i=start;i<end;i++)
	l32i.n	a2, sp, 40	# %sfp,
	bge	a12, a2, .L124	# start,,
.L142:
# @OPUS@\upstream\celt\quant_bands.c:465:             pi = 2*IMIN(i,20);
	movi.n	a3, 0x14	#,
	mov.n	a2, a12	# start, start
	bge	a3, a12, .L127	#, start,
	mov.n	a2, a3	# start,
.L127:
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	l32i.n	a3, a15, 20	# MEM[(int *)dec_66(D) + 20B], MEM[(int *)dec_66(D) + 20B]
	l32i.n	a5, sp, 16	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:465:             pi = 2*IMIN(i,20);
	slli	a2, a2, 1	# pi$41_5, start,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a4, a15, 28	# MEM[(unsigned int *)dec_66(D) + 28B], MEM[(unsigned int *)dec_66(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	addi.n	a7, a2, 1	# tmp240, pi$41_5,
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	sub	a3, a5, a3	# tmp243,, MEM[(int *)dec_66(D) + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a4, a4	# _276, MEM[(unsigned int *)dec_66(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	addi	a3, a3, 32	# tmp245, tmp243,
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	add.n	a2, a13, a2	#, prob_model, pi$41_5
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	add.n	a7, a13, a7	#, prob_model, tmp240
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	sub	a3, a3, a4	# _273, tmp245, _276
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	movi.n	a4, 0xe	# tmp246,
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	s32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	blt	a4, a3, .L128	# tmp246, _273,
# @OPUS@\upstream\celt\quant_bands.c:469:          else if(budget-tell>=2)
	bgei	a3, 2, .L129	# _273,,
# @OPUS@\upstream\celt\quant_bands.c:474:          else if(budget-tell>=1)
	movi.n	a8, -4	# prephitmp_216,
	l32r	a2, .LC15	#, prephitmp_217
	bnei	a3, 1, .L130	# _273,,
# @OPUS@\upstream\celt\quant_bands.c:476:             qi = -ec_dec_bit_logp(dec, 1);
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
# @OPUS@\upstream\celt\quant_bands.c:476:             qi = -ec_dec_bit_logp(dec, 1);
	neg	a2, a2	# _269,
	slli	a8, a2, 18	# tmp251, _269,
	srai	a8, a8, 16	# prephitmp_216, tmp251,
	slli	a2, a2, 17	# prephitmp_217, _269,
	j	.L130		#
.L129:
# @OPUS@\upstream\celt\quant_bands.c:471:             qi = ec_dec_icdf(dec, small_energy_icdf, 2);
	l32r	a3, .LC19	#,
	movi.n	a4, 2	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	extui	a3, a2, 0, 1	# tmp253, qi,
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	srai	a7, a2, 1	# _253, qi,
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	neg	a2, a3	# _251, tmp253
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	xor	a2, a2, a7	# _245, _251, _253
	slli	a8, a2, 18	# tmp258, _245,
	srai	a8, a8, 16	# prephitmp_216, tmp258,
	slli	a2, a2, 17	# prephitmp_217, _245,
	j	.L130		#
.L128:
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a4, a7, 0	# *_12, *_12
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a3, a5, 0	# *_6, *_6
# @OPUS@\upstream\celt\quant_bands.c:466:             qi = ec_laplace_decode(dec,
	slli	a4, a4, 6	#, *_12,
	slli	a3, a3, 7	#, *_6,
	mov.n	a2, a15	#, dec
	call0	ec_laplace_decode		#
	slli	a8, a2, 18	# tmp267, qi,
	srai	a8, a8, 16	# prephitmp_216, tmp267,
	slli	a2, a2, 17	# prephitmp_217, qi,
.L130:
	l32i.n	a5, sp, 20	# %sfp,
	slli	a4, a12, 1	# tmp268, start,
# @OPUS@\upstream\celt\quant_bands.c:482:          oldEBands[i+c*m->nbEBands] = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	l32r	a9, .LC20	#, tmp270
	add.n	a4, a5, a4	# _36,, tmp268
	slli	a9, a9, 16	# tmp274, tmp270,
	l16si	a10, a4, 0	# MEM[base: _36, offset: 0B], tmp271
	srai	a9, a9, 16	# tmp273, tmp274,
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	l32i.n	a7, sp, 0	# prev, _203
# @OPUS@\upstream\celt\quant_bands.c:482:          oldEBands[i+c*m->nbEBands] = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	l16ui	a3, a4, 0	# MEM[base: _36, offset: 0B],
	bge	a10, a9, .L131	# tmp271, tmp273,
	l32r	a3, .LC20	#, MEM[base: _36, offset: 0B]
.L131:
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	l32i.n	a5, sp, 24	# %sfp,
	mul16s	a3, a3, a5	# tmp275, MEM[base: _36, offset: 0B],
	movi	a5, 0x80	#,
	add.n	a3, a3, a5	# tmp277, tmp275,
	srai	a3, a3, 8	# tmp278, tmp277,
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	add.n	a3, a3, a7	# tmp279, tmp278, _203
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	add.n	a3, a3, a2	# tmp, tmp279, prephitmp_217
# @OPUS@\upstream\celt\quant_bands.c:485:          tmp = MAX32(-QCONST32(28.f, DB_SHIFT+7), tmp);
	bge	a3, a14, .L132	# tmp, tmp354,
	mov.n	a3, a14	# tmp, tmp354
.L132:
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:487:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	addi	a3, a3, 64	# tmp286, tmp,
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	mull	a8, a8, a5	# tmp289, prephitmp_216,
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	add.n	a7, a7, a2	# tmp288, _203, prephitmp_217
# @OPUS@\upstream\celt\quant_bands.c:487:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	srai	a3, a3, 7	# tmp287, tmp286,
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	sub	a7, a7, a8	# tmp290, tmp288, tmp289
# @OPUS@\upstream\celt\quant_bands.c:489:       } while (++c < C);
	l32i	a5, sp, 80	# C,
# @OPUS@\upstream\celt\quant_bands.c:487:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	s16i	a3, a4, 0	# MEM[base: _36, offset: 0B], tmp287
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	s32i.n	a7, sp, 0	# prev, tmp290
# @OPUS@\upstream\celt\quant_bands.c:489:       } while (++c < C);
	blti	a5, 2, .L133	#,,
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	l32i.n	a3, a15, 20	# MEM[(int *)dec_66(D) + 20B], MEM[(int *)dec_66(D) + 20B]
	l32i.n	a5, sp, 16	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, a15, 28	# MEM[(unsigned int *)dec_66(D) + 28B], MEM[(unsigned int *)dec_66(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	sub	a3, a5, a3	# tmp293,, MEM[(int *)dec_66(D) + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a2, a2	# _186, MEM[(unsigned int *)dec_66(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	addi	a3, a3, 32	# tmp295, tmp293,
	sub	a3, a3, a2	# _183, tmp295, _186
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	movi.n	a2, 0xe	# tmp296,
	blt	a2, a3, .L134	# tmp296, _183,
# @OPUS@\upstream\celt\quant_bands.c:469:          else if(budget-tell>=2)
	bgei	a3, 2, .L135	# _183,,
# @OPUS@\upstream\celt\quant_bands.c:474:          else if(budget-tell>=1)
	movi.n	a8, -4	# prephitmp_135,
	l32r	a2, .LC15	#, prephitmp_136
	bnei	a3, 1, .L136	# _183,,
# @OPUS@\upstream\celt\quant_bands.c:476:             qi = -ec_dec_bit_logp(dec, 1);
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
# @OPUS@\upstream\celt\quant_bands.c:476:             qi = -ec_dec_bit_logp(dec, 1);
	neg	a2, a2	# _179,
	slli	a8, a2, 18	# tmp301, _179,
	srai	a8, a8, 16	# prephitmp_135, tmp301,
	slli	a2, a2, 17	# prephitmp_136, _179,
	j	.L136		#
.L135:
# @OPUS@\upstream\celt\quant_bands.c:471:             qi = ec_dec_icdf(dec, small_energy_icdf, 2);
	l32r	a3, .LC19	#,
	movi.n	a4, 2	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	extui	a3, a2, 0, 1	# tmp303, qi,
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	srai	a4, a2, 1	# _168, qi,
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	neg	a2, a3	# _166, tmp303
# @OPUS@\upstream\celt\quant_bands.c:472:             qi = (qi>>1)^-(qi&1);
	xor	a2, a2, a4	# _164, _166, _168
	slli	a8, a2, 18	# tmp308, _164,
	srai	a8, a8, 16	# prephitmp_135, tmp308,
	slli	a2, a2, 17	# prephitmp_136, _164,
	j	.L136		#
.L134:
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i.n	a5, sp, 36	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:466:             qi = ec_laplace_decode(dec,
	mov.n	a2, a15	#, dec
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a4, a5, 0	# *_12, *_12
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:466:             qi = ec_laplace_decode(dec,
	slli	a4, a4, 6	#, *_12,
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a3, a5, 0	# *_6, *_6
# @OPUS@\upstream\celt\quant_bands.c:466:             qi = ec_laplace_decode(dec,
	slli	a3, a3, 7	#, *_6,
	call0	ec_laplace_decode		#
	slli	a8, a2, 18	# tmp317, qi,
	srai	a8, a8, 16	# prephitmp_135, tmp317,
	slli	a2, a2, 17	# prephitmp_136, qi,
.L136:
# @OPUS@\upstream\celt\quant_bands.c:482:          oldEBands[i+c*m->nbEBands] = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	l32i.n	a3, sp, 44	# %sfp,
	l32i.n	a5, sp, 20	# %sfp,
	l32i.n	a4, a3, 8	# m_79(D)->nbEBands, m_79(D)->nbEBands
	l32r	a9, .LC20	#, tmp322
	add.n	a4, a12, a4	# tmp318, start, m_79(D)->nbEBands
	slli	a4, a4, 1	# tmp320, tmp318,
	add.n	a4, a5, a4	# _129,, tmp320
	slli	a9, a9, 16	# tmp326, tmp322,
	l16si	a10, a4, 0	# *_129, tmp323
	srai	a9, a9, 16	# tmp325, tmp326,
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	l32i.n	a7, sp, 4	# prev, _122
# @OPUS@\upstream\celt\quant_bands.c:482:          oldEBands[i+c*m->nbEBands] = MAX16(-QCONST16(9.f,DB_SHIFT), oldEBands[i+c*m->nbEBands]);
	l16ui	a3, a4, 0	# *_129,
	bge	a10, a9, .L137	# tmp323, tmp325,
	l32r	a3, .LC20	#, *_129
.L137:
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	l32i.n	a5, sp, 24	# %sfp,
	mul16s	a3, a3, a5	# tmp327, *_129,
	movi	a5, 0x80	#,
	add.n	a3, a3, a5	# tmp329, tmp327,
	srai	a3, a3, 8	# tmp330, tmp329,
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	add.n	a3, a3, a7	# tmp331, tmp330, _122
# @OPUS@\upstream\celt\quant_bands.c:483:          tmp = PSHR32(MULT16_16(coef,oldEBands[i+c*m->nbEBands]),8) + prev[c] + SHL32(q,7);
	add.n	a3, a3, a2	# tmp, tmp331, prephitmp_136
# @OPUS@\upstream\celt\quant_bands.c:485:          tmp = MAX32(-QCONST32(28.f, DB_SHIFT+7), tmp);
	bge	a3, a14, .L138	# tmp, tmp354,
	mov.n	a3, a14	# tmp, tmp354
.L138:
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:487:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	addi	a3, a3, 64	# tmp338, tmp,
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	mull	a8, a8, a5	# tmp341, prephitmp_135,
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	add.n	a7, a7, a2	# tmp340, _122, prephitmp_136
# @OPUS@\upstream\celt\quant_bands.c:487:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	srai	a3, a3, 7	# tmp339, tmp338,
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	sub	a7, a7, a8	# tmp342, tmp340, tmp341
# @OPUS@\upstream\celt\quant_bands.c:489:       } while (++c < C);
	l32i	a5, sp, 80	# C,
# @OPUS@\upstream\celt\quant_bands.c:487:          oldEBands[i+c*m->nbEBands] = PSHR32(tmp, 7);
	s16i	a3, a4, 0	# *_129, tmp339
# @OPUS@\upstream\celt\quant_bands.c:488:          prev[c] = prev[c] + SHL32(q,7) - MULT16_16(beta,PSHR32(q,8));
	s32i.n	a7, sp, 4	# prev, tmp342
# @OPUS@\upstream\celt\quant_bands.c:489:       } while (++c < C);
	beqi	a5, 2, .L133	#,,
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	l32i.n	a3, a15, 20	# MEM[(int *)dec_66(D) + 20B], MEM[(int *)dec_66(D) + 20B]
	l32i.n	a5, sp, 16	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, a15, 28	# MEM[(unsigned int *)dec_66(D) + 28B], MEM[(unsigned int *)dec_66(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	sub	a12, a5, a3	# tmp345,, MEM[(int *)dec_66(D) + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a2, a2	# _91, MEM[(unsigned int *)dec_66(D) + 28B]
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	addi	a12, a12, 32	# tmp347, tmp345,
	sub	a12, a12, a2	# _3, tmp347, _91
# @OPUS@\upstream\celt\quant_bands.c:462:          if(budget-tell>=15)
	movi.n	a2, 0xe	# tmp348,
	bge	a2, a12, .L139	# tmp348, _3,
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i.n	a5, sp, 36	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:466:             qi = ec_laplace_decode(dec,
	mov.n	a2, a15	#, dec
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a4, a5, 0	# *_12, *_12
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:466:             qi = ec_laplace_decode(dec,
	slli	a4, a4, 6	#, *_12,
# @OPUS@\upstream\celt\quant_bands.c:467:                   prob_model[pi]<<7, prob_model[pi+1]<<6);
	l8ui	a3, a5, 0	# *_6, *_6
# @OPUS@\upstream\celt\quant_bands.c:466:             qi = ec_laplace_decode(dec,
	slli	a3, a3, 7	#, *_6,
	call0	ec_laplace_decode		#
	j	.L140		#
.L139:
# @OPUS@\upstream\celt\quant_bands.c:469:          else if(budget-tell>=2)
	blti	a12, 2, .L141	# _3,,
# @OPUS@\upstream\celt\quant_bands.c:471:             qi = ec_dec_icdf(dec, small_energy_icdf, 2);
	l32r	a3, .LC19	#,
	movi.n	a4, 2	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_icdf		#
	j	.L140		#
.L141:
# @OPUS@\upstream\celt\quant_bands.c:476:             qi = -ec_dec_bit_logp(dec, 1);
	movi.n	a3, 1	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
.L140:
.L133:
# @OPUS@\upstream\celt\quant_bands.c:450:    for (i=start;i<end;i++)
	l32i.n	a2, sp, 40	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:450:    for (i=start;i<end;i++)
	addi.n	a12, a12, 1	# start, start,
# @OPUS@\upstream\celt\quant_bands.c:450:    for (i=start;i<end;i++)
	bne	a2, a12, .L142	#, start,
.L124:
# @OPUS@\upstream\celt\quant_bands.c:491: }
	l32i	a0, sp, 76	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	unquant_coarse_energy, .-unquant_coarse_energy
	.section	.text.unquant_fine_energy,"ax",@progbits
	.literal_position
	.align	4
	.global	unquant_fine_energy
	.type	unquant_fine_energy, @function
# Function: unquant_fine_energy
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void unquant_fine_energy(const CELTMode *m, int start, int end, opus_val16 *oldEBands, int *fine_quant, ec_dec *dec, int C)
# C context: {
# C context: int i, c;
# C context: /* Decode finer resolution */
# C context: for (i=start;i<end;i++)
unquant_fine_energy:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 40	#,
	s32i.n	a13, sp, 36	#,
	s32i.n	a14, sp, 32	#,
	slli	a13, a3, 2	# tmp72, start,
	s32i.n	a0, sp, 44	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\celt\quant_bands.c:494: {
	s32i.n	a4, sp, 8	# %sfp, end
	s32i.n	a5, sp, 0	# %sfp, oldEBands
	s32i.n	a7, sp, 4	# %sfp, dec
	mov.n	a12, a3	# start, start
	mov.n	a14, a2	# m, m
	add.n	a13, a6, a13	# ivtmp$128, fine_quant, tmp72
# @OPUS@\upstream\celt\quant_bands.c:497:    for (i=start;i<end;i++)
	bge	a3, a4, .L152	# start, end,
.L155:
# @OPUS@\upstream\celt\quant_bands.c:499:       if (fine_quant[i] <= 0)
	l32i.n	a3, a13, 0	# MEM[base: _41, offset: 0B], _11
# @OPUS@\upstream\celt\quant_bands.c:501:       c=0;
	movi.n	a15, 0	# c,
# @OPUS@\upstream\celt\quant_bands.c:499:       if (fine_quant[i] <= 0)
	bgei	a3, 1, .L154	# _11,,
.L157:
# @OPUS@\upstream\celt\quant_bands.c:497:    for (i=start;i<end;i++)
	l32i.n	a2, sp, 8	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:497:    for (i=start;i<end;i++)
	addi.n	a12, a12, 1	# start, start,
	addi.n	a13, a13, 4	# ivtmp$128, ivtmp$128,
# @OPUS@\upstream\celt\quant_bands.c:497:    for (i=start;i<end;i++)
	bne	a2, a12, .L155	#, start,
	j	.L152		#
.L154:
# @OPUS@\upstream\celt\quant_bands.c:505:          q2 = ec_dec_bits(dec, fine_quant[i]);
	l32i.n	a2, sp, 4	# %sfp,
	call0	ec_dec_bits		#
# @OPUS@\upstream\celt\quant_bands.c:511:          oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a4, a14, 8	# m_34(D)->nbEBands, m_34(D)->nbEBands
	l32i.n	a5, sp, 0	# %sfp,
	mull	a4, a15, a4	# tmp73, c, m_34(D)->nbEBands
# @OPUS@\upstream\celt\quant_bands.c:507:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	l32i.n	a3, a13, 0	# MEM[base: _41, offset: 0B], _11
# @OPUS@\upstream\celt\quant_bands.c:511:          oldEBands[i+c*m->nbEBands] += offset;
	add.n	a4, a4, a12	# tmp75, tmp73, start
# @OPUS@\upstream\celt\quant_bands.c:507:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	slli	a2, a2, 10	# tmp77,,
# @OPUS@\upstream\celt\quant_bands.c:511:          oldEBands[i+c*m->nbEBands] += offset;
	slli	a4, a4, 1	# tmp76, tmp75,
	add.n	a4, a5, a4	# _19,, tmp76
# @OPUS@\upstream\celt\quant_bands.c:507:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	addmi	a2, a2, 0x200	# tmp78, tmp77,
# @OPUS@\upstream\celt\quant_bands.c:511:          oldEBands[i+c*m->nbEBands] += offset;
	l16ui	a6, a4, 0	# *_19,
# @OPUS@\upstream\celt\quant_bands.c:507:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	ssr	a3	# _11
	sra	a2, a2	# tmp79, tmp78
# @OPUS@\upstream\celt\quant_bands.c:507:          offset = SUB16(SHR32(SHL32(EXTEND32(q2),DB_SHIFT)+QCONST16(.5f,DB_SHIFT),fine_quant[i]),QCONST16(.5f,DB_SHIFT));
	addmi	a2, a2, -0x200	# tmp81, tmp79,
# @OPUS@\upstream\celt\quant_bands.c:511:          oldEBands[i+c*m->nbEBands] += offset;
	add.n	a2, a2, a6	# tmp84, tmp81, *_19
# @OPUS@\upstream\celt\quant_bands.c:512:       } while (++c < C);
	l32i.n	a5, sp, 48	# C,
# @OPUS@\upstream\celt\quant_bands.c:511:          oldEBands[i+c*m->nbEBands] += offset;
	s16i	a2, a4, 0	# *_19, tmp84
# @OPUS@\upstream\celt\quant_bands.c:512:       } while (++c < C);
	addi.n	a15, a15, 1	# c, c,
	blt	a15, a5, .L154	# c,,
	j	.L157		#
.L152:
# @OPUS@\upstream\celt\quant_bands.c:514: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	unquant_fine_energy, .-unquant_fine_energy
	.section	.text.unquant_energy_finalise,"ax",@progbits
	.literal_position
	.align	4
	.global	unquant_energy_finalise
	.type	unquant_energy_finalise, @function
# Function: unquant_energy_finalise
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void unquant_energy_finalise(const CELTMode *m, int start, int end, opus_val16 *oldEBands, int *fine_quant,  int *fine_priority, int bits_left, ec_dec *dec, int C)
# C context: {
# C context: int i, prio, c;
# C context:
# C context: /* Use up the remaining bits */
unquant_energy_finalise:
	addi	sp, sp, -64	#,,
	s32i.n	a3, sp, 20	# %sfp, start
	s32i.n	a15, sp, 44	#,
	mov.n	a15, a2	# m, m
	l32i.n	a2, sp, 20	# %sfp,
	s32i.n	a0, sp, 60	#,
	s32i.n	a12, sp, 56	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
# @OPUS@\upstream\celt\quant_bands.c:517: {
	s32i.n	a4, sp, 8	# %sfp, end
	s32i.n	a5, sp, 4	# %sfp, oldEBands
	s32i.n	a7, sp, 16	# %sfp, fine_priority
	l32i	a8, sp, 64	# bits_left, bits_left
	movi.n	a3, 1	# tmp96,
	blt	a2, a4, .L164	#, end,
	movi.n	a3, 0	# tmp96,
.L164:
	l32i.n	a4, sp, 20	# %sfp,
	extui	a3, a3, 0, 8	#, tmp96
	slli	a2, a4, 2	# tmp98,,
	add.n	a2, a6, a2	#, fine_quant, tmp98
# @OPUS@\upstream\celt\quant_bands.c:521:    for (prio=0;prio<2;prio++)
	movi.n	a4, 0	#,
	s32i.n	a3, sp, 28	# %sfp,
	s32i.n	a2, sp, 24	# %sfp,
	s32i.n	a4, sp, 12	# %sfp,
	j	.L165		#
.L188:
	mov.n	a2, a15	# m, m
	mov.n	a15, a12	# ivtmp$137, ivtmp$137
	mov.n	a12, a2	# m, m
.L168:
# @OPUS@\upstream\celt\quant_bands.c:525:          if (fine_quant[i] >= MAX_FINE_BITS || fine_priority[i]!=prio)
	l32i.n	a2, a15, 0	# MEM[base: _32, offset: 0B], MEM[base: _32, offset: 0B]
	bgei	a2, 8, .L166	# MEM[base: _32, offset: 0B],,
# @OPUS@\upstream\celt\quant_bands.c:525:          if (fine_quant[i] >= MAX_FINE_BITS || fine_priority[i]!=prio)
	l32i.n	a4, sp, 16	# %sfp,
	slli	a2, a14, 2	# tmp100, i,
	add.n	a2, a4, a2	# tmp101,, tmp100
# @OPUS@\upstream\celt\quant_bands.c:525:          if (fine_quant[i] >= MAX_FINE_BITS || fine_priority[i]!=prio)
	l32i.n	a2, a2, 0	# MEM[base: _85, offset: 0B], MEM[base: _85, offset: 0B]
	l32i.n	a4, sp, 12	# %sfp,
	bne	a2, a4, .L166	# MEM[base: _85, offset: 0B],,
# @OPUS@\upstream\celt\quant_bands.c:527:          c=0;
	movi.n	a13, 0	# c,
	mov.n	a2, a12	# m, m
	addi.n	a8, a8, -1	#, bits_left,
	mov.n	a12, a13	# c, c
	s32i.n	a8, sp, 0	# %sfp,
	mov.n	a13, a15	# ivtmp$137, ivtmp$137
	mov.n	a15, a2	# m, m
.L167:
# @OPUS@\upstream\celt\quant_bands.c:531:             q2 = ec_dec_bits(dec, 1);
	l32i	a2, sp, 68	# dec,
	movi.n	a3, 1	#,
	call0	ec_dec_bits		#
# @OPUS@\upstream\celt\quant_bands.c:537:             oldEBands[i+c*m->nbEBands] += offset;
	l32i.n	a3, a15, 8	# m_50(D)->nbEBands, m_50(D)->nbEBands
	l32i.n	a4, sp, 4	# %sfp,
	mull	a3, a12, a3	# tmp103, c, m_50(D)->nbEBands
# @OPUS@\upstream\celt\quant_bands.c:533:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	l32i.n	a7, a13, 0	# MEM[base: _32, offset: 0B], MEM[base: _32, offset: 0B]
# @OPUS@\upstream\celt\quant_bands.c:537:             oldEBands[i+c*m->nbEBands] += offset;
	add.n	a3, a3, a14	# tmp105, tmp103, i
# @OPUS@\upstream\celt\quant_bands.c:533:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	slli	a2, a2, 26	# tmp111,,
# @OPUS@\upstream\celt\quant_bands.c:537:             oldEBands[i+c*m->nbEBands] += offset;
	slli	a3, a3, 1	# tmp106, tmp105,
	add.n	a3, a4, a3	# _21,, tmp106
# @OPUS@\upstream\celt\quant_bands.c:533:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	srai	a2, a2, 16	# tmp110, tmp111,
# @OPUS@\upstream\celt\quant_bands.c:537:             oldEBands[i+c*m->nbEBands] += offset;
	l16ui	a8, a3, 0	# *_21,
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:533:             offset = SHR16(SHL16(q2,DB_SHIFT)-QCONST16(.5f,DB_SHIFT),fine_quant[i]+1);
	addmi	a2, a2, -0x200	# tmp112, tmp110,
	addi.n	a7, a7, 1	# tmp113, MEM[base: _32, offset: 0B],
	ssr	a7	# tmp113
	sra	a2, a2	# tmp115, tmp112
# @OPUS@\upstream\celt\quant_bands.c:537:             oldEBands[i+c*m->nbEBands] += offset;
	add.n	a2, a2, a8	# tmp118, tmp115, *_21
	sub	a8, a4, a12	# _71,, c
# @OPUS@\upstream\celt\quant_bands.c:539:          } while (++c < C);
	l32i	a4, sp, 72	# C,
# @OPUS@\upstream\celt\quant_bands.c:537:             oldEBands[i+c*m->nbEBands] += offset;
	s16i	a2, a3, 0	# *_21, tmp118
# @OPUS@\upstream\celt\quant_bands.c:539:          } while (++c < C);
	addi.n	a12, a12, 1	# c, c,
	blt	a12, a4, .L167	# c,,
	mov.n	a12, a15	# m, m
	mov.n	a15, a13	# ivtmp$137, ivtmp$137
.L166:
# @OPUS@\upstream\celt\quant_bands.c:523:       for (i=start;i<end && bits_left>=C ;i++)
	l32i.n	a4, sp, 8	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:523:       for (i=start;i<end && bits_left>=C ;i++)
	addi.n	a14, a14, 1	# i, i,
	addi.n	a15, a15, 4	# ivtmp$137, ivtmp$137,
# @OPUS@\upstream\celt\quant_bands.c:523:       for (i=start;i<end && bits_left>=C ;i++)
	bge	a14, a4, .L187	# i,,
# @OPUS@\upstream\celt\quant_bands.c:523:       for (i=start;i<end && bits_left>=C ;i++)
	l32i	a4, sp, 72	# C,
	bge	a8, a4, .L168	# bits_left,,
.L187:
	mov.n	a15, a12	# m, m
.L175:
# @OPUS@\upstream\celt\quant_bands.c:521:    for (prio=0;prio<2;prio++)
	l32i.n	a4, sp, 12	# %sfp,
	beqi	a4, 1, .L163	#,,
	movi.n	a4, 1	#,
	s32i.n	a4, sp, 12	# %sfp,
.L165:
# @OPUS@\upstream\celt\quant_bands.c:523:       for (i=start;i<end && bits_left>=C ;i++)
	l32i	a4, sp, 72	# C,
	blt	a8, a4, .L175	# bits_left,,
# @OPUS@\upstream\celt\quant_bands.c:523:       for (i=start;i<end && bits_left>=C ;i++)
	l32i.n	a4, sp, 28	# %sfp,
	l32i.n	a12, sp, 24	# %sfp, ivtmp$137
	l32i.n	a14, sp, 20	# %sfp, i
	bnez.n	a4, .L188	#,
	j	.L175		#
.L163:
# @OPUS@\upstream\celt\quant_bands.c:542: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	unquant_energy_finalise, .-unquant_energy_finalise
	.section	.text.amp2Log2,"ax",@progbits
	.literal_position
	.literal .LC23, -32767
	.literal .LC24, eMeans
	.literal .LC25, 2545
	.literal .LC26, -5217
	.literal .LC27, 15746
	.literal .LC28, -6793
	.literal .LC29, 2048
	.literal .LC30, -14336
	.literal .LC31, -939472896
	.align	4
	.global	amp2Log2
	.type	amp2Log2, @function
# Function: amp2Log2
# Module: upstream/celt/quant_bands.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void amp2Log2(const CELTMode *m, int effEnd, int end,
# C context: celt_ener *bandE, opus_val16 *bandLogE, int C)
# C context: {
# C context: int c, i;
# C context: c=0;
amp2Log2:
	addi	sp, sp, -48	#,,
	s32i.n	a3, sp, 0	# %sfp, effEnd
	s32i.n	a4, sp, 12	# %sfp, end
	addi.n	a3, a4, -1	# tmp166, end,
	l32i.n	a4, sp, 0	# %sfp,
	s32i.n	a15, sp, 32	#,
	s32i.n	a5, sp, 20	# %sfp, bandE
	sub	a3, a3, a4	#, tmp166,
# @OPUS@\upstream\celt\quant_bands.c:548:    c=0;
	movi.n	a5, 0	#,
	l32r	a15, .LC29	#, tmp281
# @OPUS@\upstream\celt\quant_bands.c:546: {
	s32i.n	a13, sp, 40	#,
	s32i.n	a14, sp, 36	#,
	s32i.n	a12, sp, 44	#,
# @OPUS@\upstream\celt\quant_bands.c:546: {
	s32i.n	a2, sp, 16	# %sfp, m
	s32i.n	a6, sp, 4	# %sfp, bandLogE
	s32i.n	a7, sp, 24	# %sfp, C
	s32i.n	a3, sp, 28	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:548:    c=0;
	s32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a14, 0x1f	# tmp283,
# @OPUS@\upstream\celt\mathops.h:212:    frac = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2], MULT16_16_Q15(n, ADD16(C[3], MULT16_16_Q15(n, C[4]))))))));
	movi	a13, -0x579	# tmp284,
.L200:
# @OPUS@\upstream\celt\quant_bands.c:550:       for (i=0;i<effEnd;i++)
	l32i.n	a8, sp, 0	# %sfp,
	blti	a8, 1, .L190	#,,
# @OPUS@\upstream\celt\quant_bands.c:553:                celt_log2(bandE[i+c*m->nbEBands])
	l32i.n	a2, sp, 16	# %sfp,
	mov.n	a4, a8	#,
	l32i.n	a3, sp, 8	# %sfp,
	l32i.n	a8, a2, 8	# m_32(D)->nbEBands, m_32(D)->nbEBands
	l32i.n	a5, sp, 20	# %sfp,
	mull	a8, a3, a8	# _65,, m_32(D)->nbEBands
	l32i.n	a6, sp, 4	# %sfp,
	add.n	a10, a8, a4	# tmp170, _65,
	slli	a7, a8, 2	# tmp168, _65,
	slli	a10, a10, 2	# tmp171, tmp170,
	slli	a8, a8, 1	# tmp169, _65,
	l32r	a9, .LC24	#, ivtmp$163
	add.n	a7, a5, a7	# ivtmp$162,, tmp168
	add.n	a8, a6, a8	# ivtmp$164,, tmp169
	add.n	a10, a5, a10	# _10,, tmp171
# @OPUS@\upstream\celt\mathops.h:213:    return SHL16(i-13,DB_SHIFT)+SHR16(frac,14-DB_SHIFT);
	movi.n	a12, 0x12	# tmp279,
# @OPUS@\upstream\celt\mathops.h:211:    n = VSHR32(x,i-15)-32768-16384;
	movi.n	a11, 0xf	# tmp280,
.L194:
# @OPUS@\upstream\celt\quant_bands.c:553:                celt_log2(bandE[i+c*m->nbEBands])
	l32i.n	a4, a7, 0	# MEM[base: _77, offset: 0B], _215
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a3, a4	# _212, _215
	sub	a5, a14, a3	# tmp174, tmp283, _212
# @OPUS@\upstream\celt\mathops.h:210:    i = celt_ilog2(x);
	slli	a5, a5, 16	# tmp175, tmp174,
	srai	a5, a5, 16	# i, tmp175,
# @OPUS@\upstream\celt\mathops.h:211:    n = VSHR32(x,i-15)-32768-16384;
	sub	a6, a11, a5	# tmp181, tmp280, i
	addi	a5, a5, -15	# _209, i,
	ssl	a6	# tmp181
	sll	a6, a4	# tmp182, _215
	ssr	a5	# _209
	sra	a2, a4	# tmp176, _215
# @OPUS@\upstream\celt\mathops.h:211:    n = VSHR32(x,i-15)-32768-16384;
	addmi	a6, a6, 0x4000	# tmp184, tmp182,
	addmi	a2, a2, 0x4000	# tmp178, tmp176,
	slli	a2, a2, 16	# tmp179, tmp178,
	slli	a6, a6, 16	# tmp185, tmp184,
# @OPUS@\upstream\celt\mathops.h:208:    if (x==0)
	beqz.n	a4, .L201	# _215,
# @OPUS@\upstream\celt\mathops.h:211:    n = VSHR32(x,i-15)-32768-16384;
	srai	a4, a2, 16	# iftmp$53_174, tmp179,
	bgei	a5, 1, .L193	# _209,,
.L192:
	srai	a4, a6, 16	# iftmp$53_174, tmp185,
.L193:
# @OPUS@\upstream\celt\mathops.h:212:    frac = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2], MULT16_16_Q15(n, ADD16(C[3], MULT16_16_Q15(n, C[4]))))))));
	mul16s	a2, a13, a4	# tmp187, tmp284, iftmp$53_174
	l32r	a5, .LC25	#,
	srai	a2, a2, 15	# tmp188, tmp187,
	add.n	a2, a2, a5	# tmp190, tmp188,
	mul16s	a2, a2, a4	# tmp192, tmp190, iftmp$53_174
	l32r	a6, .LC26	#,
	srai	a2, a2, 15	# tmp193, tmp192,
	add.n	a2, a2, a6	# tmp195, tmp193,
	mul16s	a2, a2, a4	# tmp197, tmp195, iftmp$53_174
	l32r	a5, .LC27	#,
	srai	a2, a2, 15	# tmp198, tmp197,
	add.n	a2, a2, a5	# tmp200, tmp198,
	mul16s	a2, a2, a4	# tmp202, tmp200, iftmp$53_174
# @OPUS@\upstream\celt\mathops.h:212:    frac = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2], MULT16_16_Q15(n, ADD16(C[3], MULT16_16_Q15(n, C[4]))))))));
	l32r	a6, .LC28	#,
# @OPUS@\upstream\celt\mathops.h:212:    frac = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2], MULT16_16_Q15(n, ADD16(C[3], MULT16_16_Q15(n, C[4]))))))));
	srai	a2, a2, 15	# tmp203, tmp202,
# @OPUS@\upstream\celt\mathops.h:213:    return SHL16(i-13,DB_SHIFT)+SHR16(frac,14-DB_SHIFT);
	sub	a3, a12, a3	# tmp211, tmp279, _212
# @OPUS@\upstream\celt\mathops.h:212:    frac = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2], MULT16_16_Q15(n, ADD16(C[3], MULT16_16_Q15(n, C[4]))))))));
	add.n	a2, a2, a6	# tmp205, tmp203,
# @OPUS@\upstream\celt\mathops.h:213:    return SHL16(i-13,DB_SHIFT)+SHR16(frac,14-DB_SHIFT);
	extui	a3, a3, 0, 16	# tmp212, tmp211
# @OPUS@\upstream\celt\mathops.h:213:    return SHL16(i-13,DB_SHIFT)+SHR16(frac,14-DB_SHIFT);
	slli	a2, a2, 16	# tmp208, tmp205,
# @OPUS@\upstream\celt\mathops.h:213:    return SHL16(i-13,DB_SHIFT)+SHR16(frac,14-DB_SHIFT);
	slli	a3, a3, 10	# tmp213, tmp212,
# @OPUS@\upstream\celt\mathops.h:213:    return SHL16(i-13,DB_SHIFT)+SHR16(frac,14-DB_SHIFT);
	srai	a2, a2, 20	# tmp209, tmp208,
	add.n	a2, a2, a3	# tmp216, tmp209, tmp213
	slli	a2, a2, 16	# tmp217, tmp216,
	srai	a2, a2, 16	# _173, tmp217,
	j	.L191		#
.L201:
# @OPUS@\upstream\celt\mathops.h:209:       return -32767;
	l32r	a2, .LC23	#, _173
.L191:
# @OPUS@\upstream\celt\quant_bands.c:554:                - SHL16((opus_val16)eMeans[i],6);
	l8ui	a3, a9, 0	# MEM[base: _78, offset: 0B],
	addi.n	a7, a7, 4	# ivtmp$162, ivtmp$162,
	slli	a3, a3, 24	# tmp221, MEM[base: _78, offset: 0B],
	srai	a3, a3, 24	# tmp219, tmp221,
	extui	a3, a3, 0, 16	# tmp222, tmp219
	slli	a3, a3, 6	# tmp223, tmp222,
# @OPUS@\upstream\celt\quant_bands.c:557:          bandLogE[i+c*m->nbEBands] += QCONST16(2.f, DB_SHIFT);
	sub	a3, a15, a3	# tmp225, tmp281, tmp223
	add.n	a2, a2, a3	# tmp228, _173, tmp225
	s16i	a2, a8, 0	# MEM[base: _79, offset: 0B], tmp228
	addi.n	a9, a9, 1	# ivtmp$163, ivtmp$163,
	addi.n	a8, a8, 2	# ivtmp$164, ivtmp$164,
# @OPUS@\upstream\celt\quant_bands.c:550:       for (i=0;i<effEnd;i++)
	bne	a10, a7, .L194	# _10, ivtmp$162,
.L190:
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	l32i.n	a8, sp, 0	# %sfp,
	l32i.n	a4, sp, 12	# %sfp,
	bge	a8, a4, .L195	#,,
	mov.n	a3, a8	#,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	l32i.n	a8, sp, 16	# %sfp,
	l32i.n	a5, sp, 8	# %sfp,
	l32i.n	a4, a8, 8	# m_32(D)->nbEBands, m_32(D)->nbEBands
	l32i.n	a8, sp, 12	# %sfp,
	mull	a4, a5, a4	# _19,, m_32(D)->nbEBands
	sub	a7, a8, a3	# niters$146,,
	add.n	a6, a4, a3	# _151, _19,
	l32i.n	a8, sp, 4	# %sfp,
	slli	a3, a6, 1	# tmp230, _151,
	l32i.n	a5, sp, 28	# %sfp,
	add.n	a3, a8, a3	# vectp$147,, tmp230
	extui	a2, a3, 1, 1	# prolog_loop_niters$148, vectp$147,,
	bltui	a5, 6, .L202	#,,
	l32i.n	a5, sp, 0	# %sfp, i
	beqz.n	a2, .L197	# prolog_loop_niters$148,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	l32r	a8, .LC30	#,
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	s16i	a8, a3, 0	# MEM[(opus_val16 *)vectp$147_227],
.L197:
	sub	a7, a7, a2	# niters$149, niters$146, prolog_loop_niters$148
	add.n	a2, a2, a6	# tmp234, prolog_loop_niters$148, _151
	l32i.n	a6, sp, 4	# %sfp,
	slli	a2, a2, 1	# tmp235, tmp234,
	srli	a3, a7, 1	# bnd$150, niters$149,
	add.n	a2, a6, a2	# ivtmp$159,, tmp235
	slli	a3, a3, 2	# tmp237, bnd$150,
	l32r	a6, .LC31	#, tmp265
	add.n	a3, a3, a2	# _61, tmp237, ivtmp$159
.L198:
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	s32i.n	a6, a2, 0	# MEM[base: _109, offset: 0B], tmp265
	addi.n	a2, a2, 4	# ivtmp$159, ivtmp$159,
	bne	a2, a3, .L198	# ivtmp$159, _61,
	movi.n	a2, -2	# tmp239,
	and	a2, a7, a2	# niters_vector_mult_vf$151, niters$149, tmp239
	add.n	a5, a2, a5	# tmp$152, niters_vector_mult_vf$151, i
	bne	a2, a7, .L196	# niters_vector_mult_vf$151, niters$149,
	j	.L195		#
.L202:
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	l32i.n	a5, sp, 0	# %sfp, tmp$152
.L196:
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	add.n	a2, a4, a5	# tmp240, _19, tmp$152
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	slli	a2, a2, 1	# tmp241, tmp240,
	l32r	a3, .LC30	#, tmp243
	add.n	a2, a8, a2	# tmp242,, tmp241
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	l32i.n	a8, sp, 12	# %sfp,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	s16i	a3, a2, 0	# *_21, tmp243
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	addi.n	a2, a5, 1	# i, tmp$152,
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	bge	a2, a8, .L195	# i,,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	add.n	a2, a4, a2	# tmp244, _19, i
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	l32i.n	a6, sp, 4	# %sfp,
	slli	a2, a2, 1	# tmp245, tmp244,
	add.n	a2, a6, a2	# tmp246,, tmp245
	s16i	a3, a2, 0	# *_4, tmp243
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	addi.n	a2, a5, 2	# i, tmp$152,
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	bge	a2, a8, .L195	# i,,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	add.n	a2, a2, a4	# tmp248, i, _19
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	slli	a2, a2, 1	# tmp249, tmp248,
	add.n	a2, a6, a2	# tmp250,, tmp249
	s16i	a3, a2, 0	# *_46, tmp243
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	addi.n	a2, a5, 3	# i, tmp$152,
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	bge	a2, a8, .L195	# i,,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	add.n	a2, a4, a2	# tmp252, _19, i
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	slli	a2, a2, 1	# tmp253, tmp252,
	add.n	a2, a6, a2	# tmp254,, tmp253
	s16i	a3, a2, 0	# *_228, tmp243
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	addi.n	a2, a5, 4	# i, tmp$152,
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	bge	a2, a8, .L195	# i,,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	add.n	a2, a4, a2	# tmp256, _19, i
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	slli	a2, a2, 1	# tmp257, tmp256,
	add.n	a2, a6, a2	# tmp258,, tmp257
	s16i	a3, a2, 0	# *_58, tmp243
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	addi.n	a5, a5, 5	# i, tmp$152,
# @OPUS@\upstream\celt\quant_bands.c:560:       for (i=effEnd;i<end;i++)
	bge	a5, a8, .L195	# i,,
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	add.n	a2, a4, a5	# tmp260, _19, i
# @OPUS@\upstream\celt\quant_bands.c:561:          bandLogE[c*m->nbEBands+i] = -QCONST16(14.f,DB_SHIFT);
	slli	a2, a2, 1	# tmp261, tmp260,
	add.n	a2, a6, a2	# tmp262,, tmp261
	s16i	a3, a2, 0	# *_124, tmp243
.L195:
# @OPUS@\upstream\celt\quant_bands.c:562:    } while (++c < C);
	l32i.n	a8, sp, 8	# %sfp,
	l32i.n	a2, sp, 24	# %sfp,
	addi.n	a8, a8, 1	#,,
	s32i.n	a8, sp, 8	# %sfp,
	blt	a8, a2, .L200	#,,
# @OPUS@\upstream\celt\quant_bands.c:563: }
	l32i.n	a12, sp, 44	#,
	l32i.n	a13, sp, 40	#,
	l32i.n	a14, sp, 36	#,
	l32i.n	a15, sp, 32	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	amp2Log2, .-amp2Log2
	.section	.rodata.small_energy_icdf,"a"
	.align	4
	.type	small_energy_icdf, @object
	.size	small_energy_icdf, 3
small_energy_icdf:
	.byte	2
	.byte	1
	.byte	0
	.section	.rodata.e_prob_model,"a"
	.align	4
	.type	e_prob_model, @object
	.size	e_prob_model, 336
e_prob_model:
	.byte	72
	.byte	127
	.byte	65
	.byte	-127
	.byte	66
	.byte	-128
	.byte	65
	.byte	-128
	.byte	64
	.byte	-128
	.byte	62
	.byte	-128
	.byte	64
	.byte	-128
	.byte	64
	.byte	-128
	.byte	92
	.byte	78
	.byte	92
	.byte	79
	.byte	92
	.byte	78
	.byte	90
	.byte	79
	.byte	116
	.byte	41
	.byte	115
	.byte	40
	.byte	114
	.byte	40
	.byte	-124
	.byte	26
	.byte	-124
	.byte	26
	.byte	-111
	.byte	17
	.byte	-95
	.byte	12
	.byte	-80
	.byte	10
	.byte	-79
	.byte	11
	.byte	24
	.byte	-77
	.byte	48
	.byte	-118
	.byte	54
	.byte	-121
	.byte	54
	.byte	-124
	.byte	53
	.byte	-122
	.byte	56
	.byte	-123
	.byte	55
	.byte	-124
	.byte	55
	.byte	-124
	.byte	61
	.byte	114
	.byte	70
	.byte	96
	.byte	74
	.byte	88
	.byte	75
	.byte	88
	.byte	87
	.byte	74
	.byte	89
	.byte	66
	.byte	91
	.byte	67
	.byte	100
	.byte	59
	.byte	108
	.byte	50
	.byte	120
	.byte	40
	.byte	122
	.byte	37
	.byte	97
	.byte	43
	.byte	78
	.byte	50
	.byte	83
	.byte	78
	.byte	84
	.byte	81
	.byte	88
	.byte	75
	.byte	86
	.byte	74
	.byte	87
	.byte	71
	.byte	90
	.byte	73
	.byte	93
	.byte	74
	.byte	93
	.byte	74
	.byte	109
	.byte	40
	.byte	114
	.byte	36
	.byte	117
	.byte	34
	.byte	117
	.byte	34
	.byte	-113
	.byte	17
	.byte	-111
	.byte	18
	.byte	-110
	.byte	19
	.byte	-94
	.byte	12
	.byte	-91
	.byte	10
	.byte	-78
	.byte	7
	.byte	-67
	.byte	6
	.byte	-66
	.byte	8
	.byte	-79
	.byte	9
	.byte	23
	.byte	-78
	.byte	54
	.byte	115
	.byte	63
	.byte	102
	.byte	66
	.byte	98
	.byte	69
	.byte	99
	.byte	74
	.byte	89
	.byte	71
	.byte	91
	.byte	73
	.byte	91
	.byte	78
	.byte	89
	.byte	86
	.byte	80
	.byte	92
	.byte	66
	.byte	93
	.byte	64
	.byte	102
	.byte	59
	.byte	103
	.byte	60
	.byte	104
	.byte	60
	.byte	117
	.byte	52
	.byte	123
	.byte	44
	.byte	-118
	.byte	35
	.byte	-123
	.byte	31
	.byte	97
	.byte	38
	.byte	77
	.byte	45
	.byte	61
	.byte	90
	.byte	93
	.byte	60
	.byte	105
	.byte	42
	.byte	107
	.byte	41
	.byte	110
	.byte	45
	.byte	116
	.byte	38
	.byte	113
	.byte	38
	.byte	112
	.byte	38
	.byte	124
	.byte	26
	.byte	-124
	.byte	27
	.byte	-120
	.byte	19
	.byte	-116
	.byte	20
	.byte	-101
	.byte	14
	.byte	-97
	.byte	16
	.byte	-98
	.byte	18
	.byte	-86
	.byte	13
	.byte	-79
	.byte	10
	.byte	-69
	.byte	8
	.byte	-64
	.byte	6
	.byte	-81
	.byte	9
	.byte	-97
	.byte	10
	.byte	21
	.byte	-78
	.byte	59
	.byte	110
	.byte	71
	.byte	86
	.byte	75
	.byte	85
	.byte	84
	.byte	83
	.byte	91
	.byte	66
	.byte	88
	.byte	73
	.byte	87
	.byte	72
	.byte	92
	.byte	75
	.byte	98
	.byte	72
	.byte	105
	.byte	58
	.byte	107
	.byte	54
	.byte	115
	.byte	52
	.byte	114
	.byte	55
	.byte	112
	.byte	56
	.byte	-127
	.byte	51
	.byte	-124
	.byte	40
	.byte	-106
	.byte	33
	.byte	-116
	.byte	29
	.byte	98
	.byte	35
	.byte	77
	.byte	42
	.byte	42
	.byte	121
	.byte	96
	.byte	66
	.byte	108
	.byte	43
	.byte	111
	.byte	40
	.byte	117
	.byte	44
	.byte	123
	.byte	32
	.byte	120
	.byte	36
	.byte	119
	.byte	33
	.byte	127
	.byte	33
	.byte	-122
	.byte	34
	.byte	-117
	.byte	21
	.byte	-109
	.byte	23
	.byte	-104
	.byte	20
	.byte	-98
	.byte	25
	.byte	-102
	.byte	26
	.byte	-90
	.byte	21
	.byte	-83
	.byte	16
	.byte	-72
	.byte	13
	.byte	-72
	.byte	10
	.byte	-106
	.byte	13
	.byte	-117
	.byte	15
	.byte	22
	.byte	-78
	.byte	63
	.byte	114
	.byte	74
	.byte	82
	.byte	84
	.byte	83
	.byte	92
	.byte	82
	.byte	103
	.byte	62
	.byte	96
	.byte	72
	.byte	96
	.byte	67
	.byte	101
	.byte	73
	.byte	107
	.byte	72
	.byte	113
	.byte	55
	.byte	118
	.byte	52
	.byte	125
	.byte	52
	.byte	118
	.byte	52
	.byte	117
	.byte	55
	.byte	-121
	.byte	49
	.byte	-119
	.byte	39
	.byte	-99
	.byte	32
	.byte	-111
	.byte	29
	.byte	97
	.byte	33
	.byte	77
	.byte	40
	.section	.rodata.beta_coef,"a"
	.align	4
	.type	beta_coef, @object
	.size	beta_coef, 8
beta_coef:
	.short	30147
	.short	22282
	.short	12124
	.short	6554
	.section	.rodata.pred_coef,"a"
	.align	4
	.type	pred_coef, @object
	.size	pred_coef, 8
pred_coef:
	.short	29440
	.short	26112
	.short	21248
	.short	16384
	.global	eMeans
	.section	.rodata.eMeans,"a"
	.align	4
	.type	eMeans, @object
	.size	eMeans, 25
eMeans:
	.byte	103
	.byte	100
	.byte	92
	.byte	85
	.byte	81
	.byte	77
	.byte	72
	.byte	70
	.byte	78
	.byte	75
	.byte	73
	.byte	71
	.byte	78
	.byte	74
	.byte	69
	.byte	72
	.byte	70
	.byte	74
	.byte	76
	.byte	71
	.byte	60
	.byte	60
	.byte	60
	.byte	60
	.byte	60
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
