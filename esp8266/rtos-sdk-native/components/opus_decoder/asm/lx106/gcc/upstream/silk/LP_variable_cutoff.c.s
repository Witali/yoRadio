# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/LP_variable_cutoff.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"LP_variable_cutoff.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\LP_variable_cutoff.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\LP_variable_cutoff.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\LP_variable_cutoff.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\LP_variable_cutoff.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\LP_variable_cutoff.c.s.raw
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
	.section	.text.silk_LP_variable_cutoff,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, silk_Transition_LP_B_Q28
	.literal .LC2, silk_Transition_LP_A_Q28
	.align	4
	.global	silk_LP_variable_cutoff
	.type	silk_LP_variable_cutoff, @function
# Function: silk_LP_variable_cutoff
# Module: upstream/silk/LP_variable_cutoff.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /* piece-wise linear interpolation between elliptic filters */
# C context: /* Start by setting psEncC->mode <> 0;                      */
# C context: /* Deactivate by setting psEncC->mode = 0;                  */
# C context: void silk_LP_variable_cutoff(
# C context: silk_LP_state               *psLP,                          /* I/O  LP filter state                             */
# C context: opus_int16                  *frame,                         /* I/O  Low-pass filtered output signal             */
# C context: const opus_int              frame_length                    /* I    Frame length                                */
# C context: )
silk_LP_variable_cutoff:
	addi	sp, sp, -112	#,,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:112:     if( psLP->mode != 0 ) {
	l32i.n	a6, a2, 12	# psLP_16(D)->mode, _1
# @OPUS@\upstream\silk\LP_variable_cutoff.c:105: {
	s32i	a0, sp, 108	#,
	s32i	a12, sp, 104	#,
	s32i	a13, sp, 100	#,
	s32i	a14, sp, 96	#,
	s32i	a15, sp, 92	#,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:105: {
	mov.n	a8, a3	# frame, frame
# @OPUS@\upstream\silk\LP_variable_cutoff.c:112:     if( psLP->mode != 0 ) {
	beqz.n	a6, .L1	# _1,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:115:         fac_Q16 = silk_LSHIFT( TRANSITION_FRAMES - psLP->transition_frame_no, 16 - 6 );
	l32i.n	a3, a2, 8	# psLP_16(D)->transition_frame_no,
	s32i.n	a3, sp, 32	# %sfp,
	l32i.n	a5, sp, 32	# %sfp,
	movi	a3, 0x100	# tmp167,
	sub	a3, a3, a5	# tmp168, tmp167,
	slli	a3, a3, 10	# fac_Q16, tmp168,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:119:         ind      = silk_RSHIFT( fac_Q16, 16 );
	srai	a7, a3, 16	# ind, fac_Q16,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:50:     if( ind < TRANSITION_INT_NUM - 1 ) {
	bgei	a7, 4, .L3	# ind,,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:120:         fac_Q16 -= silk_LSHIFT( ind, 16 );
	slli	a5, a7, 16	# tmp169, ind,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:120:         fac_Q16 -= silk_LSHIFT( ind, 16 );
	sub	a3, a3, a5	# fac_Q16, fac_Q16, tmp169
# @OPUS@\upstream\silk\LP_variable_cutoff.c:51:         if( fac_Q16 > 0 ) {
	blti	a3, 1, .L4	# fac_Q16,,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:52:             if( fac_Q16 < 32768 ) { /* fac_Q16 is in range of a 16-bit int */
	l32r	a5, .LC0	#, tmp170
	addi.n	a9, a7, 1	# _51, ind,
	blt	a5, a3, .L5	# tmp170, fac_Q16,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	slli	a10, a7, 1	# tmp173, ind,
	l32r	a12, .LC1	#, tmp171
	add.n	a10, a10, a7	# tmp174, tmp173, ind
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	l32r	a11, .LC2	#, tmp235
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	slli	a5, a9, 1	# tmp179, _51,
	slli	a10, a10, 2	# tmp175, tmp174,
	add.n	a10, a12, a10	# tmp176, tmp171, tmp175
	add.n	a5, a5, a9	# tmp180, tmp179, _51
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	slli	a7, a7, 3	# tmp236, ind,
	slli	a9, a9, 3	# tmp239, _51,
	add.n	a7, a11, a7	# tmp237, tmp235, tmp236
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	slli	a5, a5, 2	# tmp181, tmp180,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	add.n	a11, a11, a9	# tmp240, tmp235, tmp239
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a9, a10, 0	# silk_Transition_LP_B_Q28,
	add.n	a5, a12, a5	# tmp182, tmp171, tmp181
	l32i.n	a12, a10, 4	# silk_Transition_LP_B_Q28,
	l32i.n	a10, a10, 8	# silk_Transition_LP_B_Q28,
	s32i.n	a9, sp, 56	# %sfp,
	s32i.n	a12, sp, 40	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a9, a7, 0	# silk_Transition_LP_A_Q28,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a12, sp, 56	# %sfp,
	s32i.n	a10, sp, 52	# %sfp,
	l32i.n	a10, a5, 0	# silk_Transition_LP_B_Q28, tmp183
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	s32i.n	a9, sp, 44	# %sfp,
	l32i.n	a7, a7, 4	# silk_Transition_LP_A_Q28,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a9, a5, 4	# silk_Transition_LP_B_Q28, tmp205
	sub	a10, a10, a12	# _235, tmp183,
	l32i.n	a12, sp, 40	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	s32i.n	a7, sp, 48	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	sub	a9, a9, a12	# _75, tmp205,
	l32i.n	a7, a5, 8	# silk_Transition_LP_B_Q28, tmp227
	l32i.n	a12, sp, 52	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a5, a11, 0	# silk_Transition_LP_A_Q28, tmp241
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	sub	a7, a7, a12	# _142, tmp227,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a12, sp, 44	# %sfp,
	l32i.n	a11, a11, 4	# silk_Transition_LP_A_Q28, tmp257
	sub	a5, a5, a12	# _119, tmp241,
	l32i.n	a12, sp, 48	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	extui	a14, a9, 0, 16	# tmp206, _75,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	sub	a11, a11, a12	# _139, tmp257,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a9, a9, 16	#, _75,
	s32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a9, a11, 16	#, _139,
	s32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	extui	a11, a11, 0, 16	# tmp261, _139,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	mull	a9, a9, a3	#,, fac_Q16
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	mull	a11, a11, a3	#, tmp261, fac_Q16
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	s32i.n	a9, sp, 60	# %sfp,
	srai	a15, a10, 16	# tmp184, _235,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	extui	a10, a10, 0, 16	# tmp187, _235,
	mull	a10, a10, a3	# tmp188, tmp187, fac_Q16
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	mull	a9, a9, a3	#,, fac_Q16
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	mull	a15, a15, a3	# tmp185, tmp184, fac_Q16
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	s32i	a11, sp, 64	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a11, sp, 56	# %sfp,
	srai	a13, a7, 16	# tmp228, _142,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a12, a5, 16	# tmp242, _119,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a10, a10, 16	#, tmp188,
	extui	a7, a7, 0, 16	# tmp231, _142,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	extui	a5, a5, 0, 16	# tmp245, _119,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	mull	a14, a14, a3	# tmp207, tmp206, fac_Q16
	mull	a13, a13, a3	# tmp229, tmp228, fac_Q16
	mull	a7, a7, a3	# tmp232, tmp231, fac_Q16
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	mull	a12, a12, a3	# tmp243, tmp242, fac_Q16
	mull	a5, a5, a3	# tmp246, tmp245, fac_Q16
	s32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a3, sp, 60	# %sfp,
	add.n	a15, a15, a11	# tmp186, tmp185,
	s32i.n	a10, sp, 56	# %sfp,
	l32i.n	a10, sp, 40	# %sfp,
	l32i.n	a11, sp, 52	# %sfp,
	add.n	a9, a3, a10	# tmp211,,
	add.n	a13, a13, a11	# tmp230, tmp229,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a3, sp, 44	# %sfp,
	l32i.n	a10, sp, 36	# %sfp,
	l32i.n	a11, sp, 48	# %sfp,
	add.n	a12, a12, a3	# tmp244, tmp243,
	add.n	a3, a10, a11	# tmp260,,
	l32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a14, a14, 16	# tmp208, tmp207,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a11, a10, 16	# tmp263,,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a7, a7, 16	# tmp233, tmp232,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:62:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a5, a5, 16	# tmp247, tmp246,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:55:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a10, sp, 56	# %sfp,
	j	.L11		#
.L5:
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	slli	a10, a9, 1	# tmp268, _51,
	l32r	a12, .LC1	#, tmp266
	slli	a5, a7, 1	# tmp274, ind,
	add.n	a10, a10, a9	# tmp269, tmp268, _51
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	l32r	a11, .LC2	#, tmp330
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	add.n	a5, a5, a7	# tmp275, tmp274, ind
	slli	a10, a10, 2	# tmp270, tmp269,
	add.n	a10, a12, a10	# tmp271, tmp266, tmp270
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	slli	a7, a7, 3	# tmp334, ind,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	slli	a5, a5, 2	# tmp276, tmp275,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	slli	a9, a9, 3	# tmp331, _51,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	add.n	a5, a12, a5	# tmp277, tmp266, tmp276
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	add.n	a9, a11, a9	# tmp332, tmp330, tmp331
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a12, a10, 0	# silk_Transition_LP_B_Q28,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	add.n	a11, a11, a7	# tmp335, tmp330, tmp334
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a7, a10, 4	# silk_Transition_LP_B_Q28,
	l32i.n	a10, a10, 8	# silk_Transition_LP_B_Q28,
	s32i.n	a7, sp, 56	# %sfp,
	s32i.n	a10, sp, 48	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a10, a9, 0	# silk_Transition_LP_A_Q28,
	l32i.n	a9, a9, 4	# silk_Transition_LP_A_Q28,
	s32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a10, a5, 0	# silk_Transition_LP_B_Q28, tmp278
	s32i.n	a12, sp, 52	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	s32i.n	a9, sp, 44	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	sub	a10, a12, a10	# _255,, tmp278
	l32i.n	a9, a5, 4	# silk_Transition_LP_B_Q28, tmp300
	l32i.n	a12, sp, 56	# %sfp,
	l32i.n	a7, a5, 8	# silk_Transition_LP_B_Q28, tmp322
	sub	a9, a12, a9	# _274,, tmp300
	l32i.n	a12, sp, 48	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a5, a11, 0	# silk_Transition_LP_A_Q28, tmp336
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	sub	a7, a12, a7	# _220,, tmp322
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a12, sp, 40	# %sfp,
	l32i.n	a11, a11, 4	# silk_Transition_LP_A_Q28, tmp352
	sub	a5, a12, a5	# _159,, tmp336
	l32i.n	a12, sp, 44	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	extui	a14, a9, 0, 16	# tmp301, _274,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	sub	a11, a12, a11	# _179,, tmp352
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a9, a9, 16	#, _274,
	s32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a9, a11, 16	#, _179,
	s32i.n	a9, sp, 36	# %sfp,
	slli	a3, a3, 16	# tmp265, fac_Q16,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a9, sp, 60	# %sfp,
	srai	a3, a3, 16	# _46, tmp265,
	mull	a9, a9, a3	#,, _46
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	extui	a11, a11, 0, 16	# tmp356, _179,
	mull	a11, a11, a3	#, tmp356, _46
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	s32i.n	a9, sp, 60	# %sfp,
	extui	a15, a10, 0, 16	# tmp279, _255,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a10, a10, 16	# tmp282, _255,
	mull	a10, a10, a3	# tmp283, tmp282, _46
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	s32i	a11, sp, 64	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a11, sp, 52	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	mull	a9, a9, a3	#,, _46
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	add.n	a10, a10, a11	#, tmp283,
	extui	a13, a7, 0, 16	# tmp323, _220,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	extui	a12, a5, 0, 16	# tmp337, _159,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a7, a7, 16	# tmp326, _220,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a5, a5, 16	# tmp340, _159,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	mull	a15, a15, a3	# tmp280, tmp279, _46
	mull	a14, a14, a3	# tmp302, tmp301, _46
	mull	a13, a13, a3	# tmp324, tmp323, _46
	mull	a7, a7, a3	# tmp327, tmp326, _46
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	mull	a12, a12, a3	# tmp338, tmp337, _46
	mull	a5, a5, a3	# tmp341, tmp340, _46
	s32i.n	a9, sp, 36	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a3, sp, 60	# %sfp,
	s32i.n	a10, sp, 52	# %sfp,
	l32i.n	a10, sp, 56	# %sfp,
	l32i.n	a11, sp, 48	# %sfp,
	add.n	a9, a3, a10	# tmp306,,
	add.n	a7, a7, a11	# tmp328, tmp327,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	l32i.n	a3, sp, 40	# %sfp,
	l32i.n	a10, sp, 36	# %sfp,
	l32i.n	a11, sp, 44	# %sfp,
	add.n	a5, a5, a3	# tmp342, tmp341,
	add.n	a3, a10, a11	# tmp355,,
	l32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	srai	a15, a15, 16	# tmp281, tmp280,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a11, a10, 16	# tmp358,,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	l32i.n	a10, sp, 52	# %sfp,
	srai	a14, a14, 16	# tmp303, tmp302,
	srai	a13, a13, 16	# tmp325, tmp324,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	srai	a12, a12, 16	# tmp339, tmp338,
.L11:
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	add.n	a14, a14, a9	# tmp307, tmp303, tmp306
	add.n	a15, a15, a10	# tmp285, tmp281,
	add.n	a13, a13, a7	# tmp329, tmp325, tmp328
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	add.n	a12, a12, a5	# tmp343, tmp339, tmp342
	add.n	a11, a3, a11	# tmp359, tmp355, tmp358
# @OPUS@\upstream\silk\LP_variable_cutoff.c:72:                     B_Q28[ nb ] = silk_SMLAWB(
	s32i.n	a15, sp, 0	# MEM[(opus_int32 *)&B_Q28], tmp285
	s32i.n	a14, sp, 4	# MEM[(opus_int32 *)&B_Q28 + 4B], tmp307
	s32i.n	a13, sp, 8	# MEM[(opus_int32 *)&B_Q28 + 8B], tmp329
# @OPUS@\upstream\silk\LP_variable_cutoff.c:79:                     A_Q28[ na ] = silk_SMLAWB(
	s32i.n	a12, sp, 12	# MEM[(opus_int32 *)&A_Q28], tmp343
	s32i.n	a11, sp, 16	# MEM[(opus_int32 *)&A_Q28 + 4B], tmp359
	addi.n	a9, sp, 12	# tmp393,,
	j	.L6		#
.L4:
# @OPUS@\upstream\silk\LP_variable_cutoff.c:87:             silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ ind ], TRANSITION_NB * sizeof( opus_int32 ) );
	slli	a3, a7, 1	# tmp362, ind,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:88:             silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ ind ], TRANSITION_NA * sizeof( opus_int32 ) );
	l32r	a5, .LC2	#, tmp369
# @OPUS@\upstream\silk\LP_variable_cutoff.c:87:             silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ ind ], TRANSITION_NB * sizeof( opus_int32 ) );
	add.n	a3, a3, a7	# tmp363, tmp362, ind
# @OPUS@\upstream\silk\LP_variable_cutoff.c:88:             silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ ind ], TRANSITION_NA * sizeof( opus_int32 ) );
	slli	a7, a7, 3	# tmp370, ind,
	add.n	a7, a5, a7	# tmp371, tmp369, tmp370
# @OPUS@\upstream\silk\LP_variable_cutoff.c:87:             silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ ind ], TRANSITION_NB * sizeof( opus_int32 ) );
	slli	a5, a3, 2	# tmp364, tmp363,
	l32r	a3, .LC1	#, tmp360
# @OPUS@\upstream\silk\LP_variable_cutoff.c:88:             silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ ind ], TRANSITION_NA * sizeof( opus_int32 ) );
	l32i.n	a12, a7, 0	# MEM[(char * {ref-all})_101], MEM[(char * {ref-all})_101]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:87:             silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ ind ], TRANSITION_NB * sizeof( opus_int32 ) );
	add.n	a3, a3, a5	# tmp365, tmp360, tmp364
	l32i.n	a11, a3, 0	# MEM[(char * {ref-all})_100], MEM[(char * {ref-all})_100]
	l32i.n	a10, a3, 4	# MEM[(char * {ref-all})_100], MEM[(char * {ref-all})_100]
	l32i.n	a5, a3, 8	# MEM[(char * {ref-all})_100], MEM[(char * {ref-all})_100]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:88:             silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ ind ], TRANSITION_NA * sizeof( opus_int32 ) );
	l32i.n	a3, a7, 4	# MEM[(char * {ref-all})_101], MEM[(char * {ref-all})_101]
	addi.n	a9, sp, 12	# tmp393,,
	s32i.n	a12, sp, 12	# MEM[(char * {ref-all})&A_Q28], MEM[(char * {ref-all})_101]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:87:             silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ ind ], TRANSITION_NB * sizeof( opus_int32 ) );
	s32i.n	a11, sp, 0	# MEM[(char * {ref-all})&B_Q28], MEM[(char * {ref-all})_100]
	s32i.n	a10, sp, 4	# MEM[(char * {ref-all})&B_Q28], MEM[(char * {ref-all})_100]
	s32i.n	a5, sp, 8	# MEM[(char * {ref-all})&B_Q28], MEM[(char * {ref-all})_100]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:88:             silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ ind ], TRANSITION_NA * sizeof( opus_int32 ) );
	s32i.n	a3, a9, 4	# MEM[(char * {ref-all})&A_Q28], MEM[(char * {ref-all})_101]
	j	.L6		#
.L3:
# @OPUS@\upstream\silk\LP_variable_cutoff.c:91:         silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NB * sizeof( opus_int32 ) );
	l32r	a7, .LC1	#, tmp375
# @OPUS@\upstream\silk\LP_variable_cutoff.c:92:         silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NA * sizeof( opus_int32 ) );
	l32r	a3, .LC2	#, tmp380
# @OPUS@\upstream\silk\LP_variable_cutoff.c:91:         silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NB * sizeof( opus_int32 ) );
	addi	a5, a7, 48	# tmp376, tmp375,
# @OPUS@\upstream\silk\LP_variable_cutoff.c:92:         silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NA * sizeof( opus_int32 ) );
	l32i.n	a11, a3, 32	# MEM[(char * {ref-all})&silk_Transition_LP_A_Q28 + 32B], MEM[(char * {ref-all})&silk_Transition_LP_A_Q28 + 32B]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:91:         silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NB * sizeof( opus_int32 ) );
	l32i.n	a10, a7, 48	# MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B], MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B]
	l32i.n	a5, a5, 8	# MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B], MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B]
	l32i.n	a7, a7, 52	# MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B], MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:92:         silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NA * sizeof( opus_int32 ) );
	l32i.n	a3, a3, 36	# MEM[(char * {ref-all})&silk_Transition_LP_A_Q28 + 32B], MEM[(char * {ref-all})&silk_Transition_LP_A_Q28 + 32B]
	addi.n	a9, sp, 12	# tmp393,,
	s32i.n	a11, sp, 12	# MEM[(char * {ref-all})&A_Q28], MEM[(char * {ref-all})&silk_Transition_LP_A_Q28 + 32B]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:91:         silk_memcpy( B_Q28, silk_Transition_LP_B_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NB * sizeof( opus_int32 ) );
	s32i.n	a10, sp, 0	# MEM[(char * {ref-all})&B_Q28], MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B]
	s32i.n	a7, sp, 4	# MEM[(char * {ref-all})&B_Q28], MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B]
	s32i.n	a5, sp, 8	# MEM[(char * {ref-all})&B_Q28], MEM[(char * {ref-all})&silk_Transition_LP_B_Q28 + 48B]
# @OPUS@\upstream\silk\LP_variable_cutoff.c:92:         silk_memcpy( A_Q28, silk_Transition_LP_A_Q28[ TRANSITION_INT_NUM - 1 ], TRANSITION_NA * sizeof( opus_int32 ) );
	s32i.n	a3, a9, 4	# MEM[(char * {ref-all})&A_Q28], MEM[(char * {ref-all})&silk_Transition_LP_A_Q28 + 32B]
.L6:
# @OPUS@\upstream\silk\LP_variable_cutoff.c:129:         psLP->transition_frame_no = silk_LIMIT( psLP->transition_frame_no + psLP->mode, 0, TRANSITION_FRAMES );
	l32i.n	a11, sp, 32	# %sfp,
	movi.n	a3, 0	# tmp387,
	add.n	a6, a6, a11	# tmp385, _1,
	movltz	a6, a3, a6	# tmp388, tmp387, tmp385
# @OPUS@\upstream\silk\LP_variable_cutoff.c:129:         psLP->transition_frame_no = silk_LIMIT( psLP->transition_frame_no + psLP->mode, 0, TRANSITION_FRAMES );
	movi	a3, 0x100	# tmp391,
	bge	a3, a6, .L7	# tmp391, tmp388,
	mov.n	a6, a3	# tmp388, tmp391
.L7:
	s32i.n	a6, a2, 8	# psLP_16(D)->transition_frame_no, tmp388
# @OPUS@\upstream\silk\LP_variable_cutoff.c:133:         silk_biquad_alt_stride1( frame, B_Q28, A_Q28, psLP->In_LP_State, frame, frame_length);
	mov.n	a7, a4	#, frame_length
	mov.n	a5, a2	#, psLP
	mov.n	a6, a8	#, frame
	mov.n	a4, a9	#, tmp393
	mov.n	a3, sp	#,
	mov.n	a2, a8	#, frame
	call0	silk_biquad_alt_stride1		#
.L1:
# @OPUS@\upstream\silk\LP_variable_cutoff.c:135: }
	l32i	a0, sp, 108	#,
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	silk_LP_variable_cutoff, .-silk_LP_variable_cutoff
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
