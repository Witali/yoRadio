# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/stereo_encode_pred.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"stereo_encode_pred.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\stereo_encode_pred.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\stereo_encode_pred.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\stereo_encode_pred.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\stereo_encode_pred.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\stereo_encode_pred.c.s.raw
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
	.section	.text.silk_stereo_encode_pred,"ax",@progbits
	.literal_position
	.literal .LC0, silk_stereo_pred_joint_iCDF
	.literal .LC1, silk_uniform3_iCDF
	.literal .LC2, silk_uniform5_iCDF
	.align	4
	.global	silk_stereo_encode_pred
	.type	silk_stereo_encode_pred, @function
# Function: silk_stereo_encode_pred
# Module: upstream/silk/stereo_encode_pred.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Entropy code the mid/side quantization indices */
# C context: void silk_stereo_encode_pred(
# C context: ec_enc                      *psRangeEnc,                    /* I/O  Compressor data structure                   */
# C context: opus_int8                   ix[ 2 ][ 3 ]                    /* I    Quantization indices                        */
# C context: )
# C context: {
silk_stereo_encode_pred:
	addi	sp, sp, -32	#,,
	s32i.n	a0, sp, 28	#,
	s32i.n	a12, sp, 24	#,
	s32i.n	a13, sp, 20	#,
	s32i.n	a14, sp, 16	#,
	s32i.n	a15, sp, 12	#,
# @OPUS@\upstream\silk\stereo_encode_pred.c:39: {
	mov.n	a12, a3	# ix, ix
# @OPUS@\upstream\silk\stereo_encode_pred.c:43:     n = 5 * ix[ 0 ][ 2 ] + ix[ 1 ][ 2 ];
	l8ui	a3, a3, 2	# *ix_16(D),
# @OPUS@\upstream\silk\stereo_encode_pred.c:43:     n = 5 * ix[ 0 ][ 2 ] + ix[ 1 ][ 2 ];
	l8ui	a4, a12, 5	# MEM[(opus_int8[3] *)ix_16(D) + 3B],
# @OPUS@\upstream\silk\stereo_encode_pred.c:43:     n = 5 * ix[ 0 ][ 2 ] + ix[ 1 ][ 2 ];
	slli	a3, a3, 24	# tmp63, *ix_16(D),
	srai	a3, a3, 24	# tmp64, tmp63,
	slli	a5, a3, 2	# tmp67, tmp64,
# @OPUS@\upstream\silk\stereo_encode_pred.c:43:     n = 5 * ix[ 0 ][ 2 ] + ix[ 1 ][ 2 ];
	slli	a4, a4, 24	# tmp71, MEM[(opus_int8[3] *)ix_16(D) + 3B],
# @OPUS@\upstream\silk\stereo_encode_pred.c:39: {
	mov.n	a13, a2	# psRangeEnc, psRangeEnc
# @OPUS@\upstream\silk\stereo_encode_pred.c:43:     n = 5 * ix[ 0 ][ 2 ] + ix[ 1 ][ 2 ];
	add.n	a3, a5, a3	# tmp68, tmp67, tmp64
# @OPUS@\upstream\silk\stereo_encode_pred.c:43:     n = 5 * ix[ 0 ][ 2 ] + ix[ 1 ][ 2 ];
	srai	a2, a4, 24	# tmp69, tmp71,
# @OPUS@\upstream\silk\stereo_encode_pred.c:45:     ec_enc_icdf( psRangeEnc, n, silk_stereo_pred_joint_iCDF, 8 );
	l32r	a4, .LC0	#,
	add.n	a3, a3, a2	#, tmp68, tmp69
	movi.n	a5, 8	#,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\stereo_encode_pred.c:49:         ec_enc_icdf( psRangeEnc, ix[ n ][ 0 ], silk_uniform3_iCDF, 8 );
	l8ui	a3, a12, 0	# *ix_16(D),
	l32r	a15, .LC1	#, tmp73
	slli	a3, a3, 24	# tmp76, *ix_16(D),
	mov.n	a4, a15	#, tmp73
	mov.n	a2, a13	#, psRangeEnc
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp76,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\stereo_encode_pred.c:50:         ec_enc_icdf( psRangeEnc, ix[ n ][ 1 ], silk_uniform5_iCDF, 8 );
	l8ui	a3, a12, 1	# *ix_16(D),
	l32r	a14, .LC2	#, tmp77
	slli	a3, a3, 24	# tmp80, *ix_16(D),
	mov.n	a4, a14	#, tmp77
	mov.n	a2, a13	#, psRangeEnc
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp80,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\stereo_encode_pred.c:49:         ec_enc_icdf( psRangeEnc, ix[ n ][ 0 ], silk_uniform3_iCDF, 8 );
	l8ui	a3, a12, 3	# MEM[(opus_int8[3] *)ix_16(D) + 3B],
	mov.n	a4, a15	#, tmp73
	slli	a3, a3, 24	# tmp84, MEM[(opus_int8[3] *)ix_16(D) + 3B],
	mov.n	a2, a13	#, psRangeEnc
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp84,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\stereo_encode_pred.c:50:         ec_enc_icdf( psRangeEnc, ix[ n ][ 1 ], silk_uniform5_iCDF, 8 );
	l8ui	a3, a12, 4	# MEM[(opus_int8[3] *)ix_16(D) + 3B],
	mov.n	a4, a14	#, tmp77
	slli	a3, a3, 24	# tmp88, MEM[(opus_int8[3] *)ix_16(D) + 3B],
	mov.n	a2, a13	#, psRangeEnc
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp88,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\stereo_encode_pred.c:52: }
	l32i.n	a0, sp, 28	#,
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_stereo_encode_pred, .-silk_stereo_encode_pred
	.section	.text.silk_stereo_encode_mid_only,"ax",@progbits
	.literal_position
	.literal .LC3, silk_stereo_only_code_mid_iCDF
	.align	4
	.global	silk_stereo_encode_mid_only
	.type	silk_stereo_encode_mid_only, @function
# Function: silk_stereo_encode_mid_only
# Module: upstream/silk/stereo_encode_pred.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Entropy code the mid-only flag */
# C context: void silk_stereo_encode_mid_only(
# C context: ec_enc                      *psRangeEnc,                    /* I/O  Compressor data structure                   */
# C context: opus_int8                   mid_only_flag
# C context: )
# C context: {
silk_stereo_encode_mid_only:
# @OPUS@\upstream\silk\stereo_encode_pred.c:61:     ec_enc_icdf( psRangeEnc, mid_only_flag, silk_stereo_only_code_mid_iCDF, 8 );
	slli	a3, a3, 24	# tmp48, mid_only_flag,
	l32r	a4, .LC3	#,
# @OPUS@\upstream\silk\stereo_encode_pred.c:59: {
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\silk\stereo_encode_pred.c:61:     ec_enc_icdf( psRangeEnc, mid_only_flag, silk_stereo_only_code_mid_iCDF, 8 );
	movi.n	a5, 8	#,
	srai	a3, a3, 24	#, tmp48,
# @OPUS@\upstream\silk\stereo_encode_pred.c:59: {
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\stereo_encode_pred.c:61:     ec_enc_icdf( psRangeEnc, mid_only_flag, silk_stereo_only_code_mid_iCDF, 8 );
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\stereo_encode_pred.c:62: }
	l32i.n	a0, sp, 12	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_stereo_encode_mid_only, .-silk_stereo_encode_mid_only
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
