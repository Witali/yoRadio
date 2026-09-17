#pragma once
#include <stddef.h>

enum memory_profile_task { MEMORY_APP, MEMORY_AUDIO, MEMORY_WEB, MEMORY_TASKS };

#if YORADIO_ESP8266_MEMORY_PROFILE
void memory_profile_register(enum memory_profile_task task);
void memory_profile_poll(void);
/* Nonblocking TCP request + last completed owner-thread sample. No heap
 * allocation in the formatter; lwIP may allocate its callback message.
 * Fresh heap and older TCP timestamps must not be treated as simultaneous. */
int memory_profile_json(char *output, size_t capacity);
#else
static inline void memory_profile_register(enum memory_profile_task task) {
    (void)task;
}
static inline void memory_profile_poll(void) {}
#endif
