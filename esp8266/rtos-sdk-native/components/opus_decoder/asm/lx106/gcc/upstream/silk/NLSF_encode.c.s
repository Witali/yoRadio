# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF_encode.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF_encode.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_encode.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_encode.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_encode.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF_encode.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_encode.c.s.raw
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
	.global	__muldi3
	.section	.text.silk_NLSF_encode,"ax",@progbits
	.literal_position
	.literal .LC0, 536870911
	.literal .LC1, -2147483648
	.literal .LC2, 2147483647
	.align	4
	.global	silk_NLSF_encode
	.type	silk_NLSF_encode, @function
# Function: silk_NLSF_encode
# Module: upstream/silk/NLSF_encode.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /***********************/
# C context: /* NLSF vector encoder */
# C context: /***********************/
# C context: opus_int32 silk_NLSF_encode(                                    /* O    Returns RD value in Q25                     */
# C context: opus_int8             *NLSFIndices,                   /* I    Codebook path vector [ LPC_ORDER + 1 ]      */
# C context: opus_int16            *pNLSF_Q15,                     /* I/O  (Un)quantized NLSF vector [ LPC_ORDER ]     */
# C context: const silk_NLSF_CB_struct   *psNLSF_CB,                     /* I    Codebook object                             */
# C context: const opus_int16            *pW_Q2,                         /* I    NLSF weight vector [ LPC_ORDER ]            */
silk_NLSF_encode:
	movi	a9, 0x120	#,
	sub	sp, sp, a9	#,,
	s32i	a0, sp, 284	#,
	s32i	a7, sp, 204	# %sfp, nSurvivors
	s32i	a5, sp, 200	# %sfp, pW_Q2
	s32i	a6, sp, 184	# %sfp, NLSF_mu_Q20
	s32i	a12, sp, 280	#,
	s32i	a4, sp, 152	# %sfp, psNLSF_CB
	s32i	a13, sp, 276	#,
	s32i	a14, sp, 272	#,
	s32i	a15, sp, 268	#,
# @OPUS@\upstream\silk\NLSF_encode.c:47: {
	s32i	a3, sp, 176	# %sfp, pNLSF_Q15
	s32i	a2, sp, 212	# %sfp, NLSFIndices
# @OPUS@\upstream\silk\NLSF_encode.c:61:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i	a2, sp, 128	# _saved_stack,
# @OPUS@\upstream\silk\NLSF_encode.c:67:     silk_NLSF_stabilize( pNLSF_Q15, psNLSF_CB->deltaMin_Q15, psNLSF_CB->order );
	l32i	a2, sp, 152	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:61:     SAVE_STACK;
	s32i	a3, sp, 132	# _saved_stack,
# @OPUS@\upstream\silk\NLSF_encode.c:67:     silk_NLSF_stabilize( pNLSF_Q15, psNLSF_CB->deltaMin_Q15, psNLSF_CB->order );
	l16si	a4, a2, 2	# psNLSF_CB_105(D)->order,
	l32i.n	a3, a2, 36	# psNLSF_CB_105(D)->deltaMin_Q15,
	l32i	a2, sp, 176	# %sfp,
	call0	silk_NLSF_stabilize		#
# @OPUS@\upstream\silk\NLSF_encode.c:70:     ALLOC( err_Q24, psNLSF_CB->nVectors, opus_int32 );
	l32i	a3, sp, 152	# %sfp,
	movi.n	a4, 0	#,
	l16si	a2, a3, 0	# psNLSF_CB_105(D)->nVectors,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\NLSF_encode.c:71:     silk_NLSF_VQ( err_Q24, pNLSF_Q15, psNLSF_CB->CB1_NLSF_Q8, psNLSF_CB->CB1_Wght_Q9, psNLSF_CB->nVectors, psNLSF_CB->order );
	l32i	a4, sp, 152	# %sfp,
	l32i	a3, sp, 176	# %sfp,
	l16si	a7, a4, 2	# psNLSF_CB_105(D)->order,
	l16si	a6, a4, 0	# psNLSF_CB_105(D)->nVectors,
	l32i.n	a5, a4, 12	# psNLSF_CB_105(D)->CB1_Wght_Q9,
	l32i.n	a4, a4, 8	# psNLSF_CB_105(D)->CB1_NLSF_Q8,
# @OPUS@\upstream\silk\NLSF_encode.c:70:     ALLOC( err_Q24, psNLSF_CB->nVectors, opus_int32 );
	mov.n	a12, a2	# err_Q24,
# @OPUS@\upstream\silk\NLSF_encode.c:71:     silk_NLSF_VQ( err_Q24, pNLSF_Q15, psNLSF_CB->CB1_NLSF_Q8, psNLSF_CB->CB1_Wght_Q9, psNLSF_CB->nVectors, psNLSF_CB->order );
	call0	silk_NLSF_VQ		#
# @OPUS@\upstream\silk\NLSF_encode.c:74:     ALLOC( tempIndices1, nSurvivors, opus_int );
	l32i	a2, sp, 204	# %sfp,
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\NLSF_encode.c:75:     silk_insertion_sort_increasing( err_Q24, tempIndices1, psNLSF_CB->nVectors, nSurvivors );
	l32i	a6, sp, 152	# %sfp,
	l32i	a5, sp, 204	# %sfp,
	l16si	a4, a6, 0	# psNLSF_CB_105(D)->nVectors,
	mov.n	a3, a2	#,
# @OPUS@\upstream\silk\NLSF_encode.c:74:     ALLOC( tempIndices1, nSurvivors, opus_int );
	s32i	a2, sp, 216	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:75:     silk_insertion_sort_increasing( err_Q24, tempIndices1, psNLSF_CB->nVectors, nSurvivors );
	mov.n	a2, a12	#, err_Q24
	call0	silk_insertion_sort_increasing		#
# @OPUS@\upstream\silk\NLSF_encode.c:77:     ALLOC( RD_Q25, nSurvivors, opus_int32 );
	l32i	a2, sp, 204	# %sfp,
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\NLSF_encode.c:78:     ALLOC( tempIndices2, nSurvivors * MAX_LPC_ORDER, opus_int8 );
	l32i	a5, sp, 204	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:77:     ALLOC( RD_Q25, nSurvivors, opus_int32 );
	s32i	a2, sp, 208	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:78:     ALLOC( tempIndices2, nSurvivors * MAX_LPC_ORDER, opus_int8 );
	movi.n	a4, 0	#,
	movi.n	a3, 1	#,
	slli	a2, a5, 4	#,,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\NLSF_encode.c:81:     for( s = 0; s < nSurvivors; s++ ) {
	l32i	a6, sp, 204	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:78:     ALLOC( tempIndices2, nSurvivors * MAX_LPC_ORDER, opus_int8 );
	s32i	a2, sp, 220	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:81:     for( s = 0; s < nSurvivors; s++ ) {
	bgei	a6, 1, .L2	#,,
	addi	a2, sp, 16	#,,
	s32i	a2, sp, 180	# %sfp,
	j	.L19		#
.L2:
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	l32i	a5, sp, 184	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	l32i	a4, sp, 288	# signalType, signalType
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	slli	a3, a5, 14	# tmp252,,
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	srai	a4, a4, 1	#, signalType,
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	srai	a3, a3, 16	#, tmp252,
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	s32i	a4, sp, 188	# %sfp,
	l32i	a4, sp, 208	# %sfp,
	slli	a2, a6, 2	# tmp253,,
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	s32i	a3, sp, 192	# %sfp,
	l32i	a5, sp, 220	# %sfp,
	l32i	a3, sp, 216	# %sfp,
	add.n	a2, a2, a4	#, tmp253,
	addi	a6, sp, 16	#,,
	s32i	a3, sp, 172	# %sfp,
	s32i	a4, sp, 160	# %sfp,
	s32i	a5, sp, 168	# %sfp,
	s32i	a2, sp, 196	# %sfp,
	s32i	a6, sp, 180	# %sfp,
.L20:
# @OPUS@\upstream\silk\NLSF_encode.c:82:         ind1 = tempIndices1[ s ];
	l32i	a2, sp, 172	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:85:         pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ ind1 * psNLSF_CB->order ];
	l32i	a3, sp, 152	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:82:         ind1 = tempIndices1[ s ];
	l32i.n	a2, a2, 0	# MEM[base: _163, offset: 0B],
# @OPUS@\upstream\silk\NLSF_encode.c:86:         pCB_Wght_Q9 = &psNLSF_CB->CB1_Wght_Q9[ ind1 * psNLSF_CB->order ];
	l32i	a6, sp, 152	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:82:         ind1 = tempIndices1[ s ];
	s32i	a2, sp, 164	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:85:         pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ ind1 * psNLSF_CB->order ];
	l32i	a4, sp, 164	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:85:         pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ ind1 * psNLSF_CB->order ];
	l16si	a2, a3, 2	# psNLSF_CB_105(D)->order, _21
# @OPUS@\upstream\silk\NLSF_encode.c:85:         pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ ind1 * psNLSF_CB->order ];
	l32i.n	a5, a3, 8	# psNLSF_CB_105(D)->CB1_NLSF_Q8, _20
# @OPUS@\upstream\silk\NLSF_encode.c:85:         pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ ind1 * psNLSF_CB->order ];
	mull	a3, a2, a4	# _24, _21,
# @OPUS@\upstream\silk\NLSF_encode.c:86:         pCB_Wght_Q9 = &psNLSF_CB->CB1_Wght_Q9[ ind1 * psNLSF_CB->order ];
	l32i.n	a4, a6, 12	# psNLSF_CB_105(D)->CB1_Wght_Q9, _25
# @OPUS@\upstream\silk\NLSF_encode.c:87:         for( i = 0; i < psNLSF_CB->order; i++ ) {
	bgei	a2, 1, .L3	# _21,,
.L17:
# @OPUS@\upstream\silk\NLSF_encode.c:95:         silk_NLSF_unpack( ec_ix, pred_Q8, psNLSF_CB, ind1 );
	l32i	a5, sp, 164	# %sfp,
	l32i	a4, sp, 152	# %sfp,
	l32i	a2, sp, 180	# %sfp,
	addi	a3, sp, 112	#,,
	call0	silk_NLSF_unpack		#
# @OPUS@\upstream\silk\NLSF_encode.c:98:         RD_Q25[ s ] = silk_NLSF_del_dec_quant( &tempIndices2[ s * MAX_LPC_ORDER ], res_Q10, W_adj_Q5, pred_Q8, ec_ix,
	l32i	a2, sp, 152	# %sfp,
	l32i	a5, sp, 152	# %sfp,
	l16si	a4, a2, 2	# psNLSF_CB_105(D)->order, tmp260
	l16si	a3, a2, 6	# psNLSF_CB_105(D)->invQuantStepSize_Q6, tmp263
	l32i	a6, sp, 184	# %sfp,
	l16si	a2, a2, 4	# psNLSF_CB_105(D)->quantStepSize_Q16, tmp266
	l32i.n	a7, a5, 32	# psNLSF_CB_105(D)->ec_Rates_Q5,
	s32i.n	a6, sp, 8	#,
	s32i.n	a2, sp, 0	#, tmp266
	l32i	a6, sp, 180	# %sfp,
	l32i	a2, sp, 168	# %sfp,
	s32i.n	a4, sp, 12	#, tmp260
	s32i.n	a3, sp, 4	#, tmp263
	addi	a5, sp, 112	#,,
	addi	a4, sp, 48	#,,
	addi	a3, sp, 80	#,,
	call0	silk_NLSF_del_dec_quant		#
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	l32i	a3, sp, 152	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	l32i	a5, sp, 188	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	l16si	a4, a3, 0	# psNLSF_CB_105(D)->nVectors, tmp269
# @OPUS@\upstream\silk\NLSF_encode.c:98:         RD_Q25[ s ] = silk_NLSF_del_dec_quant( &tempIndices2[ s * MAX_LPC_ORDER ], res_Q10, W_adj_Q5, pred_Q8, ec_ix,
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	l32i.n	a3, a3, 16	# psNLSF_CB_105(D)->CB1_iCDF, psNLSF_CB_105(D)->CB1_iCDF
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	mull	a4, a4, a5	# tmp272, tmp269,
# @OPUS@\upstream\silk\NLSF_encode.c:98:         RD_Q25[ s ] = silk_NLSF_del_dec_quant( &tempIndices2[ s * MAX_LPC_ORDER ], res_Q10, W_adj_Q5, pred_Q8, ec_ix,
	s32i.n	a2, a6, 0	# MEM[base: _165, offset: 0B],
# @OPUS@\upstream\silk\NLSF_encode.c:103:         if( ind1 == 0 ) {
	l32i	a2, sp, 164	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:102:         iCDF_ptr = &psNLSF_CB->CB1_iCDF[ ( signalType >> 1 ) * psNLSF_CB->nVectors ];
	add.n	a3, a3, a4	# iCDF_ptr, psNLSF_CB_105(D)->CB1_iCDF, tmp272
# @OPUS@\upstream\silk\NLSF_encode.c:103:         if( ind1 == 0 ) {
	beqz.n	a2, .L4	#,
	j	.L26		#
.L3:
	l32i	a8, sp, 176	# %sfp, ivtmp$28
	slli	a6, a3, 1	# tmp274, _24,
	slli	a2, a2, 1	# tmp275, _21,
	add.n	a3, a5, a3	#, _20, _24
	add.n	a6, a4, a6	#, _25, tmp274
	add.n	a2, a2, a8	#, tmp275, ivtmp$28
	l32i	a10, sp, 200	# %sfp, ivtmp$30
	s32i	a3, sp, 148	# %sfp,
	s32i	a6, sp, 144	# %sfp,
	addi	a11, sp, 80	# ivtmp$29,,
	addi	a9, sp, 48	# ivtmp$31,,
	s32i	a2, sp, 156	# %sfp,
.L16:
# @OPUS@\upstream\silk\NLSF_encode.c:88:             NLSF_tmp_Q15[ i ] = silk_LSHIFT16( (opus_int16)pCB_element[ i ], 7 );
	l32i	a6, sp, 148	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:90:             res_Q10[ i ] = (opus_int16)silk_RSHIFT( silk_SMULBB( pNLSF_Q15[ i ] - NLSF_tmp_Q15[ i ], W_tmp_Q9 ), 14 );
	l16ui	a2, a8, 0	# MEM[base: _44, offset: 0B],
# @OPUS@\upstream\silk\NLSF_encode.c:88:             NLSF_tmp_Q15[ i ] = silk_LSHIFT16( (opus_int16)pCB_element[ i ], 7 );
	l8ui	a3, a6, 0	# MEM[base: _42, offset: 0B], MEM[base: _42, offset: 0B]
# @OPUS@\upstream\silk\NLSF_encode.c:89:             W_tmp_Q9 = pCB_Wght_Q9[ i ];
	l32i	a6, sp, 144	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:88:             NLSF_tmp_Q15[ i ] = silk_LSHIFT16( (opus_int16)pCB_element[ i ], 7 );
	slli	a3, a3, 7	# tmp279, MEM[base: _42, offset: 0B],
# @OPUS@\upstream\silk\NLSF_encode.c:89:             W_tmp_Q9 = pCB_Wght_Q9[ i ];
	l16si	a5, a6, 0	# MEM[base: _43, offset: 0B], _398
# @OPUS@\upstream\silk\NLSF_encode.c:90:             res_Q10[ i ] = (opus_int16)silk_RSHIFT( silk_SMULBB( pNLSF_Q15[ i ] - NLSF_tmp_Q15[ i ], W_tmp_Q9 ), 14 );
	sub	a2, a2, a3	# tmp282, MEM[base: _44, offset: 0B], tmp279
	mul16s	a2, a2, a5	# tmp283, tmp282, _398
# @OPUS@\upstream\silk\NLSF_encode.c:91:             W_adj_Q5[ i ] = silk_DIV32_varQ( (opus_int32)pW_Q2[ i ], silk_SMULBB( W_tmp_Q9, W_tmp_Q9 ), 21 );
	l16si	a12, a10, 0	# MEM[base: _152, offset: 0B], _387
# @OPUS@\upstream\silk\NLSF_encode.c:90:             res_Q10[ i ] = (opus_int16)silk_RSHIFT( silk_SMULBB( pNLSF_Q15[ i ] - NLSF_tmp_Q15[ i ], W_tmp_Q9 ), 14 );
	srai	a2, a2, 14	# tmp284, tmp283,
# @OPUS@\upstream\silk\NLSF_encode.c:90:             res_Q10[ i ] = (opus_int16)silk_RSHIFT( silk_SMULBB( pNLSF_Q15[ i ] - NLSF_tmp_Q15[ i ], W_tmp_Q9 ), 14 );
	s16i	a2, a11, 0	# MEM[base: _45, offset: 0B], tmp284
# @OPUS@\upstream\silk\NLSF_encode.c:91:             W_adj_Q5[ i ] = silk_DIV32_varQ( (opus_int32)pW_Q2[ i ], silk_SMULBB( W_tmp_Q9, W_tmp_Q9 ), 21 );
	mull	a5, a5, a5	# _385, _398, _398
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a12, .L21	# _387,
# @OPUS@\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	abs	a6, a12	# tmp287, _387
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a6, a6	# iftmp$22_379, tmp287
	addi.n	a15, a6, 8	# prephitmp_378, iftmp$22_379,
	addi.n	a3, a6, -1	# prephitmp_377, iftmp$22_379,
	j	.L6		#
.L21:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a3, 0x1f	# prephitmp_377,
	movi.n	a15, 0x28	# prephitmp_378,
	movi.n	a6, 0x20	# iftmp$22_379,
.L6:
# @OPUS@\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a3	# prephitmp_377
	sll	a12, a12	# _375, _387
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a5, .L22	# _385,
# @OPUS@\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a7, a5	# tmp288, _385
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a7, a7	# iftmp$22_365, tmp288
	addi.n	a2, a7, -1	# prephitmp_364, iftmp$22_365,
	j	.L7		#
.L22:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# prephitmp_364,
	movi.n	a7, 0x20	# iftmp$22_365,
.L7:
# @OPUS@\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a2	# prephitmp_364
	sll	a5, a5	# b32_nrm, _385
# @OPUS@\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC0	#,
	srai	a3, a5, 16	#, b32_nrm,
	s32i	a6, sp, 232	#,
	s32i	a7, sp, 228	#,
	s32i	a8, sp, 236	#,
	s32i	a9, sp, 248	#,
	s32i	a10, sp, 244	#,
	s32i	a11, sp, 240	#,
	s32i	a5, sp, 224	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp294,,
	srai	a14, a2, 16	# _350, tmp294,
	extui	a13, a12, 0, 16	# tmp295, _375,
	mull	a13, a13, a14	# tmp296, tmp295, _350
	srai	a2, a12, 16	# tmp298, _375,
	mull	a2, a2, a14	# tmp299, tmp298, _350
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a5, sp, 224	#,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a13, a13, 16	# tmp297, tmp296,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a13, a13, a2	# result, tmp297, tmp299
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a5	#, b32_nrm
	mov.n	a2, a13	#, result
	srai	a3, a13, 31	#, result,
	srai	a5, a5, 31	#, b32_nrm,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp306,,
	sub	a12, a12, a3	# a32_nrm, _375, tmp306
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a2, a12, 16	# tmp307, a32_nrm,
	extui	a12, a12, 0, 16	# tmp309, a32_nrm,
	mull	a2, a2, a14	# tmp308, tmp307, _350
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a7, sp, 228	#,
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	mull	a14, a12, a14	# tmp310, tmp309, _350
	add.n	a13, a2, a13	# _323, tmp308, result
	srai	a14, a14, 16	# tmp311, tmp310,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a15, a15, a7	# lshift, prephitmp_378, iftmp$22_365
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a14, a14, a13	# result, tmp311, _323
# @OPUS@\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a6, sp, 232	#,
	l32i	a8, sp, 236	#,
	l32i	a9, sp, 248	#,
	l32i	a10, sp, 244	#,
	l32i	a11, sp, 240	#,
	bgez	a15, .L8	# lshift,
# @OPUS@\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	movi.n	a3, -8	#,
	sub	a2, a3, a6	# tmp313,, iftmp$22_379
	l32r	a4, .LC1	#,
	l32r	a5, .LC2	#,
	add.n	a7, a2, a7	# _317, tmp313, iftmp$22_365
	ssr	a7	# _317
	sra	a2, a4	# _316,
	ssr	a7	# _317
	sra	a3, a5	# _315,
	bge	a3, a2, .L9	# _315, _316,
	blt	a2, a14, .L11	# _316, result,
	mov.n	a2, a3	# iftmp$21_309, _315
	bge	a3, a14, .L11	# iftmp$21_309, result,
	j	.L27		#
.L9:
	bge	a3, a14, .L13	# _315, result,
	mov.n	a2, a3	# iftmp$21_309, _315
	j	.L11		#
.L13:
	bge	a2, a14, .L11	# iftmp$21_309, result,
.L27:
	mov.n	a2, a14	# iftmp$21_309, result
.L11:
	ssl	a7	# _317
	sll	a2, a2	# tmp316, iftmp$21_309
	slli	a2, a2, 16	# tmp317, tmp316,
	srai	a2, a2, 16	# prephitmp_304, tmp317,
	j	.L15		#
.L8:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a6, 0x1f	#,
	movi.n	a2, 0	# prephitmp_304,
	blt	a6, a15, .L15	#, lshift,
# @OPUS@\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a15	# lshift
	sra	a14, a14	# tmp319, result
	slli	a2, a14, 16	# tmp320, tmp319,
	srai	a2, a2, 16	# prephitmp_304, tmp320,
.L15:
	l32i	a6, sp, 148	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:91:             W_adj_Q5[ i ] = silk_DIV32_varQ( (opus_int32)pW_Q2[ i ], silk_SMULBB( W_tmp_Q9, W_tmp_Q9 ), 21 );
	s16i	a2, a9, 0	# MEM[base: _153, offset: 0B], prephitmp_304
	addi.n	a6, a6, 1	#,,
	s32i	a6, sp, 148	# %sfp,
	l32i	a6, sp, 144	# %sfp,
	addi.n	a8, a8, 2	# ivtmp$28, ivtmp$28,
	addi.n	a6, a6, 2	#,,
	s32i	a6, sp, 144	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:87:         for( i = 0; i < psNLSF_CB->order; i++ ) {
	l32i	a6, sp, 156	# %sfp,
	addi.n	a11, a11, 2	# ivtmp$29, ivtmp$29,
	addi.n	a10, a10, 2	# ivtmp$30, ivtmp$30,
	addi.n	a9, a9, 2	# ivtmp$31, ivtmp$31,
	bne	a8, a6, .L16	# ivtmp$28,,
	j	.L17		#
.L4:
# @OPUS@\upstream\silk\NLSF_encode.c:104:             prob_Q8 = 256 - iCDF_ptr[ ind1 ];
	l8ui	a2, a3, 0	# *iCDF_ptr_132, *iCDF_ptr_132
# @OPUS@\upstream\silk\NLSF_encode.c:104:             prob_Q8 = 256 - iCDF_ptr[ ind1 ];
	movi	a3, 0x100	# tmp322,
# @OPUS@\upstream\silk\NLSF_encode.c:108:         bits_q7 = ( 8 << 7 ) - silk_lin2log( prob_Q8 );
	sub	a2, a3, a2	#, tmp322, *iCDF_ptr_132
	call0	silk_lin2log		#
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	l32i	a4, sp, 160	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:108:         bits_q7 = ( 8 << 7 ) - silk_lin2log( prob_Q8 );
	movi	a3, 0x400	# tmp324,
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	l32i	a5, sp, 192	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:108:         bits_q7 = ( 8 << 7 ) - silk_lin2log( prob_Q8 );
	sub	a2, a3, a2	# bits_q7, tmp324,
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	mul16s	a2, a2, a5	# tmp326, bits_q7,
	l32i.n	a3, a4, 0	# MEM[base: _165, offset: 0B], MEM[base: _165, offset: 0B]
	l32i	a6, sp, 172	# %sfp,
	add.n	a2, a3, a2	# tmp327, MEM[base: _165, offset: 0B], tmp326
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	s32i.n	a2, a4, 0	# MEM[base: _165, offset: 0B], tmp327
	l32i	a2, sp, 168	# %sfp,
	addi.n	a6, a6, 4	#,,
	addi.n	a4, a4, 4	#,,
	addi	a2, a2, 16	#,,
# @OPUS@\upstream\silk\NLSF_encode.c:81:     for( s = 0; s < nSurvivors; s++ ) {
	l32i	a3, sp, 196	# %sfp,
	s32i	a6, sp, 172	# %sfp,
	s32i	a4, sp, 160	# %sfp,
	s32i	a2, sp, 168	# %sfp,
	bne	a3, a4, .L20	#,,
	j	.L19		#
.L26:
# @OPUS@\upstream\silk\NLSF_encode.c:106:             prob_Q8 = iCDF_ptr[ ind1 - 1 ] - iCDF_ptr[ ind1 ];
	add.n	a3, a3, a2	# tmp329, iCDF_ptr, tmp4
	addi.n	a2, a3, -1	# tmp330, tmp329,
	l8ui	a4, a2, 0	# *_71, *_71
	l32i	a5, sp, 172	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:106:             prob_Q8 = iCDF_ptr[ ind1 - 1 ] - iCDF_ptr[ ind1 ];
	l8ui	a2, a3, 0	# *_74, *_74
	addi.n	a5, a5, 4	#,,
# @OPUS@\upstream\silk\NLSF_encode.c:108:         bits_q7 = ( 8 << 7 ) - silk_lin2log( prob_Q8 );
	sub	a2, a4, a2	#, *_71, *_74
	s32i	a5, sp, 172	# %sfp,
	call0	silk_lin2log		#
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:108:         bits_q7 = ( 8 << 7 ) - silk_lin2log( prob_Q8 );
	movi	a3, 0x400	# tmp335,
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	l32i	a4, sp, 192	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:108:         bits_q7 = ( 8 << 7 ) - silk_lin2log( prob_Q8 );
	sub	a2, a3, a2	# bits_q7, tmp335,
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	mul16s	a2, a2, a4	# tmp337, bits_q7,
	l32i.n	a3, a6, 0	# MEM[base: _165, offset: 0B], MEM[base: _165, offset: 0B]
	l32i	a5, sp, 168	# %sfp,
	add.n	a2, a3, a2	# tmp338, MEM[base: _165, offset: 0B], tmp337
# @OPUS@\upstream\silk\NLSF_encode.c:109:         RD_Q25[ s ] = silk_SMLABB( RD_Q25[ s ], bits_q7, silk_RSHIFT( NLSF_mu_Q20, 2 ) );
	s32i.n	a2, a6, 0	# MEM[base: _165, offset: 0B], tmp338
	addi	a5, a5, 16	#,,
	addi.n	a6, a6, 4	#,,
# @OPUS@\upstream\silk\NLSF_encode.c:81:     for( s = 0; s < nSurvivors; s++ ) {
	l32i	a2, sp, 196	# %sfp,
	s32i	a5, sp, 168	# %sfp,
	s32i	a6, sp, 160	# %sfp,
	bne	a6, a2, .L20	#,,
.L19:
# @OPUS@\upstream\silk\NLSF_encode.c:113:     silk_insertion_sort_increasing( RD_Q25, &bestIndex, nSurvivors, 1 );
	l32i	a6, sp, 180	# %sfp,
	l32i	a4, sp, 204	# %sfp,
	l32i	a2, sp, 208	# %sfp,
	addi	a3, a6, 120	#,,
	movi.n	a5, 1	#,
	call0	silk_insertion_sort_increasing		#
# @OPUS@\upstream\silk\NLSF_encode.c:115:     NLSFIndices[ 0 ] = (opus_int8)tempIndices1[ bestIndex ];
	l32i	a3, sp, 136	# bestIndex, bestIndex$13_86
# @OPUS@\upstream\silk\NLSF_encode.c:116:     silk_memcpy( &NLSFIndices[ 1 ], &tempIndices2[ bestIndex * MAX_LPC_ORDER ], psNLSF_CB->order * sizeof( opus_int8 ) );
	l32i	a4, sp, 212	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:115:     NLSFIndices[ 0 ] = (opus_int8)tempIndices1[ bestIndex ];
	l32i	a5, sp, 216	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:116:     silk_memcpy( &NLSFIndices[ 1 ], &tempIndices2[ bestIndex * MAX_LPC_ORDER ], psNLSF_CB->order * sizeof( opus_int8 ) );
	addi.n	a2, a4, 1	#,,
# @OPUS@\upstream\silk\NLSF_encode.c:115:     NLSFIndices[ 0 ] = (opus_int8)tempIndices1[ bestIndex ];
	slli	a4, a3, 2	# tmp237, bestIndex$13_86,
	add.n	a4, a5, a4	# tmp238,, tmp237
# @OPUS@\upstream\silk\NLSF_encode.c:115:     NLSFIndices[ 0 ] = (opus_int8)tempIndices1[ bestIndex ];
	l32i	a6, sp, 212	# %sfp,
	l32i.n	a4, a4, 0	# *_89, *_89
# @OPUS@\upstream\silk\NLSF_encode.c:116:     silk_memcpy( &NLSFIndices[ 1 ], &tempIndices2[ bestIndex * MAX_LPC_ORDER ], psNLSF_CB->order * sizeof( opus_int8 ) );
	l32i	a5, sp, 152	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:115:     NLSFIndices[ 0 ] = (opus_int8)tempIndices1[ bestIndex ];
	s8i	a4, a6, 0	# *NLSFIndices_140(D), *_89
# @OPUS@\upstream\silk\NLSF_encode.c:116:     silk_memcpy( &NLSFIndices[ 1 ], &tempIndices2[ bestIndex * MAX_LPC_ORDER ], psNLSF_CB->order * sizeof( opus_int8 ) );
	l32i	a6, sp, 220	# %sfp,
	l16si	a4, a5, 2	# psNLSF_CB_105(D)->order,
	slli	a3, a3, 4	# tmp244, bestIndex$13_86,
	add.n	a3, a6, a3	#,, tmp244
	call0	memcpy		#
# @OPUS@\upstream\silk\NLSF_encode.c:119:     silk_NLSF_decode( pNLSF_Q15, NLSFIndices, psNLSF_CB );
	l32i	a4, sp, 152	# %sfp,
	l32i	a3, sp, 212	# %sfp,
	l32i	a2, sp, 176	# %sfp,
	call0	silk_NLSF_decode		#
# @OPUS@\upstream\silk\NLSF_encode.c:122:     RESTORE_STACK;
	l32i	a2, sp, 128	# _saved_stack,
# @OPUS@\upstream\silk\NLSF_encode.c:121:     ret = RD_Q25[ 0 ];
	l32i	a4, sp, 208	# %sfp,
# @OPUS@\upstream\silk\NLSF_encode.c:122:     RESTORE_STACK;
	l32i	a3, sp, 132	# _saved_stack,
# @OPUS@\upstream\silk\NLSF_encode.c:121:     ret = RD_Q25[ 0 ];
	l32i.n	a12, a4, 0	# *RD_Q25_116, <retval>
# @OPUS@\upstream\silk\NLSF_encode.c:122:     RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\NLSF_encode.c:124: }
	l32i	a0, sp, 284	#,
	movi	a9, 0x120	#,
	mov.n	a2, a12	#, <retval>
	l32i	a13, sp, 276	#,
	l32i	a12, sp, 280	#,
	l32i	a14, sp, 272	#,
	l32i	a15, sp, 268	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_NLSF_encode, .-silk_NLSF_encode
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
