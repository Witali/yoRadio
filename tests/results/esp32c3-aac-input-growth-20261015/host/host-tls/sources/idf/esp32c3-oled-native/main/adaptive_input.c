#include "adaptive_input.h"

#include <stdlib.h>
#include "freertos/semphr.h"
#include "freertos/task.h"

enum { INPUT_MAX_SLOTS = 16, CONTROL_SLOT = INPUT_MAX_SLOTS,
       NO_SLOT = CONTROL_SLOT + 1 };
typedef enum { ABSENT, ALLOCATING, IDLE, WRITING, READY, READING } slot_state_t;
typedef struct {
    void *data;
    size_t size;
    slot_state_t state;
    unsigned next;
} input_slot_t;

struct adaptive_input {
    portMUX_TYPE lock;
    SemaphoreHandle_t data_ready, space_ready;
    size_t packet_capacity;
    unsigned target, minimum, resident, released, limit;
    unsigned head, tail;
    input_slot_t slots[INPUT_MAX_SLOTS];
    input_slot_t control;
    size_t control_capacity;
};

static input_slot_t *input_slot(adaptive_input_t *input, unsigned index) {
    return index == CONTROL_SLOT ? &input->control : &input->slots[index];
}

adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input) {
    adaptive_input_stats_t result = {0};
    if (!input) return result;
    portENTER_CRITICAL(&input->lock);
    result.packet_capacity = input->packet_capacity;
    result.resident = input->resident;
    result.minimum = input->minimum;
    result.target = input->target;
    result.limit = input->limit;
    result.released = input->released;
    for (unsigned i = 0; i < input->target; ++i) {
        slot_state_t state = input->slots[i].state;
        if (state == WRITING || state == READY || state == READING)
            ++result.occupied;
    }
    portEXIT_CRITICAL(&input->lock);
    return result;
}

bool adaptive_input_restore_one(adaptive_input_t *input) {
    if (!input) return false;
    for (unsigned i = 0; i < input->target; ++i) {
        portENTER_CRITICAL(&input->lock);
        bool allocate = input->resident < input->limit &&
                        input->slots[i].state == ABSENT;
        if (allocate) input->slots[i].state = ALLOCATING;
        portEXIT_CRITICAL(&input->lock);
        if (!allocate) continue;
        void *data = malloc(input->packet_capacity);
        portENTER_CRITICAL(&input->lock);
        // The policy can shrink while malloc runs. Never publish a new slot
        // beyond that limit, even if allocation itself succeeded.
        bool publish = data && input->resident < input->limit;
        input->slots[i].data = publish ? data : NULL;
        input->slots[i].state = publish ? IDLE : ABSENT;
        if (publish) ++input->resident;
        portEXIT_CRITICAL(&input->lock);
        if (publish) xSemaphoreGive(input->space_ready);
        else free(data);
        return publish;
    }
    return false;
}

void adaptive_input_restore(adaptive_input_t *input) {
    if (!input) return;
    // Bound work even if TLS keeps reclaiming slots during this refill.
    for (unsigned attempt = 0; attempt < input->target; ++attempt) {
        if (!adaptive_input_restore_one(input)) break;
    }
}

// Caller holds the queue lock. Keep the first limit resident buffers stable
// through ordinary stream shutdown. Busy later buffers retire on return.
// Emergency reclamation can leave holes, so rank resident pointers instead
// of assuming that every lower slot index still contains an allocation.
static bool should_retire_slot(const adaptive_input_t *input, unsigned index) {
    if (input->resident <= input->limit) return false;
    unsigned earlier = 0;
    for (unsigned i = 0; i < index; ++i)
        if (input->slots[i].data) ++earlier;
    return earlier >= input->limit;
}

void adaptive_input_set_limit(adaptive_input_t *input, unsigned slots) {
    if (!input) return;
    portENTER_CRITICAL(&input->lock);
    if (slots < input->minimum) slots = input->minimum;
    if (slots > input->target) slots = input->target;
    input->limit = slots;
    portEXIT_CRITICAL(&input->lock);
    for (unsigned i = input->target; i > 0; --i) {
        void *data = NULL;
        portENTER_CRITICAL(&input->lock);
        input_slot_t *slot = &input->slots[i - 1];
        if (slot->state == IDLE && should_retire_slot(input, i - 1)) {
            data = slot->data;
            slot->data = NULL;
            slot->state = ABSENT;
            --input->resident;
            ++input->released;
        }
        portEXIT_CRITICAL(&input->lock);
        free(data);
    }
}

adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity) {
    if (!packet_capacity) return NULL;
    // Round up so the legacy 8000-byte setting still provides at least that
    // much allocated packet storage; never silently lower the configured floor.
    size_t target = budget / packet_capacity + (budget % packet_capacity != 0);
    if (target < 2 || target > INPUT_MAX_SLOTS) return NULL;
    adaptive_input_t *input = calloc(1, sizeof(*input));
    if (!input) return NULL;
    input->lock = (portMUX_TYPE)portMUX_INITIALIZER_UNLOCKED;
    input->packet_capacity = packet_capacity;
    input->target = (unsigned)target;
    input->limit = input->target;
    // Round the minimum up, without overflowing on a malformed size argument.
    size_t minimum = minimum_bytes / packet_capacity +
                     (minimum_bytes % packet_capacity != 0);
    if (minimum < 2) minimum = 2;
    if (minimum > input->target) minimum = input->target;
    input->minimum = (unsigned)minimum;
    input->head = input->tail = NO_SLOT;
    input->data_ready = xSemaphoreCreateBinary();
    input->space_ready = xSemaphoreCreateBinary();
    if (!input->data_ready || !input->space_ready) {
        adaptive_input_destroy(input);
        return NULL;
    }
    adaptive_input_restore(input);
    if (input->resident < input->minimum) {
        adaptive_input_destroy(input);
        return NULL;
    }
    return input;
}

void adaptive_input_destroy(adaptive_input_t *input) {
    if (!input) return;
    for (unsigned i = 0; i < input->target; ++i) free(input->slots[i].data);
    if (input->data_ready) vSemaphoreDelete(input->data_ready);
    if (input->space_ready) vSemaphoreDelete(input->space_ready);
    free(input);
}

static bool wait_event(SemaphoreHandle_t event, TickType_t start,
                        TickType_t timeout) {
    TickType_t elapsed = xTaskGetTickCount() - start;
    if (timeout != portMAX_DELAY && elapsed >= timeout) return false;
    TickType_t remaining = timeout == portMAX_DELAY ? timeout : timeout - elapsed;
    return xSemaphoreTake(event, remaining) == pdTRUE;
}

BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout) {
    if (packet) *packet = NULL;
    if (!input || !packet || !size || size > input->packet_capacity) return pdFALSE;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        for (unsigned i = 0; i < input->target; ++i) {
            input_slot_t *slot = &input->slots[i];
            if (slot->state != IDLE) continue;
            slot->state = WRITING;
            slot->size = size;
            *packet = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return pdTRUE;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->space_ready, start, timeout));
    return pdFALSE;
}

BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet) {
    if (!input || !packet) return pdFALSE;
    portENTER_CRITICAL(&input->lock);
    for (unsigned scan = 0; scan <= input->target; ++scan) {
        unsigned i = scan == input->target ? CONTROL_SLOT : scan;
        input_slot_t *slot = input_slot(input, i);
        if (slot->data != packet || slot->state != WRITING) continue;
        slot->state = READY;
        slot->next = NO_SLOT;
        if (input->tail != NO_SLOT) input_slot(input, input->tail)->next = i;
        else input->head = i;
        input->tail = i;
        portEXIT_CRITICAL(&input->lock);
        xSemaphoreGive(input->data_ready);
        return pdTRUE;
    }
    portEXIT_CRITICAL(&input->lock);
    return pdFALSE;
}

bool adaptive_input_attach_control(adaptive_input_t *input, void *storage,
                                    size_t capacity) {
    if (!input || !storage || !capacity) return false;
    portENTER_CRITICAL(&input->lock);
    bool available = input->control.data == NULL;
    for (unsigned i = 0; i < input->target; ++i)
        if (input->slots[i].data == storage) available = false;
    if (available) {
        input->control = (input_slot_t){.data=storage, .state=IDLE, .next=NO_SLOT};
        input->control_capacity = capacity;
    }
    portEXIT_CRITICAL(&input->lock);
    return available;
}

BaseType_t adaptive_input_acquire_control(adaptive_input_t *input, void **packet,
                                          size_t size, TickType_t timeout) {
    if (packet) *packet = NULL;
    if (!input || !packet || !size) return pdFALSE;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        if (size > input->control_capacity) {
            portEXIT_CRITICAL(&input->lock);
            return pdFALSE;
        }
        input_slot_t *slot = &input->control;
        if (slot->state == IDLE) {
            slot->state = WRITING;
            slot->size = size;
            *packet = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return pdTRUE;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->space_ready, start, timeout));
    return pdFALSE;
}

void *adaptive_input_receive(adaptive_input_t *input, size_t *size,
                             TickType_t timeout) {
    if (size) *size = 0;
    if (!input || !size) return NULL;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        if (input->head != NO_SLOT) {
            input_slot_t *slot = input_slot(input, input->head);
            input->head = slot->next;
            if (input->head == NO_SLOT) input->tail = NO_SLOT;
            slot->state = READING;
            *size = slot->size;
            void *data = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return data;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->data_ready, start, timeout));
    return NULL;
}

static bool release_lease(adaptive_input_t *input, void *packet, slot_state_t expected) {
    if (!input || !packet) return false;
    portENTER_CRITICAL(&input->lock);
    for (unsigned scan = 0; scan <= input->target; ++scan) {
        unsigned i = scan == input->target ? CONTROL_SLOT : scan;
        input_slot_t *slot = input_slot(input, i);
        if (slot->data != packet || slot->state != expected) continue;
        bool release = i != CONTROL_SLOT && should_retire_slot(input, i);
        if (release) {
            slot->data = NULL;
            --input->resident;
            ++input->released;
        }
        slot->state = release ? ABSENT : IDLE;
        slot->size = 0;
        portEXIT_CRITICAL(&input->lock);
        if (release) free(packet);
        xSemaphoreGive(input->space_ready);
        return true;
    }
    portEXIT_CRITICAL(&input->lock);
    return false;
}

bool adaptive_input_return(adaptive_input_t *input, void *packet) {
    return release_lease(input, packet, READING);
}

bool adaptive_input_cancel(adaptive_input_t *input, void *packet) {
    return release_lease(input, packet, WRITING);
}

bool adaptive_input_release_one(adaptive_input_t *input) {
    if (!input) return false;
    void *data = NULL;
    portENTER_CRITICAL(&input->lock);
    if (input->resident > input->minimum) {
        for (unsigned i = input->target; i > 0; --i) {
            input_slot_t *slot = &input->slots[i - 1];
            if (slot->state != IDLE) continue;
            data = slot->data;
            slot->data = NULL;
            slot->state = ABSENT;
            --input->resident;
            ++input->released;
            break;
        }
    }
    portEXIT_CRITICAL(&input->lock);
    // Never call the heap allocator while holding the queue's spinlock.
    bool released = data != NULL;
    free(data);
    return released;
}
