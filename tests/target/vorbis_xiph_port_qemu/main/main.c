// Complete upstream Xiph evaluation through public raw packet/synthesis APIs.
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "vorbis/codec.h"
#include "cases.h"
#include "vorbis_xiph_alloc.h"
extern int xiph_arena_tests(void);
extern int xiph_book_tests(void);
extern int xiph_bitreader_tests(void);
#ifdef NDEBUG
#error "Xiph capture requires active guard assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "First upstream Xiph baseline is ESP32 only"
#endif
enum{WORKER_CORE=1,CHUNK_SAMPLES=256,CONVERSION_CONTROLS=17};
static const uint64_t CANARY=UINT64_C(0x641bf42c3d8a9705);
typedef struct{uint64_t before;int16_t samples[CHUNK_SAMPLES];uint64_t after;} conversion_t;
static conversion_t conversion;
static char hexadecimal[4*CHUNK_SAMPLES+1];
_Static_assert(sizeof(int16_t)==2 && CHAR_BIT==8,"PCM signed16 octets");
_Static_assert(__BYTE_ORDER__==__ORDER_LITTLE_ENDIAN__,"PCM byte capture is little endian");
_Static_assert(offsetof(conversion_t,samples)==8 && offsetof(conversion_t,after)==8+2*CHUNK_SAMPLES,"Adjacent typed PCM guards");
typedef struct{unsigned char *base,*data;const uint8_t *original;size_t bytes;} packet_buffer_t;
static packet_buffer_t packet_create(const uint8_t *source,size_t bytes){
    assert(source && bytes && bytes<=LONG_MAX && bytes<=SIZE_MAX-16);packet_buffer_t p={0};p.base=malloc(bytes+16);assert(p.base);p.data=p.base+8;p.bytes=bytes;p.original=source;
    memcpy(p.base,&CANARY,8);memcpy(p.data+bytes,&CANARY,8);memcpy(p.data,source,bytes);return p;
}
static void packet_check(const packet_buffer_t *p){uint64_t a,z;memcpy(&a,p->base,8);memcpy(&z,p->data+p->bytes,8);assert(a==CANARY && z==CANARY && !memcmp(p->data,p->original,p->bytes));}
static void packet_destroy(packet_buffer_t *p){packet_check(p);free(p->base);}
static void conversion_check(void){assert(conversion.before==CANARY && conversion.after==CANARY);}
static int convert(float input,int16_t *output){
    if(!isfinite(input))return -1;
    double value=(double)input*32768.0;int32_t result;
    if(value>=32767.0)result=32767;
    else if(value<=-32768.0)result=-32768;
    else{double lower=floor(value),fraction=value-lower;result=(int32_t)lower;if(fraction>0.5 || (fraction==0.5 && result%2!=0))result++;}
    *output=(int16_t)result;return 0;
}
static void controls(void){
    const float values[]={0.5f/32768,1.5f/32768,2.5f/32768,-0.5f/32768,-1.5f/32768,-2.5f/32768,1,-1,2,-2,0,-0.0f,0.25f,-0.25f};
    const int16_t expected[]={0,2,2,0,-2,-2,32767,-32768,32767,-32768,0,0,8192,-8192};unsigned count=0;
    for(size_t i=0;i<sizeof(values)/sizeof(values[0]);i++){int16_t actual=123;assert(convert(values[i],&actual)==0 && actual==expected[i]);count++;}
    const float invalid[]={NAN,INFINITY,-INFINITY};for(unsigned i=0;i<3;i++){int16_t unchanged=123;assert(convert(invalid[i],&unchanged)==-1 && unchanged==123);count++;}
    assert(count==CONVERSION_CONTROLS);printf("XIPH_CONTROLS checks=%u core=%d\n",count,xPortGetCoreID());
}
static void hex_bytes(const uint8_t *data,size_t bytes){static const char table[]="0123456789abcdef";assert(2*bytes<sizeof(hexadecimal));for(size_t i=0;i<bytes;i++){hexadecimal[2*i]=table[data[i]>>4];hexadecimal[2*i+1]=table[data[i]&15];}hexadecimal[2*bytes]=0;}
static ogg_packet make_packet(packet_buffer_t *buffer,int64_t number,int64_t granule,bool bos,bool eos){
    ogg_packet packet;memset(&packet,0,sizeof(packet));packet.packet=buffer->data;packet.bytes=(long)buffer->bytes;packet.packetno=(ogg_int64_t)number;packet.granulepos=(ogg_int64_t)granule;packet.b_o_s=bos;packet.e_o_s=eos;return packet;
}
static void metadata_check(const ogg_packet *a,const ogg_packet *b){assert(a->packet==b->packet && a->bytes==b->bytes && a->b_o_s==b->b_o_s && a->e_o_s==b->e_o_s && a->granulepos==b->granulepos && a->packetno==b->packetno);}
static void stop(const char *status){printf("XIPH_STOP status=%s\n",status);fflush(stdout);esp_restart();}
static void capture(uint32_t index){
    const xiph_case_t *test=&xiph_cases[index];assert(test->packet_count==14 && test->channels>=1 && test->channels<=255 && test->audio_bytes && test->offsets[0]==0 && test->offsets[test->packet_count]==test->audio_bytes);
    unsigned free_before=esp_get_free_heap_size(),largest_before=(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),stack_before=(unsigned)uxTaskGetStackHighWaterMark(NULL);
    printf("XIPH_CASE case=%"PRIu32" id=%s packets=%"PRIu32" core=%d\n",index,test->id,test->packet_count,xPortGetCoreID());
    vorbis_info info;vorbis_comment comment;vorbis_dsp_state dsp;vorbis_block block;memset(&dsp,0,sizeof(dsp));memset(&block,0,sizeof(block));vorbis_info_init(&info);vorbis_comment_init(&comment);
    const uint8_t *headers[]={test->identification,test->comment,test->setup};const uint32_t lengths[]={test->identification_bytes,test->comment_bytes,test->setup_bytes};bool api_ok=true;
    for(unsigned h=0;h<3;h++){
        packet_buffer_t guarded=packet_create(headers[h],lengths[h]);ogg_packet packet=make_packet(&guarded,h,0,h==0,false),before=packet;int status=api_ok?vorbis_synthesis_headerin(&info,&comment,&packet):-99;metadata_check(&before,&packet);packet_destroy(&guarded);if(status)api_ok=false;
        printf("XIPH_HEADER case=%"PRIu32" header=%u status=%d guards=1 unchanged=1 core=%d\n",index,h,status,xPortGetCoreID());
    }
    int synthesis_init_status=api_ok?vorbis_synthesis_init(&dsp,&info):-99;bool dsp_ready=synthesis_init_status==0;if(!dsp_ready)api_ok=false;
    int block_init_status=dsp_ready?vorbis_block_init(&dsp,&block):-99;bool block_ready=block_init_status==0;if(!block_ready)api_ok=false;
    printf("XIPH_INIT case=%"PRIu32" synthesis_status=%d block_status=%d core=%d\n",index,synthesis_init_status,block_init_status,xPortGetCoreID());
    if(dsp_ready){long short_block=vorbis_info_blocksize(&info,0),long_block=vorbis_info_blocksize(&info,1);assert(info.channels>=1 && info.channels<=255 && info.rate>0 && short_block>0 && long_block>0);printf("XIPH_INFO case=%"PRIu32" rate=%ld channels=%d short_block=%ld long_block=%ld core=%d\n",index,info.rate,info.channels,short_block,long_block,xPortGetCoreID());}
    unsigned free_open=esp_get_free_heap_size();uint64_t total_frames=0,total_samples=0;
    for(uint32_t p=0;p<test->packet_count;p++){
        assert(test->offsets[p]<test->offsets[p+1] && test->offsets[p+1]<=test->audio_bytes);size_t bytes=test->offsets[p+1]-test->offsets[p];packet_buffer_t guarded=packet_create(test->audio+test->offsets[p],bytes);
        ogg_packet packet=make_packet(&guarded,(int64_t)p+3,test->granules[p],false,p+1==test->packet_count),before=packet;int synthesis_status=block_ready && api_ok?vorbis_synthesis(&block,&packet):-99;int blockin_status=synthesis_status==0?vorbis_synthesis_blockin(&dsp,&block):-99;
        printf("XIPH_PACKET_BEGIN case=%"PRIu32" packet=%"PRIu32" granule=%"PRId64" eos=%u core=%d\n",index,p,test->granules[p],(unsigned)(p+1==test->packet_count),xPortGetCoreID());uint64_t packet_frames=0;int read_status=-99;
        if(synthesis_status==0 && blockin_status==0){
            float **pcm=NULL;int available;
            while((available=vorbis_synthesis_pcmout(&dsp,&pcm))>0){
                assert(pcm && info.channels>=1 && info.channels<=255);unsigned frames=(unsigned)available,limit=CHUNK_SAMPLES/(unsigned)info.channels;if(frames>limit)frames=limit;assert(frames && frames<=8192);
                int16_t *out=conversion.samples;conversion_check();memset(out,0xa5,sizeof(conversion.samples));for(unsigned frame=0;frame<frames;frame++)for(int channel=0;channel<info.channels;channel++)assert(convert(pcm[channel][frame],&out[frame*(unsigned)info.channels+(unsigned)channel])==0);conversion_check();
                unsigned samples=frames*(unsigned)info.channels;const uint8_t *raw=(const void *)out;for(size_t i=2*samples;i<sizeof(conversion.samples);i++)assert(raw[i]==0xa5);hex_bytes(raw,2*samples);printf("XIPH_PCM case=%"PRIu32" packet=%"PRIu32" start=%"PRIu64" frames=%u samples=%u hex=%s guards=1 core=%d\n",index,p,total_samples,frames,samples,hexadecimal,xPortGetCoreID());
                read_status=vorbis_synthesis_read(&dsp,(int)frames);assert(read_status==0);packet_frames+=frames;total_frames+=frames;total_samples+=samples;
            }
            assert(available==0);
        }else api_ok=false;
        metadata_check(&before,&packet);packet_destroy(&guarded);printf("XIPH_PACKET_END case=%"PRIu32" packet=%"PRIu32" synthesis_status=%d blockin_status=%d read_status=%d frames=%"PRIu64" guards=1 unchanged=1 core=%d\n",index,p,synthesis_status,blockin_status,read_status,packet_frames,xPortGetCoreID());
    }
    if(block_ready){assert(vorbis_block_clear(&block)==0);}
    if(dsp_ready){vorbis_dsp_clear(&dsp);}
    vorbis_comment_clear(&comment);vorbis_info_clear(&info);conversion_check();assert(heap_caps_check_integrity_all(true));
    printf("XIPH_CASE_END case=%"PRIu32" frames=%"PRIu64" pcm_bytes=%"PRIu64" api_ok=%u free_before=%u free_open=%u free_after=%u minimum_free=%u largest_before=%u largest_after=%u stack_before=%u stack_after=%u guards=1 unchanged=1 core=%d\n",index,total_frames,2*total_samples,(unsigned)api_ok,free_before,free_open,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),largest_before,(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),stack_before,(unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID());
}
static void port_resource_tests(void){
    assert(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    printf("PORT_RESOURCE phase=arena_before base=%s port=%s live=0 bytes=0 core=%d\n",XIPH_MANIFEST_SHA256,XIPH_PORT_MANIFEST_SHA256,xPortGetCoreID());
    int arena=xiph_arena_tests();assert(arena==11 && xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    printf("PORT_RESOURCE phase=arena_after checks=%d live=0 bytes=0 core=%d\n",arena,xPortGetCoreID());
    printf("PORT_RESOURCE phase=books_before live=0 bytes=0 core=%d\n",xPortGetCoreID());
    int books=xiph_book_tests();assert(books>0 && xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    printf("PORT_RESOURCE phase=books_after checks=%d live=0 bytes=0 core=%d\n",books,xPortGetCoreID());
    printf("PORT_RESOURCE phase=bits_before live=0 bytes=0 core=%d\n",xPortGetCoreID());
    int bits=xiph_bitreader_tests();assert(bits>0 && xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    printf("PORT_RESOURCE phase=bits_after checks=%d live=0 bytes=0 core=%d\n",bits,xPortGetCoreID());
    xiph_port_test_reset(0);
}
static void port_case_resource(uint32_t index){
    assert(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    printf("PORT_RESOURCE phase=case case=%"PRIu32" live=0 bytes=0 core=%d\n",index,xPortGetCoreID());
}
static void port_complete_resource(void){
    assert(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    printf("PORT_RESOURCE phase=complete live=0 bytes=0 core=%d\n",xPortGetCoreID());
}
static void worker(void *unused){
    (void)unused;conversion.before=conversion.after=CANARY;printf("XIPH_WORKER core=%d priority=%u stack=16384\n",xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));port_resource_tests();controls();
    const char *version=vorbis_version_string();assert(version && strlen(version)<=256);hex_bytes((const uint8_t *)version,strlen(version));printf("XIPH_VERSION hex=%s core=%d\n",hexadecimal,xPortGetCoreID());
    for(uint32_t i=0;i<XIPH_CASE_COUNT;i++){assert(xPortGetCoreID()==WORKER_CORE);capture(i);port_case_resource(i);vTaskDelay(1);}
    port_complete_resource();
    printf("XIPH_COMPLETE cases=%u controls=%u core=%d\n",(unsigned)XIPH_CASE_COUNT,CONVERSION_CONTROLS,xPortGetCoreID());stop("CAPTURED");
}
void app_main(void){printf("XIPH_BEGIN cases=%u coordinator=%d worker=%d data=%s component=%s\n",(unsigned)XIPH_CASE_COUNT,xPortGetCoreID(),WORKER_CORE,XIPH_CASES_SHA256,XIPH_MANIFEST_SHA256);fflush(stdout);if(xTaskCreatePinnedToCore(worker,"vorbis_xiph",16384,NULL,3,NULL,WORKER_CORE)!=pdPASS)stop("TASK_CREATE_FAILED");}
