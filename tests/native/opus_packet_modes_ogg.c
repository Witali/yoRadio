/* Independent creator libogg packet reconstruction from the complete file. */
#include <ogg/ogg.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t le32(const unsigned char *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void exact(FILE *f,void *p,size_t n){assert(fread(p,1,n,f)==n);}
static void walk(const unsigned char *body,size_t size,const char *transport,size_t chunk) {
    FILE *f=fopen(transport,"rb");assert(f);unsigned char head[28];exact(f,head,sizeof(head));assert(!memcmp(head,"OPMODE1\0",8));
    unsigned channels=le32(head+8),skip=le32(head+12),logical=le32(head+16),count=le32(head+20),duration=le32(head+24);
    ogg_sync_state sync;ogg_stream_state stream;assert(ogg_sync_init(&sync)==0);
    size_t at=0;unsigned pages=0,packets=0,audio=0;int serial=0;
    while(at<size) {
        size_t n=size-at;if(n>chunk)n=chunk;char *buffer=ogg_sync_buffer(&sync,(long)n);assert(buffer);memcpy(buffer,body+at,n);
        assert(ogg_sync_wrote(&sync,(long)n)==0);at+=n;
        for(;;) {
            ogg_page page;int status=ogg_sync_pageout(&sync,&page);assert(status>=0);if(!status)break;
            if(!pages){serial=ogg_page_serialno(&page);assert(ogg_stream_init(&stream,serial)==0 && ogg_page_bos(&page));}
            assert(ogg_page_serialno(&page)==serial && ogg_page_pageno(&page)==(long)pages && !ogg_page_continued(&page));
            ogg_int64_t gp=pages<2?0:pages==count+1?(ogg_int64_t)(skip+logical):(ogg_int64_t)((pages-1)*duration);
            assert(ogg_page_granulepos(&page)==gp && (ogg_page_eos(&page)!=0)==(pages==count+1));
            assert(ogg_stream_pagein(&stream,&page)==0);++pages;
            for(;;) {
                ogg_packet packet;status=ogg_stream_packetout(&stream,&packet);assert(status>=0);if(!status)break;
                assert(packet.packetno==(ogg_int64_t)packets && packet.granulepos==gp);
                if(!packets)assert(packet.bytes==19 && !memcmp(packet.packet,"OpusHead",8) && packet.packet[9]==channels && packet.packet[18]==0);
                else if(packets==1)assert(packet.bytes>=16 && !memcmp(packet.packet,"OpusTags",8));
                else {unsigned char bytes[4];exact(f,bytes,4);unsigned length=le32(bytes);assert(length && length<=61440 && packet.bytes==(long)length);
                      unsigned char expected[61440];exact(f,expected,length);assert(!memcmp(expected,packet.packet,length));++audio;}
                assert((packet.b_o_s!=0)==(!packets) && (packet.e_o_s!=0)==(packets==count+1));++packets;
            }
        }
    }
    ogg_page page;assert(ogg_sync_pageout(&sync,&page)==0 && ogg_stream_eos(&stream));
    assert(pages==count+2 && audio==count && packets==count+2 && fgetc(f)==EOF && !ferror(f));
    assert(!fclose(f) && ogg_stream_clear(&stream)==0 && ogg_sync_clear(&sync)==0);
    printf("{\"creator\":\"libogg\",\"chunk\":%zu,\"pages\":%u,\"audio_packets\":%u,\"exact_complete_packets\":true,\"eos\":true,\"sync_errors\":0,\"packet_holes\":0}\n",chunk,pages,audio);
}
int main(int argc,char **argv) {
    assert(argc==3);FILE *f=fopen(argv[1],"rb");assert(f && !fseek(f,0,SEEK_END));long length=ftell(f);assert(length>0 && length<1000000 && !fseek(f,0,SEEK_SET));
    unsigned char *body=malloc((size_t)length);assert(body);exact(f,body,(size_t)length);assert(!fclose(f));
    walk(body,(size_t)length,argv[2],(size_t)length);walk(body,(size_t)length,argv[2],257);walk(body,(size_t)length,argv[2],1);free(body);return 0;
}
