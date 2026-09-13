# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/src/opus.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"opus.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\src\opus.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\src\opus.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\src\opus.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\src\opus.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\src\opus.c.s.raw
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
	.section	.text.encode_size,"ax",@progbits
	.literal_position
	.align	4
	.global	encode_size
	.type	encode_size, @function
# Function: encode_size
# Module: upstream/src/opus.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif
# C context:
# C context: int encode_size(int size, unsigned char *data)
# C context: {
# C context: if (size < 252)
# C context: {
# C context: data[0] = size;
encode_size:
# @OPUS@\upstream\src\opus.c:142:    if (size < 252)
	movi	a4, 0xfb	# tmp53,
	blt	a4, a2, .L2	# tmp53, size,
# @OPUS@\upstream\src\opus.c:144:       data[0] = size;
	extui	a4, a2, 0, 8	# _1, size
# @OPUS@\upstream\src\opus.c:145:       return 1;
	movi.n	a2, 1	# <retval>,
	j	.L3		#
.L2:
# @OPUS@\upstream\src\opus.c:147:       data[0] = 252+(size&0x3);
	extui	a4, a2, 0, 2	# tmp55, size,
# @OPUS@\upstream\src\opus.c:147:       data[0] = 252+(size&0x3);
	addi	a4, a4, -4	# tmp57, tmp55,
	extui	a4, a4, 0, 8	# _1, tmp57
# @OPUS@\upstream\src\opus.c:148:       data[1] = (size-(int)data[0])>>2;
	sub	a2, a2, a4	# tmp58, size, _1
# @OPUS@\upstream\src\opus.c:148:       data[1] = (size-(int)data[0])>>2;
	srai	a2, a2, 2	# tmp59, tmp58,
# @OPUS@\upstream\src\opus.c:148:       data[1] = (size-(int)data[0])>>2;
	s8i	a2, a3, 1	# MEM[(unsigned char *)data_14(D) + 1B], tmp59
# @OPUS@\upstream\src\opus.c:149:       return 2;
	movi.n	a2, 2	# <retval>,
.L3:
	s8i	a4, a3, 0	# *data_14(D), _1
# @OPUS@\upstream\src\opus.c:151: }
	ret.n
	.size	encode_size, .-encode_size
	.global	__divsi3
	.section	.text.opus_packet_get_samples_per_frame,"ax",@progbits
	.literal_position
	.align	4
	.global	opus_packet_get_samples_per_frame
	.type	opus_packet_get_samples_per_frame, @function
# Function: opus_packet_get_samples_per_frame
# Module: upstream/src/opus.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: int opus_packet_get_samples_per_frame(const unsigned char *data,
# C context: opus_int32 Fs)
# C context: {
# C context: int audiosize;
# C context: if (data[0]&0x80)
opus_packet_get_samples_per_frame:
	addi	sp, sp, -16	#,,
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\src\opus.c:177:    if (data[0]&0x80)
	l8ui	a4, a2, 0	# *data_10(D), _1
# @OPUS@\upstream\src\opus.c:175: {
	mov.n	a2, a3	# Fs, Fs
# @OPUS@\upstream\src\opus.c:177:    if (data[0]&0x80)
	slli	a3, a4, 24	# tmp59, _1,
	bgez	a3, .L6	# tmp59,
# @OPUS@\upstream\src\opus.c:179:       audiosize = ((data[0]>>3)&0x3);
	extui	a4, a4, 3, 2	# audiosize, _1,,
# @OPUS@\upstream\src\opus.c:180:       audiosize = (Fs<<audiosize)/400;
	movi	a3, 0x190	#,
	ssl	a4	# audiosize
	sll	a2, a2	#, Fs
	call0	__divsi3		#
	j	.L5		#
.L6:
# @OPUS@\upstream\src\opus.c:181:    } else if ((data[0]&0x60) == 0x60)
	movi	a3, 0x60	# tmp67,
	and	a3, a4, a3	# tmp70, _1, tmp67
	movi	a5, 0x60	# tmp71,
	bne	a3, a5, .L8	# tmp70, tmp71,
# @OPUS@\upstream\src\opus.c:183:       audiosize = (data[0]&0x08) ? Fs/50 : Fs/100;
	bbci	a4, 3, .L9	# _1,,
# @OPUS@\upstream\src\opus.c:183:       audiosize = (data[0]&0x08) ? Fs/50 : Fs/100;
	movi.n	a3, 0x32	#,
	call0	__divsi3		#
	j	.L5		#
.L9:
# @OPUS@\upstream\src\opus.c:183:       audiosize = (data[0]&0x08) ? Fs/50 : Fs/100;
	movi	a3, 0x64	#,
	call0	__divsi3		#
	j	.L5		#
.L8:
	extui	a4, a4, 3, 2	# _20, _1,,
# @OPUS@\upstream\src\opus.c:186:       if (audiosize == 3)
	bnei	a4, 3, .L10	# _20,,
# @OPUS@\upstream\src\opus.c:187:          audiosize = Fs*60/1000;
	slli	a3, a2, 4	# tmp86, Fs,
	sub	a2, a3, a2	# tmp87, tmp86, Fs
# @OPUS@\upstream\src\opus.c:187:          audiosize = Fs*60/1000;
	slli	a2, a2, 2	#, tmp87,
	movi	a3, 0x3e8	#,
	call0	__divsi3		#
	j	.L5		#
.L10:
# @OPUS@\upstream\src\opus.c:189:          audiosize = (Fs<<audiosize)/100;
	movi	a3, 0x64	#,
	ssl	a4	# _20
	sll	a2, a2	#, Fs
	call0	__divsi3		#
.L5:
# @OPUS@\upstream\src\opus.c:192: }
	l32i.n	a0, sp, 12	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	opus_packet_get_samples_per_frame, .-opus_packet_get_samples_per_frame
	.global	__udivsi3
	.section	.text.opus_packet_parse_impl,"ax",@progbits
	.literal_position
	.literal .LC0, 2880
	.literal .LC1, 48000
	.literal .LC2, 5760
	.align	4
	.global	opus_packet_parse_impl
	.type	opus_packet_parse_impl, @function
# Function: opus_packet_parse_impl
# Module: upstream/src/opus.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return audiosize;
# C context: }
# C context:
# C context: int opus_packet_parse_impl(const unsigned char *data, opus_int32 len,
# C context: int self_delimited, unsigned char *out_toc,
# C context: const unsigned char *frames[48], opus_int16 size[48],
# C context: int *payload_offset, opus_int32 *packet_offset,
# C context: const unsigned char **padding, opus_int32 *padding_len)
opus_packet_parse_impl:
	addi	sp, sp, -80	#,,
	s32i	a13, sp, 68	#,
	s32i	a14, sp, 64	#,
	mov.n	a13, a7	# size, size
	s32i	a0, sp, 76	#,
	s32i	a12, sp, 72	#,
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\src\opus.c:199: {
	s32i.n	a4, sp, 12	# %sfp, self_delimited
	s32i.n	a5, sp, 0	# %sfp, out_toc
	s32i.n	a6, sp, 4	# %sfp, frames
	mov.n	a14, a2	# data, data
	mov.n	a7, a3	# len, len
# @OPUS@\upstream\src\opus.c:209:    if (size==NULL || len<0)
	beqz.n	a13, .L71	# size,
	bltz	a3, .L71	# len,
# @OPUS@\upstream\src\opus.c:211:    if (len==0)
	beqz.n	a3, .L13	# len,
# @OPUS@\upstream\src\opus.c:177:    if (data[0]&0x80)
	l8ui	a15, a2, 0	# *data_98(D), _189
# @OPUS@\upstream\src\opus.c:177:    if (data[0]&0x80)
	slli	a2, a15, 24	# tmp255, _189,
	bgez	a2, .L14	# tmp255,
# @OPUS@\upstream\src\opus.c:180:       audiosize = (Fs<<audiosize)/400;
	l32r	a4, .LC1	#, tmp260
# @OPUS@\upstream\src\opus.c:179:       audiosize = ((data[0]>>3)&0x3);
	extui	a2, a15, 3, 2	# audiosize, _189,,
# @OPUS@\upstream\src\opus.c:180:       audiosize = (Fs<<audiosize)/400;
	movi	a3, 0x190	#,
	ssl	a2	# audiosize
	sll	a2, a4	#, tmp260
	s32i.n	a7, sp, 20	#,
	call0	__divsi3		#
	l32i.n	a7, sp, 20	#,
	j	.L15		#
.L14:
# @OPUS@\upstream\src\opus.c:181:    } else if ((data[0]&0x60) == 0x60)
	movi	a2, 0x60	# tmp267,
	and	a2, a15, a2	# tmp270, _189, tmp267
	movi	a3, 0x60	# tmp271,
	bne	a2, a3, .L16	# tmp270, tmp271,
# @OPUS@\upstream\src\opus.c:183:       audiosize = (data[0]&0x08) ? Fs/50 : Fs/100;
	extui	a2, a15, 3, 1	# tmp275, _189,,
	movi	a4, 0x3c0	# tmp457,
	movi	a3, 0x1e0	# tmp458,
	movnez	a3, a4, a2	# tmp458, tmp457, tmp275
	mov.n	a2, a3	# audiosize, tmp458
	j	.L15		#
.L16:
	extui	a4, a15, 3, 2	# _201, _189,,
# @OPUS@\upstream\src\opus.c:187:          audiosize = Fs*60/1000;
	l32r	a2, .LC0	#, audiosize
# @OPUS@\upstream\src\opus.c:186:       if (audiosize == 3)
	beqi	a4, 3, .L15	# _201,,
# @OPUS@\upstream\src\opus.c:189:          audiosize = (Fs<<audiosize)/100;
	l32r	a2, .LC1	#, tmp279
	movi	a3, 0x64	#,
	ssl	a4	# _201
	sll	a2, a2	#, tmp279
	s32i.n	a7, sp, 20	#,
	call0	__divsi3		#
	l32i.n	a7, sp, 20	#,
.L15:
	extui	a4, a15, 0, 2	# _97, _189,
# @OPUS@\upstream\src\opus.c:217:    toc = *data++;
	addi.n	a12, a14, 1	# data, data,
# @OPUS@\upstream\src\opus.c:218:    len--;
	addi.n	a3, a7, -1	# len, len,
# @OPUS@\upstream\src\opus.c:220:    switch (toc&0x3)
	beqi	a4, 1, .L17	# _97,,
	beqz.n	a4, .L74	# tmp287,
	beqi	a4, 2, .L19	# _97,,
	j	.L132		#
.L17:
# @OPUS@\upstream\src\opus.c:230:       if (!self_delimited)
	l32i.n	a7, sp, 12	# %sfp,
	bnez.n	a7, .L75	#,
# @OPUS@\upstream\src\opus.c:232:          if (len&0x1)
	extui	a11, a3, 0, 1	# pad, len,
# @OPUS@\upstream\src\opus.c:232:          if (len&0x1)
	bnez.n	a11, .L13	# pad,
# @OPUS@\upstream\src\opus.c:234:          last_size = len/2;
	srai	a2, a3, 1	# last_size, len,
# @OPUS@\upstream\src\opus.c:236:          size[0] = (opus_int16)last_size;
	s16i	a2, a13, 0	# *size_100(D), last_size
# @OPUS@\upstream\src\opus.c:228:       count=2;
	movi.n	a4, 2	# <retval>,
	j	.L22		#
.L19:
# @OPUS@\upstream\src\opus.c:155:    if (len<1)
	bnez.n	a3, .L23	# len,
.L26:
# @OPUS@\upstream\src\opus.c:157:       *size = -1;
	movi.n	a2, -1	# tmp289,
	s16i	a2, a13, 0	# *size_100(D), tmp289
	j	.L13		#
.L23:
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	l8ui	a2, a14, 1	# MEM[(const unsigned char *)data_98(D) + 1B], _103
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	movi	a5, 0xfb	# tmp291,
	bltu	a5, a2, .L24	# tmp291, _103,
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	movi.n	a4, 1	# prephitmp_355,
	s16i	a2, a13, 0	# *size_100(D), _156
# @OPUS@\upstream\src\opus.c:162:       return 1;
	mov.n	a5, a4	# _255, prephitmp_355
	j	.L25		#
.L24:
# @OPUS@\upstream\src\opus.c:163:    } else if (len<2)
	beqi	a3, 1, .L26	# len,,
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	l8ui	a5, a14, 2	# MEM[(const unsigned char *)data_98(D) + 2B], MEM[(const unsigned char *)data_98(D) + 2B]
	slli	a5, a5, 2	# tmp295, MEM[(const unsigned char *)data_98(D) + 2B],
	add.n	a2, a5, a2	# _156, tmp295, _103
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	s16i	a2, a13, 0	# *size_100(D), _156
# @OPUS@\upstream\src\opus.c:169:       return 2;
	mov.n	a5, a4	# _255, prephitmp_355
	j	.L25		#
.L138:
# @OPUS@\upstream\src\opus.c:206:    opus_int32 pad = 0;
	movi.n	a11, 0	# pad,
# @OPUS@\upstream\src\opus.c:246:       data += bytes;
	add.n	a12, a12, a4	# data, data, prephitmp_355
# @OPUS@\upstream\src\opus.c:247:       last_size = len-size[0];
	sub	a2, a3, a2	# last_size, len, _156
# @OPUS@\upstream\src\opus.c:216:    cbr = 0;
	s32i.n	a11, sp, 8	# %sfp, pad
# @OPUS@\upstream\src\opus.c:241:       count = 2;
	movi.n	a4, 2	# <retval>,
# @OPUS@\upstream\src\opus.c:248:       break;
	j	.L18		#
.L132:
# @OPUS@\upstream\src\opus.c:251:       if (len<1)
	beqz.n	a3, .L13	# len,
# @OPUS@\upstream\src\opus.c:254:       ch = *data++;
	l8ui	a4, a14, 1	# MEM[(const unsigned char *)data_98(D) + 1B],
	s32i.n	a4, sp, 8	# %sfp,
	extui	a5, a4, 0, 6	# _99,,
# @OPUS@\upstream\src\opus.c:255:       count = ch&0x3F;
	mov.n	a4, a5	# <retval>, _99
# @OPUS@\upstream\src\opus.c:256:       if (count <= 0 || framesize*(opus_int32)count > 5760)
	beqz.n	a5, .L13	# _99,
# @OPUS@\upstream\src\opus.c:256:       if (count <= 0 || framesize*(opus_int32)count > 5760)
	mull	a2, a5, a2	# tmp301, _99, audiosize
# @OPUS@\upstream\src\opus.c:256:       if (count <= 0 || framesize*(opus_int32)count > 5760)
	l32r	a6, .LC2	#, tmp302
	blt	a6, a2, .L13	# tmp302, tmp301,
# @OPUS@\upstream\src\opus.c:260:       if (ch&0x40)
	l32i.n	a6, sp, 8	# %sfp,
	movi.n	a2, 0x40	# tmp303,
	and	a2, a6, a2	# tmp306,, tmp303
# @OPUS@\upstream\src\opus.c:258:       len--;
	addi	a6, a7, -2	# len, len,
# @OPUS@\upstream\src\opus.c:260:       if (ch&0x40)
	beqz.n	a2, .L27	# tmp306,
# @OPUS@\upstream\src\opus.c:265:             if (len<=0)
	beqz.n	a6, .L13	# len,
# @OPUS@\upstream\src\opus.c:267:             p = *data++;
	l8ui	a6, a14, 2	# MEM[(const unsigned char *)data_98(D) + 2B], p
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	movi	a8, 0xff	# tmp307,
# @OPUS@\upstream\src\opus.c:267:             p = *data++;
	addi.n	a12, a14, 3	# data, data,
# @OPUS@\upstream\src\opus.c:268:             len--;
	addi	a2, a7, -3	# len, len,
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	mov.n	a11, a6	# pad, p
	bne	a6, a8, .L28	# p, tmp307,
	j	.L133		#
.L135:
# @OPUS@\upstream\src\opus.c:267:             p = *data++;
	l8ui	a6, a9, 0	# MEM[base: _449, offset: 0B], p
	addi.n	a12, a12, 1	# data, data,
# @OPUS@\upstream\src\opus.c:268:             len--;
	add.n	a2, a2, a11	# len, len, tmp492
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	beq	a6, a10, .L77	# p, tmp493,
	add.n	a11, a6, a7	# pad, p, pad
	j	.L28		#
.L27:
# @OPUS@\upstream\src\opus.c:254:       ch = *data++;
	addi.n	a12, a14, 2	# data, data,
# @OPUS@\upstream\src\opus.c:206:    opus_int32 pad = 0;
	mov.n	a11, a2	# pad, tmp306
.L67:
# @OPUS@\upstream\src\opus.c:277:       cbr = !(ch&0x80);
	l32i.n	a7, sp, 8	# %sfp,
	slli	a2, a7, 24	# tmp312,,
	srai	a2, a2, 24	# tmp311, tmp312,
	movi.n	a7, -1	# tmp314,
	xor	a7, a7, a2	# tmp313, tmp314, tmp311
	extui	a7, a7, 31, 1	#, tmp313,
	s32i.n	a7, sp, 8	# %sfp,
# @OPUS@\upstream\src\opus.c:278:       if (!cbr)
	bgez	a2, .L31	# tmp311,
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	beqi	a5, 1, .L78	# _99,,
	addi	a2, a13, -2	# tmp317, size,
	slli	a5, a5, 1	# tmp319, _99,
	add.n	a5, a2, a5	# _430, tmp317, tmp319
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	s32i.n	a11, sp, 16	# %sfp, pad
	mov.n	a7, a13	# ivtmp$65, size
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	mov.n	a2, a6	# last_size, len
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	movi.n	a10, 2	# prephitmp_340,
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	mov.n	a11, a5	# _430, _430
.L36:
# @OPUS@\upstream\src\opus.c:155:    if (len<1)
	bnez.n	a6, .L32	# len,
	j	.L140		#
.L32:
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	l8ui	a8, a12, 0	# *data_311, _158
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	movi	a3, 0xfb	#,
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	mov.n	a9, a10	# prephitmp_340, prephitmp_340
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	bltu	a3, a8, .L33	#, _158,
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	movi.n	a9, 1	# prephitmp_340,
	s16i	a8, a7, 0	# MEM[base: _20, offset: 0B], _164
# @OPUS@\upstream\src\opus.c:162:       return 1;
	mov.n	a5, a9	# _215, prephitmp_340
	j	.L34		#
.L33:
# @OPUS@\upstream\src\opus.c:163:    } else if (len<2)
	bnei	a6, 1, .L35	# len,,
.L140:
# @OPUS@\upstream\src\opus.c:165:       *size = -1;
	movi.n	a2, -1	# tmp324,
	s16i	a2, a7, 0	# *_20, tmp324
	j	.L13		#
.L35:
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	l8ui	a3, a12, 1	# MEM[(const unsigned char *)data_311 + 1B], MEM[(const unsigned char *)data_311 + 1B]
# @OPUS@\upstream\src\opus.c:169:       return 2;
	mov.n	a5, a10	# _215, prephitmp_340
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	slli	a3, a3, 2	# tmp327, MEM[(const unsigned char *)data_311 + 1B],
	add.n	a8, a3, a8	# _164, tmp327, _158
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	s16i	a8, a7, 0	# MEM[base: _20, offset: 0B], _164
	j	.L34		#
.L137:
# @OPUS@\upstream\src\opus.c:288:             data += bytes;
	add.n	a12, a12, a9	# data, data, prephitmp_340
# @OPUS@\upstream\src\opus.c:289:             last_size -= bytes+size[i];
	sub	a2, a2, a5	# last_size, last_size, tmp332
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	bne	a7, a11, .L36	# ivtmp$65, _430,
	l32i.n	a11, sp, 16	# %sfp, pad
# @OPUS@\upstream\src\opus.c:291:          if (last_size<0)
	bltz	a2, .L13	# last_size,
# @OPUS@\upstream\src\opus.c:285:             len -= bytes;
	mov.n	a3, a6	# len, len
	j	.L18		#
.L31:
# @OPUS@\upstream\src\opus.c:293:       } else if (!self_delimited)
	l32i.n	a7, sp, 12	# %sfp,
	beqz.n	a7, .L37	#,
	slli	a5, a5, 1	# tmp333, _99,
	addi	a7, a5, -2	# prephitmp_283, tmp333,
	j	.L21		#
.L37:
# @OPUS@\upstream\src\opus.c:296:          last_size = len/count;
	mov.n	a3, a5	#, _99
	mov.n	a2, a6	#, len
	s32i.n	a4, sp, 32	#,
	s32i.n	a5, sp, 28	#,
	s32i.n	a6, sp, 24	#,
	s32i.n	a11, sp, 20	#,
	call0	__divsi3		#
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	l32i.n	a5, sp, 28	#,
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	l32i.n	a6, sp, 24	#,
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	mull	a3, a5, a2	# tmp341, _99, last_size
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	l32i.n	a4, sp, 32	#,
	l32i.n	a11, sp, 20	#,
	bne	a3, a6, .L13	# tmp341, len,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a9, a5, -1	# niters$35, _99,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	beqz.n	a9, .L22	# niters$35,
	slli	a10, a2, 16	# tmp342, last_size,
	addi	a5, a5, -2	# tmp345, _99,
	srai	a10, a10, 16	# _331, tmp342,
	extui	a3, a13, 1, 1	# prolog_loop_niters$37, size,,
	bltui	a5, 6, .L38	# tmp345,,
	beqz.n	a3, .L39	# prolog_loop_niters$37,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	movi.n	a7, 1	#,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a10, a13, 0	# *size_100(D), _331
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	s32i.n	a7, sp, 12	# %sfp,
.L39:
	sub	a8, a9, a3	# niters$38, niters$35, prolog_loop_niters$37
	extui	a7, a10, 0, 16	# _331, _331
	slli	a3, a3, 1	# tmp355, prolog_loop_niters$37,
	srli	a5, a8, 1	# bnd$39, niters$38,
	slli	a6, a7, 16	# tmp352, _331,
	add.n	a3, a13, a3	# ivtmp$68, size, tmp355
	slli	a5, a5, 2	# tmp357, bnd$39,
	or	a6, a7, a6	# tmp354, _331, tmp352
	add.n	a5, a5, a3	# _439, tmp357, ivtmp$68
.L40:
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s32i.n	a6, a3, 0	# MEM[base: _436, offset: 0B], tmp354
	addi.n	a3, a3, 4	# ivtmp$68, ivtmp$68,
	bne	a3, a5, .L40	# ivtmp$68, _439,
	l32i.n	a7, sp, 12	# %sfp,
	movi.n	a3, -2	# tmp358,
	and	a3, a8, a3	# niters_vector_mult_vf$40, niters$38, tmp358
	add.n	a7, a7, a3	#,, niters_vector_mult_vf$40
	s32i.n	a7, sp, 12	# %sfp,
	beq	a8, a3, .L22	# niters$38, niters_vector_mult_vf$40,
.L38:
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	l32i.n	a7, sp, 12	# %sfp,
	slli	a3, a7, 1	# _297,,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	add.n	a3, a13, a3	# tmp359, size, _297
	s16i	a10, a3, 0	# *_43, _331
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a5, a7, 1	# i,,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a5, a9, .L22	# i, niters$35,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a10, a3, 2	# *_41, _331
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a5, a7, 2	# i,,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a5, a9, .L22	# i, niters$35,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a10, a3, 4	# *_131, _331
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a5, a7, 3	# i,,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a5, a9, .L22	# i, niters$35,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a10, a3, 6	# *_204, _331
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a5, a7, 4	# i,,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a5, a9, .L22	# i, niters$35,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a10, a3, 8	# *_386, _331
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a5, a7, 5	# i,,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a5, a9, .L22	# i, niters$35,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a10, a3, 10	# *_34, _331
	j	.L22		#
.L74:
# @OPUS@\upstream\src\opus.c:206:    opus_int32 pad = 0;
	mov.n	a11, a4	# pad, tmp287
# @OPUS@\upstream\src\opus.c:216:    cbr = 0;
	s32i.n	a4, sp, 8	# %sfp, pad
# @OPUS@\upstream\src\opus.c:218:    len--;
	mov.n	a2, a3	# last_size, len
# @OPUS@\upstream\src\opus.c:224:       count=1;
	movi.n	a4, 1	# <retval>,
	j	.L18		#
.L78:
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	mov.n	a3, a6	# len, len
	mov.n	a2, a6	# last_size, len
.L18:
# @OPUS@\upstream\src\opus.c:305:    if (self_delimited)
	l32i.n	a7, sp, 12	# %sfp,
	beqz.n	a7, .L22	#,
	slli	a7, a4, 1	# tmp375, <retval>,
	mov.n	a6, a3	# len, len
	addi	a7, a7, -2	# prephitmp_283, tmp375,
	mov.n	a3, a2	# len, last_size
	j	.L21		#
.L75:
	movi.n	a7, 2	# prephitmp_283,
# @OPUS@\upstream\src\opus.c:229:       cbr = 1;
	s32i.n	a4, sp, 8	# %sfp, _97
# @OPUS@\upstream\src\opus.c:218:    len--;
	mov.n	a6, a3	# len, len
# @OPUS@\upstream\src\opus.c:206:    opus_int32 pad = 0;
	movi.n	a11, 0	# pad,
# @OPUS@\upstream\src\opus.c:228:       count=2;
	mov.n	a4, a7	# <retval>, prephitmp_283
.L21:
# @OPUS@\upstream\src\opus.c:307:       bytes = parse_size(data, len, size+count-1);
	add.n	a8, a13, a7	# _35, size, prephitmp_283
# @OPUS@\upstream\src\opus.c:155:    if (len<1)
	bnez.n	a6, .L42	# len,
	j	.L139		#
.L42:
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	l8ui	a5, a12, 0	# *data_312, _166
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	movi	a2, 0xfb	# tmp379,
	bltu	a2, a5, .L43	# tmp379, _166,
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	movi.n	a9, 1	# prephitmp_287,
	s16i	a5, a8, 0	# *_35, _172
# @OPUS@\upstream\src\opus.c:162:       return 1;
	mov.n	a10, a9	# _74, prephitmp_287
	j	.L44		#
.L43:
# @OPUS@\upstream\src\opus.c:163:    } else if (len<2)
	bnei	a6, 1, .L45	# len,,
.L139:
# @OPUS@\upstream\src\opus.c:165:       *size = -1;
	movi.n	a2, -1	# tmp381,
	s16i	a2, a8, 0	# *_35, tmp381
	j	.L13		#
.L45:
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	l8ui	a2, a12, 1	# MEM[(const unsigned char *)data_312 + 1B], MEM[(const unsigned char *)data_312 + 1B]
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	movi.n	a9, 2	# prephitmp_287,
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	ssl	a9	#
	sll	a2, a2	# tmp384, MEM[(const unsigned char *)data_312 + 1B]
	add.n	a5, a2, a5	# _172, tmp384, _166
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	s16i	a5, a8, 0	# *_35, _172
# @OPUS@\upstream\src\opus.c:169:       return 2;
	mov.n	a10, a9	# _74, prephitmp_287
	j	.L44		#
.L136:
# @OPUS@\upstream\src\opus.c:313:       if (cbr)
	l32i.n	a2, sp, 8	# %sfp,
# @OPUS@\upstream\src\opus.c:311:       data += bytes;
	add.n	a12, a12, a9	# data, data, prephitmp_287
# @OPUS@\upstream\src\opus.c:313:       if (cbr)
	beqz.n	a2, .L46	#,
# @OPUS@\upstream\src\opus.c:315:          if (size[count-1]*count > len)
	mull	a2, a5, a4	# tmp389, _172, <retval>
# @OPUS@\upstream\src\opus.c:315:          if (size[count-1]*count > len)
	blt	a6, a2, .L13	# len, tmp389,
# @OPUS@\upstream\src\opus.c:317:          for (i=0;i<count-1;i++)
	addi.n	a2, a4, -1	# _289, <retval>,
# @OPUS@\upstream\src\opus.c:317:          for (i=0;i<count-1;i++)
	beqz.n	a2, .L47	# _289,
# @OPUS@\upstream\src\opus.c:318:             size[i] = size[count-1];
	s16i	a5, a13, 0	# *size_100(D), _172
# @OPUS@\upstream\src\opus.c:317:          for (i=0;i<count-1;i++)
	beqi	a2, 1, .L47	# _289,,
	slli	a3, a4, 1	# tmp390, <retval>,
	addi	a3, a3, -2	# tmp392, tmp390,
	addi.n	a2, a13, 2	# vectp$25, size,
	movi.n	a5, 1	# tmp393,
	bge	a7, a3, .L50	# prephitmp_283, tmp392,
	movi.n	a5, 0	# tmp393,
.L50:
	addi.n	a7, a7, 2	# tmp395, prephitmp_283,
	movi.n	a6, 1	# tmp396,
	blti	a7, 3, .L51	# tmp395,,
	movi.n	a6, 0	# tmp396,
.L51:
	or	a3, a2, a8	# tmp399, vectp$25, _35
	extui	a3, a3, 0, 2	# tmp400, tmp399,
	or	a5, a5, a6	# tmp398, tmp393, tmp396
	movi.n	a7, 1	# tmp403,
	movi.n	a6, 0	# tmp404,
	moveqz	a6, a7, a3	# tmp404, tmp403, tmp400
	bnone	a6, a5, .L53	# tmp402, tmp398,
	addi	a3, a4, -3	# tmp409, <retval>,
	movi.n	a5, 0xb	# tmp412,
	bltu	a5, a3, .L48	# tmp412, tmp409,
	j	.L53		#
.L134:
	movi.n	a3, -2	# tmp414,
	and	a3, a6, a3	# niters_vector_mult_vf$28, niters$26, tmp414
	addi.n	a2, a3, 1	# tmp$29, niters_vector_mult_vf$28,
	beq	a3, a6, .L47	# niters_vector_mult_vf$28, niters$26,
	l16si	a3, a8, 0	# *_35, pretmp_173
# @OPUS@\upstream\src\opus.c:318:             size[i] = size[count-1];
	slli	a2, a2, 1	# tmp417, tmp$29,
	add.n	a2, a13, a2	# tmp418, size, tmp417
	s16i	a3, a2, 0	# *_132, pretmp_173
	j	.L47		#
.L53:
	addi	a5, a13, -2	# tmp419, size,
	slli	a3, a4, 1	# tmp420, <retval>,
	add.n	a5, a5, a3	# _415, tmp419, tmp420
.L55:
	l16si	a3, a8, 0	# *_35, pretmp_220
	s16i	a3, a2, 0	# MEM[base: _410, offset: 0B], pretmp_220
	addi.n	a2, a2, 2	# ivtmp$55, ivtmp$55,
# @OPUS@\upstream\src\opus.c:317:          for (i=0;i<count-1;i++)
	bne	a2, a5, .L55	# ivtmp$55, _415,
	j	.L47		#
.L48:
	l16ui	a7, a8, 0	# *_35, pretmp_44
	addi	a6, a4, -2	# niters$26, <retval>,
	srli	a3, a6, 1	# bnd$27, niters$26,
	slli	a5, a7, 16	# tmp431, pretmp_44,
	slli	a3, a3, 2	# tmp435, bnd$27,
	or	a5, a7, a5	# tmp433, pretmp_44, tmp431
	add.n	a3, a2, a3	# _422, ivtmp$62, tmp435
.L57:
# @OPUS@\upstream\src\opus.c:318:             size[i] = size[count-1];
	s32i.n	a5, a2, 0	# MEM[base: _419, offset: 0B], tmp433
	addi.n	a2, a2, 4	# ivtmp$62, ivtmp$62,
	bne	a2, a3, .L57	# ivtmp$62, _422,
	j	.L134		#
.L46:
# @OPUS@\upstream\src\opus.c:319:       } else if (bytes+size[count-1] > last_size)
	add.n	a5, a5, a10	# tmp436, _172, _74
# @OPUS@\upstream\src\opus.c:319:       } else if (bytes+size[count-1] > last_size)
	bge	a3, a5, .L47	# len, tmp436,
	j	.L13		#
.L22:
# @OPUS@\upstream\src\opus.c:326:       if (last_size > 1275)
	movi	a3, 0x4fb	# tmp437,
	blt	a3, a2, .L13	# tmp437, last_size,
# @OPUS@\upstream\src\opus.c:328:       size[count-1] = (opus_int16)last_size;
	slli	a3, a4, 1	# tmp438, <retval>,
# @OPUS@\upstream\src\opus.c:328:       size[count-1] = (opus_int16)last_size;
	addi	a3, a3, -2	# tmp440, tmp438,
	add.n	a3, a13, a3	# tmp441, size, tmp440
# @OPUS@\upstream\src\opus.c:328:       size[count-1] = (opus_int16)last_size;
	s16i	a2, a3, 0	# *_49, last_size
.L47:
# @OPUS@\upstream\src\opus.c:331:    if (payload_offset)
	l32i	a5, sp, 80	# payload_offset,
	beqz.n	a5, .L59	#,
# @OPUS@\upstream\src\opus.c:332:       *payload_offset = (int)(data-data0);
	sub	a2, a12, a14	# tmp442, data, data
# @OPUS@\upstream\src\opus.c:332:       *payload_offset = (int)(data-data0);
	s32i.n	a2, a5, 0	# *payload_offset_137(D), tmp442
.L59:
	l32i.n	a6, sp, 4	# %sfp,
	slli	a3, a4, 2	# tmp447, <retval>,
	add.n	a3, a6, a3	# _405, ivtmp$50, tmp447
	bnez.n	a6, .L63	#,
	slli	a3, a4, 1	# tmp443, <retval>,
	add.n	a3, a13, a3	# _393, ivtmp$46, tmp443
.L61:
# @OPUS@\upstream\src\opus.c:338:       data += size[i];
	l16si	a2, a13, 0	# MEM[base: _389, offset: 0B], tmp444
	addi.n	a13, a13, 2	# ivtmp$46, ivtmp$46,
# @OPUS@\upstream\src\opus.c:338:       data += size[i];
	add.n	a12, a12, a2	# data, data, tmp444
# @OPUS@\upstream\src\opus.c:334:    for (i=0;i<count;i++)
	bne	a13, a3, .L61	# ivtmp$46, _393,
	j	.L62		#
.L63:
# @OPUS@\upstream\src\opus.c:338:       data += size[i];
	l16si	a2, a13, 0	# MEM[base: _401, offset: 0B], tmp448
# @OPUS@\upstream\src\opus.c:337:          frames[i] = data;
	s32i.n	a12, a6, 0	# MEM[base: _400, offset: 0B], data
	addi.n	a6, a6, 4	# ivtmp$50, ivtmp$50,
# @OPUS@\upstream\src\opus.c:338:       data += size[i];
	add.n	a12, a12, a2	# data, data, tmp448
	addi.n	a13, a13, 2	# ivtmp$51, ivtmp$51,
# @OPUS@\upstream\src\opus.c:334:    for (i=0;i<count;i++)
	bne	a6, a3, .L63	# ivtmp$50, _405,
.L62:
# @OPUS@\upstream\src\opus.c:341:    if (padding != NULL)
	l32i	a7, sp, 88	# padding,
	beqz.n	a7, .L64	#,
# @OPUS@\upstream\src\opus.c:344:       *padding_len = pad;
	l32i	a2, sp, 92	# padding_len, padding_len
# @OPUS@\upstream\src\opus.c:343:       *padding = data;
	s32i.n	a12, a7, 0	# *padding_143(D), data
# @OPUS@\upstream\src\opus.c:344:       *padding_len = pad;
	s32i.n	a11, a2, 0	# *padding_len_145(D), pad
.L64:
# @OPUS@\upstream\src\opus.c:346:    if (packet_offset)
	l32i	a5, sp, 84	# packet_offset,
	beqz.n	a5, .L65	#,
# @OPUS@\upstream\src\opus.c:347:       *packet_offset = pad+(opus_int32)(data-data0);
	sub	a7, a12, a14	# tmp451, data, data
# @OPUS@\upstream\src\opus.c:347:       *packet_offset = pad+(opus_int32)(data-data0);
	add.n	a7, a7, a11	# tmp452, tmp451, pad
# @OPUS@\upstream\src\opus.c:347:       *packet_offset = pad+(opus_int32)(data-data0);
	s32i.n	a7, a5, 0	# *packet_offset_147(D), tmp452
.L65:
# @OPUS@\upstream\src\opus.c:349:    if (out_toc)
	l32i.n	a7, sp, 0	# %sfp,
	beqz.n	a7, .L11	#,
# @OPUS@\upstream\src\opus.c:350:       *out_toc = toc;
	s8i	a15, a7, 0	# *out_toc_149(D), _189
	j	.L11		#
.L71:
# @OPUS@\upstream\src\opus.c:210:       return OPUS_BAD_ARG;
	movi.n	a4, -1	# <retval>,
	j	.L11		#
.L133:
	mov.n	a9, a12	# ivtmp$77, data
# @OPUS@\upstream\src\opus.c:206:    opus_int32 pad = 0;
	movi.n	a7, 0	# pad,
# @OPUS@\upstream\src\opus.c:271:             pad += tmp;
	movi	a8, 0xfe	# tmp454,
# @OPUS@\upstream\src\opus.c:268:             len--;
	movi	a11, -0xff	# tmp492,
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	mov.n	a10, a6	# tmp493, p
	j	.L30		#
.L77:
	mov.n	a9, a12	# ivtmp$77, data
.L30:
	sub	a6, a2, a8	# _446, len, tmp454
# @OPUS@\upstream\src\opus.c:271:             pad += tmp;
	add.n	a7, a7, a8	# pad, pad, tmp454
# @OPUS@\upstream\src\opus.c:265:             if (len<=0)
	bgei	a6, 1, .L135	# _446,,
	j	.L13		#
.L28:
# @OPUS@\upstream\src\opus.c:270:             len -= tmp;
	sub	a6, a2, a6	# len, len, p
# @OPUS@\upstream\src\opus.c:274:       if (len<0)
	bgez	a6, .L67	# len,
.L13:
# @OPUS@\upstream\src\opus.c:310:          return OPUS_INVALID_PACKET;
	movi.n	a4, -4	# <retval>,
	j	.L11		#
.L44:
# @OPUS@\upstream\src\opus.c:308:       len -= bytes;
	sub	a6, a6, a10	# len, len, _74
# @OPUS@\upstream\src\opus.c:309:       if (size[count-1]<0 || size[count-1] > len)
	bge	a6, a5, .L136	# len, _172,
	j	.L13		#
.L34:
# @OPUS@\upstream\src\opus.c:285:             len -= bytes;
	sub	a6, a6, a5	# len, len, _215
	addi.n	a7, a7, 2	# ivtmp$65, ivtmp$65,
# @OPUS@\upstream\src\opus.c:289:             last_size -= bytes+size[i];
	add.n	a5, a8, a5	# tmp332, _164, _215
# @OPUS@\upstream\src\opus.c:286:             if (size[i]<0 || size[i] > len)
	bge	a6, a8, .L137	# len, _164,
	j	.L13		#
.L25:
# @OPUS@\upstream\src\opus.c:243:       len -= bytes;
	sub	a3, a3, a5	# len, len, _255
# @OPUS@\upstream\src\opus.c:244:       if (size[0]<0 || size[0] > len)
	bge	a3, a2, .L138	# len, _156,
	j	.L13		#
.L11:
# @OPUS@\upstream\src\opus.c:353: }
	l32i	a0, sp, 76	#,
	mov.n	a2, a4	#, <retval>
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	opus_packet_parse_impl, .-opus_packet_parse_impl
	.section	.text.opus_packet_parse,"ax",@progbits
	.literal_position
	.literal .LC5, 2880
	.literal .LC6, 48000
	.literal .LC7, 5760
	.align	4
	.global	opus_packet_parse
	.type	opus_packet_parse, @function
# Function: opus_packet_parse
# Module: upstream/src/opus.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return count;
# C context: }
# C context:
# C context: int opus_packet_parse(const unsigned char *data, opus_int32 len,
# C context: unsigned char *out_toc, const unsigned char *frames[48],
# C context: opus_int16 size[48], int *payload_offset)
# C context: {
# C context: return opus_packet_parse_impl(data, len, 0, out_toc,
opus_packet_parse:
	addi	sp, sp, -64	#,,
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
	mov.n	a13, a6	# size, size
	s32i.n	a0, sp, 60	#,
	s32i.n	a12, sp, 56	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\src\opus.c:358: {
	s32i.n	a4, sp, 0	# %sfp, out_toc
	s32i.n	a5, sp, 4	# %sfp, frames
	mov.n	a14, a2	# data, data
	mov.n	a6, a3	# len, len
# @OPUS@\upstream\src\opus.c:209:    if (size==NULL || len<0)
	beqz.n	a13, .L176	# size,
	bltz	a3, .L176	# len,
# @OPUS@\upstream\src\opus.c:211:    if (len==0)
	beqz.n	a3, .L143	# len,
# @OPUS@\upstream\src\opus.c:177:    if (data[0]&0x80)
	l8ui	a15, a2, 0	# *data_2(D), _151
# @OPUS@\upstream\src\opus.c:177:    if (data[0]&0x80)
	slli	a2, a15, 24	# tmp179, _151,
	bgez	a2, .L144	# tmp179,
# @OPUS@\upstream\src\opus.c:180:       audiosize = (Fs<<audiosize)/400;
	l32r	a4, .LC6	#, tmp184
# @OPUS@\upstream\src\opus.c:179:       audiosize = ((data[0]>>3)&0x3);
	extui	a2, a15, 3, 2	# audiosize, _151,,
# @OPUS@\upstream\src\opus.c:180:       audiosize = (Fs<<audiosize)/400;
	movi	a3, 0x190	#,
	ssl	a2	# audiosize
	sll	a2, a4	#, tmp184
	s32i.n	a6, sp, 12	#,
	s32i.n	a7, sp, 24	#,
	call0	__divsi3		#
	l32i.n	a6, sp, 12	#,
	l32i.n	a7, sp, 24	#,
	j	.L145		#
.L144:
# @OPUS@\upstream\src\opus.c:181:    } else if ((data[0]&0x60) == 0x60)
	movi	a2, 0x60	# tmp191,
	and	a2, a15, a2	# tmp194, _151, tmp191
	movi	a3, 0x60	# tmp195,
	bne	a2, a3, .L146	# tmp194, tmp195,
# @OPUS@\upstream\src\opus.c:183:       audiosize = (data[0]&0x08) ? Fs/50 : Fs/100;
	extui	a2, a15, 3, 1	# tmp199, _151,,
	movi	a4, 0x3c0	# tmp307,
	movi	a3, 0x1e0	# tmp308,
	movnez	a3, a4, a2	# tmp308, tmp307, tmp199
	mov.n	a2, a3	# audiosize, tmp308
	j	.L145		#
.L146:
	extui	a4, a15, 3, 2	# _163, _151,,
# @OPUS@\upstream\src\opus.c:187:          audiosize = Fs*60/1000;
	l32r	a2, .LC5	#, audiosize
# @OPUS@\upstream\src\opus.c:186:       if (audiosize == 3)
	beqi	a4, 3, .L145	# _163,,
# @OPUS@\upstream\src\opus.c:189:          audiosize = (Fs<<audiosize)/100;
	l32r	a2, .LC6	#, tmp203
	movi	a3, 0x64	#,
	ssl	a4	# _163
	sll	a2, a2	#, tmp203
	s32i.n	a6, sp, 12	#,
	s32i.n	a7, sp, 24	#,
	call0	__divsi3		#
	l32i.n	a7, sp, 24	#,
	l32i.n	a6, sp, 12	#,
.L145:
	extui	a4, a15, 0, 2	# _17, _151,
# @OPUS@\upstream\src\opus.c:217:    toc = *data++;
	addi.n	a12, a14, 1	# data, data,
# @OPUS@\upstream\src\opus.c:218:    len--;
	addi.n	a3, a6, -1	# last_size, len,
# @OPUS@\upstream\src\opus.c:220:    switch (toc&0x3)
	beqi	a4, 1, .L147	# _17,,
	beqz.n	a4, .L179	# _17,
	beqi	a4, 2, .L149	# _17,,
	j	.L215		#
.L147:
# @OPUS@\upstream\src\opus.c:232:          if (len&0x1)
	bbsi	a3, 0, .L143	# last_size,,
# @OPUS@\upstream\src\opus.c:234:          last_size = len/2;
	srai	a3, a3, 1	# last_size, last_size,
# @OPUS@\upstream\src\opus.c:236:          size[0] = (opus_int16)last_size;
	s16i	a3, a13, 0	# *size_6(D), last_size
# @OPUS@\upstream\src\opus.c:228:       count=2;
	movi.n	a4, 2	# <retval>,
	j	.L148		#
.L149:
# @OPUS@\upstream\src\opus.c:155:    if (len<1)
	bnez.n	a3, .L151	# last_size,
.L154:
# @OPUS@\upstream\src\opus.c:157:       *size = -1;
	movi.n	a2, -1	# tmp214,
	s16i	a2, a13, 0	# *size_6(D), tmp214
	j	.L143		#
.L151:
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	l8ui	a5, a14, 1	# MEM[(const unsigned char *)data_2(D) + 1B], _21
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	movi	a2, 0xfb	# tmp216,
	bltu	a2, a5, .L152	# tmp216, _21,
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	movi.n	a4, 1	# prephitmp_212,
	s16i	a5, a13, 0	# *size_6(D), _27
# @OPUS@\upstream\src\opus.c:162:       return 1;
	mov.n	a2, a4	# _199, prephitmp_212
	j	.L153		#
.L152:
# @OPUS@\upstream\src\opus.c:163:    } else if (len<2)
	beqi	a3, 1, .L154	# last_size,,
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	l8ui	a2, a14, 2	# MEM[(const unsigned char *)data_2(D) + 2B], MEM[(const unsigned char *)data_2(D) + 2B]
	slli	a2, a2, 2	# tmp220, MEM[(const unsigned char *)data_2(D) + 2B],
	add.n	a5, a2, a5	# _27, tmp220, _21
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	s16i	a5, a13, 0	# *size_6(D), _27
# @OPUS@\upstream\src\opus.c:169:       return 2;
	mov.n	a2, a4	# _199, prephitmp_212
	j	.L153		#
.L218:
# @OPUS@\upstream\src\opus.c:246:       data += bytes;
	add.n	a12, a12, a4	# data, data, prephitmp_212
# @OPUS@\upstream\src\opus.c:247:       last_size = len-size[0];
	sub	a3, a3, a5	# last_size, len, _27
# @OPUS@\upstream\src\opus.c:241:       count = 2;
	movi.n	a4, 2	# <retval>,
	j	.L148		#
.L215:
# @OPUS@\upstream\src\opus.c:251:       if (len<1)
	beqz.n	a3, .L143	# last_size,
# @OPUS@\upstream\src\opus.c:254:       ch = *data++;
	l8ui	a9, a14, 1	# MEM[(const unsigned char *)data_2(D) + 1B], ch
	extui	a8, a9, 0, 6	# _37, ch,
# @OPUS@\upstream\src\opus.c:255:       count = ch&0x3F;
	mov.n	a4, a8	# <retval>, _37
# @OPUS@\upstream\src\opus.c:256:       if (count <= 0 || framesize*(opus_int32)count > 5760)
	beqz.n	a8, .L143	# _37,
# @OPUS@\upstream\src\opus.c:256:       if (count <= 0 || framesize*(opus_int32)count > 5760)
	mull	a2, a8, a2	# tmp226, _37, audiosize
# @OPUS@\upstream\src\opus.c:256:       if (count <= 0 || framesize*(opus_int32)count > 5760)
	l32r	a3, .LC7	#, tmp227
	blt	a3, a2, .L143	# tmp227, tmp226,
# @OPUS@\upstream\src\opus.c:258:       len--;
	addi	a5, a6, -2	# len, len,
# @OPUS@\upstream\src\opus.c:260:       if (ch&0x40)
	bbci	a9, 6, .L155	# ch,,
# @OPUS@\upstream\src\opus.c:265:             if (len<=0)
	beqz.n	a5, .L143	# len,
# @OPUS@\upstream\src\opus.c:267:             p = *data++;
	l8ui	a5, a14, 2	# MEM[(const unsigned char *)data_2(D) + 2B], p
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	movi	a2, 0xff	# tmp232,
# @OPUS@\upstream\src\opus.c:267:             p = *data++;
	addi.n	a12, a14, 3	# data, data,
# @OPUS@\upstream\src\opus.c:268:             len--;
	addi	a3, a6, -3	# len, len,
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	bne	a5, a2, .L156	# p, tmp232,
	j	.L216		#
.L217:
# @OPUS@\upstream\src\opus.c:267:             p = *data++;
	l8ui	a2, a12, 0	# MEM[base: _265, offset: 0B], p
# @OPUS@\upstream\src\opus.c:268:             len--;
	add.n	a3, a3, a11	# len, len, tmp320
	mov.n	a12, a5	# data, ivtmp$110
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	bne	a2, a10, .L219	# p, tmp321,
	j	.L158		#
.L155:
# @OPUS@\upstream\src\opus.c:254:       ch = *data++;
	addi.n	a12, a14, 2	# data, data,
.L173:
# @OPUS@\upstream\src\opus.c:278:       if (!cbr)
	slli	a9, a9, 24	# tmp236, ch,
	bgez	a9, .L159	# tmp236,
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	beqi	a8, 1, .L180	# _37,,
	addi	a2, a13, -2	# tmp237, size,
	slli	a8, a8, 1	# tmp239, _37,
	add.n	a2, a2, a8	# _246, tmp237, tmp239
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	s32i.n	a15, sp, 8	# %sfp, _151
	mov.n	a9, a13	# ivtmp$98, size
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	mov.n	a3, a5	# last_size, len
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	movi.n	a11, 2	# prephitmp_92,
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	mov.n	a15, a2	# _246, _246
.L164:
# @OPUS@\upstream\src\opus.c:155:    if (len<1)
	bnez.n	a5, .L160	# len,
	j	.L220		#
.L160:
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	l8ui	a8, a12, 0	# *data_179, _62
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	movi	a2, 0xfb	#,
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	mov.n	a10, a11	# prephitmp_92, prephitmp_92
# @OPUS@\upstream\src\opus.c:159:    } else if (data[0]<252)
	bltu	a2, a8, .L161	#, _62,
# @OPUS@\upstream\src\opus.c:161:       *size = data[0];
	movi.n	a10, 1	# prephitmp_92,
	s16i	a8, a9, 0	# MEM[base: _59, offset: 0B], _68
# @OPUS@\upstream\src\opus.c:162:       return 1;
	mov.n	a6, a10	# _83, prephitmp_92
	j	.L162		#
.L161:
# @OPUS@\upstream\src\opus.c:163:    } else if (len<2)
	bnei	a5, 1, .L163	# len,,
.L220:
# @OPUS@\upstream\src\opus.c:165:       *size = -1;
	movi.n	a2, -1	# tmp244,
	s16i	a2, a9, 0	# *_59, tmp244
	j	.L143		#
.L163:
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	l8ui	a2, a12, 1	# MEM[(const unsigned char *)data_179 + 1B], MEM[(const unsigned char *)data_179 + 1B]
# @OPUS@\upstream\src\opus.c:169:       return 2;
	mov.n	a6, a11	# _83, prephitmp_92
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	slli	a2, a2, 2	# tmp247, MEM[(const unsigned char *)data_179 + 1B],
	add.n	a8, a2, a8	# _68, tmp247, _62
# @OPUS@\upstream\src\opus.c:168:       *size = 4*data[1] + data[0];
	s16i	a8, a9, 0	# MEM[base: _59, offset: 0B], _68
	j	.L162		#
.L174:
# @OPUS@\upstream\src\opus.c:288:             data += bytes;
	add.n	a12, a12, a10	# data, data, prephitmp_92
# @OPUS@\upstream\src\opus.c:289:             last_size -= bytes+size[i];
	sub	a3, a3, a6	# last_size, last_size, tmp252
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	bne	a9, a15, .L164	# ivtmp$98, _246,
	l32i.n	a15, sp, 8	# %sfp, _151
# @OPUS@\upstream\src\opus.c:291:          if (last_size<0)
	bgez	a3, .L148	# last_size,
	j	.L143		#
.L159:
# @OPUS@\upstream\src\opus.c:296:          last_size = len/count;
	mov.n	a3, a8	#, _37
	mov.n	a2, a5	#, len
	s32i.n	a4, sp, 20	#,
	s32i.n	a5, sp, 12	#,
	s32i.n	a7, sp, 24	#,
	s32i.n	a8, sp, 16	#,
	call0	__divsi3		#
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	l32i.n	a8, sp, 16	#,
# @OPUS@\upstream\src\opus.c:296:          last_size = len/count;
	mov.n	a3, a2	# last_size,
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	l32i.n	a5, sp, 12	#,
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	mull	a2, a8, a2	# tmp259, _37, last_size
# @OPUS@\upstream\src\opus.c:297:          if (last_size*count!=len)
	l32i.n	a4, sp, 20	#,
	l32i.n	a7, sp, 24	#,
	bne	a5, a2, .L143	# len, tmp259,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a10, a8, -1	# _50, _37,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	beqz.n	a10, .L148	# _50,
	slli	a6, a3, 16	# tmp260, last_size,
	addi	a5, a8, -2	# tmp263, _37,
	srai	a6, a6, 16	# _104, tmp260,
	extui	a2, a13, 1, 1	# prolog_loop_niters$85, size,,
	bltui	a5, 6, .L181	# tmp263,,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	movi.n	a5, 0	#,
	s32i.n	a5, sp, 8	# %sfp,
	beq	a2, a5, .L166	# prolog_loop_niters$85,,
	movi.n	a5, 1	#,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a6, a13, 0	# *size_6(D), _104
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	s32i.n	a5, sp, 8	# %sfp,
.L166:
	movi.n	a11, -1	# tmp265,
	xor	a11, a11, a2	# tmp264, tmp265, prolog_loop_niters$85
	add.n	a11, a11, a8	# niters$86, tmp264, _37
	extui	a9, a6, 0, 16	# _104, _104
	slli	a2, a2, 1	# tmp275, prolog_loop_niters$85,
	srli	a5, a11, 1	# bnd$87, niters$86,
	slli	a8, a9, 16	# tmp272, _104,
	add.n	a2, a13, a2	# ivtmp$103, size, tmp275
	slli	a5, a5, 2	# tmp277, bnd$87,
	or	a8, a9, a8	# tmp274, _104, tmp272
	add.n	a5, a5, a2	# _255, tmp277, ivtmp$103
.L167:
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s32i.n	a8, a2, 0	# MEM[base: _252, offset: 0B], tmp274
	addi.n	a2, a2, 4	# ivtmp$103, ivtmp$103,
	bne	a2, a5, .L167	# ivtmp$103, _255,
	movi.n	a2, -2	# tmp278,
	l32i.n	a8, sp, 8	# %sfp,
	and	a2, a11, a2	# niters_vector_mult_vf$88, niters$86, tmp278
	add.n	a5, a2, a8	# tmp$89, niters_vector_mult_vf$88,
	bne	a2, a11, .L165	# niters_vector_mult_vf$88, niters$86,
	j	.L148		#
.L181:
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	movi.n	a5, 0	# tmp$89,
.L165:
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	slli	a2, a5, 1	# _84, tmp$89,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	add.n	a2, a13, a2	# tmp279, size, _84
	s16i	a6, a2, 0	# *_85, _104
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a8, a5, 1	# i, tmp$89,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a8, a10, .L148	# i, _50,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a6, a2, 2	# *_189, _104
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a8, a5, 2	# i, tmp$89,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a8, a10, .L148	# i, _50,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a6, a2, 4	# *_101, _104
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a8, a5, 3	# i, tmp$89,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a8, a10, .L148	# i, _50,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a6, a2, 6	# *_56, _104
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a8, a5, 4	# i, tmp$89,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a8, a10, .L148	# i, _50,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a6, a2, 8	# *_165, _104
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	addi.n	a5, a5, 5	# i, tmp$89,
# @OPUS@\upstream\src\opus.c:299:          for (i=0;i<count-1;i++)
	bge	a5, a10, .L148	# i, _50,
# @OPUS@\upstream\src\opus.c:300:             size[i] = (opus_int16)last_size;
	s16i	a6, a2, 10	# *_105, _104
	j	.L148		#
.L179:
# @OPUS@\upstream\src\opus.c:224:       count=1;
	movi.n	a4, 1	# <retval>,
	j	.L148		#
.L180:
# @OPUS@\upstream\src\opus.c:282:          for (i=0;i<count-1;i++)
	mov.n	a3, a5	# last_size, len
.L148:
# @OPUS@\upstream\src\opus.c:326:       if (last_size > 1275)
	movi	a2, 0x4fb	# tmp295,
	blt	a2, a3, .L143	# tmp295, last_size,
# @OPUS@\upstream\src\opus.c:328:       size[count-1] = (opus_int16)last_size;
	slli	a2, a4, 1	# tmp296, <retval>,
# @OPUS@\upstream\src\opus.c:328:       size[count-1] = (opus_int16)last_size;
	addi	a2, a2, -2	# tmp298, tmp296,
	add.n	a2, a13, a2	# tmp299, size, tmp298
# @OPUS@\upstream\src\opus.c:328:       size[count-1] = (opus_int16)last_size;
	s16i	a3, a2, 0	# *_124, last_size
# @OPUS@\upstream\src\opus.c:331:    if (payload_offset)
	beqz.n	a7, .L169	# payload_offset,
# @OPUS@\upstream\src\opus.c:332:       *payload_offset = (int)(data-data0);
	sub	a14, a12, a14	# tmp300, data, data
# @OPUS@\upstream\src\opus.c:332:       *payload_offset = (int)(data-data0);
	s32i.n	a14, a7, 0	# *payload_offset_7(D), tmp300
.L169:
	l32i.n	a5, sp, 4	# %sfp,
	beqz.n	a5, .L170	#,
	slli	a2, a4, 2	# tmp301, <retval>,
	add.n	a2, a5, a2	# _238, ivtmp$94, tmp301
.L171:
# @OPUS@\upstream\src\opus.c:338:       data += size[i];
	l16si	a3, a13, 0	# MEM[base: _234, offset: 0B], tmp302
# @OPUS@\upstream\src\opus.c:337:          frames[i] = data;
	s32i.n	a12, a5, 0	# MEM[base: _233, offset: 0B], data
	addi.n	a5, a5, 4	# ivtmp$94, ivtmp$94,
# @OPUS@\upstream\src\opus.c:338:       data += size[i];
	add.n	a12, a12, a3	# data, data, tmp302
	addi.n	a13, a13, 2	# ivtmp$95, ivtmp$95,
# @OPUS@\upstream\src\opus.c:334:    for (i=0;i<count;i++)
	bne	a5, a2, .L171	# ivtmp$94, _238,
.L170:
# @OPUS@\upstream\src\opus.c:349:    if (out_toc)
	l32i.n	a8, sp, 0	# %sfp,
	beqz.n	a8, .L141	#,
# @OPUS@\upstream\src\opus.c:350:       *out_toc = toc;
	s8i	a15, a8, 0	# *out_toc_4(D), _151
	j	.L141		#
.L176:
# @OPUS@\upstream\src\opus.c:210:       return OPUS_BAD_ARG;
	movi.n	a4, -1	# <retval>,
# @OPUS@\upstream\src\opus.c:359:    return opus_packet_parse_impl(data, len, 0, out_toc,
	j	.L141		#
.L216:
	movi	a6, -0xfe	# tmp306,
# @OPUS@\upstream\src\opus.c:268:             len--;
	movi	a11, -0xff	# tmp320,
# @OPUS@\upstream\src\opus.c:269:             tmp = p==255 ? 254: p;
	mov.n	a10, a5	# tmp321, p
.L158:
	add.n	a2, a3, a6	# _262, len, tmp306
	addi.n	a5, a12, 1	# ivtmp$110, ivtmp$110,
# @OPUS@\upstream\src\opus.c:265:             if (len<=0)
	bgei	a2, 1, .L217	# _262,,
	j	.L143		#
.L219:
	mov.n	a5, a2	# p, p
.L156:
# @OPUS@\upstream\src\opus.c:270:             len -= tmp;
	sub	a5, a3, a5	# len, len, p
# @OPUS@\upstream\src\opus.c:274:       if (len<0)
	bgez	a5, .L173	# len,
	j	.L143		#
.L162:
# @OPUS@\upstream\src\opus.c:285:             len -= bytes;
	sub	a5, a5, a6	# len, len, _83
	addi.n	a9, a9, 2	# ivtmp$98, ivtmp$98,
# @OPUS@\upstream\src\opus.c:289:             last_size -= bytes+size[i];
	add.n	a6, a8, a6	# tmp252, _68, _83
# @OPUS@\upstream\src\opus.c:286:             if (size[i]<0 || size[i] > len)
	bge	a5, a8, .L174	# len, _68,
.L143:
# @OPUS@\upstream\src\opus.c:287:                return OPUS_INVALID_PACKET;
	movi.n	a4, -4	# <retval>,
	j	.L141		#
.L153:
# @OPUS@\upstream\src\opus.c:243:       len -= bytes;
	sub	a3, a3, a2	# len, last_size, _199
# @OPUS@\upstream\src\opus.c:244:       if (size[0]<0 || size[0] > len)
	bge	a3, a5, .L218	# len, _27,
	j	.L143		#
.L141:
# @OPUS@\upstream\src\opus.c:361: }
	l32i.n	a0, sp, 60	#,
	mov.n	a2, a4	#, <retval>
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	opus_packet_parse, .-opus_packet_parse
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
