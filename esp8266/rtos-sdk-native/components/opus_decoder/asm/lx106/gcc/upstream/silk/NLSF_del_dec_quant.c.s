# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF_del_dec_quant.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF_del_dec_quant.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_del_dec_quant.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_del_dec_quant.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_del_dec_quant.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_del_dec_quant.c.s.raw
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
	.section	.text.silk_NLSF_del_dec_quant,"ax",@progbits
	.literal_position
	.literal .LC0, -10342
	.literal .LC1, 2147483647
	.align	4
	.global	silk_NLSF_del_dec_quant
	.type	silk_NLSF_del_dec_quant, @function
# Function: silk_NLSF_del_dec_quant
# Module: upstream/silk/NLSF_del_dec_quant.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Delayed-decision quantizer for NLSF residuals */
# C context: opus_int32 silk_NLSF_del_dec_quant(                             /* O    Returns RD value in Q25                     */
# C context: opus_int8                   indices[],                      /* O    Quantization indices [ order ]              */
# C context: const opus_int16            x_Q10[],                        /* I    Input [ order ]                             */
# C context: const opus_int16            w_Q5[],                         /* I    Weights [ order ]                           */
# C context: const opus_uint8            pred_coef_Q8[],                 /* I    Backward predictor coefs [ order ]          */
silk_NLSF_del_dec_quant:
	movi	a9, 0x190	#,
	sub	sp, sp, a9	#,,
	l16si	a9, sp, 400	# quant_step_size_Q16, _709
	l32r	a8, .LC0	#, tmp397
	l16si	a10, sp, 404	# inv_quant_step_size_Q6,
	l16si	a11, sp, 412	# order,
	mul16s	a8, a9, a8	# ivtmp$44, _709, tmp397
	s32i	a12, sp, 392	#,
	s32i	a13, sp, 388	#,
	s32i	a14, sp, 384	#,
	s32i	a10, sp, 332	# %sfp,
	s32i	a11, sp, 364	# %sfp,
	s32i	a4, sp, 348	# %sfp, w_Q5
	s32i	a7, sp, 356	# %sfp, ec_rates_Q5
	s32i	a0, sp, 396	#,
	s32i	a15, sp, 380	#,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:47: {
	s32i	a2, sp, 360	# %sfp, indices
	s32i	a3, sp, 328	# %sfp, x_Q10
	s32i	a5, sp, 352	# %sfp, pred_coef_Q8
	s32i	a6, sp, 324	# %sfp, ec_ix
	addi	a10, sp, 80	# ivtmp$42,,
	mov.n	a7, sp	# ivtmp$43,
	slli	a11, a9, 10	# _720, _709,
	movi.n	a4, -0xa	# ivtmp$34,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:71:             out1_Q10 = silk_SUB16( out1_Q10, SILK_FIX_CONST( NLSF_QUANT_LEVEL_ADJ, 10 ) );
	movi	a13, 0x39a	# out1_Q10,
	movi	a12, 0x466	# tmp1118,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:63:     for (i = -NLSF_QUANT_MAX_AMPLITUDE_EXT; i <= NLSF_QUANT_MAX_AMPLITUDE_EXT-1; i++)
	movi.n	a14, 9	# tmp1119,
.L7:
	slli	a2, a4, 10	# tmp399, ivtmp$34,
	extui	a2, a2, 0, 16	# _698, tmp399
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:79:         out1_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out1_Q10, quant_step_size_Q16 ), 16 );
	add.n	a3, a8, a11	# ivtmp$44, ivtmp$44, _720
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:65:         out0_Q10 = silk_LSHIFT( i, 10 );
	slli	a5, a2, 16	# tmp400, _698,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:78:         out0_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out0_Q10, quant_step_size_Q16 ), 16 );
	srai	a15, a8, 16	# tmp401, ivtmp$44,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:79:         out1_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out1_Q10, quant_step_size_Q16 ), 16 );
	srai	a6, a3, 16	# tmp403, ivtmp$44,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:65:         out0_Q10 = silk_LSHIFT( i, 10 );
	srai	a5, a5, 16	# out0_Q10, tmp400,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:67:         if( i > 0 ) {
	blti	a4, 1, .L2	# ivtmp$34,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:78:         out0_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out0_Q10, quant_step_size_Q16 ), 16 );
	s32i.n	a15, a10, 0	# MEM[base: _575, offset: 0B], tmp401
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:79:         out1_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out1_Q10, quant_step_size_Q16 ), 16 );
	s32i.n	a6, a7, 0	# MEM[base: _579, offset: 0B], tmp403
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:63:     for (i = -NLSF_QUANT_MAX_AMPLITUDE_EXT; i <= NLSF_QUANT_MAX_AMPLITUDE_EXT-1; i++)
	bne	a4, a14, .L3	# ivtmp$34, tmp1119,
	j	.L91		#
.L2:
	add.n	a3, a2, a12	# tmp408, _698, tmp1118
	addi	a6, a2, 102	# tmp405, _698,
	slli	a15, a3, 16	# tmp409, tmp408,
	slli	a6, a6, 16	# tmp406, tmp405,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:71:             out1_Q10 = silk_SUB16( out1_Q10, SILK_FIX_CONST( NLSF_QUANT_LEVEL_ADJ, 10 ) );
	mov.n	a3, a13	# out1_Q10, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:70:         } else if( i == 0 ) {
	beqz.n	a4, .L5	# ivtmp$34,
	srai	a5, a6, 16	# out0_Q10, tmp406,
	srai	a3, a15, 16	# out1_Q10, tmp409,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:72:         } else if( i == -1 ) {
	bnei	a4, -1, .L5	# ivtmp$34,,
	j	.L6		#
.L3:
	addi.n	a4, a4, 1	# ivtmp$34, ivtmp$34,
	addi.n	a10, a10, 4	# ivtmp$42, ivtmp$42,
	addi.n	a7, a7, 4	# ivtmp$43, ivtmp$43,
	mov.n	a8, a3	# ivtmp$44, ivtmp$44
	j	.L7		#
.L91:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:85:     RD_Q25[ 0 ] = 0;
	movi	a12, 0xe0	# tmp411,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:87:     for( i = order - 1; i >= 0; i-- ) {
	l32i	a13, sp, 364	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:85:     RD_Q25[ 0 ] = 0;
	movi.n	a2, 0	# tmp413,
	add.n	a12, sp, a12	# tmp412,, tmp411
	s32i.n	a2, a12, 0	# RD_Q25, tmp413
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:86:     prev_out_Q10[ 0 ] = 0;
	s16i	a2, sp, 256	# prev_out_Q10, tmp413
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:87:     for( i = order - 1; i >= 0; i-- ) {
	addi.n	a5, a13, -1	# i,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:87:     for( i = order - 1; i >= 0; i-- ) {
	bge	a5, a2, .L8	# i,,
	j	.L92		#
.L94:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	l32i	a12, sp, 224	# RD_Q25, <retval>
.L75:
	l32i	a2, sp, 228	# RD_Q25, _670
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	movi.n	a13, 0	# ind_tmp,
	bge	a2, a12, .L10	# _670, <retval>,
	mov.n	a12, a2	# <retval>, _670
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:200:     for( j = 0; j < 2 * NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a13, 1	# ind_tmp,
.L10:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	l32i	a2, sp, 232	# RD_Q25, _658
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	bge	a2, a12, .L11	# _658, <retval>,
	mov.n	a12, a2	# <retval>, _658
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:200:     for( j = 0; j < 2 * NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a13, 2	# ind_tmp,
.L11:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	l32i	a2, sp, 236	# RD_Q25, _647
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	bge	a2, a12, .L12	# _647, <retval>,
	mov.n	a12, a2	# <retval>, _647
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:200:     for( j = 0; j < 2 * NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a13, 3	# ind_tmp,
.L12:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	l32i	a2, sp, 240	# RD_Q25, _638
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	bge	a2, a12, .L13	# _638, <retval>,
	mov.n	a12, a2	# <retval>, _638
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:200:     for( j = 0; j < 2 * NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a13, 4	# ind_tmp,
.L13:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	l32i	a2, sp, 244	# RD_Q25, _629
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	bge	a2, a12, .L14	# _629, <retval>,
	mov.n	a12, a2	# <retval>, _629
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:200:     for( j = 0; j < 2 * NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a13, 5	# ind_tmp,
.L14:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	l32i	a2, sp, 248	# RD_Q25, _620
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	bge	a2, a12, .L15	# _620, <retval>,
	mov.n	a12, a2	# <retval>, _620
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:200:     for( j = 0; j < 2 * NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a13, 6	# ind_tmp,
.L15:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	l32i	a2, sp, 252	# RD_Q25, _109
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	blt	a2, a12, .L16	# _109, <retval>,
	j	.L17		#
.L8:
	l32i	a3, sp, 408	# mu_Q20, mu_Q20
	l32i	a6, sp, 324	# %sfp,
	l32i	a7, sp, 328	# %sfp,
	slli	a2, a5, 1	# tmp1027, i,
	slli	a3, a3, 16	# tmp440, mu_Q20,
	movi	a8, 0xa0	#,
	add.n	a6, a6, a2	#,, tmp1027
	add.n	a7, a7, a2	#,, tmp1027
	srai	a3, a3, 16	#, tmp440,
	add.n	a8, a8, sp	#,,
	s32i	a3, sp, 320	# %sfp,
	s32i	a6, sp, 324	# %sfp,
	s32i	a7, sp, 328	# %sfp,
	add.n	a13, a8, a5	# ivtmp$28,, i
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:84:     nStates = 1;
	movi.n	a14, 1	# nStates,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:127:             RD_tmp_Q25            = RD_Q25[ j ];
	mov.n	a15, a5	# i, i
	mov.n	a10, a7	#,
	mov.n	a11, a6	#,
.L70:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	l32i	a9, sp, 352	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:89:         in_Q10 = x_Q10[ i ];
	l16si	a4, a10, 0	# MEM[base: _662, offset: 0B], _21
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	add.n	a3, a9, a15	# tmp449,, i
	l8ui	a7, a3, 0	# MEM[base: _672, offset: 0B], _23
	l16ui	a3, sp, 256	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:88:         rates_Q5 = &ec_rates_Q5[ ec_ix[ i ] ];
	l16si	a6, a11, 0	# MEM[base: _661, offset: 0B], tmp444
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	mul16s	a3, a3, a7	# tmp459, prev_out_Q10, _23
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:88:         rates_Q5 = &ec_rates_Q5[ ec_ix[ i ] ];
	l32i	a10, sp, 356	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	srai	a3, a3, 8	# pred_Q10, tmp459,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	l32i	a8, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:88:         rates_Q5 = &ec_rates_Q5[ ec_ix[ i ] ];
	add.n	a6, a10, a6	#,, tmp444
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:92:             res_Q10  = silk_SUB16( in_Q10, pred_Q10 );
	sub	a5, a4, a3	# res_Q10, _21, pred_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	l32i	a9, sp, 348	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	mul16s	a5, a5, a8	# tmp462, res_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:88:         rates_Q5 = &ec_rates_Q5[ ec_ix[ i ] ];
	s32i	a6, sp, 336	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a11, sp, 156	# out0_Q10_table,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:99:             out1_Q10 = out1_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a6, sp, 76	# out1_Q10_table,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a2, a9, a2	# tmp455,, tmp1027
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:99:             out1_Q10 = out1_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	s32i	a6, sp, 340	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	srai	a5, a5, 16	# ind_tmp, tmp462,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a9, 9	# tmp464,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	s32i	a11, sp, 344	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	l16si	a6, a2, 0	# MEM[base: _368, offset: 0B], _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	bge	a9, a5, .L18	# tmp464, ind_tmp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	l32i	a8, sp, 340	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a2, a11, a3	# tmp466,, _567
	slli	a2, a2, 16	# tmp467, tmp466,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a3, a8, a3	# tmp468,, _567
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a2, a2, 16	# out0_Q10, tmp467,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a3, a3, 16	# tmp469, tmp468,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a8, a14, 1	# nStates, nStates,
	addmi	a10, sp, 0x100	#,,
	add.n	a5, a10, a8	# tmp473,, nStates
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a3, a3, 16	# out1_Q10, tmp469,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a2, sp, 256	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a9, a13, 0	# MEM[base: _501, offset: 0B], tmp464
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a3, a5, 0	# prev_out_Q10, out1_Q10
	movi	a9, 0x1ef	# rate0_Q5,
	movi	a5, 0x21a	# rate1_Q5,
	j	.L19		#
.L18:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a2, -0xa	# tmp478,
	mov.n	a9, a5	# iftmp$4_555, ind_tmp
	bge	a5, a2, .L20	# ind_tmp, tmp478,
	mov.n	a9, a2	# iftmp$4_555, tmp478
.L20:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	addi.n	a2, a9, 10	# _552, iftmp$4_555,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	slli	a2, a2, 2	# tmp479, _552,
	add.n	a2, sp, a2	# tmp480,, tmp479
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a8, a2, 80	# out0_Q10_table, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:99:             out1_Q10 = out1_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a10, a2, 0	# out1_Q10_table, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a2, a8, a3	# tmp488, out0_Q10, _567
	slli	a2, a2, 16	# tmp489, tmp488,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a3, a10, a3	# tmp490, out1_Q10, _567
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a2, a2, 16	# out0_Q10, tmp489,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a3, a3, 16	# tmp491, tmp490,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a8, a14, 1	# nStates, nStates,
	addmi	a11, sp, 0x100	#,,
	add.n	a10, a11, a8	# tmp495,, nStates
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a3, a3, 16	# out1_Q10, tmp491,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a2, sp, 256	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a3, a10, 0	# prev_out_Q10, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a9, a13, 0	# MEM[base: _500, offset: 0B], iftmp$4_555
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	addi.n	a10, a9, 1	# tmp496, iftmp$4_555,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	bgei	a10, 4, .L21	# tmp496,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:115:             } else if( ind_tmp <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a10, -3	# tmp497,
	blt	a5, a10, .L22	# ind_tmp, tmp497,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a10, sp, 336	# %sfp,
	add.n	a5, a10, a9	# tmp498,, iftmp$4_555
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a9, a5, 4	# *_540, rate0_Q5
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:125:                 rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a5, a5, 5	# *_536, rate1_Q5
	j	.L19		#
.L22:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:116:                 if( ind_tmp == -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a10, -4	# tmp502,
	beq	a5, a10, .L23	# ind_tmp, tmp502,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	movi	a5, -0x2b	# tmp503,
	mull	a5, a9, a5	# _533, iftmp$4_555, tmp503
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	addi	a9, a5, 108	# rate0_Q5, _533,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:121:                     rate1_Q5 = silk_SUB16( rate0_Q5, 43 );
	addi	a5, a5, 65	# rate1_Q5, _533,
	j	.L19		#
.L23:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a11, sp, 336	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:117:                     rate0_Q5 = 280;
	movi	a9, 0x118	# rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a5, a11, 1	# MEM[(const opus_uint8 *)rates_Q5_174 + 1B], rate1_Q5
	j	.L19		#
.L21:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:108:                 if( ind_tmp + 1 == NLSF_QUANT_MAX_AMPLITUDE ) {
	beqi	a5, 3, .L24	# ind_tmp,,
	slli	a10, a9, 1	# tmp505, iftmp$4_555,
	add.n	a10, a10, a9	# tmp506, tmp505, iftmp$4_555
	slli	a5, a10, 3	# tmp507, tmp506,
	sub	a5, a5, a10	# tmp508, tmp507, tmp506
	slli	a5, a5, 1	# tmp509, tmp508,
	add.n	a5, a5, a9	# tmp510, tmp509, iftmp$4_555
	movi	a10, 0x97	# tmp511,
	addi	a9, a5, 108	# rate0_Q5, tmp510,
	add.n	a5, a5, a10	# rate1_Q5, tmp510, tmp511
	j	.L19		#
.L24:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:109:                     rate0_Q5 = rates_Q5[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a5, sp, 336	# %sfp,
	l8ui	a9, a5, 7	# MEM[(const opus_uint8 *)rates_Q5_174 + 7B], rate0_Q5
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:110:                     rate1_Q5 = 280;
	movi	a5, 0x118	# rate1_Q5,
.L19:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	l32i	a11, sp, 320	# %sfp,
	sub	a2, a4, a2	# tmp515, _21, out0_Q10
	mul16s	a2, a2, a2	# tmp522, tmp515, tmp515
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	sub	a3, a4, a3	# tmp525, _21, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:127:             RD_tmp_Q25            = RD_Q25[ j ];
	l32i.n	a10, a12, 0	# RD_Q25, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a9, a9, a11	# tmp520, rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mul16s	a3, a3, a3	# tmp534, tmp525, tmp525
	mull	a5, a5, a11	# tmp532, rate1_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a2, a2, a6	# tmp523, tmp522, _61
	add.n	a9, a9, a10	# tmp521, tmp520, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mull	a3, a3, a6	# tmp535, tmp534, _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a9, a9, a2	# tmp524, tmp521, tmp523
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	slli	a11, a14, 2	# tmp530, nStates,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a5, a5, a10	# tmp533, tmp532, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	s32i.n	a9, a12, 0	# RD_Q25, tmp524
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a11, a12, a11	# tmp531, tmp514, tmp530
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a3, a5, a3	# tmp536, tmp533, tmp535
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	s32i.n	a3, a11, 0	# RD_Q25, tmp536
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:90:         for( j = 0; j < nStates; j++ ) {
	beqi	a14, 1, .L26	# nStates,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	l16ui	a2, sp, 258	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	l32i	a10, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	mul16s	a2, a2, a7	# tmp538, prev_out_Q10, _23
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a9, 9	# tmp543,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	srai	a2, a2, 8	# pred_Q10, tmp538,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:92:             res_Q10  = silk_SUB16( in_Q10, pred_Q10 );
	sub	a5, a4, a2	# res_Q10, _21, pred_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	mul16s	a5, a5, a10	# tmp541, res_Q10,
	addi.n	a8, a14, 1	# _488, nStates,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	srai	a5, a5, 16	# ind_tmp, tmp541,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	bge	a9, a5, .L27	# tmp543, ind_tmp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	l32i	a11, sp, 344	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	l32i	a5, sp, 340	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a3, a11, a2	# tmp545,, _489
	slli	a3, a3, 16	# tmp546, tmp545,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a2, a5, a2	# tmp547,, _489
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a3, a3, 16	# out0_Q10, tmp546,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a2, a2, 16	# tmp548, tmp547,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a5, a8, 1	# tmp551, _488,
	addmi	a10, sp, 0x100	#,,
	add.n	a5, a10, a5	# tmp552,, tmp551
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a2, a2, 16	# out1_Q10, tmp548,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a3, sp, 258	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a9, a13, 16	# MEM[base: _413, offset: 16B], tmp543
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a2, a5, 0	# prev_out_Q10, out1_Q10
	movi	a9, 0x1ef	# rate0_Q5,
	movi	a5, 0x21a	# rate1_Q5,
	j	.L28		#
.L27:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a3, -0xa	# tmp557,
	mov.n	a9, a5	# iftmp$4_477, ind_tmp
	bge	a5, a3, .L29	# ind_tmp, tmp557,
	mov.n	a9, a3	# iftmp$4_477, tmp557
.L29:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	addi.n	a3, a9, 10	# _474, iftmp$4_477,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	slli	a3, a3, 2	# tmp558, _474,
	add.n	a3, sp, a3	# tmp559,, tmp558
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a10, a3, 80	# out0_Q10_table, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:99:             out1_Q10 = out1_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a11, a3, 0	# out1_Q10_table, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a3, a10, a2	# tmp567, out0_Q10, _489
	slli	a3, a3, 16	# tmp568, tmp567,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a2, a11, a2	# tmp569, out1_Q10, _489
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a3, a3, 16	# out0_Q10, tmp568,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a2, a2, 16	# tmp570, tmp569,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a10, a8, 1	# tmp573, _488,
	addmi	a11, sp, 0x100	#,,
	add.n	a10, a11, a10	# tmp574,, tmp573
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a2, a2, 16	# out1_Q10, tmp570,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a3, sp, 258	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a2, a10, 0	# prev_out_Q10, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a9, a13, 16	# MEM[base: _412, offset: 16B], iftmp$4_477
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	addi.n	a10, a9, 1	# tmp575, iftmp$4_477,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	bgei	a10, 4, .L30	# tmp575,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:115:             } else if( ind_tmp <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a10, -3	# tmp576,
	blt	a5, a10, .L31	# ind_tmp, tmp576,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a10, sp, 336	# %sfp,
	add.n	a5, a10, a9	# tmp577,, iftmp$4_477
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a9, a5, 4	# *_462, rate0_Q5
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:125:                 rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a5, a5, 5	# *_458, rate1_Q5
	j	.L28		#
.L31:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:116:                 if( ind_tmp == -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a10, -4	# tmp581,
	beq	a5, a10, .L32	# ind_tmp, tmp581,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	movi	a5, -0x2b	# tmp582,
	mull	a5, a9, a5	# _455, iftmp$4_477, tmp582
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	addi	a9, a5, 108	# rate0_Q5, _455,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:121:                     rate1_Q5 = silk_SUB16( rate0_Q5, 43 );
	addi	a5, a5, 65	# rate1_Q5, _455,
	j	.L28		#
.L32:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a11, sp, 336	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:117:                     rate0_Q5 = 280;
	movi	a9, 0x118	# rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a5, a11, 1	# MEM[(const opus_uint8 *)rates_Q5_174 + 1B], rate1_Q5
	j	.L28		#
.L30:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:108:                 if( ind_tmp + 1 == NLSF_QUANT_MAX_AMPLITUDE ) {
	beqi	a5, 3, .L33	# ind_tmp,,
	slli	a10, a9, 1	# tmp584, iftmp$4_477,
	add.n	a10, a10, a9	# tmp585, tmp584, iftmp$4_477
	slli	a5, a10, 3	# tmp586, tmp585,
	sub	a5, a5, a10	# tmp587, tmp586, tmp585
	slli	a5, a5, 1	# tmp588, tmp587,
	add.n	a5, a5, a9	# tmp589, tmp588, iftmp$4_477
	movi	a10, 0x97	# tmp590,
	addi	a9, a5, 108	# rate0_Q5, tmp589,
	add.n	a5, a5, a10	# rate1_Q5, tmp589, tmp590
	j	.L28		#
.L33:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:109:                     rate0_Q5 = rates_Q5[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a5, sp, 336	# %sfp,
	l8ui	a9, a5, 7	# MEM[(const opus_uint8 *)rates_Q5_174 + 7B], rate0_Q5
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:110:                     rate1_Q5 = 280;
	movi	a5, 0x118	# rate1_Q5,
.L28:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	l32i	a11, sp, 320	# %sfp,
	sub	a3, a4, a3	# tmp594, _21, out0_Q10
	mul16s	a3, a3, a3	# tmp601, tmp594, tmp594
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	sub	a2, a4, a2	# tmp604, _21, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:127:             RD_tmp_Q25            = RD_Q25[ j ];
	l32i.n	a10, a12, 4	# RD_Q25, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a9, a9, a11	# tmp599, rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mul16s	a2, a2, a2	# tmp613, tmp604, tmp604
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a3, a3, a6	# tmp602, tmp601, _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mull	a5, a5, a11	# tmp611, rate1_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a9, a9, a10	# tmp600, tmp599, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mull	a2, a2, a6	# tmp614, tmp613, _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a9, a9, a3	# tmp603, tmp600, tmp602
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	slli	a8, a8, 2	# tmp609, _488,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a5, a5, a10	# tmp612, tmp611, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	s32i.n	a9, a12, 4	# RD_Q25, tmp603
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a8, a12, a8	# tmp610, tmp514, tmp609
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a2, a5, a2	# tmp615, tmp612, tmp614
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	s32i.n	a2, a8, 0	# RD_Q25, tmp615
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:90:         for( j = 0; j < nStates; j++ ) {
	beqi	a14, 2, .L35	# nStates,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	l16ui	a3, sp, 260	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	l32i	a10, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	mul16s	a3, a3, a7	# tmp617, prev_out_Q10, _23
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a9, 9	# tmp622,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	srai	a3, a3, 8	# pred_Q10, tmp617,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:92:             res_Q10  = silk_SUB16( in_Q10, pred_Q10 );
	sub	a5, a4, a3	# res_Q10, _21, pred_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	mul16s	a5, a5, a10	# tmp620, res_Q10,
	addi.n	a8, a14, 2	# _315, nStates,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	srai	a5, a5, 16	# ind_tmp, tmp620,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	bge	a9, a5, .L36	# tmp622, ind_tmp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	l32i	a11, sp, 344	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	l32i	a5, sp, 340	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a2, a11, a3	# tmp624,, _316
	slli	a2, a2, 16	# tmp625, tmp624,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a3, a5, a3	# tmp626,, _316
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a2, a2, 16	# out0_Q10, tmp625,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a3, a3, 16	# tmp627, tmp626,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a5, a8, 1	# tmp630, _315,
	addmi	a10, sp, 0x100	#,,
	add.n	a5, a10, a5	# tmp631,, tmp630
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a3, a3, 16	# out1_Q10, tmp627,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a2, sp, 260	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a9, a13, 32	# MEM[base: _585, offset: 32B], tmp622
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a3, a5, 0	# prev_out_Q10, out1_Q10
	movi	a9, 0x1ef	# rate0_Q5,
	movi	a5, 0x21a	# rate1_Q5,
	j	.L37		#
.L36:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a2, -0xa	# tmp636,
	mov.n	a9, a5	# iftmp$4_278, ind_tmp
	bge	a5, a2, .L38	# ind_tmp, tmp636,
	mov.n	a9, a2	# iftmp$4_278, tmp636
.L38:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	addi.n	a2, a9, 10	# _269, iftmp$4_278,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	slli	a2, a2, 2	# tmp637, _269,
	add.n	a2, sp, a2	# tmp638,, tmp637
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a10, a2, 80	# out0_Q10_table, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:99:             out1_Q10 = out1_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a11, a2, 0	# out1_Q10_table, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a2, a10, a3	# tmp646, out0_Q10, _316
	slli	a2, a2, 16	# tmp647, tmp646,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a3, a11, a3	# tmp648, out1_Q10, _316
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a2, a2, 16	# out0_Q10, tmp647,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a3, a3, 16	# tmp649, tmp648,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a10, a8, 1	# tmp652, _315,
	addmi	a11, sp, 0x100	#,,
	add.n	a10, a11, a10	# tmp653,, tmp652
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a3, a3, 16	# out1_Q10, tmp649,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a2, sp, 260	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a3, a10, 0	# prev_out_Q10, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a9, a13, 32	# MEM[base: _409, offset: 32B], iftmp$4_278
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	addi.n	a10, a9, 1	# tmp654, iftmp$4_278,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	bgei	a10, 4, .L39	# tmp654,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:115:             } else if( ind_tmp <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a10, -3	# tmp655,
	blt	a5, a10, .L40	# ind_tmp, tmp655,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a10, sp, 336	# %sfp,
	add.n	a5, a10, a9	# tmp656,, iftmp$4_278
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a9, a5, 4	# *_220, rate0_Q5
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:125:                 rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a5, a5, 5	# *_216, rate1_Q5
	j	.L37		#
.L40:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:116:                 if( ind_tmp == -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a10, -4	# tmp660,
	beq	a5, a10, .L41	# ind_tmp, tmp660,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	movi	a5, -0x2b	# tmp661,
	mull	a5, a9, a5	# _213, iftmp$4_278, tmp661
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	addi	a9, a5, 108	# rate0_Q5, _213,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:121:                     rate1_Q5 = silk_SUB16( rate0_Q5, 43 );
	addi	a5, a5, 65	# rate1_Q5, _213,
	j	.L37		#
.L41:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a11, sp, 336	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:117:                     rate0_Q5 = 280;
	movi	a9, 0x118	# rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a5, a11, 1	# MEM[(const opus_uint8 *)rates_Q5_174 + 1B], rate1_Q5
	j	.L37		#
.L39:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:108:                 if( ind_tmp + 1 == NLSF_QUANT_MAX_AMPLITUDE ) {
	beqi	a5, 3, .L42	# ind_tmp,,
	slli	a10, a9, 1	# tmp663, iftmp$4_278,
	add.n	a10, a10, a9	# tmp664, tmp663, iftmp$4_278
	slli	a5, a10, 3	# tmp665, tmp664,
	sub	a5, a5, a10	# tmp666, tmp665, tmp664
	slli	a5, a5, 1	# tmp667, tmp666,
	add.n	a5, a5, a9	# tmp668, tmp667, iftmp$4_278
	movi	a10, 0x97	# tmp669,
	addi	a9, a5, 108	# rate0_Q5, tmp668,
	add.n	a5, a5, a10	# rate1_Q5, tmp668, tmp669
	j	.L37		#
.L42:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:109:                     rate0_Q5 = rates_Q5[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a5, sp, 336	# %sfp,
	l8ui	a9, a5, 7	# MEM[(const opus_uint8 *)rates_Q5_174 + 7B], rate0_Q5
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:110:                     rate1_Q5 = 280;
	movi	a5, 0x118	# rate1_Q5,
.L37:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	l32i	a11, sp, 320	# %sfp,
	sub	a2, a4, a2	# tmp673, _21, out0_Q10
	mul16s	a2, a2, a2	# tmp680, tmp673, tmp673
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	sub	a3, a4, a3	# tmp683, _21, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:127:             RD_tmp_Q25            = RD_Q25[ j ];
	l32i.n	a10, a12, 8	# RD_Q25, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a9, a9, a11	# tmp678, rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mul16s	a3, a3, a3	# tmp692, tmp683, tmp683
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a2, a2, a6	# tmp681, tmp680, _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mull	a5, a5, a11	# tmp690, rate1_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a9, a9, a10	# tmp679, tmp678, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mull	a3, a3, a6	# tmp693, tmp692, _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a9, a9, a2	# tmp682, tmp679, tmp681
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	slli	a8, a8, 2	# tmp688, _315,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a5, a5, a10	# tmp691, tmp690, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	s32i.n	a9, a12, 8	# RD_Q25, tmp682
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a8, a12, a8	# tmp689, tmp514, tmp688
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a3, a5, a3	# tmp694, tmp691, tmp693
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	s32i.n	a3, a8, 0	# RD_Q25, tmp694
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:90:         for( j = 0; j < nStates; j++ ) {
	beqi	a14, 3, .L44	# nStates,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	l16ui	a2, sp, 262	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	l32i	a9, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	mul16s	a2, a2, a7	# tmp696, prev_out_Q10, _23
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a5, 9	# tmp701,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:91:             pred_Q10 = silk_RSHIFT( silk_SMULBB( (opus_int16)pred_coef_Q8[ i ], prev_out_Q10[ j ] ), 8 );
	srai	a2, a2, 8	# pred_Q10, tmp696,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:92:             res_Q10  = silk_SUB16( in_Q10, pred_Q10 );
	sub	a3, a4, a2	# res_Q10, _21, pred_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	mul16s	a3, a3, a9	# tmp699, res_Q10,
	addi.n	a8, a14, 3	# _653, nStates,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:93:             ind_tmp  = silk_RSHIFT( silk_SMULBB( inv_quant_step_size_Q6, res_Q10 ), 16 );
	srai	a3, a3, 16	# ind_tmp, tmp699,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	blt	a5, a3, .L45	# tmp701, ind_tmp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:94:             ind_tmp  = silk_LIMIT( ind_tmp, -NLSF_QUANT_MAX_AMPLITUDE_EXT, NLSF_QUANT_MAX_AMPLITUDE_EXT-1 );
	movi.n	a7, -0xa	# tmp706,
	mov.n	a5, a3	# iftmp$4_182, ind_tmp
	bge	a3, a7, .L46	# ind_tmp, tmp706,
	mov.n	a5, a7	# iftmp$4_182, tmp706
.L46:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	addi.n	a7, a5, 10	# _33, iftmp$4_182,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	slli	a7, a7, 2	# tmp707, _33,
	add.n	a7, sp, a7	# tmp708,, tmp707
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:98:             out0_Q10 = out0_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a9, a7, 80	# out0_Q10_table, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:99:             out1_Q10 = out1_Q10_table[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE_EXT ];
	l16si	a10, a7, 0	# out1_Q10_table, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a7, a9, a2	# tmp716, out0_Q10, _652
	slli	a7, a7, 16	# tmp717, tmp716,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a2, a10, a2	# tmp718, out1_Q10, _652
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a7, a7, 16	# out0_Q10, tmp717,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a2, a2, 16	# tmp719, tmp718,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a9, a8, 1	# tmp722, _653,
	addmi	a10, sp, 0x100	#,,
	add.n	a9, a10, a9	# tmp723,, tmp722
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a2, a2, 16	# out1_Q10, tmp719,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a7, sp, 262	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a2, a9, 0	# prev_out_Q10, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a5, a13, 48	# MEM[base: _408, offset: 48B], iftmp$4_182
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	addi.n	a9, a5, 1	# tmp724, iftmp$4_182,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:107:             if( ind_tmp + 1 >= NLSF_QUANT_MAX_AMPLITUDE ) {
	blti	a9, 4, .L47	# tmp724,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:108:                 if( ind_tmp + 1 == NLSF_QUANT_MAX_AMPLITUDE ) {
	bnei	a3, 3, .L48	# ind_tmp,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:109:                     rate0_Q5 = rates_Q5[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a11, sp, 336	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:110:                     rate1_Q5 = 280;
	movi	a9, 0x118	# rate1_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:109:                     rate0_Q5 = rates_Q5[ ind_tmp + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a10, a11, 7	# MEM[(const opus_uint8 *)rates_Q5_174 + 7B], rate0_Q5
	j	.L49		#
.L48:
	slli	a3, a5, 1	# tmp726, iftmp$4_182,
	add.n	a9, a3, a5	# tmp727, tmp726, iftmp$4_182
	slli	a3, a9, 3	# tmp728, tmp727,
	sub	a3, a3, a9	# tmp729, tmp728, tmp727
	slli	a3, a3, 1	# tmp730, tmp729,
	add.n	a3, a3, a5	# tmp731, tmp730, iftmp$4_182
	movi	a9, 0x97	# tmp732,
	addi	a10, a3, 108	# rate0_Q5, tmp731,
	add.n	a9, a3, a9	# rate1_Q5, tmp731, tmp732
	j	.L49		#
.L47:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:115:             } else if( ind_tmp <= -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a9, -3	# tmp733,
	bge	a3, a9, .L50	# ind_tmp, tmp733,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:116:                 if( ind_tmp == -NLSF_QUANT_MAX_AMPLITUDE ) {
	movi.n	a9, -4	# tmp734,
	bne	a3, a9, .L51	# ind_tmp, tmp734,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a3, sp, 336	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:117:                     rate0_Q5 = 280;
	movi	a10, 0x118	# rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:118:                     rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a9, a3, 1	# MEM[(const opus_uint8 *)rates_Q5_174 + 1B], rate1_Q5
	j	.L49		#
.L51:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	movi	a3, -0x2b	# tmp735,
	mull	a3, a5, a3	# _48, iftmp$4_182, tmp735
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:120:                     rate0_Q5 = silk_SMLABB( 280 - 43 * NLSF_QUANT_MAX_AMPLITUDE, -43, ind_tmp );
	addi	a10, a3, 108	# rate0_Q5, _48,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:121:                     rate1_Q5 = silk_SUB16( rate0_Q5, 43 );
	addi	a9, a3, 65	# rate1_Q5, _48,
	j	.L49		#
.L50:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l32i	a9, sp, 336	# %sfp,
	add.n	a3, a9, a5	# tmp736,, iftmp$4_182
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:124:                 rate0_Q5 = rates_Q5[ ind_tmp +     NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a10, a3, 4	# *_51, rate0_Q5
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:125:                 rate1_Q5 = rates_Q5[ ind_tmp + 1 + NLSF_QUANT_MAX_AMPLITUDE ];
	l8ui	a9, a3, 5	# *_54, rate1_Q5
.L49:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	sub	a7, a4, a7	# tmp743, _21, out0_Q10
	l32i	a11, sp, 320	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	sub	a4, a4, a2	# tmp753, _21, out1_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mul16s	a7, a7, a7	# tmp748, tmp743, tmp743
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:127:             RD_tmp_Q25            = RD_Q25[ j ];
	l32i.n	a5, a12, 12	# RD_Q25, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a3, a10, a11	# tmp750, rate0_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mul16s	a4, a4, a4	# tmp760, tmp753, tmp753
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	mull	a7, a7, a6	# tmp749, tmp748, _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mull	a2, a9, a11	# tmp762, rate1_Q5,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a3, a3, a5	# tmp751, tmp750, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	mull	a6, a4, a6	# tmp761, tmp760, _61
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	add.n	a3, a7, a3	# tmp752, tmp749, tmp751
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	slli	a8, a8, 2	# tmp758, _653,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a2, a2, a5	# tmp763, tmp762, RD_tmp_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:129:             RD_Q25[ j ]           = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate0_Q5 );
	s32i.n	a3, a12, 12	# RD_Q25, tmp752
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a8, a12, a8	# tmp759, tmp514, tmp758
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	add.n	a6, a6, a2	# tmp764, tmp761, tmp763
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:131:             RD_Q25[ j + nStates ] = silk_SMLABB( silk_MLA( RD_tmp_Q25, silk_SMULBB( diff_Q10, diff_Q10 ), w_Q5[ i ] ), mu_Q20, rate1_Q5 );
	s32i.n	a6, a8, 0	# RD_Q25, tmp764
	j	.L44		#
.L26:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	l8ui	a2, a13, 0	# MEM[base: _792, offset: 0B],
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	addi	a4, sp, 16	#,,
	add.n	a3, a4, a15	# tmp767,, i
	movi	a4, 0xa0	# tmp768,
	add.n	a3, a3, a4	# tmp769, tmp767, tmp768
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	addi.n	a2, a2, 1	# tmp771, MEM[base: _792, offset: 0B],
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	s8i	a2, a3, 0	# ind, tmp771
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:139:             nStates = silk_LSHIFT( nStates, 1 );
	mov.n	a14, a8	# nStates, nStates
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:140:             for( j = nStates; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	bnei	a8, 4, .L93	# nStates,,
	j	.L60		#
.L96:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:157:                     RD_min_Q25[ j ] = RD_Q25[ j ];
	s32i	a2, sp, 288	# RD_min_Q25, _329
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	movi.n	a2, 0	# tmp775,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:158:                     RD_max_Q25[ j ] = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a3, sp, 272	# RD_max_Q25, _331
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	s32i	a2, sp, 304	# ind_sort, tmp775
	j	.L53		#
.L77:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:152:                     out0_Q10 = prev_out_Q10[ j ];
	l16si	a4, sp, 256	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	l16ui	a5, sp, 264	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:147:                     RD_max_Q25[ j ]                         = RD_Q25[ j ];
	s32i	a2, sp, 272	# RD_max_Q25, _329
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:150:                     RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] = RD_max_Q25[ j ];
	s32i.n	a2, a12, 16	# RD_Q25, _329
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	movi.n	a2, 4	# tmp792,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:148:                     RD_min_Q25[ j ]                         = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a3, sp, 288	# RD_min_Q25, _331
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:149:                     RD_Q25[ j ]                             = RD_min_Q25[ j ];
	s32i.n	a3, a12, 0	# RD_Q25, _331
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s16i	a5, sp, 256	# prev_out_Q10, prev_out_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:154:                     prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ] = out0_Q10;
	s16i	a4, sp, 264	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	s32i	a2, sp, 304	# ind_sort, tmp792
.L53:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a2, a12, 4	# RD_Q25, _348
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a3, a12, 20	# RD_Q25, _350
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	blt	a3, a2, .L54	# _350, _348,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:157:                     RD_min_Q25[ j ] = RD_Q25[ j ];
	s32i	a2, sp, 292	# RD_min_Q25, _348
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	movi.n	a2, 1	# tmp802,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:158:                     RD_max_Q25[ j ] = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a3, sp, 276	# RD_max_Q25, _350
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	s32i	a2, sp, 308	# ind_sort, tmp802
	j	.L55		#
.L54:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:152:                     out0_Q10 = prev_out_Q10[ j ];
	l16si	a4, sp, 258	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	l16ui	a5, sp, 266	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:147:                     RD_max_Q25[ j ]                         = RD_Q25[ j ];
	s32i	a2, sp, 276	# RD_max_Q25, _348
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:150:                     RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] = RD_max_Q25[ j ];
	s32i.n	a2, a12, 20	# RD_Q25, _348
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	movi.n	a2, 5	# tmp819,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:148:                     RD_min_Q25[ j ]                         = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a3, sp, 292	# RD_min_Q25, _350
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:149:                     RD_Q25[ j ]                             = RD_min_Q25[ j ];
	s32i.n	a3, a12, 4	# RD_Q25, _350
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s16i	a5, sp, 258	# prev_out_Q10, prev_out_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:154:                     prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ] = out0_Q10;
	s16i	a4, sp, 266	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	s32i	a2, sp, 308	# ind_sort, tmp819
.L55:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a2, a12, 8	# RD_Q25, _367
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a3, a12, 24	# RD_Q25, _369
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	blt	a3, a2, .L56	# _369, _367,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:157:                     RD_min_Q25[ j ] = RD_Q25[ j ];
	s32i	a2, sp, 296	# RD_min_Q25, _367
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	movi.n	a2, 2	# tmp829,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:158:                     RD_max_Q25[ j ] = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a3, sp, 280	# RD_max_Q25, _369
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	s32i	a2, sp, 312	# ind_sort, tmp829
	j	.L57		#
.L56:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:152:                     out0_Q10 = prev_out_Q10[ j ];
	l16si	a4, sp, 260	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	l16ui	a5, sp, 268	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:147:                     RD_max_Q25[ j ]                         = RD_Q25[ j ];
	s32i	a2, sp, 280	# RD_max_Q25, _367
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:150:                     RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] = RD_max_Q25[ j ];
	s32i.n	a2, a12, 24	# RD_Q25, _367
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	movi.n	a2, 6	# tmp846,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:148:                     RD_min_Q25[ j ]                         = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a3, sp, 296	# RD_min_Q25, _369
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:149:                     RD_Q25[ j ]                             = RD_min_Q25[ j ];
	s32i.n	a3, a12, 8	# RD_Q25, _369
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s16i	a5, sp, 260	# prev_out_Q10, prev_out_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:154:                     prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ] = out0_Q10;
	s16i	a4, sp, 268	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	s32i	a2, sp, 312	# ind_sort, tmp846
.L57:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a9, a12, 12	# RD_Q25, pretmp_683
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a10, a12, 28	# RD_Q25, pretmp_685
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	blt	a10, a9, .L58	# pretmp_685, pretmp_683,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	mov.n	a2, a9	# pretmp_683, pretmp_683
	movi.n	a3, 3	# tmp856,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:157:                     RD_min_Q25[ j ] = RD_Q25[ j ];
	s32i	a9, sp, 300	# RD_min_Q25, pretmp_683
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:158:                     RD_max_Q25[ j ] = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a10, sp, 284	# RD_max_Q25, pretmp_685
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:159:                     ind_sort[ j ] = j;
	mov.n	a9, a10	# pretmp_683, pretmp_685
	s32i	a3, sp, 316	# ind_sort, tmp856
	mov.n	a10, a2	# pretmp_685, pretmp_683
	s32i	a13, sp, 336	# %sfp, ivtmp$28
	j	.L69		#
.L58:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:152:                     out0_Q10 = prev_out_Q10[ j ];
	l16si	a2, sp, 262	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	l16ui	a3, sp, 270	# prev_out_Q10,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:154:                     prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ] = out0_Q10;
	s16i	a2, sp, 270	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	movi.n	a2, 7	# tmp873,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:147:                     RD_max_Q25[ j ]                         = RD_Q25[ j ];
	s32i	a9, sp, 284	# RD_max_Q25, pretmp_683
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:148:                     RD_min_Q25[ j ]                         = RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s32i	a10, sp, 300	# RD_min_Q25, pretmp_685
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:149:                     RD_Q25[ j ]                             = RD_min_Q25[ j ];
	s32i.n	a10, a12, 12	# RD_Q25, pretmp_685
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:150:                     RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] = RD_max_Q25[ j ];
	s32i.n	a9, a12, 28	# RD_Q25, pretmp_683
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:153:                     prev_out_Q10[ j ] = prev_out_Q10[ j + NLSF_QUANT_DEL_DEC_STATES ];
	s16i	a3, sp, 262	# prev_out_Q10, prev_out_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:155:                     ind_sort[ j ] = j + NLSF_QUANT_DEL_DEC_STATES;
	s32i	a2, sp, 316	# ind_sort, tmp873
	s32i	a13, sp, 336	# %sfp, ivtmp$28
	j	.L69		#
.L93:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:141:                 ind[ j ][ i ] = ind[ j - nStates ][ i ];
	movi	a5, 0xa0	#,
	add.n	a5, a5, sp	#,,
	add.n	a4, a5, a15	# tmp881,, i
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:141:                 ind[ j ][ i ] = ind[ j - nStates ][ i ];
	slli	a2, a8, 4	# tmp882, nStates,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:141:                 ind[ j ][ i ] = ind[ j - nStates ][ i ];
	l8ui	a4, a4, 0	# ind, _612
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:141:                 ind[ j ][ i ] = ind[ j - nStates ][ i ];
	add.n	a2, sp, a2	# tmp883,, tmp882
	add.n	a2, a2, a15	# tmp884, tmp883, i
	s8i	a4, a2, 160	# ind, _612
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:140:             for( j = nStates; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	bnei	a8, 2, .L60	# nStates,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:141:                 ind[ j ][ i ] = ind[ j - nStates ][ i ];
	l8ui	a3, a3, 0	# ind, _85
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:141:                 ind[ j ][ i ] = ind[ j - nStates ][ i ];
	add.n	a2, sp, a15	# tmp896,, i
	s8i	a3, a2, 208	# ind, _85
	j	.L60		#
.L69:
	l32i	a4, sp, 288	# RD_min_Q25, RD_min_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:170:                     if( min_max_Q25 > RD_max_Q25[ j ] ) {
	l32i	a8, sp, 272	# RD_max_Q25, min_max_Q25
	l32i	a2, sp, 276	# RD_max_Q25, _296
	movi.n	a3, 0	# tmp901,
	movltz	a4, a3, a4	# max_min_Q25, tmp901, RD_min_Q25
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:170:                     if( min_max_Q25 > RD_max_Q25[ j ] ) {
	bge	a2, a8, .L82	# _296, min_max_Q25,
	mov.n	a8, a2	# min_max_Q25, _296
	movi.n	a7, 5	# prephitmp_689,
	movi.n	a3, 0x10	# prephitmp_688,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:169:                 for( j = 0; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a5, 1	# ind_min_max,
	j	.L61		#
.L82:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:170:                     if( min_max_Q25 > RD_max_Q25[ j ] ) {
	movi.n	a7, 4	# prephitmp_689,
	mov.n	a5, a3	# ind_min_max, prephitmp_688
.L61:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:174:                     if( max_min_Q25 < RD_min_Q25[ j ] ) {
	l32i	a2, sp, 292	# RD_min_Q25, _299
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:174:                     if( max_min_Q25 < RD_min_Q25[ j ] ) {
	bge	a4, a2, .L83	# max_min_Q25, _299,
	mov.n	a4, a2	# max_min_Q25, _299
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:169:                 for( j = 0; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a6, 1	# ind_max_min,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:174:                     if( max_min_Q25 < RD_min_Q25[ j ] ) {
	movi.n	a2, 0x10	# prephitmp_691,
	j	.L62		#
.L83:
	movi.n	a2, 0	# prephitmp_691,
	mov.n	a6, a2	# ind_max_min, prephitmp_691
.L62:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:170:                     if( min_max_Q25 > RD_max_Q25[ j ] ) {
	l32i	a11, sp, 280	# RD_max_Q25, _308
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:170:                     if( min_max_Q25 > RD_max_Q25[ j ] ) {
	bge	a11, a8, .L63	# _308, min_max_Q25,
	mov.n	a8, a11	# min_max_Q25, _308
	movi.n	a7, 6	# prephitmp_689,
	movi.n	a3, 0x20	# prephitmp_688,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:169:                 for( j = 0; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a5, 2	# ind_min_max,
.L63:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:174:                     if( max_min_Q25 < RD_min_Q25[ j ] ) {
	l32i	a11, sp, 296	# RD_min_Q25, _311
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:174:                     if( max_min_Q25 < RD_min_Q25[ j ] ) {
	bge	a4, a11, .L64	# max_min_Q25, _311,
	mov.n	a4, a11	# max_min_Q25, _311
	movi.n	a2, 0x20	# prephitmp_691,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:169:                 for( j = 0; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a6, 2	# ind_max_min,
.L64:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:170:                     if( min_max_Q25 > RD_max_Q25[ j ] ) {
	bge	a9, a8, .L65	# pretmp_683, min_max_Q25,
	mov.n	a8, a9	# min_max_Q25, pretmp_683
	movi.n	a7, 7	# prephitmp_689,
	movi.n	a3, 0x30	# prephitmp_688,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:169:                 for( j = 0; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a5, 3	# ind_min_max,
.L65:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:174:                     if( max_min_Q25 < RD_min_Q25[ j ] ) {
	bge	a4, a10, .L66	# max_min_Q25, pretmp_685,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:179:                 if( min_max_Q25 >= max_min_Q25 ) {
	bge	a8, a10, .L67	# min_max_Q25, pretmp_685,
	movi.n	a2, 0x30	# prephitmp_691,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:169:                 for( j = 0; j < NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a6, 3	# ind_max_min,
	j	.L68		#
.L66:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:179:                 if( min_max_Q25 >= max_min_Q25 ) {
	blt	a8, a4, .L68	# min_max_Q25, max_min_Q25,
.L67:
	l32i	a13, sp, 336	# %sfp, ivtmp$28
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:192:                 ind[ j ][ i ] += silk_RSHIFT( ind_sort[ j ], NLSF_QUANT_DEL_DEC_STATES_LOG2 );
	l32i	a5, sp, 304	# ind_sort, ind_sort
	l32i	a4, sp, 308	# ind_sort, ind_sort
	l32i	a3, sp, 312	# ind_sort, ind_sort
	l32i	a2, sp, 316	# ind_sort, ind_sort
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:192:                 ind[ j ][ i ] += silk_RSHIFT( ind_sort[ j ], NLSF_QUANT_DEL_DEC_STATES_LOG2 );
	l8ui	a9, a13, 0	# MEM[base: _423, offset: 0B],
	l8ui	a8, a13, 16	# MEM[base: _423, offset: 16B],
	l8ui	a7, a13, 32	# MEM[base: _423, offset: 32B],
	l8ui	a6, a13, 48	# MEM[base: _423, offset: 48B],
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:192:                 ind[ j ][ i ] += silk_RSHIFT( ind_sort[ j ], NLSF_QUANT_DEL_DEC_STATES_LOG2 );
	srai	a5, a5, 2	# tmp907, ind_sort,
	srai	a4, a4, 2	# tmp913, ind_sort,
	srai	a3, a3, 2	# tmp919, ind_sort,
	srai	a2, a2, 2	# tmp925, ind_sort,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:192:                 ind[ j ][ i ] += silk_RSHIFT( ind_sort[ j ], NLSF_QUANT_DEL_DEC_STATES_LOG2 );
	add.n	a5, a5, a9	# tmp911, tmp907, MEM[base: _423, offset: 0B]
	add.n	a4, a4, a8	# tmp917, tmp913, MEM[base: _423, offset: 16B]
	add.n	a3, a3, a7	# tmp923, tmp919, MEM[base: _423, offset: 32B]
	add.n	a2, a2, a6	# tmp929, tmp925, MEM[base: _423, offset: 48B]
	s8i	a5, a13, 0	# MEM[base: _423, offset: 0B], tmp911
	s8i	a4, a13, 16	# MEM[base: _423, offset: 16B], tmp917
	s8i	a3, a13, 32	# MEM[base: _423, offset: 32B], tmp923
	s8i	a2, a13, 48	# MEM[base: _423, offset: 48B], tmp929
	j	.L60		#
.L68:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:185:                 prev_out_Q10[ ind_max_min ] = prev_out_Q10[ ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	slli	a4, a7, 1	# tmp952, prephitmp_689,
	addmi	a10, sp, 0x100	#,,
	add.n	a4, a10, a4	# tmp953,, tmp952
	l16si	a10, a4, 0	# prev_out_Q10, _97
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	addmi	a13, sp, 0x100	#,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	addmi	a8, sp, 0x100	#,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:184:                 RD_Q25[       ind_max_min ] = RD_Q25[       ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	slli	a9, a7, 2	# tmp944, prephitmp_689,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	slli	a5, a5, 2	# tmp935, ind_min_max,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	slli	a7, a6, 2	# tmp931, ind_max_min,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:185:                 prev_out_Q10[ ind_max_min ] = prev_out_Q10[ ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	slli	a6, a6, 1	# tmp957, ind_max_min,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	add.n	a5, a8, a5	# tmp936,, tmp935
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:185:                 prev_out_Q10[ ind_max_min ] = prev_out_Q10[ ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	add.n	a6, a13, a6	# tmp958,, tmp957
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:184:                 RD_Q25[       ind_max_min ] = RD_Q25[       ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	add.n	a9, a12, a9	# tmp945, tmp514, tmp944
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	l32i.n	a8, a5, 48	# ind_sort, tmp940
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:184:                 RD_Q25[       ind_max_min ] = RD_Q25[       ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	l32i.n	a11, a9, 0	# RD_Q25, _95
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:185:                 prev_out_Q10[ ind_max_min ] = prev_out_Q10[ ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	s16i	a10, a6, 0	# prev_out_Q10, _97
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	add.n	a9, a13, a7	# tmp932,, tmp931
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:186:                 RD_min_Q25[   ind_max_min ] = 0;
	movi.n	a6, 0	# tmp963,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:188:                 silk_memcpy( ind[ ind_max_min ], ind[ ind_min_max ], MAX_LPC_ORDER * sizeof( opus_int8 ) );
	movi	a13, 0xa0	#,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:186:                 RD_min_Q25[   ind_max_min ] = 0;
	s32i.n	a6, a9, 32	# RD_min_Q25, tmp963
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	movi.n	a4, 4	# tmp938,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:188:                 silk_memcpy( ind[ ind_max_min ], ind[ ind_min_max ], MAX_LPC_ORDER * sizeof( opus_int8 ) );
	add.n	a13, a13, sp	#,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:187:                 RD_max_Q25[   ind_min_max ] = silk_int32_MAX;
	l32r	a6, .LC1	#, tmp968
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	xor	a8, a8, a4	# tmp939, tmp940, tmp938
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:184:                 RD_Q25[       ind_max_min ] = RD_Q25[       ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	add.n	a7, a12, a7	# tmp950, tmp514, tmp931
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:188:                 silk_memcpy( ind[ ind_max_min ], ind[ ind_min_max ], MAX_LPC_ORDER * sizeof( opus_int8 ) );
	movi.n	a4, 0x10	#,
	add.n	a3, a13, a3	#,, prephitmp_688
	add.n	a2, a13, a2	#,, prephitmp_691
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:183:                 ind_sort[     ind_max_min ] = ind_sort[     ind_min_max ] ^ NLSF_QUANT_DEL_DEC_STATES;
	s32i.n	a8, a9, 48	# ind_sort, tmp939
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:184:                 RD_Q25[       ind_max_min ] = RD_Q25[       ind_min_max + NLSF_QUANT_DEL_DEC_STATES ];
	s32i.n	a11, a7, 0	# RD_Q25, _95
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:187:                 RD_max_Q25[   ind_min_max ] = silk_int32_MAX;
	s32i.n	a6, a5, 16	# RD_max_Q25, tmp968
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:188:                 silk_memcpy( ind[ ind_max_min ], ind[ ind_min_max ], MAX_LPC_ORDER * sizeof( opus_int8 ) );
	call0	memcpy		#
	l32i	a9, sp, 284	# RD_max_Q25, pretmp_683
	l32i	a10, sp, 300	# RD_min_Q25, pretmp_685
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:165:                 min_max_Q25 = silk_int32_MAX;
	j	.L69		#
.L60:
	l32i	a5, sp, 324	# %sfp,
	l32i	a6, sp, 328	# %sfp,
	addi	a5, a5, -2	#,,
	addi	a6, a6, -2	#,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:87:     for( i = order - 1; i >= 0; i-- ) {
	addi.n	a15, a15, -1	# i, i,
	s32i	a5, sp, 324	# %sfp,
	s32i	a6, sp, 328	# %sfp,
	addi.n	a13, a13, -1	# ivtmp$28, ivtmp$28,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:87:     for( i = order - 1; i >= 0; i-- ) {
	beqi	a15, -1, .L94	# i,,
	slli	a2, a15, 1	# tmp1027, i,
	mov.n	a10, a6	#,
	mov.n	a11, a5	#,
	j	.L70		#
.L16:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	mov.n	a12, a2	# <retval>, _109
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:200:     for( j = 0; j < 2 * NLSF_QUANT_DEL_DEC_STATES; j++ ) {
	movi.n	a13, 7	# ind_tmp,
.L17:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:206:     for( j = 0; j < order; j++ ) {
	l32i	a8, sp, 364	# %sfp,
	blti	a8, 1, .L73	#,,
	extui	a3, a13, 0, 2	# tmp988, ind_tmp,
	movi	a10, 0xa0	#,
	add.n	a10, a10, sp	#,,
	slli	a3, a3, 4	# tmp989, tmp988,
	l32i	a2, sp, 360	# %sfp,
	mov.n	a4, a8	#,
	add.n	a3, a10, a3	#,, tmp989
	call0	memcpy		#
	j	.L73		#
.L45:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	l32i	a11, sp, 344	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	l32i	a3, sp, 340	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	add.n	a7, a11, a2	# tmp996,, _652
	slli	a7, a7, 16	# tmp997, tmp996,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	add.n	a2, a3, a2	# tmp998,, _652
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	addmi	a9, sp, 0x100	#,,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:101:             out0_Q10  = silk_ADD16( out0_Q10, pred_Q10 );
	srai	a7, a7, 16	# out0_Q10, tmp997,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	slli	a2, a2, 16	# tmp999, tmp998,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	slli	a3, a8, 1	# tmp1002, _653,
	add.n	a3, a9, a3	# tmp1003,, tmp1002
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:102:             out1_Q10  = silk_ADD16( out1_Q10, pred_Q10 );
	srai	a2, a2, 16	# out1_Q10, tmp999,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:103:             prev_out_Q10[ j           ] = out0_Q10;
	s16i	a7, sp, 262	# prev_out_Q10, out0_Q10
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:95:             ind[ j ][ i ] = (opus_int8)ind_tmp;
	s8i	a5, a13, 48	# MEM[base: _602, offset: 48B], tmp701
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:104:             prev_out_Q10[ j + nStates ] = out1_Q10;
	s16i	a2, a3, 0	# prev_out_Q10, out1_Q10
	movi	a9, 0x21a	# rate1_Q5,
	movi	a10, 0x1ef	# rate0_Q5,
	j	.L49		#
.L6:
	addmi	a3, a2, 0x400	# tmp1004, _698,
	slli	a3, a3, 16	# tmp1005, tmp1004,
	srai	a3, a3, 16	# out1_Q10, tmp1005,
.L5:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:78:         out0_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out0_Q10, quant_step_size_Q16 ), 16 );
	mull	a2, a5, a9	# tmp1006, out0_Q10, _709
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:79:         out1_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out1_Q10, quant_step_size_Q16 ), 16 );
	mull	a3, a3, a9	# tmp1008, out1_Q10, _709
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:78:         out0_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out0_Q10, quant_step_size_Q16 ), 16 );
	srai	a2, a2, 16	# tmp1007, tmp1006,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:79:         out1_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out1_Q10, quant_step_size_Q16 ), 16 );
	srai	a3, a3, 16	# tmp1009, tmp1008,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:79:         out1_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out1_Q10, quant_step_size_Q16 ), 16 );
	s32i.n	a3, a7, 0	# MEM[base: _576, offset: 0B], tmp1009
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:78:         out0_Q10_table[ i + NLSF_QUANT_MAX_AMPLITUDE_EXT ] = silk_RSHIFT( silk_SMULBB( out0_Q10, quant_step_size_Q16 ), 16 );
	s32i.n	a2, a10, 0	# MEM[base: _600, offset: 0B], tmp1007
	add.n	a3, a8, a11	# ivtmp$44, ivtmp$44, _720
	j	.L3		#
.L92:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:201:         if( min_Q25 > RD_Q25[ j ] ) {
	mov.n	a12, a2	# <retval>, tmp413
	j	.L75		#
.L35:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	l8ui	a3, a13, 0	# MEM[base: _584, offset: 0B],
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	add.n	a2, sp, a15	# tmp1015,, i
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	addi.n	a3, a3, 1	# tmp1019, MEM[base: _584, offset: 0B],
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	s8i	a3, a2, 192	# ind, tmp1019
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	l8ui	a3, a13, 16	# MEM[base: _584, offset: 16B],
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:139:             nStates = silk_LSHIFT( nStates, 1 );
	movi.n	a14, 4	# nStates,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	addi.n	a3, a3, 1	# tmp878, MEM[base: _584, offset: 16B],
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:137:                 ind[ j + nStates ][ i ] = ind[ j ][ i ] + 1;
	s8i	a3, a2, 208	# ind, tmp878
	j	.L60		#
.L44:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a2, a12, 0	# RD_Q25, _329
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	l32i.n	a3, a12, 16	# RD_Q25, _331
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:146:                 if( RD_Q25[ j ] > RD_Q25[ j + NLSF_QUANT_DEL_DEC_STATES ] ) {
	blt	a3, a2, .L77	# _331, _329,
	j	.L96		#
.L73:
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:211:     indices[ 0 ] += silk_RSHIFT( ind_tmp, NLSF_QUANT_DEL_DEC_STATES_LOG2 );
	l32i	a9, sp, 360	# %sfp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:211:     indices[ 0 ] += silk_RSHIFT( ind_tmp, NLSF_QUANT_DEL_DEC_STATES_LOG2 );
	srai	a2, a13, 2	# tmp981, ind_tmp,
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:211:     indices[ 0 ] += silk_RSHIFT( ind_tmp, NLSF_QUANT_DEL_DEC_STATES_LOG2 );
	l8ui	a3, a9, 0	# *indices_234(D),
	add.n	a2, a2, a3	# tmp984, tmp981, *indices_234(D)
	s8i	a2, a9, 0	# *indices_234(D), tmp984
# @OPUS@\upstream\silk\NLSF_del_dec_quant.c:215: }
	l32i	a0, sp, 396	#,
	movi	a9, 0x190	#,
	mov.n	a2, a12	#, <retval>
	l32i	a13, sp, 388	#,
	l32i	a12, sp, 392	#,
	l32i	a14, sp, 384	#,
	l32i	a15, sp, 380	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_NLSF_del_dec_quant, .-silk_NLSF_del_dec_quant
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
