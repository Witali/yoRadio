#pragma once

#include "adaptive_input.h"

/* Task-only, non-owning publication by the exclusive pipeline lifecycle owner.
 * Bind after successful READY commitment, with no later startup rollback. The
 * queue and its caller-owned control storage must outlive every allocator pin.
 * A repeated bind to the same active owner is idempotent. */
bool native_input_reclaim_bind(adaptive_input_t *input);

typedef enum {
    NATIVE_INPUT_RECLAIM_DETACHED,
    NATIVE_INPUT_RECLAIM_BUSY,
    NATIVE_INPUT_RECLAIM_WRONG_OWNER,
} native_input_reclaim_detach_result_t;

/* Task-only, exclusive lifecycle owner. Wrong/NULL owner has no effects.
 * BUSY closes admission but retains ownership until an explicit retry observes
 * zero pins. New binds stay rejected; the last unpin never clears ownership.
 * DETACHED drains allocator users only: ordinary producer/consumer/restore and
 * health readers must separately be quiescent before adaptive_input_destroy.
 * Current playback Stop/EOF/maintenance never destroys the successful pool. */
native_input_reclaim_detach_result_t native_input_reclaim_detach(adaptive_input_t *input);

/* Linker entry point. Original SDK calloc is always called first and retains
 * argument/zeroing/free semantics. Only a valid task-context NULL result may
 * reclaim IDLE extras, with a fixed initial target-minus-minimum retry budget.
 * No global failed-allocation callback or free allocator is replaced. */
void *__wrap_esp_mbedtls_mem_calloc(size_t count, size_t size);
