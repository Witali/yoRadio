// Guarded caller-owned setup capture. Allocation belongs only to this fixture.
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "native_vorbis_setup.h"
#include "cases.h"
#ifdef NDEBUG
#error "Owned controls/getter capture require active assertions"
#endif
#include "controls.h"
#include "getters.h"
_Static_assert(_Alignof(native_vorbis_codebook_t)<=8 && _Alignof(native_vorbis_setup_t)<=8,"Eight-byte guarded alignment");
#if CONFIG_IDF_TARGET_ESP32
enum { worker_core=1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { worker_core=0 };
#else
#error "Unsupported setup fixture target"
#endif
enum { CHUNK=128 };
static char hex_buffer[24*CHUNK+1];
static void stop(const char *status){printf("SETUP_STOP status=%s\n",status);fflush(stdout);esp_restart();}
static void require(bool ok,int line){if(!ok){printf("SETUP_FAILURE line=%d core=%d\n",line,xPortGetCoreID());stop("FAIL");}}
#define REQUIRE(ok) require((ok),__LINE__)
typedef struct { unsigned char *base,*data,*before;size_t bytes; } guarded_t;
static guarded_t allocate(size_t count,size_t unit){
    REQUIRE(unit && count<=(SIZE_MAX-16)/unit);guarded_t b={0};b.bytes=count*unit;b.base=malloc(b.bytes+16);REQUIRE(b.base!=NULL);
    b.data=b.base+8;memcpy(b.base,&CANARY,8);memcpy(b.data+b.bytes,&CANARY,8);memset(b.data,0xa5,b.bytes);return b;
}
static void snapshot(guarded_t *b){REQUIRE(!b->before);b->before=malloc(b->bytes?b->bytes:1);REQUIRE(b->before!=NULL);memcpy(b->before,b->data,b->bytes);}
static bool guards(const guarded_t *b){uint64_t a,z;memcpy(&a,b->base,8);memcpy(&z,b->data+b->bytes,8);return a==CANARY && z==CANARY;}
static bool unchanged(const guarded_t *b){return b->before && !memcmp(b->before,b->data,b->bytes);}
static void release(guarded_t *b){free(b->before);free(b->base);memset(b,0,sizeof(*b));}
static guarded_t packet(const uint8_t *data,size_t bytes){guarded_t b=allocate(bytes,1);if(bytes)memcpy(b.data,data,bytes);snapshot(&b);return b;}
static void hex_word(char *out,uint64_t value,unsigned digits){static const char table[]="0123456789abcdef";for(unsigned i=0;i<digits;i++)out[i]=table[(value>>(4*(digits-1-i)))&15U];}
static void raw_array(const char *kind,uint32_t index,int book,const void *data,size_t count,unsigned width){
    size_t start=0;
    do{
        size_t n=count-start;if(n>CHUNK)n=CHUNK;
        for(size_t i=0;i<n;i++){
            if(width==24){const native_vorbis_codeword_t *w=data;hex_word(hex_buffer+24*i,w[start+i].code,8);hex_word(hex_buffer+24*i+8,w[start+i].entry,8);hex_word(hex_buffer+24*i+16,w[start+i].length,8);}
            else if(width==4){const uint16_t *v=data;hex_word(hex_buffer+4*i,v[start+i],4);}
            else{const uint32_t *v=data;hex_word(hex_buffer+8*i,v[start+i],8);}
        }
        hex_buffer[width*n]=0;
        if(book>=0){printf("SETUP_%s case=%"PRIu32" book=%d start=%u total=%u count=%u hex=%s core=%d\n",kind,index,book,(unsigned)start,(unsigned)count,(unsigned)n,n?hex_buffer:"-",xPortGetCoreID());}
        else{printf("SETUP_%s case=%"PRIu32" start=%u total=%u count=%u hex=%s core=%d\n",kind,index,(unsigned)start,(unsigned)count,(unsigned)n,n?hex_buffer:"-",xPortGetCoreID());}
        start+=n;
    }while(start<count);
}
static void id_values(const native_vorbis_identification_t *id,uint32_t v[7]){
    v[0]=id->channels;v[1]=id->sample_rate;v[2]=id->bitrate_maximum_bits;v[3]=id->bitrate_nominal_bits;v[4]=id->bitrate_minimum_bits;v[5]=id->blocksize_0;v[6]=id->blocksize_1;
}
static bool same_id(const native_vorbis_identification_t *a,const native_vorbis_identification_t *b){uint32_t x[7],y[7];id_values(a,x);id_values(b,y);return !memcmp(x,y,sizeof(x));}
static bool same_layout(const native_vorbis_setup_layout_t *a,const native_vorbis_setup_layout_t *b){
    return same_id(&a->identification,&b->identification) && a->end_bit==b->end_bit && a->codeword_count==b->codeword_count && a->multiplicand_count==b->multiplicand_count &&
        a->book_count==b->book_count && a->time_count==b->time_count && a->floor_count==b->floor_count && a->residue_count==b->residue_count &&
        a->mapping_count==b->mapping_count && a->mode_count==b->mode_count && a->configuration_count==b->configuration_count &&
        a->floor_table==b->floor_table && a->residue_table==b->residue_table && a->mapping_table==b->mapping_table && a->mode_table==b->mode_table;
}
static bool same_quant(const native_vorbis_quant_layout_t *a,const native_vorbis_quant_layout_t *b){
    return a->dimensions==b->dimensions && a->entries==b->entries && a->lookup_type==b->lookup_type && a->minimum_bits==b->minimum_bits && a->delta_bits==b->delta_bits &&
        a->value_bits==b->value_bits && a->sequence_p==b->sequence_p && a->multiplicand_count==b->multiplicand_count && a->start_bit==b->start_bit && a->multiplicand_bit==b->multiplicand_bit && a->end_bit==b->end_bit;
}
static void capture(uint32_t index){
    const setup_case_t *test=&setup_cases[index];REQUIRE(test->identification_bytes<=16384 && test->setup_bytes<=16384 && test->audio_bytes<=16384);
    guarded_t id_packet=packet(test->identification,test->identification_bytes),setup_packet=packet(test->setup,test->setup_bytes),audio_packet=packet(test->audio,test->audio_bytes);
    guarded_t identity=allocate(1,sizeof(native_vorbis_identification_t)),layout_buf=allocate(1,sizeof(native_vorbis_setup_layout_t)),view_buf=allocate(1,sizeof(native_vorbis_setup_t));
    native_vorbis_identification_t *id=(void *)identity.data;native_vorbis_setup_layout_t *layout=(void *)layout_buf.data;native_vorbis_setup_t *view=(void *)view_buf.data;
    int is=native_vorbis_identification_parse(id_packet.data,test->identification_bytes,test->identification_bits,id);REQUIRE(is==0);snapshot(&identity);
    int ms=native_vorbis_setup_measure(setup_packet.data,test->setup_bytes,test->setup_bits,id,layout);REQUIRE(ms==0 && same_id(id,&layout->identification));
    REQUIRE(layout->book_count>=1 && layout->book_count<=256 && layout->codeword_count<=512 && layout->multiplicand_count<=1024 && layout->configuration_count<=8192 &&
        layout->time_count>=1 && layout->time_count<=64 && layout->floor_count>=1 && layout->floor_count<=64 && layout->residue_count>=1 && layout->residue_count<=64 &&
        layout->mapping_count>=1 && layout->mapping_count<=64 && layout->mode_count>=1 && layout->mode_count<=64 && layout->end_bit<=test->setup_bits);
    snapshot(&layout_buf);
    guarded_t books=allocate(layout->book_count,sizeof(native_vorbis_codebook_t)),words=allocate((size_t)layout->codeword_count,sizeof(native_vorbis_codeword_t));
    guarded_t multiplicands=allocate((size_t)layout->multiplicand_count,sizeof(uint16_t)),configuration=allocate(layout->configuration_count,sizeof(uint32_t));
    guarded_t descriptor=allocate(1,sizeof(native_vorbis_setup_storage_t));native_vorbis_setup_storage_t *storage=(void *)descriptor.data;
    *storage=(native_vorbis_setup_storage_t){(void *)books.data,layout->book_count,(void *)words.data,(size_t)layout->codeword_count,
        (void *)multiplicands.data,(size_t)layout->multiplicand_count,(void *)configuration.data,layout->configuration_count};snapshot(&descriptor);
    int mt=native_vorbis_setup_materialize(setup_packet.data,test->setup_bytes,test->setup_bits,layout,storage,view);
    REQUIRE(mt==0 && same_layout(layout,&view->layout) && view->books==(void *)books.data && view->configuration==(void *)configuration.data &&
        view->book_count==layout->book_count && view->configuration_count==layout->configuration_count);
    size_t word_offset=0,q_offset=0;
    for(size_t i=0;i<view->book_count;i++){
        const native_vorbis_codebook_t *b=&view->books[i];size_t nw=b->layout.used_entries;uint64_t nq=b->layout.quantization.multiplicand_count;
        REQUIRE(nw<=layout->codeword_count-word_offset && nq<=layout->multiplicand_count-q_offset && b->word_count==nw && b->quantization.storage_count==nq);
        REQUIRE(b->words==(nw?(native_vorbis_codeword_t *)words.data+word_offset:NULL) &&
            b->quantization.multiplicands==(nq?(uint16_t *)multiplicands.data+q_offset:NULL) && same_quant(&b->layout.quantization,&b->quantization.layout));
        word_offset+=nw;q_offset+=(size_t)nq;
    }
    REQUIRE(word_offset==layout->codeword_count && q_offset==layout->multiplicand_count);
    snapshot(&books);snapshot(&words);snapshot(&multiplicands);snapshot(&configuration);snapshot(&view_buf);
    size_t getter_capacity=(size_t)layout->configuration_count+16U*layout->floor_count;REQUIRE(getter_capacity<=32768);
    guarded_t getter_output=allocate(getter_capacity,sizeof(uint32_t));size_t getter_count=capture_getters(view,(void *)getter_output.data,getter_capacity);
    guarded_t cursor_buf=allocate(1,sizeof(native_vorbis_packet_t)),prefix_buf=allocate(1,sizeof(native_vorbis_audio_prefix_t));
    native_vorbis_packet_t *cursor=(void *)cursor_buf.data;native_vorbis_audio_prefix_t *prefix=(void *)prefix_buf.data;
    REQUIRE(native_vorbis_packet_init(cursor,audio_packet.data,test->audio_bytes,test->audio_bits,test->audio_start)==0);
    int as=native_vorbis_audio_prefix(view,cursor,prefix);REQUIRE(as==0 && !cursor->end_of_packet && cursor->position>=test->audio_start && cursor->position<=test->audio_bits &&
        cursor->data==audio_packet.data && cursor->bytes==test->audio_bytes && cursor->bits==test->audio_bits);
    guarded_t *all[]={&id_packet,&setup_packet,&audio_packet,&identity,&layout_buf,&view_buf,&books,&words,&multiplicands,&configuration,&descriptor,&getter_output,&cursor_buf,&prefix_buf};
    bool guarded=true;for(size_t i=0;i<sizeof(all)/sizeof(all[0]);i++)guarded=guarded && guards(all[i]);
    guarded_t *inputs[]={&id_packet,&setup_packet,&audio_packet,&identity,&layout_buf,&view_buf,&books,&words,&multiplicands,&configuration,&descriptor};
    bool preserved=true;for(size_t i=0;i<sizeof(inputs)/sizeof(inputs[0]);i++)preserved=preserved && unchanged(inputs[i]);REQUIRE(guarded && preserved);
    printf("SETUP_CASE case=%"PRIu32" id=%s id_status=%d measure_status=%d materialize_status=%d audio_status=%d core=%d\n",index,test->id,is,ms,mt,as,xPortGetCoreID());
    printf("SETUP_IDENT case=%"PRIu32" channels=%"PRIu32" sample_rate=%"PRIu32" bitrate_maximum_bits=%"PRIu32" bitrate_nominal_bits=%"PRIu32" bitrate_minimum_bits=%"PRIu32" blocksize_0=%"PRIu32" blocksize_1=%"PRIu32" core=%d\n",
        index,id->channels,id->sample_rate,id->bitrate_maximum_bits,id->bitrate_nominal_bits,id->bitrate_minimum_bits,id->blocksize_0,id->blocksize_1,xPortGetCoreID());
    const native_vorbis_identification_t *li=&layout->identification;
    printf("SETUP_LAYOUT case=%"PRIu32" id_channels=%"PRIu32" id_sample_rate=%"PRIu32" id_bitrate_maximum_bits=%"PRIu32" id_bitrate_nominal_bits=%"PRIu32" id_bitrate_minimum_bits=%"PRIu32" id_blocksize_0=%"PRIu32" id_blocksize_1=%"PRIu32
        " end_bit=%"PRIu64" codeword_count=%"PRIu64" multiplicand_count=%"PRIu64" book_count=%"PRIu32" time_count=%"PRIu32" floor_count=%"PRIu32
        " residue_count=%"PRIu32" mapping_count=%"PRIu32" mode_count=%"PRIu32" configuration_count=%"PRIu32" floor_table=%"PRIu32" residue_table=%"PRIu32" mapping_table=%"PRIu32" mode_table=%"PRIu32" core=%d\n",
        index,li->channels,li->sample_rate,li->bitrate_maximum_bits,li->bitrate_nominal_bits,li->bitrate_minimum_bits,li->blocksize_0,li->blocksize_1,
        layout->end_bit,layout->codeword_count,layout->multiplicand_count,layout->book_count,layout->time_count,layout->floor_count,layout->residue_count,
        layout->mapping_count,layout->mode_count,layout->configuration_count,layout->floor_table,layout->residue_table,layout->mapping_table,layout->mode_table,xPortGetCoreID());
    for(uint32_t i=0;i<layout->book_count;i++){
        const native_vorbis_codebook_t *b=&view->books[i];const native_vorbis_quant_layout_t *q=&b->layout.quantization;
        printf("SETUP_BOOK case=%"PRIu32" book=%"PRIu32" start_bit=%"PRIu64" used_entries=%"PRIu32" maximum_length=%"PRIu32
            " dimensions=%"PRIu32" entries=%"PRIu32" lookup_type=%"PRIu32" minimum_bits=%08"PRIx32" delta_bits=%08"PRIx32" value_bits=%"PRIu32" sequence_p=%"PRIu32
            " multiplicand_count=%"PRIu64" quant_start_bit=%"PRIu64" multiplicand_bit=%"PRIu64" end_bit=%"PRIu64" core=%d\n",
            index,i,b->layout.start_bit,b->layout.used_entries,b->layout.maximum_length,q->dimensions,q->entries,q->lookup_type,q->minimum_bits,q->delta_bits,
            q->value_bits,q->sequence_p,q->multiplicand_count,q->start_bit,q->multiplicand_bit,q->end_bit,xPortGetCoreID());
        raw_array("WORDS",index,(int)i,b->words,b->word_count,24);raw_array("MULT",index,(int)i,b->quantization.multiplicands,b->quantization.storage_count,4);
    }
    raw_array("CONFIG",index,-1,configuration.data,layout->configuration_count,8);raw_array("GETTERS",index,-1,getter_output.data,getter_count,8);
    printf("SETUP_AUDIO case=%"PRIu32" mode=%"PRIu32" blockflag=%"PRIu32" previous_window=%"PRIu32" next_window=%"PRIu32" mapping=%"PRIu32" blocksize=%"PRIu32" position=%"PRIu64" end_of_packet=%u core=%d\n",
        index,prefix->mode,prefix->blockflag,prefix->previous_window,prefix->next_window,prefix->mapping,prefix->blocksize,cursor->position,(unsigned)cursor->end_of_packet,xPortGetCoreID());
    printf("SETUP_END case=%"PRIu32" id_truncation_checks=0 setup_truncation_checks=0 audio_truncation_checks=0 guards=%u unchanged=%u core=%d\n",index,(unsigned)guarded,(unsigned)preserved,xPortGetCoreID());
    for(size_t i=0;i<sizeof(all)/sizeof(all[0]);i++)release(all[i]);
}
static void worker(void *unused){
    (void)unused;printf("SETUP_WORKER core=%d priority=%u stack=16384\n",xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));unsigned checked=controls();REQUIRE(checked==SETUP_CONTROL_COUNT);
    printf("SETUP_CONTROLS checks=%u core=%d\n",checked,xPortGetCoreID());for(uint32_t i=0;i<SETUP_CASE_COUNT;i++){REQUIRE(xPortGetCoreID()==worker_core);capture(i);if((i&15U)==15U)vTaskDelay(1);}
    printf("SETUP_COMPLETE cases=%u controls=%u core=%d\n",(unsigned)SETUP_CASE_COUNT,checked,xPortGetCoreID());stop("CAPTURED");
}
void app_main(void){
    printf("SETUP_BEGIN cases=%u coordinator=%d worker=%d data=%s\n",(unsigned)SETUP_CASE_COUNT,xPortGetCoreID(),worker_core,SETUP_CASES_SHA256);fflush(stdout);
    if(xTaskCreatePinnedToCore(worker,"setup",16384,NULL,3,NULL,worker_core)!=pdPASS)stop("TASK_CREATE_FAILED");
}
