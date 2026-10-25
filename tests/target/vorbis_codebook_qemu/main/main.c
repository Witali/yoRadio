// Guarded capture of owned packed codebooks and LSB-first Huffman/VQ operations.
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "native_vorbis_codebook.h"
#include "cases.h"
#ifdef NDEBUG
#error "Owned API controls require active assertions"
#endif
_Static_assert(sizeof(native_vorbis_affine_t)==16,"Four exact uint32 fields required");
#include "controls.h"
#if CONFIG_IDF_TARGET_ESP32
enum { worker_core=1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { worker_core=0 };
#else
#error "Unsupported codebook fixture target"
#endif
enum { CAPACITY=255, BYTE_CAPACITY=4096 };
static struct { uint64_t pre;uint8_t value[BYTE_CAPACITY];uint64_t post; } setup,payload;
static struct { uint64_t pre;native_vorbis_codeword_t value[CAPACITY+1];uint64_t post; } words;
static struct { uint64_t pre;uint16_t value[CAPACITY+1];uint64_t post; } storage;
static struct { uint64_t pre;native_vorbis_affine_t value[CAPACITY+1];uint64_t post; } values;
typedef struct { uint32_t entry;uint64_t position; } decoded_t;
static struct { uint64_t pre;decoded_t value[CAPACITY+1];uint64_t post; } decoded;
static uint8_t setup_before[BYTE_CAPACITY],payload_before[BYTE_CAPACITY];
static native_vorbis_codeword_t words_before[CAPACITY+1];
static uint16_t storage_before[CAPACITY+1];
static decoded_t decoded_before[CAPACITY+1];
static char hex_buffer[32*CAPACITY+1];
static void stop(const char *status) { printf("CODEBOOK_STOP status=%s\n",status);fflush(stdout);esp_restart(); }
static void require(bool ok,int line) {
    if(!ok) { printf("CODEBOOK_FAILURE line=%d core=%d\n",line,xPortGetCoreID());stop("FAIL"); }
}
#define REQUIRE(ok) require((ok),__LINE__)
static void hex_word(char *out,uint64_t value,unsigned digits) {
    static const char table[]="0123456789abcdef";
    for(unsigned i=0;i<digits;i++)out[i]=table[(value>>(4*(digits-1-i)))&15U];
}
static bool packet_shape(const native_vorbis_packet_t *cursor,const codebook_case_t *test) {
    return cursor->data==payload.value && cursor->bytes==test->payload_bytes && cursor->bits==test->payload_bits &&
        cursor->position>=test->payload_start && cursor->position<=test->payload_bits && !cursor->end_of_packet;
}
static bool same_quant(const native_vorbis_quant_layout_t *a,const native_vorbis_quant_layout_t *b) {
    return a->dimensions==b->dimensions && a->entries==b->entries && a->lookup_type==b->lookup_type &&
        a->minimum_bits==b->minimum_bits && a->delta_bits==b->delta_bits && a->value_bits==b->value_bits &&
        a->sequence_p==b->sequence_p && a->multiplicand_count==b->multiplicand_count &&
        a->start_bit==b->start_bit && a->multiplicand_bit==b->multiplicand_bit && a->end_bit==b->end_bit;
}
static void capture(uint32_t index) {
    const codebook_case_t *test=&codebook_cases[index];
    REQUIRE(test->packet_bytes<=BYTE_CAPACITY && test->payload_bytes<=BYTE_CAPACITY && test->length<=CAPACITY);
    setup.pre=setup.post=payload.pre=payload.post=words.pre=words.post=storage.pre=storage.post=values.pre=values.post=decoded.pre=decoded.post=CANARY;
    memset(setup.value,0xa5,sizeof(setup.value));memset(payload.value,0xa5,sizeof(payload.value));
    memset(words.value,0xa5,sizeof(words.value));memset(storage.value,0xa5,sizeof(storage.value));
    memset(values.value,0xa5,sizeof(values.value));memset(decoded.value,0xa5,sizeof(decoded.value));
    if(test->packet_bytes)memcpy(setup.value,test->packet,test->packet_bytes);
    if(test->payload_bytes)memcpy(payload.value,test->payload,test->payload_bytes);
    memcpy(setup_before,setup.value,sizeof(setup_before));memcpy(payload_before,payload.value,sizeof(payload_before));
    struct { uint64_t pre;native_vorbis_codebook_layout_t value;uint64_t post; } layout={.pre=CANARY,.post=CANARY};
    struct { uint64_t pre;native_vorbis_codebook_t value;uint64_t post; } book={.pre=CANARY,.post=CANARY};
    int measured=native_vorbis_codebook_measure(setup.value,test->packet_bytes,test->packet_bits,test->start_bit,&layout.value);
    REQUIRE(measured==0 && layout.value.used_entries<=CAPACITY && layout.value.quantization.multiplicand_count<=CAPACITY);
    int materialized=native_vorbis_codebook_materialize(setup.value,test->packet_bytes,test->packet_bits,&layout.value,
        words.value,CAPACITY,storage.value,CAPACITY,&book.value);
    REQUIRE(materialized==0 && book.value.word_count==layout.value.used_entries &&
        book.value.words==(layout.value.used_entries?words.value:NULL) &&
        book.value.quantization.multiplicands==(layout.value.quantization.multiplicand_count?storage.value:NULL) &&
        book.value.quantization.storage_count==layout.value.quantization.multiplicand_count &&
        book.value.layout.start_bit==layout.value.start_bit && book.value.layout.used_entries==layout.value.used_entries &&
        book.value.layout.maximum_length==layout.value.maximum_length &&
        same_quant(&book.value.layout.quantization,&layout.value.quantization) &&
        same_quant(&book.value.quantization.layout,&layout.value.quantization));
    size_t used=layout.value.used_entries,multiplicands=(size_t)layout.value.quantization.multiplicand_count;
    for(size_t i=used;i<=CAPACITY;i++)REQUIRE(words.value[i].code==UINT32_C(0xa5a5a5a5) &&
        words.value[i].entry==UINT32_C(0xa5a5a5a5) && words.value[i].length==UINT32_C(0xa5a5a5a5));
    for(size_t i=multiplicands;i<=CAPACITY;i++)REQUIRE(storage.value[i]==UINT16_C(0xa5a5));
    unsigned char layout_before[sizeof(layout.value)],book_before[sizeof(book.value)];
    memcpy(layout_before,&layout.value,sizeof(layout.value));memcpy(book_before,&book.value,sizeof(book.value));
    memcpy(words_before,words.value,sizeof(words_before));memcpy(storage_before,storage.value,sizeof(storage_before));
    size_t decode_count=test->length;
    if(test->operation==2)decode_count=test->length>0;
    else if(test->operation==3) {
        REQUIRE(layout.value.quantization.dimensions>0 && test->length>0);
        decode_count=(test->length-1)/layout.value.quantization.dimensions+1;
    } else REQUIRE(test->operation==1);
    struct { uint64_t pre;native_vorbis_packet_t value;uint64_t post; } first={.pre=CANARY,.post=CANARY},cursor={.pre=CANARY,.post=CANARY};
    REQUIRE(native_vorbis_packet_init(&first.value,payload.value,test->payload_bytes,test->payload_bits,test->payload_start)==0);
    for(size_t i=0;i<decode_count;i++) {
        struct { uint64_t pre;uint32_t value;uint64_t post; } entry={.pre=CANARY,.value=UINT32_C(0xa5a5a5a5),.post=CANARY};
        REQUIRE(native_vorbis_codebook_decode(&book.value,&first.value,&entry.value)==0);
        REQUIRE(entry.pre==CANARY && entry.post==CANARY && packet_shape(&first.value,test));
        decoded.value[i].entry=entry.value;decoded.value[i].position=first.value.position;
    }
    memcpy(decoded_before,decoded.value,sizeof(decoded_before));
    REQUIRE(native_vorbis_packet_init(&cursor.value,payload.value,test->payload_bytes,test->payload_bits,test->payload_start)==0);
    int operated=0;
    if(test->operation==1) {
        for(size_t i=0;i<decode_count;i++) {
            uint32_t entry=UINT32_C(0xa5a5a5a5);operated=native_vorbis_codebook_decode(&book.value,&cursor.value,&entry);
            REQUIRE(operated==0 && entry==decoded.value[i].entry && cursor.value.position==decoded.value[i].position);
        }
    } else if(test->operation==2)operated=native_vorbis_codebook_vector(&book.value,&cursor.value,test->length,values.value,CAPACITY);
    else operated=native_vorbis_codebook_floor0_lsp(&book.value,&cursor.value,test->length,values.value,CAPACITY);
    REQUIRE(operated==0 && packet_shape(&cursor.value,test) && packet_shape(&first.value,test) && cursor.value.position==first.value.position);
    size_t value_count=test->operation==1?0:test->length;
    for(size_t i=value_count;i<=CAPACITY;i++)REQUIRE(values.value[i].minimum_bits==UINT32_C(0xa5a5a5a5) &&
        values.value[i].delta_bits==UINT32_C(0xa5a5a5a5) && values.value[i].minimum_multiplier==UINT32_C(0xa5a5a5a5) && values.value[i].delta_multiplier==UINT32_C(0xa5a5a5a5));
    bool guards=setup.pre==CANARY && setup.post==CANARY && payload.pre==CANARY && payload.post==CANARY &&
        words.pre==CANARY && words.post==CANARY && storage.pre==CANARY && storage.post==CANARY &&
        values.pre==CANARY && values.post==CANARY && decoded.pre==CANARY && decoded.post==CANARY &&
        layout.pre==CANARY && layout.post==CANARY && book.pre==CANARY && book.post==CANARY &&
        first.pre==CANARY && first.post==CANARY && cursor.pre==CANARY && cursor.post==CANARY;
    bool unchanged=!memcmp(setup_before,setup.value,sizeof(setup_before)) && !memcmp(payload_before,payload.value,sizeof(payload_before)) &&
        !memcmp(words_before,words.value,sizeof(words_before)) && !memcmp(storage_before,storage.value,sizeof(storage_before)) &&
        !memcmp(layout_before,&layout.value,sizeof(layout.value)) && !memcmp(book_before,&book.value,sizeof(book.value)) &&
        !memcmp(decoded_before,decoded.value,sizeof(decoded_before));
    REQUIRE(guards && unchanged);
    printf("CODEBOOK_CASE case=%"PRIu32" id=%s operation=%"PRIu32" length=%"PRIu32" measure_status=%d materialize_status=%d operation_status=%d core=%d\n",
        index,test->id,test->operation,test->length,measured,materialized,operated,xPortGetCoreID());
    const native_vorbis_quant_layout_t *q=&layout.value.quantization;
    printf("CODEBOOK_LAYOUT case=%"PRIu32" start_bit=%"PRIu64" used_entries=%"PRIu32" maximum_length=%"PRIu32
        " dimensions=%"PRIu32" entries=%"PRIu32" lookup_type=%"PRIu32" minimum_bits=%08"PRIx32" delta_bits=%08"PRIx32
        " value_bits=%"PRIu32" sequence_p=%"PRIu32" multiplicand_count=%"PRIu64" quant_start_bit=%"PRIu64" multiplicand_bit=%"PRIu64" end_bit=%"PRIu64" core=%d\n",
        index,layout.value.start_bit,layout.value.used_entries,layout.value.maximum_length,q->dimensions,q->entries,q->lookup_type,
        q->minimum_bits,q->delta_bits,q->value_bits,q->sequence_p,q->multiplicand_count,q->start_bit,q->multiplicand_bit,q->end_bit,xPortGetCoreID());
    for(size_t i=0;i<used;i++) {
        hex_word(hex_buffer+24*i,words.value[i].code,8);hex_word(hex_buffer+24*i+8,words.value[i].entry,8);hex_word(hex_buffer+24*i+16,words.value[i].length,8);
    }
    hex_buffer[24*used]=0;
    printf("CODEBOOK_WORDS case=%"PRIu32" count=%u hex=%s core=%d\n",index,(unsigned)used,used?hex_buffer:"-",xPortGetCoreID());
    for(size_t i=0;i<multiplicands;i++)hex_word(hex_buffer+4*i,storage.value[i],4);
    hex_buffer[4*multiplicands]=0;
    printf("CODEBOOK_MULT case=%"PRIu32" count=%u hex=%s core=%d\n",index,(unsigned)multiplicands,multiplicands?hex_buffer:"-",xPortGetCoreID());
    for(size_t i=0;i<decode_count;i++) {
        hex_word(hex_buffer+24*i,decoded.value[i].entry,8);hex_word(hex_buffer+24*i+8,decoded.value[i].position,16);
    }
    hex_buffer[24*decode_count]=0;
    printf("CODEBOOK_DECODED case=%"PRIu32" count=%u hex=%s core=%d\n",index,(unsigned)decode_count,decode_count?hex_buffer:"-",xPortGetCoreID());
    for(size_t i=0;i<value_count;i++) {
        native_vorbis_affine_t value=values.value[i];hex_word(hex_buffer+32*i,value.minimum_bits,8);hex_word(hex_buffer+32*i+8,value.delta_bits,8);
        hex_word(hex_buffer+32*i+16,value.minimum_multiplier,8);hex_word(hex_buffer+32*i+24,value.delta_multiplier,8);
    }
    hex_buffer[32*value_count]=0;
    printf("CODEBOOK_VALUES case=%"PRIu32" count=%u hex=%s core=%d\n",index,(unsigned)value_count,value_count?hex_buffer:"-",xPortGetCoreID());
    printf("CODEBOOK_END case=%"PRIu32" position=%"PRIu64" end_of_packet=%u truncation_checks=0 payload_truncation_checks=0 guards=%u unchanged=%u core=%d\n",
        index,cursor.value.position,(unsigned)cursor.value.end_of_packet,(unsigned)guards,(unsigned)unchanged,xPortGetCoreID());
}
static void worker(void *unused) {
    (void)unused;printf("CODEBOOK_WORKER core=%d priority=%u stack=16384\n",xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    unsigned checked=controls();REQUIRE(checked==CODEBOOK_CONTROL_COUNT);
    printf("CODEBOOK_CONTROLS checks=%u core=%d\n",checked,xPortGetCoreID());
    for(uint32_t i=0;i<CODEBOOK_CASE_COUNT;i++){REQUIRE(xPortGetCoreID()==worker_core);capture(i);if((i&15U)==15U)vTaskDelay(1);}
    printf("CODEBOOK_COMPLETE cases=%u controls=%u core=%d\n",(unsigned)CODEBOOK_CASE_COUNT,checked,xPortGetCoreID());stop("CAPTURED");
}
void app_main(void) {
    printf("CODEBOOK_BEGIN cases=%u coordinator=%d worker=%d data=%s\n",(unsigned)CODEBOOK_CASE_COUNT,xPortGetCoreID(),worker_core,CODEBOOK_CASES_SHA256);fflush(stdout);
    if(xTaskCreatePinnedToCore(worker,"codebook",16384,NULL,3,NULL,worker_core)!=pdPASS)stop("TASK_CREATE_FAILED");
}
