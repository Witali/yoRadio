# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/log2lin.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"log2lin.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\log2lin.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\log2lin.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\log2lin.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\log2lin.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\log2lin.c.s.raw
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
	.section	.text.silk_log2lin,"ax",@progbits
	.literal_position
	.literal .LC0, 2147483647
	.literal .LC1, 3966
	.align	4
	.global	silk_log2lin
	.type	silk_log2lin, @function
# Function: silk_log2lin
# Module: upstream/silk/log2lin.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Approximation of 2^() (very close inverse of silk_lin2log()) */
# C context: /* Convert input to a linear scale    */
# C context: opus_int32 silk_log2lin(
# C context: const opus_int32            inLog_Q7            /* I  input on log scale                                            */
# C context: )
# C context: {
# C context: opus_int32 out, frac_Q7;
silk_log2lin:
# @OPUS@\upstream\silk\log2lin.c:43:         return 0;
	movi.n	a3, 0	# <retval>,
# @OPUS@\upstream\silk\log2lin.c:42:     if( inLog_Q7 < 0 ) {
	blt	a2, a3, .L1	# inLog_Q7,,
# @OPUS@\upstream\silk\log2lin.c:44:     } else if ( inLog_Q7 >= 3967 ) {
	l32r	a4, .LC1	#, tmp59
# @OPUS@\upstream\silk\log2lin.c:45:         return silk_int32_MAX;
	l32r	a3, .LC0	#, <retval>
# @OPUS@\upstream\silk\log2lin.c:44:     } else if ( inLog_Q7 >= 3967 ) {
	blt	a4, a2, .L1	# tmp59, inLog_Q7,
# @OPUS@\upstream\silk\log2lin.c:49:     frac_Q7 = inLog_Q7 & 0x7F;
	extui	a5, a2, 0, 7	# frac_Q7, inLog_Q7,
	movi	a3, 0x80	# tmp65,
	sub	a3, a3, a5	# tmp64, tmp65, frac_Q7
	mull	a3, a3, a5	# tmp66, tmp64, frac_Q7
	movi	a4, -0xae	# tmp67,
	mull	a3, a3, a4	# tmp68, tmp66, tmp67
# @OPUS@\upstream\silk\log2lin.c:48:     out = silk_LSHIFT( 1, silk_RSHIFT( inLog_Q7, 7 ) );
	srai	a6, a2, 7	# _1, inLog_Q7,
	srai	a3, a3, 16	# tmp69, tmp68,
	movi.n	a4, 1	# tmp60,
# @OPUS@\upstream\silk\log2lin.c:50:     if( inLog_Q7 < 2048 ) {
	movi	a7, 0x7ff	# tmp70,
# @OPUS@\upstream\silk\log2lin.c:48:     out = silk_LSHIFT( 1, silk_RSHIFT( inLog_Q7, 7 ) );
	ssl	a6	# _1
	sll	a4, a4	# out, tmp60
	add.n	a3, a3, a5	# _37, tmp69, frac_Q7
# @OPUS@\upstream\silk\log2lin.c:50:     if( inLog_Q7 < 2048 ) {
	blt	a7, a2, .L3	# tmp70, inLog_Q7,
# @OPUS@\upstream\silk\log2lin.c:52:         out = silk_ADD_RSHIFT32( out, silk_MUL( out, silk_SMLAWB( frac_Q7, silk_SMULBB( frac_Q7, 128 - frac_Q7 ), -174 ) ), 7 );
	ssl	a6	# _1
	sll	a3, a3	# tmp71, _37
	srai	a3, a3, 7	# tmp72, tmp71,
# @OPUS@\upstream\silk\log2lin.c:52:         out = silk_ADD_RSHIFT32( out, silk_MUL( out, silk_SMLAWB( frac_Q7, silk_SMULBB( frac_Q7, 128 - frac_Q7 ), -174 ) ), 7 );
	add.n	a3, a3, a4	# <retval>, tmp72, out
	j	.L1		#
.L3:
# @OPUS@\upstream\silk\log2lin.c:55:         out = silk_MLA( out, silk_RSHIFT( out, 7 ), silk_SMLAWB( frac_Q7, silk_SMULBB( frac_Q7, 128 - frac_Q7 ), -174 ) );
	srai	a2, a4, 7	# tmp73, out,
	mull	a3, a2, a3	# _26, tmp73, _37
# @OPUS@\upstream\silk\log2lin.c:55:         out = silk_MLA( out, silk_RSHIFT( out, 7 ), silk_SMLAWB( frac_Q7, silk_SMULBB( frac_Q7, 128 - frac_Q7 ), -174 ) );
	add.n	a3, a3, a4	# <retval>, _26, out
.L1:
# @OPUS@\upstream\silk\log2lin.c:58: }
	mov.n	a2, a3	#, <retval>
	ret.n
	.size	silk_log2lin, .-silk_log2lin
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
