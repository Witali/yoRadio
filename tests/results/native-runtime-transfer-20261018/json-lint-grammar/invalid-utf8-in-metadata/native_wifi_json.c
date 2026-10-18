#include "native_wifi_json.h"

#include <string.h>

typedef struct {
    const uint8_t *at, *end;
} reader_t;

typedef struct {
    char *data;
    size_t capacity, used;
    bool failed;
} writer_t;

static size_t utf8_count(const uint8_t *p, size_t size) {
    if (!size) return 0;
    if (p[0] < 0x80) return 1;
    size_t count = p[0] >= 0xc2 && p[0] <= 0xdf ? 2U :
                   p[0] >= 0xe0 && p[0] <= 0xef ? 3U :
                   p[0] >= 0xf0 && p[0] <= 0xf4 ? 4U : 0U;
    if (!count || count > size) return 0;
    for (size_t i = 1; i < count; ++i)
        if ((p[i] & 0xc0U) != 0x80U) return 0;
    if ((p[0] == 0xe0 && p[1] < 0xa0) || (p[0] == 0xed && p[1] >= 0xa0) ||
        (p[0] == 0xf0 && p[1] < 0x90) || (p[0] == 0xf4 && p[1] >= 0x90)) return 0;
    return count;
}

static void whitespace(reader_t *in) {
    while (in->at < in->end && (*in->at == ' ' || *in->at == '\t' ||
           *in->at == '\r' || *in->at == '\n')) ++in->at;
}

static bool consume(reader_t *in, uint8_t expected) {
    whitespace(in);
    if (in->at == in->end || *in->at != expected) return false;
    ++in->at;
    return true;
}

static bool hex4(reader_t *in, uint32_t *value) {
    if ((size_t)(in->end - in->at) < 4) return false;
    uint32_t result = 0;
    for (unsigned i = 0; i < 4; ++i) {
        uint8_t c = *in->at++;
        unsigned digit = c >= '0' && c <= '9' ? (unsigned)(c - '0') :
                         c >= 'a' && c <= 'f' ? (unsigned)(c - 'a') + 10U :
                         c >= 'A' && c <= 'F' ? (unsigned)(c - 'A') + 10U : 16U;
        if (digit == 16) return false;
        result = result * 16U + digit;
    }
    *value = result;
    return true;
}

static bool append(char *out, size_t capacity, size_t *used,
                    const uint8_t *data, size_t size) {
    if (*used >= capacity || size >= capacity - *used) return false;
    memcpy(out + *used, data, size);
    *used += size;
    out[*used] = '\0';
    return true;
}

static bool string(reader_t *in, char *out, size_t capacity) {
    if (!consume(in, '"') || !capacity) return false;
    size_t used = 0;
    out[0] = '\0';
    while (in->at < in->end) {
        uint8_t c = *in->at++;
        if (c == '"') return true;
        if (c < 0x20) return false;
        if (c == '\\') {
            if (in->at == in->end) return false;
            c = *in->at++;
            switch (c) {
            case '"': case '\\': case '/': break;
            case 'b': c = '\b'; break;
            case 'f': c = '\f'; break;
            case 'n': c = '\n'; break;
            case 'r': c = '\r'; break;
            case 't': c = '\t'; break;
            case 'u': {
                uint32_t point;
                if (!hex4(in, &point) || !point) return false;
                if (point >= 0xd800 && point <= 0xdbff) {
                    if ((size_t)(in->end - in->at) < 6 || in->at[0] != '\\' || in->at[1] != 'u') return false;
                    in->at += 2;
                    uint32_t low;
                    if (!hex4(in, &low) || low < 0xdc00 || low > 0xdfff) return false;
                    point = 0x10000U + ((point - 0xd800U) << 10) + low - 0xdc00U;
                } else if (point >= 0xdc00 && point <= 0xdfff) return false;
                uint8_t bytes[4];
                size_t count;
                if (point < 0x80) { count = 1; bytes[0] = (uint8_t)point; }
                else if (point < 0x800) {
                    count = 2; bytes[0] = (uint8_t)(0xc0U | (point >> 6));
                    bytes[1] = (uint8_t)(0x80U | (point & 0x3fU));
                } else if (point < 0x10000) {
                    count = 3; bytes[0] = (uint8_t)(0xe0U | (point >> 12));
                    bytes[1] = (uint8_t)(0x80U | ((point >> 6) & 0x3fU));
                    bytes[2] = (uint8_t)(0x80U | (point & 0x3fU));
                } else {
                    count = 4; bytes[0] = (uint8_t)(0xf0U | (point >> 18));
                    bytes[1] = (uint8_t)(0x80U | ((point >> 12) & 0x3fU));
                    bytes[2] = (uint8_t)(0x80U | ((point >> 6) & 0x3fU));
                    bytes[3] = (uint8_t)(0x80U | (point & 0x3fU));
                }
                if (!append(out, capacity, &used, bytes, count)) return false;
                continue;
            }
            default: return false;
            }
        } else if (c >= 0x80) {
            --in->at;
            size_t count = utf8_count(in->at, (size_t)(in->end - in->at));
            if (!count || !append(out, capacity, &used, in->at, count)) return false;
            in->at += count;
            continue;
        }
        if (!append(out, capacity, &used, &c, 1)) return false;
    }
    return false;
}

static bool profile(reader_t *in, native_wifi_edit_profile_t *row) {
    if (!consume(in, '{')) return false;
    unsigned fields = 0;
    for (;;) {
        char key[20];
        if (!string(in, key, sizeof(key)) || !consume(in, ':')) return false;
        unsigned bit;
        if (!strcmp(key, "id")) {
            bit = 1U;
            if (fields & bit || !string(in, row->id, sizeof(row->id)) ||
                row->id[0] != 'r' || row->id[1] < '1' || row->id[1] > '5' || row->id[2]) return false;
        } else if (!strcmp(key, "ssid")) {
            bit = 2U; row->ssid_present = true;
            if (fields & bit || !string(in, row->ssid, sizeof(row->ssid)) || !row->ssid[0]) return false;
        } else if (!strcmp(key, "password_action")) {
            bit = 4U; char action[5];
            if (fields & bit || !string(in, action, sizeof(action))) return false;
            if (!strcmp(action, "keep")) row->password_action = NATIVE_WIFI_PASSWORD_KEEP;
            else if (!strcmp(action, "set")) row->password_action = NATIVE_WIFI_PASSWORD_SET;
            else return false;
        } else if (!strcmp(key, "password")) {
            bit = 8U; row->password_present = true;
            if (fields & bit || !string(in, row->password, sizeof(row->password))) return false;
        } else return false;
        fields |= bit;
        whitespace(in);
        if (consume(in, '}')) break;
        if (!consume(in, ',')) return false;
    }
    if (!(fields & 4U) || (!row->id[0] && !row->ssid_present)) return false;
    return row->password_action == NATIVE_WIFI_PASSWORD_KEEP ?
           row->id[0] && !row->password_present : row->password_present;
}

static bool profiles(reader_t *in, native_wifi_edit_t *out) {
    if (!consume(in, '[')) return false;
    if (consume(in, ']')) return true;
    for (;;) {
        if (out->count == NATIVE_WIFI_PROFILES || !profile(in, &out->profiles[out->count])) return false;
        ++out->count;
        if (consume(in, ']')) return true;
        if (!consume(in, ',')) return false;
    }
}

static bool revision_valid(const char *revision) {
    if (strlen(revision) != NATIVE_WIFI_REVISION_BYTES - 1U) return false;
    for (size_t i = 0; i < NATIVE_WIFI_REVISION_BYTES - 1U; ++i) {
        char c = revision[i];
        if (i == 16 ? c != '-' : !((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    }
    return true;
}

native_wifi_result_t native_wifi_json_decode(const uint8_t *body, size_t size,
                                            native_wifi_edit_t *out) {
    if (!out) return NATIVE_WIFI_INVALID;
    memset(out, 0, sizeof(*out));
    if (!body || !size || size > NATIVE_WIFI_BODY_BYTES) return NATIVE_WIFI_INVALID;
    reader_t in = {.at = body, .end = body + size};
    unsigned fields = 0;
    if (!consume(&in, '{')) goto invalid;
    for (;;) {
        char key[10];
        if (!string(&in, key, sizeof(key)) || !consume(&in, ':')) goto invalid;
        unsigned bit;
        if (!strcmp(key, "revision")) {
            bit = 1U;
            if ((fields & bit) || !string(&in, out->revision, sizeof(out->revision)) || !revision_valid(out->revision)) goto invalid;
        } else if (!strcmp(key, "profiles")) {
            bit = 2U;
            if ((fields & bit) || !profiles(&in, out)) goto invalid;
        } else goto invalid;
        fields |= bit;
        if (consume(&in, '}')) break;
        if (!consume(&in, ',')) goto invalid;
    }
    whitespace(&in);
    if (fields == 3U && in.at == in.end) return NATIVE_WIFI_OK;
invalid:
    native_wifi_erase(out, sizeof(*out));
    return NATIVE_WIFI_INVALID;
}

static void bytes(writer_t *out, const char *data, size_t size) {
    if (out->failed) return;
    if (out->used >= out->capacity || size >= out->capacity - out->used) {
        out->failed = true; return;
    }
    memcpy(out->data + out->used, data, size);
    out->used += size; out->data[out->used] = '\0';
}

static void raw(writer_t *out, const char *data) { bytes(out, data, strlen(data)); }

static void quoted(writer_t *out, const char *text, size_t capacity) {
    static const char hex[] = "0123456789abcdef";
    size_t size = 0;
    while (size < capacity && text[size]) ++size;
    if (size == capacity) { out->failed = true; return; }
    raw(out, "\"");
    for (size_t i = 0; i < size && !out->failed;) {
        uint8_t c = (uint8_t)text[i];
        if (c == '"' || c == '\\') {
            const char escaped[] = {'\\', (char)c}; bytes(out, escaped, sizeof(escaped)); ++i;
        } else if (c < 0x20) {
            const char escaped[] = {'\\','u','0','0',hex[c >> 4],hex[c & 15]};
            bytes(out, escaped, sizeof(escaped)); ++i;
        } else {
            size_t count = utf8_count((const uint8_t *)text + i, size - i);
            if (count) { bytes(out, text + i, count); i += count; }
            else { bytes(out, text + i, 1); ++i; }
        }
    }
    raw(out, "\"");
}

bool native_wifi_json_metadata(const native_wifi_metadata_t *metadata,
                               char *out, size_t capacity, size_t *size) {
    if (size) *size = 0;
    if (!metadata || metadata->count > NATIVE_WIFI_PROFILES || !out || !capacity || !size) return false;
    writer_t writer = {.data=out, .capacity=capacity};
    out[0] = '\0';
    raw(&writer, "{\"revision\":");
    quoted(&writer, metadata->revision, sizeof(metadata->revision));
    raw(&writer, ",\"profiles\":[");
    for (size_t i = 0; i < metadata->count; ++i) {
        const native_wifi_profile_metadata_t *row = &metadata->profiles[i];
        if (i) raw(&writer, ",");
        raw(&writer, "{\"id\":"); quoted(&writer, row->id, sizeof(row->id));
        raw(&writer, ",\"ssid\":"); quoted(&writer, row->ssid, sizeof(row->ssid));
        raw(&writer, ",\"ssid_utf8\":"); raw(&writer, row->ssid_utf8 ? "true}" : "false}");
    }
    raw(&writer, "]}");
    if (writer.failed) { out[0] = '\0'; return false; }
    *size = writer.used;
    return true;
}
