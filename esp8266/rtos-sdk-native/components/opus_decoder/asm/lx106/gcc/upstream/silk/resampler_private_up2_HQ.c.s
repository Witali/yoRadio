# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler_private_up2_HQ.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler_private_up2_HQ.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_up2_HQ.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_up2_HQ.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_up2_HQ.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_up2_HQ.c.s.raw
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
	.section	.text.silk_resampler_private_up2_HQ,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, 14986
	.literal .LC3, -26453
	.literal .LC4, 6854
	.literal .LC5, 25769
	.literal .LC6, -9994
	.align	4
	.global	silk_resampler_private_up2_HQ
	.type	silk_resampler_private_up2_HQ, @function
# Function: silk_resampler_private_up2_HQ
# Module: upstream/silk/resampler_private_up2_HQ.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /* Upsample by a factor 2, high quality */
# C context: /* Uses 2nd order allpass filters for the 2x upsampling, followed by a      */
# C context: /* notch filter just above Nyquist.                                         */
# C context: void silk_resampler_private_up2_HQ(
# C context: opus_int32                      *S,             /* I/O  Resampler state [ 6 ]       */
# C context: opus_int16                      *out,           /* O    Output signal [ 2 * len ]   */
# C context: const opus_int16                *in,            /* I    Input signal [ len ]        */
# C context: opus_int32                      len             /* I    Number of input samples     */
silk_resampler_private_up2_HQ:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 60	#,
	s32i.n	a13, sp, 56	#,
	s32i.n	a14, sp, 52	#,
	s32i.n	a15, sp, 48	#,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:44: {
	s32i.n	a2, sp, 32	# %sfp, S
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:56:     for( k = 0; k < len; k++ ) {
	blti	a5, 1, .L1	# len,,
	mov.n	a8, a2	#, S
	mov.n	a6, a2	#, S
	l32i.n	a14, a8, 16	# MEM[(opus_int32 *)S_70(D) + 16B], S__lsm$9
	l32i.n	a13, a8, 20	# MEM[(opus_int32 *)S_70(D) + 20B], S__lsm$10
	slli	a5, a5, 2	# tmp121, len,
	l32i.n	a12, a2, 0	# *S_70(D), S__lsm$5
	l32i.n	a6, a6, 8	# MEM[(opus_int32 *)S_70(D) + 8B],
	l32i.n	a2, a2, 4	# MEM[(opus_int32 *)S_70(D) + 4B],
	add.n	a5, a3, a5	#, ivtmp$14, tmp121
	l32i.n	a11, a8, 12	# MEM[(opus_int32 *)S_70(D) + 12B], S__lsm$8
	l32r	a10, .LC0	#, tmp182
	s32i.n	a4, sp, 8	# %sfp, in
	s32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	mov.n	a4, a14	# S__lsm$9, S__lsm$9
	s32i.n	a6, sp, 4	# %sfp,
	mov.n	a14, a13	# S__lsm$10, S__lsm$10
	s32i.n	a5, sp, 36	# %sfp,
	mov.n	a13, a3	# ivtmp$14, ivtmp$14
.L5:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:58:         in32 = silk_LSHIFT( (opus_int32)in[ k ], 10 );
	l32i.n	a9, sp, 8	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	movi	a8, 0x6d2	#,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:58:         in32 = silk_LSHIFT( (opus_int32)in[ k ], 10 );
	l16si	a7, a9, 0	# MEM[base: _55, offset: 0B], tmp122
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	l32r	a9, .LC4	#,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:58:         in32 = silk_LSHIFT( (opus_int32)in[ k ], 10 );
	slli	a7, a7, 10	# in32, tmp122,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:82:         Y       = silk_SUB32( in32, S[ 3 ] );
	sub	a2, a7, a11	# Y, in32, S__lsm$8
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:61:         Y       = silk_SUB32( in32, S[ 0 ] );
	sub	a3, a7, a12	# Y, in32, S__lsm$5
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	extui	a5, a2, 0, 16	# tmp152, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	extui	a6, a3, 0, 16	# tmp125, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	mull	a5, a5, a9	# tmp153, tmp152,
	srai	a2, a2, 16	# tmp156, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	mull	a6, a6, a8	# tmp127, tmp125,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	mull	a2, a2, a9	# tmp157, tmp156,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	srai	a3, a3, 16	# tmp129, Y,
	mull	a3, a3, a8	# tmp131, tmp129,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	srai	a5, a5, 16	# tmp155, tmp153,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	add.n	a2, a5, a2	#, tmp155, tmp157
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	srai	a6, a6, 16	# tmp128, tmp127,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	add.n	a6, a6, a3	# X, tmp128, tmp131
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:84:         out32_1 = silk_ADD32( S[ 3 ], X );
	add.n	a11, a2, a11	#,, S__lsm$8
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:67:         Y       = silk_SUB32( out32_1, S[ 1 ] );
	l32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:63:         out32_1 = silk_ADD32( S[ 0 ], X );
	add.n	a12, a6, a12	#, X, S__lsm$5
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:67:         Y       = silk_SUB32( out32_1, S[ 1 ] );
	sub	a8, a12, a2	# Y,,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:63:         out32_1 = silk_ADD32( S[ 0 ], X );
	s32i.n	a12, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:88:         Y       = silk_SUB32( out32_1, S[ 4 ] );
	sub	a2, a11, a4	# Y,, S__lsm$9
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	l32r	a12, .LC5	#,
	extui	a3, a2, 0, 16	# tmp159, Y,
	mull	a3, a3, a12	# tmp160, tmp159,
	srai	a2, a2, 16	# tmp163, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	l32r	a9, .LC2	#,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	mull	a2, a2, a12	# tmp164, tmp163,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	extui	a5, a8, 0, 16	# tmp132, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	srai	a3, a3, 16	# tmp162, tmp160,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	mull	a5, a5, a9	# tmp133, tmp132,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	add.n	a3, a3, a2	# X, tmp162, tmp164
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	srai	a8, a8, 16	# tmp136, Y,
	mull	a8, a8, a9	# tmp137, tmp136,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:90:         out32_2 = silk_ADD32( S[ 4 ], X );
	add.n	a4, a3, a4	#, X, S__lsm$9
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:69:         out32_2 = silk_ADD32( S[ 1 ], X );
	l32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:90:         out32_2 = silk_ADD32( S[ 4 ], X );
	s32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	srai	a5, a5, 16	# tmp135, tmp133,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	add.n	a5, a5, a8	# X, tmp135, tmp137
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:73:         Y       = silk_SUB32( out32_2, S[ 2 ] );
	l32i.n	a4, sp, 4	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:94:         Y       = silk_SUB32( out32_2, S[ 5 ] );
	l32i.n	a8, sp, 12	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:69:         out32_2 = silk_ADD32( S[ 1 ], X );
	add.n	a15, a5, a2	# out32_2, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:73:         Y       = silk_SUB32( out32_2, S[ 2 ] );
	sub	a12, a15, a4	# Y, out32_2,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:84:         out32_1 = silk_ADD32( S[ 3 ], X );
	s32i.n	a11, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:94:         Y       = silk_SUB32( out32_2, S[ 5 ] );
	sub	a11, a8, a14	# Y,, S__lsm$10
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	l32r	a8, .LC3	#,
	srai	a9, a12, 16	# tmp139, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	srai	a2, a11, 16	#, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	mull	a9, a9, a8	#, tmp139,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	s32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	extui	a4, a12, 0, 16	# tmp143, Y,
	s32i.n	a9, sp, 40	# %sfp,
	mull	a4, a4, a8	# tmp144, tmp143,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	l32i.n	a9, sp, 0	# %sfp,
	l32r	a8, .LC6	#,
	extui	a2, a11, 0, 16	# tmp170, Y,
	mull	a9, a9, a8	#,,
	mull	a2, a2, a8	# tmp171, tmp170,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	l32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	s32i.n	a9, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	srai	a4, a4, 16	# tmp146, tmp144,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	add.n	a9, a8, a12	# tmp142,, Y
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	l32i.n	a12, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	add.n	a9, a9, a4	# X, tmp142, tmp146
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:75:         out32_1 = silk_ADD32( S[ 2 ], X );
	l32i.n	a4, sp, 4	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	add.n	a8, a12, a11	# tmp169,, Y
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	srai	a2, a2, 16	# tmp173, tmp171,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:75:         out32_1 = silk_ADD32( S[ 2 ], X );
	add.n	a11, a9, a4	# out32_1, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	add.n	a2, a8, a2	# X, tmp169, tmp173
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:64:         S[ 0 ]  = silk_ADD32( in32, X );
	add.n	a12, a6, a7	# S__lsm$5, X, in32
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:70:         S[ 1 ]  = silk_ADD32( out32_1, X );
	l32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:96:         out32_1 = silk_ADD32( S[ 5 ], X );
	add.n	a8, a2, a14	# out32_1, X, S__lsm$10
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a11, a11, 9	# tmp147, out32_1,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a8, a8, 9	# tmp174, out32_1,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	addi.n	a11, a11, 1	# tmp148, tmp147,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:70:         S[ 1 ]  = silk_ADD32( out32_1, X );
	add.n	a5, a5, a6	#, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:76:         S[ 2 ]  = silk_ADD32( out32_2, X );
	add.n	a9, a9, a15	#, X, out32_2
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	addi.n	a8, a8, 1	# tmp175, tmp174,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	s32i.n	a10, sp, 28	# %sfp, tmp182
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a11, a11, 1	# _192, tmp148,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:70:         S[ 1 ]  = silk_ADD32( out32_1, X );
	s32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:76:         S[ 2 ]  = silk_ADD32( out32_2, X );
	s32i.n	a9, sp, 4	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a8, a8, 1	# _155, tmp175,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	blt	a10, a11, .L3	# tmp182, _192,
	l32r	a9, .LC1	#,
	slli	a4, a11, 16	# tmp151, _192,
	s32i.n	a9, sp, 28	# %sfp,
	blt	a11, a9, .L3	# _192, tmp5,
	srai	a4, a4, 16	#, tmp151,
	s32i.n	a4, sp, 28	# %sfp,
.L3:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:85:         S[ 3 ]  = silk_ADD32( in32, X );
	l32i.n	a9, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	s16i	a6, a13, 0	# MEM[base: _27, offset: 0B],
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:85:         S[ 3 ]  = silk_ADD32( in32, X );
	add.n	a11, a9, a7	# S__lsm$8,, in32
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:91:         S[ 4 ]  = silk_ADD32( out32_1, X );
	l32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:97:         S[ 5 ]  = silk_ADD32( out32_2, X );
	l32i.n	a9, sp, 12	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	mov.n	a5, a10	# iftmp$3_153, tmp182
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:91:         S[ 4 ]  = silk_ADD32( out32_1, X );
	add.n	a4, a3, a6	# S__lsm$9, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:97:         S[ 5 ]  = silk_ADD32( out32_2, X );
	add.n	a14, a2, a9	# S__lsm$10, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	blt	a10, a8, .L4	# tmp182, _155,
	l32r	a5, .LC1	#, iftmp$3_153
	slli	a2, a8, 16	# tmp178, _155,
	blt	a8, a5, .L4	# _155, tmp3,
	srai	a5, a2, 16	# iftmp$3_153, tmp178,
.L4:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	s16i	a5, a13, 2	# MEM[base: _27, offset: 2B], iftmp$3_153
	l32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:56:     for( k = 0; k < len; k++ ) {
	l32i.n	a6, sp, 36	# %sfp,
	addi.n	a5, a5, 2	#,,
	addi.n	a13, a13, 4	# ivtmp$14, ivtmp$14,
	s32i.n	a5, sp, 8	# %sfp,
	bne	a6, a13, .L5	#, ivtmp$14,
	l32i.n	a8, sp, 32	# %sfp,
	l32i.n	a9, sp, 0	# %sfp,
	s32i.n	a12, a8, 0	# *S_70(D), S__lsm$5
	l32i.n	a12, sp, 4	# %sfp,
	mov.n	a13, a14	# S__lsm$10, S__lsm$10
	s32i.n	a9, a8, 4	# MEM[(opus_int32 *)S_70(D) + 4B],
	s32i.n	a12, a8, 8	# MEM[(opus_int32 *)S_70(D) + 8B],
	s32i.n	a11, a8, 12	# MEM[(opus_int32 *)S_70(D) + 12B], S__lsm$8
	s32i.n	a4, a8, 16	# MEM[(opus_int32 *)S_70(D) + 16B], S__lsm$9
	s32i.n	a13, a8, 20	# MEM[(opus_int32 *)S_70(D) + 20B], S__lsm$10
.L1:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:102: }
	l32i.n	a12, sp, 60	#,
	l32i.n	a13, sp, 56	#,
	l32i.n	a14, sp, 52	#,
	l32i.n	a15, sp, 48	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_resampler_private_up2_HQ, .-silk_resampler_private_up2_HQ
	.section	.text.silk_resampler_private_up2_HQ_wrapper,"ax",@progbits
	.literal_position
	.literal .LC7, 32767
	.literal .LC8, -32768
	.literal .LC9, 14986
	.literal .LC10, -26453
	.literal .LC11, 6854
	.literal .LC12, 25769
	.literal .LC13, -9994
	.align	4
	.global	silk_resampler_private_up2_HQ_wrapper
	.type	silk_resampler_private_up2_HQ_wrapper, @function
# Function: silk_resampler_private_up2_HQ_wrapper
# Module: upstream/silk/resampler_private_up2_HQ.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void silk_resampler_private_up2_HQ_wrapper(
# C context: void                            *SS,            /* I/O  Resampler state (unused)    */
# C context: opus_int16                      *out,           /* O    Output signal [ 2 * len ]   */
# C context: const opus_int16                *in,            /* I    Input signal [ len ]        */
# C context: opus_int32                      len             /* I    Number of input samples     */
silk_resampler_private_up2_HQ_wrapper:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 60	#,
	s32i.n	a13, sp, 56	#,
	s32i.n	a14, sp, 52	#,
	s32i.n	a15, sp, 48	#,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:56:     for( k = 0; k < len; k++ ) {
	blti	a5, 1, .L12	# len,,
	slli	a5, a5, 2	# tmp121, len,
	l32i.n	a15, a2, 4	# MEM[(opus_int32 *)SS_2(D) + 4B], SS__lsm$19
	l32i.n	a14, a2, 16	# MEM[(opus_int32 *)SS_2(D) + 16B], SS__lsm$22
	add.n	a5, a3, a5	#, ivtmp$27, tmp121
	l32i.n	a9, a2, 0	# MEM[(opus_int32 *)SS_2(D)], SS__lsm$18
	l32i.n	a13, a2, 8	# MEM[(opus_int32 *)SS_2(D) + 8B], SS__lsm$20
	l32i.n	a12, a2, 12	# MEM[(opus_int32 *)SS_2(D) + 12B], SS__lsm$21
	l32i.n	a11, a2, 20	# MEM[(opus_int32 *)SS_2(D) + 20B], SS__lsm$23
	s32i.n	a4, sp, 0	# %sfp, in
	mov.n	a8, a3	# ivtmp$27, out
	s32i.n	a5, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	mov.n	a4, a14	# SS__lsm$22, SS__lsm$22
	s32i.n	a2, sp, 28	# %sfp, SS
	mov.n	a10, a15	# SS__lsm$19, SS__lsm$19
.L16:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:58:         in32 = silk_LSHIFT( (opus_int32)in[ k ], 10 );
	l32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	movi	a7, 0x6d2	#,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:58:         in32 = silk_LSHIFT( (opus_int32)in[ k ], 10 );
	l16si	a6, a2, 0	# MEM[base: _82, offset: 0B], tmp122
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	l32r	a14, .LC7	#, iftmp$1_190
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:58:         in32 = silk_LSHIFT( (opus_int32)in[ k ], 10 );
	slli	a6, a6, 10	# in32, tmp122,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:61:         Y       = silk_SUB32( in32, S[ 0 ] );
	sub	a3, a6, a9	# Y, in32, SS__lsm$18
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	extui	a15, a3, 0, 16	# tmp125, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:82:         Y       = silk_SUB32( in32, S[ 3 ] );
	sub	a2, a6, a12	# Y, in32, SS__lsm$21
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	mull	a15, a15, a7	# tmp127, tmp125,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	l32r	a7, .LC11	#,
	extui	a5, a2, 0, 16	# tmp152, Y,
	mull	a5, a5, a7	# tmp153, tmp152,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	srai	a3, a3, 16	# tmp129, Y,
	movi	a7, 0x6d2	#,
	mull	a3, a3, a7	# tmp131, tmp129,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	l32r	a7, .LC11	#,
	srai	a2, a2, 16	# tmp156, Y,
	mull	a2, a2, a7	# tmp157, tmp156,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	srai	a7, a15, 16	# tmp128, tmp127,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	add.n	a3, a7, a3	#, tmp128, tmp131
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	srai	a5, a5, 16	# tmp155, tmp153,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	add.n	a2, a5, a2	#, tmp155, tmp157
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:63:         out32_1 = silk_ADD32( S[ 0 ], X );
	add.n	a9, a3, a9	#,, SS__lsm$18
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:67:         Y       = silk_SUB32( out32_1, S[ 1 ] );
	sub	a7, a9, a10	# Y,, SS__lsm$19
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:84:         out32_1 = silk_ADD32( S[ 3 ], X );
	add.n	a12, a2, a12	#,, SS__lsm$21
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:63:         out32_1 = silk_ADD32( S[ 0 ], X );
	s32i.n	a9, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	l32r	a9, .LC9	#,
	extui	a5, a7, 0, 16	# tmp132, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:83:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 0 ] );
	s32i.n	a2, sp, 12	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:84:         out32_1 = silk_ADD32( S[ 3 ], X );
	s32i.n	a12, sp, 8	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:88:         Y       = silk_SUB32( out32_1, S[ 4 ] );
	sub	a2, a12, a4	# Y,, SS__lsm$22
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	l32r	a12, .LC12	#,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:62:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 0 ] );
	s32i.n	a3, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	mull	a5, a5, a9	# tmp133, tmp132,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	extui	a3, a2, 0, 16	# tmp159, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	srai	a7, a7, 16	# tmp136, Y,
	mull	a7, a7, a9	# tmp137, tmp136,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	mull	a3, a3, a12	# tmp160, tmp159,
	srai	a2, a2, 16	# tmp163, Y,
	mull	a2, a2, a12	# tmp164, tmp163,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	srai	a5, a5, 16	# tmp135, tmp133,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:68:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_0[ 1 ] );
	add.n	a5, a5, a7	# X, tmp135, tmp137
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	srai	a3, a3, 16	# tmp162, tmp160,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:69:         out32_2 = silk_ADD32( S[ 1 ], X );
	add.n	a15, a5, a10	# out32_2, X, SS__lsm$19
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:89:         X       = silk_SMULWB( Y, silk_resampler_up2_hq_1[ 1 ] );
	add.n	a3, a3, a2	# X, tmp162, tmp164
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:73:         Y       = silk_SUB32( out32_2, S[ 2 ] );
	sub	a12, a15, a13	# Y, out32_2, SS__lsm$20
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:90:         out32_2 = silk_ADD32( S[ 4 ], X );
	add.n	a4, a3, a4	#, X, SS__lsm$22
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:94:         Y       = silk_SUB32( out32_2, S[ 5 ] );
	sub	a10, a4, a11	# Y,, SS__lsm$23
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	extui	a2, a12, 0, 16	#, Y,
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	extui	a7, a10, 0, 16	#, Y,
	s32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	l32r	a9, .LC10	#,
	l32i.n	a7, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:90:         out32_2 = silk_ADD32( S[ 4 ], X );
	s32i.n	a4, sp, 4	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	mull	a7, a7, a9	#,,
	srai	a4, a12, 16	# tmp139, Y,
	mull	a4, a4, a9	# tmp140, tmp139,
	s32i.n	a7, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	l32r	a9, .LC13	#,
	l32i.n	a7, sp, 36	# %sfp,
	srai	a2, a10, 16	# tmp166, Y,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	add.n	a4, a4, a12	# tmp142, tmp140, Y
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	l32i.n	a12, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	mull	a7, a7, a9	#,,
	mull	a2, a2, a9	# tmp167, tmp166,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	srai	a9, a12, 16	# tmp146,,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:74:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_0[ 2 ] );
	add.n	a4, a4, a9	# X, tmp142, tmp146
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	add.n	a2, a2, a10	# tmp169, tmp167, Y
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	s32i.n	a7, sp, 36	# %sfp,
	srai	a7, a7, 16	# tmp173,,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:75:         out32_1 = silk_ADD32( S[ 2 ], X );
	add.n	a12, a4, a13	# out32_1, X, SS__lsm$20
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:95:         X       = silk_SMLAWB( Y, Y, silk_resampler_up2_hq_1[ 2 ] );
	add.n	a2, a2, a7	# X, tmp169, tmp173
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:96:         out32_1 = silk_ADD32( S[ 5 ], X );
	add.n	a7, a2, a11	# out32_1, X, SS__lsm$23
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a12, a12, 9	# tmp147, out32_1,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:64:         S[ 0 ]  = silk_ADD32( in32, X );
	l32i.n	a10, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a7, a7, 9	# tmp174, out32_1,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	addi.n	a12, a12, 1	# tmp148, tmp147,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:70:         S[ 1 ]  = silk_ADD32( out32_1, X );
	l32i.n	a11, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	addi.n	a7, a7, 1	# tmp175, tmp174,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a12, a12, 1	# _192, tmp148,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:64:         S[ 0 ]  = silk_ADD32( in32, X );
	add.n	a9, a10, a6	# SS__lsm$18,, in32
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	srai	a7, a7, 1	# _155, tmp175,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:70:         S[ 1 ]  = silk_ADD32( out32_1, X );
	add.n	a10, a5, a11	# SS__lsm$19, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:76:         S[ 2 ]  = silk_ADD32( out32_2, X );
	add.n	a13, a4, a15	# SS__lsm$20, X, out32_2
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	blt	a14, a12, .L14	# tmp4, _192,
	l32r	a14, .LC8	#, iftmp$1_190
	slli	a4, a12, 16	# tmp151, _192,
	blt	a12, a14, .L14	# _192, tmp5,
	srai	a14, a4, 16	# iftmp$1_190, tmp151,
.L14:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:85:         S[ 3 ]  = silk_ADD32( in32, X );
	l32i.n	a11, sp, 12	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	l32r	a5, .LC7	#, iftmp$3_153
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:85:         S[ 3 ]  = silk_ADD32( in32, X );
	add.n	a12, a11, a6	# SS__lsm$21,, in32
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:91:         S[ 4 ]  = silk_ADD32( out32_1, X );
	l32i.n	a6, sp, 8	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:79:         out[ 2 * k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	s16i	a14, a8, 0	# MEM[base: _43, offset: 0B], iftmp$1_190
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:91:         S[ 4 ]  = silk_ADD32( out32_1, X );
	add.n	a4, a3, a6	# SS__lsm$22, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:97:         S[ 5 ]  = silk_ADD32( out32_2, X );
	l32i.n	a3, sp, 4	# %sfp,
	add.n	a11, a2, a3	# SS__lsm$23, X,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	blt	a5, a7, .L15	# tmp6, _155,
	l32r	a5, .LC8	#, iftmp$3_153
	slli	a2, a7, 16	# tmp178, _155,
	blt	a7, a5, .L15	# _155, tmp3,
	srai	a5, a2, 16	# iftmp$3_153, tmp178,
.L15:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:100:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( out32_1, 10 ) );
	s16i	a5, a8, 2	# MEM[base: _43, offset: 2B], iftmp$3_153
	l32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:56:     for( k = 0; k < len; k++ ) {
	l32i.n	a6, sp, 24	# %sfp,
	addi.n	a5, a5, 2	#,,
	addi.n	a8, a8, 4	# ivtmp$27, ivtmp$27,
	s32i.n	a5, sp, 0	# %sfp,
	bne	a8, a6, .L16	# ivtmp$27,,
	mov.n	a15, a10	# SS__lsm$19, SS__lsm$19
	l32i.n	a10, sp, 28	# %sfp, SS
	s32i.n	a9, a10, 0	# MEM[(opus_int32 *)SS_2(D)], SS__lsm$18
	s32i.n	a15, a10, 4	# MEM[(opus_int32 *)SS_2(D) + 4B], SS__lsm$19
	s32i.n	a13, a10, 8	# MEM[(opus_int32 *)SS_2(D) + 8B], SS__lsm$20
	s32i.n	a12, a10, 12	# MEM[(opus_int32 *)SS_2(D) + 12B], SS__lsm$21
	s32i.n	a4, a10, 16	# MEM[(opus_int32 *)SS_2(D) + 16B], SS__lsm$22
	s32i.n	a11, a10, 20	# MEM[(opus_int32 *)SS_2(D) + 20B], SS__lsm$23
.L12:
# @OPUS@\upstream\silk\resampler_private_up2_HQ.c:113: }
	l32i.n	a12, sp, 60	#,
	l32i.n	a13, sp, 56	#,
	l32i.n	a14, sp, 52	#,
	l32i.n	a15, sp, 48	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_resampler_private_up2_HQ_wrapper, .-silk_resampler_private_up2_HQ_wrapper
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
