#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

uint32_t text_utf8_decode(const char *text, size_t available, size_t *consumed);
size_t text_utf8_copy(char *out, size_t capacity, const char *text, size_t source_limit);
