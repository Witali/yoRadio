# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/k2a_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"k2a_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\k2a_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_FIX.c.s.raw
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
	.section	.text.silk_k2a,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_k2a
	.type	silk_k2a, @function
# Function: silk_k2a
# Module: upstream/silk/fixed/k2a_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "SigProc_FIX.h"
# C context:
# C context: /* Step up function, converts reflection coefficients to prediction coefficients */
# C context: void silk_k2a(
# C context: opus_int32                  *A_Q24,             /* O    Prediction coefficients [order] Q24                         */
# C context: const opus_int16            *rc_Q15,            /* I    Reflection coefficients [order] Q15                         */
# C context: const opus_int32            order               /* I    Prediction order                                            */
# C context: )
silk_k2a:
	addi	sp, sp, -32	#,,
	s32i.n	a12, sp, 28	#,
	s32i.n	a13, sp, 24	#,
	s32i.n	a14, sp, 20	#,
	s32i.n	a15, sp, 16	#,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:40: {
	s32i.n	a4, sp, 0	# %sfp, order
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:44:     for( k = 0; k < order; k++ ) {
	bgei	a4, 1, .L2	# order,,
	j	.L1		#
.L4:
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	addi.n	a13, a13, 1	# _59, _59,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	srai	a12, a13, 1	# tmp95, _59,
	slli	a12, a12, 2	# tmp96, tmp95,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:45:         rc = rc_Q15[ k ];
	l16si	a8, a15, 0	# MEM[base: _106, offset: 0B], _4
	add.n	a12, a2, a12	# _114, A_Q24, tmp96
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	mov.n	a9, a14	# ivtmp$12, ivtmp$21
	mov.n	a7, a2	# ivtmp$11, A_Q24
.L3:
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:48:             tmp2 = A_Q24[ k - n - 1 ];
	l32i.n	a10, a9, 0	# MEM[base: _121, offset: 0B], tmp2
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:47:             tmp1 = A_Q24[ n ];
	l32i.n	a11, a7, 0	# MEM[base: _123, offset: 0B], tmp1
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWB( tmp1, silk_LSHIFT( tmp2, 1 ), rc );
	slli	a4, a10, 1	# _15, tmp2,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWB( tmp2, silk_LSHIFT( tmp1, 1 ), rc );
	slli	a3, a11, 1	# _25, tmp1,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWB( tmp1, silk_LSHIFT( tmp2, 1 ), rc );
	extui	a6, a4, 0, 16	# tmp97, _15,
	srai	a4, a4, 16	# tmp100, _15,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWB( tmp2, silk_LSHIFT( tmp1, 1 ), rc );
	extui	a5, a3, 0, 16	# tmp104, _25,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWB( tmp1, silk_LSHIFT( tmp2, 1 ), rc );
	mull	a6, a6, a8	# tmp98, tmp97, _4
	mull	a4, a4, a8	# tmp101, tmp100, _4
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWB( tmp2, silk_LSHIFT( tmp1, 1 ), rc );
	srai	a3, a3, 16	# tmp107, _25,
	mull	a5, a5, a8	# tmp105, tmp104, _4
	mull	a3, a3, a8	# tmp108, tmp107, _4
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWB( tmp1, silk_LSHIFT( tmp2, 1 ), rc );
	srai	a6, a6, 16	# tmp99, tmp98,
	add.n	a4, a4, a11	# tmp102, tmp101, tmp1
	add.n	a4, a6, a4	# tmp103, tmp99, tmp102
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWB( tmp2, silk_LSHIFT( tmp1, 1 ), rc );
	srai	a5, a5, 16	# tmp106, tmp105,
	add.n	a3, a3, a10	# tmp109, tmp108, tmp2
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWB( tmp1, silk_LSHIFT( tmp2, 1 ), rc );
	s32i.n	a4, a7, 0	# MEM[base: _123, offset: 0B], tmp103
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWB( tmp2, silk_LSHIFT( tmp1, 1 ), rc );
	add.n	a3, a5, a3	# tmp110, tmp106, tmp109
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWB( tmp2, silk_LSHIFT( tmp1, 1 ), rc );
	s32i.n	a3, a9, 0	# MEM[base: _121, offset: 0B], tmp110
	addi.n	a7, a7, 4	# ivtmp$11, ivtmp$11,
	addi	a9, a9, -4	# ivtmp$12, ivtmp$12,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	bne	a12, a7, .L3	# _114, ivtmp$11,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( (opus_int32)rc_Q15[ k ], 9 );
	slli	a8, a8, 9	# tmp111, _4,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( (opus_int32)rc_Q15[ k ], 9 );
	neg	a8, a8	# tmp112, tmp111
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:44:     for( k = 0; k < order; k++ ) {
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( (opus_int32)rc_Q15[ k ], 9 );
	s32i.n	a8, a14, 4	# MEM[base: _105, offset: 4B], tmp112
	addi.n	a15, a15, 2	# ivtmp$18, ivtmp$18,
	addi.n	a14, a14, 4	# ivtmp$21, ivtmp$21,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:44:     for( k = 0; k < order; k++ ) {
	bne	a4, a13, .L4	#, _59,
	j	.L1		#
.L2:
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( (opus_int32)rc_Q15[ k ], 9 );
	l16si	a4, a3, 0	# *rc_Q15_48(D), tmp113
	addi.n	a15, a3, 2	# ivtmp$18, rc_Q15,
	slli	a3, a4, 9	# tmp116, tmp113,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( (opus_int32)rc_Q15[ k ], 9 );
	neg	a3, a3	# tmp117, tmp116
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:44:     for( k = 0; k < order; k++ ) {
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( (opus_int32)rc_Q15[ k ], 9 );
	s32i.n	a3, a2, 0	# *A_Q24_50(D), tmp117
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	movi.n	a13, 1	# _59,
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:44:     for( k = 0; k < order; k++ ) {
	mov.n	a14, a2	# ivtmp$21, A_Q24
	bne	a4, a13, .L4	#,,
.L1:
# @OPUS@\upstream\silk\fixed\k2a_FIX.c:54: }
	l32i.n	a12, sp, 28	#,
	l32i.n	a13, sp, 24	#,
	l32i.n	a14, sp, 20	#,
	l32i.n	a15, sp, 16	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_k2a, .-silk_k2a
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
