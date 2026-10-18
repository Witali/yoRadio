#include "native_wifi_json.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned groups;
static const char *revision = "0123456789abcdef-0000000000000001";

static native_wifi_edit_t decode(const char *text) {
    native_wifi_edit_t edit;
    assert(native_wifi_json_decode((const uint8_t *)text, strlen(text), &edit) == NATIVE_WIFI_OK);
    ++groups; return edit;
}
static void invalid_bytes(const uint8_t *text, size_t size) {
    native_wifi_edit_t edit; memset(&edit, 0xa5, sizeof(edit));
    assert(native_wifi_json_decode(text, size, &edit) == NATIVE_WIFI_INVALID);
    const uint8_t *bytes = (const uint8_t *)&edit;
    for (size_t i = 0; i < sizeof(edit); ++i) assert(!bytes[i]);
    ++groups;
}
static void invalid(const char *text) { invalid_bytes((const uint8_t *)text, strlen(text)); }
static void wrapped(const char *row, bool valid) {
    char body[4097];
    int size = snprintf(body, sizeof(body), "{\"revision\":\"%s\",\"profiles\":[%s]}", revision, row);
    assert(size > 0 && (size_t)size < sizeof(body));
    if (valid) (void)decode(body); else invalid(body);
}

static void syntax_cases(void) {
    const char *good = " { \"profiles\" : [ {\"password_action\":\"keep\",\"id\":\"r1\"} ], \"revision\" : \"0123456789abcdef-0000000000000001\" } \r\n";
    native_wifi_edit_t edit = decode(good);
    assert(edit.count == 1 && !strcmp(edit.revision, revision) && !strcmp(edit.profiles[0].id, "r1"));
    assert(!edit.profiles[0].ssid_present && !edit.profiles[0].password_present);
    wrapped("", true); // Explicit delete-all.
    wrapped("{\"ssid\":\" new \",\"password_action\":\"set\",\"password\":\"\"}", true);
    wrapped("{\"id\":\"r2\",\"ssid\":\"renamed\",\"password_action\":\"keep\"}", true);
    wrapped("{\"id\":\"r5\",\"password_action\":\"set\",\"password\":\"********\"}", true);
    const char *bad[] = {
        "{}", "[]", "null", "", "{\"revision\":1,\"profiles\":[]}",
        "{\"revision\":\"0123456789abcdef-0000000000000001\",\"profiles\":null}",
        "{\"revision\":\"0123456789abcdef-0000000000000001\"}",
        "{\"profiles\":[]}", "{\"revision\":\"short\",\"profiles\":[]}",
        "{\"revision\":\"0123456789abcdeg-0000000000000001\",\"profiles\":[]}",
        "{\"revision\":\"0123456789abcdef_0000000000000001\",\"profiles\":[]}",
        "{\"revision\":\"0123456789abcdef-0000000000000001\",\"profiles\":[],\"profiles\":[]}",
        "{\"revision\":\"0123456789abcdef-0000000000000001\",\"profiles\":[],\"revisi\\u006fn\":\"0123456789abcdef-0000000000000001\"}",
        "{\"revision\":\"0123456789abcdef-0000000000000001\",\"profiles\":[],\"unknown\":0}",
        "{\"revision\":\"0123456789abcdef-0000000000000001\",\"profiles\":[],}",
        "{\"revision\":\"0123456789abcdef-0000000000000001\",\"profiles\":[]}x",
    };
    for (size_t i = 0; i < sizeof(bad)/sizeof(*bad); ++i) invalid(bad[i]);
    const char *rows[] = {
        "{}", "null", "[]", "{\"id\":\"r1\"}", "{\"password_action\":\"keep\"}",
        "{\"id\":\"r1\",\"password_action\":\"keep\",\"password\":\"\"}",
        "{\"id\":\"r1\",\"password_action\":\"set\"}",
        "{\"password_action\":\"set\",\"password\":\"p\"}",
        "{\"ssid\":\"\",\"password_action\":\"set\",\"password\":\"p\"}",
        "{\"ssid\":\"s\",\"password_action\":\"other\",\"password\":\"p\"}",
        "{\"ssid\":\"s\",\"password_action\":\"set\",\"password\":false}",
        "{\"ssid\":\"s\",\"password_action\":\"set\",\"password\":\"p\",\"extra\":1}",
        "{\"ssid\":\"s\",\"password_action\":\"set\",\"password\":\"p\",\"pass\\u0077ord\":\"q\"}",
        "{\"ssid\":\"s\",\"ssid\":\"x\",\"password_action\":\"set\",\"password\":\"p\"}",
        "{\"id\":\"r1\",\"id\":\"r2\",\"password_action\":\"keep\"}",
        "{\"id\":\"r1\",\"password_action\":\"keep\",\"password_action\":\"set\"}",
        "{\"id\":1,\"password_action\":\"keep\"}",
        "{\"id\":\"\",\"password_action\":\"keep\"}",
        "{\"id\":\"r0\",\"password_action\":\"keep\"}",
        "{\"id\":\"r6\",\"password_action\":\"keep\"}",
        "{\"id\":\"r1x\",\"password_action\":\"keep\"}",
        "{\"ssid\":\"s\",\"password_action\":\"set\",\"password\":\"canary\",}",
    };
    for (size_t i = 0; i < sizeof(rows)/sizeof(*rows); ++i) wrapped(rows[i], false);
    for (size_t i = 0; i + 3 < strlen(good); ++i) invalid_bytes((const uint8_t *)good, i);
    const char *unicode = "{\"revision\":\"0123456789abcdef-0000000000000001\",\"profiles\":[{\"ssid\":\"\\u00e9\\ud83d\\ude00\",\"password_action\":\"set\",\"password\":\"a\\\\b\\\"c\\/d\"}]}";
    edit = decode(unicode);
    assert(!strcmp(edit.profiles[0].ssid, "\xc3\xa9\xf0\x9f\x98\x80"));
    assert(!strcmp(edit.profiles[0].password, "a\\b\"c/d"));
    const char *escapes[] = {"\\u0000", "\\ud800", "\\udc00", "\\ud800\\u0041", "\\uXXff", "\\q", "\xff", "\xc0\x80", "\xed\xa0\x80", "\xf4\x90\x80\x80", "\xe2\x82"};
    for (size_t i = 0; i < sizeof(escapes)/sizeof(*escapes); ++i) {
        char row[256]; (void)snprintf(row, sizeof(row), "{\"ssid\":\"s\",\"password_action\":\"set\",\"password\":\"%s\"}", escapes[i]);
        wrapped(row, false);
    }
    uint8_t nul[] = {'{',0,'}'}; invalid_bytes(nul, sizeof(nul));
}
static void bounds_cases(void) {
    char row[2048], ssid[220], password[450];
    for (size_t s = 1; s <= 32; ++s) {
        for (size_t p = 0; p <= 64; ++p) {
            memset(ssid, 's', s); ssid[s] = 0;
            memset(password, 'p', p); password[p] = 0;
            (void)snprintf(row, sizeof(row), "{\"ssid\":\"%s\",\"password_action\":\"set\",\"password\":\"%s\"}", ssid, password);
            wrapped(row, s < 32 && p < 64);
        }
    }
    for (size_t n = 1; n <= 16; ++n) {
        ssid[0] = 0;
        for (size_t i = 0; i < n; ++i) strcat(ssid, "\\u00e9");
        (void)snprintf(row, sizeof(row), "{\"ssid\":\"%s\",\"password_action\":\"set\",\"password\":\"\"}", ssid);
        wrapped(row, n * 2 < 32);
    }
    char rows[1024] = "";
    for (unsigned i = 1; i <= 6; ++i) {
        if (i > 1) strcat(rows, ",");
        strcat(rows, "{\"ssid\":\"s\",\"password_action\":\"set\",\"password\":\"p\"}");
        wrapped(rows, i <= 5);
    }
    char body[4097]; memset(body, ' ', sizeof(body));
    int size = snprintf(body, sizeof(body), "{\"revision\":\"%s\",\"profiles\":[]}", revision);
    body[size] = ' ';
    native_wifi_edit_t edit;
    assert(native_wifi_json_decode((const uint8_t *)body, 4096, &edit) == NATIVE_WIFI_OK); ++groups;
    invalid_bytes((const uint8_t *)body, 4097);
}
static void metadata_cases(void) {
    native_wifi_metadata_t meta = {.count=2}; strcpy(meta.revision, revision);
    strcpy(meta.profiles[0].id, "r1"); strcpy(meta.profiles[0].ssid, " quotes\"\\\t\n "); meta.profiles[0].ssid_utf8 = true;
    strcpy(meta.profiles[1].id, "r2"); meta.profiles[1].ssid[0] = (char)0xff;
    char body[2048]; size_t size;
    assert(native_wifi_json_metadata(&meta, body, sizeof(body), &size));
    assert(size == strlen(body) && strstr(body, "\\ufffd") && strstr(body, "\"ssid_utf8\":false"));
    assert(strstr(body, "quotes\\\"\\\\\\u0009\\u000a") && !strstr(body, "password")); ++groups;
    size_t complete = size;
    for (size_t capacity = 1; capacity <= complete + 1; ++capacity) {
        memset(body, 0xa5, sizeof(body));
        bool result = native_wifi_json_metadata(&meta, body, capacity, &size);
        assert(result == (capacity > complete));
        if (!result) assert(!body[0] && !size);
        assert((uint8_t)body[capacity] == 0xa5); ++groups;
    }
    for (size_t n = 0; n < 4; ++n) {
        memset(meta.profiles[1].ssid, 0, sizeof(meta.profiles[1].ssid));
        meta.profiles[1].ssid[30 - n] = (char)0xf0;
        memset(meta.profiles[1].ssid, 's', 30 - n);
        assert(native_wifi_json_metadata(&meta, body, sizeof(body), &size)); ++groups;
    }
    memset(meta.profiles[1].ssid, 's', sizeof(meta.profiles[1].ssid));
    assert(!native_wifi_json_metadata(&meta, body, sizeof(body), &size) && !size && !body[0]); ++groups;
}
static void fuzz_cases(void) {
    uint8_t body[4096]; uint32_t random = 0x6ff00123;
    for (unsigned iteration = 0; iteration < 20000; ++iteration) {
        random = random * 1664525U + 1013904223U;
        size_t size = random % sizeof(body);
        for (size_t i = 0; i < size; ++i) {
            random = random * 1664525U + 1013904223U;
            body[i] = (uint8_t)(random >> 24);
        }
        native_wifi_edit_t edit;
        assert(native_wifi_json_decode(body, size, &edit) == NATIVE_WIFI_INVALID);
    }
}
int main(void) {
    syntax_cases(); bounds_cases(); metadata_cases(); fuzz_cases();
    printf("%u JSON groups passed; 20000 deterministic malformed-input probes\n", groups);
    return 0;
}
