# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/decode_indices.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"decode_indices.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\decode_indices.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\decode_indices.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\decode_indices.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\decode_indices.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\decode_indices.c.s.raw
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
	.section	.text.silk_decode_indices,"ax",@progbits
	.literal_position
	.literal .LC0, silk_type_offset_VAD_iCDF
	.literal .LC1, silk_type_offset_no_VAD_iCDF
	.literal .LC2, silk_delta_gain_iCDF
	.literal .LC3, silk_gain_iCDF
	.literal .LC4, silk_uniform8_iCDF
	.literal .LC5, silk_NLSF_EXT_iCDF
	.literal .LC6, silk_NLSF_interpolation_factor_iCDF
	.literal .LC7, silk_pitch_delta_iCDF
	.literal .LC8, silk_pitch_lag_iCDF
	.literal .LC9, silk_LTP_per_index_iCDF
	.literal .LC10, silk_LTP_gain_iCDF_ptrs
	.literal .LC11, silk_LTPscale_iCDF
	.literal .LC12, silk_uniform4_iCDF
	.align	4
	.global	silk_decode_indices
	.type	silk_decode_indices, @function
# Function: silk_decode_indices
# Module: upstream/silk/decode_indices.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Decode side-information parameters from payload */
# C context: void silk_decode_indices(
# C context: silk_decoder_state          *psDec,                         /* I/O  State                                       */
# C context: ec_dec                      *psRangeDec,                    /* I/O  Compressor data structure                   */
# C context: opus_int                    FrameIndex,                     /* I    Frame number                                */
# C context: opus_int                    decode_LBRR,                    /* I    Flag indicating LBRR data is being decoded  */
silk_decode_indices:
	addi	sp, sp, -96	#,,
	s32i	a13, sp, 84	#,
	s32i	a0, sp, 92	#,
	s32i	a12, sp, 88	#,
	s32i	a14, sp, 80	#,
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\silk\decode_indices.c:42: {
	s32i.n	a2, sp, 48	# %sfp, psDec
	s32i.n	a6, sp, 56	# %sfp, condCoding
	mov.n	a13, a3	# psRangeDec, psRangeDec
# @OPUS@\upstream\silk\decode_indices.c:51:     if( decode_LBRR || psDec->VAD_flags[ FrameIndex ] ) {
	bnez.n	a5, .L2	# decode_LBRR,
# @OPUS@\upstream\silk\decode_indices.c:51:     if( decode_LBRR || psDec->VAD_flags[ FrameIndex ] ) {
	movi	a2, 0x118	# tmp150,
	add.n	a4, a4, a2	# tmp151, FrameIndex, tmp150
	l32i.n	a2, sp, 48	# %sfp,
	slli	a4, a4, 2	# tmp152, tmp151,
	add.n	a4, a2, a4	# tmp153,, tmp152
# @OPUS@\upstream\silk\decode_indices.c:51:     if( decode_LBRR || psDec->VAD_flags[ FrameIndex ] ) {
	l32i.n	a2, a4, 8	# psDec_99(D)->VAD_flags, tmp155
	beqz.n	a2, .L3	# tmp155,
.L2:
# @OPUS@\upstream\silk\decode_indices.c:52:         Ix = ec_dec_icdf( psRangeDec, silk_type_offset_VAD_iCDF, 8 ) + 2;
	l32r	a3, .LC0	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:52:         Ix = ec_dec_icdf( psRangeDec, silk_type_offset_VAD_iCDF, 8 ) + 2;
	addi.n	a2, a2, 2	# Ix,,
	j	.L4		#
.L3:
# @OPUS@\upstream\silk\decode_indices.c:54:         Ix = ec_dec_icdf( psRangeDec, silk_type_offset_no_VAD_iCDF, 8 );
	l32r	a3, .LC1	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
.L4:
# @OPUS@\upstream\silk\decode_indices.c:56:     psDec->indices.signalType      = (opus_int8)silk_RSHIFT( Ix, 1 );
	l32i.n	a3, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_indices.c:63:     if( condCoding == CODE_CONDITIONALLY ) {
	l32i.n	a4, sp, 56	# %sfp,
# @OPUS@\upstream\silk\decode_indices.c:56:     psDec->indices.signalType      = (opus_int8)silk_RSHIFT( Ix, 1 );
	addmi	a12, a3, 0x500	# tmp294,,
# @OPUS@\upstream\silk\decode_indices.c:56:     psDec->indices.signalType      = (opus_int8)silk_RSHIFT( Ix, 1 );
	extui	a3, a2, 1, 8	# _4, Ix,,
# @OPUS@\upstream\silk\decode_indices.c:57:     psDec->indices.quantOffsetType = (opus_int8)( Ix & 1 );
	extui	a2, a2, 0, 1	# tmp162, Ix,
# @OPUS@\upstream\silk\decode_indices.c:56:     psDec->indices.signalType      = (opus_int8)silk_RSHIFT( Ix, 1 );
	s8i	a3, a12, 209	# psDec_99(D)->indices.signalType, _4
# @OPUS@\upstream\silk\decode_indices.c:57:     psDec->indices.quantOffsetType = (opus_int8)( Ix & 1 );
	s8i	a2, a12, 210	# psDec_99(D)->indices.quantOffsetType, tmp162
# @OPUS@\upstream\silk\decode_indices.c:63:     if( condCoding == CODE_CONDITIONALLY ) {
	bnei	a4, 2, .L5	#,,
# @OPUS@\upstream\silk\decode_indices.c:65:         psDec->indices.GainsIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_delta_gain_iCDF, 8 );
	l32r	a3, .LC2	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:65:         psDec->indices.GainsIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_delta_gain_iCDF, 8 );
	s8i	a2, a12, 180	# psDec_99(D)->indices.GainsIndices,
.L9:
# @OPUS@\upstream\silk\decode_indices.c:73:     for( i = 1; i < psDec->nb_subfr; i++ ) {
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_indices.c:73:     for( i = 1; i < psDec->nb_subfr; i++ ) {
	movi.n	a14, 1	# i,
# @OPUS@\upstream\silk\decode_indices.c:73:     for( i = 1; i < psDec->nb_subfr; i++ ) {
	addmi	a15, a2, 0x400	# tmp291,,
# @OPUS@\upstream\silk\decode_indices.c:73:     for( i = 1; i < psDec->nb_subfr; i++ ) {
	l32i.n	a2, a15, 24	# psDec_99(D)->nb_subfr, psDec_99(D)->nb_subfr
	bgei	a2, 2, .L6	# psDec_99(D)->nb_subfr,,
.L10:
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	l32i	a4, a12, 176	# psDec_99(D)->psNLSF_CB, _21
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	l8ui	a2, a12, 209	# psDec_99(D)->indices.signalType,
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	l16ui	a3, a4, 0	# _21->nVectors,
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	slli	a2, a2, 24	# tmp171, psDec_99(D)->indices.signalType,
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	srai	a2, a2, 25	# tmp174, tmp171,
	mul16s	a2, a2, a3	# tmp176, tmp174, _21->nVectors
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	l32i.n	a3, a4, 16	# _21->CB1_iCDF, _21->CB1_iCDF
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, _21->CB1_iCDF, tmp176
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	extui	a2, a2, 0, 8	# _32,
# @OPUS@\upstream\silk\decode_indices.c:81:     silk_NLSF_unpack( ec_ix, pred_Q8, psDec->psNLSF_CB, psDec->indices.NLSFIndices[ 0 ] );
	slli	a5, a2, 24	# tmp182, _32,
	l32i	a4, a12, 176	# psDec_99(D)->psNLSF_CB,
# @OPUS@\upstream\silk\decode_indices.c:80:     psDec->indices.NLSFIndices[ 0 ] = (opus_int8)ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->CB1_iCDF[ ( psDec->indices.signalType >> 1 ) * psDec->psNLSF_CB->nVectors ], 8 );
	s8i	a2, a12, 188	# psDec_99(D)->indices.NLSFIndices, _32
# @OPUS@\upstream\silk\decode_indices.c:81:     silk_NLSF_unpack( ec_ix, pred_Q8, psDec->psNLSF_CB, psDec->indices.NLSFIndices[ 0 ] );
	addi	a3, sp, 32	#,,
	mov.n	a2, sp	#,
	srai	a5, a5, 24	#, tmp182,
	call0	silk_NLSF_unpack		#
# @OPUS@\upstream\silk\decode_indices.c:83:     for( i = 0; i < psDec->psNLSF_CB->order; i++ ) {
	l32i	a3, a12, 176	# psDec_99(D)->psNLSF_CB, _42
# @OPUS@\upstream\silk\decode_indices.c:86:             Ix -= ec_dec_icdf( psRangeDec, silk_NLSF_EXT_iCDF, 8 );
	l32r	a4, .LC5	#,
# @OPUS@\upstream\silk\decode_indices.c:83:     for( i = 0; i < psDec->psNLSF_CB->order; i++ ) {
	l16si	a2, a3, 2	# _180->order, tmp186
# @OPUS@\upstream\silk\decode_indices.c:86:             Ix -= ec_dec_icdf( psRangeDec, silk_NLSF_EXT_iCDF, 8 );
	s32i.n	a4, sp, 52	# %sfp,
# @OPUS@\upstream\silk\decode_indices.c:83:     for( i = 0; i < psDec->psNLSF_CB->order; i++ ) {
	movi.n	a14, 0	# i,
# @OPUS@\upstream\silk\decode_indices.c:83:     for( i = 0; i < psDec->psNLSF_CB->order; i++ ) {
	bgei	a2, 1, .L7	# tmp186,,
	j	.L8		#
.L5:
# @OPUS@\upstream\silk\decode_indices.c:68:         psDec->indices.GainsIndices[ 0 ]  = (opus_int8)silk_LSHIFT( ec_dec_icdf( psRangeDec, silk_gain_iCDF[ psDec->indices.signalType ], 8 ), 3 );
	l32r	a2, .LC3	#, tmp196
	slli	a3, a3, 24	# tmp191, _4,
	srai	a3, a3, 21	# tmp194, tmp191,
	add.n	a3, a2, a3	#, tmp196, tmp194
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
	slli	a2, a2, 3	# tmp198,,
# @OPUS@\upstream\silk\decode_indices.c:69:         psDec->indices.GainsIndices[ 0 ] += (opus_int8)ec_dec_icdf( psRangeDec, silk_uniform8_iCDF, 8 );
	l32r	a3, .LC4	#,
# @OPUS@\upstream\silk\decode_indices.c:68:         psDec->indices.GainsIndices[ 0 ]  = (opus_int8)silk_LSHIFT( ec_dec_icdf( psRangeDec, silk_gain_iCDF[ psDec->indices.signalType ], 8 ), 3 );
	s8i	a2, a12, 180	# psDec_99(D)->indices.GainsIndices, tmp198
# @OPUS@\upstream\silk\decode_indices.c:69:         psDec->indices.GainsIndices[ 0 ] += (opus_int8)ec_dec_icdf( psRangeDec, silk_uniform8_iCDF, 8 );
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:69:         psDec->indices.GainsIndices[ 0 ] += (opus_int8)ec_dec_icdf( psRangeDec, silk_uniform8_iCDF, 8 );
	l8ui	a3, a12, 180	# psDec_99(D)->indices.GainsIndices,
	add.n	a2, a2, a3	# tmp204,, psDec_99(D)->indices.GainsIndices
	s8i	a2, a12, 180	# psDec_99(D)->indices.GainsIndices, tmp204
	j	.L9		#
.L6:
# @OPUS@\upstream\silk\decode_indices.c:74:         psDec->indices.GainsIndices[ i ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_delta_gain_iCDF, 8 );
	l32r	a3, .LC2	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:74:         psDec->indices.GainsIndices[ i ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_delta_gain_iCDF, 8 );
	movi	a4, 0x5b4	#,
	add.n	a3, a14, a4	# tmp207, i,
	l32i.n	a4, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_indices.c:73:     for( i = 1; i < psDec->nb_subfr; i++ ) {
	addi.n	a14, a14, 1	# i, i,
# @OPUS@\upstream\silk\decode_indices.c:74:         psDec->indices.GainsIndices[ i ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_delta_gain_iCDF, 8 );
	add.n	a3, a4, a3	# tmp208,, tmp207
# @OPUS@\upstream\silk\decode_indices.c:74:         psDec->indices.GainsIndices[ i ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_delta_gain_iCDF, 8 );
	s8i	a2, a3, 0	# MEM[base: _216, offset: 0B],
# @OPUS@\upstream\silk\decode_indices.c:73:     for( i = 1; i < psDec->nb_subfr; i++ ) {
	l32i.n	a2, a15, 24	# psDec_99(D)->nb_subfr, psDec_99(D)->nb_subfr
	blt	a14, a2, .L6	# i, psDec_99(D)->nb_subfr,
	j	.L10		#
.L8:
# @OPUS@\upstream\silk\decode_indices.c:94:     if( psDec->nb_subfr == MAX_NB_SUBFR ) {
	l32i.n	a2, a15, 24	# psDec_99(D)->nb_subfr, psDec_99(D)->nb_subfr
	bnei	a2, 4, .L28	# psDec_99(D)->nb_subfr,,
	j	.L11		#
.L7:
# @OPUS@\upstream\silk\decode_indices.c:84:         Ix = ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	slli	a2, a14, 1	# tmp213, i,
	add.n	a2, sp, a2	# tmp214,, tmp213
	l16si	a2, a2, 0	# MEM[base: _226, offset: 0B], tmp215
# @OPUS@\upstream\silk\decode_indices.c:84:         Ix = ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	l32i.n	a3, a3, 28	# _161->ec_iCDF, _161->ec_iCDF
# @OPUS@\upstream\silk\decode_indices.c:84:         Ix = ec_dec_icdf( psRangeDec, &psDec->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, _161->ec_iCDF, tmp215
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:85:         if( Ix == 0 ) {
	bnez.n	a2, .L13	# Ix,
# @OPUS@\upstream\silk\decode_indices.c:86:             Ix -= ec_dec_icdf( psRangeDec, silk_NLSF_EXT_iCDF, 8 );
	l32i.n	a3, sp, 52	# %sfp,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:86:             Ix -= ec_dec_icdf( psRangeDec, silk_NLSF_EXT_iCDF, 8 );
	neg	a2, a2	# Ix,
	j	.L14		#
.L13:
# @OPUS@\upstream\silk\decode_indices.c:87:         } else if( Ix == 2 * NLSF_QUANT_MAX_AMPLITUDE ) {
	bnei	a2, 8, .L14	# Ix,,
# @OPUS@\upstream\silk\decode_indices.c:88:             Ix += ec_dec_icdf( psRangeDec, silk_NLSF_EXT_iCDF, 8 );
	l32r	a3, .LC5	#,
	mov.n	a4, a2	#, Ix
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:88:             Ix += ec_dec_icdf( psRangeDec, silk_NLSF_EXT_iCDF, 8 );
	addi.n	a2, a2, 8	# Ix,,
.L14:
# @OPUS@\upstream\silk\decode_indices.c:90:         psDec->indices.NLSFIndices[ i+1 ] = (opus_int8)( Ix - NLSF_QUANT_MAX_AMPLITUDE );
	movi	a3, 0x5bd	# tmp222,
	l32i.n	a4, sp, 48	# %sfp,
	add.n	a3, a14, a3	# tmp223, i, tmp222
	add.n	a3, a4, a3	# tmp224,, tmp223
# @OPUS@\upstream\silk\decode_indices.c:90:         psDec->indices.NLSFIndices[ i+1 ] = (opus_int8)( Ix - NLSF_QUANT_MAX_AMPLITUDE );
	addi	a2, a2, -4	# tmp226, Ix,
# @OPUS@\upstream\silk\decode_indices.c:90:         psDec->indices.NLSFIndices[ i+1 ] = (opus_int8)( Ix - NLSF_QUANT_MAX_AMPLITUDE );
	s8i	a2, a3, 0	# MEM[base: _220, offset: 0B], tmp226
# @OPUS@\upstream\silk\decode_indices.c:83:     for( i = 0; i < psDec->psNLSF_CB->order; i++ ) {
	l32i	a3, a12, 176	# psDec_99(D)->psNLSF_CB, _42
	addi.n	a14, a14, 1	# i, i,
# @OPUS@\upstream\silk\decode_indices.c:83:     for( i = 0; i < psDec->psNLSF_CB->order; i++ ) {
	l16si	a2, a3, 2	# _42->order, tmp228
# @OPUS@\upstream\silk\decode_indices.c:83:     for( i = 0; i < psDec->psNLSF_CB->order; i++ ) {
	blt	a14, a2, .L7	# i, tmp228,
	j	.L8		#
.L11:
# @OPUS@\upstream\silk\decode_indices.c:95:         psDec->indices.NLSFInterpCoef_Q2 = (opus_int8)ec_dec_icdf( psRangeDec, silk_NLSF_interpolation_factor_iCDF, 8 );
	l32r	a3, .LC6	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:95:         psDec->indices.NLSFInterpCoef_Q2 = (opus_int8)ec_dec_icdf( psRangeDec, silk_NLSF_interpolation_factor_iCDF, 8 );
	s8i	a2, a12, 211	# psDec_99(D)->indices.NLSFInterpCoef_Q2,
	j	.L15		#
.L28:
# @OPUS@\upstream\silk\decode_indices.c:97:         psDec->indices.NLSFInterpCoef_Q2 = 4;
	movi.n	a2, 4	# tmp234,
	s8i	a2, a12, 211	# psDec_99(D)->indices.NLSFInterpCoef_Q2, tmp234
.L15:
# @OPUS@\upstream\silk\decode_indices.c:100:     if( psDec->indices.signalType == TYPE_VOICED )
	l8ui	a3, a12, 209	# psDec_99(D)->indices.signalType, _48
# @OPUS@\upstream\silk\decode_indices.c:100:     if( psDec->indices.signalType == TYPE_VOICED )
	slli	a2, a3, 24	# tmp293, _48,
	bnei	a3, 2, .L16	# _48,,
# @OPUS@\upstream\silk\decode_indices.c:107:         if( condCoding == CODE_CONDITIONALLY && psDec->ec_prevSignalType == TYPE_VOICED ) {
	l32i.n	a2, sp, 56	# %sfp,
	bnei	a2, 2, .L17	#,,
# @OPUS@\upstream\silk\decode_indices.c:107:         if( condCoding == CODE_CONDITIONALLY && psDec->ec_prevSignalType == TYPE_VOICED ) {
	l32i	a2, a15, 96	# psDec_99(D)->ec_prevSignalType, psDec_99(D)->ec_prevSignalType
	bnei	a2, 2, .L17	# psDec_99(D)->ec_prevSignalType,,
# @OPUS@\upstream\silk\decode_indices.c:109:             delta_lagIndex = (opus_int16)ec_dec_icdf( psRangeDec, silk_pitch_delta_iCDF, 8 );
	l32r	a3, .LC7	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:109:             delta_lagIndex = (opus_int16)ec_dec_icdf( psRangeDec, silk_pitch_delta_iCDF, 8 );
	slli	a2, a2, 16	# tmp241,,
	srai	a2, a2, 16	# _51, tmp241,
# @OPUS@\upstream\silk\decode_indices.c:110:             if( delta_lagIndex > 0 ) {
	blti	a2, 1, .L17	# _51,,
# @OPUS@\upstream\silk\decode_indices.c:112:                 psDec->indices.lagIndex = (opus_int16)( psDec->ec_prevLagIndex + delta_lagIndex );
	l16ui	a3, a15, 100	# psDec_99(D)->ec_prevLagIndex,
	addi	a3, a3, -9	# tmp244, psDec_99(D)->ec_prevLagIndex,
	add.n	a2, a2, a3	# tmp246, _51, tmp244
	slli	a2, a2, 16	# tmp247, tmp246,
	srai	a2, a2, 16	# _64, tmp247,
# @OPUS@\upstream\silk\decode_indices.c:112:                 psDec->indices.lagIndex = (opus_int16)( psDec->ec_prevLagIndex + delta_lagIndex );
	s16i	a2, a12, 206	# psDec_99(D)->indices.lagIndex, _64
	j	.L18		#
.L17:
# @OPUS@\upstream\silk\decode_indices.c:118:             psDec->indices.lagIndex  = (opus_int16)ec_dec_icdf( psRangeDec, silk_pitch_lag_iCDF, 8 ) * silk_RSHIFT( psDec->fs_kHz, 1 );
	l32r	a3, .LC8	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:118:             psDec->indices.lagIndex  = (opus_int16)ec_dec_icdf( psRangeDec, silk_pitch_lag_iCDF, 8 ) * silk_RSHIFT( psDec->fs_kHz, 1 );
	l32i.n	a4, a15, 16	# psDec_99(D)->fs_kHz, psDec_99(D)->fs_kHz
# @OPUS@\upstream\silk\decode_indices.c:119:             psDec->indices.lagIndex += (opus_int16)ec_dec_icdf( psRangeDec, psDec->pitch_lag_low_bits_iCDF, 8 );
	l32i	a3, a15, 80	# psDec_99(D)->pitch_lag_low_bits_iCDF,
# @OPUS@\upstream\silk\decode_indices.c:118:             psDec->indices.lagIndex  = (opus_int16)ec_dec_icdf( psRangeDec, silk_pitch_lag_iCDF, 8 ) * silk_RSHIFT( psDec->fs_kHz, 1 );
	srai	a4, a4, 1	# tmp252, psDec_99(D)->fs_kHz,
# @OPUS@\upstream\silk\decode_indices.c:118:             psDec->indices.lagIndex  = (opus_int16)ec_dec_icdf( psRangeDec, silk_pitch_lag_iCDF, 8 ) * silk_RSHIFT( psDec->fs_kHz, 1 );
	mul16s	a2, a4, a2	# tmp254, tmp252,
# @OPUS@\upstream\silk\decode_indices.c:119:             psDec->indices.lagIndex += (opus_int16)ec_dec_icdf( psRangeDec, psDec->pitch_lag_low_bits_iCDF, 8 );
	movi.n	a4, 8	#,
# @OPUS@\upstream\silk\decode_indices.c:118:             psDec->indices.lagIndex  = (opus_int16)ec_dec_icdf( psRangeDec, silk_pitch_lag_iCDF, 8 ) * silk_RSHIFT( psDec->fs_kHz, 1 );
	s16i	a2, a12, 206	# psDec_99(D)->indices.lagIndex, tmp254
# @OPUS@\upstream\silk\decode_indices.c:119:             psDec->indices.lagIndex += (opus_int16)ec_dec_icdf( psRangeDec, psDec->pitch_lag_low_bits_iCDF, 8 );
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:119:             psDec->indices.lagIndex += (opus_int16)ec_dec_icdf( psRangeDec, psDec->pitch_lag_low_bits_iCDF, 8 );
	l16ui	a3, a12, 206	# psDec_99(D)->indices.lagIndex,
	add.n	a2, a2, a3	# tmp259,, psDec_99(D)->indices.lagIndex
	slli	a2, a2, 16	# tmp260, tmp259,
	srai	a2, a2, 16	# _64, tmp260,
	s16i	a2, a12, 206	# psDec_99(D)->indices.lagIndex, _64
.L18:
# @OPUS@\upstream\silk\decode_indices.c:124:         psDec->indices.contourIndex = (opus_int8)ec_dec_icdf( psRangeDec, psDec->pitch_contour_iCDF, 8 );
	l32i	a3, a15, 84	# psDec_99(D)->pitch_contour_iCDF,
	movi.n	a4, 8	#,
# @OPUS@\upstream\silk\decode_indices.c:121:         psDec->ec_prevLagIndex = psDec->indices.lagIndex;
	s16i	a2, a15, 100	# psDec_99(D)->ec_prevLagIndex, _64
# @OPUS@\upstream\silk\decode_indices.c:124:         psDec->indices.contourIndex = (opus_int8)ec_dec_icdf( psRangeDec, psDec->pitch_contour_iCDF, 8 );
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:130:         psDec->indices.PERIndex = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_per_index_iCDF, 8 );
	l32r	a3, .LC9	#,
# @OPUS@\upstream\silk\decode_indices.c:124:         psDec->indices.contourIndex = (opus_int8)ec_dec_icdf( psRangeDec, psDec->pitch_contour_iCDF, 8 );
	s8i	a2, a12, 208	# psDec_99(D)->indices.contourIndex,
# @OPUS@\upstream\silk\decode_indices.c:130:         psDec->indices.PERIndex = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_per_index_iCDF, 8 );
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:130:         psDec->indices.PERIndex = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_per_index_iCDF, 8 );
	extui	a2, a2, 0, 8	# pretmp_232,
# @OPUS@\upstream\silk\decode_indices.c:130:         psDec->indices.PERIndex = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_per_index_iCDF, 8 );
	s8i	a2, a12, 212	# psDec_99(D)->indices.PERIndex, pretmp_232
# @OPUS@\upstream\silk\decode_indices.c:132:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i.n	a3, a15, 24	# psDec_99(D)->nb_subfr, psDec_99(D)->nb_subfr
	blti	a3, 1, .L19	# psDec_99(D)->nb_subfr,,
# @OPUS@\upstream\silk\decode_indices.c:132:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	movi.n	a5, 0	# k,
.L20:
# @OPUS@\upstream\silk\decode_indices.c:133:             psDec->indices.LTPIndex[ k ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_gain_iCDF_ptrs[ psDec->indices.PERIndex ], 8 );
	l32r	a3, .LC10	#,
# @OPUS@\upstream\silk\decode_indices.c:133:             psDec->indices.LTPIndex[ k ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_gain_iCDF_ptrs[ psDec->indices.PERIndex ], 8 );
	slli	a2, a2, 24	# tmp271, pretmp_232,
# @OPUS@\upstream\silk\decode_indices.c:133:             psDec->indices.LTPIndex[ k ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_gain_iCDF_ptrs[ psDec->indices.PERIndex ], 8 );
	srai	a2, a2, 22	# tmp272, tmp271,
	add.n	a2, a3, a2	# tmp273,, tmp272
# @OPUS@\upstream\silk\decode_indices.c:133:             psDec->indices.LTPIndex[ k ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_gain_iCDF_ptrs[ psDec->indices.PERIndex ], 8 );
	l32i.n	a3, a2, 0	# silk_LTP_gain_iCDF_ptrs,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	s32i.n	a5, sp, 60	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:133:             psDec->indices.LTPIndex[ k ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_gain_iCDF_ptrs[ psDec->indices.PERIndex ], 8 );
	l32i.n	a5, sp, 60	#,
	movi	a4, 0x5b8	#,
	add.n	a3, a5, a4	# tmp275, k,
	l32i.n	a4, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_indices.c:132:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	addi.n	a5, a5, 1	# k, k,
# @OPUS@\upstream\silk\decode_indices.c:133:             psDec->indices.LTPIndex[ k ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_gain_iCDF_ptrs[ psDec->indices.PERIndex ], 8 );
	add.n	a3, a4, a3	# tmp276,, tmp275
# @OPUS@\upstream\silk\decode_indices.c:133:             psDec->indices.LTPIndex[ k ] = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTP_gain_iCDF_ptrs[ psDec->indices.PERIndex ], 8 );
	s8i	a2, a3, 0	# MEM[base: _163, offset: 0B],
# @OPUS@\upstream\silk\decode_indices.c:132:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i.n	a2, a15, 24	# psDec_99(D)->nb_subfr, psDec_99(D)->nb_subfr
	bge	a5, a2, .L19	# k, psDec_99(D)->nb_subfr,
	l8ui	a2, a12, 212	# psDec_99(D)->indices.PERIndex, pretmp_232
	j	.L20		#
.L19:
# @OPUS@\upstream\silk\decode_indices.c:139:         if( condCoding == CODE_INDEPENDENTLY ) {
	l32i.n	a2, sp, 56	# %sfp,
	bnez.n	a2, .L21	#,
# @OPUS@\upstream\silk\decode_indices.c:140:             psDec->indices.LTP_scaleIndex = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTPscale_iCDF, 8 );
	l32r	a3, .LC11	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
	l8ui	a3, a12, 209	# psDec_99(D)->indices.signalType, _48
# @OPUS@\upstream\silk\decode_indices.c:140:             psDec->indices.LTP_scaleIndex = (opus_int8)ec_dec_icdf( psRangeDec, silk_LTPscale_iCDF, 8 );
	s8i	a2, a12, 213	# psDec_99(D)->indices.LTP_scaleIndex,
	slli	a2, a3, 24	# tmp293, _48,
	j	.L16		#
.L21:
	l8ui	a3, a12, 209	# psDec_99(D)->indices.signalType, _48
# @OPUS@\upstream\silk\decode_indices.c:142:             psDec->indices.LTP_scaleIndex = 0;
	movi.n	a2, 0	# tmp284,
	s8i	a2, a12, 213	# psDec_99(D)->indices.LTP_scaleIndex, tmp284
	slli	a2, a3, 24	# tmp293, _48,
.L16:
# @OPUS@\upstream\silk\decode_indices.c:145:     psDec->ec_prevSignalType = psDec->indices.signalType;
	srai	a2, a2, 24	# tmp287, tmp293,
# @OPUS@\upstream\silk\decode_indices.c:150:     psDec->indices.Seed = (opus_int8)ec_dec_icdf( psRangeDec, silk_uniform4_iCDF, 8 );
	l32r	a3, .LC12	#,
# @OPUS@\upstream\silk\decode_indices.c:145:     psDec->ec_prevSignalType = psDec->indices.signalType;
	s32i	a2, a15, 96	# psDec_99(D)->ec_prevSignalType, tmp287
# @OPUS@\upstream\silk\decode_indices.c:150:     psDec->indices.Seed = (opus_int8)ec_dec_icdf( psRangeDec, silk_uniform4_iCDF, 8 );
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_indices.c:150:     psDec->indices.Seed = (opus_int8)ec_dec_icdf( psRangeDec, silk_uniform4_iCDF, 8 );
	s8i	a2, a12, 214	# psDec_99(D)->indices.Seed,
# @OPUS@\upstream\silk\decode_indices.c:151: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	silk_decode_indices, .-silk_decode_indices
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
