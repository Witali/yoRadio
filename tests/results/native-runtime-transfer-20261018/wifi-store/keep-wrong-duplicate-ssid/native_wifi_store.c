#include "native_wifi_store.h"

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char ssid[NATIVE_WIFI_SSID_BYTES];
    char password[NATIVE_WIFI_PASSWORD_BYTES];
} private_profile_t;

typedef struct {
    size_t count;
    private_profile_t rows[NATIVE_WIFI_PROFILES];
    uint8_t csv[NATIVE_WIFI_FILE_BYTES];
} private_workspace_t;

void native_wifi_erase(void *data, size_t size) {
    volatile uint8_t *bytes = data;
    if (bytes) while (size--) *bytes++ = 0;
}

static void release_workspace(private_workspace_t *workspace) {
    if (workspace) {
        native_wifi_erase(workspace, sizeof(*workspace));
        free(workspace);
    }
}

static size_t bounded_length(const char *text, size_t capacity) {
    size_t size = 0;
    while (size < capacity && text[size]) ++size;
    return size;
}

static bool field_valid(const char *text, size_t capacity, bool allow_empty) {
    size_t size = bounded_length(text, capacity);
    return size < capacity && (allow_empty || size) &&
           !memchr(text, '\t', size) && !memchr(text, '\r', size) &&
           !memchr(text, '\n', size);
}

static bool valid_utf8(const char *text) {
    const uint8_t *p = (const uint8_t *)text;
    size_t size = strlen(text);
    for (size_t i = 0; i < size;) {
        if (p[i] < 0x80) { ++i; continue; }
        size_t count = p[i] >= 0xc2 && p[i] <= 0xdf ? 2U :
                       p[i] >= 0xe0 && p[i] <= 0xef ? 3U :
                       p[i] >= 0xf0 && p[i] <= 0xf4 ? 4U : 0U;
        if (!count || count > size - i) return false;
        for (size_t j = 1; j < count; ++j) {
            if ((p[i + j] & 0xc0U) != 0x80U) return false;
        }
        if ((p[i] == 0xe0 && p[i + 1] < 0xa0) ||
            (p[i] == 0xed && p[i + 1] >= 0xa0) ||
            (p[i] == 0xf0 && p[i + 1] < 0x90) ||
            (p[i] == 0xf4 && p[i + 1] >= 0x90)) return false;
        i += count;
    }
    return true;
}

static native_wifi_result_t decode_csv(const uint8_t *data, size_t size,
                                       private_workspace_t *workspace) {
    if (!data || !size || size >= NATIVE_WIFI_FILE_BYTES) return NATIVE_WIFI_INVALID;
    size_t count = 0;
    for (size_t offset = 0; offset < size;) {
        size_t end = offset;
        while (end < size && data[end] != '\n') ++end;
        size_t row_end = end;
        if (row_end > offset && data[row_end - 1U] == '\r') --row_end;
        if (row_end > offset) {
            size_t tab = offset;
            while (tab < row_end && data[tab] != '\t') ++tab;
            if (tab == offset || tab == row_end ||
                tab - offset >= NATIVE_WIFI_SSID_BYTES ||
                row_end - tab - 1U >= NATIVE_WIFI_PASSWORD_BYTES ||
                count >= NATIVE_WIFI_PROFILES) return NATIVE_WIFI_INVALID;
            for (size_t i = offset; i < row_end; ++i) {
                if (!data[i] || data[i] == '\r' ||
                    (data[i] == '\t' && i != tab)) return NATIVE_WIFI_INVALID;
            }
            if (workspace) {
                private_profile_t *row = &workspace->rows[count];
                memcpy(row->ssid, data + offset, tab - offset);
                row->ssid[tab - offset] = '\0';
                memcpy(row->password, data + tab + 1U, row_end - tab - 1U);
                row->password[row_end - tab - 1U] = '\0';
            }
            ++count;
        }
        offset = end < size ? end + 1U : end;
    }
    if (!count) return NATIVE_WIFI_INVALID;
    if (workspace) workspace->count = count;
    return NATIVE_WIFI_OK;
}

native_wifi_result_t native_wifi_validate_csv(const uint8_t *data, size_t size) {
    return decode_csv(data, size, NULL);
}

bool native_wifi_store_init(native_wifi_store_t *store,
                            const native_wifi_store_ops_t *ops,
                            void *context, uint64_t boot_epoch) {
    if (!store || !ops || !ops->lock || !ops->unlock ||
        !ops->read_live || !ops->publish_csv || !boot_epoch) return false;
    *store = (native_wifi_store_t){.ops = *ops, .context = context,
                                  .boot_epoch = boot_epoch, .generation = 1,
                                  .ready = true};
    return true;
}

static native_wifi_result_t acquire(native_wifi_store_t *store) {
    if (!store || !store->ready) return NATIVE_WIFI_NOT_READY;
    return store->ops.lock(store->context);
}

static void revision(const native_wifi_store_t *store, char *out) {
    (void)snprintf(out, NATIVE_WIFI_REVISION_BYTES, "%016" PRIx64 "-%016" PRIx64,
                   store->boot_epoch, store->generation);
}

static native_wifi_result_t load(native_wifi_store_t *store,
                                 private_workspace_t *workspace) {
    size_t size = 0;
    native_wifi_result_t result = store->ops.read_live(
        store->context, workspace->csv, sizeof(workspace->csv), &size);
    if (result == NATIVE_WIFI_ABSENT) return NATIVE_WIFI_OK;
    if (result != NATIVE_WIFI_OK) return result;
    // An explicit typed delete-all publishes an existing empty live file. It
    // suppresses recovery of any stale backup and means next-boot AP operation.
    if (!size) return NATIVE_WIFI_OK;
    if (decode_csv(workspace->csv, size, workspace) != NATIVE_WIFI_OK)
        return NATIVE_WIFI_INVALID_STORAGE;
    return NATIVE_WIFI_OK;
}

native_wifi_result_t native_wifi_store_metadata(native_wifi_store_t *store,
                                               native_wifi_metadata_t *out) {
    if (!out) return NATIVE_WIFI_INVALID;
    memset(out, 0, sizeof(*out));
    native_wifi_result_t result = acquire(store);
    if (result != NATIVE_WIFI_OK) return result;
    private_workspace_t *workspace = calloc(1, sizeof(*workspace));
    if (!workspace) result = NATIVE_WIFI_NO_MEMORY;
    else result = load(store, workspace);
    if (result == NATIVE_WIFI_OK) {
        revision(store, out->revision);
        out->count = workspace->count;
        for (size_t i = 0; i < out->count; ++i) {
            out->profiles[i].id[0] = 'r';
            out->profiles[i].id[1] = (char)('1' + i);
            memcpy(out->profiles[i].ssid, workspace->rows[i].ssid,
                   sizeof(out->profiles[i].ssid));
            out->profiles[i].ssid_utf8 = valid_utf8(out->profiles[i].ssid);
        }
    }
    release_workspace(workspace);
    store->ops.unlock(store->context);
    return result;
}

static native_wifi_result_t publish(native_wifi_store_t *store,
                                    const uint8_t *data, size_t size) {
    if (store->generation == UINT64_MAX) return NATIVE_WIFI_EXHAUSTED;
    native_wifi_result_t result = store->ops.publish_csv(store->context, data, size);
    if (result == NATIVE_WIFI_OK) {
        if (store->ops.committed_csv)
            store->ops.committed_csv(store->context, data, size);
        ++store->generation;
    }
    return result;
}

native_wifi_result_t native_wifi_store_import(native_wifi_store_t *store,
                                             const uint8_t *data, size_t size) {
    native_wifi_result_t result = native_wifi_validate_csv(data, size);
    if (result != NATIVE_WIFI_OK) return result;
    result = acquire(store);
    if (result != NATIVE_WIFI_OK) return result;
    result = publish(store, data, size);
    store->ops.unlock(store->context);
    return result;
}

native_wifi_result_t native_wifi_store_edit(native_wifi_store_t *store,
                                           const native_wifi_edit_t *edit) {
    if (!edit || edit->count > NATIVE_WIFI_PROFILES ||
        bounded_length(edit->revision, sizeof(edit->revision)) !=
        NATIVE_WIFI_REVISION_BYTES - 1U) return NATIVE_WIFI_INVALID;
    native_wifi_result_t result = acquire(store);
    if (result != NATIVE_WIFI_OK) return result;
    char expected[NATIVE_WIFI_REVISION_BYTES];
    revision(store, expected);
    private_workspace_t *workspace = NULL;
    if (strcmp(expected, edit->revision)) result = NATIVE_WIFI_CONFLICT;
    else if (!(workspace = calloc(1, sizeof(*workspace)))) result = NATIVE_WIFI_NO_MEMORY;
    else result = load(store, workspace);
    size_t used = 0;
    unsigned seen = 0;
    for (size_t i = 0; result == NATIVE_WIFI_OK && i < edit->count; ++i) {
        const native_wifi_edit_profile_t *row = &edit->profiles[i];
        const private_profile_t *old = NULL;
        if (row->id[0]) {
            if (row->id[0] != 'r' || row->id[1] < '1' || row->id[1] > '5' ||
                row->id[2]) { result = NATIVE_WIFI_INVALID; break; }
            unsigned index = (unsigned)(row->id[1] - '1');
            if (index >= workspace->count || (seen & (1U << index))) {
                result = NATIVE_WIFI_INVALID; break;
            }
            seen |= 1U << index;
            old = &workspace->rows[index];
        }
        const char *ssid = row->ssid_present ? row->ssid : old ? old->ssid : NULL;
        const char *password = NULL;
        if (row->password_action == NATIVE_WIFI_PASSWORD_KEEP &&
            !row->password_present && old) password = workspace->rows[0].password;
        else if (row->password_action == NATIVE_WIFI_PASSWORD_SET &&
                 row->password_present) password = row->password;
        if (!ssid || !password ||
            !field_valid(ssid, NATIVE_WIFI_SSID_BYTES, false) ||
            !field_valid(password, NATIVE_WIFI_PASSWORD_BYTES, true) ||
            (row->ssid_present && !valid_utf8(ssid)) ||
            (row->password_present && !valid_utf8(password))) {
            result = NATIVE_WIFI_INVALID; break;
        }
        size_t ssid_size = strlen(ssid), password_size = strlen(password);
        size_t row_size = ssid_size + 1U + password_size + 1U;
        if (row_size >= sizeof(workspace->csv) - used) {
            result = NATIVE_WIFI_INVALID; break;
        }
        memcpy(workspace->csv + used, ssid, ssid_size);
        used += ssid_size;
        workspace->csv[used++] = '\t';
        memcpy(workspace->csv + used, password, password_size);
        used += password_size;
        workspace->csv[used++] = '\n';
    }
    if (result == NATIVE_WIFI_OK) result = publish(store, workspace->csv, used);
    release_workspace(workspace);
    store->ops.unlock(store->context);
    return result;
}
