// Native floor-packet capture; only this fixture owns guarded allocations.
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "native_vorbis_floor_packet.h"
#include "cases.h"
#ifdef NDEBUG
#error "Floor capture and controls require active assertions"
#endif
_Static_assert(sizeof(double)==8 && DBL_MANT_DIG==53,"Binary64 gain capture");
#include "shared.h"
#include "controls.h"
#if CONFIG_IDF_TARGET_ESP32
enum{worker_core=1};
#elif CONFIG_IDF_TARGET_ESP32C3
enum{worker_core=0};
#else
#error "Unsupported native floor target"
#endif
enum{CHUNK=128};static char hexadecimal[32*CHUNK+1];
static void stop(const char *status){printf("FLOOR_PACKET_STOP status=%s\n",status);fflush(stdout);esp_restart();}
static void hex_word(char *out,uint64_t value,unsigned digits){static const char table[]="0123456789abcdef";for(unsigned i=0;i<digits;i++)out[i]=table[(value>>(4*(digits-i-1)))&15U];}
static void raw_array(const char *kind,uint32_t index,const void *data,size_t count,unsigned digits){
    size_t start=0;do{size_t n=count-start;if(n>CHUNK)n=CHUNK;
        for(size_t i=0;i<n;i++){
            if(digits==32){const native_vorbis_affine_t *v=data;hex_word(hexadecimal+32*i,v[start+i].minimum_bits,8);hex_word(hexadecimal+32*i+8,v[start+i].delta_bits,8);hex_word(hexadecimal+32*i+16,v[start+i].minimum_multiplier,8);hex_word(hexadecimal+32*i+24,v[start+i].delta_multiplier,8);}
            else if(digits==8){const uint32_t *v=data;hex_word(hexadecimal+8*i,v[start+i],8);}
            else{const uint8_t *v=data;hex_word(hexadecimal+2*i,v[start+i],2);}
        }
        hexadecimal[digits*n]=0;printf("FLOOR_PACKET_%s case=%"PRIu32" start=%u total=%u count=%u hex=%s core=%d\n",kind,index,(unsigned)start,(unsigned)count,(unsigned)n,n?hexadecimal:"-",xPortGetCoreID());start+=n;
    }while(start<count);
}
static void capture(uint32_t index,context_t *context){
    const floor_packet_case_t *test=&floor_packet_cases[index];assert(test->identification_bytes<=PACKET_LIMIT && test->setup_bytes<=PACKET_LIMIT && test->packet_bytes<=PACKET_LIMIT && test->raw_count<=65);
    buffer_t packets[3];const uint8_t *data[]={test->identification,test->setup,test->packet};const size_t lengths[]={test->identification_bytes,test->setup_bytes,test->packet_bytes};
    for(unsigned i=0;i<3;i++){packets[i]=create(lengths[i],1);if(lengths[i])memcpy(packets[i].data,data[i],lengths[i]);copy_before(&packets[i]);}
    buffer_t raw=create(test->raw_count,sizeof(uint32_t));if(test->raw_count)memcpy(raw.data,test->raw_y,test->raw_count*sizeof(uint32_t));copy_before(&raw);
    context_prepare(context,&packets[0],test->identification_bits,&packets[1],test->setup_bits);capture_t c;
    capture_case(context,test->operation,&packets[2],test->packet_bits,test->start_bit,test->floor_index,test->curve_n,(void *)raw.data,test->raw_count,&c);
    printf("FLOOR_PACKET_CASE case=%"PRIu32" id=%s operation=%"PRIu32" floor_index=%"PRIu32" curve_n=%"PRIu32" prefix_status=%d floor_status=%d reconstruct_status=%d curve_status=%d gain_status=%d gain_consistent=%"PRIu32" core=%d\n",
        index,test->id,test->operation,test->floor_index,test->curve_n,c.prefix_status,c.floor_status,c.reconstruct_status,c.curve_status,c.gain_status,c.gain_consistent,xPortGetCoreID());
    if(!c.prefix_status){const native_vorbis_audio_prefix_t *p=(void *)c.prefix.data;printf("FLOOR_PACKET_PREFIX case=%"PRIu32" mode=%"PRIu32" blockflag=%"PRIu32" previous_window=%"PRIu32" next_window=%"PRIu32" mapping=%"PRIu32" blocksize=%"PRIu32" core=%d\n",index,p->mode,p->blockflag,p->previous_window,p->next_window,p->mapping,p->blocksize,xPortGetCoreID());}
    if(!c.floor_status){const native_vorbis_floor_packet_t *s=(void *)c.state.data;printf("FLOOR_PACKET_STATE case=%"PRIu32" floor_index=%"PRIu32" type=%"PRIu32" present=%"PRIu32" value_count=%"PRIu32" selected_book=%"PRIu32" raw_amplitude=%"PRIu64" amplitude_bits=%"PRIu32" amplitude_offset=%"PRIu32" core=%d\n",index,s->floor_index,s->type,s->present,s->value_count,s->selected_book,s->amplitude.raw_amplitude,s->amplitude.amplitude_bits,s->amplitude.amplitude_offset,xPortGetCoreID());}
    raw_array("COEFFICIENTS",index,c.coefficients.data,c.coefficient_count,32);raw_array("RAW",index,c.raw_y.data,c.raw_count,8);raw_array("FINAL",index,c.final_y.data,c.final_count,8);raw_array("ACTIVE",index,c.active.data,c.active_count,2);raw_array("INDICES",index,c.indices.data,c.index_count,2);
    if(!c.gain_status){const native_vorbis_floor0_gain_t *g=(void *)c.gain.data;printf("FLOOR_PACKET_GAIN case=%"PRIu32" kind=%u log2_bits=%016"PRIx64" log2_exponent=%"PRId32" core=%d\n",index,(unsigned)g->kind,double_bits(g->log2_gain.mantissa),g->log2_gain.exponent,xPortGetCoreID());}
    const native_vorbis_packet_t *cursor=(void *)c.cursor.data;printf("FLOOR_PACKET_END case=%"PRIu32" position=%"PRIu64" end_of_packet=%u guards=1 unchanged=1 core=%d\n",index,cursor->position,(unsigned)cursor->end_of_packet,xPortGetCoreID());
    check_buffer(&raw,1);destroy(&raw);for(unsigned i=0;i<3;i++){check_buffer(&packets[i],1);destroy(&packets[i]);}capture_destroy(&c);
}
static void worker(void *unused){
    (void)unused;printf("FLOOR_PACKET_WORKER core=%d priority=%u stack=16384\n",xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));unsigned checked=controls();assert(checked==FLOOR_PACKET_CONTROL_COUNT);
    printf("FLOOR_PACKET_CONTROLS checks=%u core=%d\n",checked,xPortGetCoreID());context_t context={0};
    for(uint32_t i=0;i<FLOOR_PACKET_CASE_COUNT;i++){assert(xPortGetCoreID()==worker_core);capture(i,&context);if((i&15U)==15U)vTaskDelay(1);}
    context_check(&context);context_destroy(&context);printf("FLOOR_PACKET_COMPLETE cases=%u controls=%u core=%d\n",(unsigned)FLOOR_PACKET_CASE_COUNT,checked,xPortGetCoreID());stop("CAPTURED");
}
void app_main(void){printf("FLOOR_PACKET_BEGIN cases=%u coordinator=%d worker=%d data=%s\n",(unsigned)FLOOR_PACKET_CASE_COUNT,xPortGetCoreID(),worker_core,FLOOR_PACKET_CASES_SHA256);fflush(stdout);if(xTaskCreatePinnedToCore(worker,"floor_packet",16384,NULL,3,NULL,worker_core)!=pdPASS)stop("TASK_CREATE_FAILED");}
