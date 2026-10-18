#pragma once
#include <stdbool.h>

// Caller serializes readers/writers and supplies distinct names on one volume.
// The temporary file must already be validated, flushed and closed. Filesystem
// rename durability is platform-specific; no multi-file atomicity is promised.
// Recovery restores a retained backup only when the live name is absent.
bool native_file_recover(const char *live, const char *backup);
// Never unlink the live file before retaining its previous contents. On error
// preserve the temporary file and any backup needed for a later recovery.
bool native_file_replace(const char *temporary, const char *live, const char *backup);

// Retain both previous files until both replacements are installed. Ordinary
// failures restore the old files; failed rollback retains their backups.
// Six distinct names and caller serialization are required. This is not a
// power-loss atomic pair: consumers must validate cross-file metadata at boot.
bool native_file_replace_pair(const char *temporary_a, const char *live_a,
                              const char *backup_a, const char *temporary_b,
                              const char *live_b, const char *backup_b);
