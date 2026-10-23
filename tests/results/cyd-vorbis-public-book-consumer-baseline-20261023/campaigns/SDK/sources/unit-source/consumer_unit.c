/* Owned-array consumer diagnostics; original arithmetic is consumer_port.inc.
 * SDK: exact included production parser/ILP32 ABI. Host: consumer only.
 * No vendor decoder, handles, stream processing, synthesis or PCM. */
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef ESP_PLATFORM
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "pinned/production/vorbis_repair/setup.c"
#define CORE() xPortGetCoreID()
#else
#include "host_codebook.h"
#define CORE() (-1)
#endif
#include "consumer_data.h"
#define P "PUBLIC_BOOK_CONSUMER_"

static void demand(bool ok, const char *why) {
    if (ok) return;
    printf(P "FAILURE reason=%s core=%d\n", why, CORE()); fflush(stdout);
#ifdef ESP_PLATFORM
    for (;;) vTaskDelay(1);
#else
    exit(2);
#endif
}
typedef struct { const uint8_t *data; size_t bytes, at, end; oggpack_buffer *owner; bool eop; } view_t;
static view_t view;
static void begin(oggpack_buffer *tag, const uint8_t *data, size_t bytes, size_t first, size_t end) {
    demand(first <= end && end <= bytes * 8U, "owned_bitspan");
    memset(tag, 0, sizeof(*tag)); view = (view_t){data,bytes,first,end,tag,false};
}
static long oggpack_look(oggpack_buffer *b, int width) {
    demand(b == view.owner && width >= 0 && width <= 32, "owned_reader_width");
    if (view.eop || (size_t)width > view.end - view.at) return -1;
    uint32_t value = 0;
    for (int i = 0; i < width; ++i) {
        size_t bit = view.at + (unsigned)i;
        value |= (uint32_t)((view.data[bit / 8U] >> (bit % 8U)) & 1U) << (unsigned)i;
    }
    return (long)(int32_t)value;
}
static void oggpack_adv(oggpack_buffer *b, int width) {
    demand(b == view.owner && width >= 0 && width <= 32, "owned_reader_advance");
    if ((size_t)width > view.end - view.at) { view.eop = true; return; }
    view.at += (unsigned)width;
}
static int oggpack_eop(oggpack_buffer *b) { demand(b == view.owner, "owned_reader_eop"); return view.eop; }
#ifdef ESP_PLATFORM
long tremor_oggpack_read(oggpack_buffer *b, int width) {
    long result = oggpack_look(b, width); oggpack_adv(b, width); return view.eop ? -1 : result;
}
int tremor_oggpack_eop(oggpack_buffer *b) { return oggpack_eop(b); }
typedef struct { uint8_t *base, *data; size_t bytes; bool live; } allocation_t;
static allocation_t allocations[32];
static unsigned live;
static bool guard(const allocation_t *a) {
    for (unsigned i=0;i<16;++i) if(a->base[i]!=0xa5 || a->data[a->bytes+i]!=0x5a) return false;
    return true;
}
static void guards(void) { for(unsigned i=0;i<32;++i) if(allocations[i].live) demand(guard(allocations+i),"owned_array_guards"); }
static size_t owned(const void *p) {
    for(unsigned i=0;i<32;++i) if(allocations[i].live && allocations[i].data==p) return allocations[i].bytes;
    demand(false,"owned_array_identity"); return 0;
}
void *media_lib_module_calloc(const char *module,size_t count,size_t bytes) {
    demand(module && !strcmp(module,"AUD_Codec") && count && bytes && count<=SIZE_MAX/bytes,"owned_alloc_arguments");
    bytes*=count;demand(bytes<=8192,"finite_owned_alloc_bound");
    unsigned slot=0;while(slot<32 && allocations[slot].live)++slot;demand(slot<32,"owned_alloc_capacity");
    uint8_t *base=calloc(1,bytes+32);demand(base!=NULL,"actual_owned_alloc");
    memset(base,0xa5,16);memset(base+16+bytes,0x5a,16);
    allocations[slot]=(allocation_t){base,base+16,bytes,true};++live;return base+16;
}
void media_lib_free(void *p) {
    if(!p)return;
    for(unsigned i=0;i<32;++i)if(allocations[i].live && allocations[i].data==p){
        demand(guard(allocations+i),"owned_free_guards");free(allocations[i].base);allocations[i].live=false;--live;return;
    }
    demand(false,"single_owned_free");
}
#endif

/* Only function-local linkage and void* byte arithmetic changed from public
 * source. All original consumer shifts/multiply/sequence operations remain. */
#include "consumer_port.inc"

static unsigned calls, unequal;
#ifdef ESP_PLATFORM
static void hex(const void *data,size_t bytes) { const uint8_t *p=data;for(size_t i=0;i<bytes;++i)printf("%02x",p[i]); }
#endif

static bool probe(codebook *b,const consumer_case_t *c,unsigned ci,unsigned pi,unsigned qi) {
    const consumer_probe_t *p=c->probes+pi;
    uint8_t bits[4]={(uint8_t)p->wire,(uint8_t)(p->wire>>8),(uint8_t)(p->wire>>16),(uint8_t)(p->wire>>24)};
    oggpack_buffer reader;begin(&reader,bits,sizeof(bits),0,p->bits);
    struct { uint32_t before[4]; int32_t values[16]; uint32_t after[4]; } output;
    for(unsigned i=0;i<4;++i){output.before[i]=UINT32_C(0xa55aa55a);output.after[i]=UINT32_C(0x5aa55aa5);}
    memset(output.values,0,sizeof(output.values));
    int rc=public_decode_map(b,&reader,output.values,c->points[qi]);
    demand(rc==0 && !view.eop && view.at==p->bits,"valid_public_codeword_exact_consumption");
    for(unsigned i=0;i<4;++i)demand(output.before[i]==UINT32_C(0xa55aa55a) && output.after[i]==UINT32_C(0x5aa55aa5),"vector_full_guards");
    for(unsigned i=(unsigned)c->dim;i<16;++i)demand(output.values[i]==0,"vector_full_unused_tail");
    bool equal=!memcmp(output.values,p->expected[qi],(size_t)c->dim*sizeof(int32_t));
    printf(P "VECTOR case=%u probe=%u point=%d bits=%u consumed=%u equal=%u core=%d values=",ci,pi,c->points[qi],p->bits,(unsigned)view.at,(unsigned)equal,CORE());
    for(int i=0;i<c->dim;++i)printf("%s%" PRId32,i?",":"",output.values[i]);
    printf("\n");fflush(stdout);++calls;if(!equal)++unequal;return equal;
}

#ifdef ESP_PLATFORM
static void run_case(unsigned ci) {
    const consumer_case_t *c=consumer_cases+ci;
    demand(!live && CORE()==0,"fresh_parser_case_core0");oggpack_buffer reader;
    begin(&reader,c->setup,c->setup_bytes,c->first,c->end);codebook b={0};
    demand(repair_vorbis_book_unpack(&reader,&b)==0 && !view.eop && view.at==c->end,"exact_unchanged_parser_book");
    demand(b.dim==c->dim && b.entries==c->entries && b.used_entries==c->used && b.dec_maxlength==c->maxlen &&
        b.dec_nodeb==c->node && b.dec_leafw==c->leafwords && b.dec_type==c->type && b.q_bits==c->qbits &&
        b.q_pack==c->qpack && b.q_seq==c->sequence && b.q_min==c->qmin && b.q_minp==c->minp &&
        b.q_del==c->qdel && b.q_delp==c->delp,"published_fields_match_independent_raw_oracle");
    size_t table=owned(b.dec_table),quant=b.q_val?owned(b.q_val):0;
    demand(table==c->table_bytes && quant==c->qval_bytes && (!quant || !memcmp(b.q_val,c->qval,quant)),"published_owned_sizes_and_all_quant_rows");
    guards();printf(P "FIELDS case=%u type=%d node=%d leaf=%d qbits=%d qpack=%d qmin=%" PRId32 " minp=%d qdel=%" PRId32 " delp=%d table=",ci,b.dec_type,b.dec_nodeb,b.dec_leafw,b.q_bits,b.q_pack,b.q_min,b.q_minp,b.q_del,b.q_delp);
    hex(b.dec_table,table);printf(" qval=");if(quant)hex(b.q_val,quant);else printf("-");printf(" core=%d\n",CORE());
    for(unsigned pi=0;pi<c->probe_count;++pi)for(unsigned qi=0;qi<c->point_count;++qi){(void)probe(&b,c,ci,pi,qi);guards();vTaskDelay(1);}
    repair_vorbis_book_clear(&b);demand(!live,"all_owned_arrays_freed");
    printf(P "CASE case=%u probes=%u live=0 core=%d\n",ci,c->probe_count,CORE());
}
void app_main(void) {
    demand(CORE()==0,"unit_coordinator_core0");
    printf(P "BEGIN contract=%s cases=%u calls=%u core=%d\n",CONSUMER_CONTRACT_SHA,CONSUMER_CASES,CONSUMER_CALLS,CORE());
    for(unsigned ci=0;ci<CONSUMER_CASES;++ci)run_case(ci);
    demand(!live && calls==CONSUMER_CALLS,"complete_owned_accounting");
    printf(P "COMPLETE cases=%u calls=%u unequal=%u live=0 core=%d\n",CONSUMER_CASES,calls,unequal,CORE());fflush(stdout);
    /* Return to SDK idle. Root must additionally prove owned QMP quit/SHUTDOWN,
     * EOF/reader join and real exit0. COMPLETE alone never qualifies anything.
     * Exact public arithmetic may be nonportable; unequal is never hidden. */
}
#else
int main(int argc,char **argv) {
    demand(argc==4,"three_numeric_indices_required");unsigned values[3];
    for(int i=0;i<3;++i){char *end;unsigned long n=strtoul(argv[i+1],&end,10);demand(*argv[i+1] && !*end && n<65536,"bounded_decimal_index");values[i]=(unsigned)n;}
    unsigned ci=values[0],pi=values[1],qi=values[2];demand(ci<CONSUMER_CASES,"host_case_index");
    const consumer_case_t *c=consumer_cases+ci;demand(pi<c->probe_count && qi<c->point_count,"host_probe_point_index");
    uint32_t endian=1;demand(*(uint8_t *)&endian==1,"host_little_endian_owned_scalars");
    codebook b={0};b.dim=c->dim;b.entries=c->entries;b.used_entries=c->used;b.dec_maxlength=c->maxlen;
    b.dec_nodeb=c->host_node;b.dec_leafw=c->host_leafwords;b.dec_type=c->type;b.dec_table=(void *)c->host_table;
    b.q_bits=c->qbits;b.q_pack=c->qpack;b.q_seq=c->sequence;b.q_val=(void *)c->qval;
    b.q_min=c->qmin;b.q_minp=c->minp;b.q_del=c->qdel;b.q_delp=c->delp;
    return probe(&b,c,ci,pi,qi)?0:1;
}
#endif
