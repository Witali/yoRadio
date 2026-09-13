# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler_private_AR2.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler_private_AR2.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_AR2.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_AR2.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_AR2.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler_private_AR2.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_AR2.c.s.raw
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
	.section	.text.silk_resampler_private_AR2,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_resampler_private_AR2
	.type	silk_resampler_private_AR2, @function
# Function: silk_resampler_private_AR2
# Module: upstream/silk/resampler_private_AR2.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "resampler_private.h"
# C context:
# C context: /* Second order AR filter with single delay elements */
# C context: void silk_resampler_private_AR2(
# C context: opus_int32                      S[],            /* I/O  State vector [ 2 ]          */
# C context: opus_int32                      out_Q8[],       /* O    Output signal               */
# C context: const opus_int16                in[],           /* I    Input signal                */
# C context: const opus_int16                A_Q14[],        /* I    AR coefficients, Q14        */
silk_resampler_private_AR2:
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 12	#,
# @OPUS@\upstream\silk\resampler_private_AR2.c:47:     for( k = 0; k < len; k++ ) {
	blti	a6, 1, .L1	# len,,
	slli	a6, a6, 1	# tmp82, len,
# @OPUS@\upstream\silk\resampler_private_AR2.c:51:         S[ 0 ]      = silk_SMLAWB( S[ 1 ], out32, A_Q14[ 0 ] );
	l16si	a9, a5, 0	# *A_Q14_39(D), _16
# @OPUS@\upstream\silk\resampler_private_AR2.c:52:         S[ 1 ]      = silk_SMULWB( out32, A_Q14[ 1 ] );
	l16si	a8, a5, 2	# MEM[(const opus_int16 *)A_Q14_39(D) + 2B], _24
	l32i.n	a7, a2, 0	# *S_33(D), _22
	add.n	a6, a4, a6	# _73, ivtmp$5, tmp82
.L3:
# @OPUS@\upstream\silk\resampler_private_AR2.c:48:         out32       = silk_ADD_LSHIFT32( S[ 0 ], (opus_int32)in[ k ], 8 );
	l16si	a5, a4, 0	# MEM[base: _78, offset: 0B], tmp83
	addi.n	a4, a4, 2	# ivtmp$5, ivtmp$5,
	slli	a5, a5, 8	# tmp86, tmp83,
# @OPUS@\upstream\silk\resampler_private_AR2.c:48:         out32       = silk_ADD_LSHIFT32( S[ 0 ], (opus_int32)in[ k ], 8 );
	add.n	a7, a5, a7	# out32, tmp86, _22
# @OPUS@\upstream\silk\resampler_private_AR2.c:50:         out32       = silk_LSHIFT( out32, 2 );
	slli	a5, a7, 2	# _12, out32,
# @OPUS@\upstream\silk\resampler_private_AR2.c:49:         out_Q8[ k ] = out32;
	s32i.n	a7, a3, 0	# MEM[base: _77, offset: 0B], out32
# @OPUS@\upstream\silk\resampler_private_AR2.c:51:         S[ 0 ]      = silk_SMLAWB( S[ 1 ], out32, A_Q14[ 0 ] );
	srai	a11, a5, 16	# _14, _12,
	extui	a5, a5, 0, 16	# _18, _12,
	mull	a7, a11, a9	# tmp87, _14, _16
	mull	a10, a9, a5	# tmp90, _16, _18
	l32i.n	a12, a2, 4	# MEM[(opus_int32 *)S_33(D) + 4B],
# @OPUS@\upstream\silk\resampler_private_AR2.c:52:         S[ 1 ]      = silk_SMULWB( out32, A_Q14[ 1 ] );
	mull	a5, a5, a8	# tmp92, _18, _24
	mull	a11, a11, a8	# tmp94, _14, _24
# @OPUS@\upstream\silk\resampler_private_AR2.c:51:         S[ 0 ]      = silk_SMLAWB( S[ 1 ], out32, A_Q14[ 0 ] );
	add.n	a7, a7, a12	# tmp88, tmp87,
	srai	a10, a10, 16	# tmp91, tmp90,
# @OPUS@\upstream\silk\resampler_private_AR2.c:52:         S[ 1 ]      = silk_SMULWB( out32, A_Q14[ 1 ] );
	srai	a5, a5, 16	# tmp93, tmp92,
# @OPUS@\upstream\silk\resampler_private_AR2.c:51:         S[ 0 ]      = silk_SMLAWB( S[ 1 ], out32, A_Q14[ 0 ] );
	add.n	a7, a7, a10	# _22, tmp88, tmp91
# @OPUS@\upstream\silk\resampler_private_AR2.c:52:         S[ 1 ]      = silk_SMULWB( out32, A_Q14[ 1 ] );
	add.n	a5, a5, a11	# tmp95, tmp93, tmp94
# @OPUS@\upstream\silk\resampler_private_AR2.c:51:         S[ 0 ]      = silk_SMLAWB( S[ 1 ], out32, A_Q14[ 0 ] );
	s32i.n	a7, a2, 0	# *S_33(D), _22
# @OPUS@\upstream\silk\resampler_private_AR2.c:52:         S[ 1 ]      = silk_SMULWB( out32, A_Q14[ 1 ] );
	s32i.n	a5, a2, 4	# MEM[(opus_int32 *)S_33(D) + 4B], tmp95
	addi.n	a3, a3, 4	# ivtmp$6, ivtmp$6,
# @OPUS@\upstream\silk\resampler_private_AR2.c:47:     for( k = 0; k < len; k++ ) {
	bne	a6, a4, .L3	# _73, ivtmp$5,
.L1:
# @OPUS@\upstream\silk\resampler_private_AR2.c:54: }
	l32i.n	a12, sp, 12	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_resampler_private_AR2, .-silk_resampler_private_AR2
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
