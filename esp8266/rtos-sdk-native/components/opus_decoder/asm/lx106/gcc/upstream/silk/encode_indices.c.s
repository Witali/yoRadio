# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/encode_indices.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"encode_indices.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\encode_indices.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\encode_indices.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\encode_indices.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\encode_indices.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\encode_indices.c.s.raw
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
	.section	.text.silk_encode_indices,"ax",@progbits
	.literal_position
	.literal .LC0, 6100
	.literal .LC1, 6129
	.literal .LC2, 6130
	.literal .LC3, 4736
	.literal .LC4, silk_type_offset_VAD_iCDF
	.literal .LC5, silk_type_offset_no_VAD_iCDF
	.literal .LC6, silk_delta_gain_iCDF
	.literal .LC7, silk_gain_iCDF
	.literal .LC8, silk_uniform8_iCDF
	.literal .LC9, silk_NLSF_EXT_iCDF
	.literal .LC10, silk_NLSF_interpolation_factor_iCDF
	.literal .LC11, silk_pitch_delta_iCDF
	.literal .LC12, silk_LTP_per_index_iCDF
	.literal .LC13, silk_pitch_lag_iCDF
	.literal .LC14, silk_LTP_gain_iCDF_ptrs
	.literal .LC15, silk_LTPscale_iCDF
	.literal .LC16, silk_uniform4_iCDF
	.align	4
	.global	silk_encode_indices
	.type	silk_encode_indices, @function
# Function: silk_encode_indices
# Module: upstream/silk/encode_indices.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Encode side-information parameters to payload */
# C context: void silk_encode_indices(
# C context: silk_encoder_state          *psEncC,                        /* I/O  Encoder state                               */
# C context: ec_enc                      *psRangeEnc,                    /* I/O  Compressor data structure                   */
# C context: opus_int                    FrameIndex,                     /* I    Frame number                                */
# C context: opus_int                    encode_LBRR,                    /* I    Flag indicating LBRR data is being encoded  */
silk_encode_indices:
	addi	sp, sp, -112	#,,
	s32i	a12, sp, 104	#,
	s32i	a0, sp, 108	#,
	s32i	a13, sp, 100	#,
	s32i	a14, sp, 96	#,
	s32i	a15, sp, 92	#,
# @OPUS@\upstream\silk\encode_indices.c:42: {
	s32i.n	a2, sp, 56	# %sfp, psEncC
	s32i	a6, sp, 64	# %sfp, condCoding
	mov.n	a12, a3	# psRangeEnc, psRangeEnc
# @OPUS@\upstream\silk\encode_indices.c:49:     if( encode_LBRR ) {
	beqz.n	a5, .L2	# encode_LBRR,
# @OPUS@\upstream\silk\encode_indices.c:50:          psIndices = &psEncC->indices_LBRR[ FrameIndex ];
	slli	a13, a4, 3	# tmp176, FrameIndex,
	add.n	a13, a13, a4	# tmp177, tmp176, FrameIndex
	slli	a13, a13, 2	# tmp178, tmp177,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	l32r	a4, .LC2	#, tmp201
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	l32r	a3, .LC1	#, tmp187
	add.n	a2, a2, a13	# tmp185, psEncC, tmp178
	add.n	a3, a2, a3	# tmp186, tmp185, tmp187
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	add.n	a2, a2, a4	# tmp200, tmp185, tmp201
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	l8ui	a3, a3, 0	# MEM[(const struct SideInfoIndices *)psEncC_119(D)].indices_LBRR[FrameIndex_120(D)].signalType,
# @OPUS@\upstream\silk\encode_indices.c:50:          psIndices = &psEncC->indices_LBRR[ FrameIndex ];
	l32r	a4, .LC0	#, tmp180
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	l8ui	a2, a2, 0	# MEM[(const struct SideInfoIndices *)psEncC_119(D)].indices_LBRR[FrameIndex_120(D)].quantOffsetType,
# @OPUS@\upstream\silk\encode_indices.c:50:          psIndices = &psEncC->indices_LBRR[ FrameIndex ];
	add.n	a13, a13, a4	# tmp179, tmp178, tmp180
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	slli	a3, a3, 24	# tmp191, MEM[(const struct SideInfoIndices *)psEncC_119(D)].indices_LBRR[FrameIndex_120(D)].signalType,
# @OPUS@\upstream\silk\encode_indices.c:50:          psIndices = &psEncC->indices_LBRR[ FrameIndex ];
	l32i.n	a4, sp, 56	# %sfp,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	slli	a2, a2, 24	# tmp204, MEM[(const struct SideInfoIndices *)psEncC_119(D)].indices_LBRR[FrameIndex_120(D)].quantOffsetType,
	srai	a2, a2, 24	# tmp202, tmp204,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	srai	a3, a3, 23	# tmp194, tmp191,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	add.n	a3, a3, a2	# typeOffset, tmp194, tmp202
	addmi	a2, a4, 0x1200	#,,
# @OPUS@\upstream\silk\encode_indices.c:50:          psIndices = &psEncC->indices_LBRR[ FrameIndex ];
	add.n	a13, a4, a13	# psIndices,, tmp179
	s32i.n	a2, sp, 48	# %sfp,
	j	.L3		#
.L2:
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	addmi	a3, a2, 0x1200	#, tmp3,
	s32i.n	a3, sp, 48	# %sfp,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	l32i.n	a4, sp, 48	# %sfp,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	l8ui	a3, a3, 157	# MEM[(const struct SideInfoIndices *)psEncC_119(D) + 4736B].signalType,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	l8ui	a2, a4, 158	# MEM[(const struct SideInfoIndices *)psEncC_119(D) + 4736B].quantOffsetType,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	slli	a3, a3, 24	# tmp210, MEM[(const struct SideInfoIndices *)psEncC_119(D) + 4736B].signalType,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	slli	a2, a2, 24	# tmp217, MEM[(const struct SideInfoIndices *)psEncC_119(D) + 4736B].quantOffsetType,
	srai	a2, a2, 24	# tmp215, tmp217,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	srai	a3, a3, 23	# tmp213, tmp210,
# @OPUS@\upstream\silk\encode_indices.c:58:     typeOffset = 2 * psIndices->signalType + psIndices->quantOffsetType;
	add.n	a3, a3, a2	# typeOffset, tmp213, tmp215
# @OPUS@\upstream\silk\encode_indices.c:52:          psIndices = &psEncC->indices;
	l32r	a13, .LC3	#, tmp205
	l32i.n	a2, sp, 56	# %sfp,
	add.n	a13, a2, a13	# psIndices,, tmp205
# @OPUS@\upstream\silk\encode_indices.c:61:     if( encode_LBRR || typeOffset >= 2 ) {
	blti	a3, 2, .L4	# typeOffset,,
.L3:
# @OPUS@\upstream\silk\encode_indices.c:62:         ec_enc_icdf( psRangeEnc, typeOffset - 2, silk_type_offset_VAD_iCDF, 8 );
	l32r	a4, .LC4	#,
	movi.n	a5, 8	#,
	addi	a3, a3, -2	#, typeOffset,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
	j	.L5		#
.L4:
# @OPUS@\upstream\silk\encode_indices.c:64:         ec_enc_icdf( psRangeEnc, typeOffset, silk_type_offset_no_VAD_iCDF, 8 );
	l32r	a4, .LC5	#,
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L5:
# @OPUS@\upstream\silk\encode_indices.c:71:     if( condCoding == CODE_CONDITIONALLY ) {
	l32i	a4, sp, 64	# %sfp,
	l8ui	a3, a13, 0	# psIndices_201->GainsIndices, pretmp_240
	bnei	a4, 2, .L6	#,,
# @OPUS@\upstream\silk\encode_indices.c:74:         ec_enc_icdf( psRangeEnc, psIndices->GainsIndices[ 0 ], silk_delta_gain_iCDF, 8 );
	slli	a3, a3, 24	# tmp223, pretmp_240,
	l32r	a4, .LC6	#,
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp223,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L10:
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	l32i.n	a2, sp, 56	# %sfp,
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	movi.n	a15, 1	# i,
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	addmi	a2, a2, 0x1100	#,,
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	l32i	a2, a2, 228	# psEncC_119(D)->nb_subfr, psEncC_119(D)->nb_subfr
# @OPUS@\upstream\silk\encode_indices.c:85:         ec_enc_icdf( psRangeEnc, psIndices->GainsIndices[ i ], silk_delta_gain_iCDF, 8 );
	movi.n	a14, 8	# tmp393,
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	bgei	a2, 2, .L33	# psEncC_119(D)->nb_subfr,,
.L11:
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	l32i.n	a3, sp, 48	# %sfp,
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	l8ui	a2, a13, 29	# psIndices_201->signalType,
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	l32i	a5, a3, 84	# psEncC_119(D)->psNLSF_CB, _26
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	slli	a2, a2, 24	# tmp229, psIndices_201->signalType,
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	l16ui	a4, a5, 0	# _26->nVectors,
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	l8ui	a3, a13, 8	# psIndices_201->NLSFIndices,
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	srai	a2, a2, 25	# tmp232, tmp229,
	mul16s	a2, a2, a4	# tmp234, tmp232, _26->nVectors
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	l32i.n	a4, a5, 16	# _26->CB1_iCDF, _26->CB1_iCDF
# @OPUS@\upstream\silk\encode_indices.c:91:     ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ 0 ], &psEncC->psNLSF_CB->CB1_iCDF[ ( psIndices->signalType >> 1 ) * psEncC->psNLSF_CB->nVectors ], 8 );
	slli	a3, a3, 24	# tmp240, psIndices_201->NLSFIndices,
	add.n	a4, a4, a2	#, _26->CB1_iCDF, tmp234
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp240,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:92:     silk_NLSF_unpack( ec_ix, pred_Q8, psEncC->psNLSF_CB, psIndices->NLSFIndices[ 0 ] );
	l32i.n	a2, sp, 48	# %sfp,
	l8ui	a5, a13, 8	# psIndices_201->NLSFIndices,
	l32i	a4, a2, 84	# psEncC_119(D)->psNLSF_CB,
	slli	a5, a5, 24	# tmp243, psIndices_201->NLSFIndices,
	addi	a3, sp, 32	#,,
	mov.n	a2, sp	#,
	srai	a5, a5, 24	#, tmp243,
	call0	silk_NLSF_unpack		#
# @OPUS@\upstream\silk\encode_indices.c:94:     for( i = 0; i < psEncC->psNLSF_CB->order; i++ ) {
	l32i.n	a4, sp, 48	# %sfp,
	addi.n	a15, a13, 9	# ivtmp$7, psIndices,
	l32i	a3, a4, 84	# psEncC_119(D)->psNLSF_CB, _61
# @OPUS@\upstream\silk\encode_indices.c:98:         } else if( psIndices->NLSFIndices[ i+1 ] <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a4, -3	# tmp391,
# @OPUS@\upstream\silk\encode_indices.c:94:     for( i = 0; i < psEncC->psNLSF_CB->order; i++ ) {
	l16si	a2, a3, 2	# _280->order, tmp247
	movi.n	a14, 0	# ivtmp$5,
# @OPUS@\upstream\silk\encode_indices.c:98:         } else if( psIndices->NLSFIndices[ i+1 ] <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	slli	a6, a4, 24	# tmp392, tmp391,
# @OPUS@\upstream\silk\encode_indices.c:94:     for( i = 0; i < psEncC->psNLSF_CB->order; i++ ) {
	bgei	a2, 1, .L34	# tmp247,,
	j	.L9		#
.L6:
# @OPUS@\upstream\silk\encode_indices.c:78:         ec_enc_icdf( psRangeEnc, silk_RSHIFT( psIndices->GainsIndices[ 0 ], 3 ), silk_gain_iCDF[ psIndices->signalType ], 8 );
	l8ui	a2, a13, 29	# psIndices_201->signalType,
# @OPUS@\upstream\silk\encode_indices.c:78:         ec_enc_icdf( psRangeEnc, silk_RSHIFT( psIndices->GainsIndices[ 0 ], 3 ), silk_gain_iCDF[ psIndices->signalType ], 8 );
	l32r	a4, .LC7	#, tmp258
# @OPUS@\upstream\silk\encode_indices.c:78:         ec_enc_icdf( psRangeEnc, silk_RSHIFT( psIndices->GainsIndices[ 0 ], 3 ), silk_gain_iCDF[ psIndices->signalType ], 8 );
	slli	a2, a2, 24	# tmp253, psIndices_201->signalType,
	srai	a2, a2, 21	# tmp256, tmp253,
# @OPUS@\upstream\silk\encode_indices.c:78:         ec_enc_icdf( psRangeEnc, silk_RSHIFT( psIndices->GainsIndices[ 0 ], 3 ), silk_gain_iCDF[ psIndices->signalType ], 8 );
	slli	a3, a3, 24	# tmp260, pretmp_240,
	add.n	a4, a4, a2	#, tmp258, tmp256
	srai	a3, a3, 27	#, tmp260,
	mov.n	a2, a12	#, psRangeEnc
	movi.n	a5, 8	#,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:79:         ec_enc_icdf( psRangeEnc, psIndices->GainsIndices[ 0 ] & 7, silk_uniform8_iCDF, 8 );
	l8ui	a3, a13, 0	# psIndices_201->GainsIndices,
	l32r	a4, .LC8	#,
	movi.n	a5, 8	#,
	extui	a3, a3, 0, 3	#, psIndices_201->GainsIndices,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
	j	.L10		#
.L33:
	s32i.n	a12, sp, 52	# %sfp, psRangeEnc
	mov.n	a12, a15	# i, i
	l32i.n	a15, sp, 60	# %sfp, tmp385
.L7:
# @OPUS@\upstream\silk\encode_indices.c:85:         ec_enc_icdf( psRangeEnc, psIndices->GainsIndices[ i ], silk_delta_gain_iCDF, 8 );
	add.n	a2, a13, a12	# tmp269, psIndices, i
# @OPUS@\upstream\silk\encode_indices.c:85:         ec_enc_icdf( psRangeEnc, psIndices->GainsIndices[ i ], silk_delta_gain_iCDF, 8 );
	l8ui	a3, a2, 0	# MEM[base: _253, offset: 0B],
	l32r	a4, .LC6	#,
	l32i.n	a2, sp, 52	# %sfp,
	slli	a3, a3, 24	# tmp272, MEM[base: _253, offset: 0B],
	mov.n	a5, a14	#, tmp393
	srai	a3, a3, 24	#, tmp272,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	l32i	a2, a15, 228	# psEncC_119(D)->nb_subfr, psEncC_119(D)->nb_subfr
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	addi.n	a12, a12, 1	# i, i,
# @OPUS@\upstream\silk\encode_indices.c:83:     for( i = 1; i < psEncC->nb_subfr; i++ ) {
	blt	a12, a2, .L7	# i, psEncC_119(D)->nb_subfr,
	l32i.n	a12, sp, 52	# %sfp, psRangeEnc
	j	.L11		#
.L34:
	s32i.n	a13, sp, 52	# %sfp, psIndices
	mov.n	a13, a15	# ivtmp$7, ivtmp$7
	mov.n	a15, a6	# tmp392, tmp392
.L15:
	slli	a2, a14, 1	# tmp275, ivtmp$5,
# @OPUS@\upstream\silk\encode_indices.c:95:         if( psIndices->NLSFIndices[ i+1 ] >= NLSF_QUANT_MAX_AMPLITUDE ) {
	l8ui	a6, a13, 0	# MEM[base: _258, offset: 0B], _40
	add.n	a2, sp, a2	# tmp276,, tmp275
	l16si	a2, a2, 0	# MEM[base: _256, offset: 0B], tmp277
	l32i.n	a7, a3, 28	# _273->ec_iCDF, _273->ec_iCDF
# @OPUS@\upstream\silk\encode_indices.c:95:         if( psIndices->NLSFIndices[ i+1 ] >= NLSF_QUANT_MAX_AMPLITUDE ) {
	slli	a6, a6, 24	# tmp282, _40,
	add.n	a7, a7, a2	# _286, _273->ec_iCDF, tmp277
	srai	a6, a6, 24	# tmp281, tmp282,
# @OPUS@\upstream\silk\encode_indices.c:98:         } else if( psIndices->NLSFIndices[ i+1 ] <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	srai	a10, a15, 24	# tmp291, tmp392,
# @OPUS@\upstream\silk\encode_indices.c:96:             ec_enc_icdf( psRangeEnc, 2 * NLSF_QUANT_MAX_AMPLITUDE, &psEncC->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	mov.n	a4, a7	#, _286
	mov.n	a2, a12	#, psRangeEnc
	movi.n	a5, 8	#,
# @OPUS@\upstream\silk\encode_indices.c:95:         if( psIndices->NLSFIndices[ i+1 ] >= NLSF_QUANT_MAX_AMPLITUDE ) {
	blti	a6, 4, .L12	# tmp281,,
# @OPUS@\upstream\silk\encode_indices.c:96:             ec_enc_icdf( psRangeEnc, 2 * NLSF_QUANT_MAX_AMPLITUDE, &psEncC->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	mov.n	a3, a5	#,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:97:             ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	l8ui	a3, a13, 0	# MEM[base: _258, offset: 0B],
# @OPUS@\upstream\silk\encode_indices.c:97:             ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	l32r	a4, .LC9	#,
# @OPUS@\upstream\silk\encode_indices.c:97:             ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	slli	a3, a3, 24	# tmp286, MEM[base: _258, offset: 0B],
	srai	a3, a3, 24	# tmp284, tmp286,
# @OPUS@\upstream\silk\encode_indices.c:97:             ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	movi.n	a5, 8	#,
	addi	a3, a3, -4	#, tmp284,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
	j	.L13		#
.L12:
# @OPUS@\upstream\silk\encode_indices.c:99:             ec_enc_icdf( psRangeEnc, 0, &psEncC->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	movi.n	a3, 0	#,
# @OPUS@\upstream\silk\encode_indices.c:98:         } else if( psIndices->NLSFIndices[ i+1 ] <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	bge	a6, a10, .L14	# tmp281, tmp291,
# @OPUS@\upstream\silk\encode_indices.c:99:             ec_enc_icdf( psRangeEnc, 0, &psEncC->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:100:             ec_enc_icdf( psRangeEnc, -psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	l8ui	a2, a13, 0	# MEM[base: _258, offset: 0B],
# @OPUS@\upstream\silk\encode_indices.c:100:             ec_enc_icdf( psRangeEnc, -psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	l32r	a4, .LC9	#,
# @OPUS@\upstream\silk\encode_indices.c:100:             ec_enc_icdf( psRangeEnc, -psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	slli	a2, a2, 24	# tmp296, MEM[base: _258, offset: 0B],
	srai	a2, a2, 24	# tmp294, tmp296,
# @OPUS@\upstream\silk\encode_indices.c:100:             ec_enc_icdf( psRangeEnc, -psIndices->NLSFIndices[ i+1 ] - NLSF_QUANT_MAX_AMPLITUDE, silk_NLSF_EXT_iCDF, 8 );
	movi.n	a3, -4	# tmp297,
	sub	a3, a3, a2	#, tmp297, tmp294
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
	j	.L13		#
.L14:
# @OPUS@\upstream\silk\encode_indices.c:102:             ec_enc_icdf( psRangeEnc, psIndices->NLSFIndices[ i+1 ] + NLSF_QUANT_MAX_AMPLITUDE, &psEncC->psNLSF_CB->ec_iCDF[ ec_ix[ i ] ], 8 );
	movi.n	a5, 8	#,
	addi.n	a3, a6, 4	#, tmp281,
	call0	ec_enc_icdf		#
.L13:
# @OPUS@\upstream\silk\encode_indices.c:94:     for( i = 0; i < psEncC->psNLSF_CB->order; i++ ) {
	l32i.n	a2, sp, 48	# %sfp,
	addi.n	a14, a14, 1	# ivtmp$5, ivtmp$5,
	l32i	a3, a2, 84	# psEncC_119(D)->psNLSF_CB, _61
	addi.n	a13, a13, 1	# ivtmp$7, ivtmp$7,
# @OPUS@\upstream\silk\encode_indices.c:94:     for( i = 0; i < psEncC->psNLSF_CB->order; i++ ) {
	l16si	a2, a3, 2	# _61->order, tmp303
# @OPUS@\upstream\silk\encode_indices.c:94:     for( i = 0; i < psEncC->psNLSF_CB->order; i++ ) {
	blt	a14, a2, .L15	# ivtmp$5, tmp303,
	l32i.n	a13, sp, 52	# %sfp, psIndices
.L9:
# @OPUS@\upstream\silk\encode_indices.c:107:     if( psEncC->nb_subfr == MAX_NB_SUBFR ) {
	l32i.n	a3, sp, 60	# %sfp,
	l32i	a2, a3, 228	# psEncC_119(D)->nb_subfr, psEncC_119(D)->nb_subfr
	bnei	a2, 4, .L16	# psEncC_119(D)->nb_subfr,,
# @OPUS@\upstream\silk\encode_indices.c:109:         ec_enc_icdf( psRangeEnc, psIndices->NLSFInterpCoef_Q2, silk_NLSF_interpolation_factor_iCDF, 8 );
	l8ui	a3, a13, 31	# psIndices_201->NLSFInterpCoef_Q2,
	l32r	a4, .LC10	#,
	slli	a3, a3, 24	# tmp311, psIndices_201->NLSFInterpCoef_Q2,
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp311,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L16:
# @OPUS@\upstream\silk\encode_indices.c:112:     if( psIndices->signalType == TYPE_VOICED )
	l8ui	a3, a13, 29	# psIndices_201->signalType, _67
	l32i.n	a4, sp, 56	# %sfp,
# @OPUS@\upstream\silk\encode_indices.c:112:     if( psIndices->signalType == TYPE_VOICED )
	slli	a2, a3, 24	# tmp389, _67,
	addmi	a14, a4, 0x1600	# tmp388,,
	bnei	a3, 2, .L17	# _67,,
# @OPUS@\upstream\silk\encode_indices.c:119:         if( condCoding == CODE_CONDITIONALLY && psEncC->ec_prevSignalType == TYPE_VOICED ) {
	l32i	a2, sp, 64	# %sfp,
	l16si	a7, a13, 26	# psIndices_201->lagIndex, _288
	bnei	a2, 2, .L18	#,,
# @OPUS@\upstream\silk\encode_indices.c:119:         if( condCoding == CODE_CONDITIONALLY && psEncC->ec_prevSignalType == TYPE_VOICED ) {
	l32i	a2, a14, 136	# psEncC_119(D)->ec_prevSignalType, psEncC_119(D)->ec_prevSignalType
	bnei	a2, 2, .L18	# psEncC_119(D)->ec_prevSignalType,,
# @OPUS@\upstream\silk\encode_indices.c:121:             delta_lagIndex = psIndices->lagIndex - psEncC->ec_prevLagIndex;
	l16si	a3, a14, 140	# psEncC_119(D)->ec_prevLagIndex, tmp319
# @OPUS@\upstream\silk\encode_indices.c:122:             if( delta_lagIndex < -8 || delta_lagIndex > 11 ) {
	movi.n	a4, 0x13	# tmp323,
# @OPUS@\upstream\silk\encode_indices.c:121:             delta_lagIndex = psIndices->lagIndex - psEncC->ec_prevLagIndex;
	sub	a3, a7, a3	# delta_lagIndex, _288, tmp319
# @OPUS@\upstream\silk\encode_indices.c:122:             if( delta_lagIndex < -8 || delta_lagIndex > 11 ) {
	addi.n	a2, a3, 8	# tmp322, delta_lagIndex,
# @OPUS@\upstream\silk\encode_indices.c:122:             if( delta_lagIndex < -8 || delta_lagIndex > 11 ) {
	bgeu	a4, a2, .L19	# tmp323, tmp322,
# @OPUS@\upstream\silk\encode_indices.c:129:             ec_enc_icdf( psRangeEnc, delta_lagIndex, silk_pitch_delta_iCDF, 8 );
	l32r	a4, .LC11	#,
	movi.n	a5, 8	#,
	movi.n	a3, 0	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
	l16si	a7, a13, 26	# psIndices_201->lagIndex, _288
	j	.L18		#
.L19:
	l32r	a4, .LC11	#,
	movi.n	a5, 8	#,
	addi.n	a3, a3, 9	#, delta_lagIndex,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:141:         psEncC->ec_prevLagIndex = psIndices->lagIndex;
	l16ui	a2, a13, 26	# psIndices_201->lagIndex,
# @OPUS@\upstream\silk\encode_indices.c:149:         ec_enc_icdf( psRangeEnc, psIndices->contourIndex, psEncC->pitch_contour_iCDF, 8 );
	l32i.n	a3, sp, 48	# %sfp,
	movi.n	a5, 8	#,
	l32i	a4, a3, 80	# psEncC_119(D)->pitch_contour_iCDF,
# @OPUS@\upstream\silk\encode_indices.c:141:         psEncC->ec_prevLagIndex = psIndices->lagIndex;
	s16i	a2, a14, 140	# psEncC_119(D)->ec_prevLagIndex, psIndices_201->lagIndex
# @OPUS@\upstream\silk\encode_indices.c:149:         ec_enc_icdf( psRangeEnc, psIndices->contourIndex, psEncC->pitch_contour_iCDF, 8 );
	l8ui	a3, a13, 28	# psIndices_201->contourIndex,
	mov.n	a2, a12	#, psRangeEnc
	slli	a3, a3, 24	# tmp334, psIndices_201->contourIndex,
	srai	a3, a3, 24	#, tmp334,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:156:         ec_enc_icdf( psRangeEnc, psIndices->PERIndex, silk_LTP_per_index_iCDF, 8 );
	l8ui	a3, a13, 32	# psIndices_201->PERIndex,
	l32r	a4, .LC12	#,
	slli	a3, a3, 24	# tmp338, psIndices_201->PERIndex,
	mov.n	a2, a12	#, psRangeEnc
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp338,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:159:         for( k = 0; k < psEncC->nb_subfr; k++ ) {
	l32i.n	a4, sp, 60	# %sfp,
	l32i	a2, a4, 228	# psEncC_119(D)->nb_subfr, psEncC_119(D)->nb_subfr
	bgei	a2, 1, .L20	# psEncC_119(D)->nb_subfr,,
	j	.L35		#
.L18:
# @OPUS@\upstream\silk\encode_indices.c:134:             pitch_high_bits = silk_DIV32_16( psIndices->lagIndex, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	l32i.n	a2, sp, 60	# %sfp,
	l32i	a4, a2, 224	# psEncC_119(D)->fs_kHz, psEncC_119(D)->fs_kHz
# @OPUS@\upstream\silk\encode_indices.c:134:             pitch_high_bits = silk_DIV32_16( psIndices->lagIndex, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	mov.n	a2, a7	#, _288
# @OPUS@\upstream\silk\encode_indices.c:134:             pitch_high_bits = silk_DIV32_16( psIndices->lagIndex, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	srai	a4, a4, 1	# _78, psEncC_119(D)->fs_kHz,
# @OPUS@\upstream\silk\encode_indices.c:134:             pitch_high_bits = silk_DIV32_16( psIndices->lagIndex, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	mov.n	a3, a4	#, _78
	s32i	a4, sp, 68	#,
	s32i	a7, sp, 72	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\encode_indices.c:135:             pitch_low_bits = psIndices->lagIndex - silk_SMULBB( pitch_high_bits, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	l32i	a4, sp, 68	#,
# @OPUS@\upstream\silk\encode_indices.c:135:             pitch_low_bits = psIndices->lagIndex - silk_SMULBB( pitch_high_bits, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	l32i	a7, sp, 72	#,
# @OPUS@\upstream\silk\encode_indices.c:135:             pitch_low_bits = psIndices->lagIndex - silk_SMULBB( pitch_high_bits, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	mul16s	a6, a2, a4	# tmp346, tmp345, _78
# @OPUS@\upstream\silk\encode_indices.c:138:             ec_enc_icdf( psRangeEnc, pitch_high_bits, silk_pitch_lag_iCDF, 8 );
	l32r	a4, .LC13	#,
# @OPUS@\upstream\silk\encode_indices.c:135:             pitch_low_bits = psIndices->lagIndex - silk_SMULBB( pitch_high_bits, silk_RSHIFT( psEncC->fs_kHz, 1 ) );
	sub	a6, a7, a6	# pitch_low_bits, _288, tmp346
# @OPUS@\upstream\silk\encode_indices.c:138:             ec_enc_icdf( psRangeEnc, pitch_high_bits, silk_pitch_lag_iCDF, 8 );
	mov.n	a3, a2	#, tmp345
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	s32i	a6, sp, 68	#,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:139:             ec_enc_icdf( psRangeEnc, pitch_low_bits, psEncC->pitch_lag_low_bits_iCDF, 8 );
	l32i.n	a3, sp, 48	# %sfp,
	l32i	a6, sp, 68	#,
	l32i	a4, a3, 76	# psEncC_119(D)->pitch_lag_low_bits_iCDF,
	movi.n	a5, 8	#,
	mov.n	a3, a6	#, pitch_low_bits
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:141:         psEncC->ec_prevLagIndex = psIndices->lagIndex;
	l16ui	a2, a13, 26	# psIndices_201->lagIndex,
# @OPUS@\upstream\silk\encode_indices.c:149:         ec_enc_icdf( psRangeEnc, psIndices->contourIndex, psEncC->pitch_contour_iCDF, 8 );
	l32i.n	a3, sp, 48	# %sfp,
	movi.n	a5, 8	#,
	l32i	a4, a3, 80	# psEncC_119(D)->pitch_contour_iCDF,
# @OPUS@\upstream\silk\encode_indices.c:141:         psEncC->ec_prevLagIndex = psIndices->lagIndex;
	s16i	a2, a14, 140	# psEncC_119(D)->ec_prevLagIndex, psIndices_201->lagIndex
# @OPUS@\upstream\silk\encode_indices.c:149:         ec_enc_icdf( psRangeEnc, psIndices->contourIndex, psEncC->pitch_contour_iCDF, 8 );
	l8ui	a3, a13, 28	# psIndices_201->contourIndex,
	mov.n	a2, a12	#, psRangeEnc
	slli	a3, a3, 24	# tmp354, psIndices_201->contourIndex,
	srai	a3, a3, 24	#, tmp354,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:156:         ec_enc_icdf( psRangeEnc, psIndices->PERIndex, silk_LTP_per_index_iCDF, 8 );
	l8ui	a3, a13, 32	# psIndices_201->PERIndex,
	l32r	a4, .LC12	#,
	slli	a3, a3, 24	# tmp358, psIndices_201->PERIndex,
	mov.n	a2, a12	#, psRangeEnc
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp358,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:159:         for( k = 0; k < psEncC->nb_subfr; k++ ) {
	l32i.n	a4, sp, 60	# %sfp,
	l32i	a2, a4, 228	# psEncC_119(D)->nb_subfr, psEncC_119(D)->nb_subfr
	bgei	a2, 1, .L20	# psEncC_119(D)->nb_subfr,,
.L24:
# @OPUS@\upstream\silk\encode_indices.c:167:         if( condCoding == CODE_INDEPENDENTLY ) {
	l32i	a2, sp, 64	# %sfp,
	bnez.n	a2, .L35	#,
	j	.L22		#
.L20:
# @OPUS@\upstream\silk\encode_indices.c:161:             ec_enc_icdf( psRangeEnc, psIndices->LTPIndex[ k ], silk_LTP_gain_iCDF_ptrs[ psIndices->PERIndex ], 8 );
	l32i.n	a15, sp, 60	# %sfp, tmp385
	s32i.n	a14, sp, 48	# %sfp, tmp388
	mov.n	a14, a13	# psIndices, psIndices
.L23:
# @OPUS@\upstream\silk\encode_indices.c:161:             ec_enc_icdf( psRangeEnc, psIndices->LTPIndex[ k ], silk_LTP_gain_iCDF_ptrs[ psIndices->PERIndex ], 8 );
	l8ui	a2, a14, 32	# psIndices_201->PERIndex,
# @OPUS@\upstream\silk\encode_indices.c:161:             ec_enc_icdf( psRangeEnc, psIndices->LTPIndex[ k ], silk_LTP_gain_iCDF_ptrs[ psIndices->PERIndex ], 8 );
	l32r	a4, .LC14	#,
# @OPUS@\upstream\silk\encode_indices.c:161:             ec_enc_icdf( psRangeEnc, psIndices->LTPIndex[ k ], silk_LTP_gain_iCDF_ptrs[ psIndices->PERIndex ], 8 );
	slli	a2, a2, 24	# tmp364, psIndices_201->PERIndex,
# @OPUS@\upstream\silk\encode_indices.c:161:             ec_enc_icdf( psRangeEnc, psIndices->LTPIndex[ k ], silk_LTP_gain_iCDF_ptrs[ psIndices->PERIndex ], 8 );
	l8ui	a3, a13, 4	# MEM[base: _183, offset: 4B],
# @OPUS@\upstream\silk\encode_indices.c:161:             ec_enc_icdf( psRangeEnc, psIndices->LTPIndex[ k ], silk_LTP_gain_iCDF_ptrs[ psIndices->PERIndex ], 8 );
	srai	a2, a2, 22	# tmp365, tmp364,
	add.n	a2, a4, a2	# tmp366,, tmp365
# @OPUS@\upstream\silk\encode_indices.c:161:             ec_enc_icdf( psRangeEnc, psIndices->LTPIndex[ k ], silk_LTP_gain_iCDF_ptrs[ psIndices->PERIndex ], 8 );
	l32i.n	a4, a2, 0	# silk_LTP_gain_iCDF_ptrs,
	slli	a3, a3, 24	# tmp369, MEM[base: _183, offset: 4B],
	srai	a3, a3, 24	#, tmp369,
	mov.n	a2, a12	#, psRangeEnc
	movi.n	a5, 8	#,
	call0	ec_enc_icdf		#
	addi.n	a13, a13, 1	# ivtmp$3, ivtmp$3,
# @OPUS@\upstream\silk\encode_indices.c:159:         for( k = 0; k < psEncC->nb_subfr; k++ ) {
	l32i	a2, a15, 228	# psEncC_119(D)->nb_subfr, psEncC_119(D)->nb_subfr
	sub	a3, a13, a14	# k, ivtmp$3, psIndices
	blt	a3, a2, .L23	# k, psEncC_119(D)->nb_subfr,
	mov.n	a13, a14	# psIndices, psIndices
	l32i.n	a14, sp, 48	# %sfp, tmp388
	j	.L24		#
.L22:
# @OPUS@\upstream\silk\encode_indices.c:169:             ec_enc_icdf( psRangeEnc, psIndices->LTP_scaleIndex, silk_LTPscale_iCDF, 8 );
	l8ui	a3, a13, 33	# psIndices_201->LTP_scaleIndex,
	l32r	a4, .LC15	#,
	slli	a3, a3, 24	# tmp376, psIndices_201->LTP_scaleIndex,
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp376,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L35:
	l8ui	a3, a13, 29	# psIndices_201->signalType, _67
	slli	a2, a3, 24	# tmp389, _67,
.L17:
# @OPUS@\upstream\silk\encode_indices.c:174:     psEncC->ec_prevSignalType = psIndices->signalType;
	srai	a2, a2, 24	# tmp378, tmp389,
	s32i	a2, a14, 136	# psEncC_119(D)->ec_prevSignalType, tmp378
# @OPUS@\upstream\silk\encode_indices.c:180:     ec_enc_icdf( psRangeEnc, psIndices->Seed, silk_uniform4_iCDF, 8 );
	l8ui	a3, a13, 34	# psIndices_201->Seed,
	l32r	a4, .LC16	#,
	slli	a3, a3, 24	# tmp383, psIndices_201->Seed,
	mov.n	a2, a12	#, psRangeEnc
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp383,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_indices.c:181: }
	l32i	a0, sp, 108	#,
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	silk_encode_indices, .-silk_encode_indices
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
