# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/celt_lpc.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"celt_lpc.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\celt_lpc.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\celt_lpc.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\celt_lpc.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\celt_lpc.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\celt_lpc.c.s.raw
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
	.global	__divsi3
	.section	.text._celt_lpc,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, 163838
	.literal .LC2, -32767
	.literal .LC3, 65470
	.literal .LC4, 32768
	.literal .LC5, 4096
	.align	4
	.global	_celt_lpc
	.type	_celt_lpc, @function
# Function: _celt_lpc
# Module: upstream/celt/celt_lpc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif
# C context:
# C context: void _celt_lpc(
# C context: opus_val16       *_lpc, /* out: [0...p-1] LPC coefficients      */
# C context: const opus_val32 *ac,  /* in:  [0...p] autocorrelation values  */
# C context: int          p
# C context: )
_celt_lpc:
	movi	a9, 0xa0	#,
	sub	sp, sp, a9	#,,
	s32i	a4, sp, 112	# %sfp, p
	s32i	a13, sp, 148	#,
	mov.n	a13, a3	# ac, ac
# @OPUS@\upstream\celt\celt_lpc.c:106:    opus_val32 error = ac[0];
	l32i.n	a5, a13, 0	# *ac_205(D),
# @OPUS@\upstream\celt\celt_lpc.c:113:    OPUS_CLEAR(lpc, p);
	l32i	a3, sp, 112	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:103: {
	s32i	a2, sp, 120	# %sfp, _lpc
# @OPUS@\upstream\celt\celt_lpc.c:113:    OPUS_CLEAR(lpc, p);
	movi.n	a4, 4	#,
	mov.n	a2, sp	#,
# @OPUS@\upstream\celt\celt_lpc.c:103: {
	s32i	a0, sp, 156	#,
	s32i	a12, sp, 152	#,
	s32i	a14, sp, 144	#,
	s32i	a15, sp, 140	#,
# @OPUS@\upstream\celt\celt_lpc.c:106:    opus_val32 error = ac[0];
	s32i	a5, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:113:    OPUS_CLEAR(lpc, p);
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\celt_lpc.c:115:    if (ac[0] != 0)
	l32i.n	a2, a13, 0	# *ac_205(D), *ac_205(D)
	beqz.n	a2, .L2	# *ac_205(D),
# @OPUS@\upstream\celt\celt_lpc.c:120:       for (i = 0; i < p; i++) {
	l32i	a5, sp, 112	# %sfp,
	blti	a5, 1, .L1	#,,
	addi	a4, sp, -4	#,,
	s32i	a4, sp, 104	# %sfp,
	s32i	a13, sp, 100	# %sfp, ac
# @OPUS@\upstream\celt\celt_lpc.c:120:       for (i = 0; i < p; i++) {
	movi.n	a3, 0	# i,
	j	.L4		#
.L5:
# @OPUS@\upstream\celt\celt_lpc.c:124:             rr += MULT32_32_Q31(lpc[j],ac[i - j]);
	l32i.n	a4, a7, 0	# MEM[base: _767, offset: 0B], _3
	l32i.n	a3, a6, 0	# MEM[base: _766, offset: 0B], _11
	srai	a5, a4, 16	# _4, _3,
	srai	a8, a3, 16	# _12, _11,
	extui	a4, a4, 0, 16	# tmp243, _3,
	extui	a3, a3, 0, 16	# tmp240, _11,
	mull	a3, a3, a5	# tmp241, tmp240, _4
	mull	a4, a4, a8	# tmp244, tmp243, _12
	mull	a5, a5, a8	# tmp247, _4, _12
	srai	a3, a3, 15	# tmp242, tmp241,
	srai	a4, a4, 15	# tmp245, tmp244,
	add.n	a3, a3, a4	# tmp246, tmp242, tmp245
	slli	a5, a5, 1	# tmp248, tmp247,
	add.n	a3, a3, a5	# tmp249, tmp246, tmp248
	addi	a6, a6, -4	# ivtmp$121, ivtmp$121,
# @OPUS@\upstream\celt\celt_lpc.c:124:             rr += MULT32_32_Q31(lpc[j],ac[i - j]);
	add.n	a9, a9, a3	# rr, rr, tmp249
	addi.n	a7, a7, 4	# ivtmp$120, ivtmp$120,
# @OPUS@\upstream\celt\celt_lpc.c:123:          for (j = 0; j < i; j++)
	bne	a13, a6, .L5	# ac, ivtmp$121,
	j	.L34		#
.L35:
# @OPUS@\upstream\celt\celt_lpc.c:126:          r = -frac_div32(SHL32(rr,6), error);
	l32i	a3, sp, 96	# %sfp,
	slli	a2, a2, 6	#, _817,
	call0	frac_div32		#
# @OPUS@\upstream\celt\celt_lpc.c:126:          r = -frac_div32(SHL32(rr,6), error);
	neg	a2, a2	# r,
# @OPUS@\upstream\celt\celt_lpc.c:128:          lpc[i] = SHR32(r,6);
	l32i	a5, sp, 104	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:128:          lpc[i] = SHR32(r,6);
	srai	a3, a2, 6	# tmp251, r,
# @OPUS@\upstream\celt\celt_lpc.c:128:          lpc[i] = SHR32(r,6);
	s32i.n	a3, a5, 4	# MEM[base: _752, offset: 4B], tmp251
	srai	a7, a2, 16	# _38, r,
	extui	a8, a2, 0, 16	# prephitmp_846, r,
# @OPUS@\upstream\celt\celt_lpc.c:129:          for (j = 0; j < (i+1)>>1; j++)
	beqz.n	a14, .L9	# _819,
.L26:
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	l32i	a9, sp, 104	# %sfp, ivtmp$116
	srai	a7, a2, 16	# _38, r,
	extui	a8, a2, 0, 16	# prephitmp_846, r,
	mov.n	a10, sp	# ivtmp$115,
	movi.n	a15, 0	# j,
	s32i	a13, sp, 116	# %sfp, ac
.L8:
# @OPUS@\upstream\celt\celt_lpc.c:133:             tmp2 = lpc[i-1-j];
	l32i.n	a11, a9, 0	# MEM[base: _788, offset: 0B], tmp2
# @OPUS@\upstream\celt\celt_lpc.c:132:             tmp1 = lpc[j];
	l32i.n	a13, a10, 0	# MEM[base: _790, offset: 0B], tmp1
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	srai	a5, a11, 16	# _41, tmp2,
	extui	a6, a11, 0, 16	# tmp252, tmp2,
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	srai	a4, a13, 16	# _55, tmp1,
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	mull	a3, a5, a8	# tmp255, _41, prephitmp_846
	mull	a6, a6, a7	# tmp253, tmp252, _38
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	extui	a2, a13, 0, 16	# tmp262, tmp1,
	mull	a12, a4, a8	# tmp265, _55, prephitmp_846
	mull	a2, a2, a7	# tmp263, tmp262, _38
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	srai	a6, a6, 15	# tmp254, tmp253,
	srai	a3, a3, 15	# tmp256, tmp255,
	mull	a5, a7, a5	# tmp259, _38, _41
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	add.n	a3, a6, a3	# tmp257, tmp254, tmp256
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	srai	a2, a2, 15	# tmp264, tmp263,
	srai	a12, a12, 15	# tmp266, tmp265,
	mull	a4, a7, a4	# tmp269, _38, _55
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	add.n	a3, a3, a13	# tmp258, tmp257, tmp1
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	slli	a5, a5, 1	# tmp260, tmp259,
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	add.n	a2, a2, a12	# tmp267, tmp264, tmp266
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	add.n	a3, a3, a5	# tmp261, tmp258, tmp260
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	add.n	a11, a2, a11	# tmp268, tmp267, tmp2
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	slli	a4, a4, 1	# tmp270, tmp269,
# @OPUS@\upstream\celt\celt_lpc.c:134:             lpc[j]     = tmp1 + MULT32_32_Q31(r,tmp2);
	s32i.n	a3, a10, 0	# MEM[base: _790, offset: 0B], tmp261
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	add.n	a11, a11, a4	# tmp271, tmp268, tmp270
# @OPUS@\upstream\celt\celt_lpc.c:135:             lpc[i-1-j] = tmp2 + MULT32_32_Q31(r,tmp1);
	s32i.n	a11, a9, 0	# MEM[base: _788, offset: 0B], tmp271
# @OPUS@\upstream\celt\celt_lpc.c:129:          for (j = 0; j < (i+1)>>1; j++)
	addi.n	a15, a15, 1	# j, j,
	addi.n	a10, a10, 4	# ivtmp$115, ivtmp$115,
	addi	a9, a9, -4	# ivtmp$116, ivtmp$116,
# @OPUS@\upstream\celt\celt_lpc.c:129:          for (j = 0; j < (i+1)>>1; j++)
	blt	a15, a14, .L8	# j, _819,
	l32i	a13, sp, 116	# %sfp, ac
.L9:
# @OPUS@\upstream\celt\celt_lpc.c:138:          error = error - MULT32_32_Q31(MULT32_32_Q31(r,r),error);
	mull	a8, a7, a8	# tmp273, _38, prephitmp_846
	mull	a7, a7, a7	# tmp272, _38, _38
	srai	a8, a8, 15	# _86, tmp273,
	l32i	a2, sp, 96	# %sfp,
	add.n	a7, a8, a7	# tmp274, _86, tmp272
	slli	a7, a7, 1	# tmp275, tmp274,
	srai	a5, a2, 16	# _94,,
	srai	a3, a7, 16	# _91, tmp275,
	extui	a4, a2, 0, 16	# tmp284,,
	extui	a2, a7, 0, 16	# tmp281, tmp275
	mull	a2, a2, a5	# tmp282, tmp281, _94
	mull	a4, a4, a3	# tmp285, tmp284, _91
	srai	a2, a2, 15	# tmp283, tmp282,
	srai	a4, a4, 15	# tmp286, tmp285,
	mull	a3, a3, a5	# tmp288, _91, _94
	l32i	a5, sp, 96	# %sfp,
	add.n	a2, a2, a4	# tmp287, tmp283, tmp286
	sub	a2, a5, a2	# _254,, tmp287
# @OPUS@\upstream\celt\celt_lpc.c:141:          if (error<=SHR32(ac[0],10))
	l32i.n	a4, a13, 0	# *ac_205(D), *ac_205(D)
# @OPUS@\upstream\celt\celt_lpc.c:138:          error = error - MULT32_32_Q31(MULT32_32_Q31(r,r),error);
	slli	a3, a3, 1	# tmp289, tmp288,
# @OPUS@\upstream\celt\celt_lpc.c:138:          error = error - MULT32_32_Q31(MULT32_32_Q31(r,r),error);
	sub	a3, a2, a3	#, _254, tmp289
	s32i	a3, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:141:          if (error<=SHR32(ac[0],10))
	srai	a2, a4, 10	# tmp290, *ac_205(D),
# @OPUS@\upstream\celt\celt_lpc.c:141:          if (error<=SHR32(ac[0],10))
	bge	a2, a3, .L10	# tmp290,,
	l32i	a5, sp, 104	# %sfp,
	l32i	a4, sp, 100	# %sfp,
	addi.n	a5, a5, 4	#,,
	addi.n	a4, a4, 4	#,,
	s32i	a5, sp, 104	# %sfp,
	l32i	a3, sp, 108	# %sfp, i
# @OPUS@\upstream\celt\celt_lpc.c:120:       for (i = 0; i < p; i++) {
	l32i	a5, sp, 112	# %sfp,
	s32i	a4, sp, 100	# %sfp,
	beq	a5, a3, .L10	#, i,
.L4:
	l32i	a4, sp, 100	# %sfp,
	addi.n	a5, a3, 1	#, i,
	l32i.n	a2, a4, 4	# MEM[base: _757, offset: 4B], MEM[base: _757, offset: 4B]
	s32i	a5, sp, 108	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:122:          opus_val32 rr = 0;
	movi.n	a9, 0	# rr,
	srai	a2, a2, 6	# _817, MEM[base: _757, offset: 4B],
	srai	a14, a5, 1	# _819,,
	mov.n	a7, sp	# ivtmp$120,
# @OPUS@\upstream\celt\celt_lpc.c:123:          for (j = 0; j < i; j++)
	mov.n	a6, a4	# ivtmp$121,
	bne	a3, a9, .L5	# i,,
	j	.L35		#
.L23:
	l32i	a5, sp, 112	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:179:             lpc[p - 1] = MULT32_32_Q16(chirp_Q16, lpc[p - 1]);
	l32i	a4, sp, 100	# %sfp,
	slli	a12, a5, 2	# tmp294,,
	slli	a15, a4, 2	# tmp372,,
	addi	a5, sp, -4	#,,
# @OPUS@\upstream\celt\celt_lpc.c:120:       for (i = 0; i < p; i++) {
	movi.n	a14, 0	# idx,
	add.n	a12, a5, a12	# _807,, tmp294
# @OPUS@\upstream\celt\celt_lpc.c:179:             lpc[p - 1] = MULT32_32_Q16(chirp_Q16, lpc[p - 1]);
	add.n	a15, sp, a15	# tmp373,, tmp372
# @OPUS@\upstream\celt\celt_lpc.c:120:       for (i = 0; i < p; i++) {
	movi.n	a11, 9	# ivtmp$111,
# @OPUS@\upstream\celt\celt_lpc.c:179:             lpc[p - 1] = MULT32_32_Q16(chirp_Q16, lpc[p - 1]);
	mov.n	a10, a15	# tmp373, tmp373
	l32r	a13, .LC4	#, tmp371
	mov.n	a15, a14	# idx, idx
	mov.n	a14, a12	# _807, _807
	l32i	a12, sp, 112	# %sfp, p
	s32i	a11, sp, 96	# %sfp, ivtmp$111
.L24:
# @OPUS@\upstream\celt\celt_lpc.c:158:          maxabs = 0;
	movi.n	a5, 0	# maxabs,
# @OPUS@\upstream\celt\celt_lpc.c:120:       for (i = 0; i < p; i++) {
	mov.n	a4, sp	# ivtmp$109,
# @OPUS@\upstream\celt\celt_lpc.c:159:          for (i = 0; i < p; i++) {
	mov.n	a3, a5	# i, maxabs
.L14:
# @OPUS@\upstream\celt\celt_lpc.c:160:             absval = ABS32(lpc[i]);
	l32i.n	a2, a4, 0	# MEM[base: _803, offset: 0B], MEM[base: _803, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$109, ivtmp$109,
	abs	a2, a2	# absval, MEM[base: _803, offset: 0B]
# @OPUS@\upstream\celt\celt_lpc.c:161:             if (absval > maxabs) {
	bge	a5, a2, .L13	# maxabs, absval,
	mov.n	a15, a3	# idx, i
	mov.n	a5, a2	# maxabs, absval
.L13:
# @OPUS@\upstream\celt\celt_lpc.c:159:          for (i = 0; i < p; i++) {
	addi.n	a3, a3, 1	# i, i,
# @OPUS@\upstream\celt\celt_lpc.c:159:          for (i = 0; i < p; i++) {
	bne	a12, a3, .L14	# p, i,
# @OPUS@\upstream\celt\celt_lpc.c:166:          maxabs = PSHR32(maxabs, 13);  /* Q25->Q12 */
	addmi	a5, a5, 0x1000	# _116, maxabs,
# @OPUS@\upstream\celt\celt_lpc.c:168:          if (maxabs > 32767) {
	l32r	a2, .LC0	#,
# @OPUS@\upstream\celt\celt_lpc.c:166:          maxabs = PSHR32(maxabs, 13);  /* Q25->Q12 */
	srai	a5, a5, 13	# maxabs, _116,
# @OPUS@\upstream\celt\celt_lpc.c:168:          if (maxabs > 32767) {
	bge	a2, a5, .L36	#, maxabs,
# @OPUS@\upstream\celt\celt_lpc.c:169:             maxabs = MIN32(maxabs, 163838);
	l32r	a3, .LC1	#,
	bge	a3, a5, .L18	#, maxabs,
	mov.n	a5, a3	# maxabs,
.L18:
# @OPUS@\upstream\celt\celt_lpc.c:170:             chirp_Q16 = QCONST32(0.999, 16) - DIV32(SHL32(maxabs - 32767, 14),
	l32r	a4, .LC2	#,
	addi.n	a3, a15, 1	# tmp305, idx,
	mull	a3, a3, a5	# tmp306, tmp305, maxabs
	add.n	a2, a5, a4	# tmp302, maxabs,
	srai	a3, a3, 2	#, tmp306,
	slli	a2, a2, 14	#, tmp302,
	s32i	a10, sp, 124	#,
	call0	__divsi3		#
# @OPUS@\upstream\celt\celt_lpc.c:170:             chirp_Q16 = QCONST32(0.999, 16) - DIV32(SHL32(maxabs - 32767, 14),
	l32r	a5, .LC3	#,
# @OPUS@\upstream\celt\celt_lpc.c:175:             for (i = 0; i < p - 1; i++) {
	l32i	a4, sp, 100	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:172:             chirp_minus_one_Q16 = chirp_Q16 - 65536;
	movi	a3, -0x42	#,
# @OPUS@\upstream\celt\celt_lpc.c:170:             chirp_Q16 = QCONST32(0.999, 16) - DIV32(SHL32(maxabs - 32767, 14),
	sub	a6, a5, a2	# chirp_Q16,, tmp310
# @OPUS@\upstream\celt\celt_lpc.c:175:             for (i = 0; i < p - 1; i++) {
	l32i	a10, sp, 124	#,
# @OPUS@\upstream\celt\celt_lpc.c:172:             chirp_minus_one_Q16 = chirp_Q16 - 65536;
	sub	a2, a3, a2	# chirp_minus_one_Q16,, tmp310
# @OPUS@\upstream\celt\celt_lpc.c:175:             for (i = 0; i < p - 1; i++) {
	blti	a4, 1, .L19	#,,
	mov.n	a7, sp	# ivtmp$106,
.L20:
# @OPUS@\upstream\celt\celt_lpc.c:176:                lpc[i] = MULT32_32_Q16(chirp_Q16, lpc[i]);
	l32i.n	a5, a7, 0	# MEM[base: _824, offset: 0B], _127
	srai	a4, a6, 16	# _137, chirp_Q16,
	extui	a8, a6, 0, 16	# tmp313, chirp_Q16,
	srai	a11, a5, 16	# _133, _127,
	extui	a5, a5, 0, 16	# tmp315, _127,
	mull	a9, a5, a4	# tmp316, tmp315, _137
	mull	a3, a8, a11	# tmp314, tmp313, _133
	mull	a8, a8, a5	# tmp320, tmp313, tmp315
	mull	a4, a11, a4	# tmp323, _133, _137
# @OPUS@\upstream\celt\celt_lpc.c:177:                chirp_Q16 += PSHR32(MULT32_32_32(chirp_Q16, chirp_minus_one_Q16), 16);
	mull	a5, a2, a6	# tmp326, chirp_minus_one_Q16, chirp_Q16
# @OPUS@\upstream\celt\celt_lpc.c:176:                lpc[i] = MULT32_32_Q16(chirp_Q16, lpc[i]);
	add.n	a3, a3, a9	# tmp317, tmp314, tmp316
	extui	a8, a8, 16, 16	# tmp321, tmp320,
	add.n	a3, a3, a8	# tmp322, tmp317, tmp321
	slli	a4, a4, 16	# tmp324, tmp323,
	add.n	a3, a3, a4	# tmp325, tmp322, tmp324
# @OPUS@\upstream\celt\celt_lpc.c:177:                chirp_Q16 += PSHR32(MULT32_32_32(chirp_Q16, chirp_minus_one_Q16), 16);
	add.n	a5, a5, a13	# tmp327, tmp326, tmp371
# @OPUS@\upstream\celt\celt_lpc.c:176:                lpc[i] = MULT32_32_Q16(chirp_Q16, lpc[i]);
	s32i.n	a3, a7, 0	# MEM[base: _824, offset: 0B], tmp325
# @OPUS@\upstream\celt\celt_lpc.c:177:                chirp_Q16 += PSHR32(MULT32_32_32(chirp_Q16, chirp_minus_one_Q16), 16);
	srai	a5, a5, 16	# _150, tmp327,
	addi.n	a7, a7, 4	# ivtmp$106, ivtmp$106,
# @OPUS@\upstream\celt\celt_lpc.c:177:                chirp_Q16 += PSHR32(MULT32_32_32(chirp_Q16, chirp_minus_one_Q16), 16);
	add.n	a6, a6, a5	# chirp_Q16, chirp_Q16, _150
# @OPUS@\upstream\celt\celt_lpc.c:175:             for (i = 0; i < p - 1; i++) {
	bne	a14, a7, .L20	# _807, ivtmp$106,
.L19:
# @OPUS@\upstream\celt\celt_lpc.c:179:             lpc[p - 1] = MULT32_32_Q16(chirp_Q16, lpc[p - 1]);
	l32i.n	a7, a10, 0	# lpc, _154
	srai	a4, a6, 16	# _164, chirp_Q16,
	srai	a3, a7, 16	# _160, _154,
	extui	a6, a6, 0, 16	# tmp333, chirp_Q16,
	extui	a7, a7, 0, 16	# tmp335, _154,
	mull	a2, a6, a3	# tmp334, tmp333, _160
	mull	a5, a7, a4	# tmp336, tmp335, _164
	mull	a6, a6, a7	# tmp340, tmp333, tmp335
	mull	a3, a3, a4	# tmp343, _160, _164
	add.n	a2, a2, a5	# tmp337, tmp334, tmp336
	extui	a6, a6, 16, 16	# tmp341, tmp340,
	add.n	a6, a2, a6	# tmp342, tmp337, tmp341
	slli	a3, a3, 16	# tmp344, tmp343,
	add.n	a6, a6, a3	# tmp345, tmp342, tmp344
# @OPUS@\upstream\celt\celt_lpc.c:157:       for (iter = 0; iter < 10; iter++) {
	l32i	a5, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:179:             lpc[p - 1] = MULT32_32_Q16(chirp_Q16, lpc[p - 1]);
	s32i.n	a6, a10, 0	# lpc, tmp345
# @OPUS@\upstream\celt\celt_lpc.c:157:       for (iter = 0; iter < 10; iter++) {
	bnez.n	a5, .L21	#,
	j	.L37		#
.L2:
# @OPUS@\upstream\celt\celt_lpc.c:175:             for (i = 0; i < p - 1; i++) {
	l32i	a4, sp, 112	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:159:          for (i = 0; i < p; i++) {
	l32i	a5, sp, 112	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:175:             for (i = 0; i < p - 1; i++) {
	addi.n	a4, a4, -1	#,,
	s32i	a4, sp, 100	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:159:          for (i = 0; i < p; i++) {
	bgei	a5, 1, .L23	#,,
	j	.L1		#
.L21:
	addi.n	a4, a5, -1	#, tmp4,
	s32i	a4, sp, 96	# %sfp,
	j	.L24		#
.L25:
# @OPUS@\upstream\celt\celt_lpc.c:192:             _lpc[i] = EXTRACT16(PSHR32(lpc[i], 13));  /* Q25->Q12 */
	l32i.n	a2, a4, 0	# MEM[base: _138, offset: 0B], MEM[base: _138, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$101, ivtmp$101,
	addmi	a2, a2, 0x1000	# tmp346, MEM[base: _138, offset: 0B],
	srai	a2, a2, 13	# tmp348, tmp346,
	s16i	a2, a3, 0	# MEM[base: _92, offset: 0B], tmp348
	addi.n	a3, a3, 2	# ivtmp$102, ivtmp$102,
# @OPUS@\upstream\celt\celt_lpc.c:191:          for (i = 0; i < p; i++) {
	bne	a5, a3, .L25	# _194, ivtmp$102,
	j	.L1		#
.L37:
# @OPUS@\upstream\celt\celt_lpc.c:188:          OPUS_CLEAR(lpc, p);
	l32i	a3, sp, 112	# %sfp,
	mov.n	a2, sp	#,
	movi.n	a4, 4	#,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\celt_lpc.c:189:          _lpc[0] = 4096;  /* Q12 */
	l32r	a2, .LC5	#,
	l32i	a5, sp, 120	# %sfp,
	s16i	a2, a5, 0	# *_lpc_238(D),
	j	.L1		#
.L34:
# @OPUS@\upstream\celt\celt_lpc.c:125:          rr += SHR32(ac[i + 1],6);
	add.n	a2, a9, a2	# rr, rr, _817
# @OPUS@\upstream\celt\celt_lpc.c:126:          r = -frac_div32(SHL32(rr,6), error);
	l32i	a3, sp, 96	# %sfp,
	slli	a2, a2, 6	#, rr,
	call0	frac_div32		#
# @OPUS@\upstream\celt\celt_lpc.c:126:          r = -frac_div32(SHL32(rr,6), error);
	neg	a2, a2	# r,
# @OPUS@\upstream\celt\celt_lpc.c:128:          lpc[i] = SHR32(r,6);
	l32i	a4, sp, 104	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:128:          lpc[i] = SHR32(r,6);
	srai	a3, a2, 6	# tmp352, r,
# @OPUS@\upstream\celt\celt_lpc.c:128:          lpc[i] = SHR32(r,6);
	s32i.n	a3, a4, 4	# MEM[base: _753, offset: 4B], tmp352
	j	.L26		#
.L36:
	l32i	a2, sp, 112	# %sfp,
	l32i	a3, sp, 120	# %sfp, ivtmp$102
	slli	a5, a2, 1	# tmp353,,
	mov.n	a4, sp	# ivtmp$101,
	add.n	a5, a3, a5	# _194, ivtmp$102, tmp353
	j	.L25		#
.L10:
# @OPUS@\upstream\celt\celt_lpc.c:175:             for (i = 0; i < p - 1; i++) {
	l32i	a4, sp, 112	# %sfp,
	addi.n	a4, a4, -1	#,,
	s32i	a4, sp, 100	# %sfp,
	j	.L23		#
.L1:
# @OPUS@\upstream\celt\celt_lpc.c:197: }
	l32i	a0, sp, 156	#,
	movi	a9, 0xa0	#,
	l32i	a12, sp, 152	#,
	l32i	a13, sp, 148	#,
	l32i	a14, sp, 144	#,
	l32i	a15, sp, 140	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	_celt_lpc, .-_celt_lpc
	.section	.text.celt_fir_c,"ax",@progbits
	.literal_position
	.literal .LC6, 32767
	.literal .LC7, -32767
	.align	4
	.global	celt_fir_c
	.type	celt_fir_c, @function
# Function: celt_fir_c
# Module: upstream/celt/celt_lpc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context:
# C context: void celt_fir_c(
# C context: const opus_val16 *x,
# C context: const opus_val16 *num,
# C context: opus_val16 *y,
# C context: int N,
celt_fir_c:
	movi	a9, 0x90	#,
	sub	sp, sp, a9	#,,
	s32i	a6, sp, 76	# %sfp, ord
	s32i	a0, sp, 140	#,
	s32i	a12, sp, 136	#,
	s32i	a4, sp, 100	# %sfp, y
	s32i	a5, sp, 96	# %sfp, N
	s32i	a13, sp, 132	#,
	s32i	a14, sp, 128	#,
	s32i	a15, sp, 124	#,
# @OPUS@\upstream\celt\celt_lpc.c:207: {
	s32i	a2, sp, 92	# %sfp, x
	mov.n	a12, a3	# num, num
# @OPUS@\upstream\celt\celt_lpc.c:210:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\celt\celt_lpc.c:212:    ALLOC(rnum, ord, opus_val16);
	l32i	a2, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:210:    SAVE_STACK;
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\celt_lpc.c:212:    ALLOC(rnum, ord, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_lpc.c:213:    for(i=0;i<ord;i++)
	l32i	a6, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:212:    ALLOC(rnum, ord, opus_val16);
	s32i	a2, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:213:    for(i=0;i<ord;i++)
	bgei	a6, 1, .L41	#,,
.L45:
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	l32i	a7, sp, 96	# %sfp,
	addi	a7, a7, -3	#,,
	s32i	a7, sp, 88	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	bgei	a7, 1, .L42	#,,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	movi.n	a9, 0	#,
	s32i	a9, sp, 80	# %sfp,
	j	.L43		#
.L41:
	mov.n	a3, a2	# ivtmp$169,
	slli	a2, a6, 1	# tmp208, tmp10,
	addi	a2, a2, -2	# tmp210, tmp208,
	add.n	a2, a12, a2	# ivtmp$167, num, tmp210
	j	.L44		#
.L62:
	mov.n	a2, a5	# ivtmp$167, ivtmp$167
.L44:
# @OPUS@\upstream\celt\celt_lpc.c:214:       rnum[i] = num[ord-i-1];
	l16si	a4, a2, 0	# MEM[base: _500, offset: 0B], _10
	addi	a5, a2, -2	# ivtmp$167, ivtmp$167,
# @OPUS@\upstream\celt\celt_lpc.c:214:       rnum[i] = num[ord-i-1];
	s16i	a4, a3, 0	# MEM[base: _499, offset: 0B], _10
	addi.n	a3, a3, 2	# ivtmp$169, ivtmp$169,
# @OPUS@\upstream\celt\celt_lpc.c:213:    for(i=0;i<ord;i++)
	bne	a12, a2, .L62	# num, ivtmp$167,
	j	.L45		#
.L42:
	l32i	a6, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	movi.n	a2, 0	#,
	l32i	a10, sp, 92	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi	a9, a6, -3	#,,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	s32i	a2, sp, 80	# %sfp,
	l32r	a7, .LC6	#,
	slli	a2, a6, 1	# tmp215,,
	l32i	a6, sp, 100	# %sfp,
	sub	a2, a10, a2	#,, tmp215
	s32i.n	a7, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i	a9, sp, 72	# %sfp,
	s32i	a10, sp, 68	# %sfp,
	s32i	a2, sp, 64	# %sfp,
	s32i.n	a6, sp, 60	# %sfp,
.L55:
# @OPUS@\upstream\celt\celt_lpc.c:218:       sum[0] = SHL32(EXTEND32(x[i  ]), SIG_SHIFT);
	l32i	a7, sp, 68	# %sfp,
	l32i	a9, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:221:       sum[3] = SHL32(EXTEND32(x[i+3]), SIG_SHIFT);
	l16si	a2, a7, 6	# MEM[base: _524, offset: 6B], tmp226
# @OPUS@\upstream\celt\celt_lpc.c:218:       sum[0] = SHL32(EXTEND32(x[i  ]), SIG_SHIFT);
	l16si	a5, a7, 0	# MEM[base: _524, offset: 0B], tmp217
# @OPUS@\upstream\celt\celt_lpc.c:219:       sum[1] = SHL32(EXTEND32(x[i+1]), SIG_SHIFT);
	l16si	a4, a7, 2	# MEM[base: _524, offset: 2B], tmp220
# @OPUS@\upstream\celt\celt_lpc.c:220:       sum[2] = SHL32(EXTEND32(x[i+2]), SIG_SHIFT);
	l16si	a3, a7, 4	# MEM[base: _524, offset: 4B], tmp223
# @OPUS@\upstream\celt\celt_lpc.c:221:       sum[3] = SHL32(EXTEND32(x[i+3]), SIG_SHIFT);
	slli	a2, a2, 12	#, tmp226,
# @OPUS@\upstream\celt\pitch.h:72:    y_1=*y++;
	l32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:218:       sum[0] = SHL32(EXTEND32(x[i  ]), SIG_SHIFT);
	slli	a5, a5, 12	#, tmp217,
# @OPUS@\upstream\celt\celt_lpc.c:219:       sum[1] = SHL32(EXTEND32(x[i+1]), SIG_SHIFT);
	slli	a4, a4, 12	#, tmp220,
# @OPUS@\upstream\celt\celt_lpc.c:220:       sum[2] = SHL32(EXTEND32(x[i+2]), SIG_SHIFT);
	slli	a3, a3, 12	#, tmp223,
# @OPUS@\upstream\celt\celt_lpc.c:221:       sum[3] = SHL32(EXTEND32(x[i+3]), SIG_SHIFT);
	s32i.n	a2, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a2, sp, 72	# %sfp,
	addi.n	a15, a9, 6	# ivtmp$152,,
# @OPUS@\upstream\celt\celt_lpc.c:218:       sum[0] = SHL32(EXTEND32(x[i  ]), SIG_SHIFT);
	s32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:219:       sum[1] = SHL32(EXTEND32(x[i+1]), SIG_SHIFT);
	s32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:220:       sum[2] = SHL32(EXTEND32(x[i+2]), SIG_SHIFT);
	s32i.n	a3, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:71:    y_0=*y++;
	l16si	a9, a9, 0	# MEM[base: _520, offset: 0B], y_0
# @OPUS@\upstream\celt\pitch.h:72:    y_1=*y++;
	l16si	a14, a10, 2	# MEM[base: _520, offset: 2B], y_1
	mov.n	a6, a15	# y, ivtmp$152
# @OPUS@\upstream\celt\pitch.h:73:    y_2=*y++;
	l16si	a13, a10, 4	# MEM[base: _520, offset: 4B], y_2
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blti	a2, 1, .L63	#,,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	movi.n	a4, 0	#,
	mov.n	a11, a14	# y_1, y_1
	l32i	a3, sp, 84	# %sfp, ivtmp$153
	s32i.n	a4, sp, 44	# %sfp,
	mov.n	a14, a9	# y_0, y_0
	j	.L47		#
.L64:
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i.n	a5, sp, 44	# %sfp, j
.L47:
# @OPUS@\upstream\celt\pitch.h:77:       tmp = *x++;
	l16si	a6, a3, 0	# MEM[base: _561, offset: 0B], tmp
# @OPUS@\upstream\celt\pitch.h:83:       tmp=*x++;
	l16si	a2, a3, 2	# MEM[base: _561, offset: 2B], tmp
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	mull	a14, a6, a14	#, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a12, a15, 0	# MEM[base: _546, offset: 0B], prephitmp_591
# @OPUS@\upstream\celt\pitch.h:89:       tmp=*x++;
	l16si	a5, a3, 4	# MEM[base: _561, offset: 4B], tmp
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a14, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	mull	a9, a11, a2	#, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:84:       y_0=*y++;
	l16si	a14, a15, 2	# MEM[base: _546, offset: 2B], y_0
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i	a9, sp, 104	# %sfp,
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a7, a14, a5	#, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a9, a12, a5	#, prephitmp_591, tmp
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a11, a6, a11	#, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	s32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i	a9, sp, 108	# %sfp,
	l32i	a7, sp, 104	# %sfp,
	l32i.n	a9, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a10, a13, a5	#, y_2, tmp
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i.n	a11, sp, 20	# %sfp,
	add.n	a7, a7, a9	#,,
# @OPUS@\upstream\celt\pitch.h:95:       tmp=*x++;
	l16si	a4, a3, 6	# MEM[base: _561, offset: 6B], tmp
	s32i.n	a3, sp, 40	# %sfp, ivtmp$153
# @OPUS@\upstream\celt\pitch.h:86:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a8, a13, a2	# tmp245, y_2, tmp
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i.n	a10, sp, 52	# %sfp,
	s32i	a7, sp, 104	# %sfp,
# @OPUS@\upstream\celt\pitch.h:81:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a10, a6, a13	# tmp251, tmp, y_2
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.h:87:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a12, a2	# tmp252, prephitmp_591, tmp
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a6, a6, a12	# tmp267, tmp, prephitmp_591
# @OPUS@\upstream\celt\pitch.h:88:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a14	# tmp268, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:90:       y_1=*y++;
	l16si	a11, a15, 4	# MEM[base: _546, offset: 4B], y_1
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	mull	a9, a12, a4	#, prephitmp_591, tmp
	add.n	a8, a7, a8	# _5,, tmp245
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a6, a2	# tmp269, tmp267, tmp268
	l32i	a7, sp, 104	# %sfp,
	l32i.n	a6, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:96:       y_2=*y++;
	l16si	a13, a15, 6	# MEM[base: _546, offset: 6B], y_2
	add.n	a3, a10, a3	# tmp253, tmp251, tmp252
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	mull	a10, a14, a4	#, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a9, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:94:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mull	a5, a5, a11	# tmp270, tmp, y_1
	add.n	a9, a6, a7	# _11,,
	l32i.n	a6, sp, 56	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	s32i.n	a10, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	mull	a10, a11, a4	# tmp265, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	mull	a4, a4, a13	# tmp272, tmp, y_2
	add.n	a3, a3, a6	# _4, tmp253,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i	a7, sp, 108	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a2, a5	# tmp271, tmp269, tmp270
	l32i.n	a5, sp, 40	# %sfp,
	add.n	a2, a2, a4	# tmp273, tmp271, tmp272
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a4, sp, 32	# %sfp,
	add.n	a9, a6, a9	# tmp260,, _11
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a8, a7, a8	# tmp262,, _5
	addi.n	a7, a5, 8	# x,,
	l32i.n	a5, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	add.n	a4, a4, a9	#,, tmp260
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i.n	a9, sp, 28	# %sfp,
	add.n	a8, a8, a5	# tmp264, tmp262,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a9, a9, a8	#,, tmp264
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i.n	a6, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	s32i.n	a9, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	l32i.n	a4, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	l32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	add.n	a10, a10, a3	# tmp266, tmp265, _4
	add.n	a4, a4, a10	#,, tmp266
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a9, a9, a2	#,, tmp273
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a10, sp, 72	# %sfp,
	addi.n	a15, a15, 8	# ivtmp$152, ivtmp$152,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi.n	a5, a6, 4	# j,,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	s32i.n	a4, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	s32i.n	a9, sp, 36	# %sfp,
	mov.n	a3, a7	# ivtmp$153, x
	mov.n	a6, a15	# y, ivtmp$152
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blt	a5, a10, .L64	# j,,
	l32i.n	a2, sp, 44	# %sfp,
	mov.n	a9, a14	# y_0, y_0
	addi.n	a3, a2, 5	# _587,,
	mov.n	a14, a11	# y_1, y_1
	addi.n	a8, a2, 6	# _589,,
	j	.L46		#
.L63:
	movi.n	a12, 0	# prephitmp_591,
	l32i	a7, sp, 84	# %sfp, x
	movi.n	a8, 2	# _589,
	movi.n	a3, 1	# _587,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	mov.n	a5, a12	# j, prephitmp_591
.L46:
# @OPUS@\upstream\celt\pitch.h:102:    if (j++<len)
	l32i	a10, sp, 76	# %sfp,
	bge	a5, a10, .L48	# j,,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	l16si	a2, a7, 0	# *x_313, tmp
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	l32i.n	a10, sp, 32	# %sfp,
	mull	a6, a2, a9	# tmp278, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a4, a2, a13	# tmp280, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	add.n	a10, a10, a6	#,, tmp278
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a12, a15, 0	# *y_319, prephitmp_591
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	l32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a5, a2, a14	# tmp279, tmp, y_1
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	add.n	a10, a10, a4	#,, tmp280
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a2, a2, a12	# tmp281, tmp, prephitmp_591
	l32i.n	a4, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	add.n	a6, a6, a5	#,, tmp279
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	add.n	a4, a4, a2	#,, tmp281
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	s32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	s32i.n	a4, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:105:       y_3=*y++;
	addi.n	a6, a15, 2	# y, ivtmp$152,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	addi.n	a7, a7, 2	# x, x,
.L48:
# @OPUS@\upstream\celt\pitch.h:111:    if (j++<len)
	l32i	a10, sp, 76	# %sfp,
	bge	a3, a10, .L49	# _587,,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_227, tmp
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	l32i.n	a10, sp, 32	# %sfp,
	mull	a5, a2, a14	# tmp286, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a2, a12	# tmp288, tmp, prephitmp_591
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	add.n	a10, a10, a5	#,, tmp286
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	l16si	a9, a6, 0	# *y_230, y_0
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	l32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a4, a2, a13	# tmp287, tmp, y_2
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	add.n	a10, a10, a3	#,, tmp288
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a9	# tmp289, tmp, y_0
	l32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	add.n	a5, a5, a4	#,, tmp287
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	add.n	a3, a3, a2	#,, tmp289
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	s32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	s32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	s32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	addi.n	a6, a6, 2	# y, y,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	addi.n	a7, a7, 2	# x, x,
.L49:
# @OPUS@\upstream\celt\pitch.h:120:    if (j<len)
	l32i	a10, sp, 76	# %sfp,
	bge	a8, a10, .L50	# _589,,
# @OPUS@\upstream\celt\pitch.h:122:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_251, tmp
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	l16ui	a3, a6, 0	# *y_253,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a4, a2, a13	# tmp292, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a5, a2, a12	# tmp293, tmp, prephitmp_591
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a6, a2, a9	# tmp294, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mul16s	a2, a3, a2	# tmp295, *y_253, tmp
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	l32i.n	a3, sp, 32	# %sfp,
	add.n	a3, a3, a4	#,, tmp292
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	l32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	add.n	a4, a4, a5	#,, tmp293
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	l32i.n	a5, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	add.n	a5, a5, a6	#,, tmp294
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	l32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	s32i.n	a5, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	add.n	a6, a6, a2	#,, tmp295
	s32i.n	a6, sp, 36	# %sfp,
.L50:
# @OPUS@\upstream\celt\celt_lpc.c:233:       y[i  ] = SROUND16(sum[0], SIG_SHIFT);
	l32i.n	a7, sp, 32	# %sfp,
	l32i.n	a3, sp, 48	# %sfp, iftmp$15_87
	addmi	a2, a7, 0x800	# tmp297,,
	srai	a2, a2, 12	# _44, tmp297,
	blt	a3, a2, .L51	# iftmp$15_87, _44,
# @OPUS@\upstream\celt\celt_lpc.c:233:       y[i  ] = SROUND16(sum[0], SIG_SHIFT);
	l32r	a3, .LC7	#, iftmp$15_87
	blt	a2, a3, .L51	# _44, tmp9,
# @OPUS@\upstream\celt\celt_lpc.c:233:       y[i  ] = SROUND16(sum[0], SIG_SHIFT);
	slli	a3, a2, 16	# tmp300, _44,
	srai	a3, a3, 16	# iftmp$15_87, tmp300,
.L51:
# @OPUS@\upstream\celt\celt_lpc.c:234:       y[i+1] = SROUND16(sum[1], SIG_SHIFT);
	l32i.n	a10, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:233:       y[i  ] = SROUND16(sum[0], SIG_SHIFT);
	l32i.n	a4, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:234:       y[i+1] = SROUND16(sum[1], SIG_SHIFT);
	addmi	a2, a10, 0x800	# tmp301,,
# @OPUS@\upstream\celt\celt_lpc.c:233:       y[i  ] = SROUND16(sum[0], SIG_SHIFT);
	s16i	a3, a4, 0	# MEM[base: _517, offset: 0B], iftmp$15_87
# @OPUS@\upstream\celt\celt_lpc.c:234:       y[i+1] = SROUND16(sum[1], SIG_SHIFT);
	l32i.n	a3, sp, 48	# %sfp, iftmp$18_88
	srai	a2, a2, 12	# _48, tmp301,
	blt	a3, a2, .L52	# iftmp$18_88, _48,
# @OPUS@\upstream\celt\celt_lpc.c:234:       y[i+1] = SROUND16(sum[1], SIG_SHIFT);
	l32r	a3, .LC7	#, iftmp$18_88
	blt	a2, a3, .L52	# _48, tmp5,
# @OPUS@\upstream\celt\celt_lpc.c:234:       y[i+1] = SROUND16(sum[1], SIG_SHIFT);
	slli	a2, a2, 16	# tmp304, _48,
	srai	a3, a2, 16	# iftmp$18_88, tmp304,
.L52:
# @OPUS@\upstream\celt\celt_lpc.c:235:       y[i+2] = SROUND16(sum[2], SIG_SHIFT);
	l32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:234:       y[i+1] = SROUND16(sum[1], SIG_SHIFT);
	l32i.n	a7, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:235:       y[i+2] = SROUND16(sum[2], SIG_SHIFT);
	addmi	a2, a6, 0x800	# tmp305,,
# @OPUS@\upstream\celt\celt_lpc.c:234:       y[i+1] = SROUND16(sum[1], SIG_SHIFT);
	s16i	a3, a7, 2	# MEM[base: _517, offset: 2B], iftmp$18_88
# @OPUS@\upstream\celt\celt_lpc.c:235:       y[i+2] = SROUND16(sum[2], SIG_SHIFT);
	l32i.n	a3, sp, 48	# %sfp, iftmp$21_89
	srai	a2, a2, 12	# _52, tmp305,
	blt	a3, a2, .L53	# iftmp$21_89, _52,
# @OPUS@\upstream\celt\celt_lpc.c:235:       y[i+2] = SROUND16(sum[2], SIG_SHIFT);
	l32r	a3, .LC7	#, iftmp$21_89
	blt	a2, a3, .L53	# _52, tmp9,
# @OPUS@\upstream\celt\celt_lpc.c:235:       y[i+2] = SROUND16(sum[2], SIG_SHIFT);
	slli	a2, a2, 16	# tmp308, _52,
	srai	a3, a2, 16	# iftmp$21_89, tmp308,
.L53:
# @OPUS@\upstream\celt\celt_lpc.c:236:       y[i+3] = SROUND16(sum[3], SIG_SHIFT);
	l32i.n	a10, sp, 36	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:235:       y[i+2] = SROUND16(sum[2], SIG_SHIFT);
	l32i.n	a4, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:236:       y[i+3] = SROUND16(sum[3], SIG_SHIFT);
	addmi	a2, a10, 0x800	# tmp309,,
# @OPUS@\upstream\celt\celt_lpc.c:235:       y[i+2] = SROUND16(sum[2], SIG_SHIFT);
	s16i	a3, a4, 4	# MEM[base: _517, offset: 4B], iftmp$21_89
# @OPUS@\upstream\celt\celt_lpc.c:236:       y[i+3] = SROUND16(sum[3], SIG_SHIFT);
	l32i.n	a3, sp, 48	# %sfp, iftmp$24_90
	srai	a2, a2, 12	# _56, tmp309,
	blt	a3, a2, .L54	# iftmp$24_90, _56,
# @OPUS@\upstream\celt\celt_lpc.c:236:       y[i+3] = SROUND16(sum[3], SIG_SHIFT);
	l32r	a3, .LC7	#, iftmp$24_90
	blt	a2, a3, .L54	# _56, iftmp$24_90,
# @OPUS@\upstream\celt\celt_lpc.c:236:       y[i+3] = SROUND16(sum[3], SIG_SHIFT);
	slli	a2, a2, 16	# tmp312, _56,
	srai	a3, a2, 16	# iftmp$24_90, tmp312,
.L54:
# @OPUS@\upstream\celt\celt_lpc.c:236:       y[i+3] = SROUND16(sum[3], SIG_SHIFT);
	l32i.n	a5, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	l32i	a6, sp, 80	# %sfp,
	l32i	a7, sp, 68	# %sfp,
	l32i	a9, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:236:       y[i+3] = SROUND16(sum[3], SIG_SHIFT);
	s16i	a3, a5, 6	# MEM[base: _517, offset: 6B], iftmp$24_90
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	addi.n	a6, a6, 4	#,,
	addi.n	a7, a7, 8	#,,
	addi.n	a9, a9, 8	#,,
	addi.n	a5, a5, 8	#,,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	l32i	a10, sp, 88	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	s32i	a6, sp, 80	# %sfp,
	s32i	a7, sp, 68	# %sfp,
	s32i	a9, sp, 64	# %sfp,
	s32i.n	a5, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:215:    for (i=0;i<N-3;i+=4)
	blt	a6, a10, .L55	#,,
.L43:
# @OPUS@\upstream\celt\celt_lpc.c:238:    for (;i<N;i++)
	l32i	a2, sp, 80	# %sfp,
	l32i	a5, sp, 96	# %sfp,
	blt	a2, a5, .L56	#,,
.L61:
# @OPUS@\upstream\celt\celt_lpc.c:245:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_lpc.c:246: }
	l32i	a0, sp, 140	#,
	movi	a9, 0x90	#,
	l32i	a12, sp, 136	#,
	l32i	a13, sp, 132	#,
	l32i	a14, sp, 128	#,
	l32i	a15, sp, 124	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L56:
	mov.n	a7, a5	#,
	slli	a9, a7, 1	# tmp313,,
	l32i	a6, sp, 76	# %sfp,
	l32r	a7, .LC6	#,
	slli	a5, a2, 1	# _599, tmp6,
	slli	a10, a6, 1	# tmp316,,
	s32i.n	a7, sp, 48	# %sfp,
	l32i	a2, sp, 92	# %sfp,
	l32i	a4, sp, 84	# %sfp,
	l32i	a3, sp, 100	# %sfp,
	mov.n	a6, a10	# tmp318, tmp316
# @OPUS@\upstream\celt\celt_lpc.c:243:       y[i] = SROUND16(sum, SIG_SHIFT);
	l32r	a8, .LC7	#, tmp361
	l32i	a12, sp, 76	# %sfp, ord
	l32i.n	a11, sp, 48	# %sfp, tmp329
	add.n	a7, a2, a5	# ivtmp$141,, _599
	add.n	a9, a2, a9	# _576,, tmp313
	add.n	a5, a3, a5	# ivtmp$142,, _599
	neg	a10, a10	# tmp317, tmp316
	add.n	a6, a4, a6	# _604,, tmp318
	mov.n	a13, a4	# rnum,
.L60:
# @OPUS@\upstream\celt\celt_lpc.c:240:       opus_val32 sum = SHL32(EXTEND32(x[i]), SIG_SHIFT);
	l16si	a4, a7, 0	# MEM[base: _585, offset: 0B], tmp319
	slli	a4, a4, 12	# sum, tmp319,
# @OPUS@\upstream\celt\celt_lpc.c:241:       for (j=0;j<ord;j++)
	blti	a12, 1, .L57	# ord,,
	add.n	a14, a10, a7	# ivtmp$136, tmp317, ivtmp$141
	mov.n	a2, a13	# ivtmp$135, rnum
.L58:
# @OPUS@\upstream\celt\celt_lpc.c:242:          sum = MAC16_16(sum,rnum[j],x[i+j-ord]);
	l16ui	a3, a2, 0	# MEM[base: _609, offset: 0B],
	l16ui	a15, a14, 0	# MEM[base: _608, offset: 0B],
	addi.n	a2, a2, 2	# ivtmp$135, ivtmp$135,
	mul16s	a3, a3, a15	# tmp322, MEM[base: _609, offset: 0B], MEM[base: _608, offset: 0B]
	addi.n	a14, a14, 2	# ivtmp$136, ivtmp$136,
# @OPUS@\upstream\celt\celt_lpc.c:242:          sum = MAC16_16(sum,rnum[j],x[i+j-ord]);
	add.n	a4, a4, a3	# sum, sum, tmp322
# @OPUS@\upstream\celt\celt_lpc.c:241:       for (j=0;j<ord;j++)
	bne	a6, a2, .L58	# _604, ivtmp$135,
.L57:
# @OPUS@\upstream\celt\celt_lpc.c:243:       y[i] = SROUND16(sum, SIG_SHIFT);
	addmi	a4, a4, 0x800	# tmp325, sum,
	srai	a4, a4, 12	# _79, tmp325,
	mov.n	a2, a11	# iftmp$29_91, tmp329
	blt	a11, a4, .L59	# tmp329, _79,
# @OPUS@\upstream\celt\celt_lpc.c:243:       y[i] = SROUND16(sum, SIG_SHIFT);
	mov.n	a2, a8	# iftmp$29_91, tmp361
	blt	a4, a8, .L59	# _79, tmp361,
# @OPUS@\upstream\celt\celt_lpc.c:243:       y[i] = SROUND16(sum, SIG_SHIFT);
	slli	a4, a4, 16	# tmp328, _79,
	srai	a2, a4, 16	# iftmp$29_91, tmp328,
.L59:
# @OPUS@\upstream\celt\celt_lpc.c:243:       y[i] = SROUND16(sum, SIG_SHIFT);
	s16i	a2, a5, 0	# MEM[base: _584, offset: 0B], iftmp$29_91
	addi.n	a7, a7, 2	# ivtmp$141, ivtmp$141,
	addi.n	a5, a5, 2	# ivtmp$142, ivtmp$142,
# @OPUS@\upstream\celt\celt_lpc.c:238:    for (;i<N;i++)
	bne	a9, a7, .L60	# _576, ivtmp$141,
	j	.L61		#
	.size	celt_fir_c, .-celt_fir_c
	.section	.text.celt_iir,"ax",@progbits
	.literal_position
	.literal .LC9, -32767
	.literal .LC10, 32767
	.align	4
	.global	celt_iir
	.type	celt_iir, @function
# Function: celt_iir
# Module: upstream/celt/celt_lpc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: RESTORE_STACK;
# C context: }
# C context:
# C context: void celt_iir(const opus_val32 *_x,
# C context: const opus_val16 *den,
# C context: opus_val32 *_y,
# C context: int N,
# C context: int ord,
celt_iir:
	movi	a9, 0xa0	#,
	sub	sp, sp, a9	#,,
	s32i	a0, sp, 156	#,
	s32i	a6, sp, 84	# %sfp, ord
	s32i	a5, sp, 96	# %sfp, N
	s32i	a7, sp, 104	# %sfp, mem
	s32i	a12, sp, 152	#,
	s32i	a4, sp, 112	# %sfp, _y
	s32i	a13, sp, 148	#,
	s32i	a14, sp, 144	#,
	s32i	a15, sp, 140	#,
# @OPUS@\upstream\celt\celt_lpc.c:255: {
	s32i	a2, sp, 108	# %sfp, _x
	s32i.n	a3, sp, 60	# %sfp, den
# @OPUS@\upstream\celt\celt_lpc.c:277:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\celt\celt_lpc.c:280:    ALLOC(rden, ord, opus_val16);
	l32i	a2, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:277:    SAVE_STACK;
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\celt_lpc.c:280:    ALLOC(rden, ord, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_lpc.c:281:    ALLOC(y, N+ord, opus_val16);
	l32i	a6, sp, 84	# %sfp,
	l32i	a8, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:280:    ALLOC(rden, ord, opus_val16);
	s32i	a2, sp, 88	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:281:    ALLOC(y, N+ord, opus_val16);
	add.n	a12, a6, a8	# _2,,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, _2
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_lpc.c:282:    for(i=0;i<ord;i++)
	l32i	a9, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:281:    ALLOC(y, N+ord, opus_val16);
	s32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:282:    for(i=0;i<ord;i++)
	blti	a9, 1, .L106	#,,
	l32i.n	a10, sp, 60	# %sfp,
	slli	a2, a9, 1	# tmp271,,
	addi	a2, a2, -2	# _539, tmp271,
	add.n	a3, a10, a2	# ivtmp$221,, _539
	l32i	a4, sp, 88	# %sfp, ivtmp$223
	mov.n	a7, a10	# den,
	j	.L81		#
.L107:
	mov.n	a3, a6	# ivtmp$221, ivtmp$221
.L81:
# @OPUS@\upstream\celt\celt_lpc.c:283:       rden[i] = den[ord-i-1];
	l16si	a5, a3, 0	# MEM[base: _534, offset: 0B], _12
	addi	a6, a3, -2	# ivtmp$221, ivtmp$221,
# @OPUS@\upstream\celt\celt_lpc.c:283:       rden[i] = den[ord-i-1];
	s16i	a5, a4, 0	# MEM[base: _533, offset: 0B], _12
	addi.n	a4, a4, 2	# ivtmp$223, ivtmp$223,
# @OPUS@\upstream\celt\celt_lpc.c:282:    for(i=0;i<ord;i++)
	bne	a7, a3, .L107	# den, ivtmp$221,
	l32i	a13, sp, 104	# %sfp,
	l32i	a4, sp, 100	# %sfp, ivtmp$218
	add.n	a2, a13, a2	# ivtmp$216,, _539
	mov.n	a6, a13	# mem,
	j	.L82		#
.L108:
	mov.n	a2, a5	# ivtmp$216, ivtmp$216
.L82:
# @OPUS@\upstream\celt\celt_lpc.c:285:       y[i] = -mem[ord-i-1];
	l16ui	a3, a2, 0	# MEM[base: _548, offset: 0B],
	addi	a5, a2, -2	# ivtmp$216, ivtmp$216,
	neg	a3, a3	# tmp276, MEM[base: _548, offset: 0B]
	s16i	a3, a4, 0	# MEM[base: _547, offset: 0B], tmp276
	addi.n	a4, a4, 2	# ivtmp$218, ivtmp$218,
# @OPUS@\upstream\celt\celt_lpc.c:284:    for(i=0;i<ord;i++)
	bne	a6, a2, .L108	# mem, ivtmp$216,
	l32i	a2, sp, 84	# %sfp, i
	j	.L80		#
.L106:
# @OPUS@\upstream\celt\celt_lpc.c:284:    for(i=0;i<ord;i++)
	movi.n	a2, 0	# i,
.L80:
# @OPUS@\upstream\celt\celt_lpc.c:286:    for(;i<N+ord;i++)
	blt	a2, a12, .L83	# i, _2,
.L86:
# @OPUS@\upstream\celt\celt_lpc.c:288:    for (i=0;i<N-3;i+=4)
	l32i	a5, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:288:    for (i=0;i<N-3;i+=4)
	movi.n	a8, 0	# i,
# @OPUS@\upstream\celt\celt_lpc.c:288:    for (i=0;i<N-3;i+=4)
	addi	a2, a5, -3	# tmp277,,
# @OPUS@\upstream\celt\celt_lpc.c:288:    for (i=0;i<N-3;i+=4)
	blti	a2, 1, .L85	# tmp277,,
	j	.L84		#
.L83:
	l32i	a6, sp, 100	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:287:       y[i]=0;
	sub	a4, a12, a2	# tmp278, _2, i
	slli	a2, a2, 1	# tmp280, i,
	slli	a4, a4, 1	#, tmp278,
	movi.n	a3, 0	#,
	add.n	a2, a6, a2	#,, tmp280
	call0	memset		#
	j	.L86		#
.L84:
	addi	a2, a5, -4	# tmp286, tmp8,
	srli	a2, a2, 2	#, tmp286,
	s32i	a2, sp, 116	# %sfp,
	l32i	a9, sp, 84	# %sfp,
	l32i	a10, sp, 108	# %sfp,
	l32i	a13, sp, 116	# %sfp,
	l32i	a7, sp, 100	# %sfp,
	slli	a4, a9, 1	# tmp285,,
	addi	a2, a10, 16	# tmp287,,
	slli	a3, a13, 4	# tmp288,,
	l32r	a5, .LC10	#,
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi	a6, a9, -3	#,,
	add.n	a4, a7, a4	#,, tmp285
	add.n	a3, a2, a3	#, tmp287, tmp288
	s32i	a5, sp, 64	# %sfp,
	s32i	a6, sp, 80	# %sfp,
	s32i.n	a10, sp, 48	# %sfp,
	s32i	a7, sp, 76	# %sfp,
	s32i	a4, sp, 72	# %sfp,
	s32i	a8, sp, 68	# %sfp,
	s32i	a3, sp, 92	# %sfp,
.L96:
# @OPUS@\upstream\celt\celt_lpc.c:292:       sum[0]=_x[i];
	l32i.n	a10, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:293:       sum[1]=_x[i+1];
	l32i.n	a13, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:294:       sum[2]=_x[i+2];
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:295:       sum[3]=_x[i+3];
	l32i.n	a3, sp, 48	# %sfp,
	l32i	a9, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:293:       sum[1]=_x[i+1];
	l32i.n	a13, a13, 4	# MEM[base: _586, offset: 4B],
# @OPUS@\upstream\celt\celt_lpc.c:292:       sum[0]=_x[i];
	l32i.n	a10, a10, 0	# MEM[base: _586, offset: 0B],
# @OPUS@\upstream\celt\celt_lpc.c:294:       sum[2]=_x[i+2];
	l32i.n	a2, a2, 8	# MEM[base: _586, offset: 8B],
# @OPUS@\upstream\celt\celt_lpc.c:295:       sum[3]=_x[i+3];
	l32i.n	a3, a3, 12	# MEM[base: _586, offset: 12B],
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a4, sp, 80	# %sfp,
	addi.n	a15, a9, 6	# ivtmp$200,,
# @OPUS@\upstream\celt\celt_lpc.c:293:       sum[1]=_x[i+1];
	s32i.n	a13, sp, 36	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:292:       sum[0]=_x[i];
	s32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:294:       sum[2]=_x[i+2];
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:295:       sum[3]=_x[i+3];
	s32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:71:    y_0=*y++;
	l16si	a12, a9, 0	# MEM[base: _582, offset: 0B], y_0
# @OPUS@\upstream\celt\pitch.h:72:    y_1=*y++;
	l16si	a14, a9, 2	# MEM[base: _582, offset: 2B], y_1
	mov.n	a6, a15	# y, ivtmp$200
# @OPUS@\upstream\celt\pitch.h:73:    y_2=*y++;
	l16si	a13, a9, 4	# MEM[base: _582, offset: 4B], y_2
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blti	a4, 1, .L109	#,,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	movi.n	a5, 0	#,
	mov.n	a11, a14	# y_1, y_1
	l32i	a3, sp, 88	# %sfp, ivtmp$201
	s32i.n	a5, sp, 44	# %sfp,
	mov.n	a14, a12	# y_0, y_0
	j	.L88		#
.L110:
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i.n	a5, sp, 44	# %sfp, j
.L88:
# @OPUS@\upstream\celt\pitch.h:77:       tmp = *x++;
	l16si	a6, a3, 0	# MEM[base: _609, offset: 0B], tmp
# @OPUS@\upstream\celt\pitch.h:89:       tmp=*x++;
	l16si	a5, a3, 4	# MEM[base: _609, offset: 4B], tmp
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	mull	a14, a6, a14	#, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:83:       tmp=*x++;
	l16si	a2, a3, 2	# MEM[base: _609, offset: 2B], tmp
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a12, a15, 0	# MEM[base: _605, offset: 0B], prephitmp_696
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a14, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a9, a13, a5	#, y_2, tmp
# @OPUS@\upstream\celt\pitch.h:84:       y_0=*y++;
	l16si	a14, a15, 2	# MEM[base: _605, offset: 2B], y_0
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	mull	a8, a11, a2	#, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i.n	a9, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a7, a14, a5	#, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a9, a12, a5	#, prephitmp_696, tmp
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i	a8, sp, 120	# %sfp,
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a11, a6, a11	#, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	s32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i	a9, sp, 124	# %sfp,
	l32i	a7, sp, 120	# %sfp,
	l32i.n	a9, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i.n	a11, sp, 24	# %sfp,
	add.n	a7, a7, a9	#,,
# @OPUS@\upstream\celt\pitch.h:95:       tmp=*x++;
	l16si	a4, a3, 6	# MEM[base: _609, offset: 6B], tmp
# @OPUS@\upstream\celt\pitch.h:81:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a10, a6, a13	# tmp311, tmp, y_2
	s32i.n	a3, sp, 40	# %sfp, ivtmp$201
# @OPUS@\upstream\celt\pitch.h:86:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a8, a13, a2	# tmp305, y_2, tmp
	s32i	a7, sp, 120	# %sfp,
# @OPUS@\upstream\celt\pitch.h:87:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a12, a2	# tmp312, prephitmp_696, tmp
	l32i.n	a7, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a6, a6, a12	# tmp327, tmp, prephitmp_696
# @OPUS@\upstream\celt\pitch.h:88:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a14	# tmp328, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:90:       y_1=*y++;
	l16si	a11, a15, 4	# MEM[base: _605, offset: 4B], y_1
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	mull	a9, a12, a4	#, prephitmp_696, tmp
	add.n	a8, a7, a8	# _179,, tmp305
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a6, a2	# tmp329, tmp327, tmp328
	l32i	a7, sp, 120	# %sfp,
	l32i.n	a6, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:96:       y_2=*y++;
	l16si	a13, a15, 6	# MEM[base: _605, offset: 6B], y_2
	add.n	a3, a10, a3	# tmp313, tmp311, tmp312
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	mull	a10, a14, a4	#, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a9, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.h:94:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mull	a5, a5, a11	# tmp330, tmp, y_1
	add.n	a9, a6, a7	# _13,,
	l32i.n	a6, sp, 56	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	s32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	mull	a10, a11, a4	# tmp325, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	mull	a4, a4, a13	# tmp332, tmp, y_2
	add.n	a3, a3, a6	# _10, tmp313,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i	a7, sp, 124	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a6, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a2, a5	# tmp331, tmp329, tmp330
	l32i.n	a5, sp, 40	# %sfp,
	add.n	a2, a2, a4	# tmp333, tmp331, tmp332
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a4, sp, 16	# %sfp,
	add.n	a9, a6, a9	# tmp320,, _13
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a8, a7, a8	# tmp322,, _179
	addi.n	a7, a5, 8	# x,,
	l32i.n	a5, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	add.n	a4, a4, a9	#,, tmp320
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i.n	a9, sp, 36	# %sfp,
	add.n	a8, a8, a5	# tmp324, tmp322,
	add.n	a9, a9, a8	#,, tmp324
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a4, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i.n	a6, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	s32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	l32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	add.n	a10, a10, a3	# tmp326, tmp325, _10
	add.n	a4, a4, a10	#,, tmp326
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a8, a8, a2	#,, tmp333
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a9, sp, 80	# %sfp,
	addi.n	a15, a15, 8	# ivtmp$200, ivtmp$200,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi.n	a5, a6, 4	# j,,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	s32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	s32i.n	a8, sp, 32	# %sfp,
	mov.n	a3, a7	# ivtmp$201, x
	mov.n	a6, a15	# y, ivtmp$200
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blt	a5, a9, .L110	# j,,
	l32i.n	a10, sp, 44	# %sfp,
	mov.n	a9, a12	# prephitmp_696, prephitmp_696
	addi.n	a3, a10, 5	# _692,,
	mov.n	a12, a14	# y_0, y_0
	addi.n	a8, a10, 6	# _694,,
	mov.n	a14, a11	# y_1, y_1
	j	.L87		#
.L109:
	movi.n	a9, 0	# prephitmp_696,
	l32i	a7, sp, 88	# %sfp, x
	movi.n	a8, 2	# _694,
	movi.n	a3, 1	# _692,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	mov.n	a5, a9	# j, prephitmp_696
.L87:
# @OPUS@\upstream\celt\pitch.h:102:    if (j++<len)
	l32i	a10, sp, 84	# %sfp,
	bge	a5, a10, .L89	# j,,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	l16si	a2, a7, 0	# *x_415, tmp
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	l32i.n	a10, sp, 16	# %sfp,
	mull	a6, a2, a12	# tmp338, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a4, a2, a13	# tmp340, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	add.n	a10, a10, a6	#,, tmp338
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a9, a15, 0	# *y_407, prephitmp_696
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	l32i.n	a10, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a5, a2, a14	# tmp339, tmp, y_1
	l32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	add.n	a10, a10, a4	#,, tmp340
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a2, a2, a9	# tmp341, tmp, prephitmp_696
	l32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	add.n	a6, a6, a5	#,, tmp339
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	add.n	a4, a4, a2	#,, tmp341
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	s32i.n	a10, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	s32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:105:       y_3=*y++;
	addi.n	a6, a15, 2	# y, ivtmp$200,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	addi.n	a7, a7, 2	# x, x,
.L89:
# @OPUS@\upstream\celt\pitch.h:111:    if (j++<len)
	l32i	a10, sp, 84	# %sfp,
	bge	a3, a10, .L90	# _692,,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_315, tmp
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	l32i.n	a10, sp, 16	# %sfp,
	mull	a5, a2, a14	# tmp346, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a2, a9	# tmp348, tmp, prephitmp_696
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	add.n	a10, a10, a5	#,, tmp346
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	l16si	a12, a6, 0	# *y_318, y_0
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	l32i.n	a10, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a4, a2, a13	# tmp347, tmp, y_2
	l32i.n	a5, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	add.n	a10, a10, a3	#,, tmp348
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a12	# tmp349, tmp, y_0
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	add.n	a5, a5, a4	#,, tmp347
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	add.n	a3, a3, a2	#,, tmp349
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	s32i.n	a5, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	s32i.n	a10, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	s32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	addi.n	a6, a6, 2	# y, y,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	addi.n	a7, a7, 2	# x, x,
.L90:
# @OPUS@\upstream\celt\pitch.h:120:    if (j<len)
	l32i	a10, sp, 84	# %sfp,
	bge	a8, a10, .L91	# _694,,
# @OPUS@\upstream\celt\pitch.h:122:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_339, tmp
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	l16ui	a3, a6, 0	# *y_341,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a4, a2, a13	# tmp352, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a5, a2, a9	# tmp353, tmp, prephitmp_696
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a6, a2, a12	# tmp354, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	l32i.n	a13, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mul16s	a2, a3, a2	# tmp355, *y_341, tmp
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	l32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	add.n	a13, a13, a4	#,, tmp352
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	add.n	a3, a3, a5	#,, tmp353
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	l32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	add.n	a4, a4, a6	#,, tmp354
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	add.n	a5, a5, a2	#,, tmp355
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i.n	a13, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	s32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	s32i.n	a5, sp, 32	# %sfp,
.L91:
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	l32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	l32i	a7, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	addmi	a2, a6, 0x800	# tmp357,,
	srai	a2, a2, 12	# _48, tmp357,
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	blt	a7, a2, .L111	#, _48,
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	l32r	a8, .LC9	#,
	blt	a2, a8, .L112	# _48,,
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	neg	a2, a2	# tmp361, _48
	slli	a2, a2, 16	# tmp362, tmp361,
	srai	a2, a2, 16	# iftmp$60_158, tmp362,
	mov.n	a3, a2	# _711, iftmp$60_158
	mov.n	a4, a6	#,
	j	.L92		#
.L111:
	l32r	a3, .LC9	#, _711
	mov.n	a4, a6	#,
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	mov.n	a2, a3	# iftmp$60_158, _711
	j	.L92		#
.L112:
	mov.n	a3, a7	# _711,
	mov.n	a2, a7	# iftmp$60_158, _711
	mov.n	a4, a6	#,
.L92:
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	l32i	a9, sp, 72	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:310:       sum[1] = MAC16_16(sum[1], y[i+ord  ], den[0]);
	l32i.n	a10, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:308:       y[i+ord  ] = -SROUND16(sum[0],SIG_SHIFT);
	s16i	a2, a9, 0	# MEM[base: _577, offset: 0B], iftmp$60_158
# @OPUS@\upstream\celt\celt_lpc.c:310:       sum[1] = MAC16_16(sum[1], y[i+ord  ], den[0]);
	l16si	a5, a10, 0	# *den_177(D), tmp363
	l32i.n	a6, sp, 36	# %sfp,
	mull	a5, a5, a3	# tmp366, tmp363, _711
# @OPUS@\upstream\celt\celt_lpc.c:309:       _y[i  ] = sum[0];
	l32i	a13, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:310:       sum[1] = MAC16_16(sum[1], y[i+ord  ], den[0]);
	add.n	a5, a5, a6	# _61, tmp366,
# @OPUS@\upstream\celt\celt_lpc.c:309:       _y[i  ] = sum[0];
	s32i.n	a4, a13, 0	# MEM[base: _572, offset: 0B],
# @OPUS@\upstream\celt\celt_lpc.c:311:       y[i+ord+1] = -SROUND16(sum[1],SIG_SHIFT);
	addmi	a4, a5, 0x800	# tmp367, _61,
	srai	a4, a4, 12	# _63, tmp367,
# @OPUS@\upstream\celt\celt_lpc.c:311:       y[i+ord+1] = -SROUND16(sum[1],SIG_SHIFT);
	blt	a7, a4, .L113	#, _63,
# @OPUS@\upstream\celt\celt_lpc.c:311:       y[i+ord+1] = -SROUND16(sum[1],SIG_SHIFT);
	l32r	a8, .LC9	#,
	blt	a4, a8, .L114	# _63,,
# @OPUS@\upstream\celt\celt_lpc.c:311:       y[i+ord+1] = -SROUND16(sum[1],SIG_SHIFT);
	neg	a4, a4	# tmp371, _63
	slli	a4, a4, 16	# tmp372, tmp371,
	srai	a4, a4, 16	# iftmp$63_159, tmp372,
	mov.n	a7, a4	# _713, iftmp$63_159
	j	.L93		#
.L113:
	l32r	a7, .LC9	#, _713
# @OPUS@\upstream\celt\celt_lpc.c:311:       y[i+ord+1] = -SROUND16(sum[1],SIG_SHIFT);
	mov.n	a4, a7	# iftmp$63_159, _713
	j	.L93		#
.L114:
	mov.n	a4, a7	# iftmp$63_159, _713
.L93:
# @OPUS@\upstream\celt\celt_lpc.c:311:       y[i+ord+1] = -SROUND16(sum[1],SIG_SHIFT);
	s16i	a4, a9, 2	# MEM[base: _577, offset: 2B], iftmp$63_159
# @OPUS@\upstream\celt\celt_lpc.c:314:       sum[2] = MAC16_16(sum[2], y[i+ord  ], den[1]);
	l16ui	a3, a10, 2	# MEM[(const opus_val16 *)den_177(D) + 2B],
# @OPUS@\upstream\celt\celt_lpc.c:313:       sum[2] = MAC16_16(sum[2], y[i+ord+1], den[0]);
	l16si	a6, a10, 0	# *den_177(D), tmp376
# @OPUS@\upstream\celt\celt_lpc.c:314:       sum[2] = MAC16_16(sum[2], y[i+ord  ], den[1]);
	mul16s	a3, a3, a2	# tmp373, MEM[(const opus_val16 *)den_177(D) + 2B], iftmp$60_158
	l32i.n	a13, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:313:       sum[2] = MAC16_16(sum[2], y[i+ord+1], den[0]);
	mull	a6, a6, a7	# tmp379, tmp376, _713
# @OPUS@\upstream\celt\celt_lpc.c:314:       sum[2] = MAC16_16(sum[2], y[i+ord  ], den[1]);
	add.n	a3, a3, a13	# tmp375, tmp373,
	add.n	a6, a3, a6	# _81, tmp375, tmp379
# @OPUS@\upstream\celt\celt_lpc.c:312:       _y[i+1] = sum[1];
	l32i	a7, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	addmi	a3, a6, 0x800	# tmp380, _81,
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:312:       _y[i+1] = sum[1];
	s32i.n	a5, a7, 4	# MEM[base: _572, offset: 4B], _61
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	srai	a3, a3, 12	# _83, tmp380,
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	blt	a8, a3, .L115	#, _83,
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	l32r	a9, .LC9	#,
	blt	a3, a9, .L116	# _83,,
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	neg	a3, a3	# tmp384, _83
	slli	a5, a3, 16	# tmp385, tmp384,
	srai	a5, a5, 16	# iftmp$66_160, tmp385,
	mov.n	a3, a5	# _715, iftmp$66_160
	mov.n	a13, a10	#,
	j	.L94		#
.L115:
	l32r	a3, .LC9	#, _715
	mov.n	a13, a10	#,
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	mov.n	a5, a3	# iftmp$66_160, _715
	j	.L94		#
.L116:
	mov.n	a3, a8	# _715,
	mov.n	a5, a8	# iftmp$66_160, _715
	mov.n	a13, a10	#,
.L94:
# @OPUS@\upstream\celt\celt_lpc.c:315:       y[i+ord+2] = -SROUND16(sum[2],SIG_SHIFT);
	l32i	a10, sp, 72	# %sfp,
	s16i	a5, a10, 4	# MEM[base: _577, offset: 4B], iftmp$66_160
# @OPUS@\upstream\celt\celt_lpc.c:319:       sum[3] = MAC16_16(sum[3], y[i+ord+1], den[1]);
	l16ui	a5, a13, 2	# MEM[(const opus_val16 *)den_177(D) + 2B],
# @OPUS@\upstream\celt\celt_lpc.c:320:       sum[3] = MAC16_16(sum[3], y[i+ord  ], den[2]);
	l16ui	a7, a13, 4	# MEM[(const opus_val16 *)den_177(D) + 4B],
# @OPUS@\upstream\celt\celt_lpc.c:319:       sum[3] = MAC16_16(sum[3], y[i+ord+1], den[1]);
	mul16s	a4, a5, a4	# tmp386, MEM[(const opus_val16 *)den_177(D) + 2B], iftmp$63_159
# @OPUS@\upstream\celt\celt_lpc.c:320:       sum[3] = MAC16_16(sum[3], y[i+ord  ], den[2]);
	mul16s	a2, a7, a2	# tmp388, MEM[(const opus_val16 *)den_177(D) + 4B], iftmp$60_158
# @OPUS@\upstream\celt\celt_lpc.c:318:       sum[3] = MAC16_16(sum[3], y[i+ord+2], den[0]);
	l16si	a5, a13, 0	# *den_177(D), tmp392
# @OPUS@\upstream\celt\celt_lpc.c:320:       sum[3] = MAC16_16(sum[3], y[i+ord  ], den[2]);
	add.n	a4, a4, a2	# tmp390, tmp386, tmp388
	l32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:318:       sum[3] = MAC16_16(sum[3], y[i+ord+2], den[0]);
	mull	a3, a5, a3	# tmp395, tmp392, _715
# @OPUS@\upstream\celt\celt_lpc.c:320:       sum[3] = MAC16_16(sum[3], y[i+ord  ], den[2]);
	add.n	a4, a4, a2	# tmp391, tmp390,
	add.n	a4, a4, a3	# _107, tmp391, tmp395
# @OPUS@\upstream\celt\celt_lpc.c:316:       _y[i+2] = sum[2];
	l32i	a3, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	addmi	a2, a4, 0x800	# tmp396, _107,
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	l32i	a5, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:316:       _y[i+2] = sum[2];
	s32i.n	a6, a3, 8	# MEM[base: _572, offset: 8B], _81
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	srai	a2, a2, 12	# _109, tmp396,
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	l32r	a3, .LC9	#, iftmp$69_161
	blt	a5, a2, .L95	#, _109,
	mov.n	a6, a3	#, iftmp$69_161
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	mov.n	a3, a5	# iftmp$69_161,
	blt	a2, a6, .L95	# _109,,
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	neg	a2, a2	# tmp400, _109
	slli	a2, a2, 16	# tmp401, tmp400,
	srai	a3, a2, 16	# iftmp$69_161, tmp401,
.L95:
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	l32i	a7, sp, 72	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:322:       _y[i+3] = sum[3];
	l32i	a8, sp, 68	# %sfp,
	l32i.n	a9, sp, 48	# %sfp,
	l32i	a10, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt_lpc.c:321:       y[i+ord+3] = -SROUND16(sum[3],SIG_SHIFT);
	s16i	a3, a7, 6	# MEM[base: _577, offset: 6B], iftmp$69_161
# @OPUS@\upstream\celt\celt_lpc.c:322:       _y[i+3] = sum[3];
	s32i.n	a4, a8, 12	# MEM[base: _572, offset: 12B], _107
	addi	a9, a9, 16	#,,
	addi.n	a10, a10, 8	#,,
	addi.n	a7, a7, 8	#,,
	addi	a8, a8, 16	#,,
# @OPUS@\upstream\celt\celt_lpc.c:288:    for (i=0;i<N-3;i+=4)
	l32i	a13, sp, 92	# %sfp,
	s32i.n	a9, sp, 48	# %sfp,
	s32i	a10, sp, 76	# %sfp,
	s32i	a7, sp, 72	# %sfp,
	s32i	a8, sp, 68	# %sfp,
	bne	a13, a9, .L96	#,,
	l32i	a2, sp, 116	# %sfp,
	addi.n	a8, a2, 1	# tmp402,,
	slli	a8, a8, 2	# i, tmp402,
.L85:
# @OPUS@\upstream\celt\celt_lpc.c:324:    for (;i<N;i++)
	l32i	a5, sp, 96	# %sfp,
	blt	a8, a5, .L97	# i,,
.L104:
# @OPUS@\upstream\celt\celt_lpc.c:332:    for(i=0;i<ord;i++)
	l32i	a6, sp, 84	# %sfp,
	bgei	a6, 1, .L98	#,,
	j	.L99		#
.L97:
	l32i	a13, sp, 84	# %sfp,
	slli	a11, a5, 1	# tmp404, tmp9,
	l32i	a6, sp, 112	# %sfp,
	l32i	a5, sp, 108	# %sfp,
	slli	a10, a8, 2	# _671, i,
	l32i	a7, sp, 100	# %sfp,
	slli	a12, a13, 1	# _678,,
	l32r	a2, .LC10	#,
	l32i	a13, sp, 88	# %sfp,
	slli	a8, a8, 1	# tmp403, i,
	add.n	a9, a5, a10	# ivtmp$187,, _671
	add.n	a10, a6, a10	# ivtmp$189,, _671
	l32i	a6, sp, 84	# %sfp, ord
	add.n	a8, a7, a8	# ivtmp$190,, tmp403
	add.n	a11, a7, a11	# _621,, tmp404
	s32i	a2, sp, 64	# %sfp,
	add.n	a7, a13, a12	# _676,, _678
	mov.n	a15, a13	# rden,
	mov.n	a14, a2	# tmp419,
.L103:
# @OPUS@\upstream\celt\celt_lpc.c:326:       opus_val32 sum = _x[i];
	l32i.n	a5, a9, 0	# MEM[base: _636, offset: 0B], sum
# @OPUS@\upstream\celt\celt_lpc.c:327:       for (j=0;j<ord;j++)
	blti	a6, 1, .L100	# ord,,
	mov.n	a4, a8	# ivtmp$182, ivtmp$190
	mov.n	a2, a15	# ivtmp$181, rden
.L101:
# @OPUS@\upstream\celt\celt_lpc.c:328:          sum -= MULT16_16(rden[j],y[i+j]);
	l16ui	a3, a2, 0	# MEM[base: _681, offset: 0B],
	l16ui	a13, a4, 0	# MEM[base: _680, offset: 0B],
	addi.n	a2, a2, 2	# ivtmp$181, ivtmp$181,
	mul16s	a3, a3, a13	# tmp405, MEM[base: _681, offset: 0B],
	addi.n	a4, a4, 2	# ivtmp$182, ivtmp$182,
# @OPUS@\upstream\celt\celt_lpc.c:328:          sum -= MULT16_16(rden[j],y[i+j]);
	sub	a5, a5, a3	# sum, sum, tmp405
# @OPUS@\upstream\celt\celt_lpc.c:327:       for (j=0;j<ord;j++)
	bne	a7, a2, .L101	# _676, ivtmp$181,
.L100:
# @OPUS@\upstream\celt\celt_lpc.c:329:       y[i+ord] = SROUND16(sum,SIG_SHIFT);
	addmi	a2, a5, 0x800	# tmp408, sum,
	srai	a2, a2, 12	# _133, tmp408,
	mov.n	a3, a14	# iftmp$74_162, tmp419
	blt	a14, a2, .L102	# tmp419, _133,
# @OPUS@\upstream\celt\celt_lpc.c:329:       y[i+ord] = SROUND16(sum,SIG_SHIFT);
	l32r	a3, .LC9	#, iftmp$74_162
	blt	a2, a3, .L102	# _133, tmp4,
# @OPUS@\upstream\celt\celt_lpc.c:329:       y[i+ord] = SROUND16(sum,SIG_SHIFT);
	slli	a2, a2, 16	# tmp411, _133,
	srai	a3, a2, 16	# iftmp$74_162, tmp411,
.L102:
# @OPUS@\upstream\celt\celt_lpc.c:329:       y[i+ord] = SROUND16(sum,SIG_SHIFT);
	add.n	a2, a8, a12	# tmp412, ivtmp$190, _678
	s16i	a3, a2, 0	# MEM[base: _626, offset: 0B], iftmp$74_162
# @OPUS@\upstream\celt\celt_lpc.c:330:       _y[i] = sum;
	s32i.n	a5, a10, 0	# MEM[base: _625, offset: 0B], sum
	addi.n	a8, a8, 2	# ivtmp$190, ivtmp$190,
	addi.n	a9, a9, 4	# ivtmp$187, ivtmp$187,
	addi.n	a10, a10, 4	# ivtmp$189, ivtmp$189,
# @OPUS@\upstream\celt\celt_lpc.c:324:    for (;i<N;i++)
	bne	a11, a8, .L103	# _621, ivtmp$190,
	j	.L104		#
.L99:
# @OPUS@\upstream\celt\celt_lpc.c:334:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_lpc.c:336: }
	l32i	a0, sp, 156	#,
	movi	a9, 0xa0	#,
	l32i	a12, sp, 152	#,
	l32i	a13, sp, 148	#,
	l32i	a14, sp, 144	#,
	l32i	a15, sp, 140	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L98:
	l32i	a5, sp, 96	# %sfp,
	l32i	a7, sp, 104	# %sfp, ivtmp$178
	slli	a3, a5, 2	# tmp413,,
	l32i	a8, sp, 112	# %sfp,
	addi	a3, a3, -4	# tmp415, tmp413,
	slli	a2, a6, 1	# tmp416,,
	add.n	a3, a8, a3	# ivtmp$176,, tmp415
	add.n	a2, a7, a2	# _701, ivtmp$178, tmp416
.L105:
# @OPUS@\upstream\celt\celt_lpc.c:333:       mem[i] = _y[N-i-1];
	l32i.n	a4, a3, 0	# MEM[base: _706, offset: 0B], MEM[base: _706, offset: 0B]
	addi	a3, a3, -4	# ivtmp$176, ivtmp$176,
	s16i	a4, a7, 0	# MEM[base: _705, offset: 0B], MEM[base: _706, offset: 0B]
	addi.n	a7, a7, 2	# ivtmp$178, ivtmp$178,
# @OPUS@\upstream\celt\celt_lpc.c:332:    for(i=0;i<ord;i++)
	bne	a2, a7, .L105	# _701, ivtmp$178,
	j	.L99		#
	.size	celt_iir, .-celt_iir
	.section	.text._celt_autocorr,"ax",@progbits
	.literal_position
	.literal .LC14, 268435455
	.literal .LC15, 536870911
	.literal .LC16, 1073741823
	.align	4
	.global	_celt_autocorr
	.type	_celt_autocorr, @function
# Function: _celt_autocorr
# Module: upstream/celt/celt_lpc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: int _celt_autocorr(
# C context: const opus_val16 *x,   /*  in: [0...n-1] samples x   */
# C context: opus_val32       *ac,  /* out: [0...lag-1] ac values */
# C context: const opus_val16       *window,
# C context: int          overlap,
_celt_autocorr:
	addi	sp, sp, -64	#,,
# @OPUS@\upstream\celt\celt_lpc.c:354:    SAVE_STACK;
	s32i.n	a5, sp, 16	#,
# @OPUS@\upstream\celt\celt_lpc.c:347: {
	s32i.n	a0, sp, 60	#,
	s32i.n	a12, sp, 56	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
	mov.n	a13, a7	# n, n
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\celt\celt_lpc.c:354:    SAVE_STACK;
	s32i.n	a6, sp, 24	#, tmp8
# @OPUS@\upstream\celt\celt_lpc.c:347: {
	mov.n	a15, a4	# window, window
	mov.n	a14, a2	# x, x
	mov.n	a12, a3	# ac, ac
# @OPUS@\upstream\celt\celt_lpc.c:354:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\celt_lpc.c:362:    ALLOC(xx, n, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a13	#, n
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_lpc.c:350:    int fastN=n-lag;
	l32i.n	a8, sp, 24	#,
# @OPUS@\upstream\celt\celt_lpc.c:365:    if (overlap == 0)
	l32i.n	a5, sp, 16	#,
# @OPUS@\upstream\celt\celt_lpc.c:362:    ALLOC(xx, n, opus_val16);
	mov.n	a9, a2	# xx,
# @OPUS@\upstream\celt\celt_lpc.c:350:    int fastN=n-lag;
	sub	a10, a13, a8	# fastN, n, lag
# @OPUS@\upstream\celt\celt_lpc.c:365:    if (overlap == 0)
	beqz.n	a5, .L127	# overlap,
# @OPUS@\upstream\celt\celt_lpc.c:369:       for (i=0;i<n;i++)
	bgei	a13, 1, .L128	# n,,
.L136:
# @OPUS@\upstream\celt\celt_lpc.c:371:       for (i=0;i<overlap;i++)
	bgei	a5, 1, .L129	# overlap,,
	j	.L194		#
.L128:
	addi.n	a3, a14, 4	# tmp206, x,
	movi.n	a2, 1	# tmp207,
	bgeu	a9, a3, .L131	# xx, tmp206,
	movi.n	a2, 0	# tmp207,
.L131:
	addi.n	a3, a9, 4	# tmp209, xx,
	movi.n	a6, 1	# tmp210,
	bgeu	a14, a3, .L132	# x, tmp209,
	movi.n	a6, 0	# tmp210,
.L132:
	addi.n	a3, a13, -1	# tmp213, n,
	movi.n	a4, 0xb	# tmp216,
	or	a2, a2, a6	# tmp212, tmp207, tmp210
	movi.n	a6, 1	# tmp214,
	bltu	a4, a3, .L133	# tmp216, tmp213,
	movi.n	a6, 0	# tmp214,
.L133:
	and	a2, a2, a6	# tmp218, tmp212, tmp214
	bbci	a2, 0, .L130	# tmp218,,
	or	a2, a9, a14	# tmp221, xx, x
	extui	a2, a2, 0, 2	# tmp222, tmp221,
	bnez.n	a2, .L130	# tmp222,
	srli	a6, a13, 1	# bnd$227, n,
	slli	a6, a6, 2	# tmp229, bnd$227,
	mov.n	a2, a9	# ivtmp$288, xx
	mov.n	a3, a14	# ivtmp$290, x
	add.n	a6, a6, a9	# _288, tmp229, xx
.L134:
# @OPUS@\upstream\celt\celt_lpc.c:370:          xx[i] = x[i];
	l32i.n	a4, a3, 0	# MEM[base: _292, offset: 0B], vect__6$232
	addi.n	a3, a3, 4	# ivtmp$290, ivtmp$290,
# @OPUS@\upstream\celt\celt_lpc.c:370:          xx[i] = x[i];
	s32i.n	a4, a2, 0	# MEM[base: _291, offset: 0B], vect__6$232
	addi.n	a2, a2, 4	# ivtmp$288, ivtmp$288,
	bne	a6, a2, .L134	# _288, ivtmp$288,
	movi.n	a2, -2	# tmp230,
	and	a2, a13, a2	# niters_vector_mult_vf$228, n, tmp230
	beq	a13, a2, .L136	# n, niters_vector_mult_vf$228,
# @OPUS@\upstream\celt\celt_lpc.c:370:          xx[i] = x[i];
	slli	a2, a2, 1	# _429, niters_vector_mult_vf$228,
	add.n	a3, a14, a2	# tmp231, x, _429
	l16si	a3, a3, 0	# *_422, _420
# @OPUS@\upstream\celt\celt_lpc.c:370:          xx[i] = x[i];
	add.n	a2, a9, a2	# tmp234, xx, _429
	s16i	a3, a2, 0	# *_421, _420
	j	.L136		#
.L130:
	slli	a6, a13, 1	# tmp235, n,
	mov.n	a2, a14	# ivtmp$281, x
	mov.n	a3, a9	# ivtmp$282, xx
	add.n	a6, a6, a14	# _299, tmp235, x
.L138:
# @OPUS@\upstream\celt\celt_lpc.c:370:          xx[i] = x[i];
	l16si	a4, a2, 0	# MEM[base: _304, offset: 0B], _458
	addi.n	a2, a2, 2	# ivtmp$281, ivtmp$281,
# @OPUS@\upstream\celt\celt_lpc.c:370:          xx[i] = x[i];
	s16i	a4, a3, 0	# MEM[base: _303, offset: 0B], _458
	addi.n	a3, a3, 2	# ivtmp$282, ivtmp$282,
# @OPUS@\upstream\celt\celt_lpc.c:369:       for (i=0;i<n;i++)
	bne	a6, a2, .L138	# _299, ivtmp$281,
	j	.L136		#
.L129:
	slli	a6, a5, 1	# tmp240, overlap,
	slli	a3, a13, 1	# tmp238, n,
	mov.n	a4, a14	# ivtmp$268, x
	mov.n	a5, a9	# ivtmp$270, xx
	addi	a3, a3, -2	# ivtmp$276, tmp238,
	add.n	a6, a6, a14	# _311, tmp240, x
.L140:
# @OPUS@\upstream\celt\celt_lpc.c:373:          xx[i] = MULT16_16_Q15(x[i],window[i]);
	l16ui	a7, a15, 0	# MEM[base: _319, offset: 0B],
	l16ui	a11, a4, 0	# MEM[base: _320, offset: 0B],
# @OPUS@\upstream\celt\celt_lpc.c:374:          xx[n-i-1] = MULT16_16_Q15(x[n-i-1],window[i]);
	add.n	a2, a14, a3	# tmp246, x, ivtmp$276
# @OPUS@\upstream\celt\celt_lpc.c:373:          xx[i] = MULT16_16_Q15(x[i],window[i]);
	mul16s	a11, a11, a7	# tmp241, MEM[base: _320, offset: 0B], MEM[base: _319, offset: 0B]
# @OPUS@\upstream\celt\celt_lpc.c:374:          xx[n-i-1] = MULT16_16_Q15(x[n-i-1],window[i]);
	add.n	a7, a9, a3	# tmp245, xx, ivtmp$276
# @OPUS@\upstream\celt\celt_lpc.c:373:          xx[i] = MULT16_16_Q15(x[i],window[i]);
	srai	a11, a11, 15	# tmp244, tmp241,
# @OPUS@\upstream\celt\celt_lpc.c:373:          xx[i] = MULT16_16_Q15(x[i],window[i]);
	s16i	a11, a5, 0	# MEM[base: _317, offset: 0B], tmp244
# @OPUS@\upstream\celt\celt_lpc.c:374:          xx[n-i-1] = MULT16_16_Q15(x[n-i-1],window[i]);
	l16ui	a11, a15, 0	# MEM[base: _319, offset: 0B],
	l16ui	a2, a2, 0	# MEM[base: _316, offset: 0B],
	addi.n	a4, a4, 2	# ivtmp$268, ivtmp$268,
	mul16s	a2, a2, a11	# tmp247, MEM[base: _316, offset: 0B], MEM[base: _319, offset: 0B]
	addi.n	a15, a15, 2	# ivtmp$269, ivtmp$269,
	srai	a2, a2, 15	# tmp250, tmp247,
# @OPUS@\upstream\celt\celt_lpc.c:374:          xx[n-i-1] = MULT16_16_Q15(x[n-i-1],window[i]);
	s16i	a2, a7, 0	# MEM[base: _315, offset: 0B], tmp250
	addi.n	a5, a5, 2	# ivtmp$270, ivtmp$270,
	addi	a3, a3, -2	# ivtmp$276, ivtmp$276,
# @OPUS@\upstream\celt\celt_lpc.c:371:       for (i=0;i<overlap;i++)
	bne	a6, a4, .L140	# _311, ivtmp$268,
.L194:
# @OPUS@\upstream\celt\celt_lpc.c:376:       xptr = xx;
	mov.n	a14, a9	# x, xx
.L127:
# @OPUS@\upstream\celt\celt_lpc.c:382:       ac0 = 1+(n<<7);
	slli	a5, a13, 7	# tmp251, n,
# @OPUS@\upstream\celt\celt_lpc.c:383:       if (n&1) ac0 += SHR32(MULT16_16(xptr[0],xptr[0]),9);
	extui	a4, a13, 0, 1	# _36, n,
# @OPUS@\upstream\celt\celt_lpc.c:382:       ac0 = 1+(n<<7);
	addi.n	a5, a5, 1	# ac0, tmp251,
# @OPUS@\upstream\celt\celt_lpc.c:383:       if (n&1) ac0 += SHR32(MULT16_16(xptr[0],xptr[0]),9);
	beqz.n	a4, .L141	# _36,
# @OPUS@\upstream\celt\celt_lpc.c:383:       if (n&1) ac0 += SHR32(MULT16_16(xptr[0],xptr[0]),9);
	l16si	a2, a14, 0	# *xptr_116, _37
	mull	a2, a2, a2	# tmp254, _37, _37
	srai	a2, a2, 9	# tmp255, tmp254,
# @OPUS@\upstream\celt\celt_lpc.c:383:       if (n&1) ac0 += SHR32(MULT16_16(xptr[0],xptr[0]),9);
	add.n	a5, a5, a2	# ac0, ac0, tmp255
.L141:
# @OPUS@\upstream\celt\celt_lpc.c:384:       for(i=(n&1);i<n;i+=2)
	bge	a4, a13, .L142	# _36, n,
	slli	a3, a4, 1	# tmp256, _36,
	add.n	a3, a14, a3	# ivtmp$262, x, tmp256
.L143:
# @OPUS@\upstream\celt\celt_lpc.c:386:          ac0 += SHR32(MULT16_16(xptr[i],xptr[i]),9);
	l16si	a2, a3, 0	# MEM[base: _336, offset: 0B], _44
# @OPUS@\upstream\celt\celt_lpc.c:387:          ac0 += SHR32(MULT16_16(xptr[i+1],xptr[i+1]),9);
	l16si	a6, a3, 2	# MEM[base: _336, offset: 2B], _51
# @OPUS@\upstream\celt\celt_lpc.c:386:          ac0 += SHR32(MULT16_16(xptr[i],xptr[i]),9);
	mull	a2, a2, a2	# tmp261, _44, _44
# @OPUS@\upstream\celt\celt_lpc.c:387:          ac0 += SHR32(MULT16_16(xptr[i+1],xptr[i+1]),9);
	mull	a6, a6, a6	# tmp263, _51, _51
# @OPUS@\upstream\celt\celt_lpc.c:386:          ac0 += SHR32(MULT16_16(xptr[i],xptr[i]),9);
	srai	a2, a2, 9	# tmp262, tmp261,
# @OPUS@\upstream\celt\celt_lpc.c:387:          ac0 += SHR32(MULT16_16(xptr[i+1],xptr[i+1]),9);
	srai	a6, a6, 9	# tmp264, tmp263,
# @OPUS@\upstream\celt\celt_lpc.c:387:          ac0 += SHR32(MULT16_16(xptr[i+1],xptr[i+1]),9);
	add.n	a2, a2, a6	# tmp265, tmp262, tmp264
# @OPUS@\upstream\celt\celt_lpc.c:384:       for(i=(n&1);i<n;i+=2)
	addi.n	a4, a4, 2	# _36, _36,
# @OPUS@\upstream\celt\celt_lpc.c:387:          ac0 += SHR32(MULT16_16(xptr[i+1],xptr[i+1]),9);
	add.n	a5, a5, a2	# ac0, ac0, tmp265
	addi.n	a3, a3, 4	# ivtmp$262, ivtmp$262,
# @OPUS@\upstream\celt\celt_lpc.c:384:       for(i=(n&1);i<n;i+=2)
	blt	a4, a13, .L143	# _36, n,
	j	.L192		#
.L142:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a5, a5	# _175, ac0
# @OPUS@\upstream\celt\celt_lpc.c:390:       shift = celt_ilog2(ac0)-30+10;
	movi.n	a15, 0xb	# tmp269,
# @OPUS@\upstream\celt\celt_lpc.c:390:       shift = celt_ilog2(ac0)-30+10;
	sub	a15, a15, a5	# shift, tmp269, _175
# @OPUS@\upstream\celt\celt_lpc.c:392:       if (shift>0)
	blti	a15, 2, .L145	# shift,,
# @OPUS@\upstream\celt\celt_lpc.c:391:       shift = (shift)/2;
	srai	a15, a15, 1	# shift, shift,
# @OPUS@\upstream\celt\celt_lpc.c:394:          for(i=0;i<n;i++)
	bnei	a13, 1, .L146	# n,,
.L164:
# @OPUS@\upstream\celt\celt_lpc.c:395:             xx[i] = PSHR32(xptr[i], shift);
	movi.n	a5, 1	# tmp271,
	ssl	a15	# shift
	sll	a5, a5	# tmp272, tmp271
	srai	a5, a5, 1	# _62, tmp272,
	mov.n	a4, a9	# ivtmp$256, xx
	movi.n	a3, 0	# i,
.L147:
	l16si	a2, a14, 0	# MEM[base: _344, offset: 0B], tmp273
# @OPUS@\upstream\celt\celt_lpc.c:394:          for(i=0;i<n;i++)
	addi.n	a3, a3, 1	# i, i,
# @OPUS@\upstream\celt\celt_lpc.c:395:             xx[i] = PSHR32(xptr[i], shift);
	add.n	a2, a2, a5	# tmp276, tmp273, _62
	ssr	a15	# shift
	sra	a2, a2	# tmp277, tmp276
# @OPUS@\upstream\celt\celt_lpc.c:395:             xx[i] = PSHR32(xptr[i], shift);
	s16i	a2, a4, 0	# MEM[base: _343, offset: 0B], tmp277
	addi.n	a14, a14, 2	# ivtmp$255, ivtmp$255,
	addi.n	a4, a4, 2	# ivtmp$256, ivtmp$256,
# @OPUS@\upstream\celt\celt_lpc.c:394:          for(i=0;i<n;i++)
	blt	a3, a13, .L147	# i, n,
.L146:
# @OPUS@\upstream\celt\celt_lpc.c:401:    celt_pitch_xcorr(xptr, xptr, ac, fastN, lag+1, arch);
	l32i	a7, sp, 64	# arch,
	addi.n	a6, a8, 1	#, lag,
	mov.n	a5, a10	#, fastN
	mov.n	a3, a9	#, xx
	mov.n	a2, a9	#, xx
	mov.n	a4, a12	#, ac
	s32i.n	a8, sp, 24	#,
	s32i.n	a9, sp, 16	#,
	s32i.n	a10, sp, 20	#,
	call0	celt_pitch_xcorr_c		#
# @OPUS@\upstream\celt\celt_lpc.c:402:    for (k=0;k<=lag;k++)
	l32i.n	a8, sp, 24	#,
	slli	a14, a15, 1	# <retval>, shift,
	l32i.n	a9, sp, 16	#,
	l32i.n	a10, sp, 20	#,
	bltz	a8, .L148	# lag,
.L162:
	slli	a7, a10, 1	# tmp279, fastN,
	slli	a2, a13, 1	# tmp280, n,
	movi.n	a5, 0	# ivtmp$252,
	add.n	a7, a7, a9	# _353, tmp279, xx
	mov.n	a6, a12	# ivtmp$250, ac
	add.n	a9, a2, a9	# _372, tmp280, xx
# @OPUS@\upstream\celt\celt_lpc.c:402:    for (k=0;k<=lag;k++)
	mov.n	a11, a5	# k, ivtmp$252
.L151:
# @OPUS@\upstream\celt\celt_lpc.c:404:       for (i = k+fastN, d = 0; i < n; i++)
	add.n	a2, a11, a10	# i, k, fastN
	bge	a2, a13, .L166	# i, n,
	sub	a2, a7, a5	# ivtmp$244, _353, ivtmp$252
# @OPUS@\upstream\celt\celt_lpc.c:404:       for (i = k+fastN, d = 0; i < n; i++)
	movi.n	a4, 0	# d,
.L150:
# @OPUS@\upstream\celt\celt_lpc.c:405:          d = MAC16_16(d, xptr[i], xptr[i-k]);
	add.n	a3, a2, a5	# tmp282, ivtmp$244, ivtmp$252
	l16ui	a15, a2, 0	# MEM[base: _380, offset: 0B],
	l16ui	a3, a3, 0	# MEM[base: _376, offset: 0B],
	addi.n	a2, a2, 2	# ivtmp$244, ivtmp$244,
	mul16s	a3, a3, a15	# tmp283, MEM[base: _376, offset: 0B], MEM[base: _380, offset: 0B]
# @OPUS@\upstream\celt\celt_lpc.c:405:          d = MAC16_16(d, xptr[i], xptr[i-k]);
	add.n	a4, a4, a3	# d, d, tmp283
# @OPUS@\upstream\celt\celt_lpc.c:404:       for (i = k+fastN, d = 0; i < n; i++)
	bne	a9, a2, .L150	# _372, ivtmp$244,
	j	.L149		#
.L166:
# @OPUS@\upstream\celt\celt_lpc.c:404:       for (i = k+fastN, d = 0; i < n; i++)
	movi.n	a4, 0	# d,
.L149:
# @OPUS@\upstream\celt\celt_lpc.c:406:       ac[k] += d;
	l32i.n	a2, a6, 0	# MEM[base: _358, offset: 0B], MEM[base: _358, offset: 0B]
# @OPUS@\upstream\celt\celt_lpc.c:402:    for (k=0;k<=lag;k++)
	addi.n	a11, a11, 1	# k, k,
# @OPUS@\upstream\celt\celt_lpc.c:406:       ac[k] += d;
	add.n	a4, a2, a4	# tmp286, MEM[base: _358, offset: 0B], d
	s32i.n	a4, a6, 0	# MEM[base: _358, offset: 0B], tmp286
	addi	a5, a5, -2	# ivtmp$252, ivtmp$252,
	addi.n	a6, a6, 4	# ivtmp$250, ivtmp$250,
# @OPUS@\upstream\celt\celt_lpc.c:402:    for (k=0;k<=lag;k++)
	bge	a8, a11, .L151	# lag, k,
	l32i.n	a2, a12, 0	# *ac_156(D), pretmp_449
# @OPUS@\upstream\celt\celt_lpc.c:410:    if (shift<=0)
	bnez.n	a14, .L152	# <retval>,
.L163:
# @OPUS@\upstream\celt\celt_lpc.c:411:       ac[0] += SHL32((opus_int32)1, -shift);
	addi.n	a2, a2, 1	# pretmp_449, pretmp_449,
# @OPUS@\upstream\celt\celt_lpc.c:412:    if (ac[0] < 268435456)
	l32r	a3, .LC14	#, tmp288
# @OPUS@\upstream\celt\celt_lpc.c:411:       ac[0] += SHL32((opus_int32)1, -shift);
	s32i.n	a2, a12, 0	# *ac_156(D), pretmp_449
# @OPUS@\upstream\celt\celt_lpc.c:412:    if (ac[0] < 268435456)
	blt	a3, a2, .L167	# tmp288, pretmp_449,
# @OPUS@\upstream\celt\celt_lpc.c:414:       int shift2 = 29 - EC_ILOG(ac[0]);
	nsau	a2, a2	# _92, pretmp_449
# @OPUS@\upstream\celt\celt_lpc.c:415:       for (i=0;i<=lag;i++)
	movi.n	a14, 0	# <retval>,
# @OPUS@\upstream\celt\celt_lpc.c:414:       int shift2 = 29 - EC_ILOG(ac[0]);
	addi	a3, a2, -3	# shift2, _92,
# @OPUS@\upstream\celt\celt_lpc.c:415:       for (i=0;i<=lag;i++)
	bge	a8, a14, .L154	# lag,,
.L157:
# @OPUS@\upstream\celt\celt_lpc.c:417:       shift -= shift2;
	sub	a14, a14, a3	# <retval>, <retval>, shift2
	j	.L155		#
.L154:
	slli	a4, a8, 2	# tmp289, lag,
	addi.n	a2, a12, 4	# tmp290, ivtmp$237,
	add.n	a4, a4, a2	# _140, tmp289, tmp290
.L156:
# @OPUS@\upstream\celt\celt_lpc.c:416:          ac[i] = SHL32(ac[i], shift2);
	l32i.n	a2, a12, 0	# MEM[base: _3, offset: 0B], MEM[base: _3, offset: 0B]
	ssl	a3	# shift2
	sll	a2, a2	# tmp291, MEM[base: _3, offset: 0B]
# @OPUS@\upstream\celt\celt_lpc.c:416:          ac[i] = SHL32(ac[i], shift2);
	s32i.n	a2, a12, 0	# MEM[base: _3, offset: 0B], tmp291
	addi.n	a12, a12, 4	# ivtmp$237, ivtmp$237,
# @OPUS@\upstream\celt\celt_lpc.c:415:       for (i=0;i<=lag;i++)
	bne	a4, a12, .L156	# _140, ivtmp$237,
	j	.L157		#
.L167:
	movi.n	a14, 0	# <retval>,
.L153:
# @OPUS@\upstream\celt\celt_lpc.c:418:    } else if (ac[0] >= 536870912)
	l32r	a3, .LC15	#, tmp293
	bge	a3, a2, .L155	# tmp293, pretmp_449,
# @OPUS@\upstream\celt\celt_lpc.c:421:       if (ac[0] >= 1073741824)
	l32r	a3, .LC16	#, tmp294
# @OPUS@\upstream\celt\celt_lpc.c:420:       int shift2=1;
	movi.n	a4, 1	# shift2,
# @OPUS@\upstream\celt\celt_lpc.c:421:       if (ac[0] >= 1073741824)
	bge	a3, a2, .L158	# tmp294, pretmp_449,
# @OPUS@\upstream\celt\celt_lpc.c:422:          shift2++;
	movi.n	a4, 2	# shift2,
.L158:
	slli	a3, a8, 2	# tmp295, lag,
	addi.n	a2, a12, 4	# tmp296, ivtmp$240,
	add.n	a3, a3, a2	# _388, tmp295, tmp296
# @OPUS@\upstream\celt\celt_lpc.c:423:       for (i=0;i<=lag;i++)
	bgez	a8, .L160	# lag,
.L161:
# @OPUS@\upstream\celt\celt_lpc.c:425:       shift += shift2;
	add.n	a14, a14, a4	# <retval>, <retval>, shift2
	j	.L155		#
.L160:
# @OPUS@\upstream\celt\celt_lpc.c:424:          ac[i] = SHR32(ac[i], shift2);
	l32i.n	a2, a12, 0	# MEM[base: _399, offset: 0B], MEM[base: _399, offset: 0B]
	ssr	a4	# shift2
	sra	a2, a2	# tmp297, MEM[base: _399, offset: 0B]
# @OPUS@\upstream\celt\celt_lpc.c:424:          ac[i] = SHR32(ac[i], shift2);
	s32i.n	a2, a12, 0	# MEM[base: _399, offset: 0B], tmp297
	addi.n	a12, a12, 4	# ivtmp$240, ivtmp$240,
# @OPUS@\upstream\celt\celt_lpc.c:423:       for (i=0;i<=lag;i++)
	bne	a3, a12, .L160	# _388, ivtmp$240,
	j	.L161		#
.L145:
# @OPUS@\upstream\celt\celt_lpc.c:401:    celt_pitch_xcorr(xptr, xptr, ac, fastN, lag+1, arch);
	l32i	a7, sp, 64	# arch,
	addi.n	a6, a8, 1	#, lag,
	mov.n	a5, a10	#, fastN
	mov.n	a3, a14	#, x
	mov.n	a2, a14	#, x
	mov.n	a4, a12	#, ac
	s32i.n	a8, sp, 24	#,
	s32i.n	a10, sp, 20	#,
	call0	celt_pitch_xcorr_c		#
# @OPUS@\upstream\celt\celt_lpc.c:402:    for (k=0;k<=lag;k++)
	l32i.n	a8, sp, 24	#,
	mov.n	a9, a14	# xx, x
	movi.n	a14, 0	# <retval>,
	l32i.n	a10, sp, 20	#,
	bge	a8, a14, .L162	# lag,,
	l32i.n	a2, a12, 0	# *ac_156(D), pretmp_449
	j	.L163		#
.L192:
# @OPUS@\upstream\celt\celt_lpc.c:390:       shift = celt_ilog2(ac0)-30+10;
	movi.n	a15, 0xb	# tmp304,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a5, a5	# _113, ac0
# @OPUS@\upstream\celt\celt_lpc.c:390:       shift = celt_ilog2(ac0)-30+10;
	sub	a5, a15, a5	# shift, tmp304, _113
# @OPUS@\upstream\celt\celt_lpc.c:391:       shift = (shift)/2;
	srai	a15, a5, 1	# shift, shift,
# @OPUS@\upstream\celt\celt_lpc.c:392:       if (shift>0)
	bgei	a5, 2, .L164	# shift,,
	j	.L145		#
.L148:
	l32i.n	a2, a12, 0	# *ac_156(D), pretmp_449
# @OPUS@\upstream\celt\celt_lpc.c:412:    if (ac[0] < 268435456)
	l32r	a3, .LC14	#, tmp306
	blt	a3, a2, .L153	# tmp306, pretmp_449,
# @OPUS@\upstream\celt\celt_lpc.c:414:       int shift2 = 29 - EC_ILOG(ac[0]);
	nsau	a2, a2	# _196, pretmp_449
# @OPUS@\upstream\celt\celt_lpc.c:414:       int shift2 = 29 - EC_ILOG(ac[0]);
	addi	a3, a2, -3	# shift2, _196,
	j	.L157		#
.L165:
# @OPUS@\upstream\celt\celt_lpc.c:414:       int shift2 = 29 - EC_ILOG(ac[0]);
	nsau	a2, a2	# _286, pretmp_449
# @OPUS@\upstream\celt\celt_lpc.c:414:       int shift2 = 29 - EC_ILOG(ac[0]);
	addi	a3, a2, -3	# shift2, _286,
	j	.L154		#
.L152:
# @OPUS@\upstream\celt\celt_lpc.c:412:    if (ac[0] < 268435456)
	l32r	a3, .LC14	#, tmp307
	bge	a3, a2, .L165	# tmp307, pretmp_449,
	j	.L153		#
.L155:
# @OPUS@\upstream\celt\celt_lpc.c:429:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_lpc.c:431: }
	l32i.n	a0, sp, 60	#,
	mov.n	a2, a14	#, <retval>
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	_celt_autocorr, .-_celt_autocorr
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
