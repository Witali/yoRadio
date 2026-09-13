# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/quant_LTP_gains.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"quant_LTP_gains.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\quant_LTP_gains.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\quant_LTP_gains.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\quant_LTP_gains.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\quant_LTP_gains.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\quant_LTP_gains.c.s.raw
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
	.section	.text.silk_quant_LTP_gains,"ax",@progbits
	.literal_position
	.literal .LC0, 2147483647
	.literal .LC1, silk_LTP_gain_BITS_Q5_ptrs
	.literal .LC2, silk_LTP_vq_ptrs_Q7
	.literal .LC3, silk_LTP_vq_gain_ptrs_Q7
	.literal .LC4, silk_LTP_vq_sizes
	.literal .LC5, 6229
	.align	4
	.global	silk_quant_LTP_gains
	.type	silk_quant_LTP_gains, @function
# Function: silk_quant_LTP_gains
# Module: upstream/silk/quant_LTP_gains.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context: #include "tuning_parameters.h"
# C context:
# C context: void silk_quant_LTP_gains(
# C context: opus_int16                  B_Q14[ MAX_NB_SUBFR * LTP_ORDER ],          /* O    Quantized LTP gains             */
# C context: opus_int8                   cbk_index[ MAX_NB_SUBFR ],                  /* O    Codebook Index                  */
# C context: opus_int8                   *periodicity_index,                         /* O    Periodicity Index               */
# C context: opus_int32                  *sum_log_gain_Q7,                           /* I/O  Cumulative max prediction gain  */
silk_quant_LTP_gains:
	movi	a9, 0xa0	#,
	sub	sp, sp, a9	#,,
	s32i	a2, sp, 104	# %sfp, B_Q14
# @OPUS@\upstream\silk\quant_LTP_gains.c:62:     min_rate_dist_Q7 = silk_int32_MAX;
	l32r	a2, .LC0	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:63:     best_sum_log_gain_Q7 = 0;
	movi.n	a8, 0	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:47: {
	s32i	a0, sp, 156	#,
	s32i	a12, sp, 152	#,
	s32i	a13, sp, 148	#,
	s32i	a14, sp, 144	#,
	s32i	a15, sp, 140	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:63:     best_sum_log_gain_Q7 = 0;
	s32i	a8, sp, 84	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:47: {
	s32i	a3, sp, 96	# %sfp, cbk_index
	s32i	a4, sp, 100	# %sfp, periodicity_index
	s32i	a5, sp, 80	# %sfp, sum_log_gain_Q7
	s32i	a6, sp, 108	# %sfp, pred_gain_dB_Q7
	s32i	a7, sp, 92	# %sfp, XX_Q17
# @OPUS@\upstream\silk\quant_LTP_gains.c:62:     min_rate_dist_Q7 = silk_int32_MAX;
	s32i	a2, sp, 88	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:64:     for( k = 0; k < 3; k++ ) {
	s32i	a8, sp, 76	# %sfp,
.L8:
# @OPUS@\upstream\silk\quant_LTP_gains.c:72:         cbk_size   = silk_LTP_vq_sizes[          k ];
	l32i	a8, sp, 76	# %sfp,
	l32r	a3, .LC4	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:69:         cl_ptr_Q5  = silk_LTP_gain_BITS_Q5_ptrs[ k ];
	l32r	a4, .LC1	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:72:         cbk_size   = silk_LTP_vq_sizes[          k ];
	add.n	a2, a3, a8	# tmp170,,
# @OPUS@\upstream\silk\quant_LTP_gains.c:72:         cbk_size   = silk_LTP_vq_sizes[          k ];
	l8ui	a3, a2, 0	# MEM[base: _202, offset: 0B],
# @OPUS@\upstream\silk\quant_LTP_gains.c:70:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[        k ];
	l32r	a6, .LC2	#,
	slli	a2, a8, 2	# _228,,
# @OPUS@\upstream\silk\quant_LTP_gains.c:71:         cbk_gain_ptr_Q7 = silk_LTP_vq_gain_ptrs_Q7[ k ];
	l32r	a8, .LC3	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:69:         cl_ptr_Q5  = silk_LTP_gain_BITS_Q5_ptrs[ k ];
	add.n	a5, a4, a2	# tmp164,, _228
# @OPUS@\upstream\silk\quant_LTP_gains.c:70:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[        k ];
	add.n	a4, a6, a2	# tmp166,, _228
# @OPUS@\upstream\silk\quant_LTP_gains.c:71:         cbk_gain_ptr_Q7 = silk_LTP_vq_gain_ptrs_Q7[ k ];
	add.n	a2, a8, a2	# tmp168,, _228
# @OPUS@\upstream\silk\quant_LTP_gains.c:80:         sum_log_gain_tmp_Q7 = *sum_log_gain_Q7;
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:72:         cbk_size   = silk_LTP_vq_sizes[          k ];
	slli	a3, a3, 24	# tmp173, MEM[base: _202, offset: 0B],
# @OPUS@\upstream\silk\quant_LTP_gains.c:69:         cl_ptr_Q5  = silk_LTP_gain_BITS_Q5_ptrs[ k ];
	l32i.n	a5, a5, 0	# MEM[base: _227, offset: 0B],
# @OPUS@\upstream\silk\quant_LTP_gains.c:70:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[        k ];
	l32i.n	a4, a4, 0	# MEM[base: _224, offset: 0B],
# @OPUS@\upstream\silk\quant_LTP_gains.c:71:         cbk_gain_ptr_Q7 = silk_LTP_vq_gain_ptrs_Q7[ k ];
	l32i.n	a2, a2, 0	# MEM[base: _205, offset: 0B],
# @OPUS@\upstream\silk\quant_LTP_gains.c:72:         cbk_size   = silk_LTP_vq_sizes[          k ];
	srai	a3, a3, 24	#, tmp173,
# @OPUS@\upstream\silk\quant_LTP_gains.c:80:         sum_log_gain_tmp_Q7 = *sum_log_gain_Q7;
	l32i.n	a10, a8, 0	# *sum_log_gain_Q7_84(D), sum_log_gain_tmp_Q7
# @OPUS@\upstream\silk\quant_LTP_gains.c:81:         for( j = 0; j < nb_subfr; j++ ) {
	l32i	a8, sp, 168	# nb_subfr,
# @OPUS@\upstream\silk\quant_LTP_gains.c:69:         cl_ptr_Q5  = silk_LTP_gain_BITS_Q5_ptrs[ k ];
	s32i.n	a5, sp, 56	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:70:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[        k ];
	s32i.n	a4, sp, 60	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:71:         cbk_gain_ptr_Q7 = silk_LTP_vq_gain_ptrs_Q7[ k ];
	s32i	a2, sp, 64	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:72:         cbk_size   = silk_LTP_vq_sizes[          k ];
	s32i	a3, sp, 68	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:81:         for( j = 0; j < nb_subfr; j++ ) {
	blti	a8, 1, .L15	#,,
	addi	a12, sp, 32	# ivtmp$28,,
	add.n	a2, a12, a8	#, tmp2,
# @OPUS@\upstream\silk\quant_LTP_gains.c:75:         XX_Q17_ptr = XX_Q17;
	l32i	a8, sp, 92	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:79:         rate_dist_Q7 = 0;
	movi.n	a13, 0	# rate_dist_Q7,
# @OPUS@\upstream\silk\quant_LTP_gains.c:76:         xX_Q17_ptr = xX_Q17;
	l32i	a14, sp, 160	# xX_Q17, xX_Q17_ptr
	s32i	a2, sp, 72	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:75:         XX_Q17_ptr = XX_Q17;
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:78:         res_nrg_Q15 = 0;
	mov.n	a15, a13	# res_nrg_Q15, rate_dist_Q7
.L6:
# @OPUS@\upstream\silk\quant_LTP_gains.c:82:             max_gain_Q7 = silk_log2lin( ( SILK_FIX_CONST( MAX_SUM_LOG_GAIN_DB / 6.0, 7 ) - sum_log_gain_tmp_Q7 )
	l32r	a3, .LC5	#,
	s32i	a10, sp, 112	#,
	sub	a2, a3, a10	#,, sum_log_gain_tmp_Q7
	call0	silk_log2lin		#
# @OPUS@\upstream\silk\quant_LTP_gains.c:84:             silk_VQ_WMat_EC(
	l32i	a8, sp, 68	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:82:             max_gain_Q7 = silk_log2lin( ( SILK_FIX_CONST( MAX_SUM_LOG_GAIN_DB / 6.0, 7 ) - sum_log_gain_tmp_Q7 )
	addi	a11, a2, -51	# max_gain_Q7,,
# @OPUS@\upstream\silk\quant_LTP_gains.c:84:             silk_VQ_WMat_EC(
	s32i.n	a8, sp, 20	#,
	l32i	a8, sp, 164	# subfr_len,
	l32i.n	a6, sp, 48	# %sfp,
	s32i.n	a8, sp, 12	#,
	l32i.n	a8, sp, 56	# %sfp,
	addi	a4, sp, 40	#,,
	s32i.n	a8, sp, 8	#,
	l32i	a8, sp, 64	# %sfp,
	mov.n	a2, a12	#, ivtmp$28
	s32i.n	a8, sp, 4	#,
	l32i.n	a8, sp, 60	# %sfp,
	mov.n	a7, a14	#, xX_Q17_ptr
	addi	a5, sp, 36	#,,
	addi	a3, sp, 44	#,,
	s32i.n	a11, sp, 16	#, max_gain_Q7
	s32i.n	a8, sp, 0	#,
	call0	silk_VQ_WMat_EC_c		#
	l32i	a10, sp, 112	#,
	movi	a3, -0x380	#,
	add.n	a10, a10, a3	#, sum_log_gain_tmp_Q7,
# @OPUS@\upstream\silk\quant_LTP_gains.c:100:             res_nrg_Q15  = silk_ADD_POS_SAT32( res_nrg_Q15, res_nrg_Q15_subfr );
	l32i.n	a3, sp, 44	# res_nrg_Q15_subfr, res_nrg_Q15_subfr
# @OPUS@\upstream\silk\quant_LTP_gains.c:102:             sum_log_gain_tmp_Q7 = silk_max(0, sum_log_gain_tmp_Q7
	l32i.n	a2, sp, 36	# gain_Q7, gain_Q7
# @OPUS@\upstream\silk\quant_LTP_gains.c:100:             res_nrg_Q15  = silk_ADD_POS_SAT32( res_nrg_Q15, res_nrg_Q15_subfr );
	add.n	a15, a15, a3	# res_nrg_Q15, res_nrg_Q15, res_nrg_Q15_subfr
# @OPUS@\upstream\silk\quant_LTP_gains.c:101:             rate_dist_Q7 = silk_ADD_POS_SAT32( rate_dist_Q7, rate_dist_Q7_subfr );
	l32i.n	a3, sp, 40	# rate_dist_Q7_subfr, rate_dist_Q7_subfr
# @OPUS@\upstream\silk\quant_LTP_gains.c:102:             sum_log_gain_tmp_Q7 = silk_max(0, sum_log_gain_tmp_Q7
	addi	a2, a2, 51	#, gain_Q7,
	s32i.n	a10, sp, 52	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:101:             rate_dist_Q7 = silk_ADD_POS_SAT32( rate_dist_Q7, rate_dist_Q7_subfr );
	add.n	a13, a13, a3	# rate_dist_Q7, rate_dist_Q7, rate_dist_Q7_subfr
# @OPUS@\upstream\silk\quant_LTP_gains.c:102:             sum_log_gain_tmp_Q7 = silk_max(0, sum_log_gain_tmp_Q7
	call0	silk_lin2log		#
	l32i.n	a4, sp, 52	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:100:             res_nrg_Q15  = silk_ADD_POS_SAT32( res_nrg_Q15, res_nrg_Q15_subfr );
	l32r	a6, .LC0	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:102:             sum_log_gain_tmp_Q7 = silk_max(0, sum_log_gain_tmp_Q7
	add.n	a2, a2, a4	# tmp185,,
	movi.n	a10, 0	# sum_log_gain_tmp_Q7,
	addi.n	a12, a12, 1	# ivtmp$28, ivtmp$28,
# @OPUS@\upstream\silk\quant_LTP_gains.c:100:             res_nrg_Q15  = silk_ADD_POS_SAT32( res_nrg_Q15, res_nrg_Q15_subfr );
	movltz	a15, a6, a15	# res_nrg_Q15,, res_nrg_Q15
# @OPUS@\upstream\silk\quant_LTP_gains.c:101:             rate_dist_Q7 = silk_ADD_POS_SAT32( rate_dist_Q7, rate_dist_Q7_subfr );
	movltz	a13, a6, a13	# rate_dist_Q7,, rate_dist_Q7
# @OPUS@\upstream\silk\quant_LTP_gains.c:102:             sum_log_gain_tmp_Q7 = silk_max(0, sum_log_gain_tmp_Q7
	blt	a2, a10, .L5	# tmp185,,
# @OPUS@\upstream\silk\quant_LTP_gains.c:102:             sum_log_gain_tmp_Q7 = silk_max(0, sum_log_gain_tmp_Q7
	l32i.n	a2, sp, 36	# gain_Q7, gain_Q7
	addi	a2, a2, 51	#, gain_Q7,
	call0	silk_lin2log		#
	l32i.n	a8, sp, 52	# %sfp,
	add.n	a10, a2, a8	# sum_log_gain_tmp_Q7,,
.L5:
# @OPUS@\upstream\silk\quant_LTP_gains.c:105:             XX_Q17_ptr += LTP_ORDER * LTP_ORDER;
	l32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:106:             xX_Q17_ptr += LTP_ORDER;
	addi	a14, a14, 20	# xX_Q17_ptr, xX_Q17_ptr,
# @OPUS@\upstream\silk\quant_LTP_gains.c:105:             XX_Q17_ptr += LTP_ORDER * LTP_ORDER;
	addi	a8, a8, 100	#,,
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:81:         for( j = 0; j < nb_subfr; j++ ) {
	l32i	a8, sp, 72	# %sfp,
	bne	a8, a12, .L6	#, ivtmp$28,
# @OPUS@\upstream\silk\quant_LTP_gains.c:109:         if( rate_dist_Q7 <= min_rate_dist_Q7 ) {
	l32i	a8, sp, 88	# %sfp,
	blt	a8, a13, .L7	#, rate_dist_Q7,
	j	.L2		#
.L15:
# @OPUS@\upstream\silk\quant_LTP_gains.c:78:         res_nrg_Q15 = 0;
	movi.n	a15, 0	# res_nrg_Q15,
# @OPUS@\upstream\silk\quant_LTP_gains.c:79:         rate_dist_Q7 = 0;
	mov.n	a13, a15	# rate_dist_Q7, res_nrg_Q15
.L2:
# @OPUS@\upstream\silk\quant_LTP_gains.c:111:             *periodicity_index = (opus_int8)k;
	l32i	a2, sp, 76	# %sfp,
	l32i	a8, sp, 100	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:112:             silk_memcpy( cbk_index, temp_idx, nb_subfr * sizeof( opus_int8 ) );
	l32i	a4, sp, 168	# nb_subfr,
# @OPUS@\upstream\silk\quant_LTP_gains.c:111:             *periodicity_index = (opus_int8)k;
	s8i	a2, a8, 0	# *periodicity_index_99(D),
# @OPUS@\upstream\silk\quant_LTP_gains.c:112:             silk_memcpy( cbk_index, temp_idx, nb_subfr * sizeof( opus_int8 ) );
	l32i	a2, sp, 96	# %sfp,
	addi	a3, sp, 32	#,,
	s32i	a10, sp, 112	#,
	call0	memcpy		#
	l32i	a10, sp, 112	#,
	s32i	a13, sp, 88	# %sfp, rate_dist_Q7
	s32i	a10, sp, 84	# %sfp, sum_log_gain_tmp_Q7
.L7:
# @OPUS@\upstream\silk\quant_LTP_gains.c:64:     for( k = 0; k < 3; k++ ) {
	l32i	a8, sp, 76	# %sfp,
	addi.n	a8, a8, 1	#,,
	s32i	a8, sp, 76	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:64:     for( k = 0; k < 3; k++ ) {
	bnei	a8, 3, .L8	#,,
# @OPUS@\upstream\silk\quant_LTP_gains.c:117:     cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ *periodicity_index ];
	l32i	a8, sp, 100	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:117:     cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ *periodicity_index ];
	l32r	a4, .LC2	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:117:     cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ *periodicity_index ];
	l8ui	a3, a8, 0	# *periodicity_index_99(D),
	l32i	a2, sp, 96	# %sfp, ivtmp$17
	slli	a3, a3, 24	# tmp195, *periodicity_index_99(D),
# @OPUS@\upstream\silk\quant_LTP_gains.c:117:     cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ *periodicity_index ];
	srai	a3, a3, 22	# tmp196, tmp195,
	l32i	a8, sp, 168	# nb_subfr,
	add.n	a3, a4, a3	# tmp197,, tmp196
	l32i.n	a5, a3, 0	# silk_LTP_vq_ptrs_Q7, cbk_ptr_Q7
	add.n	a6, a2, a8	# _236, ivtmp$17,
	l32i	a3, sp, 104	# %sfp, ivtmp$18
# @OPUS@\upstream\silk\quant_LTP_gains.c:118:     for( j = 0; j < nb_subfr; j++ ) {
	bgei	a8, 1, .L12	#,,
	j	.L10		#
.L24:
# @OPUS@\upstream\silk\quant_LTP_gains.c:124:     if( nb_subfr == 2 ) {
	l32i	a8, sp, 168	# nb_subfr,
# @OPUS@\upstream\silk\quant_LTP_gains.c:125:         res_nrg_Q15 = silk_RSHIFT32( res_nrg_Q15, 1 );
	srai	a2, a15, 1	# res_nrg_Q15, res_nrg_Q15,
# @OPUS@\upstream\silk\quant_LTP_gains.c:124:     if( nb_subfr == 2 ) {
	bnei	a8, 2, .L10	#,,
	j	.L14		#
.L12:
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	l8ui	a4, a2, 0	# MEM[base: _251, offset: 0B],
	slli	a4, a4, 24	# tmp201, MEM[base: _251, offset: 0B],
	srai	a4, a4, 24	# tmp202, tmp201,
	slli	a7, a4, 2	# tmp205, tmp202,
	add.n	a4, a7, a4	# tmp206, tmp205, tmp202
	add.n	a4, a5, a4	# tmp207, cbk_ptr_Q7, tmp206
	l8ui	a4, a4, 0	# *_127,
	slli	a4, a4, 24	# tmp210, *_127,
	srai	a4, a4, 17	# tmp211, tmp210,
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	s16i	a4, a3, 0	# MEM[base: _250, offset: 0B], tmp211
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	l8ui	a4, a2, 0	# MEM[base: _251, offset: 0B],
	slli	a4, a4, 24	# tmp215, MEM[base: _251, offset: 0B],
	srai	a4, a4, 24	# tmp216, tmp215,
	slli	a7, a4, 2	# tmp219, tmp216,
	add.n	a4, a7, a4	# tmp220, tmp219, tmp216
	add.n	a4, a5, a4	# tmp221, cbk_ptr_Q7, tmp220
	l8ui	a4, a4, 1	# *_148,
	slli	a4, a4, 24	# tmp225, *_148,
	srai	a4, a4, 17	# tmp226, tmp225,
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	s16i	a4, a3, 2	# MEM[base: _250, offset: 2B], tmp226
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	l8ui	a4, a2, 0	# MEM[base: _251, offset: 0B],
	slli	a4, a4, 24	# tmp230, MEM[base: _251, offset: 0B],
	srai	a4, a4, 24	# tmp231, tmp230,
	slli	a7, a4, 2	# tmp234, tmp231,
	add.n	a4, a7, a4	# tmp235, tmp234, tmp231
	add.n	a4, a5, a4	# tmp236, cbk_ptr_Q7, tmp235
	l8ui	a4, a4, 2	# *_169,
	slli	a4, a4, 24	# tmp240, *_169,
	srai	a4, a4, 17	# tmp241, tmp240,
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	s16i	a4, a3, 4	# MEM[base: _250, offset: 4B], tmp241
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	l8ui	a4, a2, 0	# MEM[base: _251, offset: 0B],
	slli	a4, a4, 24	# tmp245, MEM[base: _251, offset: 0B],
	srai	a4, a4, 24	# tmp246, tmp245,
	slli	a7, a4, 2	# tmp249, tmp246,
	add.n	a4, a7, a4	# tmp250, tmp249, tmp246
	add.n	a4, a5, a4	# tmp251, cbk_ptr_Q7, tmp250
	l8ui	a4, a4, 3	# *_190,
	slli	a4, a4, 24	# tmp255, *_190,
	srai	a4, a4, 17	# tmp256, tmp255,
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	s16i	a4, a3, 6	# MEM[base: _250, offset: 6B], tmp256
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	l8ui	a4, a2, 0	# MEM[base: _251, offset: 0B],
	addi.n	a2, a2, 1	# ivtmp$17, ivtmp$17,
	slli	a4, a4, 24	# tmp260, MEM[base: _251, offset: 0B],
	srai	a4, a4, 24	# tmp261, tmp260,
	slli	a7, a4, 2	# tmp264, tmp261,
	add.n	a4, a7, a4	# tmp265, tmp264, tmp261
	add.n	a4, a5, a4	# tmp266, cbk_ptr_Q7, tmp265
	l8ui	a4, a4, 4	# *_211,
	slli	a4, a4, 24	# tmp270, *_211,
	srai	a4, a4, 17	# tmp271, tmp270,
# @OPUS@\upstream\silk\quant_LTP_gains.c:120:             B_Q14[ j * LTP_ORDER + k ] = silk_LSHIFT( cbk_ptr_Q7[ cbk_index[ j ] * LTP_ORDER + k ], 7 );
	s16i	a4, a3, 8	# MEM[base: _250, offset: 8B], tmp271
	addi.n	a3, a3, 10	# ivtmp$18, ivtmp$18,
# @OPUS@\upstream\silk\quant_LTP_gains.c:118:     for( j = 0; j < nb_subfr; j++ ) {
	bne	a6, a2, .L12	# _236, ivtmp$17,
	j	.L24		#
.L10:
# @OPUS@\upstream\silk\quant_LTP_gains.c:127:         res_nrg_Q15 = silk_RSHIFT32( res_nrg_Q15, 2 );
	srai	a2, a15, 2	# res_nrg_Q15, res_nrg_Q15,
.L14:
# @OPUS@\upstream\silk\quant_LTP_gains.c:130:     *sum_log_gain_Q7 = best_sum_log_gain_Q7;
	l32i	a3, sp, 84	# %sfp,
	l32i	a8, sp, 80	# %sfp,
	s32i.n	a3, a8, 0	# *sum_log_gain_Q7_84(D),
# @OPUS@\upstream\silk\quant_LTP_gains.c:131:     *pred_gain_dB_Q7 = (opus_int)silk_SMULBB( -3, silk_lin2log( res_nrg_Q15 ) - ( 15 << 7 ) );
	call0	silk_lin2log		#
	movi	a3, -0x780	# tmp272,
	add.n	a2, a2, a3	# tmp274,, tmp272
# @OPUS@\upstream\silk\quant_LTP_gains.c:131:     *pred_gain_dB_Q7 = (opus_int)silk_SMULBB( -3, silk_lin2log( res_nrg_Q15 ) - ( 15 << 7 ) );
	slli	a2, a2, 16	# tmp276, tmp274,
	srai	a2, a2, 16	# tmp275, tmp276,
# @OPUS@\upstream\silk\quant_LTP_gains.c:131:     *pred_gain_dB_Q7 = (opus_int)silk_SMULBB( -3, silk_lin2log( res_nrg_Q15 ) - ( 15 << 7 ) );
	l32i	a8, sp, 108	# %sfp,
# @OPUS@\upstream\silk\quant_LTP_gains.c:131:     *pred_gain_dB_Q7 = (opus_int)silk_SMULBB( -3, silk_lin2log( res_nrg_Q15 ) - ( 15 << 7 ) );
	slli	a3, a2, 2	# tmp278, tmp275,
# @OPUS@\upstream\silk\quant_LTP_gains.c:132: }
	l32i	a0, sp, 156	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:131:     *pred_gain_dB_Q7 = (opus_int)silk_SMULBB( -3, silk_lin2log( res_nrg_Q15 ) - ( 15 << 7 ) );
	sub	a2, a2, a3	# tmp279, tmp275, tmp278
# @OPUS@\upstream\silk\quant_LTP_gains.c:132: }
	movi	a9, 0xa0	#,
	l32i	a12, sp, 152	#,
	l32i	a13, sp, 148	#,
	l32i	a14, sp, 144	#,
	l32i	a15, sp, 140	#,
# @OPUS@\upstream\silk\quant_LTP_gains.c:131:     *pred_gain_dB_Q7 = (opus_int)silk_SMULBB( -3, silk_lin2log( res_nrg_Q15 ) - ( 15 << 7 ) );
	s32i.n	a2, a8, 0	# *pred_gain_dB_Q7_114(D), tmp279
# @OPUS@\upstream\silk\quant_LTP_gains.c:132: }
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_quant_LTP_gains, .-silk_quant_LTP_gains
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
