#pragma once

enum memory_profile_task { MEMORY_APP, MEMORY_AUDIO, MEMORY_WEB, MEMORY_TASKS };

#if YORADIO_ESP8266_MEMORY_PROFILE
void memory_profile_register(enum memory_profile_task task);
void memory_profile_poll(void);
#else
static inline void memory_profile_register(enum memory_profile_task task) {
    (void)task;
}
static inline void memory_profile_poll(void) {}
#endif
