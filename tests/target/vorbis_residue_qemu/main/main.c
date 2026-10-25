// Isolated exact residue capture; guarded allocations belong only to this test.
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "native_vorbis_residue.h"
#include "cases.h"
#ifdef NDEBUG
#error "Residue capture and controls require active assertions"
#endif
#define RESIDUE_NATIVE 1
#include "shared.h"
#include "controls.h"
#if CONFIG_IDF_TARGET_ESP32
enum{worker_core=1};
#elif CONFIG_IDF_TARGET_ESP32C3
enum{worker_core=0};
#else
#error "Unsupported isolated residue target"
#endif
enum{CHUNK=128};static char hexadecimal[8*CHUNK+1];
static void stop(const char *status){printf("RESIDUE_STOP status=%s\n",status);fflush(stdout);esp_restart();}
static void raw_array(const char *kind,uint32_t index,const uint32_t *data,size_t count){
    static const char table[]="0123456789abcdef";size_t start=0;do{size_t n=count-start;if(n>CHUNK)n=CHUNK;
        for(size_t i=0;i<n;i++)for(unsigned j=0;j<8;j++)hexadecimal[8*i+j]=table[(data[start+i]>>(4*(7-j)))&15U];
        hexadecimal[8*n]=0;printf("RESIDUE_%s case=%"PRIu32" start=%u total=%u count=%u hex=%s core=%d\n",kind,index,(unsigned)start,(unsigned)count,(unsigned)n,n?hexadecimal:"-",xPortGetCoreID());start+=n;
    }while(start<count);
}
static void capture(uint32_t index,context_t *context){
    const residue_case_t *test=&residue_cases[index];assert(test->identification_bytes<=PACKET_LIMIT && test->setup_bytes<=PACKET_LIMIT && test->packet_bytes<=PACKET_LIMIT && test->flag_count<=255);
    buffer_t packets[3];const uint8_t *data[]={test->identification,test->setup,test->packet};const size_t lengths[]={test->identification_bytes,test->setup_bytes,test->packet_bytes};
    for(unsigned i=0;i<3;i++){packets[i]=create(lengths[i],1);if(lengths[i])memcpy(packets[i].data,data[i],lengths[i]);copy_before(&packets[i]);}
    buffer_t flags=create(test->flag_count,1);if(test->flag_count)memcpy(flags.data,test->floor_present,test->flag_count);copy_before(&flags);
    context_prepare(context,&packets[0],test->identification_bits,&packets[1],test->setup_bits);capture_t c;
    capture_case(context,&packets[2],test->packet_bits,test->start_bit,test->initial_eop,test->mapping,test->bins,&flags,&c);
    printf("RESIDUE_CASE case=%"PRIu32" id=%s mapping=%"PRIu32" bins=%"PRIu32" measure_status=%d packet_status=%d coupling_status=%d core=%d\n",index,test->id,test->mapping,test->bins,c.measure_status,c.packet_status,c.coupling_status,xPortGetCoreID());
    if(!c.measure_status){const native_vorbis_residue_layout_t *p=(void *)c.layout.data;printf("RESIDUE_LAYOUT case=%"PRIu32" mapping=%"PRIu32" bins=%"PRIu32" channels=%"PRIu32" limbs=%"PRIu32" magnitude_bits=%"PRIu32" exponent=%"PRId32" sample_count=%"PRIu64" limb_count=%"PRIu64" classification_count=%"PRIu64" core=%d\n",index,p->mapping,p->bins,p->channels,p->limbs,p->magnitude_bits,p->exponent,p->sample_count,p->limb_count,p->classification_count,xPortGetCoreID());}
    if(!c.packet_status){const native_vorbis_residue_packet_t *s=(void *)c.state.data;printf("RESIDUE_STATE case=%"PRIu32" classwords=%"PRIu64" vectors=%"PRIu64" values=%"PRIu64" stopped_on_eop=%"PRIu32" core=%d\n",index,s->classwords,s->vectors,s->values,s->stopped_on_eop,xPortGetCoreID());}
    raw_array("DECODED",index,(void *)c.decoded.data,c.decoded_count);raw_array("COUPLED",index,(void *)c.coupled.data,c.coupled_count);
    const native_vorbis_packet_t *cursor=(void *)c.cursor.data;printf("RESIDUE_END case=%"PRIu32" position=%"PRIu64" end_of_packet=%u guards=1 unchanged=1 core=%d\n",index,cursor->position,(unsigned)cursor->end_of_packet,xPortGetCoreID());
    check_buffer(&flags,1);destroy(&flags);for(unsigned i=0;i<3;i++){check_buffer(&packets[i],1);destroy(&packets[i]);}capture_destroy(&c);
}
static void worker(void *unused){
    (void)unused;printf("RESIDUE_WORKER core=%d priority=%u stack=16384\n",xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));unsigned checked=controls();assert(checked==RESIDUE_CONTROL_COUNT);printf("RESIDUE_CONTROLS checks=%u core=%d\n",checked,xPortGetCoreID());context_t context={0};
    for(uint32_t i=0;i<RESIDUE_CASE_COUNT;i++){assert(xPortGetCoreID()==worker_core);capture(i,&context);if((i&15U)==15U)vTaskDelay(1);}
    context_check(&context);context_destroy(&context);printf("RESIDUE_COMPLETE cases=%u controls=%u core=%d\n",(unsigned)RESIDUE_CASE_COUNT,checked,xPortGetCoreID());stop("CAPTURED");
}
void app_main(void){printf("RESIDUE_BEGIN cases=%u coordinator=%d worker=%d data=%s\n",(unsigned)RESIDUE_CASE_COUNT,xPortGetCoreID(),worker_core,RESIDUE_CASES_SHA256);fflush(stdout);if(xTaskCreatePinnedToCore(worker,"residue",16384,NULL,3,NULL,worker_core)!=pdPASS)stop("TASK_CREATE_FAILED");}
