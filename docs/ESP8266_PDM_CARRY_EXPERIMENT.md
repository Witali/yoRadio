# PDM carry accumulation experiment (not retained)

2026-09-09, Xtensa LX106 GCC8.4, -O3, current native I2S PDM32 packer.

Candidate: replace `word = (word << 1) | (sum >> 16)` with addition.
The carry is0 or1 and the shifted word has bit0 clear, so both forms are
bit-exact. A temporary host test compiled the actual candidate kernel and
compared all65536 PCM values at16 starting accumulator states, followed by
1000000 stateful random samples:2048576 output words and final states matched.
ASan/UBSan passed.

The expected ADDX2 fusion did **not** occur with this target compiler:

| Kernel | Instructions | OR | ADDX2 | Text bytes | Stack bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original OR |164|31|0|456|0|
| Candidate addition |164|0|0|425|0|

Addition replaced OR with short ADD instructions, but did not reduce the
instruction count. No physical timing improvement was established. The
candidate and its temporary test were removed; production retains the original
OR expression. Investigate placement of the unchanged hot packer in IRAM
without shrinking the shared16-KiB decoder arena instead.
