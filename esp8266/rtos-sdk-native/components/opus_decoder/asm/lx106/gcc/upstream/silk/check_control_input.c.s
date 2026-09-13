# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/check_control_input.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"check_control_input.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\check_control_input.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\check_control_input.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\check_control_input.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\check_control_input.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\check_control_input.c.s.raw
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
	.section	.text.check_control_input,"ax",@progbits
	.literal_position
	.literal .LC0, -8000
	.literal .LC1, -12000
	.literal .LC2, -16000
	.literal .LC3, -24000
	.literal .LC4, -44100
	.literal .LC5, -48000
	.literal .LC6, 1073742849
	.align	4
	.global	check_control_input
	.type	check_control_input, @function
# Function: check_control_input
# Module: upstream/silk/check_control_input.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "errors.h"
# C context:
# C context: /* Check encoder control struct */
# C context: opus_int check_control_input(
# C context: silk_EncControlStruct        *encControl                    /* I    Control structure                           */
# C context: )
# C context: {
# C context: celt_assert( encControl != NULL );
check_control_input:
# @OPUS@\upstream\silk\check_control_input.c:43:     if( ( ( encControl->API_sampleRate            !=  8000 ) &&
	l32i.n	a5, a2, 8	# encControl_34(D)->API_sampleRate, _35
# @OPUS@\upstream\silk\check_control_input.c:43:     if( ( ( encControl->API_sampleRate            !=  8000 ) &&
	l32r	a4, .LC0	#, tmp260
	movi.n	a8, 0	# tmp111,
	l32r	a3, .LC1	#, tmp261
	movi.n	a9, 1	# tmp110,
	add.n	a10, a5, a4	# tmp108, _35, tmp260
	mov.n	a11, a8	#, tmp111
# @OPUS@\upstream\silk\check_control_input.c:40: {
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\silk\check_control_input.c:44:           ( encControl->API_sampleRate            != 12000 ) &&
	l32r	a7, .LC2	#, tmp262
# @OPUS@\upstream\silk\check_control_input.c:43:     if( ( ( encControl->API_sampleRate            !=  8000 ) &&
	add.n	a6, a5, a3	# tmp114, _35, tmp261
	movnez	a11, a9, a10	#, tmp110, tmp108
# @OPUS@\upstream\silk\check_control_input.c:40: {
	s32i.n	a12, sp, 12	#,
# @OPUS@\upstream\silk\check_control_input.c:43:     if( ( ( encControl->API_sampleRate            !=  8000 ) &&
	mov.n	a12, a8	#, tmp111
	mov.n	a10, a11	# tmp107,
	movnez	a12, a9, a6	#, tmp110, tmp114
# @OPUS@\upstream\silk\check_control_input.c:44:           ( encControl->API_sampleRate            != 12000 ) &&
	add.n	a11, a5, a7	# tmp121, _35, tmp262
	mov.n	a6, a8	#, tmp111
	movnez	a6, a9, a11	#, tmp110, tmp121
	mov.n	a11, a6	# tmp120,
# @OPUS@\upstream\silk\check_control_input.c:45:           ( encControl->API_sampleRate            != 16000 ) &&
	l32r	a6, .LC3	#, tmp130
# @OPUS@\upstream\silk\check_control_input.c:43:     if( ( ( encControl->API_sampleRate            !=  8000 ) &&
	and	a10, a10, a12	# tmp118, tmp107, tmp113
# @OPUS@\upstream\silk\check_control_input.c:44:           ( encControl->API_sampleRate            != 12000 ) &&
	and	a11, a11, a10	# tmp126, tmp120, tmp118
# @OPUS@\upstream\silk\check_control_input.c:45:           ( encControl->API_sampleRate            != 16000 ) &&
	add.n	a6, a5, a6	# tmp129, _35, tmp130
	mov.n	a10, a8	#, tmp111
	movnez	a10, a9, a6	#, tmp110, tmp129
	mov.n	a6, a10	# tmp128,
	and	a6, a6, a11	# tmp134, tmp128, tmp126
# @OPUS@\upstream\silk\check_control_input.c:46:           ( encControl->API_sampleRate            != 24000 ) &&
	addmi	a10, a5, -0x7d00	# tmp137, _35,
	mov.n	a11, a8	#, tmp111
	movnez	a11, a9, a10	#, tmp110, tmp137
	mov.n	a10, a11	# tmp136,
# @OPUS@\upstream\silk\check_control_input.c:47:           ( encControl->API_sampleRate            != 32000 ) &&
	l32r	a11, .LC4	#, tmp145
# @OPUS@\upstream\silk\check_control_input.c:46:           ( encControl->API_sampleRate            != 24000 ) &&
	and	a6, a10, a6	# tmp141, tmp136, tmp134
# @OPUS@\upstream\silk\check_control_input.c:47:           ( encControl->API_sampleRate            != 32000 ) &&
	add.n	a11, a5, a11	# tmp144, _35, tmp145
	movnez	a8, a9, a11	# tmp143, tmp110, tmp144
# @OPUS@\upstream\silk\check_control_input.c:48:           ( encControl->API_sampleRate            != 44100 ) &&
	bnone	a8, a6, .L27	# tmp143, tmp141,
	l32r	a6, .LC5	#, tmp155
	add.n	a5, a5, a6	# tmp154, _35, tmp155
	bnez.n	a5, .L17	# tmp154,
.L27:
# @OPUS@\upstream\silk\check_control_input.c:50:         ( ( encControl->desiredInternalSampleRate !=  8000 ) &&
	l32i.n	a5, a2, 20	# encControl_34(D)->desiredInternalSampleRate, _36
# @OPUS@\upstream\silk\check_control_input.c:50:         ( ( encControl->desiredInternalSampleRate !=  8000 ) &&
	movi.n	a9, 0	# tmp164,
	movi.n	a10, 1	# tmp163,
	mov.n	a12, a9	#, tmp164
	add.n	a8, a5, a4	# tmp161, _36, tmp260
	add.n	a6, a5, a3	# tmp167, _36, tmp261
	movnez	a12, a10, a8	#, tmp163, tmp161
	movnez	a9, a10, a6	# tmp164, tmp163, tmp167
# @OPUS@\upstream\silk\check_control_input.c:51:           ( encControl->desiredInternalSampleRate != 12000 ) &&
	bnone	a12, a9, .L28	# tmp160, tmp166,
	add.n	a6, a5, a7	# tmp176, _36, tmp262
	bnez.n	a6, .L17	# tmp176,
.L28:
# @OPUS@\upstream\silk\check_control_input.c:53:         ( ( encControl->maxInternalSampleRate     !=  8000 ) &&
	l32i.n	a8, a2, 12	# encControl_34(D)->maxInternalSampleRate, _37
# @OPUS@\upstream\silk\check_control_input.c:53:         ( ( encControl->maxInternalSampleRate     !=  8000 ) &&
	movi.n	a10, 0	# tmp186,
	movi.n	a11, 1	# tmp185,
	mov.n	a12, a10	#, tmp186
	add.n	a9, a8, a4	# tmp183, _37, tmp260
	add.n	a6, a8, a3	# tmp189, _37, tmp261
	movnez	a12, a11, a9	#, tmp185, tmp183
	movnez	a10, a11, a6	# tmp186, tmp185, tmp189
# @OPUS@\upstream\silk\check_control_input.c:54:           ( encControl->maxInternalSampleRate     != 12000 ) &&
	bnone	a12, a10, .L29	# tmp182, tmp188,
	add.n	a6, a8, a7	# tmp198, _37, tmp262
	bnez.n	a6, .L17	# tmp198,
.L29:
# @OPUS@\upstream\silk\check_control_input.c:56:         ( ( encControl->minInternalSampleRate     !=  8000 ) &&
	l32i.n	a6, a2, 16	# encControl_34(D)->minInternalSampleRate, _38
# @OPUS@\upstream\silk\check_control_input.c:56:         ( ( encControl->minInternalSampleRate     !=  8000 ) &&
	movi.n	a9, 0	# tmp208,
	movi.n	a10, 1	# tmp207,
	mov.n	a11, a9	#, tmp208
	add.n	a4, a6, a4	# tmp205, _38, tmp260
	add.n	a3, a6, a3	# tmp211, _38, tmp261
	movnez	a11, a10, a4	#, tmp207, tmp205
	movnez	a9, a10, a3	# tmp208, tmp207, tmp211
# @OPUS@\upstream\silk\check_control_input.c:57:           ( encControl->minInternalSampleRate     != 12000 ) &&
	bnone	a11, a9, .L30	# tmp204, tmp210,
	add.n	a7, a6, a7	# tmp220, _38, tmp262
	bnez.n	a7, .L17	# tmp220,
.L30:
# @OPUS@\upstream\silk\check_control_input.c:58:           ( encControl->minInternalSampleRate     != 16000 ) ) ||
	blt	a5, a6, .L17	# _36, _38,
# @OPUS@\upstream\silk\check_control_input.c:59:           ( encControl->minInternalSampleRate > encControl->desiredInternalSampleRate ) ||
	blt	a8, a5, .L17	# _37, _36,
# @OPUS@\upstream\silk\check_control_input.c:65:     if( encControl->payloadSize_ms != 10 &&
	l32i.n	a3, a2, 24	# encControl_34(D)->payloadSize_ms, _39
# @OPUS@\upstream\silk\check_control_input.c:65:     if( encControl->payloadSize_ms != 10 &&
	movi.n	a6, 0x1e	# tmp231,
	addi	a5, a3, -10	# _66, _39,
	movi.n	a4, 1	# _74,
	bltu	a6, a5, .L9	# tmp231, _66,
	l32r	a4, .LC6	#, tmp233
	ssr	a5	# _66
	srl	a5, a4	# tmp232, tmp233
	movi.n	a4, -1	# tmp235,
	xor	a4, a4, a5	# tmp234, tmp235, tmp232
	extui	a4, a4, 0, 1	# _74, tmp234,
.L9:
# @OPUS@\upstream\silk\check_control_input.c:67:         encControl->payloadSize_ms != 40 &&
	addi	a3, a3, -60	# tmp240, _39,
	beqz.n	a3, .L31	# tmp240,
	bnez.n	a4, .L19	# _74,
.L31:
# @OPUS@\upstream\silk\check_control_input.c:72:     if( encControl->packetLossPercentage < 0 || encControl->packetLossPercentage > 100 ) {
	l32i.n	a3, a2, 32	# encControl_34(D)->packetLossPercentage, encControl_34(D)->packetLossPercentage
	movi	a4, 0x64	# tmp244,
	bltu	a4, a3, .L20	# tmp244, encControl_34(D)->packetLossPercentage,
# @OPUS@\upstream\silk\check_control_input.c:76:     if( encControl->useDTX < 0 || encControl->useDTX > 1 ) {
	l32i.n	a3, a2, 52	# encControl_34(D)->useDTX, encControl_34(D)->useDTX
	bgeui	a3, 2, .L21	# encControl_34(D)->useDTX,,
# @OPUS@\upstream\silk\check_control_input.c:80:     if( encControl->useCBR < 0 || encControl->useCBR > 1 ) {
	l32i.n	a3, a2, 56	# encControl_34(D)->useCBR, encControl_34(D)->useCBR
	bgeui	a3, 2, .L22	# encControl_34(D)->useCBR,,
# @OPUS@\upstream\silk\check_control_input.c:84:     if( encControl->useInBandFEC < 0 || encControl->useInBandFEC > 1 ) {
	l32i.n	a3, a2, 40	# encControl_34(D)->useInBandFEC, encControl_34(D)->useInBandFEC
	bgeui	a3, 2, .L23	# encControl_34(D)->useInBandFEC,,
# @OPUS@\upstream\silk\check_control_input.c:88:     if( encControl->nChannelsAPI < 1 || encControl->nChannelsAPI > ENCODER_NUM_CHANNELS ) {
	l32i.n	a3, a2, 0	# encControl_34(D)->nChannelsAPI, _24
# @OPUS@\upstream\silk\check_control_input.c:88:     if( encControl->nChannelsAPI < 1 || encControl->nChannelsAPI > ENCODER_NUM_CHANNELS ) {
	addi.n	a4, a3, -1	# tmp249, _24,
# @OPUS@\upstream\silk\check_control_input.c:88:     if( encControl->nChannelsAPI < 1 || encControl->nChannelsAPI > ENCODER_NUM_CHANNELS ) {
	bgeui	a4, 2, .L25	# tmp249,,
# @OPUS@\upstream\silk\check_control_input.c:92:     if( encControl->nChannelsInternal < 1 || encControl->nChannelsInternal > ENCODER_NUM_CHANNELS ) {
	l32i.n	a4, a2, 4	# encControl_34(D)->nChannelsInternal, _27
# @OPUS@\upstream\silk\check_control_input.c:92:     if( encControl->nChannelsInternal < 1 || encControl->nChannelsInternal > ENCODER_NUM_CHANNELS ) {
	addi.n	a5, a4, -1	# tmp250, _27,
# @OPUS@\upstream\silk\check_control_input.c:92:     if( encControl->nChannelsInternal < 1 || encControl->nChannelsInternal > ENCODER_NUM_CHANNELS ) {
	bgeui	a5, 2, .L25	# tmp250,,
# @OPUS@\upstream\silk\check_control_input.c:96:     if( encControl->nChannelsInternal > encControl->nChannelsAPI ) {
	blt	a3, a4, .L25	# _24, _27,
# @OPUS@\upstream\silk\check_control_input.c:100:     if( encControl->complexity < 0 || encControl->complexity > 10 ) {
	l32i.n	a3, a2, 36	# encControl_34(D)->complexity, encControl_34(D)->complexity
	movi.n	a4, 0xa	# tmp258,
# @OPUS@\upstream\silk\check_control_input.c:105:     return SILK_NO_ERROR;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\silk\check_control_input.c:100:     if( encControl->complexity < 0 || encControl->complexity > 10 ) {
	bgeu	a4, a3, .L1	# tmp258, encControl_34(D)->complexity,
# @OPUS@\upstream\silk\check_control_input.c:102:         return SILK_ENC_INVALID_COMPLEXITY_SETTING;
	movi	a2, -0x6a	# <retval>,
	j	.L1		#
.L17:
# @OPUS@\upstream\silk\check_control_input.c:63:         return SILK_ENC_FS_NOT_SUPPORTED;
	movi	a2, -0x66	# <retval>,
	j	.L1		#
.L19:
# @OPUS@\upstream\silk\check_control_input.c:70:         return SILK_ENC_PACKET_SIZE_NOT_SUPPORTED;
	movi	a2, -0x67	# <retval>,
	j	.L1		#
.L20:
# @OPUS@\upstream\silk\check_control_input.c:74:         return SILK_ENC_INVALID_LOSS_RATE;
	movi	a2, -0x69	# <retval>,
	j	.L1		#
.L21:
# @OPUS@\upstream\silk\check_control_input.c:78:         return SILK_ENC_INVALID_DTX_SETTING;
	movi	a2, -0x6c	# <retval>,
	j	.L1		#
.L22:
# @OPUS@\upstream\silk\check_control_input.c:82:         return SILK_ENC_INVALID_CBR_SETTING;
	movi	a2, -0x6d	# <retval>,
	j	.L1		#
.L23:
# @OPUS@\upstream\silk\check_control_input.c:86:         return SILK_ENC_INVALID_INBAND_FEC_SETTING;
	movi	a2, -0x6b	# <retval>,
	j	.L1		#
.L25:
# @OPUS@\upstream\silk\check_control_input.c:90:         return SILK_ENC_INVALID_NUMBER_OF_CHANNELS_ERROR;
	movi	a2, -0x6f	# <retval>,
.L1:
# @OPUS@\upstream\silk\check_control_input.c:106: }
	l32i.n	a12, sp, 12	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	check_control_input, .-check_control_input
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
