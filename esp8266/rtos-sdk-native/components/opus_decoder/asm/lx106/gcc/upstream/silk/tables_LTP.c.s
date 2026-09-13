# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/tables_LTP.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"tables_LTP.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\tables_LTP.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\tables_LTP.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\tables_LTP.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\tables_LTP.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\tables_LTP.c.s.raw
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
	.global	silk_LTP_vq_sizes
	.section	.rodata.silk_LTP_vq_sizes,"a"
	.align	4
	.type	silk_LTP_vq_sizes, @object
	.size	silk_LTP_vq_sizes, 3
silk_LTP_vq_sizes:
	.byte	8
	.byte	16
	.byte	32
	.global	silk_LTP_vq_gain_ptrs_Q7
	.section	.rodata.silk_LTP_vq_gain_ptrs_Q7,"a"
	.align	4
	.type	silk_LTP_vq_gain_ptrs_Q7, @object
	.size	silk_LTP_vq_gain_ptrs_Q7, 12
silk_LTP_vq_gain_ptrs_Q7:
	.word	silk_LTP_gain_vq_0_gain
	.word	silk_LTP_gain_vq_1_gain
	.word	silk_LTP_gain_vq_2_gain
	.section	.rodata.silk_LTP_gain_vq_2_gain,"a"
	.align	4
	.type	silk_LTP_gain_vq_2_gain, @object
	.size	silk_LTP_gain_vq_2_gain, 32
silk_LTP_gain_vq_2_gain:
	.byte	126
	.byte	124
	.byte	125
	.byte	124
	.byte	-127
	.byte	121
	.byte	126
	.byte	23
	.byte	-124
	.byte	127
	.byte	127
	.byte	127
	.byte	126
	.byte	127
	.byte	122
	.byte	-123
	.byte	-126
	.byte	-122
	.byte	101
	.byte	118
	.byte	119
	.byte	-111
	.byte	126
	.byte	86
	.byte	124
	.byte	120
	.byte	123
	.byte	119
	.byte	-86
	.byte	-83
	.byte	107
	.byte	109
	.section	.rodata.silk_LTP_gain_vq_1_gain,"a"
	.align	4
	.type	silk_LTP_gain_vq_1_gain, @object
	.size	silk_LTP_gain_vq_1_gain, 16
silk_LTP_gain_vq_1_gain:
	.byte	109
	.byte	120
	.byte	118
	.byte	12
	.byte	113
	.byte	115
	.byte	117
	.byte	119
	.byte	99
	.byte	59
	.byte	87
	.byte	111
	.byte	63
	.byte	111
	.byte	112
	.byte	80
	.section	.rodata.silk_LTP_gain_vq_0_gain,"a"
	.align	4
	.type	silk_LTP_gain_vq_0_gain, @object
	.size	silk_LTP_gain_vq_0_gain, 8
silk_LTP_gain_vq_0_gain:
	.byte	46
	.byte	2
	.byte	90
	.byte	87
	.byte	93
	.byte	91
	.byte	82
	.byte	98
	.global	silk_LTP_vq_ptrs_Q7
	.section	.rodata.silk_LTP_vq_ptrs_Q7,"a"
	.align	4
	.type	silk_LTP_vq_ptrs_Q7, @object
	.size	silk_LTP_vq_ptrs_Q7, 12
silk_LTP_vq_ptrs_Q7:
	.word	silk_LTP_gain_vq_0
	.word	silk_LTP_gain_vq_1
	.word	silk_LTP_gain_vq_2
	.section	.rodata.silk_LTP_gain_vq_2,"a"
	.align	4
	.type	silk_LTP_gain_vq_2, @object
	.size	silk_LTP_gain_vq_2, 160
silk_LTP_gain_vq_2:
	.byte	-6
	.byte	27
	.byte	61
	.byte	39
	.byte	5
	.byte	-11
	.byte	42
	.byte	88
	.byte	4
	.byte	1
	.byte	-2
	.byte	60
	.byte	65
	.byte	6
	.byte	-4
	.byte	-1
	.byte	-5
	.byte	73
	.byte	56
	.byte	1
	.byte	-9
	.byte	19
	.byte	94
	.byte	29
	.byte	-9
	.byte	0
	.byte	12
	.byte	99
	.byte	6
	.byte	4
	.byte	8
	.byte	-19
	.byte	102
	.byte	46
	.byte	-13
	.byte	3
	.byte	2
	.byte	13
	.byte	3
	.byte	2
	.byte	9
	.byte	-21
	.byte	84
	.byte	72
	.byte	-18
	.byte	-11
	.byte	46
	.byte	104
	.byte	-22
	.byte	8
	.byte	18
	.byte	38
	.byte	48
	.byte	23
	.byte	0
	.byte	-16
	.byte	70
	.byte	83
	.byte	-21
	.byte	11
	.byte	5
	.byte	-11
	.byte	117
	.byte	22
	.byte	-8
	.byte	-6
	.byte	23
	.byte	117
	.byte	-12
	.byte	3
	.byte	3
	.byte	-8
	.byte	95
	.byte	28
	.byte	4
	.byte	-10
	.byte	15
	.byte	77
	.byte	60
	.byte	-15
	.byte	-1
	.byte	4
	.byte	124
	.byte	2
	.byte	-4
	.byte	3
	.byte	38
	.byte	84
	.byte	24
	.byte	-25
	.byte	2
	.byte	13
	.byte	42
	.byte	13
	.byte	31
	.byte	21
	.byte	-4
	.byte	56
	.byte	46
	.byte	-1
	.byte	-1
	.byte	35
	.byte	79
	.byte	-13
	.byte	19
	.byte	-7
	.byte	65
	.byte	88
	.byte	-9
	.byte	-14
	.byte	20
	.byte	4
	.byte	81
	.byte	49
	.byte	-29
	.byte	20
	.byte	0
	.byte	75
	.byte	3
	.byte	-17
	.byte	5
	.byte	-9
	.byte	44
	.byte	92
	.byte	-8
	.byte	1
	.byte	-3
	.byte	22
	.byte	69
	.byte	31
	.byte	-6
	.byte	95
	.byte	41
	.byte	-12
	.byte	5
	.byte	39
	.byte	67
	.byte	16
	.byte	-4
	.byte	1
	.byte	0
	.byte	-6
	.byte	120
	.byte	55
	.byte	-36
	.byte	-13
	.byte	44
	.byte	122
	.byte	4
	.byte	-24
	.byte	81
	.byte	5
	.byte	11
	.byte	3
	.byte	7
	.byte	2
	.byte	0
	.byte	9
	.byte	10
	.byte	88
	.section	.rodata.silk_LTP_gain_vq_1,"a"
	.align	4
	.type	silk_LTP_gain_vq_1, @object
	.size	silk_LTP_gain_vq_1, 80
silk_LTP_gain_vq_1:
	.byte	13
	.byte	22
	.byte	39
	.byte	23
	.byte	12
	.byte	-1
	.byte	36
	.byte	64
	.byte	27
	.byte	-6
	.byte	-7
	.byte	10
	.byte	55
	.byte	43
	.byte	17
	.byte	1
	.byte	1
	.byte	8
	.byte	1
	.byte	1
	.byte	6
	.byte	-11
	.byte	74
	.byte	53
	.byte	-9
	.byte	-12
	.byte	55
	.byte	76
	.byte	-12
	.byte	8
	.byte	-3
	.byte	3
	.byte	93
	.byte	27
	.byte	-4
	.byte	26
	.byte	39
	.byte	59
	.byte	3
	.byte	-8
	.byte	2
	.byte	0
	.byte	77
	.byte	11
	.byte	9
	.byte	-8
	.byte	22
	.byte	44
	.byte	-6
	.byte	7
	.byte	40
	.byte	9
	.byte	26
	.byte	3
	.byte	9
	.byte	-7
	.byte	20
	.byte	101
	.byte	-7
	.byte	4
	.byte	3
	.byte	-8
	.byte	42
	.byte	26
	.byte	0
	.byte	-15
	.byte	33
	.byte	68
	.byte	2
	.byte	23
	.byte	-2
	.byte	55
	.byte	46
	.byte	-2
	.byte	15
	.byte	3
	.byte	-1
	.byte	21
	.byte	16
	.byte	41
	.section	.rodata.silk_LTP_gain_vq_0,"a"
	.align	4
	.type	silk_LTP_gain_vq_0, @object
	.size	silk_LTP_gain_vq_0, 40
silk_LTP_gain_vq_0:
	.byte	4
	.byte	6
	.byte	24
	.byte	7
	.byte	5
	.byte	0
	.byte	0
	.byte	2
	.byte	0
	.byte	0
	.byte	12
	.byte	28
	.byte	41
	.byte	13
	.byte	-4
	.byte	-9
	.byte	15
	.byte	42
	.byte	25
	.byte	14
	.byte	1
	.byte	-2
	.byte	62
	.byte	41
	.byte	-9
	.byte	-10
	.byte	37
	.byte	65
	.byte	-4
	.byte	3
	.byte	-6
	.byte	4
	.byte	66
	.byte	7
	.byte	-8
	.byte	16
	.byte	14
	.byte	38
	.byte	-3
	.byte	33
	.global	silk_LTP_gain_BITS_Q5_ptrs
	.section	.rodata.silk_LTP_gain_BITS_Q5_ptrs,"a"
	.align	4
	.type	silk_LTP_gain_BITS_Q5_ptrs, @object
	.size	silk_LTP_gain_BITS_Q5_ptrs, 12
silk_LTP_gain_BITS_Q5_ptrs:
	.word	silk_LTP_gain_BITS_Q5_0
	.word	silk_LTP_gain_BITS_Q5_1
	.word	silk_LTP_gain_BITS_Q5_2
	.global	silk_LTP_gain_iCDF_ptrs
	.section	.rodata.silk_LTP_gain_iCDF_ptrs,"a"
	.align	4
	.type	silk_LTP_gain_iCDF_ptrs, @object
	.size	silk_LTP_gain_iCDF_ptrs, 12
silk_LTP_gain_iCDF_ptrs:
	.word	silk_LTP_gain_iCDF_0
	.word	silk_LTP_gain_iCDF_1
	.word	silk_LTP_gain_iCDF_2
	.section	.rodata.silk_LTP_gain_BITS_Q5_2,"a"
	.align	4
	.type	silk_LTP_gain_BITS_Q5_2, @object
	.size	silk_LTP_gain_BITS_Q5_2, 32
silk_LTP_gain_BITS_Q5_2:
	.byte	-125
	.byte	-128
	.byte	-122
	.byte	-115
	.byte	-115
	.byte	-115
	.byte	-111
	.byte	-111
	.byte	-111
	.byte	-106
	.byte	-101
	.byte	-101
	.byte	-101
	.byte	-101
	.byte	-96
	.byte	-96
	.byte	-96
	.byte	-96
	.byte	-90
	.byte	-90
	.byte	-83
	.byte	-83
	.byte	-74
	.byte	-64
	.byte	-74
	.byte	-64
	.byte	-64
	.byte	-64
	.byte	-51
	.byte	-64
	.byte	-51
	.byte	-32
	.section	.rodata.silk_LTP_gain_BITS_Q5_1,"a"
	.align	4
	.type	silk_LTP_gain_BITS_Q5_1, @object
	.size	silk_LTP_gain_BITS_Q5_1, 16
silk_LTP_gain_BITS_Q5_1:
	.byte	69
	.byte	93
	.byte	115
	.byte	118
	.byte	-125
	.byte	-118
	.byte	-115
	.byte	-118
	.byte	-106
	.byte	-106
	.byte	-101
	.byte	-106
	.byte	-101
	.byte	-96
	.byte	-90
	.byte	-96
	.section	.rodata.silk_LTP_gain_BITS_Q5_0,"a"
	.align	4
	.type	silk_LTP_gain_BITS_Q5_0, @object
	.size	silk_LTP_gain_BITS_Q5_0, 8
silk_LTP_gain_BITS_Q5_0:
	.byte	15
	.byte	-125
	.byte	-118
	.byte	-118
	.byte	-101
	.byte	-101
	.byte	-83
	.byte	-83
	.section	.rodata.silk_LTP_gain_iCDF_2,"a"
	.align	4
	.type	silk_LTP_gain_iCDF_2, @object
	.size	silk_LTP_gain_iCDF_2, 32
silk_LTP_gain_iCDF_2:
	.byte	-15
	.byte	-31
	.byte	-45
	.byte	-57
	.byte	-69
	.byte	-81
	.byte	-92
	.byte	-103
	.byte	-114
	.byte	-124
	.byte	123
	.byte	114
	.byte	105
	.byte	96
	.byte	88
	.byte	80
	.byte	72
	.byte	64
	.byte	57
	.byte	50
	.byte	44
	.byte	38
	.byte	33
	.byte	29
	.byte	24
	.byte	20
	.byte	16
	.byte	12
	.byte	9
	.byte	5
	.byte	2
	.byte	0
	.section	.rodata.silk_LTP_gain_iCDF_1,"a"
	.align	4
	.type	silk_LTP_gain_iCDF_1, @object
	.size	silk_LTP_gain_iCDF_1, 16
silk_LTP_gain_iCDF_1:
	.byte	-57
	.byte	-91
	.byte	-112
	.byte	124
	.byte	109
	.byte	96
	.byte	84
	.byte	71
	.byte	61
	.byte	51
	.byte	42
	.byte	32
	.byte	23
	.byte	15
	.byte	8
	.byte	0
	.section	.rodata.silk_LTP_gain_iCDF_0,"a"
	.align	4
	.type	silk_LTP_gain_iCDF_0, @object
	.size	silk_LTP_gain_iCDF_0, 8
silk_LTP_gain_iCDF_0:
	.byte	71
	.byte	56
	.byte	43
	.byte	30
	.byte	21
	.byte	12
	.byte	6
	.byte	0
	.global	silk_LTP_per_index_iCDF
	.section	.rodata.silk_LTP_per_index_iCDF,"a"
	.align	4
	.type	silk_LTP_per_index_iCDF, @object
	.size	silk_LTP_per_index_iCDF, 3
silk_LTP_per_index_iCDF:
	.byte	-77
	.byte	99
	.byte	0
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
