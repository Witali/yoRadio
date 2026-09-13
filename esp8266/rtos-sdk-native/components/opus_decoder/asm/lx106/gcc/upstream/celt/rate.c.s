# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/rate.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"rate.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\rate.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\rate.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\rate.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\rate.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\rate.c.s.raw
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
	.global	__udivsi3
	.section	.text.clt_compute_allocation,"ax",@progbits
	.literal_position
	.literal .LC0, LOG2_FRAC_TABLE
	.align	4
	.global	clt_compute_allocation
	.type	clt_compute_allocation, @function
# Function: clt_compute_allocation
# Module: upstream/celt/rate.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return codedBands;
# C context: }
# C context:
# C context: int clt_compute_allocation(const CELTMode *m, int start, int end, const int *offsets, const int *cap, int alloc_trim, int *intensity, int *dual_stereo,
# C context: opus_int32 total, opus_int32 *balance, int *pulses, int *ebits, int *fine_priority, int C, int LM, ec_ctx *ec, int encode, int prev, int signalBandwidth)
# C context: {
# C context: int lo, hi, len, j;
# C context: int codedBands;
clt_compute_allocation:
	movi	a9, 0xc0	#,
	sub	sp, sp, a9	#,,
	s32i	a12, sp, 184	#,
	s32i	a13, sp, 180	#,
	s32i	a5, sp, 120	# %sfp, offsets
	l32i	a13, sp, 200	# total, total
	s32i	a0, sp, 188	#,
	s32i	a14, sp, 176	#,
	s32i	a15, sp, 172	#,
# @OPUS@\upstream\celt\rate.c:536: {
	s32i.n	a2, sp, 36	# %sfp, m
	s32i.n	a3, sp, 32	# %sfp, start
	s32i.n	a4, sp, 56	# %sfp, end
	s32i	a6, sp, 84	# %sfp, cap
	mov.n	a12, a7	# alloc_trim, alloc_trim
# @OPUS@\upstream\celt\rate.c:547:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\rate.c:550:    len = m->nbEBands;
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\rate.c:547:    SAVE_STACK;
	s32i.n	a2, sp, 8	# _saved_stack,
# @OPUS@\upstream\celt\rate.c:549:    total = IMAX(total, 0);
	movi.n	a2, 0	# tmp530,
	mov.n	a5, a2	#, tmp530
# @OPUS@\upstream\celt\rate.c:550:    len = m->nbEBands;
	l32i.n	a8, a8, 8	# m_153(D)->nbEBands,
# @OPUS@\upstream\celt\rate.c:549:    total = IMAX(total, 0);
	movgez	a5, a13, a13	#, total, total
# @OPUS@\upstream\celt\rate.c:547:    SAVE_STACK;
	s32i.n	a3, sp, 12	# _saved_stack,
# @OPUS@\upstream\celt\rate.c:549:    total = IMAX(total, 0);
	s32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:550:    len = m->nbEBands;
	s32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\celt\rate.c:553:    skip_rsv = total >= 1<<BITRES ? 1<<BITRES : 0;
	s32i	a2, sp, 124	# %sfp, tmp530
	blti	a13, 8, .L2	# total,,
	addi	a5, a5, -8	#,,
	movi.n	a14, 8	#,
	s32i.n	a5, sp, 44	# %sfp,
	s32i	a14, sp, 124	# %sfp,
.L2:
# @OPUS@\upstream\celt\rate.c:556:    intensity_rsv = dual_stereo_rsv = 0;
	movi.n	a5, 0	#,
# @OPUS@\upstream\celt\rate.c:557:    if (C==2)
	l32i	a7, sp, 220	# C,
# @OPUS@\upstream\celt\rate.c:556:    intensity_rsv = dual_stereo_rsv = 0;
	s32i	a5, sp, 112	# %sfp,
# @OPUS@\upstream\celt\rate.c:556:    intensity_rsv = dual_stereo_rsv = 0;
	s32i	a5, sp, 96	# %sfp,
# @OPUS@\upstream\celt\rate.c:557:    if (C==2)
	bnei	a7, 2, .L3	#,,
# @OPUS@\upstream\celt\rate.c:559:       intensity_rsv = LOG2_FRAC_TABLE[end-start];
	l32i.n	a8, sp, 56	# %sfp,
	l32i.n	a14, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:559:       intensity_rsv = LOG2_FRAC_TABLE[end-start];
	l32r	a2, .LC0	#, tmp531
# @OPUS@\upstream\celt\rate.c:559:       intensity_rsv = LOG2_FRAC_TABLE[end-start];
	sub	a3, a8, a14	# tmp532,,
# @OPUS@\upstream\celt\rate.c:559:       intensity_rsv = LOG2_FRAC_TABLE[end-start];
	add.n	a2, a2, a3	# tmp533, tmp531, tmp532
# @OPUS@\upstream\celt\rate.c:559:       intensity_rsv = LOG2_FRAC_TABLE[end-start];
	l8ui	a2, a2, 0	# LOG2_FRAC_TABLE,
# @OPUS@\upstream\celt\rate.c:560:       if (intensity_rsv>total)
	l32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:559:       intensity_rsv = LOG2_FRAC_TABLE[end-start];
	s32i	a2, sp, 96	# %sfp,
# @OPUS@\upstream\celt\rate.c:560:       if (intensity_rsv>total)
	blt	a5, a2, .L98	#,,
# @OPUS@\upstream\celt\rate.c:564:          total -= intensity_rsv;
	sub	a5, a5, a2	#,,
	s32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:565:          dual_stereo_rsv = total>=1<<BITRES ? 1<<BITRES : 0;
	blti	a5, 8, .L3	#,,
	addi	a5, a5, -8	#,,
	movi.n	a7, 8	#,
	s32i.n	a5, sp, 44	# %sfp,
	s32i	a7, sp, 112	# %sfp,
	j	.L3		#
.L98:
# @OPUS@\upstream\celt\rate.c:561:          intensity_rsv = 0;
	l32i	a8, sp, 112	# %sfp,
	s32i	a8, sp, 96	# %sfp,
.L3:
# @OPUS@\upstream\celt\rate.c:569:    ALLOC(bits1, len, int);
	l32i.n	a2, sp, 52	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\rate.c:570:    ALLOC(bits2, len, int);
	l32i.n	a2, sp, 52	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 104	# %sfp,
# @OPUS@\upstream\celt\rate.c:571:    ALLOC(thresh, len, int);
	l32i.n	a2, sp, 52	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\celt\rate.c:572:    ALLOC(trim_offset, len, int);
	l32i.n	a2, sp, 52	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	l32i	a14, sp, 220	# C,
	l32i.n	a5, sp, 56	# %sfp,
	slli	a14, a14, 3	#,,
	s32i.n	a14, sp, 24	# %sfp,
	addi.n	a5, a5, -1	#,,
# @OPUS@\upstream\celt\rate.c:574:    for (j=start;j<end;j++)
	l32i.n	a8, sp, 32	# %sfp,
	l32i.n	a14, sp, 56	# %sfp,
# @OPUS@\upstream\celt\rate.c:572:    ALLOC(trim_offset, len, int);
	s32i	a2, sp, 108	# %sfp,
	s32i.n	a5, sp, 60	# %sfp,
# @OPUS@\upstream\celt\rate.c:574:    for (j=start;j<end;j++)
	blt	a8, a14, .L5	#,,
	slli	a5, a8, 1	#,,
	s32i	a5, sp, 64	# %sfp,
.L11:
# @OPUS@\upstream\celt\rate.c:587:    hi = m->nbAllocVectors - 1;
	l32i.n	a8, sp, 36	# %sfp,
	l32i.n	a4, sp, 60	# %sfp,
	l32i.n	a8, a8, 40	# m_153(D)->nbAllocVectors,
# @OPUS@\upstream\celt\rate.c:586:    lo = 1;
	movi.n	a2, 1	#,
# @OPUS@\upstream\celt\rate.c:587:    hi = m->nbAllocVectors - 1;
	addi.n	a3, a8, -1	#,,
	l32i.n	a14, sp, 60	# %sfp,
# @OPUS@\upstream\celt\rate.c:586:    lo = 1;
	s32i.n	a2, sp, 28	# %sfp,
	ssl	a2	#
	sll	a4, a4	#,
# @OPUS@\upstream\celt\rate.c:587:    hi = m->nbAllocVectors - 1;
	s32i	a8, sp, 116	# %sfp,
# @OPUS@\upstream\celt\rate.c:587:    hi = m->nbAllocVectors - 1;
	s32i.n	a3, sp, 48	# %sfp,
	l32i	a5, sp, 84	# %sfp,
	l32i	a7, sp, 120	# %sfp,
	l32i	a8, sp, 100	# %sfp,
	l32i	a2, sp, 108	# %sfp,
	l32i	a3, sp, 64	# %sfp,
	slli	a14, a14, 2	#,,
	add.n	a5, a5, a14	#,,
	add.n	a7, a7, a14	#,,
	add.n	a8, a8, a14	#,,
	s32i	a14, sp, 72	# %sfp,
	addi	a3, a3, -2	#,,
	add.n	a14, a2, a14	#,,
	s32i	a4, sp, 92	# %sfp,
	s32i	a5, sp, 88	# %sfp,
	s32i	a7, sp, 76	# %sfp,
	s32i.n	a8, sp, 20	# %sfp,
	s32i	a14, sp, 68	# %sfp,
	s32i	a3, sp, 80	# %sfp,
# @OPUS@\upstream\celt\rate.c:603:             done = 1;
	l32i.n	a15, sp, 28	# %sfp, done
	j	.L6		#
.L5:
# @OPUS@\upstream\celt\rate.c:577:       thresh[j] = IMAX((C)<<BITRES, (3*(m->eBands[j+1]-m->eBands[j])<<LM<<BITRES)>>4);
	l32i.n	a8, sp, 36	# %sfp,
	mov.n	a14, a5	#,
# @OPUS@\upstream\celt\rate.c:579:       trim_offset[j] = C*(m->eBands[j+1]-m->eBands[j])*(alloc_trim-5-LM)*(end-j-1)
	l32i	a5, sp, 224	# LM,
	mov.n	a3, a2	#,
	addi	a9, a12, -5	# tmp534, alloc_trim,
# @OPUS@\upstream\celt\rate.c:577:       thresh[j] = IMAX((C)<<BITRES, (3*(m->eBands[j+1]-m->eBands[j])<<LM<<BITRES)>>4);
	l32i.n	a2, a8, 24	# m_153(D)->eBands, _7
	l32i	a7, sp, 220	# C,
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:579:       trim_offset[j] = C*(m->eBands[j+1]-m->eBands[j])*(alloc_trim-5-LM)*(end-j-1)
	sub	a9, a9, a5	# tmp535, tmp534,
	slli	a6, a8, 2	# _889,,
	mull	a9, a9, a7	# _721, tmp535,
	sub	a7, a14, a8	# tmp537,,
	slli	a14, a8, 1	#,,
	l32i.n	a8, sp, 56	# %sfp,
	s32i	a14, sp, 64	# %sfp,
	addi.n	a11, a5, 3	# _1013,,
	add.n	a5, a2, a14	# ivtmp$268, _7,
	l32i	a14, sp, 100	# %sfp,
	slli	a10, a8, 1	# tmp538,,
	mull	a7, a7, a9	# ivtmp$270, tmp537, _721
	l32i.n	a12, sp, 24	# %sfp, _1012
	l32i	a4, sp, 224	# LM, LM
	add.n	a8, a14, a6	# ivtmp$269,, _889
	add.n	a10, a2, a10	# _868, _7, tmp538
	add.n	a6, a3, a6	# ivtmp$271,, _889
.L10:
# @OPUS@\upstream\celt\rate.c:577:       thresh[j] = IMAX((C)<<BITRES, (3*(m->eBands[j+1]-m->eBands[j])<<LM<<BITRES)>>4);
	l16si	a2, a5, 0	# MEM[base: _865, offset: 0B], tmp542
	l16si	a3, a5, 2	# MEM[base: _865, offset: 2B], tmp539
	sub	a3, a3, a2	# _1134, tmp539, tmp542
	slli	a2, a3, 1	# tmp546, _1134,
	add.n	a2, a2, a3	# tmp547, tmp546, _1134
	ssl	a4	# LM
	sll	a2, a2	# tmp548, tmp547
# @OPUS@\upstream\celt\rate.c:579:       trim_offset[j] = C*(m->eBands[j+1]-m->eBands[j])*(alloc_trim-5-LM)*(end-j-1)
	mull	a13, a7, a3	# tmp552, ivtmp$270, _1134
# @OPUS@\upstream\celt\rate.c:577:       thresh[j] = IMAX((C)<<BITRES, (3*(m->eBands[j+1]-m->eBands[j])<<LM<<BITRES)>>4);
	slli	a2, a2, 3	# tmp549, tmp548,
	srai	a2, a2, 4	# _1012, tmp549,
# @OPUS@\upstream\celt\rate.c:580:             *(1<<(LM+BITRES))>>6;
	ssl	a11	# _1013
	sll	a13, a13	# tmp553, tmp552
# @OPUS@\upstream\celt\rate.c:583:       if ((m->eBands[j+1]-m->eBands[j])<<LM==1)
	ssl	a4	# LM
	sll	a3, a3	# tmp554, _1134
# @OPUS@\upstream\celt\rate.c:577:       thresh[j] = IMAX((C)<<BITRES, (3*(m->eBands[j+1]-m->eBands[j])<<LM<<BITRES)>>4);
	bge	a2, a12, .L7	# _1012, _1012,
	mov.n	a2, a12	# _1012, _1012
.L7:
# @OPUS@\upstream\celt\rate.c:577:       thresh[j] = IMAX((C)<<BITRES, (3*(m->eBands[j+1]-m->eBands[j])<<LM<<BITRES)>>4);
	s32i.n	a2, a8, 0	# MEM[base: _872, offset: 0B], _1012
# @OPUS@\upstream\celt\rate.c:580:             *(1<<(LM+BITRES))>>6;
	srai	a2, a13, 6	# _1115, tmp553,
# @OPUS@\upstream\celt\rate.c:583:       if ((m->eBands[j+1]-m->eBands[j])<<LM==1)
	bnei	a3, 1, .L8	# tmp554,,
# @OPUS@\upstream\celt\rate.c:584:          trim_offset[j] -= C<<BITRES;
	sub	a2, a2, a12	# tmp555, _1115, _1012
	s32i.n	a2, a6, 0	#* ivtmp$271, tmp555
	j	.L9		#
.L8:
# @OPUS@\upstream\celt\rate.c:579:       trim_offset[j] = C*(m->eBands[j+1]-m->eBands[j])*(alloc_trim-5-LM)*(end-j-1)
	s32i.n	a2, a6, 0	#* ivtmp$271, _1115
.L9:
	addi.n	a5, a5, 2	# ivtmp$268, ivtmp$268,
	addi.n	a8, a8, 4	# ivtmp$269, ivtmp$269,
	sub	a7, a7, a9	# ivtmp$270, ivtmp$270, _721
	addi.n	a6, a6, 4	# ivtmp$271, ivtmp$271,
# @OPUS@\upstream\celt\rate.c:574:    for (j=start;j<end;j++)
	bne	a10, a5, .L10	# _868, ivtmp$268,
	j	.L11		#
.L6:
# @OPUS@\upstream\celt\rate.c:592:       int mid = (lo+hi) >> 1;
	l32i.n	a4, sp, 28	# %sfp,
	l32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	l32i.n	a7, sp, 52	# %sfp,
# @OPUS@\upstream\celt\rate.c:592:       int mid = (lo+hi) >> 1;
	add.n	a2, a4, a5	# tmp556,,
# @OPUS@\upstream\celt\rate.c:592:       int mid = (lo+hi) >> 1;
	srai	a2, a2, 1	#, tmp556,
# @OPUS@\upstream\celt\rate.c:593:       for (j=end;j-->start;)
	l32i.n	a8, sp, 32	# %sfp,
	l32i.n	a14, sp, 56	# %sfp,
# @OPUS@\upstream\celt\rate.c:592:       int mid = (lo+hi) >> 1;
	s32i.n	a2, sp, 40	# %sfp,
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	mull	a2, a7, a2	# _54,,
# @OPUS@\upstream\celt\rate.c:593:       for (j=end;j-->start;)
	bge	a8, a14, .L100	#,,
	l32i.n	a8, sp, 36	# %sfp,
	l32i	a7, sp, 80	# %sfp,
	l32i.n	a13, a8, 24	# MEM[(const opus_int16 * *)m_153(D) + 24B], m__eBands_lsm0$116
	l32i.n	a14, sp, 60	# %sfp,
	l32i	a4, sp, 92	# %sfp,
	l32i.n	a5, a8, 44	# MEM[(const unsigned char * *)m_153(D) + 44B], MEM[(const unsigned char * *)m_153(D) + 44B]
	add.n	a2, a2, a14	# tmp557, _54,
# @OPUS@\upstream\celt\rate.c:591:       int psum = 0;
	movi.n	a10, 0	# psum,
	add.n	a3, a13, a4	# ivtmp$248, m__eBands_lsm0$116,
# @OPUS@\upstream\celt\rate.c:593:       for (j=end;j-->start;)
	l32i	a9, sp, 68	# %sfp, ivtmp$259
	add.n	a13, a13, a7	# _904, m__eBands_lsm0$116,
	l32i	a6, sp, 76	# %sfp, ivtmp$255
	l32i.n	a7, sp, 20	# %sfp, ivtmp$257
	l32i	a8, sp, 88	# %sfp, ivtmp$253
	add.n	a5, a5, a2	# ivtmp$250, MEM[(const unsigned char * *)m_153(D) + 44B], tmp557
# @OPUS@\upstream\celt\rate.c:590:       int done = 0;
	mov.n	a12, a10	# done, psum
.L19:
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	l32i	a14, sp, 220	# C,
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	l8ui	a4, a5, 0	# MEM[base: _909, offset: 0B], MEM[base: _909, offset: 0B]
# @OPUS@\upstream\celt\rate.c:596:          int N = m->eBands[j+1]-m->eBands[j];
	l16si	a2, a3, 2	# MEM[base: _911, offset: 2B], tmp560
# @OPUS@\upstream\celt\rate.c:596:          int N = m->eBands[j+1]-m->eBands[j];
	l16si	a11, a3, 0	# MEM[base: _911, offset: 0B], tmp563
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	mull	a4, a4, a14	# tmp568, MEM[base: _909, offset: 0B],
# @OPUS@\upstream\celt\rate.c:596:          int N = m->eBands[j+1]-m->eBands[j];
	sub	a2, a2, a11	# N, tmp560, tmp563
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	mull	a4, a2, a4	# tmp569, N, tmp568
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	l32i	a14, sp, 224	# LM,
	ssl	a14	#
	sll	a4, a4	# tmp570, tmp569
# @OPUS@\upstream\celt\rate.c:597:          bitsj = C*N*m->allocVectors[mid*len+j]<<LM>>2;
	srai	a4, a4, 2	# bitsj, tmp570,
# @OPUS@\upstream\celt\rate.c:598:          if (bitsj > 0)
	blti	a4, 1, .L13	# bitsj,,
# @OPUS@\upstream\celt\rate.c:599:             bitsj = IMAX(0, bitsj + trim_offset[j]);
	l32i.n	a2, a9, 0	# MEM[base: _900, offset: 0B], MEM[base: _900, offset: 0B]
	add.n	a4, a4, a2	# _65, bitsj, MEM[base: _900, offset: 0B]
# @OPUS@\upstream\celt\rate.c:599:             bitsj = IMAX(0, bitsj + trim_offset[j]);
	movi.n	a2, 0	#,
	movltz	a4, a2, a4	# bitsj,, _65
.L13:
# @OPUS@\upstream\celt\rate.c:600:          bitsj += offsets[j];
	l32i.n	a2, a6, 0	# MEM[base: _902, offset: 0B], MEM[base: _902, offset: 0B]
# @OPUS@\upstream\celt\rate.c:601:          if (bitsj >= thresh[j] || done)
	l32i.n	a11, a7, 0	# MEM[base: _901, offset: 0B], MEM[base: _901, offset: 0B]
# @OPUS@\upstream\celt\rate.c:600:          bitsj += offsets[j];
	add.n	a4, a4, a2	# bitsj, bitsj, MEM[base: _902, offset: 0B]
# @OPUS@\upstream\celt\rate.c:601:          if (bitsj >= thresh[j] || done)
	bge	a4, a11, .L114	# bitsj, MEM[base: _901, offset: 0B],
# @OPUS@\upstream\celt\rate.c:601:          if (bitsj >= thresh[j] || done)
	beqz.n	a12, .L14	# done,
.L114:
# @OPUS@\upstream\celt\rate.c:605:             psum += IMIN(bitsj, cap[j]);
	l32i.n	a2, a8, 0	# MEM[base: _903, offset: 0B], MEM[base: _903, offset: 0B]
# @OPUS@\upstream\celt\rate.c:603:             done = 1;
	mov.n	a12, a15	# done, done
# @OPUS@\upstream\celt\rate.c:605:             psum += IMIN(bitsj, cap[j]);
	bge	a4, a2, .L17	# bitsj, MEM[base: _903, offset: 0B],
	mov.n	a2, a4	# MEM[base: _903, offset: 0B], bitsj
.L17:
# @OPUS@\upstream\celt\rate.c:605:             psum += IMIN(bitsj, cap[j]);
	add.n	a10, a10, a2	# psum, psum, MEM[base: _903, offset: 0B]
	j	.L18		#
.L14:
# @OPUS@\upstream\celt\rate.c:607:             if (bitsj >= C<<BITRES)
	l32i.n	a14, sp, 24	# %sfp,
	movi.n	a12, 0	# done,
	blt	a4, a14, .L18	# bitsj,,
# @OPUS@\upstream\celt\rate.c:608:                psum += C<<BITRES;
	add.n	a10, a10, a14	# psum, psum,
.L18:
	addi	a3, a3, -2	# ivtmp$248, ivtmp$248,
	addi.n	a5, a5, -1	# ivtmp$250, ivtmp$250,
	addi	a8, a8, -4	# ivtmp$253, ivtmp$253,
	addi	a6, a6, -4	# ivtmp$255, ivtmp$255,
	addi	a7, a7, -4	# ivtmp$257, ivtmp$257,
	addi	a9, a9, -4	# ivtmp$259, ivtmp$259,
# @OPUS@\upstream\celt\rate.c:593:       for (j=end;j-->start;)
	bne	a13, a3, .L19	# _904, ivtmp$248,
	j	.L12		#
.L100:
# @OPUS@\upstream\celt\rate.c:591:       int psum = 0;
	movi.n	a10, 0	# psum,
.L12:
# @OPUS@\upstream\celt\rate.c:611:       if (psum > total)
	l32i.n	a5, sp, 44	# %sfp,
	bge	a5, a10, .L20	#, psum,
# @OPUS@\upstream\celt\rate.c:612:          hi = mid - 1;
	l32i.n	a7, sp, 40	# %sfp,
# @OPUS@\upstream\celt\rate.c:617:    while (lo <= hi);
	l32i.n	a8, sp, 28	# %sfp,
# @OPUS@\upstream\celt\rate.c:612:          hi = mid - 1;
	addi.n	a7, a7, -1	#,,
	s32i.n	a7, sp, 48	# %sfp,
# @OPUS@\upstream\celt\rate.c:617:    while (lo <= hi);
	bge	a7, a8, .L6	#,,
	j	.L22		#
.L20:
# @OPUS@\upstream\celt\rate.c:614:          lo = mid + 1;
	l32i.n	a14, sp, 40	# %sfp,
# @OPUS@\upstream\celt\rate.c:617:    while (lo <= hi);
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\rate.c:614:          lo = mid + 1;
	addi.n	a14, a14, 1	#,,
	s32i.n	a14, sp, 28	# %sfp,
# @OPUS@\upstream\celt\rate.c:617:    while (lo <= hi);
	bge	a2, a14, .L6	#,,
.L22:
# @OPUS@\upstream\celt\rate.c:618:    hi = lo--;
	l32i.n	a3, sp, 28	# %sfp,
# @OPUS@\upstream\celt\rate.c:620:    for (j=start;j<end;j++)
	l32i.n	a8, sp, 32	# %sfp,
	l32i.n	a14, sp, 56	# %sfp,
# @OPUS@\upstream\celt\rate.c:618:    hi = lo--;
	addi.n	a13, a3, -1	# lo,,
# @OPUS@\upstream\celt\rate.c:620:    for (j=start;j<end;j++)
	bge	a8, a14, .L102	#,,
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	l32i.n	a5, sp, 52	# %sfp,
	mov.n	a4, a8	#,
	l32i.n	a8, sp, 36	# %sfp,
	mull	a14, a5, a13	# _89,, lo
	l32i.n	a5, a8, 24	# m_153(D)->eBands, m_153(D)->eBands
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	l32i.n	a7, sp, 52	# %sfp,
	slli	a6, a8, 2	# _991,,
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	add.n	a15, a14, a7	# _100, _89,
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	l32i.n	a12, a8, 44	# m_153(D)->allocVectors, _88
	l32i	a8, sp, 64	# %sfp,
	l32i.n	a7, sp, 16	# %sfp,
	add.n	a5, a5, a8	# ivtmp$217, m_153(D)->eBands,
	l32i	a2, sp, 120	# %sfp,
	l32i	a8, sp, 104	# %sfp,
	l32i	a3, sp, 108	# %sfp,
# @OPUS@\upstream\celt\rate.c:628:          bits1j = IMAX(0, bits1j + trim_offset[j]);
	s32i.n	a15, sp, 52	# %sfp, _100
	s32i.n	a13, sp, 48	# %sfp, lo
	l32i	a15, sp, 116	# %sfp, pretmp_1061
	l32i	a13, sp, 224	# LM, LM
	add.n	a9, a8, a6	# ivtmp$223,, _991
	add.n	a10, a7, a6	# ivtmp$221,, _991
	add.n	a8, a2, a6	# ivtmp$225,, _991
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	s32i.n	a4, sp, 40	# %sfp,
	add.n	a6, a3, a6	# ivtmp$227,, _991
# @OPUS@\upstream\celt\rate.c:628:          bits1j = IMAX(0, bits1j + trim_offset[j]);
	movi.n	a11, 0	# tmp1202,
	s32i	a14, sp, 68	# %sfp, _89
.L30:
# @OPUS@\upstream\celt\rate.c:623:       int N = m->eBands[j+1]-m->eBands[j];
	l16si	a7, a5, 2	# MEM[base: _954, offset: 2B], tmp589
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	l32i	a14, sp, 68	# %sfp,
# @OPUS@\upstream\celt\rate.c:623:       int N = m->eBands[j+1]-m->eBands[j];
	l16si	a2, a5, 0	# MEM[base: _954, offset: 0B], tmp592
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	add.n	a3, a14, a4	# tmp596,, j
# @OPUS@\upstream\celt\rate.c:623:       int N = m->eBands[j+1]-m->eBands[j];
	sub	a2, a7, a2	# N, tmp589, tmp592
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	l32i	a7, sp, 220	# C,
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	add.n	a3, a12, a3	# tmp597, _88, tmp596
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	mull	a2, a2, a7	# _87, N,
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	l8ui	a3, a3, 0	# MEM[base: _967, offset: 0B], MEM[base: _967, offset: 0B]
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	l32i.n	a14, sp, 28	# %sfp,
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	mull	a3, a3, a2	# tmp599, MEM[base: _967, offset: 0B], _87
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	ssl	a13	# LM
	sll	a3, a3	# tmp600, tmp599
# @OPUS@\upstream\celt\rate.c:624:       bits1j = C*N*m->allocVectors[lo*len+j]<<LM>>2;
	srai	a3, a3, 2	# bits1j, tmp600,
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	blt	a14, a15, .L24	#, pretmp_1061,
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	l32i	a14, sp, 84	# %sfp,
	slli	a2, a4, 2	# tmp601, j,
	add.n	a2, a14, a2	# tmp602,, tmp601
	l32i.n	a2, a2, 0	# MEM[base: _959, offset: 0B], bits2j
	j	.L25		#
.L24:
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	l32i.n	a7, sp, 52	# %sfp,
	add.n	a14, a7, a4	# tmp603,, j
	add.n	a7, a12, a14	# tmp604, _88, tmp603
	l8ui	a7, a7, 0	# MEM[base: _955, offset: 0B], MEM[base: _955, offset: 0B]
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	mull	a2, a7, a2	# tmp606, MEM[base: _955, offset: 0B], _87
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	ssl	a13	# LM
	sll	a2, a2	# tmp607, tmp606
# @OPUS@\upstream\celt\rate.c:626:             cap[j] : C*N*m->allocVectors[hi*len+j]<<LM>>2;
	srai	a2, a2, 2	# bits2j, tmp607,
.L25:
# @OPUS@\upstream\celt\rate.c:627:       if (bits1j > 0)
	blti	a3, 1, .L26	# bits1j,,
# @OPUS@\upstream\celt\rate.c:628:          bits1j = IMAX(0, bits1j + trim_offset[j]);
	l32i.n	a7, a6, 0	# MEM[base: _962, offset: 0B], MEM[base: _962, offset: 0B]
	add.n	a3, a3, a7	# _111, bits1j, MEM[base: _962, offset: 0B]
# @OPUS@\upstream\celt\rate.c:628:          bits1j = IMAX(0, bits1j + trim_offset[j]);
	movltz	a3, a11, a3	# bits1j, tmp1202, _111
.L26:
# @OPUS@\upstream\celt\rate.c:629:       if (bits2j > 0)
	blti	a2, 1, .L27	# bits2j,,
# @OPUS@\upstream\celt\rate.c:630:          bits2j = IMAX(0, bits2j + trim_offset[j]);
	l32i.n	a7, a6, 0	# MEM[base: _963, offset: 0B], MEM[base: _963, offset: 0B]
	add.n	a2, a2, a7	# bits2j, bits2j, MEM[base: _963, offset: 0B]
# @OPUS@\upstream\celt\rate.c:630:          bits2j = IMAX(0, bits2j + trim_offset[j]);
	movltz	a2, a11, a2	# bits2j, tmp1202, bits2j
.L27:
# @OPUS@\upstream\celt\rate.c:631:       if (lo > 0)
	l32i.n	a14, sp, 48	# %sfp,
	l32i.n	a7, a8, 0	# MEM[base: _964, offset: 0B], pretmp_1076
	blti	a14, 1, .L28	#,,
# @OPUS@\upstream\celt\rate.c:632:          bits1j += offsets[j];
	add.n	a3, a3, a7	# bits1j, bits1j, pretmp_1076
.L28:
# @OPUS@\upstream\celt\rate.c:633:       bits2j += offsets[j];
	add.n	a2, a2, a7	# bits2j, bits2j, pretmp_1076
# @OPUS@\upstream\celt\rate.c:634:       if (offsets[j]>0)
	blti	a7, 1, .L29	# pretmp_1076,,
	s32i.n	a4, sp, 40	# %sfp, j
.L29:
# @OPUS@\upstream\celt\rate.c:636:       bits2j = IMAX(0,bits2j-bits1j);
	sub	a2, a2, a3	# _122, bits2j, bits1j
# @OPUS@\upstream\celt\rate.c:637:       bits1[j] = bits1j;
	s32i.n	a3, a10, 0	# MEM[base: _966, offset: 0B], bits1j
# @OPUS@\upstream\celt\rate.c:636:       bits2j = IMAX(0,bits2j-bits1j);
	movltz	a2, a11, a2	# bits2j, tmp1202, _122
# @OPUS@\upstream\celt\rate.c:620:    for (j=start;j<end;j++)
	l32i.n	a14, sp, 56	# %sfp,
# @OPUS@\upstream\celt\rate.c:638:       bits2[j] = bits2j;
	s32i.n	a2, a9, 0	# MEM[base: _965, offset: 0B], bits2j
# @OPUS@\upstream\celt\rate.c:620:    for (j=start;j<end;j++)
	addi.n	a4, a4, 1	# j, j,
	addi.n	a5, a5, 2	# ivtmp$217, ivtmp$217,
	addi.n	a10, a10, 4	# ivtmp$221, ivtmp$221,
	addi.n	a9, a9, 4	# ivtmp$223, ivtmp$223,
	addi.n	a8, a8, 4	# ivtmp$225, ivtmp$225,
	addi.n	a6, a6, 4	# ivtmp$227, ivtmp$227,
# @OPUS@\upstream\celt\rate.c:620:    for (j=start;j<end;j++)
	beq	a14, a4, .L23	#, j,
	l32i.n	a14, sp, 36	# %sfp,
	l32i.n	a15, a14, 40	# m_153(D)->nbAllocVectors, pretmp_1061
	j	.L30		#
.L102:
# @OPUS@\upstream\celt\rate.c:620:    for (j=start;j<end;j++)
	s32i.n	a8, sp, 40	# %sfp,
.L23:
# @OPUS@\upstream\celt\rate.c:263:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\rate.c:266:    stereo = C>1;
	movi.n	a14, 1	#,
	l32i	a5, sp, 220	# C,
# @OPUS@\upstream\celt\rate.c:263:    SAVE_STACK;
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\rate.c:266:    stereo = C>1;
	s32i	a14, sp, 76	# %sfp,
	bgei	a5, 2, .L31	#,,
	movi.n	a7, 0	#,
	s32i	a7, sp, 76	# %sfp,
.L31:
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:268:    logM = LM<<BITRES;
	l32i	a14, sp, 224	# LM,
# @OPUS@\upstream\celt\rate.c:269:    lo = 0;
	movi.n	a13, 0	# lo,
# @OPUS@\upstream\celt\rate.c:268:    logM = LM<<BITRES;
	slli	a14, a14, 3	#,,
	slli	a2, a8, 2	# tmp617,,
	addi	a2, a2, -4	#, tmp617,
	s32i	a14, sp, 68	# %sfp,
	movi.n	a4, 6	# ivtmp_1278,
# @OPUS@\upstream\celt\rate.c:270:    hi = 1<<ALLOC_STEPS;
	movi.n	a14, 0x40	# hi,
# @OPUS@\upstream\celt\rate.c:285:             if (tmp >= alloc_floor)
	mov.n	a12, a13	# done, lo
	s32i.n	a13, sp, 48	# %sfp, lo
	l32i	a10, sp, 104	# %sfp, bits2
	l32i	a13, sp, 100	# %sfp, thresh
	l32i	a15, sp, 84	# %sfp, cap
	s32i.n	a14, sp, 52	# %sfp, hi
	s32i	a2, sp, 80	# %sfp,
# @OPUS@\upstream\celt\rate.c:281:             done = 1;
	movi.n	a11, 1	# done,
# @OPUS@\upstream\celt\rate.c:285:             if (tmp >= alloc_floor)
	mov.n	a14, a2	# _1003,
	s32i.n	a4, sp, 28	# %sfp, ivtmp_1278
.L40:
# @OPUS@\upstream\celt\rate.c:273:       int mid = (lo+hi)>>1;
	l32i.n	a2, sp, 48	# %sfp,
	l32i.n	a3, sp, 52	# %sfp,
# @OPUS@\upstream\celt\rate.c:276:       for (j=end;j-->start;)
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:273:       int mid = (lo+hi)>>1;
	add.n	a9, a2, a3	# tmp619,,
# @OPUS@\upstream\celt\rate.c:276:       for (j=end;j-->start;)
	l32i.n	a2, sp, 56	# %sfp,
# @OPUS@\upstream\celt\rate.c:273:       int mid = (lo+hi)>>1;
	srai	a9, a9, 1	# mid, tmp619,
# @OPUS@\upstream\celt\rate.c:274:       psum = 0;
	movi.n	a5, 0	# psum,
# @OPUS@\upstream\celt\rate.c:276:       for (j=end;j-->start;)
	bge	a8, a2, .L32	#,,
	l32i	a3, sp, 72	# %sfp, ivtmp$205
# @OPUS@\upstream\celt\rate.c:275:       done = 0;
	mov.n	a8, a5	# done, psum
.L38:
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	add.n	a2, a10, a3	# tmp620, bits2, ivtmp$205
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	l32i.n	a2, a2, 0	# MEM[base: _1007, offset: 0B], MEM[base: _1007, offset: 0B]
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	add.n	a6, a7, a3	# tmp624,, ivtmp$205
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	mull	a2, a9, a2	# tmp621, mid, MEM[base: _1007, offset: 0B]
# @OPUS@\upstream\celt\rate.c:279:          if (tmp >= thresh[j] || done)
	add.n	a4, a13, a3	# tmp626, thresh, ivtmp$205
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	l32i.n	a6, a6, 0	# MEM[base: _1008, offset: 0B], MEM[base: _1008, offset: 0B]
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	srai	a2, a2, 6	# tmp623, tmp621,
# @OPUS@\upstream\celt\rate.c:279:          if (tmp >= thresh[j] || done)
	l32i.n	a4, a4, 0	# MEM[base: _1006, offset: 0B], MEM[base: _1006, offset: 0B]
# @OPUS@\upstream\celt\rate.c:278:          int tmp = bits1[j] + (mid*(opus_int32)bits2[j]>>ALLOC_STEPS);
	add.n	a2, a2, a6	# tmp, tmp623, MEM[base: _1008, offset: 0B]
# @OPUS@\upstream\celt\rate.c:283:             psum += IMIN(tmp, cap[j]);
	add.n	a7, a15, a3	# tmp637, cap, ivtmp$205
# @OPUS@\upstream\celt\rate.c:279:          if (tmp >= thresh[j] || done)
	bge	a2, a4, .L115	# tmp, MEM[base: _1006, offset: 0B],
# @OPUS@\upstream\celt\rate.c:279:          if (tmp >= thresh[j] || done)
	beqz.n	a8, .L33	# done,
.L115:
# @OPUS@\upstream\celt\rate.c:283:             psum += IMIN(tmp, cap[j]);
	l32i.n	a4, a7, 0	# MEM[base: _1002, offset: 0B], MEM[base: _1002, offset: 0B]
# @OPUS@\upstream\celt\rate.c:281:             done = 1;
	mov.n	a8, a11	# done, done
# @OPUS@\upstream\celt\rate.c:283:             psum += IMIN(tmp, cap[j]);
	bge	a2, a4, .L36	# tmp, MEM[base: _1002, offset: 0B],
	mov.n	a4, a2	# MEM[base: _1002, offset: 0B], tmp
.L36:
# @OPUS@\upstream\celt\rate.c:283:             psum += IMIN(tmp, cap[j]);
	add.n	a5, a5, a4	# psum, psum, MEM[base: _1002, offset: 0B]
	j	.L37		#
.L33:
# @OPUS@\upstream\celt\rate.c:285:             if (tmp >= alloc_floor)
	l32i.n	a7, sp, 24	# %sfp,
	mov.n	a8, a12	# done, done
	blt	a2, a7, .L37	# tmp,,
# @OPUS@\upstream\celt\rate.c:286:                psum += alloc_floor;
	add.n	a5, a5, a7	# psum, psum,
.L37:
	addi	a3, a3, -4	# ivtmp$205, ivtmp$205,
# @OPUS@\upstream\celt\rate.c:276:       for (j=end;j-->start;)
	bne	a14, a3, .L38	# _1003, ivtmp$205,
.L32:
# @OPUS@\upstream\celt\rate.c:289:       if (psum > total)
	l32i.n	a8, sp, 44	# %sfp,
	bge	a8, a5, .L105	#, psum,
# @OPUS@\upstream\celt\rate.c:290:          hi = mid;
	s32i.n	a9, sp, 52	# %sfp, mid
	j	.L39		#
.L105:
# @OPUS@\upstream\celt\rate.c:292:          lo = mid;
	s32i.n	a9, sp, 48	# %sfp, mid
.L39:
	l32i.n	a2, sp, 28	# %sfp,
	addi.n	a2, a2, -1	#,,
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\rate.c:271:    for (i=0;i<ALLOC_STEPS;i++)
	bnez.n	a2, .L40	#,
# @OPUS@\upstream\celt\rate.c:297:    for (j=end;j-->start;)
	l32i.n	a8, sp, 32	# %sfp,
	l32i.n	a14, sp, 56	# %sfp,
	l32i.n	a13, sp, 48	# %sfp, lo
	bge	a8, a14, .L106	#,,
	l32i	a7, sp, 72	# %sfp,
	l32i.n	a5, sp, 16	# %sfp,
	l32i	a8, sp, 104	# %sfp,
	add.n	a6, a5, a7	# ivtmp$177,,
	l32i	a5, sp, 208	# pulses,
	add.n	a9, a8, a7	# ivtmp$179,,
	add.n	a8, a5, a7	# ivtmp$185,,
	l32i.n	a7, sp, 16	# %sfp,
	l32i	a5, sp, 80	# %sfp,
# @OPUS@\upstream\celt\rate.c:302:          if (tmp >= alloc_floor)
	l32i	a4, sp, 88	# %sfp, ivtmp$183
	add.n	a3, a7, a5	# _1023,,
# @OPUS@\upstream\celt\rate.c:297:    for (j=end;j-->start;)
	l32i.n	a7, sp, 20	# %sfp, ivtmp$181
# @OPUS@\upstream\celt\rate.c:294:    psum = 0;
	mov.n	a14, a2	# psum, ivtmp_1278
# @OPUS@\upstream\celt\rate.c:296:    done = 0;
	mov.n	a10, a2	# done, psum
# @OPUS@\upstream\celt\rate.c:307:          done = 1;
	movi.n	a11, 1	# done,
# @OPUS@\upstream\celt\rate.c:305:             tmp = 0;
	mov.n	a12, a2	# tmp, psum
.L45:
# @OPUS@\upstream\celt\rate.c:299:       int tmp = bits1[j] + ((opus_int32)lo*bits2[j]>>ALLOC_STEPS);
	l32i.n	a2, a9, 0	# MEM[base: _1031, offset: 0B], MEM[base: _1031, offset: 0B]
# @OPUS@\upstream\celt\rate.c:299:       int tmp = bits1[j] + ((opus_int32)lo*bits2[j]>>ALLOC_STEPS);
	l32i.n	a15, a6, 0	# MEM[base: _1032, offset: 0B], MEM[base: _1032, offset: 0B]
# @OPUS@\upstream\celt\rate.c:299:       int tmp = bits1[j] + ((opus_int32)lo*bits2[j]>>ALLOC_STEPS);
	mull	a2, a13, a2	# tmp642, lo, MEM[base: _1031, offset: 0B]
# @OPUS@\upstream\celt\rate.c:300:       if (tmp < thresh[j] && !done)
	l32i.n	a5, a7, 0	# MEM[base: _1030, offset: 0B],
# @OPUS@\upstream\celt\rate.c:299:       int tmp = bits1[j] + ((opus_int32)lo*bits2[j]>>ALLOC_STEPS);
	srai	a2, a2, 6	# tmp644, tmp642,
# @OPUS@\upstream\celt\rate.c:299:       int tmp = bits1[j] + ((opus_int32)lo*bits2[j]>>ALLOC_STEPS);
	add.n	a2, a2, a15	# tmp, tmp644, MEM[base: _1032, offset: 0B]
# @OPUS@\upstream\celt\rate.c:300:       if (tmp < thresh[j] && !done)
	bge	a2, a5, .L107	# tmp,,
# @OPUS@\upstream\celt\rate.c:300:       if (tmp < thresh[j] && !done)
	bbsi	a10, 0, .L107	# done,,
# @OPUS@\upstream\celt\rate.c:302:          if (tmp >= alloc_floor)
	l32i.n	a5, sp, 24	# %sfp,
	blt	a2, a5, .L108	# tmp,,
	mov.n	a2, a5	# tmp,
	mov.n	a10, a12	# done, tmp
	j	.L42		#
.L107:
# @OPUS@\upstream\celt\rate.c:307:          done = 1;
	mov.n	a10, a11	# done, done
	j	.L42		#
.L108:
# @OPUS@\upstream\celt\rate.c:305:             tmp = 0;
	mov.n	a2, a12	# tmp, tmp
# @OPUS@\upstream\celt\rate.c:302:          if (tmp >= alloc_floor)
	movi.n	a10, 0	# done,
.L42:
# @OPUS@\upstream\celt\rate.c:309:       tmp = IMIN(tmp, cap[j]);
	l32i.n	a15, a4, 0	# MEM[base: _1029, offset: 0B], tmp
	addi	a6, a6, -4	# ivtmp$177, ivtmp$177,
	bge	a2, a15, .L44	# tmp, tmp,
	mov.n	a15, a2	# tmp, tmp
.L44:
# @OPUS@\upstream\celt\rate.c:310:       bits[j] = tmp;
	s32i.n	a15, a8, 0	# MEM[base: _1028, offset: 0B], tmp
# @OPUS@\upstream\celt\rate.c:311:       psum += tmp;
	add.n	a14, a14, a15	# psum, psum, tmp
	addi	a9, a9, -4	# ivtmp$179, ivtmp$179,
	addi	a7, a7, -4	# ivtmp$181, ivtmp$181,
	addi	a4, a4, -4	# ivtmp$183, ivtmp$183,
	addi	a8, a8, -4	# ivtmp$185, ivtmp$185,
# @OPUS@\upstream\celt\rate.c:297:    for (j=end;j-->start;)
	bne	a3, a6, .L45	# _1023, ivtmp$177,
	j	.L41		#
.L106:
# @OPUS@\upstream\celt\rate.c:294:    psum = 0;
	mov.n	a14, a2	# psum, ivtmp_1278
.L41:
# @OPUS@\upstream\celt\rate.c:327:       if (j<=skip_start)
	l32i.n	a7, sp, 40	# %sfp,
	l32i.n	a8, sp, 60	# %sfp,
	blt	a7, a8, .L153	#,,
	j	.L46		#
.L64:
	l32i.n	a5, sp, 20	# %sfp,
	movi.n	a2, 0	#,
	addi	a5, a5, -4	#,,
	l32i.n	a7, sp, 40	# %sfp,
	s32i.n	a2, a14, 0	# MEM[base: _1092, offset: 0B],
	s32i.n	a5, sp, 20	# %sfp,
# @OPUS@\upstream\celt\rate.c:320:       j = codedBands-1;
	addi.n	a2, a12, -1	# j, <retval>,
	addi	a14, a14, -4	# ivtmp$162, ivtmp$162,
# @OPUS@\upstream\celt\rate.c:327:       if (j<=skip_start)
	bge	a7, a2, .L155	#, j,
.L65:
	mov.n	a12, a2	# <retval>, j
	j	.L49		#
.L46:
	l32i	a8, sp, 92	# %sfp,
	addi.n	a8, a8, 2	#,,
	s32i.n	a8, sp, 16	# %sfp,
	l32i.n	a8, sp, 56	# %sfp,
	s32i.n	a8, sp, 60	# %sfp,
	l32i	a8, sp, 96	# %sfp,
	j	.L48		#
.L155:
	mov.n	a14, a6	# psum, psum
	s32i	a13, sp, 96	# %sfp, intensity_rsv
	s32i.n	a12, sp, 60	# %sfp, <retval>
	mov.n	a8, a13	#, intensity_rsv
.L48:
# @OPUS@\upstream\celt\rate.c:330:          total += skip_rsv;
	l32i.n	a5, sp, 44	# %sfp,
	l32i	a7, sp, 124	# %sfp,
	add.n	a5, a5, a7	#,,
	s32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:395:    if (intensity_rsv > 0)
	bnez.n	a8, .L50	#,
	j	.L51		#
.L153:
	mov.n	a12, a8	# <retval>,
	l32i	a7, sp, 208	# pulses,
	l32i	a8, sp, 72	# %sfp,
	l32i.n	a5, sp, 24	# %sfp,
	add.n	a13, a7, a8	# ivtmp$162,,
	addi.n	a5, a5, 8	#,,
# @OPUS@\upstream\celt\rate.c:354:             if (codedBands > 17)
	mov.n	a6, a14	# psum, psum
	mov.n	a14, a13	# ivtmp$162, ivtmp$162
	l32i	a13, sp, 96	# %sfp, intensity_rsv
	s32i.n	a5, sp, 28	# %sfp,
.L49:
# @OPUS@\upstream\celt\rate.c:336:       percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l32i.n	a8, sp, 36	# %sfp,
	addi.n	a5, a12, 1	# codedBands, <retval>,
	l32i.n	a7, a8, 24	# MEM[(const opus_int16 * const *)m_153(D) + 24B], _280
# @OPUS@\upstream\celt\rate.c:336:       percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\celt\rate.c:336:       percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	slli	a11, a5, 1	# _282, codedBands,
	add.n	a3, a7, a11	# tmp663, _280, _282
# @OPUS@\upstream\celt\rate.c:336:       percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	add.n	a2, a7, a8	# tmp666, _280,
# @OPUS@\upstream\celt\rate.c:335:       left = total-psum;
	l32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:336:       percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l16si	a9, a2, 0	# *_288, _290
# @OPUS@\upstream\celt\rate.c:336:       percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l16si	a4, a3, 0	# *_283, _285
# @OPUS@\upstream\celt\rate.c:335:       left = total-psum;
	sub	a15, a8, a6	# left,, psum
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	sub	a3, a4, a9	#, _285, _290
	addi	a8, a11, -2	#, _282,
	mov.n	a2, a15	#, left
	s32i.n	a8, sp, 16	# %sfp,
	s32i	a4, sp, 136	#,
	s32i	a5, sp, 140	#,
	s32i	a6, sp, 148	#,
	s32i	a7, sp, 128	#,
	s32i	a9, sp, 132	#,
	s32i	a11, sp, 144	#,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	l32i.n	a8, sp, 16	# %sfp,
	l32i	a7, sp, 128	#,
# @OPUS@\upstream\celt\rate.c:337:       left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	l32i	a9, sp, 132	#,
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	add.n	a7, a7, a8	# tmp673, _280,
# @OPUS@\upstream\celt\rate.c:337:       left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	l32i	a4, sp, 136	#,
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	l16si	a7, a7, 0	# *_300, _302
# @OPUS@\upstream\celt\rate.c:337:       left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	sub	a3, a9, a4	# tmp677, _290, _285
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	add.n	a15, a15, a9	# tmp679, left, _290
# @OPUS@\upstream\celt\rate.c:337:       left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	mull	a3, a3, a2	# tmp678, tmp677, tmp672
# @OPUS@\upstream\celt\rate.c:339:       band_width = m->eBands[codedBands]-m->eBands[j];
	sub	a4, a4, a7	# band_width, _285, _302
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	sub	a15, a15, a7	# tmp680, tmp679, _302
# @OPUS@\upstream\celt\rate.c:344:       if (band_bits >= IMAX(thresh[j], alloc_floor+(1<<BITRES)))
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\rate.c:340:       band_bits = (int)(bits[j] + percoeff*band_width + rem);
	l32i.n	a9, a14, 0	# MEM[base: _1092, offset: 0B], _309
# @OPUS@\upstream\celt\rate.c:340:       band_bits = (int)(bits[j] + percoeff*band_width + rem);
	mull	a2, a2, a4	# tmp682, tmp672, band_width
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	add.n	a15, a3, a15	# rem, tmp678, tmp680
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	movi.n	a8, 0	#,
# @OPUS@\upstream\celt\rate.c:344:       if (band_bits >= IMAX(thresh[j], alloc_floor+(1<<BITRES)))
	l32i.n	a3, a7, 0	# MEM[base: _1091, offset: 0B], MEM[base: _1091, offset: 0B]
	l32i.n	a7, sp, 28	# %sfp,
# @OPUS@\upstream\celt\rate.c:338:       rem = IMAX(left-(m->eBands[j]-m->eBands[start]),0);
	movltz	a15, a8, a15	# rem,, rem
# @OPUS@\upstream\celt\rate.c:340:       band_bits = (int)(bits[j] + percoeff*band_width + rem);
	add.n	a2, a2, a9	# tmp683, tmp682, _309
# @OPUS@\upstream\celt\rate.c:340:       band_bits = (int)(bits[j] + percoeff*band_width + rem);
	add.n	a15, a15, a2	# band_bits, rem, tmp683
# @OPUS@\upstream\celt\rate.c:344:       if (band_bits >= IMAX(thresh[j], alloc_floor+(1<<BITRES)))
	l32i	a5, sp, 140	#,
	l32i	a6, sp, 148	#,
	l32i	a11, sp, 144	#,
	bge	a3, a7, .L53	# MEM[base: _1091, offset: 0B],,
	mov.n	a3, a7	# MEM[base: _1091, offset: 0B],
.L53:
# @OPUS@\upstream\celt\rate.c:344:       if (band_bits >= IMAX(thresh[j], alloc_floor+(1<<BITRES)))
	blt	a15, a3, .L52	# band_bits, MEM[base: _1091, offset: 0B],
# @OPUS@\upstream\celt\rate.c:346:          if (encode)
	l32i	a8, sp, 232	# encode,
	beqz.n	a8, .L54	#,
# @OPUS@\upstream\celt\rate.c:354:             if (codedBands > 17)
	movi.n	a3, 0x11	#,
# @OPUS@\upstream\celt\rate.c:357:                depth_threshold = 0;
	movi.n	a2, 0	# depth_threshold,
# @OPUS@\upstream\celt\rate.c:354:             if (codedBands > 17)
	bge	a3, a5, .L55	#, codedBands,
# @OPUS@\upstream\celt\rate.c:355:                depth_threshold = j<prev ? 7 : 9;
	l32i	a7, sp, 236	# prev,
	movi.n	a2, 7	# depth_threshold,
	blt	a12, a7, .L55	# <retval>,,
	movi.n	a2, 9	# depth_threshold,
.L55:
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	l32i.n	a8, sp, 32	# %sfp,
	addi.n	a3, a8, 2	# tmp690,,
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	bge	a3, a5, .L56	# tmp690, codedBands,
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	mull	a2, a4, a2	# tmp691, band_width, depth_threshold
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	l32i	a7, sp, 224	# LM,
	ssl	a7	#
	sll	a2, a2	# tmp692, tmp691
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	slli	a2, a2, 3	# tmp693, tmp692,
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	srai	a2, a2, 4	# tmp694, tmp693,
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	bge	a2, a15, .L57	# tmp694, band_bits,
# @OPUS@\upstream\celt\rate.c:363:             if (codedBands<=start+2 || (band_bits > (depth_threshold*band_width<<LM<<BITRES)>>4 && j<=signalBandwidth))
	l32i	a8, sp, 240	# signalBandwidth,
	blt	a8, a12, .L57	#, <retval>,
.L56:
# @OPUS@\upstream\celt\rate.c:366:                ec_enc_bit_logp(ec, 1, 1);
	movi.n	a4, 1	#,
	l32i	a2, sp, 228	# ec,
	mov.n	a3, a4	#,
	s32i	a5, sp, 140	#,
	mov.n	a14, a6	# psum, psum
	mov.n	a12, a11	# _282, _282
	s32i	a13, sp, 96	# %sfp, intensity_rsv
	call0	ec_enc_bit_logp		#
# @OPUS@\upstream\celt\rate.c:395:    if (intensity_rsv > 0)
	l32i	a7, sp, 96	# %sfp,
	l32i	a5, sp, 140	#,
	bnez.n	a7, .L60	#,
	s32i.n	a12, sp, 16	# %sfp, _282
	s32i.n	a5, sp, 60	# %sfp, codedBands
	j	.L51		#
.L57:
# @OPUS@\upstream\celt\rate.c:369:             ec_enc_bit_logp(ec, 0, 1);
	l32i	a2, sp, 228	# ec,
	movi.n	a4, 1	#,
	movi.n	a3, 0	#,
	s32i	a6, sp, 148	#,
	call0	ec_enc_bit_logp		#
	l32i	a6, sp, 148	#,
	j	.L61		#
.L54:
# @OPUS@\upstream\celt\rate.c:370:          } else if (ec_dec_bit_logp(ec, 1)) {
	l32i	a2, sp, 228	# ec,
	movi.n	a3, 1	#,
	s32i	a5, sp, 140	#,
	s32i	a6, sp, 148	#,
	s32i	a11, sp, 144	#,
	call0	ec_dec_bit_logp		#
# @OPUS@\upstream\celt\rate.c:370:          } else if (ec_dec_bit_logp(ec, 1)) {
	l32i	a5, sp, 140	#,
	l32i	a6, sp, 148	#,
	l32i	a11, sp, 144	#,
	bnez.n	a2, .L62	#,
.L61:
	l32i.n	a9, a14, 0	# MEM[base: _1092, offset: 0B], _309
# @OPUS@\upstream\celt\rate.c:374:          psum += 1<<BITRES;
	addi.n	a6, a6, 8	# psum, psum,
# @OPUS@\upstream\celt\rate.c:375:          band_bits -= 1<<BITRES;
	addi	a15, a15, -8	# band_bits, band_bits,
.L52:
	sub	a6, a6, a13	# _43, psum, intensity_rsv
# @OPUS@\upstream\celt\rate.c:378:       psum -= bits[j]+intensity_rsv;
	sub	a6, a6, a9	# psum, _43, _309
# @OPUS@\upstream\celt\rate.c:379:       if (intensity_rsv > 0)
	beqz.n	a13, .L63	# intensity_rsv,
# @OPUS@\upstream\celt\rate.c:380:          intensity_rsv = LOG2_FRAC_TABLE[j-start];
	l32i.n	a8, sp, 32	# %sfp,
	l32r	a3, .LC0	#, tmp703
	sub	a2, a12, a8	# tmp701, <retval>,
	add.n	a2, a2, a3	# tmp702, tmp701, tmp703
# @OPUS@\upstream\celt\rate.c:380:          intensity_rsv = LOG2_FRAC_TABLE[j-start];
	l8ui	a13, a2, 0	# MEM[base: _1086, offset: 0B], intensity_rsv
	add.n	a6, a6, a13	# psum, psum, intensity_rsv
.L63:
# @OPUS@\upstream\celt\rate.c:382:       if (band_bits >= alloc_floor)
	l32i.n	a5, sp, 24	# %sfp,
	blt	a15, a5, .L64	# band_bits,,
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\rate.c:327:       if (j<=skip_start)
	l32i.n	a8, sp, 40	# %sfp,
	addi	a7, a7, -4	#,,
	s32i.n	a5, a14, 0	# MEM[base: _1092, offset: 0B],
# @OPUS@\upstream\celt\rate.c:320:       j = codedBands-1;
	addi.n	a2, a12, -1	# j, <retval>,
	s32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\rate.c:385:          psum += alloc_floor;
	add.n	a6, a6, a5	# psum, psum,
	addi	a14, a14, -4	# ivtmp$162, ivtmp$162,
# @OPUS@\upstream\celt\rate.c:327:       if (j<=skip_start)
	blt	a8, a2, .L65	#, j,
	j	.L155		#
.L50:
# @OPUS@\upstream\celt\rate.c:397:       if (encode)
	l32i	a5, sp, 232	# encode,
	beqz.n	a5, .L66	#,
	l32i.n	a12, sp, 16	# %sfp, _282
	l32i.n	a5, sp, 60	# %sfp, codedBands
.L60:
# @OPUS@\upstream\celt\rate.c:399:          *intensity = IMIN(*intensity, codedBands);
	l32i	a7, sp, 192	# intensity,
	l32i.n	a3, a7, 0	# *intensity_206(D), _341
	bge	a5, a3, .L67	# codedBands, _341,
	mov.n	a3, a5	# _341, codedBands
.L67:
# @OPUS@\upstream\celt\rate.c:400:          ec_enc_uint(ec, *intensity-start, codedBands+1-start);
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:399:          *intensity = IMIN(*intensity, codedBands);
	l32i	a7, sp, 192	# intensity,
# @OPUS@\upstream\celt\rate.c:400:          ec_enc_uint(ec, *intensity-start, codedBands+1-start);
	sub	a4, a5, a8	# tmp709, codedBands,
# @OPUS@\upstream\celt\rate.c:400:          ec_enc_uint(ec, *intensity-start, codedBands+1-start);
	l32i	a2, sp, 228	# ec,
# @OPUS@\upstream\celt\rate.c:399:          *intensity = IMIN(*intensity, codedBands);
	s32i.n	a3, a7, 0	# *intensity_206(D), _341
# @OPUS@\upstream\celt\rate.c:400:          ec_enc_uint(ec, *intensity-start, codedBands+1-start);
	addi.n	a4, a4, 1	#, tmp709,
	sub	a3, a3, a8	#, _341,
	s32i	a5, sp, 140	#,
	call0	ec_enc_uint		#
	l32i	a8, sp, 192	# intensity,
	l32i	a5, sp, 140	#,
	s32i.n	a12, sp, 16	# %sfp, _282
	l32i.n	a2, a8, 0	# *intensity_206(D), pretmp_1154
	s32i.n	a5, sp, 60	# %sfp, codedBands
	j	.L68		#
.L66:
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	l32i.n	a5, sp, 60	# %sfp,
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	l32i	a2, sp, 228	# ec,
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	sub	a3, a5, a8	# tmp713,,
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	addi.n	a3, a3, 1	#, tmp713,
	call0	ec_dec_uint		#
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	l32i	a5, sp, 192	# intensity,
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	add.n	a2, a2, a8	# pretmp_1154,,
# @OPUS@\upstream\celt\rate.c:403:          *intensity = start+ec_dec_uint(ec, codedBands+1-start);
	s32i.n	a2, a5, 0	# *intensity_206(D), pretmp_1154
	j	.L68		#
.L51:
# @OPUS@\upstream\celt\rate.c:406:       *intensity = 0;
	l32i	a7, sp, 192	# intensity,
	movi.n	a2, 0	# tmp715,
	s32i.n	a2, a7, 0	# *intensity_206(D), tmp715
.L68:
# @OPUS@\upstream\celt\rate.c:407:    if (*intensity <= start)
	l32i.n	a8, sp, 32	# %sfp,
	blt	a8, a2, .L69	#, pretmp_1154,
# @OPUS@\upstream\celt\rate.c:409:       total += dual_stereo_rsv;
	l32i.n	a5, sp, 44	# %sfp,
	l32i	a7, sp, 112	# %sfp,
	add.n	a5, a5, a7	#,,
	s32i.n	a5, sp, 44	# %sfp,
	j	.L70		#
.L69:
# @OPUS@\upstream\celt\rate.c:412:    if (dual_stereo_rsv > 0)
	l32i	a8, sp, 112	# %sfp,
	beqz.n	a8, .L70	#,
# @OPUS@\upstream\celt\rate.c:414:       if (encode)
	l32i	a5, sp, 232	# encode,
	beqz.n	a5, .L71	#,
# @OPUS@\upstream\celt\rate.c:415:          ec_enc_bit_logp(ec, *dual_stereo, 1);
	l32i	a7, sp, 196	# dual_stereo,
	l32i	a2, sp, 228	# ec,
	l32i.n	a3, a7, 0	# *dual_stereo_207(D),
	movi.n	a4, 1	#,
	call0	ec_enc_bit_logp		#
	j	.L72		#
.L71:
# @OPUS@\upstream\celt\rate.c:417:          *dual_stereo = ec_dec_bit_logp(ec, 1);
	l32i	a2, sp, 228	# ec,
	movi.n	a3, 1	#,
	call0	ec_dec_bit_logp		#
# @OPUS@\upstream\celt\rate.c:417:          *dual_stereo = ec_dec_bit_logp(ec, 1);
	l32i	a8, sp, 196	# dual_stereo,
	s32i.n	a2, a8, 0	# *dual_stereo_207(D),
	j	.L72		#
.L70:
# @OPUS@\upstream\celt\rate.c:420:       *dual_stereo = 0;
	l32i	a5, sp, 196	# dual_stereo,
	movi.n	a2, 0	# tmp716,
	s32i.n	a2, a5, 0	# *dual_stereo_207(D), tmp716
.L72:
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l32i.n	a15, a8, 24	# MEM[(const opus_int16 * const *)m_153(D) + 24B], _363
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\celt\rate.c:423:    left = total-psum;
	l32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	add.n	a13, a15, a7	# tmp717, _363,
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	add.n	a12, a15, a8	# _371, _363,
# @OPUS@\upstream\celt\rate.c:423:    left = total-psum;
	sub	a14, a5, a14	# left,, psum
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l16si	a5, a13, 0	# *_366, _368
# @OPUS@\upstream\celt\rate.c:424:    percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	l16si	a13, a12, 0	# *_371, _373
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a2, a14	#, left
	sub	a3, a5, a13	#, _368, _373
	s32i	a5, sp, 140	#,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\rate.c:425:    left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	l32i	a5, sp, 140	#,
# @OPUS@\upstream\celt\rate.c:426:    for (j=start;j<codedBands;j++)
	l32i.n	a7, sp, 60	# %sfp,
# @OPUS@\upstream\celt\rate.c:425:    left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	sub	a5, a13, a5	# tmp726, _373, _368
# @OPUS@\upstream\celt\rate.c:425:    left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	mull	a5, a5, a2	# tmp727, tmp726, percoeff
# @OPUS@\upstream\celt\rate.c:425:    left -= (m->eBands[codedBands]-m->eBands[start])*percoeff;
	add.n	a5, a5, a14	# left, tmp727, left
# @OPUS@\upstream\celt\rate.c:426:    for (j=start;j<codedBands;j++)
	l32i.n	a14, sp, 32	# %sfp,
	bge	a14, a7, .L111	#,,
	l32i	a8, sp, 80	# %sfp,
	l32i	a7, sp, 208	# pulses,
	addi.n	a9, a8, 4	# _1231,,
	l32i.n	a8, sp, 60	# %sfp,
	add.n	a14, a7, a9	# ivtmp$130,, _1231
	slli	a3, a8, 1	# tmp728,,
	mov.n	a6, a12	# ivtmp$129, _371
	add.n	a15, a15, a3	# _1247, _363, tmp728
	mov.n	a4, a12	# ivtmp$151, _371
	mov.n	a7, a14	# ivtmp$150, ivtmp$130
.L74:
# @OPUS@\upstream\celt\rate.c:427:       bits[j] += ((int)percoeff*(m->eBands[j+1]-m->eBands[j]));
	l16si	a3, a4, 2	# MEM[base: _1248, offset: 2B], tmp729
# @OPUS@\upstream\celt\rate.c:427:       bits[j] += ((int)percoeff*(m->eBands[j+1]-m->eBands[j]));
	l16si	a10, a4, 0	# MEM[base: _1248, offset: 0B], tmp732
# @OPUS@\upstream\celt\rate.c:427:       bits[j] += ((int)percoeff*(m->eBands[j+1]-m->eBands[j]));
	l32i.n	a8, a7, 0	# MEM[base: _1239, offset: 0B], MEM[base: _1239, offset: 0B]
# @OPUS@\upstream\celt\rate.c:427:       bits[j] += ((int)percoeff*(m->eBands[j+1]-m->eBands[j]));
	sub	a3, a3, a10	# tmp735, tmp729, tmp732
# @OPUS@\upstream\celt\rate.c:427:       bits[j] += ((int)percoeff*(m->eBands[j+1]-m->eBands[j]));
	mull	a3, a3, a2	# tmp736, tmp735, percoeff
	addi.n	a4, a4, 2	# ivtmp$151, ivtmp$151,
# @OPUS@\upstream\celt\rate.c:427:       bits[j] += ((int)percoeff*(m->eBands[j+1]-m->eBands[j]));
	add.n	a3, a8, a3	# tmp737, MEM[base: _1239, offset: 0B], tmp736
	s32i.n	a3, a7, 0	# MEM[base: _1239, offset: 0B], tmp737
	addi.n	a7, a7, 4	# ivtmp$150, ivtmp$150,
# @OPUS@\upstream\celt\rate.c:426:    for (j=start;j<codedBands;j++)
	bne	a4, a15, .L74	# ivtmp$151, _1247,
	mov.n	a3, a14	# ivtmp$143, ivtmp$130
.L76:
# @OPUS@\upstream\celt\rate.c:430:       int tmp = (int)IMIN(left, m->eBands[j+1]-m->eBands[j]);
	l16si	a2, a12, 2	# MEM[base: _1168, offset: 2B], tmp739
	l16si	a4, a12, 0	# MEM[base: _1168, offset: 0B], tmp742
	addi.n	a12, a12, 2	# ivtmp$142, ivtmp$142,
	sub	a2, a2, a4	# tmp, tmp739, tmp742
# @OPUS@\upstream\celt\rate.c:430:       int tmp = (int)IMIN(left, m->eBands[j+1]-m->eBands[j]);
	bge	a5, a2, .L75	# left, tmp,
	mov.n	a2, a5	# tmp, left
.L75:
# @OPUS@\upstream\celt\rate.c:431:       bits[j] += tmp;
	l32i.n	a4, a3, 0	# MEM[base: _1162, offset: 0B], MEM[base: _1162, offset: 0B]
# @OPUS@\upstream\celt\rate.c:432:       left -= tmp;
	sub	a5, a5, a2	# left, left, tmp
# @OPUS@\upstream\celt\rate.c:431:       bits[j] += tmp;
	add.n	a2, a4, a2	# tmp746, MEM[base: _1162, offset: 0B], tmp
	s32i.n	a2, a3, 0	# MEM[base: _1162, offset: 0B], tmp746
	addi.n	a3, a3, 4	# ivtmp$143, ivtmp$143,
# @OPUS@\upstream\celt\rate.c:428:    for (j=start;j<codedBands;j++)
	bne	a12, a15, .L76	# ivtmp$142, _1247,
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	l32i	a5, sp, 220	# C,
	l32i	a8, sp, 212	# ebits,
	addi	a2, a5, -2	# tmp1186,,
# @OPUS@\upstream\celt\rate.c:436:    balance = 0;
	movi.n	a4, 0	#,
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	movi.n	a7, 1	#,
# @OPUS@\upstream\celt\rate.c:436:    balance = 0;
	s32i.n	a4, sp, 20	# %sfp,
	add.n	a15, a8, a9	# ivtmp$131,, _1231
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	moveqz	a4, a7, a2	#,, tmp1186
	l32i	a5, sp, 216	# fine_priority,
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	l32i	a8, sp, 76	# %sfp,
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	mov.n	a2, a4	# tmp1187,
	add.n	a7, a5, a9	# ivtmp$132,, _1231
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	extui	a2, a2, 0, 8	#, tmp1187
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	addi.n	a8, a8, 3	#,,
# @OPUS@\upstream\celt\rate.c:494:          excess = MAX32(0,bit-(C<<BITRES));
	l32i.n	a11, sp, 20	# %sfp, tmp1184
# @OPUS@\upstream\celt\rate.c:428:    for (j=start;j<codedBands;j++)
	l32i.n	a4, sp, 32	# %sfp, j
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	s32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	mov.n	a10, a7	# ivtmp$132, ivtmp$132
.L92:
# @OPUS@\upstream\celt\rate.c:445:       N0 = m->eBands[j+1]-m->eBands[j];
	l16si	a2, a6, 0	# MEM[base: _1104, offset: 0B], tmp751
# @OPUS@\upstream\celt\rate.c:445:       N0 = m->eBands[j+1]-m->eBands[j];
	l16si	a7, a6, 2	# MEM[base: _1104, offset: 2B], tmp748
# @OPUS@\upstream\celt\rate.c:446:       N=N0<<LM;
	l32i	a8, sp, 224	# LM,
# @OPUS@\upstream\celt\rate.c:445:       N0 = m->eBands[j+1]-m->eBands[j];
	sub	a7, a7, a2	# N0, tmp748, tmp751
# @OPUS@\upstream\celt\rate.c:447:       bit = (opus_int32)bits[j]+balance;
	l32i.n	a5, a14, 0	# MEM[base: _24, offset: 0B], MEM[base: _24, offset: 0B]
# @OPUS@\upstream\celt\rate.c:446:       N=N0<<LM;
	ssl	a8	#
	sll	a7, a7	# N, N0
# @OPUS@\upstream\celt\rate.c:447:       bit = (opus_int32)bits[j]+balance;
	l32i.n	a8, sp, 20	# %sfp,
	slli	a3, a4, 1	# _177, j,
	add.n	a2, a8, a5	# bit,, MEM[base: _24, offset: 0B]
# @OPUS@\upstream\celt\rate.c:449:       if (N>1)
	blti	a7, 2, .L77	# N,,
# @OPUS@\upstream\celt\rate.c:451:          excess = MAX32(bit-cap[j],0);
	l32i	a8, sp, 84	# %sfp,
	slli	a5, a4, 2	# tmp756, j,
	add.n	a5, a8, a5	# tmp757,, tmp756
	l32i.n	a8, sp, 36	# %sfp,
	l32i.n	a12, a5, 0	# MEM[base: _1106, offset: 0B], MEM[base: _1106, offset: 0B]
	l32i.n	a5, a8, 48	# MEM[(const opus_int16 * const *)m_153(D) + 48B], MEM[(const opus_int16 * const *)m_153(D) + 48B]
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	l32i	a8, sp, 220	# C,
	add.n	a3, a5, a3	# tmp761, MEM[(const opus_int16 * const *)m_153(D) + 48B], _177
	l16si	a5, a3, 0	# *_1251, tmp762
# @OPUS@\upstream\celt\rate.c:451:          excess = MAX32(bit-cap[j],0);
	sub	a12, a2, a12	# excess, bit, MEM[base: _1106, offset: 0B]
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	mull	a3, a8, a7	# den,, N
	l32i	a8, sp, 68	# %sfp,
# @OPUS@\upstream\celt\rate.c:451:          excess = MAX32(bit-cap[j],0);
	movltz	a12, a11, a12	# excess, tmp1184, excess
# @OPUS@\upstream\celt\rate.c:452:          bits[j] = bit-excess;
	sub	a2, a2, a12	# _442, bit, excess
	add.n	a5, a5, a8	# _1254, tmp762,
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\rate.c:452:          bits[j] = bit-excess;
	s32i.n	a2, a14, 0	# MEM[base: _24, offset: 0B], _442
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	beqz.n	a8, .L78	#,
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	blti	a7, 3, .L78	# N,,
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	l32i	a8, sp, 196	# dual_stereo,
	l32i.n	a7, a8, 0	# *dual_stereo_207(D), *dual_stereo_207(D)
	bnez.n	a7, .L80	# *dual_stereo_207(D),
# @OPUS@\upstream\celt\rate.c:455:          den=(C*N+ ((C==2 && N>2 && !*dual_stereo && j<*intensity) ? 1 : 0));
	l32i	a7, sp, 192	# intensity,
	l32i.n	a8, a7, 0	# *intensity_206(D), *intensity_206(D)
	movi.n	a7, 1	# tmp775,
	blt	a4, a8, .L81	# j, *intensity_206(D),
	mov.n	a7, a11	# tmp775, tmp1184
.L81:
	add.n	a3, a3, a7	# den, den, tmp775
	j	.L80		#
.L78:
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	slli	a8, a3, 28	# tmp781, den,
	sub	a8, a8, a3	# tmp782, tmp781, den
	slli	a8, a8, 2	# tmp783, tmp782,
	sub	a8, a8, a3	# tmp784, tmp783, den
# @OPUS@\upstream\celt\rate.c:457:          NClogN = den*(m->logN[j] + logM);
	mull	a5, a3, a5	# NClogN, den, _1254
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	slli	a13, a8, 2	# tmp785, tmp784,
	sub	a8, a13, a3	# tmp786, tmp785, den
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	srai	a9, a5, 1	# tmp779, NClogN,
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	add.n	a13, a9, a8	# offset, tmp779, tmp786
	slli	a8, a3, 3	#, den,
	s32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\celt\rate.c:464:          if (N==2)
	bnei	a7, 2, .L82	# N,,
# @OPUS@\upstream\celt\rate.c:465:             offset += den<<BITRES>>2;
	srai	a7, a8, 2	# tmp787,,
# @OPUS@\upstream\celt\rate.c:465:             offset += den<<BITRES>>2;
	add.n	a13, a13, a7	# offset, offset, tmp787
.L82:
# @OPUS@\upstream\celt\rate.c:469:          if (bits[j] + offset < den*2<<BITRES)
	add.n	a8, a2, a13	# _464, _442, offset
# @OPUS@\upstream\celt\rate.c:469:          if (bits[j] + offset < den*2<<BITRES)
	slli	a7, a3, 4	# tmp789, den,
# @OPUS@\upstream\celt\rate.c:469:          if (bits[j] + offset < den*2<<BITRES)
	slli	a9, a3, 1	# tmp788, den,
# @OPUS@\upstream\celt\rate.c:469:          if (bits[j] + offset < den*2<<BITRES)
	bge	a8, a7, .L83	# _464, tmp789,
# @OPUS@\upstream\celt\rate.c:470:             offset += NClogN>>2;
	srai	a5, a5, 2	# tmp790, NClogN,
# @OPUS@\upstream\celt\rate.c:470:             offset += NClogN>>2;
	add.n	a13, a13, a5	# offset, offset, tmp790
	j	.L84		#
.L83:
# @OPUS@\upstream\celt\rate.c:471:          else if (bits[j] + offset < den*3<<BITRES)
	add.n	a9, a9, a3	# tmp793, tmp788, den
# @OPUS@\upstream\celt\rate.c:471:          else if (bits[j] + offset < den*3<<BITRES)
	slli	a9, a9, 3	# tmp794, tmp793,
# @OPUS@\upstream\celt\rate.c:471:          else if (bits[j] + offset < den*3<<BITRES)
	bge	a8, a9, .L84	# _464, tmp794,
# @OPUS@\upstream\celt\rate.c:472:             offset += NClogN>>3;
	srai	a5, a5, 3	# tmp795, NClogN,
# @OPUS@\upstream\celt\rate.c:472:             offset += NClogN>>3;
	add.n	a13, a13, a5	# offset, offset, tmp795
.L84:
# @OPUS@\upstream\celt\rate.c:475:          ebits[j] = IMAX(0, (bits[j] + offset + (den<<(BITRES-1))));
	slli	a5, a3, 2	# tmp797, den,
	add.n	a2, a5, a2	# tmp798, tmp797, _442
	add.n	a2, a2, a13	# tmp796, tmp798, offset
	movltz	a2, a11, a2	# tmp796, tmp1184, tmp796
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	s32i	a4, sp, 136	#,
	s32i	a6, sp, 148	#,
	s32i	a10, sp, 128	#,
	s32i	a11, sp, 144	#,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\rate.c:476:          ebits[j] = celt_udiv(ebits[j], den)>>BITRES;
	srli	a2, a2, 3	# _483,,
# @OPUS@\upstream\celt\rate.c:479:          if (C*ebits[j] > (bits[j]>>BITRES))
	l32i	a7, sp, 220	# C,
# @OPUS@\upstream\celt\rate.c:476:          ebits[j] = celt_udiv(ebits[j], den)>>BITRES;
	s32i.n	a2, a15, 0	# MEM[base: _33, offset: 0B], _483
# @OPUS@\upstream\celt\rate.c:479:          if (C*ebits[j] > (bits[j]>>BITRES))
	l32i.n	a3, a14, 0	# MEM[base: _24, offset: 0B], _485
# @OPUS@\upstream\celt\rate.c:479:          if (C*ebits[j] > (bits[j]>>BITRES))
	mull	a5, a7, a2	# tmp804,, _483
# @OPUS@\upstream\celt\rate.c:479:          if (C*ebits[j] > (bits[j]>>BITRES))
	srai	a7, a3, 3	# tmp805, _485,
# @OPUS@\upstream\celt\rate.c:479:          if (C*ebits[j] > (bits[j]>>BITRES))
	l32i	a4, sp, 136	#,
	l32i	a6, sp, 148	#,
	l32i	a10, sp, 128	#,
	l32i	a11, sp, 144	#,
	bge	a7, a5, .L85	# tmp805, tmp804,
# @OPUS@\upstream\celt\rate.c:480:             ebits[j] = bits[j] >> stereo >> BITRES;
	l32i	a8, sp, 76	# %sfp,
	ssr	a8	#
	sra	a2, a3	# tmp806, _485
# @OPUS@\upstream\celt\rate.c:480:             ebits[j] = bits[j] >> stereo >> BITRES;
	srai	a2, a2, 3	# _483, tmp806,
.L85:
# @OPUS@\upstream\celt\rate.c:483:          ebits[j] = IMIN(ebits[j], MAX_FINE_BITS);
	movi.n	a3, 8	#,
	bge	a3, a2, .L86	#, _490,
	mov.n	a2, a3	# _490,
.L86:
# @OPUS@\upstream\celt\rate.c:483:          ebits[j] = IMIN(ebits[j], MAX_FINE_BITS);
	s32i.n	a2, a15, 0	# MEM[base: _33, offset: 0B], _490
# @OPUS@\upstream\celt\rate.c:487:          fine_priority[j] = ebits[j]*(den<<BITRES) >= bits[j]+offset;
	l32i.n	a5, sp, 16	# %sfp,
# @OPUS@\upstream\celt\rate.c:487:          fine_priority[j] = ebits[j]*(den<<BITRES) >= bits[j]+offset;
	l32i.n	a3, a14, 0	# MEM[base: _24, offset: 0B], MEM[base: _24, offset: 0B]
# @OPUS@\upstream\celt\rate.c:487:          fine_priority[j] = ebits[j]*(den<<BITRES) >= bits[j]+offset;
	mull	a8, a2, a5	# tmp810, _490,
# @OPUS@\upstream\celt\rate.c:487:          fine_priority[j] = ebits[j]*(den<<BITRES) >= bits[j]+offset;
	add.n	a13, a13, a3	# tmp811, offset, MEM[base: _24, offset: 0B]
# @OPUS@\upstream\celt\rate.c:487:          fine_priority[j] = ebits[j]*(den<<BITRES) >= bits[j]+offset;
	movi.n	a2, 1	# tmp813,
	bge	a8, a13, .L87	# tmp810, tmp811,
	mov.n	a2, a11	# tmp813, tmp1184
.L87:
# @OPUS@\upstream\celt\rate.c:487:          fine_priority[j] = ebits[j]*(den<<BITRES) >= bits[j]+offset;
	s32i.n	a2, a10, 0	# MEM[base: _36, offset: 0B], tmp813
# @OPUS@\upstream\celt\rate.c:490:          bits[j] -= C*ebits[j]<<BITRES;
	l32i.n	a2, a15, 0	# MEM[base: _33, offset: 0B], MEM[base: _33, offset: 0B]
	l32i	a7, sp, 220	# C,
# @OPUS@\upstream\celt\rate.c:490:          bits[j] -= C*ebits[j]<<BITRES;
	l32i.n	a3, a14, 0	# MEM[base: _24, offset: 0B], MEM[base: _24, offset: 0B]
# @OPUS@\upstream\celt\rate.c:490:          bits[j] -= C*ebits[j]<<BITRES;
	mull	a2, a7, a2	# tmp815,, MEM[base: _33, offset: 0B]
# @OPUS@\upstream\celt\rate.c:490:          bits[j] -= C*ebits[j]<<BITRES;
	slli	a2, a2, 3	# tmp817, tmp815,
# @OPUS@\upstream\celt\rate.c:490:          bits[j] -= C*ebits[j]<<BITRES;
	sub	a2, a3, a2	# tmp818, MEM[base: _24, offset: 0B], tmp817
	s32i.n	a2, a14, 0	# MEM[base: _24, offset: 0B], tmp818
	j	.L88		#
.L77:
# @OPUS@\upstream\celt\rate.c:494:          excess = MAX32(0,bit-(C<<BITRES));
	l32i.n	a8, sp, 24	# %sfp,
	sub	a12, a2, a8	# excess, bit,
# @OPUS@\upstream\celt\rate.c:494:          excess = MAX32(0,bit-(C<<BITRES));
	movltz	a12, a11, a12	# excess, tmp1184, excess
# @OPUS@\upstream\celt\rate.c:495:          bits[j] = bit-excess;
	sub	a2, a2, a12	# tmp821, bit, excess
# @OPUS@\upstream\celt\rate.c:495:          bits[j] = bit-excess;
	s32i.n	a2, a14, 0	# MEM[base: _24, offset: 0B], tmp821
# @OPUS@\upstream\celt\rate.c:496:          ebits[j] = 0;
	s32i.n	a11, a15, 0	# MEM[base: _32, offset: 0B], tmp1184
# @OPUS@\upstream\celt\rate.c:497:          fine_priority[j] = 1;
	movi.n	a2, 1	#,
	s32i.n	a2, a10, 0	# MEM[base: _37, offset: 0B],
.L88:
# @OPUS@\upstream\celt\rate.c:503:       if(excess > 0)
	beqz.n	a12, .L112	# excess,
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	l32i.n	a3, a15, 0	# MEM[base: _35, offset: 0B], _510
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	l32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	movi.n	a8, 8	#,
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	ssr	a7	#
	sra	a5, a12	# extra_fine, excess
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	sub	a2, a8, a3	# tmp827,, _510
# @OPUS@\upstream\celt\rate.c:507:          extra_fine = IMIN(excess>>(stereo+BITRES),MAX_FINE_BITS-ebits[j]);
	bge	a2, a5, .L90	# tmp827, extra_fine,
	mov.n	a5, a2	# extra_fine, tmp827
.L90:
# @OPUS@\upstream\celt\rate.c:509:          extra_bits = extra_fine*C<<BITRES;
	l32i	a7, sp, 220	# C,
# @OPUS@\upstream\celt\rate.c:510:          fine_priority[j] = extra_bits >= excess-balance;
	l32i.n	a8, sp, 20	# %sfp,
# @OPUS@\upstream\celt\rate.c:509:          extra_bits = extra_fine*C<<BITRES;
	mull	a2, a7, a5	# tmp829,, extra_fine
# @OPUS@\upstream\celt\rate.c:508:          ebits[j] += extra_fine;
	add.n	a3, a3, a5	# tmp828, _510, extra_fine
	s32i.n	a3, a15, 0	# MEM[base: _35, offset: 0B], tmp828
# @OPUS@\upstream\celt\rate.c:509:          extra_bits = extra_fine*C<<BITRES;
	slli	a2, a2, 3	# extra_bits, tmp829,
# @OPUS@\upstream\celt\rate.c:510:          fine_priority[j] = extra_bits >= excess-balance;
	sub	a5, a12, a8	# tmp830, excess,
# @OPUS@\upstream\celt\rate.c:510:          fine_priority[j] = extra_bits >= excess-balance;
	movi.n	a3, 1	# tmp831,
	bge	a2, a5, .L91	# extra_bits, tmp830,
	mov.n	a3, a11	# tmp831, tmp1184
.L91:
# @OPUS@\upstream\celt\rate.c:511:          excess -= extra_bits;
	sub	a2, a12, a2	#, excess, extra_bits
# @OPUS@\upstream\celt\rate.c:510:          fine_priority[j] = extra_bits >= excess-balance;
	s32i.n	a3, a10, 0	# MEM[base: _38, offset: 0B], tmp831
# @OPUS@\upstream\celt\rate.c:511:          excess -= extra_bits;
	s32i.n	a2, sp, 20	# %sfp,
	j	.L89		#
.L112:
# @OPUS@\upstream\celt\rate.c:503:       if(excess > 0)
	s32i.n	a11, sp, 20	# %sfp, tmp1184
.L89:
# @OPUS@\upstream\celt\rate.c:437:    for (j=start;j<codedBands;j++)
	l32i.n	a5, sp, 60	# %sfp,
# @OPUS@\upstream\celt\rate.c:437:    for (j=start;j<codedBands;j++)
	addi.n	a4, a4, 1	# j, j,
	addi.n	a6, a6, 2	# ivtmp$129, ivtmp$129,
	addi.n	a14, a14, 4	# ivtmp$130, ivtmp$130,
	addi.n	a15, a15, 4	# ivtmp$131, ivtmp$131,
	addi.n	a10, a10, 4	# ivtmp$132, ivtmp$132,
# @OPUS@\upstream\celt\rate.c:437:    for (j=start;j<codedBands;j++)
	bne	a4, a5, .L92	# j,,
	s32i.n	a5, sp, 32	# %sfp,
	mov.n	a14, a5	#,
	j	.L73		#
.L111:
# @OPUS@\upstream\celt\rate.c:436:    balance = 0;
	movi.n	a7, 0	#,
	s32i.n	a7, sp, 20	# %sfp,
.L73:
# @OPUS@\upstream\celt\rate.c:520:    *_balance = balance;
	l32i.n	a8, sp, 20	# %sfp,
	l32i	a2, sp, 204	# balance, balance
	s32i.n	a8, a2, 0	# *balance_205(D),
# @OPUS@\upstream\celt\rate.c:523:    for (;j<end;j++)
	l32i.n	a8, sp, 56	# %sfp,
	bge	a14, a8, .L95	#,,
	l32i	a8, sp, 72	# %sfp,
	slli	a5, a14, 2	# _678,,
	addi.n	a7, a8, 4	# tmp835,,
	l32i	a14, sp, 208	# pulses,
	l32i	a8, sp, 212	# ebits,
	add.n	a3, a14, a5	# ivtmp$120,, _678
	add.n	a4, a8, a5	# ivtmp$121,, _678
	l32i	a14, sp, 216	# fine_priority,
	l32i	a8, sp, 208	# pulses,
# @OPUS@\upstream\celt\rate.c:527:       bits[j] = 0;
	l32i	a9, sp, 76	# %sfp, tmp615
	add.n	a7, a8, a7	# _1224,, tmp835
	add.n	a5, a14, a5	# ivtmp$122,, _678
	movi.n	a8, 0	# tmp839,
.L94:
# @OPUS@\upstream\celt\rate.c:525:       ebits[j] = bits[j] >> stereo >> BITRES;
	l32i.n	a2, a3, 0	# MEM[base: _707, offset: 0B], MEM[base: _707, offset: 0B]
	ssr	a9	# tmp615
	sra	a2, a2	# tmp836, MEM[base: _707, offset: 0B]
# @OPUS@\upstream\celt\rate.c:525:       ebits[j] = bits[j] >> stereo >> BITRES;
	srai	a2, a2, 3	# tmp838, tmp836,
# @OPUS@\upstream\celt\rate.c:525:       ebits[j] = bits[j] >> stereo >> BITRES;
	s32i.n	a2, a4, 0	# MEM[base: _710, offset: 0B], tmp838
# @OPUS@\upstream\celt\rate.c:527:       bits[j] = 0;
	s32i.n	a8, a3, 0	# MEM[base: _707, offset: 0B], tmp839
# @OPUS@\upstream\celt\rate.c:528:       fine_priority[j] = ebits[j]<1;
	l32i.n	a6, a4, 0	# MEM[base: _710, offset: 0B], MEM[base: _710, offset: 0B]
	addi.n	a3, a3, 4	# ivtmp$120, ivtmp$120,
	addi.n	a2, a6, -1	# tmp843, MEM[base: _710, offset: 0B],
	or	a2, a2, a6	# tmp845, tmp843, MEM[base: _710, offset: 0B]
	extui	a2, a2, 31, 1	# tmp847, tmp845,
# @OPUS@\upstream\celt\rate.c:528:       fine_priority[j] = ebits[j]<1;
	s32i.n	a2, a5, 0	# MEM[base: _1228, offset: 0B], tmp847
	addi.n	a4, a4, 4	# ivtmp$121, ivtmp$121,
	addi.n	a5, a5, 4	# ivtmp$122, ivtmp$122,
# @OPUS@\upstream\celt\rate.c:523:    for (;j<end;j++)
	bne	a3, a7, .L94	# ivtmp$120, _1224,
	j	.L95		#
.L62:
	s32i	a13, sp, 96	# %sfp, intensity_rsv
# @OPUS@\upstream\celt\rate.c:336:       percoeff = celt_udiv(left, m->eBands[codedBands]-m->eBands[start]);
	s32i.n	a11, sp, 16	# %sfp, _282
# @OPUS@\upstream\celt\rate.c:395:    if (intensity_rsv > 0)
	s32i.n	a5, sp, 60	# %sfp, codedBands
	mov.n	a14, a6	# psum, psum
	bnez.n	a13, .L66	# intensity_rsv,
	j	.L51		#
.L80:
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	slli	a7, a3, 28	# tmp849, den,
	sub	a7, a7, a3	# tmp850, tmp849, den
	slli	a7, a7, 2	# tmp851, tmp850,
	sub	a13, a7, a3	# tmp852, tmp851, den
# @OPUS@\upstream\celt\rate.c:457:          NClogN = den*(m->logN[j] + logM);
	mull	a5, a5, a3	# NClogN, _1254, den
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	slli	a13, a13, 2	# tmp853, tmp852,
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	srai	a7, a5, 1	# tmp855, NClogN,
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	sub	a13, a13, a3	# tmp854, tmp853, den
# @OPUS@\upstream\celt\rate.c:461:          offset = (NClogN>>1)-den*FINE_OFFSET;
	add.n	a13, a13, a7	# offset, tmp854, tmp855
	slli	a7, a3, 3	#, den,
	s32i.n	a7, sp, 16	# %sfp,
	j	.L82		#
.L95:
# @OPUS@\upstream\celt\rate.c:530:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\rate.c:643:    RESTORE_STACK;
	l32i.n	a2, sp, 8	# _saved_stack,
	l32i.n	a3, sp, 12	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\rate.c:645: }
	l32i	a0, sp, 188	#,
	movi	a9, 0xc0	#,
	l32i.n	a2, sp, 60	# %sfp,
	l32i	a12, sp, 184	#,
	l32i	a13, sp, 180	#,
	l32i	a14, sp, 176	#,
	l32i	a15, sp, 172	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	clt_compute_allocation, .-clt_compute_allocation
	.section	.rodata.LOG2_FRAC_TABLE,"a"
	.align	4
	.type	LOG2_FRAC_TABLE, @object
	.size	LOG2_FRAC_TABLE, 24
LOG2_FRAC_TABLE:
	.byte	0
	.byte	8
	.byte	13
	.byte	16
	.byte	19
	.byte	21
	.byte	23
	.byte	24
	.byte	26
	.byte	27
	.byte	28
	.byte	29
	.byte	30
	.byte	31
	.byte	32
	.byte	32
	.byte	33
	.byte	34
	.byte	34
	.byte	35
	.byte	36
	.byte	36
	.byte	37
	.byte	37
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
