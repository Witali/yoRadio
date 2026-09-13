# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/tables_pulses_per_block.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"tables_pulses_per_block.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\tables_pulses_per_block.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\tables_pulses_per_block.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\tables_pulses_per_block.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\tables_pulses_per_block.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\tables_pulses_per_block.c.s.raw
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
	.global	silk_sign_iCDF
	.section	.rodata.silk_sign_iCDF,"a"
	.align	4
	.type	silk_sign_iCDF, @object
	.size	silk_sign_iCDF, 42
silk_sign_iCDF:
	.byte	-2
	.byte	49
	.byte	67
	.byte	77
	.byte	82
	.byte	93
	.byte	99
	.byte	-58
	.byte	11
	.byte	18
	.byte	24
	.byte	31
	.byte	36
	.byte	45
	.byte	-1
	.byte	46
	.byte	66
	.byte	78
	.byte	87
	.byte	94
	.byte	104
	.byte	-48
	.byte	14
	.byte	21
	.byte	32
	.byte	42
	.byte	51
	.byte	66
	.byte	-1
	.byte	94
	.byte	104
	.byte	109
	.byte	112
	.byte	115
	.byte	118
	.byte	-8
	.byte	53
	.byte	69
	.byte	80
	.byte	88
	.byte	95
	.byte	102
	.global	silk_shell_code_table_offsets
	.section	.rodata.silk_shell_code_table_offsets,"a"
	.align	4
	.type	silk_shell_code_table_offsets, @object
	.size	silk_shell_code_table_offsets, 17
silk_shell_code_table_offsets:
	.byte	0
	.byte	0
	.byte	2
	.byte	5
	.byte	9
	.byte	14
	.byte	20
	.byte	27
	.byte	35
	.byte	44
	.byte	54
	.byte	65
	.byte	77
	.byte	90
	.byte	104
	.byte	119
	.byte	-121
	.global	silk_shell_code_table3
	.section	.rodata.silk_shell_code_table3,"a"
	.align	4
	.type	silk_shell_code_table3, @object
	.size	silk_shell_code_table3, 152
silk_shell_code_table3:
	.byte	-126
	.byte	0
	.byte	-56
	.byte	58
	.byte	0
	.byte	-25
	.byte	-126
	.byte	26
	.byte	0
	.byte	-12
	.byte	-72
	.byte	76
	.byte	12
	.byte	0
	.byte	-7
	.byte	-42
	.byte	-126
	.byte	43
	.byte	6
	.byte	0
	.byte	-4
	.byte	-24
	.byte	-83
	.byte	87
	.byte	24
	.byte	3
	.byte	0
	.byte	-3
	.byte	-15
	.byte	-53
	.byte	-125
	.byte	56
	.byte	14
	.byte	2
	.byte	0
	.byte	-2
	.byte	-10
	.byte	-35
	.byte	-89
	.byte	94
	.byte	35
	.byte	8
	.byte	1
	.byte	0
	.byte	-2
	.byte	-7
	.byte	-24
	.byte	-63
	.byte	-126
	.byte	65
	.byte	23
	.byte	5
	.byte	1
	.byte	0
	.byte	-1
	.byte	-5
	.byte	-17
	.byte	-45
	.byte	-94
	.byte	99
	.byte	45
	.byte	15
	.byte	4
	.byte	1
	.byte	0
	.byte	-1
	.byte	-5
	.byte	-13
	.byte	-33
	.byte	-70
	.byte	-125
	.byte	74
	.byte	33
	.byte	11
	.byte	3
	.byte	1
	.byte	0
	.byte	-1
	.byte	-4
	.byte	-11
	.byte	-26
	.byte	-54
	.byte	-98
	.byte	105
	.byte	57
	.byte	24
	.byte	8
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-3
	.byte	-9
	.byte	-21
	.byte	-42
	.byte	-77
	.byte	-124
	.byte	84
	.byte	44
	.byte	19
	.byte	7
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-6
	.byte	-16
	.byte	-33
	.byte	-60
	.byte	-97
	.byte	112
	.byte	69
	.byte	36
	.byte	15
	.byte	6
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-3
	.byte	-11
	.byte	-25
	.byte	-47
	.byte	-80
	.byte	-120
	.byte	93
	.byte	55
	.byte	27
	.byte	11
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-3
	.byte	-4
	.byte	-17
	.byte	-35
	.byte	-62
	.byte	-98
	.byte	117
	.byte	76
	.byte	42
	.byte	18
	.byte	4
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.global	silk_shell_code_table2
	.section	.rodata.silk_shell_code_table2,"a"
	.align	4
	.type	silk_shell_code_table2, @object
	.size	silk_shell_code_table2, 152
silk_shell_code_table2:
	.byte	-127
	.byte	0
	.byte	-53
	.byte	54
	.byte	0
	.byte	-22
	.byte	-127
	.byte	23
	.byte	0
	.byte	-11
	.byte	-72
	.byte	73
	.byte	10
	.byte	0
	.byte	-6
	.byte	-41
	.byte	-127
	.byte	41
	.byte	5
	.byte	0
	.byte	-4
	.byte	-24
	.byte	-83
	.byte	86
	.byte	24
	.byte	3
	.byte	0
	.byte	-3
	.byte	-16
	.byte	-56
	.byte	-127
	.byte	56
	.byte	15
	.byte	2
	.byte	0
	.byte	-3
	.byte	-12
	.byte	-39
	.byte	-92
	.byte	94
	.byte	38
	.byte	10
	.byte	1
	.byte	0
	.byte	-3
	.byte	-11
	.byte	-30
	.byte	-67
	.byte	-124
	.byte	71
	.byte	27
	.byte	7
	.byte	1
	.byte	0
	.byte	-3
	.byte	-10
	.byte	-25
	.byte	-53
	.byte	-97
	.byte	105
	.byte	56
	.byte	23
	.byte	6
	.byte	1
	.byte	0
	.byte	-1
	.byte	-8
	.byte	-21
	.byte	-43
	.byte	-77
	.byte	-123
	.byte	85
	.byte	47
	.byte	19
	.byte	5
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-13
	.byte	-35
	.byte	-62
	.byte	-97
	.byte	117
	.byte	70
	.byte	37
	.byte	12
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-8
	.byte	-22
	.byte	-48
	.byte	-85
	.byte	-128
	.byte	85
	.byte	48
	.byte	22
	.byte	8
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-6
	.byte	-16
	.byte	-36
	.byte	-67
	.byte	-107
	.byte	107
	.byte	67
	.byte	36
	.byte	16
	.byte	6
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-5
	.byte	-13
	.byte	-29
	.byte	-55
	.byte	-90
	.byte	-128
	.byte	90
	.byte	55
	.byte	29
	.byte	13
	.byte	5
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-4
	.byte	-10
	.byte	-22
	.byte	-43
	.byte	-73
	.byte	-109
	.byte	109
	.byte	73
	.byte	43
	.byte	22
	.byte	10
	.byte	4
	.byte	2
	.byte	1
	.byte	0
	.global	silk_shell_code_table1
	.section	.rodata.silk_shell_code_table1,"a"
	.align	4
	.type	silk_shell_code_table1, @object
	.size	silk_shell_code_table1, 152
silk_shell_code_table1:
	.byte	-127
	.byte	0
	.byte	-49
	.byte	50
	.byte	0
	.byte	-20
	.byte	-127
	.byte	20
	.byte	0
	.byte	-11
	.byte	-71
	.byte	72
	.byte	10
	.byte	0
	.byte	-7
	.byte	-43
	.byte	-127
	.byte	42
	.byte	6
	.byte	0
	.byte	-6
	.byte	-30
	.byte	-87
	.byte	87
	.byte	27
	.byte	4
	.byte	0
	.byte	-5
	.byte	-23
	.byte	-62
	.byte	-126
	.byte	62
	.byte	20
	.byte	4
	.byte	0
	.byte	-6
	.byte	-20
	.byte	-49
	.byte	-96
	.byte	99
	.byte	47
	.byte	17
	.byte	3
	.byte	0
	.byte	-1
	.byte	-16
	.byte	-39
	.byte	-74
	.byte	-125
	.byte	81
	.byte	41
	.byte	11
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-23
	.byte	-55
	.byte	-97
	.byte	107
	.byte	61
	.byte	20
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-7
	.byte	-23
	.byte	-50
	.byte	-86
	.byte	-128
	.byte	86
	.byte	50
	.byte	23
	.byte	7
	.byte	1
	.byte	0
	.byte	-1
	.byte	-6
	.byte	-18
	.byte	-39
	.byte	-70
	.byte	-108
	.byte	108
	.byte	70
	.byte	39
	.byte	18
	.byte	6
	.byte	1
	.byte	0
	.byte	-1
	.byte	-4
	.byte	-13
	.byte	-30
	.byte	-56
	.byte	-90
	.byte	-128
	.byte	90
	.byte	56
	.byte	30
	.byte	13
	.byte	4
	.byte	1
	.byte	0
	.byte	-1
	.byte	-4
	.byte	-11
	.byte	-25
	.byte	-47
	.byte	-76
	.byte	-110
	.byte	110
	.byte	76
	.byte	47
	.byte	25
	.byte	11
	.byte	4
	.byte	1
	.byte	0
	.byte	-1
	.byte	-3
	.byte	-8
	.byte	-19
	.byte	-37
	.byte	-62
	.byte	-93
	.byte	-128
	.byte	93
	.byte	62
	.byte	37
	.byte	19
	.byte	8
	.byte	3
	.byte	1
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-6
	.byte	-15
	.byte	-30
	.byte	-51
	.byte	-79
	.byte	-111
	.byte	111
	.byte	79
	.byte	51
	.byte	30
	.byte	15
	.byte	6
	.byte	2
	.byte	1
	.byte	0
	.global	silk_shell_code_table0
	.section	.rodata.silk_shell_code_table0,"a"
	.align	4
	.type	silk_shell_code_table0, @object
	.size	silk_shell_code_table0, 152
silk_shell_code_table0:
	.byte	-128
	.byte	0
	.byte	-42
	.byte	42
	.byte	0
	.byte	-21
	.byte	-128
	.byte	21
	.byte	0
	.byte	-12
	.byte	-72
	.byte	72
	.byte	11
	.byte	0
	.byte	-8
	.byte	-42
	.byte	-128
	.byte	42
	.byte	7
	.byte	0
	.byte	-8
	.byte	-31
	.byte	-86
	.byte	80
	.byte	25
	.byte	5
	.byte	0
	.byte	-5
	.byte	-20
	.byte	-58
	.byte	126
	.byte	54
	.byte	18
	.byte	3
	.byte	0
	.byte	-6
	.byte	-18
	.byte	-45
	.byte	-97
	.byte	82
	.byte	35
	.byte	15
	.byte	5
	.byte	0
	.byte	-6
	.byte	-25
	.byte	-53
	.byte	-88
	.byte	-128
	.byte	88
	.byte	53
	.byte	25
	.byte	6
	.byte	0
	.byte	-4
	.byte	-18
	.byte	-40
	.byte	-71
	.byte	-108
	.byte	108
	.byte	71
	.byte	40
	.byte	18
	.byte	4
	.byte	0
	.byte	-3
	.byte	-13
	.byte	-31
	.byte	-57
	.byte	-90
	.byte	-128
	.byte	90
	.byte	57
	.byte	31
	.byte	13
	.byte	3
	.byte	0
	.byte	-2
	.byte	-10
	.byte	-23
	.byte	-44
	.byte	-73
	.byte	-109
	.byte	109
	.byte	73
	.byte	44
	.byte	23
	.byte	10
	.byte	2
	.byte	0
	.byte	-1
	.byte	-6
	.byte	-16
	.byte	-33
	.byte	-58
	.byte	-90
	.byte	-128
	.byte	90
	.byte	58
	.byte	33
	.byte	16
	.byte	6
	.byte	1
	.byte	0
	.byte	-1
	.byte	-5
	.byte	-12
	.byte	-25
	.byte	-46
	.byte	-75
	.byte	-110
	.byte	110
	.byte	75
	.byte	46
	.byte	25
	.byte	12
	.byte	5
	.byte	1
	.byte	0
	.byte	-1
	.byte	-3
	.byte	-8
	.byte	-18
	.byte	-35
	.byte	-60
	.byte	-92
	.byte	-128
	.byte	92
	.byte	60
	.byte	35
	.byte	18
	.byte	8
	.byte	3
	.byte	1
	.byte	0
	.byte	-1
	.byte	-3
	.byte	-7
	.byte	-14
	.byte	-27
	.byte	-48
	.byte	-76
	.byte	-110
	.byte	110
	.byte	76
	.byte	48
	.byte	27
	.byte	14
	.byte	7
	.byte	3
	.byte	1
	.byte	0
	.global	silk_rate_levels_BITS_Q5
	.section	.rodata.silk_rate_levels_BITS_Q5,"a"
	.align	4
	.type	silk_rate_levels_BITS_Q5, @object
	.size	silk_rate_levels_BITS_Q5, 18
silk_rate_levels_BITS_Q5:
	.byte	-125
	.byte	74
	.byte	-115
	.byte	79
	.byte	80
	.byte	-118
	.byte	95
	.byte	104
	.byte	-122
	.byte	95
	.byte	99
	.byte	91
	.byte	125
	.byte	93
	.byte	76
	.byte	123
	.byte	115
	.byte	123
	.global	silk_rate_levels_iCDF
	.section	.rodata.silk_rate_levels_iCDF,"a"
	.align	4
	.type	silk_rate_levels_iCDF, @object
	.size	silk_rate_levels_iCDF, 18
silk_rate_levels_iCDF:
	.byte	-15
	.byte	-66
	.byte	-78
	.byte	-124
	.byte	87
	.byte	74
	.byte	41
	.byte	14
	.byte	0
	.byte	-33
	.byte	-63
	.byte	-99
	.byte	-116
	.byte	106
	.byte	57
	.byte	39
	.byte	18
	.byte	0
	.global	silk_pulses_per_block_BITS_Q5
	.section	.rodata.silk_pulses_per_block_BITS_Q5,"a"
	.align	4
	.type	silk_pulses_per_block_BITS_Q5, @object
	.size	silk_pulses_per_block_BITS_Q5, 162
silk_pulses_per_block_BITS_Q5:
	.byte	31
	.byte	57
	.byte	107
	.byte	-96
	.byte	-51
	.byte	-51
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	69
	.byte	47
	.byte	67
	.byte	111
	.byte	-90
	.byte	-51
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	82
	.byte	74
	.byte	79
	.byte	95
	.byte	109
	.byte	-128
	.byte	-111
	.byte	-96
	.byte	-83
	.byte	-51
	.byte	-51
	.byte	-51
	.byte	-32
	.byte	-1
	.byte	-1
	.byte	-32
	.byte	-1
	.byte	-32
	.byte	125
	.byte	74
	.byte	59
	.byte	69
	.byte	97
	.byte	-115
	.byte	-74
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-83
	.byte	115
	.byte	85
	.byte	73
	.byte	76
	.byte	92
	.byte	115
	.byte	-111
	.byte	-83
	.byte	-51
	.byte	-32
	.byte	-32
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-90
	.byte	-122
	.byte	113
	.byte	102
	.byte	101
	.byte	102
	.byte	107
	.byte	118
	.byte	125
	.byte	-118
	.byte	-111
	.byte	-101
	.byte	-90
	.byte	-74
	.byte	-64
	.byte	-64
	.byte	-51
	.byte	-106
	.byte	-32
	.byte	-74
	.byte	-122
	.byte	101
	.byte	83
	.byte	79
	.byte	85
	.byte	97
	.byte	120
	.byte	-111
	.byte	-83
	.byte	-51
	.byte	-32
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-32
	.byte	-64
	.byte	-106
	.byte	120
	.byte	101
	.byte	92
	.byte	89
	.byte	93
	.byte	102
	.byte	118
	.byte	-122
	.byte	-96
	.byte	-74
	.byte	-64
	.byte	-32
	.byte	-32
	.byte	-32
	.byte	-1
	.byte	-32
	.byte	-32
	.byte	-74
	.byte	-101
	.byte	-122
	.byte	118
	.byte	109
	.byte	104
	.byte	102
	.byte	106
	.byte	111
	.byte	118
	.byte	-125
	.byte	-111
	.byte	-96
	.byte	-83
	.byte	-125
	.global	silk_pulses_per_block_iCDF
	.section	.rodata.silk_pulses_per_block_iCDF,"a"
	.align	4
	.type	silk_pulses_per_block_iCDF, @object
	.size	silk_pulses_per_block_iCDF, 180
silk_pulses_per_block_iCDF:
	.byte	125
	.byte	51
	.byte	26
	.byte	18
	.byte	15
	.byte	12
	.byte	11
	.byte	10
	.byte	9
	.byte	8
	.byte	7
	.byte	6
	.byte	5
	.byte	4
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-58
	.byte	105
	.byte	45
	.byte	22
	.byte	15
	.byte	12
	.byte	11
	.byte	10
	.byte	9
	.byte	8
	.byte	7
	.byte	6
	.byte	5
	.byte	4
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-43
	.byte	-94
	.byte	116
	.byte	83
	.byte	59
	.byte	43
	.byte	32
	.byte	24
	.byte	18
	.byte	15
	.byte	12
	.byte	9
	.byte	7
	.byte	6
	.byte	5
	.byte	3
	.byte	2
	.byte	0
	.byte	-17
	.byte	-69
	.byte	116
	.byte	59
	.byte	28
	.byte	16
	.byte	11
	.byte	10
	.byte	9
	.byte	8
	.byte	7
	.byte	6
	.byte	5
	.byte	4
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-6
	.byte	-27
	.byte	-68
	.byte	-121
	.byte	86
	.byte	51
	.byte	30
	.byte	19
	.byte	13
	.byte	10
	.byte	8
	.byte	6
	.byte	5
	.byte	4
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-7
	.byte	-21
	.byte	-43
	.byte	-71
	.byte	-100
	.byte	-128
	.byte	103
	.byte	83
	.byte	66
	.byte	53
	.byte	42
	.byte	33
	.byte	26
	.byte	21
	.byte	17
	.byte	13
	.byte	10
	.byte	0
	.byte	-2
	.byte	-7
	.byte	-21
	.byte	-50
	.byte	-92
	.byte	118
	.byte	77
	.byte	46
	.byte	27
	.byte	16
	.byte	10
	.byte	7
	.byte	5
	.byte	4
	.byte	3
	.byte	2
	.byte	1
	.byte	0
	.byte	-1
	.byte	-3
	.byte	-7
	.byte	-17
	.byte	-36
	.byte	-65
	.byte	-100
	.byte	119
	.byte	85
	.byte	57
	.byte	37
	.byte	23
	.byte	15
	.byte	10
	.byte	6
	.byte	4
	.byte	2
	.byte	0
	.byte	-1
	.byte	-3
	.byte	-5
	.byte	-10
	.byte	-19
	.byte	-33
	.byte	-53
	.byte	-77
	.byte	-104
	.byte	124
	.byte	98
	.byte	75
	.byte	55
	.byte	40
	.byte	29
	.byte	21
	.byte	15
	.byte	0
	.byte	-1
	.byte	-2
	.byte	-3
	.byte	-9
	.byte	-36
	.byte	-94
	.byte	106
	.byte	67
	.byte	42
	.byte	28
	.byte	18
	.byte	12
	.byte	9
	.byte	6
	.byte	4
	.byte	3
	.byte	2
	.byte	0
	.global	silk_max_pulses_table
	.section	.rodata.silk_max_pulses_table,"a"
	.align	4
	.type	silk_max_pulses_table, @object
	.size	silk_max_pulses_table, 4
silk_max_pulses_table:
	.byte	8
	.byte	10
	.byte	12
	.byte	16
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
