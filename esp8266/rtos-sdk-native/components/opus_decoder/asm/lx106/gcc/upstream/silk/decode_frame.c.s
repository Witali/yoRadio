# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/decode_frame.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"decode_frame.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\decode_frame.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\decode_frame.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\decode_frame.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\decode_frame.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\decode_frame.c.s.raw
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
	.section	.text.silk_decode_frame,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_decode_frame
	.type	silk_decode_frame, @function
# Function: silk_decode_frame
# Module: upstream/silk/decode_frame.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /****************/
# C context: /* Decode frame */
# C context: /****************/
# C context: opus_int silk_decode_frame(
# C context: silk_decoder_state          *psDec,                         /* I/O  Pointer to Silk decoder state               */
# C context: ec_dec                      *psRangeDec,                    /* I/O  Compressor data structure                   */
# C context: opus_int16                  pOut[],                         /* O    Pointer to output speech frame              */
# C context: opus_int32                  *pN,                            /* O    Pointer to size of output frame             */
silk_decode_frame:
	addi	sp, sp, -80	#,,
	s32i	a12, sp, 72	#,
	mov.n	a12, a2	# psDec, psDec
	s32i.n	a5, sp, 20	# %sfp, pN
	s32i	a0, sp, 76	#,
	s32i	a13, sp, 68	#,
	s32i	a14, sp, 64	#,
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\silk\decode_frame.c:58: {
	mov.n	a14, a4	# pOut, pOut
	s32i.n	a7, sp, 28	# %sfp, condCoding
# @OPUS@\upstream\silk\decode_frame.c:61:     SAVE_STACK;
	s32i.n	a6, sp, 40	#, tmp5
# @OPUS@\upstream\silk\decode_frame.c:58: {
	s32i.n	a3, sp, 24	# %sfp, psRangeDec
# @OPUS@\upstream\silk\decode_frame.c:63:     L = psDec->frame_length;
	addmi	a15, a12, 0x400	# tmp174, psDec,
# @OPUS@\upstream\silk\decode_frame.c:61:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\decode_frame.c:63:     L = psDec->frame_length;
	l32i.n	a6, a15, 28	# psDec_40(D)->frame_length,
# @OPUS@\upstream\silk\decode_frame.c:61:     SAVE_STACK;
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\decode_frame.c:64:     ALLOC( psDecCtrl, 1, silk_decoder_control );
	movi.n	a4, 0	#,
	movi	a3, 0x8c	#,
	movi.n	a2, 1	#,
# @OPUS@\upstream\silk\decode_frame.c:63:     L = psDec->frame_length;
	s32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\silk\decode_frame.c:64:     ALLOC( psDecCtrl, 1, silk_decoder_control );
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a13, a2	# psDecCtrl,
# @OPUS@\upstream\silk\decode_frame.c:70:     if(   lostFlag == FLAG_DECODE_NORMAL ||
	l32i.n	a5, sp, 40	#,
# @OPUS@\upstream\silk\decode_frame.c:65:     psDecCtrl->LTP_scale_Q14 = 0;
	movi.n	a2, 0	# tmp101,
	s32i	a2, a13, 136	# psDecCtrl_43->LTP_scale_Q14, tmp101
# @OPUS@\upstream\silk\decode_frame.c:70:     if(   lostFlag == FLAG_DECODE_NORMAL ||
	beq	a5, a2, .L2	# lostFlag,,
# @OPUS@\upstream\silk\decode_frame.c:70:     if(   lostFlag == FLAG_DECODE_NORMAL ||
	bnei	a5, 2, .L3	# lostFlag,,
# @OPUS@\upstream\silk\decode_frame.c:71:         ( lostFlag == FLAG_DECODE_LBRR && psDec->LBRR_flags[ psDec->nFramesDecoded ] == 1 ) )
	l32i	a3, a15, 88	# psDec_40(D)->nFramesDecoded, psDec_40(D)->nFramesDecoded
	movi	a2, 0x11c	# tmp102,
	add.n	a2, a2, a3	# tmp103, tmp102, psDec_40(D)->nFramesDecoded
	slli	a2, a2, 2	# tmp106, tmp103,
	add.n	a2, a12, a2	# tmp107, psDec, tmp106
# @OPUS@\upstream\silk\decode_frame.c:71:         ( lostFlag == FLAG_DECODE_LBRR && psDec->LBRR_flags[ psDec->nFramesDecoded ] == 1 ) )
	l32i.n	a2, a2, 8	# psDec_40(D)->LBRR_flags, tmp109
	bnei	a2, 1, .L3	# tmp109,,
.L2:
# @OPUS@\upstream\silk\decode_frame.c:78:         ALLOC( pulses, (L + SHELL_CODEC_FRAME_LENGTH - 1) &
	l32i.n	a3, sp, 16	# %sfp,
	movi.n	a6, -0x10	# tmp111,
	addi.n	a2, a3, 15	# tmp110,,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	and	a2, a2, a6	#, tmp110, tmp111
	s32i.n	a5, sp, 40	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\decode_frame.c:84:         silk_decode_indices( psDec, psRangeDec, psDec->nFramesDecoded, lostFlag, condCoding );
	l32i	a4, a15, 88	# psDec_40(D)->nFramesDecoded,
	l32i.n	a6, sp, 28	# %sfp,
	l32i.n	a5, sp, 40	#,
	l32i.n	a3, sp, 24	# %sfp,
# @OPUS@\upstream\silk\decode_frame.c:92:                 psDec->indices.quantOffsetType, psDec->frame_length );
	addmi	a8, a12, 0x500	# tmp115, psDec,
# @OPUS@\upstream\silk\decode_frame.c:78:         ALLOC( pulses, (L + SHELL_CODEC_FRAME_LENGTH - 1) &
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\silk\decode_frame.c:84:         silk_decode_indices( psDec, psRangeDec, psDec->nFramesDecoded, lostFlag, condCoding );
	mov.n	a2, a12	#, psDec
	s32i.n	a8, sp, 36	#,
	call0	silk_decode_indices		#
# @OPUS@\upstream\silk\decode_frame.c:91:         silk_decode_pulses( psRangeDec, pulses, psDec->indices.signalType,
	l32i.n	a8, sp, 36	#,
	l32i.n	a6, a15, 28	# psDec_40(D)->frame_length,
	l8ui	a5, a8, 210	# psDec_40(D)->indices.quantOffsetType,
	l8ui	a4, a8, 209	# psDec_40(D)->indices.signalType,
	l32i.n	a3, sp, 32	# %sfp,
	l32i.n	a2, sp, 24	# %sfp,
	slli	a5, a5, 24	# tmp118, psDec_40(D)->indices.quantOffsetType,
	slli	a4, a4, 24	# tmp122, psDec_40(D)->indices.signalType,
	srai	a5, a5, 24	#, tmp118,
	srai	a4, a4, 24	#, tmp122,
	call0	silk_decode_pulses		#
# @OPUS@\upstream\silk\decode_frame.c:99:         silk_decode_parameters( psDec, psDecCtrl, condCoding );
	l32i.n	a4, sp, 28	# %sfp,
	mov.n	a3, a13	#, psDecCtrl
	mov.n	a2, a12	#, psDec
	call0	silk_decode_parameters		#
# @OPUS@\upstream\silk\decode_frame.c:106:         silk_decode_core( psDec, psDecCtrl, pOut, pulses, arch );
	l32i	a6, sp, 80	# arch,
	l32i.n	a5, sp, 32	# %sfp,
	mov.n	a4, a14	#, pOut
	mov.n	a3, a13	#, psDecCtrl
	mov.n	a2, a12	#, psDec
	call0	silk_decode_core		#
# @OPUS@\upstream\silk\decode_frame.c:113:         mv_len = psDec->ltp_mem_length - psDec->frame_length;
	l32i.n	a2, a15, 28	# psDec_40(D)->frame_length, _13
# @OPUS@\upstream\silk\decode_frame.c:113:         mv_len = psDec->ltp_mem_length - psDec->frame_length;
	l32i.n	a5, a15, 36	# psDec_40(D)->ltp_mem_length, psDec_40(D)->ltp_mem_length
# @OPUS@\upstream\silk\decode_frame.c:114:         silk_memmove( psDec->outBuf, &psDec->outBuf[ psDec->frame_length ], mv_len * sizeof(opus_int16) );
	addi	a3, a2, 36	# tmp127, _13,
# @OPUS@\upstream\silk\decode_frame.c:113:         mv_len = psDec->ltp_mem_length - psDec->frame_length;
	sub	a5, a5, a2	# mv_len, psDec_40(D)->ltp_mem_length, _13
# @OPUS@\upstream\silk\decode_frame.c:114:         silk_memmove( psDec->outBuf, &psDec->outBuf[ psDec->frame_length ], mv_len * sizeof(opus_int16) );
	slli	a5, a5, 1	# _17, mv_len,
	slli	a3, a3, 1	# tmp128, tmp127,
	mov.n	a4, a5	#, _17
	add.n	a3, a12, a3	#, psDec, tmp128
	addi	a2, a12, 72	#, psDec,
	s32i.n	a5, sp, 40	#,
	call0	memmove		#
# @OPUS@\upstream\silk\decode_frame.c:115:         silk_memcpy( &psDec->outBuf[ mv_len ], pOut, psDec->frame_length * sizeof( opus_int16 ) );
	l32i.n	a5, sp, 40	#,
	l32i.n	a4, a15, 28	# psDec_40(D)->frame_length, psDec_40(D)->frame_length
	addi	a2, a5, 72	# tmp131, _17,
	slli	a4, a4, 1	#, psDec_40(D)->frame_length,
	mov.n	a3, a14	#, pOut
	add.n	a2, a12, a2	#, psDec, tmp131
	call0	memcpy		#
# @OPUS@\upstream\silk\decode_frame.c:127:         silk_PLC( psDec, psDecCtrl, pOut, 0,
	l32i	a6, sp, 80	# arch,
	mov.n	a4, a14	#, pOut
	mov.n	a3, a13	#, psDecCtrl
	mov.n	a2, a12	#, psDec
	movi.n	a5, 0	#,
	call0	silk_PLC		#
# @OPUS@\upstream\silk\decode_frame.c:134:         psDec->prevSignalType = psDec->indices.signalType;
	l32i.n	a8, sp, 36	#,
# @OPUS@\upstream\silk\decode_frame.c:133:         psDec->lossCnt = 0;
	addmi	a4, a12, 0xb00	# tmp140, psDec,
	movi.n	a3, 0	# tmp141,
	s32i	a3, a4, 68	# psDec_40(D)->lossCnt, tmp141
# @OPUS@\upstream\silk\decode_frame.c:134:         psDec->prevSignalType = psDec->indices.signalType;
	l8ui	a2, a8, 209	# psDec_40(D)->indices.signalType,
	slli	a2, a2, 24	# tmp146, psDec_40(D)->indices.signalType,
	srai	a2, a2, 24	# tmp144, tmp146,
	s32i	a2, a4, 72	# psDec_40(D)->prevSignalType, tmp144
# @OPUS@\upstream\silk\decode_frame.c:138:         psDec->first_frame_after_reset = 0;
	s32i	a3, a15, 76	# psDec_40(D)->first_frame_after_reset, tmp141
# @OPUS@\upstream\silk\decode_frame.c:72:     {
	j	.L4		#
.L3:
# @OPUS@\upstream\silk\decode_frame.c:141:         silk_PLC( psDec, psDecCtrl, pOut, 1,
	l32i	a6, sp, 80	# arch,
	movi.n	a5, 1	#,
	mov.n	a4, a14	#, pOut
	mov.n	a3, a13	#, psDecCtrl
	mov.n	a2, a12	#, psDec
	call0	silk_PLC		#
# @OPUS@\upstream\silk\decode_frame.c:154:         mv_len = psDec->ltp_mem_length - psDec->frame_length;
	l32i.n	a2, a15, 28	# psDec_40(D)->frame_length, _25
# @OPUS@\upstream\silk\decode_frame.c:154:         mv_len = psDec->ltp_mem_length - psDec->frame_length;
	l32i.n	a5, a15, 36	# psDec_40(D)->ltp_mem_length, psDec_40(D)->ltp_mem_length
# @OPUS@\upstream\silk\decode_frame.c:155:         silk_memmove( psDec->outBuf, &psDec->outBuf[ psDec->frame_length ], mv_len * sizeof(opus_int16) );
	addi	a3, a2, 36	# tmp153, _25,
# @OPUS@\upstream\silk\decode_frame.c:154:         mv_len = psDec->ltp_mem_length - psDec->frame_length;
	sub	a5, a5, a2	# mv_len, psDec_40(D)->ltp_mem_length, _25
# @OPUS@\upstream\silk\decode_frame.c:155:         silk_memmove( psDec->outBuf, &psDec->outBuf[ psDec->frame_length ], mv_len * sizeof(opus_int16) );
	slli	a5, a5, 1	# _29, mv_len,
	slli	a3, a3, 1	# tmp154, tmp153,
	mov.n	a4, a5	#, _29
	add.n	a3, a12, a3	#, psDec, tmp154
	addi	a2, a12, 72	#, psDec,
	s32i.n	a5, sp, 40	#,
	call0	memmove		#
# @OPUS@\upstream\silk\decode_frame.c:156:         silk_memcpy( &psDec->outBuf[ mv_len ], pOut, psDec->frame_length * sizeof( opus_int16 ) );
	l32i.n	a5, sp, 40	#,
	l32i.n	a4, a15, 28	# psDec_40(D)->frame_length, psDec_40(D)->frame_length
	addi	a2, a5, 72	# tmp157, _29,
	slli	a4, a4, 1	#, psDec_40(D)->frame_length,
	mov.n	a3, a14	#, pOut
	add.n	a2, a12, a2	#, psDec, tmp157
	call0	memcpy		#
.L4:
# @OPUS@\upstream\silk\decode_frame.c:162:     silk_CNG( psDec, psDecCtrl, pOut, L );
	l32i.n	a5, sp, 16	# %sfp,
	mov.n	a4, a14	#, pOut
	mov.n	a3, a13	#, psDecCtrl
	mov.n	a2, a12	#, psDec
	call0	silk_CNG		#
# @OPUS@\upstream\silk\decode_frame.c:167:     silk_PLC_glue_frames( psDec, pOut, L );
	l32i.n	a4, sp, 16	# %sfp,
	mov.n	a3, a14	#, pOut
	mov.n	a2, a12	#, psDec
	call0	silk_PLC_glue_frames		#
# @OPUS@\upstream\silk\decode_frame.c:170:     psDec->lagPrev = psDecCtrl->pitchL[ psDec->nb_subfr - 1 ];
	l32i.n	a3, a15, 24	# psDec_40(D)->nb_subfr, psDec_40(D)->nb_subfr
# @OPUS@\upstream\silk\decode_frame.c:173:     *pN = L;
	l32i.n	a5, sp, 16	# %sfp,
# @OPUS@\upstream\silk\decode_frame.c:170:     psDec->lagPrev = psDecCtrl->pitchL[ psDec->nb_subfr - 1 ];
	addi.n	a3, a3, -1	# tmp167, psDec_40(D)->nb_subfr,
	slli	a3, a3, 2	# tmp170, tmp167,
	add.n	a13, a13, a3	# tmp171, psDecCtrl, tmp170
# @OPUS@\upstream\silk\decode_frame.c:170:     psDec->lagPrev = psDecCtrl->pitchL[ psDec->nb_subfr - 1 ];
	l32i.n	a4, a13, 0	# psDecCtrl_43->pitchL, tmp172
# @OPUS@\upstream\silk\decode_frame.c:175:     RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\silk\decode_frame.c:170:     psDec->lagPrev = psDecCtrl->pitchL[ psDec->nb_subfr - 1 ];
	s32i.n	a4, a15, 8	# psDec_40(D)->lagPrev, tmp172
# @OPUS@\upstream\silk\decode_frame.c:173:     *pN = L;
	l32i.n	a4, sp, 20	# %sfp,
# @OPUS@\upstream\silk\decode_frame.c:175:     RESTORE_STACK;
	l32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\decode_frame.c:173:     *pN = L;
	s32i.n	a5, a4, 0	# *pN_70(D),
# @OPUS@\upstream\silk\decode_frame.c:175:     RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\decode_frame.c:177: }
	l32i	a0, sp, 76	#,
	movi.n	a2, 0	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	silk_decode_frame, .-silk_decode_frame
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
