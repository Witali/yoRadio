#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum { ICY_TITLE_CAPACITY = 192, ICY_METADATA_BLOCK_BYTES = 16 };

// Retain the published prefix, not a complete 4080-byte ICY metadata block.
// A quote followed by ';' takes precedence over the legacy bare-quote fallback.
typedef struct {
    char title[ICY_TITLE_CAPACITY];
    uint16_t stored, first_quote, pending_quote;
    uint8_t matched;
    bool found, has_quote, quote_pending, complete, stopped;
} icy_title_parser_t;

void icy_title_begin(icy_title_parser_t *parser);
void icy_title_feed(icy_title_parser_t *parser, const uint8_t *data, size_t size);
// NULL means no complete title; an empty string means explicitly clear it.
const char *icy_title_finish(icy_title_parser_t *parser);
