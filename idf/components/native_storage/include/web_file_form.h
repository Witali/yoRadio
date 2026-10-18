#pragma once

// Bounded streaming file form. Storage callbacks keep platform IO outside the
// parser so the exact receiver can be tested with arbitrary network splits.
#include "web_multipart.h"

#define WEB_FILE_FORM_MAX_FILES 16U
// SPIFFS stores complete object names (including /www/) in this bound.
// Match its configured limit; a larger form manifest wastes HTTP stack RAM.
#ifdef CONFIG_SPIFFS_OBJ_NAME_LEN
#define WEB_FILE_FORM_NAME_BYTES CONFIG_SPIFFS_OBJ_NAME_LEN
#else
#define WEB_FILE_FORM_NAME_BYTES 32U
#endif
#define WEB_FILE_FORM_WIFI_BYTES 800U

typedef enum { WEB_FORM_UPLOAD, WEB_FORM_BOARD, WEB_FORM_CREDENTIALS } web_form_mode_t;
typedef enum { WEB_PART_IGNORE, WEB_PART_FILE, WEB_PART_WIFI,
               WEB_PART_SSID, WEB_PART_PASSWORD } web_form_part_t;
typedef struct {
    bool (*begin)(unsigned slot, void *context);
    bool (*write)(const uint8_t *data, size_t size, void *context);
    bool (*end)(void *context);
    void *context;
} web_form_sink_t;
typedef struct {
    web_form_mode_t mode;
    web_form_part_t part;
    web_form_sink_t sink;
    unsigned files;
    char names[WEB_FILE_FORM_MAX_FILES][WEB_FILE_FORM_NAME_BYTES];
    bool playlist[WEB_FILE_FORM_MAX_FILES];
    size_t part_bytes;
    size_t wifi_bytes;
    bool wifi_seen, ssid_seen, password_seen, playlist_seen;
    char wifi[WEB_FILE_FORM_WIFI_BYTES];
    char ssid[33], password[65];
} web_file_form_t;

static inline bool web_form_name(const char *filename, char *out, size_t cap) {
    const char *base = filename;
    for (const char *p = filename; *p; ++p)
        if (*p == '/' || *p == '\\') base = p + 1;
    size_t n = strlen(base);
    if (!n || n >= cap || strstr(base, "..")) return false;
    for (size_t i = 0; i < n; ++i) {
        unsigned char c = (unsigned char)base[i];
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '-'))
            return false;
    }
    memcpy(out, base, n + 1);
    return true;
}

static inline bool web_file_form_part(mp_event_t event, const uint8_t *data,
                                      size_t length, void *context) {
    web_file_form_t *u = context;
    if (event == MP_BEGIN) {
        char field[32], filename[128] = "", name[WEB_FILE_FORM_NAME_BYTES];
        bool have_name = false;
        if (!mp_disposition((const char *)data, field, sizeof(field), filename,
                            sizeof(filename), &have_name))
            return false;
        u->part_bytes = 0;
        u->part = WEB_PART_IGNORE;
        if (!strcmp(field, "submit")) return true;
        if (u->mode == WEB_FORM_CREDENTIALS) {
            if (!strcmp(field, "ssid") && !u->ssid_seen) {
                u->ssid_seen = true; u->part = WEB_PART_SSID;
            } else if (!strcmp(field, "pass") && !u->password_seen) {
                u->password_seen = true; u->part = WEB_PART_PASSWORD;
            } else return false;
            return true;
        }
        bool is_playlist = !strcmp(field, "plfile");
        bool is_wifi = !strcmp(field, "wifile");
        if (u->mode == WEB_FORM_BOARD) {
            if (strcmp(field, "www") && strcmp(field, "data")) return false;
            if (!have_name) return false;
            if (!filename[0]) return true; // Unselected optional file input.
            if (!web_form_name(filename, name, sizeof(name))) return false;
            is_playlist = !strcmp(field, "data") && !strcmp(name, "playlist.csv");
            is_wifi = !strcmp(field, "data") && !strcmp(name, "wifi.csv");
            if (!is_playlist && !is_wifi) {
                size_t n = strlen(name);
                if (strcmp(field, "www") || n <= 3 || strcmp(name + n - 3, ".gz"))
                    return false;
            }
        } else {
            if ((!is_playlist && !is_wifi) || u->files || u->wifi_seen) return false;
            if (!web_form_name(is_playlist ? "playlist.csv" : "wifi.csv", name, sizeof(name))) return false;
        }
        if (is_wifi) {
            if (u->wifi_seen) return false;
            u->wifi_seen = true; u->part = WEB_PART_WIFI;
            return true;
        }
        if (u->files == WEB_FILE_FORM_MAX_FILES || (is_playlist && u->playlist_seen))
            return false;
        for (unsigned i = 0; i < u->files; ++i)
            if (u->playlist[i] == is_playlist && !strcmp(u->names[i], name))
                return false;
        size_t name_bytes = strlen(name) + 1U;
        if (name_bytes > sizeof(u->names[u->files])) return false;
        memcpy(u->names[u->files], name, name_bytes);
        u->playlist[u->files] = is_playlist;
        u->playlist_seen |= is_playlist;
        u->part = WEB_PART_FILE;
        return u->sink.begin(u->files, u->sink.context);
    }
    if (u->part == WEB_PART_IGNORE) return true;
    if (event == MP_END) {
        if (u->part == WEB_PART_FILE) {
            if (!u->part_bytes || !u->sink.end(u->sink.context)) return false;
            ++u->files;
        } else if (u->part == WEB_PART_WIFI) {
            if (!u->part_bytes) return false;
            u->wifi_bytes = u->part_bytes;
        }
        return true;
    }
    if (u->part == WEB_PART_FILE) {
        if (!u->sink.write(data, length, u->sink.context)) return false;
    } else {
        char *out = u->part == WEB_PART_WIFI ? u->wifi :
                    u->part == WEB_PART_SSID ? u->ssid : u->password;
        size_t cap = u->part == WEB_PART_WIFI ? sizeof(u->wifi) :
                     u->part == WEB_PART_SSID ? sizeof(u->ssid) : sizeof(u->password);
        if (length >= cap - u->part_bytes || memchr(data, 0, length)) return false;
        if (u->part != WEB_PART_WIFI &&
            (memchr(data, '\t', length) || memchr(data, '\r', length) ||
             memchr(data, '\n', length))) return false;
        memcpy(out + u->part_bytes, data, length);
        out[u->part_bytes + length] = 0;
    }
    u->part_bytes += length;
    return true;
}
