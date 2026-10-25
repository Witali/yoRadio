#ifndef VORBIS_XIPH_TEST_ALLOC_INJECT_H
#define VORBIS_XIPH_TEST_ALLOC_INJECT_H
#include "vorbis_xiph_alloc.h"
#include <ogg/os_types.h>
#undef _ogg_malloc
#undef _ogg_calloc
#undef _ogg_realloc
#undef _ogg_free
#define _ogg_malloc xiph_port_test_malloc
#define _ogg_calloc xiph_port_test_calloc
#define _ogg_realloc xiph_port_test_realloc
#define _ogg_free xiph_port_test_free
#endif
