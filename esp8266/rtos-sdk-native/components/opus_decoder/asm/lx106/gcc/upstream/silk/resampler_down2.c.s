# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler_down2.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler_down2.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler_down2.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2.c.s.raw
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
	.section	.text.silk_resampler_down2,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, -25727
	.literal .LC3, 9872
	.align	4
	.global	silk_resampler_down2
	.type	silk_resampler_down2, @function
# Function: silk_resampler_down2
# Module: upstream/silk/resampler_down2.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "resampler_rom.h"
# C context:
# C context: /* Downsample by a factor 2 */
# C context: void silk_resampler_down2(
# C context: opus_int32                  *S,                 /* I/O  State vector [ 2 ]                                          */
# C context: opus_int16                  *out,               /* O    Output signal [ floor(len/2) ]                              */
# C context: const opus_int16            *in,                /* I    Input signal [ len ]                                        */
# C context: opus_int32                  inLen               /* I    Number of input samples                                     */
silk_resampler_down2:
	addi	sp, sp, -32	#,,
	s32i.n	a12, sp, 28	#,
	s32i.n	a13, sp, 24	#,
	s32i.n	a14, sp, 20	#,
	s32i.n	a15, sp, 16	#,
# @OPUS@\upstream\silk\resampler_down2.c:43:     opus_int32 k, len2 = silk_RSHIFT32( inLen, 1 );
	srai	a5, a5, 1	# len2, inLen,
# @OPUS@\upstream\silk\resampler_down2.c:42: {
	s32i.n	a2, sp, 4	# %sfp, S
# @OPUS@\upstream\silk\resampler_down2.c:50:     for( k = 0; k < len2; k++ ) {
	blti	a5, 1, .L1	# len2,,
	slli	a5, a5, 2	# tmp87, len2,
	l32i.n	a12, a2, 0	# *S_41(D), S__lsm$3
	add.n	a5, a4, a5	#, ivtmp$7, tmp87
	l32i.n	a2, a2, 4	# MEM[(opus_int32 *)S_41(D) + 4B], S__lsm$4
	l32r	a15, .LC2	#, tmp117
	l32r	a14, .LC3	#, tmp118
	l32r	a13, .LC0	#, tmp116
	s32i.n	a5, sp, 0	# %sfp,
.L4:
# @OPUS@\upstream\silk\resampler_down2.c:52:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k ], 10 );
	l16si	a8, a4, 0	# MEM[base: _1, offset: 0B], tmp88
# @OPUS@\upstream\silk\resampler_down2.c:61:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k + 1 ], 10 );
	l16si	a10, a4, 2	# MEM[base: _1, offset: 2B], tmp99
# @OPUS@\upstream\silk\resampler_down2.c:52:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k ], 10 );
	slli	a8, a8, 10	# in32, tmp88,
# @OPUS@\upstream\silk\resampler_down2.c:55:         Y      = silk_SUB32( in32, S[ 0 ] );
	sub	a11, a8, a12	# Y, in32, S__lsm$3
# @OPUS@\upstream\silk\resampler_down2.c:61:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k + 1 ], 10 );
	slli	a10, a10, 10	# in32, tmp99,
# @OPUS@\upstream\silk\resampler_down2.c:64:         Y      = silk_SUB32( in32, S[ 1 ] );
	sub	a7, a10, a2	# Y, in32, S__lsm$4
# @OPUS@\upstream\silk\resampler_down2.c:56:         X      = silk_SMLAWB( Y, Y, silk_resampler_down2_1 );
	srai	a9, a11, 16	# tmp91, Y,
	extui	a5, a11, 0, 16	# tmp95, Y,
# @OPUS@\upstream\silk\resampler_down2.c:65:         X      = silk_SMULWB( Y, silk_resampler_down2_0 );
	extui	a6, a7, 0, 16	# tmp102, Y,
# @OPUS@\upstream\silk\resampler_down2.c:56:         X      = silk_SMLAWB( Y, Y, silk_resampler_down2_1 );
	mull	a9, a9, a15	# tmp92, tmp91, tmp117
	mull	a5, a5, a15	# tmp96, tmp95, tmp117
# @OPUS@\upstream\silk\resampler_down2.c:65:         X      = silk_SMULWB( Y, silk_resampler_down2_0 );
	mull	a6, a6, a14	# tmp103, tmp102, tmp118
	srai	a7, a7, 16	# tmp106, Y,
# @OPUS@\upstream\silk\resampler_down2.c:56:         X      = silk_SMLAWB( Y, Y, silk_resampler_down2_1 );
	srai	a5, a5, 16	# tmp98, tmp96,
# @OPUS@\upstream\silk\resampler_down2.c:56:         X      = silk_SMLAWB( Y, Y, silk_resampler_down2_1 );
	add.n	a9, a9, a11	# tmp94, tmp92, Y
# @OPUS@\upstream\silk\resampler_down2.c:65:         X      = silk_SMULWB( Y, silk_resampler_down2_0 );
	mull	a7, a7, a14	# tmp107, tmp106, tmp118
# @OPUS@\upstream\silk\resampler_down2.c:56:         X      = silk_SMLAWB( Y, Y, silk_resampler_down2_1 );
	add.n	a9, a9, a5	# X, tmp94, tmp98
# @OPUS@\upstream\silk\resampler_down2.c:66:         out32  = silk_ADD32( out32, S[ 1 ] );
	add.n	a12, a2, a12	# tmp109, S__lsm$4, S__lsm$3
# @OPUS@\upstream\silk\resampler_down2.c:65:         X      = silk_SMULWB( Y, silk_resampler_down2_0 );
	srai	a2, a6, 16	# tmp105, tmp103,
# @OPUS@\upstream\silk\resampler_down2.c:65:         X      = silk_SMULWB( Y, silk_resampler_down2_0 );
	add.n	a7, a2, a7	# X, tmp105, tmp107
# @OPUS@\upstream\silk\resampler_down2.c:66:         out32  = silk_ADD32( out32, S[ 1 ] );
	add.n	a12, a12, a9	# out32, tmp109, X
# @OPUS@\upstream\silk\resampler_down2.c:67:         out32  = silk_ADD32( out32, X );
	add.n	a12, a12, a7	# out32, out32, X
# @OPUS@\upstream\silk\resampler_down2.c:71:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32, 11 ) );
	srai	a12, a12, 10	# tmp111, out32,
	addi.n	a12, a12, 1	# tmp112, tmp111,
	srai	a12, a12, 1	# _85, tmp112,
	addi.n	a4, a4, 4	# ivtmp$7, ivtmp$7,
# @OPUS@\upstream\silk\resampler_down2.c:71:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32, 11 ) );
	mov.n	a5, a13	# iftmp$0_83, tmp116
# @OPUS@\upstream\silk\resampler_down2.c:58:         S[ 0 ] = silk_ADD32( in32, X );
	add.n	a9, a9, a8	# _105, X, in32
# @OPUS@\upstream\silk\resampler_down2.c:68:         S[ 1 ] = silk_ADD32( in32, X );
	add.n	a2, a7, a10	# S__lsm$4, X, in32
# @OPUS@\upstream\silk\resampler_down2.c:71:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32, 11 ) );
	blt	a13, a12, .L3	# tmp116, _85,
	l32r	a5, .LC1	#, iftmp$0_83
	slli	a6, a12, 16	# tmp115, _85,
	blt	a12, a5, .L3	# _85, tmp7,
	srai	a5, a6, 16	# iftmp$0_83, tmp115,
.L3:
# @OPUS@\upstream\silk\resampler_down2.c:71:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32, 11 ) );
	s16i	a5, a3, 0	# MEM[base: _2, offset: 0B], iftmp$0_83
# @OPUS@\upstream\silk\resampler_down2.c:50:     for( k = 0; k < len2; k++ ) {
	l32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_down2.c:58:         S[ 0 ] = silk_ADD32( in32, X );
	mov.n	a12, a9	# S__lsm$3, _105
	addi.n	a3, a3, 2	# ivtmp$8, ivtmp$8,
# @OPUS@\upstream\silk\resampler_down2.c:50:     for( k = 0; k < len2; k++ ) {
	bne	a5, a4, .L4	#, ivtmp$7,
	l32i.n	a6, sp, 4	# %sfp,
	s32i.n	a9, a6, 0	# *S_41(D), _105
	s32i.n	a2, a6, 4	# MEM[(opus_int32 *)S_41(D) + 4B], S__lsm$4
.L1:
# @OPUS@\upstream\silk\resampler_down2.c:73: }
	l32i.n	a12, sp, 28	#,
	l32i.n	a13, sp, 24	#,
	l32i.n	a14, sp, 20	#,
	l32i.n	a15, sp, 16	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_resampler_down2, .-silk_resampler_down2
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
