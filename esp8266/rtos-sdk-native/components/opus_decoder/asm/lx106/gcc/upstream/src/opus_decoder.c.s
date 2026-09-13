# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/src/opus_decoder.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"opus_decoder.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\src\opus_decoder.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\src\opus_decoder.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\src\opus_decoder.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\src\opus_decoder.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\src\opus_decoder.c.s.raw
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
	.section	.text.opus_decode_frame,"ax",@progbits
	.literal_position
	.literal .LC1, 32767
	.literal .LC2, -32768
	.literal .LC3, 2130706432
	.literal .LC4, 8000
	.literal .LC5, 12000
	.literal .LC6, 16000
	.literal .LC7, CSWTCH$60
	.literal .LC8, 10012
	.literal .LC9, 10008
	.literal .LC10, 10010
	.literal .LC11, 4031
	.literal .LC12, 4028
	.literal .LC13, 10015
	.literal .LC14, 48000
	.literal .LC15, 21771
	.literal .LC16, 10204
	.literal .LC17, 14819
	.literal .LC18, 22804
	.literal .LC19, 16383
	.literal .LC20, 32768
	.literal .LC21, -32767
	.align	4
	.type	opus_decode_frame, @function
# Function: opus_decode_frame
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return mode;
# C context: }
# C context:
# C context: static int opus_decode_frame(OpusDecoder *st, const unsigned char *data,
# C context: opus_int32 len, opus_val16 *pcm, int frame_size, int decode_fec)
# C context: {
# C context: void *silk_dec;
# C context: CELTDecoder *celt_dec;
opus_decode_frame:
	movi	a9, 0xf0	#,
	sub	sp, sp, a9	#,,
	s32i	a14, sp, 224	#,
	mov.n	a14, a2	# st, st
# @OPUS@\upstream\src\opus_decoder.c:301:    opus_uint32 redundant_rng = 0;
	movi.n	a2, 0	# tmp465,
# @OPUS@\upstream\src\opus_decoder.c:274: {
	s32i	a5, sp, 120	# %sfp, pcm
	s32i	a0, sp, 236	#,
	s32i	a12, sp, 232	#,
	s32i	a13, sp, 228	#,
	s32i	a15, sp, 220	#,
# @OPUS@\upstream\src\opus_decoder.c:274: {
	s32i	a4, sp, 140	# %sfp, len
	mov.n	a13, a6	# frame_size, frame_size
	s32i	a7, sp, 168	# %sfp, decode_fec
	s32i	a3, sp, 124	# %sfp, data
# @OPUS@\upstream\src\opus_decoder.c:301:    opus_uint32 redundant_rng = 0;
	s32i	a2, sp, 76	# redundant_rng, tmp465
# @OPUS@\upstream\src\opus_decoder.c:303:    ALLOC_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\src\opus_decoder.c:307:    F20 = st->Fs/50;
	l32i.n	a4, a14, 12	# st_282(D)->Fs, _5
# @OPUS@\upstream\src\opus_decoder.c:303:    ALLOC_STACK;
	s32i	a2, sp, 64	# _saved_stack,
	s32i	a3, sp, 68	# _saved_stack,
# @OPUS@\upstream\src\opus_decoder.c:307:    F20 = st->Fs/50;
	mov.n	a2, a4	#, _5
	movi.n	a3, 0x32	#,
	s32i	a4, sp, 192	#,
	call0	__divsi3		#
# @OPUS@\upstream\src\opus_decoder.c:305:    silk_dec = (char*)st+st->silk_dec_offset;
	l32i.n	a5, a14, 4	# st_282(D)->silk_dec_offset,
# @OPUS@\upstream\src\opus_decoder.c:306:    celt_dec = (CELTDecoder*)((char*)st+st->celt_dec_offset);
	l32i.n	a8, a14, 0	# st_282(D)->celt_dec_offset,
# @OPUS@\upstream\src\opus_decoder.c:309:    F5 = F10>>1;
	srai	a9, a2, 2	#,,
# @OPUS@\upstream\src\opus_decoder.c:307:    F20 = st->Fs/50;
	s32i	a2, sp, 108	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:310:    F2_5 = F5>>1;
	srai	a15, a2, 3	# F2_5,,
# @OPUS@\upstream\src\opus_decoder.c:305:    silk_dec = (char*)st+st->silk_dec_offset;
	s32i	a5, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:306:    celt_dec = (CELTDecoder*)((char*)st+st->celt_dec_offset);
	s32i	a8, sp, 172	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:309:    F5 = F10>>1;
	s32i	a9, sp, 148	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:308:    F10 = F20>>1;
	srai	a12, a2, 1	# F10,,
# @OPUS@\upstream\src\opus_decoder.c:311:    if (frame_size < F2_5)
	l32i	a4, sp, 192	#,
	bge	a13, a15, .L2	# frame_size, F2_5,
# @OPUS@\upstream\src\opus_decoder.c:313:       RESTORE_STACK;
	l32i	a2, sp, 64	# _saved_stack,
	l32i	a3, sp, 68	# _saved_stack,
# @OPUS@\upstream\src\opus_decoder.c:314:       return OPUS_BUFFER_TOO_SMALL;
	movi.n	a8, -2	#,
	s32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:313:       RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\src\opus_decoder.c:314:       return OPUS_BUFFER_TOO_SMALL;
	j	.L1		#
.L2:
# @OPUS@\upstream\src\opus_decoder.c:317:    frame_size = IMIN(frame_size, st->Fs/25*3);
	movi.n	a3, 0x19	#,
	mov.n	a2, a4	#, _5
	call0	__divsi3		#
	slli	a3, a2, 1	# tmp475,,
	add.n	a3, a3, a2	#, tmp475,
	s32i	a3, sp, 104	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:317:    frame_size = IMIN(frame_size, st->Fs/25*3);
	bge	a13, a3, .L4	# frame_size,,
	s32i	a13, sp, 104	# %sfp, frame_size
.L4:
# @OPUS@\upstream\src\opus_decoder.c:319:    if (len<=1)
	l32i	a9, sp, 140	# %sfp,
	bgei	a9, 2, .L5	#,,
# @OPUS@\upstream\src\opus_decoder.c:323:       frame_size = IMIN(frame_size, st->frame_size);
	l32i	a2, a14, 72	# st_282(D)->frame_size, st_282(D)->frame_size
	l32i	a8, sp, 104	# %sfp,
	bge	a2, a8, .L7	# st_282(D)->frame_size,,
	s32i	a2, sp, 104	# %sfp, st_282(D)->frame_size
	j	.L7		#
.L5:
# @OPUS@\upstream\src\opus_decoder.c:325:    if (data != NULL)
	l32i	a9, sp, 124	# %sfp,
	beqz.n	a9, .L7	#,
# @OPUS@\upstream\src\opus_decoder.c:328:       mode = st->mode;
	l32i	a8, a14, 64	# st_282(D)->mode,
# @OPUS@\upstream\src\opus_decoder.c:330:       ec_dec_init(&dec,(unsigned char*)data,len);
	mov.n	a3, a9	#,
# @OPUS@\upstream\src\opus_decoder.c:328:       mode = st->mode;
	s32i	a8, sp, 132	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:327:       audiosize = st->frame_size;
	l32i	a9, a14, 72	# st_282(D)->frame_size,
# @OPUS@\upstream\src\opus_decoder.c:329:       bandwidth = st->bandwidth;
	l32i.n	a8, a14, 60	# st_282(D)->bandwidth,
# @OPUS@\upstream\src\opus_decoder.c:330:       ec_dec_init(&dec,(unsigned char*)data,len);
	l32i	a4, sp, 140	# %sfp,
	addi	a2, sp, 16	#,,
# @OPUS@\upstream\src\opus_decoder.c:327:       audiosize = st->frame_size;
	s32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:329:       bandwidth = st->bandwidth;
	s32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:330:       ec_dec_init(&dec,(unsigned char*)data,len);
	call0	ec_dec_init		#
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	l32i	a9, sp, 132	# %sfp,
	movi	a3, -0x3ea	# tmp480,
	movi.n	a4, 0	# tmp483,
	add.n	a3, a9, a3	# tmp481,, tmp480
	movi.n	a2, 1	# tmp482,
	mov.n	a5, a4	#, tmp483
	movnez	a5, a2, a3	#, tmp482, tmp481
	extui	a3, a5, 0, 8	#, tmp479
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	l32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	s32i	a3, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	bge	a8, a12, .L8	#, F10,
	mov.n	a2, a4	# tmp484, tmp483
.L8:
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:381:    if (data!=NULL && st->prev_mode > 0 && (
	l32i	a3, a14, 68	# st_282(D)->prev_mode, _28
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	and	a2, a9, a2	# tmp486,, tmp484
	extui	a2, a2, 0, 8	#, tmp486
	s32i	a2, sp, 156	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	s32i	a2, sp, 184	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:381:    if (data!=NULL && st->prev_mode > 0 && (
	bgei	a3, 1, .L9	# _28,,
	j	.L203		#
.L7:
# @OPUS@\upstream\src\opus_decoder.c:334:       mode = st->prev_redundancy ? MODE_CELT_ONLY : st->prev_mode;
	l32i	a2, a14, 76	# st_282(D)->prev_redundancy, st_282(D)->prev_redundancy
	bnez.n	a2, .L120	# st_282(D)->prev_redundancy,
# @OPUS@\upstream\src\opus_decoder.c:334:       mode = st->prev_redundancy ? MODE_CELT_ONLY : st->prev_mode;
	l32i	a9, a14, 68	# st_282(D)->prev_mode,
	s32i	a9, sp, 132	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:337:       if (mode == 0)
	bnez.n	a9, .L11	#,
# @OPUS@\upstream\src\opus_decoder.c:340:          for (i=0;i<audiosize*st->channels;i++)
	l32i.n	a4, a14, 8	# st_282(D)->channels, st_282(D)->channels
	l32i	a8, sp, 104	# %sfp,
	mull	a4, a8, a4	# _928,, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:340:          for (i=0;i<audiosize*st->channels;i++)
	bgei	a4, 1, .L12	# _928,,
	j	.L204		#
.L12:
	l32i	a2, sp, 120	# %sfp,
	mov.n	a3, a9	#,
	slli	a4, a4, 1	#, _928,
	call0	memset		#
	j	.L204		#
.L120:
# @OPUS@\upstream\src\opus_decoder.c:334:       mode = st->prev_redundancy ? MODE_CELT_ONLY : st->prev_mode;
	movi	a9, 0x3ea	#,
	s32i	a9, sp, 132	# %sfp,
.L11:
# @OPUS@\upstream\src\opus_decoder.c:348:       if (audiosize > F20)
	l32i	a8, sp, 108	# %sfp,
	l32i	a9, sp, 104	# %sfp,
	bge	a8, a9, .L14	#,,
# @OPUS@\upstream\src\opus_decoder.c:351:             int ret = opus_decode_frame(st, NULL, 0, pcm, IMIN(audiosize, F20), 0);
	mov.n	a15, a14	# st, st
	l32i	a14, sp, 120	# %sfp, pcm
	mov.n	a12, a9	# audiosize,
	movi.n	a13, 0	# tmp1081,
.L17:
	l32i	a8, sp, 108	# %sfp,
	mov.n	a5, a14	#, pcm
	mov.n	a7, a13	#, tmp1081
	mov.n	a4, a13	#, tmp1081
	mov.n	a3, a13	#, tmp1081
	mov.n	a2, a15	#, st
	mov.n	a6, a12	# audiosize, audiosize
	bge	a8, a12, .L15	#, audiosize,
	mov.n	a6, a8	# audiosize,
.L15:
	call0	opus_decode_frame		#
# @OPUS@\upstream\src\opus_decoder.c:358:             audiosize -= ret;
	sub	a12, a12, a2	# audiosize, audiosize, ret
# @OPUS@\upstream\src\opus_decoder.c:352:             if (ret<0)
	bgez	a2, .L16	# ret,
	mov.n	a4, a2	# ret, ret
# @OPUS@\upstream\src\opus_decoder.c:354:                RESTORE_STACK;
	l32i	a3, sp, 68	# _saved_stack,
	l32i	a2, sp, 64	# _saved_stack,
# @OPUS@\upstream\src\opus_decoder.c:351:             int ret = opus_decode_frame(st, NULL, 0, pcm, IMIN(audiosize, F20), 0);
	s32i	a4, sp, 104	# %sfp, ret
# @OPUS@\upstream\src\opus_decoder.c:354:                RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\src\opus_decoder.c:355:                return ret;
	j	.L1		#
.L16:
# @OPUS@\upstream\src\opus_decoder.c:357:             pcm += ret*st->channels;
	l32i.n	a3, a15, 8	# st_282(D)->channels, st_282(D)->channels
	mull	a2, a2, a3	# tmp494, ret, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:357:             pcm += ret*st->channels;
	slli	a2, a2, 1	# tmp496, tmp494,
	add.n	a14, a14, a2	# pcm, pcm, tmp496
# @OPUS@\upstream\src\opus_decoder.c:359:          } while (audiosize > 0);
	bgei	a12, 1, .L17	# audiosize,,
.L204:
# @OPUS@\upstream\src\opus_decoder.c:360:          RESTORE_STACK;
	l32i	a2, sp, 64	# _saved_stack,
	l32i	a3, sp, 68	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\src\opus_decoder.c:361:          return frame_size;
	j	.L1		#
.L14:
	s32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:362:       } else if (audiosize < F20)
	bge	a9, a8, .L18	#,,
	s32i	a12, sp, 116	# %sfp, F10
# @OPUS@\upstream\src\opus_decoder.c:364:          if (audiosize > F10)
	blt	a12, a9, .L18	# F10,,
# @OPUS@\upstream\src\opus_decoder.c:366:          else if (mode != MODE_SILK_ONLY && audiosize > F5 && audiosize < F10)
	l32i	a8, sp, 148	# %sfp,
	movi.n	a2, 1	# tmp497,
	blt	a8, a9, .L20	#,,
	movi.n	a2, 0	# tmp497,
.L20:
# @OPUS@\upstream\src\opus_decoder.c:366:          else if (mode != MODE_SILK_ONLY && audiosize > F5 && audiosize < F10)
	l32i	a9, sp, 104	# %sfp,
	movi.n	a3, 1	# tmp499,
	blt	a9, a12, .L21	#, F10,
	movi.n	a3, 0	# tmp499,
.L21:
	and	a2, a2, a3	# tmp501, tmp497, tmp499
	bbci	a2, 0, .L136	# tmp501,,
# @OPUS@\upstream\src\opus_decoder.c:366:          else if (mode != MODE_SILK_ONLY && audiosize > F5 && audiosize < F10)
	l32i	a8, sp, 132	# %sfp,
	l32i	a9, sp, 148	# %sfp,
	movi	a2, -0x3e8	# tmp506,
	add.n	a2, a8, a2	# tmp507,, tmp506
	s32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:366:          else if (mode != MODE_SILK_ONLY && audiosize > F5 && audiosize < F10)
	bnez.n	a2, .L18	# tmp507,
.L136:
	l32i	a8, sp, 104	# %sfp,
	s32i	a8, sp, 116	# %sfp,
	j	.L18		#
.L9:
# @OPUS@\upstream\src\opus_decoder.c:381:    if (data!=NULL && st->prev_mode > 0 && (
	l32i	a9, sp, 132	# %sfp,
	movi	a2, 0x3ea	# tmp511,
	bne	a9, a2, .L22	#, tmp511,
# @OPUS@\upstream\src\opus_decoder.c:382:        (mode == MODE_CELT_ONLY && st->prev_mode != MODE_CELT_ONLY && !st->prev_redundancy)
	beq	a3, a9, .L23	# _28,,
# @OPUS@\upstream\src\opus_decoder.c:382:        (mode == MODE_CELT_ONLY && st->prev_mode != MODE_CELT_ONLY && !st->prev_redundancy)
	l32i	a13, a14, 76	# st_282(D)->prev_redundancy, start_band
# @OPUS@\upstream\src\opus_decoder.c:382:        (mode == MODE_CELT_ONLY && st->prev_mode != MODE_CELT_ONLY && !st->prev_redundancy)
	beqz.n	a13, .L24	# start_band,
	j	.L23		#
.L22:
# @OPUS@\upstream\src\opus_decoder.c:383:     || (mode != MODE_CELT_ONLY && st->prev_mode == MODE_CELT_ONLY) )
	beq	a3, a2, .L25	# _28, tmp511,
.L203:
	movi.n	a8, 0	#,
	s32i	a8, sp, 136	# %sfp,
	s32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:293:    int transition=0;
	s32i	a8, sp, 176	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:379:    pcm_transition_silk_size = ALLOC_NONE;
	s32i	a8, sp, 180	# %sfp,
	j	.L10		#
.L24:
# @OPUS@\upstream\src\opus_decoder.c:389:          pcm_transition_celt_size = F5*st->channels;
	l32i.n	a2, a14, 8	# st_282(D)->channels, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:393:    ALLOC(pcm_transition_celt, pcm_transition_celt_size, opus_val16);
	l32i	a9, sp, 148	# %sfp,
	mov.n	a4, a13	#, start_band
	mull	a2, a9, a2	#,, st_282(D)->channels
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:397:       opus_decode_frame(st, NULL, 0, pcm_transition, IMIN(F5, audiosize), 0);
	l32i	a6, sp, 148	# %sfp, F5
	l32i	a8, sp, 116	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:393:    ALLOC(pcm_transition_celt, pcm_transition_celt_size, opus_val16);
	s32i	a2, sp, 112	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:397:       opus_decode_frame(st, NULL, 0, pcm_transition, IMIN(F5, audiosize), 0);
	bge	a8, a6, .L26	#, F5,
	mov.n	a6, a8	# F5,
.L26:
	movi.n	a7, 0	#,
	l32i	a5, sp, 112	# %sfp,
	mov.n	a4, a7	#,
	mov.n	a3, a7	#, tmp4
	mov.n	a2, a14	#, st
	call0	opus_decode_frame		#
# @OPUS@\upstream\src\opus_decoder.c:399:    if (audiosize > frame_size)
	l32i	a9, sp, 104	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	bge	a9, a8, .L189	#,,
	j	.L27		#
.L25:
# @OPUS@\upstream\src\opus_decoder.c:391:          pcm_transition_silk_size = F5*st->channels;
	movi.n	a9, 1	#,
	l32i	a8, sp, 148	# %sfp,
	l32i.n	a2, a14, 8	# st_282(D)->channels, st_282(D)->channels
	s32i	a9, sp, 144	# %sfp,
	mull	a2, a8, a2	#,, st_282(D)->channels
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:386:       transition = 1;
	l32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:391:          pcm_transition_silk_size = F5*st->channels;
	s32i	a2, sp, 180	# %sfp,
	s32i	a9, sp, 136	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:386:       transition = 1;
	s32i	a8, sp, 176	# %sfp,
	j	.L10		#
.L27:
# @OPUS@\upstream\src\opus_decoder.c:402:       RESTORE_STACK;
	l32i	a2, sp, 64	# _saved_stack,
	l32i	a3, sp, 68	# _saved_stack,
# @OPUS@\upstream\src\opus_decoder.c:403:       return OPUS_BAD_ARG;
	movi.n	a9, -1	#,
	s32i	a9, sp, 104	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:402:       RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\src\opus_decoder.c:403:       return OPUS_BAD_ARG;
	j	.L1		#
.L194:
# @OPUS@\upstream\src\opus_decoder.c:409:    pcm_silk_size = (mode != MODE_CELT_ONLY && !celt_accum) ? IMAX(F10, frame_size)*st->channels : ALLOC_NONE;
	l32i	a8, sp, 156	# %sfp,
	movi.n	a2, 1	# tmp518,
# @OPUS@\upstream\src\opus_decoder.c:409:    pcm_silk_size = (mode != MODE_CELT_ONLY && !celt_accum) ? IMAX(F10, frame_size)*st->channels : ALLOC_NONE;
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:409:    pcm_silk_size = (mode != MODE_CELT_ONLY && !celt_accum) ? IMAX(F10, frame_size)*st->channels : ALLOC_NONE;
	xor	a2, a8, a2	# tmp519,, tmp518
# @OPUS@\upstream\src\opus_decoder.c:409:    pcm_silk_size = (mode != MODE_CELT_ONLY && !celt_accum) ? IMAX(F10, frame_size)*st->channels : ALLOC_NONE;
	and	a2, a9, a2	# tmp521,, tmp519
	extui	a2, a2, 0, 8	#, tmp521
	s32i	a2, sp, 160	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:409:    pcm_silk_size = (mode != MODE_CELT_ONLY && !celt_accum) ? IMAX(F10, frame_size)*st->channels : ALLOC_NONE;
	bnez.n	a2, .L29	#,
# @OPUS@\upstream\src\opus_decoder.c:410:    ALLOC(pcm_silk, pcm_silk_size, opus_int16);
	mov.n	a4, a2	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 188	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:418:       if (celt_accum)
	l32i	a8, sp, 156	# %sfp,
	l32i	a12, sp, 188	# %sfp, pcm_ptr
	l32i	a9, sp, 120	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:413:    if (mode != MODE_CELT_ONLY)
	movi	a2, 0x3ea	# tmp522,
# @OPUS@\upstream\src\opus_decoder.c:418:       if (celt_accum)
	movnez	a12, a9, a8	# pcm_ptr,,
# @OPUS@\upstream\src\opus_decoder.c:413:    if (mode != MODE_CELT_ONLY)
	l32i	a8, sp, 132	# %sfp,
	bne	a8, a2, .L33	#, tmp522,
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	l32i	a8, sp, 160	# %sfp,
	l32i	a9, sp, 136	# %sfp,
	s32i	a8, sp, 100	# %sfp,
	s32i	a9, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:296:    int redundancy_bytes = 0;
	s32i	a8, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:295:    int redundancy=0;
	s32i	a8, sp, 96	# %sfp,
	s32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:495:    start_band = 0;
	mov.n	a13, a8	# start_band,
	j	.L190		#
.L29:
# @OPUS@\upstream\src\opus_decoder.c:409:    pcm_silk_size = (mode != MODE_CELT_ONLY && !celt_accum) ? IMAX(F10, frame_size)*st->channels : ALLOC_NONE;
	l32i	a9, sp, 116	# %sfp,
	bge	a12, a9, .L32	# F10,,
	mov.n	a12, a9	# F10,
.L32:
# @OPUS@\upstream\src\opus_decoder.c:409:    pcm_silk_size = (mode != MODE_CELT_ONLY && !celt_accum) ? IMAX(F10, frame_size)*st->channels : ALLOC_NONE;
	l32i.n	a2, a14, 8	# st_282(D)->channels, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:410:    ALLOC(pcm_silk, pcm_silk_size, opus_int16);
	movi.n	a4, 0	#,
	mull	a2, a12, a2	#, F10, st_282(D)->channels
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	l32i	a8, sp, 144	# %sfp,
	l32i	a9, sp, 160	# %sfp,
	s32i	a8, sp, 136	# %sfp,
	movi.n	a8, 0	#,
	mov.n	a12, a2	# pcm_ptr,
	s32i	a2, sp, 188	# %sfp, pcm_ptr
	s32i	a9, sp, 128	# %sfp,
	s32i	a8, sp, 156	# %sfp,
.L33:
# @OPUS@\upstream\src\opus_decoder.c:305:    silk_dec = (char*)st+st->silk_dec_offset;
	l32i	a9, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:424:       if (st->prev_mode==MODE_CELT_ONLY
	l32i	a3, a14, 68	# st_282(D)->prev_mode, st_282(D)->prev_mode
# @OPUS@\upstream\src\opus_decoder.c:305:    silk_dec = (char*)st+st->silk_dec_offset;
	add.n	a9, a14, a9	#, st,
# @OPUS@\upstream\src\opus_decoder.c:424:       if (st->prev_mode==MODE_CELT_ONLY
	movi	a2, 0x3ea	# tmp526,
# @OPUS@\upstream\src\opus_decoder.c:305:    silk_dec = (char*)st+st->silk_dec_offset;
	s32i	a9, sp, 104	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:424:       if (st->prev_mode==MODE_CELT_ONLY
	bne	a3, a2, .L34	# st_282(D)->prev_mode, tmp526,
# @OPUS@\upstream\src\opus_decoder.c:429:          silk_ResetDecoder( silk_dec );
	mov.n	a2, a9	#,
	call0	silk_ResetDecoder		#
.L34:
# @OPUS@\upstream\src\opus_decoder.c:436:       st->DecControl.payloadSize_ms = IMAX(10, 1000 * audiosize / st->Fs);
	l32i	a8, sp, 116	# %sfp,
	l32i.n	a3, a14, 12	# st_282(D)->Fs,
	slli	a2, a8, 5	# tmp529,,
	sub	a2, a2, a8	# tmp530, tmp529,
	slli	a2, a2, 2	# tmp531, tmp530,
	add.n	a2, a2, a8	# tmp532, tmp531,
	slli	a2, a2, 3	#, tmp532,
	call0	__divsi3		#
	bgei	a2, 10, .L35	# tmp538,,
	movi.n	a2, 0xa	# tmp538,
.L35:
	l32i.n	a3, a14, 48	# st_282(D)->complexity, st_282(D)->complexity
# @OPUS@\upstream\src\opus_decoder.c:436:       st->DecControl.payloadSize_ms = IMAX(10, 1000 * audiosize / st->Fs);
	s32i.n	a2, a14, 32	# st_282(D)->DecControl.payloadSize_ms, tmp538
	movi.n	a2, 1	# tmp541,
	bgei	a3, 5, .L36	# st_282(D)->complexity,,
	movi.n	a2, 0	# tmp541,
.L36:
# @OPUS@\upstream\src\opus_decoder.c:438:       if (data != NULL)
	l32i	a9, sp, 124	# %sfp,
	beqz.n	a9, .L37	#,
# @OPUS@\upstream\src\opus_decoder.c:440:         st->DecControl.nChannelsInternal = st->stream_channels;
	l32i.n	a4, a14, 56	# st_282(D)->stream_channels, st_282(D)->stream_channels
# @OPUS@\upstream\src\opus_decoder.c:441:         if( mode == MODE_SILK_ONLY ) {
	l32i	a8, sp, 132	# %sfp,
	movi	a3, 0x3e8	# tmp546,
# @OPUS@\upstream\src\opus_decoder.c:440:         st->DecControl.nChannelsInternal = st->stream_channels;
	s32i.n	a4, a14, 20	# st_282(D)->DecControl.nChannelsInternal, st_282(D)->stream_channels
# @OPUS@\upstream\src\opus_decoder.c:441:         if( mode == MODE_SILK_ONLY ) {
	bne	a8, a3, .L38	#, tmp546,
# @OPUS@\upstream\src\opus_decoder.c:442:            if( bandwidth == OPUS_BANDWIDTH_NARROWBAND ) {
	l32i	a9, sp, 152	# %sfp,
	movi	a3, 0x44d	# tmp547,
	bne	a9, a3, .L39	#, tmp547,
# @OPUS@\upstream\src\opus_decoder.c:443:               st->DecControl.internalSampleRate = 8000;
	l32r	a3, .LC4	#, tmp548
	s32i.n	a3, a14, 28	# st_282(D)->DecControl.internalSampleRate, tmp548
	j	.L40		#
.L39:
# @OPUS@\upstream\src\opus_decoder.c:444:            } else if( bandwidth == OPUS_BANDWIDTH_MEDIUMBAND ) {
	movi	a3, 0x44e	# tmp549,
	bne	a9, a3, .L38	# tmp8, tmp549,
# @OPUS@\upstream\src\opus_decoder.c:445:               st->DecControl.internalSampleRate = 12000;
	l32r	a3, .LC5	#, tmp550
	s32i.n	a3, a14, 28	# st_282(D)->DecControl.internalSampleRate, tmp550
	j	.L40		#
.L38:
# @OPUS@\upstream\src\opus_decoder.c:447:               st->DecControl.internalSampleRate = 16000;
	l32r	a3, .LC6	#, tmp551
	s32i.n	a3, a14, 28	# st_282(D)->DecControl.internalSampleRate, tmp551
	j	.L40		#
.L113:
	addi	a9, a14, 16	#, st,
# @OPUS@\upstream\src\opus_decoder.c:472:         int first_frame = decoded_samples == 0;
	mov.n	a2, a14	# st, st
	s32i	a15, sp, 164	# %sfp, F2_5
	l32i	a15, sp, 116	# %sfp, audiosize
	mov.n	a14, a12	# pcm_ptr, pcm_ptr
# @OPUS@\upstream\src\opus_decoder.c:469:      decoded_samples = 0;
	movi.n	a13, 0	# decoded_samples,
	s32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:472:         int first_frame = decoded_samples == 0;
	mov.n	a12, a2	# st, st
.L44:
# @OPUS@\upstream\src\opus_decoder.c:473:         silk_ret = silk_Decode( silk_dec, &st->DecControl,
	l32i.n	a2, a12, 52	# st_282(D)->arch, st_282(D)->arch
	movi.n	a3, 1	#,
	movi.n	a5, 0	# first_frame,
	moveqz	a5, a3, a13	# first_frame,, decoded_samples
	s32i.n	a2, sp, 4	#, st_282(D)->arch
	addi	a8, sp, 80	#,,
	l32i	a4, sp, 100	# %sfp,
	l32i	a3, sp, 112	# %sfp,
	l32i	a2, sp, 104	# %sfp,
	mov.n	a7, a14	#, pcm_ptr
	addi	a6, sp, 16	#,,
	s32i.n	a8, sp, 0	#,
	call0	silk_Decode		#
# @OPUS@\upstream\src\opus_decoder.c:479:         if( silk_ret ) {
	beqz.n	a2, .L41	#,
# @OPUS@\upstream\src\opus_decoder.c:480:            if (lost_flag) {
	l32i	a9, sp, 100	# %sfp,
	movi.n	a3, 0	#,
	mov.n	a2, a14	#, pcm_ptr
	beq	a9, a3, .L42	#,,
# @OPUS@\upstream\src\opus_decoder.c:483:               for (i=0;i<frame_size*st->channels;i++)
	l32i.n	a5, a12, 8	# st_282(D)->channels, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:482:               silk_frame_size = frame_size;
	s32i	a15, sp, 80	# silk_frame_size, audiosize
# @OPUS@\upstream\src\opus_decoder.c:483:               for (i=0;i<frame_size*st->channels;i++)
	mull	a5, a15, a5	# _1254, audiosize, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:484:                  pcm_ptr[i] = 0;
	slli	a6, a5, 1	# tmp844, _1254,
	mov.n	a4, a6	#, tmp844
# @OPUS@\upstream\src\opus_decoder.c:483:               for (i=0;i<frame_size*st->channels;i++)
	blti	a5, 1, .L125	# _1254,,
	s32i	a6, sp, 192	#,
	call0	memset		#
# @OPUS@\upstream\src\opus_decoder.c:484:                  pcm_ptr[i] = 0;
	mov.n	a2, a15	# pretmp_1252, audiosize
	l32i	a6, sp, 192	#,
	j	.L43		#
.L42:
# @OPUS@\upstream\src\opus_decoder.c:486:              RESTORE_STACK;
	l32i	a2, sp, 64	# _saved_stack,
	l32i	a3, sp, 68	# _saved_stack,
# @OPUS@\upstream\src\opus_decoder.c:487:              return OPUS_INTERNAL_ERROR;
	movi.n	a8, -3	#,
	s32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:486:              RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\src\opus_decoder.c:487:              return OPUS_INTERNAL_ERROR;
	j	.L1		#
.L41:
	l32i	a2, sp, 80	# silk_frame_size, pretmp_1252
	l32i.n	a5, a12, 8	# st_282(D)->channels, st_282(D)->channels
	mull	a5, a2, a5	# _1254, pretmp_1252, st_282(D)->channels
	slli	a6, a5, 1	# tmp844, _1254,
	j	.L43		#
.L125:
# @OPUS@\upstream\src\opus_decoder.c:483:               for (i=0;i<frame_size*st->channels;i++)
	mov.n	a2, a15	# pretmp_1252, audiosize
	slli	a6, a5, 1	# tmp844, _1254,
.L43:
# @OPUS@\upstream\src\opus_decoder.c:491:         decoded_samples += silk_frame_size;
	add.n	a13, a13, a2	# decoded_samples, decoded_samples, pretmp_1252
# @OPUS@\upstream\src\opus_decoder.c:490:         pcm_ptr += silk_frame_size * st->channels;
	add.n	a14, a14, a6	# pcm_ptr, pcm_ptr, tmp844
# @OPUS@\upstream\src\opus_decoder.c:492:       } while( decoded_samples < frame_size );
	blt	a13, a15, .L44	# decoded_samples, audiosize,
	j	.L200		#
.L111:
# @OPUS@\upstream\src\opus_decoder.c:496:    if (!decode_fec && mode != MODE_CELT_ONLY && data != NULL
	l32i	a9, sp, 124	# %sfp,
	beqz.n	a9, .L126	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, sp, 44	# MEM[(unsigned int *)&dec + 28B], MEM[(unsigned int *)&dec + 28B]
	l32i	a8, sp, 140	# %sfp,
	nsau	a3, a2	# _386, MEM[(unsigned int *)&dec + 28B]
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, sp, 36	# MEM[(int *)&dec + 20B], MEM[(int *)&dec + 20B]
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	l32i	a9, sp, 132	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a2, a2, -32	# tmp566, MEM[(int *)&dec + 20B],
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	movi	a4, 0x3e9	# tmp568,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a3	# _352, tmp566, _386
	slli	a3, a8, 3	# _1258,,
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	beq	a9, a4, .L46	#, tmp568,
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	addi	a2, a2, 17	# tmp569, _352,
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	bge	a3, a2, .L47	# _1258, tmp569,
	j	.L201		#
.L117:
# @OPUS@\upstream\src\opus_decoder.c:501:          redundancy = ec_dec_bit_logp(&dec, 12);
	movi.n	a3, 0xc	#,
	addi	a2, sp, 16	#,,
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:504:       if (redundancy)
	bnez.n	a2, .L48	#,
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	s32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:296:    int redundancy_bytes = 0;
	s32i	a2, sp, 164	# %sfp,
	s32i	a2, sp, 112	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:526:       start_band = 17;
	movi.n	a13, 0x11	# start_band,
	j	.L190		#
.L116:
# @OPUS@\upstream\src\opus_decoder.c:512:          len -= redundancy_bytes;
	sub	a9, a9, a8	#,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a3	# tmp571, _426, _430
# @OPUS@\upstream\src\opus_decoder.c:512:          len -= redundancy_bytes;
	s32i	a9, sp, 140	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:515:          if (len*8 < ec_tell(&dec))
	slli	a3, a9, 3	# tmp570,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a2, a2, -32	# tmp572, tmp571,
# @OPUS@\upstream\src\opus_decoder.c:515:          if (len*8 < ec_tell(&dec))
	blt	a3, a2, .L127	# tmp570, tmp572,
	mov.n	a3, a8	# _1268,
	j	.L49		#
.L127:
	movi.n	a9, 0	#,
	s32i	a9, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:518:             redundancy_bytes = 0;
	mov.n	a3, a9	# _1268,
# @OPUS@\upstream\src\opus_decoder.c:519:             redundancy = 0;
	s32i	a9, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:517:             len = 0;
	s32i	a9, sp, 140	# %sfp, _1268
.L49:
# @OPUS@\upstream\src\opus_decoder.c:522:          dec.storage -= redundancy_bytes;
	l32i.n	a2, sp, 20	# dec.storage, dec.storage
	movi.n	a8, 0	#,
	sub	a2, a2, a3	# tmp573, dec.storage, _1268
# @OPUS@\upstream\src\opus_decoder.c:528:    if (redundancy)
	l32i	a9, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:522:          dec.storage -= redundancy_bytes;
	s32i	a8, sp, 112	# %sfp,
	s32i.n	a2, sp, 20	# dec.storage, tmp573
# @OPUS@\upstream\src\opus_decoder.c:526:       start_band = 17;
	movi.n	a13, 0x11	# start_band,
# @OPUS@\upstream\src\opus_decoder.c:528:    if (redundancy)
	bne	a9, a8, .L50	#,,
	j	.L190		#
.L126:
	s32i	a9, sp, 112	# %sfp, tmp8
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	s32i	a9, sp, 100	# %sfp, tmp8
# @OPUS@\upstream\src\opus_decoder.c:296:    int redundancy_bytes = 0;
	s32i	a9, sp, 164	# %sfp, tmp8
# @OPUS@\upstream\src\opus_decoder.c:295:    int redundancy=0;
	s32i	a9, sp, 96	# %sfp, tmp8
# @OPUS@\upstream\src\opus_decoder.c:526:       start_band = 17;
	movi.n	a13, 0x11	# start_band,
.L190:
# @OPUS@\upstream\src\opus_decoder.c:534:    ALLOC(pcm_transition_silk, pcm_transition_silk_size, opus_val16);
	l32i	a2, sp, 180	# %sfp,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:536:    if (transition && mode != MODE_CELT_ONLY)
	l32i	a9, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:534:    ALLOC(pcm_transition_silk, pcm_transition_silk_size, opus_val16);
	mov.n	a12, a2	# pcm_transition_silk,
# @OPUS@\upstream\src\opus_decoder.c:536:    if (transition && mode != MODE_CELT_ONLY)
	beqz.n	a9, .L51	#,
# @OPUS@\upstream\src\opus_decoder.c:539:       opus_decode_frame(st, NULL, 0, pcm_transition, IMIN(F5, audiosize), 0);
	l32i	a6, sp, 148	# %sfp, F5
	l32i	a8, sp, 116	# %sfp,
	bge	a8, a6, .L52	#, F5,
	mov.n	a6, a8	# F5,
.L52:
	movi.n	a7, 0	#,
	mov.n	a5, a12	#, pcm_transition_silk
	mov.n	a4, a7	#,
	mov.n	a3, a7	#, tmp4
	mov.n	a2, a14	#, st
	call0	opus_decode_frame		#
# @OPUS@\upstream\src\opus_decoder.c:534:    ALLOC(pcm_transition_silk, pcm_transition_silk_size, opus_val16);
	s32i	a12, sp, 112	# %sfp, pcm_transition_silk
.L51:
# @OPUS@\upstream\src\opus_decoder.c:306:    celt_dec = (CELTDecoder*)((char*)st+st->celt_dec_offset);
	l32i	a9, sp, 172	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:543:    if (bandwidth)
	l32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:306:    celt_dec = (CELTDecoder*)((char*)st+st->celt_dec_offset);
	add.n	a12, a14, a9	# celt_dec, st,
# @OPUS@\upstream\src\opus_decoder.c:543:    if (bandwidth)
	beqz.n	a8, .L53	#,
	movi	a2, -0x44d	# tmp576,
	add.n	a2, a8, a2	# _277,, tmp576
# @OPUS@\upstream\src\opus_decoder.c:547:       switch(bandwidth)
	movi.n	a4, 0x15	# endband,
	bgeui	a2, 4, .L54	# _277,,
	l32r	a3, .LC7	#, tmp577
	slli	a2, a2, 2	# tmp578, _277,
	add.n	a2, a3, a2	# tmp579, tmp577, tmp578
	l32i.n	a4, a2, 0	# CSWTCH$60, endband
.L54:
# @OPUS@\upstream\src\opus_decoder.c:566:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_END_BAND(endband)));
	l32r	a3, .LC8	#,
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	bnez.n	a2, .L42	#,
.L53:
# @OPUS@\upstream\src\opus_decoder.c:568:    MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_CHANNELS(st->stream_channels)));
	l32i.n	a4, a14, 56	# st_282(D)->stream_channels,
	l32r	a3, .LC9	#,
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	mov.n	a5, a2	# _83,
	bnez.n	a2, .L42	# _83,
# @OPUS@\upstream\src\opus_decoder.c:571:    redundant_audio_size = redundancy ? F5*st->channels : ALLOC_NONE;
	l32i	a9, sp, 96	# %sfp,
	beqz.n	a9, .L55	#,
# @OPUS@\upstream\src\opus_decoder.c:571:    redundant_audio_size = redundancy ? F5*st->channels : ALLOC_NONE;
	l32i.n	a2, a14, 8	# st_282(D)->channels, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:572:    ALLOC(redundant_audio, redundant_audio_size, opus_val16);
	l32i	a8, sp, 148	# %sfp,
	mov.n	a4, a5	#, _83
	mull	a2, a8, a2	#,, st_282(D)->channels
	movi.n	a3, 2	#,
	s32i	a5, sp, 196	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:582:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_START_BAND(0)));
	l32r	a8, .LC10	#,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	l32i	a9, sp, 100	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:572:    ALLOC(redundant_audio, redundant_audio_size, opus_val16);
	s32i	a2, sp, 136	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:582:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_START_BAND(0)));
	s32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	l32i	a5, sp, 196	#,
	beqz.n	a9, .L129	#,
# @OPUS@\upstream\src\opus_decoder.c:582:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_START_BAND(0)));
	mov.n	a4, a5	#, _83
	mov.n	a3, a8	#,
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	bnez.n	a2, .L42	# _89,
# @OPUS@\upstream\src\opus_decoder.c:583:       celt_decode_with_ec(celt_dec, data+len, redundancy_bytes,
	l32i	a9, sp, 124	# %sfp,
	l32i	a8, sp, 140	# %sfp,
	l32i	a4, sp, 164	# %sfp,
	l32i	a6, sp, 148	# %sfp,
	l32i	a5, sp, 136	# %sfp,
	add.n	a3, a9, a8	#,,
	s32i.n	a2, sp, 0	#, _89
	mov.n	a7, a2	#, _89
	mov.n	a2, a12	#, celt_dec
	call0	celt_decode_with_ec		#
# @OPUS@\upstream\src\opus_decoder.c:585:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, OPUS_GET_FINAL_RANGE(&redundant_rng)));
	l32r	a3, .LC11	#,
	addi	a4, sp, 76	#,,
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	bnez.n	a2, .L42	#,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	movi.n	a9, 1	#,
	s32i	a9, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	s32i	a9, sp, 128	# %sfp,
	j	.L56		#
.L129:
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	l32i	a9, sp, 100	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	movi.n	a8, 1	#,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	s32i	a9, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	s32i	a8, sp, 128	# %sfp,
.L56:
# @OPUS@\upstream\src\opus_decoder.c:589:    MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_START_BAND(start_band)));
	l32i	a3, sp, 144	# %sfp,
	mov.n	a4, a13	#, start_band
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	s32i	a2, sp, 104	# %sfp,
	bnez.n	a2, .L42	#,
# @OPUS@\upstream\src\opus_decoder.c:591:    if (mode != MODE_SILK_ONLY)
	l32i	a9, sp, 132	# %sfp,
	movi	a2, 0x3e8	# tmp590,
	l32i	a13, a14, 68	# st_282(D)->prev_mode, pretmp_1085
	beq	a9, a2, .L57	#, tmp590,
# @OPUS@\upstream\src\opus_decoder.c:593:       int celt_frame_size = IMIN(F20, frame_size);
	l32i	a6, sp, 108	# %sfp, celt_frame_size
	l32i	a8, sp, 116	# %sfp,
	bge	a8, a6, .L58	#, celt_frame_size,
	mov.n	a6, a8	# celt_frame_size,
.L58:
# @OPUS@\upstream\src\opus_decoder.c:595:       if (mode != st->prev_mode && st->prev_mode > 0 && !st->prev_redundancy)
	srai	a2, a13, 31	# tmp593, pretmp_1085,
	sub	a2, a2, a13	# tmp594, tmp593, pretmp_1085
	bgez	a2, .L59	# tmp594,
	l32i	a9, sp, 132	# %sfp,
	beq	a9, a13, .L59	#, pretmp_1085,
# @OPUS@\upstream\src\opus_decoder.c:595:       if (mode != st->prev_mode && st->prev_mode > 0 && !st->prev_redundancy)
	l32i	a2, a14, 76	# st_282(D)->prev_redundancy, st_282(D)->prev_redundancy
	bnez.n	a2, .L59	# st_282(D)->prev_redundancy,
# @OPUS@\upstream\src\opus_decoder.c:596:          MUST_SUCCEED(celt_decoder_ctl(celt_dec, OPUS_RESET_STATE));
	l32r	a3, .LC12	#,
	mov.n	a2, a12	#, celt_dec
	s32i	a6, sp, 192	#,
	call0	opus_custom_decoder_ctl		#
	l32i	a6, sp, 192	#,
	bnez.n	a2, .L42	#,
.L59:
# @OPUS@\upstream\src\opus_decoder.c:618:       celt_ret = celt_decode_with_ec_dred(celt_dec, decode_fec ? NULL : data,
	l32i	a8, sp, 168	# %sfp,
	l32i	a9, sp, 124	# %sfp,
	movi.n	a3, 0	# tmp905,
	moveqz	a3, a9, a8	# iftmp$30_240,,
	l32i	a8, sp, 184	# %sfp,
	l32i	a5, sp, 120	# %sfp,
	l32i	a4, sp, 140	# %sfp,
	s32i.n	a8, sp, 0	#,
	addi	a7, sp, 16	#,,
	mov.n	a2, a12	#, celt_dec
	call0	celt_decode_with_ec_dred		#
	s32i	a2, sp, 104	# %sfp,
	addi	a13, sp, 72	# tmp846,,
	j	.L61		#
.L57:
# @OPUS@\upstream\src\opus_decoder.c:628:       unsigned char silence[2] = {0xFF, 0xFF};
	movi.n	a2, -1	# tmp605,
# @OPUS@\upstream\src\opus_decoder.c:629:       if (!celt_accum)
	l32i	a9, sp, 156	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:628:       unsigned char silence[2] = {0xFF, 0xFF};
	s8i	a2, sp, 72	# MEM[(unsigned char[2] *)&silence], tmp605
	s8i	a2, sp, 73	# MEM[(unsigned char[2] *)&silence + 1B], tmp605
# @OPUS@\upstream\src\opus_decoder.c:629:       if (!celt_accum)
	beqz.n	a9, .L62	#,
.L65:
# @OPUS@\upstream\src\opus_decoder.c:636:       if (st->prev_mode == MODE_HYBRID && !(redundancy && celt_to_silk && st->prev_redundancy) )
	movi	a2, 0x3e9	# tmp607,
	beq	a13, a2, .L63	# pretmp_1085, tmp607,
	j	.L202		#
.L62:
# @OPUS@\upstream\src\opus_decoder.c:631:          for (i=0;i<frame_size*st->channels;i++)
	l32i.n	a4, a14, 8	# st_282(D)->channels, st_282(D)->channels
	l32i	a8, sp, 116	# %sfp,
	mull	a4, a8, a4	# _184,, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:631:          for (i=0;i<frame_size*st->channels;i++)
	blti	a4, 1, .L65	# _184,,
	l32i	a3, sp, 104	# %sfp,
	l32i	a2, sp, 120	# %sfp,
	slli	a4, a4, 1	#, _184,
	call0	memset		#
	j	.L65		#
.L63:
# @OPUS@\upstream\src\opus_decoder.c:636:       if (st->prev_mode == MODE_HYBRID && !(redundancy && celt_to_silk && st->prev_redundancy) )
	l32i	a9, sp, 96	# %sfp,
	movi.n	a3, 1	# tmp615,
	movi.n	a2, 0	# tmp616,
	moveqz	a2, a3, a9	# tmp614, tmp615,
# @OPUS@\upstream\src\opus_decoder.c:636:       if (st->prev_mode == MODE_HYBRID && !(redundancy && celt_to_silk && st->prev_redundancy) )
	extui	a2, a2, 0, 8	# tmp617, tmp614
	bnez.n	a2, .L66	# tmp617,
	l32i	a8, sp, 100	# %sfp,
	moveqz	a2, a3, a8	# tmp622, tmp615,
	bnez.n	a2, .L66	# tmp622,
# @OPUS@\upstream\src\opus_decoder.c:636:       if (st->prev_mode == MODE_HYBRID && !(redundancy && celt_to_silk && st->prev_redundancy) )
	l32i	a2, a14, 76	# st_282(D)->prev_redundancy, st_282(D)->prev_redundancy
	beqz.n	a2, .L66	# st_282(D)->prev_redundancy,
.L202:
	addi	a13, sp, 72	# tmp846,,
	j	.L61		#
.L66:
# @OPUS@\upstream\src\opus_decoder.c:638:          MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_START_BAND(0)));
	l32i	a3, sp, 144	# %sfp,
	movi.n	a4, 0	#,
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	beqz.n	a2, .L67	# _107,
	j	.L69		#
.L67:
# @OPUS@\upstream\src\opus_decoder.c:639:          celt_decode_with_ec(celt_dec, silence, 2, pcm, F2_5, NULL, celt_accum);
	l32i	a8, sp, 184	# %sfp,
	addi	a13, sp, 72	# tmp846,,
	l32i	a5, sp, 120	# %sfp,
	mov.n	a7, a2	#, _107
	s32i.n	a8, sp, 0	#,
	mov.n	a6, a15	#, F2_5
	movi.n	a4, 2	#,
	mov.n	a3, a13	#, tmp846
	mov.n	a2, a12	#, celt_dec
	call0	celt_decode_with_ec		#
.L61:
# @OPUS@\upstream\src\opus_decoder.c:643:    if (mode != MODE_CELT_ONLY && !celt_accum)
	l32i	a9, sp, 160	# %sfp,
	bnez.n	a9, .L68	#,
.L71:
# @OPUS@\upstream\src\opus_decoder.c:656:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_GET_MODE(&celt_mode)));
	l32r	a3, .LC13	#,
	mov.n	a4, a13	#, tmp846
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	mov.n	a8, a2	# _119,
	beqz.n	a2, .L192	# _119,
	j	.L69		#
.L68:
# @OPUS@\upstream\src\opus_decoder.c:646:       for (i=0;i<frame_size*st->channels;i++)
	l32i.n	a2, a14, 8	# st_282(D)->channels, st_282(D)->channels
	l32i	a8, sp, 116	# %sfp,
	mull	a2, a8, a2	# _871,, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:646:       for (i=0;i<frame_size*st->channels;i++)
	blti	a2, 1, .L71	# _871,,
	l32i	a3, sp, 120	# %sfp, ivtmp$151
	slli	a2, a2, 1	# tmp629, _871,
	l32r	a4, .LC1	#, tmp849
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\arch.h:157:    return x > 32767 ? 32767 : x < -32768 ? -32768 : (opus_int16)x;
	l32r	a10, .LC2	#, tmp1085
	l32i	a5, sp, 188	# %sfp, ivtmp$152
	add.n	a7, a2, a3	# _958, tmp629, ivtmp$151
.L73:
# @OPUS@\upstream\src\opus_decoder.c:647:          pcm[i] = SAT16(ADD32(pcm[i], pcm_silk[i]));
	l16si	a8, a3, 0	# MEM[base: _964, offset: 0B], _839
	l16si	a2, a5, 0	# MEM[base: _962, offset: 0B], _806
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\arch.h:157:    return x > 32767 ? 32767 : x < -32768 ? -32768 : (opus_int16)x;
	mov.n	a6, a4	# iftmp$46_256, tmp849
# @OPUS@\upstream\src\opus_decoder.c:647:          pcm[i] = SAT16(ADD32(pcm[i], pcm_silk[i]));
	add.n	a2, a2, a8	# _258, _806, _839
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\arch.h:157:    return x > 32767 ? 32767 : x < -32768 ? -32768 : (opus_int16)x;
	slli	a8, a2, 16	# tmp637, _258,
	blt	a4, a2, .L72	# tmp849, _258,
	blt	a2, a10, .L132	# _258, tmp1085,
	srai	a6, a8, 16	# iftmp$46_256, tmp637,
	j	.L72		#
.L132:
	mov.n	a6, a10	# iftmp$46_256, tmp1085
.L72:
# @OPUS@\upstream\src\opus_decoder.c:647:          pcm[i] = SAT16(ADD32(pcm[i], pcm_silk[i]));
	s16i	a6, a3, 0	# MEM[base: _964, offset: 0B], iftmp$46_256
	addi.n	a3, a3, 2	# ivtmp$151, ivtmp$151,
	addi.n	a5, a5, 2	# ivtmp$152, ivtmp$152,
# @OPUS@\upstream\src\opus_decoder.c:646:       for (i=0;i<frame_size*st->channels;i++)
	bne	a7, a3, .L73	# _958, ivtmp$151,
	j	.L71		#
.L69:
# @OPUS@\upstream\src\opus_decoder.c:656:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_GET_MODE(&celt_mode)));
	l32i	a2, sp, 64	# _saved_stack,
	l32i	a3, sp, 68	# _saved_stack,
	movi.n	a9, -3	#,
	s32i	a9, sp, 104	# %sfp,
	call0	yoradio_opus_scratch_restore		#
	j	.L1		#
.L192:
# @OPUS@\upstream\src\opus_decoder.c:661:    if (redundancy && !celt_to_silk)
	l32i	a9, sp, 100	# %sfp,
	movi.n	a2, 1	# tmp641,
	movnez	a2, a8, a9	# tmp640, _119,
# @OPUS@\upstream\src\opus_decoder.c:661:    if (redundancy && !celt_to_silk)
	l32i	a9, sp, 128	# %sfp,
	and	a2, a9, a2	#,, tmp640
	s32i	a2, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:657:       window = celt_mode->window;
	l32i	a2, sp, 72	# celt_mode, celt_mode
# @OPUS@\upstream\src\opus_decoder.c:661:    if (redundancy && !celt_to_silk)
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:657:       window = celt_mode->window;
	l32i.n	a2, a2, 52	# celt_mode$35_120->window,
	s32i	a2, sp, 108	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:661:    if (redundancy && !celt_to_silk)
	beqz.n	a9, .L74	#,
# @OPUS@\upstream\src\opus_decoder.c:663:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, OPUS_RESET_STATE));
	l32r	a3, .LC12	#,
	mov.n	a2, a12	#, celt_dec
	s32i	a8, sp, 200	#,
	call0	opus_custom_decoder_ctl		#
	l32i	a8, sp, 200	#,
	bnez.n	a2, .L42	#,
# @OPUS@\upstream\src\opus_decoder.c:664:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, CELT_SET_START_BAND(0)));
	l32i	a3, sp, 144	# %sfp,
	mov.n	a4, a8	#, _119
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	l32i	a8, sp, 200	#,
	bnez.n	a2, .L42	#,
# @OPUS@\upstream\src\opus_decoder.c:666:       celt_decode_with_ec(celt_dec, data+len, redundancy_bytes, redundant_audio, F5, NULL, 0);
	l32i	a9, sp, 124	# %sfp,
	l32i	a2, sp, 140	# %sfp,
	l32i	a6, sp, 148	# %sfp,
	l32i	a5, sp, 136	# %sfp,
	l32i	a4, sp, 164	# %sfp,
	add.n	a3, a9, a2	#,,
	mov.n	a7, a8	#, _119
	s32i.n	a8, sp, 0	#, _119
	mov.n	a2, a12	#, celt_dec
	call0	celt_decode_with_ec		#
# @OPUS@\upstream\src\opus_decoder.c:667:       MUST_SUCCEED(celt_decoder_ctl(celt_dec, OPUS_GET_FINAL_RANGE(&redundant_rng)));
	l32r	a3, .LC11	#,
	addi	a4, sp, 76	#,,
	mov.n	a2, a12	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	mov.n	a10, a2	# _127,
	bnez.n	a2, .L42	# _127,
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	l32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	l32i.n	a12, a14, 8	# st_282(D)->channels, _128
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	sub	a2, a9, a15	# tmp650,, F2_5
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	mull	a4, a2, a12	# tmp651, tmp650, _128
# @OPUS@\upstream\src\opus_decoder.c:245:    int inc = 48000/Fs;
	l32i.n	a3, a14, 12	# st_282(D)->Fs,
	l32r	a2, .LC14	#,
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	slli	a4, a4, 1	#, tmp651,
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	mull	a13, a12, a15	# tmp652, _128, F2_5
# @OPUS@\upstream\src\opus_decoder.c:245:    int inc = 48000/Fs;
	s32i	a10, sp, 192	#,
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	s32i	a4, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:245:    int inc = 48000/Fs;
	call0	__divsi3		#
# @OPUS@\upstream\src\opus_decoder.c:668:       smooth_fade(pcm+st->channels*(frame_size-F2_5), redundant_audio+st->channels*F2_5,
	slli	a13, a13, 1	# _136, tmp652,
# @OPUS@\upstream\src\opus_decoder.c:246:    for (c=0;c<channels;c++)
	l32i	a8, sp, 200	#,
	l32i	a10, sp, 192	#,
	blti	a12, 1, .L74	# _128,,
	blti	a15, 1, .L74	# F2_5,,
	slli	a11, a12, 1	# _972, _128,
	l32i	a6, sp, 136	# %sfp,
	add.n	a3, a13, a11	# tmp656, _136, _972
	l32i	a9, sp, 136	# %sfp,
	l32i	a4, sp, 120	# %sfp,
	l32i	a5, sp, 96	# %sfp,
	add.n	a3, a6, a3	# _971,, tmp656
	add.n	a13, a9, a13	# ivtmp$146,, _136
	s32i	a14, sp, 156	# %sfp, st
	add.n	a9, a4, a5	# ivtmp$147,,
	slli	a12, a2, 1	# _1007, tmp655,
	l32r	a4, .LC1	#, tmp849
	s32i	a8, sp, 124	# %sfp, _119
	mov.n	a14, a3	# _971, _971
	j	.L75		#
.L76:
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	l16si	a2, a8, 0	# MEM[base: _987, offset: 0B], _444
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	l16ui	a9, a5, 0	# MEM[base: _985, offset: 0B],
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	mull	a2, a2, a2	# tmp659, _444, _444
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	slli	a2, a2, 1	# tmp661, tmp659,
	srai	a2, a2, 16	# w, tmp661,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	sub	a3, a4, a2	# tmp662, tmp849, w
	mul16s	a3, a9, a3	# tmp664,, tmp662
	l16ui	a9, a7, 0	# MEM[base: _986, offset: 0B],
	add.n	a8, a8, a12	# ivtmp$140, ivtmp$140, _1007
	mul16s	a2, a9, a2	# tmp666,, w
	add.n	a7, a7, a11	# ivtmp$141, ivtmp$141, _972
	add.n	a3, a3, a2	# tmp668, tmp664, tmp666
	srai	a3, a3, 15	# tmp669, tmp668,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	s16i	a3, a5, 0	# MEM[base: _985, offset: 0B], tmp669
	add.n	a5, a5, a11	# ivtmp$142, ivtmp$142, _972
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	bne	a15, a6, .L76	# F2_5, i,
	l32i	a9, sp, 96	# %sfp, ivtmp$147
	addi.n	a13, a13, 2	# ivtmp$146, ivtmp$146,
	addi.n	a9, a9, 2	# ivtmp$147, ivtmp$147,
# @OPUS@\upstream\src\opus_decoder.c:246:    for (c=0;c<channels;c++)
	beq	a14, a13, .L196	# _971, ivtmp$146,
.L75:
	l32i	a8, sp, 108	# %sfp, ivtmp$140
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\arch.h:157:    return x > 32767 ? 32767 : x < -32768 ? -32768 : (opus_int16)x;
	mov.n	a5, a9	# ivtmp$142, ivtmp$147
	mov.n	a7, a13	# ivtmp$141, ivtmp$146
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	mov.n	a6, a10	# i, _127
	s32i	a9, sp, 96	# %sfp, ivtmp$147
	j	.L76		#
.L196:
	l32i	a8, sp, 124	# %sfp, _119
	l32i	a14, sp, 156	# %sfp, st
.L74:
# @OPUS@\upstream\src\opus_decoder.c:674:    if (redundancy && celt_to_silk && (st->prev_mode != MODE_SILK_ONLY || st->prev_redundancy))
	l32i	a9, sp, 152	# %sfp,
	beqz.n	a9, .L77	#,
# @OPUS@\upstream\src\opus_decoder.c:674:    if (redundancy && celt_to_silk && (st->prev_mode != MODE_SILK_ONLY || st->prev_redundancy))
	l32i	a3, a14, 68	# st_282(D)->prev_mode, st_282(D)->prev_mode
	movi	a2, 0x3e8	# tmp670,
	beq	a3, a2, .L78	# st_282(D)->prev_mode, tmp670,
.L80:
# @OPUS@\upstream\src\opus_decoder.c:676:       for (c=0;c<st->channels;c++)
	l32i.n	a11, a14, 8	# st_282(D)->channels, _41
# @OPUS@\upstream\src\opus_decoder.c:676:       for (c=0;c<st->channels;c++)
	blti	a11, 1, .L77	# _41,,
	blti	a15, 1, .L77	# F2_5,,
	l32i	a6, sp, 136	# %sfp, ivtmp$135
	slli	a12, a11, 1	# _1040, _41,
	l32i	a7, sp, 120	# %sfp, ivtmp$136
	add.n	a10, a6, a12	# _1011, ivtmp$135, _1040
	j	.L79		#
.L78:
# @OPUS@\upstream\src\opus_decoder.c:674:    if (redundancy && celt_to_silk && (st->prev_mode != MODE_SILK_ONLY || st->prev_redundancy))
	l32i	a2, a14, 76	# st_282(D)->prev_redundancy, st_282(D)->prev_redundancy
	bnez.n	a2, .L80	# st_282(D)->prev_redundancy,
	j	.L77		#
.L81:
# @OPUS@\upstream\src\opus_decoder.c:679:             pcm[st->channels*i+c] = redundant_audio[st->channels*i+c];
	l16si	a5, a3, 0	# MEM[base: _1022, offset: 0B], _147
# @OPUS@\upstream\src\opus_decoder.c:678:          for (i=0;i<F2_5;i++)
	addi.n	a2, a2, 1	# i, i,
# @OPUS@\upstream\src\opus_decoder.c:679:             pcm[st->channels*i+c] = redundant_audio[st->channels*i+c];
	s16i	a5, a4, 0	# MEM[base: _1021, offset: 0B], _147
	add.n	a3, a3, a12	# ivtmp$129, ivtmp$129, _1040
	add.n	a4, a4, a12	# ivtmp$130, ivtmp$130, _1040
# @OPUS@\upstream\src\opus_decoder.c:678:          for (i=0;i<F2_5;i++)
	bne	a15, a2, .L81	# F2_5, i,
	addi.n	a6, a6, 2	# ivtmp$135, ivtmp$135,
	addi.n	a7, a7, 2	# ivtmp$136, ivtmp$136,
# @OPUS@\upstream\src\opus_decoder.c:676:       for (c=0;c<st->channels;c++)
	beq	a10, a6, .L82	# _1011, ivtmp$135,
.L79:
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	mov.n	a4, a7	# ivtmp$130, ivtmp$136
	mov.n	a3, a6	# ivtmp$129, ivtmp$135
# @OPUS@\upstream\src\opus_decoder.c:678:          for (i=0;i<F2_5;i++)
	mov.n	a2, a8	# i, _119
	j	.L81		#
.L83:
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	l16si	a3, a11, 0	# MEM[base: _1055, offset: 0B], _477
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	l16ui	a8, a10, 0	# MEM[base: _1052, offset: 0B],
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	mull	a3, a3, a3	# tmp677, _477, _477
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	slli	a3, a3, 1	# tmp679, tmp677,
	srai	a3, a3, 16	# w, tmp679,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	sub	a5, a4, a3	# tmp680, tmp849, w
	mul16s	a5, a8, a5	# tmp682,, tmp680
	l16ui	a8, a6, 0	# MEM[base: _1054, offset: 0B],
	add.n	a11, a11, a2	# ivtmp$116, ivtmp$116, _1075
	mul16s	a3, a8, a3	# tmp684,, w
	add.n	a10, a10, a12	# ivtmp$118, ivtmp$118, _1040
	add.n	a5, a5, a3	# tmp686, tmp682, tmp684
	srai	a5, a5, 15	# tmp687, tmp686,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	s16i	a5, a6, 0	# MEM[base: _1054, offset: 0B], tmp687
	add.n	a6, a6, a12	# ivtmp$117, ivtmp$117, _1040
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	bne	a15, a7, .L83	# F2_5, i,
	addi.n	a13, a13, 2	# ivtmp$123, ivtmp$123,
	l32i	a8, sp, 96	# %sfp, _119
	addi.n	a9, a9, 2	# ivtmp$124, ivtmp$124,
# @OPUS@\upstream\src\opus_decoder.c:246:    for (c=0;c<channels;c++)
	beq	a14, a13, .L197	# _1039, ivtmp$123,
.L118:
	l32i	a11, sp, 108	# %sfp, ivtmp$116
# @OPUS@\upstream\src\opus_decoder.c:678:          for (i=0;i<F2_5;i++)
	mov.n	a10, a9	# ivtmp$118, ivtmp$124
	mov.n	a6, a13	# ivtmp$117, ivtmp$123
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	mov.n	a7, a8	# i, _119
	s32i	a8, sp, 96	# %sfp, _119
	j	.L83		#
.L197:
	l32i	a14, sp, 124	# %sfp, st
.L77:
# @OPUS@\upstream\src\opus_decoder.c:684:    if (transition)
	l32i	a9, sp, 176	# %sfp,
	beqz.n	a9, .L84	#,
	l32i.n	a3, a14, 12	# st_282(D)->Fs,
	l32r	a2, .LC14	#,
	l32i.n	a12, a14, 8	# st_282(D)->channels, pretmp_1105
	s32i	a8, sp, 200	#,
	call0	__divsi3		#
# @OPUS@\upstream\src\opus_decoder.c:686:       if (audiosize >= F5)
	l32i	a9, sp, 116	# %sfp,
	l32i	a3, sp, 148	# %sfp,
	l32i	a8, sp, 200	#,
	blt	a9, a3, .L85	#,,
# @OPUS@\upstream\src\opus_decoder.c:688:          for (i=0;i<st->channels*F2_5;i++)
	mull	a7, a15, a12	# _955, F2_5, pretmp_1105
# @OPUS@\upstream\src\opus_decoder.c:688:          for (i=0;i<st->channels*F2_5;i++)
	bgei	a7, 1, .L86	# _955,,
	slli	a3, a7, 1	# _163, _955,
.L94:
# @OPUS@\upstream\src\opus_decoder.c:246:    for (c=0;c<channels;c++)
	blti	a12, 1, .L84	# pretmp_1105,,
	blti	a15, 1, .L84	# F2_5,,
	l32i	a9, sp, 120	# %sfp,
	slli	a11, a12, 1	# _387, pretmp_1105,
	l32i	a5, sp, 112	# %sfp,
	add.n	a4, a9, a11	# tmp691,, _387
	add.n	a13, a9, a3	# ivtmp$86,, _163
	add.n	a9, a5, a3	# ivtmp$87,, _163
	add.n	a3, a4, a3	#, tmp691, _163
	s32i	a14, sp, 124	# %sfp, st
	s32i	a3, sp, 112	# %sfp,
	slli	a12, a2, 1	# _855, _1107,
	l32r	a4, .LC1	#, tmp849
	l32i	a14, sp, 108	# %sfp, window
	j	.L87		#
.L86:
	l32i	a9, sp, 120	# %sfp,
	movi.n	a5, 1	# tmp693,
	addi.n	a3, a9, 4	# tmp692,,
	l32i	a9, sp, 112	# %sfp,
	bgeu	a9, a3, .L89	#, tmp692,
	movi.n	a5, 0	# tmp693,
.L89:
	l32i	a9, sp, 112	# %sfp,
	movi.n	a3, 1	# tmp696,
	addi.n	a4, a9, 4	# tmp695,,
	l32i	a9, sp, 120	# %sfp,
	bgeu	a9, a4, .L90	#, tmp695,
	movi.n	a3, 0	# tmp696,
.L90:
	addi.n	a4, a7, -1	# tmp699, _955,
	movi.n	a6, 0xb	# tmp702,
	or	a3, a5, a3	# tmp698, tmp693, tmp696
	movi.n	a5, 1	# tmp700,
	bltu	a6, a4, .L91	# tmp702, tmp699,
	movi.n	a5, 0	# tmp700,
.L91:
	and	a3, a3, a5	# tmp704, tmp698, tmp700
	bbci	a3, 0, .L88	# tmp704,,
	l32i	a9, sp, 120	# %sfp,
	l32i	a4, sp, 112	# %sfp,
	or	a3, a9, a4	# tmp707,,
	extui	a3, a3, 0, 2	# tmp708, tmp707,
	bnez.n	a3, .L88	# tmp708,
	srli	a6, a7, 1	# bnd$65, _955,
	slli	a6, a6, 2	# tmp715, bnd$65,
	mov.n	a3, a9	# ivtmp$99,
	add.n	a6, a6, a9	# _1139, tmp715,
.L92:
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	l32i.n	a5, a4, 0	# MEM[base: _1143, offset: 0B], vect__159$70
	addi.n	a4, a4, 4	# ivtmp$101, ivtmp$101,
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	s32i.n	a5, a3, 0	# MEM[base: _1142, offset: 0B], vect__159$70
	addi.n	a3, a3, 4	# ivtmp$99, ivtmp$99,
	bne	a6, a3, .L92	# _1139, ivtmp$99,
	movi.n	a4, -2	# tmp716,
	and	a4, a7, a4	# niters_vector_mult_vf$66, _955, tmp716
	slli	a3, a7, 1	# _163, _955,
	beq	a4, a7, .L94	# niters_vector_mult_vf$66, _955,
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	l32i	a9, sp, 112	# %sfp,
	slli	a4, a4, 1	# _1188, niters_vector_mult_vf$66,
	add.n	a5, a9, a4	# tmp717,, _1188
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	l32i	a9, sp, 120	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	l16si	a5, a5, 0	# *_1187, _1185
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	add.n	a4, a9, a4	# tmp720,, _1188
	s16i	a5, a4, 0	# *_1186, _1185
	j	.L94		#
.L88:
	l32i	a4, sp, 112	# %sfp, ivtmp$92
	slli	a3, a7, 1	# _163, _955,
	l32i	a5, sp, 120	# %sfp, ivtmp$93
	add.n	a7, a4, a3	# _1150, ivtmp$92, _163
.L96:
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	l16si	a6, a4, 0	# MEM[base: _406, offset: 0B], _1204
	addi.n	a4, a4, 2	# ivtmp$92, ivtmp$92,
# @OPUS@\upstream\src\opus_decoder.c:689:             pcm[i] = pcm_transition[i];
	s16i	a6, a5, 0	# MEM[base: _1257, offset: 0B], _1204
	addi.n	a5, a5, 2	# ivtmp$93, ivtmp$93,
# @OPUS@\upstream\src\opus_decoder.c:688:          for (i=0;i<st->channels*F2_5;i++)
	bne	a7, a4, .L96	# _1150, ivtmp$92,
	j	.L94		#
.L98:
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	l16si	a2, a10, 0	# MEM[base: _110, offset: 0B], _510
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	l16ui	a8, a7, 0	# MEM[base: _113, offset: 0B],
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	mull	a2, a2, a2	# tmp726, _510, _510
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	slli	a2, a2, 1	# tmp728, tmp726,
	srai	a2, a2, 16	# w, tmp728,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	sub	a3, a4, a2	# tmp729, tmp849, w
	mul16s	a3, a8, a3	# tmp731,, tmp729
	l16ui	a8, a5, 0	# MEM[base: _111, offset: 0B],
	add.n	a10, a10, a12	# ivtmp$79, ivtmp$79, _855
	mul16s	a2, a8, a2	# tmp733,, w
	add.n	a7, a7, a11	# ivtmp$81, ivtmp$81, _387
	add.n	a3, a3, a2	# tmp735, tmp731, tmp733
	srai	a3, a3, 15	# tmp736, tmp735,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	s16i	a3, a5, 0	# MEM[base: _111, offset: 0B], tmp736
	add.n	a5, a5, a11	# ivtmp$80, ivtmp$80, _387
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	bne	a15, a6, .L98	# F2_5, i,
# @OPUS@\upstream\src\opus_decoder.c:246:    for (c=0;c<channels;c++)
	l32i	a2, sp, 112	# %sfp,
	addi.n	a13, a13, 2	# ivtmp$86, ivtmp$86,
	l32i	a8, sp, 96	# %sfp, _119
	addi.n	a9, a9, 2	# ivtmp$87, ivtmp$87,
	beq	a13, a2, .L198	# ivtmp$86,,
.L87:
	mov.n	a10, a14	# ivtmp$79, window
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	mov.n	a7, a9	# ivtmp$81, ivtmp$87
	mov.n	a5, a13	# ivtmp$80, ivtmp$86
	mov.n	a6, a8	# i, _119
	s32i	a8, sp, 96	# %sfp, _119
	j	.L98		#
.L85:
# @OPUS@\upstream\src\opus_decoder.c:246:    for (c=0;c<channels;c++)
	blti	a12, 1, .L84	# pretmp_1105,,
	blti	a15, 1, .L84	# F2_5,,
	l32i	a13, sp, 120	# %sfp, ivtmp$111
	slli	a11, a12, 1	# _1081, pretmp_1105,
	add.n	a3, a11, a13	# _1079, _1081, ivtmp$111
	l32i	a9, sp, 112	# %sfp, ivtmp$112
	slli	a12, a2, 1	# _1129, _1107,
	s32i	a14, sp, 112	# %sfp, st
	l32r	a4, .LC1	#, tmp849
	mov.n	a14, a3	# _1079, _1079
	j	.L99		#
.L100:
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	l16si	a2, a10, 0	# MEM[base: _1095, offset: 0B], _543
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	l16ui	a8, a7, 0	# MEM[base: _1092, offset: 0B],
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	mull	a2, a2, a2	# tmp739, _543, _543
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\src\opus_decoder.c:250:          opus_val16 w = MULT16_16_Q15(window[i*inc], window[i*inc]);
	slli	a2, a2, 1	# tmp741, tmp739,
	srai	a2, a2, 16	# w, tmp741,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	sub	a3, a4, a2	# tmp742, tmp849, w
	mul16s	a3, a8, a3	# tmp744,, tmp742
	l16ui	a8, a5, 0	# MEM[base: _1094, offset: 0B],
	add.n	a10, a10, a12	# ivtmp$104, ivtmp$104, _1129
	mul16s	a2, a8, a2	# tmp746,, w
	add.n	a7, a7, a11	# ivtmp$106, ivtmp$106, _1081
	add.n	a3, a3, a2	# tmp748, tmp744, tmp746
	srai	a3, a3, 15	# tmp749, tmp748,
# @OPUS@\upstream\src\opus_decoder.c:251:          out[i*channels+c] = SHR32(MAC16_16(MULT16_16(w,in2[i*channels+c]),
	s16i	a3, a5, 0	# MEM[base: _1094, offset: 0B], tmp749
	add.n	a5, a5, a11	# ivtmp$105, ivtmp$105, _1081
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	bne	a15, a6, .L100	# F2_5, i,
	addi.n	a13, a13, 2	# ivtmp$111, ivtmp$111,
	l32i	a8, sp, 96	# %sfp, _119
	addi.n	a9, a9, 2	# ivtmp$112, ivtmp$112,
# @OPUS@\upstream\src\opus_decoder.c:246:    for (c=0;c<channels;c++)
	beq	a14, a13, .L199	# _1079, ivtmp$111,
.L99:
	l32i	a10, sp, 108	# %sfp, ivtmp$104
# @OPUS@\upstream\src\opus_decoder.c:248:       for (i=0;i<overlap;i++)
	mov.n	a7, a9	# ivtmp$106, ivtmp$112
	mov.n	a5, a13	# ivtmp$105, ivtmp$111
	mov.n	a6, a8	# i, _119
	s32i	a8, sp, 96	# %sfp, _119
	j	.L100		#
.L198:
	l32i	a14, sp, 124	# %sfp, st
	j	.L84		#
.L199:
	l32i	a14, sp, 112	# %sfp, st
.L84:
# @OPUS@\upstream\src\opus_decoder.c:705:    if(st->decode_gain)
	l32i.n	a2, a14, 44	# st_282(D)->decode_gain, _169
# @OPUS@\upstream\src\opus_decoder.c:705:    if(st->decode_gain)
	bnez.n	a2, .L101	# _169,
.L106:
# @OPUS@\upstream\src\opus_decoder.c:717:    if (len <= 1)
	l32i	a9, sp, 140	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:718:       st->rangeFinal = 0;
	movi.n	a4, 0	# _195,
# @OPUS@\upstream\src\opus_decoder.c:717:    if (len <= 1)
	bgei	a9, 2, .L193	#,,
	j	.L102		#
.L101:
# @OPUS@\upstream\src\opus_decoder.c:708:       gain = celt_exp2(MULT16_16_P15(QCONST16(6.48814081e-4f, 25), st->decode_gain));
	l32r	a3, .LC15	#, tmp751
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:245:    if (integer>14)
	movi.n	a4, 0xe	# tmp758,
# @OPUS@\upstream\src\opus_decoder.c:708:       gain = celt_exp2(MULT16_16_P15(QCONST16(6.48814081e-4f, 25), st->decode_gain));
	mul16s	a2, a2, a3	# tmp750, _169, tmp751
	addmi	a2, a2, 0x4000	# tmp752, tmp750,
	srai	a2, a2, 15	# tmp753, tmp752,
# @OPUS@\upstream\src\opus_decoder.c:708:       gain = celt_exp2(MULT16_16_P15(QCONST16(6.48814081e-4f, 25), st->decode_gain));
	slli	a2, a2, 16	# tmp754, tmp753,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:244:    integer = SHR16(x,10);
	srai	a3, a2, 26	# _571, tmp754,
# @OPUS@\upstream\src\opus_decoder.c:708:       gain = celt_exp2(MULT16_16_P15(QCONST16(6.48814081e-4f, 25), st->decode_gain));
	srai	a2, a2, 16	# _175, tmp754,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:245:    if (integer>14)
	blt	a4, a3, .L134	# tmp758, _571,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:247:    else if (integer < -15)
	movi.n	a4, -0xf	# tmp761,
	blt	a3, a4, .L104	# _571, tmp761,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:249:    frac = celt_exp2_frac(x-SHL16(integer,10));
	extui	a4, a3, 0, 16	# _571, _571
	slli	a4, a4, 10	# tmp764, _571,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:249:    frac = celt_exp2_frac(x-SHL16(integer,10));
	sub	a2, a2, a4	# tmp766, _175, tmp764
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:230:    frac = SHL16(x, 4);
	slli	a2, a2, 20	# tmp769, tmp766,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	l32r	a4, .LC16	#, tmp771
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:230:    frac = SHL16(x, 4);
	srai	a2, a2, 16	# frac, tmp769,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	mul16s	a4, a2, a4	# tmp770, frac, tmp771
	l32r	a5, .LC17	#, tmp775
	srai	a4, a4, 15	# tmp772, tmp770,
	add.n	a4, a4, a5	# tmp774, tmp772, tmp775
	mul16s	a4, a4, a2	# tmp776, tmp774, frac
	l32r	a5, .LC18	#, tmp780
	srai	a4, a4, 15	# tmp777, tmp776,
	add.n	a4, a4, a5	# tmp779, tmp777, tmp780
	mul16s	a2, a4, a2	# tmp781, tmp779, frac
	l32r	a4, .LC19	#, tmp785
	srai	a2, a2, 15	# tmp782, tmp781,
	add.n	a2, a2, a4	# tmp784, tmp782, tmp785
	slli	a2, a2, 16	# tmp786, tmp784,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	movi.n	a4, -2	# tmp787,
	sub	a4, a4, a3	# _598, tmp787, _571
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	srai	a2, a2, 16	# _596, tmp786,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	ssr	a4	# _598
	sra	a8, a2	# _119, _596
	bgei	a4, 1, .L104	# _598,,
.L105:
	addi.n	a3, a3, 2	# tmp788, _571,
	ssl	a3	# tmp788
	sll	a8, a2	# _119, _596
	j	.L104		#
.L134:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\mathops.h:246:       return 0x7f000000;
	l32r	a8, .LC3	#, _119
.L104:
# @OPUS@\upstream\src\opus_decoder.c:709:       for (i=0;i<frame_size*st->channels;i++)
	l32i.n	a2, a14, 8	# st_282(D)->channels, st_282(D)->channels
	l32i	a9, sp, 116	# %sfp,
	mull	a2, a9, a2	# _912,, st_282(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:709:       for (i=0;i<frame_size*st->channels;i++)
	blti	a2, 1, .L106	# _912,,
	l32i	a3, sp, 120	# %sfp, ivtmp$75
	slli	a2, a2, 1	# tmp790, _912,
	l32r	a4, .LC1	#, tmp849
	l32r	a7, .LC20	#, tmp850
# @OPUS@\upstream\src\opus_decoder.c:713:          pcm[i] = SATURATE(x, 32767);
	l32r	a9, .LC21	#, tmp1082
# @OPUS@\upstream\src\opus_decoder.c:712:          x = MULT16_32_P16(pcm[i],gain);
	srai	a6, a8, 16	# _182, _119,
	extui	a10, a8, 0, 16	# _1101, _119,
	add.n	a5, a3, a2	# _159, ivtmp$75, tmp790
.L110:
	l16si	a8, a3, 0	# MEM[base: _265, offset: 0B], _379
	mull	a2, a8, a10	# tmp793, _379, _1101
	mull	a8, a6, a8	# tmp797, _182, _379
	add.n	a2, a2, a7	# tmp794, tmp793, tmp850
	srai	a2, a2, 16	# tmp796, tmp794,
# @OPUS@\upstream\src\opus_decoder.c:712:          x = MULT16_32_P16(pcm[i],gain);
	add.n	a2, a2, a8	# x, tmp796, tmp797
# @OPUS@\upstream\src\opus_decoder.c:713:          pcm[i] = SATURATE(x, 32767);
	mov.n	a8, a2	# x, x
# @OPUS@\upstream\src\opus_decoder.c:713:          pcm[i] = SATURATE(x, 32767);
	blt	a4, a2, .L107	# tmp849, x,
# @OPUS@\upstream\src\opus_decoder.c:713:          pcm[i] = SATURATE(x, 32767);
	bge	a2, a9, .L108	# x, tmp1082,
	mov.n	a8, a9	# x, tmp1082
.L108:
# @OPUS@\upstream\src\opus_decoder.c:713:          pcm[i] = SATURATE(x, 32767);
	s16i	a8, a3, 0	# MEM[base: _265, offset: 0B], x
	addi.n	a3, a3, 2	# ivtmp$75, ivtmp$75,
# @OPUS@\upstream\src\opus_decoder.c:709:       for (i=0;i<frame_size*st->channels;i++)
	bne	a5, a3, .L110	# _159, ivtmp$75,
	j	.L106		#
.L107:
# @OPUS@\upstream\src\opus_decoder.c:713:          pcm[i] = SATURATE(x, 32767);
	s16i	a4, a3, 0	# MEM[base: _265, offset: 0B], tmp849
	addi.n	a3, a3, 2	# ivtmp$75, ivtmp$75,
# @OPUS@\upstream\src\opus_decoder.c:709:       for (i=0;i<frame_size*st->channels;i++)
	bne	a5, a3, .L110	# _159, ivtmp$75,
	j	.L106		#
.L193:
# @OPUS@\upstream\src\opus_decoder.c:720:       st->rangeFinal = dec.rng ^ redundant_rng;
	l32i.n	a4, sp, 44	# dec.rng, dec.rng
	l32i	a2, sp, 76	# redundant_rng, redundant_rng
	xor	a4, a4, a2	# _195, dec.rng, redundant_rng
.L102:
# @OPUS@\upstream\src\opus_decoder.c:722:    st->prev_mode = mode;
	l32i	a8, sp, 132	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:723:    st->prev_redundancy = redundancy && !celt_to_silk;
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:731:    RESTORE_STACK;
	l32i	a2, sp, 64	# _saved_stack,
	l32i	a3, sp, 68	# _saved_stack,
# @OPUS@\upstream\src\opus_decoder.c:722:    st->prev_mode = mode;
	s32i	a8, a14, 68	# st_282(D)->prev_mode,
# @OPUS@\upstream\src\opus_decoder.c:723:    st->prev_redundancy = redundancy && !celt_to_silk;
	s32i	a9, a14, 76	# st_282(D)->prev_redundancy,
	s32i	a4, a14, 84	# st_282(D)->rangeFinal, _195
# @OPUS@\upstream\src\opus_decoder.c:731:    RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\src\opus_decoder.c:732:    return celt_ret < 0 ? celt_ret : audiosize;
	l32i	a9, sp, 104	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	movltz	a8, a9, a9	#,,
	s32i	a8, sp, 104	# %sfp,
	j	.L1		#
.L55:
	mov.n	a4, a9	#,
# @OPUS@\upstream\src\opus_decoder.c:572:    ALLOC(redundant_audio, redundant_audio_size, opus_val16);
	mov.n	a2, a9	#, tmp4
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	l32i	a8, sp, 96	# %sfp,
	l32r	a9, .LC10	#,
# @OPUS@\upstream\src\opus_decoder.c:572:    ALLOC(redundant_audio, redundant_audio_size, opus_val16);
	s32i	a2, sp, 136	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	s32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:575:    if (redundancy && celt_to_silk)
	s32i	a8, sp, 128	# %sfp,
	s32i	a9, sp, 144	# %sfp,
	j	.L56		#
.L50:
	mov.n	a4, a8	#,
# @OPUS@\upstream\src\opus_decoder.c:534:    ALLOC(pcm_transition_silk, pcm_transition_silk_size, opus_val16);
	mov.n	a2, a8	#, tmp4
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:530:       transition = 0;
	l32i	a8, sp, 112	# %sfp,
	s32i	a8, sp, 176	# %sfp,
	j	.L51		#
.L200:
# @OPUS@\upstream\src\opus_decoder.c:496:    if (!decode_fec && mode != MODE_CELT_ONLY && data != NULL
	l32i	a9, sp, 168	# %sfp,
	mov.n	a14, a12	# st, st
	l32i	a15, sp, 164	# %sfp, F2_5
# @OPUS@\upstream\src\opus_decoder.c:496:    if (!decode_fec && mode != MODE_CELT_ONLY && data != NULL
	movi.n	a12, 1	# tmp809,
# @OPUS@\upstream\src\opus_decoder.c:496:    if (!decode_fec && mode != MODE_CELT_ONLY && data != NULL
	bbsi	a9, 0, .L137	#,,
	l32i	a8, sp, 128	# %sfp,
	bnez.n	a8, .L111	#,
.L137:
	l32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	movi.n	a9, 0	#,
	s32i	a9, sp, 100	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:496:    if (!decode_fec && mode != MODE_CELT_ONLY && data != NULL
	s32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:296:    int redundancy_bytes = 0;
	s32i	a9, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:295:    int redundancy=0;
	s32i	a9, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:496:    if (!decode_fec && mode != MODE_CELT_ONLY && data != NULL
	s32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:526:       start_band = 17;
	movi.n	a13, 0x11	# start_band,
	j	.L190		#
.L37:
# @OPUS@\upstream\src\opus_decoder.c:468:      lost_flag = data == NULL ? 1 : 2 * !!decode_fec;
	movi.n	a9, 1	#,
# @OPUS@\upstream\src\opus_decoder.c:457:      st->DecControl.enable_deep_plc = st->complexity >= 5;
	s32i.n	a2, a14, 40	# st_282(D)->DecControl.enable_deep_plc, tmp541
# @OPUS@\upstream\src\opus_decoder.c:468:      lost_flag = data == NULL ? 1 : 2 * !!decode_fec;
	s32i	a9, sp, 100	# %sfp,
	j	.L113		#
.L40:
# @OPUS@\upstream\src\opus_decoder.c:468:      lost_flag = data == NULL ? 1 : 2 * !!decode_fec;
	l32i	a8, sp, 168	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:457:      st->DecControl.enable_deep_plc = st->complexity >= 5;
	s32i.n	a2, a14, 40	# st_282(D)->DecControl.enable_deep_plc, tmp541
# @OPUS@\upstream\src\opus_decoder.c:468:      lost_flag = data == NULL ? 1 : 2 * !!decode_fec;
	movi.n	a3, 2	# tmp928,
	movi.n	a2, 0	# tmp929,
	movnez	a2, a3, a8	# tmp929, tmp928,
	s32i	a2, sp, 100	# %sfp, tmp929
	j	.L113		#
.L10:
# @OPUS@\upstream\src\opus_decoder.c:393:    ALLOC(pcm_transition_celt, pcm_transition_celt_size, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:399:    if (audiosize > frame_size)
	l32i	a9, sp, 104	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	bge	a9, a8, .L194	#,,
	j	.L27		#
.L18:
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	l32i	a9, sp, 132	# %sfp,
	movi	a3, -0x3ea	# tmp817,
	movi.n	a4, 0	# tmp820,
	add.n	a3, a9, a3	# tmp818,, tmp817
	movi.n	a2, 1	# tmp819,
	mov.n	a5, a4	#, tmp820
	movnez	a5, a2, a3	#, tmp819, tmp818
	extui	a3, a5, 0, 8	#, tmp816
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	l32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	s32i	a3, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	bge	a8, a12, .L115	#, F10,
	mov.n	a2, a4	# tmp821, tmp820
.L115:
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	movi.n	a8, 0	#,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	and	a2, a9, a2	# tmp823,, tmp821
	extui	a2, a2, 0, 8	#, tmp823
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	s32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	s32i	a2, sp, 156	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:374:    celt_accum = (mode != MODE_CELT_ONLY) && (frame_size >= F10);
	s32i	a2, sp, 184	# %sfp,
	s32i	a8, sp, 144	# %sfp,
	s32i	a8, sp, 124	# %sfp,
	s32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:293:    int transition=0;
	s32i	a8, sp, 176	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:379:    pcm_transition_silk_size = ALLOC_NONE;
	s32i	a8, sp, 180	# %sfp,
	j	.L10		#
.L48:
# @OPUS@\upstream\src\opus_decoder.c:506:          celt_to_silk = ec_dec_bit_logp(&dec, 1);
	mov.n	a3, a12	#, tmp809
	addi	a2, sp, 16	#,,
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:510:                (opus_int32)ec_dec_uint(&dec, 256)+2 :
	movi	a3, 0x100	#,
	addi	a2, sp, 16	#,,
	call0	ec_dec_uint		#
# @OPUS@\upstream\src\opus_decoder.c:510:                (opus_int32)ec_dec_uint(&dec, 256)+2 :
	addi.n	a2, a2, 2	#,,
	l32i.n	a3, sp, 44	# MEM[(unsigned int *)&dec + 28B], MEM[(unsigned int *)&dec + 28B]
	s32i	a2, sp, 164	# %sfp,
	nsau	a3, a3	# _430, MEM[(unsigned int *)&dec + 28B]
	l32i.n	a2, sp, 36	# MEM[(int *)&dec + 20B], _426
	l32i	a9, sp, 140	# %sfp,
	l32i	a8, sp, 164	# %sfp,
	j	.L116		#
.L47:
# @OPUS@\upstream\src\opus_decoder.c:506:          celt_to_silk = ec_dec_bit_logp(&dec, 1);
	mov.n	a3, a12	#, tmp809
	addi	a2, sp, 16	#,,
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 100	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, sp, 44	# MEM[(unsigned int *)&dec + 28B], MEM[(unsigned int *)&dec + 28B]
# @OPUS@\upstream\src\opus_decoder.c:511:                len-((ec_tell(&dec)+7)>>3);
	l32i.n	a2, sp, 36	# MEM[(int *)&dec + 20B], _426
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a3, a3	# _430, MEM[(unsigned int *)&dec + 28B]
# @OPUS@\upstream\src\opus_decoder.c:511:                len-((ec_tell(&dec)+7)>>3);
	addi	a4, a2, -25	# tmp826, _426,
	add.n	a4, a4, a3	# tmp827, tmp826, _430
# @OPUS@\upstream\src\opus_decoder.c:510:                (opus_int32)ec_dec_uint(&dec, 256)+2 :
	l32i	a9, sp, 140	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:511:                len-((ec_tell(&dec)+7)>>3);
	srai	a4, a4, 3	# tmp828, tmp827,
# @OPUS@\upstream\src\opus_decoder.c:510:                (opus_int32)ec_dec_uint(&dec, 256)+2 :
	sub	a4, a9, a4	#,, tmp828
	s32i	a4, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:503:          redundancy = 1;
	s32i	a12, sp, 96	# %sfp, tmp809
	mov.n	a8, a4	#,
	j	.L116		#
.L46:
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	addi	a2, a2, 37	# tmp829, _352,
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	bge	a3, a2, .L117	# _1258, tmp829,
.L201:
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	movi.n	a8, 0	#,
	s32i	a8, sp, 100	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:296:    int redundancy_bytes = 0;
	s32i	a8, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:295:    int redundancy=0;
	s32i	a8, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:497:     && ec_tell(&dec)+17+20*(mode == MODE_HYBRID) <= 8*len)
	s32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:526:       start_band = 17;
	movi.n	a13, 0x11	# start_band,
	j	.L190		#
.L82:
	l32i	a9, sp, 120	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:681:       smooth_fade(redundant_audio+st->channels*F2_5, pcm+st->channels*F2_5,
	mull	a4, a11, a15	# tmp830, _41, F2_5
	l32i	a6, sp, 136	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:245:    int inc = 48000/Fs;
	l32i.n	a3, a14, 12	# st_282(D)->Fs,
# @OPUS@\upstream\src\opus_decoder.c:681:       smooth_fade(redundant_audio+st->channels*F2_5, pcm+st->channels*F2_5,
	slli	a4, a4, 1	# _470, tmp830,
	add.n	a5, a9, a12	# tmp831,, _1040
# @OPUS@\upstream\src\opus_decoder.c:245:    int inc = 48000/Fs;
	l32r	a2, .LC14	#,
	add.n	a5, a5, a4	# _1039, tmp831, _470
	add.n	a13, a9, a4	# ivtmp$123,, _470
	add.n	a9, a6, a4	# ivtmp$124,, _470
	s32i	a5, sp, 196	#,
	s32i	a8, sp, 200	#,
	s32i	a9, sp, 192	#,
	call0	__divsi3		#
	l32i	a5, sp, 196	#,
	s32i	a14, sp, 124	# %sfp, st
	slli	a2, a2, 1	# _1075,,
	l32r	a4, .LC1	#, tmp849
	l32i	a8, sp, 200	#,
	l32i	a9, sp, 192	#,
	mov.n	a14, a5	# _1039, _1039
	j	.L118		#
.L189:
# @OPUS@\upstream\src\opus_decoder.c:410:    ALLOC(pcm_silk, pcm_silk_size, opus_int16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a4	#,
	s32i	a4, sp, 144	# %sfp, tmp8
	call0	yoradio_opus_scratch_alloc		#
	l32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:386:       transition = 1;
	movi.n	a9, 1	#,
# @OPUS@\upstream\src\opus_decoder.c:410:    ALLOC(pcm_silk, pcm_silk_size, opus_int16);
	s32i	a2, sp, 188	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	s32i	a13, sp, 100	# %sfp, start_band
# @OPUS@\upstream\src\opus_decoder.c:296:    int redundancy_bytes = 0;
	s32i	a13, sp, 164	# %sfp, start_band
# @OPUS@\upstream\src\opus_decoder.c:295:    int redundancy=0;
	s32i	a13, sp, 96	# %sfp, start_band
# @OPUS@\upstream\src\opus_decoder.c:379:    pcm_transition_silk_size = ALLOC_NONE;
	s32i	a13, sp, 180	# %sfp, start_band
# @OPUS@\upstream\src\opus_decoder.c:386:       transition = 1;
	s32i	a9, sp, 176	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:410:    ALLOC(pcm_silk, pcm_silk_size, opus_int16);
	s32i	a8, sp, 160	# %sfp,
	j	.L190		#
.L195:
	movi.n	a9, 0	#,
	mov.n	a4, a9	#,
	movi.n	a3, 2	#,
	mov.n	a2, a9	#, tmp4
	s32i	a9, sp, 144	# %sfp,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	l32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:410:    ALLOC(pcm_silk, pcm_silk_size, opus_int16);
	s32i	a2, sp, 188	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:297:    int celt_to_silk=0;
	s32i	a8, sp, 100	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:296:    int redundancy_bytes = 0;
	s32i	a8, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:295:    int redundancy=0;
	s32i	a8, sp, 96	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:410:    ALLOC(pcm_silk, pcm_silk_size, opus_int16);
	s32i	a8, sp, 176	# %sfp,
	s32i	a8, sp, 112	# %sfp,
	s32i	a8, sp, 180	# %sfp,
	s32i	a8, sp, 160	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:495:    start_band = 0;
	mov.n	a13, a8	# start_band,
	j	.L190		#
.L23:
# @OPUS@\upstream\src\opus_decoder.c:393:    ALLOC(pcm_transition_celt, pcm_transition_celt_size, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\src\opus_decoder.c:399:    if (audiosize > frame_size)
	l32i	a9, sp, 104	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	bge	a9, a8, .L195	#,,
	j	.L27		#
.L1:
# @OPUS@\upstream\src\opus_decoder.c:734: }
	l32i	a0, sp, 236	#,
	movi	a9, 0xf0	#,
	l32i	a2, sp, 104	# %sfp,
	l32i	a12, sp, 232	#,
	l32i	a13, sp, 228	#,
	l32i	a14, sp, 224	#,
	l32i	a15, sp, 220	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	opus_decode_frame, .-opus_decode_frame
	.global	__modsi3
	.section	.text.opus_decode_native_impl$isra$3,"ax",@progbits
	.literal_position
	.align	4
	.type	opus_decode_native_impl$isra$3, @function
# Function: opus_decode_native_impl$isra$3
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
opus_decode_native_impl$isra$3:
	movi	a9, 0xe0	#,
	sub	sp, sp, a9	#,,
	s32i	a13, sp, 212	#,
	s32i	a14, sp, 208	#,
	s32i	a15, sp, 204	#,
	s32i	a0, sp, 220	#,
	s32i	a12, sp, 216	#,
# @OPUS@\upstream\src\opus_decoder.c:738: static int opus_decode_native_impl(OpusDecoder *st, const unsigned char *data,
	s32i	a7, sp, 148	# %sfp, decode_fec
	s32i	a5, sp, 144	# %sfp, pcm
	mov.n	a15, a2	# st, st
	mov.n	a14, a3	# data, data
	mov.n	a8, a4	# len, len
	mov.n	a13, a6	# frame_size, frame_size
# @OPUS@\upstream\src\opus_decoder.c:751:    if (decode_fec<0 || decode_fec>1)
	bgeui	a7, 2, .L240	# decode_fec,,
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	movi.n	a4, 1	# tmp130,
	movi.n	a2, 0	# tmp131,
	movnez	a4, a2, a8	# tmp129, tmp131, len
	extui	a4, a4, 0, 8	# _5, tmp129
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	bbs	a7, a2, .L208	# decode_fec,,
	bne	a4, a2, .L208	# _5,,
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	bne	a3, a2, .L210	# data,,
	j	.L209		#
.L208:
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	l32i.n	a2, a15, 12	# st_8(D)->Fs,
	movi	a3, 0x190	#,
	s32i	a4, sp, 172	#,
	s32i	a8, sp, 180	#,
	call0	__divsi3		#
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	mov.n	a3, a2	#,
	mov.n	a2, a13	#, frame_size
	call0	__modsi3		#
	mov.n	a12, a2	# pcm_count,
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	l32i	a4, sp, 172	#,
	l32i	a8, sp, 180	#,
	bnez.n	a2, .L240	# pcm_count,
# @OPUS@\upstream\src\opus_decoder.c:785:    if (len==0 || data==NULL)
	movi.n	a2, 1	# tmp148,
	movnez	a2, a12, a14	# tmp147, pcm_count, data
# @OPUS@\upstream\src\opus_decoder.c:785:    if (len==0 || data==NULL)
	extui	a2, a2, 0, 8	# tmp150, tmp147
	bnez.n	a2, .L231	# tmp150,
	beqz.n	a4, .L210	# _5,
.L231:
# @OPUS@\upstream\src\opus_decoder.c:790:          ret = opus_decode_frame(st, NULL, 0, pcm+pcm_count*st->channels, frame_size-pcm_count, 0);
	movi.n	a14, 0	# tmp253,
.L212:
# @OPUS@\upstream\src\opus_decoder.c:790:          ret = opus_decode_frame(st, NULL, 0, pcm+pcm_count*st->channels, frame_size-pcm_count, 0);
	l32i.n	a5, a15, 8	# st_8(D)->channels, st_8(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:790:          ret = opus_decode_frame(st, NULL, 0, pcm+pcm_count*st->channels, frame_size-pcm_count, 0);
	l32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:790:          ret = opus_decode_frame(st, NULL, 0, pcm+pcm_count*st->channels, frame_size-pcm_count, 0);
	mull	a5, a12, a5	# tmp152, pcm_count, st_8(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:790:          ret = opus_decode_frame(st, NULL, 0, pcm+pcm_count*st->channels, frame_size-pcm_count, 0);
	sub	a6, a13, a12	#, frame_size, pcm_count
# @OPUS@\upstream\src\opus_decoder.c:790:          ret = opus_decode_frame(st, NULL, 0, pcm+pcm_count*st->channels, frame_size-pcm_count, 0);
	slli	a5, a5, 1	# tmp154, tmp152,
# @OPUS@\upstream\src\opus_decoder.c:790:          ret = opus_decode_frame(st, NULL, 0, pcm+pcm_count*st->channels, frame_size-pcm_count, 0);
	mov.n	a7, a14	#, tmp253
	add.n	a5, a8, a5	#,, tmp154
	mov.n	a4, a14	#, tmp253
	mov.n	a3, a14	#, tmp253
	mov.n	a2, a15	#, st
	call0	opus_decode_frame		#
# @OPUS@\upstream\src\opus_decoder.c:793:          pcm_count += ret;
	add.n	a12, a12, a2	# pcm_count, pcm_count, <retval>
# @OPUS@\upstream\src\opus_decoder.c:791:          if (ret<0)
	bltz	a2, .L251	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:794:       } while (pcm_count < frame_size);
	blt	a12, a13, .L212	# pcm_count, frame_size,
# @OPUS@\upstream\src\opus_decoder.c:798:       st->last_packet_duration = pcm_count;
	s32i	a12, a15, 80	# st_8(D)->last_packet_duration, pcm_count
# @OPUS@\upstream\src\opus_decoder.c:793:          pcm_count += ret;
	mov.n	a5, a12	# <retval>, pcm_count
	j	.L206		#
.L210:
# @OPUS@\upstream\src\opus_decoder.c:800:    } else if (len<0)
	bltz	a8, .L240	# len,
# @OPUS@\upstream\src\opus_decoder.c:803:    packet_mode = opus_packet_get_mode(data);
	l8ui	a10, a14, 0	# *data_7(D), _26
# @OPUS@\upstream\src\opus_decoder.c:260:    if (data[0]&0x80)
	slli	a2, a10, 24	# tmp157, _26,
	bltz	a2, .L213	# tmp157,
# @OPUS@\upstream\src\opus_decoder.c:263:    } else if ((data[0]&0x60) == 0x60)
	movi	a2, 0x60	# tmp158,
	and	a2, a10, a2	# tmp161, _26, tmp158
	movi	a3, 0x60	# tmp162,
	bne	a2, a3, .L249	# tmp161, tmp162,
	j	.L214		#
.L230:
# @OPUS@\upstream\src\opus_decoder.c:805:    packet_frame_size = opus_packet_get_samples_per_frame(data, st->Fs);
	l32i.n	a3, a15, 12	# st_8(D)->Fs,
	mov.n	a2, a14	#, data
	s32i	a10, sp, 176	#,
	s32i	a8, sp, 180	#,
	call0	opus_packet_get_samples_per_frame		#
# @OPUS@\upstream\src\opus_decoder.c:808:    count = opus_packet_parse_impl(data, len, self_delimited, &toc, NULL,
	addi	a3, sp, 32	#,,
# @OPUS@\upstream\src\opus_decoder.c:1237:    return (data[0]&0x4) ? 2 : 1;
	l8ui	a12, a14, 0	# *data_7(D),
# @OPUS@\upstream\src\opus_decoder.c:805:    packet_frame_size = opus_packet_get_samples_per_frame(data, st->Fs);
	s32i	a2, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:808:    count = opus_packet_parse_impl(data, len, self_delimited, &toc, NULL,
	l32i	a8, sp, 180	#,
	addi	a2, a3, 96	# tmp171,,
	l32i	a3, sp, 228	# packet_offset, packet_offset
	movi.n	a6, 0	# tmp169,
	addi	a7, sp, 32	#,,
	l32i	a4, sp, 224	# self_delimited,
# @OPUS@\upstream\src\opus_decoder.c:1237:    return (data[0]&0x4) ? 2 : 1;
	extui	a11, a12, 2, 1	# tmp167, *data_7(D),,
# @OPUS@\upstream\src\opus_decoder.c:808:    count = opus_packet_parse_impl(data, len, self_delimited, &toc, NULL,
	s32i.n	a3, sp, 4	#, packet_offset
	s32i.n	a2, sp, 0	#, tmp171
	addi	a5, a7, 100	#,,
# @OPUS@\upstream\src\opus_decoder.c:1237:    return (data[0]&0x4) ? 2 : 1;
	movi.n	a9, 2	# tmp243,
# @OPUS@\upstream\src\opus_decoder.c:808:    count = opus_packet_parse_impl(data, len, self_delimited, &toc, NULL,
	s32i.n	a6, sp, 12	#, tmp169
	s32i.n	a6, sp, 8	#, tmp169
	mov.n	a3, a8	#, len
	mov.n	a2, a14	#, data
# @OPUS@\upstream\src\opus_decoder.c:1237:    return (data[0]&0x4) ? 2 : 1;
	movi.n	a12, 1	# tmp244,
	movnez	a12, a9, a11	# iftmp$52_59, tmp243, tmp167
# @OPUS@\upstream\src\opus_decoder.c:808:    count = opus_packet_parse_impl(data, len, self_delimited, &toc, NULL,
	call0	opus_packet_parse_impl		#
	mov.n	a5, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:810:    if (count<0)
	l32i	a10, sp, 176	#,
	bltz	a2, .L206	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:813:    data += offset;
	l32i	a2, sp, 128	# offset, offset
# @OPUS@\upstream\src\opus_decoder.c:815:    if (decode_fec)
	l32i	a8, sp, 148	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:813:    data += offset;
	add.n	a14, a14, a2	# data, data, offset
# @OPUS@\upstream\src\opus_decoder.c:815:    if (decode_fec)
	beqz.n	a8, .L217	#,
# @OPUS@\upstream\src\opus_decoder.c:820:       if (frame_size < packet_frame_size || packet_mode == MODE_CELT_ONLY || st->mode == MODE_CELT_ONLY)
	l32i	a8, sp, 152	# %sfp,
	blt	a13, a8, .L218	# frame_size,,
# @OPUS@\upstream\src\opus_decoder.c:820:       if (frame_size < packet_frame_size || packet_mode == MODE_CELT_ONLY || st->mode == MODE_CELT_ONLY)
	l32i	a8, sp, 164	# %sfp,
	bnez.n	a8, .L218	#,
# @OPUS@\upstream\src\opus_decoder.c:820:       if (frame_size < packet_frame_size || packet_mode == MODE_CELT_ONLY || st->mode == MODE_CELT_ONLY)
	l32i	a3, a15, 64	# st_8(D)->mode, st_8(D)->mode
	movi	a2, 0x3ea	# tmp176,
	bne	a3, a2, .L220	# st_8(D)->mode, tmp176,
.L218:
# @OPUS@\upstream\src\opus_decoder.c:914:    return opus_decode_native_impl(st, data, len, pcm, frame_size, decode_fec,
	l32i	a2, sp, 232	# soft_clip,
	movi.n	a3, 0	# tmp178,
	l32i	a5, sp, 144	# %sfp,
	s32i.n	a2, sp, 8	#,
	s32i.n	a3, sp, 16	#, tmp178
	s32i.n	a3, sp, 12	#, tmp178
	s32i.n	a3, sp, 4	#, tmp178
	s32i.n	a3, sp, 0	#, tmp178
	mov.n	a7, a3	#, tmp178
	mov.n	a6, a13	#, frame_size
	mov.n	a4, a3	#, tmp178
	mov.n	a2, a15	#, st
	call0	opus_decode_native_impl$isra$3		#
	mov.n	a5, a2	# <retval>,
	j	.L206		#
.L220:
	l32i	a8, sp, 152	# %sfp,
	sub	a9, a13, a8	# _79, frame_size,
# @OPUS@\upstream\src\opus_decoder.c:824:       if (frame_size-packet_frame_size!=0)
	beq	a13, a8, .L221	# frame_size,,
# @OPUS@\upstream\src\opus_decoder.c:914:    return opus_decode_native_impl(st, data, len, pcm, frame_size, decode_fec,
	l32i	a8, sp, 164	# %sfp,
	l32i	a2, sp, 232	# soft_clip,
	s32i.n	a8, sp, 16	#,
	s32i.n	a2, sp, 8	#,
	s32i.n	a8, sp, 12	#,
	s32i.n	a8, sp, 4	#,
	s32i.n	a8, sp, 0	#,
	mov.n	a7, a8	#,
	l32i	a5, sp, 144	# %sfp,
	mov.n	a4, a8	#, tmp7
	mov.n	a3, a8	#, tmp4
# @OPUS@\upstream\src\opus_decoder.c:823:       duration_copy = st->last_packet_duration;
	l32i	a8, a15, 80	# st_8(D)->last_packet_duration,
# @OPUS@\upstream\src\opus_decoder.c:914:    return opus_decode_native_impl(st, data, len, pcm, frame_size, decode_fec,
	mov.n	a6, a9	#, _79
	mov.n	a2, a15	#, st
	s32i	a9, sp, 172	#,
	s32i	a10, sp, 176	#,
# @OPUS@\upstream\src\opus_decoder.c:823:       duration_copy = st->last_packet_duration;
	s32i	a8, sp, 148	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:914:    return opus_decode_native_impl(st, data, len, pcm, frame_size, decode_fec,
	call0	opus_decode_native_impl$isra$3		#
	mov.n	a5, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:827:          if (ret<0)
	l32i	a9, sp, 172	#,
	l32i	a10, sp, 176	#,
	bgez	a2, .L221	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:829:             st->last_packet_duration = duration_copy;
	l32i	a8, sp, 148	# %sfp,
	s32i	a8, a15, 80	# st_8(D)->last_packet_duration,
	j	.L206		#
.L221:
# @OPUS@\upstream\src\opus_decoder.c:835:       st->mode = packet_mode;
	l32i	a8, sp, 168	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:839:       ret = opus_decode_frame(st, data, size[0], pcm+st->channels*(frame_size-packet_frame_size),
	l32i.n	a5, a15, 8	# st_8(D)->channels, st_8(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:835:       st->mode = packet_mode;
	s32i	a8, a15, 64	# st_8(D)->mode,
# @OPUS@\upstream\src\opus_decoder.c:837:       st->frame_size = packet_frame_size;
	l32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:839:       ret = opus_decode_frame(st, data, size[0], pcm+st->channels*(frame_size-packet_frame_size),
	mull	a5, a9, a5	# tmp186, _79, st_8(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:837:       st->frame_size = packet_frame_size;
	s32i	a8, a15, 72	# st_8(D)->frame_size,
# @OPUS@\upstream\src\opus_decoder.c:839:       ret = opus_decode_frame(st, data, size[0], pcm+st->channels*(frame_size-packet_frame_size),
	mov.n	a6, a8	#,
	l32i	a8, sp, 144	# %sfp,
	l16si	a4, sp, 32	# size,
# @OPUS@\upstream\src\opus_decoder.c:839:       ret = opus_decode_frame(st, data, size[0], pcm+st->channels*(frame_size-packet_frame_size),
	slli	a5, a5, 1	# tmp188, tmp186,
# @OPUS@\upstream\src\opus_decoder.c:839:       ret = opus_decode_frame(st, data, size[0], pcm+st->channels*(frame_size-packet_frame_size),
	add.n	a5, a8, a5	#,, tmp188
# @OPUS@\upstream\src\opus_decoder.c:836:       st->bandwidth = packet_bandwidth;
	s32i.n	a10, a15, 60	# st_8(D)->bandwidth, bandwidth
# @OPUS@\upstream\src\opus_decoder.c:838:       st->stream_channels = packet_stream_channels;
	s32i.n	a12, a15, 56	# st_8(D)->stream_channels, iftmp$52_59
# @OPUS@\upstream\src\opus_decoder.c:839:       ret = opus_decode_frame(st, data, size[0], pcm+st->channels*(frame_size-packet_frame_size),
	movi.n	a7, 1	#,
	mov.n	a3, a14	#, data
	mov.n	a2, a15	#, st
	call0	opus_decode_frame		#
	mov.n	a5, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:841:       if (ret<0)
	bltz	a2, .L206	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:846:          st->last_packet_duration = frame_size;
	s32i	a13, a15, 80	# st_8(D)->last_packet_duration, frame_size
	mov.n	a5, a13	# <retval>, frame_size
	j	.L206		#
.L217:
# @OPUS@\upstream\src\opus_decoder.c:851:    if ((block_output ? packet_frame_size : count*packet_frame_size) > frame_size)
	l32i	a8, sp, 236	# block_output,
# @OPUS@\upstream\src\opus_decoder.c:805:    packet_frame_size = opus_packet_get_samples_per_frame(data, st->Fs);
	l32i	a2, sp, 152	# %sfp, iftmp$8_70
# @OPUS@\upstream\src\opus_decoder.c:851:    if ((block_output ? packet_frame_size : count*packet_frame_size) > frame_size)
	bnez.n	a8, .L222	#,
	mull	a2, a2, a5	# iftmp$8_70, iftmp$8_70, <retval>
.L222:
# @OPUS@\upstream\src\opus_decoder.c:851:    if ((block_output ? packet_frame_size : count*packet_frame_size) > frame_size)
	blt	a13, a2, .L237	# frame_size, iftmp$8_70,
# @OPUS@\upstream\src\opus_decoder.c:855:    st->mode = packet_mode;
	l32i	a8, sp, 168	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:856:    st->bandwidth = packet_bandwidth;
	s32i.n	a10, a15, 60	# st_8(D)->bandwidth, bandwidth
# @OPUS@\upstream\src\opus_decoder.c:855:    st->mode = packet_mode;
	s32i	a8, a15, 64	# st_8(D)->mode,
# @OPUS@\upstream\src\opus_decoder.c:857:    st->frame_size = packet_frame_size;
	l32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:858:    st->stream_channels = packet_stream_channels;
	s32i.n	a12, a15, 56	# st_8(D)->stream_channels, iftmp$52_59
# @OPUS@\upstream\src\opus_decoder.c:857:    st->frame_size = packet_frame_size;
	s32i	a8, a15, 72	# st_8(D)->frame_size,
# @OPUS@\upstream\src\opus_decoder.c:861:    for (i=0;i<count;i++)
	beqz.n	a5, .L238	# <retval>,
	l32i	a8, sp, 236	# block_output,
	addi	a12, sp, 32	# ivtmp$156,,
	beqz.n	a8, .L224	#,
	slli	a2, a5, 1	# tmp193, <retval>,
	add.n	a2, a12, a2	#, ivtmp$156, tmp193
# @OPUS@\upstream\src\opus_decoder.c:876:       ret = opus_decode_frame(st, data, size[i],
	s32i	a15, sp, 160	# %sfp, st
	mov.n	a15, a12	# ivtmp$156, ivtmp$156
	l32i	a12, sp, 152	# %sfp, packet_frame_size
	s32i	a13, sp, 152	# %sfp, frame_size
	l32i	a13, sp, 144	# %sfp, pcm
	s32i	a2, sp, 164	# %sfp,
.L227:
	l16si	a4, a15, 0	# MEM[base: _63, offset: 0B],
	l32i	a6, sp, 152	# %sfp,
	l32i	a2, sp, 160	# %sfp,
	mov.n	a3, a14	#, data
	mov.n	a5, a13	#, pcm
	movi.n	a7, 0	#,
	call0	opus_decode_frame		#
	mov.n	a5, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:894:          output_error = block_output(block_context, frame_pcm, ret);
	mov.n	a4, a12	#, packet_frame_size
	mov.n	a3, a13	#, pcm
	l32i	a2, sp, 240	# block_context,
# @OPUS@\upstream\src\opus_decoder.c:879:       if (ret<0)
	bltz	a5, .L206	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:883:       nb_samples += ret;
	l32i	a8, sp, 148	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:882:       data += size[i];
	l16si	a6, a15, 0	# MEM[base: _63, offset: 0B], tmp197
# @OPUS@\upstream\src\opus_decoder.c:883:       nb_samples += ret;
	add.n	a8, a8, a5	#,, <retval>
	s32i	a8, sp, 148	# %sfp,
	addi.n	a15, a15, 2	# ivtmp$156, ivtmp$156,
# @OPUS@\upstream\src\opus_decoder.c:882:       data += size[i];
	add.n	a14, a14, a6	# data, data, tmp197
# @OPUS@\upstream\src\opus_decoder.c:887:          if (ret != packet_frame_size) return OPUS_INTERNAL_ERROR;
	bne	a12, a5, .L225	# packet_frame_size, <retval>,
# @OPUS@\upstream\src\opus_decoder.c:894:          output_error = block_output(block_context, frame_pcm, ret);
	l32i	a8, sp, 236	# block_output,
	callx0	a8	#
	mov.n	a5, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:895:          if (output_error) return output_error < 0 ? output_error : OPUS_INTERNAL_ERROR;
	bnez.n	a2, .L226	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:861:    for (i=0;i<count;i++)
	l32i	a8, sp, 164	# %sfp,
	bne	a8, a15, .L227	#, ivtmp$156,
	l32i	a15, sp, 160	# %sfp, st
	j	.L223		#
.L224:
	slli	a5, a5, 1	# tmp200, <retval>,
	add.n	a5, a12, a5	#, ivtmp$159, tmp200
# @OPUS@\upstream\src\opus_decoder.c:876:       ret = opus_decode_frame(st, data, size[i],
	mov.n	a2, a15	# st, st
	s32i	a13, sp, 156	# %sfp, frame_size
	l32i	a13, sp, 148	# %sfp, decode_fec
	mov.n	a15, a12	# ivtmp$159, ivtmp$159
	s32i	a5, sp, 152	# %sfp,
	mov.n	a12, a2	# st, st
.L229:
# @OPUS@\upstream\src\opus_decoder.c:864:       opus_val16 *frame_pcm = block_output ? pcm : pcm+nb_samples*st->channels;
	l32i.n	a5, a12, 8	# st_8(D)->channels, st_8(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:876:       ret = opus_decode_frame(st, data, size[i],
	l32i	a8, sp, 156	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:864:       opus_val16 *frame_pcm = block_output ? pcm : pcm+nb_samples*st->channels;
	mull	a5, a13, a5	# tmp202, decode_fec, st_8(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:876:       ret = opus_decode_frame(st, data, size[i],
	sub	a6, a8, a13	#,, decode_fec
	l32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:864:       opus_val16 *frame_pcm = block_output ? pcm : pcm+nb_samples*st->channels;
	slli	a5, a5, 1	# tmp204, tmp202,
# @OPUS@\upstream\src\opus_decoder.c:876:       ret = opus_decode_frame(st, data, size[i],
	l16si	a4, a15, 0	# MEM[base: _188, offset: 0B],
	mov.n	a3, a14	#, data
	movi.n	a7, 0	#,
	add.n	a5, a8, a5	#,, tmp204
	mov.n	a2, a12	#, st
	call0	opus_decode_frame		#
# @OPUS@\upstream\src\opus_decoder.c:879:       if (ret<0)
	bgez	a2, .L250	# <retval>,
	j	.L251		#
.L226:
# @OPUS@\upstream\src\opus_decoder.c:895:          if (output_error) return output_error < 0 ? output_error : OPUS_INTERNAL_ERROR;
	bltz	a2, .L206	# <retval>,
.L225:
	movi.n	a5, -3	# <retval>,
	j	.L206		#
.L238:
# @OPUS@\upstream\src\opus_decoder.c:860:    nb_samples=0;
	s32i	a5, sp, 148	# %sfp, <retval>
.L223:
# @OPUS@\upstream\src\opus_decoder.c:898:    st->last_packet_duration = nb_samples;
	l32i	a8, sp, 148	# %sfp,
	s32i	a8, a15, 80	# st_8(D)->last_packet_duration,
	mov.n	a5, a8	# <retval>,
	j	.L206		#
.L237:
# @OPUS@\upstream\src\opus_decoder.c:852:       return OPUS_BUFFER_TOO_SMALL;
	movi.n	a5, -2	# <retval>,
	j	.L206		#
.L240:
# @OPUS@\upstream\src\opus_decoder.c:752:       return OPUS_BAD_ARG;
	movi.n	a5, -1	# <retval>,
	j	.L206		#
.L250:
# @OPUS@\upstream\src\opus_decoder.c:882:       data += size[i];
	l16si	a3, a15, 0	# MEM[base: _188, offset: 0B], tmp210
# @OPUS@\upstream\src\opus_decoder.c:861:    for (i=0;i<count;i++)
	l32i	a8, sp, 152	# %sfp,
	addi.n	a15, a15, 2	# ivtmp$159, ivtmp$159,
# @OPUS@\upstream\src\opus_decoder.c:882:       data += size[i];
	add.n	a14, a14, a3	# data, data, tmp210
# @OPUS@\upstream\src\opus_decoder.c:883:       nb_samples += ret;
	add.n	a13, a13, a2	# decode_fec, decode_fec, <retval>
# @OPUS@\upstream\src\opus_decoder.c:861:    for (i=0;i<count;i++)
	bne	a8, a15, .L229	#, ivtmp$159,
	mov.n	a15, a12	# st, st
	s32i	a13, sp, 148	# %sfp, decode_fec
	j	.L223		#
.L213:
# @OPUS@\upstream\src\opus_decoder.c:1222:       bandwidth = OPUS_BANDWIDTH_MEDIUMBAND + ((data[0]>>5)&0x3);
	movi	a2, 0x44e	# tmp217,
# @OPUS@\upstream\src\opus_decoder.c:1222:       bandwidth = OPUS_BANDWIDTH_MEDIUMBAND + ((data[0]>>5)&0x3);
	extui	a10, a10, 5, 2	# tmp216, _26,,
# @OPUS@\upstream\src\opus_decoder.c:1222:       bandwidth = OPUS_BANDWIDTH_MEDIUMBAND + ((data[0]>>5)&0x3);
	add.n	a10, a10, a2	# bandwidth, tmp216, tmp217
# @OPUS@\upstream\src\opus_decoder.c:1223:       if (bandwidth == OPUS_BANDWIDTH_MEDIUMBAND)
	movi.n	a3, 1	#,
# @OPUS@\upstream\src\opus_decoder.c:1224:          bandwidth = OPUS_BANDWIDTH_NARROWBAND;
	sub	a2, a10, a2	# tmp261, bandwidth, tmp217
# @OPUS@\upstream\src\opus_decoder.c:1223:       if (bandwidth == OPUS_BANDWIDTH_MEDIUMBAND)
	s32i	a3, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:262:       mode = MODE_CELT_ONLY;
	movi	a5, 0x3ea	#,
# @OPUS@\upstream\src\opus_decoder.c:1224:          bandwidth = OPUS_BANDWIDTH_NARROWBAND;
	movi	a3, 0x44d	# tmp260,
# @OPUS@\upstream\src\opus_decoder.c:262:       mode = MODE_CELT_ONLY;
	s32i	a5, sp, 168	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:1224:          bandwidth = OPUS_BANDWIDTH_NARROWBAND;
	moveqz	a10, a3, a2	# bandwidth, tmp260, tmp261
	j	.L230		#
.L209:
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	l32i.n	a2, a15, 12	# st_8(D)->Fs,
	movi	a3, 0x190	#,
	call0	__divsi3		#
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	mov.n	a3, a2	#,
	mov.n	a2, a13	#, frame_size
	call0	__modsi3		#
	mov.n	a12, a2	# pcm_count,
# @OPUS@\upstream\src\opus_decoder.c:754:    if ((decode_fec || len==0 || data==NULL) && frame_size%(st->Fs/400)!=0)
	beqz.n	a2, .L231	# pcm_count,
	j	.L240		#
.L214:
# @OPUS@\upstream\src\opus_decoder.c:1227:       bandwidth = (data[0]&0x10) ? OPUS_BANDWIDTH_FULLBAND :
	movi	a2, 0x3e9	#,
	extui	a10, a10, 4, 1	# tmp232, _26,,
	s32i	a2, sp, 168	# %sfp,
	movi	a3, 0x451	# tmp247,
	movi	a2, 0x450	# tmp248,
	movi.n	a6, 0	#,
	movnez	a2, a3, a10	# tmp248, tmp247, tmp232
	s32i	a6, sp, 164	# %sfp,
	mov.n	a10, a2	# bandwidth, tmp248
	j	.L230		#
.L249:
# @OPUS@\upstream\src\opus_decoder.c:1230:       bandwidth = OPUS_BANDWIDTH_NARROWBAND + ((data[0]>>5)&0x3);
	srli	a10, a10, 5	# tmp234, _26,
# @OPUS@\upstream\src\opus_decoder.c:1230:       bandwidth = OPUS_BANDWIDTH_NARROWBAND + ((data[0]>>5)&0x3);
	movi	a2, 0x44d	# tmp235,
	movi.n	a3, 0	#,
# @OPUS@\upstream\src\opus_decoder.c:267:       mode = MODE_SILK_ONLY;
	movi	a5, 0x3e8	#,
# @OPUS@\upstream\src\opus_decoder.c:1230:       bandwidth = OPUS_BANDWIDTH_NARROWBAND + ((data[0]>>5)&0x3);
	add.n	a10, a10, a2	# bandwidth, tmp234, tmp235
	s32i	a3, sp, 164	# %sfp,
# @OPUS@\upstream\src\opus_decoder.c:267:       mode = MODE_SILK_ONLY;
	s32i	a5, sp, 168	# %sfp,
	j	.L230		#
.L251:
	mov.n	a5, a2	# <retval>, <retval>
.L206:
# @OPUS@\upstream\src\opus_decoder.c:908: }
	l32i	a0, sp, 220	#,
	movi	a9, 0xe0	#,
	mov.n	a2, a5	#, <retval>
	l32i	a12, sp, 216	#,
	l32i	a13, sp, 212	#,
	l32i	a14, sp, 208	#,
	l32i	a15, sp, 204	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	opus_decode_native_impl$isra$3, .-opus_decode_native_impl$isra$3
	.section	.text.opus_decoder_get_size,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_decoder_get_size
	.type	opus_decoder_get_size, @function
# Function: opus_decoder_get_size
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #define VALIDATE_OPUS_DECODER(st)
# C context: #endif
# C context:
# C context: int opus_decoder_get_size(int channels)
# C context: {
# C context: int silkDecSizeBytes, celtDecSizeBytes;
# C context: int ret;
# C context: if (channels<1 || channels > 2)
opus_decoder_get_size:
	addi	sp, sp, -32	#,,
	s32i.n	a12, sp, 24	#,
	s32i.n	a13, sp, 20	#,
	s32i.n	a0, sp, 28	#,
# @OPUS@\upstream\src\opus_decoder.c:140: {
	mov.n	a13, a2	# channels, channels
# @OPUS@\upstream\src\opus_decoder.c:143:    if (channels<1 || channels > 2)
	addi.n	a2, a2, -1	# tmp55, channels,
# @OPUS@\upstream\src\opus_decoder.c:144:       return 0;
	movi.n	a12, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:143:    if (channels<1 || channels > 2)
	bgeui	a2, 2, .L253	# tmp55,,
# @OPUS@\upstream\src\opus_decoder.c:145:    ret = silk_Get_Decoder_Size( &silkDecSizeBytes );
	mov.n	a2, sp	#,
	call0	silk_Get_Decoder_Size		#
# @OPUS@\upstream\src\opus_decoder.c:146:    if(ret)
	bne	a2, a12, .L253	#,,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	l32i.n	a3, sp, 0	# silkDecSizeBytes, silkDecSizeBytes
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	movi.n	a2, -4	# tmp58,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	addi.n	a3, a3, 3	# tmp56, silkDecSizeBytes,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	and	a3, a3, a2	# tmp59, tmp56, tmp58
# @OPUS@\upstream\src\opus_decoder.c:149:    celtDecSizeBytes = celt_decoder_get_size(channels);
	mov.n	a2, a13	#, channels
# @OPUS@\upstream\src\opus_decoder.c:148:    silkDecSizeBytes = align(silkDecSizeBytes);
	s32i.n	a3, sp, 0	# silkDecSizeBytes, tmp59
# @OPUS@\upstream\src\opus_decoder.c:149:    celtDecSizeBytes = celt_decoder_get_size(channels);
	call0	celt_decoder_get_size		#
# @OPUS@\upstream\src\opus_decoder.c:150:    return align(sizeof(OpusDecoder))+silkDecSizeBytes+celtDecSizeBytes;
	l32i.n	a12, sp, 0	# silkDecSizeBytes, silkDecSizeBytes
	addi	a12, a12, 88	# tmp60, silkDecSizeBytes,
# @OPUS@\upstream\src\opus_decoder.c:150:    return align(sizeof(OpusDecoder))+silkDecSizeBytes+celtDecSizeBytes;
	add.n	a12, a12, a2	# <retval>, tmp60,
.L253:
# @OPUS@\upstream\src\opus_decoder.c:151: }
	l32i.n	a0, sp, 28	#,
	mov.n	a2, a12	#, <retval>
	l32i.n	a13, sp, 20	#,
	l32i.n	a12, sp, 24	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	opus_decoder_get_size, .-opus_decoder_get_size
	.section	.text.opus_decoder_init,"ax",@progbits
	.literal_position
	.literal .LC22, -48000
	.literal .LC23, -24000
	.literal .LC24, -16000
	.literal .LC25, -12000
	.literal .LC26, -8000
	.literal .LC27, 10016
	.align	4
	.global	opus_decoder_init
	.type	opus_decoder_init, @function
# Function: opus_decoder_init
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return align(sizeof(OpusDecoder))+silkDecSizeBytes+celtDecSizeBytes;
# C context: }
# C context:
# C context: int opus_decoder_init(OpusDecoder *st, opus_int32 Fs, int channels)
# C context: {
# C context: void *silk_dec;
# C context: CELTDecoder *celt_dec;
# C context: int ret, silkDecSizeBytes;
opus_decoder_init:
	addi	sp, sp, -64	#,,
	s32i.n	a13, sp, 52	#,
	mov.n	a13, a3	# Fs, Fs
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a3, .LC22	#, tmp82
# @OPUS@\upstream\src\opus_decoder.c:154: {
	s32i.n	a12, sp, 56	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a0, sp, 60	#,
	mov.n	a14, a4	# channels, channels
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	add.n	a3, a13, a3	# tmp81, Fs, tmp82
	movi.n	a4, 0	# tmp84,
# @OPUS@\upstream\src\opus_decoder.c:154: {
	mov.n	a12, a2	# st, st
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	movi.n	a5, 1	# tmp83,
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	beq	a3, a4, .L259	# tmp81,,
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a3, .LC23	#, tmp89
	add.n	a3, a13, a3	# tmp88, Fs, tmp89
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	beq	a3, a4, .L259	# tmp88,,
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a3, .LC24	#, tmp96
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a2, .LC25	#, tmp102
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	mov.n	a6, a4	#, tmp84
	add.n	a3, a13, a3	# tmp95, Fs, tmp96
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	add.n	a2, a13, a2	# tmp101, Fs, tmp102
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	movnez	a6, a5, a3	#, tmp83, tmp95
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	movnez	a4, a5, a2	# tmp84, tmp83, tmp101
# @OPUS@\upstream\src\opus_decoder.c:159:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	bnone	a6, a4, .L259	# tmp94, tmp100,
	l32r	a2, .LC26	#, tmp111
	add.n	a2, a13, a2	# tmp110, Fs, tmp111
	bnez.n	a2, .L264	# tmp110,
.L259:
# @OPUS@\upstream\src\opus_decoder.c:160:     || (channels!=1&&channels!=2))
	addi.n	a2, a14, -1	# tmp115, channels,
# @OPUS@\upstream\src\opus_decoder.c:160:     || (channels!=1&&channels!=2))
	bgeui	a2, 2, .L264	# tmp115,,
# @OPUS@\upstream\src\opus_decoder.c:164:    if (!yoradio_opus_history_begin()) return OPUS_ALLOC_FAIL;
	call0	yoradio_opus_history_begin		#
# @OPUS@\upstream\src\opus_decoder.c:164:    if (!yoradio_opus_history_begin()) return OPUS_ALLOC_FAIL;
	beqz.n	a2, .L265	#,
# @OPUS@\upstream\src\opus_decoder.c:145:    ret = silk_Get_Decoder_Size( &silkDecSizeBytes );
	mov.n	a2, sp	#,
	call0	silk_Get_Decoder_Size		#
# @OPUS@\upstream\src\opus_decoder.c:146:    if(ret)
	movi.n	a3, 0	# _71,
	bne	a2, a3, .L262	#,,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	l32i.n	a3, sp, 0	# silkDecSizeBytes, silkDecSizeBytes
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	movi.n	a2, -4	# tmp118,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	addi.n	a3, a3, 3	# tmp116, silkDecSizeBytes,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	and	a3, a3, a2	# tmp119, tmp116, tmp118
# @OPUS@\upstream\src\opus_decoder.c:149:    celtDecSizeBytes = celt_decoder_get_size(channels);
	mov.n	a2, a14	#, channels
# @OPUS@\upstream\src\opus_decoder.c:148:    silkDecSizeBytes = align(silkDecSizeBytes);
	s32i.n	a3, sp, 0	# silkDecSizeBytes, tmp119
# @OPUS@\upstream\src\opus_decoder.c:149:    celtDecSizeBytes = celt_decoder_get_size(channels);
	call0	celt_decoder_get_size		#
# @OPUS@\upstream\src\opus_decoder.c:150:    return align(sizeof(OpusDecoder))+silkDecSizeBytes+celtDecSizeBytes;
	l32i.n	a3, sp, 0	# silkDecSizeBytes, silkDecSizeBytes
	addi	a3, a3, 88	# tmp120, silkDecSizeBytes,
# @OPUS@\upstream\src\opus_decoder.c:150:    return align(sizeof(OpusDecoder))+silkDecSizeBytes+celtDecSizeBytes;
	add.n	a3, a3, a2	# _71, tmp120,
.L262:
# @OPUS@\upstream\src\opus_decoder.c:166:    OPUS_CLEAR((char*)st, opus_decoder_get_size(channels));
	mov.n	a2, a12	#, st
	movi.n	a4, 1	#,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\src\opus_decoder.c:168:    ret = silk_Get_Decoder_Size(&silkDecSizeBytes);
	mov.n	a2, sp	#,
	call0	silk_Get_Decoder_Size		#
# @OPUS@\upstream\src\opus_decoder.c:169:    if (ret)
	bnez.n	a2, .L267	# ret,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	l32i.n	a3, sp, 0	# silkDecSizeBytes, silkDecSizeBytes
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	movi.n	a4, -4	# tmp124,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	addi.n	a3, a3, 3	# tmp122, silkDecSizeBytes,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	and	a3, a3, a4	# _49, tmp122, tmp124
# @OPUS@\upstream\src\opus_decoder.c:174:    st->celt_dec_offset = st->silk_dec_offset+silkDecSizeBytes;
	addi	a4, a3, 88	# _12, _49,
# @OPUS@\upstream\src\opus_decoder.c:173:    st->silk_dec_offset = align(sizeof(OpusDecoder));
	movi.n	a5, 0x58	# tmp125,
# @OPUS@\upstream\src\opus_decoder.c:174:    st->celt_dec_offset = st->silk_dec_offset+silkDecSizeBytes;
	s32i.n	a4, a12, 0	# st_21(D)->celt_dec_offset, _12
# @OPUS@\upstream\src\opus_decoder.c:178:    st->complexity = 0;
	s32i.n	a2, a12, 48	# st_21(D)->complexity, ret
# @OPUS@\upstream\src\opus_decoder.c:173:    st->silk_dec_offset = align(sizeof(OpusDecoder));
	s32i.n	a5, a12, 4	# st_21(D)->silk_dec_offset, tmp125
# @OPUS@\upstream\src\opus_decoder.c:177:    st->stream_channels = st->channels = channels;
	s32i.n	a14, a12, 8	# st_21(D)->channels, channels
# @OPUS@\upstream\src\opus_decoder.c:177:    st->stream_channels = st->channels = channels;
	s32i.n	a14, a12, 56	# st_21(D)->stream_channels, channels
# @OPUS@\upstream\src\opus_decoder.c:180:    st->Fs = Fs;
	s32i.n	a13, a12, 12	# st_21(D)->Fs, Fs
# @OPUS@\upstream\src\opus_decoder.c:181:    st->DecControl.API_sampleRate = st->Fs;
	s32i.n	a13, a12, 24	# st_21(D)->DecControl.API_sampleRate, Fs
# @OPUS@\upstream\src\opus_decoder.c:182:    st->DecControl.nChannelsAPI      = st->channels;
	s32i.n	a14, a12, 16	# st_21(D)->DecControl.nChannelsAPI, channels
# @OPUS@\upstream\src\opus_decoder.c:185:    ret = silk_InitDecoder( silk_dec );
	add.n	a2, a12, a5	#, st,
	s32i.n	a4, sp, 16	#,
# @OPUS@\upstream\src\opus_decoder.c:172:    silkDecSizeBytes = align(silkDecSizeBytes);
	s32i.n	a3, sp, 0	# silkDecSizeBytes, _49
# @OPUS@\upstream\src\opus_decoder.c:185:    ret = silk_InitDecoder( silk_dec );
	call0	silk_InitDecoder		#
	mov.n	a15, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:187:    if(ret)return ret;
	l32i.n	a4, sp, 16	#,
	bnez.n	a2, .L258	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:176:    celt_dec = (CELTDecoder*)((char*)st+st->celt_dec_offset);
	add.n	a5, a12, a4	# celt_dec, st, _12
# @OPUS@\upstream\src\opus_decoder.c:193:    ret = celt_decoder_init(celt_dec, Fs, channels);
	mov.n	a2, a5	#, celt_dec
	mov.n	a4, a14	#, channels
	mov.n	a3, a13	#, Fs
	s32i.n	a5, sp, 16	#,
	call0	celt_decoder_init		#
	mov.n	a15, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:195:    if(ret!=OPUS_OK)return ret;
	l32i.n	a5, sp, 16	#,
	bnez.n	a2, .L258	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:200:    celt_decoder_ctl(celt_dec, CELT_SET_SIGNALLING(0));
	l32r	a3, .LC27	#,
	mov.n	a4, a2	#, <retval>
	mov.n	a2, a5	#, celt_dec
	call0	opus_custom_decoder_ctl		#
# @OPUS@\upstream\src\opus_decoder.c:203:    st->frame_size = Fs/400;
	movi	a3, 0x190	#,
# @OPUS@\upstream\src\opus_decoder.c:202:    st->prev_mode = 0;
	s32i	a15, a12, 68	# st_21(D)->prev_mode, <retval>
# @OPUS@\upstream\src\opus_decoder.c:203:    st->frame_size = Fs/400;
	mov.n	a2, a13	#, Fs
	call0	__divsi3		#
# @OPUS@\upstream\src\opus_decoder.c:203:    st->frame_size = Fs/400;
	s32i	a2, a12, 72	# st_21(D)->frame_size,
# @OPUS@\upstream\src\opus_decoder.c:207:    st->arch = opus_select_arch();
	s32i.n	a15, a12, 52	# st_21(D)->arch, <retval>
# @OPUS@\upstream\src\opus_decoder.c:208:    return OPUS_OK;
	j	.L258		#
.L264:
# @OPUS@\upstream\src\opus_decoder.c:161:       return OPUS_BAD_ARG;
	movi.n	a15, -1	# <retval>,
	j	.L258		#
.L265:
# @OPUS@\upstream\src\opus_decoder.c:164:    if (!yoradio_opus_history_begin()) return OPUS_ALLOC_FAIL;
	movi.n	a15, -7	# <retval>,
	j	.L258		#
.L267:
# @OPUS@\upstream\src\opus_decoder.c:170:       return OPUS_INTERNAL_ERROR;
	movi.n	a15, -3	# <retval>,
.L258:
# @OPUS@\upstream\src\opus_decoder.c:209: }
	l32i.n	a0, sp, 60	#,
	mov.n	a2, a15	#, <retval>
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	opus_decoder_init, .-opus_decoder_init
	.section	.text.opus_decoder_create,"ax",@progbits
	.literal_position
	.literal .LC28, -48000
	.literal .LC29, -24000
	.literal .LC30, -16000
	.literal .LC31, -12000
	.literal .LC32, -8000
	.align	4
	.global	opus_decoder_create
	.type	opus_decoder_create, @function
# Function: opus_decoder_create
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return OPUS_OK;
# C context: }
# C context:
# C context: OpusDecoder *opus_decoder_create(opus_int32 Fs, int channels, int *error)
# C context: {
# C context: int ret;
# C context: OpusDecoder *st;
# C context: if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
opus_decoder_create:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 40	#,
	mov.n	a12, a2	# Fs, Fs
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a2, .LC28	#, tmp71
# @OPUS@\upstream\src\opus_decoder.c:212: {
	s32i.n	a14, sp, 32	#,
	s32i.n	a15, sp, 28	#,
	mov.n	a14, a4	# error, error
	s32i.n	a0, sp, 44	#,
	s32i.n	a13, sp, 36	#,
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	add.n	a2, a12, a2	# tmp70, Fs, tmp71
	movi.n	a4, 0	# tmp73,
# @OPUS@\upstream\src\opus_decoder.c:212: {
	mov.n	a15, a3	# channels, channels
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	movi.n	a5, 1	# tmp72,
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	beq	a2, a4, .L278	# tmp70,,
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a3, .LC29	#, tmp78
	add.n	a3, a12, a3	# tmp77, Fs, tmp78
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	beq	a3, a4, .L278	# tmp77,,
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a3, .LC30	#, tmp85
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	l32r	a2, .LC31	#, tmp91
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	mov.n	a6, a4	#, tmp73
	add.n	a3, a12, a3	# tmp84, Fs, tmp85
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	add.n	a2, a12, a2	# tmp90, Fs, tmp91
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	movnez	a6, a5, a3	#, tmp72, tmp84
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	movnez	a4, a5, a2	# tmp73, tmp72, tmp90
# @OPUS@\upstream\src\opus_decoder.c:215:    if ((Fs!=48000&&Fs!=24000&&Fs!=16000&&Fs!=12000&&Fs!=8000)
	bnone	a6, a4, .L278	# tmp83, tmp89,
	l32r	a2, .LC32	#, tmp100
	add.n	a2, a12, a2	# tmp99, Fs, tmp100
	bnez.n	a2, .L279	# tmp99,
.L278:
# @OPUS@\upstream\src\opus_decoder.c:216:     || (channels!=1&&channels!=2))
	addi.n	a2, a15, -1	# tmp104, channels,
# @OPUS@\upstream\src\opus_decoder.c:216:     || (channels!=1&&channels!=2))
	bltui	a2, 2, .L281	# tmp104,,
.L279:
# @OPUS@\upstream\src\opus_decoder.c:218:       if (error)
	bnez.n	a14, .L282	# error,
	j	.L307		#
.L282:
# @OPUS@\upstream\src\opus_decoder.c:219:          *error = OPUS_BAD_ARG;
	movi.n	a2, -1	# tmp105,
	s32i.n	a2, a14, 0	# *error_18(D), tmp105
# @OPUS@\upstream\src\opus_decoder.c:220:       return NULL;
	movi.n	a13, 0	# <retval>,
	j	.L277		#
.L281:
# @OPUS@\upstream\src\opus_decoder.c:145:    ret = silk_Get_Decoder_Size( &silkDecSizeBytes );
	mov.n	a2, sp	#,
	call0	silk_Get_Decoder_Size		#
# @OPUS@\upstream\src\opus_decoder.c:146:    if(ret)
	movi.n	a3, 0	# _47,
	bne	a2, a3, .L284	#,,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	l32i.n	a3, sp, 0	# silkDecSizeBytes, silkDecSizeBytes
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	movi.n	a2, -4	# tmp108,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	addi.n	a3, a3, 3	# tmp106, silkDecSizeBytes,
# @OPUS@\upstream\src\opus_private.h:171:     return ((i + alignment - 1) / alignment) * alignment;
	and	a3, a3, a2	# tmp109, tmp106, tmp108
# @OPUS@\upstream\src\opus_decoder.c:149:    celtDecSizeBytes = celt_decoder_get_size(channels);
	mov.n	a2, a15	#, channels
# @OPUS@\upstream\src\opus_decoder.c:148:    silkDecSizeBytes = align(silkDecSizeBytes);
	s32i.n	a3, sp, 0	# silkDecSizeBytes, tmp109
# @OPUS@\upstream\src\opus_decoder.c:149:    celtDecSizeBytes = celt_decoder_get_size(channels);
	call0	celt_decoder_get_size		#
# @OPUS@\upstream\src\opus_decoder.c:150:    return align(sizeof(OpusDecoder))+silkDecSizeBytes+celtDecSizeBytes;
	l32i.n	a3, sp, 0	# silkDecSizeBytes, silkDecSizeBytes
	addi	a3, a3, 88	# tmp110, silkDecSizeBytes,
# @OPUS@\upstream\src\opus_decoder.c:150:    return align(sizeof(OpusDecoder))+silkDecSizeBytes+celtDecSizeBytes;
	add.n	a3, a3, a2	# _47, tmp110,
.L284:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\os_support.h:58:    return malloc(size);
	mov.n	a2, a3	#, _47
	call0	malloc		#
	mov.n	a13, a2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:223:    if (st == NULL)
	bnez.n	a2, .L285	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:225:       if (error)
	beqz.n	a14, .L307	# error,
# @OPUS@\upstream\src\opus_decoder.c:226:          *error = OPUS_ALLOC_FAIL;
	movi.n	a2, -7	# tmp113,
	s32i.n	a2, a14, 0	# *error_18(D), tmp113
	j	.L277		#
.L285:
# @OPUS@\upstream\src\opus_decoder.c:229:    ret = opus_decoder_init(st, Fs, channels);
	mov.n	a4, a15	#, channels
	mov.n	a3, a12	#, Fs
	call0	opus_decoder_init		#
# @OPUS@\upstream\src\opus_decoder.c:230:    if (error)
	beqz.n	a14, .L287	# error,
# @OPUS@\upstream\src\opus_decoder.c:231:       *error = ret;
	s32i.n	a2, a14, 0	# *error_18(D), ret
.L287:
# @OPUS@\upstream\src\opus_decoder.c:232:    if (ret != OPUS_OK)
	beqz.n	a2, .L277	# ret,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\os_support.h:83:    free(ptr);
	mov.n	a2, a13	#, <retval>
	call0	free		#
.L307:
# @OPUS@\upstream\src\opus_decoder.c:235:       st = NULL;
	movi.n	a13, 0	# <retval>,
.L277:
# @OPUS@\upstream\src\opus_decoder.c:238: }
	l32i.n	a0, sp, 44	#,
	mov.n	a2, a13	#, <retval>
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	opus_decoder_create, .-opus_decoder_create
	.section	.text.opus_decode_native,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_decode_native
	.type	opus_decode_native, @function
# Function: opus_decode_native
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: int ret;
# C context: /* If no FEC can be present, run the PLC (recursive call) */
# C context: if (frame_size < packet_frame_size || packet_mode == MODE_CELT_ONLY || st->mode == MODE_CELT_ONLY)
# C context: return opus_decode_native(st, NULL, 0, pcm, frame_size, 0, 0, NULL, soft_clip, NULL, 0);
# C context: /* Otherwise, run the PLC on everything except the size for which we might have FEC */
# C context: duration_copy = st->last_packet_duration;
# C context: if (frame_size-packet_frame_size!=0)
# C context: {
opus_decode_native:
	addi	sp, sp, -48	#,,
# @OPUS@\upstream\src\opus_decoder.c:914:    return opus_decode_native_impl(st, data, len, pcm, frame_size, decode_fec,
	movi.n	a8, 0	# tmp54,
	s32i.n	a8, sp, 16	#, tmp54
	s32i.n	a8, sp, 12	#, tmp54
	l32i.n	a8, sp, 56	# soft_clip, soft_clip
# @OPUS@\upstream\src\opus_decoder.c:913: {
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\src\opus_decoder.c:914:    return opus_decode_native_impl(st, data, len, pcm, frame_size, decode_fec,
	s32i.n	a8, sp, 8	#, soft_clip
	l32i.n	a8, sp, 52	# packet_offset, packet_offset
	s32i.n	a8, sp, 4	#, packet_offset
	l32i.n	a8, sp, 48	# self_delimited, self_delimited
	s32i.n	a8, sp, 0	#, self_delimited
	call0	opus_decode_native_impl$isra$3		#
# @OPUS@\upstream\src\opus_decoder.c:916: }
	l32i.n	a0, sp, 44	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	opus_decode_native, .-opus_decode_native
	.section	.text.yoradio_opus_decode_blocks_native,"ax",@progbits
	.literal_position
	.literal .LC33, 48000
	.align	4
	.global	yoradio_opus_decode_blocks_native
	.type	yoradio_opus_decode_blocks_native, @function
# Function: yoradio_opus_decode_blocks_native
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: #if defined(YORADIO_OPUS_BOUNDED) && defined(FIXED_POINT)
# C context: int yoradio_opus_decode_blocks_native(void *decoder, const unsigned char *packet,
# C context: int length, int16_t *pcm, int frame_capacity,
# C context: yoradio_opus_pcm_block_fn output, void *context)
# C context: {
# C context: OpusDecoder *st = (OpusDecoder *)decoder;
yoradio_opus_decode_blocks_native:
# @OPUS@\upstream\src\opus_decoder.c:926:    if (!st || !packet || length <= 0 || !pcm || !output ||
	movi.n	a9, 1	# tmp65,
	movi.n	a8, 0	# tmp66,
# @OPUS@\upstream\src\opus_decoder.c:922: {
	addi	sp, sp, -48	#,,
# @OPUS@\upstream\src\opus_decoder.c:926:    if (!st || !packet || length <= 0 || !pcm || !output ||
	moveqz	a8, a9, a2	# tmp64, tmp65, decoder
# @OPUS@\upstream\src\opus_decoder.c:922: {
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\src\opus_decoder.c:926:    if (!st || !packet || length <= 0 || !pcm || !output ||
	extui	a8, a8, 0, 8	# tmp67, tmp64
	bnez.n	a8, .L316	# tmp67,
	moveqz	a8, a9, a3	# tmp72, tmp65, packet
	bnez.n	a8, .L316	# tmp72,
# @OPUS@\upstream\src\opus_decoder.c:926:    if (!st || !packet || length <= 0 || !pcm || !output ||
	addi.n	a8, a4, -1	# tmp75, length,
	or	a8, a4, a8	# tmp76, length, tmp75
# @OPUS@\upstream\src\opus_decoder.c:926:    if (!st || !packet || length <= 0 || !pcm || !output ||
	extui	a8, a8, 31, 1	# tmp78, tmp76,
	bnez.n	a8, .L316	# tmp78,
	moveqz	a8, a9, a5	# tmp83, tmp65, pcm
	bnez.n	a8, .L316	# tmp83,
# @OPUS@\upstream\src\opus_decoder.c:927:        frame_capacity <= 0 || frame_capacity > 960 || st->Fs != 48000 || st->channels != 1)
	addi.n	a10, a6, -1	# tmp84, frame_capacity,
	movi	a11, 0x3bf	# tmp87,
	bltu	a11, a10, .L316	# tmp87, tmp84,
# @OPUS@\upstream\src\opus_decoder.c:927:        frame_capacity <= 0 || frame_capacity > 960 || st->Fs != 48000 || st->channels != 1)
	moveqz	a8, a9, a7	# tmp93, tmp65, output
	bnez.n	a8, .L316	# tmp93,
# @OPUS@\upstream\src\opus_decoder.c:927:        frame_capacity <= 0 || frame_capacity > 960 || st->Fs != 48000 || st->channels != 1)
	l32r	a9, .LC33	#, tmp94
	l32i.n	a10, a2, 12	# MEM[(struct OpusDecoder *)decoder_14(D)].Fs, MEM[(struct OpusDecoder *)decoder_14(D)].Fs
	bne	a10, a9, .L316	# MEM[(struct OpusDecoder *)decoder_14(D)].Fs, tmp94,
# @OPUS@\upstream\src\opus_decoder.c:927:        frame_capacity <= 0 || frame_capacity > 960 || st->Fs != 48000 || st->channels != 1)
	l32i.n	a9, a2, 8	# MEM[(struct OpusDecoder *)decoder_14(D)].channels, MEM[(struct OpusDecoder *)decoder_14(D)].channels
	bnei	a9, 1, .L316	# MEM[(struct OpusDecoder *)decoder_14(D)].channels,,
# @OPUS@\upstream\src\opus_decoder.c:929:    return opus_decode_native_impl(st, packet, length, pcm, frame_capacity, 0,
	l32i.n	a9, sp, 48	# context, context
	s32i.n	a7, sp, 12	#, output
	s32i.n	a9, sp, 16	#, context
	s32i.n	a8, sp, 8	#, tmp93
	s32i.n	a8, sp, 4	#, tmp93
	s32i.n	a8, sp, 0	#, tmp93
	mov.n	a7, a8	#, tmp93
	call0	opus_decode_native_impl$isra$3		#
	j	.L309		#
.L316:
# @OPUS@\upstream\src\opus_decoder.c:928:       return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
.L309:
# @OPUS@\upstream\src\opus_decoder.c:931: }
	l32i.n	a0, sp, 44	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	yoradio_opus_decode_blocks_native, .-yoradio_opus_decode_blocks_native
	.section	.text.opus_decode,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_decode
	.type	opus_decode, @function
# Function: opus_decode
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #ifdef FIXED_POINT
# C context:
# C context: int opus_decode(OpusDecoder *st, const unsigned char *data,
# C context: opus_int32 len, opus_val16 *pcm, int frame_size, int decode_fec)
# C context: {
# C context: if(frame_size<=0)
# C context: return OPUS_BAD_ARG;
opus_decode:
	addi	sp, sp, -48	#,,
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\src\opus_decoder.c:952:    if(frame_size<=0)
	blti	a6, 1, .L320	# frame_size,,
# @OPUS@\upstream\src\opus_decoder.c:914:    return opus_decode_native_impl(st, data, len, pcm, frame_size, decode_fec,
	movi.n	a8, 0	# tmp49,
	s32i.n	a8, sp, 16	#, tmp49
	s32i.n	a8, sp, 12	#, tmp49
	s32i.n	a8, sp, 8	#, tmp49
	s32i.n	a8, sp, 4	#, tmp49
	s32i.n	a8, sp, 0	#, tmp49
	call0	opus_decode_native_impl$isra$3		#
# @OPUS@\upstream\src\opus_decoder.c:954:    return opus_decode_native(st, data, len, pcm, frame_size, decode_fec, 0, NULL, 0, NULL, 0);
	j	.L318		#
.L320:
# @OPUS@\upstream\src\opus_decoder.c:953:       return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
.L318:
# @OPUS@\upstream\src\opus_decoder.c:955: }
	l32i.n	a0, sp, 44	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	opus_decode, .-opus_decode
	.section	.text.opus_decoder_ctl,"ax",@progbits
	.literal_position
	.literal .LC34, -4009
	.literal .LC35, .L324
	.literal .LC36, 4010
	.literal .LC37, 4028
	.literal .LC38, 4033
	.literal .LC39, 32768
	.literal .LC40, 65535
	.literal .LC41, 4046
	.literal .LC42, 4047
	.align	4
	.global	opus_decoder_ctl
	.type	opus_decoder_ctl, @function
# Function: opus_decoder_ctl
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #endif
# C context:
# C context: int opus_decoder_ctl(OpusDecoder *st, int request, ...)
# C context: {
# C context: int ret = OPUS_OK;
# C context: va_list ap;
# C context: void *silk_dec;
opus_decoder_ctl:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 56	#,
	mov.n	a12, a2	# st, st
# @OPUS@\upstream\src\opus_decoder.c:1048:    celt_dec = (CELTDecoder*)((char*)st+st->celt_dec_offset);
	l32i.n	a2, a2, 0	# st_27(D)->celt_dec_offset, st_27(D)->celt_dec_offset
# @OPUS@\upstream\src\opus_decoder.c:1051:    va_start(ap, request);
	s32i.n	a4, sp, 24	#,
	addi	a4, sp, 16	# tmp155,,
	s32i.n	a4, sp, 4	# MEM[(struct  *)&ap].__va_reg, tmp155
	addi	a4, sp, 32	# tmp156,,
	s32i.n	a4, sp, 0	# MEM[(struct  *)&ap].__va_stk, tmp156
	movi.n	a4, 8	# tmp157,
	s32i.n	a4, sp, 8	# MEM[(struct  *)&ap].__va_ndx, tmp157
# @OPUS@\upstream\src\opus_decoder.c:1053:    switch (request)
	l32r	a4, .LC34	#, tmp159
# @OPUS@\upstream\src\opus_decoder.c:1041: {
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
# @OPUS@\upstream\src\opus_decoder.c:1051:    va_start(ap, request);
	s32i.n	a5, sp, 28	#,
	s32i.n	a6, sp, 32	#,
	s32i.n	a7, sp, 36	#,
# @OPUS@\upstream\src\opus_decoder.c:1053:    switch (request)
	add.n	a3, a3, a4	# tmp158, request, tmp159
# @OPUS@\upstream\src\opus_decoder.c:1041: {
	s32i.n	a0, sp, 60	#,
# @OPUS@\upstream\src\opus_decoder.c:1053:    switch (request)
	movi.n	a4, 0x26	# tmp160,
# @OPUS@\upstream\src\opus_decoder.c:1047:    silk_dec = (char*)st+st->silk_dec_offset;
	l32i.n	a14, a12, 4	# st_27(D)->silk_dec_offset, _1
# @OPUS@\upstream\src\opus_decoder.c:1048:    celt_dec = (CELTDecoder*)((char*)st+st->celt_dec_offset);
	add.n	a13, a12, a2	# celt_dec, st, st_27(D)->celt_dec_offset
# @OPUS@\upstream\src\opus_decoder.c:1053:    switch (request)
	bltu	a4, a3, .L373	# tmp160, tmp158,
	l32r	a2, .LC35	#, tmp161
	slli	a3, a3, 2	# tmp162, tmp158,
	add.n	a3, a2, a3	# tmp163, tmp161, tmp162
	l32i.n	a2, a3, 0	#, tmp164
	jx	a2		# tmp164
	.section	.rodata.opus_decoder_ctl,"a",@progbits
	.align	4
	.align	4
.L324:
	.word	.L335
	.word	.L334
	.word	.L333
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L332
	.word	.L331
	.word	.L373
	.word	.L330
	.word	.L373
	.word	.L329
	.word	.L328
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L327
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L373
	.word	.L326
	.word	.L325
	.word	.L323
	.section	.text.opus_decoder_ctl
.L335:
# @OPUS@\upstream\src\opus_decoder.c:1057:       opus_int32 *value = va_arg(ap, opus_int32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp165,
	mov.n	a4, a2	# D.5816, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L336	# tmp165, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5818
	j	.L337		#
.L336:
	blt	a3, a4, .L338	# tmp165, D.5816,
	movi.n	a2, 0x24	# tmp167,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp167
.L338:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5818
.L337:
	add.n	a2, a3, a2	# tmp169, D.5818, ap.__va_ndx
	addi	a2, a2, -4	# tmp170, tmp169,
	l32i.n	a3, a2, 0	# MEM[(opus_int32 * *)_121], value
# @OPUS@\upstream\src\opus_decoder.c:1058:       if (!value)
	beqz.n	a3, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1062:       *value = st->bandwidth;
	l32i.n	a4, a12, 60	# st_27(D)->bandwidth, _5
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1062:       *value = st->bandwidth;
	s32i.n	a4, a3, 0	#* value, _5
# @OPUS@\upstream\src\opus_decoder.c:1064:    break;
	j	.L321		#
.L334:
# @OPUS@\upstream\src\opus_decoder.c:1067:        opus_int32 value = va_arg(ap, opus_int32);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp171,
	mov.n	a4, a2	# D.5828, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L340	# tmp171, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5830
	j	.L341		#
.L340:
	blt	a3, a4, .L342	# tmp171, D.5828,
	movi.n	a2, 0x24	# tmp173,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp173
.L342:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5830
.L341:
	add.n	a2, a3, a2	# tmp175, D.5830, ap.__va_ndx
	addi	a2, a2, -4	# tmp176, tmp175,
	l32i.n	a4, a2, 0	# MEM[(opus_int32 *)_132], value
# @OPUS@\upstream\src\opus_decoder.c:1068:        if(value<0 || value>10)
	movi.n	a2, 0xa	# tmp177,
	bltu	a2, a4, .L339	# tmp177, value,
# @OPUS@\upstream\src\opus_decoder.c:1073:        celt_decoder_ctl(celt_dec, OPUS_SET_COMPLEXITY(value));
	l32r	a3, .LC36	#,
# @OPUS@\upstream\src\opus_decoder.c:1072:        st->complexity = value;
	s32i.n	a4, a12, 48	# st_27(D)->complexity, value
# @OPUS@\upstream\src\opus_decoder.c:1073:        celt_decoder_ctl(celt_dec, OPUS_SET_COMPLEXITY(value));
	mov.n	a2, a13	#, celt_dec
	call0	opus_custom_decoder_ctl		#
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1075:    break;
	j	.L321		#
.L333:
# @OPUS@\upstream\src\opus_decoder.c:1078:        opus_int32 *value = va_arg(ap, opus_int32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp179,
	mov.n	a4, a2	# D.5840, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L343	# tmp179, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5842
	j	.L344		#
.L343:
	blt	a3, a4, .L345	# tmp179, D.5840,
	movi.n	a2, 0x24	# tmp181,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp181
.L345:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5842
.L344:
	add.n	a2, a3, a2	# tmp183, D.5842, ap.__va_ndx
	addi	a2, a2, -4	# tmp184, tmp183,
	l32i.n	a3, a2, 0	# MEM[(opus_int32 * *)_143], value
# @OPUS@\upstream\src\opus_decoder.c:1079:        if (!value)
	beqz.n	a3, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1083:        *value = st->complexity;
	l32i.n	a4, a12, 48	# st_27(D)->complexity, _7
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1083:        *value = st->complexity;
	s32i.n	a4, a3, 0	#* value, _7
# @OPUS@\upstream\src\opus_decoder.c:1085:    break;
	j	.L321		#
.L330:
# @OPUS@\upstream\src\opus_decoder.c:1088:       opus_uint32 *value = va_arg(ap, opus_uint32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp185,
	mov.n	a4, a2	# D.5852, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L346	# tmp185, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5854
	j	.L347		#
.L346:
	blt	a3, a4, .L348	# tmp185, D.5852,
	movi.n	a2, 0x24	# tmp187,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp187
.L348:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5854
.L347:
	add.n	a2, a3, a2	# tmp189, D.5854, ap.__va_ndx
	addi	a2, a2, -4	# tmp190, tmp189,
	l32i.n	a3, a2, 0	# MEM[(opus_uint32 * *)_154], value
# @OPUS@\upstream\src\opus_decoder.c:1089:       if (!value)
	beqz.n	a3, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1093:       *value = st->rangeFinal;
	l32i	a4, a12, 84	# st_27(D)->rangeFinal, _8
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1093:       *value = st->rangeFinal;
	s32i.n	a4, a3, 0	#* value, _8
# @OPUS@\upstream\src\opus_decoder.c:1095:    break;
	j	.L321		#
.L332:
# @OPUS@\upstream\src\opus_decoder.c:1098:       OPUS_CLEAR((char*)&st->OPUS_DECODER_RESET_START,
	movi.n	a4, 1	#,
	movi.n	a3, 0x20	#,
	addi	a2, a12, 56	#, st,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\src\opus_decoder.c:1102:       celt_decoder_ctl(celt_dec, OPUS_RESET_STATE);
	l32r	a3, .LC37	#,
	mov.n	a2, a13	#, celt_dec
	call0	opus_custom_decoder_ctl		#
# @OPUS@\upstream\src\opus_decoder.c:1103:       silk_ResetDecoder( silk_dec );
	add.n	a2, a12, a14	#, st, _1
	call0	silk_ResetDecoder		#
# @OPUS@\upstream\src\opus_decoder.c:1104:       st->stream_channels = st->channels;
	l32i.n	a3, a12, 8	# st_27(D)->channels, st_27(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:1105:       st->frame_size = st->Fs/400;
	l32i.n	a2, a12, 12	# st_27(D)->Fs,
# @OPUS@\upstream\src\opus_decoder.c:1104:       st->stream_channels = st->channels;
	s32i.n	a3, a12, 56	# st_27(D)->stream_channels, st_27(D)->channels
# @OPUS@\upstream\src\opus_decoder.c:1105:       st->frame_size = st->Fs/400;
	movi	a3, 0x190	#,
	call0	__divsi3		#
# @OPUS@\upstream\src\opus_decoder.c:1105:       st->frame_size = st->Fs/400;
	s32i	a2, a12, 72	# st_27(D)->frame_size,
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1110:    break;
	j	.L321		#
.L331:
# @OPUS@\upstream\src\opus_decoder.c:1113:       opus_int32 *value = va_arg(ap, opus_int32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp200,
	mov.n	a4, a2	# D.5864, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L349	# tmp200, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5866
	j	.L350		#
.L349:
	blt	a3, a4, .L351	# tmp200, D.5864,
	movi.n	a2, 0x24	# tmp202,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp202
.L351:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5866
.L350:
	add.n	a2, a3, a2	# tmp204, D.5866, ap.__va_ndx
	addi	a2, a2, -4	# tmp205, tmp204,
	l32i.n	a3, a2, 0	# MEM[(opus_int32 * *)_165], value
# @OPUS@\upstream\src\opus_decoder.c:1114:       if (!value)
	beqz.n	a3, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1118:       *value = st->Fs;
	l32i.n	a4, a12, 12	# st_27(D)->Fs, _13
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1118:       *value = st->Fs;
	s32i.n	a4, a3, 0	#* value, _13
# @OPUS@\upstream\src\opus_decoder.c:1120:    break;
	j	.L321		#
.L329:
# @OPUS@\upstream\src\opus_decoder.c:1123:       opus_int32 *value = va_arg(ap, opus_int32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp206,
	mov.n	a4, a2	# D.5876, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L352	# tmp206, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5878
	j	.L353		#
.L352:
	blt	a3, a4, .L354	# tmp206, D.5876,
	movi.n	a2, 0x24	# tmp208,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp208
.L354:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5878
.L353:
	add.n	a2, a3, a2	# tmp210, D.5878, ap.__va_ndx
	addi	a2, a2, -4	# tmp211, tmp210,
	l32i.n	a4, a2, 0	# MEM[(opus_int32 * *)_176], value
# @OPUS@\upstream\src\opus_decoder.c:1124:       if (!value)
	beqz.n	a4, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1128:       if (st->prev_mode == MODE_CELT_ONLY)
	l32i	a3, a12, 68	# st_27(D)->prev_mode, st_27(D)->prev_mode
	movi	a2, 0x3ea	# tmp212,
	bne	a3, a2, .L355	# st_27(D)->prev_mode, tmp212,
# @OPUS@\upstream\src\opus_decoder.c:1129:          ret = celt_decoder_ctl(celt_dec, OPUS_GET_PITCH(value));
	l32r	a3, .LC38	#,
	mov.n	a2, a13	#, celt_dec
	call0	opus_custom_decoder_ctl		#
	j	.L321		#
.L355:
# @OPUS@\upstream\src\opus_decoder.c:1131:          *value = st->DecControl.prevPitchLag;
	l32i.n	a3, a12, 36	# st_27(D)->DecControl.prevPitchLag, _15
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1131:          *value = st->DecControl.prevPitchLag;
	s32i.n	a3, a4, 0	# *value_54, _15
	j	.L321		#
.L326:
# @OPUS@\upstream\src\opus_decoder.c:1136:       opus_int32 *value = va_arg(ap, opus_int32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp215,
	mov.n	a4, a2	# D.5888, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L356	# tmp215, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5890
	j	.L357		#
.L356:
	blt	a3, a4, .L358	# tmp215, D.5888,
	movi.n	a2, 0x24	# tmp217,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp217
.L358:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5890
.L357:
	add.n	a2, a3, a2	# tmp219, D.5890, ap.__va_ndx
	addi	a2, a2, -4	# tmp220, tmp219,
	l32i.n	a3, a2, 0	# MEM[(opus_int32 * *)_187], value
# @OPUS@\upstream\src\opus_decoder.c:1137:       if (!value)
	beqz.n	a3, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1141:       *value = st->decode_gain;
	l32i.n	a4, a12, 44	# st_27(D)->decode_gain, _16
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1141:       *value = st->decode_gain;
	s32i.n	a4, a3, 0	#* value, _16
# @OPUS@\upstream\src\opus_decoder.c:1143:    break;
	j	.L321		#
.L328:
# @OPUS@\upstream\src\opus_decoder.c:1146:        opus_int32 value = va_arg(ap, opus_int32);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp221,
	mov.n	a4, a2	# D.5900, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L359	# tmp221, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5902
	j	.L360		#
.L359:
	blt	a3, a4, .L361	# tmp221, D.5900,
	movi.n	a2, 0x24	# tmp223,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp223
.L361:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5902
.L360:
	add.n	a2, a3, a2	# tmp225, D.5902, ap.__va_ndx
	addi	a2, a2, -4	# tmp226, tmp225,
	l32i.n	a3, a2, 0	# MEM[(opus_int32 *)_198], value
# @OPUS@\upstream\src\opus_decoder.c:1147:        if (value<-32768 || value>32767)
	l32r	a2, .LC39	#, tmp228
# @OPUS@\upstream\src\opus_decoder.c:1147:        if (value<-32768 || value>32767)
	l32r	a4, .LC40	#, tmp229
# @OPUS@\upstream\src\opus_decoder.c:1147:        if (value<-32768 || value>32767)
	add.n	a2, a3, a2	# tmp227, value, tmp228
# @OPUS@\upstream\src\opus_decoder.c:1147:        if (value<-32768 || value>32767)
	bltu	a4, a2, .L339	# tmp229, tmp227,
# @OPUS@\upstream\src\opus_decoder.c:1151:        st->decode_gain = value;
	s32i.n	a3, a12, 44	# st_27(D)->decode_gain, value
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1153:    break;
	j	.L321		#
.L327:
# @OPUS@\upstream\src\opus_decoder.c:1156:       opus_int32 *value = va_arg(ap, opus_int32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp230,
	mov.n	a4, a2	# D.5912, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L362	# tmp230, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5914
	j	.L363		#
.L362:
	blt	a3, a4, .L364	# tmp230, D.5912,
	movi.n	a2, 0x24	# tmp232,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp232
.L364:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5914
.L363:
	add.n	a2, a3, a2	# tmp234, D.5914, ap.__va_ndx
	addi	a2, a2, -4	# tmp235, tmp234,
	l32i.n	a3, a2, 0	# MEM[(opus_int32 * *)_209], value
# @OPUS@\upstream\src\opus_decoder.c:1157:       if (!value)
	beqz.n	a3, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1161:       *value = st->last_packet_duration;
	l32i	a4, a12, 80	# st_27(D)->last_packet_duration, _19
# @OPUS@\upstream\src\opus_decoder.c:1042:    int ret = OPUS_OK;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1161:       *value = st->last_packet_duration;
	s32i.n	a4, a3, 0	#* value, _19
# @OPUS@\upstream\src\opus_decoder.c:1163:    break;
	j	.L321		#
.L325:
# @OPUS@\upstream\src\opus_decoder.c:1166:        opus_int32 value = va_arg(ap, opus_int32);
	l32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	movi.n	a3, 0x18	# tmp236,
	mov.n	a4, a2	# D.5924, ap.__va_ndx
	addi.n	a2, a2, 4	# ap.__va_ndx, ap.__va_ndx,
	s32i.n	a2, sp, 8	# ap.__va_ndx, ap.__va_ndx
	blt	a3, a2, .L365	# tmp236, ap.__va_ndx,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5926
	j	.L366		#
.L365:
	blt	a3, a4, .L367	# tmp236, D.5924,
	movi.n	a2, 0x24	# tmp238,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp238
.L367:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5926
.L366:
	add.n	a2, a3, a2	# tmp240, D.5926, ap.__va_ndx
	addi	a2, a2, -4	# tmp241, tmp240,
	l32i.n	a4, a2, 0	# MEM[(opus_int32 *)_220], value
# @OPUS@\upstream\src\opus_decoder.c:1167:        if(value<0 || value>1)
	bgeui	a4, 2, .L339	# value,,
# @OPUS@\upstream\src\opus_decoder.c:1171:        ret = celt_decoder_ctl(celt_dec, OPUS_SET_PHASE_INVERSION_DISABLED(value));
	l32r	a3, .LC41	#,
	mov.n	a2, a13	#, celt_dec
	call0	opus_custom_decoder_ctl		#
# @OPUS@\upstream\src\opus_decoder.c:1173:    break;
	j	.L321		#
.L323:
# @OPUS@\upstream\src\opus_decoder.c:1176:        opus_int32 *value = va_arg(ap, opus_int32*);
	l32i.n	a2, sp, 8	# ap.__va_ndx, D.5936
	movi.n	a4, 0x18	# tmp243,
	addi.n	a3, a2, 4	# D.5937, D.5936,
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5937
	blt	a4, a3, .L368	# tmp243, D.5937,
	l32i.n	a3, sp, 4	# ap.__va_reg, D.5938
	j	.L369		#
.L368:
	blt	a4, a2, .L371	# tmp243, D.5936,
	movi.n	a2, 0x24	# tmp245,
	s32i.n	a2, sp, 8	# ap.__va_ndx, tmp245
	movi.n	a2, 0x20	# _114,
.L371:
	l32i.n	a3, sp, 0	# ap.__va_stk, D.5938
.L369:
	add.n	a2, a3, a2	# tmp246, D.5938, _114
	l32i.n	a4, a2, 0	# MEM[(opus_int32 * *)_231], value
# @OPUS@\upstream\src\opus_decoder.c:1177:        if (!value)
	beqz.n	a4, .L339	# value,
# @OPUS@\upstream\src\opus_decoder.c:1181:        ret = celt_decoder_ctl(celt_dec, OPUS_GET_PHASE_INVERSION_DISABLED(value));
	l32r	a3, .LC42	#,
	mov.n	a2, a13	#, celt_dec
	call0	opus_custom_decoder_ctl		#
# @OPUS@\upstream\src\opus_decoder.c:1183:    break;
	j	.L321		#
.L373:
# @OPUS@\upstream\src\opus_decoder.c:1200:       ret = OPUS_UNIMPLEMENTED;
	movi.n	a2, -5	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1205:    return ret;
	j	.L321		#
.L339:
# @OPUS@\upstream\src\opus_decoder.c:1208:    return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
.L321:
# @OPUS@\upstream\src\opus_decoder.c:1209: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	opus_decoder_ctl, .-opus_decoder_ctl
	.section	.text.opus_decoder_destroy,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_decoder_destroy
	.type	opus_decoder_destroy, @function
# Function: opus_decoder_destroy
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return OPUS_BAD_ARG;
# C context: }
# C context:
# C context: void opus_decoder_destroy(OpusDecoder *st)
# C context: {
# C context: opus_free(st);
# C context: }
# C context:
opus_decoder_destroy:
	addi	sp, sp, -16	#,,
	s32i.n	a0, sp, 12	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\os_support.h:83:    free(ptr);
	call0	free		#
# @OPUS@\upstream\src\opus_decoder.c:1214: }
	l32i.n	a0, sp, 12	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	opus_decoder_destroy, .-opus_decoder_destroy
	.section	.text.opus_packet_get_bandwidth,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_packet_get_bandwidth
	.type	opus_packet_get_bandwidth, @function
# Function: opus_packet_get_bandwidth
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return OPUS_BAD_ARG;
# C context:
# C context: packet_mode = opus_packet_get_mode(data);
# C context: packet_bandwidth = opus_packet_get_bandwidth(data);
# C context: packet_frame_size = opus_packet_get_samples_per_frame(data, st->Fs);
# C context: packet_stream_channels = opus_packet_get_nb_channels(data);
# C context:
# C context: count = opus_packet_parse_impl(data, len, self_delimited, &toc, NULL,
opus_packet_get_bandwidth:
# @OPUS@\upstream\src\opus_decoder.c:1220:    if (data[0]&0x80)
	l8ui	a2, a2, 0	# *data_9(D), _1
# @OPUS@\upstream\src\opus_decoder.c:1220:    if (data[0]&0x80)
	slli	a3, a2, 24	# tmp54, _1,
	bgez	a3, .L400	# tmp54,
# @OPUS@\upstream\src\opus_decoder.c:1222:       bandwidth = OPUS_BANDWIDTH_MEDIUMBAND + ((data[0]>>5)&0x3);
	extui	a3, a2, 5, 2	# tmp58, _1,,
# @OPUS@\upstream\src\opus_decoder.c:1222:       bandwidth = OPUS_BANDWIDTH_MEDIUMBAND + ((data[0]>>5)&0x3);
	movi	a2, 0x44e	# tmp59,
	add.n	a2, a3, a2	# <retval>, tmp58, tmp59
# @OPUS@\upstream\src\opus_decoder.c:1224:          bandwidth = OPUS_BANDWIDTH_NARROWBAND;
	movi	a4, 0x44d	# tmp74,
	moveqz	a2, a4, a3	# <retval>, tmp74, tmp58
	j	.L399		#
.L400:
# @OPUS@\upstream\src\opus_decoder.c:1225:    } else if ((data[0]&0x60) == 0x60)
	movi	a3, 0x60	# tmp61,
	and	a3, a2, a3	# tmp64, _1, tmp61
	movi	a4, 0x60	# tmp65,
	bne	a3, a4, .L402	# tmp64, tmp65,
# @OPUS@\upstream\src\opus_decoder.c:1227:       bandwidth = (data[0]&0x10) ? OPUS_BANDWIDTH_FULLBAND :
	extui	a2, a2, 4, 1	# tmp69, _1,,
	movi	a3, 0x451	# tmp80,
	movi	a4, 0x450	# tmp81,
	movnez	a4, a3, a2	# tmp81, tmp80, tmp69
	mov.n	a2, a4	# <retval>, tmp81
	j	.L399		#
.L402:
# @OPUS@\upstream\src\opus_decoder.c:1230:       bandwidth = OPUS_BANDWIDTH_NARROWBAND + ((data[0]>>5)&0x3);
	srli	a2, a2, 5	# tmp71, _1,
# @OPUS@\upstream\src\opus_decoder.c:1230:       bandwidth = OPUS_BANDWIDTH_NARROWBAND + ((data[0]>>5)&0x3);
	movi	a3, 0x44d	# tmp72,
	add.n	a2, a2, a3	# <retval>, tmp71, tmp72
.L399:
# @OPUS@\upstream\src\opus_decoder.c:1233: }
	ret.n
	.size	opus_packet_get_bandwidth, .-opus_packet_get_bandwidth
	.section	.text.opus_packet_get_nb_channels,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_packet_get_nb_channels
	.type	opus_packet_get_nb_channels, @function
# Function: opus_packet_get_nb_channels
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: packet_mode = opus_packet_get_mode(data);
# C context: packet_bandwidth = opus_packet_get_bandwidth(data);
# C context: packet_frame_size = opus_packet_get_samples_per_frame(data, st->Fs);
# C context: packet_stream_channels = opus_packet_get_nb_channels(data);
# C context:
# C context: count = opus_packet_parse_impl(data, len, self_delimited, &toc, NULL,
# C context: size, &offset, packet_offset, NULL, NULL);
# C context: if (count<0)
opus_packet_get_nb_channels:
# @OPUS@\upstream\src\opus_decoder.c:1237:    return (data[0]&0x4) ? 2 : 1;
	l8ui	a3, a2, 0	# *data_4(D),
# @OPUS@\upstream\src\opus_decoder.c:1238: }
	movi.n	a4, 2	# tmp55,
# @OPUS@\upstream\src\opus_decoder.c:1237:    return (data[0]&0x4) ? 2 : 1;
	extui	a3, a3, 2, 1	# tmp50, *data_4(D),,
# @OPUS@\upstream\src\opus_decoder.c:1238: }
	movi.n	a2, 1	# tmp56,
	movnez	a2, a4, a3	#, tmp55, tmp50
	ret.n
	.size	opus_packet_get_nb_channels, .-opus_packet_get_nb_channels
	.section	.text.opus_packet_get_nb_frames,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_packet_get_nb_frames
	.type	opus_packet_get_nb_frames, @function
# Function: opus_packet_get_nb_frames
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return (data[0]&0x4) ? 2 : 1;
# C context: }
# C context:
# C context: int opus_packet_get_nb_frames(const unsigned char packet[], opus_int32 len)
# C context: {
# C context: int count;
# C context: if (len<1)
# C context: return OPUS_BAD_ARG;
opus_packet_get_nb_frames:
# @OPUS@\upstream\src\opus_decoder.c:1241: {
	mov.n	a5, a2	# packet, packet
# @OPUS@\upstream\src\opus_decoder.c:1243:    if (len<1)
	blti	a3, 1, .L409	# len,,
	l8ui	a4, a2, 0	# *packet_6(D),
# @OPUS@\upstream\src\opus_decoder.c:1247:       return 1;
	movi.n	a2, 1	# <retval>,
	extui	a4, a4, 0, 2	# _9, *packet_6(D),
# @OPUS@\upstream\src\opus_decoder.c:1246:    if (count==0)
	beqz.n	a4, .L407	# _9,
# @OPUS@\upstream\src\opus_decoder.c:1249:       return 2;
	movi.n	a2, 2	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1248:    else if (count!=3)
	bnei	a4, 3, .L407	# _9,,
# @OPUS@\upstream\src\opus_decoder.c:1250:    else if (len<2)
	beqi	a3, 1, .L412	# len,,
# @OPUS@\upstream\src\opus_decoder.c:1253:       return packet[1]&0x3F;
	l8ui	a2, a5, 1	# MEM[(const unsigned char *)packet_6(D) + 1B],
	extui	a2, a2, 0, 6	# <retval>, MEM[(const unsigned char *)packet_6(D) + 1B],
	j	.L407		#
.L409:
# @OPUS@\upstream\src\opus_decoder.c:1244:       return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
	j	.L407		#
.L412:
# @OPUS@\upstream\src\opus_decoder.c:1251:       return OPUS_INVALID_PACKET;
	movi.n	a2, -4	# <retval>,
.L407:
# @OPUS@\upstream\src\opus_decoder.c:1254: }
	ret.n
	.size	opus_packet_get_nb_frames, .-opus_packet_get_nb_frames
	.section	.text.opus_packet_get_nb_samples,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_packet_get_nb_samples
	.type	opus_packet_get_nb_samples, @function
# Function: opus_packet_get_nb_samples
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return packet[1]&0x3F;
# C context: }
# C context:
# C context: int opus_packet_get_nb_samples(const unsigned char packet[], opus_int32 len,
# C context: opus_int32 Fs)
# C context: {
# C context: int samples;
# C context: int count = opus_packet_get_nb_frames(packet, len);
opus_packet_get_nb_samples:
	addi	sp, sp, -16	#,,
	s32i.n	a13, sp, 4	#,
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\src\opus_decoder.c:1258: {
	mov.n	a13, a4	# Fs, Fs
# @OPUS@\upstream\src\opus_decoder.c:1243:    if (len<1)
	blti	a3, 1, .L419	# len,,
	l8ui	a5, a2, 0	# *packet_7(D),
	extui	a5, a5, 0, 2	# _14, *packet_7(D),
# @OPUS@\upstream\src\opus_decoder.c:1246:    if (count==0)
	beqz.n	a5, .L420	# _14,
# @OPUS@\upstream\src\opus_decoder.c:1248:    else if (count!=3)
	bnei	a5, 3, .L421	# _14,,
# @OPUS@\upstream\src\opus_decoder.c:1250:    else if (len<2)
	bnei	a3, 1, .L417	# len,,
.L418:
# @OPUS@\upstream\src\opus_decoder.c:1251:       return OPUS_INVALID_PACKET;
	movi.n	a2, -4	# <retval>,
	j	.L414		#
.L417:
# @OPUS@\upstream\src\opus_decoder.c:1253:       return packet[1]&0x3F;
	l8ui	a12, a2, 1	# MEM[(const unsigned char *)packet_7(D) + 1B],
	extui	a12, a12, 0, 6	# _18, MEM[(const unsigned char *)packet_7(D) + 1B],
	j	.L416		#
.L420:
# @OPUS@\upstream\src\opus_decoder.c:1247:       return 1;
	movi.n	a12, 1	# _18,
	j	.L416		#
.L421:
# @OPUS@\upstream\src\opus_decoder.c:1249:       return 2;
	movi.n	a12, 2	# _18,
.L416:
# @OPUS@\upstream\src\opus_decoder.c:1265:    samples = count*opus_packet_get_samples_per_frame(packet, Fs);
	mov.n	a3, a13	#, Fs
	call0	opus_packet_get_samples_per_frame		#
# @OPUS@\upstream\src\opus_decoder.c:1265:    samples = count*opus_packet_get_samples_per_frame(packet, Fs);
	mull	a2, a2, a12	# <retval>,, _18
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	slli	a4, a13, 1	# tmp64, Fs,
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	slli	a3, a2, 2	# tmp59, <retval>,
	add.n	a3, a3, a2	# tmp60, tmp59, <retval>
	slli	a5, a3, 2	# tmp61, tmp60,
	add.n	a3, a3, a5	# tmp62, tmp60, tmp61
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	add.n	a4, a4, a13	# tmp65, tmp64, Fs
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	bge	a4, a3, .L414	# tmp65, tmp62,
	j	.L418		#
.L419:
# @OPUS@\upstream\src\opus_decoder.c:1244:       return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
.L414:
# @OPUS@\upstream\src\opus_decoder.c:1271: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	opus_packet_get_nb_samples, .-opus_packet_get_nb_samples
	.section	.text.opus_packet_has_lbrr,"ax",@progbits
	.literal_position
	.literal .LC43, 48000
	.align	4
	.global	opus_packet_has_lbrr
	.type	opus_packet_has_lbrr, @function
# Function: opus_packet_has_lbrr
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return samples;
# C context: }
# C context:
# C context: int opus_packet_has_lbrr(const unsigned char packet[], opus_int32 len)
# C context: {
# C context: int ret;
# C context: const unsigned char *frames[48];
# C context: opus_int16 size[48];
opus_packet_has_lbrr:
	movi	a9, 0x130	#,
	sub	sp, sp, a9	#,,
	s32i	a12, sp, 296	#,
	s32i	a13, sp, 292	#,
	s32i	a0, sp, 300	#,
	s32i	a14, sp, 288	#,
# @OPUS@\upstream\src\opus_decoder.c:260:    if (data[0]&0x80)
	l8ui	a4, a2, 0	# *packet_14(D),
# @OPUS@\upstream\src\opus_decoder.c:1274: {
	mov.n	a12, a2	# packet, packet
	mov.n	a13, a3	# len, len
# @OPUS@\upstream\src\opus_decoder.c:1284:       return 0;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:260:    if (data[0]&0x80)
	bbsi	a4, 7, .L422	# *packet_14(D),,
# @OPUS@\upstream\src\opus_decoder.c:1285:    packet_frame_size = opus_packet_get_samples_per_frame(packet, 48000);
	l32r	a3, .LC43	#,
	mov.n	a2, a12	#, packet
	call0	opus_packet_get_samples_per_frame		#
# @OPUS@\upstream\src\opus_decoder.c:1286:    if (packet_frame_size > 960)
	movi	a3, 0x3c0	# tmp72,
# @OPUS@\upstream\src\opus_decoder.c:1279:    int nb_frames=1;
	movi.n	a14, 1	# nb_frames,
# @OPUS@\upstream\src\opus_decoder.c:1286:    if (packet_frame_size > 960)
	bge	a3, a2, .L424	# tmp72, packet_frame_size,
# @OPUS@\upstream\src\opus_decoder.c:1287:       nb_frames = packet_frame_size/960;
	call0	__divsi3		#
	mov.n	a14, a2	# nb_frames,
.L424:
# @OPUS@\upstream\src\opus_decoder.c:1237:    return (data[0]&0x4) ? 2 : 1;
	l8ui	a4, a12, 0	# *packet_14(D),
	movi.n	a2, 4	# tmp78,
	and	a4, a4, a2	# tmp80, *packet_14(D), tmp78
	beqz.n	a4, .L431	# tmp80,
	j	.L425		#
.L432:
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	l32i.n	a2, sp, 0	# frames, frames
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	movi.n	a4, 7	# tmp87,
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	l8ui	a3, a2, 0	# *_35, _37
# @OPUS@\upstream\src\opus_decoder.c:1294:       lbrr = lbrr || ((frames[0][0] >> (6-2*nb_frames)) & 0x1);
	movi.n	a2, 3	# tmp83,
	sub	a2, a2, a14	# tmp84, tmp83, nb_frames
	slli	a2, a2, 1	# tmp85, tmp84,
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	sub	a14, a4, a14	# tmp88, tmp87, nb_frames
# @OPUS@\upstream\src\opus_decoder.c:1294:       lbrr = lbrr || ((frames[0][0] >> (6-2*nb_frames)) & 0x1);
	ssr	a2	# tmp85
	sra	a2, a3	# tmp86, _37
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	ssr	a14	# tmp88
	sra	a3, a3	# tmp89, _37
# @OPUS@\upstream\src\opus_decoder.c:1284:       return 0;
	or	a2, a2, a3	# tmp90, tmp86, tmp89
	extui	a2, a2, 0, 1	# <retval>, tmp90,
	j	.L422		#
.L425:
# @OPUS@\upstream\src\opus_decoder.c:1289:    ret = opus_packet_parse(packet, len, NULL, frames, size, NULL);
	movi.n	a7, 0	#,
	movi	a6, 0xc0	# tmp91,
	add.n	a6, sp, a6	#,, tmp91
	mov.n	a5, sp	#,
	mov.n	a4, a7	#,
	mov.n	a3, a13	#, len
	mov.n	a2, a12	#, packet
	call0	opus_packet_parse		#
# @OPUS@\upstream\src\opus_decoder.c:1290:    if (ret <= 0)
	bgei	a2, 1, .L432	# <retval>,,
	j	.L422		#
.L433:
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	l32i.n	a2, sp, 0	# frames, frames
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	movi.n	a3, 7	# tmp95,
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	l8ui	a2, a2, 0	# *_44, *_44
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	sub	a14, a3, a14	# tmp96, tmp95, nb_frames
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	ssr	a14	# tmp96
	sra	a2, a2	# tmp97, *_44
# @OPUS@\upstream\src\opus_decoder.c:1292:    lbrr = (frames[0][0] >> (7-nb_frames)) & 0x1;
	extui	a2, a2, 0, 1	# <retval>, tmp97,
	j	.L422		#
.L431:
# @OPUS@\upstream\src\opus_decoder.c:1289:    ret = opus_packet_parse(packet, len, NULL, frames, size, NULL);
	movi	a6, 0xc0	# tmp98,
	mov.n	a7, a4	#, tmp80
	add.n	a6, sp, a6	#,, tmp98
	mov.n	a5, sp	#,
	mov.n	a3, a13	#, len
	mov.n	a2, a12	#, packet
	call0	opus_packet_parse		#
# @OPUS@\upstream\src\opus_decoder.c:1290:    if (ret <= 0)
	bgei	a2, 1, .L433	# <retval>,,
.L422:
# @OPUS@\upstream\src\opus_decoder.c:1296: }
	l32i	a0, sp, 300	#,
	movi	a9, 0x130	#,
	l32i	a12, sp, 296	#,
	l32i	a13, sp, 292	#,
	l32i	a14, sp, 288	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	opus_packet_has_lbrr, .-opus_packet_has_lbrr
	.section	.text.opus_decoder_get_nb_samples,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_decoder_get_nb_samples
	.type	opus_decoder_get_nb_samples, @function
# Function: opus_decoder_get_nb_samples
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: if (data != NULL && len > 0 && !decode_fec)
# C context: {
# C context: nb_samples = opus_decoder_get_nb_samples(st, data, len);
# C context: if (nb_samples>0)
# C context: frame_size = IMIN(frame_size, nb_samples);
# C context: else
# C context: return OPUS_INVALID_PACKET;
opus_decoder_get_nb_samples:
	addi	sp, sp, -16	#,,
	s32i.n	a13, sp, 4	#,
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\src\opus_decoder.c:1300: {
	mov.n	a5, a3	# packet, packet
# @OPUS@\upstream\src\opus_decoder.c:1301:    return opus_packet_get_nb_samples(packet, len, dec->Fs);
	l32i.n	a13, a2, 12	# dec_3(D)->Fs, _1
# @OPUS@\upstream\src\opus_decoder.c:1243:    if (len<1)
	blti	a4, 1, .L439	# len,,
	l8ui	a2, a3, 0	# *packet_4(D),
	extui	a2, a2, 0, 2	# _9, *packet_4(D),
# @OPUS@\upstream\src\opus_decoder.c:1246:    if (count==0)
	beqz.n	a2, .L440	# _9,
# @OPUS@\upstream\src\opus_decoder.c:1248:    else if (count!=3)
	bnei	a2, 3, .L441	# _9,,
# @OPUS@\upstream\src\opus_decoder.c:1250:    else if (len<2)
	bnei	a4, 1, .L437	# len,,
.L438:
# @OPUS@\upstream\src\opus_decoder.c:1251:       return OPUS_INVALID_PACKET;
	movi.n	a2, -4	# <retval>,
	j	.L434		#
.L437:
# @OPUS@\upstream\src\opus_decoder.c:1253:       return packet[1]&0x3F;
	l8ui	a2, a3, 1	# MEM[(const unsigned char *)packet_4(D) + 1B],
	extui	a12, a2, 0, 6	# _13, MEM[(const unsigned char *)packet_4(D) + 1B],
	j	.L436		#
.L440:
# @OPUS@\upstream\src\opus_decoder.c:1247:       return 1;
	movi.n	a12, 1	# _13,
	j	.L436		#
.L441:
# @OPUS@\upstream\src\opus_decoder.c:1249:       return 2;
	movi.n	a12, 2	# _13,
.L436:
# @OPUS@\upstream\src\opus_decoder.c:1265:    samples = count*opus_packet_get_samples_per_frame(packet, Fs);
	mov.n	a3, a13	#, _1
	mov.n	a2, a5	#, packet
	call0	opus_packet_get_samples_per_frame		#
# @OPUS@\upstream\src\opus_decoder.c:1265:    samples = count*opus_packet_get_samples_per_frame(packet, Fs);
	mull	a2, a2, a12	# <retval>,, _13
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	slli	a3, a13, 1	# tmp65, _1,
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	slli	a4, a2, 2	# tmp60, <retval>,
	add.n	a4, a4, a2	# tmp61, tmp60, <retval>
	slli	a5, a4, 2	# tmp62, tmp61,
	add.n	a4, a4, a5	# tmp63, tmp61, tmp62
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	add.n	a13, a3, a13	# tmp66, tmp65, _1
# @OPUS@\upstream\src\opus_decoder.c:1267:    if (samples*25 > Fs*3)
	bge	a13, a4, .L434	# tmp66, tmp63,
	j	.L438		#
.L439:
# @OPUS@\upstream\src\opus_decoder.c:1244:       return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
.L434:
# @OPUS@\upstream\src\opus_decoder.c:1302: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	opus_decoder_get_nb_samples, .-opus_decoder_get_nb_samples
	.section	.text.opus_dred_decoder_get_size,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_decoder_get_size
	.type	opus_dred_decoder_get_size, @function
# Function: opus_dred_decoder_get_size
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context:
# C context:
# C context: int opus_dred_decoder_get_size(void)
# C context: {
# C context: return sizeof(OpusDREDDecoder);
# C context: }
# C context:
opus_dred_decoder_get_size:
# @OPUS@\upstream\src\opus_decoder.c:1331: }
	movi.n	a2, 0xc	#,
	ret.n
	.size	opus_dred_decoder_get_size, .-opus_dred_decoder_get_size
	.section	.text.opus_dred_decoder_init,"ax",@progbits
	.literal_position
	.literal .LC44, -655499584
	.align	4
	.global	opus_dred_decoder_init
	.type	opus_dred_decoder_init, @function
# Function: opus_dred_decoder_init
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif
# C context:
# C context: int opus_dred_decoder_init(OpusDREDDecoder *dec)
# C context: {
# C context: int ret = 0;
# C context: dec->loaded = 0;
# C context: #if defined(ENABLE_DRED) && !defined(USE_WEIGHTS_FILE)
opus_dred_decoder_init:
# @OPUS@\upstream\src\opus_decoder.c:1356:    dec->magic = 0xD8EDDEC0;
	l32r	a4, .LC44	#, tmp46
# @OPUS@\upstream\src\opus_decoder.c:1347: {
	mov.n	a3, a2	# dec, dec
# @OPUS@\upstream\src\opus_decoder.c:1349:    dec->loaded = 0;
	movi.n	a2, 0	# tmp44,
	s32i.n	a2, a3, 0	# dec_2(D)->loaded, tmp44
# @OPUS@\upstream\src\opus_decoder.c:1354:    dec->arch = opus_select_arch();
	s32i.n	a2, a3, 4	# dec_2(D)->arch, tmp44
# @OPUS@\upstream\src\opus_decoder.c:1356:    dec->magic = 0xD8EDDEC0;
	s32i.n	a4, a3, 8	# dec_2(D)->magic, tmp46
# @OPUS@\upstream\src\opus_decoder.c:1358: }
	ret.n
	.size	opus_dred_decoder_init, .-opus_dred_decoder_init
	.section	.text.opus_dred_decoder_create,"ax",@progbits
	.literal_position
	.literal .LC45, -655499584
	.align	4
	.global	opus_dred_decoder_create
	.type	opus_dred_decoder_create, @function
# Function: opus_dred_decoder_create
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return (ret == 0) ? OPUS_OK : OPUS_UNIMPLEMENTED;
# C context: }
# C context:
# C context: OpusDREDDecoder *opus_dred_decoder_create(int *error)
# C context: {
# C context: int ret;
# C context: OpusDREDDecoder *dec;
# C context: dec = (OpusDREDDecoder *)opus_alloc(opus_dred_decoder_get_size());
opus_dred_decoder_create:
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 8	#,
	mov.n	a12, a2	# error, error
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\os_support.h:58:    return malloc(size);
	movi.n	a2, 0xc	#,
# @OPUS@\upstream\src\opus_decoder.c:1361: {
	s32i.n	a0, sp, 12	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\os_support.h:58:    return malloc(size);
	call0	malloc		#
# @OPUS@\upstream\src\opus_decoder.c:1365:    if (dec == NULL)
	bnez.n	a2, .L445	# <retval>,
# @OPUS@\upstream\src\opus_decoder.c:1367:       if (error)
	beqz.n	a12, .L444	# error,
# @OPUS@\upstream\src\opus_decoder.c:1368:          *error = OPUS_ALLOC_FAIL;
	movi.n	a3, -7	# tmp45,
	s32i.n	a3, a12, 0	# *error_6(D), tmp45
	j	.L444		#
.L445:
# @OPUS@\upstream\src\opus_decoder.c:1356:    dec->magic = 0xD8EDDEC0;
	l32r	a4, .LC45	#, tmp48
# @OPUS@\upstream\src\opus_decoder.c:1349:    dec->loaded = 0;
	movi.n	a3, 0	# tmp46,
	s32i.n	a3, a2, 0	# MEM[(struct OpusDREDDecoder *)_5].loaded, tmp46
# @OPUS@\upstream\src\opus_decoder.c:1354:    dec->arch = opus_select_arch();
	s32i.n	a3, a2, 4	# MEM[(struct OpusDREDDecoder *)_5].arch, tmp46
# @OPUS@\upstream\src\opus_decoder.c:1356:    dec->magic = 0xD8EDDEC0;
	s32i.n	a4, a2, 8	# MEM[(struct OpusDREDDecoder *)_5].magic, tmp48
# @OPUS@\upstream\src\opus_decoder.c:1372:    if (error)
	beq	a12, a3, .L444	# error,,
# @OPUS@\upstream\src\opus_decoder.c:1373:       *error = ret;
	s32i.n	a3, a12, 0	# *error_6(D), tmp46
.L444:
# @OPUS@\upstream\src\opus_decoder.c:1380: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	opus_dred_decoder_create, .-opus_dred_decoder_create
	.section	.text.opus_dred_decoder_destroy,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_decoder_destroy
	.type	opus_dred_decoder_destroy, @function
# Function: opus_dred_decoder_destroy
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return dec;
# C context: }
# C context:
# C context: void opus_dred_decoder_destroy(OpusDREDDecoder *dec)
# C context: {
# C context: if (dec) dec->magic = 0xDE57801D;
# C context: opus_free(dec);
# C context: }
opus_dred_decoder_destroy:
	addi	sp, sp, -16	#,,
	s32i.n	a0, sp, 12	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\celt\os_support.h:83:    free(ptr);
	call0	free		#
# @OPUS@\upstream\src\opus_decoder.c:1386: }
	l32i.n	a0, sp, 12	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	opus_dred_decoder_destroy, .-opus_dred_decoder_destroy
	.section	.text.opus_dred_decoder_ctl,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_decoder_ctl
	.type	opus_dred_decoder_ctl, @function
# Function: opus_dred_decoder_ctl
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: opus_free(dec);
# C context: }
# C context:
# C context: int opus_dred_decoder_ctl(OpusDREDDecoder *dred_dec, int request, ...)
# C context: {
# C context: #ifdef ENABLE_DRED
# C context: int ret = OPUS_OK;
# C context: va_list ap;
opus_dred_decoder_ctl:
# @OPUS@\upstream\src\opus_decoder.c:1428: }
	movi.n	a2, -5	#,
	ret.n
	.size	opus_dred_decoder_ctl, .-opus_dred_decoder_ctl
	.section	.text.opus_dred_get_size,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_get_size
	.type	opus_dred_get_size, @function
# Function: opus_dred_get_size
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif
# C context:
# C context: int opus_dred_get_size(void)
# C context: {
# C context: #ifdef ENABLE_DRED
# C context: return sizeof(OpusDRED);
# C context: #else
opus_dred_get_size:
# @OPUS@\upstream\src\opus_decoder.c:1503: }
	movi.n	a2, 0	#,
	ret.n
	.size	opus_dred_get_size, .-opus_dred_get_size
	.section	.text.opus_dred_alloc,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_alloc
	.type	opus_dred_alloc, @function
# Function: opus_dred_alloc
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: OpusDRED *opus_dred_alloc(int *error)
# C context: {
# C context: #ifdef ENABLE_DRED
# C context: OpusDRED *dec;
# C context: dec = (OpusDRED *)opus_alloc(opus_dred_get_size());
opus_dred_alloc:
# @OPUS@\upstream\src\opus_decoder.c:1518:   if (error)
	beqz.n	a2, .L457	# error,
# @OPUS@\upstream\src\opus_decoder.c:1519:     *error = OPUS_UNIMPLEMENTED;
	movi.n	a3, -5	# tmp44,
	s32i.n	a3, a2, 0	# *error_2(D), tmp44
.L457:
# @OPUS@\upstream\src\opus_decoder.c:1522: }
	movi.n	a2, 0	#,
	ret.n
	.size	opus_dred_alloc, .-opus_dred_alloc
	.section	.text.opus_dred_free,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_free
	.type	opus_dred_free, @function
# Function: opus_dred_free
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: void opus_dred_free(OpusDRED *dec)
# C context: {
# C context: #ifdef ENABLE_DRED
# C context: opus_free(dec);
# C context: #else
opus_dred_free:
# @OPUS@\upstream\src\opus_decoder.c:1531: }
	ret.n
	.size	opus_dred_free, .-opus_dred_free
	.section	.text.opus_dred_parse,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_parse
	.type	opus_dred_parse, @function
# Function: opus_dred_parse
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: int opus_dred_parse(OpusDREDDecoder *dred_dec, OpusDRED *dred, const unsigned char *data, opus_int32 len, opus_int32 max_dred_samples, opus_int32 sampling_rate, int *dred_end, int defer_processing)
# C context: {
# C context: #ifdef ENABLE_DRED
# C context: const unsigned char *payload;
# C context: opus_int32 payload_len;
opus_dred_parse:
# @OPUS@\upstream\src\opus_decoder.c:1570: }
	movi.n	a2, -5	#,
	ret.n
	.size	opus_dred_parse, .-opus_dred_parse
	.section	.text.opus_dred_process,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_dred_process
	.type	opus_dred_process, @function
# Function: opus_dred_process
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: min_feature_frames = IMIN(2 + offset, 2*DRED_NUM_REDUNDANCY_FRAMES);
# C context: dred_ec_decode(dred, payload, payload_len, min_feature_frames, dred_frame_offset);
# C context: if (!defer_processing)
# C context: opus_dred_process(dred_dec, dred, dred);
# C context: if (dred_end) *dred_end = IMAX(0, -dred->dred_offset*sampling_rate/400);
# C context: return IMAX(0, dred->nb_latents*sampling_rate/25 - dred->dred_offset* sampling_rate/400);
# C context: }
# C context: if (dred_end) *dred_end = 0;
opus_dred_process:
# @OPUS@\upstream\src\opus_decoder.c:1592: }
	movi.n	a2, -5	#,
	ret.n
	.size	opus_dred_process, .-opus_dred_process
	.section	.text.opus_decoder_dred_decode,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_decoder_dred_decode
	.type	opus_decoder_dred_decode, @function
# Function: opus_decoder_dred_decode
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: int opus_decoder_dred_decode(OpusDecoder *st, const OpusDRED *dred, opus_int32 dred_offset, opus_int16 *pcm, opus_int32 frame_size)
# C context: {
# C context: #ifdef ENABLE_DRED
# C context: VARDECL(float, out);
# C context: int ret, i;
opus_decoder_dred_decode:
# @OPUS@\upstream\src\opus_decoder.c:1626: }
	movi.n	a2, -5	#,
	ret.n
	.size	opus_decoder_dred_decode, .-opus_decoder_dred_decode
	.section	.text.opus_decoder_dred_decode_float,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_decoder_dred_decode_float
	.type	opus_decoder_dred_decode_float, @function
# Function: opus_decoder_dred_decode_float
# Module: upstream/src/opus_decoder.c
# Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: int opus_decoder_dred_decode_float(OpusDecoder *st, const OpusDRED *dred, opus_int32 dred_offset, float *pcm, opus_int32 frame_size)
# C context: {
# C context: #ifdef ENABLE_DRED
# C context: if(frame_size<=0)
# C context: return OPUS_BAD_ARG;
opus_decoder_dred_decode_float:
	movi.n	a2, -5	#,
	ret.n
	.size	opus_decoder_dred_decode_float, .-opus_decoder_dred_decode_float
	.section	.rodata.CSWTCH$60,"a"
	.align	4
	.type	CSWTCH$60, @object
	.size	CSWTCH$60, 16
CSWTCH$60:
	.word	13
	.word	17
	.word	17
	.word	19
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
