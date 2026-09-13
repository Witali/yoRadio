# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/VQ_WMat_EC.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"VQ_WMat_EC.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\VQ_WMat_EC.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\VQ_WMat_EC.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\VQ_WMat_EC.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\VQ_WMat_EC.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\VQ_WMat_EC.c.s.raw
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
	.section	.text.silk_VQ_WMat_EC_c,"ax",@progbits
	.literal_position
	.literal .LC0, 2147483647
	.literal .LC1, 32801
	.align	4
	.global	silk_VQ_WMat_EC_c
	.type	silk_VQ_WMat_EC_c, @function
# Function: silk_VQ_WMat_EC_c
# Module: upstream/silk/VQ_WMat_EC.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Entropy constrained matrix-weighted VQ, hard-coded to 5-element vectors, for a single input data vector */
# C context: void silk_VQ_WMat_EC_c(
# C context: opus_int8                   *ind,                           /* O    index of best codebook vector               */
# C context: opus_int32                  *res_nrg_Q15,                   /* O    best residual energy                        */
# C context: opus_int32                  *rate_dist_Q8,                  /* O    best total bitrate                          */
# C context: opus_int                    *gain_Q7,                       /* O    sum of absolute LTP coefficients            */
silk_VQ_WMat_EC_c:
	addi	sp, sp, -96	#,,
	s32i.n	a4, sp, 44	# %sfp, rate_dist_Q8
	s32i	a12, sp, 88	#,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:64:     *rate_dist_Q8 = silk_int32_MAX;
	l32r	a11, .LC0	#, tmp213
	l32i.n	a12, sp, 44	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:49: {
	s32i	a14, sp, 80	#,
	s32i	a15, sp, 76	#,
	s32i	a0, sp, 92	#,
	s32i	a13, sp, 84	#,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:57:     neg_xX_Q24[ 0 ] = -silk_LSHIFT32( xX_Q17[ 0 ], 7 );
	l32i.n	a10, a7, 0	# *xX_Q17_132(D), *xX_Q17_132(D)
# @OPUS@\upstream\silk\VQ_WMat_EC.c:58:     neg_xX_Q24[ 1 ] = -silk_LSHIFT32( xX_Q17[ 1 ], 7 );
	l32i.n	a9, a7, 4	# MEM[(const opus_int32 *)xX_Q17_132(D) + 4B], MEM[(const opus_int32 *)xX_Q17_132(D) + 4B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:59:     neg_xX_Q24[ 2 ] = -silk_LSHIFT32( xX_Q17[ 2 ], 7 );
	l32i.n	a8, a7, 8	# MEM[(const opus_int32 *)xX_Q17_132(D) + 8B], MEM[(const opus_int32 *)xX_Q17_132(D) + 8B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:60:     neg_xX_Q24[ 3 ] = -silk_LSHIFT32( xX_Q17[ 3 ], 7 );
	l32i.n	a4, a7, 12	# MEM[(const opus_int32 *)xX_Q17_132(D) + 12B], MEM[(const opus_int32 *)xX_Q17_132(D) + 12B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:49: {
	s32i.n	a2, sp, 48	# %sfp, ind
# @OPUS@\upstream\silk\VQ_WMat_EC.c:61:     neg_xX_Q24[ 4 ] = -silk_LSHIFT32( xX_Q17[ 4 ], 7 );
	l32i.n	a7, a7, 16	# MEM[(const opus_int32 *)xX_Q17_132(D) + 16B], MEM[(const opus_int32 *)xX_Q17_132(D) + 16B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:64:     *rate_dist_Q8 = silk_int32_MAX;
	s32i.n	a11, a12, 0	# *rate_dist_Q8_133(D), tmp213
# @OPUS@\upstream\silk\VQ_WMat_EC.c:65:     *res_nrg_Q15 = silk_int32_MAX;
	s32i.n	a11, a3, 0	# *res_nrg_Q15_135(D), tmp213
# @OPUS@\upstream\silk\VQ_WMat_EC.c:68:     *ind = 0;
	l32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:61:     neg_xX_Q24[ 4 ] = -silk_LSHIFT32( xX_Q17[ 4 ], 7 );
	slli	a2, a7, 7	# tmp211, MEM[(const opus_int32 *)xX_Q17_132(D) + 16B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:49: {
	s32i.n	a3, sp, 52	# %sfp, res_nrg_Q15
# @OPUS@\upstream\silk\VQ_WMat_EC.c:68:     *ind = 0;
	movi.n	a7, 0	# tmp215,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:57:     neg_xX_Q24[ 0 ] = -silk_LSHIFT32( xX_Q17[ 0 ], 7 );
	slli	a10, a10, 7	#, *xX_Q17_132(D),
# @OPUS@\upstream\silk\VQ_WMat_EC.c:58:     neg_xX_Q24[ 1 ] = -silk_LSHIFT32( xX_Q17[ 1 ], 7 );
	slli	a9, a9, 7	#, MEM[(const opus_int32 *)xX_Q17_132(D) + 4B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:59:     neg_xX_Q24[ 2 ] = -silk_LSHIFT32( xX_Q17[ 2 ], 7 );
	slli	a8, a8, 7	#, MEM[(const opus_int32 *)xX_Q17_132(D) + 8B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:60:     neg_xX_Q24[ 3 ] = -silk_LSHIFT32( xX_Q17[ 3 ], 7 );
	slli	a4, a4, 7	#, MEM[(const opus_int32 *)xX_Q17_132(D) + 12B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:49: {
	l32i	a3, sp, 116	# L, L
# @OPUS@\upstream\silk\VQ_WMat_EC.c:68:     *ind = 0;
	s8i	a7, a11, 0	# *ind_138(D), tmp215
# @OPUS@\upstream\silk\VQ_WMat_EC.c:49: {
	s32i.n	a5, sp, 56	# %sfp, gain_Q7
# @OPUS@\upstream\silk\VQ_WMat_EC.c:57:     neg_xX_Q24[ 0 ] = -silk_LSHIFT32( xX_Q17[ 0 ], 7 );
	s32i.n	a10, sp, 20	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:58:     neg_xX_Q24[ 1 ] = -silk_LSHIFT32( xX_Q17[ 1 ], 7 );
	s32i.n	a9, sp, 24	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:59:     neg_xX_Q24[ 2 ] = -silk_LSHIFT32( xX_Q17[ 2 ], 7 );
	s32i.n	a8, sp, 28	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:60:     neg_xX_Q24[ 3 ] = -silk_LSHIFT32( xX_Q17[ 3 ], 7 );
	s32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:49: {
	mov.n	a15, a6	# XX_Q17, XX_Q17
	l32i	a14, sp, 96	# cb_Q7, cb_Q7
# @OPUS@\upstream\silk\VQ_WMat_EC.c:61:     neg_xX_Q24[ 4 ] = -silk_LSHIFT32( xX_Q17[ 4 ], 7 );
	neg	a2, a2	# _21, tmp211
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	blti	a3, 1, .L1	# L,,
	slli	a4, a3, 2	# tmp217, L,
	add.n	a3, a4, a3	# tmp218, tmp217, L
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	movi.n	a12, 0	#,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:110:         sum2_Q24 = silk_LSHIFT32( neg_xX_Q24[ 4 ], 1 );
	slli	a2, a2, 1	#, _21,
	add.n	a3, a14, a3	#, cb_Q7, tmp218
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	s32i.n	a12, sp, 12	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:110:         sum2_Q24 = silk_LSHIFT32( neg_xX_Q24[ 4 ], 1 );
	s32i.n	a2, sp, 36	# %sfp,
	s32i.n	a3, sp, 40	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:117:             bits_res_Q8 = silk_SMULBB( subfr_len, silk_lin2log( sum1_Q15 + penalty) - (15 << 7) );
	mov.n	a13, a14	# cb_Q7, cb_Q7
.L6:
# @OPUS@\upstream\silk\VQ_WMat_EC.c:83:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  4 ], cb_row_Q7[ 4 ] );
	l8ui	a6, a13, 4	# MEM[base: cb_row_Q7_146, offset: 4B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:80:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 0 ], XX_Q17[  1 ], cb_row_Q7[ 1 ] );
	l8ui	a2, a13, 1	# MEM[base: cb_row_Q7_146, offset: 1B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:111:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 24 ], cb_row_Q7[ 4 ] );
	l32i	a5, a15, 96	# MEM[(const opus_int32 *)XX_Q17_145(D) + 96B], MEM[(const opus_int32 *)XX_Q17_145(D) + 96B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:83:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  4 ], cb_row_Q7[ 4 ] );
	slli	a6, a6, 24	# tmp233, MEM[base: cb_row_Q7_146, offset: 4B],
	srai	a6, a6, 24	# _43, tmp233,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	l8ui	a12, a13, 2	# MEM[base: cb_row_Q7_146, offset: 2B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:80:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 0 ], XX_Q17[  1 ], cb_row_Q7[ 1 ] );
	slli	a2, a2, 24	# tmp220, MEM[base: cb_row_Q7_146, offset: 1B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:111:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 24 ], cb_row_Q7[ 4 ] );
	l32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:111:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 24 ], cb_row_Q7[ 4 ] );
	mull	a5, a6, a5	# tmp264, _43, MEM[(const opus_int32 *)XX_Q17_145(D) + 96B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:80:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 0 ], XX_Q17[  1 ], cb_row_Q7[ 1 ] );
	srai	a2, a2, 24	#, tmp220,
	s32i.n	a2, sp, 8	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:82:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  3 ], cb_row_Q7[ 3 ] );
	l8ui	a7, a13, 3	# MEM[base: cb_row_Q7_146, offset: 3B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	slli	a12, a12, 24	# tmp222, MEM[base: cb_row_Q7_146, offset: 2B],
	srai	a14, a12, 24	# _35, tmp222,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:111:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 24 ], cb_row_Q7[ 4 ] );
	add.n	a5, a5, a9	# sum2_Q24, tmp264,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:80:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 0 ], XX_Q17[  1 ], cb_row_Q7[ 1 ] );
	l32i.n	a12, sp, 8	# %sfp,
	l32i.n	a9, a15, 4	# MEM[(const opus_int32 *)XX_Q17_145(D) + 4B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:97:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 2 ], XX_Q17[ 13 ], cb_row_Q7[ 3 ] );
	l32i.n	a8, a15, 52	# MEM[(const opus_int32 *)XX_Q17_145(D) + 52B], MEM[(const opus_int32 *)XX_Q17_145(D) + 52B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:98:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 14 ], cb_row_Q7[ 4 ] );
	l32i.n	a4, a15, 56	# MEM[(const opus_int32 *)XX_Q17_145(D) + 56B], MEM[(const opus_int32 *)XX_Q17_145(D) + 56B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:82:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  3 ], cb_row_Q7[ 3 ] );
	slli	a7, a7, 24	# tmp229, MEM[base: cb_row_Q7_146, offset: 3B],
	srai	a7, a7, 24	# _39, tmp229,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:80:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 0 ], XX_Q17[  1 ], cb_row_Q7[ 1 ] );
	mull	a12, a12, a9	#,,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:97:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 2 ], XX_Q17[ 13 ], cb_row_Q7[ 3 ] );
	mull	a8, a7, a8	# tmp251, _39, MEM[(const opus_int32 *)XX_Q17_145(D) + 52B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:104:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 3 ], XX_Q17[ 19 ], cb_row_Q7[ 4 ] );
	l32i	a3, a15, 76	# MEM[(const opus_int32 *)XX_Q17_145(D) + 76B], MEM[(const opus_int32 *)XX_Q17_145(D) + 76B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:98:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 14 ], cb_row_Q7[ 4 ] );
	mull	a4, a6, a4	# tmp253, _43, MEM[(const opus_int32 *)XX_Q17_145(D) + 56B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:80:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 0 ], XX_Q17[  1 ], cb_row_Q7[ 1 ] );
	s32i.n	a12, sp, 0	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	l32i.n	a12, a15, 8	# MEM[(const opus_int32 *)XX_Q17_145(D) + 8B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:104:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 3 ], XX_Q17[ 19 ], cb_row_Q7[ 4 ] );
	mull	a3, a6, a3	# tmp259, _43, MEM[(const opus_int32 *)XX_Q17_145(D) + 76B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:98:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 14 ], cb_row_Q7[ 4 ] );
	add.n	a4, a8, a4	# tmp255, tmp251, tmp253
# @OPUS@\upstream\silk\VQ_WMat_EC.c:105:         sum2_Q24 = silk_LSHIFT32( sum2_Q24, 1 );
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	mull	a9, a14, a12	# tmp225, _35,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:106:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 18 ], cb_row_Q7[ 3 ] );
	l32i	a12, a15, 72	# MEM[(const opus_int32 *)XX_Q17_145(D) + 72B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:105:         sum2_Q24 = silk_LSHIFT32( sum2_Q24, 1 );
	sub	a3, a3, a8	# tmp261, tmp259,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	l8ui	a8, a13, 0	# MEM[base: cb_row_Q7_146, offset: 0B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:106:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 18 ], cb_row_Q7[ 3 ] );
	mull	a12, a7, a12	#, _39,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	s8i	a8, sp, 4	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:100:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 12 ], cb_row_Q7[ 2 ] );
	l32i.n	a8, a15, 48	# MEM[(const opus_int32 *)XX_Q17_145(D) + 48B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:106:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 18 ], cb_row_Q7[ 3 ] );
	s32i.n	a12, sp, 16	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:100:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 12 ], cb_row_Q7[ 2 ] );
	mull	a12, a14, a8	# tmp257, _35,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:106:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 18 ], cb_row_Q7[ 3 ] );
	l32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:105:         sum2_Q24 = silk_LSHIFT32( sum2_Q24, 1 );
	slli	a3, a3, 1	# sum2_Q24, tmp261,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:106:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 18 ], cb_row_Q7[ 3 ] );
	add.n	a3, a8, a3	# sum2_Q24,, sum2_Q24
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	l32i.n	a8, sp, 0	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:90:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  8 ], cb_row_Q7[ 3 ] );
	l32i.n	a11, a15, 32	# MEM[(const opus_int32 *)XX_Q17_145(D) + 32B], MEM[(const opus_int32 *)XX_Q17_145(D) + 32B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:89:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 1 ], XX_Q17[  7 ], cb_row_Q7[ 2 ] );
	l32i.n	a10, a15, 28	# MEM[(const opus_int32 *)XX_Q17_145(D) + 28B], MEM[(const opus_int32 *)XX_Q17_145(D) + 28B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	add.n	a9, a8, a9	# tmp227,, tmp225
# @OPUS@\upstream\silk\VQ_WMat_EC.c:82:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  3 ], cb_row_Q7[ 3 ] );
	l32i.n	a8, a15, 12	# MEM[(const opus_int32 *)XX_Q17_145(D) + 12B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:89:         sum2_Q24 = silk_MLA( neg_xX_Q24[ 1 ], XX_Q17[  7 ], cb_row_Q7[ 2 ] );
	mull	a10, a14, a10	# tmp241, _35, MEM[(const opus_int32 *)XX_Q17_145(D) + 28B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:90:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  8 ], cb_row_Q7[ 3 ] );
	mull	a2, a7, a11	# tmp243, _39, MEM[(const opus_int32 *)XX_Q17_145(D) + 32B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:82:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  3 ], cb_row_Q7[ 3 ] );
	mull	a8, a7, a8	#, _39,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:90:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  8 ], cb_row_Q7[ 3 ] );
	add.n	a2, a10, a2	# tmp245, tmp241, tmp243
# @OPUS@\upstream\silk\VQ_WMat_EC.c:82:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  3 ], cb_row_Q7[ 3 ] );
	s32i.n	a8, sp, 0	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:98:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 14 ], cb_row_Q7[ 4 ] );
	l32i.n	a10, sp, 28	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:90:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  8 ], cb_row_Q7[ 3 ] );
	l32i.n	a8, sp, 24	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:91:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  9 ], cb_row_Q7[ 4 ] );
	l32i.n	a11, a15, 36	# MEM[(const opus_int32 *)XX_Q17_145(D) + 36B], MEM[(const opus_int32 *)XX_Q17_145(D) + 36B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:98:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 14 ], cb_row_Q7[ 4 ] );
	sub	a4, a4, a10	# sum2_Q24, tmp255,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:90:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  8 ], cb_row_Q7[ 3 ] );
	sub	a2, a2, a8	# sum2_Q24, tmp245,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:83:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  4 ], cb_row_Q7[ 4 ] );
	l32i.n	a8, a15, 16	# MEM[(const opus_int32 *)XX_Q17_145(D) + 16B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	extui	a10, a5, 0, 16	# tmp266, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:99:         sum2_Q24 = silk_LSHIFT32( sum2_Q24, 1 );
	slli	a4, a4, 1	# _78, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	srai	a5, a5, 16	# tmp269, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:91:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  9 ], cb_row_Q7[ 4 ] );
	mull	a11, a6, a11	# tmp246, _43, MEM[(const opus_int32 *)XX_Q17_145(D) + 36B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:100:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[ 12 ], cb_row_Q7[ 2 ] );
	add.n	a4, a12, a4	# sum2_Q24, tmp257, _78
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	mull	a10, a10, a6	# tmp267, tmp266, _43
	mull	a5, a5, a6	# tmp270, tmp269, _43
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	l32i.n	a12, sp, 20	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:83:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  4 ], cb_row_Q7[ 4 ] );
	mull	a6, a6, a8	#, _43,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:81:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  2 ], cb_row_Q7[ 2 ] );
	sub	a9, a9, a12	# sum2_Q24, tmp227,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:83:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  4 ], cb_row_Q7[ 4 ] );
	s32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:91:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  9 ], cb_row_Q7[ 4 ] );
	add.n	a2, a11, a2	# sum2_Q24, tmp246, sum2_Q24
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	l8ui	a12, sp, 4	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:93:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  6 ], cb_row_Q7[ 1 ] );
	l32i.n	a11, a15, 24	# MEM[(const opus_int32 *)XX_Q17_145(D) + 24B],
	l32i.n	a6, sp, 8	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:92:         sum2_Q24 = silk_LSHIFT32( sum2_Q24, 1 );
	slli	a2, a2, 1	# _64, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:93:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  6 ], cb_row_Q7[ 1 ] );
	mull	a6, a6, a11	#,,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	slli	a8, a12, 24	# tmp238,,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:93:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  6 ], cb_row_Q7[ 1 ] );
	s32i.n	a6, sp, 4	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:82:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  3 ], cb_row_Q7[ 3 ] );
	l32i.n	a6, sp, 0	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	srai	a8, a8, 24	# _49, tmp238,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:82:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  3 ], cb_row_Q7[ 3 ] );
	add.n	a9, a6, a9	# sum2_Q24,, sum2_Q24
# @OPUS@\upstream\silk\VQ_WMat_EC.c:93:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  6 ], cb_row_Q7[ 1 ] );
	l32i.n	a6, sp, 4	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	l32r	a11, .LC1	#,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:93:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  6 ], cb_row_Q7[ 1 ] );
	add.n	a2, a6, a2	# sum2_Q24,, _64
# @OPUS@\upstream\silk\VQ_WMat_EC.c:83:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  4 ], cb_row_Q7[ 4 ] );
	l32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:107:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 3 ] );
	srai	a12, a3, 16	# tmp274, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:83:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  4 ], cb_row_Q7[ 4 ] );
	add.n	a9, a6, a9	# sum2_Q24,, sum2_Q24
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	l32i.n	a6, a15, 0	# *XX_Q17_145(D),
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	srai	a10, a10, 16	# tmp268, tmp267,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	mull	a6, a8, a6	#, _49,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a11	# tmp271, tmp270,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:107:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 3 ] );
	mull	a12, a12, a7	# tmp275, tmp274, _39
# @OPUS@\upstream\silk\VQ_WMat_EC.c:101:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 2 ] );
	srai	a11, a4, 16	# tmp277, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	s32i.n	a6, sp, 0	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:107:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 3 ] );
	extui	a3, a3, 0, 16	# tmp280, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a10, a5	# tmp273, tmp268, tmp271
# @OPUS@\upstream\silk\VQ_WMat_EC.c:101:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 2 ] );
	mull	a11, a11, a14	# tmp278, tmp277, _35
# @OPUS@\upstream\silk\VQ_WMat_EC.c:107:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 3 ] );
	mull	a3, a3, a7	# tmp281, tmp280, _39
# @OPUS@\upstream\silk\VQ_WMat_EC.c:94:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 1 ] );
	l32i.n	a10, sp, 8	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	l32i.n	a7, sp, 0	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:94:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 1 ] );
	srai	a6, a2, 16	# tmp284, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:84:         sum2_Q24 = silk_LSHIFT32( sum2_Q24, 1 );
	slli	a9, a9, 1	# _46, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a12	# tmp276, tmp273, tmp275
# @OPUS@\upstream\silk\VQ_WMat_EC.c:101:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 2 ] );
	extui	a4, a4, 0, 16	# tmp287, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:85:         sum2_Q24 = silk_MLA( sum2_Q24,        XX_Q17[  0 ], cb_row_Q7[ 0 ] );
	add.n	a9, a7, a9	# sum2_Q24,, _46
# @OPUS@\upstream\silk\VQ_WMat_EC.c:101:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 2 ] );
	mull	a4, a4, a14	# tmp288, tmp287, _35
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a11	# tmp279, tmp276, tmp278
# @OPUS@\upstream\silk\VQ_WMat_EC.c:107:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 3 ] );
	srai	a3, a3, 16	# tmp282, tmp281,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:94:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 1 ] );
	mull	a6, a6, a10	# tmp285, tmp284,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:86:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 0 ] );
	srai	a14, a9, 16	# tmp291, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a3	# tmp283, tmp279, tmp282
# @OPUS@\upstream\silk\VQ_WMat_EC.c:94:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 1 ] );
	extui	a2, a2, 0, 16	# tmp294, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:86:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 0 ] );
	mull	a14, a14, a8	# tmp292, tmp291, _49
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a6	# tmp286, tmp283, tmp285
# @OPUS@\upstream\silk\VQ_WMat_EC.c:101:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 2 ] );
	srai	a4, a4, 16	# tmp289, tmp288,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:94:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 1 ] );
	mull	a2, a2, a10	# tmp295, tmp294,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:86:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 0 ] );
	extui	a9, a9, 0, 16	# tmp298, sum2_Q24,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a4	# tmp290, tmp286, tmp289
# @OPUS@\upstream\silk\VQ_WMat_EC.c:86:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 0 ] );
	mull	a8, a9, a8	# tmp299, tmp298, _49
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a14	# tmp293, tmp290, tmp292
# @OPUS@\upstream\silk\VQ_WMat_EC.c:94:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 1 ] );
	srai	a2, a2, 16	# tmp296, tmp295,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a5, a5, a2	# tmp297, tmp293, tmp296
# @OPUS@\upstream\silk\VQ_WMat_EC.c:86:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 0 ] );
	srai	a8, a8, 16	# tmp300, tmp299,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:112:         sum1_Q15 = silk_SMLAWB( sum1_Q15,        sum2_Q24,  cb_row_Q7[ 4 ] );
	add.n	a8, a5, a8	# sum1_Q15, tmp297, tmp300
# @OPUS@\upstream\silk\VQ_WMat_EC.c:115:         if( sum1_Q15 >= 0 ) {
	bltz	a8, .L4	# sum1_Q15,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:71:         gain_tmp_Q7 = cb_gain_Q7[k];
	l32i.n	a12, sp, 12	# %sfp,
	l32i	a11, sp, 100	# cb_gain_Q7,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:77:         penalty = silk_LSHIFT32( silk_max( silk_SUB32( gain_tmp_Q7, max_gain_Q7 ), 0 ), 11 );
	l32i	a3, sp, 112	# max_gain_Q7,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:71:         gain_tmp_Q7 = cb_gain_Q7[k];
	add.n	a2, a11, a12	# tmp301,,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:71:         gain_tmp_Q7 = cb_gain_Q7[k];
	l8ui	a12, a2, 0	# MEM[base: _402, offset: 0B], gain_tmp_Q7
# @OPUS@\upstream\silk\VQ_WMat_EC.c:77:         penalty = silk_LSHIFT32( silk_max( silk_SUB32( gain_tmp_Q7, max_gain_Q7 ), 0 ), 11 );
	movi.n	a4, 0	#,
	sub	a14, a12, a3	# tmp302, gain_tmp_Q7,
	movltz	a14, a4, a14	# tmp302,, tmp302
	slli	a14, a14, 11	# penalty, tmp302,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:117:             bits_res_Q8 = silk_SMULBB( subfr_len, silk_lin2log( sum1_Q15 + penalty) - (15 << 7) );
	add.n	a14, a14, a8	# _115, penalty, sum1_Q15
	mov.n	a2, a14	#, _115
	call0	silk_lin2log		#
# @OPUS@\upstream\silk\VQ_WMat_EC.c:119:             bits_tot_Q8 = silk_ADD_LSHIFT32( bits_res_Q8, cl_Q5[ k ], 3-1 );
	l32i	a5, sp, 104	# cl_Q5,
	l32i.n	a6, sp, 12	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:117:             bits_res_Q8 = silk_SMULBB( subfr_len, silk_lin2log( sum1_Q15 + penalty) - (15 << 7) );
	movi	a7, -0x780	#,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:119:             bits_tot_Q8 = silk_ADD_LSHIFT32( bits_res_Q8, cl_Q5[ k ], 3-1 );
	add.n	a3, a5, a6	# tmp305,,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:117:             bits_res_Q8 = silk_SMULBB( subfr_len, silk_lin2log( sum1_Q15 + penalty) - (15 << 7) );
	l32i	a8, sp, 108	# subfr_len,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:119:             bits_tot_Q8 = silk_ADD_LSHIFT32( bits_res_Q8, cl_Q5[ k ], 3-1 );
	l8ui	a3, a3, 0	# MEM[base: _400, offset: 0B], MEM[base: _400, offset: 0B]
# @OPUS@\upstream\silk\VQ_WMat_EC.c:117:             bits_res_Q8 = silk_SMULBB( subfr_len, silk_lin2log( sum1_Q15 + penalty) - (15 << 7) );
	add.n	a2, a2, a7	# tmp310,,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:120:             if( bits_tot_Q8 <= *rate_dist_Q8 ) {
	l32i.n	a9, sp, 44	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:117:             bits_res_Q8 = silk_SMULBB( subfr_len, silk_lin2log( sum1_Q15 + penalty) - (15 << 7) );
	mul16s	a2, a2, a8	# bits_res_Q8, tmp310,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:119:             bits_tot_Q8 = silk_ADD_LSHIFT32( bits_res_Q8, cl_Q5[ k ], 3-1 );
	slli	a3, a3, 2	# tmp307, MEM[base: _400, offset: 0B],
# @OPUS@\upstream\silk\VQ_WMat_EC.c:120:             if( bits_tot_Q8 <= *rate_dist_Q8 ) {
	l32i.n	a4, a9, 0	# *rate_dist_Q8_133(D), *rate_dist_Q8_133(D)
# @OPUS@\upstream\silk\VQ_WMat_EC.c:119:             bits_tot_Q8 = silk_ADD_LSHIFT32( bits_res_Q8, cl_Q5[ k ], 3-1 );
	add.n	a3, a3, a2	# bits_tot_Q8, tmp307, bits_res_Q8
# @OPUS@\upstream\silk\VQ_WMat_EC.c:120:             if( bits_tot_Q8 <= *rate_dist_Q8 ) {
	blt	a4, a3, .L4	# *rate_dist_Q8_133(D), bits_tot_Q8,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:122:                 *res_nrg_Q15 = sum1_Q15 + penalty;
	l32i.n	a10, sp, 52	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:121:                 *rate_dist_Q8 = bits_tot_Q8;
	s32i.n	a3, a9, 0	# *rate_dist_Q8_133(D), bits_tot_Q8
# @OPUS@\upstream\silk\VQ_WMat_EC.c:123:                 *ind = (opus_int8)k;
	l32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:122:                 *res_nrg_Q15 = sum1_Q15 + penalty;
	s32i.n	a14, a10, 0	# *res_nrg_Q15_135(D), _115
# @OPUS@\upstream\silk\VQ_WMat_EC.c:124:                 *gain_Q7 = gain_tmp_Q7;
	l32i.n	a3, sp, 56	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:123:                 *ind = (opus_int8)k;
	s8i	a6, a11, 0	# *ind_138(D),
# @OPUS@\upstream\silk\VQ_WMat_EC.c:124:                 *gain_Q7 = gain_tmp_Q7;
	s32i.n	a12, a3, 0	# *gain_Q7_179(D), gain_tmp_Q7
.L4:
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	l32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	l32i.n	a5, sp, 40	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	addi.n	a4, a4, 1	#,,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:129:         cb_row_Q7 += LTP_ORDER;
	addi.n	a13, a13, 5	# cb_Q7, cb_Q7,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	s32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\silk\VQ_WMat_EC.c:69:     for( k = 0; k < L; k++ ) {
	bne	a13, a5, .L6	# cb_Q7,,
.L1:
# @OPUS@\upstream\silk\VQ_WMat_EC.c:131: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	silk_VQ_WMat_EC_c, .-silk_VQ_WMat_EC_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
