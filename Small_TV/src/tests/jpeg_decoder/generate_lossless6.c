/* Synthetic host-only inputs; linked to the unmodified upstream JPEG encoder. */
#include <stdio.h>
#include <stdlib.h>
#include "jpeglib.h"

int main(int argc,char **argv)
{
    /* Cover all six-bit samples with a compressible gradient at native size.
     * The earlier high-frequency vectors remain source-capacity tests. */
    if(argc!=3 || (argv[2][0]!='3' && argv[2][0]!='4') || argv[2][1])return 2;
    int channels=atoi(argv[2]);FILE *file=fopen(argv[1],"wb");if(!file)return 2;
    struct jpeg_compress_struct codec={0};struct jpeg_error_mgr error;
    codec.err=jpeg_std_error(&error);jpeg_create_compress(&codec);jpeg_stdio_dest(&codec,file);
    codec.image_width=240;codec.image_height=240;codec.input_components=channels;
    codec.in_color_space=channels==3 ? JCS_RGB:JCS_CMYK;
    jpeg_set_defaults(&codec);jpeg_set_colorspace(&codec,codec.in_color_space);
    codec.data_precision=6;codec.optimize_coding=TRUE;jpeg_enable_lossless(&codec,4,0);
    jpeg_start_compress(&codec,TRUE);
    JSAMPLE row[240*4];
    while(codec.next_scanline<codec.image_height) {
        for(unsigned x=0;x<240;++x)
            for(int channel=0;channel<channels;++channel)
                row[x*(unsigned)channels+(unsigned)channel]=(JSAMPLE)((x+2u*codec.next_scanline+3u*(unsigned)channel)&63u);
        JSAMPROW pointer=row;
        if(jpeg_write_scanlines(&codec,&pointer,1)!=1)return 1;
    }
    jpeg_finish_compress(&codec);jpeg_destroy_compress(&codec);
    return fclose(file) ? 1:0;
}
