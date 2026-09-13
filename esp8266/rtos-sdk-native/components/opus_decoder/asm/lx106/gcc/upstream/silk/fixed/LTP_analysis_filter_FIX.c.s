# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/LTP_analysis_filter_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"LTP_analysis_filter_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_analysis_filter_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_analysis_filter_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_analysis_filter_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_analysis_filter_FIX.c.s.raw
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
	.section	.text.silk_LTP_analysis_filter_FIX,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.align	4
	.global	silk_LTP_analysis_filter_FIX
	.type	silk_LTP_analysis_filter_FIX, @function
# Function: silk_LTP_analysis_filter_FIX
# Module: upstream/silk/fixed/LTP_analysis_filter_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #include "main_FIX.h"
# C context:
# C context: void silk_LTP_analysis_filter_FIX(
# C context: opus_int16                      *LTP_res,                               /* O    LTP residual signal of length MAX_NB_SUBFR * ( pre_length + subfr_length )  */
# C context: const opus_int16                *x,                                     /* I    Pointer to input signal with at least max( pitchL ) preceding samples       */
# C context: const opus_int16                LTPCoef_Q14[ LTP_ORDER * MAX_NB_SUBFR ],/* I    LTP_ORDER LTP coefficients for each MAX_NB_SUBFR subframe                   */
# C context: const opus_int                  pitchL[ MAX_NB_SUBFR ],                 /* I    Pitch lag, one for each subframe                                            */
silk_LTP_analysis_filter_FIX:
	addi	sp, sp, -80	#,,
	l32i	a8, sp, 80	# nb_subfr, nb_subfr
	s32i	a12, sp, 76	#,
	s32i	a13, sp, 72	#,
	s32i	a14, sp, 68	#,
	s32i	a15, sp, 64	#,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:44: {
	s32i.n	a2, sp, 24	# %sfp, LTP_res
	s32i.n	a3, sp, 20	# %sfp, x
	s32i.n	a5, sp, 32	# %sfp, pitchL
	s32i.n	a6, sp, 36	# %sfp, invGains_Q16
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:53:     for( k = 0; k < nb_subfr; k++ ) {
	blti	a8, 1, .L1	# nb_subfr,,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:64:         for( i = 0; i < subfr_length + pre_length; i++ ) {
	l32i	a2, sp, 84	# pre_length, pre_length
	add.n	a2, a7, a2	# _114, subfr_length, pre_length
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:86:         LTP_res_ptr += subfr_length + pre_length;
	slli	a3, a2, 1	#, _114,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:87:         x_ptr       += subfr_length;
	slli	a7, a7, 1	#, subfr_length,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:86:         LTP_res_ptr += subfr_length + pre_length;
	s32i.n	a3, sp, 28	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:87:         x_ptr       += subfr_length;
	s32i.n	a7, sp, 40	# %sfp,
	blti	a2, 1, .L1	# _114,,
	slli	a8, a8, 2	#, nb_subfr,
	s32i.n	a4, sp, 12	# %sfp, LTPCoef_Q14
	s32i.n	a8, sp, 44	# %sfp,
	movi.n	a4, 0	#,
	addi	a8, a3, -4	#,,
	l32r	a9, .LC0	#, tmp166
	s32i.n	a4, sp, 16	# %sfp,
	s32i.n	a8, sp, 48	# %sfp,
.L4:
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:55:         x_lag_ptr = x_ptr - pitchL[ k ];
	l32i.n	a3, sp, 16	# %sfp,
	l32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:80:             LTP_res_ptr[ i ] = silk_SMULWB( invGains_Q16[ k ], LTP_res_ptr[ i ] );
	l32i.n	a4, sp, 36	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:55:         x_lag_ptr = x_ptr - pitchL[ k ];
	add.n	a2, a10, a3	# tmp120,,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:55:         x_lag_ptr = x_ptr - pitchL[ k ];
	l32i.n	a10, a2, 0	# MEM[base: _163, offset: 0B], MEM[base: _163, offset: 0B]
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:80:             LTP_res_ptr[ i ] = silk_SMULWB( invGains_Q16[ k ], LTP_res_ptr[ i ] );
	add.n	a2, a4, a3	# tmp133,,
	l32i.n	a11, a2, 0	# MEM[base: _157, offset: 0B], _133
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:57:         Btmp_Q14[ 0 ] = LTPCoef_Q14[ k * LTP_ORDER ];
	l32i.n	a2, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:55:         x_lag_ptr = x_ptr - pitchL[ k ];
	l32i.n	a8, sp, 20	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:57:         Btmp_Q14[ 0 ] = LTPCoef_Q14[ k * LTP_ORDER ];
	l16si	a2, a2, 0	# MEM[base: _162, offset: 0B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:59:         Btmp_Q14[ 2 ] = LTPCoef_Q14[ k * LTP_ORDER + 2 ];
	l32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:55:         x_lag_ptr = x_ptr - pitchL[ k ];
	slli	a10, a10, 1	# tmp121, MEM[base: _163, offset: 0B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:58:         Btmp_Q14[ 1 ] = LTPCoef_Q14[ k * LTP_ORDER + 1 ];
	l32i.n	a3, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:55:         x_lag_ptr = x_ptr - pitchL[ k ];
	sub	a10, a8, a10	# x_lag_ptr,, tmp121
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:59:         Btmp_Q14[ 2 ] = LTPCoef_Q14[ k * LTP_ORDER + 2 ];
	l16si	a4, a4, 4	# MEM[base: _162, offset: 4B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:60:         Btmp_Q14[ 3 ] = LTPCoef_Q14[ k * LTP_ORDER + 3 ];
	l32i.n	a8, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:57:         Btmp_Q14[ 0 ] = LTPCoef_Q14[ k * LTP_ORDER ];
	s32i.n	a2, sp, 8	# %sfp,
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:58:         Btmp_Q14[ 1 ] = LTPCoef_Q14[ k * LTP_ORDER + 1 ];
	l16si	a3, a3, 2	# MEM[base: _162, offset: 2B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:59:         Btmp_Q14[ 2 ] = LTPCoef_Q14[ k * LTP_ORDER + 2 ];
	s32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:60:         Btmp_Q14[ 3 ] = LTPCoef_Q14[ k * LTP_ORDER + 3 ];
	l16si	a14, a8, 6	# MEM[base: _162, offset: 6B], _138
	addi	a4, a10, -4	# ivtmp$31, x_lag_ptr,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:61:         Btmp_Q14[ 4 ] = LTPCoef_Q14[ k * LTP_ORDER + 4 ];
	l16si	a13, a8, 8	# MEM[base: _162, offset: 8B], _135
	add.n	a10, a10, a2	# _175, x_lag_ptr,
	l32i.n	a6, sp, 20	# %sfp, ivtmp$29
	l32i.n	a5, sp, 24	# %sfp, ivtmp$30
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:80:             LTP_res_ptr[ i ] = silk_SMULWB( invGains_Q16[ k ], LTP_res_ptr[ i ] );
	srai	a12, a11, 16	# _131, _133,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:58:         Btmp_Q14[ 1 ] = LTPCoef_Q14[ k * LTP_ORDER + 1 ];
	s32i.n	a3, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:80:             LTP_res_ptr[ i ] = silk_SMULWB( invGains_Q16[ k ], LTP_res_ptr[ i ] );
	extui	a11, a11, 0, 16	# _130, _133,
	s32i.n	a10, sp, 52	# %sfp, _175
.L7:
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:65:             LTP_res_ptr[ i ] = x_ptr[ i ];
	l16si	a7, a6, 0	# MEM[base: _86, offset: 0B], _224
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:69:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 1 ], Btmp_Q14[ 1 ] );
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:65:             LTP_res_ptr[ i ] = x_ptr[ i ];
	s16i	a7, a5, 0	# MEM[base: _84, offset: 0B], _224
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:69:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 1 ], Btmp_Q14[ 1 ] );
	l16ui	a10, a4, 6	# MEM[base: _80, offset: 6B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:68:             LTP_est = silk_SMULBB( x_lag_ptr[ LTP_ORDER / 2 ], Btmp_Q14[ 0 ] );
	l16ui	a2, a4, 8	# MEM[base: _80, offset: 8B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:69:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 1 ], Btmp_Q14[ 1 ] );
	mul16s	a10, a10, a8	# tmp139, MEM[base: _80, offset: 6B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:68:             LTP_est = silk_SMULBB( x_lag_ptr[ LTP_ORDER / 2 ], Btmp_Q14[ 0 ] );
	l32i.n	a8, sp, 8	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:70:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 0 ], Btmp_Q14[ 2 ] );
	l16ui	a15, a4, 4	# MEM[base: _80, offset: 4B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:68:             LTP_est = silk_SMULBB( x_lag_ptr[ LTP_ORDER / 2 ], Btmp_Q14[ 0 ] );
	mul16s	a2, a2, a8	# LTP_est, MEM[base: _80, offset: 8B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:70:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 0 ], Btmp_Q14[ 2 ] );
	l32i.n	a8, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:69:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 1 ], Btmp_Q14[ 1 ] );
	add.n	a2, a10, a2	# tmp143, tmp139, LTP_est
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:71:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ -1 ], Btmp_Q14[ 3 ] );
	l16ui	a10, a4, 2	# MEM[base: _80, offset: 2B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:70:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 0 ], Btmp_Q14[ 2 ] );
	mul16s	a15, a15, a8	# tmp144, MEM[base: _80, offset: 4B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:71:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ -1 ], Btmp_Q14[ 3 ] );
	mul16s	a8, a10, a14	# tmp147,, _138
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:72:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ -2 ], Btmp_Q14[ 4 ] );
	l16ui	a10, a4, 0	# MEM[base: _80, offset: 0B],
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:70:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ 0 ], Btmp_Q14[ 2 ] );
	add.n	a2, a2, a15	# tmp146, tmp143, tmp144
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:72:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ -2 ], Btmp_Q14[ 4 ] );
	mul16s	a15, a10, a13	# tmp150,, _135
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:71:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ -1 ], Btmp_Q14[ 3 ] );
	add.n	a2, a2, a8	# tmp149, tmp146, tmp147
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:72:             LTP_est = silk_SMLABB_ovflw( LTP_est, x_lag_ptr[ -2 ], Btmp_Q14[ 4 ] );
	add.n	a2, a2, a15	# _249, tmp149, tmp150
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:74:             LTP_est = silk_RSHIFT_ROUND( LTP_est, 14 ); /* round and -> Q0*/
	srai	a2, a2, 13	# tmp152, _249,
	addi.n	a2, a2, 1	# _252, tmp152,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:74:             LTP_est = silk_RSHIFT_ROUND( LTP_est, 14 ); /* round and -> Q0*/
	srai	a2, a2, 1	# LTP_est, _252,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:77:             LTP_res_ptr[ i ] = (opus_int16)silk_SAT16( (opus_int32)x_ptr[ i ] - LTP_est );
	sub	a7, a7, a2	# tmp164, _224, LTP_est
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:77:             LTP_res_ptr[ i ] = (opus_int16)silk_SAT16( (opus_int32)x_ptr[ i ] - LTP_est );
	mov.n	a3, a9	# _258, tmp166
	mov.n	a2, a9	# iftmp$9_257, tmp166
	blt	a9, a7, .L6	# tmp166, tmp164,
	l32r	a3, .LC1	#,
	slli	a2, a7, 16	# tmp157, tmp164,
	srai	a2, a2, 16	# iftmp$9_257, tmp157,
	blt	a7, a3, .L9	# tmp164,,
	mov.n	a3, a2	# _258, iftmp$9_257
	j	.L6		#
.L9:
	mov.n	a2, a3	# iftmp$9_257, _258
.L6:
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:80:             LTP_res_ptr[ i ] = silk_SMULWB( invGains_Q16[ k ], LTP_res_ptr[ i ] );
	mull	a3, a11, a3	# tmp158, _130, _258
	mull	a2, a12, a2	# tmp160, _131, iftmp$9_257
	srai	a3, a3, 16	# tmp159, tmp158,
	add.n	a2, a3, a2	# tmp163, tmp159, tmp160
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:64:         for( i = 0; i < subfr_length + pre_length; i++ ) {
	l32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:80:             LTP_res_ptr[ i ] = silk_SMULWB( invGains_Q16[ k ], LTP_res_ptr[ i ] );
	s16i	a2, a5, 0	# MEM[base: _84, offset: 0B], tmp163
	addi.n	a4, a4, 2	# ivtmp$31, ivtmp$31,
	addi.n	a6, a6, 2	# ivtmp$29, ivtmp$29,
	addi.n	a5, a5, 2	# ivtmp$30, ivtmp$30,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:64:         for( i = 0; i < subfr_length + pre_length; i++ ) {
	bne	a4, a8, .L7	# ivtmp$31,,
	l32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:86:         LTP_res_ptr += subfr_length + pre_length;
	l32i.n	a2, sp, 24	# %sfp,
	l32i.n	a3, sp, 28	# %sfp,
	addi.n	a10, a10, 4	#,,
	add.n	a2, a2, a3	#,,
	s32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:87:         x_ptr       += subfr_length;
	l32i.n	a8, sp, 20	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:86:         LTP_res_ptr += subfr_length + pre_length;
	s32i.n	a2, sp, 24	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:87:         x_ptr       += subfr_length;
	l32i.n	a10, sp, 40	# %sfp,
	l32i.n	a2, sp, 12	# %sfp,
	add.n	a8, a8, a10	#,,
	addi.n	a2, a2, 10	#,,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:53:     for( k = 0; k < nb_subfr; k++ ) {
	l32i.n	a3, sp, 44	# %sfp,
	l32i.n	a4, sp, 16	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:87:         x_ptr       += subfr_length;
	s32i.n	a8, sp, 20	# %sfp,
	s32i.n	a2, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:53:     for( k = 0; k < nb_subfr; k++ ) {
	bne	a3, a4, .L4	#,,
.L1:
# @OPUS@\upstream\silk\fixed\LTP_analysis_filter_FIX.c:89: }
	l32i	a12, sp, 76	#,
	l32i	a13, sp, 72	#,
	l32i	a14, sp, 68	#,
	l32i	a15, sp, 64	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	silk_LTP_analysis_filter_FIX, .-silk_LTP_analysis_filter_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
