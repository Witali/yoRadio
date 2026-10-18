#include "icy_title.h"

#include <string.h>

static const char title_key[] = "StreamTitle='";
_Static_assert(sizeof(icy_title_parser_t) <= 208, "Keep ICY state bounded");
_Static_assert(sizeof(title_key) < UINT8_MAX, "Prefix counter fits");

void icy_title_begin(icy_title_parser_t *parser) {
    memset(parser, 0, sizeof(*parser));
}

void icy_title_feed(icy_title_parser_t *parser, const uint8_t *data, size_t size) {
    for (size_t i = 0; i < size && !parser->stopped; ++i) {
        const uint8_t value = data[i];
        // The previous strstr/strchr parser stopped at the first padding NUL.
        if (!value) {
            parser->stopped = true;
            break;
        }
        if (!parser->found) {
            if (value == (uint8_t)title_key[parser->matched]) {
                if (++parser->matched == sizeof(title_key) - 1U) {
                    parser->found = true;
                }
            } else {
                // 'S' occurs only at the start of this fixed key; keep an
                // overlapping candidate such as "SStreamTitle='...".
                parser->matched = value == (uint8_t)title_key[0] ? 1U : 0U;
            }
            continue;
        }
        if (parser->quote_pending && value == ';') {
            parser->title[parser->pending_quote] = '\0';
            parser->complete = true;
            parser->stopped = true;
            break;
        }
        parser->quote_pending = value == '\'';
        if (parser->quote_pending) {
            parser->pending_quote = parser->stored;
            if (!parser->has_quote) {
                parser->first_quote = parser->stored;
                parser->has_quote = true;
            }
        }
        if (parser->stored < ICY_TITLE_CAPACITY - 1U) {
            parser->title[parser->stored++] = (char)value;
        }
    }
}

const char *icy_title_finish(icy_title_parser_t *parser) {
    parser->stopped = true;
    if (parser->complete) return parser->title;
    if (!parser->found || !parser->has_quote) return NULL;
    parser->title[parser->first_quote] = '\0';
    return parser->title;
}
