/* Link-only reachability probe, not a bootable program or a firmware backend. */
#include <stdio.h>
#include "jpeglib.h"

int jpeg_footprint_entry(j_decompress_ptr codec, struct jpeg_error_mgr *error,
                         const unsigned char *input, unsigned long length,
                         void *row)
{
    /* Retain all ordinary JPEG decode precisions and normal header/finish/error
     * paths for a realistic codec size measurement.  The default error manager
     * is deliberately included; no fake libc/allocator stubs shrink the result.
     * This function is never run: memory source, error handling, output buffer
     * sizing and storage still require the actual Small TV adapter. */
    int result = 0;
    codec->err = jpeg_std_error(error);
    jpeg_create_decompress(codec);
    jpeg_mem_src(codec, input, length);
    if (jpeg_read_header(codec, TRUE) != JPEG_HEADER_OK ||
        !codec->image_width || !codec->image_height ||
        codec->image_width > 240 || codec->image_height > 240)
        goto done;
    codec->do_block_smoothing = FALSE;
    codec->out_color_space = codec->num_components == 4 ? JCS_CMYK :
        codec->num_components == 1 ? JCS_GRAYSCALE : JCS_RGB;
    if (!jpeg_start_decompress(codec)) goto done;
    while (codec->output_scanline < codec->output_height) {
        JDIMENSION count;
        if (codec->data_precision <= 8) {
            JSAMPROW samples = row;
            count = jpeg_read_scanlines(codec, &samples, 1);
        } else if (codec->data_precision <= 12) {
            J12SAMPROW samples = row;
            count = jpeg12_read_scanlines(codec, &samples, 1);
        } else {
            J16SAMPROW samples = row;
            count = jpeg16_read_scanlines(codec, &samples, 1);
        }
        if (count != 1) goto done;
    }
    result = jpeg_finish_decompress(codec) ? 1 : 0;
done:
    jpeg_destroy_decompress(codec);
    return result;
}
