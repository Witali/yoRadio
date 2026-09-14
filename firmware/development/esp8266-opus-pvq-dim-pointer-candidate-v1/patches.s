# decode_pulses/cwrsi many-dimensions search, Xtensa LX106 call0.
# Cache &ROW[K-1] in a0; each later probe decrements it by4.
# Original return saved in private sp+44; a0 is restored before RET.
# First successful probe has no extra instructions; zero-coordinate path untouched.
# Preserve every table read in order, remaining K/index, sign, energy and PCM.
# All registers except dead a0 agree at the old join; SAR/frame48/RAM unchanged.
# Original C/GCC snapshot remains the fallback; no new bitrate/mode limit.
.section .text.patch0,"ax",@progbits
.begin no-transform
pvq_dim_start:
 addi.n a8, a12, -1
 slli a0, a8, 2
 add.n a0, a14, a0
 l32i.n a11, a0, 0
 neg a6, a6
 add.n a11, a11, a3
 and a9, a6, a4
 l32i.n a4, a11, 0
 sub a2, a2, a9
 bltu a2, a4, .Lprobe2
 j .Lfound
.Lprobe2:
 addi a8, a12, -2
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bltu a2, a4, .Lprobe3
 j .Lfound
.Lprobe3:
 addi a8, a12, -3
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bltu a2, a4, .Lprobe4
 j .Lfound
.Lprobe4:
 addi a8, a12, -4
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bltu a2, a4, .Lprobe5
 j .Lfound
.Lprobe5:
 addi a8, a12, -5
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bltu a2, a4, .Lprobe6
 j .Lfound
.Lprobe6:
 addi a8, a12, -6
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bltu a2, a4, .Lprobe7
 j .Lfound
.Lprobe7:
 addi a8, a12, -7
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bltu a2, a4, .Lprobe8
 j .Lfound
.Lprobe8:
 addi a8, a12, -8
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bltu a2, a4, .Lprobe9
 j .Lfound
.Lprobe9:
 addi a8, a12, -9
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bgeu a2, a4, .Lfound
.Lprobe10:
 addi a8, a12, -10
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bgeu a2, a4, .Lfound
.Lprobe11:
 addi a8, a12, -11
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bgeu a2, a4, .Lfound
.Lprobe12:
 addi a8, a12, -12
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bgeu a2, a4, .Lfound
.Lprobe13:
 addi a8, a12, -13
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bgeu a2, a4, .Lfound
.Lprobe14:
 addi a8, a12, -14
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a4, a4, a3
 l32i.n a4, a4, 0
 bgeu a2, a4, .Lfound
.Lprobe15:
 addi a12, a12, -15
 addi a0, a0, -4
 l32i.n a4, a0, 0
 add.n a3, a4, a3
 l32i.n a4, a3, 0
 j pvq_dim_done
# Keep the common MOV at its original address, so early exits add no jump.
# Probe8 uses BLTU/J to stay in conditional-branch range. Only its exit adds1.
# Padding below follows an unconditional jump and cannot execute.
 .space 284 - (. - pvq_dim_start), 0
.Lfound:
 mov.n a12, a8
.end no-transform
