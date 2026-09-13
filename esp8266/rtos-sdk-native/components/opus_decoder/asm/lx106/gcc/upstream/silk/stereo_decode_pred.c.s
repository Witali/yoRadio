# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/stereo_decode_pred.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"stereo_decode_pred.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\stereo_decode_pred.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\stereo_decode_pred.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\stereo_decode_pred.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\stereo_decode_pred.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\stereo_decode_pred.c.s.raw
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
	.section	.text.silk_stereo_decode_pred,"ax",@progbits
	.literal_position
	.literal .LC0, silk_stereo_pred_joint_iCDF
	.literal .LC1, silk_uniform3_iCDF
	.literal .LC2, silk_uniform5_iCDF
	.literal .LC3, silk_stereo_pred_quant_Q13
	.literal .LC4, 6554
	.align	4
	.global	silk_stereo_decode_pred
	.type	silk_stereo_decode_pred, @function
# Function: silk_stereo_decode_pred
# Module: upstream/silk/stereo_decode_pred.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Decode mid/side predictors */
# C context: void silk_stereo_decode_pred(
# C context: ec_dec                      *psRangeDec,                    /* I/O  Compressor data structure                   */
# C context: opus_int32                  pred_Q13[]                      /* O    Predictors                                  */
# C context: )
# C context: {
silk_stereo_decode_pred:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 40	#,
	mov.n	a12, a3	# pred_Q13, pred_Q13
# @OPUS@\upstream\silk\stereo_decode_pred.c:44:     n = ec_dec_icdf( psRangeDec, silk_stereo_pred_joint_iCDF, 8 );
	l32r	a3, .LC0	#,
	movi.n	a4, 8	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:39: {
	s32i.n	a0, sp, 44	#,
	s32i.n	a13, sp, 36	#,
	s32i.n	a14, sp, 32	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:39: {
	mov.n	a13, a2	# psRangeDec, psRangeDec
# @OPUS@\upstream\silk\stereo_decode_pred.c:44:     n = ec_dec_icdf( psRangeDec, silk_stereo_pred_joint_iCDF, 8 );
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\stereo_decode_pred.c:45:     ix[ 0 ][ 2 ] = silk_DIV32_16( n, 5 );
	movi.n	a3, 5	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:44:     n = ec_dec_icdf( psRangeDec, silk_stereo_pred_joint_iCDF, 8 );
	mov.n	a14, a2	# n,
# @OPUS@\upstream\silk\stereo_decode_pred.c:45:     ix[ 0 ][ 2 ] = silk_DIV32_16( n, 5 );
	call0	__divsi3		#
# @OPUS@\upstream\silk\stereo_decode_pred.c:48:         ix[ n ][ 0 ] = ec_dec_icdf( psRangeDec, silk_uniform3_iCDF, 8 );
	l32r	a15, .LC1	#, tmp104
# @OPUS@\upstream\silk\stereo_decode_pred.c:46:     ix[ 1 ][ 2 ] = n - 5 * ix[ 0 ][ 2 ];
	slli	a5, a2, 2	# tmp101, tmp98,
	sub	a7, a14, a2	# tmp103, n, tmp98
# @OPUS@\upstream\silk\stereo_decode_pred.c:45:     ix[ 0 ][ 2 ] = silk_DIV32_16( n, 5 );
	mov.n	a8, a2	# tmp98,
# @OPUS@\upstream\silk\stereo_decode_pred.c:46:     ix[ 1 ][ 2 ] = n - 5 * ix[ 0 ][ 2 ];
	sub	a7, a7, a5	# _3, tmp103, tmp101
# @OPUS@\upstream\silk\stereo_decode_pred.c:48:         ix[ n ][ 0 ] = ec_dec_icdf( psRangeDec, silk_uniform3_iCDF, 8 );
	mov.n	a3, a15	#, tmp104
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	s32i.n	a7, sp, 4	#,
	s32i.n	a8, sp, 8	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\stereo_decode_pred.c:49:         ix[ n ][ 1 ] = ec_dec_icdf( psRangeDec, silk_uniform5_iCDF, 8 );
	l32r	a3, .LC2	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:48:         ix[ n ][ 0 ] = ec_dec_icdf( psRangeDec, silk_uniform3_iCDF, 8 );
	mov.n	a6, a2	# _97,
# @OPUS@\upstream\silk\stereo_decode_pred.c:49:         ix[ n ][ 1 ] = ec_dec_icdf( psRangeDec, silk_uniform5_iCDF, 8 );
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	s32i.n	a6, sp, 0	#,
	call0	ec_dec_icdf		#
	mov.n	a14, a2	# _100,
# @OPUS@\upstream\silk\stereo_decode_pred.c:48:         ix[ n ][ 0 ] = ec_dec_icdf( psRangeDec, silk_uniform3_iCDF, 8 );
	mov.n	a3, a15	#, tmp104
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\stereo_decode_pred.c:49:         ix[ n ][ 1 ] = ec_dec_icdf( psRangeDec, silk_uniform5_iCDF, 8 );
	l32r	a3, .LC2	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:48:         ix[ n ][ 0 ] = ec_dec_icdf( psRangeDec, silk_uniform3_iCDF, 8 );
	mov.n	a15, a2	# _4,
# @OPUS@\upstream\silk\stereo_decode_pred.c:49:         ix[ n ][ 1 ] = ec_dec_icdf( psRangeDec, silk_uniform5_iCDF, 8 );
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\stereo_decode_pred.c:54:         ix[ n ][ 0 ] += 3 * ix[ n ][ 2 ];
	l32i.n	a8, sp, 8	#,
	l32i.n	a7, sp, 4	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:54:         ix[ n ][ 0 ] += 3 * ix[ n ][ 2 ];
	l32i.n	a6, sp, 0	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:54:         ix[ n ][ 0 ] += 3 * ix[ n ][ 2 ];
	slli	a4, a8, 1	# tmp109, tmp98,
	slli	a3, a7, 1	# tmp140, _3,
	add.n	a4, a4, a8	# tmp110, tmp109, tmp98
	add.n	a3, a3, a7	# tmp141, tmp140, _3
# @OPUS@\upstream\silk\stereo_decode_pred.c:54:         ix[ n ][ 0 ] += 3 * ix[ n ][ 2 ];
	add.n	a4, a4, a6	# _78, tmp110, _97
	add.n	a3, a3, a15	# _9, tmp141, _4
# @OPUS@\upstream\silk\stereo_decode_pred.c:55:         low_Q13 = silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] ];
	l32r	a6, .LC3	#, tmp111
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	addi.n	a9, a4, 1	# tmp117, _78,
	addi.n	a8, a3, 1	# tmp148, _9,
# @OPUS@\upstream\silk\stereo_decode_pred.c:55:         low_Q13 = silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] ];
	slli	a4, a4, 1	# tmp112, _78,
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	slli	a9, a9, 1	# tmp118, tmp117,
# @OPUS@\upstream\silk\stereo_decode_pred.c:55:         low_Q13 = silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] ];
	slli	a3, a3, 1	# tmp143, _9,
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	slli	a8, a8, 1	# tmp149, tmp148,
# @OPUS@\upstream\silk\stereo_decode_pred.c:55:         low_Q13 = silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] ];
	add.n	a4, a6, a4	# tmp113, tmp111, tmp112
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	add.n	a9, a6, a9	# tmp119, tmp111, tmp118
# @OPUS@\upstream\silk\stereo_decode_pred.c:55:         low_Q13 = silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] ];
	add.n	a3, a6, a3	# tmp144, tmp111, tmp143
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	add.n	a8, a6, a8	# tmp150, tmp111, tmp149
# @OPUS@\upstream\silk\stereo_decode_pred.c:55:         low_Q13 = silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] ];
	l16si	a7, a4, 0	# silk_stereo_pred_quant_Q13, low_Q13
	l16si	a6, a3, 0	# silk_stereo_pred_quant_Q13, low_Q13
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	l16si	a9, a9, 0	# silk_stereo_pred_quant_Q13, tmp120
	l16si	a8, a8, 0	# silk_stereo_pred_quant_Q13, tmp151
	l32r	a10, .LC4	#, tmp125
	sub	a9, a9, a7	# _71, tmp120, low_Q13
	sub	a8, a8, a6	# _14, tmp151, low_Q13
	extui	a3, a9, 0, 16	# tmp123, _71,
	extui	a4, a8, 0, 16	# tmp154, _14,
	mull	a3, a3, a10	# tmp124, tmp123, tmp125
	mull	a4, a4, a10	# tmp155, tmp154, tmp125
# @OPUS@\upstream\silk\stereo_decode_pred.c:58:         pred_Q13[ n ] = silk_SMLABB( low_Q13, step_Q13, 2 * ix[ n ][ 1 ] + 1 );
	slli	a5, a14, 1	# tmp132, _100,
	slli	a2, a2, 1	# tmp163,,
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	srai	a9, a9, 16	# tmp127, _71,
	srai	a8, a8, 16	# tmp158, _14,
	mull	a9, a9, a10	# tmp128, tmp127, tmp125
	mull	a8, a8, a10	# tmp159, tmp158, tmp125
# @OPUS@\upstream\silk\stereo_decode_pred.c:58:         pred_Q13[ n ] = silk_SMLABB( low_Q13, step_Q13, 2 * ix[ n ][ 1 ] + 1 );
	addi.n	a5, a5, 1	# tmp134, tmp132,
	addi.n	a10, a2, 1	# tmp165, tmp163,
	slli	a5, a5, 16	# tmp136, tmp134,
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	srai	a2, a3, 16	# tmp126, tmp124,
	srai	a3, a4, 16	# tmp157, tmp155,
# @OPUS@\upstream\silk\stereo_decode_pred.c:58:         pred_Q13[ n ] = silk_SMLABB( low_Q13, step_Q13, 2 * ix[ n ][ 1 ] + 1 );
	slli	a4, a10, 16	# tmp167, tmp165,
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	add.n	a2, a2, a9	# step_Q13, tmp126, tmp128
# @OPUS@\upstream\silk\stereo_decode_pred.c:58:         pred_Q13[ n ] = silk_SMLABB( low_Q13, step_Q13, 2 * ix[ n ][ 1 ] + 1 );
	srai	a5, a5, 16	# tmp135, tmp136,
# @OPUS@\upstream\silk\stereo_decode_pred.c:56:         step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ ix[ n ][ 0 ] + 1 ] - low_Q13,
	add.n	a3, a3, a8	# step_Q13, tmp157, tmp159
# @OPUS@\upstream\silk\stereo_decode_pred.c:58:         pred_Q13[ n ] = silk_SMLABB( low_Q13, step_Q13, 2 * ix[ n ][ 1 ] + 1 );
	srai	a4, a4, 16	# tmp166, tmp167,
	mull	a2, a2, a5	# tmp137, step_Q13, tmp135
	mull	a3, a3, a4	# tmp168, step_Q13, tmp166
	add.n	a2, a2, a7	# tmp138, tmp137, low_Q13
	add.n	a3, a3, a6	# tmp169, tmp168, low_Q13
# @OPUS@\upstream\silk\stereo_decode_pred.c:63: }
	l32i.n	a0, sp, 44	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:62:     pred_Q13[ 0 ] -= pred_Q13[ 1 ];
	sub	a2, a2, a3	# tmp170, tmp138, tmp169
# @OPUS@\upstream\silk\stereo_decode_pred.c:58:         pred_Q13[ n ] = silk_SMLABB( low_Q13, step_Q13, 2 * ix[ n ][ 1 ] + 1 );
	s32i.n	a3, a12, 4	# MEM[(opus_int32 *)pred_Q13_53(D) + 4B], tmp169
# @OPUS@\upstream\silk\stereo_decode_pred.c:62:     pred_Q13[ 0 ] -= pred_Q13[ 1 ];
	s32i.n	a2, a12, 0	# *pred_Q13_53(D), tmp170
# @OPUS@\upstream\silk\stereo_decode_pred.c:63: }
	l32i.n	a13, sp, 36	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_stereo_decode_pred, .-silk_stereo_decode_pred
	.section	.text.silk_stereo_decode_mid_only,"ax",@progbits
	.literal_position
	.literal .LC5, silk_stereo_only_code_mid_iCDF
	.align	4
	.global	silk_stereo_decode_mid_only
	.type	silk_stereo_decode_mid_only, @function
# Function: silk_stereo_decode_mid_only
# Module: upstream/silk/stereo_decode_pred.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Decode mid-only flag */
# C context: void silk_stereo_decode_mid_only(
# C context: ec_dec                      *psRangeDec,                    /* I/O  Compressor data structure                   */
# C context: opus_int                    *decode_only_mid                /* O    Flag that only mid channel has been coded   */
# C context: )
# C context: {
silk_stereo_decode_mid_only:
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 8	#,
	mov.n	a12, a3	# decode_only_mid, decode_only_mid
# @OPUS@\upstream\silk\stereo_decode_pred.c:72:     *decode_only_mid = ec_dec_icdf( psRangeDec, silk_stereo_only_code_mid_iCDF, 8 );
	l32r	a3, .LC5	#,
	movi.n	a4, 8	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:70: {
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:72:     *decode_only_mid = ec_dec_icdf( psRangeDec, silk_stereo_only_code_mid_iCDF, 8 );
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\stereo_decode_pred.c:73: }
	l32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\stereo_decode_pred.c:72:     *decode_only_mid = ec_dec_icdf( psRangeDec, silk_stereo_only_code_mid_iCDF, 8 );
	s32i.n	a2, a12, 0	# *decode_only_mid_5(D),
# @OPUS@\upstream\silk\stereo_decode_pred.c:73: }
	l32i.n	a12, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_stereo_decode_mid_only, .-silk_stereo_decode_mid_only
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
