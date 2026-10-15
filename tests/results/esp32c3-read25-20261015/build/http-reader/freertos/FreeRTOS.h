#pragma once
typedef unsigned UBaseType_t;
extern unsigned test_interrupt_mask;
static inline unsigned test_mask(void) { unsigned old=test_interrupt_mask; test_interrupt_mask=31; return old; }
#define portSET_INTERRUPT_MASK_FROM_ISR() test_mask()
#define portCLEAR_INTERRUPT_MASK_FROM_ISR(previous) (test_interrupt_mask=(previous))
