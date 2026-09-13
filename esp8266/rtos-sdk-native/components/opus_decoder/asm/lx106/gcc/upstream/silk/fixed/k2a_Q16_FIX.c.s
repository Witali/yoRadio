# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/k2a_Q16_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"k2a_Q16_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_Q16_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_Q16_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_Q16_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\k2a_Q16_FIX.c.s.raw
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
	.section	.text.silk_k2a_Q16,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_k2a_Q16
	.type	silk_k2a_Q16, @function
# Function: silk_k2a_Q16
# Module: upstream/silk/fixed/k2a_Q16_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "SigProc_FIX.h"
# C context:
# C context: /* Step up function, converts reflection coefficients to prediction coefficients */
# C context: void silk_k2a_Q16(
# C context: opus_int32                  *A_Q24,             /* O    Prediction coefficients [order] Q24                         */
# C context: const opus_int32            *rc_Q16,            /* I    Reflection coefficients [order] Q16                         */
# C context: const opus_int32            order               /* I    Prediction order                                            */
# C context: )
silk_k2a_Q16:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 44	#,
	s32i.n	a13, sp, 40	#,
	s32i.n	a14, sp, 36	#,
	s32i.n	a15, sp, 32	#,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:40: {
	s32i.n	a4, sp, 16	# %sfp, order
	s32i.n	a2, sp, 12	# %sfp, A_Q24
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:44:     for( k = 0; k < order; k++ ) {
	bgei	a4, 1, .L2	# order,,
	j	.L1		#
.L4:
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:45:         rc = rc_Q16[ k ];
	l32i.n	a2, sp, 8	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	l32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:45:         rc = rc_Q16[ k ];
	l32i.n	a15, a2, 0	# MEM[base: _97, offset: 0B], rc
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	addi.n	a3, a3, 1	#,,
	l32i.n	a2, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	srai	a12, a15, 15	# tmp95, rc,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	srai	a14, a3, 1	# tmp98,,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	addi.n	a12, a12, 1	# tmp96, tmp95,
	slli	a8, a15, 16	# tmp97, rc,
	slli	a14, a14, 2	# tmp99, tmp98,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	s32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	srai	a12, a12, 1	# _23, tmp96,
	srai	a8, a8, 16	# _127, tmp97,
	add.n	a14, a2, a14	# _105,, tmp99
	l32i.n	a9, sp, 4	# %sfp, ivtmp$8
	mov.n	a6, a2	# ivtmp$7,
	j	.L3		#
.L11:
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	l32i.n	a3, sp, 4	# %sfp,
	l32i.n	a2, sp, 8	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	slli	a15, a15, 8	# tmp100, rc,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	neg	a15, a15	# tmp101, tmp100
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	s32i.n	a15, a3, 4	# MEM[base: _96, offset: 4B], tmp101
	addi.n	a2, a2, 4	#,,
	addi.n	a3, a3, 4	#,,
	s32i.n	a2, sp, 8	# %sfp,
	s32i.n	a3, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:44:     for( k = 0; k < order; k++ ) {
	l32i.n	a2, sp, 0	# %sfp,
	l32i.n	a3, sp, 16	# %sfp,
	bne	a3, a2, .L4	#,,
	j	.L1		#
.L3:
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:48:             tmp2 = A_Q24[ k - n - 1 ];
	l32i.n	a10, a9, 0	# MEM[base: _110, offset: 0B], tmp2
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:47:             tmp1 = A_Q24[ n ];
	l32i.n	a4, a6, 0	# MEM[base: _112, offset: 0B], tmp1
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	srai	a3, a10, 16	# tmp102, tmp2,
	mull	a11, a12, a10	# tmp104, _23, tmp2
	extui	a5, a10, 0, 16	# tmp107, tmp2,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWW( tmp2, tmp1, rc );
	mull	a2, a12, a4	# tmp111, _23, tmp1
	srai	a7, a4, 16	# tmp113, tmp1,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	mull	a3, a3, a8	# tmp103, tmp102, _127
	mull	a5, a5, a8	# tmp108, tmp107, _127
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWW( tmp2, tmp1, rc );
	extui	a13, a4, 0, 16	# tmp116, tmp1,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	add.n	a11, a11, a4	# tmp105, tmp104, tmp1
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWW( tmp2, tmp1, rc );
	mull	a7, a7, a8	# tmp114, tmp113, _127
	mull	a4, a13, a8	# tmp117, tmp116, _127
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	add.n	a3, a3, a11	# tmp106, tmp103, tmp105
	srai	a5, a5, 16	# tmp109, tmp108,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWW( tmp2, tmp1, rc );
	add.n	a2, a2, a10	# tmp112, tmp111, tmp2
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	add.n	a3, a3, a5	# tmp110, tmp106, tmp109
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWW( tmp2, tmp1, rc );
	add.n	a2, a2, a7	# tmp115, tmp112, tmp114
	srai	a4, a4, 16	# tmp118, tmp117,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:49:             A_Q24[ n ]         = silk_SMLAWW( tmp1, tmp2, rc );
	s32i.n	a3, a6, 0	# MEM[base: _112, offset: 0B], tmp110
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWW( tmp2, tmp1, rc );
	add.n	a2, a2, a4	# tmp119, tmp115, tmp118
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:50:             A_Q24[ k - n - 1 ] = silk_SMLAWW( tmp2, tmp1, rc );
	s32i.n	a2, a9, 0	# MEM[base: _110, offset: 0B], tmp119
	addi.n	a6, a6, 4	# ivtmp$7, ivtmp$7,
	addi	a9, a9, -4	# ivtmp$8, ivtmp$8,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	bne	a14, a6, .L3	# _105, ivtmp$7,
	j	.L11		#
.L2:
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	l32i.n	a2, a3, 0	# *rc_Q16_49(D), *rc_Q16_49(D)
	addi.n	a3, a3, 4	#, rc_Q16,
	s32i.n	a3, sp, 8	# %sfp,
	slli	a2, a2, 8	# tmp120, *rc_Q16_49(D),
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	l32i.n	a3, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	neg	a2, a2	# tmp122, tmp120
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:52:         A_Q24[ k ] = -silk_LSHIFT( rc, 8 );
	s32i.n	a2, a3, 0	# *A_Q24_51(D), tmp122
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:44:     for( k = 0; k < order; k++ ) {
	s32i.n	a3, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	movi.n	a2, 1	#,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:44:     for( k = 0; k < order; k++ ) {
	l32i.n	a3, sp, 16	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:46:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	s32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:44:     for( k = 0; k < order; k++ ) {
	bne	a3, a2, .L4	#,,
.L1:
# @OPUS@\upstream\silk\fixed\k2a_Q16_FIX.c:54: }
	l32i.n	a12, sp, 44	#,
	l32i.n	a13, sp, 40	#,
	l32i.n	a14, sp, 36	#,
	l32i.n	a15, sp, 32	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_k2a_Q16, .-silk_k2a_Q16
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
