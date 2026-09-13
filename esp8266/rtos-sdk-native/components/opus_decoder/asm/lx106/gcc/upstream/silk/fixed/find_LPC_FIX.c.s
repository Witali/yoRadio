# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/find_LPC_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"find_LPC_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LPC_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LPC_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LPC_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LPC_FIX.c.s.raw
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
	.section	.text.silk_find_LPC_FIX,"ax",@progbits
	.literal_position
	.literal .LC0, 4500
	.align	4
	.global	silk_find_LPC_FIX
	.type	silk_find_LPC_FIX, @function
# Function: silk_find_LPC_FIX
# Module: upstream/silk/fixed/find_LPC_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "tuning_parameters.h"
# C context:
# C context: /* Finds LPC vector from correlations, and converts to NLSF */
# C context: void silk_find_LPC_FIX(
# C context: silk_encoder_state              *psEncC,                                /* I/O  Encoder state                                                               */
# C context: opus_int16                      NLSF_Q15[],                             /* O    NLSFs                                                                       */
# C context: const opus_int16                x[],                                    /* I    Input signal                                                                */
# C context: const opus_int32                minInvGain_Q30                          /* I    Inverse of max prediction gain                                              */
silk_find_LPC_FIX:
	movi	a9, 0x140	#,
	sub	sp, sp, a9	#,,
	s32i	a0, sp, 316	#,
	s32i	a12, sp, 312	#,
	s32i	a13, sp, 308	#,
	s32i	a14, sp, 304	#,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:57:     subfr_length = psEncC->subfr_length + psEncC->predictLPCOrder;
	addmi	a13, a2, 0x1100	# tmp116, psEncC,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:57:     subfr_length = psEncC->subfr_length + psEncC->predictLPCOrder;
	addmi	a14, a2, 0x1200	# tmp218, psEncC,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:43: {
	s32i	a15, sp, 300	#,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:43: {
	mov.n	a12, a2	# psEncC, psEncC
	s32i	a4, sp, 260	# %sfp, x
	s32i	a5, sp, 256	# %sfp, minInvGain_Q30
	s32i	a3, sp, 268	# %sfp, NLSF_Q15
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:55:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:60:     psEncC->indices.NLSFInterpCoef_Q2 = 4;
	movi.n	a5, 4	# tmp119,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:57:     subfr_length = psEncC->subfr_length + psEncC->predictLPCOrder;
	l32i	a7, a13, 236	# psEncC_73(D)->subfr_length, psEncC_73(D)->subfr_length
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:63:     silk_burg_modified( &res_nrg, &res_nrg_Q, a_Q16, x, minInvGain_Q30, subfr_length, psEncC->nb_subfr, psEncC->predictLPCOrder, psEncC->arch );
	addmi	a15, a12, 0x1300	# tmp217, psEncC,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:60:     psEncC->indices.NLSFInterpCoef_Q2 = 4;
	s8i	a5, a14, 159	# psEncC_73(D)->indices.NLSFInterpCoef_Q2, tmp119
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:63:     silk_burg_modified( &res_nrg, &res_nrg_Q, a_Q16, x, minInvGain_Q30, subfr_length, psEncC->nb_subfr, psEncC->predictLPCOrder, psEncC->arch );
	l32i	a6, a15, 228	# psEncC_73(D)->arch, psEncC_73(D)->arch
	l32i	a5, a13, 228	# psEncC_73(D)->nb_subfr, psEncC_73(D)->nb_subfr
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:57:     subfr_length = psEncC->subfr_length + psEncC->predictLPCOrder;
	l32i.n	a4, a14, 32	# psEncC_73(D)->predictLPCOrder, _2
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:55:     SAVE_STACK;
	s32i	a2, sp, 208	# _saved_stack,
	s32i	a3, sp, 212	# _saved_stack,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:63:     silk_burg_modified( &res_nrg, &res_nrg_Q, a_Q16, x, minInvGain_Q30, subfr_length, psEncC->nb_subfr, psEncC->predictLPCOrder, psEncC->arch );
	addi	a2, sp, 16	#,,
	movi	a3, 0xcc	# tmp121,
	s32i.n	a6, sp, 8	#, psEncC_73(D)->arch
	s32i.n	a5, sp, 0	#, psEncC_73(D)->nb_subfr
	add.n	a3, a2, a3	#,, tmp121
	addi	a8, sp, 16	#,,
	l32i	a6, sp, 256	# %sfp,
	l32i	a5, sp, 260	# %sfp,
	movi	a2, 0xd4	# tmp123,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:57:     subfr_length = psEncC->subfr_length + psEncC->predictLPCOrder;
	add.n	a7, a4, a7	#, _2, psEncC_73(D)->subfr_length
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:63:     silk_burg_modified( &res_nrg, &res_nrg_Q, a_Q16, x, minInvGain_Q30, subfr_length, psEncC->nb_subfr, psEncC->predictLPCOrder, psEncC->arch );
	s32i.n	a4, sp, 4	#, _2
	add.n	a2, a8, a2	#,, tmp123
	addi	a4, sp, 80	#,,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:57:     subfr_length = psEncC->subfr_length + psEncC->predictLPCOrder;
	s32i	a7, sp, 264	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:63:     silk_burg_modified( &res_nrg, &res_nrg_Q, a_Q16, x, minInvGain_Q30, subfr_length, psEncC->nb_subfr, psEncC->predictLPCOrder, psEncC->arch );
	call0	silk_burg_modified_c		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:65:     if( psEncC->useInterpolatedNLSFs && !psEncC->first_frame_after_reset && psEncC->nb_subfr == MAX_NB_SUBFR ) {
	l32i.n	a2, a14, 24	# psEncC_73(D)->useInterpolatedNLSFs, psEncC_73(D)->useInterpolatedNLSFs
	bnez.n	a2, .L2	# psEncC_73(D)->useInterpolatedNLSFs,
.L5:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:144:     if( psEncC->indices.NLSFInterpCoef_Q2 == 4 ) {
	l8ui	a2, a14, 159	# psEncC_73(D)->indices.NLSFInterpCoef_Q2, tmp132
	bnei	a2, 4, .L4	# tmp132,,
	j	.L3		#
.L2:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:65:     if( psEncC->useInterpolatedNLSFs && !psEncC->first_frame_after_reset && psEncC->nb_subfr == MAX_NB_SUBFR ) {
	l32i.n	a2, a14, 56	# psEncC_73(D)->first_frame_after_reset, psEncC_73(D)->first_frame_after_reset
	bnez.n	a2, .L5	# psEncC_73(D)->first_frame_after_reset,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:65:     if( psEncC->useInterpolatedNLSFs && !psEncC->first_frame_after_reset && psEncC->nb_subfr == MAX_NB_SUBFR ) {
	l32i	a2, a13, 228	# psEncC_73(D)->nb_subfr, psEncC_73(D)->nb_subfr
	bnei	a2, 4, .L5	# psEncC_73(D)->nb_subfr,,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:69:         silk_burg_modified( &res_tmp_nrg, &res_tmp_nrg_Q, a_tmp_Q16, x + 2 * subfr_length, minInvGain_Q30, subfr_length, 2, psEncC->predictLPCOrder, psEncC->arch );
	l32i.n	a2, a14, 32	# psEncC_73(D)->predictLPCOrder, psEncC_73(D)->predictLPCOrder
	l32i	a8, sp, 264	# %sfp,
	l32i	a3, a15, 228	# psEncC_73(D)->arch, psEncC_73(D)->arch
	slli	a5, a8, 2	# tmp139,,
	s32i.n	a2, sp, 4	#, psEncC_73(D)->predictLPCOrder
	mov.n	a7, a8	#,
	movi.n	a2, 2	# tmp149,
	l32i	a8, sp, 260	# %sfp,
	addi	a4, sp, 16	#,,
	s32i.n	a3, sp, 8	#, psEncC_73(D)->arch
	s32i.n	a2, sp, 0	#, tmp149
	l32i	a6, sp, 256	# %sfp,
	movi	a3, 0xc8	# tmp141,
	movi	a2, 0xd0	# tmp143,
	add.n	a3, a4, a3	#,, tmp141
	add.n	a2, a4, a2	#,, tmp143
	add.n	a5, a8, a5	#,, tmp139
	call0	silk_burg_modified_c		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:73:         shift = res_tmp_nrg_Q - res_nrg_Q;
	l32i	a4, sp, 216	# res_tmp_nrg_Q, res_tmp_nrg_Q$0_13
	l32i	a2, sp, 220	# res_nrg_Q, res_nrg_Q$1_14
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:73:         shift = res_tmp_nrg_Q - res_nrg_Q;
	sub	a3, a4, a2	# shift, res_tmp_nrg_Q$0_13, res_nrg_Q$1_14
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:74:         if( shift >= 0 ) {
	bltz	a3, .L6	# shift,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:75:             if( shift < 32 ) {
	movi.n	a2, 0x1f	# tmp150,
	blt	a2, a3, .L7	# tmp150, shift,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:76:                 res_nrg = res_nrg - silk_RSHIFT( res_tmp_nrg, shift );
	l32i	a2, sp, 224	# res_tmp_nrg, res_tmp_nrg
	ssr	a3	# shift
	sra	a3, a2	# tmp151, res_tmp_nrg
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:76:                 res_nrg = res_nrg - silk_RSHIFT( res_tmp_nrg, shift );
	l32i	a2, sp, 228	# res_nrg, res_nrg
	sub	a2, a2, a3	# tmp153, res_nrg, tmp151
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:76:                 res_nrg = res_nrg - silk_RSHIFT( res_tmp_nrg, shift );
	s32i	a2, sp, 228	# res_nrg, tmp153
	j	.L7		#
.L6:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:80:             res_nrg   = silk_RSHIFT( res_nrg, -shift ) - res_tmp_nrg;
	l32i	a3, sp, 228	# res_nrg, res_nrg
	sub	a2, a2, a4	# tmp155, res_nrg_Q$1_14, res_tmp_nrg_Q$0_13
	ssr	a2	# tmp155
	sra	a2, a3	# tmp156, res_nrg
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:80:             res_nrg   = silk_RSHIFT( res_nrg, -shift ) - res_tmp_nrg;
	l32i	a3, sp, 224	# res_tmp_nrg, res_tmp_nrg
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:81:             res_nrg_Q = res_tmp_nrg_Q;
	s32i	a4, sp, 220	# res_nrg_Q, res_tmp_nrg_Q$0_13
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:80:             res_nrg   = silk_RSHIFT( res_nrg, -shift ) - res_tmp_nrg;
	sub	a2, a2, a3	# tmp158, tmp156, res_tmp_nrg
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:80:             res_nrg   = silk_RSHIFT( res_nrg, -shift ) - res_tmp_nrg;
	s32i	a2, sp, 228	# res_nrg, tmp158
.L7:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:85:         silk_A2NLSF( NLSF_Q15, a_tmp_Q16, psEncC->predictLPCOrder );
	l32i.n	a4, a14, 32	# psEncC_73(D)->predictLPCOrder,
	l32i	a2, sp, 268	# %sfp,
	addi	a3, sp, 16	#,,
	call0	silk_A2NLSF		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:87:         ALLOC( LPC_res, 2 * subfr_length, opus_int16 );
	l32i	a8, sp, 264	# %sfp,
	movi.n	a4, 0	#,
	slli	a8, a8, 1	#,,
	mov.n	a2, a8	#,
	movi.n	a3, 2	#,
	s32i	a8, sp, 276	# %sfp,
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a13, a2	# LPC_res,
	l32r	a2, .LC0	#, tmp161
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:95:             silk_NLSF2A( a_tmp_Q12, NLSF0_Q15, psEncC->predictLPCOrder, psEncC->arch );
	addi	a8, sp, 16	#,,
	add.n	a2, a12, a2	#, psEncC, tmp161
	s32i	a2, sp, 280	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:92:             silk_interpolate( NLSF0_Q15, psEncC->prev_NLSFq_Q15, NLSF_Q15, k, psEncC->predictLPCOrder );
	movi	a12, 0x80	# tmp163,
	addi	a2, sp, 16	#,,
	add.n	a12, a2, a12	# tmp164,, tmp163
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:95:             silk_NLSF2A( a_tmp_Q12, NLSF0_Q15, psEncC->predictLPCOrder, psEncC->arch );
	movi	a2, 0xa0	# tmp169,
	add.n	a8, a8, a2	#,, tmp169
	s32i	a12, sp, 272	# %sfp, tmp164
	l32i	a12, sp, 264	# %sfp, subfr_length
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:90:         for( k = 3; k >= 0; k-- ) {
	movi.n	a10, 3	# k,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:95:             silk_NLSF2A( a_tmp_Q12, NLSF0_Q15, psEncC->predictLPCOrder, psEncC->arch );
	s32i	a8, sp, 256	# %sfp,
.L13:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:92:             silk_interpolate( NLSF0_Q15, psEncC->prev_NLSFq_Q15, NLSF_Q15, k, psEncC->predictLPCOrder );
	l32i.n	a6, a14, 32	# psEncC_73(D)->predictLPCOrder,
	l32i	a4, sp, 268	# %sfp,
	l32i	a3, sp, 280	# %sfp,
	l32i	a2, sp, 272	# %sfp,
	mov.n	a5, a10	#, k
	s32i	a10, sp, 284	#,
	call0	silk_interpolate		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:95:             silk_NLSF2A( a_tmp_Q12, NLSF0_Q15, psEncC->predictLPCOrder, psEncC->arch );
	l32i	a5, a15, 228	# psEncC_73(D)->arch,
	l32i.n	a4, a14, 32	# psEncC_73(D)->predictLPCOrder,
	l32i	a3, sp, 272	# %sfp,
	l32i	a2, sp, 256	# %sfp,
	call0	silk_NLSF2A		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:98:             silk_LPC_analysis_filter( LPC_res, x, a_tmp_Q12, 2 * subfr_length, psEncC->predictLPCOrder, psEncC->arch );
	l32i	a7, a15, 228	# psEncC_73(D)->arch,
	l32i.n	a6, a14, 32	# psEncC_73(D)->predictLPCOrder,
	l32i	a5, sp, 276	# %sfp,
	l32i	a4, sp, 256	# %sfp,
	l32i	a3, sp, 260	# %sfp,
	mov.n	a2, a13	#, LPC_res
	call0	silk_LPC_analysis_filter		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:100:             silk_sum_sqr_shift( &res_nrg0, &rshift0, LPC_res + psEncC->predictLPCOrder,                subfr_length - psEncC->predictLPCOrder );
	l32i.n	a5, a14, 32	# psEncC_73(D)->predictLPCOrder, _33
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:100:             silk_sum_sqr_shift( &res_nrg0, &rshift0, LPC_res + psEncC->predictLPCOrder,                subfr_length - psEncC->predictLPCOrder );
	addi	a2, sp, 16	#,,
	movi	a3, 0xdc	# tmp179,
	add.n	a3, a2, a3	#,, tmp179
	addi	a6, sp, 16	#,,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:100:             silk_sum_sqr_shift( &res_nrg0, &rshift0, LPC_res + psEncC->predictLPCOrder,                subfr_length - psEncC->predictLPCOrder );
	slli	a4, a5, 1	# tmp177, _33,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:100:             silk_sum_sqr_shift( &res_nrg0, &rshift0, LPC_res + psEncC->predictLPCOrder,                subfr_length - psEncC->predictLPCOrder );
	movi	a2, 0xe4	# tmp181,
	add.n	a2, a6, a2	#,, tmp181
	sub	a5, a12, a5	#, subfr_length, _33
	add.n	a4, a13, a4	#, LPC_res, tmp177
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:101:             silk_sum_sqr_shift( &res_nrg1, &rshift1, LPC_res + psEncC->predictLPCOrder + subfr_length, subfr_length - psEncC->predictLPCOrder );
	l32i.n	a5, a14, 32	# psEncC_73(D)->predictLPCOrder, _38
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:101:             silk_sum_sqr_shift( &res_nrg1, &rshift1, LPC_res + psEncC->predictLPCOrder + subfr_length, subfr_length - psEncC->predictLPCOrder );
	addi	a8, sp, 16	#,,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:101:             silk_sum_sqr_shift( &res_nrg1, &rshift1, LPC_res + psEncC->predictLPCOrder + subfr_length, subfr_length - psEncC->predictLPCOrder );
	add.n	a4, a5, a12	# tmp185, _38, subfr_length
	slli	a4, a4, 1	# tmp186, tmp185,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:101:             silk_sum_sqr_shift( &res_nrg1, &rshift1, LPC_res + psEncC->predictLPCOrder + subfr_length, subfr_length - psEncC->predictLPCOrder );
	movi	a3, 0xd8	# tmp188,
	movi	a2, 0xe0	# tmp190,
	sub	a5, a12, a5	#, subfr_length, _38
	add.n	a4, a13, a4	#, LPC_res, tmp186
	add.n	a3, a8, a3	#,, tmp188
	add.n	a2, a8, a2	#,, tmp190
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:104:             shift = rshift0 - rshift1;
	l32i	a2, sp, 236	# rshift0, rshift0$8_45
	l32i	a3, sp, 232	# rshift1, rshift1$9_46
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:107:                 res_nrg_interp_Q = -rshift0;
	neg	a4, a2	# res_nrg_interp_Q, rshift0$8_45
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:109:                 res_nrg0         = silk_RSHIFT( res_nrg0, -shift );
	sub	a5, a3, a2	# tmp193, rshift1$9_46, rshift0$8_45
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:104:             shift = rshift0 - rshift1;
	sub	a2, a2, a3	# shift, rshift0$8_45, rshift1$9_46
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:105:             if( shift >= 0 ) {
	l32i	a10, sp, 284	#,
	bltz	a2, .L8	# shift,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:106:                 res_nrg1         = silk_RSHIFT( res_nrg1, shift );
	l32i	a3, sp, 240	# res_nrg1, res_nrg1
	l32i	a5, sp, 244	# res_nrg0, pretmp_119
	ssr	a2	# shift
	sra	a2, a3	# _48, res_nrg1
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:106:                 res_nrg1         = silk_RSHIFT( res_nrg1, shift );
	s32i	a2, sp, 240	# res_nrg1, _48
	j	.L9		#
.L8:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:109:                 res_nrg0         = silk_RSHIFT( res_nrg0, -shift );
	l32i	a4, sp, 244	# res_nrg0, res_nrg0
	l32i	a2, sp, 240	# res_nrg1, _48
	ssr	a5	# tmp193
	sra	a5, a4	# pretmp_119, res_nrg0
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:109:                 res_nrg0         = silk_RSHIFT( res_nrg0, -shift );
	s32i	a5, sp, 244	# res_nrg0, pretmp_119
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:110:                 res_nrg_interp_Q = -rshift1;
	neg	a4, a3	# res_nrg_interp_Q, rshift1$9_46
.L9:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:115:             shift = res_nrg_interp_Q - res_nrg_Q;
	l32i	a3, sp, 220	# res_nrg_Q, res_nrg_Q$16_54
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:112:             res_nrg_interp = silk_ADD32( res_nrg0, res_nrg1 );
	add.n	a2, a2, a5	# res_nrg_interp, _48, pretmp_119
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:115:             shift = res_nrg_interp_Q - res_nrg_Q;
	sub	a6, a4, a3	# shift, res_nrg_interp_Q, res_nrg_Q$16_54
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:123:                 if( -shift < 32 ) {
	movi.n	a7, 0x1f	# tmp197,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:123:                 if( -shift < 32 ) {
	sub	a3, a3, a4	# _57, res_nrg_Q$16_54, res_nrg_interp_Q
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:117:                 if( silk_RSHIFT( res_nrg_interp, shift ) < res_nrg ) {
	ssr	a6	# shift
	sra	a5, a2	# tmp195, res_nrg_interp
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:116:             if( shift >= 0 ) {
	bltz	a6, .L10	# shift,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:117:                 if( silk_RSHIFT( res_nrg_interp, shift ) < res_nrg ) {
	l32i	a3, sp, 228	# res_nrg, res_nrg
	blt	a5, a3, .L11	# tmp195, res_nrg,
	j	.L12		#
.L10:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:123:                 if( -shift < 32 ) {
	blt	a7, a3, .L12	# tmp197, _57,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:124:                     if( res_nrg_interp < silk_RSHIFT( res_nrg, -shift ) ) {
	l32i	a5, sp, 228	# res_nrg, res_nrg
	ssr	a3	# _57
	sra	a3, a5	# tmp198, res_nrg
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:124:                     if( res_nrg_interp < silk_RSHIFT( res_nrg, -shift ) ) {
	bge	a2, a3, .L12	# res_nrg_interp, tmp198,
.L11:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:139:                 psEncC->indices.NLSFInterpCoef_Q2 = (opus_int8)k;
	s8i	a10, a14, 159	# psEncC_73(D)->indices.NLSFInterpCoef_Q2, k
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:137:                 res_nrg   = res_nrg_interp;
	s32i	a2, sp, 228	# res_nrg, res_nrg_interp
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:138:                 res_nrg_Q = res_nrg_interp_Q;
	s32i	a4, sp, 220	# res_nrg_Q, res_nrg_interp_Q
.L12:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:90:         for( k = 3; k >= 0; k-- ) {
	addi.n	a10, a10, -1	# k, k,
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:90:         for( k = 3; k >= 0; k-- ) {
	bnei	a10, -1, .L13	# k,,
	j	.L5		#
.L3:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:146:         silk_A2NLSF( NLSF_Q15, a_Q16, psEncC->predictLPCOrder );
	l32i.n	a4, a14, 32	# psEncC_73(D)->predictLPCOrder,
	l32i	a2, sp, 268	# %sfp,
	addi	a3, sp, 80	#,,
	call0	silk_A2NLSF		#
.L4:
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:150:     RESTORE_STACK;
	l32i	a2, sp, 208	# _saved_stack,
	l32i	a3, sp, 212	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\fixed\find_LPC_FIX.c:151: }
	l32i	a0, sp, 316	#,
	movi	a9, 0x140	#,
	l32i	a12, sp, 312	#,
	l32i	a13, sp, 308	#,
	l32i	a14, sp, 304	#,
	l32i	a15, sp, 300	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_find_LPC_FIX, .-silk_find_LPC_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
