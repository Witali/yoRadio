# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/dec_API.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"dec_API.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\dec_API.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\dec_API.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\dec_API.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\dec_API.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\dec_API.c.s.raw
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
	.section	.text.silk_LoadOSCEModels,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_LoadOSCEModels
	.type	silk_LoadOSCEModels, @function
# Function: silk_LoadOSCEModels
# Module: upstream/silk/dec_API.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context:
# C context:
# C context: opus_int silk_LoadOSCEModels(void *decState, const unsigned char *data, int len)
# C context: {
# C context: #ifdef ENABLE_OSCE
# C context: opus_int ret = SILK_NO_ERROR;
# C context:
silk_LoadOSCEModels:
# @OPUS@\upstream\silk\dec_API.c:78: }
	movi.n	a2, 0	#,
	ret.n
	.size	silk_LoadOSCEModels, .-silk_LoadOSCEModels
	.section	.text.silk_Get_Decoder_Size,"ax",@progbits
	.literal_position
	.literal .LC1, 6008
	.align	4
	.global	silk_Get_Decoder_Size
	.type	silk_Get_Decoder_Size, @function
# Function: silk_Get_Decoder_Size
# Module: upstream/silk/dec_API.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: opus_int silk_Get_Decoder_Size(                         /* O    Returns error code                              */
# C context: opus_int                        *decSizeBytes       /* O    Number of bytes in SILK decoder state           */
# C context: )
# C context: {
# C context: opus_int ret = SILK_NO_ERROR;
silk_Get_Decoder_Size:
# @OPUS@\upstream\silk\dec_API.c:86:     *decSizeBytes = sizeof( silk_decoder );
	l32r	a3, .LC1	#, tmp44
	s32i.n	a3, a2, 0	# *decSizeBytes_2(D), tmp44
# @OPUS@\upstream\silk\dec_API.c:89: }
	movi.n	a2, 0	#,
	ret.n
	.size	silk_Get_Decoder_Size, .-silk_Get_Decoder_Size
	.section	.text.silk_ResetDecoder,"ax",@progbits
	.literal_position
	.literal .LC2, 2992
	.literal .LC3, 5984
	.align	4
	.global	silk_ResetDecoder
	.type	silk_ResetDecoder, @function
# Function: silk_ResetDecoder
# Module: upstream/silk/dec_API.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Reset decoder state */
# C context: opus_int silk_ResetDecoder(                              /* O    Returns error code                              */
# C context: void                            *decState           /* I/O  State                                           */
# C context: )
# C context: {
# C context: opus_int n, ret = SILK_NO_ERROR;
silk_ResetDecoder:
	addi	sp, sp, -16	#,,
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\silk\dec_API.c:95: {
	mov.n	a12, a2	# decState, decState
# @OPUS@\upstream\silk\dec_API.c:100:         ret  = silk_reset_decoder( &channel_state[ n ] );
	call0	silk_reset_decoder		#
	l32r	a2, .LC2	#, tmp48
	add.n	a2, a12, a2	#, decState, tmp48
	call0	silk_reset_decoder		#
# @OPUS@\upstream\silk\dec_API.c:102:     silk_memset(&((silk_decoder *)decState)->sStereo, 0, sizeof(((silk_decoder *)decState)->sStereo));
	l32r	a3, .LC3	#, tmp50
	movi.n	a4, 0	# tmp52,
	add.n	a3, a12, a3	# tmp49, decState, tmp50
	s8i	a4, a3, 0	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 1	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 2	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 3	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 4	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 5	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 6	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 7	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 8	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 9	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 10	# MEM[(void *)decState_9(D) + 5984B], tmp52
	s8i	a4, a3, 11	# MEM[(void *)decState_9(D) + 5984B], tmp52
# @OPUS@\upstream\silk\dec_API.c:107: }
	l32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\dec_API.c:104:     ((silk_decoder *)decState)->prev_decode_only_middle = 0;
	addmi	a12, a12, 0x1700	# tmp64, decState,
	movi.n	a3, 0	# tmp65,
	s32i	a3, a12, 116	# MEM[(struct silk_decoder *)decState_9(D)].prev_decode_only_middle, tmp65
# @OPUS@\upstream\silk\dec_API.c:107: }
	l32i.n	a12, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_ResetDecoder, .-silk_ResetDecoder
	.section	.text.silk_InitDecoder,"ax",@progbits
	.literal_position
	.literal .LC4, 2560
	.literal .LC5, 2992
	.literal .LC6, 5984
	.align	4
	.global	silk_InitDecoder
	.type	silk_InitDecoder, @function
# Function: silk_InitDecoder
# Module: upstream/silk/dec_API.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context:
# C context: opus_int silk_InitDecoder(                              /* O    Returns error code                              */
# C context: void                            *decState           /* I/O  State                                           */
# C context: )
# C context: {
# C context: opus_int n, ret = SILK_NO_ERROR;
silk_InitDecoder:
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 8	#,
	mov.n	a12, a2	# decState, decState
# @OPUS@\upstream\silk\dec_API.c:119:     opus_int32 *exc = yoradio_opus_history(DECODER_NUM_CHANNELS * MAX_FRAME_LENGTH * sizeof(opus_int32));
	l32r	a2, .LC4	#,
# @OPUS@\upstream\silk\dec_API.c:113: {
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\dec_API.c:119:     opus_int32 *exc = yoradio_opus_history(DECODER_NUM_CHANNELS * MAX_FRAME_LENGTH * sizeof(opus_int32));
	call0	yoradio_opus_history		#
# @OPUS@\upstream\silk\dec_API.c:120:     if (!exc) return OPUS_ALLOC_FAIL;
	beqz.n	a2, .L7	# exc,
# @OPUS@\upstream\silk\dec_API.c:122:         channel_state[n].exc_Q14 = exc + n * MAX_FRAME_LENGTH;
	addmi	a3, a12, 0xb00	# tmp50, decState,
	s32i.n	a2, a12, 0	# MEM[(struct silk_decoder_state *)decState_19(D)].exc_Q14, exc
# @OPUS@\upstream\silk\dec_API.c:122:         channel_state[n].exc_Q14 = exc + n * MAX_FRAME_LENGTH;
	addmi	a2, a2, 0x500	# tmp51, exc,
# @OPUS@\upstream\silk\dec_API.c:122:         channel_state[n].exc_Q14 = exc + n * MAX_FRAME_LENGTH;
	s32i	a2, a3, 176	# MEM[(struct silk_decoder_state *)decState_19(D) + 2992B].exc_Q14, tmp51
# @OPUS@\upstream\silk\dec_API.c:133:         ret  = silk_init_decoder( &channel_state[ n ] );
	mov.n	a2, a12	#, decState
	call0	silk_init_decoder		#
# @OPUS@\upstream\silk\dec_API.c:122:         channel_state[n].exc_Q14 = exc + n * MAX_FRAME_LENGTH;
	l32r	a2, .LC5	#, tmp53
# @OPUS@\upstream\silk\dec_API.c:133:         ret  = silk_init_decoder( &channel_state[ n ] );
	add.n	a2, a12, a2	#, decState, tmp53
	call0	silk_init_decoder		#
# @OPUS@\upstream\silk\dec_API.c:135:     silk_memset(&((silk_decoder *)decState)->sStereo, 0, sizeof(((silk_decoder *)decState)->sStereo));
	l32r	a3, .LC6	#, tmp55
	movi.n	a4, 0	# tmp57,
	add.n	a3, a12, a3	# tmp54, decState, tmp55
	s8i	a4, a3, 0	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 1	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 2	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 3	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 4	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 5	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 6	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 7	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 8	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 9	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 10	# MEM[(void *)decState_19(D) + 5984B], tmp57
	s8i	a4, a3, 11	# MEM[(void *)decState_19(D) + 5984B], tmp57
# @OPUS@\upstream\silk\dec_API.c:137:     ((silk_decoder *)decState)->prev_decode_only_middle = 0;
	addmi	a12, a12, 0x1700	# tmp69, decState,
	movi.n	a3, 0	# tmp70,
	s32i	a3, a12, 116	# MEM[(struct silk_decoder *)decState_19(D)].prev_decode_only_middle, tmp70
# @OPUS@\upstream\silk\dec_API.c:139:     return ret;
	j	.L5		#
.L7:
# @OPUS@\upstream\silk\dec_API.c:120:     if (!exc) return OPUS_ALLOC_FAIL;
	movi.n	a2, -7	# <retval>,
.L5:
# @OPUS@\upstream\silk\dec_API.c:140: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_InitDecoder, .-silk_InitDecoder
	.global	__divsi3
	.section	.rodata
	.align	4
.LC0:
	.word	6
	.word	4
	.word	3
	.section	.text.silk_Decode,"ax",@progbits
	.literal_position
	.literal .LC7, 2992
	.literal .LC8, 5984
	.literal .LC9, 5992
	.literal .LC10, -8000
	.literal .LC11, 40000
	.literal .LC12, silk_LBRR_flags_iCDF_ptr
	.literal .LC13, 4136
	.literal .LC14, -2996
	.literal .LC15, 3064
	.literal .LC16, 3000
	.literal .LC17, 5988
	.literal .LC18, .LC0
	.align	4
	.global	silk_Decode
	.type	silk_Decode, @function
# Function: silk_Decode
# Module: upstream/silk/dec_API.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Decode a frame */
# C context: opus_int silk_Decode(                                   /* O    Returns error code                              */
# C context: void*                           decState,           /* I/O  State                                           */
# C context: silk_DecControlStruct*          decControl,         /* I/O  Control Structure                               */
# C context: opus_int                        lostFlag,           /* I    0: no loss, 1 loss, 2 decode fec                */
# C context: opus_int                        newPacketFlag,      /* I    Indicates first decoder call for this packet    */
silk_Decode:
	movi	a9, 0x310	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\dec_API.c:163:     opus_int32 MS_pred_Q13[ 2 ] = { 0 };
	addi	a8, sp, 16	#,,
# @OPUS@\upstream\silk\dec_API.c:156: {
	s32i	a12, sp, 776	#,
# @OPUS@\upstream\silk\dec_API.c:157:     opus_int   i, n, decode_only_middle = 0, ret = SILK_NO_ERROR;
	movi.n	a12, 0	# tmp346,
# @OPUS@\upstream\silk\dec_API.c:156: {
	s32i	a15, sp, 764	#,
	s32i	a13, sp, 772	#,
# @OPUS@\upstream\silk\dec_API.c:163:     opus_int32 MS_pred_Q13[ 2 ] = { 0 };
	addmi	a15, a8, 0x200	# tmp347,,
# @OPUS@\upstream\silk\dec_API.c:156: {
	s32i	a14, sp, 768	#,
	mov.n	a13, a3	# decControl, decControl
	s32i	a0, sp, 780	#,
# @OPUS@\upstream\silk\dec_API.c:156: {
	s32i	a2, sp, 704	# %sfp, decState
	s32i	a4, sp, 712	# %sfp, lostFlag
	mov.n	a14, a5	# newPacketFlag, newPacketFlag
	s32i	a6, sp, 728	# %sfp, psRangeDec
	s32i	a7, sp, 724	# %sfp, samplesOut
# @OPUS@\upstream\silk\dec_API.c:157:     opus_int   i, n, decode_only_middle = 0, ret = SILK_NO_ERROR;
	s32i	a12, sp, 684	# decode_only_middle, tmp346
# @OPUS@\upstream\silk\dec_API.c:163:     opus_int32 MS_pred_Q13[ 2 ] = { 0 };
	s32i	a12, sp, 664	# MS_pred_Q13, tmp346
	s32i	a12, sp, 668	# MS_pred_Q13, tmp346
# @OPUS@\upstream\silk\dec_API.c:170:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i	a3, a15, 132	# _saved_stack,
	s32i	a2, a15, 128	# _saved_stack,
# @OPUS@\upstream\silk\dec_API.c:178:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
# @OPUS@\upstream\silk\dec_API.c:177:     if( newPacketFlag ) {
	beq	a14, a12, .L10	# newPacketFlag,,
# @OPUS@\upstream\silk\dec_API.c:178:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blti	a3, 1, .L10	# prephitmp_630,,
	l32r	a8, .LC7	#,
	movi	a4, 0x458	# tmp352,
	s32i	a8, sp, 692	# %sfp,
	mull	a5, a3, a8	# tmp353, prephitmp_630,
	l32i	a8, sp, 704	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:179:             channel_state[ n ].nFramesDecoded = 0;  /* Used to count frames in packet */
	l32i	a6, sp, 692	# %sfp, tmp858
	add.n	a5, a8, a5	# tmp355,, tmp353
	add.n	a2, a8, a4	# ivtmp$131,, tmp352
	add.n	a5, a5, a4	# _809, tmp355, tmp352
	mov.n	a4, a12	# tmp357, tmp346
.L11:
# @OPUS@\upstream\silk\dec_API.c:179:             channel_state[ n ].nFramesDecoded = 0;  /* Used to count frames in packet */
	s32i.n	a4, a2, 0	# MEM[base: _39, offset: 0B], tmp357
	add.n	a2, a2, a6	# ivtmp$131, ivtmp$131, tmp858
# @OPUS@\upstream\silk\dec_API.c:178:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	bne	a2, a5, .L11	# ivtmp$131, _809,
.L10:
# @OPUS@\upstream\silk\dec_API.c:184:     if( decControl->nChannelsInternal > psDec->nChannelsInternal ) {
	l32i	a8, sp, 704	# %sfp,
	addmi	a8, a8, 0x1700	#,,
	s32i	a8, sp, 720	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:184:     if( decControl->nChannelsInternal > psDec->nChannelsInternal ) {
	l32i	a2, a8, 112	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal, MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal
# @OPUS@\upstream\silk\dec_API.c:157:     opus_int   i, n, decode_only_middle = 0, ret = SILK_NO_ERROR;
	movi.n	a8, 0	#,
	s32i	a8, sp, 688	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:184:     if( decControl->nChannelsInternal > psDec->nChannelsInternal ) {
	bge	a2, a3, .L12	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal, prephitmp_630,
# @OPUS@\upstream\silk\dec_API.c:185:         ret += silk_init_decoder( &channel_state[ 1 ] );
	l32i	a3, sp, 704	# %sfp,
	l32r	a8, .LC7	#,
	add.n	a2, a3, a8	#,,
	call0	silk_init_decoder		#
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
	s32i	a2, sp, 688	# %sfp,
.L12:
	l32i	a8, sp, 704	# %sfp,
	addmi	a8, a8, 0x400	#,,
	s32i	a8, sp, 708	# %sfp,
	l32i	a8, a8, 88	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded,
	s32i	a8, sp, 736	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	bnei	a3, 1, .L13	# prephitmp_630,,
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	l32i	a8, sp, 720	# %sfp,
	l32i	a2, a8, 112	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal, MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal
	bnei	a2, 2, .L14	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal,,
# @OPUS@\upstream\silk\dec_API.c:189:                      ( decControl->internalSampleRate == 1000*channel_state[ 0 ].fs_kHz );
	l32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	l32i.n	a5, a13, 12	# decControl_322(D)->internalSampleRate, decControl_322(D)->internalSampleRate
# @OPUS@\upstream\silk\dec_API.c:189:                      ( decControl->internalSampleRate == 1000*channel_state[ 0 ].fs_kHz );
	l32i.n	a4, a8, 16	# MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz, MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz
	slli	a2, a4, 5	# tmp369, MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz,
	sub	a2, a2, a4	# tmp370, tmp369, MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz
	slli	a2, a2, 2	# tmp371, tmp370,
	add.n	a2, a2, a4	# tmp372, tmp371, MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz
	slli	a2, a2, 3	# tmp373, tmp372,
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	bne	a5, a2, .L14	# decControl_322(D)->internalSampleRate, tmp373,
	j	.L15		#
.L13:
# @OPUS@\upstream\silk\dec_API.c:191:     if( channel_state[ 0 ].nFramesDecoded == 0 ) {
	bnez.n	a8, .L120	#,
# @OPUS@\upstream\silk\dec_API.c:192:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	bgei	a3, 1, .L115	# prephitmp_630,,
	j	.L16		#
.L126:
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	s32i	a3, sp, 736	# %sfp, prephitmp_630
.L115:
	l32i	a8, sp, 704	# %sfp,
	movi.n	a15, 0	# n,
	movi	a14, 0x418	# tmp375,
	add.n	a14, a8, a14	# ivtmp$126,, tmp375
# @OPUS@\upstream\silk\dec_API.c:204:             } else if( decControl->payloadSize_ms == 40 ) {
	mov.n	a2, a15	# n, n
# @OPUS@\upstream\silk\dec_API.c:201:             } else if( decControl->payloadSize_ms == 20 ) {
	movi.n	a12, 0x14	# tmp906,
# @OPUS@\upstream\silk\dec_API.c:204:             } else if( decControl->payloadSize_ms == 40 ) {
	mov.n	a15, a14	# ivtmp$126, ivtmp$126
	mov.n	a14, a2	# n, n
.L25:
# @OPUS@\upstream\silk\dec_API.c:194:             if( decControl->payloadSize_ms == 0 ) {
	l32i.n	a2, a13, 16	# decControl_322(D)->payloadSize_ms, _14
# @OPUS@\upstream\silk\dec_API.c:194:             if( decControl->payloadSize_ms == 0 ) {
	bnez.n	a2, .L17	# _14,
	j	.L231		#
.L17:
# @OPUS@\upstream\silk\dec_API.c:198:             } else if( decControl->payloadSize_ms == 10 ) {
	bnei	a2, 10, .L19	# _14,,
.L231:
# @OPUS@\upstream\silk\dec_API.c:199:                 channel_state[ n ].nFramesPerPacket = 1;
	movi.n	a3, 1	# tmp380,
	movi	a2, -0x418	# tmp379,
	s32i	a3, a15, 68	#, tmp380
# @OPUS@\upstream\silk\dec_API.c:200:                 channel_state[ n ].nb_subfr = 2;
	movi.n	a3, 2	# tmp381,
	add.n	a2, a15, a2	# _261, ivtmp$126, tmp379
	s32i.n	a3, a15, 0	#* ivtmp$126, tmp381
	j	.L18		#
.L19:
# @OPUS@\upstream\silk\dec_API.c:201:             } else if( decControl->payloadSize_ms == 20 ) {
	bne	a2, a12, .L20	# _14, tmp906,
# @OPUS@\upstream\silk\dec_API.c:202:                 channel_state[ n ].nFramesPerPacket = 1;
	movi.n	a3, 1	# tmp384,
	movi	a2, -0x418	# tmp383,
	s32i	a3, a15, 68	#, tmp384
# @OPUS@\upstream\silk\dec_API.c:203:                 channel_state[ n ].nb_subfr = 4;
	movi.n	a3, 4	# tmp385,
	add.n	a2, a15, a2	# _261, ivtmp$126, tmp383
	s32i.n	a3, a15, 0	#* ivtmp$126, tmp385
	j	.L18		#
.L20:
# @OPUS@\upstream\silk\dec_API.c:204:             } else if( decControl->payloadSize_ms == 40 ) {
	movi.n	a3, 0x28	#,
	bne	a2, a3, .L21	# _14,,
# @OPUS@\upstream\silk\dec_API.c:205:                 channel_state[ n ].nFramesPerPacket = 2;
	movi.n	a3, 2	# tmp388,
	movi	a2, -0x418	# tmp387,
	s32i	a3, a15, 68	#, tmp388
# @OPUS@\upstream\silk\dec_API.c:206:                 channel_state[ n ].nb_subfr = 4;
	movi.n	a3, 4	# tmp389,
	add.n	a2, a15, a2	# _261, ivtmp$126, tmp387
	s32i.n	a3, a15, 0	#* ivtmp$126, tmp389
	j	.L18		#
.L21:
# @OPUS@\upstream\silk\dec_API.c:207:             } else if( decControl->payloadSize_ms == 60 ) {
	movi.n	a3, 0x3c	# tmp390,
	bne	a2, a3, .L22	# _14, tmp390,
# @OPUS@\upstream\silk\dec_API.c:208:                 channel_state[ n ].nFramesPerPacket = 3;
	movi.n	a3, 3	# tmp392,
	movi	a2, -0x418	# tmp391,
	s32i	a3, a15, 68	#, tmp392
# @OPUS@\upstream\silk\dec_API.c:209:                 channel_state[ n ].nb_subfr = 4;
	movi.n	a3, 4	# tmp393,
	add.n	a2, a15, a2	# _261, ivtmp$126, tmp391
	s32i.n	a3, a15, 0	#* ivtmp$126, tmp393
	j	.L18		#
.L22:
# @OPUS@\upstream\silk\dec_API.c:212:                 RESTORE_STACK;
	l32i	a2, sp, 656	# _saved_stack,
	l32i	a3, sp, 660	# _saved_stack,
# @OPUS@\upstream\silk\dec_API.c:213:                 return SILK_DEC_INVALID_FRAME_SIZE;
	movi	a8, -0xcb	#,
	s32i	a8, sp, 688	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:212:                 RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\dec_API.c:213:                 return SILK_DEC_INVALID_FRAME_SIZE;
	j	.L8		#
.L18:
# @OPUS@\upstream\silk\dec_API.c:215:             fs_kHz_dec = ( decControl->internalSampleRate >> 10 ) + 1;
	l32i.n	a4, a13, 12	# decControl_322(D)->internalSampleRate, decControl_322(D)->internalSampleRate
# @OPUS@\upstream\silk\dec_API.c:216:             if( fs_kHz_dec != 8 && fs_kHz_dec != 12 && fs_kHz_dec != 16 ) {
	movi.n	a5, -5	# tmp397,
# @OPUS@\upstream\silk\dec_API.c:215:             fs_kHz_dec = ( decControl->internalSampleRate >> 10 ) + 1;
	srai	a4, a4, 10	# tmp395, decControl_322(D)->internalSampleRate,
# @OPUS@\upstream\silk\dec_API.c:215:             fs_kHz_dec = ( decControl->internalSampleRate >> 10 ) + 1;
	addi.n	a3, a4, 1	# fs_kHz_dec, tmp395,
# @OPUS@\upstream\silk\dec_API.c:216:             if( fs_kHz_dec != 8 && fs_kHz_dec != 12 && fs_kHz_dec != 16 ) {
	and	a5, a3, a5	# tmp398, fs_kHz_dec, tmp397
# @OPUS@\upstream\silk\dec_API.c:216:             if( fs_kHz_dec != 8 && fs_kHz_dec != 12 && fs_kHz_dec != 16 ) {
	beqi	a5, 8, .L24	# tmp398,,
	addi	a4, a4, -15	# tmp407, tmp395,
	beqz.n	a4, .L24	# tmp407,
.L30:
# @OPUS@\upstream\silk\dec_API.c:218:                 RESTORE_STACK;
	addi	a2, sp, 16	#,,
	addmi	a3, a2, 0x200	# tmp411,,
	l32i	a3, a3, 132	# _saved_stack,
	l32i	a2, sp, 656	# _saved_stack,
# @OPUS@\upstream\silk\dec_API.c:219:                 return SILK_DEC_INVALID_SAMPLING_FREQUENCY;
	movi	a8, -0xc8	#,
	s32i	a8, sp, 688	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:218:                 RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\dec_API.c:219:                 return SILK_DEC_INVALID_SAMPLING_FREQUENCY;
	j	.L8		#
.L24:
# @OPUS@\upstream\silk\dec_API.c:221:             ret += silk_decoder_set_fs( &channel_state[ n ], fs_kHz_dec, decControl->API_sampleRate );
	l32i.n	a4, a13, 8	# decControl_322(D)->API_sampleRate,
# @OPUS@\upstream\silk\dec_API.c:192:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	addi.n	a14, a14, 1	# n, n,
# @OPUS@\upstream\silk\dec_API.c:221:             ret += silk_decoder_set_fs( &channel_state[ n ], fs_kHz_dec, decControl->API_sampleRate );
	call0	silk_decoder_set_fs		#
# @OPUS@\upstream\silk\dec_API.c:221:             ret += silk_decoder_set_fs( &channel_state[ n ], fs_kHz_dec, decControl->API_sampleRate );
	l32i	a8, sp, 688	# %sfp,
	l32r	a4, .LC7	#, tmp858
	add.n	a8, a8, a2	#,,
# @OPUS@\upstream\silk\dec_API.c:192:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
# @OPUS@\upstream\silk\dec_API.c:221:             ret += silk_decoder_set_fs( &channel_state[ n ], fs_kHz_dec, decControl->API_sampleRate );
	s32i	a8, sp, 688	# %sfp,
	add.n	a15, a15, a4	# ivtmp$126, ivtmp$126, tmp858
# @OPUS@\upstream\silk\dec_API.c:192:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blt	a14, a3, .L25	# n, prephitmp_630,
	j	.L16		#
.L227:
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	l32i.n	a15, a13, 0	# decControl_322(D)->nChannelsAPI, prephitmp_638
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	s32i	a3, sp, 736	# %sfp, prephitmp_630
	j	.L26		#
.L120:
	movi.n	a8, 0	#,
	s32i	a8, sp, 736	# %sfp,
.L16:
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	l32i.n	a15, a13, 0	# decControl_322(D)->nChannelsAPI, prephitmp_638
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	bnei	a15, 2, .L26	# prephitmp_638,,
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	bnei	a3, 2, .L117	# prephitmp_630,,
	j	.L28		#
.L117:
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	movi.n	a15, 2	# prephitmp_638,
	j	.L26		#
.L28:
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	l32i	a8, sp, 720	# %sfp,
	l32i	a2, a8, 108	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsAPI, MEM[(struct silk_decoder *)decState_318(D)].nChannelsAPI
	beqi	a2, 1, .L29	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsAPI,,
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	l32i	a2, a8, 112	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal, MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal
	mov.n	a15, a3	# prephitmp_638, prephitmp_630
	bnei	a2, 1, .L26	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal,,
.L29:
# @OPUS@\upstream\silk\dec_API.c:228:         silk_memcpy( &channel_state[ 1 ].resampler_state, &channel_state[ 0 ].resampler_state, sizeof( silk_resampler_state_struct ) );
	l32r	a8, .LC7	#,
# @OPUS@\upstream\silk\dec_API.c:226:         silk_memset( psDec->sStereo.pred_prev_Q13, 0, sizeof( psDec->sStereo.pred_prev_Q13 ) );
	l32r	a2, .LC8	#, tmp418
# @OPUS@\upstream\silk\dec_API.c:228:         silk_memcpy( &channel_state[ 1 ].resampler_state, &channel_state[ 0 ].resampler_state, sizeof( silk_resampler_state_struct ) );
	s32i	a8, sp, 692	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:226:         silk_memset( psDec->sStereo.pred_prev_Q13, 0, sizeof( psDec->sStereo.pred_prev_Q13 ) );
	l32i	a8, sp, 704	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:227:         silk_memset( psDec->sStereo.sSide, 0, sizeof( psDec->sStereo.sSide ) );
	l32r	a4, .LC9	#, tmp425
# @OPUS@\upstream\silk\dec_API.c:228:         silk_memcpy( &channel_state[ 1 ].resampler_state, &channel_state[ 0 ].resampler_state, sizeof( silk_resampler_state_struct ) );
	l32i	a6, sp, 692	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:226:         silk_memset( psDec->sStereo.pred_prev_Q13, 0, sizeof( psDec->sStereo.pred_prev_Q13 ) );
	movi.n	a3, 0	# tmp420,
	add.n	a2, a8, a2	# tmp417,, tmp418
	s8i	a3, a2, 0	# MEM[(void *)decState_318(D) + 5984B], tmp420
	s8i	a3, a2, 1	# MEM[(void *)decState_318(D) + 5984B], tmp420
	s8i	a3, a2, 2	# MEM[(void *)decState_318(D) + 5984B], tmp420
	s8i	a3, a2, 3	# MEM[(void *)decState_318(D) + 5984B], tmp420
# @OPUS@\upstream\silk\dec_API.c:227:         silk_memset( psDec->sStereo.sSide, 0, sizeof( psDec->sStereo.sSide ) );
	add.n	a4, a8, a4	# tmp424,, tmp425
# @OPUS@\upstream\silk\dec_API.c:228:         silk_memcpy( &channel_state[ 1 ].resampler_state, &channel_state[ 0 ].resampler_state, sizeof( silk_resampler_state_struct ) );
	movi	a2, 0x484	# tmp433,
	add.n	a5, a8, a6	# tmp431,,
# @OPUS@\upstream\silk\dec_API.c:227:         silk_memset( psDec->sStereo.sSide, 0, sizeof( psDec->sStereo.sSide ) );
	s8i	a3, a4, 0	# MEM[(void *)decState_318(D) + 5992B], tmp420
	s8i	a3, a4, 1	# MEM[(void *)decState_318(D) + 5992B], tmp420
	s8i	a3, a4, 2	# MEM[(void *)decState_318(D) + 5992B], tmp420
	s8i	a3, a4, 3	# MEM[(void *)decState_318(D) + 5992B], tmp420
# @OPUS@\upstream\silk\dec_API.c:228:         silk_memcpy( &channel_state[ 1 ].resampler_state, &channel_state[ 0 ].resampler_state, sizeof( silk_resampler_state_struct ) );
	add.n	a3, a8, a2	#,, tmp433
	movi	a4, 0x12c	#,
	add.n	a2, a5, a2	#, tmp431, tmp433
	call0	memcpy		#
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
	l32i.n	a15, a13, 0	# decControl_322(D)->nChannelsAPI, prephitmp_638
.L26:
# @OPUS@\upstream\silk\dec_API.c:233:     if( decControl->API_sampleRate > (opus_int32)MAX_API_FS_KHZ * 1000 || decControl->API_sampleRate < 8000 ) {
	l32i.n	a4, a13, 8	# decControl_322(D)->API_sampleRate, _55
# @OPUS@\upstream\silk\dec_API.c:230:     psDec->nChannelsAPI      = decControl->nChannelsAPI;
	l32i	a8, sp, 720	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:233:     if( decControl->API_sampleRate > (opus_int32)MAX_API_FS_KHZ * 1000 || decControl->API_sampleRate < 8000 ) {
	l32r	a2, .LC10	#, tmp445
# @OPUS@\upstream\silk\dec_API.c:233:     if( decControl->API_sampleRate > (opus_int32)MAX_API_FS_KHZ * 1000 || decControl->API_sampleRate < 8000 ) {
	l32r	a5, .LC11	#, tmp446
# @OPUS@\upstream\silk\dec_API.c:230:     psDec->nChannelsAPI      = decControl->nChannelsAPI;
	s32i	a15, a8, 108	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsAPI, prephitmp_638
# @OPUS@\upstream\silk\dec_API.c:231:     psDec->nChannelsInternal = decControl->nChannelsInternal;
	s32i	a3, a8, 112	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal, prephitmp_630
# @OPUS@\upstream\silk\dec_API.c:233:     if( decControl->API_sampleRate > (opus_int32)MAX_API_FS_KHZ * 1000 || decControl->API_sampleRate < 8000 ) {
	add.n	a2, a4, a2	# tmp444, _55, tmp445
# @OPUS@\upstream\silk\dec_API.c:233:     if( decControl->API_sampleRate > (opus_int32)MAX_API_FS_KHZ * 1000 || decControl->API_sampleRate < 8000 ) {
	bltu	a5, a2, .L30	# tmp446, tmp444,
# @OPUS@\upstream\silk\dec_API.c:239:     if( lostFlag != FLAG_PACKET_LOST && channel_state[ 0 ].nFramesDecoded == 0 ) {
	l32i	a8, sp, 712	# %sfp,
	beqi	a8, 1, .L31	#,,
# @OPUS@\upstream\silk\dec_API.c:239:     if( lostFlag != FLAG_PACKET_LOST && channel_state[ 0 ].nFramesDecoded == 0 ) {
	l32i	a8, sp, 708	# %sfp,
	l32i	a8, a8, 88	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded,
	s32i	a8, sp, 700	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:239:     if( lostFlag != FLAG_PACKET_LOST && channel_state[ 0 ].nFramesDecoded == 0 ) {
	bnez.n	a8, .L32	#,
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blti	a3, 1, .L33	# prephitmp_630,,
	mov.n	a4, a8	#,
	l32i	a8, sp, 704	# %sfp,
	movi	a12, 0x45c	# tmp448,
	add.n	a12, a8, a12	# ivtmp$109,, tmp448
	l32r	a8, .LC7	#,
	mov.n	a15, a12	# ivtmp$118, ivtmp$109
	s32i	a12, sp, 732	# %sfp, ivtmp$109
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	s32i	a4, sp, 696	# %sfp,
	s32i	a8, sp, 692	# %sfp,
	s32i	a13, sp, 716	# %sfp, decControl
	l32i	a12, sp, 728	# %sfp, psRangeDec
	j	.L34		#
.L35:
# @OPUS@\upstream\silk\dec_API.c:244:                 channel_state[ n ].VAD_flags[ i ] = ec_dec_bit_logp(psRangeDec, 1);
	movi.n	a3, 1	#,
	mov.n	a2, a12	#, psRangeDec
	call0	ec_dec_bit_logp		#
# @OPUS@\upstream\silk\dec_API.c:244:                 channel_state[ n ].VAD_flags[ i ] = ec_dec_bit_logp(psRangeDec, 1);
	s32i.n	a2, a14, 0	# MEM[base: _305, offset: 0B],
# @OPUS@\upstream\silk\dec_API.c:243:             for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	l32i.n	a2, a15, 0	# MEM[base: _287, offset: 0B], MEM[base: _287, offset: 0B]
# @OPUS@\upstream\silk\dec_API.c:243:             for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	addi.n	a13, a13, 1	# i, i,
	addi.n	a14, a14, 4	# ivtmp$113, ivtmp$113,
# @OPUS@\upstream\silk\dec_API.c:243:             for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	blt	a13, a2, .L35	# i, MEM[base: _287, offset: 0B],
.L38:
# @OPUS@\upstream\silk\dec_API.c:246:             channel_state[ n ].LBRR_flag = ec_dec_bit_logp(psRangeDec, 1);
	movi.n	a3, 1	#,
	mov.n	a2, a12	#, psRangeDec
	call0	ec_dec_bit_logp		#
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i	a5, sp, 696	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i	a4, sp, 716	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:246:             channel_state[ n ].LBRR_flag = ec_dec_bit_logp(psRangeDec, 1);
	s32i.n	a2, a15, 24	# MEM[base: _287, offset: 24B],
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	addi.n	a5, a5, 1	#,,
	l32i	a8, sp, 692	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i.n	a3, a4, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	s32i	a5, sp, 696	# %sfp,
	add.n	a15, a15, a8	# ivtmp$118, ivtmp$118,
# @OPUS@\upstream\silk\dec_API.c:242:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	bge	a5, a3, .L36	#, prephitmp_630,
.L34:
# @OPUS@\upstream\silk\dec_API.c:243:             for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	l32i.n	a2, a15, 0	# MEM[base: _287, offset: 0B], MEM[base: _287, offset: 0B]
	addi.n	a14, a15, 12	# ivtmp$113, ivtmp$118,
# @OPUS@\upstream\silk\dec_API.c:243:             for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	l32i	a13, sp, 700	# %sfp, i
# @OPUS@\upstream\silk\dec_API.c:243:             for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	bgei	a2, 1, .L35	# MEM[base: _287, offset: 0B],,
	j	.L38		#
.L36:
	mov.n	a13, a4	# decControl,
	l32i	a12, sp, 732	# %sfp, ivtmp$109
# @OPUS@\upstream\silk\dec_API.c:249:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blti	a3, 1, .L33	# prephitmp_630,,
# @OPUS@\upstream\silk\dec_API.c:255:                     LBRR_symbol = ec_dec_icdf( psRangeDec, silk_LBRR_flags_iCDF_ptr[ channel_state[ n ].nFramesPerPacket - 2 ], 8 ) + 1;
	l32r	a14, .LC12	#, tmp903
# @OPUS@\upstream\silk\dec_API.c:250:             silk_memset( channel_state[ n ].LBRR_flags, 0, sizeof( channel_state[ n ].LBRR_flags ) );
	l32i	a13, sp, 700	# %sfp, n
	mov.n	a6, a8	# tmp858,
	movi.n	a15, 0	# tmp453,
	mov.n	a5, a4	# decControl, decControl
.L43:
# @OPUS@\upstream\silk\dec_API.c:251:             if( channel_state[ n ].LBRR_flag ) {
	l32i.n	a2, a12, 24	# MEM[base: _458, offset: 24B], MEM[base: _458, offset: 24B]
# @OPUS@\upstream\silk\dec_API.c:250:             silk_memset( channel_state[ n ].LBRR_flags, 0, sizeof( channel_state[ n ].LBRR_flags ) );
	s8i	a15, a12, 28	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 29	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 30	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 31	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 32	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 33	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 34	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 35	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 36	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 37	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 38	# MEM[(void *)_465], tmp453
	s8i	a15, a12, 39	# MEM[(void *)_465], tmp453
# @OPUS@\upstream\silk\dec_API.c:251:             if( channel_state[ n ].LBRR_flag ) {
	beqz.n	a2, .L40	# MEM[base: _458, offset: 24B],
# @OPUS@\upstream\silk\dec_API.c:252:                 if( channel_state[ n ].nFramesPerPacket == 1 ) {
	l32i.n	a2, a12, 0	# MEM[base: _458, offset: 0B], _71
# @OPUS@\upstream\silk\dec_API.c:252:                 if( channel_state[ n ].nFramesPerPacket == 1 ) {
	bnei	a2, 1, .L41	# _71,,
# @OPUS@\upstream\silk\dec_API.c:253:                     channel_state[ n ].LBRR_flags[ 0 ] = 1;
	s32i.n	a2, a12, 28	# MEM[base: _458, offset: 28B], _71
	j	.L40		#
.L41:
# @OPUS@\upstream\silk\dec_API.c:255:                     LBRR_symbol = ec_dec_icdf( psRangeDec, silk_LBRR_flags_iCDF_ptr[ channel_state[ n ].nFramesPerPacket - 2 ], 8 ) + 1;
	addi	a2, a2, -2	# tmp468, _71,
	slli	a2, a2, 2	# tmp469, tmp468,
	add.n	a2, a14, a2	# tmp470, tmp903, tmp469
# @OPUS@\upstream\silk\dec_API.c:255:                     LBRR_symbol = ec_dec_icdf( psRangeDec, silk_LBRR_flags_iCDF_ptr[ channel_state[ n ].nFramesPerPacket - 2 ], 8 ) + 1;
	l32i.n	a3, a2, 0	# silk_LBRR_flags_iCDF_ptr,
	l32i	a2, sp, 728	# %sfp,
	movi.n	a4, 8	#,
	s32i	a5, sp, 740	#,
	s32i	a6, sp, 744	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\dec_API.c:256:                     for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	l32i.n	a3, a12, 0	# MEM[base: _458, offset: 0B], _489
# @OPUS@\upstream\silk\dec_API.c:255:                     LBRR_symbol = ec_dec_icdf( psRangeDec, silk_LBRR_flags_iCDF_ptr[ channel_state[ n ].nFramesPerPacket - 2 ], 8 ) + 1;
	addi.n	a2, a2, 1	# LBRR_symbol,,
# @OPUS@\upstream\silk\dec_API.c:257:                         channel_state[ n ].LBRR_flags[ i ] = silk_RSHIFT( LBRR_symbol, i ) & 1;
	extui	a4, a2, 0, 1	# tmp471, LBRR_symbol,
	extui	a7, a2, 1, 1	# tmp473, LBRR_symbol,,
# @OPUS@\upstream\silk\dec_API.c:256:                     for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	l32i	a5, sp, 740	#,
# @OPUS@\upstream\silk\dec_API.c:257:                         channel_state[ n ].LBRR_flags[ i ] = silk_RSHIFT( LBRR_symbol, i ) & 1;
	extui	a2, a2, 2, 1	# tmp475, LBRR_symbol,,
# @OPUS@\upstream\silk\dec_API.c:256:                     for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	l32i	a6, sp, 744	#,
	blti	a3, 1, .L40	# _489,,
# @OPUS@\upstream\silk\dec_API.c:257:                         channel_state[ n ].LBRR_flags[ i ] = silk_RSHIFT( LBRR_symbol, i ) & 1;
	s32i.n	a4, a12, 28	# MEM[base: _458, offset: 28B], tmp471
# @OPUS@\upstream\silk\dec_API.c:256:                     for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	beqi	a3, 1, .L40	# _489,,
# @OPUS@\upstream\silk\dec_API.c:257:                         channel_state[ n ].LBRR_flags[ i ] = silk_RSHIFT( LBRR_symbol, i ) & 1;
	s32i.n	a7, a12, 32	# MEM[base: _458, offset: 32B], tmp473
# @OPUS@\upstream\silk\dec_API.c:256:                     for( i = 0; i < channel_state[ n ].nFramesPerPacket; i++ ) {
	beqi	a3, 2, .L40	# _489,,
# @OPUS@\upstream\silk\dec_API.c:257:                         channel_state[ n ].LBRR_flags[ i ] = silk_RSHIFT( LBRR_symbol, i ) & 1;
	s32i.n	a2, a12, 36	# MEM[base: _458, offset: 36B], tmp475
.L40:
# @OPUS@\upstream\silk\dec_API.c:249:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i.n	a3, a5, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
# @OPUS@\upstream\silk\dec_API.c:249:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	addi.n	a13, a13, 1	# n, n,
	add.n	a12, a12, a6	# ivtmp$109, ivtmp$109, tmp858
# @OPUS@\upstream\silk\dec_API.c:249:         for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blt	a13, a3, .L43	# n, prephitmp_630,
	mov.n	a13, a5	# decControl, decControl
.L33:
# @OPUS@\upstream\silk\dec_API.c:263:         if( lostFlag == FLAG_DECODE_NORMAL ) {
	l32i	a8, sp, 712	# %sfp,
	bnez.n	a8, .L44	#,
# @OPUS@\upstream\silk\dec_API.c:265:             for( i = 0; i < channel_state[ 0 ].nFramesPerPacket; i++ ) {
	l32i	a8, sp, 708	# %sfp,
	l32i	a2, a8, 92	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesPerPacket, prephitmp_788
# @OPUS@\upstream\silk\dec_API.c:265:             for( i = 0; i < channel_state[ 0 ].nFramesPerPacket; i++ ) {
	blti	a2, 1, .L45	# prephitmp_788,,
	l32i	a8, sp, 704	# %sfp,
	l32r	a4, .LC13	#, tmp478
# @OPUS@\upstream\silk\dec_API.c:272:                             silk_stereo_decode_pred( psRangeDec, MS_pred_Q13 );
	addi	a7, sp, 16	#,,
	add.n	a4, a8, a4	#,, tmp478
	s32i	a4, sp, 716	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:265:             for( i = 0; i < channel_state[ 0 ].nFramesPerPacket; i++ ) {
	l32i	a8, sp, 712	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:272:                             silk_stereo_decode_pred( psRangeDec, MS_pred_Q13 );
	movi	a4, 0x288	# tmp901,
	add.n	a7, a7, a4	#,, tmp901
# @OPUS@\upstream\silk\dec_API.c:265:             for( i = 0; i < channel_state[ 0 ].nFramesPerPacket; i++ ) {
	s32i	a8, sp, 692	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:272:                             silk_stereo_decode_pred( psRangeDec, MS_pred_Q13 );
	s32i	a7, sp, 732	# %sfp,
	s32i	a13, sp, 696	# %sfp, decControl
	l32i	a12, sp, 728	# %sfp, psRangeDec
	j	.L46		#
.L62:
	l32i	a8, sp, 692	# %sfp,
	bgei	a8, 1, .L47	#,,
	slli	a4, a8, 2	# _483,,
	l32r	a13, .LC7	#, tmp858
	l32i	a8, sp, 704	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:267:                     if( channel_state[ n ].LBRR_flags[ i ] ) {
	movi	a2, -0x159	# tmp481,
	add.n	a2, a4, a2	#, _483, tmp481
	movi	a7, 0x5d1	# tmp479,
	add.n	a14, a8, a7	# ivtmp$89,, tmp479
	s32i	a2, sp, 700	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:266:                 for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i	a15, sp, 712	# %sfp, n
# @OPUS@\upstream\silk\dec_API.c:267:                     if( channel_state[ n ].LBRR_flags[ i ] ) {
	mov.n	a2, a13	# tmp858, tmp858
	mov.n	a13, a14	# ivtmp$89, ivtmp$89
	mov.n	a14, a2	# tmp858, tmp858
.L53:
	l32i	a7, sp, 700	# %sfp,
	movi	a8, -0x5d1	#,
	add.n	a2, a13, a7	# tmp483, ivtmp$89,
# @OPUS@\upstream\silk\dec_API.c:267:                     if( channel_state[ n ].LBRR_flags[ i ] ) {
	l32i.n	a2, a2, 0	# MEM[base: _574, offset: 0B], MEM[base: _574, offset: 0B]
	add.n	a9, a13, a8	# _572, ivtmp$89,
	beqz.n	a2, .L48	# MEM[base: _574, offset: 0B],
# @OPUS@\upstream\silk\dec_API.c:271:                         if( decControl->nChannelsInternal == 2 && n == 0 ) {
	bnei	a3, 2, .L52	# prephitmp_630,,
	beqz.n	a15, .L49	# n,
.L52:
# @OPUS@\upstream\silk\dec_API.c:283:                         silk_decode_indices( &channel_state[ n ], psRangeDec, i, 1, condCoding );
	l32i	a4, sp, 692	# %sfp,
	mov.n	a2, a9	#, _572
	movi.n	a6, 0	#,
	movi.n	a5, 1	#,
	mov.n	a3, a12	#, psRangeDec
	call0	silk_decode_indices		#
# @OPUS@\upstream\silk\dec_API.c:284:                         silk_decode_pulses( psRangeDec, pulses, channel_state[ n ].indices.signalType,
	l8ui	a5, a13, 1	# MEM[base: _579, offset: 1B],
	l8ui	a4, a13, 0	# MEM[base: _579, offset: 0B],
	movi	a2, -0x1b5	# tmp496,
	add.n	a2, a13, a2	# tmp497, ivtmp$89, tmp496
	l32i.n	a6, a2, 0	# MEM[base: _570, offset: 0B],
	slli	a5, a5, 24	# tmp500, MEM[base: _579, offset: 1B],
	slli	a4, a4, 24	# tmp503, MEM[base: _579, offset: 0B],
	addi	a3, sp, 16	#,,
	srai	a5, a5, 24	#, tmp500,
	srai	a4, a4, 24	#, tmp503,
	mov.n	a2, a12	#, psRangeDec
	call0	silk_decode_pulses		#
	l32i	a7, sp, 696	# %sfp,
	l32i.n	a3, a7, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
	j	.L48		#
.L49:
# @OPUS@\upstream\silk\dec_API.c:272:                             silk_stereo_decode_pred( psRangeDec, MS_pred_Q13 );
	l32i	a3, sp, 732	# %sfp,
	mov.n	a2, a12	#, psRangeDec
	s32i	a9, sp, 740	#,
	call0	silk_stereo_decode_pred		#
# @OPUS@\upstream\silk\dec_API.c:273:                             if( channel_state[ 1 ].LBRR_flags[ i ] == 0 ) {
	l32i	a8, sp, 716	# %sfp,
	l32i	a9, sp, 740	#,
	l32i.n	a2, a8, 0	# MEM[base: _482, offset: 0B], MEM[base: _482, offset: 0B]
	bnez.n	a2, .L52	# MEM[base: _482, offset: 0B],
# @OPUS@\upstream\silk\dec_API.c:274:                                 silk_stereo_decode_mid_only( psRangeDec, &decode_only_middle );
	addi	a2, sp, 16	#,,
	movi	a3, 0x29c	# tmp507,
	add.n	a3, a2, a3	#,, tmp507
	mov.n	a2, a12	#, psRangeDec
	call0	silk_stereo_decode_mid_only		#
	l32i	a9, sp, 740	#,
	j	.L52		#
.L48:
# @OPUS@\upstream\silk\dec_API.c:266:                 for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	addi.n	a15, a15, 1	# n, n,
	add.n	a13, a13, a14	# ivtmp$89, ivtmp$89, tmp858
# @OPUS@\upstream\silk\dec_API.c:266:                 for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blt	a15, a3, .L53	# n, prephitmp_630,
	j	.L54		#
.L47:
	l32r	a13, .LC7	#, tmp858
	l32r	a15, .LC14	#, tmp510
	l32i	a7, sp, 716	# %sfp,
	l32i	a8, sp, 704	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:266:                 for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i	a9, sp, 712	# %sfp, n
	movi	a14, 0x5d1	# tmp511,
	mov.n	a10, a13	# tmp858, tmp858
	add.n	a15, a7, a15	# ivtmp$93,, tmp510
	add.n	a14, a8, a14	# ivtmp$97,, tmp511
	mov.n	a13, a9	# n, n
.L61:
# @OPUS@\upstream\silk\dec_API.c:267:                     if( channel_state[ n ].LBRR_flags[ i ] ) {
	l32i.n	a2, a15, 4	# MEM[base: _518, offset: 4B], MEM[base: _518, offset: 4B]
	movi	a8, -0x5d1	# tmp512,
	add.n	a8, a14, a8	# _513, ivtmp$97, tmp512
	beqz.n	a2, .L55	# MEM[base: _518, offset: 4B],
# @OPUS@\upstream\silk\dec_API.c:271:                         if( decControl->nChannelsInternal == 2 && n == 0 ) {
	bnei	a3, 2, .L58	# prephitmp_630,,
	bnez.n	a13, .L58	# n,
# @OPUS@\upstream\silk\dec_API.c:272:                             silk_stereo_decode_pred( psRangeDec, MS_pred_Q13 );
	l32i	a3, sp, 732	# %sfp,
	mov.n	a2, a12	#, psRangeDec
	s32i	a8, sp, 740	#,
	s32i	a10, sp, 744	#,
	call0	silk_stereo_decode_pred		#
# @OPUS@\upstream\silk\dec_API.c:273:                             if( channel_state[ 1 ].LBRR_flags[ i ] == 0 ) {
	l32i	a7, sp, 716	# %sfp,
	l32i	a8, sp, 740	#,
	l32i.n	a2, a7, 0	# MEM[base: _481, offset: 0B], MEM[base: _481, offset: 0B]
	l32i	a10, sp, 744	#,
	bnez.n	a2, .L58	# MEM[base: _481, offset: 0B],
# @OPUS@\upstream\silk\dec_API.c:274:                                 silk_stereo_decode_mid_only( psRangeDec, &decode_only_middle );
	addi	a2, sp, 16	#,,
	movi	a3, 0x29c	# tmp528,
	add.n	a3, a2, a3	#,, tmp528
	mov.n	a2, a12	#, psRangeDec
	call0	silk_stereo_decode_mid_only		#
	l32i	a10, sp, 744	#,
	l32i	a8, sp, 740	#,
.L58:
# @OPUS@\upstream\silk\dec_API.c:278:                         if( i > 0 && channel_state[ n ].LBRR_flags[ i - 1 ] ) {
	l32i.n	a6, a15, 0	# MEM[base: _518, offset: 0B], condCoding
# @OPUS@\upstream\silk\dec_API.c:279:                             condCoding = CODE_CONDITIONALLY;
	movi.n	a2, 2	# tmp860,
# @OPUS@\upstream\silk\dec_API.c:283:                         silk_decode_indices( &channel_state[ n ], psRangeDec, i, 1, condCoding );
	l32i	a4, sp, 692	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:279:                             condCoding = CODE_CONDITIONALLY;
	movnez	a6, a2, a6	# condCoding, tmp860, condCoding
# @OPUS@\upstream\silk\dec_API.c:283:                         silk_decode_indices( &channel_state[ n ], psRangeDec, i, 1, condCoding );
	movi.n	a5, 1	#,
	mov.n	a2, a8	#, _513
	mov.n	a3, a12	#, psRangeDec
	s32i	a10, sp, 744	#,
	call0	silk_decode_indices		#
# @OPUS@\upstream\silk\dec_API.c:284:                         silk_decode_pulses( psRangeDec, pulses, channel_state[ n ].indices.signalType,
	l8ui	a5, a14, 1	# MEM[base: _504, offset: 1B],
	l8ui	a4, a14, 0	# MEM[base: _504, offset: 0B],
	movi	a2, -0x1b5	# tmp530,
	add.n	a2, a14, a2	# tmp531, ivtmp$97, tmp530
	l32i.n	a6, a2, 0	# MEM[base: _511, offset: 0B],
	slli	a5, a5, 24	# tmp534, MEM[base: _504, offset: 1B],
	slli	a4, a4, 24	# tmp537, MEM[base: _504, offset: 0B],
	addi	a3, sp, 16	#,,
	srai	a5, a5, 24	#, tmp534,
	srai	a4, a4, 24	#, tmp537,
	mov.n	a2, a12	#, psRangeDec
	call0	silk_decode_pulses		#
	l32i	a7, sp, 696	# %sfp,
	l32i	a10, sp, 744	#,
	l32i.n	a3, a7, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
.L55:
# @OPUS@\upstream\silk\dec_API.c:266:                 for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	addi.n	a13, a13, 1	# n, n,
	add.n	a15, a15, a10	# ivtmp$93, ivtmp$93, tmp858
	add.n	a14, a14, a10	# ivtmp$97, ivtmp$97, tmp858
# @OPUS@\upstream\silk\dec_API.c:266:                 for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blt	a13, a3, .L61	# n, prephitmp_630,
.L54:
	l32i	a8, sp, 708	# %sfp,
	l32i	a2, a8, 92	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesPerPacket, prephitmp_788
.L63:
# @OPUS@\upstream\silk\dec_API.c:265:             for( i = 0; i < channel_state[ 0 ].nFramesPerPacket; i++ ) {
	l32i	a7, sp, 692	# %sfp,
	l32i	a8, sp, 716	# %sfp,
	addi.n	a7, a7, 1	#,,
	addi.n	a8, a8, 4	#,,
	s32i	a7, sp, 692	# %sfp,
	s32i	a8, sp, 716	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:265:             for( i = 0; i < channel_state[ 0 ].nFramesPerPacket; i++ ) {
	bge	a7, a2, .L229	#, prephitmp_788,
.L46:
# @OPUS@\upstream\silk\dec_API.c:266:                 for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	bgei	a3, 1, .L62	# prephitmp_630,,
	j	.L63		#
.L32:
	l32i	a8, sp, 704	# %sfp,
	addmi	a8, a8, 0xb00	#,,
	s32i	a8, sp, 696	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:293:     if( decControl->nChannelsInternal == 2 ) {
	bnei	a3, 2, .L70	# prephitmp_630,,
# @OPUS@\upstream\silk\dec_API.c:294:         if(   lostFlag == FLAG_DECODE_NORMAL ||
	l32i	a8, sp, 712	# %sfp,
	beqz.n	a8, .L65	#,
.L114:
# @OPUS@\upstream\silk\dec_API.c:294:         if(   lostFlag == FLAG_DECODE_NORMAL ||
	l32i	a8, sp, 712	# %sfp,
	beqi	a8, 2, .L66	#,,
.L69:
# @OPUS@\upstream\silk\dec_API.c:308:                 MS_pred_Q13[ n ] = psDec->sStereo.pred_prev_Q13[ n ];
	l32i	a8, sp, 720	# %sfp,
	l16si	a4, a8, 96	# MEM[(struct silk_decoder *)decState_318(D)].sStereo.pred_prev_Q13, tmp543
	l16si	a3, a8, 98	# MEM[(struct silk_decoder *)decState_318(D)].sStereo.pred_prev_Q13, tmp548
	l32i	a8, sp, 704	# %sfp,
	s32i	a4, sp, 664	# MS_pred_Q13, tmp543
	addmi	a8, a8, 0xb00	#,,
	s32i	a3, sp, 668	# MS_pred_Q13, tmp548
	s32i	a8, sp, 696	# %sfp,
	j	.L67		#
.L66:
# @OPUS@\upstream\silk\dec_API.c:295:             ( lostFlag == FLAG_DECODE_LBRR && channel_state[ 0 ].LBRR_flags[ channel_state[ 0 ].nFramesDecoded ] == 1 ) )
	l32i	a8, sp, 708	# %sfp,
	movi	a12, 0x11c	# tmp551,
	l32i	a2, a8, 88	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded
	l32i	a8, sp, 704	# %sfp,
	add.n	a2, a12, a2	# tmp552, tmp551, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded
	slli	a2, a2, 2	# tmp555, tmp552,
	add.n	a2, a8, a2	# tmp556,, tmp555
# @OPUS@\upstream\silk\dec_API.c:295:             ( lostFlag == FLAG_DECODE_LBRR && channel_state[ 0 ].LBRR_flags[ channel_state[ 0 ].nFramesDecoded ] == 1 ) )
	l32i.n	a2, a2, 8	# MEM[(struct silk_decoder_state *)decState_318(D)].LBRR_flags, tmp558
	bnei	a2, 1, .L69	# tmp558,,
	j	.L68		#
.L111:
# @OPUS@\upstream\silk\dec_API.c:302:                 silk_stereo_decode_mid_only( psRangeDec, &decode_only_middle );
	addi	a2, sp, 16	#,,
	movi	a3, 0x29c	# tmp559,
	add.n	a3, a2, a3	#,, tmp559
	l32i	a2, sp, 728	# %sfp,
	call0	silk_stereo_decode_mid_only		#
# @OPUS@\upstream\silk\dec_API.c:314:     if( decControl->nChannelsInternal == 2 && decode_only_middle == 0 && psDec->prev_decode_only_middle == 1 ) {
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
# @OPUS@\upstream\silk\dec_API.c:314:     if( decControl->nChannelsInternal == 2 && decode_only_middle == 0 && psDec->prev_decode_only_middle == 1 ) {
	beqi	a3, 2, .L67	# prephitmp_630,,
	j	.L234		#
.L112:
# @OPUS@\upstream\silk\dec_API.c:304:                 decode_only_middle = 0;
	movi.n	a2, 0	# tmp561,
# @OPUS@\upstream\silk\dec_API.c:314:     if( decControl->nChannelsInternal == 2 && decode_only_middle == 0 && psDec->prev_decode_only_middle == 1 ) {
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
# @OPUS@\upstream\silk\dec_API.c:304:                 decode_only_middle = 0;
	s32i	a2, sp, 684	# decode_only_middle, tmp561
# @OPUS@\upstream\silk\dec_API.c:314:     if( decControl->nChannelsInternal == 2 && decode_only_middle == 0 && psDec->prev_decode_only_middle == 1 ) {
	beqi	a3, 2, .L71	# prephitmp_630,,
	j	.L234		#
.L67:
# @OPUS@\upstream\silk\dec_API.c:314:     if( decControl->nChannelsInternal == 2 && decode_only_middle == 0 && psDec->prev_decode_only_middle == 1 ) {
	l32i	a2, sp, 684	# decode_only_middle, decode_only_middle
	beqz.n	a2, .L71	# decode_only_middle,
	j	.L235		#
.L71:
# @OPUS@\upstream\silk\dec_API.c:314:     if( decControl->nChannelsInternal == 2 && decode_only_middle == 0 && psDec->prev_decode_only_middle == 1 ) {
	l32i	a8, sp, 720	# %sfp,
	l32i	a12, a8, 116	# MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle, MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle
	beqi	a12, 1, .L72	# MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle,,
.L235:
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
.L234:
	l32i.n	a4, a13, 8	# decControl_322(D)->API_sampleRate, _55
	l32i.n	a15, a13, 0	# decControl_322(D)->nChannelsAPI, prephitmp_638
	j	.L70		#
.L72:
# @OPUS@\upstream\silk\dec_API.c:315:         silk_memset( psDec->channel_state[ 1 ].outBuf, 0, sizeof(psDec->channel_state[ 1 ].outBuf) );
	l32i	a8, sp, 704	# %sfp,
	l32r	a2, .LC15	#, tmp566
	movi	a4, 0x3c0	#,
	movi.n	a3, 0	#,
	add.n	a2, a8, a2	#,, tmp566
	call0	memset		#
# @OPUS@\upstream\silk\dec_API.c:316:         silk_memset( psDec->channel_state[ 1 ].sLPC_Q14_buf, 0, sizeof(psDec->channel_state[ 1 ].sLPC_Q14_buf) );
	l32i	a8, sp, 704	# %sfp,
	l32r	a2, .LC16	#, tmp572
	movi.n	a4, 0x40	#,
	movi.n	a3, 0	#,
	add.n	a2, a8, a2	#,, tmp572
	call0	memset		#
# @OPUS@\upstream\silk\dec_API.c:317:         psDec->channel_state[ 1 ].lagPrev        = 100;
	l32i	a8, sp, 704	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:318:         psDec->channel_state[ 1 ].LastGainIndex  = 10;
	movi.n	a3, 0xa	# tmp580,
# @OPUS@\upstream\silk\dec_API.c:317:         psDec->channel_state[ 1 ].lagPrev        = 100;
	addmi	a2, a8, 0xf00	# tmp577,,
# @OPUS@\upstream\silk\dec_API.c:318:         psDec->channel_state[ 1 ].LastGainIndex  = 10;
	s8i	a3, a2, 188	# MEM[(struct silk_decoder *)decState_318(D)].channel_state[1].LastGainIndex, tmp580
# @OPUS@\upstream\silk\dec_API.c:317:         psDec->channel_state[ 1 ].lagPrev        = 100;
	movi	a3, 0x64	# tmp578,
	s32i	a3, a2, 184	# MEM[(struct silk_decoder *)decState_318(D)].channel_state[1].lagPrev, tmp578
# @OPUS@\upstream\silk\dec_API.c:319:         psDec->channel_state[ 1 ].prevSignalType = TYPE_NO_VOICE_ACTIVITY;
	movi.n	a4, 0	# tmp582,
	addmi	a3, a8, 0x1600	# tmp581,,
	s32i	a4, a3, 248	# MEM[(struct silk_decoder *)decState_318(D)].channel_state[1].prevSignalType, tmp582
	l32i.n	a15, a13, 0	# decControl_322(D)->nChannelsAPI, prephitmp_638
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, prephitmp_630
	l32i.n	a4, a13, 8	# decControl_322(D)->API_sampleRate, _55
# @OPUS@\upstream\silk\dec_API.c:320:         psDec->channel_state[ 1 ].first_frame_after_reset = 1;
	s32i	a12, a2, 252	# MEM[(struct silk_decoder *)decState_318(D)].channel_state[1].first_frame_after_reset, MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle
.L70:
# @OPUS@\upstream\silk\dec_API.c:326:     delay_stack_alloc = decControl->internalSampleRate*decControl->nChannelsInternal
	l32i.n	a2, a13, 12	# decControl_322(D)->internalSampleRate, decControl_322(D)->internalSampleRate
# @OPUS@\upstream\silk\dec_API.c:327:           < decControl->API_sampleRate*decControl->nChannelsAPI;
	mull	a4, a4, a15	#, _55, prephitmp_638
# @OPUS@\upstream\silk\dec_API.c:326:     delay_stack_alloc = decControl->internalSampleRate*decControl->nChannelsInternal
	mull	a2, a3, a2	#, prephitmp_630, decControl_322(D)->internalSampleRate
# @OPUS@\upstream\silk\dec_API.c:327:           < decControl->API_sampleRate*decControl->nChannelsAPI;
	s32i	a4, sp, 716	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:326:     delay_stack_alloc = decControl->internalSampleRate*decControl->nChannelsInternal
	s32i	a2, sp, 700	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:328:     ALLOC( samplesOut1_tmp_storage1, delay_stack_alloc ? ALLOC_NONE
	blt	a2, a4, .L73	#,,
# @OPUS@\upstream\silk\dec_API.c:328:     ALLOC( samplesOut1_tmp_storage1, delay_stack_alloc ? ALLOC_NONE
	l32i	a8, sp, 708	# %sfp,
	movi.n	a4, 0	#,
	l32i.n	a2, a8, 28	# MEM[(struct silk_decoder_state *)decState_318(D)].frame_length, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length
	addi.n	a2, a2, 2	# tmp587, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length,
	mull	a2, a2, a3	#, tmp587, prephitmp_630
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\dec_API.c:337:        samplesOut1_tmp[ 1 ] = samplesOut1_tmp_storage1 + channel_state[ 0 ].frame_length + 2;
	l32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:336:        samplesOut1_tmp[ 0 ] = samplesOut1_tmp_storage1;
	s32i	a2, sp, 672	# samplesOut1_tmp, samplesOut1_tmp_storage1
# @OPUS@\upstream\silk\dec_API.c:337:        samplesOut1_tmp[ 1 ] = samplesOut1_tmp_storage1 + channel_state[ 0 ].frame_length + 2;
	l32i.n	a3, a8, 28	# MEM[(struct silk_decoder_state *)decState_318(D)].frame_length, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length
	addi.n	a3, a3, 2	# tmp593, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length,
	slli	a3, a3, 1	# tmp595, tmp593,
	add.n	a3, a2, a3	# tmp596, samplesOut1_tmp_storage1, tmp595
# @OPUS@\upstream\silk\dec_API.c:337:        samplesOut1_tmp[ 1 ] = samplesOut1_tmp_storage1 + channel_state[ 0 ].frame_length + 2;
	s32i	a3, sp, 676	# samplesOut1_tmp, tmp596
.L110:
# @OPUS@\upstream\silk\dec_API.c:340:     if( lostFlag == FLAG_DECODE_NORMAL ) {
	l32i	a8, sp, 712	# %sfp,
	l32i.n	a2, a13, 4	# decControl_322(D)->nChannelsInternal, _159
	l32i.n	a3, a13, 24	# decControl_322(D)->enable_deep_plc, pretmp_825
	bnez.n	a8, .L74	#,
# @OPUS@\upstream\silk\dec_API.c:341:         has_side = !decode_only_middle;
	l32i	a12, sp, 684	# decode_only_middle, decode_only_middle
	movi.n	a4, 1	# tmp600,
	moveqz	a8, a4, a12	#, tmp600, decode_only_middle
	extui	a12, a8, 0, 8	# prephitmp_719, tmp599
	j	.L75		#
.L74:
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	l32i	a8, sp, 720	# %sfp,
	l32i	a4, a8, 116	# MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle, MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle
	beqz.n	a4, .L122	# MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle,
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	l32i	a8, sp, 712	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	movi.n	a5, 0	# tmp608,
	movi.n	a6, 1	# tmp607,
	addi	a12, a2, -2	# tmp606, _159,
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	addi	a4, a8, -2	# tmp611,,
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	mov.n	a7, a5	#, tmp608
	moveqz	a7, a6, a12	#, tmp607, tmp606
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	movnez	a6, a5, a4	# tmp607, tmp608, tmp611
	and	a12, a7, a6	# prephitmp_719, tmp605, tmp610
	beq	a12, a5, .L75	# prephitmp_719,,
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	l32i	a8, sp, 704	# %sfp,
	addmi	a2, a8, 0x1000	# tmp620,,
	l32i.n	a4, a2, 8	# MEM[(struct silk_decoder_state *)decState_318(D) + 2992B].nFramesDecoded, MEM[(struct silk_decoder_state *)decState_318(D) + 2992B].nFramesDecoded
	movi	a2, 0x11c	# tmp617,
	add.n	a2, a2, a4	# tmp618, tmp617, MEM[(struct silk_decoder_state *)decState_318(D) + 2992B].nFramesDecoded
	l32i	a8, sp, 696	# %sfp,
	slli	a2, a2, 2	# tmp621, tmp618,
	add.n	a2, a8, a2	# tmp622,, tmp621
# @OPUS@\upstream\silk\dec_API.c:344:               || (decControl->nChannelsInternal == 2 && lostFlag == FLAG_DECODE_LBRR && channel_state[1].LBRR_flags[ channel_state[1].nFramesDecoded ] == 1 );
	l32i	a2, a2, 184	# MEM[(struct silk_decoder_state *)decState_318(D) + 2992B].LBRR_flags, tmp625
	bnei	a2, 1, .L226	# tmp625,,
	j	.L76		#
.L122:
	movi.n	a12, 1	# prephitmp_719,
.L75:
# @OPUS@\upstream\silk\dec_API.c:346:     channel_state[ 0 ].sPLC.enable_deep_plc = decControl->enable_deep_plc;
	l32i	a8, sp, 696	# %sfp,
	s32i	a3, a8, 172	# MEM[(struct silk_decoder_state *)decState_318(D)].sPLC.enable_deep_plc, pretmp_825
# @OPUS@\upstream\silk\dec_API.c:348:     for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blti	a2, 1, .L78	# _159,,
.L113:
	l32r	a8, .LC7	#,
	movi	a10, 0x458	# tmp627,
	s32i	a8, sp, 692	# %sfp,
	l32i	a8, sp, 704	# %sfp,
	movi	a2, 0x290	# tmp628,
	add.n	a15, a8, a10	# ivtmp$80,, tmp627
	addi	a8, sp, 16	#,,
	add.n	a8, a8, a2	#,, tmp628
# @OPUS@\upstream\silk\dec_API.c:346:     channel_state[ 0 ].sPLC.enable_deep_plc = decControl->enable_deep_plc;
	movi.n	a14, 0	# n,
	s32i	a8, sp, 732	# %sfp,
.L84:
	l32i	a8, sp, 732	# %sfp,
	slli	a2, a14, 2	# tmp630, n,
	add.n	a2, a8, a2	# tmp631,, tmp630
	l32i.n	a4, a2, 0	# MEM[base: _588, offset: 0B], MEM[base: _588, offset: 0B]
	movi	a2, -0x458	#,
	add.n	a10, a15, a2	# _584, ivtmp$80,
	addi.n	a4, a4, 4	# _730, MEM[base: _588, offset: 0B],
# @OPUS@\upstream\silk\dec_API.c:349:         if( n == 0 || has_side ) {
	bbci	a14, 0, .L128	# n,,
# @OPUS@\upstream\silk\dec_API.c:380:             silk_memset( &samplesOut1_tmp[ n ][ 2 ], 0, nSamplesOutDec * sizeof( opus_int16 ) );
	mov.n	a3, a12	#, prephitmp_719
	mov.n	a2, a4	#, _730
# @OPUS@\upstream\silk\dec_API.c:349:         if( n == 0 || has_side ) {
	beqz.n	a12, .L79	# prephitmp_719,
.L128:
# @OPUS@\upstream\silk\dec_API.c:353:             FrameIndex = channel_state[ 0 ].nFramesDecoded - n;
	l32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:356:                 condCoding = CODE_INDEPENDENTLY;
	movi.n	a7, 0	# condCoding,
# @OPUS@\upstream\silk\dec_API.c:353:             FrameIndex = channel_state[ 0 ].nFramesDecoded - n;
	l32i	a2, a8, 88	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded
	sub	a2, a2, a14	# FrameIndex, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded, n
# @OPUS@\upstream\silk\dec_API.c:355:             if( FrameIndex <= 0 ) {
	blti	a2, 1, .L81	# FrameIndex,,
# @OPUS@\upstream\silk\dec_API.c:357:             } else if( lostFlag == FLAG_DECODE_LBRR ) {
	l32i	a8, sp, 712	# %sfp,
	bnei	a8, 2, .L82	#,,
# @OPUS@\upstream\silk\dec_API.c:358:                 condCoding = channel_state[ n ].LBRR_flags[ FrameIndex - 1 ] ? CODE_CONDITIONALLY : CODE_INDEPENDENTLY;
	movi	a3, 0x11b	# tmp642,
	add.n	a2, a2, a3	# tmp643, FrameIndex, tmp642
	slli	a2, a2, 2	# tmp644, tmp643,
	add.n	a2, a10, a2	# tmp645, _584, tmp644
	l32i.n	a7, a2, 8	# MEM[(struct silk_decoder_state *)_584].LBRR_flags, condCoding
# @OPUS@\upstream\silk\dec_API.c:358:                 condCoding = channel_state[ n ].LBRR_flags[ FrameIndex - 1 ] ? CODE_CONDITIONALLY : CODE_INDEPENDENTLY;
	movnez	a7, a8, a7	# condCoding,, condCoding
	j	.L81		#
.L82:
	movi.n	a7, 2	# condCoding,
# @OPUS@\upstream\silk\dec_API.c:359:             } else if( n > 0 && psDec->prev_decode_only_middle ) {
	bnei	a14, 1, .L81	# n,,
# @OPUS@\upstream\silk\dec_API.c:359:             } else if( n > 0 && psDec->prev_decode_only_middle ) {
	l32i	a8, sp, 720	# %sfp,
	l32i	a2, a8, 116	# MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle, MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle
# @OPUS@\upstream\silk\dec_API.c:362:                 condCoding = CODE_INDEPENDENTLY_NO_LTP_SCALING;
	movnez	a7, a14, a2	# condCoding, n, MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle
.L81:
# @OPUS@\upstream\silk\dec_API.c:371:             ret += silk_decode_frame( &channel_state[ n ], psRangeDec, &samplesOut1_tmp[ n ][ 2 ], &nSamplesOutDec, lostFlag, condCoding,
	l32i	a8, sp, 788	# arch,
	addi	a2, sp, 16	#,,
	l32i	a6, sp, 712	# %sfp,
	movi	a5, 0x298	# tmp649,
	l32i	a3, sp, 728	# %sfp,
	s32i.n	a8, sp, 0	#,
	add.n	a5, a2, a5	#,, tmp649
	mov.n	a2, a10	#, _584
	call0	silk_decode_frame		#
# @OPUS@\upstream\silk\dec_API.c:371:             ret += silk_decode_frame( &channel_state[ n ], psRangeDec, &samplesOut1_tmp[ n ][ 2 ], &nSamplesOutDec, lostFlag, condCoding,
	l32i	a8, sp, 688	# %sfp,
	add.n	a8, a8, a2	#,,
	s32i	a8, sp, 688	# %sfp,
	j	.L83		#
.L79:
# @OPUS@\upstream\silk\dec_API.c:380:             silk_memset( &samplesOut1_tmp[ n ][ 2 ], 0, nSamplesOutDec * sizeof( opus_int16 ) );
	l32i	a4, sp, 680	# nSamplesOutDec, nSamplesOutDec
	slli	a4, a4, 1	#, nSamplesOutDec,
	call0	memset		#
.L83:
# @OPUS@\upstream\silk\dec_API.c:382:         channel_state[ n ].nFramesDecoded++;
	l32i.n	a2, a15, 0	# MEM[base: _587, offset: 0B], MEM[base: _587, offset: 0B]
	l32i	a8, sp, 692	# %sfp,
	addi.n	a2, a2, 1	# tmp656, MEM[base: _587, offset: 0B],
	s32i.n	a2, a15, 0	# MEM[base: _587, offset: 0B], tmp656
# @OPUS@\upstream\silk\dec_API.c:348:     for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	l32i.n	a2, a13, 4	# decControl_322(D)->nChannelsInternal, _159
# @OPUS@\upstream\silk\dec_API.c:348:     for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	addi.n	a14, a14, 1	# n, n,
	add.n	a15, a15, a8	# ivtmp$80, ivtmp$80,
# @OPUS@\upstream\silk\dec_API.c:348:     for( n = 0; n < decControl->nChannelsInternal; n++ ) {
	blt	a14, a2, .L84	# n, _159,
.L78:
# @OPUS@\upstream\silk\dec_API.c:385:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 ) {
	l32i.n	a5, a13, 0	# decControl_322(D)->nChannelsAPI, decControl_322(D)->nChannelsAPI
	addi	a3, sp, 16	#,,
	addmi	a4, a3, 0x200	# tmp659,,
	l32i	a3, sp, 672	# samplesOut1_tmp, pretmp_673
# @OPUS@\upstream\silk\dec_API.c:385:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 ) {
	bnei	a5, 2, .L85	# decControl_322(D)->nChannelsAPI,,
	bnei	a2, 2, .L85	# _159,,
# @OPUS@\upstream\silk\dec_API.c:387:         silk_stereo_MS_to_LR( &psDec->sStereo, samplesOut1_tmp[ 0 ], samplesOut1_tmp[ 1 ], MS_pred_Q13, channel_state[ 0 ].fs_kHz, nSamplesOutDec );
	l32i	a8, sp, 708	# %sfp,
	addi	a2, sp, 16	#,,
	movi	a5, 0x288	# tmp674,
	l32i.n	a6, a8, 16	# MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz,
	add.n	a5, a2, a5	#,, tmp674
	l32i	a8, sp, 704	# %sfp,
	l32r	a2, .LC8	#, tmp678
	l32i	a7, sp, 680	# nSamplesOutDec,
	l32i	a4, a4, 148	# samplesOut1_tmp,
	add.n	a2, a8, a2	#,, tmp678
	call0	silk_stereo_MS_to_LR		#
	l32i	a2, sp, 680	# nSamplesOutDec, nSamplesOutDec$43_168
	j	.L86		#
.L85:
# @OPUS@\upstream\silk\dec_API.c:390:         silk_memcpy( samplesOut1_tmp[ 0 ], psDec->sStereo.sMid, 2 * sizeof( opus_int16 ) );
	l32r	a4, .LC17	#, tmp679
	l32i	a8, sp, 704	# %sfp,
	add.n	a4, a8, a4	# _167,, tmp679
	l8ui	a5, a4, 0	# MEM[(void *)_167],
	l8ui	a2, a4, 1	# MEM[(void *)_167],
	s8i	a5, a3, 0	# MEM[(void *)pretmp_673], MEM[(void *)_167]
	l8ui	a5, a4, 2	# MEM[(void *)_167],
	s8i	a2, a3, 1	# MEM[(void *)pretmp_673], MEM[(void *)_167]
	l8ui	a2, a4, 3	# MEM[(void *)_167],
	s8i	a5, a3, 2	# MEM[(void *)pretmp_673], MEM[(void *)_167]
	s8i	a2, a3, 3	# MEM[(void *)pretmp_673], MEM[(void *)_167]
# @OPUS@\upstream\silk\dec_API.c:391:         silk_memcpy( psDec->sStereo.sMid, &samplesOut1_tmp[ 0 ][ nSamplesOutDec ], 2 * sizeof( opus_int16 ) );
	l32i	a2, sp, 680	# nSamplesOutDec, nSamplesOutDec$43_168
	slli	a5, a2, 1	# tmp684, nSamplesOutDec$43_168,
	add.n	a3, a3, a5	# tmp685, pretmp_673, tmp684
	l8ui	a5, a3, 0	# MEM[(void *)_171],
	l8ui	a6, a3, 1	# MEM[(void *)_171],
	s8i	a5, a4, 0	# MEM[(void *)_167], MEM[(void *)_171]
	l8ui	a5, a3, 2	# MEM[(void *)_171],
	s8i	a6, a4, 1	# MEM[(void *)_167], MEM[(void *)_171]
	l8ui	a3, a3, 3	# MEM[(void *)_171],
	s8i	a5, a4, 2	# MEM[(void *)_167], MEM[(void *)_171]
	s8i	a3, a4, 3	# MEM[(void *)_167], MEM[(void *)_171]
.L86:
# @OPUS@\upstream\silk\dec_API.c:395:     *nSamplesOut = silk_DIV32( nSamplesOutDec * decControl->API_sampleRate, silk_SMULBB( channel_state[ 0 ].fs_kHz, 1000 ) );
	l32i	a8, sp, 708	# %sfp,
	l32i.n	a5, a13, 8	# decControl_322(D)->API_sampleRate, decControl_322(D)->API_sampleRate
	l16si	a4, a8, 16	# MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz, tmp694
	mull	a2, a2, a5	#, nSamplesOutDec$43_168, decControl_322(D)->API_sampleRate
	slli	a3, a4, 5	# tmp697, tmp694,
	sub	a3, a3, a4	# tmp698, tmp697, tmp694
	slli	a3, a3, 2	# tmp699, tmp698,
	add.n	a3, a3, a4	# tmp700, tmp699, tmp694
	slli	a3, a3, 3	#, tmp700,
	call0	__divsi3		#
# @OPUS@\upstream\silk\dec_API.c:395:     *nSamplesOut = silk_DIV32( nSamplesOutDec * decControl->API_sampleRate, silk_SMULBB( channel_state[ 0 ].fs_kHz, 1000 ) );
	l32i	a8, sp, 784	# nSamplesOut,
# @OPUS@\upstream\silk\dec_API.c:398:     ALLOC( samplesOut2_tmp,
	movi.n	a14, 0	# tmp862,
# @OPUS@\upstream\silk\dec_API.c:395:     *nSamplesOut = silk_DIV32( nSamplesOutDec * decControl->API_sampleRate, silk_SMULBB( channel_state[ 0 ].fs_kHz, 1000 ) );
	s32i.n	a2, a8, 0	# *nSamplesOut_405(D), _17
# @OPUS@\upstream\silk\dec_API.c:398:     ALLOC( samplesOut2_tmp,
	l32i.n	a3, a13, 0	# decControl_322(D)->nChannelsAPI, decControl_322(D)->nChannelsAPI
	mov.n	a4, a14	#, tmp862
	addi	a3, a3, -2	# tmp863, decControl_322(D)->nChannelsAPI,
	movnez	a2, a14, a3	# _17, tmp862, tmp863
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\dec_API.c:400:     if( decControl->nChannelsAPI == 2 ) {
	l32i.n	a12, a13, 0	# decControl_322(D)->nChannelsAPI, decControl_322(D)->nChannelsAPI
# @OPUS@\upstream\silk\dec_API.c:403:         resample_out_ptr = samplesOut;
	l32i	a8, sp, 724	# %sfp,
	addi	a12, a12, -2	# tmp879, decControl_322(D)->nChannelsAPI,
	moveqz	a8, a2, a12	#,, tmp879
	mov.n	a12, a8	# samplesOut2_tmp,
# @OPUS@\upstream\silk\dec_API.c:406:     ALLOC( samplesOut1_tmp_storage2, delay_stack_alloc
	l32i	a2, sp, 716	# %sfp,
	l32i	a8, sp, 700	# %sfp,
	bge	a8, a2, .L89	#,,
# @OPUS@\upstream\silk\dec_API.c:406:     ALLOC( samplesOut1_tmp_storage2, delay_stack_alloc
	l32i	a8, sp, 708	# %sfp,
	l32i.n	a3, a13, 4	# decControl_322(D)->nChannelsInternal, decControl_322(D)->nChannelsInternal
	l32i.n	a2, a8, 28	# MEM[(struct silk_decoder_state *)decState_318(D)].frame_length, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length
	mov.n	a4, a14	#, tmp862
	addi.n	a2, a2, 2	# tmp708, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length,
	mull	a2, a2, a3	#, tmp708, decControl_322(D)->nChannelsInternal
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\dec_API.c:411:        OPUS_COPY(samplesOut1_tmp_storage2, samplesOut, decControl->nChannelsInternal*(channel_state[ 0 ].frame_length + 2));
	l32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:406:     ALLOC( samplesOut1_tmp_storage2, delay_stack_alloc
	mov.n	a14, a2	# samplesOut1_tmp_storage2,
# @OPUS@\upstream\silk\dec_API.c:411:        OPUS_COPY(samplesOut1_tmp_storage2, samplesOut, decControl->nChannelsInternal*(channel_state[ 0 ].frame_length + 2));
	l32i.n	a2, a8, 28	# MEM[(struct silk_decoder_state *)decState_318(D)].frame_length, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length
	l32i.n	a4, a13, 4	# decControl_322(D)->nChannelsInternal, decControl_322(D)->nChannelsInternal
	addi.n	a2, a2, 2	# tmp713, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length,
	mull	a4, a2, a4	#, tmp713, decControl_322(D)->nChannelsInternal
	l32i	a3, sp, 724	# %sfp,
	mov.n	a2, a14	#, samplesOut1_tmp_storage2
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\silk\dec_API.c:413:        samplesOut1_tmp[ 1 ] = samplesOut1_tmp_storage2 + channel_state[ 0 ].frame_length + 2;
	l32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:412:        samplesOut1_tmp[ 0 ] = samplesOut1_tmp_storage2;
	s32i	a14, sp, 672	# samplesOut1_tmp, samplesOut1_tmp_storage2
# @OPUS@\upstream\silk\dec_API.c:413:        samplesOut1_tmp[ 1 ] = samplesOut1_tmp_storage2 + channel_state[ 0 ].frame_length + 2;
	l32i.n	a2, a8, 28	# MEM[(struct silk_decoder_state *)decState_318(D)].frame_length, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length
	addi.n	a2, a2, 2	# tmp720, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length,
	slli	a2, a2, 1	# tmp722, tmp720,
	add.n	a2, a14, a2	# tmp723, samplesOut1_tmp_storage2, tmp722
# @OPUS@\upstream\silk\dec_API.c:413:        samplesOut1_tmp[ 1 ] = samplesOut1_tmp_storage2 + channel_state[ 0 ].frame_length + 2;
	s32i	a2, sp, 676	# samplesOut1_tmp, tmp723
	j	.L90		#
.L108:
	l32r	a8, .LC7	#,
# @OPUS@\upstream\silk\dec_API.c:419:         ret += silk_resampler( &channel_state[ n ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ n ][ 1 ], nSamplesOutDec );
	movi	a2, 0x290	# tmp725,
	s32i	a8, sp, 692	# %sfp,
	addi	a6, sp, 16	#,,
	l32i	a8, sp, 704	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:415:     for( n = 0; n < silk_min( decControl->nChannelsAPI, decControl->nChannelsInternal ); n++ ) {
	movi.n	a14, 0	# n,
# @OPUS@\upstream\silk\dec_API.c:419:         ret += silk_resampler( &channel_state[ n ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ n ][ 1 ], nSamplesOutDec );
	add.n	a6, a6, a2	#,, tmp725
	movi	a15, 0x484	# tmp724,
	mov.n	a2, a13	# decControl, decControl
	add.n	a15, a8, a15	# ivtmp$73,, tmp724
	mov.n	a13, a14	# n, n
	s32i	a6, sp, 700	# %sfp,
	mov.n	a14, a2	# decControl, decControl
.L92:
	l32i	a7, sp, 700	# %sfp,
	slli	a2, a13, 2	# tmp727, n,
	add.n	a2, a7, a2	# tmp728,, tmp727
# @OPUS@\upstream\silk\dec_API.c:419:         ret += silk_resampler( &channel_state[ n ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ n ][ 1 ], nSamplesOutDec );
	l32i.n	a4, a2, 0	# MEM[base: _600, offset: 0B], MEM[base: _600, offset: 0B]
# @OPUS@\upstream\silk\dec_API.c:419:         ret += silk_resampler( &channel_state[ n ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ n ][ 1 ], nSamplesOutDec );
	l32i	a5, sp, 680	# nSamplesOutDec,
	mov.n	a3, a12	#, samplesOut2_tmp
	addi.n	a4, a4, 2	#, MEM[base: _600, offset: 0B],
	mov.n	a2, a15	#, ivtmp$73
	call0	silk_resampler		#
# @OPUS@\upstream\silk\dec_API.c:419:         ret += silk_resampler( &channel_state[ n ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ n ][ 1 ], nSamplesOutDec );
	l32i	a8, sp, 688	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:423:         if( decControl->nChannelsAPI == 2 ) {
	l32i.n	a3, a14, 0	# decControl_322(D)->nChannelsAPI, _203
# @OPUS@\upstream\silk\dec_API.c:419:         ret += silk_resampler( &channel_state[ n ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ n ][ 1 ], nSamplesOutDec );
	add.n	a8, a8, a2	#,,
	s32i	a8, sp, 688	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:423:         if( decControl->nChannelsAPI == 2 ) {
	beqi	a3, 2, .L91	# _203,,
.L95:
	l32i	a8, sp, 692	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:415:     for( n = 0; n < silk_min( decControl->nChannelsAPI, decControl->nChannelsInternal ); n++ ) {
	l32i.n	a2, a14, 4	# decControl_322(D)->nChannelsInternal, _214
# @OPUS@\upstream\silk\dec_API.c:415:     for( n = 0; n < silk_min( decControl->nChannelsAPI, decControl->nChannelsInternal ); n++ ) {
	addi.n	a13, a13, 1	# n, n,
	add.n	a15, a15, a8	# ivtmp$73, ivtmp$73,
# @OPUS@\upstream\silk\dec_API.c:415:     for( n = 0; n < silk_min( decControl->nChannelsAPI, decControl->nChannelsInternal ); n++ ) {
	mov.n	a4, a3	# _203, _203
	bge	a2, a3, .L93	# _214, _203,
	mov.n	a4, a2	# _203, _214
.L93:
# @OPUS@\upstream\silk\dec_API.c:415:     for( n = 0; n < silk_min( decControl->nChannelsAPI, decControl->nChannelsInternal ); n++ ) {
	blt	a13, a4, .L92	# n, _203,
	mov.n	a13, a14	# decControl, decControl
	j	.L94		#
.L91:
# @OPUS@\upstream\silk\dec_API.c:424:             for( i = 0; i < *nSamplesOut; i++ ) {
	l32i	a8, sp, 784	# nSamplesOut,
	l32i.n	a2, a8, 0	# *nSamplesOut_405(D), _461
# @OPUS@\upstream\silk\dec_API.c:424:             for( i = 0; i < *nSamplesOut; i++ ) {
	blti	a2, 1, .L95	# _461,,
	slli	a5, a2, 1	# tmp734, _461,
	l32i	a8, sp, 724	# %sfp,
	add.n	a5, a5, a13	# tmp735, tmp734, n
	slli	a2, a13, 1	# tmp733, n,
	slli	a5, a5, 1	# tmp736, tmp735,
	mov.n	a4, a12	# ivtmp$68, samplesOut2_tmp
	add.n	a2, a2, a8	# ivtmp$69, tmp733,
	add.n	a5, a5, a8	# _607, tmp736,
.L96:
# @OPUS@\upstream\silk\dec_API.c:425:                 samplesOut[ n + 2 * i ] = resample_out_ptr[ i ];
	l16si	a6, a4, 0	# MEM[base: _615, offset: 0B], _212
	addi.n	a4, a4, 2	# ivtmp$68, ivtmp$68,
# @OPUS@\upstream\silk\dec_API.c:425:                 samplesOut[ n + 2 * i ] = resample_out_ptr[ i ];
	s16i	a6, a2, 0	# MEM[base: _614, offset: 0B], _212
	addi.n	a2, a2, 4	# ivtmp$69, ivtmp$69,
# @OPUS@\upstream\silk\dec_API.c:424:             for( i = 0; i < *nSamplesOut; i++ ) {
	bne	a5, a2, .L96	# _607, ivtmp$69,
	j	.L95		#
.L94:
# @OPUS@\upstream\silk\dec_API.c:431:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 1 ) {
	bnei	a2, 1, .L97	# _214,,
	bnei	a3, 2, .L97	# _203,,
# @OPUS@\upstream\silk\dec_API.c:432:         if ( stereo_to_mono ){
	l32i	a8, sp, 736	# %sfp,
	bnez.n	a8, .L98	#,
# @OPUS@\upstream\silk\dec_API.c:443:             for( i = 0; i < *nSamplesOut; i++ ) {
	l32i	a8, sp, 784	# nSamplesOut,
	l32i	a2, sp, 724	# %sfp, ivtmp$63
	l32i.n	a3, a8, 0	# *nSamplesOut_405(D), _480
	slli	a4, a3, 2	# tmp762, _480,
	add.n	a4, a2, a4	# _626, ivtmp$63, tmp762
# @OPUS@\upstream\silk\dec_API.c:443:             for( i = 0; i < *nSamplesOut; i++ ) {
	bgei	a3, 1, .L101	# _480,,
	j	.L97		#
.L98:
# @OPUS@\upstream\silk\dec_API.c:436:             ret += silk_resampler( &channel_state[ 1 ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ 0 ][ 1 ], nSamplesOutDec );
	l32i	a8, sp, 704	# %sfp,
	l32r	a2, .LC7	#, tmp755
# @OPUS@\upstream\silk\dec_API.c:436:             ret += silk_resampler( &channel_state[ 1 ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ 0 ][ 1 ], nSamplesOutDec );
	l32i	a4, sp, 672	# samplesOut1_tmp, samplesOut1_tmp
# @OPUS@\upstream\silk\dec_API.c:436:             ret += silk_resampler( &channel_state[ 1 ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ 0 ][ 1 ], nSamplesOutDec );
	add.n	a2, a8, a2	# tmp754,, tmp755
	movi	a6, 0x484	# tmp756,
	l32i	a5, sp, 680	# nSamplesOutDec,
	mov.n	a3, a12	#, samplesOut2_tmp
	addi.n	a4, a4, 2	#, samplesOut1_tmp,
	add.n	a2, a2, a6	#, tmp754, tmp756
	call0	silk_resampler		#
# @OPUS@\upstream\silk\dec_API.c:439:             for( i = 0; i < *nSamplesOut; i++ ) {
	l32i	a8, sp, 784	# nSamplesOut,
	l32i.n	a3, a8, 0	# *nSamplesOut_405(D), _275
# @OPUS@\upstream\silk\dec_API.c:436:             ret += silk_resampler( &channel_state[ 1 ].resampler_state, resample_out_ptr, &samplesOut1_tmp[ 0 ][ 1 ], nSamplesOutDec );
	l32i	a8, sp, 688	# %sfp,
	add.n	a8, a8, a2	#,,
	s32i	a8, sp, 688	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:439:             for( i = 0; i < *nSamplesOut; i++ ) {
	blti	a3, 1, .L97	# _275,,
	l32i	a8, sp, 724	# %sfp,
	slli	a4, a3, 2	# tmp758, _275,
	add.n	a4, a8, a4	# tmp759,, tmp758
	addi.n	a2, a8, 2	# ivtmp$57,,
	addi.n	a4, a4, 2	# _643, tmp759,
.L100:
# @OPUS@\upstream\silk\dec_API.c:440:                 samplesOut[ 1 + 2 * i ] = resample_out_ptr[ i ];
	l16si	a3, a12, 0	# MEM[base: _672, offset: 0B], _228
	addi.n	a12, a12, 2	# ivtmp$56, ivtmp$56,
# @OPUS@\upstream\silk\dec_API.c:440:                 samplesOut[ 1 + 2 * i ] = resample_out_ptr[ i ];
	s16i	a3, a2, 0	# MEM[base: _671, offset: 0B], _228
	addi.n	a2, a2, 4	# ivtmp$57, ivtmp$57,
# @OPUS@\upstream\silk\dec_API.c:439:             for( i = 0; i < *nSamplesOut; i++ ) {
	bne	a4, a2, .L100	# _643, ivtmp$57,
	j	.L97		#
.L101:
# @OPUS@\upstream\silk\dec_API.c:444:                 samplesOut[ 1 + 2 * i ] = samplesOut[ 0 + 2 * i ];
	l16ui	a3, a2, 0	# MEM[base: _635, offset: 0B],
	s16i	a3, a2, 2	# MEM[base: _635, offset: 2B], MEM[base: _635, offset: 0B]
	addi.n	a2, a2, 4	# ivtmp$63, ivtmp$63,
# @OPUS@\upstream\silk\dec_API.c:443:             for( i = 0; i < *nSamplesOut; i++ ) {
	bne	a4, a2, .L101	# _626, ivtmp$63,
.L97:
# @OPUS@\upstream\silk\dec_API.c:450:     if( channel_state[ 0 ].prevSignalType == TYPE_VOICED ) {
	l32i	a8, sp, 696	# %sfp,
	l32i	a2, a8, 72	# MEM[(struct silk_decoder_state *)decState_318(D)].prevSignalType, MEM[(struct silk_decoder_state *)decState_318(D)].prevSignalType
	bnei	a2, 2, .L102	# MEM[(struct silk_decoder_state *)decState_318(D)].prevSignalType,,
# @OPUS@\upstream\silk\dec_API.c:452:         decControl->prevPitchLag = channel_state[ 0 ].lagPrev * mult_tab[ ( channel_state[ 0 ].fs_kHz - 8 ) >> 2 ];
	l32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:451:         int mult_tab[ 3 ] = { 6, 4, 3 };
	l32r	a3, .LC18	#, tmp766
# @OPUS@\upstream\silk\dec_API.c:452:         decControl->prevPitchLag = channel_state[ 0 ].lagPrev * mult_tab[ ( channel_state[ 0 ].fs_kHz - 8 ) >> 2 ];
	l32i.n	a2, a8, 16	# MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz, MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz
# @OPUS@\upstream\silk\dec_API.c:451:         int mult_tab[ 3 ] = { 6, 4, 3 };
	l32i.n	a5, a3, 0	#, tmp767
	l32i.n	a4, a3, 4	#, tmp768
# @OPUS@\upstream\silk\dec_API.c:452:         decControl->prevPitchLag = channel_state[ 0 ].lagPrev * mult_tab[ ( channel_state[ 0 ].fs_kHz - 8 ) >> 2 ];
	addi	a2, a2, -8	# tmp771, MEM[(struct silk_decoder_state *)decState_318(D)].fs_kHz,
# @OPUS@\upstream\silk\dec_API.c:451:         int mult_tab[ 3 ] = { 6, 4, 3 };
	l32i.n	a3, a3, 8	#, tmp769
# @OPUS@\upstream\silk\dec_API.c:452:         decControl->prevPitchLag = channel_state[ 0 ].lagPrev * mult_tab[ ( channel_state[ 0 ].fs_kHz - 8 ) >> 2 ];
	srai	a2, a2, 2	# tmp773, tmp771,
# @OPUS@\upstream\silk\dec_API.c:451:         int mult_tab[ 3 ] = { 6, 4, 3 };
	s32i.n	a3, sp, 24	# mult_tab, tmp769
# @OPUS@\upstream\silk\dec_API.c:452:         decControl->prevPitchLag = channel_state[ 0 ].lagPrev * mult_tab[ ( channel_state[ 0 ].fs_kHz - 8 ) >> 2 ];
	slli	a2, a2, 2	# tmp774, tmp773,
	addi	a3, sp, 16	#,,
	add.n	a2, a3, a2	# tmp775,, tmp774
# @OPUS@\upstream\silk\dec_API.c:451:         int mult_tab[ 3 ] = { 6, 4, 3 };
	s32i.n	a5, sp, 16	# mult_tab, tmp767
	s32i.n	a4, sp, 20	# mult_tab, tmp768
# @OPUS@\upstream\silk\dec_API.c:452:         decControl->prevPitchLag = channel_state[ 0 ].lagPrev * mult_tab[ ( channel_state[ 0 ].fs_kHz - 8 ) >> 2 ];
	l32i.n	a3, a8, 8	# MEM[(struct silk_decoder_state *)decState_318(D)].lagPrev, MEM[(struct silk_decoder_state *)decState_318(D)].lagPrev
	l32i.n	a2, a2, 0	# mult_tab, tmp778
	mull	a2, a2, a3	# tmp777, tmp778, MEM[(struct silk_decoder_state *)decState_318(D)].lagPrev
# @OPUS@\upstream\silk\dec_API.c:452:         decControl->prevPitchLag = channel_state[ 0 ].lagPrev * mult_tab[ ( channel_state[ 0 ].fs_kHz - 8 ) >> 2 ];
	s32i.n	a2, a13, 20	# decControl_322(D)->prevPitchLag, tmp777
	j	.L103		#
.L102:
# @OPUS@\upstream\silk\dec_API.c:454:         decControl->prevPitchLag = 0;
	movi.n	a2, 0	# tmp780,
	s32i.n	a2, a13, 20	# decControl_322(D)->prevPitchLag, tmp780
.L103:
# @OPUS@\upstream\silk\dec_API.c:457:     if( lostFlag == FLAG_PACKET_LOST ) {
	l32i	a8, sp, 712	# %sfp,
	bnei	a8, 1, .L104	#,,
# @OPUS@\upstream\silk\dec_API.c:460:        for ( i = 0; i < psDec->nChannelsInternal; i++ )
	l32i	a8, sp, 720	# %sfp,
	l32i	a2, a8, 112	# MEM[(struct silk_decoder *)decState_318(D)].nChannelsInternal, _385
# @OPUS@\upstream\silk\dec_API.c:460:        for ( i = 0; i < psDec->nChannelsInternal; i++ )
	blti	a2, 1, .L106	# _385,,
# @OPUS@\upstream\silk\dec_API.c:461:           psDec->channel_state[ i ].LastGainIndex = 10;
	l32i	a8, sp, 708	# %sfp,
	movi.n	a3, 0xa	# tmp783,
	s8i	a3, a8, 12	# MEM[(struct silk_decoder *)decState_318(D)].channel_state[0].LastGainIndex, tmp783
# @OPUS@\upstream\silk\dec_API.c:460:        for ( i = 0; i < psDec->nChannelsInternal; i++ )
	beqi	a2, 1, .L106	# _385,,
# @OPUS@\upstream\silk\dec_API.c:461:           psDec->channel_state[ i ].LastGainIndex = 10;
	l32i	a8, sp, 704	# %sfp,
	addmi	a2, a8, 0xf00	# tmp784,,
	s8i	a3, a2, 188	# MEM[(struct silk_decoder *)decState_318(D)].channel_state[1].LastGainIndex, tmp783
	j	.L106		#
.L104:
# @OPUS@\upstream\silk\dec_API.c:463:        psDec->prev_decode_only_middle = decode_only_middle;
	l32i	a2, sp, 684	# decode_only_middle, decode_only_middle
	l32i	a8, sp, 720	# %sfp,
	s32i	a2, a8, 116	# MEM[(struct silk_decoder *)decState_318(D)].prev_decode_only_middle, decode_only_middle
.L106:
# @OPUS@\upstream\silk\dec_API.c:465:     RESTORE_STACK;
	addi	a2, sp, 16	#,,
	addmi	a3, a2, 0x200	# tmp788,,
	l32i	a3, a3, 132	# _saved_stack,
	l32i	a2, sp, 656	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\dec_API.c:466:     return ret;
	j	.L8		#
.L89:
# @OPUS@\upstream\silk\dec_API.c:406:     ALLOC( samplesOut1_tmp_storage2, delay_stack_alloc
	mov.n	a4, a14	#, tmp862
	movi.n	a3, 2	#,
	mov.n	a2, a14	#, tmp862
	call0	yoradio_opus_scratch_alloc		#
.L90:
# @OPUS@\upstream\silk\dec_API.c:415:     for( n = 0; n < silk_min( decControl->nChannelsAPI, decControl->nChannelsInternal ); n++ ) {
	l32i.n	a2, a13, 4	# decControl_322(D)->nChannelsInternal, _214
	l32i.n	a3, a13, 0	# decControl_322(D)->nChannelsAPI, _203
	mov.n	a4, a2	# _214, _214
	bge	a3, a2, .L109	# _203, _214,
	mov.n	a4, a3	# _214, _203
.L109:
# @OPUS@\upstream\silk\dec_API.c:415:     for( n = 0; n < silk_min( decControl->nChannelsAPI, decControl->nChannelsInternal ); n++ ) {
	bgei	a4, 1, .L108	# _214,,
	j	.L94		#
.L73:
# @OPUS@\upstream\silk\dec_API.c:328:     ALLOC( samplesOut1_tmp_storage1, delay_stack_alloc ? ALLOC_NONE
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\dec_API.c:334:        samplesOut1_tmp[ 1 ] = samplesOut + channel_state[ 0 ].frame_length + 2;
	l32i	a8, sp, 708	# %sfp,
	l32i.n	a2, a8, 28	# MEM[(struct silk_decoder_state *)decState_318(D)].frame_length, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length
	l32i	a8, sp, 724	# %sfp,
	addi.n	a2, a2, 2	# tmp794, MEM[(struct silk_decoder_state *)decState_318(D)].frame_length,
	slli	a2, a2, 1	# tmp796, tmp794,
	add.n	a2, a8, a2	# tmp797,, tmp796
# @OPUS@\upstream\silk\dec_API.c:333:        samplesOut1_tmp[ 0 ] = samplesOut;
	s32i	a8, sp, 672	# samplesOut1_tmp,
# @OPUS@\upstream\silk\dec_API.c:334:        samplesOut1_tmp[ 1 ] = samplesOut + channel_state[ 0 ].frame_length + 2;
	s32i	a2, sp, 676	# samplesOut1_tmp, tmp797
	j	.L110		#
.L68:
# @OPUS@\upstream\silk\dec_API.c:297:             silk_stereo_decode_pred( psRangeDec, MS_pred_Q13 );
	addi	a2, sp, 16	#,,
	movi	a3, 0x288	# tmp798,
	add.n	a3, a2, a3	#,, tmp798
	l32i	a2, sp, 728	# %sfp,
	call0	silk_stereo_decode_pred		#
# @OPUS@\upstream\silk\dec_API.c:300:                 ( lostFlag == FLAG_DECODE_LBRR && channel_state[ 1 ].LBRR_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) )
	l32i	a8, sp, 708	# %sfp,
	l32i	a2, a8, 88	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded
	l32i	a8, sp, 704	# %sfp,
	add.n	a2, a12, a2	# tmp802, tmp551, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded
	addmi	a8, a8, 0xb00	#,,
	slli	a2, a2, 2	# tmp805, tmp802,
	add.n	a2, a8, a2	# tmp806,, tmp805
# @OPUS@\upstream\silk\dec_API.c:300:                 ( lostFlag == FLAG_DECODE_LBRR && channel_state[ 1 ].LBRR_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) )
	l32i	a2, a2, 184	#, tmp809
# @OPUS@\upstream\silk\dec_API.c:300:                 ( lostFlag == FLAG_DECODE_LBRR && channel_state[ 1 ].LBRR_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) )
	s32i	a8, sp, 696	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:300:                 ( lostFlag == FLAG_DECODE_LBRR && channel_state[ 1 ].LBRR_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) )
	beqz.n	a2, .L111	# tmp809,
	j	.L112		#
.L65:
# @OPUS@\upstream\silk\dec_API.c:297:             silk_stereo_decode_pred( psRangeDec, MS_pred_Q13 );
	addi	a2, sp, 16	#,,
	movi	a3, 0x288	# tmp810,
	add.n	a3, a2, a3	#,, tmp810
	l32i	a2, sp, 728	# %sfp,
	call0	silk_stereo_decode_pred		#
# @OPUS@\upstream\silk\dec_API.c:299:             if( ( lostFlag == FLAG_DECODE_NORMAL && channel_state[ 1 ].VAD_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) ||
	l32i	a8, sp, 708	# %sfp,
	movi	a2, 0x118	# tmp813,
	l32i	a3, a8, 88	# MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded
	l32i	a8, sp, 704	# %sfp,
	add.n	a2, a2, a3	# tmp814, tmp813, MEM[(struct silk_decoder_state *)decState_318(D)].nFramesDecoded
	addmi	a8, a8, 0xb00	#,,
	slli	a2, a2, 2	# tmp817, tmp814,
	add.n	a2, a8, a2	# tmp818,, tmp817
# @OPUS@\upstream\silk\dec_API.c:299:             if( ( lostFlag == FLAG_DECODE_NORMAL && channel_state[ 1 ].VAD_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) ||
	l32i	a2, a2, 184	#, tmp821
# @OPUS@\upstream\silk\dec_API.c:299:             if( ( lostFlag == FLAG_DECODE_NORMAL && channel_state[ 1 ].VAD_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) ||
	s32i	a8, sp, 696	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:299:             if( ( lostFlag == FLAG_DECODE_NORMAL && channel_state[ 1 ].VAD_flags[ channel_state[ 0 ].nFramesDecoded ] == 0 ) ||
	beqz.n	a2, .L111	# tmp821,
	j	.L112		#
.L76:
# @OPUS@\upstream\silk\dec_API.c:346:     channel_state[ 0 ].sPLC.enable_deep_plc = decControl->enable_deep_plc;
	s32i	a3, a8, 172	# MEM[(struct silk_decoder_state *)decState_318(D)].sPLC.enable_deep_plc, pretmp_825
	j	.L113		#
.L31:
# @OPUS@\upstream\silk\dec_API.c:293:     if( decControl->nChannelsInternal == 2 ) {
	beqi	a3, 2, .L69	# prephitmp_630,,
	j	.L232		#
.L229:
	l32i	a13, sp, 696	# %sfp, decControl
.L45:
	beqi	a3, 2, .L65	# prephitmp_630,,
.L233:
	l32i.n	a4, a13, 8	# decControl_322(D)->API_sampleRate, _55
	l32i.n	a15, a13, 0	# decControl_322(D)->nChannelsAPI, prephitmp_638
.L232:
	l32i	a8, sp, 704	# %sfp,
	addmi	a8, a8, 0xb00	#,,
	s32i	a8, sp, 696	# %sfp,
	j	.L70		#
.L44:
	beqi	a3, 2, .L114	# prephitmp_630,,
	j	.L233		#
.L15:
# @OPUS@\upstream\silk\dec_API.c:191:     if( channel_state[ 0 ].nFramesDecoded == 0 ) {
	l32i	a8, sp, 736	# %sfp,
	beqz.n	a8, .L126	#,
	j	.L227		#
.L226:
# @OPUS@\upstream\silk\dec_API.c:346:     channel_state[ 0 ].sPLC.enable_deep_plc = decControl->enable_deep_plc;
	s32i	a3, a8, 172	# MEM[(struct silk_decoder_state *)decState_318(D)].sPLC.enable_deep_plc, pretmp_825
	mov.n	a12, a5	# prephitmp_719, tmp608
	j	.L113		#
.L14:
# @OPUS@\upstream\silk\dec_API.c:191:     if( channel_state[ 0 ].nFramesDecoded == 0 ) {
	l32i	a8, sp, 736	# %sfp,
	beqz.n	a8, .L115	#,
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	movi.n	a8, 0	#,
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	l32i.n	a15, a13, 0	# decControl_322(D)->nChannelsAPI, prephitmp_638
# @OPUS@\upstream\silk\dec_API.c:188:     stereo_to_mono = decControl->nChannelsInternal == 1 && psDec->nChannelsInternal == 2 &&
	s32i	a8, sp, 736	# %sfp,
# @OPUS@\upstream\silk\dec_API.c:225:     if( decControl->nChannelsAPI == 2 && decControl->nChannelsInternal == 2 && ( psDec->nChannelsAPI == 1 || psDec->nChannelsInternal == 1 ) ) {
	beqi	a15, 2, .L117	# prephitmp_638,,
	j	.L26		#
.L8:
# @OPUS@\upstream\silk\dec_API.c:467: }
	l32i	a0, sp, 780	#,
	movi	a9, 0x310	#,
	l32i	a2, sp, 688	# %sfp,
	l32i	a12, sp, 776	#,
	l32i	a13, sp, 772	#,
	l32i	a14, sp, 768	#,
	l32i	a15, sp, 764	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_Decode, .-silk_Decode
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
