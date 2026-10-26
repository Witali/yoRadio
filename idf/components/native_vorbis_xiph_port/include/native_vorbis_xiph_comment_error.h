/* Private error-reporting variants; the public void API is preserved.
   On refusal, existing comment state and borrowed value pointers stay intact.
   These are failure-atomic operations, not concurrent-mutator synchronization. */
#ifndef NATIVE_VORBIS_XIPH_COMMENT_ERROR_H
#define NATIVE_VORBIS_XIPH_COMMENT_ERROR_H
#include "vorbis/codec.h"
int native_xiph_comment_add(vorbis_comment *,const char *);
int native_xiph_comment_add_tag(vorbis_comment *,const char *,const char *);
#endif
