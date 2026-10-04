// QEMU-only branch bridge inside the pinned native AAC frame controller.
// At entry a4 is the parsed SBR-element count. The original branch consumes
// a4; the two continuations are exported from verified native local labels.
// Preserve every other caller-saved RV32IMC register across the C predicate.
    .section .text.aac_late_sbr_select,"ax",@progbits
    .align 2
    .global aac_late_sbr_select
    .type aac_late_sbr_select,@function
aac_late_sbr_select:
    beqz a4, .Lmissing
    j aac_late_sbr_native_active
.Lmissing:
    addi sp,sp,-64
    sw ra,0(sp)
    sw t0,4(sp)
    sw t1,8(sp)
    sw t2,12(sp)
    sw a0,16(sp)
    sw a1,20(sp)
    sw a2,24(sp)
    sw a3,28(sp)
    sw a5,32(sp)
    sw a6,36(sp)
    sw a7,40(sp)
    sw t3,44(sp)
    sw t4,48(sp)
    sw t5,52(sp)
    sw t6,56(sp)
    call aac_late_sbr_retain
    mv a4,a0
    lw ra,0(sp)
    lw t0,4(sp)
    lw t1,8(sp)
    lw t2,12(sp)
    lw a0,16(sp)
    lw a1,20(sp)
    lw a2,24(sp)
    lw a3,28(sp)
    lw a5,32(sp)
    lw a6,36(sp)
    lw a7,40(sp)
    lw t3,44(sp)
    lw t4,48(sp)
    lw t5,52(sp)
    lw t6,56(sp)
    addi sp,sp,64
    beqz a4,.Ldisabled
    j aac_late_sbr_native_active
.Ldisabled:
    j aac_late_sbr_native_disable
    .size aac_late_sbr_select,.-aac_late_sbr_select
    .section .note.GNU-stack,"",@progbits
