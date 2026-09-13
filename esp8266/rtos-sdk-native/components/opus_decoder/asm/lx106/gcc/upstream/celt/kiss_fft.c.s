# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/kiss_fft.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"kiss_fft.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\kiss_fft.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\kiss_fft.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\kiss_fft.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\kiss_fft.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\kiss_fft.c.s.raw
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
	.section	.text.opus_fft_impl,"ax",@progbits
	.literal_position
	.literal .LC0, 23170
	.literal .LC1, -28378
	.literal .LC2, 10126
	.literal .LC3, -26510
	.literal .LC4, -31164
	.literal .LC5, -19261
	.align	4
	.global	opus_fft_impl
	.type	opus_fft_impl, @function
# Function: opus_fft_impl
# Module: upstream/celt/kiss_fft.c
# Fixed-point FFT used by CELT inverse transforms.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #endif /* CUSTOM_MODES */
# C context:
# C context: void opus_fft_impl(const kiss_fft_state *st,kiss_fft_cpx *fout)
# C context: {
# C context: int m2, m;
# C context: int p;
# C context: int L;
opus_fft_impl:
	movi	a9, 0x120	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\celt\kiss_fft.c:544:     shift = st->shift>0 ? st->shift : 0;
	l32i.n	a4, a2, 12	# st_37(D)->shift, st_37(D)->shift
# @OPUS@\upstream\celt\kiss_fft.c:535: {
	s32i	a3, sp, 244	# %sfp, fout
# @OPUS@\upstream\celt\kiss_fft.c:544:     shift = st->shift>0 ? st->shift : 0;
	movi.n	a3, 0	# tmp1177,
	movgez	a3, a4, a4	# tmp1177, st_37(D)->shift, st_37(D)->shift
	s32i	a3, sp, 248	# %sfp, tmp1177
# @OPUS@\upstream\celt\kiss_fft.c:546:     fstride[0] = 1;
	movi.n	a3, 1	# tmp1178,
# @OPUS@\upstream\celt\kiss_fft.c:535: {
	s32i	a2, sp, 160	# %sfp, st
# @OPUS@\upstream\celt\kiss_fft.c:546:     fstride[0] = 1;
	s32i.n	a3, sp, 0	# fstride, tmp1178
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	addi	a2, a2, 16	# address, st,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a3, -4	# tmp1180,
# @OPUS@\upstream\celt\kiss_fft.c:535: {
	s32i	a12, sp, 284	#,
	s32i	a13, sp, 280	#,
	s32i	a14, sp, 276	#,
	s32i	a15, sp, 272	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a3, a2, a3	# tmp1181, address, tmp1180
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1181
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a2, 1, .L2	# address,,
	j	.L77		#
.L2:
	slli	a3, a3, 16	# tmp1186, value,
.L77:
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	l32i	a2, sp, 160	# %sfp,
	srai	a3, a3, 16	# iftmp$0_1552, tmp1186,
	addi	a4, a2, 18	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1188,
	and	a2, a4, a2	# tmp1189, address, tmp1188
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1189
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a4, 1, .L4	# address,,
	j	.L78		#
.L4:
	slli	a2, a2, 16	# tmp1194, value,
.L78:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	l32i.n	a4, sp, 0	# fstride, fstride
	srai	a2, a2, 16	# iftmp$0_1515, tmp1194,
	mull	a3, a4, a3	# tmp1195, fstride, iftmp$0_1552
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i.n	a3, sp, 4	# fstride, tmp1195
# @OPUS@\upstream\celt\kiss_fft.c:553:     } while(m!=1);
	beqi	a2, 1, .L57	# iftmp$0_1515,,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	l32i	a4, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a3, -4	# tmp1198,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	addi	a2, a4, 20	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a3, a2, a3	# tmp1199, address, tmp1198
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1199
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a2, 1, .L7	# address,,
	j	.L79		#
.L7:
	slli	a3, a3, 16	# tmp1204, value,
.L79:
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	l32i	a5, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1206,
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	addi	a4, a5, 22	# address,,
	srai	a3, a3, 16	# iftmp$0_1475, tmp1204,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a2, a4, a2	# tmp1207, address, tmp1206
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1207
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a4, 1, .L9	# address,,
	j	.L80		#
.L9:
	slli	a2, a2, 16	# tmp1212, value,
.L80:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	l32i.n	a4, sp, 4	# fstride, fstride
	srai	a2, a2, 16	# iftmp$0_1460, tmp1212,
	mull	a3, a4, a3	# tmp1213, fstride, iftmp$0_1475
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i.n	a3, sp, 8	# fstride, tmp1213
# @OPUS@\upstream\celt\kiss_fft.c:553:     } while(m!=1);
	beqi	a2, 1, .L58	# iftmp$0_1460,,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	l32i	a6, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a3, -4	# tmp1216,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	addi	a2, a6, 24	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a3, a2, a3	# tmp1217, address, tmp1216
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1217
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a2, 1, .L11	# address,,
	j	.L81		#
.L11:
	slli	a3, a3, 16	# tmp1222, value,
.L81:
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	l32i	a7, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1224,
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	addi	a4, a7, 26	# address,,
	srai	a3, a3, 16	# iftmp$0_1440, tmp1222,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a2, a4, a2	# tmp1225, address, tmp1224
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1225
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a4, 1, .L13	# address,,
	j	.L82		#
.L13:
	slli	a2, a2, 16	# tmp1230, value,
.L82:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	l32i.n	a4, sp, 8	# fstride, fstride
	srai	a2, a2, 16	# iftmp$0_1425, tmp1230,
	mull	a3, a4, a3	# tmp1231, fstride, iftmp$0_1440
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i.n	a3, sp, 12	# fstride, tmp1231
# @OPUS@\upstream\celt\kiss_fft.c:553:     } while(m!=1);
	beqi	a2, 1, .L59	# iftmp$0_1425,,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	l32i	a8, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1234,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	addi	a3, a8, 28	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a2, a3, a2	# tmp1235, address, tmp1234
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1235
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a3, 1, .L15	# address,,
	j	.L83		#
.L15:
	slli	a2, a2, 16	# tmp1240, value,
.L83:
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	l32i	a9, sp, 160	# %sfp,
	srai	a3, a2, 16	# iftmp$0_1405, tmp1240,
	addi	a4, a9, 30	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1242,
	and	a2, a4, a2	# tmp1243, address, tmp1242
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1243
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a4, 1, .L17	# address,,
	j	.L84		#
.L17:
	slli	a2, a2, 16	# tmp1248, value,
.L84:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	l32i.n	a4, sp, 12	# fstride, fstride
	srai	a2, a2, 16	# iftmp$0_1390, tmp1248,
	mull	a3, a4, a3	# tmp1249, fstride, iftmp$0_1405
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i.n	a3, sp, 16	# fstride, tmp1249
# @OPUS@\upstream\celt\kiss_fft.c:553:     } while(m!=1);
	beqi	a2, 1, .L60	# iftmp$0_1390,,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	l32i	a10, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a3, -4	# tmp1252,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	addi	a2, a10, 32	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a3, a2, a3	# tmp1253, address, tmp1252
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1253
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a2, 1, .L19	# address,,
	j	.L85		#
.L19:
	slli	a3, a3, 16	# tmp1258, value,
.L85:
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	l32i	a11, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1260,
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	addi	a4, a11, 34	# address,,
	srai	a3, a3, 16	# iftmp$0_1370, tmp1258,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a2, a4, a2	# tmp1261, address, tmp1260
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1261
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a4, 1, .L21	# address,,
	j	.L86		#
.L21:
	slli	a2, a2, 16	# tmp1266, value,
.L86:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	l32i.n	a4, sp, 16	# fstride, fstride
	srai	a2, a2, 16	# iftmp$0_1355, tmp1266,
	mull	a3, a4, a3	# tmp1267, fstride, iftmp$0_1370
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i.n	a3, sp, 20	# fstride, tmp1267
# @OPUS@\upstream\celt\kiss_fft.c:553:     } while(m!=1);
	beqi	a2, 1, .L61	# iftmp$0_1355,,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	l32i	a12, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a3, -4	# tmp1270,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	addi	a2, a12, 36	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a3, a2, a3	# tmp1271, address, tmp1270
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1271
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a2, 1, .L23	# address,,
	j	.L87		#
.L23:
	slli	a3, a3, 16	# tmp1276, value,
.L87:
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	l32i	a14, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1278,
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	addi	a4, a14, 38	# address,,
	srai	a3, a3, 16	# iftmp$0_1335, tmp1276,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a2, a4, a2	# tmp1279, address, tmp1278
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1279
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a4, 1, .L25	# address,,
	j	.L88		#
.L25:
	slli	a2, a2, 16	# tmp1284, value,
.L88:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	l32i.n	a4, sp, 20	# fstride, fstride
	srai	a2, a2, 16	# iftmp$0_1320, tmp1284,
	mull	a3, a4, a3	# tmp1285, fstride, iftmp$0_1335
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i.n	a3, sp, 24	# fstride, tmp1285
# @OPUS@\upstream\celt\kiss_fft.c:553:     } while(m!=1);
	beqi	a2, 1, .L62	# iftmp$0_1320,,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	l32i	a2, sp, 160	# %sfp,
	addi	a3, a2, 40	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1288,
	and	a2, a3, a2	# tmp1289, address, tmp1288
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1289
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a3, 1, .L27	# address,,
	j	.L89		#
.L27:
	slli	a2, a2, 16	# tmp1294, value,
.L89:
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
	l32i	a5, sp, 160	# %sfp,
	srai	a3, a2, 16	# iftmp$0_1300, tmp1294,
	addi	a4, a5, 42	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	# tmp1296,
	and	a2, a4, a2	# tmp1297, address, tmp1296
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1297
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a4, 1, .L29	# address,,
	j	.L90		#
.L29:
	slli	a2, a2, 16	# tmp1302, value,
.L90:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	l32i.n	a4, sp, 24	# fstride, fstride
	srai	a2, a2, 16	# iftmp$0_1285, tmp1302,
	mull	a3, a4, a3	# tmp1303, fstride, iftmp$0_1300
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i.n	a3, sp, 28	# fstride, tmp1303
# @OPUS@\upstream\celt\kiss_fft.c:553:     } while(m!=1);
	beqi	a2, 1, .L63	# iftmp$0_1285,,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	l32i	a6, sp, 160	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a4, -4	# tmp1307,
# @OPUS@\upstream\celt\kiss_fft.c:549:        p = FFT_TABLE16(st->factors[2*L]);
	addi	a3, a6, 44	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a3, a3, a4	# tmp1308, address, tmp1307
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1308
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:550:        m = FFT_TABLE16(st->factors[2*L+1]);
#NO_APP
	addi	a2, a6, 46	# address,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a2, a2, a4	# tmp1312, address, tmp1307
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1312
# 0 "" 2
#NO_APP
.L57:
# @OPUS@\upstream\celt\kiss_fft.c:547:     L=0;
	movi.n	a7, 0	#,
	s32i	a7, sp, 128	# %sfp,
	j	.L6		#
.L58:
# @OPUS@\upstream\celt\kiss_fft.c:551:        fstride[L+1] = fstride[L]*p;
	s32i	a2, sp, 128	# %sfp, iftmp$0_1460
	movi.n	a2, 2	# _822,
	j	.L6		#
.L59:
	movi.n	a8, 2	#,
	s32i	a8, sp, 128	# %sfp,
	movi.n	a2, 3	# _822,
	j	.L6		#
.L60:
	movi.n	a9, 3	#,
	s32i	a9, sp, 128	# %sfp,
	movi.n	a2, 4	# _822,
	j	.L6		#
.L61:
	movi.n	a10, 4	#,
	s32i	a10, sp, 128	# %sfp,
	movi.n	a2, 5	# _822,
	j	.L6		#
.L62:
	movi.n	a11, 5	#,
	s32i	a11, sp, 128	# %sfp,
	movi.n	a2, 6	# _822,
	j	.L6		#
.L63:
	movi.n	a12, 6	#,
	s32i	a12, sp, 128	# %sfp,
	movi.n	a2, 7	# _822,
.L6:
# @OPUS@\upstream\celt\kiss_fft.c:554:     m = FFT_TABLE16(st->factors[2*L-1]);
	l32i	a14, sp, 160	# %sfp,
	slli	a2, a2, 2	# tmp1314, _822,
	addi.n	a2, a2, 14	# tmp1315, tmp1314,
	add.n	a2, a14, a2	# address,, tmp1315
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a3, -4	# tmp1317,
	and	a3, a2, a3	# tmp1318, address, tmp1317
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a3, 0	# value, tmp1318
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bbci	a2, 1, .L31	# address,,
	srai	a2, a3, 16	# _75, value,
	j	.L32		#
.L31:
	slli	a2, a3, 16	# tmp1323, value,
	srai	a2, a2, 16	# _75, tmp1323,
.L32:
	l32i	a4, sp, 128	# %sfp,
	l32i	a5, sp, 160	# %sfp,
	slli	a3, a4, 2	# tmp1324,,
	addi	a3, a3, 16	# tmp1325, tmp1324,
	add.n	a3, a5, a3	#,, tmp1325
# @OPUS@\upstream\celt\kiss_fft.c:554:     m = FFT_TABLE16(st->factors[2*L-1]);
	s32i.n	a2, sp, 56	# %sfp, _75
	s32i	a3, sp, 132	# %sfp,
.L56:
# @OPUS@\upstream\celt\kiss_fft.c:560:           m2 = 1;
	movi.n	a6, 1	#,
# @OPUS@\upstream\celt\kiss_fft.c:557:        if (i!=0)
	l32i	a7, sp, 128	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:560:           m2 = 1;
	s32i	a6, sp, 176	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:557:        if (i!=0)
	beqz.n	a7, .L33	#,
	l32i	a8, sp, 132	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a9, -4	#,
	addi	a3, a8, -2	# _35,,
	and	a2, a3, a9	# tmp1328, _35,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1328
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	movi.n	a10, 2	#,
	bnone	a3, a10, .L34	# _35,,
	j	.L91		#
.L34:
	slli	a2, a2, 16	# tmp1333, value,
.L91:
	srai	a2, a2, 16	# _83, tmp1333,
# @OPUS@\upstream\celt\kiss_fft.c:558:           m2 = FFT_TABLE16(st->factors[2*i-1]);
	s32i	a2, sp, 176	# %sfp, _83
.L33:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	l32i	a11, sp, 132	# %sfp,
	movi.n	a12, -4	#,
	and	a2, a11, a12	# tmp1336,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a2, 0	# value, tmp1336
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	movi.n	a14, 2	#,
	bnone	a11, a14, .L36	#,,
	j	.L92		#
.L36:
	slli	a2, a2, 16	# tmp1341, value,
.L92:
	srai	a2, a2, 16	# _91, tmp1341,
# @OPUS@\upstream\celt\kiss_fft.c:561:        switch (FFT_TABLE16(st->factors[2*i]))
	beqi	a2, 3, .L38	# _91,,
	bgei	a2, 4, .L39	# _91,,
	beqi	a2, 2, .L40	# _91,,
	j	.L41		#
.L39:
	beqi	a2, 4, .L42	# _91,,
	beqi	a2, 5, .L43	# _91,,
	j	.L41		#
.L40:
# @OPUS@\upstream\celt\kiss_fft.c:564:           kf_bfly2(fout, m, fstride[i]);
	l32i	a3, sp, 128	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:90:       for (i=0;i<N;i++)
	l32i	a12, sp, 244	# %sfp, Fout
# @OPUS@\upstream\celt\kiss_fft.c:564:           kf_bfly2(fout, m, fstride[i]);
	slli	a2, a3, 2	# tmp1342,,
	add.n	a2, sp, a2	# tmp1343,, tmp1342
	l32i.n	a2, a2, 0	# MEM[base: _4, offset: 0B],
# @OPUS@\upstream\celt\kiss_fft.c:90:       for (i=0;i<N;i++)
	movi.n	a11, 0	# i,
# @OPUS@\upstream\celt\kiss_fft.c:564:           kf_bfly2(fout, m, fstride[i]);
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:90:       for (i=0;i<N;i++)
	blti	a2, 1, .L41	#,,
.L44:
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	l32i.n	a9, a12, 60	# MEM[base: Fout_525, offset: 60B], _182
	l32i.n	a2, a12, 56	# MEM[base: Fout_525, offset: 56B], _184
# @OPUS@\upstream\celt\kiss_fft.c:98:          t.r = S_MUL(ADD32_ovflw(Fout2[1].r, Fout2[1].i), tw);
	l32i.n	a10, a12, 44	# MEM[base: Fout_525, offset: 44B], _119
	l32i.n	a5, a12, 40	# MEM[base: Fout_525, offset: 40B], _117
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	extui	a7, a2, 0, 16	# _196, _184
	extui	a13, a9, 0, 16	# _195, _182
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	add.n	a3, a9, a2	# tmp1384, _182, _184
# @OPUS@\upstream\celt\kiss_fft.c:98:          t.r = S_MUL(ADD32_ovflw(Fout2[1].r, Fout2[1].i), tw);
	extui	a8, a5, 0, 16	# _130, _117
	extui	a4, a10, 0, 16	# _131, _119
	add.n	a6, a5, a10	# tmp1348, _117, _119
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	add.n	a14, a13, a7	# tmp1390, _195, _196
# @OPUS@\upstream\celt\kiss_fft.c:99:          t.i = S_MUL(SUB32_ovflw(Fout2[1].i, Fout2[1].r), tw);
	sub	a5, a10, a5	# tmp1358, _119, _117
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	sub	a13, a13, a7	# tmp1379, _195, _196
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	neg	a3, a3	# tmp1385, tmp1384
# @OPUS@\upstream\celt\kiss_fft.c:98:          t.r = S_MUL(ADD32_ovflw(Fout2[1].r, Fout2[1].i), tw);
	l32r	a7, .LC0	#,
	add.n	a15, a8, a4	# tmp1353, _130, _131
# @OPUS@\upstream\celt\kiss_fft.c:99:          t.i = S_MUL(SUB32_ovflw(Fout2[1].i, Fout2[1].r), tw);
	srai	a5, a5, 16	# tmp1359, tmp1358,
	sub	a4, a4, a8	# tmp1363, _131, _130
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	srai	a3, a3, 16	# tmp1386, tmp1385,
	neg	a14, a14	# tmp1392, tmp1390
# @OPUS@\upstream\celt\kiss_fft.c:99:          t.i = S_MUL(SUB32_ovflw(Fout2[1].i, Fout2[1].r), tw);
	mull	a5, a5, a7	# tmp1360, tmp1359, tmp8
	mul16u	a4, a4, a7	# tmp1364, tmp1363, tmp8
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	mull	a3, a3, a7	# tmp1387, tmp1386, tmp10
	mul16u	a14, a14, a7	# tmp1393, tmp1392, tmp10
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	sub	a2, a9, a2	# tmp1374, _182, _184
# @OPUS@\upstream\celt\kiss_fft.c:98:          t.r = S_MUL(ADD32_ovflw(Fout2[1].r, Fout2[1].i), tw);
	srai	a6, a6, 16	# tmp1349, tmp1348,
	mull	a6, a6, a7	# tmp1350, tmp1349,
	mul16u	a15, a15, a7	# tmp1354, tmp1353,
# @OPUS@\upstream\celt\kiss_fft.c:99:          t.i = S_MUL(SUB32_ovflw(Fout2[1].i, Fout2[1].r), tw);
	slli	a5, a5, 1	# tmp1362, tmp1360,
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	srai	a14, a14, 15	# tmp1395, tmp1393,
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	srai	a2, a2, 16	# tmp1375, tmp1374,
# @OPUS@\upstream\celt\kiss_fft.c:99:          t.i = S_MUL(SUB32_ovflw(Fout2[1].i, Fout2[1].r), tw);
	srai	a4, a4, 15	# tmp1366, tmp1364,
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	slli	a3, a3, 1	# tmp1389, tmp1387,
# @OPUS@\upstream\celt\kiss_fft.c:95:          C_SUB( Fout2[0] ,  Fout[0] , t );
	l32i.n	a8, a12, 32	# MEM[base: Fout_525, offset: 32B], _105
# @OPUS@\upstream\celt\kiss_fft.c:99:          t.i = S_MUL(SUB32_ovflw(Fout2[1].i, Fout2[1].r), tw);
	add.n	a4, a5, a4	# _158, tmp1362, tmp1366
# @OPUS@\upstream\celt\kiss_fft.c:109:          t.i = S_MUL(NEG32_ovflw(ADD32_ovflw(Fout2[3].i, Fout2[3].r)), tw);
	add.n	a3, a3, a14	# _225, tmp1389, tmp1395
# @OPUS@\upstream\celt\kiss_fft.c:95:          C_SUB( Fout2[0] ,  Fout[0] , t );
	l32i.n	a5, a12, 36	# MEM[base: Fout_525, offset: 36B],
	l32i.n	a14, a12, 0	# MEM[base: Fout_525, offset: 0B],
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	mull	a2, a2, a7	# tmp1376, tmp1375, tmp9
	mul16u	a13, a13, a7	# tmp1380, tmp1379, tmp9
# @OPUS@\upstream\celt\kiss_fft.c:95:          C_SUB( Fout2[0] ,  Fout[0] , t );
	l32i.n	a7, a12, 4	# MEM[base: Fout_525, offset: 4B], _109
# @OPUS@\upstream\celt\kiss_fft.c:98:          t.r = S_MUL(ADD32_ovflw(Fout2[1].r, Fout2[1].i), tw);
	srai	a15, a15, 15	# tmp1356, tmp1354,
	slli	a6, a6, 1	# tmp1352, tmp1350,
	add.n	a6, a6, a15	# _153, tmp1352, tmp1356
# @OPUS@\upstream\celt\kiss_fft.c:95:          C_SUB( Fout2[0] ,  Fout[0] , t );
	sub	a15, a14, a8	# tmp1344,, _105
	sub	a14, a7, a5	# tmp1345, _109,
# @OPUS@\upstream\celt\kiss_fft.c:96:          C_ADDTO( Fout[0] ,  t );
	l32i.n	a5, a12, 0	# MEM[base: Fout_525, offset: 0B],
# @OPUS@\upstream\celt\kiss_fft.c:100:          C_SUB( Fout2[1] ,  Fout[1] , t );
	l32i.n	a9, a12, 12	# MEM[base: Fout_525, offset: 12B], _157
# @OPUS@\upstream\celt\kiss_fft.c:96:          C_ADDTO( Fout[0] ,  t );
	add.n	a8, a5, a8	#,, _105
	s32i.n	a8, a12, 0	# MEM[base: Fout_525, offset: 0B],
	l32i.n	a8, a12, 36	# MEM[base: Fout_525, offset: 36B],
# @OPUS@\upstream\celt\kiss_fft.c:100:          C_SUB( Fout2[1] ,  Fout[1] , t );
	sub	a5, a9, a4	#, _157, _158
	l32i.n	a10, a12, 8	# MEM[base: Fout_525, offset: 8B], _152
	s32i.n	a5, a12, 44	# MEM[base: Fout_525, offset: 44B],
# @OPUS@\upstream\celt\kiss_fft.c:96:          C_ADDTO( Fout[0] ,  t );
	add.n	a7, a7, a8	# tmp1347, _109,
# @OPUS@\upstream\celt\kiss_fft.c:101:          C_ADDTO( Fout[1] ,  t );
	add.n	a5, a9, a4	# tmp1369, _157, _158
# @OPUS@\upstream\celt\kiss_fft.c:105:          C_SUB( Fout2[2] ,  Fout[2] , t );
	l32i.n	a8, a12, 16	# MEM[base: Fout_525, offset: 16B],
	l32i.n	a9, a12, 52	# MEM[base: Fout_525, offset: 52B],
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	srai	a13, a13, 15	# tmp1382, tmp1380,
	slli	a2, a2, 1	# tmp1378, tmp1376,
# @OPUS@\upstream\celt\kiss_fft.c:105:          C_SUB( Fout2[2] ,  Fout[2] , t );
	l32i.n	a4, a12, 20	# MEM[base: Fout_525, offset: 20B],
# @OPUS@\upstream\celt\kiss_fft.c:108:          t.r = S_MUL(SUB32_ovflw(Fout2[3].i, Fout2[3].r), tw);
	add.n	a2, a2, a13	# _220, tmp1378, tmp1382
# @OPUS@\upstream\celt\kiss_fft.c:100:          C_SUB( Fout2[1] ,  Fout[1] , t );
	sub	a13, a10, a6	# tmp1357, _152, _153
# @OPUS@\upstream\celt\kiss_fft.c:101:          C_ADDTO( Fout[1] ,  t );
	add.n	a6, a10, a6	# tmp1368, _152, _153
# @OPUS@\upstream\celt\kiss_fft.c:105:          C_SUB( Fout2[2] ,  Fout[2] , t );
	sub	a10, a8, a9	# tmp1370,,
	l32i.n	a8, a12, 48	# MEM[base: Fout_525, offset: 48B],
# @OPUS@\upstream\celt\kiss_fft.c:95:          C_SUB( Fout2[0] ,  Fout[0] , t );
	s32i.n	a14, a12, 36	# MEM[base: Fout_525, offset: 36B], tmp1345
# @OPUS@\upstream\celt\kiss_fft.c:105:          C_SUB( Fout2[2] ,  Fout[2] , t );
	add.n	a4, a4, a8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:106:          C_ADDTO( Fout[2] ,  t );
	l32i.n	a8, a12, 16	# MEM[base: Fout_525, offset: 16B],
# @OPUS@\upstream\celt\kiss_fft.c:105:          C_SUB( Fout2[2] ,  Fout[2] , t );
	s32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:106:          C_ADDTO( Fout[2] ,  t );
	add.n	a4, a8, a9	# tmp1372,,
	l32i.n	a9, a12, 20	# MEM[base: Fout_525, offset: 20B],
	l32i.n	a8, a12, 48	# MEM[base: Fout_525, offset: 48B],
# @OPUS@\upstream\celt\kiss_fft.c:95:          C_SUB( Fout2[0] ,  Fout[0] , t );
	s32i.n	a15, a12, 32	# MEM[base: Fout_525, offset: 32B], tmp1344
# @OPUS@\upstream\celt\kiss_fft.c:106:          C_ADDTO( Fout[2] ,  t );
	sub	a9, a9, a8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:110:          C_SUB( Fout2[3] ,  Fout[3] , t );
	l32i.n	a8, a12, 24	# MEM[base: Fout_525, offset: 24B],
# @OPUS@\upstream\celt\kiss_fft.c:106:          C_ADDTO( Fout[2] ,  t );
	s32i.n	a9, a12, 20	# MEM[base: Fout_525, offset: 20B],
# @OPUS@\upstream\celt\kiss_fft.c:110:          C_SUB( Fout2[3] ,  Fout[3] , t );
	sub	a9, a8, a2	# tmp1383,, _220
	l32i.n	a8, a12, 28	# MEM[base: Fout_525, offset: 28B],
# @OPUS@\upstream\celt\kiss_fft.c:96:          C_ADDTO( Fout[0] ,  t );
	s32i.n	a7, a12, 4	# MEM[base: Fout_525, offset: 4B], tmp1347
# @OPUS@\upstream\celt\kiss_fft.c:110:          C_SUB( Fout2[3] ,  Fout[3] , t );
	sub	a8, a8, a3	#,, _225
	s32i.n	a8, a12, 60	# MEM[base: Fout_525, offset: 60B],
# @OPUS@\upstream\celt\kiss_fft.c:111:          C_ADDTO( Fout[3] ,  t );
	l32i.n	a8, a12, 24	# MEM[base: Fout_525, offset: 24B],
# @OPUS@\upstream\celt\kiss_fft.c:90:       for (i=0;i<N;i++)
	addi.n	a11, a11, 1	# i, i,
# @OPUS@\upstream\celt\kiss_fft.c:111:          C_ADDTO( Fout[3] ,  t );
	add.n	a2, a8, a2	# tmp1397,, _220
	l32i.n	a8, a12, 28	# MEM[base: Fout_525, offset: 28B],
# @OPUS@\upstream\celt\kiss_fft.c:100:          C_SUB( Fout2[1] ,  Fout[1] , t );
	s32i.n	a13, a12, 40	# MEM[base: Fout_525, offset: 40B], tmp1357
# @OPUS@\upstream\celt\kiss_fft.c:105:          C_SUB( Fout2[2] ,  Fout[2] , t );
	s32i.n	a10, a12, 48	# MEM[base: Fout_525, offset: 48B], tmp1370
	l32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:111:          C_ADDTO( Fout[3] ,  t );
	add.n	a3, a8, a3	# tmp1398,, _225
# @OPUS@\upstream\celt\kiss_fft.c:90:       for (i=0;i<N;i++)
	l32i.n	a14, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:101:          C_ADDTO( Fout[1] ,  t );
	s32i.n	a6, a12, 8	# MEM[base: Fout_525, offset: 8B], tmp1368
	s32i.n	a5, a12, 12	# MEM[base: Fout_525, offset: 12B], tmp1369
# @OPUS@\upstream\celt\kiss_fft.c:105:          C_SUB( Fout2[2] ,  Fout[2] , t );
	s32i.n	a10, a12, 52	# MEM[base: Fout_525, offset: 52B],
# @OPUS@\upstream\celt\kiss_fft.c:106:          C_ADDTO( Fout[2] ,  t );
	s32i.n	a4, a12, 16	# MEM[base: Fout_525, offset: 16B], tmp1372
# @OPUS@\upstream\celt\kiss_fft.c:110:          C_SUB( Fout2[3] ,  Fout[3] , t );
	s32i.n	a9, a12, 56	# MEM[base: Fout_525, offset: 56B], tmp1383
# @OPUS@\upstream\celt\kiss_fft.c:111:          C_ADDTO( Fout[3] ,  t );
	s32i.n	a2, a12, 24	# MEM[base: Fout_525, offset: 24B], tmp1397
	s32i.n	a3, a12, 28	# MEM[base: Fout_525, offset: 28B], tmp1398
# @OPUS@\upstream\celt\kiss_fft.c:112:          Fout += 8;
	addi	a12, a12, 64	# Fout, Fout,
# @OPUS@\upstream\celt\kiss_fft.c:90:       for (i=0;i<N;i++)
	bne	a14, a11, .L44	#, i,
	j	.L41		#
.L42:
# @OPUS@\upstream\celt\kiss_fft.c:567:           kf_bfly4(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i	a3, sp, 128	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:128:    if (m==1)
	l32i.n	a4, sp, 56	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:567:           kf_bfly4(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	slli	a2, a3, 2	# tmp1399,,
	add.n	a2, sp, a2	# tmp1400,, tmp1399
	l32i.n	a2, a2, 0	# MEM[base: _1568, offset: 0B],
	s32i	a2, sp, 88	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:128:    if (m==1)
	bnei	a4, 1, .L46	#,,
# @OPUS@\upstream\celt\kiss_fft.c:131:       for (i=0;i<N;i++)
	blti	a2, 1, .L41	#,,
	l32i	a9, sp, 244	# %sfp, Fout
# @OPUS@\upstream\celt\kiss_fft.c:131:       for (i=0;i<N;i++)
	movi.n	a8, 0	# i,
.L47:
# @OPUS@\upstream\celt\kiss_fft.c:135:          C_SUB( scratch0 , *Fout, Fout[2] );
	l32i.n	a7, a9, 0	# MEM[base: Fout_577, offset: 0B], _237
	l32i.n	a6, a9, 4	# MEM[base: Fout_577, offset: 4B], _242
	l32i.n	a3, a9, 16	# MEM[base: Fout_577, offset: 16B], _239
	l32i.n	a2, a9, 20	# MEM[base: Fout_577, offset: 20B], _244
# @OPUS@\upstream\celt\kiss_fft.c:137:          C_ADD( scratch1 , Fout[1] , Fout[3] );
	l32i.n	a10, a9, 24	# MEM[base: Fout_577, offset: 24B], _251
	l32i.n	a11, a9, 12	# MEM[base: Fout_577, offset: 12B], _254
# @OPUS@\upstream\celt\kiss_fft.c:135:          C_SUB( scratch0 , *Fout, Fout[2] );
	sub	a5, a7, a3	# _240, _237, _239
	sub	a4, a6, a2	# _245, _242, _244
# @OPUS@\upstream\celt\kiss_fft.c:136:          C_ADDTO(*Fout, Fout[2]);
	add.n	a3, a7, a3	# _246, _237, _239
	add.n	a2, a6, a2	# _247, _242, _244
# @OPUS@\upstream\celt\kiss_fft.c:137:          C_ADD( scratch1 , Fout[1] , Fout[3] );
	l32i.n	a7, a9, 28	# MEM[base: Fout_577, offset: 28B],
	l32i.n	a6, a9, 8	# MEM[base: Fout_577, offset: 8B],
	add.n	a12, a11, a7	# _257, _254,
	add.n	a13, a6, a10	# _252,, _251
# @OPUS@\upstream\celt\kiss_fft.c:142:          Fout[1].r = ADD32_ovflw(scratch0.r, scratch1.i);
	sub	a7, a5, a7	# tmp1405, _240,
# @OPUS@\upstream\celt\kiss_fft.c:143:          Fout[1].i = SUB32_ovflw(scratch0.i, scratch1.r);
	sub	a6, a4, a6	# tmp1407, _245,
# @OPUS@\upstream\celt\kiss_fft.c:144:          Fout[3].r = SUB32_ovflw(scratch0.r, scratch1.i);
	sub	a5, a5, a11	# tmp1409, _240, _254
# @OPUS@\upstream\celt\kiss_fft.c:145:          Fout[3].i = ADD32_ovflw(scratch0.i, scratch1.r);
	sub	a4, a4, a10	# tmp1411, _245, _251
# @OPUS@\upstream\celt\kiss_fft.c:142:          Fout[1].r = ADD32_ovflw(scratch0.r, scratch1.i);
	add.n	a7, a7, a11	# tmp1406, tmp1405, _254
# @OPUS@\upstream\celt\kiss_fft.c:143:          Fout[1].i = SUB32_ovflw(scratch0.i, scratch1.r);
	add.n	a6, a6, a10	# tmp1408, tmp1407, _251
# @OPUS@\upstream\celt\kiss_fft.c:145:          Fout[3].i = ADD32_ovflw(scratch0.i, scratch1.r);
	l32i.n	a11, a9, 8	# MEM[base: Fout_577, offset: 8B],
# @OPUS@\upstream\celt\kiss_fft.c:144:          Fout[3].r = SUB32_ovflw(scratch0.r, scratch1.i);
	l32i.n	a10, a9, 28	# MEM[base: Fout_577, offset: 28B],
# @OPUS@\upstream\celt\kiss_fft.c:138:          C_SUB( Fout[2], *Fout, scratch1 );
	sub	a14, a2, a12	# tmp1402, _247, _257
	sub	a15, a3, a13	# tmp1401, _246, _252
# @OPUS@\upstream\celt\kiss_fft.c:139:          C_ADDTO( *Fout , scratch1 );
	add.n	a2, a2, a12	# tmp1404, _247, _257
	add.n	a3, a3, a13	# tmp1403, _246, _252
# @OPUS@\upstream\celt\kiss_fft.c:144:          Fout[3].r = SUB32_ovflw(scratch0.r, scratch1.i);
	add.n	a5, a5, a10	# tmp1410, tmp1409,
# @OPUS@\upstream\celt\kiss_fft.c:145:          Fout[3].i = ADD32_ovflw(scratch0.i, scratch1.r);
	add.n	a4, a4, a11	# tmp1412, tmp1411,
# @OPUS@\upstream\celt\kiss_fft.c:131:       for (i=0;i<N;i++)
	l32i	a12, sp, 88	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:138:          C_SUB( Fout[2], *Fout, scratch1 );
	s32i.n	a15, a9, 16	# MEM[base: Fout_577, offset: 16B], tmp1401
	s32i.n	a14, a9, 20	# MEM[base: Fout_577, offset: 20B], tmp1402
# @OPUS@\upstream\celt\kiss_fft.c:139:          C_ADDTO( *Fout , scratch1 );
	s32i.n	a3, a9, 0	# MEM[base: Fout_577, offset: 0B], tmp1403
	s32i.n	a2, a9, 4	# MEM[base: Fout_577, offset: 4B], tmp1404
# @OPUS@\upstream\celt\kiss_fft.c:142:          Fout[1].r = ADD32_ovflw(scratch0.r, scratch1.i);
	s32i.n	a7, a9, 8	# MEM[base: Fout_577, offset: 8B], tmp1406
# @OPUS@\upstream\celt\kiss_fft.c:143:          Fout[1].i = SUB32_ovflw(scratch0.i, scratch1.r);
	s32i.n	a6, a9, 12	# MEM[base: Fout_577, offset: 12B], tmp1408
# @OPUS@\upstream\celt\kiss_fft.c:144:          Fout[3].r = SUB32_ovflw(scratch0.r, scratch1.i);
	s32i.n	a5, a9, 24	# MEM[base: Fout_577, offset: 24B], tmp1410
# @OPUS@\upstream\celt\kiss_fft.c:145:          Fout[3].i = ADD32_ovflw(scratch0.i, scratch1.r);
	s32i.n	a4, a9, 28	# MEM[base: Fout_577, offset: 28B], tmp1412
# @OPUS@\upstream\celt\kiss_fft.c:131:       for (i=0;i<N;i++)
	addi.n	a8, a8, 1	# i, i,
# @OPUS@\upstream\celt\kiss_fft.c:146:          Fout+=4;
	addi	a9, a9, 32	# Fout, Fout,
# @OPUS@\upstream\celt\kiss_fft.c:131:       for (i=0;i<N;i++)
	bne	a12, a8, .L47	#, i,
	j	.L41		#
.L46:
# @OPUS@\upstream\celt\kiss_fft.c:155:       for (i=0;i<N;i++)
	blti	a2, 1, .L41	# tmp14,,
# @OPUS@\upstream\celt\kiss_fft.c:567:           kf_bfly4(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i	a3, sp, 248	# %sfp,
	mov.n	a6, a4	#,
	ssl	a3	#
	sll	a2, a2	# _21, tmp14
# @OPUS@\upstream\celt\kiss_fft.c:173:             tw3 += fstride*3;
	slli	a3, a2, 1	# tmp1414, _21,
	add.n	a3, a3, a2	# tmp1415, tmp1414, _21
# @OPUS@\upstream\celt\kiss_fft.c:171:             tw1 += fstride;
	slli	a5, a2, 2	#, _21,
# @OPUS@\upstream\celt\kiss_fft.c:162:             C_MUL_TABLE(scratch[0],Fout[m] , *tw1 );
	slli	a4, a4, 3	#,,
# @OPUS@\upstream\celt\kiss_fft.c:172:             tw2 += fstride*2;
	slli	a2, a2, 3	#, _21,
# @OPUS@\upstream\celt\kiss_fft.c:173:             tw3 += fstride*3;
	slli	a3, a3, 2	#, tmp1415,
# @OPUS@\upstream\celt\kiss_fft.c:162:             C_MUL_TABLE(scratch[0],Fout[m] , *tw1 );
	s32i	a4, sp, 68	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:171:             tw1 += fstride;
	s32i	a5, sp, 92	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:172:             tw2 += fstride*2;
	s32i	a2, sp, 96	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:173:             tw3 += fstride*3;
	s32i	a3, sp, 100	# %sfp,
	blti	a6, 1, .L41	#,,
	l32i	a7, sp, 176	# %sfp,
	l32i	a8, sp, 244	# %sfp,
	slli	a7, a7, 3	#,,
# @OPUS@\upstream\celt\kiss_fft.c:155:       for (i=0;i<N;i++)
	movi.n	a9, 0	#,
	slli	a10, a6, 4	#,,
	s32i	a7, sp, 136	# %sfp,
	s32i.n	a8, sp, 52	# %sfp,
	s32i	a9, sp, 72	# %sfp,
	s32i	a10, sp, 156	# %sfp,
.L50:
	l32i.n	a12, sp, 52	# %sfp,
	l32i	a11, sp, 68	# %sfp,
	l32i	a3, sp, 68	# %sfp,
	add.n	a11, a11, a12	#,,
# @OPUS@\upstream\celt\kiss_fft.c:158:          tw3 = tw2 = tw1 = st->twiddles;
	l32i	a14, sp, 160	# %sfp,
	add.n	a2, a3, a11	# ivtmp$224,,
	l32i	a4, sp, 156	# %sfp,
	l32i.n	a14, a14, 52	# MEM[(const struct kiss_twiddle_cpx * const *)st_37(D) + 52B],
	add.n	a3, a3, a2	# ivtmp$225,, ivtmp$224
	sub	a4, a3, a4	#, ivtmp$225,
	s32i.n	a11, sp, 32	# %sfp,
	s32i.n	a14, sp, 36	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:157:          Fout = Fout_beg + i*mm;
	mov.n	a5, a12	# Fout,
	s32i	a4, sp, 84	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:158:          tw3 = tw2 = tw1 = st->twiddles;
	s32i.n	a14, sp, 48	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:158:          tw3 = tw2 = tw1 = st->twiddles;
	s32i.n	a14, sp, 44	# %sfp,
	mov.n	a15, a2	# ivtmp$224, ivtmp$224
.L49:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i.n	a6, sp, 36	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a7, a6, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:162:             C_MUL_TABLE(scratch[0],Fout[m] , *tw1 );
#NO_APP
	l32i.n	a8, sp, 32	# %sfp,
	slli	a9, a7, 16	# tmp1419, value,
	l32i.n	a4, a8, 4	# MEM[base: _1237, offset: 4B], _310
	l32i.n	a2, a8, 0	# MEM[base: _1237, offset: 0B], _296
	srai	a9, a9, 16	# _291, tmp1419,
	srai	a7, a7, 16	# _309, value,
	srai	a8, a2, 16	# _297, _296,
	srai	a6, a4, 16	# _311, _310,
	extui	a2, a2, 0, 16	# _304, _296,
	extui	a4, a4, 0, 16	# _318, _310,
	mull	a11, a9, a8	# tmp1422, _291, _297
	mull	a14, a9, a2	# tmp1424, _291, _304
	mull	a12, a7, a6	# tmp1427, _309, _311
	mull	a10, a7, a4	# tmp1429, _309, _318
	mull	a8, a8, a7	# tmp1432, _297, _309
	mull	a2, a2, a7	# tmp1434, _304, _309
	mull	a6, a9, a6	# tmp1437, _291, _311
	mull	a4, a9, a4	# tmp1439, _291, _318
	srai	a14, a14, 15	# tmp1425, tmp1424,
	srai	a10, a10, 15	# tmp1430, tmp1429,
	srai	a2, a2, 15	# tmp1435, tmp1434,
	srai	a4, a4, 15	# tmp1440, tmp1439,
	slli	a11, a11, 1	# tmp1423, tmp1422,
	slli	a12, a12, 1	# tmp1428, tmp1427,
	slli	a8, a8, 1	# tmp1433, tmp1432,
	slli	a6, a6, 1	# tmp1438, tmp1437,
	add.n	a11, a11, a14	# tmp1426, tmp1423, tmp1425
	add.n	a12, a12, a10	# tmp1431, tmp1428, tmp1430
	add.n	a8, a8, a2	# tmp1436, tmp1433, tmp1435
	add.n	a6, a6, a4	# tmp1441, tmp1438, tmp1440
	sub	a12, a11, a12	#, tmp1426, tmp1431
	add.n	a6, a8, a6	#, tmp1436, tmp1441
	s32i.n	a12, sp, 56	# %sfp,
	s32i.n	a6, sp, 40	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i.n	a9, sp, 44	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a7, a9, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:163:             C_MUL_TABLE(scratch[1],Fout[m2] , *tw2 );
#NO_APP
	l32i.n	a6, a15, 0	# MEM[base: _1235, offset: 0B], _349
	l32i.n	a4, a15, 4	# MEM[base: _1235, offset: 4B], _363
	slli	a12, a7, 16	# tmp1443, value,
	srai	a12, a12, 16	# _345, tmp1443,
	srai	a7, a7, 16	# _362, value,
	srai	a10, a6, 16	# _350, _349,
	srai	a9, a4, 16	# _364, _363,
	extui	a6, a6, 0, 16	# _357, _349,
	extui	a4, a4, 0, 16	# _371, _363,
	mull	a14, a10, a7	# tmp1454, _350, _362
	mull	a11, a6, a7	# tmp1456, _357, _362
	mull	a13, a12, a9	# tmp1459, _345, _364
	mull	a2, a12, a4	# tmp1461, _345, _371
	mull	a10, a12, a10	# tmp1444, _345, _350
	mull	a6, a12, a6	# tmp1446, _345, _357
	mull	a9, a7, a9	# tmp1450, _362, _364
	mull	a4, a7, a4	# tmp1452, _362, _371
	slli	a14, a14, 1	# tmp1455, tmp1454,
	srai	a2, a2, 15	# tmp1462, tmp1461,
	srai	a11, a11, 15	# tmp1457, tmp1456,
	slli	a13, a13, 1	# tmp1460, tmp1459,
	add.n	a11, a14, a11	# tmp1458, tmp1455, tmp1457
	add.n	a13, a13, a2	# tmp1463, tmp1460, tmp1462
	slli	a10, a10, 1	# tmp1445, tmp1444,
	srai	a6, a6, 15	# tmp1447, tmp1446,
	slli	a9, a9, 1	# tmp1451, tmp1450,
	srai	a4, a4, 15	# tmp1453, tmp1452,
	add.n	a13, a11, a13	#, tmp1458, tmp1463
	add.n	a8, a10, a6	# _361, tmp1445, tmp1447
	add.n	a2, a9, a4	# _375, tmp1451, tmp1453
	s32i	a13, sp, 64	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i.n	a10, sp, 48	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a6, a10, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:164:             C_MUL_TABLE(scratch[2],Fout[m3] , *tw3 );
#NO_APP
	l32i.n	a11, a3, 0	# MEM[base: _1233, offset: 0B], _402
	l32i.n	a9, a3, 4	# MEM[base: _1233, offset: 4B], _416
	slli	a4, a6, 16	# tmp1465, value,
	srai	a4, a4, 16	# _398, tmp1465,
	srai	a6, a6, 16	# _415, value,
	srai	a13, a11, 16	# _403, _402,
	srai	a10, a9, 16	# _417, _416,
	extui	a11, a11, 0, 16	# _410, _402,
	extui	a9, a9, 0, 16	# _424, _416,
	mull	a14, a6, a10	# tmp1472, _415, _417
	mull	a12, a6, a9	# tmp1474, _415, _424
	mull	a7, a13, a6	# tmp1476, _403, _415
	mull	a10, a4, a10	# tmp1481, _398, _417
	mull	a6, a11, a6	# tmp1478, _410, _415
	mull	a9, a4, a9	# tmp1483, _398, _424
	mull	a13, a4, a13	# tmp1466, _398, _403
	mull	a4, a4, a11	# tmp1468, _398, _410
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	l32i.n	a11, a5, 0	# MEM[base: Fout_141, offset: 0B],
# @OPUS@\upstream\celt\kiss_fft.c:164:             C_MUL_TABLE(scratch[2],Fout[m3] , *tw3 );
	slli	a14, a14, 1	# tmp1473, tmp1472,
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	s32i.n	a11, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:164:             C_MUL_TABLE(scratch[2],Fout[m3] , *tw3 );
	srai	a4, a4, 15	# tmp1469, tmp1468,
	srai	a12, a12, 15	# tmp1475, tmp1474,
	slli	a13, a13, 1	# tmp1467, tmp1466,
	add.n	a12, a14, a12	# _428, tmp1473, tmp1475
	add.n	a13, a13, a4	# _414, tmp1467, tmp1469
# @OPUS@\upstream\celt\kiss_fft.c:167:             C_ADDTO(*Fout, scratch[1]);
	l32i.n	a14, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:168:             C_ADD( scratch[3] , scratch[0] , scratch[2] );
	l32i.n	a4, sp, 56	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:164:             C_MUL_TABLE(scratch[2],Fout[m3] , *tw3 );
	slli	a7, a7, 1	# tmp1477, tmp1476,
	slli	a10, a10, 1	# tmp1482, tmp1481,
	srai	a6, a6, 15	# tmp1479, tmp1478,
	srai	a9, a9, 15	# tmp1484, tmp1483,
	add.n	a9, a10, a9	# tmp1485, tmp1482, tmp1484
	add.n	a6, a7, a6	# tmp1480, tmp1477, tmp1479
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	l32i.n	a11, a5, 4	# MEM[base: Fout_141, offset: 4B], _451
# @OPUS@\upstream\celt\kiss_fft.c:164:             C_MUL_TABLE(scratch[2],Fout[m3] , *tw3 );
	add.n	a6, a6, a9	# _446, tmp1480, tmp1485
# @OPUS@\upstream\celt\kiss_fft.c:168:             C_ADD( scratch[3] , scratch[0] , scratch[2] );
	sub	a7, a4, a12	# tmp1488,, _428
# @OPUS@\upstream\celt\kiss_fft.c:167:             C_ADDTO(*Fout, scratch[1]);
	add.n	a9, a8, a14	# tmp1487, _361,
# @OPUS@\upstream\celt\kiss_fft.c:168:             C_ADD( scratch[3] , scratch[0] , scratch[2] );
	l32i.n	a4, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:167:             C_ADDTO(*Fout, scratch[1]);
	l32i	a14, sp, 64	# %sfp,
	sub	a9, a9, a2	# _453, tmp1487, _375
	add.n	a10, a14, a11	# _455,, _451
# @OPUS@\upstream\celt\kiss_fft.c:168:             C_ADD( scratch[3] , scratch[0] , scratch[2] );
	add.n	a14, a4, a6	# _458,, _446
# @OPUS@\upstream\celt\kiss_fft.c:167:             C_ADDTO(*Fout, scratch[1]);
	s32i.n	a9, a5, 0	# MEM[base: Fout_141, offset: 0B], _453
	s32i.n	a10, a5, 4	# MEM[base: Fout_141, offset: 4B], _455
# @OPUS@\upstream\celt\kiss_fft.c:170:             C_SUB( Fout[m2], *Fout, scratch[3] );
	sub	a10, a10, a14	# tmp1491, _455, _458
	s32i.n	a10, a15, 4	# MEM[base: _1235, offset: 4B], tmp1491
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	l32i.n	a10, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:168:             C_ADD( scratch[3] , scratch[0] , scratch[2] );
	add.n	a7, a7, a13	# _457, tmp1488, _414
# @OPUS@\upstream\celt\kiss_fft.c:170:             C_SUB( Fout[m2], *Fout, scratch[3] );
	sub	a9, a9, a7	# tmp1490, _453, _457
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	add.n	a2, a2, a10	# tmp1486, _375,
# @OPUS@\upstream\celt\kiss_fft.c:170:             C_SUB( Fout[m2], *Fout, scratch[3] );
	s32i.n	a9, a15, 0	# MEM[base: _1235, offset: 0B], tmp1490
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	sub	a2, a2, a8	# _449, tmp1486, _361
# @OPUS@\upstream\celt\kiss_fft.c:169:             C_SUB( scratch[4] , scratch[0] , scratch[2] );
	l32i.n	a8, sp, 56	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:174:             C_ADDTO( *Fout , scratch[3] );
	l32i.n	a9, a5, 4	# MEM[base: Fout_141, offset: 4B], MEM[base: Fout_141, offset: 4B]
	l32i.n	a4, a5, 0	# MEM[base: Fout_141, offset: 0B], MEM[base: Fout_141, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:169:             C_SUB( scratch[4] , scratch[0] , scratch[2] );
	sub	a13, a8, a13	# tmp1489,, _414
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	l32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:169:             C_SUB( scratch[4] , scratch[0] , scratch[2] );
	add.n	a13, a13, a12	# _459, tmp1489, _428
# @OPUS@\upstream\celt\kiss_fft.c:174:             C_ADDTO( *Fout , scratch[3] );
	add.n	a14, a9, a14	# tmp1494, MEM[base: Fout_141, offset: 4B], _458
# @OPUS@\upstream\celt\kiss_fft.c:176:             Fout[m].r = ADD32_ovflw(scratch[5].r, scratch[4].i);
	l32i.n	a12, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:174:             C_ADDTO( *Fout , scratch[3] );
	s32i.n	a14, a5, 4	# MEM[base: Fout_141, offset: 4B], tmp1494
# @OPUS@\upstream\celt\kiss_fft.c:176:             Fout[m].r = ADD32_ovflw(scratch[5].r, scratch[4].i);
	sub	a8, a2, a6	# tmp1496, _449, _446
# @OPUS@\upstream\celt\kiss_fft.c:174:             C_ADDTO( *Fout , scratch[3] );
	add.n	a7, a4, a7	# tmp1492, MEM[base: Fout_141, offset: 0B], _457
# @OPUS@\upstream\celt\kiss_fft.c:178:             Fout[m3].r = SUB32_ovflw(scratch[5].r, scratch[4].i);
	l32i.n	a14, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:174:             C_ADDTO( *Fout , scratch[3] );
	s32i.n	a7, a5, 0	# MEM[base: Fout_141, offset: 0B], tmp1492
# @OPUS@\upstream\celt\kiss_fft.c:166:             C_SUB( scratch[5] , *Fout, scratch[1] );
	sub	a11, a11, a10	# _452, _451,
# @OPUS@\upstream\celt\kiss_fft.c:176:             Fout[m].r = ADD32_ovflw(scratch[5].r, scratch[4].i);
	l32i.n	a7, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:176:             Fout[m].r = ADD32_ovflw(scratch[5].r, scratch[4].i);
	add.n	a4, a8, a12	# tmp1497, tmp1496,
# @OPUS@\upstream\celt\kiss_fft.c:171:             tw1 += fstride;
	l32i	a9, sp, 92	# %sfp,
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:177:             Fout[m].i = SUB32_ovflw(scratch[5].i, scratch[4].r);
	sub	a12, a11, a13	# tmp1498, _452, _459
# @OPUS@\upstream\celt\kiss_fft.c:178:             Fout[m3].r = SUB32_ovflw(scratch[5].r, scratch[4].i);
	sub	a2, a2, a14	# tmp1499, _449,
# @OPUS@\upstream\celt\kiss_fft.c:179:             Fout[m3].i = ADD32_ovflw(scratch[5].i, scratch[4].r);
	add.n	a13, a11, a13	# tmp1501, _452, _459
# @OPUS@\upstream\celt\kiss_fft.c:172:             tw2 += fstride*2;
	l32i.n	a10, sp, 44	# %sfp,
	l32i	a11, sp, 96	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:177:             Fout[m].i = SUB32_ovflw(scratch[5].i, scratch[4].r);
	s32i.n	a12, a7, 4	# MEM[base: _1237, offset: 4B], tmp1498
# @OPUS@\upstream\celt\kiss_fft.c:176:             Fout[m].r = ADD32_ovflw(scratch[5].r, scratch[4].i);
	s32i.n	a4, a7, 0	# MEM[base: _1237, offset: 0B], tmp1497
# @OPUS@\upstream\celt\kiss_fft.c:178:             Fout[m3].r = SUB32_ovflw(scratch[5].r, scratch[4].i);
	add.n	a6, a2, a6	# tmp1500, tmp1499, _446
# @OPUS@\upstream\celt\kiss_fft.c:171:             tw1 += fstride;
	add.n	a8, a8, a9	#,,
# @OPUS@\upstream\celt\kiss_fft.c:178:             Fout[m3].r = SUB32_ovflw(scratch[5].r, scratch[4].i);
	s32i.n	a6, a3, 0	# MEM[base: _1233, offset: 0B], tmp1500
# @OPUS@\upstream\celt\kiss_fft.c:179:             Fout[m3].i = ADD32_ovflw(scratch[5].i, scratch[4].r);
	s32i.n	a13, a3, 4	# MEM[base: _1233, offset: 4B], tmp1501
# @OPUS@\upstream\celt\kiss_fft.c:171:             tw1 += fstride;
	s32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:172:             tw2 += fstride*2;
	add.n	a10, a10, a11	#,,
	s32i.n	a10, sp, 44	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:173:             tw3 += fstride*3;
	l32i.n	a12, sp, 48	# %sfp,
	l32i	a14, sp, 100	# %sfp,
	addi.n	a7, a7, 8	#,,
	add.n	a12, a12, a14	#,,
# @OPUS@\upstream\celt\kiss_fft.c:160:          for (j=0;j<m;j++)
	l32i	a2, sp, 84	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:180:             ++Fout;
	addi.n	a5, a5, 8	# Fout, Fout,
# @OPUS@\upstream\celt\kiss_fft.c:173:             tw3 += fstride*3;
	s32i.n	a12, sp, 48	# %sfp,
	s32i.n	a7, sp, 32	# %sfp,
	addi.n	a15, a15, 8	# ivtmp$224, ivtmp$224,
	addi.n	a3, a3, 8	# ivtmp$225, ivtmp$225,
# @OPUS@\upstream\celt\kiss_fft.c:160:          for (j=0;j<m;j++)
	bne	a5, a2, .L49	# Fout,,
# @OPUS@\upstream\celt\kiss_fft.c:155:       for (i=0;i<N;i++)
	l32i	a3, sp, 72	# %sfp,
	l32i.n	a4, sp, 52	# %sfp,
	l32i	a5, sp, 136	# %sfp,
	addi.n	a3, a3, 1	#,,
	add.n	a4, a4, a5	#,,
# @OPUS@\upstream\celt\kiss_fft.c:155:       for (i=0;i<N;i++)
	l32i	a6, sp, 88	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:155:       for (i=0;i<N;i++)
	s32i	a3, sp, 72	# %sfp,
	s32i.n	a4, sp, 52	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:155:       for (i=0;i<N;i++)
	bne	a6, a3, .L50	#,,
	j	.L41		#
.L38:
# @OPUS@\upstream\celt\kiss_fft.c:571:           kf_bfly3(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i	a7, sp, 128	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:571:           kf_bfly3(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i	a8, sp, 248	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:571:           kf_bfly3(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	slli	a2, a7, 2	# tmp1502,,
	add.n	a2, sp, a2	# tmp1503,, tmp1502
	l32i.n	a2, a2, 0	# MEM[base: _1572, offset: 0B],
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	l32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:571:           kf_bfly3(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	ssl	a8	#
	sll	a2, a2	# _24,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	blti	a9, 1, .L41	#,,
# @OPUS@\upstream\celt\kiss_fft.c:225:          tw1 += fstride;
	slli	a11, a2, 2	#, _24,
# @OPUS@\upstream\celt\kiss_fft.c:220:          C_MUL_TABLE(scratch[1],Fout[m] , *tw1);
	l32i.n	a10, sp, 56	# %sfp,
	l32i	a12, sp, 176	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:225:          tw1 += fstride;
	s32i	a11, sp, 68	# %sfp,
	l32i	a11, sp, 244	# %sfp, ivtmp$200
# @OPUS@\upstream\celt\kiss_fft.c:220:          C_MUL_TABLE(scratch[1],Fout[m] , *tw1);
	slli	a10, a10, 3	#,,
# @OPUS@\upstream\celt\kiss_fft.c:226:          tw2 += fstride*2;
	slli	a2, a2, 3	#, _24,
	slli	a12, a12, 3	#,,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	movi.n	a14, 0	#,
# @OPUS@\upstream\celt\kiss_fft.c:220:          C_MUL_TABLE(scratch[1],Fout[m] , *tw1);
	s32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:226:          tw2 += fstride*2;
	s32i	a2, sp, 72	# %sfp,
	s32i	a12, sp, 84	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	s32i.n	a14, sp, 48	# %sfp,
	s32i.n	a11, sp, 36	# %sfp, ivtmp$200
.L52:
# @OPUS@\upstream\celt\kiss_fft.c:215:       tw1=tw2=st->twiddles;
	l32i	a2, sp, 160	# %sfp,
	l32i	a3, sp, 64	# %sfp,
	l32i.n	a4, sp, 36	# %sfp,
	l32i.n	a2, a2, 52	# MEM[(const struct kiss_twiddle_cpx * const *)st_37(D) + 52B],
# @OPUS@\upstream\celt\kiss_fft.c:217:       k=m;
	l32i.n	a6, sp, 56	# %sfp,
	add.n	a5, a3, a4	# ivtmp$191,,
# @OPUS@\upstream\celt\kiss_fft.c:215:       tw1=tw2=st->twiddles;
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:214:       Fout = Fout_beg + i*mm;
	mov.n	a7, a4	# Fout,
	add.n	a3, a3, a5	# ivtmp$192,, ivtmp$191
# @OPUS@\upstream\celt\kiss_fft.c:215:       tw1=tw2=st->twiddles;
	s32i.n	a2, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:217:       k=m;
	s32i.n	a6, sp, 44	# %sfp,
.L51:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i.n	a8, sp, 32	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a10, a8, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:220:          C_MUL_TABLE(scratch[1],Fout[m] , *tw1);
#NO_APP
	l32i.n	a6, a5, 0	# MEM[base: _1270, offset: 0B], _508
	l32i.n	a4, a5, 4	# MEM[base: _1270, offset: 4B], _522
	slli	a11, a10, 16	# tmp1505, value,
	srai	a11, a11, 16	# _504, tmp1505,
	srai	a10, a10, 16	# _521, value,
	srai	a9, a6, 16	# _509, _508,
	srai	a8, a4, 16	# _523, _522,
	extui	a6, a6, 0, 16	# _516, _508,
	extui	a4, a4, 0, 16	# _530, _522,
	mull	a15, a11, a9	# tmp1508, _504, _509
	mull	a13, a11, a6	# tmp1510, _504, _516
	mull	a12, a10, a8	# tmp1513, _521, _523
	mull	a14, a10, a4	# tmp1515, _521, _530
	mull	a9, a9, a10	# tmp1518, _509, _521
	mull	a6, a6, a10	# tmp1520, _516, _521
	mull	a8, a11, a8	# tmp1523, _504, _523
	mull	a4, a11, a4	# tmp1525, _504, _530
	srai	a13, a13, 15	# tmp1511, tmp1510,
	srai	a14, a14, 15	# tmp1516, tmp1515,
	slli	a15, a15, 1	# tmp1509, tmp1508,
	slli	a12, a12, 1	# tmp1514, tmp1513,
	srai	a6, a6, 15	# tmp1521, tmp1520,
	srai	a4, a4, 15	# tmp1526, tmp1525,
	add.n	a15, a15, a13	# tmp1512, tmp1509, tmp1511
	add.n	a12, a12, a14	# tmp1517, tmp1514, tmp1516
	slli	a9, a9, 1	# tmp1519, tmp1518,
	slli	a8, a8, 1	# tmp1524, tmp1523,
	add.n	a9, a9, a6	# tmp1522, tmp1519, tmp1521
	add.n	a8, a8, a4	# tmp1527, tmp1524, tmp1526
	sub	a12, a15, a12	#, tmp1512, tmp1517
	s32i.n	a12, sp, 52	# %sfp,
	add.n	a2, a9, a8	# _552, tmp1522, tmp1527
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i.n	a10, sp, 40	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a9, a10, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:221:          C_MUL_TABLE(scratch[2],Fout[m2] , *tw2);
#NO_APP
	l32i.n	a12, a3, 4	# MEM[base: _1268, offset: 4B], _574
	l32i.n	a8, a3, 0	# MEM[base: _1268, offset: 0B], _560
	srai	a13, a9, 16	# _573, value,
	srai	a6, a12, 16	# _575, _574,
	slli	a4, a9, 16	# tmp1529, value,
	extui	a12, a12, 0, 16	# _582, _574,
	srai	a4, a4, 16	# _557, tmp1529,
	srai	a9, a8, 16	# _561, _560,
	mull	a15, a13, a6	# tmp1536, _573, _575
	mull	a10, a13, a12	# tmp1538, _573, _582
	extui	a8, a8, 0, 16	# _568, _560,
	mull	a14, a4, a9	# tmp1530, _557, _561
	mull	a11, a4, a8	# tmp1532, _557, _568
	slli	a15, a15, 1	# tmp1537, tmp1536,
	mull	a6, a4, a6	# tmp1545, _557, _575
	srai	a10, a10, 15	# tmp1539, tmp1538,
	mull	a4, a4, a12	# tmp1547, _557, _582
# @OPUS@\upstream\celt\kiss_fft.c:223:          C_ADD(scratch[3],scratch[1],scratch[2]);
	l32i.n	a12, sp, 52	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:221:          C_MUL_TABLE(scratch[2],Fout[m2] , *tw2);
	add.n	a10, a15, a10	# _586, tmp1537, tmp1539
	srai	a11, a11, 15	# tmp1533, tmp1532,
	slli	a14, a14, 1	# tmp1531, tmp1530,
	add.n	a14, a14, a11	# _572, tmp1531, tmp1533
	mull	a9, a9, a13	# tmp1540, _561, _573
# @OPUS@\upstream\celt\kiss_fft.c:223:          C_ADD(scratch[3],scratch[1],scratch[2]);
	sub	a11, a12, a10	# tmp1550,, _586
# @OPUS@\upstream\celt\kiss_fft.c:221:          C_MUL_TABLE(scratch[2],Fout[m2] , *tw2);
	mull	a8, a8, a13	# tmp1542, _568, _573
# @OPUS@\upstream\celt\kiss_fft.c:228:          Fout[m].r = SUB32_ovflw(Fout->r, HALF_OF(scratch[3].r));
	l32i.n	a12, a7, 0	# MEM[base: Fout_506, offset: 0B], MEM[base: Fout_506, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:223:          C_ADD(scratch[3],scratch[1],scratch[2]);
	add.n	a11, a11, a14	# _605, tmp1550, _572
# @OPUS@\upstream\celt\kiss_fft.c:221:          C_MUL_TABLE(scratch[2],Fout[m2] , *tw2);
	srai	a8, a8, 15	# tmp1543, tmp1542,
	slli	a6, a6, 1	# tmp1546, tmp1545,
# @OPUS@\upstream\celt\kiss_fft.c:228:          Fout[m].r = SUB32_ovflw(Fout->r, HALF_OF(scratch[3].r));
	srai	a15, a11, 1	# tmp1552, _605,
# @OPUS@\upstream\celt\kiss_fft.c:221:          C_MUL_TABLE(scratch[2],Fout[m2] , *tw2);
	slli	a9, a9, 1	# tmp1541, tmp1540,
	srai	a4, a4, 15	# tmp1548, tmp1547,
	add.n	a4, a6, a4	# tmp1549, tmp1546, tmp1548
# @OPUS@\upstream\celt\kiss_fft.c:228:          Fout[m].r = SUB32_ovflw(Fout->r, HALF_OF(scratch[3].r));
	sub	a15, a12, a15	# tmp1553, MEM[base: Fout_506, offset: 0B], tmp1552
# @OPUS@\upstream\celt\kiss_fft.c:221:          C_MUL_TABLE(scratch[2],Fout[m2] , *tw2);
	add.n	a9, a9, a8	# tmp1544, tmp1541, tmp1543
# @OPUS@\upstream\celt\kiss_fft.c:228:          Fout[m].r = SUB32_ovflw(Fout->r, HALF_OF(scratch[3].r));
	s32i.n	a15, a5, 0	# MEM[base: _1270, offset: 0B], tmp1553
# @OPUS@\upstream\celt\kiss_fft.c:221:          C_MUL_TABLE(scratch[2],Fout[m2] , *tw2);
	add.n	a9, a9, a4	# _604, tmp1544, tmp1549
# @OPUS@\upstream\celt\kiss_fft.c:223:          C_ADD(scratch[3],scratch[1],scratch[2]);
	add.n	a12, a2, a9	# _607, _552, _604
# @OPUS@\upstream\celt\kiss_fft.c:229:          Fout[m].i = SUB32_ovflw(Fout->i, HALF_OF(scratch[3].i));
	l32i.n	a4, a7, 4	# MEM[base: Fout_506, offset: 4B], MEM[base: Fout_506, offset: 4B]
	srai	a6, a12, 1	# tmp1555, _607,
	sub	a4, a4, a6	# tmp1556, MEM[base: Fout_506, offset: 4B], tmp1555
# @OPUS@\upstream\celt\kiss_fft.c:229:          Fout[m].i = SUB32_ovflw(Fout->i, HALF_OF(scratch[3].i));
	s32i.n	a4, a5, 4	# MEM[base: _1270, offset: 4B], tmp1556
# @OPUS@\upstream\celt\kiss_fft.c:233:          C_ADDTO(*Fout,scratch[3]);
	l32i.n	a4, a7, 4	# MEM[base: Fout_506, offset: 4B], MEM[base: Fout_506, offset: 4B]
	l32i.n	a13, a7, 0	# MEM[base: Fout_506, offset: 0B], MEM[base: Fout_506, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:224:          C_SUB(scratch[0],scratch[1],scratch[2]);
	sub	a9, a2, a9	# _612, _552, _604
# @OPUS@\upstream\celt\kiss_fft.c:231:          C_MULBYSCALAR( scratch[0] , epi3.i );
	l32r	a2, .LC1	#,
# @OPUS@\upstream\celt\kiss_fft.c:233:          C_ADDTO(*Fout,scratch[3]);
	add.n	a12, a4, a12	# tmp1560, MEM[base: Fout_506, offset: 4B], _607
# @OPUS@\upstream\celt\kiss_fft.c:231:          C_MULBYSCALAR( scratch[0] , epi3.i );
	srai	a15, a9, 16	# tmp1562, _612,
# @OPUS@\upstream\celt\kiss_fft.c:224:          C_SUB(scratch[0],scratch[1],scratch[2]);
	l32i.n	a4, sp, 52	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:231:          C_MULBYSCALAR( scratch[0] , epi3.i );
	extui	a9, a9, 0, 16	# tmp1566, _612,
# @OPUS@\upstream\celt\kiss_fft.c:233:          C_ADDTO(*Fout,scratch[3]);
	add.n	a11, a13, a11	# tmp1558, MEM[base: Fout_506, offset: 0B], _605
# @OPUS@\upstream\celt\kiss_fft.c:231:          C_MULBYSCALAR( scratch[0] , epi3.i );
	mull	a15, a15, a2	# tmp1563, tmp1562,
	mull	a9, a9, a2	# tmp1567, tmp1566,
# @OPUS@\upstream\celt\kiss_fft.c:233:          C_ADDTO(*Fout,scratch[3]);
	s32i.n	a11, a7, 0	# MEM[base: Fout_506, offset: 0B], tmp1558
	s32i.n	a12, a7, 4	# MEM[base: Fout_506, offset: 4B], tmp1560
# @OPUS@\upstream\celt\kiss_fft.c:224:          C_SUB(scratch[0],scratch[1],scratch[2]);
	sub	a14, a4, a14	# tmp1551,, _572
	add.n	a10, a14, a10	# _610, tmp1551, _586
# @OPUS@\upstream\celt\kiss_fft.c:235:          Fout[m2].r = ADD32_ovflw(Fout[m].r, scratch[0].i);
	l32i.n	a4, a5, 0	# MEM[base: _1270, offset: 0B], MEM[base: _1270, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:231:          C_MULBYSCALAR( scratch[0] , epi3.i );
	srai	a9, a9, 15	# tmp1569, tmp1567,
	l32r	a6, .LC1	#,
	slli	a15, a15, 1	# tmp1565, tmp1563,
	add.n	a15, a15, a9	# _661, tmp1565, tmp1569
	srai	a2, a10, 16	# tmp1572, _610,
	extui	a10, a10, 0, 16	# tmp1576, _610,
# @OPUS@\upstream\celt\kiss_fft.c:235:          Fout[m2].r = ADD32_ovflw(Fout[m].r, scratch[0].i);
	add.n	a4, a4, a15	# tmp1570, MEM[base: _1270, offset: 0B], _661
# @OPUS@\upstream\celt\kiss_fft.c:231:          C_MULBYSCALAR( scratch[0] , epi3.i );
	mull	a2, a2, a6	# tmp1573, tmp1572,
	mull	a10, a10, a6	# tmp1577, tmp1576,
# @OPUS@\upstream\celt\kiss_fft.c:235:          Fout[m2].r = ADD32_ovflw(Fout[m].r, scratch[0].i);
	s32i.n	a4, a3, 0	# MEM[base: _1268, offset: 0B], tmp1570
# @OPUS@\upstream\celt\kiss_fft.c:236:          Fout[m2].i = SUB32_ovflw(Fout[m].i, scratch[0].r);
	l32i.n	a4, a5, 4	# MEM[base: _1270, offset: 4B], MEM[base: _1270, offset: 4B]
# @OPUS@\upstream\celt\kiss_fft.c:231:          C_MULBYSCALAR( scratch[0] , epi3.i );
	slli	a2, a2, 1	# tmp1575, tmp1573,
	srai	a10, a10, 15	# tmp1579, tmp1577,
	add.n	a10, a2, a10	# _666, tmp1575, tmp1579
# @OPUS@\upstream\celt\kiss_fft.c:236:          Fout[m2].i = SUB32_ovflw(Fout[m].i, scratch[0].r);
	sub	a2, a4, a10	# tmp1580, MEM[base: _1270, offset: 4B], _666
# @OPUS@\upstream\celt\kiss_fft.c:236:          Fout[m2].i = SUB32_ovflw(Fout[m].i, scratch[0].r);
	s32i.n	a2, a3, 4	# MEM[base: _1268, offset: 4B], tmp1580
# @OPUS@\upstream\celt\kiss_fft.c:239:          Fout[m].i = ADD32_ovflw(Fout[m].i, scratch[0].r);
	l32i.n	a2, a5, 4	# MEM[base: _1270, offset: 4B], MEM[base: _1270, offset: 4B]
# @OPUS@\upstream\celt\kiss_fft.c:238:          Fout[m].r = SUB32_ovflw(Fout[m].r, scratch[0].i);
	l32i.n	a9, a5, 0	# MEM[base: _1270, offset: 0B], MEM[base: _1270, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:239:          Fout[m].i = ADD32_ovflw(Fout[m].i, scratch[0].r);
	add.n	a10, a2, a10	# tmp1584, MEM[base: _1270, offset: 4B], _666
# @OPUS@\upstream\celt\kiss_fft.c:238:          Fout[m].r = SUB32_ovflw(Fout[m].r, scratch[0].i);
	sub	a15, a9, a15	# tmp1582, MEM[base: _1270, offset: 0B], _661
# @OPUS@\upstream\celt\kiss_fft.c:239:          Fout[m].i = ADD32_ovflw(Fout[m].i, scratch[0].r);
	s32i.n	a10, a5, 4	# MEM[base: _1270, offset: 4B], tmp1584
# @OPUS@\upstream\celt\kiss_fft.c:242:       } while(--k);
	l32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:225:          tw1 += fstride;
	l32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:226:          tw2 += fstride*2;
	l32i.n	a11, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:225:          tw1 += fstride;
	l32i	a10, sp, 68	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:226:          tw2 += fstride*2;
	l32i	a12, sp, 72	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:242:       } while(--k);
	addi.n	a8, a8, -1	#,,
# @OPUS@\upstream\celt\kiss_fft.c:225:          tw1 += fstride;
	add.n	a9, a9, a10	#,,
# @OPUS@\upstream\celt\kiss_fft.c:226:          tw2 += fstride*2;
	add.n	a11, a11, a12	#,,
# @OPUS@\upstream\celt\kiss_fft.c:238:          Fout[m].r = SUB32_ovflw(Fout[m].r, scratch[0].i);
	s32i.n	a15, a5, 0	# MEM[base: _1270, offset: 0B], tmp1582
# @OPUS@\upstream\celt\kiss_fft.c:242:       } while(--k);
	s32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:225:          tw1 += fstride;
	s32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:226:          tw2 += fstride*2;
	s32i.n	a11, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:241:          ++Fout;
	addi.n	a7, a7, 8	# Fout, Fout,
	addi.n	a5, a5, 8	# ivtmp$191, ivtmp$191,
	addi.n	a3, a3, 8	# ivtmp$192, ivtmp$192,
# @OPUS@\upstream\celt\kiss_fft.c:242:       } while(--k);
	bnez.n	a8, .L51	#,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	l32i.n	a14, sp, 48	# %sfp,
	l32i.n	a2, sp, 36	# %sfp,
	l32i	a3, sp, 84	# %sfp,
	addi.n	a14, a14, 1	#,,
	add.n	a2, a2, a3	#,,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	l32i.n	a4, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	s32i.n	a14, sp, 48	# %sfp,
	s32i.n	a2, sp, 36	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:212:    for (i=0;i<N;i++)
	bne	a4, a14, .L52	#,,
	j	.L41		#
.L43:
# @OPUS@\upstream\celt\kiss_fft.c:574:           kf_bfly5(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i	a5, sp, 128	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:574:           kf_bfly5(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:574:           kf_bfly5(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	slli	a2, a5, 2	# tmp1586,,
	add.n	a2, sp, a2	# tmp1587,, tmp1586
	l32i.n	a2, a2, 0	# MEM[base: _1562, offset: 0B],
# @OPUS@\upstream\celt\kiss_fft.c:574:           kf_bfly5(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i	a7, sp, 248	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:574:           kf_bfly5(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	s32i	a2, sp, 220	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:275:    for (i=0;i<N;i++)
	l32i	a8, sp, 220	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:574:           kf_bfly5(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	l32i.n	a12, a6, 52	# MEM[(const struct kiss_twiddle_cpx * *)st_37(D) + 52B], _54
# @OPUS@\upstream\celt\kiss_fft.c:574:           kf_bfly5(fout,fstride[i]<<shift,st,m, fstride[i], m2);
	ssl	a7	#
	sll	a2, a2	# _27,
# @OPUS@\upstream\celt\kiss_fft.c:275:    for (i=0;i<N;i++)
	blti	a8, 1, .L41	#,,
# @OPUS@\upstream\celt\kiss_fft.c:280:       Fout2=Fout0+2*m;
	l32i.n	a9, sp, 56	# %sfp,
	l32i.n	a10, sp, 56	# %sfp,
	slli	a9, a9, 4	#,,
	s32i	a9, sp, 224	# %sfp,
	blti	a10, 1, .L41	#,,
	slli	a11, a10, 3	#,,
	s32i	a11, sp, 180	# %sfp,
	slli	a3, a2, 1	# tmp1589, _27,
	l32i	a11, sp, 244	# %sfp, ivtmp$266
	l32i	a14, sp, 176	# %sfp,
	l32i	a4, sp, 180	# %sfp,
	add.n	a3, a3, a2	# tmp1590, tmp1589, _27
	slli	a5, a2, 2	#, _27,
	slli	a6, a2, 3	#, _27,
	slli	a14, a14, 3	#,,
	add.n	a10, a11, a4	# ivtmp$267, ivtmp$266,
	slli	a3, a3, 2	#, tmp1590,
	slli	a2, a2, 4	#, _27,
# @OPUS@\upstream\celt\kiss_fft.c:275:    for (i=0;i<N;i++)
	movi.n	a7, 0	#,
	s32i	a14, sp, 184	# %sfp,
	s32i	a5, sp, 236	# %sfp,
	s32i	a6, sp, 232	# %sfp,
	s32i	a3, sp, 240	# %sfp,
	s32i	a2, sp, 228	# %sfp,
	s32i	a7, sp, 136	# %sfp,
	s32i.n	a12, sp, 52	# %sfp, _54
	s32i.n	a10, sp, 56	# %sfp, ivtmp$267
	s32i	a11, sp, 64	# %sfp, ivtmp$266
.L55:
	l32i	a9, sp, 64	# %sfp,
	l32i	a8, sp, 224	# %sfp,
	l32i	a10, sp, 180	# %sfp,
	add.n	a8, a8, a9	#,,
	l32i	a11, sp, 180	# %sfp,
	l32i.n	a12, sp, 52	# %sfp,
	add.n	a10, a8, a10	#,,
# @OPUS@\upstream\celt\kiss_fft.c:279:       Fout1=Fout0+m;
	l32i.n	a14, sp, 56	# %sfp,
	add.n	a11, a10, a11	#,,
	s32i.n	a8, sp, 36	# %sfp,
	s32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:277:       Fout = Fout_beg + i*mm;
	s32i.n	a9, sp, 32	# %sfp,
	s32i.n	a11, sp, 48	# %sfp,
	s32i	a12, sp, 100	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:279:       Fout1=Fout0+m;
	s32i	a12, sp, 88	# %sfp,
	s32i	a12, sp, 92	# %sfp,
	s32i	a12, sp, 96	# %sfp,
	s32i.n	a14, sp, 44	# %sfp,
.L54:
# @OPUS@\upstream\celt\kiss_fft.c:286:          scratch[0] = *Fout0;
	l32i.n	a2, sp, 32	# %sfp,
	l32i.n	a3, sp, 32	# %sfp,
	l32i.n	a2, a2, 0	# MEM[base: Fout0_175, offset: 0B],
	l32i.n	a3, a3, 4	# MEM[base: Fout0_175, offset: 4B],
	s32i	a2, sp, 156	# %sfp,
	s32i	a3, sp, 164	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i	a4, sp, 100	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a6, a4, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:288:          C_MUL_TABLE(scratch[1] ,*Fout1, tw[u*fstride]);
#NO_APP
	l32i.n	a5, sp, 44	# %sfp,
	slli	a7, a6, 16	# tmp1593, value,
	l32i.n	a2, a5, 4	# MEM[base: Fout1_206, offset: 4B], _730
	l32i.n	a3, a5, 0	# MEM[base: Fout1_206, offset: 0B], _716
	srai	a7, a7, 16	# _714, tmp1593,
	srai	a6, a6, 16	# _729, value,
	srai	a5, a3, 16	# _717, _716,
	srai	a4, a2, 16	# _731, _730,
	extui	a3, a3, 0, 16	# _724, _716,
	extui	a2, a2, 0, 16	# _738, _730,
	mull	a9, a7, a5	# tmp1596, _714, _717
	mull	a11, a7, a3	# tmp1598, _714, _724
	mull	a10, a6, a4	# tmp1601, _729, _731
	mull	a8, a6, a2	# tmp1603, _729, _738
	mull	a5, a5, a6	# tmp1606, _717, _729
	mull	a3, a3, a6	# tmp1608, _724, _729
	mull	a4, a7, a4	# tmp1611, _714, _731
	mull	a2, a7, a2	# tmp1613, _714, _738
	srai	a11, a11, 15	# tmp1599, tmp1598,
	srai	a8, a8, 15	# tmp1604, tmp1603,
	srai	a3, a3, 15	# tmp1609, tmp1608,
	srai	a2, a2, 15	# tmp1614, tmp1613,
	slli	a9, a9, 1	# tmp1597, tmp1596,
	slli	a10, a10, 1	# tmp1602, tmp1601,
	slli	a5, a5, 1	# tmp1607, tmp1606,
	slli	a4, a4, 1	# tmp1612, tmp1611,
	add.n	a9, a9, a11	# tmp1600, tmp1597, tmp1599
	add.n	a10, a10, a8	# tmp1605, tmp1602, tmp1604
	add.n	a5, a5, a3	# tmp1610, tmp1607, tmp1609
	add.n	a4, a4, a2	# tmp1615, tmp1612, tmp1614
	sub	a10, a9, a10	#, tmp1600, tmp1605
	add.n	a4, a5, a4	#, tmp1610, tmp1615
	s32i	a10, sp, 76	# %sfp,
	s32i	a4, sp, 80	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i	a6, sp, 96	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a8, a6, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:289:          C_MUL_TABLE(scratch[2] ,*Fout2, tw[2*u*fstride]);
#NO_APP
	l32i.n	a7, sp, 36	# %sfp,
	slli	a9, a8, 16	# tmp1617, value,
	l32i.n	a3, a7, 0	# MEM[base: Fout2_510, offset: 0B], _768
	l32i.n	a2, a7, 4	# MEM[base: Fout2_510, offset: 4B], _782
	srai	a9, a9, 16	# _766, tmp1617,
	srai	a8, a8, 16	# _781, value,
	srai	a5, a3, 16	# _769, _768,
	srai	a4, a2, 16	# _783, _782,
	extui	a3, a3, 0, 16	# _776, _768,
	extui	a2, a2, 0, 16	# _790, _782,
	mull	a12, a9, a5	# tmp1620, _766, _769
	mull	a14, a9, a3	# tmp1622, _766, _776
	mull	a13, a8, a4	# tmp1625, _781, _783
	mull	a10, a8, a2	# tmp1627, _781, _790
	mull	a5, a5, a8	# tmp1630, _769, _781
	mull	a3, a3, a8	# tmp1632, _776, _781
	mull	a4, a9, a4	# tmp1635, _766, _783
	mull	a2, a9, a2	# tmp1637, _766, _790
	srai	a14, a14, 15	# tmp1623, tmp1622,
	srai	a10, a10, 15	# tmp1628, tmp1627,
	srai	a3, a3, 15	# tmp1633, tmp1632,
	srai	a2, a2, 15	# tmp1638, tmp1637,
	slli	a12, a12, 1	# tmp1621, tmp1620,
	slli	a13, a13, 1	# tmp1626, tmp1625,
	slli	a5, a5, 1	# tmp1631, tmp1630,
	slli	a4, a4, 1	# tmp1636, tmp1635,
	add.n	a12, a12, a14	# tmp1624, tmp1621, tmp1623
	add.n	a13, a13, a10	# tmp1629, tmp1626, tmp1628
	add.n	a5, a5, a3	# tmp1634, tmp1631, tmp1633
	add.n	a4, a4, a2	# tmp1639, tmp1636, tmp1638
	sub	a6, a12, a13	# _795, tmp1624, tmp1629
	add.n	a7, a5, a4	# _812, tmp1634, tmp1639
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i	a8, sp, 92	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a4, a8, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:290:          C_MUL_TABLE(scratch[3] ,*Fout3, tw[3*u*fstride]);
#NO_APP
	l32i.n	a9, sp, 40	# %sfp,
	slli	a12, a4, 16	# tmp1641, value,
	l32i.n	a3, a9, 0	# MEM[base: Fout3_524, offset: 0B], _820
	l32i.n	a2, a9, 4	# MEM[base: Fout3_524, offset: 4B], _834
	srai	a12, a12, 16	# _818, tmp1641,
	srai	a4, a4, 16	# _833, value,
	srai	a5, a3, 16	# _821, _820,
	srai	a11, a2, 16	# _835, _834,
	extui	a3, a3, 0, 16	# _828, _820,
	extui	a2, a2, 0, 16	# _842, _834,
	mull	a14, a5, a4	# tmp1652, _821, _833
	mull	a10, a3, a4	# tmp1654, _828, _833
	mull	a13, a12, a11	# tmp1657, _818, _835
	mull	a15, a12, a2	# tmp1659, _818, _842
	mull	a5, a12, a5	# tmp1642, _818, _821
	mull	a3, a12, a3	# tmp1644, _818, _828
	mull	a11, a4, a11	# tmp1648, _833, _835
	mull	a2, a4, a2	# tmp1650, _833, _842
	slli	a14, a14, 1	# tmp1653, tmp1652,
	srai	a15, a15, 15	# tmp1660, tmp1659,
	srai	a10, a10, 15	# tmp1655, tmp1654,
	slli	a13, a13, 1	# tmp1658, tmp1657,
	slli	a5, a5, 1	# tmp1643, tmp1642,
	srai	a3, a3, 15	# tmp1645, tmp1644,
	slli	a11, a11, 1	# tmp1649, tmp1648,
	srai	a2, a2, 15	# tmp1651, tmp1650,
	add.n	a10, a14, a10	# tmp1656, tmp1653, tmp1655
	add.n	a13, a13, a15	# tmp1661, tmp1658, tmp1660
	add.n	a8, a11, a2	# _846, tmp1649, tmp1651
	add.n	a9, a5, a3	# _832, tmp1643, tmp1645
	add.n	a10, a10, a13	# _864, tmp1656, tmp1661
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i	a11, sp, 88	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a11, 0	# value,
# 0 "" 2
# @OPUS@\upstream\celt\kiss_fft.c:291:          C_MUL_TABLE(scratch[4] ,*Fout4, tw[4*u*fstride]);
#NO_APP
	l32i.n	a12, sp, 48	# %sfp,
	slli	a5, a3, 16	# tmp1663, value,
	l32i.n	a2, a12, 0	# MEM[base: Fout4_562, offset: 0B], _872
	l32i.n	a11, a12, 4	# MEM[base: Fout4_562, offset: 4B], _886
	srai	a5, a5, 16	# _870, tmp1663,
	srai	a3, a3, 16	# _885, value,
	srai	a15, a2, 16	# _873, _872,
	srai	a13, a11, 16	# _887, _886,
	extui	a2, a2, 0, 16	# _880, _872,
	extui	a11, a11, 0, 16	# _894, _886,
	mull	a4, a3, a13	# tmp1670, _885, _887
	mull	a14, a3, a11	# tmp1672, _885, _894
	mull	a12, a15, a3	# tmp1674, _873, _885
	mull	a13, a5, a13	# tmp1679, _870, _887
	mull	a3, a2, a3	# tmp1676, _880, _885
	mull	a11, a5, a11	# tmp1681, _870, _894
	slli	a12, a12, 1	# tmp1675, tmp1674,
	srai	a11, a11, 15	# tmp1682, tmp1681,
	srai	a3, a3, 15	# tmp1677, tmp1676,
	slli	a13, a13, 1	# tmp1680, tmp1679,
	add.n	a3, a12, a3	# tmp1678, tmp1675, tmp1677
	add.n	a13, a13, a11	# tmp1683, tmp1680, tmp1682
	mull	a15, a5, a15	# tmp1664, _870, _873
	mull	a2, a5, a2	# tmp1666, _870, _880
	slli	a4, a4, 1	# tmp1671, tmp1670,
	add.n	a5, a3, a13	# _916, tmp1678, tmp1683
	srai	a14, a14, 15	# tmp1673, tmp1672,
# @OPUS@\upstream\celt\kiss_fft.c:293:          C_ADD( scratch[7],scratch[1],scratch[4]);
	l32i	a3, sp, 76	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:291:          C_MUL_TABLE(scratch[4] ,*Fout4, tw[4*u*fstride]);
	add.n	a14, a4, a14	# _898, tmp1671, tmp1673
	slli	a15, a15, 1	# tmp1665, tmp1664,
	srai	a2, a2, 15	# tmp1667, tmp1666,
	add.n	a4, a15, a2	# _884, tmp1665, tmp1667
# @OPUS@\upstream\celt\kiss_fft.c:293:          C_ADD( scratch[7],scratch[1],scratch[4]);
	l32i	a11, sp, 80	# %sfp,
	sub	a2, a3, a14	# tmp1684,, _898
	add.n	a2, a2, a4	#, tmp1684, _884
	s32i.n	a2, sp, 60	# %sfp,
	add.n	a11, a11, a5	#,, _916
# @OPUS@\upstream\celt\kiss_fft.c:295:          C_ADD( scratch[8],scratch[2],scratch[3]);
	sub	a15, a6, a8	# tmp1686, _795, _846
# @OPUS@\upstream\celt\kiss_fft.c:293:          C_ADD( scratch[7],scratch[1],scratch[4]);
	s32i	a11, sp, 68	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:294:          C_SUB( scratch[10],scratch[1],scratch[4]);
	sub	a4, a3, a4	# tmp1685,, _884
# @OPUS@\upstream\celt\kiss_fft.c:296:          C_SUB( scratch[9],scratch[2],scratch[3]);
	sub	a11, a6, a9	# tmp1687, _795, _832
# @OPUS@\upstream\celt\kiss_fft.c:294:          C_SUB( scratch[10],scratch[1],scratch[4]);
	l32i	a3, sp, 80	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	l32i.n	a6, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:295:          C_ADD( scratch[8],scratch[2],scratch[3]);
	add.n	a12, a15, a9	#, tmp1686, _832
# @OPUS@\upstream\celt\kiss_fft.c:294:          C_SUB( scratch[10],scratch[1],scratch[4]);
	add.n	a4, a4, a14	# _922, tmp1685, _898
	sub	a5, a3, a5	# _924,, _916
# @OPUS@\upstream\celt\kiss_fft.c:296:          C_SUB( scratch[9],scratch[2],scratch[3]);
	add.n	a11, a11, a8	# _930, tmp1687, _846
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	srai	a9, a12, 16	#,,
	l32i.n	a8, sp, 60	# %sfp,
	srai	a6, a6, 16	#,,
# @OPUS@\upstream\celt\kiss_fft.c:295:          C_ADD( scratch[8],scratch[2],scratch[3]);
	add.n	a2, a7, a10	#, _812, _864
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	l32i	a14, sp, 68	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:296:          C_SUB( scratch[9],scratch[2],scratch[3]);
	sub	a7, a7, a10	# _932, _812, _864
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	s32i	a6, sp, 188	# %sfp,
	s32i	a9, sp, 76	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	srai	a6, a5, 16	#, _924,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	srai	a9, a4, 16	#, _922,
	extui	a5, a5, 0, 16	#, _924,
	extui	a4, a4, 0, 16	#, _922,
# @OPUS@\upstream\celt\kiss_fft.c:295:          C_ADD( scratch[8],scratch[2],scratch[3]);
	s32i	a2, sp, 84	# %sfp,
	extui	a10, a8, 0, 16	# _951,,
	s32i	a12, sp, 72	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	srai	a8, a7, 16	#, _932,
	extui	a12, a12, 0, 16	#,,
	s32i	a5, sp, 108	# %sfp,
	extui	a7, a7, 0, 16	#, _932,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	l32r	a5, .LC2	#,
	s32i	a4, sp, 172	# %sfp,
	l32i	a4, sp, 188	# %sfp,
	s32i	a12, sp, 80	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	srai	a15, a14, 16	# _971,,
	l32i	a3, sp, 84	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	srai	a12, a11, 16	#, _930,
	s32i	a7, sp, 116	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	l32r	a7, .LC3	#,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	s32i	a6, sp, 104	# %sfp,
	s32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	l32i	a6, sp, 76	# %sfp,
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	s32i	a12, sp, 120	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	mull	a12, a4, a5	# tmp1694,,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	mull	a4, a15, a5	#, _971,
	extui	a2, a14, 0, 16	# _978,,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	s32i	a9, sp, 168	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	srai	a14, a3, 16	# _983,,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	mov.n	a9, a7	#,
	extui	a3, a3, 0, 16	# _990,,
	extui	a11, a11, 0, 16	#, _930,
	mull	a13, a10, a5	# tmp1697, _951,
	s32i	a11, sp, 124	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	s32i	a4, sp, 192	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	mull	a11, a6, a7	# tmp1701,,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	mull	a4, a3, a9	# tmp1719, _990,
	mull	a6, a2, a5	# tmp1712, _978,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	mull	a7, a8, a7	# tmp1704,, tmp9
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	mull	a5, a14, a9	# tmp1716, _983,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	l32i	a8, sp, 104	# %sfp,
	l32r	a9, .LC4	#,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	srai	a6, a6, 15	# tmp1714, tmp1712,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	mull	a8, a8, a9	#,,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	slli	a5, a5, 1	# tmp1718, tmp1716,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	s32i	a8, sp, 140	# %sfp,
	l32i	a8, sp, 108	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	srai	a4, a4, 15	# tmp1721, tmp1719,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	mull	a8, a8, a9	#,,
	l32i	a9, sp, 112	# %sfp,
	s32i	a8, sp, 144	# %sfp,
	l32r	a8, .LC5	#,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	slli	a11, a11, 1	# tmp1703, tmp1701,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	mull	a9, a9, a8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	srai	a7, a7, 15	# tmp1706, tmp1704,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	s32i	a9, sp, 148	# %sfp,
	l32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	srai	a13, a13, 15	# tmp1699, tmp1697,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	mull	a9, a9, a8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	l32i	a8, sp, 168	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	s32i	a9, sp, 152	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	l32r	a9, .LC4	#,
	mull	a8, a8, a9	#,,
	s32i	a8, sp, 196	# %sfp,
	l32i	a8, sp, 172	# %sfp,
	mull	a8, a8, a9	#,,
	l32i	a9, sp, 120	# %sfp,
	s32i	a8, sp, 200	# %sfp,
	l32r	a8, .LC5	#,
	mull	a9, a9, a8	#,,
	s32i	a9, sp, 204	# %sfp,
	l32i	a9, sp, 124	# %sfp,
	mull	a9, a9, a8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	l32r	a8, .LC3	#,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	s32i	a9, sp, 208	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	l32r	a9, .LC2	#,
	mull	a15, a15, a8	# tmp1771, _971,
	mull	a14, a14, a9	#, _983,
	mull	a3, a3, a9	# tmp1781, _990,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	slli	a9, a12, 1	# tmp1696, tmp1694,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	l32i	a12, sp, 192	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	mull	a2, a2, a8	# tmp1774, _978,
	s32i	a14, sp, 268	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	slli	a8, a12, 1	# tmp1711,,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	l32i	a14, sp, 188	# %sfp,
	l32r	a12, .LC3	#,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	add.n	a8, a8, a6	# tmp1715, tmp1711, tmp1714
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	mull	a14, a14, a12	#,,
	mull	a10, a10, a12	#, _951,
	s32i	a14, sp, 260	# %sfp,
	s32i	a10, sp, 264	# %sfp,
	l32i	a14, sp, 76	# %sfp,
	l32r	a10, .LC2	#,
	l32i	a12, sp, 80	# %sfp,
	mull	a14, a14, a10	#,,
	mull	a12, a12, a10	#,,
	s32i	a14, sp, 212	# %sfp,
	s32i	a12, sp, 216	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	l32i.n	a14, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	l32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	l32i.n	a14, a14, 0	# MEM[base: Fout0_175, offset: 0B],
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	l32i.n	a10, a10, 4	# MEM[base: Fout0_175, offset: 4B],
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	l32i	a6, sp, 148	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	s32i	a10, sp, 256	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	l32i	a10, sp, 196	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	s32i	a14, sp, 252	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	slli	a10, a10, 1	#,,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	add.n	a14, a5, a4	# tmp1722, tmp1718, tmp1721
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	l32i	a4, sp, 144	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	s32i	a10, sp, 144	# %sfp,
	l32i	a10, sp, 204	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	add.n	a12, a11, a7	# tmp1707, tmp1703, tmp1706
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	srai	a2, a2, 15	#, tmp1774,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	l32i	a11, sp, 140	# %sfp,
	l32i	a7, sp, 152	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	add.n	a9, a9, a13	# tmp1700, tmp1696, tmp1699
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	srai	a5, a4, 15	# tmp1729,,
	slli	a13, a6, 1	# tmp1733,,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	l32i	a4, sp, 200	# %sfp,
	slli	a6, a10, 1	# tmp1747,,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	s32i	a2, sp, 80	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	l32i	a10, sp, 208	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	l32i	a2, sp, 268	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	slli	a11, a11, 1	#,,
	s32i	a11, sp, 140	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	slli	a2, a2, 1	#,,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	srai	a11, a7, 15	# tmp1736,,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	srai	a7, a4, 15	# tmp1743,,
	srai	a4, a10, 15	# tmp1750,,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	slli	a10, a15, 1	#, tmp1771,
	s32i	a10, sp, 148	# %sfp,
	s32i	a2, sp, 152	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	l32i	a10, sp, 112	# %sfp,
	l32r	a2, .LC4	#,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	add.n	a14, a8, a14	#, tmp1715, tmp1722
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	mull	a10, a10, a2	#,,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	add.n	a9, a9, a12	# tmp1708, tmp1700, tmp1707
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	s32i	a10, sp, 112	# %sfp,
	l32i	a10, sp, 116	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	add.n	a6, a6, a4	# tmp1751, tmp1747, tmp1750
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	mull	a10, a10, a2	#,,
	l32i	a2, sp, 104	# %sfp,
	s32i	a10, sp, 116	# %sfp,
	l32r	a10, .LC5	#,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	add.n	a13, a13, a11	# tmp1737, tmp1733, tmp1736
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	mull	a2, a2, a10	#,,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	srai	a3, a3, 15	# tmp1783, tmp1781,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	s32i	a2, sp, 104	# %sfp,
	l32i	a2, sp, 108	# %sfp,
	mull	a2, a2, a10	#,,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	l32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	s32i	a2, sp, 108	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	l32r	a2, .LC4	#,
	mull	a10, a10, a2	#,,
	s32i	a10, sp, 120	# %sfp,
	l32i	a10, sp, 124	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	l32i	a12, sp, 140	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	mull	a10, a10, a2	#,,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	l32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	s32i	a10, sp, 124	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	l32i	a10, sp, 72	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	s32i.n	a14, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	add.n	a15, a2, a10	# tmp1688,,
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	l32i	a10, sp, 84	# %sfp,
	l32i	a2, sp, 68	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	l32i	a14, sp, 144	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	add.n	a2, a2, a10	#,,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	l32i	a4, sp, 264	# %sfp,
	l32i	a8, sp, 212	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	s32i	a2, sp, 76	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	add.n	a5, a12, a5	# tmp1730,, tmp1729
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	l32i	a2, sp, 260	# %sfp,
	l32i	a12, sp, 216	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	add.n	a7, a14, a7	# tmp1744,, tmp1743
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	srai	a10, a4, 15	# tmp1761,,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	l32i	a14, sp, 148	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	slli	a4, a8, 1	# tmp1765,,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	srai	a11, a12, 15	# tmp1768,,
	slli	a2, a2, 1	#,,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	l32i	a12, sp, 152	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	s32i	a2, sp, 84	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	add.n	a2, a14, a8	# tmp1777,,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	l32r	a8, .LC5	#,
	l32i	a14, sp, 168	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	add.n	a3, a12, a3	# tmp1784,, tmp1783
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	l32i	a12, sp, 172	# %sfp,
	mull	a14, a14, a8	#,,
	mull	a12, a12, a8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	add.n	a6, a7, a6	#, tmp1744, tmp1751
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	s32i	a14, sp, 68	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	l32i	a14, sp, 156	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	s32i	a12, sp, 72	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	l32i.n	a12, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:305:          scratch[6].i = NEG32_ovflw(ADD32_ovflw(S_MUL(scratch[10].r,ya.i), S_MUL(scratch[9].r,yb.i)));
	s32i.n	a6, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	l32i	a6, sp, 252	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:301:          scratch[5].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,ya.r), S_MUL(scratch[8].r,yb.r)));
	add.n	a9, a9, a14	# _969, tmp1708,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	l32i	a14, sp, 164	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	add.n	a15, a6, a15	# tmp1689,, tmp1688
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	l32i	a6, sp, 84	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:302:          scratch[5].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,ya.r), S_MUL(scratch[8].i,yb.r)));
	add.n	a8, a12, a14	# _996,,
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	l32i	a7, sp, 256	# %sfp,
	l32i	a12, sp, 76	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	add.n	a10, a6, a10	#,, tmp1761
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	add.n	a14, a7, a12	# tmp1692,,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	s32i	a10, sp, 76	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	l32i	a7, sp, 112	# %sfp,
	l32i	a10, sp, 116	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:304:          scratch[6].r =  ADD32_ovflw(S_MUL(scratch[10].i,ya.i), S_MUL(scratch[9].i,yb.i));
	add.n	a5, a5, a13	# _1021, tmp1730, tmp1737
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	l32i	a6, sp, 108	# %sfp,
	slli	a13, a7, 1	# tmp1788,,
	srai	a7, a10, 15	# tmp1791,,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	l32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	add.n	a4, a4, a11	# tmp1769, tmp1765, tmp1768
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	add.n	a2, a2, a3	# tmp1785, tmp1777, tmp1784
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	l32i	a11, sp, 104	# %sfp,
	srai	a3, a6, 15	# tmp1797,,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	slli	a6, a10, 1	# tmp1806,,
	l32i	a10, sp, 124	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	slli	a12, a11, 1	# tmp1794,,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	srai	a11, a10, 15	# tmp1809,,
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	l32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	add.n	a6, a6, a11	# _1124, tmp1806, tmp1809
# @OPUS@\upstream\celt\kiss_fft.c:298:          Fout0->r = ADD32_ovflw(Fout0->r, ADD32_ovflw(scratch[7].r, scratch[8].r));
	s32i.n	a15, a10, 0	# MEM[base: Fout0_175, offset: 0B], tmp1689
# @OPUS@\upstream\celt\kiss_fft.c:299:          Fout0->i = ADD32_ovflw(Fout0->i, ADD32_ovflw(scratch[7].i, scratch[8].i));
	s32i.n	a14, a10, 4	# MEM[base: Fout0_175, offset: 4B], tmp1692
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	l32i	a14, sp, 164	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:307:          C_SUB(*Fout1,scratch[5],scratch[6]);
	l32i.n	a10, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:311:          scratch[11].i = ADD32_ovflw(scratch[0].i, ADD32_ovflw(S_MUL(scratch[7].i,yb.r), S_MUL(scratch[8].i,ya.r)));
	add.n	a2, a2, a14	# _1091, tmp1785,
# @OPUS@\upstream\celt\kiss_fft.c:307:          C_SUB(*Fout1,scratch[5],scratch[6]);
	add.n	a11, a8, a10	# tmp1753, _996,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	l32i	a14, sp, 76	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	l32i	a10, sp, 68	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	add.n	a4, a14, a4	# tmp1770,, tmp1769
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	slli	a14, a10, 1	# tmp1800,,
	l32i	a10, sp, 72	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	add.n	a3, a12, a3	# _1107, tmp1794, tmp1797
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	srai	a15, a10, 15	# tmp1803,,
# @OPUS@\upstream\celt\kiss_fft.c:307:          C_SUB(*Fout1,scratch[5],scratch[6]);
	l32i.n	a10, sp, 44	# %sfp,
	sub	a12, a9, a5	# tmp1752, _969, _1021
	s32i.n	a11, a10, 4	# MEM[base: Fout1_206, offset: 4B], tmp1753
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	l32i	a11, sp, 156	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:307:          C_SUB(*Fout1,scratch[5],scratch[6]);
	s32i.n	a12, a10, 0	# MEM[base: Fout1_206, offset: 0B], tmp1752
# @OPUS@\upstream\celt\kiss_fft.c:308:          C_ADD(*Fout4,scratch[5],scratch[6]);
	l32i.n	a12, sp, 60	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:310:          scratch[11].r = ADD32_ovflw(scratch[0].r, ADD32_ovflw(S_MUL(scratch[7].r,yb.r), S_MUL(scratch[8].r,ya.r)));
	add.n	a4, a4, a11	# _1073, tmp1770,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	add.n	a7, a13, a7	# _1099, tmp1788, tmp1791
# @OPUS@\upstream\celt\kiss_fft.c:308:          C_ADD(*Fout4,scratch[5],scratch[6]);
	l32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:313:          scratch[12].i = SUB32_ovflw(S_MUL(scratch[10].r,yb.i), S_MUL(scratch[9].r,ya.i));
	add.n	a14, a14, a15	# _1116, tmp1800, tmp1803
# @OPUS@\upstream\celt\kiss_fft.c:308:          C_ADD(*Fout4,scratch[5],scratch[6]);
	add.n	a5, a9, a5	# tmp1754, _969, _1021
	sub	a8, a8, a12	# tmp1755, _996,
# @OPUS@\upstream\celt\kiss_fft.c:312:          scratch[12].r = SUB32_ovflw(S_MUL(scratch[9].i,ya.i), S_MUL(scratch[10].i,yb.i));
	sub	a10, a7, a3	# tmp1810, _1099, _1107
# @OPUS@\upstream\celt\kiss_fft.c:315:          C_ADD(*Fout2,scratch[11],scratch[12]);
	l32i.n	a12, sp, 36	# %sfp,
	sub	a9, a2, a6	# tmp1812, _1091, _1124
# @OPUS@\upstream\celt\kiss_fft.c:308:          C_ADD(*Fout4,scratch[5],scratch[6]);
	s32i.n	a5, a11, 0	# MEM[base: Fout4_562, offset: 0B], tmp1754
	s32i.n	a8, a11, 4	# MEM[base: Fout4_562, offset: 4B], tmp1755
# @OPUS@\upstream\celt\kiss_fft.c:315:          C_ADD(*Fout2,scratch[11],scratch[12]);
	add.n	a10, a10, a4	# tmp1811, tmp1810, _1073
	add.n	a9, a9, a14	# tmp1813, tmp1812, _1116
# @OPUS@\upstream\celt\kiss_fft.c:316:          C_SUB(*Fout3,scratch[11],scratch[12]);
	sub	a2, a2, a14	# tmp1816, _1091, _1116
	l32i.n	a14, sp, 40	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:315:          C_ADD(*Fout2,scratch[11],scratch[12]);
	s32i.n	a10, a12, 0	# MEM[base: Fout2_510, offset: 0B], tmp1811
	s32i.n	a9, a12, 4	# MEM[base: Fout2_510, offset: 4B], tmp1813
# @OPUS@\upstream\celt\kiss_fft.c:316:          C_SUB(*Fout3,scratch[11],scratch[12]);
	add.n	a2, a2, a6	# tmp1817, tmp1816, _1124
	sub	a7, a3, a7	# tmp1814, _1107, _1099
	s32i.n	a2, a14, 4	# MEM[base: Fout3_524, offset: 4B], tmp1817
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	l32i.n	a3, sp, 44	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	l32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:316:          C_SUB(*Fout3,scratch[11],scratch[12]);
	add.n	a4, a7, a4	# tmp1815, tmp1814, _1073
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	addi.n	a2, a2, 8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	addi.n	a3, a3, 8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:316:          C_SUB(*Fout3,scratch[11],scratch[12]);
	s32i.n	a4, a14, 0	# MEM[base: Fout3_524, offset: 0B], tmp1815
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	addi.n	a12, a12, 8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	addi.n	a11, a11, 8	#,,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	s32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	s32i.n	a3, sp, 44	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	s32i.n	a12, sp, 36	# %sfp,
	l32i	a4, sp, 100	# %sfp,
	l32i	a6, sp, 96	# %sfp,
	l32i	a8, sp, 92	# %sfp,
	l32i	a10, sp, 88	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	s32i.n	a11, sp, 48	# %sfp,
	l32i	a5, sp, 236	# %sfp,
	l32i	a7, sp, 232	# %sfp,
	l32i	a9, sp, 240	# %sfp,
	l32i	a11, sp, 228	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	addi.n	a14, a14, 8	#,,
	add.n	a4, a4, a5	#,,
	add.n	a6, a6, a7	#,,
	add.n	a8, a8, a9	#,,
	add.n	a10, a10, a11	#,,
# @OPUS@\upstream\celt\kiss_fft.c:285:       for ( u=0; u<m; ++u ) {
	l32i.n	a12, sp, 56	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:318:          ++Fout0;++Fout1;++Fout2;++Fout3;++Fout4;
	s32i.n	a14, sp, 40	# %sfp,
	s32i	a4, sp, 100	# %sfp,
	s32i	a6, sp, 96	# %sfp,
	s32i	a8, sp, 92	# %sfp,
	s32i	a10, sp, 88	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:285:       for ( u=0; u<m; ++u ) {
	bne	a2, a12, .L54	#,,
# @OPUS@\upstream\celt\kiss_fft.c:275:    for (i=0;i<N;i++)
	l32i	a14, sp, 136	# %sfp,
	l32i	a2, sp, 64	# %sfp,
	l32i	a3, sp, 184	# %sfp,
	addi.n	a14, a14, 1	#,,
	add.n	a2, a2, a3	#,,
	add.n	a12, a12, a3	#,,
# @OPUS@\upstream\celt\kiss_fft.c:275:    for (i=0;i<N;i++)
	l32i	a4, sp, 220	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:275:    for (i=0;i<N;i++)
	s32i	a14, sp, 136	# %sfp,
	s32i	a2, sp, 64	# %sfp,
	s32i.n	a12, sp, 56	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:275:    for (i=0;i<N;i++)
	bne	a4, a14, .L55	#,,
.L41:
# @OPUS@\upstream\celt\kiss_fft.c:555:     for (i=L-1;i>=0;i--)
	l32i	a5, sp, 128	# %sfp,
	l32i	a6, sp, 132	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:578:        m = m2;
	l32i	a7, sp, 176	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:555:     for (i=L-1;i>=0;i--)
	addi.n	a5, a5, -1	#,,
	addi	a6, a6, -4	#,,
	s32i	a5, sp, 128	# %sfp,
	s32i	a6, sp, 132	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:578:        m = m2;
	s32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\celt\kiss_fft.c:555:     for (i=L-1;i>=0;i--)
	bnei	a5, -1, .L56	#,,
# @OPUS@\upstream\celt\kiss_fft.c:580: }
	movi	a9, 0x120	#,
	l32i	a12, sp, 284	#,
	l32i	a13, sp, 280	#,
	l32i	a14, sp, 276	#,
	l32i	a15, sp, 272	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	opus_fft_impl, .-opus_fft_impl
	.section	.text.opus_fft_c,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_fft_c
	.type	opus_fft_c, @function
# Function: opus_fft_c
# Module: upstream/celt/kiss_fft.c
# Fixed-point FFT used by CELT inverse transforms.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void opus_fft_c(const kiss_fft_state *st,const kiss_fft_cpx *fin,kiss_fft_cpx *fout)
# C context: {
# C context: int i;
# C context: opus_val16 scale;
# C context: #ifdef FIXED_POINT
opus_fft_c:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\kiss_fft.c:589:    int scale_shift = st->scale_shift-1;
	l32i.n	a10, a2, 8	# st_33(D)->scale_shift, st_33(D)->scale_shift
# @OPUS@\upstream\celt\kiss_fft.c:595:    for (i=0;i<st->nfft;i++)
	l32i.n	a11, a2, 0	# st_33(D)->nfft, _7
# @OPUS@\upstream\celt\kiss_fft.c:583: {
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
	s32i.n	a13, sp, 4	#,
# @OPUS@\upstream\celt\kiss_fft.c:589:    int scale_shift = st->scale_shift-1;
	addi.n	a10, a10, -1	# scale_shift, st_33(D)->scale_shift,
# @OPUS@\upstream\celt\kiss_fft.c:591:    scale = st->scale;
	l16si	a8, a2, 4	# st_33(D)->scale, scale
# @OPUS@\upstream\celt\kiss_fft.c:595:    for (i=0;i<st->nfft;i++)
	bgei	a11, 1, .L95	# _7,,
.L97:
# @OPUS@\upstream\celt\kiss_fft.c:601:    opus_fft_impl(st, fout);
	mov.n	a3, a4	#, fout
	call0	opus_fft_impl		#
# @OPUS@\upstream\celt\kiss_fft.c:602: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
.L95:
	slli	a11, a11, 3	# tmp80, _7,
	l32i.n	a9, a2, 48	# st_33(D)->bitrev, ivtmp$286
	mov.n	a7, a3	# ivtmp$285, fin
	add.n	a11, a3, a11	# _78, ivtmp$285, tmp80
.L96:
# @OPUS@\upstream\celt\kiss_fft.c:597:       kiss_fft_cpx x = fin[i];
	l32i.n	a13, a7, 0	# MEM[base: _83, offset: 0B], x$r
	l32i.n	a12, a7, 4	# MEM[base: _83, offset: 4B], x$i
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	extui	a6, a13, 0, 16	# tmp85, x$r,
# @OPUS@\upstream\celt\kiss_fft.c:599:       fout[st->bitrev[i]].i = SHR32(MULT16_32_Q16(scale, x.i), scale_shift);
	extui	a5, a12, 0, 16	# tmp92, x$i,
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	mull	a6, a6, a8	# tmp86, tmp85, scale
	srai	a13, a13, 16	# tmp88, x$r,
# @OPUS@\upstream\celt\kiss_fft.c:599:       fout[st->bitrev[i]].i = SHR32(MULT16_32_Q16(scale, x.i), scale_shift);
	mull	a5, a5, a8	# tmp93, tmp92, scale
	srai	a12, a12, 16	# tmp95, x$i,
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	l16si	a3, a9, 0	# MEM[base: _82, offset: 0B], tmp81
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	mull	a13, a13, a8	# tmp89, tmp88, scale
# @OPUS@\upstream\celt\kiss_fft.c:599:       fout[st->bitrev[i]].i = SHR32(MULT16_32_Q16(scale, x.i), scale_shift);
	mull	a12, a12, a8	# tmp96, tmp95, scale
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	srai	a6, a6, 16	# tmp87, tmp86,
# @OPUS@\upstream\celt\kiss_fft.c:599:       fout[st->bitrev[i]].i = SHR32(MULT16_32_Q16(scale, x.i), scale_shift);
	srai	a5, a5, 16	# tmp94, tmp93,
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	slli	a3, a3, 3	# tmp84, tmp81,
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	add.n	a6, a6, a13	# tmp90, tmp87, tmp89
# @OPUS@\upstream\celt\kiss_fft.c:599:       fout[st->bitrev[i]].i = SHR32(MULT16_32_Q16(scale, x.i), scale_shift);
	add.n	a5, a5, a12	# tmp97, tmp94, tmp96
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	add.n	a3, a4, a3	# _19, fout, tmp84
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	ssr	a10	# scale_shift
	sra	a6, a6	# tmp91, tmp90
# @OPUS@\upstream\celt\kiss_fft.c:599:       fout[st->bitrev[i]].i = SHR32(MULT16_32_Q16(scale, x.i), scale_shift);
	ssr	a10	# scale_shift
	sra	a5, a5	# tmp98, tmp97
# @OPUS@\upstream\celt\kiss_fft.c:598:       fout[st->bitrev[i]].r = SHR32(MULT16_32_Q16(scale, x.r), scale_shift);
	s32i.n	a6, a3, 0	# _19->r, tmp91
# @OPUS@\upstream\celt\kiss_fft.c:599:       fout[st->bitrev[i]].i = SHR32(MULT16_32_Q16(scale, x.i), scale_shift);
	s32i.n	a5, a3, 4	# _19->i, tmp98
	addi.n	a7, a7, 8	# ivtmp$285, ivtmp$285,
	addi.n	a9, a9, 2	# ivtmp$286, ivtmp$286,
# @OPUS@\upstream\celt\kiss_fft.c:595:    for (i=0;i<st->nfft;i++)
	bne	a11, a7, .L96	# _78, ivtmp$285,
	j	.L97		#
	.size	opus_fft_c, .-opus_fft_c
	.section	.text.opus_ifft_c,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_ifft_c
	.type	opus_ifft_c, @function
# Function: opus_ifft_c
# Module: upstream/celt/kiss_fft.c
# Fixed-point FFT used by CELT inverse transforms.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context:
# C context: void opus_ifft_c(const kiss_fft_state *st,const kiss_fft_cpx *fin,kiss_fft_cpx *fout)
# C context: {
# C context: int i;
# C context: celt_assert2 (fin != fout, "In-place FFT not supported");
# C context: /* Bit-reverse the input */
opus_ifft_c:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\kiss_fft.c:610:    for (i=0;i<st->nfft;i++)
	l32i.n	a7, a2, 0	# st_31(D)->nfft, _44
# @OPUS@\upstream\celt\kiss_fft.c:606: {
	s32i.n	a12, sp, 8	#,
	s32i.n	a13, sp, 4	#,
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\kiss_fft.c:606: {
	mov.n	a13, a2	# st, st
	mov.n	a12, a4	# fout, fout
# @OPUS@\upstream\celt\kiss_fft.c:610:    for (i=0;i<st->nfft;i++)
	bgei	a7, 1, .L101	# _44,,
.L106:
# @OPUS@\upstream\celt\kiss_fft.c:614:    opus_fft_impl(st, fout);
	mov.n	a3, a12	#, fout
	mov.n	a2, a13	#, st
	call0	opus_fft_impl		#
# @OPUS@\upstream\celt\kiss_fft.c:615:    for (i=0;i<st->nfft;i++)
	l32i.n	a2, a13, 0	# st_31(D)->nfft, _46
	addi.n	a4, a12, 4	# ivtmp$291, fout,
	slli	a3, a2, 3	# tmp90, _46,
	add.n	a3, a4, a3	# _60, ivtmp$291, tmp90
# @OPUS@\upstream\celt\kiss_fft.c:615:    for (i=0;i<st->nfft;i++)
	bgei	a2, 1, .L107	# _46,,
	j	.L100		#
.L101:
	l32i.n	a4, a2, 48	# st_31(D)->bitrev, ivtmp$301
	slli	a8, a7, 1	# tmp77, _44,
	add.n	a8, a8, a4	# _78, tmp77, ivtmp$301
.L104:
# @OPUS@\upstream\celt\kiss_fft.c:611:       fout[st->bitrev[i]] = fin[i];
	l16si	a2, a4, 0	# MEM[base: _11, offset: 0B], tmp78
# @OPUS@\upstream\celt\kiss_fft.c:611:       fout[st->bitrev[i]] = fin[i];
	l32i.n	a6, a3, 0	# MEM[base: _83, offset: 0B], MEM[base: _83, offset: 0B]
	l32i.n	a5, a3, 4	# MEM[base: _83, offset: 0B], MEM[base: _83, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:611:       fout[st->bitrev[i]] = fin[i];
	slli	a2, a2, 3	# tmp81, tmp78,
# @OPUS@\upstream\celt\kiss_fft.c:611:       fout[st->bitrev[i]] = fin[i];
	add.n	a2, a12, a2	# tmp82, fout, tmp81
	s32i.n	a6, a2, 0	# *_10, MEM[base: _83, offset: 0B]
	s32i.n	a5, a2, 4	# *_10, MEM[base: _83, offset: 0B]
	addi.n	a4, a4, 2	# ivtmp$301, ivtmp$301,
	addi.n	a3, a3, 8	# ivtmp$302, ivtmp$302,
# @OPUS@\upstream\celt\kiss_fft.c:610:    for (i=0;i<st->nfft;i++)
	bne	a4, a8, .L104	# ivtmp$301, _78,
	addi.n	a2, a12, 4	# ivtmp$296, fout,
	slli	a4, a7, 3	# tmp86, _44,
	add.n	a4, a2, a4	# _28, ivtmp$296, tmp86
.L105:
# @OPUS@\upstream\celt\kiss_fft.c:613:       fout[i].i = -fout[i].i;
	l32i.n	a3, a2, 0	# MEM[base: _47, offset: 0B], MEM[base: _47, offset: 0B]
	neg	a3, a3	# tmp87, MEM[base: _47, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:613:       fout[i].i = -fout[i].i;
	s32i.n	a3, a2, 0	# MEM[base: _47, offset: 0B], tmp87
	addi.n	a2, a2, 8	# ivtmp$296, ivtmp$296,
# @OPUS@\upstream\celt\kiss_fft.c:612:    for (i=0;i<st->nfft;i++)
	bne	a4, a2, .L105	# _28, ivtmp$296,
	j	.L106		#
.L107:
# @OPUS@\upstream\celt\kiss_fft.c:616:       fout[i].i = -fout[i].i;
	l32i.n	a2, a4, 0	# MEM[base: _74, offset: 0B], MEM[base: _74, offset: 0B]
	neg	a2, a2	# tmp91, MEM[base: _74, offset: 0B]
# @OPUS@\upstream\celt\kiss_fft.c:616:       fout[i].i = -fout[i].i;
	s32i.n	a2, a4, 0	# MEM[base: _74, offset: 0B], tmp91
	addi.n	a4, a4, 8	# ivtmp$291, ivtmp$291,
# @OPUS@\upstream\celt\kiss_fft.c:615:    for (i=0;i<st->nfft;i++)
	bne	a4, a3, .L107	# ivtmp$291, _60,
.L100:
# @OPUS@\upstream\celt\kiss_fft.c:617: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	opus_ifft_c, .-opus_ifft_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
