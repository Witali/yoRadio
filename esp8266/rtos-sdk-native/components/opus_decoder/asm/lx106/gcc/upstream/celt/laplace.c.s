# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/laplace.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"laplace.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\laplace.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\laplace.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\laplace.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\laplace.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\laplace.c.s.raw
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
	.section	.text.ec_laplace_encode,"ax",@progbits
	.literal_position
	.literal .LC0, 32736
	.literal .LC1, 16384
	.literal .LC2, 32768
	.align	4
	.global	ec_laplace_encode
	.type	ec_laplace_encode, @function
# Function: ec_laplace_encode
# Module: upstream/celt/laplace.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return ft*(opus_int32)(16384-decay)>>15;
# C context: }
# C context:
# C context: void ec_laplace_encode(ec_enc *enc, int *value, unsigned fs, int decay)
# C context: {
# C context: unsigned fl;
# C context: int val = *value;
# C context: fl = 0;
ec_laplace_encode:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\laplace.c:54:    int val = *value;
	l32i.n	a9, a3, 0	# *value_30(D), val
# @OPUS@\upstream\celt\laplace.c:52: {
	mov.n	a8, a3	# value, value
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\celt\laplace.c:55:    fl = 0;
	movi.n	a3, 0	# fl,
# @OPUS@\upstream\celt\laplace.c:56:    if (val)
	beq	a9, a3, .L2	# val,,
# @OPUS@\upstream\celt\laplace.c:47:    ft = 32768 - LAPLACE_MINP*(2*LAPLACE_NMIN) - fs0;
	l32r	a6, .LC0	#, tmp91
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	l32r	a3, .LC1	#, tmp93
# @OPUS@\upstream\celt\laplace.c:47:    ft = 32768 - LAPLACE_MINP*(2*LAPLACE_NMIN) - fs0;
	sub	a6, a6, a4	# ft, tmp91, fs
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	sub	a3, a3, a5	# tmp92, tmp93, decay
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	mull	a6, a6, a3	# tmp94, ft, tmp92
# @OPUS@\upstream\celt\laplace.c:60:       s = -(val<0);
	extui	a11, a9, 31, 1	# _2, val,
# @OPUS@\upstream\celt\laplace.c:60:       s = -(val<0);
	neg	a10, a11	# s, _2
	sub	a3, a9, a11	# _32, val, _2
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	srli	a6, a6, 15	# fs, tmp94,
# @OPUS@\upstream\celt\laplace.c:61:       val = (val+s)^s;
	xor	a3, a3, a10	# val, _32, s
# @OPUS@\upstream\celt\laplace.c:65:       for (i=1; fs > 0 && i < val; i++)
	beqz.n	a6, .L11	# fs,
# @OPUS@\upstream\celt\laplace.c:65:       for (i=1; fs > 0 && i < val; i++)
	movi.n	a7, 1	# i,
# @OPUS@\upstream\celt\laplace.c:65:       for (i=1; fs > 0 && i < val; i++)
	blti	a3, 2, .L11	# val,,
.L5:
# @OPUS@\upstream\celt\laplace.c:67:          fs *= 2;
	slli	a6, a6, 1	# fs, fs,
# @OPUS@\upstream\celt\laplace.c:69:          fs = (fs*(opus_int32)decay)>>15;
	mull	a12, a6, a5	# _6, fs, decay
# @OPUS@\upstream\celt\laplace.c:68:          fl += fs+2*LAPLACE_MINP;
	addi.n	a9, a6, 2	# tmp103, fs,
# @OPUS@\upstream\celt\laplace.c:69:          fs = (fs*(opus_int32)decay)>>15;
	srli	a6, a12, 15	# fs, _6,
# @OPUS@\upstream\celt\laplace.c:65:       for (i=1; fs > 0 && i < val; i++)
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\celt\laplace.c:68:          fl += fs+2*LAPLACE_MINP;
	add.n	a4, a4, a9	# fs, fs, tmp103
# @OPUS@\upstream\celt\laplace.c:65:       for (i=1; fs > 0 && i < val; i++)
	beqz.n	a6, .L3	# fs,
# @OPUS@\upstream\celt\laplace.c:65:       for (i=1; fs > 0 && i < val; i++)
	blt	a7, a3, .L5	# i, val,
	j	.L3		#
.L11:
# @OPUS@\upstream\celt\laplace.c:65:       for (i=1; fs > 0 && i < val; i++)
	movi.n	a7, 1	# i,
.L3:
# @OPUS@\upstream\celt\laplace.c:72:       if (!fs)
	bnez.n	a6, .L8	# fs,
# @OPUS@\upstream\celt\laplace.c:76:          ndi_max = (32768-fl+LAPLACE_MINP-1)>>LAPLACE_LOG_MINP;
	l32r	a9, .LC2	#, tmp127
# @OPUS@\upstream\celt\laplace.c:78:          di = IMIN(val - i, ndi_max - 1);
	sub	a3, a3, a7	# tmp116, val, i
# @OPUS@\upstream\celt\laplace.c:76:          ndi_max = (32768-fl+LAPLACE_MINP-1)>>LAPLACE_LOG_MINP;
	sub	a5, a9, a4	# ndi_max, tmp127, fs
# @OPUS@\upstream\celt\laplace.c:77:          ndi_max = (ndi_max-s)>>1;
	add.n	a5, a5, a11	# _11, ndi_max, _2
# @OPUS@\upstream\celt\laplace.c:77:          ndi_max = (ndi_max-s)>>1;
	srai	a5, a5, 1	# ndi_max, _11,
# @OPUS@\upstream\celt\laplace.c:78:          di = IMIN(val - i, ndi_max - 1);
	addi.n	a6, a5, -1	# di, ndi_max,
	bge	a3, a6, .L9	# tmp116, di,
	mov.n	a6, a3	# di, tmp116
.L9:
# @OPUS@\upstream\celt\laplace.c:79:          fl += (2*di+1+s)*LAPLACE_MINP;
	slli	a3, a6, 1	# tmp117, di,
	addi.n	a4, a4, 1	# _39, fs,
# @OPUS@\upstream\celt\laplace.c:79:          fl += (2*di+1+s)*LAPLACE_MINP;
	sub	a3, a3, a11	# tmp118, tmp117, _2
	add.n	a3, a3, a4	# fl, tmp118, _39
# @OPUS@\upstream\celt\laplace.c:81:          *value = (i+di+s)^s;
	sub	a5, a7, a11	# tmp119, i, _2
	add.n	a5, a5, a6	# tmp120, tmp119, di
# @OPUS@\upstream\celt\laplace.c:80:          fs = IMIN(LAPLACE_MINP, 32768-fl);
	sub	a4, a9, a3	# fs, tmp127, fl
# @OPUS@\upstream\celt\laplace.c:80:          fs = IMIN(LAPLACE_MINP, 32768-fl);
	movi.n	a6, 1	# tmp124,
# @OPUS@\upstream\celt\laplace.c:81:          *value = (i+di+s)^s;
	xor	a5, a5, a10	# tmp121, tmp120, s
# @OPUS@\upstream\celt\laplace.c:80:          fs = IMIN(LAPLACE_MINP, 32768-fl);
	movnez	a4, a6, a4	# fs, tmp124, fs
# @OPUS@\upstream\celt\laplace.c:81:          *value = (i+di+s)^s;
	s32i.n	a5, a8, 0	# *value_30(D), tmp121
	add.n	a4, a4, a3	# fs, fs, fl
	j	.L2		#
.L8:
# @OPUS@\upstream\celt\laplace.c:85:          fs += LAPLACE_MINP;
	addi.n	a6, a6, 1	# fs, fs,
# @OPUS@\upstream\celt\laplace.c:86:          fl += fs&~s;
	addi.n	a3, a11, -1	# tmp125, _2,
# @OPUS@\upstream\celt\laplace.c:86:          fl += fs&~s;
	and	a3, a3, a6	# tmp126, tmp125, fs
# @OPUS@\upstream\celt\laplace.c:86:          fl += fs&~s;
	add.n	a3, a3, a4	# fl, tmp126, fs
	add.n	a4, a6, a3	# fs, fs, fl
.L2:
# @OPUS@\upstream\celt\laplace.c:91:    ec_encode_bin(enc, fl, fl+fs, 15);
	movi.n	a5, 0xf	#,
	call0	ec_encode_bin		#
# @OPUS@\upstream\celt\laplace.c:92: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_laplace_encode, .-ec_laplace_encode
	.section	.text.ec_laplace_decode,"ax",@progbits
	.literal_position
	.literal .LC3, 32736
	.literal .LC4, 16384
	.literal .LC5, 32768
	.align	4
	.global	ec_laplace_decode
	.type	ec_laplace_decode, @function
# Function: ec_laplace_decode
# Module: upstream/celt/laplace.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ec_encode_bin(enc, fl, fl+fs, 15);
# C context: }
# C context:
# C context: int ec_laplace_decode(ec_dec *dec, unsigned fs, int decay)
# C context: {
# C context: int val=0;
# C context: unsigned fl;
# C context: unsigned fm;
ec_laplace_decode:
	addi	sp, sp, -32	#,,
	s32i.n	a15, sp, 12	#,
	mov.n	a15, a3	# fs, fs
# @OPUS@\upstream\celt\laplace.c:99:    fm = ec_decode_bin(dec, 15);
	movi.n	a3, 0xf	#,
# @OPUS@\upstream\celt\laplace.c:95: {
	s32i.n	a12, sp, 24	#,
	s32i.n	a14, sp, 16	#,
	s32i.n	a0, sp, 28	#,
	s32i.n	a13, sp, 20	#,
# @OPUS@\upstream\celt\laplace.c:95: {
	mov.n	a12, a2	# dec, dec
	mov.n	a14, a4	# decay, decay
# @OPUS@\upstream\celt\laplace.c:99:    fm = ec_decode_bin(dec, 15);
	call0	ec_decode_bin		#
# @OPUS@\upstream\celt\laplace.c:101:    if (fm >= fs)
	bltu	a2, a15, .L33	# fm, fs,
# @OPUS@\upstream\celt\laplace.c:47:    ft = 32768 - LAPLACE_MINP*(2*LAPLACE_NMIN) - fs0;
	l32r	a5, .LC3	#, tmp68
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	l32r	a6, .LC4	#, tmp70
# @OPUS@\upstream\celt\laplace.c:47:    ft = 32768 - LAPLACE_MINP*(2*LAPLACE_NMIN) - fs0;
	sub	a5, a5, a15	# ft, tmp68, fs
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	sub	a6, a6, a14	# tmp69, tmp70, decay
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	mull	a5, a5, a6	# tmp71, ft, tmp69
# @OPUS@\upstream\celt\laplace.c:48:    return ft*(opus_int32)(16384-decay)>>15;
	srli	a5, a5, 15	# _42, tmp71,
# @OPUS@\upstream\celt\laplace.c:105:       fs = ec_laplace_get_freq1(fs, decay)+LAPLACE_MINP;
	addi.n	a6, a5, 1	# fs, _42,
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	beqi	a6, 1, .L34	# fs,,
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	slli	a5, a6, 1	# _5, fs,
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	add.n	a3, a15, a5	# fl, fs, _5
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	bltu	a2, a3, .L35	# fm, fl,
# @OPUS@\upstream\celt\laplace.c:103:       val++;
	movi.n	a13, 1	# <retval>,
	j	.L30		#
.L36:
	mov.n	a3, a4	# fl, _6
.L30:
# @OPUS@\upstream\celt\laplace.c:111:          fs = ((fs-2*LAPLACE_MINP)*(opus_int32)decay)>>15;
	addi	a5, a5, -2	# tmp72, _5,
# @OPUS@\upstream\celt\laplace.c:111:          fs = ((fs-2*LAPLACE_MINP)*(opus_int32)decay)>>15;
	mull	a5, a5, a14	# tmp73, tmp72, decay
# @OPUS@\upstream\celt\laplace.c:113:          val++;
	addi.n	a13, a13, 1	# <retval>, <retval>,
# @OPUS@\upstream\celt\laplace.c:111:          fs = ((fs-2*LAPLACE_MINP)*(opus_int32)decay)>>15;
	srli	a5, a5, 15	# fs, tmp73,
# @OPUS@\upstream\celt\laplace.c:112:          fs += LAPLACE_MINP;
	addi.n	a6, a5, 1	# fs, fs,
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	slli	a5, a6, 1	# _5, fs,
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	add.n	a4, a5, a3	# _6, _5, fl
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	beqi	a6, 1, .L28	# fs,,
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	bgeu	a2, a4, .L36	# fm, _6,
	j	.L29		#
.L35:
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	mov.n	a3, a15	# fl, fs
# @OPUS@\upstream\celt\laplace.c:103:       val++;
	movi.n	a13, 1	# <retval>,
.L29:
# @OPUS@\upstream\celt\laplace.c:123:       if (fm < fl+fs)
	add.n	a4, a3, a6	# _11, fl, fs
# @OPUS@\upstream\celt\laplace.c:123:       if (fm < fl+fs)
	bltu	a2, a4, .L31	# fm, _11,
	add.n	a15, a4, a6	# fs, _11, fs
	mov.n	a3, a4	# fl, _11
	j	.L27		#
.L31:
# @OPUS@\upstream\celt\laplace.c:124:          val = -val;
	neg	a13, a13	# <retval>, <retval>
	mov.n	a15, a4	# fs, _11
	j	.L27		#
.L33:
# @OPUS@\upstream\celt\laplace.c:100:    fl = 0;
	movi.n	a3, 0	# fl,
# @OPUS@\upstream\celt\laplace.c:96:    int val=0;
	mov.n	a13, a3	# <retval>, fl
.L27:
# @OPUS@\upstream\celt\laplace.c:132:    ec_dec_update(dec, fl, IMIN(fl+fs,32768), 32768);
	l32r	a5, .LC5	#, tmp74
	mov.n	a4, a15	# fs, fs
	bgeu	a5, a15, .L32	# tmp74, fs,
	mov.n	a4, a5	# fs, tmp74
	j	.L32		#
.L34:
# @OPUS@\upstream\celt\laplace.c:107:       while(fs > LAPLACE_MINP && fm >= fl+2*fs)
	mov.n	a3, a15	# fl, fs
# @OPUS@\upstream\celt\laplace.c:103:       val++;
	mov.n	a13, a6	# <retval>, fs
.L28:
# @OPUS@\upstream\celt\laplace.c:119:          di = (fm-fl)>>(LAPLACE_LOG_MINP+1);
	sub	a4, a2, a3	# tmp82, fm, fl
# @OPUS@\upstream\celt\laplace.c:119:          di = (fm-fl)>>(LAPLACE_LOG_MINP+1);
	srli	a4, a4, 1	# di, tmp82,
# @OPUS@\upstream\celt\laplace.c:121:          fl += 2*di*LAPLACE_MINP;
	slli	a5, a4, 1	# tmp83, di,
# @OPUS@\upstream\celt\laplace.c:120:          val += di;
	add.n	a13, a13, a4	# <retval>, <retval>, di
# @OPUS@\upstream\celt\laplace.c:121:          fl += 2*di*LAPLACE_MINP;
	add.n	a3, a3, a5	# fl, fl, tmp83
	movi.n	a6, 1	# fs,
	j	.L29		#
.L32:
# @OPUS@\upstream\celt\laplace.c:132:    ec_dec_update(dec, fl, IMIN(fl+fs,32768), 32768);
	mov.n	a2, a12	#, dec
	call0	ec_dec_update		#
# @OPUS@\upstream\celt\laplace.c:134: }
	l32i.n	a0, sp, 28	#,
	mov.n	a2, a13	#, <retval>
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	ec_laplace_decode, .-ec_laplace_decode
	.section	.text.ec_laplace_encode_p0,"ax",@progbits
	.literal_position
	.literal .LC6, -32768
	.align	4
	.global	ec_laplace_encode_p0
	.type	ec_laplace_encode_p0, @function
# Function: ec_laplace_encode_p0
# Module: upstream/celt/laplace.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return val;
# C context: }
# C context:
# C context: void ec_laplace_encode_p0(ec_enc *enc, int value, opus_uint16 p0, opus_uint16 decay)
# C context: {
# C context: int s;
# C context: opus_uint16 sign_icdf[3];
# C context: sign_icdf[0] = 32768-p0;
ec_laplace_encode_p0:
# @OPUS@\upstream\celt\laplace.c:140:    sign_icdf[0] = 32768-p0;
	l32r	a6, .LC6	#, tmp84
# @OPUS@\upstream\celt\laplace.c:137: {
	addi	sp, sp, -64	#,,
# @OPUS@\upstream\celt\laplace.c:140:    sign_icdf[0] = 32768-p0;
	sub	a4, a6, a4	# tmp83, tmp84, p0
	extui	a4, a4, 0, 16	# _3, tmp83
# @OPUS@\upstream\celt\laplace.c:137: {
	s32i.n	a12, sp, 56	#,
# @OPUS@\upstream\celt\laplace.c:141:    sign_icdf[1] = sign_icdf[0]/2;
	srli	a6, a4, 1	# tmp85, _3,
# @OPUS@\upstream\celt\laplace.c:137: {
	mov.n	a12, a3	# value, value
# @OPUS@\upstream\celt\laplace.c:142:    sign_icdf[2] = 0;
	movi.n	a3, 0	# tmp86,
# @OPUS@\upstream\celt\laplace.c:137: {
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a0, sp, 60	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\celt\laplace.c:140:    sign_icdf[0] = 32768-p0;
	s16i	a4, sp, 16	# sign_icdf, _3
# @OPUS@\upstream\celt\laplace.c:141:    sign_icdf[1] = sign_icdf[0]/2;
	s16i	a6, sp, 18	# sign_icdf, tmp85
# @OPUS@\upstream\celt\laplace.c:142:    sign_icdf[2] = 0;
	s16i	a3, sp, 20	# sign_icdf, tmp86
# @OPUS@\upstream\celt\laplace.c:137: {
	mov.n	a13, a2	# enc, enc
	extui	a14, a5, 0, 16	# decay, decay
# @OPUS@\upstream\celt\laplace.c:143:    s = value == 0 ? 0 : (value > 0 ? 1 : 2);
	beqz.n	a12, .L42	# value,
# @OPUS@\upstream\celt\laplace.c:143:    s = value == 0 ? 0 : (value > 0 ? 1 : 2);
	movi.n	a3, 1	# iftmp$3_47,
	bge	a12, a3, .L43	# value,,
	j	.L57		#
.L46:
# @OPUS@\upstream\celt\laplace.c:158:          ec_enc_icdf16(enc, IMIN(value, 7), icdf, 15);
	mov.n	a5, a14	#, tmp209
	mov.n	a4, sp	#,
	mov.n	a2, a13	#, enc
	mov.n	a3, a12	# value, value
	blti	a12, 8, .L45	# value,,
	mov.n	a3, a15	# value, value
.L45:
# @OPUS@\upstream\celt\laplace.c:159:          value -= 7;
	addi	a12, a12, -7	# value, value,
# @OPUS@\upstream\celt\laplace.c:158:          ec_enc_icdf16(enc, IMIN(value, 7), icdf, 15);
	call0	ec_enc_icdf16		#
# @OPUS@\upstream\celt\laplace.c:160:       } while (value >= 0);
	bgez	a12, .L46	# value,
	j	.L41		#
.L57:
# @OPUS@\upstream\celt\laplace.c:143:    s = value == 0 ? 0 : (value > 0 ? 1 : 2);
	movi.n	a3, 2	# iftmp$3_47,
.L43:
# @OPUS@\upstream\celt\laplace.c:144:    ec_enc_icdf16(enc, s, sign_icdf, 15);
	movi.n	a5, 0xf	#,
	addi	a4, sp, 16	#,,
	mov.n	a2, a13	#, enc
	call0	ec_enc_icdf16		#
# @OPUS@\upstream\celt\laplace.c:145:    value = abs(value);
	abs	a12, a12	# value, value
# @OPUS@\upstream\celt\laplace.c:150:       icdf[0] = IMAX(7, decay);
	mov.n	a3, a14	# decay, decay
	bgeui	a14, 7, .L47	# decay,,
	movi.n	a3, 7	# decay,
.L47:
	extui	a2, a3, 0, 16	# _5, decay
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	mull	a2, a2, a14	# tmp93, _5, decay
# @OPUS@\upstream\celt\laplace.c:150:       icdf[0] = IMAX(7, decay);
	s16i	a3, sp, 0	# icdf, decay
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a2, 15	# _44, tmp93,
	bgei	a2, 6, .L48	# _44,,
	movi.n	a2, 6	# _44,
.L48:
	mull	a3, a2, a14	# tmp96, _44, decay
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 2	# icdf, _44
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a3, 15	# _73, tmp96,
	bgei	a2, 5, .L49	# _73,,
	movi.n	a2, 5	# _73,
.L49:
	mull	a3, a14, a2	# tmp99, decay, _73
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 4	# icdf, _73
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a3, a3, 15	# _89, tmp99,
	bgei	a3, 4, .L50	# _89,,
	movi.n	a3, 4	# _89,
.L50:
	mull	a2, a14, a3	# tmp102, decay, _89
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a3, sp, 6	# icdf, _89
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a2, 15	# _105, tmp102,
	bgei	a2, 3, .L51	# _105,,
	movi.n	a2, 3	# _105,
.L51:
	mull	a3, a14, a2	# tmp105, decay, _105
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 8	# icdf, _105
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a3, 15	# _121, tmp105,
	bgei	a2, 2, .L52	# _121,,
	movi.n	a2, 2	# _121,
.L52:
	mull	a14, a14, a2	# tmp109, decay, _121
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 10	# icdf, _121
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a14, a14, 15	# tmp108, tmp109,
	bgei	a14, 1, .L53	# tmp108,,
	movi.n	a14, 1	# tmp108,
.L53:
# @OPUS@\upstream\celt\laplace.c:155:       icdf[7] = 0;
	movi.n	a2, 0	# tmp112,
# @OPUS@\upstream\celt\laplace.c:153:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a14, sp, 12	# icdf, tmp108
# @OPUS@\upstream\celt\laplace.c:155:       icdf[7] = 0;
	s16i	a2, sp, 14	# icdf, tmp112
# @OPUS@\upstream\celt\laplace.c:156:       value--;
	addi.n	a12, a12, -1	# value, value,
# @OPUS@\upstream\celt\laplace.c:158:          ec_enc_icdf16(enc, IMIN(value, 7), icdf, 15);
	movi.n	a15, 7	# value,
	movi.n	a14, 0xf	# tmp209,
	j	.L46		#
.L42:
# @OPUS@\upstream\celt\laplace.c:144:    ec_enc_icdf16(enc, s, sign_icdf, 15);
	movi.n	a5, 0xf	#,
	addi	a4, sp, 16	#,,
	mov.n	a3, a12	#, value
	call0	ec_enc_icdf16		#
.L41:
# @OPUS@\upstream\celt\laplace.c:162: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	ec_laplace_encode_p0, .-ec_laplace_encode_p0
	.section	.text.ec_laplace_decode_p0,"ax",@progbits
	.literal_position
	.literal .LC7, -32768
	.align	4
	.global	ec_laplace_decode_p0
	.type	ec_laplace_decode_p0, @function
# Function: ec_laplace_decode_p0
# Module: upstream/celt/laplace.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: int ec_laplace_decode_p0(ec_dec *dec, opus_uint16 p0, opus_uint16 decay)
# C context: {
# C context: int s;
# C context: int value;
# C context: opus_uint16 sign_icdf[3];
ec_laplace_decode_p0:
# @OPUS@\upstream\celt\laplace.c:169:    sign_icdf[0] = 32768-p0;
	l32r	a5, .LC7	#, tmp82
# @OPUS@\upstream\celt\laplace.c:165: {
	addi	sp, sp, -64	#,,
# @OPUS@\upstream\celt\laplace.c:169:    sign_icdf[0] = 32768-p0;
	sub	a5, a5, a3	# tmp81, tmp82, p0
	extui	a5, a5, 0, 16	# _3, tmp81
# @OPUS@\upstream\celt\laplace.c:170:    sign_icdf[1] = sign_icdf[0]/2;
	srli	a6, a5, 1	# tmp83, _3,
# @OPUS@\upstream\celt\laplace.c:165: {
	s32i.n	a13, sp, 52	#,
# @OPUS@\upstream\celt\laplace.c:169:    sign_icdf[0] = 32768-p0;
	s16i	a5, sp, 16	# sign_icdf, _3
# @OPUS@\upstream\celt\laplace.c:165: {
	extui	a13, a4, 0, 16	# decay, decay
# @OPUS@\upstream\celt\laplace.c:171:    sign_icdf[2] = 0;
	movi.n	a5, 0	# tmp84,
# @OPUS@\upstream\celt\laplace.c:172:    s = ec_dec_icdf16(dec, sign_icdf, 15);
	movi.n	a4, 0xf	#,
	addi	a3, sp, 16	#,,
# @OPUS@\upstream\celt\laplace.c:165: {
	s32i.n	a12, sp, 56	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a0, sp, 60	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\celt\laplace.c:165: {
	mov.n	a12, a2	# dec, dec
# @OPUS@\upstream\celt\laplace.c:170:    sign_icdf[1] = sign_icdf[0]/2;
	s16i	a6, sp, 18	# sign_icdf, tmp83
# @OPUS@\upstream\celt\laplace.c:171:    sign_icdf[2] = 0;
	s16i	a5, sp, 20	# sign_icdf, tmp84
# @OPUS@\upstream\celt\laplace.c:172:    s = ec_dec_icdf16(dec, sign_icdf, 15);
	call0	ec_dec_icdf16		#
	mov.n	a14, a2	# <retval>,
# @OPUS@\upstream\celt\laplace.c:173:    if (s==2) s = -1;
	beqi	a2, 2, .L69	# <retval>,,
# @OPUS@\upstream\celt\laplace.c:174:    if (s != 0)
	beqz.n	a2, .L58	# <retval>,
	j	.L59		#
.L69:
# @OPUS@\upstream\celt\laplace.c:173:    if (s==2) s = -1;
	movi.n	a14, -1	# <retval>,
.L59:
# @OPUS@\upstream\celt\laplace.c:179:       icdf[0] = IMAX(7, decay);
	mov.n	a3, a13	# decay, decay
	bgeui	a13, 7, .L61	# decay,,
	movi.n	a3, 7	# decay,
.L61:
	extui	a2, a3, 0, 16	# _6, decay
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	mull	a2, a13, a2	# tmp88, decay, _6
# @OPUS@\upstream\celt\laplace.c:179:       icdf[0] = IMAX(7, decay);
	s16i	a3, sp, 0	# icdf, decay
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a2, 15	# _10, tmp88,
	bgei	a2, 6, .L62	# _10,,
	movi.n	a2, 6	# _10,
.L62:
	mull	a3, a2, a13	# tmp91, _10, decay
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 2	# icdf, _10
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a3, 15	# _73, tmp91,
	bgei	a2, 5, .L63	# _73,,
	movi.n	a2, 5	# _73,
.L63:
	mull	a3, a13, a2	# tmp94, decay, _73
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 4	# icdf, _73
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a3, a3, 15	# _89, tmp94,
	bgei	a3, 4, .L64	# _89,,
	movi.n	a3, 4	# _89,
.L64:
	mull	a2, a13, a3	# tmp97, decay, _89
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a3, sp, 6	# icdf, _89
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a2, 15	# _105, tmp97,
	bgei	a2, 3, .L65	# _105,,
	movi.n	a2, 3	# _105,
.L65:
	mull	a3, a13, a2	# tmp100, decay, _105
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 8	# icdf, _105
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a2, a3, 15	# _121, tmp100,
	bgei	a2, 2, .L66	# _121,,
	movi.n	a2, 2	# _121,
.L66:
	mull	a13, a13, a2	# tmp104, decay, _121
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a2, sp, 10	# icdf, _121
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	srai	a13, a13, 15	# tmp103, tmp104,
	bgei	a13, 1, .L67	# tmp103,,
	movi.n	a13, 1	# tmp103,
.L67:
# @OPUS@\upstream\celt\laplace.c:184:       icdf[7] = 0;
	movi.n	a2, 0	# tmp107,
# @OPUS@\upstream\celt\laplace.c:182:          icdf[i] = IMAX(7-i, (icdf[i-1] * (opus_int32)decay) >> 15);
	s16i	a13, sp, 12	# icdf, tmp103
# @OPUS@\upstream\celt\laplace.c:184:       icdf[7] = 0;
	s16i	a2, sp, 14	# icdf, tmp107
# @OPUS@\upstream\celt\laplace.c:185:       value = 1;
	movi.n	a15, 1	# value,
# @OPUS@\upstream\celt\laplace.c:187:          v = ec_dec_icdf16(dec, icdf, 15);
	movi.n	a13, 0xf	# tmp133,
.L68:
# @OPUS@\upstream\celt\laplace.c:187:          v = ec_dec_icdf16(dec, icdf, 15);
	mov.n	a4, a13	#, tmp133
	mov.n	a3, sp	#,
	mov.n	a2, a12	#, dec
	call0	ec_dec_icdf16		#
# @OPUS@\upstream\celt\laplace.c:188:          value += v;
	add.n	a15, a15, a2	# value, value, v
# @OPUS@\upstream\celt\laplace.c:189:       } while (v == 7);
	beqi	a2, 7, .L68	# v,,
# @OPUS@\upstream\celt\laplace.c:190:       return s*value;
	mull	a14, a14, a15	# <retval>, <retval>, value
.L58:
# @OPUS@\upstream\celt\laplace.c:192: }
	l32i.n	a0, sp, 60	#,
	mov.n	a2, a14	#, <retval>
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	ec_laplace_decode_p0, .-ec_laplace_decode_p0
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
