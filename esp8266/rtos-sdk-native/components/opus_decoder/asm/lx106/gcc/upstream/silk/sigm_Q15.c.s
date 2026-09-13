# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/sigm_Q15.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"sigm_Q15.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\sigm_Q15.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\sigm_Q15.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\sigm_Q15.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\sigm_Q15.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\sigm_Q15.c.s.raw
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
	.section	.text.silk_sigm_Q15,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, sigm_LUT_neg_Q15
	.literal .LC2, sigm_LUT_slope_Q10
	.literal .LC3, sigm_LUT_pos_Q15
	.align	4
	.global	silk_sigm_Q15
	.type	silk_sigm_Q15, @function
# Function: silk_sigm_Q15
# Module: upstream/silk/sigm_Q15.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: 16384, 8812, 3906, 1554, 589, 219
# C context: };
# C context:
# C context: opus_int silk_sigm_Q15(
# C context: opus_int                    in_Q5               /* I                                                                */
# C context: )
# C context: {
# C context: opus_int ind;
silk_sigm_Q15:
# @OPUS@\upstream\silk\sigm_Q15.c:55:     if( in_Q5 < 0 ) {
	bgez	a2, .L2	# in_Q5,
# @OPUS@\upstream\silk\sigm_Q15.c:57:         in_Q5 = -in_Q5;
	neg	a3, a2	# in_Q5, in_Q5
# @OPUS@\upstream\silk\sigm_Q15.c:58:         if( in_Q5 >= 6 * 32 ) {
	movi	a2, 0xbf	# tmp59,
# @OPUS@\upstream\silk\sigm_Q15.c:59:             return 0;        /* Clip */
	movi.n	a4, 0	# <retval>,
# @OPUS@\upstream\silk\sigm_Q15.c:58:         if( in_Q5 >= 6 * 32 ) {
	blt	a2, a3, .L1	# tmp59, in_Q5,
# @OPUS@\upstream\silk\sigm_Q15.c:62:             ind = silk_RSHIFT( in_Q5, 5 );
	srai	a5, a3, 5	# ind, in_Q5,
# @OPUS@\upstream\silk\sigm_Q15.c:63:             return( sigm_LUT_neg_Q15[ ind ] - silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	l32r	a2, .LC2	#, tmp63
# @OPUS@\upstream\silk\sigm_Q15.c:63:             return( sigm_LUT_neg_Q15[ ind ] - silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	slli	a5, a5, 2	# tmp61, ind,
# @OPUS@\upstream\silk\sigm_Q15.c:63:             return( sigm_LUT_neg_Q15[ ind ] - silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	add.n	a2, a2, a5	# tmp65, tmp63, tmp61
	l16si	a4, a2, 0	# sigm_LUT_slope_Q10, tmp67
# @OPUS@\upstream\silk\sigm_Q15.c:63:             return( sigm_LUT_neg_Q15[ ind ] - silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	l32r	a2, .LC1	#, tmp60
	add.n	a5, a2, a5	# tmp62, tmp60, tmp61
# @OPUS@\upstream\silk\sigm_Q15.c:63:             return( sigm_LUT_neg_Q15[ ind ] - silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	extui	a2, a3, 0, 5	# tmp69, in_Q5,
	mull	a2, a4, a2	# tmp70, tmp67, tmp69
# @OPUS@\upstream\silk\sigm_Q15.c:63:             return( sigm_LUT_neg_Q15[ ind ] - silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	l32i.n	a4, a5, 0	# sigm_LUT_neg_Q15, tmp71
	sub	a4, a4, a2	# <retval>, tmp71, tmp70
	j	.L1		#
.L2:
# @OPUS@\upstream\silk\sigm_Q15.c:67:         if( in_Q5 >= 6 * 32 ) {
	movi	a3, 0xbf	# tmp72,
# @OPUS@\upstream\silk\sigm_Q15.c:68:             return 32767;        /* clip */
	l32r	a4, .LC0	#, <retval>
# @OPUS@\upstream\silk\sigm_Q15.c:67:         if( in_Q5 >= 6 * 32 ) {
	blt	a3, a2, .L1	# tmp72, in_Q5,
# @OPUS@\upstream\silk\sigm_Q15.c:71:             ind = silk_RSHIFT( in_Q5, 5 );
	srai	a3, a2, 5	# ind, in_Q5,
# @OPUS@\upstream\silk\sigm_Q15.c:72:             return( sigm_LUT_pos_Q15[ ind ] + silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	l32r	a4, .LC2	#, tmp73
	slli	a3, a3, 2	# tmp74, ind,
	add.n	a4, a4, a3	# tmp75, tmp73, tmp74
# @OPUS@\upstream\silk\sigm_Q15.c:72:             return( sigm_LUT_pos_Q15[ ind ] + silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	l32r	a5, .LC3	#, tmp81
# @OPUS@\upstream\silk\sigm_Q15.c:72:             return( sigm_LUT_pos_Q15[ ind ] + silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	l16si	a4, a4, 0	# sigm_LUT_slope_Q10, tmp77
	extui	a2, a2, 0, 5	# tmp79, in_Q5,
# @OPUS@\upstream\silk\sigm_Q15.c:72:             return( sigm_LUT_pos_Q15[ ind ] + silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	add.n	a3, a5, a3	# tmp83, tmp81, tmp74
# @OPUS@\upstream\silk\sigm_Q15.c:72:             return( sigm_LUT_pos_Q15[ ind ] + silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	mull	a2, a4, a2	# tmp80, tmp77, tmp79
# @OPUS@\upstream\silk\sigm_Q15.c:72:             return( sigm_LUT_pos_Q15[ ind ] + silk_SMULBB( sigm_LUT_slope_Q10[ ind ], in_Q5 & 0x1F ) );
	l32i.n	a4, a3, 0	# sigm_LUT_pos_Q15, tmp84
	add.n	a4, a2, a4	# <retval>, tmp80, tmp84
.L1:
# @OPUS@\upstream\silk\sigm_Q15.c:75: }
	mov.n	a2, a4	#, <retval>
	ret.n
	.size	silk_sigm_Q15, .-silk_sigm_Q15
	.section	.rodata.sigm_LUT_neg_Q15,"a"
	.align	4
	.type	sigm_LUT_neg_Q15, @object
	.size	sigm_LUT_neg_Q15, 24
sigm_LUT_neg_Q15:
	.word	16384
	.word	8812
	.word	3906
	.word	1554
	.word	589
	.word	219
	.section	.rodata.sigm_LUT_pos_Q15,"a"
	.align	4
	.type	sigm_LUT_pos_Q15, @object
	.size	sigm_LUT_pos_Q15, 24
sigm_LUT_pos_Q15:
	.word	16384
	.word	23955
	.word	28861
	.word	31213
	.word	32178
	.word	32548
	.section	.rodata.sigm_LUT_slope_Q10,"a"
	.align	4
	.type	sigm_LUT_slope_Q10, @object
	.size	sigm_LUT_slope_Q10, 24
sigm_LUT_slope_Q10:
	.word	237
	.word	153
	.word	73
	.word	30
	.word	12
	.word	7
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
