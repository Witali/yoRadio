# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/control_SNR.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"control_SNR.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\control_SNR.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\control_SNR.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\control_SNR.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\control_SNR.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\control_SNR.c.s.raw
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
	.section	.text.silk_control_SNR,"ax",@progbits
	.literal_position
	.literal .LC0, silk_TargetRate_NB_21
	.literal .LC1, silk_TargetRate_MB_21
	.literal .LC2, silk_TargetRate_WB_21
	.align	4
	.global	silk_control_SNR
	.type	silk_control_SNR, @function
# Function: silk_control_SNR
# Module: upstream/silk/control_SNR.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: };
# C context:
# C context: /* Control SNR of redidual quantizer */
# C context: opus_int silk_control_SNR(
# C context: silk_encoder_state          *psEncC,                        /* I/O  Pointer to Silk encoder state               */
# C context: opus_int32                  TargetRate_bps                  /* I    Target max bitrate (bps)                    */
# C context: )
# C context: {
silk_control_SNR:
	addi	sp, sp, -16	#,,
	addmi	a5, a2, 0x1100	# tmp62, psEncC,
	s32i.n	a12, sp, 8	#,
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\silk\control_SNR.c:91:     psEncC->TargetRate_bps = TargetRate_bps;
	addmi	a12, a2, 0x1200	# tmp87, psEncC,
# @OPUS@\upstream\silk\control_SNR.c:86: {
	s32i.n	a13, sp, 4	#,
	s32i.n	a14, sp, 0	#,
# @OPUS@\upstream\silk\control_SNR.c:92:     if( psEncC->nb_subfr == 2 ) {
	l32i	a2, a5, 228	# psEncC_19(D)->nb_subfr, psEncC_19(D)->nb_subfr
# @OPUS@\upstream\silk\control_SNR.c:91:     psEncC->TargetRate_bps = TargetRate_bps;
	s32i.n	a3, a12, 0	# psEncC_19(D)->TargetRate_bps, TargetRate_bps
# @OPUS@\upstream\silk\control_SNR.c:86: {
	mov.n	a4, a3	# TargetRate_bps, TargetRate_bps
	l32i	a3, a5, 224	# psEncC_19(D)->fs_kHz, pretmp_28
# @OPUS@\upstream\silk\control_SNR.c:92:     if( psEncC->nb_subfr == 2 ) {
	bnei	a2, 2, .L2	# psEncC_19(D)->nb_subfr,,
# @OPUS@\upstream\silk\control_SNR.c:93:         TargetRate_bps -= 2000 + psEncC->fs_kHz/16;
	addi.n	a5, a3, 15	# tmp68, pretmp_28,
	movgez	a5, a3, a3	# pretmp_28, pretmp_28, pretmp_28
	movi	a2, -0x7d0	# tmp65,
	add.n	a4, a4, a2	# _17, TargetRate_bps, tmp65
	srai	a5, a5, 4	# tmp69, pretmp_28,
# @OPUS@\upstream\silk\control_SNR.c:93:         TargetRate_bps -= 2000 + psEncC->fs_kHz/16;
	sub	a4, a4, a5	# TargetRate_bps, _17, tmp69
.L2:
# @OPUS@\upstream\silk\control_SNR.c:95:     if( psEncC->fs_kHz == 8 ) {
	beqi	a3, 8, .L6	# pretmp_28,,
# @OPUS@\upstream\silk\control_SNR.c:98:     } else if( psEncC->fs_kHz == 12 ) {
	beqi	a3, 12, .L7	# pretmp_28,,
	movi	a14, 0xbe	# prephitmp_32,
# @OPUS@\upstream\silk\control_SNR.c:103:         snr_table = silk_TargetRate_WB_21;
	l32r	a13, .LC2	#, snr_table
	j	.L3		#
.L6:
	movi	a14, 0x6a	# prephitmp_32,
# @OPUS@\upstream\silk\control_SNR.c:97:         snr_table = silk_TargetRate_NB_21;
	l32r	a13, .LC0	#, snr_table
	j	.L3		#
.L7:
# @OPUS@\upstream\silk\control_SNR.c:100:         snr_table = silk_TargetRate_MB_21;
	l32r	a13, .LC1	#, snr_table
	movi	a14, 0x9a	# prephitmp_32,
.L3:
# @OPUS@\upstream\silk\control_SNR.c:105:     id = (TargetRate_bps+200)/400;
	movi	a2, 0xc8	# tmp70,
	movi	a3, 0x190	#,
	add.n	a2, a4, a2	#, TargetRate_bps, tmp70
	call0	__divsi3		#
# @OPUS@\upstream\silk\control_SNR.c:106:     id = silk_min(id - 10, bound-1);
	addi	a2, a2, -10	# id,,
# @OPUS@\upstream\silk\control_SNR.c:106:     id = silk_min(id - 10, bound-1);
	bge	a14, a2, .L4	# prephitmp_32, id,
	mov.n	a2, a14	# id, prephitmp_32
.L4:
# @OPUS@\upstream\silk\control_SNR.c:108:         psEncC->SNR_dB_Q7 = 0;
	movi.n	a3, 0	# _13,
# @OPUS@\upstream\silk\control_SNR.c:107:     if( id <= 0 ) {
	blti	a2, 1, .L5	# id,,
# @OPUS@\upstream\silk\control_SNR.c:110:         psEncC->SNR_dB_Q7 = snr_table[id]*21;
	add.n	a2, a13, a2	# tmp76, snr_table, id
# @OPUS@\upstream\silk\control_SNR.c:110:         psEncC->SNR_dB_Q7 = snr_table[id]*21;
	l8ui	a2, a2, 0	# *_10, *_10
	slli	a3, a2, 1	# tmp81, *_10,
	add.n	a2, a3, a2	# tmp82, tmp81, *_10
	slli	a3, a2, 3	# tmp83, tmp82,
	sub	a3, a3, a2	# _13, tmp83, tmp82
.L5:
# @OPUS@\upstream\silk\control_SNR.c:113: }
	l32i.n	a0, sp, 12	#,
	s32i	a3, a12, 108	# psEncC_19(D)->SNR_dB_Q7, _13
	movi.n	a2, 0	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	l32i.n	a14, sp, 0	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_control_SNR, .-silk_control_SNR
	.section	.rodata.silk_TargetRate_WB_21,"a"
	.align	4
	.type	silk_TargetRate_WB_21, @object
	.size	silk_TargetRate_WB_21, 191
silk_TargetRate_WB_21:
	.byte	0
	.byte	0
	.byte	0
	.byte	8
	.byte	29
	.byte	41
	.byte	49
	.byte	56
	.byte	62
	.byte	66
	.byte	70
	.byte	74
	.byte	77
	.byte	80
	.byte	83
	.byte	86
	.byte	88
	.byte	91
	.byte	93
	.byte	95
	.byte	97
	.byte	99
	.byte	101
	.byte	103
	.byte	105
	.byte	107
	.byte	108
	.byte	110
	.byte	112
	.byte	113
	.byte	115
	.byte	116
	.byte	118
	.byte	119
	.byte	121
	.byte	122
	.byte	123
	.byte	125
	.byte	126
	.byte	127
	.byte	-127
	.byte	-126
	.byte	-125
	.byte	-124
	.byte	-122
	.byte	-121
	.byte	-120
	.byte	-119
	.byte	-118
	.byte	-116
	.byte	-115
	.byte	-114
	.byte	-113
	.byte	-112
	.byte	-111
	.byte	-110
	.byte	-109
	.byte	-108
	.byte	-107
	.byte	-106
	.byte	-105
	.byte	-104
	.byte	-103
	.byte	-102
	.byte	-100
	.byte	-99
	.byte	-98
	.byte	-97
	.byte	-97
	.byte	-96
	.byte	-95
	.byte	-94
	.byte	-93
	.byte	-92
	.byte	-91
	.byte	-90
	.byte	-89
	.byte	-88
	.byte	-87
	.byte	-86
	.byte	-85
	.byte	-85
	.byte	-84
	.byte	-83
	.byte	-82
	.byte	-81
	.byte	-80
	.byte	-79
	.byte	-79
	.byte	-78
	.byte	-77
	.byte	-76
	.byte	-75
	.byte	-75
	.byte	-74
	.byte	-73
	.byte	-72
	.byte	-71
	.byte	-71
	.byte	-70
	.byte	-69
	.byte	-68
	.byte	-67
	.byte	-67
	.byte	-66
	.byte	-65
	.byte	-64
	.byte	-64
	.byte	-63
	.byte	-62
	.byte	-61
	.byte	-61
	.byte	-60
	.byte	-59
	.byte	-58
	.byte	-58
	.byte	-57
	.byte	-56
	.byte	-56
	.byte	-55
	.byte	-54
	.byte	-53
	.byte	-53
	.byte	-52
	.byte	-51
	.byte	-50
	.byte	-50
	.byte	-49
	.byte	-48
	.byte	-47
	.byte	-47
	.byte	-46
	.byte	-45
	.byte	-45
	.byte	-44
	.byte	-43
	.byte	-42
	.byte	-42
	.byte	-41
	.byte	-40
	.byte	-40
	.byte	-39
	.byte	-38
	.byte	-37
	.byte	-37
	.byte	-36
	.byte	-35
	.byte	-35
	.byte	-34
	.byte	-33
	.byte	-32
	.byte	-32
	.byte	-31
	.byte	-30
	.byte	-30
	.byte	-29
	.byte	-28
	.byte	-27
	.byte	-27
	.byte	-26
	.byte	-25
	.byte	-24
	.byte	-24
	.byte	-23
	.byte	-22
	.byte	-22
	.byte	-21
	.byte	-20
	.byte	-19
	.byte	-19
	.byte	-18
	.byte	-17
	.byte	-16
	.byte	-16
	.byte	-15
	.byte	-14
	.byte	-13
	.byte	-13
	.byte	-12
	.byte	-11
	.byte	-10
	.byte	-10
	.byte	-9
	.byte	-8
	.byte	-7
	.byte	-7
	.byte	-6
	.byte	-5
	.byte	-4
	.byte	-3
	.byte	-1
	.section	.rodata.silk_TargetRate_MB_21,"a"
	.align	4
	.type	silk_TargetRate_MB_21, @object
	.size	silk_TargetRate_MB_21, 155
silk_TargetRate_MB_21:
	.byte	0
	.byte	0
	.byte	28
	.byte	43
	.byte	52
	.byte	59
	.byte	65
	.byte	70
	.byte	74
	.byte	78
	.byte	81
	.byte	85
	.byte	87
	.byte	90
	.byte	93
	.byte	95
	.byte	98
	.byte	100
	.byte	102
	.byte	105
	.byte	107
	.byte	109
	.byte	111
	.byte	113
	.byte	115
	.byte	116
	.byte	118
	.byte	120
	.byte	122
	.byte	123
	.byte	125
	.byte	127
	.byte	-128
	.byte	-126
	.byte	-125
	.byte	-123
	.byte	-122
	.byte	-120
	.byte	-119
	.byte	-118
	.byte	-116
	.byte	-115
	.byte	-113
	.byte	-112
	.byte	-111
	.byte	-109
	.byte	-108
	.byte	-107
	.byte	-105
	.byte	-104
	.byte	-103
	.byte	-102
	.byte	-100
	.byte	-99
	.byte	-98
	.byte	-97
	.byte	-96
	.byte	-94
	.byte	-93
	.byte	-92
	.byte	-91
	.byte	-90
	.byte	-89
	.byte	-88
	.byte	-87
	.byte	-85
	.byte	-84
	.byte	-83
	.byte	-82
	.byte	-81
	.byte	-80
	.byte	-79
	.byte	-78
	.byte	-77
	.byte	-76
	.byte	-75
	.byte	-74
	.byte	-73
	.byte	-72
	.byte	-71
	.byte	-70
	.byte	-69
	.byte	-68
	.byte	-68
	.byte	-67
	.byte	-66
	.byte	-65
	.byte	-64
	.byte	-63
	.byte	-62
	.byte	-61
	.byte	-60
	.byte	-59
	.byte	-58
	.byte	-57
	.byte	-56
	.byte	-55
	.byte	-54
	.byte	-53
	.byte	-53
	.byte	-52
	.byte	-51
	.byte	-50
	.byte	-49
	.byte	-48
	.byte	-47
	.byte	-46
	.byte	-45
	.byte	-44
	.byte	-43
	.byte	-42
	.byte	-42
	.byte	-41
	.byte	-40
	.byte	-39
	.byte	-38
	.byte	-37
	.byte	-36
	.byte	-35
	.byte	-34
	.byte	-33
	.byte	-32
	.byte	-32
	.byte	-31
	.byte	-30
	.byte	-29
	.byte	-28
	.byte	-27
	.byte	-26
	.byte	-25
	.byte	-24
	.byte	-23
	.byte	-22
	.byte	-21
	.byte	-20
	.byte	-20
	.byte	-19
	.byte	-18
	.byte	-17
	.byte	-16
	.byte	-15
	.byte	-14
	.byte	-13
	.byte	-12
	.byte	-11
	.byte	-10
	.byte	-9
	.byte	-8
	.byte	-7
	.byte	-6
	.byte	-5
	.byte	-4
	.byte	-3
	.byte	-2
	.byte	-1
	.section	.rodata.silk_TargetRate_NB_21,"a"
	.align	4
	.type	silk_TargetRate_NB_21, @object
	.size	silk_TargetRate_NB_21, 107
silk_TargetRate_NB_21:
	.byte	0
	.byte	15
	.byte	39
	.byte	52
	.byte	61
	.byte	68
	.byte	74
	.byte	79
	.byte	84
	.byte	88
	.byte	92
	.byte	95
	.byte	99
	.byte	102
	.byte	105
	.byte	108
	.byte	111
	.byte	114
	.byte	117
	.byte	119
	.byte	122
	.byte	124
	.byte	126
	.byte	-127
	.byte	-125
	.byte	-123
	.byte	-121
	.byte	-119
	.byte	-117
	.byte	-114
	.byte	-113
	.byte	-111
	.byte	-109
	.byte	-107
	.byte	-105
	.byte	-103
	.byte	-101
	.byte	-99
	.byte	-98
	.byte	-96
	.byte	-94
	.byte	-93
	.byte	-91
	.byte	-89
	.byte	-88
	.byte	-86
	.byte	-85
	.byte	-83
	.byte	-82
	.byte	-80
	.byte	-79
	.byte	-77
	.byte	-76
	.byte	-74
	.byte	-73
	.byte	-71
	.byte	-70
	.byte	-69
	.byte	-67
	.byte	-66
	.byte	-64
	.byte	-63
	.byte	-62
	.byte	-60
	.byte	-59
	.byte	-57
	.byte	-56
	.byte	-55
	.byte	-53
	.byte	-52
	.byte	-51
	.byte	-49
	.byte	-48
	.byte	-47
	.byte	-45
	.byte	-44
	.byte	-43
	.byte	-41
	.byte	-40
	.byte	-39
	.byte	-37
	.byte	-36
	.byte	-35
	.byte	-33
	.byte	-32
	.byte	-31
	.byte	-29
	.byte	-28
	.byte	-26
	.byte	-25
	.byte	-24
	.byte	-22
	.byte	-21
	.byte	-20
	.byte	-18
	.byte	-17
	.byte	-15
	.byte	-14
	.byte	-13
	.byte	-11
	.byte	-10
	.byte	-8
	.byte	-7
	.byte	-6
	.byte	-4
	.byte	-3
	.byte	-1
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
