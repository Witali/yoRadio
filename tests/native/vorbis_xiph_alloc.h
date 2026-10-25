#ifndef VORBIS_XIPH_TEST_ALLOC_H
#define VORBIS_XIPH_TEST_ALLOC_H
#include <stddef.h>
#ifdef NDEBUG
#error "Resource tests require active assertions"
#endif
void xiph_port_test_reset(size_t fail_at);
void xiph_port_test_zero_null(int enabled);
size_t xiph_port_test_attempts(void);
size_t xiph_port_test_realloc_attempts(void);
size_t xiph_port_test_live(void);
size_t xiph_port_test_bytes(void);
size_t xiph_port_test_failures(void);
void *xiph_port_test_malloc(size_t bytes);
void *xiph_port_test_calloc(size_t count, size_t bytes);
void *xiph_port_test_realloc(void *pointer, size_t bytes);
void xiph_port_test_free(void *pointer);
#endif
