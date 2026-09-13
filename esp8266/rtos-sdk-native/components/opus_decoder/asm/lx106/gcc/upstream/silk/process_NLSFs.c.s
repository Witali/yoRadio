# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/process_NLSFs.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"process_NLSFs.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\process_NLSFs.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\process_NLSFs.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\process_NLSFs.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\process_NLSFs.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\process_NLSFs.c.s.raw
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
	.section	.text.silk_process_NLSFs,"ax",@progbits
	.literal_position
	.literal .LC0, 59246
	.literal .LC1, 3146
	.literal .LC2, 4744
	.align	4
	.global	silk_process_NLSFs
	.type	silk_process_NLSFs, @function
# Function: silk_process_NLSFs
# Module: upstream/silk/process_NLSFs.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Limit, stabilize, convert and quantize NLSFs */
# C context: void silk_process_NLSFs(
# C context: silk_encoder_state          *psEncC,                            /* I/O  Encoder state                               */
# C context: opus_int16                  PredCoef_Q12[ 2 ][ MAX_LPC_ORDER ], /* O    Prediction coefficients                     */
# C context: opus_int16                  pNLSF_Q15[         MAX_LPC_ORDER ], /* I/O  Normalized LSFs (quant out) (0 - (2^15-1))  */
# C context: const opus_int16            prev_NLSFq_Q15[    MAX_LPC_ORDER ]  /* I    Previous Normalized LSFs (0 - (2^15-1))     */
silk_process_NLSFs:
# @OPUS@\upstream\silk\process_NLSFs.c:57:     NLSF_mu_Q20 = silk_SMLAWB( SILK_FIX_CONST( 0.003, 20 ), SILK_FIX_CONST( -0.001, 28 ), psEncC->speech_activity_Q8 );
	addmi	a7, a2, 0x1100	# tmp206, psEncC,
	l16si	a6, a7, 180	# psEncC_53(D)->speech_activity_Q8, _2
# @OPUS@\upstream\silk\process_NLSFs.c:41: {
	movi	a9, 0xa0	#,
	sub	sp, sp, a9	#,,
	s32i	a15, sp, 140	#,
# @OPUS@\upstream\silk\process_NLSFs.c:57:     NLSF_mu_Q20 = silk_SMLAWB( SILK_FIX_CONST( 0.003, 20 ), SILK_FIX_CONST( -0.001, 28 ), psEncC->speech_activity_Q8 );
	l32r	a8, .LC0	#, tmp210
# @OPUS@\upstream\silk\process_NLSFs.c:41: {
	mov.n	a15, a2	# psEncC, psEncC
# @OPUS@\upstream\silk\process_NLSFs.c:57:     NLSF_mu_Q20 = silk_SMLAWB( SILK_FIX_CONST( 0.003, 20 ), SILK_FIX_CONST( -0.001, 28 ), psEncC->speech_activity_Q8 );
	slli	a2, a6, 2	# tmp214, _2,
	neg	a2, a2	# tmp215, tmp214
	mull	a8, a6, a8	# tmp209, _2, tmp210
	sub	a2, a2, a6	# tmp216, tmp215, _2
# @OPUS@\upstream\silk\process_NLSFs.c:58:     if( psEncC->nb_subfr == 2 ) {
	l32i	a6, a7, 228	# psEncC_53(D)->nb_subfr, psEncC_53(D)->nb_subfr
# @OPUS@\upstream\silk\process_NLSFs.c:57:     NLSF_mu_Q20 = silk_SMLAWB( SILK_FIX_CONST( 0.003, 20 ), SILK_FIX_CONST( -0.001, 28 ), psEncC->speech_activity_Q8 );
	l32r	a7, .LC1	#, tmp218
# @OPUS@\upstream\silk\process_NLSFs.c:41: {
	s32i	a13, sp, 148	#,
	s32i	a14, sp, 144	#,
# @OPUS@\upstream\silk\process_NLSFs.c:57:     NLSF_mu_Q20 = silk_SMLAWB( SILK_FIX_CONST( 0.003, 20 ), SILK_FIX_CONST( -0.001, 28 ), psEncC->speech_activity_Q8 );
	srai	a8, a8, 16	# tmp211, tmp209,
# @OPUS@\upstream\silk\process_NLSFs.c:57:     NLSF_mu_Q20 = silk_SMLAWB( SILK_FIX_CONST( 0.003, 20 ), SILK_FIX_CONST( -0.001, 28 ), psEncC->speech_activity_Q8 );
	add.n	a2, a2, a7	# tmp217, tmp216, tmp218
# @OPUS@\upstream\silk\process_NLSFs.c:41: {
	s32i	a0, sp, 156	#,
	s32i	a12, sp, 152	#,
# @OPUS@\upstream\silk\process_NLSFs.c:41: {
	s32i	a5, sp, 112	# %sfp, prev_NLSFq_Q15
	mov.n	a14, a3	# PredCoef_Q12, PredCoef_Q12
	mov.n	a13, a4	# pNLSF_Q15, pNLSF_Q15
# @OPUS@\upstream\silk\process_NLSFs.c:57:     NLSF_mu_Q20 = silk_SMLAWB( SILK_FIX_CONST( 0.003, 20 ), SILK_FIX_CONST( -0.001, 28 ), psEncC->speech_activity_Q8 );
	add.n	a8, a8, a2	# NLSF_mu_Q20, tmp211, tmp217
# @OPUS@\upstream\silk\process_NLSFs.c:58:     if( psEncC->nb_subfr == 2 ) {
	bnei	a6, 2, .L2	# psEncC_53(D)->nb_subfr,,
# @OPUS@\upstream\silk\process_NLSFs.c:60:         NLSF_mu_Q20 = silk_ADD_RSHIFT( NLSF_mu_Q20, NLSF_mu_Q20, 1 );
	srai	a2, a8, 1	# _9, NLSF_mu_Q20,
# @OPUS@\upstream\silk\process_NLSFs.c:60:         NLSF_mu_Q20 = silk_ADD_RSHIFT( NLSF_mu_Q20, NLSF_mu_Q20, 1 );
	add.n	a8, a8, a2	# NLSF_mu_Q20, NLSF_mu_Q20, _9
.L2:
# @OPUS@\upstream\silk\process_NLSFs.c:67:     silk_NLSF_VQ_weights_laroia( pNLSFW_QW, pNLSF_Q15, psEncC->predictLPCOrder );
	addmi	a12, a15, 0x1200	# tmp451, psEncC,
	l32i.n	a4, a12, 32	# psEncC_53(D)->predictLPCOrder,
	addi	a2, sp, 48	#,,
	mov.n	a3, a13	#, pNLSF_Q15
	s32i	a8, sp, 116	#,
	call0	silk_NLSF_VQ_weights_laroia		#
# @OPUS@\upstream\silk\process_NLSFs.c:70:     doInterpolate = ( psEncC->useInterpolatedNLSFs == 1 ) && ( psEncC->indices.NLSFInterpCoef_Q2 < 4 );
	l32i.n	a2, a12, 24	# psEncC_53(D)->useInterpolatedNLSFs, psEncC_53(D)->useInterpolatedNLSFs
	l32i	a8, sp, 116	#,
	bnei	a2, 1, .L3	# psEncC_53(D)->useInterpolatedNLSFs,,
# @OPUS@\upstream\silk\process_NLSFs.c:70:     doInterpolate = ( psEncC->useInterpolatedNLSFs == 1 ) && ( psEncC->indices.NLSFInterpCoef_Q2 < 4 );
	l8ui	a5, a12, 159	# psEncC_53(D)->indices.NLSFInterpCoef_Q2, _12
# @OPUS@\upstream\silk\process_NLSFs.c:70:     doInterpolate = ( psEncC->useInterpolatedNLSFs == 1 ) && ( psEncC->indices.NLSFInterpCoef_Q2 < 4 );
	slli	a5, a5, 24	# tmp227, _12,
	srai	a5, a5, 24	# tmp226, tmp227,
	bgei	a5, 4, .L3	# tmp226,,
# @OPUS@\upstream\silk\process_NLSFs.c:73:         silk_interpolate( pNLSF0_temp_Q15, prev_NLSFq_Q15, pNLSF_Q15,
	l32i.n	a6, a12, 32	# psEncC_53(D)->predictLPCOrder,
	l32i	a3, sp, 112	# %sfp,
	mov.n	a4, a13	#, pNLSF_Q15
	addi	a2, sp, 80	#,,
	call0	silk_interpolate		#
# @OPUS@\upstream\silk\process_NLSFs.c:77:         silk_NLSF_VQ_weights_laroia( pNLSFW0_temp_QW, pNLSF0_temp_Q15, psEncC->predictLPCOrder );
	l32i.n	a4, a12, 32	# psEncC_53(D)->predictLPCOrder,
	addi	a2, sp, 16	#,,
	addi	a3, sp, 80	#,,
	call0	silk_NLSF_VQ_weights_laroia		#
# @OPUS@\upstream\silk\process_NLSFs.c:80:         i_sqr_Q15 = silk_LSHIFT( silk_SMULBB( psEncC->indices.NLSFInterpCoef_Q2, psEncC->indices.NLSFInterpCoef_Q2 ), 11 );
	l8ui	a2, a12, 159	# psEncC_53(D)->indices.NLSFInterpCoef_Q2, _16
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	l32i.n	a4, a12, 32	# psEncC_53(D)->predictLPCOrder, _79
# @OPUS@\upstream\silk\process_NLSFs.c:80:         i_sqr_Q15 = silk_LSHIFT( silk_SMULBB( psEncC->indices.NLSFInterpCoef_Q2, psEncC->indices.NLSFInterpCoef_Q2 ), 11 );
	mull	a2, a2, a2	# tmp241, _16, _16
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	l32i	a8, sp, 116	#,
# @OPUS@\upstream\silk\process_NLSFs.c:80:         i_sqr_Q15 = silk_LSHIFT( silk_SMULBB( psEncC->indices.NLSFInterpCoef_Q2, psEncC->indices.NLSFInterpCoef_Q2 ), 11 );
	slli	a2, a2, 27	# tmp243, tmp241,
	srai	a2, a2, 16	# i_sqr_Q15, tmp243,
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	blti	a4, 1, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 16	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 48	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp245, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp250, pNLSFW_QW,
	srai	a3, a3, 16	# tmp247, tmp245,
	srai	a5, a5, 17	# tmp251, tmp250,
	add.n	a3, a3, a5	# tmp254, tmp247, tmp251
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 48	# pNLSFW_QW, tmp254
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 1, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 18	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 50	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp255, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp260, pNLSFW_QW,
	srai	a3, a3, 16	# tmp257, tmp255,
	srai	a5, a5, 17	# tmp261, tmp260,
	add.n	a3, a3, a5	# tmp264, tmp257, tmp261
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 50	# pNLSFW_QW, tmp264
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 2, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 20	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 52	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp265, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp270, pNLSFW_QW,
	srai	a3, a3, 16	# tmp267, tmp265,
	srai	a5, a5, 17	# tmp271, tmp270,
	add.n	a3, a3, a5	# tmp274, tmp267, tmp271
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 52	# pNLSFW_QW, tmp274
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 3, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 22	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 54	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp275, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp280, pNLSFW_QW,
	srai	a3, a3, 16	# tmp277, tmp275,
	srai	a5, a5, 17	# tmp281, tmp280,
	add.n	a3, a3, a5	# tmp284, tmp277, tmp281
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 54	# pNLSFW_QW, tmp284
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 4, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 24	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 56	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp285, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp290, pNLSFW_QW,
	srai	a3, a3, 16	# tmp287, tmp285,
	srai	a5, a5, 17	# tmp291, tmp290,
	add.n	a3, a3, a5	# tmp294, tmp287, tmp291
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 56	# pNLSFW_QW, tmp294
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 5, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 26	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 58	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp295, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp300, pNLSFW_QW,
	srai	a3, a3, 16	# tmp297, tmp295,
	srai	a5, a5, 17	# tmp301, tmp300,
	add.n	a3, a3, a5	# tmp304, tmp297, tmp301
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 58	# pNLSFW_QW, tmp304
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 6, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 28	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 60	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp305, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp310, pNLSFW_QW,
	srai	a3, a3, 16	# tmp307, tmp305,
	srai	a5, a5, 17	# tmp311, tmp310,
	add.n	a3, a3, a5	# tmp314, tmp307, tmp311
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 60	# pNLSFW_QW, tmp314
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 7, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 30	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 62	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp315, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp320, pNLSFW_QW,
	srai	a3, a3, 16	# tmp317, tmp315,
	srai	a5, a5, 17	# tmp321, tmp320,
	add.n	a3, a3, a5	# tmp324, tmp317, tmp321
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 62	# pNLSFW_QW, tmp324
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 8, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 32	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 64	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp325, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp330, pNLSFW_QW,
	srai	a3, a3, 16	# tmp327, tmp325,
	srai	a5, a5, 17	# tmp331, tmp330,
	add.n	a3, a3, a5	# tmp334, tmp327, tmp331
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 64	# pNLSFW_QW, tmp334
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	movi.n	a3, 9	# tmp335,
	beq	a4, a3, .L4	# _79, tmp335,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 34	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 66	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp336, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp341, pNLSFW_QW,
	srai	a3, a3, 16	# tmp338, tmp336,
	srai	a5, a5, 17	# tmp342, tmp341,
	add.n	a3, a3, a5	# tmp345, tmp338, tmp342
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 66	# pNLSFW_QW, tmp345
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 10, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 36	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 68	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp346, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp351, pNLSFW_QW,
	srai	a3, a3, 16	# tmp348, tmp346,
	srai	a5, a5, 17	# tmp352, tmp351,
	add.n	a3, a3, a5	# tmp355, tmp348, tmp352
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 68	# pNLSFW_QW, tmp355
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	movi.n	a3, 0xb	# tmp356,
	beq	a4, a3, .L4	# _79, tmp356,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 38	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 70	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp357, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp362, pNLSFW_QW,
	srai	a3, a3, 16	# tmp359, tmp357,
	srai	a5, a5, 17	# tmp363, tmp362,
	add.n	a3, a3, a5	# tmp366, tmp359, tmp363
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 70	# pNLSFW_QW, tmp366
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	beqi	a4, 12, .L4	# _79,,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 40	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 72	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp367, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp372, pNLSFW_QW,
	srai	a3, a3, 16	# tmp369, tmp367,
	srai	a5, a5, 17	# tmp373, tmp372,
	add.n	a3, a3, a5	# tmp376, tmp369, tmp373
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 72	# pNLSFW_QW, tmp376
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	movi.n	a3, 0xd	# tmp377,
	beq	a4, a3, .L4	# _79, tmp377,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 42	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 74	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp378, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp383, pNLSFW_QW,
	srai	a3, a3, 16	# tmp380, tmp378,
	srai	a5, a5, 17	# tmp384, tmp383,
	add.n	a3, a3, a5	# tmp387, tmp380, tmp384
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 74	# pNLSFW_QW, tmp387
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	movi.n	a3, 0xe	# tmp388,
	beq	a4, a3, .L4	# _79, tmp388,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 44	# pNLSFW0_temp_QW,
	l16ui	a5, sp, 76	# pNLSFW_QW,
	mul16s	a3, a3, a2	# tmp389, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a5, a5, 16	# tmp394, pNLSFW_QW,
	srai	a3, a3, 16	# tmp391, tmp389,
	srai	a5, a5, 17	# tmp395, tmp394,
	add.n	a3, a3, a5	# tmp398, tmp391, tmp395
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a3, sp, 76	# pNLSFW_QW, tmp398
# @OPUS@\upstream\silk\process_NLSFs.c:81:         for( i = 0; i < psEncC->predictLPCOrder; i++ ) {
	movi.n	a3, 0xf	# tmp399,
	beq	a4, a3, .L4	# _79, tmp399,
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	l16ui	a3, sp, 46	# pNLSFW0_temp_QW,
	l16ui	a4, sp, 78	# pNLSFW_QW,
	mul16s	a2, a3, a2	# tmp400, pNLSFW0_temp_QW, i_sqr_Q15
	slli	a3, a4, 16	# tmp405, pNLSFW_QW,
	srai	a2, a2, 16	# tmp402, tmp400,
	srai	a3, a3, 17	# tmp406, tmp405,
	add.n	a2, a2, a3	# tmp409, tmp402, tmp406
# @OPUS@\upstream\silk\process_NLSFs.c:82:             pNLSFW_QW[ i ] = silk_ADD16( silk_RSHIFT( pNLSFW_QW[ i ], 1 ), silk_RSHIFT(
	s16i	a2, sp, 78	# pNLSFW_QW, tmp409
.L4:
# @OPUS@\upstream\silk\process_NLSFs.c:88:     silk_NLSF_encode( psEncC->indices.NLSFIndices, pNLSF_Q15, psEncC->psNLSF_CB, pNLSFW_QW,
	l8ui	a2, a12, 157	# psEncC_53(D)->indices.signalType,
	l32i.n	a7, a12, 52	# psEncC_53(D)->NLSF_MSVQ_Survivors,
	slli	a2, a2, 24	# tmp418, psEncC_53(D)->indices.signalType,
	srai	a2, a2, 24	# tmp416, tmp418,
	l32i	a4, a12, 84	# psEncC_53(D)->psNLSF_CB,
	s32i.n	a2, sp, 0	#, tmp416
	l32r	a2, .LC2	#, tmp414
	mov.n	a6, a8	#, NLSF_mu_Q20
	addi	a5, sp, 48	#,,
	mov.n	a3, a13	#, pNLSF_Q15
	add.n	a2, a15, a2	#, psEncC, tmp414
	call0	silk_NLSF_encode		#
# @OPUS@\upstream\silk\process_NLSFs.c:92:     silk_NLSF2A( PredCoef_Q12[ 1 ], pNLSF_Q15, psEncC->predictLPCOrder, psEncC->arch );
	addmi	a15, a15, 0x1300	# tmp419, psEncC,
	l32i	a5, a15, 228	# psEncC_53(D)->arch,
	l32i.n	a4, a12, 32	# psEncC_53(D)->predictLPCOrder,
	mov.n	a3, a13	#, pNLSF_Q15
	addi	a2, a14, 32	#, PredCoef_Q12,
	call0	silk_NLSF2A		#
# @OPUS@\upstream\silk\process_NLSFs.c:96:         silk_interpolate( pNLSF0_temp_Q15, prev_NLSFq_Q15, pNLSF_Q15,
	l8ui	a5, a12, 159	# psEncC_53(D)->indices.NLSFInterpCoef_Q2,
	l32i	a3, sp, 112	# %sfp,
	l32i.n	a6, a12, 32	# psEncC_53(D)->predictLPCOrder,
	slli	a5, a5, 24	# tmp426, psEncC_53(D)->indices.NLSFInterpCoef_Q2,
	mov.n	a4, a13	#, pNLSF_Q15
	addi	a2, sp, 80	#,,
	srai	a5, a5, 24	#, tmp426,
	call0	silk_interpolate		#
# @OPUS@\upstream\silk\process_NLSFs.c:100:         silk_NLSF2A( PredCoef_Q12[ 0 ], pNLSF0_temp_Q15, psEncC->predictLPCOrder, psEncC->arch );
	l32i	a5, a15, 228	# psEncC_53(D)->arch,
	l32i.n	a4, a12, 32	# psEncC_53(D)->predictLPCOrder,
	addi	a3, sp, 80	#,,
	mov.n	a2, a14	#, PredCoef_Q12
	call0	silk_NLSF2A		#
	j	.L1		#
.L3:
# @OPUS@\upstream\silk\process_NLSFs.c:88:     silk_NLSF_encode( psEncC->indices.NLSFIndices, pNLSF_Q15, psEncC->psNLSF_CB, pNLSFW_QW,
	l8ui	a2, a12, 157	# psEncC_53(D)->indices.signalType,
	l32i.n	a7, a12, 52	# psEncC_53(D)->NLSF_MSVQ_Survivors,
	slli	a2, a2, 24	# tmp439, psEncC_53(D)->indices.signalType,
	srai	a2, a2, 24	# tmp437, tmp439,
	l32i	a4, a12, 84	# psEncC_53(D)->psNLSF_CB,
	s32i.n	a2, sp, 0	#, tmp437
	l32r	a2, .LC2	#, tmp435
	mov.n	a6, a8	#, NLSF_mu_Q20
	addi	a5, sp, 48	#,,
	mov.n	a3, a13	#, pNLSF_Q15
	add.n	a2, a15, a2	#, psEncC, tmp435
	call0	silk_NLSF_encode		#
# @OPUS@\upstream\silk\process_NLSFs.c:92:     silk_NLSF2A( PredCoef_Q12[ 1 ], pNLSF_Q15, psEncC->predictLPCOrder, psEncC->arch );
	addmi	a9, a15, 0x1300	# tmp440, psEncC,
	l32i.n	a4, a12, 32	# psEncC_53(D)->predictLPCOrder,
# @OPUS@\upstream\silk\process_NLSFs.c:92:     silk_NLSF2A( PredCoef_Q12[ 1 ], pNLSF_Q15, psEncC->predictLPCOrder, psEncC->arch );
	addi	a15, a14, 32	# _98, PredCoef_Q12,
# @OPUS@\upstream\silk\process_NLSFs.c:92:     silk_NLSF2A( PredCoef_Q12[ 1 ], pNLSF_Q15, psEncC->predictLPCOrder, psEncC->arch );
	l32i	a5, a9, 228	# psEncC_53(D)->arch,
	mov.n	a3, a13	#, pNLSF_Q15
	mov.n	a2, a15	#, _98
	call0	silk_NLSF2A		#
# @OPUS@\upstream\silk\process_NLSFs.c:105:         silk_memcpy( PredCoef_Q12[ 0 ], PredCoef_Q12[ 1 ], psEncC->predictLPCOrder * sizeof( opus_int16 ) );
	l32i.n	a4, a12, 32	# psEncC_53(D)->predictLPCOrder, psEncC_53(D)->predictLPCOrder
	mov.n	a3, a15	#, _98
	slli	a4, a4, 1	#, psEncC_53(D)->predictLPCOrder,
	mov.n	a2, a14	#, PredCoef_Q12
	call0	memcpy		#
.L1:
# @OPUS@\upstream\silk\process_NLSFs.c:107: }
	l32i	a0, sp, 156	#,
	movi	a9, 0xa0	#,
	l32i	a12, sp, 152	#,
	l32i	a13, sp, 148	#,
	l32i	a14, sp, 144	#,
	l32i	a15, sp, 140	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_process_NLSFs, .-silk_process_NLSFs
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
