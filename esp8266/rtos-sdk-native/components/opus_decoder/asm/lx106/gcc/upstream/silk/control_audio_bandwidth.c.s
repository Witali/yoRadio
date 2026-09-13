# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/control_audio_bandwidth.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"control_audio_bandwidth.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\control_audio_bandwidth.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\control_audio_bandwidth.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\control_audio_bandwidth.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\control_audio_bandwidth.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\control_audio_bandwidth.c.s.raw
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
	.section	.text.silk_control_audio_bandwidth,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_control_audio_bandwidth
	.type	silk_control_audio_bandwidth, @function
# Function: silk_control_audio_bandwidth
# Module: upstream/silk/control_audio_bandwidth.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "tuning_parameters.h"
# C context:
# C context: /* Control internal sampling rate */
# C context: opus_int silk_control_audio_bandwidth(
# C context: silk_encoder_state          *psEncC,                        /* I/O  Pointer to Silk encoder state               */
# C context: silk_EncControlStruct       *encControl                     /* I    Control structure                           */
# C context: )
# C context: {
silk_control_audio_bandwidth:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:45:     orig_kHz = psEncC->fs_kHz;
	addmi	a5, a2, 0x1100	# tmp167, psEncC,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:40: {
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:45:     orig_kHz = psEncC->fs_kHz;
	l32i	a12, a5, 224	# psEncC_41(D)->fs_kHz, <retval>
# @OPUS@\upstream\silk\control_audio_bandwidth.c:40: {
	s32i.n	a13, sp, 4	#,
	s32i.n	a0, sp, 12	#,
	s32i.n	a14, sp, 0	#,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:40: {
	mov.n	a13, a3	# encControl, encControl
# @OPUS@\upstream\silk\control_audio_bandwidth.c:47:     if( orig_kHz == 0 ) {
	bnez.n	a12, .L2	# <retval>,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:48:         orig_kHz = psEncC->sLP.saved_fs_kHz;
	l32i.n	a12, a2, 32	# psEncC_41(D)->sLP.saved_fs_kHz, <retval>
.L2:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:51:     fs_Hz = silk_SMULBB( fs_kHz, 1000 );
	slli	a3, a12, 16	# tmp80, <retval>,
	srai	a4, a3, 16	# tmp79, tmp80,
	slli	a3, a4, 5	# tmp82, tmp79,
	sub	a3, a3, a4	# tmp83, tmp82, tmp79
	slli	a3, a3, 2	# tmp84, tmp83,
	add.n	a3, a3, a4	# tmp85, tmp84, tmp79
	slli	a3, a3, 3	# tmp86, tmp85,
	l32i	a6, a5, 204	# psEncC_41(D)->API_fs_Hz, pretmp_87
# @OPUS@\upstream\silk\control_audio_bandwidth.c:52:     if( fs_Hz == 0 ) {
	bnez.n	a3, .L3	# tmp86,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:54:         fs_Hz  = silk_min( psEncC->desiredInternal_fs_Hz, psEncC->API_fs_Hz );
	l32i	a2, a5, 220	# psEncC_41(D)->desiredInternal_fs_Hz, fs_Hz
	bge	a6, a2, .L9	# pretmp_87, fs_Hz,
	mov.n	a2, a6	# fs_Hz, pretmp_87
	j	.L9		#
.L3:
	l32i	a4, a5, 212	# psEncC_41(D)->maxInternal_fs_Hz, pretmp_67
	l32i	a7, a5, 216	# psEncC_41(D)->minInternal_fs_Hz, pretmp_88
# @OPUS@\upstream\silk\control_audio_bandwidth.c:56:     } else if( fs_Hz > psEncC->API_fs_Hz || fs_Hz > psEncC->maxInternal_fs_Hz || fs_Hz < psEncC->minInternal_fs_Hz ) {
	blt	a6, a3, .L6	# pretmp_87, tmp86,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:56:     } else if( fs_Hz > psEncC->API_fs_Hz || fs_Hz > psEncC->maxInternal_fs_Hz || fs_Hz < psEncC->minInternal_fs_Hz ) {
	blt	a4, a3, .L6	# pretmp_67, tmp86,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:56:     } else if( fs_Hz > psEncC->API_fs_Hz || fs_Hz > psEncC->maxInternal_fs_Hz || fs_Hz < psEncC->minInternal_fs_Hz ) {
	bge	a3, a7, .L7	# tmp86, pretmp_88,
.L6:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:59:         fs_Hz  = silk_min( fs_Hz, psEncC->maxInternal_fs_Hz );
	mov.n	a2, a4	# fs_Hz, pretmp_67
	bge	a6, a4, .L8	# pretmp_87, fs_Hz,
	mov.n	a2, a6	# fs_Hz, pretmp_87
.L8:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:60:         fs_Hz  = silk_max( fs_Hz, psEncC->minInternal_fs_Hz );
	bge	a2, a7, .L9	# fs_Hz, pretmp_88,
	mov.n	a2, a7	# fs_Hz, pretmp_88
.L9:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:61:         fs_kHz = silk_DIV32_16( fs_Hz, 1000 );
	movi	a3, 0x3e8	#,
	call0	__divsi3		#
	mov.n	a12, a2	# <retval>,
	j	.L1		#
.L7:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:64:         if( psEncC->sLP.transition_frame_no >= TRANSITION_FRAMES ) {
	l32i.n	a4, a2, 24	# psEncC_41(D)->sLP.transition_frame_no, _10
# @OPUS@\upstream\silk\control_audio_bandwidth.c:64:         if( psEncC->sLP.transition_frame_no >= TRANSITION_FRAMES ) {
	movi	a6, 0xff	# tmp103,
	bge	a6, a4, .L10	# tmp103, _10,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:66:             psEncC->sLP.mode = 0;
	movi.n	a6, 0	# tmp104,
	s32i.n	a6, a2, 28	# psEncC_41(D)->sLP.mode, tmp104
.L10:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:68:         if( psEncC->allow_bandwidth_switch || encControl->opusCanSwitch ) {
	l32i	a6, a5, 184	# psEncC_41(D)->allow_bandwidth_switch, psEncC_41(D)->allow_bandwidth_switch
	bnez.n	a6, .L11	# psEncC_41(D)->allow_bandwidth_switch,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:68:         if( psEncC->allow_bandwidth_switch || encControl->opusCanSwitch ) {
	l32i	a6, a13, 68	# encControl_48(D)->opusCanSwitch, encControl_48(D)->opusCanSwitch
	beqz.n	a6, .L1	# encControl_48(D)->opusCanSwitch,
.L11:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:70:             if( silk_SMULBB( orig_kHz, 1000 ) > psEncC->desiredInternal_fs_Hz )
	l32i	a5, a5, 220	# psEncC_41(D)->desiredInternal_fs_Hz, _13
# @OPUS@\upstream\silk\control_audio_bandwidth.c:70:             if( silk_SMULBB( orig_kHz, 1000 ) > psEncC->desiredInternal_fs_Hz )
	bge	a5, a3, .L12	# _13, tmp86,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:73:                 if( psEncC->sLP.mode == 0 ) {
	l32i.n	a3, a2, 28	# psEncC_41(D)->sLP.mode, psEncC_41(D)->sLP.mode
	bnez.n	a3, .L13	# psEncC_41(D)->sLP.mode,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:78:                     silk_memset( psEncC->sLP.In_LP_State, 0, sizeof( psEncC->sLP.In_LP_State ) );
	s8i	a3, a2, 16	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
	s8i	a3, a2, 17	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
	s8i	a3, a2, 18	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
	s8i	a3, a2, 19	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
	s8i	a3, a2, 20	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
	s8i	a3, a2, 21	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
	s8i	a3, a2, 22	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
	s8i	a3, a2, 23	# MEM[(void *)psEncC_41(D) + 16B], psEncC_41(D)->sLP.mode
# @OPUS@\upstream\silk\control_audio_bandwidth.c:75:                     psEncC->sLP.transition_frame_no = TRANSITION_FRAMES;
	movi	a4, 0x100	# tmp110,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:80:                 if( encControl->opusCanSwitch ) {
	l32i	a3, a13, 68	# encControl_48(D)->opusCanSwitch, encControl_48(D)->opusCanSwitch
# @OPUS@\upstream\silk\control_audio_bandwidth.c:75:                     psEncC->sLP.transition_frame_no = TRANSITION_FRAMES;
	s32i.n	a4, a2, 24	# psEncC_41(D)->sLP.transition_frame_no, tmp110
# @OPUS@\upstream\silk\control_audio_bandwidth.c:80:                 if( encControl->opusCanSwitch ) {
	beqz.n	a3, .L14	# encControl_48(D)->opusCanSwitch,
.L15:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:82:                     psEncC->sLP.mode = 0;
	movi.n	a3, 0	# tmp122,
	s32i.n	a3, a2, 28	# psEncC_41(D)->sLP.mode, tmp122
# @OPUS@\upstream\silk\control_audio_bandwidth.c:85:                     fs_kHz = orig_kHz == 16 ? 12 : 8;
	beqi	a12, 16, .L20	# <retval>,,
	movi.n	a12, 8	# <retval>,
	j	.L1		#
.L13:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:80:                 if( encControl->opusCanSwitch ) {
	l32i	a3, a13, 68	# encControl_48(D)->opusCanSwitch, encControl_48(D)->opusCanSwitch
	bnez.n	a3, .L15	# encControl_48(D)->opusCanSwitch,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:87:                    if( psEncC->sLP.transition_frame_no <= 0 ) {
	bgei	a4, 1, .L14	# _10,,
	j	.L29		#
.L14:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:93:                        psEncC->sLP.mode = -2;
	movi.n	a3, -2	# tmp136,
	s32i.n	a3, a2, 28	# psEncC_41(D)->sLP.mode, tmp136
	j	.L1		#
.L12:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:99:             if( silk_SMULBB( orig_kHz, 1000 ) < psEncC->desiredInternal_fs_Hz )
	bge	a3, a5, .L16	# tmp86, _13,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:102:                 if( encControl->opusCanSwitch ) {
	l32i	a3, a13, 68	# encControl_48(D)->opusCanSwitch, encControl_48(D)->opusCanSwitch
	beqz.n	a3, .L17	# encControl_48(D)->opusCanSwitch,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:104:                     fs_kHz = orig_kHz == 8 ? 12 : 16;
	beqi	a12, 8, .L21	# <retval>,,
	movi.n	a12, 0x10	# <retval>,
	j	.L18		#
.L21:
	movi.n	a12, 0xc	# <retval>,
.L18:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:107:                     psEncC->sLP.transition_frame_no = 0;
	movi.n	a3, 0	# tmp138,
	s32i.n	a3, a2, 24	# psEncC_41(D)->sLP.transition_frame_no, tmp138
# @OPUS@\upstream\silk\control_audio_bandwidth.c:110:                     silk_memset( psEncC->sLP.In_LP_State, 0, sizeof( psEncC->sLP.In_LP_State ) );
	s8i	a3, a2, 16	# MEM[(void *)psEncC_41(D) + 16B], tmp138
	s8i	a3, a2, 17	# MEM[(void *)psEncC_41(D) + 16B], tmp138
	s8i	a3, a2, 18	# MEM[(void *)psEncC_41(D) + 16B], tmp138
	s8i	a3, a2, 19	# MEM[(void *)psEncC_41(D) + 16B], tmp138
	s8i	a3, a2, 20	# MEM[(void *)psEncC_41(D) + 16B], tmp138
	s8i	a3, a2, 21	# MEM[(void *)psEncC_41(D) + 16B], tmp138
	s8i	a3, a2, 22	# MEM[(void *)psEncC_41(D) + 16B], tmp138
	s8i	a3, a2, 23	# MEM[(void *)psEncC_41(D) + 16B], tmp138
# @OPUS@\upstream\silk\control_audio_bandwidth.c:113:                     psEncC->sLP.mode = 1;
	movi.n	a3, 1	# tmp149,
	s32i.n	a3, a2, 28	# psEncC_41(D)->sLP.mode, tmp149
	j	.L1		#
.L17:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:115:                    if( psEncC->sLP.mode == 0 ) {
	l32i.n	a3, a2, 28	# psEncC_41(D)->sLP.mode, psEncC_41(D)->sLP.mode
	bnez.n	a3, .L28	# psEncC_41(D)->sLP.mode,
.L29:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:118:                        encControl->maxBits -= encControl->maxBits * 5 / ( encControl->payloadSize_ms + 5 );
	l32i.n	a14, a13, 60	# encControl_48(D)->maxBits, _27
# @OPUS@\upstream\silk\control_audio_bandwidth.c:116:                        encControl->switchReady = 1;
	movi.n	a4, 1	# tmp151,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:118:                        encControl->maxBits -= encControl->maxBits * 5 / ( encControl->payloadSize_ms + 5 );
	l32i.n	a3, a13, 24	# encControl_48(D)->payloadSize_ms, encControl_48(D)->payloadSize_ms
# @OPUS@\upstream\silk\control_audio_bandwidth.c:116:                        encControl->switchReady = 1;
	s32i	a4, a13, 92	# encControl_48(D)->switchReady, tmp151
# @OPUS@\upstream\silk\control_audio_bandwidth.c:118:                        encControl->maxBits -= encControl->maxBits * 5 / ( encControl->payloadSize_ms + 5 );
	slli	a2, a14, 2	# tmp153, _27,
# @OPUS@\upstream\silk\control_audio_bandwidth.c:118:                        encControl->maxBits -= encControl->maxBits * 5 / ( encControl->payloadSize_ms + 5 );
	movi.n	a4, -5	# tmp155,
	sub	a3, a4, a3	#, tmp155, encControl_48(D)->payloadSize_ms
	add.n	a2, a2, a14	#, tmp153, _27
	call0	__divsi3		#
# @OPUS@\upstream\silk\control_audio_bandwidth.c:118:                        encControl->maxBits -= encControl->maxBits * 5 / ( encControl->payloadSize_ms + 5 );
	add.n	a2, a2, a14	# tmp162,, _27
	s32i.n	a2, a13, 60	# encControl_48(D)->maxBits, tmp162
	j	.L1		#
.L16:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:125:                if (psEncC->sLP.mode<0)
	l32i.n	a3, a2, 28	# psEncC_41(D)->sLP.mode, psEncC_41(D)->sLP.mode
	bgez	a3, .L1	# psEncC_41(D)->sLP.mode,
.L28:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:126:                   psEncC->sLP.mode = 1;
	movi.n	a3, 1	# tmp165,
	s32i.n	a3, a2, 28	# psEncC_41(D)->sLP.mode, tmp165
	j	.L1		#
.L20:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:85:                     fs_kHz = orig_kHz == 16 ? 12 : 8;
	movi.n	a12, 0xc	# <retval>,
.L1:
# @OPUS@\upstream\silk\control_audio_bandwidth.c:132: }
	l32i.n	a0, sp, 12	#,
	mov.n	a2, a12	#, <retval>
	l32i.n	a13, sp, 4	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a14, sp, 0	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_control_audio_bandwidth, .-silk_control_audio_bandwidth
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
