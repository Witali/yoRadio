# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/pitch.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"pitch.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\pitch.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\pitch.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\pitch.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\pitch.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\pitch.c.s.raw
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
	.section	.text.find_best_pitch,"ax",@progbits
	.literal_position
	.align	4
	.type	find_best_pitch, @function
# Function: find_best_pitch
# Module: upstream/celt/pitch.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "mathops.h"
# C context: #include "celt_lpc.h"
# C context:
# C context: static void find_best_pitch(opus_val32 *xcorr, opus_val16 *y, int len,
# C context: int max_pitch, int *best_pitch
# C context: #ifdef FIXED_POINT
# C context: , int yshift, opus_val32 maxcorr
# C context: #endif
find_best_pitch:
	addi	sp, sp, -48	#,,
	s32i.n	a6, sp, 20	# %sfp, best_pitch
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	l32i.n	a6, sp, 48	# maxcorr, maxcorr
# @OPUS@\upstream\celt\pitch.c:59:    xshift = celt_ilog2(maxcorr)-14;
	movi.n	a9, 0x1f	# tmp138,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a6, a6	# _116, maxcorr
# @OPUS@\upstream\celt\pitch.c:59:    xshift = celt_ilog2(maxcorr)-14;
	sub	a6, a9, a6	# _2, tmp138, _116
# @OPUS@\upstream\celt\pitch.c:66:    best_pitch[0] = 0;
	l32i.n	a10, sp, 20	# %sfp,
# @OPUS@\upstream\celt\pitch.c:51: {
	s32i.n	a12, sp, 44	#,
	s32i.n	a13, sp, 40	#,
	s32i.n	a14, sp, 36	#,
	s32i.n	a15, sp, 32	#,
# @OPUS@\upstream\celt\pitch.c:67:    best_pitch[1] = 1;
	movi.n	a8, 1	# tmp140,
# @OPUS@\upstream\celt\pitch.c:66:    best_pitch[0] = 0;
	movi.n	a9, 0	# tmp139,
# @OPUS@\upstream\celt\pitch.c:51: {
	s32i.n	a5, sp, 0	# %sfp, max_pitch
# @OPUS@\upstream\celt\pitch.c:59:    xshift = celt_ilog2(maxcorr)-14;
	addi	a5, a6, -14	#, _2,
# @OPUS@\upstream\celt\pitch.c:66:    best_pitch[0] = 0;
	s32i.n	a9, a10, 0	# *best_pitch_95(D), tmp139
# @OPUS@\upstream\celt\pitch.c:67:    best_pitch[1] = 1;
	s32i.n	a8, a10, 4	# MEM[(int *)best_pitch_95(D) + 4B], tmp140
# @OPUS@\upstream\celt\pitch.c:59:    xshift = celt_ilog2(maxcorr)-14;
	s32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.c:68:    for (j=0;j<len;j++)
	blt	a4, a8, .L11	# len,,
	ssl	a8	#
	sll	a10, a4	# tmp141, len
	mov.n	a9, a3	# ivtmp$97, y
	add.n	a10, a10, a3	# _234, tmp141, y
# @OPUS@\upstream\celt\pitch.c:53:    opus_val32 Syy=1;
	mov.n	a5, a8	# Syy, tmp140
.L3:
# @OPUS@\upstream\celt\pitch.c:69:       Syy = ADD32(Syy, SHR32(MULT16_16(y[j],y[j]), yshift));
	l16si	a8, a9, 0	# MEM[base: _131, offset: 0B], _7
	addi.n	a9, a9, 2	# ivtmp$97, ivtmp$97,
	mull	a8, a8, a8	# tmp144, _7, _7
	ssr	a7	# yshift
	sra	a8, a8	# tmp145, tmp144
# @OPUS@\upstream\celt\pitch.c:69:       Syy = ADD32(Syy, SHR32(MULT16_16(y[j],y[j]), yshift));
	add.n	a5, a5, a8	# Syy, Syy, tmp145
# @OPUS@\upstream\celt\pitch.c:68:    for (j=0;j<len;j++)
	bne	a10, a9, .L3	# _234, ivtmp$97,
	j	.L2		#
.L11:
# @OPUS@\upstream\celt\pitch.c:53:    opus_val32 Syy=1;
	mov.n	a5, a8	# Syy, tmp140
.L2:
# @OPUS@\upstream\celt\pitch.c:70:    for (i=0;i<max_pitch;i++)
	l32i.n	a8, sp, 0	# %sfp,
	blti	a8, 1, .L1	#,,
	slli	a8, a4, 1	# tmp146, len,
	neg	a4, a8	#, tmp149
	s32i.n	a4, sp, 4	# %sfp,
# @OPUS@\upstream\celt\pitch.c:76:          xcorr16 = EXTRACT16(VSHR32(xcorr[i], xshift));
	movi.n	a4, 0xe	# tmp202,
# @OPUS@\upstream\celt\pitch.c:65:    best_den[1] = 0;
	movi.n	a14, 0	# best_den$1,
# @OPUS@\upstream\celt\pitch.c:63:    best_num[1] = -1;
	movi.n	a15, -1	# best_num$1,
# @OPUS@\upstream\celt\pitch.c:76:          xcorr16 = EXTRACT16(VSHR32(xcorr[i], xshift));
	sub	a4, a4, a6	#, tmp202, _2
	add.n	a3, a3, a8	# ivtmp$91, y, tmp146
# @OPUS@\upstream\celt\pitch.c:64:    best_den[0] = 0;
	s32i.n	a14, sp, 16	# %sfp, best_den$1
# @OPUS@\upstream\celt\pitch.c:70:    for (i=0;i<max_pitch;i++)
	mov.n	a10, a14	# i, best_den$1
# @OPUS@\upstream\celt\pitch.c:62:    best_num[0] = -1;
	s32i.n	a15, sp, 12	# %sfp, best_num$1
# @OPUS@\upstream\celt\pitch.c:76:          xcorr16 = EXTRACT16(VSHR32(xcorr[i], xshift));
	s32i.n	a4, sp, 24	# %sfp,
.L10:
# @OPUS@\upstream\celt\pitch.c:72:       if (xcorr[i]>0)
	l32i.n	a4, a2, 0	# MEM[base: _247, offset: 0B], _14
# @OPUS@\upstream\celt\pitch.c:72:       if (xcorr[i]>0)
	blti	a4, 1, .L5	# _14,,
# @OPUS@\upstream\celt\pitch.c:76:          xcorr16 = EXTRACT16(VSHR32(xcorr[i], xshift));
	l32i.n	a9, sp, 8	# %sfp,
	blti	a9, 1, .L6	#,,
# @OPUS@\upstream\celt\pitch.c:76:          xcorr16 = EXTRACT16(VSHR32(xcorr[i], xshift));
	ssr	a9	#
	sra	a4, a4	# tmp151, _14
	slli	a4, a4, 16	# tmp152, tmp151,
	srai	a4, a4, 16	# iftmp$51_87, tmp152,
	j	.L7		#
.L6:
# @OPUS@\upstream\celt\pitch.c:76:          xcorr16 = EXTRACT16(VSHR32(xcorr[i], xshift));
	l32i.n	a6, sp, 24	# %sfp,
	ssl	a6	#
	sll	a4, a4	# tmp155, _14
	slli	a4, a4, 16	# tmp156, tmp155,
	srai	a4, a4, 16	# iftmp$51_87, tmp156,
.L7:
# @OPUS@\upstream\celt\pitch.c:82:          num = MULT16_16_Q15(xcorr16,xcorr16);
	mull	a4, a4, a4	# tmp157, iftmp$51_87, iftmp$51_87
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	srai	a11, a5, 16	# _37, Syy,
# @OPUS@\upstream\celt\pitch.c:82:          num = MULT16_16_Q15(xcorr16,xcorr16);
	slli	a4, a4, 1	# tmp159, tmp157,
	srai	a4, a4, 16	# num, tmp159,
	extui	a12, a5, 0, 16	# _119, Syy,
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	srai	a6, a14, 16	# tmp160, best_den$1,
	extui	a8, a14, 0, 16	# tmp163, best_den$1,
	mull	a6, a6, a4	# tmp161, tmp160, num
	mull	a8, a8, a4	# tmp164, tmp163, num
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	mull	a9, a15, a11	# tmp167, best_num$1, _37
	mull	a13, a15, a12	# tmp169, best_num$1, _119
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	slli	a6, a6, 1	# tmp162, tmp161,
	srai	a8, a8, 15	# tmp165, tmp164,
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	slli	a9, a9, 1	# tmp168, tmp167,
	srai	a13, a13, 15	# tmp170, tmp169,
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	add.n	a8, a6, a8	# tmp166, tmp162, tmp165
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	add.n	a9, a9, a13	# tmp171, tmp168, tmp170
# @OPUS@\upstream\celt\pitch.c:83:          if (MULT16_32_Q15(num,best_den[1]) > MULT16_32_Q15(best_num[1],Syy))
	bge	a9, a8, .L5	# tmp171, tmp166,
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	l32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	l32i.n	a9, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	srai	a6, a8, 16	# tmp172,,
	extui	a8, a8, 0, 16	# tmp175,,
	mull	a6, a6, a4	# tmp173, tmp172, num
	mull	a8, a8, a4	# tmp176, tmp175, num
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	mull	a11, a11, a9	# tmp179, _37,
	mull	a12, a9, a12	# tmp181,, _119
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	slli	a6, a6, 1	# tmp174, tmp173,
	srai	a8, a8, 15	# tmp177, tmp176,
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	slli	a11, a11, 1	# tmp180, tmp179,
	srai	a12, a12, 15	# tmp182, tmp181,
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	add.n	a6, a6, a8	# tmp178, tmp174, tmp177
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	add.n	a11, a11, a12	# tmp183, tmp180, tmp182
# @OPUS@\upstream\celt\pitch.c:85:             if (MULT16_32_Q15(num,best_den[0]) > MULT16_32_Q15(best_num[0],Syy))
	bge	a11, a6, .L8	# tmp183, tmp178,
# @OPUS@\upstream\celt\pitch.c:89:                best_pitch[1] = best_pitch[0];
	l32i.n	a8, sp, 20	# %sfp,
	l32i.n	a14, sp, 16	# %sfp, best_den$1
	l32i.n	a6, a8, 0	# *best_pitch_95(D), *best_pitch_95(D)
	mov.n	a15, a9	# best_num$1,
	s32i.n	a6, a8, 4	# MEM[(int *)best_pitch_95(D) + 4B], *best_pitch_95(D)
# @OPUS@\upstream\celt\pitch.c:92:                best_pitch[0] = i;
	s32i.n	a10, a8, 0	# *best_pitch_95(D), i
	s32i.n	a5, sp, 16	# %sfp, Syy
# @OPUS@\upstream\celt\pitch.c:90:                best_num[0] = num;
	s32i.n	a4, sp, 12	# %sfp, num
	j	.L5		#
.L8:
# @OPUS@\upstream\celt\pitch.c:96:                best_pitch[1] = i;
	l32i.n	a9, sp, 20	# %sfp,
	mov.n	a14, a5	# best_den$1, Syy
	s32i.n	a10, a9, 4	# MEM[(int *)best_pitch_95(D) + 4B], i
# @OPUS@\upstream\celt\pitch.c:94:                best_num[1] = num;
	mov.n	a15, a4	# best_num$1, num
.L5:
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	l16si	a4, a3, 0	# MEM[base: _248, offset: 0B], _72
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	add.n	a6, a3, a8	# tmp187, ivtmp$91,
	l16si	a6, a6, 0	# MEM[base: _252, offset: 0B], _78
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	mull	a4, a4, a4	# tmp190, _72, _72
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	mull	a6, a6, a6	# tmp192, _78, _78
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	ssr	a7	# yshift
	sra	a4, a4	# tmp191, tmp190
	add.n	a5, a4, a5	# _4, tmp191, Syy
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	ssr	a7	# yshift
	sra	a6, a6	# tmp193, tmp192
# @OPUS@\upstream\celt\pitch.c:100:       Syy += SHR32(MULT16_16(y[i+len],y[i+len]),yshift) - SHR32(MULT16_16(y[i],y[i]),yshift);
	sub	a5, a5, a6	# Syy, _4, tmp193
# @OPUS@\upstream\celt\pitch.c:101:       Syy = MAX32(1, Syy);
	bgei	a5, 1, .L9	# Syy,,
	movi.n	a5, 1	# Syy,
.L9:
# @OPUS@\upstream\celt\pitch.c:70:    for (i=0;i<max_pitch;i++)
	l32i.n	a9, sp, 0	# %sfp,
# @OPUS@\upstream\celt\pitch.c:70:    for (i=0;i<max_pitch;i++)
	addi.n	a10, a10, 1	# i, i,
	addi.n	a2, a2, 4	# ivtmp$90, ivtmp$90,
	addi.n	a3, a3, 2	# ivtmp$91, ivtmp$91,
# @OPUS@\upstream\celt\pitch.c:70:    for (i=0;i<max_pitch;i++)
	bne	a9, a10, .L10	#, i,
.L1:
# @OPUS@\upstream\celt\pitch.c:103: }
	l32i.n	a12, sp, 44	#,
	l32i.n	a13, sp, 40	#,
	l32i.n	a14, sp, 36	#,
	l32i.n	a15, sp, 32	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	find_best_pitch, .-find_best_pitch
	.section	.text.compute_pitch_gain$part$0,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, 32766
	.align	4
	.type	compute_pitch_gain$part$0, @function
# Function: compute_pitch_gain$part$0
# Module: upstream/celt/pitch.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
compute_pitch_gain$part$0:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a8, 0x1f	# tmp91,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a5, a4	# _10, yy
	nsau	a6, a3	# _3, xx
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	sub	a6, a8, a6	# tmp93, tmp91, _3
	sub	a8, a8, a5	# tmp97, tmp91, _10
# @OPUS@\upstream\celt\pitch.c:430:    sx = celt_ilog2(xx)-14;
	slli	a6, a6, 16	# tmp94, tmp93,
# @OPUS@\upstream\celt\pitch.c:431:    sy = celt_ilog2(yy)-14;
	slli	a8, a8, 16	# tmp98, tmp97,
# @OPUS@\upstream\celt\pitch.c:422: static opus_val16 compute_pitch_gain(opus_val32 xy, opus_val32 xx, opus_val32 yy)
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\pitch.c:430:    sx = celt_ilog2(xx)-14;
	srai	a6, a6, 16	# _6, tmp94,
# @OPUS@\upstream\celt\pitch.c:431:    sy = celt_ilog2(yy)-14;
	srai	a8, a8, 16	# _13, tmp98,
# @OPUS@\upstream\celt\pitch.c:422: static opus_val16 compute_pitch_gain(opus_val32 xy, opus_val32 xx, opus_val32 yy)
	s32i.n	a12, sp, 8	#,
	s32i.n	a13, sp, 4	#,
# @OPUS@\upstream\celt\pitch.c:430:    sx = celt_ilog2(xx)-14;
	addi	a5, a6, -14	# sx, _6,
# @OPUS@\upstream\celt\pitch.c:431:    sy = celt_ilog2(yy)-14;
	addi	a7, a8, -14	# sy, _13,
# @OPUS@\upstream\celt\pitch.c:422: static opus_val16 compute_pitch_gain(opus_val32 xy, opus_val32 xx, opus_val32 yy)
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\pitch.c:422: static opus_val16 compute_pitch_gain(opus_val32 xy, opus_val32 xx, opus_val32 yy)
	mov.n	a13, a2	# xy, xy
# @OPUS@\upstream\celt\pitch.c:432:    shift = sx + sy;
	add.n	a12, a5, a7	# shift, sx, sy
# @OPUS@\upstream\celt\pitch.c:433:    x2y2 = SHR32(MULT16_16(VSHR32(xx, sx), VSHR32(yy, sy)), 14);
	blti	a5, 1, .L16	# sx,,
	ssr	a5	# sx
	sra	a5, a3	# tmp99, xx
	slli	a5, a5, 16	# tmp100, tmp99,
	srai	a5, a5, 16	# iftmp$77_18, tmp100,
	j	.L17		#
.L16:
	movi.n	a5, 0xe	# tmp101,
	sub	a5, a5, a6	# tmp102, tmp101, _6
	ssl	a5	# tmp102
	sll	a5, a3	# tmp103, xx
	slli	a5, a5, 16	# tmp104, tmp103,
	srai	a5, a5, 16	# iftmp$77_18, tmp104,
.L17:
	blti	a7, 1, .L18	# sy,,
	ssr	a7	# sy
	sra	a7, a4	# tmp105, yy
	slli	a7, a7, 16	# tmp106, tmp105,
	srai	a7, a7, 16	# iftmp$79_25, tmp106,
	j	.L19		#
.L18:
	movi.n	a7, 0xe	# tmp107,
	sub	a7, a7, a8	# tmp108, tmp107, _13
	ssl	a7	# tmp108
	sll	a7, a4	# tmp109, yy
	slli	a7, a7, 16	# tmp110, tmp109,
	srai	a7, a7, 16	# iftmp$79_25, tmp110,
.L19:
	mull	a5, a5, a7	# _32, iftmp$77_18, iftmp$79_25
# @OPUS@\upstream\celt\pitch.c:433:    x2y2 = SHR32(MULT16_16(VSHR32(xx, sx), VSHR32(yy, sy)), 14);
	srai	a2, a5, 14	# x2y2, _32,
# @OPUS@\upstream\celt\pitch.c:434:    if (shift & 1) {
	bbci	a12, 0, .L20	# shift,,
# @OPUS@\upstream\celt\pitch.c:435:       if (x2y2 < 32768)
	l32r	a3, .LC0	#, tmp112
	blt	a3, a2, .L21	# tmp112, x2y2,
# @OPUS@\upstream\celt\pitch.c:437:          x2y2 <<= 1;
	slli	a2, a2, 1	# x2y2, x2y2,
# @OPUS@\upstream\celt\pitch.c:438:          shift--;
	addi.n	a12, a12, -1	# shift, shift,
	j	.L20		#
.L21:
# @OPUS@\upstream\celt\pitch.c:440:          x2y2 >>= 1;
	srai	a2, a5, 15	# x2y2, _32,
# @OPUS@\upstream\celt\pitch.c:441:          shift++;
	addi.n	a12, a12, 1	# shift, shift,
.L20:
# @OPUS@\upstream\celt\pitch.c:444:    den = celt_rsqrt_norm(x2y2);
	call0	celt_rsqrt_norm		#
# @OPUS@\upstream\celt\pitch.c:445:    g = MULT16_32_Q15(den, xy);
	extui	a4, a13, 0, 16	# tmp117, xy,
	srai	a3, a13, 16	# tmp114, xy,
	mull	a3, a3, a2	# tmp115, tmp114, tmp113
	mull	a2, a4, a2	# tmp118, tmp117, tmp113
# @OPUS@\upstream\celt\pitch.c:446:    g = VSHR32(g, (shift>>1)-1);
	srai	a12, a12, 1	# _55, shift,
# @OPUS@\upstream\celt\pitch.c:445:    g = MULT16_32_Q15(den, xy);
	slli	a3, a3, 1	# tmp116, tmp115,
	srai	a2, a2, 15	# tmp119, tmp118,
# @OPUS@\upstream\celt\pitch.c:446:    g = VSHR32(g, (shift>>1)-1);
	addi.n	a4, a12, -1	# _56, _55,
# @OPUS@\upstream\celt\pitch.c:445:    g = MULT16_32_Q15(den, xy);
	add.n	a2, a3, a2	# g, tmp116, tmp119
# @OPUS@\upstream\celt\pitch.c:446:    g = VSHR32(g, (shift>>1)-1);
	blti	a4, 1, .L22	# _56,,
	ssr	a4	# _56
	sra	a2, a2	# iftmp$81_62, g
	j	.L23		#
.L22:
	movi.n	a3, 1	# tmp120,
	sub	a12, a3, a12	# tmp121, tmp120, _55
	ssl	a12	# tmp121
	sll	a2, a2	# iftmp$81_62, g
.L23:
# @OPUS@\upstream\celt\pitch.c:447:    return EXTRACT16(MIN32(g, Q15ONE));
	l32r	a3, .LC1	#, tmp122
	bge	a3, a2, .L24	# tmp122, iftmp$81_62,
	l32r	a2, .LC0	#, iftmp$81_62
.L24:
# @OPUS@\upstream\celt\pitch.c:448: }
	l32i.n	a0, sp, 12	#,
	slli	a2, a2, 16	# tmp125, iftmp$81_62,
	srai	a2, a2, 16	#, tmp125,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	compute_pitch_gain$part$0, .-compute_pitch_gain$part$0
	.section	.text.pitch_downsample,"ax",@progbits
	.literal_position
	.literal .LC2, 29490
	.literal .LC3, 26540
	.literal .LC4, 23885
	.literal .LC5, 21496
	.literal .LC6, 3277
	.literal .LC7, 26214
	.align	4
	.global	pitch_downsample
	.type	pitch_downsample, @function
# Function: pitch_downsample
# Module: upstream/celt/pitch.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context:
# C context: void pitch_downsample(celt_sig * OPUS_RESTRICT x[], opus_val16 * OPUS_RESTRICT x_lp,
# C context: int len, int C, int arch)
# C context: {
# C context: int i;
# C context: opus_val32 ac[5];
pitch_downsample:
	addi	sp, sp, -96	#,,
	s32i	a14, sp, 80	#,
	s32i	a0, sp, 92	#,
	s32i	a12, sp, 88	#,
	s32i	a13, sp, 84	#,
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\celt\pitch.c:142: {
	s32i.n	a6, sp, 52	# %sfp, arch
	mov.n	a8, a3	# x_lp, x_lp
# @OPUS@\upstream\celt\pitch.c:151:    opus_val32 maxabs = celt_maxabs32(x[0], len);
	l32i.n	a14, a2, 0	# *x_139(D), _1
# @OPUS@\upstream\celt\mathops.h:101:    for (i=0;i<len;i++)
	blti	a4, 1, .L29	# len,,
	slli	a12, a4, 2	# _372, len,
# @OPUS@\upstream\celt\mathops.h:100:    opus_val32 minval = 0;
	movi.n	a7, 0	# minval,
	mov.n	a3, a14	# ivtmp$124, _1
	add.n	a11, a12, a14	# _370, _372, _1
# @OPUS@\upstream\celt\mathops.h:99:    opus_val32 maxval = 0;
	mov.n	a9, a7	# maxval, minval
.L32:
# @OPUS@\upstream\celt\mathops.h:103:       maxval = MAX32(maxval, x[i]);
	l32i.n	a6, a3, 0	# MEM[base: _374, offset: 0B], _175
	addi.n	a3, a3, 4	# ivtmp$124, ivtmp$124,
# @OPUS@\upstream\celt\mathops.h:103:       maxval = MAX32(maxval, x[i]);
	bge	a9, a6, .L30	# maxval, _175,
	mov.n	a9, a6	# maxval, _175
.L30:
# @OPUS@\upstream\celt\mathops.h:104:       minval = MIN32(minval, x[i]);
	bge	a6, a7, .L31	# _175, minval,
	mov.n	a7, a6	# minval, _175
.L31:
# @OPUS@\upstream\celt\mathops.h:101:    for (i=0;i<len;i++)
	bne	a11, a3, .L32	# _370, ivtmp$124,
	j	.L66		#
.L36:
# @OPUS@\upstream\celt\mathops.h:103:       maxval = MAX32(maxval, x[i]);
	l32i.n	a6, a3, 0	# MEM[base: _382, offset: 0B], _189
	addi.n	a3, a3, 4	# ivtmp$121, ivtmp$121,
# @OPUS@\upstream\celt\mathops.h:103:       maxval = MAX32(maxval, x[i]);
	bge	a11, a6, .L34	# maxval, _189,
	mov.n	a11, a6	# maxval, _189
.L34:
# @OPUS@\upstream\celt\mathops.h:104:       minval = MIN32(minval, x[i]);
	bge	a6, a9, .L35	# _189, minval,
	mov.n	a9, a6	# minval, _189
.L35:
# @OPUS@\upstream\celt\mathops.h:101:    for (i=0;i<len;i++)
	bne	a12, a3, .L36	# _378, ivtmp$121,
	neg	a9, a9	# tmp260, minval
	bge	a11, a7, .L37	# maxval, _205,
	mov.n	a11, a7	# maxval, _205
.L37:
	bge	a9, a11, .L38	# _580, maxval,
	mov.n	a9, a11	# _580, maxval
.L38:
# @OPUS@\upstream\celt\pitch.c:157:    if (maxabs<1)
	bnez.n	a9, .L67	# _580,
	j	.L58		#
.L69:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a7, a7	# _199, _205
# @OPUS@\upstream\celt\pitch.c:159:    shift = celt_ilog2(maxabs)-10;
	movi.n	a6, 0x15	# tmp265,
# @OPUS@\upstream\celt\pitch.c:159:    shift = celt_ilog2(maxabs)-10;
	sub	a6, a6, a7	# _202, tmp265, _199
	movi.n	a3, 0	# tmp267,
	movltz	a6, a3, a6	# _202, tmp267, _202
	addi.n	a9, a6, 1	# prephitmp_461, _202,
	addi.n	a6, a6, 2	# _457, _202,
	j	.L41		#
.L58:
# @OPUS@\upstream\celt\pitch.c:157:    if (maxabs<1)
	mov.n	a9, a5	# prephitmp_461, C
	movi.n	a6, 3	# _457,
	j	.L41		#
.L60:
	movi.n	a9, 1	# prephitmp_461,
	movi.n	a6, 2	# _457,
.L41:
	l32i.n	a13, a14, 0	# *_1, *_1
	l32i.n	a3, a14, 4	# MEM[(celt_sig *)_1 + 4B], MEM[(celt_sig *)_1 + 4B]
	ssr	a9	# prephitmp_461
	sra	a13, a13	# tmp268, *_1
	ssr	a6	# _457
	sra	a3, a3	# tmp270, MEM[(celt_sig *)_1 + 4B]
	add.n	a13, a13, a3	# tmp274, tmp268, tmp270
	slli	a13, a13, 16	# tmp275, tmp274,
# @OPUS@\upstream\celt\pitch.c:164:    for (i=1;i<len>>1;i++)
	srai	a15, a4, 1	# _154, len,
	srai	a13, a13, 16	# pretmp_555, tmp275,
# @OPUS@\upstream\celt\pitch.c:164:    for (i=1;i<len>>1;i++)
	blti	a15, 2, .L42	# _154,,
	slli	a10, a15, 3	# _389, _154,
	addi.n	a11, a8, 2	# ivtmp$104, x_lp,
	add.n	a12, a14, a10	# tmp276, _1, _389
	addi.n	a4, a14, 4	# ivtmp$113, _1,
	addi	a12, a12, -4	# _386, tmp276,
	mov.n	a7, a11	# ivtmp$115, ivtmp$104
	s32i.n	a8, sp, 48	# %sfp, x_lp
.L43:
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	l32i.n	a14, a4, 0	# MEM[base: _394, offset: 0B], MEM[base: _394, offset: 0B]
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	l32i.n	a3, a4, 8	# MEM[base: _394, offset: 8B], MEM[base: _394, offset: 8B]
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	l32i.n	a8, a4, 4	# MEM[base: _394, offset: 4B],
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	ssr	a6	# _457
	sra	a14, a14	# tmp277, MEM[base: _394, offset: 0B]
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	ssr	a6	# _457
	sra	a3, a3	# tmp279, MEM[base: _394, offset: 8B]
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	add.n	a3, a14, a3	# tmp283, tmp277, tmp279
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	ssr	a9	# prephitmp_461
	sra	a14, a8	# tmp284,
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	add.n	a3, a3, a14	# tmp288, tmp283, tmp284
# @OPUS@\upstream\celt\pitch.c:165:       x_lp[i] = SHR32(x[0][(2*i-1)], shift+2) + SHR32(x[0][(2*i+1)], shift+2) + SHR32(x[0][2*i], shift+1);
	s16i	a3, a7, 0	# MEM[base: _391, offset: 0B], tmp288
	addi.n	a4, a4, 8	# ivtmp$113, ivtmp$113,
	addi.n	a7, a7, 2	# ivtmp$115, ivtmp$115,
# @OPUS@\upstream\celt\pitch.c:164:    for (i=1;i<len>>1;i++)
	bne	a12, a4, .L43	# _386, ivtmp$113,
	j	.L71		#
.L49:
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	l32i.n	a3, a2, 4	# MEM[(celt_sig * restrict *)x_139(D) + 4B], _41
	add.n	a5, a3, a10	# tmp289, _41, _389
	addi.n	a4, a3, 4	# ivtmp$106, _41,
	addi	a5, a5, -4	# _488, tmp289,
.L45:
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	l32i.n	a2, a4, 0	# MEM[base: _420, offset: 0B], MEM[base: _420, offset: 0B]
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	l32i.n	a10, a4, 8	# MEM[base: _420, offset: 8B], MEM[base: _420, offset: 8B]
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	l16ui	a12, a11, 0	# MEM[base: _287, offset: 0B],
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	l32i.n	a7, a4, 4	# MEM[base: _420, offset: 4B], MEM[base: _420, offset: 4B]
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	ssr	a6	# _457
	sra	a2, a2	# tmp290, MEM[base: _420, offset: 0B]
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	ssr	a6	# _457
	sra	a10, a10	# tmp292, MEM[base: _420, offset: 8B]
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	add.n	a2, a2, a10	# tmp296, tmp290, tmp292
	add.n	a2, a2, a12	# tmp299, tmp296, MEM[base: _287, offset: 0B]
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	ssr	a9	# prephitmp_461
	sra	a7, a7	# tmp300, MEM[base: _420, offset: 4B]
# @OPUS@\upstream\celt\pitch.c:170:          x_lp[i] += SHR32(x[1][(2*i-1)], shift+2) + SHR32(x[1][(2*i+1)], shift+2) + SHR32(x[1][2*i], shift+1);
	add.n	a2, a2, a7	# tmp304, tmp299, tmp300
	s16i	a2, a11, 0	# MEM[base: _287, offset: 0B], tmp304
	addi.n	a4, a4, 8	# ivtmp$106, ivtmp$106,
	addi.n	a11, a11, 2	# ivtmp$104, ivtmp$104,
# @OPUS@\upstream\celt\pitch.c:169:       for (i=1;i<len>>1;i++)
	bne	a5, a4, .L45	# _488, ivtmp$106,
	l16si	a13, a8, 0	# *x_lp_149(D), pretmp_555
.L52:
# @OPUS@\upstream\celt\pitch.c:171:       x_lp[0] += SHR32(x[1][1], shift+2) + SHR32(x[1][0], shift+1);
	l32i.n	a2, a3, 4	# MEM[(celt_sig *)prephitmp_558 + 4B], MEM[(celt_sig *)prephitmp_558 + 4B]
# @OPUS@\upstream\celt\pitch.c:171:       x_lp[0] += SHR32(x[1][1], shift+2) + SHR32(x[1][0], shift+1);
	l32i.n	a3, a3, 0	# *prephitmp_558, *prephitmp_558
# @OPUS@\upstream\celt\pitch.c:171:       x_lp[0] += SHR32(x[1][1], shift+2) + SHR32(x[1][0], shift+1);
	ssr	a6	# _457
	sra	a6, a2	# tmp307, MEM[(celt_sig *)prephitmp_558 + 4B]
# @OPUS@\upstream\celt\pitch.c:171:       x_lp[0] += SHR32(x[1][1], shift+2) + SHR32(x[1][0], shift+1);
	ssr	a9	# prephitmp_461
	sra	a9, a3	# tmp309, *prephitmp_558
# @OPUS@\upstream\celt\pitch.c:171:       x_lp[0] += SHR32(x[1][1], shift+2) + SHR32(x[1][0], shift+1);
	add.n	a6, a6, a9	# tmp313, tmp307, tmp309
# @OPUS@\upstream\celt\pitch.c:171:       x_lp[0] += SHR32(x[1][1], shift+2) + SHR32(x[1][0], shift+1);
	add.n	a13, a13, a6	# tmp315, pretmp_555, tmp313
	s16i	a13, a8, 0	# *x_lp_149(D), tmp315
.L50:
# @OPUS@\upstream\celt\pitch.c:184:    _celt_autocorr(x_lp, ac, NULL, 0,
	l32i.n	a9, sp, 52	# %sfp,
	movi.n	a5, 0	#,
	mov.n	a4, a5	#,
	mov.n	a2, a8	#, x_lp
	mov.n	a7, a15	#, _154
	movi.n	a6, 4	#,
	addi	a3, sp, 16	#,,
	s32i.n	a9, sp, 0	#,
	s32i.n	a8, sp, 56	#,
	call0	_celt_autocorr		#
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	l32i.n	a12, sp, 28	# ac, _419
	l32i.n	a13, sp, 24	# ac, _448
	l32i.n	a11, sp, 32	# ac, _74
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	extui	a4, a12, 0, 16	# tmp334, _419,
	srai	a7, a13, 16	#, _448,
	slli	a2, a4, 3	# tmp336, tmp334,
	s32i.n	a7, sp, 48	# %sfp,
	extui	a9, a11, 10, 6	#, _74,,
	add.n	a2, a2, a4	# tmp337, tmp336, tmp334
	extui	a4, a13, 12, 4	# tmp328, _448,,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	l32i.n	a14, sp, 20	# ac, _486
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	srai	a3, a12, 16	# tmp341, _419,
	s32i.n	a9, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	sub	a4, a13, a4	# tmp329, _448, tmp328
# @OPUS@\upstream\celt\pitch.c:189:    ac[0] += SHR32(ac[0],13);
	l32i.n	a9, sp, 16	# ac,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	l32i.n	a13, sp, 48	# %sfp,
	srli	a2, a2, 14	# tmp339, tmp337,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	sub	a2, a12, a2	# tmp340, _419, tmp339
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	slli	a6, a3, 3	# tmp343, tmp341,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	l32i.n	a12, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	extui	a10, a14, 14, 2	# tmp320, _486,,
	srai	a5, a14, 16	# tmp322, _486,
	add.n	a6, a6, a3	# tmp344, tmp343, tmp341
# @OPUS@\upstream\celt\pitch.c:189:    ac[0] += SHR32(ac[0],13);
	srai	a7, a9, 13	# tmp316,,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	srai	a3, a11, 16	# tmp352, _74,
	slli	a9, a13, 4	# tmp332,,
# @OPUS@\upstream\celt\pitch.c:189:    ac[0] += SHR32(ac[0],13);
	l32i.n	a13, sp, 16	# ac,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	slli	a5, a5, 2	# tmp324, tmp322,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	sub	a10, a14, a10	# tmp321, _486, tmp320
	sub	a11, a11, a12	# tmp351, _74,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	slli	a3, a3, 6	# tmp354, tmp352,
	slli	a6, a6, 2	# tmp346, tmp344,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	sub	a6, a2, a6	# tmp347, tmp340, tmp346
	sub	a11, a11, a3	# tmp355, tmp351, tmp354
# @OPUS@\upstream\celt\pitch.c:189:    ac[0] += SHR32(ac[0],13);
	add.n	a7, a7, a13	# tmp317, tmp316,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	sub	a10, a10, a5	# tmp325, tmp321, tmp324
	sub	a9, a4, a9	# tmp333, tmp329, tmp332
# @OPUS@\upstream\celt\pitch.c:204:    _celt_lpc(lpc, ac, 4);
	addi	a3, sp, 16	#,,
	movi.n	a4, 4	#,
	addi	a2, sp, 36	#,,
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	s32i.n	a6, sp, 28	# ac, tmp347
	s32i.n	a11, sp, 32	# ac, tmp355
# @OPUS@\upstream\celt\pitch.c:189:    ac[0] += SHR32(ac[0],13);
	s32i.n	a7, sp, 16	# ac, tmp317
# @OPUS@\upstream\celt\pitch.c:198:       ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	s32i.n	a10, sp, 20	# ac, tmp325
	s32i.n	a9, sp, 24	# ac, tmp333
# @OPUS@\upstream\celt\pitch.c:204:    _celt_lpc(lpc, ac, 4);
	call0	_celt_lpc		#
# @OPUS@\upstream\celt\pitch.c:208:       lpc[i] = MULT16_16_Q15(lpc[i], tmp);
	l32r	a5, .LC2	#, tmp359
	l32r	a4, .LC3	#, tmp363
	l32r	a3, .LC4	#, tmp367
	l16ui	a2, sp, 36	# lpc,
	l16ui	a11, sp, 38	# lpc,
	l16ui	a12, sp, 40	# lpc,
	mul16s	a2, a2, a5	# tmp357, lpc, tmp359
	mul16s	a11, a11, a4	# tmp361, lpc, tmp363
	mul16s	a12, a12, a3	# tmp365, lpc, tmp367
	l32r	a4, .LC5	#, tmp371
# @OPUS@\upstream\celt\pitch.c:212:    lpc2[1] = lpc[1] + MULT16_16_Q15(c1,lpc[0]);
	l32r	a3, .LC7	#, tmp377
# @OPUS@\upstream\celt\pitch.c:208:       lpc[i] = MULT16_16_Q15(lpc[i], tmp);
	l16ui	a13, sp, 42	# lpc,
	srai	a2, a2, 15	# _571, tmp357,
	srai	a11, a11, 15	# _527, tmp361,
	srai	a12, a12, 15	# _494, tmp365,
# @OPUS@\upstream\celt\pitch.c:211:    lpc2[0] = lpc[0] + QCONST16(.8f,SIG_SHIFT);
	l32r	a6, .LC6	#, tmp374
# @OPUS@\upstream\celt\pitch.c:208:       lpc[i] = MULT16_16_Q15(lpc[i], tmp);
	mul16s	a13, a13, a4	# tmp369, lpc, tmp371
# @OPUS@\upstream\celt\pitch.c:212:    lpc2[1] = lpc[1] + MULT16_16_Q15(c1,lpc[0]);
	mull	a5, a2, a3	# tmp376, _571, tmp377
# @OPUS@\upstream\celt\pitch.c:213:    lpc2[2] = lpc[2] + MULT16_16_Q15(c1,lpc[1]);
	mull	a4, a11, a3	# tmp382, _527, tmp377
# @OPUS@\upstream\celt\pitch.c:214:    lpc2[3] = lpc[3] + MULT16_16_Q15(c1,lpc[2]);
	mull	a14, a12, a3	# tmp388, _494, tmp377
# @OPUS@\upstream\celt\pitch.c:211:    lpc2[0] = lpc[0] + QCONST16(.8f,SIG_SHIFT);
	add.n	a2, a2, a6	# tmp373, _571, tmp374
# @OPUS@\upstream\celt\pitch.c:208:       lpc[i] = MULT16_16_Q15(lpc[i], tmp);
	srai	a13, a13, 15	# _97, tmp369,
# @OPUS@\upstream\celt\pitch.c:212:    lpc2[1] = lpc[1] + MULT16_16_Q15(c1,lpc[0]);
	srai	a5, a5, 15	# tmp378, tmp376,
# @OPUS@\upstream\celt\pitch.c:213:    lpc2[2] = lpc[2] + MULT16_16_Q15(c1,lpc[1]);
	srai	a4, a4, 15	# tmp384, tmp382,
# @OPUS@\upstream\celt\pitch.c:214:    lpc2[3] = lpc[3] + MULT16_16_Q15(c1,lpc[2]);
	srai	a14, a14, 15	# tmp390, tmp388,
# @OPUS@\upstream\celt\pitch.c:211:    lpc2[0] = lpc[0] + QCONST16(.8f,SIG_SHIFT);
	slli	a2, a2, 16	# tmp375, tmp373,
# @OPUS@\upstream\celt\pitch.c:214:    lpc2[3] = lpc[3] + MULT16_16_Q15(c1,lpc[2]);
	add.n	a14, a13, a14	# tmp392, _97, tmp390
# @OPUS@\upstream\celt\pitch.c:212:    lpc2[1] = lpc[1] + MULT16_16_Q15(c1,lpc[0]);
	add.n	a11, a11, a5	# tmp380, _527, tmp378
# @OPUS@\upstream\celt\pitch.c:213:    lpc2[2] = lpc[2] + MULT16_16_Q15(c1,lpc[1]);
	add.n	a12, a12, a4	# tmp386, _494, tmp384
# @OPUS@\upstream\celt\pitch.c:215:    lpc2[4] = MULT16_16_Q15(c1,lpc[3]);
	mull	a13, a13, a3	# tmp394, _97, tmp377
# @OPUS@\upstream\celt\pitch.c:211:    lpc2[0] = lpc[0] + QCONST16(.8f,SIG_SHIFT);
	srai	a2, a2, 16	#, tmp375,
# @OPUS@\upstream\celt\pitch.c:212:    lpc2[1] = lpc[1] + MULT16_16_Q15(c1,lpc[0]);
	slli	a11, a11, 16	# tmp381, tmp380,
# @OPUS@\upstream\celt\pitch.c:213:    lpc2[2] = lpc[2] + MULT16_16_Q15(c1,lpc[1]);
	slli	a12, a12, 16	# tmp387, tmp386,
# @OPUS@\upstream\celt\pitch.c:214:    lpc2[3] = lpc[3] + MULT16_16_Q15(c1,lpc[2]);
	slli	a14, a14, 16	# tmp393, tmp392,
# @OPUS@\upstream\celt\pitch.c:211:    lpc2[0] = lpc[0] + QCONST16(.8f,SIG_SHIFT);
	s32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:212:    lpc2[1] = lpc[1] + MULT16_16_Q15(c1,lpc[0]);
	srai	a11, a11, 16	# _106, tmp381,
# @OPUS@\upstream\celt\pitch.c:213:    lpc2[2] = lpc[2] + MULT16_16_Q15(c1,lpc[1]);
	srai	a12, a12, 16	# _112, tmp387,
# @OPUS@\upstream\celt\pitch.c:214:    lpc2[3] = lpc[3] + MULT16_16_Q15(c1,lpc[2]);
	srai	a14, a14, 16	# _118, tmp393,
# @OPUS@\upstream\celt\pitch.c:215:    lpc2[4] = MULT16_16_Q15(c1,lpc[3]);
	srai	a13, a13, 15	# _121, tmp394,
# @OPUS@\upstream\celt\pitch.c:122:    for (i=0;i<N;i++)
	l32i.n	a8, sp, 56	#,
	blti	a15, 1, .L28	# _154,,
	slli	a15, a15, 1	# tmp396, _154,
# @OPUS@\upstream\celt\pitch.c:121:    mem4=0;
	movi.n	a5, 0	# mem4,
	add.n	a2, a8, a15	#, ivtmp$100, tmp396
	mov.n	a3, a8	# ivtmp$100, x_lp
	s32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.c:120:    mem3=0;
	mov.n	a6, a5	# mem3, mem4
# @OPUS@\upstream\celt\pitch.c:119:    mem2=0;
	mov.n	a10, a5	# mem2, mem4
# @OPUS@\upstream\celt\pitch.c:118:    mem1=0;
	mov.n	a9, a5	# mem1, mem4
# @OPUS@\upstream\celt\pitch.c:117:    mem0=0;
	mov.n	a8, a5	# mem0, mem4
	j	.L47		#
.L59:
# @OPUS@\upstream\celt\pitch.c:122:    for (i=0;i<N;i++)
	mov.n	a6, a10	# mem3, mem2
	mov.n	a10, a9	# mem2, mem1
	mov.n	a9, a8	# mem1, mem0
# @OPUS@\upstream\celt\pitch.c:134:       mem0 = x[i];
	mov.n	a8, a7	# mem0, _212
.L47:
# @OPUS@\upstream\celt\pitch.c:125:       sum = MAC16_16(sum,num0,mem0);
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:129:       sum = MAC16_16(sum,num4,mem4);
	mull	a7, a13, a5	# tmp399, _121, mem4
# @OPUS@\upstream\celt\pitch.c:125:       sum = MAC16_16(sum,num0,mem0);
	mull	a4, a8, a2	# tmp401, mem0,
# @OPUS@\upstream\celt\pitch.c:135:       x[i] = ROUND16(sum, SIG_SHIFT);
	addmi	a7, a7, 0x800	# tmp400, tmp399,
# @OPUS@\upstream\celt\pitch.c:126:       sum = MAC16_16(sum,num1,mem1);
	mull	a2, a9, a11	# tmp403, mem1, _106
# @OPUS@\upstream\celt\pitch.c:127:       sum = MAC16_16(sum,num2,mem2);
	mull	a5, a10, a12	# tmp405, mem2, _112
# @OPUS@\upstream\celt\pitch.c:135:       x[i] = ROUND16(sum, SIG_SHIFT);
	add.n	a4, a7, a4	# tmp402, tmp400, tmp401
# @OPUS@\upstream\celt\pitch.c:128:       sum = MAC16_16(sum,num3,mem3);
	mull	a15, a6, a14	# tmp407, mem3, _118
# @OPUS@\upstream\celt\pitch.c:124:       opus_val32 sum = SHL32(EXTEND32(x[i]), SIG_SHIFT);
	l16si	a7, a3, 0	# MEM[base: _285, offset: 0B], _212
# @OPUS@\upstream\celt\pitch.c:135:       x[i] = ROUND16(sum, SIG_SHIFT);
	add.n	a2, a4, a2	# tmp404, tmp402, tmp403
	add.n	a2, a2, a5	# tmp406, tmp404, tmp405
	add.n	a15, a2, a15	# tmp408, tmp406, tmp407
# @OPUS@\upstream\celt\pitch.c:124:       opus_val32 sum = SHL32(EXTEND32(x[i]), SIG_SHIFT);
	slli	a2, a7, 12	# sum, _212,
# @OPUS@\upstream\celt\pitch.c:135:       x[i] = ROUND16(sum, SIG_SHIFT);
	add.n	a15, a15, a2	# tmp410, tmp408, sum
	srai	a15, a15, 12	# tmp411, tmp410,
# @OPUS@\upstream\celt\pitch.c:122:    for (i=0;i<N;i++)
	l32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.c:135:       x[i] = ROUND16(sum, SIG_SHIFT);
	s16i	a15, a3, 0	# MEM[base: _285, offset: 0B], tmp411
	addi.n	a3, a3, 2	# ivtmp$100, ivtmp$100,
	mov.n	a5, a6	# mem4, mem3
# @OPUS@\upstream\celt\pitch.c:122:    for (i=0;i<N;i++)
	bne	a3, a2, .L59	# ivtmp$100,,
	j	.L28		#
.L71:
	l32i.n	a8, sp, 48	# %sfp, x_lp
# @OPUS@\upstream\celt\pitch.c:166:    x_lp[0] = SHR32(x[0][1], shift+2) + SHR32(x[0][0], shift+1);
	s16i	a13, a8, 0	# *x_lp_149(D), pretmp_555
# @OPUS@\upstream\celt\pitch.c:167:    if (C==2)
	bnei	a5, 2, .L50	# C,,
	j	.L49		#
.L42:
# @OPUS@\upstream\celt\pitch.c:166:    x_lp[0] = SHR32(x[0][1], shift+2) + SHR32(x[0][0], shift+1);
	s16i	a13, a8, 0	# *x_lp_149(D), pretmp_555
# @OPUS@\upstream\celt\pitch.c:167:    if (C==2)
	bnei	a5, 2, .L50	# C,,
.L54:
	l32i.n	a3, a2, 4	# MEM[(celt_sig * restrict *)x_139(D) + 4B], _41
	j	.L52		#
.L70:
# @OPUS@\upstream\celt\pitch.c:157:    if (maxabs<1)
	bnez.n	a7, .L69	# _205,
	j	.L60		#
.L29:
# @OPUS@\upstream\celt\pitch.c:152:    if (C==2)
	movi.n	a6, 2	# _457,
	movi.n	a9, 1	# prephitmp_461,
	bne	a5, a6, .L41	# C,,
	l32i.n	a13, a14, 0	# *_1, *_1
	l32i.n	a3, a14, 4	# MEM[(celt_sig *)_1 + 4B], MEM[(celt_sig *)_1 + 4B]
	ssr	a6	#
	sra	a13, a13	# tmp412, *_1
	srai	a3, a3, 3	# tmp414, MEM[(celt_sig *)_1 + 4B],
	add.n	a13, a13, a3	# tmp418, tmp412, tmp414
	slli	a13, a13, 16	# tmp419, tmp418,
# @OPUS@\upstream\celt\pitch.c:164:    for (i=1;i<len>>1;i++)
	mov.n	a9, a6	# prephitmp_461, _457
	srai	a15, a4, 1	# _154, len,
	srai	a13, a13, 16	# pretmp_555, tmp419,
	movi.n	a6, 3	# _457,
	j	.L54		#
.L56:
	l32i.n	a3, a2, 4	# MEM[(celt_sig * restrict *)x_139(D) + 4B], ivtmp$121
# @OPUS@\upstream\celt\mathops.h:100:    opus_val32 minval = 0;
	movi.n	a9, 0	# minval,
	add.n	a12, a12, a3	# _378, _372, ivtmp$121
# @OPUS@\upstream\celt\mathops.h:99:    opus_val32 maxval = 0;
	mov.n	a11, a9	# maxval, minval
	j	.L36		#
.L66:
# @OPUS@\upstream\celt\mathops.h:106:    return MAX32(maxval, -minval);
	neg	a7, a7	# _205, minval
	bge	a7, a9, .L55	# _205, maxval,
	mov.n	a7, a9	# _205, maxval
.L55:
# @OPUS@\upstream\celt\pitch.c:152:    if (C==2)
	bnei	a5, 2, .L70	# C,,
	j	.L56		#
.L67:
# @OPUS@\upstream\celt\pitch.c:159:    shift = celt_ilog2(maxabs)-10;
	movi.n	a3, 0x15	# tmp424,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a9, a9	# _13, _580
# @OPUS@\upstream\celt\pitch.c:159:    shift = celt_ilog2(maxabs)-10;
	sub	a9, a3, a9	# _37, tmp424, _13
	movi.n	a3, 0	# tmp426,
	movltz	a9, a3, a9	# _37, tmp426, _37
	addi.n	a6, a9, 3	# _457, _37,
	addi.n	a9, a9, 2	# prephitmp_461, _37,
	j	.L41		#
.L28:
# @OPUS@\upstream\celt\pitch.c:217: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	pitch_downsample, .-pitch_downsample
	.section	.text.celt_pitch_xcorr_c,"ax",@progbits
	.literal_position
	.align	4
	.global	celt_pitch_xcorr_c
	.type	celt_pitch_xcorr_c, @function
# Function: celt_pitch_xcorr_c
# Module: upstream/celt/pitch.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #else
# C context: void
# C context: #endif
# C context: celt_pitch_xcorr_c(const opus_val16 *_x, const opus_val16 *_y,
# C context: opus_val32 *xcorr, int len, int max_pitch, int arch)
# C context: {
# C context:
# C context: #if 0 /* This is a simple version of the pitch correlation that should work
celt_pitch_xcorr_c:
	addi	sp, sp, -112	#,,
	s32i	a6, sp, 68	# %sfp, max_pitch
	s32i	a12, sp, 108	#,
	s32i	a13, sp, 104	#,
	s32i	a14, sp, 100	#,
	s32i	a15, sp, 96	#,
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	addi	a6, a6, -3	# tmp173, max_pitch,
# @OPUS@\upstream\celt\pitch.c:227: {
	s32i.n	a2, sp, 60	# %sfp, _x
	s32i	a3, sp, 80	# %sfp, _y
	s32i	a4, sp, 72	# %sfp, xcorr
	s32i.n	a5, sp, 56	# %sfp, len
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	blti	a6, 1, .L89	# tmp173,,
	l32i	a6, sp, 68	# %sfp,
# @OPUS@\upstream\celt\pitch.c:258:    opus_val32 maxcorr=1;
	movi.n	a8, 1	#,
	addi	a2, a6, -4	# tmp174,,
	srli	a2, a2, 2	#, tmp174,
	s32i	a2, sp, 76	# %sfp,
	l32i	a7, sp, 76	# %sfp,
	addi	a2, a4, 16	# tmp175, xcorr,
	slli	a3, a7, 4	# tmp176,,
	l32i	a6, sp, 80	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi	a10, a5, -3	#, len,
	add.n	a3, a2, a3	#, tmp175, tmp176
# @OPUS@\upstream\celt\pitch.c:258:    opus_val32 maxcorr=1;
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i.n	a10, sp, 52	# %sfp,
	s32i.n	a6, sp, 44	# %sfp,
	s32i.n	a4, sp, 32	# %sfp, xcorr
	s32i	a3, sp, 64	# %sfp,
.L83:
	l32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i.n	a10, sp, 52	# %sfp,
	addi.n	a8, a7, 6	# ivtmp$146,,
# @OPUS@\upstream\celt\pitch.h:71:    y_0=*y++;
	l16si	a9, a7, 0	# MEM[base: _337, offset: 0B], y_0
# @OPUS@\upstream\celt\pitch.h:72:    y_1=*y++;
	l16si	a15, a7, 2	# MEM[base: _337, offset: 2B], y_1
	mov.n	a6, a8	# y, ivtmp$146
# @OPUS@\upstream\celt\pitch.h:73:    y_2=*y++;
	l16si	a14, a7, 4	# MEM[base: _337, offset: 4B], y_2
# @OPUS@\upstream\celt\pitch.c:264:       opus_val32 sum[4]={0,0,0,0};
	movi.n	a12, 0	# sum$3,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blti	a10, 1, .L90	#,,
# @OPUS@\upstream\celt\pitch.c:264:       opus_val32 sum[4]={0,0,0,0};
	s32i.n	a12, sp, 12	# %sfp, sum$3
	s32i.n	a12, sp, 8	# %sfp, sum$3
	s32i.n	a12, sp, 16	# %sfp, sum$3
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i.n	a12, sp, 24	# %sfp, sum$3
	s32i.n	a12, sp, 28	# %sfp, sum$3
	l32i.n	a3, sp, 60	# %sfp, ivtmp$145
	mov.n	a12, a15	# y_1, y_1
	mov.n	a15, a9	# y_0, y_0
	j	.L75		#
.L91:
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i.n	a5, sp, 24	# %sfp, j
.L75:
# @OPUS@\upstream\celt\pitch.h:77:       tmp = *x++;
	l16si	a6, a3, 0	# MEM[base: _351, offset: 0B], tmp
# @OPUS@\upstream\celt\pitch.h:83:       tmp=*x++;
	l16si	a2, a3, 2	# MEM[base: _351, offset: 2B], tmp
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a13, a8, 0	# MEM[base: _347, offset: 0B], prephitmp_409
# @OPUS@\upstream\celt\pitch.h:89:       tmp=*x++;
	l16si	a5, a3, 4	# MEM[base: _351, offset: 4B], tmp
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	mull	a4, a6, a15	#, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	mull	a10, a12, a2	#, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:84:       y_0=*y++;
	l16si	a15, a8, 2	# MEM[base: _347, offset: 2B], y_0
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i	a10, sp, 84	# %sfp,
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a7, a15, a5	#, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a10, a13, a5	#, prephitmp_409, tmp
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a12, a6, a12	#, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	s32i.n	a7, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i	a10, sp, 88	# %sfp,
	l32i	a7, sp, 84	# %sfp,
	l32i.n	a10, sp, 0	# %sfp,
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i.n	a12, sp, 4	# %sfp,
	add.n	a7, a7, a10	#,,
# @OPUS@\upstream\celt\pitch.h:95:       tmp=*x++;
	l16si	a4, a3, 6	# MEM[base: _351, offset: 6B], tmp
	s32i.n	a3, sp, 20	# %sfp, ivtmp$145
# @OPUS@\upstream\celt\pitch.h:86:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a9, a14, a2	# tmp193, y_2, tmp
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a3, a14, a5	#, y_2, tmp
	s32i	a7, sp, 84	# %sfp,
	l32i.n	a7, sp, 4	# %sfp,
# @OPUS@\upstream\celt\pitch.h:81:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a11, a6, a14	# tmp199, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a6, a6, a13	# tmp215, tmp, prephitmp_409
# @OPUS@\upstream\celt\pitch.h:87:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a13, a2	# tmp200, prephitmp_409, tmp
	add.n	a9, a7, a9	# _16,, tmp193
# @OPUS@\upstream\celt\pitch.h:88:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a15	# tmp216, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	mull	a7, a15, a4	#, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:90:       y_1=*y++;
	l16si	a12, a8, 4	# MEM[base: _347, offset: 4B], y_1
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	mull	a10, a13, a4	#, prephitmp_409, tmp
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	s32i.n	a7, sp, 4	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a6, a2	# tmp217, tmp215, tmp216
	l32i	a7, sp, 84	# %sfp,
	l32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:96:       y_2=*y++;
	l16si	a14, a8, 6	# MEM[base: _347, offset: 6B], y_2
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a10, sp, 0	# %sfp,
# @OPUS@\upstream\celt\pitch.h:94:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mull	a5, a5, a12	# tmp218, tmp, y_1
	add.n	a10, a6, a7	# _3,,
	l32i.n	a6, sp, 40	# %sfp,
	add.n	a3, a11, a3	# tmp201, tmp199, tmp200
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	mull	a11, a12, a4	# tmp213, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	mull	a4, a4, a14	# tmp220, tmp, y_2
	add.n	a3, a3, a6	# _7, tmp201,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i	a7, sp, 88	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a6, sp, 0	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a2, a5	# tmp219, tmp217, tmp218
	l32i.n	a5, sp, 20	# %sfp,
	add.n	a2, a2, a4	# tmp221, tmp219, tmp220
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a4, sp, 16	# %sfp,
	add.n	a10, a6, a10	# tmp208,, _3
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a9, a7, a9	# tmp210,, _16
	addi.n	a7, a5, 8	# x,,
	l32i.n	a5, sp, 4	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	add.n	a4, a4, a10	#,, tmp208
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i.n	a10, sp, 8	# %sfp,
	add.n	a9, a9, a5	# tmp212, tmp210,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a4, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a10, a10, a9	#,, tmp212
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	s32i.n	a10, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	l32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	l32i.n	a10, sp, 28	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	add.n	a11, a11, a3	# tmp214, tmp213, _7
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a10, a10, a2	#,, tmp221
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	add.n	a4, a4, a11	#,, tmp214
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i.n	a2, sp, 52	# %sfp,
	addi.n	a8, a8, 8	# ivtmp$146, ivtmp$146,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi.n	a5, a6, 4	# j,,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	s32i.n	a4, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	s32i.n	a10, sp, 28	# %sfp,
	mov.n	a3, a7	# ivtmp$145, x
	mov.n	a6, a8	# y, ivtmp$146
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blt	a5, a2, .L91	# j,,
	l32i.n	a3, sp, 24	# %sfp,
	mov.n	a9, a15	# y_0, y_0
	addi.n	a11, a3, 5	# _405,,
	mov.n	a15, a12	# y_1, y_1
	mov.n	a12, a10	# sum$3,
	addi.n	a10, a3, 6	# _407,,
	j	.L74		#
.L90:
	l32i.n	a7, sp, 60	# %sfp, x
	mov.n	a13, a12	# prephitmp_409, sum$3
	movi.n	a10, 2	# _407,
	movi.n	a11, 1	# _405,
# @OPUS@\upstream\celt\pitch.c:264:       opus_val32 sum[4]={0,0,0,0};
	s32i.n	a12, sp, 12	# %sfp, sum$3
	s32i.n	a12, sp, 8	# %sfp, sum$3
	s32i.n	a12, sp, 16	# %sfp, sum$3
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	mov.n	a5, a12	# j, prephitmp_409
.L74:
# @OPUS@\upstream\celt\pitch.h:102:    if (j++<len)
	l32i.n	a4, sp, 56	# %sfp,
	bge	a5, a4, .L76	# j,,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	l16si	a2, a7, 0	# *x_259, tmp
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	l32i.n	a6, sp, 16	# %sfp,
	mull	a5, a2, a9	# tmp226, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a13, a8, 0	# *y_261, prephitmp_409
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	add.n	a6, a6, a5	#,, tmp226
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a4, a2, a15	# tmp227, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a3, a2, a14	# tmp228, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	l32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	l32i.n	a6, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a2, a2, a13	# tmp229, tmp, prephitmp_409
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	add.n	a6, a6, a3	#,, tmp228
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	add.n	a5, a5, a4	#,, tmp227
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	s32i.n	a6, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	add.n	a12, a12, a2	# sum$3, sum$3, tmp229
# @OPUS@\upstream\celt\pitch.h:105:       y_3=*y++;
	addi.n	a6, a8, 2	# y, ivtmp$146,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	addi.n	a7, a7, 2	# x, x,
.L76:
# @OPUS@\upstream\celt\pitch.h:111:    if (j++<len)
	l32i.n	a8, sp, 56	# %sfp,
	bge	a11, a8, .L77	# _405,,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_168, tmp
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	l32i.n	a8, sp, 16	# %sfp,
	mull	a5, a2, a15	# tmp234, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	l16si	a9, a6, 0	# *y_171, y_0
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	add.n	a8, a8, a5	#,, tmp234
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a4, a2, a14	# tmp235, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a2, a13	# tmp236, tmp, prephitmp_409
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	l32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	l32i.n	a8, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a9	# tmp237, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	add.n	a5, a5, a4	#,, tmp235
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	add.n	a8, a8, a3	#,, tmp236
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	s32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	s32i.n	a8, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	add.n	a12, a12, a2	# sum$3, sum$3, tmp237
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	addi.n	a6, a6, 2	# y, y,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	addi.n	a7, a7, 2	# x, x,
.L77:
# @OPUS@\upstream\celt\pitch.h:120:    if (j<len)
	l32i.n	a2, sp, 56	# %sfp,
	bge	a10, a2, .L78	# _407,,
# @OPUS@\upstream\celt\pitch.h:122:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_192, tmp
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	l16ui	a3, a6, 0	# *y_194,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a4, a2, a14	# tmp240, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a5, a2, a13	# tmp241, tmp, prephitmp_409
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a6, a2, a9	# tmp242, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mul16s	a2, a3, a2	# tmp243, *y_194, tmp
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	l32i.n	a3, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	add.n	a12, a12, a2	# sum$3, sum$3, tmp243
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	add.n	a3, a3, a4	#,, tmp240
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	l32i.n	a4, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i.n	a3, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	add.n	a4, a4, a5	#,, tmp241
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	l32i.n	a5, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i.n	a4, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	add.n	a5, a5, a6	#,, tmp242
	s32i.n	a5, sp, 12	# %sfp,
.L78:
# @OPUS@\upstream\celt\pitch.c:275:       xcorr[i]=sum[0];
	l32i.n	a6, sp, 32	# %sfp,
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\pitch.c:276:       xcorr[i+1]=sum[1];
	l32i.n	a8, sp, 8	# %sfp,
# @OPUS@\upstream\celt\pitch.c:277:       xcorr[i+2]=sum[2];
	l32i.n	a10, sp, 12	# %sfp,
# @OPUS@\upstream\celt\pitch.c:275:       xcorr[i]=sum[0];
	s32i.n	a7, a6, 0	# MEM[base: _334, offset: 0B],
# @OPUS@\upstream\celt\pitch.c:276:       xcorr[i+1]=sum[1];
	s32i.n	a8, a6, 4	# MEM[base: _334, offset: 4B],
# @OPUS@\upstream\celt\pitch.c:277:       xcorr[i+2]=sum[2];
	s32i.n	a10, a6, 8	# MEM[base: _334, offset: 8B],
# @OPUS@\upstream\celt\pitch.c:278:       xcorr[i+3]=sum[3];
	s32i.n	a12, a6, 12	# MEM[base: _334, offset: 12B], sum$3
	mov.n	a2, a7	# sum$0,
	bge	a7, a12, .L79	# sum$0, sum$3,
	mov.n	a2, a12	# sum$0, sum$3
.L79:
	l32i.n	a3, sp, 48	# %sfp,
	bge	a2, a3, .L80	# sum$0,,
	mov.n	a2, a3	# sum$0,
.L80:
	l32i.n	a4, sp, 8	# %sfp,
	bge	a2, a4, .L81	# _272,,
	mov.n	a2, a4	# _272,
.L81:
# @OPUS@\upstream\celt\pitch.c:283:       maxcorr = MAX32(maxcorr, sum[0]);
	l32i.n	a5, sp, 12	# %sfp,
	s32i.n	a5, sp, 48	# %sfp,
	bge	a5, a2, .L82	#, _272,
	s32i.n	a2, sp, 48	# %sfp, _272
.L82:
	l32i.n	a6, sp, 32	# %sfp,
	l32i.n	a7, sp, 44	# %sfp,
	addi	a6, a6, 16	#,,
	addi.n	a7, a7, 8	#,,
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	l32i	a8, sp, 64	# %sfp,
	s32i.n	a6, sp, 32	# %sfp,
	s32i.n	a7, sp, 44	# %sfp,
	bne	a8, a6, .L83	#,,
	l32i	a10, sp, 76	# %sfp,
	addi.n	a9, a10, 1	# tmp247,,
	slli	a9, a9, 2	# i, tmp247,
	j	.L73		#
.L89:
# @OPUS@\upstream\celt\pitch.c:258:    opus_val32 maxcorr=1;
	movi.n	a2, 1	#,
	s32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	movi.n	a9, 0	# i,
.L73:
# @OPUS@\upstream\celt\pitch.c:287:    for (;i<max_pitch;i++)
	l32i	a6, sp, 68	# %sfp,
	bge	a9, a6, .L72	# i,,
	l32i.n	a2, sp, 56	# %sfp,
	slli	a10, a6, 2	# tmp250,,
	slli	a7, a2, 1	# tmp251,,
	l32i	a3, sp, 72	# %sfp,
	l32i.n	a2, sp, 60	# %sfp,
	l32i	a6, sp, 80	# %sfp,
	slli	a8, a9, 2	# tmp248, i,
	l32i.n	a11, sp, 48	# %sfp, <retval>
	slli	a9, a9, 1	# tmp249, i,
	l32i.n	a12, sp, 56	# %sfp, len
	add.n	a8, a3, a8	# ivtmp$137,, tmp248
	add.n	a9, a6, a9	# ivtmp$138,, tmp249
	add.n	a10, a3, a10	# _363,, tmp250
	add.n	a7, a2, a7	# _392,, tmp251
	mov.n	a13, a2	# _x,
.L88:
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	blti	a12, 1, .L92	# len,,
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	mov.n	a4, a9	# ivtmp$132, ivtmp$138
	mov.n	a2, a13	# ivtmp$131, _x
# @OPUS@\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a5, 0	# xy,
.L86:
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	l16ui	a3, a2, 0	# MEM[base: _401, offset: 0B],
	l16ui	a6, a4, 0	# MEM[base: _396, offset: 0B],
	addi.n	a2, a2, 2	# ivtmp$131, ivtmp$131,
	mul16s	a3, a3, a6	# tmp252, MEM[base: _401, offset: 0B], MEM[base: _396, offset: 0B]
	addi.n	a4, a4, 2	# ivtmp$132, ivtmp$132,
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a5, a5, a3	# xy, xy, tmp252
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	bne	a7, a2, .L86	# _392, ivtmp$131,
	j	.L85		#
.L92:
# @OPUS@\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a5, 0	# xy,
.L85:
# @OPUS@\upstream\celt\pitch.c:291:       xcorr[i] = sum;
	s32i.n	a5, a8, 0	# MEM[base: _367, offset: 0B], xy
# @OPUS@\upstream\celt\pitch.c:293:       maxcorr = MAX32(maxcorr, sum);
	bge	a11, a5, .L87	# <retval>, xy,
	mov.n	a11, a5	# <retval>, xy
.L87:
	addi.n	a8, a8, 4	# ivtmp$137, ivtmp$137,
	addi.n	a9, a9, 2	# ivtmp$138, ivtmp$138,
# @OPUS@\upstream\celt\pitch.c:287:    for (;i<max_pitch;i++)
	bne	a10, a8, .L88	# _363, ivtmp$137,
	s32i.n	a11, sp, 48	# %sfp, <retval>
.L72:
# @OPUS@\upstream\celt\pitch.c:300: }
	l32i.n	a2, sp, 48	# %sfp,
	l32i	a12, sp, 108	#,
	l32i	a13, sp, 104	#,
	l32i	a14, sp, 100	#,
	l32i	a15, sp, 96	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	celt_pitch_xcorr_c, .-celt_pitch_xcorr_c
	.section	.text.pitch_search,"ax",@progbits
	.literal_position
	.literal .LC9, 22938
	.align	4
	.global	pitch_search
	.type	pitch_search, @function
# Function: pitch_search
# Module: upstream/celt/pitch.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: }
# C context:
# C context: void pitch_search(const opus_val16 * OPUS_RESTRICT x_lp, opus_val16 * OPUS_RESTRICT y,
# C context: int len, int max_pitch, int *pitch, int arch)
# C context: {
# C context: int i, j;
# C context: int lag;
pitch_search:
	movi	a9, 0xc0	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\celt\pitch.c:324:    ALLOC(x_lp4, len>>2, opus_val16);
	srai	a8, a4, 2	#, len,
# @OPUS@\upstream\celt\pitch.c:304: {
	s32i	a13, sp, 180	#,
# @OPUS@\upstream\celt\pitch.c:307:    int best_pitch[2]={0,0};
	movi.n	a13, 0	# tmp326,
# @OPUS@\upstream\celt\pitch.c:324:    ALLOC(x_lp4, len>>2, opus_val16);
	s32i	a8, sp, 88	# %sfp,
# @OPUS@\upstream\celt\pitch.c:304: {
	s32i	a0, sp, 188	#,
	s32i	a6, sp, 140	# %sfp, pitch
	s32i	a12, sp, 184	#,
	s32i	a14, sp, 176	#,
	mov.n	a12, a5	# max_pitch, max_pitch
	s32i	a4, sp, 124	# %sfp, len
	s32i	a15, sp, 172	#,
# @OPUS@\upstream\celt\pitch.c:304: {
	s32i	a2, sp, 120	# %sfp, x_lp
	s32i	a3, sp, 108	# %sfp, y
# @OPUS@\upstream\celt\pitch.c:307:    int best_pitch[2]={0,0};
	s32i.n	a13, sp, 24	# best_pitch, tmp326
	s32i.n	a13, sp, 28	# best_pitch, tmp326
# @OPUS@\upstream\celt\pitch.c:318:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\pitch.c:322:    lag = len+max_pitch;
	l32i	a9, sp, 124	# %sfp,
# @OPUS@\upstream\celt\pitch.c:318:    SAVE_STACK;
	s32i.n	a2, sp, 16	# _saved_stack,
# @OPUS@\upstream\celt\pitch.c:324:    ALLOC(x_lp4, len>>2, opus_val16);
	l32i	a2, sp, 88	# %sfp,
# @OPUS@\upstream\celt\pitch.c:322:    lag = len+max_pitch;
	add.n	a14, a9, a12	# lag,, max_pitch
# @OPUS@\upstream\celt\pitch.c:318:    SAVE_STACK;
	s32i.n	a3, sp, 20	# _saved_stack,
# @OPUS@\upstream\celt\pitch.c:324:    ALLOC(x_lp4, len>>2, opus_val16);
	mov.n	a4, a13	#, tmp326
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\pitch.c:325:    ALLOC(y_lp4, lag>>2, opus_val16);
	srai	a14, a14, 2	# _3, lag,
# @OPUS@\upstream\celt\pitch.c:324:    ALLOC(x_lp4, len>>2, opus_val16);
	s32i	a2, sp, 92	# %sfp,
# @OPUS@\upstream\celt\pitch.c:325:    ALLOC(y_lp4, lag>>2, opus_val16);
	mov.n	a4, a13	#, tmp326
	movi.n	a3, 2	#,
	mov.n	a2, a14	#, _3
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\pitch.c:326:    ALLOC(xcorr, max_pitch>>1, opus_val32);
	srai	a11, a12, 1	#, max_pitch,
# @OPUS@\upstream\celt\pitch.c:325:    ALLOC(y_lp4, lag>>2, opus_val16);
	s32i	a2, sp, 104	# %sfp,
# @OPUS@\upstream\celt\pitch.c:326:    ALLOC(xcorr, max_pitch>>1, opus_val32);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	mov.n	a2, a11	#,
	s32i	a11, sp, 116	# %sfp,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\pitch.c:329:    for (j=0;j<len>>2;j++)
	l32i	a8, sp, 88	# %sfp,
# @OPUS@\upstream\celt\pitch.c:326:    ALLOC(xcorr, max_pitch>>1, opus_val32);
	s32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\celt\pitch.c:329:    for (j=0;j<len>>2;j++)
	blti	a8, 1, .L97	#,,
	l32i	a2, sp, 120	# %sfp, ivtmp$214
	slli	a5, a8, 2	# tmp329,,
	l32i	a3, sp, 92	# %sfp, ivtmp$215
	add.n	a5, a5, a2	# _703, tmp329, ivtmp$214
.L98:
# @OPUS@\upstream\celt\pitch.c:330:       x_lp4[j] = x_lp[2*j];
	l16si	a4, a2, 0	# MEM[base: _708, offset: 0B], _13
	addi.n	a2, a2, 4	# ivtmp$214, ivtmp$214,
# @OPUS@\upstream\celt\pitch.c:330:       x_lp4[j] = x_lp[2*j];
	s16i	a4, a3, 0	# MEM[base: _707, offset: 0B], _13
	addi.n	a3, a3, 2	# ivtmp$215, ivtmp$215,
# @OPUS@\upstream\celt\pitch.c:329:    for (j=0;j<len>>2;j++)
	bne	a5, a2, .L98	# _703, ivtmp$214,
	j	.L172		#
.L147:
	l32i	a4, sp, 108	# %sfp, ivtmp$210
	l32i	a3, sp, 104	# %sfp, ivtmp$211
# @OPUS@\upstream\celt\pitch.c:331:    for (j=0;j<lag>>2;j++)
	movi.n	a2, 0	# j,
.L100:
# @OPUS@\upstream\celt\pitch.c:332:       y_lp4[j] = y[2*j];
	l16si	a5, a4, 0	# MEM[base: _716, offset: 0B], _21
# @OPUS@\upstream\celt\pitch.c:331:    for (j=0;j<lag>>2;j++)
	addi.n	a2, a2, 1	# j, j,
# @OPUS@\upstream\celt\pitch.c:332:       y_lp4[j] = y[2*j];
	s16i	a5, a3, 0	# MEM[base: _715, offset: 0B], _21
	addi.n	a4, a4, 4	# ivtmp$210, ivtmp$210,
	addi.n	a3, a3, 2	# ivtmp$211, ivtmp$211,
# @OPUS@\upstream\celt\pitch.c:331:    for (j=0;j<lag>>2;j++)
	blt	a2, a14, .L100	# j, _3,
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	l32i	a9, sp, 88	# %sfp,
	blti	a9, 1, .L149	#,,
.L148:
# @OPUS@\upstream\celt\pitch.c:331:    for (j=0;j<lag>>2;j++)
	movi.n	a2, 0	# minval,
	l32i	a7, sp, 92	# %sfp, ivtmp$207
	l32i	a9, sp, 88	# %sfp, _1
	mov.n	a4, a2	# maxval, minval
	mov.n	a6, a2	# i, minval
.L104:
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	l16si	a3, a7, 0	# MEM[base: _723, offset: 0B], _205
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	slli	a8, a3, 16	# tmp540, _205,
	mov.n	a5, a3	# _205, _205
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	srai	a8, a8, 16	# tmp345, tmp540,
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	bge	a3, a4, .L102	# _205, maxval,
	mov.n	a5, a4	# _205, maxval
.L102:
	slli	a5, a5, 16	# tmp342, _205,
	srai	a4, a5, 16	# maxval, tmp342,
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	bge	a2, a8, .L103	# minval, tmp345,
	mov.n	a3, a2	# _205, minval
.L103:
	slli	a3, a3, 16	# tmp349, _205,
	srai	a2, a3, 16	# minval, tmp349,
	addi.n	a7, a7, 2	# ivtmp$207, ivtmp$207,
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	blt	a6, a9, .L104	# i, _1,
	neg	a2, a2	# tmp350, minval
	bgei	a4, 1, .L105	# maxval,,
	movi.n	a4, 1	# maxval,
.L105:
	bge	a2, a4, .L106	# prephitmp_202, maxval,
	mov.n	a2, a4	# prephitmp_202, maxval
.L106:
	bgei	a14, 1, .L101	# _3,,
	j	.L150		#
.L149:
	movi.n	a2, 1	# prephitmp_202,
.L101:
	l32i	a6, sp, 104	# %sfp, ivtmp$204
	slli	a8, a14, 1	# tmp354, _3,
# @OPUS@\upstream\celt\mathops.h:84:    opus_val16 minval = 0;
	movi.n	a4, 0	# minval,
	add.n	a8, a8, a6	# _727, tmp354, ivtmp$204
# @OPUS@\upstream\celt\mathops.h:83:    opus_val16 maxval = 0;
	mov.n	a5, a4	# maxval, minval
.L110:
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	l16si	a3, a6, 0	# MEM[base: _731, offset: 0B], _191
	addi.n	a6, a6, 2	# ivtmp$204, ivtmp$204,
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	slli	a9, a3, 16	# tmp539, _191,
	mov.n	a7, a3	# _191, _191
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	srai	a9, a9, 16	# tmp366, tmp539,
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	bge	a3, a5, .L108	# _191, maxval,
	mov.n	a7, a5	# _191, maxval
.L108:
	slli	a7, a7, 16	# tmp363, _191,
	srai	a5, a7, 16	# maxval, tmp363,
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	bge	a4, a9, .L109	# minval, tmp366,
	mov.n	a3, a4	# _191, minval
.L109:
	slli	a3, a3, 16	# tmp370, _191,
	srai	a4, a3, 16	# minval, tmp370,
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	bne	a8, a6, .L110	# _727, ivtmp$204,
	neg	a4, a4	# _822, minval
	j	.L107		#
.L150:
	movi.n	a5, 0	# _824,
	mov.n	a4, a5	# _822, _824
.L107:
# @OPUS@\upstream\celt\pitch.c:337:    shift = celt_ilog2(MAX32(1, MAX32(xmax, ymax)))-11;
	bge	a4, a5, .L111	# _822, _824,
	mov.n	a4, a5	# _822, _824
.L111:
	bge	a4, a2, .L112	# _822, prephitmp_202,
	mov.n	a4, a2	# _822, prephitmp_202
.L112:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a4, a4	# _162, _822
# @OPUS@\upstream\celt\pitch.c:337:    shift = celt_ilog2(MAX32(1, MAX32(xmax, ymax)))-11;
	movi.n	a2, 0x14	# tmp376,
# @OPUS@\upstream\celt\pitch.c:337:    shift = celt_ilog2(MAX32(1, MAX32(xmax, ymax)))-11;
	sub	a4, a2, a4	# shift, tmp376, _162
# @OPUS@\upstream\celt\pitch.c:338:    if (shift>0)
	blti	a4, 1, .L151	# shift,,
	l32i	a11, sp, 88	# %sfp,
	l32i	a2, sp, 92	# %sfp, ivtmp$201
	slli	a5, a11, 1	# tmp378,,
	add.n	a5, a5, a2	# _735, tmp378, ivtmp$201
# @OPUS@\upstream\celt\pitch.c:340:       for (j=0;j<len>>2;j++)
	bgei	a11, 1, .L117	#,,
.L118:
	l32i	a2, sp, 104	# %sfp, ivtmp$198
	slli	a5, a14, 1	# tmp383, _3,
	add.n	a5, a5, a2	# _744, tmp383, ivtmp$198
# @OPUS@\upstream\celt\pitch.c:342:       for (j=0;j<lag>>2;j++)
	bgei	a14, 1, .L119	# _3,,
	j	.L116		#
.L117:
# @OPUS@\upstream\celt\pitch.c:341:          x_lp4[j] = SHR16(x_lp4[j], shift);
	l16si	a3, a2, 0	# MEM[base: _740, offset: 0B], tmp379
	ssr	a4	# shift
	sra	a3, a3	# tmp382, tmp379
# @OPUS@\upstream\celt\pitch.c:341:          x_lp4[j] = SHR16(x_lp4[j], shift);
	s16i	a3, a2, 0	# MEM[base: _740, offset: 0B], tmp382
	addi.n	a2, a2, 2	# ivtmp$201, ivtmp$201,
# @OPUS@\upstream\celt\pitch.c:340:       for (j=0;j<len>>2;j++)
	bne	a5, a2, .L117	# _735, ivtmp$201,
	j	.L118		#
.L116:
# @OPUS@\upstream\celt\pitch.c:345:       shift *= 2;
	slli	a4, a4, 1	#, shift,
	addi.n	a13, a4, 1	#,,
	s32i	a4, sp, 132	# %sfp,
	s32i	a13, sp, 136	# %sfp,
	j	.L113		#
.L119:
# @OPUS@\upstream\celt\pitch.c:343:          y_lp4[j] = SHR16(y_lp4[j], shift);
	l16si	a3, a2, 0	# MEM[base: _749, offset: 0B], tmp384
	ssr	a4	# shift
	sra	a3, a3	# tmp387, tmp384
# @OPUS@\upstream\celt\pitch.c:343:          y_lp4[j] = SHR16(y_lp4[j], shift);
	s16i	a3, a2, 0	# MEM[base: _749, offset: 0B], tmp387
	addi.n	a2, a2, 2	# ivtmp$198, ivtmp$198,
# @OPUS@\upstream\celt\pitch.c:342:       for (j=0;j<lag>>2;j++)
	bne	a5, a2, .L119	# _744, ivtmp$198,
	j	.L116		#
.L151:
	movi.n	a8, 1	#,
# @OPUS@\upstream\celt\pitch.c:347:       shift = 0;
	movi.n	a9, 0	#,
	s32i	a8, sp, 136	# %sfp,
	s32i	a9, sp, 132	# %sfp,
.L113:
# @OPUS@\upstream\celt\pitch.c:356:    celt_pitch_xcorr(x_lp4, y_lp4, xcorr, len>>2, max_pitch>>2, arch);
	srai	a12, a12, 2	#, max_pitch,
	s32i	a12, sp, 112	# %sfp,
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	addi	a2, a12, -3	# tmp388,,
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	blti	a2, 1, .L152	# tmp388,,
	addi	a8, a12, -4	# tmp389,,
	srli	a8, a8, 2	# _760, tmp389,
	addi.n	a8, a8, 1	#, _760,
	l32i	a9, sp, 100	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a13, sp, 88	# %sfp,
	slli	a2, a8, 4	# tmp391,,
	s32i	a8, sp, 128	# %sfp,
	l32i	a8, sp, 104	# %sfp,
# @OPUS@\upstream\celt\pitch.c:258:    opus_val32 maxcorr=1;
	movi.n	a11, 1	#,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi	a13, a13, -3	#,,
	add.n	a2, a2, a9	#, tmp391,
# @OPUS@\upstream\celt\pitch.c:258:    opus_val32 maxcorr=1;
	s32i	a11, sp, 84	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i	a13, sp, 76	# %sfp,
	s32i	a8, sp, 80	# %sfp,
	s32i	a9, sp, 72	# %sfp,
	s32i	a2, sp, 96	# %sfp,
.L130:
	l32i	a11, sp, 80	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a2, sp, 76	# %sfp,
	addi.n	a15, a11, 6	# ivtmp$186,,
# @OPUS@\upstream\celt\pitch.h:71:    y_0=*y++;
	l16si	a12, a11, 0	# MEM[base: _769, offset: 0B], y_0
# @OPUS@\upstream\celt\pitch.h:72:    y_1=*y++;
	l16si	a14, a11, 2	# MEM[base: _769, offset: 2B], y_1
	mov.n	a6, a15	# y, ivtmp$186
# @OPUS@\upstream\celt\pitch.h:73:    y_2=*y++;
	l16si	a13, a11, 4	# MEM[base: _769, offset: 4B], y_2
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blti	a2, 1, .L153	#,,
# @OPUS@\upstream\celt\pitch.c:264:       opus_val32 sum[4]={0,0,0,0};
	movi.n	a3, 0	#,
	s32i.n	a3, sp, 32	# %sfp,
	l32i.n	a4, sp, 32	# %sfp,
	l32i	a3, sp, 92	# %sfp, ivtmp$185
	mov.n	a10, a14	# y_1, y_1
	s32i.n	a4, sp, 44	# %sfp,
	s32i.n	a4, sp, 48	# %sfp,
	s32i.n	a4, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i.n	a4, sp, 60	# %sfp,
	mov.n	a14, a12	# y_0, y_0
	mov.n	a11, a3	# ivtmp$185, ivtmp$185
	j	.L122		#
.L154:
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	s32i.n	a5, sp, 60	# %sfp, j
.L122:
# @OPUS@\upstream\celt\pitch.h:77:       tmp = *x++;
	l16si	a6, a11, 0	# MEM[base: _800, offset: 0B], tmp
# @OPUS@\upstream\celt\pitch.h:83:       tmp=*x++;
	l16si	a2, a11, 2	# MEM[base: _800, offset: 2B], tmp
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	mull	a14, a6, a14	#, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a12, a15, 0	# MEM[base: _786, offset: 0B], prephitmp_871
# @OPUS@\upstream\celt\pitch.h:89:       tmp=*x++;
	l16si	a5, a11, 4	# MEM[base: _800, offset: 4B], tmp
# @OPUS@\upstream\celt\pitch.h:79:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a14, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:84:       y_0=*y++;
	l16si	a14, a15, 2	# MEM[base: _786, offset: 2B], y_0
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	mull	a8, a10, a2	#, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a10, a6, a10	#, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:95:       tmp=*x++;
	l16si	a4, a11, 6	# MEM[base: _800, offset: 6B], tmp
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a9, a13, a5	#, y_2, tmp
	s32i.n	a11, sp, 56	# %sfp, ivtmp$185
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a7, a12, a5	#, prephitmp_871, tmp
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a11, a14, a5	#, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:85:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\celt\pitch.h:80:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i	a10, sp, 148	# %sfp,
# @OPUS@\upstream\celt\pitch.h:86:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a8, a13, a2	# tmp408, y_2, tmp
# @OPUS@\upstream\celt\pitch.h:90:       y_1=*y++;
	l16si	a10, a15, 4	# MEM[base: _786, offset: 4B], y_1
# @OPUS@\upstream\celt\pitch.h:91:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i	a9, sp, 64	# %sfp,
# @OPUS@\upstream\celt\pitch.h:93:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	s32i	a11, sp, 68	# %sfp,
# @OPUS@\upstream\celt\pitch.h:92:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i	a7, sp, 152	# %sfp,
	l32i.n	a11, sp, 36	# %sfp,
	l32i	a9, sp, 144	# %sfp,
	l32i	a7, sp, 148	# %sfp,
# @OPUS@\upstream\celt\pitch.h:81:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a13, a6, a13	#, tmp, y_2
	add.n	a9, a9, a11	#,,
# @OPUS@\upstream\celt\pitch.h:87:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a12, a2	# tmp415, prephitmp_871, tmp
# @OPUS@\upstream\celt\pitch.h:82:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a6, a6, a12	# tmp430, tmp, prephitmp_871
	add.n	a8, a7, a8	# _12,, tmp408
# @OPUS@\upstream\celt\pitch.h:88:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a14	# tmp431, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	mull	a7, a10, a4	#, y_1, tmp
# @OPUS@\upstream\celt\pitch.h:81:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	s32i.n	a13, sp, 40	# %sfp,
	s32i	a9, sp, 144	# %sfp,
# @OPUS@\upstream\celt\pitch.h:96:       y_2=*y++;
	l16si	a13, a15, 6	# MEM[base: _786, offset: 6B], y_2
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	mull	a11, a12, a4	#, prephitmp_871, tmp
	l32i.n	a9, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.h:94:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mull	a5, a5, a10	# tmp433, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	s32i.n	a7, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a6, a2	# tmp432, tmp430, tmp431
	l32i	a7, sp, 144	# %sfp,
	l32i	a6, sp, 64	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a11, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	mull	a11, a14, a4	# tmp426, y_0, tmp
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	mull	a4, a4, a13	# tmp435, tmp, y_2
	add.n	a3, a9, a3	# tmp416,, tmp415
	add.n	a2, a2, a5	# tmp434, tmp432, tmp433
	add.n	a9, a6, a7	# _19,,
	l32i	a6, sp, 68	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i	a7, sp, 152	# %sfp,
	l32i.n	a5, sp, 56	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a2, a2, a4	# tmp436, tmp434, tmp435
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i.n	a4, sp, 60	# %sfp,
	add.n	a3, a3, a6	# _8, tmp416,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a8, a7, a8	# tmp425,, _12
	addi.n	a7, a5, 8	# x,,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	addi.n	a5, a4, 4	# j,,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	l32i.n	a4, sp, 52	# %sfp,
	add.n	a9, a6, a9	# tmp423,, _19
	add.n	a4, a4, a9	#,, tmp423
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a8, a8, a11	# tmp427, tmp425, tmp426
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	l32i.n	a11, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.h:97:       sum[0] = MAC16_16(sum[0],tmp,y_3);
	s32i.n	a4, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	l32i.n	a9, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	l32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	add.n	a9, a9, a8	#,, tmp427
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	add.n	a3, a11, a3	# tmp429,, _8
# @OPUS@\upstream\celt\pitch.h:98:       sum[1] = MAC16_16(sum[1],tmp,y_0);
	s32i.n	a9, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	add.n	a4, a4, a3	#,, tmp429
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	add.n	a8, a8, a2	#,, tmp436
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a9, sp, 76	# %sfp,
	addi.n	a15, a15, 8	# ivtmp$186, ivtmp$186,
# @OPUS@\upstream\celt\pitch.h:99:       sum[2] = MAC16_16(sum[2],tmp,y_1);
	s32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:100:       sum[3] = MAC16_16(sum[3],tmp,y_2);
	s32i.n	a8, sp, 32	# %sfp,
	mov.n	a11, a7	# ivtmp$185, x
	mov.n	a6, a15	# y, ivtmp$186
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	blt	a5, a9, .L154	# j,,
	l32i.n	a11, sp, 60	# %sfp,
	mov.n	a9, a12	# prephitmp_871, prephitmp_871
	addi.n	a8, a11, 5	# _867,,
	mov.n	a12, a14	# y_0, y_0
	mov.n	a14, a10	# y_1, y_1
	addi.n	a10, a11, 6	# _869,,
	j	.L121		#
.L153:
# @OPUS@\upstream\celt\pitch.c:264:       opus_val32 sum[4]={0,0,0,0};
	movi.n	a2, 0	#,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	l32i	a7, sp, 92	# %sfp, x
# @OPUS@\upstream\celt\pitch.c:264:       opus_val32 sum[4]={0,0,0,0};
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	mov.n	a9, a2	# prephitmp_871,
	movi.n	a10, 2	# _869,
	movi.n	a8, 1	# _867,
# @OPUS@\upstream\celt\pitch.c:264:       opus_val32 sum[4]={0,0,0,0};
	s32i.n	a2, sp, 44	# %sfp,
	s32i.n	a2, sp, 48	# %sfp,
	s32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:74:    for (j=0;j<len-3;j+=4)
	mov.n	a5, a2	# j, prephitmp_871
.L121:
# @OPUS@\upstream\celt\pitch.h:102:    if (j++<len)
	l32i	a11, sp, 88	# %sfp,
	bge	a5, a11, .L123	# j,,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	l16si	a2, a7, 0	# *x_516, tmp
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	l32i.n	a6, sp, 52	# %sfp,
	mull	a5, a2, a12	# tmp441, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	mull	a4, a2, a14	# tmp442, tmp, y_1
	l32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l16si	a9, a15, 0	# *y_518, prephitmp_871
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	add.n	a6, a6, a5	#,, tmp441
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	mull	a3, a2, a13	# tmp443, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	add.n	a11, a11, a4	#,, tmp442
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	l32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	mull	a2, a2, a9	# tmp444, tmp, prephitmp_871
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	add.n	a4, a4, a3	#,, tmp443
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	add.n	a5, a5, a2	#,, tmp444
# @OPUS@\upstream\celt\pitch.h:106:       sum[0] = MAC16_16(sum[0],tmp,y_0);
	s32i.n	a6, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:107:       sum[1] = MAC16_16(sum[1],tmp,y_1);
	s32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:108:       sum[2] = MAC16_16(sum[2],tmp,y_2);
	s32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:109:       sum[3] = MAC16_16(sum[3],tmp,y_3);
	s32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:105:       y_3=*y++;
	addi.n	a6, a15, 2	# y, ivtmp$186,
# @OPUS@\upstream\celt\pitch.h:104:       opus_val16 tmp = *x++;
	addi.n	a7, a7, 2	# x, x,
.L123:
# @OPUS@\upstream\celt\pitch.h:111:    if (j++<len)
	l32i	a11, sp, 88	# %sfp,
	bge	a8, a11, .L124	# _867,,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_375, tmp
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	l16si	a12, a6, 0	# *y_378, y_0
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	mull	a5, a2, a14	# tmp449, tmp, y_1
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	mull	a4, a2, a13	# tmp450, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	l32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	l32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	mull	a3, a2, a9	# tmp451, tmp, prephitmp_871
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	add.n	a8, a8, a5	#,, tmp449
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	add.n	a11, a11, a4	#,, tmp450
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	l32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	mull	a2, a2, a12	# tmp452, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	add.n	a4, a4, a3	#,, tmp451
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	add.n	a5, a5, a2	#,, tmp452
# @OPUS@\upstream\celt\pitch.h:115:       sum[0] = MAC16_16(sum[0],tmp,y_1);
	s32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:116:       sum[1] = MAC16_16(sum[1],tmp,y_2);
	s32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:117:       sum[2] = MAC16_16(sum[2],tmp,y_3);
	s32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:118:       sum[3] = MAC16_16(sum[3],tmp,y_0);
	s32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:114:       y_0=*y++;
	addi.n	a6, a6, 2	# y, y,
# @OPUS@\upstream\celt\pitch.h:113:       opus_val16 tmp=*x++;
	addi.n	a7, a7, 2	# x, x,
.L124:
# @OPUS@\upstream\celt\pitch.h:120:    if (j<len)
	l32i	a8, sp, 88	# %sfp,
	bge	a10, a8, .L125	# _869,,
# @OPUS@\upstream\celt\pitch.h:122:       opus_val16 tmp=*x++;
	l16si	a2, a7, 0	# *x_399, tmp
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	l16ui	a3, a6, 0	# *y_401,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	mull	a4, a2, a13	# tmp455, tmp, y_2
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	mull	a5, a2, a9	# tmp456, tmp, prephitmp_871
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	mull	a6, a2, a12	# tmp457, tmp, y_0
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	l32i.n	a9, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	mul16s	a2, a3, a2	# tmp458, *y_401, tmp
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	l32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	l32i.n	a13, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	add.n	a9, a9, a4	#,, tmp455
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	add.n	a11, a11, a5	#,, tmp456
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	add.n	a13, a13, a6	#,, tmp457
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	add.n	a3, a3, a2	#,, tmp458
# @OPUS@\upstream\celt\pitch.h:124:       sum[0] = MAC16_16(sum[0],tmp,y_2);
	s32i.n	a9, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:125:       sum[1] = MAC16_16(sum[1],tmp,y_3);
	s32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:126:       sum[2] = MAC16_16(sum[2],tmp,y_0);
	s32i.n	a13, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.h:127:       sum[3] = MAC16_16(sum[3],tmp,y_1);
	s32i.n	a3, sp, 32	# %sfp,
.L125:
# @OPUS@\upstream\celt\pitch.c:275:       xcorr[i]=sum[0];
	l32i	a4, sp, 72	# %sfp,
# @OPUS@\upstream\celt\pitch.c:278:       xcorr[i+3]=sum[3];
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.c:275:       xcorr[i]=sum[0];
	l32i.n	a5, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.c:276:       xcorr[i+1]=sum[1];
	l32i.n	a6, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:277:       xcorr[i+2]=sum[2];
	l32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.c:275:       xcorr[i]=sum[0];
	s32i.n	a5, a4, 0	# MEM[base: _766, offset: 0B],
# @OPUS@\upstream\celt\pitch.c:276:       xcorr[i+1]=sum[1];
	s32i.n	a6, a4, 4	# MEM[base: _766, offset: 4B],
# @OPUS@\upstream\celt\pitch.c:277:       xcorr[i+2]=sum[2];
	s32i.n	a7, a4, 8	# MEM[base: _766, offset: 8B],
# @OPUS@\upstream\celt\pitch.c:278:       xcorr[i+3]=sum[3];
	s32i.n	a8, a4, 12	# MEM[base: _766, offset: 12B],
	mov.n	a2, a8	# sum$3,
	bge	a8, a7, .L126	# sum$3,,
	mov.n	a2, a7	# sum$3,
.L126:
	l32i	a9, sp, 84	# %sfp,
	bge	a2, a9, .L127	# sum$3,,
	mov.n	a2, a9	# sum$3,
.L127:
	l32i.n	a11, sp, 48	# %sfp,
	bge	a2, a11, .L128	# _14,,
	mov.n	a2, a11	# _14,
.L128:
# @OPUS@\upstream\celt\pitch.c:283:       maxcorr = MAX32(maxcorr, sum[0]);
	l32i.n	a13, sp, 52	# %sfp,
	s32i	a2, sp, 84	# %sfp, _14
	bge	a2, a13, .L129	# _14,,
	s32i	a13, sp, 84	# %sfp,
.L129:
	l32i	a2, sp, 72	# %sfp,
	l32i	a3, sp, 80	# %sfp,
	addi	a2, a2, 16	#,,
	addi.n	a3, a3, 8	#,,
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	l32i	a4, sp, 96	# %sfp,
	s32i	a2, sp, 72	# %sfp,
	s32i	a3, sp, 80	# %sfp,
	bne	a4, a2, .L130	#,,
	l32i	a5, sp, 128	# %sfp,
	slli	a8, a5, 2	# i,,
	j	.L120		#
.L152:
# @OPUS@\upstream\celt\pitch.c:258:    opus_val32 maxcorr=1;
	movi.n	a6, 1	#,
	s32i	a6, sp, 84	# %sfp,
# @OPUS@\upstream\celt\pitch.c:262:    for (i=0;i<max_pitch-3;i+=4)
	movi.n	a8, 0	# i,
.L120:
# @OPUS@\upstream\celt\pitch.c:287:    for (;i<max_pitch;i++)
	l32i	a9, sp, 112	# %sfp,
	bge	a8, a9, .L131	# i,,
	mov.n	a11, a9	#,
	l32i	a13, sp, 88	# %sfp,
	slli	a10, a11, 2	# tmp465,,
	l32i	a11, sp, 100	# %sfp,
	slli	a9, a8, 2	# tmp463, i,
	slli	a7, a13, 1	# tmp466,,
	l32i	a5, sp, 92	# %sfp,
	l32i	a13, sp, 104	# %sfp,
	slli	a8, a8, 1	# tmp464, i,
	add.n	a9, a11, a9	# ivtmp$177,, tmp463
	add.n	a10, a11, a10	# _812,, tmp465
	l32i	a12, sp, 88	# %sfp, _1
	l32i	a11, sp, 84	# %sfp, maxcorr
	add.n	a8, a13, a8	# ivtmp$178,, tmp464
	add.n	a7, a5, a7	# _853,, tmp466
	mov.n	a13, a5	# x_lp4,
.L135:
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	blti	a12, 1, .L155	# _1,,
	mov.n	a4, a8	# ivtmp$172, ivtmp$178
	mov.n	a2, a13	# ivtmp$171, x_lp4
# @OPUS@\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a5, 0	# xy,
.L133:
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	l16ui	a3, a2, 0	# MEM[base: _858, offset: 0B],
	l16ui	a6, a4, 0	# MEM[base: _857, offset: 0B],
	addi.n	a2, a2, 2	# ivtmp$171, ivtmp$171,
	mul16s	a3, a3, a6	# tmp467, MEM[base: _858, offset: 0B], MEM[base: _857, offset: 0B]
	addi.n	a4, a4, 2	# ivtmp$172, ivtmp$172,
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a5, a5, a3	# xy, xy, tmp467
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	bne	a7, a2, .L133	# _853, ivtmp$171,
	j	.L132		#
.L155:
# @OPUS@\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a5, 0	# xy,
.L132:
# @OPUS@\upstream\celt\pitch.c:291:       xcorr[i] = sum;
	s32i.n	a5, a9, 0	# MEM[base: _826, offset: 0B], xy
# @OPUS@\upstream\celt\pitch.c:293:       maxcorr = MAX32(maxcorr, sum);
	bge	a11, a5, .L134	# maxcorr, xy,
	mov.n	a11, a5	# maxcorr, xy
.L134:
	addi.n	a9, a9, 4	# ivtmp$177, ivtmp$177,
	addi.n	a8, a8, 2	# ivtmp$178, ivtmp$178,
# @OPUS@\upstream\celt\pitch.c:287:    for (;i<max_pitch;i++)
	bne	a10, a9, .L135	# _812, ivtmp$177,
	s32i	a11, sp, 84	# %sfp, maxcorr
.L131:
# @OPUS@\upstream\celt\pitch.c:358:    find_best_pitch(xcorr, y_lp4, len>>2, max_pitch>>2, best_pitch
	l32i	a6, sp, 84	# %sfp,
	l32i	a4, sp, 88	# %sfp,
	l32i	a5, sp, 112	# %sfp,
	l32i	a3, sp, 104	# %sfp,
	l32i	a2, sp, 100	# %sfp,
	s32i.n	a6, sp, 0	#,
	movi.n	a7, 0	#,
	addi	a6, sp, 24	#,,
	call0	find_best_pitch		#
	l32i	a8, sp, 124	# %sfp,
# @OPUS@\upstream\celt\pitch.c:368:    for (i=0;i<max_pitch>>1;i++)
	l32i	a9, sp, 116	# %sfp,
	srai	a4, a8, 1	# _907,,
	blti	a9, 1, .L156	#,,
	l32i	a11, sp, 120	# %sfp,
	mov.n	a15, a9	# _5,
# @OPUS@\upstream\celt\pitch.c:368:    for (i=0;i<max_pitch>>1;i++)
	movi.n	a8, 0	# i,
	slli	a9, a4, 1	# tmp471, _907,
	l32i	a10, sp, 100	# %sfp, ivtmp$167
	l32i	a14, sp, 132	# %sfp, shift
	l32i	a7, sp, 120	# %sfp, x_lp
	add.n	a9, a11, a9	# _885,, tmp471
# @OPUS@\upstream\celt\pitch.c:366:    maxcorr=1;
	movi.n	a12, 1	# maxcorr,
# @OPUS@\upstream\celt\pitch.c:371:       xcorr[i] = 0;
	mov.n	a11, a8	# tmp472, i
.L143:
	s32i.n	a11, a10, 0	# MEM[base: _881, offset: 0B], tmp472
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	l32i.n	a2, sp, 24	# best_pitch, best_pitch
	slli	a2, a2, 1	# tmp476, best_pitch,
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	sub	a2, a8, a2	# tmp478, i, tmp476
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	abs	a2, a2	# tmp479, tmp478
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	blti	a2, 3, .L137	# tmp479,,
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	l32i.n	a2, sp, 28	# best_pitch, best_pitch
	slli	a2, a2, 1	# tmp483, best_pitch,
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	sub	a2, a8, a2	# tmp485, i, tmp483
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	abs	a2, a2	# tmp486, tmp485
# @OPUS@\upstream\celt\pitch.c:372:       if (abs(i-2*best_pitch[0])>2 && abs(i-2*best_pitch[1])>2)
	bgei	a2, 3, .L138	# tmp486,,
	j	.L137		#
.L141:
	l32i	a13, sp, 108	# %sfp,
	slli	a5, a8, 1	# tmp487, i,
	add.n	a5, a13, a5	# ivtmp$163,, tmp487
# @OPUS@\upstream\celt\pitch.c:376:       for (j=0;j<len>>1;j++)
	mov.n	a3, a7	# ivtmp$162, x_lp
	movi.n	a6, 0	# sum,
.L139:
# @OPUS@\upstream\celt\pitch.c:377:          sum += SHR32(MULT16_16(x_lp[j],y[i+j]), shift);
	l16ui	a2, a3, 0	# MEM[base: _890, offset: 0B],
	l16ui	a13, a5, 0	# MEM[base: _889, offset: 0B],
	addi.n	a3, a3, 2	# ivtmp$162, ivtmp$162,
	mul16s	a2, a2, a13	# tmp488, MEM[base: _890, offset: 0B],
	addi.n	a5, a5, 2	# ivtmp$163, ivtmp$163,
	ssr	a14	# shift
	sra	a2, a2	# tmp491, tmp488
# @OPUS@\upstream\celt\pitch.c:377:          sum += SHR32(MULT16_16(x_lp[j],y[i+j]), shift);
	add.n	a6, a6, a2	# sum, sum, tmp491
# @OPUS@\upstream\celt\pitch.c:376:       for (j=0;j<len>>1;j++)
	bne	a9, a3, .L139	# _885, ivtmp$162,
	movi.n	a2, -1	# _933,
	movgez	a2, a6, a6	# _933, sum, sum
	j	.L140		#
.L137:
# @OPUS@\upstream\celt\pitch.c:376:       for (j=0;j<len>>1;j++)
	bgei	a4, 1, .L141	# _907,,
# @OPUS@\upstream\celt\pitch.c:376:       for (j=0;j<len>>1;j++)
	mov.n	a2, a11	# _933, tmp472
	movi.n	a6, 0	# sum,
.L140:
# @OPUS@\upstream\celt\pitch.c:381:       xcorr[i] = MAX32(-1, sum);
	s32i.n	a2, a10, 0	# MEM[base: _881, offset: 0B], _933
# @OPUS@\upstream\celt\pitch.c:383:       maxcorr = MAX32(maxcorr, sum);
	bge	a12, a6, .L138	# maxcorr, sum,
	mov.n	a12, a6	# maxcorr, sum
.L138:
# @OPUS@\upstream\celt\pitch.c:368:    for (i=0;i<max_pitch>>1;i++)
	addi.n	a8, a8, 1	# i, i,
	addi.n	a10, a10, 4	# ivtmp$167, ivtmp$167,
# @OPUS@\upstream\celt\pitch.c:368:    for (i=0;i<max_pitch>>1;i++)
	bne	a15, a8, .L143	# _5, i,
	j	.L136		#
.L156:
# @OPUS@\upstream\celt\pitch.c:366:    maxcorr=1;
	movi.n	a12, 1	# maxcorr,
.L136:
# @OPUS@\upstream\celt\pitch.c:386:    find_best_pitch(xcorr, y, len>>1, max_pitch>>1, best_pitch
	l32i	a2, sp, 100	# %sfp,
	l32i	a7, sp, 136	# %sfp,
	l32i	a5, sp, 116	# %sfp,
	l32i	a3, sp, 108	# %sfp,
	s32i.n	a12, sp, 0	#, maxcorr
	addi	a6, sp, 24	#,,
	call0	find_best_pitch		#
# @OPUS@\upstream\celt\pitch.c:393:    if (best_pitch[0]>0 && best_pitch[0]<(max_pitch>>1)-1)
	l32i.n	a2, sp, 24	# best_pitch, _71
# @OPUS@\upstream\celt\pitch.c:414:       offset = 0;
	movi.n	a4, 0	# offset,
# @OPUS@\upstream\celt\pitch.c:393:    if (best_pitch[0]>0 && best_pitch[0]<(max_pitch>>1)-1)
	blti	a2, 1, .L144	# _71,,
# @OPUS@\upstream\celt\pitch.c:393:    if (best_pitch[0]>0 && best_pitch[0]<(max_pitch>>1)-1)
	l32i	a8, sp, 116	# %sfp,
	addi.n	a3, a8, -1	# tmp494,,
# @OPUS@\upstream\celt\pitch.c:393:    if (best_pitch[0]>0 && best_pitch[0]<(max_pitch>>1)-1)
	bge	a2, a3, .L144	# _71, tmp494,
# @OPUS@\upstream\celt\pitch.c:399:       a = yoradio_opus_load32(&xcorr[best_pitch[0]-1]);
	l32i	a9, sp, 100	# %sfp,
# @OPUS@\upstream\celt\pitch.c:399:       a = yoradio_opus_load32(&xcorr[best_pitch[0]-1]);
	slli	a2, a2, 2	# tmp496, _71,
	addi	a2, a2, -4	# tmp498, tmp496,
# @OPUS@\upstream\celt\pitch.c:399:       a = yoradio_opus_load32(&xcorr[best_pitch[0]-1]);
	add.n	a2, a9, a2	# tmp499,, tmp498
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp499
# 0 "" 2
# @OPUS@\upstream\celt\pitch.c:400:       b = yoradio_opus_load32(&xcorr[best_pitch[0]]);
#NO_APP
	l32i.n	a3, sp, 24	# best_pitch, best_pitch
	slli	a3, a3, 2	# tmp501, best_pitch,
# @OPUS@\upstream\celt\pitch.c:400:       b = yoradio_opus_load32(&xcorr[best_pitch[0]]);
	add.n	a3, a9, a3	# tmp503,, tmp501
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp503
# 0 "" 2
# @OPUS@\upstream\celt\pitch.c:401:       c = yoradio_opus_load32(&xcorr[best_pitch[0]+1]);
#NO_APP
	l32i.n	a5, sp, 24	# best_pitch, best_pitch
	addi.n	a5, a5, 1	# tmp505, best_pitch,
	slli	a5, a5, 2	# tmp507, tmp505,
# @OPUS@\upstream\celt\pitch.c:401:       c = yoradio_opus_load32(&xcorr[best_pitch[0]+1]);
	add.n	a5, a9, a5	# tmp508,, tmp507
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a5, a5, 0	# value, tmp508
# 0 "" 2
# @OPUS@\upstream\celt\pitch.c:407:       if ((c-a) > MULT16_32_Q15(QCONST16(.7f,15),b-a))
#NO_APP
	slli	a8, a3, 16	# tmp509, value,
	l32r	a7, .LC9	#, tmp514
	srai	a8, a8, 16	# _95, tmp509,
	sub	a6, a3, a2	# tmp511, value, value
	srai	a6, a6, 16	# tmp512, tmp511,
	sub	a9, a8, a2	# tmp517, _95, value
	mull	a6, a6, a7	# tmp513, tmp512, tmp514
	mul16u	a9, a9, a7	# tmp518, tmp517, tmp514
	slli	a6, a6, 1	# tmp515, tmp513,
	srai	a9, a9, 15	# tmp520, tmp518,
# @OPUS@\upstream\celt\pitch.c:407:       if ((c-a) > MULT16_32_Q15(QCONST16(.7f,15),b-a))
	sub	a10, a5, a2	# tmp510, value, value
# @OPUS@\upstream\celt\pitch.c:407:       if ((c-a) > MULT16_32_Q15(QCONST16(.7f,15),b-a))
	add.n	a6, a6, a9	# tmp521, tmp515, tmp520
# @OPUS@\upstream\celt\pitch.c:407:       if ((c-a) > MULT16_32_Q15(QCONST16(.7f,15),b-a))
	bge	a6, a10, .L145	# tmp521, tmp510,
	l32i.n	a2, sp, 24	# best_pitch, _71
# @OPUS@\upstream\celt\pitch.c:408:          offset = 1;
	movi.n	a4, 1	# offset,
	j	.L144		#
.L145:
# @OPUS@\upstream\celt\pitch.c:409:       else if ((a-c) > MULT16_32_Q15(QCONST16(.7f,15),b-c))
	sub	a3, a3, a5	# tmp523, value, value
	sub	a6, a8, a5	# tmp529, _95, value
	srai	a3, a3, 16	# tmp524, tmp523,
	mull	a3, a3, a7	# tmp525, tmp524, tmp514
	mul16u	a6, a6, a7	# tmp530, tmp529, tmp514
	slli	a3, a3, 1	# tmp527, tmp525,
	srai	a6, a6, 15	# tmp532, tmp530,
# @OPUS@\upstream\celt\pitch.c:409:       else if ((a-c) > MULT16_32_Q15(QCONST16(.7f,15),b-c))
	sub	a2, a2, a5	# tmp522, value, value
# @OPUS@\upstream\celt\pitch.c:409:       else if ((a-c) > MULT16_32_Q15(QCONST16(.7f,15),b-c))
	add.n	a3, a3, a6	# tmp533, tmp527, tmp532
# @OPUS@\upstream\celt\pitch.c:409:       else if ((a-c) > MULT16_32_Q15(QCONST16(.7f,15),b-c))
	movi.n	a5, 1	# tmp534,
	blt	a3, a2, .L146	# tmp533, tmp522,
	mov.n	a5, a4	# tmp534, offset
.L146:
	l32i.n	a2, sp, 24	# best_pitch, _71
	neg	a4, a5	# offset, tmp534
.L144:
# @OPUS@\upstream\celt\pitch.c:416:    *pitch = 2*best_pitch[0]-offset;
	l32i	a11, sp, 140	# %sfp,
# @OPUS@\upstream\celt\pitch.c:416:    *pitch = 2*best_pitch[0]-offset;
	slli	a2, a2, 1	# tmp536, _71,
# @OPUS@\upstream\celt\pitch.c:416:    *pitch = 2*best_pitch[0]-offset;
	sub	a4, a2, a4	# tmp537, tmp536, offset
# @OPUS@\upstream\celt\pitch.c:418:    RESTORE_STACK;
	l32i.n	a3, sp, 20	# _saved_stack,
	l32i.n	a2, sp, 16	# _saved_stack,
# @OPUS@\upstream\celt\pitch.c:416:    *pitch = 2*best_pitch[0]-offset;
	s32i.n	a4, a11, 0	# *pitch_181(D), tmp537
# @OPUS@\upstream\celt\pitch.c:418:    RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\pitch.c:419: }
	l32i	a0, sp, 188	#,
	movi	a9, 0xc0	#,
	l32i	a12, sp, 184	#,
	l32i	a13, sp, 180	#,
	l32i	a14, sp, 176	#,
	l32i	a15, sp, 172	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L172:
# @OPUS@\upstream\celt\pitch.c:331:    for (j=0;j<lag>>2;j++)
	bgei	a14, 1, .L147	# _3,,
	j	.L148		#
.L97:
	bgei	a14, 1, .L147	# _3,,
	movi.n	a8, 1	#,
	s32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\celt\pitch.c:347:       shift = 0;
	s32i	a13, sp, 132	# %sfp, tmp326
	j	.L113		#
	.size	pitch_search, .-pitch_search
	.global	__udivsi3
	.section	.text.remove_doubling,"ax",@progbits
	.literal_position
	.literal .LC10, 22938
	.literal .LC11, 27853
	.literal .LC12, 29491
	.literal .LC13, second_check
	.literal .LC14, 13107
	.literal .LC15, 9830
	.literal .LC16, 16384
	.align	4
	.global	remove_doubling
	.type	remove_doubling, @function
# Function: remove_doubling
# Module: upstream/celt/pitch.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context:
# C context: static const int second_check[16] = {0, 0, 3, 2, 3, 2, 5, 2, 3, 2, 3, 2, 5, 2, 3, 2};
# C context: opus_val16 remove_doubling(opus_val16 *x, int maxperiod, int minperiod,
# C context: int N, int *T0_, int prev_period, opus_val16 prev_gain, int arch)
# C context: {
# C context: int k, i, T, T0;
# C context: opus_val16 g, g0;
remove_doubling:
	movi	a9, 0xb0	#,
	sub	sp, sp, a9	#,,
	s32i.n	a5, sp, 40	# %sfp, N
	l16si	a5, sp, 176	# prev_gain,
	s32i	a12, sp, 168	#,
	s32i	a13, sp, 164	#,
	s32i	a14, sp, 160	#,
	mov.n	a13, a7	# prev_period, prev_period
	mov.n	a14, a3	# maxperiod, maxperiod
	s32i	a6, sp, 116	# %sfp, T0_
	s32i	a4, sp, 112	# %sfp, minperiod
	mov.n	a12, a2	# x, x
	s32i.n	a5, sp, 56	# %sfp,
	s32i	a0, sp, 172	#,
	s32i	a15, sp, 156	#,
# @OPUS@\upstream\celt\pitch.c:469:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\pitch.c:474:    *T0_ /= 2;
	l32i	a6, sp, 116	# %sfp,
# @OPUS@\upstream\celt\pitch.c:473:    minperiod /= 2;
	l32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\celt\pitch.c:472:    maxperiod /= 2;
	extui	a4, a14, 31, 1	# tmp236, maxperiod,
# @OPUS@\upstream\celt\pitch.c:474:    *T0_ /= 2;
	l32i.n	a5, a6, 0	# *T0__154(D), *T0__154(D)
# @OPUS@\upstream\celt\pitch.c:472:    maxperiod /= 2;
	add.n	a4, a4, a14	# tmp237, tmp236, maxperiod
# @OPUS@\upstream\celt\pitch.c:473:    minperiod /= 2;
	extui	a6, a9, 31, 1	# tmp239,,
# @OPUS@\upstream\celt\pitch.c:476:    N /= 2;
	l32i.n	a9, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.c:472:    maxperiod /= 2;
	srai	a4, a4, 1	#, tmp237,
	s32i	a4, sp, 88	# %sfp,
# @OPUS@\upstream\celt\pitch.c:476:    N /= 2;
	extui	a4, a9, 31, 1	# tmp249,,
# @OPUS@\upstream\celt\pitch.c:473:    minperiod /= 2;
	l32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\celt\pitch.c:474:    *T0_ /= 2;
	extui	a8, a5, 31, 1	# tmp243, *T0__154(D),
# @OPUS@\upstream\celt\pitch.c:473:    minperiod /= 2;
	add.n	a6, a6, a9	# tmp240, tmp239,
# @OPUS@\upstream\celt\pitch.c:476:    N /= 2;
	l32i.n	a9, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.c:474:    *T0_ /= 2;
	add.n	a8, a8, a5	# tmp244, tmp243, *T0__154(D)
# @OPUS@\upstream\celt\pitch.c:476:    N /= 2;
	add.n	a4, a4, a9	# tmp250, tmp249,
# @OPUS@\upstream\celt\pitch.c:477:    x += maxperiod;
	l32i	a9, sp, 88	# %sfp,
# @OPUS@\upstream\celt\pitch.c:475:    prev_period /= 2;
	extui	a5, a13, 31, 1	# tmp246, prev_period,
	add.n	a5, a5, a13	# tmp247, tmp246, prev_period
# @OPUS@\upstream\celt\pitch.c:477:    x += maxperiod;
	slli	a7, a9, 1	# tmp252,,
# @OPUS@\upstream\celt\pitch.c:474:    *T0_ /= 2;
	srai	a8, a8, 1	#, tmp244,
# @OPUS@\upstream\celt\pitch.c:473:    minperiod /= 2;
	srai	a6, a6, 1	#, tmp240,
# @OPUS@\upstream\celt\pitch.c:475:    prev_period /= 2;
	srai	a5, a5, 1	#, tmp247,
# @OPUS@\upstream\celt\pitch.c:477:    x += maxperiod;
	add.n	a7, a12, a7	#, x, tmp252
# @OPUS@\upstream\celt\pitch.c:469:    SAVE_STACK;
	s32i.n	a2, sp, 12	# _saved_stack,
	s32i.n	a3, sp, 16	# _saved_stack,
# @OPUS@\upstream\celt\pitch.c:474:    *T0_ /= 2;
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:473:    minperiod /= 2;
	s32i.n	a6, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.c:475:    prev_period /= 2;
	s32i	a5, sp, 72	# %sfp,
# @OPUS@\upstream\celt\pitch.c:477:    x += maxperiod;
	s32i.n	a7, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.c:476:    N /= 2;
	srai	a13, a4, 1	# N, tmp250,
# @OPUS@\upstream\celt\pitch.c:478:    if (*T0_>=maxperiod)
	bge	a8, a9, .L177	#,,
# @OPUS@\upstream\celt\pitch.c:474:    *T0_ /= 2;
	l32i	a6, sp, 116	# %sfp,
	s32i.n	a8, a6, 0	# *T0__154(D),
	j	.L178		#
.L177:
# @OPUS@\upstream\celt\pitch.c:479:       *T0_=maxperiod-1;
	addi.n	a7, a9, -1	#, tmp7,
# @OPUS@\upstream\celt\pitch.c:479:       *T0_=maxperiod-1;
	l32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\celt\pitch.c:479:       *T0_=maxperiod-1;
	s32i.n	a7, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:479:       *T0_=maxperiod-1;
	s32i.n	a7, a9, 0	# *T0__154(D),
.L178:
# @OPUS@\upstream\celt\pitch.c:482:    ALLOC(yy_lookup, maxperiod+1, opus_val32);
	l32i	a5, sp, 88	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	add.n	a2, a5, a4	#,,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\pitch.c:483:    dual_inner_prod(x, x, x-T0, N, &xx, &xy, arch);
	l32i.n	a6, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	l32i.n	a9, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.c:483:    dual_inner_prod(x, x, x-T0, N, &xx, &xy, arch);
	slli	a6, a6, 1	#,,
# @OPUS@\upstream\celt\pitch.c:482:    ALLOC(yy_lookup, maxperiod+1, opus_val32);
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\pitch.c:483:    dual_inner_prod(x, x, x-T0, N, &xx, &xy, arch);
	s32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	blti	a9, 2, .L179	#,,
	l32i.n	a5, sp, 52	# %sfp,
# @OPUS@\upstream\celt\pitch.h:142:    opus_val32 xy02=0;
	movi.n	a12, 0	# xy02,
	sub	a2, a5, a6	# ivtmp$262,,
	mov.n	a8, a6	# _32,
# @OPUS@\upstream\celt\pitch.h:141:    opus_val32 xy01=0;
	s32i.n	a12, sp, 60	# %sfp, xy02
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	mov.n	a5, a12	# i, xy02
	mov.n	a6, a12	# xy01, i
.L180:
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	add.n	a3, a2, a8	# tmp254, ivtmp$262, _32
	l16si	a4, a3, 0	# MEM[base: _504, offset: 0B], _199
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	l16ui	a3, a2, 0	# MEM[base: _505, offset: 0B],
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	mull	a7, a4, a4	# tmp257, _199, _199
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	mul16s	a3, a3, a4	# tmp258, MEM[base: _505, offset: 0B], _199
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	add.n	a6, a6, a7	# xy01, xy01, tmp257
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	add.n	a12, a12, a3	# xy02, xy02, tmp258
	addi.n	a2, a2, 2	# ivtmp$262, ivtmp$262,
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	blt	a5, a13, .L180	# i, N,
	movi.n	a10, 0	# tmp263,
	movi.n	a2, 1	# tmp262,
	mov.n	a3, a10	# tmp261, tmp263
	moveqz	a3, a2, a6	# tmp261, tmp262, xy01
# @OPUS@\upstream\celt\pitch.c:484:    yy_lookup[0] = xx;
	l32i.n	a7, sp, 32	# %sfp,
	extui	a3, a3, 0, 8	#, tmp261
	movnez	a2, a10, a12	# tmp265, tmp263, xy02
	s32i.n	a6, sp, 60	# %sfp, xy01
	s32i	a3, sp, 64	# %sfp,
	s32i.n	a6, a7, 0	# *yy_lookup_166, xy01
	or	a10, a3, a2	# prephitmp_227,, tmp265
# @OPUS@\upstream\celt\pitch.c:486:    for (i=1;i<=maxperiod;i++)
	bgei	a14, 2, .L181	# maxperiod,,
.L185:
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	l32i.n	a9, sp, 48	# %sfp,
	l32i.n	a5, sp, 32	# %sfp,
	slli	a2, a9, 2	# tmp269,,
	add.n	a2, a5, a2	#,, tmp269
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	l32i.n	a6, a2, 0	# *_31,
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	s32i	a2, sp, 120	# %sfp,
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	s32i	a6, sp, 84	# %sfp,
# @OPUS@\upstream\celt\pitch.c:428:    if (xy == 0 || xx == 0 || yy == 0)
	beqz.n	a6, .L210	#,
	beqz.n	a10, .L225	# prephitmp_227,
	j	.L210		#
.L218:
# @OPUS@\upstream\celt\pitch.c:486:    for (i=1;i<=maxperiod;i++)
	movi.n	a10, 1	# prephitmp_227,
	s32i	a10, sp, 64	# %sfp, prephitmp_227
# @OPUS@\upstream\celt\pitch.h:141:    opus_val32 xy01=0;
	s32i.n	a12, sp, 60	# %sfp, xy02
.L181:
	l32i.n	a7, sp, 52	# %sfp,
	l32i.n	a9, sp, 32	# %sfp,
	l32i.n	a4, sp, 60	# %sfp, yy
# @OPUS@\upstream\celt\pitch.c:489:       yy_lookup[i] = MAX32(0, yy);
	l32i	a11, sp, 88	# %sfp, maxperiod
	addi	a5, a7, -2	# ivtmp$251,,
# @OPUS@\upstream\celt\pitch.c:486:    for (i=1;i<=maxperiod;i++)
	movi.n	a6, 1	# i,
	addi.n	a7, a9, 4	# ivtmp$255,,
# @OPUS@\upstream\celt\pitch.c:489:       yy_lookup[i] = MAX32(0, yy);
	movi.n	a8, 0	# tmp284,
	slli	a9, a13, 1	# _513, N,
.L184:
# @OPUS@\upstream\celt\pitch.c:488:       yy = yy+MULT16_16(x[-i],x[-i])-MULT16_16(x[N-i],x[N-i]);
	add.n	a3, a5, a9	# tmp277, ivtmp$251, _513
# @OPUS@\upstream\celt\pitch.c:488:       yy = yy+MULT16_16(x[-i],x[-i])-MULT16_16(x[N-i],x[N-i]);
	l16si	a2, a5, 0	# MEM[base: _516, offset: 0B], _15
# @OPUS@\upstream\celt\pitch.c:488:       yy = yy+MULT16_16(x[-i],x[-i])-MULT16_16(x[N-i],x[N-i]);
	l16si	a3, a3, 0	# MEM[base: _512, offset: 0B], _23
# @OPUS@\upstream\celt\pitch.c:488:       yy = yy+MULT16_16(x[-i],x[-i])-MULT16_16(x[N-i],x[N-i]);
	mull	a2, a2, a2	# tmp280, _15, _15
# @OPUS@\upstream\celt\pitch.c:488:       yy = yy+MULT16_16(x[-i],x[-i])-MULT16_16(x[N-i],x[N-i]);
	mull	a3, a3, a3	# tmp281, _23, _23
# @OPUS@\upstream\celt\pitch.c:486:    for (i=1;i<=maxperiod;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\celt\pitch.c:488:       yy = yy+MULT16_16(x[-i],x[-i])-MULT16_16(x[N-i],x[N-i]);
	sub	a2, a2, a3	# tmp282, tmp280, tmp281
	add.n	a4, a4, a2	# yy, yy, tmp282
# @OPUS@\upstream\celt\pitch.c:489:       yy_lookup[i] = MAX32(0, yy);
	mov.n	a2, a8	# tmp283, tmp284
	movgez	a2, a4, a4	# tmp283, yy, yy
# @OPUS@\upstream\celt\pitch.c:489:       yy_lookup[i] = MAX32(0, yy);
	s32i.n	a2, a7, 0	# MEM[base: _511, offset: 0B], tmp283
	addi	a5, a5, -2	# ivtmp$251, ivtmp$251,
	addi.n	a7, a7, 4	# ivtmp$255, ivtmp$255,
# @OPUS@\upstream\celt\pitch.c:486:    for (i=1;i<=maxperiod;i++)
	bge	a11, a6, .L184	# maxperiod, i,
	j	.L185		#
.L225:
	l32i.n	a3, sp, 60	# %sfp,
	mov.n	a4, a6	#,
	mov.n	a2, a12	#, xy02
	call0	compute_pitch_gain$part$0		#
	s32i	a2, sp, 80	# %sfp,
	l32i	a5, sp, 80	# %sfp,
	l32r	a4, .LC10	#, tmp287
	l32r	a3, .LC11	#, tmp289
	l32r	a2, .LC12	#, tmp291
	mul16s	a4, a5, a4	# tmp286,, tmp287
	mul16s	a3, a5, a3	# tmp288,, tmp289
	mul16s	a2, a5, a2	# tmp290,, tmp291
	srai	a4, a4, 15	#, tmp286,
	srai	a3, a3, 15	#, tmp288,
	srai	a2, a2, 15	#, tmp290,
	s32i	a4, sp, 76	# %sfp,
	s32i	a3, sp, 104	# %sfp,
	s32i	a2, sp, 108	# %sfp,
	j	.L182		#
.L210:
# @OPUS@\upstream\celt\pitch.c:428:    if (xy == 0 || xx == 0 || yy == 0)
	movi.n	a6, 0	#,
	s32i	a6, sp, 108	# %sfp,
	s32i	a6, sp, 104	# %sfp,
	s32i	a6, sp, 76	# %sfp,
# @OPUS@\upstream\celt\pitch.c:429:       return 0;
	s32i	a6, sp, 80	# %sfp,
.L182:
# @OPUS@\upstream\celt\pitch.c:529:       if (T1<3*minperiod)
	l32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\celt\pitch.c:523:          cont = HALF16(prev_gain);
	l32i.n	a9, sp, 56	# %sfp,
# @OPUS@\upstream\celt\pitch.c:529:       if (T1<3*minperiod)
	l32i.n	a5, sp, 44	# %sfp,
	slli	a7, a7, 1	#,,
# @OPUS@\upstream\celt\pitch.c:481:    T = T0 = *T0_;
	l32i.n	a6, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:523:          cont = HALF16(prev_gain);
	srai	a9, a9, 1	#,,
# @OPUS@\upstream\celt\pitch.c:529:       if (T1<3*minperiod)
	add.n	a5, a7, a5	#,,
	s32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\celt\pitch.c:523:          cont = HALF16(prev_gain);
	s32i	a9, sp, 124	# %sfp,
# @OPUS@\upstream\celt\pitch.c:529:       if (T1<3*minperiod)
	s32i	a5, sp, 68	# %sfp,
# @OPUS@\upstream\celt\pitch.c:481:    T = T0 = *T0_;
	s32i	a6, sp, 92	# %sfp,
# @OPUS@\upstream\celt\pitch.c:496:    for (k=2;k<=15;k++)
	movi.n	a14, 2	# k,
# @OPUS@\upstream\celt\pitch.c:517:       xy = HALF32(xy + xy2);
	s32i	a12, sp, 100	# %sfp, xy02
.L200:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a7, sp, 36	# %sfp,
	slli	a12, a14, 1	# _532, k,
	mov.n	a3, a12	#, _532
	add.n	a2, a7, a14	#,, k
	call0	__udivsi3		#
# @OPUS@\upstream\celt\pitch.c:503:       if (T1 < minperiod)
	l32i.n	a9, sp, 44	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a15, a2	# _218,
# @OPUS@\upstream\celt\pitch.c:503:       if (T1 < minperiod)
	blt	a2, a9, .L186	# _218,,
# @OPUS@\upstream\celt\pitch.c:506:       if (k==2)
	bnei	a14, 2, .L187	# k,,
# @OPUS@\upstream\celt\pitch.c:508:          if (T1+T0>maxperiod)
	l32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:508:          if (T1+T0>maxperiod)
	l32i	a6, sp, 88	# %sfp,
# @OPUS@\upstream\celt\pitch.c:508:          if (T1+T0>maxperiod)
	add.n	a2, a2, a5	# _37, _218,
# @OPUS@\upstream\celt\pitch.c:508:          if (T1+T0>maxperiod)
	blt	a6, a2, .L211	#, _37,
	l32i.n	a7, sp, 32	# %sfp,
	slli	a4, a2, 2	# tmp301, _219,
	add.n	a4, a7, a4	# _553,, tmp301
	mov.n	a6, a7	#,
	j	.L188		#
.L187:
# @OPUS@\upstream\celt\pitch.c:514:          T1b = celt_udiv(2*second_check[k]*T0+k, 2*k);
	l32r	a3, .LC13	#, tmp304
	slli	a2, a14, 2	# tmp302, k,
	add.n	a2, a2, a3	# tmp303, tmp302, tmp304
# @OPUS@\upstream\celt\pitch.c:514:          T1b = celt_udiv(2*second_check[k]*T0+k, 2*k);
	l32i.n	a9, sp, 36	# %sfp,
	l32i.n	a2, a2, 0	# MEM[base: _525, offset: 0B], MEM[base: _525, offset: 0B]
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a12	#, _532
# @OPUS@\upstream\celt\pitch.c:514:          T1b = celt_udiv(2*second_check[k]*T0+k, 2*k);
	mull	a2, a9, a2	# tmp305,, MEM[base: _525, offset: 0B]
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	add.n	a2, a2, a14	#, tmp305, k
	call0	__udivsi3		#
	l32i.n	a5, sp, 32	# %sfp,
	slli	a4, a2, 2	# tmp311, _219,
	add.n	a4, a5, a4	# _553,, tmp311
	mov.n	a6, a5	#,
	j	.L188		#
.L211:
	l32i	a4, sp, 120	# %sfp, _553
	l32i.n	a6, sp, 32	# %sfp,
	mov.n	a2, a5	# _219,
.L188:
	slli	a3, a15, 2	# tmp320, _218,
	add.n	a3, a6, a3	# tmp321,, tmp320
	l32i.n	a8, a3, 0	# *_568, *_568
	l32i.n	a3, a4, 0	# *prephitmp_555, *prephitmp_555
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	l32i.n	a9, sp, 40	# %sfp,
# @OPUS@\upstream\celt\pitch.c:516:       dual_inner_prod(x, &x[-T1], &x[-T1b], N, &xy, &xy2, arch);
	slli	a11, a15, 1	# tmp314, _218,
	slli	a2, a2, 1	# tmp318, _219,
	add.n	a8, a8, a3	# tmp322, *_568, *prephitmp_555
	neg	a11, a11	# tmp315, tmp314
	neg	a10, a2	# tmp319, tmp318
	srai	a8, a8, 1	# _572, tmp322,
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	blti	a9, 2, .L212	#,,
# @OPUS@\upstream\celt\pitch.h:142:    opus_val32 xy02=0;
	movi.n	a9, 0	# xy02,
	l32i.n	a2, sp, 52	# %sfp, ivtmp$231
# @OPUS@\upstream\celt\pitch.h:141:    opus_val32 xy01=0;
	mov.n	a7, a9	# xy01, xy02
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	mov.n	a5, a9	# i, xy02
.L190:
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	add.n	a4, a2, a11	# tmp327, ivtmp$231, tmp315
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	add.n	a3, a2, a10	# tmp330, ivtmp$231, tmp319
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	l16si	a6, a2, 0	# MEM[base: _546, offset: 0B], _228
	l16ui	a4, a4, 0	# MEM[base: _544, offset: 0B],
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	l16ui	a3, a3, 0	# MEM[base: _542, offset: 0B],
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	mul16s	a4, a4, a6	# tmp328, MEM[base: _544, offset: 0B], _228
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	mul16s	a3, a3, a6	# tmp331, MEM[base: _542, offset: 0B], _228
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	add.n	a7, a7, a4	# xy01, xy01, tmp328
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	add.n	a9, a9, a3	# xy02, xy02, tmp331
	addi.n	a2, a2, 2	# ivtmp$231, ivtmp$231,
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	blt	a5, a13, .L190	# i, N,
# @OPUS@\upstream\celt\pitch.c:428:    if (xy == 0 || xx == 0 || yy == 0)
	movi.n	a3, 1	# tmp336,
	movi.n	a2, 0	# tmp335,
	l32i	a5, sp, 64	# %sfp,
	moveqz	a2, a3, a8	# tmp335, tmp336, _572
# @OPUS@\upstream\celt\pitch.c:517:       xy = HALF32(xy + xy2);
	add.n	a7, a7, a9	# tmp333, xy01, xy02
# @OPUS@\upstream\celt\pitch.c:428:    if (xy == 0 || xx == 0 || yy == 0)
	or	a2, a5, a2	# tmp340,, tmp335
# @OPUS@\upstream\celt\pitch.c:517:       xy = HALF32(xy + xy2);
	ssr	a3	#
	sra	a7, a7	# _47, tmp333
# @OPUS@\upstream\celt\pitch.c:428:    if (xy == 0 || xx == 0 || yy == 0)
	bnez.n	a2, .L213	# tmp340,
	moveqz	a2, a3, a7	# tmp345, tmp336, _47
	bnez.n	a2, .L213	# tmp345,
	l32i.n	a3, sp, 60	# %sfp,
	mov.n	a4, a8	#, _572
	mov.n	a2, a7	#, _47
	s32i	a7, sp, 128	#,
	s32i	a8, sp, 132	#,
	call0	compute_pitch_gain$part$0		#
	l32i	a7, sp, 128	#,
	l32i	a8, sp, 132	#,
	j	.L189		#
.L212:
# @OPUS@\upstream\celt\pitch.c:517:       xy = HALF32(xy + xy2);
	movi.n	a7, 0	# _47,
# @OPUS@\upstream\celt\pitch.c:429:       return 0;
	mov.n	a2, a7	# _222, _47
	j	.L189		#
.L213:
	movi.n	a2, 0	# _222,
.L189:
# @OPUS@\upstream\celt\pitch.c:520:       if (abs(T1-prev_period)<=1)
	l32i	a6, sp, 72	# %sfp,
	sub	a3, a15, a6	# _55, _218,
# @OPUS@\upstream\celt\pitch.c:520:       if (abs(T1-prev_period)<=1)
	addi.n	a4, a3, 1	# tmp347, _55,
# @OPUS@\upstream\celt\pitch.c:520:       if (abs(T1-prev_period)<=1)
	bgeui	a4, 3, .L191	# tmp347,,
	l32i.n	a3, sp, 56	# %sfp, _592
	l32i	a9, sp, 76	# %sfp,
	sub	a4, a9, a3	# _595,, _592
	j	.L192		#
.L191:
# @OPUS@\upstream\celt\pitch.c:522:       else if (abs(T1-prev_period)<=2 && 5*k*k < T0)
	addi.n	a3, a3, 2	# tmp348, _55,
# @OPUS@\upstream\celt\pitch.c:522:       else if (abs(T1-prev_period)<=2 && 5*k*k < T0)
	bgeui	a3, 5, .L215	# tmp348,,
# @OPUS@\upstream\celt\pitch.c:522:       else if (abs(T1-prev_period)<=2 && 5*k*k < T0)
	mull	a4, a14, a14	# tmp349, k, k
# @OPUS@\upstream\celt\pitch.c:522:       else if (abs(T1-prev_period)<=2 && 5*k*k < T0)
	l32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:522:       else if (abs(T1-prev_period)<=2 && 5*k*k < T0)
	slli	a3, a4, 2	# tmp351, tmp349,
	add.n	a3, a3, a4	# tmp352, tmp351, tmp349
# @OPUS@\upstream\celt\pitch.c:522:       else if (abs(T1-prev_period)<=2 && 5*k*k < T0)
	bge	a3, a5, .L215	# tmp352,,
	l32i	a3, sp, 124	# %sfp, _592
	l32i	a6, sp, 76	# %sfp,
	sub	a4, a6, a3	# _595,, _592
# @OPUS@\upstream\celt\pitch.c:523:          cont = HALF16(prev_gain);
	j	.L192		#
.L215:
	l32i	a4, sp, 76	# %sfp, _595
	movi.n	a3, 0	# _592,
.L192:
# @OPUS@\upstream\celt\pitch.c:529:       if (T1<3*minperiod)
	l32i	a9, sp, 68	# %sfp,
	bge	a15, a9, .L193	# _218,,
# @OPUS@\upstream\celt\pitch.c:530:          thresh = MAX16(QCONST16(.4f,15), MULT16_16_Q15(QCONST16(.85f,15),g0)-cont);
	l32i	a5, sp, 104	# %sfp,
	l32r	a4, .LC14	#, tmp358
	sub	a3, a5, a3	# tmp353,, _592
	bge	a3, a4, .L198	# tmp353, tmp358,
	j	.L228		#
.L193:
# @OPUS@\upstream\celt\pitch.c:531:       else if (T1<2*minperiod)
	l32i	a6, sp, 96	# %sfp,
	blt	a15, a6, .L196	# _218,,
# @OPUS@\upstream\celt\pitch.c:526:       thresh = MAX16(QCONST16(.3f,15), MULT16_16_Q15(QCONST16(.7f,15),g0)-cont);
	l32r	a3, .LC15	#, tmp365
	bge	a4, a3, .L197	# _595, tmp365,
	mov.n	a4, a3	# _595, tmp365
.L197:
# @OPUS@\upstream\celt\pitch.c:526:       thresh = MAX16(QCONST16(.3f,15), MULT16_16_Q15(QCONST16(.7f,15),g0)-cont);
	slli	a4, a4, 16	# tmp366, _595,
	srai	a3, a4, 16	# thresh, tmp366,
	j	.L195		#
.L196:
# @OPUS@\upstream\celt\pitch.c:532:          thresh = MAX16(QCONST16(.5f,15), MULT16_16_Q15(QCONST16(.9f,15),g0)-cont);
	l32i	a9, sp, 108	# %sfp,
	l32r	a4, .LC16	#, tmp372
	sub	a3, a9, a3	# tmp367,, _592
	bge	a3, a4, .L198	# tmp367, tmp372,
.L228:
	mov.n	a3, a4	# tmp367, tmp372
.L198:
# @OPUS@\upstream\celt\pitch.c:532:          thresh = MAX16(QCONST16(.5f,15), MULT16_16_Q15(QCONST16(.9f,15),g0)-cont);
	slli	a3, a3, 16	# tmp373, tmp367,
	srai	a3, a3, 16	# thresh, tmp373,
.L195:
# @OPUS@\upstream\celt\pitch.c:533:       if (g1 > thresh)
	bge	a3, a2, .L199	# thresh, _222,
	s32i	a8, sp, 84	# %sfp, _572
	s32i	a7, sp, 100	# %sfp, _47
	s32i	a2, sp, 80	# %sfp, _222
	s32i	a15, sp, 92	# %sfp, _218
.L199:
# @OPUS@\upstream\celt\pitch.c:496:    for (k=2;k<=15;k++)
	addi.n	a14, a14, 1	# k, k,
# @OPUS@\upstream\celt\pitch.c:496:    for (k=2;k<=15;k++)
	bnei	a14, 16, .L200	# k,,
.L186:
	l32i	a12, sp, 100	# %sfp, xy02
# @OPUS@\upstream\celt\pitch.c:541:    best_xy = MAX32(0, best_xy);
	movi.n	a2, 0	# tmp374,
# @OPUS@\upstream\celt\pitch.c:542:    if (best_yy <= best_xy)
	l32i	a5, sp, 84	# %sfp,
# @OPUS@\upstream\celt\pitch.c:541:    best_xy = MAX32(0, best_xy);
	movgez	a2, a12, a12	# best_xy, xy02, xy02
# @OPUS@\upstream\celt\pitch.c:542:    if (best_yy <= best_xy)
	bge	a2, a5, .L201	# best_xy,,
# @OPUS@\upstream\celt\pitch.c:545:       pg = SHR32(frac_div32(best_xy,best_yy+1),16);
	addi.n	a3, a5, 1	#,,
	call0	frac_div32		#
	l32i	a6, sp, 80	# %sfp,
	srai	a2, a2, 16	# tmp377,,
	slli	a3, a6, 16	# tmp382,,
	srai	a3, a3, 16	# tmp381, tmp382,
	mov.n	a4, a2	# <retval>, tmp377
	bge	a3, a2, .L202	# tmp381, tmp377,
	mov.n	a4, a6	# <retval>,
.L202:
	slli	a4, a4, 16	# tmp383, <retval>,
	srai	a4, a4, 16	#, tmp383,
	s32i	a4, sp, 80	# %sfp,
.L201:
	l32i	a9, sp, 92	# %sfp,
	l32i.n	a11, sp, 52	# %sfp, x
	slli	a7, a9, 1	# tmp386,,
	l32i.n	a10, sp, 40	# %sfp, N
	mov.n	a8, sp	# ivtmp$227,
	neg	a7, a7	# ivtmp$228, tmp386
	addi.n	a9, sp, 12	# _558,,
.L205:
# @OPUS@\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a5, 0	# xy,
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	blti	a10, 2, .L203	# N,,
	mov.n	a2, a11	# ivtmp$218, x
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	mov.n	a4, a5	# i, xy
.L204:
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a3, a2, a7	# tmp388, ivtmp$218, ivtmp$228
	l16ui	a6, a2, 0	# MEM[base: _583, offset: 0B],
	l16ui	a3, a3, 2	# MEM[base: _580, offset: 2B],
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	addi.n	a4, a4, 1	# i, i,
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	mul16s	a3, a3, a6	# tmp389, MEM[base: _580, offset: 2B], MEM[base: _583, offset: 0B]
	addi.n	a2, a2, 2	# ivtmp$218, ivtmp$218,
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a5, a5, a3	# xy, xy, tmp389
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	blt	a4, a13, .L204	# i, N,
.L203:
# @OPUS@\upstream\celt\pitch.c:548:       xcorr[k] = celt_inner_prod(x, x-(T+k-1), N, arch);
	s32i.n	a5, a8, 0	# MEM[base: _560, offset: 0B], xy
	addi.n	a8, a8, 4	# ivtmp$227, ivtmp$227,
	addi	a7, a7, -2	# ivtmp$228, ivtmp$228,
# @OPUS@\upstream\celt\pitch.c:547:    for (k=0;k<3;k++)
	bne	a9, a8, .L205	# _558, ivtmp$227,
# @OPUS@\upstream\celt\pitch.c:549:    if ((xcorr[2]-xcorr[0]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[0]))
	l32i.n	a4, sp, 0	# xcorr, _86
# @OPUS@\upstream\celt\pitch.c:549:    if ((xcorr[2]-xcorr[0]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[0]))
	l32i.n	a3, sp, 4	# xcorr, _88
	l16si	a5, sp, 4	# xcorr, _97
	l32r	a7, .LC10	#, tmp397
	sub	a2, a3, a4	# tmp394, _88, _86
	srai	a2, a2, 16	# tmp395, tmp394,
	sub	a6, a5, a4	# tmp400, _97, _86
	mull	a2, a2, a7	# tmp396, tmp395, tmp397
	mul16u	a6, a6, a7	# tmp401, tmp400, tmp397
# @OPUS@\upstream\celt\pitch.c:549:    if ((xcorr[2]-xcorr[0]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[0]))
	l32i.n	a8, sp, 8	# xcorr, _85
# @OPUS@\upstream\celt\pitch.c:549:    if ((xcorr[2]-xcorr[0]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[0]))
	srai	a6, a6, 15	# tmp403, tmp401,
	slli	a2, a2, 1	# tmp398, tmp396,
	add.n	a2, a2, a6	# tmp404, tmp398, tmp403
# @OPUS@\upstream\celt\pitch.c:549:    if ((xcorr[2]-xcorr[0]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[0]))
	sub	a9, a8, a4	# tmp393, _85, _86
# @OPUS@\upstream\celt\pitch.c:550:       offset = 1;
	movi.n	a6, 1	# offset,
# @OPUS@\upstream\celt\pitch.c:549:    if ((xcorr[2]-xcorr[0]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[0]))
	blt	a2, a9, .L206	# tmp404, tmp393,
# @OPUS@\upstream\celt\pitch.c:551:    else if ((xcorr[0]-xcorr[2]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[2]))
	sub	a2, a3, a8	# tmp406, _88, _85
	srai	a2, a2, 16	# tmp407, tmp406,
	sub	a3, a5, a8	# tmp412, _97, _85
	mull	a2, a2, a7	# tmp408, tmp407, tmp397
	mul16u	a3, a3, a7	# tmp413, tmp412, tmp397
	ssl	a6	#
	sll	a2, a2	# tmp410, tmp408
	srai	a3, a3, 15	# tmp415, tmp413,
# @OPUS@\upstream\celt\pitch.c:551:    else if ((xcorr[0]-xcorr[2]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[2]))
	sub	a8, a4, a8	# tmp405, _86, _85
# @OPUS@\upstream\celt\pitch.c:551:    else if ((xcorr[0]-xcorr[2]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[2]))
	add.n	a2, a2, a3	# tmp416, tmp410, tmp415
# @OPUS@\upstream\celt\pitch.c:551:    else if ((xcorr[0]-xcorr[2]) > MULT16_32_Q15(QCONST16(.7f,15),xcorr[1]-xcorr[2]))
	mov.n	a4, a6	# tmp417, offset
	blt	a2, a8, .L207	# tmp416, tmp405,
	movi.n	a4, 0	# tmp417,
.L207:
	neg	a6, a4	# offset, tmp417
.L206:
# @OPUS@\upstream\celt\pitch.c:557:    *T0_ = 2*T+offset;
	l32i	a5, sp, 92	# %sfp,
	slli	a4, a5, 1	# tmp419,,
# @OPUS@\upstream\celt\pitch.c:557:    *T0_ = 2*T+offset;
	add.n	a4, a4, a6	# minperiod, tmp419, offset
	l32i	a6, sp, 112	# %sfp,
	bge	a4, a6, .L208	# minperiod,,
	mov.n	a4, a6	# minperiod,
	j	.L208		#
.L227:
	mov.n	a6, a5	#,
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	l32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	movi.n	a9, 1	#,
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	slli	a2, a5, 2	# tmp423,,
	add.n	a2, a6, a2	#,, tmp423
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	l32i.n	a7, a2, 0	# *_204,
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	s32i	a2, sp, 120	# %sfp,
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	s32i	a7, sp, 84	# %sfp,
	s32i	a9, sp, 64	# %sfp,
# @OPUS@\upstream\celt\pitch.h:141:    opus_val32 xy01=0;
	s32i.n	a12, sp, 60	# %sfp, xy02
# @OPUS@\upstream\celt\pitch.c:491:    yy = yy_lookup[T0];
	s32i	a12, sp, 108	# %sfp, xy02
	s32i	a12, sp, 104	# %sfp, xy02
	s32i	a12, sp, 76	# %sfp, xy02
# @OPUS@\upstream\celt\pitch.c:429:       return 0;
	s32i	a12, sp, 80	# %sfp, xy02
	j	.L182		#
.L179:
# @OPUS@\upstream\celt\pitch.c:484:    yy_lookup[0] = xx;
	movi.n	a12, 0	# tmp424,
	s32i.n	a12, a2, 0	# *yy_lookup_166, tmp424
	mov.n	a5, a2	#,
# @OPUS@\upstream\celt\pitch.c:486:    for (i=1;i<=maxperiod;i++)
	bgei	a14, 2, .L218	# maxperiod,,
	j	.L227		#
.L208:
	l32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\celt\pitch.c:561:    RESTORE_STACK;
	l32i.n	a2, sp, 12	# _saved_stack,
	l32i.n	a3, sp, 16	# _saved_stack,
	s32i.n	a4, a9, 0	# MEM[(void *)T0__154(D)], minperiod
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\pitch.c:563: }
	l32i	a0, sp, 172	#,
	movi	a9, 0xb0	#,
	l32i	a2, sp, 80	# %sfp,
	l32i	a12, sp, 168	#,
	l32i	a13, sp, 164	#,
	l32i	a14, sp, 160	#,
	l32i	a15, sp, 156	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	remove_doubling, .-remove_doubling
	.section	.rodata.second_check,"a"
	.align	4
	.type	second_check, @object
	.size	second_check, 64
second_check:
	.word	0
	.word	0
	.word	3
	.word	2
	.word	3
	.word	2
	.word	5
	.word	2
	.word	3
	.word	2
	.word	3
	.word	2
	.word	5
	.word	2
	.word	3
	.word	2
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
