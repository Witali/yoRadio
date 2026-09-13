# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/ana_filt_bank_1.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"ana_filt_bank_1.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\ana_filt_bank_1.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\ana_filt_bank_1.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\ana_filt_bank_1.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\ana_filt_bank_1.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\ana_filt_bank_1.c.s.raw
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
	.section	.text.silk_ana_filt_bank_1,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, -24290
	.literal .LC3, 10788
	.align	4
	.global	silk_ana_filt_bank_1
	.type	silk_ana_filt_bank_1, @function
# Function: silk_ana_filt_bank_1
# Module: upstream/silk/ana_filt_bank_1.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: static opus_int16 A_fb1_21 = -24290; /* (opus_int16)(20623 << 1) */
# C context:
# C context: /* Split signal into two decimated bands using first-order allpass filters */
# C context: void silk_ana_filt_bank_1(
# C context: const opus_int16            *in,                /* I    Input signal [N]                                            */
# C context: opus_int32                  *S,                 /* I/O  State vector [2]                                            */
# C context: opus_int16                  *outL,              /* O    Low band [N/2]                                              */
# C context: opus_int16                  *outH,              /* O    High band [N/2]                                             */
silk_ana_filt_bank_1:
	addi	sp, sp, -32	#,,
	s32i.n	a12, sp, 28	#,
	s32i.n	a13, sp, 24	#,
	s32i.n	a14, sp, 20	#,
	s32i.n	a15, sp, 16	#,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:47:     opus_int      k, N2 = silk_RSHIFT( N, 1 );
	srai	a6, a6, 1	# N2, N,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:46: {
	s32i.n	a3, sp, 4	# %sfp, S
# @OPUS@\upstream\silk\ana_filt_bank_1.c:51:     for( k = 0; k < N2; k++ ) {
	blti	a6, 1, .L1	# N2,,
	slli	a6, a6, 2	# tmp94, N2,
	l32i.n	a9, a3, 0	# *S_52(D), S__lsm$10
	add.n	a6, a2, a6	#, ivtmp$14, tmp94
	l32i.n	a3, a3, 4	# MEM[(opus_int32 *)S_52(D) + 4B], S__lsm$11
	l32r	a12, .LC0	#, tmp130
	s32i.n	a6, sp, 0	# %sfp,
.L5:
# @OPUS@\upstream\silk\ana_filt_bank_1.c:53:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k ], 10 );
	l16si	a11, a2, 0	# MEM[base: _4, offset: 0B], tmp95
# @OPUS@\upstream\silk\ana_filt_bank_1.c:62:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k + 1 ], 10 );
	l16si	a10, a2, 2	# MEM[base: _4, offset: 2B], tmp106
# @OPUS@\upstream\silk\ana_filt_bank_1.c:53:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k ], 10 );
	slli	a11, a11, 10	# in32, tmp95,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:56:         Y      = silk_SUB32( in32, S[ 0 ] );
	sub	a14, a11, a9	# Y, in32, S__lsm$10
# @OPUS@\upstream\silk\ana_filt_bank_1.c:57:         X      = silk_SMLAWB( Y, Y, A_fb1_21 );
	l32r	a13, .LC2	#,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:62:         in32 = silk_LSHIFT( (opus_int32)in[ 2 * k + 1 ], 10 );
	slli	a10, a10, 10	# in32, tmp106,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:57:         X      = silk_SMLAWB( Y, Y, A_fb1_21 );
	srai	a15, a14, 16	# tmp98, Y,
	extui	a7, a14, 0, 16	# tmp102, Y,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:65:         Y      = silk_SUB32( in32, S[ 1 ] );
	sub	a6, a10, a3	# Y, in32, S__lsm$11
# @OPUS@\upstream\silk\ana_filt_bank_1.c:57:         X      = silk_SMLAWB( Y, Y, A_fb1_21 );
	mull	a15, a15, a13	# tmp99, tmp98,
	mull	a7, a7, a13	# tmp103, tmp102,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:66:         X      = silk_SMULWB( Y, A_fb1_20 );
	l32r	a13, .LC3	#,
	extui	a8, a6, 0, 16	# tmp109, Y,
	mull	a8, a8, a13	# tmp110, tmp109,
	srai	a6, a6, 16	# tmp113, Y,
	mull	a6, a6, a13	# tmp114, tmp113,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:57:         X      = silk_SMLAWB( Y, Y, A_fb1_21 );
	add.n	a14, a15, a14	# tmp101, tmp99, Y
# @OPUS@\upstream\silk\ana_filt_bank_1.c:57:         X      = silk_SMLAWB( Y, Y, A_fb1_21 );
	srai	a7, a7, 16	# tmp105, tmp103,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:66:         X      = silk_SMULWB( Y, A_fb1_20 );
	srai	a8, a8, 16	# tmp112, tmp110,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:57:         X      = silk_SMLAWB( Y, Y, A_fb1_21 );
	add.n	a14, a14, a7	# X, tmp101, tmp105
# @OPUS@\upstream\silk\ana_filt_bank_1.c:66:         X      = silk_SMULWB( Y, A_fb1_20 );
	add.n	a8, a8, a6	# X, tmp112, tmp114
# @OPUS@\upstream\silk\ana_filt_bank_1.c:67:         out_2  = silk_ADD32( S[ 1 ], X );
	add.n	a3, a8, a3	# out_2, X, S__lsm$11
# @OPUS@\upstream\silk\ana_filt_bank_1.c:58:         out_1  = silk_ADD32( S[ 0 ], X );
	add.n	a6, a14, a9	# out_1, X, S__lsm$10
# @OPUS@\upstream\silk\ana_filt_bank_1.c:71:         outL[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_ADD32( out_2, out_1 ), 11 ) );
	add.n	a7, a3, a6	# tmp116, out_2, out_1
	srai	a7, a7, 10	# tmp117, tmp116,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:72:         outH[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SUB32( out_2, out_1 ), 11 ) );
	sub	a3, a3, a6	# tmp122, out_2, out_1
	srai	a6, a3, 10	# tmp123, tmp122,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:71:         outL[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_ADD32( out_2, out_1 ), 11 ) );
	addi.n	a7, a7, 1	# tmp118, tmp117,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:72:         outH[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SUB32( out_2, out_1 ), 11 ) );
	addi.n	a6, a6, 1	# tmp124, tmp123,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:71:         outL[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_ADD32( out_2, out_1 ), 11 ) );
	srai	a7, a7, 1	# _98, tmp118,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:72:         outH[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SUB32( out_2, out_1 ), 11 ) );
	srai	a6, a6, 1	# _88, tmp124,
	addi.n	a2, a2, 4	# ivtmp$14, ivtmp$14,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:71:         outL[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_ADD32( out_2, out_1 ), 11 ) );
	mov.n	a15, a12	# iftmp$4_96, tmp130
# @OPUS@\upstream\silk\ana_filt_bank_1.c:59:         S[ 0 ] = silk_ADD32( in32, X );
	add.n	a9, a14, a11	# S__lsm$10, X, in32
# @OPUS@\upstream\silk\ana_filt_bank_1.c:68:         S[ 1 ] = silk_ADD32( in32, X );
	add.n	a3, a8, a10	# S__lsm$11, X, in32
# @OPUS@\upstream\silk\ana_filt_bank_1.c:71:         outL[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_ADD32( out_2, out_1 ), 11 ) );
	blt	a12, a7, .L3	# tmp130, _98,
	l32r	a10, .LC1	#,
	slli	a8, a7, 16	# tmp121, _98,
	mov.n	a15, a10	# iftmp$4_96,
	blt	a7, a10, .L3	# _98,,
	srai	a15, a8, 16	# iftmp$4_96, tmp121,
.L3:
# @OPUS@\upstream\silk\ana_filt_bank_1.c:71:         outL[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_ADD32( out_2, out_1 ), 11 ) );
	s16i	a15, a4, 0	# MEM[base: _11, offset: 0B], iftmp$4_96
# @OPUS@\upstream\silk\ana_filt_bank_1.c:72:         outH[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SUB32( out_2, out_1 ), 11 ) );
	mov.n	a7, a12	# iftmp$7_86, tmp130
	blt	a12, a6, .L4	# tmp130, _88,
	l32r	a7, .LC1	#, iftmp$7_86
	slli	a8, a6, 16	# tmp127, _88,
	blt	a6, a7, .L4	# _88, tmp13,
	srai	a7, a8, 16	# iftmp$7_86, tmp127,
.L4:
# @OPUS@\upstream\silk\ana_filt_bank_1.c:51:     for( k = 0; k < N2; k++ ) {
	l32i.n	a6, sp, 0	# %sfp,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:72:         outH[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SUB32( out_2, out_1 ), 11 ) );
	s16i	a7, a5, 0	# MEM[base: _5, offset: 0B], iftmp$7_86
	addi.n	a4, a4, 2	# ivtmp$16, ivtmp$16,
	addi.n	a5, a5, 2	# ivtmp$15, ivtmp$15,
# @OPUS@\upstream\silk\ana_filt_bank_1.c:51:     for( k = 0; k < N2; k++ ) {
	bne	a6, a2, .L5	#, ivtmp$14,
	l32i.n	a7, sp, 4	# %sfp,
	s32i.n	a9, a7, 0	# *S_52(D), S__lsm$10
	s32i.n	a3, a7, 4	# MEM[(opus_int32 *)S_52(D) + 4B], S__lsm$11
.L1:
# @OPUS@\upstream\silk\ana_filt_bank_1.c:74: }
	l32i.n	a12, sp, 28	#,
	l32i.n	a13, sp, 24	#,
	l32i.n	a14, sp, 20	#,
	l32i.n	a15, sp, 16	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_ana_filt_bank_1, .-silk_ana_filt_bank_1
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
