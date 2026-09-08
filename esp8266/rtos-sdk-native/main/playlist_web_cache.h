#pragma once
#include <stddef.h>
#include "sdkconfig.h"

#if CONFIG_YORADIO_PLAYLIST_WEB_GZIP
/* Called under the playlist service lock, before HTTP starts or while its
 * upload handler owns the request. A cache failure never invalidates CSV. */
void playlist_web_cache_invalidate(void);
void playlist_web_cache_refresh(void);
/* Return a read-only descriptor positioned at gzip data, or -1 for fallback.
 * Only the HTTP task opens it; callers close it after bounded streaming. */
int playlist_web_cache_open(size_t *length);
#else
static inline void playlist_web_cache_invalidate(void) {}
static inline void playlist_web_cache_refresh(void) {}
static inline int playlist_web_cache_open(size_t *length) { (void)length; return -1; }
#endif
