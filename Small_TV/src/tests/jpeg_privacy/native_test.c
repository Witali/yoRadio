/* Privacy grammar tests are separate from entropy decoding qualification. */
#include "jpeg_privacy.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned assertions;
#define CHECK(value) do {++assertions;if(!(value)){fprintf(stderr,"privacy failure at %d: %s\n",__LINE__,#value);exit(1);}}while(0)
typedef struct {
    uint8_t bytes[2048];
    uint32_t length;
    unsigned reads,checks,fail_read,fail_check;
} fixture_t;

static int read_source(void *context,uint32_t offset,void *data,size_t bytes)
{
    /* Reject every overread independently of the parser, and inject exact faults. */
    fixture_t *f=context;CHECK(offset<=f->length && bytes<=f->length-offset);
    if(++f->reads==f->fail_read)return -17;
    memcpy(data,f->bytes+offset,bytes);return 0;
}

static int checkpoint(void *context)
{
    /* A stopped parser must not issue another physical source read. */
    fixture_t *f=context;return ++f->checks==f->fail_check ? -23:0;
}

static void append(fixture_t *f,const void *data,size_t bytes)
{
    /* Construct independent marker streams, without a production serializer. */
    CHECK(bytes<=sizeof(f->bytes)-f->length);memcpy(f->bytes+f->length,data,bytes);f->length+=(uint32_t)bytes;
}

static void marker(fixture_t *f,uint8_t code,const void *payload,size_t bytes)
{
    /* Segment size includes its two length bytes and excludes FF/marker. */
    uint8_t head[]={255,code,(uint8_t)((bytes+2)>>8),(uint8_t)(bytes+2)};
    append(f,head,4);if(bytes)append(f,payload,bytes);
}

static fixture_t begin(unsigned process,unsigned precision)
{
    /* Intentionally minimal grammar fixture; codec validates the tables/scan. */
    fixture_t f={0};const uint8_t soi[]={255,216};append(&f,soi,2);
    const uint8_t jfif[]={'J','F','I','F',0,1,1,0,0,1,0,1,0,0};
    marker(&f,0xe0,jfif,sizeof(jfif));
    uint8_t frame[]={(uint8_t)precision,0,240,0,240,1,1,0x11,0};
    marker(&f,(uint8_t)process,frame,sizeof(frame));return f;
}

static void scan(fixture_t *f)
{
    /* Stuffed FF and standalone restart/TEM are entropy, not metadata segments. */
    const uint8_t sos[]={1,1,0,0,63,0};marker(f,0xda,sos,sizeof(sos));
    const uint8_t entropy[]={1,2,255,0,3,255,0xd0,4,255,1,5};append(f,entropy,sizeof(entropy));
}

static void end(fixture_t *f)
{
    /* Accept only one EOI at the exact declared end. */
    const uint8_t eoi[]={255,217};append(f,eoi,2);
}

static jpeg_privacy_diagnostic_t inspect(fixture_t *f,jpeg_privacy_result_t expected)
{
    /* Domain errors, rather than process crashes or decoder failure, are tested. */
    jpeg_privacy_diagnostic_t d;jpeg_privacy_source_t source={f,f->length,read_source,checkpoint};
    CHECK(jpeg_privacy_check(&source,&d)==expected);CHECK(d.status==expected);return d;
}

static void tests(void)
{
    /* Exercise all metadata positions, scan boundaries, truncations and callbacks. */
    fixture_t f=begin(0xc2,12);scan(&f);uint8_t entropy[270];memset(entropy,42,sizeof(entropy));
    /* FF at offset255 and its stuffed zero at256 cross the physical buffer. */
    CHECK(f.length<255);entropy[255-f.length]=255;entropy[256-f.length]=0;
    entropy[250]=255;entropy[251]=255;entropy[252]=0;append(&f,entropy,sizeof(entropy));
    marker(&f,0xc4,"xx",2);scan(&f);end(&f);
    jpeg_privacy_diagnostic_t d=inspect(&f,JPEG_PRIVACY_OK);
    CHECK(d.width==240 && d.height==240 && d.precision==12 && d.process==0xc2 && d.scans==2);
    unsigned reads=f.reads,checks=f.checks;
    for(unsigned i=1;i<=reads;++i){fixture_t bad=f;bad.reads=bad.checks=0;bad.fail_read=i;d=inspect(&bad,JPEG_PRIVACY_IO);CHECK(d.callback_error==-17 && bad.reads==i);}
    for(unsigned i=1;i<=checks;++i){fixture_t bad=f;bad.reads=bad.checks=0;bad.fail_check=i;d=inspect(&bad,JPEG_PRIVACY_STOP);CHECK(d.callback_error==-23 && bad.checks==i);}
    for(uint32_t size=0;size<f.length;++size){fixture_t bad=f;bad.length=size;bad.reads=bad.checks=0;jpeg_privacy_source_t source={&bad,size,read_source,checkpoint};CHECK(jpeg_privacy_check(&source,&d)!=JPEG_PRIVACY_OK);}
    const unsigned private_markers[]={0xe1,0xe2,0xe3,0xe4,0xe5,0xe6,0xe7,0xe8,0xe9,0xea,0xeb,0xec,0xed,0xef,0xfe};
    for(unsigned i=0;i<sizeof(private_markers)/sizeof(private_markers[0]);++i)
        for(unsigned position=0;position<3;++position) {
            fixture_t bad=begin(0xc0,8);if(position)scan(&bad);
            if(position==2){marker(&bad,0xc4,"xx",2);scan(&bad);}
            uint32_t at=bad.length;marker(&bad,(uint8_t)private_markers[i],"EXIF/private/date/GPS",21);scan(&bad);end(&bad);
            d=inspect(&bad,JPEG_PRIVACY_METADATA);CHECK(d.marker==private_markers[i] && d.offset==at);
        }
    for(unsigned transform=0;transform<3;++transform) {
        fixture_t adobe=begin(0xc2,12);uint8_t data[]={'A','d','o','b','e',0,100,0,0,0,0,(uint8_t)transform};
        marker(&adobe,0xee,data,sizeof(data));scan(&adobe);end(&adobe);inspect(&adobe,JPEG_PRIVACY_OK);
        const unsigned fields[]={0,5,6,7,8,9,10,11};
        for(unsigned i=0;i<sizeof(fields)/sizeof(fields[0]);++i) {
            fixture_t bad=begin(0xc0,8);uint8_t changed[12];memcpy(changed,data,12);changed[fields[i]]=255;
            marker(&bad,0xee,changed,12);scan(&bad);end(&bad);inspect(&bad,JPEG_PRIVACY_METADATA);
        }
    }
    fixture_t bad=f;append(&bad,"x",1);inspect(&bad,JPEG_PRIVACY_TRAILING);
    bad=begin(0xc0,8);bad.bytes[18]=1;scan(&bad);end(&bad);inspect(&bad,JPEG_PRIVACY_THUMBNAIL);
    bad=begin(0xc0,8);uint8_t junk[15]={0};marker(&bad,0xe0,junk,sizeof(junk));scan(&bad);end(&bad);inspect(&bad,JPEG_PRIVACY_METADATA);
    bad=begin(0xc0,8);scan(&bad);uint8_t dnl[]={0,240};marker(&bad,0xdc,dnl,2);append(&bad,"continued entropy",17);end(&bad);inspect(&bad,JPEG_PRIVACY_OK);
    const unsigned processes[]={0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf};
    for(unsigned i=0;i<sizeof(processes)/sizeof(processes[0]);++i){bad=begin(processes[i],16);scan(&bad);end(&bad);inspect(&bad,JPEG_PRIVACY_OK);}
    bad=begin(0xc0,8);const uint8_t fill[]={255,255,255,0xda,0,8,1,1,0,0,63,0};append(&bad,fill,sizeof(fill));append(&bad,"x",1);end(&bad);inspect(&bad,JPEG_PRIVACY_OK);
    jpeg_privacy_source_t invalid={0};CHECK(jpeg_privacy_check(NULL,&d)==JPEG_PRIVACY_ARGUMENT);CHECK(jpeg_privacy_check(&invalid,&d)==JPEG_PRIVACY_ARGUMENT);
    CHECK(!strcmp(jpeg_privacy_status_name(JPEG_PRIVACY_METADATA),"private-metadata"));
    printf("{\"passed\":true,\"assertions\":%u,\"read_faults\":%u,\"check_stops\":%u,\"truncations\":%u,\"metadata_positions\":45}\n",assertions,reads,checks,f.length);
}

static int file_read(void *context,uint32_t offset,void *data,size_t bytes)
{
    /* Driver path for real codec-qualified JPEG files; no metadata rewriting. */
    FILE *file=context;return fseek(file,(long)offset,SEEK_SET) || fread(data,1,bytes,file)!=bytes;
}

static int file_check(void *context)
{
    /* No clock is imposed by this host-only privacy inspection driver. */
    (void)context;return 0;
}

int main(int argc,char **argv)
{
    /* No argument runs controls; one filename prints the exact privacy result. */
    if(argc==1){tests();return 0;}
    CHECK(argc==2);FILE *file=fopen(argv[1],"rb");CHECK(file);CHECK(!fseek(file,0,SEEK_END));long bytes=ftell(file);CHECK(bytes>=0 && bytes<=2000000);
    jpeg_privacy_source_t source={file,(uint32_t)bytes,file_read,file_check};jpeg_privacy_diagnostic_t d;
    jpeg_privacy_result_t result=jpeg_privacy_check(&source,&d);CHECK(!fclose(file));
    printf("{\"result\":\"%s\",\"marker\":%u,\"offset\":%u,\"precision\":%u,\"scans\":%u}\n",jpeg_privacy_status_name(result),d.marker,d.offset,d.precision,d.scans);return 0;
}
