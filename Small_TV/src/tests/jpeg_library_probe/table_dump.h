/* Host-only inspection of the pinned library's actual initialized 12-bit tables. */
#ifndef SMALL_TV_JPEG_TABLE_DUMP_H
#define SMALL_TV_JPEG_TABLE_DUMP_H
#include <stdio.h>
#include "jpeglib.h"
int jpeg_probe_dump_tables12(j_decompress_ptr codec, FILE *range, FILE *color);
#endif
