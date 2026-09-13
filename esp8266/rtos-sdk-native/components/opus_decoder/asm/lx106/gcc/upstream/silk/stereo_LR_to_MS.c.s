# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/stereo_LR_to_MS.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"stereo_LR_to_MS.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\stereo_LR_to_MS.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\stereo_LR_to_MS.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\stereo_LR_to_MS.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\stereo_LR_to_MS.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\stereo_LR_to_MS.c.s.raw
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
	.section	.text.silk_stereo_LR_to_MS,"ax",@progbits
	.literal_position
	.literal .LC0, 16384
	.literal .LC1, 1073741824
	.literal .LC2, 16777216
	.literal .LC3, 32767
	.literal .LC4, -32768
	.literal .LC5, 32768
	.literal .LC6, 65536
	.literal .LC7, 851968
	.literal .LC8, 536870911
	.literal .LC9, -2147483648
	.literal .LC10, 2147483647
	.literal .LC11, 15565
	.literal .LC12, 10000
	.align	4
	.global	silk_stereo_LR_to_MS
	.type	silk_stereo_LR_to_MS, @function
# Function: silk_stereo_LR_to_MS
# Module: upstream/silk/stereo_LR_to_MS.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "stack_alloc.h"
# C context:
# C context: /* Convert Left/Right stereo signal to adaptive Mid/Side representation */
# C context: void silk_stereo_LR_to_MS(
# C context: stereo_enc_state            *state,                         /* I/O  State                                       */
# C context: opus_int16                  x1[],                           /* I/O  Left input signal, becomes mid signal       */
# C context: opus_int16                  x2[],                           /* I/O  Right input signal, becomes side signal     */
# C context: opus_int8                   ix[ 2 ][ 3 ],                   /* O    Quantization indices                        */
silk_stereo_LR_to_MS:
	movi	a9, 0xa0	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:61:     ALLOC( side, frame_length + 2, opus_int16 );
	l32i	a8, sp, 176	# frame_length,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:49: {
	s32i	a0, sp, 156	#,
	s32i	a12, sp, 152	#,
	s32i	a4, sp, 64	# %sfp, x2
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:61:     ALLOC( side, frame_length + 2, opus_int16 );
	addi.n	a12, a8, 2	# _1,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:49: {
	s32i	a5, sp, 100	# %sfp, ix
	s32i	a6, sp, 72	# %sfp, mid_only_flag
	s32i.n	a7, sp, 52	# %sfp, mid_side_rates_bps
	s32i	a13, sp, 148	#,
	s32i	a14, sp, 144	#,
	s32i	a15, sp, 140	#,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:49: {
	s32i.n	a3, sp, 56	# %sfp, x1
	s32i.n	a2, sp, 36	# %sfp, state
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:59:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:61:     ALLOC( side, frame_length + 2, opus_int16 );
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, _1
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:58:     opus_int16 *mid = &x1[ -2 ];
	l32i.n	a11, sp, 56	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:61:     ALLOC( side, frame_length + 2, opus_int16 );
	s32i.n	a2, sp, 44	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:58:     opus_int16 *mid = &x1[ -2 ];
	addi	a11, a11, -4	#,,
	s32i	a11, sp, 68	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:63:     for( n = 0; n < frame_length + 2; n++ ) {
	bgei	a12, 1, .L2	# _1,,
	l32i	a12, sp, 176	# frame_length,
	slli	a12, a12, 1	#,,
	s32i	a12, sp, 92	# %sfp,
.L7:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:71:     silk_memcpy( mid,  state->sMid,  2 * sizeof( opus_int16 ) );
	l32i.n	a8, sp, 36	# %sfp,
	l32i	a11, sp, 68	# %sfp,
	l8ui	a4, a8, 4	# MEM[(void *)_26],
	l8ui	a2, a8, 5	# MEM[(void *)_26],
	s8i	a4, a11, 0	# MEM[(void *)mid_377], MEM[(void *)_26]
	l8ui	a4, a8, 6	# MEM[(void *)_26],
	s8i	a2, a11, 1	# MEM[(void *)mid_377], MEM[(void *)_26]
	l8ui	a2, a8, 7	# MEM[(void *)_26],
	s8i	a4, a11, 2	# MEM[(void *)mid_377], MEM[(void *)_26]
	s8i	a2, a11, 3	# MEM[(void *)mid_377], MEM[(void *)_26]
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:72:     silk_memcpy( side, state->sSide, 2 * sizeof( opus_int16 ) );
	l8ui	a5, a8, 8	# MEM[(void *)_27],
	l32i.n	a12, sp, 44	# %sfp,
	l8ui	a4, a8, 9	# MEM[(void *)_27],
	s8i	a5, a12, 0	# MEM[(void *)side_382], MEM[(void *)_27]
	l8ui	a6, a8, 10	# MEM[(void *)_27],
	s8i	a4, a12, 1	# MEM[(void *)side_382], MEM[(void *)_27]
	l8ui	a5, a8, 11	# MEM[(void *)_27],
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:71:     silk_memcpy( mid,  state->sMid,  2 * sizeof( opus_int16 ) );
	addi.n	a3, a8, 4	# _26,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:72:     silk_memcpy( side, state->sSide, 2 * sizeof( opus_int16 ) );
	addi.n	a2, a8, 8	# _27,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:73:     silk_memcpy( state->sMid,  &mid[  frame_length ], 2 * sizeof( opus_int16 ) );
	l32i	a8, sp, 92	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:72:     silk_memcpy( side, state->sSide, 2 * sizeof( opus_int16 ) );
	s8i	a6, a12, 2	# MEM[(void *)side_382], MEM[(void *)_27]
	s8i	a5, a12, 3	# MEM[(void *)side_382], MEM[(void *)_27]
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:73:     silk_memcpy( state->sMid,  &mid[  frame_length ], 2 * sizeof( opus_int16 ) );
	add.n	a4, a11, a8	# tmp524,,
	l8ui	a6, a4, 0	# MEM[(void *)_30],
	l32i.n	a11, sp, 36	# %sfp,
	l8ui	a5, a4, 1	# MEM[(void *)_30],
	s8i	a6, a11, 4	# MEM[(void *)_26], MEM[(void *)_30]
	l8ui	a6, a4, 2	# MEM[(void *)_30],
	s8i	a5, a3, 1	# MEM[(void *)_26], MEM[(void *)_30]
	l8ui	a4, a4, 3	# MEM[(void *)_30],
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:74:     silk_memcpy( state->sSide, &side[ frame_length ], 2 * sizeof( opus_int16 ) );
	add.n	a14, a12, a8	# _345,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:73:     silk_memcpy( state->sMid,  &mid[  frame_length ], 2 * sizeof( opus_int16 ) );
	s8i	a6, a3, 2	# MEM[(void *)_26], MEM[(void *)_30]
	s8i	a4, a3, 3	# MEM[(void *)_26], MEM[(void *)_30]
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:74:     silk_memcpy( state->sSide, &side[ frame_length ], 2 * sizeof( opus_int16 ) );
	l8ui	a4, a14, 0	# MEM[(void *)_31],
	l8ui	a3, a14, 1	# MEM[(void *)_31],
	s8i	a4, a11, 8	# MEM[(void *)_27], MEM[(void *)_31]
	l8ui	a7, a14, 2	# MEM[(void *)_31],
	s8i	a3, a2, 1	# MEM[(void *)_27], MEM[(void *)_31]
	l8ui	a6, a14, 3	# MEM[(void *)_31],
	s8i	a7, a2, 2	# MEM[(void *)_27], MEM[(void *)_31]
	s8i	a6, a2, 3	# MEM[(void *)_27], MEM[(void *)_31]
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:77:     ALLOC( LP_mid, frame_length, opus_int16 );
	l32i	a2, sp, 176	# frame_length,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a12, a2	# LP_mid,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:78:     ALLOC( HP_mid, frame_length, opus_int16 );
	l32i	a2, sp, 176	# frame_length,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:79:     for( n = 0; n < frame_length; n++ ) {
	l32i	a8, sp, 176	# frame_length,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:78:     ALLOC( HP_mid, frame_length, opus_int16 );
	mov.n	a13, a2	# HP_mid,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:79:     for( n = 0; n < frame_length; n++ ) {
	bgei	a8, 1, .L3	#,,
	j	.L79		#
.L2:
	l32i	a12, sp, 64	# %sfp,
	mov.n	a3, a11	# ivtmp$109,
	l32i	a11, sp, 176	# frame_length,
	addi	a6, a12, -4	# ivtmp$111,,
	l32i.n	a12, sp, 56	# %sfp,
	slli	a11, a11, 1	#,,
	l32r	a9, .LC5	#, tmp951
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:67:         side[ n ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( diff, 1 ) );
	l32r	a10, .LC3	#, tmp1053
	mov.n	a5, a2	# ivtmp$113,
	s32i	a11, sp, 92	# %sfp,
	add.n	a8, a12, a11	# _257,,
.L8:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:64:         sum  = x1[ n - 2 ] + (opus_int32)x2[ n - 2 ];
	l16si	a7, a6, 0	# MEM[base: _252, offset: 0B], _1486
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:64:         sum  = x1[ n - 2 ] + (opus_int32)x2[ n - 2 ];
	l16si	a2, a3, 0	# MEM[base: _250, offset: 0B], _1489
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:66:         mid[  n ] = (opus_int16)silk_RSHIFT_ROUND( sum, 1 );
	add.n	a4, a7, a2	# tmp539, _1486, _1489
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:65:         diff = x1[ n - 2 ] - (opus_int32)x2[ n - 2 ];
	sub	a2, a2, a7	# diff, _1489, _1486
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:66:         mid[  n ] = (opus_int16)silk_RSHIFT_ROUND( sum, 1 );
	extui	a7, a4, 0, 1	# tmp541, tmp539,
	srai	a4, a4, 1	# tmp543, tmp539,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:66:         mid[  n ] = (opus_int16)silk_RSHIFT_ROUND( sum, 1 );
	add.n	a4, a7, a4	# tmp546, tmp541, tmp543
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:67:         side[ n ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( diff, 1 ) );
	srai	a7, a2, 1	# _1472, diff,
	extui	a2, a2, 0, 1	# tmp956, diff,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:66:         mid[  n ] = (opus_int16)silk_RSHIFT_ROUND( sum, 1 );
	s16i	a4, a3, 0	# MEM[base: _250, offset: 0B], tmp546
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:67:         side[ n ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( diff, 1 ) );
	add.n	a2, a2, a7	# tmp548, tmp956, _1472
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:67:         side[ n ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( diff, 1 ) );
	beq	a2, a9, .L5	# tmp548, tmp951,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:67:         side[ n ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( diff, 1 ) );
	s16i	a2, a5, 0	# MEM[base: _678, offset: 0B], tmp548
	addi.n	a3, a3, 2	# ivtmp$109, ivtmp$109,
	addi.n	a6, a6, 2	# ivtmp$111, ivtmp$111,
	addi.n	a5, a5, 2	# ivtmp$113, ivtmp$113,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:63:     for( n = 0; n < frame_length + 2; n++ ) {
	bne	a8, a3, .L8	# _257, ivtmp$109,
	j	.L7		#
.L5:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:67:         side[ n ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( diff, 1 ) );
	s16i	a10, a5, 0	# MEM[base: _253, offset: 0B], tmp1053
	addi.n	a3, a3, 2	# ivtmp$109, ivtmp$109,
	addi.n	a6, a6, 2	# ivtmp$111, ivtmp$111,
	addi.n	a5, a5, 2	# ivtmp$113, ivtmp$113,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:63:     for( n = 0; n < frame_length + 2; n++ ) {
	bne	a3, a8, .L8	# ivtmp$109, _257,
	j	.L7		#
.L3:
	l32i	a8, sp, 92	# %sfp,
	l32i.n	a11, sp, 56	# %sfp,
	addi	a9, a8, -4	# tmp557,,
	l32i	a3, sp, 68	# %sfp, ivtmp$105
	mov.n	a7, a12	# ivtmp$103, LP_mid
	mov.n	a6, a2	# ivtmp$104, HP_mid
	add.n	a9, a11, a9	# _649,, tmp557
.L9:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:80:         sum = silk_RSHIFT_ROUND( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 2 );
	l16si	a2, a3, 0	# MEM[base: _658, offset: 0B], tmp558
	l16si	a5, a3, 4	# MEM[base: _658, offset: 4B], tmp561
	l16si	a4, a3, 2	# MEM[base: _658, offset: 2B], tmp565
	add.n	a2, a2, a5	# tmp564, tmp558, tmp561
	slli	a4, a4, 1	# tmp568, tmp565,
	add.n	a2, a2, a4	# tmp569, tmp564, tmp568
	srai	a2, a2, 1	# tmp570, tmp569,
	addi.n	a2, a2, 1	# tmp571, tmp570,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:81:         LP_mid[ n ] = sum;
	slli	a2, a2, 15	# tmp573, tmp571,
	srai	a2, a2, 16	# _54, tmp573,
	s16i	a2, a7, 0	# MEM[base: _349, offset: 0B], _54
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:82:         HP_mid[ n ] = mid[ n + 1 ] - sum;
	l16ui	a4, a3, 2	# MEM[base: _658, offset: 2B],
	addi.n	a3, a3, 2	# ivtmp$105, ivtmp$105,
	sub	a2, a4, a2	# tmp575, MEM[base: _658, offset: 2B], _54
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:82:         HP_mid[ n ] = mid[ n + 1 ] - sum;
	s16i	a2, a6, 0	# MEM[base: _485, offset: 0B], tmp575
	addi.n	a7, a7, 2	# ivtmp$103, ivtmp$103,
	addi.n	a6, a6, 2	# ivtmp$104, ivtmp$104,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:79:     for( n = 0; n < frame_length; n++ ) {
	bne	a9, a3, .L9	# _649, ivtmp$105,
	j	.L80		#
.L11:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:89:         sum = silk_RSHIFT_ROUND( silk_ADD_LSHIFT32( side[ n ] + (opus_int32)side[ n + 2 ], side[ n + 1 ], 1 ), 2 );
	l16si	a2, a3, 0	# MEM[base: _340, offset: 0B], tmp576
	l16si	a5, a3, 4	# MEM[base: _340, offset: 4B], tmp579
	l16si	a4, a3, 2	# MEM[base: _340, offset: 2B], tmp583
	add.n	a2, a2, a5	# tmp582, tmp576, tmp579
	slli	a4, a4, 1	# tmp586, tmp583,
	add.n	a2, a2, a4	# tmp587, tmp582, tmp586
	srai	a2, a2, 1	# tmp588, tmp587,
	addi.n	a2, a2, 1	# tmp589, tmp588,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:90:         LP_side[ n ] = sum;
	slli	a2, a2, 15	# tmp591, tmp589,
	srai	a2, a2, 16	# _80, tmp591,
	s16i	a2, a7, 0	# MEM[base: _407, offset: 0B], _80
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:91:         HP_side[ n ] = side[ n + 1 ] - sum;
	l16ui	a4, a3, 2	# MEM[base: _340, offset: 2B],
	addi.n	a3, a3, 2	# ivtmp$96, ivtmp$96,
	sub	a2, a4, a2	# tmp593, MEM[base: _340, offset: 2B], _80
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:91:         HP_side[ n ] = side[ n + 1 ] - sum;
	s16i	a2, a6, 0	# MEM[base: _406, offset: 0B], tmp593
	addi.n	a7, a7, 2	# ivtmp$97, ivtmp$97,
	addi.n	a6, a6, 2	# ivtmp$98, ivtmp$98,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:88:     for( n = 0; n < frame_length; n++ ) {
	bne	a3, a14, .L11	# ivtmp$96, _345,
.L59:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:95:     is10msFrame = frame_length == 10 * fs_kHz;
	l32i	a8, sp, 172	# fs_kHz,
	l32i	a11, sp, 172	# fs_kHz,
	slli	a8, a8, 2	#,,
	s32i	a8, sp, 96	# %sfp,
	add.n	a8, a8, a11	# tmp596,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:99:     smooth_coef_Q16 = silk_SMULWB( silk_SMULBB( prev_speech_act_Q8, prev_speech_act_Q8 ), smooth_coef_Q16 );
	l32i	a5, sp, 164	# prev_speech_act_Q8,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:95:     is10msFrame = frame_length == 10 * fs_kHz;
	slli	a14, a8, 1	# tmp597, tmp596,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:97:         SILK_FIX_CONST( STEREO_RATIO_SMOOTH_COEF / 2, 16 ) :
	l32i	a8, sp, 176	# frame_length,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:99:     smooth_coef_Q16 = silk_SMULWB( silk_SMULBB( prev_speech_act_Q8, prev_speech_act_Q8 ), smooth_coef_Q16 );
	mul16s	a2, a5, a5	# _87,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:97:         SILK_FIX_CONST( STEREO_RATIO_SMOOTH_COEF / 2, 16 ) :
	sub	a4, a14, a8	# tmp965, tmp597,
	movi	a5, 0x148	# tmp963,
	movi	a3, 0x28f	# tmp964,
	moveqz	a3, a5, a4	# tmp964, tmp963, tmp965
	mov.n	a4, a3	# iftmp$26_363, tmp964
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:99:     smooth_coef_Q16 = silk_SMULWB( silk_SMULBB( prev_speech_act_Q8, prev_speech_act_Q8 ), smooth_coef_Q16 );
	extui	a3, a2, 0, 16	# tmp599, _87,
	mull	a3, a3, a4	# tmp600, tmp599, iftmp$26_363
	srai	a2, a2, 16	# tmp602, _87,
	mull	a2, a2, a4	# tmp603, tmp602, iftmp$26_363
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:101:     pred_Q13[ 0 ] = silk_stereo_find_predictor( &LP_ratio_Q14, LP_mid, LP_side, &state->mid_side_amp_Q0[ 0 ], frame_length, smooth_coef_Q16 );
	l32i.n	a11, sp, 36	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:99:     smooth_coef_Q16 = silk_SMULWB( silk_SMULBB( prev_speech_act_Q8, prev_speech_act_Q8 ), smooth_coef_Q16 );
	srai	a3, a3, 16	# tmp601, tmp600,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:99:     smooth_coef_Q16 = silk_SMULWB( silk_SMULBB( prev_speech_act_Q8, prev_speech_act_Q8 ), smooth_coef_Q16 );
	add.n	a2, a3, a2	#, tmp601, tmp603
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:101:     pred_Q13[ 0 ] = silk_stereo_find_predictor( &LP_ratio_Q14, LP_mid, LP_side, &state->mid_side_amp_Q0[ 0 ], frame_length, smooth_coef_Q16 );
	mov.n	a7, a2	#,
	mov.n	a6, a8	#,
	addi.n	a5, a11, 12	#,,
	mov.n	a3, a12	#, LP_mid
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:99:     smooth_coef_Q16 = silk_SMULWB( silk_SMULBB( prev_speech_act_Q8, prev_speech_act_Q8 ), smooth_coef_Q16 );
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:101:     pred_Q13[ 0 ] = silk_stereo_find_predictor( &LP_ratio_Q14, LP_mid, LP_side, &state->mid_side_amp_Q0[ 0 ], frame_length, smooth_coef_Q16 );
	mov.n	a4, a15	#, LP_side
	addi	a2, sp, 20	#,,
	s32i	a9, sp, 124	#,
	call0	silk_stereo_find_predictor		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:102:     pred_Q13[ 1 ] = silk_stereo_find_predictor( &HP_ratio_Q14, HP_mid, HP_side, &state->mid_side_amp_Q0[ 2 ], frame_length, smooth_coef_Q16 );
	l32i	a9, sp, 124	#,
	l32i.n	a12, sp, 36	# %sfp,
	l32i.n	a7, sp, 60	# %sfp,
	l32i	a6, sp, 176	# frame_length,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:101:     pred_Q13[ 0 ] = silk_stereo_find_predictor( &LP_ratio_Q14, LP_mid, LP_side, &state->mid_side_amp_Q0[ 0 ], frame_length, smooth_coef_Q16 );
	s32i.n	a2, sp, 8	# pred_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:102:     pred_Q13[ 1 ] = silk_stereo_find_predictor( &HP_ratio_Q14, HP_mid, HP_side, &state->mid_side_amp_Q0[ 2 ], frame_length, smooth_coef_Q16 );
	mov.n	a4, a9	#, HP_side
	mov.n	a3, a13	#, HP_mid
	addi	a5, a12, 20	#,,
	addi	a2, sp, 16	#,,
	call0	silk_stereo_find_predictor		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:104:     frac_Q16 = silk_SMLABB( HP_ratio_Q14, LP_ratio_Q14, 3 );
	l16si	a3, sp, 20	# LP_ratio_Q14, tmp609
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:102:     pred_Q13[ 1 ] = silk_stereo_find_predictor( &HP_ratio_Q14, HP_mid, HP_side, &state->mid_side_amp_Q0[ 2 ], frame_length, smooth_coef_Q16 );
	s32i	a2, sp, 88	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:104:     frac_Q16 = silk_SMLABB( HP_ratio_Q14, LP_ratio_Q14, 3 );
	slli	a2, a3, 1	# tmp612, tmp609,
	add.n	a2, a2, a3	# tmp613, tmp612, tmp609
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:102:     pred_Q13[ 1 ] = silk_stereo_find_predictor( &HP_ratio_Q14, HP_mid, HP_side, &state->mid_side_amp_Q0[ 2 ], frame_length, smooth_coef_Q16 );
	l32i	a6, sp, 88	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:104:     frac_Q16 = silk_SMLABB( HP_ratio_Q14, LP_ratio_Q14, 3 );
	l32i.n	a3, sp, 16	# HP_ratio_Q14, HP_ratio_Q14
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:105:     frac_Q16 = silk_min( frac_Q16, SILK_FIX_CONST( 1, 16 ) );
	l32r	a7, .LC6	#,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:102:     pred_Q13[ 1 ] = silk_stereo_find_predictor( &HP_ratio_Q14, HP_mid, HP_side, &state->mid_side_amp_Q0[ 2 ], frame_length, smooth_coef_Q16 );
	s32i.n	a6, sp, 12	# pred_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:104:     frac_Q16 = silk_SMLABB( HP_ratio_Q14, LP_ratio_Q14, 3 );
	add.n	a9, a2, a3	# frac_Q16, tmp613, HP_ratio_Q14
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:105:     frac_Q16 = silk_min( frac_Q16, SILK_FIX_CONST( 1, 16 ) );
	bge	a7, a9, .L13	#, frac_Q16,
	mov.n	a9, a7	# frac_Q16,
.L13:
	l32i	a8, sp, 172	# fs_kHz,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:108:     total_rate_bps -= is10msFrame ? 1200 : 600;      /* Subtract approximate bitrate for coding stereo parameters */
	movi	a4, 0x4b0	# tmp972,
	slli	a2, a8, 16	# tmp620,,
	srai	a2, a2, 16	#, tmp620,
	slli	a11, a2, 2	# tmp626,,
	s32i	a2, sp, 80	# %sfp,
	add.n	a2, a11, a2	# tmp627, tmp626,
	l32i	a11, sp, 176	# frame_length,
	movi	a3, 0x258	# tmp973,
	sub	a8, a14, a11	# tmp974, tmp597,
	slli	a11, a2, 4	# tmp628, tmp627,
	sub	a11, a11, a2	# tmp629, tmp628, tmp627
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:108:     total_rate_bps -= is10msFrame ? 1200 : 600;      /* Subtract approximate bitrate for coding stereo parameters */
	l32i	a2, sp, 160	# total_rate_bps, total_rate_bps
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:108:     total_rate_bps -= is10msFrame ? 1200 : 600;      /* Subtract approximate bitrate for coding stereo parameters */
	moveqz	a3, a4, a8	# tmp973, tmp972, tmp974
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:108:     total_rate_bps -= is10msFrame ? 1200 : 600;      /* Subtract approximate bitrate for coding stereo parameters */
	sub	a2, a2, a3	#, total_rate_bps, iftmp$29_364
	s32i.n	a2, sp, 40	# %sfp,
	slli	a10, a9, 1	# tmp622, frac_Q16,
	l32r	a6, .LC7	#, tmp624
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:109:     if( total_rate_bps < 1 ) {
	l32i.n	a12, sp, 40	# %sfp,
	add.n	a10, a10, a9	# _1424, tmp622, frac_Q16
	slli	a11, a11, 3	# tmp630, tmp629,
	movi	a2, 0x7d0	# tmp631,
	add.n	a6, a10, a6	# _1425, _1424, tmp624
	add.n	a11, a11, a2	# _1426, tmp630, tmp631
	blti	a12, 1, .L62	#,,
	nsau	a7, a12	#,
	addi.n	a15, a7, -1	# tmp632,,
	ssl	a15	# tmp632
	sll	a15, a12	# _1433,
	s32i	a7, sp, 76	# %sfp,
	srai	a14, a15, 16	# _1437, _1433,
	extui	a12, a15, 0, 16	# _1439, _1433,
	addi.n	a13, a7, 10	# _1441,,
	j	.L15		#
.L62:
	movi.n	a8, 0x1f	#,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:110:         total_rate_bps = 1;
	movi.n	a7, 1	#,
	l32r	a14, .LC0	#, _1437
	l32r	a15, .LC1	#, _1433
	movi.n	a13, 0x29	# _1441,
	movi.n	a12, 0	# _1439,
	s32i	a8, sp, 76	# %sfp,
	s32i.n	a7, sp, 40	# %sfp,
.L15:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a6, .L63	# _1425,
# @OPUS@\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a8, a6	# tmp633, _1425
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a8, a8	# iftmp$58_505, tmp633
	addi.n	a2, a8, -1	# _1475, iftmp$58_505,
	j	.L16		#
.L63:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# _1475,
	movi.n	a8, 0x20	# iftmp$58_505,
.L16:
# @OPUS@\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a2	# _1475
	sll	a6, a6	# b32_nrm, _1425
# @OPUS@\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC8	#,
	srai	a3, a6, 16	#, b32_nrm,
	s32i	a8, sp, 104	#,
	s32i	a9, sp, 124	#,
	s32i	a10, sp, 112	#,
	s32i	a11, sp, 120	#,
	s32i	a6, sp, 108	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp639,,
	srai	a7, a2, 16	# _515, tmp639,
	mull	a12, a7, a12	# tmp640, _515, _1439
	mull	a14, a7, a14	# tmp642, _515, _1437
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a6, sp, 108	#,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a12, a12, 16	# tmp641, tmp640,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a14, a12, a14	# result, tmp641, tmp642
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a14	#, result
	srai	a5, a14, 31	#, result,
	mov.n	a2, a6	#, b32_nrm
	srai	a3, a6, 31	#, b32_nrm,
	s32i	a7, sp, 116	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp649,,
	sub	a15, a15, a3	# a32_nrm, _1433, tmp649
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a7, sp, 116	#,
	srai	a2, a15, 16	# tmp650, a32_nrm,
	extui	a15, a15, 0, 16	# tmp652, a32_nrm,
	mull	a2, a2, a7	# tmp651, tmp650, _515
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a8, sp, 104	#,
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	mull	a7, a15, a7	# tmp653, tmp652, _515
	add.n	a14, a2, a14	# _702, tmp651, result
	srai	a7, a7, 16	# tmp654, tmp653,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a13, a13, a8	# lshift, _1441, iftmp$58_505
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a7, a14	# result, tmp654, _702
# @OPUS@\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a9, sp, 124	#,
	l32i	a10, sp, 112	#,
	l32i	a11, sp, 120	#,
	bgez	a13, .L17	# lshift,
# @OPUS@\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	l32i	a12, sp, 76	# %sfp,
	l32r	a3, .LC9	#, tmp657
	sub	a8, a8, a12	# tmp656, iftmp$58_505,
	l32r	a4, .LC10	#, tmp658
	addi	a8, a8, -10	# _541, tmp656,
	ssr	a8	# _541
	sra	a3, a3	# _542, tmp657
	ssr	a8	# _541
	sra	a4, a4	# _543, tmp658
	bge	a4, a3, .L18	# _543, _542,
	bge	a3, a7, .L19	# _542, result,
	j	.L83		#
.L19:
	bge	a7, a4, .L20	# iftmp$56_544, _543,
	j	.L84		#
.L18:
	bge	a4, a7, .L22	# _543, result,
.L84:
	mov.n	a7, a4	# iftmp$56_544, _543
	j	.L20		#
.L22:
	bge	a7, a3, .L20	# iftmp$56_544, _542,
.L83:
	mov.n	a7, a3	# iftmp$56_544, _542
.L20:
	ssl	a8	# _541
	sll	a2, a7	# _553, iftmp$56_544
	j	.L24		#
.L17:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a3, 0x1f	# tmp659,
# @OPUS@\upstream\silk\Inlines.h:137:             return 0;
	movi.n	a2, 0	# _553,
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	blt	a3, a13, .L24	# tmp659, lshift,
# @OPUS@\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a13	# lshift
	sra	a2, a7	# _553, result
.L24:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:116:     mid_side_rates_bps[ 0 ] = silk_DIV32_varQ( total_rate_bps, SILK_FIX_CONST( 8 + 5, 16 ) + frac_3_Q16, 16+3 );
	l32i.n	a8, sp, 52	# %sfp,
	s32i.n	a2, a8, 0	# *mid_side_rates_bps_426(D), _553
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:118:     if( mid_side_rates_bps[ 0 ] < min_mid_rate_bps ) {
	bge	a2, a11, .L25	# _553, _1426,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:123:             silk_SMULWB( SILK_FIX_CONST( 1, 16 ) + frac_3_Q16, min_mid_rate_bps ), 14+2 );
	l32r	a12, .LC6	#,
	slli	a3, a11, 16	# tmp661, _1426,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:120:         mid_side_rates_bps[ 1 ] = total_rate_bps - mid_side_rates_bps[ 0 ];
	l32i.n	a6, sp, 40	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:123:             silk_SMULWB( SILK_FIX_CONST( 1, 16 ) + frac_3_Q16, min_mid_rate_bps ), 14+2 );
	add.n	a2, a10, a12	# tmp662, _1424,
	srai	a3, a3, 16	# _117, tmp661,
	extui	a10, a10, 0, 16	# tmp666, _1424,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:120:         mid_side_rates_bps[ 1 ] = total_rate_bps - mid_side_rates_bps[ 0 ];
	sub	a4, a6, a11	# _109,, _1426
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:123:             silk_SMULWB( SILK_FIX_CONST( 1, 16 ) + frac_3_Q16, min_mid_rate_bps ), 14+2 );
	srai	a2, a2, 16	# tmp664, tmp662,
	mull	a10, a10, a3	# tmp667, tmp666, _117
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:122:         width_Q14 = silk_DIV32_varQ( silk_LSHIFT( mid_side_rates_bps[ 1 ], 1 ) - min_mid_rate_bps,
	slli	a12, a4, 1	# tmp660, _109,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:123:             silk_SMULWB( SILK_FIX_CONST( 1, 16 ) + frac_3_Q16, min_mid_rate_bps ), 14+2 );
	mull	a2, a2, a3	# tmp665, tmp664, _117
	srai	a13, a10, 16	# tmp668, tmp667,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:119:         mid_side_rates_bps[ 0 ] = min_mid_rate_bps;
	s32i.n	a11, a8, 0	# *mid_side_rates_bps_426(D), _1426
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:120:         mid_side_rates_bps[ 1 ] = total_rate_bps - mid_side_rates_bps[ 0 ];
	s32i.n	a4, a8, 4	# MEM[(opus_int32 *)mid_side_rates_bps_426(D) + 4B], _109
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:122:         width_Q14 = silk_DIV32_varQ( silk_LSHIFT( mid_side_rates_bps[ 1 ], 1 ) - min_mid_rate_bps,
	sub	a12, a12, a11	# _113, tmp660, _1426
	add.n	a13, a2, a13	# _122, tmp665, tmp668
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a12, .L65	# _113,
# @OPUS@\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	abs	a7, a12	# tmp669, _113
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a7, a7	# iftmp$58_557, tmp669
	addi.n	a8, a7, 13	#, iftmp$58_557,
	addi.n	a2, a7, -1	# _1610, iftmp$58_557,
	s32i	a8, sp, 76	# %sfp,
	j	.L26		#
.L65:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a6, 0x2d	#,
	s32i	a6, sp, 76	# %sfp,
	movi.n	a2, 0x1f	# _1610,
	movi.n	a7, 0x20	# iftmp$58_557,
.L26:
# @OPUS@\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a2	# _1610
	sll	a12, a12	# _561, _113
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a13, .L66	# _122,
# @OPUS@\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a6, a13	# tmp670, _122
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a6, a6	# iftmp$58_565, tmp670
	addi.n	a2, a6, -1	# _1650, iftmp$58_565,
	j	.L27		#
.L66:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# _1650,
	movi.n	a6, 0x20	# iftmp$58_565,
.L27:
# @OPUS@\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a2	# _1650
	sll	a13, a13	# b32_nrm, _122
# @OPUS@\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC8	#,
	srai	a3, a13, 16	#, b32_nrm,
	s32i	a6, sp, 108	#,
	s32i	a7, sp, 116	#,
	s32i	a9, sp, 124	#,
	s32i	a11, sp, 120	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp676,,
	srai	a15, a2, 16	# _575, tmp676,
	extui	a14, a12, 0, 16	# tmp677, _561,
	mull	a14, a14, a15	# tmp678, tmp677, _575
	srai	a2, a12, 16	# tmp680, _561,
	mull	a2, a2, a15	# tmp681, tmp680, _575
	srai	a14, a14, 16	# tmp679, tmp678,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a14, a14, a2	# result, tmp679, tmp681
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a14	#, result
	srai	a5, a14, 31	#, result,
	mov.n	a2, a13	#, b32_nrm
	srai	a3, a13, 31	#, b32_nrm,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp688,,
	sub	a12, a12, a3	# a32_nrm, _561, tmp688
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a2, a12, 16	# tmp689, a32_nrm,
	extui	a12, a12, 0, 16	# tmp691, a32_nrm,
	mull	a2, a2, a15	# tmp690, tmp689, _575
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a6, sp, 108	#,
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	mull	a15, a12, a15	# tmp692, tmp691, _575
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a8, sp, 76	# %sfp,
	add.n	a14, a2, a14	# _696, tmp690, result
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a15, a15, 16	# tmp693, tmp692,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a3, a8, a6	# lshift,, iftmp$58_565
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a15, a15, a14	# result, tmp693, _696
# @OPUS@\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a7, sp, 116	#,
	l32i	a9, sp, 124	#,
	l32i	a11, sp, 120	#,
	bgez	a3, .L28	# lshift,
# @OPUS@\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a2, a6, a7	# tmp695, iftmp$58_565, iftmp$58_557
	l32r	a4, .LC9	#, tmp696
	l32r	a5, .LC10	#, tmp697
	addi	a2, a2, -13	# _601, tmp695,
	ssr	a2	# _601
	sra	a4, a4	# _602, tmp696
	ssr	a2	# _601
	sra	a5, a5	# _603, tmp697
	bge	a5, a4, .L29	# _603, _602,
	bge	a4, a15, .L30	# _602, result,
	j	.L85		#
.L30:
	bge	a15, a5, .L31	# iftmp$56_604, _603,
	j	.L86		#
.L29:
	bge	a5, a15, .L33	# _603, result,
.L86:
	mov.n	a15, a5	# iftmp$56_604, _603
	j	.L31		#
.L33:
	bge	a15, a4, .L31	# iftmp$56_604, _602,
.L85:
	mov.n	a15, a4	# iftmp$56_604, _602
.L31:
	ssl	a2	# _601
	sll	a15, a15	# _613, iftmp$56_604
	j	.L35		#
.L28:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a4, 0x1f	# tmp698,
	movi.n	a2, 0	# width_Q14,
	blt	a4, a3, .L37	# tmp698, lshift,
# @OPUS@\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a3	# lshift
	sra	a15, a15	# _613, result
.L35:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:124:         width_Q14 = silk_LIMIT( width_Q14, 0, SILK_FIX_CONST( 1, 14 ) );
	l32r	a2, .LC0	#, width_Q14
	blt	a2, a15, .L37	# width_Q14, _613,
	movi.n	a2, 0	# tmp700,
	movgez	a2, a15, a15	# width_Q14, _613, _613
	j	.L37		#
.L25:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:126:         mid_side_rates_bps[ 1 ] = total_rate_bps - mid_side_rates_bps[ 0 ];
	l32i.n	a12, sp, 40	# %sfp,
	sub	a7, a12, a2	# tmp701,, _553
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:127:         width_Q14 = SILK_FIX_CONST( 1, 14 );
	l32r	a2, .LC0	#, width_Q14
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:126:         mid_side_rates_bps[ 1 ] = total_rate_bps - mid_side_rates_bps[ 0 ];
	s32i.n	a7, a8, 4	# MEM[(opus_int32 *)mid_side_rates_bps_426(D) + 4B], tmp701
.L37:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:131:     state->smth_width_Q14 = (opus_int16)silk_SMLAWB( state->smth_width_Q14, width_Q14 - state->smth_width_Q14, smooth_coef_Q16 );
	l32i.n	a12, sp, 36	# %sfp,
	l32i.n	a8, sp, 60	# %sfp,
	l16si	a4, a12, 28	# state_391(D)->smth_width_Q14, _124
	slli	a3, a8, 16	# tmp704,,
	sub	a2, a2, a4	# _126, width_Q14, _124
	srai	a3, a3, 16	# _129, tmp704,
	extui	a5, a2, 0, 16	# tmp705, _126,
	srai	a2, a2, 16	# tmp708, _126,
	mul16s	a2, a2, a3	# tmp709, tmp708, _129
	mull	a5, a5, a3	# tmp706, tmp705, _129
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:131:     state->smth_width_Q14 = (opus_int16)silk_SMLAWB( state->smth_width_Q14, width_Q14 - state->smth_width_Q14, smooth_coef_Q16 );
	add.n	a4, a4, a2	# tmp711, _124, tmp709
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:131:     state->smth_width_Q14 = (opus_int16)silk_SMLAWB( state->smth_width_Q14, width_Q14 - state->smth_width_Q14, smooth_coef_Q16 );
	srai	a3, a5, 16	# tmp707, tmp706,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:131:     state->smth_width_Q14 = (opus_int16)silk_SMLAWB( state->smth_width_Q14, width_Q14 - state->smth_width_Q14, smooth_coef_Q16 );
	add.n	a3, a3, a4	# tmp714, tmp707, tmp711
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:131:     state->smth_width_Q14 = (opus_int16)silk_SMLAWB( state->smth_width_Q14, width_Q14 - state->smth_width_Q14, smooth_coef_Q16 );
	s16i	a3, a12, 28	# state_391(D)->smth_width_Q14, tmp714
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:134:     *mid_only_flag = 0;
	l32i	a12, sp, 72	# %sfp,
	movi.n	a2, 0	# tmp715,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:135:     if( toMono ) {
	l32i	a8, sp, 168	# toMono,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:134:     *mid_only_flag = 0;
	s8i	a2, a12, 0	# *mid_only_flag_434(D), tmp715
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:135:     if( toMono ) {
	beqz.n	a8, .L38	#,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:140:         silk_stereo_quant_pred( pred_Q13, ix );
	l32i	a3, sp, 100	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:138:         pred_Q13[ 0 ] = 0;
	movi.n	a4, 0	# tmp716,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:140:         silk_stereo_quant_pred( pred_Q13, ix );
	addi.n	a2, sp, 8	#,,
	s32i	a4, sp, 88	# %sfp, tmp716
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:138:         pred_Q13[ 0 ] = 0;
	s32i.n	a4, sp, 8	# pred_Q13, tmp716
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:139:         pred_Q13[ 1 ] = 0;
	s32i.n	a4, sp, 12	# pred_Q13, tmp716
	s32i	a4, sp, 76	# %sfp, tmp716
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:140:         silk_stereo_quant_pred( pred_Q13, ix );
	call0	silk_stereo_quant_pred		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:137:         width_Q14 = 0;
	l32i	a11, sp, 88	# %sfp,
	s32i	a11, sp, 168	# toMono,
	j	.L39		#
.L38:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:141:     } else if( state->width_prev_Q14 == 0 &&
	l32i.n	a12, sp, 36	# %sfp,
	l32i.n	a6, sp, 40	# %sfp,
	l16si	a12, a12, 30	# state_391(D)->width_prev_Q14,
	l32i.n	a8, sp, 36	# %sfp,
	s32i	a12, sp, 76	# %sfp,
	slli	a2, a6, 3	# _1603,,
	l16si	a3, a8, 28	# state_391(D)->smth_width_Q14, pretmp_1691
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:141:     } else if( state->width_prev_Q14 == 0 &&
	bnez.n	a12, .L40	#,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:142:         ( 8 * total_rate_bps < 13 * min_mid_rate_bps || silk_SMULWB( frac_Q16, state->smth_width_Q14 ) < SILK_FIX_CONST( 0.05, 14 ) ) )
	slli	a4, a11, 1	# tmp724, _1426,
	add.n	a4, a4, a11	# tmp725, tmp724, _1426
	slli	a4, a4, 2	# tmp726, tmp725,
	add.n	a11, a4, a11	# tmp727, tmp726, _1426
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:141:     } else if( state->width_prev_Q14 == 0 &&
	blt	a2, a11, .L41	# _1603, tmp727,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:142:         ( 8 * total_rate_bps < 13 * min_mid_rate_bps || silk_SMULWB( frac_Q16, state->smth_width_Q14 ) < SILK_FIX_CONST( 0.05, 14 ) ) )
	extui	a2, a9, 0, 16	# tmp728, frac_Q16,
	mull	a2, a2, a3	# tmp729, tmp728, pretmp_1691
	srai	a4, a9, 16	# tmp731, frac_Q16,
	mull	a4, a4, a3	# tmp732, tmp731, pretmp_1691
	srai	a2, a2, 16	# tmp730, tmp729,
	add.n	a2, a2, a4	# tmp733, tmp730, tmp732
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:142:         ( 8 * total_rate_bps < 13 * min_mid_rate_bps || silk_SMULWB( frac_Q16, state->smth_width_Q14 ) < SILK_FIX_CONST( 0.05, 14 ) ) )
	movi	a4, 0x332	# tmp734,
	blt	a4, a2, .L42	# tmp734, tmp733,
.L41:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:146:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	l32i.n	a4, sp, 8	# pred_Q13, pred_Q13
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:147:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	l32i	a11, sp, 88	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:148:         silk_stereo_quant_pred( pred_Q13, ix );
	addi.n	a2, sp, 8	#,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:147:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	mul16s	a5, a11, a3	# tmp738,, pretmp_1691
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:146:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	mul16s	a3, a4, a3	# tmp736, pred_Q13, pretmp_1691
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:147:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	srai	a5, a5, 14	# tmp739, tmp738,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:146:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	srai	a4, a3, 14	# tmp737, tmp736,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:148:         silk_stereo_quant_pred( pred_Q13, ix );
	l32i	a3, sp, 100	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:146:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	s32i.n	a4, sp, 8	# pred_Q13, tmp737
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:147:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	s32i.n	a5, sp, 12	# pred_Q13, tmp739
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:148:         silk_stereo_quant_pred( pred_Q13, ix );
	call0	silk_stereo_quant_pred		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:153:         mid_side_rates_bps[ 0 ] = total_rate_bps;
	l32i.n	a6, sp, 40	# %sfp,
	l32i.n	a12, sp, 52	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:151:         pred_Q13[ 0 ] = 0;
	movi.n	a2, 0	# tmp741,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:155:         *mid_only_flag = 1;
	l32i	a8, sp, 72	# %sfp,
	l32i	a11, sp, 168	# toMono,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:154:         mid_side_rates_bps[ 1 ] = 0;
	s32i.n	a2, a12, 4	# MEM[(opus_int32 *)mid_side_rates_bps_426(D) + 4B], tmp741
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:153:         mid_side_rates_bps[ 0 ] = total_rate_bps;
	s32i.n	a6, a12, 0	# *mid_side_rates_bps_426(D),
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:151:         pred_Q13[ 0 ] = 0;
	s32i.n	a2, sp, 8	# pred_Q13, tmp741
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:152:         pred_Q13[ 1 ] = 0;
	s32i.n	a2, sp, 12	# pred_Q13, tmp741
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:155:         *mid_only_flag = 1;
	movi.n	a2, 1	# tmp744,
	s8i	a2, a8, 0	# *mid_only_flag_434(D), tmp744
	s32i	a11, sp, 88	# %sfp,
	j	.L43		#
.L40:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:157:         ( 8 * total_rate_bps < 11 * min_mid_rate_bps || silk_SMULWB( frac_Q16, state->smth_width_Q14 ) < SILK_FIX_CONST( 0.02, 14 ) ) )
	slli	a4, a11, 2	# tmp746, _1426,
	add.n	a4, a4, a11	# tmp747, tmp746, _1426
	slli	a4, a4, 1	# tmp748, tmp747,
	add.n	a11, a4, a11	# tmp749, tmp748, _1426
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:156:     } else if( state->width_prev_Q14 != 0 &&
	blt	a2, a11, .L44	# _1603, tmp749,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:157:         ( 8 * total_rate_bps < 11 * min_mid_rate_bps || silk_SMULWB( frac_Q16, state->smth_width_Q14 ) < SILK_FIX_CONST( 0.02, 14 ) ) )
	extui	a4, a9, 0, 16	# tmp750, frac_Q16,
	mull	a4, a4, a3	# tmp751, tmp750, pretmp_1691
	srai	a2, a9, 16	# tmp753, frac_Q16,
	mull	a2, a2, a3	# tmp754, tmp753, pretmp_1691
	srai	a4, a4, 16	# tmp752, tmp751,
	add.n	a2, a4, a2	# tmp755, tmp752, tmp754
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:157:         ( 8 * total_rate_bps < 11 * min_mid_rate_bps || silk_SMULWB( frac_Q16, state->smth_width_Q14 ) < SILK_FIX_CONST( 0.02, 14 ) ) )
	movi	a4, 0x147	# tmp756,
	blt	a4, a2, .L42	# tmp756, tmp755,
.L44:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:161:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	l32i.n	a4, sp, 8	# pred_Q13, pred_Q13
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:162:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	l32i	a12, sp, 88	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:163:         silk_stereo_quant_pred( pred_Q13, ix );
	addi.n	a2, sp, 8	#,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:162:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	mul16s	a5, a12, a3	# tmp760,, pretmp_1691
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:161:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	mul16s	a3, a4, a3	# tmp758, pred_Q13, pretmp_1691
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:162:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	srai	a5, a5, 14	# tmp761, tmp760,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:161:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	srai	a4, a3, 14	# tmp759, tmp758,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:163:         silk_stereo_quant_pred( pred_Q13, ix );
	l32i	a3, sp, 100	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:161:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	s32i.n	a4, sp, 8	# pred_Q13, tmp759
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:162:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	s32i.n	a5, sp, 12	# pred_Q13, tmp761
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:163:         silk_stereo_quant_pred( pred_Q13, ix );
	call0	silk_stereo_quant_pred		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:167:         pred_Q13[ 1 ] = 0;
	l32i	a8, sp, 168	# toMono,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:166:         pred_Q13[ 0 ] = 0;
	movi.n	a2, 0	# tmp763,
	s32i.n	a2, sp, 8	# pred_Q13, tmp763
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:167:         pred_Q13[ 1 ] = 0;
	s32i.n	a2, sp, 12	# pred_Q13, tmp763
	s32i	a8, sp, 88	# %sfp,
	s32i	a2, sp, 76	# %sfp, tmp763
	j	.L39		#
.L42:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:168:     } else if( state->smth_width_Q14 > SILK_FIX_CONST( 0.95, 14 ) ) {
	l32r	a2, .LC11	#, tmp765
	slli	a2, a2, 16	# tmp767, tmp765,
	srai	a2, a2, 16	# tmp766, tmp767,
	bge	a2, a3, .L45	# tmp766, pretmp_1691,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:170:         silk_stereo_quant_pred( pred_Q13, ix );
	l32i	a3, sp, 100	# %sfp,
	addi.n	a2, sp, 8	#,,
	call0	silk_stereo_quant_pred		#
	l32r	a11, .LC0	#,
	l32r	a12, .LC2	#,
	s32i	a11, sp, 76	# %sfp,
	s32i	a12, sp, 88	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:171:         width_Q14 = SILK_FIX_CONST( 1, 14 );
	s32i	a11, sp, 168	# toMono,
	j	.L39		#
.L45:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:174:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	l32i.n	a5, sp, 8	# pred_Q13, pred_Q13
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:175:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	l32i	a6, sp, 88	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:176:         silk_stereo_quant_pred( pred_Q13, ix );
	addi.n	a2, sp, 8	#,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:175:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	mul16s	a4, a6, a3	# tmp772,, pretmp_1691
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:174:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	mul16s	a3, a5, a3	# tmp770, pred_Q13, pretmp_1691
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:175:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	srai	a4, a4, 14	# tmp773, tmp772,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:174:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	srai	a5, a3, 14	# tmp771, tmp770,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:176:         silk_stereo_quant_pred( pred_Q13, ix );
	l32i	a3, sp, 100	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:174:         pred_Q13[ 0 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 0 ] ), 14 );
	s32i.n	a5, sp, 8	# pred_Q13, tmp771
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:175:         pred_Q13[ 1 ] = silk_RSHIFT( silk_SMULBB( state->smth_width_Q14, pred_Q13[ 1 ] ), 14 );
	s32i.n	a4, sp, 12	# pred_Q13, tmp773
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:176:         silk_stereo_quant_pred( pred_Q13, ix );
	call0	silk_stereo_quant_pred		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:177:         width_Q14 = state->smth_width_Q14;
	l32i.n	a8, sp, 36	# %sfp,
	l16si	a8, a8, 28	# state_391(D)->smth_width_Q14,
	slli	a11, a8, 10	#,,
	s32i	a8, sp, 76	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:177:         width_Q14 = state->smth_width_Q14;
	s32i	a8, sp, 168	# toMono,
	s32i	a11, sp, 88	# %sfp,
.L39:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:181:     if( *mid_only_flag == 1 ) {
	l32i	a12, sp, 72	# %sfp,
	l8ui	a2, a12, 0	# *mid_only_flag_434(D), tmp777
	bnei	a2, 1, .L46	# tmp777,,
.L43:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:182:         state->silent_side_len += frame_length - STEREO_INTERP_LEN_MS * fs_kHz;
	l32i	a6, sp, 80	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:182:         state->silent_side_len += frame_length - STEREO_INTERP_LEN_MS * fs_kHz;
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:182:         state->silent_side_len += frame_length - STEREO_INTERP_LEN_MS * fs_kHz;
	slli	a2, a6, 13	# tmp782,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:182:         state->silent_side_len += frame_length - STEREO_INTERP_LEN_MS * fs_kHz;
	l16ui	a3, a8, 32	# state_391(D)->silent_side_len,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:182:         state->silent_side_len += frame_length - STEREO_INTERP_LEN_MS * fs_kHz;
	sub	a2, a2, a6	# tmp784, tmp782,
	slli	a2, a2, 3	# tmp786, tmp784,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:182:         state->silent_side_len += frame_length - STEREO_INTERP_LEN_MS * fs_kHz;
	l32i	a11, sp, 176	# frame_length,
	add.n	a2, a2, a3	# tmp789, tmp786, state_391(D)->silent_side_len
	add.n	a2, a2, a11	# tmp792, tmp789,
	slli	a2, a2, 16	# tmp793, tmp792,
	srai	a2, a2, 16	# _198, tmp793,
	s16i	a2, a8, 32	# state_391(D)->silent_side_len, _198
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:183:         if( state->silent_side_len < LA_SHAPE_MS * fs_kHz ) {
	l32i	a12, sp, 96	# %sfp,
	l32i	a8, sp, 172	# fs_kHz,
	add.n	a3, a12, a8	# tmp796,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:183:         if( state->silent_side_len < LA_SHAPE_MS * fs_kHz ) {
	bge	a2, a3, .L47	# _198, tmp796,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:184:             *mid_only_flag = 0;
	l32i	a11, sp, 72	# %sfp,
	movi.n	a2, 0	# tmp797,
	s8i	a2, a11, 0	# *mid_only_flag_434(D), tmp797
	j	.L48		#
.L47:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:187:             state->silent_side_len = 10000;
	l32r	a2, .LC12	#,
	l32i.n	a12, sp, 36	# %sfp,
	l32i	a11, sp, 72	# %sfp,
	s16i	a2, a12, 32	# state_391(D)->silent_side_len,
	j	.L49		#
.L46:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:190:         state->silent_side_len = 0;
	l32i.n	a8, sp, 36	# %sfp,
	movi.n	a2, 0	# tmp799,
	s16i	a2, a8, 32	# state_391(D)->silent_side_len, tmp799
	mov.n	a11, a12	#,
.L49:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:193:     if( *mid_only_flag == 0 && mid_side_rates_bps[ 1 ] < 1 ) {
	l8ui	a2, a11, 0	# *mid_only_flag_434(D), tmp802
	bnez.n	a2, .L50	# tmp802,
.L48:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:193:     if( *mid_only_flag == 0 && mid_side_rates_bps[ 1 ] < 1 ) {
	l32i.n	a12, sp, 52	# %sfp,
	l32i.n	a2, a12, 4	# MEM[(opus_int32 *)mid_side_rates_bps_426(D) + 4B], MEM[(opus_int32 *)mid_side_rates_bps_426(D) + 4B]
	bgei	a2, 1, .L50	# MEM[(opus_int32 *)mid_side_rates_bps_426(D) + 4B],,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:195:         mid_side_rates_bps[ 0 ] = silk_max_int( 1, total_rate_bps - mid_side_rates_bps[ 1 ]);
	l32i.n	a6, sp, 40	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:194:         mid_side_rates_bps[ 1 ] = 1;
	movi.n	a3, 1	# tmp804,
	s32i.n	a3, a12, 4	# MEM[(opus_int32 *)mid_side_rates_bps_426(D) + 4B], tmp804
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:195:         mid_side_rates_bps[ 0 ] = silk_max_int( 1, total_rate_bps - mid_side_rates_bps[ 1 ]);
	addi.n	a2, a6, -1	# tmp806,,
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	bge	a2, a3, .L51	# tmp806,,
	mov.n	a2, a3	# tmp806, tmp804
.L51:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:195:         mid_side_rates_bps[ 0 ] = silk_max_int( 1, total_rate_bps - mid_side_rates_bps[ 1 ]);
	l32i.n	a8, sp, 52	# %sfp,
	s32i.n	a2, a8, 0	# *mid_side_rates_bps_426(D), tmp806
.L50:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:202:     denom_Q16  = silk_DIV32_16( (opus_int32)1 << 16, STEREO_INTERP_LEN_MS * fs_kHz );
	l32i	a11, sp, 172	# fs_kHz,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:201:     w_Q24      =  silk_LSHIFT( state->width_prev_Q14, 10 );
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:202:     denom_Q16  = silk_DIV32_16( (opus_int32)1 << 16, STEREO_INTERP_LEN_MS * fs_kHz );
	slli	a14, a11, 3	# _211,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:202:     denom_Q16  = silk_DIV32_16( (opus_int32)1 << 16, STEREO_INTERP_LEN_MS * fs_kHz );
	l32r	a2, .LC6	#,
	mov.n	a3, a14	#, _211
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:201:     w_Q24      =  silk_LSHIFT( state->width_prev_Q14, 10 );
	l16si	a12, a8, 30	# state_391(D)->width_prev_Q14, _208
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:202:     denom_Q16  = silk_DIV32_16( (opus_int32)1 << 16, STEREO_INTERP_LEN_MS * fs_kHz );
	call0	__divsi3		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:199:     pred0_Q13  = -state->pred_prev_Q13[ 0 ];
	l32i.n	a11, sp, 36	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	l16si	a5, sp, 12	# pred_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:199:     pred0_Q13  = -state->pred_prev_Q13[ 0 ];
	l16si	a13, a11, 0	# state_391(D)->pred_prev_Q13, _204
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	l16si	a3, sp, 8	# pred_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	l32i	a8, sp, 168	# toMono,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	s32i	a5, sp, 80	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	slli	a2, a2, 16	# tmp820,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	sub	a7, a8, a12	# _231,, _208
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:200:     pred1_Q13  = -state->pred_prev_Q13[ 1 ];
	l16si	a4, a11, 2	# state_391(D)->pred_prev_Q13, _206
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	srai	a8, a2, 16	# _216, tmp820,
	sub	a5, a3, a13	# tmp821,, _204
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	l32i	a11, sp, 80	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	mul16s	a5, a5, a8	# tmp822, tmp821, _216
	s32i	a3, sp, 72	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	extui	a2, a7, 0, 16	# tmp830, _231,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	sub	a3, a11, a4	# tmp826,, _206
	mul16s	a3, a3, a8	# tmp827, tmp826, _216
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	mull	a2, a2, a8	# tmp831, tmp830, _216
	srai	a6, a7, 16	# tmp833, _231,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	srai	a5, a5, 15	# tmp823, tmp822,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	mull	a6, a6, a8	# tmp834, tmp833, _216
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	addi.n	a5, a5, 1	# tmp824, tmp823,
	srai	a5, a5, 1	#, tmp824,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	srai	a3, a3, 15	# tmp828, tmp827,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	srai	a2, a2, 16	# tmp832, tmp831,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	addi.n	a3, a3, 1	# tmp829, tmp828,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	add.n	a2, a2, a6	# tmp835, tmp832, tmp834
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:201:     w_Q24      =  silk_LSHIFT( state->width_prev_Q14, 10 );
	slli	a9, a12, 10	# w_Q24, _208,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	s32i.n	a5, sp, 48	# %sfp,
	l32i.n	a12, sp, 8	# pred_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	l32i.n	a5, sp, 12	# pred_Q13,
	srai	a3, a3, 1	#, tmp829,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	slli	a2, a2, 10	#, tmp835,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:203:     delta0_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	s32i	a12, sp, 84	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:204:     delta1_Q13 = -silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	s32i	a5, sp, 96	# %sfp,
	s32i.n	a3, sp, 52	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:205:     deltaw_Q24 =  silk_LSHIFT( silk_SMULWB( width_Q14 - state->width_prev_Q14, denom_Q16 ), 10 );
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:199:     pred0_Q13  = -state->pred_prev_Q13[ 0 ];
	neg	a13, a13	# pred0_Q13, _204
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:200:     pred1_Q13  = -state->pred_prev_Q13[ 1 ];
	neg	a4, a4	# pred1_Q13, _206
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:206:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	movi.n	a10, 0	# n,
	l32r	a8, .LC3	#, tmp950
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:206:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	bgei	a14, 1, .L82	# _211,,
.L56:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:216:     pred0_Q13 = -pred_Q13[ 0 ];
	l32i	a6, sp, 84	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:217:     pred1_Q13 = -pred_Q13[ 1 ];
	l32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:219:     for( n = STEREO_INTERP_LEN_MS * fs_kHz; n < frame_length; n++ ) {
	l32i	a8, sp, 176	# frame_length,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:216:     pred0_Q13 = -pred_Q13[ 0 ];
	neg	a13, a6	# pred0_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:217:     pred1_Q13 = -pred_Q13[ 1 ];
	neg	a12, a7	# pred1_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:219:     for( n = STEREO_INTERP_LEN_MS * fs_kHz; n < frame_length; n++ ) {
	blt	a14, a8, .L53	# _211,,
	j	.L54		#
.L82:
	s32i.n	a14, sp, 40	# %sfp, _211
	l32i	a14, sp, 68	# %sfp, mid
.L52:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	l32i.n	a11, sp, 56	# %sfp,
	slli	a6, a10, 1	# _1571, n,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	l32i.n	a12, sp, 44	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	add.n	a5, a11, a6	# tmp839,, _1571
	addi.n	a7, a6, 2	# _1560, _1571,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:209:         w_Q24   += deltaw_Q24;
	l32i.n	a11, sp, 60	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	add.n	a2, a14, a6	# tmp843, mid, _1571
	add.n	a3, a14, a7	# tmp836, mid, _1560
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	add.n	a7, a12, a7	# tmp850,, _1560
	l16si	a7, a7, 0	# *_1549, _1547
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:209:         w_Q24   += deltaw_Q24;
	add.n	a9, a9, a11	# w_Q24, w_Q24,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	l16si	a12, a5, 0	# *_1565, tmp840
	l16si	a11, a2, 0	# *_1570, tmp844
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	extui	a5, a9, 0, 16	# tmp857, w_Q24,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	add.n	a11, a12, a11	# tmp847, tmp840, tmp844
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	mull	a5, a5, a7	#, tmp857, _1547
	srai	a12, a9, 16	# tmp860, w_Q24,
	mull	a12, a12, a7	#, tmp860, _1547
	l32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	l16si	a3, a3, 0	# *_1559, _1557
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	s32i.n	a5, sp, 32	# %sfp,
	sub	a4, a4, a2	# pred1_Q13, pred1_Q13,
	l32i.n	a5, sp, 48	# %sfp,
	s32i	a12, sp, 68	# %sfp,
	l32i.n	a12, sp, 32	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:212:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	slli	a2, a3, 11	# _1523, _1557,
	slli	a15, a4, 16	# tmp856, pred1_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	slli	a3, a3, 1	# tmp848, _1557,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:212:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	srai	a15, a15, 16	# _1520, tmp856,
	sub	a13, a13, a5	# pred0_Q13, pred0_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	add.n	a3, a11, a3	# tmp849, tmp847, tmp848
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	srai	a5, a12, 16	# tmp859,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:212:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	srai	a11, a2, 16	# tmp863, _1523,
	l32i	a12, sp, 68	# %sfp,
	extui	a2, a2, 0, 16	# tmp866, _1523,
	mull	a11, a11, a15	# tmp864, tmp863, _1520
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:210:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	slli	a3, a3, 9	# sum, tmp849,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	slli	a7, a13, 16	# tmp853, pred0_Q13,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:212:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	mull	a2, a2, a15	# tmp867, tmp866, _1520
	add.n	a5, a5, a12	# tmp862, tmp859,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	srai	a15, a7, 16	# _1540, tmp853,
	extui	a7, a3, 0, 16	# tmp854, sum,
	srai	a3, a3, 16	# tmp870, sum,
	add.n	a5, a5, a11	# tmp865, tmp862, tmp864
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:212:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	srai	a2, a2, 16	# tmp868, tmp867,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:211:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	mull	a7, a7, a15	# tmp855, tmp854, _1540
	mull	a3, a3, a15	# tmp871, tmp870, _1540
	add.n	a5, a5, a2	# tmp869, tmp865, tmp868
	add.n	a3, a5, a3	# _1512, tmp869, tmp871
	srai	a7, a7, 16	# _1536, tmp855,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:212:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	add.n	a7, a3, a7	# sum, _1512, _1536
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	srai	a2, a7, 7	# tmp873, sum,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	l32i	a11, sp, 64	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	addi.n	a2, a2, 1	# tmp874, tmp873,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	add.n	a6, a11, a6	# tmp878,, _1571
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	srai	a2, a2, 1	# _1508, tmp874,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	addi	a6, a6, -2	# tmp879, tmp878,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:206:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	addi.n	a10, a10, 1	# n, n,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	mov.n	a3, a8	# iftmp$38_1506, tmp950
	blt	a8, a2, .L55	# tmp950, _1508,
	l32r	a3, .LC4	#, iftmp$38_1506
	slli	a5, a2, 16	# tmp877, _1508,
	blt	a2, a3, .L55	# _1508, iftmp$38_1506,
	srai	a3, a5, 16	# iftmp$38_1506, tmp877,
.L55:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:206:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	l32i.n	a12, sp, 40	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:213:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	s16i	a3, a6, 0	# *_1503, iftmp$38_1506
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:206:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	blt	a10, a12, .L52	# n,,
	mov.n	a14, a12	# _211,
	j	.L56		#
.L54:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:225:     state->pred_prev_Q13[ 0 ] = (opus_int16)pred_Q13[ 0 ];
	l32i	a3, sp, 80	# %sfp,
	l32i	a5, sp, 72	# %sfp,
	l32i.n	a8, sp, 36	# %sfp,
	slli	a2, a3, 16	# tmp886,,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:227:     state->width_prev_Q14     = (opus_int16)width_Q14;
	l32i	a11, sp, 76	# %sfp,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:225:     state->pred_prev_Q13[ 0 ] = (opus_int16)pred_Q13[ 0 ];
	extui	a4, a5, 0, 16	# tmp887,
	or	a4, a4, a2	# tmp888, tmp887, tmp886
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:228:     RESTORE_STACK;
	l32i.n	a3, sp, 4	# _saved_stack,
	l32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:225:     state->pred_prev_Q13[ 0 ] = (opus_int16)pred_Q13[ 0 ];
	s32i.n	a4, a8, 0	# MEM[(short int *)state_391(D)], tmp888
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:227:     state->width_prev_Q14     = (opus_int16)width_Q14;
	s16i	a11, a8, 30	# state_391(D)->width_prev_Q14,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:228:     RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:229: }
	l32i	a0, sp, 156	#,
	movi	a9, 0xa0	#,
	l32i	a12, sp, 152	#,
	l32i	a13, sp, 148	#,
	l32i	a14, sp, 144	#,
	l32i	a15, sp, 140	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L53:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:221:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	l32i	a2, sp, 88	# %sfp,
	slli	a10, a14, 1	# tmp893, _211,
	l32i	a8, sp, 92	# %sfp,
	srai	a2, a2, 16	#,,
	addi.n	a11, a14, 1	# tmp891, _211,
	mov.n	a4, a10	# tmp896, tmp893
	s32i.n	a2, sp, 32	# %sfp,
	l32i	a5, sp, 88	# %sfp,
	l32i.n	a2, sp, 56	# %sfp,
	l32i.n	a6, sp, 44	# %sfp,
	l32i	a7, sp, 64	# %sfp,
	addi	a15, a8, -4	# tmp899,,
	slli	a13, a13, 16	# tmp889, pred0_Q13,
	slli	a12, a12, 16	# tmp890, pred1_Q13,
	slli	a11, a11, 1	# tmp892, tmp891,
	addi	a10, a10, -2	# tmp895, tmp893,
	addi	a4, a4, -4	# tmp898, tmp896,
	l32r	a8, .LC3	#, tmp950
	extui	a14, a5, 0, 16	# _1579,,
	srai	a13, a13, 16	# _1581, tmp889,
	srai	a12, a12, 16	# _1583, tmp890,
	add.n	a11, a6, a11	# ivtmp$66,, tmp892
	add.n	a10, a7, a10	# ivtmp$68,, tmp895
	add.n	a4, a2, a4	# ivtmp$70,, tmp898
	add.n	a15, a2, a15	# _321,, tmp899
.L58:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:220:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	l16si	a6, a4, 2	# MEM[base: _323, offset: 2B], _1660
	l16si	a2, a4, 0	# MEM[base: _323, offset: 0B], tmp905
	l16si	a3, a4, 4	# MEM[base: _323, offset: 4B], tmp902
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:222:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	slli	a5, a6, 11	# _1639, _1660,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:221:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	l16si	a7, a11, 0	# MEM[base: _315, offset: 0B], _1649
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:220:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	add.n	a3, a3, a2	# tmp908, tmp902, tmp905
	slli	a6, a6, 1	# tmp909, _1660,
	add.n	a3, a3, a6	# tmp910, tmp908, tmp909
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:221:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	l32i.n	a6, sp, 32	# %sfp,
	mull	a2, a14, a7	# tmp915, _1579, _1649
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:222:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	srai	a9, a5, 16	# tmp919, _1639,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:221:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	mull	a7, a6, a7	# tmp917,, _1649
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:222:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	extui	a5, a5, 0, 16	# tmp922, _1639,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:220:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( mid[ n ] + (opus_int32)mid[ n + 2 ], mid[ n + 1 ], 1 ), 9 );    /* Q11 */
	slli	a3, a3, 9	# sum, tmp910,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:221:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	srai	a2, a2, 16	# tmp916, tmp915,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:222:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	mull	a9, a9, a12	# tmp920, tmp919, _1583
	mull	a5, a5, a12	# tmp923, tmp922, _1583
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:221:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	extui	a6, a3, 0, 16	# tmp913, sum,
	add.n	a7, a2, a7	# tmp918, tmp916, tmp917
	srai	a3, a3, 16	# tmp926, sum,
	mull	a3, a3, a13	# tmp927, tmp926, _1581
	mull	a6, a6, a13	# tmp914, tmp913, _1581
	add.n	a2, a7, a9	# tmp921, tmp918, tmp920
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:222:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	srai	a5, a5, 16	# tmp924, tmp923,
	add.n	a2, a2, a5	# tmp925, tmp921, tmp924
	add.n	a2, a2, a3	# _1630, tmp925, tmp927
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:221:         sum = silk_SMLAWB( silk_SMULWB( w_Q24, side[ n + 1 ] ), sum, pred0_Q13 );               /* Q8  */
	srai	a6, a6, 16	# _1641, tmp914,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:222:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)mid[ n + 1 ], 11 ), pred1_Q13 );       /* Q8  */
	add.n	a2, a2, a6	# sum, _1630, _1641
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:223:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	srai	a2, a2, 7	# tmp929, sum,
	addi.n	a2, a2, 1	# tmp930, tmp929,
	srai	a2, a2, 1	# _1626, tmp930,
	addi.n	a4, a4, 2	# ivtmp$70, ivtmp$70,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:223:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	mov.n	a3, a8	# iftmp$49_1624, tmp950
	blt	a8, a2, .L57	# tmp950, _1626,
	l32r	a3, .LC4	#, iftmp$49_1624
	slli	a5, a2, 16	# tmp933, _1626,
	blt	a2, a3, .L57	# _1626, tmp7,
	srai	a3, a5, 16	# iftmp$49_1624, tmp933,
.L57:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:223:         x2[ n - 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	s16i	a3, a10, 0	# MEM[base: _316, offset: 0B], iftmp$49_1624
	addi.n	a11, a11, 2	# ivtmp$66, ivtmp$66,
	addi.n	a10, a10, 2	# ivtmp$68, ivtmp$68,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:219:     for( n = STEREO_INTERP_LEN_MS * fs_kHz; n < frame_length; n++ ) {
	bne	a4, a15, .L58	# ivtmp$70, _321,
	j	.L54		#
.L80:
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:86:     ALLOC( LP_side, frame_length, opus_int16 );
	l32i	a2, sp, 176	# frame_length,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a15, a2	# LP_side,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:87:     ALLOC( HP_side, frame_length, opus_int16 );
	l32i	a2, sp, 176	# frame_length,
	movi.n	a3, 2	#,
	movi.n	a4, 0	#,
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a9, a2	# HP_side,
	l32i.n	a3, sp, 44	# %sfp, ivtmp$96
	mov.n	a7, a15	# ivtmp$97, LP_side
	mov.n	a6, a2	# ivtmp$98, HP_side
	j	.L11		#
.L79:
	mov.n	a2, a8	#,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:86:     ALLOC( LP_side, frame_length, opus_int16 );
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a15, a2	# LP_side,
# @OPUS@\upstream\silk\stereo_LR_to_MS.c:87:     ALLOC( HP_side, frame_length, opus_int16 );
	l32i	a2, sp, 176	# frame_length,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a9, a2	# HP_side,
	j	.L59		#
	.size	silk_stereo_LR_to_MS, .-silk_stereo_LR_to_MS
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
