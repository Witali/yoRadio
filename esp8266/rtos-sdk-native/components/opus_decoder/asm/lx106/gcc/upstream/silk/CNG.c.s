# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/CNG.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"CNG.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\CNG.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\CNG.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\CNG.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\CNG.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\CNG.c.s.raw
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
	.section	.text.silk_CNG_Reset,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, 3176576
	.align	4
	.global	silk_CNG_Reset
	.type	silk_CNG_Reset, @function
# Function: silk_CNG_Reset
# Module: upstream/silk/CNG.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: *rand_seed = seed;
# C context: }
# C context:
# C context: void silk_CNG_Reset(
# C context: silk_decoder_state          *psDec                          /* I/O  Decoder state                               */
# C context: )
# C context: {
# C context: opus_int i, NLSF_step_Q15, NLSF_acc_Q15;
silk_CNG_Reset:
	addi	sp, sp, -16	#,,
	s32i.n	a13, sp, 4	#,
	mov.n	a13, a2	# psDec, psDec
# @OPUS@\upstream\silk\CNG.c:68:     NLSF_step_Q15 = silk_DIV32_16( silk_int16_MAX, psDec->LPC_order + 1 );
	addmi	a2, a2, 0x400	# tmp77, psDec,
# @OPUS@\upstream\silk\CNG.c:65: {
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\silk\CNG.c:68:     NLSF_step_Q15 = silk_DIV32_16( silk_int16_MAX, psDec->LPC_order + 1 );
	l32i.n	a12, a2, 40	# psDec_8(D)->LPC_order, _1
# @OPUS@\upstream\silk\CNG.c:68:     NLSF_step_Q15 = silk_DIV32_16( silk_int16_MAX, psDec->LPC_order + 1 );
	l32r	a2, .LC0	#,
	addi.n	a3, a12, 1	#, _1,
# @OPUS@\upstream\silk\CNG.c:65: {
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\CNG.c:68:     NLSF_step_Q15 = silk_DIV32_16( silk_int16_MAX, psDec->LPC_order + 1 );
	call0	__divsi3		#
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	blti	a12, 1, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	addmi	a4, a13, 0xa00	# tmp108, psDec,
	s16i	a2, a4, 216	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_step_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 1, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	slli	a3, a2, 1	# NLSF_acc_Q15, NLSF_step_Q15,
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 218	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 2, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 220	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 3, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 222	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 4, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 224	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 5, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 226	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 6, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 228	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 7, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 230	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 8, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 232	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 9	# tmp91,
	beq	a12, a5, .L2	# _1, tmp91,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 234	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 10, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 236	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xb	# tmp94,
	beq	a12, a5, .L2	# _1, tmp94,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 238	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 12, .L2	# _1,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 240	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xd	# tmp97,
	beq	a12, a5, .L2	# _1, tmp97,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 242	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xe	# tmp99,
	beq	a12, a5, .L2	# _1, tmp99,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 244	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xf	# tmp101,
	beq	a12, a5, .L2	# _1, tmp101,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a3, a2, a3	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a3, a4, 246	# psDec_8(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
.L2:
# @OPUS@\upstream\silk\CNG.c:74:     psDec->sCNG.CNG_smth_Gain_Q16 = 0;
	addmi	a13, a13, 0xb00	# tmp104, psDec,
	movi.n	a2, 0	# tmp105,
	s32i.n	a2, a13, 56	# psDec_8(D)->sCNG.CNG_smth_Gain_Q16, tmp105
# @OPUS@\upstream\silk\CNG.c:76: }
	l32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\CNG.c:75:     psDec->sCNG.rand_seed = 3176576;
	l32r	a2, .LC1	#, tmp107
# @OPUS@\upstream\silk\CNG.c:76: }
	l32i.n	a12, sp, 8	#,
# @OPUS@\upstream\silk\CNG.c:75:     psDec->sCNG.rand_seed = 3176576;
	s32i.n	a2, a13, 60	# psDec_8(D)->sCNG.rand_seed, tmp107
# @OPUS@\upstream\silk\CNG.c:76: }
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_CNG_Reset, .-silk_CNG_Reset
	.section	.text.silk_CNG,"ax",@progbits
	.literal_position
	.literal .LC2, 46214
	.literal .LC3, 32768
	.literal .LC4, -2147483648
	.literal .LC5, 2147483632
	.literal .LC6, -32768
	.literal .LC7, 32767
	.literal .LC8, 2147483647
	.literal .LC9, 3176576
	.literal .LC10, 4634
	.literal .LC11, -19140
	.literal .LC12, 2097151
	.literal .LC13, 8388608
	.literal .LC14, 196314165
	.literal .LC15, 907633515
	.literal .LC16, 134217727
	.literal .LC17, -134217728
	.align	4
	.global	silk_CNG
	.type	silk_CNG, @function
# Function: silk_CNG
# Module: upstream/silk/CNG.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Updates CNG estimate, and applies the CNG when packet was lost   */
# C context: void silk_CNG(
# C context: silk_decoder_state          *psDec,                         /* I/O  Decoder state                               */
# C context: silk_decoder_control        *psDecCtrl,                     /* I/O  Decoder control                             */
# C context: opus_int16                  frame[],                        /* I/O  Signal                                      */
# C context: opus_int                    length                          /* I    Length of residual                          */
silk_CNG:
	movi	a9, 0xd0	#,
	sub	sp, sp, a9	#,,
	s32i	a12, sp, 200	#,
	s32i	a13, sp, 196	#,
	s32i	a14, sp, 192	#,
	mov.n	a13, a2	# psDec, psDec
	s32i	a15, sp, 188	#,
	s32i.n	a4, sp, 48	# %sfp, frame
	s32i	a0, sp, 204	#,
# @OPUS@\upstream\silk\CNG.c:85: {
	s32i.n	a3, sp, 52	# %sfp, psDecCtrl
	mov.n	a15, a5	# length, length
# @OPUS@\upstream\silk\CNG.c:90:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\CNG.c:92:     if( psDec->fs_kHz != psCNG->fs_kHz ) {
	movi	a4, 0x5d8	# tmp740,
	add.n	a4, a13, a4	# tmp741, psDec, tmp740
# @OPUS@\upstream\silk\CNG.c:92:     if( psDec->fs_kHz != psCNG->fs_kHz ) {
	addmi	a6, a13, 0x400	#, psDec,
# @OPUS@\upstream\silk\CNG.c:92:     if( psDec->fs_kHz != psCNG->fs_kHz ) {
	addmi	a4, a4, 0x500	# tmp742, tmp741,
# @OPUS@\upstream\silk\CNG.c:92:     if( psDec->fs_kHz != psCNG->fs_kHz ) {
	l32i.n	a14, a6, 16	# psDec_382(D)->fs_kHz, _1
# @OPUS@\upstream\silk\CNG.c:92:     if( psDec->fs_kHz != psCNG->fs_kHz ) {
	l32i	a4, a4, 104	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].fs_kHz, MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].fs_kHz
# @OPUS@\upstream\silk\CNG.c:92:     if( psDec->fs_kHz != psCNG->fs_kHz ) {
	s32i.n	a6, sp, 56	# %sfp,
# @OPUS@\upstream\silk\CNG.c:90:     SAVE_STACK;
	s32i.n	a2, sp, 32	# _saved_stack,
	s32i.n	a3, sp, 36	# _saved_stack,
	addmi	a12, a13, 0xb00	# tmp1749, psDec,
# @OPUS@\upstream\silk\CNG.c:92:     if( psDec->fs_kHz != psCNG->fs_kHz ) {
	beq	a14, a4, .L35	# _1, MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].fs_kHz,
# @OPUS@\upstream\silk\CNG.c:68:     NLSF_step_Q15 = silk_DIV32_16( silk_int16_MAX, psDec->LPC_order + 1 );
	l32i.n	a12, a6, 40	# psDec_382(D)->LPC_order, _402
# @OPUS@\upstream\silk\CNG.c:68:     NLSF_step_Q15 = silk_DIV32_16( silk_int16_MAX, psDec->LPC_order + 1 );
	l32r	a2, .LC7	#,
	addi.n	a3, a12, 1	#, _402,
	call0	__divsi3		#
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	bgei	a12, 1, .L36	# _402,,
.L37:
# @OPUS@\upstream\silk\CNG.c:74:     psDec->sCNG.CNG_smth_Gain_Q16 = 0;
	addmi	a12, a13, 0xb00	# tmp1749, psDec,
	movi.n	a3, 0	# tmp750,
	s32i.n	a3, a12, 56	# psDec_382(D)->sCNG.CNG_smth_Gain_Q16, tmp750
# @OPUS@\upstream\silk\CNG.c:96:         psCNG->fs_kHz = psDec->fs_kHz;
	movi	a2, 0x5d8	# tmp754,
# @OPUS@\upstream\silk\CNG.c:75:     psDec->sCNG.rand_seed = 3176576;
	l32r	a3, .LC9	#, tmp752
# @OPUS@\upstream\silk\CNG.c:96:         psCNG->fs_kHz = psDec->fs_kHz;
	add.n	a2, a13, a2	# tmp755, psDec, tmp754
# @OPUS@\upstream\silk\CNG.c:75:     psDec->sCNG.rand_seed = 3176576;
	s32i.n	a3, a12, 60	# psDec_382(D)->sCNG.rand_seed, tmp752
# @OPUS@\upstream\silk\CNG.c:96:         psCNG->fs_kHz = psDec->fs_kHz;
	addmi	a2, a2, 0x500	# tmp756, tmp755,
	s32i	a14, a2, 104	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].fs_kHz, _1
	j	.L35		#
.L36:
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	addmi	a3, a13, 0xa00	# tmp1744, psDec,
	s16i	a2, a3, 216	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_step_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 1, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	slli	a4, a2, 1	# NLSF_acc_Q15, NLSF_step_Q15,
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 218	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 2, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 220	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 3, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 222	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 4, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 224	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 5, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 226	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 6, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 228	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 7, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 230	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 8, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 232	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 9	# tmp766,
	beq	a12, a5, .L37	# _402, tmp766,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 234	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 10, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 236	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xb	# tmp769,
	beq	a12, a5, .L37	# _402, tmp769,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 238	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a12, 12, .L37	# _402,,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 240	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xd	# tmp772,
	beq	a12, a5, .L37	# _402, tmp772,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 242	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xe	# tmp774,
	beq	a12, a5, .L37	# _402, tmp774,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 244	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:70:     for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a5, 0xf	# tmp776,
	beq	a12, a5, .L37	# _402, tmp776,
# @OPUS@\upstream\silk\CNG.c:71:         NLSF_acc_Q15 += NLSF_step_Q15;
	add.n	a4, a2, a4	# NLSF_acc_Q15, NLSF_step_Q15, NLSF_acc_Q15
# @OPUS@\upstream\silk\CNG.c:72:         psDec->sCNG.CNG_smth_NLSF_Q15[ i ] = NLSF_acc_Q15;
	s16i	a4, a3, 246	# psDec_382(D)->sCNG.CNG_smth_NLSF_Q15, NLSF_acc_Q15
	j	.L37		#
.L35:
# @OPUS@\upstream\silk\CNG.c:98:     if( psDec->lossCnt == 0 && psDec->prevSignalType == TYPE_NO_VOICE_ACTIVITY ) {
	l32i	a2, a12, 68	# psDec_382(D)->lossCnt, psDec_382(D)->lossCnt
	bnez.n	a2, .L38	# psDec_382(D)->lossCnt,
	l32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\silk\CNG.c:98:     if( psDec->lossCnt == 0 && psDec->prevSignalType == TYPE_NO_VOICE_ACTIVITY ) {
	l32i	a14, a12, 72	# psDec_382(D)->prevSignalType, subfr
	l32i.n	a4, a7, 40	# psDec_382(D)->LPC_order, pretmp_1202
# @OPUS@\upstream\silk\CNG.c:98:     if( psDec->lossCnt == 0 && psDec->prevSignalType == TYPE_NO_VOICE_ACTIVITY ) {
	bnez.n	a14, .L39	# subfr,
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	bgei	a4, 1, .L40	# pretmp_1202,,
.L43:
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	l32i.n	a8, sp, 56	# %sfp,
	l32i.n	a2, a8, 24	# psDec_382(D)->nb_subfr, _533
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	bgei	a2, 1, .L41	# _533,,
	j	.L42		#
.L40:
	mov.n	a9, a7	#,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	addmi	a3, a13, 0xa00	# tmp1744, psDec,
	l16si	a7, a3, 216	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2776B], _1094
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a9, 44	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1068B], tmp788
	sub	a2, a2, a7	# _1090, tmp788, _1094
	srai	a9, a2, 16	# tmp792, _1090,
	extui	a8, a2, 0, 16	# tmp806, _1090,
	slli	a5, a9, 9	# tmp795, tmp792,
	slli	a2, a8, 9	# tmp808, tmp806,
	sub	a5, a5, a9	# tmp797, tmp795, tmp792
	sub	a2, a2, a8	# tmp809, tmp808, tmp806
	slli	a5, a5, 3	# tmp799, tmp797,
	slli	a2, a2, 3	# tmp810, tmp809,
	sub	a5, a5, a9	# tmp801, tmp799, tmp792
	sub	a2, a2, a8	# tmp811, tmp810, tmp806
	slli	a5, a5, 2	# tmp803, tmp801,
	slli	a2, a2, 2	# tmp812, tmp811,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp805, _1094, tmp803
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp813, tmp812,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp816, tmp805, tmp813
	s16i	a2, a3, 216	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2776B], tmp816
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 1, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l32i.n	a10, sp, 56	# %sfp,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 218	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2778B], _1076
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a10, 46	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1070B], tmp821
	sub	a2, a2, a7	# _1072, tmp821, _1076
	srai	a9, a2, 16	# tmp825, _1072,
	extui	a8, a2, 0, 16	# tmp839, _1072,
	slli	a5, a9, 9	# tmp828, tmp825,
	slli	a2, a8, 9	# tmp841, tmp839,
	sub	a5, a5, a9	# tmp830, tmp828, tmp825
	sub	a2, a2, a8	# tmp842, tmp841, tmp839
	slli	a5, a5, 3	# tmp832, tmp830,
	slli	a2, a2, 3	# tmp843, tmp842,
	sub	a5, a5, a9	# tmp834, tmp832, tmp825
	sub	a2, a2, a8	# tmp844, tmp843, tmp839
	slli	a5, a5, 2	# tmp836, tmp834,
	slli	a2, a2, 2	# tmp845, tmp844,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp838, _1076, tmp836
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp846, tmp845,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp849, tmp838, tmp846
	s16i	a2, a3, 218	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2778B], tmp849
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 2, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 220	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2780B], _1058
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a10, 48	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1072B], tmp854
	sub	a2, a2, a7	# _1025, tmp854, _1058
	srai	a9, a2, 16	# tmp858, _1025,
	extui	a8, a2, 0, 16	# tmp872, _1025,
	slli	a5, a9, 9	# tmp861, tmp858,
	slli	a2, a8, 9	# tmp874, tmp872,
	sub	a5, a5, a9	# tmp863, tmp861, tmp858
	sub	a2, a2, a8	# tmp875, tmp874, tmp872
	slli	a5, a5, 3	# tmp865, tmp863,
	slli	a2, a2, 3	# tmp876, tmp875,
	sub	a5, a5, a9	# tmp867, tmp865, tmp858
	sub	a2, a2, a8	# tmp877, tmp876, tmp872
	slli	a5, a5, 2	# tmp869, tmp867,
	slli	a2, a2, 2	# tmp878, tmp877,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp871, _1058, tmp869
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp879, tmp878,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp882, tmp871, tmp879
	s16i	a2, a3, 220	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2780B], tmp882
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 3, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 222	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2782B], _1004
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a10, 50	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1074B], tmp887
	sub	a2, a2, a7	# _1000, tmp887, _1004
	srai	a9, a2, 16	# tmp891, _1000,
	extui	a8, a2, 0, 16	# tmp905, _1000,
	slli	a5, a9, 9	# tmp894, tmp891,
	slli	a2, a8, 9	# tmp907, tmp905,
	sub	a5, a5, a9	# tmp896, tmp894, tmp891
	sub	a2, a2, a8	# tmp908, tmp907, tmp905
	slli	a5, a5, 3	# tmp898, tmp896,
	slli	a2, a2, 3	# tmp909, tmp908,
	sub	a5, a5, a9	# tmp900, tmp898, tmp891
	sub	a2, a2, a8	# tmp910, tmp909, tmp905
	slli	a5, a5, 2	# tmp902, tmp900,
	slli	a2, a2, 2	# tmp911, tmp910,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp904, _1004, tmp902
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp912, tmp911,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp915, tmp904, tmp912
	s16i	a2, a3, 222	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2782B], tmp915
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 4, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 224	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2784B], _986
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a10, 52	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1076B], tmp920
	sub	a2, a2, a7	# _982, tmp920, _986
	srai	a9, a2, 16	# tmp924, _982,
	extui	a8, a2, 0, 16	# tmp938, _982,
	slli	a5, a9, 9	# tmp927, tmp924,
	slli	a2, a8, 9	# tmp940, tmp938,
	sub	a5, a5, a9	# tmp929, tmp927, tmp924
	sub	a2, a2, a8	# tmp941, tmp940, tmp938
	slli	a5, a5, 3	# tmp931, tmp929,
	slli	a2, a2, 3	# tmp942, tmp941,
	sub	a5, a5, a9	# tmp933, tmp931, tmp924
	sub	a2, a2, a8	# tmp943, tmp942, tmp938
	slli	a5, a5, 2	# tmp935, tmp933,
	slli	a2, a2, 2	# tmp944, tmp943,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp937, _986, tmp935
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp945, tmp944,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp948, tmp937, tmp945
	s16i	a2, a3, 224	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2784B], tmp948
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 5, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 226	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2786B], _968
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a10, 54	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1078B], tmp953
	sub	a2, a2, a7	# _964, tmp953, _968
	srai	a9, a2, 16	# tmp957, _964,
	extui	a8, a2, 0, 16	# tmp971, _964,
	slli	a5, a9, 9	# tmp960, tmp957,
	slli	a2, a8, 9	# tmp973, tmp971,
	sub	a5, a5, a9	# tmp962, tmp960, tmp957
	sub	a2, a2, a8	# tmp974, tmp973, tmp971
	slli	a5, a5, 3	# tmp964, tmp962,
	slli	a2, a2, 3	# tmp975, tmp974,
	sub	a5, a5, a9	# tmp966, tmp964, tmp957
	sub	a2, a2, a8	# tmp976, tmp975, tmp971
	slli	a5, a5, 2	# tmp968, tmp966,
	slli	a2, a2, 2	# tmp977, tmp976,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp970, _968, tmp968
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp978, tmp977,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp981, tmp970, tmp978
	s16i	a2, a3, 226	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2786B], tmp981
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 6, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 228	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2788B], _950
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a10, 56	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1080B], tmp986
	sub	a2, a2, a7	# _946, tmp986, _950
	srai	a9, a2, 16	# tmp990, _946,
	extui	a8, a2, 0, 16	# tmp1004, _946,
	slli	a5, a9, 9	# tmp993, tmp990,
	slli	a2, a8, 9	# tmp1006, tmp1004,
	sub	a5, a5, a9	# tmp995, tmp993, tmp990
	sub	a2, a2, a8	# tmp1007, tmp1006, tmp1004
	slli	a5, a5, 3	# tmp997, tmp995,
	slli	a2, a2, 3	# tmp1008, tmp1007,
	sub	a5, a5, a9	# tmp999, tmp997, tmp990
	sub	a2, a2, a8	# tmp1009, tmp1008, tmp1004
	slli	a5, a5, 2	# tmp1001, tmp999,
	slli	a2, a2, 2	# tmp1010, tmp1009,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp1003, _950, tmp1001
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1011, tmp1010,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp1014, tmp1003, tmp1011
	s16i	a2, a3, 228	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2788B], tmp1014
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 7, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 230	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2790B], _932
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a10, 58	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1082B], tmp1019
	sub	a2, a2, a7	# _928, tmp1019, _932
	srai	a9, a2, 16	# tmp1023, _928,
	extui	a8, a2, 0, 16	# tmp1037, _928,
	slli	a5, a9, 9	# tmp1026, tmp1023,
	slli	a2, a8, 9	# tmp1039, tmp1037,
	sub	a5, a5, a9	# tmp1028, tmp1026, tmp1023
	sub	a2, a2, a8	# tmp1040, tmp1039, tmp1037
	slli	a5, a5, 3	# tmp1030, tmp1028,
	slli	a2, a2, 3	# tmp1041, tmp1040,
	sub	a5, a5, a9	# tmp1032, tmp1030, tmp1023
	sub	a2, a2, a8	# tmp1042, tmp1041, tmp1037
	slli	a5, a5, 2	# tmp1034, tmp1032,
	slli	a2, a2, 2	# tmp1043, tmp1042,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp1036, _932, tmp1034
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1044, tmp1043,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp1047, tmp1036, tmp1044
	s16i	a2, a3, 230	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2790B], tmp1047
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 8, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a8, a3, 232	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2792B], _914
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a10, 60	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1084B], tmp1052
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a10, 9	# tmp1081,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	sub	a7, a7, a8	# _910, tmp1052, _914
	srai	a9, a7, 16	# tmp1056, _910,
	extui	a7, a7, 0, 16	# tmp1070, _910,
	ssl	a10	#
	sll	a5, a9	# tmp1059, tmp1056
	ssl	a10	#
	sll	a2, a7	# tmp1072, tmp1070
	sub	a5, a5, a9	# tmp1061, tmp1059, tmp1056
	sub	a2, a2, a7	# tmp1073, tmp1072, tmp1070
	slli	a5, a5, 3	# tmp1063, tmp1061,
	slli	a2, a2, 3	# tmp1074, tmp1073,
	sub	a5, a5, a9	# tmp1065, tmp1063, tmp1056
	sub	a2, a2, a7	# tmp1075, tmp1074, tmp1070
	slli	a5, a5, 2	# tmp1067, tmp1065,
	slli	a2, a2, 2	# tmp1076, tmp1075,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a8, a8, a5	# tmp1069, _914, tmp1067
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1077, tmp1076,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a8, a2	# tmp1080, tmp1069, tmp1077
	s16i	a2, a3, 232	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2792B], tmp1080
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a10, .L43	# pretmp_1202, tmp1081,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l32i.n	a11, sp, 56	# %sfp,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 234	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2794B], _896
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a11, 62	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1086B], tmp1086
	sub	a2, a2, a7	# _892, tmp1086, _896
	srai	a9, a2, 16	# tmp1090, _892,
	extui	a8, a2, 0, 16	# tmp1104, _892,
	ssl	a10	#
	sll	a5, a9	# tmp1093, tmp1090
	ssl	a10	#
	sll	a2, a8	# tmp1106, tmp1104
	sub	a5, a5, a9	# tmp1095, tmp1093, tmp1090
	sub	a2, a2, a8	# tmp1107, tmp1106, tmp1104
	slli	a5, a5, 3	# tmp1097, tmp1095,
	slli	a2, a2, 3	# tmp1108, tmp1107,
	sub	a5, a5, a9	# tmp1099, tmp1097, tmp1090
	sub	a2, a2, a8	# tmp1109, tmp1108, tmp1104
	slli	a5, a5, 2	# tmp1101, tmp1099,
	slli	a2, a2, 2	# tmp1110, tmp1109,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp1103, _896, tmp1101
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1111, tmp1110,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp1114, tmp1103, tmp1111
	s16i	a2, a3, 234	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2794B], tmp1114
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 10, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a8, a3, 236	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2796B], _878
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a11, 64	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1088B], tmp1119
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a10, 0xb	# tmp1148,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	sub	a7, a7, a8	# _874, tmp1119, _878
	srai	a9, a7, 16	# tmp1123, _874,
	extui	a7, a7, 0, 16	# tmp1137, _874,
	slli	a5, a9, 9	# tmp1126, tmp1123,
	slli	a2, a7, 9	# tmp1139, tmp1137,
	sub	a5, a5, a9	# tmp1128, tmp1126, tmp1123
	sub	a2, a2, a7	# tmp1140, tmp1139, tmp1137
	slli	a5, a5, 3	# tmp1130, tmp1128,
	slli	a2, a2, 3	# tmp1141, tmp1140,
	sub	a5, a5, a9	# tmp1132, tmp1130, tmp1123
	sub	a2, a2, a7	# tmp1142, tmp1141, tmp1137
	slli	a5, a5, 2	# tmp1134, tmp1132,
	slli	a2, a2, 2	# tmp1143, tmp1142,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a8, a8, a5	# tmp1136, _878, tmp1134
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1144, tmp1143,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a8, a2	# tmp1147, tmp1136, tmp1144
	s16i	a2, a3, 236	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2796B], tmp1147
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a10, .L43	# pretmp_1202, tmp1148,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a3, 238	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2798B], _860
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a2, a11, 66	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1090B], tmp1153
	sub	a2, a2, a7	# _856, tmp1153, _860
	srai	a9, a2, 16	# tmp1157, _856,
	extui	a8, a2, 0, 16	# tmp1171, _856,
	slli	a5, a9, 9	# tmp1160, tmp1157,
	slli	a2, a8, 9	# tmp1173, tmp1171,
	sub	a5, a5, a9	# tmp1162, tmp1160, tmp1157
	sub	a2, a2, a8	# tmp1174, tmp1173, tmp1171
	slli	a5, a5, 3	# tmp1164, tmp1162,
	slli	a2, a2, 3	# tmp1175, tmp1174,
	sub	a5, a5, a9	# tmp1166, tmp1164, tmp1157
	sub	a2, a2, a8	# tmp1176, tmp1175, tmp1171
	slli	a5, a5, 2	# tmp1168, tmp1166,
	slli	a2, a2, 2	# tmp1177, tmp1176,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a5, a7, a5	# tmp1170, _860, tmp1168
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1178, tmp1177,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a5, a2	# tmp1181, tmp1170, tmp1178
	s16i	a2, a3, 238	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2798B], tmp1181
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 12, .L43	# pretmp_1202,,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a8, a3, 240	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2800B], _842
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a11, 68	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1092B], tmp1186
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a10, 0xd	# tmp1215,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	sub	a7, a7, a8	# _838, tmp1186, _842
	srai	a9, a7, 16	# tmp1190, _838,
	extui	a7, a7, 0, 16	# tmp1204, _838,
	slli	a5, a9, 9	# tmp1193, tmp1190,
	slli	a2, a7, 9	# tmp1206, tmp1204,
	sub	a5, a5, a9	# tmp1195, tmp1193, tmp1190
	sub	a2, a2, a7	# tmp1207, tmp1206, tmp1204
	slli	a5, a5, 3	# tmp1197, tmp1195,
	slli	a2, a2, 3	# tmp1208, tmp1207,
	sub	a5, a5, a9	# tmp1199, tmp1197, tmp1190
	sub	a2, a2, a7	# tmp1209, tmp1208, tmp1204
	slli	a5, a5, 2	# tmp1201, tmp1199,
	slli	a2, a2, 2	# tmp1210, tmp1209,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a8, a8, a5	# tmp1203, _842, tmp1201
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1211, tmp1210,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a8, a2	# tmp1214, tmp1203, tmp1211
	s16i	a2, a3, 240	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2800B], tmp1214
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a10, .L43	# pretmp_1202, tmp1215,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a8, a3, 242	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2802B], _824
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a11, 70	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1094B], tmp1220
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a10, 0xe	# tmp1249,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	sub	a7, a7, a8	# _820, tmp1220, _824
	srai	a9, a7, 16	# tmp1224, _820,
	extui	a7, a7, 0, 16	# tmp1238, _820,
	slli	a5, a9, 9	# tmp1227, tmp1224,
	slli	a2, a7, 9	# tmp1240, tmp1238,
	sub	a5, a5, a9	# tmp1229, tmp1227, tmp1224
	sub	a2, a2, a7	# tmp1241, tmp1240, tmp1238
	slli	a5, a5, 3	# tmp1231, tmp1229,
	slli	a2, a2, 3	# tmp1242, tmp1241,
	sub	a5, a5, a9	# tmp1233, tmp1231, tmp1224
	sub	a2, a2, a7	# tmp1243, tmp1242, tmp1238
	slli	a5, a5, 2	# tmp1235, tmp1233,
	slli	a2, a2, 2	# tmp1244, tmp1243,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a8, a8, a5	# tmp1237, _824, tmp1235
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1245, tmp1244,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a8, a2	# tmp1248, tmp1237, tmp1245
	s16i	a2, a3, 242	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2802B], tmp1248
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a10, .L43	# pretmp_1202, tmp1249,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a8, a3, 244	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2804B], _806
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a7, a11, 72	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1096B], tmp1254
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a10, 0xf	# tmp1283,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	sub	a7, a7, a8	# _802, tmp1254, _806
	srai	a9, a7, 16	# tmp1258, _802,
	extui	a7, a7, 0, 16	# tmp1272, _802,
	slli	a5, a9, 9	# tmp1261, tmp1258,
	slli	a2, a7, 9	# tmp1274, tmp1272,
	sub	a5, a5, a9	# tmp1263, tmp1261, tmp1258
	sub	a2, a2, a7	# tmp1275, tmp1274, tmp1272
	slli	a5, a5, 3	# tmp1265, tmp1263,
	slli	a2, a2, 3	# tmp1276, tmp1275,
	sub	a5, a5, a9	# tmp1267, tmp1265, tmp1258
	sub	a2, a2, a7	# tmp1277, tmp1276, tmp1272
	slli	a5, a5, 2	# tmp1269, tmp1267,
	slli	a2, a2, 2	# tmp1278, tmp1277,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a8, a8, a5	# tmp1271, _806, tmp1269
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	srai	a2, a2, 16	# tmp1279, tmp1278,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a2, a8, a2	# tmp1282, tmp1271, tmp1279
	s16i	a2, a3, 244	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2804B], tmp1282
# @OPUS@\upstream\silk\CNG.c:102:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a10, .L43	# pretmp_1202, tmp1283,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a4, a3, 246	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2806B], _6
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	l16si	a5, a11, 74	# MEM[(struct silk_decoder_state *)psDec_382(D) + 1098B], tmp1288
	sub	a5, a5, a4	# _10, tmp1288, _6
	extui	a7, a5, 0, 16	# tmp1292, _10,
	srai	a5, a5, 16	# tmp1300, _10,
	slli	a8, a5, 9	# tmp1303, tmp1300,
	slli	a2, a7, 9	# tmp1294, tmp1292,
	sub	a8, a8, a5	# tmp1305, tmp1303, tmp1300
	sub	a2, a2, a7	# tmp1295, tmp1294, tmp1292
	slli	a2, a2, 3	# tmp1296, tmp1295,
	slli	a8, a8, 3	# tmp1307, tmp1305,
	sub	a2, a2, a7	# tmp1297, tmp1296, tmp1292
	sub	a5, a8, a5	# tmp1309, tmp1307, tmp1300
	slli	a2, a2, 2	# tmp1298, tmp1297,
	slli	a5, a5, 2	# tmp1311, tmp1309,
	srai	a2, a2, 16	# tmp1299, tmp1298,
# @OPUS@\upstream\silk\CNG.c:103:             psCNG->CNG_smth_NLSF_Q15[ i ] += silk_SMULWB( (opus_int32)psDec->prevNLSF_Q15[ i ] - (opus_int32)psCNG->CNG_smth_NLSF_Q15[ i ], CNG_NLSF_SMTH_Q16 );
	add.n	a4, a4, a5	# tmp1313, _6, tmp1311
	add.n	a2, a2, a4	# tmp1316, tmp1299, tmp1313
	s16i	a2, a3, 246	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 2806B], tmp1316
	j	.L43		#
.L41:
	l32i.n	a6, sp, 52	# %sfp,
	movi.n	a3, 0	# max_Gain_Q16,
	l32i.n	a4, a6, 16	# psDecCtrl_389(D)->Gains_Q16, psDecCtrl_389(D)->Gains_Q16
	bge	a3, a4, .L44	# max_Gain_Q16, psDecCtrl_389(D)->Gains_Q16,
	mov.n	a3, a4	# max_Gain_Q16, psDecCtrl_389(D)->Gains_Q16
.L44:
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	beqi	a2, 1, .L42	# _533,,
# @OPUS@\upstream\silk\CNG.c:109:             if( psDecCtrl->Gains_Q16[ i ] > max_Gain_Q16 ) {
	l32i.n	a7, sp, 52	# %sfp,
	l32i.n	a4, a7, 20	# psDecCtrl_389(D)->Gains_Q16, _1213
# @OPUS@\upstream\silk\CNG.c:109:             if( psDecCtrl->Gains_Q16[ i ] > max_Gain_Q16 ) {
	bge	a3, a4, .L46	# max_Gain_Q16, _1213,
	mov.n	a3, a4	# max_Gain_Q16, _1213
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	movi.n	a14, 1	# subfr,
.L46:
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	beqi	a2, 2, .L42	# _533,,
# @OPUS@\upstream\silk\CNG.c:109:             if( psDecCtrl->Gains_Q16[ i ] > max_Gain_Q16 ) {
	l32i.n	a8, sp, 52	# %sfp,
	l32i.n	a4, a8, 24	# psDecCtrl_389(D)->Gains_Q16, _497
# @OPUS@\upstream\silk\CNG.c:109:             if( psDecCtrl->Gains_Q16[ i ] > max_Gain_Q16 ) {
	bge	a3, a4, .L47	# max_Gain_Q16, _497,
	mov.n	a3, a4	# max_Gain_Q16, _497
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	movi.n	a14, 2	# subfr,
.L47:
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	beqi	a2, 3, .L42	# _533,,
# @OPUS@\upstream\silk\CNG.c:109:             if( psDecCtrl->Gains_Q16[ i ] > max_Gain_Q16 ) {
	l32i.n	a9, sp, 52	# %sfp,
	l32i.n	a4, a9, 28	# psDecCtrl_389(D)->Gains_Q16, psDecCtrl_389(D)->Gains_Q16
	bge	a3, a4, .L42	# max_Gain_Q16, psDecCtrl_389(D)->Gains_Q16,
# @OPUS@\upstream\silk\CNG.c:108:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	movi.n	a14, 3	# subfr,
.L42:
# @OPUS@\upstream\silk\CNG.c:115:         silk_memmove( &psCNG->CNG_exc_buf_Q14[ psDec->subfr_length ], psCNG->CNG_exc_buf_Q14, ( psDec->nb_subfr - 1 ) * psDec->subfr_length * sizeof( opus_int32 ) );
	l32i.n	a10, sp, 56	# %sfp,
	addi.n	a2, a2, -1	# tmp1323, _533,
	l32i.n	a8, a10, 32	# psDec_382(D)->subfr_length, _23
	movi	a7, 0x5d8	# tmp1322,
	mull	a4, a2, a8	# tmp1324, tmp1323, _23
	add.n	a7, a13, a7	# _20, psDec, tmp1322
	slli	a2, a8, 2	# tmp1326, _23,
	mov.n	a3, a7	#, _20
	slli	a4, a4, 2	#, tmp1324,
	add.n	a2, a7, a2	#, _20, tmp1326
	s32i	a7, sp, 160	#,
	s32i	a8, sp, 156	#,
	call0	memmove		#
# @OPUS@\upstream\silk\CNG.c:117:         yoradio_opus_copy(psCNG->CNG_exc_buf_Q14, &psDec->exc_Q14[subfr * psDec->subfr_length], psDec->subfr_length, sizeof(opus_int32));
	l32i	a8, sp, 156	#,
# @OPUS@\upstream\silk\CNG.c:117:         yoradio_opus_copy(psCNG->CNG_exc_buf_Q14, &psDec->exc_Q14[subfr * psDec->subfr_length], psDec->subfr_length, sizeof(opus_int32));
	l32i	a7, sp, 160	#,
# @OPUS@\upstream\silk\CNG.c:117:         yoradio_opus_copy(psCNG->CNG_exc_buf_Q14, &psDec->exc_Q14[subfr * psDec->subfr_length], psDec->subfr_length, sizeof(opus_int32));
	mull	a14, a8, a14	# tmp1328, _23, subfr
# @OPUS@\upstream\silk\CNG.c:117:         yoradio_opus_copy(psCNG->CNG_exc_buf_Q14, &psDec->exc_Q14[subfr * psDec->subfr_length], psDec->subfr_length, sizeof(opus_int32));
	l32i.n	a3, a13, 0	# psDec_382(D)->exc_Q14, psDec_382(D)->exc_Q14
# @OPUS@\upstream\silk\CNG.c:117:         yoradio_opus_copy(psCNG->CNG_exc_buf_Q14, &psDec->exc_Q14[subfr * psDec->subfr_length], psDec->subfr_length, sizeof(opus_int32));
	slli	a14, a14, 2	# tmp1329, tmp1328,
# @OPUS@\upstream\silk\CNG.c:117:         yoradio_opus_copy(psCNG->CNG_exc_buf_Q14, &psDec->exc_Q14[subfr * psDec->subfr_length], psDec->subfr_length, sizeof(opus_int32));
	mov.n	a4, a8	#, _23
	mov.n	a2, a7	#, _20
	movi.n	a5, 4	#,
	add.n	a3, a3, a14	#, psDec_382(D)->exc_Q14, tmp1329
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	l32i.n	a11, sp, 56	# %sfp,
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	l32i	a7, sp, 160	#,
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	l32i.n	a4, a11, 24	# psDec_382(D)->nb_subfr, _323
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	blti	a4, 1, .L49	# _323,,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	l32i.n	a6, sp, 52	# %sfp,
	addmi	a7, a7, 0x500	# tmp1336, _20,
	l32i	a8, a7, 96	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].CNG_smth_Gain_Q16, psDec__CNG_smth_Gain_Q16_lsm$72
	l32i.n	a3, a6, 16	# psDecCtrl_389(D)->Gains_Q16, psDec__CNG_smth_Gain_Q16_lsm$72
	l32r	a5, .LC10	#, tmp1750
	sub	a2, a3, a8	# _557, psDec__CNG_smth_Gain_Q16_lsm$72, psDec__CNG_smth_Gain_Q16_lsm$72
	extui	a7, a2, 0, 16	# tmp1337, _557,
	srai	a2, a2, 16	# tmp1341, _557,
	mull	a7, a7, a5	# tmp1338, tmp1337, tmp1750
	mull	a2, a2, a5	# tmp1342, tmp1341, tmp1750
	srai	a7, a7, 16	# tmp1340, tmp1338,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	add.n	a2, a2, a8	# tmp1344, tmp1342, psDec__CNG_smth_Gain_Q16_lsm$72
	add.n	a2, a7, a2	# _45, tmp1340, tmp1344
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	l32r	a8, .LC11	#, tmp1751
	extui	a7, a2, 0, 16	# tmp1345, _45,
	srai	a9, a2, 16	# tmp1349, _45,
	mull	a7, a7, a8	# tmp1346, tmp1345, tmp1751
	mull	a9, a9, a8	# tmp1350, tmp1349, tmp1751
	srai	a7, a7, 16	# tmp1348, tmp1346,
	add.n	a9, a9, a2	# tmp1352, tmp1350, _45
	add.n	a7, a7, a9	# tmp1353, tmp1348, tmp1352
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	blt	a3, a7, .L50	# psDec__CNG_smth_Gain_Q16_lsm$72, tmp1353,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	mov.n	a3, a2	# psDec__CNG_smth_Gain_Q16_lsm$72, _45
.L50:
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	beqi	a4, 1, .L51	# _323,,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	l32i.n	a9, sp, 52	# %sfp,
	l32i.n	a7, a9, 20	# psDecCtrl_389(D)->Gains_Q16, psDec__CNG_smth_Gain_Q16_lsm$72
	sub	a2, a7, a3	# _543, psDec__CNG_smth_Gain_Q16_lsm$72, psDec__CNG_smth_Gain_Q16_lsm$72
	extui	a9, a2, 0, 16	# tmp1354, _543,
	srai	a2, a2, 16	# tmp1358, _543,
	mull	a2, a2, a5	# tmp1359, tmp1358, tmp1750
	mull	a9, a9, a5	# tmp1355, tmp1354, tmp1750
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	add.n	a3, a2, a3	# tmp1361, tmp1359, psDec__CNG_smth_Gain_Q16_lsm$72
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	srai	a9, a9, 16	# tmp1357, tmp1355,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	add.n	a3, a9, a3	# _1149, tmp1357, tmp1361
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	extui	a2, a3, 0, 16	# tmp1362, _1149,
	srai	a9, a3, 16	# tmp1366, _1149,
	mull	a2, a2, a8	# tmp1363, tmp1362, tmp1751
	mull	a9, a9, a8	# tmp1367, tmp1366, tmp1751
	srai	a2, a2, 16	# tmp1365, tmp1363,
	add.n	a9, a9, a3	# tmp1369, tmp1367, _1149
	add.n	a2, a2, a9	# tmp1370, tmp1365, tmp1369
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	blt	a7, a2, .L52	# psDec__CNG_smth_Gain_Q16_lsm$72, tmp1370,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	mov.n	a7, a3	# psDec__CNG_smth_Gain_Q16_lsm$72, _1149
.L52:
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	beqi	a4, 2, .L91	# _323,,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	l32i.n	a10, sp, 52	# %sfp,
	l32i.n	a9, a10, 24	# psDecCtrl_389(D)->Gains_Q16, psDec__CNG_smth_Gain_Q16_lsm$72
	sub	a2, a9, a7	# _1198, psDec__CNG_smth_Gain_Q16_lsm$72, psDec__CNG_smth_Gain_Q16_lsm$72
	extui	a3, a2, 0, 16	# tmp1371, _1198,
	srai	a2, a2, 16	# tmp1375, _1198,
	mull	a2, a2, a5	# tmp1376, tmp1375, tmp1750
	mull	a3, a3, a5	# tmp1372, tmp1371, tmp1750
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	add.n	a7, a2, a7	# tmp1378, tmp1376, psDec__CNG_smth_Gain_Q16_lsm$72
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	srai	a3, a3, 16	# tmp1374, tmp1372,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	add.n	a7, a3, a7	# _1178, tmp1374, tmp1378
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	extui	a2, a7, 0, 16	# tmp1379, _1178,
	srai	a3, a7, 16	# tmp1383, _1178,
	mull	a2, a2, a8	# tmp1380, tmp1379, tmp1751
	mull	a3, a3, a8	# tmp1384, tmp1383, tmp1751
	srai	a2, a2, 16	# tmp1382, tmp1380,
	add.n	a3, a3, a7	# tmp1386, tmp1384, _1178
	add.n	a2, a2, a3	# tmp1387, tmp1382, tmp1386
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	blt	a9, a2, .L53	# psDec__CNG_smth_Gain_Q16_lsm$72, tmp1387,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	mov.n	a9, a7	# psDec__CNG_smth_Gain_Q16_lsm$72, _1178
.L53:
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	beqi	a4, 3, .L92	# _323,,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	l32i.n	a11, sp, 52	# %sfp,
	l32i.n	a3, a11, 28	# psDecCtrl_389(D)->Gains_Q16, psDec__CNG_smth_Gain_Q16_lsm$72
	sub	a2, a3, a9	# _1142, psDec__CNG_smth_Gain_Q16_lsm$72, psDec__CNG_smth_Gain_Q16_lsm$72
	srai	a4, a2, 16	# tmp1388, _1142,
	extui	a2, a2, 0, 16	# tmp1392, _1142,
	mull	a4, a4, a5	# tmp1389, tmp1388, tmp1750
	mull	a5, a2, a5	# tmp1393, tmp1392, tmp1750
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	add.n	a9, a4, a9	# tmp1391, tmp1389, psDec__CNG_smth_Gain_Q16_lsm$72
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	srai	a5, a5, 16	# tmp1395, tmp1393,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	add.n	a5, a9, a5	# _1115, tmp1391, tmp1395
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	srai	a2, a5, 16	# tmp1396, _1115,
	extui	a4, a5, 0, 16	# tmp1400, _1115,
	mull	a2, a2, a8	# tmp1397, tmp1396, tmp1751
	mull	a8, a4, a8	# tmp1401, tmp1400, tmp1751
	add.n	a2, a2, a5	# tmp1399, tmp1397, _1115
	srai	a8, a8, 16	# tmp1403, tmp1401,
	add.n	a2, a2, a8	# tmp1404, tmp1399, tmp1403
# @OPUS@\upstream\silk\CNG.c:126:             if( silk_SMULWW( psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_THRESHOLD_Q16 ) > psDecCtrl->Gains_Q16[ i ] ) {
	blt	a3, a2, .L51	# psDec__CNG_smth_Gain_Q16_lsm$72, tmp1404,
# @OPUS@\upstream\silk\CNG.c:124:             psCNG->CNG_smth_Gain_Q16 += silk_SMULWB( psDecCtrl->Gains_Q16[ i ] - psCNG->CNG_smth_Gain_Q16, CNG_GAIN_SMTH_Q16 );
	mov.n	a3, a5	# psDec__CNG_smth_Gain_Q16_lsm$72, _1115
	j	.L51		#
.L91:
# @OPUS@\upstream\silk\CNG.c:123:         for( i = 0; i < psDec->nb_subfr; i++ ) {
	mov.n	a3, a7	# psDec__CNG_smth_Gain_Q16_lsm$72, psDec__CNG_smth_Gain_Q16_lsm$72
	j	.L51		#
.L92:
	mov.n	a3, a9	# psDec__CNG_smth_Gain_Q16_lsm$72, psDec__CNG_smth_Gain_Q16_lsm$72
.L51:
	movi	a2, 0x5d8	# tmp1406,
	add.n	a2, a13, a2	# tmp1407, psDec, tmp1406
	addmi	a2, a2, 0x500	# tmp1408, tmp1407,
	s32i	a3, a2, 96	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].CNG_smth_Gain_Q16, psDec__CNG_smth_Gain_Q16_lsm$72
.L49:
# @OPUS@\upstream\silk\CNG.c:133:     if( psDec->lossCnt ) {
	l32i	a2, a12, 68	# psDec_382(D)->lossCnt, psDec_382(D)->lossCnt
	bnez.n	a2, .L38	# psDec_382(D)->lossCnt,
	l32i.n	a12, sp, 56	# %sfp,
	l32i.n	a4, a12, 40	# psDec_382(D)->LPC_order, pretmp_1202
	j	.L39		#
.L38:
# @OPUS@\upstream\silk\CNG.c:135:         ALLOC( CNG_sig_Q14, length + MAX_LPC_ORDER, opus_int32 );
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	addi	a2, a15, 16	#, length,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\CNG.c:138:         gain_Q16 = silk_SMULWW( psDec->sPLC.randScale_Q14, psDec->sPLC.prevGain_Q16[1] );
	l16ui	a3, a12, 136	# psDec_382(D)->sPLC.randScale_Q14,
# @OPUS@\upstream\silk\CNG.c:135:         ALLOC( CNG_sig_Q14, length + MAX_LPC_ORDER, opus_int32 );
	s32i	a2, sp, 112	# %sfp,
# @OPUS@\upstream\silk\CNG.c:138:         gain_Q16 = silk_SMULWW( psDec->sPLC.randScale_Q14, psDec->sPLC.prevGain_Q16[1] );
	l32i	a2, a12, 156	# psDec_382(D)->sPLC.prevGain_Q16, _63
	slli	a3, a3, 16	# tmp1415, psDec_382(D)->sPLC.randScale_Q14,
	srai	a7, a3, 16	# _61, tmp1415,
	l16si	a4, a12, 156	# psDec_382(D)->sPLC.prevGain_Q16, _65
	srai	a2, a2, 15	# tmp1418, _63,
	addi.n	a2, a2, 1	# tmp1419, tmp1418,
	extui	a5, a7, 0, 16	# tmp1422, _61,
	mull	a5, a5, a4	# tmp1423, tmp1422, _65
	srai	a2, a2, 1	# tmp1420, tmp1419,
	mull	a2, a2, a7	# tmp1421, tmp1420, _61
	srai	a3, a3, 31	# tmp1426, tmp1415,
	mull	a3, a3, a4	# tmp1427, tmp1426, _65
	srai	a5, a5, 16	# tmp1424, tmp1423,
# @OPUS@\upstream\silk\CNG.c:138:         gain_Q16 = silk_SMULWW( psDec->sPLC.randScale_Q14, psDec->sPLC.prevGain_Q16[1] );
	add.n	a2, a2, a5	# tmp1425, tmp1421, tmp1424
# @OPUS@\upstream\silk\CNG.c:139:         if( gain_Q16 >= (1 << 21) || psCNG->CNG_smth_Gain_Q16 > (1 << 23) ) {
	l32r	a4, .LC12	#, tmp1428
# @OPUS@\upstream\silk\CNG.c:138:         gain_Q16 = silk_SMULWW( psDec->sPLC.randScale_Q14, psDec->sPLC.prevGain_Q16[1] );
	add.n	a2, a2, a3	# gain_Q16, tmp1425, tmp1427
	srai	a3, a2, 16	# _1227, gain_Q16,
# @OPUS@\upstream\silk\CNG.c:139:         if( gain_Q16 >= (1 << 21) || psCNG->CNG_smth_Gain_Q16 > (1 << 23) ) {
	bge	a4, a2, .L55	# tmp1428, gain_Q16,
	movi	a2, 0x5d8	# tmp1430,
	add.n	a2, a13, a2	# tmp1431, psDec, tmp1430
	addmi	a2, a2, 0x500	# tmp1432, tmp1431,
	l16si	a4, a2, 98	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].CNG_smth_Gain_Q16, _1247
	j	.L56		#
.L55:
# @OPUS@\upstream\silk\CNG.c:139:         if( gain_Q16 >= (1 << 21) || psCNG->CNG_smth_Gain_Q16 > (1 << 23) ) {
	movi	a4, 0x5d8	# tmp1435,
	add.n	a4, a13, a4	# tmp1436, psDec, tmp1435
	addmi	a4, a4, 0x500	# tmp1437, tmp1436,
	l32i	a7, a4, 96	# MEM[(struct silk_CNG_struct *)psDec_382(D) + 1496B].CNG_smth_Gain_Q16, _75
# @OPUS@\upstream\silk\CNG.c:139:         if( gain_Q16 >= (1 << 21) || psCNG->CNG_smth_Gain_Q16 > (1 << 23) ) {
	l32r	a5, .LC13	#, tmp1438
	srai	a4, a7, 16	# _1247, _75,
	bge	a5, a7, .L57	# tmp1438, _75,
.L56:
# @OPUS@\upstream\silk\CNG.c:140:             gain_Q16 = silk_SMULTT( gain_Q16, gain_Q16 );
	mull	a3, a3, a3	# gain_Q16, _1227, _1227
# @OPUS@\upstream\silk\CNG.c:141:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULTT( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	mull	a4, a4, a4	# tmp1440, _1247, _1247
	slli	a3, a3, 5	# _82, gain_Q16,
# @OPUS@\upstream\silk\CNG.c:141:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULTT( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	sub	a4, a4, a3	# gain_Q16, tmp1440, _82
# @OPUS@\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	blti	a4, 1, .L95	# gain_Q16,,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a3, a4	# iftmp$67_478, gain_Q16
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a5, 0x18	# tmp1441,
	sub	a5, a5, a3	# _479, tmp1441, iftmp$67_478
# @OPUS@\upstream\silk\SigProc_FIX.h:403:     if( rot == 0 ) {
	beqz.n	a5, .L59	# _479,
# @OPUS@\upstream\silk\SigProc_FIX.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a5	# _479
	src	a2, a4, a4	# _487, gain_Q16
# @OPUS@\upstream\silk\SigProc_FIX.h:405:     } else if( rot < 0 ) {
	bgez	a5, .L61	# _479,
# @OPUS@\upstream\silk\SigProc_FIX.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a2, a3, -24	# m, iftmp$67_478,
# @OPUS@\upstream\silk\SigProc_FIX.h:406:         return (opus_int32) ((x << m) | (x >> (32 - m)));
	ssl	a2	# m
	src	a2, a4, a4	# _487, gain_Q16
.L61:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a4, a2, 0, 7	# _489, _487,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a7, .LC2	#, tmp1774
	l32r	a2, .LC3	#, tmp1775
# @OPUS@\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	extui	a5, a3, 0, 1	# tmp1443, iftmp$67_478,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	moveqz	a2, a7, a5	# tmp1775, tmp1774, tmp1443
	mov.n	a5, a2	# y, tmp1775
.L62:
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a2, a4, 3	# tmp1447, _489,
	add.n	a2, a4, a2	# tmp1449, _489, tmp1447
	slli	a2, a2, 3	# tmp1451, tmp1449,
	sub	a4, a2, a4	# tmp1453, tmp1451, _489
	slli	a2, a4, 2	# tmp1455, tmp1453,
	sub	a2, a2, a4	# tmp1458, tmp1455, tmp1453
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	srai	a3, a3, 1	# tmp1444, iftmp$67_478,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a2, a2, 16	# tmp1460, tmp1458,
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	ssr	a3	# tmp1444
	sra	a5, a5	# y, y
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a2, a2, 16	# tmp1459, tmp1460,
	mull	a2, a2, a5	# tmp1461, tmp1459, y
	srai	a2, a2, 16	# _499, tmp1461,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	add.n	a5, a5, a2	# y, y, _499
	slli	a5, a5, 16	#, y,
	s32i.n	a5, sp, 52	# %sfp,
	srai	a11, a5, 6	# prephitmp_1165,,
	j	.L63		#
.L57:
# @OPUS@\upstream\silk\CNG.c:144:             gain_Q16 = silk_SMULWW( gain_Q16, gain_Q16 );
	slli	a5, a2, 16	# tmp1463, gain_Q16,
	srai	a8, a2, 15	# tmp1464, gain_Q16,
	srai	a6, a5, 16	# _88, tmp1463,
	extui	a11, a2, 0, 16	# tmp1468, gain_Q16,
	addi.n	a8, a8, 1	# tmp1465, tmp1464,
# @OPUS@\upstream\silk\CNG.c:145:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULWW( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	slli	a9, a7, 16	# tmp1471, _75,
	srai	a5, a7, 15	# tmp1474, _75,
	srai	a9, a9, 16	# _100, tmp1471,
# @OPUS@\upstream\silk\CNG.c:144:             gain_Q16 = silk_SMULWW( gain_Q16, gain_Q16 );
	srai	a8, a8, 1	# tmp1466, tmp1465,
	mull	a11, a11, a6	# tmp1469, tmp1468, _88
# @OPUS@\upstream\silk\CNG.c:145:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULWW( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	addi.n	a5, a5, 1	# tmp1475, tmp1474,
	extui	a10, a7, 0, 16	# tmp1478, _75,
# @OPUS@\upstream\silk\CNG.c:144:             gain_Q16 = silk_SMULWW( gain_Q16, gain_Q16 );
	mull	a2, a8, a2	# tmp1467, tmp1466, gain_Q16
# @OPUS@\upstream\silk\CNG.c:145:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULWW( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	srai	a5, a5, 1	# tmp1476, tmp1475,
	mull	a10, a10, a9	# tmp1479, tmp1478, _100
# @OPUS@\upstream\silk\CNG.c:144:             gain_Q16 = silk_SMULWW( gain_Q16, gain_Q16 );
	srai	a11, a11, 16	# tmp1470, tmp1469,
	mull	a3, a6, a3	# tmp1472, _88, _1227
# @OPUS@\upstream\silk\CNG.c:145:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULWW( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	mull	a5, a5, a7	# tmp1477, tmp1476, _75
	add.n	a2, a2, a11	# _610, tmp1467, tmp1470
	srai	a10, a10, 16	# tmp1480, tmp1479,
	mull	a4, a9, a4	# tmp1482, _100, _1247
# @OPUS@\upstream\silk\CNG.c:144:             gain_Q16 = silk_SMULWW( gain_Q16, gain_Q16 );
	add.n	a3, a3, a2	# gain_Q16, tmp1472, _610
# @OPUS@\upstream\silk\CNG.c:145:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULWW( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	add.n	a2, a5, a10	# tmp1481, tmp1477, tmp1480
	slli	a3, a3, 5	# _113, gain_Q16,
	add.n	a2, a2, a4	# tmp1483, tmp1481, tmp1482
# @OPUS@\upstream\silk\CNG.c:145:             gain_Q16 = silk_SUB_LSHIFT32(silk_SMULWW( psCNG->CNG_smth_Gain_Q16, psCNG->CNG_smth_Gain_Q16 ), gain_Q16, 5 );
	sub	a2, a2, a3	# gain_Q16, tmp1483, _113
# @OPUS@\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	blti	a2, 1, .L95	# gain_Q16,,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a3, a2	# iftmp$67_504, gain_Q16
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a4, 0x18	# tmp1484,
	sub	a4, a4, a3	# _505, tmp1484, iftmp$67_504
# @OPUS@\upstream\silk\SigProc_FIX.h:403:     if( rot == 0 ) {
	beqz.n	a4, .L65	# _505,
# @OPUS@\upstream\silk\SigProc_FIX.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a4	# _505
	src	a7, a2, a2	# _513, gain_Q16
# @OPUS@\upstream\silk\SigProc_FIX.h:405:     } else if( rot < 0 ) {
	bgez	a4, .L67	# _505,
# @OPUS@\upstream\silk\SigProc_FIX.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a7, a3, -24	# m, iftmp$67_504,
# @OPUS@\upstream\silk\SigProc_FIX.h:406:         return (opus_int32) ((x << m) | (x >> (32 - m)));
	ssl	a7	# m
	src	a7, a2, a2	# _513, gain_Q16
.L67:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a2, a7, 0, 7	# _515, _513,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a4, .LC3	#, tmp1779
	l32r	a7, .LC2	#, tmp1778
# @OPUS@\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	extui	a5, a3, 0, 1	# tmp1486, iftmp$67_504,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	moveqz	a4, a7, a5	# tmp1779, tmp1778, tmp1486
	mov.n	a5, a4	# y, tmp1779
.L68:
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a4, a2, 3	# tmp1490, _515,
	add.n	a4, a2, a4	# tmp1492, _515, tmp1490
	slli	a4, a4, 3	# tmp1494, tmp1492,
	sub	a4, a4, a2	# tmp1496, tmp1494, _515
	slli	a2, a4, 2	# tmp1498, tmp1496,
	sub	a2, a2, a4	# tmp1501, tmp1498, tmp1496
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	srai	a3, a3, 1	# tmp1487, iftmp$67_504,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a2, a2, 16	# tmp1503, tmp1501,
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	ssr	a3	# tmp1487
	sra	a5, a5	# y, y
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a2, a2, 16	# tmp1502, tmp1503,
	mull	a2, a2, a5	# tmp1504, tmp1502, y
	srai	a2, a2, 16	# _525, tmp1504,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	add.n	a5, a5, a2	# y, y, _525
	slli	a5, a5, 8	#, y,
	s32i.n	a5, sp, 52	# %sfp,
	srai	a11, a5, 6	# prephitmp_1165,,
	j	.L63		#
.L95:
# @OPUS@\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	movi.n	a11, 0	# prephitmp_1165,
	s32i.n	a11, sp, 52	# %sfp, prephitmp_1165
.L63:
# @OPUS@\upstream\silk\CNG.c:150:         silk_CNG_exc( CNG_sig_Q14 + MAX_LPC_ORDER, psCNG->CNG_exc_buf_Q14, length, &psCNG->rand_seed );
	movi	a7, 0x5d8	# tmp1506,
# @OPUS@\upstream\silk\CNG.c:47:     while( exc_mask > length ) {
	movi	a2, 0xfe	# tmp1507,
# @OPUS@\upstream\silk\CNG.c:150:         silk_CNG_exc( CNG_sig_Q14 + MAX_LPC_ORDER, psCNG->CNG_exc_buf_Q14, length, &psCNG->rand_seed );
	add.n	a7, a13, a7	# _117, psDec, tmp1506
# @OPUS@\upstream\silk\CNG.c:47:     while( exc_mask > length ) {
	blt	a2, a15, .L69	# tmp1507, length,
# @OPUS@\upstream\silk\CNG.c:46:     exc_mask = CNG_BUF_MASK_MAX;
	movi	a5, 0xff	# exc_mask,
.L70:
# @OPUS@\upstream\silk\CNG.c:48:         exc_mask = silk_RSHIFT( exc_mask, 1 );
	srai	a5, a5, 1	# exc_mask, exc_mask,
# @OPUS@\upstream\silk\CNG.c:47:     while( exc_mask > length ) {
	blt	a15, a5, .L70	# length, exc_mask,
	movi	a3, 0x5d8	# tmp1509,
	add.n	a3, a13, a3	# tmp1510, psDec, tmp1509
	movi	a2, 0x520	# tmp1511,
	add.n	a2, a3, a2	#, tmp1510, tmp1511
	s32i	a2, sp, 144	# %sfp,
# @OPUS@\upstream\silk\CNG.c:51:     seed = *rand_seed;
	l32i.n	a4, a12, 60	# MEM[(opus_int32 *)psDec_382(D) + 2876B], seed
	addmi	a3, a3, 0x500	# pretmp_1012, tmp1510,
# @OPUS@\upstream\silk\CNG.c:52:     for( i = 0; i < length; i++ ) {
	blti	a15, 1, .L71	# length,,
.L90:
	slli	a6, a15, 2	#, length,
	l32i	a2, sp, 112	# %sfp,
	addi	a8, a6, 64	# tmp1514,,
	l32r	a10, .LC14	#, tmp1752
	l32r	a9, .LC15	#, tmp1753
	s32i	a6, sp, 140	# %sfp,
	mov.n	a14, a2	# ivtmp$75,
	addi	a6, a2, 64	# ivtmp$80,,
	add.n	a8, a8, a2	# _648, tmp1514,
.L72:
# @OPUS@\upstream\silk\CNG.c:53:         seed = silk_RAND( seed );
	mull	a4, a4, a10	# tmp1515, seed, tmp1752
	add.n	a4, a4, a9	# seed, tmp1515, tmp1753
# @OPUS@\upstream\silk\CNG.c:54:         idx = (opus_int)( silk_RSHIFT( seed, 24 ) & exc_mask );
	srai	a2, a4, 24	# tmp1518, seed,
# @OPUS@\upstream\silk\CNG.c:54:         idx = (opus_int)( silk_RSHIFT( seed, 24 ) & exc_mask );
	and	a2, a2, a5	# idx, tmp1518, exc_mask
# @OPUS@\upstream\silk\CNG.c:57:         exc_Q14[ i ] = exc_buf_Q14[ idx ];
	slli	a2, a2, 2	# tmp1520, idx,
	add.n	a2, a7, a2	# tmp1521, _117, tmp1520
	l32i.n	a2, a2, 0	# *_463, _468
# @OPUS@\upstream\silk\CNG.c:57:         exc_Q14[ i ] = exc_buf_Q14[ idx ];
	s32i.n	a2, a6, 0	# MEM[base: _653, offset: 0B], _468
	addi.n	a6, a6, 4	# ivtmp$80, ivtmp$80,
# @OPUS@\upstream\silk\CNG.c:52:     for( i = 0; i < length; i++ ) {
	bne	a8, a6, .L72	# _648, ivtmp$80,
	j	.L181		#
.L83:
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	l32i.n	a11, a14, 60	# MEM[base: _666, offset: 60B], _127
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	l32i.n	a10, a14, 56	# MEM[base: _666, offset: 56B], _139
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	l32i.n	a7, sp, 60	# %sfp,
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	l32i	a12, sp, 64	# %sfp,
# @OPUS@\upstream\silk\CNG.c:160:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	l32i.n	a6, sp, 56	# %sfp,
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	srai	a3, a11, 16	# tmp1523, _127,
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	srai	a2, a10, 16	# tmp1525, _139,
# @OPUS@\upstream\silk\CNG.c:160:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	l32i.n	a6, a6, 40	# psDec_382(D)->LPC_order,
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	mull	a2, a2, a12	# tmp1526, tmp1525,
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	mull	a3, a3, a7	# tmp1524, tmp1523,
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	l32i.n	a9, a14, 52	# MEM[base: _666, offset: 52B], _151
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	l32i.n	a8, a14, 48	# MEM[base: _666, offset: 48B], _163
# @OPUS@\upstream\silk\CNG.c:160:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	srai	a5, a6, 1	# LPC_pred_Q10,,
	add.n	a3, a3, a2	# tmp1527, tmp1524, tmp1526
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	l32i	a2, sp, 68	# %sfp,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	l32i.n	a7, a14, 44	# MEM[base: _666, offset: 44B], _175
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	srai	a4, a9, 16	# tmp1530, _151,
	add.n	a3, a3, a5	# tmp1529, tmp1527, LPC_pred_Q10
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	l32i	a5, sp, 72	# %sfp,
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	mull	a4, a4, a2	# tmp1531, tmp1530,
# @OPUS@\upstream\silk\CNG.c:160:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	s32i	a6, sp, 152	# %sfp,
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	srai	a2, a8, 16	# tmp1533, _163,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	l32i	a6, sp, 76	# %sfp,
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	mull	a13, a2, a5	# tmp1534, tmp1533,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	srai	a2, a7, 16	# tmp1536, _175,
	mull	a12, a2, a6	# tmp1537, tmp1536,
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	l32i.n	a2, a14, 40	# MEM[base: _666, offset: 40B],
	add.n	a3, a3, a4	# tmp1532, tmp1529, tmp1531
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	l32i.n	a6, a14, 36	# MEM[base: _666, offset: 36B],
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	srai	a15, a2, 16	# tmp1539,,
	add.n	a2, a3, a13	# tmp1535, tmp1532, tmp1534
	l32i	a3, sp, 80	# %sfp,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	l32i.n	a5, a14, 32	# MEM[base: _666, offset: 32B], _211
	add.n	a2, a2, a12	# tmp1538, tmp1535, tmp1537
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	l32i	a12, sp, 84	# %sfp,
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	mull	a15, a15, a3	# tmp1540, tmp1539,
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	srai	a13, a6, 16	# tmp1542,,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	l32i	a6, sp, 88	# %sfp,
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	mull	a13, a13, a12	# tmp1543, tmp1542,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	srai	a12, a5, 16	# tmp1545, _211,
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	l32i.n	a4, a14, 28	# MEM[base: _666, offset: 28B], _223
	add.n	a2, a2, a15	# tmp1541, tmp1538, tmp1540
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	mull	a12, a12, a6	# tmp1546, tmp1545,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	l32i.n	a3, a14, 24	# MEM[base: _666, offset: 24B], _235
	add.n	a2, a2, a13	# tmp1544, tmp1541, tmp1543
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	l32i	a6, sp, 92	# %sfp,
	srai	a15, a4, 16	# tmp1548, _223,
	add.n	a12, a2, a12	# tmp1547, tmp1544, tmp1546
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	l32i	a2, sp, 96	# %sfp,
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	mull	a13, a15, a6	# tmp1549, tmp1548,
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	l32i.n	a6, sp, 60	# %sfp,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	srai	a15, a3, 16	# tmp1551, _235,
	mull	a15, a15, a2	# tmp1552, tmp1551,
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	extui	a11, a11, 0, 16	# tmp1554, _127,
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	l32i	a2, sp, 64	# %sfp,
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	mull	a11, a11, a6	# tmp1555, tmp1554,
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	extui	a10, a10, 0, 16	# tmp1558, _139,
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	l32i	a6, sp, 68	# %sfp,
	add.n	a12, a12, a13	# tmp1550, tmp1547, tmp1549
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	mull	a10, a10, a2	# tmp1559, tmp1558,
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	extui	a9, a9, 0, 16	# tmp1562, _151,
	add.n	a15, a12, a15	# tmp1553, tmp1550, tmp1552
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	srai	a11, a11, 16	# tmp1556, tmp1555,
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	mull	a9, a9, a6	# tmp1563, tmp1562,
	add.n	a15, a15, a11	# tmp1557, tmp1553, tmp1556
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	srai	a10, a10, 16	# tmp1560, tmp1559,
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	l32i	a11, sp, 72	# %sfp,
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	l32i.n	a6, a14, 40	# MEM[base: _666, offset: 40B],
	add.n	a15, a15, a10	# tmp1561, tmp1557, tmp1560
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	srai	a9, a9, 16	# tmp1564, tmp1563,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	l32i	a12, sp, 76	# %sfp,
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	extui	a8, a8, 0, 16	# tmp1566, _163,
	mull	a8, a8, a11	# tmp1567, tmp1566,
	add.n	a15, a15, a9	# tmp1565, tmp1561, tmp1564
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	l32i.n	a10, a14, 36	# MEM[base: _666, offset: 36B],
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	l32i	a9, sp, 80	# %sfp,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	extui	a7, a7, 0, 16	# tmp1570, _175,
	mull	a7, a7, a12	# tmp1571, tmp1570,
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	extui	a2, a6, 0, 16	# tmp1574,,
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	l32i	a11, sp, 84	# %sfp,
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	srai	a8, a8, 16	# tmp1568, tmp1567,
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	mull	a2, a2, a9	# tmp1575, tmp1574,
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	extui	a6, a10, 0, 16	# tmp1578,,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	srai	a7, a7, 16	# tmp1572, tmp1571,
	add.n	a15, a15, a8	# tmp1569, tmp1565, tmp1568
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	mull	a6, a6, a11	# tmp1579, tmp1578,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	l32i	a12, sp, 88	# %sfp,
	add.n	a15, a15, a7	# tmp1573, tmp1569, tmp1572
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	srai	a2, a2, 16	# tmp1576, tmp1575,
	add.n	a15, a15, a2	# tmp1577, tmp1573, tmp1576
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	srai	a6, a6, 16	# tmp1580, tmp1579,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	extui	a5, a5, 0, 16	# tmp1582, _211,
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	l32i	a2, sp, 92	# %sfp,
	add.n	a15, a15, a6	# tmp1581, tmp1577, tmp1580
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	mull	a5, a5, a12	# tmp1583, tmp1582,
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	extui	a4, a4, 0, 16	# tmp1586, _223,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	l32i	a6, sp, 96	# %sfp,
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	mull	a4, a4, a2	# tmp1587, tmp1586,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	extui	a3, a3, 0, 16	# tmp1589, _235,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	srai	a5, a5, 16	# tmp1584, tmp1583,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	mull	a3, a3, a6	# tmp1590, tmp1589,
	add.n	a15, a15, a5	# tmp1585, tmp1581, tmp1584
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	srai	a4, a4, 16	# tmp1588, tmp1587,
# @OPUS@\upstream\silk\CNG.c:171:             if( psDec->LPC_order == 16 ) {
	l32i	a7, sp, 152	# %sfp,
	add.n	a15, a15, a4	# _608, tmp1585, tmp1588
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	srai	a3, a3, 16	# tmp1591, tmp1590,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	add.n	a3, a3, a15	# LPC_pred_Q10, tmp1591, _608
# @OPUS@\upstream\silk\CNG.c:171:             if( psDec->LPC_order == 16 ) {
	bnei	a7, 16, .L74	#,,
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	l32i.n	a8, a14, 20	# MEM[base: _666, offset: 20B], _247
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	l32i.n	a7, a14, 16	# MEM[base: _666, offset: 16B], _259
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	l32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	l32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	srai	a2, a8, 16	# tmp1592, _247,
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	l32i.n	a6, a14, 12	# MEM[base: _666, offset: 12B], _271
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	srai	a13, a7, 16	# tmp1594, _259,
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	mull	a11, a2, a9	# tmp1593, tmp1592,
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	mull	a13, a13, a10	# tmp1595, tmp1594,
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	l32i	a12, sp, 124	# %sfp,
	srai	a2, a6, 16	# tmp1597, _271,
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	l32i.n	a5, a14, 8	# MEM[base: _666, offset: 8B], _283
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	mull	a10, a2, a12	# tmp1598, tmp1597,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a2, a11, a13	# tmp1596, tmp1593, tmp1595
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	l32i	a11, sp, 128	# %sfp,
	srai	a12, a5, 16	# tmp1600, _283,
	mull	a12, a12, a11	# tmp1601, tmp1600,
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	l32i.n	a4, a14, 4	# MEM[base: _666, offset: 4B], _295
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	l32i.n	a9, a14, 0	# MEM[base: _666, offset: 0B], _306
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a2, a2, a10	# tmp1599, tmp1596, tmp1598
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	l32i	a10, sp, 132	# %sfp,
	srai	a11, a4, 16	# tmp1603, _295,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a2, a2, a12	# tmp1602, tmp1599, tmp1601
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	l32i	a12, sp, 136	# %sfp,
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	mull	a11, a11, a10	# tmp1604, tmp1603,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	srai	a10, a9, 16	# tmp1606, _306,
	mull	a10, a10, a12	# tmp1607, tmp1606,
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	l32i	a12, sp, 116	# %sfp,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a2, a2, a11	# tmp1605, tmp1602, tmp1604
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	extui	a8, a8, 0, 16	# tmp1609, _247,
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	l32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	mull	a8, a8, a12	# tmp1610, tmp1609,
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	extui	a7, a7, 0, 16	# tmp1613, _259,
	mull	a7, a7, a11	# tmp1614, tmp1613,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a2, a2, a10	# tmp1608, tmp1605, tmp1607
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	srai	a8, a8, 16	# tmp1611, tmp1610,
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	l32i	a12, sp, 124	# %sfp,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a8, a2, a8	# tmp1612, tmp1608, tmp1611
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	extui	a6, a6, 0, 16	# tmp1617, _271,
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	srai	a7, a7, 16	# tmp1615, tmp1614,
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	l32i	a2, sp, 128	# %sfp,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a7, a8, a7	# tmp1616, tmp1612, tmp1615
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	mull	a6, a6, a12	# tmp1618, tmp1617,
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	extui	a5, a5, 0, 16	# tmp1621, _283,
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	l32i	a8, sp, 132	# %sfp,
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	mull	a5, a5, a2	# tmp1622, tmp1621,
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	extui	a4, a4, 0, 16	# tmp1625, _295,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	l32i	a10, sp, 136	# %sfp,
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	srai	a6, a6, 16	# tmp1619, tmp1618,
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	mull	a4, a4, a8	# tmp1626, tmp1625,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	extui	a9, a9, 0, 16	# tmp1629, _306,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a6, a7, a6	# tmp1620, tmp1616, tmp1619
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	srai	a5, a5, 16	# tmp1623, tmp1622,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	mull	a9, a9, a10	# tmp1630, tmp1629,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a5, a6, a5	# tmp1624, tmp1620, tmp1623
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	srai	a4, a4, 16	# tmp1627, tmp1626,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a4, a5, a4	# tmp1628, tmp1624, tmp1627
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	srai	a9, a9, 16	# tmp1631, tmp1630,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	add.n	a4, a4, a9	# tmp1632, tmp1628, tmp1631
	add.n	a3, a3, a4	# LPC_pred_Q10, LPC_pred_Q10, tmp1632
.L74:
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	l32r	a11, .LC16	#,
	l32i	a4, a14, 64	# MEM[base: _666, offset: 64B], _319
	blt	a11, a3, .L75	#, LPC_pred_Q10,
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	l32r	a12, .LC17	#,
	blt	a3, a12, .L76	# LPC_pred_Q10,,
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	slli	a3, a3, 4	# iftmp$36_428, LPC_pred_Q10,
	add.n	a5, a4, a3	# tmp1635, _319, iftmp$36_428
	mov.n	a2, a3	# iftmp$46_371, iftmp$36_428
	bltz	a5, .L86	# tmp1635,
.L87:
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	and	a2, a4, a3	# tmp1636, _319, iftmp$39_370
	bltz	a2, .L97	# tmp1636,
.L85:
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	add.n	a3, a4, a3	# iftmp$34_368, _319, iftmp$39_370
	l32i	a2, sp, 100	# %sfp,
	extui	a4, a3, 0, 16	# tmp1637, iftmp$34_368,
	mull	a4, a4, a2	# tmp1638, tmp1637,
	srai	a2, a3, 16	# _1119, iftmp$34_368,
	srai	a4, a4, 16	# _1135, tmp1638,
	j	.L78		#
.L86:
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	or	a3, a4, a2	# tmp1639, _319, iftmp$46_371
	bgez	a3, .L98	# tmp1639,
.L88:
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	add.n	a3, a4, a2	# iftmp$34_368, _319, iftmp$46_371
	l32i	a5, sp, 100	# %sfp,
	extui	a4, a3, 0, 16	# tmp1640, iftmp$34_368,
	mull	a4, a4, a5	# tmp1641, tmp1640,
	srai	a2, a3, 16	# _1119, iftmp$34_368,
	srai	a4, a4, 16	# _1135, tmp1641,
	j	.L78		#
.L97:
	movi.n	a4, 0	# _1135,
	l32r	a2, .LC6	#, _1119
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	l32r	a3, .LC4	#, iftmp$34_368
	j	.L78		#
.L98:
	l32i	a4, sp, 148	# %sfp, _1135
	l32r	a2, .LC7	#, _1119
	l32r	a3, .LC8	#, iftmp$34_368
.L78:
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	l32i	a6, sp, 100	# %sfp,
	l32i	a7, sp, 104	# %sfp,
	mull	a2, a6, a2	# tmp1644,, _1119
	mull	a5, a7, a3	# tmp1645,, iftmp$34_368
	l32i.n	a8, sp, 48	# %sfp,
	add.n	a2, a2, a5	# tmp1646, tmp1644, tmp1645
	add.n	a2, a2, a4	# tmp1647, tmp1646, _1135
	srai	a2, a2, 7	# tmp1648, tmp1647,
	addi.n	a2, a2, 1	# tmp1649, tmp1648,
	l32r	a9, .LC6	#,
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	s32i	a3, a14, 64	# MEM[base: _666, offset: 64B], iftmp$34_368
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	srai	a2, a2, 1	# _349, tmp1649,
	l16si	a4, a8, 0	# MEM[base: _662, offset: 0B], _332
	mov.n	a3, a2	# _349, _349
	bge	a2, a9, .L79	# _349,,
	mov.n	a3, a9	# _349,
.L79:
	l32r	a10, .LC7	#,
	bge	a10, a3, .L80	#, _349,
	mov.n	a3, a10	# _349,
.L80:
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	l32r	a5, .LC7	#, iftmp$52_372
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	add.n	a3, a3, a4	# _350, _349, _332
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	mov.n	a11, a5	#, iftmp$52_372
	blt	a5, a3, .L81	# tmp11, _350,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	l32r	a5, .LC6	#, iftmp$52_372
	mov.n	a12, a5	#, iftmp$52_372
	blt	a3, a5, .L81	# _350, tmp12,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	mov.n	a5, a11	# iftmp$59_374,
	blt	a11, a2, .L82	#, _349,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	mov.n	a5, a12	# iftmp$59_374,
	blt	a2, a12, .L82	# _349,,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	slli	a2, a2, 16	# tmp1665, _349,
	srai	a5, a2, 16	# iftmp$59_374, tmp1665,
.L82:
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	add.n	a5, a4, a5	# tmp1666, _332, iftmp$59_374
	slli	a5, a5, 16	# tmp1667, tmp1666,
	srai	a5, a5, 16	# iftmp$52_372, tmp1667,
.L81:
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\silk\CNG.c:158:         for( i = 0; i < length; i++ ) {
	l32i	a3, sp, 108	# %sfp,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	s16i	a5, a2, 0	# MEM[base: _662, offset: 0B], iftmp$52_372
	addi.n	a2, a2, 2	#,,
	addi.n	a14, a14, 4	# ivtmp$75, ivtmp$75,
	s32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\silk\CNG.c:158:         for( i = 0; i < length; i++ ) {
	bne	a3, a14, .L83	#, ivtmp$75,
.L89:
# @OPUS@\upstream\silk\CNG.c:187:         silk_memcpy( psCNG->CNG_synth_state, &CNG_sig_Q14[ length ], MAX_LPC_ORDER * sizeof( opus_int32 ) );
	l32i	a6, sp, 112	# %sfp,
	l32i	a7, sp, 140	# %sfp,
	l32i	a2, sp, 144	# %sfp,
	movi.n	a4, 0x40	#,
	add.n	a3, a6, a7	#,,
	call0	memcpy		#
	j	.L84		#
.L39:
# @OPUS@\upstream\silk\CNG.c:189:         silk_memset( psCNG->CNG_synth_state, 0, psDec->LPC_order *  sizeof( opus_int32 ) );
	movi	a2, 0x5d8	# tmp1675,
	add.n	a13, a13, a2	# tmp1676, psDec, tmp1675
	movi	a2, 0x520	# tmp1677,
	slli	a4, a4, 2	#, pretmp_1202,
	movi.n	a3, 0	#,
	add.n	a2, a13, a2	#, tmp1676, tmp1677
	call0	memset		#
.L84:
# @OPUS@\upstream\silk\CNG.c:191:     RESTORE_STACK;
	l32i.n	a2, sp, 32	# _saved_stack,
	l32i.n	a3, sp, 36	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\CNG.c:192: }
	l32i	a0, sp, 204	#,
	movi	a9, 0xd0	#,
	l32i	a12, sp, 200	#,
	l32i	a13, sp, 196	#,
	l32i	a14, sp, 192	#,
	l32i	a15, sp, 188	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L75:
# @OPUS@\upstream\silk\CNG.c:181:             CNG_sig_Q14[ MAX_LPC_ORDER + i ] = silk_ADD_SAT32( CNG_sig_Q14[ MAX_LPC_ORDER + i ], silk_LSHIFT_SAT32( LPC_pred_Q10, 4 ) );
	l32r	a8, .LC5	#,
	add.n	a2, a4, a8	# tmp1683, _319,
	mov.n	a3, a8	# iftmp$39_370,
	bgez	a2, .L85	# tmp1683,
	mov.n	a2, a8	# iftmp$46_371,
	j	.L86		#
.L76:
	l32r	a9, .LC4	#,
	add.n	a2, a4, a9	# tmp1685, _319,
	mov.n	a3, a9	# iftmp$39_370,
	bgez	a2, .L87	# tmp1685,
	mov.n	a2, a9	# iftmp$46_371,
	j	.L88		#
.L181:
# @OPUS@\upstream\silk\CNG.c:153:         silk_NLSF2A( A_Q12, psCNG->CNG_smth_NLSF_Q15, psDec->LPC_order, psDec->arch );
	l32i.n	a10, sp, 56	# %sfp,
# @OPUS@\upstream\silk\CNG.c:59:     *rand_seed = seed;
	s32i.n	a4, a12, 60	# MEM[(opus_int32 *)psDec_382(D) + 2876B], seed
# @OPUS@\upstream\silk\CNG.c:153:         silk_NLSF2A( A_Q12, psCNG->CNG_smth_NLSF_Q15, psDec->LPC_order, psDec->arch );
	l32i	a5, a12, 76	# psDec_382(D)->arch,
	l32i.n	a4, a10, 40	# psDec_382(D)->LPC_order,
	mov.n	a2, sp	#,
	s32i	a11, sp, 156	#,
	call0	silk_NLSF2A		#
# @OPUS@\upstream\silk\CNG.c:156:         silk_memcpy( CNG_sig_Q14, psCNG->CNG_synth_state, MAX_LPC_ORDER * sizeof( opus_int32 ) );
	l32i	a3, sp, 144	# %sfp,
	l32i	a2, sp, 112	# %sfp,
	movi.n	a4, 0x40	#,
	call0	memcpy		#
	l32i	a11, sp, 156	#,
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	l16si	a3, sp, 0	# A_Q12,
	slli	a2, a11, 16	# tmp1728, prephitmp_1165,
	srai	a2, a2, 16	#, tmp1728,
	s32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	l32i.n	a11, sp, 52	# %sfp,
	l32i	a12, sp, 100	# %sfp,
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	l16si	a4, sp, 2	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	l16si	a5, sp, 4	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	l16si	a6, sp, 6	# A_Q12,
	slli	a2, a2, 16	# tmp1730,,
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	l16si	a8, sp, 10	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	l16si	a9, sp, 12	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	l16si	a10, sp, 14	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	srai	a13, a11, 21	# tmp1726,,
	sub	a2, a2, a12	# tmp1731, tmp1730,
# @OPUS@\upstream\silk\CNG.c:161:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12[ 0 ] );
	s32i.n	a3, sp, 60	# %sfp,
# @OPUS@\upstream\silk\CNG.c:162:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12[ 1 ] );
	s32i	a4, sp, 64	# %sfp,
# @OPUS@\upstream\silk\CNG.c:163:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12[ 2 ] );
	s32i	a5, sp, 68	# %sfp,
# @OPUS@\upstream\silk\CNG.c:164:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12[ 3 ] );
	s32i	a6, sp, 72	# %sfp,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	l16si	a7, sp, 8	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	l16si	a11, sp, 16	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	l16si	a12, sp, 18	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	l16si	a3, sp, 20	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	l16si	a4, sp, 22	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	l16si	a5, sp, 24	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	l16si	a6, sp, 26	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:166:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12[ 5 ] );
	s32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\silk\CNG.c:167:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12[ 6 ] );
	s32i	a9, sp, 84	# %sfp,
# @OPUS@\upstream\silk\CNG.c:168:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12[ 7 ] );
	s32i	a10, sp, 88	# %sfp,
# @OPUS@\upstream\silk\CNG.c:165:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12[ 4 ] );
	s32i	a7, sp, 76	# %sfp,
# @OPUS@\upstream\silk\CNG.c:169:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12[ 8 ] );
	s32i	a11, sp, 92	# %sfp,
# @OPUS@\upstream\silk\CNG.c:170:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12[ 9 ] );
	s32i	a12, sp, 96	# %sfp,
# @OPUS@\upstream\silk\CNG.c:172:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12[ 10 ] );
	s32i	a3, sp, 116	# %sfp,
# @OPUS@\upstream\silk\CNG.c:173:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12[ 11 ] );
	s32i	a4, sp, 120	# %sfp,
# @OPUS@\upstream\silk\CNG.c:174:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12[ 12 ] );
	s32i	a5, sp, 124	# %sfp,
# @OPUS@\upstream\silk\CNG.c:175:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12[ 13 ] );
	s32i	a6, sp, 128	# %sfp,
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	l16si	a7, sp, 28	# A_Q12,
	l32i	a9, sp, 112	# %sfp,
	l32i	a10, sp, 140	# %sfp,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	addi.n	a13, a13, 1	# tmp1727, tmp1726,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	l16si	a8, sp, 30	# A_Q12,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	srai	a13, a13, 1	#, tmp1727,
	add.n	a9, a9, a10	#,,
	srai	a2, a2, 16	#, tmp1731,
# @OPUS@\upstream\silk\CNG.c:176:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12[ 14 ] );
	s32i	a7, sp, 132	# %sfp,
# @OPUS@\upstream\silk\CNG.c:177:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, CNG_sig_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12[ 15 ] );
	s32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\silk\CNG.c:184:             frame[ i ] = (opus_int16)silk_ADD_SAT16( frame[ i ], silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( CNG_sig_Q14[ MAX_LPC_ORDER + i ], gain_Q10 ), 8 ) ) );
	s32i	a13, sp, 104	# %sfp,
	s32i	a9, sp, 108	# %sfp,
	s32i	a2, sp, 148	# %sfp,
	j	.L83		#
.L71:
# @OPUS@\upstream\silk\CNG.c:153:         silk_NLSF2A( A_Q12, psCNG->CNG_smth_NLSF_Q15, psDec->LPC_order, psDec->arch );
	l32i.n	a11, sp, 56	# %sfp,
	l32i	a5, a12, 76	# psDec_382(D)->arch,
	l32i.n	a4, a11, 40	# psDec_382(D)->LPC_order,
	mov.n	a2, sp	#,
	call0	silk_NLSF2A		#
# @OPUS@\upstream\silk\CNG.c:156:         silk_memcpy( CNG_sig_Q14, psCNG->CNG_synth_state, MAX_LPC_ORDER * sizeof( opus_int32 ) );
	l32i	a3, sp, 144	# %sfp,
	l32i	a2, sp, 112	# %sfp,
	movi.n	a4, 0x40	#,
	slli	a12, a15, 2	#, length,
	call0	memcpy		#
	s32i	a12, sp, 140	# %sfp,
	j	.L89		#
.L59:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a4, a4, 0, 7	# _489, gain_Q16,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a5, .LC2	#, y
	j	.L62		#
.L65:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a2, a2, 0, 7	# _515, gain_Q16,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a5, .LC2	#, y
	j	.L68		#
.L69:
	movi	a2, 0x520	# tmp1741,
	add.n	a2, a7, a2	#, _117, tmp1741
# @OPUS@\upstream\silk\CNG.c:51:     seed = *rand_seed;
	l32i.n	a4, a12, 60	# MEM[(opus_int32 *)psDec_382(D) + 2876B], seed
	s32i	a2, sp, 144	# %sfp,
	addmi	a3, a7, 0x500	# pretmp_1012, _117,
# @OPUS@\upstream\silk\CNG.c:46:     exc_mask = CNG_BUF_MASK_MAX;
	movi	a5, 0xff	# exc_mask,
	j	.L90		#
	.size	silk_CNG, .-silk_CNG
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
