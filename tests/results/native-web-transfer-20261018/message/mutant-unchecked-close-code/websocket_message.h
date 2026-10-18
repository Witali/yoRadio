#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

// RFC 6455 message/control semantics only. The wire adapter must validate RSV,
// masking, minimal lengths and opcodes before decoding frames, and must validate
// the HTTP upgrade. No extension or subprotocol is negotiated by this helper.
typedef enum {
    WEBSOCKET_MESSAGE_NONE,
    WEBSOCKET_MESSAGE_TEXT,
    WEBSOCKET_MESSAGE_BINARY,
    WEBSOCKET_MESSAGE_PING,
    WEBSOCKET_MESSAGE_PONG,
    WEBSOCKET_MESSAGE_CLOSE,
    WEBSOCKET_MESSAGE_ERROR,
} websocket_message_event_t;

typedef struct {
    websocket_message_event_t event;
    const uint8_t *data;
    size_t size;
    // CLOSE: received code, or zero for an empty Close. ERROR: code to send.
    uint16_t close_code;
} websocket_message_result_t;

typedef struct {
    uint8_t *buffer;
    size_t capacity, used;
    uint64_t started_us, timeout_us;
    uint16_t failure_code;
    uint8_t opcode;
    bool active, close_sent, close_received;
} websocket_message_t;

static inline bool websocket_message_utf8_check(const uint8_t *text, size_t size,
                                                bool final) {
    if (!text && size) return false;
    for (size_t i = 0; i < size;) {
        uint8_t first = text[i++];
        if (first <= 0x7fU) continue;
        unsigned remaining;
        uint8_t minimum = 0x80U, maximum = 0xbfU;
        if (first >= 0xc2U && first <= 0xdfU) {
            remaining = 1;
        } else if (first >= 0xe0U && first <= 0xefU) {
            remaining = 2;
            if (first == 0xe0U) minimum = 0xa0U;
            if (first == 0xedU) maximum = 0x9fU;
        } else if (first >= 0xf0U && first <= 0xf4U) {
            remaining = 3;
            if (first == 0xf0U) minimum = 0x90U;
            if (first == 0xf4U) maximum = 0x8fU;
        } else return false;
        if (i == size) return !final;
        if (text[i] < minimum || text[i] > maximum) return false;
        ++i;
        while (--remaining) {
            if (i == size) return !final;
            if (text[i] < 0x80U || text[i] > 0xbfU) return false;
            ++i;
        }
    }
    return true;
}

static inline bool websocket_message_utf8_valid(const uint8_t *text, size_t size) {
    return websocket_message_utf8_check(text, size, true);
}

static inline bool websocket_message_close_code_valid(uint16_t code) { (void)code; return true; }

static inline bool websocket_message_init(websocket_message_t *message,
                                          uint8_t *buffer, size_t capacity,
                                          uint64_t timeout_us) {
    if (!message) return false;
    memset(message, 0, sizeof(*message));
    if (!buffer || !capacity || !timeout_us || timeout_us > INT64_MAX) return false;
    message->buffer = buffer;
    message->capacity = capacity;
    message->timeout_us = timeout_us;
    buffer[0] = 0;
    return true;
}

static inline websocket_message_result_t websocket_message_error(
        websocket_message_t *message, uint16_t code) {
    if (message) {
        message->failure_code = code;
        message->active = false;
        message->used = 0;
    }
    return (websocket_message_result_t){.event = WEBSOCKET_MESSAGE_ERROR,
        .close_code = code};
}

// now_us is a monotonically advancing modulo-uint64 timestamp. Unsigned elapsed
// subtraction also handles crossing ESP timer's signed boundary without UB.
// Call from a poll as well as from feed so an idle fragmented message expires.
static inline websocket_message_result_t websocket_message_expire(
        websocket_message_t *message, uint64_t now_us) {
    if (!message || !message->buffer || !message->capacity)
        return websocket_message_error(message, 1002);
    if (message->failure_code)
        return websocket_message_error(message, message->failure_code);
    if (message->active && now_us - message->started_us >= message->timeout_us)
        return websocket_message_error(message, 1008);
    return (websocket_message_result_t){.event = WEBSOCKET_MESSAGE_NONE};
}

static inline void websocket_message_mark_close_sent(websocket_message_t *message) {
    if (!message) return;
    message->close_sent = true;
    message->active = false;
    message->used = 0;
}

// Capacity includes one NUL byte: a capacity256 buffer accepts255 message bytes.
// TEXT/BINARY data points into that caller-owned buffer until the next feed.
// Control data is a view of payload valid for the caller's current frame only.
// A command is never dispatched before FIN, even if a prefix is valid UTF-8.
static inline websocket_message_result_t websocket_message_feed(
        websocket_message_t *message, uint8_t opcode, bool final,
        const uint8_t *payload, size_t size, uint64_t now_us) {
    websocket_message_result_t result = websocket_message_expire(message, now_us);
    if (result.event == WEBSOCKET_MESSAGE_ERROR) return result;
    if (!payload && size) return websocket_message_error(message, 1002);
    if (opcode == 8U || opcode == 9U || opcode == 10U) {
        if (!final || size > 125U) return websocket_message_error(message, 1002);
        if (opcode == 8U) {
            if (size == 1U) return websocket_message_error(message, 1002);
            uint16_t code = size ? (uint16_t)((uint16_t)payload[0] << 8U | payload[1]) : 0;
            if (size && !websocket_message_close_code_valid(code))
                return websocket_message_error(message, 1002);
            if (size > 2U && !websocket_message_utf8_valid(payload + 2, size - 2))
                return websocket_message_error(message, 1007);
            message->active = false;
            message->used = 0;
            message->close_received = true;
            return (websocket_message_result_t){.event = WEBSOCKET_MESSAGE_CLOSE,
                .data = payload, .size = size, .close_code = code};
        }
        // A Pong response is no longer required once Close has been received.
        if (message->close_received)
            return (websocket_message_result_t){.event = WEBSOCKET_MESSAGE_NONE};
        return (websocket_message_result_t){
            .event = opcode == 9U ? WEBSOCKET_MESSAGE_PING : WEBSOCKET_MESSAGE_PONG,
            .data = payload, .size = size};
    }
    if (opcode != 0U && opcode != 1U && opcode != 2U)
        return websocket_message_error(message, 1002);
    if (message->close_sent || message->close_received)
        return websocket_message_error(message, 1002);
    if (opcode == 0U) {
        if (!message->active) return websocket_message_error(message, 1002);
    } else {
        if (message->active) return websocket_message_error(message, 1002);
        message->opcode = opcode;
        message->used = 0;
        message->started_us = now_us;
    }
    if (size > message->capacity - 1U - message->used)
        return websocket_message_error(message, 1009);
    if (size) memmove(message->buffer + message->used, payload, size);
    message->used += size;
    message->buffer[message->used] = 0;
    // Reject an irreparable prefix immediately; an incomplete final codepoint
    // may cross fragment boundaries, but overlong/surrogate/range errors may not.
    if (message->opcode == 1U &&
        !websocket_message_utf8_check(message->buffer, message->used, final))
        return websocket_message_error(message, 1007);
    if (!final) {
        message->active = true;
        return (websocket_message_result_t){.event = WEBSOCKET_MESSAGE_NONE};
    }
    message->active = false;
    result = (websocket_message_result_t){
        .event = message->opcode == 1U ? WEBSOCKET_MESSAGE_TEXT : WEBSOCKET_MESSAGE_BINARY,
        .data = message->buffer, .size = message->used};
    message->used = 0;
    return result;
}
