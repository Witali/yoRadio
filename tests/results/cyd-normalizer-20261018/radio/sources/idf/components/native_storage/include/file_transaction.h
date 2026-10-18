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
