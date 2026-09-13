# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/lin2log.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"lin2log.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\lin2log.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\lin2log.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\lin2log.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\lin2log.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\lin2log.c.s.raw
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
	.section	.text.silk_lin2log,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_lin2log
	.type	silk_lin2log, @function
# Function: silk_lin2log
# Module: upstream/silk/lin2log.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "SigProc_FIX.h"
# C context: /* Approximation of 128 * log2() (very close inverse of silk_log2lin()) */
# C context: /* Convert input to a log scale    */
# C context: opus_int32 silk_lin2log(
# C context: const opus_int32            inLin               /* I  input in linear scale                                         */
# C context: )
# C context: {
# C context: opus_int32 lz, frac_Q7;
silk_lin2log:
# @OPUS@\upstream\silk\lin2log.c:38: {
	mov.n	a3, a2	# inLin, inLin
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi	a2, -0x80	# <retval>,
	beqz.n	a3, .L1	# inLin,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a5, a3	# iftmp$6_16, inLin
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a2, 0x18	# tmp76,
	sub	a2, a2, a5	# _18, tmp76, iftmp$6_16
# @OPUS@\upstream\silk\SigProc_FIX.h:403:     if( rot == 0 ) {
	bnez.n	a2, .L3	# _18,
	extui	a3, a3, 0, 7	# _110, inLin,
	movi	a2, 0x80	# tmp77,
	sub	a2, a2, a3	# tmp78, tmp77, _110
	mull	a4, a2, a3	# tmp79, tmp78, _110
	slli	a2, a4, 1	# tmp81, tmp79,
	add.n	a5, a2, a4	# tmp82, tmp81, tmp79
	slli	a2, a5, 4	# tmp83, tmp82,
	sub	a2, a2, a5	# tmp84, tmp83, tmp82
	slli	a2, a2, 2	# tmp85, tmp84,
	sub	a2, a2, a4	# tmp86, tmp85, tmp79
	movi	a4, 0x380	# tmp88,
	srai	a2, a2, 16	# tmp87, tmp86,
	add.n	a3, a3, a4	# tmp89, _110, tmp88
	add.n	a2, a2, a3	# <retval>, tmp87, tmp89
	j	.L1		#
.L3:
	movi.n	a4, 0x1f	# tmp90,
	sub	a4, a4, a5	# tmp91, tmp90, iftmp$6_16
	slli	a6, a4, 7	# _107, tmp91,
# @OPUS@\upstream\silk\SigProc_FIX.h:405:     } else if( rot < 0 ) {
	bgez	a2, .L5	# _18,
# @OPUS@\upstream\silk\SigProc_FIX.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a4, a5, -24	# m, iftmp$6_16,
	ssl	a4	# m
	src	a4, a3, a3	# tmp93, inLin
	extui	a4, a4, 0, 7	# _80, tmp93,
	movi	a2, 0x80	# tmp94,
	sub	a2, a2, a4	# tmp95, tmp94, _80
	mull	a3, a2, a4	# tmp96, tmp95, _80
	add.n	a4, a4, a6	# tmp105, _80, _107
	slli	a2, a3, 1	# tmp98, tmp96,
	add.n	a5, a2, a3	# tmp99, tmp98, tmp96
	slli	a2, a5, 4	# tmp100, tmp99,
	sub	a2, a2, a5	# tmp101, tmp100, tmp99
	slli	a2, a2, 2	# tmp102, tmp101,
	sub	a2, a2, a3	# tmp103, tmp102, tmp96
	srai	a2, a2, 16	# tmp104, tmp103,
	add.n	a2, a2, a4	# <retval>, tmp104, tmp105
	j	.L1		#
.L5:
# @OPUS@\upstream\silk\SigProc_FIX.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a2	# _18
	src	a3, a3, a3	# tmp106, inLin
	extui	a3, a3, 0, 7	# _108, tmp106,
	movi	a2, 0x80	# tmp107,
	sub	a2, a2, a3	# tmp108, tmp107, _108
	mull	a5, a2, a3	# tmp109, tmp108, _108
	add.n	a3, a6, a3	# tmp118, _107, _108
	slli	a2, a5, 1	# tmp111, tmp109,
	add.n	a6, a2, a5	# tmp112, tmp111, tmp109
	slli	a2, a6, 4	# tmp113, tmp112,
	sub	a2, a2, a6	# tmp114, tmp113, tmp112
	slli	a2, a2, 2	# tmp115, tmp114,
	sub	a2, a2, a5	# tmp116, tmp115, tmp109
	srai	a2, a2, 16	# tmp117, tmp116,
	add.n	a2, a2, a3	# <retval>, tmp117, tmp118
.L1:
# @OPUS@\upstream\silk\lin2log.c:45: }
	ret.n
	.size	silk_lin2log, .-silk_lin2log
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
