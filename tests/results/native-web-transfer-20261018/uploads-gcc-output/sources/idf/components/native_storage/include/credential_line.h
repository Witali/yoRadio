#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

// Read one complete physical row, preserving field whitespace. Oversized or
// NUL-containing rows are discarded through their newline so a suffix can never
// become a separate credential. Strip only a terminal CR from a CRLF row.
// A read error rejects the partial row; callers can inspect ferror(file).
static inline bool native_credential_next_row(FILE *file, char *line, size_t capacity) {
    if (!file || !line || !capacity || feof(file) || ferror(file)) return false;
    for (;;) {
        size_t used = 0;
        bool valid = true, present = false;
        int value;
        while ((value = fgetc(file)) != EOF && value != '\n') {
            present = true;
            if (!value || used + 1U >= capacity) valid = false;
            else if (valid) line[used++] = (char)value;
        }
        if (ferror(file) || (value == EOF && !present)) return false;
        if (valid) {
            if (used && line[used - 1U] == '\r') --used;
            line[used] = '\0';
            return true;
        }
        if (value == EOF) return false;
    }
}
