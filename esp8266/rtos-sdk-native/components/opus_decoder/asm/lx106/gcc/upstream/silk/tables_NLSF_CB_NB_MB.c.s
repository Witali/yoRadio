# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/tables_NLSF_CB_NB_MB.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"tables_NLSF_CB_NB_MB.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\tables_NLSF_CB_NB_MB.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\tables_NLSF_CB_NB_MB.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\tables_NLSF_CB_NB_MB.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\tables_NLSF_CB_NB_MB.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\tables_NLSF_CB_NB_MB.c.s.raw
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
	.global	silk_NLSF_CB_NB_MB
	.section	.rodata.silk_NLSF_CB_NB_MB,"a"
	.align	4
	.type	silk_NLSF_CB_NB_MB, @object
	.size	silk_NLSF_CB_NB_MB, 40
silk_NLSF_CB_NB_MB:
# nVectors:
	.short	32
# order:
	.short	10
# quantStepSize_Q16:
	.short	11796
# invQuantStepSize_Q6:
	.short	356
# CB1_NLSF_Q8:
	.word	silk_NLSF_CB1_NB_MB_Q8
# CB1_Wght_Q9:
	.word	silk_NLSF_CB1_Wght_Q9
# CB1_iCDF:
	.word	silk_NLSF_CB1_iCDF_NB_MB
# pred_Q8:
	.word	silk_NLSF_PRED_NB_MB_Q8
# ec_sel:
	.word	silk_NLSF_CB2_SELECT_NB_MB
# ec_iCDF:
	.word	silk_NLSF_CB2_iCDF_NB_MB
# ec_Rates_Q5:
	.word	silk_NLSF_CB2_BITS_NB_MB_Q5
# deltaMin_Q15:
	.word	silk_NLSF_DELTA_MIN_NB_MB_Q15
	.section	.rodata.silk_NLSF_DELTA_MIN_NB_MB_Q15,"a"
	.align	4
	.type	silk_NLSF_DELTA_MIN_NB_MB_Q15, @object
	.size	silk_NLSF_DELTA_MIN_NB_MB_Q15, 22
silk_NLSF_DELTA_MIN_NB_MB_Q15:
	.short	250
	.short	3
	.short	6
	.short	3
	.short	3
	.short	3
	.short	4
	.short	3
	.short	3
	.short	3
	.short	461
	.section	.rodata.silk_NLSF_PRED_NB_MB_Q8,"a"
	.align	4
	.type	silk_NLSF_PRED_NB_MB_Q8, @object
	.size	silk_NLSF_PRED_NB_MB_Q8, 18
silk_NLSF_PRED_NB_MB_Q8:
	.byte	-77
	.byte	-118
	.byte	-116
	.byte	-108
	.byte	-105
	.byte	-107
	.byte	-103
	.byte	-105
	.byte	-93
	.byte	116
	.byte	67
	.byte	82
	.byte	59
	.byte	92
	.byte	72
	.byte	100
	.byte	89
	.byte	92
	.section	.rodata.silk_NLSF_CB2_BITS_NB_MB_Q5,"a"
	.align	4
	.type	silk_NLSF_CB2_BITS_NB_MB_Q5, @object
	.size	silk_NLSF_CB2_BITS_NB_MB_Q5, 72
silk_NLSF_CB2_BITS_NB_MB_Q5:
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-125
	.byte	6
	.byte	-111
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-20
	.byte	93
	.byte	15
	.byte	96
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-62
	.byte	83
	.byte	25
	.byte	71
	.byte	-35
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-94
	.byte	73
	.byte	34
	.byte	66
	.byte	-94
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-46
	.byte	126
	.byte	73
	.byte	43
	.byte	57
	.byte	-83
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-55
	.byte	125
	.byte	71
	.byte	48
	.byte	58
	.byte	-126
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-90
	.byte	110
	.byte	73
	.byte	57
	.byte	62
	.byte	104
	.byte	-46
	.byte	-1
	.byte	-1
	.byte	-5
	.byte	123
	.byte	65
	.byte	55
	.byte	68
	.byte	100
	.byte	-85
	.byte	-1
	.section	.rodata.silk_NLSF_CB2_iCDF_NB_MB,"a"
	.align	4
	.type	silk_NLSF_CB2_iCDF_NB_MB, @object
	.size	silk_NLSF_CB2_iCDF_NB_MB, 72
silk_NLSF_CB2_iCDF_NB_MB:
	.byte	-1
	.byte	-2
	.byte	-3
	.byte	-18
	.byte	14
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-4
	.byte	-38
	.byte	35
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-6
	.byte	-48
	.byte	59
	.byte	4
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-10
	.byte	-62
	.byte	71
	.byte	10
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-4
	.byte	-20
	.byte	-73
	.byte	82
	.byte	8
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-4
	.byte	-21
	.byte	-76
	.byte	90
	.byte	17
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-8
	.byte	-32
	.byte	-85
	.byte	97
	.byte	30
	.byte	4
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-20
	.byte	-83
	.byte	95
	.byte	37
	.byte	7
	.byte	1
	.byte	0
	.section	.rodata.silk_NLSF_CB2_SELECT_NB_MB,"a"
	.align	4
	.type	silk_NLSF_CB2_SELECT_NB_MB, @object
	.size	silk_NLSF_CB2_SELECT_NB_MB, 160
silk_NLSF_CB2_SELECT_NB_MB:
	.byte	16
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	99
	.byte	66
	.byte	36
	.byte	36
	.byte	34
	.byte	36
	.byte	34
	.byte	34
	.byte	34
	.byte	34
	.byte	83
	.byte	69
	.byte	36
	.byte	52
	.byte	34
	.byte	116
	.byte	102
	.byte	70
	.byte	68
	.byte	68
	.byte	-80
	.byte	102
	.byte	68
	.byte	68
	.byte	34
	.byte	65
	.byte	85
	.byte	68
	.byte	84
	.byte	36
	.byte	116
	.byte	-115
	.byte	-104
	.byte	-117
	.byte	-86
	.byte	-124
	.byte	-69
	.byte	-72
	.byte	-40
	.byte	-119
	.byte	-124
	.byte	-7
	.byte	-88
	.byte	-71
	.byte	-117
	.byte	104
	.byte	102
	.byte	100
	.byte	68
	.byte	68
	.byte	-78
	.byte	-38
	.byte	-71
	.byte	-71
	.byte	-86
	.byte	-12
	.byte	-40
	.byte	-69
	.byte	-69
	.byte	-86
	.byte	-12
	.byte	-69
	.byte	-69
	.byte	-37
	.byte	-118
	.byte	103
	.byte	-101
	.byte	-72
	.byte	-71
	.byte	-119
	.byte	116
	.byte	-73
	.byte	-101
	.byte	-104
	.byte	-120
	.byte	-124
	.byte	-39
	.byte	-72
	.byte	-72
	.byte	-86
	.byte	-92
	.byte	-39
	.byte	-85
	.byte	-101
	.byte	-117
	.byte	-12
	.byte	-87
	.byte	-72
	.byte	-71
	.byte	-86
	.byte	-92
	.byte	-40
	.byte	-33
	.byte	-38
	.byte	-118
	.byte	-42
	.byte	-113
	.byte	-68
	.byte	-38
	.byte	-88
	.byte	-12
	.byte	-115
	.byte	-120
	.byte	-101
	.byte	-86
	.byte	-88
	.byte	-118
	.byte	-36
	.byte	-37
	.byte	-117
	.byte	-92
	.byte	-37
	.byte	-54
	.byte	-40
	.byte	-119
	.byte	-88
	.byte	-70
	.byte	-10
	.byte	-71
	.byte	-117
	.byte	116
	.byte	-71
	.byte	-37
	.byte	-71
	.byte	-118
	.byte	100
	.byte	100
	.byte	-122
	.byte	100
	.byte	102
	.byte	34
	.byte	68
	.byte	68
	.byte	100
	.byte	68
	.byte	-88
	.byte	-53
	.byte	-35
	.byte	-38
	.byte	-88
	.byte	-89
	.byte	-102
	.byte	-120
	.byte	104
	.byte	70
	.byte	-92
	.byte	-10
	.byte	-85
	.byte	-119
	.byte	-117
	.byte	-119
	.byte	-101
	.byte	-38
	.byte	-37
	.byte	-117
	.section	.rodata.silk_NLSF_CB1_iCDF_NB_MB,"a"
	.align	4
	.type	silk_NLSF_CB1_iCDF_NB_MB, @object
	.size	silk_NLSF_CB1_iCDF_NB_MB, 64
silk_NLSF_CB1_iCDF_NB_MB:
	.byte	-44
	.byte	-78
	.byte	-108
	.byte	-127
	.byte	108
	.byte	96
	.byte	85
	.byte	82
	.byte	79
	.byte	77
	.byte	61
	.byte	59
	.byte	57
	.byte	56
	.byte	51
	.byte	49
	.byte	48
	.byte	45
	.byte	42
	.byte	41
	.byte	40
	.byte	38
	.byte	36
	.byte	34
	.byte	31
	.byte	30
	.byte	21
	.byte	12
	.byte	10
	.byte	3
	.byte	1
	.byte	0
	.byte	-1
	.byte	-11
	.byte	-12
	.byte	-20
	.byte	-23
	.byte	-31
	.byte	-39
	.byte	-53
	.byte	-66
	.byte	-80
	.byte	-81
	.byte	-95
	.byte	-107
	.byte	-120
	.byte	125
	.byte	114
	.byte	102
	.byte	91
	.byte	81
	.byte	71
	.byte	60
	.byte	52
	.byte	43
	.byte	35
	.byte	28
	.byte	20
	.byte	19
	.byte	18
	.byte	12
	.byte	11
	.byte	5
	.byte	0
	.section	.rodata.silk_NLSF_CB1_Wght_Q9,"a"
	.align	4
	.type	silk_NLSF_CB1_Wght_Q9, @object
	.size	silk_NLSF_CB1_Wght_Q9, 640
silk_NLSF_CB1_Wght_Q9:
	.short	2897
	.short	2314
	.short	2314
	.short	2314
	.short	2287
	.short	2287
	.short	2314
	.short	2300
	.short	2327
	.short	2287
	.short	2888
	.short	2580
	.short	2394
	.short	2367
	.short	2314
	.short	2274
	.short	2274
	.short	2274
	.short	2274
	.short	2194
	.short	2487
	.short	2340
	.short	2340
	.short	2314
	.short	2314
	.short	2314
	.short	2340
	.short	2340
	.short	2367
	.short	2354
	.short	3216
	.short	2766
	.short	2340
	.short	2340
	.short	2314
	.short	2274
	.short	2221
	.short	2207
	.short	2261
	.short	2194
	.short	2460
	.short	2474
	.short	2367
	.short	2394
	.short	2394
	.short	2394
	.short	2394
	.short	2367
	.short	2407
	.short	2314
	.short	3479
	.short	3056
	.short	2127
	.short	2207
	.short	2274
	.short	2274
	.short	2274
	.short	2287
	.short	2314
	.short	2261
	.short	3282
	.short	3141
	.short	2580
	.short	2394
	.short	2247
	.short	2221
	.short	2207
	.short	2194
	.short	2194
	.short	2114
	.short	4096
	.short	3845
	.short	2221
	.short	2620
	.short	2620
	.short	2407
	.short	2314
	.short	2394
	.short	2367
	.short	2074
	.short	3178
	.short	3244
	.short	2367
	.short	2221
	.short	2553
	.short	2434
	.short	2340
	.short	2314
	.short	2167
	.short	2221
	.short	3338
	.short	3488
	.short	2726
	.short	2194
	.short	2261
	.short	2460
	.short	2354
	.short	2367
	.short	2207
	.short	2101
	.short	2354
	.short	2420
	.short	2327
	.short	2367
	.short	2394
	.short	2420
	.short	2420
	.short	2420
	.short	2460
	.short	2367
	.short	3779
	.short	3629
	.short	2434
	.short	2527
	.short	2367
	.short	2274
	.short	2274
	.short	2300
	.short	2207
	.short	2048
	.short	3254
	.short	3225
	.short	2713
	.short	2846
	.short	2447
	.short	2327
	.short	2300
	.short	2300
	.short	2274
	.short	2127
	.short	3263
	.short	3300
	.short	2753
	.short	2806
	.short	2447
	.short	2261
	.short	2261
	.short	2247
	.short	2127
	.short	2101
	.short	2873
	.short	2981
	.short	2633
	.short	2367
	.short	2407
	.short	2354
	.short	2194
	.short	2247
	.short	2247
	.short	2114
	.short	3225
	.short	3197
	.short	2633
	.short	2580
	.short	2274
	.short	2181
	.short	2247
	.short	2221
	.short	2221
	.short	2141
	.short	3178
	.short	3310
	.short	2740
	.short	2407
	.short	2274
	.short	2274
	.short	2274
	.short	2287
	.short	2194
	.short	2114
	.short	3141
	.short	3272
	.short	2460
	.short	2061
	.short	2287
	.short	2500
	.short	2367
	.short	2487
	.short	2434
	.short	2181
	.short	3507
	.short	3282
	.short	2314
	.short	2700
	.short	2647
	.short	2474
	.short	2367
	.short	2394
	.short	2340
	.short	2127
	.short	3423
	.short	3535
	.short	3038
	.short	3056
	.short	2300
	.short	1950
	.short	2221
	.short	2274
	.short	2274
	.short	2274
	.short	3404
	.short	3366
	.short	2087
	.short	2687
	.short	2873
	.short	2354
	.short	2420
	.short	2274
	.short	2474
	.short	2540
	.short	3760
	.short	3488
	.short	1950
	.short	2660
	.short	2897
	.short	2527
	.short	2394
	.short	2367
	.short	2460
	.short	2261
	.short	3028
	.short	3272
	.short	2740
	.short	2888
	.short	2740
	.short	2154
	.short	2127
	.short	2287
	.short	2234
	.short	2247
	.short	3695
	.short	3657
	.short	2025
	.short	1969
	.short	2660
	.short	2700
	.short	2580
	.short	2500
	.short	2327
	.short	2367
	.short	3207
	.short	3413
	.short	2354
	.short	2074
	.short	2888
	.short	2888
	.short	2340
	.short	2487
	.short	2247
	.short	2167
	.short	3338
	.short	3366
	.short	2846
	.short	2780
	.short	2327
	.short	2154
	.short	2274
	.short	2287
	.short	2114
	.short	2061
	.short	2327
	.short	2300
	.short	2181
	.short	2167
	.short	2181
	.short	2367
	.short	2633
	.short	2700
	.short	2700
	.short	2553
	.short	2407
	.short	2434
	.short	2221
	.short	2261
	.short	2221
	.short	2221
	.short	2340
	.short	2420
	.short	2607
	.short	2700
	.short	3038
	.short	3244
	.short	2806
	.short	2888
	.short	2474
	.short	2074
	.short	2300
	.short	2314
	.short	2354
	.short	2380
	.short	2221
	.short	2154
	.short	2127
	.short	2287
	.short	2500
	.short	2793
	.short	2793
	.short	2620
	.short	2580
	.short	2367
	.short	3676
	.short	3713
	.short	2234
	.short	1838
	.short	2181
	.short	2753
	.short	2726
	.short	2673
	.short	2513
	.short	2207
	.short	2793
	.short	3160
	.short	2726
	.short	2553
	.short	2846
	.short	2513
	.short	2181
	.short	2394
	.short	2221
	.short	2181
	.section	.rodata.silk_NLSF_CB1_NB_MB_Q8,"a"
	.align	4
	.type	silk_NLSF_CB1_NB_MB_Q8, @object
	.size	silk_NLSF_CB1_NB_MB_Q8, 320
silk_NLSF_CB1_NB_MB_Q8:
	.byte	12
	.byte	35
	.byte	60
	.byte	83
	.byte	108
	.byte	-124
	.byte	-99
	.byte	-76
	.byte	-50
	.byte	-28
	.byte	15
	.byte	32
	.byte	55
	.byte	77
	.byte	101
	.byte	125
	.byte	-105
	.byte	-81
	.byte	-55
	.byte	-31
	.byte	19
	.byte	42
	.byte	66
	.byte	89
	.byte	114
	.byte	-119
	.byte	-94
	.byte	-72
	.byte	-47
	.byte	-26
	.byte	12
	.byte	25
	.byte	50
	.byte	72
	.byte	97
	.byte	120
	.byte	-109
	.byte	-84
	.byte	-56
	.byte	-33
	.byte	26
	.byte	44
	.byte	69
	.byte	90
	.byte	114
	.byte	-121
	.byte	-97
	.byte	-76
	.byte	-51
	.byte	-31
	.byte	13
	.byte	22
	.byte	53
	.byte	80
	.byte	106
	.byte	-126
	.byte	-100
	.byte	-76
	.byte	-51
	.byte	-28
	.byte	15
	.byte	25
	.byte	44
	.byte	64
	.byte	90
	.byte	115
	.byte	-114
	.byte	-88
	.byte	-60
	.byte	-34
	.byte	19
	.byte	24
	.byte	62
	.byte	82
	.byte	100
	.byte	120
	.byte	-111
	.byte	-88
	.byte	-66
	.byte	-42
	.byte	22
	.byte	31
	.byte	50
	.byte	79
	.byte	103
	.byte	120
	.byte	-105
	.byte	-86
	.byte	-53
	.byte	-29
	.byte	21
	.byte	29
	.byte	45
	.byte	65
	.byte	106
	.byte	124
	.byte	-106
	.byte	-85
	.byte	-60
	.byte	-32
	.byte	30
	.byte	49
	.byte	75
	.byte	97
	.byte	121
	.byte	-114
	.byte	-91
	.byte	-70
	.byte	-47
	.byte	-27
	.byte	19
	.byte	25
	.byte	52
	.byte	70
	.byte	93
	.byte	116
	.byte	-113
	.byte	-90
	.byte	-64
	.byte	-37
	.byte	26
	.byte	34
	.byte	62
	.byte	75
	.byte	97
	.byte	118
	.byte	-111
	.byte	-89
	.byte	-62
	.byte	-39
	.byte	25
	.byte	33
	.byte	56
	.byte	70
	.byte	91
	.byte	113
	.byte	-113
	.byte	-91
	.byte	-60
	.byte	-33
	.byte	21
	.byte	34
	.byte	51
	.byte	72
	.byte	97
	.byte	117
	.byte	-111
	.byte	-85
	.byte	-60
	.byte	-34
	.byte	20
	.byte	29
	.byte	50
	.byte	67
	.byte	90
	.byte	117
	.byte	-112
	.byte	-88
	.byte	-59
	.byte	-35
	.byte	22
	.byte	31
	.byte	48
	.byte	66
	.byte	95
	.byte	117
	.byte	-110
	.byte	-88
	.byte	-60
	.byte	-34
	.byte	24
	.byte	33
	.byte	51
	.byte	77
	.byte	116
	.byte	-122
	.byte	-98
	.byte	-76
	.byte	-56
	.byte	-32
	.byte	21
	.byte	28
	.byte	70
	.byte	87
	.byte	106
	.byte	124
	.byte	-107
	.byte	-86
	.byte	-62
	.byte	-39
	.byte	26
	.byte	33
	.byte	53
	.byte	64
	.byte	83
	.byte	117
	.byte	-104
	.byte	-83
	.byte	-52
	.byte	-31
	.byte	27
	.byte	34
	.byte	65
	.byte	95
	.byte	108
	.byte	-127
	.byte	-101
	.byte	-82
	.byte	-46
	.byte	-31
	.byte	20
	.byte	26
	.byte	72
	.byte	99
	.byte	113
	.byte	-125
	.byte	-102
	.byte	-80
	.byte	-56
	.byte	-37
	.byte	34
	.byte	43
	.byte	61
	.byte	78
	.byte	93
	.byte	114
	.byte	-101
	.byte	-79
	.byte	-51
	.byte	-27
	.byte	23
	.byte	29
	.byte	54
	.byte	97
	.byte	124
	.byte	-118
	.byte	-93
	.byte	-77
	.byte	-47
	.byte	-27
	.byte	30
	.byte	38
	.byte	56
	.byte	89
	.byte	118
	.byte	-127
	.byte	-98
	.byte	-78
	.byte	-56
	.byte	-25
	.byte	21
	.byte	29
	.byte	49
	.byte	63
	.byte	85
	.byte	111
	.byte	-114
	.byte	-93
	.byte	-63
	.byte	-34
	.byte	27
	.byte	48
	.byte	77
	.byte	103
	.byte	-123
	.byte	-98
	.byte	-77
	.byte	-60
	.byte	-41
	.byte	-24
	.byte	29
	.byte	47
	.byte	74
	.byte	99
	.byte	124
	.byte	-105
	.byte	-80
	.byte	-58
	.byte	-36
	.byte	-19
	.byte	33
	.byte	42
	.byte	61
	.byte	76
	.byte	93
	.byte	121
	.byte	-101
	.byte	-82
	.byte	-49
	.byte	-31
	.byte	29
	.byte	53
	.byte	87
	.byte	112
	.byte	-120
	.byte	-102
	.byte	-86
	.byte	-68
	.byte	-48
	.byte	-29
	.byte	24
	.byte	30
	.byte	52
	.byte	84
	.byte	-125
	.byte	-106
	.byte	-90
	.byte	-70
	.byte	-53
	.byte	-27
	.byte	37
	.byte	48
	.byte	64
	.byte	84
	.byte	104
	.byte	118
	.byte	-100
	.byte	-79
	.byte	-55
	.byte	-26
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
