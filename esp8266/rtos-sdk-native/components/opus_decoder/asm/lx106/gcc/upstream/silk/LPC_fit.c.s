# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/LPC_fit.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"LPC_fit.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\LPC_fit.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\LPC_fit.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\LPC_fit.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\LPC_fit.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\LPC_fit.c.s.raw
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
	.section	.text.silk_LPC_fit,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, 163838
	.literal .LC3, -32767
	.literal .LC4, 65470
	.align	4
	.global	silk_LPC_fit
	.type	silk_LPC_fit, @function
# Function: silk_LPC_fit
# Module: upstream/silk/LPC_fit.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Convert int32 coefficients to int16 coefs and make sure there's no wrap-around.
# C context: This logic is reused in _celt_lpc(). Any bug fixes should also be applied there. */
# C context: void silk_LPC_fit(
# C context: opus_int16                  *a_QOUT,            /* O    Output signal                                               */
# C context: opus_int32                    *a_QIN,             /* I/O  Input signal                                                */
# C context: const opus_int              QOUT,               /* I    Input Q domain                                              */
# C context: const opus_int              QIN,                /* I    Input Q domain                                              */
silk_LPC_fit:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 40	#,
	s32i.n	a13, sp, 36	#,
	s32i.n	a14, sp, 32	#,
	s32i.n	a15, sp, 28	#,
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\silk\LPC_fit.c:43: {
	s32i.n	a2, sp, 0	# %sfp, a_QOUT
	mov.n	a12, a3	# a_QIN, a_QIN
	mov.n	a13, a6	# d, d
# @OPUS@\upstream\silk\LPC_fit.c:58:         maxabs = silk_RSHIFT_ROUND( maxabs, QIN - QOUT );
	sub	a15, a5, a4	# _5, QIN, QOUT
	movi.n	a14, 0xa	# ivtmp_88,
# @OPUS@\upstream\silk\LPC_fit.c:44:     opus_int    i, k, idx = 0;
	movi.n	a7, 0	# idx,
	l32r	a8, .LC0	#, tmp190
	j	.L2		#
.L4:
# @OPUS@\upstream\silk\LPC_fit.c:52:             absval = silk_abs( a_QIN[k] );
	l32i.n	a2, a4, 0	# MEM[base: _174, offset: 0B], MEM[base: _174, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$43, ivtmp$43,
	abs	a2, a2	# absval, MEM[base: _174, offset: 0B]
# @OPUS@\upstream\silk\LPC_fit.c:53:             if( absval > maxabs ) {
	bge	a9, a2, .L3	# maxabs, absval,
	mov.n	a7, a3	# idx, k
	mov.n	a9, a2	# maxabs, absval
.L3:
# @OPUS@\upstream\silk\LPC_fit.c:51:         for( k = 0; k < d; k++ ) {
	addi.n	a3, a3, 1	# k, k,
# @OPUS@\upstream\silk\LPC_fit.c:51:         for( k = 0; k < d; k++ ) {
	bne	a13, a3, .L4	# d, k,
.L13:
# @OPUS@\upstream\silk\LPC_fit.c:58:         maxabs = silk_RSHIFT_ROUND( maxabs, QIN - QOUT );
	bnei	a15, 1, .L5	# _5,,
# @OPUS@\upstream\silk\LPC_fit.c:58:         maxabs = silk_RSHIFT_ROUND( maxabs, QIN - QOUT );
	srai	a2, a9, 1	# tmp133, maxabs,
	extui	a9, a9, 0, 1	# tmp134, maxabs,
	add.n	a9, a2, a9	# iftmp$1_104, tmp133, tmp134
	j	.L6		#
.L5:
# @OPUS@\upstream\silk\LPC_fit.c:58:         maxabs = silk_RSHIFT_ROUND( maxabs, QIN - QOUT );
	addi.n	a2, a15, -1	# tmp191, _5,
	ssr	a2	# tmp191
	sra	a9, a9	# tmp136, maxabs
	addi.n	a9, a9, 1	# tmp137, tmp136,
	srai	a9, a9, 1	# iftmp$1_104, tmp137,
.L6:
# @OPUS@\upstream\silk\LPC_fit.c:60:         if( maxabs > silk_int16_MAX ) {
	blt	a8, a9, .L7	# tmp190, iftmp$1_104,
# @OPUS@\upstream\silk\LPC_fit.c:78:         for( k = 0; k < d; k++ ) {
	bgei	a13, 1, .L8	# d,,
	j	.L1		#
.L7:
# @OPUS@\upstream\silk\LPC_fit.c:62:             maxabs = silk_min( maxabs, 163838 );  /* ( silk_int32_MAX >> 14 ) + silk_int16_MAX = 163838 */
	l32r	a2, .LC2	#,
	bge	a2, a9, .L9	#, maxabs,
	mov.n	a9, a2	# maxabs,
.L9:
# @OPUS@\upstream\silk\LPC_fit.c:63:             chirp_Q16 = SILK_FIX_CONST( 0.999, 16 ) - silk_DIV32( silk_LSHIFT( maxabs - silk_int16_MAX, 14 ),
	addi.n	a3, a7, 1	# tmp147, idx,
	l32r	a2, .LC3	#, tmp145
	mull	a3, a3, a9	# tmp148, tmp147, maxabs
	add.n	a2, a9, a2	# tmp144, maxabs, tmp145
	srai	a3, a3, 2	#, tmp148,
	slli	a2, a2, 14	#, tmp144,
	s32i.n	a7, sp, 4	#,
	s32i.n	a8, sp, 8	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\LPC_fit.c:65:             silk_bwexpander_32( a_QIN, d, chirp_Q16 );
	l32r	a4, .LC4	#, tmp155
	mov.n	a3, a13	#, d
	sub	a4, a4, a2	#, tmp155,
	mov.n	a2, a12	#, a_QIN
	call0	silk_bwexpander_32		#
	addi.n	a14, a14, -1	# ivtmp_88, ivtmp_88,
# @OPUS@\upstream\silk\LPC_fit.c:48:     for( i = 0; i < 10; i++ ) {
	l32i.n	a7, sp, 4	#,
	l32i.n	a8, sp, 8	#,
	bnez.n	a14, .L2	# ivtmp_88,
# @OPUS@\upstream\silk\LPC_fit.c:73:         for( k = 0; k < d; k++ ) {
	bgei	a13, 1, .L10	# d,,
	j	.L1		#
.L2:
# @OPUS@\upstream\silk\LPC_fit.c:50:         maxabs = 0;
	movi.n	a9, 0	# maxabs,
	mov.n	a4, a12	# ivtmp$43, a_QIN
# @OPUS@\upstream\silk\LPC_fit.c:51:         for( k = 0; k < d; k++ ) {
	mov.n	a3, a9	# k, maxabs
# @OPUS@\upstream\silk\LPC_fit.c:51:         for( k = 0; k < d; k++ ) {
	bgei	a13, 1, .L4	# d,,
	j	.L13		#
.L10:
	beqi	a15, 1, .L14	# _5,,
	slli	a6, a13, 2	# tmp156, d,
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	l32r	a7, .LC1	#, tmp205
	l32i.n	a13, sp, 0	# %sfp, ivtmp$27
	add.n	a9, a12, a6	# _26, ivtmp$26, tmp156
	addi.n	a2, a15, -1	# tmp191, _5,
.L16:
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	l32i.n	a3, a12, 0	# MEM[base: _109, offset: 0B], MEM[base: _109, offset: 0B]
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	mov.n	a4, a8	# _133, tmp190
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	ssr	a2	# tmp191
	sra	a3, a3	# tmp158, MEM[base: _109, offset: 0B]
	addi.n	a3, a3, 1	# tmp160, tmp158,
	srai	a3, a3, 1	# _34, tmp160,
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	mov.n	a6, a8	# iftmp$12_35, tmp190
	blt	a8, a3, .L15	# tmp190, _34,
	slli	a6, a3, 16	# tmp163, _34,
	blt	a3, a7, .L25	# _34, tmp205,
	srai	a6, a6, 16	# iftmp$12_35, tmp163,
	mov.n	a4, a3	# _133, _34
	j	.L15		#
.L25:
	mov.n	a4, a7	# _133, tmp205
	mov.n	a6, a7	# iftmp$12_35, tmp205
.L15:
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	s16i	a6, a13, 0	# MEM[base: _150, offset: 0B], iftmp$12_35
# @OPUS@\upstream\silk\LPC_fit.c:75:             a_QIN[ k ] = silk_LSHIFT( (opus_int32)a_QOUT[ k ], QIN - QOUT );
	ssl	a15	# _5
	sll	a4, a4	# tmp164, _133
# @OPUS@\upstream\silk\LPC_fit.c:75:             a_QIN[ k ] = silk_LSHIFT( (opus_int32)a_QOUT[ k ], QIN - QOUT );
	s32i.n	a4, a12, 0	# MEM[base: _109, offset: 0B], tmp164
	addi.n	a12, a12, 4	# ivtmp$26, ivtmp$26,
	addi.n	a13, a13, 2	# ivtmp$27, ivtmp$27,
# @OPUS@\upstream\silk\LPC_fit.c:73:         for( k = 0; k < d; k++ ) {
	bne	a9, a12, .L16	# _26, ivtmp$26,
	j	.L1		#
.L14:
	slli	a5, a13, 2	# tmp165, d,
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	l32r	a7, .LC1	#, tmp209
	l32i.n	a13, sp, 0	# %sfp, ivtmp$32
	add.n	a5, a12, a5	# _105, ivtmp$31, tmp165
.L18:
	l32i.n	a2, a12, 0	# MEM[base: _156, offset: 0B], pretmp_60
	mov.n	a3, a8	# prephitmp_28, tmp190
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	srai	a4, a2, 1	# _84, pretmp_60,
	extui	a2, a2, 0, 1	# tmp189, pretmp_60,
	add.n	a2, a2, a4	# _86, tmp189, _84
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	mov.n	a4, a8	# iftmp$12_78, tmp190
	blt	a8, a2, .L19	# tmp190, _86,
	slli	a4, a2, 16	# tmp174, _86,
	srai	a4, a4, 16	# iftmp$12_78, tmp174,
	mov.n	a3, a4	# prephitmp_28, iftmp$12_78
	bge	a2, a7, .L19	# _86, tmp209,
.L27:
	mov.n	a3, a7	# prephitmp_28, tmp209
	mov.n	a4, a7	# iftmp$12_78, tmp209
.L19:
# @OPUS@\upstream\silk\LPC_fit.c:74:             a_QOUT[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT ) );
	s16i	a4, a13, 0	# MEM[base: _67, offset: 0B], iftmp$12_78
# @OPUS@\upstream\silk\LPC_fit.c:75:             a_QIN[ k ] = silk_LSHIFT( (opus_int32)a_QOUT[ k ], QIN - QOUT );
	slli	a3, a3, 1	# tmp175, prephitmp_28,
# @OPUS@\upstream\silk\LPC_fit.c:75:             a_QIN[ k ] = silk_LSHIFT( (opus_int32)a_QOUT[ k ], QIN - QOUT );
	s32i.n	a3, a12, 0	# MEM[base: _156, offset: 0B], tmp175
	addi.n	a12, a12, 4	# ivtmp$31, ivtmp$31,
	addi.n	a13, a13, 2	# ivtmp$32, ivtmp$32,
# @OPUS@\upstream\silk\LPC_fit.c:73:         for( k = 0; k < d; k++ ) {
	bne	a12, a5, .L18	# ivtmp$31, _105,
	j	.L1		#
.L8:
	beqi	a15, 1, .L20	# _5,,
	slli	a4, a13, 2	# tmp176, d,
	l32i.n	a13, sp, 0	# %sfp, ivtmp$36
	add.n	a4, a12, a4	# _137, ivtmp$35, tmp176
	addi.n	a2, a15, -1	# tmp191, _5,
.L21:
# @OPUS@\upstream\silk\LPC_fit.c:79:             a_QOUT[ k ] = (opus_int16)silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT );
	l32i.n	a3, a12, 0	# MEM[base: _69, offset: 0B], MEM[base: _69, offset: 0B]
	addi.n	a12, a12, 4	# ivtmp$35, ivtmp$35,
	ssr	a2	# tmp191
	sra	a3, a3	# tmp178, MEM[base: _69, offset: 0B]
	addi.n	a3, a3, 1	# tmp180, tmp178,
	srai	a3, a3, 1	# tmp181, tmp180,
# @OPUS@\upstream\silk\LPC_fit.c:79:             a_QOUT[ k ] = (opus_int16)silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT );
	s16i	a3, a13, 0	# MEM[base: _135, offset: 0B], tmp181
	addi.n	a13, a13, 2	# ivtmp$36, ivtmp$36,
# @OPUS@\upstream\silk\LPC_fit.c:78:         for( k = 0; k < d; k++ ) {
	bne	a4, a12, .L21	# _137, ivtmp$35,
	j	.L1		#
.L20:
	slli	a2, a13, 2	# tmp182, d,
	l32i.n	a13, sp, 0	# %sfp, ivtmp$40
	add.n	a2, a12, a2	# _148, ivtmp$39, tmp182
.L23:
	l32i.n	a3, a12, 0	# MEM[base: _164, offset: 0B], pretmp_185
	addi.n	a12, a12, 4	# ivtmp$39, ivtmp$39,
# @OPUS@\upstream\silk\LPC_fit.c:79:             a_QOUT[ k ] = (opus_int16)silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT );
	srai	a4, a3, 1	# tmp183, pretmp_185,
	extui	a3, a3, 0, 1	# tmp185, pretmp_185,
# @OPUS@\upstream\silk\LPC_fit.c:79:             a_QOUT[ k ] = (opus_int16)silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT );
	add.n	a3, a4, a3	# tmp188, tmp183, tmp185
# @OPUS@\upstream\silk\LPC_fit.c:79:             a_QOUT[ k ] = (opus_int16)silk_RSHIFT_ROUND( a_QIN[ k ], QIN - QOUT );
	s16i	a3, a13, 0	# MEM[base: _162, offset: 0B], tmp188
	addi.n	a13, a13, 2	# ivtmp$40, ivtmp$40,
# @OPUS@\upstream\silk\LPC_fit.c:78:         for( k = 0; k < d; k++ ) {
	bne	a2, a12, .L23	# _148, ivtmp$39,
.L1:
# @OPUS@\upstream\silk\LPC_fit.c:82: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_LPC_fit, .-silk_LPC_fit
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
