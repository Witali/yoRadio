# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/stereo_find_predictor.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"stereo_find_predictor.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\stereo_find_predictor.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\stereo_find_predictor.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\stereo_find_predictor.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\stereo_find_predictor.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\stereo_find_predictor.c.s.raw
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
	.global	__muldi3
	.section	.text.silk_stereo_find_predictor,"ax",@progbits
	.literal_position
	.literal .LC0, 4096
	.literal .LC1, 16384
	.literal .LC2, 46214
	.literal .LC3, 32768
	.literal .LC4, 32767
	.literal .LC5, 536870911
	.literal .LC6, -2147483648
	.literal .LC7, 2147483647
	.literal .LC8, -16384
	.align	4
	.global	silk_stereo_find_predictor
	.type	silk_stereo_find_predictor, @function
# Function: silk_stereo_find_predictor
# Module: upstream/silk/stereo_find_predictor.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Find least-squares prediction gain for one signal based on another and quantize it */
# C context: opus_int32 silk_stereo_find_predictor(                          /* O    Returns predictor in Q13                    */
# C context: opus_int32                  *ratio_Q14,                     /* O    Ratio of residual and mid energies          */
# C context: const opus_int16            x[],                            /* I    Basis signal                                */
# C context: const opus_int16            y[],                            /* I    Target signal                               */
# C context: opus_int32                  mid_res_amp_Q0[],               /* I/O  Smoothed mid, residual norms                */
silk_stereo_find_predictor:
	addi	sp, sp, -80	#,,
	s32i.n	a15, sp, 60	#,
	mov.n	a15, a3	# x, x
	s32i	a12, sp, 72	#,
	s32i	a14, sp, 64	#,
	mov.n	a12, a4	# y, y
# @OPUS@\upstream\silk\stereo_find_predictor.c:48:     silk_sum_sqr_shift( &nrgx, &scale1, x, length );
	addi.n	a3, sp, 12	#,,
# @OPUS@\upstream\silk\stereo_find_predictor.c:43: {
	s32i.n	a2, sp, 20	# %sfp, ratio_Q14
# @OPUS@\upstream\silk\stereo_find_predictor.c:48:     silk_sum_sqr_shift( &nrgx, &scale1, x, length );
	mov.n	a4, a15	#, x
	addi.n	a2, sp, 4	#,,
# @OPUS@\upstream\silk\stereo_find_predictor.c:43: {
	mov.n	a14, a5	# mid_res_amp_Q0, mid_res_amp_Q0
# @OPUS@\upstream\silk\stereo_find_predictor.c:48:     silk_sum_sqr_shift( &nrgx, &scale1, x, length );
	mov.n	a5, a6	#, length
# @OPUS@\upstream\silk\stereo_find_predictor.c:43: {
	s32i	a0, sp, 76	#,
	s32i	a13, sp, 68	#,
# @OPUS@\upstream\silk\stereo_find_predictor.c:43: {
	s32i.n	a7, sp, 24	# %sfp, smooth_coef_Q16
# @OPUS@\upstream\silk\stereo_find_predictor.c:48:     silk_sum_sqr_shift( &nrgx, &scale1, x, length );
	s32i.n	a6, sp, 44	#,
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\stereo_find_predictor.c:49:     silk_sum_sqr_shift( &nrgy, &scale2, y, length );
	l32i.n	a6, sp, 44	#,
	addi.n	a3, sp, 8	#,,
	mov.n	a5, a6	#, length
	mov.n	a2, sp	#,
	mov.n	a4, a12	#, y
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\stereo_find_predictor.c:50:     scale = silk_max_int( scale1, scale2 );
	l32i.n	a2, sp, 12	# scale1, scale1$0_1
	l32i.n	a3, sp, 8	# scale2, scale2$1_2
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	mov.n	a13, a2	# scale1$0_1, scale1$0_1
	l32i.n	a6, sp, 44	#,
	bge	a2, a3, .L2	# scale1$0_1, scale2$1_2,
	mov.n	a13, a3	# scale1$0_1, scale2$1_2
.L2:
# @OPUS@\upstream\silk\stereo_find_predictor.c:51:     scale = scale + ( scale & 1 );          /* make even */
	movi.n	a4, -2	# tmp275,
# @OPUS@\upstream\silk\stereo_find_predictor.c:51:     scale = scale + ( scale & 1 );          /* make even */
	addi.n	a13, a13, 1	# tmp274, scale1$0_1,
# @OPUS@\upstream\silk\stereo_find_predictor.c:51:     scale = scale + ( scale & 1 );          /* make even */
	and	a13, a13, a4	# scale, tmp274, tmp275
# @OPUS@\upstream\silk\stereo_find_predictor.c:52:     nrgy = silk_RSHIFT32( nrgy, scale - scale2 );
	l32i.n	a4, sp, 0	# nrgy, nrgy
	sub	a3, a13, a3	# tmp276, scale, scale2$1_2
# @OPUS@\upstream\silk\stereo_find_predictor.c:53:     nrgx = silk_RSHIFT32( nrgx, scale - scale1 );
	l32i.n	a7, sp, 4	# nrgx, nrgx
# @OPUS@\upstream\silk\stereo_find_predictor.c:52:     nrgy = silk_RSHIFT32( nrgy, scale - scale2 );
	ssr	a3	# tmp276
	sra	a3, a4	# tmp277, nrgy
# @OPUS@\upstream\silk\stereo_find_predictor.c:53:     nrgx = silk_RSHIFT32( nrgx, scale - scale1 );
	sub	a2, a13, a2	# tmp279, scale, scale1$0_1
# @OPUS@\upstream\silk\stereo_find_predictor.c:52:     nrgy = silk_RSHIFT32( nrgy, scale - scale2 );
	s32i.n	a3, sp, 0	# nrgy, tmp277
# @OPUS@\upstream\silk\stereo_find_predictor.c:53:     nrgx = silk_RSHIFT32( nrgx, scale - scale1 );
	ssr	a2	# tmp279
	sra	a7, a7	# tmp282, nrgx
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	bgei	a7, 1, .L3	# tmp282,,
	movi.n	a7, 1	# tmp282,
.L3:
# @OPUS@\upstream\silk\stereo_find_predictor.c:55:     corr = silk_inner_prod_aligned_scale( x, y, scale, length );
	mov.n	a5, a6	#, length
	mov.n	a4, a13	#, scale
	mov.n	a3, a12	#, y
	mov.n	a2, a15	#, x
# @OPUS@\upstream\silk\stereo_find_predictor.c:54:     nrgx = silk_max_int( nrgx, 1 );
	s32i.n	a7, sp, 4	# nrgx, tmp282
# @OPUS@\upstream\silk\stereo_find_predictor.c:55:     corr = silk_inner_prod_aligned_scale( x, y, scale, length );
	call0	silk_inner_prod_aligned_scale		#
	mov.n	a6, a2	# corr,
# @OPUS@\upstream\silk\stereo_find_predictor.c:56:     pred_Q13 = silk_DIV32_varQ( corr, nrgx, 13 );
	l32i.n	a8, sp, 4	# nrgx, nrgx$7_10
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a2, .L41	# corr,
# @OPUS@\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	abs	a11, a2	# tmp285, corr
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a15, a11	# iftmp$22_105, tmp285
	addi	a2, a15, 16	#, iftmp$22_105,
	addi.n	a12, a15, -1	# _629, iftmp$22_105,
	s32i.n	a2, sp, 16	# %sfp,
	j	.L4		#
.L41:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a3, 0x30	#,
	s32i.n	a3, sp, 16	# %sfp,
	movi.n	a12, 0x1f	# _629,
	movi.n	a15, 0x20	# iftmp$22_105,
.L4:
# @OPUS@\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a12	# _629
	sll	a12, a6	# _109, corr
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a8, .L42	# nrgx$7_10,
# @OPUS@\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a11, a8	# tmp286, nrgx$7_10
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a11, a11	# iftmp$22_113, tmp286
	addi.n	a10, a11, -1	# _669, iftmp$22_113,
	j	.L5		#
.L42:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a10, 0x1f	# _669,
	movi.n	a11, 0x20	# iftmp$22_113,
.L5:
# @OPUS@\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a10	# _669
	sll	a10, a8	# b32_nrm, nrgx$7_10
# @OPUS@\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC5	#,
	srai	a3, a10, 16	#, b32_nrm,
	s32i.n	a6, sp, 44	#,
	s32i.n	a8, sp, 40	#,
	s32i.n	a11, sp, 32	#,
	s32i.n	a10, sp, 28	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp292,,
	srai	a9, a2, 16	# _123, tmp292,
	extui	a7, a12, 0, 16	# tmp293, _109,
	mull	a7, a7, a9	# tmp294, tmp293, _123
	srai	a2, a12, 16	# tmp296, _109,
	mull	a2, a2, a9	# tmp297, tmp296, _123
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i.n	a10, sp, 28	#,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a7, a7, 16	# tmp295, tmp294,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a7, a2	# result, tmp295, tmp297
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a7	#, result
	srai	a5, a7, 31	#, result,
	mov.n	a2, a10	#, b32_nrm
	srai	a3, a10, 31	#, b32_nrm,
	s32i.n	a7, sp, 28	#,
	s32i.n	a9, sp, 36	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp304,,
	sub	a12, a12, a3	# a32_nrm, _109, tmp304
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i.n	a9, sp, 36	#,
	srai	a2, a12, 16	# tmp305, a32_nrm,
	mull	a2, a2, a9	# tmp306, tmp305, _123
	l32i.n	a7, sp, 28	#,
	extui	a12, a12, 0, 16	# tmp307, a32_nrm,
	mull	a9, a12, a9	# tmp308, tmp307, _123
	add.n	a7, a2, a7	# _290, tmp306, result
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i.n	a11, sp, 32	#,
	l32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a9, a9, 16	# tmp309, tmp308,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a12, a2, a11	# lshift,, iftmp$22_113
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a9, a9, a7	# result, tmp309, _290
# @OPUS@\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i.n	a6, sp, 44	#,
	l32i.n	a8, sp, 40	#,
	bgez	a12, .L6	# lshift,
# @OPUS@\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a11, a11, a15	# tmp311, iftmp$22_113, iftmp$22_105
	l32r	a2, .LC6	#, tmp312
	l32r	a3, .LC7	#, tmp313
	addi	a11, a11, -16	# _149, tmp311,
	ssr	a11	# _149
	sra	a2, a2	# _150, tmp312
	ssr	a11	# _149
	sra	a3, a3	# _151, tmp313
	bge	a3, a2, .L7	# _151, _150,
	bge	a2, a9, .L8	# _150, result,
	j	.L52		#
.L8:
	bge	a9, a3, .L9	# iftmp$28_152, _151,
	j	.L53		#
.L7:
	bge	a3, a9, .L11	# _151, result,
.L53:
	mov.n	a9, a3	# iftmp$28_152, _151
	j	.L9		#
.L11:
	bge	a9, a2, .L9	# iftmp$28_152, _150,
.L52:
	mov.n	a9, a2	# iftmp$28_152, _150
.L9:
	ssl	a11	# _149
	sll	a9, a9	# _161, iftmp$28_152
	j	.L13		#
.L6:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a2, 0x1f	# tmp314,
	blt	a2, a12, .L43	# tmp314, lshift,
# @OPUS@\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a12	# lshift
	sra	a9, a9	# _161, result
.L13:
# @OPUS@\upstream\silk\stereo_find_predictor.c:57:     pred_Q13 = silk_LIMIT( pred_Q13, -(1 << 14), 1 << 14 );
	l32r	a12, .LC1	#, tmp315
	srai	a7, a6, 16	# _1011, corr,
	srai	a3, a8, 16	# _1013, nrgx$7_10,
	extui	a6, a6, 0, 16	# _1012, corr,
	extui	a2, a8, 0, 16	# _1014, nrgx$7_10,
	bge	a12, a9, .L15	# tmp315, _161,
	srli	a6, a6, 2	# tmp317, _1012,
	slli	a7, a7, 14	# tmp318, _1011,
	srli	a4, a2, 4	# tmp321, _1014,
	slli	a3, a3, 12	# tmp322, _1013,
	add.n	a6, a6, a7	# tmp319, tmp317, tmp318
	add.n	a4, a4, a3	# tmp323, tmp321, tmp322
	slli	a6, a6, 4	# prephitmp_917, tmp319,
	slli	a4, a4, 6	# prephitmp_933, tmp323,
	l32r	a5, .LC0	#, prephitmp_698
	j	.L16		#
.L15:
	l32r	a4, .LC8	#, tmp328
	mov.n	a12, a9	# <retval>, _161
	bge	a9, a4, .L17	# <retval>, tmp328,
	mov.n	a12, a4	# <retval>, tmp328
.L17:
	extui	a5, a12, 0, 16	# tmp329, <retval>,
	mull	a5, a5, a12	# tmp330, tmp329, <retval>
	srai	a4, a12, 16	# tmp332, <retval>,
	mull	a4, a4, a12	# tmp333, tmp332, <retval>
	srai	a5, a5, 16	# tmp331, tmp330,
	add.n	a5, a5, a4	# _898, tmp331, tmp333
	mull	a4, a5, a2	# tmp338, _898, _1014
	mull	a6, a12, a6	# tmp334, <retval>, _1012
	mull	a3, a5, a3	# tmp340, _898, _1013
	mull	a7, a12, a7	# tmp336, <retval>, _1011
	srai	a6, a6, 16	# tmp335, tmp334,
	srai	a4, a4, 16	# tmp339, tmp338,
	add.n	a6, a6, a7	# tmp337, tmp335, tmp336
	add.n	a4, a4, a3	# tmp341, tmp339, tmp340
	abs	a5, a5	# prephitmp_698, _898
	slli	a6, a6, 4	# prephitmp_917, tmp337,
	slli	a4, a4, 6	# prephitmp_933, tmp341,
	j	.L16		#
.L43:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a4, 0	# prephitmp_933,
	mov.n	a6, a4	# prephitmp_917, prephitmp_933
	mov.n	a5, a4	# prephitmp_698, prephitmp_933
	mov.n	a12, a4	# <retval>, prephitmp_933
.L16:
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	l32i.n	a3, sp, 24	# %sfp, _92
	bge	a3, a5, .L18	# _92, prephitmp_698,
	mov.n	a3, a5	# _92, prephitmp_698
.L18:
# @OPUS@\upstream\silk\stereo_find_predictor.c:65:     scale = silk_RSHIFT( scale, 1 );
	srai	a13, a13, 1	# scale, scale,
# @OPUS@\upstream\silk\stereo_find_predictor.c:66:     mid_res_amp_Q0[ 0 ] = silk_SMLAWB( mid_res_amp_Q0[ 0 ], silk_LSHIFT( silk_SQRT_APPROX( nrgx ), scale ) - mid_res_amp_Q0[ 0 ],
	l32i.n	a7, a14, 0	# *mid_res_amp_Q0_90(D), _19
# @OPUS@\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	movi.n	a2, 0	# _733,
	blti	a8, 1, .L19	# nrgx$7_10,,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a2, a8	# iftmp$22_250, nrgx$7_10
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a9, 0x18	# tmp342,
	sub	a9, a9, a2	# _251, tmp342, iftmp$22_250
# @OPUS@\upstream\silk\SigProc_FIX.h:403:     if( rot == 0 ) {
	beqz.n	a9, .L20	# _251,
# @OPUS@\upstream\silk\SigProc_FIX.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a9	# _251
	src	a5, a8, a8	# _259, nrgx$7_10
# @OPUS@\upstream\silk\SigProc_FIX.h:405:     } else if( rot < 0 ) {
	bgez	a9, .L22	# _251,
# @OPUS@\upstream\silk\SigProc_FIX.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a5, a2, -24	# m, iftmp$22_250,
# @OPUS@\upstream\silk\SigProc_FIX.h:406:         return (opus_int32) ((x << m) | (x >> (32 - m)));
	ssl	a5	# m
	src	a5, a8, a8	# _259, nrgx$7_10
.L22:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a8, a5, 0, 7	# _208, _259,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a10, .LC2	#, tmp469
	l32r	a5, .LC3	#, tmp470
# @OPUS@\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	extui	a9, a2, 0, 1	# tmp344, iftmp$22_250,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	moveqz	a5, a10, a9	# tmp470, tmp469, tmp344
	mov.n	a9, a5	# y, tmp470
.L23:
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a5, a8, 3	# tmp348, _208,
	add.n	a5, a8, a5	# tmp350, _208, tmp348
	slli	a5, a5, 3	# tmp352, tmp350,
	sub	a8, a5, a8	# tmp354, tmp352, _208
	slli	a5, a8, 2	# tmp356, tmp354,
	sub	a5, a5, a8	# tmp359, tmp356, tmp354
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	srai	a2, a2, 1	# tmp345, iftmp$22_250,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a5, a5, 16	# tmp361, tmp359,
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	ssr	a2	# tmp345
	sra	a2, a9	# y, y
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a5, a5, 16	# tmp360, tmp361,
	mull	a5, a5, a2	# tmp362, tmp360, y
	srai	a5, a5, 16	# _271, tmp362,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	add.n	a2, a2, a5	# y, y, _271
	ssl	a13	# scale
	sll	a2, a2	# _733, y
.L19:
# @OPUS@\upstream\silk\stereo_find_predictor.c:66:     mid_res_amp_Q0[ 0 ] = silk_SMLAWB( mid_res_amp_Q0[ 0 ], silk_LSHIFT( silk_SQRT_APPROX( nrgx ), scale ) - mid_res_amp_Q0[ 0 ],
	sub	a2, a2, a7	# _24, _733, _19
	slli	a3, a3, 16	# tmp364, _92,
	srai	a5, a3, 16	# _27, tmp364,
	extui	a3, a2, 0, 16	# tmp365, _24,
	srai	a2, a2, 16	# tmp368, _24,
	mull	a3, a3, a5	# tmp366, tmp365, _27
	mull	a2, a2, a5	# tmp369, tmp368, _27
	srai	a3, a3, 16	# tmp367, tmp366,
	add.n	a2, a2, a7	# tmp370, tmp369, _19
	add.n	a2, a3, a2	# _33, tmp367, tmp370
# @OPUS@\upstream\silk\stereo_find_predictor.c:70:     nrgy = silk_ADD_LSHIFT32( nrgy, silk_SMULWB( nrgx, pred2_Q10 ), 6 );
	l32i.n	a3, sp, 0	# nrgy, nrgy
# @OPUS@\upstream\silk\stereo_find_predictor.c:66:     mid_res_amp_Q0[ 0 ] = silk_SMLAWB( mid_res_amp_Q0[ 0 ], silk_LSHIFT( silk_SQRT_APPROX( nrgx ), scale ) - mid_res_amp_Q0[ 0 ],
	s32i.n	a2, a14, 0	# *mid_res_amp_Q0_90(D), _33
# @OPUS@\upstream\silk\stereo_find_predictor.c:70:     nrgy = silk_ADD_LSHIFT32( nrgy, silk_SMULWB( nrgx, pred2_Q10 ), 6 );
	add.n	a4, a4, a3	# tmp371, prephitmp_933, nrgy
	sub	a6, a4, a6	# _56, tmp371, prephitmp_917
# @OPUS@\upstream\silk\stereo_find_predictor.c:71:     mid_res_amp_Q0[ 1 ] = silk_SMLAWB( mid_res_amp_Q0[ 1 ], silk_LSHIFT( silk_SQRT_APPROX( nrgy ), scale ) - mid_res_amp_Q0[ 1 ],
	l32i.n	a7, a14, 4	# MEM[(opus_int32 *)mid_res_amp_Q0_90(D) + 4B], _57
# @OPUS@\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	movi.n	a3, 0	# _739,
	blti	a6, 1, .L24	# _56,,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a4, a6	# iftmp$22_224, _56
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a3, 0x18	# tmp373,
	sub	a3, a3, a4	# _225, tmp373, iftmp$22_224
# @OPUS@\upstream\silk\SigProc_FIX.h:403:     if( rot == 0 ) {
	beqz.n	a3, .L25	# _225,
# @OPUS@\upstream\silk\SigProc_FIX.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a3	# _225
	src	a8, a6, a6	# _233, _56
# @OPUS@\upstream\silk\SigProc_FIX.h:405:     } else if( rot < 0 ) {
	bgez	a3, .L27	# _225,
# @OPUS@\upstream\silk\SigProc_FIX.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a8, a4, -24	# m, iftmp$22_224,
# @OPUS@\upstream\silk\SigProc_FIX.h:406:         return (opus_int32) ((x << m) | (x >> (32 - m)));
	ssl	a8	# m
	src	a8, a6, a6	# _233, _56
.L27:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a9, a8, 0, 7	# _205, _233,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a6, .LC3	#, tmp474
	l32r	a8, .LC2	#, tmp473
# @OPUS@\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	extui	a3, a4, 0, 1	# tmp375, iftmp$22_224,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	moveqz	a6, a8, a3	# tmp474, tmp473, tmp375
	mov.n	a3, a6	# y, tmp474
.L28:
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a8, a9, 3	# tmp379, _205,
	add.n	a8, a9, a8	# tmp381, _205, tmp379
	slli	a6, a8, 3	# tmp383, tmp381,
	sub	a8, a6, a9	# tmp385, tmp383, _205
	slli	a6, a8, 2	# tmp387, tmp385,
	sub	a6, a6, a8	# tmp390, tmp387, tmp385
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	srai	a4, a4, 1	# tmp376, iftmp$22_224,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a6, a6, 16	# tmp392, tmp390,
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	ssr	a4	# tmp376
	sra	a3, a3	# y, y
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a4, a6, 16	# tmp391, tmp392,
	mull	a4, a4, a3	# tmp393, tmp391, y
	srai	a4, a4, 16	# _245, tmp393,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	add.n	a3, a3, a4	# y, y, _245
	ssl	a13	# scale
	sll	a3, a3	# _739, y
.L24:
# @OPUS@\upstream\silk\stereo_find_predictor.c:71:     mid_res_amp_Q0[ 1 ] = silk_SMLAWB( mid_res_amp_Q0[ 1 ], silk_LSHIFT( silk_SQRT_APPROX( nrgy ), scale ) - mid_res_amp_Q0[ 1 ],
	sub	a3, a3, a7	# _62, _739, _57
	extui	a4, a3, 0, 16	# tmp395, _62,
	srai	a3, a3, 16	# tmp398, _62,
	mull	a4, a4, a5	# tmp396, tmp395, _27
	mull	a3, a3, a5	# tmp399, tmp398, _27
	srai	a4, a4, 16	# tmp397, tmp396,
	add.n	a3, a3, a7	# tmp400, tmp399, _57
	add.n	a4, a4, a3	# _69, tmp397, tmp400
# @OPUS@\upstream\silk\stereo_find_predictor.c:71:     mid_res_amp_Q0[ 1 ] = silk_SMLAWB( mid_res_amp_Q0[ 1 ], silk_LSHIFT( silk_SQRT_APPROX( nrgy ), scale ) - mid_res_amp_Q0[ 1 ],
	s32i.n	a4, a14, 4	# MEM[(opus_int32 *)mid_res_amp_Q0_90(D) + 4B], _69
# @OPUS@\upstream\silk\stereo_find_predictor.c:75:     *ratio_Q14 = silk_DIV32_varQ( mid_res_amp_Q0[ 1 ], silk_max( mid_res_amp_Q0[ 0 ], 1 ), 14 );
	bgei	a2, 1, .L29	# _70,,
	movi.n	a2, 1	# _70,
.L29:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a4, .L48	# _69,
# @OPUS@\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	abs	a14, a4	# tmp403, _69
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a14, a14	# iftmp$22_165, tmp403
	addi.n	a7, a14, -1	# _789, iftmp$22_165,
	addi.n	a6, a14, 15	# _791, iftmp$22_165,
	j	.L30		#
.L48:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a6, 0x2f	# _791,
	movi.n	a7, 0x1f	# _789,
	movi.n	a14, 0x20	# iftmp$22_165,
.L30:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a13, a2	# iftmp$22_173, _70
# @OPUS@\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	addi.n	a10, a13, -1	# b_headrm, iftmp$22_173,
# @OPUS@\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a10	# b_headrm
	sll	a10, a2	# b32_nrm, _70
# @OPUS@\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC5	#,
	srai	a3, a10, 16	#, b32_nrm,
# @OPUS@\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a7	# _789
	sll	a15, a4	# _169, _69
# @OPUS@\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	s32i.n	a6, sp, 44	#,
	s32i.n	a10, sp, 28	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp410,,
	srai	a9, a2, 16	# _183, tmp410,
	extui	a8, a15, 0, 16	# tmp411, _169,
	mull	a8, a8, a9	# tmp412, tmp411, _183
	srai	a3, a15, 16	# tmp414, _169,
	mull	a3, a3, a9	# tmp415, tmp414, _183
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i.n	a10, sp, 28	#,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a8, a8, 16	# tmp413, tmp412,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a8, a8, a3	# result, tmp413, tmp415
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a8	#, result
	srai	a5, a8, 31	#, result,
	mov.n	a2, a10	#, b32_nrm
	srai	a3, a10, 31	#, b32_nrm,
	s32i.n	a8, sp, 40	#,
	s32i.n	a9, sp, 36	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp422,,
	sub	a3, a15, a3	# a32_nrm, _169, tmp422
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i.n	a9, sp, 36	#,
	srai	a2, a3, 16	# tmp423, a32_nrm,
	extui	a3, a3, 0, 16	# tmp425, a32_nrm,
	mull	a2, a2, a9	# tmp424, tmp423, _183
	mull	a3, a3, a9	# tmp426, tmp425, _183
	l32i.n	a8, sp, 40	#,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i.n	a6, sp, 44	#,
	add.n	a8, a2, a8	# _294, tmp424, result
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a3, a3, 16	# tmp427, tmp426,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a6, a6, a13	# lshift, _791, iftmp$22_173
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a3, a3, a8	# result, tmp427, _294
# @OPUS@\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	bgez	a6, .L31	# lshift,
# @OPUS@\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	addi	a13, a13, -15	# tmp428, iftmp$22_173,
	l32r	a2, .LC6	#, tmp429
	l32r	a4, .LC7	#, tmp430
	sub	a14, a13, a14	# _209, tmp428, iftmp$22_165
	ssr	a14	# _209
	sra	a2, a2	# _210, tmp429
	ssr	a14	# _209
	sra	a4, a4	# _211, tmp430
	bge	a4, a2, .L32	# _211, _210,
	bge	a2, a3, .L33	# _210, result,
	j	.L54		#
.L33:
	bge	a3, a4, .L34	# iftmp$28_212, _211,
	j	.L55		#
.L32:
	bge	a4, a3, .L36	# _211, result,
.L55:
	mov.n	a3, a4	# iftmp$28_212, _211
	j	.L34		#
.L36:
	bge	a3, a2, .L34	# iftmp$28_212, _210,
.L54:
	mov.n	a3, a2	# iftmp$28_212, _210
.L34:
	ssl	a14	# _209
	sll	a3, a3	# _221, iftmp$28_212
	j	.L38		#
.L31:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a4, 0x1f	# tmp431,
	movi.n	a2, 0	# iftmp$17_73,
	blt	a4, a6, .L40	# tmp431, lshift,
# @OPUS@\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a6	# lshift
	sra	a3, a3	# _221, result
.L38:
# @OPUS@\upstream\silk\stereo_find_predictor.c:76:     *ratio_Q14 = silk_LIMIT( *ratio_Q14, 0, 32767 );
	l32r	a2, .LC4	#, iftmp$17_73
	blt	a2, a3, .L40	# iftmp$17_73, _221,
	movi.n	a2, 0	# tmp433,
	movgez	a2, a3, a3	# iftmp$17_73, _221, _221
	j	.L40		#
.L25:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a9, a6, 0, 7	# _205, _56,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a3, .LC2	#, y
	j	.L28		#
.L20:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a8, a8, 0, 7	# _208, nrgx$7_10,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a9, .LC2	#, y
	j	.L23		#
.L40:
# @OPUS@\upstream\silk\stereo_find_predictor.c:76:     *ratio_Q14 = silk_LIMIT( *ratio_Q14, 0, 32767 );
	l32i.n	a3, sp, 20	# %sfp,
# @OPUS@\upstream\silk\stereo_find_predictor.c:79: }
	l32i	a0, sp, 76	#,
# @OPUS@\upstream\silk\stereo_find_predictor.c:76:     *ratio_Q14 = silk_LIMIT( *ratio_Q14, 0, 32767 );
	s32i.n	a2, a3, 0	# *ratio_Q14_96(D), iftmp$17_73
# @OPUS@\upstream\silk\stereo_find_predictor.c:79: }
	l32i	a13, sp, 68	#,
	mov.n	a2, a12	#, <retval>
	l32i	a14, sp, 64	#,
	l32i	a12, sp, 72	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	silk_stereo_find_predictor, .-silk_stereo_find_predictor
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
