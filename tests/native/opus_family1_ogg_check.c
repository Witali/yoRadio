/* Independent creator libogg walk of each complete generated family1 file. */
#include <ogg/ogg.h>
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t le32(const unsigned char *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void exact(FILE *f,void *p,size_t n){assert(fread(p,1,n,f)==n);}
static void walk(const unsigned char *body,size_t size,const char *transport,size_t chunk) {
    FILE *f=fopen(transport,"rb");assert(f);unsigned char head[40];exact(f,head,sizeof(head));assert(!memcmp(head,"OFAM101\0",8));
    unsigned channels=le32(head+8),streams=le32(head+12),coupled=le32(head+16),pre_skip=le32(head+20),packets=le32(head+28);
    assert(channels==3 || channels==6 || channels==8);ogg_sync_state sync;ogg_stream_state stream;
    assert(ogg_sync_init(&sync)==0);unsigned pages=0,count=0,audio=0;size_t at=0;int serial=0,eos=0;
    while(at<size) {
        size_t n=size-at;if(n>chunk)n=chunk;char *buffer=ogg_sync_buffer(&sync,(long)n);assert(buffer);memcpy(buffer,body+at,n);
        assert(ogg_sync_wrote(&sync,(long)n)==0);at+=n;
        for(;;) {
            ogg_page page;int status=ogg_sync_pageout(&sync,&page);assert(status>=0);if(!status)break;
            if(!pages){serial=ogg_page_serialno(&page);assert(ogg_stream_init(&stream,serial)==0 && ogg_page_bos(&page));}
            assert(ogg_page_serialno(&page)==serial && ogg_page_pageno(&page)==(long)pages && !ogg_page_continued(&page));
            ogg_int64_t gp=pages<2?0:pages==12?(ogg_int64_t)(pre_skip+9600):(ogg_int64_t)((pages-1)*960);
            assert(ogg_page_granulepos(&page)==gp && (ogg_page_eos(&page)!=0)==(pages==12));
            assert(ogg_stream_pagein(&stream,&page)==0);++pages;
            for(;;) {
                ogg_packet packet;status=ogg_stream_packetout(&stream,&packet);assert(status>=0);if(!status)break;
                assert(packet.packetno==(ogg_int64_t)count && packet.granulepos==gp);
                if(!count) {
                    assert(packet.bytes==(long)(21+channels) && !memcmp(packet.packet,"OpusHead",8) && packet.packet[8]==1 &&
                        packet.packet[9]==channels && packet.packet[18]==1 && packet.packet[19]==streams && packet.packet[20]==coupled &&
                        !memcmp(packet.packet+21,head+32,channels));
                } else if(count==1)assert(packet.bytes>=16 && !memcmp(packet.packet,"OpusTags",8));
                else {
                    unsigned char nbytes[4];exact(f,nbytes,4);uint32_t bytes=le32(nbytes);assert(bytes && bytes<=61440 && packet.bytes==(long)bytes);
                    unsigned char *expected=malloc(bytes);assert(expected);exact(f,expected,bytes);assert(!memcmp(expected,packet.packet,bytes));free(expected);++audio;
                }
                assert((packet.b_o_s!=0)==(!count) && (packet.e_o_s!=0)==(count==12));++count;
            }
        }
    }
    ogg_page page;assert(ogg_sync_pageout(&sync,&page)==0);eos=ogg_stream_eos(&stream);
    assert(pages==13 && audio==packets && packets==11 && count==13 && eos && fgetc(f)==EOF && !ferror(f));
    assert(!fclose(f) && ogg_stream_clear(&stream)==0 && ogg_sync_clear(&sync)==0);
    printf("{\"creator\":\"libogg\",\"channels\":%u,\"chunk\":%zu,\"input_bytes\":%zu,\"pages\":%u,\"audio_packets\":%u,\"exact_original_packets\":true,\"eos\":true,\"sync_errors\":0,\"packet_holes\":0}\n",
        channels,chunk,size,pages,audio);
}
int main(int argc,char **argv) {
    assert(argc==3);FILE *f=fopen(argv[1],"rb");assert(f && !fseek(f,0,SEEK_END));long length=ftell(f);assert(length>0 && length<1000000 && !fseek(f,0,SEEK_SET));
    size_t size=(size_t)length;unsigned char *body=malloc(size);assert(body);exact(f,body,size);assert(!fclose(f));
    walk(body,size,argv[2],size);walk(body,size,argv[2],257);free(body);return 0;
}
