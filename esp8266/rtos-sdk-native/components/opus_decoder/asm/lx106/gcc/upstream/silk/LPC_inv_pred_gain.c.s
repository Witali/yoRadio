# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/LPC_inv_pred_gain.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"LPC_inv_pred_gain.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\LPC_inv_pred_gain.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\LPC_inv_pred_gain.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\LPC_inv_pred_gain.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\LPC_inv_pred_gain.c.s.raw
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
	.global	__muldi3
	.global	__divsi3
	.section	.text.silk_LPC_inverse_pred_gain_c,"ax",@progbits
	.literal_position
	.literal .LC0, 1073741824
	.literal .LC1, 16773022
	.literal .LC2, 4095
	.literal .LC3, 33546044
	.literal .LC4, 107373
	.literal .LC5, 536870911
	.literal .LC6, 536870912
	.literal .LC7, 2147483647, 0
	.literal .LC8, -2147483648, -1
	.literal .LC10, -2147483648
	.align	4
	.global	silk_LPC_inverse_pred_gain_c
	.type	silk_LPC_inverse_pred_gain_c, @function
# Function: silk_LPC_inverse_pred_gain_c
# Module: upstream/silk/LPC_inv_pred_gain.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* For input in Q12 domain */
# C context: opus_int32 silk_LPC_inverse_pred_gain_c(            /* O   Returns inverse prediction gain in energy domain, Q30        */
# C context: const opus_int16            *A_Q12,             /* I   Prediction coefficients, Q12 [order]                         */
# C context: const opus_int              order               /* I   Prediction order                                             */
# C context: )
# C context: {
silk_LPC_inverse_pred_gain_c:
	movi	a9, 0xe0	#,
	sub	sp, sp, a9	#,,
	s32i	a12, sp, 216	#,
	s32i	a0, sp, 220	#,
	s32i	a13, sp, 212	#,
	s32i	a14, sp, 208	#,
	s32i	a15, sp, 204	#,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:126: {
	mov.n	a12, a3	# order, order
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:132:     for( k = 0; k < order; k++ ) {
	bgei	a3, 1, .L2	# order,,
.L7:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:51:     for( k = order - 1; k > 0; k-- ) {
	addi.n	a3, a12, -1	# k, order,
	slli	a2, a3, 2	# tmp271, k,
	add.n	a2, sp, a2	# tmp272,, tmp271
	l32i.n	a2, a2, 0	# MEM[(opus_int32 *)_590], pretmp_591
	l32r	a5, .LC1	#,
	add.n	a4, a2, a5	# _593, pretmp_591,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:51:     for( k = order - 1; k > 0; k-- ) {
	bgei	a3, 1, .L3	# k,,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:50:     invGain_Q30 = SILK_FIX_CONST( 1, 30 );
	l32r	a6, .LC0	#,
	l32r	a7, .LC3	#,
	s32i	a6, sp, 180	# %sfp,
	s32i	a7, sp, 176	# %sfp,
	s32i	a6, sp, 156	# %sfp,
	j	.L4		#
.L2:
	slli	a7, a3, 1	# tmp274, order,
	add.n	a7, a2, a7	# _712, ivtmp$70, tmp274
	mov.n	a3, sp	# ivtmp$71,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:129:     opus_int32 DC_resp = 0;
	movi.n	a5, 0	# DC_resp,
.L5:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:133:         DC_resp += (opus_int32)A_Q12[ k ];
	l16si	a4, a2, 0	# MEM[base: _717, offset: 0B], _4
	addi.n	a2, a2, 2	# ivtmp$70, ivtmp$70,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:134:         Atmp_QA[ k ] = silk_LSHIFT32( (opus_int32)A_Q12[ k ], QA - 12 );
	slli	a6, a4, 12	# tmp277, _4,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:134:         Atmp_QA[ k ] = silk_LSHIFT32( (opus_int32)A_Q12[ k ], QA - 12 );
	s32i.n	a6, a3, 0	# MEM[base: _716, offset: 0B], tmp277
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:133:         DC_resp += (opus_int32)A_Q12[ k ];
	add.n	a5, a5, a4	# DC_resp, DC_resp, _4
	addi.n	a3, a3, 4	# ivtmp$71, ivtmp$71,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:132:     for( k = 0; k < order; k++ ) {
	bne	a7, a2, .L5	# _712, ivtmp$70,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:137:     if( DC_resp >= 4096 ) {
	l32r	a2, .LC2	#, tmp278
	blt	a2, a5, .L6	# tmp278, DC_resp,
	j	.L7		#
.L3:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:53:         if( ( A_QA[ k ] > A_LIMIT ) || ( A_QA[ k ] < -A_LIMIT ) ) {
	l32r	a6, .LC3	#,
	s32i	a6, sp, 176	# %sfp,
	bltu	a6, a4, .L6	#, _593,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:58:         rc_Q31 = -silk_LSHIFT( A_QA[ k ], 31 - QA );
	slli	a2, a2, 7	# tmp280, pretmp_591,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:58:         rc_Q31 = -silk_LSHIFT( A_QA[ k ], 31 - QA );
	neg	a2, a2	#, tmp280
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	srai	a7, a2, 31	#,,
	mov.n	a5, a7	#,
	mov.n	a3, a7	#, tmp5
	mov.n	a4, a2	#,
	s32i	a7, sp, 108	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:58:         rc_Q31 = -silk_LSHIFT( A_QA[ k ], 31 - QA );
	s32i	a2, sp, 104	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	call0	__muldi3		#
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	l32r	a6, .LC0	#,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:70:         if( invGain_Q30 < SILK_FIX_CONST( 1.0f / MAX_PREDICTION_POWER_GAIN, 30 ) ) {
	l32r	a7, .LC4	#,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	sub	a13, a6, a3	# rc_mult1_Q30,,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:67:         invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	srli	a2, a13, 2	# tmp289, rc_mult1_Q30,
	slli	a2, a2, 2	#, tmp289,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	s32i	a6, sp, 180	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:67:         invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	s32i	a2, sp, 156	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:70:         if( invGain_Q30 < SILK_FIX_CONST( 1.0f / MAX_PREDICTION_POWER_GAIN, 30 ) ) {
	bge	a7, a2, .L6	#,,
	addi	a2, a12, -2	# tmp292, order,
	slli	a2, a2, 2	# tmp293, tmp292,
	add.n	a2, sp, a2	#,, tmp293
	s32i	a2, sp, 164	# %sfp,
	s32i	a12, sp, 160	# %sfp, order
	movi.n	a15, 1	# tmp834,
	j	.L8		#
.L11:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:53:         if( ( A_QA[ k ] > A_LIMIT ) || ( A_QA[ k ] < -A_LIMIT ) ) {
	l32i	a6, sp, 176	# %sfp,
	bltu	a6, a4, .L6	#, _593,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:58:         rc_Q31 = -silk_LSHIFT( A_QA[ k ], 31 - QA );
	slli	a2, a2, 7	# tmp295, pretmp_768,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:58:         rc_Q31 = -silk_LSHIFT( A_QA[ k ], 31 - QA );
	neg	a2, a2	#, tmp295
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	srai	a7, a2, 31	#,,
	mov.n	a5, a7	#,
	mov.n	a3, a7	#, tmp5
	mov.n	a4, a2	#,
	s32i	a7, sp, 108	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:58:         rc_Q31 = -silk_LSHIFT( A_QA[ k ], 31 - QA );
	s32i	a2, sp, 104	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	call0	__muldi3		#
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	l32i	a6, sp, 180	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:67:         invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	l32i	a2, sp, 156	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:61:         rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	sub	a13, a6, a3	# rc_mult1_Q30,,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:67:         invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	mov.n	a4, a13	#, rc_mult1_Q30
	srai	a3, a2, 31	#,,
	srai	a5, a13, 31	#, rc_mult1_Q30,
	call0	__muldi3		#
	l32i	a7, sp, 164	# %sfp,
	l32i	a6, sp, 160	# %sfp,
	addi	a7, a7, -4	#,,
	slli	a3, a3, 2	#,,
	s32i	a7, sp, 164	# %sfp,
	addi.n	a6, a6, -1	#,,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:70:         if( invGain_Q30 < SILK_FIX_CONST( 1.0f / MAX_PREDICTION_POWER_GAIN, 30 ) ) {
	l32r	a7, .LC4	#,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:67:         invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	s32i	a3, sp, 156	# %sfp,
	s32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:70:         if( invGain_Q30 < SILK_FIX_CONST( 1.0f / MAX_PREDICTION_POWER_GAIN, 30 ) ) {
	bge	a7, a3, .L6	#,,
.L8:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a13, .L42	# rc_mult1_Q30,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:75:         mult2Q = 32 - silk_CLZ32( silk_abs( rc_mult1_Q30 ) );
	abs	a12, a13	# tmp308, rc_mult1_Q30
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a12, a12	# iftmp$45_51, tmp308
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:75:         mult2Q = 32 - silk_CLZ32( silk_abs( rc_mult1_Q30 ) );
	movi.n	a6, 0x20	#,
	sub	a6, a6, a12	#,, iftmp$45_51
	s32i	a6, sp, 124	# %sfp,
	addi.n	a14, a12, -1	# _672, iftmp$45_51,
	j	.L9		#
.L42:
	movi.n	a7, 0	#,
	s32i	a7, sp, 124	# %sfp,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a14, 0x1f	# _672,
	movi.n	a12, 0x20	# iftmp$45_51,
.L9:
# @OPUS@\upstream\silk\Inlines.h:156:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                */
	ssl	a14	# _672
	sll	a14, a13	# b32_nrm, rc_mult1_Q30
# @OPUS@\upstream\silk\Inlines.h:159:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm    */
	srai	a13, a14, 16	# _251, b32_nrm,
# @OPUS@\upstream\silk\Inlines.h:159:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm    */
	l32r	a2, .LC5	#,
	mov.n	a3, a13	#, _251
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	slli	a4, a2, 16	# tmp313, tmp312,
	srai	a5, a4, 16	# _257, tmp313,
	extui	a14, a14, 0, 16	# tmp317, b32_nrm,
	l32r	a3, .LC6	#,
	mull	a13, a13, a5	# tmp314, _251, _257
	mull	a14, a14, a5	# tmp318, tmp317, _257
	sub	a13, a3, a13	# tmp315,, tmp314
	srai	a14, a14, 16	# tmp319, tmp318,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	srai	a3, a2, 15	# tmp321, tmp312,
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	sub	a13, a13, a14	# tmp320, tmp315, tmp319
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	addi.n	a3, a3, 1	# tmp322, tmp321,
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	slli	a2, a13, 3	# err_Q32, tmp320,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	srai	a3, a3, 1	# tmp323, tmp322,
	mull	a3, a3, a2	# tmp324, tmp323, err_Q32
	srai	a6, a2, 16	# tmp327, err_Q32,
	extui	a2, a2, 0, 16	# tmp329, err_Q32,
	mull	a6, a6, a5	# tmp328, tmp327, _257
	mull	a2, a2, a5	# tmp330, tmp329, _257
	add.n	a3, a3, a4	# tmp326, tmp324, tmp313
	add.n	a3, a3, a6	# _295, tmp326, tmp328
	srai	a2, a2, 16	# tmp331, tmp330,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:79:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	add.n	a2, a2, a3	#, tmp331, _295
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:79:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	srai	a13, a6, 1	# _22,,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	s32i	a2, sp, 112	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:79:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	bgei	a13, 1, .L10	# _22,,
.L34:
	l32i	a7, sp, 164	# %sfp,
	l32r	a3, .LC1	#,
	l32i.n	a2, a7, 0	# MEM[base: _724, offset: 0B], pretmp_768
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:51:     for( k = order - 1; k > 0; k-- ) {
	l32i	a6, sp, 160	# %sfp,
	add.n	a4, a2, a3	# _593, pretmp_768,
	bnei	a6, 2, .L11	#,,
	j	.L4		#
.L10:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:83:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp1,
	srai	a7, a2, 31	#, tmp7,
	l32r	a4, .LC7	#,
	l32r	a5, .LC7+4	#,
	l32i	a2, sp, 112	# %sfp,
	mov.n	a3, a7	#,
	s32i	a7, sp, 116	# %sfp,
	call0	__muldi3		#
	mov.n	a7, a2	# tmp879,
	mov.n	a6, a3	# tmp880,
	srli	a2, a2, 1	#, tmp879,
	s32i	a2, sp, 152	# %sfp,
	s32i	a6, sp, 148	# %sfp, tmp880
	s32i	a7, sp, 144	# %sfp, tmp879
	l32i	a6, sp, 152	# %sfp,
	l32i	a7, sp, 148	# %sfp,
	slli	a8, a3, 31	# tmp335, tmp880,
	l32r	a4, .LC8	#,
	l32r	a5, .LC8+4	#,
	l32i	a2, sp, 112	# %sfp,
	l32i	a3, sp, 116	# %sfp,
	or	a6, a8, a6	#, tmp335,
	srai	a7, a7, 1	#,,
	s32i	a6, sp, 152	# %sfp,
	s32i	a7, sp, 172	# %sfp,
	call0	__muldi3		#
	movi.n	a4, 0x1f	#,
	ssl	a4	#
	sll	a5, a3	# tmp337, tmp882
	srli	a6, a2, 1	#, tmp881,
	or	a6, a5, a6	#, tmp337,
	sub	a12, a4, a12	#,, iftmp$45_51
	s32i	a2, sp, 132	# %sfp, tmp881
	slli	a4, a13, 2	# tmp338, _22,
	s32i	a6, sp, 140	# %sfp,
	movi.n	a2, -1	# tmp827,
	movi.n	a6, 0x20	#,
	srai	a7, a3, 1	#, tmp882,
	add.n	a4, a4, sp	#, tmp338,
	and	a6, a12, a6	#,,
	xor	a2, a12, a2	#,, tmp827
	l32i	a14, sp, 164	# %sfp, ivtmp$55
	s32i	a12, sp, 96	# %sfp,
	s32i	a3, sp, 136	# %sfp, tmp882
	s32i	a7, sp, 168	# %sfp,
	mov.n	a13, sp	# ivtmp$54,
	s32i	a4, sp, 128	# %sfp,
	s32i	a6, sp, 100	# %sfp,
	s32i	a2, sp, 120	# %sfp,
.L33:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:82:             tmp2 = A_QA[ k - n - 1 ];
	l32i.n	a12, a14, 0	# MEM[base: _757, offset: 0B], tmp2
	l32i	a4, sp, 104	# %sfp,
	l32i	a5, sp, 108	# %sfp,
	mov.n	a2, a12	#, tmp2
	srai	a3, a12, 31	#, tmp2,
	call0	__muldi3		#
	slli	a4, a3, 2	# tmp343, tmp570,
	extui	a5, a2, 30, 2	# tmp571,,
	or	a5, a4, a5	# tmp571, tmp343, tmp571
	addi.n	a2, a5, 1	# tmp573, tmp571,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:81:             tmp1 = A_QA[ n ];
	l32i.n	a6, a13, 0	# MEM[base: _758, offset: 0B], tmp1
	srai	a3, a3, 30	# tmp572, tmp570,
	mov.n	a4, a15	# mult2Q, tmp834
	bltu	a2, a5, .L12	# tmp573, tmp571,
	movi.n	a4, 0	# mult2Q,
.L12:
	add.n	a4, a4, a3	# tmp348, mult2Q, tmp572
	slli	a4, a4, 31	# tmp349, tmp348,
	srli	a2, a2, 1	# _739, tmp573,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:83:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp1,
	l32i	a7, sp, 124	# %sfp,
	or	a2, a4, a2	# _739, tmp349, _739
	sub	a3, a6, a2	# tmp643, tmp1, _739
	bnei	a7, 1, .L13	#,,
	bltz	a3, .L14	# tmp643,
	l32r	a4, .LC10	#,
	xor	a2, a2, a4	# tmp350, _739,
	and	a2, a2, a6	# tmp352, tmp350, tmp1
	bltz	a2, .L43	# tmp352,
	j	.L57		#
.L14:
	l32r	a5, .LC10	#,
	xor	a4, a6, a5	# tmp358, tmp1,
	and	a2, a4, a2	# tmp360, tmp358, _739
	bltz	a2, .L44	# tmp360,
.L57:
	l32i	a4, sp, 112	# %sfp,
	l32i	a5, sp, 116	# %sfp,
	mov.n	a2, a3	#, tmp643
	srai	a3, a3, 31	#, tmp643,
	s32i	a6, sp, 184	#,
	call0	__muldi3		#
	slli	a4, a3, 31	# tmp365, tmp886,
	srli	a7, a2, 1	# _334, tmp885,
	or	a7, a4, a7	# _334, tmp365, _334
	srai	a5, a3, 1	# _334, tmp886,
	l32i	a6, sp, 184	#,
	j	.L15		#
.L43:
	l32i	a2, sp, 132	# %sfp, _363
	l32i	a7, sp, 140	# %sfp, _334
	l32i	a5, sp, 168	# %sfp, _334
	j	.L15		#
.L44:
	l32i	a2, sp, 144	# %sfp, _363
	l32i	a7, sp, 152	# %sfp, _334
	l32i	a5, sp, 172	# %sfp, _334
.L15:
	extui	a2, a2, 0, 1	# tmp579, _363,
	add.n	a7, a2, a7	# tmp581, tmp579, _334
	mov.n	a4, a15	# mult2Q, tmp834
	bltu	a7, a2, .L16	# tmp581, tmp579,
	movi.n	a4, 0	# mult2Q,
.L16:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:85:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	l32r	a2, .LC10	#,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:83:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp1,
	add.n	a4, a4, a5	# tmp371, mult2Q, _334
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:85:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	add.n	a3, a7, a2	# tmp583, tmp581,
	mov.n	a2, a15	# mult2Q, tmp834
	bltu	a3, a7, .L17	# tmp583, tmp581,
	movi.n	a2, 0	# mult2Q,
.L17:
	add.n	a2, a2, a4	# tmp376, mult2Q, tmp371
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:85:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	beqz.n	a2, .L53	# tmp376,
	j	.L6		#
.L13:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:83:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp1,
	bltz	a3, .L20	# tmp643,
	l32r	a4, .LC10	#,
	xor	a2, a2, a4	# tmp377, _739,
	and	a2, a2, a6	# tmp379, tmp377, tmp1
	bltz	a2, .L45	# tmp379,
	j	.L58		#
.L20:
	l32r	a5, .LC10	#,
	xor	a4, a6, a5	# tmp384, tmp1,
	and	a2, a4, a2	# tmp386, tmp384, _739
	bltz	a2, .L46	# tmp386,
.L58:
	l32i	a4, sp, 112	# %sfp,
	l32i	a5, sp, 116	# %sfp,
	mov.n	a2, a3	#, tmp643
	srai	a3, a3, 31	#, tmp643,
	s32i	a6, sp, 184	#,
	call0	__muldi3		#
	l32i	a6, sp, 184	#,
	j	.L21		#
.L45:
	l32i	a2, sp, 132	# %sfp, _744
	l32i	a3, sp, 136	# %sfp, _744
	j	.L21		#
.L46:
	l32i	a2, sp, 144	# %sfp, _744
	l32i	a3, sp, 148	# %sfp, _744
.L21:
	l32i	a7, sp, 120	# %sfp,
	slli	a5, a3, 1	# tmp396, _744,
	ssl	a7	#
	sll	a5, a5	# tmp399, tmp396
	l32i	a7, sp, 96	# %sfp,
	ssr	a7	#
	sra	a4, a3	# tmp590, _744
	ssr	a7	#
	srl	a2, a2	# tmp589, _744
	l32i	a7, sp, 100	# %sfp,
	or	a2, a5, a2	# tmp589, tmp399, tmp589
	movnez	a2, a4, a7	# tmp589, tmp590,
	l32i	a5, sp, 100	# %sfp,
	srai	a3, a3, 31	# tmp395, _744,
	addi.n	a7, a2, 1	# tmp591, tmp589,
	movnez	a4, a3, a5	# tmp590, tmp395,
	mov.n	a3, a15	# mult2Q, tmp834
	bltu	a7, a2, .L22	# tmp591, tmp589,
	movi.n	a3, 0	# mult2Q,
.L22:
	add.n	a2, a3, a4	# tmp404, mult2Q, tmp590
	slli	a3, a2, 31	# tmp405, tmp404,
	srli	a7, a7, 1	# iftmp$5_135, tmp591,
	or	a7, a3, a7	# iftmp$5_135, tmp405, iftmp$5_135
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:85:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	l32r	a3, .LC10	#,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:83:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp1,
	srai	a2, a2, 1	# iftmp$5_135, tmp404,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:85:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	add.n	a4, a7, a3	# tmp593, iftmp$5_135,
	mov.n	a3, a15	# mult2Q, tmp834
	bltu	a4, a7, .L23	# tmp593, iftmp$5_135,
	movi.n	a3, 0	# mult2Q,
.L23:
	add.n	a2, a3, a2	# tmp410, mult2Q, iftmp$5_135
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:85:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	beqz.n	a2, .L54	# tmp410,
	j	.L6		#
.L40:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:89:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp2,
	l32r	a4, .LC10	#,
	xor	a2, a2, a4	# tmp411, _145,
	and	a12, a2, a12	# tmp413, tmp411, tmp2
	bltz	a12, .L47	# tmp413,
	j	.L59		#
.L56:
	l32r	a5, .LC10	#,
	xor	a12, a12, a5	# tmp419, tmp2,
	and	a2, a12, a2	# tmp421, tmp419, _145
	bltz	a2, .L48	# tmp421,
.L59:
	l32i	a4, sp, 112	# %sfp,
	l32i	a5, sp, 116	# %sfp,
	mov.n	a2, a3	#, tmp641
	srai	a3, a3, 31	#, tmp641,
	call0	__muldi3		#
	slli	a5, a3, 31	# tmp426, tmp894,
	srli	a4, a2, 1	# _288, tmp893,
	or	a4, a5, a4	# _288, tmp426, _288
	srai	a6, a3, 1	# _288, tmp894,
	j	.L26		#
.L47:
	l32i	a2, sp, 132	# %sfp, _10
	l32i	a4, sp, 140	# %sfp, _288
	l32i	a6, sp, 168	# %sfp, _288
	j	.L26		#
.L48:
	l32i	a2, sp, 144	# %sfp, _10
	l32i	a4, sp, 152	# %sfp, _288
	l32i	a6, sp, 172	# %sfp, _288
.L26:
	extui	a5, a2, 0, 1	# tmp599, _10,
	add.n	a2, a5, a4	# tmp601, tmp599, _288
	mov.n	a3, a15	# mult2Q, tmp834
	bltu	a2, a5, .L27	# tmp601, tmp599,
	movi.n	a3, 0	# mult2Q,
.L27:
	add.n	a3, a3, a6	# iftmp$25_208, mult2Q, _288
	j	.L28		#
.L37:
	l32r	a6, .LC10	#,
	xor	a2, a2, a6	# tmp433, _186,
	and	a12, a2, a12	# tmp435, tmp433, tmp2
	bltz	a12, .L49	# tmp435,
	j	.L60		#
.L55:
	l32r	a7, .LC10	#,
	xor	a12, a12, a7	# tmp440, tmp2,
	and	a2, a12, a2	# tmp442, tmp440, _186
	bltz	a2, .L50	# tmp442,
.L60:
	l32i	a4, sp, 112	# %sfp,
	l32i	a5, sp, 116	# %sfp,
	mov.n	a2, a3	#, tmp642
	srai	a3, a3, 31	#, tmp642,
	call0	__muldi3		#
	j	.L29		#
.L49:
	l32i	a2, sp, 132	# %sfp, _747
	l32i	a3, sp, 136	# %sfp, _747
	j	.L29		#
.L50:
	l32i	a2, sp, 144	# %sfp, _747
	l32i	a3, sp, 148	# %sfp, _747
.L29:
	l32i	a7, sp, 120	# %sfp,
	slli	a6, a3, 1	# tmp451, _747,
	ssl	a7	#
	sll	a6, a6	# tmp454, tmp451
	l32i	a7, sp, 96	# %sfp,
	ssr	a7	#
	srl	a4, a2	# tmp607, _747
	or	a4, a6, a4	# tmp607, tmp454, tmp607
	l32i	a6, sp, 100	# %sfp,
	ssr	a7	#
	sra	a5, a3	# tmp608, _747
	movnez	a4, a5, a6	# tmp607, tmp608,
	srai	a3, a3, 31	# tmp450, _747,
	addi.n	a2, a4, 1	# tmp609, tmp607,
	movnez	a5, a3, a6	# tmp608, tmp450,
	mov.n	a3, a15	# mult2Q, tmp834
	bltu	a2, a4, .L30	# tmp609, tmp607,
	movi.n	a3, 0	# mult2Q,
.L30:
	add.n	a3, a3, a5	# tmp459, mult2Q, tmp608
	slli	a4, a3, 31	# tmp460, tmp459,
	srli	a2, a2, 1	# iftmp$25_208, tmp609,
	or	a2, a4, a2	# iftmp$25_208, tmp460, iftmp$25_208
	srai	a3, a3, 1	# iftmp$25_208, tmp459,
.L28:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:91:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	l32r	a7, .LC10	#,
	mov.n	a4, a15	# mult2Q, tmp834
	add.n	a5, a2, a7	# tmp611, iftmp$25_208,
	bltu	a5, a2, .L31	# tmp611, iftmp$25_208,
	movi.n	a4, 0	# mult2Q,
.L31:
	add.n	a3, a4, a3	# tmp465, mult2Q, iftmp$25_208
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:91:             if( tmp64 > silk_int32_MAX || tmp64 < silk_int32_MIN ) {
	bnez.n	a3, .L6	# tmp465,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:79:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	l32i	a6, sp, 128	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:94:             A_QA[ k - n - 1 ] = ( opus_int32 )tmp64;
	s32i.n	a2, a14, 0	# MEM[base: _757, offset: 0B], iftmp$25_208
	addi.n	a13, a13, 4	# ivtmp$54, ivtmp$54,
	addi	a14, a14, -4	# ivtmp$55, ivtmp$55,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:79:         for( n = 0; n < (k + 1) >> 1; n++ ) {
	bne	a13, a6, .L33	# ivtmp$54,,
	j	.L34		#
.L4:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:99:     if( ( A_QA[ k ] > A_LIMIT ) || ( A_QA[ k ] < -A_LIMIT ) ) {
	l32i	a7, sp, 176	# %sfp,
	bltu	a7, a4, .L6	#, _593,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:104:     rc_Q31 = -silk_LSHIFT( A_QA[ 0 ], 31 - QA );
	l32i.n	a2, sp, 0	# MEM[(opus_int32 *)&Atmp_QA], MEM[(opus_int32 *)&Atmp_QA]
	slli	a2, a2, 7	# tmp467, MEM[(opus_int32 *)&Atmp_QA],
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:104:     rc_Q31 = -silk_LSHIFT( A_QA[ 0 ], 31 - QA );
	neg	a2, a2	# rc_Q31, tmp467
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:107:     rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	srai	a3, a2, 31	# tmp470, rc_Q31,
	mov.n	a4, a2	#, rc_Q31
	mov.n	a5, a3	#, tmp470
	call0	__muldi3		#
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:107:     rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	l32i	a6, sp, 180	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:111:     invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	l32i	a4, sp, 156	# %sfp,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:107:     rc_mult1_Q30 = silk_SUB32( SILK_FIX_CONST( 1, 30 ), silk_SMMUL( rc_Q31, rc_Q31 ) );
	sub	a3, a6, a3	# rc_mult1_Q30,,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:111:     invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	srai	a5, a4, 31	#,,
	mov.n	a2, a3	#, rc_mult1_Q30
	srai	a3, a3, 31	#, rc_mult1_Q30,
	call0	__muldi3		#
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:114:     if( invGain_Q30 < SILK_FIX_CONST( 1.0f / MAX_PREDICTION_POWER_GAIN, 30 ) ) {
	l32r	a4, .LC4	#, tmp481
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:111:     invGain_Q30 = silk_LSHIFT( silk_SMMUL( invGain_Q30, rc_mult1_Q30 ), 2 );
	slli	a2, a3, 2	# <retval>,,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:114:     if( invGain_Q30 < SILK_FIX_CONST( 1.0f / MAX_PREDICTION_POWER_GAIN, 30 ) ) {
	blt	a4, a2, .L1	# tmp481, <retval>,
.L6:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:115:         return 0;
	movi.n	a2, 0	# <retval>,
	j	.L1		#
.L54:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:89:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp2,
	l32i	a4, sp, 104	# %sfp,
	l32i	a5, sp, 108	# %sfp,
	mov.n	a2, a6	#, tmp1
	srai	a3, a6, 31	#, tmp1,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:88:             A_QA[ n ] = ( opus_int32 )tmp64;
	s32i.n	a7, a13, 0	# MEM[base: _758, offset: 0B], iftmp$5_135
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:89:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp2,
	call0	__muldi3		#
	slli	a4, a3, 2	# tmp487, tmp628,
	extui	a5, a2, 30, 2	# tmp629,,
	or	a5, a4, a5	# tmp629, tmp487, tmp629
	addi.n	a2, a5, 1	# tmp631, tmp629,
	srai	a3, a3, 30	# tmp630, tmp628,
	mov.n	a4, a15	# mult2Q, tmp834
	bltu	a2, a5, .L36	# tmp631, tmp629,
	movi.n	a4, 0	# mult2Q,
.L36:
	add.n	a4, a4, a3	# tmp492, mult2Q, tmp630
	slli	a4, a4, 31	# tmp493, tmp492,
	srli	a2, a2, 1	# _186, tmp631,
	or	a2, a4, a2	# _186, tmp493, _186
	sub	a3, a12, a2	# tmp642, tmp2, _186
	bgez	a3, .L37	# tmp642,
	j	.L55		#
.L53:
	l32i	a4, sp, 104	# %sfp,
	l32i	a5, sp, 108	# %sfp,
	mov.n	a2, a6	#, tmp1
	srai	a3, a6, 31	#, tmp1,
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:88:             A_QA[ n ] = ( opus_int32 )tmp64;
	s32i.n	a7, a13, 0	# MEM[base: _758, offset: 0B], tmp581
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:89:             tmp64 = silk_RSHIFT_ROUND64( silk_SMULL( silk_SUB_SAT32(tmp2,
	call0	__muldi3		#
	slli	a4, a3, 2	# tmp499, tmp636,
	extui	a5, a2, 30, 2	# tmp637,,
	or	a5, a4, a5	# tmp637, tmp499, tmp637
	addi.n	a2, a5, 1	# tmp639, tmp637,
	srai	a3, a3, 30	# tmp638, tmp636,
	mov.n	a4, a15	# mult2Q, tmp834
	bltu	a2, a5, .L39	# tmp639, tmp637,
	movi.n	a4, 0	# mult2Q,
.L39:
	add.n	a4, a4, a3	# tmp504, mult2Q, tmp638
	slli	a4, a4, 31	# tmp505, tmp504,
	srli	a2, a2, 1	# _145, tmp639,
	or	a2, a4, a2	# _145, tmp505, _145
	sub	a3, a12, a2	# tmp641, tmp2, _145
	bgez	a3, .L40	# tmp641,
	j	.L56		#
.L1:
# @OPUS@\upstream\silk\LPC_inv_pred_gain.c:141: }
	l32i	a0, sp, 220	#,
	movi	a9, 0xe0	#,
	l32i	a12, sp, 216	#,
	l32i	a13, sp, 212	#,
	l32i	a14, sp, 208	#,
	l32i	a15, sp, 204	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_LPC_inverse_pred_gain_c, .-silk_LPC_inverse_pred_gain_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
