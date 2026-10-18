#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define NATIVE_WIFI_PROFILES 5U
#define NATIVE_WIFI_SSID_BYTES 32U
#define NATIVE_WIFI_PASSWORD_BYTES 64U
#define NATIVE_WIFI_FILE_BYTES 800U /* exclusive maximum, including legacy CSV */
#define NATIVE_WIFI_BODY_BYTES 4096U
#define NATIVE_WIFI_REVISION_BYTES 34U
#define NATIVE_WIFI_ID_BYTES 3U

typedef enum {
    NATIVE_WIFI_OK,
    NATIVE_WIFI_ABSENT,
    NATIVE_WIFI_INVALID,
    NATIVE_WIFI_INVALID_STORAGE,
    NATIVE_WIFI_CONFLICT,
    NATIVE_WIFI_BUSY,
    NATIVE_WIFI_IO,
    NATIVE_WIFI_NO_MEMORY,
    NATIVE_WIFI_NOT_READY,
    NATIVE_WIFI_EXHAUSTED,
} native_wifi_result_t;

typedef struct {
    char id[NATIVE_WIFI_ID_BYTES];
    char ssid[NATIVE_WIFI_SSID_BYTES];
    // False means a JSON presentation must replace invalid bytes for display.
    // An unchanged editor MUST omit SSID, preserving the stored bytes exactly.
    bool ssid_utf8;
} native_wifi_profile_metadata_t;

typedef struct {
    char revision[NATIVE_WIFI_REVISION_BYTES];
    size_t count;
    native_wifi_profile_metadata_t profiles[NATIVE_WIFI_PROFILES];
} native_wifi_metadata_t;

typedef enum {
    NATIVE_WIFI_PASSWORD_KEEP,
    NATIVE_WIFI_PASSWORD_SET,
} native_wifi_password_action_t;

// Contains only request-supplied values, never a saved password. Empty id marks
// a new row. An existing row may omit SSID; a new row must supply it. For KEEP,
// password_present must be false. SET requires it, including explicit "" (open).
typedef struct {
    char id[NATIVE_WIFI_ID_BYTES];
    bool ssid_present;
    char ssid[NATIVE_WIFI_SSID_BYTES];
    native_wifi_password_action_t password_action;
    bool password_present;
    char password[NATIVE_WIFI_PASSWORD_BYTES];
} native_wifi_edit_profile_t;

typedef struct {
    char revision[NATIVE_WIFI_REVISION_BYTES];
    size_t count;
    native_wifi_edit_profile_t profiles[NATIVE_WIFI_PROFILES];
} native_wifi_edit_t;

typedef struct {
    // All callbacks run while this owner lock is held, except lock/unlock.
    // The owner must bound lock acquisition; no recursive store calls allowed.
    native_wifi_result_t (*lock)(void *context);
    void (*unlock)(void *context);
    // Reads the COMPLETE private live file. ABSENT is only a missing live file;
    // IO/corruption must never masquerade as an empty profile set. Reject >=800
    // bytes, even if the caller's bounded buffer could hold a truncated prefix.
    native_wifi_result_t (*read_live)(void *context, uint8_t *data,
                                      size_t capacity, size_t *size);
    // Atomically publish validated CSV, retaining prior live data on ordinary
    // failure. Flush+close the temporary before existing file_transaction rename.
    native_wifi_result_t (*publish_csv)(void *context, const uint8_t *data,
                                        size_t size);
    // Optional infallible RAM publication after durable CSV publication. Copy
    // synchronously; no pointer retention, SDK I/O, allocation or failure path.
    void (*committed_csv)(void *context, const uint8_t *data, size_t size);
} native_wifi_store_ops_t;

// Non-secret owner state only. Initialize once before exposing tasks; afterward
// callbacks serialize every snapshot, typed edit and legacy import. No old-key
// getter exists. Private temporary workspaces are bounded and erased on release.
typedef struct {
    native_wifi_store_ops_t ops;
    void *context;
    uint64_t boot_epoch, generation;
    bool ready;
} native_wifi_store_t;

bool native_wifi_store_init(native_wifi_store_t *store,
                            const native_wifi_store_ops_t *ops,
                            void *context, uint64_t boot_epoch);
native_wifi_result_t native_wifi_validate_csv(const uint8_t *data, size_t size);
// Clears the complete output at entry, including NOT_READY/BUSY/IO/invalid-store
// failure. Only OK provides a coherent usable revision and metadata snapshot.
native_wifi_result_t native_wifi_store_metadata(native_wifi_store_t *store,
                                               native_wifi_metadata_t *out);
native_wifi_result_t native_wifi_store_edit(native_wifi_store_t *store,
                                           const native_wifi_edit_t *edit);
// An explicit zero-row edit publishes an EMPTY live file: next boot has no
// profiles and recovery must not resurrect an old backup. CSV import below
// deliberately retains the legacy rejection of empty input.
// Explicit full replacement; does not resolve KEEP markers. Can repair invalid
// old storage. Must be used by ALL single-credential and CSV import write paths.
native_wifi_result_t native_wifi_store_import(native_wifi_store_t *store,
                                             const uint8_t *data, size_t size);
// Erase caller-owned newly entered passwords/JSON bodies after request cleanup.
void native_wifi_erase(void *data, size_t size);

#ifdef __cplusplus
}
#endif
