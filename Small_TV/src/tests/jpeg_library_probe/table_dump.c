/* Inspect real private table pointers using the pinned source's own type layout.
 * The unused copied initializer is renamed; normal decoding calls the library's
 * initializer.  This inspection object is never part of the RV32 codec build. */
#define BITS_IN_JSAMPLE 12
#define j12init_color_deconverter jpeg_probe_unused_color_init12
#include "jdcolor.c"
#include "table_dump.h"

int jpeg_probe_dump_tables12(j_decompress_ptr codec, FILE *range, FILE *color)
{
    /* Export every actual C-initialized value, including unused mask segments,
     * so generated constants are checked against upstream, not a second copy
     * of the Python generator's formula.  Lossless passthrough has no tables. */
    if (codec->data_precision != 12 || codec->master->lossless ||
        codec->jpeg_color_space != JCS_YCbCr || codec->out_color_space != JCS_RGB ||
        !codec->sample_range_limit || !codec->cconvert) return 0;
    my_cconvert_ptr conversion = (my_cconvert_ptr)codec->cconvert;
    if (!conversion->Cr_r_tab || !conversion->Cb_b_tab ||
        !conversion->Cr_g_tab || !conversion->Cb_g_tab) return 0;
    const J12SAMPLE *base = (const J12SAMPLE *)codec->sample_range_limit - 4096;
    return fwrite(base, sizeof(*base), 22528, range) == 22528 &&
           fwrite(conversion->Cr_r_tab, sizeof(int), 4096, color) == 4096 &&
           fwrite(conversion->Cb_b_tab, sizeof(int), 4096, color) == 4096 &&
           fwrite(conversion->Cr_g_tab, sizeof(JLONG), 4096, color) == 4096 &&
           fwrite(conversion->Cb_g_tab, sizeof(JLONG), 4096, color) == 4096;
}
