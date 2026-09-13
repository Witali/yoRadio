# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF_VQ_weights_laroia.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF_VQ_weights_laroia.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ_weights_laroia.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ_weights_laroia.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ_weights_laroia.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ_weights_laroia.c.s.raw
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
	.global	__udivsi3
	.global	__divsi3
	.section	.text.silk_NLSF_VQ_weights_laroia,"ax",@progbits
	.literal_position
	.literal .LC0, 131072
	.literal .LC1, 32767
	.literal .LC3, 32768
	.align	4
	.global	silk_NLSF_VQ_weights_laroia
	.type	silk_NLSF_VQ_weights_laroia, @function
# Function: silk_NLSF_VQ_weights_laroia
# Module: upstream/silk/NLSF_VQ_weights_laroia.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: */
# C context:
# C context: /* Laroia low complexity NLSF weights */
# C context: void silk_NLSF_VQ_weights_laroia(
# C context: opus_int16                  *pNLSFW_Q_OUT,      /* O     Pointer to input vector weights [D]                        */
# C context: const opus_int16            *pNLSF_Q15,         /* I     Pointer to input vector         [D]                        */
# C context: const opus_int              D                   /* I     Input vector dimension (even)                              */
# C context: )
silk_NLSF_VQ_weights_laroia:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 56	#,
	s32i.n	a3, sp, 4	# %sfp, pNLSF_Q15
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:55:     tmp1_int = silk_max_int( pNLSF_Q15[ 0 ], 1 );
	l16si	a12, a3, 0	# *pNLSF_Q15_49(D), _2
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:57:     tmp2_int = silk_max_int( pNLSF_Q15[ 1 ] - pNLSF_Q15[ 0 ], 1 );
	l16si	a3, a3, 2	# MEM[(const opus_int16 *)pNLSF_Q15_49(D) + 2B], tmp105
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:47: {
	s32i.n	a0, sp, 60	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:47: {
	s32i.n	a2, sp, 8	# %sfp, pNLSFW_Q_OUT
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:57:     tmp2_int = silk_max_int( pNLSF_Q15[ 1 ] - pNLSF_Q15[ 0 ], 1 );
	sub	a3, a3, a12	# tmp104, tmp105, _2
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:47: {
	s32i.n	a4, sp, 12	# %sfp, D
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	bgei	a3, 1, .L2	# tmp104,,
	movi.n	a3, 1	# tmp104,
.L2:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:58:     tmp2_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp2_int );
	l32r	a2, .LC0	#,
	call0	__divsi3		#
	mov.n	a14, a2	# tmp2_int,
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	mov.n	a3, a12	# _2, _2
	bgei	a12, 1, .L3	# _2,,
	movi.n	a3, 1	# _2,
.L3:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:56:     tmp1_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp1_int );
	l32r	a2, .LC0	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	l32r	a12, .LC1	#, tmp203
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:59:     pNLSFW_Q_OUT[ 0 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	add.n	a2, a2, a14	# tmp116,, tmp2_int
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	bge	a12, a2, .L4	# tmp203, tmp116,
	mov.n	a2, a12	# tmp116, tmp203
.L4:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:59:     pNLSFW_Q_OUT[ 0 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	l32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:63:     for( k = 1; k < D - 1; k += 2 ) {
	l32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:59:     pNLSFW_Q_OUT[ 0 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	s16i	a2, a5, 0	# *pNLSFW_Q_OUT_55(D), tmp116
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:63:     for( k = 1; k < D - 1; k += 2 ) {
	addi.n	a2, a4, -1	# tmp133,,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:63:     for( k = 1; k < D - 1; k += 2 ) {
	blti	a2, 2, .L5	# tmp133,,
	l32i.n	a5, sp, 4	# %sfp,
	addi	a13, a4, -3	# tmp134,,
	srli	a13, a13, 1	# tmp135, tmp134,
	slli	a2, a13, 2	# tmp136, tmp135,
	addi.n	a3, a5, 6	# tmp137,,
	addi.n	a13, a5, 2	# ivtmp$12,,
	l32i.n	a5, sp, 8	# %sfp,
	add.n	a3, a2, a3	#, tmp136, tmp137
	addi.n	a15, a5, 2	# ivtmp$14,,
	s32i.n	a3, sp, 0	# %sfp,
.L10:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:64:         tmp1_int = silk_max_int( pNLSF_Q15[ k + 1 ] - pNLSF_Q15[ k ], 1 );
	l16si	a3, a13, 2	# MEM[base: _102, offset: 2B], tmp139
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:64:         tmp1_int = silk_max_int( pNLSF_Q15[ k + 1 ] - pNLSF_Q15[ k ], 1 );
	l16si	a4, a13, 0	# MEM[base: _102, offset: 0B], tmp142
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:65:         tmp1_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp1_int );
	l32r	a2, .LC0	#,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:64:         tmp1_int = silk_max_int( pNLSF_Q15[ k + 1 ] - pNLSF_Q15[ k ], 1 );
	sub	a3, a3, a4	# tmp138, tmp139, tmp142
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	bgei	a3, 1, .L6	# tmp138,,
	movi.n	a3, 1	# tmp138,
.L6:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:65:         tmp1_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp1_int );
	call0	__divsi3		#
	mov.n	a4, a2	# tmp1_int,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:66:         pNLSFW_Q_OUT[ k ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	add.n	a3, a4, a14	# tmp153, tmp1_int, tmp2_int
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:70:         tmp2_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp2_int );
	l32r	a2, .LC0	#,
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	bge	a12, a3, .L7	# tmp203, tmp153,
	mov.n	a3, a12	# tmp153, tmp203
.L7:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:66:         pNLSFW_Q_OUT[ k ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	s16i	a3, a15, 0	# MEM[base: _100, offset: 0B], tmp153
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:69:         tmp2_int = silk_max_int( pNLSF_Q15[ k + 2 ] - pNLSF_Q15[ k + 1 ], 1 );
	l16si	a3, a13, 4	# MEM[base: _102, offset: 4B], tmp160
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:69:         tmp2_int = silk_max_int( pNLSF_Q15[ k + 2 ] - pNLSF_Q15[ k + 1 ], 1 );
	l16si	a7, a13, 2	# MEM[base: _102, offset: 2B], tmp163
	addi.n	a13, a13, 4	# ivtmp$12, ivtmp$12,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:69:         tmp2_int = silk_max_int( pNLSF_Q15[ k + 2 ] - pNLSF_Q15[ k + 1 ], 1 );
	sub	a3, a3, a7	# tmp159, tmp160, tmp163
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	bgei	a3, 1, .L8	# tmp159,,
	movi.n	a3, 1	# tmp159,
.L8:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:70:         tmp2_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp2_int );
	s32i.n	a4, sp, 16	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:71:         pNLSFW_Q_OUT[ k + 1 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	l32i.n	a4, sp, 16	#,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:70:         tmp2_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp2_int );
	mov.n	a14, a2	# tmp2_int,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:71:         pNLSFW_Q_OUT[ k + 1 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	add.n	a2, a4, a2	# tmp174, tmp1_int, tmp2_int
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	bge	a12, a2, .L9	# tmp203, tmp174,
	mov.n	a2, a12	# tmp174, tmp203
.L9:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:63:     for( k = 1; k < D - 1; k += 2 ) {
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:71:         pNLSFW_Q_OUT[ k + 1 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	s16i	a2, a15, 2	# MEM[base: _100, offset: 2B], tmp174
	addi.n	a15, a15, 4	# ivtmp$14, ivtmp$14,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:63:     for( k = 1; k < D - 1; k += 2 ) {
	bne	a4, a13, .L10	#, ivtmp$12,
.L5:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:76:     tmp1_int = silk_max_int( ( 1 << 15 ) - pNLSF_Q15[ D - 1 ], 1 );
	l32i.n	a5, sp, 12	# %sfp,
	slli	a4, a5, 1	# tmp180,,
	l32i.n	a5, sp, 4	# %sfp,
	addi	a4, a4, -2	# _37, tmp180,
	add.n	a2, a5, a4	# tmp184,, _37
	l16si	a3, a2, 0	# *_38, tmp185
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:77:     tmp1_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp1_int );
	l32r	a5, .LC3	#, tmp189
	l32r	a2, .LC0	#,
	sub	a3, a5, a3	#, tmp189, tmp185
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:78:     pNLSFW_Q_OUT[ D - 1 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	l32i.n	a5, sp, 8	# %sfp,
	add.n	a13, a5, a4	# tmp182,, _37
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:77:     tmp1_int = silk_DIV32_16( (opus_int32)1 << ( 15 + NLSF_W_Q ), tmp1_int );
	call0	__divsi3		#
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:78:     pNLSFW_Q_OUT[ D - 1 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	add.n	a2, a2, a14	# tmp183,, tmp2_int
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	bge	a12, a2, .L11	# tmp203, tmp183,
	mov.n	a2, a12	# tmp183, tmp203
.L11:
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:80: }
	l32i.n	a0, sp, 60	#,
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:78:     pNLSFW_Q_OUT[ D - 1 ] = (opus_int16)silk_min_int( tmp1_int + tmp2_int, silk_int16_MAX );
	s16i	a2, a13, 0	# *_43, tmp183
# @OPUS@\upstream\silk\NLSF_VQ_weights_laroia.c:80: }
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_NLSF_VQ_weights_laroia, .-silk_NLSF_VQ_weights_laroia
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
