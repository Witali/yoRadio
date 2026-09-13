# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/vector_ops_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"vector_ops_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\vector_ops_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\vector_ops_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\vector_ops_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\vector_ops_FIX.c.s.raw
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
	.section	.text.silk_scale_copy_vector16,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_scale_copy_vector16
	.type	silk_scale_copy_vector16, @function
# Function: silk_scale_copy_vector16
# Module: upstream/silk/fixed/vector_ops_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "pitch.h"
# C context:
# C context: /* Copy and multiply a vector by a constant */
# C context: void silk_scale_copy_vector16(
# C context: opus_int16                  *data_out,
# C context: const opus_int16            *data_in,
# C context: opus_int32                  gain_Q16,           /* I    Gain in Q16                                                 */
# C context: const opus_int              dataSize            /* I    Length                                                      */
silk_scale_copy_vector16:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:46:     for( i = 0; i < dataSize; i++ ) {
	blti	a5, 1, .L1	# dataSize,,
	slli	a5, a5, 1	# tmp62, dataSize,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:47:         tmp32 = silk_SMULWB( gain_Q16, data_in[ i ] );
	srai	a8, a4, 16	# _1, gain_Q16,
	add.n	a7, a3, a5	# _29, ivtmp$11, tmp62
	extui	a4, a4, 0, 16	# _42, gain_Q16,
.L3:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:47:         tmp32 = silk_SMULWB( gain_Q16, data_in[ i ] );
	l16si	a6, a3, 0	# MEM[base: _34, offset: 0B], _6
	addi.n	a3, a3, 2	# ivtmp$11, ivtmp$11,
	mull	a5, a6, a4	# tmp65, _6, _42
	mull	a6, a8, a6	# tmp67, _1, _6
	srai	a5, a5, 16	# tmp66, tmp65,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:47:         tmp32 = silk_SMULWB( gain_Q16, data_in[ i ] );
	add.n	a5, a5, a6	# tmp32, tmp66, tmp67
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:48:         data_out[ i ] = (opus_int16)silk_CHECK_FIT16( tmp32 );
	s16i	a5, a2, 0	# MEM[base: _33, offset: 0B], tmp32
	addi.n	a2, a2, 2	# ivtmp$12, ivtmp$12,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:46:     for( i = 0; i < dataSize; i++ ) {
	bne	a7, a3, .L3	# _29, ivtmp$11,
.L1:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:50: }
	ret.n
	.size	silk_scale_copy_vector16, .-silk_scale_copy_vector16
	.global	__muldi3
	.section	.text.silk_scale_vector32_Q26_lshift_18,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_scale_vector32_Q26_lshift_18
	.type	silk_scale_vector32_Q26_lshift_18, @function
# Function: silk_scale_vector32_Q26_lshift_18
# Module: upstream/silk/fixed/vector_ops_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Multiply a vector by a constant */
# C context: void silk_scale_vector32_Q26_lshift_18(
# C context: opus_int32                  *data1,             /* I/O  Q0/Q18                                                      */
# C context: opus_int32                  gain_Q26,           /* I    Q26                                                         */
# C context: opus_int                    dataSize            /* I    length                                                      */
# C context: )
silk_scale_vector32_Q26_lshift_18:
	addi	sp, sp, -32	#,,
	s32i.n	a14, sp, 16	#,
	s32i.n	a0, sp, 28	#,
	s32i.n	a12, sp, 24	#,
	s32i.n	a13, sp, 20	#,
	s32i.n	a15, sp, 12	#,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:58: {
	mov.n	a14, a3	# gain_Q26, gain_Q26
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:61:     for( i = 0; i < dataSize; i++ ) {
	blti	a4, 1, .L7	# dataSize,,
	slli	a4, a4, 2	# tmp57, dataSize,
	mov.n	a12, a2	# ivtmp$17, data1
	srai	a15, a3, 31	# _33, gain_Q26,
	add.n	a13, a2, a4	# _23, ivtmp$17, tmp57
.L9:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:62:         data1[ i ] = (opus_int32)silk_CHECK_FIT32( silk_RSHIFT64( silk_SMULL( data1[ i ], gain_Q26 ), 8 ) );    /* OUTPUT: Q18 */
	l32i.n	a3, a12, 0	# MEM[base: _28, offset: 0B], MEM[base: _28, offset: 0B]
	mov.n	a4, a14	#, gain_Q26
	mov.n	a2, a3	#, MEM[base: _28, offset: 0B]
	mov.n	a5, a15	#, _33
	srai	a3, a3, 31	#, MEM[base: _28, offset: 0B],
	call0	__muldi3		#
	slli	a3, a3, 24	# tmp63,,
	srli	a2, a2, 8	# tmp70,,
	or	a2, a3, a2	# tmp70, tmp63, tmp70
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:62:         data1[ i ] = (opus_int32)silk_CHECK_FIT32( silk_RSHIFT64( silk_SMULL( data1[ i ], gain_Q26 ), 8 ) );    /* OUTPUT: Q18 */
	s32i.n	a2, a12, 0	# MEM[base: _28, offset: 0B], tmp70
	addi.n	a12, a12, 4	# ivtmp$17, ivtmp$17,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:61:     for( i = 0; i < dataSize; i++ ) {
	bne	a13, a12, .L9	# _23, ivtmp$17,
.L7:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:64: }
	l32i.n	a0, sp, 28	#,
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_scale_vector32_Q26_lshift_18, .-silk_scale_vector32_Q26_lshift_18
	.section	.text.silk_inner_prod_aligned,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_inner_prod_aligned
	.type	silk_inner_prod_aligned, @function
# Function: silk_inner_prod_aligned
# Module: upstream/silk/fixed/vector_ops_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /*        * inVec1 and inVec2 should be at least 2 byte aligned.                */
# C context: /*        * len should be positive 16bit integer.                               */
# C context: /*        * only when len>6, memory access can be reduced by half.              */
# C context: opus_int32 silk_inner_prod_aligned(
# C context: const opus_int16 *const     inVec1,             /*    I input vector 1                                              */
# C context: const opus_int16 *const     inVec2,             /*    I input vector 2                                              */
# C context: const opus_int              len,                /*    I vector lengths                                              */
# C context: int                         arch                /*    I Run-time architecture                                       */
silk_inner_prod_aligned:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	blti	a4, 1, .L15	# len,,
	slli	a4, a4, 1	# tmp58, len,
	mov.n	a5, a2	# ivtmp$20, inVec1
	add.n	a7, a2, a4	# _27, ivtmp$20, tmp58
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a2, 0	# <retval>,
.L14:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	l16ui	a4, a5, 0	# MEM[base: _32, offset: 0B],
	l16ui	a6, a3, 0	# MEM[base: _31, offset: 0B],
	addi.n	a5, a5, 2	# ivtmp$20, ivtmp$20,
	mul16s	a4, a4, a6	# tmp59, MEM[base: _32, offset: 0B], MEM[base: _31, offset: 0B]
	addi.n	a3, a3, 2	# ivtmp$21, ivtmp$21,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a2, a2, a4	# <retval>, <retval>, tmp59
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	bne	a7, a5, .L14	# _27, ivtmp$20,
	j	.L12		#
.L15:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a2, 0	# <retval>,
.L12:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:88: }
	ret.n
	.size	silk_inner_prod_aligned, .-silk_inner_prod_aligned
	.section	.text.silk_inner_prod16_c,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_inner_prod16_c
	.type	silk_inner_prod16_c, @function
# Function: silk_inner_prod16_c
# Module: upstream/silk/fixed/vector_ops_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: opus_int64 silk_inner_prod16_c(
# C context: const opus_int16            *inVec1,            /*    I input vector 1                                              */
# C context: const opus_int16            *inVec2,            /*    I input vector 2                                              */
# C context: const opus_int              len                 /*    I vector lengths                                              */
# C context: )
silk_inner_prod16_c:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:98:     for( i = 0; i < len; i++ ) {
	blti	a4, 1, .L21	# len,,
	slli	a4, a4, 1	# tmp59, len,
	mov.n	a6, a2	# ivtmp$25, inVec1
	add.n	a9, a2, a4	# _30, ivtmp$25, tmp59
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:97:     opus_int64 sum = 0;
	movi.n	a2, 0	# <retval>,
	mov.n	a7, a3	# ivtmp$26, inVec2
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:99:         sum = silk_SMLALBB( sum, inVec1[ i ], inVec2[ i ] );
	movi.n	a10, 1	# tmp91,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:97:     opus_int64 sum = 0;
	mov.n	a3, a2	# <retval>, <retval>
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:99:         sum = silk_SMLALBB( sum, inVec1[ i ], inVec2[ i ] );
	mov.n	a11, a2	# tmp92, <retval>
.L20:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:99:         sum = silk_SMLALBB( sum, inVec1[ i ], inVec2[ i ] );
	l16ui	a5, a6, 0	# MEM[base: _35, offset: 0B],
	l16ui	a4, a7, 0	# MEM[base: _34, offset: 0B],
	addi.n	a6, a6, 2	# ivtmp$25, ivtmp$25,
	mul16s	a4, a5, a4	# tmp60, MEM[base: _35, offset: 0B], MEM[base: _34, offset: 0B]
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:99:         sum = silk_SMLALBB( sum, inVec1[ i ], inVec2[ i ] );
	mov.n	a8, a10	# tmp66, tmp91
	add.n	a5, a2, a4	# tmp72, <retval>, tmp60
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:99:         sum = silk_SMLALBB( sum, inVec1[ i ], inVec2[ i ] );
	srai	a4, a4, 31	# tmp71, tmp60,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:99:         sum = silk_SMLALBB( sum, inVec1[ i ], inVec2[ i ] );
	add.n	a4, a3, a4	# tmp73, <retval>, tmp71
	bltu	a5, a2, .L19	# tmp72, <retval>,
	mov.n	a8, a11	# tmp66, tmp92
.L19:
	mov.n	a2, a5	# <retval>, tmp72
	add.n	a3, a8, a4	# <retval>, tmp66, tmp73
	addi.n	a7, a7, 2	# ivtmp$26, ivtmp$26,
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:98:     for( i = 0; i < len; i++ ) {
	bne	a9, a6, .L20	# _30, ivtmp$25,
	j	.L17		#
.L21:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:97:     opus_int64 sum = 0;
	movi.n	a2, 0	# <retval>,
	mov.n	a3, a2	# <retval>, <retval>
.L17:
# @OPUS@\upstream\silk\fixed\vector_ops_FIX.c:102: }
	ret.n
	.size	silk_inner_prod16_c, .-silk_inner_prod16_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
