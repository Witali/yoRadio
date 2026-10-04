/* QEMU-only call0 entry. Never linked into a radio firmware. */
.section .entry,"ax"
.global qemu_start
.align 4
.literal_position
.literal .Lstack, 0x3fff8000
.literal .Lbottom, 0x3fff6000
.literal .Lpattern, 0xa5a5a5a5
qemu_start:
    l32r a1, .Lstack
    l32r a3, .Lbottom
    l32r a4, .Lpattern
2:  s32i a4, a3, 0
    addi a3, a3, 4
    bltu a3, a1, 2b
    movi a2, 0
    wsr a2, ps
    rsync
    call0 qemu_main
    mov a3, a2
    movi a2, 1
    simcall
1:  j 1b
