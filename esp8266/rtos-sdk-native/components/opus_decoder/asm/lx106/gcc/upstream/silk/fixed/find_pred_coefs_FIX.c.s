# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/find_pred_coefs_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"find_pred_coefs_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_pred_coefs_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_pred_coefs_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_pred_coefs_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_pred_coefs_FIX.c.s.raw
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
	.global	__udivsi3
	.section	.text.silk_find_pred_coefs_FIX,"ax",@progbits
	.literal_position
	.literal .LC0, 10737418
	.literal .LC1, 33554431
	.literal .LC2, 536870911
	.literal .LC3, 65536
	.literal .LC4, -2147483648
	.literal .LC5, 2147483647
	.literal .LC6, 4656
	.literal .LC7, 4768
	.literal .LC8, 4740
	.literal .LC9, 10000
	.literal .LC10, 4500
	.align	4
	.global	silk_find_pred_coefs_FIX
	.type	silk_find_pred_coefs_FIX, @function
# Function: silk_find_pred_coefs_FIX
# Module: upstream/silk/fixed/find_pred_coefs_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main_FIX.h"
# C context: #include "stack_alloc.h"
# C context:
# C context: void silk_find_pred_coefs_FIX(
# C context: silk_encoder_state_FIX          *psEnc,                                 /* I/O  encoder state                                                               */
# C context: silk_encoder_control_FIX        *psEncCtrl,                             /* I/O  encoder control                                                             */
# C context: const opus_int16                res_pitch[],                            /* I    Residual from pitch analysis                                                */
# C context: const opus_int16                x[],                                    /* I    Speech signal                                                               */
silk_find_pred_coefs_FIX:
	movi	a9, 0xc0	#,
	sub	sp, sp, a9	#,,
	s32i	a2, sp, 104	# %sfp, psEnc
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:46:     opus_int16       NLSF_Q15[ MAX_LPC_ORDER ]={0};
	movi.n	a2, 0	# tmp398,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:42: {
	s32i	a12, sp, 184	#,
	s32i	a0, sp, 188	#,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	addmi	a12, a8, 0x1100	# tmp821,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:42: {
	s32i	a13, sp, 180	#,
	s32i	a14, sp, 176	#,
	s32i	a15, sp, 172	#,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:42: {
	s32i	a3, sp, 100	# %sfp, psEncCtrl
	s32i	a4, sp, 120	# %sfp, res_pitch
	s32i	a5, sp, 116	# %sfp, x
	s32i	a6, sp, 124	# %sfp, condCoding
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:46:     opus_int16       NLSF_Q15[ MAX_LPC_ORDER ]={0};
	s32i.n	a2, sp, 16	# NLSF_Q15, tmp398
	s32i.n	a2, sp, 20	# NLSF_Q15, tmp398
	s32i.n	a2, sp, 24	# NLSF_Q15, tmp398
	s32i.n	a2, sp, 28	# NLSF_Q15, tmp398
	s32i.n	a2, sp, 32	# NLSF_Q15, tmp398
	s32i.n	a2, sp, 36	# NLSF_Q15, tmp398
	s32i.n	a2, sp, 40	# NLSF_Q15, tmp398
	s32i.n	a2, sp, 44	# NLSF_Q15, tmp398
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:51:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a7, a12, 228	# psEnc_106(D)->sCmn.nb_subfr,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:51:     SAVE_STACK;
	s32i	a2, sp, 80	# _saved_stack,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	s32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:51:     SAVE_STACK;
	s32i	a3, sp, 84	# _saved_stack,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	bgei	a7, 1, .L2	#,,
.L23:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:74:     ALLOC( LPC_in_pre,
	l32i	a8, sp, 104	# %sfp,
	l32i	a7, sp, 96	# %sfp,
	addmi	a13, a8, 0x1200	# tmp820,,
	l32i.n	a2, a13, 32	# psEnc_106(D)->sCmn.predictLPCOrder, psEnc_106(D)->sCmn.predictLPCOrder
	l32i	a5, a12, 232	# psEnc_106(D)->sCmn.frame_length, psEnc_106(D)->sCmn.frame_length
	mull	a2, a7, a2	# tmp409,, psEnc_106(D)->sCmn.predictLPCOrder
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	add.n	a2, a2, a5	#, tmp409, psEnc_106(D)->sCmn.frame_length
	call0	yoradio_opus_scratch_alloc		#
	l32i	a8, sp, 100	# %sfp,
	s32i	a2, sp, 108	# %sfp,
	addi	a8, a8, 80	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:77:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	l8ui	a2, a13, 157	# psEnc_106(D)->sCmn.indices.signalType, tmp415
	s32i	a8, sp, 112	# %sfp,
	bnei	a2, 2, .L109	# tmp415,,
	j	.L3		#
.L2:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:56:         min_gain_Q16 = silk_min( min_gain_Q16, psEncCtrl->Gains_Q16[ i ] );
	l32i	a8, sp, 100	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:56:         min_gain_Q16 = silk_min( min_gain_Q16, psEncCtrl->Gains_Q16[ i ] );
	l32r	a2, .LC1	#, tmp422
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:56:         min_gain_Q16 = silk_min( min_gain_Q16, psEncCtrl->Gains_Q16[ i ] );
	l32i.n	a5, a8, 0	# psEncCtrl_107(D)->Gains_Q16, _302
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:56:         min_gain_Q16 = silk_min( min_gain_Q16, psEncCtrl->Gains_Q16[ i ] );
	mov.n	a13, a5	# min_gain_Q16, _302
	bge	a2, a5, .L5	# tmp422, _302,
	mov.n	a13, a2	# min_gain_Q16, tmp422
.L5:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a7, sp, 96	# %sfp,
	beqi	a7, 1, .L6	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:56:         min_gain_Q16 = silk_min( min_gain_Q16, psEncCtrl->Gains_Q16[ i ] );
	l32i	a8, sp, 100	# %sfp,
	l32i.n	a2, a8, 4	# psEncCtrl_107(D)->Gains_Q16, psEncCtrl_107(D)->Gains_Q16
	bge	a2, a13, .L7	# psEncCtrl_107(D)->Gains_Q16, min_gain_Q16,
	mov.n	a13, a2	# min_gain_Q16, psEncCtrl_107(D)->Gains_Q16
.L7:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a7, sp, 96	# %sfp,
	beqi	a7, 2, .L6	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:56:         min_gain_Q16 = silk_min( min_gain_Q16, psEncCtrl->Gains_Q16[ i ] );
	l32i	a8, sp, 100	# %sfp,
	l32i.n	a2, a8, 8	# psEncCtrl_107(D)->Gains_Q16, psEncCtrl_107(D)->Gains_Q16
	bge	a2, a13, .L8	# psEncCtrl_107(D)->Gains_Q16, min_gain_Q16,
	mov.n	a13, a2	# min_gain_Q16, psEncCtrl_107(D)->Gains_Q16
.L8:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:55:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a7, sp, 96	# %sfp,
	beqi	a7, 3, .L6	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:56:         min_gain_Q16 = silk_min( min_gain_Q16, psEncCtrl->Gains_Q16[ i ] );
	l32i	a8, sp, 100	# %sfp,
	l32i.n	a2, a8, 12	# psEncCtrl_107(D)->Gains_Q16, psEncCtrl_107(D)->Gains_Q16
	bge	a2, a13, .L6	# psEncCtrl_107(D)->Gains_Q16, min_gain_Q16,
	mov.n	a13, a2	# min_gain_Q16, psEncCtrl_107(D)->Gains_Q16
.L6:
	abs	a7, a13	#, min_gain_Q16
	s32i	a7, sp, 108	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a13, .L75	# min_gain_Q16,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a8, a7	# iftmp$6_524,
	addi.n	a9, a8, 15	# _525, iftmp$6_524,
	addi.n	a14, a8, -1	# _526, iftmp$6_524,
	j	.L10		#
.L75:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a14, 0x1f	# _526,
	movi.n	a9, 0x2f	# _525,
	movi.n	a8, 0x20	# iftmp$6_524,
.L10:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a14	# _526
	sll	a14, a13	# _530, min_gain_Q16
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a5, .L76	# _302,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a7, a5	# tmp426, _302
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a7, a7	# iftmp$6_534, tmp426
	addi.n	a2, a7, -1	# prephitmp_281, iftmp$6_534,
	j	.L11		#
.L76:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# prephitmp_281,
	movi.n	a7, 0x20	# iftmp$6_534,
.L11:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a2	# prephitmp_281
	sll	a5, a5	# b32_nrm, _302
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC2	#,
	srai	a3, a5, 16	#, b32_nrm,
	s32i	a7, sp, 136	#,
	s32i	a8, sp, 144	#,
	s32i	a9, sp, 132	#,
	s32i	a5, sp, 128	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp432,,
	srai	a6, a2, 16	# _510, tmp432,
	extui	a15, a14, 0, 16	# tmp433, _530,
	mull	a15, a15, a6	# tmp434, tmp433, _510
	srai	a2, a14, 16	# tmp436, _530,
	mull	a2, a2, a6	# tmp437, tmp436, _510
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a5, sp, 128	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a15, a15, 16	# tmp435, tmp434,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a15, a15, a2	# result, tmp435, tmp437
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a5	#, b32_nrm
	mov.n	a2, a15	#, result
	srai	a3, a15, 31	#, result,
	srai	a5, a5, 31	#, b32_nrm,
	s32i	a6, sp, 140	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp444,,
	sub	a14, a14, a3	# a32_nrm, _530, tmp444
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a6, sp, 140	#,
	srai	a2, a14, 16	# tmp445, a32_nrm,
	extui	a14, a14, 0, 16	# tmp447, a32_nrm,
	mull	a2, a2, a6	# tmp446, tmp445, _510
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a7, sp, 136	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	mull	a6, a14, a6	# tmp448, tmp447, _510
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a9, sp, 132	#,
	add.n	a15, a2, a15	# _491, tmp446, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a6, a6, 16	# tmp449, tmp448,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a9, a9, a7	# lshift, _525, iftmp$6_534
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a15, a6, a15	# result, tmp449, _491
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a8, sp, 144	#,
	bltz	a9, .L12	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a2, 0x1f	# tmp450,
	blt	a2, a9, .L77	# tmp450, lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a9	# lshift
	sra	a15, a15	# prephitmp_459, result
	movi	a2, 0x64	# tmp455,
	bge	a15, a2, .L17	# prephitmp_459, tmp455,
	j	.L120		#
.L12:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a7, a7, a8	# tmp463, iftmp$6_534, iftmp$6_524
	l32r	a3, .LC4	#, tmp464
	l32r	a2, .LC5	#, tmp465
	addi	a6, a7, -15	# _484, tmp463,
	ssr	a6	# _484
	sra	a3, a3	# _479, tmp464
	ssr	a6	# _484
	sra	a2, a2	# _478, tmp465
	blt	a2, a3, .L15	# _478, _479,
	j	.L110		#
.L20:
	ssl	a6	# _484
	sll	a15, a9	# prephitmp_459, iftmp$5_464
	movi	a2, 0x64	# tmp470,
	bge	a15, a2, .L17	# prephitmp_459, tmp470,
.L120:
	mov.n	a15, a2	# prephitmp_459, tmp470
.L17:
	l32r	a2, .LC3	#,
	mov.n	a3, a15	#, prephitmp_459
	call0	__divsi3		#
	j	.L13		#
.L110:
	mov.n	a9, a2	# iftmp$5_464, _478
	blt	a2, a15, .L20	# iftmp$5_464, result,
	mov.n	a9, a3	# iftmp$5_464, _479
	bge	a3, a15, .L20	# iftmp$5_464, result,
	j	.L113		#
.L15:
	mov.n	a9, a3	# iftmp$5_464, _479
	blt	a3, a15, .L20	# iftmp$5_464, result,
	mov.n	a9, a2	# iftmp$5_464, _478
	bge	a2, a15, .L20	# iftmp$5_464, result,
.L113:
	mov.n	a9, a15	# iftmp$5_464, result
	j	.L20		#
.L77:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi	a2, 0x28f	# prephitmp_458,
	movi	a15, 0x64	# prephitmp_459,
.L13:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:58:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a8, sp, 96	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:65:         invGains_Q16[ i ] = silk_max( invGains_Q16[ i ], 100 );
	s32i	a15, sp, 64	# invGains_Q16, prephitmp_459
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:71:         local_gains[ i ] = silk_DIV32( ( (opus_int32)1 << 16 ), invGains_Q16[ i ] );
	s32i.n	a2, sp, 48	# local_gains, prephitmp_458
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:58:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	beqi	a8, 1, .L23	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:62:         invGains_Q16[ i ] = silk_DIV32_varQ( min_gain_Q16, psEncCtrl->Gains_Q16[ i ], 16 - 2 );
	l32i	a8, sp, 100	# %sfp,
	l32i.n	a5, a8, 4	# psEncCtrl_107(D)->Gains_Q16, _452
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a13, .L78	# min_gain_Q16,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	l32i	a7, sp, 108	# %sfp,
	nsau	a6, a7	# iftmp$6_447,
	addi.n	a8, a6, 15	#, iftmp$6_447,
	s32i	a8, sp, 112	# %sfp,
	addi.n	a3, a6, -1	# prephitmp_445, iftmp$6_447,
	j	.L24		#
.L78:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a7, 0x2f	#,
	movi.n	a3, 0x1f	# prephitmp_445,
	s32i	a7, sp, 112	# %sfp,
	movi.n	a6, 0x20	# iftmp$6_447,
.L24:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a3	# prephitmp_445
	sll	a14, a13	# _444, min_gain_Q16
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a5, .L79	# _452,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a15, a5	# tmp477, _452
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a15, a15	# iftmp$6_436, tmp477
	addi.n	a2, a15, -1	# prephitmp_435, iftmp$6_436,
	j	.L25		#
.L79:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# prephitmp_435,
	movi.n	a15, 0x20	# iftmp$6_436,
.L25:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a2	# prephitmp_435
	sll	a5, a5	# b32_nrm, _452
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC2	#,
	srai	a3, a5, 16	#, b32_nrm,
	s32i	a6, sp, 140	#,
	s32i	a5, sp, 128	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp483,,
	srai	a8, a2, 16	# _427, tmp483,
	extui	a7, a14, 0, 16	# tmp484, _444,
	mull	a7, a7, a8	# tmp485, tmp484, _427
	srai	a3, a14, 16	# tmp487, _444,
	mull	a3, a3, a8	# tmp488, tmp487, _427
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a5, sp, 128	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a7, a7, 16	# tmp486, tmp485,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a7, a3	# result, tmp486, tmp488
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a5	#, b32_nrm
	mov.n	a2, a7	#, result
	srai	a3, a7, 31	#, result,
	srai	a5, a5, 31	#, b32_nrm,
	s32i	a7, sp, 136	#,
	s32i	a8, sp, 144	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp495,,
	sub	a3, a14, a3	# a32_nrm, _444, tmp495
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a8, sp, 144	#,
	srai	a2, a3, 16	# tmp496, a32_nrm,
	extui	a3, a3, 0, 16	# tmp498, a32_nrm,
	mull	a2, a2, a8	# tmp497, tmp496, _427
	mull	a3, a3, a8	# tmp499, tmp498, _427
	l32i	a7, sp, 136	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a8, sp, 112	# %sfp,
	add.n	a7, a2, a7	# _408, tmp497, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a3, a3, 16	# tmp500, tmp499,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a14, a8, a15	# lshift,, iftmp$6_436
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a3, a7	# result, tmp500, _408
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a6, sp, 140	#,
	bltz	a14, .L26	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a2, 0x1f	# tmp501,
	blt	a2, a14, .L80	# tmp501, lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a14	# lshift
	sra	a14, a7	# prephitmp_379, result
	movi	a2, 0x64	# tmp506,
	bge	a14, a2, .L31	# prephitmp_379, tmp506,
	j	.L121		#
.L26:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a14, a15, a6	# tmp514, iftmp$6_436, iftmp$6_447
	l32r	a3, .LC4	#, tmp515
	l32r	a2, .LC5	#, tmp516
	addi	a14, a14, -15	# _393, tmp514,
	ssr	a14	# _393
	sra	a3, a3	# _392, tmp515
	ssr	a14	# _393
	sra	a2, a2	# _391, tmp516
	blt	a2, a3, .L29	# _391, _392,
	j	.L111		#
.L34:
	ssl	a14	# _393
	sll	a14, a4	# prephitmp_379, iftmp$5_384
	movi	a2, 0x64	# tmp521,
	bge	a14, a2, .L31	# prephitmp_379, tmp521,
.L121:
	mov.n	a14, a2	# prephitmp_379, tmp521
.L31:
	l32r	a2, .LC3	#,
	mov.n	a3, a14	#, prephitmp_379
	call0	__divsi3		#
	j	.L27		#
.L111:
	mov.n	a4, a2	# iftmp$5_384, _391
	blt	a2, a7, .L34	# iftmp$5_384, result,
	mov.n	a4, a3	# iftmp$5_384, _392
	bge	a3, a7, .L34	# iftmp$5_384, result,
	j	.L114		#
.L29:
	mov.n	a4, a3	# iftmp$5_384, _392
	blt	a3, a7, .L34	# iftmp$5_384, result,
	mov.n	a4, a2	# iftmp$5_384, _391
	bge	a2, a7, .L34	# iftmp$5_384, result,
.L114:
	mov.n	a4, a7	# iftmp$5_384, result
	j	.L34		#
.L80:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi	a2, 0x28f	# prephitmp_378,
	movi	a14, 0x64	# prephitmp_379,
.L27:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:58:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:65:         invGains_Q16[ i ] = silk_max( invGains_Q16[ i ], 100 );
	s32i	a14, sp, 68	# invGains_Q16, prephitmp_379
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:71:         local_gains[ i ] = silk_DIV32( ( (opus_int32)1 << 16 ), invGains_Q16[ i ] );
	s32i.n	a2, sp, 52	# local_gains, prephitmp_378
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:58:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	beqi	a7, 2, .L23	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:62:         invGains_Q16[ i ] = silk_DIV32_varQ( min_gain_Q16, psEncCtrl->Gains_Q16[ i ], 16 - 2 );
	l32i	a8, sp, 100	# %sfp,
	l32i.n	a5, a8, 8	# psEncCtrl_107(D)->Gains_Q16, _372
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a13, .L81	# min_gain_Q16,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	l32i	a7, sp, 108	# %sfp,
	nsau	a6, a7	# iftmp$6_367,
	addi.n	a8, a6, 15	#, iftmp$6_367,
	s32i	a8, sp, 112	# %sfp,
	addi.n	a3, a6, -1	# prephitmp_365, iftmp$6_367,
	j	.L37		#
.L81:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a7, 0x2f	#,
	movi.n	a3, 0x1f	# prephitmp_365,
	s32i	a7, sp, 112	# %sfp,
	movi.n	a6, 0x20	# iftmp$6_367,
.L37:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a3	# prephitmp_365
	sll	a14, a13	# _364, min_gain_Q16
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a5, .L82	# _372,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a15, a5	# tmp528, _372
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a15, a15	# iftmp$6_358, tmp528
	addi.n	a2, a15, -1	# prephitmp_357, iftmp$6_358,
	j	.L38		#
.L82:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# prephitmp_357,
	movi.n	a15, 0x20	# iftmp$6_358,
.L38:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a2	# prephitmp_357
	sll	a5, a5	# b32_nrm, _372
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC2	#,
	srai	a3, a5, 16	#, b32_nrm,
	s32i	a6, sp, 140	#,
	s32i	a5, sp, 128	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp534,,
	srai	a8, a2, 16	# _349, tmp534,
	extui	a7, a14, 0, 16	# tmp535, _364,
	mull	a7, a7, a8	# tmp536, tmp535, _349
	srai	a3, a14, 16	# tmp538, _364,
	mull	a3, a3, a8	# tmp539, tmp538, _349
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a5, sp, 128	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a7, a7, 16	# tmp537, tmp536,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a7, a3	# result, tmp537, tmp539
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a5	#, b32_nrm
	mov.n	a2, a7	#, result
	srai	a3, a7, 31	#, result,
	srai	a5, a5, 31	#, b32_nrm,
	s32i	a7, sp, 136	#,
	s32i	a8, sp, 144	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp546,,
	sub	a3, a14, a3	# a32_nrm, _364, tmp546
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a8, sp, 144	#,
	srai	a2, a3, 16	# tmp547, a32_nrm,
	extui	a3, a3, 0, 16	# tmp549, a32_nrm,
	mull	a2, a2, a8	# tmp548, tmp547, _349
	mull	a3, a3, a8	# tmp550, tmp549, _349
	l32i	a7, sp, 136	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a8, sp, 112	# %sfp,
	add.n	a7, a2, a7	# _330, tmp548, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a3, a3, 16	# tmp551, tmp550,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a14, a8, a15	# lshift,, iftmp$6_358
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a3, a7	# result, tmp551, _330
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a6, sp, 140	#,
	bltz	a14, .L39	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a2, 0x1f	# tmp552,
	blt	a2, a14, .L83	# tmp552, lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a14	# lshift
	sra	a14, a7	# prephitmp_309, result
	movi	a2, 0x64	# tmp557,
	bge	a14, a2, .L44	# prephitmp_309, tmp557,
	j	.L122		#
.L39:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a14, a15, a6	# tmp565, iftmp$6_358, iftmp$6_367
	l32r	a3, .LC4	#, tmp566
	l32r	a2, .LC5	#, tmp567
	addi	a14, a14, -15	# _323, tmp565,
	ssr	a14	# _323
	sra	a3, a3	# _322, tmp566
	ssr	a14	# _323
	sra	a2, a2	# _321, tmp567
	blt	a2, a3, .L42	# _321, _322,
	j	.L112		#
.L47:
	ssl	a14	# _323
	sll	a14, a4	# prephitmp_309, iftmp$5_314
	movi	a2, 0x64	# tmp572,
	bge	a14, a2, .L44	# prephitmp_309, tmp572,
.L122:
	mov.n	a14, a2	# prephitmp_309, tmp572
.L44:
	l32r	a2, .LC3	#,
	mov.n	a3, a14	#, prephitmp_309
	call0	__divsi3		#
	j	.L40		#
.L112:
	mov.n	a4, a2	# iftmp$5_314, _321
	blt	a2, a7, .L47	# iftmp$5_314, result,
	mov.n	a4, a3	# iftmp$5_314, _322
	bge	a3, a7, .L47	# iftmp$5_314, result,
	j	.L115		#
.L42:
	mov.n	a4, a3	# iftmp$5_314, _322
	blt	a3, a7, .L47	# iftmp$5_314, result,
	mov.n	a4, a2	# iftmp$5_314, _321
	bge	a2, a7, .L47	# iftmp$5_314, result,
.L115:
	mov.n	a4, a7	# iftmp$5_314, result
	j	.L47		#
.L83:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi	a2, 0x28f	# prephitmp_308,
	movi	a14, 0x64	# prephitmp_309,
.L40:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:58:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:65:         invGains_Q16[ i ] = silk_max( invGains_Q16[ i ], 100 );
	s32i	a14, sp, 72	# invGains_Q16, prephitmp_309
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:71:         local_gains[ i ] = silk_DIV32( ( (opus_int32)1 << 16 ), invGains_Q16[ i ] );
	s32i.n	a2, sp, 56	# local_gains, prephitmp_308
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:58:     for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	beqi	a7, 3, .L23	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:62:         invGains_Q16[ i ] = silk_DIV32_varQ( min_gain_Q16, psEncCtrl->Gains_Q16[ i ], 16 - 2 );
	l32i	a8, sp, 100	# %sfp,
	l32i.n	a6, a8, 12	# psEncCtrl_107(D)->Gains_Q16, _3
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a13, .L84	# min_gain_Q16,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	l32i	a7, sp, 108	# %sfp,
	nsau	a15, a7	# iftmp$6_148,
	addi.n	a9, a15, 15	# _399, iftmp$6_148,
	addi.n	a3, a15, -1	# _401, iftmp$6_148,
	j	.L50		#
.L84:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a3, 0x1f	# _401,
	movi.n	a9, 0x2f	# _399,
	movi.n	a15, 0x20	# iftmp$6_148,
.L50:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a3	# _401
	sll	a13, a13	# _152, min_gain_Q16
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a6, .L85	# _3,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a8, a6	# tmp579, _3
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a8, a8	# iftmp$6_156, tmp579
	addi.n	a2, a8, -1	# _439, iftmp$6_156,
	j	.L51		#
.L85:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# _439,
	movi.n	a8, 0x20	# iftmp$6_156,
.L51:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a2	# _439
	sll	a6, a6	# b32_nrm, _3
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC2	#,
	srai	a3, a6, 16	#, b32_nrm,
	s32i	a8, sp, 144	#,
	s32i	a9, sp, 132	#,
	s32i	a6, sp, 140	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp585,,
	srai	a7, a2, 16	# _166, tmp585,
	extui	a14, a13, 0, 16	# tmp586, _152,
	mull	a14, a14, a7	# tmp587, tmp586, _166
	srai	a2, a13, 16	# tmp589, _152,
	mull	a2, a2, a7	# tmp590, tmp589, _166
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a6, sp, 140	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a14, a14, 16	# tmp588, tmp587,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a14, a14, a2	# result, tmp588, tmp590
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a14	#, result
	srai	a5, a14, 31	#, result,
	mov.n	a2, a6	#, b32_nrm
	srai	a3, a6, 31	#, b32_nrm,
	s32i	a7, sp, 136	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp597,,
	sub	a13, a13, a3	# a32_nrm, _152, tmp597
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a7, sp, 136	#,
	srai	a2, a13, 16	# tmp598, a32_nrm,
	extui	a13, a13, 0, 16	# tmp600, a32_nrm,
	mull	a2, a2, a7	# tmp599, tmp598, _166
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a8, sp, 144	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	mull	a7, a13, a7	# tmp601, tmp600, _166
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a9, sp, 132	#,
	add.n	a14, a2, a14	# _7, tmp599, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a7, a7, 16	# tmp602, tmp601,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a9, a9, a8	# lshift, _399, iftmp$6_156
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a14, a7, a14	# result, tmp602, _7
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	bgez	a9, .L52	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a15, a8, a15	# tmp604, iftmp$6_156, iftmp$6_148
	l32r	a2, .LC4	#, tmp605
	l32r	a3, .LC5	#, tmp606
	addi	a7, a15, -15	# _192, tmp604,
	ssr	a7	# _192
	sra	a2, a2	# _193, tmp605
	ssr	a7	# _192
	sra	a3, a3	# _194, tmp606
	bge	a3, a2, .L53	# _194, _193,
	bge	a2, a14, .L54	# _193, result,
	j	.L116		#
.L54:
	bge	a14, a3, .L55	# iftmp$4_195, _194,
	j	.L117		#
.L53:
	bge	a3, a14, .L57	# _194, result,
.L117:
	mov.n	a14, a3	# iftmp$4_195, _194
	j	.L55		#
.L57:
	bge	a14, a2, .L55	# iftmp$4_195, _193,
.L116:
	mov.n	a14, a2	# iftmp$4_195, _193
.L55:
	ssl	a7	# _192
	sll	a14, a14	# _467, iftmp$4_195
	movi	a2, 0x64	# tmp611,
	bge	a14, a2, .L61	# _467, tmp611,
	j	.L123		#
.L52:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a2, 0x1f	# tmp618,
	blt	a2, a9, .L86	# tmp618, lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a9	# lshift
	sra	a14, a14	# _467, result
	movi	a2, 0x64	# tmp623,
	bge	a14, a2, .L61	# _467, tmp623,
.L123:
	mov.n	a14, a2	# _467, tmp623
.L61:
	l32r	a2, .LC3	#,
	mov.n	a3, a14	#, _467
	call0	__divsi3		#
	j	.L60		#
.L86:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi	a2, 0x28f	# _470,
	movi	a14, 0x64	# _467,
.L60:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:65:         invGains_Q16[ i ] = silk_max( invGains_Q16[ i ], 100 );
	s32i	a14, sp, 76	# invGains_Q16, _467
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:71:         local_gains[ i ] = silk_DIV32( ( (opus_int32)1 << 16 ), invGains_Q16[ i ] );
	s32i.n	a2, sp, 60	# local_gains, _470
	j	.L23		#
.L3:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:86:         ALLOC( xXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER, opus_int32 );
	l32i	a2, a12, 228	# psEnc_106(D)->sCmn.nb_subfr, psEnc_106(D)->sCmn.nb_subfr
	movi.n	a4, 0	#,
	slli	a5, a2, 2	# tmp633, psEnc_106(D)->sCmn.nb_subfr,
	movi.n	a3, 4	#,
	add.n	a2, a5, a2	#, tmp633, psEnc_106(D)->sCmn.nb_subfr
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:87:         ALLOC( XXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER * LTP_ORDER, opus_int32 );
	l32i	a3, a12, 228	# psEnc_106(D)->sCmn.nb_subfr, psEnc_106(D)->sCmn.nb_subfr
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:86:         ALLOC( xXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER, opus_int32 );
	mov.n	a15, a2	# xXLTP_Q17,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:87:         ALLOC( XXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER * LTP_ORDER, opus_int32 );
	slli	a2, a3, 2	# tmp638, psEnc_106(D)->sCmn.nb_subfr,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:90:         silk_find_LTP_FIX( XXLTP_Q17, xXLTP_Q17, res_pitch,
	l32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:87:         ALLOC( XXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER * LTP_ORDER, opus_int32 );
	add.n	a2, a2, a3	# tmp639, tmp638, psEnc_106(D)->sCmn.nb_subfr
	slli	a5, a2, 2	# tmp640, tmp639,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:90:         silk_find_LTP_FIX( XXLTP_Q17, xXLTP_Q17, res_pitch,
	addmi	a8, a8, 0x1300	#,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:87:         ALLOC( XXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER * LTP_ORDER, opus_int32 );
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	add.n	a2, a2, a5	#, tmp639, tmp640
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:90:         silk_find_LTP_FIX( XXLTP_Q17, xXLTP_Q17, res_pitch,
	s32i	a8, sp, 96	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:87:         ALLOC( XXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER * LTP_ORDER, opus_int32 );
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:90:         silk_find_LTP_FIX( XXLTP_Q17, xXLTP_Q17, res_pitch,
	l32i	a8, sp, 96	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:87:         ALLOC( XXLTP_Q17, psEnc->sCmn.nb_subfr * LTP_ORDER * LTP_ORDER, opus_int32 );
	mov.n	a9, a2	# XXLTP_Q17,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:91:             psEncCtrl->pitchL, psEnc->sCmn.subfr_length, psEnc->sCmn.nb_subfr, psEnc->sCmn.arch );
	l32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:90:         silk_find_LTP_FIX( XXLTP_Q17, xXLTP_Q17, res_pitch,
	l32i	a10, a8, 228	# psEnc_106(D)->sCmn.arch, psEnc_106(D)->sCmn.arch
	l32i	a7, a12, 228	# psEnc_106(D)->sCmn.nb_subfr,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:91:             psEncCtrl->pitchL, psEnc->sCmn.subfr_length, psEnc->sCmn.nb_subfr, psEnc->sCmn.arch );
	addi	a8, a2, 124	# _21,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:90:         silk_find_LTP_FIX( XXLTP_Q17, xXLTP_Q17, res_pitch,
	l32i	a6, a12, 236	# psEnc_106(D)->sCmn.subfr_length,
	l32i	a4, sp, 120	# %sfp,
	s32i.n	a10, sp, 0	#, psEnc_106(D)->sCmn.arch
	mov.n	a5, a8	#, _21
	mov.n	a3, a15	#, xXLTP_Q17
	mov.n	a2, a9	#, XXLTP_Q17
	mov.n	a14, a8	# _21, _21
	s32i	a9, sp, 132	#,
	call0	silk_find_LTP_FIX		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:94:         silk_quant_LTP_gains( psEncCtrl->LTPCoef_Q14, psEnc->sCmn.indices.LTPIndex, &psEnc->sCmn.indices.PERIndex,
	l32i	a8, sp, 96	# %sfp,
	l32i	a3, a12, 228	# psEnc_106(D)->sCmn.nb_subfr, psEnc_106(D)->sCmn.nb_subfr
	l32i	a4, a8, 228	# psEnc_106(D)->sCmn.arch, psEnc_106(D)->sCmn.arch
	l32i	a8, sp, 100	# %sfp,
	l32i	a2, a12, 236	# psEnc_106(D)->sCmn.subfr_length, psEnc_106(D)->sCmn.subfr_length
	movi	a6, 0x18c	# tmp646,
	l32i	a9, sp, 132	#,
	add.n	a6, a8, a6	#,, tmp646
	s32i.n	a4, sp, 12	#, psEnc_106(D)->sCmn.arch
	l32i	a8, sp, 104	# %sfp,
	s32i.n	a3, sp, 8	#, psEnc_106(D)->sCmn.nb_subfr
	l32r	a5, .LC6	#, tmp649
	l32r	a4, .LC7	#, tmp651
	l32r	a3, .LC8	#, tmp653
	s32i.n	a2, sp, 4	#, psEnc_106(D)->sCmn.subfr_length
	l32i	a2, sp, 112	# %sfp,
	mov.n	a7, a9	#, XXLTP_Q17
	add.n	a5, a8, a5	#,, tmp649
	add.n	a4, a8, a4	#,, tmp651
	add.n	a3, a8, a3	#,, tmp653
	s32i.n	a15, sp, 0	#, xXLTP_Q17
	call0	silk_quant_LTP_gains		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:98:         silk_LTP_scale_ctrl_FIX( psEnc, psEncCtrl, condCoding );
	l32i	a4, sp, 124	# %sfp,
	l32i	a3, sp, 100	# %sfp,
	l32i	a2, sp, 104	# %sfp,
	call0	silk_LTP_scale_ctrl_FIX		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:101:         silk_LTP_analysis_filter_FIX( LPC_in_pre, x - psEnc->sCmn.predictLPCOrder, psEncCtrl->LTPCoef_Q14,
	l32i.n	a2, a13, 32	# psEnc_106(D)->sCmn.predictLPCOrder, _33
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:101:         silk_LTP_analysis_filter_FIX( LPC_in_pre, x - psEnc->sCmn.predictLPCOrder, psEncCtrl->LTPCoef_Q14,
	l32i	a4, a12, 228	# psEnc_106(D)->sCmn.nb_subfr, psEnc_106(D)->sCmn.nb_subfr
	l32i	a8, sp, 116	# %sfp,
	l32i	a7, a12, 236	# psEnc_106(D)->sCmn.subfr_length,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:101:         silk_LTP_analysis_filter_FIX( LPC_in_pre, x - psEnc->sCmn.predictLPCOrder, psEncCtrl->LTPCoef_Q14,
	slli	a3, a2, 1	# tmp663, _33,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:101:         silk_LTP_analysis_filter_FIX( LPC_in_pre, x - psEnc->sCmn.predictLPCOrder, psEncCtrl->LTPCoef_Q14,
	s32i.n	a2, sp, 4	#, _33
	s32i.n	a4, sp, 0	#, psEnc_106(D)->sCmn.nb_subfr
	l32i	a2, sp, 108	# %sfp,
	l32i	a4, sp, 112	# %sfp,
	addi	a6, sp, 64	#,,
	mov.n	a5, a14	#, _21
	sub	a3, a8, a3	#,, tmp663
	call0	silk_LTP_analysis_filter_FIX		#
	j	.L62		#
.L109:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:109:         x_ptr     = x - psEnc->sCmn.predictLPCOrder;
	l32i.n	a5, a13, 32	# psEnc_106(D)->sCmn.predictLPCOrder, _49
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:109:         x_ptr     = x - psEnc->sCmn.predictLPCOrder;
	l32i	a8, sp, 116	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:111:         for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a4, a12, 228	# psEnc_106(D)->sCmn.nb_subfr, _55
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:109:         x_ptr     = x - psEnc->sCmn.predictLPCOrder;
	slli	a7, a5, 1	# tmp668, _49,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:109:         x_ptr     = x - psEnc->sCmn.predictLPCOrder;
	sub	a7, a8, a7	# x_ptr,, tmp668
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:111:         for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	blti	a4, 1, .L63	# _55,,
	l32i	a2, a12, 236	# psEnc_106(D)->sCmn.subfr_length, _48
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:110:         x_pre_ptr = LPC_in_pre;
	l32i	a14, sp, 108	# %sfp, x_pre_ptr
	s32i	a13, sp, 96	# %sfp, tmp820
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:111:         for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	movi.n	a15, 0	# i,
	mov.n	a13, a12	# tmp821, tmp821
	add.n	a5, a2, a5	# tmp823, _48, _49
	mov.n	a12, a7	# x_ptr, x_ptr
.L64:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:112:             silk_scale_copy_vector16( x_pre_ptr, x_ptr, invGains_Q16[ i ],
	slli	a2, a15, 2	# tmp673, i,
	addi	a3, sp, 64	#,,
	add.n	a2, a3, a2	# tmp674,, tmp673
	l32i.n	a4, a2, 0	# MEM[base: _278, offset: 0B],
	mov.n	a3, a12	#, x_ptr
	mov.n	a2, a14	#, x_pre_ptr
	call0	silk_scale_copy_vector16		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:114:             x_pre_ptr += psEnc->sCmn.subfr_length + psEnc->sCmn.predictLPCOrder;
	l32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:114:             x_pre_ptr += psEnc->sCmn.subfr_length + psEnc->sCmn.predictLPCOrder;
	l32i	a2, a13, 236	# psEnc_106(D)->sCmn.subfr_length, _48
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:114:             x_pre_ptr += psEnc->sCmn.subfr_length + psEnc->sCmn.predictLPCOrder;
	l32i.n	a5, a7, 32	# psEnc_106(D)->sCmn.predictLPCOrder, _49
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:111:         for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	l32i	a4, a13, 228	# psEnc_106(D)->sCmn.nb_subfr, _55
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:114:             x_pre_ptr += psEnc->sCmn.subfr_length + psEnc->sCmn.predictLPCOrder;
	add.n	a5, a2, a5	# tmp823, _48, _49
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:114:             x_pre_ptr += psEnc->sCmn.subfr_length + psEnc->sCmn.predictLPCOrder;
	slli	a3, a5, 1	# tmp678, tmp823,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:115:             x_ptr     += psEnc->sCmn.subfr_length;
	slli	a2, a2, 1	# tmp679, _48,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:111:         for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	addi.n	a15, a15, 1	# i, i,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:114:             x_pre_ptr += psEnc->sCmn.subfr_length + psEnc->sCmn.predictLPCOrder;
	add.n	a14, a14, a3	# x_pre_ptr, x_pre_ptr, tmp678
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:115:             x_ptr     += psEnc->sCmn.subfr_length;
	add.n	a12, a12, a2	# x_ptr, x_ptr, tmp679
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:111:         for( i = 0; i < psEnc->sCmn.nb_subfr; i++ ) {
	blt	a15, a4, .L64	# i, _55,
	mov.n	a12, a13	# tmp821, tmp821
	mov.n	a13, a7	# tmp820,
.L63:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:118:         silk_memset( psEncCtrl->LTPCoef_Q14, 0, psEnc->sCmn.nb_subfr * LTP_ORDER * sizeof( opus_int16 ) );
	slli	a2, a4, 2	# tmp682, _55,
	add.n	a4, a2, a4	# tmp683, tmp682, _55
	l32i	a2, sp, 112	# %sfp,
	slli	a4, a4, 1	#, tmp683,
	movi.n	a3, 0	#,
	call0	memset		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:119:         psEncCtrl->LTPredCodGain_Q7 = 0;
	l32i	a8, sp, 100	# %sfp,
	movi.n	a2, 0	# tmp688,
	s32i	a2, a8, 396	# psEncCtrl_107(D)->LTPredCodGain_Q7, tmp688
	l32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:120:         psEnc->sCmn.sum_log_gain_Q7 = 0;
	s32i.n	a2, a13, 48	# psEnc_106(D)->sCmn.sum_log_gain_Q7, tmp688
	addmi	a8, a8, 0x1300	#,,
	s32i	a8, sp, 96	# %sfp,
.L62:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:124:     if( psEnc->sCmn.first_frame_after_reset ) {
	l32i.n	a2, a13, 56	# psEnc_106(D)->sCmn.first_frame_after_reset, psEnc_106(D)->sCmn.first_frame_after_reset
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:125:         minInvGain_Q30 = SILK_FIX_CONST( 1.0f / MAX_PREDICTION_POWER_GAIN_AFTER_RESET, 30 );
	l32r	a5, .LC0	#, minInvGain_Q30
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:124:     if( psEnc->sCmn.first_frame_after_reset ) {
	bnez.n	a2, .L65	# psEnc_106(D)->sCmn.first_frame_after_reset,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:127:         minInvGain_Q30 = silk_log2lin( silk_SMLAWB( 16 << 7, (opus_int32)psEncCtrl->LTPredCodGain_Q7, SILK_FIX_CONST( 1.0 / 3, 16 ) ) );      /* Q16 */
	l32i	a8, sp, 100	# %sfp,
	l32i	a2, a8, 396	# psEncCtrl_107(D)->LTPredCodGain_Q7, _61
	extui	a5, a2, 0, 16	# tmp693, _61,
	srai	a4, a2, 16	# tmp702, _61,
	slli	a3, a5, 2	# tmp695, tmp693,
	slli	a2, a4, 2	# tmp704, tmp702,
	add.n	a3, a3, a5	# tmp696, tmp695, tmp693
	add.n	a2, a2, a4	# tmp705, tmp704, tmp702
	slli	a5, a3, 4	# tmp697, tmp696,
	slli	a4, a2, 4	# tmp706, tmp705,
	add.n	a3, a3, a5	# tmp698, tmp696, tmp697
	add.n	a2, a2, a4	# tmp707, tmp705, tmp706
	slli	a5, a3, 8	# tmp699, tmp698,
	slli	a4, a2, 8	# tmp708, tmp707,
	add.n	a3, a3, a5	# tmp700, tmp698, tmp699
	add.n	a2, a2, a4	# tmp709, tmp707, tmp708
	srai	a3, a3, 16	# tmp701, tmp700,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:127:         minInvGain_Q30 = silk_log2lin( silk_SMLAWB( 16 << 7, (opus_int32)psEncCtrl->LTPredCodGain_Q7, SILK_FIX_CONST( 1.0 / 3, 16 ) ) );      /* Q16 */
	addmi	a2, a2, 0x800	# tmp710, tmp709,
	add.n	a2, a3, a2	#, tmp701, tmp710
	call0	silk_log2lin		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:129:             silk_SMULWW( SILK_FIX_CONST( MAX_PREDICTION_POWER_GAIN, 0 ),
	l32i	a8, sp, 100	# %sfp,
	l32r	a5, .LC9	#, tmp723
	l16si	a3, a8, 388	# psEncCtrl_107(D)->coding_quality_Q14, _70
	slli	a4, a3, 1	# tmp715, _70,
	add.n	a4, a4, a3	# tmp716, tmp715, _70
	l32r	a3, .LC3	#, tmp718
	add.n	a3, a4, a3	# tmp717, tmp716, tmp718
	srai	a3, a3, 15	# tmp719, tmp717,
	addi.n	a3, a3, 1	# tmp720, tmp719,
	srai	a3, a3, 1	# tmp721, tmp720,
	mul16s	a4, a4, a5	# tmp729, tmp716, tmp723
	mull	a3, a3, a5	# tmp722, tmp721, tmp723
	srai	a4, a4, 16	# tmp731, tmp729,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:128:         minInvGain_Q30 = silk_DIV32_varQ( minInvGain_Q30,
	add.n	a3, a3, a4	# _82, tmp722, tmp731
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a2, .L88	# minInvGain_Q30,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	abs	a7, a2	# tmp732, minInvGain_Q30
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a7, a7	# iftmp$6_208, tmp732
	addi.n	a10, a7, -1	# _480, iftmp$6_208,
	addi.n	a14, a7, 15	# _482, iftmp$6_208,
	j	.L66		#
.L88:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a14, 0x2f	# _482,
	movi.n	a10, 0x1f	# _480,
	movi.n	a7, 0x20	# iftmp$6_208,
.L66:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a10	# _480
	sll	a15, a2	# _212, minInvGain_Q30
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a3, .L89	# _82,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a6, a3	# tmp733, _82
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a6, a6	# iftmp$6_216, tmp733
	addi.n	a11, a6, -1	# _520, iftmp$6_216,
	j	.L67		#
.L89:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a11, 0x1f	# _520,
	movi.n	a6, 0x20	# iftmp$6_216,
.L67:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a11	# _520
	sll	a11, a3	# b32_nrm, _82
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC2	#,
	srai	a3, a11, 16	#, b32_nrm,
	s32i	a6, sp, 140	#,
	s32i	a7, sp, 136	#,
	s32i	a11, sp, 128	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp739,,
	srai	a9, a2, 16	# _226, tmp739,
	extui	a8, a15, 0, 16	# tmp740, _212,
	mull	a8, a8, a9	# tmp741, tmp740, _226
	srai	a2, a15, 16	# tmp743, _212,
	mull	a2, a2, a9	# tmp744, tmp743, _226
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a11, sp, 128	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a8, a8, 16	# tmp742, tmp741,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a8, a8, a2	# result, tmp742, tmp744
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a8	#, result
	srai	a5, a8, 31	#, result,
	mov.n	a2, a11	#, b32_nrm
	srai	a3, a11, 31	#, b32_nrm,
	s32i	a8, sp, 144	#,
	s32i	a9, sp, 132	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp751,,
	sub	a3, a15, a3	# a32_nrm, _212, tmp751
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a9, sp, 132	#,
	extui	a2, a3, 0, 16	# tmp754, a32_nrm,
	srai	a4, a3, 16	# tmp752, a32_nrm,
	mull	a3, a4, a9	# tmp753, tmp752, _226
	mull	a2, a2, a9	# tmp755, tmp754, _226
	l32i	a8, sp, 144	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a6, sp, 140	#,
	add.n	a8, a3, a8	# _95, tmp753, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a2, a2, 16	# tmp756, tmp755,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a2, a2, a8	# result, tmp756, _95
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a15, a14, a6	# lshift, _482, iftmp$6_216
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a15	# lshift
	sra	a5, a2	# minInvGain_Q30, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a7, sp, 136	#,
	bgez	a15, .L65	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a5, a6, a7	# tmp758, iftmp$6_216, iftmp$6_208
	l32r	a3, .LC4	#, tmp759
	l32r	a4, .LC5	#, tmp760
	addi	a5, a5, -15	# _252, tmp758,
	ssr	a5	# _252
	sra	a3, a3	# _253, tmp759
	ssr	a5	# _252
	sra	a4, a4	# _254, tmp760
	bge	a4, a3, .L69	# _254, _253,
	bge	a3, a2, .L70	# _253, result,
	j	.L118		#
.L70:
	bge	a2, a4, .L71	# iftmp$4_255, _254,
	j	.L119		#
.L69:
	bge	a4, a2, .L73	# _254, result,
.L119:
	mov.n	a2, a4	# iftmp$4_255, _254
	j	.L71		#
.L73:
	bge	a2, a3, .L71	# iftmp$4_255, _253,
.L118:
	mov.n	a2, a3	# iftmp$4_255, _253
.L71:
	ssl	a5	# _252
	sll	a5, a2	# minInvGain_Q30, iftmp$4_255
.L65:
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:134:     silk_find_LPC_FIX( &psEnc->sCmn, NLSF_Q15, LPC_in_pre, minInvGain_Q30 );
	l32i	a4, sp, 108	# %sfp,
	l32i	a2, sp, 104	# %sfp,
	addi	a3, sp, 16	#,,
	call0	silk_find_LPC_FIX		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:137:     silk_process_NLSFs( &psEnc->sCmn, psEncCtrl->PredCoef_Q12, NLSF_Q15, psEnc->sCmn.prev_NLSFq_Q15 );
	l32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:137:     silk_process_NLSFs( &psEnc->sCmn, psEncCtrl->PredCoef_Q12, NLSF_Q15, psEnc->sCmn.prev_NLSFq_Q15 );
	l32i	a3, sp, 104	# %sfp,
	l32r	a15, .LC10	#, tmp761
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:137:     silk_process_NLSFs( &psEnc->sCmn, psEncCtrl->PredCoef_Q12, NLSF_Q15, psEnc->sCmn.prev_NLSFq_Q15 );
	addi	a8, a2, 16	# _84,,
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:137:     silk_process_NLSFs( &psEnc->sCmn, psEncCtrl->PredCoef_Q12, NLSF_Q15, psEnc->sCmn.prev_NLSFq_Q15 );
	add.n	a15, a3, a15	# _85,, tmp761
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:137:     silk_process_NLSFs( &psEnc->sCmn, psEncCtrl->PredCoef_Q12, NLSF_Q15, psEnc->sCmn.prev_NLSFq_Q15 );
	l32i	a2, sp, 104	# %sfp,
	mov.n	a5, a15	#, _85
	addi	a4, sp, 16	#,,
	mov.n	a3, a8	#, _84
	s32i	a8, sp, 144	#,
	call0	silk_process_NLSFs		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:140:     silk_residual_energy_FIX( psEncCtrl->ResNrg, psEncCtrl->ResNrgQ, LPC_in_pre, psEncCtrl->PredCoef_Q12, local_gains,
	l32i	a4, sp, 96	# %sfp,
	l32i	a8, sp, 144	#,
	l32i	a9, a12, 228	# psEnc_106(D)->sCmn.nb_subfr, psEnc_106(D)->sCmn.nb_subfr
	l32i	a10, a4, 228	# psEnc_106(D)->sCmn.arch, psEnc_106(D)->sCmn.arch
	l32i.n	a11, a13, 32	# psEnc_106(D)->sCmn.predictLPCOrder, psEnc_106(D)->sCmn.predictLPCOrder
	mov.n	a5, a8	#, _84
	l32i	a8, sp, 100	# %sfp,
	l32i	a7, a12, 236	# psEnc_106(D)->sCmn.subfr_length,
	l32i	a4, sp, 108	# %sfp,
	movi	a3, 0x1a0	# tmp764,
	movi	a2, 0x190	# tmp766,
	s32i.n	a9, sp, 0	#, psEnc_106(D)->sCmn.nb_subfr
	addi	a6, sp, 48	#,,
	add.n	a3, a8, a3	#,, tmp764
	add.n	a2, a8, a2	#,, tmp766
	s32i.n	a10, sp, 8	#, psEnc_106(D)->sCmn.arch
	s32i.n	a11, sp, 4	#, psEnc_106(D)->sCmn.predictLPCOrder
	call0	silk_residual_energy_FIX		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:144:     silk_memcpy( psEnc->sCmn.prev_NLSFq_Q15, NLSF_Q15, sizeof( psEnc->sCmn.prev_NLSFq_Q15 ) );
	addi	a3, sp, 16	#,,
	movi.n	a4, 0x20	#,
	mov.n	a2, a15	#, _85
	call0	memcpy		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:145:     RESTORE_STACK;
	l32i	a2, sp, 80	# _saved_stack,
	l32i	a3, sp, 84	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\fixed\find_pred_coefs_FIX.c:146: }
	l32i	a0, sp, 188	#,
	movi	a9, 0xc0	#,
	l32i	a12, sp, 184	#,
	l32i	a13, sp, 180	#,
	l32i	a14, sp, 176	#,
	l32i	a15, sp, 172	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_find_pred_coefs_FIX, .-silk_find_pred_coefs_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
