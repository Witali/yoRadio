# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/biquad_alt.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"biquad_alt.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\biquad_alt.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\biquad_alt.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\biquad_alt.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\biquad_alt.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\biquad_alt.c.s.raw
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
	.section	.text.silk_biquad_alt_stride1,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, 16383
	.align	4
	.global	silk_biquad_alt_stride1
	.type	silk_biquad_alt_stride1, @function
# Function: silk_biquad_alt_stride1
# Module: upstream/silk/biquad_alt.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "SigProc_FIX.h"
# C context:
# C context: /* Second order ARMA filter, alternative implementation */
# C context: void silk_biquad_alt_stride1(
# C context: const opus_int16            *in,                /* I     input signal                                               */
# C context: const opus_int32            *B_Q28,             /* I     MA coefficients [3]                                        */
# C context: const opus_int32            *A_Q28,             /* I     AR coefficients [2]                                        */
# C context: opus_int32                  *S,                 /* I/O   State vector [2]                                           */
silk_biquad_alt_stride1:
# @OPUS@\upstream\silk\biquad_alt.c:56:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	l32i.n	a8, a4, 0	# *A_Q28_79(D), *A_Q28_79(D)
# @OPUS@\upstream\silk\biquad_alt.c:58:     A1_L_Q28 = ( -A_Q28[ 1 ] ) & 0x00003FFF;        /* lower part */
	l32i.n	a4, a4, 4	# MEM[(const opus_int32 *)A_Q28_79(D) + 4B], MEM[(const opus_int32 *)A_Q28_79(D) + 4B]
# @OPUS@\upstream\silk\biquad_alt.c:56:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	neg	a8, a8	# _2, *A_Q28_79(D)
# @OPUS@\upstream\silk\biquad_alt.c:50: {
	addi	sp, sp, -48	#,,
# @OPUS@\upstream\silk\biquad_alt.c:56:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	extui	a9, a8, 0, 14	#, _2,
# @OPUS@\upstream\silk\biquad_alt.c:58:     A1_L_Q28 = ( -A_Q28[ 1 ] ) & 0x00003FFF;        /* lower part */
	neg	a4, a4	# _4, MEM[(const opus_int32 *)A_Q28_79(D) + 4B]
# @OPUS@\upstream\silk\biquad_alt.c:50: {
	s32i.n	a14, sp, 36	#,
	s32i.n	a12, sp, 44	#,
	s32i.n	a13, sp, 40	#,
	s32i.n	a15, sp, 32	#,
# @OPUS@\upstream\silk\biquad_alt.c:56:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	s32i.n	a9, sp, 0	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:58:     A1_L_Q28 = ( -A_Q28[ 1 ] ) & 0x00003FFF;        /* lower part */
	extui	a14, a4, 0, 14	# A1_L_Q28, _4,
# @OPUS@\upstream\silk\biquad_alt.c:57:     A0_U_Q28 = silk_RSHIFT( -A_Q28[ 0 ], 14 );      /* upper part */
	srai	a8, a8, 14	# A0_U_Q28, _2,
# @OPUS@\upstream\silk\biquad_alt.c:59:     A1_U_Q28 = silk_RSHIFT( -A_Q28[ 1 ], 14 );      /* upper part */
	srai	a4, a4, 14	# A1_U_Q28, _4,
# @OPUS@\upstream\silk\biquad_alt.c:61:     for( k = 0; k < len; k++ ) {
	blti	a7, 1, .L1	# len,,
	slli	a8, a8, 16	# tmp128, A0_U_Q28,
	slli	a4, a4, 16	# tmp129, A1_U_Q28,
	slli	a7, a7, 1	# tmp130, len,
	srai	a8, a8, 16	#, tmp128,
	srai	a4, a4, 16	#, tmp129,
	add.n	a7, a2, a7	#, ivtmp$12, tmp130
	l32i.n	a13, a5, 0	# *S_87(D), _137
	l32i.n	a9, a5, 4	# MEM[(opus_int32 *)S_87(D) + 4B], _115
	s32i.n	a8, sp, 4	# %sfp,
	s32i.n	a4, sp, 8	# %sfp,
	s32i.n	a7, sp, 12	# %sfp,
.L4:
# @OPUS@\upstream\silk\biquad_alt.c:64:         out32_Q14 = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], inval ), 2 );
	l32i.n	a7, a3, 0	# *B_Q28_88(D), _171
# @OPUS@\upstream\silk\biquad_alt.c:63:         inval = in[ k ];
	l16si	a11, a2, 0	# MEM[base: _6, offset: 0B], inval
# @OPUS@\upstream\silk\biquad_alt.c:64:         out32_Q14 = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], inval ), 2 );
	extui	a4, a7, 0, 16	# tmp133, _171,
	mull	a4, a4, a11	# tmp134, tmp133, inval
	srai	a7, a7, 16	# tmp136, _171,
	mull	a7, a7, a11	# tmp137, tmp136, inval
	srai	a4, a4, 16	# tmp135, tmp134,
	add.n	a4, a4, a7	# tmp138, tmp135, tmp137
	add.n	a13, a4, a13	# tmp139, tmp138, _137
	slli	a4, a13, 2	# out32_Q14, tmp139,
# @OPUS@\upstream\silk\biquad_alt.c:66:         S[ 0 ] = S[1] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A0_L_Q28 ), 14 );
	l32i.n	a13, sp, 0	# %sfp,
	extui	a8, a4, 0, 16	# _158, out32_Q14,
	srai	a12, a4, 16	# _160, out32_Q14,
	mull	a10, a13, a8	# tmp140,, _158
	mull	a7, a13, a12	# tmp142,, _160
	srai	a10, a10, 16	# tmp141, tmp140,
	add.n	a10, a10, a7	# tmp143, tmp141, tmp142
# @OPUS@\upstream\silk\biquad_alt.c:67:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14, A0_U_Q28 );
	l32i.n	a7, sp, 4	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:66:         S[ 0 ] = S[1] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A0_L_Q28 ), 14 );
	srai	a10, a10, 13	# tmp144, tmp143,
# @OPUS@\upstream\silk\biquad_alt.c:67:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14, A0_U_Q28 );
	mull	a13, a8, a7	# tmp147, _158,
	mull	a15, a12, a7	# tmp149, _160,
# @OPUS@\upstream\silk\biquad_alt.c:66:         S[ 0 ] = S[1] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A0_L_Q28 ), 14 );
	addi.n	a10, a10, 1	# tmp145, tmp144,
# @OPUS@\upstream\silk\biquad_alt.c:67:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14, A0_U_Q28 );
	srai	a13, a13, 16	# tmp148, tmp147,
# @OPUS@\upstream\silk\biquad_alt.c:66:         S[ 0 ] = S[1] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A0_L_Q28 ), 14 );
	srai	a10, a10, 1	# tmp146, tmp145,
# @OPUS@\upstream\silk\biquad_alt.c:67:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14, A0_U_Q28 );
	add.n	a13, a13, a15	# tmp150, tmp148, tmp149
	add.n	a13, a10, a13	# tmp151, tmp146, tmp150
	add.n	a7, a13, a9	# _146, tmp151, _115
# @OPUS@\upstream\silk\biquad_alt.c:67:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14, A0_U_Q28 );
	s32i.n	a7, a5, 0	# *S_87(D), _146
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	l32i.n	a13, a3, 4	# MEM[(const opus_int32 *)B_Q28_88(D) + 4B], _144
# @OPUS@\upstream\silk\biquad_alt.c:70:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A1_L_Q28 ), 14 );
	mull	a9, a14, a8	# tmp158, A1_L_Q28, _158
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	extui	a10, a13, 0, 16	# tmp152, _144,
	mull	a10, a10, a11	#, tmp152, inval
# @OPUS@\upstream\silk\biquad_alt.c:70:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A1_L_Q28 ), 14 );
	mull	a15, a14, a12	# tmp160, A1_L_Q28, _160
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	s32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:71:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14, A1_U_Q28 );
	l32i.n	a10, sp, 8	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:70:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A1_L_Q28 ), 14 );
	srai	a9, a9, 16	# tmp159, tmp158,
	add.n	a9, a9, a15	# tmp161, tmp159, tmp160
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	srai	a13, a13, 16	# tmp155, _144,
# @OPUS@\upstream\silk\biquad_alt.c:71:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14, A1_U_Q28 );
	mull	a15, a8, a10	# tmp165, _158,
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	l32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:71:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14, A1_U_Q28 );
	mull	a12, a12, a10	# tmp167, _160,
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	mull	a13, a13, a11	# tmp156, tmp155, inval
# @OPUS@\upstream\silk\biquad_alt.c:70:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A1_L_Q28 ), 14 );
	srai	a9, a9, 13	# tmp162, tmp161,
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	srai	a10, a8, 16	# tmp154,,
# @OPUS@\upstream\silk\biquad_alt.c:70:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A1_L_Q28 ), 14 );
	addi.n	a9, a9, 1	# tmp163, tmp162,
# @OPUS@\upstream\silk\biquad_alt.c:71:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14, A1_U_Q28 );
	srai	a8, a15, 16	# tmp166, tmp165,
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	add.n	a13, a10, a13	# tmp157, tmp154, tmp156
# @OPUS@\upstream\silk\biquad_alt.c:71:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14, A1_U_Q28 );
	add.n	a8, a8, a12	# tmp168, tmp166, tmp167
# @OPUS@\upstream\silk\biquad_alt.c:70:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14, A1_L_Q28 ), 14 );
	srai	a9, a9, 1	# tmp164, tmp163,
# @OPUS@\upstream\silk\biquad_alt.c:71:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14, A1_U_Q28 );
	add.n	a9, a9, a8	# _124, tmp164, tmp168
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	add.n	a13, a13, a7	# _137, tmp157, _146
# @OPUS@\upstream\silk\biquad_alt.c:71:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14, A1_U_Q28 );
	s32i.n	a9, a5, 4	# MEM[(opus_int32 *)S_87(D) + 4B], _124
# @OPUS@\upstream\silk\biquad_alt.c:68:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], inval);
	s32i.n	a13, a5, 0	# *S_87(D), _137
# @OPUS@\upstream\silk\biquad_alt.c:72:         S[ 1 ] = silk_SMLAWB( S[ 1 ], B_Q28[ 2 ], inval );
	l32i.n	a8, a3, 8	# MEM[(const opus_int32 *)B_Q28_88(D) + 8B], _122
# @OPUS@\upstream\silk\biquad_alt.c:75:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14 + (1<<14) - 1, 14 ) );
	l32r	a10, .LC2	#,
	addi.n	a2, a2, 2	# ivtmp$12, ivtmp$12,
	add.n	a4, a4, a10	# tmp175, out32_Q14,
# @OPUS@\upstream\silk\biquad_alt.c:72:         S[ 1 ] = silk_SMLAWB( S[ 1 ], B_Q28[ 2 ], inval );
	extui	a10, a8, 0, 16	# tmp169, _122,
	mull	a10, a10, a11	# tmp170, tmp169, inval
	srai	a8, a8, 16	# tmp172, _122,
	mull	a8, a8, a11	# tmp173, tmp172, inval
	srai	a7, a10, 16	# tmp171, tmp170,
	add.n	a7, a7, a8	# tmp174, tmp171, tmp173
	add.n	a9, a7, a9	# _115, tmp174, _124
# @OPUS@\upstream\silk\biquad_alt.c:75:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14 + (1<<14) - 1, 14 ) );
	l32r	a7, .LC0	#, iftmp$1_110
# @OPUS@\upstream\silk\biquad_alt.c:72:         S[ 1 ] = silk_SMLAWB( S[ 1 ], B_Q28[ 2 ], inval );
	s32i.n	a9, a5, 4	# MEM[(opus_int32 *)S_87(D) + 4B], _115
# @OPUS@\upstream\silk\biquad_alt.c:75:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14 + (1<<14) - 1, 14 ) );
	srai	a4, a4, 14	# _112, tmp175,
# @OPUS@\upstream\silk\biquad_alt.c:75:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14 + (1<<14) - 1, 14 ) );
	blt	a7, a4, .L3	# tmp8, _112,
	l32r	a7, .LC1	#, iftmp$1_110
	slli	a8, a4, 16	# tmp179, _112,
	blt	a4, a7, .L3	# _112, tmp10,
	srai	a7, a8, 16	# iftmp$1_110, tmp179,
.L3:
# @OPUS@\upstream\silk\biquad_alt.c:61:     for( k = 0; k < len; k++ ) {
	l32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:75:         out[ k ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14 + (1<<14) - 1, 14 ) );
	s16i	a7, a6, 0	# MEM[base: _7, offset: 0B], iftmp$1_110
	addi.n	a6, a6, 2	# ivtmp$13, ivtmp$13,
# @OPUS@\upstream\silk\biquad_alt.c:61:     for( k = 0; k < len; k++ ) {
	bne	a4, a2, .L4	#, ivtmp$12,
.L1:
# @OPUS@\upstream\silk\biquad_alt.c:77: }
	l32i.n	a12, sp, 44	#,
	l32i.n	a13, sp, 40	#,
	l32i.n	a14, sp, 36	#,
	l32i.n	a15, sp, 32	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_biquad_alt_stride1, .-silk_biquad_alt_stride1
	.section	.text.silk_biquad_alt_stride2_c,"ax",@progbits
	.literal_position
	.literal .LC3, 32767
	.literal .LC4, -32768
	.literal .LC5, 16383
	.align	4
	.global	silk_biquad_alt_stride2_c
	.type	silk_biquad_alt_stride2_c, @function
# Function: silk_biquad_alt_stride2_c
# Module: upstream/silk/biquad_alt.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void silk_biquad_alt_stride2_c(
# C context: const opus_int16            *in,                /* I     input signal                                               */
# C context: const opus_int32            *B_Q28,             /* I     MA coefficients [3]                                        */
# C context: const opus_int32            *A_Q28,             /* I     AR coefficients [2]                                        */
# C context: opus_int32                  *S,                 /* I/O   State vector [4]                                           */
silk_biquad_alt_stride2_c:
# @OPUS@\upstream\silk\biquad_alt.c:93:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	l32i.n	a9, a4, 0	# *A_Q28_142(D), *A_Q28_142(D)
# @OPUS@\upstream\silk\biquad_alt.c:95:     A1_L_Q28 = ( -A_Q28[ 1 ] ) & 0x00003FFF;        /* lower part */
	l32i.n	a8, a4, 4	# MEM[(const opus_int32 *)A_Q28_142(D) + 4B], MEM[(const opus_int32 *)A_Q28_142(D) + 4B]
# @OPUS@\upstream\silk\biquad_alt.c:87: {
	addi	sp, sp, -80	#,,
# @OPUS@\upstream\silk\biquad_alt.c:93:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	neg	a4, a9	# _2, *A_Q28_142(D)
# @OPUS@\upstream\silk\biquad_alt.c:95:     A1_L_Q28 = ( -A_Q28[ 1 ] ) & 0x00003FFF;        /* lower part */
	neg	a8, a8	# _4, MEM[(const opus_int32 *)A_Q28_142(D) + 4B]
# @OPUS@\upstream\silk\biquad_alt.c:87: {
	s32i	a15, sp, 64	#,
	mov.n	a9, a3	# B_Q28, B_Q28
	mov.n	a15, a5	# S, S
# @OPUS@\upstream\silk\biquad_alt.c:93:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	extui	a3, a4, 0, 14	#, _2,
# @OPUS@\upstream\silk\biquad_alt.c:95:     A1_L_Q28 = ( -A_Q28[ 1 ] ) & 0x00003FFF;        /* lower part */
	extui	a5, a8, 0, 14	#, _4,
# @OPUS@\upstream\silk\biquad_alt.c:93:     A0_L_Q28 = ( -A_Q28[ 0 ] ) & 0x00003FFF;        /* lower part */
	s32i.n	a3, sp, 8	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:87: {
	s32i	a12, sp, 76	#,
	s32i	a13, sp, 72	#,
	s32i	a14, sp, 68	#,
# @OPUS@\upstream\silk\biquad_alt.c:95:     A1_L_Q28 = ( -A_Q28[ 1 ] ) & 0x00003FFF;        /* lower part */
	s32i.n	a5, sp, 12	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:94:     A0_U_Q28 = silk_RSHIFT( -A_Q28[ 0 ], 14 );      /* upper part */
	srai	a4, a4, 14	# A0_U_Q28, _2,
# @OPUS@\upstream\silk\biquad_alt.c:96:     A1_U_Q28 = silk_RSHIFT( -A_Q28[ 1 ], 14 );      /* upper part */
	srai	a3, a8, 14	# A1_U_Q28, _4,
# @OPUS@\upstream\silk\biquad_alt.c:98:     for( k = 0; k < len; k++ ) {
	blti	a7, 1, .L10	# len,,
	slli	a3, a3, 16	# tmp185, A1_U_Q28,
	s32i.n	a2, sp, 0	# %sfp, in
	srai	a3, a3, 16	#, tmp185,
	s32i.n	a3, sp, 24	# %sfp,
	l32i.n	a3, sp, 0	# %sfp,
	l32i.n	a11, a15, 4	# MEM[(opus_int32 *)S_148(D) + 4B],
	slli	a4, a4, 16	# tmp184, A0_U_Q28,
	slli	a7, a7, 2	# tmp186, len,
	l32i.n	a5, a15, 0	# *S_148(D), _253
	srai	a4, a4, 16	#, tmp184,
	add.n	a7, a3, a7	#,, tmp186
	l32i.n	a13, a15, 8	# MEM[(opus_int32 *)S_148(D) + 8B], _244
	l32i.n	a2, a15, 12	# MEM[(opus_int32 *)S_148(D) + 12B], _200
# @OPUS@\upstream\silk\biquad_alt.c:119:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 1 ] + (1<<14) - 1, 14 ) );
	mov.n	a14, a15	# S, S
	s32i.n	a11, sp, 4	# %sfp,
	s32i.n	a4, sp, 20	# %sfp,
	s32i.n	a6, sp, 16	# %sfp, out
	s32i.n	a7, sp, 40	# %sfp,
	mov.n	a15, a5	# _253, _253
.L14:
# @OPUS@\upstream\silk\biquad_alt.c:100:         out32_Q14[ 0 ] = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], in[ 2 * k + 0 ] ), 2 );
	l32i.n	a5, sp, 0	# %sfp,
	l32i.n	a4, a9, 0	# *B_Q28_149(D), _320
# @OPUS@\upstream\silk\biquad_alt.c:101:         out32_Q14[ 1 ] = silk_LSHIFT( silk_SMLAWB( S[ 2 ], B_Q28[ 0 ], in[ 2 * k + 1 ] ), 2 );
	l16si	a8, a5, 2	# MEM[base: _37, offset: 2B], _301
# @OPUS@\upstream\silk\biquad_alt.c:100:         out32_Q14[ 0 ] = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], in[ 2 * k + 0 ] ), 2 );
	l16si	a10, a5, 0	# MEM[base: _37, offset: 0B], _314
	extui	a3, a4, 0, 16	# _312, _320,
	mull	a5, a3, a10	# tmp189, _312, _314
	srai	a4, a4, 16	# _319, _320,
# @OPUS@\upstream\silk\biquad_alt.c:101:         out32_Q14[ 1 ] = silk_LSHIFT( silk_SMLAWB( S[ 2 ], B_Q28[ 0 ], in[ 2 * k + 1 ] ), 2 );
	mull	a3, a8, a3	# tmp196, _301, _312
# @OPUS@\upstream\silk\biquad_alt.c:100:         out32_Q14[ 0 ] = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], in[ 2 * k + 0 ] ), 2 );
	mull	a6, a10, a4	# tmp191, _314, _319
# @OPUS@\upstream\silk\biquad_alt.c:101:         out32_Q14[ 1 ] = silk_LSHIFT( silk_SMLAWB( S[ 2 ], B_Q28[ 0 ], in[ 2 * k + 1 ] ), 2 );
	mull	a4, a8, a4	# tmp198, _301, _319
# @OPUS@\upstream\silk\biquad_alt.c:100:         out32_Q14[ 0 ] = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], in[ 2 * k + 0 ] ), 2 );
	srai	a5, a5, 16	# tmp190, tmp189,
# @OPUS@\upstream\silk\biquad_alt.c:101:         out32_Q14[ 1 ] = silk_LSHIFT( silk_SMLAWB( S[ 2 ], B_Q28[ 0 ], in[ 2 * k + 1 ] ), 2 );
	srai	a3, a3, 16	# tmp197, tmp196,
	add.n	a3, a3, a4	# tmp199, tmp197, tmp198
# @OPUS@\upstream\silk\biquad_alt.c:100:         out32_Q14[ 0 ] = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], in[ 2 * k + 0 ] ), 2 );
	add.n	a5, a5, a6	# tmp192, tmp190, tmp191
	add.n	a5, a5, a15	# tmp193, tmp192, _253
# @OPUS@\upstream\silk\biquad_alt.c:101:         out32_Q14[ 1 ] = silk_LSHIFT( silk_SMLAWB( S[ 2 ], B_Q28[ 0 ], in[ 2 * k + 1 ] ), 2 );
	add.n	a13, a3, a13	# tmp200, tmp199, _244
# @OPUS@\upstream\silk\biquad_alt.c:100:         out32_Q14[ 0 ] = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], in[ 2 * k + 0 ] ), 2 );
	slli	a5, a5, 2	#, tmp193,
# @OPUS@\upstream\silk\biquad_alt.c:101:         out32_Q14[ 1 ] = silk_LSHIFT( silk_SMLAWB( S[ 2 ], B_Q28[ 0 ], in[ 2 * k + 1 ] ), 2 );
	slli	a13, a13, 2	#, tmp200,
# @OPUS@\upstream\silk\biquad_alt.c:103:         S[ 0 ] = S[ 1 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A0_L_Q28 ), 14 );
	l32i.n	a7, sp, 8	# %sfp,
	extui	a4, a5, 0, 16	# _290,,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	extui	a3, a13, 0, 16	# _281,,
	srai	a11, a13, 16	# _283,,
# @OPUS@\upstream\silk\biquad_alt.c:101:         out32_Q14[ 1 ] = silk_LSHIFT( silk_SMLAWB( S[ 2 ], B_Q28[ 0 ], in[ 2 * k + 1 ] ), 2 );
	s32i.n	a13, sp, 28	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	l32i.n	a13, sp, 8	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:103:         S[ 0 ] = S[ 1 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A0_L_Q28 ), 14 );
	srai	a12, a5, 16	# _292,,
	mull	a6, a7, a4	# tmp201,, _290
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	mull	a15, a13, a11	# tmp215,, _283
# @OPUS@\upstream\silk\biquad_alt.c:100:         out32_Q14[ 0 ] = silk_LSHIFT( silk_SMLAWB( S[ 0 ], B_Q28[ 0 ], in[ 2 * k + 0 ] ), 2 );
	s32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	l32i.n	a13, sp, 20	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	mull	a5, a7, a3	# tmp213,, _281
# @OPUS@\upstream\silk\biquad_alt.c:103:         S[ 0 ] = S[ 1 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A0_L_Q28 ), 14 );
	mull	a7, a7, a12	# tmp203,, _292
	srai	a6, a6, 16	# tmp202, tmp201,
	add.n	a6, a6, a7	# tmp204, tmp202, tmp203
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	mull	a7, a4, a13	# tmp208, _290,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	mull	a13, a3, a13	#, _281,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	srai	a5, a5, 16	# tmp214, tmp213,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	s32i.n	a13, sp, 44	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	l32i.n	a13, sp, 20	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	add.n	a5, a5, a15	# tmp216, tmp214, tmp215
# @OPUS@\upstream\silk\biquad_alt.c:103:         S[ 0 ] = S[ 1 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A0_L_Q28 ), 14 );
	srai	a6, a6, 13	# tmp205, tmp204,
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	mull	a15, a12, a13	# tmp210, _292,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	mull	a13, a11, a13	#, _283,
# @OPUS@\upstream\silk\biquad_alt.c:103:         S[ 0 ] = S[ 1 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A0_L_Q28 ), 14 );
	addi.n	a6, a6, 1	# tmp206, tmp205,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	s32i.n	a13, sp, 36	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:103:         S[ 0 ] = S[ 1 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A0_L_Q28 ), 14 );
	srai	a6, a6, 1	#, tmp206,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	l32i.n	a13, sp, 44	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	srai	a5, a5, 13	# tmp217, tmp216,
# @OPUS@\upstream\silk\biquad_alt.c:103:         S[ 0 ] = S[ 1 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A0_L_Q28 ), 14 );
	s32i.n	a6, sp, 44	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	l32i.n	a6, sp, 36	# %sfp,
	srai	a13, a13, 16	#,,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	addi.n	a5, a5, 1	# tmp218, tmp217,
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	srai	a7, a7, 16	# tmp209, tmp208,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	s32i.n	a13, sp, 48	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:104:         S[ 2 ] = S[ 3 ] + silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A0_L_Q28 ), 14 );
	srai	a5, a5, 1	# tmp219, tmp218,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	add.n	a13, a13, a6	# tmp223,,
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	l32i.n	a6, sp, 44	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	add.n	a5, a5, a13	# tmp224, tmp219, tmp223
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	add.n	a15, a7, a15	# tmp211, tmp209, tmp210
	l32i.n	a13, sp, 4	# %sfp,
	add.n	a7, a6, a15	# tmp212,, tmp211
	add.n	a7, a7, a13	# _269, tmp212,
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	add.n	a2, a5, a2	# _262, tmp224, _200
# @OPUS@\upstream\silk\biquad_alt.c:105:         S[ 0 ] = silk_SMLAWB( S[ 0 ], out32_Q14[ 0 ], A0_U_Q28 );
	s32i.n	a7, a14, 0	# *S_148(D), _269
# @OPUS@\upstream\silk\biquad_alt.c:106:         S[ 2 ] = silk_SMLAWB( S[ 2 ], out32_Q14[ 1 ], A0_U_Q28 );
	s32i.n	a2, a14, 8	# MEM[(opus_int32 *)S_148(D) + 8B], _262
# @OPUS@\upstream\silk\biquad_alt.c:107:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], in[ 2 * k + 0 ] );
	l32i.n	a13, a9, 4	# MEM[(const opus_int32 *)B_Q28_149(D) + 4B], _260
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	l32i.n	a5, sp, 12	# %sfp,
	mull	a6, a5, a4	# tmp237,, _290
# @OPUS@\upstream\silk\biquad_alt.c:107:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], in[ 2 * k + 0 ] );
	extui	a5, a13, 0, 16	# tmp225, _260,
	mull	a5, a5, a10	# tmp226, tmp225, _314
	srai	a13, a13, 16	# tmp228, _260,
	mull	a13, a13, a10	# tmp229, tmp228, _314
	srai	a5, a5, 16	# tmp227, tmp226,
	add.n	a5, a5, a13	# tmp230, tmp227, tmp229
	add.n	a15, a5, a7	# _253, tmp230, _269
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	l32i.n	a7, sp, 12	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:107:         S[ 0 ] = silk_SMLAWB( S[ 0 ], B_Q28[ 1 ], in[ 2 * k + 0 ] );
	s32i.n	a15, a14, 0	# *S_148(D), _253
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	mull	a5, a7, a3	# tmp248,, _281
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	mull	a7, a7, a12	#,, _292
# @OPUS@\upstream\silk\biquad_alt.c:108:         S[ 2 ] = silk_SMLAWB( S[ 2 ], B_Q28[ 1 ], in[ 2 * k + 1 ] );
	l32i.n	a13, a9, 4	# MEM[(const opus_int32 *)B_Q28_149(D) + 4B], _251
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	s32i.n	a7, sp, 4	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	l32i.n	a7, sp, 12	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	srai	a6, a6, 16	# tmp238, tmp237,
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	mull	a7, a7, a11	#,, _283
	srai	a5, a5, 16	# tmp249, tmp248,
	s32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:108:         S[ 2 ] = silk_SMLAWB( S[ 2 ], B_Q28[ 1 ], in[ 2 * k + 1 ] );
	extui	a7, a13, 0, 16	# tmp231, _251,
	mull	a7, a7, a8	#, tmp231, _301
	srai	a13, a13, 16	# tmp234, _251,
	s32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	l32i.n	a7, sp, 4	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:108:         S[ 2 ] = silk_SMLAWB( S[ 2 ], B_Q28[ 1 ], in[ 2 * k + 1 ] );
	mull	a13, a13, a8	# tmp235, tmp234, _301
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	add.n	a6, a6, a7	# tmp240, tmp238,
# @OPUS@\upstream\silk\biquad_alt.c:112:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14[ 0 ], A1_U_Q28 );
	l32i.n	a7, sp, 24	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	srai	a6, a6, 13	# tmp241, tmp240,
# @OPUS@\upstream\silk\biquad_alt.c:112:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14[ 0 ], A1_U_Q28 );
	mull	a4, a4, a7	# tmp244, _290,
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	l32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	addi.n	a6, a6, 1	# tmp242, tmp241,
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	add.n	a5, a5, a7	# tmp251, tmp249,
# @OPUS@\upstream\silk\biquad_alt.c:113:         S[ 3 ] = silk_SMLAWB( S[ 3 ], out32_Q14[ 1 ], A1_U_Q28 );
	l32i.n	a7, sp, 24	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	srai	a5, a5, 13	# tmp252, tmp251,
# @OPUS@\upstream\silk\biquad_alt.c:113:         S[ 3 ] = silk_SMLAWB( S[ 3 ], out32_Q14[ 1 ], A1_U_Q28 );
	mull	a11, a11, a7	#, _283,
	mull	a3, a3, a7	# tmp255, _281,
	s32i.n	a11, sp, 4	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:108:         S[ 2 ] = silk_SMLAWB( S[ 2 ], B_Q28[ 1 ], in[ 2 * k + 1 ] );
	l32i.n	a11, sp, 44	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:112:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14[ 0 ], A1_U_Q28 );
	mull	a12, a12, a7	# tmp246, _292,
# @OPUS@\upstream\silk\biquad_alt.c:108:         S[ 2 ] = silk_SMLAWB( S[ 2 ], B_Q28[ 1 ], in[ 2 * k + 1 ] );
	srai	a7, a11, 16	# tmp233,,
	add.n	a13, a7, a13	# tmp236, tmp233, tmp235
# @OPUS@\upstream\silk\biquad_alt.c:113:         S[ 3 ] = silk_SMLAWB( S[ 3 ], out32_Q14[ 1 ], A1_U_Q28 );
	l32i.n	a7, sp, 4	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:112:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14[ 0 ], A1_U_Q28 );
	srai	a4, a4, 16	# tmp245, tmp244,
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	addi.n	a5, a5, 1	# tmp253, tmp252,
# @OPUS@\upstream\silk\biquad_alt.c:113:         S[ 3 ] = silk_SMLAWB( S[ 3 ], out32_Q14[ 1 ], A1_U_Q28 );
	srai	a3, a3, 16	# tmp256, tmp255,
# @OPUS@\upstream\silk\biquad_alt.c:112:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14[ 0 ], A1_U_Q28 );
	add.n	a4, a4, a12	# tmp247, tmp245, tmp246
# @OPUS@\upstream\silk\biquad_alt.c:113:         S[ 3 ] = silk_SMLAWB( S[ 3 ], out32_Q14[ 1 ], A1_U_Q28 );
	add.n	a3, a3, a7	# tmp258, tmp256,
# @OPUS@\upstream\silk\biquad_alt.c:110:         S[ 1 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 0 ], A1_L_Q28 ), 14 );
	srai	a6, a6, 1	# tmp243, tmp242,
# @OPUS@\upstream\silk\biquad_alt.c:111:         S[ 3 ] = silk_RSHIFT_ROUND( silk_SMULWB( out32_Q14[ 1 ], A1_L_Q28 ), 14 );
	srai	a5, a5, 1	# tmp254, tmp253,
# @OPUS@\upstream\silk\biquad_alt.c:112:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14[ 0 ], A1_U_Q28 );
	add.n	a6, a6, a4	# _224, tmp243, tmp247
# @OPUS@\upstream\silk\biquad_alt.c:113:         S[ 3 ] = silk_SMLAWB( S[ 3 ], out32_Q14[ 1 ], A1_U_Q28 );
	add.n	a5, a5, a3	# _218, tmp254, tmp258
# @OPUS@\upstream\silk\biquad_alt.c:108:         S[ 2 ] = silk_SMLAWB( S[ 2 ], B_Q28[ 1 ], in[ 2 * k + 1 ] );
	add.n	a13, a13, a2	# _244, tmp236, _262
# @OPUS@\upstream\silk\biquad_alt.c:112:         S[ 1 ] = silk_SMLAWB( S[ 1 ], out32_Q14[ 0 ], A1_U_Q28 );
	s32i.n	a6, a14, 4	# MEM[(opus_int32 *)S_148(D) + 4B], _224
# @OPUS@\upstream\silk\biquad_alt.c:113:         S[ 3 ] = silk_SMLAWB( S[ 3 ], out32_Q14[ 1 ], A1_U_Q28 );
	s32i.n	a5, a14, 12	# MEM[(opus_int32 *)S_148(D) + 12B], _218
# @OPUS@\upstream\silk\biquad_alt.c:108:         S[ 2 ] = silk_SMLAWB( S[ 2 ], B_Q28[ 1 ], in[ 2 * k + 1 ] );
	s32i.n	a13, a14, 8	# MEM[(opus_int32 *)S_148(D) + 8B], _244
# @OPUS@\upstream\silk\biquad_alt.c:114:         S[ 1 ] = silk_SMLAWB( S[ 1 ], B_Q28[ 2 ], in[ 2 * k + 0 ] );
	l32i.n	a2, a9, 8	# MEM[(const opus_int32 *)B_Q28_149(D) + 8B], _216
# @OPUS@\upstream\silk\biquad_alt.c:118:         out[ 2 * k + 0 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 0 ] + (1<<14) - 1, 14 ) );
	l32r	a4, .LC5	#,
	l32i.n	a11, sp, 32	# %sfp,
	add.n	a3, a11, a4	# tmp271,,
# @OPUS@\upstream\silk\biquad_alt.c:114:         S[ 1 ] = silk_SMLAWB( S[ 1 ], B_Q28[ 2 ], in[ 2 * k + 0 ] );
	extui	a4, a2, 0, 16	# tmp259, _216,
	mull	a4, a4, a10	# tmp260, tmp259, _314
	srai	a2, a2, 16	# tmp262, _216,
	mull	a2, a2, a10	# tmp263, tmp262, _314
	srai	a4, a4, 16	# tmp261, tmp260,
	add.n	a2, a4, a2	# tmp264, tmp261, tmp263
	add.n	a2, a2, a6	#, tmp264, _224
# @OPUS@\upstream\silk\biquad_alt.c:114:         S[ 1 ] = silk_SMLAWB( S[ 1 ], B_Q28[ 2 ], in[ 2 * k + 0 ] );
	s32i.n	a2, a14, 4	# MEM[(opus_int32 *)S_148(D) + 4B],
# @OPUS@\upstream\silk\biquad_alt.c:115:         S[ 3 ] = silk_SMLAWB( S[ 3 ], B_Q28[ 2 ], in[ 2 * k + 1 ] );
	l32i.n	a4, a9, 8	# MEM[(const opus_int32 *)B_Q28_149(D) + 8B], _207
# @OPUS@\upstream\silk\biquad_alt.c:114:         S[ 1 ] = silk_SMLAWB( S[ 1 ], B_Q28[ 2 ], in[ 2 * k + 0 ] );
	s32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:115:         S[ 3 ] = silk_SMLAWB( S[ 3 ], B_Q28[ 2 ], in[ 2 * k + 1 ] );
	extui	a6, a4, 0, 16	# tmp265, _207,
	mull	a6, a6, a8	# tmp266, tmp265, _301
	srai	a4, a4, 16	# tmp268, _207,
	mull	a4, a4, a8	# tmp269, tmp268, _301
	srai	a6, a6, 16	# tmp267, tmp266,
	add.n	a2, a6, a4	# tmp270, tmp267, tmp269
	add.n	a2, a2, a5	# _200, tmp270, _218
# @OPUS@\upstream\silk\biquad_alt.c:118:         out[ 2 * k + 0 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 0 ] + (1<<14) - 1, 14 ) );
	l32r	a4, .LC3	#, iftmp$4_195
# @OPUS@\upstream\silk\biquad_alt.c:118:         out[ 2 * k + 0 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 0 ] + (1<<14) - 1, 14 ) );
	srai	a3, a3, 14	# _197, tmp271,
# @OPUS@\upstream\silk\biquad_alt.c:115:         S[ 3 ] = silk_SMLAWB( S[ 3 ], B_Q28[ 2 ], in[ 2 * k + 1 ] );
	s32i.n	a2, a14, 12	# MEM[(opus_int32 *)S_148(D) + 12B], _200
# @OPUS@\upstream\silk\biquad_alt.c:118:         out[ 2 * k + 0 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 0 ] + (1<<14) - 1, 14 ) );
	blt	a4, a3, .L12	# tmp5, _197,
	l32r	a4, .LC4	#, iftmp$4_195
	blt	a3, a4, .L12	# _197, tmp6,
	slli	a3, a3, 16	# tmp275, _197,
	srai	a4, a3, 16	# iftmp$4_195, tmp275,
.L12:
# @OPUS@\upstream\silk\biquad_alt.c:119:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 1 ] + (1<<14) - 1, 14 ) );
	l32i.n	a7, sp, 28	# %sfp,
	l32r	a11, .LC5	#,
# @OPUS@\upstream\silk\biquad_alt.c:118:         out[ 2 * k + 0 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 0 ] + (1<<14) - 1, 14 ) );
	l32i.n	a5, sp, 16	# %sfp,
# @OPUS@\upstream\silk\biquad_alt.c:119:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 1 ] + (1<<14) - 1, 14 ) );
	add.n	a3, a7, a11	# tmp276,,
# @OPUS@\upstream\silk\biquad_alt.c:118:         out[ 2 * k + 0 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 0 ] + (1<<14) - 1, 14 ) );
	s16i	a4, a5, 0	# MEM[base: _6, offset: 0B], iftmp$4_195
# @OPUS@\upstream\silk\biquad_alt.c:119:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 1 ] + (1<<14) - 1, 14 ) );
	l32r	a4, .LC3	#, iftmp$6_189
# @OPUS@\upstream\silk\biquad_alt.c:119:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 1 ] + (1<<14) - 1, 14 ) );
	srai	a3, a3, 14	# _191, tmp276,
# @OPUS@\upstream\silk\biquad_alt.c:119:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 1 ] + (1<<14) - 1, 14 ) );
	blt	a4, a3, .L13	# tmp6, _191,
	l32r	a4, .LC4	#, iftmp$6_189
	blt	a3, a4, .L13	# _191, tmp7,
	slli	a3, a3, 16	# tmp280, _191,
	srai	a4, a3, 16	# iftmp$6_189, tmp280,
.L13:
# @OPUS@\upstream\silk\biquad_alt.c:119:         out[ 2 * k + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT( out32_Q14[ 1 ] + (1<<14) - 1, 14 ) );
	l32i.n	a11, sp, 16	# %sfp,
	l32i.n	a3, sp, 0	# %sfp,
	s16i	a4, a11, 2	# MEM[base: _6, offset: 2B], iftmp$6_189
	addi.n	a3, a3, 4	#,,
	addi.n	a11, a11, 4	#,,
# @OPUS@\upstream\silk\biquad_alt.c:98:     for( k = 0; k < len; k++ ) {
	l32i.n	a4, sp, 40	# %sfp,
	s32i.n	a3, sp, 0	# %sfp,
	s32i.n	a11, sp, 16	# %sfp,
	bne	a4, a3, .L14	#,,
.L10:
# @OPUS@\upstream\silk\biquad_alt.c:121: }
	l32i	a12, sp, 76	#,
	l32i	a13, sp, 72	#,
	l32i	a14, sp, 68	#,
	l32i	a15, sp, 64	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	silk_biquad_alt_stride2_c, .-silk_biquad_alt_stride2_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
