# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/PLC.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"PLC.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\PLC.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\PLC.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\PLC.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\PLC.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\PLC.c.s.raw
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
	.section	.text.silk_PLC_Reset,"ax",@progbits
	.literal_position
	.literal .LC0, 65536
	.align	4
	.global	silk_PLC_Reset
	.type	silk_PLC_Reset, @function
# Function: silk_PLC_Reset
# Module: upstream/silk/PLC.c
# SILK packet-loss concealment and state recovery.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: );
# C context:
# C context:
# C context: void silk_PLC_Reset(
# C context: silk_decoder_state                  *psDec              /* I/O Decoder state        */
# C context: )
# C context: {
# C context: psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
silk_PLC_Reset:
# @OPUS@\upstream\silk\PLC.c:86:     psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
	addmi	a3, a2, 0x400	# tmp48, psDec,
	l32i.n	a3, a3, 28	# psDec_6(D)->frame_length, psDec_6(D)->frame_length
# @OPUS@\upstream\silk\PLC.c:86:     psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
	addmi	a2, a2, 0xb00	# tmp47, psDec,
# @OPUS@\upstream\silk\PLC.c:86:     psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
	slli	a3, a3, 7	# tmp49, psDec_6(D)->frame_length,
# @OPUS@\upstream\silk\PLC.c:87:     psDec->sPLC.prevGain_Q16[ 0 ] = SILK_FIX_CONST( 1, 16 );
	l32r	a4, .LC0	#, tmp52
# @OPUS@\upstream\silk\PLC.c:86:     psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
	s32i	a3, a2, 80	# psDec_6(D)->sPLC.pitchL_Q8, tmp49
# @OPUS@\upstream\silk\PLC.c:89:     psDec->sPLC.subfr_length = 20;
	movi.n	a3, 0x14	# tmp56,
	s32i	a3, a2, 168	# psDec_6(D)->sPLC.subfr_length, tmp56
# @OPUS@\upstream\silk\PLC.c:90:     psDec->sPLC.nb_subfr = 2;
	movi.n	a3, 2	# tmp58,
# @OPUS@\upstream\silk\PLC.c:87:     psDec->sPLC.prevGain_Q16[ 0 ] = SILK_FIX_CONST( 1, 16 );
	s32i	a4, a2, 152	# psDec_6(D)->sPLC.prevGain_Q16, tmp52
# @OPUS@\upstream\silk\PLC.c:88:     psDec->sPLC.prevGain_Q16[ 1 ] = SILK_FIX_CONST( 1, 16 );
	s32i	a4, a2, 156	# psDec_6(D)->sPLC.prevGain_Q16, tmp52
# @OPUS@\upstream\silk\PLC.c:90:     psDec->sPLC.nb_subfr = 2;
	s32i	a3, a2, 164	# psDec_6(D)->sPLC.nb_subfr, tmp58
# @OPUS@\upstream\silk\PLC.c:91: }
	ret.n
	.size	silk_PLC_Reset, .-silk_PLC_Reset
	.global	__divsi3
	.global	__udivsi3
	.section	.text.silk_PLC,"ax",@progbits
	.literal_position
	.literal .LC1, 32767
	.literal .LC2, -32768
	.literal .LC3, 16384
	.literal .LC4, -2147483648
	.literal .LC5, 2147483632
	.literal .LC6, 2147483647
	.literal .LC7, 13312
	.literal .LC8, 65536
	.literal .LC9, 2896
	.literal .LC10, HARM_ATT_Q15
	.literal .LC11, PLC_RAND_ATTENUATE_V_Q15
	.literal .LC12, PLC_RAND_ATTENUATE_UV_Q15
	.literal .LC13, 64881
	.literal .LC14, 3277
	.literal .LC15, 134217728
	.literal .LC16, 4194304
	.literal .LC17, 536870911
	.literal .LC18, 536870912
	.literal .LC19, 1073741823
	.literal .LC20, 196314165
	.literal .LC21, 907633515
	.literal .LC23, 134217727
	.literal .LC24, -134217728
	.literal .LC25, 11468
	.literal .LC26, 11744256
	.literal .LC27, 15565
	.literal .LC28, 255016960
	.align	4
	.global	silk_PLC
	.type	silk_PLC, @function
# Function: silk_PLC
# Module: upstream/silk/PLC.c
# SILK packet-loss concealment and state recovery.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: psDec->sPLC.nb_subfr = 2;
# C context: }
# C context:
# C context: void silk_PLC(
# C context: silk_decoder_state                  *psDec,             /* I/O Decoder state        */
# C context: silk_decoder_control                *psDecCtrl,         /* I/O Decoder control      */
# C context: opus_int16                          frame[],            /* I/O  signal              */
# C context: opus_int                            lost,               /* I Loss flag              */
silk_PLC:
	movi	a9, 0xf0	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\PLC.c:105:     if( psDec->fs_kHz != psDec->sPLC.fs_kHz ) {
	addmi	a8, a2, 0x400	#, psDec,
# @OPUS@\upstream\silk\PLC.c:103: {
	s32i	a12, sp, 232	#,
# @OPUS@\upstream\silk\PLC.c:105:     if( psDec->fs_kHz != psDec->sPLC.fs_kHz ) {
	addmi	a12, a2, 0xb00	# tmp1807, psDec,
# @OPUS@\upstream\silk\PLC.c:103: {
	s32i	a2, sp, 76	# %sfp, psDec
# @OPUS@\upstream\silk\PLC.c:105:     if( psDec->fs_kHz != psDec->sPLC.fs_kHz ) {
	l32i.n	a7, a8, 16	# psDec_8(D)->fs_kHz, _1
# @OPUS@\upstream\silk\PLC.c:105:     if( psDec->fs_kHz != psDec->sPLC.fs_kHz ) {
	l32i	a2, a12, 160	# psDec_8(D)->sPLC.fs_kHz, psDec_8(D)->sPLC.fs_kHz
# @OPUS@\upstream\silk\PLC.c:103: {
	s32i	a0, sp, 236	#,
	s32i	a13, sp, 228	#,
	s32i	a14, sp, 224	#,
	s32i	a15, sp, 220	#,
# @OPUS@\upstream\silk\PLC.c:105:     if( psDec->fs_kHz != psDec->sPLC.fs_kHz ) {
	s32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:103: {
	s32i	a3, sp, 100	# %sfp, psDecCtrl
	s32i	a4, sp, 116	# %sfp, frame
	s32i	a6, sp, 104	# %sfp, arch
# @OPUS@\upstream\silk\PLC.c:105:     if( psDec->fs_kHz != psDec->sPLC.fs_kHz ) {
	beq	a7, a2, .L4	# _1, psDec_8(D)->sPLC.fs_kHz,
# @OPUS@\upstream\silk\PLC.c:86:     psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
	l32i.n	a2, a8, 28	# psDec_8(D)->frame_length, psDec_8(D)->frame_length
# @OPUS@\upstream\silk\PLC.c:87:     psDec->sPLC.prevGain_Q16[ 0 ] = SILK_FIX_CONST( 1, 16 );
	l32r	a3, .LC8	#, tmp811
# @OPUS@\upstream\silk\PLC.c:86:     psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
	slli	a2, a2, 7	# tmp808, psDec_8(D)->frame_length,
# @OPUS@\upstream\silk\PLC.c:86:     psDec->sPLC.pitchL_Q8 = silk_LSHIFT( psDec->frame_length, 8 - 1 );
	s32i	a2, a12, 80	# psDec_8(D)->sPLC.pitchL_Q8, tmp808
# @OPUS@\upstream\silk\PLC.c:89:     psDec->sPLC.subfr_length = 20;
	movi.n	a2, 0x14	# tmp815,
	s32i	a2, a12, 168	# psDec_8(D)->sPLC.subfr_length, tmp815
# @OPUS@\upstream\silk\PLC.c:90:     psDec->sPLC.nb_subfr = 2;
	movi.n	a2, 2	# tmp817,
# @OPUS@\upstream\silk\PLC.c:87:     psDec->sPLC.prevGain_Q16[ 0 ] = SILK_FIX_CONST( 1, 16 );
	s32i	a3, a12, 152	# psDec_8(D)->sPLC.prevGain_Q16, tmp811
# @OPUS@\upstream\silk\PLC.c:88:     psDec->sPLC.prevGain_Q16[ 1 ] = SILK_FIX_CONST( 1, 16 );
	s32i	a3, a12, 156	# psDec_8(D)->sPLC.prevGain_Q16, tmp811
# @OPUS@\upstream\silk\PLC.c:90:     psDec->sPLC.nb_subfr = 2;
	s32i	a2, a12, 164	# psDec_8(D)->sPLC.nb_subfr, tmp817
# @OPUS@\upstream\silk\PLC.c:107:         psDec->sPLC.fs_kHz = psDec->fs_kHz;
	s32i	a7, a12, 160	# psDec_8(D)->sPLC.fs_kHz, _1
.L4:
	l32i	a11, sp, 76	# %sfp,
	l32r	a13, .LC9	#,
	add.n	a3, a11, a13	# tmp819,,
	addi.n	a14, a3, 14	#, tmp819,
	s32i	a14, sp, 68	# %sfp,
	addi.n	a2, a3, 4	# pretmp_1856, tmp819,
# @OPUS@\upstream\silk\PLC.c:110:     if( lost ) {
	beqz.n	a5, .L5	# lost,
# @OPUS@\upstream\silk\PLC.c:269:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\PLC.c:275:     ALLOC( sLTP_Q14, psDec->ltp_mem_length + psDec->frame_length, opus_int32 );
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:269:     SAVE_STACK;
	s32i.n	a2, sp, 32	# _saved_stack,
# @OPUS@\upstream\silk\PLC.c:275:     ALLOC( sLTP_Q14, psDec->ltp_mem_length + psDec->frame_length, opus_int32 );
	l32i.n	a6, a8, 36	# psDec_8(D)->ltp_mem_length, psDec_8(D)->ltp_mem_length
	l32i.n	a5, a8, 28	# psDec_8(D)->frame_length, psDec_8(D)->frame_length
# @OPUS@\upstream\silk\PLC.c:269:     SAVE_STACK;
	s32i.n	a3, sp, 36	# _saved_stack,
# @OPUS@\upstream\silk\PLC.c:275:     ALLOC( sLTP_Q14, psDec->ltp_mem_length + psDec->frame_length, opus_int32 );
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	add.n	a2, a6, a5	#, psDec_8(D)->ltp_mem_length, psDec_8(D)->frame_length
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\PLC.c:281:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	l32i	a11, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:275:     ALLOC( sLTP_Q14, psDec->ltp_mem_length + psDec->frame_length, opus_int32 );
	s32i	a2, sp, 96	# %sfp,
# @OPUS@\upstream\silk\PLC.c:281:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	l32i.n	a2, a11, 36	# psDec_8(D)->ltp_mem_length,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 84	# %sfp,
# @OPUS@\upstream\silk\PLC.c:284:     prevGain_Q10[0] = silk_RSHIFT( psPLC->prevGain_Q16[ 0 ], 6);
	l32i	a3, a12, 152	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevGain_Q16, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevGain_Q16
# @OPUS@\upstream\silk\PLC.c:285:     prevGain_Q10[1] = silk_RSHIFT( psPLC->prevGain_Q16[ 1 ], 6);
	l32i	a2, a12, 156	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevGain_Q16, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevGain_Q16
# @OPUS@\upstream\silk\PLC.c:287:     if( psDec->first_frame_after_reset ) {
	l32i	a13, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:284:     prevGain_Q10[0] = silk_RSHIFT( psPLC->prevGain_Q16[ 0 ], 6);
	srai	a3, a3, 6	# tmp831, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevGain_Q16,
# @OPUS@\upstream\silk\PLC.c:285:     prevGain_Q10[1] = silk_RSHIFT( psPLC->prevGain_Q16[ 1 ], 6);
	srai	a2, a2, 6	# tmp834, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevGain_Q16,
# @OPUS@\upstream\silk\PLC.c:287:     if( psDec->first_frame_after_reset ) {
	l32i	a4, a13, 76	# psDec_8(D)->first_frame_after_reset, psDec_8(D)->first_frame_after_reset
# @OPUS@\upstream\silk\PLC.c:284:     prevGain_Q10[0] = silk_RSHIFT( psPLC->prevGain_Q16[ 0 ], 6);
	s32i.n	a3, sp, 40	# prevGain_Q10, tmp831
# @OPUS@\upstream\silk\PLC.c:285:     prevGain_Q10[1] = silk_RSHIFT( psPLC->prevGain_Q16[ 1 ], 6);
	s32i.n	a2, sp, 44	# prevGain_Q10, tmp834
# @OPUS@\upstream\silk\PLC.c:287:     if( psDec->first_frame_after_reset ) {
	beqz.n	a4, .L6	# psDec_8(D)->first_frame_after_reset,
# @OPUS@\upstream\silk\PLC.c:288:        silk_memset( psPLC->prevLPC_Q12, 0, sizeof( psPLC->prevLPC_Q12 ) );
	l32i	a2, sp, 68	# %sfp,
	movi.n	a4, 0x20	#,
	movi.n	a3, 0	#,
	call0	memset		#
.L6:
# @OPUS@\upstream\silk\PLC.c:291:     silk_PLC_energy(&energy1, &shift1, &energy2, &shift2, psDec->exc_Q14, prevGain_Q10, psDec->subfr_length, psDec->nb_subfr);
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:291:     silk_PLC_energy(&energy1, &shift1, &energy2, &shift2, psDec->exc_Q14, prevGain_Q10, psDec->subfr_length, psDec->nb_subfr);
	l32i	a11, sp, 76	# %sfp,
# @OPUS@\upstream\silk\PLC.c:291:     silk_PLC_energy(&energy1, &shift1, &energy2, &shift2, psDec->exc_Q14, prevGain_Q10, psDec->subfr_length, psDec->nb_subfr);
	l32i.n	a14, a8, 32	# psDec_8(D)->subfr_length, _41
# @OPUS@\upstream\silk\PLC.c:291:     silk_PLC_energy(&energy1, &shift1, &energy2, &shift2, psDec->exc_Q14, prevGain_Q10, psDec->subfr_length, psDec->nb_subfr);
	l32i.n	a5, a11, 0	# psDec_8(D)->exc_Q14, _40
# @OPUS@\upstream\silk\PLC.c:291:     silk_PLC_energy(&energy1, &shift1, &energy2, &shift2, psDec->exc_Q14, prevGain_Q10, psDec->subfr_length, psDec->nb_subfr);
	l32i.n	a13, a8, 24	# psDec_8(D)->nb_subfr, _42
# @OPUS@\upstream\silk\PLC.c:220:     ALLOC( exc_buf, 2*subfr_length, opus_int16 );
	slli	a15, a14, 1	# _503, _41,
# @OPUS@\upstream\silk\PLC.c:219:     SAVE_STACK;
	s32i	a5, sp, 188	#,
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\PLC.c:220:     ALLOC( exc_buf, 2*subfr_length, opus_int16 );
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a15	#, _503
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 72	# %sfp,
	addi	a2, a13, -2	# tmp844, _42,
	mull	a2, a2, a14	# tmp845, tmp844, _41
	l32i	a5, sp, 188	#,
	slli	a13, a14, 2	#, _41,
	slli	a2, a2, 2	# tmp846, tmp845,
	s32i	a13, sp, 88	# %sfp,
	add.n	a2, a5, a2	# ivtmp$137, _40, tmp846
	addi	a13, sp, 48	# tmp1814,,
	addi	a5, sp, 40	# ivtmp$138,,
# @OPUS@\upstream\silk\PLC.c:223:     exc_buf_ptr = exc_buf;
	l32i	a9, sp, 72	# %sfp, exc_buf_ptr
	j	.L7		#
.L9:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a11, a4, 0	# value, ivtmp$126
# 0 "" 2
# @OPUS@\upstream\silk\PLC.c:228:             exc_buf_ptr[i] = (opus_int16)silk_SAT16(silk_RSHIFT(silk_SMULWW(excitation, prevGain_Q10[k]), 8));
#NO_APP
	l32i.n	a2, a5, 0	# MEM[base: _1311, offset: 0B], _520
	l16si	a8, a5, 0	# MEM[base: _1311, offset: 0B], _522
	srai	a2, a2, 15	# tmp849, _520,
	addi.n	a2, a2, 1	# tmp850, tmp849,
	srai	a2, a2, 1	# tmp851, tmp850,
	srai	a7, a11, 16	# tmp853, value,
	extui	a3, a11, 0, 16	# tmp856, value,
	mull	a2, a2, a11	# tmp852, tmp851, value
	mull	a7, a7, a8	# tmp854, tmp853, _522
	mull	a3, a3, a8	# tmp857, tmp856, _522
	add.n	a2, a2, a7	# tmp855, tmp852, tmp854
	srai	a3, a3, 16	# tmp858, tmp857,
	add.n	a2, a2, a3	# tmp859, tmp855, tmp858
# @OPUS@\upstream\silk\PLC.c:228:             exc_buf_ptr[i] = (opus_int16)silk_SAT16(silk_RSHIFT(silk_SMULWW(excitation, prevGain_Q10[k]), 8));
	l32r	a3, .LC1	#, iftmp$61_534
# @OPUS@\upstream\silk\PLC.c:228:             exc_buf_ptr[i] = (opus_int16)silk_SAT16(silk_RSHIFT(silk_SMULWW(excitation, prevGain_Q10[k]), 8));
	srai	a2, a2, 8	# _533, tmp859,
	addi.n	a4, a4, 4	# ivtmp$126, ivtmp$126,
# @OPUS@\upstream\silk\PLC.c:228:             exc_buf_ptr[i] = (opus_int16)silk_SAT16(silk_RSHIFT(silk_SMULWW(excitation, prevGain_Q10[k]), 8));
	blt	a3, a2, .L8	# tmp7, _533,
	l32r	a3, .LC2	#, iftmp$61_534
	slli	a7, a2, 16	# tmp862, _533,
	blt	a2, a3, .L8	# _533, tmp8,
	srai	a3, a7, 16	# iftmp$61_534, tmp862,
.L8:
# @OPUS@\upstream\silk\PLC.c:228:             exc_buf_ptr[i] = (opus_int16)silk_SAT16(silk_RSHIFT(silk_SMULWW(excitation, prevGain_Q10[k]), 8));
	s16i	a3, a6, 0	# MEM[base: _1337, offset: 0B], iftmp$61_534
	addi.n	a6, a6, 2	# ivtmp$127, ivtmp$127,
# @OPUS@\upstream\silk\PLC.c:225:         for( i = 0; i < subfr_length; i++ ) {
	bne	a10, a4, .L9	# ivtmp$137, ivtmp$126,
.L12:
	addi.n	a5, a5, 4	# ivtmp$138, ivtmp$138,
# @OPUS@\upstream\silk\PLC.c:234:         exc_buf_ptr += subfr_length;
	add.n	a9, a9, a15	# exc_buf_ptr, exc_buf_ptr, _503
	mov.n	a2, a10	# ivtmp$137, ivtmp$137
# @OPUS@\upstream\silk\PLC.c:224:     for( k = 0; k < 2; k++ ) {
	beq	a13, a5, .L10	# tmp1814, ivtmp$138,
.L7:
	l32i	a11, sp, 88	# %sfp,
	mov.n	a6, a9	# ivtmp$127, exc_buf_ptr
	add.n	a10, a11, a2	# ivtmp$137,, ivtmp$137
# @OPUS@\upstream\silk\PLC.c:225:         for( i = 0; i < subfr_length; i++ ) {
	mov.n	a4, a2	# ivtmp$126, ivtmp$137
	bgei	a14, 1, .L9	# _41,,
	j	.L12		#
.L10:
# @OPUS@\upstream\silk\PLC.c:237:     silk_sum_sqr_shift( energy1, shift1, exc_buf,                  subfr_length );
	l32i	a4, sp, 72	# %sfp,
	mov.n	a5, a14	#, _41
	addi	a3, sp, 60	#,,
	addi	a2, sp, 52	#,,
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\PLC.c:238:     silk_sum_sqr_shift( energy2, shift2, &exc_buf[ subfr_length ], subfr_length );
	mov.n	a5, a14	#, _41
	l32i	a14, sp, 72	# %sfp,
	addi	a3, sp, 56	#,,
	add.n	a4, a14, a15	#,, _503
	mov.n	a2, a13	#, tmp1814
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\PLC.c:239:     RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\PLC.c:293:     if( silk_RSHIFT( energy1, shift2 ) < silk_RSHIFT( energy2, shift1 ) ) {
	l32i.n	a2, sp, 56	# shift2, shift2
	l32i.n	a3, sp, 52	# energy1, energy1
# @OPUS@\upstream\silk\PLC.c:293:     if( silk_RSHIFT( energy1, shift2 ) < silk_RSHIFT( energy2, shift1 ) ) {
	l32i.n	a4, sp, 60	# shift1, shift1
# @OPUS@\upstream\silk\PLC.c:293:     if( silk_RSHIFT( energy1, shift2 ) < silk_RSHIFT( energy2, shift1 ) ) {
	ssr	a2	# shift2
	sra	a3, a3	# tmp868, energy1
# @OPUS@\upstream\silk\PLC.c:293:     if( silk_RSHIFT( energy1, shift2 ) < silk_RSHIFT( energy2, shift1 ) ) {
	l32i.n	a2, sp, 48	# energy2, energy2
	ssr	a4	# shift1
	sra	a2, a2	# tmp871, energy2
# @OPUS@\upstream\silk\PLC.c:293:     if( silk_RSHIFT( energy1, shift2 ) < silk_RSHIFT( energy2, shift1 ) ) {
	bge	a3, a2, .L13	# tmp868, tmp871,
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	l32i	a2, a12, 164	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].nb_subfr, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].nb_subfr
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	l32i	a3, a12, 168	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].subfr_length, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].subfr_length
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	addi.n	a2, a2, -1	# tmp876, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].nb_subfr,
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	mull	a2, a2, a3	# tmp879, tmp876, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].subfr_length
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	l32i	a8, sp, 76	# %sfp,
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	movi.n	a3, 0	# tmp881,
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	addi	a2, a2, -128	# tmp874, tmp879,
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	movltz	a2, a3, a2	# tmp874, tmp881, tmp874
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	l32i.n	a3, a8, 0	# psDec_8(D)->exc_Q14, psDec_8(D)->exc_Q14
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	slli	a2, a2, 2	# tmp882, tmp874,
# @OPUS@\upstream\silk\PLC.c:295:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, ( psPLC->nb_subfr - 1 ) * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	add.n	a3, a3, a2	#, psDec_8(D)->exc_Q14, tmp882
	s32i	a3, sp, 124	# %sfp,
	j	.L14		#
.L13:
# @OPUS@\upstream\silk\PLC.c:298:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, psPLC->nb_subfr * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	l32i	a3, a12, 168	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].subfr_length, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].subfr_length
	l32i	a2, a12, 164	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].nb_subfr, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].nb_subfr
# @OPUS@\upstream\silk\PLC.c:298:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, psPLC->nb_subfr * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	l32i	a11, sp, 76	# %sfp,
# @OPUS@\upstream\silk\PLC.c:298:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, psPLC->nb_subfr * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	mull	a2, a2, a3	# tmp887, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].nb_subfr, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].subfr_length
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	movi.n	a4, 0	# tmp890,
# @OPUS@\upstream\silk\PLC.c:298:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, psPLC->nb_subfr * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	addi	a2, a2, -128	# tmp884, tmp887,
# @OPUS@\upstream\silk\PLC.c:298:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, psPLC->nb_subfr * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	l32i.n	a3, a11, 0	# psDec_8(D)->exc_Q14, psDec_8(D)->exc_Q14
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	movltz	a2, a4, a2	# tmp884, tmp890, tmp884
# @OPUS@\upstream\silk\PLC.c:298:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, psPLC->nb_subfr * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	slli	a2, a2, 2	# tmp891, tmp884,
# @OPUS@\upstream\silk\PLC.c:298:         rand_ptr = &psDec->exc_Q14[ silk_max_int( 0, psPLC->nb_subfr * psPLC->subfr_length - RAND_BUF_SIZE ) ];
	add.n	a3, a3, a2	#, psDec_8(D)->exc_Q14, tmp891
	s32i	a3, sp, 124	# %sfp,
.L14:
# @OPUS@\upstream\silk\PLC.c:303:     rand_scale_Q14 = psPLC->randScale_Q14;
	l16si	a13, a12, 136	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].randScale_Q14,
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	l32i	a2, a12, 68	# psDec_8(D)->lossCnt, _71
# @OPUS@\upstream\silk\PLC.c:303:     rand_scale_Q14 = psPLC->randScale_Q14;
	s32i	a13, sp, 88	# %sfp,
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	blti	a2, 1, .L15	# _71,,
	movi.n	a2, 1	# _71,
.L15:
# @OPUS@\upstream\silk\PLC.c:306:     harm_Gain_Q15 = HARM_ATT_Q15[ silk_min_int( NB_ATT - 1, psDec->lossCnt ) ];
	l32r	a3, .LC10	#, tmp903
	slli	a2, a2, 1	# tmp904, _71,
	add.n	a3, a3, a2	# tmp905, tmp903, tmp904
	l16si	a3, a3, 0	# HARM_ATT_Q15,
# @OPUS@\upstream\silk\PLC.c:307:     if( psDec->prevSignalType == TYPE_VOICED ) {
	l32i	a4, a12, 72	# psDec_8(D)->prevSignalType, psDec_8(D)->prevSignalType
# @OPUS@\upstream\silk\PLC.c:306:     harm_Gain_Q15 = HARM_ATT_Q15[ silk_min_int( NB_ATT - 1, psDec->lossCnt ) ];
	s32i	a3, sp, 72	# %sfp,
# @OPUS@\upstream\silk\PLC.c:307:     if( psDec->prevSignalType == TYPE_VOICED ) {
	bnei	a4, 2, .L16	# psDec_8(D)->prevSignalType,,
# @OPUS@\upstream\silk\PLC.c:308:         rand_Gain_Q15 = PLC_RAND_ATTENUATE_V_Q15[  silk_min_int( NB_ATT - 1, psDec->lossCnt ) ];
	l32r	a3, .LC11	#, tmp910
	add.n	a2, a3, a2	# tmp912, tmp910, tmp904
# @OPUS@\upstream\silk\PLC.c:308:         rand_Gain_Q15 = PLC_RAND_ATTENUATE_V_Q15[  silk_min_int( NB_ATT - 1, psDec->lossCnt ) ];
	l16si	a2, a2, 0	#,
	s32i	a2, sp, 92	# %sfp,
	j	.L17		#
.L16:
# @OPUS@\upstream\silk\PLC.c:310:         rand_Gain_Q15 = PLC_RAND_ATTENUATE_UV_Q15[ silk_min_int( NB_ATT - 1, psDec->lossCnt ) ];
	l32r	a3, .LC12	#, tmp915
	add.n	a2, a3, a2	# tmp917, tmp915, tmp904
# @OPUS@\upstream\silk\PLC.c:310:         rand_Gain_Q15 = PLC_RAND_ATTENUATE_UV_Q15[ silk_min_int( NB_ATT - 1, psDec->lossCnt ) ];
	l16si	a2, a2, 0	#,
	s32i	a2, sp, 92	# %sfp,
.L17:
# @OPUS@\upstream\silk\PLC.c:314:     silk_bwexpander( psPLC->prevLPC_Q12, psDec->LPC_order, SILK_FIX_CONST( BWE_COEF, 16 ) );
	l32i	a14, sp, 64	# %sfp,
	l32r	a4, .LC13	#,
	l32i.n	a3, a14, 40	# psDec_8(D)->LPC_order,
	l32i	a2, sp, 68	# %sfp,
	call0	silk_bwexpander		#
# @OPUS@\upstream\silk\PLC.c:317:     silk_memcpy( A_Q12, psPLC->prevLPC_Q12, psDec->LPC_order * sizeof( opus_int16 ) );
	l32i.n	a13, a14, 40	# psDec_8(D)->LPC_order, _81
	l32i	a3, sp, 68	# %sfp,
	slli	a4, a13, 1	#, _81,
	mov.n	a2, sp	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\PLC.c:320:     if( psDec->lossCnt == 0 ) {
	l32i	a2, a12, 68	# psDec_8(D)->lossCnt, psDec_8(D)->lossCnt
	bnez.n	a2, .L18	# psDec_8(D)->lossCnt,
# @OPUS@\upstream\silk\PLC.c:324:         if( psDec->prevSignalType == TYPE_VOICED ) {
	l32i	a2, a12, 72	# psDec_8(D)->prevSignalType, psDec_8(D)->prevSignalType
	bnei	a2, 2, .L19	# psDec_8(D)->prevSignalType,,
# @OPUS@\upstream\silk\PLC.c:326:                 rand_scale_Q14 -= B_Q14[ i ];
	l16ui	a3, a12, 84	# MEM[(opus_int16 *)psDec_8(D) + 2900B],
	l32r	a5, .LC3	#, tmp935
	l16ui	a2, a12, 86	# MEM[(opus_int16 *)psDec_8(D) + 2902B],
	sub	a5, a5, a3	# tmp934, tmp935, MEM[(opus_int16 *)psDec_8(D) + 2900B]
	l16ui	a3, a12, 88	# MEM[(opus_int16 *)psDec_8(D) + 2904B],
	sub	a5, a5, a2	# tmp939, tmp934, MEM[(opus_int16 *)psDec_8(D) + 2902B]
	l16ui	a2, a12, 90	# MEM[(opus_int16 *)psDec_8(D) + 2906B],
	sub	a5, a5, a3	# tmp943, tmp939, MEM[(opus_int16 *)psDec_8(D) + 2904B]
	sub	a5, a5, a2	# tmp947, tmp943, MEM[(opus_int16 *)psDec_8(D) + 2906B]
	l16ui	a3, a12, 92	# MEM[(opus_int16 *)psDec_8(D) + 2908B],
	slli	a5, a5, 16	# tmp948, tmp947,
	srai	a5, a5, 16	# rand_scale_Q14, tmp948,
# @OPUS@\upstream\silk\SigProc_FIX.h:570:     return (((a) > (b)) ? (a) : (b));
	l32r	a2, .LC14	#, tmp953
# @OPUS@\upstream\silk\PLC.c:326:                 rand_scale_Q14 -= B_Q14[ i ];
	sub	a5, a5, a3	# tmp952, rand_scale_Q14, MEM[(opus_int16 *)psDec_8(D) + 2908B]
# @OPUS@\upstream\silk\SigProc_FIX.h:570:     return (((a) > (b)) ? (a) : (b));
	slli	a2, a2, 16	# tmp957, tmp953,
	slli	a3, a5, 16	# tmp956, tmp952,
	bge	a3, a2, .L20	# tmp956, tmp957,
	l32r	a5, .LC14	#, tmp949
.L20:
# @OPUS@\upstream\silk\PLC.c:329:             rand_scale_Q14 = (opus_int16)silk_RSHIFT( silk_SMULBB( rand_scale_Q14, psPLC->prevLTP_scale_Q14 ), 14 );
	l16ui	a2, a12, 148	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevLTP_scale_Q14,
	mul16s	a5, a5, a2	# tmp959, tmp949, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevLTP_scale_Q14
# @OPUS@\upstream\silk\PLC.c:329:             rand_scale_Q14 = (opus_int16)silk_RSHIFT( silk_SMULBB( rand_scale_Q14, psPLC->prevLTP_scale_Q14 ), 14 );
	slli	a5, a5, 2	# tmp961, tmp959,
	srai	a5, a5, 16	#, tmp961,
	s32i	a5, sp, 88	# %sfp,
	j	.L18		#
.L19:
# @OPUS@\upstream\silk\PLC.c:334:             invGain_Q30 = silk_LPC_inverse_pred_gain( psPLC->prevLPC_Q12, psDec->LPC_order, arch );
	l32i	a2, sp, 68	# %sfp,
	mov.n	a3, a13	#, _81
	call0	silk_LPC_inverse_pred_gain_c		#
# @OPUS@\upstream\silk\SigProc_FIX.h:556:     return (((a) < (b)) ? (a) : (b));
	l32r	a3, .LC15	#, tmp967
	bge	a3, a2, .L21	# tmp967, invGain_Q30,
	mov.n	a2, a3	# invGain_Q30, tmp967
.L21:
# @OPUS@\upstream\silk\SigProc_FIX.h:574:     return (((a) > (b)) ? (a) : (b));
	l32r	a3, .LC16	#, tmp972
	bge	a2, a3, .L22	# invGain_Q30, tmp972,
	mov.n	a2, a3	# invGain_Q30, tmp972
.L22:
# @OPUS@\upstream\silk\PLC.c:340:             rand_Gain_Q15 = silk_RSHIFT( silk_SMULWB( down_scale_Q30, rand_Gain_Q15 ), 14 );
	l32i	a8, sp, 92	# %sfp,
# @OPUS@\upstream\silk\PLC.c:338:             down_scale_Q30 = silk_LSHIFT( down_scale_Q30, LOG2_INV_LPC_GAIN_HIGH_THRES );
	slli	a2, a2, 3	# down_scale_Q30, invGain_Q30,
# @OPUS@\upstream\silk\PLC.c:340:             rand_Gain_Q15 = silk_RSHIFT( silk_SMULWB( down_scale_Q30, rand_Gain_Q15 ), 14 );
	extui	a3, a2, 0, 16	# tmp973, down_scale_Q30,
	mull	a3, a3, a8	# tmp974, tmp973,
	srai	a2, a2, 16	# tmp976, down_scale_Q30,
	mull	a2, a2, a8	# tmp977, tmp976,
	srai	a3, a3, 16	# tmp975, tmp974,
	l32i	a11, sp, 64	# %sfp,
	add.n	a2, a3, a2	# _116, tmp975, tmp977
# @OPUS@\upstream\silk\PLC.c:321:         rand_scale_Q14 = 1 << 14;
	l32r	a14, .LC3	#,
# @OPUS@\upstream\silk\PLC.c:340:             rand_Gain_Q15 = silk_RSHIFT( silk_SMULWB( down_scale_Q30, rand_Gain_Q15 ), 14 );
	srai	a2, a2, 14	#, _116,
	l32i.n	a13, a11, 40	# psDec_8(D)->LPC_order, _81
# @OPUS@\upstream\silk\PLC.c:321:         rand_scale_Q14 = 1 << 14;
	s32i	a14, sp, 88	# %sfp,
# @OPUS@\upstream\silk\PLC.c:340:             rand_Gain_Q15 = silk_RSHIFT( silk_SMULWB( down_scale_Q30, rand_Gain_Q15 ), 14 );
	s32i	a2, sp, 92	# %sfp,
.L18:
# @OPUS@\upstream\silk\PLC.c:345:     lag          = silk_RSHIFT_ROUND( psPLC->pitchL_Q8, 8 );
	l32i	a2, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8
# @OPUS@\upstream\silk\PLC.c:346:     sLTP_buf_idx = psDec->ltp_mem_length;
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:345:     lag          = silk_RSHIFT_ROUND( psPLC->pitchL_Q8, 8 );
	srai	a2, a2, 7	# tmp981, MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8,
	addi.n	a2, a2, 1	# tmp983, tmp981,
# @OPUS@\upstream\silk\PLC.c:345:     lag          = silk_RSHIFT_ROUND( psPLC->pitchL_Q8, 8 );
	srai	a2, a2, 1	#, tmp983,
# @OPUS@\upstream\silk\PLC.c:346:     sLTP_buf_idx = psDec->ltp_mem_length;
	l32i.n	a9, a8, 36	# psDec_8(D)->ltp_mem_length, sLTP_buf_idx
# @OPUS@\upstream\silk\PLC.c:345:     lag          = silk_RSHIFT_ROUND( psPLC->pitchL_Q8, 8 );
	s32i	a2, sp, 68	# %sfp,
# @OPUS@\upstream\silk\PLC.c:349:     idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	l32i	a11, sp, 68	# %sfp,
	addi	a2, a9, -2	# tmp985, sLTP_buf_idx,
	sub	a2, a2, a11	# tmp986, tmp985,
	sub	a2, a2, a13	#, tmp986, _81
# @OPUS@\upstream\silk\PLC.c:351:     silk_LPC_analysis_filter( &sLTP[ idx ], &psDec->outBuf[ idx ], A_Q12, psDec->ltp_mem_length - idx, psDec->LPC_order, arch );
	addi.n	a5, a11, 2	# tmp987,,
# @OPUS@\upstream\silk\PLC.c:349:     idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	s32i	a2, sp, 80	# %sfp,
# @OPUS@\upstream\silk\PLC.c:351:     silk_LPC_analysis_filter( &sLTP[ idx ], &psDec->outBuf[ idx ], A_Q12, psDec->ltp_mem_length - idx, psDec->LPC_order, arch );
	mov.n	a6, a13	#, _81
# @OPUS@\upstream\silk\PLC.c:351:     silk_LPC_analysis_filter( &sLTP[ idx ], &psDec->outBuf[ idx ], A_Q12, psDec->ltp_mem_length - idx, psDec->LPC_order, arch );
	slli	a2, a2, 1	# _129,,
# @OPUS@\upstream\silk\PLC.c:351:     silk_LPC_analysis_filter( &sLTP[ idx ], &psDec->outBuf[ idx ], A_Q12, psDec->ltp_mem_length - idx, psDec->LPC_order, arch );
	add.n	a5, a5, a13	#, tmp987, _81
	l32i	a14, sp, 84	# %sfp,
	l32i	a13, sp, 76	# %sfp,
# @OPUS@\upstream\silk\PLC.c:344:     rand_seed    = psPLC->rand_seed;
	l32i	a8, a12, 132	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].rand_seed,
# @OPUS@\upstream\silk\PLC.c:351:     silk_LPC_analysis_filter( &sLTP[ idx ], &psDec->outBuf[ idx ], A_Q12, psDec->ltp_mem_length - idx, psDec->LPC_order, arch );
	addi	a3, a2, 72	# tmp989, _129,
# @OPUS@\upstream\silk\PLC.c:351:     silk_LPC_analysis_filter( &sLTP[ idx ], &psDec->outBuf[ idx ], A_Q12, psDec->ltp_mem_length - idx, psDec->LPC_order, arch );
	l32i	a7, sp, 104	# %sfp,
	add.n	a3, a13, a3	#,, tmp989
	mov.n	a4, sp	#,
	add.n	a2, a14, a2	#,, _129
	s32i	a9, sp, 192	#,
# @OPUS@\upstream\silk\PLC.c:344:     rand_seed    = psPLC->rand_seed;
	s32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\silk\PLC.c:351:     silk_LPC_analysis_filter( &sLTP[ idx ], &psDec->outBuf[ idx ], A_Q12, psDec->ltp_mem_length - idx, psDec->LPC_order, arch );
	call0	silk_LPC_analysis_filter		#
# @OPUS@\upstream\silk\PLC.c:353:     inv_gain_Q30 = silk_INVERSE32_varQ( psPLC->prevGain_Q16[ 1 ], 46 );
	l32i	a13, a12, 156	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevGain_Q16, _133
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	l32i	a9, sp, 192	#,
	beqz.n	a13, .L76	# _133,
# @OPUS@\upstream\silk\Inlines.h:155:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a15, a13	# tmp993, _133
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a15, a15	# iftmp$76_550, tmp993
	movi.n	a14, 0x10	# tmp994,
	addi.n	a2, a15, -1	# _1586, iftmp$76_550,
	sub	a14, a14, a15	# _1588, tmp994, iftmp$76_550
	j	.L23		#
.L76:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a14, -0x10	# _1588,
	movi.n	a2, 0x1f	# _1586,
	movi.n	a15, 0x20	# iftmp$76_550,
.L23:
# @OPUS@\upstream\silk\Inlines.h:156:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                */
	ssl	a2	# _1586
	sll	a13, a13	# b32_nrm, _133
# @OPUS@\upstream\silk\Inlines.h:159:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm    */
	srai	a6, a13, 16	# _556, b32_nrm,
# @OPUS@\upstream\silk\Inlines.h:159:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm    */
	l32r	a2, .LC17	#,
	mov.n	a3, a6	#, _556
	s32i	a6, sp, 188	#,
	s32i	a9, sp, 192	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	slli	a3, a2, 16	# tmp998, tmp997,
	l32i	a6, sp, 188	#,
	srai	a5, a3, 16	# _562, tmp998,
	extui	a13, a13, 0, 16	# tmp1002, b32_nrm,
	mull	a6, a6, a5	# tmp999, _556, _562
	mull	a13, a13, a5	# tmp1003, tmp1002, _562
	l32r	a4, .LC18	#, tmp1001
	srai	a13, a13, 16	# tmp1004, tmp1003,
	sub	a4, a4, a6	# tmp1000, tmp1001, tmp999
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	srai	a2, a2, 15	# tmp1006, tmp997,
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	sub	a4, a4, a13	# tmp1005, tmp1000, tmp1004
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	addi.n	a2, a2, 1	# tmp1007, tmp1006,
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	slli	a4, a4, 3	# err_Q32, tmp1005,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	srai	a2, a2, 1	# tmp1008, tmp1007,
	mull	a2, a2, a4	# tmp1009, tmp1008, err_Q32
	srai	a7, a4, 16	# tmp1012, err_Q32,
	extui	a4, a4, 0, 16	# tmp1014, err_Q32,
	mull	a7, a7, a5	# tmp1013, tmp1012, _562
	mull	a4, a4, a5	# tmp1015, tmp1014, _562
	add.n	a3, a2, a3	# tmp1011, tmp1009, tmp998
	add.n	a7, a3, a7	# _762, tmp1011, tmp1013
	srai	a4, a4, 16	# tmp1016, tmp1015,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	add.n	a7, a4, a7	# result, tmp1016, _762
# @OPUS@\upstream\silk\Inlines.h:176:             return silk_RSHIFT(result, lshift);
	ssr	a14	# _1588
	sra	a2, a7	# _598, result
# @OPUS@\upstream\silk\Inlines.h:172:     if( lshift <= 0 ) {
	l32i	a9, sp, 192	#,
	bgei	a14, 1, .L31	# _1588,,
# @OPUS@\upstream\silk\Inlines.h:173:         return silk_LSHIFT_SAT32(result, -lshift);
	l32r	a2, .LC4	#, tmp1017
	l32r	a3, .LC6	#, tmp1018
	addi	a15, a15, -16	# _586, iftmp$76_550,
	ssr	a15	# _586
	sra	a2, a2	# _587, tmp1017
	ssr	a15	# _586
	sra	a3, a3	# _588, tmp1018
	bge	a3, a2, .L25	# _588, _587,
	bge	a2, a7, .L26	# _587, result,
	j	.L100		#
.L26:
	bge	a7, a3, .L27	# iftmp$74_589, _588,
	j	.L101		#
.L25:
	bge	a3, a7, .L29	# _588, result,
.L101:
	mov.n	a7, a3	# iftmp$74_589, _588
	j	.L27		#
.L29:
	bge	a7, a2, .L27	# iftmp$74_589, _587,
.L100:
	mov.n	a7, a2	# iftmp$74_589, _587
.L27:
	ssl	a15	# _586
	sll	a2, a7	# _598, iftmp$74_589
.L31:
# @OPUS@\upstream\silk\PLC.c:354:     inv_gain_Q30 = silk_min( inv_gain_Q30, silk_int32_MAX >> 1 );
	l32r	a3, .LC19	#, tmp1023
	mov.n	a15, a2	# inv_gain_Q30, _598
	bge	a3, a2, .L32	# tmp1023, inv_gain_Q30,
	mov.n	a15, a3	# inv_gain_Q30, tmp1023
.L32:
# @OPUS@\upstream\silk\PLC.c:355:     for( i = idx + psDec->LPC_order; i < psDec->ltp_mem_length; i++ ) {
	l32i	a11, sp, 64	# %sfp,
	l32i	a13, sp, 80	# %sfp,
	l32i.n	a3, a11, 40	# psDec_8(D)->LPC_order, psDec_8(D)->LPC_order
# @OPUS@\upstream\silk\PLC.c:355:     for( i = idx + psDec->LPC_order; i < psDec->ltp_mem_length; i++ ) {
	l32i.n	a2, a11, 36	# psDec_8(D)->ltp_mem_length, _153
# @OPUS@\upstream\silk\PLC.c:355:     for( i = idx + psDec->LPC_order; i < psDec->ltp_mem_length; i++ ) {
	add.n	a7, a13, a3	# i,, psDec_8(D)->LPC_order
# @OPUS@\upstream\silk\PLC.c:355:     for( i = idx + psDec->LPC_order; i < psDec->ltp_mem_length; i++ ) {
	bge	a7, a2, .L33	# i, _153,
	l32i	a8, sp, 96	# %sfp,
	l32i	a14, sp, 84	# %sfp,
	slli	a5, a7, 1	# tmp1027, i,
	slli	a3, a7, 2	# tmp1028, i,
# @OPUS@\upstream\silk\PLC.c:356:         PLC_STORE_WORD(sLTP_Q14, i, silk_SMULWB(inv_gain_Q30, sLTP[i]));
	srai	a4, a15, 16	# _138, inv_gain_Q30,
	add.n	a3, a8, a3	# ivtmp$123,, tmp1028
	extui	a15, a15, 0, 16	# _1615, inv_gain_Q30,
	add.n	a5, a14, a5	# ivtmp$122,, tmp1027
	mov.n	a8, a11	# tmp1809,
.L34:
	l16si	a6, a5, 0	# MEM[base: _1348, offset: 0B], _144
# @OPUS@\upstream\silk\PLC.c:355:     for( i = idx + psDec->LPC_order; i < psDec->ltp_mem_length; i++ ) {
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\silk\PLC.c:356:         PLC_STORE_WORD(sLTP_Q14, i, silk_SMULWB(inv_gain_Q30, sLTP[i]));
	mull	a2, a6, a15	# tmp1031, _144, _1615
	mull	a6, a4, a6	# tmp1033, _138, _144
	srai	a2, a2, 16	# tmp1032, tmp1031,
	add.n	a2, a2, a6	# tmp1034, tmp1032, tmp1033
	s32i.n	a2, a3, 0	# MEM[base: _1347, offset: 0B], tmp1034
# @OPUS@\upstream\silk\PLC.c:355:     for( i = idx + psDec->LPC_order; i < psDec->ltp_mem_length; i++ ) {
	l32i.n	a2, a8, 36	# psDec_8(D)->ltp_mem_length, _153
	addi.n	a5, a5, 2	# ivtmp$122, ivtmp$122,
	addi.n	a3, a3, 4	# ivtmp$123, ivtmp$123,
# @OPUS@\upstream\silk\PLC.c:355:     for( i = idx + psDec->LPC_order; i < psDec->ltp_mem_length; i++ ) {
	blt	a7, a2, .L34	# i, _153,
.L33:
# @OPUS@\upstream\silk\PLC.c:362:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i	a11, sp, 64	# %sfp,
	l32i.n	a13, a11, 24	# psDec_8(D)->nb_subfr, prephitmp_1703
# @OPUS@\upstream\silk\PLC.c:362:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	blti	a13, 1, .L35	# prephitmp_1703,,
	l32i	a14, sp, 92	# %sfp,
	mov.n	a3, a11	#,
	slli	a2, a14, 16	# tmp1037,,
	l32i.n	a14, a3, 32	# psDec_8(D)->subfr_length, prephitmp_1755
	l16si	a11, a12, 90	# MEM[(opus_int16 *)psDec_8(D) + 2906B], _803
	l16si	a15, a12, 92	# MEM[(opus_int16 *)psDec_8(D) + 2908B], _815
	srai	a2, a2, 16	#, tmp1037,
	l16si	a6, a12, 88	# MEM[(opus_int16 *)psDec_8(D) + 2904B], _791
# @OPUS@\upstream\silk\PLC.c:362:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	mov.n	a3, a14	# prephitmp_1755, prephitmp_1755
	s32i	a2, sp, 128	# %sfp,
	movi.n	a4, 0	#,
	l16si	a8, a12, 84	# MEM[(opus_int16 *)psDec_8(D) + 2900B], _767
	l16si	a7, a12, 86	# MEM[(opus_int16 *)psDec_8(D) + 2902B], _779
	l32i	a2, sp, 68	# %sfp, lag
	mov.n	a14, a9	# sLTP_buf_idx, sLTP_buf_idx
	s32i	a4, sp, 84	# %sfp,
	mov.n	a9, a11	# _803, _803
	mov.n	a10, a6	# _791, _791
	mov.n	a11, a15	# _815, _815
	mov.n	a15, a3	# prephitmp_1755, prephitmp_1755
.L40:
# @OPUS@\upstream\silk\PLC.c:364:         pred_lag_ptr = &sLTP_Q14[ sLTP_buf_idx - lag + LTP_ORDER / 2 ];
	sub	a2, a14, a2	# tmp1054, sLTP_buf_idx, lag
# @OPUS@\upstream\silk\PLC.c:364:         pred_lag_ptr = &sLTP_Q14[ sLTP_buf_idx - lag + LTP_ORDER / 2 ];
	addi.n	a2, a2, 2	# tmp1055, tmp1054,
	slli	a4, a2, 2	# _159, tmp1055,
# @OPUS@\upstream\silk\PLC.c:365:         for( i = 0; i < psDec->subfr_length; i++ ) {
	blti	a15, 1, .L36	# prephitmp_1755,,
	l32i	a13, sp, 96	# %sfp,
	slli	a2, a14, 2	# tmp1056, sLTP_buf_idx,
	add.n	a2, a13, a2	#,, tmp1056
	addi	a4, a4, -16	# tmp1057, _159,
	s32i	a2, sp, 80	# %sfp,
	addi.n	a14, a14, 1	#, sLTP_buf_idx,
# @OPUS@\upstream\silk\PLC.c:365:         for( i = 0; i < psDec->subfr_length; i++ ) {
	movi.n	a2, 0	#,
	add.n	a4, a13, a4	# ivtmp$115,, tmp1057
	s32i	a2, sp, 68	# %sfp,
	s32i	a14, sp, 120	# %sfp,
.L38:
# @OPUS@\upstream\silk\PLC.c:377:             rand_seed = silk_RAND( rand_seed );
	l32i	a13, sp, 104	# %sfp,
	l32r	a14, .LC20	#,
	l32r	a5, .LC21	#,
	mull	a3, a13, a14	# tmp1058,,
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	l32i.n	a13, a4, 8	# MEM[base: _1618, offset: 8B],
# @OPUS@\upstream\silk\PLC.c:377:             rand_seed = silk_RAND( rand_seed );
	add.n	a3, a3, a5	#, tmp1058,
	s32i	a3, sp, 104	# %sfp,
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	s32i	a13, sp, 92	# %sfp,
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	l32i.n	a14, a4, 4	# MEM[base: _1618, offset: 4B],
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	l32i.n	a5, a4, 0	# MEM[base: _1618, offset: 0B],
# @OPUS@\upstream\silk\PLC.c:380:             const opus_int32 excitation = yoradio_opus_load32(&rand_ptr[idx]);
	l32i	a13, sp, 124	# %sfp,
# @OPUS@\upstream\silk\PLC.c:378:             idx = silk_RSHIFT( rand_seed, 25 ) & RAND_BUF_MASK;
	extui	a3, a3, 25, 7	# tmp1062,,
# @OPUS@\upstream\silk\PLC.c:380:             const opus_int32 excitation = yoradio_opus_load32(&rand_ptr[idx]);
	slli	a3, a3, 2	# tmp1063, tmp1062,
# @OPUS@\upstream\silk\PLC.c:369:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr,  0), B_Q14[ 0 ] );
	l32i.n	a2, a4, 16	# MEM[base: _1618, offset: 16B], _162
# @OPUS@\upstream\silk\PLC.c:370:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -1), B_Q14[ 1 ] );
	l32i.n	a6, a4, 12	# MEM[base: _1618, offset: 12B], _172
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	s32i	a14, sp, 108	# %sfp,
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	s32i	a5, sp, 112	# %sfp,
# @OPUS@\upstream\silk\PLC.c:380:             const opus_int32 excitation = yoradio_opus_load32(&rand_ptr[idx]);
	add.n	a3, a13, a3	# tmp1064,, tmp1063
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1064
# 0 "" 2
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
#NO_APP
	l32i	a14, sp, 88	# %sfp,
	srai	a5, a3, 16	# tmp1065, value,
	mull	a15, a5, a14	# tmp1066, tmp1065,
# @OPUS@\upstream\silk\PLC.c:369:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr,  0), B_Q14[ 0 ] );
	srai	a5, a2, 16	# tmp1068, _162,
	mull	a14, a5, a8	# tmp1069, tmp1068, _767
# @OPUS@\upstream\silk\PLC.c:370:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -1), B_Q14[ 1 ] );
	srai	a5, a6, 16	# tmp1071, _172,
	mull	a5, a5, a7	#, tmp1071, _779
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	l32i	a13, sp, 92	# %sfp,
# @OPUS@\upstream\silk\PLC.c:370:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -1), B_Q14[ 1 ] );
	s32i	a5, sp, 132	# %sfp,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	addi.n	a5, a15, 2	# tmp1067, tmp1066,
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	srai	a15, a13, 16	# tmp1074,,
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	l32i	a13, sp, 108	# %sfp,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	add.n	a5, a5, a14	# tmp1070, tmp1067, tmp1069
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	srai	a14, a13, 16	# tmp1077,,
	mull	a14, a14, a9	#, tmp1077, _803
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	mull	a15, a15, a10	# tmp1075, tmp1074, _791
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	s32i	a14, sp, 136	# %sfp,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	l32i	a14, sp, 132	# %sfp,
# @OPUS@\upstream\silk\PLC.c:369:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr,  0), B_Q14[ 0 ] );
	extui	a2, a2, 0, 16	# tmp1087, _162,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	add.n	a5, a5, a14	# tmp1073, tmp1070,
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	l32i	a14, sp, 112	# %sfp,
# @OPUS@\upstream\silk\PLC.c:369:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr,  0), B_Q14[ 0 ] );
	mull	a2, a2, a8	# tmp1088, tmp1087, _767
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	srai	a13, a14, 16	# tmp1080,,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	l32i	a14, sp, 88	# %sfp,
	l32i	a8, sp, 136	# %sfp,
	extui	a3, a3, 0, 16	# tmp1083, value,
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	mull	a13, a13, a11	# tmp1081, tmp1080, _815
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	add.n	a5, a5, a15	# tmp1076, tmp1073, tmp1075
	mull	a3, a3, a14	# tmp1084, tmp1083,
	add.n	a5, a5, a8	# tmp1079, tmp1076,
	add.n	a5, a5, a13	# tmp1082, tmp1079, tmp1081
	srai	a3, a3, 16	# tmp1085, tmp1084,
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	l32i	a13, sp, 92	# %sfp,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	add.n	a5, a5, a3	# tmp1086, tmp1082, tmp1085
# @OPUS@\upstream\silk\PLC.c:369:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr,  0), B_Q14[ 0 ] );
	srai	a2, a2, 16	# tmp1089, tmp1088,
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	l32i	a14, sp, 108	# %sfp,
# @OPUS@\upstream\silk\PLC.c:370:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -1), B_Q14[ 1 ] );
	extui	a6, a6, 0, 16	# tmp1091, _172,
	mull	a6, a6, a7	# tmp1092, tmp1091, _779
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	add.n	a5, a5, a2	# tmp1090, tmp1086, tmp1089
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	extui	a7, a13, 0, 16	# tmp1095,,
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	l32i	a2, sp, 112	# %sfp,
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	extui	a3, a14, 0, 16	# tmp1099,,
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	mull	a10, a7, a10	# tmp1096, tmp1095, _791
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	mull	a9, a3, a9	# tmp1100, tmp1099, _803
# @OPUS@\upstream\silk\PLC.c:370:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -1), B_Q14[ 1 ] );
	srai	a6, a6, 16	# tmp1093, tmp1092,
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	extui	a8, a2, 0, 16	# tmp1103,,
	mull	a8, a8, a11	# tmp1104, tmp1103, _815
# @OPUS@\upstream\silk\PLC.c:371:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -2), B_Q14[ 2 ] );
	srai	a10, a10, 16	# tmp1097, tmp1096,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	add.n	a11, a5, a6	# tmp1094, tmp1090, tmp1093
	add.n	a11, a11, a10	# tmp1098, tmp1094, tmp1097
# @OPUS@\upstream\silk\PLC.c:372:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -3), B_Q14[ 3 ] );
	srai	a9, a9, 16	# tmp1101, tmp1100,
# @OPUS@\upstream\silk\PLC.c:373:             LTP_pred_Q12 = silk_SMLAWB( LTP_pred_Q12, PLC_WORD(pred_lag_ptr, -4), B_Q14[ 4 ] );
	srai	a8, a8, 16	# tmp1105, tmp1104,
# @OPUS@\upstream\silk\PLC.c:381:             PLC_STORE_WORD(sLTP_Q14, sLTP_buf_idx, silk_LSHIFT32(silk_SMLAWB(LTP_pred_Q12, excitation, rand_scale_Q14), 2));
	add.n	a11, a11, a9	# tmp1102, tmp1098, tmp1101
	l32i	a3, sp, 80	# %sfp,
	add.n	a11, a11, a8	# tmp1106, tmp1102, tmp1105
	slli	a11, a11, 2	# tmp1107, tmp1106,
	s32i.n	a11, a3, 0	# MEM[base: _1619, offset: 0B], tmp1107
	l32i	a13, sp, 68	# %sfp,
# @OPUS@\upstream\silk\PLC.c:365:         for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i	a8, sp, 64	# %sfp,
	l32i	a11, sp, 120	# %sfp,
	addi.n	a3, a3, 4	#,,
	add.n	a14, a11, a13	# sLTP_buf_idx,,
	l32i.n	a15, a8, 32	# psDec_8(D)->subfr_length, prephitmp_1755
# @OPUS@\upstream\silk\PLC.c:365:         for( i = 0; i < psDec->subfr_length; i++ ) {
	addi.n	a13, a13, 1	#,,
	s32i	a13, sp, 68	# %sfp,
	s32i	a3, sp, 80	# %sfp,
	addi.n	a4, a4, 4	# ivtmp$115, ivtmp$115,
# @OPUS@\upstream\silk\PLC.c:365:         for( i = 0; i < psDec->subfr_length; i++ ) {
	blt	a13, a15, .L37	#, prephitmp_1755,
	l32i.n	a13, a8, 24	# psDec_8(D)->nb_subfr, prephitmp_1703
	l16si	a7, a12, 86	# MEM[(opus_int16 *)psDec_8(D) + 2902B], _779
	l16si	a8, a12, 84	# MEM[(opus_int16 *)psDec_8(D) + 2900B], _767
	l16si	a10, a12, 88	# MEM[(opus_int16 *)psDec_8(D) + 2904B], _791
	l16si	a9, a12, 90	# MEM[(opus_int16 *)psDec_8(D) + 2906B], _803
	l16si	a11, a12, 92	# MEM[(opus_int16 *)psDec_8(D) + 2908B], _815
	j	.L36		#
.L37:
	l16si	a8, a12, 84	# MEM[(opus_int16 *)psDec_8(D) + 2900B], _767
	l16si	a7, a12, 86	# MEM[(opus_int16 *)psDec_8(D) + 2902B], _779
	l16si	a10, a12, 88	# MEM[(opus_int16 *)psDec_8(D) + 2904B], _791
	l16si	a9, a12, 90	# MEM[(opus_int16 *)psDec_8(D) + 2906B], _803
	l16si	a11, a12, 92	# MEM[(opus_int16 *)psDec_8(D) + 2908B], _815
	j	.L38		#
.L36:
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	l32i	a2, sp, 72	# %sfp,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	l32i	a3, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8,
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	mull	a8, a2, a8	#,, _767
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	extui	a5, a3, 0, 16	# tmp1164,,
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	s32i	a8, sp, 68	# %sfp,
	l32i	a8, sp, 72	# %sfp,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	srai	a4, a3, 16	# tmp1173,,
	slli	a3, a5, 6	# tmp1166, tmp1164,
	add.n	a3, a3, a5	# tmp1167, tmp1166, tmp1164
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	mull	a7, a8, a7	# tmp1145,, _779
	mull	a10, a8, a10	# tmp1149,, _791
	mull	a9, a8, a9	# tmp1153,, _803
	mull	a11, a8, a11	# tmp1157,, _815
# @OPUS@\upstream\silk\PLC.c:397:         psPLC->pitchL_Q8 = silk_min_32( psPLC->pitchL_Q8, silk_LSHIFT( silk_SMULBB( MAX_PITCH_LAG_MS, psDec->fs_kHz ), 8 ) );
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	slli	a3, a3, 1	# tmp1168, tmp1167,
# @OPUS@\upstream\silk\PLC.c:397:         psPLC->pitchL_Q8 = silk_min_32( psPLC->pitchL_Q8, silk_LSHIFT( silk_SMULBB( MAX_PITCH_LAG_MS, psDec->fs_kHz ), 8 ) );
	l16si	a6, a8, 16	# psDec_8(D)->fs_kHz, tmp1185
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	add.n	a3, a3, a5	# tmp1169, tmp1168, tmp1164
# @OPUS@\upstream\silk\PLC.c:393:         rand_scale_Q14 = silk_RSHIFT( silk_SMULBB( rand_scale_Q14, rand_Gain_Q15 ), 15 );
	l32i	a8, sp, 88	# %sfp,
	l32i	a5, sp, 128	# %sfp,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	slli	a2, a4, 6	# tmp1175, tmp1173,
# @OPUS@\upstream\silk\PLC.c:393:         rand_scale_Q14 = silk_RSHIFT( silk_SMULBB( rand_scale_Q14, rand_Gain_Q15 ), 15 );
	mull	a5, a5, a8	#,,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	add.n	a2, a2, a4	# tmp1176, tmp1175, tmp1173
	slli	a2, a2, 1	# tmp1177, tmp1176,
	add.n	a2, a2, a4	# tmp1178, tmp1177, tmp1173
# @OPUS@\upstream\silk\PLC.c:393:         rand_scale_Q14 = silk_RSHIFT( silk_SMULBB( rand_scale_Q14, rand_Gain_Q15 ), 15 );
	s32i	a5, sp, 88	# %sfp,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	slli	a4, a3, 2	#, tmp1169,
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	l32i	a5, sp, 68	# %sfp,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	s32i	a4, sp, 80	# %sfp,
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	slli	a8, a5, 1	# tmp1143,,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	slli	a4, a2, 2	# tmp1179, tmp1178,
	l32i	a5, sp, 80	# %sfp,
	add.n	a2, a2, a4	# tmp1180, tmp1178, tmp1179
# @OPUS@\upstream\silk\PLC.c:397:         psPLC->pitchL_Q8 = silk_min_32( psPLC->pitchL_Q8, silk_LSHIFT( silk_SMULBB( MAX_PITCH_LAG_MS, psDec->fs_kHz ), 8 ) );
	slli	a4, a6, 3	# tmp1188, tmp1185,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	add.n	a3, a3, a5	# tmp1171, tmp1169,
# @OPUS@\upstream\silk\PLC.c:397:         psPLC->pitchL_Q8 = silk_min_32( psPLC->pitchL_Q8, silk_LSHIFT( silk_SMULBB( MAX_PITCH_LAG_MS, psDec->fs_kHz ), 8 ) );
	add.n	a4, a4, a6	# tmp1189, tmp1188, tmp1185
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	l32i	a5, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8,
# @OPUS@\upstream\silk\PLC.c:393:         rand_scale_Q14 = silk_RSHIFT( silk_SMULBB( rand_scale_Q14, rand_Gain_Q15 ), 15 );
	l32i	a6, sp, 88	# %sfp,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	add.n	a2, a2, a5	# tmp1181, tmp1180,
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	slli	a7, a7, 1	# tmp1147, tmp1145,
	slli	a10, a10, 1	# tmp1151, tmp1149,
	slli	a9, a9, 1	# tmp1155, tmp1153,
	slli	a11, a11, 1	# tmp1159, tmp1157,
# @OPUS@\upstream\silk\PLC.c:393:         rand_scale_Q14 = silk_RSHIFT( silk_SMULBB( rand_scale_Q14, rand_Gain_Q15 ), 15 );
	slli	a5, a6, 1	# tmp1162,,
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	srai	a8, a8, 16	# _767, tmp1143,
	srai	a7, a7, 16	# _779, tmp1147,
	srai	a10, a10, 16	# _791, tmp1151,
	srai	a9, a9, 16	# _803, tmp1155,
	srai	a11, a11, 16	# _815, tmp1159,
# @OPUS@\upstream\silk\PLC.c:396:         psPLC->pitchL_Q8 = silk_SMLAWB( psPLC->pitchL_Q8, psPLC->pitchL_Q8, PITCH_DRIFT_FAC_Q16 );
	srai	a3, a3, 16	# tmp1172, tmp1171,
# @OPUS@\upstream\silk\PLC.c:393:         rand_scale_Q14 = silk_RSHIFT( silk_SMULBB( rand_scale_Q14, rand_Gain_Q15 ), 15 );
	srai	a5, a5, 16	#, tmp1162,
# @OPUS@\upstream\silk\PLC.c:390:             B_Q14[ j ] = silk_RSHIFT( silk_SMULBB( harm_Gain_Q15, B_Q14[ j ] ), 15 );
	s16i	a8, a12, 84	# MEM[(opus_int16 *)psDec_8(D) + 2900B], _767
	s16i	a7, a12, 86	# MEM[(opus_int16 *)psDec_8(D) + 2902B], _779
	s16i	a10, a12, 88	# MEM[(opus_int16 *)psDec_8(D) + 2904B], _791
	s16i	a9, a12, 90	# MEM[(opus_int16 *)psDec_8(D) + 2906B], _803
	s16i	a11, a12, 92	# MEM[(opus_int16 *)psDec_8(D) + 2908B], _815
# @OPUS@\upstream\silk\PLC.c:397:         psPLC->pitchL_Q8 = silk_min_32( psPLC->pitchL_Q8, silk_LSHIFT( silk_SMULBB( MAX_PITCH_LAG_MS, psDec->fs_kHz ), 8 ) );
	slli	a4, a4, 9	# tmp1191, tmp1189,
# @OPUS@\upstream\silk\SigProc_FIX.h:556:     return (((a) < (b)) ? (a) : (b));
	add.n	a3, a3, a2	# _276, tmp1172, tmp1181
# @OPUS@\upstream\silk\PLC.c:393:         rand_scale_Q14 = silk_RSHIFT( silk_SMULBB( rand_scale_Q14, rand_Gain_Q15 ), 15 );
	s32i	a5, sp, 88	# %sfp,
# @OPUS@\upstream\silk\SigProc_FIX.h:556:     return (((a) < (b)) ? (a) : (b));
	bge	a4, a3, .L39	# tmp1191, _276,
	mov.n	a3, a4	# _276, tmp1191
.L39:
# @OPUS@\upstream\silk\PLC.c:398:         lag = silk_RSHIFT_ROUND( psPLC->pitchL_Q8, 8 );
	srai	a2, a3, 7	# tmp1193, _276,
# @OPUS@\upstream\silk\PLC.c:397:         psPLC->pitchL_Q8 = silk_min_32( psPLC->pitchL_Q8, silk_LSHIFT( silk_SMULBB( MAX_PITCH_LAG_MS, psDec->fs_kHz ), 8 ) );
	s32i	a3, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8, _276
# @OPUS@\upstream\silk\PLC.c:362:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i	a3, sp, 84	# %sfp,
# @OPUS@\upstream\silk\PLC.c:398:         lag = silk_RSHIFT_ROUND( psPLC->pitchL_Q8, 8 );
	addi.n	a2, a2, 1	# tmp1194, tmp1193,
# @OPUS@\upstream\silk\PLC.c:362:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	addi.n	a3, a3, 1	#,,
	s32i	a3, sp, 84	# %sfp,
# @OPUS@\upstream\silk\PLC.c:398:         lag = silk_RSHIFT_ROUND( psPLC->pitchL_Q8, 8 );
	srai	a2, a2, 1	# lag, tmp1194,
# @OPUS@\upstream\silk\PLC.c:362:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	blt	a3, a13, .L40	#, prephitmp_1703,
	l32i	a8, sp, 64	# %sfp,
	s32i	a2, sp, 68	# %sfp, lag
	l32i.n	a2, a8, 36	# psDec_8(D)->ltp_mem_length, _153
.L35:
# @OPUS@\upstream\silk\PLC.c:407:     PLC_COPY_WORDS(sLPC_Q14_ptr, psDec->sLPC_Q14_buf, MAX_LPC_ORDER);
	l32i	a13, sp, 76	# %sfp,
# @OPUS@\upstream\silk\PLC.c:404:     sLPC_Q14_ptr = &sLTP_Q14[ psDec->ltp_mem_length - MAX_LPC_ORDER ];
	l32i	a11, sp, 96	# %sfp,
# @OPUS@\upstream\silk\PLC.c:404:     sLPC_Q14_ptr = &sLTP_Q14[ psDec->ltp_mem_length - MAX_LPC_ORDER ];
	slli	a2, a2, 2	# tmp1196, _153,
# @OPUS@\upstream\silk\PLC.c:407:     PLC_COPY_WORDS(sLPC_Q14_ptr, psDec->sLPC_Q14_buf, MAX_LPC_ORDER);
	addi.n	a13, a13, 8	#,,
# @OPUS@\upstream\silk\PLC.c:404:     sLPC_Q14_ptr = &sLTP_Q14[ psDec->ltp_mem_length - MAX_LPC_ORDER ];
	addi	a2, a2, -64	# tmp1198, tmp1196,
# @OPUS@\upstream\silk\PLC.c:404:     sLPC_Q14_ptr = &sLTP_Q14[ psDec->ltp_mem_length - MAX_LPC_ORDER ];
	add.n	a2, a11, a2	#,, tmp1198
# @OPUS@\upstream\silk\PLC.c:407:     PLC_COPY_WORDS(sLPC_Q14_ptr, psDec->sLPC_Q14_buf, MAX_LPC_ORDER);
	mov.n	a3, a13	#,
	movi.n	a4, 0x40	#,
# @OPUS@\upstream\silk\PLC.c:404:     sLPC_Q14_ptr = &sLTP_Q14[ psDec->ltp_mem_length - MAX_LPC_ORDER ];
	s32i	a2, sp, 168	# %sfp,
# @OPUS@\upstream\silk\PLC.c:407:     PLC_COPY_WORDS(sLPC_Q14_ptr, psDec->sLPC_Q14_buf, MAX_LPC_ORDER);
	s32i	a13, sp, 172	# %sfp,
	call0	memcpy		#
# @OPUS@\upstream\silk\PLC.c:410:     for( i = 0; i < psDec->frame_length; i++ ) {
	l32i	a14, sp, 64	# %sfp,
	l32i.n	a3, a14, 28	# psDec_8(D)->frame_length, _488
# @OPUS@\upstream\silk\PLC.c:410:     for( i = 0; i < psDec->frame_length; i++ ) {
	blti	a3, 1, .L41	# _488,,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	l16si	a2, sp, 44	# prevGain_Q10,
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	l16si	a5, sp, 0	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	s32i	a2, sp, 76	# %sfp,
	l32i	a4, sp, 76	# %sfp,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	l16si	a6, sp, 2	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	l16si	a7, sp, 4	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	l16si	a8, sp, 6	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	l16si	a11, sp, 8	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	l16si	a13, sp, 10	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	l32i.n	a3, sp, 44	# prevGain_Q10, _467
	slli	a2, a2, 16	# tmp1240,,
	sub	a2, a2, a4	# tmp1241, tmp1240,
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	s32i	a5, sp, 84	# %sfp,
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	l16si	a4, sp, 14	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	l16si	a5, sp, 16	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	s32i	a6, sp, 92	# %sfp,
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	s32i	a7, sp, 108	# %sfp,
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	l16si	a6, sp, 18	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	s32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	s32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	s32i	a13, sp, 124	# %sfp,
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	l16si	a14, sp, 12	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	l16si	a7, sp, 20	# A_Q12,
	l16si	a8, sp, 22	# A_Q12,
	l16si	a11, sp, 24	# A_Q12,
	l16si	a13, sp, 26	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	srai	a3, a3, 15	# tmp1225, _467,
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	s32i	a4, sp, 132	# %sfp,
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	s32i	a5, sp, 136	# %sfp,
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	s32i	a6, sp, 140	# %sfp,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	addi.n	a3, a3, 1	# tmp1226, tmp1225,
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	s32i	a14, sp, 128	# %sfp,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	s32i	a7, sp, 164	# %sfp,
	s32i	a8, sp, 160	# %sfp,
	s32i	a11, sp, 156	# %sfp,
	s32i	a13, sp, 152	# %sfp,
	l16si	a14, sp, 28	# A_Q12,
	l16si	a4, sp, 30	# A_Q12,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	srai	a3, a3, 1	#, tmp1226,
	srai	a2, a2, 16	#, tmp1241,
# @OPUS@\upstream\silk\PLC.c:410:     for( i = 0; i < psDec->frame_length; i++ ) {
	movi.n	a5, 0	#,
	l32i	a6, sp, 168	# %sfp, ivtmp$96
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	s32i	a14, sp, 148	# %sfp,
	s32i	a4, sp, 144	# %sfp,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	s32i	a3, sp, 176	# %sfp,
	s32i	a2, sp, 180	# %sfp,
# @OPUS@\upstream\silk\PLC.c:410:     for( i = 0; i < psDec->frame_length; i++ ) {
	s32i	a5, sp, 72	# %sfp,
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	s32i	a12, sp, 184	# %sfp, tmp1807
.L49:
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	l32i.n	a11, a6, 60	# MEM[base: _1521, offset: 60B], _296
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	l32i.n	a10, a6, 56	# MEM[base: _1521, offset: 56B], _309
# @OPUS@\upstream\silk\PLC.c:413:         LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	l32i	a13, sp, 64	# %sfp,
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	l32i	a3, sp, 84	# %sfp,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	l32i	a4, sp, 92	# %sfp,
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	l32i.n	a9, a6, 52	# MEM[base: _1521, offset: 52B], _322
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	srai	a14, a11, 16	# tmp1243, _296,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	srai	a2, a10, 16	# tmp1245, _309,
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	l32i.n	a8, a6, 48	# MEM[base: _1521, offset: 48B], _335
# @OPUS@\upstream\silk\PLC.c:413:         LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	l32i.n	a12, a13, 40	# psDec_8(D)->LPC_order, _289
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	mull	a2, a2, a4	# tmp1246, tmp1245,
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	l32i	a5, sp, 108	# %sfp,
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	mull	a14, a14, a3	# tmp1244, tmp1243,
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	l32i.n	a7, a6, 44	# MEM[base: _1521, offset: 44B], _348
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	l32i	a13, sp, 112	# %sfp,
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	srai	a15, a9, 16	# tmp1250, _322,
	mull	a15, a15, a5	# tmp1251, tmp1250,
	add.n	a14, a14, a2	# tmp1247, tmp1244, tmp1246
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	l32i	a5, sp, 120	# %sfp,
# @OPUS@\upstream\silk\PLC.c:413:         LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	srai	a3, a12, 1	# LPC_pred_Q10, _289,
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	srai	a2, a8, 16	# tmp1253, _335,
	add.n	a14, a14, a3	# tmp1249, tmp1247, LPC_pred_Q10
	mull	a2, a2, a13	# tmp1254, tmp1253,
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	srai	a13, a7, 16	# tmp1256, _348,
	add.n	a14, a14, a15	# tmp1252, tmp1249, tmp1251
	mull	a13, a13, a5	# tmp1257, tmp1256,
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	l32i.n	a5, a6, 40	# MEM[base: _1521, offset: 40B],
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	l32i.n	a4, a6, 36	# MEM[base: _1521, offset: 36B], _374
	add.n	a2, a14, a2	# tmp1255, tmp1252, tmp1254
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	l32i	a14, sp, 124	# %sfp,
	srai	a15, a5, 16	# tmp1259,,
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	l32i	a5, sp, 128	# %sfp,
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	l32i.n	a3, a6, 32	# MEM[base: _1521, offset: 32B], _387
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	mull	a15, a15, a14	# tmp1260, tmp1259,
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	srai	a14, a4, 16	# tmp1262, _374,
	mull	a14, a14, a5	# tmp1263, tmp1262,
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	l32i	a5, sp, 132	# %sfp,
	add.n	a2, a2, a13	# tmp1258, tmp1255, tmp1257
	srai	a13, a3, 16	# tmp1265, _387,
	mull	a13, a13, a5	# tmp1266, tmp1265,
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	l32i.n	a5, a6, 28	# MEM[base: _1521, offset: 28B],
	add.n	a2, a2, a15	# tmp1261, tmp1258, tmp1260
	srai	a15, a5, 16	# tmp1268,,
	l32i	a5, sp, 136	# %sfp,
	add.n	a2, a2, a14	# tmp1264, tmp1261, tmp1263
	mull	a14, a15, a5	# tmp1269, tmp1268,
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	l32i.n	a5, a6, 24	# MEM[base: _1521, offset: 24B],
	add.n	a13, a2, a13	# tmp1267, tmp1264, tmp1266
	srai	a15, a5, 16	# tmp1271,,
	l32i	a2, sp, 140	# %sfp,
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	l32i	a5, sp, 84	# %sfp,
	extui	a11, a11, 0, 16	# tmp1274, _296,
	add.n	a13, a13, a14	# tmp1270, tmp1267, tmp1269
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	mull	a15, a15, a2	# tmp1272, tmp1271,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	l32i	a14, sp, 92	# %sfp,
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	mull	a11, a11, a5	# tmp1275, tmp1274,
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	l32i	a2, sp, 108	# %sfp,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	extui	a10, a10, 0, 16	# tmp1278, _309,
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	l32i	a5, sp, 112	# %sfp,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	mull	a10, a10, a14	# tmp1279, tmp1278,
	add.n	a15, a13, a15	# tmp1273, tmp1270, tmp1272
# @OPUS@\upstream\silk\PLC.c:414:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  1), A_Q12[ 0 ] );
	srai	a11, a11, 16	# tmp1276, tmp1275,
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	extui	a9, a9, 0, 16	# tmp1282, _322,
	mull	a9, a9, a2	# tmp1283, tmp1282,
	add.n	a15, a15, a11	# tmp1277, tmp1273, tmp1276
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	extui	a8, a8, 0, 16	# tmp1286, _335,
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	l32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	mull	a8, a8, a5	# tmp1287, tmp1286,
# @OPUS@\upstream\silk\PLC.c:415:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  2), A_Q12[ 1 ] );
	srai	a10, a10, 16	# tmp1280, tmp1279,
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	extui	a7, a7, 0, 16	# tmp1290, _348,
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	l32i.n	a13, a6, 40	# MEM[base: _1521, offset: 40B],
# @OPUS@\upstream\silk\PLC.c:416:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  3), A_Q12[ 2 ] );
	srai	a9, a9, 16	# tmp1284, tmp1283,
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	mull	a7, a7, a11	# tmp1291, tmp1290,
	add.n	a15, a15, a10	# tmp1281, tmp1277, tmp1280
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	l32i	a14, sp, 124	# %sfp,
	add.n	a15, a15, a9	# tmp1285, tmp1281, tmp1284
# @OPUS@\upstream\silk\PLC.c:417:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  4), A_Q12[ 3 ] );
	srai	a8, a8, 16	# tmp1288, tmp1287,
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	l32i	a2, sp, 128	# %sfp,
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	extui	a5, a13, 0, 16	# tmp1294,,
	add.n	a15, a15, a8	# tmp1289, tmp1285, tmp1288
# @OPUS@\upstream\silk\PLC.c:418:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  5), A_Q12[ 4 ] );
	srai	a7, a7, 16	# tmp1292, tmp1291,
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	mull	a5, a5, a14	# tmp1295, tmp1294,
	add.n	a15, a15, a7	# tmp1293, tmp1289, tmp1292
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	l32i.n	a8, a6, 28	# MEM[base: _1521, offset: 28B],
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	l32i	a7, sp, 132	# %sfp,
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	extui	a4, a4, 0, 16	# tmp1298, _374,
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	l32i	a11, sp, 136	# %sfp,
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	mull	a4, a4, a2	# tmp1299, tmp1298,
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	extui	a3, a3, 0, 16	# tmp1302, _387,
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	l32i.n	a13, a6, 24	# MEM[base: _1521, offset: 24B],
# @OPUS@\upstream\silk\PLC.c:419:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  6), A_Q12[ 5 ] );
	srai	a5, a5, 16	# tmp1296, tmp1295,
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	mull	a3, a3, a7	# tmp1303, tmp1302,
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	extui	a2, a8, 0, 16	# tmp1306,,
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	l32i	a14, sp, 140	# %sfp,
	add.n	a15, a15, a5	# tmp1297, tmp1293, tmp1296
# @OPUS@\upstream\silk\PLC.c:420:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  7), A_Q12[ 6 ] );
	srai	a4, a4, 16	# tmp1300, tmp1299,
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	mull	a2, a2, a11	# tmp1307, tmp1306,
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	extui	a9, a13, 0, 16	# tmp1309,,
# @OPUS@\upstream\silk\PLC.c:421:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  8), A_Q12[ 7 ] );
	srai	a3, a3, 16	# tmp1304, tmp1303,
	add.n	a15, a15, a4	# tmp1301, tmp1297, tmp1300
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	mull	a9, a9, a14	# tmp1310, tmp1309,
	add.n	a15, a15, a3	# tmp1305, tmp1301, tmp1304
# @OPUS@\upstream\silk\PLC.c:422:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i -  9), A_Q12[ 8 ] );
	srai	a2, a2, 16	# tmp1308, tmp1307,
	add.n	a2, a15, a2	# _754, tmp1305, tmp1308
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	srai	a9, a9, 16	# tmp1311, tmp1310,
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	movi.n	a3, 0xa	#,
# @OPUS@\upstream\silk\PLC.c:423:         LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - 10), A_Q12[ 9 ] );
	add.n	a2, a9, a2	# LPC_pred_Q10, tmp1311, _754
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	bge	a3, a12, .L42	#, _289,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	l32i.n	a4, a6, 20	# MEM[base: _1521, offset: 20B], _1815
	l32i	a5, sp, 164	# %sfp,
	extui	a3, a4, 0, 16	# tmp1313, _1815,
	mull	a3, a3, a5	# tmp1314, tmp1313,
	srai	a4, a4, 16	# tmp1316, _1815,
	mull	a4, a4, a5	# tmp1317, tmp1316,
	srai	a3, a3, 16	# tmp1315, tmp1314,
	add.n	a3, a3, a4	# tmp1318, tmp1315, tmp1317
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	movi.n	a7, 0xb	#,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	add.n	a2, a2, a3	# LPC_pred_Q10, LPC_pred_Q10, tmp1318
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	beq	a12, a7, .L42	# _289,,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	l32i.n	a4, a6, 16	# MEM[base: _1521, offset: 16B], _1796
	l32i	a8, sp, 160	# %sfp,
	extui	a3, a4, 0, 16	# tmp1320, _1796,
	mull	a3, a3, a8	# tmp1321, tmp1320,
	srai	a4, a4, 16	# tmp1323, _1796,
	mull	a4, a4, a8	# tmp1324, tmp1323,
	srai	a3, a3, 16	# tmp1322, tmp1321,
	add.n	a3, a3, a4	# tmp1325, tmp1322, tmp1324
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	add.n	a2, a2, a3	# LPC_pred_Q10, LPC_pred_Q10, tmp1325
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	beqi	a12, 12, .L42	# _289,,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	l32i.n	a4, a6, 12	# MEM[base: _1521, offset: 12B], _1734
	l32i	a11, sp, 156	# %sfp,
	extui	a3, a4, 0, 16	# tmp1326, _1734,
	mull	a3, a3, a11	# tmp1327, tmp1326,
	srai	a4, a4, 16	# tmp1329, _1734,
	mull	a4, a4, a11	# tmp1330, tmp1329,
	srai	a3, a3, 16	# tmp1328, tmp1327,
	add.n	a3, a3, a4	# tmp1331, tmp1328, tmp1330
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	movi.n	a13, 0xd	#,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	add.n	a2, a2, a3	# LPC_pred_Q10, LPC_pred_Q10, tmp1331
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	beq	a12, a13, .L42	# _289,,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	l32i.n	a4, a6, 8	# MEM[base: _1521, offset: 8B], _1704
	l32i	a14, sp, 152	# %sfp,
	extui	a3, a4, 0, 16	# tmp1333, _1704,
	mull	a3, a3, a14	# tmp1334, tmp1333,
	srai	a4, a4, 16	# tmp1336, _1704,
	mull	a4, a4, a14	# tmp1337, tmp1336,
	srai	a3, a3, 16	# tmp1335, tmp1334,
	add.n	a3, a3, a4	# tmp1338, tmp1335, tmp1337
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	movi.n	a5, 0xe	# tmp1339,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	add.n	a2, a2, a3	# LPC_pred_Q10, LPC_pred_Q10, tmp1338
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	beq	a12, a5, .L42	# _289, tmp1339,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	l32i.n	a4, a6, 4	# MEM[base: _1521, offset: 4B], _1685
	l32i	a7, sp, 148	# %sfp,
	extui	a3, a4, 0, 16	# tmp1340, _1685,
	mull	a3, a3, a7	# tmp1341, tmp1340,
	srai	a4, a4, 16	# tmp1343, _1685,
	mull	a4, a4, a7	# tmp1344, tmp1343,
	srai	a3, a3, 16	# tmp1342, tmp1341,
	add.n	a3, a3, a4	# tmp1345, tmp1342, tmp1344
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	movi.n	a5, 0xf	# tmp1346,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	add.n	a2, a2, a3	# LPC_pred_Q10, LPC_pred_Q10, tmp1345
# @OPUS@\upstream\silk\PLC.c:424:         for( j = 10; j < psDec->LPC_order; j++ ) {
	beq	a12, a5, .L42	# _289, tmp1346,
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	l32i.n	a4, a6, 0	# MEM[base: _1521, offset: 0B], _429
	l32i	a8, sp, 144	# %sfp,
	extui	a3, a4, 0, 16	# tmp1347, _429,
	mull	a3, a3, a8	# tmp1348, tmp1347,
	srai	a4, a4, 16	# tmp1350, _429,
	mull	a4, a4, a8	# tmp1351, tmp1350,
	srai	a3, a3, 16	# tmp1349, tmp1348,
	add.n	a3, a3, a4	# tmp1352, tmp1349, tmp1351
# @OPUS@\upstream\silk\PLC.c:425:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i - j - 1), A_Q12[ j ] );
	add.n	a2, a2, a3	# LPC_pred_Q10, LPC_pred_Q10, tmp1352
.L42:
# @OPUS@\upstream\silk\PLC.c:429:         PLC_STORE_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i,
	l32r	a11, .LC23	#,
	l32i	a4, a6, 64	# MEM[base: _1521, offset: 64B], _445
	blt	a11, a2, .L44	#, LPC_pred_Q10,
	l32r	a3, .LC24	#, tmp1354
	blt	a2, a3, .L45	# LPC_pred_Q10, tmp1354,
	slli	a2, a2, 4	# iftmp$38_449, LPC_pred_Q10,
	add.n	a5, a4, a2	# tmp1355, _445, iftmp$38_449
	mov.n	a3, a2	# iftmp$48_438, iftmp$38_449
	bltz	a5, .L68	# tmp1355,
.L65:
	and	a3, a4, a2	# tmp1356, _445, iftmp$42_455
	bltz	a3, .L77	# tmp1356,
.L67:
	add.n	a2, a2, a4	# iftmp$40_458, iftmp$42_455, _445
	l32i	a13, sp, 76	# %sfp,
	extui	a4, a2, 0, 16	# tmp1357, iftmp$40_458,
	mull	a4, a4, a13	# tmp1358, tmp1357,
	srai	a3, a2, 16	# _1824, iftmp$40_458,
	srai	a4, a4, 16	# _1834, tmp1358,
	j	.L47		#
.L68:
	or	a2, a4, a3	# tmp1359, _445, iftmp$48_438
	bgez	a2, .L78	# tmp1359,
.L66:
	add.n	a2, a3, a4	# iftmp$40_458, iftmp$48_438, _445
	l32i	a14, sp, 76	# %sfp,
	extui	a4, a2, 0, 16	# tmp1360, iftmp$40_458,
	mull	a4, a4, a14	# tmp1361, tmp1360,
	srai	a3, a2, 16	# _1824, iftmp$40_458,
	srai	a4, a4, 16	# _1834, tmp1361,
	j	.L47		#
.L77:
	movi.n	a4, 0	# _1834,
	l32r	a3, .LC2	#, _1824
	l32r	a2, .LC4	#, iftmp$40_458
	j	.L47		#
.L78:
	l32r	a2, .LC6	#, iftmp$40_458
	l32i	a4, sp, 180	# %sfp, _1834
	l32r	a3, .LC1	#, _1824
.L47:
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	l32i	a5, sp, 76	# %sfp,
	l32i	a7, sp, 176	# %sfp,
	mull	a3, a5, a3	# tmp1362,, _1824
	mull	a5, a2, a7	# tmp1363, iftmp$40_458,
# @OPUS@\upstream\silk\PLC.c:429:         PLC_STORE_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i,
	s32i	a2, a6, 64	# MEM[base: _1521, offset: 64B], iftmp$40_458
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	add.n	a3, a3, a5	# tmp1364, tmp1362, tmp1363
	add.n	a4, a3, a4	# tmp1365, tmp1364, _1834
	srai	a4, a4, 7	# tmp1366, tmp1365,
	addi.n	a4, a4, 1	# tmp1367, tmp1366,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	l32r	a2, .LC1	#, iftmp$55_483
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	srai	a4, a4, 1	# _482, tmp1367,
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	blt	a2, a4, .L48	# tmp8, _482,
	l32r	a2, .LC2	#, iftmp$55_483
	blt	a4, a2, .L48	# _482, tmp11,
	slli	a4, a4, 16	# tmp1370, _482,
	srai	a2, a4, 16	# iftmp$55_483, tmp1370,
.L48:
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	l32i	a14, sp, 116	# %sfp,
# @OPUS@\upstream\silk\PLC.c:410:     for( i = 0; i < psDec->frame_length; i++ ) {
	l32i	a13, sp, 64	# %sfp,
	addi.n	a6, a6, 4	# ivtmp$96, ivtmp$96,
	l32i.n	a3, a13, 28	# psDec_8(D)->frame_length, _488
# @OPUS@\upstream\silk\PLC.c:433:         frame[ i ] = (opus_int16)silk_SAT16( silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( PLC_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i), prevGain_Q10[ 1 ] ), 8 ) ) );
	s16i	a2, a14, 0	# MEM[base: _1536, offset: 0B], iftmp$55_483
# @OPUS@\upstream\silk\PLC.c:410:     for( i = 0; i < psDec->frame_length; i++ ) {
	l32i	a2, sp, 72	# %sfp,
	addi.n	a14, a14, 2	#,,
	addi.n	a2, a2, 1	#,,
	s32i	a2, sp, 72	# %sfp,
	s32i	a14, sp, 116	# %sfp,
# @OPUS@\upstream\silk\PLC.c:410:     for( i = 0; i < psDec->frame_length; i++ ) {
	blt	a2, a3, .L49	#, _488,
	l32i	a12, sp, 184	# %sfp, tmp1807
.L41:
# @OPUS@\upstream\silk\PLC.c:455:     PLC_COPY_WORDS(psDec->sLPC_Q14_buf, &sLPC_Q14_ptr[psDec->frame_length], MAX_LPC_ORDER);
	l32i	a5, sp, 168	# %sfp,
	slli	a3, a3, 2	# tmp1372, _488,
	l32i	a2, sp, 172	# %sfp,
	add.n	a3, a5, a3	#,, tmp1372
	movi.n	a4, 0x40	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\PLC.c:460:     psPLC->rand_seed     = rand_seed;
	l32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\silk\PLC.c:461:     psPLC->randScale_Q14 = rand_scale_Q14;
	l32i	a11, sp, 88	# %sfp,
# @OPUS@\upstream\silk\PLC.c:463:         psDecCtrl->pitchL[ i ] = lag;
	l32i	a14, sp, 68	# %sfp,
	l32i	a13, sp, 100	# %sfp,
# @OPUS@\upstream\silk\PLC.c:460:     psPLC->rand_seed     = rand_seed;
	s32i	a8, a12, 132	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].rand_seed,
# @OPUS@\upstream\silk\PLC.c:461:     psPLC->randScale_Q14 = rand_scale_Q14;
	s16i	a11, a12, 136	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].randScale_Q14,
# @OPUS@\upstream\silk\PLC.c:465:     RESTORE_STACK;
	l32i.n	a2, sp, 32	# _saved_stack,
	l32i.n	a3, sp, 36	# _saved_stack,
# @OPUS@\upstream\silk\PLC.c:463:         psDecCtrl->pitchL[ i ] = lag;
	s32i.n	a14, a13, 0	# psDecCtrl_11(D)->pitchL,
	s32i.n	a14, a13, 4	# psDecCtrl_11(D)->pitchL,
	s32i.n	a14, a13, 8	# psDecCtrl_11(D)->pitchL,
	s32i.n	a14, a13, 12	# psDecCtrl_11(D)->pitchL,
# @OPUS@\upstream\silk\PLC.c:465:     RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\PLC.c:120:         psDec->lossCnt++;
	l32i	a2, a12, 68	# psDec_8(D)->lossCnt, psDec_8(D)->lossCnt
	addi.n	a2, a2, 1	# tmp1382, psDec_8(D)->lossCnt,
	s32i	a2, a12, 68	# psDec_8(D)->lossCnt, tmp1382
	j	.L3		#
.L5:
# @OPUS@\upstream\silk\PLC.c:152:     psDec->prevSignalType = psDec->indices.signalType;
	addmi	a4, a11, 0x500	# tmp1384, tmp8,
	l8ui	a4, a4, 209	# psDec_8(D)->indices.signalType, _600
	slli	a4, a4, 24	# tmp1387, _600,
	srai	a4, a4, 24	# tmp1386, tmp1387,
	s32i	a4, a12, 72	# psDec_8(D)->prevSignalType, tmp1386
# @OPUS@\upstream\silk\PLC.c:154:     if( psDec->indices.signalType == TYPE_VOICED ) {
	bnei	a4, 2, .L51	# tmp1386,,
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	l32i	a11, sp, 64	# %sfp,
	l32i	a8, sp, 100	# %sfp,
	l32i.n	a13, a11, 24	# psDec_8(D)->nb_subfr, _794
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	l32i.n	a14, a11, 32	# psDec_8(D)->subfr_length, _785
	slli	a15, a13, 2	# tmp1392, _794,
	add.n	a15, a8, a15	# _1655,, tmp1392
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	addi	a15, a15, -4	# tmp1806, _1655,
	l32i.n	a6, a15, 0	# MEM[(struct silk_decoder_control *)_1655 + 4294967292B], _690
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	addi.n	a8, a13, -1	# tmp1813, _794,
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	addi.n	a4, a6, -1	# tmp1397, _690,
	or	a4, a6, a4	# tmp1398, _690, tmp1397
# @OPUS@\upstream\silk\PLC.c:157:             if( j == psDec->nb_subfr ) {
	bltz	a4, .L52	# tmp1398,
	movi.n	a10, 1	# tmp1403,
	mov.n	a4, a5	# tmp1402, lost
	moveqz	a4, a10, a13	# tmp1402, tmp1403, _794
	extui	a4, a4, 0, 8	# tmp1405, tmp1402
	bnez.n	a4, .L52	# tmp1405,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	slli	a9, a8, 2	# tmp1407, tmp1813,
	l32i	a11, sp, 100	# %sfp,
	add.n	a4, a9, a8	# tmp1408, tmp1407, tmp1813
	ssl	a10	#
	sll	a4, a4	# tmp1409, tmp1408
	add.n	a4, a11, a4	# _611,, tmp1409
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a7, a4, 100	# MEM[(struct silk_decoder_control *)_611 + 100B],
	l16si	a11, a4, 96	# MEM[(struct silk_decoder_control *)_611 + 96B],
	s32i	a7, sp, 80	# %sfp,
	s32i	a11, sp, 72	# %sfp,
	l16si	a7, a4, 98	# MEM[(struct silk_decoder_control *)_611 + 98B], tmp1413
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l32i	a11, sp, 80	# %sfp,
	add.n	a7, a11, a7	# tmp1416,, tmp1413
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a11, a4, 102	# MEM[(struct silk_decoder_control *)_611 + 102B],
	l16si	a4, a4, 104	# MEM[(struct silk_decoder_control *)_611 + 104B],
	s32i	a11, sp, 80	# %sfp,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l32i	a11, sp, 72	# %sfp,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	s32i	a4, sp, 84	# %sfp,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l32i	a4, sp, 80	# %sfp,
	add.n	a7, a7, a11	#, tmp1416,
	add.n	a11, a4, a7	# temp_LTP_Gain_Q14,,
	l32i	a7, sp, 84	# %sfp,
	add.n	a11, a7, a11	# temp_LTP_Gain_Q14,, temp_LTP_Gain_Q14
# @OPUS@\upstream\silk\PLC.c:164:             if( temp_LTP_Gain_Q14 > LTP_Gain_Q14 ) {
	blt	a11, a10, .L53	# temp_LTP_Gain_Q14,,
# @OPUS@\upstream\silk\PLC.c:166:                 silk_memcpy( psPLC->LTPCoef_Q14,
	slli	a6, a8, 16	# tmp1429, tmp1813,
	srai	a6, a6, 16	# tmp1428, tmp1429,
	slli	a4, a6, 2	# tmp1431, tmp1428,
	add.n	a4, a4, a6	# tmp1432, tmp1431, tmp1428
	addi	a4, a4, 48	# tmp1433, tmp1432,
	l32i	a6, sp, 100	# %sfp,
	ssl	a10	#
	sll	a4, a4	# tmp1434, tmp1433
	add.n	a4, a6, a4	# tmp1435,, tmp1434
	l8ui	a6, a4, 0	# MEM[(void *)_1466],
	l8ui	a7, a4, 1	# MEM[(void *)_1466],
	s8i	a6, a3, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a6, a4, 2	# MEM[(void *)_1466],
	s8i	a7, a2, 1	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a7, a4, 3	# MEM[(void *)_1466],
	s8i	a6, a2, 2	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a6, a4, 4	# MEM[(void *)_1466],
	s8i	a7, a2, 3	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a7, a4, 5	# MEM[(void *)_1466],
	s8i	a6, a2, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a6, a4, 6	# MEM[(void *)_1466],
	s8i	a7, a2, 5	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a7, a4, 7	# MEM[(void *)_1466],
	s8i	a6, a2, 6	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a6, a4, 8	# MEM[(void *)_1466],
	s8i	a7, a2, 7	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	l8ui	a4, a4, 9	# MEM[(void *)_1466],
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	l32i	a7, sp, 100	# %sfp,
# @OPUS@\upstream\silk\PLC.c:166:                 silk_memcpy( psPLC->LTPCoef_Q14,
	s8i	a6, a2, 8	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
	s8i	a4, a2, 9	# MEM[(void *)pretmp_1856], MEM[(void *)_1466]
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	add.n	a9, a7, a9	# tmp1448,, tmp1407
	l32i.n	a4, a9, 0	# psDecCtrl_11(D)->pitchL, tmp1450
	l32i.n	a6, a15, 0	# MEM[(struct silk_decoder_control *)_1655 + 4294967292B], _690
	slli	a4, a4, 8	# tmp1449, tmp1450,
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	s32i	a4, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8, tmp1449
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	bge	a14, a6, .L81	# _785, _690,
# @OPUS@\upstream\silk\PLC.c:157:             if( j == psDec->nb_subfr ) {
	moveqz	a5, a10, a8	# tmp1457, tmp1403, tmp1813
	extui	a5, a5, 0, 8	# tmp1461, tmp1457
	bnez.n	a5, .L81	# tmp1461,
	mov.n	a5, a11	# lost, temp_LTP_Gain_Q14
.L73:
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	addi	a10, a13, -2	# tmp1812, _794,
	slli	a9, a10, 2	# tmp1463, tmp1812,
	l32i	a8, sp, 100	# %sfp,
	add.n	a4, a9, a10	# tmp1464, tmp1463, tmp1812
	slli	a4, a4, 1	# tmp1465, tmp1464,
	add.n	a4, a8, a4	# _397,, tmp1465
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a7, a4, 100	# MEM[(struct silk_decoder_control *)_397 + 100B], tmp1466
	l16si	a8, a4, 98	# MEM[(struct silk_decoder_control *)_397 + 98B], tmp1469
	l16si	a11, a4, 96	# MEM[(struct silk_decoder_control *)_397 + 96B], tmp1473
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	add.n	a8, a7, a8	# tmp1472, tmp1466, tmp1469
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a7, a4, 102	# MEM[(struct silk_decoder_control *)_397 + 102B], tmp1476
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	add.n	a8, a8, a11	# temp_LTP_Gain_Q14, tmp1472, tmp1473
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a4, a4, 104	# MEM[(struct silk_decoder_control *)_397 + 104B], tmp1479
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	add.n	a8, a7, a8	# temp_LTP_Gain_Q14, tmp1476, temp_LTP_Gain_Q14
	add.n	a4, a4, a8	# temp_LTP_Gain_Q14, tmp1479, temp_LTP_Gain_Q14
# @OPUS@\upstream\silk\PLC.c:164:             if( temp_LTP_Gain_Q14 > LTP_Gain_Q14 ) {
	bge	a5, a4, .L56	# lost, temp_LTP_Gain_Q14,
# @OPUS@\upstream\silk\PLC.c:166:                 silk_memcpy( psPLC->LTPCoef_Q14,
	slli	a6, a10, 16	# tmp1485, tmp1812,
	srai	a6, a6, 16	# tmp1484, tmp1485,
	slli	a5, a6, 2	# tmp1487, tmp1484,
	add.n	a5, a5, a6	# tmp1488, tmp1487, tmp1484
	l32i	a11, sp, 100	# %sfp,
	addi	a5, a5, 48	# tmp1489, tmp1488,
	slli	a5, a5, 1	# tmp1490, tmp1489,
	add.n	a5, a11, a5	# tmp1491,, tmp1490
	l8ui	a6, a5, 0	# MEM[(void *)_1417],
	l8ui	a7, a5, 1	# MEM[(void *)_1417],
	s8i	a6, a3, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a6, a5, 2	# MEM[(void *)_1417],
	s8i	a7, a2, 1	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a7, a5, 3	# MEM[(void *)_1417],
	s8i	a6, a2, 2	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a6, a5, 4	# MEM[(void *)_1417],
	s8i	a7, a2, 3	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a7, a5, 5	# MEM[(void *)_1417],
	s8i	a6, a2, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a6, a5, 6	# MEM[(void *)_1417],
	s8i	a7, a2, 5	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a7, a5, 7	# MEM[(void *)_1417],
	s8i	a6, a2, 6	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a6, a5, 8	# MEM[(void *)_1417],
	s8i	a7, a2, 7	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	l8ui	a5, a5, 9	# MEM[(void *)_1417],
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	add.n	a9, a11, a9	# tmp1504,, tmp1463
# @OPUS@\upstream\silk\PLC.c:166:                 silk_memcpy( psPLC->LTPCoef_Q14,
	s8i	a6, a2, 8	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
	s8i	a5, a2, 9	# MEM[(void *)pretmp_1856], MEM[(void *)_1417]
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	l32i.n	a5, a9, 0	# psDecCtrl_11(D)->pitchL, tmp1506
	l32i.n	a6, a15, 0	# MEM[(struct silk_decoder_control *)_1655 + 4294967292B], _690
	slli	a5, a5, 8	# tmp1505, tmp1506,
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	s32i	a5, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8, tmp1505
	mov.n	a5, a4	# lost, temp_LTP_Gain_Q14
.L56:
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	slli	a9, a14, 1	# _1405, _785,
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	bge	a9, a6, .L54	# _1405, _690,
# @OPUS@\upstream\silk\PLC.c:157:             if( j == psDec->nb_subfr ) {
	beqz.n	a10, .L54	# tmp1812,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	addi	a10, a13, -3	# tmp1811, _794,
	slli	a11, a10, 2	# tmp1519, tmp1811,
	l32i	a8, sp, 100	# %sfp,
	add.n	a4, a11, a10	# tmp1520, tmp1519, tmp1811
	slli	a4, a4, 1	# tmp1521, tmp1520,
	add.n	a4, a8, a4	# _372,, tmp1521
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a7, a4, 100	# MEM[(struct silk_decoder_control *)_372 + 100B],
	l16si	a8, a4, 98	# MEM[(struct silk_decoder_control *)_372 + 98B], tmp1525
	s32i	a7, sp, 80	# %sfp,
	l16si	a7, a4, 96	# MEM[(struct silk_decoder_control *)_372 + 96B],
	s32i	a7, sp, 72	# %sfp,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l32i	a7, sp, 80	# %sfp,
	add.n	a8, a7, a8	# tmp1528,, tmp1525
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a7, a4, 102	# MEM[(struct silk_decoder_control *)_372 + 102B],
	l16si	a4, a4, 104	# MEM[(struct silk_decoder_control *)_372 + 104B], tmp1535
	s32i	a7, sp, 80	# %sfp,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l32i	a7, sp, 72	# %sfp,
	add.n	a8, a8, a7	# temp_LTP_Gain_Q14, tmp1528,
	l32i	a7, sp, 80	# %sfp,
	add.n	a8, a7, a8	# temp_LTP_Gain_Q14,, temp_LTP_Gain_Q14
	add.n	a4, a4, a8	# temp_LTP_Gain_Q14, tmp1535, temp_LTP_Gain_Q14
# @OPUS@\upstream\silk\PLC.c:164:             if( temp_LTP_Gain_Q14 > LTP_Gain_Q14 ) {
	bge	a5, a4, .L58	# lost, temp_LTP_Gain_Q14,
# @OPUS@\upstream\silk\PLC.c:166:                 silk_memcpy( psPLC->LTPCoef_Q14,
	slli	a6, a10, 16	# tmp1541, tmp1811,
	srai	a6, a6, 16	# tmp1540, tmp1541,
	slli	a5, a6, 2	# tmp1543, tmp1540,
	add.n	a5, a5, a6	# tmp1544, tmp1543, tmp1540
	l32i	a8, sp, 100	# %sfp,
	addi	a5, a5, 48	# tmp1545, tmp1544,
	slli	a5, a5, 1	# tmp1546, tmp1545,
	add.n	a5, a8, a5	# tmp1547,, tmp1546
	l8ui	a6, a5, 0	# MEM[(void *)_1368],
	l8ui	a7, a5, 1	# MEM[(void *)_1368],
	s8i	a6, a3, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a6, a5, 2	# MEM[(void *)_1368],
	s8i	a7, a2, 1	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a7, a5, 3	# MEM[(void *)_1368],
	s8i	a6, a2, 2	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a6, a5, 4	# MEM[(void *)_1368],
	s8i	a7, a2, 3	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a7, a5, 5	# MEM[(void *)_1368],
	s8i	a6, a2, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a6, a5, 6	# MEM[(void *)_1368],
	s8i	a7, a2, 5	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a7, a5, 7	# MEM[(void *)_1368],
	s8i	a6, a2, 6	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a6, a5, 8	# MEM[(void *)_1368],
	s8i	a7, a2, 7	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	l8ui	a7, a5, 9	# MEM[(void *)_1368],
	s8i	a6, a2, 8	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
	s8i	a7, a2, 9	# MEM[(void *)pretmp_1856], MEM[(void *)_1368]
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	add.n	a5, a8, a11	# tmp1560,, tmp1519
	l32i.n	a5, a5, 0	# psDecCtrl_11(D)->pitchL, tmp1562
	l32i.n	a6, a15, 0	# MEM[(struct silk_decoder_control *)_1655 + 4294967292B], _690
	slli	a5, a5, 8	# tmp1561, tmp1562,
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	s32i	a5, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8, tmp1561
	mov.n	a5, a4	# lost, temp_LTP_Gain_Q14
.L58:
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	add.n	a9, a14, a9	# tmp1565, _785, _1405
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	bge	a9, a6, .L54	# tmp1565, _690,
# @OPUS@\upstream\silk\PLC.c:157:             if( j == psDec->nb_subfr ) {
	beqz.n	a10, .L54	# tmp1811,
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	addi	a13, a13, -4	# tmp1810, _794,
	slli	a7, a13, 2	# tmp1576, tmp1810,
	add.n	a4, a7, a13	# tmp1577, tmp1576, tmp1810
	l32i	a11, sp, 100	# %sfp,
	slli	a4, a4, 1	# tmp1578, tmp1577,
	add.n	a4, a11, a4	# _1798,, tmp1578
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a9, a4, 98	# MEM[(struct silk_decoder_control *)_1798 + 98B], tmp1579
	l16si	a6, a4, 100	# MEM[(struct silk_decoder_control *)_1798 + 100B], tmp1582
	l16si	a8, a4, 96	# MEM[(struct silk_decoder_control *)_1798 + 96B], tmp1586
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	add.n	a6, a9, a6	# tmp1585, tmp1579, tmp1582
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a9, a4, 102	# MEM[(struct silk_decoder_control *)_1798 + 102B], tmp1589
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	add.n	a6, a6, a8	# temp_LTP_Gain_Q14, tmp1585, tmp1586
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	l16si	a4, a4, 104	# MEM[(struct silk_decoder_control *)_1798 + 104B], tmp1592
# @OPUS@\upstream\silk\PLC.c:162:                 temp_LTP_Gain_Q14 += psDecCtrl->LTPCoef_Q14[ ( psDec->nb_subfr - 1 - j ) * LTP_ORDER  + i ];
	add.n	a9, a9, a6	# temp_LTP_Gain_Q14, tmp1589, temp_LTP_Gain_Q14
	add.n	a9, a4, a9	# temp_LTP_Gain_Q14, tmp1592, temp_LTP_Gain_Q14
# @OPUS@\upstream\silk\PLC.c:164:             if( temp_LTP_Gain_Q14 > LTP_Gain_Q14 ) {
	bge	a5, a9, .L54	# lost, temp_LTP_Gain_Q14,
# @OPUS@\upstream\silk\PLC.c:166:                 silk_memcpy( psPLC->LTPCoef_Q14,
	slli	a13, a13, 16	# tmp1598, tmp1810,
	srai	a13, a13, 16	# tmp1597, tmp1598,
	slli	a4, a13, 2	# tmp1600, tmp1597,
	add.n	a4, a4, a13	# tmp1601, tmp1600, tmp1597
	addi	a4, a4, 48	# tmp1602, tmp1601,
	slli	a4, a4, 1	# tmp1603, tmp1602,
	add.n	a4, a11, a4	# tmp1604,, tmp1603
	l8ui	a5, a4, 0	# MEM[(void *)_623],
	l8ui	a6, a4, 1	# MEM[(void *)_623],
	s8i	a5, a3, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a5, a4, 2	# MEM[(void *)_623],
	s8i	a6, a2, 1	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a6, a4, 3	# MEM[(void *)_623],
	s8i	a5, a2, 2	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a5, a4, 4	# MEM[(void *)_623],
	s8i	a6, a2, 3	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a6, a4, 5	# MEM[(void *)_623],
	s8i	a5, a2, 4	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a5, a4, 6	# MEM[(void *)_623],
	s8i	a6, a2, 5	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a6, a4, 7	# MEM[(void *)_623],
	s8i	a5, a2, 6	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a5, a4, 8	# MEM[(void *)_623],
	s8i	a6, a2, 7	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	l8ui	a4, a4, 9	# MEM[(void *)_623],
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	add.n	a7, a11, a7	# tmp1617,, tmp1576
# @OPUS@\upstream\silk\PLC.c:166:                 silk_memcpy( psPLC->LTPCoef_Q14,
	s8i	a5, a2, 8	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
	s8i	a4, a2, 9	# MEM[(void *)pretmp_1856], MEM[(void *)_623]
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	l32i.n	a4, a7, 0	# psDecCtrl_11(D)->pitchL, tmp1619
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	mov.n	a5, a9	# lost, temp_LTP_Gain_Q14
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	slli	a4, a4, 8	# tmp1618, tmp1619,
# @OPUS@\upstream\silk\PLC.c:170:                 psPLC->pitchL_Q8 = silk_LSHIFT( psDecCtrl->pitchL[ psDec->nb_subfr - 1 - j ], 8 );
	s32i	a4, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8, tmp1618
	j	.L54		#
.L81:
# @OPUS@\upstream\silk\PLC.c:157:             if( j == psDec->nb_subfr ) {
	mov.n	a5, a11	# lost, temp_LTP_Gain_Q14
.L54:
# @OPUS@\upstream\silk\PLC.c:174:         silk_memset( psPLC->LTPCoef_Q14, 0, LTP_ORDER * sizeof( opus_int16 ) );
	movi.n	a4, 0	# tmp1620,
	s8i	a4, a3, 4	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 1	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 2	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 3	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 4	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 5	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 6	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 7	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 8	# MEM[(void *)pretmp_1856], tmp1620
	s8i	a4, a2, 9	# MEM[(void *)pretmp_1856], tmp1620
# @OPUS@\upstream\silk\PLC.c:178:         if( LTP_Gain_Q14 < V_PITCH_GAIN_START_MIN_Q14 ) {
	l32r	a2, .LC25	#, tmp1631
# @OPUS@\upstream\silk\PLC.c:175:         psPLC->LTPCoef_Q14[ LTP_ORDER / 2 ] = LTP_Gain_Q14;
	s16i	a5, a12, 88	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].LTPCoef_Q14, lost
# @OPUS@\upstream\silk\PLC.c:178:         if( LTP_Gain_Q14 < V_PITCH_GAIN_START_MIN_Q14 ) {
	blt	a2, a5, .L61	# tmp1631, lost,
	mov.n	a3, a5	# lost, lost
	bgei	a5, 1, .L62	# lost,,
.L98:
	movi.n	a3, 1	# lost,
.L62:
	l32r	a2, .LC26	#,
	call0	__divsi3		#
	slli	a2, a2, 16	# tmp1643,,
	srai	a2, a2, 16	# _1566, tmp1643,
.L69:
# @OPUS@\upstream\silk\PLC.c:185:                 psPLC->LTPCoef_Q14[ i ] = silk_RSHIFT( silk_SMULBB( psPLC->LTPCoef_Q14[ i ], scale_Q10 ), 10 );
	l16si	a6, a12, 84	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].LTPCoef_Q14, tmp1646
	l16si	a5, a12, 86	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2902B], tmp1653
	l16si	a4, a12, 88	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2904B], tmp1660
	l16si	a3, a12, 90	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2906B], tmp1667
	l16si	a7, a12, 92	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2908B], tmp1674
	mull	a6, a6, a2	# tmp1649, tmp1646, _1566
	mull	a5, a5, a2	# tmp1656, tmp1653, _1566
	mull	a4, a4, a2	# tmp1663, tmp1660, _1566
	mull	a3, a3, a2	# tmp1670, tmp1667, _1566
	mull	a2, a7, a2	# tmp1677, tmp1674, _1566
	srai	a6, a6, 10	# tmp1650, tmp1649,
	srai	a5, a5, 10	# tmp1657, tmp1656,
	srai	a4, a4, 10	# tmp1664, tmp1663,
	srai	a3, a3, 10	# tmp1671, tmp1670,
	srai	a2, a2, 10	# tmp1678, tmp1677,
# @OPUS@\upstream\silk\PLC.c:185:                 psPLC->LTPCoef_Q14[ i ] = silk_RSHIFT( silk_SMULBB( psPLC->LTPCoef_Q14[ i ], scale_Q10 ), 10 );
	s16i	a6, a12, 84	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].LTPCoef_Q14, tmp1650
	s16i	a5, a12, 86	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2902B], tmp1657
	s16i	a4, a12, 88	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2904B], tmp1664
	s16i	a3, a12, 90	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2906B], tmp1671
	s16i	a2, a12, 92	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2908B], tmp1678
	j	.L63		#
.L61:
# @OPUS@\upstream\silk\PLC.c:187:         } else if( LTP_Gain_Q14 > V_PITCH_GAIN_START_MAX_Q14 ) {
	l32r	a2, .LC27	#, tmp1679
	bge	a2, a5, .L63	# tmp1679, lost,
# @OPUS@\upstream\silk\PLC.c:192:             scale_Q14 = silk_DIV32( tmp, silk_max( LTP_Gain_Q14, 1 ) );
	l32r	a2, .LC28	#,
	mov.n	a3, a5	#, lost
	s32i	a5, sp, 188	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\PLC.c:194:                 psPLC->LTPCoef_Q14[ i ] = silk_RSHIFT( silk_SMULBB( psPLC->LTPCoef_Q14[ i ], scale_Q14 ), 14 );
	l32i	a5, sp, 188	#,
	l16si	a6, a12, 84	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].LTPCoef_Q14, tmp1688
	l16si	a8, a12, 86	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2902B], tmp1695
	l16si	a4, a12, 90	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2906B], tmp1709
	l16si	a7, a12, 92	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2908B], tmp1716
	slli	a3, a5, 16	# tmp1704, lost,
	srai	a3, a3, 16	# tmp1702, tmp1704,
	mull	a6, a6, a2	# tmp1691, tmp1688, tmp1685
	mull	a5, a8, a2	# tmp1698, tmp1695, tmp1685
	mull	a3, a3, a2	# tmp1705, tmp1702, tmp1685
	mull	a4, a4, a2	# tmp1712, tmp1709, tmp1685
	mull	a2, a7, a2	# tmp1719, tmp1716, tmp1685
	srai	a6, a6, 14	# tmp1692, tmp1691,
	srai	a5, a5, 14	# tmp1699, tmp1698,
	srai	a3, a3, 14	# tmp1706, tmp1705,
	srai	a4, a4, 14	# tmp1713, tmp1712,
	srai	a2, a2, 14	# tmp1720, tmp1719,
# @OPUS@\upstream\silk\PLC.c:194:                 psPLC->LTPCoef_Q14[ i ] = silk_RSHIFT( silk_SMULBB( psPLC->LTPCoef_Q14[ i ], scale_Q14 ), 14 );
	s16i	a6, a12, 84	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].LTPCoef_Q14, tmp1692
	s16i	a5, a12, 86	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2902B], tmp1699
	s16i	a3, a12, 88	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2904B], tmp1706
	s16i	a4, a12, 90	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2906B], tmp1713
	s16i	a2, a12, 92	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2908B], tmp1720
	j	.L63		#
.L51:
# @OPUS@\upstream\silk\PLC.c:198:         psPLC->pitchL_Q8 = silk_LSHIFT( silk_SMULBB( psDec->fs_kHz, 18 ), 8 );
	slli	a7, a7, 16	# tmp1723, _1,
	srai	a7, a7, 16	# tmp1722, tmp1723,
	slli	a4, a7, 3	# tmp1725, tmp1722,
	add.n	a7, a4, a7	# tmp1726, tmp1725, tmp1722
	slli	a7, a7, 9	# tmp1728, tmp1726,
# @OPUS@\upstream\silk\PLC.c:198:         psPLC->pitchL_Q8 = silk_LSHIFT( silk_SMULBB( psDec->fs_kHz, 18 ), 8 );
	s32i	a7, a12, 80	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].pitchL_Q8, tmp1728
# @OPUS@\upstream\silk\PLC.c:199:         silk_memset( psPLC->LTPCoef_Q14, 0, LTP_ORDER * sizeof( opus_int16 ));
	s8i	a5, a3, 4	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 1	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 2	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 3	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 4	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 5	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 6	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 7	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 8	# MEM[(void *)pretmp_1856], lost
	s8i	a5, a2, 9	# MEM[(void *)pretmp_1856], lost
.L63:
# @OPUS@\upstream\silk\PLC.c:203:     silk_memcpy( psPLC->prevLPC_Q12, psDecCtrl->PredCoef_Q12[ 1 ], psDec->LPC_order * sizeof( opus_int16 ) );
	l32i	a13, sp, 64	# %sfp,
	l32i	a14, sp, 100	# %sfp,
	l32i.n	a4, a13, 40	# psDec_8(D)->LPC_order, psDec_8(D)->LPC_order
	l32i	a2, sp, 68	# %sfp,
	addi	a3, a14, 64	#,,
	slli	a4, a4, 1	#, psDec_8(D)->LPC_order,
	call0	memcpy		#
# @OPUS@\upstream\silk\PLC.c:207:     silk_memcpy( psPLC->prevGain_Q16, &psDecCtrl->Gains_Q16[ psDec->nb_subfr - 2 ], 2 * sizeof( opus_int32 ) );
	l32i.n	a4, a13, 24	# psDec_8(D)->nb_subfr, _676
# @OPUS@\upstream\silk\PLC.c:204:     psPLC->prevLTP_scale_Q14 = psDecCtrl->LTP_scale_Q14;
	l32i	a3, a14, 136	# psDecCtrl_11(D)->LTP_scale_Q14, psDecCtrl_11(D)->LTP_scale_Q14
# @OPUS@\upstream\silk\PLC.c:207:     silk_memcpy( psPLC->prevGain_Q16, &psDecCtrl->Gains_Q16[ psDec->nb_subfr - 2 ], 2 * sizeof( opus_int32 ) );
	addi.n	a2, a4, 2	# tmp1753, _676,
	slli	a2, a2, 2	# tmp1754, tmp1753,
# @OPUS@\upstream\silk\PLC.c:204:     psPLC->prevLTP_scale_Q14 = psDecCtrl->LTP_scale_Q14;
	s16i	a3, a12, 148	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].prevLTP_scale_Q14, psDecCtrl_11(D)->LTP_scale_Q14
# @OPUS@\upstream\silk\PLC.c:207:     silk_memcpy( psPLC->prevGain_Q16, &psDecCtrl->Gains_Q16[ psDec->nb_subfr - 2 ], 2 * sizeof( opus_int32 ) );
	add.n	a2, a14, a2	# tmp1755,, tmp1754
	l32i	a8, sp, 76	# %sfp,
	l32r	a11, .LC9	#,
	l8ui	a5, a2, 0	# MEM[(void *)_678],
	l8ui	a6, a2, 1	# MEM[(void *)_678],
	add.n	a3, a8, a11	# tmp1750,,
	s8i	a5, a3, 72	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
	l8ui	a5, a2, 2	# MEM[(void *)_678],
	s8i	a6, a3, 73	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
	l8ui	a6, a2, 3	# MEM[(void *)_678],
	s8i	a5, a3, 74	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
	l8ui	a5, a2, 4	# MEM[(void *)_678],
	s8i	a6, a3, 75	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
	l8ui	a6, a2, 5	# MEM[(void *)_678],
	s8i	a5, a3, 76	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
	l8ui	a5, a2, 6	# MEM[(void *)_678],
	s8i	a6, a3, 77	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
	l8ui	a2, a2, 7	# MEM[(void *)_678],
	s8i	a5, a3, 78	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
	s8i	a2, a3, 79	# MEM[(void *)psDec_8(D) + 2968B], MEM[(void *)_678]
# @OPUS@\upstream\silk\PLC.c:209:     psPLC->subfr_length = psDec->subfr_length;
	l32i.n	a2, a13, 32	# psDec_8(D)->subfr_length, psDec_8(D)->subfr_length
# @OPUS@\upstream\silk\PLC.c:210:     psPLC->nb_subfr = psDec->nb_subfr;
	s32i	a4, a12, 164	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].nb_subfr, _676
# @OPUS@\upstream\silk\PLC.c:209:     psPLC->subfr_length = psDec->subfr_length;
	s32i	a2, a12, 168	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].subfr_length, psDec_8(D)->subfr_length
# @OPUS@\upstream\silk\PLC.c:135: }
	j	.L3		#
.L45:
# @OPUS@\upstream\silk\PLC.c:429:         PLC_STORE_WORD(sLPC_Q14_ptr, MAX_LPC_ORDER + i,
	l32r	a13, .LC4	#,
	add.n	a3, a4, a13	# tmp1768, _445,
	mov.n	a2, a13	# iftmp$42_455,
	bgez	a3, .L65	# tmp1768,
	mov.n	a3, a13	# iftmp$48_438,
	j	.L66		#
.L44:
	l32r	a14, .LC5	#,
	add.n	a3, a4, a14	# tmp1770, _445,
	mov.n	a2, a14	# iftmp$42_455,
	bgez	a3, .L67	# tmp1770,
	mov.n	a3, a14	# iftmp$48_438,
	j	.L68		#
.L52:
# @OPUS@\upstream\silk\PLC.c:174:         silk_memset( psPLC->LTPCoef_Q14, 0, LTP_ORDER * sizeof( opus_int16 ) );
	movi.n	a4, 0	# tmp1772,
	s8i	a4, a3, 4	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 1	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 2	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 3	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 4	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 5	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 6	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 7	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 8	# MEM[(void *)pretmp_1856], tmp1772
	s8i	a4, a2, 9	# MEM[(void *)pretmp_1856], tmp1772
# @OPUS@\upstream\silk\PLC.c:175:         psPLC->LTPCoef_Q14[ LTP_ORDER / 2 ] = LTP_Gain_Q14;
	movi.n	a2, 0	# tmp1783,
	s16i	a2, a12, 88	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].LTPCoef_Q14, tmp1783
	l32r	a2, .LC7	#, _1566
	j	.L69		#
.L71:
# @OPUS@\upstream\silk\PLC.c:174:         silk_memset( psPLC->LTPCoef_Q14, 0, LTP_ORDER * sizeof( opus_int16 ) );
	movi.n	a4, 0	# tmp1784,
	s8i	a4, a3, 4	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 1	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 2	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 3	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 4	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 5	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 6	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 7	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 8	# MEM[(void *)pretmp_1856], tmp1784
	s8i	a4, a2, 9	# MEM[(void *)pretmp_1856], tmp1784
# @OPUS@\upstream\silk\PLC.c:175:         psPLC->LTPCoef_Q14[ LTP_ORDER / 2 ] = LTP_Gain_Q14;
	movi.n	a2, 0	# tmp1795,
	s16i	a2, a12, 88	# MEM[(struct silk_PLC_struct *)psDec_8(D) + 2896B].LTPCoef_Q14, tmp1795
	j	.L98		#
.L53:
# @OPUS@\upstream\silk\PLC.c:156:         for( j = 0; j * psDec->subfr_length < psDecCtrl->pitchL[ psDec->nb_subfr - 1 ]; j++ ) {
	bge	a14, a6, .L71	# _785, _690,
# @OPUS@\upstream\silk\PLC.c:157:             if( j == psDec->nb_subfr ) {
	movnez	a10, a5, a8	# tmp1403, lost, tmp1813
	extui	a8, a10, 0, 8	# tmp1804, tmp1800
	beqz.n	a8, .L73	# tmp1804,
	j	.L71		#
.L3:
# @OPUS@\upstream\silk\PLC.c:135: }
	l32i	a0, sp, 236	#,
	movi	a9, 0xf0	#,
	l32i	a12, sp, 232	#,
	l32i	a13, sp, 228	#,
	l32i	a14, sp, 224	#,
	l32i	a15, sp, 220	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_PLC, .-silk_PLC
	.section	.text.silk_PLC_glue_frames,"ax",@progbits
	.literal_position
	.literal .LC29, 46214
	.literal .LC30, 32768
	.literal .LC31, 65536
	.literal .LC32, 2896
	.align	4
	.global	silk_PLC_glue_frames
	.type	silk_PLC_glue_frames, @function
# Function: silk_PLC_glue_frames
# Module: upstream/silk/PLC.c
# SILK packet-loss concealment and state recovery.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Glues concealed frames with new good received frames */
# C context: void silk_PLC_glue_frames(
# C context: silk_decoder_state                  *psDec,             /* I/O decoder state        */
# C context: opus_int16                          frame[],            /* I/O signal               */
# C context: opus_int                            length              /* I length of signal       */
# C context: )
silk_PLC_glue_frames:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 56	#,
# @OPUS@\upstream\silk\PLC.c:480:     if( psDec->lossCnt ) {
	addmi	a12, a2, 0xb00	# tmp205, psDec,
	l32i	a7, a12, 68	# psDec_46(D)->lossCnt, _1
# @OPUS@\upstream\silk\PLC.c:474: {
	s32i.n	a13, sp, 52	#,
	s32i.n	a0, sp, 60	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\silk\PLC.c:474: {
	mov.n	a8, a3	# frame, frame
	mov.n	a13, a4	# length, length
# @OPUS@\upstream\silk\PLC.c:480:     if( psDec->lossCnt ) {
	beqz.n	a7, .L103	# _1,
# @OPUS@\upstream\silk\PLC.c:482:         silk_sum_sqr_shift( &psPLC->conc_energy, &psPLC->conc_energy_shift, frame, length );
	l32r	a3, .LC32	#, tmp123
	mov.n	a5, a4	#, length
	add.n	a2, a2, a3	# tmp122, psDec, tmp123
	addi	a3, a2, 64	#, tmp122,
	mov.n	a4, a8	#, frame
	addi	a2, a2, 60	#, tmp122,
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\PLC.c:484:         psPLC->last_frame_lost = 1;
	movi.n	a2, 1	# tmp129,
	s32i	a2, a12, 128	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].last_frame_lost, tmp129
	j	.L102		#
.L103:
# @OPUS@\upstream\silk\PLC.c:486:         if( psDec->sPLC.last_frame_lost ) {
	l32i	a2, a12, 128	# psDec_46(D)->sPLC.last_frame_lost, psDec_46(D)->sPLC.last_frame_lost
	bnez.n	a2, .L105	# psDec_46(D)->sPLC.last_frame_lost,
.L108:
# @OPUS@\upstream\silk\PLC.c:527:         psPLC->last_frame_lost = 0;
	movi.n	a2, 0	# tmp133,
	s32i	a2, a12, 128	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].last_frame_lost, tmp133
	j	.L102		#
.L105:
# @OPUS@\upstream\silk\PLC.c:488:             silk_sum_sqr_shift( &energy, &energy_shift, frame, length );
	mov.n	a5, a4	#, length
	mov.n	a2, sp	#,
	mov.n	a4, a3	#, frame
	addi.n	a3, sp, 4	#,,
	s32i.n	a7, sp, 16	#,
	s32i.n	a8, sp, 20	#,
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\PLC.c:491:             if( energy_shift > psPLC->conc_energy_shift ) {
	l32i	a5, a12, 144	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy_shift, _5
# @OPUS@\upstream\silk\PLC.c:491:             if( energy_shift > psPLC->conc_energy_shift ) {
	l32i.n	a4, sp, 4	# energy_shift, energy_shift$78_6
# @OPUS@\upstream\silk\PLC.c:491:             if( energy_shift > psPLC->conc_energy_shift ) {
	l32i.n	a7, sp, 16	#,
	l32i.n	a8, sp, 20	#,
	bge	a5, a4, .L106	# _5, energy_shift$78_6,
# @OPUS@\upstream\silk\PLC.c:492:                 psPLC->conc_energy = silk_RSHIFT( psPLC->conc_energy, energy_shift - psPLC->conc_energy_shift );
	l32i	a6, a12, 140	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy, MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy
	sub	a4, a4, a5	# tmp137, energy_shift$78_6, _5
	ssr	a4	# tmp137
	sra	a15, a6	# prephitmp_174, MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy
# @OPUS@\upstream\silk\PLC.c:492:                 psPLC->conc_energy = silk_RSHIFT( psPLC->conc_energy, energy_shift - psPLC->conc_energy_shift );
	s32i	a15, a12, 140	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy, prephitmp_174
	l32i.n	a3, sp, 0	# energy, pretmp_175
	j	.L107		#
.L106:
	l32i	a15, a12, 140	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy, prephitmp_174
	l32i.n	a3, sp, 0	# energy, pretmp_175
# @OPUS@\upstream\silk\PLC.c:493:             } else if( energy_shift < psPLC->conc_energy_shift ) {
	bge	a4, a5, .L107	# energy_shift$78_6, _5,
# @OPUS@\upstream\silk\PLC.c:494:                 energy = silk_RSHIFT( energy, psPLC->conc_energy_shift - energy_shift );
	sub	a4, a5, a4	# tmp141, _5, energy_shift$78_6
	ssr	a4	# tmp141
	sra	a3, a3	# pretmp_175, pretmp_175
.L107:
# @OPUS@\upstream\silk\PLC.c:498:             if( energy > psPLC->conc_energy ) {
	bge	a15, a3, .L108	# prephitmp_174, pretmp_175,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a15, .L109	# prephitmp_174,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a2, a15	# iftmp$76_55, prephitmp_174
# @OPUS@\upstream\silk\PLC.c:503:                 LZ = LZ - 1;
	addi.n	a2, a2, -1	# LZ, iftmp$76_55,
# @OPUS@\upstream\silk\PLC.c:505:                 energy = silk_RSHIFT( energy, silk_max_32( 24 - LZ, 0 ) );
	movi.n	a4, 0x18	# tmp144,
	sub	a4, a4, a2	# tmp143, tmp144, LZ
# @OPUS@\upstream\silk\SigProc_FIX.h:574:     return (((a) > (b)) ? (a) : (b));
	movi.n	a5, 0	# tmp145,
# @OPUS@\upstream\silk\PLC.c:504:                 psPLC->conc_energy = silk_LSHIFT( psPLC->conc_energy, LZ );
	ssl	a2	# LZ
	sll	a2, a15	# _17, prephitmp_174
# @OPUS@\upstream\silk\SigProc_FIX.h:574:     return (((a) > (b)) ? (a) : (b));
	movltz	a4, a5, a4	# tmp143, tmp145, tmp143
# @OPUS@\upstream\silk\PLC.c:504:                 psPLC->conc_energy = silk_LSHIFT( psPLC->conc_energy, LZ );
	s32i	a2, a12, 140	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy, _17
# @OPUS@\upstream\silk\PLC.c:507:                 frac_Q24 = silk_DIV32( psPLC->conc_energy, silk_max( energy, 1 ) );
	ssr	a4	# tmp143
	sra	a3, a3	# _19, pretmp_175
	bgei	a3, 1, .L110	# _19,,
	movi.n	a3, 1	# _19,
.L110:
# @OPUS@\upstream\silk\PLC.c:507:                 frac_Q24 = silk_DIV32( psPLC->conc_energy, silk_max( energy, 1 ) );
	s32i.n	a7, sp, 16	#,
	s32i.n	a8, sp, 20	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	l32i.n	a7, sp, 16	#,
	l32i.n	a8, sp, 20	#,
	blti	a2, 1, .L118	# tmp151,,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a4, a2	# iftmp$76_73, tmp151
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a5, 0x18	# tmp152,
	sub	a5, a5, a4	# _74, tmp152, iftmp$76_73
# @OPUS@\upstream\silk\SigProc_FIX.h:403:     if( rot == 0 ) {
	beqz.n	a5, .L112	# _74,
# @OPUS@\upstream\silk\SigProc_FIX.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a5	# _74
	src	a3, a2, a2	# _82, tmp151
# @OPUS@\upstream\silk\SigProc_FIX.h:405:     } else if( rot < 0 ) {
	bgez	a5, .L114	# _74,
# @OPUS@\upstream\silk\SigProc_FIX.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a3, a4, -24	# m, iftmp$76_73,
# @OPUS@\upstream\silk\SigProc_FIX.h:406:         return (opus_int32) ((x << m) | (x >> (32 - m)));
	ssl	a3	# m
	src	a3, a2, a2	# _82, tmp151
.L114:
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a5, .LC29	#, tmp212
	l32r	a2, .LC30	#, tmp213
# @OPUS@\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	extui	a6, a4, 0, 1	# tmp154, iftmp$76_73,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	moveqz	a2, a5, a6	# tmp213, tmp212, tmp154
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a3, a3, 0, 7	# _84, _82,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	mov.n	a6, a2	# y, tmp213
.L115:
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a2, a3, 3	# tmp158, _84,
	add.n	a2, a3, a2	# tmp160, _84, tmp158
	slli	a2, a2, 3	# tmp162, tmp160,
	sub	a3, a2, a3	# tmp164, tmp162, _84
	slli	a2, a3, 2	# tmp166, tmp164,
	sub	a2, a2, a3	# tmp169, tmp166, tmp164
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	srai	a4, a4, 1	# tmp155, iftmp$76_73,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a2, a2, 16	# tmp171, tmp169,
# @OPUS@\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	ssr	a4	# tmp155
	sra	a6, a6	# y, y
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a2, a2, 16	# tmp170, tmp171,
	mull	a2, a2, a6	# tmp172, tmp170, y
	l32r	a14, .LC31	#, tmp204
	srai	a2, a2, 16	# _94, tmp172,
# @OPUS@\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	add.n	a6, a6, a2	# y, y, _94
	slli	a15, a6, 4	# prephitmp_174, y,
	sub	a2, a14, a15	# _227, tmp204, prephitmp_174
	j	.L111		#
.L118:
# @OPUS@\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	l32r	a14, .LC31	#, tmp204
	mov.n	a15, a7	# prephitmp_174, _1
	mov.n	a2, a14	# _227, tmp204
.L111:
# @OPUS@\upstream\silk\PLC.c:510:                 slope_Q16 = silk_DIV32_16( ( (opus_int32)1 << 16 ) - gain_Q16, length );
	mov.n	a3, a13	#, length
	s32i.n	a8, sp, 20	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\PLC.c:512:                 slope_Q16 = silk_LSHIFT( slope_Q16, 2 );
	slli	a2, a2, 2	# slope_Q16,,
# @OPUS@\upstream\silk\PLC.c:517:                     for( i = 0; i < length; i++ ) {
	l32i.n	a8, sp, 20	#,
	blti	a13, 1, .L108	# length,,
# @OPUS@\upstream\silk\PLC.c:518:                         frame[ i ] = silk_SMULWB( gain_Q16, frame[ i ] );
	l16si	a5, a8, 0	# *frame_48(D), _108
	extui	a3, a15, 0, 16	# tmp181, prephitmp_174,
	mull	a3, a3, a5	# tmp182, tmp181, _108
	srai	a4, a15, 16	# tmp184, prephitmp_174,
	mul16s	a4, a4, a5	# tmp185, tmp184, _108
	srai	a3, a3, 16	# tmp183, tmp182,
	add.n	a3, a3, a4	# tmp188, tmp183, tmp185
# @OPUS@\upstream\silk\PLC.c:518:                         frame[ i ] = silk_SMULWB( gain_Q16, frame[ i ] );
	s16i	a3, a8, 0	# *frame_48(D), tmp188
# @OPUS@\upstream\silk\PLC.c:519:                         gain_Q16 += slope_Q16;
	add.n	a6, a2, a15	# gain_Q16, slope_Q16, prephitmp_174
# @OPUS@\upstream\silk\PLC.c:520:                         if( gain_Q16 > (opus_int32)1 << 16 ) {
	blt	a14, a6, .L108	# tmp204, gain_Q16,
	slli	a13, a13, 1	# tmp190, length,
	addi.n	a7, a8, 2	# ivtmp$145, frame,
	add.n	a13, a8, a13	# _266, frame, tmp190
	j	.L116		#
.L117:
# @OPUS@\upstream\silk\PLC.c:518:                         frame[ i ] = silk_SMULWB( gain_Q16, frame[ i ] );
	l16si	a9, a7, 0	# MEM[base: _265, offset: 0B], _32
	mull	a5, a5, a9	# tmp194, tmp193, _32
	mul16s	a8, a8, a9	# tmp197, tmp196, _32
	srai	a5, a5, 16	# tmp195, tmp194,
	add.n	a5, a5, a8	# tmp200, tmp195, tmp197
# @OPUS@\upstream\silk\PLC.c:518:                         frame[ i ] = silk_SMULWB( gain_Q16, frame[ i ] );
	s16i	a5, a7, 0	# MEM[base: _265, offset: 0B], tmp200
	addi.n	a7, a7, 2	# ivtmp$145, ivtmp$145,
# @OPUS@\upstream\silk\PLC.c:520:                         if( gain_Q16 > (opus_int32)1 << 16 ) {
	blt	a14, a6, .L108	# tmp204, gain_Q16,
.L116:
# @OPUS@\upstream\silk\PLC.c:518:                         frame[ i ] = silk_SMULWB( gain_Q16, frame[ i ] );
	extui	a5, a6, 0, 16	# tmp193, gain_Q16,
	srai	a8, a6, 16	# tmp196, gain_Q16,
# @OPUS@\upstream\silk\PLC.c:519:                         gain_Q16 += slope_Q16;
	add.n	a6, a6, a2	# gain_Q16, gain_Q16, slope_Q16
# @OPUS@\upstream\silk\PLC.c:517:                     for( i = 0; i < length; i++ ) {
	bne	a7, a13, .L117	# ivtmp$145, _266,
	j	.L108		#
.L112:
# @OPUS@\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a3, a2, 0, 7	# _84, tmp151,
# @OPUS@\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a6, .LC29	#, y
	j	.L115		#
.L109:
# @OPUS@\upstream\silk\PLC.c:504:                 psPLC->conc_energy = silk_LSHIFT( psPLC->conc_energy, LZ );
	l32r	a14, .LC31	#, tmp204
	s32i	a15, a12, 140	# MEM[(struct silk_PLC_struct *)psDec_46(D) + 2896B].conc_energy, prephitmp_174
	mov.n	a2, a14	# _227, tmp204
	j	.L111		#
.L102:
# @OPUS@\upstream\silk\PLC.c:529: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_PLC_glue_frames, .-silk_PLC_glue_frames
	.section	.rodata.PLC_RAND_ATTENUATE_UV_Q15,"a"
	.align	4
	.type	PLC_RAND_ATTENUATE_UV_Q15, @object
	.size	PLC_RAND_ATTENUATE_UV_Q15, 4
PLC_RAND_ATTENUATE_UV_Q15:
	.short	32440
	.short	29491
	.section	.rodata.PLC_RAND_ATTENUATE_V_Q15,"a"
	.align	4
	.type	PLC_RAND_ATTENUATE_V_Q15, @object
	.size	PLC_RAND_ATTENUATE_V_Q15, 4
PLC_RAND_ATTENUATE_V_Q15:
	.short	31130
	.short	26214
	.section	.rodata.HARM_ATT_Q15,"a"
	.align	4
	.type	HARM_ATT_Q15, @object
	.size	HARM_ATT_Q15, 4
HARM_ATT_Q15:
	.short	32440
	.short	31130
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
