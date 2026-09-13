# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler_private_IIR_FIR.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler_private_IIR_FIR.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_IIR_FIR.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_IIR_FIR.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_IIR_FIR.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_IIR_FIR.c.s.raw
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
	.section	.text.silk_resampler_private_IIR_FIR,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, silk_resampler_frac_FIR_12
	.align	4
	.global	silk_resampler_private_IIR_FIR
	.type	silk_resampler_private_IIR_FIR, @function
# Function: silk_resampler_private_IIR_FIR
# Module: upstream/silk/resampler_private_IIR_FIR.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return out;
# C context: }
# C context: /* Upsample using a combination of allpass-based 2x upsampling and FIR interpolation */
# C context: void silk_resampler_private_IIR_FIR(
# C context: void                            *SS,            /* I/O  Resampler state             */
# C context: opus_int16                      out[],          /* O    Output signal               */
# C context: const opus_int16                in[],           /* I    Input signal                */
# C context: opus_int32                      inLen           /* I    Number of input samples     */
silk_resampler_private_IIR_FIR:
	addi	sp, sp, -80	#,,
	s32i	a0, sp, 76	#,
	s32i	a12, sp, 72	#,
	s32i	a13, sp, 68	#,
	s32i	a14, sp, 64	#,
	mov.n	a13, a5	# inLen, inLen
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:93: {
	mov.n	a12, a4	# in, in
	mov.n	a15, a3	# out, out
	s32i.n	a2, sp, 20	# %sfp, SS
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:98:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:100:     ALLOC( buf, 2 * S->batchSize + RESAMPLER_ORDER_FIR_12, opus_int16 );
	l32i.n	a11, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:98:     SAVE_STACK;
	s32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:100:     ALLOC( buf, 2 * S->batchSize + RESAMPLER_ORDER_FIR_12, opus_int16 );
	l32i	a4, a11, 268	# MEM[(struct silk_resampler_state_struct *)SS_25(D)].batchSize, MEM[(struct silk_resampler_state_struct *)SS_25(D)].batchSize
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:98:     SAVE_STACK;
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:100:     ALLOC( buf, 2 * S->batchSize + RESAMPLER_ORDER_FIR_12, opus_int16 );
	addi.n	a2, a4, 4	# tmp125, MEM[(struct silk_resampler_state_struct *)SS_25(D)].batchSize,
	movi.n	a3, 2	#,
	movi.n	a4, 0	#,
	slli	a2, a2, 1	#, tmp125,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:103:     silk_memcpy( buf, S->sFIR.i16, RESAMPLER_ORDER_FIR_12 * sizeof( opus_int16 ) );
	l32i.n	a11, sp, 20	# %sfp,
	movi.n	a4, 0x10	#,
	addi	a11, a11, 24	#,,
	mov.n	a3, a11	#,
	s32i.n	a11, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:100:     ALLOC( buf, 2 * S->batchSize + RESAMPLER_ORDER_FIR_12, opus_int16 );
	s32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:103:     silk_memcpy( buf, S->sFIR.i16, RESAMPLER_ORDER_FIR_12 * sizeof( opus_int16 ) );
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:106:     index_increment_Q16 = S->invRatio_Q16;
	l32i.n	a11, sp, 20	# %sfp,
	mov.n	a14, a15	# out, out
	l32i	a11, a11, 272	# MEM[(struct silk_resampler_state_struct *)SS_25(D)].invRatio_Q16,
	mov.n	a15, a13	# inLen, inLen
	s32i.n	a11, sp, 24	# %sfp,
	l32i.n	a11, sp, 16	# %sfp,
	addi	a11, a11, 16	#,,
	s32i.n	a11, sp, 28	# %sfp,
.L7:
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:108:         nSamplesIn = silk_min( inLen, S->batchSize );
	l32i.n	a11, sp, 20	# %sfp,
	l32i	a13, a11, 268	# MEM[(struct silk_resampler_state_struct *)SS_25(D)].batchSize, nSamplesIn
	bge	a15, a13, .L2	# inLen, nSamplesIn,
	mov.n	a13, a15	# nSamplesIn, inLen
.L2:
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:111:         silk_resampler_private_up2_HQ( S->sIIR, &buf[ RESAMPLER_ORDER_FIR_12 ], in, nSamplesIn );
	l32i.n	a3, sp, 28	# %sfp,
	l32i.n	a2, sp, 20	# %sfp,
	mov.n	a5, a13	#, nSamplesIn
	mov.n	a4, a12	#, in
	call0	silk_resampler_private_up2_HQ		#
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:113:         max_index_Q16 = silk_LSHIFT32( nSamplesIn, 16 + 1 );         /* + 1 because 2x upsampling */
	slli	a8, a13, 17	# max_index_Q16, nSamplesIn,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:51:     for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	blti	a8, 1, .L3	# max_index_Q16,,
	mov.n	a9, a14	# ivtmp$18, out
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:51:     for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	movi.n	a7, 0	# index_Q16,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:59:         const opus_int16 *back = silk_resampler_frac_FIR_12[11 - table_index];
	movi.n	a6, 0xb	# tmp145,
.L5:
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:52:         table_index = silk_SMULWB( index_Q16 & 0xFFFF, 12 );
	extui	a3, a7, 0, 16	# tmp136, index_Q16,
	slli	a2, a3, 1	# tmp138, tmp136,
	add.n	a2, a2, a3	# tmp139, tmp138, tmp136
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:52:         table_index = silk_SMULWB( index_Q16 & 0xFFFF, 12 );
	srli	a2, a2, 14	# table_index, tmp139,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:59:         const opus_int16 *back = silk_resampler_frac_FIR_12[11 - table_index];
	sub	a4, a6, a2	# tmp146, tmp145, table_index
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:58:         const opus_int16 *front = silk_resampler_frac_FIR_12[table_index];
	l32r	a5, .LC2	#,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:53:         buf_ptr = &buf[ index_Q16 >> 16 ];
	srai	a3, a7, 16	# tmp141, index_Q16,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:53:         buf_ptr = &buf[ index_Q16 >> 16 ];
	l32i.n	a11, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:53:         buf_ptr = &buf[ index_Q16 >> 16 ];
	slli	a3, a3, 1	# tmp142, tmp141,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:58:         const opus_int16 *front = silk_resampler_frac_FIR_12[table_index];
	slli	a2, a2, 3	# tmp143, table_index,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:59:         const opus_int16 *back = silk_resampler_frac_FIR_12[11 - table_index];
	slli	a4, a4, 3	# tmp147, tmp146,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:53:         buf_ptr = &buf[ index_Q16 >> 16 ];
	add.n	a3, a11, a3	# buf_ptr,, tmp142
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:58:         const opus_int16 *front = silk_resampler_frac_FIR_12[table_index];
	add.n	a2, a5, a2	# front,, tmp143
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:59:         const opus_int16 *back = silk_resampler_frac_FIR_12[11 - table_index];
	add.n	a4, a5, a4	# back,, tmp147
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a5, a2, 0	# value, front
# 0 "" 2
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:61:         res_Q15 = silk_SMULBB(          buf_ptr[ 0 ], pair.half[0] );
#NO_APP
	l16ui	a11, a3, 0	# *buf_ptr_53,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:62:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 1 ], pair.half[1] );
	srai	a10, a5, 16	# tmp151, value,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:61:         res_Q15 = silk_SMULBB(          buf_ptr[ 0 ], pair.half[0] );
	mul16s	a5, a11, a5	# res_Q15, *buf_ptr_53, value
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:62:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 1 ], pair.half[1] );
	l16ui	a11, a3, 2	# MEM[(opus_int16 *)buf_ptr_53 + 2B],
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:63:         pair = yoradio_opus_fir_pair(front + 2);
	addi.n	a2, a2, 4	# tmp155, front,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:62:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 1 ], pair.half[1] );
	mul16s	a10, a11, a10	# tmp152,, tmp151
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:62:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 1 ], pair.half[1] );
	add.n	a10, a10, a5	# res_Q15, tmp152, res_Q15
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp155
# 0 "" 2
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:64:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 2 ], pair.half[0] );
#NO_APP
	l16ui	a11, a3, 4	# MEM[(opus_int16 *)buf_ptr_53 + 4B],
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:65:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 3 ], pair.half[1] );
	l16ui	a5, a3, 6	# MEM[(opus_int16 *)buf_ptr_53 + 6B],
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:64:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 2 ], pair.half[0] );
	mul16s	a11, a11, a2	# tmp156, MEM[(opus_int16 *)buf_ptr_53 + 4B], value
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:65:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 3 ], pair.half[1] );
	srai	a2, a2, 16	# tmp158, value,
	mul16s	a2, a5, a2	# tmp159, MEM[(opus_int16 *)buf_ptr_53 + 6B], tmp158
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:64:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 2 ], pair.half[0] );
	add.n	a11, a11, a10	# res_Q15, tmp156, res_Q15
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:65:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 3 ], pair.half[1] );
	add.n	a5, a2, a11	# res_Q15, tmp159, res_Q15
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:66:         pair = yoradio_opus_fir_pair(back + 2);
	addi.n	a10, a4, 4	# tmp162, back,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a10, a10, 0	# value, tmp162
# 0 "" 2
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:67:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 4 ], pair.half[1] );
#NO_APP
	l16ui	a11, a3, 8	# MEM[(opus_int16 *)buf_ptr_53 + 8B],
	srai	a2, a10, 16	# tmp163, value,
	mul16s	a11, a11, a2	# tmp164, MEM[(opus_int16 *)buf_ptr_53 + 8B], tmp163
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:68:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 5 ], pair.half[0] );
	l16ui	a2, a3, 10	# MEM[(opus_int16 *)buf_ptr_53 + 10B],
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:67:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 4 ], pair.half[1] );
	add.n	a5, a11, a5	# res_Q15, tmp164, res_Q15
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:68:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 5 ], pair.half[0] );
	mul16s	a10, a2, a10	# tmp166,, value
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:68:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 5 ], pair.half[0] );
	add.n	a5, a10, a5	# res_Q15, tmp166, res_Q15
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a4, a4, 0	# value, back
# 0 "" 2
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:70:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 6 ], pair.half[1] );
#NO_APP
	l16ui	a10, a3, 12	# MEM[(opus_int16 *)buf_ptr_53 + 12B],
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:71:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 7 ], pair.half[0] );
	l16ui	a2, a3, 14	# MEM[(opus_int16 *)buf_ptr_53 + 14B],
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:70:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 6 ], pair.half[1] );
	srai	a3, a4, 16	# tmp169, value,
	mul16s	a10, a10, a3	# tmp170, MEM[(opus_int16 *)buf_ptr_53 + 12B], tmp169
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:71:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 7 ], pair.half[0] );
	mul16s	a2, a2, a4	# tmp172, MEM[(opus_int16 *)buf_ptr_53 + 14B], value
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:70:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 6 ], pair.half[1] );
	add.n	a10, a10, a5	# res_Q15, tmp170, res_Q15
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:71:         res_Q15 = silk_SMLABB( res_Q15, buf_ptr[ 7 ], pair.half[0] );
	add.n	a2, a2, a10	# res_Q15, tmp172, res_Q15
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:82:         *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q15, 15 ) );
	srai	a2, a2, 14	# tmp175, res_Q15,
	addi.n	a2, a2, 1	# tmp176, tmp175,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:51:     for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	l32i.n	a11, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:82:         *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q15, 15 ) );
	l32r	a3, .LC0	#, iftmp$3_113
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:82:         *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q15, 15 ) );
	srai	a2, a2, 1	# _112, tmp176,
	addi.n	a14, a14, 2	# out, out,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:51:     for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	add.n	a7, a7, a11	# index_Q16, index_Q16,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:82:         *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q15, 15 ) );
	blt	a3, a2, .L4	# tmp4, _112,
	l32r	a3, .LC1	#, iftmp$3_113
	slli	a4, a2, 16	# tmp179, _112,
	blt	a2, a3, .L4	# _112, tmp5,
	srai	a3, a4, 16	# iftmp$3_113, tmp179,
.L4:
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:82:         *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q15, 15 ) );
	s16i	a3, a9, 0	# MEM[base: _149, offset: 0B], iftmp$3_113
	mov.n	a9, a14	# ivtmp$18, out
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:51:     for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	blt	a7, a8, .L5	# index_Q16, max_index_Q16,
.L3:
	l32i.n	a11, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:115:         in += nSamplesIn;
	slli	a2, a13, 1	# tmp180, nSamplesIn,
	slli	a3, a13, 2	# tmp182, nSamplesIn,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:116:         inLen -= nSamplesIn;
	sub	a15, a15, a13	# inLen, inLen, nSamplesIn
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:115:         in += nSamplesIn;
	add.n	a12, a12, a2	# in, in, tmp180
	add.n	a3, a11, a3	# _177,, tmp182
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:120:             silk_memcpy( buf, &buf[ nSamplesIn << 1 ], RESAMPLER_ORDER_FIR_12 * sizeof( opus_int16 ) );
	movi.n	a4, 0x10	#,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:118:         if( inLen > 0 ) {
	blti	a15, 1, .L6	# inLen,,
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:120:             silk_memcpy( buf, &buf[ nSamplesIn << 1 ], RESAMPLER_ORDER_FIR_12 * sizeof( opus_int16 ) );
	mov.n	a2, a11	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:108:         nSamplesIn = silk_min( inLen, S->batchSize );
	j	.L7		#
.L6:
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:127:     silk_memcpy( S->sFIR.i16, &buf[ nSamplesIn << 1 ], RESAMPLER_ORDER_FIR_12 * sizeof( opus_int16 ) );
	l32i.n	a2, sp, 32	# %sfp,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:128:     RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\resampler_private_IIR_FIR.c:129: }
	l32i	a0, sp, 76	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	silk_resampler_private_IIR_FIR, .-silk_resampler_private_IIR_FIR
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
