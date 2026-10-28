/* Real legal noninterleaved scans for sampling ratios beyond old420/422/444. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "jpeglib.h"

int main(int argc,char **argv)
{
    /* Each component has separate DC and AC scans, so4x4 factors do not violate
     * the interleaved10-block MCU limit. Actual padded coefficient arrays can
     * exceed460800 even though the native output is still240x240. */
    if(argc!=5 && argc!=6)return 2;
    int flat=argc==6;if(flat && strcmp(argv[5],"flat"))return 2;
    unsigned factors=(unsigned)strtoul(argv[2],NULL,16),bits=(unsigned)atoi(argv[3]),components=(unsigned)atoi(argv[4]);
    if(!factors || (bits!=8 && bits!=12) || (components!=1 && components!=3 && components!=4))return 2;
    struct jpeg_compress_struct codec={0};struct jpeg_error_mgr error;codec.err=jpeg_std_error(&error);
    jpeg_create_compress(&codec);FILE *file=fopen(argv[1],"wb");if(!file)return 2;jpeg_stdio_dest(&codec,file);
    codec.image_width=codec.image_height=240;codec.input_components=(int)components;
    codec.in_color_space=components==4 ? JCS_CMYK : components==3 ? JCS_RGB : JCS_GRAYSCALE;
    jpeg_set_defaults(&codec);codec.data_precision=(int)bits;jpeg_set_quality(&codec,83,FALSE);codec.optimize_coding=TRUE;
    for(unsigned i=0;i<components;++i){codec.comp_info[i].h_samp_factor=(int)(factors>>4);codec.comp_info[i].v_samp_factor=(int)(factors&15);}
    /*411/440/410 test luma sampling relative to the other two components. */
    if(components==3 && factors!=0x44)
        for(unsigned i=1;i<components;++i)codec.comp_info[i].h_samp_factor=codec.comp_info[i].v_samp_factor=1;
    jpeg_scan_info scans[8]={0};
    for(unsigned i=0;i<components;++i) {
        scans[2*i].comps_in_scan=1;scans[2*i].component_index[0]=(int)i;scans[2*i].Ss=scans[2*i].Se=0;
        scans[2*i+1].comps_in_scan=1;scans[2*i+1].component_index[0]=(int)i;scans[2*i+1].Ss=1;scans[2*i+1].Se=63;
    }
    codec.scan_info=scans;codec.num_scans=(int)components*2;jpeg_start_compress(&codec,TRUE);
    JSAMPLE row8[240*4];J12SAMPLE row12[240*4];
    while(codec.next_scanline<codec.image_height) {
        for(unsigned x=0;x<240;++x)for(unsigned c=0;c<components;++c) {
            /* Flat controls retain the SAME padded array geometry while fitting
             * the real photo source slot; rich controls still test its limit. */
            unsigned value=flat ? 1u<<(bits-1u):(x*17u+codec.next_scanline*31u+c*47u)&((1u<<bits)-1u);
            row8[x*components+c]=(JSAMPLE)value;row12[x*components+c]=(J12SAMPLE)value;
        }
        if(bits==8){JSAMPROW row=row8;jpeg_write_scanlines(&codec,&row,1);}
        else {J12SAMPROW row=row12;jpeg12_write_scanlines(&codec,&row,1);}
    }
    jpeg_finish_compress(&codec);jpeg_destroy_compress(&codec);return fclose(file) ? 2:0;
}
