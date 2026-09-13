# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/LPC_analysis_filter.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"LPC_analysis_filter.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\LPC_analysis_filter.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\LPC_analysis_filter.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\LPC_analysis_filter.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\LPC_analysis_filter.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\LPC_analysis_filter.c.s.raw
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
	.section	.text.silk_LPC_analysis_filter,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.align	4
	.global	silk_LPC_analysis_filter
	.type	silk_LPC_analysis_filter, @function
# Function: silk_LPC_analysis_filter
# Module: upstream/silk/LPC_analysis_filter.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: C89-compliant. */
# C context: #define USE_CELT_FIR 0
# C context:
# C context: void silk_LPC_analysis_filter(
# C context: opus_int16                  *out,               /* O    Output signal                                               */
# C context: const opus_int16            *in,                /* I    Input signal                                                */
# C context: const opus_int16            *B,                 /* I    MA prediction coefficients, Q12 [order]                     */
# C context: const opus_int32            len,                /* I    Signal length                                               */
silk_LPC_analysis_filter:
	addi	sp, sp, -48	#,,
	s32i.n	a0, sp, 44	#,
	s32i.n	a12, sp, 40	#,
	s32i.n	a13, sp, 36	#,
	s32i.n	a14, sp, 32	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\LPC_analysis_filter.c:57: {
	s32i.n	a2, sp, 4	# %sfp, out
# @OPUS@\upstream\silk\LPC_analysis_filter.c:82:     for( ix = d; ix < len; ix++ ) {
	blt	a6, a5, .L2	# d, len,
	slli	a6, a6, 1	#, d,
	s32i.n	a6, sp, 0	# %sfp,
.L7:
# @OPUS@\upstream\silk\LPC_analysis_filter.c:109:     silk_memset( out, 0, d * sizeof( opus_int16 ) );
	l32i.n	a4, sp, 0	# %sfp,
	l32i.n	a2, sp, 4	# %sfp,
	movi.n	a3, 0	#,
	call0	memset		#
# @OPUS@\upstream\silk\LPC_analysis_filter.c:111: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
.L2:
	mov.n	a8, a2	#, out
	addi	a2, a6, -7	# tmp131, d,
	slli	a7, a6, 1	#, d,
	srli	a2, a2, 1	# tmp132, tmp131,
	addi	a9, a7, -16	# tmp128,,
	addi	a12, a3, -16	# tmp129, in,
	slli	a5, a5, 1	# tmp130, len,
	slli	a2, a2, 2	# _301, tmp132,
	movi.n	a13, -0x12	# tmp183,
	l32r	a11, .LC0	#, tmp176
	s32i.n	a7, sp, 0	# %sfp,
	add.n	a10, a8, a7	# ivtmp$34,,
	add.n	a9, a3, a9	# ivtmp$35, in, tmp128
	add.n	a12, a12, a5	# _269, tmp129, tmp130
	sub	a13, a13, a2	# tmp184, tmp183, _301
.L6:
# @OPUS@\upstream\silk\LPC_analysis_filter.c:88:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -1 ], B[ 1 ] );
	l16ui	a15, a9, 12	# MEM[base: _262, offset: 12B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:85:         out32_Q12 = silk_SMULBB( in_ptr[  0 ], B[ 0 ] );
	l16ui	a5, a4, 0	# *B_91(D),
# @OPUS@\upstream\silk\LPC_analysis_filter.c:89:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -2 ], B[ 2 ] );
	l16ui	a3, a4, 4	# MEM[(const opus_int16 *)B_91(D) + 4B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:88:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -1 ], B[ 1 ] );
	l16ui	a7, a4, 2	# MEM[(const opus_int16 *)B_91(D) + 2B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:85:         out32_Q12 = silk_SMULBB( in_ptr[  0 ], B[ 0 ] );
	l16ui	a2, a9, 14	# MEM[base: _262, offset: 14B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:89:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -2 ], B[ 2 ] );
	l16ui	a8, a9, 10	# MEM[base: _262, offset: 10B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:88:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -1 ], B[ 1 ] );
	mul16s	a7, a15, a7	# tmp133, MEM[base: _262, offset: 12B], MEM[(const opus_int16 *)B_91(D) + 2B]
# @OPUS@\upstream\silk\LPC_analysis_filter.c:85:         out32_Q12 = silk_SMULBB( in_ptr[  0 ], B[ 0 ] );
	mul16s	a2, a2, a5	# out32_Q12, MEM[base: _262, offset: 14B], *B_91(D)
# @OPUS@\upstream\silk\LPC_analysis_filter.c:90:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -3 ], B[ 3 ] );
	l16ui	a15, a4, 6	# MEM[(const opus_int16 *)B_91(D) + 6B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:89:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -2 ], B[ 2 ] );
	mul16s	a8, a8, a3	# tmp140, MEM[base: _262, offset: 10B], MEM[(const opus_int16 *)B_91(D) + 4B]
# @OPUS@\upstream\silk\LPC_analysis_filter.c:91:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -4 ], B[ 4 ] );
	l16ui	a14, a4, 8	# MEM[(const opus_int16 *)B_91(D) + 8B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:90:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -3 ], B[ 3 ] );
	l16ui	a5, a9, 8	# MEM[base: _262, offset: 8B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:91:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -4 ], B[ 4 ] );
	l16ui	a3, a9, 6	# MEM[base: _262, offset: 6B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:88:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -1 ], B[ 1 ] );
	add.n	a2, a7, a2	# tmp139, tmp133, out32_Q12
# @OPUS@\upstream\silk\LPC_analysis_filter.c:90:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -3 ], B[ 3 ] );
	mul16s	a5, a5, a15	# tmp144, MEM[base: _262, offset: 8B], MEM[(const opus_int16 *)B_91(D) + 6B]
# @OPUS@\upstream\silk\LPC_analysis_filter.c:91:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -4 ], B[ 4 ] );
	mul16s	a7, a3, a14	# tmp148, MEM[base: _262, offset: 6B], MEM[(const opus_int16 *)B_91(D) + 8B]
# @OPUS@\upstream\silk\LPC_analysis_filter.c:92:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -5 ], B[ 5 ] );
	l16ui	a15, a4, 10	# MEM[(const opus_int16 *)B_91(D) + 10B],
	l16ui	a14, a9, 4	# MEM[base: _262, offset: 4B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:89:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -2 ], B[ 2 ] );
	add.n	a2, a2, a8	# tmp143, tmp139, tmp140
# @OPUS@\upstream\silk\LPC_analysis_filter.c:90:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -3 ], B[ 3 ] );
	add.n	a5, a2, a5	# tmp147, tmp143, tmp144
# @OPUS@\upstream\silk\LPC_analysis_filter.c:92:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -5 ], B[ 5 ] );
	mul16s	a2, a14, a15	# tmp152,, MEM[(const opus_int16 *)B_91(D) + 10B]
# @OPUS@\upstream\silk\LPC_analysis_filter.c:91:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -4 ], B[ 4 ] );
	add.n	a7, a5, a7	# tmp151, tmp147, tmp148
# @OPUS@\upstream\silk\LPC_analysis_filter.c:92:         out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -5 ], B[ 5 ] );
	add.n	a7, a7, a2	# out32_Q12, tmp151, tmp152
# @OPUS@\upstream\silk\LPC_analysis_filter.c:93:         for( j = 6; j < d; j += 2 ) {
	blti	a6, 7, .L3	# d,,
	addi.n	a15, a9, 14	# tmp157, ivtmp$35,
	addi.n	a5, a4, 12	# ivtmp$23, B,
	add.n	a15, a13, a15	# _299, tmp184, tmp157
	mov.n	a3, a9	# ivtmp$21, ivtmp$35
.L4:
# @OPUS@\upstream\silk\LPC_analysis_filter.c:94:             out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -j     ], B[ j     ] );
	l16ui	a2, a5, 0	# MEM[base: _306, offset: 0B],
	l16ui	a14, a3, 2	# MEM[base: _298, offset: 2B],
	addi	a3, a3, -4	# ivtmp$21, ivtmp$21,
	mul16s	a14, a14, a2	#, MEM[base: _298, offset: 2B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:95:             out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -j - 1 ], B[ j + 1 ] );
	l16ui	a2, a5, 2	# MEM[base: _306, offset: 2B],
# @OPUS@\upstream\silk\LPC_analysis_filter.c:94:             out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -j     ], B[ j     ] );
	s32i.n	a14, sp, 8	# %sfp,
# @OPUS@\upstream\silk\LPC_analysis_filter.c:95:             out32_Q12 = silk_SMLABB_ovflw( out32_Q12, in_ptr[ -j - 1 ], B[ j + 1 ] );
	l16ui	a14, a3, 4	# MEM[base: _298, offset: 0B],
	addi.n	a5, a5, 4	# ivtmp$23, ivtmp$23,
	mul16s	a8, a14, a2	# tmp161,,
	l32i.n	a14, sp, 8	# %sfp,
	add.n	a2, a14, a8	# tmp164,, tmp161
	add.n	a7, a2, a7	# out32_Q12, tmp164, out32_Q12
# @OPUS@\upstream\silk\LPC_analysis_filter.c:93:         for( j = 6; j < d; j += 2 ) {
	bne	a15, a3, .L4	# _299, ivtmp$21,
.L3:
# @OPUS@\upstream\silk\LPC_analysis_filter.c:99:         out32_Q12 = silk_SUB32_ovflw( silk_LSHIFT( (opus_int32)in_ptr[ 1 ], 12 ), out32_Q12 );
	l16si	a2, a9, 16	# MEM[base: _262, offset: 16B], tmp165
# @OPUS@\upstream\silk\LPC_analysis_filter.c:105:         out[ ix ] = (opus_int16)silk_SAT16( out32 );
	mov.n	a3, a11	# iftmp$13_84, tmp176
# @OPUS@\upstream\silk\LPC_analysis_filter.c:99:         out32_Q12 = silk_SUB32_ovflw( silk_LSHIFT( (opus_int32)in_ptr[ 1 ], 12 ), out32_Q12 );
	slli	a2, a2, 12	# tmp168, tmp165,
	sub	a2, a2, a7	# out32_Q12, tmp168, out32_Q12
# @OPUS@\upstream\silk\LPC_analysis_filter.c:102:         out32 = silk_RSHIFT_ROUND( out32_Q12, 12 );
	srai	a2, a2, 11	# tmp170, out32_Q12,
	addi.n	a2, a2, 1	# tmp171, tmp170,
# @OPUS@\upstream\silk\LPC_analysis_filter.c:102:         out32 = silk_RSHIFT_ROUND( out32_Q12, 12 );
	srai	a2, a2, 1	# out32, tmp171,
# @OPUS@\upstream\silk\LPC_analysis_filter.c:105:         out[ ix ] = (opus_int16)silk_SAT16( out32 );
	blt	a11, a2, .L5	# tmp176, out32,
# @OPUS@\upstream\silk\LPC_analysis_filter.c:105:         out[ ix ] = (opus_int16)silk_SAT16( out32 );
	l32r	a3, .LC1	#, iftmp$13_84
	blt	a2, a3, .L5	# out32, tmp5,
# @OPUS@\upstream\silk\LPC_analysis_filter.c:105:         out[ ix ] = (opus_int16)silk_SAT16( out32 );
	slli	a2, a2, 16	# tmp174, out32,
	srai	a3, a2, 16	# iftmp$13_84, tmp174,
.L5:
# @OPUS@\upstream\silk\LPC_analysis_filter.c:105:         out[ ix ] = (opus_int16)silk_SAT16( out32 );
	s16i	a3, a10, 0	# MEM[base: _274, offset: 0B], iftmp$13_84
	addi.n	a9, a9, 2	# ivtmp$35, ivtmp$35,
	addi.n	a10, a10, 2	# ivtmp$34, ivtmp$34,
# @OPUS@\upstream\silk\LPC_analysis_filter.c:82:     for( ix = d; ix < len; ix++ ) {
	bne	a12, a9, .L6	# _269, ivtmp$35,
	j	.L7		#
	.size	silk_LPC_analysis_filter, .-silk_LPC_analysis_filter
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
